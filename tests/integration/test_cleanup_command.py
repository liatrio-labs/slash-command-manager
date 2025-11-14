"""Integration tests for cleanup command."""

import subprocess
from datetime import UTC, datetime

from .conftest import REPO_ROOT, get_slash_man_command


def test_cleanup_dry_run_mode(temp_test_dir, test_prompts_dir):
    """Test cleanup with dry-run mode shows files without deleting."""
    # First generate files
    generate_cmd = get_slash_man_command() + [
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
        generate_cmd,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0

    generated_file = temp_test_dir / ".claude" / "commands" / "test-prompt-1.md"
    assert generated_file.exists()

    # Now test cleanup dry-run (needs --yes to skip confirmation)
    cleanup_cmd = get_slash_man_command() + [
        "cleanup",
        "--agent",
        "claude-code",
        "--target-path",
        str(temp_test_dir),
        "--dry-run",
        "--yes",
    ]
    result = subprocess.run(
        cleanup_cmd,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    assert result.returncode == 0
    # Verify files still exist
    assert generated_file.exists(), "Files should still exist in dry-run mode"


def test_cleanup_removes_generated_files(temp_test_dir, test_prompts_dir):
    """Test cleanup removes generated files."""
    # First generate files
    generate_cmd = get_slash_man_command() + [
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
        generate_cmd,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0

    generated_file = temp_test_dir / ".claude" / "commands" / "test-prompt-1.md"
    assert generated_file.exists()

    # Now cleanup
    cleanup_cmd = get_slash_man_command() + [
        "cleanup",
        "--agent",
        "claude-code",
        "--target-path",
        str(temp_test_dir),
        "--yes",
    ]
    result = subprocess.run(
        cleanup_cmd,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    assert result.returncode == 0
    # Verify files are deleted
    assert not generated_file.exists(), "Files should be deleted after cleanup"


def test_cleanup_includes_backups(temp_test_dir, test_prompts_dir):
    """Test cleanup includes backup files when --include-backups is used."""
    # First generate files
    generate_cmd = get_slash_man_command() + [
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
        generate_cmd,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0

    generated_file = temp_test_dir / ".claude" / "commands" / "test-prompt-1.md"
    assert generated_file.exists()

    # Manually create backup file
    timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    backup_file = generated_file.parent / f"test-prompt-1.md.{timestamp}.bak"
    backup_file.write_text(generated_file.read_text(encoding="utf-8"), encoding="utf-8")
    assert backup_file.exists()

    # Cleanup with --include-backups
    cleanup_cmd = get_slash_man_command() + [
        "cleanup",
        "--agent",
        "claude-code",
        "--target-path",
        str(temp_test_dir),
        "--include-backups",
        "--yes",
    ]
    result = subprocess.run(
        cleanup_cmd,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    assert result.returncode == 0
    # Verify both command file and backup are deleted
    assert not generated_file.exists(), "Command file should be deleted"
    assert not backup_file.exists(), "Backup file should be deleted with --include-backups"


def test_cleanup_excludes_backups_by_default(temp_test_dir, test_prompts_dir):
    """Test cleanup excludes backup files when --no-backups is used."""
    # First generate files
    generate_cmd = get_slash_man_command() + [
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
        generate_cmd,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0

    generated_file = temp_test_dir / ".claude" / "commands" / "test-prompt-1.md"
    assert generated_file.exists()

    # Manually create backup file
    timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    backup_file = generated_file.parent / f"test-prompt-1.md.{timestamp}.bak"
    backup_file.write_text(generated_file.read_text(encoding="utf-8"), encoding="utf-8")
    assert backup_file.exists()

    # Cleanup with --no-backups (excludes backups)
    cleanup_cmd = get_slash_man_command() + [
        "cleanup",
        "--agent",
        "claude-code",
        "--target-path",
        str(temp_test_dir),
        "--no-backups",
        "--yes",
    ]
    result = subprocess.run(
        cleanup_cmd,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    assert result.returncode == 0
    # Verify command file is deleted but backup remains
    assert not generated_file.exists(), "Command file should be deleted"
    assert backup_file.exists(), "Backup file should remain when --no-backups is used"


def test_cleanup_multiple_agents(temp_test_dir, test_prompts_dir):
    """Test cleanup with multiple agents."""
    # Generate files for multiple agents
    generate_cmd = get_slash_man_command() + [
        "generate",
        "--prompts-dir",
        str(test_prompts_dir),
        "--agent",
        "claude-code",
        "--agent",
        "cursor",
        "--target-path",
        str(temp_test_dir),
        "--yes",
    ]
    result = subprocess.run(
        generate_cmd,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0

    claude_file = temp_test_dir / ".claude" / "commands" / "test-prompt-1.md"
    cursor_file = temp_test_dir / ".cursor" / "commands" / "test-prompt-1.md"
    assert claude_file.exists()
    assert cursor_file.exists()

    # Cleanup both agents
    cleanup_cmd = get_slash_man_command() + [
        "cleanup",
        "--agent",
        "claude-code",
        "--agent",
        "cursor",
        "--target-path",
        str(temp_test_dir),
        "--yes",
    ]
    result = subprocess.run(
        cleanup_cmd,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    assert result.returncode == 0
    assert not claude_file.exists(), "Claude files should be deleted"
    assert not cursor_file.exists(), "Cursor files should be deleted"


def test_cleanup_all_agents(temp_test_dir, test_prompts_dir):
    """Test cleanup without --agent flag cleans all agents."""
    # Generate files for multiple agents
    generate_cmd = get_slash_man_command() + [
        "generate",
        "--prompts-dir",
        str(test_prompts_dir),
        "--agent",
        "claude-code",
        "--agent",
        "cursor",
        "--target-path",
        str(temp_test_dir),
        "--yes",
    ]
    result = subprocess.run(
        generate_cmd,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0

    claude_file = temp_test_dir / ".claude" / "commands" / "test-prompt-1.md"
    cursor_file = temp_test_dir / ".cursor" / "commands" / "test-prompt-1.md"
    assert claude_file.exists()
    assert cursor_file.exists()

    # Cleanup without --agent flag (should clean all)
    cleanup_cmd = get_slash_man_command() + [
        "cleanup",
        "--target-path",
        str(temp_test_dir),
        "--yes",
    ]
    result = subprocess.run(
        cleanup_cmd,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    assert result.returncode == 0
    assert not claude_file.exists(), "Claude files should be deleted"
    assert not cursor_file.exists(), "Cursor files should be deleted"
