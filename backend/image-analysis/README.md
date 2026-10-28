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

## Wiki catalog refresh

The matcher loads `wiki_aesthetics.py` at startup and unions those names with
all original descriptive prompts in `summarized_aesthetics.py`. Existing
prompts are kept unchanged. New categories use their Wiki title as the CLIP
prompt. Matching ignores case and repeated whitespace, and result titles
preserve commas. This expands coverage without changing the model or ranking
algorithm; it does not establish improved accuracy.

From the repository root, refresh the checked-in snapshot:

```bash
python3 research/catalog/sync_aesthetics_wiki.py --apply
python3 -m unittest discover -s backend/image-analysis/tests -p test_catalog.py
```

Without `--apply`, the command only writes an ignored discovery report under
`research/catalog/generated/`. It fetches the alphabetical list from
https://aesthetics.fandom.com/wiki/List_of_Aesthetics through the MediaWiki API.
Previously imported labels are retained even when absent from the latest list.
Malformed/failed responses leave the snapshot untouched; writes use atomic
replacement. `--input-json` supports replaying a saved API response.

Deploy the changed backend files and restart `image-analysis-flask.service`
for a refresh to become active. This is a maintained snapshot, not an automatic
scheduled fetch or a network dependency on each upload. A deployment should
retain the prior backend revision for rollback and verify a real image request.
The shared service also handles Pic-to-Playlist, so restart briefly interrupts
both routes. Rollback restores the previous revision and restarts the service.
