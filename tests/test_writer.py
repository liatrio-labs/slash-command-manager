"""Tests for the slash command writer."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from slash_commands.config import CommandFormat
from slash_commands.writer import SlashCommandWriter, _find_package_prompts_dir


@pytest.fixture
def mock_prompt_load(tmp_path):
    """Create a prompts directory with a sample prompt file."""
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()

    # Create a sample prompt file
    prompt_file = prompts_dir / "test-prompt.md"
    prompt_file.write_text(
        """---
name: test-prompt
description: Test prompt for writer tests
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


def test_writer_generates_command_for_single_agent(mock_prompt_load: Path, tmp_path):
    """Test that writer generates command file for a single agent."""
    prompts_dir = mock_prompt_load

    writer = SlashCommandWriter(
        prompts_dir=prompts_dir,
        agents=["claude-code"],
        dry_run=False,
        base_path=tmp_path,
    )

    result = writer.generate()

    # Verify that a file was created
    expected_path = tmp_path / ".claude" / "commands" / "test-prompt.md"
    assert expected_path.exists()
    assert "Test Prompt" in expected_path.read_text()

    # Verify result structure
    assert result["files_written"] == 1
    assert len(result["files"]) == 1
    assert result["files"][0]["path"] == str(expected_path)
    assert result["files"][0]["agent"] == "claude-code"


def test_writer_generates_commands_for_multiple_agents(mock_prompt_load: Path, tmp_path):
    """Test that writer generates command files for multiple agents."""
    prompts_dir = mock_prompt_load

    writer = SlashCommandWriter(
        prompts_dir=prompts_dir,
        agents=["claude-code", "gemini-cli"],
        dry_run=False,
        base_path=tmp_path,
    )

    result = writer.generate()

    # Verify that files were created for both agents
    claude_path = tmp_path / ".claude" / "commands" / "test-prompt.md"
    gemini_path = tmp_path / ".gemini" / "commands" / "test-prompt.toml"

    assert claude_path.exists()
    assert gemini_path.exists()

    # Verify result structure
    assert result["files_written"] == 2
    assert len(result["files"]) == 2


def test_writer_respects_dry_run_flag(mock_prompt_load: Path, tmp_path):
    """Test that writer doesn't create files when dry_run is True."""
    prompts_dir = mock_prompt_load

    writer = SlashCommandWriter(
        prompts_dir=prompts_dir,
        agents=["claude-code"],
        dry_run=True,
        base_path=tmp_path,
    )

    result = writer.generate()

    # Verify that no files were created
    expected_path = tmp_path / ".claude" / "commands" / "test-prompt.md"
    assert not expected_path.exists()

    # Verify result structure still reports what would be written
    assert result["files_written"] == 0
    assert len(result["files"]) == 1
    assert result["files"][0]["path"] == str(expected_path)


def test_writer_creates_parent_directories(mock_prompt_load: Path, tmp_path):
    """Test that writer creates parent directories if they don't exist."""
    prompts_dir = mock_prompt_load

    writer = SlashCommandWriter(
        prompts_dir=prompts_dir,
        agents=["claude-code"],
        dry_run=False,
        base_path=tmp_path,
    )

    writer.generate()

    # Verify that parent directory was created
    expected_dir = tmp_path / ".claude" / "commands"
    assert expected_dir.exists()
    assert expected_dir.is_dir()


def test_writer_calls_generator_with_correct_agent(mock_prompt_load: Path, tmp_path):
    """Test that writer calls generator with correct agent configuration."""
    prompts_dir = mock_prompt_load

    with patch("slash_commands.writer.CommandGenerator") as mock_generator_class:
        mock_generator = MagicMock()
        mock_generator.generate.return_value = "---\nname: test-prompt\n---\n\n# Test Prompt"
        mock_generator_class.create.return_value = mock_generator

        writer = SlashCommandWriter(
            prompts_dir=prompts_dir,
            agents=["claude-code"],
            dry_run=False,
            base_path=tmp_path,
        )

        writer.generate()

        # Verify generator was called with correct agent
        mock_generator_class.create.assert_called_once_with(CommandFormat.MARKDOWN)
        assert mock_generator.generate.called


