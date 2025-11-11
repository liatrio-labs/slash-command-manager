# Task List: Slash Command Manager Extraction & SDD Workflow Refactoring

Generated from: `0001-spec-slash-command-manager-extraction.md`

## Relevant Files

### Slash Command Manager Repository (Target)

- `pyproject.toml` - Package configuration with dependencies, entry points (`slash-man`), and build metadata
- `__version__.py` - Version definition for semantic versioning
- `README.md` - Project documentation tailored for generator + MCP functionality
- `CONTRIBUTING.md` - Contribution guidelines
- `LICENSE` - License file (copied from source repository)
- `.pre-commit-config.yaml` - Pre-commit hooks configuration
- `.github/workflows/ci.yml` - CI workflow for linting and testing
- `.github/workflows/release.yml` - Release automation workflow
- `slash_commands/__init__.py` - Package initialization
- `slash_commands/cli.py` - CLI implementation using Typer
- `slash_commands/config.py` - Configuration management
- `slash_commands/writer.py` - File writing utilities
- `slash_commands/detection.py` - Code detection logic
- `mcp_server/__init__.py` - MCP server package initialization
- `mcp_server/config.py` - MCP server configuration
- `mcp_server/prompt_utils.py` - Prompt utility functions
- `mcp_server/prompts_loader.py` - Prompts loading logic
- `server.py` - MCP server entry point (main function)
- `prompts/` - Directory containing reference prompts for MCP server
- `tests/conftest.py` - Pytest configuration and shared fixtures
- `tests/test_cli.py` - CLI tests
- `tests/test_generators.py` - Generator functionality tests
- `tests/test_detection.py` - Detection logic tests
- `tests/test_config.py` - Configuration tests
- `tests/test_mcp_server.py` - MCP server tests (if exists in source)
- `docs/slash-command-generator.md` - Generator documentation
- `CHANGELOG.md` - Changelog for release notes

### SDD Workflow Repository (Source - to be modified)

- `pyproject.toml` - Remove generator/MCP dependencies and entry points
- `README.md` - Update with links to Slash Command Manager and migration guidance
- `.github/workflows/ci.yml` - Simplify or remove if not needed
- `.github/workflows/release.yml` - Remove or simplify

### Notes

- Unit tests should be placed alongside the code files they are testing (e.g., `tests/test_cli.py` tests `slash_commands/cli.py`)
- Use `pytest tests/` to run all tests. Running without a path executes all tests found by the pytest configuration
- Source repository code locations will need to be identified during implementation (assumed to exist based on spec)

### Proof Artifacts

> **Artifact Storage:** All proof artifacts and demo files generated during task implementation should be stored in `./docs/artifacts/<spec-number>/task-<task-number>/` (e.g., `./docs/artifacts/0001/task-1.0/`). This organization ensures artifacts are properly categorized by specification number and task number for easy review and documentation.
>
> **Naming Convention:** Artifact files should be named descriptively (e.g., `directory-structure.txt`, `wheel-build.log`, `pyproject.toml.txt`).
>
> Each task directory should include a `README.md` explaining what artifacts are present and their purpose.

## Tasks

- [x] 1.0 Set up Slash Command Manager Repository Structure and Configuration
  - Demo Criteria: "Repository initialized with all necessary directory structure, packaging configuration (`pyproject.toml`), versioning (`__version__.py`), license files, and CI/CD workflow scaffolding; package build succeeds: `python -m build --wheel`"
  - Proof Artifact(s): "Directory tree output showing structure; `pyproject.toml` content; successful wheel build log; `__version__.py` showing initial version"
  - [x] 1.1 Create directory structure: `slash_commands/`, `mcp_server/`, `prompts/`, `tests/`, `docs/`, `.github/workflows/`
  - [x] 1.2 Create `pyproject.toml` with package metadata, build system configuration, dependencies (fastmcp, questionary, tomli-w, rich, typer, pyyaml, pytest, ruff, pre-commit), and entry point definition for `slash-man`
  - [x] 1.3 Create `__version__.py` with initial semantic version (e.g., `__version__ = "1.0.0"`)
  - [x] 1.4 Copy `LICENSE` file from source SDD workflow repository
  - [x] 1.5 Create `.pre-commit-config.yaml` with hooks for ruff, pytest, and other code quality tools (copy and adapt from source repo)
  - [x] 1.6 Create `.github/workflows/ci.yml` workflow for linting (`ruff check`), testing (`pytest`), and pre-commit validation
  - [x] 1.7 Create `.github/workflows/release.yml` workflow for semantic versioning and package publishing to PyPI
  - [x] 1.8 Create basic `README.md` structure with project description, installation instructions, and links to documentation
  - [x] 1.9 Create `CONTRIBUTING.md` with contribution guidelines
  - [x] 1.10 Verify package structure: run `python -m build --wheel` and confirm successful wheel build in `dist/` directory

