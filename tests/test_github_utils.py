"""Tests for GitHub utilities."""

from __future__ import annotations

import base64
from unittest.mock import MagicMock, patch

import pytest
import requests

from slash_commands.github_utils import (
    _construct_raw_github_url,
    _download_github_prompts_to_temp_dir,
    _fix_branch_in_download_url,
    _validate_and_normalize_file_path,
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


def test_validate_github_repo_rejects_invalid_characters():
    """Test that validate_github_repo rejects invalid characters in owner/repo."""
    # Owner with invalid characters
    with pytest.raises(ValueError, match="invalid characters"):
        validate_github_repo("owner@evil/repo")
    with pytest.raises(ValueError, match="invalid characters"):
        validate_github_repo("owner space/repo")
    with pytest.raises(ValueError, match="invalid characters"):
        validate_github_repo("owner/repo#tag")

    # Valid characters should still work
    assert validate_github_repo("owner-name/repo.name") == ("owner-name", "repo.name")
    assert validate_github_repo("owner_name/repo_name") == ("owner_name", "repo_name")


def test_validate_and_normalize_file_path_valid_paths():
    """Test that _validate_and_normalize_file_path accepts valid file paths."""
    assert _validate_and_normalize_file_path("prompts/prompt.md") == "prompts/prompt.md"
    assert _validate_and_normalize_file_path("/prompts/prompt.md") == "prompts/prompt.md"
    assert _validate_and_normalize_file_path("prompt.md") == "prompt.md"
    assert (
        _validate_and_normalize_file_path("prompts/subdir/prompt.md") == "prompts/subdir/prompt.md"
    )
    assert _validate_and_normalize_file_path("prompt-name.md") == "prompt-name.md"
    assert _validate_and_normalize_file_path("prompt_name.md") == "prompt_name.md"
    assert _validate_and_normalize_file_path("prompt.name.md") == "prompt.name.md"


def test_validate_and_normalize_file_path_rejects_empty():
    """Test that _validate_and_normalize_file_path rejects empty paths."""
    with pytest.raises(ValueError, match="cannot be empty"):
        _validate_and_normalize_file_path("")
    with pytest.raises(ValueError, match="cannot be empty"):
        _validate_and_normalize_file_path("/")
    with pytest.raises(ValueError, match="cannot be empty"):
        _validate_and_normalize_file_path("///")


def test_validate_and_normalize_file_path_rejects_absolute():
    """Test that _validate_and_normalize_file_path rejects dangerous absolute paths."""
    # Reject system paths
    with pytest.raises(ValueError, match="cannot be absolute"):
        _validate_and_normalize_file_path("/etc/passwd")
    with pytest.raises(ValueError, match="cannot be absolute"):
        _validate_and_normalize_file_path("/usr/bin/script")
    with pytest.raises(ValueError, match="cannot be absolute"):
        _validate_and_normalize_file_path("/var/log/file")


def test_validate_and_normalize_file_path_rejects_traversal():
    """Test that _validate_and_normalize_file_path rejects path traversal."""
    with pytest.raises(ValueError, match="cannot contain traversal"):
        _validate_and_normalize_file_path("../prompt.md")
    with pytest.raises(ValueError, match="cannot contain traversal"):
        _validate_and_normalize_file_path("prompts/../../etc/passwd")
    with pytest.raises(ValueError, match="cannot contain traversal"):
        _validate_and_normalize_file_path("prompts/../other/prompt.md")


def test_validate_and_normalize_file_path_rejects_null_bytes():
    """Test that _validate_and_normalize_file_path rejects null bytes."""
    with pytest.raises(ValueError, match="cannot contain null bytes"):
        _validate_and_normalize_file_path("prompt\x00.md")
    with pytest.raises(ValueError, match="cannot contain null bytes"):
        _validate_and_normalize_file_path("prompts/\x00prompt.md")


def test_validate_and_normalize_file_path_rejects_invalid_characters():
    """Test that _validate_and_normalize_file_path rejects invalid characters."""
    with pytest.raises(ValueError, match="invalid characters"):
        _validate_and_normalize_file_path("prompt@evil.md")
    with pytest.raises(ValueError, match="invalid characters"):
        _validate_and_normalize_file_path("prompt space.md")
    with pytest.raises(ValueError, match="invalid characters"):
        _validate_and_normalize_file_path("prompt#tag.md")
    with pytest.raises(ValueError, match="invalid characters"):
        _validate_and_normalize_file_path("prompt$var.md")
    with pytest.raises(ValueError, match="invalid characters"):
        _validate_and_normalize_file_path("prompt<script>.md")


@patch("slash_commands.github_utils.requests.get")
def test_download_prompts_from_github_rejects_invalid_owner(mock_get):
    """Test that invalid owner characters are rejected."""
    with pytest.raises(ValueError, match="invalid characters"):
        download_prompts_from_github("owner@evil", "repo", "main", "prompts")
    with pytest.raises(ValueError, match="invalid characters"):
        download_prompts_from_github("owner space", "repo", "main", "prompts")


@patch("slash_commands.github_utils.requests.get")
def test_download_prompts_from_github_rejects_invalid_repo(mock_get):
    """Test that invalid repo characters are rejected."""
    with pytest.raises(ValueError, match="invalid characters"):
        download_prompts_from_github("owner", "repo@evil", "main", "prompts")
    with pytest.raises(ValueError, match="invalid characters"):
        download_prompts_from_github("owner", "repo space", "main", "prompts")


@patch("slash_commands.github_utils.requests.get")
def test_download_prompts_from_github_rejects_invalid_branch(mock_get):
    """Test that invalid branch characters are rejected."""
    with pytest.raises(ValueError, match="invalid characters"):
        download_prompts_from_github("owner", "repo", "branch@evil", "prompts")
    # But slashes should be allowed in branch names
    directory_response = MagicMock()
    directory_response.status_code = 200
    directory_response.json.return_value = []
    directory_response.raise_for_status = MagicMock()
    mock_get.return_value = directory_response
    # This should not raise a validation error
    download_prompts_from_github("owner", "repo", "feature/add-feature", "prompts")


@patch("slash_commands.github_utils.requests.get")
def test_download_prompts_from_github_rejects_path_traversal(mock_get):
    """Test that path traversal sequences are rejected."""
    with pytest.raises(ValueError, match="traversal"):
        download_prompts_from_github("owner", "repo", "main", "../etc/passwd")
    with pytest.raises(ValueError, match="traversal"):
        download_prompts_from_github("owner", "repo", "main", "prompts/../../etc")


@patch("slash_commands.github_utils.requests.get")
def test_download_prompts_from_github_rejects_absolute_path(mock_get):
    """Test that absolute paths are rejected."""
    with pytest.raises(ValueError, match="relative"):
        download_prompts_from_github("owner", "repo", "main", "/etc/passwd")


@patch("slash_commands.github_utils.requests.get")
def test_download_prompts_from_github_directory(mock_get):
    """Test downloading prompts from a GitHub directory."""
    # Mock directory response (real API behavior: no content field, has download_url)
    directory_response = MagicMock()
    directory_response.status_code = 200
    directory_response.json.return_value = [
        {
            "type": "file",
            "name": "prompt1.md",
            "path": "prompts/prompt1.md",
            "download_url": "https://raw.githubusercontent.com/owner/repo/main/prompts/prompt1.md",
            "size": 100,
        },
        {
            "type": "file",
            "name": "prompt2.md",
            "path": "prompts/prompt2.md",
            "download_url": "https://raw.githubusercontent.com/owner/repo/main/prompts/prompt2.md",
            "size": 100,
        },
        {
            "type": "file",
            "name": "not-markdown.txt",
            "path": "prompts/not-markdown.txt",
            "download_url": "https://raw.githubusercontent.com/owner/repo/main/prompts/not-markdown.txt",
            "size": 50,
        },
        {"type": "dir", "name": "subdir", "path": "prompts/subdir"},
    ]
    directory_response.raise_for_status = MagicMock()

    # Mock file download responses
    file1_response = MagicMock()
    file1_response.status_code = 200
    file1_response.text = "# Prompt 1\nContent 1"
    file1_response.raise_for_status = MagicMock()

    file2_response = MagicMock()
    file2_response.status_code = 200
    file2_response.text = "# Prompt 2\nContent 2"
    file2_response.raise_for_status = MagicMock()

    # Setup mock to return directory response first, then file responses
    mock_get.side_effect = [
        directory_response,  # Directory listing
        file1_response,  # prompt1.md download
        file2_response,  # prompt2.md download
    ]

    prompts = download_prompts_from_github("owner", "repo", "main", "prompts")

    assert len(prompts) == 2
    assert ("prompt1.md", "# Prompt 1\nContent 1") in prompts
    assert ("prompt2.md", "# Prompt 2\nContent 2") in prompts

    # Verify API calls: 1 for directory + 2 for files
    assert mock_get.call_count == 3
    # First call: directory listing
    call_args = mock_get.call_args_list[0]
    assert "application/vnd.github+json" in call_args[1]["headers"]["Accept"]
    assert call_args[1]["params"]["ref"] == "main"
    assert "contents/prompts" in call_args[0][0]
    # Second and third calls: file downloads via download_url
    assert "raw.githubusercontent.com" in mock_get.call_args_list[1][0][0]
    assert "raw.githubusercontent.com" in mock_get.call_args_list[2][0][0]


@patch("slash_commands.github_utils.requests.get")
def test_download_prompts_from_github_directory_rejects_non_raw_host(mock_get):
    """Ensure download URLs must point to raw.githubusercontent.com."""
    directory_response = MagicMock()
    directory_response.status_code = 200
    directory_response.json.return_value = [
        {
            "type": "file",
            "name": "prompt1.md",
            "path": "prompts/prompt1.md",
            "download_url": "https://evil.com/raw.githubusercontent.com/owner/repo/main/prompts/prompt1.md",
            "size": 100,
        }
    ]
    directory_response.raise_for_status = MagicMock()

    def fake_get(url, *args, **kwargs):
        if "contents/prompts" in url:
            return directory_response
        pytest.fail(f"Unexpected download attempt to {url}")

    mock_get.side_effect = fake_get

    with pytest.raises(ValueError, match="raw\\.githubusercontent\\.com"):
        download_prompts_from_github("owner", "repo", "main", "prompts")


@patch("slash_commands.github_utils.requests.get")
def test_download_prompts_from_github_directory_rejects_non_https(mock_get):
    """Ensure download URLs must use HTTPS."""
    directory_response = MagicMock()
    directory_response.status_code = 200
    directory_response.json.return_value = [
        {
            "type": "file",
            "name": "prompt1.md",
            "path": "prompts/prompt1.md",
            "download_url": "http://raw.githubusercontent.com/owner/repo/main/prompts/prompt1.md",
            "size": 100,
        }
    ]
    directory_response.raise_for_status = MagicMock()

    def fake_get(url, *args, **kwargs):
        if "contents/prompts" in url:
            return directory_response
        pytest.fail(f"Unexpected download attempt to {url}")

    mock_get.side_effect = fake_get

    with pytest.raises(ValueError, match="HTTPS"):
        download_prompts_from_github("owner", "repo", "main", "prompts")


@patch("slash_commands.github_utils.requests.get")
def test_download_prompts_from_github_directory_fixes_branch_in_download_url(mock_get):
    """Test that download_url branch is corrected when requesting non-default branch.

    This test reproduces the bug where GitHub API returns download_url values
    pointing to the default branch (main) even when requesting a different branch.
    The code should replace the branch name in download_url with the requested branch.
    """
    # Request a non-main branch
    requested_branch = "damien-test"

    # Mock directory response with download_url pointing to wrong branch (main)
    # This simulates the bug where GitHub returns main branch URLs even when
    # requesting a different branch
    directory_response = MagicMock()
    directory_response.status_code = 200
    directory_response.json.return_value = [
        {
            "type": "file",
            "name": "generate_spec.md",
            "path": "prompts/generate_spec.md",
            # download_url incorrectly points to 'main' branch
            "download_url": "https://raw.githubusercontent.com/owner/repo/main/prompts/generate_spec.md",
            "size": 100,
        }
    ]
    directory_response.raise_for_status = MagicMock()

    # Mock file download response with content from the correct branch
    file_response = MagicMock()
    file_response.status_code = 200
    file_response.text = "THIS IS A TEST"
    file_response.raise_for_status = MagicMock()

    # Track the URLs that are actually requested
    requested_urls = []

    def capture_urls(url, *args, **kwargs):
        requested_urls.append(url)
        if "contents/prompts" in url:
            return directory_response
        elif url.startswith("https://raw.githubusercontent.com/"):
            return file_response
        pytest.fail(f"Unexpected URL: {url}")

    mock_get.side_effect = capture_urls

    prompts = download_prompts_from_github("owner", "repo", requested_branch, "prompts")

    # Verify correct content was downloaded
    assert len(prompts) == 1
    assert prompts[0][0] == "generate_spec.md"
    assert prompts[0][1] == "THIS IS A TEST"

    # Verify API calls: 1 for directory + 1 for file
    assert mock_get.call_count == 2

    # Verify directory listing was requested with correct branch
    directory_call = mock_get.call_args_list[0]
    assert directory_call[1]["params"]["ref"] == requested_branch
    assert "contents/prompts" in directory_call[0][0]

    # Verify file download URL was corrected to use requested branch
    file_download_url = mock_get.call_args_list[1][0][0]
    assert file_download_url.startswith("https://raw.githubusercontent.com/")
    assert f"/{requested_branch}/" in file_download_url
    assert "/main/" not in file_download_url


@patch("slash_commands.github_utils.requests.get")
def test_download_prompts_from_github_directory_handles_branch_with_slash(mock_get):
    """Test that branch names with slashes are correctly handled in download URLs."""
    # Request a branch with a slash (e.g., feature/add-feature)
    requested_branch = "feature/add-feature"

    directory_response = MagicMock()
    directory_response.status_code = 200
    directory_response.json.return_value = [
        {
            "type": "file",
            "name": "prompt.md",
            "path": "prompts/prompt.md",
            # download_url incorrectly points to 'main' branch
            "download_url": "https://raw.githubusercontent.com/owner/repo/main/prompts/prompt.md",
            "size": 100,
        }
    ]
    directory_response.raise_for_status = MagicMock()

    file_response = MagicMock()
    file_response.status_code = 200
    file_response.text = "Content from feature branch"
    file_response.raise_for_status = MagicMock()

    mock_get.side_effect = [directory_response, file_response]

    prompts = download_prompts_from_github("owner", "repo", requested_branch, "prompts")

    assert len(prompts) == 1
    assert prompts[0][1] == "Content from feature branch"

    # Verify file download URL was corrected to use requested branch with slash
    file_download_url = mock_get.call_args_list[1][0][0]
    assert f"/{requested_branch}/" in file_download_url
    assert "/main/" not in file_download_url


@patch("slash_commands.github_utils.requests.get")
def test_download_prompts_from_github_directory_preserves_correct_branch(mock_get):
    """Test that download_url with correct branch is not modified."""
    # Request main branch
    requested_branch = "main"

    directory_response = MagicMock()
    directory_response.status_code = 200
    directory_response.json.return_value = [
        {
            "type": "file",
            "name": "prompt.md",
            "path": "prompts/prompt.md",
            # download_url correctly points to 'main' branch
            "download_url": "https://raw.githubusercontent.com/owner/repo/main/prompts/prompt.md",
            "size": 100,
        }
    ]
    directory_response.raise_for_status = MagicMock()

    file_response = MagicMock()
    file_response.status_code = 200
    file_response.text = "Content from main"
    file_response.raise_for_status = MagicMock()

    mock_get.side_effect = [directory_response, file_response]

    prompts = download_prompts_from_github("owner", "repo", requested_branch, "prompts")

    assert len(prompts) == 1
    # Verify URL still contains main branch (should be preserved)
    file_download_url = mock_get.call_args_list[1][0][0]
    assert "/main/" in file_download_url


def test_fix_branch_in_download_url_replaces_branch():
    """Test that _fix_branch_in_download_url correctly replaces branch name."""
    download_url = "https://raw.githubusercontent.com/owner/repo/main/prompts/file.md"
    requested_branch = "damien-test"

    fixed_url = _fix_branch_in_download_url(download_url, requested_branch)

    assert fixed_url == "https://raw.githubusercontent.com/owner/repo/damien-test/prompts/file.md"
    assert "/main/" not in fixed_url
    assert f"/{requested_branch}/" in fixed_url


def test_fix_branch_in_download_url_handles_branch_with_slash():
    """Test that _fix_branch_in_download_url handles branch names with slashes."""
    download_url = "https://raw.githubusercontent.com/owner/repo/main/prompts/file.md"
    requested_branch = "feature/add-feature"

    fixed_url = _fix_branch_in_download_url(download_url, requested_branch)

    assert (
        fixed_url
        == "https://raw.githubusercontent.com/owner/repo/feature/add-feature/prompts/file.md"
    )
    assert "/main/" not in fixed_url
    assert f"/{requested_branch}/" in fixed_url


def test_fix_branch_in_download_url_preserves_path():
    """Test that _fix_branch_in_download_url preserves the full file path."""
    download_url = "https://raw.githubusercontent.com/owner/repo/main/path/to/nested/file.md"
    requested_branch = "test-branch"

    fixed_url = _fix_branch_in_download_url(download_url, requested_branch)

    assert (
        fixed_url
        == "https://raw.githubusercontent.com/owner/repo/test-branch/path/to/nested/file.md"
    )
    assert "/path/to/nested/file.md" in fixed_url


def test_fix_branch_in_download_url_rejects_invalid_host():
    """Test that _fix_branch_in_download_url rejects non-GitHub URLs."""
    download_url = "https://evil.com/owner/repo/main/file.md"

    with pytest.raises(ValueError, match="raw\\.githubusercontent\\.com"):
        _fix_branch_in_download_url(download_url, "test-branch")


# Tests for _construct_raw_github_url (new function)


def test_construct_raw_github_url_basic():
    """Test that _construct_raw_github_url constructs URLs correctly."""
    url = _construct_raw_github_url("owner", "repo", "main", "path/to/file.md")
    assert url == "https://raw.githubusercontent.com/owner/repo/main/path/to/file.md"


def test_construct_raw_github_url_with_leading_slash():
    """Test that _construct_raw_github_url handles paths with leading slashes."""
    url = _construct_raw_github_url("owner", "repo", "main", "/path/to/file.md")
    assert url == "https://raw.githubusercontent.com/owner/repo/main/path/to/file.md"


def test_construct_raw_github_url_with_branch_containing_slash():
    """Test that _construct_raw_github_url handles branch names with slashes."""
    url = _construct_raw_github_url("owner", "repo", "feature/add-feature", "path/to/file.md")
    assert url == "https://raw.githubusercontent.com/owner/repo/feature/add-feature/path/to/file.md"


def test_construct_raw_github_url_with_nested_path():
    """Test that _construct_raw_github_url handles deeply nested paths."""
    url = _construct_raw_github_url("owner", "repo", "main", "very/deeply/nested/path/to/file.md")
    assert (
        url
        == "https://raw.githubusercontent.com/owner/repo/main/very/deeply/nested/path/to/file.md"
    )


def test_construct_raw_github_url_rejects_empty_branch():
    """Test that _construct_raw_github_url rejects empty branch names."""
    with pytest.raises(ValueError, match="Branch cannot be empty"):
        _construct_raw_github_url("owner", "repo", "", "path/to/file.md")


def test_construct_raw_github_url_rejects_invalid_branch():
    """Test that _construct_raw_github_url rejects invalid branch characters."""
    with pytest.raises(ValueError, match="invalid characters"):
        _construct_raw_github_url("owner", "repo", "branch@evil", "path/to/file.md")


# Tests for edge cases in download_prompts_from_github


@patch("slash_commands.github_utils.requests.get")
def test_download_prompts_from_github_missing_path_field(mock_get):
    """Test that download_prompts_from_github skips files with missing path field."""
    directory_response = MagicMock()
    directory_response.status_code = 200
    directory_response.json.return_value = [
        {
            "type": "file",
            "name": "prompt.md",
            # Missing "path" field
            "download_url": "https://raw.githubusercontent.com/owner/repo/main/prompts/prompt.md",
            "size": 100,
        }
    ]
    directory_response.raise_for_status = MagicMock()
    mock_get.return_value = directory_response

    prompts = download_prompts_from_github("owner", "repo", "main", "prompts")

    # File should be skipped because path is missing
    assert len(prompts) == 0
    # Should only call directory listing, not file download
    assert mock_get.call_count == 1


@patch("slash_commands.github_utils.requests.get")
def test_download_prompts_from_github_empty_path_field(mock_get):
    """Test that download_prompts_from_github skips files with empty path field."""
    directory_response = MagicMock()
    directory_response.status_code = 200
    directory_response.json.return_value = [
        {
            "type": "file",
            "name": "prompt.md",
            "path": "",  # Empty path
            "download_url": "https://raw.githubusercontent.com/owner/repo/main/prompts/prompt.md",
            "size": 100,
        }
    ]
    directory_response.raise_for_status = MagicMock()
    mock_get.return_value = directory_response

    prompts = download_prompts_from_github("owner", "repo", "main", "prompts")

    # File should be skipped because path is empty
    assert len(prompts) == 0
    # Should only call directory listing, not file download
    assert mock_get.call_count == 1


@patch("slash_commands.github_utils.requests.get")
def test_download_prompts_from_github_handles_original_url_with_branch_slash(mock_get):
    """Test that download works when original download_url has branch with slashes.

    This tests the fix for Issue 1: when GitHub returns a download_url with a branch
    containing slashes, we should still construct the correct URL using the path field.
    """
    requested_branch = "feature/add-feature"

    directory_response = MagicMock()
    directory_response.status_code = 200
    directory_response.json.return_value = [
        {
            "type": "file",
            "name": "prompt.md",
            "path": "prompts/prompt.md",
            # Original URL has branch with slashes (simulating GitHub API behavior)
            "download_url": "https://raw.githubusercontent.com/owner/repo/feature/add-feature/prompts/prompt.md",
            "size": 100,
        }
    ]
    directory_response.raise_for_status = MagicMock()

    file_response = MagicMock()
    file_response.status_code = 200
    file_response.text = "Content from feature branch"
    file_response.raise_for_status = MagicMock()

    mock_get.side_effect = [directory_response, file_response]

    prompts = download_prompts_from_github("owner", "repo", requested_branch, "prompts")

    assert len(prompts) == 1
    assert prompts[0][1] == "Content from feature branch"

    # Verify file download URL was constructed correctly (not parsed from original)
    file_download_url = mock_get.call_args_list[1][0][0]
    assert (
        file_download_url
        == "https://raw.githubusercontent.com/owner/repo/feature/add-feature/prompts/prompt.md"
    )
    assert f"/{requested_branch}/" in file_download_url


@patch("slash_commands.github_utils.requests.get")
@patch("slash_commands.github_utils._construct_raw_github_url")
def test_download_prompts_from_github_handles_url_construction_error(
    mock_construct_url, mock_get, caplog
):
    """Test that download_prompts_from_github handles URL construction errors gracefully.

    This tests that when URL construction fails, the file is skipped and an error is logged,
    allowing processing to continue with other files.
    """
    directory_response = MagicMock()
    directory_response.status_code = 200
    directory_response.json.return_value = [
        {
            "type": "file",
            "name": "prompt1.md",
            "path": "prompts/prompt1.md",
            "download_url": "https://raw.githubusercontent.com/owner/repo/main/prompts/prompt1.md",
            "size": 100,
        },
        {
            "type": "file",
            "name": "prompt2.md",
            "path": "prompts/prompt2.md",
            "download_url": "https://raw.githubusercontent.com/owner/repo/main/prompts/prompt2.md",
            "size": 100,
        },
    ]
    directory_response.raise_for_status = MagicMock()

    file_response = MagicMock()
    file_response.status_code = 200
    file_response.text = "Content from prompt2"
    file_response.raise_for_status = MagicMock()

    # Mock _construct_raw_github_url to raise ValueError for first file, succeed for second
    def construct_url_side_effect(owner, repo, branch, file_path):
        if file_path == "prompts/prompt1.md":
            raise ValueError("Invalid branch format")
        return f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file_path}"

    mock_construct_url.side_effect = construct_url_side_effect
    mock_get.side_effect = [directory_response, file_response]

    # Process prompts - prompt1 should be skipped due to URL construction error
    prompts = download_prompts_from_github("owner", "repo", "main", "prompts")

    # Should only have prompt2, prompt1 was skipped
    assert len(prompts) == 1
    assert prompts[0][0] == "prompt2.md"
    assert prompts[0][1] == "Content from prompt2"

    # Verify error was logged for prompt1
    assert len(caplog.records) == 1
    assert "prompt1.md" in caplog.records[0].message
    assert "Failed to construct download URL" in caplog.records[0].message
    assert "Original download_url" in caplog.records[0].message
    assert caplog.records[0].levelname == "WARNING"


