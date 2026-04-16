"""Nexus-MCP Mock Data Library.

Realistic enterprise mock data for all 6 shards.
Deliberate drift is seeded across systems to make audit tools return meaningful results.

Identity / Workday drift scenarios:
  - Bob Martinez:    jobTitle drift — AD "Sr. Software Engineer" vs Workday/Entra "Software Engineer"
  - Carol Chen:      department drift — AD "Engineering" vs Workday/Entra "Product Management"
  - Grace Lee:       title drift — AD "Human Resources Director" vs Workday "HR Director"
  - Frank Davis:     department drift — AD "Information Technology" vs Workday "IT Operations"
  - Taylor Brooks:   terminated in Workday but AD account still ENABLED (HIGH severity)
  - Henry Park:      Active in Workday (new hire) but AD account DISABLED / not yet provisioned
  - David Kim:       AD account disabled but Entra account still enabled (cloud/on-prem split)
  - Emma Wilson:     AD stale account — no login in 120 days

Asset drift scenarios:
  - LAPTOP-CAROL-03: serialNumber differs — Lansweeper "SN-CAROL-03A" vs Intune "SN-CAROL-03B"
  - SERVER-PROD-01:  exists in Lansweeper + Helix CMDB but not in Intune (unmanaged server)

Workday worker objects follow the REST API v6 staffing/workers response shape:
  https://community.workday.com/sites/default/files/file-hosting/restapi/
"""

import datetime

_NOW = datetime.datetime.now(datetime.timezone.utc)
_FMT = "%Y-%m-%dT%H:%M:%SZ"
_D = lambda days: (_NOW - datetime.timedelta(days=days)).strftime(_FMT)
_DATE = lambda days: (_NOW - datetime.timedelta(days=days)).strftime("%Y-%m-%d")
_TODAY = _NOW.strftime("%Y-%m-%d")


# ─── Active Directory ─────────────────────────────────────────────────────────

AD_USERS: list[dict] = [
    {
        "dn": "CN=Alice Johnson,OU=Users,DC=corp,DC=nexus,DC=local",
        "sAMAccountName": "alicej",
        "displayName": "Alice Johnson",
        "mail": "alice.johnson@nexus.corp",
        "department": "Engineering",
        "title": "Engineering Manager",
        "manager": "CN=Frank Davis,OU=Users,DC=corp,DC=nexus,DC=local",
        "memberOf": "CN=Engineering,OU=Groups,DC=corp,DC=nexus,DC=local",
        "employeeID": "EMP-1001",
        "userAccountControl": "512",
        "lastLogonTimestamp": _D(3),
        "whenCreated": "2019-04-01T08:00:00Z",
        "telephoneNumber": "+1-555-0101",
        "physicalDeliveryOfficeName": "HQ-Floor3",
        "cn": "Alice Johnson",
    },
    {
        "dn": "CN=Bob Martinez,OU=Users,DC=corp,DC=nexus,DC=local",
        "sAMAccountName": "bobm",
        "displayName": "Bob Martinez",
        "mail": "bob.martinez@nexus.corp",
        "department": "Engineering",
        # ⚡ DRIFT: AD title doesn't match Workday/Entra ("Software Engineer")
        "title": "Sr. Software Engineer",
        "manager": "CN=Alice Johnson,OU=Users,DC=corp,DC=nexus,DC=local",
        "memberOf": "CN=Engineering,OU=Groups,DC=corp,DC=nexus,DC=local",
        "employeeID": "EMP-1002",
        "userAccountControl": "512",
        "lastLogonTimestamp": _D(1),
        "whenCreated": "2021-06-15T08:00:00Z",
        "telephoneNumber": "+1-555-0102",
        "physicalDeliveryOfficeName": "HQ-Floor3",
        "cn": "Bob Martinez",
    },
    {
        "dn": "CN=Carol Chen,OU=Users,DC=corp,DC=nexus,DC=local",
        "sAMAccountName": "carolc",
        "displayName": "Carol Chen",
        "mail": "carol.chen@nexus.corp",
        # ⚡ DRIFT: AD department is "Engineering" but Workday/Entra is "Product Management"
        "department": "Engineering",
        "title": "Product Manager",
        "manager": "CN=Alice Johnson,OU=Users,DC=corp,DC=nexus,DC=local",
        "memberOf": "CN=Product,OU=Groups,DC=corp,DC=nexus,DC=local",
        "employeeID": "EMP-1003",
        "userAccountControl": "512",
        "lastLogonTimestamp": _D(2),
        "whenCreated": "2020-09-10T08:00:00Z",
        "telephoneNumber": "+1-555-0103",
        "physicalDeliveryOfficeName": "HQ-Floor2",
        "cn": "Carol Chen",
    },
    {
        "dn": "CN=David Kim,OU=Users,DC=corp,DC=nexus,DC=local",
        "sAMAccountName": "davidk",
        "displayName": "David Kim",
        "mail": "david.kim@nexus.corp",
        "department": "IT Operations",
        "title": "Systems Administrator",
        "manager": "CN=Frank Davis,OU=Users,DC=corp,DC=nexus,DC=local",
        "memberOf": "CN=IT Ops,OU=Groups,DC=corp,DC=nexus,DC=local",
        "employeeID": "EMP-1004",
        # ⚡ DRIFT: disabled in AD but active in Entra
        "userAccountControl": "514",
        "lastLogonTimestamp": _D(45),
        "whenCreated": "2018-02-20T08:00:00Z",
        "telephoneNumber": "+1-555-0104",
        "physicalDeliveryOfficeName": "HQ-Floor1",
        "cn": "David Kim",
    },
    {
        "dn": "CN=Emma Wilson,OU=Users,DC=corp,DC=nexus,DC=local",
        "sAMAccountName": "emmaw",
        "displayName": "Emma Wilson",
        "mail": "emma.wilson@nexus.corp",
        "department": "Human Resources",
        "title": "HR Specialist",
        "manager": "CN=Grace Lee,OU=Users,DC=corp,DC=nexus,DC=local",
        "memberOf": "CN=HR,OU=Groups,DC=corp,DC=nexus,DC=local",
        "employeeID": "EMP-1005",
        "userAccountControl": "512",
        # ⚡ Stale: no login in 120 days
        "lastLogonTimestamp": _D(120),
        "whenCreated": "2017-11-05T08:00:00Z",
        "telephoneNumber": "+1-555-0105",
        "physicalDeliveryOfficeName": "HQ-Floor2",
        "cn": "Emma Wilson",
    },
    {
        "dn": "CN=Frank Davis,OU=Users,DC=corp,DC=nexus,DC=local",
        "sAMAccountName": "frankd",
        "displayName": "Frank Davis",
        "mail": "frank.davis@nexus.corp",
        # ⚡ DRIFT: AD department is "Information Technology" but Workday has "IT Operations"
        "department": "Information Technology",
        "title": "IT Director",
        "manager": None,
        "memberOf": "CN=IT Ops,OU=Groups,DC=corp,DC=nexus,DC=local",
        "employeeID": "EMP-1006",
        "userAccountControl": "512",
        "lastLogonTimestamp": _D(0),
        "whenCreated": "2016-03-01T08:00:00Z",
        "telephoneNumber": "+1-555-0106",
        "physicalDeliveryOfficeName": "HQ-Floor1",
        "cn": "Frank Davis",
    },
    {
        "dn": "CN=Grace Lee,OU=Users,DC=corp,DC=nexus,DC=local",
        "sAMAccountName": "gracel",
        "displayName": "Grace Lee",
        "mail": "grace.lee@nexus.corp",
        "department": "Human Resources",
        # ⚡ DRIFT: AD title is "Human Resources Director" but Workday has "HR Director"
        "title": "Human Resources Director",
        "manager": None,
        "memberOf": "CN=HR,OU=Groups,DC=corp,DC=nexus,DC=local",
        "employeeID": "EMP-1007",
        "userAccountControl": "512",
        "lastLogonTimestamp": _D(1),
        "whenCreated": "2016-07-15T08:00:00Z",
        "telephoneNumber": "+1-555-0107",
        "physicalDeliveryOfficeName": "HQ-Floor2",
        "cn": "Grace Lee",
    },
    {
        # ⚡ NEW HIRE NOT PROVISIONED: Active in Workday but AD account is disabled
        "dn": "CN=Henry Park,OU=Users,DC=corp,DC=nexus,DC=local",
        "sAMAccountName": "henryp",
        "displayName": "Henry Park",
        "mail": "henry.park@nexus.corp",
        "department": "Engineering",
        "title": "Junior Software Engineer",
        "manager": "CN=Alice Johnson,OU=Users,DC=corp,DC=nexus,DC=local",
        "memberOf": "CN=Engineering,OU=Groups,DC=corp,DC=nexus,DC=local",
        "employeeID": "EMP-1008",
        "userAccountControl": "514",
        "lastLogonTimestamp": None,
        "whenCreated": _D(5),
        "telephoneNumber": "+1-555-0108",
        "physicalDeliveryOfficeName": "HQ-Floor3",
        "cn": "Henry Park",
    },
    {
        # ⚡ TERMINATED BUT ENABLED: Terminated in Workday; AD account still active
        "dn": "CN=Taylor Brooks,OU=Users,DC=corp,DC=nexus,DC=local",
        "sAMAccountName": "taylorb",
        "displayName": "Taylor Brooks",
        "mail": "taylor.brooks@nexus.corp",
        "department": "Sales",
        "title": "Account Executive",
        "manager": "CN=Frank Davis,OU=Users,DC=corp,DC=nexus,DC=local",
        "memberOf": "CN=VPN Users,OU=Groups,DC=corp,DC=nexus,DC=local",
        "employeeID": "EMP-1009",
        "userAccountControl": "512",
        "lastLogonTimestamp": _D(14),
        "whenCreated": "2022-03-15T08:00:00Z",
        "telephoneNumber": "+1-555-0109",
        "physicalDeliveryOfficeName": "HQ-Floor2",
        "cn": "Taylor Brooks",
    },
]

