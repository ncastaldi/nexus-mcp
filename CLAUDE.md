# nexus-mcp

## Project overview

Nexus-MCP is a self-hosted MCP server that bridges enterprise systems — Active Directory, Entra ID, Workday HCM, BMC Helix ITSM, Lansweeper, Intune, and FedEx — with LLM-based agents via the Model Context Protocol. It normalizes responses from all those systems into canonical Pydantic schemas, detects cross-system drift (e.g., an employee terminated in Workday but still enabled in AD), and appends a structured JSONL audit trail for every tool call to satisfy SOC 2 controls CC7.2, CC6.1, PI1.4, PI1.5, and A1.1. The primary consumer is Frank v6, a modular AI assistant, but any MCP-compatible client (Claude Desktop, VS Code extension) can connect. The project is maintained by Nathan Castaldi and is at version 0.1.4.

---

## Architecture

### Shard pattern

Every integration domain lives in its own module under `nexus-mcp/src/shards/`. Each shard exports exactly one function:

```python
def register(mcp: FastMCP) -> None: ...
```

`src/main.py` reads `ENABLE_*` environment flags and calls `register()` for each enabled shard at import time. No other file changes when a shard is added or removed. No shard imports from another shard — cross-shard coupling is explicitly forbidden.

### Module map

| Path | Owns |
|---|---|
| `src/main.py` | Server construction, feature-flag shard loading, SOC 2 audit middleware, two built-in audit query tools |
| `src/shards/identity.py` | 15 AD + Entra ID tools |
| `src/shards/workday.py` | 7 Workday HCM tools |
| `src/shards/audit.py` | 4 cross-system drift detection tools + 2 audit-log query tools |
| `src/shards/itsm.py` | 6 BMC Helix ITSM tools (see [current state](#current-state)) |
| `src/shards/assets.py` | 11 Lansweeper + Intune tools (see [current state](#current-state)) |
| `src/shards/logistics.py` | 5 FedEx tools |
| `lib/config.py` | Pydantic `BaseSettings` classes for every system's credentials |
| `lib/schemas.py` | Canonical models: `CanonicalUser`, `CanonicalDevice`, `CanonicalIncident`, `CanonicalShipment`, `FieldDrift`, `UserDriftReport`, enums |
| `lib/adapters.py` | Per-system adapter classes; each exposes `.to_canonical()` returning a model from `schemas.py` |
| `lib/ad_adapter.py` | LDAP/Active Directory backend using ldap3 |
| `lib/entra_client.py` | Microsoft Graph API via MSAL OAuth2 |
| `lib/workday_client.py` | Workday REST v1/v6 with OAuth2 refresh token flow |
| `lib/helix_client.py` | BMC Helix AR-JWT authentication |
| `lib/lansweeper_client.py` | Lansweeper GraphQL queries |
| `lib/intune_client.py` | Microsoft Graph (same Entra credentials as `entra_client.py`) |
| `lib/fedex_client.py` | FedEx OAuth2 + REST |
| `lib/drift_detection.py` | `scan_*` functions comparing cross-system fields |
| `lib/audit_log.py` | Append-only JSONL logger; auto-redacts secrets; `AuditLogger` singleton |
| `lib/resilience.py` | `@resilient_http_call` retry decorator, `CircuitBreaker` (5 failures → 60 s open) |
| `lib/mock_data.py` | 9 synthetic employee records (EMP001–EMP777) with pre-seeded drift scenarios |
| `lib/identity_utils.py` | AD-specific helpers |

### Data flow

```
MCP client (stdio)
  → FastMCP router
    → tool function (shard)
      → system client  OR  mock_data (when USE_MOCK=true)
        → adapter.to_canonical()      # [currently bypassed — see open questions]
          → return value to caller
  ← SOC 2 audit middleware (wraps every tool fn at startup)
    → logs/nexus_audit.jsonl
```

### SOC 2 audit middleware

Applied once in `main.py` **after** all shards load. It iterates `mcp._tool_manager._tools` and replaces each tool's `.fn` with an async wrapper that records `event_id` (UUID v4), `timestamp`, `tool`, `shard`, `action_category`, redacted `args_summary`, `mock_mode`, `status`, `latency_ms`, and any error detail to a JSONL file. Shards are completely unaware of it.

**Known gap:** `nexus_audit_recent` and `nexus_audit_stats` are registered in `main.py` *after* the wrapping loop runs, so those two tools are never audited themselves (`nexus-mcp Consistency Audit.md`, high severity).

### Mock mode

When `USE_MOCK=true`, all shards return data from `lib/mock_data.py` without making real API calls. The 9 synthetic records have intentional cross-system drift (status, job title, department, name) for realistic testing without credentials.

---

## Tech stack

| Component | Package / version |
|---|---|
| Language | Python ≥ 3.11 |
| MCP framework | `mcp >= 1.2.0` (FastMCP) |
| Data validation | `pydantic >= 2.0.0`, `pydantic-settings >= 2.0.0` |
| HTTP client | `httpx >= 0.27.0` |
| AD/LDAP | `ldap3 >= 2.9.1` |
| Microsoft auth | `msal >= 1.28.0` |
| Retry/circuit-breaker | `tenacity >= 8.2.0` |
| Env loading | `python-dotenv >= 1.0.0` |
| Async file I/O | `aiofiles >= 24.1.0` |
| Report formatting | `tabulate >= 0.9.0`, `jinja2 >= 3.1.0` |
| Scheduling | `schedule >= 1.2.0` |
| Date parsing | `python-dateutil >= 2.9.0` |
| Testing | `pytest >= 8.0.0`, `pytest-cov >= 5.0.0`, `pytest-asyncio >= 0.24.0` |
| Build system | `setuptools >= 68`, `wheel` |

`asyncio_mode = "auto"` is set in `pyproject.toml` — all test coroutines run without explicit `@pytest.mark.asyncio`.

---

## Development workflow

All commands run from the `nexus-mcp/` subdirectory (where `pyproject.toml` lives).

### Install

```bash
cd nexus-mcp
python -m venv .venv
source .venv/bin/activate          # Windows: .\.venv\Scripts\Activate.ps1
pip install -e ".[test]"           # installs runtime deps + test extras
cp .env.example .env
```

Edit `.env` before first run. For local development with no credentials:

```
USE_MOCK=true
ENABLE_IDENTITY=true
ENABLE_WORKDAY=true
ENABLE_AUDIT=true
ENABLE_ITSM=true
ENABLE_ASSETS=true
ENABLE_LOGISTICS=true
AUDIT_LOGGING_ENABLED=true
```

### Run the server

```bash
# Via module (works without pip install -e)
python -m main

# Via installed entry point
nexus-mcp
```

The server speaks MCP over stdio. Connect via Claude Desktop or the VS Code extension — see `documentation/VSCODE_INTEGRATION_GUIDE.md`.

### Run tests

```bash
# All unit tests (integration tests skipped by default)
pytest

# Explicit skip of integration tests
pytest -m "not integration"

# With coverage
pytest --cov=src --cov=lib --cov-report=term-missing

# Single file
pytest tests/identity_tests/test_ad_adapter.py

# Resilience unit tests
pytest tests/test_resilience.py -v
```

Integration tests (marked `@pytest.mark.integration`) require live API credentials and are excluded in CI by default.

### Utility scripts

```bash
# Browse all registered tools grouped by shard
python list_tools.py

# Validate MCP protocol handshake
python verify_mcp_protocol.py

# Run all 4 audit tools against mock data with formatted output
python test_client.py
```

### Version bump

```bash
python scripts/bump_version.py [major|minor|patch]
```

### Audit log inspection

```bash
tail -f logs/nexus_audit.jsonl
```

---

## Conventions

### Shard contract

- Every shard module exports exactly `register(mcp: FastMCP) -> None` and nothing else at the public level.
- No shard imports from another shard.
- All `@mcp.tool()` functions are `async def` without exception.
- Every tool carries a docstring describing purpose, parameters, and any required API permissions.

### Client initialization

Clients are never instantiated at module level. Each shard uses a lazy closure:

```python
_client: SomeClient | None = None

def _get() -> SomeClient:
    global _client
    if _client is None:
        _client = SomeClient(Config())
    return _client
```

This defers credential loading until the tool is first called.

### Config access

All credentials flow through Pydantic `BaseSettings` classes in `lib/config.py` (`ADConfig`, `EntraConfig`, `WorkdayConfig`, `HelixConfig`, `LansweeperConfig`, `FedExConfig`, `AuditConfig`, `ReportConfig`). Do not call `os.getenv()` directly in shard or adapter code.

### Tool naming

Tool names use `snake_case` prefixed by system: `ad_`, `entra_`, `workday_`, `helix_`, `lansweeper_`, `intune_`, `fedex_`, `audit_`, `generate_`, `nexus_`. The audit middleware uses these prefixes to infer the originating shard for log entries.

### Return types (stated intent vs. current practice)

The stated design requires tool return values to be canonical Pydantic models from `lib/schemas.py`. In practice, `identity.py` and `workday.py` tools are annotated `-> dict | None` or `-> list[dict]` and return raw adapter output without calling `.to_canonical()`. This is a documented inconsistency (high severity in `nexus-mcp Consistency Audit.md`).

### Known inconsistencies (consistency audit, 2026-05-30)

| Location | Issue | Severity |
|---|---|---|
| `src/shards/identity.py`, `workday.py` | Tools return `dict` instead of canonical models | High |
| `src/main.py` lines 167–188 | Audit query tools registered after middleware loop — never audited | High |
| `src/shards/audit_minimal.py` (if present) | Empty `register()` with module-level `AuditLog()` instantiation side effect | High |
| `src/shards/identity.py`, `workday.py` | `@resilient_http_call` not applied; resilience library tested but unused by live shards | Medium |
| `src/main.py`, `list_tools.py`, `test_client.py`, `verify_mcp_protocol.py` | `_enabled()` helper duplicated in 4 files | Low |
| `src/shards/logistics.py` | `FedExConfig` imported inside tool function body, not at module top | Low |
| `lib/ad_adapter.py` | Unused `import os` | Low |
| 9 Entra-specific tools | Zero test coverage | Medium |

---

## Decision log

### Shard pattern

- Each integration domain is a self-contained Python module with a single `register()` function.
- No shard knows about any other shard; all orchestration lives in `main.py`.
- Ruled out: monolithic tool file; per-shard server processes.

### SOC 2 audit middleware placement

- Middleware wraps all tools in one pass after all shards load, rather than being injected into each shard.
- This keeps shard code ignorant of logging concerns and ensures consistent coverage regardless of which shards are enabled.
- Ruled out: per-shard audit decorators; shard-level logging calls.

### Mock mode design

- `USE_MOCK=true` routes all shards through `lib/mock_data.py` with pre-seeded drift scenarios requiring zero external credentials.
- Drift scenarios are intentional and documented, not random.
- Ruled out: per-shard mock flags; separate mock server process.

### Resilience layer (NEXUS-012, DONE)

- Circuit breaker: 5 consecutive failures → 60 s open window.
- Exponential backoff: 3 attempts (2 s → 4 s → 8 s); does not retry 4xx responses.
- Ruled out: retrying client errors (401, 403, 404).
- Current gap: decorators are implemented and tested but not yet applied to live shard HTTP call sites.

### Git workflow (from `CONTRIBUTING.md`)

- Short-lived feature branches (`feat/`, `project/`, `chore/`).
- Rebase is optional — do nothing unless `main` has changes that affect your branch.
- Wrong-branch commits: cherry-pick onto the correct branch + reset; do not rewrite shared history.
- Ruled out: merge commits for feature integration; forced pushes to `main`.

### Autonomy boundary

- [UNCLEAR — see open questions] `agentic-design-intent.md` at the repo root appears to originate from a different project (`homelab-registry-mcp`). Its principles may still reflect operator intent for this project.
- Fully autonomous writes to live infrastructure (degree 5 on the agentic spectrum) are explicitly out of scope.
- The stated next agentic step (degree 3) is human-in-loop: system proposes a change; a human approves it before it is applied.

### Work item numbering

- NEXUS-XXX format supersedes the original WIS-XXX numbering used during the Workday-AD identity sync planning phase.
- Source of truth: `documentation/project-standards/nexus-work-item-register.md`.

---

## Constraints

- **Do not** add LLM calls, reasoning logic, or DSPy modules inside shards. Shards are thin wrappers.
- **Do not** import one shard from another.
- **Do not** initialize system clients at module level. Use lazy `_get_*()` functions.
- **Do not** read credentials via `os.getenv()` directly in shard or adapter code; use `lib/config.py` Pydantic settings classes.
- **Do not** hardcode credentials anywhere in `src/` or `lib/`.
- **Do not** change the transport from `stdio` without verifying MCP client compatibility. Claude Desktop and the VS Code extension both expect stdio.
- **Do not** register tools after the SOC 2 middleware loop in `main.py` without also wrapping those tools manually. The existing `nexus_audit_recent` / `nexus_audit_stats` pattern is a known bug, not a precedent.
- **Do not** introduce a new shard without the exact `register(mcp: FastMCP) -> None` signature.
- **Do not** merge directly to `main` without a pull request.
- **Do not** clear drift flags manually in data stores — they are re-evaluated on the next scan pass.

---

## Current state

### Done

| NEXUS ID | Work item |
|---|---|
| NEXUS-006 | Workday MCP project scaffold to identity parity |
| NEXUS-007 | In-memory mock backend with deterministic worker fixtures |
| NEXUS-012 | Resilience/retry logic (tenacity + circuit breaker) |
| NEXUS-014 | Mismatch detector: terminated in Workday but active in AD |
| NEXUS-017 | Identity shard — AD + Entra ID, 15 tools, tests passing |

### In progress

| NEXUS ID | Work item |
|---|---|
| NEXUS-008 | Workday API backend token flow and secure secret loading |
| NEXUS-009 | Workday shard live tool validation |
| NEXUS-018 | Audit shard cross-system drift reporting |

### Ready (not started)

NEXUS-001 through NEXUS-005 (Workday API credential provisioning chain), NEXUS-010, NEXUS-011, NEXUS-013, NEXUS-015, NEXUS-016, NEXUS-019 through NEXUS-030. Full backlog with priorities and dependencies in `documentation/project-standards/nexus-work-item-register.md`.

### Shard implementation vs. documentation mismatch

The README and this file have historically labeled `itsm`, `assets`, and `logistics` as "stubs." The consistency audit found all three contain fully implemented tool functions with real API query construction, mock data consumption, and lazy client initialization. They are more accurately described as "implemented but not validated against live systems." Update documentation or gate the tools behind explicit `# NOT YET VALIDATED` comment blocks.

---

## Open questions

1. **`agentic-design-intent.md` provenance.** The file at the repo root explicitly references `homelab-registry-mcp`, Traefik, Authentik, Docker, and Gitea — it is a design document from a different project. Should it be removed from this repo, or does it intentionally capture cross-project autonomy principles that apply here?

2. **`audit_minimal.py` existence.** The 2026-05-30 consistency audit references `src/shards/audit_minimal.py` as a dead shard with an empty `register()` and a module-level `AuditLog()` side effect. This file does not appear in the directory listing from the code survey and is not imported in `main.py`. [UNCLEAR] whether it has already been deleted or was missed. Confirm and remove if it still exists.

3. **Return type discipline.** Identity and Workday tools return `dict | None` instead of canonical models, though `.to_canonical()` methods are implemented in `lib/adapters.py`. Should closing this gap be tracked as a NEXUS work item? The consistency audit rates it high severity.

4. **Audit middleware registration order.** `nexus_audit_recent` and `nexus_audit_stats` are registered after the middleware loop and are never audited. Is this intentional (querying the audit log makes logging those calls potentially circular), or an oversight that should be fixed by moving the registrations before the loop?

5. **`_enabled()` duplication.** The helper is copied verbatim into at least four files (`main.py`, `list_tools.py`, `test_client.py`, `verify_mcp_protocol.py`). Should it be extracted to `lib/feature_flags.py`?

6. **Entra test coverage gap.** Nine Entra-specific tools have zero test coverage. Is this a blocking gate for NEXUS-017's "production-ready" designation, or is mock-mode coverage accepted as sufficient?

7. **Resilience decorator application.** `@resilient_http_call` is tested but not applied to any live shard HTTP call site. Should applying it to Entra and Workday clients be a standalone NEXUS work item?

8. **`USE_MOCK` config consolidation.** `os.getenv("USE_MOCK", "false")` is called directly in `lib/audit_log.py` and throughout shards, bypassing Pydantic validation. Should a `MockConfig` or `DevelopmentConfig` class be added to `lib/config.py` to consolidate this?

9. **Default `ENABLE_*` values for unvalidated shards.** `itsm`, `assets`, and `logistics` are enabled by default (`_enabled()` defaults to `"true"`). Given that their live API credentials are not provisioned, should the defaults be changed to `"false"` to avoid startup noise or failed client initialization in production deployments?
