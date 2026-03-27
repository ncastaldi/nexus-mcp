# Identity MCP implementation kickoff (Phase 1)

## Purpose

This document starts implementation of an Identity MCP server with a read-only baseline.

## What is implemented

- Python MCP server scaffold using FastMCP
- Read-only tool exposed: `get_user`
- Read-only tool exposed: `get_user_groups`
- Read-only tool exposed: `get_group_members`
- Read-only tool exposed: `find_stale_users`
- Read-only tool exposed: `get_computer`
- In-memory backend for local contract testing
- Active Directory backend using PowerShell subprocess wrappers
- Environment-based backend selection (memory vs AD)
- STDERR-only logging for STDIO transport safety
- Basic audit log entries for tool calls
- Unit tests and integration smoke tests

## Files

- `identity_mcp_server.py`: FastMCP server, tool definitions, logging, backend selection, and run entrypoint
- `identity_backend.py`: backend interface and in-memory implementation
- `ad_adapter.py`: Active Directory backend using PowerShell Get-AD* cmdlets
- `tests/test_ad_adapter.py`: unit tests for AD adapter output parsing and error handling
- `tests/test_integration.py`: integration smoke tests against non-production AD
- `pyproject.toml`: project metadata, dependency pin for MCP SDK, and CLI entrypoint
- `.gitignore`: excludes Python bytecode, test cache, and local virtual environment artifacts

## How to run

### Using in-memory backend (default, safe mode)

```bash
uv run identity_mcp_server.py
```

### Using Active Directory backend

Set environment variables before running:

```bash
# Test environment with explicit credentials
export IDENTITY_BACKEND=ad
export AD_USERNAME=your_test_username
export AD_PASSWORD=your_test_password
uv run identity_mcp_server.py
```

```bash
# Production environment with service account context
export IDENTITY_BACKEND=ad
# Service account runs process, no explicit credentials needed
uv run identity_mcp_server.py
```

### Running tests

```bash
# Install test dependencies
uv pip install -e ".[test]"

# Run unit tests only (no AD connection required)
pytest tests/test_ad_adapter.py -v

# Run integration smoke tests (requires AD credentials)
export AD_TEST_USERNAME=your_test_username
export AD_TEST_PASSWORD=your_test_password
export AD_TEST_USER=known_test_user
export AD_TEST_GROUP=known_test_group
export AD_TEST_COMPUTER=known_test_computer
pytest tests/test_integration.py -v

# Run all tests
pytest tests/ -v
```

## Active Directory adapter details

### Query mapping

- `get_user`: Uses `Get-ADUser` with samAccountName filter, retrieves Enabled, DistinguishedName, Description, lastLogonTimestamp
- `get_user_groups`: Uses `Get-ADUser` with MemberOf property, resolves group names
- `get_group_members`: Uses `Get-ADGroup` + `Get-ADGroupMember`, filters user objects only
- `find_stale_users`: Uses `Get-ADUser` with lastLogonTimestamp cutoff (FileTime comparison)
- `get_computer`: Uses `Get-ADComputer`, returns OU and null assigned_username (Phase 1)

### Authentication model

- Test environments: explicit username/password via environment variables
- Production: process runs as dedicated service account, no credentials in code
- Service account requires Read Directory Data permission only (no write permissions)

### Error handling

All backend failures (timeout, auth denied, permission denied) return:

- `None` for get_user and get_computer (tool wrapper converts to "User not found" or "Computer not found")
- Empty list `[]` for get_user_groups, get_group_members, find_stale_users

### Timeouts

Default: 30 seconds per query. Override with `AD_TIMEOUT` environment variable.

## Known gaps (deferred to later phases)

- Ticket-ID enforcement for write actions (Phase 3)
- PII redaction in audit logs (toggle ready, not enabled by default)
- Entra ID/Azure AD integration (separate adapter)
- Production service account provisioning (infrastructure task)
- Host/client configuration details depend on your selected MCP client

## Verification checklist

Before deploying to production:

- [ ] Unit tests pass: `pytest tests/test_ad_adapter.py -v`
- [ ] Integration smoke tests pass against non-production AD: `pytest tests/test_integration.py -v`
- [ ] Service account provisioned with Read Directory Data only
- [ ] MCP tool responses match expected contract shapes
- [ ] Error messages are friendly strings (not exceptions or technical errors)
- [ ] Stale-user logic confirmed using lastLogonTimestamp
- [ ] Computer assigned_username returns null in Phase 1
- [ ] Backend selection tested: memory mode and AD mode both run successfully

## Next implementation slice

1. Add structured PII redaction toggle for audit logs.
2. Add phase gate config that blocks write tools entirely until explicitly enabled (Phase 3 prep).
3. Implement Entra ID/Azure AD adapter (separate backend).
4. Add canary/rollback mechanism for backend switching.
