"""Nexus-MCP — Core Orchestrator (src/main.py).

This is the only file that decides WHAT loads. Each shard is self-contained.
To enable a shard: set its ENABLE_* flag to "true" in .env or the environment.
To put a shard in holding pattern: set it to "false" or omit the variable.

Shard status legend used in WIS tracking:
  🟢 Green  — Production-ready, enabled by default
  🟡 Yellow — In progress / partially ready
  🔴 Red    — Planned, not yet registered (keep import commented out)

SOC 2 audit middleware (CC7.2 / CC6.1) is applied automatically after all
shards load — every registered tool is wrapped with a structured JSONL logger.
No shard code needs to know about it.
"""

import asyncio
import functools
import os
import sys
import time
import uuid

# Fix Windows console encoding for emoji support
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Make lib/ importable from shards and main alike
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_root, "lib"))
sys.path.insert(0, os.path.join(_root, "src"))

from dotenv import load_dotenv
load_dotenv(os.path.join(_root, ".env"))

from mcp.server.fastmcp import FastMCP
from shards import identity, workday, itsm, assets, logistics, audit, reports

# ── Build the server ──────────────────────────────────────────────────────────

mcp = FastMCP(
    name="Nexus",
    instructions=(
        "Nexus is the enterprise integration MCP. You have access to identity "
        "(AD + Entra), workforce (Workday), ITSM (BMC Helix), asset inventory "
        "(Lansweeper + Intune), logistics (FedEx), and cross-system audit tools. "
        "Use audit_* tools to detect field drift. Use generate_* tools for weekly reports."
    ),
)


def _enabled(flag: str, default: str = "true") -> bool:
    """Return True if the ENABLE_<flag> environment variable is truthy."""
    return os.getenv(f"ENABLE_{flag}", default).strip().lower() == "true"


# ── Shard loading ─────────────────────────────────────────────────────────────
# Each block is independent. Comment out a block to put that shard in "holding
# pattern" without touching any other file.

# 🟢 Identity — Active Directory + Entra ID (WIS-017)
if _enabled("IDENTITY"):
    identity.register(mcp)
    print("[nexus] ✅ identity shard loaded")
else:
    print("[nexus] ⏸  identity shard disabled (ENABLE_IDENTITY != true)")

# 🟡 Workday — Worker & Org tools (WIS-009)
if _enabled("WORKDAY"):
    workday.register(mcp)
    print("[nexus] ✅ workday shard loaded")
else:
    print("[nexus] ⏸  workday shard disabled (ENABLE_WORKDAY != true)")

# 🔴 ITSM — BMC Helix (Planned)
if _enabled("ITSM"):
    itsm.register(mcp)
    print("[nexus] ✅ itsm shard loaded")
else:
    print("[nexus] ⏸  itsm shard disabled (ENABLE_ITSM != true)")

# 🔴 Assets — Lansweeper + Intune (Planned)
if _enabled("ASSETS"):
    assets.register(mcp)
    print("[nexus] ✅ assets shard loaded")
else:
    print("[nexus] ⏸  assets shard disabled (ENABLE_ASSETS != true)")

# 🔴 Logistics — FedEx (Planned — credentials pending)
if _enabled("LOGISTICS"):
    logistics.register(mcp)
    print("[nexus] ✅ logistics shard loaded")
else:
    print("[nexus] ⏸  logistics shard disabled (ENABLE_LOGISTICS != true)")

# 🟡 Audit — Cross-system drift + reporting
if _enabled("AUDIT"):
    audit.register(mcp)
    print("[nexus] ✅ audit shard loaded")
else:
    print("[nexus] ⏸  audit shard disabled (ENABLE_AUDIT != true)")

# 🟢 Reports — save_report tool for persisting large outputs (WIS-TBD)
if _enabled("REPORTS"):
    reports.register(mcp)
    print("[nexus] ✅ reports shard loaded")
else:
    print("[nexus] ⏸  reports shard disabled (ENABLE_REPORTS != true)")


# ── SOC 2 Audit Middleware (CC7.2 / CC6.1) ───────────────────────────────────
# Applied AFTER all shards register so every tool — regardless of which shard
# it came from — is wrapped in one place. Shards are completely unaware of it.
#
# Each wrapper:
#   1. Generates a UUID v4 event_id for correlation
#   2. Calls the original tool function (async or sync)
#   3. Records status, latency_ms, and (on failure) sanitised error details
#   4. Appends a JSONL entry to AUDIT_LOG_FILE (default: logs/nexus_audit.jsonl)
#   5. Optionally mirrors the entry to stderr for SIEM / syslog forwarding
#
# To disable audit logging: set AUDIT_LOGGING_ENABLED=false in .env
# To silence stderr output: set AUDIT_LOG_STDERR=false in .env

from config import AuditConfig
from audit_log import AuditLogger

_audit_cfg = AuditConfig()

if _audit_cfg.enabled:
    _auditor = AuditLogger.get()

    def _make_audited_wrapper(orig_fn, tool_name: str):
        """Return an async wrapper that logs every invocation of *orig_fn*."""
        @functools.wraps(orig_fn)
        async def _audited(**kwargs):
            event_id = str(uuid.uuid4())
            t0 = time.monotonic()
            try:
                if asyncio.iscoroutinefunction(orig_fn):
                    result = await orig_fn(**kwargs)
                else:
                    result = orig_fn(**kwargs)
                latency_ms = int((time.monotonic() - t0) * 1000)
                _auditor.record_success(event_id, tool_name, kwargs, latency_ms)
                return result
            except Exception as exc:
                latency_ms = int((time.monotonic() - t0) * 1000)
                _auditor.record_error(event_id, tool_name, kwargs, latency_ms, exc)
                raise
        return _audited

    _wrapped = 0
    for _tool_name, _tool_obj in mcp._tool_manager._tools.items():
        _tool_obj.fn = _make_audited_wrapper(_tool_obj.fn, _tool_name)
        _wrapped += 1

    print(f"[nexus] 🔒 SOC 2 audit middleware active — {_wrapped} tools wrapped"
          f" → {_audit_cfg.log_file}")
else:
    print("[nexus] ⚠️  SOC 2 audit middleware DISABLED (AUDIT_LOGGING_ENABLED=false)")


# ── Built-in audit query tools ────────────────────────────────────────────────
# Two additional MCP tools that let an authorised Claude session query the
# audit log directly — useful for compliance reviews and spot-checks.
# These are always registered (they do not require a shard flag).

from audit_log import tail_audit_log, audit_log_stats as _log_stats_fn


@mcp.tool()
async def nexus_audit_recent(n: int = 50) -> list[dict]:
    """Return the last *n* entries from the Nexus-MCP SOC 2 audit log.

    Each entry contains: event_id, timestamp, tool, shard, action_category,
    args_summary (redacted), mock_mode, status, latency_ms, error details.
    Default n=50; max recommended 500.
    """
    from config import AuditConfig
    return tail_audit_log(n=min(n, 500), log_file=AuditConfig().log_file)


@mcp.tool()
async def nexus_audit_stats() -> dict:
    """Return summary statistics over the entire Nexus-MCP audit log.

    Includes: total call count, status breakdown (success/error), shard
    breakdown, action_category breakdown, top-10 tools by call volume,
    error count, recent errors, and mock-mode call count.
    """
    from config import AuditConfig
    return _log_stats_fn(log_file=AuditConfig().log_file)


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
