"""Integration tests for list command."""

import subprocess
from datetime import UTC, datetime

from slash_commands.list_discovery import (
    count_backups,
    discover_managed_prompts,
    format_source_info,
)

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


def test_list_shows_backup_counts(temp_test_dir, test_prompts_dir):
    """Test that backup counts are calculated correctly for managed prompts."""
    # Generate a managed prompt
    cmd = get_slash_man_command() + [
        "generate",
        "--prompts-dir",
        str(test_prompts_dir),
        "--agent",
        "claude-code",
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
    assert result.returncode == 0, f"Failed to generate prompt: {result.stderr}"

    # Find the generated file
    generated_file = temp_test_dir / ".claude" / "commands" / "test-prompt-1.md"
    assert generated_file.exists(), "Generated file should exist"

    # Initially no backups
    count = count_backups(generated_file)
    assert count == 0, "Should have 0 backups initially"

    # Create backup files matching the pattern from writer.py
    timestamp1 = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    backup1 = generated_file.parent / f"test-prompt-1.md.{timestamp1}.bak"
    backup1.write_text("backup content 1", encoding="utf-8")

    # Wait a moment to ensure different timestamp
    import time

    time.sleep(1)

    timestamp2 = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    backup2 = generated_file.parent / f"test-prompt-1.md.{timestamp2}.bak"
    backup2.write_text("backup content 2", encoding="utf-8")

    # Count backups
    count = count_backups(generated_file)
    assert count == 2, f"Should have 2 backups, got {count}"


def test_list_shows_source_info(temp_test_dir, test_prompts_dir):
    """Test that source information is formatted correctly for local and GitHub sources."""
    # Generate prompts from local source
    cmd_local = get_slash_man_command() + [
        "generate",
        "--prompts-dir",
        str(test_prompts_dir),
        "--agent",
        "claude-code",
        "--target-path",
        str(temp_test_dir),
        "--yes",
    ]
    result_local = subprocess.run(
        cmd_local,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result_local.returncode == 0, (
        f"Failed to generate from local source: {result_local.stderr}"
    )

    # Discover managed prompts
    discovered = discover_managed_prompts(temp_test_dir, ["claude-code"])
    assert len(discovered) > 0, "Should discover at least one prompt"

    # Check source info formatting for local source
    for prompt in discovered:
        source_info = format_source_info(prompt["meta"])
        assert source_info.startswith("local:"), f"Expected local source, got: {source_info}"
        # Verify it contains the source directory or path
        assert "prompts" in source_info.lower() or "test" in source_info.lower(), (
            f"Source info should contain path info: {source_info}"
        )


def test_list_output_structure(temp_test_dir, test_prompts_dir):
    """Test that list output structure matches expected format."""
    from slash_commands.list_discovery import (
        build_list_data_structure,
        count_unmanaged_prompts,
        discover_managed_prompts,
        render_list_tree,
    )

    # Generate prompts for multiple agents
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

    # Discover managed prompts
    discovered = discover_managed_prompts(temp_test_dir, agents)

    # Count unmanaged prompts
    unmanaged_counts = count_unmanaged_prompts(temp_test_dir, agents)

    # Build data structure
    data_structure = build_list_data_structure(discovered, unmanaged_counts)

    # Render tree and capture output
    output = render_list_tree(data_structure, record=True)

    # Verify output structure
    assert output is not None, "Output should not be None"
    assert "Managed Prompts" in output or "List Summary" in output, (
        "Output should contain tree root"
    )

    # Verify prompts are grouped by name
    assert "Prompts" in output, "Output should contain Prompts section"

    # Verify source information is shown
    assert "Source:" in output or "local:" in output.lower(), (
        "Output should contain source information"
    )

    # Verify agents are shown
    for agent in agents:
        assert agent in output.lower(), f"Output should contain agent {agent}"

    # Verify unmanaged counts section exists (even if empty)
    # The function adds this section if unmanaged_counts dict exists
    assert "Unmanaged" in output or len(unmanaged_counts) == 0, (
        "Output should handle unmanaged counts"
    )
