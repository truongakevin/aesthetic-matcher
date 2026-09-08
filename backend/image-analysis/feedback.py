import json
import logging
import os
import smtplib
import time
from collections import defaultdict, deque
from datetime import datetime, timezone
from email.message import EmailMessage
from threading import Lock
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import UUID, uuid4

from dotenv import load_dotenv
from flask import Blueprint, jsonify, request


load_dotenv()

logger = logging.getLogger(__name__)
feedback_blueprint = Blueprint("feedback", __name__)

KEVIN_INDEX_API_URL = os.getenv("KEVIN_INDEX_API_URL", "").rstrip("/")
KEVIN_INDEX_FOLDER_ID = os.getenv("KEVIN_INDEX_FOLDER_ID", "scratch")
FEEDBACK_SMTP_HOST = os.getenv("FEEDBACK_SMTP_HOST", "smtp.gmail.com")
FEEDBACK_SMTP_PORT = int(os.getenv("FEEDBACK_SMTP_PORT", "465"))
FEEDBACK_EMAIL_USER = os.getenv("FEEDBACK_EMAIL_USER", "")
FEEDBACK_EMAIL_PASSWORD = os.getenv("FEEDBACK_EMAIL_PASSWORD", "")
FEEDBACK_EMAIL_TO = os.getenv("FEEDBACK_EMAIL_TO", FEEDBACK_EMAIL_USER)
FEEDBACK_RATE_LIMIT = int(os.getenv("FEEDBACK_RATE_LIMIT", "5"))
FEEDBACK_RATE_WINDOW_SECONDS = int(os.getenv("FEEDBACK_RATE_WINDOW_SECONDS", "3600"))

MAX_MESSAGE_LENGTH = 4000
MAX_EMAIL_LENGTH = 320
MAX_PAGE_URL_LENGTH = 1000

submission_times = defaultdict(deque)
submission_times_lock = Lock()


class FeedbackDeliveryError(RuntimeError):
    pass


def feedback_error(message, status):
    return jsonify({"error": message}), status


def configured():
    return all((
        KEVIN_INDEX_API_URL,
        FEEDBACK_EMAIL_USER,
        FEEDBACK_EMAIL_PASSWORD,
        FEEDBACK_EMAIL_TO,
    ))


def client_address():
    return request.headers.get("X-Real-IP", request.remote_addr or "unknown").strip()


def consume_rate_limit(address, now=None):
    current_time = now if now is not None else time.monotonic()
    cutoff = current_time - FEEDBACK_RATE_WINDOW_SECONDS
    with submission_times_lock:
        recent = submission_times[address]
        while recent and recent[0] <= cutoff:
            recent.popleft()
        if len(recent) >= FEEDBACK_RATE_LIMIT:
            return False
        recent.append(current_time)
    return True


def validated_payload():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValueError("Send feedback as JSON.")

    if str(data.get("website", "")).strip():
        return None

    message = str(data.get("message", "")).strip()
    email = str(data.get("email", "")).strip()
    page_url = str(data.get("pageUrl", "")).strip()
    idempotency_key = str(data.get("idempotencyKey", "")).strip()

    if not message:
        raise ValueError("Write a message before sending feedback.")
    if len(message) > MAX_MESSAGE_LENGTH:
        raise ValueError(f"Keep feedback under {MAX_MESSAGE_LENGTH} characters.")
    if len(email) > MAX_EMAIL_LENGTH or (email and ("@" not in email or "\n" in email or "\r" in email)):
        raise ValueError("Enter a valid email address or leave it blank.")
    if len(page_url) > MAX_PAGE_URL_LENGTH:
        raise ValueError("The page URL is too long.")
    try:
        UUID(idempotency_key)
    except (ValueError, AttributeError) as error:
        raise ValueError("The submission ID is invalid.") from error

    return {
        "message": message,
        "email": email,
        "page_url": page_url,
        "idempotency_key": idempotency_key,
    }


