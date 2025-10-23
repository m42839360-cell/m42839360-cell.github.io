default:
  just --list

fetch:
    ./scripts/fetch_commits.py

generate:
  ./scripts/generate_post.py

serve:
    bundle exec jekyll serve