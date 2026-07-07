# StadiumIQ Architecture

This document describes the system architecture, layer responsibilities, design rules, and frontend structure. It explains **why** each layer exists, not just what files are in it.

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Browser (Fan / Operator)                  │
│  ┌────────────┐ ┌───────────┐ ┌──────────┐ ┌────────────────┐  │
│  │FanAssistant│ │ CrowdMap  │ │Wayfinding│ │ Sustainability │  │
│  └─────┬──────┘ └─────┬─────┘ └────┬─────┘ └───────┬────────┘  │
│        └──────────────┼────────────┼────────────────┘           │
│                       │ useStadium hook                          │
│                       ▼                                          │
│                  api.ts (typed HTTP client)                      │
└──────────────────────┬──────────────────────────────────────────┘
                       │ HTTPS (JSON)
┌──────────────────────▼──────────────────────────────────────────┐
│                    FastAPI Application                           │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Middleware: BodySize → SecurityHeaders → CORS → RateLimit│    │
│  └─────────────────────────────────────────────────────────┘    │
│                       │                                          │
│  ┌────────────────────▼────────────────────────────────────┐    │
│  │              Transport (routes/)                          │    │
│  │  crowd.py │ assist.py │ wayfinding.py │ sustainability.py│    │
│  └────────────────────┬────────────────────────────────────┘    │
│          ┌────────────┼─────────────┐                           │
│          ▼            ▼             ▼                           │
│  ┌──────────────┐ ┌────────────┐ ┌──────────────────┐          │
│  │ Domain (pure) │ │  Insights  │ │   Persistence    │          │
│  │ crowd/        │ │ assistant/ │ │   repository/    │          │
│  │ wayfinding/   │ │ gemini.py  │ │   base.py        │          │
│  │ sustainability│ │ rules.py   │ │   firestore_repo │          │
│  └──────────────┘ └────────────┘ │   memory_repo    │          │
│                                   └──────────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

## Layer Responsibilities

| Layer | Module(s) | Rule | Why It Exists |
|-------|-----------|------|---------------|
| **Domain** | `crowd/density.py`, `crowd/factors.py`, `wayfinding/navigator.py`, `wayfinding/venue_graph.py`, `sustainability/tracker.py` | **No I/O** — pure computation only | Deterministic crowd models, pathfinding, and footprint calculations must be testable without network, database, or AI |
| **Insights** | `assistant/gemini.py`, `assistant/rules.py`, `assistant/prompts/` | **Graceful degradation** — Gemini → rules fallback | AI enriches responses but must never be required; the rule engine guarantees 100% availability |
| **Persistence** | `repository/base.py`, `repository/firestore_repo.py`, `repository/memory_repo.py` | **Protocol interface** — two implementations | Fan query history requires storage, but tests and local dev must work without Firestore |
| **Transport** | `routes/crowd.py`, `routes/assist.py`, `routes/wayfinding.py`, `routes/sustainability.py`, `routes/health.py` | **Depends on abstractions** — never imports concrete implementations | Routes validate input, call domain/insight layers, return typed responses |
| **Composition** | `config.py`, `deps.py`, `main.py`, `rate_limit.py` | **Owns no logic** — only wiring and infrastructure | Configuration, DI, middleware, and app factory are separate from business logic |

## Design Rules

- **Graceful Degradation**: Every external dependency (Gemini, Firestore) has a full-featured fallback. Every response is tagged with its `source` ("gemini", "rules", "cache"). The system is always operational.

- **Inward-Only Dependencies**: Transport → Domain → Models. The domain layer imports nothing from routes or framework code. Routes depend on Protocol interfaces, never concrete implementations.

- **Accessibility-First**: Every UI component uses semantic HTML, ARIA landmarks, and live regions. Every component test includes an axe assertion. Color never conveys information alone.

- **Stateless Core**: Domain computation functions are pure — same input always produces same output, no I/O, no side effects. This makes them cacheable, testable, and deterministic.

## Frontend Structure

| Directory | Contents | Rule |
|-----------|----------|------|
| `components/` | `FanAssistant`, `CrowdHeatmap`, `WayfindingPanel`, `SustainabilityDashboard`, `TransportPanel`, `LanguageSelector` | One component per visual concern; each has co-located `.test.tsx` |
| `hooks/` | `useStadium` | Returns state + actions; owns all API calls; components never call fetch |
| `lib/` | `api.ts`, `types.ts`, `format.ts`, `deviceId.ts` | Pure utilities and typed clients; zero React imports in `format.ts` |
| `styles/` | `theme.css` | CSS custom properties with documented contrast ratios, dark mode, focus-visible, reduced-motion |

## Quality Gates Reference

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the full quality gates table and coding conventions.
