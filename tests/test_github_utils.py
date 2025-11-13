"""Tests for GitHub utilities."""

from __future__ import annotations

import pytest

from slash_commands.github_utils import validate_github_repo


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
