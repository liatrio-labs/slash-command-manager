"""Integration tests for list command."""

import subprocess
from datetime import UTC, datetime

from slash_commands.cli_utils import format_source_info
from slash_commands.list_discovery import (
    build_list_data_structure,
    count_backups,
    count_unmanaged_prompts,
    discover_managed_prompts,
    render_list_tree,
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
    """Test that source information is formatted correctly for local sources."""
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


def test_list_command_executes_successfully(temp_test_dir, test_prompts_dir):
    """Test that list command executes successfully."""
    # Generate a managed prompt first
    cmd_generate = get_slash_man_command() + [
        "generate",
        "--prompts-dir",
        str(test_prompts_dir),
        "--agent",
        "claude-code",
        "--target-path",
        str(temp_test_dir),
        "--yes",
    ]
    result_generate = subprocess.run(
        cmd_generate,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result_generate.returncode == 0, f"Failed to generate prompt: {result_generate.stderr}"

    # Run list command
    cmd_list = get_slash_man_command() + [
        "list",
        "--target-path",
        str(temp_test_dir),
        "--detection-path",
        str(temp_test_dir),
    ]
    result_list = subprocess.run(
        cmd_list,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    # Verify exit code is 0
    assert result_list.returncode == 0, (
        f"List command failed with exit code {result_list.returncode}: {result_list.stderr}"
    )

    # Verify output contains expected elements
    assert "Managed Prompts" in result_list.stdout or "List Summary" in result_list.stdout, (
        "Output should contain tree structure"
    )


def test_list_agent_flag_filters_results(temp_test_dir, test_prompts_dir):
    """Test that --agent flag filters results to only specified agent."""
    # Generate prompts for multiple agents
    agents = ["cursor", "claude-code"]

    for agent in agents:
        cmd_generate = get_slash_man_command() + [
            "generate",
            "--prompts-dir",
            str(test_prompts_dir),
            "--agent",
            agent,
            "--target-path",
            str(temp_test_dir),
            "--yes",
        ]
        result_generate = subprocess.run(
            cmd_generate,
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result_generate.returncode == 0, (
            f"Failed to generate for {agent}: {result_generate.stderr}"
        )

    # Run list with --agent cursor filter
    cmd_list = get_slash_man_command() + [
        "list",
        "--agent",
        "cursor",
        "--target-path",
        str(temp_test_dir),
        "--detection-path",
        str(temp_test_dir),
    ]
    result_list = subprocess.run(
        cmd_list,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    assert result_list.returncode == 0, f"List command failed: {result_list.stderr}"
    # Should only show cursor prompts
    assert "cursor" in result_list.stdout.lower()
    # Should not show claude-code prompts (or show fewer)
    # Since prompts are grouped by name, we check that cursor is present
    assert "claude" not in result_list.stdout.lower() or result_list.stdout.count(
        "cursor"
    ) > result_list.stdout.count("claude")


def test_list_target_path_flag(temp_test_dir, test_prompts_dir):
    """Test that --target-path flag modifies search location."""
    # Generate prompt in temp_test_dir
    cmd_generate = get_slash_man_command() + [
        "generate",
        "--prompts-dir",
        str(test_prompts_dir),
        "--agent",
        "claude-code",
        "--target-path",
        str(temp_test_dir),
        "--yes",
    ]
    result_generate = subprocess.run(
        cmd_generate,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result_generate.returncode == 0, f"Failed to generate: {result_generate.stderr}"

    # Run list with --target-path pointing to temp_test_dir
    cmd_list = get_slash_man_command() + [
        "list",
        "--agent",
        "claude-code",
        "--target-path",
        str(temp_test_dir),
        "--detection-path",
        str(temp_test_dir),
    ]
    result_list = subprocess.run(
        cmd_list,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    assert result_list.returncode == 0, f"List command failed: {result_list.stderr}"
    assert "Managed Prompts" in result_list.stdout or "List Summary" in result_list.stdout


def test_list_detection_path_flag(temp_test_dir, test_prompts_dir):
    """Test that --detection-path flag modifies detection location."""
    # Generate prompt
    cmd_generate = get_slash_man_command() + [
        "generate",
        "--prompts-dir",
        str(test_prompts_dir),
        "--agent",
        "claude-code",
        "--target-path",
        str(temp_test_dir),
        "--yes",
    ]
    result_generate = subprocess.run(
        cmd_generate,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result_generate.returncode == 0, f"Failed to generate: {result_generate.stderr}"

    # Run list with --detection-path pointing to temp_test_dir
    cmd_list = get_slash_man_command() + [
        "list",
        "--target-path",
        str(temp_test_dir),
        "--detection-path",
        str(temp_test_dir),
    ]
    result_list = subprocess.run(
        cmd_list,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    assert result_list.returncode == 0, f"List command failed: {result_list.stderr}"


def test_list_multiple_agent_flags(temp_test_dir, test_prompts_dir):
    """Test that multiple --agent flags work correctly."""
    # Generate prompts for multiple agents
    agents = ["cursor", "claude-code"]

    for agent in agents:
        cmd_generate = get_slash_man_command() + [
            "generate",
            "--prompts-dir",
            str(test_prompts_dir),
            "--agent",
            agent,
            "--target-path",
            str(temp_test_dir),
            "--yes",
        ]
        result_generate = subprocess.run(
            cmd_generate,
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result_generate.returncode == 0, (
            f"Failed to generate for {agent}: {result_generate.stderr}"
        )

    # Run list with multiple --agent flags
    cmd_list = get_slash_man_command() + [
        "list",
        "--agent",
        "cursor",
        "--agent",
        "claude-code",
        "--target-path",
        str(temp_test_dir),
        "--detection-path",
        str(temp_test_dir),
    ]
    result_list = subprocess.run(
        cmd_list,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    assert result_list.returncode == 0, f"List command failed: {result_list.stderr}"
    # Should show prompts from both agents
    assert "cursor" in result_list.stdout.lower()
    assert "claude" in result_list.stdout.lower()


def test_list_empty_state(temp_test_dir):
    """Test that list command shows informative empty state message."""
    # Run list in a directory with no managed prompts
    cmd_list = get_slash_man_command() + [
        "list",
        "--target-path",
        str(temp_test_dir),
        "--detection-path",
        str(temp_test_dir),
        "--agent",
        "claude-code",  # Specify agent to avoid detection issues
    ]
    result_list = subprocess.run(
        cmd_list,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    # Should exit with code 0 (success, not error)
    assert result_list.returncode == 0, (
        f"Empty state should exit with code 0, got {result_list.returncode}: {result_list.stderr}"
    )

    # Should show informative message
    assert (
        "No managed prompts found" in result_list.stdout
        or "managed_by" in result_list.stdout.lower()
    )
    assert (
        "older versions" in result_list.stdout.lower()
        or "regenerated" in result_list.stdout.lower()
    )
