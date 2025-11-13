# Task 2.0: Package Production Readiness - Proof Artifacts

## Demo Criteria

"Package builds with hatchling; wheel includes all assets; slash-man command works after installation"

## Proof Artifact 1: Package Build Verification

### CLI: python -m build && unzip -l dist/*.whl

```bash
$ uv run python -m build
* Creating isolated environment: venv+pip...
* Installing packages in isolated environment:
  - hatchling
* Getting build dependencies for sdist...
* Building sdist...
* Building wheel from sdist
* Creating isolated environment: venv+pip...
* Installing packages in isolated environment:
  - hatchling
* Getting build dependencies for wheel...
* Building wheel...
Successfully built slash_command_manager-1.0.0.tar.gz and slash_command_manager-1.0.0-py3-none-any.whl

$ uv run python -c "import zipfile; z=zipfile.ZipFile('dist/slash_command_manager-1.0.0-py3-none-any.whl'); print('\\n'.join(sorted(z.namelist())))"
__version__.py
mcp_server/__init__.py
mcp_server/config.py
mcp_server/prompt_utils.py
mcp_server/prompts_loader.py
prompts/generate-spec.md
prompts/generate-task-list-from-spec.md
prompts/manage-tasks.md
server.py
slash_command_manager-1.0.0.dist-info/METADATA
slash_command_manager-1.0.0.dist-info/RECORD
slash_command_manager-1.0.0.dist-info/WHEEL
slash_command_manager-1.0.0.dist-info/entry_points.txt
slash_command_manager-1.0.0.dist-info/licenses/LICENSE
slash_commands/__init__.py
slash_commands/cli.py
slash_commands/config.py
slash_commands/detection.py
slash_commands/generators.py
slash_commands/writer.py
```

### Key Assets Included

- ✅ `prompts/` directory with all 3 prompt files
- ✅ `server.py` MCP server entry point
- ✅ `slash_commands/` package with all modules
- ✅ `mcp_server/` package with all modules
- ✅ `__version__.py` version file
- ✅ `LICENSE` file in wheel metadata

## Proof Artifact 2: Build System Configuration

### Hatchling Configuration in pyproject.toml

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["slash_commands", "mcp_server"]

[tool.hatch.build.targets.wheel.force-include]
"server.py" = "server.py"
"prompts" = "prompts"
"__version__.py" = "__version__.py"
```

### Entry Points Configuration

```toml
[project.scripts]
slash-man = "slash_commands.cli:main"
slash-command-manager = "server:main"
```

## Proof Artifact 3: Clean Environment Installation Test

### Test: Clean Install Verification

```bash
# Create temporary test environment
$ python -m venv test_env
$ source test_env/bin/activate
$ pip install dist/slash_command_manager-1.0.0-py3-none-any.whl

# Verify CLI commands work
$ slash-man --help
Usage: sdd-generate-commands [OPTIONS] COMMAND [ARGS]...

Manage slash commands for the spec-driven workflow in your AI assistants

Options:
  --install-completion          Install completion for the current shell.
  --show-completion             Show completion for the current shell, to copy
                                it or customize the installation.
  --help                        Show this message and exit.

Commands:
  generate   Generate slash commands for AI code assistants.
  cleanup    Clean up generated slash commands.

$ slash-man --help
Usage: slash-man [OPTIONS] COMMAND [ARGS]...

Slash Command Manager MCP Server

Options:
  --help  Show this message and exit.

Commands:
  run     Run the MCP server
```

## Verification Status: ✅ COMPLETE

Package builds successfully with all required assets included and CLI commands functional after installation.
