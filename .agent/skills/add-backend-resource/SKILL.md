---
name: add-backend-resource
description: Add a full CRUD backend resource to this FastAPI + SQLModel project (model, schema, crud, service, route, router registration, Alembic migration, tests). Use when adding a new entity, table, or API endpoint group on the backend.
---

<!--
HƯỚNG DẪN DÙNG (How to use)
- Antigravity tự nhận skill này trong project (.agent/skills/). Để kích hoạt, nhắn agent kèm tên tài nguyên, ví dụ:
    "Dùng skill add-backend-resource để thêm resource: product"
  hoặc chỉ cần mô tả: "Thêm CRUD API cho product" — agent sẽ tự khớp theo description.
- Thay <resource> trong các bước bằng tên thật (số ít, snake_case), ví dụ product, order_item.
- Yêu cầu trước: backend chạy được bằng uv (đã cài deps), DB sẵn sàng cho alembic.
- Sao chép skill sang tool khác: copy cả thư mục này vào .github/skills/ (Copilot) hoặc .claude/skills/ (Claude). Trong Copilot có thể gọi tương đương qua prompt file /add-backend-resource.
-->

# Add Backend Resource

Add a new CRUD resource following the project's layered architecture:
`api/routes → services → crud → models / schemas`.

Work in `backend/`. Do each step in order and verify before moving on. Match existing patterns exactly; do not invent new ones. Do not add dependencies not already in `pyproject.toml`.

## Steps

1. **Model** — `backend/app/models/<resource>.py`. SQLModel table, UUID primary key, `created_at`/`updated_at`. Pattern: `backend/app/models/item.py`.
2. **Schema** — `backend/app/schemas/<resource>.py`. Define `<Resource>Create`, `<Resource>Update`, `<Resource>Public`. Pattern: `backend/app/schemas/item.py`.
3. **Register** model/schema in `backend/app/models/__init__.py` and `backend/app/schemas/__init__.py`.
4. **CRUD** — `backend/app/crud/<resource>.py`. Functions `get_*`, `get_*s`, `create_*`, `update_*`, `delete_*`. Keyword-only args (`*`), typed, no business logic. Pattern: `backend/app/crud/item.py`.
5. **Service** (if business logic) — `backend/app/services/<resource>_service.py`. Use `get_logger(__name__)`, raise from `app.exceptions`, keyword-only args.
6. **Route** — `backend/app/api/routes/<resource>.py`. Use `SessionDep`, `CurrentUser` from `app.api.dependencies`. Every handler has a docstring + `response_model`. Pattern: `backend/app/api/routes/items.py`.
7. **Register router** in `backend/app/api/main.py`:
   ```python
   from app.api.routes import <resource>
   api_router.include_router(<resource>.router)
   ```
8. **Migration**:
   ```bash
   uv run alembic revision --autogenerate -m "add <resource> table"
   # review the generated file, then:
   uv run alembic upgrade head
   ```
9. **Tests** — `backend/tests/api/routes/test_<resource>.py`. Cover create, read, update, delete, auth checks.

## Conventions (must follow)

- Custom exceptions from `app.exceptions` (e.g. `NotFoundException`), not bare `HTTPException` in services.
- `get_logger(__name__)` instead of `print` (ruff blocks `T201`).
- Full type hints (mypy strict): `list[str]`, `str | None`.
- Keyword-only args: `def get_item(*, session: Session, item_id: str) -> Item | None: ...`

## Done when

```bash
cd backend && uv run ruff check . && uv run mypy app && uv run pytest
```
All commands exit 0.
