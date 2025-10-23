# Dockerfile for blog automation and Jekyll server
# This container runs:
# - fetch_commits.py and generate_post.py using uv
# - Jekyll server for blog serving

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

# Copy Jekyll configuration and content
COPY _config.yml ./
COPY _layouts/ ./_layouts/
COPY _includes/ ./_includes/
COPY _posts/ ./_posts/
COPY index.html ./
COPY assets/ ./assets/

# Copy automation scripts and config
COPY config.yml .
COPY .env.example .env
COPY scripts/ scripts/

# Create data directory
RUN mkdir -p data

# Expose Jekyll default port
EXPOSE 4000

# Create entrypoint script
RUN echo '#!/bin/bash\n\
if [ "$1" = "serve" ]; then\n\
    echo "Starting Jekyll server..."\n\
    exec bundle exec jekyll serve --host 0.0.0.0\n\
elif [ "$1" = "fetch" ]; then\n\
    shift\n\
    exec uv run scripts/fetch_commits.py "$@"\n\
elif [ "$1" = "generate" ]; then\n\
    shift\n\
    exec uv run scripts/generate_post.py "$@"\n\
else\n\
    echo "Blog Automation & Jekyll Server Container"\n\
    echo ""\n\
    echo "Available commands:"\n\
    echo "  serve                    - Start Jekyll server (port 4000)"\n\
    echo "  fetch [options]          - Run fetch_commits.py"\n\
    echo "  generate [options]       - Run generate_post.py"\n\
    echo ""\n\
    echo "Examples:"\n\
    echo "  docker run -p 4000:4000 <image> serve"\n\
    echo "  docker run -v \$(pwd)/.env:/app/.env -v \$(pwd)/data:/app/data <image> fetch"\n\
    echo "  docker run -v \$(pwd)/data:/app/data -v \$(pwd)/_posts:/app/_posts <image> generate"\n\
fi\n' > /entrypoint.sh && chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["help"]
