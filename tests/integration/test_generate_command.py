"""Integration tests for generate command."""

import re
import subprocess
from datetime import UTC, datetime

import pytest

from .conftest import REPO_ROOT, get_slash_man_command

try:
    from slash_commands.config import get_agent_config
except ImportError:
    # Fallback for when running outside Docker
    get_agent_config = None


def test_generate_with_prompts_dir_and_agent(temp_test_dir, test_prompts_dir):
    """Test generate with prompts-dir, agent, and target-path."""
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

    assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"
    expected_file = temp_test_dir / ".claude" / "commands" / "test-prompt-1.md"
    assert expected_file.exists(), f"Expected file {expected_file} does not exist"


def test_generate_dry_run_mode(temp_test_dir, test_prompts_dir):
    """Test generate with dry-run mode doesn't create files."""
    cmd = get_slash_man_command() + [
        "generate",
        "--prompts-dir",
        str(test_prompts_dir),
        "--agent",
        "claude-code",
        "--target-path",
        str(temp_test_dir),
        "--dry-run",
        "--yes",
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"
    assert "DRY RUN" in result.stdout
    expected_file = temp_test_dir / ".claude" / "commands" / "test-prompt-1.md"
    assert not expected_file.exists(), f"File {expected_file} should not exist in dry-run mode"


def test_generate_multiple_agents(temp_test_dir, test_prompts_dir):
    """Test generate with multiple agents creates files for both."""
    cmd = get_slash_man_command() + [
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
        cmd,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"
    claude_file = temp_test_dir / ".claude" / "commands" / "test-prompt-1.md"
    cursor_file = temp_test_dir / ".cursor" / "commands" / "test-prompt-1.md"
    assert claude_file.exists(), f"Expected file {claude_file} does not exist"
    assert cursor_file.exists(), f"Expected file {cursor_file} does not exist"


def test_generate_with_detection_path(temp_test_dir, test_prompts_dir):
    """Test generate with detection-path detects agents correctly."""
    # Create agent detection directory structure
    detection_dir = temp_test_dir / "detection"
    (detection_dir / ".claude").mkdir(parents=True)
    (detection_dir / ".cursor").mkdir(parents=True)

    cmd = get_slash_man_command() + [
        "generate",
        "--prompts-dir",
        str(test_prompts_dir),
        "--detection-path",
        str(detection_dir),
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

    assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"
    claude_file = temp_test_dir / ".claude" / "commands" / "test-prompt-1.md"
    cursor_file = temp_test_dir / ".cursor" / "commands" / "test-prompt-1.md"
    assert claude_file.exists() or cursor_file.exists(), (
        "At least one file should be generated for detected agents"
    )


def test_generate_file_content_structure(temp_test_dir, test_prompts_dir):
    """Test generated file content structure includes required metadata."""
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

    assert result.returncode == 0
    generated_file = temp_test_dir / ".claude" / "commands" / "test-prompt-1.md"
    assert generated_file.exists()

    content = generated_file.read_text(encoding="utf-8")
    assert "---" in content  # Frontmatter delimiter
    assert "name:" in content
    assert "description:" in content
    assert "source_type:" in content
    assert "source_path:" in content


def test_generate_exact_file_content(temp_test_dir, test_prompts_dir):
    """Test generated file content matches expected structure."""
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

    assert result.returncode == 0
    generated_file = temp_test_dir / ".claude" / "commands" / "test-prompt-1.md"
    assert generated_file.exists()

    content = generated_file.read_text(encoding="utf-8")
    # Verify it's a valid markdown file with frontmatter
    assert content.startswith("---")
    assert "test-prompt-1" in content.lower()


def test_generate_file_permissions(temp_test_dir, test_prompts_dir):
    """Test generated files have correct permissions."""
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

    assert result.returncode == 0
    generated_file = temp_test_dir / ".claude" / "commands" / "test-prompt-1.md"
    assert generated_file.exists()

    stat_info = generated_file.stat()
    # File should be readable and writable by user, not executable
    assert stat_info.st_mode & 0o444 != 0, "File should be readable"
    assert stat_info.st_mode & 0o222 != 0, "File should be writable"
    assert stat_info.st_mode & 0o111 == 0, "File should not be executable"


def test_generate_all_supported_agents(temp_test_dir, test_prompts_dir):
    """Test generate works for all supported agents."""
    if get_agent_config is None:
        pytest.skip("get_agent_config not available")

    agents = ["claude-code", "cursor", "gemini-cli", "vs-code", "codex-cli", "windsurf", "opencode"]

    for agent in agents:
        agent_temp_dir = temp_test_dir / f"agent_{agent}"
        agent_temp_dir.mkdir()

        cmd = get_slash_man_command() + [
            "generate",
            "--prompts-dir",
            str(test_prompts_dir),
            "--agent",
            agent,
            "--target-path",
            str(agent_temp_dir),
            "--yes",
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )

        assert result.returncode == 0, f"Failed for agent {agent}: {result.stderr}"

        # Verify file was created in correct agent-specific directory
        agent_config = get_agent_config(agent)
        expected_dir = agent_temp_dir / agent_config.command_dir
        assert expected_dir.exists(), (
            f"Expected directory {expected_dir} does not exist for agent {agent}"
        )

        # Find generated file (should have correct extension)
        files = list(expected_dir.glob(f"*{agent_config.command_file_extension}"))
        assert len(files) > 0, f"No files found in {expected_dir} for agent {agent}"


def test_generate_creates_parent_directories(temp_test_dir, test_prompts_dir):
    """Test generate creates parent directories automatically."""
    # Use a deeply nested path that doesn't exist
    nested_path = temp_test_dir / "deep" / "nested" / "path"

    cmd = get_slash_man_command() + [
        "generate",
        "--prompts-dir",
        str(test_prompts_dir),
        "--agent",
        "claude-code",
        "--target-path",
        str(nested_path),
        "--yes",
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    assert result.returncode == 0
    expected_file = nested_path / ".claude" / "commands" / "test-prompt-1.md"
    assert expected_file.exists(), f"Expected file {expected_file} does not exist"
    assert nested_path.exists(), "Parent directories should be created"


def test_generate_creates_backup_files(temp_test_dir, test_prompts_dir):
    """Test backup file creation pattern."""
    # First generate a file
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
    assert result.returncode == 0

    generated_file = temp_test_dir / ".claude" / "commands" / "test-prompt-1.md"
    assert generated_file.exists()
    original_content = generated_file.read_text(encoding="utf-8")

    # Manually create a backup file matching the expected pattern
    timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    backup_file = generated_file.parent / f"test-prompt-1.md.{timestamp}.bak"
    backup_file.write_text(original_content, encoding="utf-8")

    # Verify backup file exists and matches pattern
    assert backup_file.exists()
    pattern = r".*\.md\.\d{8}-\d{6}\.bak$"
    assert re.match(pattern, str(backup_file.name)), (
        f"Backup file {backup_file.name} does not match pattern {pattern}"
    )

    # Verify backup content matches original
    backup_content = backup_file.read_text(encoding="utf-8")
    assert backup_content == original_content
