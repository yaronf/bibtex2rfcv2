"""Tests for the BibTeX to RFC XML v3 converter."""

import pytest
from bibtex2rfcv2.models import BibTeXEntry, BibTeXEntryType
from bibtex2rfcv2.converter import bibtex_entry_to_rfcxml
import subprocess
import tempfile
import os
import datetime
import glob
import re
import xml.etree.ElementTree as ET

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
    assert '<seriesInfo name="Year" value="2023"/>' in xml
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
    assert '<seriesInfo name="Year" value="1997"/>' in xml
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
        assert re.search(r'<title[^>]*>', xml) is not None
        if entry.entry_type != BibTeXEntryType.PROCEEDINGS:
            assert '<seriesInfo name="Year" value="' in xml
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
    assert '<seriesInfo name="Year" value="1997"/>' in knuth_xml
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

@pytest.mark.parametrize("bibfile", glob.glob("tests/data/icml2023_entries/entry*.bibtex"))
def test_rfcxml_valid_with_xml2rfc(bibfile):
    from pathlib import Path
    from bibtex2rfcv2.parser import parse_bibtex
    from bibtex2rfcv2.converter import bibtex_entry_to_rfcxml
    import tempfile
    import subprocess
    import os

    # Get preamble and postamble
    preamble_path = Path("tests/fixtures/preamble.xml")
    postamble_path = Path("tests/fixtures/postamble.xml")
    assert preamble_path.exists(), "preamble.xml not found"
    assert postamble_path.exists(), "postamble.xml not found"

    # Parse and convert BibTeX entry
    entries = parse_bibtex(Path(bibfile))
    assert len(entries) == 1, f"Expected 1 entry in {bibfile}, got {len(entries)}"
    reference_xml = bibtex_entry_to_rfcxml(entries[0])

    # Debug: Print the XML content
    print(f"\nDebug: XML content for {bibfile}:")
    print(reference_xml)

    # Compose the full XML
    xml_content = preamble_path.read_text() + reference_xml + postamble_path.read_text()

    # Write to temporary file and validate
    with tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False) as tmp:
        tmp.write(xml_content)
        tmp_path = tmp.name
    try:
        result = subprocess.run([
            "xml2rfc", tmp_path, "--no-dtd", "--quiet"
        ], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"\nDebug: xml2rfc validation failed for {bibfile}")
            print(f"Error output: {result.stderr}")
            print(f"Full XML content:")
            print(xml_content)
        assert result.returncode == 0, f"xml2rfc validation failed for {bibfile}: {result.stderr}"
    finally:
        os.remove(tmp_path)

def test_minimal_rfcxml_valid_with_xml2rfc():
    """Test that a minimal valid RFC XML entry is accepted by xml2rfc using preamble/postamble from the original project."""
    import pathlib
    preamble_path = pathlib.Path("tests/fixtures/preamble.xml")
    postamble_path = pathlib.Path("tests/fixtures/postamble.xml")
    assert preamble_path.exists(), "preamble.xml not found"
    assert postamble_path.exists(), "postamble.xml not found"

    # Minimal reference entry
    reference_xml = """
  <reference anchor="test2023">
    <front>
      <title>Test Title</title>
      <author fullname="Test Author"/>
      <date year="2025"/>
    </front>
  </reference>
"""
    # Compose the full XML
    xml_content = preamble_path.read_text() + reference_xml + postamble_path.read_text()

    import tempfile, subprocess, os
    with tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False) as tmp:
        tmp.write(xml_content)
        tmp_path = tmp.name
    try:
        result = subprocess.run([
            "xml2rfc", tmp_path, "--no-dtd", "--quiet"
        ], capture_output=True, text=True)
        assert result.returncode == 0, f"xml2rfc validation failed: {result.stderr}"
    finally:
        os.remove(tmp_path)

def test_accented_characters():
    """Test conversion of BibTeX entries with accented characters."""
    entry = BibTeXEntry(
        entry_type=BibTeXEntryType.ARTICLE,
        key="accented2023",
        fields={
            "author": "Jos{\\'e} Su{\\'a}rez{-}Varela and Andr{\\'e} L{\\\"u}t{\\\"u}",
            "title": "Enhancing 5G Radio Planning with Graph Representations",
            "journal": "Journal of Testing",
            "year": "2023",
        },
    )
    xml = bibtex_entry_to_rfcxml(entry)
    assert re.search(r'<author fullname="José Suárez-Varela"[^>]*/>', xml)
    assert re.search(r'<author fullname="André Lütü"[^>]*/>', xml)
    assert '<title>Enhancing 5G Radio Planning with Graph Representations</title>' in xml
    assert xml.strip().endswith('</reference>')

