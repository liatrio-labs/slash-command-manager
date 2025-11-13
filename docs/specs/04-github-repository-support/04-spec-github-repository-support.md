# 04-spec-github-repository-support.md

## Introduction/Overview

This specification adds GitHub repository support to the slash command manager, enabling users to download prompt files directly from public GitHub repositories. The feature provides explicit CLI flags (`--github-repo`, `--github-branch`, `--github-path`) that eliminate parsing ambiguity and make the interface clearer and more maintainable. Users can now source prompts from GitHub repositories alongside local directories, expanding prompt distribution and sharing capabilities across teams and organizations.

## Goals

- Enable downloading prompt files from public GitHub repositories using explicit CLI flags
- Provide clear, unambiguous interface for specifying repository, branch, and path
- Integrate GitHub repository support seamlessly with existing local directory functionality
- Maintain mutual exclusivity between local and GitHub prompt sources
- Provide helpful error messages with examples when validation fails

## User Stories

**As a developer**, I want to download prompts from a GitHub repository using explicit flags so that I can easily use shared prompt collections without manual file management or URL parsing ambiguity.

**As a team lead**, I want to specify a repository, branch, and path explicitly so that my team can use consistent prompt versions across different environments with clear, unambiguous configuration.

**As a prompt author**, I want to distribute my prompts via GitHub so that others can consume them directly without cloning repositories manually or dealing with complex URL formats.

**As a DevOps engineer**, I want to use different prompt sets from different branches and paths so that I can test prompt variations in CI/CD pipelines with clear, scriptable configuration.

## Demoable Units of Work

### [Unit 1]: GitHub Repository Flag Integration

**Purpose:** Add GitHub repository support to the CLI with explicit flags for repository, branch, and path
**Demo Criteria:** Running `uv run slash-man generate --github-repo owner/repo --github-branch main --github-path prompts --agent claude-code --dry-run --target-path /tmp/test-output` successfully validates flags and shows prompts that would be downloaded
**Proof Artifacts:** CLI help output showing new flags, successful command execution with dry-run output, test: `test_cli_github_flags_validation()`

### [Unit 2]: GitHub Repository Validation

**Purpose:** Validate repository format and provide clear error messages when flags are invalid or missing
**Demo Criteria:** Running `uv run slash-man generate --github-repo invalid-format --target-path /tmp/test-output` shows clear error: "Repository must be in format owner/repo, got: invalid-format. Example: liatrio-labs/spec-driven-workflow"
**Proof Artifacts:** CLI error output showing validation messages, test: `test_validate_github_repo_invalid_format()`, test: `test_cli_github_flags_missing_required()`

### [Unit 3]: GitHub Prompt Download and Loading

**Purpose:** Download markdown files from GitHub repository and load them as prompts
**Demo Criteria:**

- Directory path on `main` branch: Running `uv run slash-man generate --github-repo liatrio-labs/spec-driven-workflow --github-branch main --github-path prompts --agent claude-code --target-path /tmp/test-output` downloads prompts from directory and generates command files
- Directory path on `refactor/improve-workflow` branch: Running `uv run slash-man generate --github-repo liatrio-labs/spec-driven-workflow --github-branch refactor/improve-workflow --github-path prompts --agent claude-code --target-path /tmp/test-output` downloads prompts from directory and generates command files
- Single file path on `refactor/improve-workflow` branch: Running `uv run slash-man generate --github-repo liatrio-labs/spec-driven-workflow --github-branch refactor/improve-workflow --github-path prompts/generate-spec.md --agent claude-code --target-path /tmp/test-output` downloads single file and generates command files
- Single file path on `main` branch: Running `uv run slash-man generate --github-repo liatrio-labs/spec-driven-workflow --github-branch main --github-path prompts/generate-spec.md --agent claude-code --target-path /tmp/test-output` downloads single file and generates command files (if file exists on main branch)
**Proof Artifacts:** Generated command files in agent directories, CLI output showing prompts loaded, test: `test_writer_loads_prompts_from_github()`, test: `test_writer_loads_single_file_from_github()`

### [Unit 4]: GitHub and Local Directory Mutual Exclusivity

