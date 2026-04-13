"""Cross-system drift detection logic for Workday and Active Directory synchronization.

This module provides the core logic for detecting mismatches between
Workday (source of truth) and AD (target system) across multiple dimensions:
- Status reconciliation (terminated users still enabled)
- Job title alignment
- Department drift
- Name variance (legal/preferred vs display name)

For production deployment, replace MOCK_WORKERS with live API calls to
workday_client.py and ad_adapter.py.
"""

from typing import Any

# Mock dataset with reporting-line relationships for manager checks (WIS-017 prep)
MOCK_WORKERS: dict[str, dict[str, Any]] = {
    "EMP001": {
        "name": "Nathan",
        "legal_name": "Nathaniel Cole",
        "preferred_name": "Nathan",
        "ad_display_name": "Nathan Cole",
        "status": "Active",
        "ad_enabled": True,
        "dept": "IT",
        "workday_cost_center": "CC100-IT",
        "workday_title": "Systems Engineer",
        "ad_title": "Systems Engineer",
        "ad_department": "IT",
        "email": "nathan@example.com",
        "manager_id": "EMP010",
    },
    "EMP002": {
        "name": "Terminated User",
        "legal_name": "Taylor Brooks",
        "preferred_name": "Taylor",
        "ad_display_name": "Taylor Brooks",
        "status": "Terminated",
        "ad_enabled": True,
        "dept": "Sales",
        "workday_cost_center": "CC200-SALES",
        "workday_title": "Account Executive",
        "ad_title": "Account Executive",
        "ad_department": "Sales",
        "email": "user2@example.com",
        "manager_id": "EMP020",
    },
    "EMP003": {
        "name": "Alicia",
        "legal_name": "Alicia Gomez",
        "preferred_name": "Alicia",
        "ad_display_name": "Alicia Gomez",
        "status": "Active",
        "ad_enabled": True,
        "dept": "IT",
        "workday_cost_center": "CC100-IT",
        "workday_title": "Senior Systems Analyst",
        "ad_title": "Systems Analyst",
        "ad_department": "IT",
        "email": "alicia@example.com",
        "manager_id": "EMP010",
    },
    "EMP004": {
        "name": "Jordan",
        "legal_name": "Jordan Lee",
        "preferred_name": "Jordan",
        "ad_display_name": "Jordan Lee",
        "status": "Leave",
        "ad_enabled": True,
        "dept": "Finance",
        "workday_cost_center": "CC300-FIN",
        "workday_title": "Finance Analyst",
        "ad_title": "Finance Analyst",
        "ad_department": "Accounting",
        "email": "jordan@example.com",
        "manager_id": "EMP030",
    },
    "EMP010": {
        "name": "Priya Manager",
        "legal_name": "Priya Narayanan",
        "preferred_name": "Priya",
        "ad_display_name": "Priya Manager",
        "status": "Active",
        "ad_enabled": True,
        "dept": "IT",
        "workday_cost_center": "CC110-IT-MGMT",
        "workday_title": "IT Manager",
        "ad_title": "IT Manager",
        "ad_department": "IT",
        "email": "priya@example.com",
        "manager_id": "EMP100",
    },
    "EMP020": {
        "name": "Ramon Director",
        "legal_name": "Ramon Alvarez",
        "preferred_name": "Ramon",
        "ad_display_name": "Ramon Director",
        "status": "Active",
        "ad_enabled": True,
        "dept": "Sales",
        "workday_cost_center": "CC210-SALES-MGMT",
        "workday_title": "Sales Director",
        "ad_title": "Sales Director",
        "ad_department": "Sales",
        "email": "ramon@example.com",
        "manager_id": "EMP100",
    },
    "EMP030": {
        "name": "Morgan Lead",
        "legal_name": "Morgan Patel",
        "preferred_name": "Morgan",
        "ad_display_name": "Morgan Patel",
        "status": "Active",
        "ad_enabled": True,
        "dept": "Finance",
        "workday_cost_center": "CC310-FIN-MGMT",
        "workday_title": "Finance Lead",
        "ad_title": "Finance Lead",
        "ad_department": "Finance",
        "email": "morgan@example.com",
        "manager_id": "EMP100",
    },
    "EMP100": {
        "name": "Chief Exec",
        "legal_name": "Evelyn Carter",
        "preferred_name": "Evelyn",
        "ad_display_name": "Evelyn Carter",
        "status": "Active",
        "ad_enabled": True,
        "dept": "Executive",
        "workday_cost_center": "CC999-EXEC",
        "workday_title": "Chief Executive Officer",
        "ad_title": "Chief Executive Officer",
        "ad_department": "Executive",
        "email": "ceo@example.com",
        "manager_id": "",
    },
    # Intentional unresolved manager reference for mismatch test scenarios
    "EMP777": {
        "name": "Mismatch Case",
        "legal_name": "Alexandra Rivers",
        "preferred_name": "Alex",
        "ad_display_name": "Jordan Rivers",
        "status": "Active",
        "ad_enabled": True,
        "dept": "Operations",
        "workday_cost_center": "CC400-OPS",
        "workday_title": "Operations Specialist",
        "ad_title": "Operations Specialist",
        "ad_department": "Operations",
        "email": "mismatch@example.com",
        "manager_id": "EMP999",
    },
}


