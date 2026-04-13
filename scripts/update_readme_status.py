#!/usr/bin/env python3
"""Deterministically update nexus-mcp README status sections.

This script standardizes a managed status block in nexus-mcp/README.md using:
- staged diff (git diff --cached)
- latest session snapshot in documentation/project-history/
- TODO / RESTART NOTE markers in changed files

Usage:
  python scripts/update_readme_status.py           # write updates
  python scripts/update_readme_status.py --check   # fail if README is stale
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path


STATUS_BEGIN = "<!-- STATUS_PAGE:BEGIN -->"
STATUS_END = "<!-- STATUS_PAGE:END -->"

# Map known moved/renamed docs to current locations.
LINK_REWRITE_MAP = {
    "mcp-server/README.md": "Local-Setup.md",
}


def run_git(repo_root: Path, args: list[str]) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        return ""
    return proc.stdout


def get_staged_files(repo_root: Path) -> list[str]:
    out = run_git(repo_root, ["diff", "--cached", "--name-only"])
    return [line.strip() for line in out.splitlines() if line.strip()]


def get_staged_diff(repo_root: Path) -> str:
    return run_git(repo_root, ["diff", "--cached"])


def find_latest_snapshot(repo_root: Path) -> Path | None:
    snaps = sorted((repo_root / "documentation" / "project-history").glob("SESSION_SNAPSHOT_*.md"))
    return snaps[-1] if snaps else None


def detect_components(files: list[str]) -> list[str]:
    labels = set()
    for path in files:
        p = path.lower()
        if p.startswith("nexus-mcp/src/"):
            labels.add("core")
        if "/shards/" in p:
            labels.add("shards")
        if p.startswith("nexus-mcp/lib/"):
            labels.add("adapters")
        if p.startswith("nexus-mcp/tests/"):
            labels.add("tests")
        if p.endswith("readme.md") or "/docs" in p or p.startswith("documentation/"):
            labels.add("docs")
        if "/workday" in p:
            labels.add("workday")
        if "/identity" in p:
            labels.add("identity")
        if "/audit" in p:
            labels.add("audit")
        if p.startswith(".github/workflows/") or "/hooks/" in p:
            labels.add("ci")
        if p.endswith("pyproject.toml"):
            labels.add("packaging")
    return sorted(labels) or ["none"]


def find_notes(repo_root: Path, files: list[str]) -> list[str]:
    notes: list[str] = []
    pat = re.compile(r"TODO|//\s*RESTART NOTE", re.IGNORECASE)
    for rel in files:
        p = repo_root / rel
        if not p.exists() or p.is_dir():
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for idx, line in enumerate(text.splitlines(), start=1):
            if pat.search(line):
                notes.append(f"{rel}:{idx}")
    return notes


def is_breaking(diff_text: str) -> bool:
    if "compose.yaml" not in diff_text and "docker-compose" not in diff_text:
        return False
    return ("ports:" in diff_text) or ("volumes:" in diff_text)


def render_status_block(
    snapshot_name: str,
    components: list[str],
    notes: list[str],
    breaking: bool,
    staged_empty: bool,
) -> str:
    today = dt.date.today().isoformat()
    comp = ", ".join(components)
    note_summary = "none" if not notes else f"{len(notes)} marker(s)"
    break_txt = "Yes" if breaking else "No"
    staged_txt = "No staged files" if staged_empty else "Staged changes detected"

    return f"""{STATUS_BEGIN}
## Status Page (Managed)

| Field | Value |
|---|---|
| Last Updated | {today} |
| Latest Session Snapshot | {snapshot_name} |
| Change Signal | {staged_txt} |
| Components Affected | {comp} |
| TODO/RESTART Markers | {note_summary} |
| BREAKING CHANGE (compose ports/volumes) | {break_txt} |

## Shard Status Board (Traffic Light)

| Shard | System(s) | Status | WIS Ref | Flag | Standard Gate |
|---|---|---|---|---|---|
| identity | Active Directory + Entra ID | 🟢 Green | WIS-017 | ENABLE_IDENTITY | Tool tests passing |
| workday | Workday HCM | 🟡 Yellow | WIS-009 | ENABLE_WORKDAY | Credentials + live validation pending |
| audit | Cross-system drift + reporting | 🟡 Yellow | WIS-018 | ENABLE_AUDIT | Verification maturing |
| itsm | BMC Helix ITSM | 🔴 Red | WIS-021 | ENABLE_ITSM | Stub only |
| assets | Lansweeper + Intune | 🔴 Red | WIS-022 | ENABLE_ASSETS | Stub only |
| logistics | FedEx | 🔴 Red | WIS-023 | ENABLE_LOGISTICS | Stub only |

## Discipline Drives Quality

| Pillar | Target Standard | Current Signal |
|---|---|---|
| Type Hinting | Public interfaces typed | 🟢 Pydantic-based schemas in place |
| Pylance | Zero-error baseline | 🟡 Enforced goal, pending full workspace sweep |
| Modular Structure | Orchestrator -> shards -> adapters | 🟢 Applied in current architecture |
| Test Gates | Pre-push tests + validation | 🟢 Active local gate |
| Security Logging | SOC 2 audit trail with redaction | 🟢 Active |

