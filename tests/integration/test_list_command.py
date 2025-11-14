"""Integration tests for list command."""

import subprocess

from slash_commands.list_discovery import discover_managed_prompts

from .conftest import REPO_ROOT, get_slash_man_command


def test_list_discovers_managed_prompts(temp_test_dir, test_prompts_dir):
    """Test that list discovers managed prompts across multiple agent directories."""
    # Create managed prompts for multiple agents using generate command
    agents = ["cursor", "claude-code"]

    for agent in agents:
        cmd = get_slash_man_command() + [
            "generate",
            "--prompts-dir",
            str(test_prompts_dir),
            "--agent",
            agent,
            "--target-path",
            str(temp_test_dir),
            "--yes",
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result.returncode == 0, f"Failed to generate prompts for {agent}: {result.stderr}"

    # Discover managed prompts using discovery function
    discovered = discover_managed_prompts(temp_test_dir, agents)

    # Verify prompts were discovered for all agents
    assert len(discovered) > 0, "No managed prompts were discovered"

    # Verify we have prompts from both agents
    discovered_agents = {prompt["agent"] for prompt in discovered}
    assert "cursor" in discovered_agents, "Cursor prompts not discovered"
    assert "claude-code" in discovered_agents, "Claude-code prompts not discovered"

    # Verify all discovered prompts have managed_by field
    for prompt in discovered:
        assert prompt["meta"].get("managed_by") == "slash-man", (
            f"Prompt {prompt['name']} missing managed_by field"
        )
        assert prompt["name"] is not None, f"Prompt missing name: {prompt}"
        assert prompt["file_path"].exists(), (
            f"Prompt file path does not exist: {prompt['file_path']}"
        )