@patch("slash_commands.github_utils.requests.get")
def test_download_prompts_from_github_continues_on_missing_path(mock_get):
    """Test that download_prompts_from_github continues processing other files when one is missing path."""
    directory_response = MagicMock()
    directory_response.status_code = 200
    directory_response.json.return_value = [
        {
            "type": "file",
            "name": "prompt1.md",
            # Missing path field
            "download_url": "https://raw.githubusercontent.com/owner/repo/main/prompts/prompt1.md",
            "size": 100,
        },
        {
            "type": "file",
            "name": "prompt2.md",
            "path": "prompts/prompt2.md",
            "download_url": "https://raw.githubusercontent.com/owner/repo/main/prompts/prompt2.md",
            "size": 100,
        },
    ]
    directory_response.raise_for_status = MagicMock()

    file_response = MagicMock()
    file_response.status_code = 200
    file_response.text = "Content from prompt2"
    file_response.raise_for_status = MagicMock()

    mock_get.side_effect = [directory_response, file_response]

    prompts = download_prompts_from_github("owner", "repo", "main", "prompts")

    # Should only get prompt2.md (prompt1.md skipped due to missing path)
    assert len(prompts) == 1
    assert prompts[0][0] == "prompt2.md"
    assert prompts[0][1] == "Content from prompt2"


