"""Tests for the RFC XML v3 models."""

import pytest
from bibtex2rfcv2.xml_models import (
    Author,
    Date,
    SeriesInfo,
    Front,
    Reference,
)


def test_author_to_xml():
    """Test author XML generation."""
    author = Author(
        fullname="John Doe",
        initials="J.",
        surname="Doe",
        organization="Test Org",
        role="editor",
        email="john@example.com",
        uri="https://example.com/john",
    )
    xml = author.to_xml()
    assert 'fullname="John Doe"' in xml
    assert 'initials="J."' in xml
    assert 'surname="Doe"' in xml
    assert 'organization="Test Org"' in xml
    assert 'role="editor"' in xml
    assert 'email="john@example.com"' in xml
    assert 'uri="https://example.com/john"' in xml


def test_date_to_xml():
    """Test date XML generation."""
    date = Date(year="2023", month="12", day="31")
    xml = date.to_xml()
    assert 'year="2023"' in xml
    assert 'month="12"' in xml
    assert 'day="31"' in xml


def test_series_info_to_xml():
    """Test series info XML generation."""
    info = SeriesInfo(
        name="Journal",
        value="Test Journal",
        ascii_name="Test Journal",
        ascii_value="Test Journal",
    )
    xml = info.to_xml()
    assert 'name="Journal"' in xml
    assert 'value="Test Journal"' in xml
    assert 'asciiName="Test Journal"' in xml
    assert 'asciiValue="Test Journal"' in xml


def test_front_to_xml():
    """Test front matter XML generation."""
    front = Front(
        title="Test Title",
        authors=[
            Author(fullname="John Doe"),
            Author(fullname="Jane Smith"),
        ],
        date=Date(year="2023"),
        abstract="This is a test abstract",
        note="This is a test note",
    )
    xml = front.to_xml()
    assert "<front>" in xml
    assert "<title>Test Title</title>" in xml
    assert '<author fullname="John Doe"/>' in xml
    assert '<author fullname="Jane Smith"/>' in xml
    assert '<date year="2023"/>' in xml
    assert "<abstract>This is a test abstract</abstract>" in xml
    assert "<note>This is a test note</note>" in xml
    assert "</front>" in xml


def test_reference_to_xml():
    """Test reference XML generation."""
    ref = Reference(
        anchor="test-ref",
        front=Front(
            title="Test Title",
            authors=[Author(fullname="John Doe")],
            date=Date(year="2023"),
        ),
        series_info=[
            SeriesInfo(name="Journal", value="Test Journal"),
        ],
        target="https://example.com/ref",
        status="informational",
        organization="Test Org",
    )
    xml = ref.to_xml()
    assert 'anchor="test-ref"' in xml
    assert 'target="https://example.com/ref"' in xml
    assert 'status="informational"' in xml
    assert 'organization="Test Org"' in xml
    assert "<front>" in xml
    assert '<seriesInfo name="Journal" value="Test Journal"/>' in xml
    assert "</reference>" in xml


def test_xml_escaping():
    """Test XML escaping in generated output."""
    ref = Reference(
        anchor="test&ref",
        front=Front(
            title="Test <Title> & More",
            authors=[Author(fullname="John & Jane")],
        ),
        series_info=[
            SeriesInfo(name="Journal & More", value="Test <Journal>"),
        ],
    )
    xml = ref.to_xml()
    assert 'anchor="test&amp;ref"' in xml
    assert "Test &lt;Title&gt; &amp; More" in xml
    assert "John &amp; Jane" in xml
    assert "Journal &amp; More" in xml
    assert "Test &lt;Journal&gt;" in xml 