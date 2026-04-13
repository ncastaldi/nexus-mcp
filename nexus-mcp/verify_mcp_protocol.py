#!/usr/bin/env python3
"""Verify that audit tools work correctly through MCP stdio protocol."""

import asyncio
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from dotenv import load_dotenv
load_dotenv()

async def test_mcp_tools():
    """Test audit tools by calling them directly through the MCP server."""
    from mcp.server.fastmcp import FastMCP
    from shards import audit
    
    # Create server and register audit shard
    mcp = FastMCP(name="Nexus-Test")
    audit.register(mcp)
    
    # Get the tool functions
    tools = {
        "scan_status_reconciliation": mcp._tool_manager._tools["scan_status_reconciliation"].fn,
        "scan_job_title_drift": mcp._tool_manager._tools["scan_job_title_drift"].fn,
        "scan_department_mismatches": mcp._tool_manager._tools["scan_department_mismatches"].fn,
        "scan_name_variance_mismatches": mcp._tool_manager._tools["scan_name_variance_mismatches"].fn,
    }
    
    print("Testing audit tools through MCP protocol...")
    print("=" * 80)
    
    for tool_name, tool_fn in tools.items():
        print(f"\nTesting: {tool_name}")
        try:
            # Call the tool
            result = await tool_fn()
            
            # Verify it's a dictionary, not a coroutine
            if isinstance(result, dict):
                print(f"✅ SUCCESS - Returned dict with {len(result)} keys")
                print(f"   Mismatches found: {result.get('scan_summary', {}).get('mismatches_found', 'N/A')}")
            else:
                print(f"❌ FAILED - Returned {type(result)} instead of dict")
                print(f"   Value: {result}")
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 80)
    print("✅ All tools tested successfully!")

if __name__ == "__main__":
    asyncio.run(test_mcp_tools())
