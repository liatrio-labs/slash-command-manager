"""Telemetry tracking for CLI usage analytics.

This module provides anonymous telemetry tracking using PostHog to collect
usage data about CLI commands and flags without collecting any user-identifying
information.
"""

from __future__ import annotations

import sys
from typing import Any

from slash_commands.__version__ import __version_with_commit__


def _is_telemetry_disabled() -> bool:
    """Check if telemetry is disabled via environment variables.

    Respects both POSTHOG_DISABLED and DO_NOT_TRACK environment variables.
    DO_NOT_TRACK accepts common truthy values: 1, t, true, y, yes, on, enable, enabled.

    Returns:
        True if telemetry should be disabled, False otherwise
    """
    import os

    # Check POSTHOG_DISABLED
    posthog_disabled = os.getenv("POSTHOG_DISABLED", "").lower()
    if posthog_disabled in ("1", "t", "true", "y", "yes", "on", "enable", "enabled"):
        return True

    # Check DO_NOT_TRACK (standard opt-out)
    do_not_track = os.getenv("DO_NOT_TRACK", "").lower()
    if do_not_track in ("1", "t", "true", "y", "yes", "on", "enable", "enabled"):
        return True

    return False


def _sanitize_flags_for_generate(
    *,
    dry_run: bool,
    yes: bool,
    list_agents_flag: bool,
    github_repo: str | None,
    agents: list[str] | None,
) -> dict[str, Any]:
    """Sanitize flags for generate command to remove PII.

    Args:
        dry_run: Whether dry-run mode is enabled
        yes: Whether --yes flag was used
        list_agents_flag: Whether --list-agents flag was used
        github_repo: GitHub repo string (will be converted to boolean)
        agents: List of agent keys (will be converted to count only)

    Returns:
        Dictionary of sanitized flags safe for telemetry
    """
    return {
        "dry_run": dry_run,
        "yes": yes,
        "list_agents": list_agents_flag,
        "has_github_source": github_repo is not None,
        "agent_count": len(agents) if agents else 0,
    }


def _sanitize_flags_for_cleanup(
    *,
    dry_run: bool,
    yes: bool,
    include_backups: bool,
    agents: list[str] | None,
) -> dict[str, Any]:
    """Sanitize flags for cleanup command to remove PII.

    Args:
        dry_run: Whether dry-run mode is enabled
        yes: Whether --yes flag was used
        include_backups: Whether backups are included
        agents: List of agent keys (will be converted to count only)

    Returns:
        Dictionary of sanitized flags safe for telemetry
    """
    return {
        "dry_run": dry_run,
        "yes": yes,
        "include_backups": include_backups,
        "agent_count": len(agents) if agents else 0,
    }


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

    try:
        posthog_client.capture(
            event="cli_app_started",
            properties={
                "$process_person_profile": False,
                "app_version": __version_with_commit__,
                "python_version": _get_python_version(),
            },
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
        flags: Dictionary of sanitized flags
    """
    if _is_telemetry_disabled():
        return

    try:
        posthog_client.capture(
            event="cli_command_executed",
            properties={
                "$process_person_profile": False,
                "command": command,
                "app_version": __version_with_commit__,
                "flags": flags,
            },
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