AD_USERS_BY_SAM = {u["sAMAccountName"]: u for u in AD_USERS}
AD_USERS_BY_EMAIL = {u["mail"]: u for u in AD_USERS}

AD_GROUPS: list[dict] = [
    {"dn": "CN=Engineering,OU=Groups,DC=corp,DC=nexus,DC=local", "cn": "Engineering",
     "description": "All engineering staff", "memberCount": 3, "groupType": "-2147483646", "whenCreated": "2016-01-01T00:00:00Z"},
    {"dn": "CN=IT Ops,OU=Groups,DC=corp,DC=nexus,DC=local", "cn": "IT Ops",
     "description": "IT Operations team", "memberCount": 2, "groupType": "-2147483646", "whenCreated": "2016-01-01T00:00:00Z"},
    {"dn": "CN=HR,OU=Groups,DC=corp,DC=nexus,DC=local", "cn": "HR",
     "description": "Human Resources", "memberCount": 2, "groupType": "-2147483648", "whenCreated": "2016-01-01T00:00:00Z"},
    {"dn": "CN=Product,OU=Groups,DC=corp,DC=nexus,DC=local", "cn": "Product",
     "description": "Product Management team", "memberCount": 1, "groupType": "-2147483646", "whenCreated": "2018-06-01T00:00:00Z"},
    {"dn": "CN=VPN Users,OU=Groups,DC=corp,DC=nexus,DC=local", "cn": "VPN Users",
     "description": "Remote access group", "memberCount": 6, "groupType": "-2147483648", "whenCreated": "2017-01-01T00:00:00Z"},
]


# ─── Microsoft Entra ID ───────────────────────────────────────────────────────

ENTRA_USERS: list[dict] = [
    {
        "id": "aaa11111-0000-0000-0000-000000000001",
        "displayName": "Alice Johnson",
        "userPrincipalName": "alice.johnson@nexus.corp",
        "mail": "alice.johnson@nexus.corp",
        "jobTitle": "Engineering Manager",
        "department": "Engineering",
        "accountEnabled": True,
        "createdDateTime": "2019-04-01T08:00:00Z",
        "onPremisesSyncEnabled": True,
        "assignedLicenses": [{"skuId": "6fd2c87f-b296-42f0-b197-1e91e994b900"}],
    },
    {
        "id": "aaa11111-0000-0000-0000-000000000002",
        "displayName": "Bob Martinez",
        "userPrincipalName": "bob.martinez@nexus.corp",
        "mail": "bob.martinez@nexus.corp",
        # ⚡ DRIFT: Entra has "Software Engineer" but AD has "Sr. Software Engineer"
        "jobTitle": "Software Engineer",
        "department": "Engineering",
        "accountEnabled": True,
        "createdDateTime": "2021-06-15T08:00:00Z",
        "onPremisesSyncEnabled": True,
        "assignedLicenses": [{"skuId": "6fd2c87f-b296-42f0-b197-1e91e994b900"}],
    },
    {
        "id": "aaa11111-0000-0000-0000-000000000003",
        "displayName": "Carol Chen",
        "userPrincipalName": "carol.chen@nexus.corp",
        "mail": "carol.chen@nexus.corp",
        "jobTitle": "Product Manager",
        # ⚡ DRIFT: Entra has "Product Management" but AD has "Engineering"
        "department": "Product Management",
        "accountEnabled": True,
        "createdDateTime": "2020-09-10T08:00:00Z",
        "onPremisesSyncEnabled": True,
        "assignedLicenses": [{"skuId": "6fd2c87f-b296-42f0-b197-1e91e994b900"}],
    },
    {
        "id": "aaa11111-0000-0000-0000-000000000004",
        "displayName": "David Kim",
        "userPrincipalName": "david.kim@nexus.corp",
        "mail": "david.kim@nexus.corp",
        "jobTitle": "Systems Administrator",
        "department": "IT Operations",
        # ⚡ DRIFT: Entra still enabled but AD is disabled
        "accountEnabled": True,
        "createdDateTime": "2018-02-20T08:00:00Z",
        "onPremisesSyncEnabled": True,
        "assignedLicenses": [{"skuId": "6fd2c87f-b296-42f0-b197-1e91e994b900"}],
    },
    {
        "id": "aaa11111-0000-0000-0000-000000000005",
        "displayName": "Emma Wilson",
        "userPrincipalName": "emma.wilson@nexus.corp",
        "mail": "emma.wilson@nexus.corp",
        "jobTitle": "HR Specialist",
        "department": "HR",
        "accountEnabled": True,
        "createdDateTime": "2017-11-05T08:00:00Z",
        "onPremisesSyncEnabled": True,
        "assignedLicenses": [{"skuId": "6fd2c87f-b296-42f0-b197-1e91e994b900"}],
    },
    {
        "id": "aaa11111-0000-0000-0000-000000000006",
        "displayName": "Frank Davis",
        "userPrincipalName": "frank.davis@nexus.corp",
        "mail": "frank.davis@nexus.corp",
        "jobTitle": "IT Director",
        "department": "IT Operations",
        "accountEnabled": True,
        "createdDateTime": "2016-03-01T08:00:00Z",
        "onPremisesSyncEnabled": True,
        "assignedLicenses": [{"skuId": "6fd2c87f-b296-42f0-b197-1e91e994b900"}],
    },
    {
        "id": "aaa11111-0000-0000-0000-000000000007",
        "displayName": "Grace Lee",
        "userPrincipalName": "grace.lee@nexus.corp",
        "mail": "grace.lee@nexus.corp",
        "jobTitle": "HR Director",
        "department": "HR",
        "accountEnabled": True,
        "createdDateTime": "2016-07-15T08:00:00Z",
        "onPremisesSyncEnabled": True,
        "assignedLicenses": [{"skuId": "6fd2c87f-b296-42f0-b197-1e91e994b900"}],
    },
    {
        "id": "aaa11111-0000-0000-0000-000000000008",
        "displayName": "Svc-Monitoring",
        "userPrincipalName": "svc-monitoring@nexus.corp",
        "mail": None,
        "jobTitle": None,
        "department": None,
        "accountEnabled": True,
        "createdDateTime": "2020-01-01T00:00:00Z",
        "onPremisesSyncEnabled": False,
        "assignedLicenses": [],
    },
    {
        # ⚡ TERMINATED BUT STILL ENABLED in Entra (cloud side of the same terminated scenario)
        "id": "aaa11111-0000-0000-0000-000000000009",
        "displayName": "Taylor Brooks",
        "userPrincipalName": "taylor.brooks@nexus.corp",
        "mail": "taylor.brooks@nexus.corp",
        "jobTitle": "Account Executive",
        "department": "Sales",
        "accountEnabled": True,
        "createdDateTime": "2022-03-15T08:00:00Z",
        "onPremisesSyncEnabled": True,
        "assignedLicenses": [{"skuId": "6fd2c87f-b296-42f0-b197-1e91e994b900"}],
    },
]

