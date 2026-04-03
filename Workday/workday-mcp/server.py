from mcp.server.fastmcp import FastMCP
from typing import Any

# This stays the same - it's your server's identity
mcp = FastMCP("Workday-Sync")

# Mock dataset with reporting-line relationships for manager checks (WIS-017 prep)
MOCK_WORKERS: dict[str, dict[str, str]] = {
    "EMP001": {
        "name": "Nathan",
        "status": "Active",
        "dept": "IT",
        "email": "nathan@example.com",
        "manager_id": "EMP010",
    },
    "EMP002": {
        "name": "Terminated User",
        "status": "Terminated",
        "dept": "Sales",
        "email": "user2@example.com",
        "manager_id": "EMP020",
    },
    "EMP003": {
        "name": "Alicia",
        "status": "Active",
        "dept": "IT",
        "email": "alicia@example.com",
        "manager_id": "EMP010",
    },
    "EMP004": {
        "name": "Jordan",
        "status": "Leave",
        "dept": "Finance",
        "email": "jordan@example.com",
        "manager_id": "EMP030",
    },
    "EMP010": {
        "name": "Priya Manager",
        "status": "Active",
        "dept": "IT",
        "email": "priya@example.com",
        "manager_id": "EMP100",
    },
    "EMP020": {
        "name": "Ramon Director",
        "status": "Active",
        "dept": "Sales",
        "email": "ramon@example.com",
        "manager_id": "EMP100",
    },
    "EMP030": {
        "name": "Morgan Lead",
        "status": "Active",
        "dept": "Finance",
        "email": "morgan@example.com",
        "manager_id": "EMP100",
    },
    "EMP100": {
        "name": "Chief Exec",
        "status": "Active",
        "dept": "Executive",
        "email": "ceo@example.com",
        "manager_id": "",
    },
    # Intentional unresolved manager reference for mismatch test scenarios
    "EMP777": {
        "name": "Mismatch Case",
        "status": "Active",
        "dept": "Operations",
        "email": "mismatch@example.com",
        "manager_id": "EMP999",
    },
}

@mcp.tool()
def get_worker_status(employee_id: str) -> dict[str, Any]:
    """
    WIS-009: Fetch structured worker status.
    This replaces the previous string-based version.
    """
    worker_id = employee_id.upper()
    worker = MOCK_WORKERS.get(worker_id)

    # Structured Return (WIS-004 Allowlist)
    if worker:
        return {
            "employee_id": worker_id,
            "full_name": worker["name"],
            "status": worker["status"],
            "department": worker["dept"],
            "work_email": worker["email"],
            "manager_id": worker["manager_id"],
        }

    return {"error": f"Worker {employee_id} not found."}


@mcp.tool()
def get_worker_manager(employee_id: str) -> dict[str, Any]:
    """WIS-017 prep: resolve a worker's manager relationship from mock data."""
    worker_id = employee_id.upper()
    worker = MOCK_WORKERS.get(worker_id)
    if not worker:
        return {"error": f"Worker {employee_id} not found."}

    manager_id = worker.get("manager_id", "")
    if not manager_id:
        return {
            "employee_id": worker_id,
            "employee_name": worker["name"],
            "manager_id": "",
            "manager_name": None,
            "relationship_status": "no_manager_assigned",
        }

    manager = MOCK_WORKERS.get(manager_id)
    if not manager:
        return {
            "employee_id": worker_id,
            "employee_name": worker["name"],
            "manager_id": manager_id,
            "manager_name": None,
            "relationship_status": "manager_not_found",
        }

    return {
        "employee_id": worker_id,
        "employee_name": worker["name"],
        "manager_id": manager_id,
        "manager_name": manager["name"],
        "relationship_status": "ok",
    }

if __name__ == "__main__":
    mcp.run()