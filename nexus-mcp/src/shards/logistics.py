"""Logistics Shard — FedEx shipment tracking & shipping tools.

Status: 🔴 Red (Planned — credentials pending)
Mock:   Set USE_MOCK=true to use built-in sample data (no credentials needed).
"""

from __future__ import annotations
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "lib"))

from mcp.server.fastmcp import FastMCP
import mock_data as M

_USE_MOCK = os.getenv("USE_MOCK", "false").lower() == "true"

_client = None


def _get():
    global _client
    if _client is None:
        from fedex_client import FedExClient
        _client = FedExClient()
    return _client


def register(mcp: FastMCP) -> None:
    """Register all Logistics shard tools onto the MCP server."""

    @mcp.tool()
    async def fedex_track_shipment(tracking_number: str) -> dict:
        """Track a FedEx shipment by tracking number and return full tracking details."""
        if _USE_MOCK:
            record = M.FEDEX_TRACKING.get(tracking_number)
            if not record:
                return {"error": f"No mock tracking data for {tracking_number}",
                        "available_numbers": list(M.FEDEX_TRACKING.keys())}
            results = record.get("trackResults", [])
            return {"trackingNumber": tracking_number, "trackResults": results}
        payload = {
            "includeDetailedScans": True,
            "trackingInfo": [
                {"trackingNumberInfo": {"trackingNumber": tracking_number}}
            ],
        }
        data = await _get().post("/track/v1/trackingnumbers", payload)
        results = data.get("output", {}).get("completeTrackResults", [])
        return results[0] if results else {"error": "No tracking results found"}

    @mcp.tool()
    async def fedex_track_multiple(tracking_numbers: list[str]) -> list[dict]:
        """Track multiple FedEx shipments in one request (up to 30).

        Args:
            tracking_numbers: List of FedEx tracking numbers to query.
        """
        if _USE_MOCK:
            return [
                {"trackingNumber": tn, "trackResults": M.FEDEX_TRACKING[tn]["trackResults"]}
                if tn in M.FEDEX_TRACKING
                else {"trackingNumber": tn, "error": "Not found in mock data"}
                for tn in tracking_numbers[:30]
            ]
        payload = {
            "includeDetailedScans": True,
            "trackingInfo": [
                {"trackingNumberInfo": {"trackingNumber": tn}}
                for tn in tracking_numbers[:30]
            ],
        }
        data = await _get().post("/track/v1/trackingnumbers", payload)
        return data.get("output", {}).get("completeTrackResults", [])

    @mcp.tool()
    async def fedex_get_shipment_events(tracking_number: str) -> list[dict]:
        """Return the ordered list of scan events for a FedEx tracking number."""
        if _USE_MOCK:
            record = M.FEDEX_TRACKING.get(tracking_number)
            if not record:
                return []
            track_results = record.get("trackResults", [])
            return track_results[0].get("scanEvents", []) if track_results else []
        payload = {
            "includeDetailedScans": True,
            "trackingInfo": [
                {"trackingNumberInfo": {"trackingNumber": tracking_number}}
            ],
        }
        data = await _get().post("/track/v1/trackingnumbers", payload)
        results = data.get("output", {}).get("completeTrackResults", [])
        if not results:
            return []
        track_results = results[0].get("trackResults", [])
        return track_results[0].get("scanEvents", []) if track_results else []

    @mcp.tool()
    async def fedex_validate_address(
        street: str,
        city: str,
        state: str,
        postal: str,
        country: str = "US",
    ) -> dict:
        """Validate a shipping address with the FedEx Address Validation API."""
        if _USE_MOCK:
            return {
                "addressesToValidate": [{"address": {"streetLines": [street], "city": city,
                    "stateOrProvinceCode": state, "postalCode": postal, "countryCode": country}}],
                "output": {"resolvedAddresses": [{"classification": "RESIDENTIAL",
                    "attributes": {"PO_BOX": "false", "VALID_RESIDENTIAL": "true"},
                    "streetLinesToken": [street], "city": city.upper(),
                    "stateOrProvinceCode": state.upper(), "postalCode": postal,
                    "countryCode": country}]},
                "mock": True,
            }
        payload = {
            "addressesToValidate": [
                {
                    "address": {
                        "streetLines": [street],
                        "city": city,
                        "stateOrProvinceCode": state,
                        "postalCode": postal,
                        "countryCode": country,
                    }
                }
            ]
        }
        return await _get().post("/address/v1/addresses/resolve", payload)

    @mcp.tool()
    async def fedex_get_rates(
        origin_postal: str,
        dest_postal: str,
        weight_lb: float,
        origin_country: str = "US",
        dest_country: str = "US",
    ) -> list[dict]:
        """Get available FedEx shipping rates between two postal codes."""
        if _USE_MOCK:
            return [
                {**rate, "requestedWeight": {"units": "LB", "value": weight_lb},
                 "origin": origin_postal, "destination": dest_postal}
                for rate in M.FEDEX_RATES_SAMPLE
            ]
        from config import FedExConfig
        account = FedExConfig().account_number
        payload = {
            "accountNumber": {"value": account},
            "requestedShipment": {
                "shipper": {"address": {"postalCode": origin_postal, "countryCode": origin_country}},
                "recipient": {"address": {"postalCode": dest_postal, "countryCode": dest_country}},
                "pickupType": "DROPOFF_AT_FEDEX_LOCATION",
                "requestedPackageLineItems": [
                    {"weight": {"units": "LB", "value": weight_lb}}
                ],
            },
        }
        data = await _get().post("/rate/v1/rates/quotes", payload)
        return data.get("output", {}).get("rateReplyDetails", [])
