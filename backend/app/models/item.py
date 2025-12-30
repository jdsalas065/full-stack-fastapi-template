"""Item database model."""

from uuid import uuid4

from sqlmodel import Field, SQLModel


class Item(SQLModel, table=True):
    """
    Item model for database storage.
    
    Represents items owned by users.
    """
    
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    title: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    owner_id: str = Field(foreign_key="user.id")
