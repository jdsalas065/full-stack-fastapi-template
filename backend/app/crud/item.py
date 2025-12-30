"""CRUD operations for Item model."""

from sqlmodel import Session, select

from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate


def create_item(*, session: Session, item_in: ItemCreate, owner_id: str) -> Item:
    """
    Create a new item.
    
    Args:
        session: Database session
        item_in: Item creation data
        owner_id: ID of the item owner
        
    Returns:
        Created item instance
    """
    db_obj = Item(
        title=item_in.title,
        description=item_in.description,
        owner_id=owner_id,
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_item(*, session: Session, db_item: Item, item_in: ItemUpdate) -> Item:
    """
    Update an item.
    
    Args:
        session: Database session
        db_item: Existing item from database
        item_in: Item update data
        
    Returns:
        Updated item instance
    """
    item_data = item_in.model_dump(exclude_unset=True)
    db_item.sqlmodel_update(item_data)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def get_item(*, session: Session, item_id: str) -> Item | None:
    """
    Get an item by ID.
    
    Args:
        session: Database session
        item_id: Item ID
        
    Returns:
        Item instance if found, None otherwise
    """
    return session.get(Item, item_id)


def get_items(
    *, session: Session, owner_id: str, skip: int = 0, limit: int = 100
) -> tuple[list[Item], int]:
    """
    Get list of items for a specific owner with pagination.
    
    Args:
        session: Database session
        owner_id: Owner user ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        Tuple of (list of items, total count)
    """
    count_statement = select(Item).where(Item.owner_id == owner_id)
    count = len(session.exec(count_statement).all())
    
    statement = select(Item).where(Item.owner_id == owner_id).offset(skip).limit(limit)
    items = session.exec(statement).all()
    
    return list(items), count


def delete_item(*, session: Session, item_id: str) -> None:
    """
    Delete an item.
    
    Args:
        session: Database session
        item_id: Item ID to delete
    """
    item = session.get(Item, item_id)
    if item:
        session.delete(item)
        session.commit()
