---
description: Add a full CRUD backend resource (model → schema → crud → service → route → migration). Use when adding a new entity or API endpoint.
---

# Add Backend Resource: ${input:resourceName}

Follow these steps **in order**. Complete and verify each step before moving to the next.

## Checklist

- [ ] **1. Model** — Create `backend/app/models/${input:resourceName}.py`
  - SQLModel table class, UUID primary key, timestamps (`created_at`, `updated_at`).
  - Reference pattern: `backend/app/models/item.py`.

- [ ] **2. Schema** — Create `backend/app/schemas/${input:resourceName}.py`
  - Define `${input:resourceName}Create`, `${input:resourceName}Update`, `${input:resourceName}Public`.
  - Reference pattern: `backend/app/schemas/item.py`.

- [ ] **3. Register model/schema** — Add to `backend/app/models/__init__.py` and `backend/app/schemas/__init__.py`.

- [ ] **4. CRUD** — Create `backend/app/crud/${input:resourceName}.py`
  - Functions: `get_${input:resourceName}`, `get_${input:resourceName}s`, `create_${input:resourceName}`, `update_${input:resourceName}`, `delete_${input:resourceName}`.
  - Use keyword-only args (`*`), return typed values, no business logic here.
  - Reference pattern: `backend/app/crud/item.py`.

- [ ] **5. Service** (if business logic needed) — Create `backend/app/services/${input:resourceName}_service.py`
  - Use `get_logger(__name__)`, raise from `app.exceptions`, keyword-only args.

- [ ] **6. Route** — Create `backend/app/api/routes/${input:resourceName}.py`
  - Use `SessionDep`, `CurrentUser` from `app.api.dependencies`.
  - Every handler: docstring + `response_model`.
  - Reference pattern: `backend/app/api/routes/items.py`.

- [ ] **7. Register router** — Add router to `backend/app/api/main.py`:
  ```python
  from app.api.routes import ${input:resourceName}
  api_router.include_router(${input:resourceName}.router)
  ```

- [ ] **8. Migration** — From `backend/` run:
  ```bash
  uv run alembic revision --autogenerate -m "add ${input:resourceName} table"
  ```
  Review the generated file, then:
  ```bash
  uv run alembic upgrade head
  ```

- [ ] **9. Tests** — Create `backend/tests/api/routes/test_${input:resourceName}.py`
  - Cover: create, read, update, delete, auth checks.
  - Reference pattern: `backend/tests/api/routes/test_items.py` if it exists.

- [ ] **10. Verify** — Run full check:
  ```bash
  cd backend && uv run ruff check . && uv run mypy app && uv run pytest
  ```
  Fix all errors before declaring done.
