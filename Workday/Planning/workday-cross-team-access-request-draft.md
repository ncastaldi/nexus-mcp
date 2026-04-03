---
title: "Workday to AD sync — cross-team access request draft"
description: "Draft message to align Workday, Security, IT Ops, and Compliance stakeholders on non-prod access and governance prerequisites."
type: "Draft Communication"
version: "v1"
author: "N. Castaldi"
date: "2026-04-03"
status: "DRAFT"
---

## Subject

Request to align on Workday-to-AD automation access and data requirements

## Draft message

Hi team,

I am leading an initiative to reduce manual onboarding and identity reconciliation work by connecting Workday worker status data to our identity operations workflow (AD/Entra), starting in non-production. The objective is to improve speed, reduce manual errors, and provide a repeatable view of identity mismatches before any remediation actions are considered.

To move this forward safely, I need alignment and approvals across teams on the following:

- Confirm the right Workday data fields we are approved to use.
- Provision non-prod API access and integration credentials.
- Approve auth/token and least-privilege scope.
- Confirm secrets handling and runtime connectivity path.
- Validate privacy/compliance guardrails on allowed vs restricted attributes.

What I need from each group:

- HRIS/Workday owner: confirm required business fields, source-of-truth definitions, and authoritative business rules.
- Workday integration admin: provide non-prod API endpoint details and create integration account/client credentials.
- Security/IAM: approve authentication approach, token lifecycle expectations, and least-privilege scopes.
- Platform/IT operations: confirm approved secret storage mechanism and runtime connectivity path.
- Compliance/privacy (if required): validate allowed versus restricted attributes and retention/logging constraints.

Proposed next step:

I am requesting a 30-minute working session next week to confirm owners, decisions, and timeline. Once these dependencies are closed, we can begin non-prod validation and provide a clear readiness update.

Thank you for partnering on this. The outcome is a lower-risk, more reliable identity process with stronger operational visibility.

## Notes for sender

- Keep this message as-is for broad audience send.
- Customize the timeline sentence after checking stakeholder availability.
- Attach supporting docs:
- [workday-ad-identity-sync-next-steps.md](workday-ad-identity-sync-next-steps.md)
- [workday-ad-identity-sync-sprint-board.md](workday-ad-identity-sync-sprint-board.md)
