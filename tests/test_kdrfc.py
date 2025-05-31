"""Tests for kdrfc output and CLI integration."""

from click.testing import CliRunner
import shutil
import os
from pathlib import Path
import tempfile
import subprocess
from bibtex2rfcv2.cli import main
from bibtex2rfcv2.parser import parse_bibtex
import yaml

def run_kdrfc_test(bibtex_str, expected_fields, anchor):
    runner = CliRunner()
    with runner.isolated_filesystem():
        os.makedirs('tests/data', exist_ok=True)
        bib_path = f'tests/data/{anchor}.bibtex'
        with open(bib_path, 'w') as f:
            f.write(bibtex_str)
        result = runner.invoke(main, ['to-kdrfc', bib_path, 'output.yaml'])
        assert result.exit_code == 0
        assert 'Conversion completed. 1 entries written to output.yaml.' in result.output
        with open('output.yaml') as f:
            yaml_content = f.read()
        # Parse YAML and check fields
        data = yaml.safe_load(yaml_content)
        entry = data[anchor]
        for key, value in expected_fields.items():
            assert entry.get(key) == value, f"Expected {key}: {value}, got {entry.get(key)}"
        # Print YAML for inspection
        print("Generated YAML content:")
        print(yaml_content)
        print("\nYAML content with newline markers:")
        print(yaml_content.replace('\n', '\\n'))
        # Copy preamble and postamble
        shutil.copyfile(os.path.join(os.path.dirname(__file__), 'fixtures', 'preamble.md'), 'preamble.md')
        shutil.copyfile(os.path.join(os.path.dirname(__file__), 'fixtures', 'postamble.md'), 'postamble.md')
        with open('preamble.md') as f:
            preamble_content = f.read()
        with open('postamble.md') as f:
            postamble_content = f.read()
        # Replace citation in postamble
        postamble_content = postamble_content.replace(f'{{{{test}}}}', f'{{{{{anchor}}}}}')
        # Indent YAML for informative
        yaml_lines = yaml_content.strip().split('\n')
        reference_yaml = '\n'.join('  ' + line for line in yaml_lines)
        preamble_content = preamble_content.replace('informative:', 'informative:\n' + reference_yaml)
        full_markdown = preamble_content.rstrip() + '\n\n' + postamble_content.lstrip()
        print("Full Markdown content:")
        print(full_markdown)
        print("\nFull Markdown content with newline markers:")
        print(full_markdown.replace('\n', '\\n'))
        # Run kdrfc
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as tmp:
            tmp.write(full_markdown)
            tmp_path = tmp.name
        try:
            result = subprocess.run([
                "kdrfc", tmp_path, "-v"
            ], capture_output=True, text=True)
            print("\nDebug: kdrfc output:")
            print(result.stdout)
            print("\nDebug: kdrfc error output:")
            print(result.stderr)
            xml_path = tmp_path.replace('.md', '.xml')
            with open(xml_path) as f:
                print("\nDebug: Generated XML:")
                print(f.read())
            assert result.returncode == 0, f"kdrfc validation failed: {result.stderr}"
        finally:
            os.remove(tmp_path)

def test_kdrfc_processing():
    bibtex = '@article{test, author="John Doe", title="Test Title", year="2023", journal="Test Journal"}'
    expected = {
        'title': 'Test Title',
        'journal': 'Test Journal',
        'date': {'year': 2023},
        'author': [{'ins': 'John Doe', 'name': 'John Doe'}],
    }
    run_kdrfc_test(bibtex, expected, 'test')

def test_kdrfc_book_entry():
    bibtex = '''@book{knuth1997,
        author = "Donald E. Knuth",
        title = "Art of Computer Programming, Volume 1: Fundamental Algorithms",
        publisher = "Addison-Wesley Professional",
        year = "1997",
        edition = "3",
        isbn = "0201896834"
    }'''
    expected = {
        'title': 'Art of Computer Programming, Volume 1: Fundamental Algorithms',
        'publisher': 'Addison-Wesley Professional',
        'edition': 3,
        'isbn': '0201896834',
        'date': {'year': 1997},
        'author': [{'ins': 'Donald E. Knuth', 'name': 'Donald E. Knuth'}],
    }
    run_kdrfc_test(bibtex, expected, 'knuth1997')

def test_kdrfc_conference_entry():
    bibtex = '''@conference{sigcomm2023,
        author = "Henning Schulzrinne and Vishal Misra and Eddie Kohler",
        title = "SIGCOMM 2023",
        booktitle = "Proceedings of the ACM SIGCOMM 2023 Conference",
        year = "2023",
        publisher = "ACM",
        pages = "1--10"
    }'''
    expected = {
        'title': 'SIGCOMM 2023',
        'booktitle': 'Proceedings of the ACM SIGCOMM 2023 Conference',
        'publisher': 'ACM',
        'pages': '1--10',
        'date': {'year': 2023},
        'author': [
            {'ins': 'Henning Schulzrinne', 'name': 'Henning Schulzrinne'},
            {'ins': 'Vishal Misra', 'name': 'Vishal Misra'},
            {'ins': 'Eddie Kohler', 'name': 'Eddie Kohler'}
        ],
    }
    run_kdrfc_test(bibtex, expected, 'sigcomm2023')

def test_kdrfc_thesis_entry():
    bibtex = '''@phdthesis{smith2023,
        author = "Jane Smith",
        title = "Advanced Network Protocols",
        school = "Stanford University",
        year = "2023",
        abstract = "This thesis explores...",
        url = "https://example.com/thesis"
    }'''
    expected = {
        'title': 'Advanced Network Protocols',
        'school': 'Stanford University',
        'abstract': 'This thesis explores...',
        'url': 'https://example.com/thesis',
        'date': {'year': 2023},
        'author': [{'ins': 'Jane Smith', 'name': 'Jane Smith'}],
    }
    run_kdrfc_test(bibtex, expected, 'smith2023')

def test_kdrfc_techreport_entry():
    bibtex = '''@techreport{rfc2119,
        author = "S. Bradner",
        title = "Key words for use in RFCs to Indicate Requirement Levels",
        institution = "IETF",
        year = "1997",
        number = "14",
        note = "RFC 2119"
    }'''
    expected = {
        'title': 'Key words for use in RFCs to Indicate Requirement Levels',
        'institution': 'IETF',
        'number': 14,
        'note': 'RFC 2119',
        'date': {'year': 1997},
        'author': [{'ins': 'S. Bradner', 'name': 'S. Bradner'}],
    }
    run_kdrfc_test(bibtex, expected, 'rfc2119') 