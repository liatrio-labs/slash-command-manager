"""Centralized version management for the project.

This module reads the version from pyproject.toml to ensure a single source of truth,
and includes git commit SHA when available for development debugging.

Version format:
- Development (git repo): "1.0.0+8b4e417"
- Production (installed): "1.0.0+def456" (from build-time file, matches release commit)
- Fallback: "1.0.0"

The commit SHA is determined in this order of priority:
1. Build-time injection (for installed packages, matches release commit)
2. Runtime git detection (for local development)
3. None (fallback)

This approach follows Python best practices by:
1. Using pyproject.toml as the single source of truth for version
2. Embedding git metadata at build time for production packages
3. Providing runtime detection for local development
4. Ensuring version SHA matches the release commit for traceability
"""

from __future__ import annotations

import subprocess
from importlib.metadata import version as get_package_version
from pathlib import Path

import tomllib


def _get_build_time_commit() -> str | None:
    """Get the git commit SHA that was embedded at build time."""
    try:
        # Try to import the build-time commit file
        from slash_commands._git_commit import __git_commit__

        return __git_commit__
    except ImportError:
        # Build-time commit file not available (development mode)
        return None


def _find_git_repo_root(start_path: Path) -> Path | None:
    """Find the git repository root by traversing up from start_path.

    Args:
        start_path: Starting directory to search from

    Returns:
        Path to git repository root (directory containing .git), or None if not found
    """
    current = start_path.resolve()
    while current != current.parent:
        # Prioritize finding .git directory (actual git repo)
        if (current / ".git").exists():
            return current
        # Only use pyproject.toml as indicator if we're likely in source (not installed)
        # Check if current directory looks like a project root (has both pyproject.toml and is likely source)
        if (current / "pyproject.toml").exists() and (current / ".git").exists():
            return current
        current = current.parent
    return None


def _get_git_commit() -> str | None:
    """Get the short git commit SHA from the local repository."""
    # First try build-time commit
    build_commit = _get_build_time_commit()
    if build_commit:
        return build_commit

    # Fall back to runtime detection
    try:
        # Find the git repository root by traversing up from __version__.py location
        # This works whether __version__.py is in source or installed location
        version_file_path = Path(__file__).parent
        git_repo_root = _find_git_repo_root(version_file_path)

        if git_repo_root is None:
            # If we can't find the repo root, try using git rev-parse --show-toplevel
            try:
                result = subprocess.run(
                    ["git", "rev-parse", "--show-toplevel"],
                    capture_output=True,
                    text=True,
                    check=True,
                    cwd=version_file_path,
                )
                git_repo_root = Path(result.stdout.strip())
            except subprocess.CalledProcessError:
                return None

        # Run git rev-parse from the repository root
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=git_repo_root,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Not in a git repository or git not available
        return None


def _get_version() -> str:
    """Get the version from pyproject.toml."""
    pyproject_path = Path(__file__).parent / "pyproject.toml"
    if pyproject_path.exists():
        # Local development mode
        with pyproject_path.open("rb") as f:
            data = tomllib.load(f)
            return data["project"]["version"]
    else:
        # Installed package mode
        return get_package_version("slash-command-manager")


def _get_version_with_commit() -> str:
    """Get version string including git commit SHA when available."""
    version = _get_version()
    commit = _get_git_commit()

    if commit:
        return f"{version}+{commit}"
    return version


__version__ = _get_version()
__version_with_commit__ = _get_version_with_commit()
