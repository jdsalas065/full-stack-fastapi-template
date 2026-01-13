"""
Custom exception handlers for the application.

Define custom exceptions and their handlers here.
"""

from typing import Any

from fastapi import Request, status
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Base exception for application-specific errors."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        """
        Initialize application exception.

        Args:
            message: Human-readable error message
            status_code: HTTP status code
            error_code: Machine-readable error code
            details: Additional error details
        """
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


class NotFoundException(AppException):
    """Exception raised when a resource is not found."""

    def __init__(self, message: str = "Resource not found", resource: str | None = None):
        details = {"resource": resource} if resource else {}
        super().__init__(
            message,
            status_code=status.HTTP_404_NOT_FOUND,
            details=details,
        )


class ValidationException(AppException):
    """Exception raised when validation fails."""

    def __init__(
        self,
        message: str = "Validation error",
        field: str | None = None,
        errors: list[dict[str, Any]] | None = None,
    ):
        details: dict[str, Any] = {}
        if field:
            details["field"] = field
        if errors:
            details["errors"] = errors
        super().__init__(
            message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class ServiceUnavailableException(AppException):
    """Exception raised when external service is unavailable."""

    def __init__(self, message: str = "Service unavailable", service: str | None = None):
        details = {"service": service} if service else {}
        super().__init__(
            message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details,
        )


class RateLimitException(AppException):
    """Exception raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: int | None = None,
    ):
        details = {"retry_after": retry_after} if retry_after else {}
        super().__init__(
            message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=details,
        )


async def app_exception_handler(_request: Request, exc: AppException) -> JSONResponse:
    """
    Handle application-specific exceptions.

    Args:
        _request: The incoming request (unused)
        exc: The exception that was raised

    Returns:
        JSON response with structured error details
    """
    response_content: dict[str, Any] = {
        "error": {
            "message": exc.message,
            "code": exc.error_code,
            "status_code": exc.status_code,
        }
    }

    if exc.details:
        response_content["error"]["details"] = exc.details

    # Add retry_after header for rate limit errors
    headers = {}
    if isinstance(exc, RateLimitException) and exc.details.get("retry_after"):
        headers["Retry-After"] = str(exc.details["retry_after"])

    return JSONResponse(
        status_code=exc.status_code,
        content=response_content,
        headers=headers,
    )


async def generic_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected exceptions.

    Args:
        _request: The incoming request
        exc: The exception that was raised

    Returns:
        JSON response with generic error message
    """
    from app.core.logging import get_logger

    logger = get_logger(__name__)
    logger.error(
        f"Unhandled exception: {exc}",
        exc_info=exc,
        extra={
            "path": _request.url.path,
            "method": _request.method,
        },
    )

    # In production, return generic message to avoid leaking internal details
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "message": "Internal server error",
                "code": "INTERNAL_SERVER_ERROR",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            }
        },
    )
