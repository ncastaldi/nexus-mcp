# ✅ VS Code & CI/CD Setup - Quick Reference

## 🚀 You're All Set!

The Nexus MCP server is now registered in VS Code with full CI/CD pipeline.

---

## 🎯 Quick Actions

### Use MCP Server in VS Code

```bash
# 1. Reload VS Code
Ctrl+Shift+P → "Developer: Reload Window"

# 2. Open Copilot Chat (@)

# 3. Type: @nexus 
# You'll see: nexus - Nexus MCP Server (48 tools)

# 4. Try it:
@nexus scan_status_reconciliation
@nexus list all audit tools
```

### Run Tests

```bash
cd nexus-mcp

# Quick test
pytest tests/integration_test_audit_shard.py -v

# Full suite
pytest tests/ -v
```

### Bump Version

```bash
# Local
python scripts/bump_version.py patch

# Or via GitHub Actions
# Actions → "Auto Version Bump" → Run workflow
```

---

## 📁 Files Created

### VS Code Configuration
- ✅ `.vscode/settings.json` - MCP server registration
- ✅ `.vscode/launch.json` - Debug configurations

### CI/CD Pipeline
- ✅ `.github/workflows/nexus-mcp-ci.yml` - Main pipeline
- ✅ `.github/workflows/version-bump.yml` - Auto version bump

### Scripts & Tools
- ✅ `scripts/bump_version.py` - Version management
- ✅ `VSCODE_INTEGRATION_GUIDE.md` - Full documentation

---

## 🔄 Will Registration Need Updates?

### ✅ Auto (No Action Needed)
- Adding/removing tools
- Changing tool implementations
- Updating dependencies

### ⚠️ Manual (Update `.vscode/settings.json`)
- Adding new shards
- Changing environment variables
- Moving server location

**How to check:** Review [VSCODE_INTEGRATION_GUIDE.md](VSCODE_INTEGRATION_GUIDE.md#future-updates--maintenance)

---

## 🏗️ CI/CD Pipeline

**Runs on:**
- Every push to main/develop
- Every pull request
- Manual trigger

**Checks:**
- ✅ Tests (Python 3.11-3.13)
- ✅ Server validation
- ✅ Security scan
- ✅ Version check (PRs)
- ✅ Build package

**View Status:**
GitHub → Actions tab → Latest runs

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| `VSCODE_INTEGRATION_GUIDE.md` | Complete setup & maintenance guide |
| `nexus-mcp/TEST_VALIDATION_REPORT.md` | Production readiness report |
| `nexus-mcp/DEMO_GUIDE.md` | Testing & demo scripts |
| `nexus-mcp/README.md` | Server documentation |

---

## 🐛 Troubleshooting

**MCP server not showing in Copilot Chat?**
1. Reload VS Code window
2. Check: View → Output → GitHub Copilot Chat
3. Verify `.vscode/settings.json` has `github.copilot.chat.mcpServers`

**Tools not working?**
1. Check server can start: `python nexus-mcp/src/main.py`
2. Run test client: `python nexus-mcp/test_client.py`
3. Check environment: `USE_MOCK=true` in config

**CI pipeline failing?**
1. View logs: GitHub → Actions → Failed run
2. Run tests locally: `pytest tests/ -v`
3. Check version was bumped (PRs)

---

## 🎉 Next Steps

1. **Test Integration**
   - Reload VS Code
   - Try `@nexus` in Copilot Chat
   - Run a tool: `@nexus scan_status_reconciliation`

2. **Commit This Setup**
   ```bash
   git add .vscode/ .github/ scripts/ *.md
   git commit -m "chore: add VS Code integration & CI/CD pipeline"
   git push origin rebuild-audit-tools
   ```

3. **Create PR to Main**
   - CI pipeline will run automatically
   - Version check will enforce version bump
   - Merge after approval

4. **Celebrate!** 🎉
   - You now have MCP server in VS Code
   - Full CI/CD validation
   - Automated version management

---

**Need Help?** See [VSCODE_INTEGRATION_GUIDE.md](VSCODE_INTEGRATION_GUIDE.md)
