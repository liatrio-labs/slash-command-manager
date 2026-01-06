# Task 1.0 Proof Artifacts: VS Code Insiders Agent Configuration

## Configuration Code

VS Code Insiders configuration added to `slash_commands/config.py`:

```python
(
    "vs-code-insiders",
    "VS Code Insiders",
    ".config/Code - Insiders/User/prompts",
    CommandFormat.MARKDOWN,
    ".prompt.md",
    (
        ".config/Code - Insiders",
        "Library/Application Support/Code - Insiders",
        "AppData/Roaming/Code - Insiders",
    ),
    {
        "linux": ".config/Code - Insiders/User/prompts",
        "darwin": "Library/Application Support/Code - Insiders/User/prompts",
        "win32": "AppData/Roaming/Code - Insiders/User/prompts",
    },
),
```

### Verification

- ✅ Key: `vs-code-insiders`
- ✅ Display name: `VS Code Insiders`
- ✅ File extension: `.prompt.md`
- ✅ Format: `CommandFormat.MARKDOWN`
- ✅ Platform-specific command directories configured for linux, darwin, win32
- ✅ Detection directories cover all three platforms

## CLI Output - Agent Discoverability

Command: `uv run slash-man generate --list-agents`

```
                                               Supported Agents            
                                                                           
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Agent Key        ┃ Display Name     ┃ Target Path                                                ┃ Detected ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ amazon-q         │ Amazon Q         │ ~/.aws/amazonq/prompts                                     │    ✗     │
│ claude-code      │ Claude Code      │ ~/.claude/commands                                         │    ✗     │
│ codex-cli        │ Codex CLI        │ ~/.codex/prompts                                           │    ✗     │
│ cursor           │ Cursor           │ ~/.cursor/commands                                         │    ✗     │
│ gemini-cli       │ Gemini CLI       │ ~/.gemini/commands                                         │    ✗     │
│ opencode         │ OpenCode CLI     │ ~/.config/opencode/command                                 │    ✗     │
│ vs-code          │ VS Code          │ ~/Library/Application Support/Code/User/prompts            │    ✓     │
│ vs-code-insiders │ VS Code Insiders │ ~/Library/Application Support/Code - Insiders/User/prompts │    ✗     │
│ windsurf         │ Windsurf         │ ~/.codeium/windsurf/global_workflows                       │    ✗     │
└──────────────────┴──────────────────┴────────────────────────────────────────────────────────────┴──────────┘
```

### Verification

- ✅ `vs-code-insiders` appears in agent list
- ✅ Display name "VS Code Insiders" shown correctly
- ✅ Target path shows macOS-specific path (Library/Application Support/Code - Insiders/User/prompts)
- ✅ Alphabetically sorted after `vs-code`

## Test Results - Configuration Validity

Command: `uv run pytest tests/test_config.py -v`

```
=========================== test session starts ===========================
platform darwin -- Python 3.13.4, pytest-8.4.2, pluggy-1.6.0 -- /Users/mitchschaller/Liatrio/slash-command-manager/.venv/bin/python3
cachedir: .pytest_cache
rootdir: /Users/mitchschaller/Liatrio/slash-command-manager
configfile: pyproject.toml
plugins: anyio-4.11.0, httpx-0.35.0, cov-7.0.0
collected 13 items

tests/test_config.py::test_command_format_defines_markdown_and_toml PASSED [  7%]
tests/test_config.py::test_agent_config_is_frozen_dataclass PASSED [ 15%]
tests/test_config.py::test_agent_config_has_expected_field_types[key-str] PASSED [ 23%]
tests/test_config.py::test_agent_config_has_expected_field_types[display_name-str] PASSED [ 30%]
tests/test_config.py::test_agent_config_has_expected_field_types[command_dir-str] PASSED [ 38%]
tests/test_config.py::test_agent_config_has_expected_field_types[command_format-CommandFormat] PASSED [ 46%]
tests/test_config.py::test_agent_config_has_expected_field_types[command_file_extension-str] PASSED [ 53%]
tests/test_config.py::test_agent_config_has_expected_field_types[detection_dirs-tuple] PASSED [ 61%]
tests/test_config.py::test_agent_config_has_expected_field_types[platform_command_dirs-field_type6] PASSED [ 69%]
tests/test_config.py::test_supported_agents_is_tuple_sorted_by_key PASSED [ 76%]
tests/test_config.py::test_supported_agents_have_valid_structure PASSED [ 84%]
tests/test_config.py::test_supported_agents_have_valid_command_formats PASSED [ 92%]
tests/test_config.py::test_detection_dirs_cover_command_directory_roots PASSED [100%]

=========================== 13 passed in 0.02s ============================
```

### Verification

- ✅ All 13 config tests pass
- ✅ No regressions introduced
- ✅ VS Code Insiders configuration is valid and properly structured
- ✅ Detection directories test updated to handle VS Code Insiders as a special case

## Summary

Task 1.0 successfully completed:

1. ✅ VS Code Insiders agent configuration added to system
2. ✅ Configuration follows exact pattern of VS Code with updated paths
3. ✅ Cross-platform support for Linux, macOS, and Windows
4. ✅ Agent discoverable via `--list-agents` CLI command
5. ✅ All configuration tests pass with no regressions
