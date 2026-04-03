# Local development quick-start

## 1. Move to runtime directory (why: inspector resolves `server.py` from current directory)

```bash
cd Workday/workday-mcp
```

## 2. Activate environment (why: guarantees the project Python and dependencies are used)

```bash
source .venv/Scripts/activate
```

## 3. Launch inspector (tested)

Use the explicit Python path to avoid shell alias/path drift:

```bash
npx @modelcontextprotocol/inspector "c:/Users/castn1.CORP/OneDrive - Wheels/Repos/mcp_servers/Workday/workday-mcp/.venv/Scripts/python.exe" server.py
```

Why: this starts the Inspector UI and spawns the MCP server over STDIO. If startup succeeds, the CLI prints a localhost URL that includes an auth token.

## 4. Port cleanup when blocked (tested)

If you see `Proxy Server PORT IS IN USE at port 6277`, use one of the following:

PowerShell (recommended):

```powershell
Get-NetTCPConnection -State Listen -LocalPort 6277,6274 |
    Select-Object LocalAddress,LocalPort,OwningProcess

Stop-Process -Id <PID> -Force
```

Why: kill by PID is more reliable than killing `node.exe` by name because the owning process may vary.

Git Bash alternative:

```bash
for p in 6277 6274; do
  pids=$(netstat -ano | awk -v port=":$p" '$2 ~ port {print $5}' | tr -d '\r' | sort -u)
  for pid in $pids; do
    cmd.exe /c taskkill /F /PID "$pid"
  done
done
```

## 5. Optional quick health checks after connect

Run these tools in Inspector and verify non-empty output:

- `scan_status_reconciliation`
- `scan_job_title_drift`
- `scan_department_mismatches`
- `scan_name_variance_mismatches`

Expected baseline in current mock data:

- status drift: 1 mismatch
- title drift: 1 mismatch
- department drift: 1 mismatch
- name variance: 3 mismatches
