"""BibTeX parser module."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Union, TextIO

import bibtexparser
from bibtex2rfcv2.models import BibTeXEntry, BibTeXEntryType
from bibtex2rfcv2.error_handling import InvalidInputError, FileNotFoundError


def parse_bibtex(source: Union[str, Path, TextIO]) -> List[BibTeXEntry]:
    """Parse BibTeX content from a file, string, or file-like object.

    Args:
        source: Either a path to a BibTeX file, a string containing BibTeX content,
               or a file-like object (like stdin).

    Returns:
        A list of BibTeXEntry objects.

    Raises:
        InvalidInputError: If the input is invalid BibTeX or wrong type.
        FileNotFoundError: If the file cannot be read.
    """
    parser = bibtexparser.bparser.BibTexParser(common_strings=True)
    content = None
    if isinstance(source, (str, Path)):
        if isinstance(source, Path):
            try:
                print(f"Reading file: {source}")  # Debugging statement
                content = source.read_text()
                print(f"Content read: {content}")  # Debugging statement
            except Exception as e:
                raise FileNotFoundError(f"Could not read file: {source}") from e
        else:
            content = source
            print(f"Parsing content from string: {content}")  # Debugging statement
    elif hasattr(source, 'read'):
        # Handle file-like objects (like stdin)
        content = source.read()
    else:
        raise InvalidInputError("source must be a string, Path, or file-like object")

    try:
        entries = bibtexparser.loads(content, parser=parser)
    except Exception as e:
        raise InvalidInputError(f"Failed to parse BibTeX: {e}") from e

    # Check if we got any entries
    if not entries.entries:
        if content and content.strip():
            raise InvalidInputError("No valid BibTeX entries found in input")
        return []

    result = []
    for entry in entries.entries:
        result.append(
            BibTeXEntry(
                entry_type=BibTeXEntryType(entry["ENTRYTYPE"]),
                key=entry["ID"],
                fields={k: v for k, v in entry.items() if k not in ("ENTRYTYPE", "ID")},
            )
        )
    return result 