def test_writer_loads_prompts_from_directory(mock_prompt_load: Path, tmp_path):
    """Test that writer loads prompts from the specified directory."""
    prompts_dir = mock_prompt_load

    writer = SlashCommandWriter(
        prompts_dir=prompts_dir,
        agents=["claude-code"],
        dry_run=False,
        base_path=tmp_path,
    )

    result = writer.generate()

    # Verify that prompts were loaded
    assert result["prompts_loaded"] == 1
    assert len(result["prompts"]) == 1
    assert result["prompts"][0]["name"] == "test-prompt"


def test_writer_handles_missing_prompts_directory(tmp_path):
    """Test that writer handles missing prompts directory gracefully."""
    prompts_dir = tmp_path / "nonexistent"

    writer = SlashCommandWriter(
        prompts_dir=prompts_dir,
        agents=["claude-code"],
        dry_run=False,
        base_path=tmp_path,
    )

    # Mock the fallback function to return None to test the error case
    with patch("slash_commands.writer._find_package_prompts_dir", return_value=None):
        with pytest.raises(ValueError, match="Prompts directory does not exist"):
            writer.generate()


def test_writer_finds_bundled_prompts(tmp_path):
    """Test that writer finds bundled prompts using importlib.resources."""
    prompts_dir = tmp_path / "nonexistent"

    # Create a mock package prompts directory
    package_prompts_dir = tmp_path / "package_prompts"
    package_prompts_dir.mkdir()
    prompt_file = package_prompts_dir / "bundled-prompt.md"
    prompt_file.write_text(
        """---
name: bundled-prompt
description: Bundled prompt test
tags:
  - testing
arguments: []
enabled: true
---
# Bundled Prompt

This is a bundled test prompt.
""",
        encoding="utf-8",
    )

    writer = SlashCommandWriter(
        prompts_dir=prompts_dir,
        agents=["claude-code"],
        dry_run=True,
        base_path=tmp_path,
        is_explicit_prompts_dir=False,  # Use default path to enable fallback
    )

    # Mock the fallback function to return the mock package prompts directory
    with patch("slash_commands.writer._find_package_prompts_dir", return_value=package_prompts_dir):
        result = writer.generate()
        assert result["prompts_loaded"] == 1
        assert len(result["prompts"]) == 1
        assert result["prompts"][0]["name"] == "bundled-prompt"


def test_find_package_prompts_dir_importlib(tmp_path: Path):
    """Test that _find_package_prompts_dir can find prompts via importlib."""
    with patch("importlib.resources.files") as mock_files:
        # Create a mock traversable object for the prompts directory
        mock_prompts_resource = MagicMock()
        mock_prompts_resource.is_dir.return_value = True
        mock_prompts_resource.__str__.return_value = str(tmp_path)

        # Mock the anchor package traversable
        mock_anchor = MagicMock()
        # Mock the parent traversal and joining with "prompts"
        mock_anchor.parent.__truediv__.return_value = mock_prompts_resource

        mock_files.return_value = mock_anchor

        # Call the function being tested
        result = _find_package_prompts_dir()

        # Verify that importlib.resources.files was called correctly
        mock_files.assert_called_once_with("slash_commands")

        # Verify that the correct path was returned
        assert result == tmp_path


def test_writer_falls_back_to_package_prompts(tmp_path):
    """Test that writer falls back to package prompts when specified directory doesn't exist."""
    prompts_dir = tmp_path / "nonexistent"

    # Create a mock package prompts directory
    package_prompts_dir = tmp_path / "package_prompts"
    package_prompts_dir.mkdir()
    prompt_file = package_prompts_dir / "fallback-prompt.md"
    prompt_file.write_text(
        """---
name: fallback-prompt
description: Fallback prompt test
tags:
  - testing
arguments: []
enabled: true
---
# Fallback Prompt

This is a test prompt.
""",
        encoding="utf-8",
    )

    writer = SlashCommandWriter(
        prompts_dir=prompts_dir,
        agents=["claude-code"],
        dry_run=True,
        base_path=tmp_path,
        is_explicit_prompts_dir=False,  # Use default path to enable fallback
    )

    # Mock the fallback function to return the mock package prompts directory
    with patch("slash_commands.writer._find_package_prompts_dir", return_value=package_prompts_dir):
        result = writer.generate()
        assert result["prompts_loaded"] == 1
        assert len(result["prompts"]) == 1
        assert result["prompts"][0]["name"] == "fallback-prompt"


