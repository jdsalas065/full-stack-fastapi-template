"""
Database models using SQLModel.

Organize models by domain/resource in separate files as the project grows.
Example:
    from app.models.user import User
    from app.models.item import Item

For now, this is a placeholder for future database models.
When you add database integration:
1. Install sqlmodel: uv add sqlmodel
2. Create model files in this directory
3. Import and expose models through __init__.py
"""

from app.models.file import File
from app.models.item import Item
from app.models.user import User

__all__ = ["User", "Item", "File"]
