# Aesthetic Matcher

Aesthetic Matcher classifies uploaded images into visual aesthetics using a
custom image-analysis service and research derived from Aesthetics Wiki data.

The current public application is available at
[aestheticmatcher.com](https://aestheticmatcher.com).

<p align="center">
  <img src="docs/images/am-screenshot1.png" alt="Main page" width="250" height="475" />
  <img src="docs/images/am-screenshot2.png" alt="Processed images" width="250" height="475" />
  <img src="docs/images/am-screenshot3.png" alt="Post-processing menu" width="250" height="475" />
</p>

## Repository layout

```text
aesthetic-matcher/
├── web/
│   └── astro/                 # Current public Astro application
├── legacy/
│   ├── expo-client/           # Previous Expo and React Native client
│   └── flask-backend/         # Original backend prototype
├── research/
│   ├── data-refinement/       # Scraping and preprocessing tools
│   └── fine-tuning/           # Model experiments and notebooks
├── docs/
│   ├── ARCHITECTURE.md
│   └── images/
└── .github/workflows/         # Build and deployment pipeline
```

The production image-analysis API is maintained separately in the
`image-analysis` project. The Flask code in `legacy/flask-backend` is retained
for history and comparison while useful logic is consolidated into that
service.

## Develop the web application

```bash
cd web/astro
npm ci
npm run dev
```

## Build

```bash
cd web/astro
npm ci
npm run build
```

Static output is written to `web/astro/dist`.

## Deployment

`.github/workflows/deploy.yml` builds the Astro site and deploys the generated
files to `/srv/kevin/web/aestheticmatcher.com` on the Linux server. Production
credentials are supplied through the GitHub `production` environment and are
never stored in this repository.

## Research data

Research scripts and notebooks are versioned. Downloaded images, generated
datasets, model output, dependencies, and local environments are not committed.
Server-side research data belongs under
`/srv/kevin/data/aesthetic-matcher/research` when Linux processing is needed.
