"""Tests for GitHub utilities."""

from __future__ import annotations

import base64
from unittest.mock import MagicMock, patch

import pytest
import requests

from slash_commands.github_utils import (
    _download_github_prompts_to_temp_dir,
    download_prompts_from_github,
    validate_github_repo,
)


def test_validate_github_repo_valid_formats():
    """Test that validate_github_repo accepts valid repository formats."""
    # Test basic format
    owner, repo = validate_github_repo("owner/repo")
    assert owner == "owner"
    assert repo == "repo"

    # Test with hyphens
    owner, repo = validate_github_repo("liatrio-labs/spec-driven-workflow")
    assert owner == "liatrio-labs"
    assert repo == "spec-driven-workflow"

    # Test with underscores
    owner, repo = validate_github_repo("my_org/my_repo")
    assert owner == "my_org"
    assert repo == "my_repo"

    # Test with numbers
    owner, repo = validate_github_repo("org123/repo456")
    assert owner == "org123"
    assert repo == "repo456"


def test_validate_github_repo_invalid_formats():
    """Test that validate_github_repo rejects invalid repository formats."""
    # Test invalid format without slash
    with pytest.raises(ValueError, match="Repository must be in format owner/repo"):
        validate_github_repo("invalid-format")

    # Test invalid format with multiple slashes
    with pytest.raises(ValueError, match="Repository must be in format owner/repo"):
        validate_github_repo("owner/repo/extra")

    # Test empty string
    with pytest.raises(ValueError, match="Repository must be in format owner/repo"):
        validate_github_repo("")

    # Test only owner (no slash)
    with pytest.raises(ValueError, match="Repository must be in format owner/repo"):
        validate_github_repo("owner")

    # Test owner with trailing slash but no repo
    with pytest.raises(ValueError, match="Repository must be in format owner/repo"):
        validate_github_repo("owner/")

    # Test slash only
    with pytest.raises(ValueError, match="Repository must be in format owner/repo"):
        validate_github_repo("/")

    # Test leading slash
    with pytest.raises(ValueError, match="Repository must be in format owner/repo"):
        validate_github_repo("/repo")


def test_validate_github_repo_error_message_includes_example():
    """Test that error messages include helpful example."""
    with pytest.raises(ValueError) as exc_info:
        validate_github_repo("invalid-format")
    error_msg = str(exc_info.value)
    assert "liatrio-labs/spec-driven-workflow" in error_msg
    assert "Example:" in error_msg


@patch("slash_commands.github_utils.requests.get")
def test_download_prompts_from_github_directory(mock_get):
    """Test downloading prompts from a GitHub directory."""
    # Mock GitHub API response for directory listing
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            "name": "prompt1.md",
            "type": "file",
            "content": base64.b64encode(b"# Prompt 1\nContent").decode("utf-8"),
            "encoding": "base64",
        },
        {
            "name": "prompt2.md",
            "type": "file",
            "content": base64.b64encode(b"# Prompt 2\nContent").decode("utf-8"),
            "encoding": "base64",
        },
        {
            "name": "readme.txt",
            "type": "file",
            "content": base64.b64encode(b"Readme content").decode("utf-8"),
            "encoding": "base64",
        },
        {
            "name": "subdir",
            "type": "dir",
        },
    ]
    mock_get.return_value = mock_response

    result = download_prompts_from_github("owner", "repo", "main", "prompts")

    # Verify API call
    mock_get.assert_called_once_with(
        "https://api.github.com/repos/owner/repo/contents/prompts",
        params={"ref": "main"},
        headers={"Accept": "application/vnd.github+json"},
        timeout=30,
    )

    # Verify result - should only include .md files
    assert len(result) == 2
    assert result[0] == ("prompt1.md", "# Prompt 1\nContent")
    assert result[1] == ("prompt2.md", "# Prompt 2\nContent")


@patch("slash_commands.github_utils.requests.get")
def test_download_prompts_from_github_single_file(mock_get):
    """Test downloading a single prompt file from GitHub."""
    # Mock GitHub API response for single file
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "name": "generate-spec.md",
        "type": "file",
        "content": base64.b64encode(b"# Generate Spec\nContent").decode("utf-8"),
        "encoding": "base64",
    }
    mock_get.return_value = mock_response

    result = download_prompts_from_github("owner", "repo", "main", "prompts/generate-spec.md")

    # Verify API call
    mock_get.assert_called_once_with(
        "https://api.github.com/repos/owner/repo/contents/prompts/generate-spec.md",
        params={"ref": "main"},
        headers={"Accept": "application/vnd.github+json"},
        timeout=30,
    )

    # Verify result
    assert len(result) == 1
    assert result[0] == ("generate-spec.md", "# Generate Spec\nContent")


