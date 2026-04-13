# VS Code Integration & CI/CD Guide

**Last Updated:** April 13, 2026  
**Version:** 0.1.0

---

## 📋 Table of Contents

1. [VS Code MCP Registration](#vs-code-mcp-registration)
2. [Future Updates & Maintenance](#future-updates--maintenance)
3. [CI/CD Pipeline](#cicd-pipeline)
4. [Version Management](#version-management)
5. [Development Workflow](#development-workflow)

---

## VS Code MCP Registration

### ✅ Initial Setup (Complete)

The Nexus MCP server is now registered in VS Code Copilot!

**Configuration Files Created:**
- `.vscode/settings.json` - MCP server registration + Python settings
- `.vscode/launch.json` - Debug configurations

### How to Use

**1. Reload VS Code**
```bash
# Press Ctrl+Shift+P (or Cmd+Shift+P on Mac)
# Type: "Developer: Reload Window"
```

**2. Verify Registration**
- Open GitHub Copilot Chat
- Type: `@nexus` - you should see the server autocomplete
- Try: `@nexus scan_status_reconciliation`

**3. Available Commands**
All 48 tools from the Nexus server are now available in Copilot Chat:

```
🔍 Audit Tools (4):
  • scan_status_reconciliation
  • scan_job_title_drift
  • scan_department_mismatches
  • scan_name_variance_mismatches

🔐 Identity Tools (15):
  • ad_get_user, ad_search_users, entra_list_users, etc.

👥 Workday Tools (7):
  • workday_get_worker, workday_list_workers, etc.

... and 22 more tools across ITSM, Assets, and Logistics
```

### Current Configuration

**Location:** `.vscode/settings.json`

```json
{
  "github.copilot.chat.mcpServers": {
    "nexus": {
      "command": "python",
      "args": ["${workspaceFolder}/nexus-mcp/src/main.py"],
      "cwd": "${workspaceFolder}/nexus-mcp",
      "env": {
        "USE_MOCK": "true",
        "ENABLE_AUDIT": "true"
        // ... all shards enabled
      }
    }
  }
}
```

**Key Features:**
- ✅ Uses workspace-relative paths (portable across machines)
- ✅ Mock mode enabled by default (no credentials needed)
- ✅ All 6 shards enabled
- ✅ Auto-activates Python virtual environment

---

## Future Updates & Maintenance

### ❓ Will Registration Need Updates?

**YES** - in these scenarios:

| Scenario | Update Required | Auto-Detected |
|----------|-----------------|---------------|
| **New tools added** | ❌ No | ✅ Yes - Auto-discovery |
| **Tool signatures change** | ❌ No | ✅ Yes - Auto-discovery |
| **New shards added** | ⚠️ Maybe | Add `ENABLE_*` flag |
| **Environment variables change** | ✅ Yes | Update `.vscode/settings.json` |
| **Server path moves** | ✅ Yes | Update `args` in config |
| **Python version upgrade** | ❌ No | Uses workspace .venv |

### 🔄 When to Update

**AUTO (No Action Needed):**
- Adding/removing MCP tools within existing shards
- Changing tool implementations
- Updating dependencies in pyproject.toml

**MANUAL (Update Required):**
- Adding new shard (e.g., `ENABLE_HR=true`)
- Changing required environment variables
- Moving server location in repo structure

### 📝 How to Update

**Option 1: Edit `.vscode/settings.json` directly**
```json
{
  "github.copilot.chat.mcpServers": {
    "nexus": {
      "env": {
        "ENABLE_NEW_SHARD": "true"  // ← Add new flag
      }
    }
  }
}
```

**Option 2: Use version bump script (recommended)**
```bash
python scripts/bump_version.py minor
# Automatically updates version-sensitive configs
```

---

## CI/CD Pipeline

### 🔧 GitHub Actions Workflows

**1. Main CI Pipeline** (`.github/workflows/nexus-mcp-ci.yml`)

**Triggers:**
- Push to `main`, `develop`, or `rebuild-*` branches
- Pull requests to `main` or `develop`
- Manual workflow dispatch

**Jobs:**

| Job | Purpose | Duration |
|-----|---------|----------|
| **test** | Run unit + integration tests (Python 3.11-3.13) | ~2 min |
| **validate-server** | Verify server starts and tools register | ~1 min |
| **security-scan** | Check dependencies & scan for secrets | ~3 min |
| **version-check** | Ensure version bumped (PR only) | ~30 sec |
| **build** | Create distribution package | ~1 min |

**2. Version Bump Workflow** (`.github/workflows/version-bump.yml`)

**Trigger:** Manual workflow dispatch

**Inputs:**
- `bump_type`: patch | minor | major
- `update_readme`: true | false

**Actions:**
1. Bumps version in `pyproject.toml`
2. Updates README with version note
3. Commits changes: `chore: bump version to X.Y.Z`
4. Creates git tag: `vX.Y.Z`
5. Pushes to repository

### 📊 Pipeline Status

**View Status:**
- Badge (add to README): `![CI](https://github.com/USER/REPO/workflows/nexus-mcp-ci/badge.svg)`
- Actions tab: https://github.com/your-org/mcp_servers/actions

**Email Notifications:**
- Enabled by default for workflow failures
- Configure in GitHub settings: Settings → Notifications

---

## Version Management

### 🏷️ Semantic Versioning

We follow [SemVer 2.0.0](https://semver.org/):

```
MAJOR.MINOR.PATCH

major: Breaking changes (e.g., remove tools, change schemas)
minor: New features (e.g., add tools, new shards)
patch: Bug fixes, documentation, refactoring
```

**Current Version:** 0.1.0

### 📦 Version Bump Methods

**Method 1: Automated (GitHub Actions)**

```bash
# Via GitHub UI:
# 1. Go to Actions → "Auto Version Bump"
# 2. Click "Run workflow"
# 3. Select bump type
# 4. Click "Run workflow"
```

**Method 2: Local Script**

```bash
# Patch: 0.1.0 → 0.1.1
python scripts/bump_version.py patch

# Minor: 0.1.0 → 0.2.0
python scripts/bump_version.py minor

# Major: 0.1.0 → 1.0.0
python scripts/bump_version.py major

# Then commit & push
git push origin main --tags
```

**Method 3: Manual**

```toml
# Edit nexus-mcp/pyproject.toml
[project]
version = "0.2.0"  # ← Update here
```

```bash
git add nexus-mcp/pyproject.toml
git commit -m "chore: bump version to 0.2.0"
git tag v0.2.0
git push origin main --tags
```

### 📋 Version Checklist

Before releasing a new version:

- [ ] All tests passing (`pytest tests/ -v`)
- [ ] Server starts successfully
- [ ] Tools execute without errors
- [ ] README updated with changes
- [ ] Version bumped in `pyproject.toml`
- [ ] Git tag created: `vX.Y.Z`
- [ ] CHANGELOG updated (if exists)

---

## Development Workflow

### 🎯 Typical Development Cycle

```bash
# 1. Create feature branch
git checkout -b feature/add-new-audit-tool

# 2. Make changes
vim nexus-mcp/src/shards/audit.py

# 3. Add tests
vim nexus-mcp/tests/test_new_audit_tool.py

# 4. Run tests locally
cd nexus-mcp
python -m pytest tests/ -v

# 5. Test in VS Code
# - Reload window (Ctrl+Shift+P → "Reload Window")
# - Test with @nexus in Copilot Chat

# 6. Commit & push
git add .
git commit -m "feat(audit): add new audit tool"
git push origin feature/add-new-audit-tool

# 7. Create PR
# - CI pipeline runs automatically
# - Version check enforced
# - Merge after approval

# 8. Bump version & release
python scripts/bump_version.py minor
git push origin main --tags
```

### 🔍 Testing Before Commit

**Quick Validation:**
```bash
# Run audit tests only
pytest tests/workday_tests/test_mismatch_scans.py tests/integration_test_audit_shard.py -v

# Test server startup
python test_client.py

# Verify tool count
python list_tools.py | grep "Total:"
# Should show: ✅ Total: 48 tools available
```

**Full Validation:**
```bash
# All tests
pytest tests/ -v --tb=short

# Server functionality
python test_mcp_protocol.py

# Linting (if ruff installed)
ruff check src/ lib/ tests/
```

### 🐛 Debugging with VS Code

**Launch Configurations Available:**

1. **Nexus MCP Server (Mock Mode)** - Start server with debugger
2. **Run Audit Tests** - Debug audit test suite
3. **Run All Tests** - Debug full test suite
4. **Demo: Test Client** - Debug client demonstration

**Usage:**
1. Press `F5` or use Debug panel
2. Select configuration from dropdown
3. Set breakpoints in source files
4. Step through code execution

---

## ❓ FAQ

### Q: Will adding a new tool break the VS Code integration?

**A:** No! Tools are auto-discovered via MCP protocol. Just:
1. Register tool with `@mcp.tool()` decorator
2. Reload VS Code window
3. Tool is immediately available via `@nexus`

### Q: Do I need to restart VS Code after every code change?

**A:** Only for:
- ✅ Adding/removing tools
- ✅ Changing tool names
- ✅ Modifying `.vscode/settings.json`

**Not needed for:**
- ❌ Changing tool implementations
- ❌ Updating mock data
- ❌ Modifying dependencies

### Q: How do I disable mock mode?

**Edit `.vscode/settings.json`:**
```json
{
  "github.copilot.chat.mcpServers": {
    "nexus": {
      "env": {
        "USE_MOCK": "false"  // ← Change to false
      }
    }
  }
}
```

Then configure real credentials in `nexus-mcp/.env`.

### Q: Can I have multiple MCP server configurations?

**Yes!** Add multiple entries:
```json
{
  "github.copilot.chat.mcpServers": {
    "nexus-mock": {
      "env": { "USE_MOCK": "true" }
    },
    "nexus-prod": {
      "env": { "USE_MOCK": "false" }
    }
  }
}
```

Use `@nexus-mock` or `@nexus-prod` in Copilot Chat.

### Q: Where do CI/CD logs go?

**GitHub Actions:**
- Tab: https://github.com/your-org/mcp_servers/actions
- Each workflow run shows detailed logs per job
- Artifacts (builds) stored for 30 days

### Q: How do I add a new CI check?

**Edit `.github/workflows/nexus-mcp-ci.yml`:**
```yaml
jobs:
  my-new-check:
    name: My New Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run my check
        run: echo "Custom check here"
```

---

## 📞 Support

**Issues:**
- GitHub Issues: https://github.com/your-org/mcp_servers/issues
- Tag with: `nexus-mcp`, `vscode-integration`, or `ci-cd`

**Documentation:**
- Main README: `nexus-mcp/README.md`
- Test Report: `nexus-mcp/TEST_VALIDATION_REPORT.md`
- Demo Guide: `nexus-mcp/DEMO_GUIDE.md`

---

**Last Updated:** April 13, 2026  
**Maintainer:** IT Engineering Team  
**Status:** ✅ Production Ready
