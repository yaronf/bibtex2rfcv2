"""Tests for the CLI module."""

from click.testing import CliRunner
import pytest
from bibtex2rfcv2.cli import main
import shutil
import os
from pathlib import Path
from unittest import mock


def test_version() -> None:
    """Test version command."""
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "version" in result.output.lower()


def test_convert_command():
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create a minimal valid BibTeX file
        os.makedirs('tests/data', exist_ok=True)
        minimal_bibtex = '@article{test, author="John Doe", title="Test Title", year="2023", journal="Test Journal"}'
        with open('tests/data/minimal.bibtex', 'w') as f:
            f.write(minimal_bibtex)
        result = runner.invoke(main, ['convert', 'tests/data/minimal.bibtex', 'output.xml'])
        assert result.exit_code == 0
        assert 'Conversion completed. Output written to output.xml.' in result.output
        # Check that output.xml was created and contains expected XML
        with open('output.xml') as f:
            xml_content = f.read()
        assert '<author fullname="John Doe"' in xml_content
        assert '<title>Test Title</title>' in xml_content


def test_convert_command_with_missing_fields():
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Use absolute path to the icml2023.bibtex file
        src = str(Path(__file__).parent.parent / 'tests' / 'data' / 'icml2023.bibtex')
        os.makedirs('tests/data', exist_ok=True)
        shutil.copyfile(src, 'tests/data/icml2023.bibtex')
        result = runner.invoke(main, ['convert', 'tests/data/icml2023.bibtex', 'output.xml'])
        assert result.exit_code != 0
        assert 'Error: Missing required fields: author or editor, and title' in result.output


def test_help_message():
    runner = CliRunner()
    result = runner.invoke(main, ['--help'])
    assert result.exit_code == 0
    assert 'Convert BibTeX citations to RFC-compliant XML references.' in result.output


def test_convert_command_with_invalid_file():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, ['convert', 'nonexistent.bibtex', 'output.xml'])
        assert result.exit_code != 0
        assert 'Error' in result.output


# New test for file reading
def test_file_reading():
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create a minimal valid BibTeX file
        os.makedirs('tests/data', exist_ok=True)
        minimal_bibtex = '@article{test, author="John Doe", title="Test Title", year="2023", journal="Test Journal"}'
        with open('tests/data/minimal.bibtex', 'w') as f:
            f.write(minimal_bibtex)
        result = runner.invoke(main, ['convert', 'tests/data/minimal.bibtex', 'output.xml'])
        assert result.exit_code == 0
        assert 'Conversion completed. Output written to output.xml.' in result.output


# New test for file writing
def test_file_writing():
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create a minimal valid BibTeX file
        os.makedirs('tests/data', exist_ok=True)
        minimal_bibtex = '@article{test, author="John Doe", title="Test Title", year="2023", journal="Test Journal"}'
        with open('tests/data/minimal.bibtex', 'w') as f:
            f.write(minimal_bibtex)
        result = runner.invoke(main, ['convert', 'tests/data/minimal.bibtex', 'output.xml'])
        assert result.exit_code == 0
        assert 'Conversion completed. Output written to output.xml.' in result.output
        # Check that output.xml was created and contains expected XML
        with open('output.xml') as f:
            xml_content = f.read()
        assert '<author fullname="John Doe"' in xml_content
        assert '<title>Test Title</title>' in xml_content


# New test for file permissions
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
            result = runner.invoke(main, ['convert', 'tests/data/minimal.bibtex', 'output.xml'])
            assert result.exit_code != 0
            assert "Permission denied" in result.output


# New test for stdin support
def test_stdin_stdout():
    runner = CliRunner()
    minimal_bibtex = '@article{test, author="John Doe", title="Test Title", year="2023", journal="Test Journal"}'
    result = runner.invoke(main, ['convert', '-', '-'], input=minimal_bibtex)
    assert result.exit_code == 0
    assert '<author fullname="John Doe"' in result.output
    assert '<title>Test Title</title>' in result.output


# New test for stdin with file output
def test_stdin_file_output():
    runner = CliRunner()
    with runner.isolated_filesystem():
        minimal_bibtex = '@article{test, author="John Doe", title="Test Title", year="2023", journal="Test Journal"}'
        result = runner.invoke(main, ['convert', '-', 'output.xml'], input=minimal_bibtex)
        assert result.exit_code == 0
        assert 'Conversion completed. Output written to output.xml.' in result.output
        with open('output.xml') as f:
            xml_content = f.read()
        assert '<author fullname="John Doe"' in xml_content
        assert '<title>Test Title</title>' in xml_content


# New test for file input with stdout
def test_file_input_stdout():
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create a minimal valid BibTeX file
        os.makedirs('tests/data', exist_ok=True)
        minimal_bibtex = '@article{test, author="John Doe", title="Test Title", year="2023", journal="Test Journal"}'
        with open('tests/data/minimal.bibtex', 'w') as f:
            f.write(minimal_bibtex)
        result = runner.invoke(main, ['convert', 'tests/data/minimal.bibtex', '-'])
        assert result.exit_code == 0
        assert '<author fullname="John Doe"' in result.output
        assert '<title>Test Title</title>' in result.output 