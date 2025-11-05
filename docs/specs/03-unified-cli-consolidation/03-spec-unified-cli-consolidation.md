# 03-unified-cli-consolidation.md

## Introduction/Overview

This specification consolidates the Slash Command Manager's dual entry points (`slash-man` for CLI operations and `slash-command-manager` for MCP server) into a single unified CLI interface. The consolidation eliminates user confusion by integrating the MCP server as a subcommand under `slash-man mcp`, providing configurable options for custom TOML configuration files and transport selection, while removing the separate `slash-command-manager` entry point entirely to simplify the user experience and improve command discoverability.

## Goals

- Eliminate user confusion between multiple entry points by providing a single, unified CLI interface
- Improve command discoverability through unified help documentation and logical command grouping
- Replace environment variable configuration with a more intuitive TOML-based configuration system
- Maintain full MCP server functionality while integrating it seamlessly into the CLI workflow
- Provide a clean, breaking change that simplifies the overall user experience

## User Stories

**As a developer using the Slash Command Manager**, I want to access all functionality through a single `slash-man` command so that I don't need to remember or discover multiple entry points.

**As a DevOps engineer configuring the MCP server**, I want to use a TOML configuration file instead of environment variables so that I can manage settings in a more familiar and version-controllable format.

**As a new user exploring the tool**, I want to see all available commands and their purposes in one unified help output so that I can quickly understand the full capabilities of the tool.

**As a system administrator deploying the MCP server**, I want to choose between stdio and HTTP transport via command-line options so that I can easily integrate with different deployment scenarios.

## Demoable Units of Work

### Unit 1: Unified CLI Structure

**Purpose:** Establish the foundation for the consolidated CLI interface with proper command grouping
**Demo Criteria:** Running `slash-man --help` shows all commands in a single, well-organized help output
**Proof Artifacts:** CLI help output showing both existing CLI commands and new `mcp` subcommand

### Unit 2: MCP Server Integration

**Purpose:** Integrate the MCP server functionality as a subcommand with configurable options
**Demo Criteria:** Running `slash-man mcp --transport http --port 8080` successfully starts the MCP server
**Proof Artifacts:** Server startup logs, HTTP endpoint accessibility, functional MCP operations

### Unit 3: TOML Configuration System

**Purpose:** Replace environment variables with TOML-based configuration management
**Demo Criteria:** Using `slash-man --config custom.toml mcp` loads configuration from specified TOML file
**Proof Artifacts:** Custom TOML configuration file, server behavior reflecting custom settings

### Unit 4: Entry Point Cleanup

**Purpose:** Remove the old `slash-command-manager` entry point and update packaging
**Demo Criteria:** Installing the package provides only `slash-man` entry point, with `slash-command-manager` no longer available
**Proof Artifacts:** Updated pyproject.toml, successful package installation and testing

## Functional Requirements

1. **The system shall** provide a single entry point named `slash-man` that exposes all functionality
2. **The system shall** integrate MCP server functionality as a subcommand under `slash-man mcp`
3. **The system shall** support `--config` option for specifying custom TOML configuration files
4. **The system shall** support `--transport` option for choosing between stdio and HTTP transport
5. **The system shall** maintain all existing CLI functionality (generate, cleanup) without breaking changes
6. **The system shall** remove the `slash-command-manager` entry point entirely from the package configuration
7. **The system shall** provide unified help documentation that groups commands logically
8. **The system shall** support both command-line options and TOML configuration with proper precedence handling
9. **The system shall** validate TOML configuration files and provide clear error messages for invalid configurations
10. **The system shall** maintain backward compatibility for existing MCP server functionality through the new interface

## Non-Goals (Out of Scope)

1. **Maintaining backward compatibility** for the `slash-command-manager` entry point (this is intentionally a breaking change)
2. **Supporting environment variable configuration** alongside TOML files (replacing entirely with TOML)
3. **Creating migration utilities** for existing users (as requested, no users currently using the tool)
4. **Modifying core MCP server functionality** beyond integration and configuration changes
5. **Adding new MCP server features** beyond what exists in the current implementation

## Design Considerations

The unified CLI should follow Typer's best practices for command grouping and help organization:

- **Main help structure**: Single help page with all commands grouped by functionality
- **Command groups**: CLI Operations (generate, cleanup) and MCP Operations (mcp)
- **Contextual help**: Subcommand-specific help accessible via `slash-man mcp --help`
- **Configuration help**: Clear documentation of TOML configuration options and precedence

The TOML configuration format should be intuitive and follow Python packaging conventions:

```toml
[server]
transport = "stdio"  # or "http"
port = 8000
host = "0.0.0.0"

[workspace]
root = "/workspace"
prompts_dir = "./prompts"

[logging]
level = "INFO"
format = "json"
```

## Technical Considerations

- **Entry point modification**: Update `pyproject.toml` to remove `slash-command-manager` and keep only `slash-man`
- **CLI structure**: Use Typer's subcommand functionality to add `mcp` as a command group
- **Configuration loading**: Implement TOML parsing with proper error handling and validation
- **Server integration**: Refactor `server.py` functionality to be callable from the CLI context
- **Option precedence**: Command-line options should override TOML configuration values
- **Error handling**: Provide clear, actionable error messages for configuration and transport issues
- **Testing**: Ensure all existing functionality remains accessible through the new interface

## Success Metrics

1. **Command discoverability**: Users can find all available commands through `slash-man --help`
2. **Single entry point**: Package installation provides only one executable command
3. **Configuration adoption**: TOML configuration files are properly parsed and applied
4. **Functionality preservation**: All existing CLI and MCP server features work through the unified interface
5. **Error handling**: Invalid configurations or missing files result in clear, actionable error messages

## Acceptance Criteria

- [ ] `slash-man --help` displays all commands in a unified help output
- [ ] `slash-man mcp --transport stdio` starts the MCP server with stdio transport
- [ ] `slash-man mcp --transport http --port 8080` starts the MCP server with HTTP transport on port 8080
- [ ] `slash-man --config custom.toml mcp` loads and applies configuration from the specified TOML file
- [ ] Command-line options override TOML configuration values correctly
- [ ] Invalid TOML configuration produces clear error messages with line numbers
- [ ] Package installation provides only the `slash-man` entry point
- [ ] All existing `slash-man generate` and `slash-man cleanup` functionality works unchanged
- [ ] MCP server functionality is identical to the previous `slash-command-manager` implementation
- [ ] Help documentation is comprehensive and follows Typer conventions for command grouping
