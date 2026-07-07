# CODE_QUALITY Blueprint

Rules extracted from architecture, naming, typing, tooling, and writing conventions.
Every rule is domain-agnostic and applies to any project on any topic.

---

## ARCHITECTURE RULES

---

RULE: Inward-Only Dependency Direction
WHAT: Dependencies always point inward: transport/routes → domain logic → models. The domain (pure-logic) layer imports nothing from the layers above it. Routes depend on abstract interfaces (Protocol), never on concrete implementations.
WHY IT SCORES: AI evaluators detect import cycles and bidirectional coupling as structural defects. A clean dependency graph signals professional architecture. It also proves the developer understands separation of concerns beyond just "put things in folders."
HOW TO APPLY: Draw your layers as concentric circles. Code in an inner circle must never import from an outer circle. Enforce this by checking that domain modules have zero imports from routes, middleware, or framework code. Use a Protocol/interface for persistence so the domain layer never references a database SDK.
SIGNAL IN REPO: backend/app/carbon/calculator.py (imports only from models and factors — zero framework imports), backend/app/repository/base.py (Protocol interface), backend/app/routes/entries.py (imports the Protocol, not the Firestore implementation)

---

RULE: One-Responsibility-Per-File Splitting
WHAT: Every file has exactly one reason to exist, named after what it does. A new file is created when a new concept appears (e.g., rate limiting is its own module, not buried in main.py). A new folder is created when a concept has multiple files (e.g., repository/ has base.py, firestore_repo.py, memory_repo.py).
WHY IT SCORES: Evaluators measure cohesion per file. When a file does one thing, its line count stays small, its test file can be named `test_{thing}.py`, and reviewers can understand it in isolation. High cohesion per file is one of the strongest signals of code quality.
HOW TO APPLY: If a function serves a different concern than the file's stated purpose, move it. If a module grows beyond ~150 lines, look for a concept that deserves extraction. Name the new file after the concept, not the action.
SIGNAL IN REPO: backend/app/rate_limit.py (15 lines, exists solely to avoid circular imports and isolate the limiter singleton), backend/app/config.py (47 lines, only configuration), backend/app/deps.py (27 lines, only DI wiring)

---

RULE: Explicit Layer Responsibility Table
WHAT: Document each layer's responsibility in a table in ARCHITECTURE.md, stating what the layer does and what rule it follows. This makes responsibilities unambiguous and prevents "responsibility bleed."
WHY IT SCORES: An AI evaluator can verify that the documented responsibilities match the actual code. Documenting layers also signals that the developer designed the architecture intentionally rather than letting it emerge ad-hoc.
HOW TO APPLY: Create a table with columns: Layer, Module(s), Rule. Fill it for every directory. The "Rule" column should be a constraint, not a description (e.g., "No I/O" not "Handles data").
SIGNAL IN REPO: docs/ARCHITECTURE.md (lines 25–31: a table mapping Domain, Insights, Persistence, Transport, Composition to their modules and rules)

---

RULE: Convention-Based Naming Taxonomy
WHAT: Every file type has a naming convention that reveals its role: `calculator.py` for domain logic, `factors.py` for constants, `models.py` for schemas, `base.py` for abstractions, `{thing}_repo.py` for implementations, `{verb}.py` for routes, `use{Noun}.ts` for hooks, `{PascalCase}.tsx` for components, `{name}.test.{ext}` for tests co-located next to their source.
WHY IT SCORES: Consistent naming lets evaluators predict file contents from the name alone. It reduces cognitive load and demonstrates disciplined project organization.
HOW TO APPLY: Define a naming table in your contributing guide. Enforce it in code review. Route files are verbs (calculate, entries, health). Model files are nouns. Test files mirror source files with `.test.` inserted.
SIGNAL IN REPO: backend/app/routes/calculate.py, backend/app/routes/entries.py, backend/app/routes/health.py (verb-named routes); frontend/src/hooks/useFootprint.ts (use-prefixed hook); frontend/src/components/CalculatorForm.tsx, frontend/src/components/NumberField.tsx (PascalCase components with co-located .test.tsx files)

---

## PYTHON WRITING RULES

---

RULE: `from __future__ import annotations` Everywhere
WHAT: Every Python file starts with `from __future__ import annotations` as the first import. This enables PEP 604 union syntax (`X | None`) and deferred annotation evaluation on Python 3.10+.
WHY IT SCORES: It signals awareness of modern Python, enables cleaner type annotations, and avoids forward-reference issues. Evaluators that check annotation consistency reward this pattern.
HOW TO APPLY: Add it as the first import in every `.py` file. Configure your linter to require it (ruff rule UP007 catches old-style Optional).
SIGNAL IN REPO: Every single `.py` file in backend/app/ and backend/tests/ uses this import as the first line after the docstring.

---

