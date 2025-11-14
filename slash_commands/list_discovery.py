"""Prompt discovery and filtering logic for list command."""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

import yaml

from mcp_server.prompt_utils import parse_frontmatter
from slash_commands.config import AgentConfig, get_agent_config


def discover_managed_prompts(base_path: Path, agents: list[str]) -> list[dict[str, Any]]:
    """Discover managed prompts across agent command directories.

    Scans agent command directories for files with `managed_by: slash-man` metadata.
    Handles both Markdown (frontmatter) and TOML formats.

    Args:
        base_path: Base directory for searching agent command directories
        agents: List of agent keys to search (e.g., ["cursor", "claude-code"])

    Returns:
        List of dicts, each containing:
        - name: Prompt name (str)
        - agent: Agent key (str)
        - agent_display_name: Agent display name (str)
        - file_path: Absolute path to command file (Path)
        - meta: Metadata dict from file (dict)
        - format: File format ("markdown" or "toml") (str)
    """
    discovered: list[dict[str, Any]] = []

    for agent_key in agents:
        agent = get_agent_config(agent_key)
        command_dir = base_path / agent.command_dir

        if not command_dir.exists():
            continue

        # Scan for files matching agent's command_file_extension
        for file_path in command_dir.glob(f"*{agent.command_file_extension}"):
            # Skip backup files (pattern: *.{extension}.{timestamp}.bak)
            if _is_backup_file(file_path):
                continue

            try:
                prompt_data = _parse_command_file(file_path, agent)
                if prompt_data and prompt_data.get("meta", {}).get("managed_by") == "slash-man":
                    discovered.append(prompt_data)
            except (yaml.YAMLError, tomllib.TOMLDecodeError, UnicodeDecodeError, PermissionError):
                # Skip malformed files silently per spec assumption
                continue

    return discovered


def _is_backup_file(file_path: Path) -> bool:
    """Check if file matches backup pattern: *.{extension}.{timestamp}.bak."""
    # Pattern: filename.{extension}.YYYYMMDD-HHMMSS.bak
    name = file_path.name
    if not name.endswith(".bak"):
        return False

    # Check for timestamp pattern: YYYYMMDD-HHMMSS
    parts = name.rsplit(".", 3)
    if len(parts) != 4:
        return False

    timestamp = parts[-2]
    if len(timestamp) != 15 or not timestamp.replace("-", "").isdigit():
        return False

    return True


def _parse_command_file(file_path: Path, agent: AgentConfig) -> dict[str, Any] | None:
    """Parse a command file and extract metadata.

    Args:
        file_path: Path to command file
        agent: Agent configuration

    Returns:
        Dict with prompt data or None if parsing fails
    """
    try:
        content = file_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError):
        return None

    if agent.command_format.value == "markdown":
        return _parse_markdown_file(file_path, content, agent)
    elif agent.command_format.value == "toml":
        return _parse_toml_file(file_path, content, agent)
    else:
        return None


def _parse_markdown_file(
    file_path: Path, content: str, agent: AgentConfig
) -> dict[str, Any] | None:
    """Parse Markdown command file with frontmatter."""
    try:
        frontmatter, _body = parse_frontmatter(content)
        if not frontmatter:
            return None

        name = frontmatter.get("name") or file_path.stem
        meta = frontmatter.get("meta") or {}

        return {
            "name": name,
            "agent": agent.key,
            "agent_display_name": agent.display_name,
            "file_path": file_path,
            "meta": meta,
            "format": "markdown",
        }
    except yaml.YAMLError:
        return None


def _parse_toml_file(file_path: Path, content: str, agent: AgentConfig) -> dict[str, Any] | None:
    """Parse TOML command file."""
    try:
        data = tomllib.loads(content)
        if not isinstance(data, dict):
            return None

        # Extract name from prompt field or use filename
        name = data.get("prompt", "")
        if not name:
            name = file_path.stem
        else:
            # Extract name from prompt content or use filename
            name = file_path.stem

        meta = data.get("meta") or {}

        return {
            "name": name,
            "agent": agent.key,
            "agent_display_name": agent.display_name,
            "file_path": file_path,
            "meta": meta,
            "format": "toml",
        }
    except tomllib.TOMLDecodeError:
        return None


def count_unmanaged_prompts(base_path: Path, agents: list[str]) -> dict[str, int]:
    """Count unmanaged prompt files in agent command directories.

    Counts valid prompt files that don't have `managed_by: slash-man` metadata.
    Excludes backup files and managed files.

    Args:
        base_path: Base directory for searching agent command directories
        agents: List of agent keys to search

    Returns:
        Dict mapping agent keys to counts of unmanaged prompts
    """
    unmanaged_counts: dict[str, int] = {}

    for agent_key in agents:
        agent = get_agent_config(agent_key)
        command_dir = base_path / agent.command_dir

        if not command_dir.exists():
            unmanaged_counts[agent_key] = 0
            continue

        count = 0
        # Scan for files matching agent's command_file_extension
        for file_path in command_dir.glob(f"*{agent.command_file_extension}"):
            # Skip backup files
            if _is_backup_file(file_path):
                continue

            # Attempt to parse as valid prompt file
            try:
                prompt_data = _parse_command_file(file_path, agent)
                # If parsing succeeds, check if it's managed
                if prompt_data:
                    # Skip managed files
                    if prompt_data.get("meta", {}).get("managed_by") == "slash-man":
                        continue
                    # Valid prompt file without managed_by - count it
                    count += 1
            except (yaml.YAMLError, tomllib.TOMLDecodeError, UnicodeDecodeError, PermissionError):
                # Skip invalid/malformed files silently per spec assumption
                continue

        unmanaged_counts[agent_key] = count

    return unmanaged_counts
