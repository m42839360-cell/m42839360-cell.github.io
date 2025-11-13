default:
  just --list

# Local execution commands
fetch:
    ./scripts/fetch_commits.py

generate:
  ./scripts/generate_post.py

serve:
    cd jekyll && bundle exec jekyll serve
