#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "requests>=2.31.0",
#   "pyyaml>=6.0.0",
#   "python-dotenv>=1.0.0",
# ]
# requires-python = ">=3.11"
# ///

"""
GitHub Commits Fetcher
Fetches commits from GitHub API since last run with rate limiting and pagination support.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
import yaml
from dotenv import load_dotenv


class ConfigReader:
    """Reads configuration from config.yml and .env files."""

    def __init__(self, config_path: str = "config.yml", env_path: str = ".env"):
        self.config_path = Path(config_path)
        self.env_path = Path(env_path)
        self.config: Dict[str, Any] = {}
        self.github_token: Optional[str] = None

    def load(self) -> None:
        """Load configuration from files."""
        # Load environment variables
        if self.env_path.exists():
            load_dotenv(self.env_path)
            print(f"✓ Loaded environment from {self.env_path}")
        else:
            print(f"⚠ No .env file found at {self.env_path}")

        # Load YAML config
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, "r") as f:
            self.config = yaml.safe_load(f)
            print(f"✓ Loaded config from {self.config_path}")

        # Get GitHub token from environment
        self.github_token = os.getenv("GITHUB_TOKEN")
        if not self.github_token:
            print("⚠ GITHUB_TOKEN not found in environment")
            print("  API rate limits will be restricted (60 requests/hour)")

    def get_github_username(self) -> str:
        """Get GitHub username from config."""
        return self.config.get("github", {}).get("username", "")

    def get_lookback_days(self) -> int:
        """Get number of days to look back for commits."""
        return self.config.get("automation", {}).get("lookback_days", 7)

    def get_repo_filters(self) -> List[str]:
        """Get list of repositories to include (empty = all repos)."""
        return self.config.get("github", {}).get("repo_filters", [])

    def get_exclude_repos(self) -> List[str]:
        """Get list of repositories to exclude."""
        return self.config.get("github", {}).get("exclude_repos", [])


class TimestampTracker:
    """Manages the .last_build file for tracking last run timestamp."""

    def __init__(self, file_path: str = ".last_build"):
        self.file_path = Path(file_path)

    def read(self) -> Optional[datetime]:
        """Read last run timestamp from file."""
        if not self.file_path.exists():
            return None

        try:
            with open(self.file_path, "r") as f:
                timestamp_str = f.read().strip()
                return datetime.fromisoformat(timestamp_str)
        except (ValueError, OSError) as e:
            print(f"⚠ Error reading {self.file_path}: {e}")
            return None

    def write(self, timestamp: Optional[datetime] = None) -> None:
        """Write timestamp to file (defaults to now)."""
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)

        with open(self.file_path, "w") as f:
            f.write(timestamp.isoformat())

        print(f"✓ Updated {self.file_path} with timestamp: {timestamp.isoformat()}")


class GitHubAPIClient:
    """GitHub API client with rate limiting and pagination support."""

    BASE_URL = "https://api.github.com"

    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.session = requests.Session()
        if self.token:
            self.session.headers.update({"Authorization": f"token {self.token}"})
        self.session.headers.update({"Accept": "application/vnd.github.v3+json"})

    def validate_token(self) -> bool:
        """Validate GitHub token by testing authentication."""
        if not self.token:
            return True  # No token is fine, just limited rate

        try:
            response = self.session.get(f"{self.BASE_URL}/user", timeout=10)

            if response.status_code == 401:
                print("\n" + "="*60)
                print("✗ ERROR: Invalid GitHub Token")
                print("="*60)
                print("\nYour GITHUB_TOKEN in .env file is invalid or expired.")
                print("\nTo fix this issue:")
                print("1. Go to: https://github.com/settings/tokens")
                print("2. Generate a new Personal Access Token")
                print("3. Required scopes: 'public_repo' (or 'repo' for private repos)")
                print("4. Update your .env file:")
                print("   GITHUB_TOKEN=ghp_your_new_token_here")
                print("\nMake sure there are:")
                print("  - No spaces around the '='")
                print("  - No quotes around the token")
                print("  - No extra whitespace")
                print("="*60 + "\n")
                return False

            if response.status_code == 403:
                print("\n" + "="*60)
                print("✗ ERROR: GitHub Token Lacks Required Permissions")
                print("="*60)
                print("\nYour token doesn't have the required scopes.")
                print("\nTo fix:")
                print("1. Go to: https://github.com/settings/tokens")
                print("2. Click on your token")
                print("3. Add 'public_repo' scope (or 'repo' for private repos)")
                print("4. Or generate a new token with correct scopes")
                print("="*60 + "\n")
                return False

            if response.status_code != 200:
                print(f"⚠ Warning: Unexpected response from GitHub API: {response.status_code}")
                return True  # Continue anyway

            # Token is valid
            user_data = response.json()
            username = user_data.get("login", "unknown")
            print(f"✓ GitHub token validated for user: {username}")
            return True

        except requests.exceptions.RequestException as e:
            print(f"⚠ Warning: Could not validate GitHub token: {e}")
            return True  # Continue anyway

    def _check_rate_limit(self) -> None:
        """Check and display current rate limit status."""
        response = self.session.get(f"{self.BASE_URL}/rate_limit")
        if response.status_code == 200:
            data = response.json()
            core = data.get("resources", {}).get("core", {})
            remaining = core.get("remaining", 0)
            reset_time = core.get("reset", 0)

            if remaining < 10:
                reset_dt = datetime.fromtimestamp(reset_time, tz=timezone.utc)
                wait_seconds = (reset_dt - datetime.now(timezone.utc)).total_seconds()
                print(f"⚠ Rate limit low: {remaining} requests remaining")
                if wait_seconds > 0:
                    print(f"  Resets in {wait_seconds:.0f} seconds")
            else:
                print(f"✓ Rate limit: {remaining} requests remaining")

    def get_user_events(
        self, username: str, per_page: int = 100
    ) -> List[Dict[str, Any]]:
        """Fetch all user events with pagination."""
        events = []
        page = 1

        self._check_rate_limit()

        while True:
            url = f"{self.BASE_URL}/users/{username}/events"
            params = {"per_page": per_page, "page": page}

            response = self.session.get(url, params=params)

            if response.status_code == 403:
                # Rate limit exceeded
                reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
                if reset_time:
                    reset_dt = datetime.fromtimestamp(reset_time, tz=timezone.utc)
                    wait_seconds = (reset_dt - datetime.now(timezone.utc)).total_seconds()
                    print(f"⚠ Rate limit exceeded. Waiting {wait_seconds:.0f} seconds...")
                    time.sleep(max(wait_seconds + 1, 0))
                    continue
                else:
                    raise Exception("Rate limit exceeded and no reset time provided")

            if response.status_code != 200:
                raise Exception(
                    f"GitHub API error: {response.status_code} - {response.text}"
                )

            page_events = response.json()
            if not page_events:
                break

            events.extend(page_events)
            print(f"  Fetched page {page} ({len(page_events)} events)")

            # GitHub events API returns max 300 events (10 pages)
            if page >= 10 or len(page_events) < per_page:
                break

            page += 1
            time.sleep(0.5)  # Be nice to the API

        return events

    def get_commit_details(
        self, repo_full_name: str, commit_sha: str
    ) -> Optional[Dict[str, Any]]:
        """Fetch detailed commit information including files changed."""
        url = f"{self.BASE_URL}/repos/{repo_full_name}/commits/{commit_sha}"

        try:
            response = self.session.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                print(
                    f"⚠ Failed to fetch commit {commit_sha}: {response.status_code}"
                )
                return None
        except Exception as e:
            print(f"⚠ Error fetching commit {commit_sha}: {e}")
            return None


class CommitProcessor:
    """Processes and filters commits from GitHub events."""

    def __init__(
        self,
        since: datetime,
        repo_filters: List[str],
        exclude_repos: List[str],
    ):
        self.since = since
        self.repo_filters = repo_filters
        self.exclude_repos = exclude_repos

    def extract_commits(
        self, events: List[Dict[str, Any]], api_client: GitHubAPIClient
    ) -> List[Dict[str, Any]]:
        """Extract and process commits from events."""
        commits = []
        seen_commits = set()
        push_events_count = 0
        empty_payloads_count = 0

        for event in events:
            # Only process PushEvents
            if event.get("type") != "PushEvent":
                continue

            # Check event timestamp
            event_time_str = event.get("created_at", "")
            try:
                event_time = datetime.fromisoformat(
                    event_time_str.replace("Z", "+00:00")
                )
            except ValueError:
                continue

            if event_time < self.since:
                continue

            # Get repository info
            repo = event.get("repo", {})
            repo_name = repo.get("name", "")

            # Apply filters
            if self._should_exclude_repo(repo_name):
                continue

            # Process each commit in the push
            payload = event.get("payload", {})
            push_commits = payload.get("commits", [])

            push_events_count += 1
            if not push_commits:
                empty_payloads_count += 1

            for commit in push_commits:
                commit_sha = commit.get("sha", "")
                if commit_sha in seen_commits:
                    continue

                seen_commits.add(commit_sha)

                # Get detailed commit info (including files)
                detailed_commit = api_client.get_commit_details(repo_name, commit_sha)

                if detailed_commit:
                    processed = self._process_commit(
                        commit, detailed_commit, repo_name, event_time
                    )
                    commits.append(processed)
                    time.sleep(0.3)  # Rate limiting

        # Warn if all push events had empty commit payloads
        if push_events_count > 0 and empty_payloads_count == push_events_count:
            print("\n" + "="*60)
            print("⚠ WARNING: GitHub Events API Returned Empty Commit Data")
            print("="*60)
            print(f"\nFound {push_events_count} push events, but all had empty commit payloads.")
            print("\nThis usually means:")
            print("1. Your GITHUB_TOKEN may be invalid or expired")
            print("2. The token lacks required scopes (needs 'repo' or 'public_repo')")
            print("3. GitHub's Events API has limitations for your account")
            print("\nTo fix:")
            print("1. Check your .env file has a valid GITHUB_TOKEN")
            print("2. Generate a new token: https://github.com/settings/tokens")
            print("3. Ensure the token has 'public_repo' scope")
            print("4. Update .env and remove .last_build file")
            print("="*60 + "\n")

        return commits

    def _should_exclude_repo(self, repo_name: str) -> bool:
        """Check if repository should be excluded."""
        # Check exclude list
        repo_short_name = repo_name.split("/")[-1]
        if repo_short_name in self.exclude_repos or repo_name in self.exclude_repos:
            return True

        # Check include filters (if specified)
        if self.repo_filters:
            if (
                repo_short_name not in self.repo_filters
                and repo_name not in self.repo_filters
            ):
                return True

        return False

    def _process_commit(
        self,
        commit: Dict[str, Any],
        detailed_commit: Dict[str, Any],
        repo_name: str,
        event_time: datetime,
    ) -> Dict[str, Any]:
        """Process and extract commit data."""
        commit_data = detailed_commit.get("commit", {})
        author_data = commit_data.get("author", {})

        # Extract files changed
        files = []
        for file_info in detailed_commit.get("files", []):
            files.append(
                {
                    "filename": file_info.get("filename", ""),
                    "status": file_info.get("status", ""),
                    "additions": file_info.get("additions", 0),
                    "deletions": file_info.get("deletions", 0),
                    "changes": file_info.get("changes", 0),
                }
            )

        return {
            "sha": commit.get("sha", ""),
            "message": commit_data.get("message", ""),
            "date": author_data.get("date", event_time.isoformat()),
            "author": author_data.get("name", "Unknown"),
            "author_email": author_data.get("email", ""),
            "repository": repo_name,
            "url": detailed_commit.get("html_url", ""),
            "files": files,
            "stats": {
                "additions": detailed_commit.get("stats", {}).get("additions", 0),
                "deletions": detailed_commit.get("stats", {}).get("deletions", 0),
                "total": detailed_commit.get("stats", {}).get("total", 0),
            },
        }

    def group_by_repository(
        self, commits: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Group commits by repository."""
        grouped = {}
        for commit in commits:
            repo = commit.get("repository", "")
            if repo not in grouped:
                grouped[repo] = []
            grouped[repo].append(commit)

        return grouped


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Fetch GitHub commits since last run",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview commits without writing output file",
    )
    parser.add_argument(
        "--config",
        default="config.yml",
        help="Path to config file (default: config.yml)",
    )
    parser.add_argument(
        "--output",
        default="data/commits.json",
        help="Output file path (default: data/commits.json)",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("GitHub Commits Fetcher")
    print("=" * 60)

    try:
        # Load configuration
        print("\n[1/5] Loading configuration...")
        config = ConfigReader(config_path=args.config)
        config.load()

        username = config.get_github_username()
        if not username:
            print("✗ GitHub username not found in config")
            sys.exit(1)

        print(f"  GitHub user: {username}")

        # Determine time range
        print("\n[2/5] Determining time range...")
        tracker = TimestampTracker()
        last_run = tracker.read()

        if last_run:
            since = last_run
            print(f"  Last run: {last_run.isoformat()}")
        else:
            lookback_days = config.get_lookback_days()
            since = datetime.now(timezone.utc) - timedelta(days=lookback_days)
            print(f"  No previous run found, looking back {lookback_days} days")

        print(f"  Fetching commits since: {since.isoformat()}")

        # Fetch commits
        print("\n[3/5] Fetching commits from GitHub...")
        api_client = GitHubAPIClient(token=config.github_token)

        # Validate token before proceeding
        if not api_client.validate_token():
            print("✗ Cannot proceed with invalid GitHub token")
            sys.exit(1)

        events = api_client.get_user_events(username)
        print(f"  Fetched {len(events)} events total")

        # Process commits
        print("\n[4/5] Processing commits...")
        processor = CommitProcessor(
            since=since,
            repo_filters=config.get_repo_filters(),
            exclude_repos=config.get_exclude_repos(),
        )
        commits = processor.extract_commits(events, api_client)
        print(f"  Found {len(commits)} commits")

        # Group by repository
        grouped_commits = processor.group_by_repository(commits)
        print(f"  Commits across {len(grouped_commits)} repositories")

        for repo, repo_commits in grouped_commits.items():
            print(f"    - {repo}: {len(repo_commits)} commits")

        # Output results
        print("\n[5/5] Writing output...")
        output_data = {
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "since": since.isoformat(),
            "total_commits": len(commits),
            "repositories": grouped_commits,
        }

        if args.dry_run:
            print("\n⚠ DRY RUN MODE - No files will be written")
            print("\nPreview of output:")
            print(json.dumps(output_data, indent=2))
        else:
            # Create output directory if needed
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write JSON output
            with open(output_path, "w") as f:
                json.dump(output_data, f, indent=2)

            print(f"✓ Written to {output_path}")

            # Update timestamp
            tracker.write()

        print("\n" + "=" * 60)
        print("✓ Complete!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
