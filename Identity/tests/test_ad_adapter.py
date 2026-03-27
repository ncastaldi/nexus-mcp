import asyncio
import pytest
from unittest.mock import AsyncMock, patch
from ad_adapter import ActiveDirectoryIdentityBackend


@pytest.fixture
def ad_backend():
    """Create AD adapter instance for testing without credentials."""
    return ActiveDirectoryIdentityBackend(timeout_seconds=5.0)


@pytest.fixture
def ad_backend_with_creds():
    """Create AD adapter with test credentials."""
    return ActiveDirectoryIdentityBackend(
        username="test_user", password="test_pass", timeout_seconds=5.0
    )


class TestActiveDirectoryBackend:
    """Unit tests for AD adapter output parsing and error handling."""

    @pytest.mark.asyncio
    async def test_get_user_success(self, ad_backend):
        """Test successful user lookup with valid JSON response."""
        mock_output = '{"username":"jane.doe","first_name":"Jane","last_name":"Doe","display_name":"Jane Doe","enabled":true,"ou":"OU=Users,DC=example,DC=local","description":"Test User","last_logon_utc":"2026-03-10T15:30:00.0000000Z"}'

        with patch.object(
            ad_backend, "_run_powershell", return_value={"success": True, "data": mock_output, "error": None}
        ):
            result = await ad_backend.get_user("jane.doe")

        assert result is not None
        assert result["username"] == "jane.doe"
        assert result["first_name"] == "Jane"
        assert result["last_name"] == "Doe"
        assert result["display_name"] == "Jane Doe"
        assert result["enabled"] is True
        assert result["ou"] == "OU=Users,DC=example,DC=local"
        assert result["description"] == "Test User"
        assert "2026-03-10" in result["last_logon_utc"]

    @pytest.mark.asyncio
    async def test_search_users_by_name_success_list(self, ad_backend):
        """Test name search parsing for list response."""
        mock_output = '[{"username":"jane.doe","first_name":"Jane","last_name":"Doe","display_name":"Jane Doe","enabled":true,"ou":"OU=Users,DC=example,DC=local"},{"username":"john.doe","first_name":"John","last_name":"Doe","display_name":"John Doe","enabled":true,"ou":"OU=Users,DC=example,DC=local"}]'

        with patch.object(
            ad_backend, "_run_powershell", return_value={"success": True, "data": mock_output, "error": None}
        ):
            result = await ad_backend.search_users_by_name("doe", limit=10)

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["username"] == "jane.doe"
        assert result[0]["display_name"] == "Jane Doe"

    @pytest.mark.asyncio
    async def test_search_users_by_name_success_single_object(self, ad_backend):
        """Test name search parsing for single-object JSON response."""
        mock_output = '{"username":"jane.doe","first_name":"Jane","last_name":"Doe","display_name":"Jane Doe","enabled":true,"ou":"OU=Users,DC=example,DC=local"}'

        with patch.object(
            ad_backend, "_run_powershell", return_value={"success": True, "data": mock_output, "error": None}
        ):
            result = await ad_backend.search_users_by_name("Jane Doe", limit=10)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["username"] == "jane.doe"

    @pytest.mark.asyncio
    async def test_search_users_by_name_empty_query(self, ad_backend):
        """Test name search rejects blank query."""
        result = await ad_backend.search_users_by_name("   ", limit=10)
        assert result == []

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, ad_backend):
        """Test user lookup when user does not exist."""
        with patch.object(
            ad_backend, "_run_powershell", return_value={"success": True, "data": "", "error": None}
        ):
            result = await ad_backend.get_user("nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_user_command_failure(self, ad_backend):
        """Test user lookup when PowerShell command fails."""
        with patch.object(
            ad_backend,
            "_run_powershell",
            return_value={"success": False, "data": None, "error": "Access denied"},
        ):
            result = await ad_backend.get_user("jane.doe")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_user_groups_success(self, ad_backend):
        """Test group membership retrieval."""
        mock_output = '["GG-Global-VPN","GG-ServiceDesk"]'

        with patch.object(
            ad_backend, "_run_powershell", return_value={"success": True, "data": mock_output, "error": None}
        ):
            result = await ad_backend.get_user_groups("jane.doe")

        assert isinstance(result, list)
        assert len(result) == 2
        assert "GG-Global-VPN" in result
        assert "GG-ServiceDesk" in result

    @pytest.mark.asyncio
    async def test_get_user_groups_empty(self, ad_backend):
        """Test group membership when user has no groups."""
        mock_output = "[]"

        with patch.object(
            ad_backend, "_run_powershell", return_value={"success": True, "data": mock_output, "error": None}
        ):
            result = await ad_backend.get_user_groups("jane.doe")

        assert result == []

    @pytest.mark.asyncio
    async def test_get_group_members_success(self, ad_backend):
        """Test retrieving members of a group."""
        mock_output = '["jane.doe","john.smith"]'

        with patch.object(
            ad_backend, "_run_powershell", return_value={"success": True, "data": mock_output, "error": None}
        ):
            result = await ad_backend.get_group_members("GG-ServiceDesk")

        assert isinstance(result, list)
        assert len(result) == 2
        assert "jane.doe" in result

    @pytest.mark.asyncio
    async def test_find_stale_users_success(self, ad_backend):
        """Test finding stale users with lastLogonTimestamp cutoff."""
        mock_output = '[{"username":"john.smith","enabled":false,"last_logon_utc":"2025-12-01T10:00:00.0000000Z"}]'

        with patch.object(
            ad_backend, "_run_powershell", return_value={"success": True, "data": mock_output, "error": None}
        ):
            result = await ad_backend.find_stale_users(60)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["username"] == "john.smith"
        assert result[0]["enabled"] is False

    @pytest.mark.asyncio
    async def test_find_stale_users_negative_days(self, ad_backend):
        """Test stale user query with invalid negative days."""
        result = await ad_backend.find_stale_users(-5)
        assert result == []

    @pytest.mark.asyncio
    async def test_get_computer_success(self, ad_backend):
        """Test computer lookup returns OU and null assigned_username."""
        mock_output = '{"computer_name":"LT-1001","ou":"OU=Workstations,DC=example,DC=local","assigned_username":null}'

        with patch.object(
            ad_backend, "_run_powershell", return_value={"success": True, "data": mock_output, "error": None}
        ):
            result = await ad_backend.get_computer("LT-1001")

        assert result is not None
        assert result["computer_name"] == "LT-1001"
        assert result["ou"] == "OU=Workstations,DC=example,DC=local"
        assert result["assigned_username"] is None

    @pytest.mark.asyncio
    async def test_get_computer_not_found(self, ad_backend):
        """Test computer lookup when computer does not exist."""
        with patch.object(
            ad_backend, "_run_powershell", return_value={"success": True, "data": "", "error": None}
        ):
            result = await ad_backend.get_computer("NONEXISTENT")

        assert result is None

    @pytest.mark.asyncio
    async def test_run_powershell_timeout(self, ad_backend):
        """Test PowerShell execution timeout handling."""
        with patch("asyncio.wait_for", side_effect=asyncio.TimeoutError):
            result = await ad_backend._run_powershell("Start-Sleep -Seconds 60")

        assert result["success"] is False
        assert "timeout" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_run_powershell_with_credentials(self, ad_backend_with_creds):
        """Test PowerShell command includes credential block when configured."""
        mock_process = AsyncMock()
        mock_process.communicate.return_value = (b"", b"")
        mock_process.returncode = 0

        with patch(
            "asyncio.create_subprocess_exec", return_value=mock_process
        ) as mock_subprocess:
            await ad_backend_with_creds._run_powershell("Get-ADUser test")
            
            # Verify credential block was included in command args
            call_args = mock_subprocess.call_args[0]
            full_command = call_args[4]  # 5th arg is the command string
            assert "ConvertTo-SecureString" in full_command
            assert "PSCredential" in full_command


class TestBackendContract:
    """Contract tests ensuring AD adapter matches IdentityBackend interface."""

    @pytest.mark.asyncio
    async def test_get_user_return_shape(self, ad_backend):
        """Verify get_user returns correct shape or None."""
        mock_output = '{"username":"test","first_name":"Test","last_name":"User","display_name":"Test User","enabled":true,"ou":"OU=Test","description":"","last_logon_utc":""}'

        with patch.object(
            ad_backend, "_run_powershell", return_value={"success": True, "data": mock_output, "error": None}
        ):
            result = await ad_backend.get_user("test")

        assert result is None or isinstance(result, dict)
        if result:
            assert "username" in result
            assert "first_name" in result
            assert "last_name" in result
            assert "display_name" in result
            assert "enabled" in result
            assert "ou" in result
            assert "description" in result
            assert "last_logon_utc" in result

    @pytest.mark.asyncio
    async def test_search_users_by_name_return_shape(self, ad_backend):
        """Verify search_users_by_name returns list of expected user records."""
        mock_output = '[{"username":"test","first_name":"Test","last_name":"User","display_name":"Test User","enabled":true,"ou":"OU=Test"}]'

        with patch.object(
            ad_backend, "_run_powershell", return_value={"success": True, "data": mock_output, "error": None}
        ):
            result = await ad_backend.search_users_by_name("test", limit=10)

        assert isinstance(result, list)
        for user in result:
            assert "username" in user
            assert "first_name" in user
            assert "last_name" in user
            assert "display_name" in user
            assert "enabled" in user
            assert "ou" in user

    @pytest.mark.asyncio
    async def test_get_user_groups_return_shape(self, ad_backend):
        """Verify get_user_groups always returns list[str]."""
        with patch.object(
            ad_backend, "_run_powershell", return_value={"success": True, "data": "[]", "error": None}
        ):
            result = await ad_backend.get_user_groups("test")

        assert isinstance(result, list)
        assert all(isinstance(item, str) for item in result)

    @pytest.mark.asyncio
    async def test_find_stale_users_return_shape(self, ad_backend):
        """Verify find_stale_users returns list of dicts with correct keys."""
        mock_output = '[{"username":"test","enabled":true,"last_logon_utc":""}]'

        with patch.object(
            ad_backend, "_run_powershell", return_value={"success": True, "data": mock_output, "error": None}
        ):
            result = await ad_backend.find_stale_users(30)

        assert isinstance(result, list)
        for user in result:
            assert "username" in user
            assert "enabled" in user
            assert "last_logon_utc" in user