@patch("slash_commands.github_utils.requests.get")
def test_download_prompts_from_github_empty_directory(mock_get):
    """Test downloading from an empty directory (no .md files)."""
    # Mock GitHub API response for directory with no .md files
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            "name": "readme.txt",
            "type": "file",
            "content": base64.b64encode(b"Readme").decode("utf-8"),
            "encoding": "base64",
        },
    ]
    mock_get.return_value = mock_response

    result = download_prompts_from_github("owner", "repo", "main", "prompts")

    # Verify result is empty list (no .md files)
    assert result == []


@patch("slash_commands.github_utils.requests.get")
def test_download_prompts_from_github_single_file_non_markdown(mock_get):
    """Test that single file path must be a markdown file."""
    # Mock GitHub API response for non-markdown file
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "name": "readme.txt",
        "type": "file",
        "content": base64.b64encode(b"Readme").decode("utf-8"),
        "encoding": "base64",
    }
    mock_get.return_value = mock_response

    with pytest.raises(ValueError, match="must be a markdown file"):
        download_prompts_from_github("owner", "repo", "main", "prompts/readme.txt")


@patch("slash_commands.github_utils.requests.get")
def test_download_prompts_from_github_404_error(mock_get):
    """Test handling of 404 Not Found error."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
    mock_get.return_value = mock_response

    with pytest.raises(requests.exceptions.HTTPError):
        download_prompts_from_github("owner", "repo", "main", "nonexistent")


@patch("slash_commands.github_utils.requests.get")
def test_download_prompts_from_github_403_error(mock_get):
    """Test handling of 403 Forbidden error (rate limiting)."""
    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("403 Forbidden")
    mock_get.return_value = mock_response

    with pytest.raises(requests.exceptions.HTTPError):
        download_prompts_from_github("owner", "repo", "main", "prompts")


@patch("slash_commands.github_utils.requests.get")
def test_download_prompts_from_github_network_error(mock_get):
    """Test handling of network errors."""
    mock_get.side_effect = requests.exceptions.RequestException("Network error")

    with pytest.raises(requests.exceptions.RequestException):
        download_prompts_from_github("owner", "repo", "main", "prompts")


@patch("slash_commands.github_utils.requests.get")
def test_download_prompts_from_github_filters_subdirectories(mock_get):
    """Test that subdirectories are not processed recursively."""
    # Mock GitHub API response with subdirectories
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            "name": "prompt1.md",
            "type": "file",
            "content": base64.b64encode(b"# Prompt 1").decode("utf-8"),
            "encoding": "base64",
        },
        {
            "name": "subdir",
            "type": "dir",
        },
    ]
    mock_get.return_value = mock_response

    result = download_prompts_from_github("owner", "repo", "main", "prompts")

    # Should only return immediate .md files, not subdirectories
    assert len(result) == 1
    assert result[0][0] == "prompt1.md"


@patch("slash_commands.github_utils.requests.get")
def test_download_prompts_from_github_non_json_response(mock_get):
    """Test handling of non-JSON responses (e.g., HTML error pages)."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "text/html"}
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_get.return_value = mock_response

    with pytest.raises(ValueError, match="Invalid response from GitHub API"):
        download_prompts_from_github("owner", "repo", "main", "prompts")


@patch("slash_commands.github_utils.download_prompts_from_github")
def test_download_github_prompts_to_temp_dir(mock_download, tmp_path):
    """Test that _download_github_prompts_to_temp_dir writes files to temp directory."""
    mock_download.return_value = [
        ("prompt1.md", "# Prompt 1\nContent"),
        ("prompt2.md", "# Prompt 2\nContent"),
    ]

    _download_github_prompts_to_temp_dir("owner", "repo", "main", "prompts", tmp_path)

    # Verify files were written
    assert (tmp_path / "prompt1.md").exists()
    assert (tmp_path / "prompt2.md").exists()
    assert (tmp_path / "prompt1.md").read_text() == "# Prompt 1\nContent"
    assert (tmp_path / "prompt2.md").read_text() == "# Prompt 2\nContent"

    # Verify download function was called correctly
    mock_download.assert_called_once_with("owner", "repo", "main", "prompts")


@patch("slash_commands.github_utils.requests.get")
def test_download_prompts_from_github_http_error_without_response(mock_get):
    """Test handling of HTTPError without response attribute (edge case)."""
    # Create an HTTPError without a response attribute
    http_error = requests.exceptions.HTTPError("HTTP Error")
    # Explicitly remove response attribute if it exists
    if hasattr(http_error, "response"):
        delattr(http_error, "response")
    mock_get.side_effect = http_error

    # Should not raise AttributeError, should raise HTTPError
    with pytest.raises(requests.exceptions.HTTPError):
        download_prompts_from_github("owner", "repo", "main", "prompts")


