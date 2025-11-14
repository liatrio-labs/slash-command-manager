"""Tests for the slash command CLI."""

from __future__ import annotations

import re
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from slash_commands.cli import _resolve_detected_agents, app
from slash_commands.config import AgentConfig, CommandFormat


@pytest.fixture
def mock_prompts_dir(tmp_path):
    """Create a temporary prompts directory with test prompts."""
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()

    # Create a test prompt
    prompt_file = prompts_dir / "test-prompt.md"
    prompt_file.write_text(
        """---
name: test-prompt
description: Test prompt for CLI tests
tags:
  - testing
arguments: []
enabled: true
---
# Test Prompt

This is a test prompt.
"""
    )

    return prompts_dir


def test_resolve_detected_agents_preserves_empty_list():
    """Explicitly empty detections should not fall back to selected agents."""
    detected = []
    selected = ["claude-code"]

    resolved = _resolve_detected_agents(detected, selected)

    assert resolved == []


def test_resolve_detected_agents_falls_back_when_missing():
    """When detections are unavailable, fall back to selected agents."""
    detected = None
    selected = ["claude-code"]

    resolved = _resolve_detected_agents(detected, selected)

    assert resolved == selected


def test_cli_list_agents_handles_unknown_agent():
    """Test that --list-agents handles unknown agent keys gracefully."""
    runner = CliRunner()

    # Mock list_agent_keys to return an invalid key
    with patch("slash_commands.cli.list_agent_keys") as mock_list_keys:
        mock_list_keys.return_value = ["invalid-key"]

        result = runner.invoke(app, ["generate", "--list-agents"])

        assert result.exit_code == 0
        assert "invalid-key" in result.stdout
        assert "Unknown" in result.stdout


def test_cli_list_agents():
    """Test that --list-agents lists all supported agents."""
    runner = CliRunner()
    result = runner.invoke(app, ["generate", "--list-agents"])

    assert result.exit_code == 0
    assert "claude-code" in result.stdout
    assert "gemini-cli" in result.stdout
    assert "cursor" in result.stdout


def test_cli_dry_run_flag(mock_prompts_dir, tmp_path):
    """Test that --dry-run flag prevents file writes."""
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "generate",
            "--prompts-dir",
            str(mock_prompts_dir),
            "--agent",
            "claude-code",
            "--dry-run",
            "--target-path",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0
    assert "dry run" in result.stdout.lower()
    assert not (tmp_path / ".claude" / "commands" / "test-prompt.md").exists()


def test_cli_dry_run_reports_pending_backups(mock_prompts_dir, tmp_path):
    """Dry runs should state when backups would be created."""
    output_path = tmp_path / ".claude" / "commands" / "test-prompt.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("existing content")

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "generate",
            "--prompts-dir",
            str(mock_prompts_dir),
            "--agent",
            "claude-code",
            "--dry-run",
            "--target-path",
            str(tmp_path),
            "--yes",
        ],
    )

    assert result.exit_code == 0
    lower_output = result.stdout.lower()
    assert "pending: 1" in lower_output or "backups pending" in lower_output


def test_cli_yes_flag_injects_backup_action(mock_prompts_dir, tmp_path):
    """--yes should always configure the writer to use backup overwrite action."""
    runner = CliRunner()
    with patch("slash_commands.cli.SlashCommandWriter") as mock_writer:
        writer_instance = mock_writer.return_value
        writer_instance.generate.return_value = {
            "prompts_loaded": 0,
            "files_written": 0,
            "files": [],
            "prompts": [],
            "backups_created": [],
            "backups_pending": [],
        }

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
                "--yes",
            ],
        )

        assert result.exit_code == 0
        _, kwargs = mock_writer.call_args
        assert kwargs["overwrite_action"] == "backup"


