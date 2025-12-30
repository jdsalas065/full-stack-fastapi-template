"""Item schemas for API request/response validation."""

from sqlmodel import Field, SQLModel


# Shared properties
class ItemBase(SQLModel):
    """Base item properties shared across schemas."""

    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    """Schema for creating a new item."""

    pass


# Properties to receive on item update
class ItemUpdate(SQLModel):
    """Schema for updating an existing item."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)


# Properties to return via API
class ItemPublic(ItemBase):
    """Public item information returned by API."""

    id: str
    owner_id: str


class ItemsPublic(SQLModel):
    """Schema for paginated list of items."""

    data: list[ItemPublic]
    count: int
