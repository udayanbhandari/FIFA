# GOOGLE_SERVICES Blueprint

Rules extracted from client initialization, credential handling, prompt management, and service integration.
Every rule is domain-agnostic and applies to any project integrating Google Cloud services.

---

RULE: Lazy Initialization + lru_cache for Service Clients
WHAT: Google service clients (Gemini, Firestore) are initialized lazily — only when first needed — and cached with `@lru_cache` so credentials are loaded once per process. The cache key includes parameters (project_id, region) so different configurations get separate clients.
WHY IT SCORES: Client re-initialization on every request wastes time and loads credentials redundantly. Evaluators detect this as an efficiency anti-pattern. lru_cache combined with lazy import demonstrates both efficiency and clean dependency management.
HOW TO APPLY: Create a `@lru_cache` function that initializes and returns the client. Import the SDK inside this function (lazy import). Accept configuration parameters as function arguments (they become the cache key). Clear the cache in test fixtures.
SIGNAL IN REPO: backend/app/insights/gemini.py (lines 148–157: `@lru_cache` on `_get_gemini_client` with lazy `from google import genai`), backend/tests/test_gemini.py (test_gemini_client_is_cached verifies single initialization)

---

RULE: Application Default Credentials Only — No API Keys
WHAT: All authentication to Google services uses Application Default Credentials (ADC). No API keys exist in the codebase or environment. In production, the Cloud Run service account provides credentials automatically. Locally, `gcloud auth application-default login` provides credentials. The `.env.example` explicitly documents this choice.
WHY IT SCORES: ADC is the most secure and manageable authentication method. API keys can leak. Evaluators scan for API key patterns and flag them. Using ADC means there is no secret management problem — credentials are platform-native.
HOW TO APPLY: Initialize clients with `vertexai=True` (for Vertex AI) or with just a project ID (for Firestore). Never set `api_key` parameters. Document in `.env.example` that credentials come from ADC. In README, mention that the service account needs specific IAM roles.
SIGNAL IN REPO: backend/app/insights/gemini.py (line 157: `genai.Client(vertexai=True, project=..., location=...)`), backend/app/repository/firestore_repo.py (line 35: `firestore.Client(project=project_id)` — no credentials parameter), .env.example (line 4: "credentials come from the runtime service account (Application Default Credentials)")

---

RULE: Prompt Versioning via External Config Files
WHAT: AI prompts live in versioned YAML files (`prompts/v1.yaml`), not in code strings. The version is selected by an environment variable (`GEMINI_PROMPT_VERSION`). This enables A/B testing, rollback, and prompt tuning without code changes. The config includes: system instruction, response schema, temperature, and max output tokens.
WHY IT SCORES: Hardcoded prompts are an anti-pattern — they require code changes for tuning. Versioned config files demonstrate mature AI integration. Evaluators value the separation of prompt content from code logic.
HOW TO APPLY: Create a `prompts/` directory with versioned YAML files (v1.yaml, v2.yaml). Load the config via a cached function. Include the system instruction, response schema, temperature, and token limits. Select the version via an environment variable. Provide inline defaults as fallback if the file is missing.
SIGNAL IN REPO: backend/app/insights/prompts/v1.yaml (system_instruction, response_schema, temperature, max_output_tokens), backend/app/insights/gemini.py (lines 61–73: _load_prompt_config with fallback), backend/app/config.py (line 32: gemini_prompt_version setting)

---

RULE: Structured Output Schema for Reliable AI Responses
WHAT: The Gemini call specifies `response_mime_type="application/json"` and provides a `response_schema` that defines the exact shape of the expected output. This forces the model to produce structured, parseable JSON instead of free-form text. The schema specifies required fields, types, and nested structure.
WHY IT SCORES: Unstructured AI output is unreliable. Evaluators check whether AI responses are parsed safely. A response schema with mime type enforcement demonstrates production-grade AI integration.
HOW TO APPLY: Always use `response_mime_type="application/json"` when you need structured output. Provide a JSON schema specifying the exact shape, types, and required fields. Parse the response with `json.loads()`. Validate the parsed result before using it.
SIGNAL IN REPO: backend/app/insights/gemini.py (lines 177–183: GenerateContentConfig with response_mime_type and response_schema), backend/app/insights/prompts/v1.yaml (lines 13–35: full response schema definition)

---

RULE: AI Output Trust Rule — Validate Before Use
WHAT: After parsing the AI response, run a validation function that checks: (1) all categories are from a known whitelist, (2) all numeric values are positive, (3) no value exceeds a logical bound (e.g., savings cannot exceed total footprint), (4) text fields are bounded in length. If validation fails, fall back to the deterministic engine.
WHY IT SCORES: AI models hallucinate. Trusting raw AI output is a security and reliability risk. Evaluators specifically check whether AI responses are validated. This rule transforms an unreliable AI call into a reliable feature.
HOW TO APPLY: Create a `_validate_ai_response(payload, context)` function. Check every field against known bounds. Use frozenset for category whitelists. Raise ValueError on any violation. Catch the exception in the caller and trigger the fallback path.
SIGNAL IN REPO: backend/app/insights/gemini.py (lines 119–145: _validate_gemini_response; lines 187–189: validation called before response is used; lines 251–258: broad except triggers fallback)

