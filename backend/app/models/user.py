"""User database model."""

from uuid import uuid4

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """
    User model for database storage.
    
    Represents application users with authentication and authorization data.
    """
    
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    hashed_password: str
    full_name: str | None = Field(default=None, max_length=255)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
