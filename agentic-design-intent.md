# Agentic design intent

> This document exists to provide context for any developer, AI assistant, or future
> maintainer working on this codebase. It captures the architectural reasoning behind
> the project's design choices so that intelligence can be added at the right layer,
> in the right way, at the right time.

---

## What this project is

`homelab-registry-mcp` is a Python MCP server that acts as the single authoritative
catalog of services running in the Team Castaldi homelab. It discovers services from
Traefik, Authentik, and Docker; reconciles them into a unified registry; detects
configuration drift; and exposes everything through MCP tools consumable by AI
assistants like Frank v6.

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
| 0 — Reactive | Acts only when prompted | MCP tools called by Frank or a user |
| 1 — Scheduled | Acts on a timer without prompting | ✅ Discovery scheduler |
| 2 — Event-driven | Acts because it detected something | ✅ Conflict flagging |
| 3 — Human-in-loop | Pursues goal, pauses for human approval | 🔲 Gitea write path (pinned) |
| 4 — Supervised | Acts autonomously, human can intervene | 🔲 Future consideration |
| 5 — Fully autonomous | Pursues goal end-to-end | ❌ Not appropriate for infrastructure |

Degrees 1 and 2 are already implemented. Degree 3 is the next intentional step.
Degree 5 is explicitly out of scope — the blast radius of an autonomous wrong decision
on live infrastructure is an outage, and that risk is not acceptable without a human
gate.

---

## The agentic loop this project is building toward

```
Scheduler          (perceive)   — runs every 5 min, queries Traefik/Authentik/Docker
Reconciler         (detect)     — finds drift: new services, missing auth, conflicts
DSPy modules       (reason)     — evaluates risk, infers correct remediation
Gitea PR           (propose)    — opens a branch with the config change and a diff
Human review       (approve)    — engineer reviews and merges
Next discovery     (verify)     — confirms the change landed, clears the conflict flag
```

Each step in this loop has a defined home in the codebase. Do not collapse steps or
skip layers. The value of the design is that each concern is isolated and testable.

---

## Where intelligence belongs

This is the most important section for anyone adding capability to this project.

### Perception layer — `discovery/`

**What lives here**: source adapters (Traefik, Authentik, Docker), the scheduler,
the discovery engine.

**What does NOT live here**: reasoning, inference, LLM calls. This layer produces
raw `DiscoveredService` objects. It should be fast, reliable, and deterministic.
A failure here means no data, not wrong data.

### Detection layer — `registry/reconcile.py`

**What lives here**: deterministic matching logic (exact name, URL host, slug),
per-source auth mode tracking, conflict flag computation.

**What does NOT live here**: LLM calls. Conflict detection is rule-based on purpose.
Rules are auditable. An LLM deciding whether something is a conflict is not auditable
at this layer. If a rule needs to change, change the rule explicitly.

### Reasoning layer — `dspy/` (Phase 7, not yet built)

**What lives here**: DSPy modules for entity resolution and enrichment:
- `ResolveServiceIdentity` — fuzzy cross-source matching when deterministic rules fail
- `InferServiceMetadata` — infer category, auth_mode, display_name for new services
- `SummarizeAccessAudit` — pre-synthesize Authentik event data before returning to client

**What does NOT live here**: infrastructure writes, API mutations, file generation.
This layer reasons. It does not act.

**Key constraint**: DSPy modules are optimizable. As the registry accumulates confirmed
service matches (~50+), run `BootstrapFewShot` against a match-accuracy metric. Save
the compiled module to disk and load it at startup. This is the "self-improving" payoff.
Do not manually tune DSPy signatures — let the optimizer do it.

### Proposal layer — `integrations/gitea/` (Phase 8, pinned)

**What lives here**: Gitea API client, config generation logic (Traefik dynamic YAML,
compose label patches), PR creation tools.

**What does NOT live here**: autonomous apply. This layer opens PRs. It does not merge
them. The merge is always a human action.

**New tools at this layer**:
- `config_propose_traefik_change(router, change)` — generates a YAML patch, opens a PR
- `config_propose_compose_label(service, label, value)` — same for compose labels
- `config_list_open_proposals()` — lists open PRs created by this server
- `config_preview_diff(proposal_id)` — shows the diff before it's merged

