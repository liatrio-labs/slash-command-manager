"""Tests for version functionality and git commit detection."""

import subprocess
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from slash_commands.__version__ import (
    __version__,
    __version_with_commit__,
    _get_build_time_commit,
    _get_git_commit,
    _get_version,
    _get_version_with_commit,
)


# Helper to get current version for tests
def get_current_version():
    """Get the current version for use in tests."""
    return __version__


class TestVersionModule:
    """Test the version module functionality."""

    def test_version_exists(self):
        """Test that version variables are defined."""
        assert __version__ is not None
        assert isinstance(__version__, str)
        assert __version_with_commit__ is not None
        assert isinstance(__version_with_commit__, str)

    def test_version_format(self):
        """Test that version follows expected format."""
        current_version = get_current_version()
        # Base version should be semantic version like "1.0.0"
        assert "." in current_version
        assert len(current_version.split(".")) >= 2

        # Version with commit should be either "1.0.0" or "1.0.0+abc123"
        if "+" in __version_with_commit__:
            base, commit = __version_with_commit__.split("+", 1)
            assert base == current_version
            assert len(commit) == 7  # Short git commit SHA
            assert commit.isalnum()


class TestBuildTimeCommit:
    """Test build-time commit detection."""

    def test_no_build_time_commit_file(self):
        """Test when build-time commit file doesn't exist."""
        # Ensure the file doesn't exist
        with patch.dict("sys.modules", **{"slash_commands._git_commit": None}):
            with patch("builtins.__import__", side_effect=ImportError("No module named")):
                result = _get_build_time_commit()
                assert result is None

    def test_build_time_commit_file_exists(self):
        """Test when build-time commit file exists."""
        # Mock the import to return a test commit
        mock_commit = "abc1234"

        with patch.dict("sys.modules"):
            with patch("builtins.__import__") as mock_import:
                mock_module = MagicMock()
                mock_module.__git_commit__ = mock_commit
                mock_import.return_value = mock_module

                result = _get_build_time_commit()
                assert result == mock_commit