ENTRA_USERS_BY_MAIL = {u["mail"]: u for u in ENTRA_USERS if u.get("mail")}
ENTRA_USERS_BY_UPN = {u["userPrincipalName"]: u for u in ENTRA_USERS}

ENTRA_GROUPS: list[dict] = [
    {"id": "ggg00001", "displayName": "Engineering", "description": "Engineering staff", "groupTypes": ["Unified"], "mailEnabled": True},
    {"id": "ggg00002", "displayName": "IT Operations", "description": "IT Ops team", "groupTypes": [], "mailEnabled": False},
    {"id": "ggg00003", "displayName": "HR", "description": "Human Resources", "groupTypes": [], "mailEnabled": False},
    {"id": "ggg00004", "displayName": "All Employees", "description": "Company-wide distribution list", "groupTypes": [], "mailEnabled": True},
    {"id": "ggg00005", "displayName": "Intune Admins", "description": "Intune device management admins", "groupTypes": [], "mailEnabled": False},
]

ENTRA_CONDITIONAL_ACCESS_POLICIES: list[dict] = [
    {
        "id": "cap-001", "displayName": "Require MFA for All Users",
        "state": "enabled",
        "conditions": {"users": {"includeUsers": ["All"]}, "applications": {"includeApplications": ["All"]}},
        "grantControls": {"operator": "OR", "builtInControls": ["mfa"]},
    },
    {
        "id": "cap-002", "displayName": "Block Legacy Authentication",
        "state": "enabled",
        "conditions": {"clientAppTypes": ["exchangeActiveSync", "other"]},
        "grantControls": {"operator": "OR", "builtInControls": ["block"]},
    },
    {
        "id": "cap-003", "displayName": "Require Compliant Device for Corp Apps",
        "state": "enabledForReportingButNotEnforced",
        "conditions": {"users": {"includeUsers": ["All"]}, "applications": {"includeApplications": ["Office365"]}},
        "grantControls": {"operator": "AND", "builtInControls": ["compliantDevice"]},
    },
]

ENTRA_RISKY_USERS: list[dict] = [
    {
        "id": "aaa11111-0000-0000-0000-000000000002",
        "isDeleted": False,
        "isProcessing": False,
        "riskLevel": "medium",
        "riskState": "atRisk",
        "riskDetail": "userPassedMFADrivenByRiskBasedPolicy",
        "riskLastUpdatedDateTime": _D(2),
        "userDisplayName": "Bob Martinez",
        "userPrincipalName": "bob.martinez@nexus.corp",
    },
]

ENTRA_SIGNIN_LOGS: list[dict] = [
    {
        "id": "sign-001", "createdDateTime": _D(0),
        "userDisplayName": "Alice Johnson", "userPrincipalName": "alice.johnson@nexus.corp",
        "appDisplayName": "Microsoft Teams", "ipAddress": "203.0.113.42",
        "status": {"errorCode": 0, "failureReason": None}, "location": {"city": "New York", "countryOrRegion": "US"},
    },
    {
        "id": "sign-002", "createdDateTime": _D(0),
        "userDisplayName": "Bob Martinez", "userPrincipalName": "bob.martinez@nexus.corp",
        "appDisplayName": "GitHub Enterprise", "ipAddress": "198.51.100.17",
        "status": {"errorCode": 50126, "failureReason": "Invalid username or password"}, "location": {"city": "Unknown", "countryOrRegion": "RU"},
    },
    {
        "id": "sign-003", "createdDateTime": _D(1),
        "userDisplayName": "Frank Davis", "userPrincipalName": "frank.davis@nexus.corp",
        "appDisplayName": "Azure Portal", "ipAddress": "203.0.113.10",
        "status": {"errorCode": 0, "failureReason": None}, "location": {"city": "New York", "countryOrRegion": "US"},
    },
]

ENTRA_SERVICE_PRINCIPALS: list[dict] = [
    {"id": "sp-001", "displayName": "Nexus-MCP Integration App", "appId": "app-nexus-001", "servicePrincipalType": "Application", "accountEnabled": True},
    {"id": "sp-002", "displayName": "Lansweeper Connector", "appId": "app-ls-002", "servicePrincipalType": "Application", "accountEnabled": True},
    {"id": "sp-003", "displayName": "SIEM Integration", "appId": "app-siem-003", "servicePrincipalType": "Application", "accountEnabled": False},
]


# ─── Workday ──────────────────────────────────────────────────────────────────

