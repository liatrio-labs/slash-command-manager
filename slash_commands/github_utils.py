"""GitHub API utilities for downloading prompts from repositories."""

from __future__ import annotations


def validate_github_repo(repo: str) -> tuple[str, str]:
    """Validate GitHub repository format and return owner/repo tuple.

    Args:
        repo: Repository string in format 'owner/repo'

    Returns:
        Tuple of (owner, repo)

    Raises:
        ValueError: If repository format is invalid, with helpful error message
    """
    if not repo:
        raise ValueError(
            "Repository cannot be empty. "
            "Repository must be in format owner/repo, got: ''. "
            "Example: liatrio-labs/spec-driven-workflow"
        )

    parts = repo.split("/")
    if len(parts) != 2:
        example = "liatrio-labs/spec-driven-workflow"
        raise ValueError(
            f"Repository must be in format owner/repo, got: {repo!r}. Example: {example}"
        )

    owner, repo_name = parts

    if not owner or not repo_name:
        example = "liatrio-labs/spec-driven-workflow"
        raise ValueError(
            f"Repository must be in format owner/repo, got: {repo!r}. Example: {example}"
        )

    return (owner, repo_name)
