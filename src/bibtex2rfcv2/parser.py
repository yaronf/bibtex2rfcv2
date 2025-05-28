"""BibTeX parser module."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Union

import bibtexparser


@dataclass
class BibTeXEntry:
    """A BibTeX entry."""

    entry_type: str
    key: str
    fields: Dict[str, str]


def parse_bibtex(source: Union[str, Path]) -> List[BibTeXEntry]:
    """Parse BibTeX content from a file or string.

    Args:
        source: Either a path to a BibTeX file or a string containing BibTeX content.

    Returns:
        A list of BibTeXEntry objects.

    Raises:
        ValueError: If the input is invalid BibTeX.
    """
    parser = bibtexparser.bparser.BibTexParser(common_strings=True)
    
    if isinstance(source, (str, Path)):
        if isinstance(source, Path):
            content = source.read_text()
        else:
            content = source
            
        try:
            entries = bibtexparser.loads(content, parser=parser)
        except Exception as e:
            raise ValueError(f"Failed to parse BibTeX: {e}")
    else:
        raise TypeError("source must be a string or Path")

    # Check if we got any entries
    if not entries.entries:
        # If the content is not empty, it's probably invalid BibTeX
        if content.strip():
            raise ValueError("No valid BibTeX entries found in input")
        return []

    result = []
    for entry in entries.entries:
        result.append(
            BibTeXEntry(
                entry_type=entry["ENTRYTYPE"],
                key=entry["ID"],
                fields={k: v for k, v in entry.items() if k not in ("ENTRYTYPE", "ID")},
            )
        )

    return result 