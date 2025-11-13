default:
  just --list

# Install dependencies
install:
  uv sync

# Local execution commands
fetch:
  uv run fetch-commits

generate:
  uv run generate-post

run:
  uv run run-blog-update

serve:
  cd jekyll && bundle exec jekyll serve

# Example mode commands (use mock data instead of GitHub API)
example:
  uv run run-blog-update --example --skip-build

# Development commands
fmt:
  uv run ruff format src/

lint:
  uv run ruff check src/

check:
  uv run ruff check --fix src/
