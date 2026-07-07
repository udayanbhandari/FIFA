# EFFICIENCY Blueprint

Rules extracted from statelessness, caching, async I/O, repository abstraction, and build optimization.
Every rule is domain-agnostic and applies to any project on any topic.

---

RULE: Core Logic is Stateless and Pure
WHAT: The core computation engine is a pure function — same input always produces same output, no I/O, no side effects, no database calls. It imports only domain models and constants. This makes it deterministic, cacheable, and trivially testable.
WHY IT SCORES: Pure functions are the gold standard for code quality evaluators. They eliminate entire categories of bugs (race conditions, I/O failures, non-determinism). The engine can be called from any context (routes, tests, CLI) without setup.
HOW TO APPLY: Identify the core computation of your domain. Put it in a dedicated module with zero I/O imports (no database, no HTTP, no filesystem). Accept typed input, return typed output. Test it with unit tests that need no mocking.
SIGNAL IN REPO: backend/app/carbon/calculator.py (module docstring states "Pure, deterministic, side-effect-free functions: the same input always yields the same output, with no I/O"), backend/app/carbon/factors.py (module-level constants only, no functions that perform I/O)

---

RULE: Multi-Layer Caching with Clear Invalidation
WHAT: Caching is applied at three levels: (1) singleton settings via `@lru_cache` (never re-parsed per request), (2) singleton repository via `@lru_cache` (never re-created per request), (3) TTL cache for expensive API responses (60s TTL, SHA-256 input hash as key, thread-safe via lock). Each cache level has a clear invalidation strategy: lru_cache is cleared in tests, TTL cache self-invalidates.
WHY IT SCORES: Multi-layer caching demonstrates efficiency awareness. Evaluators detect repeated expensive operations (credential loading, API calls) as performance anti-patterns. SHA-256 keyed TTL caching shows sophisticated cache design.
HOW TO APPLY: Use `@lru_cache` for process-lifetime singletons (settings, clients, repositories). Use `TTLCache` for expensive operations with time-bounded freshness. Key TTL caches by a SHA-256 hash of the serialized input. Protect shared caches with a threading lock. Always clear caches in test fixtures.
SIGNAL IN REPO: backend/app/config.py (lru_cache on get_settings), backend/app/deps.py (lru_cache on get_repository), backend/app/insights/gemini.py (lines 57–58: TTLCache with SHA-256 key, lines 229–238: cache check with lock), backend/tests/conftest.py (cache_clear calls in fixtures)

---

RULE: Lazy Cloud SDK Imports
WHAT: Cloud SDKs (Google Firestore, Google GenAI) are imported inside the functions that use them, not at module top level. This means importing the module never triggers credential loading, so local development and CI never need cloud credentials.
WHY IT SCORES: Lazy imports reduce startup cost and eliminate unnecessary dependencies. Evaluators that analyze import graphs see cleaner dependency trees. It also means the test suite runs without any cloud setup — a strong testability signal.
HOW TO APPLY: Import heavy or credential-requiring SDKs inside the function that first uses them, not at the module level. Guard with the feature flag check before the import. This keeps the import path clean for offline/test scenarios.
SIGNAL IN REPO: backend/app/insights/gemini.py (line 155: `from google import genai` inside `_get_gemini_client`; line 169: `from google.genai import types` inside `_call_gemini`), backend/app/repository/firestore_repo.py (line 33: `from google.cloud import firestore` inside `__init__`)

---

RULE: Async I/O via Thread Wrapping for Sync SDKs
WHAT: When the SDK provides only synchronous methods (Firestore client, Gemini SDK), async route handlers use `asyncio.to_thread()` to run the sync call in a thread pool. This avoids blocking the event loop under concurrent load. The async wrappers (`async_add`, `async_list_for_device`) are defined in the repository Protocol so callers don't need to know the I/O strategy.
WHY IT SCORES: Blocking the event loop is a performance anti-pattern that evaluators detect. Using `to_thread` demonstrates understanding of async concurrency. Defining async methods in the Protocol interface shows clean abstraction.
HOW TO APPLY: For sync SDKs in async frameworks, wrap calls with `asyncio.to_thread(sync_function, *args)`. Define both sync and async method signatures in the interface. In-memory implementations can skip the thread (instant operations). Real implementations delegate to to_thread.
SIGNAL IN REPO: backend/app/repository/firestore_repo.py (lines 88–94: async_add and async_list_for_device use asyncio.to_thread), backend/app/repository/memory_repo.py (lines 42–48: async methods call sync directly, no thread needed), backend/app/insights/gemini.py (line 250: `await asyncio.to_thread(_call_gemini, ...)`)

---

RULE: Repository Pattern Decouples Domain from Storage
WHAT: A `Protocol` interface defines the persistence contract (add, list_for_device, async variants). Two implementations exist: Firestore (production) and in-memory (dev/tests). The choice is made once at startup via configuration and injected through DI. Business logic never references a specific database.
WHY IT SCORES: The repository pattern is a high-value architectural signal. It proves the developer can swap storage backends without touching business logic. It enables testing without a real database. Evaluators detect direct database calls in route handlers as a coupling anti-pattern.
HOW TO APPLY: Define a Protocol class with the CRUD methods your domain needs. Create at least two implementations: one real (database) and one fake (in-memory). Wire the selection in a DI module that reads from configuration. Inject the interface type in route handlers via framework DI.
SIGNAL IN REPO: backend/app/repository/base.py (EntryRepository Protocol), backend/app/repository/firestore_repo.py (real implementation), backend/app/repository/memory_repo.py (test/dev implementation), backend/app/deps.py (configuration-driven selection via lru_cached factory)

