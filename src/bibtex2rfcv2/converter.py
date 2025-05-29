"""Converter from BibTeXEntry to RFC XML v3 reference."""

import logging
from typing import Optional
import re
from datetime import datetime

from bibtex2rfcv2.models import BibTeXEntry, BibTeXEntryType
from bibtex2rfcv2.xml_models import (
    Author,
    Date,
    SeriesInfo,
    Format,
    Annotation,
    Front,
    Reference,
    ReferenceGroup,
    References,
    ReferenceStatus,
)
from bibtex2rfcv2.utils import latex_to_unicode
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
    month = month.lower()
    return month_map.get(month, month)


def extract_ascii(text: str) -> Optional[str]:
    """Extract ASCII version of text by removing accents and special characters."""
    if not text:
        return None
    # Convert to Unicode first to handle LaTeX accents
    unicode_text = latex_to_unicode(text)
    # Then convert to ASCII by removing non-ASCII characters
    ascii_text = ''.join(c for c in unicode_text if ord(c) < 128)
    return ascii_text if ascii_text != unicode_text else None


def bibtex_entry_to_rfcxml(entry: BibTeXEntry) -> str:
    """Convert a BibTeXEntry to an RFC XML v3 reference.

    Args:
        entry: The BibTeXEntry to convert.

    Returns:
        A string containing the RFC XML reference.

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
        ascii_title = extract_ascii(title)
        front = Front(title=title, ascii_title=ascii_title)
        authors = entry.get_authors()
        if not authors:
            editors = entry.get_field("editor")
            if editors:
                # Split editors by ' and ' and add all as authors
                editors_clean = " ".join(editors.split())
                authors = [editor.strip() for editor in editors_clean.split(" and ") if editor.strip()]
        if not authors:
            authors = ["Unknown"]
        for author in authors:
            unicode_author = latex_to_unicode(author)
            ascii_fullname = extract_ascii(unicode_author)
            front.authors.append(Author(fullname=unicode_author, ascii_fullname=ascii_fullname))
        abstract = entry.get_field("abstract")
        if abstract:
            ascii_abstract = extract_ascii(abstract)
            front.abstract = abstract
            front.ascii_abstract = ascii_abstract
        note = entry.get_field("note")
        if note:
            ascii_note = extract_ascii(note)
            front.note = note
            front.ascii_note = ascii_note
        ref = Reference(anchor=entry.key, front=front)
        year = entry.get_field("year")
        month = entry.get_field("month")
        day = entry.get_field("day")
        if year:
            ref.series_info.append(SeriesInfo(name="Year", value=year))
        if month:
            ref.series_info.append(SeriesInfo(name="Month", value=normalize_month(month)))
        if day:
            ref.series_info.append(SeriesInfo(name="Day", value=day))
        if entry.entry_type == BibTeXEntryType.ARTICLE:
            journal = entry.get_field("journal")
            volume = entry.get_field("volume")
            number = entry.get_field("number")
            pages = entry.get_field("pages")
            if journal:
                ascii_journal = extract_ascii(journal)
                ref.series_info.append(SeriesInfo(name="Journal", value=journal, ascii_value=ascii_journal))
            if volume:
                ref.series_info.append(SeriesInfo(name="Volume", value=volume))
            if number:
                ref.series_info.append(SeriesInfo(name="Number", value=number))
            if pages:
                ref.series_info.append(SeriesInfo(name="Pages", value=pages))
        elif entry.entry_type == BibTeXEntryType.BOOK:
            publisher = entry.get_field("publisher")
            edition = entry.get_field("edition")
            isbn = entry.get_field("isbn")
            if publisher:
                ascii_publisher = extract_ascii(publisher)
                ref.series_info.append(SeriesInfo(name="Publisher", value=publisher, ascii_value=ascii_publisher))
            if edition:
                ref.series_info.append(SeriesInfo(name="Edition", value=edition))
            if isbn:
                ref.series_info.append(SeriesInfo(name="ISBN", value=isbn))
        elif entry.entry_type in [BibTeXEntryType.CONFERENCE, BibTeXEntryType.INPROCEEDINGS, BibTeXEntryType.PROCEEDINGS]:
            booktitle = entry.get_field("booktitle")
            publisher = entry.get_field("publisher")
            pages = entry.get_field("pages")
            if booktitle:
                ascii_booktitle = extract_ascii(booktitle)
                ref.series_info.append(SeriesInfo(name="Booktitle", value=booktitle, ascii_value=ascii_booktitle))
            if publisher:
                ascii_publisher = extract_ascii(publisher)
                ref.series_info.append(SeriesInfo(name="Publisher", value=publisher, ascii_value=ascii_publisher))
            if pages:
                ref.series_info.append(SeriesInfo(name="Pages", value=pages))
        elif entry.entry_type == BibTeXEntryType.TECHREPORT:
            institution = entry.get_field("institution")
            number = entry.get_field("number")
            if institution:
                ascii_institution = extract_ascii(institution)
                ref.series_info.append(SeriesInfo(name="Institution", value=institution, ascii_value=ascii_institution))
            if number:
                ref.series_info.append(SeriesInfo(name="Report Number", value=number))
        elif entry.entry_type in [BibTeXEntryType.MASTERSTHESIS, BibTeXEntryType.PHDTHESIS, BibTeXEntryType.THESIS]:
            school = entry.get_field("school")
            if school:
                ascii_school = extract_ascii(school)
                ref.series_info.append(SeriesInfo(name="School", value=school, ascii_value=ascii_school))
        elif entry.entry_type == BibTeXEntryType.INCOLLECTION:
            booktitle = entry.get_field("booktitle")
            publisher = entry.get_field("publisher")
            if booktitle:
                ascii_booktitle = extract_ascii(booktitle)
                ref.series_info.append(SeriesInfo(name="Booktitle", value=booktitle, ascii_value=ascii_booktitle))
            if publisher:
                ascii_publisher = extract_ascii(publisher)
                ref.series_info.append(SeriesInfo(name="Publisher", value=publisher, ascii_value=ascii_publisher))
        handled_fields = {
            "title", "author", "editor", "year", "month", "day", "key",
            "journal", "volume", "number", "pages", "publisher", "edition", "isbn",
            "booktitle", "institution", "school", "abstract", "note", "timezone",
        }
        field_case_map = {
            "url": "URL",
            "doi": "DOI",
            "howpublished": "HowPublished",
            "date-modified": "DateModified",
            "posted-at": "PostedAt",
            "archive": "Archive",
            "archiveprefix": "ArchivePrefix",
            "arxivid": "arXivID",
            "pubmedid": "PubMedID",
            "pmcid": "PMCID",
            "isbn": "ISBN",
            "issn": "ISSN",
            "lccn": "LCCN",
            "mrnumber": "MRNumber",
            "zblnumber": "ZBLNumber",
        }
        for field, value in entry.fields.items():
            if field not in handled_fields and value:
                field_name = field_case_map.get(field.lower())
                if not field_name:
                    field_name = field.replace("-", " ").title().replace(" ", "")
                ascii_value = extract_ascii(value)
                ref.series_info.append(SeriesInfo(name=field_name, value=value, ascii_value=ascii_value))
        url = entry.get_field("url")
        if url:
            ascii_url = extract_ascii(url)
            ref.formats.append(Format(type="TXT", target=url, ascii_target=ascii_url))
        doi = entry.get_field("doi")
        if doi:
            doi_url = f"https://doi.org/{doi}"
            ref.formats.append(Format(type="DOI", target=doi_url))
        logger.info(f"Generated XML for entry {entry.key} ({entry.entry_type}):")
        xml = ref.to_xml()
        logger.info(xml)
        return xml
        # --- End conversion logic ---
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        raise ConversionError(f"Conversion failed: {e}") from e 