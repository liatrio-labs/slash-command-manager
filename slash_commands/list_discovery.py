"""Prompt discovery and filtering logic for list command."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path
from typing import Any

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from mcp_server.prompt_utils import parse_frontmatter
from slash_commands.cli_utils import format_source_info
from slash_commands.config import AgentConfig, get_agent_config

# Panel width matching generate command summary
LIST_PANEL_WIDTH = 80


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
            except (
                yaml.YAMLError,
                tomllib.TOMLDecodeError,
                UnicodeDecodeError,
                PermissionError,
                FileNotFoundError,
            ):
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
    # Strict validation: exactly 8 digits, hyphen, 6 digits
    if not re.match(r"^\d{8}-\d{6}$", timestamp):
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
    except (UnicodeDecodeError, PermissionError, FileNotFoundError):
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
        raw_meta = frontmatter.get("meta") or {}
        if not isinstance(raw_meta, dict):
            # Treat files with non-mapping meta as invalid prompts
            return None
        meta = raw_meta

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

        raw_meta = data.get("meta") or {}
        if not isinstance(raw_meta, dict):
            # Treat files with non-table meta as invalid prompts
            return None
        meta = raw_meta

        # Extract name from meta.source_prompt (where generator stores it) or use filename
        name = meta.get("source_prompt") or file_path.stem

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
            except (
                yaml.YAMLError,
                tomllib.TOMLDecodeError,
                UnicodeDecodeError,
                PermissionError,
                FileNotFoundError,
            ):
                # Skip invalid/malformed files silently per spec assumption
                continue

        unmanaged_counts[agent_key] = count

    return unmanaged_counts


def count_backups(file_path: Path) -> int:
    """Count backup files for a given command file.

    Counts files matching pattern: {filename}.{extension}.{timestamp}.bak
    where timestamp format is YYYYMMDD-HHMMSS.

    Args:
        file_path: Path to the command file

    Returns:
        Number of backup files found
    """
    if not file_path.exists():
        return 0

    # Get directory and base filename
    directory = file_path.parent
    base_name = file_path.stem
    extension = file_path.suffix

    # Pattern: filename.{extension}.YYYYMMDD-HHMMSS.bak
    # Escape the extension for regex
    escaped_ext = re.escape(extension)
    pattern = re.compile(rf"^{re.escape(base_name)}{escaped_ext}\.\d{{8}}-\d{{6}}\.bak$")

    count = 0
    # Look for files matching the pattern in the same directory
    for backup_file in directory.iterdir():
        if backup_file.is_file() and pattern.match(backup_file.name):
            count += 1

    return count


def build_list_data_structure(
    discovered_prompts: list[dict[str, Any]], unmanaged_counts: dict[str, int]
) -> dict[str, Any]:
    """Build structured data for list command output.

    Groups discovered prompts by name and aggregates agent information per prompt.

    Args:
        discovered_prompts: List of prompt dicts from discover_managed_prompts()
        unmanaged_counts: Dict mapping agent keys to unmanaged prompt counts

    Returns:
        Dict with structure:
        {
            "prompts": {
                prompt_name: {
                    "name": str,
                    "agents": [
                        {
                            "agent": str,
                            "display_name": str,
                            "file_path": Path,
                            "backup_count": int
                        }
                    ],
                    "source_info": str,
                    "updated_at": str
                }
            },
            "unmanaged_counts": {agent_key: int}
        }
    """
    prompts_dict: dict[str, dict[str, Any]] = {}

    # Group prompts by name
    for prompt in discovered_prompts:
        name = prompt["name"]
        if name not in prompts_dict:
            prompts_dict[name] = {
                "name": name,
                "agents": [],
                "source_info": format_source_info(prompt["meta"]),
                "updated_at": prompt["meta"].get("updated_at", "Unknown"),
            }

        # Add agent information
        agent_info = {
            "agent": prompt["agent"],
            "display_name": prompt["agent_display_name"],
            "file_path": prompt["file_path"],
            "backup_count": count_backups(prompt["file_path"]),
        }
        prompts_dict[name]["agents"].append(agent_info)

    return {
        "prompts": prompts_dict,
        "unmanaged_counts": unmanaged_counts,
    }


def classify_file_type(file_path: Path, agent: AgentConfig) -> str:
    """Classify a file by type based on its content and metadata.

    Classifies files as:
    - "managed": Files with `meta.managed_by == "slash-man"`
    - "unmanaged": Valid prompt files without `managed_by` metadata
    - "backup": Files matching backup pattern `*.{extension}.{timestamp}.bak`
    - "other": Invalid/malformed files or files that don't match above categories

    Args:
        file_path: Path to the file to classify
        agent: Agent configuration

    Returns:
        Classification string: "managed", "unmanaged", "backup", or "other"
    """
    # Check if it's a backup file first
    if _is_backup_file(file_path):
        return "backup"

    # Try to parse the file
    try:
        prompt_data = _parse_command_file(file_path, agent)
        if prompt_data:
            # Check if it's managed
            if prompt_data.get("meta", {}).get("managed_by") == "slash-man":
                return "managed"
            # Valid prompt file but not managed
            return "unmanaged"
    except (
        yaml.YAMLError,
        tomllib.TOMLDecodeError,
        UnicodeDecodeError,
        PermissionError,
        FileNotFoundError,
    ):
        # Parsing error - classify as "other"
        pass

    # Invalid/malformed file or parsing failed
    return "other"


def discover_all_files(base_path: Path, agents: list[str]) -> dict[str, Any]:
    """Discover all files in agent command directories and classify them.

    Scans all files matching `command_file_extension` pattern for each agent,
    including backup files, classifies each file by type (managed, unmanaged,
    backup, other), and returns file information along with directory status.

    Args:
        base_path: Base directory for searching agent command directories
        agents: List of agent keys to search (e.g., ["cursor", "claude-code"])

    Returns:
        Dict containing:
        - files: List of dicts, each containing:
          - file_path: Absolute path to file (Path)
          - type: Classification string ("managed", "unmanaged", "backup", "other")
          - agent: Agent key (str)
          - agent_display_name: Agent display name (str)
        - directory_status: Dict mapping agent keys to {"exists": bool}
    """
    discovered: list[dict[str, Any]] = []
    directory_status: dict[str, dict[str, bool]] = {}

    for agent_key in agents:
        agent = get_agent_config(agent_key)
        command_dir = base_path / agent.command_dir

        # Track directory existence status for each agent
        directory_exists = command_dir.exists()
        directory_status[agent_key] = {"exists": directory_exists}

        if not directory_exists:
            # Directory doesn't exist - continue to next agent
            continue

        # Track files we've already processed to avoid duplicates
        processed_files: set[Path] = set()

        # Scan for all files matching agent's command_file_extension
        for file_path in command_dir.glob(f"*{agent.command_file_extension}"):
            if file_path not in processed_files:
                file_type = classify_file_type(file_path, agent)
                discovered.append(
                    {
                        "file_path": file_path,
                        "type": file_type,
                        "agent": agent.key,
                        "agent_display_name": agent.display_name,
                    }
                )
                processed_files.add(file_path)

        # Also scan for backup files (pattern: *{extension}.{timestamp}.bak)
        escaped_ext = re.escape(agent.command_file_extension)
        backup_pattern = re.compile(rf".*{escaped_ext}\.\d{{8}}-\d{{6}}\.bak$")
        for file_path in command_dir.iterdir():
            if file_path.is_file() and backup_pattern.match(file_path.name):
                if file_path not in processed_files:
                    file_type = classify_file_type(file_path, agent)
                    discovered.append(
                        {
                            "file_path": file_path,
                            "type": file_type,
                            "agent": agent.key,
                            "agent_display_name": agent.display_name,
                        }
                    )
                    processed_files.add(file_path)

    return {"files": discovered, "directory_status": directory_status}


def _build_agent_summary_panel(
    agent: AgentConfig,
    files: list[dict[str, Any]],
    target_path: Path,
    *,
    directory_exists: bool = True,
) -> Panel:
    """Build Rich Panel with agent summary information.

    Shows agent display name, agent key, command directory path (relative to target_path),
    total file count, and breakdown by type. Handles empty and missing directories.

    Args:
        agent: Agent configuration
        files: List of file dicts for this agent
        target_path: Base path for relative path calculation
        directory_exists: Whether the command directory exists

    Returns:
        Rich Panel with summary information
    """
    # Get command directory path relative to target_path
    command_dir = target_path / agent.command_dir
    from slash_commands.cli_utils import relative_to_candidates

    relative_dir = relative_to_candidates(str(command_dir), [target_path])

    # Build summary text
    summary_lines = [
        f"Agent: {agent.display_name} ({agent.key})",
        f"Directory: {relative_dir}",
    ]

    # Handle empty or missing directory
    if not directory_exists:
        summary_lines.append("")
        summary_lines.append("Directory does not exist")
    elif len(files) == 0:
        summary_lines.append("")
        summary_lines.append("No files found")
    else:
        # Count files by type
        type_counts: dict[str, int] = {"managed": 0, "unmanaged": 0, "backup": 0, "other": 0}
        for file_info in files:
            file_type = file_info.get("type", "other")
            if file_type in type_counts:
                type_counts[file_type] += 1

        total_files = len(files)

        summary_lines.append(f"Total Files: {total_files}")
        summary_lines.append("")
        summary_lines.append("Breakdown:")
        summary_lines.append(f"  Managed: {type_counts['managed']}")
        summary_lines.append(f"  Unmanaged: {type_counts['unmanaged']}")
        summary_lines.append(f"  Backup: {type_counts['backup']}")
        summary_lines.append(f"  Other: {type_counts['other']}")

    summary_text = "\n".join(summary_lines)

    return Panel(
        summary_text,
        title=f"{agent.display_name} Summary",
        border_style="cyan",
        width=LIST_PANEL_WIDTH,
        expand=False,
    )


def _build_agent_file_table(files: list[dict[str, Any]], target_path: Path) -> Table:
    """Build Rich Table for a single agent's files.

    Creates a table with "Type" and "File Path" columns, sorted by type
    (managed, unmanaged, backup, other) then alphabetically by filename.
    Applies color coding: green for managed, red for unmanaged/other, default for backup.

    Args:
        files: List of file dicts for this agent
        target_path: Base path for relative path calculation

    Returns:
        Rich Table with file information
    """
    from slash_commands.cli_utils import relative_to_candidates

    # Create table
    table = Table(show_header=True, header_style="bold cyan", width=LIST_PANEL_WIDTH)
    table.add_column("Type", style="cyan", width=12)
    table.add_column("File Path", style="white", overflow="fold")

    # Define sort order for types
    type_order = {"managed": 0, "unmanaged": 1, "backup": 2, "other": 3}

    # Sort files: first by type order, then alphabetically by filename
    def sort_key(file_info: dict[str, Any]) -> tuple[int, str]:
        file_type = file_info.get("type", "other")
        type_rank = type_order.get(file_type, 3)
        file_path = file_info.get("file_path", Path())
        filename = file_path.name
        return (type_rank, filename.lower())

    sorted_files = sorted(files, key=sort_key)

    # Add rows to table with color coding
    for file_info in sorted_files:
        file_type = file_info.get("type", "other")
        file_path = file_info.get("file_path", Path())

        # Get relative path
        relative_path = relative_to_candidates(str(file_path), [target_path])

        # Determine color based on type
        if file_type == "managed":
            type_style = "green"
            path_style = "green"
        elif file_type in ("unmanaged", "other"):
            type_style = "red"
            path_style = "red"
        else:  # backup
            type_style = None  # Default color
            path_style = None  # Default color

        # Add row with appropriate styling
        type_text = (
            Text(file_type.capitalize(), style=type_style) if type_style else file_type.capitalize()
        )
        path_text = Text(relative_path, style=path_style) if path_style else relative_path

        table.add_row(type_text, path_text)

    return table


def render_all_files_tables(
    files_by_agent: dict[str, list[dict[str, Any]]],
    target_path: Path,
    *,
    record: bool = False,
    directory_status: dict[str, dict[str, bool]] | None = None,
) -> str | None:
    """Render all files in Rich table format organized by agent.

    Creates a summary panel and table for each agent, displaying files
    with proper sorting and color coding. Handles empty directories and
    missing directories with appropriate messages.

    Args:
        files_by_agent: Dict mapping agent keys to lists of file dicts
        target_path: Base path for relative path calculation
        record: If True, record output and return as string instead of printing
        directory_status: Dict mapping agent keys to {"exists": bool} for directory status

    Returns:
        Rendered text if record=True, None otherwise
    """
    target_console = (
        Console(record=True, width=LIST_PANEL_WIDTH) if record else Console(width=LIST_PANEL_WIDTH)
    )

    # Show informational note about file extension filtering
    if files_by_agent:
        # Collect unique extensions for all agents being shown
        extensions = {
            get_agent_config(agent_key).command_file_extension
            for agent_key in files_by_agent.keys()
        }
        if len(extensions) == 1:
            ext_text = f"*{extensions.pop()} pattern"
        else:
            ext_text = f"expected extension patterns ({', '.join(f'*{ext}' for ext in sorted(extensions))})"
        extension_note = f"[dim]Note: Only files matching the {ext_text} are shown.[/dim]"
        target_console.print(extension_note)
        target_console.print()

    # Process each agent
    for agent_key in sorted(files_by_agent.keys()):
        files = files_by_agent[agent_key]
        agent = get_agent_config(agent_key)

        # Check directory status
        directory_exists = True
        if directory_status and agent_key in directory_status:
            directory_exists = directory_status[agent_key].get("exists", True)

        # Build and print summary panel (handles empty state)
        summary_panel = _build_agent_summary_panel(
            agent, files, target_path, directory_exists=directory_exists
        )
        target_console.print(summary_panel)

        # Build and print file table (only if files exist)
        if files:
            file_table = _build_agent_file_table(files, target_path)
            target_console.print(file_table)

        # Add spacing between agents
        target_console.print()

    if record:
        return target_console.export_text(clear=False)
    return None


def render_list_tree(data_structure: dict[str, Any], *, record: bool = False) -> str | None:
    """Render the list data structure using Rich Tree format.

    Similar to `_render_rich_summary()` in cli.py, but organized by prompt name.

    Args:
        data_structure: Dict from build_list_data_structure() containing prompts and unmanaged_counts
        record: If True, record output and return as string instead of printing

    Returns:
        Rendered text if record=True, None otherwise
    """
    target_console = (
        Console(record=True, width=LIST_PANEL_WIDTH) if record else Console(width=LIST_PANEL_WIDTH)
    )

    root = Tree("Managed Prompts")

    prompts = data_structure.get("prompts", {})
    unmanaged_counts = data_structure.get("unmanaged_counts", {})

    # Add prompts grouped by name
    if prompts:
        prompts_branch = root.add("Prompts")
        for prompt_name, prompt_data in sorted(prompts.items()):
            prompt_branch = prompts_branch.add(prompt_name)

            # Add source info
            source_info = prompt_data.get("source_info", "Unknown")
            prompt_branch.add(f"Source: {source_info}")

            # Add updated timestamp
            updated_at = prompt_data.get("updated_at", "Unknown")
            prompt_branch.add(f"Updated: {updated_at}")

            # Add agents
            agents = prompt_data.get("agents", [])
            if agents:
                agents_branch = prompt_branch.add(f"Agents ({len(agents)})")
                for agent_info in agents:
                    agent_key = agent_info.get("agent", "unknown")
                    display_name = agent_info.get("display_name", agent_key)
                    file_path = agent_info.get("file_path", Path())
                    backup_count = agent_info.get("backup_count", 0)

                    # Format agent entry: "Display Name (agent-key) • X backup(s)"
                    backup_text = f"{backup_count} backup" + ("s" if backup_count != 1 else "")
                    agent_entry = f"{display_name} ({agent_key}) • {backup_text}"

                    agent_node = agents_branch.add(agent_entry)
                    # Add file path as child
                    agent_node.add(Text(str(file_path), overflow="fold"))
            else:
                prompt_branch.add("No agents")
    else:
        root.add("No managed prompts found")

    # Add unmanaged counts
    if unmanaged_counts:
        unmanaged_branch = root.add("Unmanaged Prompts")
        for agent_key, count in sorted(unmanaged_counts.items()):
            if count > 0:
                unmanaged_branch.add(f"{agent_key}: {count}")

    panel = Panel(
        root,
        title="List Summary",
        border_style="cyan",
        width=LIST_PANEL_WIDTH,
        expand=False,
    )
    target_console.print(panel)

    if record:
        return target_console.export_text(clear=False)
    return None
