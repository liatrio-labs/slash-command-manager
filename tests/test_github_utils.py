"""Tests for GitHub utilities."""

from __future__ import annotations

import pytest

from slash_commands.github_utils import validate_github_repo


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
