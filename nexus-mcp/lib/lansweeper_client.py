"""Lansweeper GraphQL API adapter (lib layer)."""

from typing import Any
import httpx
from config import LansweeperConfig


class LansweeperClient:
    """Low-level Lansweeper Cloud GraphQL client."""

    def __init__(self):
        self.cfg = LansweeperConfig()
        self._token: str | None = None
        self._http = httpx.AsyncClient(timeout=30)

    async def get_token(self) -> str:
        if self._token:
            return self._token
        resp = await self._http.post(
            "https://app.lansweeper.com/api/oauth/token",
            json={
                "client_id": self.cfg.application_id,
                "client_secret": self.cfg.application_secret,
                "grant_type": "client_credentials",
            },
        )
        resp.raise_for_status()
        self._token = resp.json()["access_token"]
        return self._token

    async def gql(self, query: str, variables: dict | None = None) -> Any:
        token = await self.get_token()
        resp = await self._http.post(
            self.cfg.api_url,
            json={"query": query, "variables": variables or {}},
            headers={"Authorization": f"Bearer {token}"},
        )
        resp.raise_for_status()
        payload = resp.json()
        if "errors" in payload:
            raise RuntimeError(f"Lansweeper GQL error: {payload['errors']}")
        return payload["data"]

    async def close(self):
        await self._http.aclose()
