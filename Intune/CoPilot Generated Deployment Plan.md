# Intune / Device Management MCP — Deployment & Initial Guidance

## Purpose

This document provides initial guidance for deploying a **read‑only (and later controlled‑action) Intune MCP** that exposes **live device state** to AI-assisted IT workflows.

The Intune MCP is designed to:

*   Improve **device lifecycle visibility**
*   Reduce reliance on **manual exports and static reports**
*   Enable **cross-system reasoning** with Identity, Inventory, and Service Desk systems

It does **not** replace Microsoft Intune, Autopilot, or existing device management processes.

***

## Why this matters in our environment

Your team already manages the following via Microsoft Intune:

*   Device enrollment and compliance
*   Device refresh and replacement cycles
*   Device wipes, retirements, and repurposing
*   Devices that stop checking in or fail to refresh

These activities are explicitly documented and actively discussed in your Intune and device review materials, including Autopilot deployment and device check‑in workflows. [\[LEARN Auto...It's Hot) | Loop\]](https://loop.cloud.microsoft/p/eyJ1IjoiaHR0cHM6Ly93aGVlbHNpbmMtbXkuc2hhcmVwb2ludC5jb20vcGVyc29uYWwvY2FzdG4xX3doZWVsc19jb20%2FbmF2PWN6MGxNa1p3WlhKemIyNWhiQ1V5Um1OaGMzUnVNU1UxUm5kb1pXVnNjeVUxUm1OdmJTWmtQV0lsTWpGdFFrZ3lWekZSYUVaVlQwUlBibU5GVFd4NlowSlBWMVZCVWpCdVVERkNRWFZXVVVNM1UyTm9NSFZ0UkdFM1NqaEtSRFExVkRWM2FrMTViRU5WVW10aEptWTlNREUzUnpNMFJ6SXlUMDVYTjBSQlRVWkxRbFpCU2tWRFVVVk9OVGRWVEZoSVF5WmpQU1V5UmcifQ%3D%3D), [\[Intune | Word\]](https://wheelsinc-my.sharepoint.com/personal/nkicchan_wheels_com/_layouts/15/Doc.aspx?sourcedoc=%7B5E3AC388-A887-4AA7-AD62-219F56B9B96E%7D\&file=Intune.docx\&action=default\&mobileredirect=true\&DefaultItemOpen=1)

The problem today is **visibility friction**, not capability.

***

## What MCP enables for Intune

With an Intune MCP, AI clients can ask **live, contextual questions** such as:

*   “Which laptops are enrolled but haven’t checked in for 30 days?”
*   “Show devices that are compliant in Intune but missing from inventory.”
*   “Which devices belong to disabled users?”
*   “Retire this device and flag it as eligible for repurpose.” *(future, controlled action)*

Unlike CSV exports or copied portal views, MCP queries **current Intune state** at the time of the request.

***

## Scope and guardrails

### In scope

*   Read access to device state, compliance, and activity metadata
*   Correlation with Identity MCP and Inventory MCP
*   Human-approved device lifecycle actions (future phase)

### Explicitly out of scope (initially)

*   Autonomous device wipes
*   Policy creation or modification
*   Bulk or unattended actions
*   Replacement of Autopilot or Intune portal workflows

***

## Definitions

| Term                | Definition                                                                      |
| ------------------- | ------------------------------------------------------------------------------- |
| **Intune MCP**      | An MCP server that exposes Microsoft Intune device context and approved actions |
| **Enrollment**      | Device registration into Intune (Autopilot or manual)                           |
| **Compliance**      | Device posture relative to Intune policy                                        |
| **Check‑in**        | Last successful device contact with Intune                                      |
| **Lifecycle state** | Active, stale, retired, or eligible-for-repurpose                               |

***

## Deployment phases (high level)



***

## Phase 0 — Governance and alignment

**Objective:** Define what the Intune MCP is allowed to observe and do before any build work begins.

### Steps

1.  Identify stakeholders:
    *   Endpoint / Intune owners
    *   IAM / Identity MCP owners
    *   Security
    *   Deskside / IT Ops

2.  Agree on non-negotiables:
    *   Intune remains the authoritative device management system
    *   MCP is an **interface**, not a policy engine
    *   Initial access is **read-only**
    *   Any device action requires human approval

✅ **Exit criteria:** Written agreement on read vs write boundaries.

***

## Phase 1 — Read‑only Intune MCP

**Objective:** Expose live device state safely.

### Example read-only tools

The Intune MCP should initially expose tools equivalent to what your team already checks manually in the Intune portal:

*   `intune.getDevice(deviceId)`
*   `intune.listDevicesByUser(userId)`
*   `intune.getDeviceCompliance(deviceId)`
*   `intune.getLastCheckIn(deviceId)`
*   `intune.listStaleDevices(days)`

These map directly to enrollment, compliance, and check‑in data already used during Autopilot demos and device investigations. [\[LEARN Auto...It's Hot) | Loop\]](https://loop.cloud.microsoft/p/eyJ1IjoiaHR0cHM6Ly93aGVlbHNpbmMtbXkuc2hhcmVwb2ludC5jb20vcGVyc29uYWwvY2FzdG4xX3doZWVsc19jb20%2FbmF2PWN6MGxNa1p3WlhKemIyNWhiQ1V5Um1OaGMzUnVNU1UxUm5kb1pXVnNjeVUxUm1OdmJTWmtQV0lsTWpGdFFrZ3lWekZSYUVaVlQwUlBibU5GVFd4NlowSlBWMVZCVWpCdVVERkNRWFZXVVVNM1UyTm9NSFZ0UkdFM1NqaEtSRFExVkRWM2FrMTViRU5WVW10aEptWTlNREUzUnpNMFJ6SXlUMDVYTjBSQlRVWkxRbFpCU2tWRFVVVk9OVGRWVEZoSVF5WmpQU1V5UmcifQ%3D%3D), [\[Intune | Word\]](https://wheelsinc-my.sharepoint.com/personal/nkicchan_wheels_com/_layouts/15/Doc.aspx?sourcedoc=%7B5E3AC388-A887-4AA7-AD62-219F56B9B96E%7D\&file=Intune.docx\&action=default\&mobileredirect=true\&DefaultItemOpen=1)

### Validation

*   Compare MCP output to Intune portal views for known devices
*   Confirm no write operations are exposed

✅ **Exit criteria:** MCP answers device-state questions without altering Intune data.

***

## Phase 2 — Cross-system correlation

**Objective:** Combine Intune context with Identity and Inventory MCPs.

### Example correlated questions

*   Devices active in Intune but owned by disabled users (Identity MCP)
*   Devices compliant in Intune but missing from inventory records
*   Devices enrolled but not assigned to a user
*   Devices enrolled but never completed Autopilot setup

This phase directly addresses the “devices not checking in / not refreshing” issues discussed in device review meetings and documentation. [\[LEARN Auto...It's Hot) | Loop\]](https://loop.cloud.microsoft/p/eyJ1IjoiaHR0cHM6Ly93aGVlbHNpbmMtbXkuc2hhcmVwb2ludC5jb20vcGVyc29uYWwvY2FzdG4xX3doZWVsc19jb20%2FbmF2PWN6MGxNa1p3WlhKemIyNWhiQ1V5Um1OaGMzUnVNU1UxUm5kb1pXVnNjeVUxUm1OdmJTWmtQV0lsTWpGdFFrZ3lWekZSYUVaVlQwUlBibU5GVFd4NlowSlBWMVZCVWpCdVVERkNRWFZXVVVNM1UyTm9NSFZ0UkdFM1NqaEtSRFExVkRWM2FrMTViRU5WVW10aEptWTlNREUzUnpNMFJ6SXlUMDVYTjBSQlRVWkxRbFpCU2tWRFVVVk9OVGRWVEZoSVF5WmpQU1V5UmcifQ%3D%3D)

✅ **Exit criteria:** Cross-system insights are accurate and explainable.

***

## Phase 3 — Controlled lifecycle actions (future)

**Objective:** Introduce **human-approved** device actions.

### Allowed actions (initial)

*   Retire device
*   Mark device as eligible for repurpose
*   Trigger a reset *only with explicit approval*

### Guardrail model

    AI identifies device issue
    → AI explains current state (Intune data)
    → Human approves action
    → MCP executes single action
    → Ticket and audit log updated

No unattended execution.

✅ **Exit criteria:** Every action is approved, logged, and traceable.

***

## Phase 4 — Audit and steady state

### Controls

*   Request-level logging for all MCP calls
*   Tool definitions version-controlled
*   Quarterly review of exposed fields and actions
*   Re-validation after Intune / Autopilot process changes

***

## Why this is powerful

Traditional workflows rely on:

*   Exported device lists
*   Static reports
*   Manual portal navigation

An Intune MCP enables:

*   **Live device state**
*   **Contextual reasoning**
*   **Faster, more accurate lifecycle decisions**

✅ This directly improves device lifecycle accuracy without increasing operational risk.

***

## Relationship to other MCPs

| MCP            | Role                                 |
| -------------- | ------------------------------------ |
| Workday MCP    | Who *should* have a device           |
| Identity MCP   | Who *does* have access               |
| **Intune MCP** | What the device is actually doing    |
| Inventory MCP  | Where the device is in its lifecycle |

The Intune MCP is the **ground truth for device reality**.

***

## One‑sentence takeaway

> The Intune MCP gives AI real‑time visibility into device state, turning enrollment, compliance, and refresh decisions from guesswork into facts.

***