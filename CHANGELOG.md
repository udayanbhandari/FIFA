# Changelog

All notable changes to StadiumIQ are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-07

### Added

- Real-time crowd density estimation using FIFA Green Guide and Fruin LOS standards
- AI congestion prediction with zone-level rerouting suggestions
- Gemini-powered multilingual fan assistant supporting 9 languages (EN, ES, FR, AR, PT, DE, JA, KO, ZH)
- Deterministic rule engine fallback ensuring 100% uptime without AI dependency
- A* accessible wayfinding with wheelchair, visual, hearing, and cognitive need support
- Nearest accessible facility finder (restrooms, medical, concessions)
- Per-match sustainability footprint calculator with FIFA 2026 target comparison
- Transport mode analysis (metro, bus, rideshare, walk, accessible shuttle)
- Prompt versioning via external YAML configuration (v1)
- TTL cache with SHA-256 input hashing for AI response deduplication
- Repository pattern with Firestore (production) and in-memory (dev/test) implementations
- Security headers middleware (CSP, X-Frame-Options, nosniff, Permissions-Policy)
- Body size limiter middleware (64 KB guard)
- Rate limiting on AI-powered endpoints (10 req/min per IP)
- Structured JSON logging with latency tracking
- Multi-stage Docker build (Node build → Python 3.12-slim runtime, non-root)
- 4-job CI pipeline (backend quality, frontend quality, E2E, API drift)
- Full accessibility: skip link, ARIA live regions, focus-visible, reduced motion, documented contrast ratios
- axe accessibility assertion in every component test
- ≥90% test coverage gates enforced in CI
