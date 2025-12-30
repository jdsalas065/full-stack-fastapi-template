"""Item management routes."""

from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import CurrentUser, SessionDep
from app.crud import item as item_crud
from app.schemas.item import ItemCreate, ItemPublic, ItemsPublic, ItemUpdate
from app.schemas.user import Message

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=ItemsPublic)
def read_items(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve items.
    """
    if current_user.is_superuser:
        # Superusers can see all items
        from sqlmodel import select
        
        from app.models.item import Item
        
        count_statement = select(Item)
        count = len(session.exec(count_statement).all())
        
        statement = select(Item).offset(skip).limit(limit)
        items = session.exec(statement).all()
        
        return ItemsPublic(data=list(items), count=count)
    else:
        # Regular users can only see their own items
        items, count = item_crud.get_items(
            session=session, owner_id=current_user.id, skip=skip, limit=limit
        )
        return ItemsPublic(data=items, count=count)


@router.post("/", response_model=ItemPublic)
def create_item(
    *, session: SessionDep, current_user: CurrentUser, item_in: ItemCreate
) -> Any:
    """
    Create new item.
    """
    item = item_crud.create_item(
        session=session, item_in=item_in, owner_id=current_user.id
    )
    return item


@router.get("/{id}", response_model=ItemPublic)
def read_item(session: SessionDep, current_user: CurrentUser, id: str) -> Any:
    """
    Get item by ID.
    """
    item = item_crud.get_item(session=session, item_id=id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )
    if not current_user.is_superuser and item.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return item


@router.put("/{id}", response_model=ItemPublic)
def update_item(
    *, session: SessionDep, current_user: CurrentUser, id: str, item_in: ItemUpdate
) -> Any:
    """
    Update an item.
    """
    item = item_crud.get_item(session=session, item_id=id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )
    if not current_user.is_superuser and item.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    item = item_crud.update_item(session=session, db_item=item, item_in=item_in)
    return item


@router.delete("/{id}")
def delete_item(session: SessionDep, current_user: CurrentUser, id: str) -> Message:
    """
    Delete an item.
    """
    item = item_crud.get_item(session=session, item_id=id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )
    if not current_user.is_superuser and item.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    item_crud.delete_item(session=session, item_id=id)
    return Message(message="Item deleted successfully")
