"""
Rate limiting middleware.

Provides rate limiting functionality to prevent abuse.
"""

import time
from collections import defaultdict
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import get_logger
from app.exceptions import RateLimitException

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware.

    Limits requests per IP address or user.
    Uses sliding window algorithm.
    """

    def __init__(
        self,
        app: any,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        enabled: bool = True,
    ):
        """
        Initialize rate limiting middleware.

        Args:
            app: FastAPI application
            requests_per_minute: Maximum requests per minute per IP
            requests_per_hour: Maximum requests per hour per IP
            enabled: Whether rate limiting is enabled
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.enabled = enabled

        # Store request timestamps per IP
        # Format: {ip: [timestamp1, timestamp2, ...]}
        self.request_history: dict[str, list[float]] = defaultdict(list)

        # Cleanup old entries periodically
        self._last_cleanup = time.time()
        self._cleanup_interval = 3600  # 1 hour

    def _get_client_ip(self, request: Request) -> str:
        """
        Get client IP address from request.

        Args:
            request: FastAPI request

        Returns:
            Client IP address
        """
        # Check for forwarded IP (behind proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take first IP if multiple
            return forwarded_for.split(",")[0].strip()

        # Check for real IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()

        # Fallback to direct client
        if request.client:
            return request.client.host

        return "unknown"

    def _cleanup_old_entries(self) -> None:
        """Remove old entries from request history."""
        current_time = time.time()
        cutoff_time = current_time - 3600  # 1 hour ago

        for ip in list(self.request_history.keys()):
            # Keep only recent requests
            self.request_history[ip] = [
                ts for ts in self.request_history[ip] if ts > cutoff_time
            ]

            # Remove IP if no recent requests
            if not self.request_history[ip]:
                del self.request_history[ip]

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """
        Process request with rate limiting.

        Args:
            request: The incoming request
            call_next: The next middleware or route handler

        Returns:
            The response from the next handler

        Raises:
            RateLimitException: If rate limit is exceeded
        """
        if not self.enabled:
            return await call_next(request)

        # Cleanup old entries periodically
        current_time = time.time()
        if current_time - self._last_cleanup > self._cleanup_interval:
            self._cleanup_old_entries()
            self._last_cleanup = current_time

        # Get client IP
        client_ip = self._get_client_ip(request)

        # Skip rate limiting for health checks
        if request.url.path.endswith("/health-check"):
            return await call_next(request)

        # Get request history for this IP
        history = self.request_history[client_ip]
        current_time = time.time()

        # Remove requests older than 1 hour
        history = [ts for ts in history if current_time - ts < 3600]
        self.request_history[client_ip] = history

        # Check per-minute limit
        recent_minute = [ts for ts in history if current_time - ts < 60]
        if len(recent_minute) >= self.requests_per_minute:
            retry_after = 60 - int(current_time - recent_minute[0])
            logger.warning(
                f"Rate limit exceeded for IP {client_ip}: "
                f"{len(recent_minute)} requests in last minute"
            )
            raise RateLimitException(
                f"Rate limit exceeded: {self.requests_per_minute} requests per minute",
                retry_after=retry_after,
            )

        # Check per-hour limit
        recent_hour = [ts for ts in history if current_time - ts < 3600]
        if len(recent_hour) >= self.requests_per_hour:
            retry_after = 3600 - int(current_time - recent_hour[0])
            logger.warning(
                f"Rate limit exceeded for IP {client_ip}: "
                f"{len(recent_hour)} requests in last hour"
            )
            raise RateLimitException(
                f"Rate limit exceeded: {self.requests_per_hour} requests per hour",
                retry_after=retry_after,
            )

        # Add current request
        history.append(current_time)
        self.request_history[client_ip] = history

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        remaining_minute = self.requests_per_minute - len(recent_minute)
        remaining_hour = self.requests_per_hour - len(recent_hour)

        response.headers["X-RateLimit-Limit-Minute"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining-Minute"] = str(max(0, remaining_minute))
        response.headers["X-RateLimit-Limit-Hour"] = str(self.requests_per_hour)
        response.headers["X-RateLimit-Remaining-Hour"] = str(max(0, remaining_hour))

        return response
