# Architecture

## Active application

The public site is the static Astro application in `frontend`.

```text
Browser
  -> Nginx
  -> Static Astro build
  -> Shared image-analysis API
```

The site is built by GitHub Actions and deployed to:

```text
/srv/kevin/web/aestheticmatcher.com
```

Nginx owns public HTTP and HTTPS routing. The static application does not run
as a separate systemd service.

## Image analysis

The production image-analysis backend supports Aesthetic Matcher and
Pic-to-Playlist. Its canonical source belongs in `backend/image-analysis` in
this repository. A synchronized copy is maintained in the Pic-to-Playlist
repository for local development, but only Aesthetic Matcher deploys the
shared GPU service. Code in `legacy/flask-backend` records the original
implementation and must not be treated as the production service.

## Legacy client

`legacy/expo-client` contains the earlier Expo and React Native application.
Its JavaScript source is retained in Git. Generated iOS and Android projects,
CocoaPods, build output, and local dependencies remain outside Git.

## Research

`research/data-refinement` contains scraping and preprocessing tools.
`research/fine-tuning` contains model training experiments and notebooks.

Research code belongs in Git. Downloaded images, generated datasets, trained
model output, and local environments belong outside Git. Linux-hosted research
data uses:

```text
/srv/kevin/data/aesthetic-matcher/research
```

## Configuration and secrets

Repository configuration must contain no production credentials. Safe examples
may be committed as `.env.example`. Production values belong in the centralized
Linux environment configuration and GitHub environment secrets.