RULE: Strict mypy with Pydantic Plugin
WHAT: mypy is configured in strict mode (`strict = true`) with the Pydantic plugin enabled. Google SDK modules get `ignore_missing_imports = true` because they lack complete stubs.
WHY IT SCORES: Strict mypy catches entire categories of bugs at analysis time. Using the Pydantic plugin ensures model fields and validators are correctly typed. Evaluators check for type-checking strictness as a top-tier quality signal.
HOW TO APPLY: Set `strict = true` in `[tool.mypy]`. Add `plugins = ["pydantic.mypy"]`. Override `ignore_missing_imports` only for third-party modules without stubs — never for your own code.
SIGNAL IN REPO: backend/pyproject.toml (lines 38–49: strict mypy config with pydantic plugin and targeted override for google.* modules)

---

RULE: Return-Type Annotations on Every Function
WHAT: Every function and method has explicit return-type annotations. Combined with strict mypy, this makes the codebase end-to-end type-safe. Even small helpers like `_log_insight` annotate `-> None`.
WHY IT SCORES: Evaluators scan for missing return annotations as a quality gap. Complete annotations make the code self-documenting and enable IDE tooling to catch errors.
HOW TO APPLY: Never write a function without `-> ReturnType`. Use `-> None` for side-effectful functions. Use `-> dict[str, str]` not `-> dict`.
SIGNAL IN REPO: backend/app/insights/gemini.py (every function annotated: `-> str`, `-> dict`, `-> InsightsResponse`, `-> None`), backend/app/config.py (`-> Settings`, `-> list[str]`)

---

RULE: Pydantic Models as Validated Contracts
WHAT: Every Pydantic model uses `Field()` with explicit `ge`, `le`, `min_length`, `max_length`, and `pattern` constraints. Models serve as both input validation and OpenAPI documentation. Every field has a bounded, finite range — no unbounded inputs.
WHY IT SCORES: Bounded fields are a security and quality signal. Evaluators detect unbounded numeric inputs or missing constraints as vulnerabilities. Pydantic models that double as OpenAPI docs demonstrate API-first design.
HOW TO APPLY: For every numeric field, define a named upper-bound constant and use `Field(ge=0, le=MAX_VALUE)`. For strings, use `min_length`, `max_length`, and `pattern`. Document the bounds with a comment explaining why they were chosen.
SIGNAL IN REPO: backend/app/models.py (lines 18–22 define named bound constants; every field uses `ge=`, `le=`, `min_length=`, `max_length=`, `pattern=`)

---

RULE: Enums over Plain Strings for Finite Sets
WHAT: When a field has a fixed set of valid values, it is modeled as a `str, Enum` subclass, not a plain string. This provides compile-time validation, auto-generates dropdown docs in OpenAPI, and prevents typos.
WHY IT SCORES: Evaluators detect stringly-typed code as a quality anti-pattern. Enums make invalid states unrepresentable and enable exhaustive pattern matching.
HOW TO APPLY: Create `class MyType(str, Enum)` for any field with a known finite set of values. Use the enum in Pydantic models and domain logic. The `str` base class ensures JSON serialization works transparently.
SIGNAL IN REPO: backend/app/carbon/factors.py (CarFuel and DietType are both `str, Enum` subclasses), backend/app/models.py (uses `CarFuel`, `DietType` as field types), backend/app/models.py line 91 (`source: Literal["gemini", "rules", "cache"]`)

---

RULE: Named Constants with Source Citations
WHAT: Every numeric constant is a named module-level variable with a comment citing its source (publication, URL, or dataset). No magic numbers appear in logic functions. Even time conversions like `WEEKS_PER_YEAR = 52` are named.
WHY IT SCORES: Named constants make code self-documenting and auditable. AI evaluators flag unexplained numeric literals as magic numbers. Citing sources demonstrates domain rigor and makes the code verifiable.
HOW TO APPLY: Define all constants in a dedicated `constants.py` or `factors.py` file. Each constant gets a comment with its source. Reference the constant by name in all computations.
SIGNAL IN REPO: backend/app/carbon/factors.py (every constant has a comment citing DEFRA, EPA, IPCC, or Our World in Data), backend/app/insights/rules.py (reduction fractions are named: `_FLIGHT_REDUCTION_SHARE = 0.5`)

---

RULE: Docstrings on Every Public Interface
WHAT: Every module, class, and public function has a docstring following PEP 257 convention. Docstrings explain the "why" and design intent, not just the "what." Module-level docstrings describe the module's role and design principle.
WHY IT SCORES: Evaluators check docstring presence on public interfaces as a documentation quality signal. Module-level docstrings that explain architectural intent score higher than trivial per-function docstrings.
HOW TO APPLY: Follow PEP 257 convention. Module docstrings go at the very top and explain the module's purpose and design rules. Function docstrings explain non-obvious behavior, constraints, or rationale. Configure ruff with `D` rules.
SIGNAL IN REPO: backend/app/carbon/calculator.py (module docstring explains "pure, deterministic, side-effect-free"), backend/app/insights/gemini.py (module docstring explains the graceful degradation principle), backend/app/__init__.py (package docstring)

