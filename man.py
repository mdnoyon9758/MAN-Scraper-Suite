#!/usr/bin/env python3
"""
Simplified MAN CLI.
"""

import click

@click.group()
def cli():
    pass

@cli.command()
@click.argument('url')
@click.option('--dynamic', is_flag=True, help='Use dynamic scraping')
@click.option('--output', type=str, help='Output filename')
@click.option('--format', type=click.Choice(['json', 'csv', 'excel']), default='json')
def scrape(url: str, dynamic: bool, output: str, format: str):
    """Scrape a single webpage."""
    click.echo(f"Scraping {url} with format {format}...")

# Placeholder command for Google Auth with success page
@cli.command()
def google_auth():
    """Authenticate using Google OAuth"""
    click.echo("Opening browser for Google OAuth...")
    click.echo("Google Authentication Successful! Visit: /success.html")

if __name__ == '__main__':
    cli()
