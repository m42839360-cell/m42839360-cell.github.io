
"""
Blog Post Generator
Generates Jekyll blog posts from commit data using LLM API.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from dotenv import load_dotenv
import dspy


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
        lines.append(
            f"Time period: {data.get('since', 'N/A')} to {data.get('fetched_at', 'N/A')}"
        )
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


class BlogPostSignature(dspy.Signature):
    """Generate a structured blog post from development activity data.

    The blog post should have a compelling headline and comprehensive summary
    of the development work, written in the specified style.
    """

    commit_summary: str = dspy.InputField(desc="Summary of git commits and development activity")
    style_instruction: str = dspy.InputField(desc="Writing style and tone to use")
    include_code: bool = dspy.InputField(desc="Whether to include code snippets")
    include_stats: bool = dspy.InputField(desc="Whether to include statistics")

    headline: str = dspy.OutputField(desc="Catchy, descriptive blog post title (without # markdown)")
    summary: str = dspy.OutputField(desc="Complete blog post body content in markdown format")


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

    def get_enable_no_update_posts(self) -> bool:
        """Get whether to generate no-update posts."""
        return self.config.get("automation", {}).get("enable_no_update_posts", False)

    def get_jekyll_config(self) -> Dict[str, Any]:
        """Get Jekyll configuration."""
        return self.config.get("jekyll", {})

    def get_author(self) -> str:
        """Get author from Jekyll configuration."""
        return self.config.get("jekyll", {}).get("author", "")

    def create_dspy_lm(self) -> "dspy.LM":
        """Create and return a configured DSPy LM instance.

        Returns:
            Configured dspy.LM instance ready to use
        """
        provider = self.get_provider()
        model = self.get_model()
        max_tokens = self.get_max_tokens()
        temperature = self.get_temperature()

        if provider == "openai":
            return dspy.LM(
                f"openai/{model}",
                api_key=self.api_key,
                max_tokens=max_tokens,
                temperature=temperature,
            )
        elif provider == "anthropic":
            return dspy.LM(
                f"anthropic/{model}",
                api_key=self.api_key,
                max_tokens=max_tokens,
                temperature=temperature,
            )
        elif provider == "ollama":
            return dspy.LM(
                f"ollama/{model}",
                api_base="http://localhost:11434",
                max_tokens=max_tokens,
                temperature=temperature,
            )
        elif provider == "openrouter":
            return dspy.LM(
                model,
                api_key=self.api_key,
                api_base="https://openrouter.ai/api/v1",
                max_tokens=max_tokens,
                temperature=temperature,
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")


class PromptBuilder:
    """Builds structured prompts for LLM using DSPy signatures."""

    def __init__(self, article_style: str, blog_config: Dict[str, Any]):
        self.article_style = article_style
        self.blog_config = blog_config
        self.predictor = dspy.ChainOfThought(BlogPostSignature)

    def build_style_instruction(self) -> str:
        """Build style instruction based on article style."""
        style_descriptions = {
            "technical": "Write in a technical, detailed style with code examples and technical terminology.",
            "casual": "Write in a casual, conversational tone that's easy to read.",
            "detailed": "Write a comprehensive, in-depth analysis with extensive details.",
            "concise": "Write a brief, to-the-point summary focusing on key points.",
            "tutorial": "Write in a tutorial style, explaining steps and providing guidance.",
            "story": "Write in a narrative, story-telling style that engages readers.",
        }

        base_instruction = style_descriptions.get(
            self.article_style,
            "Write in a professional, informative style.",
        )

        include_code = self.blog_config.get("include_code_snippets", True)
        include_stats = self.blog_config.get("include_stats", True)

        additional = []
        if include_code:
            additional.append("Include relevant code snippets where appropriate.")
        if include_stats:
            additional.append("Include statistics about changes (lines added/removed, files changed).")

        additional.append("Group related changes together logically.")
        additional.append("Use only information from commit messages, don't guess implementation details.")

        return base_instruction + " " + " ".join(additional)

    def generate(self, commit_summary: str) -> Dict[str, str]:
        """Generate structured blog post using DSPy.

        Returns:
            Dictionary with 'headline' and 'summary' keys
        """
        style_instruction = self.build_style_instruction()
        include_code = self.blog_config.get("include_code_snippets", True)
        include_stats = self.blog_config.get("include_stats", True)

        result = self.predictor(
            commit_summary=commit_summary,
            style_instruction=style_instruction,
            include_code=include_code,
            include_stats=include_stats,
        )

        return {
            "headline": result.headline,
            "summary": result.summary,
        }


class JekyllPostGenerator:
    """Generates Jekyll blog posts with frontmatter."""

    def __init__(self, blog_config: Dict[str, Any], author: str = ""):
        self.blog_config = blog_config
        self.author = author

    def generate(self, structured_content: Dict[str, str]) -> str:
        """Generate complete Jekyll post with frontmatter from structured content.

        Args:
            structured_content: Dictionary with 'headline' and 'summary' keys

        Returns:
            Complete Jekyll post with frontmatter
        """
        title = structured_content.get("headline", "Development Update")
        content = structured_content.get("summary", "")

        # Generate frontmatter
        now = datetime.now(timezone.utc)
        date_str = now.strftime("%Y-%m-%d")

        default_tags = self.blog_config.get("default_tags", ["development", "updates"])

        frontmatter = f"""---
