# Dev Blog - Automated Commit-Based Blog Posts

An automated blogging system that generates blog posts from your GitHub commit history using AI.

## Overview

This project automatically:
- Fetches your recent GitHub commits
- Analyzes commit patterns and changes
- Generates engaging blog posts using LLM
- Publishes to GitHub Pages via Jekyll

## Features

- 🤖 AI-powered post generation using Claude, GPT, or local models
- 📊 Commit statistics and code snippets
- 🎨 Clean, responsive Jekyll theme
- 📡 RSS feed support
- ⚙️ Flexible configuration options
- 🔒 Secure API key management

## Setup

### Prerequisites

- Ruby 3.x
- Bundler
- Python 3.8+ (for automation scripts)
- LLM API key (Anthropic, OpenAI, or OpenRouter)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/m42839360-cell/m42839360-cell.github.io.git
   cd m42839360-cell.github.io
   ```

2. **Install Jekyll dependencies**
   ```bash
   bundle install
   ```

3. **Configure the blog**

   Copy the environment template:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your API key:
   ```bash
   LLM_API_KEY=your_actual_api_key_here
   ```

4. **Customize settings**

   Edit `config.yml` to configure:
   - GitHub username and repository filters
   - LLM provider and model
   - Article style and tone
   - Automation frequency
   - Blog post settings

### Local Development

Run the Jekyll development server:
```bash
bundle exec jekyll serve
```

Visit http://localhost:4000 to see your blog.

## Configuration

### config.yml

The main configuration file with the following sections:

#### GitHub Configuration

```yaml
github:
  username: "your-github-username"     # Required: Your GitHub username
  repo_filters: []                      # Optional: Only include these repos
  exclude_repos:                        # Repos to skip
    - "m42839360-cell.github.io"
```

**Options:**
- `username` (required): Your GitHub username for fetching commits
- `repo_filters` (optional): List of repository names to include. Leave empty to include all repos.
- `exclude_repos` (optional): List of repositories to exclude from blog posts

#### LLM Configuration

```yaml
llm:
  provider: "anthropic"                      # LLM provider
  api_key_env: "LLM_API_KEY"                 # Environment variable name
  model: "claude-3-5-sonnet-20241022"        # Model to use
  article_style: "technical"                 # Writing style
  max_tokens: 2000                           # Max response length
  temperature: 0.7                           # Creativity (0.0-1.0)
```

**Supported Providers:**
- `anthropic`: Claude models (claude-3-5-sonnet-20241022, claude-3-opus-20240229)
- `openai`: GPT models (gpt-4, gpt-3.5-turbo)
- `ollama`: Local models (llama2, mistral, codellama)
- `openrouter`: Multiple providers via OpenRouter

**Article Styles:**
- `technical`: Detailed technical explanations
- `casual`: Friendly, conversational tone
- `detailed`: Comprehensive analysis
- `concise`: Brief, to-the-point
- `tutorial`: Step-by-step format
- `story`: Narrative style

#### Automation Settings

```yaml
automation:
  lookback_days: 7          # Days to look back for commits
  min_commits: 3            # Minimum commits for a post
  max_commits: 20           # Maximum commits per post
  frequency: "weekly"       # Post frequency (daily/weekly/biweekly/monthly)
```

**Options:**
- `lookback_days`: Number of days to search for commits (default: 7)
- `min_commits`: Minimum commits required to generate a post
- `max_commits`: Maximum commits to include in a single post
- `frequency`: How often to generate posts via GitHub Actions

#### Blog Post Settings

```yaml
blog:
  title_template: "Development Update - Week of {date}"
  include_code_snippets: true
  max_snippet_lines: 20
  include_stats: true
  default_tags:
    - "development"
    - "updates"
  author: "m42839360-cell"
```

**Options:**
- `title_template`: Post title format (variables: {date}, {week}, {month}, {year}, {commit_count})
- `include_code_snippets`: Whether to include code examples
- `max_snippet_lines`: Maximum lines per code snippet
- `include_stats`: Include commit statistics
- `default_tags`: Tags applied to all posts
- `author`: Author name for posts

### Environment Variables (.env)

Sensitive credentials are stored in `.env` (never committed to git):

```bash
# LLM API Key (required)
LLM_API_KEY=your_api_key_here

# GitHub Token (optional, for private repos or higher rate limits)
GITHUB_TOKEN=your_github_token_here
```

**Getting API Keys:**
- **Anthropic Claude**: https://console.anthropic.com/
- **OpenAI GPT**: https://platform.openai.com/api-keys
- **OpenRouter**: https://openrouter.ai/keys
- **GitHub Token**: https://github.com/settings/tokens (scopes: `repo` or `public_repo`)

## Usage

### Manual Workflow

The blog automation consists of three main scripts that can be run individually or together.

#### 1. Fetch Commits

Fetch your recent GitHub commits and save to `data/commits.json`:

```bash
./scripts/fetch_commits.py
```

**Options:**
- `--dry-run`: Preview without writing files
- `--config PATH`: Use custom config file (default: `config.yml`)
- `--output PATH`: Custom output file (default: `data/commits.json`)

**Example:**
```bash
# Dry run to see what would be fetched
./scripts/fetch_commits.py --dry-run

