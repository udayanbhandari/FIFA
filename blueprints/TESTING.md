# TESTING Blueprint

Rules extracted from test structure, fixtures, mocking strategy, coverage enforcement, and naming.
Every rule is domain-agnostic and applies to any project on any topic.

---

RULE: Test Layer Matches Code Layer
WHAT: Unit tests cover domain logic (pure calculators, validators, rules engines). Integration tests cover route handlers (via TestClient) exercising the full middleware stack. E2E tests cover the critical user flow through the actual UI. Each layer tests what only that layer can test — unit tests don't need HTTP, integration tests don't need a browser, E2E tests don't test math.
WHY IT SCORES: The testing pyramid is a quality signal evaluators check for. Having distinct test layers demonstrates mature testing strategy. Testing the right thing at the right layer prevents both test gaps and redundant tests.
HOW TO APPLY: Organize tests so each file tests one module at one layer. Unit tests for pure logic (no mocking needed). Integration tests for HTTP routes (using framework test clients). E2E tests for critical user flows (using Playwright). Name test files `test_{module}.py` (backend) or `{Component}.test.tsx` (frontend).
SIGNAL IN REPO: backend/tests/test_calculator.py (unit: pure math), backend/tests/test_api.py (integration: full HTTP stack via TestClient), frontend/e2e/calculator.spec.ts (E2E: full user flow through browser)

---

RULE: Minimum Test Count Per File Type
WHAT: Every meaningful source file has a corresponding test file with multiple test cases. Route files get ≥5 tests (happy path, validation rejection, error handling, security headers, edge cases). Model files get ≥5 tests (boundary validation for each bounded field). Calculator files get ≥8 tests (each calculation path, consistency checks, rounding). Component files get ≥3 tests (axe, rendering, interaction). Hook files get ≥5 tests (via App integration tests). Utility files get ≥4 tests (each function, edge cases).
WHY IT SCORES: Evaluators count test cases and check coverage per file. Files with many focused tests score higher than files with few broad tests. The variety of test types (boundary, interaction, accessibility) demonstrates thorough coverage.
HOW TO APPLY: For every source file, create a test file with at least: one happy-path test, one boundary/validation test, one error-handling test, and one accessibility test (for UI). Count your tests per file — if a file has fewer than 3 tests, it's likely undertested.
SIGNAL IN REPO: backend/tests/test_calculator.py (9 tests), backend/tests/test_gemini.py (12 tests), backend/tests/test_rules.py (9 tests), backend/tests/test_models.py (5 tests), frontend/src/components/CalculatorForm.test.tsx (5 tests), frontend/src/App.test.tsx (6 tests)

---

RULE: Fixtures for Reusable Setup, Inline for One-Off Data
WHAT: Shared setup (test client creation, environment overrides, cache clearing) lives in `conftest.py` fixtures. One-off test data (specific inputs, expected outputs) is created inline in the test function. Helper functions like `_ctx()` or `_add()` are local to the test file when used in multiple tests within that file.
WHY IT SCORES: Evaluators check whether tests are isolated and readable. Fixtures for shared setup prove the developer understands DRY in testing. Inline data for specific cases proves the developer values test readability over abstraction.
HOW TO APPLY: Put shared infrastructure (client creation, env setup, cache clearing) in conftest.py fixtures. Create per-file helper functions for repeated patterns within a test file. Keep test-specific data inline so each test is self-documenting.
SIGNAL IN REPO: backend/tests/conftest.py (client fixture: env setup, cache clearing, TestClient creation), backend/tests/test_gemini.py (_ctx() helper creates default data), backend/tests/test_firestore_repo.py (_add() helper, _Fake* classes local to file)

---

RULE: External Services are Always Mocked
WHAT: No test touches a real external service. The Firestore repository is tested against a hand-built fake client that mimics the Firestore API surface. Gemini is tested by patching `_call_gemini` or monkeypatching `google.genai.Client`. The in-memory repository IS the test implementation. Frontend API calls are mocked with `vi.mock()`.
WHY IT SCORES: Tests that require external services are fragile, slow, and non-deterministic. Evaluators check whether tests can run offline. Providing a fake implementation for testing shows architectural foresight (the repository pattern enables this).
HOW TO APPLY: Use monkeypatch/mock to replace external SDK clients with fake implementations. Build fakes that mimic only the API surface your code actually uses. Use feature flags (USE_FIRESTORE=false, USE_GEMINI=false) to select test-friendly implementations automatically.
SIGNAL IN REPO: backend/tests/test_firestore_repo.py (_FakeFirestoreClient mimics collection/document/set/stream), backend/tests/test_gemini.py (_fake_genai_client returns canned responses), backend/tests/conftest.py (USE_GEMINI=false, USE_FIRESTORE=false), frontend/src/App.test.tsx (vi.mock("./lib/api"))

---

RULE: Coverage Thresholds are Hard CI Gates
WHAT: Coverage thresholds are enforced in CI configuration, not just aspirational targets. Backend: `--cov-fail-under=90` in pytest config (100% achieved). Frontend: `statements: 90, branches: 85, functions: 90, lines: 90` in vitest coverage config. The build FAILS if coverage drops below thresholds.
WHY IT SCORES: Enforced coverage is qualitatively different from reported coverage. Evaluators detect the difference — a project that gates on coverage will never silently regress. This is one of the strongest testing signals.
HOW TO APPLY: Set coverage thresholds in your test runner's config file (not just CI scripts). Backend: `addopts = "--cov-fail-under=90"` in pyproject.toml. Frontend: `coverage.thresholds` in vitest config. Run coverage in CI as a gate, not a report.
SIGNAL IN REPO: backend/pyproject.toml (line 10: `--cov-fail-under=90`), frontend/vite.config.ts (lines 29–34: thresholds for statements, branches, functions, lines)

