# Agentic design intent

> This document exists to provide context for any developer, AI assistant, or future
> maintainer working on this codebase. It captures the architectural reasoning behind
> the project's design choices so that intelligence can be added at the right layer,
> in the right way, at the right time.

---

## What this project is

`nexus-mcp` is a Python MCP server that acts as the authoritative integration point
for enterprise identity and operations systems: Active Directory, Entra ID, Workday
HCM, BMC Helix ITSM, Lansweeper, Intune, and FedEx. It collects data from all those
systems, normalizes it into canonical schemas, detects cross-system drift, and exposes
everything through MCP tools consumable by AI assistants like Frank v6.

It is also — intentionally — a partially agentic system that is designed to become
more agentic over time, in a controlled and deliberate way.

---

## What "agentic" means here

Agentic does not mean "no human involved." It means the system pursues a goal across
multiple steps autonomously. The degree of human involvement is a conscious design
choice, not a measure of how agentic the system is.

This project operates on a spectrum:

| Degree | Description | Status |
|---|---|---|
| 0 — Reactive | Acts only when prompted | ✅ All MCP tools called by Frank or a user |
| 1 — Scheduled | Acts on a timer without prompting | 🔲 Drift scans on schedule (planned) |
| 2 — Event-driven | Acts because it detected something | 🔲 Drift flag escalation (planned) |
| 3 — Human-in-loop | Pursues goal, pauses for human approval | 🔲 Helix ticket proposal (next step) |
| 4 — Supervised | Acts autonomously, human can intervene | 🔲 Future consideration |
| 5 — Fully autonomous | Pursues goal end-to-end | ❌ Not appropriate for identity/HR systems |

Degree 0 is the current state. Degree 3 is the next intentional step.
Degree 5 is explicitly out of scope — an autonomous wrong decision on a live identity
system (disabling the wrong account, corrupting HR data) is an incident, and that risk
is not acceptable without a human gate.

---

## The agentic loop this project is building toward

```
Scan trigger        (perceive)   — polls AD, Entra, Workday on a schedule
Drift detector      (detect)     — finds mismatches: status, job title, dept, name
Reasoning module    (reason)     — evaluates severity, infers correct remediation
Helix ticket        (propose)    — creates an ITSM incident with the drift diff; no fix applied
Human review        (approve)    — IT admin reviews and approves the remediation
Next scan           (verify)     — confirms fix landed; mismatch no longer flagged
```

Each step in this loop has a defined home in the codebase. Do not collapse steps or
skip layers. The value of the design is that each concern is isolated and testable.

---

## Where intelligence belongs

This is the most important section for anyone adding capability to this project.

### Perception layer — `lib/*_client.py`, `lib/ad_adapter.py`

**What lives here**: system API adapters (AD/LDAP, Microsoft Graph, Workday REST,
Helix, Lansweeper GraphQL, Intune, FedEx). This layer produces raw `CanonicalUser`,
`CanonicalDevice`, and related objects. It should be fast, reliable, and deterministic.
A failure here means no data, not wrong data.

**What does NOT live here**: reasoning, inference, LLM calls. If an adapter is doing
anything more than mapping fields, that logic belongs in a higher layer.

### Detection layer — `lib/drift_detection.py`

**What lives here**: deterministic comparison logic — `scan_status_reconciliation`,
`scan_job_title_drift`, `scan_department_mismatches`, `scan_name_variance_mismatches`.
Each function compares canonical fields across systems and returns `FieldDrift` objects
with severity ratings.

**What does NOT live here**: LLM calls. Drift detection is rule-based on purpose.
Rules are auditable. An LLM deciding whether something is a mismatch is not auditable
at this layer. If a rule needs to change, change the rule explicitly in
`lib/drift_detection.py`.

### Reasoning layer — `lib/reasoning/` (not yet built)

**What will live here**: modules for cross-system entity resolution and remediation
inference — for example, fuzzy name matching when Workday legal name and AD display
name differ by a nickname, or severity scoring that weighs a terminated employee's
access against the age of the termination event.

**What does NOT live here**: API writes, ticket creation, field mutations. This layer
reasons. It does not act.

**Key constraint**: when reasoning modules use DSPy or a similar optimization
framework, do not manually tune signatures. Let the optimizer run against accumulated
confirmed-mismatch examples once enough data exists (~50+ labeled cases).

### Proposal layer — `src/shards/itsm.py` (when live against real Helix credentials)