# Fetch and save to custom location
./scripts/fetch_commits.py --output my-commits.json
```

#### 2. Generate Blog Post

Generate a blog post from commit data using LLM:

```bash
./scripts/generate_post.py
```

**Options:**
- `--preview`: Output to stdout instead of writing file
- `--config PATH`: Use custom config file (default: `config.yml`)
- `--input PATH`: Input commits file (default: `data/commits.json`)

**Example:**
```bash
# Preview the generated post
./scripts/generate_post.py --preview

# Generate with custom data
./scripts/generate_post.py --input test-data/commits.json
```

**Note:** Requires valid LLM API key in `.env` file.

#### 3. Complete Workflow

Run the entire workflow with a single command:

```bash
./scripts/run_blog_update.py
```

**Options:**
- `--dry-run`: Test without writing files
- `--skip-build`: Skip Jekyll build step
- `--config PATH`: Use custom config file

**Example:**
```bash
# Test the complete workflow
./scripts/run_blog_update.py --dry-run

# Run workflow without building Jekyll (faster for testing)
./scripts/run_blog_update.py --skip-build

# Full workflow with Jekyll build
./scripts/run_blog_update.py
```

### GitHub Actions (Automated)

The blog can automatically generate posts using GitHub Actions. See the **GitHub Actions Setup** section below for configuration instructions.

## GitHub Actions Setup

To enable automated blog post generation via GitHub Actions, you need to configure repository secrets.

### Required Repository Secrets

Navigate to your repository settings: **Settings → Secrets and variables → Actions → New repository secret**

Add the following secrets:

#### 1. LLM_API_KEY (Required)

Your LLM provider API key for generating blog posts.

- **Secret name:** `LLM_API_KEY`
- **Secret value:** Your API key from one of these providers:
  - **OpenAI:** Get from https://platform.openai.com/api-keys
  - **Anthropic:** Get from https://console.anthropic.com/
  - **OpenRouter:** Get from https://openrouter.ai/keys

**Example:**
```
Name: LLM_API_KEY
Value: sk-ant-api03-xxxxx...  (for Anthropic)
       sk-xxxxx...             (for OpenAI)
