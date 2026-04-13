"""
Root conftest.py — adds lib/ to sys.path so legacy identity tests can import
adapters directly (e.g. `from ad_adapter import ...`) without package prefix.
"""
import sys
from pathlib import Path

# Allow bare imports like `from ad_adapter import ...` used by identity_tests/
sys.path.insert(0, str(Path(__file__).parent / "lib"))
