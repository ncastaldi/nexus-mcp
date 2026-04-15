from typing import Set

# Fields allowed to be returned to the MCP client
ALLOWED_USER_FIELDS: Set[str] = {
    "username",
    "display_name",
    "first_name",
    "last_name",
    "email",
    "enabled",
    "ou",
    "description",
    "last_logon_utc",
    "when_created_utc",
    "department",
    "title",
}


class IdentityBackend:
    """Base interface for Identity Shard backends."""
    pass