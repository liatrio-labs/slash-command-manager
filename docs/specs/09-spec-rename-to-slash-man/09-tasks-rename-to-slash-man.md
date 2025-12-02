# 09-tasks-rename-to-slash-man.md

## Relevant Files

- `pyproject.toml` - Contains the package name configuration that needs to be updated from `slash-command-manager` to `slash-man`.
- `slash_commands/__version__.py` - Contains version detection fallback that references the package name `"slash-command-manager"` which needs updating to `"slash-man"`.
- `mcp_server/__init__.py` - Contains version detection fallback referencing `"slash-command-manager"` and MCP server name `"slash-command-manager-mcp"` that need updating to `"slash-man"` and `"slash-man-mcp"` respectively.
- `slash_commands/generators.py` - Contains version detection fallback that references the package name `"slash-command-manager"` which needs updating to `"slash-man"`.
- `README.md` - Contains user-facing documentation with installation instructions and Docker examples that reference `slash-command-manager` and need updating to `slash-man`.
- `docs/operations.md` - Contains MCP server configuration examples and Docker deployment examples that reference `slash-command-manager` and need updating to `slash-man`.
- `docs/GitHub_Branch_Download_Bug.md` - Contains Docker image name examples that reference `slash-command-manager` and need updating to `slash-man` for consistency.

### Notes

- Repository URLs (e.g., `https://github.com/liatrio-labs/slash-command-manager`) should remain unchanged as the repository name stays the same.
- Historical references in `CHANGELOG.md` and proof artifacts in `docs/specs/` should remain unchanged to preserve project history.
- The GitHub workflow file `.github/workflows/ci.yml` already uses `slash-man-test` for Docker image naming, so it may not need changes.
- `.github/SECURITY.md` and `.github/ISSUE_TEMPLATE/config.yml` only contain repository URLs and should remain unchanged.
- Follow repository standards: use conventional commits, run pre-commit hooks (`uv run pre-commit run --all-files`), and maintain test coverage.

## Tasks

### [x] 1.0 Update Package Configuration Files

#### 1.0 Proof Artifact(s)

- CLI: `cat pyproject.toml | grep 'name ='` shows `name = "slash-man"` demonstrates package name updated
- CLI: `grep -r "slash-command-manager" slash_commands/ mcp_server/ --include="*.py"` shows no results demonstrates code references updated
- CLI: `uv run python -m build --wheel --sdist` completes successfully demonstrates package builds correctly

#### 1.0 Tasks

- [x] 1.1 Update `pyproject.toml` line 6: Change `name = "slash-command-manager"` to `name = "slash-man"`
- [x] 1.2 Update `slash_commands/__version__.py` line 83: Change `get_package_version("slash-command-manager")` to `get_package_version("slash-man")`
- [x] 1.3 Update `mcp_server/__init__.py` line 17: Change `version("slash-command-manager")` to `version("slash-man")`
- [x] 1.4 Update `mcp_server/__init__.py` line 30: Change MCP server name from `"slash-command-manager-mcp"` to `"slash-man-mcp"` in the `FastMCP(name=...)` call
- [x] 1.5 Update `slash_commands/generators.py` line 18: Change `version("slash-command-manager")` to `version("slash-man")`
- [x] 1.6 Verify package builds: Run `uv run python -m build --wheel --sdist` to ensure build succeeds with new package name
- [x] 1.7 Verify no old references remain: Run `grep -r "slash-command-manager" slash_commands/ mcp_server/ --include="*.py"` and confirm no results

### [x] 2.0 Update User-Facing Documentation

#### 2.0 Proof Artifact(s)

- CLI: `grep -i "slash-command-manager" README.md` shows no user-facing references demonstrates README updated
- Screenshot: README.md installation section shows `uv slash-man` commands demonstrates installation instructions updated
- CLI: `grep -r "slash-command-manager" docs/*.md` shows only historical/contextual references demonstrates user docs updated

#### 2.0 Tasks

