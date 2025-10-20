---
id: task-3
title: Python Script - Fetch Commits
status: To Do
assignee: []
created_date: '2025-10-20 08:20'
labels:
  - python
  - github-api
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create script to fetch GitHub commits since last run using GitHub API with rate limiting and pagination support
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Create scripts/fetch_commits.py with config.yml reading
- [ ] #2 Read last run timestamp from .last_build file or use lookback_days
- [ ] #3 Use GitHub API to fetch commits since last timestamp with filtering
- [ ] #4 Extract commit data: message, files changed, repo name, date, URL, author
- [ ] #5 Group commits by repository and output to data/commits.json
- [ ] #6 Handle API rate limiting and pagination
- [ ] #7 Add --dry-run flag to preview without writing
- [ ] #8 Test locally with own GitHub activity
<!-- AC:END -->