WORKDAY_WORKERS: list[dict] = [
    {
        # Workday REST API v6 staffing/workers response shape
        "id": "WD-EMP-1001",
        "descriptor": "Alice Johnson",
        "employeeID": "EMP-1001",
        "firstName": "Alice",
        "lastName": "Johnson",
        "legalName": "Alice Mary Johnson",
        "preferredName": "Alice",
        "primaryWorkEmail": "alice.johnson@nexus.corp",
        "primaryWorkPhone": "+1-555-0101",
        "hireDate": "2019-04-01",
        "effectiveDate": _TODAY,
        "primaryJob": {
            "jobProfile": {"descriptor": "Engineering Manager", "id": "PROFILE-101"},
            "businessUnit": {"descriptor": "Engineering", "id": "ORG-101"},
            "location": {"descriptor": "New York HQ", "id": "LOC-001"},
            "manager": {
                "descriptor": "Frank Davis",
                "primaryWorkEmail": "frank.davis@nexus.corp",
                "id": "WD-EMP-1006",
            },
        },
        "supervisoryOrganization": {"descriptor": "Engineering", "id": "ORG-101"},
        "costCenter": {"descriptor": "CC110-ENG", "id": "CC-101"},
        "workerType": {"descriptor": "Employee"},
        "workerStatus": {"descriptor": "Active"},
    },
    {
        "id": "WD-EMP-1002",
        "descriptor": "Bob Martinez",
        "employeeID": "EMP-1002",
        "firstName": "Bob",
        "lastName": "Martinez",
        "legalName": "Robert Martinez",
        "preferredName": "Bob",
        "primaryWorkEmail": "bob.martinez@nexus.corp",
        "primaryWorkPhone": "+1-555-0102",
        "hireDate": "2021-06-15",
        "effectiveDate": _TODAY,
        "primaryJob": {
            # ⚡ DRIFT: Workday says "Software Engineer" — AD says "Sr. Software Engineer"
            "jobProfile": {"descriptor": "Software Engineer", "id": "PROFILE-102"},
            "businessUnit": {"descriptor": "Engineering", "id": "ORG-101"},
            "location": {"descriptor": "New York HQ", "id": "LOC-001"},
            "manager": {
                "descriptor": "Alice Johnson",
                "primaryWorkEmail": "alice.johnson@nexus.corp",
                "id": "WD-EMP-1001",
            },
        },
        "supervisoryOrganization": {"descriptor": "Engineering", "id": "ORG-101"},
        "costCenter": {"descriptor": "CC110-ENG", "id": "CC-101"},
        "workerType": {"descriptor": "Employee"},
        "workerStatus": {"descriptor": "Active"},
    },
    {
        "id": "WD-EMP-1003",
        "descriptor": "Carol Chen",
        "employeeID": "EMP-1003",
        "firstName": "Carol",
        "lastName": "Chen",
        "legalName": "Carol Chen",
        "preferredName": "Carol",
        "primaryWorkEmail": "carol.chen@nexus.corp",
        "primaryWorkPhone": "+1-555-0103",
        "hireDate": "2020-09-10",
        "effectiveDate": _TODAY,
        "primaryJob": {
            "jobProfile": {"descriptor": "Product Manager", "id": "PROFILE-103"},
            # ⚡ DRIFT: Workday dept "Product Management" — AD has "Engineering"
            "businessUnit": {"descriptor": "Product Management", "id": "ORG-102"},
            "location": {"descriptor": "New York HQ", "id": "LOC-001"},
            "manager": {
                "descriptor": "Alice Johnson",
                "primaryWorkEmail": "alice.johnson@nexus.corp",
                "id": "WD-EMP-1001",
            },
        },
        "supervisoryOrganization": {"descriptor": "Product Management", "id": "ORG-102"},
        "costCenter": {"descriptor": "CC120-PROD", "id": "CC-102"},
        "workerType": {"descriptor": "Employee"},
        "workerStatus": {"descriptor": "Active"},
    },
    {
        "id": "WD-EMP-1004",
        "descriptor": "David Kim",
        "employeeID": "EMP-1004",
        "firstName": "David",
        "lastName": "Kim",
        "legalName": "David Kim",
        "preferredName": "David",
        "primaryWorkEmail": "david.kim@nexus.corp",
        "primaryWorkPhone": "+1-555-0104",
        "hireDate": "2018-02-20",
        "effectiveDate": _TODAY,
        "primaryJob": {
            "jobProfile": {"descriptor": "Systems Administrator", "id": "PROFILE-104"},
            "businessUnit": {"descriptor": "IT Operations", "id": "ORG-103"},
            "location": {"descriptor": "New York HQ", "id": "LOC-001"},
            "manager": {
                "descriptor": "Frank Davis",
                "primaryWorkEmail": "frank.davis@nexus.corp",
                "id": "WD-EMP-1006",
            },
        },
        "supervisoryOrganization": {"descriptor": "IT Operations", "id": "ORG-103"},
        "costCenter": {"descriptor": "CC130-ITOPS", "id": "CC-103"},
        "workerType": {"descriptor": "Employee"},
        "workerStatus": {"descriptor": "Leave of Absence"},
    },
    {
        "id": "WD-EMP-1005",
        "descriptor": "Emma Wilson",
        "employeeID": "EMP-1005",
        "firstName": "Emma",
        "lastName": "Thompson",
        # ⚡ NAME VARIANCE: recently married — legal name updated in Workday but AD still shows maiden name "Wilson"
        "legalName": "Emma Thompson",
        "preferredName": "Emma",
        "primaryWorkEmail": "emma.wilson@nexus.corp",
        "primaryWorkPhone": "+1-555-0105",
        "hireDate": "2017-11-05",
        "effectiveDate": _TODAY,
        "primaryJob": {
            "jobProfile": {"descriptor": "HR Specialist", "id": "PROFILE-105"},
            "businessUnit": {"descriptor": "Human Resources", "id": "ORG-104"},
            "location": {"descriptor": "New York HQ", "id": "LOC-001"},
            "manager": {
                "descriptor": "Grace Lee",
                "primaryWorkEmail": "grace.lee@nexus.corp",
                "id": "WD-EMP-1007",
            },
        },
        "supervisoryOrganization": {"descriptor": "Human Resources", "id": "ORG-104"},
        "costCenter": {"descriptor": "CC140-HR", "id": "CC-104"},
        "workerType": {"descriptor": "Employee"},
        "workerStatus": {"descriptor": "Active"},
    },
    {
        "id": "WD-EMP-1006",
        "descriptor": "Frank Davis",
        "employeeID": "EMP-1006",
        "firstName": "Frank",
        "lastName": "Davis",
        "legalName": "Franklin Davis",
        "preferredName": "Frank",
        "primaryWorkEmail": "frank.davis@nexus.corp",
        "primaryWorkPhone": "+1-555-0106",
        "hireDate": "2016-03-01",
        "effectiveDate": _TODAY,
        "primaryJob": {
            "jobProfile": {"descriptor": "IT Director", "id": "PROFILE-106"},
            # ⚡ DRIFT: Workday dept "IT Operations" — AD has "Information Technology"
            "businessUnit": {"descriptor": "IT Operations", "id": "ORG-103"},
            "location": {"descriptor": "New York HQ", "id": "LOC-001"},
            "manager": None,
        },
        "supervisoryOrganization": {"descriptor": "IT Operations", "id": "ORG-103"},
        "costCenter": {"descriptor": "CC130-ITOPS", "id": "CC-103"},
        "workerType": {"descriptor": "Employee"},
        "workerStatus": {"descriptor": "Active"},
    },
    {
        "id": "WD-EMP-1007",
        "descriptor": "Grace Lee",
        "employeeID": "EMP-1007",
        "firstName": "Grace",
        "lastName": "Lee",
        "legalName": "Grace Lee",
        "preferredName": "Grace",
        "primaryWorkEmail": "grace.lee@nexus.corp",
        "primaryWorkPhone": "+1-555-0107",
        "hireDate": "2016-07-15",
        "effectiveDate": _TODAY,
        "primaryJob": {
            # ⚡ DRIFT: Workday title "HR Director" — AD has "Human Resources Director"
            "jobProfile": {"descriptor": "HR Director", "id": "PROFILE-107"},
            "businessUnit": {"descriptor": "Human Resources", "id": "ORG-104"},
            "location": {"descriptor": "New York HQ", "id": "LOC-001"},
            "manager": None,
        },
        "supervisoryOrganization": {"descriptor": "Human Resources", "id": "ORG-104"},
        "costCenter": {"descriptor": "CC140-HR", "id": "CC-104"},
        "workerType": {"descriptor": "Employee"},
        "workerStatus": {"descriptor": "Active"},
    },
    {
        # ⚡ NEW HIRE: Active in Workday; AD account created but still DISABLED (not provisioned)
        "id": "WD-EMP-1008",
        "descriptor": "Henry Park",
        "employeeID": "EMP-1008",
        "firstName": "Henry",
        "lastName": "Park",
        "legalName": "Henry Park",
        "preferredName": "Henry",
        "primaryWorkEmail": "henry.park@nexus.corp",
        "primaryWorkPhone": "+1-555-0108",
        "hireDate": _DATE(5),
        "effectiveDate": _TODAY,
        "primaryJob": {
            "jobProfile": {"descriptor": "Junior Software Engineer", "id": "PROFILE-108"},
            "businessUnit": {"descriptor": "Engineering", "id": "ORG-101"},
            "location": {"descriptor": "New York HQ", "id": "LOC-001"},
            "manager": {
                "descriptor": "Alice Johnson",
                "primaryWorkEmail": "alice.johnson@nexus.corp",
                "id": "WD-EMP-1001",
            },
        },
        "supervisoryOrganization": {"descriptor": "Engineering", "id": "ORG-101"},
        "costCenter": {"descriptor": "CC110-ENG", "id": "CC-101"},
        "workerType": {"descriptor": "Employee"},
        "workerStatus": {"descriptor": "Active"},
    },
    {
        # ⚡ TERMINATED BUT AD STILL ENABLED — highest severity drift scenario
        "id": "WD-EMP-1009",
        "descriptor": "Taylor Brooks",
        "employeeID": "EMP-1009",
        "firstName": "Taylor",
        "lastName": "Brooks",
        "legalName": "Taylor Brooks",
        "preferredName": "Taylor",
        "primaryWorkEmail": "taylor.brooks@nexus.corp",
        "primaryWorkPhone": "+1-555-0109",
        "hireDate": "2022-03-15",
        "effectiveDate": _TODAY,
        "primaryJob": {
            "jobProfile": {"descriptor": "Account Executive", "id": "PROFILE-109"},
            "businessUnit": {"descriptor": "Sales", "id": "ORG-105"},
            "location": {"descriptor": "New York HQ", "id": "LOC-001"},
            "manager": {
                "descriptor": "Frank Davis",
                "primaryWorkEmail": "frank.davis@nexus.corp",
                "id": "WD-EMP-1006",
            },
        },
        "supervisoryOrganization": {"descriptor": "Sales", "id": "ORG-105"},
        "costCenter": {"descriptor": "CC150-SALES", "id": "CC-105"},
        "workerType": {"descriptor": "Employee"},
        "workerStatus": {"descriptor": "Terminated"},
    },
]