def scan_status_reconciliation_mismatches() -> dict[str, Any]:
    """Detect workers terminated in Workday but still enabled in AD.
    
    Returns:
        dict with 'scan_summary' (total_records_checked, mismatches_found, status)
        and 'mismatches' array of affected employees.
    """
    mismatches: list[dict[str, Any]] = []
    total_scanned = 0

    for employee_id, details in MOCK_WORKERS.items():
        total_scanned += 1
        workday_status = details.get("status")
        ad_enabled = bool(details.get("ad_enabled", False))

        if workday_status == "Terminated" and ad_enabled:
            mismatches.append(
                {
                    "employee_id": employee_id,
                    "employee_name": details["name"],
                    "workday_status": workday_status,
                    "ad_enabled": ad_enabled,
                    "mismatch_type": "terminated_but_enabled",
                    "severity": "high",
                }
            )

    return {
        "scan_summary": {
            "total_records_checked": total_scanned,
            "mismatches_found": len(mismatches),
            "status": "action_required" if mismatches else "clean",
        },
        "mismatches": mismatches,
    }


def scan_job_title_mismatches() -> dict[str, Any]:
    """Detect workers whose Workday title differs from their AD title.
    
    Returns:
        dict with 'scan_summary' and 'mismatches' array.
    """
    mismatches: list[dict[str, Any]] = []
    total_scanned = 0

    for employee_id, details in MOCK_WORKERS.items():
        total_scanned += 1
        workday_title = details.get("workday_title", "")
        ad_title = details.get("ad_title", "")

        if workday_title and ad_title and workday_title != ad_title:
            mismatches.append(
                {
                    "employee_id": employee_id,
                    "employee_name": details["name"],
                    "workday_title": workday_title,
                    "ad_title": ad_title,
                    "mismatch_type": "job_title_mismatch",
                    "severity": "medium",
                }
            )

    return {
        "scan_summary": {
            "total_records_checked": total_scanned,
            "mismatches_found": len(mismatches),
            "status": "action_required" if mismatches else "clean",
        },
        "mismatches": mismatches,
    }


def scan_department_drift() -> dict[str, Any]:
    """Detect workers whose Workday department context differs from AD department.
    
    Returns:
        dict with 'scan_summary' and 'mismatches' array.
    """
    mismatches: list[dict[str, Any]] = []
    total_scanned = 0

    for employee_id, details in MOCK_WORKERS.items():
        total_scanned += 1
        workday_department = details.get("dept", "")
        workday_cost_center = details.get("workday_cost_center", "")
        ad_department = details.get("ad_department", "")

        if workday_department and ad_department and workday_department != ad_department:
            mismatches.append(
                {
                    "employee_id": employee_id,
                    "employee_name": details["name"],
                    "workday_department": workday_department,
                    "workday_cost_center": workday_cost_center,
                    "ad_department": ad_department,
                    "mismatch_type": "department_drift",
                    "severity": "medium",
                }
            )

    return {
        "scan_summary": {
            "total_records_checked": total_scanned,
            "mismatches_found": len(mismatches),
            "status": "action_required" if mismatches else "clean",
        },
        "mismatches": mismatches,
    }


def _normalize_name_tokens(value: str) -> list[str]:
    """Helper to normalize names for comparison (lowercase, split on space/dot)."""
    return [token for token in value.lower().replace(".", " ").split() if token]


def scan_name_variance() -> dict[str, Any]:
    """Detect AD display names that do not align to legal or preferred Workday names.
    
    Returns:
        dict with 'scan_summary' and 'mismatches' array.
    """
    mismatches: list[dict[str, Any]] = []
    total_scanned = 0

    for employee_id, details in MOCK_WORKERS.items():
        total_scanned += 1
        legal_name = details.get("legal_name", "")
        preferred_name = details.get("preferred_name", "")
        ad_display_name = details.get("ad_display_name", "")

        if not legal_name or not ad_display_name:
            continue

        legal_tokens = _normalize_name_tokens(legal_name)
        preferred_tokens = _normalize_name_tokens(preferred_name)
        display_tokens = _normalize_name_tokens(ad_display_name)

        if not legal_tokens or not display_tokens:
            continue

        legal_first = legal_tokens[0]
        legal_last = legal_tokens[-1]
        preferred_first = preferred_tokens[0] if preferred_tokens else ""
        display_first = display_tokens[0]
        display_last = display_tokens[-1]

        first_name_aligned = display_first in {legal_first, preferred_first}
        last_name_aligned = display_last == legal_last

        if first_name_aligned and last_name_aligned:
            continue

        mismatches.append(
            {
                "employee_id": employee_id,
                "employee_name": details["name"],
                "workday_legal_name": legal_name,
                "workday_preferred_name": preferred_name,
                "ad_display_name": ad_display_name,
                "mismatch_type": "name_variance_requires_review",
                "severity": "low",
            }
        )

    return {
        "scan_summary": {
            "total_records_checked": total_scanned,
            "mismatches_found": len(mismatches),
            "status": "action_required" if mismatches else "clean",
        },
        "mismatches": mismatches,
    }
