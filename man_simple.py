#!/usr/bin/env python3
"""
Simplified MAN CLI - Easy Access
"""

import click

@click.group()
def cli():
    pass

@cli.command()
@click.argument('url')
@click.option('--format', type=click.Choice(['json', 'csv', 'excel']), default='json',
              help='Output format')
def scrape(url: str, format: str):
    """Scrape a webpage easily"""
    click.echo(f"Scraping {url} in format {format}...")

@cli.command()
def google_auth():
    """Authenticate via Google OAuth for simple access"""
    click.echo("Starting Google OAuth authentication...")
    click.echo("Success! Visit: /success.html for details")

if __name__ == '__main__':
    cli()

