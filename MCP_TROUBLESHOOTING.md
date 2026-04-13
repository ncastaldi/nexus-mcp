# MCP Server Troubleshooting Guide

## Issue: MCP Server Not Showing in VS Code Copilot

### What We've Done

1. ✅ Updated `.vscode/settings.json` with full Python path
2. ✅ Added PYTHONPATH and PYTHONUNBUFFERED environment variables
3. ✅ Verified server has proper `mcp.run(transport="stdio")` setup
4. ✅ Created alternative configuration file

### Diagnostic Steps

#### 1. Check VS Code Output Panel

**How:**
1. Open: `View` → `Output`
2. Select dropdown: `GitHub Copilot Chat`
3. Look for MCP-related errors

**What to look for:**
- `Failed to start MCP server "nexus"`
- `Python not found`
- `Module not found`
- Any error mentioning "nexus" or "mcp"

#### 2. Verify Copilot Extension Version

**Required:** GitHub Copilot extension **v0.12.0 or newer**

**Check:**
1. Extensions panel (`Ctrl+Shift+X`)
2. Search: "GitHub Copilot"
3. Check version number
4. Update if needed

**Note:** MCP support is a recent feature. Older versions won't recognize MCP servers.

#### 3. Verify Settings Location

**Workspace vs User Settings:**

The configuration should be in **workspace settings**, not user settings.

**Check:**
```
.vscode/settings.json  ← Should be here (workspace)
```

**Not here:**
```
%APPDATA%\Code\User\settings.json  ← User settings (wrong location)
```

#### 4. Alternative Configuration Locations

VS Code Copilot may look for MCP servers in:

**Option A: Workspace settings (recommended)**
```
.vscode/settings.json
```

**Option B: User-level MCP config**
```
%APPDATA%\Code\User\globalStorage\github.copilot-chat\mcp_settings.json
```

I've created `mcp_settings.json` in the workspace root as an alternative.

**To use Option B:**
1. Copy `mcp_settings.json` to the user-level path above
2. Create the directory if it doesn't exist
3. Reload VS Code

#### 5. Test Server Manually

Verify the server can start:

```bash
cd nexus-mcp
.venv\Scripts\python.exe src\main.py
```

**Expected:** Server starts and waits for stdio input (no output is normal)
**Press Ctrl+C to exit**

If this fails, there's a problem with the server itself (not VS Code config).

#### 6. Check for Python Path Issues

Current configuration uses:
```
${workspaceFolder}/nexus-mcp/.venv/Scripts/python.exe
```

**Test if VS Code resolves this:**
1. Open Terminal in VS Code
2. Run: `echo ${workspaceFolder}`
3. Should show: `C:\Users\castn1.CORP\OneDrive - Wheels\Repos\mcp_servers`

If blank, VS Code can't resolve workspace variables.

**Workaround:** Use absolute path in settings.json:
```json
"command": "C:/Users/castn1.CORP/OneDrive - Wheels/Repos/mcp_servers/nexus-mcp/.venv/Scripts/python.exe"
```

### Common Issues & Solutions

#### Issue: "command not found: python"

**Solution:** Use absolute path to Python:
```json
"command": "C:/Users/castn1.CORP/OneDrive - Wheels/Repos/mcp_servers/nexus-mcp/.venv/Scripts/python.exe"
```

#### Issue: "No such file or directory: main.py"

**Solution:** Check `cwd` is correct:
```json
"cwd": "${workspaceFolder}/nexus-mcp"
```

#### Issue: "Module not found" errors

**Solution:** Add PYTHONPATH:
```json
"env": {
  "PYTHONPATH": "${workspaceFolder}/nexus-mcp/src:${workspaceFolder}/nexus-mcp/lib"
}
```

#### Issue: Server starts but tools don't appear

**Possible causes:**
1. Copilot extension too old (update to v0.12.0+)
2. MCP protocol mismatch
3. Server responding but not following MCP spec

**Debug:** Check Copilot output panel for protocol errors

### Alternative: Use Claude Desktop Instead

If VS Code Copilot continues to have issues, you can use Claude Desktop with the same MCP server:

**Location:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "nexus": {
      "command": "C:/Users/castn1.CORP/OneDrive - Wheels/Repos/mcp_servers/nexus-mcp/.venv/Scripts/python.exe",
      "args": [
        "C:/Users/castn1.CORP/OneDrive - Wheels/Repos/mcp_servers/nexus-mcp/src/main.py"
      ],
      "env": {
        "USE_MOCK": "true",
        "ENABLE_AUDIT": "true"
      }
    }
  }
}
```

### Still Not Working?

**Try this minimal test:**

1. Create a simple MCP server test:

```python
# test_simple_mcp.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("test")

@mcp.tool()
def hello() -> str:
    """Say hello"""
    return "Hello from MCP!"

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

2. Add to settings.json:

```json
"github.copilot.chat.mcpServers": {
  "test": {
    "command": "python",
    "args": ["${workspaceFolder}/test_simple_mcp.py"]
  }
}
```

3. Reload VS Code
4. Try `@test` in Copilot Chat

If this works, the issue is with the Nexus server. If not, it's a VS Code/Copilot configuration issue.

### Report Issues

If none of these work, the issue may be:
1. VS Code Copilot doesn't support MCP yet on your version
2. Feature not available in your region/license
3. Bug in Copilot extension

Check: https://github.com/microsoft/vscode-copilot/issues
