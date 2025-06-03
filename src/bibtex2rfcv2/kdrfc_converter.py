"""Converter from BibTeXEntry to kdrfc format using YAML for references."""

import logging
import yaml
from typing import Optional, Any, Dict, List, TextIO, Union
from bibtex2rfcv2.models import BibTeXEntry, BibTeXEntryType
from typing import Optional, Any
from bibtex2rfcv2.models import BibTeXEntry
from bibtex2rfcv2.error_handling import InvalidInputError, ConversionError, logger
from bibtex2rfcv2.utils import latex_to_unicode

def _try_convert_to_int(value: str) -> Any:
    """Try to convert a string to an integer, return original string if conversion fails."""
    try:
        return int(value)
    except ValueError:
        return value

def _field_to_str(val):
    """Safely convert a BibTeX field value to a string for YAML output."""
    if isinstance(val, list):
        # If list contains dicts with 'name', return the first name
        if val and isinstance(val[0], dict) and 'name' in val[0]:
            return val[0]['name']
        else:
            return str(val[0]) if val else ''
    elif isinstance(val, dict):
        # If dict has 'name', use it
        if 'name' in val:
            return val['name']
        else:
            return str(val)
    elif val is None:
        return ''
    else:
        return str(val)

def _convert_author_name(name: str) -> str:
    """Convert author name from 'Last, First' to 'First Last' format."""
    name = name.strip()
    if ', ' in name:
        parts = name.split(', ', 1)
        return parts[1] + ' ' + parts[0]
    return name

def _flatten_to_str(val):
    """Recursively flatten lists and join all string elements with a space."""
    if isinstance(val, list):
        return ' '.join(_flatten_to_str(item) for item in val)
    elif isinstance(val, str):
        return val
    elif val is None:
        return ''
    else:
        return str(val)

