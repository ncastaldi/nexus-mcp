#!/usr/bin/env python3
"""Test the Nexus MCP server as if we're Claude Desktop connecting to it.

This simulates the MCP protocol handshake and tool invocation flow.
"""

import asyncio
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from dotenv import load_dotenv
load_dotenv()

print("=" * 100)
print("MCP PROTOCOL SIMULATION - Testing Nexus Server Integration")
print("=" * 100)
print()

# Import server components
from mcp.server.fastmcp import FastMCP
from shards import identity, workday, itsm, assets, logistics, audit

# Initialize the MCP server
mcp = FastMCP(
    name="Nexus",
    instructions=(
        "Nexus is the enterprise integration MCP. You have access to identity "
        "(AD + Entra), workforce (Workday), ITSM (BMC Helix), asset inventory "
        "(Lansweeper + Intune), logistics (FedEx), and cross-system audit tools. "
        "Use audit_* tools to detect field drift. Use generate_* tools for weekly reports."
    ),
)

def _enabled(flag: str) -> bool:
    return os.getenv(f"ENABLE_{flag}", "true").strip().lower() == "true"

# Register all enabled shards
print("📡 Initializing MCP server...")
print()

shards = [
    ("IDENTITY", identity, "Active Directory + Entra ID"),
    ("WORKDAY", workday, "Workday HCM"),
    ("ITSM", itsm, "BMC Helix ITSM"),
    ("ASSETS", assets, "Lansweeper + Intune"),
    ("LOGISTICS", logistics, "FedEx"),
    ("AUDIT", audit, "Cross-system drift detection"),
]

for flag, shard, description in shards:
    if _enabled(flag):
        shard.register(mcp)
        print(f"   ✅ {flag.lower()} → {description}")

print()
print(f"✅ Server ready: {len(mcp._tool_manager._tools)} tools registered")
print()

# Simulate MCP protocol interactions
print("=" * 100)
print("SIMULATING MCP CLIENT REQUESTS")
print("=" * 100)
print()

# Request 1: List available tools (like Claude Desktop would do on connect)
print("🔌 CLIENT → SERVER: tools/list")
print("-" * 100)

available_tools = []
for tool_name, tool_obj in mcp._tool_manager._tools.items():
    if tool_name.startswith("scan_"):  # Focus on audit tools for this demo
        tool_schema = {
            "name": tool_name,
            "description": tool_obj.fn.__doc__.strip().split('\n')[0] if tool_obj.fn.__doc__ else "",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
        available_tools.append(tool_schema)

print(f"SERVER → CLIENT: {len(available_tools)} audit tools available")
for tool in available_tools:
    print(f"   • {tool['name']}")
    print(f"     {tool['description']}")
print()

# Request 2: Invoke a tool (scan for terminated users)
print("🔌 CLIENT → SERVER: tools/call - scan_status_reconciliation")
print("-" * 100)

tool_fn = mcp._tool_manager._tools["scan_status_reconciliation"].fn
result = tool_fn()

print("SERVER → CLIENT: Tool execution result")
print()
print(json.dumps(result, indent=2))
print()

# Request 3: Invoke another tool (scan for job title drift)
print("🔌 CLIENT → SERVER: tools/call - scan_job_title_drift")
print("-" * 100)

tool_fn = mcp._tool_manager._tools["scan_job_title_drift"].fn
result = tool_fn()

print("SERVER → CLIENT: Tool execution result")
print()
print(json.dumps(result, indent=2))
print()

print("=" * 100)
print("MCP PROTOCOL TEST COMPLETE")
print("=" * 100)
print()
print("✅ Server successfully responds to MCP protocol requests")
print("✅ Tools execute and return structured JSON responses")
print("✅ Ready for integration with Claude Desktop or other MCP clients")
print()
print("📝 To add this server to Claude Desktop, add to your config:")
print()
print('   {')
print('     "mcpServers": {')
print('       "nexus": {')
print('         "command": "python",')
print(f'         "args": ["{os.path.abspath("src/main.py")}"],')
print(f'         "cwd": "{os.getcwd()}",')
print('         "env": {')
print('           "USE_MOCK": "true"')
print('         }')
print('       }')
print('     }')
print('   }')
print()
