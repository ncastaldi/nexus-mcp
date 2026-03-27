# Identity MCP – Deployment Plan

## Scope definition (what “Identity MCP” means here)

**Identity MCP** in your environment = an MCP server that exposes **Active Directory + Entra ID identity state and approved identity operations** to AI clients **without replacing existing IAM processes**.

**Authoritative systems remain unchanged**:

*   On‑prem Active Directory
*   Entra ID (Azure AD)
*   Microsoft 365 admin center
*   Service desk ticketing

MCP becomes a **governed interface**, not a new identity system.

***

## Phase 0 – Pre‑deployment alignment (required)

### Inputs already in your tenant

Your identity operations are well‑documented and standardized:

*   AD scripts and procedures for:
    *   Group membership
    *   VPN access
    *   Termination workflows [\[Active Directory \| OneNote\]](https://wheelsinc.sharepoint.com/sites/WheelsITServiceDesk/_layouts/15/Doc.aspx?action=edit&mobileredirect=true&wdorigin=Sharepoint&DefaultItemOpen=1&sourcedoc={04cb4993-3d7c-4785-b67f-6a6afefdcaa8}&wd=target(/PowerShell.one/)&wdpartid={4d895098-550e-0b0c-194c-af7c0195f51e}{1}&wdsectionfileid={7ffa6051-4ff6-4039-96a0-8533c34d8ade}), [\[Active Directory \| OneNote\]](https://wheelsinc.sharepoint.com/sites/WheelsITServiceDesk/_layouts/15/Doc.aspx?action=edit&mobileredirect=true&wdorigin=Sharepoint&DefaultItemOpen=1&sourcedoc={04cb4993-3d7c-4785-b67f-6a6afefdcaa8}&wd=target(/User Termination.one/)&wdpartid={b2ba40a3-f389-4021-9ec5-54268ce102ab}{1}&wdsectionfileid={33ca8871-68c7-4218-a016-fca812102c86})
*   New‑hire and onboarding SOPs with explicit AD and Entra steps [\[Onboarding...ount setup \| Word\]](https://wheelsinc.sharepoint.com/sites/WheelsITServiceDesk/_layouts/15/Doc.aspx?sourcedoc=%7B2594F0FC-A36C-40A2-A5E8-C227EE9ACC6F%7D&file=Onboarding%20Process%20-%20New%20account%20setup.docx&action=default&mobileredirect=true&DefaultItemOpen=1), [\[Latest Ser...ount setup \| Word\]](https://wheelsinc.sharepoint.com/sites/WheelsITDesksideServices/_layouts/15/Doc.aspx?sourcedoc=%7B8B3CF4B1-D9C1-4A6F-A5AA-99277B453783%7D&file=Latest%20Service%20Desk%20Documentation%20-%20New%20account%20setup.docx&action=default&mobileredirect=true&DefaultItemOpen=1)
*   Device and user setup SOPs that depend on identity state [\[Device Ima...Setup SoP \| Word\]](https://wheelsinc.sharepoint.com/sites/WheelsITDesksideServices/_layouts/15/Doc.aspx?sourcedoc=%7B8BF1A3D1-C48A-4921-86FD-6A00AC9FE198%7D&file=Device%20Image%20and%20Setup%20SoP.docx&action=default&mobileredirect=true&DefaultItemOpen=1), [\[IT-SOP-009...vice Setup \| PDF\]](https://wheelsinc.sharepoint.com/sites/WheelsITDesksideServices/Shared%20Documents/General/SOPs/IT-SOP-009%20New%20Device%20Setup.pdf?web=1)

### Deliverables

*   ✅ List of **approved identity operations**
*   ✅ Service account model
*   ✅ Read vs write separation

No MCP code is written until this is agreed.

***

## Phase 1 – Read‑only Identity MCP (foundation)

### Objective

Allow AI to **observe identity state safely**.

### MCP server capabilities (read‑only)

Expose **only** what your team already queries manually:

**Users**

*   Enabled / disabled
*   OU
*   Description (termination markers)
*   Last logon

**Groups**

*   Group membership for a user
*   Members of a group
*   VPN‑related group membership (already queried today) [\[Active Directory \| OneNote\]](https://wheelsinc.sharepoint.com/sites/WheelsITServiceDesk/_layouts/15/Doc.aspx?action=edit&mobileredirect=true&wdorigin=Sharepoint&DefaultItemOpen=1&sourcedoc={04cb4993-3d7c-4785-b67f-6a6afefdcaa8}&wd=target(/PowerShell.one/)&wdpartid={4d895098-550e-0b0c-194c-af7c0195f51e}{1}&wdsectionfileid={7ffa6051-4ff6-4039-96a0-8533c34d8ade})

**Computers**

*   Device accounts
*   OU placement

### Technical pattern

*   MCP server runs under **dedicated AD service account**
*   Permissions: *Read Directory Data only*
*   Each MCP tool maps **1:1 to an existing PowerShell query**

No abstraction magic. No new logic.

### Example MCP tools

    identity.getUser(username)
    identity.getUserGroups(username)
    identity.getGroupMembers(groupName)
    identity.findStaleUsers(days)
    identity.getComputer(computerName)

✅ **Outcome**  
AI can answer questions your team already investigates manually—without taking action.

***

## Phase 2 – Correlated identity insight

### Objective

Connect identity data to **device and process context**.

At this point, Identity MCP is used *together with*:

*   Intune MCP
*   Inventory MCP
*   Service Desk MCP (read‑only)

### Example queries unlocked

*   “Which users still have VPN access but are no longer active?”
*   “Which devices belong to disabled users but are still domain‑joined?”
*   “Which onboarding tickets are missing required group assignments?”

This directly supports SOP enforcement without automation.

✅ **Outcome**  
Identity becomes **context**, not just attributes.

***

## Phase 3 – Controlled write actions (SOP‑aligned)

### Objective

Introduce **safe, reversible identity actions** that already exist in SOPs.

### Allowed write actions (initial)

Based strictly on documented procedures:

*   Add/remove user from **non‑privileged groups**
*   Update user description fields (termination markers) [\[Active Directory \| OneNote\]](https://wheelsinc.sharepoint.com/sites/WheelsITServiceDesk/_layouts/15/Doc.aspx?action=edit&mobileredirect=true&wdorigin=Sharepoint&DefaultItemOpen=1&sourcedoc={04cb4993-3d7c-4785-b67f-6a6afefdcaa8}&wd=target(/User Termination.one/)&wdpartid={b2ba40a3-f389-4021-9ec5-54268ce102ab}{1}&wdsectionfileid={33ca8871-68c7-4218-a016-fca812102c86})
*   Move users or computers between **approved OUs**

🚫 Explicitly excluded initially:

*   Account deletion
*   Privileged group changes
*   Password resets
*   MFA changes

### Guardrail model

1.  AI proposes action
2.  Human approves
3.  MCP executes
4.  Result logged (ticket or audit log)

No silent execution.

✅ **Outcome**  
AI assists identity work **without becoming an identity admin**.

***

## Phase 4 – Identity MCP + Service Desk coupling

### Objective

Tie identity state to **work tracking and compliance**.

Your SOPs already require ticket updates and closure steps. [\[Latest Ser...ount setup \| Word\]](https://wheelsinc.sharepoint.com/sites/WheelsITDesksideServices/_layouts/15/Doc.aspx?sourcedoc=%7B8B3CF4B1-D9C1-4A6F-A5AA-99277B453783%7D&file=Latest%20Service%20Desk%20Documentation%20-%20New%20account%20setup.docx&action=default&mobileredirect=true&DefaultItemOpen=1)

### MCP enables

*   Linking identity actions to tickets automatically
*   Preventing “work done, ticket forgotten”
*   Auditable identity changes tied to request origin

✅ **Outcome**  
Identity actions become traceable, not tribal knowledge.

***

## Security & governance controls (non‑negotiable)

### Identity

*   Separate MCP service account
*   No reuse of admin credentials
*   Least‑privilege per operation

### Audit

*   Every MCP call logged
*   Tool name + parameters + result recorded
*   Correlates to human prompt

### Change control

*   MCP tool definitions version‑controlled
*   Changes reviewed like scripts
*   SOP changes trigger MCP review

***

## What Identity MCP deliberately does *not* do

*   Replace ADUC or Azure Portal
*   Auto‑provision users
*   Decide identity policy
*   Bypass approvals

Identity MCP is **assistive infrastructure**, not automation for automation’s sake.

***

## Rollout summary (executive‑safe)

| Phase | Capability                 | Risk                |
| ----- | -------------------------- | ------------------- |
| 1     | Read‑only identity queries | None                |
| 2     | Cross‑system correlation   | Low                 |
| 3     | SOP‑approved writes        | Medium (controlled) |
| 4     | Ticket integration         | Low                 |

***

## One‑sentence summary

> Identity MCP in your environment should start as a **read‑only mirror of existing AD knowledge**, then gradually expose **only those identity actions already defined in SOPs**, with human approval and audit at every step.

***