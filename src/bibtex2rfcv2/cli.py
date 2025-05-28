"""Command-line interface for BibTeX to RFC converter."""

import sys
from typing import Optional

import click

from bibtex2rfcv2 import __version__


@click.group()
@click.version_option(version=__version__)
def main() -> None:
    """Convert BibTeX citations to RFC-compliant XML references."""
    pass


@main.command()
@click.argument("input_file", type=click.Path(exists=True), required=False)
@click.argument("output_file", type=click.Path(), required=False)
def convert(input_file: Optional[str], output_file: Optional[str]) -> None:
    """Convert BibTeX file to RFC XML format."""
    # TODO: Implement conversion logic
    click.echo("Conversion not yet implemented")


if __name__ == "__main__":
    main() 