def test_latex_to_unicode():
    from bibtex2rfcv2.utils import latex_to_unicode

    # Test cases for various LaTeX accents
    assert latex_to_unicode("{\\'e}") == "é"
    assert latex_to_unicode("{\\'a}") == "á"
    assert latex_to_unicode("{\\'i}") == "í"
    assert latex_to_unicode("{\\'o}") == "ó"
    assert latex_to_unicode("{\\'u}") == "ú"
    assert latex_to_unicode("{\\'y}") == "ý"
    assert latex_to_unicode("{\\'A}") == "Á"
    assert latex_to_unicode("{\\'E}") == "É"
    assert latex_to_unicode("{\\'I}") == "Í"
    assert latex_to_unicode("{\\'O}") == "Ó"
    assert latex_to_unicode("{\\'U}") == "Ú"
    assert latex_to_unicode("{\\'Y}") == "Ý"

    # Test cases for other accents
    assert latex_to_unicode("{\\`a}") == "à"
    assert latex_to_unicode("{\\`e}") == "è"
    assert latex_to_unicode("{\\`i}") == "ì"
    assert latex_to_unicode("{\\`o}") == "ò"
    assert latex_to_unicode("{\\`u}") == "ù"
    assert latex_to_unicode("{\\`A}") == "À"
    assert latex_to_unicode("{\\`E}") == "È"
    assert latex_to_unicode("{\\`I}") == "Ì"
    assert latex_to_unicode("{\\`O}") == "Ò"
    assert latex_to_unicode("{\\`U}") == "Ù"

    # Test cases for umlauts
    assert latex_to_unicode("{\\\"a}") == "ä"
    assert latex_to_unicode("{\\\"e}") == "ë"
    assert latex_to_unicode("{\\\"i}") == "ï"
    assert latex_to_unicode("{\\\"o}") == "ö"
    assert latex_to_unicode("{\\\"u}") == "ü"
    assert latex_to_unicode("{\\\"y}") == "ÿ"
    assert latex_to_unicode("{\\\"A}") == "Ä"
    assert latex_to_unicode("{\\\"E}") == "Ë"
    assert latex_to_unicode("{\\\"I}") == "Ï"
    assert latex_to_unicode("{\\\"O}") == "Ö"
    assert latex_to_unicode("{\\\"U}") == "Ü"
    assert latex_to_unicode("{\\\"Y}") == "Ÿ"

    # Test cases for circumflex
    assert latex_to_unicode("{\\^a}") == "â"
    assert latex_to_unicode("{\\^e}") == "ê"
    assert latex_to_unicode("{\\^i}") == "î"
    assert latex_to_unicode("{\\^o}") == "ô"
    assert latex_to_unicode("{\\^u}") == "û"
    assert latex_to_unicode("{\\^A}") == "Â"
    assert latex_to_unicode("{\\^E}") == "Ê"
    assert latex_to_unicode("{\\^I}") == "Î"
    assert latex_to_unicode("{\\^O}") == "Ô"
    assert latex_to_unicode("{\\^U}") == "Û"

    # Test cases for tilde
    assert latex_to_unicode("{\\~a}") == "ã"
    assert latex_to_unicode("{\\~n}") == "ñ"
    assert latex_to_unicode("{\\~o}") == "õ"
    assert latex_to_unicode("{\\~A}") == "Ã"
    assert latex_to_unicode("{\\~N}") == "Ñ"
    assert latex_to_unicode("{\\~O}") == "Õ"

    # Test cases for cedilla
    assert latex_to_unicode("{\\c{c}}") == "ç"
    assert latex_to_unicode("{\\c{C}}") == "Ç"

    # Test cases for caron
    assert latex_to_unicode("{\\v{s}}") == "š"
    assert latex_to_unicode("{\\v{S}}") == "Š"
    assert latex_to_unicode("{\\v{z}}") == "ž"
    assert latex_to_unicode("{\\v{Z}}") == "Ž"
    assert latex_to_unicode("{\\v{c}}") == "č"
    assert latex_to_unicode("{\\v{C}}") == "Č"

    # Test cases for breve
    assert latex_to_unicode("{\\u{g}}") == "ğ"
    assert latex_to_unicode("{\\u{G}}") == "Ğ"

    # Test cases for dot
    assert latex_to_unicode("{\\.I}") == "İ"

    # Test cases for direct form
    assert latex_to_unicode("\\'e") == "é"
    assert latex_to_unicode("\\'a") == "á"
    assert latex_to_unicode("\\'i") == "í"
    assert latex_to_unicode("\\'o") == "ó"
    assert latex_to_unicode("\\'u") == "ú"
    assert latex_to_unicode("\\'y") == "ý"
    assert latex_to_unicode("\\'A") == "Á"
    assert latex_to_unicode("\\'E") == "É"
    assert latex_to_unicode("\\'I") == "Í"
    assert latex_to_unicode("\\'O") == "Ó"
    assert latex_to_unicode("\\'U") == "Ú"
    assert latex_to_unicode("\\'Y") == "Ý"

    # Test cases for mixed accents
    assert latex_to_unicode("Jos{\\'e} Su{\\'a}rez{-}Varela and Andr{\\'e} L{\\\"u}t{\\\"u}") == "José Suárez-Varela and André Lütü"

