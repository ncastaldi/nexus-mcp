# Enterprise System Resilience Feature

## Overview

This document describes the enterprise system resilience feature that resolves **CRITICAL #1** from the code health report: "No Resilience When Enterprise Systems Fail."

**Problem:** Your HTTP clients crashed on any API failure. If Workday went down during a weekly drift audit, the ENTIRE audit failed—even though AD and Entra data were still accessible.

**Solution:** Automatic retry logic with exponential backoff, circuit breaker pattern, and graceful degradation allow drift audits to continue with partial data when some systems are unavailable.

---

## Features

### 1. Automatic Retry Logic

All HTTP clients automatically retry transient failures with exponential backoff:

- **Max Attempts:** 3 (configurable)
- **Backoff Strategy:** 2s → 4s → 8s exponential delay
- **Retries On:** 5xx errors, timeouts, connection errors
- **Does NOT Retry:** 4xx errors (client errors like 404 are instant failures)

**Example: Transient Failure**
```
Attempt 1: 503 Service Unavailable → wait 2s
Attempt 2: 503 Service Unavailable → wait 4s
Attempt 3: Data returned → success ✓
```

### 2. Circuit Breaker Pattern

Prevents hammering a failing service by "opening the circuit":

- **Threshold:** 5 consecutive failures triggers the circuit to open
- **Open State (60s):** Subsequent requests fail instantly with `CircuitBreakerOpenError` (no timeout waste)
- **Half-Open State (testing):** After 60s timeout, one test request allowed
- **Close State (recovery):** If test succeeds, circuit closes and normal operation resumes

**Example: Sustained Failure**
```
Requests 1-5:  Each retries 3 times (network errors)
Request 6:     Circuit opens immediately (no retry)
Request 7:     Circuit still open, fails fast (<100ms)
After 60s:     Circuit half-open, test request sent
Test success:  Circuit closes, normal retries resume
```

### 3. Graceful Degradation in Audit Tools

Audit tools wrap each system call separately, so if one system fails, the audit continues with available systems:

**audit_user_drift() Example:**
```python
# Before: Any failure crashed the entire audit
# After: Wraps each system separately
try:
    wd_data = await _get_wd().get("/staffing/v6/workers", ...)
    systems_available.append("Workday")
except Exception as e:
    systems_failed.append("Workday")
    logger.warning(f"Workday unavailable: {e}")

# Continue with AD and Entra even if Workday failed...
```

**Response Example:**
```json
{
  "email": "john.doe@wheels.com",
  "systems_checked": ["Workday", "ActiveDirectory", "Entra"],
  "systems_available": ["ActiveDirectory", "Entra"],
  "systems_failed": ["Workday"],
  "workday_found": false,
  "ad_found": true,
  "entra_found": true,
  "discrepancy_count": 1,
  "discrepancies": [
    {
      "field": "job_title",
      "system_a": "ActiveDirectory",
      "value_a": "Senior Engineer",
      "system_b": "Entra",
      "value_b": "Engineer",
      "severity": "medium"
    }
  ]
}
```

### 4. Proactive Health Monitoring

**New Tool: `check_system_health()`**

Pings all enterprise systems and returns availability + response times:

```json
{
  "timestamp": "2026-04-13T14:30:00Z",
  "systems": {
    "Workday": {"available": true, "response_time_ms": 245},
    "ActiveDirectory": {"available": true, "response_time_ms": 150},
    "Entra": {"available": true, "response_time_ms": 320},
    "Lansweeper": {"available": false, "error": "TimeoutException..."},
    "Intune": {"available": true, "response_time_ms": 280},
    "Helix": {"available": true, "response_time_ms": 410}
  },
  "summary": {
    "total_systems": 6,
    "available_systems": 5,
    "unavailable_systems": 1,
    "availability_percentage": 83
  }
}
```

**Use Case:** Run this before bulk audits to decide whether to proceed or wait.

---

## Implementation Details

### Modified Files

| File | Change |
|------|--------|
| `pyproject.toml` | Added `tenacity>=8.2.0` dependency |
| `lib/resilience.py` | **NEW** — Retry decorator, circuit breaker, 404 handler |
| `lib/workday_client.py` | Applied `@resilient_http_call` to `get()`, `raas()` |
| `lib/entra_client.py` | Applied `@resilient_http_call` to `get()`, `get_all_pages()` |
| `lib/helix_client.py` | Applied `@resilient_http_call` to `get()`, `post()` |
| `lib/intune_client.py` | Applied `@resilient_http_call` to `get()` |
| `lib/lansweeper_client.py` | Applied `@resilient_http_call` to `gql()` |
| `lib/fedex_client.py` | Applied `@resilient_http_call` to `post()` |
| `src/shards/audit.py` | Graceful degradation in `audit_user_drift()`, `audit_device_drift()`, new `check_system_health()` tool |
| `tests/test_resilience.py` | **NEW** — 12 comprehensive unit tests |

