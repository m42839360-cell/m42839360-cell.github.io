---
id: task-23
title: Update Helm chart and Dockerfile for roboblog automation
status: Done
assignee:
  - '@claude'
created_date: '2025-10-24 09:18'
updated_date: '2025-10-24 09:25'
labels: []
dependencies: []
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The roboblog container should run scripts/run_blog_update.py to automate blog post generation. Environment variables need to be mounted as secrets, and all relevant files (commits data, generated posts, Jekyll site) must be stored on the shared volume for persistence.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Container runs scripts/run_blog_update.py as main process
- [x] #2 Environment variables (GITHUB_TOKEN, etc.) are mounted as Kubernetes secrets
- [x] #3 Shared volume is configured to persist data/ directory
- [x] #4 Shared volume is configured to persist _posts/ directory
- [x] #5 Shared volume is configured to persist _site/ directory
- [x] #6 .last_build timestamp file is persisted on shared volume
- [x] #7 Dockerfile is updated with correct entrypoint
- [x] #8 Helm chart values include secret references
- [x] #9 Helm chart includes volume mount configurations
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Update Dockerfile to use scripts/run_blog_update.py as the main entrypoint
   - Remove Jekyll serve functionality (nginx handles serving)
   - Remove _posts/ from COPY instructions (generated dynamically)
   - Set entrypoint to run the automation script

2. Create Kubernetes Secret template for environment variables
   - Add secret.yaml template for GITHUB_TOKEN and other env vars
   - Reference in cronjob for env injection

3. Expand volume mount configuration
   - Mount shared volume for: data/, _posts/, _site/, and .last_build
   - Ensure proper subPath configurations

4. Update CronJob to run the automation workflow
   - Change command from jekyll build to scripts/run_blog_update.py
   - Add environment variable references from secret
   - Configure volume mounts for all persistence paths

5. Update values.yaml
   - Add secrets configuration section
   - Adjust volume mount paths and subPaths
   - Update resource limits if needed

6. Test the configuration with dry-run
   - Validate Helm template rendering
   - Check volume mount paths
   - Verify secret references
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Updated Dockerfile and Helm chart to run the complete blog automation workflow via scripts/run_blog_update.py.

## Changes Made

### Dockerfile (roboblog-chart/Dockerfile)
- Changed entrypoint from multi-command script to `scripts/run_blog_update.py`
- Removed `_posts/` from COPY instructions (now generated dynamically)
- Removed Jekyll serve functionality (nginx handles serving)
- Added volume mount point directories: data/, _posts/, _site/
- Updated comments to reflect automation-only purpose

### Helm Chart - Secret Management (roboblog-chart/templates/secret.yaml)
- Created new Secret template for environment variables
- Supports GITHUB_TOKEN and additional custom variables
- Uses base64 encoding for secret data
- Configurable via values.yaml secrets section

### Helm Chart - Values (roboblog-chart/values.yaml)
- Added secrets configuration section with githubToken and extra fields
- Updated CronJob description to reflect automation workflow
- Added documentation about proper secret handling

### Helm Chart - CronJob (roboblog-chart/templates/cronjob.yaml)
- Renamed container from jekyll-builder to blog-automation
- Changed from manual jekyll build to Dockerfile entrypoint
- Added envFrom to inject secrets as environment variables
- Configured volume mounts for all persistence paths:
  - /app/data (subPath: data) - commits.json storage
  - /app/_posts (subPath: _posts) - generated blog posts
  - /app/_site (subPath: _site) - built Jekyll site for nginx
  - /app/.last_build (subPath: .last_build) - timestamp tracking

## Testing
- Helm template renders successfully without errors
- Docker build completes successfully
- Container entrypoint executes run_blog_update.py correctly
- All volume mounts configured with proper subPaths

## Deployment Notes
When deploying, provide the GitHub token via:
```bash
helm install roboblog ./roboblog-chart --set secrets.githubToken=<your-token>
```

Or create a separate secrets.yaml file (not committed to git):
```yaml
secrets:
  githubToken: "ghp_your_token_here"
```

Then deploy with:
```bash
helm install roboblog ./roboblog-chart -f secrets.yaml
```
<!-- SECTION:NOTES:END -->
