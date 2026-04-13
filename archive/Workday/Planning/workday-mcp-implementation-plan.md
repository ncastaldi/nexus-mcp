---
title: "Workday MCP — implementation and auth plan"
description: "Execution plan to build a read-only Workday MCP server using the proven Identity MCP pattern."
type: "Implementation Plan"
version: "v1"
author: "N. Castaldi"
date: "2026-03-11"
---

## Objective

Build a read-only Workday MCP server by reusing the implementation pattern that succeeded in the Identity MCP server, while replacing the AD/PowerShell adapter with a Workday REST/OAuth adapter.

## Scope for first release

Included:
- Read-only tools only:
    - workday.getWorker(identifier)
    - workday.getWorkerStatus(identifier)
    - workday.getWorkerOrgAttributes(identifier)
    - workday.getWorkerManager(identifier)
    - workday.getWorkerEffectiveDates(identifier)
- Workday MCP project scaffolding equivalent to the Identity MCP structure
- In-memory backend for local contract testing
- API backend for Workday REST integration
- Unit tests and integration smoke tests
- Logging and audit controls

Excluded:
- Any write actions to Workday
- Any HR transaction support
- Ticketing automation from Workday MCP
- Correlation/remediation execution logic beyond read-only outputs

## Current decisions captured

- API family for v1: REST only
- Security model: least privilege, read-only field scope
- Deployment model: phased rollout aligned to existing Workday install guide
- Architecture pattern: dual backend (`memory` default, `api` production)

## Build plan (execution sequence)

1. Clone the Identity MCP skeleton into Workday equivalents.
2. Create Workday backend contract with five async tool methods.
3. Implement in-memory backend with safe sample worker payloads.
4. Implement FastMCP server entrypoint and tool wrappers.
5. Implement Workday REST adapter with OAuth token handling.
6. Add config and secret-loading contract.
7. Add adapter unit tests with mocked HTTP/token responses.
8. Add non-prod integration smoke tests for end-to-end validation.
9. Validate output schema allowlist and excluded fields.
10. Publish runbook updates and final verification checklist.

## Files to create for parity with Identity MCP

- workday_mcp_server.py
- workday_backend.py
- workday_adapter.py
- debug_workday_connectivity.py
- pyproject.toml
- .gitignore
- tests/test_workday_adapter.py
- tests/test_integration.py

## Authentication implementation requirements

1. Use Workday REST API with OAuth 2.0 for API calls.
2. Use a dedicated Integration System User (ISU) for MCP access.
3. Register and manage a dedicated Workday API client for this service.
4. Restrict security group and domain permissions to approved read-only fields.
5. Keep separate credentials and client configuration for non-production and production.
6. Store client secret/token material in approved secret storage, never in code.
7. Enforce token refresh, timeout, retry, and rate-limit handling in adapter logic.

## Data to gather (required before build proceeds)

### A. Workday auth and tenant details
- Tenant name(s) for non-production and production
- Base API host URL(s)
- Approved OAuth grant type for this integration
- Token endpoint details and expected token lifetime
- Refresh token policy and rotation requirements

### B. Identity and access control details
- ISU account name and owner
- Integration security group name
- Exact domain permissions approved for read-only use
- Explicit list of denied domains/fields

### C. Endpoint and schema contract
- Exact Workday REST endpoints for each of the 5 tools
- Required request parameters and lookup identifiers
- Expected success payload shape per endpoint
- Error payload examples for 401/403/404/429/5xx

### D. Operations and observability
- Required logging sink and retention policy
- Required audit fields per MCP invocation
- Retry/backoff thresholds and timeout limits
- Rate-limit constraints provided by tenant admins

## Current blockers

1. OAuth grant type is not finalized.
2. Ownership for credential and security-group provisioning is not assigned.
3. Non-production Workday tenant/sandbox access is not yet available.
4. Exact endpoint-to-tool mapping is not finalized.
5. Approved field allowlist and denylist are not yet locked to testable schema contracts.

## Dedicated next steps

1. Assign owner for Workday auth provisioning (HRIS or IAM/Security) and confirm accountable approver.
2. Finalize OAuth grant type and token lifecycle policy in a short design decision record.
3. Provision non-production tenant access and generate non-prod API client credentials.
4. Confirm ISU + security group + domain permissions for read-only scope.
5. Produce endpoint mapping table (tool -> endpoint -> fields -> error contract).
6. Create initial Workday project scaffold and run server in memory mode.
7. Implement adapter token flow and one tool end-to-end in non-prod.
8. Expand to all five tools and complete unit plus integration test gates.
9. Validate logs and outputs for secret safety and field-scope compliance.
10. Update install guide with exact run/test commands once implementation is proven.

## Verification checklist

- [ ] All blocker items are resolved and documented.
- [ ] Server starts in memory mode and API mode.
- [ ] All five tools return only approved fields.
- [ ] Unit tests pass with mocked auth and API error scenarios.
- [ ] Integration tests pass against non-production tenant.
- [ ] No secrets appear in logs.
- [ ] Audit logs capture tool name, parameters, timestamp, and result status.

## Related documents

- [workday-mcp-install-guide.md](./workday-mcp-install-guide.md)
- [CoPilot Generated Deployment Plan.md](./CoPilot%20Generated%20Deployment%20Plan.md)
- [CoPilot Generated Additional Steps.md](./CoPilot%20Generated%20Additional%20Steps.md)
- [../Identity/implementation-guide.md](../Identity/implementation-guide.md)
