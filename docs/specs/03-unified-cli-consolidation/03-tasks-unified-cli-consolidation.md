# 03-tasks-unified-cli-consolidation.md

## Relevant Files

- `slash_commands/cli.py` - Main CLI entry point that needs modification to add mcp subcommand and --config option
- `server.py` - MCP server entry point that needs refactoring to be callable from CLI context
- `mcp_server/config.py` - Configuration system that needs TOML support added to replace environment variables
- `mcp_server/__init__.py` - MCP server creation that needs to accept configuration parameters
- `pyproject.toml` - Package configuration that needs entry point cleanup and TOML dependency addition
- `tests/test_cli.py` - CLI tests that need updating for new mcp subcommand functionality
- `tests/test_config.py` - Configuration tests that need TOML configuration testing
- `slash_commands/config.py` - New file for TOML configuration parsing and validation

### Notes

- Unit tests should be placed alongside the code files they are testing (e.g., `cli.py` and `test_cli.py` in the same directory structure).
- Use `uv run pytest tests/` to run tests. Running without a path executes all tests.
- Follow existing code patterns in the CLI for error handling and rich output formatting.
- Ensure backward compatibility for existing generate and cleanup commands.

## Tasks

- [ ] 1.0 Unified CLI Structure Foundation
  - [ ] 1.1 Add MCP subcommand structure to CLI with Typer command grouping
  - [ ] 1.2 Implement --config global option for TOML configuration file path
  - [ ] 1.3 Update help documentation to show unified command structure
  - [ ] 1.4 Add basic MCP subcommand with placeholder functionality
  - Demo Criteria: "Run `slash-man --help` and see all commands grouped logically with CLI Operations (generate, cleanup) and MCP Operations (mcp) sections"
  - Proof Artifact(s): "CLI: `slash-man --help` -> unified help output showing both existing and new mcp subcommand; Screenshot of help output"

- [ ] 2.0 MCP Server Subcommand Integration
  - [ ] 2.1 Refactor server.py main() function to be callable from CLI context
  - [ ] 2.2 Implement --transport and --port options in mcp subcommand
  - [ ] 2.3 Add proper error handling for transport configuration
  - [ ] 2.4 Integrate FastMCP server startup within CLI command structure
  - [ ] 2.5 Add health check endpoint verification for HTTP transport
  - Demo Criteria: "Run `slash-man mcp --transport http --port 8080` and successfully start MCP server with HTTP transport; verify server responds to health checks"
  - Proof Artifact(s): "CLI: `slash-man mcp --transport http --port 8080` -> server startup logs; URL: http://localhost:8080/health -> OK response; Test: MCP client connection test"

- [ ] 3.0 TOML Configuration System Implementation
  - [ ] 3.1 Create slash_commands/config.py for TOML parsing and validation
  - [ ] 3.2 Add toml dependency to pyproject.toml for TOML file support
  - [ ] 3.3 Implement configuration precedence (CLI options > TOML > defaults)
  - [ ] 3.4 Add TOML schema validation with clear error messages
  - [ ] 3.5 Update mcp_server/config.py to accept TOML configuration parameters
  - [ ] 3.6 Add configuration loading and error handling to CLI
  - Demo Criteria: "Create custom.toml with server settings and run `slash-man --config custom.toml mcp`; server starts with custom configuration values"
  - Proof Artifact(s): "File: custom.toml with custom port/host settings; CLI: `slash-man --config custom.toml mcp` -> logs showing custom config applied; Diff: config validation error messages"

- [ ] 4.0 Entry Point Cleanup and Packaging Updates
  - [ ] 4.1 Remove slash-command-manager entry point from pyproject.toml [project.scripts]
  - [ ] 4.2 Update build configuration to exclude standalone server entry point
  - [ ] 4.3 Update documentation and README to reflect unified CLI usage
  - [ ] 4.4 Add tests to verify only slash-man command is available after installation
  - [ ] 4.5 Update package metadata and descriptions for unified CLI
  - Demo Criteria: "Install package and verify only `slash-man` command is available; `slash-command-manager` command no longer exists"
  - Proof Artifact(s): "CLI: `which slash-man` -> shows command location; CLI: `slash-command-manager` -> command not found error; Diff: updated pyproject.toml entry points"
