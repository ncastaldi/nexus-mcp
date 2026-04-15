# Plan: Fix PowerShell Command Injection in `ad_adapter.py`

## 🌿 Branch Identity

**Suggested Branch Name:** `fix/ps-command-injection-ad-adapter`

**Purpose:** Closes CRITICAL #2 from the code health report — eliminates a PowerShell command injection vulnerability (OWASP A03) in `nexus-mcp/lib/ad_adapter.py` before any production connection to the AD server.

---

## 🚀 The Fix: Parameterized PowerShell Execution

**Plain English:** Right now, when a username like `jane.doe` is looked up, Python builds a PowerShell command *as a string* with the username baked into it — like handing someone a note that says `"search for jane.doe"`. A malicious input like `'; Remove-Item C:\Important; '` would make the note say *"search for nothing, then delete files."*

The fix passes user values through a separate channel — **OS environment variables** — so they can never change the *structure* of the command, only its *data*. PowerShell reads them via `$env:NEXUS_ARG0`, exactly like reading from a locked box, not from the note itself. No new libraries are needed.

---

## 💻 Implementation Plan

This is a 5-phase change, all contained to one file plus its test file.

### Phase 1 — Harden `_run_powershell()` *(blocks all other phases)*

In `nexus-mcp/lib/ad_adapter.py`:

1. Add `import os` to the top-of-file imports (line 1–6 block).
2. Change the `_run_powershell()` signature to add `env_params: dict[str, str] | None = None`.
3. Before the `create_subprocess_exec` call, build: `proc_env = {**os.environ, **(env_params or {})}`.
4. Pass `env=proc_env` to `asyncio.create_subprocess_exec(...)`.
5. Fix the `cred_block` injection surface: replace `'{escaped_password}'` and `'{self.username}'` with `$env:NEXUS_PS_PASSWORD` and `$env:NEXUS_PS_USERNAME` in the PowerShell string. Inject those values via `proc_env` from `self.password` / `self.username` directly (they are server-config values, not user input, but this eliminates the escape-quote surface entirely).

### Phase 2 — Fix `get_user()`, `get_user_groups()`, `get_group_members()`, `get_computer()` *(parallel — all follow the same pattern)*

For each:
1. Add a length guard at the top: `if len(input_var) > 256: raise ValueError(...)`.
2. Remove the `_escape_ps_single_quoted()` call.
3. Pass the value via `env_params={"NEXUS_ARG0": input_var}` in the `_run_powershell()` call.
4. In the PowerShell command string, replace `'{escaped_X}'` with `'$($env:NEXUS_ARG0)'`.

**Before** (line ~113 in `get_user()`):
```python
escaped_username = self._escape_ps_single_quoted(username)
command = f"""
    $user = Get-ADUser -Filter "samAccountName -eq '{escaped_username}'" ...
"""
result = await self._run_powershell(command, {"username": username})
```

**After:**
```python
if len(username) > 256:
    raise ValueError("username too long")
command = """
    $user = Get-ADUser -Filter "samAccountName -eq '$($env:NEXUS_ARG0)'" ...
"""
result = await self._run_powershell(command, {"username": username}, env_params={"NEXUS_ARG0": username})
```

### Phase 3 — Fix `search_users_by_name()` *(parallel with Phase 2)*

1. Add length guard: `if len(query.strip()) > 100: raise ValueError(...)`.
2. Remove `escaped_query` interpolation.
3. Pass `env_params={"NEXUS_ARG0": query}`.
4. In the PowerShell script, add `$query = $env:NEXUS_ARG0` as the first line. All downstream PS-internal variable uses (`$query`, `$tokens`, `$adFilter`) already operate on that PS variable — they stay as-is.

### Phase 4 — Fix `query_users()`, `count_users()`, `summarize_users()` *(parallel with Phase 2)*

These build dynamic filters from multiple string params. Each filter string value gets its own env var:

| Python key           | Env var              | Max length |
| :------------------- | :------------------- | :--------- |
| `name_contains`      | `NEXUS_FILTER_NAME`  | 256        |
| `username_prefix`    | `NEXUS_FILTER_PREFIX`| 64         |
| `ou_contains`        | `NEXUS_FILTER_OU`    | 512        |
| `description_contains`| `NEXUS_FILTER_DESC` | 256        |
| `group_any` (JSON)   | `NEXUS_FILTER_GROUPS`| 2048       |

In the PowerShell filter fragment, replace the Python-interpolated value with the env var reference. For example:
```powershell
# Before (Python builds this):  "DisplayName -like '*{escaped_query}*'"
# After: "DisplayName -like '*$($env:NEXUS_FILTER_NAME)*'"
```

Collect all env vars into a single `env_params` dict and pass once to `_run_powershell()`.

### Phase 5 — Tests *(depends on Phases 1–4)*

Add to `nexus-mcp/tests/identity_tests/test_ad_adapter.py`:

1. **`test_get_user_injection_attempt`** — calls `get_user("'; Remove-Item C:\\test; '")` with `_run_powershell` mocked. Asserts it returns `None` (not raised, not crashed) — proving the method still works with hostile input.
2. **`test_search_users_injection_attempt`** — same for `search_users_by_name`.
3. **`test_run_powershell_passes_env_params`** — mocks `asyncio.create_subprocess_exec`, calls `_run_powershell("echo test", env_params={"NEXUS_ARG0": "val"})`, asserts the `env` kwarg passed to `create_subprocess_exec` contains `"NEXUS_ARG0": "val"`.
4. **`test_get_user_input_too_long`** — asserts `ValueError` is raised for a 257-char username.

> **Note on existing test impact:** The `cred_block` fix in Phase 1 affects `test_run_powershell_with_credentials` — that test currently asserts on the command string content. It will need updating to assert on env var presence instead of password interpolation in the command string.

---

## 🛠️ Deployment Steps

```bash
# 1. Create and switch to the feature branch
git checkout -b fix/ps-command-injection-ad-adapter

# 2. No new packages required — os is stdlib, pyproject.toml is unchanged

# 3. Run existing tests before making changes (baseline)
cd nexus-mcp
python -m pytest tests/identity_tests/test_ad_adapter.py -v

# 4. Implement the phases above in ad_adapter.py and test_ad_adapter.py

# 5. Run tests after changes
python -m pytest tests/identity_tests/test_ad_adapter.py -v

# 6. Run full nexus-mcp test suite to confirm no regressions
python -m pytest tests/ -v --ignore=tests/integration_test_audit_shard.py
```

---

## 🧪 How to Verify It Works

**Success metric — automated:**
```
tests/identity_tests/test_ad_adapter.py::TestActiveDirectoryBackend::test_get_user_injection_attempt PASSED
tests/identity_tests/test_ad_adapter.py::TestActiveDirectoryBackend::test_run_powershell_passes_env_params PASSED
tests/identity_tests/test_ad_adapter.py::TestActiveDirectoryBackend::test_get_user_input_too_long PASSED
```

**Success metric — code audit (zero output expected):**
```bash
# Should return nothing — no more _escape_ps_single_quoted calls in method bodies
grep -n "_escape_ps_single_quoted(" nexus-mcp/lib/ad_adapter.py | grep -v "def _escape"

# Should return nothing — no more Python f-string interpolation of user values into PS command strings
grep -n "escaped_" nexus-mcp/lib/ad_adapter.py
```

**Out of scope:** `archive/Identity/` tree. The static method `_escape_ps_single_quoted()` remains in place, marked `# DEPRECATED`, to avoid breaking archive callers.