---

RULE: Route Tests Assert Status, Shape, and Content
WHAT: Every route test checks three things: (1) HTTP status code, (2) response shape (required keys, types), (3) meaningful content (not just "200 OK" but actual values). Validation rejection tests check for 422. Security tests check for specific headers.
WHY IT SCORES: Three-layer assertion catches regressions at every level. An evaluator that sees only `assert resp.status_code == 200` detects shallow testing. Full shape and content assertions demonstrate thorough coverage.
HOW TO APPLY: For every route test: assert the status code, assert the response body has the expected keys, assert at least one value is correct. For error cases: assert the specific 4xx status and the error message pattern.
SIGNAL IN REPO: backend/tests/test_api.py (test_calculate_returns_breakdown: status 200, checks set of keys, checks total > 0, checks comparison key exists; test_calculate_rejects_negative_values: status 422)

---

RULE: Component Tests Assert Rendering, Interaction, and Accessibility
WHAT: Every React component test has at minimum: (1) an axe accessibility assertion (`expect(await axe(container)).toHaveNoViolations()`), (2) rendering assertions (expected text/elements appear), (3) interaction assertions (user events trigger expected callbacks). Components with ARIA wiring get specific attribute assertions.
WHY IT SCORES: The axe assertion per component is a standout quality signal. Most projects skip accessibility testing entirely. Per-component axe plus interaction testing demonstrates the accessibility is real, not just claimed.
HOW TO APPLY: Import `axe` from `vitest-axe`. Add an axe test as the first test in every component describe block. Test user interactions with `@testing-library/user-event`. Assert callback invocations with `vi.fn()`. Check ARIA attributes with `toHaveAttribute` and `toHaveAccessibleDescription`.
SIGNAL IN REPO: frontend/src/components/CalculatorForm.test.tsx (axe assertion + form submission + loading state + aria-describedby + bounds check), frontend/src/components/NumberField.test.tsx (axe with and without hint, onChange emission, aria-describedby conditional rendering)

---

RULE: Axe Assertion on Every Component — No Exceptions
WHAT: Every component test file includes `import { axe } from "vitest-axe"` and has at least one test: `expect(await axe(container)).toHaveNoViolations()`. This is treated as a definition-of-done requirement in CONTRIBUTING.md.
WHY IT SCORES: Automated accessibility testing per component is rare and highly valued by evaluators. It proves accessibility is verified, not assumed. The pattern catches WCAG violations before they reach users.
HOW TO APPLY: Add `vitest-axe` as a dev dependency. Create a test setup file that extends `expect` with axe matchers. Create a type declaration file for axe matchers. Add an axe test as the first test in every component test file.
SIGNAL IN REPO: frontend/src/test/setup.ts (axe matchers registered), frontend/src/test/vitest-axe.d.ts (type declarations), every component test file has `expect(await axe(container)).toHaveNoViolations()` as its first test

---

RULE: E2E Tests Cover the Critical User Journey
WHAT: The E2E test exercises the complete user flow that no unit or integration test can: fill the form → calculate → verify results appear → verify insights appear → save to history → verify history updates. It also tests error handling by blocking API routes and verifying the error alert.
WHY IT SCORES: E2E tests prove the system works as a whole. Unit tests cannot catch integration bugs between frontend and backend. Evaluators value E2E tests that cover the primary user journey, not just smoke tests.
HOW TO APPLY: Identify the critical user flow (the one flow that must never break). Write one E2E test that exercises it end-to-end with real assertions at each step. Run against the full stack in offline mode (deterministic). Add one error-handling E2E test that simulates API failure.
SIGNAL IN REPO: frontend/e2e/calculator.spec.ts (7-step flow test with assertions at each step + error handling test with route blocking)

---

RULE: Test Names Describe Intent, Not Implementation
WHAT: Test names are complete sentences that describe the expected behavior from the user/caller perspective: `test_electric_car_lower_than_petrol`, `test_frequent_flyer_gets_flight_recommendation`, `test_insights_cache_returns_cached_result`. They never describe the implementation mechanism.
WHY IT SCORES: Descriptive test names serve as executable documentation. Evaluators that read test names can understand the system's behavior without reading the test body. Names like `test_1` or `test_function` are anti-patterns that score poorly.
HOW TO APPLY: Name tests as: `test_{scenario}_{expected_outcome}`. Use the format "when X happens, Y should result." Include the domain concept in the name. Never use numbers or implementation details (e.g., avoid `test_mock_works`).
SIGNAL IN REPO: backend/tests/test_calculator.py (test_home_energy_split_by_household_size, test_flights_use_representative_distances), backend/tests/test_rules.py (test_frequent_flyer_gets_flight_recommendation, test_already_green_user_still_gets_constructive_summary)

---

RULE: CI Test Execution Order: Fast → Slow, Gate → Deploy
WHAT: CI runs in parallel jobs with dependencies: (1) backend job (lint → format → types → tests), (2) frontend job (typecheck → lint → format → tests → build), (3) E2E job (runs only on push, needs backend+frontend to pass first), (4) API drift job (needs backend). Faster checks run first to fail fast.
WHY IT SCORES: Ordered CI with dependency gates demonstrates professional DevOps. Fast failures save CI minutes. Conditional E2E (push only, not PR) shows cost awareness.
HOW TO APPLY: Order checks from fastest to slowest within each job (lint before tests). Use `needs:` to gate expensive jobs on cheaper ones. Run E2E only on merge to main (not every PR). Run drift detection as a separate job.
SIGNAL IN REPO: .github/workflows/ci.yml (backend and frontend jobs run in parallel; E2E job has `needs: [backend, frontend]` and `if: github.event_name == 'push'`; api-drift job has `needs: [backend]`)
