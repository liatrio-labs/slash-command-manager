"""Tests for GitHub utilities module."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from slash_commands.github_utils import (
    GitHubRepoError,
    download_github_prompts,
    get_github_repo_info,
    list_github_directory_files,
    parse_github_url,
)


def test_github_repo_error_creation():
    """Test that GitHubRepoError can be created with a message."""
    error = GitHubRepoError("Test error message")
    assert str(error) == "Test error message"
    assert error.args[0] == "Test error message"


def test_github_repo_error_inheritance():
    """Test that GitHubRepoError inherits from Exception."""
    error = GitHubRepoError("Test error")
    assert isinstance(error, Exception)
    assert isinstance(error, GitHubRepoError)


def test_github_repo_error_with_context():
    """Test that GitHubRepoError can include context information."""
    error = GitHubRepoError("Repository not found", repo="owner/repo", status=404)
    assert str(error) == "Repository not found"
    # The error should be able to store context if implemented
    # This test will fail initially until we add context support


def test_parse_github_url_valid_complete_url():
    """Test parsing a valid complete GitHub URL with tree/branch/path."""
    url = "https://github.com/liatrio-labs/spec-driven-workflow/tree/main/prompts"
    result = parse_github_url(url)
    expected = {
        "owner": "liatrio-labs",
        "repo": "spec-driven-workflow",
        "branch": "main",
        "path": "prompts",
    }
    assert result == expected


def test_parse_github_url_valid_nested_path():
    """Test parsing a valid GitHub URL with nested path."""
    url = "https://github.com/owner/repo/tree/develop/docs/prompts"
    result = parse_github_url(url)
    expected = {"owner": "owner", "repo": "repo", "branch": "develop", "path": "docs/prompts"}
    assert result == expected


def test_parse_github_url_valid_root_path():
    """Test parsing a valid GitHub URL with root path."""
    url = "https://github.com/owner/repo/tree/main/"
    result = parse_github_url(url)
    expected = {"owner": "owner", "repo": "repo", "branch": "main", "path": ""}
    assert result == expected


def test_parse_github_url_invalid_missing_tree():
    """Test that URL without tree/branch raises error."""
    url = "https://github.com/owner/repo/blob/main/file.md"
    with pytest.raises(GitHubRepoError, match="Invalid GitHub URL format"):
        parse_github_url(url)


def test_parse_github_url_invalid_not_github():
    """Test that non-GitHub URL raises error."""
    url = "https://gitlab.com/owner/repo/tree/main/prompts"
    with pytest.raises(GitHubRepoError, match="Invalid GitHub URL format"):
        parse_github_url(url)


def test_parse_github_url_invalid_malformed():
    """Test that malformed URL raises error."""
    url = "not-a-url"
    with pytest.raises(GitHubRepoError, match="Invalid GitHub URL format"):
        parse_github_url(url)


def test_parse_github_url_invalid_missing_components():
    """Test that URL with missing components raises error."""
    url = "https://github.com/owner/tree/main/prompts"
    with pytest.raises(GitHubRepoError, match="Invalid GitHub URL format"):
        parse_github_url(url)


# Tests for list_github_directory_files() function
def test_list_github_directory_files_success():
    """Test successful listing of GitHub directory files."""
    with patch("slash_commands.github_utils.requests.get") as mock_get:
        mock_get.return_value.json.return_value = [
            {
                "name": "prompt1.md",
                "type": "file",
                "download_url": "https://raw.githubusercontent.com/owner/repo/main/prompts/prompt1.md",
            },
            {
                "name": "prompt2.md",
                "type": "file",
                "download_url": "https://raw.githubusercontent.com/owner/repo/main/prompts/prompt2.md",
            },
            {
                "name": "README.txt",
                "type": "file",
                "download_url": "https://raw.githubusercontent.com/owner/repo/main/prompts/README.txt",
            },
        ]
        mock_get.return_value.raise_for_status.return_value = None

        result = list_github_directory_files("owner", "repo", "main", "prompts")

        expected = [
            {
                "name": "prompt1.md",
                "type": "file",
                "download_url": "https://raw.githubusercontent.com/owner/repo/main/prompts/prompt1.md",
            },
            {
                "name": "prompt2.md",
                "type": "file",
                "download_url": "https://raw.githubusercontent.com/owner/repo/main/prompts/prompt2.md",
            },
        ]
        assert result == expected


def test_list_github_directory_files_api_error():
    """Test handling of GitHub API errors."""
    with patch("slash_commands.github_utils.requests.get") as mock_get:
        mock_get.return_value.raise_for_status.side_effect = Exception("API Error")

        with pytest.raises(GitHubRepoError, match="Failed to list directory"):
            list_github_directory_files("owner", "repo", "main", "prompts")


# Tests for download_github_prompts() function
def test_download_github_prompts_success(tmp_path):
    """Test successful download of GitHub prompts."""
    mock_files = [
        {
            "name": "prompt1.md",
            "download_url": "https://raw.githubusercontent.com/owner/repo/main/prompts/prompt1.md",
        }
    ]

    with (
        patch("slash_commands.github_utils.list_github_directory_files") as mock_list,
        patch("slash_commands.github_utils.requests.get") as mock_get,
        patch("slash_commands.github_utils.tempfile.mkdtemp") as mock_temp,
    ):
        mock_list.return_value = mock_files
        mock_temp.return_value = str(tmp_path)
        mock_get.return_value.text = "# Test Prompt\n\nThis is a test prompt."
        mock_get.return_value.raise_for_status.return_value = None

        result = download_github_prompts("owner", "repo", "main", "prompts")

        assert isinstance(result, Path)
        assert result.exists()
        assert (result / "prompt1.md").exists()


def test_download_github_prompts_network_timeout():
    """Test handling of network timeouts during download."""
    with (
        patch("slash_commands.github_utils.list_github_directory_files") as mock_list,
        patch("slash_commands.github_utils.requests.get") as mock_get,
    ):
        mock_list.return_value = [{"name": "prompt1.md", "download_url": "url"}]
        mock_get.return_value.raise_for_status.side_effect = TimeoutError("Timeout")

        with pytest.raises(GitHubRepoError, match="Network timeout"):
            download_github_prompts("owner", "repo", "main", "prompts")


# Tests for file size validation
def test_file_size_validation_large_file():
    """Test rejection of files larger than 1MB."""
    with (
        patch("slash_commands.github_utils.list_github_directory_files") as mock_list,
        patch("slash_commands.github_utils.requests.get") as mock_get,
        patch("slash_commands.github_utils.tempfile.mkdtemp") as mock_temp,
    ):
        mock_list.return_value = [{"name": "large.md", "download_url": "url"}]
        mock_get.return_value.headers = {"content-length": "2097152"}  # 2MB
        mock_temp.return_value = "/tmp/test"

        with pytest.raises(GitHubRepoError, match="File too large"):
            download_github_prompts("owner", "repo", "main", "prompts")


def test_file_size_validation_many_files_warning():
    """Test warning for repositories with more than 100 files."""
    mock_files = [{"name": f"prompt{i}.md", "download_url": f"url{i}"} for i in range(101)]

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

        mock_print.assert_any_call(
            "Warning: Repository contains 101 files, which may impact performance"
        )


# Tests for get_github_repo_info() function
def test_get_github_repo_info_success():
    """Test successful retrieval of GitHub repository info."""
    with patch("slash_commands.github_utils.requests.get") as mock_get:
        mock_get.return_value.json.return_value = {
            "name": "test-repo",
            "full_name": "owner/test-repo",
            "description": "Test repository",
            "default_branch": "main",
            "stargazers_count": 10,
            "forks_count": 5,
        }
        mock_get.return_value.raise_for_status.return_value = None

        result = get_github_repo_info("owner", "repo")

        expected = {
            "name": "test-repo",
            "full_name": "owner/test-repo",
            "description": "Test repository",
            "default_branch": "main",
            "stargazers_count": 10,
            "forks_count": 5,
        }
        assert result == expected


def test_get_github_repo_info_not_found():
    """Test handling of repository not found error."""
    with patch("slash_commands.github_utils.requests.get") as mock_get:
        mock_get.return_value.raise_for_status.side_effect = Exception("Not Found")

        with pytest.raises(GitHubRepoError, match="Repository not found"):
            get_github_repo_info("owner", "nonexistent")
