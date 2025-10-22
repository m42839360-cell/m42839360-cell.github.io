---
id: task-13
title: Update Configuration for GitHub
status: To Do
assignee:
  - '@claude'
created_date: '2025-10-20 08:20'
updated_date: '2025-10-22 12:06'
labels:
  - config
  - github-actions
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Adapt configuration system for GitHub Actions environment with secrets and timestamp persistence
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Move update_interval to workflow cron schedule
- [ ] #2 Remove API keys from config.yml (use secrets only)
- [ ] #3 Update config.yml.example with safe defaults
- [ ] #4 Ensure .last_build is tracked in git or use alternative (releases/tags)
- [ ] #5 Test that timestamp persistence works across workflow runs
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Review current config.yml for API keys and sensitive data (none found - already using env vars)
2. Update config.yml comments to clarify GitHub Actions usage
3. Add note about frequency being handled by workflow cron schedule
4. Create config.yml.example as a template for users
5. Check .last_build handling - currently in .gitignore, evaluate if it should be tracked
6. Update .gitignore if needed for timestamp persistence
7. Update documentation to explain configuration approach
8. Mark acceptance criteria complete
<!-- SECTION:PLAN:END -->