- [x] 2.0 Extract and Port Generator Code (`slash_commands/` package)
  - Demo Criteria: "All `slash_commands/` modules (CLI, config, writer, detection) copied and adapted with updated imports; CLI entry point `slash-man` configured in `pyproject.toml`; `slash-man --help` displays usage without errors"
  - Proof Artifact(s): "CLI invocation output: `$ slash-man --help`; directory structure showing all modules; `pyproject.toml` entry points section"
  - [x] 2.1 Copy `slash_commands/` directory from source SDD workflow repository to Slash Command Manager repository
  - [x] 2.2 Review and update `slash_commands/__init__.py` to ensure proper package initialization and exports
  - [x] 2.3 Review `slash_commands/cli.py` and update any import paths that reference old repository structure; ensure CLI uses Typer framework correctly
  - [x] 2.4 Review and update `slash_commands/config.py` for any path or package name references
  - [x] 2.5 Review and update `slash_commands/writer.py` for any import path changes
  - [x] 2.6 Review and update `slash_commands/detection.py` for any import path changes
  - [x] 2.7 Verify `pyproject.toml` has correct entry point configuration: `[project.scripts]` section with `slash-man = "slash_commands.cli:main"` (or appropriate entry point)
  - [x] 2.8 Install package in editable mode: `pip install -e .` (or `uv pip install -e .`)
  - [x] 2.9 Test CLI entry point: run `slash-man --help` and verify it displays usage information without import or runtime errors

- [x] 3.0 Extract and Port MCP Server Code (`mcp_server/` package and `server.py`)
  - Demo Criteria: "`mcp_server/` package ported with all MCP functionality; `server.py` entry point ported; `prompts/` directory copied; MCP server starts without errors"
  - Proof Artifact(s): "Directory structure showing `mcp_server/` and `server.py`; successful server startup log or test run"
  - [x] 3.1 Copy `mcp_server/` directory from source SDD workflow repository to Slash Command Manager repository
  - [x] 3.2 Review and update `mcp_server/__init__.py` to ensure proper package initialization
  - [x] 3.3 Review `mcp_server/config.py` and update any import paths or configuration references
  - [x] 3.4 Review `mcp_server/prompt_utils.py` and update any import paths
  - [x] 3.5 Review `mcp_server/prompts_loader.py` and update paths to `prompts/` directory (ensure it references the correct location)
  - [x] 3.6 Copy `prompts/` directory from source repository to Slash Command Manager repository
  - [x] 3.7 Copy `server.py` entry point file from source repository to Slash Command Manager repository root
  - [x] 3.8 Review and update `server.py` to ensure it correctly imports from `mcp_server` package and references `prompts/` directory correctly
  - [x] 3.9 Verify MCP server dependencies are listed in `pyproject.toml` (fastmcp, pyyaml)
  - [x] 3.10 Test MCP server startup: run `python server.py` (or appropriate command) and verify it starts without import or configuration errors

- [x] 4.0 Port and Adapt Test Suite
  - Demo Criteria: "All generator and MCP tests copied and adapted with updated import paths; all tests pass: `pytest tests/`; pre-commit hooks pass: `pre-commit run --all-files`"
  - Proof Artifact(s): "Test run output showing all tests passing; pre-commit run summary; test coverage report"
  - [x] 4.1 Copy `tests/conftest.py` from source repository and update any fixture paths or import references
  - [x] 4.2 Copy generator test files (`tests/test_cli.py`, `tests/test_generators.py`, `tests/test_detection.py`, `tests/test_config.py`) from source repository
  - [x] 4.3 Copy MCP server test files (e.g., `tests/test_mcp_server.py` or equivalent) if they exist in source repository
  - [x] 4.4 Update all test files to use correct import paths for `slash_commands` and `mcp_server` packages (change from old package structure if needed)
  - [x] 4.5 Update any test fixtures or test data paths that reference source repository structure
  - [x] 4.6 Review `pyproject.toml` to ensure pytest configuration includes correct test paths and coverage settings
  - [x] 4.7 Run test suite: `pytest tests/` and fix any failing tests due to import or path issues
  - [x] 4.8 Verify all tests pass: confirm pytest summary shows all tests passing with appropriate coverage
  - [x] 4.9 Install pre-commit hooks: `pre-commit install`
  - [x] 4.10 Run pre-commit on all files: `pre-commit run --all-files` and fix any linting or formatting issues

