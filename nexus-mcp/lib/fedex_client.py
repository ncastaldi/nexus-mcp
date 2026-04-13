"""FedEx REST API adapter (lib layer)."""

from typing import Any
import httpx
from config import FedExConfig


class FedExClient:
    """Low-level FedEx Track + Ship REST client."""

    def __init__(self):
        self.cfg = FedExConfig()
        self._token: str | None = None
        self._http = httpx.AsyncClient(timeout=30)

    async def get_token(self) -> str:
        if self._token:
            return self._token
        resp = await self._http.post(
            f"{self.cfg.api_url}/oauth/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "client_credentials",
                "client_id": self.cfg.api_key,
                "client_secret": self.cfg.api_secret,
            },
        )
        resp.raise_for_status()
        self._token = resp.json()["access_token"]
        return self._token

    async def post(self, path: str, body: dict) -> Any:
        token = await self.get_token()
        resp = await self._http.post(
            f"{self.cfg.api_url}{path}",
            json=body,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "X-locale": "en_US",
            },
        )
        resp.raise_for_status()
        return resp.json()

    async def close(self):
        await self._http.aclose()
