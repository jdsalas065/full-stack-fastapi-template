---
applyTo: "backend/**/*.py"
---

# Backend Conventions

## Layer Architecture

```
api/routes  →  services  →  crud  →  models / schemas
```

- **Routes**: thin handlers — validate input, call service, return response. No DB queries.
- **Services**: all business logic. Inject `Session` as a parameter (keyword-only with `*`).
- **CRUD**: raw DB queries only using `sqlmodel` `select()`.
- **Models**: `SQLModel` table models.
- **Schemas**: Pydantic shapes for request/response. Keep separate from models.

## Route Handler Pattern

```python
# ✅ GOOD
from app.api.dependencies import CurrentUser, SessionDep
from app.schemas.item import ItemCreate, ItemPublic

@router.post("/", response_model=ItemPublic)
def create_item(
    *, session: SessionDep, current_user: CurrentUser, item_in: ItemCreate
) -> Any:
    """Create a new item."""
    return item_crud.create_item(session=session, item_in=item_in, owner_id=current_user.id)

# ❌ BAD — DB logic in route, no response_model, missing docstring
@router.post("/")
def create_item(item_in: ItemCreate, session: Session = Depends(get_db)):
    item = Item(**item_in.dict())
    session.add(item)
    session.commit()
    return item
```

## Exceptions

```python
# ✅ GOOD — use custom exceptions from app.exceptions
from app.exceptions import NotFoundException, RateLimitException

if not item:
    raise NotFoundException("Item not found", resource=str(item_id))

# ❌ BAD — bare HTTPException in service layer
raise HTTPException(status_code=404, detail="Item not found")
```

## Logging

```python
# ✅ GOOD
from app.core.logging import get_logger
logger = get_logger(__name__)
logger.info("Processing item %s", item_id)

# ❌ BAD — blocked by ruff T201
print("Processing item", item_id)
```

## Type Hints

- All function arguments and return types must be annotated (mypy strict).
- Use `list[str]` not `List[str]`; `str | None` not `Optional[str]`.
- Keyword-only arguments: use `*` separator for service/crud functions.

## Keyword-Only Args

```python
# ✅ GOOD
def get_item(*, session: Session, item_id: str) -> Item | None: ...

# ❌ BAD
def get_item(session: Session, item_id: str) -> Item | None: ...
```
