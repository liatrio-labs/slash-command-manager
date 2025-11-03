# Slash Command Generator

The Slash Command Generator automates the creation of slash command files for AI code assistants like Claude Code, Cursor, Windsurf, and others. It generates command files from markdown prompts, supporting multiple agents and formats.

## Overview

The generator reads markdown prompts from the `prompts/` directory and produces command files in the appropriate format for each configured AI assistant. It supports:

- **Multiple agents**: 7 supported AI assistants with different command formats
- **Auto-detection**: Automatically detects configured agents in your workspace
- **Dry run mode**: Preview changes without writing files
- **Safe overwrite handling**: Prompts before overwriting existing files with backup support
- **Cleanup command**: Remove generated files and backups

## Installation

The CLI is installed as part of the project dependencies:

```bash
uv sync
```

## Python Version Requirements

This project requires **Python 3.12 or higher**. The `tomllib` module is used for parsing TOML files and is part of the Python standard library starting with Python 3.11, but Python 3.12+ is required to ensure compatibility with all project dependencies.

### Why Python 3.12+?

1. **Standard Library TOML Support**: The `tomllib` module is included in Python's standard library since Python 3.11, eliminating the need for external TOML parsing dependencies like `tomli`.
2. **Dependency Compatibility**: Project dependencies such as `fastmcp`, `ruff`, and others require Python 3.12+.
3. **Modern Language Features**: Python 3.12 introduces performance improvements and language features that benefit the project.

### Verifying Your Python Version

To check your current Python version:

```bash
python --version
```

Expected output: `Python 3.12.x` or higher

### No Additional Dependencies Required

Because `tomllib` is part of the standard library, you don't need to install additional packages for TOML parsing:

```python
import tomllib # Built-in, no pip install needed
```

This means:

- ✅ No external TOML parsing dependencies
- ✅ One less package to manage
- ✅ Guaranteed compatibility with your Python installation
- ✅ Faster import times

**Note**: While `tomllib` handles parsing TOML files (reading), the project uses `tomli-w` for writing TOML files (generating command files for Gemini CLI). Both are lightweight dependencies and `tomli-w` is required for generating TOML command files.

## Running Commands

After installation, use `uv run` to execute the command:

```bash
uv run sdd-generate-commands [OPTIONS]
```

### Basic Usage

Generate commands for all auto-detected agents in your home directory:

```bash
uv run sdd-generate-commands
```

**Note**: By default, the generator:

- Detects agents in your home directory (`~`)
- Generates command files in your home directory
- Without `--yes`, prompts you to select which detected agents to generate commands for (all detected agents are pre-selected)
- Use `--detection-path` to search in a different directory
- Use `--target-path` to generate files in a different location

### Agent Selection

Generate commands for specific agents:

```bash
uv run sdd-generate-commands --agents claude-code --agents cursor
```

### Dry Run

Preview changes without writing files:

```bash
uv run sdd-generate-commands --dry-run
```

### List Supported Agents

View all available agents:

```bash
uv run sdd-generate-commands --list-agents
```

### Custom Prompts Directory

Specify a custom prompts directory:

```bash
uv run sdd-generate-commands --prompts-dir ./my-prompts
```

### Detection Path

Specify a custom directory to search for agents:

```bash
uv run sdd-generate-commands --detection-path /path/to/project
```

**Note**: By default, the generator searches for agents in your home directory. Use `--detection-path` to search in a different location (e.g., current directory for project-specific detection).

### Overwrite Handling

When existing command files are detected, the generator will prompt you for action:

- **Cancel**: Abort the operation (no files modified)
- **Overwrite**: Replace the existing file
- **Backup**: Create a timestamped backup before overwriting
- **Overwrite All**: Apply the overwrite decision to all remaining files

To skip prompts and auto-overwrite:

```bash
uv run sdd-generate-commands --yes
```

#### Backup File Management

Backup files are created with the format `filename.ext.YYYYMMDD-HHMMSS.bak` (e.g., `manage-tasks.md.20250122-143059.bak`).

**Important**: Backup files are **not automatically cleaned up**. Periodically review and remove old backup files to keep your workspace clean:

```bash
# Find all backup files
find . -name "*.bak" -type f

# Remove backup files older than 30 days
find . -name "*.bak" -type f -mtime +30 -delete
```

### Cleanup Command

Remove generated command files and backups:

```bash
# Show what would be deleted (dry run)
uv run sdd-generate-commands cleanup --dry-run

# Clean up all generated files
uv run sdd-generate-commands cleanup --yes

# Clean up specific agents only
uv run sdd-generate-commands cleanup --agents claude-code --agents cursor --yes

# Clean up without including backup files
uv run sdd-generate-commands cleanup --no-backups --yes

# Clean up with custom target path
uv run sdd-generate-commands cleanup --target-path /path/to/project --yes
```

**Options**:

- `--agents`: Specify which agents to clean (can be specified multiple times). If not specified, cleans all agents.
- `--dry-run`: Show what would be deleted without actually deleting files
- `--yes`, `-y`: Skip confirmation prompts
- `--target-path`, `-t`: Target directory to search for generated files (defaults to home directory)
- `--include-backups/--no-backups`: Include backup files in cleanup (default: true)

