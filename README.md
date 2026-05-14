# Nexus-MCP — Enterprise Integration Server

>Sharded Model Context Protocol server for enterprise systems.
>
>Each shard is self-contained and can be toggled independently via feature flags.

---

## Why This Exists

Enterprise identity data lies. A user gets promoted in Workday, but their Active Directory title doesn't update. An employee is terminated, but their Entra ID account stays enabled. A legal name change happens in HR, but AD still has the old one — quietly, for months.

These aren't edge cases. They're compliance risks, security gaps, and audit findings waiting to happen. And they're almost impossible to catch manually across three platforms.

Nexus-MCP was built to surface exactly this: identity drift between Workday HCM, Active Directory, and Entra ID — detected automatically, severity-scored, and reported before it becomes a problem.

Built on my own time. Driven by a real problem observed in a production enterprise environment.

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
