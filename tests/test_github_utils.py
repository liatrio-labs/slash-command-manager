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
    assert validate_github_repo("owner/repo") == ("owner", "repo")
    assert validate_github_repo("liatrio-labs/spec-driven-workflow") == (
        "liatrio-labs",
        "spec-driven-workflow",
    )
    assert validate_github_repo("user-name/repo-name") == ("user-name", "repo-name")
    assert validate_github_repo("org/repo") == ("org", "repo")


def test_validate_github_repo_invalid_format():
    """Test that validate_github_repo rejects invalid repository formats."""
    # Missing slash
    with pytest.raises(ValueError, match="Repository must be in format owner/repo"):
        validate_github_repo("invalid-format")

    # Too many slashes
    with pytest.raises(ValueError, match="Repository must be in format owner/repo"):
        validate_github_repo("owner/repo/extra")

    # Empty string
    with pytest.raises(ValueError, match="Repository cannot be empty"):
        validate_github_repo("")

    # Only owner, no repo
    with pytest.raises(ValueError, match="Repository must be in format owner/repo"):
        validate_github_repo("owner")

    # Only slash, no owner or repo
    with pytest.raises(ValueError, match="Repository must be in format owner/repo"):
        validate_github_repo("/")

    # Owner empty
    with pytest.raises(ValueError, match="Repository must be in format owner/repo"):
        validate_github_repo("/repo")

    # Repo empty
    with pytest.raises(ValueError, match="Repository must be in format owner/repo"):
        validate_github_repo("owner/")


def test_validate_github_repo_error_message_includes_example():
    """Test that error messages include helpful examples."""
    with pytest.raises(ValueError) as exc_info:
        validate_github_repo("invalid-format")
    assert "liatrio-labs/spec-driven-workflow" in str(exc_info.value)
    assert "Example:" in str(exc_info.value)


@patch("slash_commands.github_utils.requests.get")
def test_download_prompts_from_github_directory(mock_get):
    """Test downloading prompts from a GitHub directory."""
    # Mock directory response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            "type": "file",
            "name": "prompt1.md",
            "content": base64.b64encode(b"# Prompt 1\nContent 1").decode("utf-8"),
        },
        {
            "type": "file",
            "name": "prompt2.md",
            "content": base64.b64encode(b"# Prompt 2\nContent 2").decode("utf-8"),
        },
        {"type": "file", "name": "not-markdown.txt", "content": "ignored"},
        {"type": "dir", "name": "subdir", "path": "prompts/subdir"},
    ]
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    prompts = download_prompts_from_github("owner", "repo", "main", "prompts")

    assert len(prompts) == 2
    assert ("prompt1.md", "# Prompt 1\nContent 1") in prompts
    assert ("prompt2.md", "# Prompt 2\nContent 2") in prompts

    # Verify API call
    mock_get.assert_called_once()
    call_args = mock_get.call_args
    assert "application/vnd.github+json" in call_args[1]["headers"]["Accept"]
    assert call_args[1]["params"]["ref"] == "main"


@patch("slash_commands.github_utils.requests.get")
def test_download_prompts_from_github_single_file(mock_get):
    """Test downloading a single prompt file from GitHub."""
    # Mock single file response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "type": "file",
        "name": "generate-spec.md",
        "content": base64.b64encode(b"# Generate Spec\nContent").decode("utf-8"),
    }
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    prompts = download_prompts_from_github("owner", "repo", "main", "prompts/generate-spec.md")

    assert len(prompts) == 1
    assert prompts[0][0] == "generate-spec.md"
    assert prompts[0][1] == "# Generate Spec\nContent"


