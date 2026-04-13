"""Assets Shard — Lansweeper IT inventory + Microsoft Intune device management.

Status: 🔴 Red (Planned)
Mock:   Set USE_MOCK=true to use built-in sample data (no credentials needed).
"""

from __future__ import annotations
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "lib"))

from mcp.server.fastmcp import FastMCP
import mock_data as M

_USE_MOCK = os.getenv("USE_MOCK", "false").lower() == "true"

_ls = None
_intune = None


def _get_ls():
    global _ls
    if _ls is None:
        from lansweeper_client import LansweeperClient
        _ls = LansweeperClient()
    return _ls


def _get_intune():
    global _intune
    if _intune is None:
        from intune_client import IntuneClient
        _intune = IntuneClient()
    return _intune


def _site_id() -> str:
    from config import LansweeperConfig
    return LansweeperConfig().site_id


def register(mcp: FastMCP) -> None:
    """Register all Assets shard tools onto the MCP server."""

    # ── Lansweeper ─────────────────────────────────────────────────────────────

    @mcp.tool()
    async def lansweeper_list_assets(limit: int = 100, asset_type: str | None = None) -> list[dict]:
        """List assets from Lansweeper.

        Args:
            limit: Maximum number of assets to return.
            asset_type: Optional type filter e.g. 'Windows', 'Linux', 'Network Device'.
        """
        if _USE_MOCK:
            results = M.LANSWEEPER_ASSETS
            if asset_type:
                results = [a for a in results if a["assetType"].lower() == asset_type.lower()]
            return results[:limit]
        filter_part = f'assetType: "{asset_type}"' if asset_type else ""
        query = f"""
        query GetAssets($siteId: String!, $limit: Int!) {{
          site(id: $siteId) {{
            assetResources(
              pagination: {{ limit: $limit, page: 1 }}
              {filter_part}
            ) {{
              items {{
                assetId assetName assetType ipAddress mac lastSeen
                lastLoggedOnUser operatingSystem domain manufacturer model serialNumber
                custom1 custom2 custom3 custom4
              }}
            }}
          }}
        }}
        """
        data = await _get_ls().gql(query, {"siteId": _site_id(), "limit": limit})
        return data["site"]["assetResources"]["items"]

    @mcp.tool()
    async def lansweeper_get_asset(asset_id: str) -> dict | None:
        """Retrieve full details for a single Lansweeper asset by its ID."""
        if _USE_MOCK:
            return M.LANSWEEPER_ASSETS_BY_ID.get(asset_id)
        query = """
        query GetAsset($siteId: String!, $assetId: String!) {
          site(id: $siteId) {
            asset(assetId: $assetId) {
              assetId assetName assetType ipAddress mac lastSeen
              lastLoggedOnUser operatingSystem domain manufacturer model serialNumber
              custom1 custom2 custom3 custom4 warrantyDate purchaseDate
            }
          }
        }
        """
        data = await _get_ls().gql(query, {"siteId": _site_id(), "assetId": asset_id})
        return data["site"]["asset"]

    @mcp.tool()
    async def lansweeper_get_software(asset_id: str) -> list[dict]:
        """List all installed software on a given Lansweeper asset."""
        if _USE_MOCK:
            return M.LANSWEEPER_SOFTWARE.get(asset_id, [])
        query = """
        query GetSoftware($siteId: String!, $assetId: String!) {
          site(id: $siteId) {
            asset(assetId: $assetId) {
              software { name version publisher installDate }
            }
          }
        }
        """
        data = await _get_ls().gql(query, {"siteId": _site_id(), "assetId": asset_id})
        return data["site"]["asset"]["software"]

    @mcp.tool()
    async def lansweeper_search_assets(query: str, limit: int = 50) -> list[dict]:
        """Search Lansweeper assets by name, IP address, or serial number fragment."""
        if _USE_MOCK:
            q = query.lower()
            return [a for a in M.LANSWEEPER_ASSETS if q in a["assetName"].lower()][:limit]
        gql_query = """
        query SearchAssets($siteId: String!, $query: String!, $limit: Int!) {
          site(id: $siteId) {
            assetResources(
              pagination: { limit: $limit, page: 1 }
              assetBasicFilters: { assetName: $query }
            ) {
              items {
                assetId assetName assetType ipAddress mac lastSeen
                lastLoggedOnUser operatingSystem domain
              }
            }
          }
        }
        """
        data = await _get_ls().gql(gql_query, {
            "siteId": _site_id(),
            "query": query,
            "limit": limit,
        })
        return data["site"]["assetResources"]["items"]

    # ── Intune ─────────────────────────────────────────────────────────────────

    @mcp.tool()
    async def intune_list_managed_devices(limit: int = 100) -> list[dict]:
        """List all managed devices enrolled in Microsoft Intune."""
        if _USE_MOCK:
            return M.INTUNE_DEVICES[:limit]
        fields = (
            "id,deviceName,operatingSystem,osVersion,complianceState,"
            "managementState,enrolledDateTime,lastSyncDateTime,deviceType,"
            "userPrincipalName,manufacturer,model,serialNumber,"
            "isEncrypted,azureADRegistered,azureADDeviceId"
        )
        data = await _get_intune().get(
            "/deviceManagement/managedDevices",
            params={"$select": fields, "$top": min(limit, 1000)},
        )
        return data.get("value", [])

    @mcp.tool()
    async def intune_get_managed_device(device_id: str) -> dict | None:
        """Retrieve full details for a single Intune managed device by its device ID or name."""
        if _USE_MOCK:
            return (
                M.INTUNE_DEVICES_BY_ID.get(device_id)
                or M.INTUNE_DEVICES_BY_NAME.get(device_id.lower())
            )
        return await _get_intune().get(f"/deviceManagement/managedDevices/{device_id}")

    @mcp.tool()
    async def intune_get_noncompliant_devices() -> list[dict]:
        """Return all Intune devices currently in a non-compliant state."""
        if _USE_MOCK:
            return [d for d in M.INTUNE_DEVICES if d["complianceState"] == "noncompliant"]
        data = await _get_intune().get(
            "/deviceManagement/managedDevices",
            params={"$filter": "complianceState eq 'noncompliant'"},
        )
        return data.get("value", [])

    @mcp.tool()
    async def intune_list_compliance_policies() -> list[dict]:
        """List device compliance policies configured in Intune."""
        if _USE_MOCK:
            return M.INTUNE_COMPLIANCE_POLICIES
        data = await _get_intune().get("/deviceManagement/deviceCompliancePolicies")
        return data.get("value", [])

    @mcp.tool()
    async def intune_list_configuration_profiles() -> list[dict]:
        """List device configuration profiles in Intune."""
        if _USE_MOCK:
            return M.INTUNE_CONFIGURATION_PROFILES
        data = await _get_intune().get("/deviceManagement/deviceConfigurations")
        return data.get("value", [])

    @mcp.tool()
    async def intune_list_apps(limit: int = 100) -> list[dict]:
        """List managed applications deployed via Intune."""
        if _USE_MOCK:
            return M.INTUNE_APPS[:limit]
        data = await _get_intune().get(
            "/deviceManagement/deviceAppManagement/mobileApps",
            params={"$top": min(limit, 1000)},
        )
        return data.get("value", [])

    @mcp.tool()
    async def intune_get_autopilot_devices() -> list[dict]:
        """List Windows Autopilot device registrations in Intune."""
        if _USE_MOCK:
            return M.INTUNE_AUTOPILOT_DEVICES
        data = await _get_intune().get(
            "/deviceManagement/windowsAutopilotDeviceIdentities"
        )
        return data.get("value", [])