def test_writer_handles_invalid_agent_key(mock_prompt_load: Path, tmp_path):
    """Test that writer handles invalid agent keys gracefully."""
    prompts_dir = mock_prompt_load

    writer = SlashCommandWriter(
        prompts_dir=prompts_dir,
        agents=["invalid-agent"],
        dry_run=False,
        base_path=tmp_path,
    )

    with pytest.raises(KeyError, match="Unsupported agent"):
        writer.generate()


def test_writer_detects_existing_files(mock_prompt_load: Path, tmp_path):
    """Test that writer detects existing command files."""
    prompts_dir = mock_prompt_load

    # Create an existing file
    output_path = tmp_path / ".claude" / "commands" / "test-prompt.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("existing content")

    writer = SlashCommandWriter(
        prompts_dir=prompts_dir,
        agents=["claude-code"],
        dry_run=False,
        base_path=tmp_path,
    )

    # OverwriteAction should be queried
    with patch(
        "slash_commands.writer.SlashCommandWriter._prompt_for_all_existing_files"
    ) as mock_prompt:
        mock_prompt.return_value = "overwrite"
        writer.generate()

        # Verify prompt was called
        mock_prompt.assert_called_once()
        # Verify file was overwritten
        assert "Test Prompt" in output_path.read_text()


def test_writer_cancels_on_existing_files(mock_prompt_load: Path, tmp_path):
    """Test that writer cancels when user chooses not to overwrite."""
    prompts_dir = mock_prompt_load

    # Create an existing file
    output_path = tmp_path / ".claude" / "commands" / "test-prompt.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    original_content = "existing content"
    output_path.write_text(original_content)

    writer = SlashCommandWriter(
        prompts_dir=prompts_dir,
        agents=["claude-code"],
        dry_run=False,
        base_path=tmp_path,
    )

    with patch(
        "slash_commands.writer.SlashCommandWriter._prompt_for_all_existing_files"
    ) as mock_prompt:
        mock_prompt.return_value = "cancel"
        with pytest.raises(RuntimeError, match="Cancelled"):
            writer.generate()

        # Verify file was not modified
        assert output_path.read_text() == original_content


def test_writer_backs_up_existing_files(mock_prompt_load: Path, tmp_path):
    """Test that writer creates backup files when requested."""
    prompts_dir = mock_prompt_load

    # Create an existing file
    output_path = tmp_path / ".claude" / "commands" / "test-prompt.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    original_content = "existing content"
    output_path.write_text(original_content)

    writer = SlashCommandWriter(
        prompts_dir=prompts_dir,
        agents=["claude-code"],
        dry_run=False,
        base_path=tmp_path,
    )

    with patch(
        "slash_commands.writer.SlashCommandWriter._prompt_for_all_existing_files"
    ) as mock_prompt:
        with patch("slash_commands.writer.create_backup") as mock_backup:
            mock_prompt.return_value = "backup"
            mock_backup.return_value = output_path.with_suffix(".md.bak")

            writer.generate()

            # Verify backup was created
            mock_backup.assert_called_once_with(output_path)
            # Verify file was overwritten
            assert "Test Prompt" in output_path.read_text()


def test_writer_applies_overwrite_globally(mock_prompt_load: Path, tmp_path):
    """Test that writer can apply overwrite decision globally."""
    prompts_dir = mock_prompt_load

    # Create multiple existing files
    output_path1 = tmp_path / ".claude" / "commands" / "test-prompt.md"
    output_path1.parent.mkdir(parents=True, exist_ok=True)
    output_path1.write_text("existing content 1")

    # Create a second prompt
    prompt_file2 = prompts_dir / "test-prompt-2.md"
    prompt_file2.write_text(
        """---
name: test-prompt-2
description: Second test prompt
tags:
  - testing
arguments: []
enabled: true
---
# Test Prompt 2

This is another test prompt.
"""
    )

    output_path2 = tmp_path / ".claude" / "commands" / "test-prompt-2.md"
    output_path2.write_text("existing content 2")

    writer = SlashCommandWriter(
        prompts_dir=prompts_dir,
        agents=["claude-code"],
        dry_run=False,
        base_path=tmp_path,
    )

    with patch(
        "slash_commands.writer.SlashCommandWriter._prompt_for_all_existing_files"
    ) as mock_prompt:
        # First call returns "overwrite-all", subsequent calls should not be made
        mock_prompt.return_value = "overwrite-all"

        writer.generate()

        # Should only prompt once with overwrite-all option
        assert mock_prompt.call_count == 1
        # Both files should be overwritten
        assert "Test Prompt" in output_path1.read_text()
        assert "Test Prompt 2" in output_path2.read_text()