---

RULE: Parallel API Calls with Promise.all
WHAT: When two independent API calls are needed (calculate + insights), they are fired in parallel with `Promise.all([api.calculate(input), api.getInsights(input)])`. This halves the perceived latency compared to sequential calls.
WHY IT SCORES: Evaluators detect sequential independent API calls as an efficiency anti-pattern. Using Promise.all demonstrates understanding of async concurrency on the frontend. It directly improves user-perceived performance.
HOW TO APPLY: Identify independent API calls that don't depend on each other's results. Wrap them in `Promise.all()`. Destructure the results. Only use sequential calls when one call's output is the other's input.
SIGNAL IN REPO: frontend/src/hooks/useFootprint.ts (line 43: `const [calc, ins] = await Promise.all([api.calculate(input), api.getInsights(input)])`)

---

RULE: Docker Layer Ordering for Cache Efficiency
WHAT: The Dockerfile orders layers from least-frequently-changed to most-frequently-changed: (1) base image, (2) system config, (3) dependency install (requirements.txt/package.json first, then `npm ci`/`pip install`), (4) application code last. This means changing application code doesn't rebuild dependencies.
WHY IT SCORES: Layer ordering is a Docker best practice that evaluators check. Proper ordering dramatically reduces build times and demonstrates understanding of container caching mechanics.
HOW TO APPLY: Always COPY dependency manifests (requirements.txt, package.json, package-lock.json) before application code. Run the install command between the manifest copy and the code copy. Use `npm ci` (not `npm install`) for deterministic installs. Use `pip install --no-cache-dir`.
SIGNAL IN REPO: Dockerfile (lines 9–12: COPY package.json then npm ci then COPY frontend/; lines 25–29: COPY requirements.txt then pip install then COPY backend/app)

---

RULE: Multi-Stage Build for Minimal Runtime Image
WHAT: The Dockerfile uses a multi-stage build: stage 1 (Node) builds the frontend, stage 2 (Python slim) runs the backend and serves the built static assets. The final image contains no Node.js, no frontend source, no dev dependencies. This produces a minimal production image.
WHY IT SCORES: Multi-stage builds demonstrate production-readiness and security awareness. Smaller images have less attack surface and deploy faster. Evaluators check for dev dependencies in production images as a vulnerability.
HOW TO APPLY: Use a builder stage for compilation (frontend build, Go compile, etc.). Use a slim runtime stage for the final image. COPY only the build output from the builder stage. Never install dev dependencies in the runtime stage.
SIGNAL IN REPO: Dockerfile (line 7: `FROM node:20-alpine AS frontend` for build; line 15: `FROM python:3.12-slim AS runtime` for production; line 30: `COPY --from=frontend /frontend/dist ./static`)

---

RULE: Format/Utility Functions Never Do I/O
WHAT: Display formatting functions (formatKg, formatTonnes, categoryLabel, formatDate) are pure transformations with no I/O, no side effects, no imports from API or state modules. They live in a dedicated `lib/format.ts` file with its own test file.
WHY IT SCORES: Pure utility functions are a signal of clean architecture. They are independently testable without mocking. Evaluators flag utilities that import React, fetch, or state management as design flaws.
HOW TO APPLY: Create a `format.ts` (or `utils.ts`) file with only pure transformation functions. Never import framework code, HTTP clients, or state libraries. Test each function with simple input/output assertions.
SIGNAL IN REPO: frontend/src/lib/format.ts (four pure functions, zero imports from React or API), frontend/src/lib/format.test.ts (tests are pure assertions with no mocking)

---

RULE: Structured Logging Captures Latency Without Adding Cost
WHAT: Logging uses a JSON formatter with first-class fields (endpoint, latency_ms, source, device_id_hash) that can be queried in cloud logging without parsing free-text messages. Latency is captured with `time.monotonic()` (low overhead). Log messages are short strings; structured data goes in `extra={}`.
WHY IT SCORES: Structured logging is a production-readiness signal. Evaluators detect print-statement logging and unstructured messages as quality gaps. First-class JSON fields enable monitoring dashboards without log parsing.
HOW TO APPLY: Use `python-json-logger` or equivalent. Define standard fields (endpoint, latency_ms, source) as `extra` dict keys. Use `time.monotonic()` for latency measurement (not `time.time()`). Hash any identifiers before logging. Rename fields to match cloud logging conventions (asctime→timestamp, levelname→severity).
SIGNAL IN REPO: backend/app/main.py (lines 48–65: _configure_logging with JsonFormatter, field renaming), backend/app/insights/gemini.py (lines 267–279: _log_insight with latency_ms, source, device_id_hash as structured fields)

---

RULE: Build Optimization: Sourcemaps Off, Coverage Excluded from Bundle
WHAT: Vite build config disables sourcemaps in production (`sourcemap: false`). Test setup files, type declarations, and test files are excluded from coverage measurement. The CSS build is disabled in test mode to speed up test runs.
WHY IT SCORES: Production sourcemaps leak code structure. Correct coverage exclusions prevent inflated metrics. Evaluators check build configuration for production-readiness signals.
HOW TO APPLY: Set `sourcemap: false` in production builds. Exclude entry points, test setup, type declarations, and test files from coverage measurement. Disable CSS processing in test mode.
SIGNAL IN REPO: frontend/vite.config.ts (line 16: `sourcemap: false`; line 22: `css: false` in test config; lines 27: coverage excludes main.tsx, test/, *.d.ts, *.test.*)
