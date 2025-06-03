"""Data models for BibTeX entries and RFC references."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Any, Union
from bibtex2rfcv2.error_handling import InvalidInputError
from bibtex2rfcv2.utils import latex_to_unicode
import re


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
                f"Missing required fields for {self.entry_type.value}: {', '.join(missing)}"
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
            if isinstance(value, list):
                # For lists (like authors), return the list as is
                return value
            # Remove single curly braces but preserve double braces
            value = value.replace("{{", "").replace("}}", "")
            value = value.replace("{", "").replace("}", "")
            # Normalize multiline fields by replacing newlines with spaces
            value = value.replace("\n", " ")
        return value

    def has_field(self, field_name: str) -> bool:
        """Check if the entry has a specific field.

        Args:
            field_name: The name of the field to check.

        Returns:
            True if the field is present, False otherwise.
        """
        return field_name in self.fields

    def _process_names(self, field_value: Union[str, List[str]]) -> List[str]:
        """Helper method to process author/editor names.
        
        Args:
            field_value: String or list of strings containing author/editor names
            
        Returns:
            List of author/editor names in "First Last" format
        """
        if not field_value:
            return []
            
        # Handle both list and string inputs
        if isinstance(field_value, list):
            names = field_value
        else:
            # Split on ' and ' but not within braces
            names = []
            current = ""
            brace_level = 0
            for char in field_value:
                if char == '{':
                    brace_level += 1
                elif char == '}':
                    brace_level -= 1
                elif char == 'a' and brace_level == 0 and current.endswith(' '):
                    # Check for ' and ' pattern
                    if current.endswith(' and '):
                        names.append(current[:-5].strip())
                        current = ""
                        continue
                current += char
            if current:
                names.append(current.strip())
        
        # Process each name
        processed_names = []
        for name in names:
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
                processed_names.append(name)
                
        return processed_names

    def get_authors(self) -> List[str]:
        """Get list of authors from the author field."""
        author_field = self.fields.get('author')
        if author_field is None:
            return []
        return self._process_names(author_field)

    def get_editors(self) -> List[str]:
        """Get list of editors from the editor field."""
        editor_field = self.fields.get('editor')
        if editor_field is None:
            return []
        return self._process_names(editor_field) 