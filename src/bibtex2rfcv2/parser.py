"""BibTeX parser module."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Union, TextIO, Any
import logging

import bibtexparser
from bibtexparser.customization import convert_to_unicode, editor, author
from bibtex2rfcv2.models import BibTeXEntry, BibTeXEntryType
from bibtex2rfcv2.error_handling import InvalidInputError, FileNotFoundError

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def _process_month_field(month_val: Any) -> str:
    """Process a month field value from BibTeX entry.
    
    Args:
        month_val: The raw month value from the BibTeX entry
        
    Returns:
        A string representation of the month value
        
    Note:
        Handles various data structures that might contain the month value:
        - BibDataStringExpression objects
        - Objects with .value attribute
        - Iterable objects
        - String values
    """
    print(f"DEBUG: month_val type: {type(month_val)}, value: {month_val}")  # Debug print
    try:
        # If it has a .l attribute (BibDataStringExpression), extract the .value of the first item
        if hasattr(month_val, 'l') and month_val.l and hasattr(month_val.l[0], 'value'):
            return month_val.l[0].value
        elif hasattr(month_val, 'value'):
            return month_val.value
        elif hasattr(month_val, '__iter__') and not isinstance(month_val, str):
            return ''.join(str(x) for x in month_val)
        else:
            return str(month_val)
    except Exception:
        return str(month_val)

def customizations(record):
    """Customize parsed entries.
    
    Args:
        record: A record dictionary
        
    Returns:
        The customized record
    """
    # Convert BibDataStringExpression objects to strings
    for key, val in record.items():
        if hasattr(val, 'l') and val.l and hasattr(val.l[0], 'value'):
            record[key] = val.l[0].value
        elif hasattr(val, 'value'):
            record[key] = val.value
        elif hasattr(val, '__iter__') and not isinstance(val, str):
            record[key] = ''.join(str(x) for x in val)
        else:
            record[key] = str(val)
    
    # Convert LaTeX to Unicode
    record = convert_to_unicode(record)
    
    # Use bibtexparser's built-in author/editor handling
    record = author(record)
    record = editor(record)
    
    # Normalize newlines and spaces in URL field
    if 'url' in record:
        record['url'] = ', '.join(url.strip() for url in record['url'].replace('\n', ',').split(','))
    
    return record

def extract_content(source: Union[str, Path, TextIO]) -> str:
    """Extract BibTeX content from a file, string, or file-like object.

    Args:
        source: Either a path to a BibTeX file, a string containing BibTeX content,
               or a file-like object (like stdin).

    Returns:
        A string containing the BibTeX content.

    Raises:
        InvalidInputError: If the input is invalid or wrong type.
        FileNotFoundError: If the file cannot be read.
    """
    if isinstance(source, (str, Path)):
        if isinstance(source, Path):
            try:
                print(f"Reading file: {source}")  # Debugging statement
                content = source.read_text()
                print(f"Content read: {content}")  # Debugging statement
            except UnicodeDecodeError as e:
                raise InvalidInputError(f"Could not decode file: {source}") from e
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
    return content

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
    logger.debug(f"Parsing BibTeX content from: {source}")
    # Configure parser to be lenient with unknown fields
    parser = bibtexparser.bparser.BibTexParser(
        common_strings=True,
        ignore_nonstandard_types=False,
        homogenize_fields=False,
        interpolate_strings=False,
        customization=customizations  # Use our customizations function during parsing
    )
    
    content = extract_content(source)

    try:
        entries = bibtexparser.loads(content, parser=parser)
        # No need to apply customizations here since we're using it in the parser
        logger.debug(f"Raw parsed entries: {entries.entries}")
        # Print the parsed entries for debugging
        print(f"Parsed entries: {entries.entries}")
        
        # Debug log the author/editor fields
        for entry in entries.entries:
            if 'author' in entry:
                logger.debug(f"Author field for {entry.get('ID', 'unknown')}: {entry['author']}")
            if 'editor' in entry:
                logger.debug(f"Editor field for {entry.get('ID', 'unknown')}: {entry['editor']}")
                
    except Exception as e:
        logger.error(f"Error parsing BibTeX: {e}")
        raise InvalidInputError(f"Failed to parse BibTeX: {e}") from e

    # Check if we got any entries
    if not entries.entries:
        if content and content.strip():
            raise InvalidInputError("No valid BibTeX entries found in input")
        return []

    result = []
    for entry in entries.entries:
        # Convert entry type to lowercase for case-insensitive matching
        entry_type = entry["ENTRYTYPE"].lower()
        # Handle the only special case: inproceeding -> inproceedings
        if entry_type == "inproceeding":
            entry_type = "inproceedings"
        
        # Convert BibDataStringExpression or similar objects to string for 'month'
        fields = {k: v for k, v in entry.items() if k not in ("ENTRYTYPE", "ID")}
        if "month" in fields:
            fields["month"] = _process_month_field(fields["month"])
            
        try:
            result.append(
                BibTeXEntry(
                    entry_type=BibTeXEntryType(entry_type),
                    key=entry["ID"],
                    fields=fields,
                )
            )
        except ValueError as e:
            logger.warning(f"Warning: Skipping entry with unsupported type '{entry_type}': {e}")
            continue
            
    return result 