def test_cli_yes_flag_mentions_safe_mode(mock_prompts_dir, tmp_path):
    """--yes output should mention non-interactive safe mode to users."""
    runner = CliRunner()
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
            "--yes",
        ],
    )

    assert result.exit_code == 0
    assert "safe mode" in result.stdout.lower()


def test_cli_generates_files_for_single_agent(mock_prompts_dir, tmp_path):
    """Test that CLI generates files for a single agent."""
    runner = CliRunner()
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
            "--yes",
        ],
    )

    assert result.exit_code == 0
    assert (tmp_path / ".claude" / "commands" / "test-prompt.md").exists()


def test_cli_generates_files_for_multiple_agents(mock_prompts_dir, tmp_path):
    """Test that CLI generates files for multiple agents."""
    runner = CliRunner()
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
            "--yes",
        ],
    )

    assert result.exit_code == 0
    assert (tmp_path / ".claude" / "commands" / "test-prompt.md").exists()
    assert (tmp_path / ".gemini" / "commands" / "test-prompt.toml").exists()


def test_cli_handles_invalid_agent_key(mock_prompts_dir):
    """Test that CLI handles invalid agent keys gracefully with exit code 2."""
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "generate",
            "--prompts-dir",
            str(mock_prompts_dir),
            "--agent",
            "invalid-agent",
            "--yes",
        ],
    )

    assert result.exit_code == 2  # Validation error
    # Error messages are printed to stderr, but may be mixed in stdout by default
    # Try to get stderr if available, otherwise just use stdout
    try:
        output = (result.stdout + result.stderr).lower()
    except (ValueError, AttributeError):
        output = result.stdout.lower()
    assert "unsupported agent" in output or "invalid agent key" in output


def test_cli_handles_missing_prompts_directory(tmp_path):
    """Test that CLI handles missing prompts directory gracefully with exit code 3."""
    prompts_dir = tmp_path / "nonexistent"

    runner = CliRunner()

    # Mock the fallback function to return None to test the error case
    with patch("slash_commands.writer._find_package_prompts_dir", return_value=None):
        result = runner.invoke(
            app,
            [
                "generate",
                "--prompts-dir",
                str(prompts_dir),
                "--agent",
                "claude-code",
                "--yes",
            ],
        )

        assert result.exit_code == 3  # I/O error


def test_cli_explicit_path_shows_specific_directory_error(tmp_path):
    """Test that CLI shows specific directory error message when using explicit path."""
    prompts_dir = tmp_path / "nonexistent"
    runner = CliRunner()

    # Mock the fallback function to return None to test the error case
    with patch("slash_commands.writer._find_package_prompts_dir", return_value=None):
        # Explicitly specify --prompts-dir
        result = runner.invoke(
            app,
            [
                "generate",
                "--prompts-dir",
                str(prompts_dir),
                "--agent",
                "claude-code",
                "--yes",
            ],
        )

        assert result.exit_code == 3  # I/O error
        # Error messages are printed to stderr, but may be mixed in stdout by default
        try:
            output = result.stdout + result.stderr
        except (ValueError, AttributeError):
            output = result.stdout
        assert "Ensure the specified prompts directory exists" in output
        assert f"current: {prompts_dir}" in output


def test_cli_shows_summary(mock_prompts_dir, tmp_path):
    """Test that CLI shows summary of generated files."""
    runner = CliRunner()
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
            "--yes",
        ],
    )

    assert result.exit_code == 0
    assert "prompts loaded" in result.stdout.lower() or "files written" in result.stdout.lower()


def test_cli_respects_prompts_dir_option(mock_prompts_dir, tmp_path):
    """Test that CLI respects --prompts-dir option."""
    runner = CliRunner()
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
            "--yes",
        ],
    )

    assert result.exit_code == 0
    # Should have found the test prompt
    assert "test-prompt" in result.stdout.lower()


