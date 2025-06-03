"""Tests for the BibTeX entry model."""

import pytest
from pathlib import Path

from bibtex2rfcv2.models import BibTeXEntry, BibTeXEntryType
from bibtex2rfcv2.error_handling import InvalidInputError
from bibtex2rfcv2.parser import parse_bibtex


def test_article_entry_validation():
    """Test validation of an article entry."""
    # Valid article entry
    entry = BibTeXEntry(
        entry_type=BibTeXEntryType.ARTICLE,
        key="test2023",
        fields={
            "author": "John Doe",
            "title": "Test Article",
            "journal": "Test Journal",
            "year": "2023",
        },
    )
    assert entry.entry_type == BibTeXEntryType.ARTICLE
    assert entry.key == "test2023"
    assert entry.get_field("author") == "John Doe"

    # Invalid article entry (missing required fields)
    with pytest.raises(InvalidInputError) as exc_info:
        BibTeXEntry(
            entry_type=BibTeXEntryType.ARTICLE,
            key="invalid2023",
            fields={"author": "John Doe"},  # Missing title, journal, year
        )
    assert "Missing required fields" in str(exc_info.value)


def test_get_authors():
    """Test author field parsing."""
    entry = BibTeXEntry(
        entry_type=BibTeXEntryType.ARTICLE,
        key="test2023",
        fields={
            "author": "John Doe and Jane Smith and Bob Johnson",
            "title": "Test Article",
            "journal": "Test Journal",
            "year": "2023",
        },
    )
    authors = entry.get_authors()
    assert len(authors) == 3
    assert authors[0] == "John Doe"
    assert authors[1] == "Jane Smith"
    assert authors[2] == "Bob Johnson"


def test_get_field():
    """Test field access methods."""
    entry = BibTeXEntry(
        entry_type=BibTeXEntryType.ARTICLE,
        key="test2023",
        fields={
            "author": "John Doe",
            "title": "Test Article",
            "journal": "Test Journal",
            "year": "2023",
            "volume": "42",
        },
    )
    assert entry.get_field("author") == "John Doe"
    assert entry.get_field("volume") == "42"
    assert entry.get_field("number") is None
    assert entry.get_field("number", "N/A") == "N/A"
    assert entry.has_field("volume")
    assert not entry.has_field("number")


def test_misc_entry_validation():
    """Test validation of a misc entry (no required fields)."""
    entry = BibTeXEntry(
        entry_type=BibTeXEntryType.MISC,
        key="test2023",
        fields={},  # No fields required
    )
    assert entry.entry_type == BibTeXEntryType.MISC
    assert entry.key == "test2023"


def test_online_entry_validation():
    """Test validation of an online entry."""
    # Valid online entry
    entry = BibTeXEntry(
        entry_type=BibTeXEntryType.ONLINE,
        key="test2023",
        fields={
            "title": "Test Website",
            "url": "https://example.com",
        },
    )
    assert entry.entry_type == BibTeXEntryType.ONLINE
    assert entry.get_field("url") == "https://example.com"

    # Invalid online entry (missing required fields)
    with pytest.raises(InvalidInputError) as exc_info:
        BibTeXEntry(
            entry_type=BibTeXEntryType.ONLINE,
            key="invalid2023",
            fields={"title": "Test Website"},  # Missing url
        )
    assert "Missing required fields" in str(exc_info.value)


def test_invalid_field():
    with pytest.raises(InvalidInputError) as exc_info:
        BibTeXEntry(
            entry_type=BibTeXEntryType.ARTICLE,
            key="invalid",
            fields={"invalid_field": "value"}
        )


def test_missing_field():
    with pytest.raises(InvalidInputError) as exc_info:
        BibTeXEntry(
            entry_type=BibTeXEntryType.ARTICLE,
            key="missing",
            fields={}
        )
    assert "Missing required fields" in str(exc_info.value)


def test_field_format():
    with pytest.raises(InvalidInputError) as exc_info:
        BibTeXEntry(
            entry_type=BibTeXEntryType.ARTICLE,
            key="format",
            fields={"year": "invalid_year"}
        )


