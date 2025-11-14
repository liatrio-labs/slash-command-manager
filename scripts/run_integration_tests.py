#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# ///
"""Pre-commit hook to run integration tests in Docker (optional).

This script checks if Docker is available and runs integration tests if possible.
If Docker is not available, it exits gracefully with a warning message.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

# Docker configuration - can be overridden via environment variables
DOCKER_WORKDIR = os.environ.get("DOCKER_WORKDIR", "/app")


def check_docker_available() -> bool:
    """Check if Docker is installed and the daemon is running.

    Returns:
        True if Docker is available and running, False otherwise.
    """
    # Check if docker command exists
    docker_cmd = shutil.which("docker")
    if not docker_cmd:
        return False

    # Check if Docker daemon is running
    try:
        result = subprocess.run(
            [docker_cmd, "info"],
            capture_output=True,
            timeout=5,
            check=False,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def run_integration_tests() -> int:
    """Run integration tests in Docker.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    docker_cmd = shutil.which("docker")
    if not docker_cmd:
        return 1

    repo_root = Path(__file__).parent.parent

    # Build Docker image
    print("Building Docker image for integration tests...")
    build_result = subprocess.run(
        [docker_cmd, "build", "-t", "slash-man-test", "."],
        cwd=repo_root,
        check=False,
        timeout=300,  # 5 minute timeout for building
    )
    if build_result.returncode != 0:
        print("❌ Docker build for integration tests failed")
        return build_result.returncode

    # Run integration tests (override ENTRYPOINT from Dockerfile)
    print("Running integration tests in Docker container...")
    test_cmd = f"cd {DOCKER_WORKDIR} && uv run pytest tests/integration/ -v -m integration"
    test_result = subprocess.run(
        [
            docker_cmd,
            "run",
            "--rm",
            "--entrypoint",
            "",
            "slash-man-test",
            "sh",
            "-c",
            test_cmd,
        ],
        cwd=repo_root,
        check=False,
        timeout=300,  # 5 minute timeout for running tests
    )
    return test_result.returncode


def main() -> int:
    """Main entry point for the pre-commit hook.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    if not check_docker_available():
        print("⚠️  Docker not available, skipping integration tests (CI will run them)")
        return 0

    return run_integration_tests()


if __name__ == "__main__":
    sys.exit(main())
