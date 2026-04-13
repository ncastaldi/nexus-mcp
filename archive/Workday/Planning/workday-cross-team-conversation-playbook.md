---
title: "Workday to AD sync — cross-team conversation playbook"
description: "Detailed prep and conversation guide for closing Workday access, security, connectivity, and compliance prerequisites."
type: "Execution Playbook"
version: "v1"
author: "N. Castaldi"
date: "2026-04-03"
status: "DRAFT"
---

## Purpose

Use this playbook to run focused conversations with each stakeholder group so prerequisites are closed quickly and in the right sequence.

## Core outcomes to close

- Confirm the right Workday data fields we are approved to use.
- Provision non-prod API access and integration credentials.
- Approve auth/token and least-privilege scope.
- Confirm secrets handling and runtime connectivity path.
- Validate privacy/compliance guardrails on allowed vs restricted attributes.

## Recommended sequence

1. HRIS/Workday owner (field and business-rule alignment)
2. Workday integration admin (API enablement and credentials)
3. Security/IAM (auth and access approval)
4. Platform/IT operations (secrets and runtime path)
5. Compliance/privacy (data handling validation)

## Global prep package (have ready before any meeting)

- Project one-liner: what problem is being solved and expected operational value.
- Scope boundaries: read-only non-prod pilot first; no write/remediation in initial phase.
- High-level workflow: Workday source data -> MCP read tools -> mismatch reporting.
- Target timeline: requested decision date and target pilot start date.
- Draft field list: requested attributes and intended usage for each.
- Architecture summary: where code runs, how credentials are stored, who can access logs.
- Risk controls summary: least privilege, redaction, audit logging, approval gates.
- Decision log template: owner, decision, date, follow-up tasks.

## Team-by-team conversation guide

## HRIS / Workday functional owner

### Objective

Confirm business semantics and approved fields so downstream technical setup is based on correct policy and definitions.

### You need to have ready

- Draft list of required worker attributes and why each is needed.
- Proposed source-of-truth assumptions (status, manager, effective dates).
- Examples of mismatch scenarios the process needs to detect.
- Definition of out-of-scope fields for phase 1.

### You need to ask them

- Which exact fields are approved for this use case?
- Which fields are restricted or require additional approvals?
- What are the authoritative business rules for worker status transitions?
- Are there known edge cases (contractors, leaves, future hires) we must handle?
- Who is final approver for field-level usage decisions?

### Expected outputs

- Approved field allowlist.
- Explicit denylist/restricted-field list.
- Confirmed business-rule references and data definitions.
- Named functional approver.

## Workday integration administrator

### Objective

Enable non-prod API connectivity and provide integration credentials aligned to approved field scope.

### You need to have ready

- Approved field allowlist from HRIS discussion.
- Required endpoint list mapped to planned tools.
- Environment details for where integration will run.
- Requested timeline for first non-prod connectivity test.

### You need to ask them

- Which non-prod endpoint base URLs should be used?
- What auth mechanism is supported for this integration pattern?
- What integration client/account needs to be created?
- What scopes/permissions are required to support approved fields only?
- What are token TTL, refresh behavior, rate limits, and expected error patterns?
- Who owns credential rotation and break-glass procedures?

### Expected outputs

- Non-prod API endpoint details.
- Integration account/client provisioned.
- Initial credentials or secure retrieval path.
- API constraints documented (timeouts, throttling, limits).

## Security / IAM

### Objective

Approve authentication model, token lifecycle, and least-privilege access boundaries before runtime connection is enabled.

### You need to have ready

- Proposed auth flow and token lifecycle design.
- Requested scopes and rationale tied to allowlisted fields.
- Role and access matrix (who can access secrets/logs/runtime).
- Incident handling approach for auth failures.

### You need to ask them

- Does the proposed auth/token approach meet policy?
- Are requested scopes minimal and compliant?
- What are mandatory controls for token rotation and revocation?
- What logging or audit evidence is required for periodic review?
- What security sign-off is required before pilot launch?

### Expected outputs

- Auth model approved or revised with clear action items.
- Scope approvals documented.
- Token governance requirements confirmed.
- Security sign-off owner identified.

## Platform / IT operations

### Objective

Confirm where and how secrets are managed and verify runtime network/connectivity path for non-prod calls.

### You need to have ready

- Proposed runtime host/environment details.
- Secret storage options and preferred approach.
- Connectivity requirements (egress destinations, DNS, firewall needs).
- Operational support expectations (monitoring, alerting, on-call routing).

### You need to ask them

- Which secret manager/process is approved for this workload?
- How should credentials be injected at runtime?
- What network rules are required to reach non-prod Workday endpoints?
- What observability minimums are required for production readiness?
- What is the escalation path for connectivity or runtime failures?

### Expected outputs

- Approved secret handling pattern.
- Confirmed runtime connectivity path and network changes.
- Logging/monitoring baseline requirements.
- Platform support owner and escalation model.

## Compliance / privacy

### Objective

Validate that data usage, storage, logging, and retention patterns meet privacy and compliance requirements.

### You need to have ready

- Approved allowlist and denylist.
- Data flow summary showing where attributes are read, transformed, and stored.
- Logging and redaction plan.
- Retention and deletion approach for reports/log artifacts.

### You need to ask them

- Are approved attributes compliant for this use case?
- Are any attributes subject to heightened controls?
- What retention period and deletion controls are required?
- What masking/redaction standards are required in logs and reports?
- Is a formal privacy review or exception request required?

### Expected outputs

- Compliance disposition for field usage.
- Required privacy controls documented.
- Retention requirements confirmed.
- Named compliance approver and any follow-up tasks.

## Meeting cadence and format

- Format: 30-minute focused decision sessions.
- Cadence: run in sequence within one week.
- Artifacts: update decision log immediately after each session.
- Escalation: unresolved decision over 3 business days escalates to project sponsor.

## Suggested tracking table

| Workstream | Owner | Decision due | Current status | Blocker | Next action |
| --- | --- | --- | --- | --- | --- |
| Field allowlist/denylist | Unassigned | TBD | READY | None | Schedule HRIS review |
| Non-prod API credentials | Unassigned | TBD | READY | None | Confirm integration admin owner |
| Auth/token and scope approval | Unassigned | TBD | READY | None | Schedule IAM review |
| Secrets and connectivity path | Unassigned | TBD | READY | None | Confirm platform review participants |
| Privacy/compliance validation | Unassigned | TBD | READY | None | Share data-flow summary |

## References

- [workday-ad-identity-sync-next-steps.md](workday-ad-identity-sync-next-steps.md)
- [workday-ad-identity-sync-sprint-board.md](workday-ad-identity-sync-sprint-board.md)
- [workday-mcp-implementation-plan.md](workday-mcp-implementation-plan.md)
