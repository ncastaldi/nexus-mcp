from __future__ import annotations

import logging
import os
import sys
from typing import Any

from mcp.server.fastmcp import FastMCP

from identity_backend import IdentityBackend, InMemoryIdentityBackend

mcp = FastMCP("identity")

# Backend selection via environment variable
# Set IDENTITY_BACKEND=ad to use Active Directory adapter
# Set AD_USERNAME and AD_PASSWORD for explicit credentials (test only)
backend_type = os.getenv("IDENTITY_BACKEND", "memory").lower()

if backend_type == "ad":
    from ad_adapter import ActiveDirectoryIdentityBackend
    
    ad_username = os.getenv("AD_USERNAME")
    ad_password = os.getenv("AD_PASSWORD")
    timeout = float(os.getenv("AD_TIMEOUT", "30.0"))
    
    backend: IdentityBackend = ActiveDirectoryIdentityBackend(
        username=ad_username,
        password=ad_password,
        timeout_seconds=timeout,
    )
    logging.getLogger("identity-mcp").info(
        "Using Active Directory backend with %s",
        "explicit credentials" if ad_username else "process context",
    )
else:
    backend: IdentityBackend = InMemoryIdentityBackend()
    logging.getLogger("identity-mcp").info("Using in-memory backend (safe mode)")

# STDIO MCP servers must avoid stdout logging to prevent JSON-RPC corruption.
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("identity-mcp")


def _audit(tool: str, params: dict[str, Any], result: Any) -> None:
    result_type = type(result).__name__
    if isinstance(result, list):
        result_size = len(result)
    elif isinstance(result, dict):
        result_size = len(result.keys())
    else:
        result_size = 0
    logger.info(
        "tool=%s params=%s result_type=%s result_size=%s",
        tool,
        params,
        result_type,
        result_size,
    )


@mcp.tool()
async def get_user(username: str) -> dict[str, Any] | str:
    """Get user state for a username.

    Returns enabled/disabled, OU, description, and last logon.
    """
    result = await backend.get_user(username)
    if result is None:
        message = "User not found."
        _audit("get_user", {"username": username}, message)
        return message
    _audit("get_user", {"username": username}, result)
    return result


@mcp.tool()
async def search_users_by_name(name_query: str, limit: int = 20) -> list[dict[str, Any]] | str:
    """Search users by first name, last name, or full display name."""
    if not name_query.strip():
        message = "name_query must not be empty"
        _audit(
            "search_users_by_name",
            {"name_query": name_query, "limit": limit},
            message,
        )
        return message

    if limit < 1:
        message = "limit must be >= 1"
        _audit(
            "search_users_by_name",
            {"name_query": name_query, "limit": limit},
            message,
        )
        return message

    clamped_limit = min(limit, 100)
    result = await backend.search_users_by_name(name_query=name_query, limit=clamped_limit)
    _audit(
        "search_users_by_name",
        {"name_query": name_query, "limit": clamped_limit},
        result,
    )
    return result


@mcp.tool()
async def get_user_groups(username: str) -> list[str]:
    """Get all group memberships for a user."""
    result = await backend.get_user_groups(username)
    _audit("get_user_groups", {"username": username}, result)
    return result


@mcp.tool()
async def get_group_members(group_name: str) -> list[str]:
    """Get all members of a named group."""
    result = await backend.get_group_members(group_name)
    _audit("get_group_members", {"group_name": group_name}, result)
    return result


@mcp.tool()
async def find_stale_users(days: int) -> list[dict[str, Any]] | str:
    """Get users with no logon activity in N days."""
    if days < 0:
        message = "days must be >= 0"
        _audit("find_stale_users", {"days": days}, message)
        return message
    result = await backend.find_stale_users(days)
    _audit("find_stale_users", {"days": days}, result)
    return result


@mcp.tool()
async def get_computer(computer_name: str) -> dict[str, Any] | str:
    """Get computer account details including OU placement."""
    result = await backend.get_computer(computer_name)
    if result is None:
        message = "Computer not found."
        _audit("get_computer", {"computer_name": computer_name}, message)
        return message
    _audit("get_computer", {"computer_name": computer_name}, result)
    return result


