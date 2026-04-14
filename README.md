# Nexus-MCP — Enterprise Integration Server

Sharded Model Context Protocol server for enterprise systems.
Each shard is self-contained and can be toggled independently via feature flags.

---

<!-- STATUS_PAGE:BEGIN -->
## Status Page (Managed)

| Field | Value |
|---|---|
| Last Updated | 2026-04-13 |
| Latest Session Snapshot | SESSION_SNAPSHOT_2026-04-13.md |
| Change Signal | No staged files |
| Components Affected | none |
| TODO/RESTART Markers | none |
| BREAKING CHANGE (compose ports/volumes) | No |

## Shard Status Board (Traffic Light)

| Shard | System(s) | Status | NEXUS Ref | Flag | Standard Gate |
|---|---|---|---|---|---|
| identity | Active Directory + Entra ID | 🟢 Green | NEXUS-017 | ENABLE_IDENTITY | Tool tests passing |
| workday | Workday HCM | 🟡 Yellow | NEXUS-009 | ENABLE_WORKDAY | Credentials + live validation pending |
| audit | Cross-system drift + reporting | 🟡 Yellow | NEXUS-018 | ENABLE_AUDIT | Verification maturing |
| itsm | BMC Helix ITSM | 🔴 Red | NEXUS-021 | ENABLE_ITSM | Stub only |
| assets | Lansweeper + Intune | 🔴 Red | NEXUS-022 | ENABLE_ASSETS | Stub only |
| logistics | FedEx | 🔴 Red | NEXUS-023 | ENABLE_LOGISTICS | Stub only |

## Discipline Drives Quality

| Pillar | Target Standard | Current Signal |
|---|---|---|
| Type Hinting | Public interfaces typed | 🟢 Pydantic-based schemas in place |
| Pylance | Zero-error baseline | 🟡 Enforced goal, pending full workspace sweep |
| Modular Structure | Orchestrator -> shards -> adapters | 🟢 Applied in current architecture |
| Test Gates | Pre-push tests + validation | 🟢 Active local gate |
| Security Logging | SOC 2 audit trail with redaction | 🟢 Active |

## Sprint Traceability (2026)

| NEXUS ID | Area | Status |
|---|---|---|
| NEXUS-009 | Workday integration | 🟡 In progress |
| NEXUS-017 | Identity integration | 🟢 Production-ready |
| NEXUS-018 | Audit capability | 🟡 In progress |
| NEXUS-021 | ITSM shard | 🔴 Planned |
| NEXUS-022 | Assets shard | 🔴 Planned |
| NEXUS-023 | Logistics shard | 🔴 Planned |
<!-- STATUS_PAGE:END -->

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

## Claude Desktop config

```json
{
  "mcpServers": {
    "nexus": {
      "command": "python",
      "args": ["src/main.py"],
      "cwd": "/path/to/nexus-mcp"
    }
  }
}
```

---

## Required permissions

See [DEMO_GUIDE.md](DEMO_GUIDE.md) for the full permission matrix, credential configuration, and live-mode setup.
All credentials live in `nexus-mcp/.env` — no need to put them in the Claude config.
