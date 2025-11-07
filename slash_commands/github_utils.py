"""GitHub API utilities for downloading prompts from repositories."""

from __future__ import annotations

import base64
from pathlib import Path

import requests


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


def download_prompts_from_github(
    owner: str, repo: str, branch: str, path: str
) -> list[tuple[str, str]]:
    """Download markdown prompt files from a GitHub repository.

    Args:
        owner: Repository owner
        repo: Repository name
        branch: Branch name (e.g., "main", "refactor/improve-workflow")
        path: Path to prompts directory or single prompt file within repository

    Returns:
        List of tuples (filename, content) for each markdown file found

    Raises:
        requests.exceptions.HTTPError: For GitHub API errors (404, 403, etc.)
        requests.exceptions.RequestException: For network errors
        ValueError: If path points to a single file that is not a markdown file
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {"Accept": "application/vnd.github+json"}
    params = {"ref": branch}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        # Check status code from the response if available
        if hasattr(e.response, "status_code"):
            if e.response.status_code == 404:
                raise requests.exceptions.HTTPError(
                    f"Repository, branch, or path not found: {owner}/{repo}@{branch}/{path}. "
                    "Please verify the repository exists, the branch name is correct, and the path is valid."
                ) from e
            elif e.response.status_code == 403:
                raise requests.exceptions.HTTPError(
                    f"Access forbidden (403) for {owner}/{repo}. "
                    "This may be due to rate limiting or the repository may be private. "
                    "Only public repositories are supported."
                ) from e
        raise
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            f"Network error while accessing GitHub API: {e}. "
            "Please check your internet connection and try again."
        ) from e

    # Handle non-JSON responses (e.g., HTML error pages)
    try:
        data = response.json()
    except ValueError as e:
        raise ValueError(
            f"Invalid response from GitHub API (expected JSON, got {response.headers.get('Content-Type', 'unknown')}). "
            f"Status code: {response.status_code}"
        ) from e

    # Check if path points to a single file
    if isinstance(data, dict):
        if data.get("type") == "file":
            filename = Path(data["name"]).name
            if not filename.endswith(".md"):
                raise ValueError(
                    f"File at path '{path}' must be a markdown file (.md), got: {filename}"
                )
            content = base64.b64decode(data["content"]).decode("utf-8")
            return [(filename, content)]
        # If it's a dict but not a file, treat as error
        return []

    # Handle directory response (array)
    if isinstance(data, list):
        prompts = []
        for item in data:
            if item.get("type") == "file" and item["name"].endswith(".md"):
                filename = Path(item["name"]).name
                content = base64.b64decode(item["content"]).decode("utf-8")
                prompts.append((filename, content))
        return prompts

    # Unexpected response format
    return []


def _download_github_prompts_to_temp_dir(
    owner: str, repo: str, branch: str, path: str, temp_dir: Path
) -> None:
    """Download GitHub prompts to a temporary directory.

    Args:
        owner: Repository owner
        repo: Repository name
        branch: Branch name
        path: Path to prompts directory or single prompt file
        temp_dir: Temporary directory path where files will be written

    Raises:
        requests.exceptions.HTTPError: For GitHub API errors
        requests.exceptions.RequestException: For network errors
        ValueError: If path points to a non-markdown file
    """
    prompts = download_prompts_from_github(owner, repo, branch, path)
    for filename, content in prompts:
        file_path = temp_dir / filename
        file_path.write_text(content, encoding="utf-8")
