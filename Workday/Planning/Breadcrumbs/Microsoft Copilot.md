Perfect — this gives us the **real-world shape** of the Workday record we should design around, *before* you ever get API access. Based on what you pasted, your **Employee ID is numeric (8 digits)** and you have a stable set of “Job Details” + “Public Contact” fields we can treat as your **Phase 1 canonical Worker contract**. [\[wheelsinc-...epoint.com\]](https://wheelsinc-my.sharepoint.com/personal/castn1_wheels_com/Documents/Microsoft%20Copilot%20Chat%20Files/server.py)

Below I’m going to do two things:

1.  Translate your Workday profile into a **clean canonical schema** (fields, types, constraints) that you can enforce with Pydantic (**WIS-010**) now.
2.  Show how that schema feeds your **dry-run diff tool** (**WIS-019**) and your later Workday→AD sync logic—without needing Workday access yet.

***

## 1) What your profile tells us about “employee\_id” (and constraints)

From your profile:

*   `Employee ID` = `10016638` → **numeric string**, **8 digits** (at least in your tenant).
*   This is a **better primary key** than email or name for matching to AD.

### Recommended constraint (for now)

*   Treat `employee_id` as a **string** (not int) to preserve leading zeros if they exist in other records.
*   Enforce pattern: `^[0-9]{8}$` (8 digits)

> If you later discover IDs vary (e.g., 6–10 digits), you can loosen the regex to `^[0-9]{6,10}$` without breaking downstream contracts.

***

## 2) Canonical Worker Schema (Phase 1 / no Workday API required)

Here’s a **normalized Worker model** derived from your field list. I’m using names that are stable + automation-friendly, while keeping the original Workday labels clear.

### Field mapping (Workday → canonical)

**Identity**

*   `employee_id` ← Employee ID (string, 8-digit numeric)
*   `work_email` ← Email (string, email format)

**Org / Reporting**

*   `supervisory_organization` ← Supervisory Organization (string)
*   `manager_name` ← Supervisory Organization trailing manager name (string, optional)
*   `manager_employee_id` ← (not present in your paste; optional until Workday API provides it)

**Job**

*   `position` ← Position
*   `business_title` ← Business Title
*   `job_profile` ← Job Profile
*   `employee_type` ← Employee Type (e.g., Regular)
*   `management_level` ← Management Level (e.g., Individual Contributor)
*   `time_type` ← Time Type (e.g., Full time)
*   `fte_percent` ← FTE (decimal percent)

**Employment dates**

*   `hire_date` ← Hire Date (date)
*   `original_hire_date` ← Original Hire Date (date)
*   `continuous_service_date` ← Continuous Service Date (date)

**Location**

*   `location` ← Location
*   `work_address` ← Work Address (string)

### Why this specific cut matters

This set gives you enough to drive:

*   onboarding timing (hire date)
*   basic directory attributes (title, department-like org fields, location)
*   reporting chain resolution (supervisory org / manager)
*   future group mapping (job profile, employee type, management level)

…and it’s stable enough to validate *before* Workday access.

***

## 3) How I’d update your current MCP server **right now** (targeted improvements)

Your current `server.py` is a solid scaffold, but it’s using:

*   mock IDs like `EMP001`, and
*   a flat dict with fields (`name`, `status`, `dept`, `email`, `manager_id`) [\[wheelsinc-...epoint.com\]](https://wheelsinc-my.sharepoint.com/personal/castn1_wheels_com/Documents/Microsoft%20Copilot%20Chat%20Files/server.py)

To align with *real Workday data* **before you ever connect**:

### A) Switch your mock dataset to real ID format

Change mock keys from `EMP001` → `10016638` style.

*   This forces you to solve input validation and casing issues now (numeric IDs have no casing).
*   It prevents later refactors when Workday is live.

### B) Standardize your tool outputs (strongly recommended)

Right now, tools return either:

*   a worker dict OR
*   `{"error": ...}` [\[wheelsinc-...epoint.com\]](https://wheelsinc-my.sharepoint.com/personal/castn1_wheels_com/Documents/Microsoft%20Copilot%20Chat%20Files/server.py)

Before Workday access, lock in a stable envelope like:

```json
{
  "ok": true,
  "data": { ... },
  "error": null,
  "meta": {
    "correlation_id": "uuid",
    "source": "mock",
    "contract_version": "wis.v1"
  }
}
```

Why now? Because Power Automate + connectors love consistent shapes. If you wait, you’ll end up rewriting flows and schemas later.

### C) Build Pydantic models for:

*   Worker input (`WorkerModel`)
*   Tool response (`WorkerStatusResponse`)
*   Error (`ErrorModel`)
*   Envelope (`ToolResponse[T]`)

This is the core of **WIS-010**.

***

## 4) Concrete Pydantic Contract Proposal (WIS-010)

Here’s the **contract design** I recommend based on your profile fields and your automation goals.

### WorkerModel constraints (recommended)

*   `employee_id`: `^[0-9]{8}$`
*   `work_email`: must validate as email
*   `fte_percent`: 0–100 (float)
*   `time_type`: enum (`Full time`, `Part time`, etc.)
*   Dates: parsed into real `date` objects

### “Strict mode” recommendation

Start with:

*   `extra="forbid"` (reject unknown fields)
*   later relax to `extra="ignore"` if Workday payloads contain extra fields you don’t care about

This gives you confidence early.

***

## 5) Your Dry-Run Diff Tool (WIS-019) — now shaped by real Workday fields

Once you validate Workday-shaped inputs, your dry-run diff becomes meaningful:

### What it should compare (Phase 1 scope)

From the fields you pasted, your first drift checks should include:

*   Title / Business Title / Job Profile
*   Location
*   Manager / supervisory org reference
*   Employee status → AD enabled/disabled state
*   Email → UPN/mail alignment

### Diff item example (your intended format + enhancements)

You suggested:

```json
{"field":"department","old":"Sales","new":"Marketing","action":"update"}
```

I’d add two fields **now** that become critical in Phase 3:

*   `severity` (low/medium/high)
*   `reversible` (true/false)

Example:

```json
{
  "field": "business_title",
  "old": "Team Lead, Deskside Support",
  "new": "Team Lead, Deskside Support",
  "action": "none",
  "severity": "low",
  "reversible": true
}
```

Then your approval payload can be generated directly from the diff result (no extra logic later).

***

## 6) Break Tests you can run **today** (with your real constraints)

Since we now know your ID shape, your “try to break it” script should include:

### Employee ID failure cases

*   empty string `""`
*   non-numeric `"EMP001"`
*   wrong length `"1001663"` (7 digits), `"100166380"` (9 digits)
*   whitespace `" 10016638 "`

### Data failures (WorkerModel)

*   invalid email `"not-an-email"`
*   FTE out of range `150.0`
*   Hire date invalid `"2021-13-40"`
*   Missing required fields (`employee_id`, `work_email`)

### Expected behavior

*   Tools return `ok:false`
*   Error has stable code (e.g., `VALIDATION_ERROR`)
*   No sensitive fields are echoed in logs (see below)

This is how you prove WIS-010 is real, not theoretical.

***

## 7) Security/Hardening decisions informed by your profile fields

Because Workday records contain PII-like data (email, address), your hardening step (WIS-027) should **explicitly redact**:

*   `work_email`
*   `work_address`
*   `employee_id` (optional partial mask like `******38`)

### Redaction policy (recommended)

*   In logs: redact always
*   In tool responses:
    *   keep email if the tool is intended for automation and access is controlled
    *   or provide a config switch: `RETURN_PII=false` (defaults safe)

This is much easier to implement now than after Workday is live.

***

# 8) What I would change in your current `server.py` (actionable list)

In order, **before Workday API access**:

1.  **Replace EMP### mock IDs with numeric employee IDs** (like your `10016638`) [\[wheelsinc-...epoint.com\]](https://wheelsinc-my.sharepoint.com/personal/castn1_wheels_com/Documents/Microsoft%20Copilot%20Chat%20Files/server.py)
2.  **Add Pydantic WorkerModel + Response envelope** (WIS-010) [\[wheelsinc-...epoint.com\]](https://wheelsinc-my.sharepoint.com/personal/castn1_wheels_com/Documents/Microsoft%20Copilot%20Chat%20Files/server.py)
3.  **Normalize tool outputs** into `{ok,data,error,meta}` for every tool [\[wheelsinc-...epoint.com\]](https://wheelsinc-my.sharepoint.com/personal/castn1_wheels_com/Documents/Microsoft%20Copilot%20Chat%20Files/server.py)
4.  **Implement dry\_run\_compare() tool** returning a typed DiffResult (WIS-019)
5.  **Add rate-limit simulation decorator** and make errors explicitly retryable (WIS-027)
6.  **Add log redaction helper** for email/address/employee\_id (WIS-027)
7.  **Externalize mock data** into JSON + support multiple scenario datasets
8.  **Pytest suite**: manager resolution scenarios (Found/Not Found/No Manager) using your mock structure [\[wheelsinc-...epoint.com\]](https://wheelsinc-my.sharepoint.com/personal/castn1_wheels_com/Documents/Microsoft%20Copilot%20Chat%20Files/server.py)
9.  **Pre-commit hooks** to block commits on failing tests/lint

***

## 9) Two quick questions so I lock the schema correctly

1.  In your tenant, is **Employee ID always 8 digits**, or have you seen contractors/vendors with a different format?
2.  Do you want **Work Address** treated as:
    *   a field you *store* in AD/Entra, or
    *   *reference only* (used for location logic but not written anywhere)?

***

## If you want, I can take the next step automatically

If you say “go,” I’ll draft:

*   A **Pydantic schema pack** (`models.py`) for WorkerModel, DiffResult, Envelope
*   A revised `server.py` that:
    *   uses numeric employee IDs
    *   returns consistent envelopes
    *   includes `dry_run_compare`
    *   includes redaction + rate-limit simulation toggles
*   A `/tests` folder with the manager tests + “break tests” script

Just tell me whether you prefer **Pydantic v1 or v2** (most orgs are v2 now, but I’ll match your repo dependency reality).
