# REPO_STRUCTURE Blueprint

Rules extracted from root files, CI configuration, documentation, and project organization.
Every rule is domain-agnostic and applies to any project on any topic.

---

RULE: Root File Completeness Checklist
WHAT: The root of the repository must contain: README.md, LICENSE, CONTRIBUTING.md, CHANGELOG.md, Dockerfile, .gitignore, .dockerignore, .editorconfig, .env.example, .pre-commit-config.yaml. Each file serves a specific scoring purpose — none is optional.
WHY IT SCORES: AI evaluators scan the root directory and count the presence of standard project files. Each file signals a different quality dimension: README (documentation), LICENSE (legal clarity), CONTRIBUTING (process maturity), CHANGELOG (change discipline), Dockerfile (deployment readiness), .editorconfig (consistency), .env.example (security awareness). Missing any of these reduces the overall quality score.
HOW TO APPLY: Create every file in this list before writing application code. Use community-standard formats (Keep a Changelog, MIT license, PEP 257 docstrings). Keep each file focused on its purpose — do not combine concerns.
SIGNAL IN REPO: Root directory contains all 10 files listed above.

---

RULE: README Sections in Scoring Order
WHAT: The README follows a strict section order that maps to evaluation criteria: (1) Title + badges (CI status, license), (2) One-paragraph elevator pitch, (3) Live demo link, (4) Chosen vertical / problem statement, (5) Approach and decision-making logic, (6) Architecture + project layout, (7) Key endpoints, (8) Running locally, (9) Testing (with coverage numbers), (10) Deployment instructions, (11) Assumptions, (12) Rubric mapping table, (13) License.
WHY IT SCORES: A README that explicitly maps to evaluation criteria tells the evaluator exactly where to look for each quality signal. The "rubric mapping" table is a meta-signal — it proves the developer understands what is being evaluated and can demonstrate alignment. Badges at the top provide instant quality signals (passing CI, license type).
HOW TO APPLY: Start with the badge row (CI, license). Write a one-paragraph pitch. Add a live demo link. Include a "How this maps to the rubric" table near the end. Use code blocks for architecture diagrams, tables for endpoints, and command blocks for setup instructions. Number sections for easy reference.
SIGNAL IN REPO: README.md (sections 1–8 follow this exact order; lines 218–228: rubric mapping table; lines 2–4: CI and license badges)

---

RULE: ARCHITECTURE.md Explains the Why, Not Just the What
WHAT: ARCHITECTURE.md documents: (1) a system overview diagram, (2) a layer responsibility table, (3) design rules the codebase follows (stated as constraints, not descriptions), (4) frontend structure table, (5) quality gates reference. It explains WHY each layer exists and what rule it follows, not just what files are in it.
WHY IT SCORES: An architecture document that explains constraints and rules is far more valuable to evaluators than a file listing. It proves the developer designed the system intentionally. Evaluators use it to verify that the code matches the documented architecture.
HOW TO APPLY: Create `docs/ARCHITECTURE.md`. Start with a system overview diagram (ASCII art). Add a table mapping each layer to its modules and its rule/constraint. List the design rules as bullet points with bold headings. Reference other docs (README, CONTRIBUTING) rather than duplicating content.
SIGNAL IN REPO: docs/ARCHITECTURE.md (system overview diagram, 5-row layer table with Rule column, 4 design rules as bold-headed bullet points, frontend structure table)

---

RULE: CHANGELOG Follows Keep a Changelog Format
WHAT: CHANGELOG.md follows the Keep a Changelog format with Semantic Versioning. Each version section lists changes under Added, Changed, Fixed, Removed headers. Entries are written in past tense and describe the change in enough detail to understand its impact.
WHY IT SCORES: A maintained changelog demonstrates disciplined release management. Evaluators check for its presence and format. Keep a Changelog is the community standard and shows the developer follows conventions.
HOW TO APPLY: Create CHANGELOG.md with a header linking to keepachangelog.com and semver.org. Add a section for each version with the date. Group changes under Added/Changed/Fixed/Removed. Write entries in past tense with enough detail to understand the impact.
SIGNAL IN REPO: CHANGELOG.md (lines 1–5: format references, 4 versioned sections with Added/Changed headers, detailed entries describing each improvement)

