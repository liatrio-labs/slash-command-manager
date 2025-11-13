"""GitHub API utilities for downloading prompts from repositories."""

from __future__ import annotations

import base64
from pathlib import Path

import requests


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


def download_prompts_from_github(
    owner: str, repo: str, branch: str, path: str
) -> list[tuple[str, str]]:
    """Download markdown prompt files from a GitHub repository.

    Args:
        owner: Repository owner
        repo: Repository name
        branch: Branch name (e.g., 'main', 'refactor/improve-workflow')
        path: Path to directory or single file within repository

    Returns:
        List of (filename, content) tuples for markdown files

    Raises:
        requests.exceptions.HTTPError: For GitHub API errors (404, 403, etc.)
        requests.exceptions.RequestException: For network errors
        ValueError: If path points to a non-markdown file
    """
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {"Accept": "application/vnd.github+json"}
    params = {"ref": branch}

    try:
        response = requests.get(api_url, headers=headers, params=params, timeout=30)
        response.raise_for_status()

        # Handle non-JSON responses (e.g., HTML error pages)
        try:
            data = response.json()
        except ValueError as e:
            raise requests.exceptions.HTTPError(
                f"GitHub API returned non-JSON response: {response.status_code}"
            ) from e

        prompts = []

        # Check if path points to a single file or directory
        if isinstance(data, dict):
            # Single file response
            if not path.endswith(".md"):
                raise ValueError(
                    f"File must have .md extension, got: {path}. Only markdown files are supported."
                )

            filename = Path(path).name
            content_encoded = data.get("content", "")
            if not content_encoded:
                return []

            # Decode base64 content
            try:
                content = base64.b64decode(content_encoded).decode("utf-8")
            except Exception as e:
                raise ValueError(f"Failed to decode file content: {e}") from e

            prompts.append((filename, content))

        elif isinstance(data, list):
            # Directory response - filter for .md files only in immediate directory
            for item in data:
                if item.get("type") == "file" and item.get("name", "").endswith(".md"):
                    filename = item["name"]
                    content_encoded = item.get("content", "")
                    if not content_encoded:
                        continue

                    # Decode base64 content
                    try:
                        content = base64.b64decode(content_encoded).decode("utf-8")
                    except Exception:
                        # Skip files that can't be decoded
                        continue

                    prompts.append((filename, content))
                # Skip subdirectories (do not recursively process)

        return prompts

    except requests.exceptions.HTTPError as e:
        # Provide helpful error messages for common errors
        if e.response is not None:
            status_code = e.response.status_code
            if status_code == 404:
                raise requests.exceptions.HTTPError(
                    f"Repository, branch, or path not found: {owner}/{repo}@{branch}/{path}. "
                    "Verify the repository exists, branch name is correct, and path is valid."
                ) from e
            if status_code == 403:
                raise requests.exceptions.HTTPError(
                    f"Access forbidden (403) for {owner}/{repo}. "
                    "This may be due to rate limiting or repository access restrictions. "
                    "Ensure the repository is public."
                ) from e
        raise
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            f"Network error while accessing GitHub API: {e}. "
            "Check your internet connection and try again."
        ) from e


def _download_github_prompts_to_temp_dir(
    temp_dir: Path, owner: str, repo: str, branch: str, path: str
) -> None:
    """Download GitHub prompts to a temporary directory.

    Args:
        temp_dir: Temporary directory to write files to
        owner: Repository owner
        repo: Repository name
        branch: Branch name
        path: Path to directory or single file within repository

    Raises:
        requests.exceptions.HTTPError: For GitHub API errors
        requests.exceptions.RequestException: For network errors
        ValueError: If path points to a non-markdown file
    """
    prompts = download_prompts_from_github(owner, repo, branch, path)

    for filename, content in prompts:
        file_path = temp_dir / filename
        file_path.write_text(content, encoding="utf-8")
