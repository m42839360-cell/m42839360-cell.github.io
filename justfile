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

# Development commands
fmt:
  uv run ruff format src/

lint:
  uv run ruff check src/

check:
  uv run ruff check --fix src/