- [x] 5.0 Refactor SDD Workflow Repository (Remove Extracted Components)
  - Demo Criteria: "Generator and MCP code removed from SDD workflow repo (`slash_commands/`, `mcp_server/`, `server.py`, related tests); dependencies cleaned from `pyproject.toml`; README updated with Slash Command Manager link; pre-commit passes"
  - Proof Artifact(s): "Git diff showing removed files and dependencies; updated README snippet; pre-commit pass confirmation"
  - [x] 5.1 Remove `slash_commands/` directory from SDD workflow repository
  - [x] 5.2 Remove `mcp_server/` directory from SDD workflow repository
  - [x] 5.3 Remove `server.py` entry point file from SDD workflow repository
  - [x] 5.4 Remove generator-related test files (`tests/test_cli.py`, `tests/test_generators.py`, `tests/test_detection.py`, `tests/test_config.py`) from SDD workflow repository
  - [x] 5.5 Remove MCP server test files from SDD workflow repository (if they exist)
  - [x] 5.6 Remove VHS demo files and scripts (`vhs_demos/` directory and related scripts) from SDD workflow repository
  - [x] 5.7 Update `pyproject.toml` in SDD workflow repository: remove generator/MCP dependencies (fastmcp, questionary, tomli-w, rich, typer, pyyaml) and remove CLI entry points section
  - [x] 5.8 Update `pyproject.toml` in SDD workflow repository: retain only shared tooling dependencies (pytest, ruff, pre-commit) if needed, or simplify to minimal configuration for docs-only repo
  - [x] 5.9 Update `README.md` in SDD workflow repository: add clear section explaining that generator and MCP functionality moved to Slash Command Manager, include installation link and migration instructions
  - [x] 5.10 Update `.github/workflows/ci.yml` in SDD workflow repository: simplify or remove workflows that no longer apply (remove test runs, packaging steps; keep minimal linting for docs if desired)
  - [x] 5.11 Update or remove `.github/workflows/release.yml` in SDD workflow repository (SDD workflow no longer publishes as package)
  - [x] 5.12 Verify `prompts/` directory is retained in SDD workflow repository (for reference)
  - [x] 5.13 Run pre-commit in SDD workflow repository: `pre-commit run --all-files` and verify it passes
  - [x] 5.14 Create git commit in SDD workflow repository with clear message documenting the extraction

- [x] 6.0 Create Release Artifacts and Migration Documentation
  - Demo Criteria: "CHANGELOG entry created in Slash Command Manager; migration guide added to SDD workflow README; Slash Command Manager tagged with initial semantic version (e.g., `v1.0.0`); package installable via `uvx --from ./dist slash-man generate --help`"
  - Proof Artifact(s): "CHANGELOG entry; migration guide document; git tag and release notes; `uvx` test output showing CLI working from locally-built wheel"
  - [x] 6.1 Create or update `CHANGELOG.md` in Slash Command Manager with initial release entry documenting project launch and extracted components from SDD workflow
  - [x] 6.2 Update `README.md` in Slash Command Manager with complete installation instructions (uvx, pip), usage examples, and link back to SDD workflow repository
  - [x] 6.3 Create migration guide section in SDD workflow `README.md` explaining: how to install Slash Command Manager separately, migration from old `sdd-commands` entry point to `slash-man`, backward compatibility notes for old scripts/CI
  - [x] 6.4 Build final package wheel: `python -m build --wheel` in Slash Command Manager repository
  - [x] 6.5 Test package installation locally: `uvx --from ./dist slash-man generate --help` and verify CLI works correctly
  - [x] 6.6 Test package installation via pip workflow: `pip install ./dist/*.whl` (or equivalent) and verify `slash-man --help` works
  - [x] 6.7 Create git tag in Slash Command Manager repository: `git tag -a v1.0.0 -m "Initial release: Slash Command Manager extraction"`
  - [x] 6.8 Prepare release notes (can be GitHub release description) summarizing the initial release, extracted components, and migration path
  - [x] 6.9 Update GitHub repository metadata: add topics/tags, update description, add links to documentation
  - [x] 6.10 Update SDD workflow repository with final links and ensure migration guide is complete and clear
