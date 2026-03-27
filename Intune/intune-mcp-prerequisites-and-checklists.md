---
title: "Intune MCP - prerequisites and implementation checklists"
description: "Practical prerequisites and phase checklists to build an Intune MCP server using the proven Identity MCP pattern."
type: "Implementation Guide"
version: "v1"
author: "N. Castaldi"
date: "2026-03-11"
---

## Purpose

This guide defines exactly what is needed to build an Intune MCP server using the same
delivery pattern that worked for Identity MCP:

- Phased rollout
- Read-only first
- Least privilege and explicit approvals
- Contract-first tool design
- Unit + integration test gates before production

## What to replicate from Identity MCP

Use these proven patterns from the Identity MCP implementation as non-negotiables:

- Backend abstraction with a safe default backend for local contract testing
- Environment-based backend selection
- Tool-level input validation and friendly error messages
- STDERR-only logging for MCP STDIO safety
- Per-tool audit logging (tool, params, result type, result size)
- Separate unit tests and integration smoke tests
- Read-only phase before any write/action capability

## Scope for Intune MCP (Phase 1)

Phase 1 should be read-only device context only.

- Allowed: device inventory, compliance state, ownership, last check-in, management state
- Not allowed: wipe, retire, sync, policy changes, enrollment profile changes

## Prerequisites checklist

Complete all prerequisites before implementation starts.

### A. Governance and ownership

- [ ] Product owner assigned (Endpoint/Intune)
- [ ] Security owner assigned
- [ ] Operational owner assigned (Service Desk or Endpoint Ops)
- [ ] Approved operation list created (read operations only for Phase 1)
- [ ] Read vs write boundary documented and signed off
- [ ] Audit and retention requirements documented

### B. Microsoft tenant and licensing

- [ ] Intune tenant active and healthy
- [ ] Microsoft Graph access for Intune data approved
- [ ] Required roles identified for app consent and validation
- [ ] Non-production tenant or pilot group available for testing

### C. Identity and authentication model

- [ ] App registration created for Intune MCP
- [ ] Authentication method selected:
  - [ ] Certificate-based auth (preferred)
  - [ ] Client secret (temporary/non-production only)
- [ ] Service principal created and documented
- [ ] Token lifetime and credential rotation policy defined

### D. Graph API permissions (least privilege)

Start with read-only permissions, then add only what is required.

- [ ] `DeviceManagementManagedDevices.Read.All`
- [ ] `DeviceManagementConfiguration.Read.All` (only if config/policy context is needed)
- [ ] `Directory.Read.All` (only if user/device directory joins are needed)
- [ ] Admin consent granted by approved role holder
- [ ] Permission justification recorded for each scope

### E. Platform and runtime

- [ ] Python 3.10+ runtime available
- [ ] Project scaffold created (same pattern as Identity MCP)
- [ ] Dependency management chosen and documented (`uv` + `pyproject.toml` recommended)
- [ ] Logging destination defined (file/central sink)
- [ ] Secrets stored in approved secret store (never in code or plain env files)

### F. Data contract and tool design

- [ ] Tool names and response schemas drafted
- [ ] Field-level data minimization applied
- [ ] Error contract defined (`not found`, `access denied`, `timeout`, `throttled`)
- [ ] PII handling and redaction behavior documented

### G. Testing prerequisites

- [ ] Known test devices identified (compliant, non-compliant, stale, retired)
- [ ] Known test users identified (active, disabled, missing owner)
- [ ] Integration test credentials configured securely
- [ ] Expected results captured from Intune portal for baseline comparison

## Recommended Intune MCP tool set (Phase 1)

Keep the same contract style used in Identity MCP.

```text
intune.get_device(device_id)
intune.get_device_by_name(device_name)
intune.list_devices_by_user(user_principal_name)
intune.get_device_compliance(device_id)
intune.get_device_last_check_in(device_id)
intune.list_stale_devices(days)
intune.search_devices(query, limit)
```

## Build checklist (implementation)

### Phase 0 - Kickoff and design

- [ ] Create approved operations list and sign-offs
- [ ] Confirm Graph permission set and admin consent
- [ ] Finalize tool contracts (input/output examples)
- [ ] Define production and non-production configuration values

### Phase 1 - Project scaffold

- [ ] Create files:
  - [ ] `intune_mcp_server.py`
  - [ ] `intune_backend.py`
  - [ ] `intune_graph_adapter.py`
  - [ ] `tests/test_intune_adapter.py`
  - [ ] `tests/test_integration.py`
  - [ ] `pyproject.toml`
- [ ] Add MCP server entrypoint script
- [ ] Add in-memory backend for local safe mode
- [ ] Add environment-based backend switch (`INTUNE_BACKEND=memory|graph`)

### Phase 2 - Graph adapter and contracts

- [ ] Implement token acquisition and refresh logic
- [ ] Implement retry with backoff for Graph throttling (429)
- [ ] Implement timeout handling with clear user-safe messages
- [ ] Map Graph fields to stable MCP response schemas
- [ ] Ensure null-safe handling for missing owner/primary user values

### Phase 3 - Observability and safety

- [ ] Implement STDERR-only logging for STDIO transport safety
- [ ] Add audit log record per tool invocation
- [ ] Redact sensitive fields in logs
- [ ] Add correlation/request IDs to logs

### Phase 4 - Test gates

- [ ] Unit tests pass for parser/mapper/error-handling behavior
- [ ] Integration smoke tests pass against non-production tenant
- [ ] MCP output compared to Intune portal for sampled devices
- [ ] Negative tests pass (`not found`, no permission, timeout, throttling)

### Phase 5 - Pilot rollout

- [ ] Enable read-only tools for pilot users only
- [ ] Validate top 10 service desk queries using Intune MCP responses
- [ ] Collect accuracy and latency metrics
- [ ] Run rollback test (disable graph backend, return to safe mode)

## Definition of done checklist (Phase 1 release)

All items must be true before declaring Intune MCP Phase 1 complete.

- [ ] No write/action tools are exposed
- [ ] All Phase 1 tools return stable schemas
- [ ] Error messages are friendly and non-leaky
- [ ] Audit logs are complete and searchable
- [ ] Unit + integration tests are green
- [ ] Security sign-off is recorded
- [ ] Operational runbook and escalation path are published

## Phase 2 preview (cross-system correlation)

After Phase 1 is stable, add correlation with Identity MCP and Inventory MCP.

- [ ] Devices assigned to disabled users
- [ ] Devices compliant in Intune but missing in inventory
- [ ] Devices stale in Intune and still tied to active users

No automated remediation in this phase.

## Phase 3 preview (controlled actions)

Only after explicit approval and SOP mapping:

- [ ] `intune.retire_device(device_id)` (human approval gate required)
- [ ] `intune.sync_device(device_id)` (rate-limited and logged)
- [ ] Additional actions only with Security + Endpoint sign-off

Guardrail sequence must always be:

1. AI recommends action
2. Human approves action
3. MCP executes one action
4. Result is written to audit trail (and ticket when integrated)

## Common failure points to prevent early

- Over-scoped Graph permissions in initial release
- No throttling strategy for Graph API calls
- Returning raw Graph payloads instead of stable response contracts
- Missing comparison tests against Intune portal values
- Logging secrets or full token payloads
- Introducing write actions before read-only maturity

## Suggested next artifact set

Create these two follow-on docs next:

- `intune-mcp-install-guide.md` (step-by-step deployment)
- `intune-mcp-test-plan.md` (test matrix and evidence checklist)
