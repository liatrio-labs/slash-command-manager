# 04-tasks-github-repository-support.md

## Relevant Files

- `slash_commands/github_utils.py` - New file containing GitHub API integration functions (validate_github_repo, download_prompts_from_github, etc.). Will need imports: `requests`, `base64`, `tempfile`, `Path` from `pathlib`
- `tests/test_github_utils.py` - New file containing unit tests for GitHub utilities
- `slash_commands/cli.py` - Main CLI entry point that needs GitHub flag options added and validation logic
- `tests/test_cli.py` - CLI tests that need GitHub flag validation and mutual exclusivity tests
- `slash_commands/writer.py` - Writer class that needs GitHub prompt loading support added
- `tests/test_writer.py` - Writer tests that need GitHub prompt loading tests
- `slash_commands/generators.py` - Generator classes that need source metadata tracking added to _build_meta methods
- `tests/test_generators.py` - Generator tests that need metadata source tracking tests
- `README.md` - Documentation that needs GitHub usage examples added
- `.github/workflows/ci.yml` - CI workflow that needs --help flag tests added
- `pyproject.toml` - Package configuration that needs requests dependency added (if not already present)

### Notes

- Unit tests should be placed in the `tests/` directory following the naming pattern `test_*.py` (e.g., `test_github_utils.py` for `github_utils.py`).
- Use `uv run pytest tests/` to run tests. Running without a path executes all tests.
- Follow existing code patterns in CLI for error handling and rich output formatting.
- Use `tempfile.TemporaryDirectory()` for temporary directory management (see `tests/conftest.py` for examples).
- Mock GitHub API calls in tests using `unittest.mock` to avoid network dependencies.
- The `requests` library needs to be added to dependencies in `pyproject.toml` if not already present.
- Follow TDD workflow: write failing tests first, then implement minimal code to make tests pass.
- **GitHub API Best Practices:**
  - Use `GET /repos/{owner}/{repo}/contents/{path}?ref={branch}` endpoint (ref is a query parameter, not path parameter)
  - Set `Accept: application/vnd.github+json` header for proper API versioning
  - Handle both file and directory responses (directory returns array, file returns single object)
  - Decode base64 content from `content` field using `base64.b64decode()`
  - Use `response.raise_for_status()` for HTTP error handling
  - Handle `requests.exceptions.HTTPError` for 4xx/5xx errors
  - Handle `requests.exceptions.RequestException` for network errors
  - Check for rate limiting (403 status) and provide helpful error messages
  - For directories, recursively process subdirectories if needed (or filter for `.md` files only)

## Tasks

- [x] 1.0 GitHub Repository Flag Integration and Validation
  - Demo Criteria: Running `uv run slash-man generate --github-repo owner/repo --github-branch main --github-path prompts --agent claude-code --dry-run --target-path /tmp/test-output` successfully validates flags and shows prompts that would be downloaded. Running `uv run slash-man generate --github-repo invalid-format --target-path /tmp/test-output` shows clear error: "Repository must be in format owner/repo, got: invalid-format. Example: liatrio-labs/spec-driven-workflow"
  - Proof Artifact(s): CLI help output showing new flags (`--github-repo`, `--github-branch`, `--github-path`), successful command execution with dry-run output, error output showing validation messages, test: `test_cli_github_flags_validation()`, test: `test_validate_github_repo_invalid_format()`, test: `test_cli_github_flags_missing_required()`
  - [x] 1.1 Add `requests` dependency to `pyproject.toml` in the dependencies list (check if already present first)
  - [x] 1.2 Create `slash_commands/github_utils.py` with `validate_github_repo()` function that validates `owner/repo` format (must contain exactly one `/`) and returns tuple `(owner, repo)` or raises ValueError with helpful error message including example
  - [x] 1.3 Write test `test_validate_github_repo()` in `tests/test_cli.py` or new `tests/test_github_utils.py` that tests valid formats (e.g., "owner/repo", "liatrio-labs/spec-driven-workflow") and invalid formats (e.g., "invalid-format", "owner/repo/extra", "", "owner", "owner/")
  - [x] 1.4 Add three CLI flags to `generate()` function in `slash_commands/cli.py`: `--github-repo`, `--github-branch`, and `--github-path` using `typer.Option()` with appropriate help text. For `--github-path`, help text should indicate it can be a directory or single file (e.g., "Path to prompts directory or single prompt file within repository (e.g., 'prompts' for directory, 'prompts/my-prompt.md' for file)")
  - [x] 1.5 Add validation logic in `generate()` function that calls `validate_github_repo()` when `--github-repo` is provided, catching ValueError and printing clear error message with example before raising `typer.Exit(code=2)`
  - [x] 1.6 Add validation logic that requires all three GitHub flags (`--github-repo`, `--github-branch`, `--github-path`) to be provided together when any one is provided, raising clear error with `typer.Exit(code=2)` if any are missing
  - [x] 1.7 Write test `test_cli_github_flags_validation()` in `tests/test_cli.py` that verifies CLI help shows new flags and validates successful flag parsing
  - [x] 1.8 Write test `test_validate_github_repo_invalid_format()` in `tests/test_cli.py` that verifies invalid repository format produces clear error message
  - [x] 1.9 Write test `test_cli_github_flags_missing_required()` in `tests/test_cli.py` that verifies missing required flags produce clear error message

