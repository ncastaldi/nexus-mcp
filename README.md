# Nexus — Enterprise Integration Platform

> A self-hosted, sharded integration server that connects enterprise business systems and surfaces what they can't see individually.

---

## The Problem

Enterprise systems don't talk to each other. They each hold a piece of the truth — and the gaps between them are where problems hide.

A terminated employee still active in Active Directory. A device enrolled in Intune but untracked in the helpdesk. Fifty laptops
inbound from a voluntary retirement program with no system of record for where they go next. A user generating tickets at an unusual rate that nobody notices because the data lives in three different places.

These aren't edge cases. They're the normal state of enterprise IT when systems grow independently and nobody builds the layer that connects them.

Nexus is that layer.

---

## What It Does

Nexus polls enterprise systems via their native APIs, normalizes the data, and does two things: surfaces inconsistencies between
systems, and aggregates what no single system can report alone.

Each integration is a self-contained **shard**: independently togglable, independently testable, and designed to be extended without touching anything else. The platform grows with the problem.

**Current focus areas:**

- **Identity** — Reconciles user records across Active Directory and Entra ID. Detects status drift, title mismatches, department
  changes, and name variances before they become compliance findings. Workday HCM integration is in active development.

- **ITSM** *(in development)* — Pulls ticket data from BMC Helix to enable operational reporting across users, devices, and issue types Answers questions no single system can: how many tickets has this device generated? What's the incident pattern across a refresh cohort? Which users generate the most escalations?

- **Assets** *(in development)* — Correlates device data across Intune, Lansweeper, and BMC Helix to build a complete picture of device assignment history. Built to support PC refresh programs, voluntary retirement collections, and asset lifecycle management.

- **Logistics** *(in development)* — Tracks device movement through receiving, staging, deployment, and decommission. Started as a solution for tracking inbound refresh hardware; designed to scale to full lifecycle logistics.

**The roadmap:** Host in Azure. Expose via Microsoft Copilot agent. Turn multi-system investigations into conversations.

---

## Built By

Nathan Castaldi — IT systems and integration practitioner.
Built on own time, against real enterprise problems observed in
a production environment.
Portfolio: [linkedin.com/in/nathancastaldi](https://linkedin.com/in/nathancastaldi)

---
---
<!-- STATUS_PAGE:BEGIN -->
## Shard Status Board (Traffic Light)

| Shard | System(s) | Status | NEXUS Ref | Flag | Standard Gate |
| --- | --- | --- | --- | --- | --- |
| identity | Active Directory + Entra ID | 🟢 Green | NEXUS-017 | ENABLE_IDENTITY | Tool tests passing |
| workday | Workday HCM | 🟡 Yellow | NEXUS-009 | ENABLE_WORKDAY | Credentials + live validation pending |
| audit | Cross-system drift + reporting | 🟡 Yellow | NEXUS-018 | ENABLE_AUDIT | Verification maturing |
| itsm | BMC Helix ITSM | 🔴 Red | NEXUS-021 | ENABLE_ITSM | Stub only |
| assets | Lansweeper + Intune | 🔴 Red | NEXUS-022 | ENABLE_ASSETS | Stub only |
| logistics | FedEx | 🔴 Red | NEXUS-023 | ENABLE_LOGISTICS | Stub only |

## Folder Structure

```plaintext
nexus-mcp/
├── src/
│   ├── main.py              # Core Orchestrator — reads flags, loads shards
│   └── shards/              # The 6 Shards (one file = one system domain)
│       ├── __init__.py
│       ├── identity.py      # 🟢 AD & Entra tools
│       ├── workday.py       # 🟡 Worker & Org tools
│       ├── itsm.py          # 🔴 BMC Helix tools
│       ├── assets.py        # 🔴 Lansweeper + Intune tools
│       ├── logistics.py     # 🔴 FedEx tools
│       └── audit.py         # 🟡 Cross-system drift + reporting
├── lib/                     # Low-level system adapters (no tool logic here)
│   ├── config.py
│   ├── ad_adapter.py        # LDAP/AD connection wrapper
│   ├── entra_client.py      # Microsoft Graph (Entra)
│   ├── workday_client.py    # Workday REST + OAuth2
│   ├── helix_client.py      # BMC Helix AR-JWT auth
│   ├── lansweeper_client.py # Lansweeper GraphQL
│   ├── intune_client.py     # Microsoft Graph (Intune)
│   └── fedex_client.py      # FedEx REST + OAuth2
├── tests/
├── .env                     # Feature flags + credentials
├── .env.example             # Template — copy this to .env
└── README.md
```

---

## Architecture: The Shard Contract

Every shard file exposes exactly one function:

```python
def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def my_tool(...) -> ...:
        """Tool docstring visible to the LLM."""
        ...
```

The orchestrator (`src/main.py`) reads feature flags and calls `register(mcp)` for each enabled shard. **No other file is changed to add or remove a shard.**

### Adding a new shard

1. Create `src/shards/my_system.py` following the template above.
2. Add the adapter to `lib/` if needed.
3. Add one line to `src/main.py`:

   ```python
   from shards import my_system
   if _enabled("MY_SYSTEM"):
       my_system.register(mcp)
   ```

4. Add `ENABLE_MY_SYSTEM=true` to `.env`.

### Holding pattern

Leave a shard unregistered (or set flag to `false`) to hold it without breaking anything:

```python
# 🔴 Planned — credentials not yet available
# if _enabled("MY_SYSTEM"):
#     my_system.register(mcp)
```

---

## Local Use and Demo Guide

- See [DEMO_GUIDE.md](DEMO_GUIDE.md) for the full permission matrix, credential configuration, and live-mode setup.
- All credentials live in `nexus-mcp/.env` — no need to put them in the Claude config.
