[![CI](https://github.com/stadiumiq/stadiumiq/actions/workflows/ci.yml/badge.svg)](https://github.com/stadiumiq/stadiumiq/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue.svg)](https://www.typescriptlang.org/)

# StadiumIQ — Smart Stadium Operations for FIFA World Cup 2026

> AI-powered stadium intelligence that enhances crowd safety, fan experience, and sustainability for the world's largest sporting events — with graceful degradation ensuring it never fails to serve.

## Live Demo

🌐 **[https://stadiumiq.example.run.app](https://stadiumiq.example.run.app)** _(Cloud Run deployment)_

## Problem Statement

FIFA World Cup 2026 venues host 60,000–100,000 fans per match, spanning 16 cities across 3 countries. Organizers face unprecedented operational challenges:

| Challenge | Impact | StadiumIQ Solution |
|-----------|--------|-------------------|
| **Crowd Safety** | Crush incidents from unmanaged density | Real-time density estimation + AI congestion prediction |
| **Language Barriers** | 30+ languages among global fans | Gemini-powered multilingual assistant (9 languages) |
| **Accessibility Gaps** | Wheelchair/visual/hearing needs unmet | A* pathfinding with accessibility-weighted routing |
| **Post-Match Chaos** | 100K fans exiting simultaneously | Transport mode coordination + staggered exit plans |
| **Sustainability Targets** | FIFA 2026 carbon neutrality goals | Per-match footprint tracking vs. FIFA targets |

## Approach & Decision-Making

StadiumIQ follows a **reliability-first architecture**:

1. **Gemini AI** provides the richest, most contextual fan assistance — personalized multilingual answers, crowd prediction insights, and sustainability recommendations
2. **Deterministic rule engines** serve as full-featured fallbacks — every feature works without AI
3. **Every response is tagged** with its source (`gemini`, `rules`, `cache`) for transparency and observability

This means StadiumIQ is **always operational**, even when cloud services are unavailable.

## Architecture

```
                        ┌──────────────────────┐
                        │    Frontend (Vite)    │
                        │  React + TypeScript   │
                        └──────────┬───────────┘
                                   │ HTTPS
                        ┌──────────▼───────────┐
                        │   FastAPI Gateway     │
                        │ Security│Rate│Logging │
                        └──────────┬───────────┘
               ┌───────────────────┼───────────────────┐
               ▼                   ▼                   ▼
    ┌──────────────────┐ ┌─────────────────┐ ┌────────────────┐
    │  Crowd Intel      │ │  Fan Assistant   │ │  Sustainability│
    │  density.py       │ │  gemini.py       │ │  tracker.py    │
    │  (pure math)      │ │  rules.py        │ │  (pure math)   │
    └──────────────────┘ │  (fallback)       │ └────────────────┘
               ▲         └────────┬──────────┘         ▲
               │                  │                    │
    ┌──────────────────┐ ┌────────▼──────────┐ ┌──────────────┐
    │  Wayfinding       │ │  Persistence      │ │  Venue Graph  │
    │  navigator.py     │ │  Protocol →       │ │  venue_graph  │
    │  (A* pathfinding) │ │  Firestore│Memory │ │  (pure data)  │
    └──────────────────┘ └───────────────────┘ └──────────────┘
```

### Project Layout

```
Challenge4/
├── backend/
│   ├── app/
│   │   ├── crowd/          # Crowd density & congestion (pure domain)
│   │   ├── wayfinding/     # Accessible route finding (pure domain)
│   │   ├── sustainability/ # Carbon footprint tracking (pure domain)
│   │   ├── assistant/      # Gemini AI + rule engine fallback
│   │   ├── repository/     # Persistence (Firestore + in-memory)
│   │   ├── routes/         # HTTP transport layer
│   │   ├── config.py       # Validated settings (pydantic-settings)
│   │   ├── deps.py         # Dependency injection wiring
│   │   └── main.py         # App factory, middleware, logging
│   ├── tests/              # pytest (unit + integration, ≥90% coverage)
│   └── pyproject.toml      # Strict mypy, ruff, coverage gates
├── frontend/
│   ├── src/
│   │   ├── components/     # React presentational components
│   │   ├── hooks/          # State + API logic
│   │   ├── lib/            # Pure utilities, types, API client
│   │   └── styles/         # CSS with documented contrast ratios
│   ├── e2e/                # Playwright end-to-end tests
│   └── vite.config.ts      # Build + test + coverage config
├── docs/ARCHITECTURE.md    # Layer responsibilities & design rules
├── Dockerfile              # Multi-stage (Node build → Python slim)
└── .github/workflows/      # 4-job CI pipeline
```

## Key Endpoints

| Method | Endpoint | Description | Rate Limit |
|--------|----------|-------------|------------|
| `POST` | `/api/crowd/density` | Zone density analysis from gate counts | — |
| `POST` | `/api/crowd/predict` | AI congestion prediction | — |
| `POST` | `/api/crowd/reroute` | Alternative route suggestions | — |
| `POST` | `/api/assist` | Multilingual fan assistant (Gemini + fallback) | 10/min |
| `POST` | `/api/wayfinding/route` | Accessible route between zones | — |
| `POST` | `/api/wayfinding/nearest` | Nearest accessible facility | — |
| `POST` | `/api/sustainability/footprint` | Match carbon footprint calculation | — |
| `GET`  | `/api/sustainability/targets` | FIFA 2026 sustainability targets | — |
| `GET`  | `/api/health` | Liveness probe | — |

## Running Locally

### Prerequisites

- Python 3.12+
- Node.js 20+
- (Optional) `gcloud auth application-default login` for Gemini AI

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm ci
npm run dev
```

### Environment Variables

Copy `.env.example` to `backend/.env` and configure:

```bash
GCP_PROJECT_ID=your-project-id       # Required for Gemini
GCP_REGION=us-central1               # Vertex AI region
USE_GEMINI=false                     # Set true when GCP is configured
USE_FIRESTORE=false                  # Set true for persistent storage
GEMINI_PROMPT_VERSION=v1             # Prompt config version
```

## Testing

### Backend (target: ≥90% coverage)

```bash
cd backend
python -m pytest --cov=app --cov-report=term-missing
```

### Frontend (target: ≥90% statements)

```bash
cd frontend
npm test -- --coverage
```

### E2E

```bash
cd frontend
npx playwright test
```

## Deployment

### Cloud Run (recommended)

```bash
# Build and push
docker build -t gcr.io/$PROJECT_ID/stadiumiq .
docker push gcr.io/$PROJECT_ID/stadiumiq

# Deploy
gcloud run deploy stadiumiq \
  --image gcr.io/$PROJECT_ID/stadiumiq \
  --platform managed \
  --region us-central1 \
  --set-env-vars "GCP_PROJECT_ID=$PROJECT_ID,USE_GEMINI=true,USE_FIRESTORE=true" \
  --allow-unauthenticated
```

The Cloud Run service account needs:
- `roles/aiplatform.user` (Vertex AI / Gemini)
- `roles/datastore.user` (Firestore)

## Assumptions

1. Stadium venue graph uses a realistic generic layout (~50 zones) configurable per venue
2. Gate count data is simulated in real-time for demo; production would integrate with turnstile hardware
3. Crowd density model uses FIFA Green Guide and Fruin LOS standards
4. Sustainability factors use FIFA 2026 Sustainability Strategy and EPA emission factors
5. Gemini responses are validated and bounded before display — hallucinated values trigger fallback
6. Anonymous device IDs provide history without collecting PII

## How This Maps to the Evaluation Rubric

| Criterion | Evidence |
|-----------|----------|
| **GenAI Integration** | `assistant/gemini.py` — Vertex AI Gemini with structured output, prompt versioning, response validation, graceful degradation |
| **Problem–Solution Fit** | 5 pillars (crowd, multilingual, accessibility, transport, sustainability) each with dedicated domain modules |
| **Architecture Quality** | Inward-only dependencies, Repository Protocol pattern, DI wiring, pure domain layer |
| **Code Quality** | Strict mypy + ruff (14 rule categories), Pydantic bounded models, enums, named constants with citations |
| **Testing** | ≥90% coverage gate, unit/integration/E2E pyramid, axe accessibility per component |
| **Accessibility** | Semantic HTML, ARIA live regions, skip link, focus-visible, reduced motion, contrast ratios documented |
| **Security** | ADC (no API keys), body size guard, rate limiting, security headers, AI output validation, non-root Docker |
| **Efficiency** | TTL + lru_cache multi-layer caching, lazy imports, asyncio.to_thread, Promise.all, multi-stage Docker |
| **Google Services** | Gemini (meaningful AI assistance), Firestore (persistent fan query history), ADC authentication |
| **Sustainability** | Per-match carbon footprint tracker with FIFA 2026 targets, transport mix analysis |
| **Multilingual** | 9-language support via Gemini + template fallback, language selector UI |
| **Deployment** | Dockerfile, Cloud Run instructions, CI/CD pipeline, health endpoint |

## License

[MIT](LICENSE)
