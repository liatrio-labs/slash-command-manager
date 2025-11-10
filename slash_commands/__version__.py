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
import tomllib
from importlib.metadata import version as get_package_version
from pathlib import Path


def _get_build_time_commit() -> str | None:
    """Get the git commit SHA that was embedded at build time."""
    try:
        # Try to import the build-time commit file
        from slash_commands._git_commit import __git_commit__

        return __git_commit__
    except ImportError:
        # Build-time commit file not available (development mode)
        return None


def _get_git_commit() -> str | None:
    """Get the short git commit SHA from the local repository."""
    # First try build-time commit
    build_commit = _get_build_time_commit()
    if build_commit:
        return build_commit

    # Fall back to runtime detection
    try:
        # Get the directory where this __version__.py file is located
        # Navigate up to find the repository root (where pyproject.toml is)
        version_file_path = Path(__file__).parent
        # Go up from slash_commands/ to the repo root
        repo_root = version_file_path.parent
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=repo_root,  # Always run from slash-command-manager directory
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Not in a git repository or git not available
        return None


def _get_version() -> str:
    """Get the version from pyproject.toml."""
    # Navigate up from slash_commands/__version__.py to find pyproject.toml
    version_file_path = Path(__file__).parent
    repo_root = version_file_path.parent
    pyproject_path = repo_root / "pyproject.toml"
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
