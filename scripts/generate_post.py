#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "requests>=2.31.0",
#   "pyyaml>=6.0.0",
#   "python-dotenv>=1.0.0",
#   "openai>=1.0.0",
#   "anthropic>=0.18.0",
# ]
# requires-python = ">=3.11"
# ///

"""
Blog Post Generator
Generates Jekyll blog posts from commit data using LLM API.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from dotenv import load_dotenv


class CommitDataLoader:
    """Loads and processes commit data from JSON file."""

    def __init__(self, data_path: str = "data/commits.json"):
        self.data_path = Path(data_path)

    def load(self) -> Dict[str, Any]:
        """Load commit data from JSON file."""
        if not self.data_path.exists():
            raise FileNotFoundError(f"Commit data not found: {self.data_path}")

        with open(self.data_path, "r") as f:
            data = json.load(f)
            print(f"✓ Loaded commit data from {self.data_path}")
            return data

    def format_for_prompt(self, data: Dict[str, Any]) -> str:
        """Format commit data for LLM prompt."""
        repositories = data.get("repositories", {})
        total_commits = data.get("total_commits", 0)

        if total_commits == 0:
            return "No commits found in the specified time period."

        lines = []
        lines.append(f"Total commits: {total_commits}")
        lines.append(f"Time period: {data.get('since', 'N/A')} to {data.get('fetched_at', 'N/A')}")
        lines.append("")

        for repo_name, commits in repositories.items():
            lines.append(f"## Repository: {repo_name}")
            lines.append(f"Commits: {len(commits)}")
            lines.append("")

            for commit in commits:
                lines.append(f"### Commit: {commit.get('sha', '')[:7]}")
                lines.append(f"Author: {commit.get('author', 'Unknown')}")
                lines.append(f"Date: {commit.get('date', 'Unknown')}")
                lines.append(f"Message: {commit.get('message', '')}")

                # File changes
                files = commit.get("files", [])
                if files:
                    lines.append(f"Files changed ({len(files)}):")
                    for file_info in files[:10]:  # Limit to 10 files
                        status = file_info.get("status", "modified")
                        filename = file_info.get("filename", "")
                        lines.append(f"  - {status}: {filename}")

                    if len(files) > 10:
                        lines.append(f"  ... and {len(files) - 10} more files")

                # Stats
                stats = commit.get("stats", {})
                lines.append(
                    f"Stats: +{stats.get('additions', 0)} -{stats.get('deletions', 0)}"
                )
                lines.append(f"URL: {commit.get('url', '')}")
                lines.append("")

        return "\n".join(lines)


class LLMConfig:
    """Manages LLM configuration from config.yml and environment."""

    def __init__(self, config_path: str = "config.yml", env_path: str = ".env"):
        self.config_path = Path(config_path)
        self.env_path = Path(env_path)
        self.config: Dict[str, Any] = {}
        self.api_key: Optional[str] = None

    def load(self) -> None:
        """Load configuration from files."""
        # Load environment variables
        if self.env_path.exists():
            load_dotenv(self.env_path)
            print(f"✓ Loaded environment from {self.env_path}")

        # Load YAML config
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, "r") as f:
            self.config = yaml.safe_load(f)
            print(f"✓ Loaded config from {self.config_path}")

        # Get API key from environment
        api_key_env_var = self.config.get("llm", {}).get("api_key_env", "LLM_API_KEY")
        self.api_key = os.getenv(api_key_env_var)

        if not self.api_key:
            raise ValueError(
                f"API key not found in environment variable: {api_key_env_var}"
            )

    def get_provider(self) -> str:
        """Get LLM provider name."""
        return self.config.get("llm", {}).get("provider", "anthropic")

    def get_model(self) -> str:
        """Get LLM model name."""
        return self.config.get("llm", {}).get("model", "claude-3-5-sonnet-20241022")

    def get_article_style(self) -> str:
        """Get article style/tone."""
        return self.config.get("llm", {}).get("article_style", "technical")

    def get_max_tokens(self) -> int:
        """Get maximum tokens for generation."""
        return self.config.get("llm", {}).get("max_tokens", 2000)

    def get_temperature(self) -> float:
        """Get temperature for creativity."""
        return self.config.get("llm", {}).get("temperature", 0.7)

    def get_blog_config(self) -> Dict[str, Any]:
        """Get blog configuration."""
        return self.config.get("blog", {})

    def get_automation_config(self) -> Dict[str, Any]:
        """Get automation configuration."""
        return self.config.get("automation", {})


class LLMClient:
    """Base class for LLM API clients."""

    def generate(self, prompt: str) -> str:
        """Generate text from prompt."""
        raise NotImplementedError


class OpenAIClient(LLMClient):
    """OpenAI API client."""

    def __init__(self, api_key: str, model: str, max_tokens: int, temperature: float):
        from openai import OpenAI

        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    def generate(self, prompt: str) -> str:
        """Generate text using OpenAI API."""
        # Newer models (gpt-4o, gpt-4o-mini, etc.) use max_completion_tokens
        # Older models (gpt-4, gpt-3.5-turbo) use max_tokens
        kwargs = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
        }

        # Use max_completion_tokens for newer models, max_tokens for older ones
        if "gpt-4o" in self.model or "gpt-5" in self.model:
            kwargs["max_completion_tokens"] = self.max_tokens
        else:
            kwargs["max_tokens"] = self.max_tokens

        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content


class AnthropicClient(LLMClient):
    """Anthropic API client."""

    def __init__(self, api_key: str, model: str, max_tokens: int, temperature: float):
        from anthropic import Anthropic

        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    def generate(self, prompt: str) -> str:
        """Generate text using Anthropic API."""
        message = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text


class OllamaClient(LLMClient):
    """Ollama API client (local)."""

    def __init__(
        self,
        model: str,
        max_tokens: int,
        temperature: float,
        base_url: str = "http://localhost:11434",
    ):
        import requests

        self.session = requests.Session()
        self.base_url = base_url
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    def generate(self, prompt: str) -> str:
        """Generate text using Ollama API."""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens,
            },
        }

        response = self.session.post(url, json=payload)
        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.status_code} - {response.text}")

        return response.json().get("response", "")


class OpenRouterClient(LLMClient):
    """OpenRouter API client."""

    def __init__(self, api_key: str, model: str, max_tokens: int, temperature: float):
        import requests

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
        )
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    def generate(self, prompt: str) -> str:
        """Generate text using OpenRouter API."""
        url = "https://openrouter.ai/api/v1/chat/completions"
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }

        response = self.session.post(url, json=payload)
        if response.status_code != 200:
            raise Exception(
                f"OpenRouter API error: {response.status_code} - {response.text}"
            )

        return response.json()["choices"][0]["message"]["content"]


class PromptBuilder:
    """Builds prompts for LLM based on commit data and configuration."""

    def __init__(self, article_style: str, blog_config: Dict[str, Any]):
        self.article_style = article_style
        self.blog_config = blog_config

    def build(self, commit_summary: str) -> str:
        """Build prompt for LLM."""
        style_descriptions = {
            "technical": "Write in a technical, detailed style with code examples and technical terminology.",
            "casual": "Write in a casual, conversational tone that's easy to read.",
            "detailed": "Write a comprehensive, in-depth analysis with extensive details.",
            "concise": "Write a brief, to-the-point summary focusing on key points.",
            "tutorial": "Write in a tutorial style, explaining steps and providing guidance.",
            "story": "Write in a narrative, story-telling style that engages readers.",
        }

        style_instruction = style_descriptions.get(
            self.article_style,
            "Write in a professional, informative style.",
        )

        include_code = self.blog_config.get("include_code_snippets", True)
        include_stats = self.blog_config.get("include_stats", True)

        prompt = f"""You are a technical blog post writer. Generate a blog post based on the following development activity.

