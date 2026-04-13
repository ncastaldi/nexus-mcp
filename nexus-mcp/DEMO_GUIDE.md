# Demo & Test Scripts

This directory contains scripts for testing and demonstrating the Nexus MCP server functionality.

## Quick Start

All scripts run against mock data (no credentials required).

### 🔍 Audit Tools Demonstration

```bash
python test_client.py
```

**Shows:**
- All 4 audit tools executing
- Detailed mismatch detection results
- Severity classification (HIGH/MEDIUM/LOW)
- Complete scan summaries

**Expected output:** 6 total mismatches across 9 employee records

---

### 📋 Tool Catalog Browser

```bash
python list_tools.py
```

**Shows:**
- Complete tool inventory (48 tools)
- Tools organized by shard
- Tool descriptions from docstrings
- Shard loading status

---

### 📡 MCP Protocol Simulation

```bash
python test_mcp_protocol.py
```

**Shows:**
- MCP protocol handshake
- Tool discovery (tools/list)
- Tool invocation (tools/call)
- JSON response format
- Claude Desktop configuration example

---

### ✅ Full Test Suite

```bash
python -m pytest tests/workday_tests/ tests/integration_test_audit_shard.py -v
```

**Runs:**
- 4 unit tests (drift detection functions)
- 6 integration tests (MCP tool registration & execution)

**Expected:** 10/10 passing in ~0.6s

---

## Test Data

Mock data is defined in `lib/drift_detection.py`:

**Employee Records:** 9 (EMP001-EMP777)

**Pre-seeded Mismatches:**
- 1 terminated user still enabled (HIGH)
- 1 job title inconsistency (MEDIUM)
- 1 department drift (MEDIUM)
- 3 name variances (LOW)

---

## Validation Report

See `TEST_VALIDATION_REPORT.md` for:
- Complete test results
- Tool inventory
- MCP protocol compliance verification
- Commit readiness checklist

---

## Next Steps

1. **Review test output** - Confirm all tools work as expected
2. **Check validation report** - Review production readiness
3. **Commit code** - Use suggested commit message from report
4. **Integrate with Claude Desktop** - Add server to config (see test_mcp_protocol.py output)

---

**Status:** ✅ All tests passing, ready for production