WORKDAY_WORKERS_BY_EMAIL = {w["primaryWorkEmail"]: w for w in WORKDAY_WORKERS}
WORKDAY_WORKERS_BY_ID = {w["id"]: w for w in WORKDAY_WORKERS}

WORKDAY_POSITIONS: list[dict] = [
    {"id": "POS-2001", "descriptor": "Senior Product Manager", "status": "Open", "businessUnit": "Product Management", "location": "New York HQ"},
    {"id": "POS-2002", "descriptor": "DevOps Engineer", "status": "Open", "businessUnit": "Engineering", "location": "New York HQ"},
    {"id": "POS-2003", "descriptor": "HR Business Partner", "status": "Open", "businessUnit": "Human Resources", "location": "Remote"},
    {"id": "POS-2004", "descriptor": "Engineering Manager", "status": "Filled", "businessUnit": "Engineering", "location": "New York HQ"},
]

WORKDAY_ORGANIZATIONS: list[dict] = [
    {"id": "ORG-100", "descriptor": "Nexus Corp", "type": "Company", "headcount": 9},
    {"id": "ORG-101", "descriptor": "Engineering", "type": "Supervisory", "headcount": 3, "parent": "ORG-100"},
    {"id": "ORG-102", "descriptor": "Product Management", "type": "Supervisory", "headcount": 1, "parent": "ORG-100"},
    {"id": "ORG-103", "descriptor": "IT Operations", "type": "Supervisory", "headcount": 2, "parent": "ORG-100"},
    {"id": "ORG-104", "descriptor": "Human Resources", "type": "Supervisory", "headcount": 2, "parent": "ORG-100"},
    {"id": "ORG-105", "descriptor": "Sales", "type": "Supervisory", "headcount": 1, "parent": "ORG-100"},
]

WORKDAY_COMPENSATION: dict[str, dict] = {
    "WD-EMP-1001": {"grade": "G7", "salaryRange": {"min": 130000, "max": 170000, "currency": "USD"}, "payFrequency": "Annual"},
    "WD-EMP-1002": {"grade": "G5", "salaryRange": {"min": 95000, "max": 125000, "currency": "USD"}, "payFrequency": "Annual"},
    "WD-EMP-1003": {"grade": "G6", "salaryRange": {"min": 110000, "max": 145000, "currency": "USD"}, "payFrequency": "Annual"},
    "WD-EMP-1004": {"grade": "G4", "salaryRange": {"min": 80000, "max": 105000, "currency": "USD"}, "payFrequency": "Annual"},
    "WD-EMP-1005": {"grade": "G3", "salaryRange": {"min": 65000, "max": 85000, "currency": "USD"}, "payFrequency": "Annual"},
    "WD-EMP-1006": {"grade": "G8", "salaryRange": {"min": 155000, "max": 200000, "currency": "USD"}, "payFrequency": "Annual"},
    "WD-EMP-1007": {"grade": "G7", "salaryRange": {"min": 130000, "max": 170000, "currency": "USD"}, "payFrequency": "Annual"},
    "WD-EMP-1008": {"grade": "G2", "salaryRange": {"min": 75000, "max": 95000, "currency": "USD"}, "payFrequency": "Annual"},
    "WD-EMP-1009": {"grade": "G4", "salaryRange": {"min": 80000, "max": 105000, "currency": "USD"}, "payFrequency": "Annual"},
}


# ─── BMC Helix ITSM ───────────────────────────────────────────────────────────

def _helix_entry(entry_id: str, values: dict) -> dict:
    return {"_links": {"self": [{"href": f"/api/arsys/v1/entry/{entry_id}"}]}, "values": values}


HELIX_INCIDENTS: list[dict] = [
    _helix_entry("INC0001234", {
        "Incident Number": "INC0001234",
        "Status": "In Progress",
        "Priority": "1-Critical",
        "Summary": "LAPTOP-BOB-02 BitLocker encryption disabled — compliance violation",
        "Description": "Intune compliance check detected BitLocker is disabled on LAPTOP-BOB-02. Requires immediate remediation.",
        "Assignee": "Frank Davis",
        "Assigned Group": "IT Operations",
        "Customer First Name": "Bob",
        "Customer Last Name": "Martinez",
        "Submit Date": _D(1),
        "Last Modified Date": _D(0),
        "CI Name": "LAPTOP-BOB-02",
        "Resolution": None,
    }),
    _helix_entry("INC0001235", {
        "Incident Number": "INC0001235",
        "Status": "Assigned",
        "Priority": "2-High",
        "Summary": "VPN connection dropping intermittently for remote users",
        "Description": "Multiple users reporting VPN drops every 2-3 hours. Affects 4 remote employees.",
        "Assignee": "David Kim",
        "Assigned Group": "IT Operations",
        "Customer First Name": "Alice",
        "Customer Last Name": "Johnson",
        "Submit Date": _D(3),
        "Last Modified Date": _D(2),
        "CI Name": "VPN-GW-01",
        "Resolution": None,
    }),
    _helix_entry("INC0001236", {
        "Incident Number": "INC0001236",
        "Status": "Pending",
        "Priority": "4-Low",
        "Summary": "Password reset request — Emma Wilson",
        "Description": "User locked out after multiple failed attempts.",
        "Assignee": "Frank Davis",
        "Assigned Group": "IT Operations",
        "Customer First Name": "Emma",
        "Customer Last Name": "Wilson",
        "Submit Date": _D(2),
        "Last Modified Date": _D(1),
        "CI Name": None,
        "Resolution": None,
    }),
    _helix_entry("INC0001237", {
        "Incident Number": "INC0001237",
        "Status": "Resolved",
        "Priority": "3-Medium",
        "Summary": "Outlook calendar not syncing on LAPTOP-CAROL-03",
        "Description": "Calendar sync issue resolved by re-enrolling device profile.",
        "Assignee": "Frank Davis",
        "Assigned Group": "IT Operations",
        "Customer First Name": "Carol",
        "Customer Last Name": "Chen",
        "Submit Date": _D(7),
        "Last Modified Date": _D(5),
        "CI Name": "LAPTOP-CAROL-03",
        "Resolution": "Re-enrolled Intune device profile. Calendar syncing correctly.",
    }),
    _helix_entry("INC0001238", {
        "Incident Number": "INC0001238",
        "Status": "Assigned",
        "Priority": "2-High",
        "Summary": "Suspicious sign-in detected for bob.martinez@nexus.corp",
        "Description": "Entra Identity Protection flagged a medium-risk sign-in from Russia. Account under review.",
        "Assignee": "Frank Davis",
        "Assigned Group": "IT Operations",
        "Customer First Name": "Bob",
        "Customer Last Name": "Martinez",
        "Submit Date": _D(2),
        "Last Modified Date": _D(1),
        "CI Name": None,
        "Resolution": None,
    }),
]

HELIX_INCIDENTS_BY_ID = {e["values"]["Incident Number"]: e for e in HELIX_INCIDENTS}