class TestGitCommit:
    """Test git commit detection."""

    def test_git_commit_success(self):
        """Test successful git commit detection."""
        mock_commit = "def5678"

        with patch("slash_commands.__version__.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout=mock_commit, returncode=0)

            # Mock build-time commit to None to force runtime detection
            with patch("slash_commands.__version__._get_build_time_commit", return_value=None):
                result = _get_git_commit()
                assert result == mock_commit
                mock_run.assert_called_once()

    def test_git_commit_failure(self):
        """Test git commit detection failure."""
        with patch("slash_commands.__version__.subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(1, "git")

            # Mock build-time commit to None to force runtime detection
            with patch("slash_commands.__version__._get_build_time_commit", return_value=None):
                result = _get_git_commit()
                assert result is None

    def test_git_not_found(self):
        """Test when git command is not found."""
        with patch("slash_commands.__version__.subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError()

            # Mock build-time commit to None to force runtime detection
            with patch("slash_commands.__version__._get_build_time_commit", return_value=None):
                result = _get_git_commit()
                assert result is None

    def test_git_commit_uses_correct_directory(self):
        """Test that git command runs from the correct directory."""
        with patch("slash_commands.__version__.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="abc1234", returncode=0)

            # Mock build-time commit to None to force runtime detection
            with patch("slash_commands.__version__._get_build_time_commit", return_value=None):
                _get_git_commit()

                # Verify that cwd was set to the directory containing __version__.py
                call_args = mock_run.call_args
                assert "cwd" in call_args.kwargs
                # The cwd should be the directory where __version__.py is located
                # Works for both development (project root) and installed scenarios
                from slash_commands import __version__

                expected_dir = Path(__version__.__file__).parent.parent
                assert call_args.kwargs["cwd"] == expected_dir


class TestVersionDetection:
    """Test version detection logic."""

    def test_get_version_from_pyproject(self):
        """Test getting version from pyproject.toml."""
        # This should work in development
        version = _get_version()
        assert version is not None
        assert isinstance(version, str)
        assert "." in version

    def test_get_version_fallback_to_metadata(self):
        """Test fallback to importlib.metadata."""
        with patch("slash_commands.__version__.Path.exists", return_value=False):
            with patch("slash_commands.__version__.get_package_version") as mock_version:
                mock_version.return_value = "2.0.0"

                version = _get_version()
                assert version == "2.0.0"
                mock_version.assert_called_once_with("slash-man")

    def test_version_with_commit_priority(self):
        """Test that build-time commit takes priority over runtime."""
        current_version = get_current_version()
        mock_build_commit = "build123"
        mock_runtime_commit = "runtime456"

        with patch(
            "slash_commands.__version__._get_build_time_commit", return_value=mock_build_commit
        ):
            with patch("slash_commands.__version__.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(stdout=mock_runtime_commit, returncode=0)

                result = _get_version_with_commit()
                assert result == f"{current_version}+{mock_build_commit}"
                # Runtime git should not be called when build-time commit exists
                mock_run.assert_not_called()

    def test_version_with_commit_runtime_fallback(self):
        """Test fallback to runtime git detection."""
        current_version = get_current_version()
        mock_runtime_commit = "runtime789"

        with patch("slash_commands.__version__._get_build_time_commit", return_value=None):
            with patch("slash_commands.__version__.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(stdout=mock_runtime_commit, returncode=0)

                result = _get_version_with_commit()
                assert result == f"{current_version}+{mock_runtime_commit}"

    def test_version_with_commit_no_git(self):
        """Test version when no git commit is available."""
        current_version = get_current_version()

        with patch("slash_commands.__version__._get_build_time_commit", return_value=None):
            with patch("slash_commands.__version__.subprocess.run") as mock_run:
                mock_run.side_effect = subprocess.CalledProcessError(1, "git")

                result = _get_version_with_commit()
                assert result == current_version  # Just version, no commit


class TestVersionIntegration:
    """Integration tests for version functionality."""

    def test_version_in_different_git_repositories(self):
        """Test that version is consistent across different git repositories."""
        # Create a temporary directory with a different git repo
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Initialize a new git repo in temp directory
            subprocess.run(["git", "init"], cwd=temp_path, capture_output=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=temp_path,
                capture_output=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"], cwd=temp_path, capture_output=True
            )

            # Create and commit a file
            test_file = temp_path / "test.txt"
            test_file.write_text("test content")
            subprocess.run(["git", "add", "test.txt"], cwd=temp_path, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "test commit"], cwd=temp_path, capture_output=True
            )

            # Get the commit from the temp repo
            temp_commit = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=temp_path,
                capture_output=True,
                text=True,
            ).stdout.strip()

            # Mock build-time commit to None to force runtime detection
            with patch("slash_commands.__version__._get_build_time_commit", return_value=None):
                with patch("slash_commands.__version__.subprocess.run") as mock_run:
                    # Mock git to return the slash-command-manager commit (not temp repo)
                    slash_command_commit = "slash123"
                    mock_run.return_value = MagicMock(stdout=slash_command_commit, returncode=0)

                    # Get the commit - should be from slash-command-manager, not temp repo
                    result = _get_git_commit()

                    # The result should be the slash-command-manager commit
                    assert result == slash_command_commit
                    assert result != temp_commit

                    # Verify that git was called with the correct directory
                    # This should be the repository root (parent of slash_commands/)
                    # (works for both development and installed scenarios)
                    call_args = mock_run.call_args
                    from slash_commands import __version__

                    expected_dir = Path(__version__.__file__).parent.parent
                    assert call_args.kwargs["cwd"] == expected_dir

    def test_version_consistency(self):
        """Test that version is consistent across multiple calls."""
        # Clear any build-time commit to ensure consistent testing
        with patch("slash_commands.__version__._get_build_time_commit", return_value=None):
            version1 = _get_version_with_commit()
            version2 = _get_version_with_commit()

            assert version1 == version2


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_git_output(self):
        """Test handling of empty git output."""
        with patch("slash_commands.__version__.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="", returncode=0)

            # Mock build-time commit to None to force runtime detection
            with patch("slash_commands.__version__._get_build_time_commit", return_value=None):
                result = _get_git_commit()
                assert result == ""

    def test_git_output_with_newline(self):
        """Test handling of git output with trailing newline."""
        mock_commit = "abc1234\n"

        with patch("slash_commands.__version__.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout=mock_commit, returncode=0)

            # Mock build-time commit to None to force runtime detection
            with patch("slash_commands.__version__._get_build_time_commit", return_value=None):
                result = _get_git_commit()
                assert result == "abc1234"  # Newline should be stripped

    def test_corrupted_build_time_file(self):
        """Test handling of corrupted build-time file."""
        from types import SimpleNamespace

        with patch.dict("sys.modules"):
            with patch("builtins.__import__") as mock_import:
                # Mock a module without __git_commit__ attribute
                # Use SimpleNamespace to create an object that truly lacks the attribute
                mock_module = SimpleNamespace()
                mock_import.return_value = mock_module

                result = _get_build_time_commit()
                assert result is None
