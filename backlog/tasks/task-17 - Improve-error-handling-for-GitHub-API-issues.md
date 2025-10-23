---
id: task-17
title: Improve error handling for GitHub API issues
status: Done
assignee:
  - '@claude'
created_date: '2025-10-20 09:56'
updated_date: '2025-10-23 07:18'
labels:
  - enhancement
  - error-handling
  - github-api
dependencies: []
priority: high
ordinal: 7000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add better error messages when GitHub token is invalid or commits can't be fetched, helping users debug authentication and API issues more easily
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Detect and report invalid GitHub token with clear error message
- [x] #2 Show helpful message when API returns 401/403 errors
- [x] #3 Provide guidance on how to fix token issues (regenerate, check scopes)
- [x] #4 Detect when Events API returns empty commit payloads
- [x] #5 Add validation for token format before making API calls
- [x] #6 Test error handling with invalid token
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Implementation Summary

Added comprehensive error handling for GitHub API issues in fetch_commits.py.

### Error Handling Improvements

**1. Token Validation**
- Added `validate_token()` method to GitHubAPIClient
- Tests authentication before making API calls
- Returns detailed error messages for failures

**2. Invalid Token Detection (401 Error)**
- Detects "Bad credentials" responses
- Shows clear error message with step-by-step fix instructions:
  - Where to generate new token (GitHub settings)
  - Required scopes (public_repo or repo)
  - How to update .env file
  - Common formatting mistakes to avoid

**3. Permission Issues (403 Error)**
- Detects insufficient token scopes
- Explains how to add required scopes
- Provides direct link to token settings

**4. Empty Commit Payload Detection**
- Tracks push events vs commits found
- Warns when all push events have empty payloads
- Explains GitHub Events API limitations
- Provides troubleshooting steps

**5. Network Error Handling**
- Catches RequestException errors
- Shows warnings but continues if validation fails
- Graceful degradation for network issues

### Error Messages

All error messages follow a consistent format:
- Clear header with ✗ or ⚠ indicator
- Explanation of the problem
- Step-by-step fix instructions
- Relevant URLs and examples
- Formatting guidelines

### Testing Results

Tested with:
- ✓ Valid token: Shows username validation
- ✓ Invalid token: Shows detailed error with fix steps
- ✓ Empty commit payloads: Shows warning with explanation
- ✓ Network issues: Graceful handling

### User Experience

Before:
- Silent failures or cryptic errors
- No guidance on how to fix issues
- Unclear why commits not found

After:
- Clear error messages
- Step-by-step fix instructions
- URLs to relevant documentation
- Format validation guidance
- Helpful warnings for edge cases

### Files Modified

- `scripts/fetch_commits.py`:
  - Added `validate_token()` method
  - Added token validation in main()
  - Added empty payload detection
  - Added comprehensive error messages

### Code Quality

- Error messages are user-friendly
- Includes actionable fix steps
- Validates before making expensive API calls
- Graceful degradation
- Helpful warnings without blocking execution
<!-- SECTION:NOTES:END -->