@mcp.tool()
async def query_users(
    enabled: bool | None = None,
    name_contains: str | None = None,
    username_prefix: str | None = None,
    ou_contains: str | None = None,
    group_any: list[str] | None = None,
    description_contains: str | None = None,
    last_logon_before_days: int | None = None,
    fields: list[str] | None = None,
    sort_by: str = "display_name",
    sort_direction: str = "asc",
    page_size: int = 50,
    cursor: str | None = None,
) -> dict[str, Any]:
    """Query users with flexible validated filters for casual userbase exploration.
    
    Use this for questions like:
    - "Show me all disabled users"
    - "Find users in the ServiceDesk OU"
    - "Which users haven't logged in for 90 days?"
    - "List users with VPN access"
    
    Args:
        enabled: Filter by account enabled/disabled state
        name_contains: Search display names containing this string (min 2 chars)
        username_prefix: Filter usernames starting with this prefix (min 1 char)
        ou_contains: Filter by OU path containing this string (min 2 chars)
        group_any: List of groups - match users in ANY of these groups (1-10 groups)
        description_contains: Search descriptions containing this string (min 2 chars)
        last_logon_before_days: Filter users who last logged in more than N days ago (0-3650)
        fields: List of fields to return (default: all allowed fields)
        sort_by: Field to sort by (display_name, username, last_logon_utc, when_created_utc, department)
        sort_direction: Sort direction (asc or desc)
        page_size: Results per page (1-200, default 50)
        cursor: Pagination cursor from previous response
    
    Returns:
        dict with items, next_cursor, page_size, total_estimate, applied_filter, warnings
    """
    # Build filter params from provided arguments
    filter_params: dict[str, Any] = {}
    
    if enabled is not None:
        filter_params["enabled"] = enabled
    
    if name_contains is not None:
        if len(name_contains.strip()) < 2:
            return {
                "items": [],
                "next_cursor": None,
                "page_size": page_size,
                "total_estimate": 0,
                "applied_filter": {},
                "warnings": ["name_contains must be at least 2 characters"],
            }
        filter_params["name_contains"] = name_contains.strip()
    
    if username_prefix is not None:
        if len(username_prefix.strip()) < 1:
            return {
                "items": [],
                "next_cursor": None,
                "page_size": page_size,
                "total_estimate": 0,
                "applied_filter": {},
                "warnings": ["username_prefix must be at least 1 character"],
            }
        filter_params["username_prefix"] = username_prefix.strip()
    
    if ou_contains is not None:
        if len(ou_contains.strip()) < 2:
            return {
                "items": [],
                "next_cursor": None,
                "page_size": page_size,
                "total_estimate": 0,
                "applied_filter": {},
                "warnings": ["ou_contains must be at least 2 characters"],
            }
        filter_params["ou_contains"] = ou_contains.strip()
    
    if group_any is not None:
        if not isinstance(group_any, list) or len(group_any) < 1 or len (group_any) > 10:
            return {
                "items": [],
                "next_cursor": None,
                "page_size": page_size,
                "total_estimate": 0,
                "applied_filter": {},
                "warnings": ["group_any must be a list of 1-10 group names"],
            }
        filter_params["group_any"] = group_any
    
    if description_contains is not None:
        if len(description_contains.strip()) < 2:
            return {
                "items": [],
                "next_cursor": None,
                "page_size": page_size,
                "total_estimate": 0,
                "applied_filter": {},
                "warnings": ["description_contains must be at least 2 characters"],
            }
        filter_params["description_contains"] = description_contains.strip()
    
    if last_logon_before_days is not None:
        if last_logon_before_days < 0 or last_logon_before_days > 3650:
            return {
                "items": [],
                "next_cursor": None,
                "page_size": page_size,
                "total_estimate": 0,
                "applied_filter": {},
                "warnings": ["last_logon_before_days must be between 0 and 3650"],
            }
        filter_params["last_logon_before_days"] = last_logon_before_days
    
    # Validate sort options
    valid_sort_by = ["display_name", "username", "last_logon_utc", "when_created_utc", "department"]
    if sort_by not in valid_sort_by:
        return {
            "items": [],
            "next_cursor": None,
            "page_size": page_size,
            "total_estimate": 0,
            "applied_filter": filter_params,
            "warnings": [f"Invalid sort_by. Must be one of: {', '.join(valid_sort_by)}"],
        }
    
    if sort_direction not in ["asc", "desc"]:
        return {
            "items": [],
            "next_cursor": None,
            "page_size": page_size,
            "total_estimate": 0,
            "applied_filter": filter_params,
            "warnings": ["sort_direction must be 'asc' or 'desc'"],
        }
    
    result = await backend.query_users(
        filter_params=filter_params,
        fields=fields,
        sort_by=sort_by,
        sort_direction=sort_direction,
        page_size=page_size,
        cursor=cursor,
    )
    
    _audit("query_users", {"filter": filter_params, "page_size": page_size}, result)
    return result