**Purpose:** Ensure users cannot specify both local directory and GitHub repository simultaneously
**Demo Criteria:** Running `uv run slash-man generate --prompts-dir ./prompts --github-repo owner/repo --github-branch main --github-path prompts --target-path /tmp/test-output` shows error explaining mutual exclusivity
**Proof Artifacts:** CLI error message, test: `test_cli_github_and_local_mutually_exclusive()`

### [Unit 5]: Prompt Metadata Source Tracking

**Purpose:** Update prompt metadata to include source information (local directory or GitHub repository details)
**Demo Criteria:**

- GitHub directory: Running `uv run slash-man generate --github-repo liatrio-labs/spec-driven-workflow --github-branch refactor/improve-workflow --github-path prompts --agent claude-code --target-path /tmp/test-output` generates command files with metadata containing `source_type: "github"`, `source_repo: "liatrio-labs/spec-driven-workflow"`, `source_branch: "refactor/improve-workflow"`, and `source_path: "prompts"`
- GitHub single file: Running `uv run slash-man generate --github-repo liatrio-labs/spec-driven-workflow --github-branch refactor/improve-workflow --github-path prompts/generate-spec.md --agent claude-code --target-path /tmp/test-output` generates command files with metadata containing `source_type: "github"`, `source_repo: "liatrio-labs/spec-driven-workflow"`, `source_branch: "refactor/improve-workflow"`, and `source_path: "prompts/generate-spec.md"`
- Local directory: Running with `uv run slash-man generate --prompts-dir ./prompts --target-path /tmp/test-output` generates metadata containing `source_type: "local"` and `source_dir: "./prompts"` (or absolute path)
**Proof Artifacts:** Generated command file metadata inspection showing source tracking fields, test: `test_prompt_metadata_github_source()`, test: `test_prompt_metadata_local_source()`

### [Unit 6]: Documentation and CI Updates

**Purpose:** Update documentation and audit CI workflows to ensure compatibility with GitHub repository support functionality
**Demo Criteria:** README.md includes examples of GitHub flag usage, CI workflows include `--help` flag tests for main command and subcommands, and existing CI workflows continue to pass with the new changes
**Proof Artifacts:** Updated README.md with GitHub examples, CI workflow with `--help` flag tests for `uv run slash-man --help`, `uv run slash-man generate --help`, and `uv run slash-man cleanup --help`, CI workflow audit report showing compatibility, documentation build passes, test: `test_documentation_github_examples()`

## Functional Requirements

1. **The system shall provide three CLI flags for GitHub repository access:**
   - `--github-repo` (required): Repository in format `owner/repo`
   - `--github-branch` (required): Branch name (e.g., `main`, `release/v1.0`)
   - `--github-path` (required): Path to prompts directory or single prompt file within repository (e.g., `prompts` for a directory, `prompts/my-prompt.md` for a single file)

2. **The system shall require all three GitHub flags to be provided together** when using GitHub as a prompt source

3. **The system shall validate the `--github-repo` format** and raise clear errors with examples if the format is invalid (must contain exactly one `/` separating owner and repo)

4. **The system shall validate that `--github-repo`, `--github-branch`, and `--github-path` are mutually exclusive with `--prompts-dir`** and provide clear error messages when both are specified

5. **The system shall download markdown files (`.md`) from the specified GitHub repository path** using the GitHub Contents API. The `--github-path` may point to either:
   - A directory: The system shall download all `.md` files from the immediate directory (not recursively processing subdirectories)
   - A single file: The system shall download the single `.md` file if the path points directly to a markdown file

6. **The system shall load downloaded GitHub prompts** using the same `MarkdownPrompt` loading mechanism as local prompts

7. **The system shall update prompt metadata to include source information:**
   - For local prompts: Include `source_type: "local"` and `source_dir` (the directory path provided via `--prompts-dir`)
   - For GitHub prompts: Include `source_type: "github"`, `source_repo` (owner/repo), `source_branch` (branch name), and `source_path` (path within repository)
   - Source metadata shall be included in the generated command file metadata alongside existing fields

8. **The system shall handle GitHub API errors gracefully** with clear error messages indicating repository access issues, network problems, or invalid branch/path combinations

