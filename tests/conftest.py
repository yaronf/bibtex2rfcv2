"""Pytest configuration and fixtures."""

import os
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def test_data_dir() -> Path:
    """Return the path to the test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def test_fixtures_dir() -> Path:
    """Return the path to the test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_bibtex_file(test_data_dir: Path) -> Path:
    """Return the path to a sample BibTeX file."""
    return test_data_dir / "welcome.bibtex"


@pytest.fixture
def sample_bibtex_content(sample_bibtex_file: Path) -> str:
    """Return the content of a sample BibTeX file."""
    return sample_bibtex_file.read_text()


@pytest.fixture
def xml_preamble(test_fixtures_dir: Path) -> str:
    """Return the XML preamble content."""
    return (test_fixtures_dir / "preamble.xml").read_text()


@pytest.fixture
def xml_postamble(test_fixtures_dir: Path) -> str:
    """Return the XML postamble content."""
    return (test_fixtures_dir / "postamble.xml").read_text() 