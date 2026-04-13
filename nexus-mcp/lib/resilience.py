"""Resilience utilities for enterprise HTTP clients.

Provides retry logic with exponential backoff and circuit breaker pattern
to prevent cascade failures when enterprise systems are unavailable.

Usage:
    from resilience import resilient_http_call
    
    @resilient_http_call(service_name="Workday")
    async def get(self, path: str) -> Any:
        # Your HTTP call here
        pass
"""

from __future__ import annotations
import asyncio
import logging
from datetime import datetime, timedelta, UTC
from enum import Enum
from typing import Any, Callable, TypeVar
from functools import wraps

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception,
    before_sleep_log,
    RetryError,
)

logger = logging.getLogger(__name__)

# Type variable for async functions
T = TypeVar("T")


class CircuitState(str, Enum):
    """Circuit breaker states following the classic pattern."""
    CLOSED = "closed"       # Normal operation
    OPEN = "open"           # Failures exceeded threshold, rejecting calls
    HALF_OPEN = "half_open" # Testing if service recovered


class CircuitBreaker:
    """Circuit breaker for a single service to prevent hammering failing systems.
    
    Pattern:
    - CLOSED: Normal operation. Count consecutive failures.
    - OPEN: After threshold failures, open circuit and reject calls for timeout period.
    - HALF_OPEN: After timeout, allow one test request. If succeeds → CLOSED, if fails → OPEN.
    
    Args:
        service_name: Identifier for the protected service (e.g., "Workday", "Entra").
        failure_threshold: Number of consecutive failures before opening circuit.
        timeout_seconds: How long to wait before testing recovery (half-open state).
    """
    
    def __init__(
        self,
        service_name: str,
        failure_threshold: int = 5,
        timeout_seconds: int = 60,
    ):
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        
        self.state = CircuitState.CLOSED
        self.consecutive_failures = 0
        self.last_failure_time: datetime | None = None
        self._lock = asyncio.Lock()
    
    async def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Execute function with circuit breaker protection.
        
        Raises:
            CircuitBreakerOpenError: If circuit is open and not ready for retry.
        """
        async with self._lock:
            # Check if we should transition from OPEN → HALF_OPEN
            if self.state == CircuitState.OPEN:
                if self.last_failure_time and datetime.now(UTC) - self.last_failure_time > timedelta(seconds=self.timeout_seconds):
                    logger.info(f"[{self.service_name}] Circuit transitioning OPEN → HALF_OPEN (testing recovery)")
                    self.state = CircuitState.HALF_OPEN
                else:
                    raise CircuitBreakerOpenError(
                        f"{self.service_name} circuit breaker is OPEN (fast-fail mode). "
                        f"Retry after {self.timeout_seconds}s timeout."
                    )
        
        # Execute the function
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except Exception as e:
            await self._on_failure()
            raise
    
    async def _on_success(self) -> None:
        """Handle successful call — reset failure count and close circuit."""
        async with self._lock:
            if self.state == CircuitState.HALF_OPEN:
                logger.info(f"[{self.service_name}] Circuit HALF_OPEN → CLOSED (service recovered)")
            self.state = CircuitState.CLOSED
            self.consecutive_failures = 0
            self.last_failure_time = None
    
    async def _on_failure(self) -> None:
        """Handle failed call — increment failures and potentially open circuit."""
        async with self._lock:
            self.consecutive_failures += 1
            self.last_failure_time = datetime.now(UTC)
            
            if self.state == CircuitState.HALF_OPEN:
                # Half-open test failed → back to OPEN
                logger.warning(f"[{self.service_name}] Circuit HALF_OPEN → OPEN (recovery test failed)")
                self.state = CircuitState.OPEN
            elif self.consecutive_failures >= self.failure_threshold:
                # Threshold exceeded → open circuit
                logger.error(
                    f"[{self.service_name}] Circuit CLOSED → OPEN "
                    f"({self.consecutive_failures} consecutive failures, threshold={self.failure_threshold})"
                )
                self.state = CircuitState.OPEN


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open and rejecting calls."""
    pass


# Global registry of circuit breakers (one per service)
_circuit_breakers: dict[str, CircuitBreaker] = {}


def get_circuit_breaker(service_name: str) -> CircuitBreaker:
    """Get or create circuit breaker for a service."""
    if service_name not in _circuit_breakers:
        _circuit_breakers[service_name] = CircuitBreaker(service_name)
    return _circuit_breakers[service_name]


def resilient_http_call(
    service_name: str,
    max_attempts: int = 3,
    enable_circuit_breaker: bool = True,
) -> Callable:
    """Decorator for HTTP calls that adds retry logic and circuit breaker.
    
    Retry strategy:
    - 3 attempts by default with exponential backoff (2s → 4s → 8s)
    - Retries on: httpx.TimeoutException, httpx.HTTPStatusError (5xx only)
    - No retry on: 4xx errors (client errors like 404, 401)
    
    Circuit breaker:
    - Opens after 5 consecutive failures
    - Fast-fails subsequent requests for 60 seconds
    - Automatically tests recovery after timeout
    
    Args:
        service_name: Name of the service (for logging and circuit breaker tracking).
        max_attempts: Maximum number of retry attempts (default: 3).
        enable_circuit_breaker: Whether to use circuit breaker (default: True).
    
    Example:
        @resilient_http_call(service_name="Workday")
        async def get(self, path: str) -> dict:
            resp = await self._http.get(url)
            resp.raise_for_status()
            return resp.json()
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        # Determine if we should retry based on exception type and status code
        def should_retry_exception(exception: Exception) -> bool:
            """Only retry on transient failures (timeouts, 5xx errors)."""
            if isinstance(exception, httpx.TimeoutException):
                return True
            if isinstance(exception, httpx.HTTPStatusError):
                # Retry on 5xx (server errors), not on 4xx (client errors)
                return exception.response.status_code >= 500
            if isinstance(exception, (httpx.ConnectError, httpx.RemoteProtocolError)):
                return True
            return False
        
        # Apply tenacity retry decorator with custom retry condition
        retrying_func = retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            retry=retry_if_exception(should_retry_exception),
            before_sleep=before_sleep_log(logger, logging.INFO),
            reraise=True,
        )(func)
        
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            if enable_circuit_breaker:
                breaker = get_circuit_breaker(service_name)
                try:
                    return await breaker.call(retrying_func, *args, **kwargs)
                except RetryError as e:
                    # Extract original exception from tenacity wrapper
                    logger.error(f"[{service_name}] All retry attempts exhausted: {e}")
                    raise e.last_attempt.exception() if e.last_attempt.exception() else e
            else:
                # No circuit breaker, just retry logic
                try:
                    return await retrying_func(*args, **kwargs)
                except RetryError as e:
                    logger.error(f"[{service_name}] All retry attempts exhausted: {e}")
                    raise e.last_attempt.exception() if e.last_attempt.exception() else e
        
        return wrapper
    
    return decorator


def handle_404_gracefully(func: Callable[..., T]) -> Callable[..., T | None]:
    """Decorator to convert 404 errors to None instead of raising.
    
    Useful for "get user/device by ID" operations where 404 = "not found" is a valid state.
    
    Example:
        @handle_404_gracefully
        @resilient_http_call(service_name="Entra")
        async def get_user(self, user_id: str) -> dict | None:
            resp = await self._http.get(f"/users/{user_id}")
            resp.raise_for_status()  # Will be caught if 404
            return resp.json()
    """
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> T | None:
        try:
            return await func(*args, **kwargs)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.debug(f"Resource not found (404): {e.request.url}")
                return None
            raise
    
    return wrapper
