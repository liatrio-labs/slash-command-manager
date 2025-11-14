"""Unit tests for list discovery logic."""

from __future__ import annotations

from pathlib import Path

from slash_commands.list_discovery import discover_managed_prompts


def test_discover_managed_prompts_finds_files_with_managed_by(tmp_path: Path):
    """Test that files with managed_by: slash-man are discovered."""
    # Create cursor agent command directory
    cursor_dir = tmp_path / ".cursor" / "commands"
    cursor_dir.mkdir(parents=True)

    # Create a managed command file
    command_file = cursor_dir / "test-command.md"
    command_file.write_text(
        """---
name: test-command
description: Test command
meta:
  managed_by: slash-man
  version: 1.0.0
---
# Test Command
""",
        encoding="utf-8",
    )

    # Discover managed prompts
    result = discover_managed_prompts(tmp_path, ["cursor"])

    # Verify file was discovered
    assert len(result) == 1
    assert result[0]["name"] == "test-command"
    assert result[0]["agent"] == "cursor"
    assert result[0]["agent_display_name"] == "Cursor"
    assert result[0]["file_path"] == command_file
    assert result[0]["meta"]["managed_by"] == "slash-man"
    assert result[0]["format"] == "markdown"


def test_discover_managed_prompts_excludes_files_without_managed_by(tmp_path: Path):
    """Test that files without managed_by field are excluded from managed results."""
    # Create cursor agent command directory
    cursor_dir = tmp_path / ".cursor" / "commands"
    cursor_dir.mkdir(parents=True)

    # Create a command file WITHOUT managed_by field
    unmanaged_file = cursor_dir / "unmanaged-command.md"
    unmanaged_file.write_text(
        """---
name: unmanaged-command
description: Unmanaged command
meta:
  version: 1.0.0
---
# Unmanaged Command
""",
        encoding="utf-8",
    )

    # Create a managed command file
    managed_file = cursor_dir / "managed-command.md"
    managed_file.write_text(
        """---
name: managed-command
description: Managed command
meta:
  managed_by: slash-man
  version: 1.0.0
---
# Managed Command
""",
        encoding="utf-8",
    )

    # Discover managed prompts
    result = discover_managed_prompts(tmp_path, ["cursor"])

    # Verify only managed file was discovered
    assert len(result) == 1
    assert result[0]["name"] == "managed-command"
    assert result[0]["file_path"] == managed_file


def test_discover_managed_prompts_handles_markdown_format(tmp_path: Path):
    """Test that Markdown format files are handled correctly."""
    # Create cursor agent command directory (Markdown format)
    cursor_dir = tmp_path / ".cursor" / "commands"
    cursor_dir.mkdir(parents=True)

    # Create a managed Markdown command file
    command_file = cursor_dir / "test-markdown.md"
    command_file.write_text(
        """---
name: test-markdown
description: Test Markdown command
meta:
  managed_by: slash-man
---
# Test Markdown
""",
        encoding="utf-8",
    )

    # Discover managed prompts
    result = discover_managed_prompts(tmp_path, ["cursor"])

    # Verify Markdown file was discovered correctly
    assert len(result) == 1
    assert result[0]["format"] == "markdown"
    assert result[0]["name"] == "test-markdown"


def test_discover_managed_prompts_handles_toml_format(tmp_path: Path):
    """Test that TOML format files are handled correctly."""
    # Create gemini-cli agent command directory (TOML format)
    gemini_dir = tmp_path / ".gemini" / "commands"
    gemini_dir.mkdir(parents=True)

    # Create a managed TOML command file
    command_file = gemini_dir / "test-toml.toml"
    command_file.write_text(
        """prompt = "# Test TOML"
description = "Test TOML command"

[meta]
managed_by = "slash-man"
version = "1.0.0"
""",
        encoding="utf-8",
    )

    # Discover managed prompts
    result = discover_managed_prompts(tmp_path, ["gemini-cli"])

    # Verify TOML file was discovered correctly
    assert len(result) == 1
    assert result[0]["format"] == "toml"
    assert result[0]["name"] == "test-toml"
    assert result[0]["meta"]["managed_by"] == "slash-man"


def test_discover_managed_prompts_excludes_backup_files(tmp_path: Path):
    """Test that backup files matching pattern *.{extension}.{timestamp}.bak are excluded."""
    # Create cursor agent command directory
    cursor_dir = tmp_path / ".cursor" / "commands"
    cursor_dir.mkdir(parents=True)

    # Create a managed command file
    command_file = cursor_dir / "test-command.md"
    command_file.write_text(
        """---
name: test-command
description: Test command
meta:
  managed_by: slash-man
---
# Test Command
""",
        encoding="utf-8",
    )

    # Create backup files (matching pattern: filename.{extension}.{timestamp}.bak)
    backup1 = cursor_dir / "test-command.md.20250115-123456.bak"
    backup1.write_text("backup content 1", encoding="utf-8")

    backup2 = cursor_dir / "test-command.md.20250116-234567.bak"
    backup2.write_text("backup content 2", encoding="utf-8")

    # Discover managed prompts
    result = discover_managed_prompts(tmp_path, ["cursor"])

    # Verify backup files are excluded (they don't match *.md glob pattern)
    # Should only find: command_file (1 file)
    assert len(result) == 1
    assert result[0]["name"] == "test-command"
    assert result[0]["file_path"] == command_file

    # Verify backup files exist but weren't discovered
    assert backup1.exists()
    assert backup2.exists()


def test_discover_managed_prompts_handles_empty_directories(tmp_path: Path):
    """Test that empty directories are handled gracefully."""
    # Create cursor agent command directory (empty)
    cursor_dir = tmp_path / ".cursor" / "commands"
    cursor_dir.mkdir(parents=True)

    # Discover managed prompts from empty directory
    result = discover_managed_prompts(tmp_path, ["cursor"])

    # Verify empty result (no errors)
    assert len(result) == 0
    assert isinstance(result, list)


def test_discover_managed_prompts_handles_multiple_agents(tmp_path: Path):
    """Test that multiple agents are discovered correctly."""
    # Create cursor agent command directory
    cursor_dir = tmp_path / ".cursor" / "commands"
    cursor_dir.mkdir(parents=True)

    # Create claude-code agent command directory
    claude_dir = tmp_path / ".claude" / "commands"
    claude_dir.mkdir(parents=True)

    # Create managed command files for each agent
    cursor_file = cursor_dir / "cursor-command.md"
    cursor_file.write_text(
        """---
name: cursor-command
meta:
  managed_by: slash-man
---
# Cursor Command
""",
        encoding="utf-8",
    )

    claude_file = claude_dir / "claude-command.md"
    claude_file.write_text(
        """---
name: claude-command
meta:
  managed_by: slash-man
---
# Claude Command
""",
        encoding="utf-8",
    )

    # Discover managed prompts from multiple agents
    result = discover_managed_prompts(tmp_path, ["cursor", "claude-code"])

    # Verify both agents' files were discovered
    assert len(result) == 2
    file_names = {r["name"] for r in result}
    assert "cursor-command" in file_names
    assert "claude-command" in file_names

    # Verify agent information is correct
    agents = {r["agent"] for r in result}
    assert "cursor" in agents
    assert "claude-code" in agents
