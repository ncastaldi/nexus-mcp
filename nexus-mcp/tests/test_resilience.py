"""Unit tests for resilience module (retry logic and circuit breaker)."""

import pytest
import asyncio
import sys
import os
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

# Add lib/ to path so we can import resilience module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))

from resilience import (
    resilient_http_call,
    handle_404_gracefully,
    CircuitBreaker,
    CircuitState,
    CircuitBreakerOpenError,
    get_circuit_breaker,
)


class TestCircuitBreaker:
    """Test circuit breaker state machine."""
    
    @pytest.mark.asyncio
    async def test_circuit_closed_to_open_after_threshold_failures(self):
        """Circuit should open after consecutive failures exceed threshold."""
        breaker = CircuitBreaker("TestService", failure_threshold=3, timeout_seconds=60)
        
        async def failing_func():
            raise httpx.HTTPStatusError("Server error", request=MagicMock(), response=MagicMock(status_code=503))
        
        # Execute 3 failures
        for _ in range(3):
            with pytest.raises(httpx.HTTPStatusError):
                await breaker.call(failing_func)
        
        # Circuit should now be OPEN
        assert breaker.state == CircuitState.OPEN
        
        # Next call should fail fast with CircuitBreakerOpenError
        with pytest.raises(CircuitBreakerOpenError):
            await breaker.call(failing_func)
    
    @pytest.mark.asyncio
    async def test_circuit_half_open_to_closed_on_success(self):
        """Circuit should close after successful test in half-open state."""
        breaker = CircuitBreaker("TestService", failure_threshold=2, timeout_seconds=1)
        
        async def failing_func():
            raise httpx.TimeoutException("Timeout")
        
        async def success_func():
            return "OK"
        
        # Trigger failures to open circuit
        for _ in range(2):
            with pytest.raises(httpx.TimeoutException):
                await breaker.call(failing_func)
        
        assert breaker.state == CircuitState.OPEN
        
        # Wait for timeout to transition to half-open
        await asyncio.sleep(1.1)
        
        # Successful call should close circuit
        result = await breaker.call(success_func)
        assert result == "OK"
        assert breaker.state == CircuitState.CLOSED
        assert breaker.consecutive_failures == 0
    
    @pytest.mark.asyncio
    async def test_circuit_half_open_to_open_on_failure(self):
        """Circuit should reopen if test fails in half-open state."""
        breaker = CircuitBreaker("TestService", failure_threshold=2, timeout_seconds=1)
        
        async def failing_func():
            raise httpx.ConnectError("Connection refused")
        
        # Trigger failures to open circuit
        for _ in range(2):
            with pytest.raises(httpx.ConnectError):
                await breaker.call(failing_func)
        
        assert breaker.state == CircuitState.OPEN
        
        # Wait for timeout to transition to half-open
        await asyncio.sleep(1.1)
        
        # Failed test should reopen circuit
        with pytest.raises(httpx.ConnectError):
            await breaker.call(failing_func)
        
        assert breaker.state == CircuitState.OPEN
    
    @pytest.mark.asyncio
    async def test_circuit_resets_on_success(self):
        """Successful calls should reset failure counter."""
        breaker = CircuitBreaker("TestService", failure_threshold=3)
        
        async def failing_func():
            raise httpx.TimeoutException("Timeout")
        
        async def success_func():
            return "OK"
        
        # Execute 2 failures (below threshold)
        for _ in range(2):
            with pytest.raises(httpx.TimeoutException):
                await breaker.call(failing_func)
        
        assert breaker.consecutive_failures == 2
        assert breaker.state == CircuitState.CLOSED
        
        # Successful call resets counter
        await breaker.call(success_func)
        assert breaker.consecutive_failures == 0
        assert breaker.state == CircuitState.CLOSED


