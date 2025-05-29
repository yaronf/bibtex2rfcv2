"""Tests for the BibTeX entry model."""

import pytest

from bibtex2rfcv2.models import BibTeXEntry, BibTeXEntryType, InvalidInputError


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