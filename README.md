# Nexus-MCP status page

**Updated:** 2026-04-13

This page is the high-visibility execution status for Nexus-MCP, the sharded enterprise integration server supporting 53 tools across 9 system categories.

## Traffic-light legend

| Status | Meaning |
| --- | --- |
| 🟢 Green | Functional / production-ready |
| 🟡 Yellow | In progress / development |
| 🔴 Red | Blocked / not started |

## Nexus-MCP shard status board

Each shard is independently toggleable via feature flags. Shards load only when their `ENABLE_*` flag is set to `true` in `.env`.

| Shard | System(s) | Tools | Status | WIS Ref | Flag |
|---|---|---|---|---|---|
| `identity` | Active Directory + Entra ID | 15 | 🟢 Green | WIS-017 | `ENABLE_IDENTITY` |
| `workday` | Workday HCM | 7 | 🟢 Green | WIS-009 | `ENABLE_WORKDAY` |
| `audit` | Cross-system drift | 9 | 🟡 Yellow | WIS-014-018 | `ENABLE_AUDIT` |
| `itsm` | BMC Helix ITSM | 6 | 🔴 Red | Planned | `ENABLE_ITSM` |
| `assets` | Lansweeper + Intune | 11 | 🔴 Red | Planned | `ENABLE_ASSETS` |
| `logistics` | FedEx | 5 | 🔴 Red | Planned | `ENABLE_LOGISTICS` |

**Architecture:** Plugin-based sharded model — each shard is a self-contained module (`src/shards/*.py`) that registers its tools via a `register(mcp)` function. The orchestrator (`src/main.py`) checks feature flags and loads only enabled shards. This allows piece-at-a-time deployment without touching the core server code.

## Architecture wins

| Engineering discipline pillar | Current state | Evidence |
| --- | --- | --- |
| Atomic deployment discipline | 🟢 Green | Each shard can be deployed independently via feature flags without risk to other shards. |
| Type hinting discipline | 🟢 Green | All shards and lib/ adapters use typed return contracts per repository standards. |
| Modular architecture discipline | 🟢 Green | Orchestrator (main.py), shards (tools), lib/ (adapters) cleanly separated — no cross-contamination. |
| Mock-mode discipline | 🟢 Green | USE_MOCK flag enables full 53-tool testing without credentials (lib/mock_data.py with drift scenarios). |
| SOC 2 audit logging | 🟢 Green | Automatic JSONL audit trail with PII redaction for every tool invocation (CC7.2 / CC6.1). |
| Traceability discipline | 🟢 Green | WIS IDs embedded in tool docstrings; shard status board maps directly to roadmap. |

## Execution roadmap

| Workstream | WIS IDs | Status | Execution posture |
| --- | --- | --- | --- |
| Core shards (Identity + Workday + Audit) | WIS-006 to WIS-018 | 🟢 Green | Nexus-MCP sharded architecture operational with 31 tools in mock mode. |
| API/credentials transition | WIS-001 to WIS-008 | 🟡 Yellow | Live AD backend working; Workday API and Entra awaiting credential approval. |
| Extended shards (ITSM + Assets + Logistics) | Phase 2+ | 🔴 Red | Stub shards created; awaiting credential provisioning and client development. |
| Automation, reporting, remediation | WIS-019 to WIS-030 | 🔴 Red | Flow automation, KPI instrumentation, and cutover remain roadmap backlog. |

## Recent activity (from git history)

- Added local development quick-start and operational startup guidance.
- Added formalized README update prompt for repeatable status refreshes.
- Refined Workday runtime modular structure and validated three core tools.
- Completed type-hint quality refinements consistent with Pylance discipline.
- Added four mismatch-detection tools for status, title, department, and name variance review.
- Added focused pytest coverage for Workday mismatch scans and MCP wrappers.

## Next milestones

| Milestone | ID | Status | Exit criteria |
| --- | --- | --- | --- |
| Nexus-MCP verification | Integration | 🟡 Yellow | All mock-mode tools tested; pytest passes; Pylance zero errors; SOC 2 audit log verified |
| Live credential integration | WIS-008, WIS-001-003 | 🔴 Red | Non-prod credentials approved, Entra + Workday API backends operational |
| Extended shard activation | Phase 2 | 🔴 Red | ITSM, Assets, Logistics shards transition from Red to Yellow with stub client implementations |

## Reference documents

### Nexus-MCP core

- [Nexus-MCP comprehensive README](nexus-mcp/README.md) — full tool reference, shard architecture, and API docs
- [Local setup guide](nexus-mcp/Local-Setup.md) — installation, configuration, feature flags, and troubleshooting
- [Nexus orchestrator](nexus-mcp/src/main.py) — feature flag logic and shard loader
- [SOC 2 audit logger](nexus-mcp/lib/audit_log.py) — automatic PII redaction and JSONL event writer

### Legacy implementation (archived for reference)

- [Identity MCP server](Identity/identity_mcp_server.py) — original AD tool implementation (see identity shard)
- [Workday MCP server](Workday/workday-mcp/server.py) — original worker + drift tools (see workday + audit shards)
- [Workday execution backlog](Workday/Planning/workday-ad-identity-sync-next-steps.md)
- [Workday sprint board](Workday/Planning/workday-ad-identity-sync-sprint-board.md)
- [Workday implementation plan](Workday/Planning/workday-mcp-implementation-plan
```bash
cd nexus-mcp
python -m venv .venv
source .venv/Scripts/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -e .
cp .env.example .env

# Edit .env: set USE_MOCK=true
python src/main.py
```

See [nexus-mcp/Local-Setup.md](nexus-mcp/Local-Setup.md) for full installation guide.

### Claude Desktop configuration

```json
{
  "mcpServers": {
    "nexus": {
      "command": "python",
      "args": ["src/main.py"],
      "cwd": "/path/to/mcp_servers/nexus-mcp",
      "env": {
        "USE_MOCK": "true"
      }
    }
  }
}
```

Restart Claude Desktop to load the Nexus tool
- [Workday execution backlog](Workday/Planning/workday-ad-identity-sync-next-steps.md)
- [Workday sprint board](Workday/Planning/workday-ad-identity-sync-sprint-board.md)
- [Workday implementation plan](Workday/Planning/workday-mcp-implementation-plan.md)
- [Workday installation guide](Workday/Planning/workday-mcp-install-guide.md)
- [Workday runtime entrypoint](Workday/workday-mcp/server.py)
- [Operational startup guidance](Local%20Setup.md)
