# 03-tasks-unified-cli-consolidation.md

## Relevant Files

- `slash_commands/cli.py` - Main CLI application file that needs the new `mcp` subcommand added
- `server.py` - MCP server entry point that will be integrated into the CLI subcommand
- `pyproject.toml` - Package configuration that needs the `slash-command-manager` entry point removed
- `README.md` - Main documentation that needs updating to reflect unified command structure
- `tests/test_cli.py` - CLI tests that need updating to cover the new `mcp` subcommand
- `tests/test_cli_version.py` - Version-related tests that may need updates
- `mcp_server/__init__.py` - MCP server creation logic that will be used by the new subcommand
- `mcp_server/config.py` - Configuration handling that needs integration for custom TOML files
- `docs/operations.md` - Operations documentation that needs updating for new command structure
- `CHANGELOG.md` - Changelog that needs entry for this breaking change
- `CONTRIBUTING.md` - Contributing guide that may need command examples updated

## Tasks

- [x] 1.0 MCP Server Subcommand Integration
  - Demo Criteria: "Run `slash-man mcp` starts the MCP server with stdio transport, identical to current `slash-command-manager` behavior"
  - Proof Artifact(s): "CLI output showing server startup, help documentation displaying new subcommand structure"
  - [x] 1.1 Add MCP server import and dependencies to CLI module
  - [x] 1.2 Create `mcp` subcommand function in `slash_commands/cli.py` with basic stdio transport
  - [x] 1.3 Integrate existing server.py logic into the new subcommand
  - [x] 1.4 Add help text and command description for the new `mcp` subcommand
  - [x] 1.5 Test basic `slash-man mcp` functionality matches current `slash-command-manager` behavior

- [x] 2.0 Enhanced Configuration Options
  - Demo Criteria: "`slash-man mcp --config custom.toml --transport http --port 8080` successfully starts server with custom configuration"
  - Proof Artifact(s): "Server logs showing custom config loading, HTTP server responding on specified port"
  - [x] 2.1 Add `--config` flag to `mcp` subcommand for custom TOML configuration file paths
  - [x] 2.2 Add `--transport` flag with "stdio" (default) and "http" options to `mcp` subcommand
  - [x] 2.3 Add `--port` flag for HTTP server port configuration (default: 8000)
  - [x] 2.4 Integrate `mcp_server.config` module for handling custom TOML files
  - [x] 2.5 Add configuration validation with clear error messages for invalid configs
  - [x] 2.6 Test all configuration combinations (stdio, http with custom ports, custom TOML files)

- [x] 3.0 Entry Point Removal and Documentation Update
  - Demo Criteria: "`slash-command-manager` command no longer exists, all README examples use `slash-man` commands"
  - Proof Artifact(s): "Updated README.md, unified help output showing complete command structure"
  - [x] 3.1 Remove `slash-command-manager = "server:main"` entry point from `pyproject.toml`
  - [x] 3.2 Update README.md to use `slash-man mcp` instead of `slash-command-manager`
  - [x] 3.3 Update all documentation files to reflect unified command structure
  - [x] 3.6 Update `docs/operations.md` with new unified command structure and migration guide
  - [x] 3.4 Update CHANGELOG.md with breaking change notice and migration guide
  - [x] 3.5 Update CONTRIBUTING.md with new command examples and development setup
  - [x] 3.7 Verify unified help output shows complete command structure with `slash-man --help`

- [x] 4.0 Testing and Validation
  - Demo Criteria: "All tests pass with new command structure, coverage maintained at 95%+"
  - Proof Artifact(s): "Test suite results showing 95%+ coverage for new command structure"
  - [x] 4.1 Update existing CLI tests to work with new subcommand structure
  - [x] 4.2 Add comprehensive tests for `slash-man mcp` subcommand functionality
  - [x] 4.3 Add tests for all configuration options (config, transport, port)
  - [x] 4.4 Add tests for error handling and configuration validation
  - [x] 4.5 Update integration tests to use unified command structure
  - [x] 4.6 Verify test coverage meets 95%+ requirement for new functionality
  - [x] 4.7 Test that old `slash-command-manager` command is no longer available