@mcp.tool()
async def count_users(
    enabled: bool | None = None,
    name_contains: str | None = None,
    username_prefix: str | None = None,
    ou_contains: str | None = None,
    group_any: list[str] | None = None,
    description_contains: str | None = None,
    last_logon_before_days: int | None = None,
) -> dict[str, Any]:
    """Count users matching filter criteria without returning full records.
    
    Use this for quick sizing questions like:
    - "How many disabled users are there?"
    - "How many users are in the IT department OU?"
    - "How many users haven't logged in for 90 days?"
    
    Args:
        enabled: Filter by account enabled/disabled state
        name_contains: Search display names containing this string (min 2 chars)
        username_prefix: Filter usernames starting with this prefix (min 1 char)
        ou_contains: Filter by OU path containing this string (min 2 chars)
        group_any: List of groups - match users in ANY of these groups (1-10 groups)
        description_contains: Search descriptions containing this string (min 2 chars)
        last_logon_before_days: Filter users who last logged in more than N days ago (0-3650)
    
    Returns:
        dict with count and applied_filter
    """
    # Build filter params (same validation as query_users)
    filter_params: dict[str, Any] = {}
    warnings: list[str] = []
    
    if enabled is not None:
        filter_params["enabled"] = enabled
    
    if name_contains is not None:
        if len(name_contains.strip()) < 2:
            warnings.append("name_contains must be at least 2 characters")
        else:
            filter_params["name_contains"] = name_contains.strip()
    
    if username_prefix is not None:
        if len(username_prefix.strip()) < 1:
            warnings.append("username_prefix must be at least 1 character")
        else:
            filter_params["username_prefix"] = username_prefix.strip()
    
    if ou_contains is not None:
        if len(ou_contains.strip()) < 2:
            warnings.append("ou_contains must be at least 2 characters")
        else:
            filter_params["ou_contains"] = ou_contains.strip()
    
    if group_any is not None:
        if not isinstance(group_any, list) or len(group_any) < 1 or len(group_any) > 10:
            warnings.append("group_any must be a list of 1-10 group names")
        else:
            filter_params["group_any"] = group_any
    
    if description_contains is not None:
        if len(description_contains.strip()) < 2:
            warnings.append("description_contains must be at least 2 characters")
        else:
            filter_params["description_contains"] = description_contains.strip()
    
    if last_logon_before_days is not None:
        if last_logon_before_days < 0 or last_logon_before_days > 3650:
            warnings.append("last_logon_before_days must be between 0 and 3650")
        else:
            filter_params["last_logon_before_days"] = last_logon_before_days
    
    if warnings:
        result = {
            "count": 0,
            "applied_filter": filter_params,
            "warnings": warnings,
        }
        _audit("count_users", {"filter": filter_params}, result)
        return result
    
    result = await backend.count_users(filter_params=filter_params)
    _audit("count_users", {"filter": filter_params}, result)
    return result


