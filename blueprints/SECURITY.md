# SECURITY Blueprint

Rules extracted from authentication, validation, headers, rate limiting, and supply chain practices.
Every rule is domain-agnostic and applies to any project on any topic.

---

RULE: Secrets Never Exist in Code — Structural Enforcement
WHAT: No API keys, tokens, or credential files exist anywhere in the repository. Authentication uses platform-native credential mechanisms (e.g., Application Default Credentials for GCP, IAM roles for AWS). The `.env.example` file documents required variables but contains only safe defaults. The `.gitignore` blocks `.env`, `*.key.json`, and `service-account*.json` patterns.
WHY IT SCORES: AI evaluators scan for secrets in code as a critical security failure. Using ADC/IAM means there is literally no secret to leak. The structural decision (no key → no risk) is stronger than any runtime check.
HOW TO APPLY: Choose platform-native credential mechanisms (ADC, IAM roles, managed identity) for all cloud services. Never create an API key when a service account will work. Add all secret patterns to `.gitignore`. Create `.env.example` with placeholder values and comments — never real credentials. Add `detect-private-key` to pre-commit hooks.
SIGNAL IN REPO: .env.example (no secrets, only project ID and feature flags), .gitignore (lines 21–26: blocks .env, key files, service account files), .pre-commit-config.yaml (detect-private-key hook), backend/app/config.py docstring ("No secret values live here")

---

RULE: Validated Configuration at Startup
WHAT: All configuration is loaded through a validated settings class (pydantic-settings `BaseSettings`) so invalid or missing values are caught at process startup, not at request time. The settings object is cached as a singleton (`@lru_cache`) to avoid re-parsing.
WHY IT SCORES: Fail-fast configuration prevents runtime surprises. Evaluators detect string-based `os.getenv()` calls without validation as a fragility signal. Pydantic validation ensures type correctness and provides clear error messages.
HOW TO APPLY: Create a `Settings(BaseSettings)` class with typed fields and defaults. Use `SettingsConfigDict` to specify the `.env` file and encoding. Cache the instance with `@lru_cache`. Access settings only through the cached factory function, never through raw `os.getenv()`.
SIGNAL IN REPO: backend/app/config.py (Settings class with typed fields, lru_cache on get_settings()), backend/app/deps.py (uses get_settings() not os.getenv())

---

RULE: Input Validation at the Boundary via Schema Models
WHAT: Every API input is validated by a Pydantic model with bounded fields before any business logic runs. Bounds are generous enough for real users but finite (e.g., max 20,000 km/week, max 200 flights/year). The schema IS the validation — no separate validation code needed.
WHY IT SCORES: Boundary validation prevents injection, overflow, and nonsensical inputs. Evaluators check whether unbounded inputs can reach business logic. Pydantic models that validate AND document simultaneously score higher than manual validation.
HOW TO APPLY: Define upper bounds as named constants with explanatory comments. Use `Field(ge=0, le=MAX_VALUE)` for every numeric input. Use `min_length`, `max_length`, and `pattern` for strings (especially identifiers). Mirror these bounds in the frontend form's `min`/`max` attributes.
SIGNAL IN REPO: backend/app/models.py (every field bounded), frontend/src/components/CalculatorForm.tsx (MAX constants mirror backend bounds in HTML min/max attributes)

---

RULE: Rate Limiting on Expensive Endpoints Only
WHAT: Rate limiting is applied selectively to endpoints that call expensive external services (10 req/min per IP on `/api/insights` which calls Gemini). Pure-computation endpoints like `/api/calculate` are not rate-limited. The limiter is keyed by client IP. Rate limit exceeded returns 429 with a `Retry-After` header.
WHY IT SCORES: Evaluators check for rate limiting as a security/efficiency measure. Selective application shows the developer understands which endpoints need protection and which don't, rather than applying a blanket limit.
HOW TO APPLY: Rate-limit only endpoints that cost money, make external calls, or are abuse-prone. Key by client IP. Return 429 with `Retry-After`. Place the limiter in a separate module to avoid circular imports. Do NOT rate-limit stateless computation endpoints.
SIGNAL IN REPO: backend/app/rate_limit.py (limiter singleton), backend/app/routes/calculate.py (line 21: @limiter.limit("10/minute") on insights only, calculate has no limiter), backend/app/main.py (429 handler with Retry-After)

---

RULE: Body Size Guard at the Middleware Layer
WHAT: A middleware rejects POST requests larger than 64 KB before the JSON parser runs. It performs two checks: (1) a fast header-check on `Content-Length`, and (2) a streaming byte count that catches clients who omit or forge the header. Non-numeric Content-Length values return 400.
WHY IT SCORES: Body-size limits prevent memory-exhaustion attacks. Evaluators detect the absence of size limits as a denial-of-service vulnerability. The two-layer check (header + streaming) demonstrates defense in depth.
HOW TO APPLY: Define `_MAX_BODY_BYTES` as a named constant. Implement middleware that checks the `Content-Length` header (fast path) and also reads actual bytes (trust-nothing path). Return 413 for oversized bodies and 400 for malformed headers. Do this BEFORE JSON parsing, not after.
SIGNAL IN REPO: backend/app/main.py (lines 31–146: body_size_limiter middleware with header check, streaming check, and ValueError handling)

---

