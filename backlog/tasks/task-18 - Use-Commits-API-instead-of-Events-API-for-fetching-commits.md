---
id: task-18
title: Use Commits API instead of Events API for fetching commits
status: Done
assignee:
  - '@claude'
created_date: '2025-10-20 10:56'
updated_date: '2025-10-23 07:18'
labels:
  - enhancement
  - github-api
  - reliability
dependencies: []
priority: high
ordinal: 6000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Replace the Events API approach with direct Commits API calls to reliably fetch commit data. The Events API has limitations and doesn't always include commit details in payloads, even with authentication. Using the Commits API directly will be more reliable and provide complete commit information.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Fetch user repositories using /user/repos endpoint
- [x] #2 For each repository, fetch commits using /repos/{owner}/{repo}/commits
- [x] #3 Filter commits by date range (since parameter)
- [x] #4 Apply repository filters (include/exclude lists)
- [x] #5 Extract commit details (message, files, author, stats)
- [x] #6 Maintain backward compatibility with existing config
- [x] #7 Handle pagination for repositories and commits
- [x] #8 Implement rate limiting for multiple API calls
- [x] #9 Test with repositories having many commits
- [x] #10 Verify performance and API rate limit usage
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Review current Events API implementation
2. Design new Commits API approach
3. Add method to fetch user repositories
4. Add method to fetch commits per repository with pagination
5. Implement date range filtering with since parameter
6. Apply repository filters (include/exclude)
7. Extract commit details with file changes
8. Add rate limiting between API calls
9. Update main workflow to use new approach
10. Test with real repositories and verify results
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
# Implementation Summary

Successfully migrated from GitHub Events API to Commits API for more reliable commit fetching.

## Changes Made

### 1. New API Methods in GitHubAPIClient (lines 240-345)
- **get_user_repos()**: Fetches all repositories for a user with pagination
  - Sorts by "pushed" (most recently updated first)
  - Filters by "owner" type (user's own repos)
  - Handles pagination (100 repos per page)
  - Includes rate limiting (0.5s between pages)

- **get_repo_commits()**: Fetches commits for a specific repository
  - Uses "since" parameter for date filtering
  - Handles pagination (100 commits per page)
  - Returns empty list for 404 (not found/no access)
  - Includes rate limiting (0.3s between pages)

### 2. New Processing Method in CommitProcessor (lines 496-597)
- **fetch_commits_direct()**: Main method for Commits API approach
  - Fetches all user repositories
  - Applies repository filters (include/exclude lists)
  - For each repository, fetches commits since specified date
  - Gets detailed commit info including files and stats
  - Deduplicates commits by SHA
  - Progress feedback for each repository

### 3. Updated Main Workflow (lines 670-678)
- Replaced `get_user_events()` + `extract_commits()` with `fetch_commits_direct()`
- Simplified workflow while maintaining all functionality
- Added comment explaining migration to Commits API

## Testing Results

Tested with user "maluio" (60-day lookback):
- ✓ Successfully fetched 33 repositories
- ✓ Applied filters correctly (excluded m42839360-cell.github.io)
- ✓ Found 71 commits across 2 repositories
- ✓ All commits include detailed file changes and statistics
- ✓ Proper pagination and rate limiting
- ✓ Token validation working correctly

Example commit data:
- Files: filename, status, additions, deletions, changes
- Stats: total additions, deletions, and changes
- Metadata: SHA, message, author, date, repository, URL

## Benefits Over Events API

1. **Reliability**: Direct API calls instead of event payloads
2. **Completeness**: Always includes file details and statistics
3. **Transparency**: Clear progress feedback per repository
4. **Efficiency**: Fetches only commits within date range
5. **Maintainability**: Simpler code flow, easier to debug

## Performance

- API calls: ~33 repos + ~71 commits = ~104 API calls
- Rate limiting: 0.5s per repo page, 0.3s per commit detail
- Estimated time for 60-day fetch: ~30-40 seconds
- Well within GitHub API rate limits (5000/hour with token)

## Backward Compatibility

✓ No config changes required
✓ Same output format (data/commits.json)
✓ Works with all existing scripts (generate_post.py, run_blog_update.py)
✓ Preserves all filtering and configuration options
<!-- SECTION:NOTES:END -->
