"""Pytest fixtures for integration tests."""

import base64
import tempfile
from pathlib import Path

import pytest
import pytest_httpx


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
def mock_github_api(httpx_mock, test_prompts_dir):
    """Mock GitHub API responses using pytest-httpx.

    This fixture sets up common GitHub API mocks for integration tests.
    Tests can override these mocks as needed.

    Args:
        httpx_mock: pytest-httpx mock fixture
        test_prompts_dir: Path to test prompts directory

    Yields:
        httpx_mock: The mock object for further customization
    """

    # Helper function to encode content as base64 (GitHub API format)
    def encode_content(content: str) -> str:
        return base64.b64encode(content.encode("utf-8")).decode("utf-8")

    # Read test prompt files
    prompt_files = {}
    for prompt_file in test_prompts_dir.glob("*.md"):
        prompt_files[prompt_file.name] = prompt_file.read_text(encoding="utf-8")

    # Default mock: directory listing with test prompts
    def directory_response(request):
        """Return directory listing response."""
        items = []
        for filename, content in prompt_files.items():
            items.append(
                {
                    "type": "file",
                    "name": filename,
                    "content": encode_content(content),
                    "encoding": "base64",
                }
            )
        return pytest_httpx.HTTPXMockResponse(json=items, status_code=200)

    # Default mock: single file response
    def file_response(request):
        """Return single file response."""
        # Extract filename from path
        path = request.url.path.split("/")[-1]
        filename = Path(path).name

        if filename in prompt_files:
            content = prompt_files[filename]
            return pytest_httpx.HTTPXMockResponse(
                json={
                    "type": "file",
                    "name": filename,
                    "content": encode_content(content),
                    "encoding": "base64",
                },
                status_code=200,
            )
        # File not found
        return pytest_httpx.HTTPXMockResponse(status_code=404)

    # Register default mocks (can be overridden in tests)
    httpx_mock.add_callback(
        directory_response,
        url="https://api.github.com/repos/owner/repo/contents/prompts",
    )
    httpx_mock.add_callback(
        file_response,
        url="https://api.github.com/repos/owner/repo/contents/prompts/test-prompt-1.md",
    )

    yield httpx_mock


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
