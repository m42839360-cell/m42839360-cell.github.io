
"""
Human Posts Processor
Processes bare markdown files in jekyll/_posts/ and adds Jekyll frontmatter.
Uses git history to determine creation and modification dates.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple


class RepoCloner:
    """Clones a git repository to a temporary directory."""

    @staticmethod
    def clone_repo(repo_url: str, branch: str = "main") -> Optional[Path]:
        """Clone repository to temporary directory.

        Args:
            repo_url: Git repository URL
            branch: Branch to clone (default: main)

        Returns:
            Path to temporary directory, or None if cloning failed
        """
        try:
            temp_dir = Path(tempfile.mkdtemp(prefix="human-posts-"))
            print(f"📦 Cloning {repo_url} (branch: {branch})...")

            result = subprocess.run(
                ["git", "clone", "--depth", "1", "--branch", branch, repo_url, str(temp_dir)],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                print(f"   ✓ Cloned to: {temp_dir}")
                return temp_dir
            else:
                print(f"   ✗ Clone failed: {result.stderr}")
                # Clean up failed clone
                shutil.rmtree(temp_dir, ignore_errors=True)
                return None

        except Exception as e:
            print(f"   ✗ Clone failed: {e}")
            return None

    @staticmethod
    def cleanup(temp_dir: Path) -> None:
        """Remove temporary directory.

        Args:
            temp_dir: Path to temporary directory
        """
        try:
            if temp_dir and temp_dir.exists():
                shutil.rmtree(temp_dir)
                print(f"🧹 Cleaned up temporary directory")
        except Exception as e:
            print(f"⚠ Warning: Could not clean up {temp_dir}: {e}")


class GitDateExtractor:
    """Extracts creation and modification dates from git history."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root

    def get_file_dates(self, file_path: Path) -> Tuple[Optional[datetime], Optional[datetime]]:
        """Get creation and last modified dates from git log.

        Args:
            file_path: Path to the file

        Returns:
            Tuple of (creation_date, last_modified_date) as datetime objects
            Returns (None, None) if file is not tracked in git
        """
        try:
            # Get creation date (first commit that added the file)
            result = subprocess.run(
                ["git", "log", "--diff-filter=A", "--follow", "--format=%aI", "--", str(file_path)],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False,
            )

            creation_date = None
            if result.returncode == 0 and result.stdout.strip():
                # Get the last line (earliest commit)
                lines = result.stdout.strip().split("\n")
                if lines:
                    creation_date = datetime.fromisoformat(lines[-1])

            # Get last modified date (most recent commit)
            result = subprocess.run(
                ["git", "log", "-1", "--format=%aI", "--", str(file_path)],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False,
            )

            last_modified = None
            if result.returncode == 0 and result.stdout.strip():
                last_modified = datetime.fromisoformat(result.stdout.strip())

            return creation_date, last_modified

        except Exception as e:
            print(f"⚠ Warning: Could not extract git dates for {file_path}: {e}")
            return None, None


class MarkdownParser:
    """Parses markdown files to extract title and check for frontmatter."""

    @staticmethod
    def has_frontmatter(content: str) -> bool:
        """Check if content already has Jekyll frontmatter."""
        return content.strip().startswith("---")

    @staticmethod
    def extract_title(content: str, filename: str) -> str:
        """Extract title from first # heading or generate from filename.

        Args:
            content: Markdown content
            filename: Name of the file (without extension)

        Returns:
            Extracted or generated title
        """
        # Try to find first # heading
        lines = content.strip().split("\n")
        for line in lines:
            if line.strip().startswith("# "):
                title = line.strip()[2:].strip()
                if title:
                    return title

        # Fallback: generate from filename
        # Remove date prefix if present (YYYY-MM-DD-)
        name = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", filename)
        # Replace hyphens/underscores with spaces and title case
        title = name.replace("-", " ").replace("_", " ").title()
        return title


