---
id: task-4
title: Python Script - Generate Post
status: To Do
assignee: []
created_date: '2025-10-20 08:20'
labels:
  - python
  - llm
  - jekyll
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create script to generate Jekyll blog posts from commit data using LLM API
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Create scripts/generate_post.py reading from data/commits.json
- [ ] #2 Read LLM configuration from config.yml
- [ ] #3 Construct LLM prompt with commit summaries grouped by repo and style instructions
- [ ] #4 Call LLM API (OpenAI) using API key from env var
- [ ] #5 Parse LLM response and generate Jekyll frontmatter
- [ ] #6 Create markdown file in _posts/ with format YYYY-MM-DD-title.md
- [ ] #7 Update .last_build timestamp file
- [ ] #8 Add --preview flag to output to stdout instead of file
- [ ] #9 Test locally with sample commit data
<!-- AC:END -->
