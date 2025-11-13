"""Integration tests for basic CLI commands."""

import subprocess

from slash_commands.__version__ import __version__

from .conftest import REPO_ROOT, get_slash_man_command


def test_main_help_command():
    """Test that slash-man --help produces correct help output."""
    cmd = get_slash_man_command() + ["--help"]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        timeout=10,
    )

    assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"
    assert "Manage slash commands" in result.stdout
    assert "generate" in result.stdout
    assert "cleanup" in result.stdout
    assert "mcp" in result.stdout


def test_main_version_command():
    """Test that slash-man --version outputs version string."""
    cmd = get_slash_man_command() + ["--version"]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"
    assert "slash-man" in result.stdout
    assert __version__ in result.stdout


def test_generate_help_command():
    """Test that slash-man generate --help shows generate command help."""
    cmd = get_slash_man_command() + ["generate", "--help"]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"
    assert "Generate slash commands" in result.stdout
    assert "--prompts-dir" in result.stdout
    assert "--agent" in result.stdout
    assert "--dry-run" in result.stdout


def test_cleanup_help_command():
    """Test that slash-man cleanup --help shows cleanup command help."""
    cmd = get_slash_man_command() + ["cleanup", "--help"]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"
    assert "Clean up generated slash commands" in result.stdout
    assert "--agent" in result.stdout
    assert "--dry-run" in result.stdout
    assert "--include-backups" in result.stdout


def test_mcp_help_command():
    """Test that slash-man mcp --help shows mcp command help."""
    cmd = get_slash_man_command() + ["mcp", "--help"]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"
    assert "Start the MCP server" in result.stdout
    assert "--transport" in result.stdout
    assert "--port" in result.stdout
    assert "--config" in result.stdout


def test_list_agents_command():
    """Test that slash-man generate --list-agents lists all supported agents."""
    cmd = get_slash_man_command() + ["generate", "--list-agents"]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"

    # Verify all expected agents are present
    expected_agents = {
        "claude-code": "Claude Code",
        "cursor": "Cursor",
        "gemini-cli": "Gemini CLI",
        "vs-code": "VS Code",
        "codex-cli": "Codex CLI",
        "windsurf": "Windsurf",
        "opencode": "OpenCode CLI",
    }

    for agent_key, display_name in expected_agents.items():
        assert agent_key in result.stdout, f"Missing agent key: {agent_key}"
        assert display_name in result.stdout, f"Missing display name: {display_name}"
