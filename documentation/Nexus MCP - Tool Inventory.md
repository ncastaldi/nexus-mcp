# Nexus MCP - Tool inventory

A complete reference of every service and tool currently registered in the Nexus MCP server. Sorted alphabetically by service, then by tool name within each service.

---

## Active Directory

**Shard:** `identity` | **Status:** 🟢 Green (WIS-017)

| Tool | Description |
|---|---|
| `ad_get_disabled_accounts` | Returns all disabled user accounts in Active Directory (userAccountControl = 514). |
| `ad_get_group_members` | Returns all members of an AD group by its distinguished name (DN). |
| `ad_get_stale_accounts` | Returns active AD accounts with no recorded login activity within a configurable number of days (default: 90). |
| `ad_get_user` | Looks up a single AD user by their sAMAccountName (login name) and returns a normalized user object. |
| `ad_get_user_by_email` | Looks up a single AD user by their email address and returns a normalized user object. |
| `ad_list_groups` | Lists all security and distribution groups in Active Directory. |
| `ad_search_users` | Searches AD users by display name or sAMAccountName fragment and returns a list of normalized user objects. |

---

## Audit (cross-system)

**Shard:** `audit` + `main.py` | **Status:** 🟢 Green

| Tool | Description |
|---|---|
| `nexus_audit_recent` | Returns the last *n* entries from the Nexus-MCP SOC 2 structured audit log. Each entry includes tool name, shard, action category, redacted argument summary, status, and latency. |
| `nexus_audit_stats` | Returns aggregate statistics over the entire audit log, including total call count, status breakdown, shard breakdown, top-10 tools by call volume, and recent errors. |
| `scan_department_mismatches` | Detects workers whose department in Workday differs from their department attribute in Active Directory. Severity: MEDIUM. |
| `scan_job_title_drift` | Detects workers whose job title in Workday differs from their title attribute in Active Directory. Severity: MEDIUM. |
| `scan_name_variance_mismatches` | Detects AD display names that do not align with the legal or preferred name stored in Workday. Severity: LOW. |
| `scan_status_reconciliation` | Detects workers who are terminated in Workday but still have an enabled account in Active Directory. Severity: HIGH. |

---

## BMC Helix (ITSM)

**Shard:** `itsm` | **Status:** 🔴 Red (Planned)

| Tool | Description |
|---|---|
| `helix_get_incident` | Retrieves full details for a single Helix incident ticket by its Entry ID (e.g. `INC0001234`). |
| `helix_get_problem` | Retrieves a Helix problem investigation record by its problem ID (e.g. `PRB0000456`). |
| `helix_list_changes` | Lists change requests from BMC Helix with optional status filter (e.g. Draft, Scheduled, In Progress). |
| `helix_list_cmdb_assets` | Lists hardware assets registered in the BMC Helix CMDB. |
| `helix_list_incidents` | Lists incidents from BMC Helix ITSM with optional filters for status and assignee. |
| `helix_search_cmdb` | Searches the BMC Helix CMDB for configuration items (CIs) matching a name fragment. |

---

## FedEx

**Shard:** `logistics` | **Status:** 🔴 Red (Planned — credentials pending)

| Tool | Description |
|---|---|
| `fedex_get_rates` | Returns available FedEx shipping service options and rates between two postal codes for a given package weight. |
| `fedex_get_shipment_events` | Returns the full ordered list of scan events (location, timestamp, description) for a single FedEx tracking number. |
| `fedex_track_multiple` | Tracks up to 30 FedEx shipments in a single API call and returns tracking results for each. |
| `fedex_track_shipment` | Tracks a single FedEx shipment by tracking number and returns full tracking details including current status and estimated delivery. |
| `fedex_validate_address` | Validates a shipping address against the FedEx Address Validation API and returns the classification and resolved address. |

---

## Microsoft Entra ID

**Shard:** `identity` | **Status:** 🟢 Green (WIS-017)

