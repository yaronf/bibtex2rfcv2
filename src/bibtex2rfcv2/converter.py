"""Converter from BibTeXEntry to RFC XML reference (expanded entry type support)."""

from xml.sax.saxutils import escape
from typing import Optional
import logging

from bibtex2rfcv2.models import BibTeXEntry, BibTeXEntryType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def bibtex_entry_to_rfcxml(entry: BibTeXEntry) -> str:
    """Convert a BibTeXEntry to an RFC XML reference (expanded entry type support).

    Args:
        entry: The BibTeXEntry to convert.

    Returns:
        A string containing the RFC XML reference.

    Raises:
        ValueError: If required fields are missing.
    """
    # Special field name mapping for <seriesInfo>
    special_field_names = {
        "url": "URL",
        "doi": "DOI",
        "date-modified": "DateModified",
        "howpublished": "HowPublished",
    }
    title = entry.get_field("title")
    year = entry.get_field("year")
    authors = entry.get_authors()
    # If no authors, try editors
    if not authors:
        editors = entry.get_field("editor")
        if editors:
            # Treat editors as authors, robustly splitting on ' and ' and handling newlines/whitespace
            editors_clean = " ".join(editors.split())  # collapse all whitespace/newlines to single spaces
            authors = [editor.strip() for editor in editors_clean.split(" and ") if editor.strip()]

    xml = [f'<reference anchor="{escape(entry.key)}">']
    xml.append(f'  <front>')
    # Always emit <title>
    xml.append(f'    <title>{escape(title)}</title>')
    # For proceedings entries, add organization as author
    if entry.entry_type == BibTeXEntryType.PROCEEDINGS:
        publisher = entry.get_field("publisher")
        if publisher:
            xml.append(f'    <author fullname="{escape(publisher)}"/>')
    # Split authors and create individual author elements
    for author in authors:
        xml.append(f'    <author fullname="{escape(author)}"/>')
    # Only emit <date> in front for non-proceedings entries
    if year and entry.entry_type != BibTeXEntryType.PROCEEDINGS:
        date_parts = [f'year="{escape(year)}"']
        month = entry.get_field("month")
        if month:
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
            month = month.lower()
            if month in month_map:
                month = month_map[month]
            date_parts.append(f'month="{escape(month)}"')
        day = entry.get_field("day")
        if day:
            date_parts.append(f'day="{escape(day)}"')
        xml.append(f'    <date {" ".join(date_parts)}/>')
    xml.append(f'  </front>')

    # Track handled fields
    handled_fields = {"title", "author", "editor", "year", "month", "day", "key"}

    # Add seriesInfo elements based on entry type
    if entry.entry_type == BibTeXEntryType.ARTICLE:
        journal = entry.get_field("journal")
        volume = entry.get_field("volume")
        number = entry.get_field("number")
        pages = entry.get_field("pages")
        if journal:
            xml.append(f'  <seriesInfo name="Journal" value="{escape(journal)}"/>')
            handled_fields.add("journal")
        if volume:
            xml.append(f'  <seriesInfo name="Volume" value="{escape(volume)}"/>')
            handled_fields.add("volume")
        if number:
            xml.append(f'  <seriesInfo name="Number" value="{escape(number)}"/>')
            handled_fields.add("number")
        if pages:
            xml.append(f'  <seriesInfo name="Pages" value="{escape(pages)}"/>')
            handled_fields.add("pages")
    elif entry.entry_type == BibTeXEntryType.BOOK:
        publisher = entry.get_field("publisher")
        edition = entry.get_field("edition")
        isbn = entry.get_field("isbn")
        if publisher:
            xml.append(f'  <seriesInfo name="Publisher" value="{escape(publisher)}"/>')
            handled_fields.add("publisher")
        if edition:
            xml.append(f'  <seriesInfo name="Edition" value="{escape(edition)}"/>')
            handled_fields.add("edition")
        if isbn:
            xml.append(f'  <seriesInfo name="ISBN" value="{escape(isbn)}"/>')
            handled_fields.add("isbn")
    elif entry.entry_type in [BibTeXEntryType.CONFERENCE, BibTeXEntryType.INPROCEEDINGS, BibTeXEntryType.PROCEEDINGS]:
        booktitle = entry.get_field("booktitle")
        publisher = entry.get_field("publisher")
        pages = entry.get_field("pages")
        if booktitle:
            xml.append(f'  <seriesInfo name="Booktitle" value="{escape(booktitle)}"/>')
            handled_fields.add("booktitle")
        if publisher:
            xml.append(f'  <seriesInfo name="Publisher" value="{escape(publisher)}"/>')
            handled_fields.add("publisher")
        if pages:
            xml.append(f'  <seriesInfo name="Pages" value="{escape(pages)}"/>')
            handled_fields.add("pages")
        # For proceedings entries, add year as seriesInfo
        if year and entry.entry_type == BibTeXEntryType.PROCEEDINGS:
            xml.append(f'  <seriesInfo name="Year" value="{escape(year)}"/>')
    elif entry.entry_type == BibTeXEntryType.TECHREPORT:
        institution = entry.get_field("institution")
        number = entry.get_field("number")
        if institution:
            xml.append(f'  <seriesInfo name="Institution" value="{escape(institution)}"/>')
            handled_fields.add("institution")
        if number:
            xml.append(f'  <seriesInfo name="Report Number" value="{escape(number)}"/>')
            handled_fields.add("number")
    elif entry.entry_type in [BibTeXEntryType.MASTERSTHESIS, BibTeXEntryType.PHDTHESIS, BibTeXEntryType.THESIS]:
        school = entry.get_field("school")
        if school:
            xml.append(f'  <seriesInfo name="School" value="{escape(school)}"/>')
            handled_fields.add("school")
    elif entry.entry_type == BibTeXEntryType.INCOLLECTION:
        booktitle = entry.get_field("booktitle")
        publisher = entry.get_field("publisher")
        if booktitle:
            xml.append(f'  <seriesInfo name="Booktitle" value="{escape(booktitle)}"/>')
            handled_fields.add("booktitle")
        if publisher:
            xml.append(f'  <seriesInfo name="Publisher" value="{escape(publisher)}"/>')
            handled_fields.add("publisher")

    # Add all other fields as <seriesInfo> (using mapped names if available)
    for field, value in entry.fields.items():
        if field not in handled_fields and value:
            name = special_field_names.get(field, field.capitalize())
            xml.append(f'  <seriesInfo name="{name}" value="{escape(value)}"/>')

    # Add URL as <format> if present
    url = entry.get_field("url")
    if url:
        xml.append(f'  <format type="TXT" target="{escape(url)}"/>')

    xml.append('</reference>')
    
    # Log the generated XML
    logger.info(f"Generated XML for entry {entry.key} ({entry.entry_type}):")
    logger.info("\n".join(xml))
    print("\n".join(xml))  # TEMP: print generated XML for debugging
    return "\n".join(xml) 