# 05-tasks-github-repository-support.md

## Relevant Files

- `slash_commands/github_utils.py` - New module for GitHub URL parsing, API integration, and file downloading functionality
- `tests/test_github_utils.py` - Unit tests for GitHub utilities module
- `slash_commands/cli.py` - Main CLI entry point, needs modification to add --github-url option and validation logic
- `tests/test_cli.py` - CLI tests, needs extension for GitHub URL option testing
- `slash_commands/writer.py` - Core SlashCommandWriter class, needs extension to support GitHub sources and metadata generation
- `tests/test_writer.py` - Writer tests, needs extension for GitHub source functionality
- `slash_commands/generators.py` - Command generators, needs modification to include source metadata in output
- `tests/test_generators.py` - Generator tests, needs extension for metadata verification
- `mcp_server/prompt_utils.py` - Contains MarkdownPrompt dataclass, may need extension for source metadata
- `pyproject.toml` - Project dependencies, needs requests library added
- `tests/conftest.py` - Test configuration, may need fixtures for GitHub testing

### Notes

- All code changes should be implemented via a strict Test-Driven Development (TDD) approach
- Unit tests should be placed in the `tests/` directory following the existing project structure (e.g., `tests/test_github_utils.py` for `slash_commands/github_utils.py`)
- Use `pytest` to run tests (as used in pre-commit hooks) or `uv run pytest` for local development
- Mock external GitHub API calls using `unittest.mock` to avoid network dependencies (following existing test patterns)
- Use temporary directories for testing file downloads to avoid polluting the filesystem
- Integration tests should use a real public repository (spec-driven-workflow) for end-to-end validation
- Follow existing test patterns using `typer.testing.CliRunner` for CLI testing

## Tasks

- [x] 1.0 Create GitHub Utilities Module
  - **Satisfies:** U1, FR1, FR2
  - Demo Criteria: "Run unit tests for GitHub URL parsing and validation; test parsing of https://github.com/liatrio-labs/spec-driven-workflow/tree/main/prompts and rejection of invalid URLs"
  - Proof Artifact(s): "Test: test_github_utils.py showing URL parsing tests; CLI: python -c 'from slash_commands.github_utils import parse_github_url; print(parse_github_url(\"https://github.com/owner/repo/tree/main/prompts\"))'"
  - [x] 1.1 Create failing unit tests in tests/test_github_utils.py for GitHubRepoError exception class
  - [x] 1.2 Create failing unit tests for parse_github_url() function with valid/invalid URL scenarios
  - [x] 1.3 Create failing unit tests for list_github_directory_files() function with GitHub API integration
  - [x] 1.4 Create failing unit tests for download_github_prompts() function with network timeout scenarios
  - [x] 1.5 Create failing unit tests for file size validation (>1MB rejection, >100 files warning)
  - [x] 1.6 Create failing unit tests for get_github_repo_info() function with repository metadata
  - [x] 1.7 Add requests dependency to pyproject.toml
  - [x] 1.8 Implement slash_commands/github_utils.py with GitHubRepoError exception class to make tests pass
  - [x] 1.9 Implement parse_github_url() function to make URL parsing tests pass
  - [x] 1.10 Implement remaining GitHub utilities functions to make all tests pass

- [ ] 2.0 Implement GitHub API Integration and File Download
  - **Satisfies:** U2, FR3, FR4, FR10, FR11, FR12, FR13, FR17
  - Demo Criteria: "Successfully download .md files from spec-driven-workflow repository prompts directory to temporary location"
  - Proof Artifact(s): "CLI: python -c 'from slash_commands.github_utils import download_github_prompts; print(download_github_prompts(\"liatrio-labs\", \"spec-driven-workflow\"))'; Test: integration test showing file download"
  - [ ] 2.1 Create failing integration tests for network timeout configuration (30 seconds) scenarios
  - [ ] 2.2 Create failing integration tests for retry logic with exponential backoff (up to 3 retries)
  - [ ] 2.3 Create failing integration tests for temporary directory creation and cleanup using tempfile
  - [ ] 2.4 Create failing integration tests for file size validation during download process
  - [ ] 2.5 Create failing integration tests for progress reporting of downloaded files count
  - [ ] 2.6 Create failing integration tests for enhanced error scenarios (empty directories, no .md files, permission errors)
  - [ ] 2.7 Create failing integration tests for actual GitHub repository downloads
  - [ ] 2.8 Create failing performance tests for large repository handling
  - [ ] 2.9 Create failing end-to-end integration tests for complete download workflow
  - [ ] 2.10 Implement GitHub API integration functions to make all integration tests pass

