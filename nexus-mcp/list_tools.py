#!/usr/bin/env python3
"""Browse all available MCP tools in the Nexus server.

This shows the full tool catalog across all enabled shards.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from dotenv import load_dotenv
load_dotenv()

from mcp.server.fastmcp import FastMCP
from shards import identity, workday, itsm, assets, logistics, audit

# Initialize server
mcp = FastMCP(name="Nexus")

def _enabled(flag: str) -> bool:
    return os.getenv(f"ENABLE_{flag}", "true").strip().lower() == "true"

# Register shards
shard_map = {
    "IDENTITY": (identity, "🔐"),
    "WORKDAY": (workday, "👥"),
    "ITSM": (itsm, "🎫"),
    "ASSETS": (assets, "💻"),
    "LOGISTICS": (logistics, "📦"),
    "AUDIT": (audit, "🔍"),
}

print("=" * 100)
print("NEXUS MCP SERVER - COMPLETE TOOL CATALOG")
print("=" * 100)
print()

for flag, (shard, emoji) in shard_map.items():
    if _enabled(flag):
        before_count = len(mcp._tool_manager._tools)
        shard.register(mcp)
        after_count = len(mcp._tool_manager._tools)
        tools_added = after_count - before_count
        print(f"{emoji} {flag.lower()} shard: {tools_added} tools registered")

total_tools = len(mcp._tool_manager._tools)
print()
print(f"✅ Total: {total_tools} tools available")
print()

# Group tools by shard
print("=" * 100)
print("TOOLS BY SHARD")
print("=" * 100)
print()

# Categorize based on naming patterns
categories = {
    "🔍 Audit Tools (Cross-System Drift Detection)": [],
    "👥 Workday Tools": [],
    "🔐 Identity Tools (AD + Entra)": [],
    "🎫 ITSM Tools": [],
    "💻 Asset Tools": [],
    "📦 Logistics Tools": [],
    "🔒 Audit Log Tools": [],
}

for tool_name in sorted(mcp._tool_manager._tools.keys()):
    if tool_name.startswith("scan_"):
        categories["🔍 Audit Tools (Cross-System Drift Detection)"].append(tool_name)
    elif "workday" in tool_name.lower() or tool_name.startswith("get_worker"):
        categories["👥 Workday Tools"].append(tool_name)
    elif any(x in tool_name for x in ["ad_", "entra_", "user_", "group_"]):
        categories["🔐 Identity Tools (AD + Entra)"].append(tool_name)
    elif "incident" in tool_name or "ticket" in tool_name:
        categories["🎫 ITSM Tools"].append(tool_name)
    elif "asset" in tool_name or "device" in tool_name or "intune" in tool_name:
        categories["💻 Asset Tools"].append(tool_name)
    elif "fedex" in tool_name or "ship" in tool_name:
        categories["📦 Logistics Tools"].append(tool_name)
    elif "audit" in tool_name or "nexus_audit" in tool_name:
        categories["🔒 Audit Log Tools"].append(tool_name)
    else:
        # Add to most relevant category based on first match
        categories.get("🔍 Audit Tools (Cross-System Drift Detection)", []).append(tool_name)

for category, tools in categories.items():
    if tools:
        print(f"{category}")
        print("-" * 100)
        for i, tool_name in enumerate(tools, 1):
            tool = mcp._tool_manager._tools[tool_name]
            print(f"  {i}. {tool_name}")
            if tool.fn.__doc__:
                doc_lines = tool.fn.__doc__.strip().split('\n')
                summary = doc_lines[0].strip()
                if summary:
                    print(f"     → {summary}")
        print()

print("=" * 100)
print(f"✅ USE_MOCK={os.getenv('USE_MOCK', 'false')} - All tools run on synthetic data")
print("=" * 100)
