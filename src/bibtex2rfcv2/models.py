"""Data models for BibTeX entries and RFC references."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set
from bibtex2rfcv2.error_handling import InvalidInputError


class BibTeXEntryType(str, Enum):
    """Standard BibTeX entry types."""

    ARTICLE = "article"
    BOOK = "book"
    INBOOK = "inbook"
    BOOKLET = "booklet"
    CONFERENCE = "conference"
    INPROCEEDINGS = "inproceedings"
    MANUAL = "manual"
    MASTERSTHESIS = "mastersthesis"
    MISC = "misc"
    PHDTHESIS = "phdthesis"
    PROCEEDINGS = "proceedings"
    TECHREPORT = "techreport"
    UNPUBLISHED = "unpublished"
    ONLINE = "online"
    PATENT = "patent"
    PERIODICAL = "periodical"
    SUPPPERIODICAL = "suppperiodical"
    INCOLLECTION = "incollection"
    INREFERENCE = "inreference"
    REPORT = "report"
    SOFTWARE = "software"
    STANDARD = "standard"
    THESIS = "thesis"


# Required fields for each entry type
REQUIRED_FIELDS: Dict[BibTeXEntryType, Set[str]] = {
    BibTeXEntryType.ARTICLE: {"author", "title", "journal", "year"},
    BibTeXEntryType.BOOK: {"author", "title", "publisher", "year"},
    BibTeXEntryType.INBOOK: {"author", "title", "chapter", "publisher", "year"},
    BibTeXEntryType.BOOKLET: {"title"},
    BibTeXEntryType.CONFERENCE: {"author", "title", "booktitle", "year"},
    BibTeXEntryType.INPROCEEDINGS: {"author", "title", "booktitle", "year"},
    BibTeXEntryType.MANUAL: {"title"},
    BibTeXEntryType.MASTERSTHESIS: {"author", "title", "school", "year"},
    BibTeXEntryType.MISC: set(),
    BibTeXEntryType.PHDTHESIS: {"author", "title", "school", "year"},
    BibTeXEntryType.PROCEEDINGS: {"title", "year"},
    BibTeXEntryType.TECHREPORT: {"author", "title", "institution", "year"},
    BibTeXEntryType.UNPUBLISHED: {"author", "title", "note"},
    BibTeXEntryType.ONLINE: {"title", "url"},
    BibTeXEntryType.PATENT: {"author", "title", "number"},
    BibTeXEntryType.PERIODICAL: {"title", "year"},
    BibTeXEntryType.SUPPPERIODICAL: {"author", "title", "journal", "year"},
    BibTeXEntryType.INCOLLECTION: {"author", "title", "booktitle", "publisher", "year"},
    BibTeXEntryType.INREFERENCE: {"author", "title", "booktitle", "year"},
    BibTeXEntryType.REPORT: {"author", "title", "institution", "year"},
    BibTeXEntryType.SOFTWARE: {"title"},
    BibTeXEntryType.STANDARD: {"title", "organization"},
    BibTeXEntryType.THESIS: {"author", "title", "school", "year"},
}


@dataclass
class BibTeXEntry:
    """A BibTeX entry with validation and field support."""

    entry_type: BibTeXEntryType
    key: str
    fields: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate the entry after initialization."""
        self.validate()

    def validate(self) -> None:
        """Validate the entry's required fields and field formats.

        Raises:
            InvalidInputError: If required fields are missing or if fields have invalid formats.
        """
        # Check for invalid fields
        valid_fields = {
            "author", "title", "journal", "year", "month", "day", "publisher", "editor",
            "volume", "number", "pages", "booktitle", "institution", "school", "abstract",
            "note", "url", "doi", "isbn", "issn", "lccn", "mrnumber", "zblnumber",
            "howpublished", "date-modified", "posted-at", "archive", "archiveprefix",
            "arxivid", "pubmedid", "pmcid", "keywords", "timestamp", "series", "edition",
            "address", "organization", "chapter", "type", "language", "location", "annote",
            "crossref", "key", "mendeley-tags", "priority", "citeulike-article-id", "citeulike-linkout-0",
            "citeulike-linkout-1", "citeulike-linkout-2", "citeulike-linkout-3", "citeulike-linkout-4",
            "citeulike-linkout-5", "citeulike-linkout-6", "citeulike-linkout-7", "citeulike-linkout-8",
            "citeulike-linkout-9", "citeulike-linkout-10", "biburl", "added-by", "interhash",
            "added-at", "intrahash"
        }
        invalid_fields = set(self.fields.keys()) - valid_fields
        if invalid_fields:
            raise InvalidInputError(f"Invalid fields: {', '.join(invalid_fields)}")

        # Validate field formats
        if "year" in self.fields:
            year = self.fields["year"]
            if not year.isdigit() or len(year) != 4:
                raise InvalidInputError(f"Invalid year format: {year}")

        # Check for missing required fields
        required = REQUIRED_FIELDS.get(self.entry_type, set())
        missing = required - set(self.fields.keys())
        if missing:
            raise InvalidInputError(
                f"Missing required fields for {self.entry_type}: {', '.join(missing)}"
            )

    def get_field(self, field_name: str, default: Optional[str] = None) -> Optional[str]:
        """Get a field value with optional default.

        Args:
            field_name: The name of the field to get.
            default: The default value to return if the field is not present.

        Returns:
            The field value or the default if not present.
        """
        value = self.fields.get(field_name, default)
        if value is not None:
            # Remove curly braces from the value
            value = value.replace("{", "").replace("}", "")
        return value

    def has_field(self, field_name: str) -> bool:
        """Check if the entry has a specific field.

        Args:
            field_name: The name of the field to check.

        Returns:
            True if the field is present, False otherwise.
        """
        return field_name in self.fields

    def get_authors(self) -> List[str]:
        """Get the list of authors.

        Returns:
            A list of author names.
        """
        if "author" not in self.fields:
            return []
        # Normalize whitespace and split authors by " and "
        author_field = self.fields["author"].replace("\n", " ")
        return [author.strip() for author in author_field.split(" and ")] 