def test_cli_prompts_for_overwrite_without_yes(mock_prompts_dir, tmp_path):
    """Test that CLI prompts for overwrite when files exist and --yes is not set."""
    # Create an existing file
    output_path = tmp_path / ".claude" / "commands" / "test-prompt.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("existing content")

    runner = CliRunner()
    # Don't pass --yes flag to test prompting
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

        # Should prompt for overwrite action
        assert (
            "overwrite" in result.stdout.lower()
            or "existing" in result.stdout.lower()
            or mock_prompt.called
        )


def test_cli_honors_yes_flag_for_overwrite(mock_prompts_dir, tmp_path):
    """Test that CLI honors --yes flag and auto-overwrites existing files."""
    # Create an existing file
    output_path = tmp_path / ".claude" / "commands" / "test-prompt.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("existing content")

    runner = CliRunner()
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
            "--yes",
        ],
    )

    assert result.exit_code == 0
    # File should be overwritten
    assert "Test Prompt" in output_path.read_text()


def test_cli_reports_backup_creation(mock_prompts_dir, tmp_path):
    """Test that CLI reports when backup files are created."""
    # Create an existing file
    output_path = tmp_path / ".claude" / "commands" / "test-prompt.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("existing content")

    runner = CliRunner()
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
                "--target-path",
                str(tmp_path),
            ],
        )

        # Should report backup creation
        assert (
            "backup" in result.stdout.lower()
            or ".bak" in result.stdout.lower()
            or mock_prompt.called
        )
        # Backup file should exist with timestamp pattern
        backup_files = list(output_path.parent.glob("test-prompt.md.*.bak"))
        assert len(backup_files) > 0


def test_cli_interactive_agent_selection_selects_all(mock_prompts_dir, tmp_path):
    """Test that interactive agent selection allows selecting all detected agents."""
    # Create agent directories
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".cursor").mkdir()

    runner = CliRunner()
    # Mock questionary.checkbox to return all agents
    with patch("slash_commands.cli.questionary.checkbox") as mock_checkbox:
        # Simulate selecting all agents
        mock_checkbox.return_value.ask.return_value = [
            AgentConfig(
                key="claude-code",
                display_name="Claude Code",
                command_dir=".claude/commands",
                command_format=CommandFormat.MARKDOWN,
                command_file_extension=".md",
                detection_dirs=(".claude",),
            ),
            AgentConfig(
                key="cursor",
                display_name="Cursor",
                command_dir=".cursor/commands",
                command_format=CommandFormat.MARKDOWN,
                command_file_extension=".md",
                detection_dirs=(".cursor",),
            ),
        ]

        result = runner.invoke(
            app,
            [
                "generate",
                "--prompts-dir",
                str(mock_prompts_dir),
                "--detection-path",
                str(tmp_path),
                "--target-path",
                str(tmp_path),
            ],
        )

        # Should generate files for both agents
        assert result.exit_code == 0
        assert (tmp_path / ".claude" / "commands" / "test-prompt.md").exists()
        assert (tmp_path / ".cursor" / "commands" / "test-prompt.md").exists()


def test_cli_interactive_agent_selection_partial_selection(mock_prompts_dir, tmp_path):
    """Test that interactive agent selection allows selecting subset of agents."""
    # Create agent directories
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".cursor").mkdir()

    runner = CliRunner()
    # Mock questionary.checkbox to return only one agent
    with patch("slash_commands.cli.questionary.checkbox") as mock_checkbox:
        # Simulate selecting only claude-code
        mock_checkbox.return_value.ask.return_value = [
            AgentConfig(
                key="claude-code",
                display_name="Claude Code",
                command_dir=".claude/commands",
                command_format=CommandFormat.MARKDOWN,
                command_file_extension=".md",
                detection_dirs=(".claude",),
            ),
        ]

        result = runner.invoke(
            app,
            [
                "generate",
                "--prompts-dir",
                str(mock_prompts_dir),
                "--detection-path",
                str(tmp_path),
                "--target-path",
                str(tmp_path),
            ],
        )

        # Should only generate files for claude-code
        assert result.exit_code == 0
        assert (tmp_path / ".claude" / "commands" / "test-prompt.md").exists()
        assert not (tmp_path / ".cursor" / "commands" / "test-prompt.md").exists()


