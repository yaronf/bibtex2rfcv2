"""Tests for the BibTeX parser."""

from pathlib import Path

import pytest

from bibtex2rfcv2.parser import parse_bibtex


def test_parse_bibtex_file(sample_bibtex_file: Path) -> None:
    """Test parsing a BibTeX file."""
    entries = parse_bibtex(sample_bibtex_file)
    assert len(entries) == 1
    entry = entries[0]
    assert entry.entry_type == "article"
    assert entry.key == "825694"
    assert "Altman" in entry.fields["author"]
    assert entry.fields["title"] == "Welcome to the opportunities of binary translation"
    assert entry.fields["year"] == "2000"
    assert entry.fields["volume"] == "33"
    assert entry.fields["number"] == "3"
    assert entry.fields["pages"] == "40-45"


def test_parse_bibtex_content(sample_bibtex_content: str) -> None:
    """Test parsing BibTeX content from a string."""
    entries = parse_bibtex(sample_bibtex_content)
    assert len(entries) == 1
    entry = entries[0]
    assert entry.entry_type == "article"
    assert entry.key == "825694"


def test_parse_empty_file(tmp_path: Path) -> None:
    """Test parsing an empty file."""
    empty_file = tmp_path / "empty.bibtex"
    empty_file.write_text("")
    entries = parse_bibtex(empty_file)
    assert len(entries) == 0


def test_parse_invalid_file(tmp_path: Path) -> None:
    """Test parsing an invalid BibTeX file."""
    invalid_file = tmp_path / "invalid.bibtex"
    invalid_file.write_text("This is not BibTeX")
    with pytest.raises(ValueError):
        parse_bibtex(invalid_file) 