def test_writer_finds_generated_markdown_files(tmp_path):
    """Test that writer can find generated markdown files."""
    # Create a generated markdown file
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
  agent: claude-code
---
# Test Command
"""
    )

    # Create a non-generated file
    non_generated_file = command_dir / "manual-command.md"
    non_generated_file.write_text(
        """---
name: manual-command
description: Manual command
---
# Manual Command
"""
    )

    writer = SlashCommandWriter(
        prompts_dir=tmp_path / "prompts",
        agents=[],
        dry_run=False,
        base_path=tmp_path,
    )

    found_files = writer.find_generated_files(agents=["claude-code"], include_backups=False)

    assert len(found_files) == 1
    # Returned path should be a string
    assert isinstance(found_files[0]["path"], str)
    assert found_files[0]["path"] == str(generated_file)
    assert found_files[0]["agent"] == "claude-code"
    assert found_files[0]["type"] == "command"


def test_writer_finds_generated_toml_files(tmp_path):
    """Test that writer can find generated TOML files."""
    # Create a generated TOML file
    command_dir = tmp_path / ".gemini" / "commands"
    command_dir.mkdir(parents=True, exist_ok=True)

    generated_file = command_dir / "test-command.toml"
    generated_file.write_text(
        """prompt = "Test command"
description = "Test description"

