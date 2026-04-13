# Archive — Legacy MCP Servers

This folder contains the original Identity and Workday MCP server implementations that were migrated into the unified Nexus-MCP sharded architecture on 2026-04-13.

## Archived folders

### Identity/
- **Original purpose:** Active Directory MCP server with 8 tools
- **Key files:** `identity_mcp_server.py`, `ad_adapter.py`, `identity_backend.py`
- **Status:** Superseded by `nexus-mcp/src/shards/identity.py`
- **Preserved for:** Reference implementation, PowerShell adapter patterns

### Workday/
- **Original purpose:** Workday HCM MCP server with worker lookup and drift detection
- **Key files:** `server.py`, `lib/data.py`, mismatch scan functions
- **Status:** Superseded by `nexus-mcp/src/shards/workday.py` and `nexus-mcp/src/shards/audit.py`
- **Preserved for:** Mock data structures, drift scan algorithms

### Local Setup.md
- **Original purpose:** Installation guide for the monolithic Identity server
- **Status:** Replaced by `nexus-mcp/Local-Setup.md`

## Migration summary

**Migration date:** 2026-04-13  
**Commit:** feat(nexus): implement sharded architecture  
**Session snapshot:** [documentation/project-history/SESSION_SNAPSHOT_2026-04-13.md](../documentation/project-history/SESSION_SNAPSHOT_2026-04-13.md)

**What was migrated:**
- 8 Identity tools → `nexus-mcp/src/shards/identity.py` (15 tools including Entra)
- 3 Workday worker tools → `nexus-mcp/src/shards/workday.py`
- 5 drift detection tools → `nexus-mcp/src/shards/audit.py`
- AD PowerShell adapter → `nexus-mcp/lib/ad_adapter.py`
- Mock data → `nexus-mcp/lib/mock_data.py`
- Test suites → `nexus-mcp/tests/identity_tests/` and `nexus-mcp/tests/workday_tests/`

## Active server

**Current primary:** [nexus-mcp/](../nexus-mcp/)

For installation, configuration, and usage, see:
- [nexus-mcp/README.md](../nexus-mcp/README.md) — full tool reference
- [nexus-mcp/Local-Setup.md](../nexus-mcp/Local-Setup.md) — installation guide
- [README.md](../README.md) — repository status page

---

**Note:** These folders are preserved for reference and historical context. Do not use them for new development. All active work should occur in `nexus-mcp/`.
