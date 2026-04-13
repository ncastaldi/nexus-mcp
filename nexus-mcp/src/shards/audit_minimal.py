"""Audit Shard - cross-system content drift detection and weekly reporting.

Status: Yellow  
Mock: Set USE_MOCK=true to use built-in sample data (no credentials needed).
"""

from __future__ import annotations
import asyncio
import datetime
import json
import sys
import os
from pathlib import Path
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "lib"))

from mcp.server.fastmcp import FastMCP
import mock_data as M
from config import WorkdayConfig, entra_config, ADConfig, IntegrationsConfig, DEVELOPMENTConfig, LansweeperConfig, HelixConfig, FedexConfig
from schemas import WorkdayWorker, ADUser, EntraUser, DeviceComparison, FieldDrift, HealthCheck
from workday_client import WorkdayClient
from entra_client import EntraClient
from ad_adapter import ADAdapter
from intune_client import IntuneClient
from lansweeper_client import LansweeperClient
from helix_client import HelixClient
from audit_log import AuditLog

_USE_MOCK = os.getenv("USE_MOCK", "false").lower() == "true"
_audit_log = AuditLog()

# Client singletons
_wd_client: WorkdayClient | None = None
_entra_client: EntraClient | None = None
_ad_adapter: ADAdapter | None = None
_intune_client: IntuneClient | None = None
_ls_client: LansweeperClient | None = None
_helix_client: HelixClient | None = None

def _get_wd() -> WorkdayClient:
    global _wd_client
    if not _wd_client:
        _wd_client = WorkdayClient()
    return _wd_client

def _get_entra() -> EntraClient:
    global _entra_client
    if not _entra_client:
        _entra_client = EntraClient()
    return _entra_client

def _get_ad() -> ADAdapter:
    global _ad_adapter
    if not _ad_adapter:
        _ad_adapter = ADAdapter()
    return _ad_adapter

def _get_intune() -> IntuneClient:
    global _intune_client
    if not _intune_client:
        _intune_client = IntuneClient()
    return _intune_client

def _get_ls() -> LansweeperClient:
    global _ls_client
    if not _ls_client:
        _ls_client = LansweeperClient()
    return _ls_client

def _get_helix() -> HelixClient:
    global _helix_client
    if not _helix_client:
        _helix_client = HelixClient()
    return _helix_client

def _norm(val: Any) -> str:
    """Normalize value to lowercase string for comparison."""
    if val is None:
        return ""
    return str(val).lower().strip()

def register(mcp: FastMCP) -> None:
    """Register all Audit shard tools onto the MCP server."""
    pass