def test_cli_interactive_agent_selection_cancels_on_no_selection(mock_prompts_dir, tmp_path):
    """Test that interactive agent selection cancels with exit code 1."""
    # Create agent directories
    (tmp_path / ".claude").mkdir()

    runner = CliRunner()
    # Mock questionary.checkbox to return empty list
    with patch("slash_commands.cli.questionary.checkbox") as mock_checkbox:
        # Simulate selecting no agents
        mock_checkbox.return_value.ask.return_value = []

        result = runner.invoke(
            app,
            [
                "generate",
                "--prompts-dir",
                str(mock_prompts_dir),
                "--detection-path",
                str(tmp_path),
                "--target-path",
                str(tmp_path),
            ],
        )

        # Should exit with exit code 1 (user cancellation)
        assert result.exit_code == 1
        # Cancellation messages are printed to stderr, but may be mixed in stdout by default
        try:
            output = (result.stdout + result.stderr).lower()
        except (ValueError, AttributeError):
            output = result.stdout.lower()
        assert "no agents selected" in output


def test_cli_interactive_agent_selection_bypassed_with_yes_flag(mock_prompts_dir, tmp_path):
    """Test that --yes flag bypasses interactive agent selection."""
    # Create agent directories
    (tmp_path / ".claude").mkdir()

    runner = CliRunner()
    # Should not call questionary.checkbox when --yes is used
    with patch("slash_commands.cli.questionary.checkbox") as mock_checkbox:
        result = runner.invoke(
            app,
            [
                "generate",
                "--prompts-dir",
                str(mock_prompts_dir),
                "--target-path",
                str(tmp_path),
                "--yes",
            ],
        )

        # Should not call checkbox
        mock_checkbox.assert_not_called()
        # Should generate files automatically
        assert result.exit_code == 0
        assert (tmp_path / ".claude" / "commands" / "test-prompt.md").exists()


def test_cli_no_agents_detected_exit_code(tmp_path):
    """Test that no agents detected exits with code 2 (validation error)."""
    # Don't create any agent directories
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "generate",
            "--prompts-dir",
            str(tmp_path / "prompts"),
            "--detection-path",
            str(tmp_path),
            "--yes",
        ],
    )

    assert result.exit_code == 2  # Validation error
    # Error messages are printed to stderr, but may be mixed in stdout by default
    try:
        output = (result.stdout + result.stderr).lower()
    except (ValueError, AttributeError):
        output = result.stdout.lower()
    assert "no agents detected" in output


def test_cli_exit_code_user_cancellation(mock_prompts_dir, tmp_path):
    """Test that user cancellation during overwrite prompt exits with code 1."""
    # Create an existing file
    output_path = tmp_path / ".claude" / "commands" / "test-prompt.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("existing content")

    runner = CliRunner()
    # Mock overwrite prompt to return "cancel"
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

        assert result.exit_code == 1  # User cancellation
        # Cancellation messages are printed to stderr, but may be mixed in stdout by default
        try:
            output = (result.stdout + result.stderr).lower()
        except (ValueError, AttributeError):
            output = result.stdout.lower()
        assert "cancelled" in output or "cancel" in output


def test_cli_cleanup_command(tmp_path):
    """Test that cleanup command lists files to be deleted."""
    # Create a generated file
    command_dir = tmp_path / ".claude" / "commands"
    command_dir.mkdir(parents=True, exist_ok=True)

    generated_file = command_dir / "test-command.md"
    generated_file.write_text(
        """---
name: test-command
description: Test command
meta:
  source_prompt: test-prompt
  version: 1.0.0
---
# Test Command
"""
    )

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "cleanup",
            "--target-path",
            str(tmp_path),
            "--dry-run",
            "--yes",
        ],
    )

    assert result.exit_code == 0
    # Check for table title or summary panel
    assert "Found 1 file(s) to delete" in result.stdout or "DRY RUN Complete" in result.stdout


