"""Data models for BibTeX entries and RFC references."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set


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
        """Validate the entry's required fields.

        Raises:
            ValueError: If required fields are missing.
        """
        required = REQUIRED_FIELDS.get(self.entry_type, set())
        missing = required - set(self.fields.keys())
        if missing:
            raise ValueError(
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
        return self.fields.get(field_name, default)

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
        # Split authors by "and" and strip whitespace
        return [author.strip() for author in self.fields["author"].split(" and ")] 