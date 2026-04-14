# Nexus work item register

Canonical registry for all NEXUS-XXX work items. This supersedes the original `WIS-XXX` numbering used during the Workday-AD Identity Sync planning phase.

**ID format:** `NEXUS-NNN` (zero-padded to 3 digits)
**Source of truth:** This file. All other documents should reference NEXUS-XXX IDs.
**Legacy mapping:** Original IDs were `WIS-NNN` (same numbers, renamed for project scope clarity).

---

## Shard assignments (current)

These NEXUS IDs are actively used as shard tracking references in `nexus-mcp/README.md`:

| NEXUS ID | Shard | System(s) | Status |
|---|---|---|---|
| NEXUS-009 | `workday` | Workday HCM | 🟡 In progress |
| NEXUS-017 | `identity` | Active Directory + Entra ID | 🟢 Production-ready |
| NEXUS-018 | `audit` | Cross-system drift + reporting | 🟡 In progress |
| NEXUS-021 | `itsm` | BMC Helix ITSM | 🔴 Planned |
| NEXUS-022 | `assets` | Lansweeper + Intune | 🔴 Planned |
| NEXUS-023 | `logistics` | FedEx | 🔴 Planned |

---

## Full work item backlog

Derived from `archive/Workday/Planning/workday-ad-identity-sync-sprint-board.md` (v1, 2026-04-03).
Original scope was Workday-AD identity sync; items have since been absorbed into the broader Nexus-MCP roadmap.

| NEXUS ID | Priority | Work item | Dependency | Status |
|---|---|---|---|---|
| NEXUS-001 | P0 | Finalize OAuth grant type and token lifecycle policy | — | READY |
| NEXUS-002 | P0 | Provision non-prod Workday API credentials and tenant access | NEXUS-001 | READY |
| NEXUS-003 | P0 | Confirm ISU, security group, and domain read-only permissions | NEXUS-002 | READY |
| NEXUS-004 | P0 | Publish field allowlist and explicit denylist in version control | NEXUS-003 | READY |
| NEXUS-005 | P0 | Create endpoint mapping table for all Workday tools | NEXUS-004 | READY |
| NEXUS-006 | P1 | Scaffold Workday MCP project files to Identity parity | NEXUS-005 | DONE |
| NEXUS-007 | P1 | Implement memory backend with deterministic worker fixtures | NEXUS-006 | DONE |
| NEXUS-008 | P1 | Implement API backend token flow with secure secret loading | NEXUS-006, NEXUS-002 | IN_PROGRESS |
| NEXUS-009 | P1 | Implement and validate Workday shard tools | NEXUS-008, NEXUS-005 | IN_PROGRESS |
| NEXUS-010 | P1 | Add allowlist schema validation tests for all tool outputs | NEXUS-009, NEXUS-004 | READY |
| NEXUS-011 | P1 | Implement remaining Workday tools (worker, org, manager, effective dates) | NEXUS-009, NEXUS-010 | READY |
| NEXUS-012 | P1 | Add adapter resilience for 401/403/404/429/5xx with retry/timeouts | NEXUS-011 | DONE |
| NEXUS-013 | P2 | Define canonical correlation key precedence across Workday and AD | NEXUS-011 | READY |
| NEXUS-014 | P2 | Implement mismatch detector: terminated in Workday but active in AD | NEXUS-013 | DONE |
| NEXUS-015 | P2 | Implement mismatch detector: future-dated hire prematurely provisioned | NEXUS-013 | READY |
| NEXUS-016 | P2 | Implement mismatch detector: active worker missing in AD | NEXUS-013 | READY |
| NEXUS-017 | P2 | Identity shard: AD + Entra tools production-ready | NEXUS-013 | DONE |
| NEXUS-018 | P2 | Audit shard: cross-system drift detection and reporting | NEXUS-013 | IN_PROGRESS |
| NEXUS-019 | P3 | Build Power Automate daily sync flow (non-prod) | NEXUS-011, NEXUS-014–018 | READY |
| NEXUS-020 | P3 | Build Power Automate weekly drift reporting flow | NEXUS-019 | READY |
| NEXUS-021 | P3 | ITSM shard: BMC Helix incidents, changes, problems, CMDB | NEXUS-019, NEXUS-021 | READY |
| NEXUS-022 | P4 | Assets shard: Lansweeper + Intune device inventory | NEXUS-019, NEXUS-021 | READY |
| NEXUS-023 | P4 | Logistics shard: FedEx shipment tracking and address validation | NEXUS-014–018 | READY |
| NEXUS-024 | P4 | Implement rollback procedures and tests for each remediation action | NEXUS-023 | READY |
| NEXUS-025 | P5 | Instrument KPI baseline for Q1 2026 MTTP | Historical ticket access | READY |
| NEXUS-026 | P5 | Implement KPI dashboard metrics and weekly trend outputs | NEXUS-020, NEXUS-025 | READY |
| NEXUS-027 | P6 | Enable production logging/redaction and operational monitoring | NEXUS-012, NEXUS-026 | READY |
| NEXUS-028 | P6 | Execute pilot rollout and validate SLA/severity routing | NEXUS-022, NEXUS-027 | READY |
| NEXUS-029 | P7 | Production cutover and manual reconciliation retirement | NEXUS-028 | READY |
| NEXUS-030 | P7 | Q3 outcome verification and executive evidence pack | NEXUS-029 | READY |

---

## Status key

| Value | Meaning |
|---|---|
| `READY` | Not started; all dependencies met or waived |
| `IN_PROGRESS` | Actively being worked |
| `VALIDATING` | Implementation complete; under test/review |
| `BLOCKED` | Waiting on an external dependency |
| `DONE` | Accepted and closed |

---

## Change log

| Date | Change |
|---|---|
| 2026-04-14 | Register created; WIS-XXX IDs retired in favour of NEXUS-XXX |
| 2026-04-03 | Original sprint board authored (`workday-ad-identity-sync-sprint-board.md`) |
