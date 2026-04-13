from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Literal

# Import AD adapter for backend selection
try:
    from ad_adapter import ActiveDirectoryIdentityBackend
except ImportError:
    ActiveDirectoryIdentityBackend = None  # type: ignore


# Type definitions for Phase 2 query contract
SortByField = Literal["display_name", "username", "last_logon_utc", "when_created_utc", "department"]
SortDirection = Literal["asc", "desc"]
GroupByField = Literal["enabled", "ou", "department", "title", "created_month", "last_logon_bucket"]

ALLOWED_USER_FIELDS = {
    "username",
    "display_name",
    "first_name",
    "last_name",
    "enabled",
    "ou",
    "description",
    "last_logon_utc",
    "when_created_utc",
    "department",
    "title",
    "email",
}


@dataclass
class UserRecord:
    username: str
    first_name: str
    last_name: str
    display_name: str
    enabled: bool
    ou: str
    description: str
    last_logon_utc: datetime
    groups: list[str]


@dataclass
class ComputerRecord:
    computer_name: str
    ou: str
    assigned_username: str | None


class IdentityBackend:
    """Backend interface for identity data providers.

    Replace this in-memory implementation with approved AD/Entra integrations.
    """

    async def get_user(self, username: str) -> dict[str, Any] | None:
        raise NotImplementedError

    async def search_users_by_name(
        self, name_query: str, limit: int = 20
    ) -> list[dict[str, Any]]:
        raise NotImplementedError

    async def get_user_groups(self, username: str) -> list[str]:
        raise NotImplementedError

    async def get_group_members(self, group_name: str) -> list[str]:
        raise NotImplementedError

    async def find_stale_users(self, days: int) -> list[dict[str, Any]]:
        raise NotImplementedError

    async def get_computer(self, computer_name: str) -> dict[str, Any] | None:
        raise NotImplementedError

    async def query_users(
        self,
        filter_params: dict[str, Any] | None = None,
        fields: list[str] | None = None,
        sort_by: str = "display_name",
        sort_direction: str = "asc",
        page_size: int = 50,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Query users with flexible validated filters and pagination.
        
        Returns:
            dict with keys: items, next_cursor, page_size, total_estimate, applied_filter, warnings
        """
        raise NotImplementedError

    async def count_users(
        self,
        filter_params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Count users matching filter without returning full records.
        
        Returns:
            dict with keys: count, applied_filter
        """
        raise NotImplementedError

    async def summarize_users(
        self,
        filter_params: dict[str, Any] | None = None,
        group_by: str = "enabled",
        top: int = 20,
    ) -> dict[str, Any]:
        """Return grouped aggregates for users matching filter.
        
        Returns:
            dict with keys: buckets, total, applied_filter
        """
        raise NotImplementedError


class InMemoryIdentityBackend(IdentityBackend):
    """Local-safe backend for initial MCP wiring and tool contract validation."""

    def __init__(self) -> None:
        now = datetime.now(tz=timezone.utc)
        self._users: dict[str, UserRecord] = {
            "jane.doe": UserRecord(
                username="jane.doe",
                first_name="Jane",
                last_name="Doe",
                display_name="Jane Doe",
                enabled=True,
                ou="OU=Users,DC=example,DC=local",
                description="Service Desk",
                last_logon_utc=now - timedelta(days=2),
                groups=["GG-Global-VPN", "GG-ServiceDesk"],
            ),
            "john.smith": UserRecord(
                username="john.smith",
                first_name="John",
                last_name="Smith",
                display_name="John Smith",
                enabled=False,
                ou="OU=DisabledUsers,DC=example,DC=local",
                description="Terminated 2026-02-20",
                last_logon_utc=now - timedelta(days=65),
                groups=["GG-FormerEmployees"],
            ),            "alice.tech": UserRecord(
                username="alice.tech",
                first_name="Alice",
                last_name="Tech",
                display_name="Alice Tech",
                enabled=True,
                ou="OU=IT,OU=Users,DC=example,DC=local",
                description="IT Infrastructure",
                last_logon_utc=now - timedelta(days=1),
                groups=["GG-IT-Infrastructure", "GG-Global-VPN"],
            ),
            "bob.sales": UserRecord(
                username="bob.sales",
                first_name="Bob",
                last_name="Sales",
                display_name="Bob Sales",
                enabled=False,
                ou="OU=DisabledUsers,DC=example,DC=local",
                description="Inactive 2025-12-01",
                last_logon_utc=now - timedelta(days=120),
                groups=["GG-Sales-Disabled"],
            ),        }
        self._computers: dict[str, ComputerRecord] = {
            "LT-1001": ComputerRecord(
                computer_name="LT-1001",
                ou="OU=Workstations,DC=example,DC=local",
                assigned_username="jane.doe",
            )
        }

    async def get_user(self, username: str) -> dict[str, Any] | None:
        user = self._users.get(username.lower())
        if user is None:
            return None
        return {
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "display_name": user.display_name,
            "enabled": user.enabled,
            "ou": user.ou,
            "description": user.description,
            "last_logon_utc": user.last_logon_utc.isoformat(),
        }

    async def search_users_by_name(
        self, name_query: str, limit: int = 20
    ) -> list[dict[str, Any]]:
        query = name_query.strip().lower()
        if not query:
            return []

        max_results = max(1, min(limit, 100))
        results: list[dict[str, Any]] = []
        for user in self._users.values():
            searchable = [user.first_name, user.last_name, user.display_name]
            if any(query in value.lower() for value in searchable):
                results.append(
                    {
                        "username": user.username,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "display_name": user.display_name,
                        "enabled": user.enabled,
                        "ou": user.ou,
                    }
                )

        results = sorted(results, key=lambda row: row["display_name"].lower())
        return results[:max_results]

    async def get_user_groups(self, username: str) -> list[str]:
        user = self._users.get(username.lower())
        if user is None:
            return []
        return list(user.groups)

    async def get_group_members(self, group_name: str) -> list[str]:
        wanted = group_name.lower()
        members: list[str] = []
        for user in self._users.values():
            if any(g.lower() == wanted for g in user.groups):
                members.append(user.username)
        return sorted(members)

    async def find_stale_users(self, days: int) -> list[dict[str, Any]]:
        if days < 0:
            return []
        cutoff = datetime.now(tz=timezone.utc) - timedelta(days=days)
        results: list[dict[str, Any]] = []
        for user in self._users.values():
            if user.last_logon_utc < cutoff:
                results.append(
                    {
                        "username": user.username,
                        "enabled": user.enabled,
                        "last_logon_utc": user.last_logon_utc.isoformat(),
                    }
                )
        return sorted(results, key=lambda row: row["username"])

    async def get_computer(self, computer_name: str) -> dict[str, Any] | None:
        computer = self._computers.get(computer_name.upper())
        if computer is None:
            return None
        return {
            "computer_name": computer.computer_name,
            "ou": computer.ou,
            "assigned_username": computer.assigned_username,
        }

    async def query_users(
        self,
        filter_params: dict[str, Any] | None = None,
        fields: list[str] | None = None,
        sort_by: str = "display_name",
        sort_direction: str = "asc",
        page_size: int = 50,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Query users with flexible validated filters and pagination."""
        filter_params = filter_params or {}
        fields = fields or list(ALLOWED_USER_FIELDS)
        
        # Validate fields
        invalid_fields = set(fields) - ALLOWED_USER_FIELDS
        if invalid_fields:
            return {
                "items": [],
                "next_cursor": None,
                "page_size": page_size,
                "total_estimate": 0,
                "applied_filter": filter_params,
                "warnings": [f"Invalid fields requested: {', '.join(invalid_fields)}"],
            }
        
        # Filter users
        matching_users: list[UserRecord] = []
        for user in self._users.values():
            if not self._user_matches_filter(user, filter_params):
                continue
            matching_users.append(user)
        
        # Sort
        sort_key_map = {
            "display_name": lambda u: u.display_name.lower(),
            "username": lambda u: u.username.lower(),
            "last_logon_utc": lambda u: u.last_logon_utc,
        }
        sort_func = sort_key_map.get(sort_by, lambda u: u.display_name.lower())
        matching_users = sorted(
            matching_users,
            key=sort_func,
            reverse=(sort_direction == "desc"),
        )
        
        # Paginate
        clamped_size = min(max(1, page_size), 200)
        start_index = 0
        if cursor:
            try:
                start_index = int(cursor)
            except ValueError:
                pass
        
        page_users = matching_users[start_index:start_index + clamped_size]
        next_cursor = None
        if start_index + clamped_size < len(matching_users):
            next_cursor = str(start_index + clamped_size)
        
        # Project fields
        items = []
        for user in page_users:
            item: dict[str, Any] = {}
            if "username" in fields:
                item["username"] = user.username
            if "display_name" in fields:
                item["display_name"] = user.display_name
            if "first_name" in fields:
                item["first_name"] = user.first_name
            if "last_name" in fields:
                item["last_name"] = user.last_name
            if "enabled" in fields:
                item["enabled"] = user.enabled
            if "ou" in fields:
                item["ou"] = user.ou
            if "description" in fields:
                item["description"] = user.description
            if "last_logon_utc" in fields:
                item["last_logon_utc"] = user.last_logon_utc.isoformat()
            if "department" in fields:
                item["department"] = ""
            if "title" in fields:
                item["title"] = ""
            if "email" in fields:
                item["email"] = f"{user.username}@example.local"
            if "when_created_utc" in fields:
                item["when_created_utc"] = ""
            items.append(item)
        
        return {
            "items": items,
            "next_cursor": next_cursor,
            "page_size": clamped_size,
            "total_estimate": len(matching_users),
            "applied_filter": filter_params,
            "warnings": [],
        }

    async def count_users(
        self,
        filter_params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Count users matching filter without returning full records."""
        filter_params = filter_params or {}
        
        count = 0
        for user in self._users.values():
            if self._user_matches_filter(user, filter_params):
                count += 1
        
        return {
            "count": count,
            "applied_filter": filter_params,
        }

    async def summarize_users(
        self,
        filter_params: dict[str, Any] | None = None,
        group_by: str = "enabled",
        top: int = 20,
    ) -> dict[str, Any]:
        """Return grouped aggregates for users matching filter."""
        filter_params = filter_params or {}
        
        # Filter users
        matching_users: list[UserRecord] = []
        for user in self._users.values():
            if self._user_matches_filter(user, filter_params):
                matching_users.append(user)
        
        # Group
        bucket_counts: dict[str, int] = {}
        for user in matching_users:
            key = self._get_group_key(user, group_by)
            bucket_counts[key] = bucket_counts.get(key, 0) + 1
        
        # Sort by count descending and take top N
        sorted_buckets = sorted(
            bucket_counts.items(),
            key=lambda x: x[1],
            reverse=True,
        )
        clamped_top = min(max(1, top), 50)
        top_buckets = sorted_buckets[:clamped_top]
        
        buckets = [{"key": key, "count": count} for key, count in top_buckets]
        
        return {
            "buckets": buckets,
            "total": len(matching_users),
            "applied_filter": filter_params,
        }

    def _user_matches_filter(self, user: UserRecord, filter_params: dict[str, Any]) -> bool:
        """Check if user matches all filter criteria."""
        if "enabled" in filter_params:
            if user.enabled != filter_params["enabled"]:
                return False
        
        if "name_contains" in filter_params:
            query = filter_params["name_contains"].lower()
            if query not in user.display_name.lower():
                return False
        
        if "username_prefix" in filter_params:
            prefix = filter_params["username_prefix"].lower()
            if not user.username.lower().startswith(prefix):
                return False
        
        if "ou_contains" in filter_params:
            ou_query = filter_params["ou_contains"].lower()
            if ou_query not in user.ou.lower():
                return False
        
        if "description_contains" in filter_params:
            desc_query = filter_params["description_contains"].lower()
            if desc_query not in user.description.lower():
                return False
        
        if "last_logon_before_days" in filter_params:
            days = filter_params["last_logon_before_days"]
            cutoff = datetime.now(tz=timezone.utc) - timedelta(days=days)
            if user.last_logon_utc >= cutoff:
                return False
        
        if "group_any" in filter_params:
            wanted_groups = {g.lower() for g in filter_params["group_any"]}
            user_groups = {g.lower() for g in user.groups}
            if not wanted_groups.intersection(user_groups):
                return False
        
        return True

    def _get_group_key(self, user: UserRecord, group_by: str) -> str:
        """Get grouping key for a user."""
        if group_by == "enabled":
            return "Enabled" if user.enabled else "Disabled"
        if group_by == "ou":
            return user.ou
        if group_by == "department":
            return "Unknown"
        if group_by == "title":
            return "Unknown"
        if group_by == "created_month":
            return "Unknown"
        if group_by == "last_logon_bucket":
            days_ago = (datetime.now(tz=timezone.utc) - user.last_logon_utc).days
            if days_ago < 7:
                return "Last 7 days"
            elif days_ago < 30:
                return "Last 30 days"
            elif days_ago < 90:
                return "Last 90 days"
            else:
                return "90+ days"
        return "Unknown"