```

#### 2. GITHUB_TOKEN (Optional, but Recommended)

A Personal Access Token for fetching commits with higher rate limits.

- **Secret name:** `GITHUB_TOKEN`
- **Secret value:** Personal Access Token from https://github.com/settings/tokens
- **Required scopes:**
  - `public_repo` (for public repositories)
  - `repo` (if you want to include private repositories)

**Why add this?**
- **Without token:** 60 requests/hour (may be insufficient for large commit history)
- **With token:** 5,000 requests/hour (recommended for reliable automation)

**Note:** GitHub Actions provides a default `GITHUB_TOKEN`, but it has restrictions. A Personal Access Token gives better access to your commit history.

**Example:**
```
Name: GITHUB_TOKEN
Value: ghp_xxxxx...
```

### Setting Up Secrets

**Step-by-step instructions:**

1. **Go to repository settings:**
   ```
   https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions
   ```

2. **Click "New repository secret"**

3. **Add LLM_API_KEY:**
   - Name: `LLM_API_KEY`
   - Value: Your API key (paste without quotes)
   - Click "Add secret"

4. **Add GITHUB_TOKEN (optional but recommended):**
   - Generate token: https://github.com/settings/tokens → "Generate new token (classic)"
   - Select scopes: `public_repo` or `repo`
   - Copy the generated token (starts with `ghp_`)
   - Add as repository secret:
     - Name: `GITHUB_TOKEN`
     - Value: Your token (paste without quotes)
   - Click "Add secret"

### Verifying Secrets Configuration

After adding secrets, you can verify they're configured correctly:

1. **Check secrets list:**
   - Go to: Settings → Secrets and variables → Actions
   - You should see `LLM_API_KEY` and optionally `GITHUB_TOKEN` listed
   - Secret values are hidden (you'll only see when they were last updated)

2. **Test with workflow:**
   - Once you set up the GitHub Actions workflow (task-12), it will use these secrets automatically
   - Check workflow runs for any authentication errors

### How Scripts Use Secrets

The Python scripts are designed to work seamlessly with both local development and GitHub Actions:

**Local development:**
- Scripts read from `.env` file using `python-dotenv`
- Create `.env` from `.env.example` template
- Add your API keys to `.env` (never commit this file!)

**GitHub Actions:**
- Secrets are automatically exposed as environment variables
- Scripts read from environment variables directly
- No `.env` file needed in the repository
- The `load_dotenv()` function does NOT override existing environment variables

**Priority:** Environment variables (GitHub Actions) → `.env` file (local)

### Security Best Practices

✅ **DO:**
- Add secrets via GitHub's repository settings UI
- Use repository secrets (not environment secrets) for personal repos
- Rotate API keys periodically
- Use minimal required token scopes

❌ **DON'T:**
- Never commit `.env` file to git (it's in `.gitignore`)
- Never hardcode API keys in scripts or config files
- Never share secrets in issues, pull requests, or documentation
- Don't use organization secrets unless necessary

### Troubleshooting Secrets

**Error:** `API key not found in environment variable: LLM_API_KEY`
- Verify secret name is exactly `LLM_API_KEY` (case-sensitive)
- Check the secret is added to repository secrets (not environment secrets)
- Ensure workflow references the secret correctly in `env:` section

**Error:** `GITHUB_TOKEN not found in environment`
- This is just a warning - the script will use unauthenticated requests (60/hour limit)
- Add `GITHUB_TOKEN` as repository secret to fix
- Or ignore if you have low commit volume

**Error:** `Invalid API key` or `401 Unauthorized`
- Verify the API key is correct and active
- Check you're using the right provider in `config.yml`
- Regenerate the API key if necessary

## Project Structure

```
.
├── _config.yml                # Jekyll configuration
├── config.yml                 # Blog automation configuration
├── .env                       # API keys (not in git)
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
├── Gemfile                    # Ruby dependencies
├── Gemfile.lock               # Locked Ruby dependency versions
├── README.md                  # This file
│
├── _layouts/                  # Jekyll templates
│   ├── default.html           # Base layout with header/footer
│   └── post.html              # Blog post layout with GitHub notice
│
├── _posts/                    # Published blog posts (auto-generated)
│   └── YYYY-MM-DD-title.md    # Post files with Jekyll frontmatter
│
├── assets/                    # Static assets
│   └── css/
│       └── style.css          # Main stylesheet (GitHub-inspired)
│
├── scripts/                   # Python automation scripts
│   ├── fetch_commits.py       # Fetch GitHub commits via API
│   ├── generate_post.py       # Generate blog post with LLM
│   └── run_blog_update.py     # Orchestrate complete workflow
│
├── data/                      # Runtime data (not in git)
│   └── commits.json           # Fetched commit data
│
├── index.html                 # Home page with about and recent posts
├── archive.html               # Archive page listing all posts
│
├── .last_build                # Timestamp of last run (not in git)
└── _site/                     # Generated site (not in git)
```

### Key Files Explained

**Configuration:**
- `config.yml` - Main automation settings (GitHub username, LLM provider, article style)
- `_config.yml` - Jekyll site settings (title, description, plugins)
- `.env` - Secret API keys (create from `.env.example`)

**Scripts:**
- `fetch_commits.py` - Queries GitHub API for your commits
- `generate_post.py` - Uses LLM to create blog post from commits
- `run_blog_update.py` - Runs complete workflow (fetch → generate → build)

**Templates:**
- `_layouts/default.html` - Base layout with site header and footer
- `_layouts/post.html` - Post template with GitHub activity notice and metadata

**Content:**
- `index.html` - Home page with about section and recent posts
- `archive.html` - Complete post archive organized by date
- `_posts/` - Auto-generated blog posts in Jekyll format

## Customization

### Changing the Theme

Edit `assets/css/style.css` to customize the look and feel:

```css
/* Change primary color */
.link-button, .post-content a {
    color: #your-color;  /* Default: #0366d6 (GitHub blue) */
}

/* Customize code blocks */
.post-content pre {
    background-color: #your-bg;  /* Default: #282c34 (dark) */
}

/* Modify fonts */
body {
    font-family: your-font-stack;
}
```

**Key CSS classes:**
- `.github-notice` - GitHub activity banner
- `.post-content` - Blog post body
- `.link-button` - Action buttons on home page
- `.archive-page` - Archive page styling

### LLM Prompts

Customize how blog posts are generated by editing `scripts/generate_post.py`:

**Location:** `class PromptBuilder` → `def build()`

**What you can customize:**
- Writing style descriptions
- Content guidelines
- Formatting requirements
- Code snippet instructions

**Example modification:**
```python
style_descriptions = {
    "technical": "Your custom technical style instruction...",
    "casual": "Your custom casual style instruction...",
    # Add new styles:
    "academic": "Write in an academic, research-oriented style...",
}
```

### Post Templates

Modify `_layouts/post.html` to change the blog post layout:

**Current features:**
- GitHub activity notice with timestamp
- Author attribution
- Post metadata (categories, tags)
- Previous/Next navigation

**Example customization:**
```html
<!-- Add reading time estimate -->
<span class="reading-time">{{ content | number_of_words | divided_by: 200 }} min read</span>