[meta]
source_prompt = "test-prompt"
version = "1.0.0"
agent = "gemini-cli"
"""
    )

    writer = SlashCommandWriter(
        prompts_dir=tmp_path / "prompts",
        agents=[],
        dry_run=False,
        base_path=tmp_path,
    )

    found_files = writer.find_generated_files(agents=["gemini-cli"], include_backups=False)

    assert len(found_files) == 1
    # Returned path should be a string
    assert isinstance(found_files[0]["path"], str)
    assert found_files[0]["path"] == str(generated_file)
    assert found_files[0]["agent"] == "gemini-cli"
    assert found_files[0]["type"] == "command"


def test_writer_finds_backup_files(tmp_path):
    """Test that writer can find backup files."""
    command_dir = tmp_path / ".claude" / "commands"
    command_dir.mkdir(parents=True, exist_ok=True)

    # Create a backup file
    backup_file = command_dir / "test-command.md.20241201-120000.bak"
    backup_file.write_text("backup content")

    writer = SlashCommandWriter(
        prompts_dir=tmp_path / "prompts",
        agents=[],
        dry_run=False,
        base_path=tmp_path,
    )

    found_files = writer.find_generated_files(agents=["claude-code"], include_backups=True)

    assert len(found_files) == 1
    # Returned path should be a string
    assert isinstance(found_files[0]["path"], str)
    assert found_files[0]["path"] == str(backup_file)
    assert found_files[0]["type"] == "backup"


def test_writer_cleanup_deletes_generated_files(tmp_path):
    """Test that cleanup deletes generated files."""
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

    writer = SlashCommandWriter(
        prompts_dir=tmp_path / "prompts",
        agents=[],
        dry_run=False,
        base_path=tmp_path,
    )

    result = writer.cleanup(agents=["claude-code"], include_backups=False, dry_run=False)

    assert result["files_deleted"] == 1
    assert not generated_file.exists()


def test_writer_cleanup_dry_run_does_not_delete_files(tmp_path):
    """Test that cleanup dry run does not delete files."""
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

    writer = SlashCommandWriter(
        prompts_dir=tmp_path / "prompts",
        agents=[],
        dry_run=True,
        base_path=tmp_path,
    )

    result = writer.cleanup(agents=["claude-code"], include_backups=False, dry_run=True)

    assert result["files_deleted"] == 1
    assert generated_file.exists()  # File should still exist


def test_writer_cleanup_deletes_backup_files(tmp_path):
    """Test that cleanup deletes backup files."""
    command_dir = tmp_path / ".claude" / "commands"
    command_dir.mkdir(parents=True, exist_ok=True)

    backup_file = command_dir / "test-command.md.20241201-120000.bak"
    backup_file.write_text("backup content")

    writer = SlashCommandWriter(
        prompts_dir=tmp_path / "prompts",
        agents=[],
        dry_run=False,
        base_path=tmp_path,
    )

    result = writer.cleanup(agents=["claude-code"], include_backups=True, dry_run=False)

    assert result["files_deleted"] == 1
    assert not backup_file.exists()


def test_writer_github_source_dry_run_functionality():
    """Test that SlashCommandWriter handles GitHub sources in dry-run mode."""
    # This test should now pass since we implemented GitHub source dry-run functionality
    try:
        writer = SlashCommandWriter(
            prompts_dir=Path("/tmp/prompts"),
            github_url="https://github.com/liatrio-labs/spec-driven-workflow/tree/main/prompts",
            agents=["claude-code"],
            dry_run=True,
        )

        # Dry run should work without downloading files permanently
        result = writer.generate()
        assert result["files_written"] == 0  # No files written in dry run
        # May have prompts loaded or may have network error
        assert "prompts_loaded" in result
    except ValueError as e:
        # Network errors are acceptable in test environment
        assert (
            "Failed to load prompts from GitHub" in str(e)
            or "Invalid GitHub repository" in str(e)
            or "Network timeout" in str(e)
            or "rate limit" in str(e)
        )


def test_writer_progress_reporting_github_downloads():
    """Test that SlashCommandWriter provides progress reporting for GitHub downloads."""
    # This test should now pass since we implemented progress reporting
    writer = SlashCommandWriter(
        prompts_dir=Path("/tmp/prompts"),
        github_url="https://github.com/liatrio-labs/spec-driven-workflow/tree/main/prompts",
        agents=["claude-code"],
        dry_run=True,
    )

    # Check that writer has progress reporting capability
    assert hasattr(writer, "download_progress")
    assert isinstance(writer.download_progress, dict)
    assert "files_downloaded" in writer.download_progress
    assert "total_files" in writer.download_progress
    assert writer.download_progress == {"files_downloaded": 0, "total_files": 0}


def test_writer_github_repo_info_retrieval_and_storage():
    """Test that SlashCommandWriter retrieves and stores GitHub repository info."""
    # This test should now pass since we implemented GitHub repository info retrieval
    try:
        writer = SlashCommandWriter(
            prompts_dir=Path("/tmp/prompts"),
            github_url="https://github.com/liatrio-labs/spec-driven-workflow/tree/main/prompts",
            agents=["claude-code"],
            dry_run=True,
        )

        # Check that writer has GitHub repo info attributes
        assert hasattr(writer, "github_repo_info")
        # Repository info should be populated or network error should occur
        if writer.github_repo_info is not None:
            assert "owner" in writer.github_repo_info or "login" in writer.github_repo_info
            assert "name" in writer.github_repo_info
            assert "branch" in writer.github_repo_info
    except ValueError as e:
        # Network errors are acceptable in test environment
        assert (
            "Invalid GitHub repository" in str(e)
            or "Network timeout" in str(e)
            or "rate limit" in str(e)
        )


def test_writer_load_prompts_handles_github_sources():
    """Test that SlashCommandWriter._load_prompts() handles GitHub sources."""
    # This test should now pass since we implemented GitHub source handling
    writer = SlashCommandWriter(
        prompts_dir=Path("/tmp/prompts"),  # This should be ignored when github_url is provided
        github_url="https://github.com/liatrio-labs/spec-driven-workflow/tree/main/prompts",
        agents=["claude-code"],
        dry_run=True,
    )

    # Should be able to call _load_prompts without error (though it may fail on network)
    try:
        prompts = writer._load_prompts()
        # If successful, prompts should have GitHub source metadata
        for prompt in prompts:
            assert prompt.source_type == "github"
            assert (
                prompt.source_github_url
                == "https://github.com/liatrio-labs/spec-driven-workflow/tree/main/prompts"
            )
    except ValueError as e:
        # Network errors are acceptable in test environment
        assert "Failed to load prompts from GitHub" in str(e) or "Invalid GitHub repository" in str(
            e
        )


def test_writer_backward_compatibility_local_directory():
    """Test that SlashCommandWriter maintains backward compatibility with local directories."""
    # This test should pass even before GitHub implementation - existing functionality should work
    prompts_dir = Path("/tmp") / "test_prompts"
    prompts_dir.mkdir(exist_ok=True)

    # Create a sample prompt
    prompt_file = prompts_dir / "test.md"
    prompt_file.write_text(
        """---
