"""Tests for the RFC XML v3 models."""

import pytest
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


def test_format_to_xml():
    """Test format XML generation."""
    fmt = Format(
        type="TXT",
        target="https://example.com/doc.txt",
        octets="1234",
    )
    xml = fmt.to_xml()
    assert 'type="TXT"' in xml
    assert 'target="https://example.com/doc.txt"' in xml
    assert 'octets="1234"' in xml


def test_annotation_to_xml():
    """Test annotation XML generation."""
    annotation = Annotation(
        text="This is a test annotation",
        anchor="test-anchor",
    )
    xml = annotation.to_xml()
    assert 'anchor="test-anchor"' in xml
    assert "This is a test annotation" in xml


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
        formats=[
            Format(type="TXT", target="https://example.com/doc.txt"),
        ],
        annotations=[
            Annotation(text="Test annotation"),
        ],
        target="https://example.com/ref",
        status=ReferenceStatus.INFORMATIONAL,
        organization="Test Org",
    )
    xml = ref.to_xml()
    assert 'anchor="test-ref"' in xml
    assert 'target="https://example.com/ref"' in xml
    assert 'status="informational"' in xml
    assert 'organization="Test Org"' in xml
    assert "<front>" in xml
    assert '<seriesInfo name="Journal" value="Test Journal"/>' in xml
    assert '<format type="TXT" target="https://example.com/doc.txt"/>' in xml
    assert "<annotation>Test annotation</annotation>" in xml
    assert "</reference>" in xml


def test_reference_group_to_xml():
    """Test reference group XML generation."""
    group = ReferenceGroup(
        anchor="test-group",
        title="Test Group",
        references=[
            Reference(
                anchor="ref1",
                front=Front(title="Ref 1", authors=[Author(fullname="John Doe")]),
            ),
            Reference(
                anchor="ref2",
                front=Front(title="Ref 2", authors=[Author(fullname="Jane Smith")]),
            ),
        ],
    )
    xml = group.to_xml()
    assert 'anchor="test-group"' in xml
    assert 'title="Test Group"' in xml
    assert 'anchor="ref1"' in xml
    assert 'anchor="ref2"' in xml
    assert "</referencegroup>" in xml


def test_references_to_xml():
    """Test references section XML generation."""
    refs = References(
        title="Test References",
        references=[
            Reference(
                anchor="ref1",
                front=Front(title="Ref 1", authors=[Author(fullname="John Doe")]),
            ),
        ],
        reference_groups=[
            ReferenceGroup(
                anchor="group1",
                title="Group 1",
                references=[
                    Reference(
                        anchor="ref2",
                        front=Front(title="Ref 2", authors=[Author(fullname="Jane Smith")]),
                    ),
                ],
            ),
        ],
    )
    xml = refs.to_xml()
    assert 'title="Test References"' in xml
    assert 'anchor="ref1"' in xml
    assert 'anchor="group1"' in xml
    assert 'anchor="ref2"' in xml
    assert "</references>" in xml


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