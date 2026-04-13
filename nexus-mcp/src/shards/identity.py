"""Identity Shard — Active Directory + Microsoft Entra ID tools.

Status: 🟢 Green  |  WIS-017
Mock:   Set USE_MOCK=true to use built-in sample data (no credentials needed).
"""

from __future__ import annotations
import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "lib"))

from mcp.server.fastmcp import FastMCP
import mock_data as M
from adapters import ADUserAdapter, EntraUserAdapter
from schemas import CanonicalUser

_USE_MOCK = os.getenv("USE_MOCK", "false").lower() == "true"

_ad = None
_entra = None


def _get_ad():
    global _ad
    if _ad is None:
        from ad_adapter import ActiveDirectoryAdapter
        _ad = ActiveDirectoryAdapter()
    return _ad


def _get_entra():
    global _entra
    if _entra is None:
        from entra_client import EntraClient
        _entra = EntraClient()
    return _entra


def register(mcp: FastMCP) -> None:

    # ── Active Directory ───────────────────────────────────────────────────────

    @mcp.tool()
    async def ad_get_user(sam_account_name: str) -> dict | None:
        """Look up an Active Directory user by their sAMAccountName (login name).
        
        Returns a normalized user object with consistent field names across all systems.
        """
        if _USE_MOCK:
            ad_dict = M.AD_USERS_BY_SAM.get(sam_account_name.lower())
            if not ad_dict:
                return None
            canonical = ADUserAdapter.to_canonical(ad_dict)
            return canonical.model_dump(mode='json', exclude_none=True)
        
        ad_dict = await asyncio.to_thread(_get_ad().get_user, sam_account_name)
        if not ad_dict:
            return None
        canonical = ADUserAdapter.to_canonical(ad_dict)
        return canonical.model_dump(mode='json', exclude_none=True)

    @mcp.tool()
    async def ad_get_user_by_email(email: str) -> dict | None:
        """Look up an Active Directory user by their email address.
        
        Returns a normalized user object with consistent field names across all systems.
        """
        if _USE_MOCK:
            ad_dict = M.AD_USERS_BY_EMAIL.get(email.lower())
            if not ad_dict:
                return None
            canonical = ADUserAdapter.to_canonical(ad_dict)
            return canonical.model_dump(mode='json', exclude_none=True)
        
        ad_dict = await asyncio.to_thread(_get_ad().get_user_by_email, email)
        if not ad_dict:
            return None
        canonical = ADUserAdapter.to_canonical(ad_dict)
        return canonical.model_dump(mode='json', exclude_none=True)

    @mcp.tool()
    async def ad_search_users(query: str, limit: int = 50) -> list[dict]:
        """Search Active Directory users by display name or sAMAccountName fragment.
        
        Returns a list of normalized user objects with consistent field names.
        """
        if _USE_MOCK:
            q = query.lower()
            matches = [
                u for u in M.AD_USERS
                if q in u["displayName"].lower() or q in u["sAMAccountName"].lower()
            ]
            # Convert to canonical format
            canonical_users = [ADUserAdapter.to_canonical(u) for u in matches[:limit]]
            return [u.model_dump(mode='json', exclude_none=True) for u in canonical_users]
        
        ad_dicts = await asyncio.to_thread(_get_ad().search_users, query, limit)
        canonical_users = [ADUserAdapter.to_canonical(u) for u in ad_dicts]
        return [u.model_dump(mode='json', exclude_none=True) for u in canonical_users]

    @mcp.tool()
    async def ad_list_groups(limit: int = 200) -> list[dict]:
        """List all security and distribution groups in Active Directory."""
        if _USE_MOCK:
            return M.AD_GROUPS[:limit]
        return await asyncio.to_thread(_get_ad().get_groups, limit)

    @mcp.tool()
    async def ad_get_group_members(group_dn: str) -> list[dict]:
        """Return all members of an Active Directory group by its distinguished name."""
        if _USE_MOCK:
            group_cn = group_dn.split(",")[0].replace("CN=", "").lower()
            return [
                {"dn": u["dn"], "cn": u["cn"], "sAMAccountName": u["sAMAccountName"],
                 "mail": u["mail"], "title": u["title"]}
                for u in M.AD_USERS
                if group_cn in (u.get("memberOf") or "").lower()
            ]
        return await asyncio.to_thread(_get_ad().get_group_members, group_dn)

    @mcp.tool()
    async def ad_get_disabled_accounts() -> list[dict]:
        """Return all disabled user accounts in Active Directory.

        userAccountControl value 514 = normal account (512) + disabled (2).
        """
        if _USE_MOCK:
            return [u for u in M.AD_USERS if u.get("userAccountControl") == "514"]
        return await asyncio.to_thread(_get_ad().get_disabled_accounts)

    @mcp.tool()
    async def ad_get_stale_accounts(days_inactive: int = 90) -> list[dict]:
        """Return Active Directory accounts with no login for the given number of days.

        Args:
            days_inactive: Inactivity threshold in days (default 90).
        """
        if _USE_MOCK:
            import datetime
            cutoff = (
                datetime.datetime.utcnow() - datetime.timedelta(days=days_inactive)
            ).strftime("%Y-%m-%dT%H:%M:%SZ")
            return [
                u for u in M.AD_USERS
                if u.get("userAccountControl") != "514"
                and (u.get("lastLogonTimestamp") or "9999") < cutoff
            ]
        return await asyncio.to_thread(_get_ad().get_stale_accounts, days_inactive)

    # ── Microsoft Entra ID ────────────────────────────────────────────────────

    @mcp.tool()
    async def entra_list_users(limit: int = 100) -> list[dict]:
        """List users in Microsoft Entra ID (Azure AD).
        
        Returns a list of normalized user objects with consistent field names.
        """
        if _USE_MOCK:
            canonical_users = [EntraUserAdapter.to_canonical(u) for u in M.ENTRA_USERS[:limit]]
            return [u.model_dump(mode='json', exclude_none=True) for u in canonical_users]
        
        fields = (
            "id,displayName,userPrincipalName,mail,jobTitle,department,"
            "accountEnabled,createdDateTime,onPremisesSyncEnabled,assignedLicenses"
        )
        data = await _get_entra().get(
            "/users", params={"$select": fields, "$top": min(limit, 999)}
        )
        entra_users = data.get("value", [])
        canonical_users = [EntraUserAdapter.to_canonical(u) for u in entra_users]
        return [u.model_dump(mode='json', exclude_none=True) for u in canonical_users]

    @mcp.tool()
    async def entra_get_user(user_id_or_upn: str) -> dict | None:
        """Retrieve a single Entra ID user by object ID or UPN (user@company.com).
        
        Returns a normalized user object with consistent field names across all systems.
        """
        if _USE_MOCK:
            entra_dict = (
                M.ENTRA_USERS_BY_UPN.get(user_id_or_upn)
                or M.ENTRA_USERS_BY_MAIL.get(user_id_or_upn)
                or next((u for u in M.ENTRA_USERS if u["id"] == user_id_or_upn), None)
            )
            if not entra_dict:
                return None
            canonical = EntraUserAdapter.to_canonical(entra_dict)
            return canonical.model_dump(mode='json', exclude_none=True)
        
        entra_dict = await _get_entra().get(f"/users/{user_id_or_upn}")
        if not entra_dict:
            return None
        canonical = EntraUserAdapter.to_canonical(entra_dict)
        return canonical.model_dump(mode='json', exclude_none=True)

    @mcp.tool()
    async def entra_list_groups(limit: int = 100) -> list[dict]:
        """List all groups in Microsoft Entra ID."""
        if _USE_MOCK:
            return M.ENTRA_GROUPS[:limit]
        data = await _get_entra().get("/groups", params={"$top": min(limit, 999)})
        return data.get("value", [])

    @mcp.tool()
    async def entra_get_group_members(group_id: str) -> list[dict]:
        """List members of an Entra ID group by its object ID."""
        if _USE_MOCK:
            group = next((g for g in M.ENTRA_GROUPS if g["id"] == group_id), None)
            if not group:
                return []
            gname = group["displayName"].lower()
            return [
                u for u in M.ENTRA_USERS
                if gname in (u.get("department") or "").lower()
                or gname in u.get("displayName", "").lower()
            ]
        return await _get_entra().get_all_pages(f"/groups/{group_id}/members")

    @mcp.tool()
    async def entra_list_service_principals(limit: int = 100) -> list[dict]:
        """List service principals (app registrations / enterprise apps) in Entra ID."""
        if _USE_MOCK:
            return M.ENTRA_SERVICE_PRINCIPALS[:limit]
        data = await _get_entra().get(
            "/servicePrincipals", params={"$top": min(limit, 999)}
        )
        return data.get("value", [])

    @mcp.tool()
    async def entra_get_conditional_access_policies() -> list[dict]:
        """List all Conditional Access policies configured in Entra ID."""
        if _USE_MOCK:
            return M.ENTRA_CONDITIONAL_ACCESS_POLICIES
        data = await _get_entra().get("/identity/conditionalAccess/policies")
        return data.get("value", [])

    @mcp.tool()
    async def entra_get_signin_logs(limit: int = 50) -> list[dict]:
        """Retrieve recent sign-in log entries from Entra ID.

        Requires AuditLog.Read.All Graph permission.
        """
        if _USE_MOCK:
            return M.ENTRA_SIGNIN_LOGS[:limit]
        data = await _get_entra().get(
            "/auditLogs/signIns",
            params={"$top": limit, "$orderby": "createdDateTime desc"},
        )
        return data.get("value", [])

    @mcp.tool()
    async def entra_get_risky_users() -> list[dict]:
        """List users flagged as risky by Entra ID Identity Protection.

        Requires IdentityRiskyUser.Read.All Graph permission.
        """
        if _USE_MOCK:
            return M.ENTRA_RISKY_USERS
        data = await _get_entra().get("/identityProtection/riskyUsers")
        return data.get("value", [])
