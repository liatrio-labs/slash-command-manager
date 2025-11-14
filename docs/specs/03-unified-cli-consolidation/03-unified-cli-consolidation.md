# 03-spec-unified-cli-consolidation.md

## Introduction/Overview

This specification consolidates the Slash Command Manager's dual entry points into a single unified CLI interface. Currently, users must navigate two separate commands (`slash-man` for CLI operations and `slash-command-manager` for MCP server), creating confusion and complexity. This feature will integrate the MCP server functionality as a subcommand under `slash-man mcp`, providing configurable options while removing the separate entry point entirely to simplify user experience and improve command discoverability.

## Goals

- Eliminate user confusion between multiple entry points by providing a single `slash-man` command
- Improve command discoverability through unified help documentation and logical command grouping
- Maintain full feature parity for existing MCP server functionality under the new subcommand structure
- Add enhanced configuration options (`--config` for custom TOML files, `--transport` for stdio/HTTP selection)
- Reduce installation and deployment complexity by consolidating to a single binary/executable
- Simplify documentation maintenance and reduce cognitive load for users

## User Stories

**As a developer**, I want to use a single command for all Slash Command Manager operations so that I don't have to remember and switch between different entry points.

**As a DevOps engineer**, I want to deploy and configure the MCP server through the main CLI so that I can manage all aspects of the tool through one interface.

**As a new user**, I want to discover all available functionality through unified help documentation so that I can quickly understand and use the tool's capabilities.

**As a documentation maintainer**, I want to update and maintain a single set of command examples so that I can reduce documentation complexity and prevent inconsistencies.

## Demoable Units of Work

### Unit 1: MCP Server Subcommand Integration

**Purpose:** Integrate existing MCP server functionality as a subcommand under `slash-man mcp`
**Demo Criteria:** Running `slash-man mcp` starts the MCP server with stdio transport, identical to current `slash-command-manager` behavior
**Proof Artifacts:** CLI output showing server startup, help documentation displaying new subcommand structure

### Unit 2: Enhanced Configuration Options

**Purpose:** Add configurable options for MCP server operation
**Demo Criteria:** `slash-man mcp --config custom.toml --transport http --port 8080` successfully starts server with custom configuration
**Proof Artifacts:** Server logs showing custom config loading, HTTP server responding on specified port

### Unit 3: Entry Point Removal and Documentation Update

**Purpose:** Remove old entry point and update all documentation to reflect unified structure
**Demo Criteria:** `slash-command-manager` command no longer exists, all README examples use `slash-man` commands
**Proof Artifacts:** Updated README.md, unified help output showing complete command structure

## Functional Requirements

1. **The system shall** provide a single entry point `slash-man` that encompasses all current functionality
2. **The system shall** implement `slash-man mcp` as a subcommand that starts the MCP server with stdio transport by default
3. **The system shall** support `--config` flag for specifying custom TOML configuration file paths
4. **The system shall** support `--transport` flag with options for "stdio" (default) and "http" transport modes
5. **The system shall** support `--port` flag for specifying HTTP server port when using http transport (default: 8000)
6. **The system shall** maintain full feature parity with existing MCP server functionality
7. **The system shall** remove the `slash-command-manager` entry point entirely from pyproject.toml
8. **The system shall** provide unified help documentation that displays all commands and subcommands logically
9. **The system shall** ensure all existing CLI commands (`generate`, `cleanup`) continue to work unchanged
10. **The system shall** validate configuration files and provide clear error messages for invalid configurations

## Non-Goals (Out of Scope)

1. **Backward compatibility** for the `slash-command-manager` command (this is intentionally a breaking change)
2. **Migration scripts** or automated tools for updating user configurations
3. **Additional transport protocols** beyond stdio and HTTP (WebSocket, etc.)
4. **New MCP server features** beyond current functionality
5. **Performance optimizations** or architectural changes to the MCP server itself
6. **Changes to existing CLI command behavior** (`generate`, `cleanup` commands remain unchanged)

## Design Considerations

No specific design requirements identified. The changes are primarily architectural and functional, focusing on command structure and user experience rather than visual design.

## Technical Considerations

- **Entry point configuration**: Modify `[project.scripts]` in pyproject.toml to remove `slash-command-manager` and keep only `slash-man`
- **CLI framework**: Use existing Typer framework to add `mcp` subcommand to the main CLI app
- **Configuration loading**: Leverage existing `mcp_server.config` module for handling custom TOML files
- **Transport abstraction**: Utilize existing FastMCP server's transport capabilities in the new subcommand
- **Error handling**: Maintain existing error handling patterns from both CLI and server components
- **Testing**: Ensure comprehensive test coverage for new command structure and configuration options
- **Documentation**: Update all references to use unified command structure

## Success Metrics

1. **Command discoverability**: Users can find all functionality through `slash-man --help` without prior knowledge
2. **Installation simplicity**: Single binary/executable installation reduces deployment complexity by 50%
3. **Documentation consistency**: 100% of examples in documentation use unified command structure
4. **User confusion reduction**: Zero support requests related to command selection or entry point confusion
5. **Feature parity**: All existing MCP server functionality works through new subcommand interface
6. **Test coverage**: 95%+ test coverage for new command structure and configuration options

## Proof Artifacts

- **CLI help output**: `slash-man --help` showing unified command structure with `mcp` subcommand
- **MCP subcommand help**: `slash-man mcp --help` displaying configuration options
- **Server startup logs**: Output showing successful server startup with various transport/config options
- **Updated README**: Documentation reflecting single entry point usage
- **Test results**: Comprehensive test suite passing for new command structure
- **Package configuration**: pyproject.toml showing single entry point configuration