---

RULE: CONTRIBUTING.md Defines Gates as Requirements
WHAT: CONTRIBUTING.md defines: (1) project layout, (2) development setup instructions, (3) pre-commit hook setup, (4) a quality gates TABLE showing the exact commands for lint, format, types, and tests with their thresholds, (5) coding conventions stated as rules, (6) submission workflow. Gates are stated as requirements ("must pass"), not suggestions.
WHY IT SCORES: A contributing guide that defines hard gates proves the project has enforced standards. Evaluators check whether the guide's commands match the CI pipeline. The table format makes gates scannable and verifiable.
HOW TO APPLY: Create a table with columns: Gate, Backend, Frontend. Fill in the exact commands for each check. State coverage thresholds with numeric values. List conventions as rules, not recommendations. Include "every component test includes an axe assertion" as a definition of done.
SIGNAL IN REPO: CONTRIBUTING.md (lines 47–53: quality gates table; lines 57–66: conventions stated as rules; lines 60–62: "Accessibility is part of the definition of done")

---

RULE: Monorepo Split Enforces Separation
WHAT: Backend and frontend live in separate top-level directories (backend/, frontend/) with independent dependency files (requirements.txt vs package.json), independent CI jobs, and independent tooling configs. They share nothing at the module level — type alignment is enforced by a separate tooling step.
WHY IT SCORES: A clean monorepo split demonstrates that the developer understands service boundaries. Evaluators check whether the backend and frontend can be built and tested independently. Shared imports between them would be a coupling anti-pattern.
HOW TO APPLY: Create top-level `backend/` and `frontend/` directories. Give each its own dependency manifest, lint config, and test config. Create separate CI jobs for each. If types need to stay aligned, use a tooling step (type sync script) rather than shared imports.
SIGNAL IN REPO: backend/ (pyproject.toml, requirements.txt, ruff in pyproject.toml), frontend/ (package.json, tsconfig.json, eslint.config.js, .prettierrc.json), .github/workflows/ci.yml (separate backend and frontend jobs)

---

RULE: .gitignore Covers Five Categories
WHAT: .gitignore is organized into five labeled categories: (1) Language artifacts (Python: __pycache__, .pyc; Node: node_modules, dist), (2) Tool caches (.pytest_cache, .ruff_cache, coverage/), (3) Environment/secrets (.env, .env.*, *-key.json, service-account*.json), (4) Editor/OS files (.DS_Store, .idea/, .vscode/, Thumbs.db), (5) Build artifacts (*.egg-info, build/). The `.env.example` is explicitly NOT ignored.
WHY IT SCORES: A comprehensive, categorized .gitignore prevents accidental commits of secrets, build artifacts, and OS files. Evaluators scan for committed secrets and build artifacts as quality failures. The explicit `!.env.example` exception shows intentional design.
HOW TO APPLY: Organize your .gitignore into labeled sections. Cover all five categories. Use negation patterns (!) to explicitly include files that would otherwise be caught by a broad pattern (e.g., `!.env.example`).
SIGNAL IN REPO: .gitignore (lines 1–37: five labeled sections; line 23: `!.env.example` exception)

---

RULE: CI Pipeline Has Four Job Types
WHAT: The CI pipeline contains four distinct jobs: (1) Backend quality (lint + format + types + tests with coverage), (2) Frontend quality (typecheck + lint + format + tests with coverage + build), (3) E2E testing (full stack, conditional on push to main, depends on jobs 1+2), (4) API contract drift detection (depends on job 1). This structure ensures fast feedback, gated progression, and cross-stack validation.
WHY IT SCORES: A four-job CI pipeline demonstrates professional DevOps. Each job type serves a distinct purpose. Evaluators check for CI comprehensiveness — having lint, format, types, tests, build, E2E, and drift detection covers every quality dimension.
HOW TO APPLY: Create separate CI jobs for backend and frontend. Add an E2E job that depends on both (runs only on push, not PRs). Add a drift-detection job that verifies cross-stack type alignment. Pin all actions to commit SHAs.
SIGNAL IN REPO: .github/workflows/ci.yml (4 jobs: backend, frontend, e2e, api-drift)

