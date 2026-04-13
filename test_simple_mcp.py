#!/usr/bin/env python3
"""Minimal MCP server for testing VS Code Copilot integration.

This is a simplified version to help diagnose MCP server issues.
If this works, the problem is with the Nexus server configuration.
If this doesn't work, it's a VS Code/Copilot setup issue.
"""

from mcp.server.fastmcp import FastMCP

# Create minimal server
mcp = FastMCP(
    name="test-server",
    instructions="A minimal MCP server for testing VS Code integration"
)


@mcp.tool()
def hello(name: str = "World") -> str:
    """Say hello to someone.
    
    Args:
        name: The name to greet (default: World)
    
    Returns:
        A friendly greeting
    """
    return f"Hello, {name}! MCP server is working! 🎉"


@mcp.tool()
def test_connection() -> dict:
    """Test that the MCP connection is working.
    
    Returns:
        Status information about the server
    """
    return {
        "status": "connected",
        "server": "test-server",
        "message": "MCP server is responding correctly",
        "tools_available": 3
    }


@mcp.tool()
def check_environment() -> dict:
    """Check environment variables and paths.
    
    Returns:
        Environment information
    """
    import os
    import sys
    
    return {
        "python_version": sys.version,
        "python_executable": sys.executable,
        "current_directory": os.getcwd(),
        "use_mock": os.getenv("USE_MOCK", "not set"),
    }


def main():
    """Run the MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