@patch("slash_commands.github_utils.requests.get")
def test_download_prompts_from_github_403_error_with_rate_limit_headers(mock_get):
    """Test that 403 errors include rate limit information when available."""
    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.headers = {
        "X-RateLimit-Remaining": "0",
        "X-RateLimit-Reset": "1234567890",
    }
    # Create HTTPError and attach the response
    http_error = requests.exceptions.HTTPError("403 Forbidden")
    http_error.response = mock_response
    mock_response.raise_for_status.side_effect = http_error
    mock_get.return_value = mock_response

    with pytest.raises(requests.exceptions.HTTPError) as exc_info:
        download_prompts_from_github("owner", "repo", "main", "prompts")

    # Verify error message includes rate limit information
    error_msg = str(exc_info.value)
    assert (
        "rate limit" in error_msg.lower()
        or "X-RateLimit" in error_msg
        or "remaining" in error_msg.lower()
    )


@patch("slash_commands.github_utils.requests.get")
def test_download_prompts_from_github_directory_item_without_content_or_download_url(mock_get):
    """Test handling of directory items without content or download_url (fallback path)."""
    # First call returns directory listing without content/download_url
    directory_response = MagicMock()
    directory_response.status_code = 200
    directory_response.json.return_value = [
        {
            "name": "prompt1.md",
            "type": "file",
            # No content or download_url
        },
    ]

    # Second call (fallback) returns file content
    file_response = MagicMock()
    file_response.status_code = 200
    file_response.json.return_value = {
        "name": "prompt1.md",
        "type": "file",
        "content": base64.b64encode(b"# Prompt 1\nContent").decode("utf-8"),
        "encoding": "base64",
    }

    mock_get.side_effect = [directory_response, file_response]

    result = download_prompts_from_github("owner", "repo", "main", "prompts")

    # Verify fallback API call was made
    assert mock_get.call_count == 2
    # Verify result includes the file
    assert len(result) == 1
    assert result[0] == ("prompt1.md", "# Prompt 1\nContent")


@patch("slash_commands.github_utils.requests.get")
def test_download_prompts_from_github_malformed_base64_content(mock_get):
    """Test handling of malformed base64 content."""

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "name": "prompt.md",
        "type": "file",
        "content": "not-valid-base64!!!",  # Invalid base64
        "encoding": "base64",
    }
    mock_get.return_value = mock_response

    with pytest.raises(ValueError, match="Invalid file content encoding"):
        download_prompts_from_github("owner", "repo", "main", "prompts/prompt.md")


@patch("slash_commands.github_utils.requests.get")
def test_download_prompts_from_github_invalid_utf8_after_base64_decode(mock_get):
    """Test handling of invalid UTF-8 after base64 decoding."""

    # Create valid base64 that decodes to invalid UTF-8
    # Base64 encoding of bytes that aren't valid UTF-8
    invalid_utf8_bytes = bytes([0xFF, 0xFE, 0xFD])  # Invalid UTF-8 sequence
    invalid_base64 = base64.b64encode(invalid_utf8_bytes).decode("ascii")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "name": "prompt.md",
        "type": "file",
        "content": invalid_base64,
        "encoding": "base64",
    }
    mock_get.return_value = mock_response

    with pytest.raises(ValueError, match="Invalid file content encoding"):
        download_prompts_from_github("owner", "repo", "main", "prompts/prompt.md")


@patch("slash_commands.github_utils.requests.get")
def test_download_prompts_from_github_path_normalization(mock_get):
    """Test that paths are normalized correctly in fallback API calls."""
    # First call returns directory listing without content/download_url
    directory_response = MagicMock()
    directory_response.status_code = 200
    directory_response.json.return_value = [
        {
            "name": "prompt1.md",
            "type": "file",
            # No content or download_url
        },
    ]

    # Second call (fallback) returns file content
    file_response = MagicMock()
    file_response.status_code = 200
    file_response.json.return_value = {
        "name": "prompt1.md",
        "type": "file",
        "content": base64.b64encode(b"# Prompt 1\nContent").decode("utf-8"),
        "encoding": "base64",
    }

    mock_get.side_effect = [directory_response, file_response]

    # Test with a path that could potentially have traversal issues
    result = download_prompts_from_github("owner", "repo", "main", "prompts/subdir")

    # Verify fallback API call was made with normalized path
    assert mock_get.call_count == 2
    # Check that the second call uses proper path construction
    second_call_args = mock_get.call_args_list[1]
    assert "prompts/subdir/prompt1.md" in second_call_args[0][0] or "prompts/subdir" in str(
        second_call_args
    )
    # Verify result includes the file
    assert len(result) == 1
    assert result[0] == ("prompt1.md", "# Prompt 1\nContent")
