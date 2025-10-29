# Release Notes: Slash Command Manager v1.0.0

**Release Date:** October 29, 2025

## ?? Initial Release

This is the initial release of Slash Command Manager, extracted from the [SDD Workflow](https://github.com/liatrio-labs/spec-driven-workflow) repository to enable independent versioning and release cycles.

## What's New

### CLI Generator (`slash-man`)

A command-line tool for generating slash command definitions for various AI coding assistants:

- **Supported AI Tools:** Claude Code, Cursor, Windsurf, Codex CLI, Gemini CLI, VS Code
- **Interactive CLI:** Automatic detection of installed AI assistants
- **Multiple Formats:** Support for both Markdown and TOML command formats
- **Safety Features:** Dry-run mode, backup creation, and cleanup utilities

### MCP Server

A Model Context Protocol server for programmatic access to slash command generation:

- **FastMCP Implementation:** Built on the FastMCP framework
- **Multiple Transports:** Support for stdio and HTTP transports
- **SDD Integration:** Integrated with Spec-Driven Development workflow prompts

## Installation

### Via uvx (Recommended)

```bash
uvx --from git+https://github.com/liatrio-labs/slash-command-manager slash-man generate --yes
```

### Via pip

```bash
pip install slash-command-manager
```

### From Source

```bash
git clone https://github.com/liatrio-labs/slash-command-manager.git
cd slash-command-manager
pip install -e .
```

## Migration from SDD Workflow

If you were previously using `sdd-commands` from the SDD Workflow repository:

- **Old command:** `sdd-commands`
- **New command:** `slash-man`

The functionality remains the same; only the entry point name has changed.

For complete migration instructions, see the [SDD Workflow repository migration guide](https://github.com/liatrio-labs/spec-driven-workflow#migration-notice-generator-and-mcp-functionality-moved).

## What's Included

- **Package:** `slash-command-manager` (PyPI-ready)
- **CLI Entry Point:** `slash-man`
- **MCP Server Entry Point:** `slash-command-manager-mcp`
- **Packages:** `slash_commands/`, `mcp_server/`
- **Prompts:** Reference prompts for SDD workflow integration
- **Tests:** 79 passing tests with comprehensive coverage
- **Documentation:** README, CONTRIBUTING guide, CHANGELOG, and generator documentation

## Documentation

- [README](README.md) - Installation and usage guide
- [CHANGELOG](CHANGELOG.md) - Detailed changelog
- [Contributing Guide](CONTRIBUTING.md) - How to contribute
- [Generator Documentation](docs/slash-command-generator.md) - Detailed CLI documentation

## Related Projects

- [SDD Workflow](https://github.com/liatrio-labs/spec-driven-workflow) - Spec-Driven Development prompts and workflow documentation

## Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for the complete list of changes.

---

**Note:** This package was extracted from `spec-driven-workflow` to enable independent versioning and release cycles. All functionality has been preserved and enhanced for standalone use.
