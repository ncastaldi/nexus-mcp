"""Nexus-MCP SOC 2 Audit Logger.

Implements:
  CC7.2  — System Monitoring (every tool call recorded)
  CC6.1  — Logical Access Controls (action_category per call)
  PI1.4  — Processing Integrity: completeness (pre/post logging)
  PI1.5  — Processing Integrity: accuracy (mock_mode flag)
  A1.1   — Availability monitoring (latency_ms per call)

Log format: newline-delimited JSON (JSONL) — one event object per line.
The file is opened in append mode; existing lines are never modified.
That property, combined with file-system ACL controls, provides the
tamper-evident quality required by SOC 2 auditors.

Log entry schema v1:
  event_id        str   — UUID v4; globally unique per invocation
  timestamp       str   — ISO 8601 UTC with microsecond precision
  schema_version  str   — "1" (increment on breaking schema changes)
  source          str   — always "nexus-mcp"
  tool            str   — MCP tool name, e.g. "ad_get_user"
  shard           str   — domain: identity | workday | itsm | assets | logistics | audit
  action_category str   — READ | AUDIT | REPORT  (CC6.1 logical access label)
  args_summary    dict  — call arguments with sensitive values replaced by **REDACTED**
  mock_mode       bool  — True when USE_MOCK=true (no real system data accessed)
  status          str   — "success" | "error"
  latency_ms      int   — wall-clock duration in milliseconds
  error_type      str?  — exception class name; null on success
  error_message   str?  — sanitised error text; null on success
"""

from __future__ import annotations

import json
import logging
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ── Sensitive field redaction ─────────────────────────────────────────────────
# Any argument key whose name contains one of these substrings has its value
# replaced with **REDACTED** before the entry is written to disk.

_REDACT_SUBSTRINGS: frozenset[str] = frozenset({
    "password", "passwd", "secret", "token",
    "api_key", "apikey", "access_key", "private_key",
    "credential", "credentials", "auth", "authorization",
    "ssn", "dob", "date_of_birth", "birth",
    "card", "cvv", "pin", "account_number",
})


def _should_redact(key: str) -> bool:
    k = key.lower()
    return any(s in k for s in _REDACT_SUBSTRINGS)


