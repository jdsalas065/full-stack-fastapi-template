"""
Dependency injection for FastAPI routes.

Common dependencies used across endpoints.
Organize by domain as the project grows.
"""

from typing import Annotated

from fastapi import Header, HTTPException, status


async def verify_api_key(x_api_key: Annotated[str | None, Header()] = None) -> str:
    """
    Verify API key from request header (example dependency).

    Args:
        x_api_key: API key from X-API-Key header

    Returns:
        The verified API key

    Raises:
        HTTPException: If API key is missing or invalid

    Example:
        @router.get("/protected")
        async def protected_route(
            api_key: Annotated[str, Depends(verify_api_key)]
        ):
            return {"message": "Access granted"}
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
        )

    # Add your API key verification logic here
    # For now, this is just a placeholder

    return x_api_key


# Add more common dependencies here as needed:
# - Database session dependency
# - Current user dependency
# - Pagination dependency
# - Rate limiting dependency
