# Identity MCP → Copilot Studio Deployment Guide

## Overview

This guide walks you through deploying your Identity MCP server to Microsoft Copilot Studio using **Option 2: Custom MCP Connector** via Power Apps.

**Prerequisite:** You must have an HTTPS-accessible endpoint for your Identity MCP server. Copilot Studio cannot connect to localhost or STDIO-based servers.

---

## Phase 1: Prepare your Identity MCP for HTTP transport

### Step 1: Update dependencies (if needed)

Your Identity MCP can now run with streamable HTTP transport. Ensure you have the server extras installed:

```bash
cd "MCP Servers/Identity"
uv pip install "mcp[server]>=1.2.0"
```

### Step 2: Configure environment variables

The server now supports two transport modes via environment variables:

**For local/VS Code testing (STDIO):**
```bash
# Default - no env vars needed
export MCP_TRANSPORT=stdio
python identity_mcp_server.py
```

**For Copilot Studio (Streamable HTTP):**
```bash
export MCP_TRANSPORT=streamable
export MCP_HOST=0.0.0.0          # Bind to all interfaces
export MCP_PORT=8000             # Choose your port
export IDENTITY_BACKEND=ad       # Use Active Directory backend
python identity_mcp_server.py
```

### Step 3: Test streamable transport locally

Before deploying to production, validate the HTTP endpoint works:

```bash
# Terminal 1: Start the server
cd "MCP Servers/Identity"
export MCP_TRANSPORT=streamable
export MCP_PORT=8000
export IDENTITY_BACKEND=memory  # Safe mode for testing
python identity_mcp_server.py
```

```bash
# Terminal 2: Test the endpoint
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":"test-1"}'
```

**Expected response:** JSON with available tools (get_user, search_users_by_name, etc.)

---

## Phase 2: Deploy to production hosting

### Hosting options

Your Identity MCP must be accessible via HTTPS from Power Platform cloud services. Common options:

1. **Azure App Service** (recommended for Microsoft ecosystem)
2. **Azure Container Instances** with HTTPS ingress
3. **On-premises IIS** with reverse proxy + public HTTPS endpoint
4. **VM with nginx/caddy** reverse proxy + Let's Encrypt cert

### Security requirements

✅ **HTTPS only** — Power Platform will not connect to HTTP  
✅ **Valid SSL certificate** — self-signed certs will fail  
✅ **Firewall rules** — allow inbound HTTPS from Power Platform IP ranges  
✅ **Authentication** — configure API key or OAuth (see Phase 3)

### Example: Azure App Service deployment

```bash
# Install Azure CLI if not already installed
az login

# Create resource group
az group create --name rg-identity-mcp --location eastus

# Create App Service plan (Linux)
az appservice plan create \
  --name plan-identity-mcp \
  --resource-group rg-identity-mcp \
  --sku B1 \
  --is-linux

# Create web app with Python runtime
az webapp create \
  --name identity-mcp-wheels \
  --resource-group rg-identity-mcp \
  --plan plan-identity-mcp \
  --runtime "PYTHON:3.11"

# Configure environment variables
az webapp config appsettings set \
  --name identity-mcp-wheels \
  --resource-group rg-identity-mcp \
  --settings \
    MCP_TRANSPORT=streamable \
    MCP_HOST=0.0.0.0 \
    MCP_PORT=8000 \
    IDENTITY_BACKEND=ad \
    AD_USERNAME="svc-identity-mcp@wheelsinc.com" \
    AD_PASSWORD="<secure-password-from-key-vault>"

# Deploy code (from repo root)
cd "MCP Servers/Identity"
zip -r deploy.zip .
az webapp deploy \
  --name identity-mcp-wheels \
  --resource-group rg-identity-mcp \
  --src-path deploy.zip \
  --type zip

# Verify deployment
curl https://identity-mcp-wheels.azurewebsites.net/mcp
```

**Your production URL:** `https://identity-mcp-wheels.azurewebsites.net`

---

## Phase 3: Configure authentication (recommended)

### Option A: API Key (simplest for Phase 1)

1. **Generate a strong API key:**

```bash
# Generate a secure random key (save this!)
openssl rand -hex 32
# Example output: a1b2c3d4e5f6...
```

2. **Configure your MCP server to validate API keys:**

Add to your server code (before tool definitions):

```python
import os
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

API_KEY = os.getenv("MCP_API_KEY")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

async def verify_api_key(key: str = Security(api_key_header)):
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return key
```

3. **Store API key in your hosting environment:**

```bash
# Azure App Service
az webapp config appsettings set \
  --name identity-mcp-wheels \
  --resource-group rg-identity-mcp \
  --settings MCP_API_KEY="<your-generated-key>"
```

### Option B: OAuth 2.0 (for Phase 3+ with user delegation)