- [ ] 3.0 Add CLI Option Integration and Validation
  - **Satisfies:** U3, U6, U7, FR5, FR8, FR9
  - Demo Criteria: "Run slash-man generate --github-url https://github.com/liatrio-labs/spec-driven-workflow/tree/main/prompts and see option validation working"
  - Proof Artifact(s): "CLI: slash-man generate --help showing new --github-url option; CLI: slash-man generate --github-url invalid-url showing error; CLI: slash-man generate --prompts-dir ./local --github-url https://... showing conflict error"
  - [ ] 3.1 Create failing CLI tests for --github-url option addition to generate command
  - [ ] 3.2 Create failing CLI tests for option mutual exclusivity validation (--prompts-dir vs --github-url)
  - [ ] 3.3 Create failing CLI tests for required prompt source validation (neither option specified)
  - [ ] 3.4 Create failing CLI tests for GitHub URL format validation in CLI layer
  - [ ] 3.5 Create failing CLI tests for help text with GitHub URL format examples
  - [ ] 3.6 Create failing CLI tests for error messages on invalid URLs and conflicting options
  - [ ] 3.7 Create failing CLI tests for option conflict scenarios using CliRunner
  - [ ] 3.8 Create failing CLI tests for missing source validation scenarios
  - [ ] 3.9 Create failing CLI tests for help text output validation
  - [ ] 3.10 Implement CLI option integration and validation to make all CLI tests pass

- [ ] 4.0 Extend SlashCommandWriter for GitHub Sources
  - **Satisfies:** U3, U4, FR6, FR14
  - Demo Criteria: "Generate slash commands successfully from GitHub repository with proper source metadata"
  - Proof Artifact(s): "CLI: slash-man generate --github-url https://github.com/liatrio-labs/spec-driven-workflow/tree/main/prompts --dry-run; Generated files: .windsurf/workflows/*.md showing GitHub source metadata"
  - [ ] 4.1 Create failing writer tests for SlashCommandWriter.**init** accepting GitHub URL parameters
  - [ ] 4.2 Create failing writer tests for _load_prompts() method handling GitHub sources
  - [ ] 4.3 Create failing writer tests for GitHub repository info retrieval and storage
  - [ ] 4.4 Create failing writer tests for progress reporting of GitHub downloads in writer
  - [ ] 4.5 Create failing writer tests for backward compatibility with existing local directory functionality
  - [ ] 4.6 Create failing writer tests for GitHub source handling in dry-run functionality
  - [ ] 4.7 Create failing writer tests for integration with existing agent detection and selection
  - [ ] 4.8 Create failing writer tests for temporary file cleanup in writer workflow
  - [ ] 4.9 Create failing writer tests for GitHub source metadata generation
  - [ ] 4.10 Implement SlashCommandWriter extensions to make all writer tests pass

- [ ] 5.0 Implement Enhanced Error Handling and Validation
  - **Satisfies:** U4, U6, U7, FR7, FR17
  - Demo Criteria: "Test comprehensive error scenarios including missing source, empty directories, and network failures"
  - Proof Artifact(s): "CLI: slash-man generate (no options) showing required source error; CLI: slash-man generate --github-url https://github.com/owner/nonexistent showing specific error; Test: error handling test suite"
  - [ ] 5.1 Create failing error handling tests for empty repository directories scenarios
  - [ ] 5.2 Create failing error handling tests for repositories with no .md files scenarios
  - [ ] 5.3 Create failing error handling tests for malformed markdown file detection and reporting
  - [ ] 5.4 Create failing error handling tests for permission denied errors in GitHub API calls
  - [ ] 5.5 Create failing error handling tests for enhanced network error messages with troubleshooting guidance
  - [ ] 5.6 Create failing error handling tests for GitHub repository existence validation
  - [ ] 5.7 Create failing error handling tests for CLI integration error scenarios
  - [ ] 5.8 Create failing error handling tests for user-friendly and actionable error messages
  - [ ] 5.9 Create failing error handling tests for application stability during errors
  - [ ] 5.10 Implement enhanced error handling and validation to make all error tests pass

