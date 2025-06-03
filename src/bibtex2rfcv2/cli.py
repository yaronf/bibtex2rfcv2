"""Command-line interface for BibTeX to RFC converter."""

import sys
from typing import Optional
import os
import logging

import click
from bibtex2rfcv2.xml_converter import bibtex_entry_to_rfcxml
from bibtex2rfcv2.parser import parse_bibtex
from pathlib import Path
from tqdm import tqdm
from bibtex2rfcv2.kdrfc_converter import bibtex_entry_to_kdrfc

from bibtex2rfcv2 import __version__

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version=__version__)
def main() -> None:
    """Convert BibTeX citations to RFC-compliant XML references."""
    pass


@main.command()
@click.argument("input_file")
@click.argument("output_file")
@click.option("--progress/--no-progress", default=True, help="Show progress bar")
def to_xml(input_file: str, output_file: str, progress: bool) -> None:
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

        if not entries:
            click.echo('Warning: No BibTeX entries found in input.', err=True)
            sys.exit(0)

        # Handle stdout
        if output_file == '-':
            for entry in tqdm(entries, desc="Converting entries", disable=not progress):
                logger.info("Calling bibtex_entry_to_rfcxml for entry: %s", entry)
                xml = bibtex_entry_to_rfcxml(entry)
                click.echo(xml)
        else:
            with open(output_file, 'w') as f:
                for entry in tqdm(entries, desc="Converting entries", disable=not progress):
                    logger.info("Calling bibtex_entry_to_rfcxml for entry: %s", entry)
                    xml = bibtex_entry_to_rfcxml(entry)
                    f.write(xml + '\n')
            click.echo(f'Conversion completed. {len(entries)} entries written to {output_file}.', err=True)
    except Exception as e:
        click.echo(f'Error: {e}', err=True)
        sys.exit(1)


@main.command()
@click.argument("input_file")
@click.argument("output_file")
@click.option("--progress/--no-progress", default=True, help="Show progress bar")
def to_kdrfc(input_file: str, output_file: str, progress: bool) -> None:
    """Convert a BibTeX file to kdrfc format.
    
    Use '-' for input_file to read from stdin.
    Use '-' for output_file to write to stdout.
    """
    try:
        # Handle stdin
        if input_file == '-':
            logger.info("Reading from stdin.")
            entries = parse_bibtex(sys.stdin)
        else:
            # Custom permission check
            if not os.path.exists(input_file):
                logger.error(f'Error: File not found: {input_file}')
                click.echo(f'Error: File not found: {input_file}', err=True)
                sys.exit(1)
            if not os.access(input_file, os.R_OK):
                logger.error(f'Error: Permission denied: {input_file} is not readable.')
                click.echo(f'Error: Permission denied: {input_file} is not readable.', err=True)
                sys.exit(1)
            logger.info(f"Reading from file: {input_file}")
            entries = parse_bibtex(Path(input_file))

        if not entries:
            logger.warning('No BibTeX entries found in input.')
            click.echo('Warning: No BibTeX entries found in input.', err=True)
            sys.exit(0)

        # Handle stdout
        if output_file == '-':
            logger.info("Writing to stdout.")
            for entry in tqdm(entries, desc="Converting entries", disable=not progress):
                logger.info("Calling bibtex_entry_to_kdrfc for entry: %s", entry)
                yaml = bibtex_entry_to_kdrfc(entry)
                click.echo(yaml)
        else:
            logger.info(f"Writing to file: {output_file}")
            with open(output_file, 'w') as f:
                for entry in tqdm(entries, desc="Converting entries", disable=not progress):
                    logger.info("Calling bibtex_entry_to_kdrfc for entry: %s", entry)
                    yaml = bibtex_entry_to_kdrfc(entry)
                    f.write(yaml + '\n')
            click.echo(f'Conversion completed. {len(entries)} entries written to {output_file}.', err=True)
            print(f"Output of to-kdrfc command: {yaml}")
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        click.echo(f'Error: {e}', err=True)
        sys.exit(1)


if __name__ == "__main__":
    main() 