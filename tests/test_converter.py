"""Tests for the BibTeX to RFC XML converter."""

import pytest
from bibtex2rfcv2.models import BibTeXEntry, BibTeXEntryType
from bibtex2rfcv2.converter import bibtex_entry_to_rfcxml

def test_article_to_rfcxml():
    entry = BibTeXEntry(
        entry_type=BibTeXEntryType.ARTICLE,
        key="smith2023",
        fields={
            "author": "Alice Smith and Bob Jones",
            "title": "A Study on BibTeX Conversion",
            "journal": "Journal of Testing",
            "year": "2023",
        },
    )
    xml = bibtex_entry_to_rfcxml(entry)
    assert '<reference anchor="smith2023">' in xml
    assert '<title>A Study on BibTeX Conversion</title>' in xml
    assert '<author fullname="Alice Smith"/>' in xml
    assert '<author fullname="Bob Jones"/>' in xml
    assert '<date year="2023"/>' in xml
    assert '<seriesInfo name="Journal" value="Journal of Testing"/>' in xml
    assert xml.strip().endswith('</reference>')

def test_missing_required_fields():
    with pytest.raises(ValueError) as exc_info:
        BibTeXEntry(
            entry_type=BibTeXEntryType.ARTICLE,
            key="missingfields",
            fields={
                "author": "Alice Smith",
                # Missing title and year
            },
        )
    assert "Missing required fields" in str(exc_info.value)

def test_book_to_rfcxml():
    entry = BibTeXEntry(
        entry_type=BibTeXEntryType.BOOK,
        key="doe2022",
        fields={
            "author": "Jane Doe",
            "title": "The Book of Testing",
            "publisher": "Test Press",
            "year": "2022",
            "isbn": "123-4567890123",
        },
    )
    xml = bibtex_entry_to_rfcxml(entry)
    assert '<reference anchor="doe2022">' in xml
    assert '<seriesInfo name="Publisher" value="Test Press"/>' in xml
    assert '<seriesInfo name="ISBN" value="123-4567890123"/>' in xml
    assert xml.strip().endswith('</reference>')

def test_book_with_additional_fields():
    entry = BibTeXEntry(
        entry_type=BibTeXEntryType.BOOK,
        key="knuth1997",
        fields={
            "author": "Donald E. Knuth",
            "title": "Art of Computer Programming, Volume 1: Fundamental Algorithms",
            "publisher": "Addison-Wesley Professional",
            "year": "1997",
            "edition": "3",
            "isbn": "0201896834",
            "abstract": "This magnificent tour de force presents a comprehensive overview...",
            "keywords": "programming",
            "url": "http://www.amazon.com/exec/obidos/redirect?tag=citeulike07-20&path=ASIN/0201896834",
            "month": "jul",
            "day": "17",
            "howpublished": "Hardcover"
        },
    )
    xml = bibtex_entry_to_rfcxml(entry)
    assert '<reference anchor="knuth1997">' in xml
    assert '<seriesInfo name="Edition" value="3"/>' in xml
    assert '<seriesInfo name="ISBN" value="0201896834"/>' in xml
    assert '<seriesInfo name="Keywords" value="programming"/>' in xml
    assert '<seriesInfo name="URL" value="http://www.amazon.com/exec/obidos/redirect?tag=citeulike07-20&amp;path=ASIN/0201896834"/>' in xml
    assert '<date year="1997" month="7" day="17"/>' in xml
    assert '<seriesInfo name="HowPublished" value="Hardcover"/>' in xml
    assert xml.strip().endswith('</reference>')

def test_article_with_additional_fields():
    entry = BibTeXEntry(
        entry_type=BibTeXEntryType.ARTICLE,
        key="fips197",
        fields={
            "author": "National Institute of Standards and Technology",
            "title": "Advanced Encryption Standard",
            "journal": "NIST FIPS PUB 197",
            "year": "2001",
            "keywords": "imported",
            "timestamp": "2011-02-14T16:52:54.000+0100",
            "date-modified": "2006-08-22 11:34:23 +0200"
        },
    )
    xml = bibtex_entry_to_rfcxml(entry)
    assert '<reference anchor="fips197">' in xml
    assert '<seriesInfo name="Journal" value="NIST FIPS PUB 197"/>' in xml
    assert '<seriesInfo name="Keywords" value="imported"/>' in xml
    assert '<seriesInfo name="Timestamp" value="2011-02-14T16:52:54.000+0100"/>' in xml
    assert '<seriesInfo name="DateModified" value="2006-08-22 11:34:23 +0200"/>' in xml
    assert xml.strip().endswith('</reference>')

def test_inproceedings_to_rfcxml():
    entry = BibTeXEntry(
        entry_type=BibTeXEntryType.INPROCEEDINGS,
        key="smith2021",
        fields={
            "author": "Sam Smith",
            "title": "Conference Paper",
            "booktitle": "Proc. of Testing",
            "publisher": "Conf Press",
            "year": "2021",
        },
    )
    xml = bibtex_entry_to_rfcxml(entry)
    assert '<seriesInfo name="Booktitle" value="Proc. of Testing"/>' in xml
    assert '<seriesInfo name="Publisher" value="Conf Press"/>' in xml
    assert xml.strip().endswith('</reference>')

