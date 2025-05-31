"""Converter from BibTeXEntry to kdrfc format using YAML for references."""

import logging
import yaml
from typing import Optional, Any
from bibtex2rfcv2.models import BibTeXEntry
from bibtex2rfcv2.error_handling import InvalidInputError, ConversionError, logger

def _try_convert_to_int(value: str) -> Any:
    """Try to convert a string to an integer, return original string if conversion fails."""
    try:
        return int(value)
    except ValueError:
        return value

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
    if not entry.fields.get("author") and not entry.fields.get("editor") or not entry.fields.get("title"):
        logger.error("Missing required fields: author or editor, and title")
        raise InvalidInputError("Missing required fields: author or editor, and title")
    try:
        title = entry.get_field("title") or "Untitled"
        authors = entry.get_authors()
        if not authors:
            editors = entry.get_field("editor")
            if editors:
                editors_clean = " ".join(editors.split())
                authors = [editor.strip() for editor in editors_clean.split(" and ") if editor.strip()]
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
            yaml_dict[entry.key]["date"] = {"year": _try_convert_to_int(year)}
            if month:
                yaml_dict[entry.key]["date"]["month"] = month

        # Add entry type specific fields
        if entry.entry_type == "article":
            journal = entry.get_field("journal")
            volume = entry.get_field("volume")
            number = entry.get_field("number")
            pages = entry.get_field("pages")
            if journal:
                yaml_dict[entry.key]["journal"] = journal
            if volume:
                yaml_dict[entry.key]["volume"] = _try_convert_to_int(volume)
            if number:
                yaml_dict[entry.key]["number"] = _try_convert_to_int(number)
            if pages:
                yaml_dict[entry.key]["pages"] = pages
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
            if booktitle:
                yaml_dict[entry.key]["booktitle"] = booktitle
            if publisher:
                yaml_dict[entry.key]["publisher"] = publisher
            if pages:
                yaml_dict[entry.key]["pages"] = pages
        elif entry.entry_type == "techreport":
            institution = entry.get_field("institution")
            number = entry.get_field("number")
            if institution:
                yaml_dict[entry.key]["institution"] = institution
            if number:
                yaml_dict[entry.key]["number"] = _try_convert_to_int(number)
        elif entry.entry_type in ["mastersthesis", "phdthesis", "thesis"]:
            school = entry.get_field("school")
            if school:
                yaml_dict[entry.key]["school"] = school

        # Add common optional fields
        url = entry.get_field("url")
        doi = entry.get_field("doi")
        abstract = entry.get_field("abstract")
        note = entry.get_field("note")

        if url:
            yaml_dict[entry.key]["url"] = url
        if doi:
            yaml_dict[entry.key]["doi"] = doi
        if abstract:
            yaml_dict[entry.key]["abstract"] = abstract
        if note:
            yaml_dict[entry.key]["note"] = note

        # Serialize the dictionary to YAML text
        yaml_output = yaml.dump(yaml_dict, default_flow_style=False)
        return yaml_output
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        raise ConversionError(f"Conversion failed: {e}") from e 