@patch("slash_commands.github_utils.requests.get")
def test_download_prompts_from_github_single_file_non_markdown(mock_get):
    """Test that non-markdown single file raises ValueError."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "type": "file",
        "name": "file.txt",
        "content": base64.b64encode(b"content").decode("utf-8"),
    }
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    with pytest.raises(ValueError, match="File must have .md extension"):
        download_prompts_from_github("owner", "repo", "main", "prompts/file.txt")


@patch("slash_commands.github_utils.requests.get")
def test_download_prompts_from_github_empty_directory(mock_get):
    """Test that empty directory returns empty list without error."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"type": "file", "name": "not-markdown.txt", "content": "ignored"},
        {"type": "dir", "name": "subdir", "path": "prompts/subdir"},
    ]
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    prompts = download_prompts_from_github("owner", "repo", "main", "prompts")

    assert prompts == []


@patch("slash_commands.github_utils.requests.get")
def test_download_prompts_from_github_filters_subdirectories(mock_get):
    """Test that subdirectories are not recursively processed."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            "type": "file",
            "name": "prompt.md",
            "content": base64.b64encode(b"# Prompt").decode("utf-8"),
        },
        {"type": "dir", "name": "subdir", "path": "prompts/subdir"},
    ]
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    prompts = download_prompts_from_github("owner", "repo", "main", "prompts")

    assert len(prompts) == 1
    assert prompts[0][0] == "prompt.md"


@patch("slash_commands.github_utils.requests.get")
def test_download_prompts_from_github_404_error(mock_get):
    """Test that 404 error produces helpful error message."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        response=mock_response
    )
    mock_get.return_value = mock_response

    with pytest.raises(requests.exceptions.HTTPError) as exc_info:
        download_prompts_from_github("owner", "repo", "main", "nonexistent")

    assert "not found" in str(exc_info.value).lower()
    assert "owner/repo" in str(exc_info.value)


@patch("slash_commands.github_utils.requests.get")
def test_download_prompts_from_github_403_error(mock_get):
    """Test that 403 error produces helpful error message."""
    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        response=mock_response
    )
    mock_get.return_value = mock_response

    with pytest.raises(requests.exceptions.HTTPError) as exc_info:
        download_prompts_from_github("owner", "repo", "main", "prompts")

    assert "403" in str(exc_info.value) or "forbidden" in str(exc_info.value).lower()
    assert "rate limiting" in str(exc_info.value).lower() or "public" in str(exc_info.value).lower()


@patch("slash_commands.github_utils.requests.get")
def test_download_prompts_from_github_network_error(mock_get):
    """Test that network errors produce helpful error message."""
    mock_get.side_effect = requests.exceptions.RequestException("Connection timeout")

    with pytest.raises(requests.exceptions.RequestException) as exc_info:
        download_prompts_from_github("owner", "repo", "main", "prompts")

    assert "Network error" in str(exc_info.value) or "network" in str(exc_info.value).lower()


@patch("slash_commands.github_utils.requests.get")
def test_download_prompts_from_github_non_json_response(mock_get):
    """Test that non-JSON responses are handled gracefully."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("Not JSON")
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    with pytest.raises(requests.exceptions.HTTPError) as exc_info:
        download_prompts_from_github("owner", "repo", "main", "prompts")

    assert (
        "non-json" in str(exc_info.value).lower()
        or "non-json response" in str(exc_info.value).lower()
    )


@patch("slash_commands.github_utils.download_prompts_from_github")
def test_download_github_prompts_to_temp_dir(mock_download, tmp_path):
    """Test that prompts are downloaded and written to temp directory."""
    mock_download.return_value = [
        ("prompt1.md", "# Prompt 1\nContent 1"),
        ("prompt2.md", "# Prompt 2\nContent 2"),
    ]

    _download_github_prompts_to_temp_dir(tmp_path, "owner", "repo", "main", "prompts")

    assert (tmp_path / "prompt1.md").exists()
    assert (tmp_path / "prompt2.md").exists()
    assert (tmp_path / "prompt1.md").read_text() == "# Prompt 1\nContent 1"
    assert (tmp_path / "prompt2.md").read_text() == "# Prompt 2\nContent 2"