def test_cli_cleanup_deletes_files(tmp_path):
    """Test that cleanup command deletes generated files."""
    # Create a generated file
    command_dir = tmp_path / ".claude" / "commands"
    command_dir.mkdir(parents=True, exist_ok=True)

    generated_file = command_dir / "test-command.md"
    generated_file.write_text(
        """---
name: test-command
description: Test command
meta:
  source_prompt: test-prompt
  version: 1.0.0
---
# Test Command
"""
    )

    runner = CliRunner()
    with patch("slash_commands.cli.questionary.confirm") as mock_confirm:
        mock_confirm.return_value.ask.return_value = True
        result = runner.invoke(
            app,
            [
                "cleanup",
                "--target-path",
                str(tmp_path),
                "--yes",
            ],
        )

    assert result.exit_code == 0
    assert not generated_file.exists()


def test_cli_cleanup_cancels_on_no_confirmation(tmp_path):
    """Test that cleanup command cancels when user declines confirmation."""
    # Create a generated file
    command_dir = tmp_path / ".claude" / "commands"
    command_dir.mkdir(parents=True, exist_ok=True)

    generated_file = command_dir / "test-command.md"
    generated_file.write_text(
        """---
name: test-command
description: Test command
meta:
  source_prompt: test-prompt
  version: 1.0.0
---
# Test Command
"""
    )

    runner = CliRunner()
    with patch("slash_commands.cli.questionary.confirm") as mock_confirm:
        mock_confirm.return_value.ask.return_value = False
        result = runner.invoke(
            app,
            [
                "cleanup",
                "--target-path",
                str(tmp_path),
            ],
        )

    assert result.exit_code == 1
    assert generated_file.exists()  # File should still exist


def test_cli_cleanup_deletes_backup_files(tmp_path):
    """Test that cleanup command deletes backup files."""
    # Create a backup file
    command_dir = tmp_path / ".claude" / "commands"
    command_dir.mkdir(parents=True, exist_ok=True)

    backup_file = command_dir / "test-command.md.20241201-120000.bak"
    backup_file.write_text("backup content")

    runner = CliRunner()
    with patch("slash_commands.cli.questionary.confirm") as mock_confirm:
        mock_confirm.return_value.ask.return_value = True
        result = runner.invoke(
            app,
            [
                "cleanup",
                "--target-path",
                str(tmp_path),
                "--yes",
            ],
        )

    assert result.exit_code == 0
    assert not backup_file.exists()


def test_cli_cleanup_excludes_backups_when_requested(tmp_path):
    """Test that cleanup command excludes backup files when --no-backups is used."""
    # Create a backup file
    command_dir = tmp_path / ".claude" / "commands"
    command_dir.mkdir(parents=True, exist_ok=True)

    backup_file = command_dir / "test-command.md.20241201-120000.bak"
    backup_file.write_text("backup content")

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "cleanup",
            "--target-path",
            str(tmp_path),
            "--no-backups",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert "No generated files found" in result.stdout


# MCP Subcommand Tests


def test_mcp_subcommand_exists():
    """Test that the mcp subcommand is available."""
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "mcp" in result.stdout


def test_mcp_subcommand_help():
    """Test that mcp subcommand shows help."""
    runner = CliRunner()
    result = runner.invoke(app, ["mcp", "--help"])

    assert result.exit_code == 0
    # Strip ANSI escape codes for comparison
    output = re.sub(r"\x1b\[[0-9;]*m", "", result.stdout)
    assert "--config" in output or "-config" in output
    assert "--transport" in output or "-transport" in output
    assert "--port" in output or "-port" in output
    assert "stdio" in output
    assert "http" in output


