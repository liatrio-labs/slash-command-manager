"""Integration tests for basic CLI commands."""

import shutil
import subprocess
import sys
from pathlib import Path


def _get_slash_man_command():
    """Get the slash-man command to execute."""
    # In Docker, the package is installed in .venv, so we can call it directly
    # Try to find slash-man in the venv, otherwise use uv run
    venv_bin = Path(__file__).parent.parent.parent / ".venv" / "bin" / "slash-man"
    if venv_bin.exists():
        return [str(venv_bin)]
    # Fallback: use uv run (for local development)
    uv_path = shutil.which("uv")
    if uv_path:
        return [uv_path, "run", "slash-man"]
    # Last resort: try python -m slash_commands.cli
    return [sys.executable, "-m", "slash_commands.cli"]


def test_main_help_command():
    """Test that slash-man --help produces correct help output."""
    cmd = _get_slash_man_command() + ["--help"]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent.parent,
    )

    assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"
    assert "Manage slash commands" in result.stdout
    assert "generate" in result.stdout
    assert "cleanup" in result.stdout
    assert "mcp" in result.stdout


def test_main_version_command():
    """Test that slash-man --version outputs version string."""
    cmd = _get_slash_man_command() + ["--version"]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent.parent,
    )

    assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"
    assert "slash-man" in result.stdout
    assert "0.1.0" in result.stdout


def test_generate_help_command():
    """Test that slash-man generate --help shows generate command help."""
    cmd = _get_slash_man_command() + ["generate", "--help"]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent.parent,
    )

    assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"
    assert "Generate slash commands" in result.stdout
    assert "--prompts-dir" in result.stdout
    assert "--agent" in result.stdout
    assert "--dry-run" in result.stdout


def test_cleanup_help_command():
    """Test that slash-man cleanup --help shows cleanup command help."""
    cmd = _get_slash_man_command() + ["cleanup", "--help"]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent.parent,
    )

    assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"
    assert "Clean up generated slash commands" in result.stdout
    assert "--agent" in result.stdout
    assert "--dry-run" in result.stdout
    assert "--include-backups" in result.stdout


def test_mcp_help_command():
    """Test that slash-man mcp --help shows mcp command help."""
    cmd = _get_slash_man_command() + ["mcp", "--help"]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent.parent,
    )

    assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"
    assert "Start the MCP server" in result.stdout
    assert "--transport" in result.stdout
    assert "--port" in result.stdout
    assert "--config" in result.stdout


def test_list_agents_command():
    """Test that slash-man generate --list-agents lists all supported agents."""
    cmd = _get_slash_man_command() + ["generate", "--list-agents"]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent.parent,
    )

    assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"
    assert "claude-code" in result.stdout
    assert "cursor" in result.stdout
    assert "gemini-cli" in result.stdout
    assert "vs-code" in result.stdout
    assert "codex-cli" in result.stdout
    assert "windsurf" in result.stdout
    assert "opencode" in result.stdout
    assert "Claude Code" in result.stdout
    assert "Cursor" in result.stdout
    assert "Gemini CLI" in result.stdout
    assert "VS Code" in result.stdout
    assert "Codex CLI" in result.stdout
    assert "Windsurf" in result.stdout
    assert "OpenCode CLI" in result.stdout
