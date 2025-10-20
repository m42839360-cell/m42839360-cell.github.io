---
id: task-5
title: Local Automation Script
status: To Do
assignee: []
created_date: '2025-10-20 08:20'
labels:
  - python
  - automation
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create wrapper script to orchestrate full blog update workflow from fetching commits to building site
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Create scripts/run_blog_update.py wrapper script
- [ ] #2 Run fetch_commits.py and check if commits found
- [ ] #3 Run generate_post.py if commits exist
- [ ] #4 Optionally rebuild Jekyll site
- [ ] #5 Test full local workflow end-to-end
- [ ] #6 Verify Jekyll builds successfully after new post generation
- [ ] #7 Check generated posts display correctly
- [ ] #8 Validate RSS feed format
<!-- AC:END -->
