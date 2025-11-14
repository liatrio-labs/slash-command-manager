# 06-Task-02 Proofs

## CLI Help (Docker)

```bash
docker run --rm slash-man-test generate --help

Usage: slash-man generate [OPTIONS]

Generate slash commands for AI code assistants.

--prompts-dir  Directory containing prompt files
--agent        Agent key to generate commands for (can be specified multiple times)
--dry-run      Show what would be done without writing files
--yes          Skip confirmation prompts (forces backup-safe mode)
--target-path  Target directory for output paths (defaults to home directory)
--detection-path  Directory to search for agent configurations (defaults to home directory)
--list-agents  List all supported agents and exit
--github-repo  GitHub repository in format owner/repo
--github-branch  GitHub branch name (e.g., main, release/v1.0)
--github-path  Path to prompts directory or single prompt file within repository
--help         Show this message and exit.
```

## Safe Mode Run (Docker)

```bash
docker run --rm --entrypoint="" slash-man-test sh -c '
set -euo pipefail
cd /app
TARGET=/tmp/safe-mode-demo
rm -rf "$TARGET"
uv run slash-man generate --agent claude-code --yes --prompts-dir tests/integration/fixtures/prompts --target-path "$TARGET"
'

Selected agents: claude-code
Running in non-interactive safe mode: backups will be created before overwriting.

Generation complete:
  Prompts loaded: 3
  Files  written: 3
```

## Tests

```bash
uv run pytest tests/test_writer.py tests/test_single_overwrite_prompt.py tests/test_cli.py
============================== 78 passed in 0.86s ==============================

uv run pytest tests/integration/test_overwrite_prompt.py -m integration
============================== 1 passed in 2.73s ===============================
```