def test_inproceedings_with_additional_fields():
    entry = BibTeXEntry(
        entry_type=BibTeXEntryType.INPROCEEDINGS,
        key="sigcomm2023",
        fields={
            "author": "Rahul Bothra and Rohan Gandhi and Ranjita Bhagwan and Venkata N. Padmanabhan and Rui Liang and Steve Carlson and Vinayaka Kamath and Sreangsu Acharyya and Ken Sueda and Somesh Chaturmohta and Harsha Sharma",
            "title": "Switchboard: Efficient Resource Management for Conferencing Services",
            "booktitle": "SIGCOMM",
            "pages": "1000--1011",
            "publisher": "ACM",
            "year": "2023",
            "doi": "10.1145/3544216.3544222",
            "url": "https://doi.org/10.1145/3544216.3544222"
        },
    )
    xml = bibtex_entry_to_rfcxml(entry)
    assert '<reference anchor="sigcomm2023">' in xml
    assert '<seriesInfo name="Pages" value="1000--1011"/>' in xml
    assert '<seriesInfo name="DOI" value="10.1145/3544216.3544222"/>' in xml
    assert '<seriesInfo name="URL" value="https://doi.org/10.1145/3544216.3544222"/>' in xml
    assert xml.strip().endswith('</reference>')

def test_techreport_to_rfcxml():
    entry = BibTeXEntry(
        entry_type=BibTeXEntryType.TECHREPORT,
        key="lee2020",
        fields={
            "author": "Chris Lee",
            "title": "A Technical Report",
            "institution": "Test University",
            "number": "TR-2020-01",
            "year": "2020",
        },
    )
    xml = bibtex_entry_to_rfcxml(entry)
    assert '<seriesInfo name="Institution" value="Test University"/>' in xml
    assert '<seriesInfo name="Report Number" value="TR-2020-01"/>' in xml
    assert xml.strip().endswith('</reference>')

def test_icml2023_bibtex_to_rfcxml():
    from pathlib import Path
    from bibtex2rfcv2.parser import parse_bibtex
    from bibtex2rfcv2.converter import bibtex_entry_to_rfcxml

    bibtex_file = Path("tests/data/icml2023.bibtex")
    entries = parse_bibtex(bibtex_file)
    assert len(entries) > 0, "No entries parsed from ICML 2023 BibTeX file"

    for entry in entries:
        xml = bibtex_entry_to_rfcxml(entry)
        assert '<reference anchor="' in xml
        assert '<title>' in xml
        assert '<date year="' in xml
        assert xml.strip().endswith('</reference>')

def test_real_bibtex_files():
    """Test conversion of real BibTeX files from our data directory."""
    from pathlib import Path
    from bibtex2rfcv2.parser import parse_bibtex
    from bibtex2rfcv2.converter import bibtex_entry_to_rfcxml

    # Test Knuth's book entry
    knuth_entries = parse_bibtex(Path("tests/data/knuth.bibtex"))
    assert len(knuth_entries) > 0
    knuth_xml = bibtex_entry_to_rfcxml(knuth_entries[0])
    assert '<reference anchor="citeulike:175024">' in knuth_xml
    assert '<seriesInfo name="Edition" value="3"/>' in knuth_xml
    assert '<seriesInfo name="ISBN" value="0201896834"/>' in knuth_xml
    assert '<seriesInfo name="Keywords" value="programming"/>' in knuth_xml
    assert '<date year="1997" month="7" day="17"/>' in knuth_xml
    assert '<seriesInfo name="HowPublished" value="Hardcover"/>' in knuth_xml

    # Test FIPS article entry
    fips_entries = parse_bibtex(Path("tests/data/fips197.bibtex"))
    assert len(fips_entries) > 0
    fips_xml = bibtex_entry_to_rfcxml(fips_entries[0])
    assert '<reference anchor="Standards2001">' in fips_xml
    assert '<seriesInfo name="Journal" value="NIST FIPS PUB 197"/>' in fips_xml
    assert '<seriesInfo name="Keywords" value="imported"/>' in fips_xml
    assert '<seriesInfo name="Timestamp" value="2011-02-14T16:52:54.000+0100"/>' in fips_xml

    # Test SIGCOMM proceedings entry
    sigcomm_entries = parse_bibtex(Path("tests/data/sigcomm2023.bibtex"))
    assert len(sigcomm_entries) > 0
    sigcomm_xml = bibtex_entry_to_rfcxml(sigcomm_entries[0])
    assert '<reference anchor="DBLP:conf/sigcomm/2023">' in sigcomm_xml
    assert '<author fullname="Henning Schulzrinne"/>' in sigcomm_xml
    assert '<author fullname="Vishal Misra"/>' in sigcomm_xml
    assert '<author fullname="Eddie Kohler"/>' in sigcomm_xml
    assert '<author fullname="David A. Maltz"/>' in sigcomm_xml
    assert '<seriesInfo name="Publisher" value="ACM"/>' in sigcomm_xml 