# Slash Command Manager

A standalone CLI tool and MCP server for generating and managing slash commands as part of the Spec-Driven Development (SDD) workflow.

## Overview

Slash Command Manager provides both a command-line interface (`slash-man`) for generating slash command definitions and an MCP server for programmatic access. This repository was extracted from the SDD Workflow repository to enable independent versioning and release cycles.

## Features

- **CLI Generator**: Interactive command-line tool for creating slash command configurations
- **MCP Server**: Programmatic API for generating slash commands via Model Context Protocol
- **Code Detection**: Automatic detection of code patterns and generation of appropriate command structures
- **Flexible Configuration**: Support for various configuration formats and customization options

## Installation

### Using uvx (Recommended)

Install and run directly from the repository:

```bash
# Generate slash commands for detected AI assistants
uvx --from git+https://github.com/liatrio-labs/slash-command-manager slash-man generate --yes

# View available commands
uvx --from git+https://github.com/liatrio-labs/slash-command-manager slash-man --help
```

Once published to PyPI, you'll be able to use:

```bash
uvx slash-command-manager generate --yes
```

### From Source

```bash
git clone https://github.com/liatrio-labs/slash-command-manager.git
cd slash-command-manager
uv pip install -e .
```

## Quick Start

### CLI Usage

```bash
# Generate slash commands for all detected AI assistants
slash-man generate

# Generate for specific agents (interactive selection)
slash-man generate --agents claude-code,cursor

# Generate with dry-run to preview changes
slash-man generate --dry-run

# View help
slash-man --help

# Clean up generated files
slash-man cleanup
```

### MCP Server Usage

Run the MCP server for programmatic access:

```bash
# STDIO transport (for MCP clients)
python server.py

# HTTP transport
python server.py --transport http --port 8000

# Or via uvx (once published)
uvx --from git+https://github.com/liatrio-labs/slash-command-manager slash-command-manager-mcp
```

### Supported AI Tools

The generator supports the following AI coding assistants:

- **Claude Code**: Commands installed to `~/.claude/commands`
- **Cursor**: Commands installed to `~/.cursor/commands`
- **Windsurf**: Commands installed to `~/.codeium/windsurf/global_workflows`
- **Codex CLI**: Commands installed to `~/.codex/prompts`
- **Gemini CLI**: Commands installed to `~/.gemini/commands`
- **VS Code**: Commands installed to `~/.config/Code/User/prompts`

## Documentation

- [Generator Documentation](docs/slash-command-generator.md)
- [Contributing Guidelines](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

## Related Projects

- [SDD Workflow](https://github.com/liatrio-labs/spec-driven-workflow) - Spec-Driven Development prompts and workflow documentation

## SDD Workflow Integration

This package was extracted from the [SDD Workflow](https://github.com/liatrio-labs/spec-driven-workflow) repository to enable independent versioning and release cycles.

### About SDD Workflow

The [Spec-Driven Development (SDD) Workflow](https://github.com/liatrio-labs/spec-driven-workflow) provides a structured approach to AI-assisted software development using three core prompts:

1. **`generate-spec`**: Creates detailed specifications from feature ideas
2. **`generate-task-list-from-spec`**: Transforms specs into actionable task lists
3. **`manage-tasks`**: Coordinates execution and tracks progress

Slash Command Manager generates the slash commands that enable these prompts in your AI coding assistant. The workflow prompts themselves are maintained in the SDD Workflow repository.

### Usage with SDD Workflow

1. **Install Slash Command Manager** (this package) to generate slash commands
2. **Reference SDD Workflow prompts** from the [SDD Workflow repository](https://github.com/liatrio-labs/spec-driven-workflow) when using the generated commands

For complete documentation on the SDD workflow, see the [SDD Workflow repository](https://github.com/liatrio-labs/spec-driven-workflow).

## License

MIT License - see [LICENSE](LICENSE) file for details
