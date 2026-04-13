#!/usr/bin/env python3
"""Test MCP server stdio communication.

This verifies the server can start and respond to MCP protocol messages.
"""

import subprocess
import json
import sys
from pathlib import Path

# Path to server
server_path = Path(__file__).parent / "nexus-mcp" / "src" / "main.py"
python_path = Path(__file__).parent / "nexus-mcp" / ".venv" / "Scripts" / "python.exe"

print("🔍 Testing MCP Server stdio Communication\n")
print(f"Python: {python_path}")
print(f"Server: {server_path}")
print()

# Start the server
try:
    proc = subprocess.Popen(
        [str(python_path), str(server_path)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=server_path.parent.parent,
        env={
            "USE_MOCK": "true",
            "ENABLE_AUDIT": "true",
        }
    )
    
    print("✅ Server process started")
    
    # Send initialize request (MCP protocol)
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "0.1.0",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    print("📤 Sending initialize request...")
    proc.stdin.write((json.dumps(init_request) + "\n").encode())
    proc.stdin.flush()
    
    # Read response (with timeout)
    import select
    import time
    
    start = time.time()
    timeout = 5
    
    while time.time() - start < timeout:
        if proc.stdout in select.select([proc.stdout], [], [], 0.1)[0]:
            response = proc.stdout.readline()
            if response:
                print("📥 Received response:")
                print(response.decode().strip())
                print("\n✅ Server is responding via stdio!")
                break
    else:
        print("❌ No response within timeout")
        stderr = proc.stderr.read().decode()
        if stderr:
            print("\n🔴 Server errors:")
            print(stderr)
    
    # Cleanup
    proc.terminate()
    proc.wait(timeout=2)
    
except FileNotFoundError as e:
    print(f"❌ Error: {e}")
    print("\nPossible issues:")
    print("  1. Python not found - check virtual environment")
    print("  2. Server script not found - check path")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