9. **The system shall support branch names with slashes** (e.g., `release/v1.0`, `feature/add-new-feature`) without any parsing ambiguity since they are provided explicitly

10. **The system shall support paths with nested directories** (e.g., `docs/prompts/commands`) without any parsing ambiguity since paths are provided explicitly

11. **The system shall support paths pointing to single files** (e.g., `prompts/my-prompt.md`) in addition to directories. When a single file path is provided, only that file shall be downloaded and processed. The file must have a `.md` extension or an error shall be raised with a clear message.

12. **The system shall provide helpful error messages with examples** when validation fails, including format requirements and usage examples

13. **The system shall update README.md documentation** to include examples of GitHub repository flag usage alongside existing local directory examples, including examples for both directory paths and single file paths

14. **The system shall add CI tests that verify `--help` flag functionality** for the main command (`slash-man --help`) and all subcommands (`slash-man generate --help`, `slash-man cleanup --help`) to ensure help output is properly generated and formatted

15. **The system shall audit existing CI workflows** to ensure they remain compatible with the new GitHub repository functionality without requiring specific updates

16. **The system shall ensure documentation builds successfully** with all new GitHub-related examples and references properly formatted and validated

17. **The system shall verify existing test coverage** adequately covers the new GitHub functionality through the existing test framework

## Non-Goals (Out of Scope)

1. **URL parsing support**: This specification does not include support for parsing GitHub URLs (e.g., `https://github.com/owner/repo/tree/branch/path`). Users must provide explicit flags for repository, branch, and path.

2. **Backward compatibility with URL-based flags**: There is no `--github-url` flag or URL parsing functionality. This is a clean implementation without legacy URL support.

3. **GitHub authentication**: This feature only supports public repositories. Private repository access and authentication are out of scope.

4. **Support for other Git hosting platforms**: Only GitHub is supported. GitLab, Bitbucket, and other platforms are out of scope.

5. **GitHub Enterprise support**: Only `github.com` is supported. Custom GitHub Enterprise domains are out of scope.

6. **Automatic branch detection**: The system does not automatically determine the default branch. Users must explicitly specify `--github-branch`.

7. **Path auto-discovery**: The system does not automatically search for prompt directories. Users must explicitly specify `--github-path`.

8. **Caching or offline support**: Downloaded prompts are not cached. Each execution requires fresh API calls to GitHub.

9. **Documentation maintenance automation**: Automated documentation updates are out of scope. Documentation updates must be done manually as part of the implementation.

## Design Considerations

No specific UI/UX design requirements for this feature. The functionality is internal to the CLI tool and does not affect user-facing interfaces directly. Error messages will be displayed in the CLI output following existing patterns (see `slash_commands/cli.py` for current error message format).

## Technical Considerations

1. **GitHub API Integration**: The system shall use the GitHub REST API Contents endpoint (`GET /repos/{owner}/{repo}/contents/{path}`) to list and download files from the specified repository path.

2. **Dependencies**: The system shall use the existing `requests` library (already in dependencies) for GitHub API calls. No new dependencies are required.

