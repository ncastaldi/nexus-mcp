"""Integration test for audit shard - verifies full end-to-end functionality.

This test simulates the full MCP server lifecycle:
1. Imports and initializes FastMCP server
2. Registers audit shard with real tool decorators
3. Calls each tool and validates output structure
4. Verifies expected mismatch counts from mock data

Run: python -m pytest tests/integration_test_audit_shard.py -v
"""

import sys
import os

# Setup paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from mcp.server.fastmcp import FastMCP
from shards import audit


def test_audit_shard_registration():
    """Verify audit shard registers 4 tools with FastMCP."""
    mcp = FastMCP(name="TestServer")
    audit.register(mcp)
    
    # Check all expected tools are registered
    expected_tools = [
        "scan_status_reconciliation",
        "scan_job_title_drift",
        "scan_department_mismatches",
        "scan_name_variance_mismatches",
    ]
    
    for tool_name in expected_tools:
        assert tool_name in mcp._tool_manager._tools, f"Tool {tool_name} not registered"


def test_audit_tools_execute_successfully():
    """Verify each audit tool executes and returns valid data."""
    mcp = FastMCP(name="TestServer")
    audit.register(mcp)
    
    # Test each tool
    test_cases = {
        "scan_status_reconciliation": 1,  # Expected mismatch count
        "scan_job_title_drift": 1,
        "scan_department_mismatches": 1,
        "scan_name_variance_mismatches": 3,
    }
    
    for tool_name, expected_mismatches in test_cases.items():
        tool_fn = mcp._tool_manager._tools[tool_name].fn
        result = tool_fn()
        
        # Validate structure
        assert "scan_summary" in result
        assert "mismatches" in result
        
        summary = result["scan_summary"]
        assert "total_records_checked" in summary
        assert "mismatches_found" in summary
        assert "status" in summary
        
        # Validate mock data expectations
        assert summary["total_records_checked"] == 9
        assert summary["mismatches_found"] == expected_mismatches
        
        if expected_mismatches > 0:
            assert summary["status"] == "action_required"
            assert len(result["mismatches"]) == expected_mismatches


def test_status_reconciliation_mismatch_details():
    """Verify status reconciliation tool returns correct mismatch details."""
    mcp = FastMCP(name="TestServer")
    audit.register(mcp)
    
    tool_fn = mcp._tool_manager._tools["scan_status_reconciliation"].fn
    result = tool_fn()
    
    # Should detect EMP002 (Terminated User still enabled)
    assert len(result["mismatches"]) == 1
    mismatch = result["mismatches"][0]
    
    assert mismatch["employee_id"] == "EMP002"
    assert mismatch["employee_name"] == "Terminated User"
    assert mismatch["workday_status"] == "Terminated"
    assert mismatch["ad_enabled"] is True
    assert mismatch["mismatch_type"] == "terminated_but_enabled"
    assert mismatch["severity"] == "high"


def test_job_title_drift_mismatch_details():
    """Verify job title drift tool returns correct mismatch details."""
    mcp = FastMCP(name="TestServer")
    audit.register(mcp)
    
    tool_fn = mcp._tool_manager._tools["scan_job_title_drift"].fn
    result = tool_fn()
    
    # Should detect EMP003 (Alicia - title mismatch)
    assert len(result["mismatches"]) == 1
    mismatch = result["mismatches"][0]
    
    assert mismatch["employee_id"] == "EMP003"
    assert mismatch["employee_name"] == "Alicia"
    assert mismatch["workday_title"] == "Senior Systems Analyst"
    assert mismatch["ad_title"] == "Systems Analyst"
    assert mismatch["mismatch_type"] == "job_title_mismatch"
    assert mismatch["severity"] == "medium"


def test_department_drift_mismatch_details():
    """Verify department drift tool returns correct mismatch details."""
    mcp = FastMCP(name="TestServer")
    audit.register(mcp)
    
    tool_fn = mcp._tool_manager._tools["scan_department_mismatches"].fn
    result = tool_fn()
    
    # Should detect EMP004 (Jordan - Finance vs Accounting)
    assert len(result["mismatches"]) == 1
    mismatch = result["mismatches"][0]
    
    assert mismatch["employee_id"] == "EMP004"
    assert mismatch["employee_name"] == "Jordan"
    assert mismatch["workday_department"] == "Finance"
    assert mismatch["ad_department"] == "Accounting"
    assert mismatch["workday_cost_center"] == "CC300-FIN"
    assert mismatch["mismatch_type"] == "department_drift"
    assert mismatch["severity"] == "medium"


def test_name_variance_mismatch_details():
    """Verify name variance tool returns correct mismatch details."""
    mcp = FastMCP(name="TestServer")
    audit.register(mcp)
    
    tool_fn = mcp._tool_manager._tools["scan_name_variance_mismatches"].fn
    result = tool_fn()
    
    # Should detect 3 name variance issues
    assert len(result["mismatches"]) == 3
    
    # Verify employee IDs match expected
    employee_ids = {m["employee_id"] for m in result["mismatches"]}
    assert employee_ids == {"EMP010", "EMP020", "EMP777"}
    
    # All should be low severity
    for mismatch in result["mismatches"]:
        assert mismatch["mismatch_type"] == "name_variance_requires_review"
        assert mismatch["severity"] == "low"
        assert "workday_legal_name" in mismatch
        assert "workday_preferred_name" in mismatch
        assert "ad_display_name" in mismatch
