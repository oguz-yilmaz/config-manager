import json
import os
from typing import Optional

import click

from .config_manager import ConfigManager
from .storage import Storage


@click.group()
def cli():
    """Configuration Management System CLI"""
    pass


@cli.command()
@click.argument("path")
@click.option("--environment", "-e", default="prod")
@click.option("--api-key", envvar="CONFIG_API_KEY")
def get(path: str, environment: str, api_key: str):
    """Get configuration value"""
    config_manager = _get_config_manager(api_key)
    try:
        config = config_manager.get_config(path, environment)
        click.echo(json.dumps(config, indent=2))
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)


@cli.command()
@click.argument("path")
@click.argument("config_file", type=click.File("r"))
@click.option("--api-key", envvar="CONFIG_API_KEY")
def update(path: str, config_file, api_key: str):
    """Update configuration from file"""
    config_manager = _get_config_manager(api_key)
    try:
        config = json.load(config_file)
        config_manager.update_config(path, config, api_key)
        click.echo("Configuration updated successfully")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)


def _get_config_manager(api_key: Optional[str] = None) -> ConfigManager:
    if not api_key:
        raise click.UsageError("API key is required")

    storage = Storage(
        host=os.getenv("ETCD_HOST", "localhost"),
        port=int(os.getenv("ETCD_PORT", "2379")),
    )
    return ConfigManager(storage, api_key)


if __name__ == "__main__":
    cli()