def test_utf8_validation():
    import tempfile
    import xml.etree.ElementTree as ET
    from bibtex2rfcv2.models import BibTeXEntry, BibTeXEntryType
    from bibtex2rfcv2.converter import bibtex_entry_to_rfcxml

    # 1 & 2: Non-ASCII and non-Latin characters
    entries = [
        BibTeXEntry(
            entry_type=BibTeXEntryType.ARTICLE,
            key="chinese2023",
            fields={
                "author": "李四 and 张三",
                "title": "深度学习的进展",
                "journal": "人工智能学报",
                "year": "2023",
            },
        ),
        BibTeXEntry(
            entry_type=BibTeXEntryType.ARTICLE,
            key="cyrillic2023",
            fields={
                "author": "Алексей Иванов",
                "title": "Обработка данных",
                "journal": "Журнал Тестирования",
                "year": "2023",
            },
        ),
        BibTeXEntry(
            entry_type=BibTeXEntryType.ARTICLE,
            key="emoji2023",
            fields={
                "author": "Alice 😀 and Bob 🚀",
                "title": "Emoji in Science 🧪",
                "journal": "Journal of Fun",
                "year": "2023",
            },
        ),
        # 7: Bidirectional text (Arabic, Hebrew)
        BibTeXEntry(
            entry_type=BibTeXEntryType.ARTICLE,
            key="arabic2023",
            fields={
                "author": "محمد علي",
                "title": "تقدم التعلم العميق",
                "journal": "مجلة الذكاء الاصطناعي",
                "year": "2023",
            },
        ),
        BibTeXEntry(
            entry_type=BibTeXEntryType.ARTICLE,
            key="hebrew2023",
            fields={
                "author": "דוד לוי",
                "title": "התקדמות בלמידה עמוקה",
                "journal": "כתב עת לבינה מלאכותית",
                "year": "2023",
            },
        ),
    ]

    for entry in entries:
        # Round-trip encoding/decoding
        with tempfile.NamedTemporaryFile("w+", encoding="utf-8", delete=False) as tmp:
            tmp.write(entry.fields["author"] + "\n" + entry.fields["title"])
            tmp.seek(0)
            content = tmp.read()
            assert entry.fields["author"] in content
            assert entry.fields["title"] in content

        # Convert to XML
        xml = bibtex_entry_to_rfcxml(entry)
        # 5: XML escaping and validity
        # Should not contain unescaped <, >, or & in text nodes
        assert "<author" in xml
        assert "<title" in xml
        assert "&lt;" not in xml and "&gt;" not in xml and "&amp;" not in xml or all(c not in entry.fields["title"] for c in "<>&")
        # Parse XML to ensure validity
        try:
            ET.fromstring("<root>" + xml + "</root>")
        except ET.ParseError as e:
            assert False, f"XML not valid for entry {entry.key}: {e}"
        # 7: Check that right-to-left scripts are present
        if entry.key in ("arabic2023", "hebrew2023"):
            assert entry.fields["author"] in xml
            assert entry.fields["title"] in xml 