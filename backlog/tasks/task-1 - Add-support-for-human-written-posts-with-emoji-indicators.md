---
id: task-1
title: Add support for human-written posts with emoji indicators
status: To Do
assignee: []
created_date: '2025-11-13 13:39'
updated_date: '2025-11-13 13:50'
labels: []
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add functionality to distinguish between AI-generated posts (🤖) and human-written posts (👤). Human-written posts should be committed to the repository, while AI-generated posts remain uncommitted as they are auto-generated.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Post frontmatter includes an 'author_type' field (human or ai)
- [x] #2 AI-generated posts display 🤖 emoji in the post layout
- [x] #3 Human-written posts display 👤 emoji in the post layout
- [x] #4 Post list/index pages show emoji indicators for each post
- [x] #5 Human-written posts are NOT added to .gitignore
- [x] #6 AI-generated posts remain in .gitignore (jekyll/_posts/*.md pattern)
- [x] #7 Documentation explains how to create human-written posts

- [x] #8 Script extracts dates from git log (creation and last modified)
- [x] #9 Files not in git yet use current timestamp as fallback

- [x] #10 Dockerfile includes git (verify it's already installed)
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Update generate_post.py to add author_type: ai to all AI-generated posts
2. Create a new script/command to process human posts:
   - Scan jekyll/_posts/ for .md files without proper frontmatter
   - Use git log to determine dates:
     * Creation date: first commit that added the file
     * Last modified date: most recent commit that modified the file
   - Extract title from first # heading in the file or generate from filename
   - Generate and prepend Jekyll frontmatter with author_type: human
   - Use creation date for the post date field
   - Optionally add last_modified field if file was updated
   - Preserve the original markdown content
   - Handle files not yet in git (use current date as fallback)
3. Update Jekyll templates (post.html, index.html, archive.html):
   - Add emoji indicators based on author_type field
   - Show 🤖 for AI posts (default/missing author_type)
   - Show 👤 for human posts
   - Optionally show last_modified date if present
4. Integrate human post processing into run_blog_update.py workflow
5. Update documentation with examples
6. Create example human post to demonstrate the feature
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Successfully implemented human-written posts feature with emoji indicators.

## Implementation Summary

**Files Created:**
- src/roboblog/process_human_posts.py: New script to process bare markdown files
- jekyll/_posts/welcome-to-human-posts.md: Example human post

**Files Modified:**
- src/roboblog/generate_post.py: Added author_type: ai to AI-generated posts
- pyproject.toml: Added process-human-posts command
- src/roboblog/run_blog_update.py: Integrated human post processing as step 5
- jekyll/_layouts/post.html: Added emoji indicators and author type notices
- jekyll/index.html: Added emoji indicators to post listings
- jekyll/archive.html: Added emoji indicators to archive
- README.md: Added comprehensive documentation on writing human posts

## Key Features Delivered

1. **Git-based date extraction**: Uses git log to determine creation and last modified dates
2. **Automatic frontmatter generation**: Processes bare markdown files without manual YAML
3. **Emoji indicators**: 🤖 for AI posts, 👤 for human posts throughout the site
4. **Workflow integration**: Human posts processed before Jekyll build
5. **Update tracking**: last_modified field added when files are updated
6. **Fallback handling**: Uses current time if file not yet in git

## Testing Notes

To test:
1. Create a bare markdown file in jekyll/_posts/
2. Commit it to git
3. Run: uv run process-human-posts
4. Or run full workflow: uv run run-blog-update

The system will automatically add frontmatter and the post will display with 👤 emoji.
<!-- SECTION:NOTES:END -->