---

RULE: Functions Stay Small and Single-Purpose
WHAT: Functions do one thing. Helper functions are extracted with a leading underscore prefix (`_transport_annual_kg`, `_home_annual_kg`). The public function (`calculate_footprint`) orchestrates the helpers. McCabe complexity is capped at 10.
WHY IT SCORES: Small functions are independently testable and readable. Evaluators measure cyclomatic complexity — functions below the threshold score well. The underscore prefix signals internal use without export.
HOW TO APPLY: If a function has more than one level of nesting or more than ~25 lines, extract a helper. Set `max-complexity = 10` in your linter. Name helpers with a leading underscore.
SIGNAL IN REPO: backend/app/carbon/calculator.py (4 private helpers + 1 public function, each under 15 lines), pyproject.toml line 32 (`max-complexity = 10`)

---

## TYPESCRIPT WRITING RULES

---

RULE: Strict TypeScript with Zero `any`
WHAT: `tsconfig.json` enables `strict: true`, `noUnusedLocals: true`, `noUnusedParameters: true`, `noFallthroughCasesInSwitch: true`. The codebase has zero uses of `any` except in the type-declaration file for vitest-axe (where it is required by the library interface).
WHY IT SCORES: Strict TypeScript catches entire categories of runtime errors at compile time. Evaluators flag any use of `any` in application code as a quality defect.
HOW TO APPLY: Enable all strict flags in tsconfig.json. Use the `@typescript-eslint/recommended` ruleset to catch `any` usage. Allow `any` only in `.d.ts` files where third-party types require it, with an eslint-disable comment.
SIGNAL IN REPO: frontend/tsconfig.json (strict: true, noUnusedLocals: true, noUnusedParameters: true), frontend/src/test/vitest-axe.d.ts (eslint-disable for the `any` required by the AxeMatchers interface)

---

RULE: Interfaces for Props, Types for Unions
WHAT: Component props are always defined as an `interface Props` block directly above the component. Union types (like `CarFuel`, `DietType`) use `type` aliases. Types mirror the backend schema exactly, field-for-field.
WHY IT SCORES: Consistent typing convention makes the codebase predictable. Using interfaces for props enables declaration merging if needed and is the React community convention. Type aliases for unions are more readable for finite sets.
HOW TO APPLY: Define `interface Props` above each component. Use `type` for union literals. Mirror backend models field-for-field in a dedicated `types.ts` file.
SIGNAL IN REPO: frontend/src/components/CalculatorForm.tsx (interface Props { onSubmit, loading }), frontend/src/lib/types.ts (type CarFuel = "petrol" | ..., interface CarbonInput { ... })

---

RULE: Hook Returns State + Actions, Never I/O
WHAT: A custom hook returns a flat object of state values and action functions. All API calls live inside the hook. Components never call fetch directly — they receive data and callbacks from the hook.
WHY IT SCORES: This pattern enforces a clean separation between state management and presentation. Evaluators look for this as a sign that the developer understands React architecture and testability.
HOW TO APPLY: Create one custom hook per feature that owns all async state. The hook imports from the API client and returns `{ data, loading, error, doSomething }`. Components are pure renderers of the hook's return value.
SIGNAL IN REPO: frontend/src/hooks/useFootprint.ts (returns { result, insights, entries, loading, saving, error, status, calculate, save }), frontend/src/App.tsx (destructures the hook and passes values to presentational components)

---

RULE: Pure Utility Functions with No Side Effects
WHAT: Utility functions in `lib/` are pure: they take values and return values, with no I/O, no DOM access, no state mutation. The `format.ts` module is a perfect example — four pure functions that transform data for display.
WHY IT SCORES: Pure functions are trivially testable and compose safely. Evaluators flag side effects in utility code as a design flaw.
HOW TO APPLY: Create a `lib/` directory for pure utilities. Each function should be referentially transparent — same input always produces same output. Never import React, fetch, or localStorage in a utility file.
SIGNAL IN REPO: frontend/src/lib/format.ts (four pure functions: formatKg, formatTonnes, categoryLabel, formatDate — no imports, no side effects)

---

