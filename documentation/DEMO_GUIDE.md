# Nexus-MCP — demo and setup guide

Sharded enterprise integration MCP server for Active Directory, Entra ID, Workday, BMC Helix, Lansweeper, Intune, FedEx, and cross-system drift auditing.

> **All test scripts must be run from the `nexus-mcp/` directory.**

---

## Prerequisites

- Python 3.11 or newer
- Git
- PowerShell (Windows) or bash (Linux/macOS)
- Access to corporate systems (AD, Entra, Workday) — or enable mock mode (no credentials needed)

---

## Installation

### 1. Navigate to the server directory

```bash
cd /path/to/mcp_servers/nexus-mcp
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows (bash/Git Bash):**

```bash
python -m venv .venv
source .venv/Scripts/activate
```

**Linux/macOS:**

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -e .
```

Installs nexus-mcp in editable mode with all required packages (`mcp`, `httpx`, `python-dotenv`, `ldap3`, `msal`, etc.).

---

## Configuration

### 1. Create .env file

```bash
cp .env.example .env
```

### 2. Choose your mode

**Option A: Mock mode (no credentials needed)**

Good for development, testing shards, and exploring drift scenarios.

```env
USE_MOCK=true

ENABLE_IDENTITY=true
ENABLE_WORKDAY=true
ENABLE_AUDIT=true
ENABLE_ITSM=false
ENABLE_ASSETS=false
ENABLE_LOGISTICS=false

AUDIT_LOGGING_ENABLED=true
AUDIT_LOG_FILE=./logs/nexus_audit.jsonl
AUDIT_LOG_STDERR=true
```

**Option B: Live mode (production credentials)**

Requires actual service accounts and API credentials. Enable only the shards where credentials are available.

```env
USE_MOCK=false

ENABLE_IDENTITY=true
ENABLE_WORKDAY=false    # Set true when credentials available
ENABLE_AUDIT=true
ENABLE_ITSM=false
ENABLE_ASSETS=false
ENABLE_LOGISTICS=false

# Active Directory
AD_SERVER=ldap://your-dc.company.com
AD_PORT=389
AD_BASE_DN=DC=company,DC=com
AD_USER=CN=svc_nexus,OU=Service Accounts,DC=company,DC=com
AD_PASSWORD=your_password
AD_USE_SSL=false

# Microsoft Entra ID (Azure AD)
ENTRA_TENANT_ID=your_tenant_id
ENTRA_CLIENT_ID=your_client_id
ENTRA_CLIENT_SECRET=your_client_secret
```

Your `.env` file is never committed to git.

---

## Running the server

```bash
python src/main.py
```

**Expected startup output (mock mode, default shards):**

```
[nexus] ✅ identity shard loaded
[nexus] ✅ workday shard loaded
[nexus] ✅ audit shard loaded
[nexus] ⏸  itsm shard disabled (ENABLE_ITSM != true)
[nexus] ⏸  assets shard disabled (ENABLE_ASSETS != true)
[nexus] ⏸  logistics shard disabled (ENABLE_LOGISTICS != true)
[nexus] 🔒 SOC 2 audit middleware active → ./logs/nexus_audit.jsonl
```

The server runs on stdio transport and waits for MCP protocol messages.

---

## Claude Desktop integration

Add this block to your Claude Desktop `config.json`:

- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "nexus": {
      "command": "python",
      "args": ["src/main.py"],
      "cwd": "C:/Users/your-username/repos/mcp_servers/nexus-mcp",
      "env": {
        "USE_MOCK": "true"
      }
    }
  }
}
```

Restart Claude Desktop. The Nexus tools will appear in the tool picker.

---

## Feature flag reference

| Flag | Shard | Systems | Default |
|---|---|---|---|
| `ENABLE_IDENTITY` | `identity.py` | Active Directory + Entra ID | `true` |
| `ENABLE_WORKDAY` | `workday.py` | Workday HCM | `true` |
| `ENABLE_AUDIT` | `audit.py` | Cross-system drift | `true` |
| `ENABLE_ITSM` | `itsm.py` | BMC Helix | `false` |
| `ENABLE_ASSETS` | `assets.py` | Lansweeper + Intune | `false` |
| `ENABLE_LOGISTICS` | `logistics.py` | FedEx | `false` |

Set a flag to `false` (or omit it) to put that shard in holding pattern. The server will start successfully and skip those tools.

---

## Quick start — demo scripts

All scripts run from the `nexus-mcp/` directory against mock data.

### Audit tools demonstration

```bash
python test_client.py
```

Shows all 4 audit scan tools executing with severity classification and mismatch summaries.

**Expected:** 6 total mismatches across 9 employee records.

### Tool catalog browser

```bash
python list_tools.py
```

Shows the complete tool inventory (50 tools), organized by shard, with descriptions from docstrings.

### MCP protocol simulation

```bash
python test_mcp_protocol.py
```

Simulates the full MCP handshake: protocol negotiation → `tools/list` discovery → `tools/call` invocation → JSON response. Useful for verifying Claude Desktop compatibility.

---

## Test suite

Run from the `nexus-mcp/` directory:

```bash
# Full suite
pytest tests/ -v

