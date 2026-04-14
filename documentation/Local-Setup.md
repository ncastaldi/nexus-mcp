# Nexus-MCP local setup

Sharded enterprise integration MCP server for Active Directory, Entra ID, Workday, and cross-system drift auditing.

---

## Prerequisites

- Python 3.11 or newer
- Git
- PowerShell (Windows) or bash (Linux/macOS)
- Access to corporate systems (AD, Entra, Workday) or mock mode enabled

---

## Installation

### 1. Clone and navigate

```bash
cd /path/to/mcp_servers
cd nexus-mcp
```

### 2. Create virtual environment

```bash
python -m venv .venv
```

### 3. Activate virtual environment

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows (bash/Git Bash):**
```bash
source .venv/Scripts/activate
```

**Linux/macOS:**
```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -e .
```

This installs nexus-mcp in editable mode with all required packages (mcp, httpx, python-dotenv, ldap3, msal, etc.).

---

## Configuration

### 1. Create .env file

```bash
cp .env.example .env
```

### 2. Choose your mode

**Option A: Mock Mode (No credentials needed)**

Good for development, testing shards, and exploring drift scenarios.

```env
USE_MOCK=true

# Enable the shards you want to test
ENABLE_IDENTITY=true
ENABLE_WORKDAY=true
ENABLE_AUDIT=true
ENABLE_ITSM=false
ENABLE_ASSETS=false
ENABLE_LOGISTICS=false

# Audit logging
AUDIT_LOGGING_ENABLED=true
AUDIT_LOG_FILE=./logs/nexus_audit.jsonl
AUDIT_LOG_STDERR=true
```

**Option B: Live Mode (Production credentials)**

Requires actual service accounts and API credentials.

```env
USE_MOCK=false

# Enable only the shards where you have credentials
ENABLE_IDENTITY=true
ENABLE_WORKDAY=false    # Set true when credentials available
ENABLE_AUDIT=true
ENABLE_ITSM=false
ENABLE_ASSETS=false
ENABLE_LOGISTICS=false

# Active Directory credentials
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

# (Add other system credentials as needed)
```

### 3. Verify configuration

Your `.env` file is never committed to git (listed in `.gitignore`).

---

## Running the server

### Start the MCP server

```bash
python src/main.py
```

**Expected output (mock mode):**

```
[nexus] ✅ identity shard loaded
[nexus] ✅ workday shard loaded
[nexus] ✅ audit shard loaded
[nexus] ⏸  itsm shard disabled (ENABLE_ITSM != true)
[nexus] ⏸  assets shard disabled (ENABLE_ASSETS != true)
[nexus] ⏸  logistics shard disabled (ENABLE_LOGISTICS != true)
[nexus] 🔒 SOC 2 audit middleware active — 16 tools wrapped → ./logs/nexus_audit.jsonl
```

The server runs on stdio transport and waits for MCP protocol messages.

---

## Claude Desktop integration

Add this to your Claude Desktop `config.json`:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

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

Restart Claude Desktop. You should see the Nexus tools in the tool picker.

---

## Feature flag reference

Control which shards load at startup:

| Flag | Shard | Systems | Default |
|---|---|---|---|
| `ENABLE_IDENTITY` | identity.py | AD + Entra ID | `true` |
| `ENABLE_WORKDAY` | workday.py | Workday HCM | `true` |
| `ENABLE_AUDIT` | audit.py | Cross-system drift | `true` |
| `ENABLE_ITSM` | itsm.py | BMC Helix | `false` |
| `ENABLE_ASSETS` | assets.py | Lansweeper + Intune | `false` |
| `ENABLE_LOGISTICS` | logistics.py | FedEx | `false` |

Set a flag to `false` (or omit it) to put that shard in "holding pattern" mode. The server will start successfully but skip loading those tools.

---

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

Run specific test modules:

```bash
pytest tests/identity_tests/ -v
pytest tests/workday_tests/ -v
```

Run with coverage:

```bash
pytest tests/ --cov=lib --cov=src --cov-report=term-missing
```

---

## Mock mode drift scenarios

The lib/mock_data.py file includes deliberate drift:

- **Bob Martinez:** title differs between AD ("Sr. Software Engineer") and Workday/Entra ("Software Engineer")
- **Carol Chen:** department differs — Workday "Product Management" vs AD "Engineering"
- **David Kim:** AD account disabled but Entra account still enabled
- **Emma Wilson:** AD stale account (no login in 120 days)

Use the audit tools to detect these:

```python
# In Claude chat with Nexus-MCP active
"Run audit_user_drift for Bob Martinez"
"Show me all stale AD accounts"
```

---

## Troubleshooting

### Server won't start

- Check Python version: `python --version` (must be 3.11+)
- Verify virtual environment is active (you should see `(.venv)` in your prompt)
- Verify dependencies installed: `pip list | grep mcp`

### Shard not loading

- Check the feature flag in `.env`: `ENABLE_IDENTITY=true`
- Look for error messages in the startup output
- Verify the shard file exists: `ls src/shards/identity.py`

### Credentials not working (live mode)

- Test AD connectivity: `python -c "import ldap3; print(ldap3.__version__)"`
- Verify service account can bind to LDAP
- Check firewall rules if connecting to on-prem AD

### Audit log not writing

- Check permissions on the `logs/` directory
- Verify `AUDIT_LOGGING_ENABLED=true` in `.env`
- Check disk space

---

## Development workflow

### Adding a new tool to an existing shard

1. Edit the shard file: `src/shards/identity.py`
2. Add your tool function inside the `register(mcp)` function
3. Restart the server
4. Test with Claude Desktop

### Creating a new shard

1. Copy an existing shard as a template: `cp src/shards/identity.py src/shards/my_system.py`
2. Implement the `register(mcp)` function with your tools
3. Add the shard to `src/main.py`:
   ```python
   if _enabled("MY_SYSTEM"):
       my_system.register(mcp)
   ```
4. Add the feature flag to `.env.example`: `ENABLE_MY_SYSTEM=false`

### Switching between mock and live mode

Just change `USE_MOCK` in `.env` and restart:

```bash
# Switch to live
USE_MOCK=false

# Restart server
python src/main.py
```

No code changes needed — every shard checks the `USE_MOCK` flag automatically.

---

## SOC 2 audit logging

Every tool call is logged to `logs/nexus_audit.jsonl` (one JSON object per line).

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

Query the audit log using the built-in tools:

```python
# In Claude chat
"Show me the last 50 audit log entries"  # calls nexus_audit_recent
"Give me audit statistics"               # calls nexus_audit_stats
```

---

## Next steps

1. Test mock mode with `USE_MOCK=true` to verify the shards load
2. Explore the drift scenarios using audit tools
3. Configure credentials for live systems
4. Enable additional shards as credentials become available
5. Build custom reports using the audit shard tools

For more details, see [README.md](README.md) for the full tool reference.
