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
@click.argument("input_file")
@click.argument("output_file")
def convert(input_file: str, output_file: str) -> None:
    """Convert a BibTeX file to RFC XML format.
    
    Use '-' for input_file to read from stdin.
    Use '-' for output_file to write to stdout.
    """
    try:
        # Handle stdin
        if input_file == '-':
            entries = parse_bibtex(sys.stdin)
        else:
            # Custom permission check
            if not os.path.exists(input_file):
                click.echo(f'Error: File not found: {input_file}', err=True)
                sys.exit(1)
            if not os.access(input_file, os.R_OK):
                click.echo(f'Error: Permission denied: {input_file} is not readable.', err=True)
                sys.exit(1)
            entries = parse_bibtex(Path(input_file))

        # Handle stdout
        if output_file == '-':
            for entry in entries:
                xml = bibtex_entry_to_rfcxml(entry)
                click.echo(xml)
        else:
            with open(output_file, 'w') as f:
                for entry in entries:
                    xml = bibtex_entry_to_rfcxml(entry)
                    f.write(xml + '\n')
            click.echo(f'Conversion completed. Output written to {output_file}.', err=True)
    except Exception as e:
        click.echo(f'Error: {e}', err=True)
        sys.exit(1)


if __name__ == "__main__":
    main() 