{style_instruction}

IMPORTANT FORMATTING REQUIREMENTS:
- Write ONLY the blog post content (title and body)
- DO NOT include Jekyll frontmatter (no --- delimiters, no YAML metadata)
- Start with a markdown heading (# Title)
- Use proper markdown formatting
- Make the content engaging and informative
- Focus on the "why" and "what" rather than just listing commits

CONTENT GUIDELINES:
- Create a catchy, descriptive title that reflects the work done
- Write an engaging introduction paragraph
- Group related changes together logically
- Explain the impact and purpose of the changes
{'- Include relevant code snippets where appropriate' if include_code else ''}
{'- Include statistics about the changes (lines added/removed, files changed)' if include_stats else ''}
- End with a conclusion or next steps section

DEVELOPMENT ACTIVITY:

{commit_summary}

Now write the blog post:"""

        return prompt


class JekyllPostGenerator:
    """Generates Jekyll blog posts with frontmatter."""

    def __init__(self, blog_config: Dict[str, Any]):
        self.blog_config = blog_config

    def generate(self, llm_content: str) -> str:
        """Generate complete Jekyll post with frontmatter."""
        # Extract title from LLM content (first # heading)
        title_match = re.search(r"^#\s+(.+)$", llm_content, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()
            # Remove the title from content since it will be in frontmatter
            content = re.sub(r"^#\s+.+$\n?", "", llm_content, count=1, flags=re.MULTILINE)
        else:
            title = "Development Update"
            content = llm_content

        # Generate frontmatter
        now = datetime.now(timezone.utc)
        date_str = now.strftime("%Y-%m-%d")

        default_tags = self.blog_config.get("default_tags", ["development", "updates"])
        author = self.blog_config.get("author", "")

        frontmatter = f"""---
layout: post
title: "{title}"
date: {now.strftime("%Y-%m-%d %H:%M:%S %z")}
categories: {' '.join(default_tags)}
author: {author}
---

"""

        return frontmatter + content.strip()

    def get_filename(self, content: str) -> str:
        """Generate filename from post content."""
        # Extract title
        title_match = re.search(r'^title:\s*"(.+)"$', content, re.MULTILINE)
        if title_match:
            title = title_match.group(1)
        else:
            title = "development-update"

        # Slugify title
        slug = re.sub(r"[^\w\s-]", "", title.lower())
        slug = re.sub(r"[-\s]+", "-", slug).strip("-")

        # Generate date prefix
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        return f"{date_str}-{slug}.md"


class PostWriter:
    """Writes blog posts to _posts directory."""

    def __init__(self, posts_dir: str = "_posts"):
        self.posts_dir = Path(posts_dir)

    def write(self, filename: str, content: str) -> Path:
        """Write post to file."""
        # Create directory if it doesn't exist
        self.posts_dir.mkdir(parents=True, exist_ok=True)

        filepath = self.posts_dir / filename

        with open(filepath, "w") as f:
            f.write(content)

        print(f"✓ Written blog post to {filepath}")
        return filepath


class TimestampUpdater:
    """Updates .last_build timestamp file."""

    def __init__(self, file_path: str = ".last_build"):
        self.file_path = Path(file_path)

    def update(self) -> None:
        """Update timestamp to now."""
        timestamp = datetime.now(timezone.utc)
        with open(self.file_path, "w") as f:
            f.write(timestamp.isoformat())
        print(f"✓ Updated {self.file_path} with timestamp: {timestamp.isoformat()}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate Jekyll blog post from commit data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Output to stdout instead of writing file",
    )
    parser.add_argument(
        "--config",
        default="config.yml",
        help="Path to config file (default: config.yml)",
    )
    parser.add_argument(
        "--input",
        default="data/commits.json",
        help="Input commits JSON file (default: data/commits.json)",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Blog Post Generator")
    print("=" * 60)

    try:
        # Load commit data
        print("\n[1/6] Loading commit data...")
        loader = CommitDataLoader(data_path=args.input)
        commit_data = loader.load()
        commit_summary = loader.format_for_prompt(commit_data)

        if commit_data.get("total_commits", 0) == 0:
            print("✗ No commits found to generate post")
            sys.exit(1)

        print(f"  Found {commit_data.get('total_commits')} commits")

        # Load LLM configuration
        print("\n[2/6] Loading LLM configuration...")
        llm_config = LLMConfig(config_path=args.config)
        llm_config.load()

        provider = llm_config.get_provider()
        model = llm_config.get_model()
        print(f"  Provider: {provider}")
        print(f"  Model: {model}")

        # Create LLM client
        print("\n[3/6] Initializing LLM client...")
        if provider == "openai":
            client = OpenAIClient(
                api_key=llm_config.api_key,
                model=model,
                max_tokens=llm_config.get_max_tokens(),
                temperature=llm_config.get_temperature(),
            )
        elif provider == "anthropic":
            client = AnthropicClient(
                api_key=llm_config.api_key,
                model=model,
                max_tokens=llm_config.get_max_tokens(),
                temperature=llm_config.get_temperature(),
            )
        elif provider == "ollama":
            client = OllamaClient(
                model=model,
                max_tokens=llm_config.get_max_tokens(),
                temperature=llm_config.get_temperature(),
            )
        elif provider == "openrouter":
            client = OpenRouterClient(
                api_key=llm_config.api_key,
                model=model,
                max_tokens=llm_config.get_max_tokens(),
                temperature=llm_config.get_temperature(),
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

        # Build prompt
        print("\n[4/6] Building prompt...")
        prompt_builder = PromptBuilder(
            article_style=llm_config.get_article_style(),
            blog_config=llm_config.get_blog_config(),
        )
        prompt = prompt_builder.build(commit_summary)

        # Generate content
        print("\n[5/6] Generating blog post with LLM...")
        print("  (This may take a moment...)")
        llm_content = client.generate(prompt)
        print("  ✓ Content generated")

        # Generate Jekyll post
        print("\n[6/6] Creating Jekyll post...")
        post_generator = JekyllPostGenerator(blog_config=llm_config.get_blog_config())
        post_content = post_generator.generate(llm_content)
        filename = post_generator.get_filename(post_content)

        if args.preview:
            print("\n⚠ PREVIEW MODE - No files will be written")
            print("\nFilename:", filename)
            print("\nContent:")
            print("=" * 60)
            print(post_content)
            print("=" * 60)
        else:
            # Write post
            writer = PostWriter()
            filepath = writer.write(filename, post_content)

            # Update timestamp
            updater = TimestampUpdater()
            updater.update()

        print("\n" + "=" * 60)
        print("✓ Complete!")
        print("=" * 60)

    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}")
        print("  Make sure to run fetch_commits.py first")
        sys.exit(1)
    except ValueError as e:
        print(f"\n✗ Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
