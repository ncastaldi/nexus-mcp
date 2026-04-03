"I am working with the Frank Meadows agentic framework to prepare a sensitive production script for my public GitHub portfolio. I need to perform a Sanitization and Atomic Refactor of the attached RBAC Governance script.

The Objectives:

Data Masking: Replace all internal company names, tenant IDs, specific Entra ID (Azure AD) group names, and API keys with generic placeholders.

Security Hardening: Ensure the script uses environment variables (e.g., os.getenv or $env:) instead of hardcoded credentials.

Validation Check: Ensure the logic includes error-handling for API timeouts or 'not found' objects, as per the Frank Meadows core directives.

The Workflow Instructions:

Gated Workflow: Do NOT output the entire scrubbed script at once. We will move through the script in functional blocks.

Atomic Edits: For each block, provide the refactored code and wait for my 'Approved' or 'Modify' signal before moving to the next block.

The First Gate: Please acknowledge these constraints and ask me to provide the first block of code (Imports and Connection/Authentication logic) to begin the sanitization process."