### Decorators

#### @resilient_http_call

Applies retry logic and circuit breaker to async HTTP functions:

```python
from resilience import resilient_http_call

@resilient_http_call(service_name="Workday", max_attempts=3)
async def get(self, path: str) -> dict:
    resp = await self._http.get(url)
    resp.raise_for_status()
    return resp.json()
```

**Parameters:**
- `service_name` (str): Service identifier for logging and circuit breaker tracking
- `max_attempts` (int): Maximum retry attempts (default: 3)
- `enable_circuit_breaker` (bool): Whether to use circuit breaker (default: True)

#### @handle_404_gracefully

Converts 404 errors to `None` instead of raising:

```python
from resilience import handle_404_gracefully

@handle_404_gracefully
@resilient_http_call(service_name="Entra")
async def get_user(user_id: str) -> dict | None:
    resp = await self._http.get(f"/users/{user_id}")
    resp.raise_for_status()
    return resp.json()

result = await get_user("nonexistent-id")  # Returns None instead of raising
```

---

## Testing

### Run All Tests

```bash
cd nexus-mcp
pytest tests/test_resilience.py -v
```

**Expected Output:**
```
tests/test_resilience.py::TestCircuitBreaker::test_circuit_closed_to_open_after_threshold_failures PASSED
tests/test_resilience.py::TestCircuitBreaker::test_circuit_half_open_to_closed_on_success PASSED
tests/test_resilience.py::TestCircuitBreaker::test_circuit_half_open_to_open_on_failure PASSED
tests/test_resilience.py::TestCircuitBreaker::test_circuit_resets_on_success PASSED
tests/test_resilience.py::TestResilientHttpCall::test_retries_on_timeout_exception PASSED
tests/test_resilience.py::TestResilientHttpCall::test_retries_on_5xx_errors PASSED
tests/test_resilience.py::TestResilientHttpCall::test_no_retry_on_4xx_errors PASSED
tests/test_resilience.py::TestResilientHttpCall::test_exhausts_retries_and_raises PASSED
tests/test_resilience.py::TestHandle404Gracefully::test_converts_404_to_none PASSED
tests/test_resilience.py::TestHandle404Gracefully::test_does_not_convert_other_errors PASSED
tests/test_resilience.py::TestHandle404Gracefully::test_returns_normal_result_on_success PASSED
tests/test_resilience.py::TestCircuitBreakerIntegration::test_circuit_breaker_opens_after_failures PASSED

======================== 12 passed in 12.40s ========================
```

### Manual Testing

#### Test 1: Graceful Degradation

**Setup:**
1. Edit `.env` — temporarily invalidate one credential (e.g., `WORKDAY_CLIENT_ID=invalid`)
2. Ensure `USE_MOCK=false` (live mode)

**Run:**
```bash
python src/main.py
# In MCP client:
audit_user_drift(email="test@example.com")
```

**Expected Result:**
```json
{
  "systems_available": ["ActiveDirectory", "Entra"],
  "systems_failed": ["Workday"],
  "discrepancy_count": 1
}
```

**Verification:**
- ✅ No crash
- ✅ Audit continues with available systems
- ✅ Drift comparison runs for AD ↔ Entra

#### Test 2: Circuit Breaker

**Setup:**
1. Simulate sustained Workday outage (disable service or firewall block)
2. Credentials valid but service unreachable

**Run:**
```bash
python src/main.py
# In MCP client:
audit_bulk_user_drift(emails=["user1@example.com", "user2@example.com", ..., "user10@example.com"])
```

**Expected Logs:**
```
[audit_user_drift] Workday: Attempt 1/3 (retry on transient error)
[audit_user_drift] Workday: Attempt 2/3 (retry on transient error)
[audit_user_drift] Workday: Attempt 3/3 (retry on transient error)
[resilience] [Workday] Circuit CLOSED → OPEN (5 consecutive failures)
[audit_user_drift] Workday: CircuitBreakerOpenError (fast-fail)
```

**Verification:**
- ✅ First 5 requests retry 3 times each
- ✅ Subsequent requests fail instantly (< 100ms)
- ✅ Logs show circuit state transitions

#### Test 3: Retry on Transient Failure

**Setup:**
1. Valid credentials
2. Introduce 1-second network delay (via proxy or `tc` on Linux)

**Run:**
```bash
python src/main.py
# In MCP client:
audit_user_drift(email="test@example.com")
```

**Expected Result:**
- ✅ Tool succeeds (after retries)
- ✅ Response includes full drift data
- ✅ Logs show "Retry attempt 1/3", "Retry attempt 2/3"

