"""Microsoft Entra ID (Graph API) adapter (lib layer)."""

from typing import Any
import httpx
import msal
from config import EntraConfig

GRAPH_BASE = "https://graph.microsoft.com/v1.0"
GRAPH_BETA = "https://graph.microsoft.com/beta"


class EntraClient:
    """Low-level Microsoft Graph client for Entra ID.

    Handles token acquisition and pagination transparently.
    """

    def __init__(self):
        self.cfg = EntraConfig()
        self._app: msal.ConfidentialClientApplication | None = None
        self._http = httpx.AsyncClient(timeout=30)

    def _get_app(self) -> msal.ConfidentialClientApplication:
        if self._app is None:
            self._app = msal.ConfidentialClientApplication(
                self.cfg.client_id,
                authority=f"https://login.microsoftonline.com/{self.cfg.tenant_id}",
                client_credential=self.cfg.client_secret,
            )
        return self._app

    async def get_token(self) -> str:
        app = self._get_app()
        result = app.acquire_token_silent(
            ["https://graph.microsoft.com/.default"], account=None
        )
        if not result:
            result = app.acquire_token_for_client(
                scopes=["https://graph.microsoft.com/.default"]
            )
        if "access_token" not in result:
            raise RuntimeError(f"MSAL token error: {result.get('error_description')}")
        return result["access_token"]

    async def get(self, path: str, params: dict | None = None, beta: bool = False) -> Any:
        token = await self.get_token()
        base = GRAPH_BETA if beta else GRAPH_BASE
        resp = await self._http.get(
            f"{base}{path}",
            headers={"Authorization": f"Bearer {token}"},
            params=params,
        )
        resp.raise_for_status()
        return resp.json()

    async def get_all_pages(self, path: str, params: dict | None = None) -> list[dict]:
        results: list[dict] = []
        data = await self.get(path, params)
        results.extend(data.get("value", []))
        while "@odata.nextLink" in data:
            token = await self.get_token()
            resp = await self._http.get(
                data["@odata.nextLink"],
                headers={"Authorization": f"Bearer {token}"},
            )
            resp.raise_for_status()
            data = resp.json()
            results.extend(data.get("value", []))
        return results

    async def close(self):
        await self._http.aclose()
