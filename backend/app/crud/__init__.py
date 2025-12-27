"""
CRUD operations for database models.

Organize CRUD operations by domain/resource in separate files as the project grows.
Example:
    from app.crud.user import user_crud
    from app.crud.item import item_crud

For now, this is a placeholder for future CRUD operations.
When you add database integration:
1. Create CRUD class files in this directory (e.g., user.py, item.py)
2. Each file should contain CRUD operations for that specific model
3. Import and expose CRUD instances through __init__.py

Example structure:
    crud/
    ├── __init__.py (this file)
    ├── base.py     (common CRUD base class)
    ├── user.py     (user CRUD operations)
    └── item.py     (item CRUD operations)
"""

# Example of how to organize CRUD when you add them:
# from app.crud.user import user_crud
# from app.crud.item import item_crud
#
# __all__ = ["user_crud", "item_crud"]

__all__ = []
