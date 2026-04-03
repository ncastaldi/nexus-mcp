from typing import Any

# Mock dataset with reporting-line relationships for manager checks (WIS-017 prep)
MOCK_WORKERS: dict[str, dict[str, Any]] = {
    "EMP001": {
        "name": "Nathan",
        "status": "Active",
        "dept": "IT",
        "email": "nathan@example.com",
        "manager_id": "EMP010",
    },
    "EMP002": {
        "name": "Terminated User",
        "status": "Terminated",
        "dept": "Sales",
        "email": "user2@example.com",
        "manager_id": "EMP020",
    },
    "EMP003": {
        "name": "Alicia",
        "status": "Active",
        "dept": "IT",
        "email": "alicia@example.com",
        "manager_id": "EMP010",
    },
    "EMP004": {
        "name": "Jordan",
        "status": "Leave",
        "dept": "Finance",
        "email": "jordan@example.com",
        "manager_id": "EMP030",
    },
    "EMP010": {
        "name": "Priya Manager",
        "status": "Active",
        "dept": "IT",
        "email": "priya@example.com",
        "manager_id": "EMP100",
    },
    "EMP020": {
        "name": "Ramon Director",
        "status": "Active",
        "dept": "Sales",
        "email": "ramon@example.com",
        "manager_id": "EMP100",
    },
    "EMP030": {
        "name": "Morgan Lead",
        "status": "Active",
        "dept": "Finance",
        "email": "morgan@example.com",
        "manager_id": "EMP100",
    },
    "EMP100": {
        "name": "Chief Exec",
        "status": "Active",
        "dept": "Executive",
        "email": "ceo@example.com",
        "manager_id": "",
    },
    # Intentional unresolved manager reference for mismatch test scenarios
    "EMP777": {
        "name": "Mismatch Case",
        "status": "Active",
        "dept": "Operations",
        "email": "mismatch@example.com",
        "manager_id": "EMP999",
    },
}