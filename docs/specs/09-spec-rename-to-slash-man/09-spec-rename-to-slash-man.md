# 09-spec-rename-to-slash-man.md

## Introduction/Overview

Rename the Python package from `slash-command-manager` to `slash-man` to enable PyPI publication and eventually allow users to run `uvx slash-man --help` directly. The CLI entry point is already `slash-man`, so this change creates consistency between the package name and CLI command. The GitHub repository name will remain `slash-command-manager` as package names can differ from repository names.

## Goals

- Rename PyPI package from `slash-command-manager` to `slash-man` for consistency with CLI command
- Update all code references to use the new package name `slash-man`
- Update user-facing documentation to reflect the new package name
- Update MCP server metadata to use the new name
- Ensure package builds correctly
- Verify all tests pass and functionality remains intact after rename

## User Stories

**As a developer**, I still want to run the package locally using `uv slash-man` with no functionality changes.

**As a package maintainer**, I want the package name to be `slash-man` so that it can be published to PyPI with a name consistent with the CLI entry point.

**As a user**, I want to see consistent naming between the package name and CLI command so that the tool is easier to discover and remember.

## Demoable Units of Work

### [Unit 1]: Package Configuration Update

**Purpose:** Update core package configuration files to use the new package name `slash-man`, ensuring the package can be built and installed correctly.

**Functional Requirements:**

- The system shall have `name = "slash-man"` in `pyproject.toml` instead of `"slash-command-manager"`
- The system shall update `__version__.py` to reference `"slash-man"` in the `get_package_version()` call
- The system shall update `mcp_server/__init__.py` to reference `"slash-man"` in version detection fallback
- The system shall update `slash_commands/generators.py` to reference `"slash-man"` in version detection
- The system shall update MCP server name from `"slash-command-manager-mcp"` to `"slash-man-mcp"` in `mcp_server/__init__.py`

**Proof Artifacts:**

- `CLI: cat pyproject.toml | grep 'name ='` shows `name = "slash-man"` demonstrates package name updated
- `CLI: uv run python -m build --wheel --sdist` completes successfully demonstrates package builds correctly
- `CLI: grep -r "slash-command-manager" slash_commands/ mcp_server/ --include="*.py"` shows no results demonstrates code references updated

### [Unit 2]: Documentation Updates

**Purpose:** Update user-facing documentation to reflect the new package name, ensuring users can find and install the package correctly.

**Functional Requirements:**

- The system shall update `README.md` to reference `slash-man` as the package name in installation instructions
- The system shall update Docker image references in `README.md` from `slash-command-manager` to `slash-man`
- The system shall update any user-facing documentation in `docs/` directory that references the package name
- The system shall NOT update historical references in `CHANGELOG.md` (preserve history)

**Proof Artifacts:**

- `CLI: grep -i "slash-command-manager" README.md` shows no user-facing references demonstrates README updated
- `Screenshot: README.md installation section` shows `uv slash-man` commands demonstrates installation instructions updated
- `CLI: grep -r "slash-command-manager" docs/*.md` shows only historical/contextual references demonstrates user docs updated

### [Unit 3]: GitHub Workflows and External References

**Purpose:** Update GitHub Actions workflows and external configuration files that reference the package name or related metadata.

**Functional Requirements:**

- The system shall update any GitHub Actions workflow files that reference the package name
- The system shall update `.github/SECURITY.md` if it contains package-specific references (repository URLs remain unchanged)
- The system shall update `.github/ISSUE_TEMPLATE/config.yml` if it contains package-specific references (repository URLs remain unchanged)
- The system shall verify Docker image names in workflows match new naming (e.g., `slash-man-test`)

**Proof Artifacts:**

- `CLI: grep -r "slash-command-manager" .github/ --include="*.yml" --include="*.yaml" --include="*.md"` shows only repository URL references demonstrates workflows updated
- `CLI: cat .github/workflows/ci.yml | grep "docker build"` shows `slash-man-test` or similar demonstrates Docker naming updated

### [Unit 4]: Verification and Testing

**Purpose:** Verify the rename is complete and all functionality works correctly with the new package name.

**Functional Requirements:**

- The system shall pass all existing unit tests (`uv run pytest`)
- The system shall build the package successfully (`uv run python -m build`)
- The system shall allow installation via `uv pip install dist/*.whl` and execution of `slash-man --help`
- The system shall pass Docker-based integration tests in a clean environment

**Proof Artifacts:**

- `CLI: uv run pytest` shows all tests passing demonstrates functionality intact
- `CLI: uv run python -m build --wheel --sdist && uv pip install dist/*.whl && slash-man --help` shows help output demonstrates package installs and runs
- `CLI: docker run --rm -v $(pwd):/app -w /app python:3.12-slim bash -c "pip install uv && uv sync && uv run slash-man --help"` shows help output demonstrates clean environment works

## Non-Goals (Out of Scope)

1. **Repository Name Change**: The GitHub repository will remain `slash-command-manager` - only the PyPI package name changes
2. **Python Package Directory Renaming**: The `slash_commands/` and `mcp_server/` directories remain unchanged - only package metadata references change
3. **CHANGELOG Historical References**: Historical entries in `CHANGELOG.md` will not be updated to preserve project history
4. **Backward Compatibility**: No support for the old package name `slash-command-manager` - clean break to new name
5. **PyPI Publication**: Actual publication to PyPI is out of scope - this spec covers preparation and testing only

## Design Considerations

No specific design requirements identified. This is a package metadata and documentation update task.

## Repository Standards

Follow established repository patterns and conventions:

- Use conventional commits for all changes
- Run pre-commit hooks before committing (`uv run pre-commit run --all-files`)
- Follow existing code formatting standards (ruff)
- Maintain test coverage requirements
- Update documentation following existing markdown linting rules

## Technical Considerations

**Package Name Format:**

- PyPI package names use hyphens (`slash-man`), not underscores
- The CLI entry point is already `slash-man`, creating consistency

**Version Detection:**

- `__version__.py` uses `importlib.metadata.version()` which requires the installed package name
- Update all references from `"slash-command-manager"` to `"slash-man"` immediately
- No backward compatibility needed - clean break

**Build System:**

- Package builds using `hatchling` via `pyproject.toml`
- Build hooks in `hatch_build.py` may need verification but shouldn't require changes
- Wheel and source distribution must build successfully

**Testing Strategy:**

- Run all existing tests to ensure nothing breaks
- Docker-based clean environment testing to verify installation from scratch

**Files Requiring Updates:**

- `pyproject.toml` - package name
- `slash_commands/__version__.py` - version detection
- `mcp_server/__init__.py` - version detection and MCP server name
- `slash_commands/generators.py` - version detection
- `README.md` - user-facing documentation
- `docs/*.md` - user-facing documentation files
- `.github/workflows/*.yml` - if they reference package name
- `.github/SECURITY.md` - if it contains package-specific references
- `.github/ISSUE_TEMPLATE/config.yml` - if it contains package-specific references

## Success Metrics

1. **Package Builds Successfully**: `uv run python -m build` completes without errors
2. **All Tests Pass**: `uv run pytest` shows 100% test pass rate
3. **Package Installs Correctly**: `uv pip install dist/*.whl` succeeds and `slash-man --help` works
4. **No Old References**: `grep -r "slash-command-manager"` in code directories shows no results (except repository URLs)
5. **Docker Clean Environment Works**: Docker-based installation test passes in clean Python 3.12 container

## Open Questions

No open questions at this time. All requirements have been clarified through the questions round.
