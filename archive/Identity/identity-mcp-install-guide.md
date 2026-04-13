---
title: "Identity MCP — Deployment and install guide"
description: "Step-by-step guide for deploying the Identity MCP server in a phased rollout across Active Directory and Entra ID environments."
type: "Install Guide"
version: "v2"
author: "N. Castaldi"
date: "2026-03-11"
---

<!-- Guide Title and Logo Row -->
<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5em;">
  <h1 style="margin: 0; font-size: 2em;">Identity MCP — Deployment and install guide</h1>
  <img src="https://rwdn-uploads.s3.amazonaws.com/mcgl15001/production/54b7a8d305541296303508cec6e5dfb6.png" alt="Company Logo" style="height:60px; max-width:180px; object-fit:contain;">
</div>

## Table of contents

- [Introduction](#introduction)
- [Definitions](#definitions)
- [Prerequisites / Required tools & access](#prerequisites--required-tools--access)
- [Installation procedure](#installation-procedure)
- [Post-installation actions](#post-installation-actions)
- [Troubleshooting / Escalation procedures](#troubleshooting--escalation-procedures)
- [References / Related documents](#references--related-documents)
- [Revision history](#revision-history)

---

## Introduction

### Purpose

This guide describes how to deploy the **Identity MCP** server in a phased rollout. It covers pre-deployment alignment, read-only AD/Entra ID exposure, correlated cross-system queries, SOP-aligned write actions with human-approval guardrails, and final Service Desk integration.

### Audience

IT Management, Security team, and Developers or Automation engineers responsible for implementing or governing the Identity MCP deployment.

### Scope

This guide covers the deployment of Identity MCP as a **governed interface** to Active Directory and Entra ID. It does not replace any existing IAM system. All authoritative identity systems remain unchanged:

- On-premises Active Directory
- Entra ID (Azure AD)
- Microsoft 365 admin center
- Service desk ticketing system

MCP becomes an assistive interface, not a new identity system.

---

## Definitions

| Term | Definition |
| --- | --- |
| **MCP** | Model Context Protocol — a standard interface that exposes structured data and approved operations to AI clients |
| **Identity MCP** | An MCP server that surfaces AD and Entra ID identity state, and approved identity operations, to AI clients |
| **AD** | Active Directory — on-premises directory service managing users, computers, and groups |
| **Entra ID** | Microsoft cloud identity platform (formerly Azure AD) |
| **OU** | Organizational Unit — a container within AD used to organize objects and apply Group Policy |
| **Service account** | A dedicated, non-personal AD account used exclusively by the MCP server with least-privilege permissions |

---

## Prerequisites / Required tools & access

Complete all items below before beginning any phase of deployment.

- [ ] **Approved identity operations list** — written list of every operation the MCP server is permitted to perform
- [ ] **Service account provisioned** — dedicated AD service account created (e.g., `svc-identity-mcp`); no shared or admin credentials
- [ ] **Read vs write separation documented** — explicit written boundary between read-only phases and write-action phases
- [ ] **AD permissions set** — service account has *Read Directory Data* only (minimum required for Phase 1)
- [ ] **MCP server host prepared** — server or container host ready to run the MCP process
- [ ] **Version control repository** — MCP tool definitions must be tracked in source control from day 1
- [ ] **Access to existing SOP documentation** — see [References / Related documents](#references--related-documents)

> **No MCP code is written until all Phase 0 alignment deliverables are confirmed.**

### Validation steps (Prerequisites)

Before proceeding, explicitly validate each prerequisite:

1. **Approved identity operations list**
    - Confirm the list is written and version-controlled.
    - Confirm each operation maps to an existing SOP step.
    - Confirm Security has reviewed and approved the list.

2. **Service account**
    - Verify the service account is non-interactive.
    - Verify the service account is not a member of admin groups.
    - Verify the account has no delegated permissions beyond *Read Directory Data*.
    - Test authentication using service account credentials from the MCP host.

3. **Read vs write boundary**
    - Confirm Phases 1 and 2 include no write-capable tools.
    - Confirm write-capable tools are not defined in source control before Phase 3 approval.

4. **Version control readiness**
    - Confirm the repository exists and is accessible.
    - Confirm tool definitions are committed before deployment.
    - Confirm all changes require pull request review (or equivalent).

Deployment must not proceed until all validation steps are complete.

---

## Installation procedure

The deployment follows five sequential phases. Each phase must reach its defined exit criteria before the next begins.

```mermaid
flowchart LR
    phase-zero[Phase 0: Pre-deployment alignment] --> phase-one[Phase 1: Read-only identity]
    phase-one --> phase-two[Phase 2: Correlated insight]
    phase-two --> phase-three[Phase 3: Controlled writes]
    phase-three --> phase-four[Phase 4: Service Desk coupling]
```

| Phase | Capability | Risk level |
| --- | --- | --- |
| 0 | Pre-deployment alignment | None |
| 1 | Read-only identity queries | None |
| 2 | Cross-system correlation | Low |
| 3 | SOP-approved write actions | Medium (controlled) |
| 4 | Ticket integration | Low |

---

### Phase 0: Pre-deployment alignment

**Objective:** Reach written agreement on what Identity MCP is permitted to do before any code is written.

1. Review all existing identity-related SOPs and PowerShell scripts (see [References](#references--related-documents)).
2. Produce and circulate the **approved identity operations list** — enumerate every operation the MCP server will be allowed to perform.
3. Define the **service account model**:
    - Create a dedicated AD service account (e.g., `svc-identity-mcp`).
    - Grant *Read Directory Data* permissions only at this stage.
    - Do not reuse admin or named-user credentials.
4. Document the **read vs write boundary** in writing. Phases 1 and 2 are strictly read-only. Phase 3 introduces the first write actions.
5. Obtain sign-off from IT Management and the Security team before proceeding to Phase 1.

#### Phase 0 execution steps

1. Inventory all identity-related SOPs that involve group membership changes, OU moves, termination handling, and device-to-user relationships.
2. For each SOP, classify the steps as read-only or write, and mark which write steps are reversible.
3. Build the **Approved Identity Operations List** with one row per operation, including object type, scope, risk level, and SOP reference.
4. Review the operations list with IT Management for operational fit and Security for audit and risk posture.
5. Create and harden the service account using the naming standard `svc-identity-mcp`, with no mailbox and no interactive logon.
6. Publish and circulate the final Phase 0 sign-off artifact before any implementation work begins.

✅ **Exit criteria:** Approved operations list, service account created, read/write boundary documented, sign-off obtained.

---

### Phase 1: Read-only identity deployment

**Objective:** Allow AI clients to observe identity state safely, without taking any action.

1. Configure the MCP server to run under the dedicated AD service account provisioned in Phase 0.
2. Implement the following read-only tools. Each must map **1:1 to an existing PowerShell query** and must not add new logic:

    ```powershell
    identity.getUser(username)           # Returns: enabled/disabled, OU, description, last logon
    identity.getUserGroups(username)     # Returns: all group memberships for a user
    identity.getGroupMembers(groupName)  # Returns: all members of a named group
    identity.findStaleUsers(days)        # Returns: users with no logon activity in N days
    identity.getComputer(computerName)   # Returns: device account, OU placement
    ```

3. Test each tool against known objects in a non-production OU before enabling it for AI client access.
4. Confirm audit logging is active — each MCP call must record: tool name, input parameters, result, and timestamp.

#### Phase 1 implementation steps

1. Deploy and harden the MCP host.
    - Confirm network connectivity to domain controllers.
    - Confirm DNS resolution and system time synchronization.
2. Configure runtime authentication.
    - Run the MCP process under the dedicated service account.
    - Confirm no fallback credentials are configured.
3. Validate functional parity.
    - Run each MCP tool against an enabled user, disabled user, and known test OU.
    - Compare MCP outputs to the equivalent manual PowerShell query output.
4. Validate logging integrity.
    - Confirm logs capture tool name, parameters, timestamp, and result count.
    - Confirm log retention matches security policy.
5. Restrict tool exposure.
    - Expose tools only to approved AI clients.
    - Do not expose tools directly to end users.

✅ **Exit criteria:** All five read-only tools deployed and verified. AI can answer identity questions the team already investigates manually — without taking action.

---

### Phase 2: Correlated identity insight

**Objective:** Connect identity data to device and process context by combining Identity MCP with other MCP servers.

1. Confirm the following MCP servers are operational (or plan their deployment in parallel):
    - Intune MCP
    - Inventory MCP
    - Service Desk MCP (read-only)

2. Define and validate cross-system query patterns. Example queries enabled at this phase:

    | Query | MCP servers involved |
    | --- | --- |
    | Which users still have VPN access but are no longer active? | Identity MCP |
    | Which devices belong to disabled users but remain domain-joined? | Identity MCP + Intune MCP |
    | Which onboarding tickets are missing required group assignments? | Identity MCP + Service Desk MCP |

3. Validate each cross-system query returns accurate results against real data before exposing it to end users.

✅ **Exit criteria:** Identity is used as enrichment context alongside at least one other MCP source. Cross-system queries support SOP enforcement without performing any automated actions.

---

### Phase 3: Controlled write actions

**Objective:** Introduce safe, reversible identity actions that are already defined in existing SOPs.

> **Warning:** Do not implement any write action that does not have a corresponding documented SOP step.

**Allowed write actions (initial scope):**

- Add or remove a user from a **non-privileged group**
- Update a user's description field (termination markers, per termination SOP)
- Move users or computers between **approved OUs**

**Explicitly excluded from Phase 3:**

- Account deletion
- Privileged group changes
- Password resets
- MFA configuration changes

**Guardrail model — every write action must follow this sequence without exception:**

```
1. AI proposes action
2. Human reviews and explicitly approves
3. MCP executes
4. Result logged (ticket update and/or audit log entry)
```

No silent execution is permitted at any point.

#### Phase 3 write-action enforcement mechanics

Every write-capable tool must implement the controls below:

1. **Pre-execution validation**
    - Verify the target object exists.
    - Verify the requested operation exists in the Approved Identity Operations List.
    - Verify the target group or OU is on the approved target list.
2. **Human approval gate**
    - Present object, current state, and proposed state.
    - Require explicit human confirmation before execution.
3. **Execution boundaries**
    - Execute exactly one identity change per invocation.
    - Do not chain multiple write actions in one run.
4. **Post-execution verification**
    - Re-query the object and confirm the expected state change is present.
5. **Audit completion**
    - Record approver identity, change details, timestamp, and ticket reference.

✅ **Exit criteria:** Write actions deployed behind a human-approval gate. No action executes without an explicit approval step. Audit log entries confirmed for each write operation.

---

### Phase 4: Service Desk coupling

**Objective:** Tie every identity action to a work-tracking record, enforcing ticket-update requirements already present in existing SOPs.

1. Configure the MCP server to require a ticket ID for all write operations.
2. Implement a check that blocks action completion if no ticket reference is provided.
3. Configure automatic ticket updates on action completion to prevent "work done, ticket forgotten."
4. Validate the audit trail end-to-end: each identity change must be traceable from the originating ticket to the MCP call log entry.

✅ **Exit criteria:** Every identity action is tied to a ticket. Full audit trail confirmed from human request → MCP execution → ticket update.

---

## Post-installation actions

Once all phases are deployed, enforce the following controls on an ongoing basis.

### Identity controls

- The MCP service account must never be used interactively or by any other service.
- Apply the principle of least privilege per operation — do not pre-elevate permissions ahead of need.
- Review service account permissions each time a new write operation is added.

### Audit controls

- Every MCP call must log: tool name, input parameters, result, and timestamp.
- Logs must be retained and correlatable to the originating human prompt and ticket.
- Review audit logs regularly — weekly is recommended during initial rollout.

### Change control

- All MCP tool definitions must be version-controlled.
- Changes to tool definitions must go through the same review process as PowerShell script changes.
- Any change to an underlying SOP must trigger a review of the corresponding MCP tool definition.

---

## Troubleshooting / Escalation procedures

| Issue | Resolution |
| --- | --- |
| MCP server cannot connect to AD | Verify service account credentials and network access to the domain controller. Check firewall rules between the MCP host and AD. |
| Tool returns no results for a known user | Confirm the service account has *Read Directory Data* permission. Test the equivalent PowerShell query directly on the MCP host. |
| Write action executes without triggering an approval step | Immediately disable the write-action tool. Review the guardrail configuration. Do not re-enable until the approval gate is confirmed functional. |
| Audit log has missing entries | Halt all write-action operations until logging is restored and the gap is accounted for. |
| Cross-system query returns inconsistent data | Isolate to the specific MCP source (Identity, Intune, or Inventory). Test each source independently with known test data. |
| Phase 3 write operation blocked with no clear reason | Check that a valid ticket ID was provided. Confirm the target group or OU is on the approved list from Phase 0. |

**Important:** Identity MCP is explicitly designed to **not** do the following. If a request falls into this list, fulfil it through standard tooling — it is out of scope for Identity MCP:

- Replace ADUC or the Azure portal for direct identity management
- Auto-provision new user accounts
- Decide or modify identity policy
- Bypass approval workflows or change control

**Escalation contact:** Raise a ticket with the IT Automation team for issues outside the above resolutions.

### Troubleshooting decision flow

When an issue occurs:

1. Determine the failing phase.
    - Phase 1 or 2 indicates a read-only failure domain.
    - Phase 3 or 4 indicates a write workflow or enforcement failure domain.
2. For read-only failures:
    - Run the equivalent manual PowerShell query.
    - Compare manual and MCP outputs.
    - Disable the affected tool if outputs diverge.
3. For write-related failures:
    - Immediately disable the affected write tool.
    - Do not auto-retry execution.
    - Re-validate approval gate behavior before re-enabling.
4. For audit logging failures:
    - Suspend all write actions.
    - Resume only after log integrity is restored and verified.

Escalate only after isolating the failure to a specific tool or phase.

---

## References / Related documents

- [Active Directory — PowerShell procedures (OneNote)](https://wheelsinc.sharepoint.com/sites/WheelsITServiceDesk/_layouts/15/Doc.aspx?action=edit&mobileredirect=true&wdorigin=Sharepoint&DefaultItemOpen=1&sourcedoc={04cb4993-3d7c-4785-b67f-6a6afefdcaa8}&wd=target(/PowerShell.one/)&wdpartid={4d895098-550e-0b0c-194c-af7c0195f51e}{1}&wdsectionfileid={7ffa6051-4ff6-4039-96a0-8533c34d8ade})
- [User termination SOP (OneNote)](https://wheelsinc.sharepoint.com/sites/WheelsITServiceDesk/_layouts/15/Doc.aspx?action=edit&mobileredirect=true&wdorigin=Sharepoint&DefaultItemOpen=1&sourcedoc={04cb4993-3d7c-4785-b67f-6a6afefdcaa8}&wd=target(/User Termination.one/)&wdpartid={b2ba40a3-f389-4021-9ec5-54268ce102ab}{1}&wdsectionfileid={33ca8871-68c7-4218-a016-fca812102c86})
- [Onboarding — new account setup (Word)](https://wheelsinc.sharepoint.com/sites/WheelsITServiceDesk/_layouts/15/Doc.aspx?sourcedoc=%7B2594F0FC-A36C-40A2-A5E8-C227EE9ACC6F%7D&file=Onboarding%20Process%20-%20New%20account%20setup.docx&action=default&mobileredirect=true&DefaultItemOpen=1)
- [Service Desk documentation — new account setup (Word)](https://wheelsinc.sharepoint.com/sites/WheelsITDesksideServices/_layouts/15/Doc.aspx?sourcedoc=%7B8B3CF4B1-D9C1-4A6F-A5AA-99277B453783%7D&file=Latest%20Service%20Desk%20Documentation%20-%20New%20account%20setup.docx&action=default&mobileredirect=true&DefaultItemOpen=1)
- [Device image and setup SOP (Word)](https://wheelsinc.sharepoint.com/sites/WheelsITDesksideServices/_layouts/15/Doc.aspx?sourcedoc=%7B8BF1A3D1-C48A-4921-86FD-6A00AC9FE198%7D&file=Device%20Image%20and%20Setup%20SoP.docx&action=default&mobileredirect=true&DefaultItemOpen=1)
- [IT-SOP-009 — New device setup (PDF)](https://wheelsinc.sharepoint.com/sites/WheelsITDesksideServices/Shared%20Documents/General/SOPs/IT-SOP-009%20New%20Device%20Setup.pdf?web=1)

---

## Revision history

| Version | Date | Author | Description |
| --- | --- | --- | --- |
| v2 | 2026-03-11 | N. Castaldi | Added operational validation and enforcement steps from Additional Steps guidance |
| v1 | 2026-03-11 | N. Castaldi | Initial draft |
