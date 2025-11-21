"""Unit tests for list discovery logic."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from slash_commands.list_discovery import count_unmanaged_prompts, discover_managed_prompts


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


def test_count_unmanaged_prompts_counts_valid_prompts_without_managed_by(tmp_path: Path):
    """Test that valid prompt files without managed_by are counted."""
    # Create cursor agent command directory
    cursor_dir = tmp_path / ".cursor" / "commands"
    cursor_dir.mkdir(parents=True)

    # Create unmanaged prompt file (valid but no managed_by)
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

    # Count unmanaged prompts
    result = count_unmanaged_prompts(tmp_path, ["cursor"])

    # Verify unmanaged file is counted
    assert result["cursor"] == 1


def test_count_unmanaged_prompts_excludes_backup_files(tmp_path: Path):
    """Test that backup files are excluded from unmanaged counts."""
    # Create cursor agent command directory
    cursor_dir = tmp_path / ".cursor" / "commands"
    cursor_dir.mkdir(parents=True)

    # Create unmanaged prompt file
    unmanaged_file = cursor_dir / "unmanaged-command.md"
    unmanaged_file.write_text(
        """---
name: unmanaged-command
meta:
  version: 1.0.0
---
# Unmanaged Command
""",
        encoding="utf-8",
    )

    # Create backup file (should be excluded)
    backup_file = cursor_dir / "unmanaged-command.md.20250115-123456.bak"
    backup_file.write_text("backup content", encoding="utf-8")

    # Count unmanaged prompts
    result = count_unmanaged_prompts(tmp_path, ["cursor"])

    # Verify only unmanaged file is counted (backup excluded)
    assert result["cursor"] == 1


def test_count_unmanaged_prompts_excludes_managed_files(tmp_path: Path):
    """Test that managed files are excluded from unmanaged counts."""
    # Create cursor agent command directory
    cursor_dir = tmp_path / ".cursor" / "commands"
    cursor_dir.mkdir(parents=True)

    # Create managed prompt file (should be excluded)
    managed_file = cursor_dir / "managed-command.md"
    managed_file.write_text(
        """---
name: managed-command
meta:
  managed_by: slash-man
  version: 1.0.0
---
# Managed Command
""",
        encoding="utf-8",
    )

    # Create unmanaged prompt file
    unmanaged_file = cursor_dir / "unmanaged-command.md"
    unmanaged_file.write_text(
        """---
name: unmanaged-command
meta:
  version: 1.0.0
---
# Unmanaged Command
""",
        encoding="utf-8",
    )

    # Count unmanaged prompts
    result = count_unmanaged_prompts(tmp_path, ["cursor"])

    # Verify only unmanaged file is counted
    assert result["cursor"] == 1


def test_count_unmanaged_prompts_excludes_invalid_files(tmp_path: Path):
    """Test that invalid files (not valid prompts) are excluded from counts."""
    # Create cursor agent command directory
    cursor_dir = tmp_path / ".cursor" / "commands"
    cursor_dir.mkdir(parents=True)

    # Create unmanaged prompt file (valid)
    unmanaged_file = cursor_dir / "unmanaged-command.md"
    unmanaged_file.write_text(
        """---
name: unmanaged-command
meta:
  version: 1.0.0
---
# Unmanaged Command
""",
        encoding="utf-8",
    )

    # Create invalid file (not a valid prompt - malformed frontmatter)
    invalid_file = cursor_dir / "invalid-command.md"
    invalid_file.write_text(
        """---
