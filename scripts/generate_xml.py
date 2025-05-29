#!/usr/bin/env python3
"""Script to generate XML from a BibTeX entry."""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path
import re

# Add src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.append(str(src_path))

from bibtex2rfcv2.models import BibTeXEntry, BibTeXEntryType
from bibtex2rfcv2.converter import latex_to_unicode

def generate_xml(entry: BibTeXEntry) -> str:
    """Generate XML representation of a BibTeX entry.
    
    Args:
        entry: The BibTeX entry to convert
        
    Returns:
        str: XML representation of the entry
    """
    # Create root element
    root = ET.Element("reference")
    
    # Add entry type as an attribute
    root.set("type", entry.entry_type.value)
    
    # Add key as an attribute
    root.set("key", entry.key)
    
    # Add all fields as child elements
    for field_name, field_value in entry.fields.items():
        # Skip empty values
        if not field_value:
            continue
            
        # Convert LaTeX accents to Unicode
        field_value_unicode = latex_to_unicode(field_value)
        
        # Create field element
        field_elem = ET.SubElement(root, field_name)
        field_elem.text = field_value_unicode
    
    # Convert to string with pretty printing
    ET.indent(root, space="  ")
    return ET.tostring(root, encoding="unicode")

def main():
    """Main function to demonstrate XML generation."""
    # Exact DBLP entry from sigcomm2023.bibtex
    entry = BibTeXEntry(
        entry_type=BibTeXEntryType.INPROCEEDINGS,
        key="DBLP:conf/5g-memu/AlmasanSLCB23",
        fields={
            "author": "Paul Almasan and Jos{\'e} Su{\'a}rez{-}Varela and Andra Lutu and Albert Cabellos{-}Aparicio and Pere Barlet{-}Ros",
            "title": "Enhancing 5G Radio Planning with Graph Representations and Deep Learning",
            "booktitle": "5G-MeMZ@SIGCOMM",
            "pages": "14--20",
            "publisher": "ACM",
            "year": "2023"
        }
    )
    
    # Generate and print XML
    xml_str = generate_xml(entry)
    print(xml_str)

if __name__ == "__main__":
    main() 