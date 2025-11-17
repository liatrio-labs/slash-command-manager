# Slash Command Manager

<div align="center">

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![Development Status](https://img.shields.io/badge/status-beta-yellow.svg)](https://github.com/liatrio-labs/slash-command-manager)

A powerful CLI tool and MCP server for generating and managing slash commands for AI coding assistants

[Quick Start](#quick-start) • [Documentation](#documentation) • [Contributing](CONTRIBUTING.md)

</div>

---

## 📖 Overview

Slash Command Manager (`slash-man`) is a standalone tool that generates and manages slash command definitions for AI coding assistants like Claude Code, Cursor, Windsurf, and others. It provides both a command-line interface and a Model Context Protocol (MCP) server for programmatic access.

### What Problem Does This Solve?

Managing slash commands across multiple AI coding assistants is tedious and error-prone. Slash Command Manager automates this process by:

- **Auto-detecting** configured AI assistants in your workspace
- **Generating** command files in the correct format for each agent
- **Managing** prompts from local directories or GitHub repositories
- **Providing** a unified CLI and MCP API for automation

### Key Features

- 🚀 **CLI Generator**: Interactive command-line tool for creating slash command configurations
- 🔌 **MCP Server**: Programmatic API for generating slash commands via Model Context Protocol
- 🔍 **Auto-Detection**: Automatically detects configured agents in your workspace
- 📦 **GitHub Integration**: Download prompts directly from public GitHub repositories
- 🛡️ **Safe Operations**: Dry-run mode, backup support, and confirmation prompts
- 📋 **List Command**: Discover and list all managed prompts across agents

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
  - [CLI Commands](#cli-commands)
  - [GitHub Repository Support](#github-repository-support)
  - [MCP Server](#mcp-server)
- [Supported AI Tools](#supported-ai-tools)
- [Version Management](#version-management)
- [Documentation](#documentation)
- [Development](#development)
- [SDD Workflow Integration](#sdd-workflow-integration)
- [Contributing](#contributing)
- [License](#license)

## 🚀 Quick Start

Get started in under 2 minutes:

```bash
# Install and run directly (no local installation needed)
uvx --from git+https://github.com/liatrio-labs/slash-command-manager slash-man generate --yes

# Or install from source
git clone https://github.com/liatrio-labs/slash-command-manager.git
cd slash-command-manager
uv pip install -e .

# Generate commands for all detected AI assistants
slash-man generate
```

That's it! Your slash commands are now available in your AI coding assistants.

## 💻 Installation

### Using uvx (Recommended)

Install and run directly from the repository without local installation:

```bash
# Generate slash commands for detected AI assistants
uvx --from git+https://github.com/liatrio-labs/slash-command-manager slash-man generate --yes

# View available commands
uvx --from git+https://github.com/liatrio-labs/slash-command-manager slash-man --help
```

Once published to PyPI, you'll be able to use:

```bash
uvx slash-man generate --yes
```

### From Source

```bash
git clone https://github.com/liatrio-labs/slash-command-manager.git
cd slash-command-manager
uv pip install -e .
```

**Requirements:** Python 3.12 or higher

## 📚 Usage

### CLI Commands

#### Generate Commands

```bash
# Generate for all detected AI assistants (interactive)
slash-man generate

# Generate for specific agents
slash-man generate --agent claude-code --agent cursor

# Preview changes without writing files
slash-man generate --dry-run

# Skip confirmation prompts (auto-backup mode)
slash-man generate --yes
```

#### List Managed Prompts

```bash
# List all managed prompts across all agents
slash-man list

# List prompts for specific agents
slash-man list --agent claude-code --agent cursor

# Use custom target path
slash-man list --target-path /custom/path
```

#### Cleanup Generated Files

```bash
# Preview what would be deleted
slash-man cleanup --dry-run

# Remove generated files and backups
slash-man cleanup --yes
```

#### View Help

```bash
# General help
slash-man --help

# Command-specific help
slash-man generate --help
slash-man list --help
slash-man cleanup --help

# List all supported agents
slash-man generate --list-agents
```

### GitHub Repository Support

Download prompts directly from public GitHub repositories:

```bash
# Download prompts from a GitHub repository directory
uv run slash-man generate \
  --github-repo liatrio-labs/spec-driven-workflow \
  --github-branch main \
  --github-path prompts \
  --agent claude-code \
  --target-path /tmp/test-output

# Download a single prompt file
uv run slash-man generate \
  --github-repo liatrio-labs/spec-driven-workflow \
  --github-branch main \
  --github-path prompts/generate-spec.md \
  --agent claude-code \
  --target-path /tmp/test-output
```

**Important Notes:**

- All three GitHub flags (`--github-repo`, `--github-branch`, `--github-path`) must be provided together
- GitHub flags are mutually exclusive with `--prompts-dir` (cannot use both)
- Repository must be in format `owner/repo` (e.g., `liatrio-labs/spec-driven-workflow`)
- Only public repositories are supported
- Only `.md` files are downloaded and processed
- The `--github-path` can point to either a directory or a single `.md` file

### MCP Server

Run the MCP server for programmatic access:

```bash
# STDIO transport (for MCP clients)
slash-man mcp

# HTTP transport
slash-man mcp --transport http --port 8000

# With custom configuration
slash-man mcp --config custom.toml --transport http --port 8080
```

## 🤖 Supported AI Tools

The generator supports the following AI coding assistants:

| AI Assistant | Command Directory | Format |
|--------------|-------------------|--------|
| **Claude Code** | `~/.claude/commands` | Markdown |
| **Cursor** | `~/.cursor/commands` | Markdown |
| **Windsurf** | `~/.codeium/windsurf/global_workflows` | Markdown |
| **Codex CLI** | `~/.codex/prompts` | Markdown |
| **Gemini CLI** | `~/.gemini/commands` | TOML |
| **VS Code** | `~/.config/Code/User/prompts` | Markdown |

## 🔢 Version Management

Slash Command Manager includes comprehensive version management with git commit SHA tracking:

### Version Format

The version follows the format `VERSION+COMMIT_SHA`:

- **Development**: `1.0.0+8b4e417` (includes current git commit)
- **Production**: `1.0.0+def456` (includes release commit at build time)
- **Fallback**: `1.0.0` (when git commit unavailable)

### Version Detection Priority

1. **Build-time injection** (for installed packages) - matches the release commit
2. **Runtime git detection** (for local development) - current git commit
3. **Fallback** - version only when git unavailable

### Viewing Version

```bash
# Show version with git commit SHA
slash-man --version
slash-man -v

# Example output:
# slash-man 1.0.0+8b4e417
```

This ensures traceability between installed versions and their corresponding git commits, useful for debugging and deployment tracking.

## 📖 Documentation

- [Generator Documentation](docs/slash-command-generator.md) - Detailed guide to the CLI generator
- [Operations Guide](docs/operations.md) - Operational procedures and best practices
- [MCP Prompt Support](docs/mcp-prompt-support.md) - MCP server usage and integration
- [Contributing Guidelines](CONTRIBUTING.md) - How to contribute to the project
- [Changelog](CHANGELOG.md) - Project history and changes

## 🛠️ Development

### Testing in Clean Environment (Docker)

For testing the installation in a completely clean environment without any local dependencies:

#### Option 1: One-line Testing

```bash
# Build and test in an ephemeral Docker container
docker run --rm -v $(pwd):/app -w /app python:3.12-slim bash -c "
    pip install uv && \
    uv sync && \
    uv run slash-man generate --list-agents && \
    echo '✅ Installation test passed - CLI is functional'
"
```

#### Option 2: Interactive Docker Container

```bash
# Build the Docker image
docker build -t slash-command-manager .

# Run interactively with shell access
docker run -it --rm slash-command-manager bash

# Or run directly with the CLI
docker run -it --rm slash-command-manager slash-man generate --list-agents
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=mcp_server --cov=slash_commands --cov-report=term-missing

# Run pre-commit hooks
uv run pre-commit run --all-files
```

### Building Package

```bash
# Build wheel and source distribution
uv run python -m build

# Install built package locally
pip install dist/*.whl
```

## 🔗 SDD Workflow Integration

Pairs great with [Liatrio's SDD Workflow](https://github.com/liatrio-labs/spec-driven-workflow)! This package was originally part of that repository and was extracted to enable independent versioning and release cycles.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details on:

- How to set up your development environment
- Our code style and standards
- How to submit pull requests
- Our issue reporting process

## 📄 License

Apache License 2.0 - see [LICENSE](LICENSE) file for details

---

<div align="center">

**Made with ❤️ by [Liatrio](https://www.liatrio.com)**

[Report Bug](https://github.com/liatrio-labs/slash-command-manager/issues) • [Request Feature](https://github.com/liatrio-labs/slash-command-manager/issues) • [View Documentation](docs/)

</div>
