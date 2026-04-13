# Nexus-MCP — Enterprise Integration Server

Sharded Model Context Protocol server for enterprise systems.
Each shard is self-contained and can be toggled independently via feature flags.

---

## Shard Status Board

| Shard | System(s) | Status | WIS Ref | Flag | Notes |
|---|---|---|---|---|---|
| `identity` | Active Directory + Entra ID | 🟢 **Green** | WIS-017 | `ENABLE_IDENTITY` | **15 tools** — Production-ready |
| `workday` | Workday HCM | 🟡 **Yellow** | WIS-009 | `ENABLE_WORKDAY` | **7 tools** — Functional; API credentials pending |
| `audit` | Cross-system drift + reporting | 🟡 **Yellow** | — | `ENABLE_AUDIT` | **11 tools** — Async execution enabled; verification in progress |
| `itsm` | BMC Helix ITSM | 🔴 **Red** | Planned | `ENABLE_ITSM` | Stub only — credentials not configured |
| `assets` | Lansweeper + Intune | 🔴 **Red** | Planned | `ENABLE_ASSETS` | Stub only — credentials not configured |
| `logistics` | FedEx | 🔴 **Red** | Planned | `ENABLE_LOGISTICS` | Stub only — credentials not configured |

**Total Registered Tools:** 33 (15 Identity + 7 Workday + 11 Audit)  
**Last Updated:** 2026-04-13 (Session: Audit shard async execution)

---

## Project Health: "Discipline Drives Quality"

| Pillar | Status | Evidence |
|---|---|---|
| **Type Safety** | 🟢 | Pydantic models for all cross-system schemas |
| **Error Handling** | 🟢 | Enterprise resilience layer with graceful degradation |
| **Configuration** | 🟢 | `pydantic-settings` validation + feature flag control |
| **Audit Compliance** | 🟢 | SOC 2 logging (CC7.2/CC6.1) with PII redaction |
| **Test Coverage** | 🟡 | Pytest suites migrated; live API validation pending |
| **Mock Support** | 🟢 | Full mock mode via `USE_MOCK=true` for all shards |

---

## Folder Structure

```
nexus-mcp/
├── src/
│   ├── main.py              # Core Orchestrator — reads flags, loads shards
│   └── shards/              # The 6 Shards (one file = one system domain)
│       ├── __init__.py
│       ├── identity.py      # 🟢 AD & Entra tools
│       ├── workday.py       # 🟡 Worker & Org tools
│       ├── itsm.py          # 🔴 BMC Helix tools
│       ├── assets.py        # 🔴 Lansweeper + Intune tools
│       ├── logistics.py     # 🔴 FedEx tools
│       └── audit.py         # 🟡 Cross-system drift + reporting
├── lib/                     # Low-level system adapters (no tool logic here)
│   ├── config.py
│   ├── ad_adapter.py        # LDAP/AD connection wrapper
│   ├── entra_client.py      # Microsoft Graph (Entra)
│   ├── workday_client.py    # Workday REST + OAuth2
│   ├── helix_client.py      # BMC Helix AR-JWT auth
│   ├── lansweeper_client.py # Lansweeper GraphQL
│   ├── intune_client.py     # Microsoft Graph (Intune)
│   └── fedex_client.py      # FedEx REST + OAuth2
├── tests/
├── .env                     # Feature flags + credentials
├── .env.example             # Template — copy this to .env
└── README.md
```

---

## Architecture: The Shard Contract

Every shard file exposes exactly one function:

```python
def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def my_tool(...) -> ...:
        """Tool docstring visible to the LLM."""
        ...
```

The orchestrator (`src/main.py`) reads feature flags and calls `register(mcp)` for each enabled shard. **No other file is changed to add or remove a shard.**

### Adding a new shard

1. Create `src/shards/my_system.py` following the template above.
2. Add the adapter to `lib/` if needed.
3. Add one line to `src/main.py`:
   ```python
   from shards import my_system
   if _enabled("MY_SYSTEM"):
       my_system.register(mcp)
   ```
4. Add `ENABLE_MY_SYSTEM=true` to `.env`.

### Holding pattern

Leave a shard unregistered (or set flag to `false`) to hold it without breaking anything:

```python
# 🔴 Planned — credentials not yet available
# if _enabled("MY_SYSTEM"):
#     my_system.register(mcp)
```

---

## Tools Reference

### Identity shard (🟢)
| Tool | Description |
|---|---|
| `ad_get_user` | Look up AD user by sAMAccountName |
| `ad_get_user_by_email` | Look up AD user by email |
| `ad_search_users` | Search AD by display name fragment |
| `ad_list_groups` | List all AD groups |
| `ad_get_group_members` | Members of a group by DN |
| `ad_get_disabled_accounts` | All disabled AD accounts |
| `ad_get_stale_accounts` | Accounts inactive beyond N days |
| `entra_list_users` | List Entra ID users |
| `entra_get_user` | Get user by ID or UPN |
| `entra_list_groups` | List Entra groups |
| `entra_get_group_members` | Members of an Entra group |
| `entra_list_service_principals` | List app registrations |
| `entra_get_conditional_access_policies` | List CA policies |
| `entra_get_signin_logs` | Recent sign-in logs |
| `entra_get_risky_users` | Identity Protection risky users |

