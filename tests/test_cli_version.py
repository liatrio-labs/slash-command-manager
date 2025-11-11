"""Tests for CLI version functionality."""

import re
from unittest.mock import patch

import pytest
import typer
from typer.testing import CliRunner

from slash_commands.__version__ import __version__
from slash_commands.cli import app, version_callback_impl


def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from text."""
    ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
    return ansi_escape.sub("", text)


# Helper to get current version for tests
def get_current_version():
    """Get the current version for use in tests."""
    return __version__


class TestCLIVersion:
    """Test CLI version functionality."""

    def test_version_callback(self):
        """Test the version callback function."""
        # Test that callback raises typer.Exit when True
        with pytest.raises(typer.Exit):
            version_callback_impl(True)

        # Test that callback doesn't exit when False
        result = version_callback_impl(False)
        assert result is None

    def test_version_flag(self):
        """Test --version flag."""
        runner = CliRunner()
        result = runner.invoke(app, ["--version"])

        assert result.exit_code == 0
        assert "slash-man" in result.stdout
        # Should contain version like "1.0.0" or "1.0.0+abc123"
        current_version = get_current_version()
        assert current_version in result.stdout

    def test_short_version_flag(self):
        """Test -v short flag."""
        runner = CliRunner()
        result = runner.invoke(app, ["-v"])

        assert result.exit_code == 0
        assert "slash-man" in result.stdout
        current_version = get_current_version()
        assert current_version in result.stdout

    def test_version_in_help(self):
        """Test that version option appears in help."""
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        # Strip ANSI codes to check for text content
        output = strip_ansi(result.stdout)
        assert "--version" in output
        assert "-v" in output
        assert "Show version and exit" in output

    def test_version_not_available_in_subcommands(self):
        """Test that version flag is not available in subcommands."""
        runner = CliRunner()

        # Test generate subcommand
        result = runner.invoke(app, ["generate", "--version"])
        assert result.exit_code != 0  # Should fail, not succeed

        # Test cleanup subcommand
        result = runner.invoke(app, ["cleanup", "--version"])
        assert result.exit_code != 0  # Should fail, not succeed

    def test_version_format_consistency(self):
        """Test that version format is consistent between calls."""
        runner = CliRunner()

        # Test --version
        result1 = runner.invoke(app, ["--version"])
        assert result1.exit_code == 0
        version1 = result1.stdout.strip()

        # Test -v
        result2 = runner.invoke(app, ["-v"])
        assert result2.exit_code == 0
        version2 = result2.stdout.strip()

        # Should be identical
        assert version1 == version2

    def test_version_contains_commit_when_available(self):
        """Test that version contains commit SHA when available."""
        runner = CliRunner()
        result = runner.invoke(app, ["--version"])

        assert result.exit_code == 0
        output = result.stdout.strip()
        current_version = get_current_version()

        # Should start with "slash-man {current_version}"
        assert output.startswith(f"slash-man {current_version}")

        # May or may not have commit SHA depending on environment
        if "+" in output:
            # If commit is present, it should be 7 characters (short SHA)
            version_part = output.split(" ", 1)[1]  # Remove "slash-man " prefix
            if "+" in version_part:
                commit = version_part.split("+", 1)[1]
                assert len(commit) == 7
                assert commit.isalnum()

    def test_version_with_build_time_commit(self):
        """Test version when build-time commit is available."""
        runner = CliRunner()
        current_version = get_current_version()

        # Mock the version import to test with build-time commit
        with patch("slash_commands.cli.__version_with_commit__", f"{current_version}+build123"):
            result = runner.invoke(app, ["--version"])
            assert result.exit_code == 0
            assert "build123" in result.stdout

    def test_subcommands_still_work(self):
        """Test that adding version flag doesn't break subcommands."""
        runner = CliRunner()

        # Test that subcommands still work
        result = runner.invoke(app, ["generate", "--help"])
        assert result.exit_code == 0
        assert "Generate" in result.stdout or "generate" in result.stdout.lower()

        result = runner.invoke(app, ["cleanup", "--help"])
        assert result.exit_code == 0
        assert "Clean up" in result.stdout or "cleanup" in result.stdout.lower()