class FrontmatterGenerator:
    """Generates Jekyll frontmatter for human posts."""

    @staticmethod
    def generate(
        title: str,
        creation_date: Optional[datetime],
        last_modified: Optional[datetime],
        categories: str = "blog",
    ) -> str:
        """Generate Jekyll frontmatter.

        Args:
            title: Post title
            creation_date: When the file was first committed (or None for current time)
            last_modified: When the file was last modified (or None to omit)
            categories: Space-separated categories

        Returns:
            Formatted frontmatter string
        """
        # Use creation date or current time
        if creation_date:
            date = creation_date
        else:
            date = datetime.now(timezone.utc)

        frontmatter_lines = [
            "---",
            "layout: post",
            f'title: "{title}"',
            f"date: {date.strftime('%Y-%m-%d %H:%M:%S %z')}",
        ]

        # Add last_modified if different from creation date
        if last_modified and creation_date and last_modified != creation_date:
            frontmatter_lines.append(f"last_modified: {last_modified.strftime('%Y-%m-%d %H:%M:%S %z')}")

        frontmatter_lines.extend([
            f"categories: {categories}",
            "author_type: human",
            "---",
            "",
        ])

        return "\n".join(frontmatter_lines)


class HumanPostProcessor:
    """Processes human-written posts and adds frontmatter."""

    def __init__(
        self,
        source_dir: str = "human-posts",
        dest_dir: str = "jekyll/_posts",
        dry_run: bool = False,
        repo_url: Optional[str] = None,
        repo_branch: str = "main"
    ):
        self.source_dir = Path(source_dir)
        self.dest_dir = Path(dest_dir)
        self.dry_run = dry_run
        self.repo_url = repo_url
        self.repo_branch = repo_branch
        self.temp_dir: Optional[Path] = None
        self.repo_root = self._find_repo_root()
        self.git_extractor = GitDateExtractor(self.repo_root) if self.repo_root else None

    def _find_repo_root(self) -> Optional[Path]:
        """Find git repository root."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                return Path(result.stdout.strip())
        except Exception:
            pass
        return None

    def process_file(self, file_path: Path) -> bool:
        """Process a single markdown file from source and copy to destination.

        Args:
            file_path: Path to the markdown file in source directory

        Returns:
            True if file was processed, False if skipped
        """
        # Read file
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"✗ Error reading {file_path}: {e}")
            return False

        # Skip if already has frontmatter (shouldn't happen in source dir, but check anyway)
        if MarkdownParser.has_frontmatter(content):
            print(f"⚠ Skipping {file_path.name}: already has frontmatter")
            return False

        print(f"📝 Processing: {file_path.name}")

        # Extract title
        filename_without_ext = file_path.stem
        title = MarkdownParser.extract_title(content, filename_without_ext)
        print(f"   Title: {title}")

        # Get dates from git
        creation_date = None
        last_modified = None

        if self.git_extractor:
            creation_date, last_modified = self.git_extractor.get_file_dates(file_path)
            if creation_date:
                print(f"   Created: {creation_date.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print(f"   ⚠ Not in git, using current time")

            if last_modified and creation_date and last_modified != creation_date:
                print(f"   Modified: {last_modified.strftime('%Y-%m-%d %H:%M:%S')}")

        # Generate frontmatter
        frontmatter = FrontmatterGenerator.generate(title, creation_date, last_modified)

        # Combine frontmatter with content
        new_content = frontmatter + "\n" + content

        # Determine destination filename with date prefix (Jekyll requirement)
        date_for_filename = creation_date if creation_date else datetime.now(timezone.utc)
        date_prefix = date_for_filename.strftime("%Y-%m-%d")

        # Always use date prefix for destination
        if not re.match(r"^\d{4}-\d{2}-\d{2}-", file_path.name):
            dest_filename = f"{date_prefix}-{file_path.name}"
        else:
            dest_filename = file_path.name

        dest_file_path = self.dest_dir / dest_filename

        # Write to destination (or dry run)
        if self.dry_run:
            print(f"   [DRY RUN] Would copy to: {dest_file_path}")
            print(f"   Preview:")
            print("   " + "\n   ".join(frontmatter.split("\n")[:8]))
        else:
            try:
                # Ensure destination directory exists
                self.dest_dir.mkdir(parents=True, exist_ok=True)

                # Write to destination with frontmatter
                with open(dest_file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)

                print(f"   ✓ Copied to: {dest_file_path}")
            except Exception as e:
                print(f"   ✗ Error writing file: {e}")
                return False

        return True

    def process_all(self) -> Tuple[int, int]:
        """Process all markdown files from source directory to destination.

        If repo_url is provided, clones the repository first.

        Returns:
            Tuple of (processed_count, skipped_count)
        """
        # Clone repository if URL is provided
        if self.repo_url:
            self.temp_dir = RepoCloner.clone_repo(self.repo_url, self.repo_branch)
            if not self.temp_dir:
                print(f"✗ Failed to clone repository")
                return 0, 0

            # Update source directory to point to cloned repo
            self.source_dir = self.temp_dir / "human-posts"
            # Update git extractor to use cloned repo
            self.repo_root = self.temp_dir
            self.git_extractor = GitDateExtractor(self.repo_root)

        try:
            if not self.source_dir.exists():
                print(f"✗ Source directory not found: {self.source_dir}")
                return 0, 0

            # Find all markdown files in source
            md_files = sorted(self.source_dir.glob("*.md"))

            if not md_files:
                print(f"ℹ No markdown files found in {self.source_dir}")
                return 0, 0

            processed = 0
            skipped = 0

            for file_path in md_files:
                if self.process_file(file_path):
                    processed += 1
                else:
                    skipped += 1

            return processed, skipped

        finally:
            # Clean up temporary directory if we cloned
            if self.temp_dir:
                RepoCloner.cleanup(self.temp_dir)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Process human-written posts and copy to Jekyll with frontmatter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all posts from human-posts/ to jekyll/_posts/
  %(prog)s

  # Dry run to preview changes
  %(prog)s --dry-run

  # Custom directories
  %(prog)s --source-dir my-posts --dest-dir jekyll/_posts

This script:
- Scans human-posts/ for markdown files (bare markdown, no frontmatter)
- Extracts dates from git history (creation and last modified)
- Extracts title from first # heading or filename
- Generates Jekyll frontmatter with author_type: human
- Copies to jekyll/_posts/ with date prefix (YYYY-MM-DD-filename.md)
- Falls back to current time if file is not in git yet
        """,
    )

    parser.add_argument(
        "--source-dir",
        default="human-posts",
        help="Path to source directory with human posts (default: human-posts)",
    )
    parser.add_argument(
        "--dest-dir",
        default="jekyll/_posts",
        help="Path to destination directory (default: jekyll/_posts)",
    )
    parser.add_argument(
        "--repo-url",
        help="Git repository URL to clone (optional, for Docker deployments)",
    )
    parser.add_argument(
        "--repo-branch",
        default="main",
        help="Git branch to clone (default: main)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying files",
    )

    args = parser.parse_args()

    processor = HumanPostProcessor(
        source_dir=args.source_dir,
        dest_dir=args.dest_dir,
        dry_run=args.dry_run,
        repo_url=args.repo_url,
        repo_branch=args.repo_branch
    )

    print("=" * 60)
    print("Human Posts Processor")
    print("=" * 60)
    print()

    if args.dry_run:
        print("⚠ DRY RUN MODE - No files will be modified")
        print()

    processed, skipped = processor.process_all()

    print()
    print("=" * 60)
    print(f"✓ Complete!")
    print(f"  Processed: {processed} file(s)")
    print(f"  Skipped: {skipped} file(s) (already have frontmatter)")
    print("=" * 60)

    return 0 if processed >= 0 else 1


if __name__ == "__main__":
    sys.exit(main())
