# Task 2.0 Proof Artifacts: Prompt Discovery and Filtering Logic

## Test Results

### Unit Tests - Prompt Discovery

```bash
pytest tests/test_list_discovery.py -k "discover_managed_prompts" -v
```

Output:

```text
============================= test session starts ==============================
platform linux -- Python 3.12.6, pytest-8.4.2, pluggy-1.5.0
collecting ... collected 10 items

tests/test_list_discovery.py::test_discover_managed_prompts_finds_files_with_managed_by PASSED [ 10%]
tests/test_list_discovery.py::test_discover_managed_prompts_excludes_files_without_managed_by PASSED [ 20%]
tests/test_list_discovery.py::test_discover_managed_prompts_handles_markdown_format PASSED [ 30%]
tests/test_list_discovery.py::test_discover_managed_prompts_handles_toml_format PASSED [ 40%]
tests/test_list_discovery.py::test_discover_managed_prompts_excludes_backup_files PASSED [ 50%]
tests/test_list_discovery.py::test_discover_managed_prompts_handles_empty_directories PASSED [ 60%]
tests/test_list_discovery.py::test_discover_managed_prompts_handles_multiple_agents PASSED [ 70%]
tests/test_list_discovery.py::test_discover_managed_prompts_handles_malformed_frontmatter PASSED [ 80%]
tests/test_list_discovery.py::test_discover_managed_prompts_handles_unicode_errors PASSED [ 90%]
tests/test_list_discovery.py::test_discover_managed_prompts_handles_permission_errors PASSED [100%]

============================== 10 passed in 0.05s ===============================
```

### Unit Tests - Unmanaged Prompt Counting

```bash
pytest tests/test_list_discovery.py -k "count_unmanaged_prompts" -v
```

Output:

```text
============================= test session starts ==============================
platform linux -- Python 3.12.6, pytest-8.4.2, pluggy-1.5.0
collecting ... collected 4 items

tests/test_list_discovery.py::test_count_unmanaged_prompts_counts_valid_prompts_without_managed_by PASSED [ 25%]
tests/test_list_discovery.py::test_count_unmanaged_prompts_excludes_backup_files PASSED [ 50%]
tests/test_list_discovery.py::test_count_unmanaged_prompts_excludes_managed_files PASSED [ 75%]
tests/test_list_discovery.py::test_count_unmanaged_prompts_excludes_invalid_files PASSED [100%]

============================== 4 passed in 0.02s ===============================
```

### Integration Tests

```bash
pytest tests/integration/test_list_command.py::test_list_discovers_managed_prompts -v -m integration
```

Output:

```text
============================= test session starts ==============================
platform linux -- Python 3.12.6, pytest-8.4.2, pluggy-1.5.0
collecting ... collected 1 item

tests/integration/test_list_command.py::test_list_discovers_managed_prompts PASSED [100%]

============================== 1 passed in 2.05s ===============================
```

## CLI Transcript - Prompt Discovery

### Setup: Generate Managed Prompts

```bash
cd /tmp/list-proof-test
python -m slash_commands.cli generate \
  --prompts-dir test-prompts \
  --agent cursor \
  --agent claude-code \
  --target-path /tmp/list-proof-test \
  --yes
```

Output:

```text
Selected agents: cursor, claude-code
Running in non-interactive safe mode: backups will be created before overwriting.
╭───────────────────────── Generation Summary ──────────────────────────╮
│ Generation (safe mode) Summary                                        │
│ ├── Counts                                                            │
│ │   ├── Prompts loaded: 1                                             │
│ │   ├── Files planned: 2                                              │
│ │   └── Files written: 2                                              │
│ ├── Agents                                                            │
│ │   ├── Detected                                                      │
│ │   │   ├── cursor                                                    │
│ │   │   └── claude-code                                               │
│ │   └── Selected                                                      │
│ │       ├── cursor                                                    │
│ │       └── claude-code                                               │
│ ├── Source                                                            │
│ │   └── Directory: /tmp/list-proof-test/test-prompts                  │
│ ├── Output                                                            │
│ │   └── Directory: /tmp/list-proof-test                               │
│ ├── Backups                                                           │
│ │   ├── Created: 2                                                    │
│ │   │   ├── .cursor/commands/test-prompt.md.20251114-221150.bak       │
│ │   │   └── .claude/commands/test-prompt.md.20251114-221150.bak       │
│ │   └── Pending: 0                                                    │
│ ├── Files                                                             │
│ │   ├── Cursor (cursor) • 1 file(s)                                   │
│ │   │   └── .cursor/commands/test-prompt.md                           │
│ │   └── Claude Code (claude-code) • 1 file(s)                         │
│ │       └── .claude/commands/test-prompt.md                           │
│ └── Prompts                                                           │
│     └── test-prompt: /tmp/list-proof-test/test-prompts/test-prompt.md │
╰───────────────────────────────────────────────────────────────────────╯

Generation complete:
  Prompts loaded: 1
  Files written: 2
```

### Run List Command to Discover Prompts

```bash
python -m slash_commands.cli list \
  --target-path /tmp/list-proof-test \
  --detection-path /tmp/list-proof-test
```

Output:

```text
╭────────────────────────────── List Summary ──────────────────────────────╮
│ Managed Prompts                                                          │
│ ├── Prompts                                                              │
│ │   └── test-prompt                                                      │
│ │       ├── Source: local: /tmp/list-proof-test/test-prompts             │
│ │       ├── Updated: 2025-11-14T22:11:50.058023+00:00                    │
│ │       └── Agents (2)                                                   │
│ │           ├── Claude Code (claude-code) • 1 backup                     │
│ │           │   └── /tmp/list-proof-test/.claude/commands/test-prompt.md │
│ │           └── Cursor (cursor) • 1 backup                               │
│ │               └── /tmp/list-proof-test/.cursor/commands/test-prompt.md │
│ └── Unmanaged Prompts                                                    │
╰──────────────────────────────────────────────────────────────────────────╯
```

**Verification:**

- ✅ Successfully discovers managed prompts across multiple agent directories (cursor and claude-code)
- ✅ Groups prompts by name (test-prompt appears once, not per agent)
- ✅ Shows both agents where the prompt is installed
- ✅ Displays file paths for each agent
- ✅ Shows backup counts (1 backup per file)
- ✅ Displays source information (local source)
- ✅ Shows updated timestamp
- ✅ Unmanaged prompts section is present (empty in this case)
