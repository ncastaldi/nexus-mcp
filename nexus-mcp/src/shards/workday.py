"""Workday Shard — Worker, Organisation & Compensation tools.

Status: 🟡 Yellow  |  WIS-009
Mock:   Set USE_MOCK=true to use built-in sample data (no credentials needed).
"""

from __future__ import annotations
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "lib"))

from mcp.server.fastmcp import FastMCP
import mock_data as M

_USE_MOCK = os.getenv("USE_MOCK", "false").lower() == "true"

_client = None


def _get():
    global _client
    if _client is None:
        from workday_client import WorkdayClient
        _client = WorkdayClient()
    return _client


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    async def workday_list_workers(limit: int = 100, offset: int = 0) -> list[dict]:
        """List workers from Workday HCM.

        Args:
            limit: Page size.
            offset: Pagination offset.
        """
        if _USE_MOCK:
            return M.WORKDAY_WORKERS[offset:offset + limit]
        data = await _get().get(
            "/staffing/v6/workers", params={"limit": limit, "offset": offset}
        )
        return data.get("data", [])

    @mcp.tool()
    async def workday_get_worker(worker_id: str) -> dict | None:
        """Retrieve full details for a single Workday worker by their Workday ID."""
        if _USE_MOCK:
            return next((w for w in M.WORKDAY_WORKERS if w["id"] == worker_id), None)
        return await _get().get(f"/staffing/v6/workers/{worker_id}")

    @mcp.tool()
    async def workday_find_worker_by_email(email: str) -> dict | None:
        """Find a Workday worker by their primary work email address."""
        if _USE_MOCK:
            return M.WORKDAY_WORKERS_BY_EMAIL.get(email.lower())
        data = await _get().get("/staffing/v6/workers", params={"limit": 500})
        for w in data.get("data", []):
            if (w.get("primaryWorkEmail") or "").lower() == email.lower():
                return w
        return None

    @mcp.tool()
    async def workday_list_positions(limit: int = 100) -> list[dict]:
        """List open and filled positions in Workday."""
        if _USE_MOCK:
            return M.WORKDAY_POSITIONS[:limit]
        data = await _get().get("/staffing/v6/positions", params={"limit": limit})
        return data.get("data", [])

    @mcp.tool()
    async def workday_get_compensation(worker_id: str) -> dict | None:
        """Retrieve compensation details (grade, salary band) for a Workday worker."""
        if _USE_MOCK:
            return M.WORKDAY_COMPENSATION.get(worker_id)
        return await _get().get(f"/compensation/v1/employees/{worker_id}")

    @mcp.tool()
    async def workday_list_organizations(limit: int = 200) -> list[dict]:
        """List supervisory organisations in Workday."""
        if _USE_MOCK:
            return M.WORKDAY_ORGANIZATIONS[:limit]
        data = await _get().get("/organization/v2/orgs", params={"limit": limit})
        return data.get("data", [])

    @mcp.tool()
    async def workday_run_raas_report(report_path: str, params: dict | None = None) -> list[dict]:
        """Execute a Workday Report-as-a-Service (RaaS) custom report.

        Args:
            report_path: Path after /ccx/service/customreport2/<tenant>/
            params: Optional extra query parameters.
        """
        if _USE_MOCK:
            return [
                {
                    "reportName": report_path,
                    "note": "Mock mode — returning synthetic report data",
                    "rows": [
                        {"employee": w["descriptor"], "department": w["primaryJob"]["businessUnit"]["descriptor"],
                         "title": w["primaryJob"]["jobProfile"]["descriptor"]}
                        for w in M.WORKDAY_WORKERS
                    ],
                }
            ]
        return await _get().raas(report_path, params)
