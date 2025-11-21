# 08 Task 03 Proofs - Flag Integration and Output Replacement

## Test Results

### Integration Tests

All integration tests for the `--all-files` flag pass successfully:

```bash
python -m pytest tests/integration/test_list_command.py -m integration -v
```

**Output:**

```text
tests/integration/test_list_command.py::test_list_cmd_with_all_files_flag PASSED
tests/integration/test_list_command.py::test_list_cmd_all_files_respects_agent_flag PASSED
tests/integration/test_list_command.py::test_list_cmd_all_files_respects_target_path_flag PASSED
tests/integration/test_list_command.py::test_list_cmd_all_files_respects_detection_path_flag PASSED

============================= 14 passed in 31.46s ==============================
```

### Unit Tests

All unit tests for list discovery pass:

```bash
python -m pytest tests/test_list_discovery.py tests/integration/test_list_command.py -v
```

**Output:**

```text
====================== 45 passed, 14 deselected in 0.18s =======================
```

## CLI Help Output

The `--all-files` flag is properly documented in the CLI help:

```bash
python -m slash_commands.cli list --help
```

**Output:**

```text
 Usage: python -m slash_commands.cli list [OPTIONS]

 List all managed slash commands.

╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --agent           -a      TEXT  Agent key to list prompts for (can be        │
│                                 specified multiple times)                    │
│ --target-path     -t      PATH  Target directory for searching agent command │
│                                 directories (defaults to home directory)     │
│ --detection-path  -d      PATH  Directory to search for agent configurations │
│                                 (defaults to home directory)                 │
│ --all-files                     List all files in agent command directories, │
│                                 not just managed prompts                     │
│ --help                          Show this message and exit.                  │
╰──────────────────────────────────────────────────────────────────────────────╯
```

## Code Quality

### Ruff Check

```bash
ruff check slash_commands/cli.py tests/integration/test_list_command.py
```

**Output:**

```text
All checks passed!
```

### Ruff Format

```bash
ruff format slash_commands/cli.py tests/integration/test_list_command.py
```

**Output:**

```text
2 files left unchanged
```

## Implementation Details

### Flag Parameter Added

The `all_files` parameter was added to `list_cmd()` function in `slash_commands/cli.py`:

```python
all_files: Annotated[
    bool,
    typer.Option(
        "--all-files",
        help="List all files in agent command directories, not just managed prompts",
    ),
] = False,
```

### Conditional Logic Implemented

The function now checks the `all_files` flag and calls the appropriate discovery and rendering functions:

- When `all_files` is `True`: Uses `discover_all_files()` and `render_all_files_tables()`
- When `all_files` is `False`: Uses `discover_managed_prompts()` and `render_list_tree()` (existing behavior)

### Agent Detection Logic

The agent detection logic works the same way for both standard and `--all-files` modes:

- Uses `detect_agents()` when agents are not specified
- Filters by `selected_agents` list when agents are specified
- Handles invalid agent keys with proper error messages

## Verification

### Test Coverage

All required tests pass:

- ✅ `test_list_cmd_with_all_files_flag()` - Verifies flag executes and shows table output
- ✅ `test_list_cmd_all_files_respects_agent_flag()` - Verifies agent filtering works
- ✅ `test_list_cmd_all_files_respects_target_path_flag()` - Verifies target-path flag works
- ✅ `test_list_cmd_all_files_respects_detection_path_flag()` - Verifies detection-path flag works

### Functionality Verification

- ✅ Flag parsing works correctly
- ✅ Table output replaces tree output when flag is used
- ✅ Existing flags (`--agent`, `--target-path`, `--detection-path`) work with `--all-files`
- ✅ Help output shows flag documentation
- ✅ Code quality checks pass
- ✅ No regressions in existing functionality

## Related to T03 in Spec 08

This task completes the flag integration and output replacement functionality, allowing users to list all files in agent command directories with proper classification and formatting.
