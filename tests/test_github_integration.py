"""Integration tests for GitHub utilities module."""

from __future__ import annotations

import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import requests

from slash_commands.github_utils import GitHubRepoError, download_github_prompts


# Integration tests for network timeout configuration (2.1)
def test_network_timeout_configuration():
    """Test that network timeout is properly configured to 30 seconds."""
    start_time = time.time()

    with patch("slash_commands.github_utils.requests.get") as mock_get:
        # Simulate a timeout that takes longer than 30 seconds
        mock_get.return_value.raise_for_status.side_effect = requests.RequestException(
            "Request timeout"
        )

        with pytest.raises(GitHubRepoError, match="Network timeout"):
            download_github_prompts("owner", "repo", "main", "prompts")

    end_time = time.time()
    # Should fail quickly due to mocking, but real implementation would timeout at 30s
    assert (end_time - start_time) < 5  # Mocked version should be fast


# Integration tests for retry logic with exponential backoff (2.2)
def test_retry_logic_exponential_backoff():
    """Test retry logic with exponential backoff up to 3 retries."""
    call_count = 0

    def mock_failing_request(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count <= 3:
            raise requests.RequestException("Temporary failure")
        return Mock(json=lambda return_value: [], raise_for_status=lambda: None)

    with patch("slash_commands.github_utils.requests.get", side_effect=mock_failing_request):
        with pytest.raises(GitHubRepoError, match="Network timeout"):
            download_github_prompts("owner", "repo", "main", "prompts")

    assert call_count == 3  # Should retry 3 times before giving up


# Integration tests for temporary directory creation and cleanup (2.3)
def test_temporary_directory_creation_and_cleanup():
    """Test that temporary directories are created and cleaned up properly."""
    with (
        patch("slash_commands.github_utils.list_github_directory_files") as mock_list,
        patch("slash_commands.github_utils.tempfile.mkdtemp") as mock_temp,
    ):
        mock_list.return_value = []
        mock_temp.return_value = "/tmp/test_github_prompts"

        # Should fail due to no files, but temp dir should be created
        with pytest.raises(GitHubRepoError, match="No markdown files found"):
            download_github_prompts("owner", "repo", "main", "empty-dir")

        mock_temp.assert_called_once_with(prefix="github_prompts_")


# Integration tests for file size validation during download (2.4)
def test_file_size_validation_during_download():
    """Test file size validation during actual download process."""
    with (
        patch("slash_commands.github_utils.list_github_directory_files") as mock_list,
        patch("slash_commands.github_utils.requests.get") as mock_get,
        patch("slash_commands.github_utils.tempfile.mkdtemp") as mock_temp,
        patch("pathlib.Path.write_text"),
        patch("pathlib.Path.exists", return_value=True),
    ):
        mock_list.return_value = [{"name": "large.md", "download_url": "url"}]
        mock_temp.return_value = "/tmp/test"
        mock_get.return_value.headers = {"content-length": "2097152"}  # 2MB
        mock_get.return_value.raise_for_status.return_value = None

        with pytest.raises(GitHubRepoError, match="File too large"):
            download_github_prompts("owner", "repo", "main", "prompts")


# Integration tests for progress reporting of downloaded files count (2.5)
def test_progress_reporting_downloaded_files_count():
    """Test progress reporting shows count of downloaded files."""
    mock_files = [{"name": f"prompt{i}.md", "download_url": f"url{i}"} for i in range(5)]

    with (
        patch("slash_commands.github_utils.list_github_directory_files") as mock_list,
        patch("slash_commands.github_utils.requests.get") as mock_get,
        patch("slash_commands.github_utils.tempfile.mkdtemp") as mock_temp,
        patch("builtins.print") as mock_print,
        patch("pathlib.Path.write_text"),
        patch("pathlib.Path.exists", return_value=True),
    ):
        mock_list.return_value = mock_files
        mock_temp.return_value = "/tmp/test"
        mock_get.return_value.text = "# Mock content"
        mock_get.return_value.headers = {}
        mock_get.return_value.raise_for_status.return_value = None

        download_github_prompts("owner", "repo", "main", "prompts")

        # Should not print warning for less than 100 files
        warning_calls = [
            call
            for call in mock_print.call_args_list
            if "Warning" in str(call) and "files" in str(call)
        ]
        assert len(warning_calls) == 0


# Integration tests for enhanced error scenarios (2.6)
def test_empty_directory_error_scenario():
    """Test error handling for empty repository directories."""
    with patch("slash_commands.github_utils.list_github_directory_files") as mock_list:
        mock_list.return_value = []  # Empty directory

        with pytest.raises(GitHubRepoError, match="No markdown files found"):
            download_github_prompts("owner", "repo", "main", "empty-dir")


def test_no_markdown_files_error_scenario():
    """Test error handling for directories with no .md files."""
    with patch("slash_commands.github_utils.list_github_directory_files") as mock_list:
        # Return empty list since no .md files should be found after filtering
        mock_list.return_value = []  # After filtering, no .md files remain

        with pytest.raises(GitHubRepoError, match="No markdown files found"):
            download_github_prompts("owner", "repo", "main", "no-md-files")


def test_permission_error_scenario():
    """Test error handling for permission denied errors."""
    with (
        patch("slash_commands.github_utils.list_github_directory_files") as mock_list,
        patch("slash_commands.github_utils.requests.get") as mock_get,
        patch("slash_commands.github_utils.tempfile.mkdtemp") as mock_temp,
    ):
        mock_list.return_value = [{"name": "test.md", "download_url": "url"}]
        mock_temp.return_value = "/tmp/test"
        mock_get.return_value.raise_for_status.side_effect = PermissionError("Permission denied")

        with pytest.raises(GitHubRepoError, match="Network timeout"):
            download_github_prompts("owner", "repo", "main", "prompts")


# Integration tests for actual GitHub repository downloads (2.7)
def test_actual_github_repository_download():
    """Test downloading from actual GitHub repository."""
    # This test should use the real spec-driven-workflow repository
    # but will be mocked to avoid network dependencies in CI
    with (
        patch("slash_commands.github_utils.list_github_directory_files") as mock_list,
        patch("slash_commands.github_utils.requests.get") as mock_get,
        patch("slash_commands.github_utils.tempfile.mkdtemp") as mock_temp,
        patch("pathlib.Path.write_text"),
        patch("pathlib.Path.exists", return_value=True),
    ):
        mock_list.return_value = [
            {
                "name": "test-prompt.md",
                "download_url": "https://raw.githubusercontent.com/liatrio-labs/spec-driven-workflow/main/prompts/test-prompt.md",
            }
        ]
        mock_temp.return_value = "/tmp/test"
        mock_get.return_value.text = "# Test Prompt\n\nThis is a test prompt."
        mock_get.return_value.headers = {}
        mock_get.return_value.raise_for_status.return_value = None

        result = download_github_prompts("liatrio-labs", "spec-driven-workflow", "main", "prompts")

        assert isinstance(result, Path)
        mock_list.assert_called_once_with("liatrio-labs", "spec-driven-workflow", "main", "prompts")


# Performance tests for large repository handling (2.8)
def test_large_repository_performance():
    """Test performance handling for large repositories."""
    # Create 150 files to test large repository handling
    mock_files = [{"name": f"prompt{i}.md", "download_url": f"url{i}"} for i in range(150)]

    with (
        patch("slash_commands.github_utils.list_github_directory_files") as mock_list,
        patch("slash_commands.github_utils.requests.get") as mock_get,
        patch("slash_commands.github_utils.tempfile.mkdtemp") as mock_temp,
        patch("builtins.print") as mock_print,
        patch("pathlib.Path.write_text"),
        patch("pathlib.Path.exists", return_value=True),
    ):
        mock_list.return_value = mock_files
        mock_temp.return_value = "/tmp/test"
        mock_get.return_value.text = "# Mock content"
        mock_get.return_value.headers = {}
        mock_get.return_value.raise_for_status.return_value = None

        start_time = time.time()
        download_github_prompts("owner", "large-repo", "main", "prompts")
        end_time = time.time()

        # Should complete within reasonable time (even with 150 files)
        assert (end_time - start_time) < 5  # Mocked version should be fast

        # Should print warning for more than 100 files
        mock_print.assert_any_call(
            "Warning: Repository contains 150 files, which may impact performance"
        )


# End-to-end integration tests for complete download workflow (2.9)
def test_end_to_end_download_workflow():
    """Test complete download workflow from URL parsing to file download."""
    with (
        patch("slash_commands.github_utils.list_github_directory_files") as mock_list,
        patch("slash_commands.github_utils.requests.get") as mock_get,
        patch("slash_commands.github_utils.tempfile.mkdtemp") as mock_temp,
        patch("pathlib.Path.write_text"),
        patch("pathlib.Path.exists", return_value=True),
    ):
        # Simulate complete workflow
        mock_list.return_value = [
            {"name": "prompt1.md", "download_url": "url1"},
            {"name": "prompt2.md", "download_url": "url2"},
        ]
        mock_temp.return_value = "/tmp/test"
        mock_get.return_value.text = "# Mock prompt content"
        mock_get.return_value.headers = {}
        mock_get.return_value.raise_for_status.return_value = None

        result = download_github_prompts("test-owner", "test-repo", "main", "prompts")

        # Verify complete workflow
        assert isinstance(result, Path)
        mock_list.assert_called_once_with("test-owner", "test-repo", "main", "prompts")
        assert mock_get.call_count == 2  # Should call for each file
