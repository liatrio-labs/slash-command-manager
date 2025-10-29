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

```bash
uvx slash-command-manager generate --help
```

### Using pip

```bash
pip install slash-command-manager
```

### From Source

```bash
git clone https://github.com/liatrio/slash-command-manager.git
cd slash-command-manager
pip install -e .
```

## Quick Start

```bash
# Generate a new slash command
slash-man generate

# View help
slash-man --help
```

## Documentation

- [Generator Documentation](docs/slash-command-generator.md)
- [Contributing Guidelines](CONTRIBUTING.md)

## Related Projects

- [SDD Workflow](https://github.com/liatrio/sdd-workflow) - Spec-Driven Development prompts and workflow documentation

## License

MIT License - see [LICENSE](LICENSE) file for details