RULE: Co-located Test Files
WHAT: Every source file has its test file adjacent to it with the pattern `{filename}.test.{ext}`. Components have `Component.test.tsx` next to `Component.tsx`. Utilities have `util.test.ts` next to `util.ts`.
WHY IT SCORES: Co-location makes it immediately obvious whether a file has tests. Evaluators can verify coverage by checking for missing test files. It also makes refactoring safer because the test moves with the source.
HOW TO APPLY: Place test files next to their source files. Use the `.test.` infix convention. Configure vitest/jest to find tests by this pattern.
SIGNAL IN REPO: frontend/src/components/CalculatorForm.tsx and CalculatorForm.test.tsx, frontend/src/lib/api.ts and api.test.ts, frontend/src/lib/format.ts and format.test.ts

---

## TOOLING RULES

---

RULE: Format is Never a Human Decision
WHAT: Formatting is handled by automated tools (ruff format for Python, Prettier for TypeScript) with committed configuration files. Formatting is checked in CI with `--check` flags. Pre-commit hooks run formatting before code reaches the repo.
WHY IT SCORES: Evaluators detect formatting inconsistency as a quality signal. When formatting is automated and checked in CI, every file in the repo is guaranteed to be consistently formatted.
HOW TO APPLY: Commit a formatter config file (`.prettierrc.json`, `pyproject.toml [tool.ruff]`). Add `format:check` to CI. Install pre-commit hooks that run the formatter. Never discuss formatting in code review — the tool decides.
SIGNAL IN REPO: .pre-commit-config.yaml (ruff and ruff-format hooks), frontend/.prettierrc.json, .github/workflows/ci.yml (ruff format --check, npm run format:check)

---

RULE: Lint Rules Selected for Specific Reasons
WHAT: The ruff lint selection is explicit and covers 14 rule categories (E, W, F, I, N, D, UP, ANN, B, C4, SIM, PL, C90, RUF). Each ignored rule has a comment explaining why. Test files get targeted per-file-ignores for rules that don't apply to tests.
WHY IT SCORES: A broad, intentional lint rule selection demonstrates quality discipline. Comments on ignored rules prove the developer considered and dismissed them deliberately, not lazily.
HOW TO APPLY: List every lint category you enable. Comment on every rule you ignore. Use per-file-ignores for test directories (e.g., disable docstring and annotation rules in tests). Set McCabe complexity limits.
SIGNAL IN REPO: backend/pyproject.toml (lines 19–36: explicit rule selection with comments on E501 and B008 ignores, per-file-ignores for tests)

---

RULE: Pre-commit Hooks Run Safety Checks First
WHAT: Pre-commit hooks run in order: (1) file hygiene (end-of-file-fixer, trailing-whitespace, check-yaml, check-json), (2) security (check-added-large-files, detect-private-key), (3) linting (ruff check), (4) formatting (ruff format). This catches issues before they reach CI.
WHY IT SCORES: Pre-commit hooks demonstrate a "shift left" quality philosophy. The ordering ensures security checks run before style checks, catching secrets before they're committed.
HOW TO APPLY: Use the pre-commit framework. Order hooks from most-critical (security) to least-critical (formatting). Scope Python hooks to `^backend/` to avoid false positives on non-Python files.
SIGNAL IN REPO: .pre-commit-config.yaml (6 hygiene/security hooks from pre-commit-hooks, then ruff check and ruff-format scoped to backend/)

---

RULE: EditorConfig as the Cross-Editor Foundation
WHAT: A `.editorconfig` file ensures every contributor's editor uses the same settings: UTF-8, LF line endings, final newline, trimmed trailing whitespace. Language-specific indent sizes (4 for Python, 2 for TS/JSON/CSS/YAML/HTML). Markdown exempts trailing whitespace for hard line breaks.
WHY IT SCORES: EditorConfig prevents whitespace-only diffs and encoding issues. It is a universal standard supported by all major editors without plugins. Evaluators see it as a sign of professional project setup.
HOW TO APPLY: Create `.editorconfig` at the root with `root = true`. Set global defaults and language-specific overrides. Explain non-obvious choices in comments.
SIGNAL IN REPO: .editorconfig (lines 1–22: root=true, charset=utf-8, end_of_line=lf, language-specific indentation, Markdown trailing-whitespace exception)

---

RULE: Quality Gates Defined as Non-Negotiable in CONTRIBUTING.md
WHAT: CONTRIBUTING.md defines a table of quality gates (lint, format, types, tests with coverage thresholds) for both backend and frontend. Every gate runs in CI and must pass before merging. The document also defines coding conventions (fully type-annotated, docstrings, no secrets, axe assertions).
WHY IT SCORES: Evaluators value explicit quality standards. A contributing guide that defines gates proves the project has standards, not just aspirations. It also makes the project appear professionally maintained.
HOW TO APPLY: Create a CONTRIBUTING.md with a gates table showing the exact commands for each check. State conventions as non-negotiable rules, not suggestions. Reference the CI config for proof that gates are enforced.
SIGNAL IN REPO: CONTRIBUTING.md (lines 42–64: quality gates table, coding conventions, definition of done for accessibility)
