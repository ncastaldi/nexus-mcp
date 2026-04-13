from lib.data import (
    scan_department_drift,
    scan_job_title_mismatches,
    scan_name_variance,
    scan_status_reconciliation_mismatches,
)
from server import (
    scan_department_mismatches,
    scan_job_title_drift,
    scan_name_variance_mismatches,
    scan_status_reconciliation,
)


def test_scan_status_reconciliation_mismatches_returns_expected_record() -> None:
    result = scan_status_reconciliation_mismatches()

    assert result["scan_summary"]["total_records_checked"] == 9
    assert result["scan_summary"]["mismatches_found"] == 1
    assert result["mismatches"] == [
        {
            "employee_id": "EMP002",
            "employee_name": "Terminated User",
            "workday_status": "Terminated",
            "ad_enabled": True,
            "mismatch_type": "terminated_but_enabled",
            "severity": "high",
        }
    ]


def test_scan_job_title_mismatches_returns_expected_record() -> None:
    result = scan_job_title_mismatches()

    assert result["scan_summary"]["total_records_checked"] == 9
    assert result["scan_summary"]["mismatches_found"] == 1
    assert result["mismatches"] == [
        {
            "employee_id": "EMP003",
            "employee_name": "Alicia",
            "workday_title": "Senior Systems Analyst",
            "ad_title": "Systems Analyst",
            "mismatch_type": "job_title_mismatch",
            "severity": "medium",
        }
    ]


def test_scan_department_drift_returns_expected_record() -> None:
    result = scan_department_drift()

    assert result["scan_summary"]["total_records_checked"] == 9
    assert result["scan_summary"]["mismatches_found"] == 1
    assert result["mismatches"] == [
        {
            "employee_id": "EMP004",
            "employee_name": "Jordan",
            "workday_department": "Finance",
            "workday_cost_center": "CC300-FIN",
            "ad_department": "Accounting",
            "mismatch_type": "department_drift",
            "severity": "medium",
        }
    ]


def test_scan_name_variance_returns_expected_records() -> None:
    result = scan_name_variance()

    assert result["scan_summary"]["total_records_checked"] == 9
    assert result["scan_summary"]["mismatches_found"] == 3
    assert [item["employee_id"] for item in result["mismatches"]] == [
        "EMP010",
        "EMP020",
        "EMP777",
    ]


def test_scan_status_reconciliation_tool_matches_detector() -> None:
    assert scan_status_reconciliation() == scan_status_reconciliation_mismatches()


def test_scan_job_title_drift_tool_matches_detector() -> None:
    assert scan_job_title_drift() == scan_job_title_mismatches()


def test_scan_department_mismatches_tool_matches_detector() -> None:
    assert scan_department_mismatches() == scan_department_drift()


def test_scan_name_variance_mismatches_tool_matches_detector() -> None:
    assert scan_name_variance_mismatches() == scan_name_variance()