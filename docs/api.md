# API Reference

## Core Modules

### bibtex2rfcv2.parser

#### `parse_bibtex(source: Union[str, Path, TextIO]) -> List[Dict[str, str]]`
Parse a BibTeX source into a list of entry dictionaries.

**Parameters:**
- `source`: BibTeX source as a string, file path, or file-like object

**Returns:**
- List of dictionaries, each representing a BibTeX entry

**Example:**
```python
from bibtex2rfcv2.parser import parse_bibtex
from pathlib import Path

# Parse from file
entries = parse_bibtex(Path('input.bib'))

# Parse from string
bibtex_str = '@article{test, title="Test"}'
entries = parse_bibtex(bibtex_str)
```

### bibtex2rfcv2.converter

#### `bibtex_entry_to_rfcxml(entry: Dict[str, str]) -> str`
Convert a BibTeX entry dictionary to RFC XML format.

**Parameters:**
- `entry`: Dictionary containing BibTeX entry fields

**Returns:**
- String containing RFC-compliant XML

**Example:**
```python
from bibtex2rfcv2.converter import bibtex_entry_to_rfcxml

entry = {
    'type': 'article',
    'key': 'test2023',
    'author': 'John Doe',
    'title': 'Test Title',
    'year': '2023'
}
xml = bibtex_entry_to_rfcxml(entry)
```

### bibtex2rfcv2.cli

#### `main() -> None`
Main entry point for the command-line interface.

**Example:**
```python
from bibtex2rfcv2.cli import main

if __name__ == '__main__':
    main()
```

## Data Structures

### BibTeX Entry
A BibTeX entry is represented as a dictionary with the following structure:
```python
{
    'type': str,        # Entry type (article, book, etc.)
    'key': str,         # Citation key
    'author': str,      # Author(s)
    'title': str,       # Title
    'year': str,        # Publication year
    'journal': str,     # Journal name (for articles)
    'booktitle': str,   # Book title (for inproceedings)
    'publisher': str,   # Publisher
    'volume': str,      # Volume number
    'number': str,      # Issue number
    'pages': str,       # Page range
    'doi': str,         # Digital Object Identifier
    # ... additional fields
}
```

### RFC XML Structure
The generated XML follows the xml2rfc v3 format:
```xml
<reference anchor="key">
  <front>
    <title>Title</title>
    <author fullname="Author Name"/>
    <date year="2023"/>
  </front>
  <seriesInfo name="Journal" value="Volume"/>
  <format type="application/pdf" target="https://doi.org/..."/>
</reference>
```

## Error Handling

### bibtex2rfcv2.errors

#### `BibTeXError`
Base class for all BibTeX-related errors.

#### `MissingRequiredFieldError`
Raised when a required field is missing from a BibTeX entry.

#### `InvalidFieldError`
Raised when a field contains invalid data.

#### `XMLGenerationError`
Raised when there's an error generating the XML output.

## Constants

### bibtex2rfcv2.constants

#### `REQUIRED_FIELDS`
Dictionary mapping entry types to their required fields:
```python
{
    'article': ['author', 'title', 'journal', 'year'],
    'book': ['author', 'title', 'publisher', 'year'],
    # ... other entry types
}
```

#### `FIELD_ALIASES`
Dictionary mapping alternative field names to standard names:
```python
{
    'authors': 'author',
    'editors': 'editor',
    # ... other aliases
}
``` 