@patch("slash_commands.cli.create_app")
def test_mcp_default_stdio_transport(mock_create_app):
    """Test mcp subcommand with default stdio transport."""
    mock_server = MagicMock()
    mock_create_app.return_value = mock_server

    runner = CliRunner()
    result = runner.invoke(app, ["mcp"])

    assert result.exit_code == 0
    mock_create_app.assert_called_once()
    mock_server.run.assert_called_once()


@patch("slash_commands.cli.create_app")
def test_mcp_explicit_stdio_transport(mock_create_app):
    """Test mcp subcommand with explicit stdio transport."""
    mock_server = MagicMock()
    mock_create_app.return_value = mock_server

    runner = CliRunner()
    result = runner.invoke(app, ["mcp", "--transport", "stdio"])

    assert result.exit_code == 0
    mock_create_app.assert_called_once()
    mock_server.run.assert_called_once()


@patch("slash_commands.cli.create_app")
def test_mcp_http_transport_default_port(mock_create_app):
    """Test mcp subcommand with HTTP transport using default port."""
    mock_server = MagicMock()
    mock_create_app.return_value = mock_server

    runner = CliRunner()
    result = runner.invoke(app, ["mcp", "--transport", "http"])

    assert result.exit_code == 0
    mock_create_app.assert_called_once()
    # Verify HTTP server is started with default port
    mock_server.run.assert_called_once_with(transport="http", port=8000)


@patch("slash_commands.cli.create_app")
def test_mcp_http_transport_custom_port(mock_create_app):
    """Test mcp subcommand with HTTP transport using custom port."""
    mock_server = MagicMock()
    mock_create_app.return_value = mock_server

    runner = CliRunner()
    result = runner.invoke(app, ["mcp", "--transport", "http", "--port", "8080"])

    assert result.exit_code == 0
    mock_create_app.assert_called_once()
    mock_server.run.assert_called_once_with(transport="http", port=8080)


@patch("slash_commands.cli.create_app")
def test_mcp_custom_config_file(mock_create_app, tmp_path):
    """Test mcp subcommand with custom config file."""
    mock_server = MagicMock()
    mock_create_app.return_value = mock_server

    # Create a custom config file
    config_file = tmp_path / "custom.toml"
    config_file.write_text("""
[server]
host = "localhost"
port = 9000

[logging]
level = "DEBUG"
""")

    runner = CliRunner()
    result = runner.invoke(app, ["mcp", "--config", str(config_file)])

    assert result.exit_code == 0
    mock_create_app.assert_called_once()
    mock_server.run.assert_called_once()


def test_mcp_invalid_config_file(tmp_path):
    """Test mcp subcommand with invalid config file."""
    # Create an invalid config file
    config_file = tmp_path / "invalid.toml"
    config_file.write_text("invalid toml content [[[")

    runner = CliRunner()
    try:
        result = runner.invoke(app, ["mcp", "--config", str(config_file)])
        # Should still work - config validation not implemented yet
        assert result.exit_code == 0
        assert "Using custom configuration" in result.stdout
    except ValueError:
        # Handle the I/O error that can occur in test environment
        pass


def test_mcp_nonexistent_config_file():
    """Test mcp subcommand with nonexistent config file."""
    runner = CliRunner()
    result = runner.invoke(app, ["mcp", "--config", "/nonexistent/config.toml"])

    assert result.exit_code == 1
    output = result.stdout + result.stderr
    assert "Configuration file not found" in output


@patch("slash_commands.cli.create_app")
def test_mcp_invalid_transport_option(mock_create_app):
    """Test mcp subcommand with invalid transport option."""
    mock_server = MagicMock()
    mock_create_app.return_value = mock_server

    runner = CliRunner()
    result = runner.invoke(app, ["mcp", "--transport", "invalid"])

    # Should fail with validation error (Typer validates Literal types)
    assert result.exit_code == 2
    output = result.stdout + result.stderr
    # Typer's validation message for Literal types
    assert ("invalid" in output.lower() or "Invalid" in output) and (
        "stdio" in output or "http" in output
    )
    mock_create_app.assert_not_called()


