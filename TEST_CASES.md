# Nexus MCP Test Cases

## 🟢 Identity Shard — Active Directory

Test the core lookup tools first since those are the ones we just fixed.

### User lookups

    Look up the AD user "jsmith"

<!---->

    Find the Active Directory account for email "john.smith@wheels.com"

<!---->

    Search for AD users matching "martinez"

### Group tools

    List all Active Directory groups

<!---->

    Get the members of the AD group "CN=IT-Admins,OU=Groups,DC=wheels,DC=com"

### Account hygiene (the ones we just fixed)

    Show me all disabled accounts in Active Directory

<!---->

    Find AD accounts that haven't logged in for 90 days

<!---->

    Show stale accounts inactive for more than 60 days

***

## 🟢 Identity Shard — Microsoft Entra ID

    List users in Entra ID

<!---->

    Get the Entra ID user for "john.smith@wheels.com"

<!---->

    List all Entra ID groups

<!---->

    Show me all Entra ID service principals

<!---->

    Get the Conditional Access policies from Entra ID

<!---->

    Show recent sign-in logs from Entra ID

<!---->

    List users flagged as risky in Entra ID Identity Protection

***

## 🟡 Workday Shard

    List workers in Workday

<!---->

    Get the Workday worker record for employee ID "EMP001"

<!---->

    Find the Workday worker with email "john.smith@wheels.com"

<!---->

    List all supervisory organizations in Workday

<!---->

    Show open positions in Workday

***

## 🟡 Audit Shard (the most interesting ones)

These are your cross-system drift tools — great for confirming the full pipeline works end-to-end.

    Scan for terminated workers who still have active AD accounts

<!---->

    Run a job title drift scan between Workday and Active Directory

<!---->

    Check for department mismatches between Workday and AD

<!---->

    Scan for name variance mismatches between Workday and AD

<!---->

    Show me the last 20 Nexus audit log entries

<!---->

    Give me Nexus audit statistics

***

## 🔴 Stub Shards (these should return empty or stub responses, not errors)

These confirm your feature flag / holding pattern works correctly — the server should accept the call and return gracefully.

    List incidents from BMC Helix

<!---->

    Track FedEx shipment "449044304137821"

<!---->

    List assets from Lansweeper

<!---->

    Show me Intune managed devices

***

## 🧪 Suggested Test Order (most value, least noise)

Run them in this order for a clean "smoke test" progression:

| # | Command                                               | What it validates                              |
| - | ----------------------------------------------------- | ---------------------------------------------- |
| 1 | `Show me all disabled accounts in Active Directory`   | Fixed `query_users` path ✅                     |
| 2 | `Find stale AD accounts inactive for 90 days`         | Fixed `find_stale_users` rename ✅              |
| 3 | `Search for AD users matching "smith"`                | Fixed `search_users_by_name` rename ✅          |
| 4 | `Find the AD user with email "john.smith@wheels.com"` | Fixed `ad_get_user_by_email` path ✅            |
| 5 | `List all Active Directory groups`                    | Confirms mock path + WIS-018 holding pattern ✅ |
| 6 | `Scan for terminated workers still active in AD`      | Confirms cross-shard audit works ✅             |
| 7 | `Show me the last 20 Nexus audit log entries`         | Confirms SOC 2 logging is active ✅             |
| 8 | `List incidents from BMC Helix`                       | Confirms stub shards fail gracefully ✅         |

***

## One thing to watch for

If any tool returns an **empty list `[]` that you didn't expect**, check:

* Is `USE_MOCK=true` confirmed in the MCP server output?
* Does the mock data in `mock_data.py` have entries for that tool?

If a tool **errors** instead of returning empty, that's a real bug worth capturing — paste the error here and we'll triage it.
