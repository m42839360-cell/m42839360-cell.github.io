---
id: task-13
title: Update Configuration for GitHub
status: To Do
assignee: []
created_date: '2025-10-20 08:20'
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
