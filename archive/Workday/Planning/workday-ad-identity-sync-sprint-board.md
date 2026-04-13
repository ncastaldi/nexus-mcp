---
title: "Workday to AD identity sync — sprint board"
description: "Sprint-ready execution board converted from the next-steps backlog."
type: "Sprint Board"
version: "v1"
author: "N. Castaldi"
date: "2026-04-03"
source: "workday-ad-identity-sync-next-steps.md"
---

## Usage

- Update Status using: BLOCKED, READY, IN_PROGRESS, VALIDATING, DONE.
- Replace placeholder owners and dates during sprint planning.
- Keep one row per deliverable-sized work item.

## Sprint board

| ID | Work item | Priority | Owner | Target date | Dependency | Definition of done | Verification | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| WIS-001 | Finalize OAuth grant type and token lifecycle policy | P0 | Unassigned | 2026-04-10 | Security + HRIS decision meeting | Decision record approved and stored in repo | Review signed decision doc and confirm policy values | READY |
| WIS-002 | Provision non-prod Workday API credentials and tenant access | P0 | Unassigned | 2026-04-12 | WIS-001 | Service account/API client active in non-prod with read-only scope | Run connectivity script and receive valid token + successful API call | READY |
| WIS-003 | Confirm ISU, security group, and domain read-only permissions | P0 | Unassigned | 2026-04-12 | WIS-002 | Approved least-privilege matrix published | Validate permissions against allowlist and denylist checklist | READY |
| WIS-004 | Publish field allowlist and explicit denylist in version control | P0 | Unassigned | 2026-04-13 | WIS-003 | Field-scope policy document merged and referenced by tests | Peer review confirms all sensitive domains excluded | READY |
| WIS-005 | Create endpoint mapping table for all five Workday tools | P0 | Unassigned | 2026-04-14 | WIS-004 | Tool-to-endpoint mapping complete with request/response/error contracts | Trace each tool to endpoint and run contract review | READY |
| WIS-006 | Scaffold Workday MCP project files to Identity parity | P1 | Unassigned | 2026-04-16 | WIS-005 | Server, backend, adapter, debug script, tests, and pyproject created | Local startup succeeds in memory mode | READY |
| WIS-007 | Implement memory backend with deterministic worker fixtures | P1 | Unassigned | 2026-04-17 | WIS-006 | Fixtures cover active, terminated, future-dated, contractor cases | Unit tests pass for fixture-driven tool outputs | READY |
| WIS-008 | Implement API backend token flow with secure secret loading | P1 | Unassigned | 2026-04-18 | WIS-006, WIS-002 | OAuth token acquisition and refresh work with no secrets in code/logs | Integration smoke test obtains token and executes read call | READY |
| WIS-009 | Implement and validate first tool: getWorkerStatus | P1 | Unassigned | 2026-04-19 | WIS-008, WIS-005 | Tool returns allowlisted fields only with stable schema | Run tool in non-prod and compare to expected schema | READY |
| WIS-010 | Add allowlist schema validation tests for all tool outputs | P1 | Unassigned | 2026-04-20 | WIS-009, WIS-004 | Automated tests fail on disallowed fields and pass on compliant output | Execute test suite and confirm gate behavior | READY |
| WIS-011 | Implement remaining tools: worker, org attributes, manager, effective dates | P1 | Unassigned | 2026-04-22 | WIS-009, WIS-010 | All five read-only tools operational in memory and API modes | Run tool-by-tool smoke checks and integration tests | READY |
| WIS-012 | Add adapter resilience for 401/403/404/429/5xx with retry/timeouts | P1 | Unassigned | 2026-04-23 | WIS-011 | Error handling and backoff logic validated by tests | Mock HTTP scenarios and verify controlled responses | READY |
| WIS-013 | Define canonical correlation key precedence across Workday and AD | P2 | Unassigned | 2026-04-24 | WIS-011 | Correlation strategy documented and approved | Validate mapping against sample records with edge cases | READY |
| WIS-014 | Implement mismatch detector: terminated in Workday but active in AD | P2 | Unassigned | 2026-04-25 | WIS-013 | Rule triggers correctly and emits actionable mismatch record | Run detector on test dataset with known outcomes | READY |
| WIS-015 | Implement mismatch detector: future-dated hire prematurely provisioned | P2 | Unassigned | 2026-04-26 | WIS-013 | Rule identifies early-provisioning violations | Validate against future-dated hire scenarios | READY |
| WIS-016 | Implement mismatch detector: active worker missing in AD | P2 | Unassigned | 2026-04-27 | WIS-013 | Missing-account cases are detected without false positives | Reconcile detector output with manually curated sample set | READY |
| WIS-017 | Implement mismatch detector: manager mismatch | P2 | Unassigned | 2026-04-28 | WIS-013 | Manager differences flagged with both source values | Compare output to Workday and AD manager fields | READY |
| WIS-018 | Implement mismatch detector: contractor past end date still active | P2 | Unassigned | 2026-04-29 | WIS-013 | Expired contractor access identified and categorized | Validate with contractor end-date test records | READY |
| WIS-019 | Build Power Automate daily sync flow (non-prod) | P3 | Unassigned | 2026-05-02 | WIS-011, WIS-014-WIS-018 | Daily flow executes MCP calls and writes run telemetry | Trigger flow manually and by schedule; verify run logs | READY |
| WIS-020 | Build Power Automate weekly drift reporting flow | P3 | Unassigned | 2026-05-03 | WIS-019 | Weekly report generated, distributed, and archived | Confirm report delivery list receives expected summary | READY |
| WIS-021 | Add idempotency controls to avoid duplicate tickets/actions | P3 | Unassigned | 2026-05-04 | WIS-019 | Duplicate processing prevented across reruns | Execute repeated test runs and confirm no duplicate artifacts | READY |
| WIS-022 | Integrate ticket approval gate before remediation execution | P4 | Unassigned | 2026-05-06 | WIS-019, WIS-021 | No remediation executes without valid approval metadata | Attempt unapproved run and confirm hard block | READY |
| WIS-023 | Define remediation action catalog mapped to mismatch types | P4 | Unassigned | 2026-05-07 | WIS-014-WIS-018 | Action matrix approved by IAM/Security and IT Ops | Review matrix and sign off in change record | READY |
| WIS-024 | Implement rollback procedures and tests for each remediation action | P4 | Unassigned | 2026-05-09 | WIS-023 | Rollback path documented and successfully tested for each action | Execute rollback drills in non-prod with evidence captured | READY |
| WIS-025 | Instrument KPI baseline for Q1 2026 MTTP | P5 | Unassigned | 2026-05-10 | Access to historical onboarding tickets | Baseline dataset and formula documented | Recompute baseline independently and match results | READY |
| WIS-026 | Implement KPI dashboard metrics and weekly trend outputs | P5 | Unassigned | 2026-05-12 | WIS-020, WIS-025 | Dashboard shows MTTP delta, drift volume, resolution mode split, hours saved | Validate dashboard calculations against raw report data | READY |
| WIS-027 | Enable production logging/redaction and operational monitoring | P6 | Unassigned | 2026-05-14 | WIS-012, WIS-026 | Request-level logs, redaction checks, and health monitors active | Run synthetic checks for auth, latency, and failure paths | READY |
| WIS-028 | Execute pilot rollout and validate SLA/severity routing | P6 | Unassigned | 2026-05-16 | WIS-022, WIS-027 | Pilot operates without policy violations and with acceptable false-positive rate | 2-week pilot report accepted by IT Operations | READY |
| WIS-029 | Production cutover and manual reconciliation retirement | P7 | Unassigned | 2026-06-15 | WIS-028 | Automated process is primary; manual reconciliation decommissioned | Confirm no manual reconciliation tasks required for 2 cycles | READY |
| WIS-030 | Q3 outcome verification and executive evidence pack | P7 | Unassigned | 2026-09-30 | WIS-029 | Evidence shows >=30% MTTP reduction and weekly drift reports running | Validate KPI package against baseline and audit records | READY |

## Notes

- Date placeholders are proposed sequencing dates and should be adjusted to active sprint cadence.
- If needed, split large items into child stories but preserve the same ID as parent epic prefix.