@pytest.mark.parametrize(
    "author_field,expected_authors",
    [
        # Single author with double braces (organization)
        (
            "{{National Institute of Standards and Technology}}",
            ["National Institute of Standards and Technology"],
        ),
        # Multiple authors with "and"
        (
            "John Smith and Jane Doe",
            ["John Smith", "Jane Doe"],
        ),
        # Multiple authors with braces
        (
            "{John Smith} and {Jane Doe}",
            ["John Smith", "Jane Doe"],
        ),
        # Multiple authors with double braces
        (
            "{{John Smith}} and {{Jane Doe}}",
            ["John Smith", "Jane Doe"],
        ),
        # Single author with single braces
        (
            "{John Smith}",
            ["John Smith"],
        ),
        # Multiple authors with mixed formats
        (
            "{{National Institute of Standards and Technology}} and John Smith",
            ["National Institute of Standards and Technology", "John Smith"],
        ),
        # Multiple authors with complex names
        (
            "Jean-Pierre Dupont and María García",
            ["Jean-Pierre Dupont", "María García"],
        ),
        # Multiple authors with "and" inside braces
        (
            "{{Smith and Sons}} and Jane Doe",
            ["Smith and Sons", "Jane Doe"],
        ),
    ],
)
def test_get_authors(author_field: str, expected_authors: list[str]) -> None:
    """Test author field parsing with various formats."""
    entry = BibTeXEntry(
        entry_type=BibTeXEntryType.ARTICLE,
        key="test",
        fields={"author": author_field, "title": "Test", "journal": "Test Journal", "year": "2024"},
    )
    assert entry.get_authors() == expected_authors


def test_get_field_handling() -> None:
    """Test field value handling with braces."""
    entry = BibTeXEntry(
        entry_type=BibTeXEntryType.ARTICLE,
        key="test",
        fields={
            "author": "{{National Institute of Standards and Technology}}",
            "title": "{Test Title}",
            "journal": "Test Journal",
            "year": "2024",
        },
    )
    assert entry.get_field("author") == "National Institute of Standards and Technology"
    assert entry.get_field("title") == "Test Title"
    assert entry.get_field("journal") == "Test Journal"


def test_required_fields_validation() -> None:
    """Test validation of required fields."""
    # Test missing required fields
    with pytest.raises(InvalidInputError):
        BibTeXEntry(
            entry_type=BibTeXEntryType.ARTICLE,
            key="test",
            fields={},
        )

    # Test invalid year format
    with pytest.raises(InvalidInputError):
        BibTeXEntry(
            entry_type=BibTeXEntryType.ARTICLE,
            key="test",
            fields={
                "author": "John Smith",
                "title": "Test",
                "journal": "Test Journal",
                "year": "invalid",
            },
        )

    # Test valid entry
    entry = BibTeXEntry(
        entry_type=BibTeXEntryType.ARTICLE,
        key="test",
        fields={
            "author": "John Smith",
            "title": "Test",
            "journal": "Test Journal",
            "year": "2024",
        },
    )
    assert entry.entry_type == BibTeXEntryType.ARTICLE
    assert entry.key == "test"


def test_parse_multiline_bibtex():
    """Test that parse_bibtex correctly handles multiline fields."""
    bibtex_str = """@inproceedings{DBLP:conf/icml/HayouY23,
 author = {Soufiane Hayou and
Greg Yang},
 booktitle = {{ICML}},
 pages = {12700--12723},
 publisher = {{PMLR}},
 series = {Proceedings of Machine Learning Research},
 title = {Width and Depth Limits Commute in Residual Networks},
 volume = {202},
 year = {2023}
}"""
    entries = parse_bibtex(bibtex_str)
    assert len(entries) == 1
    entry = entries[0]
    assert entry.entry_type == "inproceedings"
    assert entry.key == "DBLP:conf/icml/HayouY23"
    assert entry.get_field("author") == "Soufiane Hayou and Greg Yang"
    assert entry.get_field("title") == "Width and Depth Limits Commute in Residual Networks"
    assert entry.get_field("year") == "2023" 