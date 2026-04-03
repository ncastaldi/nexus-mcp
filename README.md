# MCP servers

## Repository intent

This repository defines MCP servers and implementation guides that support
enterprise identity operations across multiple systems.

- Identity: provides a production-oriented read path for AD user and group data,
	with adapters, server wiring, and tests.
- Workday: defines the Workday-to-AD identity sync implementation approach,
	phased delivery, and operational controls.
- Intune: captures deployment prerequisites and planning artifacts for endpoint
	management integrations.

## Current workflow intent

The active workflow is focused on delivering a controlled Workday-to-AD sync
capability that:

- Uses Workday as source of truth for worker lifecycle state.
- Uses Identity MCP as the downstream enforcement and validation interface.
- Starts read-only, then introduces approval-gated remediation actions.
- Tracks measurable outcomes, including drift reduction and provisioning speed.

## Progress snapshot (2026-04-03)

### Completed

- Workday execution backlog created: [Workday/workday-ad-identity-sync-next-steps.md](Workday/workday-ad-identity-sync-next-steps.md).
- Sprint-ready board created: [Workday/workday-ad-identity-sync-sprint-board.md](Workday/workday-ad-identity-sync-sprint-board.md).
- Identity MCP baseline is in place with code and tests under [Identity](Identity/).

### In progress

- Converting strategy into sprint-trackable work items (WIS-001 to WIS-030).
- Preparing dependency closure sequence for auth, non-prod access, and data
	contract controls.

### Next milestones

- Q2 milestone 1: close blockers and validate non-prod read-only path.
- Q2 milestone 2: implement core Workday MCP tools and mismatch detection.
- Q2 milestone 3: enable daily sync checks with ticketed approval workflow.
- Q3 milestones: drift reporting, production rollout, and >=30% MTTP
	reduction versus Q1 baseline.

## Key documents

- [Workday/workday-ad-identity-sync-next-steps.md](Workday/workday-ad-identity-sync-next-steps.md)
- [Workday/workday-ad-identity-sync-sprint-board.md](Workday/workday-ad-identity-sync-sprint-board.md)
- [Identity/implementation-guide.md](Identity/implementation-guide.md)
- [Identity/copilot-studio-deployment-guide.md](Identity/copilot-studio-deployment-guide.md)
