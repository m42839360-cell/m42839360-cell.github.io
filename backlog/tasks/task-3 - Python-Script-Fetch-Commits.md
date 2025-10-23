---
id: task-3
title: Python Script - Fetch Commits
status: Done
assignee:
  - '@claude'
created_date: '2025-10-20 08:20'
updated_date: '2025-10-23 07:18'
labels:
  - python
  - github-api
dependencies: []
priority: high
ordinal: 14000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create script to fetch GitHub commits since last run using GitHub API with rate limiting and pagination support
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create scripts/fetch_commits.py with config.yml reading
- [x] #2 Read last run timestamp from .last_build file or use lookback_days
- [x] #3 Use GitHub API to fetch commits since last timestamp with filtering
- [x] #4 Extract commit data: message, files changed, repo name, date, URL, author
- [x] #5 Group commits by repository and output to data/commits.json
- [x] #6 Handle API rate limiting and pagination
- [x] #7 Add --dry-run flag to preview without writing
- [x] #8 Test locally with own GitHub activity
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Check Python environment and required packages (requests, pyyaml)
2. Create scripts/ directory structure
3. Implement config reader to load config.yml and .env
4. Implement timestamp tracking (.last_build file read/write)
5. Implement GitHub API client with authentication and rate limiting
6. Implement commit fetching with pagination and filtering
7. Implement data extraction (message, files, repo, date, URL, author)
8. Implement repository grouping and JSON output to data/commits.json
9. Add --dry-run flag for preview mode
10. Test with real GitHub data and verify output format
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Implementation Summary

Created `scripts/fetch_commits.py` as a standalone UV-managed Python script with PEP 723 inline dependencies.

### Key Features Implemented

- **Configuration Management**: `ConfigReader` class loads settings from `config.yml` and optional `.env` file
- **Timestamp Tracking**: `TimestampTracker` class manages `.last_build` file to track last run time
- **GitHub API Client**: `GitHubAPIClient` class with:
  - Token-based authentication (optional, falls back to 60 req/hour)
  - Automatic rate limit checking and handling
  - Pagination support for fetching all user events
  - Detailed commit info retrieval including file changes
- **Commit Processing**: `CommitProcessor` class with:
  - Event filtering by timestamp
  - Repository filtering (include/exclude lists)
  - Extraction of commit metadata (message, files, author, date, URL)
  - File change statistics (additions, deletions, changes)
  - Repository grouping for organized output
- **CLI Features**:
  - `--dry-run` flag for preview without writing files
  - `--config` flag to specify custom config path
  - `--output` flag to specify custom output path
  - Detailed progress output with status indicators

### Technical Details

- Uses UV shebang: `#!/usr/bin/env -S uv run --script`
- Dependencies: `requests>=2.31.0`, `pyyaml>=6.0.0`, `python-dotenv>=1.0.0`
- Requires Python >= 3.11
- Outputs JSON to `data/commits.json` with structure:
  ```json
  {
    "fetched_at": "ISO timestamp",
    "since": "ISO timestamp",
    "total_commits": 0,
    "repositories": {
      "owner/repo": [/* commits */]
    }
  }
  ```

### Testing

- Tested with `--dry-run` flag successfully
- Script correctly handles missing `.env` file
- Rate limiting detection works
- JSON output structure validated

### Files Modified

- Created: `scripts/fetch_commits.py` (executable)
- No other files modified
<!-- SECTION:NOTES:END -->