layout: post
title: "{title}"
date: {now.strftime("%Y-%m-%d %H:%M:%S %z")}
categories: {" ".join(default_tags)}
author: {self.author}
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
    """Writes blog posts to jekyll/_posts directory."""

    def __init__(self, posts_dir: str = "jekyll/_posts"):
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


def generate_no_update_post(blog_config: Dict[str, Any], author: str = "") -> str:
    """Generate a post indicating no updates for the previous day.

    Args:
        blog_config: Blog configuration dictionary
        author: Author name from jekyll config

    Returns:
        Complete Jekyll post content with frontmatter
    """
    now = datetime.now(timezone.utc)
    yesterday = now - timedelta(days=1)

    date_str = yesterday.strftime("%Y-%m-%d")
    friendly_date = yesterday.strftime("%B %d, %Y")

    default_tags = blog_config.get("default_tags", ["development", "updates"])

    title = f"No Development Updates - {friendly_date}"

    frontmatter = f"""---
layout: post
title: "{title}"
date: {now.strftime("%Y-%m-%d %H:%M:%S %z")}
categories: {" ".join(default_tags)}
author: {author}
---

"""

    content = f"""No development activity was recorded on {friendly_date}.

This is an automated post generated because the `enable_no_update_posts` configuration option is enabled.

Check back tomorrow for new updates!
"""

    return frontmatter + content


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

        # Load LLM configuration first to check if no-update posts are enabled
        llm_config = LLMConfig(config_path=args.config)
        llm_config.load()

        if commit_data.get("total_commits", 0) == 0:
            if llm_config.get_enable_no_update_posts():
                print("  No commits found, generating no-update post...")
                print("\n[2/6] Generating no-update post...")
                post_content = generate_no_update_post(
                    llm_config.get_blog_config(),
                    llm_config.get_author()
                )

                # Generate filename for no-update post
                post_generator = JekyllPostGenerator(
                    blog_config=llm_config.get_blog_config(),
                    author=llm_config.get_author()
                )
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
                print("✓ Complete! Generated no-update post.")
                print("=" * 60)
                return
            else:
                print("✗ No commits found to generate post")
                sys.exit(1)

        print(f"  Found {commit_data.get('total_commits')} commits")

        # LLM configuration already loaded above
        print("\n[2/6] Using loaded LLM configuration...")

        provider = llm_config.get_provider()
        model = llm_config.get_model()
        print(f"  Provider: {provider}")
        print(f"  Model: {model}")

        # Configure DSPy with the LLM
        print("\n[3/6] Configuring DSPy...")
        lm = llm_config.create_dspy_lm()
        dspy.configure(lm=lm)
        print(f"  ✓ DSPy configured with {provider}/{model}")

        # Build structured prompt with DSPy
        print("\n[4/6] Initializing DSPy prompt builder...")
        prompt_builder = PromptBuilder(
            article_style=llm_config.get_article_style(),
            blog_config=llm_config.get_blog_config(),
        )
        print("  ✓ Prompt builder ready")

        # Generate structured content
        print("\n[5/6] Generating structured blog post with DSPy...")
        print("  (This may take a moment...)")
        structured_content = prompt_builder.generate(commit_summary)
        print("  ✓ Content generated")
        print(f"  - Headline: {structured_content['headline'][:60]}...")
        print(f"  - Summary length: {len(structured_content['summary'])} chars")

        # Generate Jekyll post
        print("\n[6/6] Creating Jekyll post...")
        post_generator = JekyllPostGenerator(
            blog_config=llm_config.get_blog_config(),
            author=llm_config.get_author()
        )
        post_content = post_generator.generate(structured_content)
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