## Sprint Traceability (2026)

| WIS ID | Area | Status |
|---|---|---|
| WIS-009 | Workday integration | 🟡 In progress |
| WIS-017 | Identity integration | 🟢 Production-ready |
| WIS-018 | Audit capability | 🟡 In progress |
| WIS-021 | ITSM shard | 🔴 Planned |
| WIS-022 | Assets shard | 🔴 Planned |
| WIS-023 | Logistics shard | 🔴 Planned |
{STATUS_END}
"""


def update_readme_content(existing: str, block: str) -> str:
    if STATUS_BEGIN in existing and STATUS_END in existing:
        pattern = re.compile(
            rf"{re.escape(STATUS_BEGIN)}.*?{re.escape(STATUS_END)}(?:\r?\n)*",
            re.DOTALL,
        )
        return pattern.sub(block + "\n\n", existing, count=1)

    start = existing.find("## Shard Status Board")
    end = existing.find("## Folder Structure")
    if start != -1 and end != -1 and end > start:
        return existing[:start] + block + "\n\n" + existing[end:]

    header = "# Nexus-MCP — Enterprise Integration Server\n\n"
    if existing.startswith("# Nexus-MCP"):
        first_break = existing.find("\n\n")
        if first_break != -1:
            return existing[: first_break + 2] + block + "\n\n" + existing[first_break + 2 :]

    return header + block + "\n\n" + existing


def _is_external_link(target: str) -> bool:
    lowered = target.lower()
    return (
        lowered.startswith("http://")
        or lowered.startswith("https://")
        or lowered.startswith("mailto:")
        or lowered.startswith("#")
    )


def _resolve_internal_link(repo_root: Path, readme_path: Path, target: str) -> Path:
    clean = target.split("#", 1)[0].strip()
    if not clean:
        return Path(".")

    rel_from_readme = (readme_path.parent / clean).resolve()
    if rel_from_readme.exists():
        return rel_from_readme

    rel_from_repo = (repo_root / clean).resolve()
    if rel_from_repo.exists():
        return rel_from_repo

    return rel_from_readme


def normalize_links(repo_root: Path, readme_path: Path, text: str) -> tuple[str, dict[str, int]]:
    """Validate Markdown links, rewrite known moved targets, remove unresolved links.

    "remove" means replacing `[text](missing/path.md)` with plain `text`.
    """
    counters = {"rewritten": 0, "removed": 0, "checked": 0}
    link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

    def repl(match: re.Match[str]) -> str:
        label = match.group(1)
        target = match.group(2).strip()

        if _is_external_link(target):
            return match.group(0)

        counters["checked"] += 1
        normalized_target = target
        if target in LINK_REWRITE_MAP:
            normalized_target = LINK_REWRITE_MAP[target]
            counters["rewritten"] += 1

        resolved = _resolve_internal_link(repo_root, readme_path, normalized_target)
        if resolved.exists():
            return f"[{label}]({normalized_target})"

        counters["removed"] += 1
        return label

    updated = link_pattern.sub(repl, text)

    # Handle known legacy backtick path outside markdown link format.
    if "`mcp-server/README.md`" in updated:
        updated = updated.replace("`mcp-server/README.md`", "[Local-Setup.md](Local-Setup.md)")
        counters["rewritten"] += 1

    return updated, counters


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if README would change")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    readme = repo_root / "nexus-mcp" / "README.md"
    if not readme.exists():
        print("ERROR: nexus-mcp/README.md not found")
        return 2

    staged_files = get_staged_files(repo_root)
    staged_diff = get_staged_diff(repo_root)
    snapshot = find_latest_snapshot(repo_root)
    snapshot_name = snapshot.name if snapshot else "none"

    if not staged_files:
        print("WARN: git diff --cached is empty; README status generated from current metadata only")

    components = detect_components(staged_files)
    notes = find_notes(repo_root, staged_files)
    breaking = is_breaking(staged_diff)

    block = render_status_block(
        snapshot_name=snapshot_name,
        components=components,
        notes=notes,
        breaking=breaking,
        staged_empty=(len(staged_files) == 0),
    )

    current = readme.read_text(encoding="utf-8", errors="ignore")
    updated = update_readme_content(current, block)
    updated, link_stats = normalize_links(repo_root, readme, updated)

    if args.check:
        if updated != current:
            print("README status is stale. Run: python scripts/update_readme_status.py")
            return 1
        print("README status is up to date")
        if link_stats["checked"]:
            print(
                f"Link check: checked={link_stats['checked']} "
                f"rewritten={link_stats['rewritten']} removed={link_stats['removed']}"
            )
        return 0

    if updated != current:
        readme.write_text(updated, encoding="utf-8")
        print("Updated nexus-mcp/README.md status block")
    else:
        print("No README changes needed")
    if link_stats["checked"]:
        print(
            f"Link check: checked={link_stats['checked']} "
            f"rewritten={link_stats['rewritten']} removed={link_stats['removed']}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
