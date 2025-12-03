"""Telemetry tracking for CLI usage analytics.

This module provides anonymous telemetry tracking using PostHog to collect
usage data about CLI commands and flags without collecting any user-identifying
information.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from slash_commands.__version__ import __version_with_commit__


def _is_debug_enabled() -> bool:
    """Check if debug mode is enabled via DEBUG environment variable.

    Returns:
        True if DEBUG environment variable is set to a truthy value
    """
    debug = os.getenv("DEBUG", "").lower()
    return debug in ("1", "t", "true", "y", "yes", "on", "enable", "enabled")


def _is_telemetry_disabled() -> bool:
    """Check if telemetry is disabled via environment variables.

    Respects both POSTHOG_DISABLED and DO_NOT_TRACK environment variables.
    DO_NOT_TRACK accepts common truthy values: 1, t, true, y, yes, on, enable, enabled.

    Returns:
        True if telemetry should be disabled, False otherwise
    """
    # Check POSTHOG_DISABLED
    posthog_disabled = os.getenv("POSTHOG_DISABLED", "").lower()
    if posthog_disabled in ("1", "t", "true", "y", "yes", "on", "enable", "enabled"):
        if _is_debug_enabled():
            print("[DEBUG] PostHog telemetry disabled via POSTHOG_DISABLED environment variable", file=sys.stderr)
        return True

    # Check DO_NOT_TRACK (standard opt-out)
    do_not_track = os.getenv("DO_NOT_TRACK", "").lower()
    if do_not_track in ("1", "t", "true", "y", "yes", "on", "enable", "enabled"):
        if _is_debug_enabled():
            print("[DEBUG] PostHog telemetry disabled via DO_NOT_TRACK environment variable", file=sys.stderr)
        return True

    return False


def _sanitize_flags_for_generate(
    *,
    dry_run: bool,
    yes: bool,
    list_agents_flag: bool,
    github_repo: str | None,
    github_branch: str | None,
    github_path: str | None,
    prompts_dir: str | Path | None,
    target_path: str | Path | None,
    detection_path: str | Path | None,
    agents: list[str] | None,
) -> dict[str, Any]:
    """Sanitize flags for generate command.

    Args:
        dry_run: Whether dry-run mode is enabled
        yes: Whether --yes flag was used
        list_agents_flag: Whether --list-agents flag was used
        github_repo: GitHub repo string
        github_branch: GitHub branch name
        github_path: GitHub path within repository
        prompts_dir: Prompts directory path
        target_path: Target directory path
        detection_path: Detection directory path
        agents: List of agent keys (will be converted to count and list)

    Returns:
        Dictionary of flags for telemetry
    """
    flags: dict[str, Any] = {
        "dry_run": dry_run,
        "yes": yes,
        "list_agents": list_agents_flag,
        "agent_count": len(agents) if agents else 0,
    }

    # Add GitHub flags if provided
    if github_repo is not None:
        flags["github_repo"] = github_repo
    if github_branch is not None:
        flags["github_branch"] = github_branch
    if github_path is not None:
        flags["github_path"] = github_path

    # Add directory paths if provided (convert Path to string)
    if prompts_dir is not None:
        flags["prompts_dir"] = str(prompts_dir)
    if target_path is not None:
        flags["target_path"] = str(target_path)
    if detection_path is not None:
        flags["detection_path"] = str(detection_path)

    # Add agent list if provided
    if agents:
        flags["agents"] = agents

    return flags


def _sanitize_flags_for_cleanup(
    *,
    dry_run: bool,
    yes: bool,
    include_backups: bool,
    target_path: str | Path | None,
    agents: list[str] | None,
) -> dict[str, Any]:
    """Sanitize flags for cleanup command.

    Args:
        dry_run: Whether dry-run mode is enabled
        yes: Whether --yes flag was used
        include_backups: Whether backups are included
        target_path: Target directory path
        agents: List of agent keys (will be converted to count and list)

    Returns:
        Dictionary of flags for telemetry
    """
    flags: dict[str, Any] = {
        "dry_run": dry_run,
        "yes": yes,
        "include_backups": include_backups,
        "agent_count": len(agents) if agents else 0,
    }

    # Add directory path if provided
    if target_path is not None:
        flags["target_path"] = str(target_path)

    # Add agent list if provided
    if agents:
        flags["agents"] = agents

    return flags


def _get_python_version() -> str:
    """Get Python version in major.minor format.

    Returns:
        Python version string (e.g., "3.12")
    """
    return f"{sys.version_info.major}.{sys.version_info.minor}"


def track_app_start(posthog_client: Any) -> None:
    """Track CLI app startup event.

    Args:
        posthog_client: PostHog client instance
    """
    if _is_telemetry_disabled():
        return

    event_data = {
        "event": "cli_app_started",
        "properties": {
            "$process_person_profile": False,
            "app_version": __version_with_commit__,
            "python_version": _get_python_version(),
        },
    }

    if _is_debug_enabled():
        print("[DEBUG] PostHog event would be sent:", file=sys.stderr)
        print(json.dumps(event_data, indent=2), file=sys.stderr)

    try:
        posthog_client.capture(
            event="cli_app_started",
            properties=event_data["properties"],
        )
    except Exception:
        # Silently fail - telemetry should never break the app
        pass


def track_command(
    posthog_client: Any,
    command: str,
    flags: dict[str, Any],
) -> None:
    """Track command execution event.

    Args:
        posthog_client: PostHog client instance
        command: Command name ("generate", "cleanup", "version")
        flags: Dictionary of flag values (will be flattened as top-level properties)
    """
    if _is_telemetry_disabled():
        return

    # Flatten flags as top-level properties for easier filtering in PostHog
    properties = {
        "$process_person_profile": False,
        "command": command,
        "app_version": __version_with_commit__,
    }
    # Add all flags as top-level properties
    properties.update(flags)

    event_data = {
        "event": "cli_command_executed",
        "properties": properties,
    }

    if _is_debug_enabled():
        print("[DEBUG] PostHog event would be sent:", file=sys.stderr)
        print(json.dumps(event_data, indent=2), file=sys.stderr)

    try:
        posthog_client.capture(
            event="cli_command_executed",
            properties=properties,
        )
    except Exception:
        # Silently fail - telemetry should never break the app
        pass


def flush_telemetry(posthog_client: Any) -> None:
    """Flush telemetry events and shutdown PostHog client.

    Args:
        posthog_client: PostHog client instance
    """
    if _is_telemetry_disabled():
        return

    try:
        posthog_client.flush()
        posthog_client.shutdown()
    except Exception:
        # Silently fail - telemetry should never break the app
        pass
