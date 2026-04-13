"""Audit Shard - cross-system drift detection and weekly reporting.

Status: Yellow
Mock: Set USE_MOCK=true to use built-in sample data (no credentials needed).
"""

from __future__ import annotations
import asyncio
import sys
import os
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "lib"))

from mcp.server.fastmcp import FastMCP

_USE_MOCK = os.getenv("USE_MOCK", "false").lower() == "true"

def register(mcp: FastMCP) -> None:
    """Register all Audit shard tools onto the MCP server."""
    pass
