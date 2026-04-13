"""ITSM Shard — BMC Helix Incidents, Changes, Problems & CMDB.

Status: 🔴 Red (Planned)
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
        from helix_client import HelixClient
        _client = HelixClient()
    return _client


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    async def helix_list_incidents(
        status: str | None = None,
        assignee: str | None = None,
        limit: int = 50,
    ) -> list[dict]:
        """List incidents from BMC Helix ITSM.

        Args:
            status: Filter by status e.g. 'Assigned', 'In Progress', 'Pending', 'Resolved'.
            assignee: Partial assignee name to filter on.
            limit: Maximum results to return.
        """
        if _USE_MOCK:
            results = M.HELIX_INCIDENTS
            if status:
                results = [e for e in results if e["values"].get("Status", "").lower() == status.lower()]
            if assignee:
                results = [e for e in results if assignee.lower() in (e["values"].get("Assignee") or "").lower()]
            return results[:limit]
        parts = []
        if status:
            parts.append(f"'Status' = \"{status}\"")
        if assignee:
            parts.append(f"'Assignee' LIKE \"%{assignee}%\"")
        q = " AND ".join(parts) if parts else "('Status' != \"Closed\")"
        data = await _get().get(
            "/api/arsys/v1/entry/HPD:Help%20Desk",
            params={"q": q, "limit": limit},
        )
        return data.get("entries", [])

    @mcp.tool()
    async def helix_get_incident(incident_id: str) -> dict | None:
        """Retrieve full details for a single Helix incident by its Entry ID (e.g. INC0001234)."""
        if _USE_MOCK:
            return M.HELIX_INCIDENTS_BY_ID.get(incident_id)
        return await _get().get(f"/api/arsys/v1/entry/HPD:Help%20Desk/{incident_id}")

    @mcp.tool()
    async def helix_list_changes(status: str | None = None, limit: int = 50) -> list[dict]:
        """List change requests from BMC Helix.

        Args:
            status: Optional status filter e.g. 'Draft', 'Scheduled', 'In Progress', 'Completed'.
            limit: Maximum results to return.
        """
        if _USE_MOCK:
            results = M.HELIX_CHANGES
            if status:
                results = [e for e in results if e["values"].get("Status", "").lower() == status.lower()]
            return results[:limit]
        q = f"'Status' = \"{status}\"" if status else "'Status' != \"Closed\""
        data = await _get().get(
            "/api/arsys/v1/entry/CHG:ChangeInterface_Create",
            params={"q": q, "limit": limit},
        )
        return data.get("entries", [])

    @mcp.tool()
    async def helix_get_problem(problem_id: str) -> dict | None:
        """Retrieve a Helix problem investigation ticket by ID (e.g. PRB0000456)."""
        if _USE_MOCK:
            return next(
                (e for e in M.HELIX_PROBLEMS if e["values"].get("Problem Number") == problem_id),
                None,
            )
        return await _get().get(
            f"/api/arsys/v1/entry/PBM:Problem%20Investigation/{problem_id}"
        )

    @mcp.tool()
    async def helix_search_cmdb(ci_name: str) -> list[dict]:
        """Search the BMC Helix CMDB for configuration items matching a name fragment."""
        if _USE_MOCK:
            q = ci_name.lower()
            return [e for e in M.HELIX_CMDB if q in e["values"]["Name"].lower()]
        data = await _get().get(
            "/api/arsys/v1/entry/BMC.CORE:BMC_ComputerSystem",
            params={"q": f"'Name' LIKE \"%{ci_name}%\"", "limit": 50},
        )
        return data.get("entries", [])

    @mcp.tool()
    async def helix_list_cmdb_assets(limit: int = 100) -> list[dict]:
        """List hardware assets from the BMC Helix CMDB."""
        if _USE_MOCK:
            return M.HELIX_CMDB[:limit]
        data = await _get().get(
            "/api/arsys/v1/entry/BMC.CORE:BMC_ComputerSystem",
            params={"limit": limit},
        )
        return data.get("entries", [])
