"""Setup command for Tootles configuration."""

import webbrowser

import click
import httpx

from tootles.config.manager import ConfigManager


class MastodonApp:
    """Represents a Mastodon application registration."""

    def __init__(self, instance: str, base_url: str, client_id: str, client_secret: str):
        self.instance = instance
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret


async def create_app(base_url: str) -> MastodonApp:
    """Register a new application with the Mastodon instance."""
    url = f"{base_url}/api/v1/apps"

    data = {
        'client_name': 'Tootles',
        'redirect_uris': 'urn:ietf:wg:oauth:2.0:oob',
        'scopes': 'read write follow',
        'website': 'https://github.com/tootles/tootles',
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=data)
            response.raise_for_status()
            app_data = response.json()

            # Extract domain from base_url for instance name
            instance = base_url.replace('https://', '').replace('http://', '').rstrip('/')

            return MastodonApp(
                instance=instance,
                base_url=base_url,
                client_id=app_data['client_id'],
                client_secret=app_data['client_secret']
            )
        except httpx.HTTPError as e:
            raise click.ClickException(f"Failed to register app with {base_url}: {e}") from e


def get_browser_login_url(app: MastodonApp) -> str:
    """Generate the OAuth authorization URL."""
    from urllib.parse import urlencode

    params = {
        "response_type": "code",
        "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
        "scope": "read write follow",
        "client_id": app.client_id,
    }

    return f"{app.base_url}/oauth/authorize/?{urlencode(params)}"


async def request_access_token(app: MastodonApp, authorization_code: str) -> str:
    """Exchange authorization code for access token."""
    url = f"{app.base_url}/oauth/token"

    data = {
        'grant_type': 'authorization_code',
        'client_id': app.client_id,
        'client_secret': app.client_secret,
        'code': authorization_code,
        'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, data=data, follow_redirects=False)
            response.raise_for_status()
            token_data = response.json()
            return token_data['access_token']
        except httpx.HTTPError as e:
            raise click.ClickException(f"Failed to get access token: {e}") from e


def validate_instance_url(ctx, param, value: str) -> str:
    """Validate and normalize instance URL."""
    if not value:
        return value

    # Add https:// if no protocol specified
    if not value.startswith(('http://', 'https://')):
        value = f"https://{value}"

    # Remove trailing slash
    value = value.rstrip('/')

    return value


@click.command()
@click.option(
    "--instance", "-i",
    prompt="Enter your Mastodon instance URL",
    default="https://mastodon.social",
    callback=validate_instance_url,
    help="Domain or base URL of your Mastodon instance (e.g., 'mastodon.social' or 'https://mastodon.social')"
)
def setup(instance: str):
    """Set up Tootles with your Mastodon account using browser authentication."""
    import asyncio

    async def setup_flow():
        click.echo(f"Setting up Tootles for {instance}...")

        # Register app with the instance
        try:
            app = await create_app(instance)
            click.echo(f"✓ Registered Tootles with {instance}")
        except Exception as e:
            raise click.ClickException(f"Failed to register with instance: {e}") from e

        # Generate authorization URL
        auth_url = get_browser_login_url(app)

        # Show instructions
        click.echo("\n" + "="*60)
        click.echo("AUTHORIZATION REQUIRED")
        click.echo("="*60)
        click.echo("Tootles needs permission to access your Mastodon account.")
        click.echo("You will be redirected to your instance's authorization page.")
        click.echo("After granting permission, you'll receive an authorization code.")
        click.echo("="*60)

        click.echo("\nAuthorization URL:")
        click.echo(auth_url)

        # Ask to open browser
        open_browser = click.prompt(
            "\nOpen this URL in your browser? [Y/n]",
            default="Y",
            show_default=False
        )

        if not open_browser or open_browser.lower() == 'y':
            try:
                webbrowser.open(auth_url)
                click.echo("✓ Opened authorization page in your browser")
            except Exception:
                click.echo("⚠ Could not open browser automatically")
                click.echo("Please copy and paste the URL above into your browser")

        # Get authorization code
        click.echo("\nAfter authorizing Tootles, you'll see an authorization code.")
        authorization_code = ""
        while not authorization_code:
            authorization_code = click.prompt("Enter the authorization code").strip()

        # Exchange code for token
        try:
            access_token = await request_access_token(app, authorization_code)
            click.echo("✓ Successfully obtained access token")
        except Exception as e:
            raise click.ClickException(f"Failed to get access token: {e}") from e

        # Save configuration
        config_manager = ConfigManager()
        config_manager.config.instance_url = instance
        config_manager.config.access_token = access_token
        config_manager.save_config()

        click.echo(f"✓ Configuration saved to {config_manager.config_path}")
        click.echo("\n🎉 Setup complete! You can now run 'tootles' to start the application.")

    # Run the async setup flow
    asyncio.run(setup_flow())


if __name__ == "__main__":
    setup()
