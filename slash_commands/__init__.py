"""Slash command generator package."""

from .config import SUPPORTED_AGENTS, AgentConfig, CommandFormat, get_agent_config, list_agent_keys
from .detection import detect_agents
from .writer import NoPromptsDiscoveredError, SlashCommandWriter

__all__ = [
    "SUPPORTED_AGENTS",
    "AgentConfig",
    "CommandFormat",
    "SlashCommandWriter",
    "NoPromptsDiscoveredError",
    "app",
    "detect_agents",
    "get_agent_config",
    "list_agent_keys",
]

# Expose CLI for testing
from .cli import app
