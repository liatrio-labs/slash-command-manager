"""Integration tests for interactive overwrite prompts."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pexpect
import pytest

from .conftest import REPO_ROOT, get_slash_man_command


def _run_generate(args: list[str]) -> subprocess.CompletedProcess[str]:
    """Helper to run slash-man generate with base command."""
    cmd = get_slash_man_command() + args
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return result


@pytest.mark.integration
def test_skip_backups_only_route_without_backups(temp_test_dir: Path, test_prompts_dir: Path):
    """Ensure skip-backups selection is the only way to avoid backups."""
    target_path = temp_test_dir
    base_args = [
        "generate",
        "--prompts-dir",
        str(test_prompts_dir),
        "--agent",
        "claude-code",
        "--target-path",
        str(target_path),
    ]

    # Seed files so the second run encounters existing files.
    _run_generate(base_args + ["--yes"])
    command_dir = target_path / ".claude" / "commands"
    assert command_dir.exists()

    # Ensure no leftover backups before interactive run.
    for backup in command_dir.glob("*.bak"):
        backup.unlink()

    spawn_cmd = get_slash_man_command()
    command = spawn_cmd[0]
    args = spawn_cmd[1:] + base_args

    child = pexpect.spawn(
        command,
        args=args,
        cwd=str(REPO_ROOT),
        encoding="utf-8",
        timeout=60,
    )

    child.expect("What would you like to do\\?")

    # Move selection down to the skip-backups option and confirm.
    child.send("\x1b[B")
    child.expect(r"» Create backups and overwrite all \(recommended\)")
    child.send("\x1b[B")
    child.expect(r"» Skip backups and overwrite all \(NOT RECOMMENDED\)")
    child.send("\r")

    child.expect("WARNING: Skip backups selected", timeout=60)
    child.expect("Generation complete:", timeout=60)
    exit_status = child.wait()
    assert exit_status == 0, f"Process exited with code {exit_status}"

    backup_files = list(command_dir.glob("*.bak"))
    assert backup_files == [], f"Unexpected backups created: {backup_files}"
