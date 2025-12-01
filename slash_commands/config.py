"""Configuration models for slash command generation."""

from __future__ import annotations

import sys
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import Enum


class CommandFormat(str, Enum):
    """Supported slash command file formats."""

    MARKDOWN = "markdown"
    TOML = "toml"


@dataclass(frozen=True)
class AgentConfig:
    """Metadata describing how to generate commands for a specific agent."""

    key: str
    display_name: str
    command_dir: str
    command_format: CommandFormat
    command_file_extension: str
    detection_dirs: tuple[str, ...]
    platform_command_dirs: dict[str, str] | None = None

    def iter_detection_dirs(self) -> Iterable[str]:
        """Return an iterator over configured detection directories."""

        return iter(self.detection_dirs)

    def get_command_dir(self) -> str:
        """Return the command directory for the current platform.

        If platform_command_dirs is configured, returns the platform-specific path.
        Otherwise, returns the default command_dir.
        """
        if self.platform_command_dirs is not None:
            return self.platform_command_dirs.get(sys.platform, self.command_dir)
        return self.command_dir


_SUPPORTED_AGENT_DATA: tuple[
    tuple[
        str,
        str,
        str,
        CommandFormat,
        str,
        tuple[str, ...],
        dict[str, str] | None,
    ],
    ...,
] = (
    (
        "claude-code",
        "Claude Code",
        ".claude/commands",
        CommandFormat.MARKDOWN,
        ".md",
        (".claude",),
        None,
    ),
    (
        "vs-code",
        "VS Code",
        ".config/Code/User/prompts",
        CommandFormat.MARKDOWN,
        ".prompt.md",
        (".config/Code", "Library/Application Support/Code", "AppData/Roaming/Code"),
        {
            "linux": ".config/Code/User/prompts",
            "darwin": "Library/Application Support/Code/User/prompts",
            "win32": "AppData/Roaming/Code/User/prompts",
        },
    ),
    ("codex-cli", "Codex CLI", ".codex/prompts", CommandFormat.MARKDOWN, ".md", (".codex",), None),
    (
        "cursor",
        "Cursor",
        ".cursor/commands",
        CommandFormat.MARKDOWN,
        ".md",
        (".cursor",),
        None,
    ),
    (
        "gemini-cli",
        "Gemini CLI",
        ".gemini/commands",
        CommandFormat.TOML,
        ".toml",
        (".gemini",),
        None,
    ),
    (
        "windsurf",
        "Windsurf",
        ".codeium/windsurf/global_workflows",
        CommandFormat.MARKDOWN,
        ".md",
        (".codeium", ".codeium/windsurf"),
        None,
    ),
    (
        "opencode",
        "OpenCode CLI",
        ".config/opencode/command",
        CommandFormat.MARKDOWN,
        ".md",
        (".opencode",),
        None,
    ),
    (
        "amazon-q",
        "Amazon Q",
        ".aws/amazonq/prompts",
        CommandFormat.MARKDOWN,
        ".md",
        (".aws/amazonq",),
        None,
    ),
)

_SORTED_AGENT_DATA = tuple(sorted(_SUPPORTED_AGENT_DATA, key=lambda item: item[0]))

SUPPORTED_AGENTS: tuple[AgentConfig, ...] = tuple(
    AgentConfig(
        key=key,
        display_name=display_name,
        command_dir=command_dir,
        command_format=command_format,
        command_file_extension=command_file_extension,
        detection_dirs=detection_dirs,
        platform_command_dirs=platform_command_dirs,
    )
    for (
        key,
        display_name,
        command_dir,
        command_format,
        command_file_extension,
        detection_dirs,
        platform_command_dirs,
    ) in _SORTED_AGENT_DATA
)

_AGENT_LOOKUP: Mapping[str, AgentConfig] = {agent.key: agent for agent in SUPPORTED_AGENTS}


def list_agent_keys() -> tuple[str, ...]:
    """Return the keys for all supported agents in order."""

    return tuple(agent.key for agent in SUPPORTED_AGENTS)


def get_agent_config(key: str) -> AgentConfig:
    """Return configuration for the requested agent key."""

    try:
        return _AGENT_LOOKUP[key]
    except KeyError as exc:  # pragma: no cover - defensive branch
        raise KeyError(f"Unsupported agent: {key}") from exc