- [ ] 6.0 Add Source Metadata Generation for All Sources
  - **Satisfies:** U5, FR15, FR16
  - Demo Criteria: "Generate commands from both GitHub and local sources, verify metadata includes appropriate source attribution"
  - Proof Artifact(s): "CLI: slash-man generate --github-url https://...; CLI: slash-man generate --prompts-dir ./local; Generated files: showing source_type, source_github_url, source_local_path, and timestamps"
  - [ ] 6.1 Create failing generator tests for MarkdownPrompt dataclass extension with source metadata fields
  - [ ] 6.2 Create failing generator tests for command generators including source metadata in output
  - [ ] 6.3 Create failing generator tests for GitHub source metadata (URL, branch, commit hash, timestamp)
  - [ ] 6.4 Create failing generator tests for local directory source metadata (absolute path, timestamp)
  - [ ] 6.5 Create failing generator tests for source type distinction in metadata (github vs local)
  - [ ] 6.6 Create failing generator tests for ISO 8601 timestamp format consistency
  - [ ] 6.7 Create failing generator tests for metadata generation from both GitHub and local sources
  - [ ] 6.8 Create failing generator tests for metadata preservation in generated command files
  - [ ] 6.9 Create failing generator tests for clear and unambiguous source attribution in output
  - [ ] 6.10 Implement source metadata generation to make all generator tests pass

## Spec Coverage Validation

### Demoable Units Coverage

- ✅ U1: GitHub URL Parsing and Validation → Task 1.0
- ✅ U2: GitHub API Integration for Directory Listing → Task 2.0
- ✅ U3: CLI Integration with Generate Command → Tasks 3.0, 4.0
- ✅ U4: Multi-Branch Support and Error Handling → Task 5.0
- ✅ U5: Source Metadata Generation → Task 6.0
- ✅ U6: Option Conflict Handling → Task 3.0, 5.0
- ✅ U7: Required Source Validation → Task 3.0, 5.0

### Functional Requirements Coverage

- ✅ FR1: GitHub URL Parsing → Task 1.0
- ✅ FR2: Branch Auto-Detection → Task 1.0
- ✅ FR3: GitHub API Integration → Task 2.0
- ✅ FR4: File Download → Task 2.0
- ✅ FR5: CLI Option Integration → Task 3.0
- ✅ FR6: Backward Compatibility → Task 4.0
- ✅ FR7: Error Handling → Tasks 2.0, 3.0, 5.0
- ✅ FR8: Option Mutual Exclusivity → Task 3.0
- ✅ FR9: Required Prompt Source → Task 3.0
- ✅ FR10: Network Timeout and Retry → Task 2.0
- ✅ FR11: File Size Limits → Task 2.0
- ✅ FR12: Temporary File Management → Task 2.0
- ✅ FR13: Public Repository Support → Task 2.0
- ✅ FR14: Progress Reporting → Task 4.0
- ✅ FR15: Source Metadata Generation → Task 6.0
- ✅ FR16: Metadata Preservation → Task 6.0
- ✅ FR17: Enhanced Error Scenarios → Tasks 2.0, 5.0

**All demoable units and functional requirements are covered by the parent tasks.**

## Implementation Notes

### End-to-End Validation

After completing all tasks, verify the complete workflow:

```bash
# Test GitHub repository installation
slash-man generate --github-url https://github.com/liatrio-labs/spec-driven-workflow/tree/main/prompts --dry-run

# Test local directory installation (backward compatibility)
slash-man generate --prompts-dir ./local --dry-run

# Test error scenarios
slash-man generate --github-url invalid-url
slash-man generate --prompts-dir ./local --github-url https://...
slash-man generate  # (no source specified)
```

### TDD Implementation Guidelines

- **Red Phase:** Write failing tests first for each sub-task
- **Green Phase:** Implement minimal code to make tests pass
- **Refactor Phase:** Improve code while maintaining test coverage
- **Run Tests:** Use `pytest` for pre-commit compliance or `uv run pytest` for local development
- **Mock External Dependencies:** Use `unittest.mock` for GitHub API calls in unit tests
- **Integration Tests:** Use real repositories for end-to-end validation (spec-driven-workflow)