def _redact(args: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of *args* with sensitive values replaced by **REDACTED**."""
    out: dict[str, Any] = {}
    for k, v in args.items():
        if _should_redact(k):
            out[k] = "**REDACTED**"
        elif isinstance(v, dict):
            out[k] = _redact(v)
        elif isinstance(v, list) and v and isinstance(v[0], dict):
            out[k] = [_redact(i) if isinstance(i, dict) else i for i in v]
        else:
            out[k] = v
    return out


# ── Shard inference ───────────────────────────────────────────────────────────

_SHARD_PREFIXES: list[tuple[tuple[str, ...], str]] = [
    (("ad_", "entra_"), "identity"),
    (("workday_",), "workday"),
    (("helix_",), "itsm"),
    (("lansweeper_", "intune_"), "assets"),
    (("fedex_",), "logistics"),
    (("audit_", "generate_"), "audit"),
]


def _infer_shard(tool_name: str) -> str:
    for prefixes, shard in _SHARD_PREFIXES:
        if any(tool_name.startswith(p) for p in prefixes):
            return shard
    return "unknown"


# ── Action category inference (CC6.1) ─────────────────────────────────────────
# Logical access categories tell auditors what class of operation was performed.

_AUDIT_PREFIXES: tuple[str, ...] = ("audit_",)
_REPORT_PREFIXES: tuple[str, ...] = ("generate_",)


def _infer_action_category(tool_name: str) -> str:
    if any(tool_name.startswith(p) for p in _AUDIT_PREFIXES):
        return "AUDIT"
    if any(tool_name.startswith(p) for p in _REPORT_PREFIXES):
        return "REPORT"
    return "READ"


# ── AuditLogger ───────────────────────────────────────────────────────────────

class AuditLogger:
    """Thread-safe, append-only SOC 2 audit logger.

    Writes one JSONL record per tool invocation to *log_file*.
    When *log_to_stderr* is True it also emits the same JSON to stderr
    so the record flows into systemd / CloudWatch / SIEM without a sidecar.
    """

    _instance: AuditLogger | None = None

    def __init__(self, log_file: Path | None = None, log_to_stderr: bool | None = None) -> None:
        if log_file is None:
            from config import AuditConfig  # lazy — avoids circular import at module level
            cfg = AuditConfig()
            log_file = cfg.log_file
            if log_to_stderr is None:
                log_to_stderr = cfg.log_to_stderr

        self._log_file = Path(log_file)
        self._log_to_stderr = bool(log_to_stderr)
        self._mock_mode: bool = os.getenv("USE_MOCK", "false").lower() == "true"

        self._log_file.parent.mkdir(parents=True, exist_ok=True)

        self._stderr_logger = logging.getLogger("nexus.audit")
        if not self._stderr_logger.handlers:
            handler = logging.StreamHandler(sys.stderr)
            handler.setFormatter(logging.Formatter("%(message)s"))
            self._stderr_logger.addHandler(handler)
            self._stderr_logger.propagate = False
        self._stderr_logger.setLevel(logging.INFO)

    # ── Public API ────────────────────────────────────────────────────────────

    def record(
        self,
        *,
        event_id: str,
        tool: str,
        args: dict[str, Any],
        status: str,
        latency_ms: int,
        error_type: str | None = None,
        error_message: str | None = None,
    ) -> None:
        """Write one audit record.  Called by the middleware after every tool call."""
        entry = {
            "event_id": event_id,
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="microseconds"),
            "schema_version": "1",
            "source": "nexus-mcp",
            "tool": tool,
            "shard": _infer_shard(tool),
            "action_category": _infer_action_category(tool),
            "args_summary": _redact(args),
            "mock_mode": self._mock_mode,
            "status": status,
            "latency_ms": latency_ms,
            "error_type": error_type,
            "error_message": error_message,
        }
        line = json.dumps(entry, default=str)
        with open(self._log_file, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
        if self._log_to_stderr:
            self._stderr_logger.info(line)

    # ── Convenience helpers ────────────────────────────────────────────────────

    def record_success(self, event_id: str, tool: str, args: dict, latency_ms: int) -> None:
        self.record(event_id=event_id, tool=tool, args=args,
                    status="success", latency_ms=latency_ms)

    def record_error(self, event_id: str, tool: str, args: dict, latency_ms: int,
                     exc: Exception) -> None:
        self.record(
            event_id=event_id, tool=tool, args=args,
            status="error", latency_ms=latency_ms,
            error_type=type(exc).__name__,
            error_message=_sanitise_error(str(exc)),
        )

    # ── Singleton accessor ────────────────────────────────────────────────────

    @classmethod
    def get(cls) -> AuditLogger:
        """Return the process-wide singleton (created on first call)."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


def _sanitise_error(msg: str) -> str:
    """Strip anything that looks like a credential or token from an error string."""
    import re
    msg = re.sub(r"(password|secret|token|key)\s*[=:]\s*\S+",
                 r"\1=**REDACTED**", msg, flags=re.IGNORECASE)
    return msg[:500]


# ── Audit log reader (for compliance queries) ─────────────────────────────────

def tail_audit_log(n: int = 100, log_file: Path | None = None) -> list[dict]:
    """Return the last *n* audit log entries as parsed dicts.

    Useful for building internal compliance dashboards or spot-checks.
    """
    if log_file is None:
        from config import AuditConfig
        log_file = AuditConfig().log_file
    if not Path(log_file).exists():
        return []
    with open(log_file, encoding="utf-8") as fh:
        lines = fh.readlines()
    return [json.loads(l) for l in lines[-n:] if l.strip()]


def audit_log_stats(log_file: Path | None = None) -> dict:
    """Summarise the audit log — total calls, errors, tool frequency.

    Returns a dict suitable for feeding into a compliance dashboard.
    """
    entries = tail_audit_log(n=100_000, log_file=log_file)
    if not entries:
        return {"total_entries": 0}

    from collections import Counter
    tools = Counter(e["tool"] for e in entries)
    statuses = Counter(e["status"] for e in entries)
    shards = Counter(e["shard"] for e in entries)
    categories = Counter(e["action_category"] for e in entries)
    errors = [e for e in entries if e["status"] == "error"]

    return {
        "total_entries": len(entries),
        "status_breakdown": dict(statuses),
        "shard_breakdown": dict(shards),
        "action_category_breakdown": dict(categories),
        "top_10_tools": tools.most_common(10),
        "error_count": len(errors),
        "recent_errors": [
            {"timestamp": e["timestamp"], "tool": e["tool"],
             "error_type": e["error_type"], "error_message": e["error_message"]}
            for e in errors[-10:]
        ],
        "mock_mode_calls": sum(1 for e in entries if e.get("mock_mode")),
    }
