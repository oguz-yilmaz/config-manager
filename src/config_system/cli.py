import click
import json

@click.group()
def cli():
    pass

@cli.command()
@click.argument('path')
def get(path):
    """Get configuration value"""
    click.echo(f"Getting config from {path}")
