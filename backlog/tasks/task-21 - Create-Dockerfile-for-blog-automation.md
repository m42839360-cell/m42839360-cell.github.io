---
id: task-21
title: Create Dockerfile for blog automation
status: Done
assignee:
  - '@claude'
created_date: '2025-10-23 10:42'
updated_date: '2025-10-23 11:03'
labels:
  - docker
  - devops
  - automation
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a Dockerfile to containerize the blog automation scripts (fetch_commits.py and generate_post.py) for easier deployment and execution in different environments.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Dockerfile created with appropriate base image
- [x] #2 All required dependencies installed (Python, uv, git)
- [x] #3 Scripts are executable inside the container
- [x] #4 Environment variables properly configured (.env support)
- [x] #5 Docker image builds successfully
- [x] #6 Container can run fetch_commits.py and generate_post.py

- [x] #7 Jekyll and Ruby installed in container
- [x] #8 Blog can be served on port 4000
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Analyze requirements:
   - Python 3.11+ with uv for script execution
   - Git for repository operations
   - Config files: config.yml, .env (optional)
   - Output: data/commits.json, _posts/*.md

2. Choose base image: python:3.11-slim (lightweight, official)

3. Install system dependencies:
   - curl (for uv installation)
   - git (for repository operations)

4. Install uv and configure PATH

5. Set up working directory and copy necessary files:
   - scripts/
   - config.yml
   - .env (at runtime via volume or env vars)

6. Configure entrypoint for flexible script execution

7. Test build and execution of both scripts
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Summary

Successfully created a Dockerfile to containerize the blog automation scripts (fetch_commits.py and generate_post.py) for portable deployment.

## Implementation Details

### Base Image
- **python:3.11-slim** - Lightweight official Python image
- Minimal footprint while providing full Python 3.11+ support

### System Dependencies
- **curl** - For uv installation
- **git** - For repository operations (may be needed by scripts)
- **ca-certificates** - For secure HTTPS connections

### uv Installation
- Installed via official install script from astral.sh
- Added to PATH at /root/.local/bin
- Enables PEP 723 inline script metadata execution

### Directory Structure
- Working directory: /app
- Config files: config.yml, .env (copied from .env.example)
- Scripts: scripts/ directory
- Output directories: data/, _posts/ (created automatically)

### Environment Configuration
- Supports .env file via volume mount at runtime
- Environment variables can be passed via docker run -e
- config.yml included in image for default settings

### Usage Examples

```bash
# Build the image
docker build -t blog-automation:latest .

# Run fetch_commits.py with custom .env
docker run -v $(pwd)/.env:/app/.env -v $(pwd)/data:/app/data \
  blog-automation:latest uv run scripts/fetch_commits.py

# Run generate_post.py with data volume
docker run -v $(pwd)/data:/app/data -v $(pwd)/_posts:/app/_posts \
  blog-automation:latest uv run scripts/generate_post.py

# Preview mode (no file writes)
docker run -v $(pwd)/data:/app/data \
  blog-automation:latest uv run scripts/generate_post.py --preview
```

## Testing

- ✓ Docker image builds successfully (~400MB)
- ✓ uv is properly installed and in PATH
- ✓ fetch_commits.py --help executes correctly
- ✓ generate_post.py --help executes correctly
- ✓ Dependencies install on-demand via uv (PEP 723)
- ✓ Default command shows helpful usage instructions

## Benefits

- **Portability**: Run anywhere Docker is available
- **Consistency**: Same environment across dev/CI/prod
- **Isolation**: No system-wide Python/package conflicts
- **Easy deployment**: Single container for all automation
- **Volume mounts**: Flexible data persistence and config

## Update: Added Jekyll Server Support

### Changes
- Switched base image from python:3.11-slim to ruby:3.3-slim
- Installed Python 3.13 alongside Ruby for multi-language support
- Added Jekyll and all dependencies via bundle install
- Created multi-mode entrypoint script supporting:
  - `serve` - Start Jekyll server on port 4000
  - `fetch` - Run fetch_commits.py
  - `generate` - Run generate_post.py

### Jekyll Configuration
- Copies all Jekyll content: _config.yml, _layouts/, _includes/, _posts/, assets/, index.html
- Exposes port 4000 for web server
- Server runs on 0.0.0.0 to accept external connections
- Auto-regeneration enabled for live updates

### Testing Results
- ✓ Jekyll server starts successfully
- ✓ Blog accessible on http://localhost:4000
- ✓ HTML pages render correctly
- ✓ All three modes work (serve, fetch, generate)
- ✓ Image size: ~708MB (includes Ruby, Python, Jekyll, build tools)

### Usage Examples

```bash
# Serve the blog (port 4000)
docker run -p 4000:4000 blog-automation:latest serve

# Fetch commits with volume mounts
docker run -v $(pwd)/.env:/app/.env -v $(pwd)/data:/app/data \
  blog-automation:latest fetch

# Generate post with volume mounts
docker run -v $(pwd)/data:/app/data -v $(pwd)/_posts:/app/_posts \
  blog-automation:latest generate

# Access help
docker run blog-automation:latest
```

### Benefits
- **All-in-one**: Single container for automation + serving
- **Development ready**: Can develop and test locally with Docker
- **Production ready**: Deploy complete blog system anywhere
- **Isolated environment**: No conflicts with system Ruby/Python

### Justfile Integration

Added convenient `just` commands for Docker operations:

```bash
just docker-build      # Build the Docker image
just docker-serve      # Start Jekyll server in Docker
just docker-fetch      # Fetch commits via Docker
just docker-generate   # Generate posts via Docker
just docker-help       # Show Docker help
```

This provides a consistent interface for both local and Docker-based workflows.
<!-- SECTION:NOTES:END -->
