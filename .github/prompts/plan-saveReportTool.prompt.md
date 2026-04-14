# Plan: Add `save_report` Tool to nexus-mcp

## TL;DR
Add a new `save_report` MCP tool that accepts a title and markdown content, then writes it as a `.md` file to the configured reports directory (`./documentation/output-reports/`). Implemented as a new `reports.py` shard — consistent with the existing shard pattern and aligned with the pre-staged `generate_*` tools referenced in the README. All dependencies (`aiofiles`, `ReportConfig`) are already present.

---

## Branch Identity
- Branch name: `feat/add-save-report-tool`

---

## Steps

### Phase 1 — Create the shard
1. Create `nexus-mcp/src/shards/reports.py`
   - Define `register(mcp: FastMCP) -> None`
   - Inside, define `save_report(title, content, subfolder, filename)` as `@mcp.tool()` async fn
   - Use `ReportConfig` from `lib/config.py` for `output_dir`
   - Slugify title → safe filename; add ISO timestamp suffix to avoid collisions
   - `mkdir(parents=True, exist_ok=True)` on resolved path
   - Write file using `aiofiles.open(..., "w")`
   - Return `{"status": "saved", "path": str(abs_path), "filename": final_filename, "size_bytes": N}`

### Phase 2 — Register the shard in main.py
2. In `nexus-mcp/src/main.py`:
   - Import the new shard: `from shards import reports`
   - Add conditional registration block (matches existing pattern): `if os.getenv("ENABLE_REPORTS", "true").lower() == "true": reports.register(mcp)`
   - Placement: after the existing shard registrations, before audit middleware wrapping

### Phase 3 — Environment config
3. Add `ENABLE_REPORTS=true` to `nexus-mcp/.env` (if file exists; else note it as optional)

---

## Relevant Files
- `nexus-mcp/src/shards/reports.py` — NEW file to create
- `nexus-mcp/src/main.py` — add shard import + conditional registration
- `nexus-mcp/lib/config.py` — reuse `ReportConfig` (specifically `output_dir: Path`)
- `nexus-mcp/.env` — add `ENABLE_REPORTS=true`
- `nexus-mcp/pyproject.toml` — no changes needed (aiofiles, jinja2, tabulate already listed)

---

## Verification
1. Restart nexus-mcp server; tool list should include `save_report`
2. Call `save_report(title="Test Report", content="# Hello\nThis is a test.")` from Claude
3. Verify file appears at `nexus-mcp/reports/test-report-<timestamp>.md`
4. Call `nexus_audit_recent` and confirm a `save_report` entry was logged
5. Run existing tests: `cd nexus-mcp && python -m pytest tests/`

---

## Decisions
- New shard (`reports.py`) over adding to `main.py` — keeps built-ins minimal, aligns with planned `generate_*` tools
- `aiofiles` for async writes — already a dependency, correct for async tool context
- Timestamp in filename — prevents silent overwrite collisions
- Default `ENABLE_REPORTS=true` — safe; no external API calls, pure local I/O
- Scope: only `save_report` — user requested this one tool; `generate_*` stubs are out of scope

---

## Out of Scope
- Implementing planned `generate_*` tools
- A `list_reports` or `delete_report` tool
- Any templating (Jinja2) or formatting logic beyond saving raw markdown
