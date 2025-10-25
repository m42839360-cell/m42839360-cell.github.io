# Dockerfile for blog automation
# This container runs the complete blog update workflow:
# - Fetches commits from GitHub
# - Generates blog posts
# - Builds Jekyll static site
# The built site is served by a separate nginx container

FROM ruby:3.3-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

# Install system dependencies (Python, build tools, git)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-venv \
        curl \
        git \
        build-essential \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Create symlink for python command
RUN ln -s /usr/bin/python3 /usr/bin/python

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH (it installs to ~/.local/bin)
ENV PATH="/root/.local/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy Gemfile and install Jekyll dependencies
COPY Gemfile Gemfile.lock ./
RUN bundle install

# Copy Jekyll configuration and static content
# Note: _posts/ is NOT copied - it's generated dynamically and stored on volume
COPY _config.yml ./
COPY _layouts/ ./_layouts/
COPY index.html ./
COPY assets/ ./assets/

# Copy automation scripts
# Note: config.yml is NOT copied - it's provided at runtime via ConfigMap
COPY scripts/ scripts/

# Note: Environment variables (GITHUB_TOKEN, etc.) are injected at runtime via Kubernetes secrets
# Note: Persistent data (data/, _posts/, _site/, .last_build) stored on mounted volumes

# Create directories that will be volume mount points
RUN mkdir -p data _posts _site

# Default entrypoint runs the complete automation workflow
ENTRYPOINT ["scripts/run_blog_update.py"]
CMD []