HELIX_CHANGES: list[dict] = [
    _helix_entry("CHG0002001", {
        "Change Number": "CHG0002001",
        "Status": "Scheduled",
        "Change Type": "Standard",
        "Summary": "Monthly Windows Update cycle — all managed devices",
        "Description": "Intune-pushed Windows updates for all compliant devices. Scheduled maintenance window.",
        "Change Manager": "Frank Davis",
        "Scheduled Start Date": _D(-3),
        "Scheduled End Date": _D(-1),
    }),
    _helix_entry("CHG0002002", {
        "Change Number": "CHG0002002",
        "Status": "In Progress",
        "Change Type": "Emergency",
        "Summary": "Emergency patch: CVE-2025-9902 remote code execution",
        "Description": "Critical RCE vulnerability. Emergency patching all Windows 11 endpoints via Intune.",
        "Change Manager": "Frank Davis",
        "Scheduled Start Date": _D(0),
        "Scheduled End Date": _D(-1),
    }),
    _helix_entry("CHG0002003", {
        "Change Number": "CHG0002003",
        "Status": "Draft",
        "Change Type": "Normal",
        "Summary": "Upgrade SERVER-PROD-01 from Ubuntu 22.04 to 24.04",
        "Description": "Planned OS upgrade with 2-hour downtime window. Backup required before start.",
        "Change Manager": "Alice Johnson",
        "Scheduled Start Date": _D(-14),
        "Scheduled End Date": _D(-13),
    }),
]

HELIX_CHANGES_BY_ID = {e["values"]["Change Number"]: e for e in HELIX_CHANGES}

HELIX_PROBLEMS: list[dict] = [
    _helix_entry("PRB0000456", {
        "Problem Number": "PRB0000456",
        "Status": "Under Investigation",
        "Priority": "2-High",
        "Summary": "Recurring VPN instability — root cause unknown",
        "Description": "Three incidents in two weeks. Suspected gateway capacity issue. Network team engaged.",
        "Assignee": "Frank Davis",
        "Submit Date": _D(10),
        "Last Modified Date": _D(1),
        "CI Name": "VPN-GW-01",
        "Known Error": False,
        "Workaround": "Reconnect VPN client. Issue resolves itself within 60 seconds.",
    }),
]

HELIX_CMDB: list[dict] = [
    _helix_entry("BMC.ASSET-01", {
        "Name": "LAPTOP-ALICE-01", "Asset Type": "Workstation",
        "Manufacturer": "Dell", "Model": "Latitude 5540", "Serial Number": "SN-ALICE-01",
        "Operating System": "Windows 11 Pro", "Status": "Deployed",
        "Assigned To": "Alice Johnson", "Location": "HQ-Floor3",
        "Last Modified Date": _D(30),
    }),
    _helix_entry("BMC.ASSET-02", {
        "Name": "LAPTOP-BOB-02", "Asset Type": "Workstation",
        "Manufacturer": "HP", "Model": "EliteBook 840 G10", "Serial Number": "SN-BOB-02",
        "Operating System": "Windows 11 Pro", "Status": "Deployed",
        "Assigned To": "Bob Martinez", "Location": "HQ-Floor3",
        "Last Modified Date": _D(14),
    }),
    _helix_entry("BMC.ASSET-03", {
        "Name": "LAPTOP-CAROL-03", "Asset Type": "Workstation",
        "Manufacturer": "Lenovo", "Model": "ThinkPad X1 Carbon", "Serial Number": "SN-CAROL-03A",
        "Operating System": "Windows 10 Pro", "Status": "Deployed",
        "Assigned To": "Carol Chen", "Location": "HQ-Floor2",
        "Last Modified Date": _D(60),
    }),
    _helix_entry("BMC.ASSET-05", {
        "Name": "SERVER-PROD-01", "Asset Type": "Server",
        "Manufacturer": "Dell", "Model": "PowerEdge R750", "Serial Number": "SN-PROD-01",
        "Operating System": "Ubuntu 22.04 LTS", "Status": "Deployed",
        "Assigned To": "Frank Davis", "Location": "DataCenter-A",
        "Last Modified Date": _D(90),
    }),
]

HELIX_CMDB_BY_NAME = {e["values"]["Name"]: e for e in HELIX_CMDB}


# ─── Lansweeper ───────────────────────────────────────────────────────────────

LANSWEEPER_ASSETS: list[dict] = [
    {
        "assetId": "ls-001", "assetName": "LAPTOP-ALICE-01", "assetType": "Windows",
        "ipAddress": "10.0.1.101", "mac": "AA:BB:CC:DD:EE:01",
        "lastSeen": _D(0), "lastLoggedOnUser": "CORP\\alicej",
        "operatingSystem": "Windows 11 Pro 23H2",
        "domain": "corp.nexus.local", "manufacturer": "Dell",
        "model": "Latitude 5540", "serialNumber": "SN-ALICE-01",
        "custom1": "Asset Tag: NEXUS-0101", "custom2": None, "custom3": None, "custom4": None,
    },
    {
        "assetId": "ls-002", "assetName": "LAPTOP-BOB-02", "assetType": "Windows",
        "ipAddress": "10.0.1.102", "mac": "AA:BB:CC:DD:EE:02",
        "lastSeen": _D(1), "lastLoggedOnUser": "CORP\\bobm",
        "operatingSystem": "Windows 11 Pro 23H2",
        "domain": "corp.nexus.local", "manufacturer": "HP",
        "model": "EliteBook 840 G10", "serialNumber": "SN-BOB-02",
        "custom1": "Asset Tag: NEXUS-0102", "custom2": None, "custom3": None, "custom4": None,
    },
    {
        "assetId": "ls-003", "assetName": "LAPTOP-CAROL-03", "assetType": "Windows",
        "ipAddress": "10.0.1.103", "mac": "AA:BB:CC:DD:EE:03",
        "lastSeen": _D(2), "lastLoggedOnUser": "CORP\\carolc",
        "operatingSystem": "Windows 10 Pro 22H2",
        "domain": "corp.nexus.local", "manufacturer": "Lenovo",
        "model": "ThinkPad X1 Carbon", "serialNumber": "SN-CAROL-03A",
        # ⚡ DRIFT: Lansweeper has SN-CAROL-03A but Intune has SN-CAROL-03B
        "custom1": "Asset Tag: NEXUS-0103", "custom2": None, "custom3": None, "custom4": None,
    },
    {
        "assetId": "ls-004", "assetName": "TABLET-DAVID-04", "assetType": "Apple iOS",
        "ipAddress": "10.0.1.104", "mac": "AA:BB:CC:DD:EE:04",
        "lastSeen": _D(45), "lastLoggedOnUser": "davidk",
        "operatingSystem": "iPadOS 17.4",
        "domain": None, "manufacturer": "Apple",
        "model": "iPad Pro 12.9 M2", "serialNumber": "SN-DAVID-04",
        "custom1": "Asset Tag: NEXUS-0104", "custom2": None, "custom3": None, "custom4": None,
    },
    {
        "assetId": "ls-005", "assetName": "SERVER-PROD-01", "assetType": "Linux",
        "ipAddress": "10.0.2.10", "mac": "AA:BB:CC:DD:EE:05",
        "lastSeen": _D(0), "lastLoggedOnUser": "root",
        "operatingSystem": "Ubuntu 22.04.4 LTS",
        "domain": None, "manufacturer": "Dell",
        "model": "PowerEdge R750", "serialNumber": "SN-PROD-01",
        "custom1": "Asset Tag: NEXUS-SRV-001", "custom2": "Rack: DC-A Row-3", "custom3": None, "custom4": None,
    },
    {
        "assetId": "ls-006", "assetName": "SW-CORE-01", "assetType": "Network Device",
        "ipAddress": "10.0.0.1", "mac": "AA:BB:CC:DD:FF:01",
        "lastSeen": _D(0), "lastLoggedOnUser": None,
        "operatingSystem": "Cisco IOS 17.9.4",
        "domain": None, "manufacturer": "Cisco",
        "model": "Catalyst 9300", "serialNumber": "SN-CISCO-01",
        "custom1": "Asset Tag: NEXUS-NET-001", "custom2": "Location: DataCenter-A", "custom3": None, "custom4": None,
    },
]