3. **Error Handling**: The system shall handle common GitHub API error scenarios:
   - 404 Not Found (repository, branch, or path doesn't exist)
   - 403 Forbidden (rate limiting, authentication required)
   - Network timeouts and connection errors
   - Invalid file formats (non-markdown files)

4. **Validation Function**: A new `validate_github_repo()` function shall be created in `slash_commands/github_utils.py` to validate and split the `owner/repo` format, returning a tuple of `(owner, repo)`.

5. **Writer Class Extension**: The `SlashCommandWriter` class shall be extended to accept GitHub parameters (`github_repo`, `github_branch`, `github_path`) and handle prompt loading from GitHub repositories.

6. **Temporary Directory Management**: Downloaded GitHub prompts shall be stored in a temporary directory that is cleaned up after processing, similar to existing temporary file handling patterns.

7. **File Filtering**: Only markdown files (`.md` extension) shall be downloaded and processed from the GitHub repository path, consistent with local prompt loading behavior. When `--github-path` points to a single file, the file must have a `.md` extension or an error shall be raised. When `--github-path` points to a directory, only `.md` files in the immediate directory shall be processed (subdirectories are not recursively processed).

8. **Retry Logic**: GitHub API calls shall use existing retry logic patterns (if any) or implement basic retry with exponential backoff for transient network failures.

9. **Testing Strategy**: Tests shall use mocking for GitHub API calls to avoid network dependencies and ensure deterministic test execution.

10. **TDD Workflow**: All GitHub repository functionality shall be implemented using strict Test-Driven Development:
    - Write failing tests first for each piece of functionality
    - Implement minimal code to make tests pass
    - Refactor while maintaining test coverage
    - No implementation code shall be written without corresponding tests

11. **Code Organization**: New GitHub-related functionality shall be added to `slash_commands/github_utils.py` following existing code patterns and conventions.

12. **Metadata Source Tracking**: The `_build_meta()` method in `MarkdownCommandGenerator` shall be updated to include source tracking metadata:
    - For local prompts: Add `source_type: "local"` and `source_dir: <prompts_dir_path>` to metadata
    - For GitHub prompts: Add `source_type: "github"`, `source_repo: <owner/repo>`, `source_branch: <branch>`, and `source_path: <path>` to metadata
    - Source metadata shall be included in all generated command files regardless of format (markdown or TOML)

13. **Documentation Updates**: README.md shall be updated with GitHub usage examples in the "Usage" section, including:
    - Basic GitHub repository example (directory path): `uv run slash-man generate --github-repo liatrio-labs/spec-driven-workflow --github-branch main --github-path prompts --agent claude-code --target-path /tmp/test-output`
    - Single file path example: `uv run slash-man generate --github-repo liatrio-labs/spec-driven-workflow --github-branch refactor/improve-workflow --github-path prompts/generate-spec.md --agent claude-code --target-path /tmp/test-output`
    - Branch with slash notation example: `uv run slash-man generate --github-repo liatrio-labs/spec-driven-workflow --github-branch refactor/improve-workflow --github-path prompts --agent claude-code --target-path /tmp/test-output`
    - Nested path example (if applicable)
    - Error handling examples
    - All examples shall include `--target-path` flag to avoid polluting user configs

14. **CI Help Flag Testing**: CI workflows shall include tests that verify `--help` flag functionality:
    - Test `uv run slash-man --help` exits successfully and shows main command help
    - Test `uv run slash-man generate --help` exits successfully and shows generate subcommand help
    - Test `uv run slash-man cleanup --help` exits successfully and shows cleanup subcommand help
    - These tests ensure CLI help output is properly generated and formatted

15. **CI Compatibility Audit**: Existing CI workflows (.github/workflows/*.yml) shall be audited to ensure:
    - Current test runners continue to work with new GitHub functionality
    - No breaking changes to existing CI processes
    - New GitHub-related tests integrate seamlessly with existing test suites
    - Documentation builds continue to pass with new examples
    - Help flag tests are integrated into CI workflow

## Success Metrics

1. **Functional correctness**: All three GitHub flags work together to successfully download and load prompts from public GitHub repositories

2. **Validation accuracy**: 100% of invalid repository formats are caught with clear error messages including examples

3. **Error handling**: All GitHub API error scenarios (404, 403, network errors) produce clear, actionable error messages

4. **Test coverage**: Comprehensive test coverage for all GitHub functionality including flag validation, GitHub API integration, error handling, mutual exclusivity scenarios, prompt metadata source tracking, and documentation examples

5. **User experience**: CLI help output clearly documents the three required flags and their format requirements, including that `--github-path` can point to either a directory or a single file

6. **Code maintainability**: Implementation adds less than 300 lines of code and follows existing codebase patterns

7. **Documentation completeness**: README.md includes comprehensive GitHub examples that are tested and validated

8. **CI compatibility**: Existing CI workflows continue to pass without modification, confirming no breaking changes to the testing infrastructure

9. **Metadata source tracking**: 100% of generated command files include accurate source metadata (local directory path or GitHub repository details) in their metadata fields

10. **Help flag testing**: CI workflows successfully test `--help` flag for main command and all subcommands, ensuring help output is properly generated

## Open Questions

No open questions at this time.
