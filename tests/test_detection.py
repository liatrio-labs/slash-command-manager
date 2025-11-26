"""Tests for agent auto-detection helpers."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from slash_commands.config import SUPPORTED_AGENTS, AgentConfig, get_agent_config
from slash_commands.detection import detect_agents


@pytest.fixture(scope="module")
def supported_agents_by_key() -> dict[str, AgentConfig]:
    return {agent.key: agent for agent in SUPPORTED_AGENTS}


def test_detect_agents_returns_empty_when_no_matching_directories(tmp_path: Path):
    (tmp_path / "unrelated").mkdir()
    detected = detect_agents(tmp_path)
    assert detected == []


def test_detect_agents_identifies_configured_directories(
    tmp_path: Path, supported_agents_by_key: dict[str, AgentConfig]
):
    # Test all supported agents to ensure detection works for any new additions
    agent_keys = {agent.key for agent in SUPPORTED_AGENTS}
    for key in agent_keys:
        agent = supported_agents_by_key[key]
        for directory in agent.detection_dirs:
            full_dir = tmp_path / directory
            full_dir.mkdir(parents=True, exist_ok=True)

    detected = detect_agents(tmp_path)
    detected_keys = [agent.key for agent in detected]

    expected_order = [a.key for a in SUPPORTED_AGENTS if a.key in agent_keys]
    assert detected_keys == expected_order
    for key in detected_keys:
        directories = {tmp_path / path for path in supported_agents_by_key[key].detection_dirs}
        assert all(directory.exists() for directory in directories)


def test_detect_agents_deduplicates_and_orders_results(tmp_path: Path):
    claude_agent = next(agent for agent in SUPPORTED_AGENTS if agent.key == "claude-code")
    cursor_agent = next(agent for agent in SUPPORTED_AGENTS if agent.key == "cursor")

    for directory in claude_agent.detection_dirs + cursor_agent.detection_dirs:
        (tmp_path / directory).mkdir(parents=True, exist_ok=True)

    # create unrelated directories that should be ignored
    (tmp_path / ".unknown").mkdir()
    (tmp_path / "not-a-config").mkdir()

    detected = detect_agents(tmp_path)
    detected_keys = [agent.key for agent in detected]

    assert detected_keys == ["claude-code", "cursor"]
    assert all(detected_keys.count(key) == 1 for key in detected_keys)


@pytest.mark.parametrize(
    "platform_value,expected_dir",
    [
        ("linux", ".config/Code"),
        ("darwin", "Library/Application Support/Code"),
        ("win32", "AppData/Roaming/Code"),
    ],
)
def test_vs_code_detection_multiplatform(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, platform_value: str, expected_dir: str
) -> None:
    """Test VS Code detection works on all platforms."""
    monkeypatch.setattr(sys, "platform", platform_value)
    (tmp_path / expected_dir).mkdir(parents=True, exist_ok=True)

    detected = detect_agents(tmp_path)
    detected_keys = [agent.key for agent in detected]

    assert "vs-code" in detected_keys


@pytest.mark.parametrize("platform_value", ["linux", "darwin", "win32"])
def test_vs_code_detection_empty_when_no_directories(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, platform_value: str
) -> None:
    """Test VS Code detection returns nothing when paths don't exist."""
    monkeypatch.setattr(sys, "platform", platform_value)

    detected = detect_agents(tmp_path)
    detected_keys = [agent.key for agent in detected]

    assert "vs-code" not in detected_keys


@pytest.mark.parametrize(
    "platform_value,expected_command_dir",
    [
        ("linux", ".config/Code/User/prompts"),
        ("darwin", "Library/Application Support/Code/User/prompts"),
        ("win32", "AppData/Roaming/Code/User/prompts"),
    ],
)
def test_vs_code_get_command_dir_platform_specific(
    monkeypatch: pytest.MonkeyPatch, platform_value: str, expected_command_dir: str
) -> None:
    """Test get_command_dir() returns correct platform-specific path."""
    monkeypatch.setattr(sys, "platform", platform_value)

    vs_code_agent = get_agent_config("vs-code")
    actual_dir = vs_code_agent.get_command_dir()

    assert actual_dir == expected_command_dir


def test_vs_code_get_command_dir_fallback_to_default() -> None:
    """Test get_command_dir() falls back to command_dir when platform_command_dirs is None."""
    claude_code_agent = get_agent_config("claude-code")
    # Claude Code agent should have platform_command_dirs=None (not platform-specific)

    actual_dir = claude_code_agent.get_command_dir()

    assert actual_dir == claude_code_agent.command_dir
