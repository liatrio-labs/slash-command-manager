"""Tests for single overwrite prompt behavior."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from slash_commands.cli import app


@pytest.fixture
def mock_prompts_dir(tmp_path):
    """Create a temporary prompts directory with multiple test prompts."""
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()

    # Create multiple test prompts
    for prompt_name in ["prompt1.md", "prompt2.md", "prompt3.md"]:
        prompt_file = prompts_dir / prompt_name
        prompt_file.write_text(
            f"""---
name: {prompt_name[:-3]}
description: Test prompt {prompt_name[:-3]}
tags:
  - testing
arguments: []
enabled: true
---
# Test Prompt {prompt_name[:-3]}

This is test prompt {prompt_name[:-3]}.
"""
        )

    return prompts_dir


def test_single_prompt_for_all_existing_files(mock_prompts_dir, tmp_path):
    """Test that existing files prompt only once for all files, not per file."""
    # Create existing files for multiple agents and prompts
    existing_files = []

    # Create files for claude-code agent
    claude_dir = tmp_path / ".claude" / "commands"
    claude_dir.mkdir(parents=True, exist_ok=True)

    for prompt_name in ["prompt1.md", "prompt2.md", "prompt3.md"]:
        file_path = claude_dir / prompt_name
        file_path.write_text("existing content")
        existing_files.append(file_path)

    # Create files for gemini-cli agent
    gemini_dir = tmp_path / ".gemini" / "commands"
    gemini_dir.mkdir(parents=True, exist_ok=True)

    for prompt_name in ["prompt1.toml", "prompt2.toml", "prompt3.toml"]:
        file_path = gemini_dir / prompt_name
        file_path.write_text("existing content")
        existing_files.append(file_path)

    runner = CliRunner()

    # Track how many times the overwrite prompt is called
    with patch(
        "slash_commands.writer.SlashCommandWriter._prompt_for_all_existing_files"
    ) as mock_prompt:
        mock_prompt.return_value = "backup"

        result = runner.invoke(
            app,
            [
                "generate",
                "--prompts-dir",
                str(mock_prompts_dir),
                "--agent",
                "claude-code",
                "--agent",
                "gemini-cli",
                "--target-path",
                str(tmp_path),
            ],
        )

        # Should succeed
        assert result.exit_code == 0

        # The prompt should only be called ONCE, not 6 times (once per file)
        assert mock_prompt.call_count == 1, f"Expected 1 prompt call, got {mock_prompt.call_count}"

        # All files should be backed up and overwritten
        for file_path in existing_files:
            # Check that backup files were created
            backup_files = list(file_path.parent.glob(f"{file_path.name}.*.bak"))
            assert len(backup_files) > 0, f"No backup found for {file_path}"

            # Check that new content was written
            assert "Test Prompt" in file_path.read_text()


def test_single_prompt_cancel_cancels_all(mock_prompts_dir, tmp_path):
    """Test that cancelling the single prompt cancels the entire operation."""
    # Create existing files
    claude_dir = tmp_path / ".claude" / "commands"
    claude_dir.mkdir(parents=True, exist_ok=True)

    for prompt_name in ["prompt1.md", "prompt2.md"]:
        file_path = claude_dir / prompt_name
        file_path.write_text("existing content")

    runner = CliRunner()

    with patch(
        "slash_commands.writer.SlashCommandWriter._prompt_for_all_existing_files"
    ) as mock_prompt:
        mock_prompt.return_value = "cancel"

        result = runner.invoke(
            app,
            [
                "generate",
                "--prompts-dir",
                str(mock_prompts_dir),
                "--agent",
                "claude-code",
                "--target-path",
                str(tmp_path),
            ],
        )

        # Should exit with code 1 (user cancellation)
        assert result.exit_code == 1

        # Should only prompt once
        assert mock_prompt.call_count == 1

        # Files should remain unchanged
        for prompt_name in ["prompt1.md", "prompt2.md"]:
            file_path = claude_dir / prompt_name
            assert file_path.read_text() == "existing content"


def test_single_prompt_skip_backups_applies_to_all(mock_prompts_dir, tmp_path):
    """Test that the skip backups choice applies to all existing files."""
    # Create existing files
    claude_dir = tmp_path / ".claude" / "commands"
    claude_dir.mkdir(parents=True, exist_ok=True)

    for prompt_name in ["prompt1.md", "prompt2.md", "prompt3.md"]:
        file_path = claude_dir / prompt_name
        file_path.write_text("existing content")

    runner = CliRunner()

    with patch(
        "slash_commands.writer.SlashCommandWriter._prompt_for_all_existing_files"
    ) as mock_prompt:
        mock_prompt.return_value = "skip-backups"

        result = runner.invoke(
            app,
            [
                "generate",
                "--prompts-dir",
                str(mock_prompts_dir),
                "--agent",
                "claude-code",
                "--target-path",
                str(tmp_path),
            ],
        )

        # Should succeed
        assert result.exit_code == 0

        # Should only prompt once
        assert mock_prompt.call_count == 1

        # All files should be overwritten without backups
        for prompt_name in ["prompt1.md", "prompt2.md", "prompt3.md"]:
            file_path = claude_dir / prompt_name
            assert "Test Prompt" in file_path.read_text()

            # No backup files should be created
            backup_files = list(file_path.parent.glob(f"{file_path.name}.*.bak"))
            assert len(backup_files) == 0
