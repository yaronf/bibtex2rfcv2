"""Converter from BibTeXEntry to RFC XML reference (expanded entry type support)."""

from xml.sax.saxutils import escape
from typing import Optional

from bibtex2rfcv2.models import BibTeXEntry, BibTeXEntryType


def bibtex_entry_to_rfcxml(entry: BibTeXEntry) -> str:
    """Convert a BibTeXEntry to an RFC XML reference (expanded entry type support).

    Args:
        entry: The BibTeXEntry to convert.

    Returns:
        A string containing the RFC XML reference.

    Raises:
        ValueError: If required fields are missing.
    """
    title = entry.get_field("title")
    year = entry.get_field("year")
    authors = entry.get_authors()
    # If no authors, try editors
    if not authors:
        editors = entry.get_field("editor")
        if editors:
            # Treat newlines as whitespace and split on ' and '
            editors_clean = " ".join(editors.split())
            authors = [a.strip() for a in editors_clean.split(" and ") if a.strip()]
    
    # Generate just the reference content
    xml = [f'<reference anchor="{escape(entry.key)}">']
    xml.append(f'  <front>')
    xml.append(f'    <title>{escape(title)}</title>')
    for author in authors:
        xml.append(f'    <author fullname="{escape(author)}"/>')
    
    # Handle date fields
    date_parts = [f'year="{escape(year)}"']
    month = entry.get_field("month")
    if month:
        # Convert month names (short or full) to numbers
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
            "dec": "12", "december": "12"
        }
        month_key = month.lower().strip()
        month_num = month_map.get(month_key, month)
        date_parts.append(f'month="{escape(month_num)}"')
    day = entry.get_field("day")
    if day:
        date_parts.append(f'day="{escape(day)}"')
    xml.append(f'    <date {" ".join(date_parts)}/>')
    xml.append(f'  </front>')

    # Common fields for all types
    keywords = entry.get_field("keywords")
    if keywords:
        xml.append(f'  <seriesInfo name="Keywords" value="{escape(keywords)}"/>')
    url = entry.get_field("url")
    if url:
        xml.append(f'  <seriesInfo name="URL" value="{escape(url)}"/>')
    doi = entry.get_field("doi")
    if doi:
        xml.append(f'  <seriesInfo name="DOI" value="{escape(doi)}"/>')
    timestamp = entry.get_field("timestamp")
    if timestamp:
        xml.append(f'  <seriesInfo name="Timestamp" value="{escape(timestamp)}"/>')
    date_modified = entry.get_field("date-modified")
    if date_modified:
        xml.append(f'  <seriesInfo name="DateModified" value="{escape(date_modified)}"/>')

    # Entry-type-specific fields
    if entry.entry_type == BibTeXEntryType.ARTICLE:
        journal = entry.get_field("journal")
        if journal:
            xml.append(f'  <seriesInfo name="Journal" value="{escape(journal)}"/>')
    elif entry.entry_type == BibTeXEntryType.BOOK:
        publisher = entry.get_field("publisher")
        if publisher:
            xml.append(f'  <seriesInfo name="Publisher" value="{escape(publisher)}"/>')
        isbn = entry.get_field("isbn")
        if isbn:
            xml.append(f'  <seriesInfo name="ISBN" value="{escape(isbn)}"/>')
        edition = entry.get_field("edition")
        if edition:
            xml.append(f'  <seriesInfo name="Edition" value="{escape(edition)}"/>')
        howpublished = entry.get_field("howpublished")
        if howpublished:
            xml.append(f'  <seriesInfo name="HowPublished" value="{escape(howpublished)}"/>')
    elif entry.entry_type == BibTeXEntryType.INPROCEEDINGS:
        booktitle = entry.get_field("booktitle")
        if booktitle:
            xml.append(f'  <seriesInfo name="Booktitle" value="{escape(booktitle)}"/>')
        publisher = entry.get_field("publisher")
        if publisher:
            xml.append(f'  <seriesInfo name="Publisher" value="{escape(publisher)}"/>')
        pages = entry.get_field("pages")
        if pages:
            xml.append(f'  <seriesInfo name="Pages" value="{escape(pages)}"/>')
    elif entry.entry_type == BibTeXEntryType.TECHREPORT:
        institution = entry.get_field("institution")
        if institution:
            xml.append(f'  <seriesInfo name="Institution" value="{escape(institution)}"/>')
        number = entry.get_field("number")
        if number:
            xml.append(f'  <seriesInfo name="Report Number" value="{escape(number)}"/>')
    elif entry.entry_type == BibTeXEntryType.PROCEEDINGS:
        publisher = entry.get_field("publisher")
        if publisher:
            xml.append(f'  <seriesInfo name="Publisher" value="{escape(publisher)}"/>')
        # Editors are already handled as authors above if present

    xml.append('</reference>')
    return '\n'.join(xml) 