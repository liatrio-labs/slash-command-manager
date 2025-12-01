"""Typer CLI for generating slash commands."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Annotated, Any

import questionary
import requests
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from slash_commands import (
    NoPromptsDiscoveredError,
    SlashCommandWriter,
    detect_agents,
    get_agent_config,
    list_agent_keys,
)
from slash_commands.__version__ import __version_with_commit__
from slash_commands.github_utils import validate_github_repo

app = typer.Typer(
    name="slash-man",
    help="Manage slash commands for the spec-driven workflow in your AI assistants",
    rich_markup_mode="rich",
)


def version_callback_impl(value: bool) -> None:
    """Print version and exit."""
    if value:
        typer.echo(f"slash-man {__version_with_commit__}")
        raise typer.Exit()


@app.callback()
def version_callback(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-v",
            callback=version_callback_impl,
            is_eager=True,
            help="Show version and exit",
        ),
    ] = False,
) -> None:
    """Slash Command Manager - Generate and manage slash commands for AI code assistants."""


console = Console(width=120)
SUMMARY_PANEL_WIDTH = 80


def _find_project_root() -> Path:
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


def _display_local_path(path: Path) -> str:
    """Return a path relative to the current working directory or project root."""
    resolved_path = path.resolve()
    candidates = [Path.cwd().resolve(), _find_project_root()]
    for candidate in candidates:
        try:
            return str(resolved_path.relative_to(candidate))
        except ValueError:
            continue
    return str(resolved_path)


def _resolve_detected_agents(detected: list[str] | None, selected: list[str]) -> list[str]:
    """Preserve explicitly empty detections while falling back when missing."""
    return detected if detected is not None else selected


def _build_summary_data(
    *,
    result: dict[str, Any] | None,
    detected_agents: list[str],
    selected_agents: list[str],
    safe_mode: bool,
    dry_run: bool,
    source_info: dict[str, Any],
    output_base: str,
) -> dict[str, Any]:
    """Build structured data describing generation results."""
    prompts_loaded = result["prompts_loaded"] if result else 0
    files_written = result["files_written"] if result else 0
    planned_files = len(result["files"]) if result else 0
    files_by_agent: dict[str, dict[str, Any]] = {}
    prompt_entries: list[dict[str, str]] = []
    base_path = Path(output_base).resolve()
    repo_root = _find_project_root()
    cwd = Path.cwd().resolve()
    source_candidates = [cwd, repo_root]

    def _relative_to_candidates(path_str: str, candidates: list[Path]) -> str:
        file_path = Path(path_str)
        for candidate in candidates:
            try:
                return str(file_path.resolve().relative_to(candidate.resolve()))
            except (ValueError, FileNotFoundError):
                continue
        return str(file_path)

    if result:
        for file_info in result["files"]:
            agent_key = file_info["agent"]
            agent_entry = files_by_agent.setdefault(
                agent_key,
                {
                    "display_name": file_info["agent_display_name"],
                    "paths": [],
                },
            )
            file_path = Path(file_info["path"])
            rel_path = file_info["path"]
            try:
                rel_path = str(file_path.resolve().relative_to(base_path.resolve()))
            except (ValueError, FileNotFoundError):
                rel_path = str(file_path)
            agent_entry["paths"].append(rel_path)

        for entry in files_by_agent.values():
            entry["count"] = len(entry["paths"])

    def _relative_backup(path: str) -> str:
        file_path = Path(path)
        try:
            return str(file_path.resolve().relative_to(base_path.resolve()))
        except (ValueError, FileNotFoundError):
            return path

    backups_created = (
        [_relative_backup(path) for path in result["backups_created"]] if result else []
    )
    backups_pending = (
        [_relative_backup(path) for path in result["backups_pending"]] if result else []
    )

    if result:
        for prompt in result["prompts"]:
            prompt_entries.append(
                {
                    "name": prompt["name"],
                    "path": _relative_to_candidates(prompt["path"], source_candidates),
                }
            )

    return {
        "mode": "dry-run" if dry_run else "generation",
        "safe_mode": safe_mode,
        "prompts_loaded": prompts_loaded,
        "files_written": files_written,
        "files_planned": planned_files,
        "agents": {
            "detected": detected_agents,
            "selected": selected_agents,
        },
        "files": files_by_agent,
        "backups": {
            "created": backups_created,
            "pending": backups_pending,
        },
        "source": source_info,
        "prompts": prompt_entries,
        "output_base": output_base,
    }


def _render_rich_summary(summary: dict[str, Any], *, record: bool = False) -> str | None:
    """Render the structured summary using Rich."""
    target_console = (
        Console(record=True, width=SUMMARY_PANEL_WIDTH)
        if record
        else Console(width=SUMMARY_PANEL_WIDTH)
    )
    mode_label = "DRY RUN" if summary["mode"] == "dry-run" else "Generation"
    mode_text = f"{mode_label} (safe mode)" if summary["safe_mode"] else mode_label

    root = Tree(f"{mode_text} Summary")

    counts = root.add("Counts")
    counts.add(f"Prompts loaded: {summary['prompts_loaded']}")
    counts.add(f"Files planned: {summary['files_planned']}")
    counts.add(f"Files written: {summary['files_written']}")

    agents_branch = root.add("Agents")
    detected = agents_branch.add("Detected")
    for agent in summary["agents"]["detected"] or ["None"]:
        detected.add(agent)
    selected = agents_branch.add("Selected")
    for agent in summary["agents"]["selected"] or ["None"]:
        selected.add(agent)

    source_branch = root.add("Source")
    if summary["source"]["type"] == "github":
        gh = summary["source"]
        source_branch.add(Text(f"Repository: {gh['display']}", overflow="fold"))
    else:
        source_branch.add(Text(f"Directory: {summary['source']['display']}", overflow="fold"))

    output_branch = root.add("Output")
    output_branch.add(Text(f"Directory: {summary['output_base']}", overflow="fold"))

    backups_branch = root.add("Backups")
    created = summary["backups"]["created"]
    pending = summary["backups"]["pending"]
    created_branch = backups_branch.add(f"Created: {len(created)}")
    if created:
        for path in created:
            created_branch.add(path)
    pending_branch = backups_branch.add(f"Pending: {len(pending)}")
    if pending:
        for path in pending:
            pending_branch.add(path)

    files_branch = root.add("Files")
    if summary["files"]:
        for agent_key, info in summary["files"].items():
            display = info.get("display_name", agent_key)
            count = info.get("count", 0)
            agent_branch = files_branch.add(f"{display} ({agent_key}) • {count} file(s)")
            for path in info.get("paths", []):
                agent_branch.add(Text(path, overflow="fold"))
    else:
        files_branch.add("None")

    prompts_branch = root.add("Prompts")
    if summary["prompts"]:
        for prompt in summary["prompts"]:
            prompts_branch.add(Text(f"{prompt['name']}: {prompt['path']}", overflow="fold"))
    else:
        prompts_branch.add("None")

    panel = Panel(
        root,
        title="Generation Summary",
        border_style="cyan",
        width=SUMMARY_PANEL_WIDTH,
        expand=False,
    )
    target_console.print(panel)

    if record:
        return target_console.export_text(clear=False)
    return None


def _print_generation_complete(summary: dict[str, Any]) -> None:
    """Print a concise textual completion message for interactive workflows."""
    mode_label = "DRY RUN complete" if summary["mode"] == "dry-run" else "Generation complete"
    console.print()
    console.print(f"{mode_label}:")
    console.print(f"  Prompts loaded: {summary['prompts_loaded']}")
    console.print(f"  Files written: {summary['files_written']}")


def _prompt_agent_selection(detected_agents: list) -> list:
    """Prompt user to select which agents to generate commands for.

    Args:
        detected_agents: List of detected agent configurations

    Returns:
        List of selected agent configurations (empty if cancelled)
    """

    choices = [
        questionary.Choice(
            f"{agent.display_name} ({agent.key})",
            agent,
            checked=True,  # Pre-check all detected agents
        )
        for agent in detected_agents
    ]

    selected = questionary.checkbox(
        "Select agents to generate commands for (use space to select/deselect, enter to confirm):",
        choices=choices,
    ).ask()

    if selected is None:
        # User pressed Ctrl+C
        return []

    return selected


@app.command()
def generate(  # noqa: PLR0913 PLR0912 PLR0915
    prompts_dir: Annotated[
        Path | None,
        typer.Option(
            "--prompts-dir",
            "-p",
            help="Directory containing prompt files",
        ),
    ] = None,
    agents: Annotated[
        list[str] | None,
        typer.Option(
            "--agent",
            "-a",
            help="Agent key to generate commands for (can be specified multiple times)",
        ),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            help="Show what would be done without writing files",
        ),
    ] = False,
    yes: Annotated[
        bool,
        typer.Option(
            "--yes",
            "-y",
            help="Skip confirmation prompts (forces backup-safe mode)",
        ),
    ] = False,
    target_path: Annotated[
        Path | None,
        typer.Option(
            "--target-path",
            "-t",
            help="Target directory for output paths (defaults to home directory)",
        ),
    ] = None,
    detection_path: Annotated[
        Path | None,
        typer.Option(
            "--detection-path",
            "-d",
            help="Directory to search for agent configurations (defaults to home directory)",
        ),
    ] = None,
    list_agents_flag: Annotated[
        bool,
        typer.Option(
            "--list-agents",
            help="List all supported agents and exit",
        ),
    ] = False,
    github_repo: Annotated[
        str | None,
        typer.Option(
            "--github-repo",
            help="GitHub repository in format owner/repo",
        ),
    ] = None,
    github_branch: Annotated[
        str | None,
        typer.Option(
            "--github-branch",
            help="GitHub branch name (e.g., main, release/v1.0)",
        ),
    ] = None,
    github_path: Annotated[
        str | None,
        typer.Option(
            "--github-path",
            help=(
                "Path to prompts directory or single prompt file within repository "
                "(e.g., 'prompts' for directory, 'prompts/my-prompt.md' for file)"
            ),
        ),
    ] = None,
) -> None:
    """Generate slash commands for AI code assistants."""
    # Validate GitHub flags
    github_flags_provided = [
        flag for flag in [github_repo, github_branch, github_path] if flag is not None
    ]
    if github_flags_provided:
        # Check if all three GitHub flags are provided together
        if len(github_flags_provided) != 3:
            missing_flags = []
            if github_repo is None:
                missing_flags.append("--github-repo")
            if github_branch is None:
                missing_flags.append("--github-branch")
            if github_path is None:
                missing_flags.append("--github-path")
            print(
                f"Error: All GitHub flags must be provided together. "
                f"Missing: {', '.join(missing_flags)}",
                file=sys.stderr,
            )
            print(
                "\nTo fix this:",
                file=sys.stderr,
            )
            print(
                "  - Provide all three flags: --github-repo, --github-branch, --github-path",
                file=sys.stderr,
            )
            raise typer.Exit(code=2) from None  # Validation error

        # Validate GitHub repository format
        try:
            validate_github_repo(github_repo)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            raise typer.Exit(code=2) from None  # Validation error

    # Check mutual exclusivity between --prompts-dir and GitHub flags
    if prompts_dir is not None and github_repo is not None:
        print(
            "Error: Cannot specify both --prompts-dir and GitHub repository flags "
            "(--github-repo, --github-branch, --github-path) simultaneously",
            file=sys.stderr,
        )
        print(
            "\nTo fix this:",
            file=sys.stderr,
        )
        print(
            "  - Use either --prompts-dir for local prompts, or",
            file=sys.stderr,
        )
        print(
            "  - Use --github-repo, --github-branch, and --github-path for GitHub prompts",
            file=sys.stderr,
        )
        raise typer.Exit(code=2) from None  # Validation error

    # Handle --list-agents
    if list_agents_flag:
        # Create Rich table
        table = Table(title="Supported Agents")
        table.add_column("Agent Key", style="cyan", no_wrap=True)
        table.add_column("Display Name", style="magenta")
        table.add_column("Target Path", style="blue")
        table.add_column("Detected", justify="center")

        # Get home directory for checking paths
        home_dir = Path.home()

        for agent_key in list_agent_keys():
            try:
                agent = get_agent_config(agent_key)
                # Check if command directory exists
                command_dir = agent.get_command_dir()
                command_path = home_dir / command_dir
                exists = command_path.exists()
                detected = "[green]✓[/green]" if exists else "[red]✗[/red]"

                table.add_row(
                    agent_key,
                    agent.display_name,
                    f"~/{command_dir}",
                    detected,
                )
            except KeyError:
                table.add_row(agent_key, "Unknown", "N/A", "[red]✗[/red]")

        console.print(table)
        return

    # Detect agents if not specified
    detected_agent_keys: list[str] = []

    if agents is None or len(agents) == 0:
        # Use detection_path if specified, otherwise target_path, otherwise home directory
        detection_dir = (
            detection_path
            if detection_path is not None
            else (target_path if target_path is not None else Path.home())
        )
        detected = detect_agents(detection_dir)
        if not detected:
            print("Error: No agents detected.", file=sys.stderr)
            print(f"Detection path: {detection_dir}", file=sys.stderr)
            print("\nTo fix this:", file=sys.stderr)
            print(
                "  1. Ensure at least one agent directory exists (e.g., .claude, .cursor, .gemini)",
                file=sys.stderr,
            )
            print(
                "  2. Or use --agent to specify agents manually: --agent claude-code",
                file=sys.stderr,
            )
            print(
                "  3. Or use --detection-path to search in a different directory", file=sys.stderr
            )
            raise typer.Exit(code=2) from None  # Validation error

        # Interactive selection: all detected agents pre-selected
        if not yes:
            selected_agents = _prompt_agent_selection(detected)
            if not selected_agents:
                print("Cancelled: No agents selected.", file=sys.stderr)
                raise typer.Exit(code=1) from None  # User cancellation
            agents = [agent.key for agent in selected_agents]
        else:
            # If --yes is used, auto-select all detected agents
            agents = [agent.key for agent in detected]
            print(f"Detected agents: {', '.join(agents)}")
        detected_agent_keys = [agent.key for agent in detected]
    else:
        print(f"Selected agents: {', '.join(agents)}")
        detected_agent_keys = agents.copy()

    safe_mode = bool(yes)
    if safe_mode:
        print("Running in non-interactive safe mode: backups will be created before overwriting.")

    # Determine target path (default to home directory)
    actual_target_path = target_path if target_path is not None else Path.home()

    # Track whether prompts_dir was explicitly provided by the user
    # If None, use default (bundled prompts fallback)
    # If provided, it's user-specified
    is_explicit_prompts_dir = prompts_dir is not None
    actual_prompts_dir = prompts_dir if prompts_dir is not None else Path("prompts")

    # Create writer
    overwrite_action = "backup" if yes else None
    writer = SlashCommandWriter(
        prompts_dir=actual_prompts_dir,
        agents=agents,
        dry_run=dry_run,
        base_path=actual_target_path,
        overwrite_action=overwrite_action,
        is_explicit_prompts_dir=is_explicit_prompts_dir,
        github_repo=github_repo,
        github_branch=github_branch,
        github_path=github_path,
    )

    if github_repo and github_branch and github_path:
        source_info: dict[str, Any] = {
            "type": "github",
            "repo": github_repo,
            "branch": github_branch,
            "path": github_path,
            "display": f"{github_repo}@{github_branch}:{github_path}",
        }
    else:
        resolved_prompts = actual_prompts_dir.resolve()
        display_dir = _display_local_path(resolved_prompts)
        source_info = {
            "type": "local",
            "path": str(resolved_prompts),
            "display": display_dir,
        }

    selected_agent_keys = agents.copy()

    # Generate commands
    try:
        result = writer.generate()
    except requests.exceptions.HTTPError as e:
        print(f"Error: GitHub API error: {e}", file=sys.stderr)
        print("\nTo fix this:", file=sys.stderr)
        print("  - Verify the repository exists and is public", file=sys.stderr)
        print("  - Check that the branch name is correct", file=sys.stderr)
        print("  - Ensure the path exists in the repository", file=sys.stderr)
        if github_repo:
            print(f"  - Repository: {github_repo}", file=sys.stderr)
            print(f"  - Branch: {github_branch}", file=sys.stderr)
            print(f"  - Path: {github_path}", file=sys.stderr)
        raise typer.Exit(code=3) from None  # I/O error
    except requests.exceptions.RequestException as e:
        print(f"Error: Network error accessing GitHub: {e}", file=sys.stderr)
        print("\nTo fix this:", file=sys.stderr)
        print("  - Check your internet connection", file=sys.stderr)
        print("  - Verify GitHub API is accessible", file=sys.stderr)
        raise typer.Exit(code=3) from None  # I/O error
    except NoPromptsDiscoveredError as e:
        print(str(e), file=sys.stderr)
        summary_data = _build_summary_data(
            result=None,
            detected_agents=_resolve_detected_agents(detected_agent_keys, selected_agent_keys),
            selected_agents=selected_agent_keys,
            safe_mode=safe_mode,
            dry_run=dry_run,
            source_info=source_info,
            output_base=str(actual_target_path.resolve()),
        )
        _render_rich_summary(summary_data)
        raise typer.Exit(code=1) from None
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("\nTo fix this:", file=sys.stderr)
        if is_explicit_prompts_dir:
            # User explicitly provided --prompts-dir
            print("  - Ensure the specified prompts directory exists", file=sys.stderr)
            print(
                "  - Check that --prompts-dir points to a valid directory",
                file=sys.stderr,
            )
            print(f"    (current: {prompts_dir})", file=sys.stderr)
        else:
            # Default path, tried to fall back to bundled prompts
            print("  - Bundled prompts were not found in the installed package", file=sys.stderr)
            print("  - Use --prompts-dir to specify a custom prompts directory", file=sys.stderr)
        raise typer.Exit(code=3) from None  # I/O error (e.g., prompts directory doesn't exist)
    except KeyError as e:
        print(f"Error: Invalid agent key: {e}", file=sys.stderr)
        print("\nTo fix this:", file=sys.stderr)
        print("  - Use --list-agents to see all supported agents", file=sys.stderr)
        print("  - Ensure agent keys are spelled correctly", file=sys.stderr)
        valid_keys = ", ".join(list_agent_keys())
        print(f"  - Valid agent keys: {valid_keys}", file=sys.stderr)
        raise typer.Exit(code=2) from None  # Validation error (invalid agent key)
    except PermissionError as e:
        print(f"Error: Permission denied: {e}", file=sys.stderr)
        print("\nTo fix this:", file=sys.stderr)
        print("  - Check file and directory permissions", file=sys.stderr)
        print("  - Ensure you have write access to the output directory", file=sys.stderr)
        print("  - Try running with elevated permissions if needed", file=sys.stderr)
        raise typer.Exit(code=3) from None  # I/O error (permission denied)
    except OSError as e:
        print(f"Error: I/O error: {e}", file=sys.stderr)
        print("\nTo fix this:", file=sys.stderr)
        print("  - Check that the output directory is writable", file=sys.stderr)
        print("  - Ensure there's sufficient disk space", file=sys.stderr)
        print(
            f"  - Verify the path exists: {actual_target_path}",
            file=sys.stderr,
        )
        raise typer.Exit(code=3) from None  # I/O error (file system errors)
    except RuntimeError as e:
        if "Cancelled" in str(e):
            print("Cancelled: Operation cancelled by user.", file=sys.stderr)
            raise typer.Exit(code=1) from None  # User cancellation
        raise

    summary_data = _build_summary_data(
        result=result,
        detected_agents=_resolve_detected_agents(detected_agent_keys, selected_agent_keys),
        selected_agents=selected_agent_keys,
        safe_mode=safe_mode,
        dry_run=dry_run,
        source_info=source_info,
        output_base=str(actual_target_path.resolve()),
    )
    _render_rich_summary(summary_data)
    if result is not None:
        _print_generation_complete(summary_data)


@app.command()
def cleanup(
    agents: Annotated[
        list[str] | None,
        typer.Option(
            "--agent",
            "-a",
            help=(
                "Agent keys to clean (can be specified multiple times). "
                "If not specified, cleans all agents."
            ),
        ),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            help="Show what would be deleted without actually deleting files",
        ),
    ] = False,
    yes: Annotated[
        bool,
        typer.Option(
            "--yes",
            "-y",
            help="Skip confirmation prompts",
        ),
    ] = False,
    target_path: Annotated[
        Path | None,
        typer.Option(
            "--target-path",
            "-t",
            help="Target directory to search for generated files (defaults to home directory)",
        ),
    ] = None,
    include_backups: Annotated[
        bool,
        typer.Option(
            "--include-backups/--no-backups",
            help="Include backup files in cleanup (default: True)",
        ),
    ] = True,
) -> None:
    """Clean up generated slash commands."""
    # Determine target path (default to home directory)
    actual_target_path = target_path if target_path is not None else Path.home()

    # Create writer for finding files
    writer = SlashCommandWriter(
        prompts_dir=Path("prompts"),  # Not used for cleanup
        agents=[],
        dry_run=dry_run,
        base_path=actual_target_path,
    )

    # Find files
    found_files = writer.find_generated_files(agents=agents, include_backups=include_backups)

    if not found_files:
        console.print("[green]No generated files found.[/green]")
        return

    # Display what will be deleted in a table
    table = Table(title=f"Found {len(found_files)} file(s) to delete")
    table.add_column("File Path", style="cyan", no_wrap=False)
    table.add_column("Agent", style="magenta")
    table.add_column("Type", style="yellow", justify="center")

    # Group files by agent for better readability
    files_by_agent: dict[str, list[dict[str, Any]]] = {}
    for file_info in found_files:
        agent = file_info["agent_display_name"]
        if agent not in files_by_agent:
            files_by_agent[agent] = []
        files_by_agent[agent].append(file_info)

    # Add rows to table
    for agent, files in sorted(files_by_agent.items()):
        for file_info in files:
            type_display = {
                "command": "[green]command[/green]",
                "backup": "[yellow]backup[/yellow]",
            }.get(file_info["type"], file_info["type"])
            table.add_row(
                str(file_info["path"]),
                agent,
                type_display,
            )

    console.print()
    console.print(table)

    # Prompt for confirmation
    if not yes:
        console.print()
        console.print(
            Panel(
                "[bold red]⚠️  WARNING: This will permanently delete "
                "the files listed above.[/bold red]",
                title="Confirm Deletion",
                border_style="red",
            )
        )
        confirmed = questionary.confirm("Are you sure you want to proceed?", default=False).ask()
        if not confirmed:
            console.print("[yellow]Cleanup cancelled.[/yellow]")
            raise typer.Exit(code=1) from None

    # Perform cleanup
    try:
        result = writer.cleanup(agents=agents, include_backups=include_backups, dry_run=dry_run)
    except Exception as e:
        console.print(f"[bold red]Error during cleanup: {e}[/bold red]")
        raise typer.Exit(code=3) from None

    # Print summary in a panel
    mode = "DRY RUN" if dry_run else "Cleanup"
    deleted_text = "would be" if dry_run else ""
    summary_lines = [
        f"Files {deleted_text} deleted: [bold green]{result['files_deleted']}[/bold green]",
    ]
    if result.get("errors"):
        summary_lines.append(f"Errors: [bold red]{len(result['errors'])}[/bold red]")
        for error in result["errors"]:
            summary_lines.append(f"  - {error['path']}: {error['error']}")

    console.print()
    console.print(
        Panel(
            "\n".join(summary_lines),
            title=f"{mode} Complete",
            border_style="green" if not result.get("errors") else "red",
        )
    )


def main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