**What lives here**: Helix incident creation, remediation proposals. A tool in this
layer opens a ticket describing a drift finding and a suggested fix. It does not apply
the fix.

**What does NOT live here**: autonomous execution. The ITSM ticket is the safety
mechanism. This server never writes directly to AD, Entra, or Workday. Direct writes
bypass the audit trail and remove the human gate. If a bad write reaches a live
identity system it takes effect immediately. The ticket path is not optional.

### Tool surface — `src/shards/`

**What lives here**: MCP tool definitions — thin wrappers that call into the layers
above and return results to the MCP caller.

**What does NOT live here**: business logic. If a tool function is doing complex
reasoning, that reasoning belongs in the reasoning layer, not in the shard.

**Key constraint**: all tool return types must be well-typed Pydantic models, not raw
dicts. This ensures Frank (and eventually DSPy-powered consumers) can consume them
with typed tool selection. This is the stated design intent; the current `dict | None`
annotations in `identity.py` and `workday.py` are a known gap to be closed.

---

## What drift flags mean and what to do with them

`scan_*` functions in `lib/drift_detection.py` return `FieldDrift` objects. These
represent detected mismatches between systems for a given employee, with a severity
of `HIGH`, `MEDIUM`, or `LOW`.

Do not manually clear or suppress drift findings in code. They are re-evaluated on
every scan pass. The only correct way to clear a drift finding is to fix the
underlying data in the source system (e.g., update the AD display name to match
Workday, or process the termination in AD). Once fixed, the next scan will no longer
flag it.

When the proposal layer is live, a HIGH-severity finding (e.g., terminated in Workday
but still enabled in AD) will automatically result in a Helix incident. The IT admin
who resolves the incident is the human gate.

---

## What Frank v6 is and how it relates

Frank v6 is a modular AI assistant framework (core/skills/specialties layers)
implementing C.R.A.F.T., CoT, ToT, and RAG techniques. It is the primary consumer
of this MCP server.

Frank consumes this server via MCP tools. It does not need to know about the internal
architecture. From Frank's perspective, this server is a tool provider that answers
questions about people, devices, incidents, and shipments.

The highest-value scenario for Frank is answering questions like "is Alex Chen's
account properly terminated across all systems?" without chaining multiple tool calls.
A future `get_user_cross_system_status(email)` tool that aggregates AD, Entra, and
Workday state in a single call would serve this pattern directly.

When Frank v6 itself adopts DSPy (`dspy.ReAct` + `dspy.MCPServerManager`), it will
be able to consume this server with typed tool selection and automatic retry on
structured output failures. That is a Frank concern, not a nexus-mcp concern. Keep
tool signatures clean and typed so that integration is straightforward when the time
comes.

---

## Open items

| Item | Notes |
|---|---|
| Degree 1 — scheduled drift scans | `schedule` is a declared dependency; wire it to `scan_*` functions on a configurable interval |
| Degree 2 — drift flag escalation | Emit a structured event when HIGH-severity drift is detected; proposal layer consumes it |
| Degree 3 — Helix ticket proposal | `itsm.py` tools exist; need live Helix credentials and a `propose_remediation` tool that creates a ticket from a `FieldDrift` result |
| Reasoning layer scaffold | Placeholder module in `lib/reasoning/`; define interfaces before adding implementation |
| `get_user_cross_system_status` | Aggregated single-call view across AD, Entra, Workday; highest-value Frank tool |
| Return type discipline | `identity.py` and `workday.py` return `dict`; should return canonical models (see `nexus-mcp Consistency Audit.md`) |
| Resilience decorator application | `@resilient_http_call` tested but not wired to live shard HTTP call sites |

---

## A note on scope discipline

This project will attract feature ideas. Before adding capability, ask:

1. **Which layer does this belong to?** If you can't answer clearly, the design isn't
   ready yet.
2. **Does this add intelligence at the right layer?** Reasoning in the detection layer
   and rules in the reasoning layer are both wrong.
3. **Does this preserve the human gate?** Any feature that allows autonomous writes to
   AD, Entra, Workday, or any HR/identity system without a review step is out of scope
   until explicitly decided otherwise.
4. **Does this improve the core loop?** Perceive → detect → reason → propose → approve
   → verify. Features that don't touch this loop are probably better as a separate
   project.

The goal is not a feature-complete platform. The goal is a reliable, auditable agent
loop for enterprise identity governance.

---

*Framework originated in a homelab project; rewritten for nexus-mcp. Maintained as a living document.*
