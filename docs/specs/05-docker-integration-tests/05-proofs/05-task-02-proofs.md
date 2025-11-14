# Proof Artifacts: Task 2.0 - Basic CLI Command Tests

## Test Results

### Test Execution Output

```bash
docker run --rm --entrypoint="" slash-man-test sh -c "cd /app && /usr/local/bin/python -m uv run pytest tests/integration/test_basic_commands.py -v -m integration"
```

```text
============================= test session starts ==============================
platform linux -- Python 3.12.12, pytest-8.4.2, pluggy-1.6.0 -- /app/.venv/bin/python
cachedir: .pytest_cache
rootdir: /app
configfile: pyproject.toml
plugins: cov-7.0.0, httpx-0.35.0, anyio-4.11.0
collecting ... collected 6 items

tests/integration/test_basic_commands.py::test_main_help_command PASSED  [ 16%]
tests/integration/test_basic_commands.py::test_main_version_command PASSED [ 33%]
tests/integration/test_basic_commands.py::test_generate_help_command PASSED [ 50%]
tests/integration/test_basic_commands.py::test_cleanup_help_command PASSED [ 66%]
tests/integration/test_basic_commands.py::test_mcp_help_command PASSED   [ 83%]
tests/integration/test_basic_commands.py::test_list_agents_command PASSED [100%]

============================== 6 passed in 7.35s ===============================
```

## CLI Output Examples

### Main Help Command

```bash
slash-man --help
```

```text
Usage: slash-man [OPTIONS] COMMAND [ARGS]...

Manage slash commands for the spec-driven workflow in your AI assistants

╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --version             -v        Show version and exit                        │
│ --install-completion            Install completion for the current shell.    │
│ --show-completion               Show completion for the current shell, to    │
│                                 copy it or customize the installation.       │
│ --help                          Show this message and exit.                  │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ generate   Generate slash commands for AI code assistants.                   │
│ cleanup    Clean up generated slash commands.                                │
│ mcp        Start the MCP server for spec-driven development workflows.       │
╰──────────────────────────────────────────────────────────────────────────────╯
```

### Version Command

```bash
slash-man --version
```

```text
slash-man 0.1.0
```

### List Agents Command

```bash
slash-man generate --list-agents
```

```text
                                Supported Agents
┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Agent Key   ┃ Display Name ┃ Target Path                          ┃ Detected ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ claude-code │ Claude Code  │ ~/.claude/commands                   │    ✗     │
│ codex-cli   │ Codex CLI    │ ~/.codex/prompts                     │    ✗     │
│ cursor      │ Cursor       │ ~/.cursor/commands                   │    ✗     │
│ gemini-cli  │ Gemini CLI   │ ~/.gemini/commands                   │    ✗     │
│ opencode    │ OpenCode CLI │ ~/.config/opencode/command           │    ✗     │
│ vs-code     │ VS Code      │ ~/.config/Code/User/prompts          │    ✗     │
│ windsurf    │ Windsurf     │ ~/.codeium/windsurf/global_workflows │    ✗     │
└─────────────┴──────────────┴──────────────────────────────────────┴──────────┘
```

## Exit Code Verification

All tests verify exit code is 0 for success cases:

- `test_main_help_command`: ✅ Exit code 0
- `test_main_version_command`: ✅ Exit code 0
- `test_generate_help_command`: ✅ Exit code 0
- `test_cleanup_help_command`: ✅ Exit code 0
- `test_mcp_help_command`: ✅ Exit code 0
- `test_list_agents_command`: ✅ Exit code 0

## Test File

Created: `tests/integration/test_basic_commands.py`

The test file includes:

- Helper function `_get_slash_man_command()` to locate the slash-man executable
- 6 test functions covering all basic CLI commands
- Exact text matching for output validation
- Exit code verification for all commands

## Demo Validation

✅ **Tests verify `slash-man --help` produces correct help output**: Test passes with exact text matching
✅ **Tests verify `slash-man --version` outputs version string**: Test passes, verifies "slash-man" and "0.1.0" in output
✅ **Tests verify `slash-man generate --help` shows generate command help**: Test passes with expected strings
✅ **Tests verify `slash-man cleanup --help` shows cleanup command help**: Test passes with expected strings
✅ **Tests verify `slash-man mcp --help` shows mcp command help**: Test passes with expected strings
✅ **Tests verify `slash-man generate --list-agents` lists all supported agents**: Test passes, verifies all 7 agent keys and display names
✅ **All tests run successfully inside Docker container**: All 6 tests pass using subprocess execution