- [x] 2.0 GitHub and Local Directory Mutual Exclusivity
  - Demo Criteria: Running `uv run slash-man generate --prompts-dir ./prompts --github-repo owner/repo --github-branch main --github-path prompts --target-path /tmp/test-output` shows error explaining mutual exclusivity with clear message
  - Proof Artifact(s): CLI error message output, test: `test_cli_github_and_local_mutually_exclusive()`
  - [x] 2.1 Add validation logic in `generate()` function in `slash_commands/cli.py` that checks if both `--prompts-dir` and any GitHub flag (`--github-repo`, `--github-branch`, or `--github-path`) are provided simultaneously
  - [x] 2.2 When both are detected, print clear error message to stderr explaining mutual exclusivity (e.g., "Error: Cannot specify both --prompts-dir and GitHub repository flags (--github-repo, --github-branch, --github-path) simultaneously") and raise `typer.Exit(code=2)`
  - [x] 2.3 Write test `test_cli_github_and_local_mutually_exclusive()` in `tests/test_cli.py` that verifies mutual exclusivity error is raised with clear message when both are provided

- [x] 3.0 GitHub Prompt Download and Loading
  - Demo Criteria:
    - Directory path on `main` branch: `uv run slash-man generate --github-repo liatrio-labs/spec-driven-workflow --github-branch main --github-path prompts --agent claude-code --target-path /tmp/test-output` downloads prompts from directory and generates command files successfully
    - Directory path on `refactor/improve-workflow` branch: `uv run slash-man generate --github-repo liatrio-labs/spec-driven-workflow --github-branch refactor/improve-workflow --github-path prompts --agent claude-code --target-path /tmp/test-output` downloads prompts from directory and generates command files successfully
    - Single file path on `refactor/improve-workflow` branch: `uv run slash-man generate --github-repo liatrio-labs/spec-driven-workflow --github-branch refactor/improve-workflow --github-path prompts/generate-spec.md --agent claude-code --target-path /tmp/test-output` downloads single file and generates command files successfully
    - Single file path on `main` branch: `uv run slash-man generate --github-repo liatrio-labs/spec-driven-workflow --github-branch main --github-path prompts/generate-spec.md --agent claude-code --target-path /tmp/test-output` downloads single file and generates command files successfully (if file exists on main branch)
  - Proof Artifact(s): Generated command files in agent directories, CLI output showing prompts loaded, test: `test_writer_loads_prompts_from_github()`, test: `test_writer_loads_single_file_from_github()`, test: `test_github_api_error_handling()`
  - [x] 3.1 Add `download_prompts_from_github()` function to `slash_commands/github_utils.py` that takes `owner`, `repo`, `branch`, and `path` parameters, uses GitHub REST API (`GET /repos/{owner}/{repo}/contents/{path}?ref={branch}`) with `Accept: application/vnd.github+json` header, handles both file and directory responses (directory returns array, file returns single object), filters for `.md` files only in the immediate directory (do not recursively process subdirectories, matching local `glob("*.md")` behavior), decodes base64 content from `content` field using `base64.b64decode()`, and returns list of `(filename, content)` tuples. If path points to a single file, verify it has `.md` extension and return single-item list. If directory exists but contains no `.md` files, return empty list (handle gracefully, don't raise error)
  - [x] 3.2 Add error handling in `download_prompts_from_github()` using `response.raise_for_status()` and catching `requests.exceptions.HTTPError` for common GitHub API errors: 404 (repository/path not found), 403 (rate limiting/forbidden), and `requests.exceptions.RequestException` for network errors, with clear error messages following existing CLI error message patterns. Also handle case where response is not JSON (e.g., HTML error page) gracefully. If path points to a single file that does not have `.md` extension, raise ValueError with clear error message indicating the file must be a markdown file
  - [x] 3.3 Add `_download_github_prompts_to_temp_dir()` helper function in `slash_commands/github_utils.py` that takes `temp_dir: Path` parameter, calls `download_prompts_from_github()`, and writes downloaded files to the provided temp directory. This allows caller to manage the temporary directory lifecycle
  - [x] 3.4 Extend `SlashCommandWriter.__init__()` in `slash_commands/writer.py` to accept optional `github_repo`, `github_branch`, and `github_path` parameters
  - [x] 3.5 Modify `SlashCommandWriter._load_prompts()` to check if GitHub parameters are provided, and if so, use `tempfile.TemporaryDirectory()` context manager, call `_download_github_prompts_to_temp_dir()` within the context to download prompts to temporary directory, then load from temp dir using existing logic. The context manager ensures automatic cleanup of temp directory after loading completes
  - [x] 3.6 Update `generate()` function in `slash_commands/cli.py` to pass GitHub parameters (`github_repo`, `github_branch`, `github_path`) to `SlashCommandWriter` when GitHub flags are provided
  - [x] 3.7 Add error handling in CLI `generate()` function to catch GitHub API errors and print clear error messages with actionable guidance before raising `typer.Exit(code=3)` for I/O errors
  - [x] 3.8 Write test `test_writer_loads_prompts_from_github()` in `tests/test_writer.py` that mocks GitHub API calls using `unittest.mock.patch`, verifies prompts are downloaded and loaded correctly. Test should cover both `main` and `refactor/improve-workflow` branches for `liatrio-labs/spec-driven-workflow` repository with path `prompts`
  - [x] 3.9 Write test `test_github_api_error_handling()` in `tests/test_writer.py` or `tests/test_github_utils.py` that mocks various GitHub API error responses (404, 403, network errors using `requests.exceptions.RequestException`) and verifies clear error messages are produced following existing error handling patterns
  - [x] 3.10 Write test `test_github_downloads_only_markdown_files()` in `tests/test_github_utils.py` that verifies only `.md` files are downloaded and processed
  - [x] 3.11 Write test `test_github_empty_directory()` in `tests/test_github_utils.py` that verifies empty directory (no `.md` files) returns empty list without error
  - [x] 3.12 Write test `test_github_handles_subdirectories()` in `tests/test_github_utils.py` that verifies subdirectories in the GitHub path are not recursively processed (only immediate `.md` files are downloaded)
  - [x] 3.13 Write test `test_github_single_file_path()` in `tests/test_github_utils.py` that verifies when path points to a single `.md` file, it downloads and processes that file correctly
  - [x] 3.14 Write test `test_github_single_file_non_markdown()` in `tests/test_github_utils.py` that verifies when path points to a single non-`.md` file, it raises ValueError with clear error message
  - [x] 3.15 Write test `test_writer_loads_single_file_from_github()` in `tests/test_writer.py` that mocks GitHub API to return a single file response and verifies it is loaded and processed correctly. Test should cover `liatrio-labs/spec-driven-workflow` repository with path `prompts/generate-spec.md` on `refactor/improve-workflow` branch (and `main` branch if file exists)

- [x] 4.0 Prompt Metadata Source Tracking
  - Demo Criteria:
    - GitHub directory: Running `uv run slash-man generate --github-repo liatrio-labs/spec-driven-workflow --github-branch refactor/improve-workflow --github-path prompts --agent claude-code --target-path /tmp/test-output` generates command files with metadata containing `source_type: "github"`, `source_repo: "liatrio-labs/spec-driven-workflow"`, `source_branch: "refactor/improve-workflow"`, and `source_path: "prompts"`
    - GitHub single file: Running `uv run slash-man generate --github-repo liatrio-labs/spec-driven-workflow --github-branch refactor/improve-workflow --github-path prompts/generate-spec.md --agent claude-code --target-path /tmp/test-output` generates command files with metadata containing `source_type: "github"`, `source_repo: "liatrio-labs/spec-driven-workflow"`, `source_branch: "refactor/improve-workflow"`, and `source_path: "prompts/generate-spec.md"`
    - Local directory: Running with `uv run slash-man generate --prompts-dir ./prompts --target-path /tmp/test-output` generates metadata containing `source_type: "local"` and `source_dir: "./prompts"` (or absolute path)
  - Proof Artifact(s): Generated command file metadata inspection showing source tracking fields, test: `test_prompt_metadata_github_source()`, test: `test_prompt_metadata_local_source()`
  - [x] 4.1 Extend `SlashCommandWriter.__init__()` to store source information (source_type, source_dir for local, or source_repo/source_branch/source_path for GitHub) as instance attributes
  - [x] 4.2 Update `SlashCommandWriter._generate_file()` to pass source information to generator via new parameter or extend `CommandGeneratorProtocol` to accept source metadata
  - [x] 4.3 Modify `MarkdownCommandGenerator._build_meta()` in `slash_commands/generators.py` to accept source metadata parameters and add `source_type`, `source_dir` (for local), or `source_repo`, `source_branch`, `source_path` (for GitHub) to metadata dict
  - [x] 4.4 Modify `TomlCommandGenerator.generate()` in `slash_commands/generators.py` to accept source metadata parameters and add same source tracking fields to `meta` dict in TOML output
  - [x] 4.5 Update `CommandGeneratorProtocol` type hint if needed to include source metadata parameters
  - [x] 4.6 Update `SlashCommandWriter._generate_file()` to pass source metadata to generator when calling `generator.generate()`
  - [x] 4.7 Update CLI `generate()` function to determine source type and pass appropriate source metadata to `SlashCommandWriter` constructor
  - [x] 4.8 Write test `test_prompt_metadata_github_source()` in `tests/test_generators.py` that verifies generated markdown and TOML files contain correct GitHub source metadata fields
  - [x] 4.9 Write test `test_prompt_metadata_local_source()` in `tests/test_generators.py` that verifies generated markdown and TOML files contain correct local source metadata fields (`source_type: "local"`, `source_dir`)

- [x] 5.0 Documentation and CI Updates
  - Demo Criteria: README.md includes examples of GitHub flag usage with `--target-path` flag, CI workflows include `--help` flag tests for `uv run slash-man --help`, `uv run slash-man generate --help`, and `uv run slash-man cleanup --help`, and existing CI workflows continue to pass with the new changes
  - Proof Artifact(s): Updated README.md with GitHub examples, CI workflow with `--help` flag tests, CI workflow audit report showing compatibility, documentation build passes, test: `test_documentation_github_examples()`
  - [x] 5.1 Add new "GitHub Repository Support" section to README.md after "Quick Start" section with examples showing basic usage, branch with slashes, nested paths, and error handling, all including `--target-path` flag
  - [x] 5.2 Add example commands to README.md:
    - Basic GitHub repo example (directory path): `uv run slash-man generate --github-repo liatrio-labs/spec-driven-workflow --github-branch main --github-path prompts --agent claude-code --target-path /tmp/test-output`
    - Single file path example: `uv run slash-man generate --github-repo liatrio-labs/spec-driven-workflow --github-branch refactor/improve-workflow --github-path prompts/generate-spec.md --agent claude-code --target-path /tmp/test-output`
    - Branch with slash notation: `uv run slash-man generate --github-repo liatrio-labs/spec-driven-workflow --github-branch refactor/improve-workflow --github-path prompts --agent claude-code --target-path /tmp/test-output`
    - Nested path example (if applicable): `uv run slash-man generate --github-repo owner/repo --github-branch main --github-path docs/prompts/commands --agent claude-code --target-path /tmp/test-output`
    - Error handling examples (invalid repo format, missing flags, etc.)
  - [x] 5.3 Add new job `help-test` to `.github/workflows/ci.yml` that runs `uv run slash-man --help`, `uv run slash-man generate --help`, and `uv run slash-man cleanup --help` and verifies they exit successfully (exit code 0)
  - [x] 5.4 Verify existing CI jobs (`test` and `lint`) continue to pass with new GitHub functionality (run tests locally or check CI output)
  - [x] 5.5 Write test `test_documentation_github_examples()` in `tests/test_cli.py` or new `tests/test_documentation.py` that verifies example commands from README.md execute successfully (optional, can be manual verification)
