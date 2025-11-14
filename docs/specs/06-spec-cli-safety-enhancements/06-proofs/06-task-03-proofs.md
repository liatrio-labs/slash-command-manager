# 06-Task-03 Proofs

## Zero-Prompt Failure (Docker)

```bash
docker run --rm --entrypoint="" slash-man-test sh -c '
set -euo pipefail
cd /app
EMPTY=/tmp/empty-prompts
rm -rf "$EMPTY"
mkdir -p "$EMPTY"
set +e
uv run slash-man generate --prompts-dir "$EMPTY" --agent claude-code --target-path /tmp/zero-test --yes
status=$?
set -e
echo "exit code: $status"
exit "$status"
'

Selected agents: claude-code
Running in non-interactive safe mode: backups will be created before overwriting.
╭───────────────────────────── Generation Summary ─────────────────────────────╮
│ Prompts loaded: 0                                                            │
│ Files written: 0                                                             │
│ Backups created: 0                                                           │
╰──────────────────────────────────────────────────────────────────────────────╯
Error: No prompts were discovered.
Source directory: /tmp/empty-prompts

To fix this:
  - Ensure the prompts directory contains .md files
  - Provide --prompts-dir pointing to a populated directory
  - Or use --github-repo/--github-branch/--github-path to pull prompts
exit code: 1
```

## Tests

```bash
uv run pytest tests/test_writer.py tests/test_cli.py tests/test_single_overwrite_prompt.py
============================== 78 passed in 0.81s ==============================

uv run pytest tests/integration/test_prompt_discovery.py -m integration
============================== 2 passed in 0.05s ===============================
```
