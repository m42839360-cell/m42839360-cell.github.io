"""
Jekyll Configuration Sync
Generates jekyll/_config.yml from the main config.yml file using a template.
"""

import argparse
import sys
from pathlib import Path
from typing import Any, Dict

import yaml
from jinja2 import Template


class ConfigLoader:
    """Loads configuration from config.yml."""

    def __init__(self, config_path: str = "config.yml"):
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}

    def load(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, "r") as f:
            self.config = yaml.safe_load(f)
            print(f"✓ Loaded config from {self.config_path}")
            return self.config

    def get_jekyll_config(self) -> Dict[str, Any]:
        """Extract Jekyll configuration section."""
        jekyll_config = self.config.get("jekyll", {})
        if not jekyll_config:
            raise ValueError("No 'jekyll' section found in config.yml")
        return jekyll_config


class JekyllConfigGenerator:
    """Generates Jekyll _config.yml from user configuration using a template."""

    def __init__(self, jekyll_config: Dict[str, Any], template_path: str = "jekyll/_config.yml.template"):
        self.jekyll_config = jekyll_config
        self.template_path = Path(template_path)

    def load_template(self) -> str:
        """Load the template file.

        Returns:
            Template content as string
        """
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template file not found: {self.template_path}")

        with open(self.template_path, "r") as f:
            return f.read()

    def generate(self) -> str:
        """Generate complete Jekyll configuration YAML from template.

        Returns:
            Complete Jekyll _config.yml content as string
        """
        # Extract user settings with defaults
        title = self.jekyll_config.get("title", "My Blog")
        description = self.jekyll_config.get("description", "")
        author = self.jekyll_config.get("author", "")
        url = self.jekyll_config.get("url", "")
        baseurl = self.jekyll_config.get("baseurl", "")

        # Load template
        template_content = self.load_template()
        template = Template(template_content)

        # Render template with values
        rendered = template.render(
            title=title,
            description=description,
            author=author,
            url=url,
            baseurl=baseurl,
        )

        return rendered


class JekyllConfigWriter:
    """Writes Jekyll configuration to file."""

    def __init__(self, output_path: str = "jekyll/_config.yml"):
        self.output_path = Path(output_path)

    def write(self, content: str) -> None:
        """Write Jekyll config to file.

        Args:
            content: Complete YAML content to write
        """
        # Ensure directory exists
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.output_path, "w") as f:
            f.write(content)

        print(f"✓ Generated {self.output_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Sync Jekyll configuration from config.yml",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--config",
        default="config.yml",
        help="Path to main config file (default: config.yml)",
    )
    parser.add_argument(
        "--output",
        default="jekyll/_config.yml",
        help="Path to output Jekyll config (default: jekyll/_config.yml)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print generated config without writing to file",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Jekyll Configuration Sync")
    print("=" * 60)

    try:
        # Load main configuration
        print("\n[1/3] Loading configuration...")
        loader = ConfigLoader(config_path=args.config)
        loader.load()
        jekyll_config = loader.get_jekyll_config()

        print(f"  Title: {jekyll_config.get('title')}")
        print(f"  Author: {jekyll_config.get('author')}")
        print(f"  URL: {jekyll_config.get('url')}")

        # Generate Jekyll config
        print("\n[2/3] Generating Jekyll configuration...")
        generator = JekyllConfigGenerator(jekyll_config)
        config_content = generator.generate()
        print("  ✓ Configuration generated")

        # Write to file or print
        print("\n[3/3] Writing configuration...")
        if args.dry_run:
            print("\n⚠ DRY RUN - No files will be written")
            print("\nGenerated config:")
            print("=" * 60)
            print(config_content)
            print("=" * 60)
        else:
            writer = JekyllConfigWriter(output_path=args.output)
            writer.write(config_content)

        print("\n" + "=" * 60)
        print("✓ Complete!")
        print("=" * 60)

    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"\n✗ Configuration error: {e}")
        print("  Make sure config.yml has a 'jekyll' section")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