**Critical constraint**: this layer writes to Gitea only. It never writes directly to
the filesystem that Traefik watches. Direct writes skip the review gate and remove the
audit trail. If a bad config lands in the watched directory it goes live immediately.
The PR path is not optional — it is the safety mechanism.

### Tool surface — `tools/`, `integrations/*/tools.py`

**What lives here**: MCP tool definitions, resource endpoints, prompt templates.

**What does NOT live here**: business logic. Tools are thin wrappers. If a tool is
doing complex reasoning, that reasoning belongs in the reasoning layer, not the tool.

**Key constraint**: all tool return types must be well-typed Pydantic models, not raw
dicts. This ensures DSPy can consume them via `dspy.Tool.from_mcp_tool` cleanly.

---

## What the conflict flags mean and what to do with them

The reconciler sets `auth_mode_conflict = True` when:
- A service is linked to both Traefik (`traefik_router` set) and Authentik
  (`authentik_app_slug` set)
- `traefik_auth_mode = none` (no auth middleware in Traefik)
- `authentik_auth_mode = forward_auth` or `oauth2_proxy` (Authentik has a provider)

This means: **Authentik thinks it's protecting this service. Traefik is not enforcing
it. The service is reachable without authentication.**

As of the time this document was written, 10 services have this flag set. The correct
remediation for `forward_auth` conflicts is to add `authentik-auth@file` to the
Traefik router. The Gitea write path (when built) will propose this automatically.

Do not clear conflict flags manually in the database. They will be re-evaluated on the
next discovery pass. The only correct way to clear a conflict is to fix the underlying
infrastructure.

---

## What Frank v6 is and how it relates

Frank v6 is a modular AI assistant framework (core/skills/specialties layers)
implementing C.R.A.F.T., CoT, ToT, and RAG techniques. It is the primary consumer
of this MCP server.

Frank consumes this server via MCP tools. It does not need to know about the internal
architecture. From Frank's perspective, this server is a tool provider that answers
questions about the homelab.

The `service_get_full_context` tool (Phase 7) is the highest-value tool for Frank —
it returns a complete picture of a service across all sources in one call, allowing
Frank to answer questions like "is Prowlarr actually protected?" without chaining
multiple tool calls.

When Frank v6 itself adopts DSPy (`dspy.ReAct` + `dspy.MCPServerManager`), it will
be able to consume this server with typed tool selection and automatic retry on
structured output failures. That is a Frank concern, not a registry-mcp concern.
Keep the tool signatures clean and typed so that integration is straightforward when
the time comes.

---

## Open items (as of initial authorship)

| Item | Notes |
|---|---|
| Phase 7 — `service_get_full_context` | Aggregated view across all sources; primary Frank tool |
| Phase 7 — DSPy enrichment modules | `ResolveServiceIdentity`, `InferServiceMetadata`, `SummarizeAccessAudit` |
| Phase 8 — Gitea write path | Config proposal tools; the degree-3 agentic step |
| Phase 8 — Authentik RBAC | Service account should use least-privilege role, not Admins group |
| Phase 9 — DSPy optimization pass | Run after 50+ confirmed service matches accumulate |
| FastMCP lifespan bug | `streamable_http_app()` in FastMCP 1.27.1 ignores custom lifespan; scheduler started via `run_streamable_http_async` monkey-patch in `main()`. Remove when FastMCP fixes this upstream. |
| Traefik dashboard — C1 finding | `dashboard-auth@file` middleware exists but `usedBy` is empty; dashboard is publicly accessible. First candidate for the Gitea write path when built. |

---

## A note on scope discipline

This project will attract feature ideas. Before adding capability, ask:

1. **Which layer does this belong to?** If you can't answer clearly, the design isn't
   ready yet.
2. **Does this add intelligence at the right layer?** Reasoning in the detection layer
   and rules in the reasoning layer are both wrong.
3. **Does this preserve the human gate?** Any feature that allows autonomous writes to
   live infrastructure without a review step is out of scope until explicitly decided
   otherwise.
4. **Does this improve the core loop?** Perceive → detect → reason → propose → approve
   → verify. Features that don't touch this loop are probably better as a separate
   project.

The goal is not a feature-complete platform. The goal is a reliable, self-improving
agent loop for homelab infrastructure governance.

---

*Authored through a collaborative design session. Maintained as a living document.*