### Workday shard (🟡)
| Tool | Description |
|---|---|
| `workday_list_workers` | Paginated worker list |
| `workday_get_worker` | Worker by Workday ID |
| `workday_find_worker_by_email` | Worker lookup by email |
| `workday_list_positions` | Open and filled positions |
| `workday_get_compensation` | Compensation details |
| `workday_list_organizations` | Supervisory orgs |
| `workday_run_raas_report` | Execute a RaaS custom report |

### ITSM shard (🔴)
| Tool | Description |
|---|---|
| `helix_list_incidents` | Incidents (filterable by status/assignee) |
| `helix_get_incident` | Incident by Entry ID |
| `helix_list_changes` | Change requests |
| `helix_get_problem` | Problem investigation ticket |
| `helix_search_cmdb` | CMDB CI search by name |
| `helix_list_cmdb_assets` | Hardware assets from CMDB |

### Assets shard (🔴)
| Tool | Description |
|---|---|
| `lansweeper_list_assets` | Asset list (filterable by type) |
| `lansweeper_get_asset` | Asset by ID |
| `lansweeper_get_software` | Installed software on asset |
| `lansweeper_search_assets` | Search by name/IP/serial |
| `intune_list_managed_devices` | Managed device inventory |
| `intune_get_managed_device` | Device by ID |
| `intune_get_noncompliant_devices` | Non-compliant devices |
| `intune_list_compliance_policies` | Compliance policies |
| `intune_list_configuration_profiles` | Config profiles |
| `intune_list_apps` | Deployed app list |
| `intune_get_autopilot_devices` | Autopilot registrations |

### Logistics shard (🔴)
| Tool | Description |
|---|---|
| `fedex_track_shipment` | Track by tracking number |
| `fedex_track_multiple` | Track up to 30 at once |
| `fedex_get_shipment_events` | Scan event history |
| `fedex_validate_address` | Address validation |
| `fedex_get_rates` | Rate quote between postal codes |

### Audit shard (🟡)
| Tool | Description | Execution |
|---|---|---|
| `audit_user_drift` | Single user across Workday / AD / Entra | Async |
| `audit_bulk_user_drift` | Up to 50 users concurrently | Async |
| `audit_device_drift` | Single device across Lansweeper / Intune / Helix | Async |
| `audit_entra_ad_sync_drift` | Full Entra→AD sync scan | Async |
| `audit_intune_lansweeper_device_drift` | Intune vs Lansweeper reconciliation | Async |
| `generate_weekly_report` | Full weekly cross-system report | Async |
| `generate_compliance_report` | Device + identity risk snapshot | Async |
| `generate_asset_reconciliation_report` | Intune vs Lansweeper diff | Async |
| `generate_itsm_weekly_summary` | Helix ticket volume summary | Async |
| `nexus_audit_recent` | Query recent audit events (last N days) | Sync |
| `nexus_audit_stats` | Aggregate statistics on audit activity | Sync |

**Recent Improvements (2026-04-13):**
- ✅ Async execution for all drift detection scans
- ✅ MCP protocol verification script (`verify_mcp_protocol.py`)
- ✅ Resilience layer with retry logic and graceful degradation

---

## Setup

```bash
cd nexus-mcp
cp .env.example .env        # fill in credentials and set feature flags
pip install -e .
python src/main.py          # or: nexus-mcp
```

## Claude Desktop Config

```json
{
  "mcpServers": {
    "nexus": {
      "command": "python",
      "args": ["src/main.py"],
      "cwd": "/path/to/nexus-mcp"
    }
  }
}Sprint Status & Next Steps

### ✅ Recently Completed (2026-04-13)
- Async audit execution for high-volume scans
- Enterprise resilience framework (retry logic, circuit breakers)
- Pydantic schema standardization for cross-system data
- Code health report with actionable improvements

### 🟡 In Progress
- **Pytest validation** of all 33 tools against live APIs
- **Workday API credential approval** (WIS-009)
- **Claude Desktop integration testing** with updated config

### 🔴 Blocked / Pending Approval
- **ITSM shard (BMC Helix):** AR-JWT credentials pending
- **Assets shard (Lansweeper + Intune):** GraphQL + Graph API setup
- **Logistics shard (FedEx):** OAuth2 client registration

---

## Required Permissions

See [Local-Setup.md](Local-Setup.md) for the full permission matrix and credential configuration guide
All credentials can live in `nexus-mcp/.env` — no need to put them in the Claude config.

---

## Required Permissions

See `mcp-server/README.md` for the full permission matrix for each system.
The same requirements apply here — Nexus-MCP is a refactor of that server,
not a new system.