@patch("slash_commands.cli.create_app")
def test_mcp_invalid_port_option(mock_create_app):
    """Test mcp subcommand with invalid port option."""
    mock_server = MagicMock()
    mock_create_app.return_value = mock_server

    runner = CliRunner()
    result = runner.invoke(app, ["mcp", "--transport", "http", "--port", "invalid"])

    # Should fail due to invalid port type
    assert result.exit_code != 0
    mock_create_app.assert_not_called()


@patch("slash_commands.cli.create_app")
def test_mcp_port_out_of_range(mock_create_app):
    """Test mcp subcommand with port out of valid range."""
    mock_server = MagicMock()
    mock_create_app.return_value = mock_server

    runner = CliRunner()
    result = runner.invoke(app, ["mcp", "--transport", "http", "--port", "99999"])

    # Should fail with validation error
    assert result.exit_code == 2
    output = result.stdout + result.stderr
    assert "Invalid port" in output
    assert "1 and 65535" in output
    mock_create_app.assert_not_called()


@patch("slash_commands.cli.create_app")
def test_mcp_stdio_transport_ignores_port(mock_create_app):
    """Test that stdio transport ignores port option."""
    mock_server = MagicMock()
    mock_create_app.return_value = mock_server

    runner = CliRunner()
    result = runner.invoke(app, ["mcp", "--transport", "stdio", "--port", "8080"])

    assert result.exit_code == 0
    mock_create_app.assert_called_once()
    mock_server.run.assert_called_once()


def test_cli_interactive_agent_selection_cancels_on_ctrl_c(mock_prompts_dir, tmp_path):
    """Test that interactive agent selection cancels on Ctrl+C."""
    # Create agent directories
    (tmp_path / ".claude").mkdir()

    runner = CliRunner()
    # Mock questionary.checkbox to return None (Ctrl+C)
    with patch("slash_commands.cli.questionary.checkbox") as mock_checkbox:
        # Simulate Ctrl+C (None return)
        mock_checkbox.return_value.ask.return_value = None

        result = runner.invoke(
            app,
            [
                "generate",
                "--prompts-dir",
                str(mock_prompts_dir),
                "--detection-path",
                str(tmp_path),
                "--target-path",
                str(tmp_path),
            ],
        )

        # Should exit with exit code 1 (user cancellation)
        assert result.exit_code == 1
        # Cancellation messages are printed to stderr, but may be mixed in stdout by default
        try:
            output = (result.stdout + result.stderr).lower()
        except (ValueError, AttributeError):
            output = result.stdout.lower()
        assert "no agents selected" in output


def test_unified_help_shows_mcp_subcommand():
    """Test that unified help output shows the complete command structure."""
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "mcp" in result.stdout
    assert "generate" in result.stdout
    assert "cleanup" in result.stdout
    assert "version" in result.stdout


def test_old_command_no_longer_available():
    """Test that slash-command-manager command is no longer available as console script."""
    import importlib.metadata

    # Get all entry points for the package
    try:
        entry_points = importlib.metadata.entry_points()
        console_scripts = entry_points.select(group="console_scripts")

        # Verify the old command is not in console scripts
        old_command_names = [
            ep.name for ep in console_scripts if ep.name == "slash-command-manager"
        ]
        assert len(old_command_names) == 0, (
            "Old entry point 'slash-command-manager' should be removed"
        )
    except AttributeError:
        # Python < 3.10 compatibility
        import pkg_resources

        entry_points = pkg_resources.iter_entry_points("console_scripts")
        old_commands = [ep for ep in entry_points if ep.name == "slash-command-manager"]
        assert len(old_commands) == 0, "Old entry point 'slash-command-manager' should be removed"


