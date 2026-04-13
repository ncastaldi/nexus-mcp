"""BMC Helix ITSM REST API adapter (lib layer)."""

from typing import Any
import httpx
from config import HelixConfig
from resilience import resilient_http_call


class HelixClient:
    """Low-level BMC Helix REST client.

    Handles AR-JWT token acquisition.
    """

    def __init__(self):
        self.cfg = HelixConfig()
        self._token: str | None = None
        self._http = httpx.AsyncClient(timeout=30)

    async def get_token(self) -> str:
        if self._token:
            return self._token
        resp = await self._http.post(
            f"{self.cfg.base_url}/api/jwt/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={"username": self.cfg.username, "password": self.cfg.password},
        )
        resp.raise_for_status()
        self._token = resp.text.strip()
        return self._token

    @resilient_http_call(service_name="Helix")
    async def get(self, path: str, params: dict | None = None) -> Any:
        token = await self.get_token()
        resp = await self._http.get(
            f"{self.cfg.base_url}{path}",
            headers={"Authorization": f"AR-JWT {token}"},
            params=params,
        )
        resp.raise_for_status()
        return resp.json()

    @resilient_http_call(service_name="Helix")
    async def post(self, path: str, body: dict) -> Any:
        token = await self.get_token()
        resp = await self._http.post(
            f"{self.cfg.base_url}{path}",
            headers={"Authorization": f"AR-JWT {token}", "Content-Type": "application/json"},
            json=body,
        )
        resp.raise_for_status()
        return resp.json()

    async def close(self):
        await self._http.aclose()
