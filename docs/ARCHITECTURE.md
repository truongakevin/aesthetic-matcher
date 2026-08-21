# Architecture

## Active application

The public site is the static Astro application in `web/astro`.

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

The production Flask and Node image-analysis components support more than one
application. Their canonical source belongs in the separate `image-analysis`
project. Code in `legacy/flask-backend` records the original Aesthetic Matcher
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