class TestResilientHttpCall:
    """Test resilient_http_call decorator with retry logic."""
    
    @pytest.mark.asyncio
    async def test_retries_on_timeout_exception(self):
        """Decorator should retry on timeout exceptions."""
        call_count = 0
        
        @resilient_http_call(service_name="TestService", max_attempts=3, enable_circuit_breaker=False)
        async def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise httpx.TimeoutException("Timeout")
            return "Success"
        
        result = await flaky_function()
        assert result == "Success"
        assert call_count == 3  # 1 initial + 2 retries
    
    @pytest.mark.asyncio
    async def test_retries_on_5xx_errors(self):
        """Decorator should retry on 5xx HTTP errors."""
        call_count = 0
        
        @resilient_http_call(service_name="TestService", max_attempts=3, enable_circuit_breaker=False)
        async def server_error_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                response = MagicMock()
                response.status_code = 503
                raise httpx.HTTPStatusError("Service Unavailable", request=MagicMock(), response=response)
            return "Success"
        
        result = await server_error_function()
        assert result == "Success"
        assert call_count == 2  # 1 initial + 1 retry
    
    @pytest.mark.asyncio
    async def test_no_retry_on_4xx_errors(self):
        """Decorator should NOT retry on 4xx client errors."""
        call_count = 0
        
        @resilient_http_call(service_name="TestService", max_attempts=3, enable_circuit_breaker=False)
        async def client_error_function():
            nonlocal call_count
            call_count += 1
            response = MagicMock()
            response.status_code = 404
            raise httpx.HTTPStatusError("Not Found", request=MagicMock(), response=response)
        
        with pytest.raises(httpx.HTTPStatusError):
            await client_error_function()
        
        assert call_count == 1  # No retries on 4xx
    
    @pytest.mark.asyncio
    async def test_exhausts_retries_and_raises(self):
        """Decorator should raise original exception after exhausting retries."""
        call_count = 0
        
        @resilient_http_call(service_name="TestService", max_attempts=3, enable_circuit_breaker=False)
        async def always_fails():
            nonlocal call_count
            call_count += 1
            raise httpx.TimeoutException("Persistent timeout")
        
        with pytest.raises(httpx.TimeoutException) as exc_info:
            await always_fails()
        
        assert "Persistent timeout" in str(exc_info.value)
        assert call_count == 3  # 1 initial + 2 retries


class TestHandle404Gracefully:
    """Test handle_404_gracefully decorator."""
    
    @pytest.mark.asyncio
    async def test_converts_404_to_none(self):
        """Decorator should convert 404 errors to None."""
        @handle_404_gracefully
        async def get_user():
            response = MagicMock()
            response.status_code = 404
            response.request.url = "https://api.example.com/users/123"
            raise httpx.HTTPStatusError("Not Found", request=MagicMock(), response=response)
        
        result = await get_user()
        assert result is None
    
    @pytest.mark.asyncio
    async def test_does_not_convert_other_errors(self):
        """Decorator should NOT convert non-404 errors."""
        @handle_404_gracefully
        async def get_user():
            response = MagicMock()
            response.status_code = 500
            raise httpx.HTTPStatusError("Server Error", request=MagicMock(), response=response)
        
        with pytest.raises(httpx.HTTPStatusError):
            await get_user()
    
    @pytest.mark.asyncio
    async def test_returns_normal_result_on_success(self):
        """Decorator should pass through successful results."""
        @handle_404_gracefully
        async def get_user():
            return {"id": 123, "name": "John Doe"}
        
        result = await get_user()
        assert result == {"id": 123, "name": "John Doe"}


class TestCircuitBreakerIntegration:
    """Test integration of circuit breaker with resilient_http_call decorator."""
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_after_failures(self):
        """Circuit breaker should open and fast-fail after threshold."""
        # Get a fresh circuit breaker for this test
        service_name = "IntegrationTestService"
        breaker = get_circuit_breaker(service_name)
        breaker.failure_threshold = 3
        breaker.state = CircuitState.CLOSED
        breaker.consecutive_failures = 0
        
        call_count = 0
        
        @resilient_http_call(service_name=service_name, max_attempts=1)
        async def always_fails():
            nonlocal call_count
            call_count += 1
            raise httpx.TimeoutException("Persistent failure")
        
        # Execute 3 failures to open circuit
        for _ in range(3):
            with pytest.raises(httpx.TimeoutException):
                await always_fails()
        
        assert breaker.state == CircuitState.OPEN
        
        # Next call should fail fast with CircuitBreakerOpenError
        with pytest.raises(CircuitBreakerOpenError):
            await always_fails()
        
        # Call count should be 3 (circuit now open, no more attempts)
        assert call_count == 3


# Run tests with pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
