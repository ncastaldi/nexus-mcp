# nexus-mcp

Self-hosted MCP server that bridges enterprise systems (Active Directory, Entra ID, Workday, BMC Helix ITSM, Lansweeper, Intune, FedEx) with LLM-based agents via the Model Context Protocol. Normalizes data into canonical schemas, detects cross-system inconsistencies, and logs every tool call for SOC 2 compliance.

## Repository Layout

```
nexus-mcp/          # Main Python package
  src/
    main.py         # Orchestrator: loads enabled shards, applies audit middleware
    shards/         # One module per integration domain
      identity.py   # AD + Entra ID (15 tools) — live
      workday.py    # Workday HCM (12 tools) — integration in progress
      audit.py      # Cross-system drift scanning (6 tools) — live
      itsm.py       # BMC Helix ITSM — stub
      assets.py     # Lansweeper + Intune — stub
      logistics.py  # FedEx — stub
  lib/
    config.py       # Pydantic BaseSettings for all system credentials
    schemas.py      # Canonical data models (CanonicalUser, Device, Incident, …)
    adapters.py     # System API response → canonical schema transforms
    ad_adapter.py   # Production LDAP/Active Directory backend
    audit_log.py    # SOC 2 JSONL logger (append-only, auto-redacts secrets)
    drift_detection.py  # Cross-system mismatch scanning logic
    mock_data.py    # Synthetic test data with pre-seeded drift scenarios
    resilience.py   # Retry/timeout/circuit-breaker patterns
    *_client.py     # REST/GraphQL clients (Entra, Workday, Helix, Lansweeper, Intune, FedEx)
  tests/
    identity_tests/ # AD/Entra unit + integration tests
    workday_tests/  # Workday drift detection tests
    test_resilience.py
  .env.example      # All config keys with comments
  pyproject.toml    # Package config, entry point, test markers
  list_tools.py     # Browse all registered MCP tools
  verify_mcp_protocol.py  # Validate MCP compatibility
documentation/
scripts/
.github/
  agents/           # AI assistant instructions (Frank v6, Data Analyst, …)
  prompts/          # 30+ workflow automation prompts
```

## Setup

```bash
cd nexus-mcp
python -m venv .venv
source .venv/bin/activate       # Windows: .\.venv\Scripts\Activate.ps1
pip install -e .

cp .env.example .env
```

Edit `.env` before starting. The key flags:

| Variable | Purpose |
|---|---|
| `USE_MOCK=true` | Run all tools on synthetic data — no credentials needed |
| `ENABLE_IDENTITY=true` | Load the identity shard (AD + Entra) |
| `ENABLE_WORKDAY=true` | Load the Workday shard |
| `ENABLE_AUDIT=true` | Load the audit/drift shard |
| `ENABLE_ITSM/ASSETS/LOGISTICS` | Load stub shards |
| `AUDIT_LOGGING_ENABLED=true` | Write SOC 2 audit log to `logs/nexus_audit.jsonl` |

For live mode, fill in the system-specific credential sections (AD, Entra, Workday, etc.) in `.env`.

## Running

```bash
# From nexus-mcp/ directory
python -m main
# or after pip install -e .
nexus-mcp
```

Communicates via stdio (MCP protocol). Connect via any MCP-compatible client (Claude Desktop, VS Code extension, etc.). See `documentation/VSCODE_INTEGRATION_GUIDE.md` for IDE setup.

## Testing

```bash
# All unit tests (integration tests skipped by default)
pytest

# Skip integration tests explicitly
pytest -m "not integration"

# With coverage
pytest --cov=src --cov=lib

# Single file
pytest tests/identity_tests/test_ad_adapter.py

# Browse all registered tools
python list_tools.py

# Verify MCP protocol compliance
python verify_mcp_protocol.py

# Watch audit log
tail -f logs/nexus_audit.jsonl
```

Mock mode (`USE_MOCK=true`) is the fastest way to exercise all tools — no external systems required. `lib/mock_data.py` has pre-seeded drift scenarios for realistic testing.

## Architecture

### Shard Pattern

Every shard exports a single `register(mcp: FastMCP) -> None` function. `main.py` reads feature flags and calls `register()` for each enabled shard. No other file changes when adding or removing a shard.

```python
# Minimal shard skeleton
def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def my_tool(arg: str) -> dict:
        """Tool description visible to the LLM."""
        ...
```

### Canonical Schemas

All system adapters transform native API responses into Pydantic models defined in `lib/schemas.py`:
- `CanonicalUser` — normalized across AD, Entra ID, Workday
- `CanonicalDevice` — normalized across Intune, Lansweeper, Helix
- `CanonicalIncident`, `CanonicalShipment`, `FieldDrift` — other domains

Use canonical types as return values; never pass raw dicts between layers.

### SOC 2 Audit Middleware

Applied in `main.py` after all shards load — wraps every tool automatically. Each call records `event_id`, `timestamp`, `tool`, `shard`, `action_category`, `args_summary` (secrets redacted), `mock_mode`, `status`, and `latency_ms` to `logs/nexus_audit.jsonl`.

## Shard Status

| Shard | Systems | Status | Notes |
|---|---|---|---|
| `identity` | AD + Entra ID | Live | 15 tools; tests passing |
| `workday` | Workday HCM | In progress | 12 tools; credentials + validation pending |
| `audit` | Cross-system drift | Live | 4 scan tools + 2 audit log query tools |
| `itsm` | BMC Helix ITSM | Stub | 6 tools planned |
| `assets` | Lansweeper + Intune | Stub | 13 tools planned |
| `logistics` | FedEx | Stub | 5 tools planned |

## Branching

- `main` — stable; changes via PR only
- `feat/`, `project/`, `chore/` — short-lived feature branches
- Rebase is intentional, not automated
- See `CONTRIBUTING.md` for full workflow