RULE: AI/LLM Response Validation Before Trust
WHAT: Responses from AI services (Gemini) are validated against a whitelist of known values and bounded ranges before being used. Specific checks: (1) savings must be positive, (2) savings cannot exceed the user's total footprint, (3) categories must be from a known set (`frozenset`), (4) summary length is bounded. Any validation failure triggers a graceful fallback.
WHY IT SCORES: Evaluators check whether AI output is trusted blindly — a common vulnerability. Validating AI responses demonstrates security awareness and prevents hallucinated or adversarial values from reaching users.
HOW TO APPLY: Define a validation function that checks every field of the AI response against known bounds and allowed values. Use a `frozenset` for category whitelists. Raise `ValueError` on any violation. Catch all validation failures in the caller and fall back to a deterministic alternative.
SIGNAL IN REPO: backend/app/insights/gemini.py (lines 119–145: _validate_gemini_response checks savings bounds, known categories, summary length; line 189: validation called before response is used)

---

RULE: Anonymous Identity Without PII
WHAT: User identity is a random device ID generated client-side (crypto.randomUUID or timestamp fallback), stored in localStorage, and validated server-side with a regex pattern. No login, no email, no personal data collected. The device ID is hashed before logging.
WHY IT SCORES: Evaluators check for data minimization and PII handling. A random device ID gives functionality (tracking history) without collecting personal data. Hashing before logging demonstrates privacy-by-design.
HOW TO APPLY: Generate a random ID client-side using the platform CSPRNG. Store it in localStorage. Validate it server-side with `pattern=r"^[A-Za-z0-9_-]+$"` and length bounds. Hash it before including in log entries. Never store or log the raw identifier server-side.
SIGNAL IN REPO: frontend/src/lib/deviceId.ts (crypto.randomUUID with fallback, localStorage persistence), backend/app/models.py line 98 (device_id field with pattern and length validation), backend/app/insights/gemini.py line 226 (SHA-256 hash of device_id before logging)

---

RULE: Security Headers on Every Response
WHAT: A middleware adds security headers to every response: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`, `Permissions-Policy` (disabling geolocation, microphone, camera), and a `Content-Security-Policy` restricting sources. Headers use `setdefault` to avoid overwriting route-specific values.
WHY IT SCORES: Security headers are a standard checklist item for evaluators. CSP, frame-ancestors, and permission restrictions demonstrate defense in depth. Using `setdefault` shows the developer considered route-level overrides.
HOW TO APPLY: Define security headers as a module-level dict. Add middleware that applies them via `setdefault` to every response. Include CSP with `default-src 'self'`, frame-ancestors `'none'`, and restrict scripts and connections. Test that headers are present in the API test suite.
SIGNAL IN REPO: backend/app/main.py (lines 37–46: _SECURITY_HEADERS dict, lines 97–104: security_headers middleware), backend/tests/test_api.py (test_security_headers_present asserts X-Content-Type-Options, X-Frame-Options, CSP)

---

RULE: Non-Root Container with Minimal Surface
WHAT: The Dockerfile creates and switches to a non-root user (UID 10001) before running the application. The image is `python:3.12-slim` (minimal base). `.pyc` files are disabled. Only required files are copied. The `.dockerignore` excludes `.git`, `node_modules`, secrets, and documentation.
WHY IT SCORES: Running as non-root is a standard container security check. Evaluators flag root-running containers as a vulnerability. Slim base images reduce attack surface. Comprehensive `.dockerignore` prevents secret leakage into images.
HOW TO APPLY: Add `RUN useradd --create-home --uid 10001 appuser` and `USER appuser` after installing dependencies. Use `-slim` or `-alpine` base images. Set `PYTHONDONTWRITEBYTECODE=1`. Create a `.dockerignore` that excludes `.git`, `node_modules`, `.env*`, `*-key.json`, and documentation.
SIGNAL IN REPO: Dockerfile (lines 32–34: useradd + USER appuser, line 15: python:3.12-slim), .dockerignore (excludes secrets, .git, node_modules, docs)

---

RULE: Supply Chain Security via Pinned Actions and Dependabot
WHAT: GitHub Actions are pinned to full commit SHAs (not tags) to prevent supply-chain attacks. Dependabot is configured for three ecosystems (pip, npm, github-actions) with weekly checks. Dependencies in requirements.txt are pinned to exact versions with a comment about hash-pinning.
WHY IT SCORES: Evaluators check for pinned action versions as a supply-chain security signal. SHA pinning is stronger than tag pinning because tags can be moved. Dependabot keeps dependencies fresh, reducing vulnerability exposure.
HOW TO APPLY: Pin every `uses:` action to its full commit SHA with a comment showing the tag version. Configure Dependabot for every package ecosystem in your project (including actions). Pin runtime dependencies to exact versions. Document hash-pinning as an option for maximum security.
SIGNAL IN REPO: .github/workflows/ci.yml (lines 20–21: actions pinned to SHAs with tag comments), .github/dependabot.yml (three ecosystems: pip, npm, github-actions), backend/requirements.txt (exact version pins with supply-chain comment)

---

RULE: Error Messages Never Leak Implementation Details
WHAT: Error responses use generic, user-facing messages. Rate limit errors say "Rate limit exceeded" not the internal limit. Body size errors say "Request body too large" not the byte count. API 404s return `{"detail": "Not Found"}` not stack traces. Fallback errors say "Something went wrong" not exception details.
WHY IT SCORES: Evaluators check error responses for information leakage. Generic messages prevent attackers from fingerprinting the stack or probing for limits. Structured error responses (JSON with `detail` key) maintain API consistency.
HOW TO APPLY: Define error responses as simple `{"detail": "user-facing message"}` JSON. Never include exception messages, stack traces, or internal limits in responses. Log the detailed error server-side with structured logging, but return only the generic message to the client.
SIGNAL IN REPO: backend/app/main.py (lines 83–87: rate limit handler returns generic message; lines 129–137: body size returns generic "too large"), backend/app/insights/gemini.py (line 253: logs detailed error but returns rule-based fallback to user)
