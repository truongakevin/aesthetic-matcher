import React, { useRef, useState } from 'react';

const MATCHER_API_URL = import.meta.env.PUBLIC_IMAGE_ANALYSIS_URL
  ?? 'https://kevinatruong.com/api/image-analysis/am';
const FEEDBACK_API_URL = import.meta.env.PUBLIC_FEEDBACK_URL
  ?? `${MATCHER_API_URL.replace(/\/$/, '')}/feedback`;

interface FeedbackResponse {
  error?: string;
}

const FeedbackForm = () => {
  const [message, setMessage] = useState('');
  const [email, setEmail] = useState('');
  const [website, setWebsite] = useState('');
  const [sending, setSending] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const submissionId = useRef<string | null>(null);

  const updateMessage = (value: string) => {
    setMessage(value);
    submissionId.current = null;
    setError(null);
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!message.trim()) {
      setError('Write a message before sending feedback.');
      return;
    }

    setSending(true);
    setError(null);
    submissionId.current ??= crypto.randomUUID();

    try {
      const response = await fetch(FEEDBACK_API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message,
          email,
          website,
          pageUrl: window.location.href,
          idempotencyKey: submissionId.current,
        }),
      });
      const data = await response.json().catch(() => null) as FeedbackResponse | null;
      if (!response.ok) {
        throw new Error(data?.error ?? 'Feedback could not be sent right now.');
      }
      setSent(true);
      setMessage('');
      setEmail('');
      submissionId.current = null;
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : 'Feedback could not be sent right now.');
    } finally {
      setSending(false);
    }
  };

  if (sent) {
    return (
      <section className="feedback-panel" aria-live="polite">
        <p className="feedback-thanks">thanks, your feedback was sent to Kevin!</p>
        <button className="feedback-link-button" type="button" onClick={() => setSent(false)}>
          send another note
        </button>
      </section>
    );
  }

  return (
    <details className="feedback-panel">
      <summary>send feedback</summary>
      <form onSubmit={handleSubmit} className="feedback-form">
        <label htmlFor="feedback-message">what should Kevin know?</label>
        <textarea
          id="feedback-message"
          value={message}
          onChange={(event) => updateMessage(event.target.value)}
          maxLength={4000}
          rows={5}
          required
        />

        <label htmlFor="feedback-email">email (optional, only if you want a reply)</label>
        <input
          id="feedback-email"
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          maxLength={320}
          autoComplete="email"
        />

        <div className="feedback-honeypot" aria-hidden="true">
          <label htmlFor="feedback-website">website</label>
          <input
            id="feedback-website"
            type="text"
            value={website}
            onChange={(event) => setWebsite(event.target.value)}
            tabIndex={-1}
            autoComplete="off"
          />
        </div>

        {error && <p className="feedback-error" role="alert">{error}</p>}
        <button type="submit" disabled={sending}>{sending ? 'sending...' : 'send feedback'}</button>
      </form>
    </details>
  );
};

export default FeedbackForm;
