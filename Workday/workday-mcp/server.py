from mcp.server.fastmcp import FastMCP
from typing import Any

# This stays the same - it's your server's identity
mcp = FastMCP("Workday-Sync")

@mcp.tool()
def get_worker_status(employee_id: str) -> dict[str, Any]:
    """
    WIS-009: Fetch structured worker status.
    This replaces the previous string-based version.
    """
    # 1. Mock Database (WIS-007)
    mock_workers = {
        "EMP001": {"name": "Nathan", "status": "Active", "dept": "IT", "email": "nathan@example.com"},
        "EMP002": {"name": "Terminated User", "status": "Terminated", "dept": "Sales", "email": "user2@example.com"}
    }
    
    # 2. Logic
    worker = mock_workers.get(employee_id.upper())
    
    # 3. Structured Return (WIS-004 Allowlist)
    if worker:
        return {
            "employee_id": employee_id.upper(),
            "full_name": worker["name"],
            "status": worker["status"],
            "department": worker["dept"],
            "work_email": worker["email"]
        }
    
    return {"error": f"Worker {employee_id} not found."}

if __name__ == "__main__":
    mcp.run()