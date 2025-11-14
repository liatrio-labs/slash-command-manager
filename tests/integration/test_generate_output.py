"""Snapshot tests for the Rich generation summary."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from typer.testing import CliRunner

from slash_commands.cli import app
from tests.integration.conftest import REPO_ROOT

runner = CliRunner()


def _extract_summary(output: str) -> str:
    try:
        start = output.index("╭")
        end = output.rindex("╯")
    except ValueError as err:
        raise AssertionError("Generation summary panel not found") from err
    block = output[start : end + 1]
    return "\n".join(line.rstrip() for line in block.splitlines())


def _normalize_summary(summary: str, target_path: Path) -> str:
    normalized = summary.replace(str(REPO_ROOT), "<repo>")
    normalized = normalized.replace(str(target_path), "<target>")
    normalized = re.sub(r"\.\d{8}-\d{6}\.bak", ".<timestamp>.bak", normalized)
    normalized = re.sub(r"(Directory: <target>) +│", r"\1 │", normalized)
    return normalized


EXPECTED_REAL_RUN = """╭──────────────────────────── Generation Summary ────────────────────────────╮
│ Generation (safe mode) Summary                                             │
│ ├── Counts                                                                 │
│ │   ├── Prompts loaded: 3                                                  │
│ │   ├── Files planned: 3                                                   │
│ │   └── Files written: 3                                                   │
│ ├── Agents                                                                 │
│ │   ├── Detected                                                           │
│ │   │   └── claude-code                                                    │
│ │   └── Selected                                                           │
│ │       └── claude-code                                                    │
│ ├── Source                                                                 │
│ │   └── Directory: tests/integration/fixtures/prompts                      │
│ ├── Output                                                                 │
│ │   └── Directory: <target> │
│ ├── Backups                                                                │
│ │   ├── Created: 0                                                         │
│ │   └── Pending: 0                                                         │
│ ├── Files                                                                  │
│ │   └── Claude Code (claude-code) • 3 file(s)                              │
│ │       ├── .claude/commands/test-prompt-1.md                              │
│ │       ├── .claude/commands/test-prompt-2.md                              │
│ │       └── .claude/commands/test-prompt-3.md                              │
│ └── Prompts                                                                │
│     ├── test-prompt-1: tests/integration/fixtures/prompts/test-prompt-1.md │
│     ├── test-prompt-2: tests/integration/fixtures/prompts/test-prompt-2.md │
│     └── test-prompt-3: tests/integration/fixtures/prompts/test-prompt-3.md │
╰────────────────────────────────────────────────────────────────────────────╯"""


EXPECTED_BACKUP_RUN = """╭──────────────────────────── Generation Summary ────────────────────────────╮
│ Generation (safe mode) Summary                                             │
│ ├── Counts                                                                 │
│ │   ├── Prompts loaded: 3                                                  │
│ │   ├── Files planned: 3                                                   │
│ │   └── Files written: 3                                                   │
│ ├── Agents                                                                 │
│ │   ├── Detected                                                           │
│ │   │   └── claude-code                                                    │
│ │   └── Selected                                                           │
│ │       └── claude-code                                                    │
│ ├── Source                                                                 │
│ │   └── Directory: tests/integration/fixtures/prompts                      │
│ ├── Output                                                                 │
│ │   └── Directory: <target> │
│ ├── Backups                                                                │
│ │   ├── Created: 3                                                         │
│ │   │   ├── .claude/commands/test-prompt-1.md.<timestamp>.bak          │
│ │   │   ├── .claude/commands/test-prompt-2.md.<timestamp>.bak          │
│ │   │   └── .claude/commands/test-prompt-3.md.<timestamp>.bak          │
│ │   └── Pending: 0                                                         │
│ ├── Files                                                                  │
│ │   └── Claude Code (claude-code) • 3 file(s)                              │
│ │       ├── .claude/commands/test-prompt-1.md                              │
│ │       ├── .claude/commands/test-prompt-2.md                              │
│ │       └── .claude/commands/test-prompt-3.md                              │
│ └── Prompts                                                                │
│     ├── test-prompt-1: tests/integration/fixtures/prompts/test-prompt-1.md │
│     ├── test-prompt-2: tests/integration/fixtures/prompts/test-prompt-2.md │
│     └── test-prompt-3: tests/integration/fixtures/prompts/test-prompt-3.md │
╰────────────────────────────────────────────────────────────────────────────╯"""


EXPECTED_DRY_RUN = """╭──────────────────────────── Generation Summary ────────────────────────────╮
│ DRY RUN (safe mode) Summary                                                │
│ ├── Counts                                                                 │
│ │   ├── Prompts loaded: 3                                                  │
│ │   ├── Files planned: 3                                                   │
│ │   └── Files written: 0                                                   │
│ ├── Agents                                                                 │
│ │   ├── Detected                                                           │
│ │   │   └── claude-code                                                    │
│ │   └── Selected                                                           │
│ │       └── claude-code                                                    │
│ ├── Source                                                                 │
│ │   └── Directory: tests/integration/fixtures/prompts                      │
│ ├── Output                                                                 │
│ │   └── Directory: <target> │
│ ├── Backups                                                                │
│ │   ├── Created: 0                                                         │
│ │   └── Pending: 3                                                         │
│ │       ├── .claude/commands/test-prompt-1.md                              │
│ │       ├── .claude/commands/test-prompt-2.md                              │
│ │       └── .claude/commands/test-prompt-3.md                              │
│ ├── Files                                                                  │
│ │   └── Claude Code (claude-code) • 3 file(s)                              │
│ │       ├── .claude/commands/test-prompt-1.md                              │
│ │       ├── .claude/commands/test-prompt-2.md                              │
│ │       └── .claude/commands/test-prompt-3.md                              │
│ └── Prompts                                                                │
│     ├── test-prompt-1: tests/integration/fixtures/prompts/test-prompt-1.md │
│     ├── test-prompt-2: tests/integration/fixtures/prompts/test-prompt-2.md │
│     └── test-prompt-3: tests/integration/fixtures/prompts/test-prompt-3.md │
╰────────────────────────────────────────────────────────────────────────────╯"""


@pytest.mark.integration
def test_rich_summary_real_run_snapshot(temp_test_dir: Path, test_prompts_dir: Path):
    result = runner.invoke(
        app,
        [
            "generate",
            "--prompts-dir",
            str(test_prompts_dir),
            "--agent",
            "claude-code",
            "--target-path",
            str(temp_test_dir),
            "--yes",
        ],
    )
    assert result.exit_code == 0
    summary = _normalize_summary(_extract_summary(result.output), temp_test_dir)
    assert summary == EXPECTED_REAL_RUN


@pytest.mark.integration
def test_rich_summary_backup_counts_snapshot(temp_test_dir: Path, test_prompts_dir: Path):
    seed = runner.invoke(
        app,
        [
            "generate",
            "--prompts-dir",
            str(test_prompts_dir),
            "--agent",
            "claude-code",
            "--target-path",
            str(temp_test_dir),
            "--yes",
        ],
    )
    assert seed.exit_code == 0

    result = runner.invoke(
        app,
        [
            "generate",
            "--prompts-dir",
            str(test_prompts_dir),
            "--agent",
            "claude-code",
            "--target-path",
            str(temp_test_dir),
            "--yes",
        ],
    )
    assert result.exit_code == 0
    summary = _normalize_summary(_extract_summary(result.output), temp_test_dir)
    assert summary == EXPECTED_BACKUP_RUN


@pytest.mark.integration
def test_rich_summary_dry_run_pending_backups(temp_test_dir: Path, test_prompts_dir: Path):
    seed = runner.invoke(
        app,
        [
            "generate",
            "--prompts-dir",
            str(test_prompts_dir),
            "--agent",
            "claude-code",
            "--target-path",
            str(temp_test_dir),
            "--yes",
        ],
    )
    assert seed.exit_code == 0

    result = runner.invoke(
        app,
        [
            "generate",
            "--prompts-dir",
            str(test_prompts_dir),
            "--agent",
            "claude-code",
            "--target-path",
            str(temp_test_dir),
            "--dry-run",
            "--yes",
        ],
    )
    assert result.exit_code == 0
    summary = _normalize_summary(_extract_summary(result.output), temp_test_dir)
    assert summary == EXPECTED_DRY_RUN