LANSWEEPER_ASSETS_BY_NAME = {a["assetName"].lower(): a for a in LANSWEEPER_ASSETS}
LANSWEEPER_ASSETS_BY_ID = {a["assetId"]: a for a in LANSWEEPER_ASSETS}

LANSWEEPER_SOFTWARE: dict[str, list[dict]] = {
    "ls-001": [
        {"name": "Microsoft 365 Apps", "version": "16.0.17628", "publisher": "Microsoft", "installDate": _DATE(30)},
        {"name": "Google Chrome", "version": "124.0.6367", "publisher": "Google LLC", "installDate": _DATE(7)},
        {"name": "CrowdStrike Falcon Sensor", "version": "7.14.17002", "publisher": "CrowdStrike", "installDate": _DATE(60)},
        {"name": "Zoom", "version": "6.0.11", "publisher": "Zoom Video Communications", "installDate": _DATE(14)},
        {"name": "Bitdefender GravityZone", "version": "7.9.9.324", "publisher": "Bitdefender", "installDate": _DATE(90)},
    ],
    "ls-002": [
        {"name": "Microsoft 365 Apps", "version": "16.0.17628", "publisher": "Microsoft", "installDate": _DATE(30)},
        {"name": "Google Chrome", "version": "123.0.6312", "publisher": "Google LLC", "installDate": _DATE(45)},
        {"name": "CrowdStrike Falcon Sensor", "version": "7.14.17002", "publisher": "CrowdStrike", "installDate": _DATE(60)},
        {"name": "Wireshark", "version": "4.2.4", "publisher": "Wireshark Foundation", "installDate": _DATE(20)},
        # ⚠️ Note: No BitLocker visible (encryption not enforced — triggers INC0001234)
    ],
    "ls-003": [
        {"name": "Microsoft 365 Apps", "version": "16.0.17531", "publisher": "Microsoft", "installDate": _DATE(90)},
        {"name": "Microsoft Edge", "version": "124.0.2478", "publisher": "Microsoft", "installDate": _DATE(7)},
        {"name": "Miro", "version": "0.8.35", "publisher": "Miro", "installDate": _DATE(30)},
        {"name": "CrowdStrike Falcon Sensor", "version": "7.13.16901", "publisher": "CrowdStrike", "installDate": _DATE(180)},
    ],
}


# ─── Microsoft Intune ─────────────────────────────────────────────────────────

INTUNE_DEVICES: list[dict] = [
    {
        "id": "intune-001", "deviceName": "LAPTOP-ALICE-01",
        "operatingSystem": "Windows", "osVersion": "10.0.22631.3593",
        "complianceState": "compliant", "managementState": "managed",
        "enrolledDateTime": "2023-01-10T08:00:00Z", "lastSyncDateTime": _D(0),
        "deviceType": "laptop", "userPrincipalName": "alice.johnson@nexus.corp",
        "manufacturer": "Dell", "model": "Latitude 5540", "serialNumber": "SN-ALICE-01",
        "isEncrypted": True, "azureADRegistered": True, "azureADDeviceId": "aad-001",
    },
    {
        "id": "intune-002", "deviceName": "LAPTOP-BOB-02",
        "operatingSystem": "Windows", "osVersion": "10.0.22631.3593",
        # ⚡ Non-compliant: BitLocker not enabled
        "complianceState": "noncompliant", "managementState": "managed",
        "enrolledDateTime": "2022-08-20T08:00:00Z", "lastSyncDateTime": _D(1),
        "deviceType": "laptop", "userPrincipalName": "bob.martinez@nexus.corp",
        "manufacturer": "HP", "model": "EliteBook 840 G10", "serialNumber": "SN-BOB-02",
        "isEncrypted": False, "azureADRegistered": True, "azureADDeviceId": "aad-002",
    },
    {
        "id": "intune-003", "deviceName": "LAPTOP-CAROL-03",
        "operatingSystem": "Windows", "osVersion": "10.0.19045.4412",
        "complianceState": "compliant", "managementState": "managed",
        "enrolledDateTime": "2021-03-15T08:00:00Z", "lastSyncDateTime": _D(2),
        "deviceType": "laptop", "userPrincipalName": "carol.chen@nexus.corp",
        "manufacturer": "Lenovo", "model": "ThinkPad X1 Carbon",
        # ⚡ DRIFT: Intune serial is SN-CAROL-03B, Lansweeper/Helix has SN-CAROL-03A
        "serialNumber": "SN-CAROL-03B",
        "isEncrypted": True, "azureADRegistered": True, "azureADDeviceId": "aad-003",
    },
    {
        "id": "intune-004", "deviceName": "TABLET-DAVID-04",
        "operatingSystem": "iOS", "osVersion": "17.4.1",
        # Non-compliant: device not checked in > 30 days
        "complianceState": "noncompliant", "managementState": "managed",
        "enrolledDateTime": "2022-01-05T08:00:00Z", "lastSyncDateTime": _D(45),
        "deviceType": "tablet", "userPrincipalName": "david.kim@nexus.corp",
        "manufacturer": "Apple", "model": "iPad Pro 12.9 M2", "serialNumber": "SN-DAVID-04",
        "isEncrypted": True, "azureADRegistered": True, "azureADDeviceId": "aad-004",
    },
    {
        "id": "intune-005", "deviceName": "LAPTOP-HENRY-05",
        "operatingSystem": "Windows", "osVersion": "10.0.22631.3593",
        "complianceState": "compliant", "managementState": "managed",
        "enrolledDateTime": _D(5), "lastSyncDateTime": _D(0),
        "deviceType": "laptop", "userPrincipalName": "henry.park@nexus.corp",
        "manufacturer": "Dell", "model": "Latitude 5540", "serialNumber": "SN-HENRY-05",
        "isEncrypted": True, "azureADRegistered": True, "azureADDeviceId": "aad-005",
    },
]

INTUNE_DEVICES_BY_NAME = {d["deviceName"].lower(): d for d in INTUNE_DEVICES}
INTUNE_DEVICES_BY_ID = {d["id"]: d for d in INTUNE_DEVICES}

INTUNE_COMPLIANCE_POLICIES: list[dict] = [
    {
        "id": "cp-001", "displayName": "Windows 11 Baseline",
        "description": "Requires BitLocker, Defender, and up-to-date OS",
        "platformType": "windows10AndLater", "createdDateTime": "2023-01-01T00:00:00Z",
        "settingCount": 12,
    },
    {
        "id": "cp-002", "displayName": "iOS Device Policy",
        "description": "Passcode and check-in requirements for iOS",
        "platformType": "ios", "createdDateTime": "2022-06-01T00:00:00Z",
        "settingCount": 6,
    },
]

INTUNE_CONFIGURATION_PROFILES: list[dict] = [
    {"id": "prof-001", "displayName": "Windows Security Baseline", "description": "CIS L1 controls", "platformType": "windows10AndLater", "createdDateTime": "2023-01-01T00:00:00Z"},
    {"id": "prof-002", "displayName": "BitLocker Enforcement", "description": "Enforce full-disk encryption", "platformType": "windows10AndLater", "createdDateTime": "2023-03-01T00:00:00Z"},
    {"id": "prof-003", "displayName": "Wi-Fi — Corp SSID", "description": "Automatic corporate Wi-Fi configuration", "platformType": "windows10AndLater", "createdDateTime": "2022-06-01T00:00:00Z"},
]

INTUNE_APPS: list[dict] = [
    {"id": "app-001", "displayName": "Microsoft 365 Apps for Business", "publisher": "Microsoft", "appType": "windowsMicrosoftEdgeApp", "isFeatured": True, "createdDateTime": "2022-01-01T00:00:00Z"},
    {"id": "app-002", "displayName": "CrowdStrike Falcon Sensor", "publisher": "CrowdStrike", "appType": "win32LobApp", "isFeatured": False, "createdDateTime": "2022-06-01T00:00:00Z"},
    {"id": "app-003", "displayName": "Zoom Workplace", "publisher": "Zoom Video Communications", "appType": "win32LobApp", "isFeatured": False, "createdDateTime": "2023-02-01T00:00:00Z"},
    {"id": "app-004", "displayName": "Google Chrome", "publisher": "Google LLC", "appType": "win32LobApp", "isFeatured": False, "createdDateTime": "2022-06-01T00:00:00Z"},
]

