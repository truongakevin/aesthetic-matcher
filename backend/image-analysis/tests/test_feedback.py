import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from flask import Flask

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import feedback


class FeedbackEndpointTests(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        app.register_blueprint(feedback.feedback_blueprint)
        self.client = app.test_client()
        feedback.submission_times.clear()
        self.payload = {
            "message": "I would love more architecture aesthetics.",
            "email": "visitor@example.com",
            "website": "",
            "pageUrl": "https://aestheticmatcher.com/match/",
            "idempotencyKey": "e3157a69-a264-4bb3-8495-cc818b19c620",
        }

    @patch.object(feedback, "send_feedback_email")
    @patch.object(feedback, "create_index_item", return_value={"id": "feedback-item"})
    @patch.object(feedback, "configured", return_value=True)
    def test_valid_feedback_is_saved_and_emailed(self, _configured, create_item, send_email):
        response = self.client.post("/image-analysis/am/feedback", json=self.payload)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json(), {"ok": True, "emailSent": True})
        create_item.assert_called_once()
        send_email.assert_called_once()

    @patch.object(
        feedback,
        "send_feedback_email",
        side_effect=feedback.FeedbackDeliveryError("email failed"),
    )
    @patch.object(feedback, "create_index_item", return_value={"id": "feedback-item"})
    @patch.object(feedback, "configured", return_value=True)
    def test_email_failure_preserves_saved_feedback(
        self,
        _configured,
        create_item,
        _send_email,
    ):
        response = self.client.post("/image-analysis/am/feedback", json=self.payload)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json(), {"ok": True, "emailSent": False})
        create_item.assert_called_once()

    @patch.object(feedback, "create_index_item")
    @patch.object(feedback, "configured", return_value=True)
    def test_honeypot_returns_success_without_delivery(self, _configured, create_item):
        payload = {**self.payload, "website": "spam.example"}
        response = self.client.post("/image-analysis/am/feedback", json=payload)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json(), {"ok": True})
        create_item.assert_not_called()

    @patch.object(feedback, "create_index_item")
    @patch.object(feedback, "configured", return_value=False)
    def test_missing_configuration_fails_before_saving(self, _configured, create_item):
        response = self.client.post("/image-analysis/am/feedback", json=self.payload)

        self.assertEqual(response.status_code, 503)
        create_item.assert_not_called()

    def test_empty_feedback_is_rejected(self):
        response = self.client.post(
            "/image-analysis/am/feedback",
            json={**self.payload, "message": "   "},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Write a message", response.get_json()["error"])

    @patch.object(feedback, "send_feedback_email")
    @patch.object(feedback, "create_index_item", return_value={"id": "feedback-item"})
    @patch.object(feedback, "configured", return_value=True)
    def test_rate_limit_rejects_sixth_message(self, _configured, _create_item, _send_email):
        for index in range(5):
            payload = {
                **self.payload,
                "idempotencyKey": f"e3157a69-a264-4bb3-8495-cc818b19c62{index}",
            }
            self.assertEqual(
                self.client.post("/image-analysis/am/feedback", json=payload).status_code,
                201,
            )

        response = self.client.post(
            "/image-analysis/am/feedback",
            json={**self.payload, "idempotencyKey": "e3157a69-a264-4bb3-8495-cc818b19c629"},
        )
        self.assertEqual(response.status_code, 429)


class FeedbackDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.payload = {
            "message": "Please add more architecture aesthetics.",
            "email": "visitor@example.com",
            "page_url": "https://aestheticmatcher.com/match/",
            "idempotency_key": "e3157a69-a264-4bb3-8495-cc818b19c620",
        }

    @patch.object(feedback, "KEVIN_INDEX_API_URL", "http://index.test/api/v1")
    @patch.object(feedback, "urlopen")
    def test_index_request_targets_inbox_with_provenance(self, urlopen):
        response = MagicMock()
        response.read.return_value = b'{"id":"feedback-item"}'
        urlopen.return_value.__enter__.return_value = response

        item = feedback.create_index_item(self.payload, "2026-09-08T17:00:00+00:00")

        self.assertEqual(item["id"], "feedback-item")
        index_request = urlopen.call_args.args[0]
        body = json.loads(index_request.data)
        self.assertEqual(index_request.full_url, "http://index.test/api/v1/items")
        self.assertEqual(body["folderId"], "scratch")
        self.assertEqual(body["source"], "aesthetic-matcher-feedback")
        self.assertEqual(index_request.headers["X-actor-id"], "aesthetic-matcher")
        self.assertTrue(index_request.headers["Idempotency-key"].startswith("aesthetic-matcher-feedback-"))

    @patch.object(feedback, "FEEDBACK_EMAIL_USER", "sender@example.com")
    @patch.object(feedback, "FEEDBACK_EMAIL_PASSWORD", "app-password")
    @patch.object(feedback, "FEEDBACK_EMAIL_TO", "kevin@example.com")
    @patch.object(feedback.smtplib, "SMTP_SSL")
    def test_email_uses_optional_contact_as_reply_to(self, smtp_ssl):
        smtp = smtp_ssl.return_value.__enter__.return_value

        feedback.send_feedback_email(
            self.payload,
            "2026-09-08T17:00:00+00:00",
            {"id": "feedback-item"},
        )

        smtp.login.assert_called_once_with("sender@example.com", "app-password")
        sent_message = smtp.send_message.call_args.args[0]
        self.assertEqual(sent_message["To"], "kevin@example.com")
        self.assertEqual(sent_message["Reply-To"], "visitor@example.com")
        self.assertIn("feedback-item", sent_message.get_content())


if __name__ == "__main__":
    unittest.main()
