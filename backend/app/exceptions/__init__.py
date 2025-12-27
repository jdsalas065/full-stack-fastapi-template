"""
Custom exception handlers for the application.

Define custom exceptions and their handlers here.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Base exception for application-specific errors."""

    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundException(AppException):
    """Exception raised when a resource is not found."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)


class ValidationException(AppException):
    """Exception raised when validation fails."""

    def __init__(self, message: str = "Validation error"):
        super().__init__(message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


async def app_exception_handler(_request: Request, exc: AppException) -> JSONResponse:
    """
    Handle application-specific exceptions.

    Args:
        _request: The incoming request (unused)
        exc: The exception that was raised

    Returns:
        JSON response with error details
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


async def generic_exception_handler(_request: Request, _exc: Exception) -> JSONResponse:
    """
    Handle unexpected exceptions.

    Args:
        _request: The incoming request (unused)
        _exc: The exception that was raised (unused)

    Returns:
        JSON response with generic error message
    """
    # In production, you might want to log this and return a generic message
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )
