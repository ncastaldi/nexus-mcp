"""Integration smoke tests for AD adapter against non-production AD environment.

These tests require:
1. Access to a non-production AD environment
2. Test credentials set via environment variables:
   - AD_TEST_USERNAME
   - AD_TEST_PASSWORD
3. Known test objects in AD for validation

Run with: pytest tests/test_integration.py -v
Skip with: pytest tests/ --ignore=tests/test_integration.py
"""

import os
import pytest
from ad_adapter import ActiveDirectoryIdentityBackend

# Skip all integration tests if credentials not configured
pytestmark = pytest.mark.skipif(
    not os.getenv("AD_TEST_USERNAME") or not os.getenv("AD_TEST_PASSWORD"),
    reason="AD test credentials not configured (set AD_TEST_USERNAME and AD_TEST_PASSWORD)",
)


@pytest.fixture
def ad_integration_backend():
    """Create AD adapter with test credentials from environment."""
    username = os.getenv("AD_TEST_USERNAME")
    password = os.getenv("AD_TEST_PASSWORD")
    return ActiveDirectoryIdentityBackend(
        username=username, password=password, timeout_seconds=30.0
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_user_smoke(ad_integration_backend):
    """Smoke test: get_user returns expected shape for known test user.

    TODO: Replace 'test_user' with actual test username in your AD environment.
    """
    test_username = os.getenv("AD_TEST_USER", "test_user")
    result = await ad_integration_backend.get_user(test_username)

    # Should return user data or None if user doesn't exist
    assert result is None or isinstance(result, dict)
    if result:
        assert "username" in result
        assert "enabled" in result
        assert "ou" in result
        assert result["username"] == test_username


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_user_groups_smoke(ad_integration_backend):
    """Smoke test: get_user_groups returns list for known test user."""
    test_username = os.getenv("AD_TEST_USER", "test_user")
    result = await ad_integration_backend.get_user_groups(test_username)

    assert isinstance(result, list)
    assert all(isinstance(group, str) for group in result)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_search_users_by_name_smoke(ad_integration_backend):
    """Smoke test: search_users_by_name returns list with expected keys."""
    test_name_query = os.getenv("AD_TEST_NAME_QUERY", "test")
    result = await ad_integration_backend.search_users_by_name(test_name_query, limit=10)

    assert isinstance(result, list)
    for user in result:
        assert "username" in user
        assert "first_name" in user
        assert "last_name" in user
        assert "display_name" in user
        assert "enabled" in user
        assert "ou" in user


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_group_members_smoke(ad_integration_backend):
    """Smoke test: get_group_members returns list for known test group."""
    test_group = os.getenv("AD_TEST_GROUP", "Domain Users")
    result = await ad_integration_backend.get_group_members(test_group)

    assert isinstance(result, list)
    assert all(isinstance(member, str) for member in result)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_find_stale_users_smoke(ad_integration_backend):
    """Smoke test: find_stale_users returns list with proper shape."""
    result = await ad_integration_backend.find_stale_users(90)

    assert isinstance(result, list)
    for user in result:
        assert "username" in user
        assert "enabled" in user
        assert "last_logon_utc" in user


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_computer_smoke(ad_integration_backend):
    """Smoke test: get_computer returns expected shape for known test computer.

    TODO: Replace 'test_computer' with actual test computer name in your AD.
    """
    test_computer = os.getenv("AD_TEST_COMPUTER", "test_computer")
    result = await ad_integration_backend.get_computer(test_computer)

    # Should return computer data or None if computer doesn't exist
    assert result is None or isinstance(result, dict)
    if result:
        assert "computer_name" in result
        assert "ou" in result
        assert "assigned_username" in result
        assert result["assigned_username"] is None  # Phase 1 requirement


@pytest.mark.integration
@pytest.mark.asyncio
async def test_nonexistent_user_returns_none(ad_integration_backend):
    """Verify nonexistent users return None, not error."""
    result = await ad_integration_backend.get_user("nonexistent_user_12345")
    assert result is None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_nonexistent_group_returns_empty(ad_integration_backend):
    """Verify nonexistent groups return empty list, not error."""
    result = await ad_integration_backend.get_group_members("nonexistent_group_12345")
    assert result == []
