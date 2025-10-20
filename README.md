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

### Local Testing

Generate a blog post manually:
```bash
python scripts/generate_post.py
```

### GitHub Actions (Automated)

The blog automatically generates posts based on the configured frequency:
- Posts are created in `_posts/` directory
- Committed and pushed to the repository
- Published via GitHub Pages

## Project Structure

```
.
├── _config.yml           # Jekyll configuration
├── config.yml            # Blog automation configuration
├── .env                  # API keys (not in git)
├── .env.example          # Environment template
├── _posts/               # Blog posts (markdown)
├── _layouts/             # Jekyll templates
├── assets/               # CSS, images, etc.
├── scripts/              # Python automation scripts
│   ├── fetch_commits.py  # Fetch GitHub commits
│   └── generate_post.py  # Generate blog post with LLM
├── Gemfile               # Ruby dependencies
└── README.md             # This file
```

## Customization

### Changing the Theme

Edit `assets/css/style.css` to customize colors, fonts, and layout.

### Post Templates

Modify `_layouts/post.html` to change the blog post layout.

### Automation Logic

Edit Python scripts in `scripts/` to customize:
- Commit filtering logic
- Post generation prompts
- Content formatting

## Troubleshooting

### Jekyll build fails
```bash
bundle install
bundle exec jekyll build --verbose
```

### API key errors
- Check `.env` file exists and contains valid key
- Verify `config.yml` references correct environment variable
- Test API key with: `curl https://api.anthropic.com/v1/messages -H "x-api-key: $LLM_API_KEY"`

### No posts generated
- Check `lookback_days` and `min_commits` settings
- Verify commits exist in the timeframe
- Review script logs for errors

## Contributing

This is a personal blog project, but feel free to fork and customize for your own use!

## License

MIT License - feel free to use and modify as needed.

## Acknowledgments

- Built with [Jekyll](https://jekyllrb.com/)
- Powered by AI (Claude/GPT)
- Hosted on [GitHub Pages](https://pages.github.com/)
