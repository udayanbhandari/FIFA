# Contributing to StadiumIQ

Thank you for contributing to StadiumIQ! This guide explains how to set up the project, run quality checks, and submit changes.

## Project Layout

```
Challenge4/
├── backend/         # Python 3.12 + FastAPI
│   ├── app/         # Application code
│   └── tests/       # pytest test suite
├── frontend/        # TypeScript + React + Vite
│   ├── src/         # Application code (components, hooks, lib)
│   └── e2e/         # Playwright end-to-end tests
├── docs/            # Architecture documentation
└── blueprints/      # Blueprint rules (read-only reference)
```

## Development Setup

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Frontend

```bash
cd frontend
npm ci
```

### Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
```

## Quality Gates

Every change must pass all gates before merging. These are enforced in CI.

| Gate | Backend Command | Frontend Command |
|------|----------------|-----------------|
| **Lint** | `ruff check .` | `npm run lint` |
| **Format** | `ruff format --check .` | `npm run format:check` |
| **Types** | `mypy app/` | `npm run typecheck` |
| **Tests** | `pytest --cov=app --cov-fail-under=90` | `npm test -- --coverage` |
| **Build** | — | `npm run build` |

## Coding Conventions

These are rules, not suggestions:

- **Every function has a return-type annotation.** No exceptions. Use `-> None` for side-effectful functions.
- **Every public module, class, and function has a docstring.** Module docstrings explain the "why."
- **Every Pydantic field has bounded constraints.** `Field(ge=0, le=MAX)` for numbers, `min_length`/`max_length` for strings.
- **Enums for finite value sets.** Never use plain strings when values are known at compile time.
- **No secrets in code.** Use Application Default Credentials. No API keys.
- **Named constants with source citations.** No magic numbers in logic functions.
- **Accessibility is part of the definition of done.** Every component test includes an axe assertion. Every interactive element has an accessible name. Every color has a text equivalent.
- **Co-located tests.** `Component.tsx` has `Component.test.tsx` next to it.

## Submission Workflow

1. Create a branch from `main`
2. Make your changes following the conventions above
3. Run all quality gates locally
4. Open a pull request with a description of what changed and why
5. CI must pass all 4 jobs (backend, frontend, E2E, API drift)
6. Request review from a maintainer