@mcp.tool()
async def summarize_users(
    group_by: str = "enabled",
    top: int = 20,
    enabled: bool | None = None,
    name_contains: str | None = None,
    username_prefix: str | None = None,
    ou_contains: str | None = None,
    group_any: list[str] | None = None,
    description_contains: str | None = None,
    last_logon_before_days: int | None = None,
) -> dict[str, Any]:
    """Return grouped aggregates for users matching filter criteria.
    
    Use this for leadership-style questions like:
    - "Which departments have the most stale users?"
    - "Show me user distribution by OU"
    - "How many users per enabled/disabled status?"
    - "What's the breakdown of users by last logon activity?"
    
    Args:
        group_by: Field to group by (enabled, ou, department, title, created_month, last_logon_bucket)
        top: Maximum number of buckets to return (1-50, default 20)
        enabled: Filter by account enabled/disabled state
        name_contains: Search display names containing this string (min 2 chars)
        username_prefix: Filter usernames starting with this prefix (min 1 char)
        ou_contains: Filter by OU path containing this string (min 2 chars)
        group_any: List of groups - match users in ANY of these groups (1-10 groups)
        description_contains: Search descriptions containing this string (min 2 chars)
        last_logon_before_days: Filter users who last logged in more than N days ago (0-3650)
    
    Returns:
        dict with buckets (array of {key, count}), total, and applied_filter
    """
    # Validate group_by
    valid_group_by = ["enabled", "ou", "department", "title", "created_month", "last_logon_bucket"]
    if group_by not in valid_group_by:
        return {
            "buckets": [],
            "total": 0,
            "applied_filter": {},
            "warnings": [f"Invalid group_by. Must be one of: {', '.join(valid_group_by)}"],
        }
    
    # Validate top
    if top < 1 or top > 50:
        return {
            "buckets": [],
            "total": 0,
            "applied_filter": {},
            "warnings": ["top must be between 1 and 50"],
        }
    
    # Build filter params (same validation as query_users)
    filter_params: dict[str, Any] = {}
    warnings: list[str] = []
    
    if enabled is not None:
        filter_params["enabled"] = enabled
    
    if name_contains is not None:
        if len(name_contains.strip()) < 2:
            warnings.append("name_contains must be at least 2 characters")
        else:
            filter_params["name_contains"] = name_contains.strip()
    
    if username_prefix is not None:
        if len(username_prefix.strip()) < 1:
            warnings.append("username_prefix must be at least 1 character")
        else:
            filter_params["username_prefix"] = username_prefix.strip()
    
    if ou_contains is not None:
        if len(ou_contains.strip()) < 2:
            warnings.append("ou_contains must be at least 2 characters")
        else:
            filter_params["ou_contains"] = ou_contains.strip()
    
    if group_any is not None:
        if not isinstance(group_any, list) or len(group_any) < 1 or len(group_any) > 10:
            warnings.append("group_any must be a list of 1-10 group names")
        else:
            filter_params["group_any"] = group_any
    
    if description_contains is not None:
        if len(description_contains.strip()) < 2:
            warnings.append("description_contains must be at least 2 characters")
        else:
            filter_params["description_contains"] = description_contains.strip()
    
    if last_logon_before_days is not None:
        if last_logon_before_days < 0 or last_logon_before_days > 3650:
            warnings.append("last_logon_before_days must be between 0 and 3650")
        else:
            filter_params["last_logon_before_days"] = last_logon_before_days
    
    if warnings:
        result = {
            "buckets": [],
            "total": 0,
            "applied_filter": filter_params,
            "warnings": warnings,
        }
        _audit("summarize_users", {"filter": filter_params, "group_by": group_by}, result)
        return result
    
    result = await backend.summarize_users(
        filter_params=filter_params,
        group_by=group_by,
        top=top,
    )
    _audit("summarize_users", {"filter": filter_params, "group_by": group_by}, result)
    return result


def main() -> None:
    """Run MCP server with transport determined by environment variable.
    
    Environment variables:
    - MCP_TRANSPORT: "stdio" (default) or "streamable" for HTTP
    - MCP_HOST: Host to bind to (default: 0.0.0.0 for streamable)
    - MCP_PORT: Port to bind to (default: 8000 for streamable)
    """
    transport = os.getenv("MCP_TRANSPORT", "stdio").lower()
    
    if transport == "streamable":
        # Streamable HTTP transport for Copilot Studio integration
        host = os.getenv("MCP_HOST", "0.0.0.0")
        port = int(os.getenv("MCP_PORT", "8000"))
        logger.info(
            "Starting Identity MCP server with streamable HTTP transport on %s:%d",
            host,
            port,
        )
        # Note: FastMCP with streamable transport requires mcp[server] extras
        # Install with: pip install "mcp[server]" or uv pip install "mcp[server]"
        mcp.run(transport="streamable", host=host, port=port)
    else:
        # STDIO transport for local testing and VS Code integration
        logger.info("Starting Identity MCP server with stdio transport")
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