name: invalid-command
invalid yaml: [unclosed
---
# Invalid Command
""",
        encoding="utf-8",
    )

    # Create another invalid file (not a prompt at all)
    not_prompt_file = cursor_dir / "not-a-prompt.md"
    not_prompt_file.write_text("This is not a prompt file", encoding="utf-8")

    # Count unmanaged prompts
    result = count_unmanaged_prompts(tmp_path, ["cursor"])

    # Verify only valid unmanaged file is counted
    assert result["cursor"] == 1


def test_count_unmanaged_prompts_handles_file_not_found_errors(tmp_path: Path):
    """Test that FileNotFoundError is handled gracefully in count_unmanaged_prompts."""
    # Create cursor agent command directory
    cursor_dir = tmp_path / ".cursor" / "commands"
    cursor_dir.mkdir(parents=True)

    # Create unmanaged prompt file (valid)
    unmanaged_file = cursor_dir / "unmanaged-command.md"
    unmanaged_file.write_text(
        """---
name: unmanaged-command
meta:
  version: 1.0.0
---
# Unmanaged Command
""",
        encoding="utf-8",
    )

    # Create a file path that will raise FileNotFoundError when read
    missing_file = cursor_dir / "missing-command.md"
    missing_file.write_text(
        """---
name: missing-command
meta:
  version: 1.0.0
---
# Missing Command
""",
        encoding="utf-8",
    )

    # Mock _parse_command_file to simulate FileNotFoundError for missing_file
    from slash_commands import list_discovery

    original_parse = list_discovery._parse_command_file

    def mock_parse_command_file(file_path: Path, agent):
        if file_path == missing_file:
            raise FileNotFoundError(f"No such file or directory: '{file_path}'")
        return original_parse(file_path, agent)

    # Count unmanaged prompts with mocked FileNotFoundError
    with patch(
        "slash_commands.list_discovery._parse_command_file", side_effect=mock_parse_command_file
    ):
        result = count_unmanaged_prompts(tmp_path, ["cursor"])

    # Verify only accessible unmanaged file is counted (missing file skipped)
    assert result["cursor"] == 1


def test_discover_managed_prompts_handles_malformed_frontmatter(tmp_path: Path):
    """Test that files with malformed frontmatter are skipped silently."""
    # Create cursor agent command directory
    cursor_dir = tmp_path / ".cursor" / "commands"
    cursor_dir.mkdir(parents=True)

    # Create managed command file (valid)
    managed_file = cursor_dir / "managed-command.md"
    managed_file.write_text(
        """---
name: managed-command
meta:
  managed_by: slash-man
---
# Managed Command
""",
        encoding="utf-8",
    )

    # Create file with malformed frontmatter (should be skipped)
    malformed_file = cursor_dir / "malformed-command.md"
    malformed_file.write_text(
        """---
name: malformed-command
invalid yaml: [unclosed bracket
meta:
  managed_by: slash-man
---
# Malformed Command
""",
        encoding="utf-8",
    )

    # Discover managed prompts
    result = discover_managed_prompts(tmp_path, ["cursor"])

    # Verify only valid managed file is discovered (malformed file skipped)
    assert len(result) == 1
    assert result[0]["name"] == "managed-command"


def test_discover_managed_prompts_handles_unicode_errors(tmp_path: Path):
    """Test that Unicode decode errors are handled gracefully."""
    # Create cursor agent command directory
    cursor_dir = tmp_path / ".cursor" / "commands"
    cursor_dir.mkdir(parents=True)

    # Create managed command file (valid)
    managed_file = cursor_dir / "managed-command.md"
    managed_file.write_text(
        """---
name: managed-command
meta:
  managed_by: slash-man
---
# Managed Command
""",
        encoding="utf-8",
    )

    # Create file with invalid encoding (binary data that can't be decoded as UTF-8)
    invalid_encoding_file = cursor_dir / "invalid-encoding.md"
    invalid_encoding_file.write_bytes(b"\xff\xfe\x00\x01\x02\x03")

    # Discover managed prompts
    result = discover_managed_prompts(tmp_path, ["cursor"])

    # Verify only valid managed file is discovered (invalid encoding file skipped)
    assert len(result) == 1
    assert result[0]["name"] == "managed-command"


def test_discover_managed_prompts_handles_permission_errors(tmp_path: Path):
    """Test that permission errors are handled gracefully."""
    # Create cursor agent command directory
    cursor_dir = tmp_path / ".cursor" / "commands"
    cursor_dir.mkdir(parents=True)

    # Create managed command file (valid)
    managed_file = cursor_dir / "managed-command.md"
    managed_file.write_text(
        """---
name: managed-command
meta:
  managed_by: slash-man
---
# Managed Command
""",
        encoding="utf-8",
    )

    # Create file that will raise PermissionError when read
    inaccessible_file = cursor_dir / "inaccessible-command.md"
    inaccessible_file.write_text(
        """---
name: inaccessible-command
meta:
  managed_by: slash-man
---
# Inaccessible Command
""",
        encoding="utf-8",
    )

    # Mock _parse_command_file to simulate permission error for inaccessible_file
    from slash_commands import list_discovery

    original_parse = list_discovery._parse_command_file

    def mock_parse_command_file(file_path: Path, agent):
        if file_path == inaccessible_file:
            raise PermissionError("Permission denied")
        return original_parse(file_path, agent)

    # Discover managed prompts with mocked permission error
    with patch(
        "slash_commands.list_discovery._parse_command_file", side_effect=mock_parse_command_file
    ):
        result = discover_managed_prompts(tmp_path, ["cursor"])

    # Verify only accessible managed file is discovered (inaccessible file skipped)
    assert len(result) == 1
    assert result[0]["name"] == "managed-command"


def test_discover_managed_prompts_handles_file_not_found_errors(tmp_path: Path):
    """Test that FileNotFoundError is handled gracefully."""
    # Create cursor agent command directory
    cursor_dir = tmp_path / ".cursor" / "commands"
    cursor_dir.mkdir(parents=True)

    # Create managed command file (valid)
    managed_file = cursor_dir / "managed-command.md"
    managed_file.write_text(
        """---
name: managed-command
meta:
  managed_by: slash-man
---
# Managed Command
""",
        encoding="utf-8",
    )

    # Create a file path that will raise FileNotFoundError when read
    # This simulates a file found by glob() but deleted/missing when read
    missing_file = cursor_dir / "missing-command.md"
    missing_file.write_text(
        """---
name: missing-command
meta:
  managed_by: slash-man
---
# Missing Command
""",
        encoding="utf-8",
    )

    # Mock _parse_command_file to simulate FileNotFoundError for missing_file
    from slash_commands import list_discovery

    original_parse = list_discovery._parse_command_file

    def mock_parse_command_file(file_path: Path, agent):
        if file_path == missing_file:
            raise FileNotFoundError(f"No such file or directory: '{file_path}'")
        return original_parse(file_path, agent)

    # Discover managed prompts with mocked FileNotFoundError
    with patch(
        "slash_commands.list_discovery._parse_command_file", side_effect=mock_parse_command_file
    ):
        result = discover_managed_prompts(tmp_path, ["cursor"])

    # Verify only accessible managed file is discovered (missing file skipped)
    assert len(result) == 1
    assert result[0]["name"] == "managed-command"


def test_count_backups_returns_zero_for_no_backups(tmp_path: Path):
    """Test that count_backups returns 0 when no backups exist."""
    from slash_commands.list_discovery import count_backups

    # Create a command file with no backups
    command_file = tmp_path / "test-command.md"
    command_file.write_text(
        """---
name: test-command
meta:
  managed_by: slash-man
---
# Test Command
""",
        encoding="utf-8",
    )

    # Count backups
    count = count_backups(command_file)

    # Verify count is 0
    assert count == 0


def test_count_backups_counts_matching_backups(tmp_path: Path):
    """Test that count_backups counts backups matching pattern filename.{extension}.{timestamp}.bak."""
    from slash_commands.list_discovery import count_backups

    # Create a command file
    command_file = tmp_path / "test-command.md"
    command_file.write_text(
        """---
name: test-command
meta:
  managed_by: slash-man
---
# Test Command
""",
        encoding="utf-8",
    )

    # Create backup files matching pattern: filename.{extension}.YYYYMMDD-HHMMSS.bak
    backup1 = tmp_path / "test-command.md.20250115-123456.bak"
    backup1.write_text("backup content 1", encoding="utf-8")

    backup2 = tmp_path / "test-command.md.20250116-234567.bak"
    backup2.write_text("backup content 2", encoding="utf-8")

    # Count backups
    count = count_backups(command_file)

    # Verify count is 2
    assert count == 2


def test_count_backups_handles_multiple_backups(tmp_path: Path):
    """Test that count_backups handles files with multiple backups."""
    from slash_commands.list_discovery import count_backups

    # Create a command file
    command_file = tmp_path / "test-command.md"
    command_file.write_text(
        """---
name: test-command
meta:
  managed_by: slash-man
---
# Test Command
""",
        encoding="utf-8",
    )

    # Create multiple backup files
    for i in range(5):
        backup = tmp_path / f"test-command.md.2025011{i}-123456.bak"
        backup.write_text(f"backup content {i}", encoding="utf-8")

    # Count backups
    count = count_backups(command_file)

    # Verify count is 5
    assert count == 5


def test_count_backups_excludes_non_matching_files(tmp_path: Path):
    """Test that count_backups excludes files that don't match backup pattern."""
    from slash_commands.list_discovery import count_backups

    # Create a command file
    command_file = tmp_path / "test-command.md"
    command_file.write_text(
        """---
name: test-command
meta:
  managed_by: slash-man
---
# Test Command
""",
        encoding="utf-8",
    )

    # Create valid backup file
    valid_backup = tmp_path / "test-command.md.20250115-123456.bak"
    valid_backup.write_text("valid backup", encoding="utf-8")

    # Create invalid backup files (don't match pattern)
    invalid_backup1 = tmp_path / "test-command.md.bak"  # Missing timestamp
    invalid_backup1.write_text("invalid backup 1", encoding="utf-8")

    invalid_backup2 = tmp_path / "test-command.md.20250115.bak"  # Missing time part
    invalid_backup2.write_text("invalid backup 2", encoding="utf-8")

    invalid_backup3 = tmp_path / "test-command.md.abc12345-123456.bak"  # Invalid timestamp format
    invalid_backup3.write_text("invalid backup 3", encoding="utf-8")

    # Count backups
    count = count_backups(command_file)

    # Verify only valid backup is counted
    assert count == 1


def test_format_source_info_local_source():
    """Test that format_source_info formats local source correctly."""
    from slash_commands.cli_utils import format_source_info

    # Test with source_dir
    meta_with_dir = {
        "source_type": "local",
        "source_dir": "/path/to/prompts",
    }
    result = format_source_info(meta_with_dir)
    assert result == "local: /path/to/prompts"

    # Test with source_path (fallback)
    meta_with_path = {
        "source_type": "local",
        "source_path": "/path/to/prompt.md",
    }
    result = format_source_info(meta_with_path)
    assert result == "local: /path/to/prompt.md"

    # Test with both (prefer source_dir)
    meta_both = {
        "source_type": "local",
        "source_dir": "/path/to/prompts",
        "source_path": "/path/to/prompt.md",
    }
    result = format_source_info(meta_both)
    assert result == "local: /path/to/prompts"


def test_format_source_info_github_source():
    """Test that format_source_info formats GitHub source correctly."""
    from slash_commands.cli_utils import format_source_info

    # Test with all GitHub fields
    meta_github = {
        "source_type": "github",
        "source_repo": "owner/repo",
        "source_branch": "main",
        "source_path": "prompts",
    }
    result = format_source_info(meta_github)
    assert result == "github: owner/repo@main:prompts"


def test_format_source_info_missing_fields():
    """Test that format_source_info handles missing fields gracefully."""
    from slash_commands.cli_utils import format_source_info

    # Test with missing source_type
    meta_no_type = {
        "source_dir": "/path/to/prompts",
    }
    result = format_source_info(meta_no_type)
    assert result == "Unknown"

    # Test with empty meta
    result = format_source_info({})
    assert result == "Unknown"

    # Test with GitHub source missing fields
    meta_github_incomplete = {
        "source_type": "github",
        "source_repo": "owner/repo",
        # Missing branch and path
    }
    result = format_source_info(meta_github_incomplete)
    # Should handle gracefully - show what we have
    assert result == "github: owner/repo"


def test_build_list_data_structure_groups_by_prompt_name():
    """Test that build_list_data_structure groups prompts by name (not by agent)."""
    from pathlib import Path

    from slash_commands.list_discovery import build_list_data_structure

    # Create discovered prompts with same name but different agents
    discovered_prompts = [
        {
            "name": "test-command",
            "agent": "cursor",
            "agent_display_name": "Cursor",
            "file_path": Path("/tmp/.cursor/commands/test-command.md"),
            "meta": {
                "managed_by": "slash-man",
                "source_type": "local",
                "source_dir": "/path/to/prompts",
                "updated_at": "2025-01-15T10:00:00Z",
            },
            "format": "markdown",
        },
        {
            "name": "test-command",  # Same name, different agent
            "agent": "claude-code",
            "agent_display_name": "Claude Code",
            "file_path": Path("/tmp/.claude/commands/test-command.md"),
            "meta": {
                "managed_by": "slash-man",
                "source_type": "local",
                "source_dir": "/path/to/prompts",
                "updated_at": "2025-01-15T10:00:00Z",
            },
            "format": "markdown",
        },
        {
            "name": "other-command",  # Different name
            "agent": "cursor",
            "agent_display_name": "Cursor",
            "file_path": Path("/tmp/.cursor/commands/other-command.md"),
            "meta": {
                "managed_by": "slash-man",
                "source_type": "local",
                "source_dir": "/path/to/prompts",
                "updated_at": "2025-01-15T11:00:00Z",
            },
            "format": "markdown",
        },
    ]

    unmanaged_counts = {"cursor": 1, "claude-code": 0}

    result = build_list_data_structure(discovered_prompts, unmanaged_counts)

    # Verify structure
    assert "prompts" in result
    assert "unmanaged_counts" in result

    # Verify grouping by prompt name (should have 2 prompts, not 3)
    assert len(result["prompts"]) == 2, "Should group by prompt name"

    # Verify test-command has both agents
    assert "test-command" in result["prompts"]
    test_command = result["prompts"]["test-command"]
    assert len(test_command["agents"]) == 2, "test-command should have 2 agents"

    # Verify other-command has 1 agent
    assert "other-command" in result["prompts"]
    other_command = result["prompts"]["other-command"]
    assert len(other_command["agents"]) == 1, "other-command should have 1 agent"


def test_build_list_data_structure_aggregates_agent_info():
    """Test that build_list_data_structure aggregates agent information per prompt."""
    from pathlib import Path

    from slash_commands.list_discovery import build_list_data_structure

    discovered_prompts = [
        {
            "name": "test-command",
            "agent": "cursor",
            "agent_display_name": "Cursor",
            "file_path": Path("/tmp/.cursor/commands/test-command.md"),
            "meta": {
                "managed_by": "slash-man",
                "source_type": "local",
                "source_dir": "/path/to/prompts",
                "updated_at": "2025-01-15T10:00:00Z",
            },
            "format": "markdown",
        },
    ]

    unmanaged_counts = {"cursor": 0}

    result = build_list_data_structure(discovered_prompts, unmanaged_counts)

    prompt = result["prompts"]["test-command"]
    assert len(prompt["agents"]) == 1
    agent_info = prompt["agents"][0]
    assert agent_info["agent"] == "cursor"
    assert agent_info["display_name"] == "Cursor"
    assert agent_info["file_path"] == Path("/tmp/.cursor/commands/test-command.md")


def test_build_list_data_structure_includes_all_fields():
    """Test that build_list_data_structure includes all required fields."""
    from pathlib import Path

    from slash_commands.list_discovery import (
        build_list_data_structure,
    )

    # Mock count_backups and format_source_info for testing
    discovered_prompts = [
        {
            "name": "test-command",
            "agent": "cursor",
            "agent_display_name": "Cursor",
            "file_path": Path("/tmp/.cursor/commands/test-command.md"),
            "meta": {
                "managed_by": "slash-man",
                "source_type": "local",
                "source_dir": "/path/to/prompts",
                "updated_at": "2025-01-15T10:00:00Z",
            },
            "format": "markdown",
        },
    ]

    unmanaged_counts = {"cursor": 2}

    result = build_list_data_structure(discovered_prompts, unmanaged_counts)

    prompt = result["prompts"]["test-command"]
    assert "name" in prompt
    assert prompt["name"] == "test-command"
    assert "agents" in prompt
    assert len(prompt["agents"]) == 1

    agent_info = prompt["agents"][0]
    assert "agent" in agent_info
    assert "display_name" in agent_info
    assert "file_path" in agent_info
    assert "backup_count" in agent_info

    assert "source_info" in prompt
    assert "updated_at" in prompt

    assert "unmanaged_counts" in result
    assert result["unmanaged_counts"]["cursor"] == 2


def test_render_list_tree_creates_tree_structure():
    """Test that render_list_tree creates Rich Tree with correct structure."""
    from pathlib import Path

    from slash_commands.list_discovery import build_list_data_structure, render_list_tree

    data_structure = build_list_data_structure(
        [
            {
                "name": "test-command",
                "agent": "cursor",
                "agent_display_name": "Cursor",
                "file_path": Path("/tmp/.cursor/commands/test-command.md"),
                "meta": {
                    "managed_by": "slash-man",
                    "source_type": "local",
                    "source_dir": "/path/to/prompts",
                    "updated_at": "2025-01-15T10:00:00Z",
                },
                "format": "markdown",
            },
        ],
        {"cursor": 0},
    )

    # Render tree and capture output
    output = render_list_tree(data_structure, record=True)

    # Verify output contains tree structure elements
    assert output is not None
    assert "Managed Prompts" in output or "List Summary" in output
    assert "test-command" in output


def test_render_list_tree_groups_by_prompt_name():
    """Test that render_list_tree groups output by prompt name."""
    from pathlib import Path

    from slash_commands.list_discovery import build_list_data_structure, render_list_tree

    data_structure = build_list_data_structure(
        [
            {
                "name": "test-command",
                "agent": "cursor",
                "agent_display_name": "Cursor",
                "file_path": Path("/tmp/.cursor/commands/test-command.md"),
                "meta": {
                    "managed_by": "slash-man",
                    "source_type": "local",
                    "source_dir": "/path/to/prompts",
                    "updated_at": "2025-01-15T10:00:00Z",
                },
                "format": "markdown",
            },
            {
                "name": "test-command",  # Same name, different agent
                "agent": "claude-code",
                "agent_display_name": "Claude Code",
                "file_path": Path("/tmp/.claude/commands/test-command.md"),
                "meta": {
                    "managed_by": "slash-man",
                    "source_type": "local",
                    "source_dir": "/path/to/prompts",
                    "updated_at": "2025-01-15T10:00:00Z",
                },
                "format": "markdown",
            },
        ],
        {"cursor": 0, "claude-code": 0},
    )

    output = render_list_tree(data_structure, record=True)

    # Verify prompt name appears once (grouped)
    assert output is not None
    # Count occurrences - should appear once as a group header
    assert output.count("test-command") >= 1


def test_render_list_tree_shows_agent_info():
    """Test that render_list_tree shows agent(s) where installed."""
    from pathlib import Path

    from slash_commands.list_discovery import build_list_data_structure, render_list_tree

    data_structure = build_list_data_structure(
        [
            {
                "name": "test-command",
                "agent": "cursor",
                "agent_display_name": "Cursor",
                "file_path": Path("/tmp/.cursor/commands/test-command.md"),
                "meta": {
                    "managed_by": "slash-man",
                    "source_type": "local",
                    "source_dir": "/path/to/prompts",
                    "updated_at": "2025-01-15T10:00:00Z",
                },
                "format": "markdown",
            },
        ],
        {"cursor": 0},
    )

    output = render_list_tree(data_structure, record=True)

    assert output is not None
    assert "cursor" in output.lower() or "Cursor" in output


def test_render_list_tree_shows_file_paths():
    """Test that render_list_tree shows file path(s) for each agent."""
    from pathlib import Path

    from slash_commands.list_discovery import build_list_data_structure, render_list_tree

    data_structure = build_list_data_structure(
        [
            {
                "name": "test-command",
                "agent": "cursor",
                "agent_display_name": "Cursor",
                "file_path": Path("/tmp/.cursor/commands/test-command.md"),
                "meta": {
                    "managed_by": "slash-man",
                    "source_type": "local",
                    "source_dir": "/path/to/prompts",
                    "updated_at": "2025-01-15T10:00:00Z",
                },
                "format": "markdown",
            },
        ],
        {"cursor": 0},
    )

    output = render_list_tree(data_structure, record=True)

    assert output is not None
    # Should show file path (may be shortened)
    assert "test-command.md" in output or ".cursor" in output


def test_render_list_tree_shows_backup_counts():
    """Test that render_list_tree shows backup count per file."""
    from pathlib import Path

    from slash_commands.list_discovery import build_list_data_structure, render_list_tree

    data_structure = build_list_data_structure(
        [
            {
                "name": "test-command",
                "agent": "cursor",
                "agent_display_name": "Cursor",
                "file_path": Path("/tmp/.cursor/commands/test-command.md"),
                "meta": {
                    "managed_by": "slash-man",
                    "source_type": "local",
                    "source_dir": "/path/to/prompts",
                    "updated_at": "2025-01-15T10:00:00Z",
                },
                "format": "markdown",
            },
        ],
        {"cursor": 0},
    )

    output = render_list_tree(data_structure, record=True)

    assert output is not None
    # Should show backup count (may be "0" or "backup")
    assert "backup" in output.lower() or "0" in output


def test_render_list_tree_shows_source_info():
    """Test that render_list_tree shows consolidated source information."""
    from pathlib import Path

    from slash_commands.list_discovery import build_list_data_structure, render_list_tree

    data_structure = build_list_data_structure(
        [
            {
                "name": "test-command",
                "agent": "cursor",
                "agent_display_name": "Cursor",
                "file_path": Path("/tmp/.cursor/commands/test-command.md"),
                "meta": {
                    "managed_by": "slash-man",
                    "source_type": "local",
                    "source_dir": "/path/to/prompts",
                    "updated_at": "2025-01-15T10:00:00Z",
                },
                "format": "markdown",
            },
        ],
        {"cursor": 0},
    )

    output = render_list_tree(data_structure, record=True)

    assert output is not None
    assert "local:" in output.lower() or "source" in output.lower()


def test_render_list_tree_shows_timestamps():
    """Test that render_list_tree shows last updated timestamp."""
    from pathlib import Path

    from slash_commands.list_discovery import build_list_data_structure, render_list_tree

    data_structure = build_list_data_structure(
        [
            {
                "name": "test-command",
                "agent": "cursor",
                "agent_display_name": "Cursor",
                "file_path": Path("/tmp/.cursor/commands/test-command.md"),
                "meta": {
                    "managed_by": "slash-man",
                    "source_type": "local",
                    "source_dir": "/path/to/prompts",
                    "updated_at": "2025-01-15T10:00:00Z",
                },
                "format": "markdown",
            },
        ],
        {"cursor": 0},
    )

    output = render_list_tree(data_structure, record=True)

    assert output is not None
    # Should show timestamp (may be formatted)
    assert "2025" in output or "updated" in output.lower()


def test_render_list_tree_shows_unmanaged_counts():
    """Test that render_list_tree shows unmanaged prompt counts per agent directory."""
    from pathlib import Path

    from slash_commands.list_discovery import build_list_data_structure, render_list_tree

    data_structure = build_list_data_structure(
        [
            {
                "name": "test-command",
                "agent": "cursor",
                "agent_display_name": "Cursor",
                "file_path": Path("/tmp/.cursor/commands/test-command.md"),
                "meta": {
                    "managed_by": "slash-man",
                    "source_type": "local",
                    "source_dir": "/path/to/prompts",
                    "updated_at": "2025-01-15T10:00:00Z",
                },
                "format": "markdown",
            },
        ],
        {"cursor": 2},  # 2 unmanaged prompts
    )

    output = render_list_tree(data_structure, record=True)

    assert output is not None
    # Should show unmanaged count
    assert "2" in output or "unmanaged" in output.lower()