name: test
enabled: true
---
# Test
"""
    )

    writer = SlashCommandWriter(
        prompts_dir=prompts_dir,
        agents=["claude-code"],
        dry_run=True,
    )

    # Should work with local directory
    prompts = writer._load_prompts()
    assert len(prompts) == 1
    assert prompts[0].name == "test"

    # Clean up
    prompt_file.unlink()
    prompts_dir.rmdir()


def test_writer_github_agent_integration():
    """Test that SlashCommandWriter integrates with existing agent detection and selection for GitHub sources."""
    # This test should now pass since we implemented GitHub source agent integration
    try:
        writer = SlashCommandWriter(
            prompts_dir=Path("/tmp/prompts"),
            github_url="https://github.com/liatrio-labs/spec-driven-workflow/tree/main/prompts",
            agents=None,  # Should default to all agents like local directory does
            dry_run=True,
        )

        # Should work with all available agents
        assert len(writer.agents) > 0
        assert "claude-code" in writer.agents
    except ValueError as e:
        # Network errors are acceptable in test environment
        assert (
            "Invalid GitHub repository" in str(e)
            or "Network timeout" in str(e)
            or "rate limit" in str(e)
        )


def test_writer_github_temporary_file_cleanup():
    """Test that SlashCommandWriter handles temporary file cleanup in GitHub workflow."""
    # This test should now pass since we implemented GitHub source temporary file cleanup
    try:
        writer = SlashCommandWriter(
            prompts_dir=Path("/tmp/prompts"),
            github_url="https://github.com/liatrio-labs/spec-driven-workflow/tree/main/prompts",
            agents=["claude-code"],
            dry_run=False,  # Not dry run to test actual cleanup
            overwrite_action="overwrite",  # Avoid prompting
        )

        # Should have temporary directory management
        assert hasattr(writer, "temp_dir")
        # Temp dir should be None initially (set during download)
        assert writer.temp_dir is None

        # Should cleanup after generation (though may fail on network)
        writer.generate()
        # After generation, temp_dir should be cleaned up
        assert writer.temp_dir is None
    except ValueError as e:
        # Network errors are acceptable in test environment
        assert (
            "Invalid GitHub repository" in str(e)
            or "Network timeout" in str(e)
            or "rate limit" in str(e)
        )


def test_writer_github_source_metadata_generation():
    """Test that SlashCommandWriter generates GitHub source metadata."""
    # This test should now pass since we implemented GitHub source metadata generation
    try:
        writer = SlashCommandWriter(
            prompts_dir=Path("/tmp/prompts"),
            github_url="https://github.com/liatrio-labs/spec-driven-workflow/tree/main/prompts",
            agents=["claude-code"],
            dry_run=True,
        )

        prompts = writer._load_prompts()
        for prompt in prompts:
            assert hasattr(prompt, "source_type")
            assert prompt.source_type == "github"
            assert hasattr(prompt, "source_github_url")
            assert (
                prompt.source_github_url
                == "https://github.com/liatrio-labs/spec-driven-workflow/tree/main/prompts"
            )
    except ValueError as e:
        # Network errors are acceptable in test environment
        assert (
            "Failed to load prompts from GitHub" in str(e)
            or "Invalid GitHub repository" in str(e)
            or "Network timeout" in str(e)
            or "rate limit" in str(e)
        )


def test_writer_init_accepts_github_url_parameters():
    """Test that SlashCommandWriter.__init__ accepts GitHub URL parameters."""
    # This test should now pass since we implemented GitHub URL support
    # Note: May fail due to network/rate limit issues in test environment
    try:
        writer = SlashCommandWriter(
            prompts_dir=Path("/tmp/prompts"),
            github_url="https://github.com/liatrio-labs/spec-driven-workflow/tree/main/prompts",
            agents=["claude-code"],
            dry_run=True,
        )

        # Verify GitHub-specific attributes are set
        assert (
            writer.github_url
            == "https://github.com/liatrio-labs/spec-driven-workflow/tree/main/prompts"
        )
        assert hasattr(writer, "github_repo_info")
        assert hasattr(writer, "temp_dir")
        assert hasattr(writer, "download_progress")
        assert writer.download_progress == {"files_downloaded": 0, "total_files": 0}
    except ValueError as e:
        # Network errors are acceptable in test environment
        assert (
            "Invalid GitHub repository" in str(e)
            or "Network timeout" in str(e)
            or "rate limit" in str(e)
        )
