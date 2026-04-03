Act as a Senior Technical Program Manager. I need to update the `README.md` for my 'Workday-MCP' project to serve as a high-visibility Status Page. 

## CONTEXT
### Phase 1: Context Retrieval (RAG)
**Execute these lookups to ground your analysis:**
1.  **Get the "What" (Code):**
    * Run: `git diff --cached` (If empty, warn user to stage files first).
2.  **Get the "Why" (Intent):**
    * **Search Workspace:** Find the most recent `SESSION_SNAPSHOT*.md` in `documentation/project-history/`.
    * **Search Workspace:** Look for `TODO` or `// RESTART NOTE` comments in the changed files themselves.
    * *Reasoning:* A commit message is better if it says "feat(auth): enable TFA per session plan" rather than just "feat(auth): update config".

### Phase 2: Change Analysis (Chain of Thought)
*Reference: `.github/knowledge/example.CoT-Prompting.md`*

Analyze the combined inputs (Diff + Session Context):
1.  **Component Determination:** Identify which major component(s) of the project are affected (e.g., `core`, `auth`, `docs`).
2.  **Scope/WIS Identification:** Narrow to the specific module (e.g., `core`, `auth`, `docs`) and align with WIS IDs for traceability.
3.  **Breaking Change Check:** Does this modify `compose.yaml` ports or volume paths? If yes, flag as `BREAKING CHANGE`.

## REQUIREMENTS
1. **Visual Status:** Use a "Traffic Light" system for project components:
   - 🟢 Green: Functional/Production-Ready
   - 🟡 Yellow: In Progress/Development
   - 🔴 Red: Blocked/Not Started
2. **Standardization:** Ensure the README reflects our "Discipline Drives Quality" pillar (e.g., mention Type Hinting, Pylance-zero-error status, and modular structure).
3. **Sprint Alignment:** Reference the WIS (Workday Integration Suite) IDs to maintain traceability to our 2026 roadmap.
4. **Readability:** Use clean Markdown tables and bold headers for scannability.

## INPUT DATA
[PASTE YOUR CURRENT README HERE]

## RECENT ACTIVITY
[PASTE YOUR RECENT GIT LOG OR SUMMARY HERE]