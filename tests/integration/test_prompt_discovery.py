"""Integration tests covering prompt discovery failures."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from slash_commands.cli import app


@pytest.mark.integration
def test_zero_prompts_local_directory_fails(temp_test_dir: Path):
    """Empty prompts directory should fail with actionable messaging."""
    empty_prompts = temp_test_dir / "empty-prompts"
    empty_prompts.mkdir()
    target_path = temp_test_dir / "target"

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "generate",
            "--prompts-dir",
            str(empty_prompts),
            "--agent",
            "claude-code",
            "--target-path",
            str(target_path),
            "--yes",
        ],
    )

    assert result.exit_code == 1
    combined = result.output.lower()
    assert "no prompts were discovered" in combined
    assert "prompts loaded: 0" in combined
    assert "--prompts-dir" in combined


@pytest.mark.integration
def test_zero_prompts_github_download_fails(temp_test_dir: Path):
    """GitHub downloads that return zero prompts should fail with guidance."""
    target_path = temp_test_dir / "target"
    target_path.mkdir()

    def _no_prompts(temp_dir: Path, *_args, **_kwargs) -> None:
        Path(temp_dir).mkdir(parents=True, exist_ok=True)

    runner = CliRunner()
    with patch(
        "slash_commands.writer._download_github_prompts_to_temp_dir", side_effect=_no_prompts
    ):
        result = runner.invoke(
            app,
            [
                "generate",
                "--github-repo",
                "owner/repo",
                "--github-branch",
                "main",
                "--github-path",
                "prompts",
                "--agent",
                "claude-code",
                "--target-path",
                str(target_path),
                "--yes",
            ],
        )

    assert result.exit_code == 1
    combined = result.output.lower()
    assert "no prompts were discovered" in combined
    assert "prompts loaded: 0" in combined
    assert "github" in combined
