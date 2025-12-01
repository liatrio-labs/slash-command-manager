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
uvx slash-man generate --yes
```

### From Source

```bash
git clone https://github.com/liatrio-labs/slash-command-manager.git
cd slash-command-manager
uv pip install -e .
```

## Version Management

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

### GitHub Repository Support

You can download prompts directly from public GitHub repositories using explicit flags:

```bash
# Download prompts from a GitHub repository directory
uv run slash-man generate \
  --github-repo liatrio-labs/spec-driven-workflow \
  --github-branch main \
  --github-path prompts \
  --agent claude-code \
  --target-path /tmp/test-output

# Download from a branch with slashes in the name
uv run slash-man generate \
  --github-repo liatrio-labs/spec-driven-workflow \
  --github-branch refactor/improve-workflow \
  --github-path prompts \
  --agent claude-code \
  --target-path /tmp/test-output

# Download a single prompt file from GitHub
uv run slash-man generate \
  --github-repo liatrio-labs/spec-driven-workflow \
  --github-branch refactor/improve-workflow \
  --github-path prompts/generate-spec.md \
  --agent claude-code \
  --target-path /tmp/test-output

# Download from a nested path
uv run slash-man generate \
  --github-repo owner/repo \
  --github-branch main \
  --github-path docs/prompts/commands \
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

**Error Handling:**

```bash
# Invalid repository format
uv run slash-man generate --github-repo invalid-format --target-path /tmp/test-output
# Error: Repository must be in format owner/repo, got: 'invalid-format'. Example: liatrio-labs/spec-driven-workflow

# Missing required flags
uv run slash-man generate --github-repo owner/repo --target-path /tmp/test-output
# Error: All GitHub flags must be provided together. Missing: --github-branch, --github-path

# Mutual exclusivity error
uv run slash-man generate \
  --prompts-dir ./prompts \
  --github-repo owner/repo \
  --github-branch main \
  --github-path prompts \
  --target-path /tmp/test-output
# Error: Cannot specify both --prompts-dir and GitHub repository flags simultaneously
```

### MCP Server Usage

Run the MCP server for programmatic access:

```bash
# STDIO transport (for MCP clients)
slash-man mcp

# HTTP transport
slash-man mcp --transport http --port 8000

# With custom configuration
slash-man mcp --config custom.toml --transport http --port 8080

# Or via uvx (once published)
uvx --from git+https://github.com/liatrio-labs/slash-command-manager slash-man mcp
```

### Supported AI Tools

The generator supports the following AI coding assistants:

- **Claude Code**: Commands installed to `~/.claude/commands`
- **Cursor**: Commands installed to `~/.cursor/commands`
- **Windsurf**: Commands installed to `~/.codeium/windsurf/global_workflows`
- **Codex CLI**: Commands installed to `~/.codex/prompts`
- **Gemini CLI**: Commands installed to `~/.gemini/commands`
- **VS Code**: Commands installed to platform-specific directories:
  - Linux: `~/.config/Code/User/prompts`
  - macOS: `~/Library/Application Support/Code/User/prompts`
  - Windows: `%APPDATA%\Code\User\prompts`
- **OpenCode CLI**: Commands installed to `~/.config/opencode/command`
- **Amazon Q**: Commands installed to `~/.aws/amazonq/prompts` (Windows & macOS/Linux)

## Documentation

- [Generator Documentation](docs/slash-command-generator.md)
- [Operations Guide](docs/operations.md)
- [MCP Prompt Support](docs/mcp-prompt-support.md)
- [Contributing Guidelines](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

## Related Projects

- [SDD Workflow](https://github.com/liatrio-labs/spec-driven-workflow) - Spec-Driven Development prompts and workflow documentation

## Development

### Testing in Clean Environment (Docker)

For testing the installation in a completely clean environment without any local dependencies, use these `docker` commands:

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

This command:

- Uses a fresh Python 3.12 slim container
- Installs uv package manager
- Syncs dependencies from scratch
- Tests the CLI functionality
- Automatically cleans up the container when done

For a more comprehensive test including package building:

```bash
# Full test: build package and test CLI in clean environment
docker run --rm -v $(pwd):/app -w /app python:3.12-slim bash -c "
    pip install uv build && \
    uv sync && \
    python -m build && \
    pip install dist/*.whl && \
    slash-man generate --list-agents && \
    slash-man generate --agent claude-code && \
    ls -lh ~/.claude/commands/ | grep .md && \
    echo '✅ Full installation and functionality test passed'
"
```

#### Option 2: Interactive Docker Container

Build the Docker image and run it interactively:

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

Apache License 2.0 - see [LICENSE](LICENSE) file for details
