
"""
Blog Update Orchestrator
Runs the complete blog update workflow: fetch commits -> generate post -> build Jekyll site.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple

import yaml


class Colors:
    """ANSI color codes for terminal output."""

    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


class WorkflowOrchestrator:
    """Orchestrates the blog update workflow."""

    def __init__(
        self,
        config_path: str = "config.yml",
        dry_run: bool = False,
        skip_build: bool = False,
        example_mode: bool = False,
    ):
        self.config_path = Path(config_path)
        self.dry_run = dry_run
        self.skip_build = skip_build
        self.example_mode = example_mode
        self.scripts_dir = Path("scripts")
        self.work_dir = Path()
        self.default_build_path = Path("jekyll/_site")

    def print_step(self, step: int, total: int, message: str) -> None:
        """Print a step header."""
        print(f"\n{Colors.BOLD}[{step}/{total}] {message}{Colors.ENDC}")
        print("=" * 60)

    def print_success(self, message: str) -> None:
        """Print success message."""
        print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")

    def print_error(self, message: str) -> None:
        """Print error message."""
        print(f"{Colors.RED}✗ {message}{Colors.ENDC}")

    def print_warning(self, message: str) -> None:
        """Print warning message."""
        print(f"{Colors.YELLOW}⚠ {message}{Colors.ENDC}")

    def print_info(self, message: str) -> None:
        """Print info message."""
        print(f"{Colors.CYAN}ℹ {message}{Colors.ENDC}")

    def run_command(
        self, command: list, description: str, capture_output: bool = True
    ) -> Tuple[bool, str, str]:
        """Run a shell command and return success status and output."""
        if self.dry_run:
            self.print_info(f"DRY RUN: Would run: {' '.join(command)}")
            return True, "", ""

        try:
            self.print_info(f"{description}...")
            result = subprocess.run(
                command,
                capture_output=capture_output,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                self.print_success(f"{description} completed")
                return True, result.stdout, result.stderr
            else:
                self.print_error(
                    f"{description} failed with exit code {result.returncode}"
                )
                if result.stderr:
                    print(f"  Error: {result.stderr}")
                return False, result.stdout, result.stderr

        except Exception as e:
            self.print_error(f"{description} failed: {e}")
            return False, "", str(e)

    def check_commits_found(self, commits_json_path: Path) -> Tuple[bool, int]:
        """Check if commits were found in the JSON file."""
        if not commits_json_path.exists():
            return False, 0

        try:
            with open(commits_json_path, "r") as f:
                data = json.load(f)
                total_commits = data.get("total_commits", 0)
                return total_commits > 0, total_commits
        except Exception as e:
            self.print_error(f"Failed to read commits JSON: {e}")
            return False, 0

    def load_config(self) -> dict:
        """Load configuration from config.yml."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, "r") as f:
            return yaml.safe_load(f)

    def step_fetch_commits(self) -> bool:
        """Step 1: Fetch commits from GitHub."""
        if self.example_mode:
            self.print_step(1, 4, "Loading example commits")
        else:
            self.print_step(1, 4, "Fetching commits from GitHub")

        # Use uv run to execute the fetch-commits command
        command = ["uv", "run", "fetch-commits", "--config", str(self.config_path)]
        if self.dry_run:
            command.append("--dry-run")
        if self.example_mode:
            command.append("--example")

        success, stdout, stderr = self.run_command(
            command, "Running fetch_commits.py", capture_output=True
        )

        if success:
            # Print relevant output
            for line in stdout.split("\n"):
                if "Found" in line or "commits" in line or "repositories" in line:
                    print(f"  {line}")
            return True
        else:
            if stdout:
                print(stdout)
            if stderr:
                print(stderr)
            return False

    def step_check_commits(self) -> Tuple[bool, int]:
        """Step 2: Check if commits were found."""
        self.print_step(2, 4, "Checking for new commits")

        commits_json = Path("data/commits.json")

        if self.dry_run:
            self.print_info("DRY RUN: Skipping commit check")
            return True, 3  # Assume some commits for dry run

        found, count = self.check_commits_found(commits_json)

        if found:
            self.print_success(f"Found {count} commits to process")
            return True, count
        else:
            self.print_warning("No new commits found")
            return False, 0

    def step_generate_post(self) -> bool:
        """Step 3: Generate blog post from commits."""
        self.print_step(3, 4, "Generating blog post")

        # Use uv run to execute the generate-post command
        command = [
            "uv",
            "run",
            "generate-post",
            "--config",
            str(self.config_path),
            "--input",
            "data/commits.json",
        ]

        if self.dry_run:
            command.append("--preview")

        success, stdout, stderr = self.run_command(
            command, "Running generate_post.py", capture_output=True
        )

        if success:
            # Print relevant output
            for line in stdout.split("\n"):
                if "✓" in line or "Generated" in line or "Written" in line:
                    print(f"  {line}")
            return True
        else:
            if stdout:
                print(stdout)
            if stderr:
                print(stderr)
            return False

    def step_sync_jekyll_config(self) -> bool:
        """Step 4: Sync Jekyll configuration from config.yml."""
        self.print_step(4, 6, "Syncing Jekyll configuration")

        # Use uv run to execute the sync command
        command = [
            "uv",
            "run",
            "sync-jekyll-config",
            "--config",
            str(self.config_path),
        ]

        success, stdout, stderr = self.run_command(
            command, "Syncing Jekyll config", capture_output=True
        )

        if success:
            self.print_success("Jekyll configuration synced")
            return True
        else:
            self.print_error("Failed to sync Jekyll configuration")
            if stdout:
                print(stdout)
            if stderr:
                print(stderr)
            return False

    def step_process_human_posts(self) -> bool:
        """Step 5: Process human-written posts and add frontmatter."""
        self.print_step(5, 6, "Processing human-written posts")

        # Use uv run to execute the process-human-posts command
        command = [
            "uv",
            "run",
            "process-human-posts",
            "--posts-dir",
            "jekyll/_posts",
        ]

        if self.dry_run:
            command.append("--dry-run")

        success, stdout, stderr = self.run_command(
            command, "Processing human posts", capture_output=True
        )

        if success:
            # Print relevant output
            for line in stdout.split("\n"):
                if "Processing:" in line or "Processed:" in line or "Complete!" in line:
                    print(f"  {line}")
            return True
        else:
            # This is not a critical failure - continue even if processing fails
            self.print_warning("Human post processing had issues (continuing anyway)")
            if stdout:
                print(stdout)
            if stderr:
                print(stderr)
            return True  # Continue workflow

    def step_build_jekyll(self) -> bool:
        """Step 6: Build Jekyll site."""
        self.print_step(6, 6, "Building Jekyll site")

        if self.skip_build:
            self.print_info("Skipping Jekyll build (--skip-build flag)")
            return True

        # Check if bundle is available
        bundle_check = subprocess.run(
            ["which", "bundle"], capture_output=True, text=True
        )

        if bundle_check.returncode != 0:
            self.print_warning("Bundle not found, skipping Jekyll build")
            self.print_info("Install with: gem install bundler && bundle install")
            return True

        # Check if Gemfile exists
        jekyll_dir = Path("jekyll")
        if not (jekyll_dir / "Gemfile").exists():
            self.print_warning("Gemfile not found, skipping Jekyll build")
            return True

        # Determine build destination
        build_dest = os.environ.get('JEKYLL_BUILD_DESTINATION', '_site')

        # Run bundle exec from jekyll directory
        command = ["bundle", "exec", "jekyll", "build", "--destination", build_dest]

        if self.dry_run:
            self.print_info(f"DRY RUN: Would run: {' '.join(command)} (from jekyll/ directory)")
            return True

        try:
            self.print_info("Building Jekyll site...")
            result = subprocess.run(
                command,
                cwd=jekyll_dir,  # Run from jekyll directory
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                self.print_success("Building Jekyll site completed")
                self.print_success("Jekyll site built successfully")
                self.print_info(f"Site available in jekyll/{build_dest}/ directory")
                return True
            else:
                self.print_error(f"Building Jekyll site failed with exit code {result.returncode}")
                self.print_error("Jekyll build failed")
                if result.stdout:
                    print(result.stdout)
                if result.stderr:
                    print(result.stderr)
                return False

        except Exception as e:
            self.print_error(f"Building Jekyll site failed: {e}")
            return False

    def run(self) -> int:
        """Run the complete workflow."""
        print(f"{Colors.BOLD}{Colors.HEADER}")
        print("=" * 60)
        print("Blog Update Workflow")
        print("=" * 60)
        print(Colors.ENDC)

        if self.dry_run:
            self.print_warning("DRY RUN MODE - No files will be written")
            print()

        try:
            # Load config to validate it exists
            config = self.load_config()
            self.print_success(f"Loaded configuration from {self.config_path}")
            print()

            # Step 1: Fetch commits
            if not self.step_fetch_commits():
                self.print_error("Failed to fetch commits")
                return 1

            # Step 2: Check if commits found
            has_commits, commit_count = self.step_check_commits()

            # Check if no-update posts are enabled
            enable_no_update = config.get("automation", {}).get("enable_no_update_posts", False)

            if not has_commits and not enable_no_update:
                self.print_info("No new commits to process, exiting")
                print()
                print("=" * 60)
                self.print_success("Workflow complete (no new commits)")
                print("=" * 60)
                return 0
            elif not has_commits and enable_no_update:
                self.print_info("No commits found, but no-update posts are enabled")
                commit_count = 0

            # Step 3: Generate post
            if not self.step_generate_post():
                self.print_error("Failed to generate blog post")
                return 1

            # Step 4: Sync Jekyll configuration
            if not self.step_sync_jekyll_config():
                self.print_error("Failed to sync Jekyll configuration")
                return 1

            # Step 5: Process human-written posts
            if not self.step_process_human_posts():
                self.print_error("Failed to process human posts")
                return 1

            # Step 6: Build Jekyll site
            if not self.step_build_jekyll():
                self.print_error("Failed to build Jekyll site")
                return 1

            # Success!
            print()
            print(f"{Colors.BOLD}{Colors.GREEN}")
            print("=" * 60)
            print("✓ Workflow Complete!")
            print("=" * 60)
            print(Colors.ENDC)
            print()
            self.print_info(f"Processed {commit_count} commits")
            if not self.dry_run and not self.skip_build:
                self.print_info("Site built and ready to deploy")
                self.print_info("View locally with: cd jekyll && bundle exec jekyll serve")

            return 0

        except FileNotFoundError as e:
            self.print_error(str(e))
            return 1
        except Exception as e:
            self.print_error(f"Unexpected error: {e}")
            import traceback

            traceback.print_exc()
            return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run complete blog update workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full workflow
  %(prog)s

  # Dry run to test without side effects
  %(prog)s --dry-run

  # Skip Jekyll build step
  %(prog)s --skip-build

  # Use custom config
  %(prog)s --config custom-config.yml

  # Use example data (no GitHub API calls)
  %(prog)s --example
        """,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Test workflow without writing files",
    )
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Skip Jekyll build step",
    )
    parser.add_argument(
        "--config",
        default="config.yml",
        help="Path to config file (default: config.yml)",
    )
    parser.add_argument(
        "--example",
        action="store_true",
        help="Use example commit data instead of fetching from GitHub",
    )

    args = parser.parse_args()

    orchestrator = WorkflowOrchestrator(
        config_path=args.config,
        dry_run=args.dry_run,
        skip_build=args.skip_build,
        example_mode=args.example,
    )

    exit_code = orchestrator.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
