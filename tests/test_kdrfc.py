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
import pytest
from bibtex2rfcv2.error_handling import InvalidInputError

def run_kdrfc_test(bibtex_str, expected_fields, anchor):
    runner = CliRunner()
    with runner.isolated_filesystem():
        bib_path = f'tests/data/{anchor}.bibtex'
        os.makedirs(os.path.dirname(bib_path), exist_ok=True)
        with open(bib_path, 'w') as f:
            f.write(bibtex_str)
        print(f"bibtex_str: {bibtex_str}")
        print(f"expected_fields: {expected_fields}")
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

# Discover all .bibtex files recursively under tests/data/
bibtex_files = [str(p.relative_to("tests/data")) for p in Path("tests/data").rglob("*.bibtex") if p.name != "invalid_encoding.bibtex"]

@pytest.mark.parametrize("bibfile", bibtex_files)
def test_kdrfc_all_bibtex_files(bibfile):
    """Test kdrfc conversion for all BibTeX files in the test data directory (recursively)."""
    from pathlib import Path
    from bibtex2rfcv2.parser import parse_bibtex
    from bibtex2rfcv2.error_handling import InvalidInputError

    # Parse BibTeX file
    bib_path = Path("tests/data") / bibfile
    try:
        entries = parse_bibtex(bib_path)
    except InvalidInputError as e:
        if "No valid BibTeX entries found" in str(e):
            pytest.skip(f"Skipping file with no valid entries: {bibfile}")
        else:
            raise
    except FileNotFoundError as e:
        if str(bibfile) == "invalid_encoding.bibtex":
            pytest.skip(f"Skipping file with invalid encoding: {bibfile}")
        else:
            raise

    assert len(entries) > 0, f"No entries found in {bibfile}"

    # Test each entry
    for entry in entries:
        # Skip entries missing required fields
        if not (entry.fields.get('author') or entry.fields.get('editor')) or not entry.fields.get('title'):
            pytest.skip(f"Skipping entry {entry.key} missing required fields: author/editor or title")
        # Convert entry back to BibTeX string format
        bibtex_str = f"@{entry.entry_type.value}{{{entry.key},\n"
        for field, value in entry.fields.items():
            # Handle different value types
            if isinstance(value, list):
                # If list contains dictionaries with 'name' field, extract names
                if value and isinstance(value[0], dict) and 'name' in value[0]:
                    value = ' and '.join(v['name'] for v in value)
                else:
                    value = ' and '.join(str(v) for v in value)
            elif isinstance(value, dict):
                # If dictionary has 'name' field, use that
                if 'name' in value:
                    value = value['name']
                else:
                    value = str(value)
            else:
                value = str(value)
            bibtex_str += f"    {field} = \"{value}\",\n"
        bibtex_str = bibtex_str.rstrip(",\n") + "\n}"

        # Create expected fields dictionary
        title_val = entry.fields.get('title', '').replace('{', '').replace('}', '').replace('\n', ' ')
        date_dict = {'year': int(entry.fields.get('year', 0))}
        if 'month' in entry.fields and entry.fields.get('month', ''):
            date_dict['month'] = entry.fields['month']
        
        # Handle author field which may be a list or string
        author_field = entry.fields.get('author', '')
        if isinstance(author_field, list):
            authors = author_field
        else:
            authors = [author_field]
        
        # Convert 'Last, First' to 'First Last' for expected values
        def to_first_last(name):
            name = name.strip()
            if ', ' in name:
                parts = name.split(', ', 1)
                return parts[1] + ' ' + parts[0]
            return name
        authors = [to_first_last(author) for author in authors]

        expected = {
            'title': title_val,
            'date': date_dict,
            'author': [{'ins': author, 'name': author} for author in authors],
        }
        # Add optional fields if present
        for field in ['journal', 'publisher', 'booktitle', 'school', 'institution', 'number', 'note', 'pages', 'url', 'abstract', 'isbn', 'edition']:
            if field in entry.fields:
                val = entry.fields[field].replace('{', '').replace('}', '').replace('\n', ' ')
                # Convert number/edition to int if possible
                if field in ['number', 'edition']:
                    if val.isdigit():
                        val = int(val)
                expected[field] = val

        # Run the test using existing function
        run_kdrfc_test(bibtex_str, expected, entry.key)

def test_kdrfc_invalid_encoding():
    """Test that a file with invalid encoding raises InvalidInputError."""
    from pathlib import Path
    from bibtex2rfcv2.parser import parse_bibtex
    from bibtex2rfcv2.error_handling import InvalidInputError
    bib_path = Path("tests/data/invalid_encoding.bibtex")
    with pytest.raises(InvalidInputError):
        parse_bibtex(bib_path) 