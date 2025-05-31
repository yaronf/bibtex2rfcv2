"""Tests for the CLI module."""

from click.testing import CliRunner
import pytest
from bibtex2rfcv2.cli import main
import shutil
import os
from pathlib import Path
from unittest import mock
import tempfile
import subprocess


def test_version() -> None:
    """Test version command."""
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "main, version" in result.output.lower()


def test_to_xml_command():
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create a minimal valid BibTeX file
        os.makedirs('tests/data', exist_ok=True)
        minimal_bibtex = '@article{test, author="John Doe", title="Test Title", year="2023", journal="Test Journal"}'
        with open('tests/data/minimal.bibtex', 'w') as f:
            f.write(minimal_bibtex)
        result = runner.invoke(main, ['to-xml', 'tests/data/minimal.bibtex', 'output.xml'])
        assert result.exit_code == 0
        assert 'Conversion completed. 1 entries written to output.xml.' in result.output
        # Check that output.xml was created and contains expected XML
        with open('output.xml') as f:
            xml_content = f.read()
        assert '<author fullname="John Doe"' in xml_content
        assert '<title>Test Title</title>' in xml_content


def test_to_kdrfc_command():
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create a minimal valid BibTeX file
        os.makedirs('tests/data', exist_ok=True)
        minimal_bibtex = '@article{test, author="John Doe", title="Test Title", year="2023", journal="Test Journal"}'
        with open('tests/data/minimal.bibtex', 'w') as f:
            f.write(minimal_bibtex)
        result = runner.invoke(main, ['to-kdrfc', 'tests/data/minimal.bibtex', 'output.yaml'])
        assert result.exit_code == 0
        assert 'Conversion completed. 1 entries written to output.yaml.' in result.output
        # Check that output.yaml was created and contains expected YAML
        with open('output.yaml') as f:
            yaml_content = f.read()
        assert 'title: Test Title' in yaml_content
        assert 'author:' in yaml_content
        assert '  - John Doe' in yaml_content


def test_to_xml_command_with_missing_fields():
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Use absolute path to the icml2023.bibtex file
        src = str(Path(__file__).parent.parent / 'tests' / 'data' / 'icml2023.bibtex')
        os.makedirs('tests/data', exist_ok=True)
        shutil.copyfile(src, 'tests/data/icml2023.bibtex')
        result = runner.invoke(main, ['to-xml', 'tests/data/icml2023.bibtex', 'output.xml'])
        assert result.exit_code != 0
        assert 'Error: Missing required fields: author or editor, and title' in result.output


def test_to_xml_command_with_invalid_file():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, ['to-xml', 'nonexistent.bibtex', 'output.xml'])
        assert result.exit_code != 0
        assert 'Error: File not found: nonexistent.bibtex' in result.output


def test_file_reading():
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create a minimal valid BibTeX file
        os.makedirs('tests/data', exist_ok=True)
        minimal_bibtex = '@article{test, author="John Doe", title="Test Title", year="2023", journal="Test Journal"}'
        with open('tests/data/minimal.bibtex', 'w') as f:
            f.write(minimal_bibtex)
        result = runner.invoke(main, ['to-xml', 'tests/data/minimal.bibtex', 'output.xml'])
        assert result.exit_code == 0
        assert 'Conversion completed. 1 entries written to output.xml.' in result.output


def test_file_writing():
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create a minimal valid BibTeX file
        os.makedirs('tests/data', exist_ok=True)
        minimal_bibtex = '@article{test, author="John Doe", title="Test Title", year="2023", journal="Test Journal"}'
        with open('tests/data/minimal.bibtex', 'w') as f:
            f.write(minimal_bibtex)
        result = runner.invoke(main, ['to-xml', 'tests/data/minimal.bibtex', 'output.xml'])
        assert result.exit_code == 0
        assert 'Conversion completed. 1 entries written to output.xml.' in result.output
        # Check that output.xml was created and contains expected XML
        with open('output.xml') as f:
            xml_content = f.read()
        assert '<author fullname="John Doe"' in xml_content
        assert '<title>Test Title</title>' in xml_content


def test_file_permissions():
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create a minimal valid BibTeX file
        os.makedirs('tests/data', exist_ok=True)
        minimal_bibtex = '@article{test, author="John Doe", title="Test Title", year="2023", journal="Test Journal"}'
        with open('tests/data/minimal.bibtex', 'w') as f:
            f.write(minimal_bibtex)
        # Mock os.access to simulate permission denied
        with mock.patch('os.access', return_value=False):
            result = runner.invoke(main, ['to-xml', 'tests/data/minimal.bibtex', 'output.xml'])
            assert result.exit_code != 0
            assert 'Error: Permission denied' in result.output


def test_stdin_stdout():
    runner = CliRunner()
    minimal_bibtex = '@article{test, author="John Doe", title="Test Title", year="2023", journal="Test Journal"}'
    result = runner.invoke(main, ['to-xml', '-', '-'], input=minimal_bibtex)
    assert result.exit_code == 0
    assert '<author fullname="John Doe"' in result.output
    assert '<title>Test Title</title>' in result.output


def test_stdin_file_output():
    runner = CliRunner()
    with runner.isolated_filesystem():
        minimal_bibtex = '@article{test, author="John Doe", title="Test Title", year="2023", journal="Test Journal"}'
        result = runner.invoke(main, ['to-xml', '-', 'output.xml'], input=minimal_bibtex)
        assert result.exit_code == 0
        assert 'Conversion completed. 1 entries written to output.xml.' in result.output
        with open('output.xml') as f:
            xml_content = f.read()
        assert '<author fullname="John Doe"' in xml_content
        assert '<title>Test Title</title>' in xml_content


