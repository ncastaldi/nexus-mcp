---
title: "Workday to AD identity sync — next steps backlog"
description: "Granular execution checklist mapped to 2026 goal milestones and current Workday/Identity MCP artifact status."
type: "Implementation Backlog"
version: "v1"
author: "N. Castaldi"
date: "2026-04-03"
---

## Current status snapshot

- Workday artifacts define architecture, phases, and governance clearly.
- Workday implementation artifacts still indicate unresolved blockers: OAuth grant decision, owner assignment, non-prod tenant access, endpoint mappings, and field allowlist lock.
- Identity MCP appears production-capable with read-only tools and test scaffolding, which is suitable as the downstream enforcement interface for remediation orchestration.
- Missing from current docs: measurable KPI instrumentation plan, weekly drift-report automation implementation details, and a sequenced cutover plan to remove manual reconciliation.

## Priority 0: Unblockers that must be closed first

- [ ] Assign a single accountable owner for Workday auth provisioning and approve named backups.
- [ ] Finalize OAuth grant type and token lifecycle policy (token TTL, refresh behavior, secret rotation frequency).
- [ ] Provision non-production Workday tenant/API access and confirm connectivity from the MCP runtime host.
- [ ] Confirm Integration System User and security group permissions for strict read-only domains.
- [ ] Publish an approved field allowlist and explicit denylist, then version it in source control.
- [ ] Produce endpoint-to-tool mapping table: tool name, endpoint URL, required params, output shape, and error contract.

## Priority 1: Build Workday MCP to parity with Identity MCP pattern

- [ ] Scaffold project files listed in the implementation plan: server, backend contract, adapter, debug script, tests, and packaging metadata.
- [ ] Implement memory backend first and add deterministic sample worker records for contract testing.
- [ ] Implement API backend auth flow with secure secret loading from approved store (no secrets in code or logs).
- [ ] Implement tool 1 end-to-end: get worker status by authoritative identifier.
- [ ] Add schema validation to ensure responses include only allowlisted fields.
- [ ] Implement remaining core tools in sequence: worker profile, org attributes, manager, effective dates.
- [ ] Add robust adapter behavior for 401, 403, 404, 429, and 5xx responses with safe retry and timeout controls.
- [ ] Add structured STDERR logging compatible with MCP stdio transport and include invocation audit metadata.

## Priority 2: Identity correlation and mismatch detection

- [ ] Define canonical correlation key precedence (employee ID, then work email, then UPN fallback).
- [ ] Create a correlation module that compares Workday status against AD/Entra state from Identity MCP.
- [ ] Implement mismatch categories with deterministic rules:
- [ ] Terminated in Workday but enabled in AD.
- [ ] Future-dated hire in Workday but account created too early.
- [ ] Active in Workday but missing in AD.
- [ ] Manager mismatch between Workday and AD attributes.
- [ ] Contractor end date passed but access still active.
- [ ] Define severity levels and SLA targets per mismatch category.
- [ ] Add suppression logic for approved exceptions (legal hold, approved delayed start, merger-transition records).

## Priority 3: Automation workflow in Power Automate

- [ ] Create a scheduled flow for daily sync checks and a separate weekly reporting flow.
- [ ] Build connectors/actions to call Workday MCP and Identity MCP safely with service principal credentials.
- [ ] Implement idempotent processing so repeated runs do not duplicate tickets or actions.
- [ ] Add decision branches for each mismatch category and route to the correct remediation path.
- [ ] Integrate with ticketing workflow for human approval gates before identity changes execute.
- [ ] Capture full run telemetry: start/end time, processed records, mismatches found, remediations requested, remediations completed.
- [ ] Implement failure handling with retry policy, dead-letter queue pattern, and escalation notifications.

## Priority 4: Automated remediation via Identity MCP

- [ ] Confirm Phase-gate controls so any write actions stay disabled until approvals are complete.
- [ ] Define remediation action catalog mapped to mismatch categories (disable account, update manager, queue provisioning task).
- [ ] Add mandatory approval checks (ticket ID, approver identity, timestamp, change reason) before any write path.
- [ ] Build rollback procedures per remediation type and test rollback on non-production data.
- [ ] Add post-action validation checks to confirm AD/Entra state now matches Workday source-of-truth.

## Priority 5: Measurement and reporting (SMART metrics)

- [ ] Establish Q1 2026 baseline for mean-time-to-provision (MTTP) using existing onboarding tickets.
- [ ] Define MTTP formula and data source contract so measurements are reproducible.
- [ ] Implement weekly identity drift report generation with trend lines by mismatch type.
- [ ] Add dashboard metrics required for Q3 target tracking:
- [ ] MTTP reduction percentage versus Q1 baseline.
- [ ] Total mismatches detected per week.
- [ ] Percent auto-resolved versus human-resolved mismatches.
- [ ] Manual reconciliation hours eliminated.
- [ ] Publish weekly report distribution list and archival location for audit retention.

## Priority 6: Security, compliance, and operational hardening

- [ ] Run a log redaction test to verify no secrets or restricted fields are emitted.
- [ ] Perform least-privilege review across Workday ISU, MCP host identity, and Power Automate connectors.
- [ ] Add change-control requirements for schema updates and new tool introduction.
- [ ] Create a quarterly access recertification checklist for service accounts and app registrations.
- [ ] Add synthetic monitoring checks for token acquisition, endpoint latency, and tool health.
- [ ] Create incident response runbook for sync failures, auth failures, and drift-report pipeline outages.

## Priority 7: Delivery plan by quarter

- [ ] Q2 milestone 1: close all unblocking dependencies and complete non-prod end-to-end read-only validation.
- [ ] Q2 milestone 2: complete Workday MCP core tools plus correlation logic and automated mismatch classification.
- [ ] Q2 milestone 3: deploy Power Automate daily sync and ticketed approval workflow to pilot scope.
- [ ] Q3 milestone 1: enable weekly drift reporting to IT Operations with stable SLA performance.
- [ ] Q3 milestone 2: complete production rollout and retire manual reconciliation process.
- [ ] Q3 milestone 3: verify at least 30 percent MTTP reduction against Q1 baseline and document evidence.

## Immediate next 10 execution steps

- [ ] Confirm OAuth grant type in writing and record decision in implementation plan.
- [ ] Request and obtain non-prod Workday API credentials.
- [ ] Implement and test one Workday MCP tool in API mode.
- [ ] Lock response schema allowlist in tests.
- [ ] Define correlation key precedence and test with sample identity data.
- [ ] Implement first mismatch detector: terminated-in-Workday but active-in-AD.
- [ ] Stand up daily Power Automate check flow in non-production.
- [ ] Generate first weekly drift report draft and validate with IT Operations.
- [ ] Pilot one human-approved remediation path end-to-end.
- [ ] Capture baseline MTTP and publish first KPI scorecard.

## Suggested status tracking tags

- [ ] Add one tag to each backlog item: BLOCKED, READY, IN_PROGRESS, VALIDATING, DONE.
- [ ] Add owner and target date to each item before sprint planning.
- [ ] Review and update this backlog weekly until Q3 completion.