<!-- Add share buttons -->
<div class="share-buttons">
  <a href="https://twitter.com/share?url={{ page.url | absolute_url }}">Tweet</a>
</div>
```

### Commit Filtering

Customize which commits are included by editing `scripts/fetch_commits.py`:

**Location:** `class CommitProcessor` → `def _should_exclude_repo()`

**Current filters:**
- Repository name matching
- Exclude list from config
- Include list from config

**Example: Add custom logic:**
```python
def _should_exclude_repo(self, repo_name: str) -> bool:
    # Exclude archived repos
    if "archive" in repo_name.lower():
        return True

    # Only include certain programming languages
    # (You'd need to add API calls to check repo language)

    return False  # Include by default
```

### Home Page Content

Edit `index.html` to customize the home page:
- Change the about section text
- Modify feature highlights
- Adjust number of recent posts (currently 10)
- Add custom sections

### Article Styles

Create new article styles in `config.yml`:

```yaml
llm:
  article_style: "your-custom-style"
```

Then add the style definition in `generate_post.py`:
```python
style_descriptions = {
    "your-custom-style": "Write in your custom style...",
}
```

## Troubleshooting

### Jekyll build fails

**Error:** `bundle: command not found`
```bash
gem install bundler
bundle install
```

**Error:** Missing dependencies
```bash
bundle install
bundle exec jekyll build --verbose
```

**Error:** Permission denied
```bash
bundle install --path vendor/bundle
```

### Python/UV Issues

**Error:** `uv: command not found`

Install UV package manager:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Error:** Python version mismatch

UV automatically handles Python versions. Make sure you have Python 3.11+ available:
```bash
python3 --version  # Should be 3.11 or higher
```

### API Key Errors

**Error:** `API key not found in environment variable: LLM_API_KEY`

1. Create `.env` file from template:
   ```bash
   cp .env.example .env
   ```

2. Add your API key to `.env`:
   ```bash
   LLM_API_KEY=your_actual_key_here
   ```

3. Verify the file is not in git:
   ```bash
   git status  # .env should not appear
   ```

**Test API key validity:**

For Anthropic:
```bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $LLM_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-3-5-sonnet-20241022","max_tokens":10,"messages":[{"role":"user","content":"test"}]}'
```

For OpenAI:
```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $LLM_API_KEY"
```

### No Posts Generated

**Issue:** Script runs but no posts created

1. **Check commit count:**
   ```bash
   ./scripts/fetch_commits.py --dry-run
   ```
   Look for "Found X commits" in output

2. **Verify minimum commits threshold:**
   - Check `config.yml`: `automation.min_commits` (default: 3)
   - If you have fewer commits, lower this value or wait for more activity

3. **Check date range:**
   - Default `lookback_days: 7`
   - Increase to search further back: `lookback_days: 30`

4. **Verify repositories not excluded:**
   - Check `config.yml`: `github.exclude_repos`
   - Make sure your active repos aren't in the exclude list

### Rate Limiting

**Error:** GitHub API rate limit exceeded

**Without GitHub token:** 60 requests/hour
**With GitHub token:** 5,000 requests/hour

**Solution:** Add GitHub token to `.env`:
```bash
GITHUB_TOKEN=ghp_your_token_here
```

Get token from: https://github.com/settings/tokens
Required scopes: `public_repo` (or `repo` for private repos)

### Generated Posts Look Wrong

**Issue:** LLM output includes frontmatter or wrong format

The prompts explicitly instruct the LLM not to include frontmatter. If this happens:

1. **Try different temperature:** Lower temperature (0.3-0.5) for more consistent output
2. **Change model:** Try a different LLM model
3. **Modify prompt:** Edit `scripts/generate_post.py` → `PromptBuilder.build()`

**Issue:** Code snippets not rendering

Make sure your commit messages or LLM output uses proper markdown code blocks:
<pre>
```python
code here
```
</pre>

### Local Development

**View site locally:**
```bash
bundle exec jekyll serve
# Visit http://localhost:4000
```

**Live reload during development:**
```bash
bundle exec jekyll serve --livereload
```

**Clear Jekyll cache:**
```bash
bundle exec jekyll clean
bundle exec jekyll build
```

## Contributing

This is a personal blog project, but feel free to fork and customize for your own use!

## License

MIT License - feel free to use and modify as needed.

## Acknowledgments

- Built with [Jekyll](https://jekyllrb.com/)
- Powered by AI (Claude/GPT)
- Hosted on [GitHub Pages](https://pages.github.com/)
