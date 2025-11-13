# Dev Blog - Automated Commit-Based Blog Posts

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Active-brightgreen)](https://m42839360-cell.github.io)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)

Automatically generates blog posts from your GitHub commits using AI and publishes to GitHub Pages.

## Setup on GitHub (5 minutes)

### 1. Fork & Configure

```bash
# Fork this repo, then:
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

# Update config.yml
cp config.yml.example config.yml
# Edit: Set your GitHub username, choose LLM provider (openai/anthropic)
```

### 2. Get API Key

- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/

### 3. Enable GitHub Pages

- Go to **Settings** → **Pages**
- Source: **Deploy from a branch**
- Branch: **main** / **(root)**
- Click **Save**

### 4. Add Secrets

- Go to **Settings** → **Secrets and variables** → **Actions**
- Click **New repository secret**
- Add `LLM_API_KEY`: Paste your API key
- (Optional) Add `GITHUB_TOKEN`: Personal access token for higher rate limits

### 5. Run First Workflow

- Go to **Actions** tab
- Click **"Automated Blog Post Generation"**
- Click **"Run workflow"**
- Set `lookback_days` to **30** (to get initial posts)
- Click **Run workflow**

### 6. Visit Your Blog

- `https://YOUR_USERNAME.github.io`
- First build takes 1-2 minutes

## How It Works

1. **Weekly automation** (Monday 9 AM UTC) or manual trigger
2. Fetches your commits via GitHub API
3. Generates blog post using AI (Claude/GPT)
4. Commits post to `_posts/` directory
5. GitHub Pages rebuilds and publishes automatically

## Configuration

Edit `config.yml`:

```yaml
github:
  username: "your-username"           # Your GitHub username
  exclude_repos:
    - "your-username.github.io"       # Don't blog about the blog

llm:
  provider: "openai"                  # or "anthropic"
  model: "gpt-4o-mini"                # or "claude-3-5-sonnet-20241022"
  article_style: "technical"          # technical/casual/detailed/concise

automation:
  min_commits: 3                      # Minimum commits to generate post
  lookback_days: 7                    # Days to search (overridden by workflow)
```

## Manual Trigger Options

Run workflow manually with custom parameters:

- **lookback_days** (default: 7): How many days back to search
- **force_generate** (default: false): Generate even with few commits

## Change Schedule

Edit `.github/workflows/auto-blog.yml`:

```yaml
schedule:
  - cron: '0 9 * * 1'  # Weekly Monday 9 AM UTC
```

Common schedules:
- Daily: `'0 9 * * *'`
- Weekly: `'0 9 * * 1'`
- Monthly: `'0 9 1 * *'`

## Local Testing (Optional)

### Prerequisites

Install [uv](https://docs.astral.sh/uv/) (Python package manager):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install [just](https://github.com/casey/just) (task runner):
```bash
# macOS
brew install just

# Linux
cargo install just
```

### Setup and Run

```bash
# Copy environment template
cp .env.example .env
# Add your LLM_API_KEY to .env

# Install Python dependencies with uv
just install  # or: uv sync

# Test scripts individually
just fetch     # Fetch commits from GitHub
just generate  # Generate blog post

# Or run complete workflow
just run       # Run fetch → generate → build

# Preview Jekyll site
just serve     # Starts Jekyll server at http://localhost:4000
```

### Development Commands

```bash
just fmt       # Format code with ruff
just lint      # Check code quality
just check     # Auto-fix linting issues
```

## Troubleshooting

**No posts generated?**
- Check Actions tab for workflow errors
- Verify `LLM_API_KEY` is set in repository secrets
- Ensure you have at least 3 commits in the lookback period

**Site not accessible?**
- Verify GitHub Pages is enabled in Settings → Pages
- Check Actions tab for deployment status
- Wait 1-2 minutes for first build

**Workflow fails?**
- Check that secrets are named exactly: `LLM_API_KEY`
- Verify API key is valid
- Check workflow logs for specific errors

## Customization

- **Theme**: Edit `jekyll/assets/css/style.css`
- **LLM prompts**: Edit `src/roboblog/generate_post.py` → `PromptBuilder`
- **Post template**: Edit `jekyll/_layouts/post.html`
- **Exclude repos**: Add to `config.yml` → `exclude_repos`

## Project Structure

```
.
├── config.yml                 # Main configuration
├── pyproject.toml             # Python package configuration
├── .github/workflows/
│   └── auto-blog.yml          # GitHub Actions workflow
├── src/roboblog/              # Python package
│   ├── fetch_commits.py       # Fetch commits from GitHub
│   ├── generate_post.py       # Generate post with AI
│   └── run_blog_update.py     # Complete workflow orchestrator
├── jekyll/
│   ├── _posts/                # Published posts (auto-generated)
│   ├── _layouts/              # Jekyll templates
│   └── assets/css/            # Styles
└── justfile                   # Task runner commands
```

## License

MIT License - See [LICENSE](LICENSE) file.

## Support

- Issues: https://github.com/m42839360-cell/m42839360-cell.github.io/issues
- Powered by Jekyll, GitHub Pages, and AI (Claude/GPT)
