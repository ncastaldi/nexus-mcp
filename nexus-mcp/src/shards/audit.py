"""Audit Shard — cross-system content drift detection and weekly reporting.

Status: 🟡 Yellow
Mock:   Set USE_MOCK=true to use built-in sample data (no credentials needed).
        All cross-system comparisons run entirely on mock_data.py — no live calls made.
"""

from __future__ import annotations
import asyncio
import datetime
import json
import sys
import os
from pathlib import Path
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "lib"))

from mcp.server.fastmcp import FastMCP
import mock_data as M
from adapters import ADUserAdapter, EntraUserAdapter, WorkdayWorkerAdapter
from schemas import CanonicalUser, FieldDrift, DriftType

_USE_MOCK = os.getenv("USE_MOCK", "false").lower() == "true"

# Lazy singletons shared within this shard only
_ad = None
_entra = None
_wd = None
_ls = None
_helix = None
_intune = None


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


def _get_wd():
    global _wd
    if _wd is None:
        from workday_client import WorkdayClient
        _wd = WorkdayClient()
    return _wd


def _get_ls():
    global _ls
    if _ls is None:
        from lansweeper_client import LansweeperClient
        _ls = LansweeperClient()
    return _ls


def _get_helix():
    global _helix
    if _helix is None:
        from helix_client import HelixClient
        _helix = HelixClient()
    return _helix


def _get_intune():
    global _intune
    if _intune is None:
        from intune_client import IntuneClient
        _intune = IntuneClient()
    return _intune


# ── Internal helpers ──────────────────────────────────────────────────────────

def _norm(val: Any) -> str | None:
    """Normalize value to lowercase string for comparison."""
    return str(val).strip().lower() if val is not None else None


def _compare_field(field_name: str, sys_a: str, val_a: Any, sys_b: str, val_b: Any) -> FieldDrift | None:
    """Compare a single field between two systems, return FieldDrift if different."""
    if _norm(val_a) != _norm(val_b):
        return FieldDrift(
            drift_type=DriftType.FIELD_MISMATCH,
            field_name=field_name,
            system_a=sys_a,
            value_a=str(val_a) if val_a is not None else None,
            system_b=sys_b,
            value_b=str(val_b) if val_b is not None else None,
            severity="medium",
        )
    return None


