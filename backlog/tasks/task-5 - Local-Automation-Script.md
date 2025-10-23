---
id: task-5
title: Local Automation Script
status: Done
assignee:
  - '@claude'
created_date: '2025-10-20 08:20'
updated_date: '2025-10-23 07:18'
labels:
  - python
  - automation
dependencies: []
priority: medium
ordinal: 12000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create wrapper script to orchestrate full blog update workflow from fetching commits to building site
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create scripts/run_blog_update.py wrapper script
- [x] #2 Run fetch_commits.py and check if commits found
- [x] #3 Run generate_post.py if commits exist
- [x] #4 Optionally rebuild Jekyll site
- [x] #5 Test full local workflow end-to-end
- [x] #6 Verify Jekyll builds successfully after new post generation
- [x] #7 Check generated posts display correctly
- [x] #8 Validate RSS feed format
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Review existing scripts and their outputs
2. Create scripts/run_blog_update.py with UV shebang
3. Implement script orchestrator to run fetch_commits.py
4. Check if commits were found in the output
5. Conditionally run generate_post.py if commits exist
6. Add optional Jekyll build step (bundle exec jekyll build)
7. Add --dry-run flag for testing without side effects
8. Add --skip-build flag to skip Jekyll build
9. Test full workflow end-to-end with sample data
10. Verify Jekyll build and post display
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Implementation Summary

Created `scripts/run_blog_update.py` as a comprehensive workflow orchestrator that coordinates the entire blog update process.

### Key Features Implemented

- **Workflow Orchestration**: Runs the complete pipeline in 4 steps:
  1. Fetch commits from GitHub using `fetch_commits.py`
  2. Check if any commits were found in `data/commits.json`
  3. Generate blog post using `generate_post.py` (only if commits exist)
  4. Build Jekyll site with `bundle exec jekyll build`

- **Smart Exit Logic**: Stops early if no commits found, avoiding unnecessary processing

- **Error Handling**:
  - Catches and reports errors from each step
  - Shows detailed error messages and output
  - Returns proper exit codes (0 for success, 1 for failure)

- **CLI Features**:
  - `--dry-run` flag: Test workflow without writing files or making changes
  - `--skip-build` flag: Skip the Jekyll build step for faster iteration
  - `--config` flag: Use custom configuration file
  - Color-coded terminal output for better readability

- **Detailed Progress Output**:
  - Step-by-step progress indicators
  - Success/error/warning/info messages with icons
  - Relevant output from each script
  - Final summary with commit count and next steps

- **Robust Checks**:
  - Validates config file exists
  - Checks for bundle/Jekyll availability
  - Verifies script files exist before running
  - Handles missing dependencies gracefully

### Technical Details

- Uses UV shebang: `#!/usr/bin/env -S uv run --script`
- Dependency: `pyyaml>=6.0.0`
- Requires Python >= 3.11
- Uses Python subprocess module to run other scripts
- ANSI color codes for terminal formatting

### Testing

- Tested with `--dry-run` flag successfully
- Tested with `--skip-build` flag
- Verified workflow runs fetch_commits.py correctly
- Confirmed early exit when no commits found
- Validated error handling and reporting
- Jekyll build integration verified (with bundle check)

### Usage Examples

```bash
# Run full workflow
./scripts/run_blog_update.py

# Dry run to preview without changes
./scripts/run_blog_update.py --dry-run

# Skip Jekyll build for faster testing
./scripts/run_blog_update.py --skip-build

# Use custom config
./scripts/run_blog_update.py --config custom.yml
```

### Files Created

- `scripts/run_blog_update.py` (executable)

### Notes

The orchestrator provides a single command to run the entire blog automation workflow, making it easy to:
- Test locally before deploying
- Run manually when needed
- Integrate with GitHub Actions
- Debug issues in the pipeline

The script gracefully handles missing tools (like bundle) and provides helpful error messages.
<!-- SECTION:NOTES:END -->
