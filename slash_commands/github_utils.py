"""GitHub API utilities for downloading prompts from repositories."""

from __future__ import annotations

import base64
import logging
import re
from pathlib import Path, PurePosixPath
from urllib.parse import urljoin, urlparse

import requests

# GitHub allows alphanumeric, hyphens, underscores, and dots in owner/repo names
# This regex matches valid GitHub repository identifiers (no slashes)
_GITHUB_REPO_PATTERN = re.compile(r"^[a-zA-Z0-9._-]+$")

# Branch names can contain slashes (e.g., 'refactor/improve-workflow')
# This regex matches valid GitHub branch names
_GITHUB_BRANCH_PATTERN = re.compile(r"^[a-zA-Z0-9._/\-]+$")


def _validate_github_identifier(identifier: str, name: str) -> None:
    """Validate a GitHub identifier (owner, repo) contains only safe characters.

    Args:
        identifier: The identifier to validate
        name: Human-readable name for error messages (e.g., 'owner', 'repo')

    Raises:
        ValueError: If identifier contains invalid characters
    """
    if not identifier:
        raise ValueError(f"{name} cannot be empty")
    if not _GITHUB_REPO_PATTERN.match(identifier):
        raise ValueError(
            f"{name} contains invalid characters. "
            f"Only alphanumeric characters, dots, hyphens, and underscores are allowed. "
            f"Got: {identifier!r}"
        )


def _validate_github_branch(branch: str) -> None:
    """Validate a GitHub branch name contains only safe characters.

    Args:
        branch: The branch name to validate

    Raises:
        ValueError: If branch contains invalid characters
    """
    if not branch:
        raise ValueError("Branch cannot be empty")
    if not _GITHUB_BRANCH_PATTERN.match(branch):
        raise ValueError(
            "Branch contains invalid characters. "
            "Only alphanumeric characters, dots, slashes, hyphens, and underscores are allowed. "
            f"Got: {branch!r}"
        )