#### Test 4: Health Check

**Run:**
```bash
python src/main.py
# In MCP client:
check_system_health()
```

**Expected Result:**
```json
{
  "summary": {
    "total_systems": 6,
    "available_systems": 6,
    "availability_percentage": 100
  },
  "systems": {
    "Workday": {"available": true, "response_time_ms": ...},
    ...
  }
}
```

**Decision Logic:**
- If `availability_percentage >= 80`: Safe to run bulk audits
- If `availability_percentage < 80`: Postpone or expect partial results

---

## Deployment

### Prerequisites

```bash
# Navigate to nexus-mcp
cd nexus-mcp

# Install dependencies (including tenacity)
pip install -e .
```

### Verify Installation

```bash
python -c "from resilience import resilient_http_call; print('✓ Installed')"
```

### Run in Production

**With credential-based authentication:**
```bash
USE_MOCK=false python src/main.py
```

**With mock data (testing):**
```bash
USE_MOCK=true python src/main.py
```

### Monitoring

Watch logs for:
- `[resilience]` messages — retry events, circuit breaker state changes
- `CircuitBreakerOpenError` — indicates sustained service outage
- Retry counts — indicates transient network issues

**Example Alert Rules:**
- If `"CircuitBreakerOpenError found in logs"` → Investigate service
- If `"Retry attempt 2/3" repeated > 10 times in 5 minutes` → Network degradation
- If `"Circuit.*OPEN"` → Service outage (escalate to on-call)

---

## Troubleshooting

### Symptom: "CircuitBreakerOpenError: Workday circuit breaker is OPEN"

**Cause:** 5 consecutive Workday failures within the monitoring window.

**Solution:**
1. Check Workday status (https://status.workday.com)
2. Verify credentials in `.env` — test manually with `curl` or Postman
3. Check network connectivity — can you reach `api.myworkday.com`?
4. Wait 60 seconds for circuit to enter half-open state and test recovery
5. Monitor logs for `"Circuit HALF_OPEN → CLOSED"` indicating recovery

### Symptom: Audit returns empty `systems_available` list

**Cause:** All systems are down or credentials are invalid.

**Solution:**
1. Run `check_system_health()` to identify which system is down
2. For downed systems:
   - Check system status pages
   - Verify network connectivity
   - Wait for service to recover
3. For credential issues:
   - Verify `.env` has valid credentials
   - Test credentials manually via API (e.g., `curl` for Workday OAuth)
   - Regenerate tokens/credentials if expired

### Symptom: Slow response times even on successful requests

**Observe:** Use `check_system_health()` to identify slow systems.

**Solution:**
- If `response_time_ms > 5000`: System is under load, expect slower audits
- Network latency → Consider running audits during low-traffic windows
- Consider increasing timeouts if system is reliably slow but functional

### Symptom: Excessively verbose retry logs

**Cause:** Transient network issues causing multiple retries.

**Solution:**
- Expected during network instability
- Monitor for patterns (e.g., always fails at certain time)
- Use `check_system_health()` to confirm system is reachable
- If persistent, investigate network (firewall, ISP, proxy issues)

---

## Configuration

### Retry Policy

**Currently Hard-Coded:**
- Max attempts: 3
- Backoff: exponential (2s, 4s, 8s)

**To Customize:**
Edit retry decorator in [lib/resilience.py](lib/resilience.py):

```python
@resilient_http_call(service_name="Workday", max_attempts=5)  # ← Change here
```

### Circuit Breaker Threshold

**Currently Hard-Coded:**
- Failure threshold: 5 consecutive failures
- Timeout before half-open: 60 seconds

**To Customize:**
Edit [lib/resilience.py](lib/resilience.py):

```python
breaker = CircuitBreaker("Workday", failure_threshold=10, timeout_seconds=120)
```

---

## Future Enhancements

1. **Configurable Retry Policy** — Move retry/backoff settings to `.env` or config file
2. **Metrics & Observability** — Track retry counts, circuit breaker events in audit logs
3. **Token Expiration Handling** — Cache token expiry times and refresh proactively (CRITICAL #2)
4. **PowerShell Command Injection Fix** — Use parameterized queries to prevent AD injection attacks (CRITICAL #3)
5. **Database Fallback** — Cache drift results locally for offline resilience
6. **Rate Limiting** — Implement exponential backoff to respect API rate limits

---

## References

- **Code Health Report:** `documentation/reports/code-health-report-2026-04-13.md`
- **Tenacity Docs:** https://tenacity.readthedocs.io/
- **Feature Branch:** `feat/add-enterprise-resilience`
- **Commits:**
  - `6337182` — Initial implementation
  - `eb8b14b` — Fix retry logic and datetime deprecation
