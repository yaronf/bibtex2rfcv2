"""Converter from BibTeXEntry to kdrfc format using YAML for references."""

import logging
from typing import Optional
from bibtex2rfcv2.models import BibTeXEntry
from bibtex2rfcv2.error_handling import InvalidInputError, ConversionError, logger

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
        # --- Begin conversion logic ---
        title = entry.get_field("title") or "Untitled"
        authors = entry.get_authors()
        if not authors:
            editors = entry.get_field("editor")
            if editors:
                # Split editors by ' and ' and add all as authors
                editors_clean = " ".join(editors.split())
                authors = [editor.strip() for editor in editors_clean.split(" and ") if editor.strip()]
        if not authors:
            authors = ["Unknown"]
        # Create YAML structure
        yaml_output = f"{entry.key}:\n"
        yaml_output += f"  author:\n"
        for author in authors:
            yaml_output += f"  - ins: {author}\n"
            yaml_output += f"    name: {author}\n"
        yaml_output += f"  title: {title}\n"
        # Add other fields as needed
        # --- End conversion logic ---
        return yaml_output
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        raise ConversionError(f"Conversion failed: {e}") from e 