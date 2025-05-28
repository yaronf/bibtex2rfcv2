"""Tests for the CLI module."""

from click.testing import CliRunner

from bibtex2rfcv2.cli import main


def test_version() -> None:
    """Test version command."""
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "version" in result.output.lower()


def test_convert_command() -> None:
    """Test convert command."""
    runner = CliRunner()
    result = runner.invoke(main, ["convert"])
    assert result.exit_code == 0
    assert "not yet implemented" in result.output.lower() 