OAuth configuration is outlined in the OpenAPI file. Defer to Phase 3 when write operations are enabled.

---

## Phase 4: Import OpenAPI schema to Power Apps

### Step 1: Customize the OpenAPI file

Edit `identity-mcp-openapi.yaml`:

1. **Update host:** Replace `your-identity-mcp-host.yourdomain.com` with your actual production URL:
   ```yaml
   host: identity-mcp-wheels.azurewebsites.net
   ```

2. **Configure authentication:** Uncomment the security method you chose (API key is already configured).

3. **Save the file.**

### Step 2: Create custom connector in Power Apps

1. Go to your Copilot Studio agent
2. Navigate to **Tools** page
3. Click **Add a tool**
4. Select **New tool**
5. Select **Custom connector**

   ➜ You're redirected to Power Apps

6. In Power Apps:
   - Click **New custom connector**
   - Select **Import OpenAPI file**
   - Upload `identity-mcp-openapi.yaml`
   - Click **Continue**

### Step 3: Configure connector security

On the **Security** tab:

**If using API Key:**
- Authentication type: **API Key**
- Parameter label: `API Key`
- Parameter name: `X-API-Key`
- Parameter location: **Header**

**If using OAuth 2.0:**
- Follow the OAuth configuration from the Microsoft Learn doc (linked in References)

Click **Create connector** when done.

### Step 4: Test the connector

1. On the **Test** tab, click **New connection**
2. Enter your API key (if using API key auth)
3. Click **Create connection**
4. In the **Operations** section, select `InvokeIdentityMCP`
5. Paste a test MCP request payload:

```json
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "id": "test-1"
}
```

6. Click **Test operation**
7. **Expected result:** 200 OK with list of available tools

---

## Phase 5: Add connector to Copilot Studio agent

1. Return to Copilot Studio (close Power Apps tab)
2. On the **Add tool** dialog:
   - Select your newly created **Identity MCP** connector
   - Click **Create a new connection** (or use existing)
3. Authenticate if prompted
4. Click **Add to agent**

---

## Phase 6: Validate end-to-end

### Test in agent chat

1. Open your agent's **Test chat** panel
2. Ask a question that should trigger Identity MCP tools:

   **Example prompts:**
   - "Get user details for jsmith"
   - "Who are the members of the VPN-Users group?"
   - "Find users who haven't logged in for 90 days"

3. **Check tool invocation:**
   - Open the trace/tool panel (if available)
   - Confirm the Identity MCP tool was invoked
   - Validate the response matches expected data

### Troubleshooting validation

| Issue | Check |
| --- | --- |
| Tool not invoked | Improve connector description and operation summary so orchestrator understands when to call it |
| 401 Unauthorized | Verify API key matches in both server config and connector connection |
| 500 Server error | Check server logs for backend failures (AD connectivity, permissions) |
| Tool returns empty results | Test the same query via manual PowerShell to isolate MCP vs AD issue |

---

## Security & governance checklist

Before enabling for production use:

- [ ] HTTPS with valid certificate confirmed
- [ ] API key (or OAuth) authentication enabled and tested
- [ ] Service account permissions validated (Read Directory Data only for Phase 1)
- [ ] Audit logging verified (tool name, params, timestamp, result)
- [ ] Connector restricted to authorized agents only
- [ ] Rate limiting configured (if available in hosting environment)
- [ ] Connection timeout tested under load
- [ ] Disaster recovery plan documented (connector re-import procedure)

---

## Maintenance procedures

### Update connector after schema changes

If you modify tool definitions or add new tools:

1. Update `identity-mcp-openapi.yaml` with new endpoint details
2. In Power Apps, navigate to **Custom connectors**
3. Select **Identity MCP** connector
4. Click **Update from OpenAPI file**
5. Upload the updated YAML
6. Click **Update connector**
7. Test updated operations on the **Test** tab
8. Return to Copilot Studio and verify new tools are available

### Monitor API usage

Check connector call metrics regularly:

1. Power Apps → **Custom connectors** → **Identity MCP**
2. View **Analytics** tab for:
   - Call volume
   - Error rates
   - Latency trends

---

## References

- [Microsoft Learn: Add existing MCP server to agent](https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-add-existing-server-to-agent#option-2-create-a-custom-mcp-connector-in-power-apps)
- [Microsoft Learn: Custom connectors in Power Apps](https://learn.microsoft.com/en-us/connectors/custom-connectors/)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/specification/)
- Internal: `identity-mcp-install-guide.md` (Phase 0-4 governance procedures)

---

## Revision history

| Version | Date | Author | Changes |
| --- | --- | --- | --- |
| 1.0 | 2026-03-11 | N. Castaldi | Initial deployment guide for Option 2 (Custom Connector) path |
