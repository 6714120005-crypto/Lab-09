"""
Rate Limiting Middleware and Utilities.
Provides protection against brute-force and DDoS attacks.
"""
import time
from typing import Callable, Optional
from collections import defaultdict
from datetime import datetime
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from fastapi import status

from config import settings


class InMemoryRateLimitStorage:
    """
    Simple in-memory rate limit storage.
    For production, use Redis or similar distributed storage.
    """

    def __init__(self):
        self.requests = defaultdict(list)
        self.blocked_ips = {}  # IP -> block_until_timestamp

    def add_request(self, key: str, timestamp: float):
        """Add a request timestamp for a key."""
        self.requests[key].append(timestamp)

    def get_request_count(self, key: str, window_start: float) -> int:
        """Get count of requests after window_start."""
        # Clean old entries
        self.requests[key] = [
            ts for ts in self.requests[key] if ts > window_start
        ]
        return len(self.requests[key])

    def block_ip(self, ip: str, duration_seconds: int):
        """Block an IP for a duration."""
        self.blocked_ips[ip] = time.time() + duration_seconds

    def is_blocked(self, ip: str) -> bool:
        """Check if an IP is blocked."""
        if ip in self.blocked_ips:
            if time.time() < self.blocked_ips[ip]:
                return True
            else:
                del self.blocked_ips[ip]
        return False

    def get_block_remaining(self, ip: str) -> int:
        """Get remaining block time in seconds."""
        if ip in self.blocked_ips:
            remaining = int(self.blocked_ips[ip] - time.time())
            return max(0, remaining)
        return 0


# Global storage instance
rate_limit_storage = InMemoryRateLimitStorage()


def parse_rate_limit(limit_str: str) -> tuple[int, int]:
    """
    Parse rate limit string like '5/minute' or '100/hour'.

    Returns:
        Tuple of (max_requests, window_seconds)
    """
    parts = limit_str.lower().split("/")
    if len(parts) != 2:
        raise ValueError(f"Invalid rate limit format: {limit_str}")

    max_requests = int(parts[0])
    period = parts[1]

    period_map = {
        "second": 1,
        "minute": 60,
        "hour": 3600,
        "day": 86400,
    }

    if period not in period_map:
        raise ValueError(f"Invalid period: {period}")

    return max_requests, period_map[period]


def get_client_ip(request: Request) -> str:
    """
    Get the real client IP, considering proxies.
    """
    # Check for forwarded headers (when behind proxy/load balancer)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # Get the first IP in the chain (original client)
        return forwarded.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()

    # Fallback to direct client IP
    if request.client:
        return request.client.host

    return "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Advanced rate limiting middleware with:
    - Per-endpoint rate limits
    - IP-based blocking for repeated violations
    - Rate limit headers in responses
    """

    # Endpoint-specific rate limits
    ENDPOINT_LIMITS = {
        "/auth/login": settings.RATE_LIMIT_LOGIN,
        "/auth/register": settings.RATE_LIMIT_REGISTER,
        "/auth/refresh": settings.RATE_LIMIT_REFRESH,
    }

    # Block settings
    VIOLATION_THRESHOLD = 10  # Number of violations before blocking
    BLOCK_DURATION = 300  # Block duration in seconds (5 minutes)

    def __init__(self, app):
        super().__init__(app)
        self.violations = defaultdict(int)  # IP -> violation count

    async def dispatch(self, request: Request, call_next) -> Response:
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)

        client_ip = get_client_ip(request)
        path = request.url.path

        # Check if IP is blocked
        if rate_limit_storage.is_blocked(client_ip):
            remaining = rate_limit_storage.get_block_remaining(client_ip)
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Too Many Requests",
                    "detail": f"IP temporarily blocked. Try again in {remaining} seconds.",
                    "retry_after": remaining,
                },
                headers={
                    "Retry-After": str(remaining),
                    "X-RateLimit-Blocked": "true",
                },
            )

        # Get rate limit for this endpoint
        limit_str = self.ENDPOINT_LIMITS.get(path, settings.RATE_LIMIT_DEFAULT)
        max_requests, window_seconds = parse_rate_limit(limit_str)

        # Calculate rate limit
        now = time.time()
        window_start = now - window_seconds
        key = f"{client_ip}:{path}"

        current_count = rate_limit_storage.get_request_count(key, window_start)

        # Check if limit exceeded
        if current_count >= max_requests:
            # Record violation
            self.violations[client_ip] += 1

            # Block IP if too many violations
            if self.violations[client_ip] >= self.VIOLATION_THRESHOLD:
                rate_limit_storage.block_ip(client_ip, self.BLOCK_DURATION)
                self.violations[client_ip] = 0  # Reset counter

                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": "Too Many Requests",
                        "detail": f"IP blocked for {self.BLOCK_DURATION} seconds due to repeated violations.",
                        "retry_after": self.BLOCK_DURATION,
                    },
                    headers={
                        "Retry-After": str(self.BLOCK_DURATION),
                        "X-RateLimit-Blocked": "true",
                    },
                )

            # Calculate retry time
            oldest_request = min(rate_limit_storage.requests[key])
            retry_after = int(oldest_request + window_seconds - now) + 1

            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Too Many Requests",
                    "detail": f"Rate limit exceeded. Maximum {max_requests} requests per {window_seconds} seconds.",
                    "retry_after": retry_after,
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(oldest_request + window_seconds)),
                },
            )

        # Add current request
        rate_limit_storage.add_request(key, now)

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        remaining = max_requests - current_count - 1
        reset_time = int(now + window_seconds)

        response.headers["X-RateLimit-Limit"] = str(max_requests)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        response.headers["X-RateLimit-Reset"] = str(reset_time)

        return response


def rate_limit(limit: str = None):
    """
    Decorator for endpoint-specific rate limiting.

    Usage:
        @app.get("/api/resource")
        @rate_limit("10/minute")
        async def get_resource():
            ...
    """
    def decorator(func: Callable) -> Callable:
        func._rate_limit = limit or settings.RATE_LIMIT_DEFAULT
        return func
    return decorator
