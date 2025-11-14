# 06-Task-04 Proofs

## CLI Output – Real Run (Docker)

```bash
docker run --rm --entrypoint="" slash-man-test sh -c '
set -euo pipefail
cd /app
TARGET=/tmp/task4-real
rm -rf "$TARGET"
uv run slash-man generate --prompts-dir tests/integration/fixtures/prompts --agent claude-code --target-path "$TARGET" --yes
'

Selected agents: claude-code
Running in non-interactive safe mode: backups will be created before overwriting.
╭───────────────────────────────────────────────── Generation Summary ─────────────────────────────────────────────────╮
│ Generation (safe mode) Summary                                                                                       │
│ ├── Counts                                                                                                           │
│ │   ├── Prompts loaded: 3                                                                                            │
│ │   ├── Files planned: 3                                                                                             │
│ │   └── Files written: 3                                                                                             │
│ ├── Agents                                                                                                           │
│ │   ├── Detected                                                                                                     │
│ │   │   └── claude-code                                                                                              │
│ │   └── Selected                                                                                                     │
│ │       └── claude-code                                                                                              │
│ ├── Source                                                                                                           │
│ │   └── Directory: tests/integration/fixtures/prompts                                                                │
│ ├── Output                                                                                                           │
│ │   └── Directory: /tmp/task4-real                                                                                   │
│ ├── Backups                                                                                                          │
│ │   ├── Created: 0                                                                                                   │
│ │   └── Pending: 0                                                                                                   │
│ ├── Files                                                                                                            │
│ │   └── Claude Code (claude-code) • 3 file(s)                                                                        │
│ │       ├── .claude/commands/test-prompt-1.md                                                                        │
│ │       ├── .claude/commands/test-prompt-2.md                                                                        │
│ │       └── .claude/commands/test-prompt-3.md                                                                        │
│ └── Prompts                                                                                                          │
│     ├── test-prompt-1: tests/integration/fixtures/prompts/test-prompt-1.md                                           │
│     ├── test-prompt-2: tests/integration/fixtures/prompts/test-prompt-2.md                                           │
│     └── test-prompt-3: tests/integration/fixtures/prompts/test-prompt-3.md                                           │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## CLI Output – Dry Run (Docker)

```bash
docker run --rm --entrypoint="" slash-man-test sh -c '
set -euo pipefail
cd /app
TARGET=/tmp/task4-dry
rm -rf "$TARGET"
uv run slash-man generate --prompts-dir tests/integration/fixtures/prompts --agent claude-code --target-path "$TARGET" --yes >/dev/null
uv run slash-man generate --prompts-dir tests/integration/fixtures/prompts --agent claude-code --target-path "$TARGET" --dry-run --yes
'

Selected agents: claude-code
Running in non-interactive safe mode: backups will be created before overwriting.
╭───────────────────────────────────────────────── Generation Summary ─────────────────────────────────────────────────╮
│ DRY RUN (safe mode) Summary                                                                                          │
│ ├── Counts                                                                                                           │
│ │   ├── Prompts loaded: 3                                                                                            │
│ │   ├── Files planned: 3                                                                                             │
│ │   └── Files written: 0                                                                                             │
│ ├── Agents                                                                                                           │
│ │   ├── Detected                                                                                                     │
│ │   │   └── claude-code                                                                                              │
│ │   └── Selected                                                                                                     │
│ │       └── claude-code                                                                                              │
│ ├── Source                                                                                                           │
│ │   └── Directory: tests/integration/fixtures/prompts                                                                │
│ ├── Output                                                                                                           │
│ │   └── Directory: /tmp/task4-dry                                                                                    │
│ ├── Backups                                                                                                          │
│ │   ├── Created: 0                                                                                                   │
│ │   └── Pending: 3                                                                                                   │
│ │       ├── .claude/commands/test-prompt-1.md                                                                        │
│ │       ├── .claude/commands/test-prompt-2.md                                                                        │
│ │       └── .claude/commands/test-prompt-3.md                                                                        │
│ ├── Files                                                                                                            │
│ │   └── Claude Code (claude-code) • 3 file(s)                                                                        │
│ │       ├── .claude/commands/test-prompt-1.md                                                                        │
│ │       ├── .claude/commands/test-prompt-2.md                                                                        │
│ │       └── .claude/commands/test-prompt-3.md                                                                        │
│ └── Prompts                                                                                                          │
│     ├── test-prompt-1: tests/integration/fixtures/prompts/test-prompt-1.md                                           │
│     ├── test-prompt-2: tests/integration/fixtures/prompts/test-prompt-2.md                                           │
│     └── test-prompt-3: tests/integration/fixtures/prompts/test-prompt-3.md                                           │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## Tests

```bash
uv run pytest tests/integration/test_generate_output.py -m integration
============================== 3 passed in 0.12s ===============================

uv run pytest tests/test_writer.py tests/test_cli.py tests/test_single_overwrite_prompt.py
============================== 78 passed in 0.98s ==============================
```