def _validate_github_path(path: str) -> None:
    """Validate a GitHub repository path doesn't contain path traversal or unsafe characters.

    Args:
        path: The path to validate

    Raises:
        ValueError: If path contains traversal sequences or unsafe characters
    """
    if not path:
        raise ValueError("Path cannot be empty")

    # Check for path traversal sequences
    normalized_path = PurePosixPath(path)
    if ".." in normalized_path.parts:
        raise ValueError(f"Path cannot contain traversal segments (..). Got: {path!r}")

    # Check for absolute paths
    if normalized_path.is_absolute():
        raise ValueError(f"Path must be relative, got absolute path: {path!r}")

    # Check for unsafe characters that could be exploited in URL construction
    # Allow alphanumeric, dots, slashes, hyphens, underscores, and spaces
    if not re.match(r"^[a-zA-Z0-9._/\s-]+$", path):
        raise ValueError(
            f"Path contains invalid characters. "
            f"Only alphanumeric characters, dots, slashes, hyphens, underscores, and spaces are allowed. "
            f"Got: {path!r}"
        )


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

    # Validate owner and repo contain only safe characters
    _validate_github_identifier(owner, "Owner")
    _validate_github_identifier(repo_name, "Repository")

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
        ValueError: If path points to a non-markdown file or contains invalid characters
    """
    # Validate all inputs to prevent SSRF attacks
    _validate_github_identifier(owner, "Owner")
    _validate_github_identifier(repo, "Repository")
    _validate_github_branch(branch)
    _validate_github_path(path)

    # Construct URL safely to prevent SSRF
    # All inputs are validated above, so we can safely construct the URL
    # Use urljoin with a fixed base URL to ensure we only target api.github.com
    base_url = "https://api.github.com/"
    # Construct path segments - owner and repo are validated, so safe to use
    repo_segment = f"repos/{owner}/{repo}/contents/"
    # Use urljoin to safely combine base URL with repo segment
    api_url = urljoin(base_url, repo_segment)
    # Append path - path is validated, so safe to append
    # Ensure trailing slash for proper urljoin behavior
    if not api_url.endswith("/"):
        api_url += "/"
    api_url = urljoin(api_url, path)

    # Validate the final URL to ensure it only targets api.github.com
    # This is a defense-in-depth measure to prevent SSRF attacks
    parsed_url = urlparse(api_url)
    if parsed_url.scheme != "https":
        raise ValueError(f"API URL must use HTTPS scheme, got: {parsed_url.scheme}")
    if parsed_url.netloc != "api.github.com":
        raise ValueError(f"API URL must target api.github.com, got: {parsed_url.netloc}")

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

                    if content_encoded:
                        # Single file requests include base64-encoded content
                        try:
                            content = base64.b64decode(content_encoded).decode("utf-8")
                            prompts.append((filename, content))
                        except Exception:
                            # Skip files that can't be decoded
                            continue
                    else:
                        # Directory listings don't include content, use download_url
                        download_url = item.get("download_url")
                        file_path = item.get("path")

                        if not download_url or not file_path:
                            continue

                        # Validate original download_url for safety (defense in depth)
                        _validate_raw_github_download_url(download_url)

                        # Preserve original download_url for error logging
                        original_download_url = download_url

                        # Validate and normalize file_path before constructing URL
                        try:
                            normalized_file_path = _validate_and_normalize_file_path(file_path)
                        except ValueError as e:
                            # Log warning and skip this file (matches decode/download error handling)
                            logger = logging.getLogger(__name__)
                            logger.warning(
                                f"Skipping {filename}: Invalid file path: {e}. "
                                f"Original download_url: {original_download_url}"
                            )
                            continue

                        # Construct URL from known components instead of parsing
                        # This handles branches with slashes correctly and avoids parsing bugs
                        try:
                            download_url = _construct_raw_github_url(
                                owner, repo, branch, normalized_file_path
                            )
                        except ValueError as e:
                            # Log warning and skip this file (matches decode/download error handling)
                            logger = logging.getLogger(__name__)
                            logger.warning(
                                f"Skipping {filename}: Failed to construct download URL: {e}. "
                                f"Original download_url: {original_download_url}"
                            )
                            continue

                        try:
                            # Fetch file content from download_url
                            file_response = requests.get(download_url, timeout=30)
                            file_response.raise_for_status()
                            content = file_response.text
                            prompts.append((filename, content))
                        except requests.exceptions.RequestException:
                            # Skip files that can't be downloaded
                            continue
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


def _validate_raw_github_download_url(download_url: str) -> None:
    """Ensure download URLs only target raw.githubusercontent.com over HTTPS."""
    parsed = urlparse(download_url)

    if parsed.scheme != "https":
        raise ValueError(f"GitHub download URLs must use HTTPS, got scheme: {parsed.scheme}")

    if parsed.netloc != "raw.githubusercontent.com":
        raise ValueError(
            f"GitHub download URLs must use host raw.githubusercontent.com, got: {parsed.netloc}"
        )

    normalized_path = PurePosixPath(parsed.path)
    if ".." in normalized_path.parts:
        raise ValueError(
            f"GitHub download URL path cannot contain traversal segments: {parsed.path}"
        )


def _validate_and_normalize_file_path(file_path: str) -> str:
    """Validate and normalize a file path from GitHub API.

    This function ensures file paths are safe before being used to construct URLs.
    It validates against path traversal, absolute paths, null bytes, and suspicious characters.

    Args:
        file_path: File path from GitHub API (may have leading slash)

    Returns:
        Normalized file path (leading slashes removed, validated)

    Raises:
        ValueError: If path is invalid (empty, absolute, contains traversal, null bytes, etc.)
    """
    if not file_path:
        raise ValueError("File path cannot be empty")

    # Check for null bytes
    if "\x00" in file_path:
        raise ValueError("File path cannot contain null bytes")

    # Strip leading slashes first (GitHub API may return paths with leading slashes)
    clean_path = file_path.lstrip("/")

    # Ensure path is non-empty after normalization (check this first)
    if not clean_path:
        raise ValueError("File path cannot be empty after normalization")

    # Check for absolute paths - reject if it's a system path
    # After stripping leading slashes, check if original was a dangerous absolute path
    if file_path.startswith("/"):
        # Reject known system paths (defense against /etc/passwd, /usr/bin, etc.)
        first_segment = clean_path.split("/")[0]
        system_paths = {
            "etc",
            "usr",
            "var",
            "sys",
            "proc",
            "dev",
            "bin",
            "sbin",
            "lib",
            "lib64",
            "opt",
            "root",
            "home",
            "tmp",
        }
        if first_segment in system_paths:
            raise ValueError(f"File path cannot be absolute: {file_path}")

    # Normalize using PurePosixPath (after stripping leading slashes)
    normalized_path = PurePosixPath(clean_path)

    # Reject paths containing traversal segments
    if ".." in normalized_path.parts:
        raise ValueError(f"File path cannot contain traversal segments: {file_path}")

    # Validate allowed characters: letters, numbers, dots, dashes, underscores, slashes
    # This is a whitelist approach for security
    allowed_chars_pattern = re.compile(r"^[a-zA-Z0-9._/\-]+$")
    if not allowed_chars_pattern.match(clean_path):
        raise ValueError(
            f"File path contains invalid characters. "
            f"Only letters, numbers, dots, dashes, underscores, and slashes are allowed. "
            f"Got: {file_path!r}"
        )

    return clean_path


def _construct_raw_github_url(owner: str, repo: str, branch: str, file_path: str) -> str:
    """Construct a raw.githubusercontent.com URL from components.

    This function constructs URLs directly from known components instead of parsing
    existing URLs, which avoids issues with branch names containing slashes.

    Args:
        owner: Repository owner (already validated)
        repo: Repository name (already validated)
        branch: Branch name (will be validated)
        file_path: File path from GitHub API (relative, may have leading slash)
                   Should be validated with _validate_and_normalize_file_path first

    Returns:
        URL in format: https://raw.githubusercontent.com/owner/repo/branch/file_path

    Raises:
        ValueError: If branch is invalid (empty or contains invalid characters)
    """
    _validate_github_branch(branch)
    # Path should already be normalized, but strip leading slash as defense in depth
    clean_path = file_path.lstrip("/")
    return f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{clean_path}"


def _fix_branch_in_download_url(download_url: str, requested_branch: str) -> str:
    """Replace the branch name in a GitHub download URL with the requested branch.

    DEPRECATED: This function is deprecated in favor of _construct_raw_github_url()
    which constructs URLs from known components instead of parsing URLs.

    GitHub API may return download_url values pointing to the default branch (main)
    even when requesting a different branch. This function ensures the URL uses
    the correct branch name.

    Args:
        download_url: GitHub download URL in format
            https://raw.githubusercontent.com/owner/repo/branch/path/to/file.md
        requested_branch: The branch name that should be used in the URL

    Returns:
        URL with branch name replaced to match requested_branch

    Raises:
        ValueError: If URL format is unexpected

    Note:
        This function has a bug: it fails when the original download_url contains
        a branch name with slashes because it assumes the branch is always at
        path_parts[2]. Use _construct_raw_github_url() instead.
    """
    parsed = urlparse(download_url)

    # Validate URL structure
    if parsed.netloc != "raw.githubusercontent.com":
        raise ValueError(f"Expected raw.githubusercontent.com, got: {parsed.netloc}")

    # Parse path: /owner/repo/branch/path/to/file.md
    path_parts = parsed.path.strip("/").split("/")
    if len(path_parts) < 4:
        raise ValueError(
            f"Unexpected download URL format. Expected /owner/repo/branch/path, got: {parsed.path}"
        )

    # Replace branch (3rd element, index 2) with requested branch
    # path_parts = [owner, repo, branch, ...rest of path]
    path_parts[2] = requested_branch

    # Reconstruct URL
    new_path = "/" + "/".join(path_parts)
    return f"{parsed.scheme}://{parsed.netloc}{new_path}"


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
