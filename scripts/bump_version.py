#!/usr/bin/env python3
"""Version management script for Nexus MCP.

Usage:
    python scripts/bump_version.py patch   # 0.1.0 → 0.1.1
    python scripts/bump_version.py minor   # 0.1.0 → 0.2.0
    python scripts/bump_version.py major   # 0.1.0 → 1.0.0
"""

import sys
import re
from pathlib import Path
from datetime import datetime

def bump_version(bump_type: str) -> tuple[str, str]:
    """Bump version in pyproject.toml."""
    
    pyproject = Path(__file__).parent.parent / "nexus-mcp" / "pyproject.toml"
    
    # Read current version
    content = pyproject.read_text()
    match = re.search(r'version = "(\d+)\.(\d+)\.(\d+)"', content)
    
    if not match:
        raise ValueError("Could not find version in pyproject.toml")
    
    major, minor, patch = map(int, match.groups())
    old_version = f"{major}.{minor}.{patch}"
    
    # Bump version
    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "patch":
        patch += 1
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")
    
    new_version = f"{major}.{minor}.{patch}"
    
    # Update file
    new_content = re.sub(
        r'version = "\d+\.\d+\.\d+"',
        f'version = "{new_version}"',
        content
    )
    
    pyproject.write_text(new_content)
    
    return old_version, new_version


def update_readme(new_version: str):
    """Add version note to README."""
    
    readme = Path(__file__).parent.parent / "nexus-mcp" / "README.md"
    content = readme.read_text()
    
    # Find the "Latest changes" section
    date_str = datetime.now().strftime("%Y-%m-%d")
    version_note = f"\n**Version {new_version}** ({date_str})\n"
    
    # Insert after the "Latest changes" header
    if "## Latest changes" in content:
        content = content.replace(
            "## Latest changes\n",
            f"## Latest changes\n{version_note}"
        )
        readme.write_text(content)
        print(f"✅ Updated README.md with version {new_version}")
    else:
        print("⚠️  Could not find 'Latest changes' section in README.md")


def update_vscode_config(new_version: str):
    """Update VS Code MCP registration if version-specific."""
    
    settings = Path(__file__).parent.parent / ".vscode" / "settings.json"
    
    if settings.exists():
        content = settings.read_text()
        # If we start versioning the MCP server registration, update it here
        print(f"✅ VS Code config is version-agnostic (no update needed)")
    else:
        print("⚠️  No VS Code settings.json found")


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ["major", "minor", "patch"]:
        print(__doc__)
        sys.exit(1)
    
    bump_type = sys.argv[1]
    
    try:
        old_version, new_version = bump_version(bump_type)
        
        print("")
        print("=" * 60)
        print(f"VERSION BUMP: {old_version} → {new_version}")
        print("=" * 60)
        print("")
        print(f"Bump type: {bump_type}")
        print(f"Old version: {old_version}")
        print(f"New version: {new_version}")
        print("")
        
        # Update related files
        update_readme(new_version)
        update_vscode_config(new_version)
        
        print("")
        print("✅ Version bump complete!")
        print("")
        print("Next steps:")
        print(f"  1. Review changes: git diff")
        print(f"  2. Commit: git add . && git commit -m 'chore: bump version to {new_version}'")
        print(f"  3. Tag: git tag v{new_version}")
        print(f"  4. Push: git push origin main --tags")
        print("")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