**Note**: Without `--yes`, the cleanup command will prompt for confirmation before deleting files.

## Supported Agents

The following agents are supported:

| Agent | Display Name | Format | Extension | Target Directory | Reference |
|-------|--------------|--------|-----------|------------------|-----------|
| `claude-code` | Claude Code | Markdown | `.md` | `.claude/commands` | [Home](https://docs.claude.com/) · [Docs](https://docs.claude.com/en/docs/claude-code/overview) |
| `codex-cli` | Codex CLI | Markdown | `.md` | `.codex/prompts` | [Home](https://developers.openai.com/codex) · [Docs](https://developers.openai.com/codex/cli/) |
| `cursor` | Cursor | Markdown | `.md` | `.cursor/commands` | [Home](https://cursor.com/) · [Docs](https://cursor.com/docs) |
| `gemini-cli` | Gemini CLI | TOML | `.toml` | `.gemini/commands` | [Home](https://github.com/google-gemini/gemini-cli) · [Docs](https://geminicli.com/docs/) |
| `opencode` | OpenCode CLI | Markdown | `.md` | `.config/opencode/command` | [Home](https://opencode.ai) · [Docs](https://opencode.ai/docs/commands) |
| `vs-code` | VS Code | Markdown | `.prompt.md` | `.config/Code/User/prompts` | [Home](https://code.visualstudio.com/) · [Docs](https://code.visualstudio.com/docs) |
| `windsurf` | Windsurf | Markdown | `.md` | `.codeium/windsurf/global_workflows` | [Home](https://windsurf.com/editor) · [Docs](https://docs.windsurf.com/) |

## Command File Formats

### Markdown Format

Markdown-based agents (Claude Code, Cursor, etc.) use frontmatter with a body:

```markdown
---
name: command-name
description: Command description
tags:
- tag1
- tag2
arguments:
- name: arg1
  description: Argument description
  required: true
enabled: true
---

# Command Name

Command body content.

$ARGUMENTS
```

### TOML Format

TOML-based agents (Gemini CLI) use TOML syntax:

```toml
[command]
name = "command-name"
description = "Command description"
tags = ["tag1", "tag2"]
enabled = true

[command.arguments]
required = { "arg1" = "Argument description" }
optional = {}

[command.body]
text = """
# Command Name

Command body content.

{{args}}
"""

[command.meta]
category = "example"
agent = "gemini-cli"
agent_display_name = "Gemini CLI"
command_dir = ".gemini/commands"
command_format = "toml"
command_file_extension = ".toml"
```

## Prompt Structure

Prompts are markdown files with YAML frontmatter. Key fields:

- **name**: Unique command identifier
- **description**: Human-readable description
- **tags**: List of tags for categorization
- **arguments**: List of command arguments
- **enabled**: Whether the command is active (default: true)
- **agent_overrides**: Agent-specific customization
- **meta**: Metadata object (optional)
- **command_prefix**: Optional prefix to prepend to the command name (e.g., "sdd-" to create "sdd-manage-tasks")

### Example Prompt

```markdown
---
name: generate-spec
description: Generate a detailed specification from a user idea
tags:
- spec
- planning
- documentation
arguments:
- name: idea
  description: The user's idea or requirement
  required: true
enabled: true
command_prefix: sdd-
---

# Generate Specification

Generate a comprehensive specification for the following idea:

{{idea}}

Please create a detailed specification that includes:
1. Overview and goals
2. User stories
3. Technical requirements
4. Success criteria
5. Implementation considerations

$ARGUMENTS
```

## Advanced Usage

### Custom Agent Configuration

You can extend the generator with custom agents by modifying the configuration in `slash_commands/config.py`. Each agent requires:

- **Display name**: Human-readable name
- **Format**: File format (markdown or toml)
- **File extension**: Output file extension
- **Target directory**: Where to place generated files
- **Template function**: Function to generate the command file content

### Integration with CI/CD

The generator can be integrated into CI/CD pipelines to automatically update slash commands when prompts change:

```yaml
- name: Update slash commands
  run: |
    uv sync
    uv run sdd-generate-commands --yes --target-path $HOME
    git add .
    git diff --staged --quiet || git commit -m "ci: update slash commands"
```

## Troubleshooting

### Common Issues

1. **Permission denied**: Ensure the target directory is writable
2. **Agent not detected**: Check that the agent's configuration directory exists
3. **Invalid prompt format**: Verify YAML frontmatter is properly formatted
4. **Python version**: Ensure Python 3.12+ is being used

### Debug Mode

Enable debug logging for troubleshooting:

```bash
uv run sdd-generate-commands --dry-run --verbose
```

### Getting Help

```bash
uv run sdd-generate-commands --help
```

## Contributing

To add support for a new AI assistant:

1. Add the agent configuration to `slash_commands/config.py`
2. Implement the template function in `slash_commands/generators.py`
3. Add tests for the new agent
4. Update this documentation

Please ensure the new agent follows the existing patterns and includes comprehensive test coverage.
