# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-29

### Added

- Initial release of Slash Command Manager as a standalone package
- **CLI Generator** (`slash-man`): Interactive command-line tool for generating slash command definitions for various AI coding assistants
  - Support for Claude Code, Cursor, Windsurf, Codex CLI, Gemini CLI, and VS Code
  - Automatic detection of installed AI tools
  - Interactive agent selection
  - Support for both Markdown and TOML command formats
  - Backup and cleanup functionality
- **MCP Server**: Model Context Protocol server for programmatic access to slash command generation
  - FastMCP-based implementation
  - Support for stdio and HTTP transports
  - Integration with SDD workflow prompts
- **Core Packages**:
  - `slash_commands/`: CLI generator package with config, detection, generators, and writer modules
  - `mcp_server/`: MCP server package with prompt utilities and loading logic
  - `prompts/`: Reference prompt files for SDD workflow integration
- **Testing**: Comprehensive test suite with 79 passing tests
- **CI/CD**: GitHub Actions workflows for linting, testing, and release automation
- **Documentation**: README, CONTRIBUTING guide, and generator documentation

### Changed

- Extracted from `spec-driven-workflow` repository to enable independent versioning and release cycles
- CLI entry point changed from `sdd-commands` to `slash-man`
- Package name changed from `spec-driven-workflow` to `slash-command-manager`
- MCP server name changed from `spec-driven-workflow-mcp` to `slash-command-manager-mcp`

### Migration Notes

- **From `sdd-commands` to `slash-man`**: Users of the old CLI entry point should switch to `slash-man`

  ```bash
  # Old
  sdd-commands generate

  # New
  slash-man generate
  ```

- **Installation**: The package is now available separately from the SDD workflow prompts

  ```bash
  # Install via uvx
  uvx --from git+https://github.com/liatrio-labs/slash-command-manager slash-man generate --yes

  # Or via uv (once published)
  uv add slash-command-manager
  ```

- **SDD Workflow Repository**: The original repository now focuses on workflow prompts and documentation. Generator and MCP functionality are available via this package.

---

[1.0.0]: https://github.com/liatrio-labs/slash-command-manager/releases/tag/v1.0.0
