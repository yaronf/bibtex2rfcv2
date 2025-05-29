"""Command-line interface for BibTeX to RFC converter."""

import sys
from typing import Optional
import os

import click
from bibtex2rfcv2.converter import bibtex_entry_to_rfcxml
from bibtex2rfcv2.parser import parse_bibtex
from pathlib import Path

from bibtex2rfcv2 import __version__


@click.group()
@click.version_option(version=__version__)
def main() -> None:
    """Convert BibTeX citations to RFC-compliant XML references."""
    pass


@main.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
def convert(input_file: str, output_file: str) -> None:
    """Convert a BibTeX file to RFC XML format."""
    try:
        # Check if the input file is readable
        if not os.access(input_file, os.R_OK):
            click.echo(f'Error: Permission denied: {input_file} is not readable.', err=True)
            sys.exit(1)
        entries = parse_bibtex(Path(input_file))
        with open(output_file, 'w') as f:
            for entry in entries:
                xml = bibtex_entry_to_rfcxml(entry)
                f.write(xml + '\n')
        click.echo(f'Conversion completed. Output written to {output_file}.')
    except Exception as e:
        click.echo(f'Error: {e}', err=True)
        sys.exit(1)


if __name__ == "__main__":
    main() 