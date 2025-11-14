# Specification: Docker-Based Integration Tests for Slash Command Manager

## Introduction/Overview

This specification adds comprehensive Docker-based integration tests that exercise the `slash-man` CLI tool in a clean, isolated environment. These tests verify end-to-end functionality including command execution, output validation, file generation, and GitHub repository integration, ensuring the tool works correctly as installed and distributed.

## Goals

- Provide automated integration tests that run in a clean Docker environment
- Verify all CLI commands and flag combinations work correctly
- Validate command output matches expected patterns
- Verify file generation and placement in correct locations
- Test GitHub repository integration end-to-end
- Ensure tests can run locally and in CI/CD pipelines

## User Stories

**As a developer**, I want Docker-based integration tests so that I can verify the CLI works correctly in a clean environment without local dependencies affecting results.

**As a CI/CD engineer**, I want automated integration tests so that I can verify releases work correctly before deployment.

**As a maintainer**, I want comprehensive integration tests so that I can catch regressions and verify new features work end-to-end.

## Demoable Units of Work

### [Unit 1]: Docker Test Environment Setup

**Purpose:** Create a Docker-based test environment that mirrors production installation
**Demo Criteria:** Running `docker build -t slash-man-test .` builds the test image using the existing Dockerfile, and `docker run --rm slash-man-test pytest tests/integration/` executes integration tests successfully

### [Unit 2]: Basic CLI Command Tests

**Purpose:** Verify all main commands (`generate`, `cleanup`, `mcp`) execute successfully
**Demo Criteria:** Tests verify `slash-man --help`, `slash-man generate --help`, `slash-man cleanup --help`, and `slash-man mcp --help` all produce correct output

### [Unit 3]: Generate Command Integration Tests

**Purpose:** Test `generate` command with various flag combinations and verify file generation
**Demo Criteria:** Tests verify:

- `slash-man generate --list-agents` lists all agents
- `slash-man generate --agent claude-code --target-path /tmp/test` generates files in correct location
- Generated files contain expected content and metadata
- Dry-run mode works without creating files

### [Unit 4]: GitHub Integration Tests

**Purpose:** Test GitHub repository integration end-to-end
**Demo Criteria:** Tests verify:

- `slash-man generate --github-repo owner/repo --github-branch main --github-path prompts` downloads and processes prompts
- Error handling for invalid repositories, branches, or paths
- Source metadata is correctly included in generated files

### [Unit 5]: File System Verification Tests

**Purpose:** Verify files are created in correct locations with correct content
**Demo Criteria:** Tests verify:

- Files are created in agent-specific directories (e.g., `~/.claude/commands/`)
- File names match expected patterns
- File content includes correct metadata (source_type, source_repo, etc.)
- File permissions are correct

### [Unit 6]: Error Scenario Tests

**Purpose:** Verify error handling and validation work correctly
**Demo Criteria:** Tests verify:

- Invalid flag combinations produce appropriate errors
- Missing required flags produce clear error messages
- GitHub API errors are handled gracefully
- File system errors are handled appropriately

## Functional Requirements

1. **The system shall provide a Docker-based test environment** that:
   - Uses the existing Dockerfile (which is intended for testing purposes)
   - Installs the package as it would be installed in production
   - Provides a clean environment without local dependencies

2. **The system shall provide pytest-based integration tests** that:
   - Use `subprocess.run()` to execute actual CLI commands
   - Verify exit codes, stdout, and stderr using exact text matching
   - Use pytest fixtures for test setup and teardown
   - Follow existing test patterns where possible
   - Be part of the existing pytest test suite structure (`tests/integration/`)

3. **The system shall test all CLI commands** including:
   - `slash-man --help` and `slash-man --version`
   - `slash-man generate` with **all** flag combinations
   - `slash-man cleanup` with **all** flag combinations
   - `slash-man mcp` with **all** flag combinations
   - Tests for **all** supported agents

4. **The system shall verify command output** by:
   - Checking exit codes (0 for success, non-zero for errors)
   - Validating stdout using **exact text matching** (not regex patterns)
   - Validating stderr contains expected error messages using **exact text matching**
   - Verifying help output format and content using **exact text matching**

