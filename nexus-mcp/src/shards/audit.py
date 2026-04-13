"""Audit Shard - cross-system drift detection and weekly reporting.

Status: Green
Mock: Set USE_MOCK=true to use built-in sample data (no credentials needed).
"""

from __future__ import annotations
import asyncio
import sys
import os
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "lib"))

from mcp.server.fastmcp import FastMCP
from drift_detection import (
    scan_department_drift,
    scan_job_title_mismatches,
    scan_name_variance,
    scan_status_reconciliation_mismatches,
)

_USE_MOCK = os.getenv("USE_MOCK", "false").lower() == "true"

def register(mcp: FastMCP) -> None:
    """Register all Audit shard tools onto the MCP server."""

    @mcp.tool()
    async def scan_status_reconciliation() -> dict:
        """Detect workers terminated in Workday but still enabled in Active Directory.
        
        Returns a report with scan_summary (total checked, mismatches found, status)
        and mismatches array with employee details.
        Severity: HIGH - represents potential security risk.
        """
        return scan_status_reconciliation_mismatches()

    @mcp.tool()
    async def scan_job_title_drift() -> dict:
        """Detect workers whose job title in Workday differs from their Active Directory title.
        
        Returns a report with scan_summary and mismatches array.
        Severity: MEDIUM - may indicate stale AD attributes.
        """
        return scan_job_title_mismatches()

    @mcp.tool()
    async def scan_department_mismatches() -> dict:
        """Detect workers whose department in Workday differs from their Active Directory department.
        
        Returns a report with scan_summary and mismatches array including cost center details.
        Severity: MEDIUM - may cause reporting or access control issues.
        """
        return scan_department_drift()

    @mcp.tool()
    async def scan_name_variance_mismatches() -> dict:
        """Detect AD display names that don't align with legal or preferred names in Workday.
        
        Compares first/last name tokens (normalized) between Workday legal name,
        preferred name, and AD display name.
        Returns a report with scan_summary and mismatches array.
        Severity: LOW - cosmetic issue but may cause confusion for users.
        """
        return scan_name_variance()