def _compare_users(wd_user: CanonicalUser | None, ad_user: CanonicalUser | None, entra_user: CanonicalUser | None) -> list[FieldDrift]:
    """Compare canonical user objects across systems and return list of drifts."""
    drifts: list[FieldDrift] = []
    
    # Compare Workday vs AD
    if wd_user and ad_user:
        for field_name, wd_val, ad_val in [
            ("display_name", wd_user.display_name, ad_user.display_name),
            ("job_title", wd_user.job_title, ad_user.job_title),
            ("department", wd_user.department, ad_user.department),
        ]:
            drift = _compare_field(field_name, "Workday", wd_val, "ActiveDirectory", ad_val)
            if drift:
                drifts.append(drift)
    
    # Compare Workday vs Entra
    if wd_user and entra_user:
        for field_name, wd_val, entra_val in [
            ("display_name", wd_user.display_name, entra_user.display_name),
            ("job_title", wd_user.job_title, entra_user.job_title),
            ("department", wd_user.department, entra_user.department),
        ]:
            drift = _compare_field(field_name, "Workday", wd_val, "Entra", entra_val)
            if drift:
                drifts.append(drift)
    
    # Compare AD vs Entra
    if ad_user and entra_user:
        for field_name, ad_val, entra_val in [
            ("display_name", ad_user.display_name, entra_user.display_name),
            ("job_title", ad_user.job_title, entra_user.job_title),
            ("department", ad_user.department, entra_user.department),
        ]:
            drift = _compare_field(field_name, "ActiveDirectory", ad_val, "Entra", entra_val)
            if drift:
                drifts.append(drift)
    _name, job_title, and department across all three systems using
        canonical pydantic schemas for type safety and consistent field names.

        Args:
            email: Primary work email of the user to audit.
        """
        if _USE_MOCK:
            # Get raw dicts from mock data
            wd_dict = M.WORKDAY_WORKERS_BY_EMAIL.get(email.lower())
            ad_dict = M.AD_USERS_BY_EMAIL.get(email.lower())
            entra_dict = M.ENTRA_USERS_BY_MAIL.get(email.lower())
            
            # Transform to canonical models
            wd_user = WorkdayWorkerAdapter.to_canonical(wd_dict) if wd_dict else None
            ad_user = ADUserAdapter.to_canonical(ad_dict) if ad_dict else None
            entra_user = EntraUserAdapter.to_canonical(entra_dict) if entra_dict else None
            
            # Compare using canonical models
            drifts = _compare_users(wd_user, ad_user, entra_user)
            
            return {
                "email": email,
                "systems_checked": ["Workday", "ActiveDirectory", "Entra"],
                "workday_found": wd_user is not None,
                "ad_found": ad_user is not None,
                "entra_found": entra_user is not None,
                "discrepancy_count": len(drifts),
                "discrepancies": [d.model_dump(mode='json') for d in drifts]
# ── Shard registration ────────────────────────────────────────────────────────

def register(mcp: FastMCP) -> None:
    """Register all Audit shard tools onto the MCP server."""

    # ── Drift tools ───────────────────────────────────────────────────────────

    @mcp.tool()
    async def audit_user_drift(email: str) -> dict:
        """Audit a single user across Workday, Active Directory, and Entra ID for field drift.

        Compares displayName, jobTitle, and department across all three systems.

        Args:
            email: Primary work email of the user to audit.
        """
        if _USE_MOCK:
            wd_worker = M.WORKDAY_WORKERS_BY_EMAIL.get(email.lower())
            ad_user = M.AD_USERS_BY_EMAIL.get(email.lower())
            entra_user = M.ENTRA_USERS_BY_MAIL.get(email.lower())
            diffs: list[dict] = []
            comparisons = [
                ("displayName", "Workday", _pick(wd_worker, "descriptor"),
                 "ActiveDirectory", _pick(ad_user, "displayName")),
                ("displayName", "Workday", _pick(wd_worker, "descriptor"),
                 "Entra", _pick(entra_user, "displayName")),
                ("displayName", "ActiveDirectory", _pick(ad_user, "displayName"),
                 "Entra", _pick(entra_user, "displayName")),
                ("jobTitle", "Workday", _pick(wd_worker, "primaryJob", "jobProfile", "descriptor"),
                 "ActiveDirectory", _pick(ad_user, "title")),
                ("jobTitle", "Workday", _pick(wd_worker, "primaryJob", "jobProfile", "descriptor"),
                 "Entra", _pick(entra_user, "jobTitle")),
                ("department", "Workday", _pick(wd_worker, "primaryJob", "businessUnit", "descriptor"),
                 "ActiveDirectory", _pick(ad_user, "department")),
                ("department", "Workday", _pick(wd_worker, "primaryJob", "businessUnit", "descriptor"),
                 "Entra", _pick(entra_user, "department")),
            ]
            for field, sa, va, sb, vb in comparisons:
                d = _drift(sa, sb, field, va, vb)
                if d:
                    diffs.append(d)
            return {
                "email": email,
                "systems_checked": ["Workday", "ActiveDirectory", "Entra"],
                "workday_found": wd_worker is not None,
                "ad_found": ad_user is not None,
                "entra_found": entra_user is not None,
                "discrepancy_count": len(diffs),
                "discrepancies": diffs,
            }
        wd_task = asyncio.create_task(_get_wd().get(
            "/staffing/v6/workers", params={"limit": 500}
        ))
        entra_task = asyncio.create_task(_get_entra().get(
            "/users",
            params={
                "$select": "id,displayName,userPrincipalName,mail,jobTitle,department,accountEnabled",
                "$top": 999,
            },
        ))
        wd_data, entra_data = await asyncio.gather(wd_task, entra_task)
        ad_user = await asyncio.to_thread(_get_ad().get_user_by_email, email)

        wd_worker = next(
            (w for w in wd_data.get("data", [])
             if (w.get("primaryWorkEmail") or "").lower() == email.lower()),
            None,
        )
        entra_user = next(
            (u for u in entra_data.get("value", [])
             if _norm(u.get("mail")) == _norm(email)
             or _norm(u.get("userPrincipalName")) == _norm(email)),
            None,
        )

        diffs: list[dict] = []
        comparisons = [
            ("displayName",
             "Workday", _pick(wd_worker, "descriptor"),
             "ActiveDirectory", _pick(ad_user, "displayName")),
            ("displayName",
             "Workday", _pick(wd_worker, "descriptor"),
             "Entra", _pick(entra_user, "displayName")),
            ("displayName",
             "ActiveDirectory", _pick(ad_user, "displayName"),
             "Entra", _pick(entra_user, "displayName")),
            ("jobTitle",
             "Workday", _pick(wd_worker, "primaryJob", "jobProfile", "descriptor"),
             "ActiveDirectory", _pick(ad_user, "title")),
            ("jobTitle",
             "Workday", _pick(wd_worker, "primaryJob", "jobProfile", "descriptor"),
             "Entra", _pick(entra_user, "jobTitle")),
            ("department",
             "Workday", _pick(wd_worker, "primaryJob", "businessUnit", "descriptor"),
             "ActiveDirectory", _pick(ad_user, "department")),
            ("department",
             "Workday", _pick(wd_worker, "primaryJob", "businessUnit", "descriptor"),
             "Entra", _pick(entra_user, "department")),
        ]
        for field, sa, va, sb, vb in comparisons:
            d = _drift(sa, sb, field, va, vb)
            if d:
                diffs.append(d)

        return {
            "email": email,
            "systems_checked": ["Workday", "ActiveDirectory", "Entra"],
            "workday_found": wd_worker is not None,
            "ad_found": ad_user is not None,
            "entra_found": entra_user is not None,
            "discrepancy_count": len(diffs),
            "discrepancies": diffs,
        }

    @mcp.tool()
    async def audit_bulk_user_drift(emails: list[str]) -> list[dict]:
        """Run user drift audit for a list of email addresses concurrently (max 50).

        Args:
            emails: List of work email addresses to audit.
        """
        async def _one(email: str) -> dict:
            try:
                return await audit_user_drift(email)
            except Exception as e:
                return {"email": email, "error": str(e)}

        return await asyncio.gather(*[_one(e) for e in emails[:50]])

    @mcp.tool()
    async def audit_device_drift(device_name: str) -> dict:
        """Audit a device across Lansweeper, Intune, and BMC Helix CMDB for field drift.

        Compares manufacturer and serial number across all three asset systems.

        Args:
            device_name: The computer/device name to look up.
        """
        if _USE_MOCK:
            dn = device_name.lower()
            ls_asset = M.LANSWEEPER_ASSETS_BY_NAME.get(dn)
            intune_device = M.INTUNE_DEVICES_BY_NAME.get(dn)
            helix_ci = M.HELIX_CMDB_BY_NAME.get(device_name.upper()) or M.HELIX_CMDB_BY_NAME.get(device_name)
            diffs: list[dict] = []
            for field, ik, hk in [("manufacturer", "manufacturer", "Manufacturer"),
                                   ("serialNumber", "serialNumber", "Serial Number")]:
                ls_val = _pick(ls_asset, field)
                intune_val = _pick(intune_device, ik)
                helix_val = _pick(helix_ci, "values", hk)
                for sa, sb, va, vb in [
                    ("Lansweeper", "Intune", ls_val, intune_val),
                    ("Lansweeper", "Helix", ls_val, helix_val),
                ]:
                    d = _drift(sa, sb, field, va, vb)
                    if d:
                        diffs.append(d)
            return {
                "device_name": device_name,
                "systems_checked": ["Lansweeper", "Intune", "HelixCMDB"],
                "lansweeper_found": ls_asset is not None,
                "intune_found": intune_device is not None,
                "helix_found": helix_ci is not None,
                "discrepancy_count": len(diffs),
                "discrepancies": diffs,
            }
        from config import LansweeperConfig
        site_id = LansweeperConfig().site_id
        ls_query = """
        query S($siteId: String!, $q: String!) {
          site(id: $siteId) {
            assetResources(
              pagination: { limit: 5, page: 1 }
              assetBasicFilters: { assetName: $q }
            ) {
              items { assetId assetName operatingSystem manufacturer serialNumber }
            }
          }
        }
        """
        ls_task = asyncio.create_task(
            _get_ls().gql(ls_query, {"siteId": site_id, "q": device_name})
        )
        intune_task = asyncio.create_task(
            _get_intune().get("/deviceManagement/managedDevices", params={"$top": 500})
        )
        helix_task = asyncio.create_task(
            _get_helix().get(
                "/api/arsys/v1/entry/BMC.CORE:BMC_ComputerSystem",
                params={"q": f"'Name' LIKE \"%{device_name}%\"", "limit": 5},
            )
        )
        ls_data, intune_data, helix_data = await asyncio.gather(ls_task, intune_task, helix_task)

        ls_results = ls_data["site"]["assetResources"]["items"]
        ls_asset = ls_results[0] if ls_results else None
        intune_device = next(
            (d for d in intune_data.get("value", [])
             if _norm(d.get("deviceName")) == _norm(device_name)),
            None,
        )
        helix_entries = helix_data.get("entries", [])
        helix_ci = helix_entries[0] if helix_entries else None

        diffs: list[dict] = []
        for field, lk, ik, hk in [
            ("manufacturer", "manufacturer", "manufacturer", "Manufacturer"),
            ("serialNumber", "serialNumber", "serialNumber", "Serial Number"),
        ]:
            ls_val = _pick(ls_asset, field)
            intune_val = _pick(intune_device, ik)
            helix_val = _pick(helix_ci, "values", hk)
            for sa, sb, va, vb in [
                ("Lansweeper", "Intune", ls_val, intune_val),
                ("Lansweeper", "Helix", ls_val, helix_val),
            ]:
                d = _drift(sa, sb, field, va, vb)
                if d:
                    diffs.append(d)

        return {
            "device_name": device_name,
            "systems_checked": ["Lansweeper", "Intune", "HelixCMDB"],
            "lansweeper_found": ls_asset is not None,
            "intune_found": intune_device is not None,
            "helix_found": helix_ci is not None,
            "discrepancy_count": len(diffs),
            "discrepancies": diffs,
        }

    @mcp.tool()
    async def audit_entra_ad_sync_drift(limit: int = 200) -> dict:
        """Compare Entra ID synced users against Active Directory for field drift.

        Args:
            limit: Number of Entra users to evaluate (default 200).
        """
        if _USE_MOCK:
            synced = [u for u in M.ENTRA_USERS if u.get("onPremisesSyncEnabled")][:limit]
            drifted = []
            for u in synced:
                upn = u.get("userPrincipalName", "")
                sam = upn.split("@")[0] if "@" in upn else upn
                ad_user = M.AD_USERS_BY_SAM.get(sam.lower())
                if not ad_user:
                    drifted.append({"upn": upn, "issue": "Not found in AD", "discrepancies": []})
                    continue
                diffs = []
                for field, ek, ak in [("displayName", "displayName", "displayName"),
                                       ("jobTitle", "jobTitle", "title"),
                                       ("department", "department", "department")]:
                    d = _drift("Entra", "ActiveDirectory", field, u.get(ek), ad_user.get(ak))
                    if d:
                        diffs.append(d)
                if diffs:
                    drifted.append({"upn": upn, "discrepancies": diffs})
            return {
                "users_evaluated": len(synced),
                "drifted_users_count": len(drifted),
                "drifted_users": drifted,
            }
        users = (await _get_entra().get(
            "/users",
            params={
                "$select": "id,displayName,userPrincipalName,mail,jobTitle,department,onPremisesSyncEnabled",
                "$top": min(limit, 999),
            },
        )).get("value", [])

        drifted = []
        for u in users:
            if not u.get("onPremisesSyncEnabled"):
                continue
            upn = u.get("userPrincipalName", "")
            sam = upn.split("@")[0] if "@" in upn else upn
            ad_user = await asyncio.to_thread(_get_ad().get_user, sam)
            if not ad_user:
                drifted.append({"upn": upn, "issue": "Not found in AD", "discrepancies": []})
                continue
            diffs = []
            for field, ek, ak in [
                ("displayName", "displayName", "displayName"),
                ("jobTitle", "jobTitle", "title"),
                ("department", "department", "department"),
            ]:
                d = _drift("Entra", "ActiveDirectory", field, u.get(ek), ad_user.get(ak))
                if d:
                    diffs.append(d)
            if diffs:
                drifted.append({"upn": upn, "discrepancies": diffs})

        return {
            "users_evaluated": len(users),
            "drifted_users_count": len(drifted),
            "drifted_users": drifted,
        }

    @mcp.tool()
    async def audit_intune_lansweeper_device_drift(limit: int = 100) -> dict:
        """Compare Intune managed devices against Lansweeper for manufacturer/serial drift.

        Args:
            limit: Number of Intune devices to evaluate (default 100).
        """
        if _USE_MOCK:
            devices = M.INTUNE_DEVICES[:limit]
            ls_idx = {a["assetName"].lower(): a for a in M.LANSWEEPER_ASSETS}
            drifted, missing = [], []
            for device in devices:
                name = device.get("deviceName", "")
                ls_asset = ls_idx.get(name.lower())
                if not ls_asset:
                    missing.append(name)
                    continue
                diffs = []
                for field, ik, lk in [("manufacturer", "manufacturer", "manufacturer"),
                                       ("serialNumber", "serialNumber", "serialNumber")]:
                    d = _drift("Intune", "Lansweeper", field, device.get(ik), ls_asset.get(lk))
                    if d:
                        diffs.append(d)
                if diffs:
                    drifted.append({"device": name, "discrepancies": diffs})
            return {
                "intune_devices_evaluated": len(devices),
                "drifted_count": len(drifted),
                "missing_in_lansweeper_count": len(missing),
                "missing_in_lansweeper": missing,
                "drifted_devices": drifted,
            }
        intune_devices = (await _get_intune().get(
            "/deviceManagement/managedDevices", params={"$top": min(limit, 1000)}
        )).get("value", [])

        from config import LansweeperConfig
        site_id = LansweeperConfig().site_id
        drifted, missing = [], []

        for device in intune_devices:
            name = device.get("deviceName", "")
            q = """
            query S($siteId: String!, $q: String!) {
              site(id: $siteId) {
                assetResources(
                  pagination: { limit: 3, page: 1 }
                  assetBasicFilters: { assetName: $q }
                ) { items { assetName manufacturer serialNumber } }
              }
            }
            """
            ls_data = await _get_ls().gql(q, {"siteId": site_id, "q": name})
            ls_items = ls_data["site"]["assetResources"]["items"]
            ls_asset = next(
                (a for a in ls_items if _norm(a.get("assetName")) == _norm(name)), None
            )
            if not ls_asset:
                missing.append(name)
                continue
            diffs = []
            for field, ik, lk in [
                ("manufacturer", "manufacturer", "manufacturer"),
                ("serialNumber", "serialNumber", "serialNumber"),
            ]:
                d = _drift("Intune", "Lansweeper", field, device.get(ik), ls_asset.get(lk))
                if d:
                    diffs.append(d)
            if diffs:
                drifted.append({"device": name, "discrepancies": diffs})

        return {
            "intune_devices_evaluated": len(intune_devices),
            "drifted_count": len(drifted),
            "missing_in_lansweeper_count": len(missing),
            "missing_in_lansweeper": missing,
            "drifted_devices": drifted,
        }

    # ── Reporting tools ────────────────────────────────────────────────────────

    @mcp.tool()
    async def generate_weekly_report(save_to_file: bool = True) -> dict:
        """Generate a comprehensive weekly operational report across all enterprise systems.

        Covers Workday headcount, Entra account health, Intune compliance,
        Lansweeper inventory, and Helix ITSM ticket volumes.

        Args:
            save_to_file: Save the report as JSON to the configured output directory.
        """
        if _USE_MOCK:
            one_week_ago = (datetime.datetime.utcnow() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")

            def _hf(e: dict, k: str) -> str:
                return (e.get("values") or {}).get(k) or "unknown"

            report = {
                "report_type": "weekly_operational_report",
                "week": _week(),
                "generated_at": _ts(),
                "mock": True,
                "workday": {
                    "total_workers": len(M.WORKDAY_WORKERS),
                    "new_hires_this_week": len([w for w in M.WORKDAY_WORKERS if (w.get("hireDate") or "") >= one_week_ago]),
                },
                "entra_id": {
                    "total_users": len(M.ENTRA_USERS),
                    "enabled": len([u for u in M.ENTRA_USERS if u.get("accountEnabled")]),
                    "disabled": len([u for u in M.ENTRA_USERS if not u.get("accountEnabled")]),
                    "on_prem_synced": len([u for u in M.ENTRA_USERS if u.get("onPremisesSyncEnabled")]),
                    "licensed": len([u for u in M.ENTRA_USERS if u.get("assignedLicenses")]),
                },
                "intune": {
                    "total_managed_devices": len(M.INTUNE_DEVICES),
                    "compliance_breakdown": _count_by(M.INTUNE_DEVICES, "complianceState"),
                    "os_breakdown": _count_by(M.INTUNE_DEVICES, "operatingSystem"),
                    "noncompliant_devices": [d.get("deviceName") for d in M.INTUNE_DEVICES if d.get("complianceState") == "noncompliant"],
                },
                "lansweeper": {
                    "total_assets": len(M.LANSWEEPER_ASSETS),
                    "assets_by_type": _count_by(M.LANSWEEPER_ASSETS, "assetType"),
                    "assets_by_os": _count_by(M.LANSWEEPER_ASSETS, "operatingSystem"),
                },
                "helix_itsm": {
                    "open_incidents": len([i for i in M.HELIX_INCIDENTS if _hf(i, "Status") != "Resolved"]),
                    "incident_by_status": _count_by([{"s": _hf(i, "Status")} for i in M.HELIX_INCIDENTS], "s"),
                    "open_changes": len([c for c in M.HELIX_CHANGES if _hf(c, "Status") not in ("Completed", "Cancelled")]),
                    "change_by_status": _count_by([{"s": _hf(c, "Status")} for c in M.HELIX_CHANGES], "s"),
                },
            }
            if save_to_file:
                report["saved_to"] = _save(report, f"weekly_report_{_week()}.json")
            return report

        wd = _get_wd()
        entra = _get_entra()
        intune = _get_intune()
        ls = _get_ls()
        helix = _get_helix()
        from config import LansweeperConfig
        site_id = LansweeperConfig().site_id

        ls_gql = """
        query($siteId: String!) {
          site(id: $siteId) {
            assetResources(pagination: { limit: 500, page: 1 }) {
              items { assetType operatingSystem }
            }
          }
        }
        """

        (workers_resp, entra_users, intune_devices, ls_data, incidents, changes) = (
            await asyncio.gather(
                wd.get("/staffing/v6/workers", params={"limit": 500}),
                entra.get("/users", params={"$select": "id,accountEnabled,onPremisesSyncEnabled,assignedLicenses", "$top": 999}),
                intune.get("/deviceManagement/managedDevices", params={"$top": 1000}),
                ls.gql(ls_gql, {"siteId": site_id}),
                helix.get("/api/arsys/v1/entry/HPD:Help%20Desk", params={"q": "('Status' != \"Closed\")", "limit": 200}),
                helix.get("/api/arsys/v1/entry/CHG:ChangeInterface_Create", params={"q": "'Status' != \"Closed\"", "limit": 200}),
            )
        )

        workers = workers_resp.get("data", [])
        entra_list = entra_users.get("value", [])
        intune_list = intune_devices.get("value", [])
        ls_assets = ls_data["site"]["assetResources"]["items"]
        incident_list = incidents.get("entries", [])
        change_list = changes.get("entries", [])

        one_week_ago = (datetime.datetime.utcnow() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")

        def _hfield(e: dict, k: str) -> str:
            return (e.get("values") or {}).get(k) or "unknown"

        report = {
            "report_type": "weekly_operational_report",
            "week": _week(),
            "generated_at": _ts(),
            "workday": {
                "total_workers": len(workers),
                "new_hires_this_week": len([w for w in workers if (w.get("hireDate") or "") >= one_week_ago]),
            },
            "entra_id": {
                "total_users": len(entra_list),
                "enabled": len([u for u in entra_list if u.get("accountEnabled")]),
                "disabled": len([u for u in entra_list if not u.get("accountEnabled")]),
                "on_prem_synced": len([u for u in entra_list if u.get("onPremisesSyncEnabled")]),
                "licensed": len([u for u in entra_list if u.get("assignedLicenses")]),
            },
            "intune": {
                "total_managed_devices": len(intune_list),
                "compliance_breakdown": _count_by(intune_list, "complianceState"),
                "os_breakdown": _count_by(intune_list, "operatingSystem"),
                "noncompliant_devices": [
                    d.get("deviceName") for d in intune_list if d.get("complianceState") == "noncompliant"
                ][:50],
            },
            "lansweeper": {
                "total_assets": len(ls_assets),
                "assets_by_type": _count_by(ls_assets, "assetType"),
                "assets_by_os": _count_by(ls_assets, "operatingSystem"),
            },
            "helix_itsm": {
                "open_incidents": len(incident_list),
                "incident_by_status": _count_by(
                    [{"s": _hfield(i, "Status")} for i in incident_list], "s"
                ),
                "open_changes": len(change_list),
                "change_by_status": _count_by(
                    [{"s": _hfield(c, "Status")} for c in change_list], "s"
                ),
            },
        }

        if save_to_file:
            report["saved_to"] = _save(report, f"weekly_report_{_week()}.json")

        return report

    @mcp.tool()
    async def generate_compliance_report(save_to_file: bool = True) -> dict:
        """Generate a device compliance and identity risk report.

        Covers Intune non-compliant devices and Entra ID risky users.

        Args:
            save_to_file: Save the report as JSON to the configured output directory.
        """
        if _USE_MOCK:
            nc = [d for d in M.INTUNE_DEVICES if d["complianceState"] == "noncompliant"]
            report = {
                "report_type": "compliance_report",
                "generated_at": _ts(),
                "mock": True,
                "intune": {
                    "noncompliant_device_count": len(nc),
                    "noncompliant_devices": [
                        {"name": d["deviceName"], "user": d.get("userPrincipalName"),
                         "os": d["operatingSystem"], "last_sync": d["lastSyncDateTime"],
                         "isEncrypted": d.get("isEncrypted")}
                        for d in nc
                    ],
                },
                "entra_identity_protection": {
                    "risky_user_count": len(M.ENTRA_RISKY_USERS),
                    "risky_users": [
                        {"id": u["id"], "risk_level": u["riskLevel"],
                         "risk_state": u["riskState"], "upn": u.get("userPrincipalName"),
                         "risk_last_updated": u["riskLastUpdatedDateTime"]}
                        for u in M.ENTRA_RISKY_USERS
                    ],
                },
                "entra_summary": {
                    "total_users": len(M.ENTRA_USERS),
                    "disabled": len([u for u in M.ENTRA_USERS if not u.get("accountEnabled")]),
                    "licensed": len([u for u in M.ENTRA_USERS if u.get("assignedLicenses")]),
                },
                "ad_disabled_accounts": [u["sAMAccountName"] for u in M.AD_USERS if u.get("userAccountControl") == "514"],
            }
            if save_to_file:
                report["saved_to"] = _save(report, f"compliance_report_{_ts()[:10]}.json")
            return report

        noncompliant, risky, all_users = await asyncio.gather(
            _get_intune().get("/deviceManagement/managedDevices", params={"$filter": "complianceState eq 'noncompliant'"}),
            _get_entra().get("/identityProtection/riskyUsers"),
            _get_entra().get("/users", params={"$select": "id,accountEnabled,assignedLicenses", "$top": 999}),
        )

        report = {
            "report_type": "compliance_report",
            "generated_at": _ts(),
            "intune": {
                "noncompliant_device_count": len(noncompliant.get("value", [])),
                "noncompliant_devices": [
                    {"name": d.get("deviceName"), "user": d.get("userPrincipalName"),
                     "os": d.get("operatingSystem"), "last_sync": d.get("lastSyncDateTime")}
                    for d in noncompliant.get("value", [])
                ],
            },
            "entra_identity_protection": {
                "risky_user_count": len(risky.get("value", [])),
                "risky_users": [
                    {"id": u.get("id"), "risk_level": u.get("riskLevel"),
                     "risk_state": u.get("riskState"), "risk_last_updated": u.get("riskLastUpdatedDateTime")}
                    for u in risky.get("value", [])
                ],
            },
            "entra_summary": {
                "total_users": len(all_users.get("value", [])),
                "disabled": len([u for u in all_users.get("value", []) if not u.get("accountEnabled")]),
                "licensed": len([u for u in all_users.get("value", []) if u.get("assignedLicenses")]),
            },
        }

        if save_to_file:
            ts_date = _ts()[:10]
            report["saved_to"] = _save(report, f"compliance_report_{ts_date}.json")

        return report

    @mcp.tool()
    async def generate_asset_reconciliation_report(save_to_file: bool = True) -> dict:
        """Compare Intune and Lansweeper inventories — find gaps and field mismatches.

        Args:
            save_to_file: Save the report as JSON to the configured output directory.
        """
        if _USE_MOCK:
            intune_list = M.INTUNE_DEVICES
            ls_list = M.LANSWEEPER_ASSETS
            intune_idx = {(_norm(d.get("deviceName")) or ""): d for d in intune_list}
            ls_idx = {(_norm(a.get("assetName")) or ""): a for a in ls_list}
            only_intune = [n for n in intune_idx if n not in ls_idx]
            only_ls = [n for n in ls_idx if n not in intune_idx]
            in_both = [n for n in intune_idx if n in ls_idx]
            mismatches = []
            for name in in_both:
                i = intune_idx[name]
                l = ls_idx[name]
                diffs = []
                for field, ik, lk in [("manufacturer", "manufacturer", "manufacturer"),
                                       ("serialNumber", "serialNumber", "serialNumber")]:
                    iv, lv = _norm(i.get(ik)), _norm(l.get(lk))
                    if iv and lv and iv != lv:
                        diffs.append({"field": field, "intune": i.get(ik), "lansweeper": l.get(lk)})
                if diffs:
                    mismatches.append({"device": name, "discrepancies": diffs})
            report = {
                "report_type": "asset_reconciliation_report",
                "generated_at": _ts(),
                "mock": True,
                "intune_device_count": len(intune_list),
                "lansweeper_asset_count": len(ls_list),
                "only_in_intune_count": len(only_intune),
                "only_in_lansweeper_count": len(only_ls),
                "in_both_count": len(in_both),
                "mismatch_count": len(mismatches),
                "only_in_intune": only_intune,
                "only_in_lansweeper": only_ls,
                "mismatches": mismatches,
            }
            if save_to_file:
                report["saved_to"] = _save(report, f"asset_reconciliation_{_ts()[:10]}.json")
            return report

        from config import LansweeperConfig
        site_id = LansweeperConfig().site_id
        ls_gql = """
        query($siteId: String!) {
          site(id: $siteId) {
            assetResources(pagination: { limit: 500, page: 1 }) {
              items { assetName manufacturer serialNumber }
            }
          }
        }
        """
        intune_resp, ls_data = await asyncio.gather(
            _get_intune().get("/deviceManagement/managedDevices", params={"$top": 1000}),
            _get_ls().gql(ls_gql, {"siteId": site_id}),
        )

        intune_list = intune_resp.get("value", [])
        ls_list = ls_data["site"]["assetResources"]["items"]

        intune_idx = {(_norm(d.get("deviceName")) or ""): d for d in intune_list}
        ls_idx = {(_norm(a.get("assetName")) or ""): a for a in ls_list}

        only_intune = [n for n in intune_idx if n not in ls_idx]
        only_ls = [n for n in ls_idx if n not in intune_idx]
        in_both = [n for n in intune_idx if n in ls_idx]

        mismatches = []
        for name in in_both:
            i = intune_idx[name]
            l = ls_idx[name]
            diffs = []
            for field, ik, lk in [("manufacturer", "manufacturer", "manufacturer"),
                                    ("serialNumber", "serialNumber", "serialNumber")]:
                iv, lv = _norm(i.get(ik)), _norm(l.get(lk))
                if iv and lv and iv != lv:
                    diffs.append({"field": field, "intune": i.get(ik), "lansweeper": l.get(lk)})
            if diffs:
                mismatches.append({"device": name, "discrepancies": diffs})

        report = {
            "report_type": "asset_reconciliation_report",
            "generated_at": _ts(),
            "intune_device_count": len(intune_list),
            "lansweeper_asset_count": len(ls_list),
            "only_in_intune_count": len(only_intune),
            "only_in_lansweeper_count": len(only_ls),
            "in_both_count": len(in_both),
            "mismatch_count": len(mismatches),
            "only_in_intune": only_intune[:100],
            "only_in_lansweeper": only_ls[:100],
            "mismatches": mismatches,
        }

        if save_to_file:
            ts_date = _ts()[:10]
            report["saved_to"] = _save(report, f"asset_reconciliation_{ts_date}.json")

        return report

    @mcp.tool()
    async def generate_itsm_weekly_summary(save_to_file: bool = True) -> dict:
        """Generate a weekly ITSM summary from BMC Helix — incidents and changes.

        Args:
            save_to_file: Save the report as JSON to the configured output directory.
        """
        if _USE_MOCK:
            def _f(e: dict, k: str) -> str:
                return (e.get("values") or {}).get(k) or "unknown"

            report = {
                "report_type": "itsm_weekly_summary",
                "week": _week(),
                "generated_at": _ts(),
                "mock": True,
                "incidents": {
                    "total": len(M.HELIX_INCIDENTS),
                    "by_status": _count_by([{"s": _f(i, "Status")} for i in M.HELIX_INCIDENTS], "s"),
                    "by_priority": _count_by([{"p": _f(i, "Priority")} for i in M.HELIX_INCIDENTS], "p"),
                    "highlights": [
                        {"id": _f(i, "Incident Number"), "summary": _f(i, "Summary"),
                         "priority": _f(i, "Priority"), "assignee": _f(i, "Assignee")}
                        for i in M.HELIX_INCIDENTS if _f(i, "Status") not in ("Resolved", "Closed")
                    ],
                },
                "changes": {
                    "total": len(M.HELIX_CHANGES),
                    "by_status": _count_by([{"s": _f(c, "Status")} for c in M.HELIX_CHANGES], "s"),
                    "by_type": _count_by([{"t": _f(c, "Change Type")} for c in M.HELIX_CHANGES], "t"),
                },
                "problems": {
                    "total": len(M.HELIX_PROBLEMS),
                    "open": [{"id": _f(p, "Problem Number"), "summary": _f(p, "Summary")} for p in M.HELIX_PROBLEMS],
                },
            }
            if save_to_file:
                report["saved_to"] = _save(report, f"itsm_summary_{_week()}.json")
            return report

        helix = _get_helix()
        incidents, changes = await asyncio.gather(
            helix.get("/api/arsys/v1/entry/HPD:Help%20Desk", params={"q": "('Status' != \"Closed\")", "limit": 500}),
            helix.get("/api/arsys/v1/entry/CHG:ChangeInterface_Create", params={"q": "'Status' != \"Closed\"", "limit": 500}),
        )

        def _f(e: dict, k: str) -> str:
            return (e.get("values") or {}).get(k) or "unknown"

        i_list = incidents.get("entries", [])
        c_list = changes.get("entries", [])

        report = {
            "report_type": "itsm_weekly_summary",
            "week": _week(),
            "generated_at": _ts(),
            "incidents": {
                "total": len(i_list),
                "by_status": _count_by([{"s": _f(i, "Status")} for i in i_list], "s"),
                "by_priority": _count_by([{"p": _f(i, "Priority")} for i in i_list], "p"),
            },
            "changes": {
                "total": len(c_list),
                "by_status": _count_by([{"s": _f(c, "Status")} for c in c_list], "s"),
                "by_type": _count_by([{"t": _f(c, "Change Type")} for c in c_list], "t"),
            },
        }

        if save_to_file:
            report["saved_to"] = _save(report, f"itsm_summary_{_week()}.json")

        return report