5. **The system shall verify file generation** by:
   - Checking files are created in expected locations
   - Verifying file names match expected patterns
   - Validating file content structure (metadata format, required fields)
   - Validating **exact file content** (full content comparison)
   - Checking file metadata including **permissions and timestamps**

6. **The system shall test GitHub integration** by:
   - **Mocking GitHub API** using pytest-httpx or similar
   - Verifying prompts are downloaded correctly
   - Verifying source metadata is included
   - Testing **critical error scenarios** (404, 403, network errors, invalid repository format, missing flags)

7. **The system shall provide test fixtures** for:
   - Temporary directories for test data
   - **Mock GitHub API responses** (using pytest-httpx or similar)
   - **Test prompt files** (stored in `tests/integration/fixtures/prompts/` in the repository)
   - Clean agent directories

8. **The system shall integrate with CI/CD** by:
   - Running tests in GitHub Actions **on every PR** (not optional, cannot be skipped)
   - Running tests in **pre-commit hooks on push**
   - Providing clear test output and reporting
   - Failing CI builds on test failures

## Non-Goals (Out of Scope)

1. **Unit test replacement**: These are integration tests, not replacements for existing unit tests
2. **Performance testing**: Focus is on correctness, not performance
3. **Cross-platform testing**: Focus on Linux/Docker environment initially
4. **GUI testing**: Only CLI functionality is tested
5. **MCP server runtime testing**: MCP server startup/operation testing is out of scope (only CLI flags)

## Design Considerations

### Test Structure

**Selected:** Pytest Test Suite

- Full pytest test suite (`tests/integration/`)
- Uses pytest fixtures and markers
- Better integration with existing test infrastructure
- Can use pytest-docker for Docker management
- More maintainable and extensible
- Tests will be part of existing pytest suite structure

### Docker Approach

**Selected:** Use Existing Dockerfile

- The existing Dockerfile is intended for testing purposes
- Single Dockerfile simplifies maintenance
- Tests will run inside the container built from existing Dockerfile

### GitHub API Testing

**Selected:** Mock GitHub API

- Use pytest-httpx or similar to mock API responses
- More reliable and faster
- Requires maintaining mock data
- No dependency on external network or rate limits

## Technical Considerations

1. **Test Execution**: Tests run inside Docker container using pytest, executed as part of CI and pre-commit hooks on push
2. **Test Data**: Use test prompt files created in the repository (`tests/integration/fixtures/prompts/`) - no dynamic generation
3. **Output Verification**: Use exact text matching for command output validation
4. **File Verification**: Use pathlib to verify:
   - File existence
   - File content structure (metadata format, required fields)
   - Exact file content (full content comparison)
   - File metadata (permissions, timestamps)
5. **Error Testing**: Test critical error cases (invalid flags, missing required flags, GitHub API errors, file system errors)
6. **Test Isolation**: Each test should be independent and clean up after itself
7. **Test Scope**: Cover all flag combinations, all agents, both success and error scenarios
8. **CI Integration**: Tests run on every PR, are not optional, and fail CI builds on failure

## Design Decisions Summary

Based on requirements and clarifications:

- **Test Structure**: Pytest Test Suite (`tests/integration/`) - part of existing pytest suite
- **Docker Approach**: Use existing Dockerfile (intended for testing purposes)
- **GitHub API**: Mock GitHub API using pytest-httpx or similar
- **Test Scope**: All flag combinations, all agents, both success and error scenarios
- **Test Data**: Test prompt files stored in repository (`tests/integration/fixtures/prompts/`), no dynamic generation
- **CI Integration**: Run on every PR, in pre-commit hooks on push, not optional
- **Output Verification**: Exact text matching (not regex patterns)
- **File Verification**: File existence, content structure, exact content, and metadata (permissions, timestamps)
- **Error Scenarios**: Critical error cases only (invalid flags, missing required flags, GitHub API errors, file system errors)

## Success Metrics

1. **Test Coverage**: All main CLI commands have integration tests covering all flag combinations and all agents
2. **Reliability**: Tests pass consistently in clean Docker environment
3. **Maintainability**: Tests are easy to understand and modify
4. **CI Integration**: Tests run automatically on every PR and in pre-commit hooks, failing builds on failure
5. **Documentation**: Test execution is clearly documented
6. **Completeness**: All critical error scenarios are tested