@patch("slash_commands.github_utils.requests.get")
def test_download_prompts_from_github_handles_path_with_leading_slash(mock_get):
    """Test that download_prompts_from_github handles paths with leading slashes."""
    directory_response = MagicMock()
    directory_response.status_code = 200
    directory_response.json.return_value = [
        {
            "type": "file",
            "name": "prompt.md",
            "path": "/prompts/prompt.md",  # Path with leading slash
            "download_url": "https://raw.githubusercontent.com/owner/repo/main/prompts/prompt.md",
            "size": 100,
        }
    ]
    directory_response.raise_for_status = MagicMock()

    file_response = MagicMock()
    file_response.status_code = 200
    file_response.text = "Content"
    file_response.raise_for_status = MagicMock()

    mock_get.side_effect = [directory_response, file_response]

    prompts = download_prompts_from_github("owner", "repo", "main", "prompts")

    assert len(prompts) == 1
    # Verify URL was constructed correctly (leading slash removed)
    file_download_url = mock_get.call_args_list[1][0][0]
    assert (
        file_download_url == "https://raw.githubusercontent.com/owner/repo/main/prompts/prompt.md"
    )
    assert not file_download_url.endswith("//prompts/prompt.md")  # No double slash


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
    directory_response = MagicMock()
    directory_response.status_code = 200
    directory_response.json.return_value = [
        {
            "type": "file",
            "name": "prompt.md",
            "path": "prompts/prompt.md",
            "download_url": "https://raw.githubusercontent.com/owner/repo/main/prompts/prompt.md",
            "size": 100,
        },
        {"type": "dir", "name": "subdir", "path": "prompts/subdir"},
    ]
    directory_response.raise_for_status = MagicMock()

    file_response = MagicMock()
    file_response.status_code = 200
    file_response.text = "# Prompt"
    file_response.raise_for_status = MagicMock()

    mock_get.side_effect = [directory_response, file_response]

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
