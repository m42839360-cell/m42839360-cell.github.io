default:
  just --list

# Local execution commands
fetch:
    ./scripts/fetch_commits.py

generate:
  ./scripts/generate_post.py

serve:
    bundle exec jekyll serve

# Docker commands
docker-build:
    docker build -t blog-automation:latest .

docker-serve:
    docker run -p 4000:4000 blog-automation:latest serve

docker-fetch:
    docker run -v $(pwd)/.env:/app/.env -v $(pwd)/data:/app/data blog-automation:latest fetch

docker-generate:
    docker run -v $(pwd)/data:/app/data -v $(pwd)/_posts:/app/_posts blog-automation:latest generate

docker-help:
    docker run blog-automation:latest