---

RULE: Dependabot Covers All Ecosystems
WHAT: Dependabot is configured for three package ecosystems: pip (backend), npm (frontend), and github-actions (CI). Each has weekly checks, a conventional-commit prefix (deps(backend):, deps(frontend):, ci:), and descriptive labels. This ensures no ecosystem's dependencies go stale.
WHY IT SCORES: Evaluators check for dependency management. Covering all three ecosystems (language packages AND CI actions) shows comprehensive supply-chain awareness. Conventional-commit prefixes demonstrate process discipline.
HOW TO APPLY: Create `.github/dependabot.yml` with an entry for each package ecosystem in your project. Include GitHub Actions as an ecosystem. Set weekly intervals. Use conventional-commit prefixes and labels for automated categorization.
SIGNAL IN REPO: .github/dependabot.yml (three ecosystem entries: pip, npm, github-actions; conventional-commit prefixes; descriptive labels)

---

RULE: Type Sync Between Backend and Frontend
WHAT: A script (`sync-types.sh`) fetches the OpenAPI spec from the running backend and generates TypeScript types. A CI job (api-drift) runs this script and fails if the generated types differ from the committed types. This ensures frontend types always match backend schemas.
WHY IT SCORES: Type drift between backend and frontend is a common source of bugs. Automated drift detection demonstrates professional cross-stack quality management. Evaluators value this as a sign of complete type safety.
HOW TO APPLY: Create a script that: (1) starts the backend, (2) fetches the OpenAPI spec, (3) generates TypeScript types from it, (4) diffs against the committed types. Run this as a CI job. Fail the build on drift.
SIGNAL IN REPO: frontend/scripts/sync-types.sh (fetches OpenAPI, generates types), .github/workflows/ci.yml (lines 92–131: api-drift job)

---

RULE: Problem Statement Alignment is Visible in Structure
WHAT: The README explicitly states the problem being solved, maps the solution to the problem pillars, and includes a "How this maps to the rubric" table. The ARCHITECTURE.md explains why each layer exists in terms of the user need. File names, section headings, and API endpoint names all reflect the problem vocabulary, not generic tech terms.
WHY IT SCORES: Evaluators check whether the submission solves the stated problem or is a generic template. A project where the README, architecture, and code structure all reflect the problem domain demonstrates genuine alignment. The rubric mapping table is the strongest alignment signal — it proves the developer mapped every requirement to a specific implementation.
HOW TO APPLY: Use the challenge description's vocabulary in your code (not just generic names). Map every requirement to a specific file or feature. Include a rubric/criteria mapping table in your README. Make sure the ARCHITECTURE.md explains each layer in terms of user needs, not just technical concerns.
SIGNAL IN REPO: README.md (lines 218–228: rubric mapping table; lines 24–36: solution mapped to problem pillars), docs/ARCHITECTURE.md (layers explained in terms of user flow)

---

RULE: Professional Completeness Signals
WHAT: The project includes signals of completeness beyond code: a live demo URL, CI badges in the README, a version number in `__init__.py` matching pyproject.toml and CHANGELOG, deployment instructions with exact commands, documented assumptions, and a license file. These collectively signal "this is finished, not a prototype."
WHY IT SCORES: AI evaluators assess overall project maturity. A project with a live demo, CI badges, consistent versioning, and deployment docs appears production-grade. Missing any of these creates a "prototype" impression that lowers scores.
HOW TO APPLY: Deploy your project and include the live URL in the README. Add CI status badges. Keep the version number consistent across __init__.py, pyproject.toml, package.json, and CHANGELOG. Include deployment instructions with exact commands. Document your assumptions explicitly.
SIGNAL IN REPO: README.md (lines 15–17: live demo URL; lines 2–4: CI + license badges), backend/app/__init__.py (version "1.3.0"), backend/pyproject.toml (version = "1.3.0"), CHANGELOG.md (## [1.3.0])
