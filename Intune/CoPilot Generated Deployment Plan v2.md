# Step‑by‑Step Guide: Building an Intune MCP Server (Phase 1 – Read‑Only)

***

## 0. What you are building (anchor this first)

From both documents, the **Intune MCP** is defined as:

> A read‑only MCP server that exposes **live Microsoft Intune device state** (inventory, compliance, ownership, last check‑in) to AI clients, using the same delivery pattern as Identity MCP. [\[wheelsinc-...epoint.com\]](https://wheelsinc-my.sharepoint.com/personal/castn1_wheels_com/Documents/Microsoft%20Copilot%20Chat%20Files/intune-mcp-prerequisites-and-checklists.md), [\[wheelsinc-...epoint.com\]](https://wheelsinc-my.sharepoint.com/personal/castn1_wheels_com/Documents/Microsoft%20Copilot%20Chat%20Files/CoPilot%20Generated%20Deployment%20Plan.md)

Key constraints (do **not** skip these):

*   **Read‑only only** in Phase 1
*   **Microsoft Graph is the backend**
*   **Stable tool contracts** (no raw Graph payloads)
*   **STDIO MCP transport**
*   **Per‑tool audit logging**
*   **No device actions yet**

***

## 1. Complete prerequisites (must be done first)

Everything in this section is taken directly from [intune-mcp-prerequisites-and-checklists.md](https://wheelsinc-my.sharepoint.com/personal/castn1_wheels_com/Documents/Microsoft%20Copilot%20Chat%20Files/intune-mcp-prerequisites-and-checklists.md?EntityRepresentationId=aab065d3-d6ce-46e8-8e59-4a042ed7b2f5). [\[wheelsinc-...epoint.com\]](https://wheelsinc-my.sharepoint.com/personal/castn1_wheels_com/Documents/Microsoft%20Copilot%20Chat%20Files/intune-mcp-prerequisites-and-checklists.md)

### 1.1 Governance & ownership

Confirm and document:

*   Product owner: Endpoint / Intune
*   Security owner
*   Operational owner (Service Desk / Endpoint Ops)
*   Approved operation list (read operations only)
*   Signed read vs write boundary

✅ **Output:** Approved Phase 1 scope document

***

### 1.2 Microsoft tenant preparation

Verify:

*   Intune tenant is healthy
*   Microsoft Graph access is approved
*   A non‑production tenant or pilot scope exists

✅ **Output:** Tenant readiness confirmation

***

### 1.3 App registration (authentication model)

Create an **Azure App Registration** for the Intune MCP:

*   Authentication:
    *   ✅ Certificate‑based auth (preferred)
    *   ⛔ Client secret (temporary only)
*   Create a **service principal**
*   Define token lifetime & rotation policy

✅ **Output:** App ID, Tenant ID, auth method documented

***

### 1.4 Microsoft Graph permissions (least privilege)

Grant **only** the following for Phase 1:

*   `DeviceManagementManagedDevices.Read.All`
*   `DeviceManagementConfiguration.Read.All` *(only if policy context is needed)*
*   `Directory.Read.All` *(only if joining user/device info)*

Admin consent must be explicitly granted and justified. [\[wheelsinc-...epoint.com\]](https://wheelsinc-my.sharepoint.com/personal/castn1_wheels_com/Documents/Microsoft%20Copilot%20Chat%20Files/intune-mcp-prerequisites-and-checklists.md)

✅ **Output:** Permission justification record

***

### 1.5 Runtime & platform

Prepare:

*   Python 3.10+
*   Dependency manager (`uv` recommended)
*   Secure secret storage (no tokens in code)
*   Logging destination (file or central sink)

✅ **Output:** Runtime ready

***

## 2. Create the MCP project scaffold

This follows the **Identity MCP replication pattern** explicitly required in the prerequisites file. [\[wheelsinc-...epoint.com\]](https://wheelsinc-my.sharepoint.com/personal/castn1_wheels_com/Documents/Microsoft%20Copilot%20Chat%20Files/intune-mcp-prerequisites-and-checklists.md)

### 2.1 Create project

```bash
mkdir intune-mcp
cd intune-mcp
uv init
uv venv
uv add "mcp[cli]" httpx
```

***

### 2.2 Create file structure

From the **Build checklist (implementation)** section: [\[wheelsinc-...epoint.com\]](https://wheelsinc-my.sharepoint.com/personal/castn1_wheels_com/Documents/Microsoft%20Copilot%20Chat%20Files/intune-mcp-prerequisites-and-checklists.md)

    intune_mcp_server.py
    intune_backend.py
    intune_graph_adapter.py
    tests/
      test_intune_adapter.py
      test_integration.py
    pyproject.toml

***

## 3. Implement the MCP server entrypoint

### 3.1 MCP server (STDIO only)

`intune_mcp_server.py`

```python
from mcp.server.fastmcp import FastMCP
from intune_backend import IntuneBackend

mcp = FastMCP("intune-mcp")
backend = IntuneBackend()

@mcp.tool()
async def intune_get_device(device_id: str):
    """Return core device metadata."""
    return await backend.get_device(device_id)

@mcp.tool()
async def intune_get_device_last_check_in(device_id: str):
    """Return last Intune check-in timestamp."""
    return await backend.get_last_check_in(device_id)

@mcp.tool()
async def intune_list_stale_devices(days: int):
    """List devices that have not checked in for N days."""
    return await backend.list_stale_devices(days)

if __name__ == "__main__":
    # STDIO transport is mandatory for safety
    mcp.run(transport="stdio")
```

This aligns with the **recommended Phase 1 tool set**. [\[wheelsinc-...epoint.com\]](https://wheelsinc-my.sharepoint.com/personal/castn1_wheels_com/Documents/Microsoft%20Copilot%20Chat%20Files/intune-mcp-prerequisites-and-checklists.md)

***

## 4. Implement backend abstraction (safe by default)

### 4.1 Backend selector

`intune_backend.py`

```python
import os
from intune_graph_adapter import GraphIntuneAdapter

class IntuneBackend:
    def __init__(self):
        backend = os.getenv("INTUNE_BACKEND", "graph")
        if backend == "graph":
            self.adapter = GraphIntuneAdapter()
        else:
            raise ValueError("Unsupported backend")

    async def get_device(self, device_id):
        return await self.adapter.get_device(device_id)

    async def get_last_check_in(self, device_id):
        return await self.adapter.get_last_check_in(device_id)

    async def list_stale_devices(self, days):
        return await self.adapter.list_stale_devices(days)
```

This matches the **environment‑based backend selection** requirement. [\[wheelsinc-...epoint.com\]](https://wheelsinc-my.sharepoint.com/personal/castn1_wheels_com/Documents/Microsoft%20Copilot%20Chat%20Files/intune-mcp-prerequisites-and-checklists.md)

***

## 5. Implement the Microsoft Graph adapter

### 5.1 Graph adapter responsibilities

From the checklist, the adapter **must**: [\[wheelsinc-...epoint.com\]](https://wheelsinc-my.sharepoint.com/personal/castn1_wheels_com/Documents/Microsoft%20Copilot%20Chat%20Files/intune-mcp-prerequisites-and-checklists.md)

*   Handle token acquisition
*   Handle throttling (429)
*   Map Graph fields → stable schemas
*   Never return raw Graph payloads

***

### 5.2 Example adapter

`intune_graph_adapter.py`

```python
import httpx
import datetime

class GraphIntuneAdapter:
    def __init__(self):
        self.base_url = "https://graph.microsoft.com/v1.0"

    async def get_device(self, device_id):
        data = await self._get(f"/deviceManagement/managedDevices/{device_id}")
        return {
            "device_id": data["id"],
            "device_name": data["deviceName"],
            "os": data["operatingSystem"],
            "owner": data.get("userPrincipalName"),
            "compliance_state": data["complianceState"],
        }

    async def get_last_check_in(self, device_id):
        data = await self._get(f"/deviceManagement/managedDevices/{device_id}")
        return {
            "device_id": data["id"],
            "last_check_in": data["lastSyncDateTime"],
        }

    async def list_stale_devices(self, days):
        cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=days)
        devices = await self._get("/deviceManagement/managedDevices")
        return [
            {
                "device_id": d["id"],
                "device_name": d["deviceName"],
                "last_check_in": d["lastSyncDateTime"],
            }
            for d in devices["value"]
            if datetime.datetime.fromisoformat(
                d["lastSyncDateTime"].replace("Z", "")
            ) < cutoff
        ]

    async def _get(self, path):
        # token acquisition omitted here by design (handled securely)
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(self.base_url + path, headers=self._headers())
            if r.status_code == 429:
                raise Exception("Graph throttling encountered")
            r.raise_for_status()
            return r.json()

    def _headers(self):
        return {"Authorization": "Bearer <token>"}
```

***

## 6. Logging and audit controls (mandatory)

From the prerequisites: [\[wheelsinc-...epoint.com\]](https://wheelsinc-my.sharepoint.com/personal/castn1_wheels_com/Documents/Microsoft%20Copilot%20Chat%20Files/intune-mcp-prerequisites-and-checklists.md)

*   **STDERR‑only logging**
*   **Per‑tool audit record**
*   **No secrets logged**

Implement:

*   tool name
*   parameters (redacted)
*   result size
*   correlation ID

✅ **Failure to do this blocks Phase 1 completion**

***

## 7. Testing gates

### 7.1 Unit tests

From the checklist: [\[wheelsinc-...epoint.com\]](https://wheelsinc-my.sharepoint.com/personal/castn1_wheels_com/Documents/Microsoft%20Copilot%20Chat%20Files/intune-mcp-prerequisites-and-checklists.md)

*   Parser behavior
*   Field mapping
*   Error handling

### 7.2 Integration tests

*   Run against **non‑production tenant**
*   Compare MCP output vs Intune portal for:
    *   compliant device
    *   non‑compliant device
    *   stale device

✅ **Output:** Test evidence retained

***

## 8. Pilot rollout

From Phase 5 checklist: [\[wheelsinc-...epoint.com\]](https://wheelsinc-my.sharepoint.com/personal/castn1_wheels_com/Documents/Microsoft%20Copilot%20Chat%20Files/intune-mcp-prerequisites-and-checklists.md)

*   Enable MCP for pilot users only
*   Validate top service desk questions:
    *   “Devices not checking in”
    *   “Devices assigned to disabled users”
*   Test rollback by disabling Graph backend

***

## 9. Definition of Done (Phase 1)

All must be true: [\[wheelsinc-...epoint.com\]](https://wheelsinc-my.sharepoint.com/personal/castn1_wheels_com/Documents/Microsoft%20Copilot%20Chat%20Files/intune-mcp-prerequisites-and-checklists.md)

*   No write tools exist
*   Stable response schemas
*   Friendly errors
*   Complete audit logs
*   Tests passing
*   Security sign‑off recorded
*   Runbook published

***

## What you have when this is finished

*   A **real MCP server**
*   Backed by **Microsoft Graph**
*   Answering **live Intune questions**
*   Safe, auditable, and production‑defensible
*   Ready for Phase 2 correlation with Identity + Inventory MCPs [\[wheelsinc-...epoint.com\]](https://wheelsinc-my.sharepoint.com/personal/castn1_wheels_com/Documents/Microsoft%20Copilot%20Chat%20Files/CoPilot%20Generated%20Deployment%20Plan.md)

***