---

RULE: Graceful Degradation — Never Fail to Serve
WHAT: When a Google service is unavailable (disabled, no credentials, network failure, quota exceeded, malformed response), the system transparently falls back to a deterministic alternative. The public API entry point catches ALL exceptions from the service call and returns the fallback result. The response is tagged with its source ("gemini", "rules", "cache") so users and logs know which path was taken.
WHY IT SCORES: Graceful degradation is a top-tier architectural signal. It means the system is always functional — evaluators value reliability above all. Tagging the source demonstrates transparency and observability.
HOW TO APPLY: Wrap every external service call in a try/except that catches `Exception` (deliberately broad for degradation). In the except handler, log the error and return the fallback result. Tag every response with a `source` field. Design the fallback to be a full-featured alternative, not a stub.
SIGNAL IN REPO: backend/app/insights/gemini.py (lines 248–258: broad except catches any failure, logs it, returns rule-based insights), backend/app/models.py (line 91: `source: Literal["gemini", "rules", "cache"]`), docs/ARCHITECTURE.md (line 37: "Graceful degradation" listed as design rule)

---

RULE: Repository Protocol Enables Backend Swapping
WHAT: The persistence layer uses a `Protocol` (structural typing) interface with two implementations. The DI module reads a feature flag (USE_FIRESTORE) and selects the implementation. Routes depend on the Protocol type, never on a concrete class. This means switching from Firestore to any other database requires only a new implementation file — no route changes.
WHY IT SCORES: The repository pattern with Protocol typing is a sophisticated architectural pattern. It proves the developer can design for swappability. Evaluators detect direct database coupling in routes as an anti-pattern.
HOW TO APPLY: Define a Protocol class with the methods your routes need. Create at least two implementations (real and in-memory). Wire selection in a DI module using configuration flags. Import only the Protocol type in route handlers.
SIGNAL IN REPO: backend/app/repository/base.py (EntryRepository Protocol), backend/app/repository/firestore_repo.py, backend/app/repository/memory_repo.py (two implementations), backend/app/deps.py (configuration-driven selection), backend/app/routes/entries.py (depends on EntryRepository, not FirestoreEntryRepository)

---

RULE: Meaningful Integration Over Shallow Integration
WHAT: A Google service "counts" when it provides unique value that no local code could replicate. Gemini provides personalized, natural-language advice — the rule engine is the fallback, not the feature. Firestore provides persistent, queryable storage — the in-memory store is for dev/test only. Each service has a clear purpose documented in the architecture.
WHY IT SCORES: Evaluators can distinguish between meaningful and shallow integration. Importing a SDK without using it adds no value. Using it for a core feature (personalized advice, persistent history) demonstrates that the service is essential, not decorative.
HOW TO APPLY: For each service you integrate, answer: "What does this provide that local code cannot?" If the answer is "nothing," remove it. Document the value in your architecture document. Build a full-featured fallback so the service is an enhancement, not a dependency.
SIGNAL IN REPO: docs/ARCHITECTURE.md (lines 28–29: Gemini provides "the richest, most personal advice"; Firestore provides persistent anonymous tracking), README.md (lines 62–70: Gemini's unique value is natural-language advice, rule engine is the fallback)

---

RULE: DI Wires Services Without Coupling
WHAT: Google service clients are created in the DI module (`deps.py`) and injected via FastAPI's `Depends()`. Routes never import or construct service clients directly. The DI module reads configuration and makes the implementation choice. Service-specific code stays inside the service module.
WHY IT SCORES: Dependency injection is a standard quality pattern. Evaluators detect service construction inside route handlers as coupling. Clean DI demonstrates separation of concerns between wiring and logic.
HOW TO APPLY: Create a `deps.py` module with factory functions decorated with `@lru_cache`. Each factory reads configuration and returns the appropriate implementation. In route handlers, declare dependencies with `Depends(get_repository)`. Never import concrete implementations in routes.
SIGNAL IN REPO: backend/app/deps.py (get_repository factory with lru_cache), backend/app/routes/entries.py (repo: EntryRepository = Depends(get_repository)), backend/app/routes/calculate.py (settings: Settings = Depends(get_settings))

---

RULE: Persistence Captures Complete Snapshots
WHAT: Each stored entry captures the complete input AND the complete result at the time of saving — not just a summary. This means the history shows exactly what the user entered and what they were told, enabling trend analysis and audit. Entries are keyed by a random device ID with no personal data.
WHY IT SCORES: Complete snapshots demonstrate data-design thinking. Evaluators value persistence schemas that capture enough data to be useful for the stated feature (tracking trends over time). Minimal PII demonstrates privacy awareness.
HOW TO APPLY: Store both the input and the output together in each entry. Include a timestamp (ISO-8601 UTC). Key by an anonymous identifier, not by personal data. Use Firestore subcollections or equivalent scoping to partition data per user.
SIGNAL IN REPO: backend/app/repository/firestore_repo.py (lines 47–53: stores created_at, input (full CarbonInput), result (full FootprintResult)), backend/app/models.py (lines 95–107: EntryCreate includes device_id, input, result; Entry adds id and created_at)