def feedback_title(message):
    compact = " ".join(message.split())
    excerpt = compact[:72].rstrip()
    if len(compact) > len(excerpt):
        excerpt += "..."
    return f"Aesthetic Matcher feedback: {excerpt}"


def create_index_item(payload, submitted_at):
    contact = payload["email"] or "Not provided"
    page = payload["page_url"] or "Not provided"
    content = (
        f"{payload['message']}\n\n"
        f"Submitted: {submitted_at}\n"
        f"Contact email: {contact}\n"
        f"Page: {page}"
    )
    body = {
        "kind": "note",
        "folderId": KEVIN_INDEX_FOLDER_ID,
        "title": feedback_title(payload["message"]),
        "blocks": [{"id": f"block-{uuid4()}", "type": "text", "text": content}],
        "source": "aesthetic-matcher-feedback",
        "feedback": {
            "submittedAt": submitted_at,
            "contactEmail": payload["email"] or None,
            "pageUrl": payload["page_url"] or None,
        },
    }
    encoded = json.dumps(body, ensure_ascii=False).encode("utf-8")
    index_request = Request(
        f"{KEVIN_INDEX_API_URL}/items",
        data=encoded,
        method="POST",
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Idempotency-Key": f"aesthetic-matcher-feedback-{payload['idempotency_key']}",
            "X-Actor-Type": "integration",
            "X-Actor-ID": "aesthetic-matcher",
        },
    )
    try:
        with urlopen(index_request, timeout=15) as response:
            return json.loads(response.read())
    except (HTTPError, URLError, TimeoutError, ValueError) as error:
        raise FeedbackDeliveryError("Kevin Index did not accept the feedback.") from error


def send_feedback_email(payload, submitted_at, item):
    message = EmailMessage()
    message["From"] = FEEDBACK_EMAIL_USER
    message["To"] = FEEDBACK_EMAIL_TO
    message["Subject"] = "New Aesthetic Matcher feedback"
    if payload["email"]:
        message["Reply-To"] = payload["email"]
    message.set_content(
        f"{payload['message']}\n\n"
        f"Submitted: {submitted_at}\n"
        f"Contact email: {payload['email'] or 'Not provided'}\n"
        f"Page: {payload['page_url'] or 'Not provided'}\n"
        f"Kevin Index item: {item.get('id', 'unknown')}\n"
        f"Kevin Index: http://10.0.0.153:3010/index"
    )
    try:
        with smtplib.SMTP_SSL(FEEDBACK_SMTP_HOST, FEEDBACK_SMTP_PORT, timeout=15) as smtp:
            smtp.login(FEEDBACK_EMAIL_USER, FEEDBACK_EMAIL_PASSWORD)
            smtp.send_message(message)
    except (OSError, smtplib.SMTPException) as error:
        raise FeedbackDeliveryError("The feedback email could not be sent.") from error


@feedback_blueprint.post("/image-analysis/am/feedback")
def submit_feedback():
    try:
        payload = validated_payload()
    except ValueError as error:
        return feedback_error(str(error), 400)

    if payload is None:
        return jsonify({"ok": True}), 201
    if not configured():
        logger.error("Feedback endpoint is missing Kevin Index or email configuration")
        return feedback_error("Feedback is unavailable right now. Please try again later.", 503)
    if not consume_rate_limit(client_address()):
        return feedback_error("Too many messages were sent from this connection. Please try again later.", 429)

    submitted_at = datetime.now(timezone.utc).isoformat()
    try:
        item = create_index_item(payload, submitted_at)
    except FeedbackDeliveryError:
        logger.exception("Could not save Aesthetic Matcher feedback to Kevin Index")
        return feedback_error("Feedback could not be saved right now. Please try again later.", 503)

    email_sent = True
    try:
        send_feedback_email(payload, submitted_at, item)
    except FeedbackDeliveryError:
        email_sent = False
        logger.exception("Feedback was saved to Kevin Index but its email notification failed")

    return jsonify({"ok": True, "emailSent": email_sent}), 201
