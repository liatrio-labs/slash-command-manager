"""GitHub API utilities for downloading prompts from repositories."""

from __future__ import annotations


def validate_github_repo(repo: str) -> tuple[str, str]:
    """Validate GitHub repository format and return owner and repo name.

    Args:
        repo: Repository string in format "owner/repo"

    Returns:
        Tuple of (owner, repo)

    Raises:
        ValueError: If repository format is invalid, with helpful error message
            including example format.
    """
    if not repo:
        raise ValueError(
            "Repository must be in format owner/repo, got: (empty string). "
            "Example: liatrio-labs/spec-driven-workflow"
        )

    parts = repo.split("/")
    if len(parts) != 2:
        raise ValueError(
            f"Repository must be in format owner/repo, got: {repo}. "
            "Example: liatrio-labs/spec-driven-workflow"
        )

    owner, repo_name = parts
    if not owner or not repo_name:
        raise ValueError(
            f"Repository must be in format owner/repo, got: {repo}. "
            "Example: liatrio-labs/spec-driven-workflow"
        )

    return (owner, repo_name)
