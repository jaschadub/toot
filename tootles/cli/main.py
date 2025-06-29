"""CLI entry point for Tootles."""

import sys
from pathlib import Path
from typing import Optional

import click

from tootles.main import main as run_app


@click.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Path to configuration file",
)
@click.version_option()
def main(config: Optional[Path]) -> None:
    """Tootles - Modern Textual-based Mastodon client."""
    try:
        run_app(config)
    except KeyboardInterrupt:
        click.echo("Interrupted by user", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