- [x] 2.1 Update `README.md` line 253: Change Docker image name from `slash-command-manager` to `slash-man` in the `docker build` command example
- [x] 2.2 Update `README.md` line 256: Change Docker image name from `slash-command-manager` to `slash-man` in the `docker run` command example
- [x] 2.3 Update `README.md` line 259: Change Docker image name from `slash-command-manager` to `slash-man` in the `docker run` command example
- [x] 2.4 Update `docs/operations.md` line 101: Change MCP server name from `"slash-command-manager"` to `"slash-man"` in the Claude Desktop configuration example
- [x] 2.5 Update `docs/operations.md` line 103: Update the path comment to reference `slash-man` instead of `slash-command-manager` (if applicable)
- [x] 2.6 Update `docs/operations.md` line 117: Change MCP server name from `"slash-command-manager"` to `"slash-man"` in the VS Code MCP plugin configuration example
- [x] 2.7 Update `docs/operations.md` line 119: Update the path comment to reference `slash-man` instead of `slash-command-manager` (if applicable)
- [x] 2.8 Update `docs/operations.md` line 231: Change Docker image name from `slash-command-manager` to `slash-man` in the Docker deployment example
- [x] 2.9 Update `docs/GitHub_Branch_Download_Bug.md` line 189: Change Docker image name from `slash-command-manager` to `slash-man` in the Docker build example
- [x] 2.10 Update `docs/GitHub_Branch_Download_Bug.md` line 195: Change Docker image name from `slash-command-manager` to `slash-man` in the Docker run example (if present)
- [x] 2.11 Verify documentation updates: Run `grep -i "slash-command-manager" README.md` and confirm no user-facing references remain (repository URLs are acceptable)
- [x] 2.12 Verify docs directory: Run `grep -r "slash-command-manager" docs/*.md` and confirm only historical/contextual references remain (repository URLs are acceptable)

### [x] 3.0 Update GitHub Workflows and Configuration Files

#### 3.0 Proof Artifact(s)

- CLI: `grep -r "slash-command-manager" .github/ --include="*.yml" --include="*.yaml" --include="*.md"` shows only repository URL references demonstrates workflows updated
- CLI: `cat .github/workflows/ci.yml | grep "docker build"` shows `slash-man-test` or similar demonstrates Docker naming updated

#### 3.0 Tasks

- [x] 3.1 Verify `.github/workflows/ci.yml`: Check if Docker image name references need updating (line 207 already uses `slash-man-test`, verify no other references exist)
- [x] 3.2 Verify `.github/SECURITY.md`: Confirm it only contains repository URLs (line 19) and no package-specific references that need updating
- [x] 3.3 Verify `.github/ISSUE_TEMPLATE/config.yml`: Confirm it only contains repository URLs and no package-specific references that need updating
- [x] 3.4 Run verification grep: Execute `grep -r "slash-command-manager" .github/ --include="*.yml" --include="*.yaml" --include="*.md"` and confirm only repository URL references remain

### [x] 4.0 Verify Package Builds and Tests Pass

#### 4.0 Proof Artifact(s)

- CLI: `uv run pytest` shows all tests passing demonstrates functionality intact
- CLI: `uv run python -m build --wheel --sdist && uv pip install dist/*.whl && slash-man --help` shows help output demonstrates package installs and runs
- CLI: `docker run --rm -v $(pwd):/app -w /app python:3.12-slim bash -c "pip install uv && uv sync && uv run slash-man --help"` shows help output demonstrates clean environment works

#### 4.0 Tasks

- [x] 4.1 Run all unit tests: Execute `uv run pytest` and verify all tests pass
- [x] 4.2 Build package: Run `uv run python -m build --wheel --sdist` and verify build completes successfully
- [x] 4.3 Test package installation: Run `uv pip install dist/*.whl` and verify installation succeeds
- [x] 4.4 Test CLI execution: Run `slash-man --help` after installation and verify help output displays correctly
- [x] 4.5 Test Docker clean environment: Execute `docker run --rm -v $(pwd):/app -w /app python:3.12-slim bash -c "pip install uv && uv sync && uv run slash-man --help"` and verify help output displays correctly
- [x] 4.6 Run pre-commit hooks: Execute `uv run pre-commit run --all-files` to ensure code quality standards are met
- [x] 4.7 Verify version detection: Run `slash-man --version` and verify version string displays correctly with new package name
