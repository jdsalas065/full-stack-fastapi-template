"""User schemas for API request/response validation."""

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


# Shared properties
class UserBase(SQLModel):
    """Base user properties shared across schemas."""
    
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    """Schema for creating a new user."""
    
    password: str = Field(min_length=8, max_length=40)


# Properties to receive via API on update
class UserUpdate(SQLModel):
    """Schema for updating an existing user."""
    
    email: EmailStr | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None
    is_superuser: bool | None = None


class UserUpdateMe(SQLModel):
    """Schema for users updating their own profile."""
    
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    """Schema for password update."""
    
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Properties to return via API
class UserPublic(UserBase):
    """Public user information returned by API."""
    
    id: str


class UsersPublic(SQLModel):
    """Schema for paginated list of users."""
    
    data: list[UserPublic]
    count: int


# Properties for user registration
class UserRegister(SQLModel):
    """Schema for user self-registration."""
    
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Additional properties stored in DB
class UserRead(UserBase):
    """Full user data read from database."""
    
    id: str


# Generic message
class Message(SQLModel):
    """Generic message response."""
    
    message: str


# Token schemas
class Token(SQLModel):
    """JWT token response."""
    
    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    """JWT token payload."""
    
    sub: str | None = None


# Password reset schemas
class NewPassword(SQLModel):
    """Schema for password reset."""
    
    token: str
    new_password: str = Field(min_length=8, max_length=40)


# Private user creation (by superuser)
class PrivateUserCreate(SQLModel):
    """Schema for creating users with verified status (superuser only)."""
    
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str = Field(max_length=255)
    is_verified: bool = True
