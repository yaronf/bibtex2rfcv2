"""Converter from BibTeXEntry to RFC XML v3 reference."""

import logging
from typing import Optional
import re
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, TextIO, Union

from bibtex2rfcv2.models import BibTeXEntry, BibTeXEntryType
from bibtex2rfcv2.xml_models import (
    Author,
    Date,
    SeriesInfo,
    Front,
    Reference,
)
from bibtex2rfcv2.utils import latex_to_unicode, extract_ascii
from bibtex2rfcv2.error_handling import InvalidInputError, FileNotFoundError, ConversionError, logger

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def normalize_month(month: str) -> str:
    """Normalize month string to RFC XML v3 format.
    
    Args:
        month: Month string from BibTeX
        
    Returns:
        Normalized month string (1-12)
    """
    month_map = {
        "jan": "1", "january": "1",
        "feb": "2", "february": "2",
        "mar": "3", "march": "3",
        "apr": "4", "april": "4",
        "may": "5",
        "jun": "6", "june": "6",
        "jul": "7", "july": "7",
        "aug": "8", "august": "8",
        "sep": "9", "september": "9",
        "oct": "10", "october": "10",
        "nov": "11", "november": "11",
        "dec": "12", "december": "12",
    }
    # Handle BibDataStringExpression by converting to string first
    month_str = str(month).lower()
    return month_map.get(month_str, month_str)


def bibtex_entry_to_rfcxml(entry: BibTeXEntry) -> str:
    """Convert a BibTeXEntry to an RFC XML v3 reference.

    Args:
        entry: The BibTeXEntry to convert.

    Returns:
        A string containing the XML representation of the reference.

    Raises:
        InvalidInputError: If the entry cannot be converted.
    """
    if not entry.fields.get("author") and not entry.fields.get("editor") or not entry.fields.get("title"):
        logger.error("Missing required fields: author or editor, and title")
        raise InvalidInputError("Missing required fields: author or editor, and title")
    try:
        # --- Begin conversion logic ---
        logger.info(f"Generated XML for entry {entry.key} ({entry.entry_type}):")
        
        # Get authors
        authors = []
        author_field = entry.get_field('author')
        if author_field:
            # Split on ' and ' but not within braces
            author_names = []
            current = ""
            brace_level = 0
            for char in author_field:
                if char == '{':
                    brace_level += 1
                elif char == '}':
                    brace_level -= 1
                elif char == 'a' and brace_level == 0 and current.endswith(' '):
                    # Check for ' and ' pattern
                    if current.endswith(' and '):
                        author_names.append(current[:-5].strip())
                        current = ""
                        continue
                current += char
            if current:
                author_names.append(current.strip())
            
            # Process each author name
            for name in author_names:
                # Remove outer braces and convert LaTeX to Unicode
                name = name.strip('{}')
                name = latex_to_unicode(name)
                
                # Convert "Last, First" to "First Last"
                if ', ' in name:
                    parts = name.split(', ', 1)
                    name = parts[1] + ' ' + parts[0]
                
                # Clean up whitespace
                name = ' '.join(name.split())
                if name:
                    authors.append(Author(name))
        
        # If no authors found, try editors
        if not authors:
            editor_field = entry.get_field('editor')
            if editor_field:
                # Split on ' and ' but not within braces
                editor_names = []
                current = ""
                brace_level = 0
                for char in editor_field:
                    if char == '{':
                        brace_level += 1
                    elif char == '}':
                        brace_level -= 1
                    elif char == 'a' and brace_level == 0 and current.endswith(' '):
                        # Check for ' and ' pattern
                        if current.endswith(' and '):
                            editor_names.append(current[:-5].strip())
                            current = ""
                            continue
                    current += char
                if current:
                    editor_names.append(current.strip())
                
                # Process each editor name
                for name in editor_names:
                    # Remove outer braces and convert LaTeX to Unicode
                    name = name.strip('{}')
                    name = latex_to_unicode(name)
                    
                    # Convert "Last, First" to "First Last"
                    if ', ' in name:
                        parts = name.split(', ', 1)
                        name = parts[1] + ' ' + parts[0]
                    
                    # Clean up whitespace
                    name = ' '.join(name.split())
                    if name:
                        authors.append(Author(name))
        
        # If still no authors, use "Unknown"
        if not authors:
            authors = [Author("Unknown")]

        # Create series info list
        series_info = []
        
        # Add year if present
        if "year" in entry.fields:
            series_info.append(SeriesInfo(name="Year", value=entry.fields["year"]))
        
        # Add month if present
        if "month" in entry.fields:
            month_value = normalize_month(entry.fields["month"])
            series_info.append(SeriesInfo(name="Month", value=month_value))
        
        # Add journal if present
        if "journal" in entry.fields:
            series_info.append(SeriesInfo(name="Journal", value=entry.fields["journal"]))
        
        # Add booktitle if present
        if "booktitle" in entry.fields:
            series_info.append(SeriesInfo(name="Booktitle", value=entry.fields["booktitle"]))
        
        # Add other fields as series info
        for field, value in entry.fields.items():
            if field not in ["year", "month", "journal", "booktitle", "author", "title", "abstract", "note"]:
                # Map BibTeX field names to RFCXML field names
                field_mapping = {
                    'isbn': 'ISBN',
                    'doi': 'DOI',
                    'date-modified': 'DateModified',
                    'number': 'Report Number',
                    'url': 'URL',
                    'howpublished': 'HowPublished',
                    'publisher': 'Publisher',
                }
                # Ensure value is a string and not None
                if value is not None:
                    value_str = str(value)
                    # Special handling for URLs and DOIs
                    if field.lower() == 'url':
                        series_info.append(SeriesInfo(name="URL", value=value_str))
                    elif field.lower() == 'doi':
                        series_info.append(SeriesInfo(name="DOI", value=value_str))
                    else:
                        field_name = field_mapping.get(field.lower(), field.capitalize())
                        series_info.append(SeriesInfo(name=field_name, value=value_str))

        # Create the reference
        ref = Reference(
            anchor=entry.key,
            front=Front(
                title=entry.fields.get("title", ""),
                authors=authors,
                abstract=entry.fields.get("abstract"),
                note=entry.fields.get("note"),
                ascii_abstract=extract_ascii(entry.fields.get("abstract")) if entry.fields.get("abstract") else None,
                ascii_note=extract_ascii(entry.fields.get("note")) if entry.fields.get("note") else None
            ),
            series_info=series_info
        )
        
        logger.info(f"<reference anchor=\"{ref.anchor}\">\n  <front>\n  <title>{ref.front.title}</title>")
        for author in ref.front.authors:
            logger.info(f"  <author fullname=\"{author.fullname}\"/>")
        logger.info("</front>")
        for info in ref.series_info:
            logger.info(f"  <seriesInfo name=\"{info.name}\" value=\"{info.value}\"/>")
        logger.info("</reference>")
        
        return ref.to_xml()
        # --- End conversion logic ---
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        raise ConversionError(f"Conversion failed: {e}") from e 