def test_file_input_stdout():
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create a minimal valid BibTeX file
        os.makedirs('tests/data', exist_ok=True)
        minimal_bibtex = '@article{test, author="John Doe", title="Test Title", year="2023", journal="Test Journal"}'
        with open('tests/data/minimal.bibtex', 'w') as f:
            f.write(minimal_bibtex)
        result = runner.invoke(main, ['to-xml', 'tests/data/minimal.bibtex', '-'])
        assert result.exit_code == 0
        assert '<author fullname="John Doe"' in result.output
        assert '<title>Test Title</title>' in result.output


def test_batch_processing():
    """Test batch processing of multiple references."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create a BibTeX file with multiple entries
        os.makedirs('tests/data', exist_ok=True)
        multiple_bibtex = '''@article{test1,
    author = "John Doe",
    title = "Test Title 1",
    year = "2023",
    journal = "Test Journal"
}
@article{test2,
    author = "Jane Smith",
    title = "Test Title 2",
    year = "2023",
    journal = "Test Journal"
}'''
        with open('tests/data/multiple.bibtex', 'w') as f:
            f.write(multiple_bibtex)
        
        # Test with progress bar
        result = runner.invoke(main, ['to-xml', 'tests/data/multiple.bibtex', 'output.xml'])
        assert result.exit_code == 0
        assert 'Conversion completed. 2 entries written to output.xml.' in result.output
        
        # Check that output.xml was created and contains both entries
        with open('output.xml') as f:
            xml_content = f.read()
        assert '<reference anchor="test1">' in xml_content
        assert '<reference anchor="test2">' in xml_content
        assert '<author fullname="John Doe"' in xml_content
        assert '<author fullname="Jane Smith"' in xml_content
        assert '<title>Test Title 1</title>' in xml_content
        assert '<title>Test Title 2</title>' in xml_content
        
        # Test without progress bar
        result = runner.invoke(main, ['to-xml', '--no-progress', 'tests/data/multiple.bibtex', 'output2.xml'])
        assert result.exit_code == 0
        assert 'Conversion completed. 2 entries written to output2.xml.' in result.output

        # Test xml2rfc compatibility
        # Use absolute paths for fixture files
        test_dir = Path(__file__).parent.parent.resolve()
        preamble_src = test_dir / 'tests' / 'fixtures' / 'preamble.xml'
        postamble_src = test_dir / 'tests' / 'fixtures' / 'postamble.xml'
        preamble_path = Path('preamble.xml')
        postamble_path = Path('postamble.xml')
        shutil.copyfile(preamble_src, preamble_path)
        shutil.copyfile(postamble_src, postamble_path)
        assert preamble_path.exists(), "preamble.xml not found"
        assert postamble_path.exists(), "postamble.xml not found"

        # Create a complete RFC document with the references
        with open('output.xml') as f:
            references_xml = f.read()
        full_xml = preamble_path.read_text() + references_xml + postamble_path.read_text()

        # Write to temporary file and validate with xml2rfc
        with tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False) as tmp:
            tmp.write(full_xml)
            tmp_path = tmp.name
        try:
            result = subprocess.run([
                "xml2rfc", tmp_path, "--no-dtd", "--quiet"
            ], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"\nDebug: xml2rfc validation failed")
                print(f"Error output: {result.stderr}")
                print(f"Full XML content:")
                print(full_xml)
            assert result.returncode == 0, f"xml2rfc validation failed: {result.stderr}"
        finally:
            os.remove(tmp_path) 


def test_kdrfc_processing():
    """Test that the kdrfc tool processes the generated reference correctly."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create a minimal valid BibTeX file
        os.makedirs('tests/data', exist_ok=True)
        minimal_bibtex = '@article{test, author="John Doe", title="Test Title", year="2023", journal="Test Journal"}'
        with open('tests/data/minimal.bibtex', 'w') as f:
            f.write(minimal_bibtex)
        result = runner.invoke(main, ['to-kdrfc', 'tests/data/minimal.bibtex', 'output.yaml'])
        assert result.exit_code == 0
        assert 'Conversion completed. 1 entries written to output.yaml.' in result.output
        # Check that output.yaml was created and contains expected YAML
        with open('output.yaml') as f:
            yaml_content = f.read()
        assert 'title: Test Title' in yaml_content
        assert 'author:' in yaml_content
        assert '  - ins: John Doe' in yaml_content

        # Print the generated YAML content for inspection
        print("Generated YAML content:")
        print(yaml_content)

        # Copy preamble and postamble files into the isolated filesystem
        shutil.copyfile(os.path.join(os.path.dirname(__file__), 'fixtures', 'preamble.md'), 'preamble.md')
        shutil.copyfile(os.path.join(os.path.dirname(__file__), 'fixtures', 'postamble.md'), 'postamble.md')

        # Create a complete Markdown document with the references
        with open('preamble.md') as f:
            preamble_content = f.read()
        with open('postamble.md') as f:
            postamble_content = f.read()
        full_markdown = preamble_content + yaml_content + postamble_content

        # Print the full Markdown content for inspection
        print("Full Markdown content:")
        print(full_markdown)

        # Write to temporary file and validate with kdrfc
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as tmp:
            tmp.write(full_markdown)
            tmp_path = tmp.name
        try:
            result = subprocess.run([
                "kdrfc", tmp_path, "-v", "-x"
            ], capture_output=True, text=True)
            assert result.returncode == 0, f"kdrfc validation failed: {result.stderr}"
        finally:
            os.remove(tmp_path) 