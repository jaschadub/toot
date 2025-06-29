"""CLI entry point for Tootles."""

import sys
from pathlib import Path
from typing import Optional

import click

from tootles.cli.setup import setup
from tootles.main import main as run_app


# Override the group to make 'run' the default command
@click.group(invoke_without_command=True)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Path to configuration file",
)
@click.version_option()
@click.pass_context
def cli(ctx: click.Context, config: Optional[Path]):
    """Tootles - Modern Textual-based Mastodon client."""
    if ctx.invoked_subcommand is None:
        # No subcommand provided, run the main app
        try:
            run_app(config)
        except KeyboardInterrupt:
            click.echo("Interrupted by user", err=True)
            sys.exit(1)
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)


@cli.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Path to configuration file",
)
def run(config: Optional[Path]) -> None:
    """Run the Tootles application."""
    try:
        run_app(config)
    except KeyboardInterrupt:
        click.echo("Interrupted by user", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# Add the setup command
cli.add_command(setup)


if __name__ == "__main__":
    cli()
