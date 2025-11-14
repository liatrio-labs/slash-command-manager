"""Pytest fixtures for integration tests."""

import shutil
import sys
import tempfile
from pathlib import Path

import pytest

# Repository root directory
REPO_ROOT = Path(__file__).parent.parent.parent


def pytest_collection_modifyitems(config, items):
    """Automatically mark all tests in the integration directory as integration tests."""
    for item in items:
        # Check if test is in the integration directory using pathlib
        path_parts = Path(item.fspath).parts
        # Verify that 'tests' and 'integration' appear consecutively in the path
        if "tests" in path_parts and "integration" in path_parts:
            # Find the index of 'tests' and check if 'integration' follows it
            tests_index = path_parts.index("tests")
            if tests_index + 1 < len(path_parts) and path_parts[tests_index + 1] == "integration":
                item.add_marker(pytest.mark.integration)


@pytest.fixture
def temp_test_dir():
    """Create temporary directory for test execution.

    Yields:
        Path to temporary directory
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def test_prompts_dir():
    """Return path to test prompts directory.

    Returns:
        Path to tests/integration/fixtures/prompts/
    """
    return Path(__file__).parent / "fixtures" / "prompts"


@pytest.fixture
def clean_agent_dirs(temp_test_dir):
    """Ensure agent directories are clean before each test.

    This fixture creates a clean temporary directory structure
    that mimics the home directory structure for agent command directories.

    Args:
        temp_test_dir: Temporary directory fixture

    Yields:
        Path to temporary test directory (acts as home directory)
    """
    # Create agent detection directories to ensure clean state
    agent_dirs = [
        ".claude",
        ".cursor",
        ".codex",
        ".gemini",
        ".config/Code",
        ".codeium/windsurf",
        ".opencode",
    ]

    for agent_dir in agent_dirs:
        full_path = temp_test_dir / agent_dir
        full_path.mkdir(parents=True, exist_ok=True)

    yield temp_test_dir

    # Cleanup happens automatically via tempfile.TemporaryDirectory


def get_slash_man_command():
    """Get the slash-man command to execute."""
    venv_bin = REPO_ROOT / ".venv" / "bin" / "slash-man"
    if venv_bin.exists():
        return [str(venv_bin)]
    uv_path = shutil.which("uv")
    if uv_path:
        return [uv_path, "run", "slash-man"]
    return [sys.executable, "-m", "slash_commands.cli"]


def run_command(args):
    """Run slash-man command and return result.

    Args:
        args: List of command arguments (without the base command)

    Returns:
        CompletedProcess result from subprocess.run
    """
    import subprocess

    cmd = get_slash_man_command() + args
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        timeout=30,  # Prevent hanging tests
        check=False,  # Explicit: caller handles exit codes
    )
