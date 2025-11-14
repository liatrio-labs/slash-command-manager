"""Shared CLI utilities for generate and list commands."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any


def find_project_root() -> Path:
    """Find the project root directory using a robust strategy.

    Strategy:
    1. Check PROJECT_ROOT environment variable first
    2. Walk upward from Path.cwd() and Path(__file__) looking for marker files/directories
       (.git directory, pyproject.toml, setup.py)
    3. Fall back to Path.cwd() if no marker is found

    Returns:
        Resolved Path to the project root directory
    """
    # Check environment variable first
    env_root = os.getenv("PROJECT_ROOT")
    if env_root:
        return Path(env_root).resolve()

    # Marker files/directories that indicate a project root
    marker_files = [".git", "pyproject.toml", "setup.py"]

    # Start from current working directory and __file__ location
    start_paths = [Path.cwd(), Path(__file__).resolve().parent]

    for start_path in start_paths:
        current = start_path.resolve()
        # Walk upward looking for marker files
        for _ in range(10):  # Limit depth to prevent infinite loops
            # Check if any marker file exists in current directory
            if any((current / marker).exists() for marker in marker_files):
                return current
            # Stop at filesystem root
            parent = current.parent
            if parent == current:
                break
            current = parent

    # Fall back to current working directory
    return Path.cwd().resolve()


def display_local_path(path: Path) -> str:
    """Return a path relative to the current working directory or project root.

    Args:
        path: Path to display

    Returns:
        Relative path string if possible, otherwise absolute path string
    """
    resolved_path = path.resolve()
    candidates = [Path.cwd().resolve(), find_project_root()]
    for candidate in candidates:
        try:
            return str(resolved_path.relative_to(candidate))
        except ValueError:
            continue
    return str(resolved_path)


def relative_to_candidates(path_str: str, candidates: list[Path]) -> str:
    """Return a path relative to one of the candidate directories.

    Args:
        path_str: Path string to make relative
        candidates: List of candidate directories to try

    Returns:
        Relative path string if possible, otherwise original path string
    """
    file_path = Path(path_str)
    for candidate in candidates:
        try:
            return str(file_path.resolve().relative_to(candidate.resolve()))
        except (ValueError, FileNotFoundError):
            continue
    return str(file_path)


def format_source_info(meta: dict[str, Any]) -> str:
    """Format source metadata into a single display line.

    Consolidates source information from metadata:
    - Local sources: "local: /path/to/prompts" (uses source_dir or source_path)
    - GitHub sources: "github: owner/repo@branch:path"
    - Missing fields: "Unknown"

    Args:
        meta: Metadata dict from command file

    Returns:
        Formatted source information string
    """
    source_type = meta.get("source_type", "")

    if source_type == "local":
        # Prefer source_dir, fallback to source_path
        source_dir = meta.get("source_dir")
        if source_dir:
            return f"local: {source_dir}"
        source_path = meta.get("source_path")
        if source_path:
            return f"local: {source_path}"
        return "Unknown"

    if source_type == "github":
        source_repo = meta.get("source_repo")
        source_branch = meta.get("source_branch", "")
        source_path = meta.get("source_path", "")

        if source_repo:
            parts = [f"github: {source_repo}"]
            if source_branch:
                parts.append(f"@{source_branch}")
            if source_path:
                parts.append(f":{source_path}")
            return "".join(parts)
        return "Unknown"

    # Unknown or missing source_type
    return "Unknown"
