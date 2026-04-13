"""Workday REST API adapter (lib layer)."""

from typing import Any
import httpx
from config import WorkdayConfig
from resilience import resilient_http_call, handle_404_gracefully


class WorkdayClient:
    """Low-level Workday REST client.

    Handles OAuth2 refresh-token flow and base URL composition.
    """

    def __init__(self):
        self.cfg = WorkdayConfig()
        self._token: str | None = None
        self._http = httpx.AsyncClient(timeout=30)

    async def get_token(self) -> str:
        if self._token:
            return self._token
        token_url = f"{self.cfg.base_url}/oauth2/{self.cfg.tenant}/token"
        resp = await self._http.post(
            token_url,
            data={
                "grant_type": "refresh_token",
                "refresh_token": self.cfg.refresh_token,
                "client_id": self.cfg.client_id,
                "client_secret": self.cfg.client_secret,
            },
        )
        resp.raise_for_status()
        self._token = resp.json()["access_token"]
        return self._token

    @resilient_http_call(service_name="Workday")
    async def get(self, path: str, params: dict | None = None) -> Any:
        token = await self.get_token()
        url = f"{self.cfg.base_url}/{self.cfg.tenant}{path}"
        resp = await self._http.get(
            url,
            headers={"Authorization": f"Bearer {token}"},
            params=params,
        )
        resp.raise_for_status()
        return resp.json()

    @resilient_http_call(service_name="Workday")
    async def raas(self, report_path: str, params: dict | None = None) -> list[dict]:
        token = await self.get_token()
        url = (
            f"https://services1.myworkday.com/ccx/service/customreport2/"
            f"{self.cfg.tenant}/{report_path}"
        )
        resp = await self._http.get(
            url,
            headers={"Authorization": f"Bearer {token}"},
            params={"format": "json", **(params or {})},
        )
        resp.raise_for_status()
        return resp.json().get("Report_Entry", [])

    async def close(self):
        await self._http.aclose()