INTUNE_AUTOPILOT_DEVICES: list[dict] = [
    {"id": "ap-001", "serialNumber": "SN-ALICE-01", "model": "Latitude 5540", "manufacturer": "Dell", "groupTag": "Engineering", "enrollmentState": "enrolled"},
    {"id": "ap-002", "serialNumber": "SN-BOB-02", "model": "EliteBook 840 G10", "manufacturer": "HP", "groupTag": "Engineering", "enrollmentState": "enrolled"},
    {"id": "ap-003", "serialNumber": "SN-CAROL-03B", "model": "ThinkPad X1 Carbon", "manufacturer": "Lenovo", "groupTag": "Product", "enrollmentState": "enrolled"},
    {"id": "ap-005", "serialNumber": "SN-HENRY-05", "model": "Latitude 5540", "manufacturer": "Dell", "groupTag": "Engineering", "enrollmentState": "enrolled"},
]


# ─── FedEx ────────────────────────────────────────────────────────────────────

def _scan_event(status: str, desc: str, city: str, state: str, days_ago: float) -> dict:
    dt = (_NOW - datetime.timedelta(days=days_ago)).strftime(_FMT)
    return {
        "date": dt, "eventType": status, "eventDescription": desc,
        "scanLocation": {"city": city, "stateOrProvinceCode": state, "countryCode": "US"},
        "derivedStatus": desc,
    }


FEDEX_TRACKING: dict[str, dict] = {
    "776126785997": {
        "trackingNumber": "776126785997",
        "trackResults": [{
            "trackingNumberInfo": {"trackingNumber": "776126785997", "trackingNumberUniqueId": "12013~776126785997~FX"},
            "additionalTrackingInfo": {"packageIdentifiers": [{"type": "PURCHASE_ORDER", "value": "PO-LAPTOP-001"}]},
            "shipperInformation": {"address": {"city": "Austin", "stateOrProvinceCode": "TX", "countryCode": "US"}},
            "recipientInformation": {"address": {"city": "New York", "stateOrProvinceCode": "NY", "countryCode": "US"}},
            "latestStatusDetail": {"code": "DL", "derivedCode": "DL", "statusByLocale": "Delivered", "description": "Delivered", "scanLocation": {"city": "New York", "stateOrProvinceCode": "NY", "countryCode": "US"}},
            "dateAndTimes": [{"type": "SHIP", "dateTime": _D(5)}, {"type": "ACTUAL_DELIVERY", "dateTime": _D(2)}],
            "packageDetails": {"physicalPackagingType": "PACKAGE", "sequenceNumber": "1/1", "weightAndDimensions": {"weight": [{"unit": "LB", "value": "4.5"}]}},
            "shipmentDetails": {"possessionStatus": "OD", "weight": [{"unit": "LB", "value": "4.5"}]},
            "scanEvents": [
                _scan_event("DL", "Delivered — Front Door/Porch", "New York", "NY", 2),
                _scan_event("OD", "On FedEx vehicle for delivery", "New York", "NY", 2.2),
                _scan_event("AR", "Arrived at FedEx facility", "New York", "NY", 2.5),
                _scan_event("IT", "In transit", "Philadelphia", "PA", 3),
                _scan_event("PU", "Picked up", "Austin", "TX", 5),
            ],
        }],
    },
    "776126785998": {
        "trackingNumber": "776126785998",
        "trackResults": [{
            "trackingNumberInfo": {"trackingNumber": "776126785998", "trackingNumberUniqueId": "12013~776126785998~FX"},
            "additionalTrackingInfo": {"packageIdentifiers": [{"type": "PURCHASE_ORDER", "value": "PO-MONITOR-002"}]},
            "shipperInformation": {"address": {"city": "Seattle", "stateOrProvinceCode": "WA", "countryCode": "US"}},
            "recipientInformation": {"address": {"city": "New York", "stateOrProvinceCode": "NY", "countryCode": "US"}},
            "latestStatusDetail": {"code": "IT", "derivedCode": "IT", "statusByLocale": "In Transit", "description": "In transit", "scanLocation": {"city": "Chicago", "stateOrProvinceCode": "IL", "countryCode": "US"}},
            "dateAndTimes": [{"type": "SHIP", "dateTime": _D(2)}, {"type": "ESTIMATED_DELIVERY", "dateTime": _D(-1)}],
            "packageDetails": {"physicalPackagingType": "PACKAGE", "sequenceNumber": "1/1", "weightAndDimensions": {"weight": [{"unit": "LB", "value": "12.0"}]}},
            "scanEvents": [
                _scan_event("IT", "In transit", "Chicago", "IL", 0.5),
                _scan_event("AR", "Arrived at FedEx facility", "Chicago", "IL", 0.8),
                _scan_event("IT", "In transit", "Denver", "CO", 1),
                _scan_event("PU", "Picked up", "Seattle", "WA", 2),
            ],
        }],
    },
    "776126785999": {
        "trackingNumber": "776126785999",
        "trackResults": [{
            "trackingNumberInfo": {"trackingNumber": "776126785999", "trackingNumberUniqueId": "12013~776126785999~FX"},
            "additionalTrackingInfo": {"packageIdentifiers": [{"type": "PURCHASE_ORDER", "value": "PO-KEYBOARD-003"}]},
            "shipperInformation": {"address": {"city": "Memphis", "stateOrProvinceCode": "TN", "countryCode": "US"}},
            "recipientInformation": {"address": {"city": "New York", "stateOrProvinceCode": "NY", "countryCode": "US"}},
            "latestStatusDetail": {"code": "OD", "derivedCode": "OD", "statusByLocale": "Out for Delivery", "description": "On FedEx vehicle for delivery", "scanLocation": {"city": "New York", "stateOrProvinceCode": "NY", "countryCode": "US"}},
            "dateAndTimes": [{"type": "SHIP", "dateTime": _D(1)}, {"type": "ESTIMATED_DELIVERY", "dateTime": _D(0)}],
            "packageDetails": {"physicalPackagingType": "ENVELOPE", "sequenceNumber": "1/1", "weightAndDimensions": {"weight": [{"unit": "LB", "value": "0.8"}]}},
            "scanEvents": [
                _scan_event("OD", "On FedEx vehicle for delivery", "New York", "NY", 0.1),
                _scan_event("AR", "At local FedEx facility", "New York", "NY", 0.3),
                _scan_event("IT", "In transit", "Newark", "NJ", 0.6),
                _scan_event("PU", "Picked up", "Memphis", "TN", 1),
            ],
        }],
    },
}

FEDEX_RATES_SAMPLE: list[dict] = [
    {"serviceType": "FEDEX_OVERNIGHT", "serviceName": "FedEx First Overnight®", "currency": "USD", "totalNetCharge": 89.50, "estimatedDeliveryTime": "Next business day by 8:00 AM"},
    {"serviceType": "PRIORITY_OVERNIGHT", "serviceName": "FedEx Priority Overnight®", "currency": "USD", "totalNetCharge": 62.75, "estimatedDeliveryTime": "Next business day by 10:30 AM"},
    {"serviceType": "STANDARD_OVERNIGHT", "serviceName": "FedEx Standard Overnight®", "currency": "USD", "totalNetCharge": 48.20, "estimatedDeliveryTime": "Next business day by 3:00 PM"},
    {"serviceType": "FEDEX_2_DAY", "serviceName": "FedEx 2Day®", "currency": "USD", "totalNetCharge": 32.10, "estimatedDeliveryTime": "2 business days"},
    {"serviceType": "FEDEX_GROUND", "serviceName": "FedEx Ground®", "currency": "USD", "totalNetCharge": 12.85, "estimatedDeliveryTime": "3-5 business days"},
]