# Specific modules
pytest tests/identity_tests/ -v
pytest tests/workday_tests/ -v

# With coverage
pytest tests/ --cov=lib --cov=src --cov-report=term-missing

# Audit integration tests only
pytest tests/workday_tests/ tests/integration_test_audit_shard.py -v
```

**Expected baseline:** 10/10 passing in ~0.6s.

See `nexus-mcp/TEST_VALIDATION_REPORT.md` for full results and MCP protocol compliance details.

---

## Mock data and drift scenarios

Mock data is defined in `lib/mock_data.py`. Pre-seeded mismatches cover all severity levels:

| Employee | Mismatch | Severity | Detected by |
|---|---|---|---|
| Terminated worker | Active in Workday as terminated, AD account still enabled | HIGH | `scan_status_reconciliation` |
| Bob Martinez | Title differs — AD: "Sr. Software Engineer" vs Workday: "Software Engineer" | MEDIUM | `scan_job_title_drift` |
| Carol Chen | Department differs — Workday: "Product Management" vs AD: "Engineering" | MEDIUM | `scan_department_mismatches` |
| 3 employees | AD display name doesn't align with legal/preferred name in Workday | LOW | `scan_name_variance_mismatches` |

**Employee records:** 9 (EMP001–EMP777) | **Total pre-seeded mismatches:** 6

Try the audit tools in Claude chat with Nexus-MCP active:

```
"Scan for terminated workers still active in AD"
"Run a job title drift scan"
"Show me all stale AD accounts"
"Run audit statistics"
```

---

## SOC 2 audit logging

Every tool call is logged to `logs/nexus_audit.jsonl` (one JSON object per line, automatically redacted).

Each entry contains:

- `event_id` — UUID v4 for correlation
- `timestamp` — ISO 8601 UTC
- `tool` — MCP tool name
- `shard` — identity | workday | audit | etc.
- `action_category` — READ | AUDIT | REPORT
- `args_summary` — call arguments with passwords/tokens redacted
- `mock_mode` — true/false
- `status` — success | error
- `latency_ms` — execution time

Query the audit log directly using the built-in tools:

```
"Show me the last 50 audit log entries"   → nexus_audit_recent
"Give me audit statistics"                → nexus_audit_stats
```

---

## Troubleshooting

**Server won't start**

- Check Python version: `python --version` (must be 3.11+)
- Verify the venv is active (`(.venv)` should appear in your prompt)
- Verify dependencies: `pip list | grep mcp`

**Shard not loading**

- Check the feature flag in `.env`: `ENABLE_IDENTITY=true`
- Look for error messages in the startup output
- Verify the shard file exists: `ls src/shards/identity.py`

**Credentials not working (live mode)**

- Test AD connectivity: `python -c "import ldap3; print(ldap3.__version__)"`
- Verify the service account can bind to LDAP
- Check firewall rules for on-prem AD

**Audit log not writing**

- Check permissions on the `logs/` directory
- Verify `AUDIT_LOGGING_ENABLED=true` in `.env`

---

## Development workflow

### Adding a tool to an existing shard

1. Edit the shard file (e.g. `src/shards/identity.py`)
2. Add the tool function inside `register(mcp)` using the `@mcp.tool()` decorator
3. Restart the server and test in Claude Desktop

### Creating a new shard

1. Copy an existing shard as a template: `cp src/shards/identity.py src/shards/my_system.py`
2. Implement `register(mcp)` with your tools
3. Add the shard to `src/main.py`:

    ```python
    if _enabled("MY_SYSTEM"):
        my_system.register(mcp)
    ```

4. Add the flag to `.env.example`: `ENABLE_MY_SYSTEM=false`

### Switching between mock and live mode

Change `USE_MOCK` in `.env` and restart — no code changes needed:

```bash
USE_MOCK=false
python src/main.py
```

---

## Next steps

1. Run `python test_client.py` to verify audit tools work in mock mode
2. Explore the pre-seeded drift scenarios using audit tools in Claude chat
3. Populate `.env` with live credentials for available systems
4. Enable additional shards as credentials are provisioned
5. Review `nexus-mcp/README.md` for the full tool reference and NEXUS work item tracking