| Tool | Description |
|---|---|
| `entra_get_conditional_access_policies` | Lists all Conditional Access policies configured in the Entra ID tenant. |
| `entra_get_group_members` | Lists members of an Entra ID group by its object ID. |
| `entra_get_risky_users` | Lists users currently flagged as risky by Entra ID Identity Protection. Requires `IdentityRiskyUser.Read.All` Graph permission. |
| `entra_get_signin_logs` | Retrieves recent sign-in log entries from Entra ID, ordered by most recent. Requires `AuditLog.Read.All` Graph permission. |
| `entra_get_user` | Retrieves a single Entra ID user by object ID or UPN and returns a normalized user object. |
| `entra_list_groups` | Lists all groups in the Microsoft Entra ID tenant. |
| `entra_list_service_principals` | Lists service principals (app registrations and enterprise applications) registered in Entra ID. |
| `entra_list_users` | Lists users in Microsoft Entra ID and returns normalized user objects. |

---

## Microsoft Intune

**Shard:** `assets` | **Status:** 🔴 Red (Planned)

| Tool | Description |
|---|---|
| `intune_get_autopilot_devices` | Lists all Windows Autopilot device registrations in Intune. |
| `intune_get_managed_device` | Retrieves full details for a single Intune managed device by its device ID or device name. |
| `intune_get_noncompliant_devices` | Returns all Intune-managed devices currently in a non-compliant state. |
| `intune_list_apps` | Lists managed applications deployed through Intune mobile app management. |
| `intune_list_compliance_policies` | Lists the device compliance policies configured in Intune. |
| `intune_list_configuration_profiles` | Lists the device configuration profiles configured in Intune. |
| `intune_list_managed_devices` | Lists all devices enrolled in Microsoft Intune with key health and compliance attributes. |

---

## Lansweeper

**Shard:** `assets` | **Status:** 🔴 Red (Planned)

| Tool | Description |
|---|---|
| `lansweeper_get_asset` | Retrieves full inventory details for a single Lansweeper asset by its asset ID. |
| `lansweeper_get_software` | Lists all installed software (name, version, publisher) on a given Lansweeper asset. |
| `lansweeper_list_assets` | Lists assets from Lansweeper with optional filtering by asset type (e.g. Windows, Linux, Network Device). |
| `lansweeper_search_assets` | Searches Lansweeper assets by name, IP address, or serial number fragment and returns matching records. |

---

## Workday

**Shard:** `workday` | **Status:** 🟡 Yellow (WIS-009)

| Tool | Description |
|---|---|
| `workday_find_worker_by_email` | Finds a Workday worker record by their primary work email address. |
| `workday_get_compensation` | Retrieves compensation details (grade, salary band) for a worker by their Workday ID. |
| `workday_get_worker` | Retrieves full details for a single Workday worker by their Workday worker ID. |
| `workday_list_organizations` | Lists supervisory organisations in the Workday tenant. |
| `workday_list_positions` | Lists open and filled positions in Workday HCM. |
| `workday_list_workers` | Lists workers from Workday HCM with support for pagination via `limit` and `offset`. |
| `workday_run_raas_report` | Executes a Workday Report-as-a-Service (RaaS) custom report by path and returns the result rows. |

---

## Summary

| Service | Shard | Status | Tool count |
|---|---|---|---|
| Active Directory | `identity` | 🟢 Green | 7 |
| Audit (cross-system) | `audit` / `main.py` | 🟢 Green | 6 |
| BMC Helix (ITSM) | `itsm` | 🔴 Planned | 6 |
| FedEx | `logistics` | 🔴 Planned | 5 |
| Microsoft Entra ID | `identity` | 🟢 Green | 8 |
| Microsoft Intune | `assets` | 🔴 Planned | 7 |
| Lansweeper | `assets` | 🔴 Planned | 4 |
| Workday | `workday` | 🟡 In progress | 7 |
| **Total** | | | **50** |

---

*Generated: 2026-04-14 | Source: `nexus-mcp/src/shards/` + `nexus-mcp/src/main.py`*