def bibtex_entry_to_kdrfc(entry: BibTeXEntry) -> str:
    """Convert a BibTeXEntry to kdrfc format using YAML for references.

    Args:
        entry: The BibTeXEntry to convert.

    Returns:
        A string containing the kdrfc reference in YAML format.

    Raises:
        InvalidInputError: If required fields are missing.
        ConversionError: If conversion fails unexpectedly.
    """
    logger.info(f"Converting entry: {entry.key} of type {entry.entry_type}")
    if not entry.fields.get("author") and not entry.fields.get("editor") or not entry.fields.get("title"):
        logger.error("Missing required fields: author or editor, and title")
        raise InvalidInputError("Missing required fields: author or editor, and title")
    try:
        # Preserve line breaks in title
        title = entry.get_field("title") or "Untitled"
        title = _flatten_to_str(title).replace("\\n", "\n")
        if not title:
            title = "Untitled"
        
        # Get authors
        authors = []
        author_field = entry.get_field('author')
        if author_field:
            if isinstance(author_field, list):
                # If it's already a list, process each name
                for name in author_field:
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
                        authors.append(name)
            else:
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
                        authors.append(name)
        
        # If no authors found, try editors
        if not authors:
            editor_field = entry.get_field('editor')
            if editor_field:
                if isinstance(editor_field, list):
                    # If it's already a list, process each name
                    for name in editor_field:
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
                            authors.append(name)
                else:
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
                            authors.append(name)
        
        # If still no authors, use "Unknown"
        if not authors:
            authors = ["Unknown"]

        # Build a dictionary structure for YAML
        yaml_dict = {
            entry.key: {
                "title": title,
                "author": [{"ins": author, "name": author} for author in authors]
            }
        }

        # Add date information
        year = entry.get_field("year")
        month = entry.get_field("month")
        if year:
            date_dict = {"year": _try_convert_to_int(year)}
            if month:
                date_dict["month"] = month
            yaml_dict[entry.key]["date"] = date_dict

        # Add entry type specific fields
        if entry.entry_type == "article":
            journal = entry.get_field("journal")
            volume = entry.get_field("volume")
            number = entry.get_field("number")
            pages = entry.get_field("pages")
            publisher = entry.get_field("publisher")
            if journal:
                yaml_dict[entry.key]["journal"] = journal
            if volume:
                yaml_dict[entry.key]["volume"] = _try_convert_to_int(volume)
            if number:
                yaml_dict[entry.key]["number"] = _try_convert_to_int(number)
            if pages:
                yaml_dict[entry.key]["pages"] = pages
            if publisher:
                yaml_dict[entry.key]["publisher"] = publisher
        elif entry.entry_type == "book":
            publisher = entry.get_field("publisher")
            edition = entry.get_field("edition")
            isbn = entry.get_field("isbn")
            if publisher:
                yaml_dict[entry.key]["publisher"] = publisher
            if edition:
                yaml_dict[entry.key]["edition"] = _try_convert_to_int(edition)
            if isbn:
                yaml_dict[entry.key]["isbn"] = isbn
        elif entry.entry_type in ["conference", "inproceedings", "proceedings"]:
            booktitle = entry.get_field("booktitle")
            publisher = entry.get_field("publisher")
            pages = entry.get_field("pages")
            editors = entry.get_field("editor")
            if booktitle:
                yaml_dict[entry.key]["booktitle"] = booktitle
            if publisher:
                yaml_dict[entry.key]["publisher"] = publisher
            if pages:
                yaml_dict[entry.key]["pages"] = pages
            if editors:
                editors_str = _field_to_str(editors)
                yaml_dict[entry.key]["editor"] = editors_str
        elif entry.entry_type == "techreport":
            institution = entry.get_field("institution")
            number = entry.get_field("number")
            publisher = entry.get_field("publisher")
            if institution:
                yaml_dict[entry.key]["institution"] = institution
            if number:
                yaml_dict[entry.key]["number"] = _try_convert_to_int(number)
            if publisher:
                yaml_dict[entry.key]["publisher"] = publisher
        elif entry.entry_type in ["mastersthesis", "phdthesis", "thesis"]:
            school = entry.get_field("school")
            if school:
                yaml_dict[entry.key]["school"] = school

        # Add common optional fields
        url = entry.get_field("url")
        doi = entry.get_field("doi")
        abstract = entry.get_field("abstract")
        note = entry.get_field("note")
        publisher = entry.get_field("publisher")
        number = entry.get_field("number")
        editor = entry.get_field("editor")

        if url:
            url_str = _field_to_str(url)
            logger.debug(f"url field type: {type(url_str)}, value: {url_str}")
            yaml_dict[entry.key]["url"] = url_str
        if doi:
            doi_str = _field_to_str(doi)
            logger.debug(f"doi field type: {type(doi_str)}, value: {doi_str}")
            yaml_dict[entry.key]["doi"] = doi_str
        if abstract:
            abstract_str = _field_to_str(abstract)
            logger.debug(f"abstract field type: {type(abstract_str)}, value: {abstract_str}")
            yaml_dict[entry.key]["abstract"] = abstract_str
        if note:
            note_str = _field_to_str(note)
            logger.debug(f"note field type: {type(note_str)}, value: {note_str}")
            yaml_dict[entry.key]["note"] = note_str
        if publisher:
            publisher_str = _field_to_str(publisher)
            logger.debug(f"publisher field type: {type(publisher_str)}, value: {publisher_str}")
            yaml_dict[entry.key]["publisher"] = publisher_str
        if number:
            num_str = _field_to_str(number)
            logger.debug(f"number field type: {type(num_str)}, value: {num_str}")
            yaml_dict[entry.key]["number"] = _try_convert_to_int(num_str)

        # Serialize the dictionary to YAML text
        yaml_output = yaml.dump(yaml_dict, default_flow_style=False)
        logger.info(f"Generated YAML output: {yaml_output}")
        return yaml_output
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        raise ConversionError(f"Conversion failed: {e}") from e 