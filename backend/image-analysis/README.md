# Image analysis

This directory contains the production image-analysis source used by Aesthetic
Matcher and Pic-to-Playlist. It was copied unchanged from the Linux production
runtime during the repository restructure.

Aesthetic Matcher is the canonical owner and the only repository that deploys
the shared Linux service. Pic-to-Playlist receives a synchronized source copy
for local development.

Production runs through Gunicorn with one worker and one inference request at
a time. This keeps the shared 8 GB GPU from loading duplicate model processes
or processing simultaneous Aesthetic Matcher and Pic-to-Playlist requests.

Production configuration, model caches, Python environments, and uploaded
images remain outside Git.

## Request safety

The API validates request size, image count, decoded pixel count, and image
format before inference.

See `.env.example` for the supported limits and defaults.

## Feedback delivery

`POST /image-analysis/am/feedback` accepts the small feedback form on the
matcher page. Valid submissions are written as notes to the configured Kevin
Index folder, then an email notification is sent to Kevin. The route does not
store uploaded images or matcher results.

The production environment must provide `KEVIN_INDEX_API_URL`,
`FEEDBACK_EMAIL_USER`, `FEEDBACK_EMAIL_PASSWORD`, and `FEEDBACK_EMAIL_TO`.
The endpoint rejects requests until all delivery settings are present. A
honeypot, request validation, idempotency keys, and a per-address rate limit
reduce accidental duplicates and basic form spam.
