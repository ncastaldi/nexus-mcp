# Deployment Plan — Workday READ‑ONLY MCP

## Purpose & Scope

### What this MCP is

A **Workday Context MCP** that exposes **authoritative workforce data** to downstream identity and device workflows **without performing HR actions**.

### What this MCP is *not*

*   ❌ Not provisioning users
*   ❌ Not triggering hires/terminations
*   ❌ Not modifying worker records
*   ❌ Not replacing PECI or HR integrations

> MCP is used to **observe and reason**, not execute HR transactions.

***

## Phase 0 — Governance & alignment (mandatory)

### Stakeholders

*   HRIS (Workday owner)
*   IAM / AD owners
*   Security
*   Deskside / IT Ops

### Explicit agreements (write these down)

*   Workday remains **sole Source of Truth**
*   MCP access is **read‑only**
*   Identity actions remain **IT‑owned**
*   MCP insights may **recommend**, not execute

This mirrors how Workday integrations are typically consumed by downstream systems today. [\[sqlservercentral.com\]](https://www.sqlservercentral.com/articles/model-context-protocol-mcp-a-developers-guide-to-long-context-llm-integration)

✅ **Exit criteria:**  
Security and HR sign off on *read‑only contextual access*.

***

## Phase 1 — Integration foundation (no AI yet)

### Objective

Create a **Workday MCP server** that safely wraps existing Workday APIs.

### Technical model

*   Workday **Integration System User (ISU)**
*   OAuth 2.0 / API credentials
*   Scoped to **GET‑only endpoints**
*   No custom UI access
*   No background jobs

This matches standard Workday REST integration practices. [\[sqlservercentral.com\]](https://www.sqlservercentral.com/articles/model-context-protocol-mcp-a-developers-guide-to-long-context-llm-integration)

***

## Phase 2 — Tool surface definition (critical)

### Only expose identity‑relevant context

These tools already exist conceptually in HRIS integrations and are widely used by downstream systems:

#### Core MCP tools

    workday.getWorker(identifier)
    workday.getWorkerStatus(identifier)
    workday.getWorkerOrgAttributes(identifier)
    workday.getWorkerManager(identifier)
    workday.getWorkerEffectiveDates(identifier)

### Data allowed

*   Worker ID
*   Name / email
*   Employment status (active, terminated, future‑dated)
*   Job profile
*   Cost center / department
*   Location
*   Manager

### Explicit exclusions

*   Compensation
*   Performance
*   Benefits
*   Payroll
*   Medical / protected fields

✅ **Exit criteria:**  
HR confirms fields exposed align with least‑privilege HRIS policy.

***

## Phase 3 — Read‑only validation & drift detection

### Objective

Use Workday MCP to **detect identity drift**, not fix it.

### Example read‑only use cases

*   “User active in AD but terminated in Workday”
*   “User manager mismatch between AD and Workday”
*   “Future‑dated hires missing in AD”
*   “Contractors whose Workday end date has passed”

These patterns are already common in Workday → downstream sync architectures. [\[artificial...school.com\]](https://artificialintelligenceschool.com/model-context-protocol-mcp-guide/)

✅ **Exit criteria:**  
Workday MCP reliably answers identity state questions without writes.

***

## Phase 4 — Correlation with Identity MCP (key value)

### Objective

Let AI reason across **Workday → AD / Entra → Intune**.

### Architecture

    Workday MCP (SoT)
         ↓
    Identity MCP (AD / Entra)
         ↓
    Device / Access Decisions

### Example insight queries

*   “Who *should* exist vs who *does* exist”
*   “Which users still have access but are no longer employees”
*   “Which new hires are future‑dated and should not be provisioned yet”

✅ **Important**
Workday MCP **never** updates AD.  
It only provides authoritative context.

***

## Phase 5 — Human‑approved remediation workflows

### Objective

Use Workday MCP insights to **support existing SOPs**, not replace them.

### Pattern

1.  AI detects mismatch
2.  AI explains *why* (Workday vs AD)
3.  Human chooses remediation
4.  Identity MCP or existing automation executes change
5.  Ticket updated

This preserves separation of duties and auditability.

***

## Phase 6 — Audit, security, and lifecycle controls

### Logging

*   Every MCP request logged
*   Tool name + parameters + timestamp
*   No PII expansion beyond approved fields

### Change management

*   Tool definitions version‑controlled
*   HR schema changes reviewed
*   Workday biannual releases validated (standard HRIS practice) [\[dev.to\]](https://dev.to/jamie_thompson/mcp-servers-explained-how-ai-assistants-connect-to-your-tools-598o)

### Access lifecycle

*   Integration user rotated per policy
*   MCP server access limited to approved hosts

***

## Risk analysis (why this is safe)

| Risk                  | Mitigation                 |
| --------------------- | -------------------------- |
| HR data misuse        | Read‑only + scoped fields  |
| AI acting as HR       | No write tools exposed     |
| Privilege creep       | Fixed tool manifest        |
| Audit gaps            | Full request logging       |
| Integration fragility | Uses standard Workday APIs |

This is **safer than CSV exports or ad‑hoc scripts**, which bypass observability.

***

## Deployment sequencing (recommended)

1.  ✅ Workday MCP (read‑only)
2.  ✅ Identity MCP (read‑only)
3.  ✅ Correlation & reporting
4.  ✅ Human‑approved remediation
5.  ❌ Never allow Workday writes via MCP

***

## Executive‑level summary (one paragraph)

> This deployment introduces a read‑only Workday MCP that exposes authoritative workforce data to IT identity systems without allowing AI or automation to modify HR records. Workday remains the Source of Truth, while AD and Entra remain enforcement systems. MCP improves visibility, reduces identity drift, and strengthens auditability without changing ownership boundaries or compliance posture.

***

## One‑sentence takeaway

> **A read‑only Workday MCP gives IT perfect awareness of “who should exist” without ever letting AI touch “who exists.”**

***
