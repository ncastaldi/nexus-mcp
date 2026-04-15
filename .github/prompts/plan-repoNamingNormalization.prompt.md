## Plan: Repository naming normalization

Recommend a selective rename pass rather than full standardization. Normalize documentation and archive filenames toward kebab-case where references are limited and easy to update together. Leave Python package, module import, and primary project directory naming alone for now because those names are embedded in packaging, VS Code settings, scripts, prompts, and path assumptions.

**Steps**
1. Define target convention: keep canonical root exceptions like README.md; use kebab-case for Markdown/doc folders and snake_case for Python modules; keep distribution name `nexus-mcp` unchanged.
2. Phase 1, low-risk renames: rename isolated doc/config files with no active references or only trivial text references. This can run in parallel across `.github/agents/`, `.github/prompts/`, `documentation/Gemini/`, and archive-only docs.
3. Phase 2, medium-risk renames: rename root and archive docs that are referenced by markdown links or prompt text, then update those references in the same change. This depends on step 1 and can run in parallel by area: root docs vs archive docs.
4. Phase 3, defer high-risk names: keep `nexus-mcp/`, `README.md`, `SESSION_SNAPSHOT_*.md`, and Python import structure unchanged unless there is an explicit refactor goal. These block on a broader migration plan because tooling assumes exact paths/patterns.
5. If implementation is approved later, execute renames in smallest possible batches and verify after each batch with text search for stale paths and broken links.

**Relevant files**
- `c:/Users/castn1.CORP/OneDrive - Wheels/dev.work/mcp_servers/.github/instructions/style.markdown.instructions.md` — repo rule requiring kebab-case for Markdown filenames.
- `c:/Users/castn1.CORP/OneDrive - Wheels/dev.work/mcp_servers/README.md` — references root docs such as DEMO_GUIDE.md.
- `c:/Users/castn1.CORP/OneDrive - Wheels/dev.work/mcp_servers/documentation/VSCODE_INTEGRATION_GUIDE.md` — contains hardcoded doc paths and `nexus-mcp` references.
- `c:/Users/castn1.CORP/OneDrive - Wheels/dev.work/mcp_servers/archive/README.md` — contains stale/hardcoded references such as Local-Setup naming.
- `c:/Users/castn1.CORP/OneDrive - Wheels/dev.work/mcp_servers/archive/Workday/Planning/workday-mcp-implementation-plan.md` — uses URL-encoded links to `CoPilot Generated ...` files.
- `c:/Users/castn1.CORP/OneDrive - Wheels/dev.work/mcp_servers/scripts/update_readme_status.py` — hardcodes `nexus-mcp` paths and snapshot filename patterns.
- `c:/Users/castn1.CORP/OneDrive - Wheels/dev.work/mcp_servers/.vscode/settings.json` — hardcodes `nexus-mcp` directory and PYTHONPATH.
- `c:/Users/castn1.CORP/OneDrive - Wheels/dev.work/mcp_servers/.vscode/launch.json` — hardcodes `nexus-mcp` program and working directory.
- `c:/Users/castn1.CORP/OneDrive - Wheels/dev.work/mcp_servers/nexus-mcp/pyproject.toml` — defines distribution/entry-point naming that should remain stable.

**Verification**
1. Use workspace text search for old filenames immediately after each rename batch; expected result is zero stale references except preserved historical notes.
2. Re-scan markdown links in `README.md`, `documentation/`, and `archive/` for renamed targets.
3. If any path under `nexus-mcp/` changes in a future refactor, validate `.vscode/settings.json`, `.vscode/launch.json`, `scripts/update_readme_status.py`, `scripts/bump_version.py`, and packaging metadata together.
4. Keep session snapshot glob behavior unchanged unless prompts and scripts are updated in the same batch.

**Decisions**
- Included scope: filename normalization audit and phased rename recommendations.
- Excluded scope: implementation, package refactor, import cleanup, or project directory rename.
- Keep `README.md` as a canonical exception.
- Keep `nexus-mcp` distribution and directory naming unchanged.

**Further Considerations**
1. Recommended target set for first cleanup batch: `.github/agents/Data Analyst.agent.md`, `.github/agents/SCCM Tutor.agent.md`, `.github/prompts/ITIL-Rooted Troubleshooting.prompt.md`, `documentation/Gemini/ChatFromVacation.md`, `archive/Identity/COPILOT-STUDIO-QUICKSTART.md`.
2. Recommended second batch: `DEMO_GUIDE.md`, `TOOL_INVENTORY.md`, `documentation/VSCODE_INTEGRATION_GUIDE.md`, and archive `CoPilot Generated ...` docs, but only with coordinated link updates.
3. Defer any rename touching `SESSION_SNAPSHOT_*.md`, `nexus-mcp/`, `lib/`, or Python modules until there is a separate refactor objective.