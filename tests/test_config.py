"""Tests for slash command configuration data models."""

from __future__ import annotations

import dataclasses
from collections.abc import Iterable
from typing import get_type_hints

import pytest

from slash_commands.config import SUPPORTED_AGENTS, AgentConfig, CommandFormat


@pytest.fixture(scope="module")
def supported_agents_by_key() -> dict[str, AgentConfig]:
    return {agent.key: agent for agent in SUPPORTED_AGENTS}


def test_command_format_defines_markdown_and_toml():
    assert CommandFormat.MARKDOWN.value == "markdown"
    assert CommandFormat.TOML.value == "toml"
    assert {member.value for member in CommandFormat} == {"markdown", "toml"}


def test_agent_config_is_frozen_dataclass():
    assert dataclasses.is_dataclass(AgentConfig)
    params = getattr(AgentConfig, "__dataclass_params__", None)
    assert params is not None and params.frozen is True


@pytest.mark.parametrize(
    "field_name, field_type",
    [
        ("key", str),
        ("display_name", str),
        ("command_dir", str),
        ("command_format", CommandFormat),
        ("command_file_extension", str),
        ("detection_dirs", tuple[str, ...]),
        ("platform_command_dirs", dict[str, str] | None),
    ],
)
def test_agent_config_has_expected_field_types(field_name: str, field_type: object):
    field_types = get_type_hints(AgentConfig)
    assert field_name in field_types
    assert field_types[field_name] == field_type


def test_supported_agents_is_tuple_sorted_by_key():
    assert isinstance(SUPPORTED_AGENTS, tuple)
    keys = tuple(agent.key for agent in SUPPORTED_AGENTS)
    assert keys == tuple(sorted(keys))


def test_supported_agents_have_valid_structure(
    supported_agents_by_key: dict[str, AgentConfig],
):
    """Validate structural invariants for all agent configurations."""
    for agent in supported_agents_by_key.values():
        # Command directory must end with a known suffix
        assert (
            agent.command_dir.endswith("/commands")
            or agent.command_dir.endswith("/prompts")
            or agent.command_dir.endswith("/global_workflows")
            or agent.command_dir.endswith("/command")
        ), (
            f"{agent.key}: command_dir must end with /commands, /prompts, /global_workflows, or /command"
        )
        # File extension must start with a dot
        assert agent.command_file_extension.startswith("."), (
            f"{agent.key}: command_file_extension must start with '.'"
        )
        # Detection dirs must be a tuple of hidden directories or cross-platform paths
        assert isinstance(agent.detection_dirs, tuple), (
            f"{agent.key}: detection_dirs must be a tuple"
        )
        # Allow hidden directories (starting with .) or cross-platform paths (macOS, Windows)
        for dir_ in agent.detection_dirs:
            assert dir_.startswith(".") or "Library" in dir_ or "AppData" in dir_, (
                f"{agent.key}: detection_dir '{dir_}' must start with '.', contain 'Library' (macOS), or 'AppData' (Windows)"
            )


def test_supported_agents_have_valid_command_formats(
    supported_agents_by_key: dict[str, AgentConfig],
):
    """Validate that all agents use a supported command format."""
    valid_formats = {CommandFormat.MARKDOWN, CommandFormat.TOML}
    for agent in supported_agents_by_key.values():
        assert agent.command_format in valid_formats, (
            f"{agent.key}: command_format must be MARKDOWN or TOML"
        )


def test_detection_dirs_cover_command_directory_roots(
    supported_agents_by_key: dict[str, AgentConfig],
):
    for agent in supported_agents_by_key.values():
        # For nested paths like .config/opencode/commands, check parent directories.
        # Some agents have platform-specific or special detection paths that don't follow
        # the standard "root directory in detection_dirs" pattern.
        if "/" in agent.command_dir:
            path_parts = agent.command_dir.split("/")
            # Check first directory component
            command_root = path_parts[0]
            # Special cases: agents with non-standard detection patterns (e.g., .config/Code for vs-code)
            if agent.key == "vs-code":
                assert ".config" in agent.detection_dirs or ".config/Code" in agent.detection_dirs
            elif agent.key == "windsurf":
                assert (
                    ".codeium" in agent.detection_dirs
                    or ".codeium/windsurf" in agent.detection_dirs
                )
            elif agent.key == "opencode":
                assert ".opencode" in agent.detection_dirs
            elif agent.key == "amazon-q":
                # Uses .aws/amazonq specifically to avoid false positives from .aws directory
                assert ".aws/amazonq" in agent.detection_dirs
            else:
                assert command_root in agent.detection_dirs
        else:
            command_root = agent.command_dir.split("/", 1)[0]
            assert command_root in agent.detection_dirs
        assert isinstance(agent.detection_dirs, Iterable)
