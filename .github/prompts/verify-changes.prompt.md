---
description: Run all quality checks (lint, types, tests, build) and fix every error found. Use before finishing any task or committing code.
---

# Verify All Changes

Run every check below and fix all errors before declaring done.

## Backend Checks

```bash
cd backend

# 1. Ruff format (auto-fix formatting)
uv run ruff format .

# 2. Ruff lint (auto-fix where possible)
uv run ruff check . --fix

# 3. Type checking (must pass with zero errors)
uv run mypy app

# 4. Tests (all must pass)
uv run pytest
```

## Frontend Checks

```bash
cd frontend

# 1. Biome lint + format (auto-fix)
npm run lint

# 2. TypeScript compile + Vite build (must succeed with zero errors)
npm run build
```

## Fix Strategy

- **Ruff errors**: Most are auto-fixable with `--fix`. For remaining ones, fix manually following the rule description.
- **mypy errors**: Add missing type annotations; replace `Any` with proper types; use `cast()` only when truly necessary.
- **pytest failures**: Read the full traceback, fix the root cause — do not skip or mock away the failure.
- **Build errors**: TypeScript errors must be resolved; do not use `// @ts-ignore` unless absolutely unavoidable.

## Done Criteria

All four commands exit with code 0. Only then is the task complete.
