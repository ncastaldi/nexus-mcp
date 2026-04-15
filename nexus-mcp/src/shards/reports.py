"""Reports shard — provides save_report tool for persisting large outputs to disk."""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import aiofiles
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger("nexus-mcp.reports")

# Workspace root = nexus-mcp/src/shards/ -> up 4
_WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
_DEFAULT_OUTPUT_DIR = _WORKSPACE_ROOT / "output-reports"


def _resolve_output_dir(raw_output_dir: Optional[Path]) -> Path:
    """Resolve output path; relative paths are anchored at workspace root."""
    if raw_output_dir is None:
        return _DEFAULT_OUTPUT_DIR
    if raw_output_dir.is_absolute():
        return raw_output_dir.resolve()
    return (_WORKSPACE_ROOT / raw_output_dir).resolve()


def _slugify(text: str) -> str:
    """Convert a title string to a safe, lowercase filename slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    text = re.sub(r"^-+|-+$", "", text)
    return text or "report"


def register(mcp: FastMCP) -> None:
    """Register reports tools onto the shared FastMCP instance."""

    try:
        import os
        if os.getenv("REPORT_OUTPUT_DIR"):
            from config import ReportConfig
            _output_dir = _resolve_output_dir(Path(ReportConfig().output_dir))
        else:
            _output_dir = _DEFAULT_OUTPUT_DIR
    except Exception:
        _output_dir = _DEFAULT_OUTPUT_DIR

    @mcp.tool()
    async def save_report(
        title: str,
        content: str,
        subfolder: Optional[str] = None,
        filename: Optional[str] = None,
    ) -> dict:
        """Save markdown content to the configured reports directory.

        Accepts a large markdown string, writes it as a .md file, and returns
        only a small metadata dict (path, filename, size_bytes) so the chat
        context stays lightweight regardless of report size.

        Args:
            title: Human-readable report title. Used to derive filename when
                   'filename' is not provided.
            content: Full markdown body to write to disk.
            subfolder: Optional subdirectory under the output dir (e.g. "identity").
                       Non-alphanumeric characters are replaced with hyphens.
            filename: Override filename base (without extension). Defaults to a
                      slugified version of 'title' with an ISO timestamp suffix.

        Returns:
            {"status": "saved", "path": str, "filename": str, "size_bytes": int}
        """
        base_dir = _output_dir
        if subfolder:
            safe_sub = re.sub(r"[^\w\-]", "-", subfolder.strip())
            base_dir = base_dir / safe_sub

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        safe_filename = (
            re.sub(r"[^\w\-]", "-", filename.strip()) if filename else _slugify(title)
        )
        final_filename = f"{safe_filename}-{timestamp}.md"
        abs_path = (base_dir / final_filename).resolve()

        # Safety guard: keep all writes inside the permitted output tree
        try:
            abs_path.relative_to(_output_dir)
        except ValueError:
            return {
                "status": "error",
                "error": "Resolved path is outside the permitted output directory.",
            }

        abs_path.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(abs_path, "w", encoding="utf-8") as f:
            await f.write(content)

        size_bytes = abs_path.stat().st_size
        logger.info("save_report: wrote %d bytes → %s", size_bytes, abs_path)

        return {
            "status": "saved",
            "path": str(abs_path),
            "filename": final_filename,
            "size_bytes": size_bytes,
        }
