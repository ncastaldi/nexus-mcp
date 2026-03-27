# Identity MCP → Copilot Studio Quick Start

## Prerequisites
- [ ] Identity MCP server running with streamable HTTP transport  
- [ ] HTTPS endpoint publicly accessible from Power Platform  
- [ ] API key generated and configured  

## Quick setup commands

```bash
# 1. Test streamable transport locally
cd "MCP Servers/Identity"
export MCP_TRANSPORT=streamable
export MCP_PORT=8000
export IDENTITY_BACKEND=memory
python identity_mcp_server.py

# 2. Generate API key
openssl rand -hex 32

# 3. Test endpoint
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":"1"}'
```

## OpenAPI file configuration

Edit `identity-mcp-openapi.yaml`:
1. Line 16: Replace `your-identity-mcp-host.yourdomain.com` with your actual host
2. Lines 26-30: Ensure API key security is uncommented (default)
3. Save file

## Import to Copilot Studio

1. Copilot Studio → Tools → Add tool → New tool → Custom connector  
2. Power Apps → New custom connector → Import OpenAPI file  
3. Upload `identity-mcp-openapi.yaml` → Continue  
4. Security tab → API Key → Header → `X-API-Key` → Create  
5. Test tab → New connection → Enter API key → Test operation  
6. Return to Copilot Studio → Add tool → Select connector → Add to agent  

## Test prompts

- "Get user details for jsmith"
- "Who are the members of VPN-Users?"
- "Find stale users over 90 days"

## Files created

✅ `identity-mcp-openapi.yaml` — OpenAPI schema for Power Apps import  
✅ `identity_mcp_server.py` — Updated with streamable HTTP support  
✅ `copilot-studio-deployment-guide.md` — Full step-by-step walkthrough  

---

**Next step:** Follow [copilot-studio-deployment-guide.md](copilot-studio-deployment-guide.md) for full deployment procedure.
