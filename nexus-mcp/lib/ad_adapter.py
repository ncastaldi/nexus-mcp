# Rule:
# ad_adapter.py outputs normalized snake_case fields
# All adapters (ADUserAdapter, EntraUserAdapter, etc.) consume that contract

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

logger = logging.getLogger("identity-mcp.ad-adapter")


class ActiveDirectoryIdentityBackend:
    """PowerShell-based Active Directory backend for read-only identity queries.

    Uses subprocess calls to approved Get-AD* cmdlets with deterministic output
    parsing. All methods maintain the same async contract and return shapes as
    IdentityBackend interface.
    """

    def __init__(
        self,
        username: str | None = None,
        password: str | None = None,
        timeout_seconds: float = 30.0,
    ) -> None:
        """Initialize AD adapter with optional explicit credentials for testing.

        Args:
            username: Optional explicit username for test environments only
            password: Optional explicit password for test environments only
            timeout_seconds: Per-query timeout limit
        """
        self.username = username
        self.password = password
        self.timeout = timeout_seconds

    @staticmethod
    def _escape_ps_single_quoted(value: str) -> str:
        return value.replace("'", "''")

    async def _run_powershell(
        self, command: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Execute PowerShell command and return parsed output or error.

        Args:
            command: PowerShell command string
            params: Optional parameters for logging context

        Returns:
            dict with "success" (bool), "data" (Any), "error" (str | None)
        """
        # Build credential block if explicit auth is configured
        cred_block = ""
        if self.username and self.password:
            # Escape single quotes in password for PowerShell
            escaped_password = self.password.replace("'", "''")
            # Use single quotes to avoid variable expansion and special char issues
            cred_block = f"$secpass = ConvertTo-SecureString '{escaped_password}' -AsPlainText -Force; $cred = New-Object System.Management.Automation.PSCredential('{self.username}', $secpass); "

        full_command = cred_block + command

        try:
            # Use create_subprocess_exec to avoid shell $ interpretation
            process = await asyncio.create_subprocess_exec(
                'powershell',
                '-NoProfile',
                '-NonInteractive',
                '-Command',
                full_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=self.timeout
            )

            stdout_text = stdout.decode("utf-8", errors="replace").strip()
            stderr_text = stderr.decode("utf-8", errors="replace").strip()

            if process.returncode != 0:
                logger.warning(
                    "PowerShell command failed: returncode=%d stderr=%s",
                    process.returncode,
                    stderr_text,
                )
                return {
                    "success": False,
                    "data": None,
                    "error": f"Command failed: {stderr_text[:200]}",
                }

            if stderr_text:
                logger.debug("PowerShell stderr: %s", stderr_text)

            return {"success": True, "data": stdout_text, "error": None}

        except asyncio.TimeoutError:
            logger.error("PowerShell command timeout after %s seconds", self.timeout)
            return {
                "success": False,
                "data": None,
                "error": f"Query timeout after {self.timeout} seconds",
            }
        except Exception as e:
            logger.error("PowerShell execution error: %s", str(e))
            return {
                "success": False,
                "data": None,
                "error": f"Execution error: {str(e)[:200]}",
            }

    async def get_user(self, username: str) -> dict[str, Any] | None:
        """Get user state for a username.

        Returns enabled/disabled, OU, description, and last logon timestamp.
        """
        # Build PowerShell command using JSON output for reliable parsing
        escaped_username = self._escape_ps_single_quoted(username)
        command = f"""
        $user = Get-ADUser -Filter "samAccountName -eq '{escaped_username}'" -Properties displayName,mail,givenName,sn,Enabled,DistinguishedName,Description,lastLogonTimestamp -ErrorAction Stop
        if ($user) {{
            $lastLogon = if ($user.lastLogonTimestamp) {{ [DateTime]::FromFileTime($user.lastLogonTimestamp).ToUniversalTime().ToString('o') }} else {{ $null }}
            @{{
                username = $user.SamAccountName
                display_name = if ($user.displayName) {{$user.displayName}} else {{$user.Name}}
                first_name = if ($user.givenName) {{$user.givenName}} else {{''}}
                last_name = if ($user.sn) {{$user.sn}} else {{''}}
                email = if ($user.mail) {{$user.mail}} else {{''}}
                enabled = $user.Enabled
                ou = $user.DistinguishedName
                description = if ($user.Description) {{$user.Description}} else {{''}}
                last_logon_utc = $lastLogon
            }} | ConvertTo-Json -Compress
        }}
        """

        result = await self._run_powershell(command, {"username": username})

        if not result["success"]:
            logger.warning(
                "get_user failed for username=%s: %s", username, result["error"]
            )
            return None

        if not result["data"]:
            return None

        try:
            user_data = json.loads(result["data"])
            return {
                "username": user_data["username"],
                "first_name": user_data.get("first_name", "") or "",
                "last_name": user_data.get("last_name", "") or "",
                "display_name": user_data.get("display_name", "") or "",
                "email": user_data.get("email", "") or "",
                "enabled": user_data["enabled"],
                "ou": user_data["ou"],
                "description": user_data["description"] or "",
                "last_logon_utc": user_data["last_logon_utc"] or "",
            }
        except (json.JSONDecodeError, KeyError) as e:
            logger.error("Failed to parse user data: %s", str(e))
            return None

    async def search_users_by_name(
        self, name_query: str, limit: int = 20
    ) -> list[dict[str, Any]]:
        """Search users by first name, last name, or full display name."""
        query = name_query.strip()
        if not query:
            return []

        max_results = max(1, min(limit, 100))
        escaped_query = self._escape_ps_single_quoted(query)
        command = f"""
        $query = '{escaped_query}'
        $tokens = @($query.Split(' ', [System.StringSplitOptions]::RemoveEmptyEntries))
        if ($tokens.Count -ge 2) {{
            $first = $tokens[0]
            $last = $tokens[1]
            $adFilter = "(givenName -like '$($first)*' -and sn -like '$($last)*') -or (displayName -like '$query*')"
        }} else {{
            $adFilter = "givenName -like '$query*' -or sn -like '$query*' -or displayName -like '$query*'"
        }}

        $users = @(Get-ADUser -Filter $adFilter -Properties displayName,mail,givenName,sn,Enabled,DistinguishedName -ErrorAction Stop |
            ForEach-Object {{
                @{{
                    username = $_.SamAccountName
                    display_name = if ($_.displayName) {{ $_.displayName }} else {{ $_.Name }}
                    first_name = if ($_.givenName) {{ $_.givenName }} else {{ '' }}
                    last_name = if ($_.sn) {{ $_.sn }} else {{ '' }}
                    email = if ($_.mail) {{ $_.mail }} else {{ '' }}
                    enabled = $_.Enabled
                    ou = $_.DistinguishedName
                }}
            }} | Select-Object -First {max_results})

        $users | ConvertTo-Json -Compress
        """


        result = await self._run_powershell(
            command,
            {"name_query": name_query, "limit": max_results},
        )

        if not result["success"]:
            logger.warning(
                "search_users_by_name failed for query=%s: %s",
                name_query,
                result["error"],
            )
            return []

        if not result["data"]:
            return []

        try:
            users = json.loads(result["data"])
            if isinstance(users, dict):
                users = [users]
            if not isinstance(users, list):
                return []

            normalized: list[dict[str, Any]] = []
            for user in users:
                if not isinstance(user, dict):
                    continue
                normalized.append(
                    {
                        "username": user.get("username", "") or "",
                        "first_name": user.get("first_name", "") or "",
                        "last_name": user.get("last_name", "") or "",
                        "display_name": user.get("display_name", "") or "",
                        "email": user.get("email", "") or "",
                        "enabled": bool(user.get("enabled", False)),
                        "ou": user.get("ou", "") or "",
                    }
                )
            return normalized
        except json.JSONDecodeError as e:
            logger.error("Failed to parse search user data: %s", str(e))
            return []

    async def get_user_groups(self, username: str) -> list[str]:
        """Get all group memberships for a user."""
        escaped_username = self._escape_ps_single_quoted(username)
        command = f"""
            $user = Get-ADUser -Filter "samAccountName -eq '{escaped_username}'" -Properties MemberOf -ErrorAction Stop
            if ($user -and $user.MemberOf) {{
                $groups = @($user.MemberOf | ForEach-Object {{
                    $group = Get-ADGroup $_ -ErrorAction SilentlyContinue
                    if ($group) {{ $group.Name }}
                }})
                $groups | ConvertTo-Json -Compress
            }} else {{
                @() | ConvertTo-Json -Compress
            }}
        """

        result = await self._run_powershell(command, {"username": username})

        if not result["success"]:
            logger.warning(
                "get_user_groups failed for username=%s: %s",
                username,
                result["error"],
            )
            return []

        if not result["data"]:
            return []

        try:
            groups = json.loads(result["data"])
            return sorted(groups) if isinstance(groups, list) else []
        except json.JSONDecodeError as e:
            logger.error("Failed to parse group data: %s", str(e))
            return []

    async def get_group_members(self, group_name: str) -> list[str]:
        """Get all members of a named group."""
        escaped_group_name = self._escape_ps_single_quoted(group_name)
        command = f"""
            $group = Get-ADGroup -Filter "Name -eq '{escaped_group_name}'" -ErrorAction Stop
            if ($group) {{
                $members = @(Get-ADGroupMember $group -ErrorAction Stop | Where-Object {{ $_.objectClass -eq 'user' }} | ForEach-Object {{ $_.SamAccountName }})
                $members | ConvertTo-Json -Compress
            }} else {{
                @() | ConvertTo-Json -Compress
            }}
        """

        result = await self._run_powershell(command, {"group_name": group_name})

        if not result["success"]:
            logger.warning(
                "get_group_members failed for group=%s: %s",
                group_name,
                result["error"],
            )
            return []

        if not result["data"]:
            return []

        try:
            members = json.loads(result["data"])
            return sorted(members) if isinstance(members, list) else []
        except json.JSONDecodeError as e:
            logger.error("Failed to parse member data: %s", str(e))
            return []

    async def find_stale_users(self, days: int) -> list[dict[str, Any]]:
        """Get users with no logon activity in N days using lastLogonTimestamp."""
        if days < 0:
            return []

        command = f"""
            $cutoff = (Get-Date).AddDays(-{days})
            $cutoffFileTime = $cutoff.ToFileTime()
            $users = @(Get-ADUser -Filter * -Properties Enabled,lastLogonTimestamp -ErrorAction Stop | Where-Object {{
                (-not $_.lastLogonTimestamp) -or ($_.lastLogonTimestamp -lt $cutoffFileTime)
            }} | Select-Object -First 100 | ForEach-Object {{
                $lastLogon = if ($_.lastLogonTimestamp) {{ [DateTime]::FromFileTime($_.lastLogonTimestamp).ToUniversalTime().ToString('o') }} else {{ '' }}
                @{{
                    username = $_.SamAccountName
                    enabled = $_.Enabled
                    last_logon_utc = $lastLogon
                }}
            }})
            $users | ConvertTo-Json -Compress
        """

        result = await self._run_powershell(command, {"days": days})

        if not result["success"]:
            logger.warning("find_stale_users failed: %s", result["error"])
            return []

        if not result["data"]:
            return []

        try:
            users = json.loads(result["data"])
            if not isinstance(users, list):
                users = [users] if users else []
            return sorted(users, key=lambda u: u.get("username", ""))
        except json.JSONDecodeError as e:
            logger.error("Failed to parse stale user data: %s", str(e))
            return []

    async def get_computer(self, computer_name: str) -> dict[str, Any] | None:
        """Get computer account details including OU placement.

        Note: assigned_username returns null in this phase per requirements.
        """
        escaped_computer_name = self._escape_ps_single_quoted(computer_name)
        command = f"""
            $computer = Get-ADComputer -Filter "Name -eq '{escaped_computer_name}'" -Properties DistinguishedName -ErrorAction Stop
            if ($computer) {{
                @{{
                    computer_name = $computer.Name
                    ou = $computer.DistinguishedName
                    assigned_username = $null
                }} | ConvertTo-Json -Compress
            }}
        """

        result = await self._run_powershell(command, {"computer_name": computer_name})

        if not result["success"]:
            logger.warning(
                "get_computer failed for computer=%s: %s",
                computer_name,
                result["error"],
            )
            return None

        if not result["data"]:
            return None

        try:
            computer_data = json.loads(result["data"])
            return {
                "computer_name": computer_data["computer_name"],
                "ou": computer_data["ou"],
                "assigned_username": None,
            }
        except (json.JSONDecodeError, KeyError) as e:
            logger.error("Failed to parse computer data: %s", str(e))
            return None

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
        from identity_backend import ALLOWED_USER_FIELDS
        
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
        
        # Build AD filter from filter_params
        ad_filter_parts = []
        
        if "enabled" in filter_params:
            enabled_val = "True" if filter_params["enabled"] else "False"
            ad_filter_parts.append(f"Enabled -eq ${enabled_val}")
        
        if "name_contains" in filter_params:
            name_query = self._escape_ps_single_quoted(filter_params["name_contains"])
            ad_filter_parts.append(f"DisplayName -like '*{name_query}*'")
        
        if "username_prefix" in filter_params:
            prefix = self._escape_ps_single_quoted(filter_params["username_prefix"])
            ad_filter_parts.append(f"samAccountName -like '{prefix}*'")
        
        if "ou_contains" in filter_params:
            ou_part = self._escape_ps_single_quoted(filter_params["ou_contains"])
            ad_filter_parts.append(f"DistinguishedName -like '*{ou_part}*'")
        
        if "description_contains" in filter_params:
            desc_part = self._escape_ps_single_quoted(filter_params["description_contains"])
            ad_filter_parts.append(f"Description -like '*{desc_part}*'")
        
        # Build final filter - default to all users if no filters specified
        if ad_filter_parts:
            ad_filter = " -and ".join(ad_filter_parts)
        else:
            ad_filter = "*"
        
        # Determine which AD properties to fetch
        ad_properties = [
            "SamAccountName",
            "GivenName",
            "Surname",
            "DisplayName",
            "Enabled",
            "DistinguishedName",
            "Description",
            "lastLogonTimestamp",
        ]
        if "when_created_utc" in fields:
            ad_properties.append("whenCreated")
        if "department" in fields:
            ad_properties.append("Department")
        if "title" in fields:
            ad_properties.append("Title")
        if "email" in fields:
            ad_properties.append("EmailAddress")
        
        # Build sort expression
        sort_field_map = {
            "display_name": "DisplayName",
            "username": "SamAccountName",
            "last_logon_utc": "lastLogonTimestamp",
            "when_created_utc": "whenCreated",
            "department": "Department",
        }
        sort_field = sort_field_map.get(sort_by, "DisplayName")
        
        # Clamp page size
        clamped_size = min(max(1, page_size), 200)
        
        # Note: Simple offset-based pagination for Phase 2
        # For production, consider lastLogonTimestamp-based keyset pagination
        start_index = 0
        if cursor:
            try:
                start_index = int(cursor)
            except ValueError:
                pass
        
        # Build PowerShell command
        props_csv = ", ".join(ad_properties)
        command = f"""
            $filter = "{ad_filter}"
            $users = Get-ADUser -Filter $filter -Properties {props_csv} -ErrorAction Stop | Sort-Object {sort_field}"""
        
        if sort_direction == "desc":
            command += " -Descending"
        
        command += "\n"
        
        # Handle last_logon_before_days post-filter (requires FileTime comparison)
        if "last_logon_before_days" in filter_params:
            days = filter_params["last_logon_before_days"]
            command += f"$users = $users | Where-Object {{ if ($_.lastLogonTimestamp) {{ $cutoff = (Get-Date).AddDays(-{days}).ToFileTime(); $_.lastLogonTimestamp -lt $cutoff }} else {{ $true }} }}\n"
        
        # Handle group_any post-filter
        if "group_any" in filter_params:
            groups_json = json.dumps(filter_params["group_any"])
            escaped_groups_json = groups_json.replace("'", "''")
            command += f"$users = $users | Where-Object {{ $targetGroups = '{escaped_groups_json}' | ConvertFrom-Json; $userGroups = @($_.MemberOf | ForEach-Object {{ $g = Get-ADGroup $_ -ErrorAction SilentlyContinue; if ($g) {{ $g.Name }} }}); $found = $false; foreach ($tg in $targetGroups) {{ if ($userGroups -contains $tg) {{ $found = $true; break }} }}; $found }}\n"
        
        # Add pagination and field projection
        command += f"""
            $users = @($users)
            $total = $users.Count
            $pageUsers = $users | Select-Object -Skip {start_index} -First {clamped_size}
            $hasMore = ($total -gt {start_index + clamped_size})
            
            $items = @($pageUsers | ForEach-Object {{
                $lastLogon = if ($_.lastLogonTimestamp) {{ 
                    [DateTime]::FromFileTime($_.lastLogonTimestamp).ToUniversalTime().ToString('o') 
                }} else {{ '' }}
                $whenCreated = if ($_.whenCreated) {{
                    $_.whenCreated.ToUniversalTime().ToString('o')
                }} else {{ '' }}
                
                @{{
                    username = $_.SamAccountName
                    display_name = if ($_.DisplayName) {{ $_.DisplayName }} else {{ '' }}
                    first_name = if ($_.GivenName) {{ $_.GivenName }} else {{ '' }}
                    last_name = if ($_.Surname) {{ $_.Surname }} else {{ '' }}
                    enabled = $_.Enabled
                    ou = $_.DistinguishedName
                    description = if ($_.Description) {{ $_.Description }} else {{ '' }}
                    last_logon_utc = $lastLogon
                    when_created_utc = $whenCreated
                    department = if ($_.Department) {{ $_.Department }} else {{ '' }}
                    title = if ($_.Title) {{ $_.Title }} else {{ '' }}
                    email = if ($_.EmailAddress) {{ $_.EmailAddress }} else {{ '' }}
                }}
            }})
            
            $nextCursor = if ($hasMore) {{ {start_index + clamped_size} }} else {{ $null }}
            
            @{{
                items = $items
                next_cursor = $nextCursor
                page_size = {clamped_size}
                total_estimate = $total
            }} | ConvertTo-Json -Depth 3 -Compress
        """
        
        result = await self._run_powershell(
            command,
            {"filter_params": filter_params, "page_size": clamped_size},
        )
        
        if not result["success"]:
            logger.warning("query_users failed: %s", result["error"])
            return {
                "items": [],
                "next_cursor": None,
                "page_size": clamped_size,
                "total_estimate": 0,
                "applied_filter": filter_params,
                "warnings": [f"Query failed: {result['error'][:100]}"],
            }
        
        if not result["data"]:
            return {
                "items": [],
                "next_cursor": None,
                "page_size": clamped_size,
                "total_estimate": 0,
                "applied_filter": filter_params,
                "warnings": [],
            }
        
        try:
            response = json.loads(result["data"])
            
            # Filter fields based on requested fields
            filtered_items = []
            for item in response.get("items", []):
                filtered_item = {k: v for k, v in item.items() if k in fields}
                filtered_items.append(filtered_item)
            
            return {
                "items": filtered_items,
                "next_cursor": response.get("next_cursor"),
                "page_size": clamped_size,
                "total_estimate": response.get("total_estimate", 0),
                "applied_filter": filter_params,
                "warnings": [],
            }
        except json.JSONDecodeError as e:
            logger.error("Failed to parse query_users data: %s", str(e))
            return {
                "items": [],
                "next_cursor": None,
                "page_size": clamped_size,
                "total_estimate": 0,
                "applied_filter": filter_params,
                "warnings": ["Failed to parse query results"],
            }

    async def count_users(
        self,
        filter_params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Count users matching filter without returning full records."""
        filter_params = filter_params or {}
        
        # Build AD filter from filter_params (same logic as query_users)
        ad_filter_parts = []
        
        if "enabled" in filter_params:
            enabled_val = "True" if filter_params["enabled"] else "False"
            ad_filter_parts.append(f"Enabled -eq ${enabled_val}")
        
        if "name_contains" in filter_params:
            name_query = self._escape_ps_single_quoted(filter_params["name_contains"])
            ad_filter_parts.append(f"DisplayName -like '*{name_query}*'")
        
        if "username_prefix" in filter_params:
            prefix = self._escape_ps_single_quoted(filter_params["username_prefix"])
            ad_filter_parts.append(f"samAccountName -like '{prefix}*'")
        
        if "ou_contains" in filter_params:
            ou_part = self._escape_ps_single_quoted(filter_params["ou_contains"])
            ad_filter_parts.append(f"DistinguishedName -like '*{ou_part}*'")
        
        if "description_contains" in filter_params:
            desc_part = self._escape_ps_single_quoted(filter_params["description_contains"])
            ad_filter_parts.append(f"Description -like '*{desc_part}*'")
        
        if ad_filter_parts:
            ad_filter = " -and ".join(ad_filter_parts)
        else:
            ad_filter = "*"
        
        command = f"""
            $filter = "{ad_filter}"
            $users = Get-ADUser -Filter $filter -Properties lastLogonTimestamp,MemberOf -ErrorAction Stop
        """
        
        # Handle last_logon_before_days post-filter
        if "last_logon_before_days" in filter_params:
            days = filter_params["last_logon_before_days"]
            command += f"$users = $users | Where-Object {{ if ($_.lastLogonTimestamp) {{ $cutoff = (Get-Date).AddDays(-{days}).ToFileTime(); $_.lastLogonTimestamp -lt $cutoff }} else {{ $true }} }}\n"
        
        # Handle group_any post-filter
        if "group_any" in filter_params:
            groups_json = json.dumps(filter_params["group_any"])
            escaped_groups_json = groups_json.replace("'", "''")
            command += f"$users = $users | Where-Object {{ $targetGroups = '{escaped_groups_json}' | ConvertFrom-Json; $userGroups = @($_.MemberOf | ForEach-Object {{ $g = Get-ADGroup $_ -ErrorAction SilentlyContinue; if ($g) {{ $g.Name }} }}); $found = $false; foreach ($tg in $targetGroups) {{ if ($userGroups -contains $tg) {{ $found = $true; break }} }}; $found }}\n"
        
        command += """
            $users = @($users)
            @{
                count = $users.Count
            } | ConvertTo-Json -Compress
        """
        
        result = await self._run_powershell(command, {"filter_params": filter_params})
        
        if not result["success"]:
            logger.warning("count_users failed: %s", result["error"])
            return {
                "count": 0,
                "applied_filter": filter_params,
            }
        
        if not result["data"]:
            return {
                "count": 0,
                "applied_filter": filter_params,
            }
        
        try:
            response = json.loads(result["data"])
            return {
                "count": response.get("count", 0),
                "applied_filter": filter_params,
            }
        except json.JSONDecodeError as e:
            logger.error("Failed to parse count_users data: %s", str(e))
            return {
                "count": 0,
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
        
        # Build AD filter (same as count_users)
        ad_filter_parts = []
        
        if "enabled" in filter_params:
            enabled_val = "True" if filter_params["enabled"] else "False"
            ad_filter_parts.append(f"Enabled -eq ${enabled_val}")
        
        if "name_contains" in filter_params:
            name_query = self._escape_ps_single_quoted(filter_params["name_contains"])
            ad_filter_parts.append(f"DisplayName -like '*{name_query}*'")
        
        if "username_prefix" in filter_params:
            prefix = self._escape_ps_single_quoted(filter_params["username_prefix"])
            ad_filter_parts.append(f"samAccountName -like '{prefix}*'")
        
        if "ou_contains" in filter_params:
            ou_part = self._escape_ps_single_quoted(filter_params["ou_contains"])
            ad_filter_parts.append(f"DistinguishedName -like '*{ou_part}*'")
        
        if "description_contains" in filter_params:
            desc_part = self._escape_ps_single_quoted(filter_params["description_contains"])
            ad_filter_parts.append(f"Description -like '*{desc_part}*'")
        
        if ad_filter_parts:
            ad_filter = " -and ".join(ad_filter_parts)
        else:
            ad_filter = "*"
        
        # Determine grouping field
        group_field_map = {
            "enabled": "Enabled",
            "ou": "DistinguishedName",
            "department": "Department",
            "title": "Title",
        }
        group_field = group_field_map.get(group_by, "Enabled")
        
        # Determine required properties
        required_props = ["Enabled", "lastLogonTimestamp", "MemberOf", "whenCreated"]
        if group_by in ["department", "title", "ou"]:
            if group_by == "department":
                required_props.append("Department")
            elif group_by == "title":
                required_props.append("Title")
        
        props_csv = ", ".join(set(required_props))
        clamped_top = min(max(1, top), 50)
        
        command = f"""
            $filter = "{ad_filter}"
            $users = Get-ADUser -Filter $filter -Properties {props_csv} -ErrorAction Stop
        """
        
        # Handle last_logon_before_days post-filter
        if "last_logon_before_days" in filter_params:
            days = filter_params["last_logon_before_days"]
            command += f"$users = $users | Where-Object {{ if ($_.lastLogonTimestamp) {{ $cutoff = (Get-Date).AddDays(-{days}).ToFileTime(); $_.lastLogonTimestamp -lt $cutoff }} else {{ $true }} }}\n"
        
        # Handle group_any post-filter
        if "group_any" in filter_params:
            groups_json = json.dumps(filter_params["group_any"])
            escaped_groups_json = groups_json.replace("'", "''")
            command += f"$users = $users | Where-Object {{ $targetGroups = '{escaped_groups_json}' | ConvertFrom-Json; $userGroups = @($_.MemberOf | ForEach-Object {{ $g = Get-ADGroup $_ -ErrorAction SilentlyContinue; if ($g) {{ $g.Name }} }}); $found = $false; foreach ($tg in $targetGroups) {{ if ($userGroups -contains $tg) {{ $found = $true; break }} }}; $found }}\n"
        
        # Group by logic
        command += """
            $users = @($users)
        """
        if group_by == "enabled":
            command += """
                $buckets = $users | Group-Object Enabled | ForEach-Object {
                    @{
                        key = if ($_.Name -eq "True") { "Enabled" } else { "Disabled" }
                        count = $_.Count
                    }
                } | Sort-Object count -Descending
            """
        elif group_by == "ou":
            command += """
                $buckets = $users | ForEach-Object {
                    # Extract OU from DN
                    $dn = $_.DistinguishedName
                    if ($dn -match 'OU=([^,]+)') {
                        $matches[1]
                    } else {
                        "Root"
                    }
                } | Group-Object | ForEach-Object {
                    @{
                        key = $_.Name
                        count = $_.Count
                    }
                } | Sort-Object count -Descending
            """
        elif group_by == "department":
            command += """
                $buckets = $users | ForEach-Object {
                    if ($_.Department) { $_.Department } else { "No Department" }
                } | Group-Object | ForEach-Object {
                    @{
                        key = $_.Name
                        count = $_.Count
                    }
                } | Sort-Object count -Descending
            """
        elif group_by == "title":
            command += """
                $buckets = $users | ForEach-Object {
                    if ($_.Title) { $_.Title } else { "No Title" }
                } | Group-Object | ForEach-Object {
                    @{
                        key = $_.Name
                        count = $_.Count
                    }
                } | Sort-Object count -Descending
            """
        elif group_by == "last_logon_bucket":
            command += """
                $now = Get-Date
                $buckets = $users | ForEach-Object {
                    if ($_.lastLogonTimestamp) {
                        $lastLogon = [DateTime]::FromFileTime($_.lastLogonTimestamp)
                        $daysAgo = ($now - $lastLogon).Days
                        if ($daysAgo -lt 7) { "Last 7 days" }
                        elseif ($daysAgo -lt 30) { "Last 30 days" }
                        elseif ($daysAgo -lt 90) { "Last 90 days" }
                        else { "90+ days" }
                    } else {
                        "Never logged in"
                    }
                } | Group-Object | ForEach-Object {
                    @{
                        key = $_.Name
                        count = $_.Count
                    }
                } | Sort-Object count -Descending
            """
        elif group_by == "created_month":
            command += """
                $buckets = $users | ForEach-Object {
                    if ($_.whenCreated) {
                        $_.whenCreated.ToString("yyyy-MM")
                    } else {
                        "Unknown"
                    }
                } | Group-Object | ForEach-Object {
                    @{
                        key = $_.Name
                        count = $_.Count
                    }
                } | Sort-Object key -Descending
            """
        else:
            command += """
                $buckets = @(@{
                    key = "Unknown"
                    count = $users.Count
                })
            """
        
        command += f"""
            @{{
                buckets = @($buckets | Select-Object -First {clamped_top})
                total = $users.Count
            }} | ConvertTo-Json -Depth 3 -Compress
        """
        
        result = await self._run_powershell(
            command,
            {"filter_params": filter_params, "group_by": group_by},
        )
        
        if not result["success"]:
            logger.warning("summarize_users failed: %s", result["error"])
            return {
                "buckets": [],
                "total": 0,
                "applied_filter": filter_params,
            }
        
        if not result["data"]:
            return {
                "buckets": [],
                "total": 0,
                "applied_filter": filter_params,
            }
        
        try:
            response = json.loads(result["data"])
            buckets = response.get("buckets", [])
            if not isinstance(buckets, list):
                buckets = [buckets] if buckets else []
            
            return {
                "buckets": buckets,
                "total": response.get("total", 0),
                "applied_filter": filter_params,
            }
        except json.JSONDecodeError as e:
            logger.error("Failed to parse summarize_users data: %s", str(e))
            return {
                "buckets": [],
                "total": 0,
                "applied_filter": filter_params,
            }

