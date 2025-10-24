---
id: task-24
title: Mount config.yml from ConfigMap in Helm chart
status: Done
assignee:
  - '@claude'
created_date: '2025-10-24 09:43'
updated_date: '2025-10-24 09:47'
labels: []
dependencies: []
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The config.yml file should be provided via a Kubernetes ConfigMap instead of being baked into the Docker image. This allows for runtime configuration changes without rebuilding the image.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create ConfigMap template for config.yml in Helm chart
- [x] #2 Add config.yml content to values.yaml
- [x] #3 Mount ConfigMap as volume in CronJob
- [x] #4 Update Dockerfile to not copy config.yml (use mounted version)
- [x] #5 ConfigMap mounted at /app/config.yml path
- [x] #6 Test Helm template rendering with ConfigMap
- [x] #7 Verify config.yml is properly accessible in container
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Create ConfigMap template in roboblog-chart/templates/configmap-config.yaml
   - Use values.yaml to populate config.yml content
   - Make all settings configurable via Helm values

2. Add config section to values.yaml
   - Mirror current config.yml structure
   - Use current config.yml as default values
   - Document each configuration option

3. Update CronJob template to mount ConfigMap
   - Add volume definition for config ConfigMap
   - Add volumeMount to /app/config.yml path
   - Use subPath to mount as a file (not directory)

4. Update Dockerfile
   - Remove COPY config.yml line
   - Add comment explaining config.yml is provided at runtime

5. Test Helm template rendering
   - Verify ConfigMap renders correctly
   - Check volume mounts in CronJob
   - Validate config.yml content in rendered template
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Migrated config.yml from being baked into the Docker image to a Kubernetes ConfigMap for runtime configuration.

## Changes Made

### ConfigMap Template (roboblog-chart/templates/configmap-config.yaml)
- Created new ConfigMap template for blog automation configuration
- Mirrors complete config.yml structure
- Uses Helm values to populate all settings
- Properly handles YAML arrays and nested structures

### Values Configuration (roboblog-chart/values.yaml)
- Added comprehensive config section with all blog automation settings:
  - GitHub: username, repo filters, exclude repos
  - LLM: provider, model, API key env var, style, tokens, temperature
  - Automation: lookback days, min/max commits, frequency
  - Blog: title template, code snippets, stats, tags, author
- Used camelCase for Helm values (e.g., repoFilters, maxTokens)
- Documented all configuration options with comments

### CronJob Updates (roboblog-chart/templates/cronjob.yaml)
- Added config-volume volume definition referencing ConfigMap
- Added volumeMount for config.yml at /app/config.yml
- Used subPath to mount as file (not directory)
- Set readOnly: true for config mount

### Dockerfile Updates
- Removed COPY config.yml line
- Added comment explaining config.yml is provided via ConfigMap at runtime

## Testing Results
- Helm template renders without errors
- ConfigMap contains properly formatted YAML config
- Volume mounts correctly configured in CronJob:
  - /app/config.yml mounted from ConfigMap
  - All existing mounts (data, _posts, _site, .last_build) preserved
- Config values correctly interpolated from values.yaml

## Benefits
- Configuration changes without image rebuilds
- Environment-specific configs (dev/staging/prod)
- Easy to customize via Helm values or separate values files
- Follows Kubernetes best practices for configuration management

## Usage Example
```bash
# Override specific config values
helm install roboblog ./roboblog-chart \
  --set config.llm.model=gpt-4o \
  --set config.automation.lookbackDays=14

# Or use custom values file
helm install roboblog ./roboblog-chart -f custom-config.yaml
```
<!-- SECTION:NOTES:END -->