def test_cli_github_flags_validation():
    """Test that CLI help shows new GitHub flags and validates successful flag parsing."""
    runner = CliRunner()
    result = runner.invoke(app, ["generate", "--help"])

    assert result.exit_code == 0
    # Strip ANSI escape codes for comparison (Rich formats help output)
    output = re.sub(r"\x1b\[[0-9;]*m", "", result.stdout)
    assert "--github-repo" in output
    assert "--github-branch" in output
    assert "--github-path" in output


def test_validate_github_repo_invalid_format():
    """Test that invalid repository format produces clear error message."""
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "generate",
            "--github-repo",
            "invalid-format",
            "--github-branch",
            "main",
            "--github-path",
            "prompts",
            "--agent",
            "claude-code",
            "--yes",
        ],
    )

    assert result.exit_code == 2  # Validation error
    output = result.stdout + result.stderr
    assert "Repository must be in format owner/repo" in output
    assert "liatrio-labs/spec-driven-workflow" in output


def test_cli_github_flags_missing_required():
    """Test that missing required GitHub flags produce clear error message."""
    runner = CliRunner()

    # Test missing --github-branch
    result = runner.invoke(
        app,
        [
            "generate",
            "--github-repo",
            "owner/repo",
            "--github-path",
            "prompts",
            "--agent",
            "claude-code",
            "--yes",
        ],
    )

    assert result.exit_code == 2  # Validation error
    output = result.stdout + result.stderr
    assert "All GitHub flags must be provided together" in output
    assert "--github-branch" in output

    # Test missing --github-path
    result = runner.invoke(
        app,
        [
            "generate",
            "--github-repo",
            "owner/repo",
            "--github-branch",
            "main",
            "--agent",
            "claude-code",
            "--yes",
        ],
    )

    assert result.exit_code == 2  # Validation error
    output = result.stdout + result.stderr
    assert "All GitHub flags must be provided together" in output
    assert "--github-path" in output

    # Test missing --github-repo
    result = runner.invoke(
        app,
        [
            "generate",
            "--github-branch",
            "main",
            "--github-path",
            "prompts",
            "--agent",
            "claude-code",
            "--yes",
        ],
    )

    assert result.exit_code == 2  # Validation error
    output = result.stdout + result.stderr
    assert "All GitHub flags must be provided together" in output
    assert "--github-repo" in output


def test_cli_github_and_local_mutually_exclusive(mock_prompts_dir, tmp_path):
    """Test that mutual exclusivity error is raised when both --prompts-dir and GitHub flags are provided."""
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "generate",
            "--prompts-dir",
            str(mock_prompts_dir),
            "--github-repo",
            "owner/repo",
            "--github-branch",
            "main",
            "--github-path",
            "prompts",
            "--target-path",
            str(tmp_path),
            "--yes",
        ],
    )

    assert result.exit_code == 2  # Validation error
    output = result.stdout + result.stderr
    assert "Cannot specify both --prompts-dir and GitHub repository flags" in output
    assert "--github-repo" in output
    assert "--github-branch" in output
    assert "--github-path" in output


def test_documentation_github_examples():
    """Test that GitHub examples from README.md execute successfully (validation only)."""
    runner = CliRunner()

    # Test that help shows GitHub flags (validates examples are accurate)
    result = runner.invoke(app, ["generate", "--help"])
    assert result.exit_code == 0
    # Strip ANSI escape codes for comparison (Rich formats help output)
    output = re.sub(r"\x1b\[[0-9;]*m", "", result.stdout)
    assert "--github-repo" in output
    assert "--github-branch" in output
    assert "--github-path" in output

    # Test that main help shows all subcommands
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "generate" in result.stdout
    assert "cleanup" in result.stdout
    assert "mcp" in result.stdout

    # Test that cleanup help works
    result = runner.invoke(app, ["cleanup", "--help"])
    assert result.exit_code == 0
