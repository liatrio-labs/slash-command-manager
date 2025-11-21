# 08-spec-list-all-files-flag

## Introduction/Overview

This feature adds a `--all-files` flag to the existing `list` command that displays all files found in agent command directories, regardless of their managed status. When this flag is used, the output replaces the standard managed prompts tree with a comprehensive file listing organized by agent. Files are classified as "managed", "unmanaged", "backup", or "other" and displayed in a table format with color coding (green for managed files with `managed_by` metadata, red for unmanaged/other files, regular text for backups). This provides users with complete visibility into their agent command directories for debugging, auditing, and cleanup purposes.

## Goals

- Add `--all-files` flag to the `list` command that lists all files in agent command directories.
- Display files in a table format organized by agent, with summary information for each agent directory.
- Classify files by type (managed/unmanaged/backup/other) with appropriate color coding.
- Show file paths relative to the `--target-path` directory for clarity.
- Respect all existing `list` command flags (`--agent`, `--target-path`, `--detection-path`) for consistent behavior.
- Provide clear empty state handling showing directory structure and existence status.

## User Stories

- **As a developer debugging prompt issues**, I want to see all files in agent command directories so that I can identify unexpected files, malformed prompts, or missing managed files.
- **As a user auditing my agent configurations**, I want a complete view of all files in each agent directory so that I can understand what's installed and identify files that need attention.
- **As a user cleaning up old or unused files**, I want to see all files categorized by type so that I can easily identify which files are managed, unmanaged, backups, or other files that may need removal.
- **As a user troubleshooting detection issues**, I want to see the directory structure and file counts for each agent so that I can verify directories exist and understand what files are present.

## Demoable Units of Work

### [Unit 1]: File Discovery and Classification

**Purpose:** Implement logic to discover all files in agent command directories and classify them by type (managed, unmanaged, backup, other).

**Functional Requirements:**

- The system shall scan all files in each agent's command directory (matching `command_file_extension` pattern).
- The system shall classify files as "managed" if they contain `meta.managed_by == "slash-man"` metadata.
- The system shall classify files as "backup" if they match the backup pattern `*.{extension}.{timestamp}.bak`.
- The system shall classify files as "unmanaged" if they are valid prompt files (parseable) but lack `managed_by` metadata.
- The system shall classify files as "other" if they don't match any of the above categories (invalid prompts, wrong format, etc.).
- The system shall handle parsing errors gracefully, classifying unparseable files as "other".

**Proof Artifacts:**

- Unit tests: Test file classification logic with various file types (managed, unmanaged, backup, invalid, etc.)
- Integration test: Verify classification across multiple agents with mixed file types
- CLI transcript: `slash-man list --all-files` showing files correctly classified

### [Unit 2]: Table Output Format

**Purpose:** Display files in a Rich table format organized by agent, with summary information and proper color coding.

**Functional Requirements:**

- The system shall display a separate table for each agent directory.
- The system shall show summary information above each table including: agent display name, agent key, command directory path (relative to target-path), total file count, and breakdown by type.
- The system shall display files in a table with columns: "Type" and "File Path".
- The system shall sort files first by type (managed, unmanaged, backup, other), then alphabetically by filename.
- The system shall color code files: green for managed files, red for unmanaged/other files, default (regular) text for backup files.
- The system shall display file paths relative to the `--target-path` directory.

**Proof Artifacts:**

- Unit tests: Test table building logic and sorting behavior
- Integration test: Verify table output structure and formatting
- CLI transcript: `slash-man list --all-files` showing formatted tables with color coding

### [Unit 3]: Flag Integration and Output Replacement

**Purpose:** Integrate `--all-files` flag with existing `list` command, replacing standard output when flag is used.

**Functional Requirements:**

- The system shall add `--all-files` flag to the `list` command.
- The system shall replace the standard managed prompts tree output entirely when `--all-files` flag is used.
- The system shall respect all existing `list` command flags (`--agent`, `--target-path`, `--detection-path`).
- The system shall use the same agent detection logic as the standard `list` command.
- The system shall exit with code 0 when no files are found (empty state).

**Proof Artifacts:**

- Unit tests: Test flag parsing and conditional output logic
- Integration tests: Verify flag combinations work correctly (`--all-files --agent cursor`, `--all-files --target-path /custom/path`, etc.)
- CLI transcript: `slash-man list --all-files --help` showing flag documentation

### [Unit 4]: Empty State and Directory Handling

**Purpose:** Provide clear feedback when directories are empty or don't exist, showing directory structure information.

**Functional Requirements:**

- The system shall display directory information for each agent even when no files are found.
- The system shall indicate whether each agent's command directory exists or doesn't exist.
- The system shall show the expected directory path (relative to target-path) for each agent.
- The system shall display a message indicating "No files found" when directory exists but is empty.
- The system shall display a message indicating "Directory does not exist" when the directory path doesn't exist.

**Proof Artifacts:**

- Unit tests: Test empty state handling logic
- Integration test: Verify empty directory and non-existent directory scenarios
- CLI transcript: `slash-man list --all-files` showing empty state output

## Non-Goals (Out of Scope)

1. **Source prompt directory listing**: This feature only lists files in agent command directories (where generated files are stored), not source prompt directories.
2. **File content display**: The feature shows file paths and types only, not file contents or metadata details.
3. **Interactive file management**: This is a read-only listing feature; it does not provide commands to delete, move, or modify files.
4. **Pagination or limiting**: All files are displayed without pagination or limits (per user requirements).
5. **File modification timestamps**: File modification times are not displayed in the table output.
6. **Backup file details**: Individual backup files are listed but detailed backup information (like which file they backup) is not shown.

## Design Considerations

The output will use Rich library tables for consistent formatting with the rest of the CLI. Each agent will have its own table with a summary panel above it showing:

- Agent display name and key
- Command directory path (relative to target-path)
- Total file count
- Count breakdown by type (managed: X, unmanaged: Y, backup: Z, other: W)

Files will be displayed in a two-column table:

- **Type column**: Shows classification (managed/unmanaged/backup/other) with appropriate color
- **File Path column**: Shows relative path from target-path

Color scheme:

- **Green**: Files with `managed_by: slash-man` metadata (managed files)
- **Red**: Files without `managed_by` metadata (unmanaged and other files)
- **Default/Regular**: Backup files (matching backup pattern)

## Repository Standards

- **Coding Standards**: Follow PEP 8 style guidelines, use `ruff` for linting and formatting, maximum line length 100 characters, type hints encouraged.
- **Testing Patterns**: Write unit tests in `tests/test_list_discovery.py` and integration tests in `tests/integration/test_list_command.py`, follow existing pytest patterns with fixtures from `conftest.py`, use TDD workflow (write tests first).
- **Quality Gates**: All tests must pass, pre-commit hooks must pass (`ruff check`, `ruff format`), ensure test coverage for new functionality.
- **Commit Standards**: Use Conventional Commits format (e.g., `feat(list): add --all-files flag`).
- **Code Organization**: Reuse existing patterns from `list_discovery.py`, extract shared functionality following DRY principles, maintain consistency with existing `list` command structure.

## Technical Considerations

- **File Discovery**: Reuse existing `discover_managed_prompts()` logic but extend it to discover ALL files, not just managed ones. May need new function `discover_all_files()` that doesn't filter by `managed_by`.
- **File Classification**: Parse files using existing `_parse_command_file()` logic to determine if they're valid prompts and check for `managed_by` metadata. Handle parsing errors gracefully.
- **Backup Detection**: Reuse existing `_is_backup_file()` function to identify backup files.
- **Output Format**: Use Rich `Table` and `Panel` components similar to existing `render_list_tree()` but with different structure. May need new function `render_all_files_tables()`.
- **Path Resolution**: Use existing `cli_utils.py` utilities for path resolution and relative path display.
- **Agent Detection**: Reuse existing `detect_agents()` and agent filtering logic from `list_cmd()` function.
- **Error Handling**: Follow existing patterns for handling file read errors, permission errors, and malformed files (skip silently or classify as "other").

## Success Metrics

1. **Functionality**: `--all-files` flag successfully lists all files in agent command directories with correct classification.
2. **Accuracy**: File classification is 100% accurate (managed files correctly identified, backups correctly identified, unmanaged files correctly identified).
3. **Performance**: Command completes in reasonable time even with many files (no pagination needed per requirements).
4. **User Experience**: Output is clear and easy to read with proper color coding and organization.
5. **Test Coverage**: All new functionality has unit and integration tests with 100% coverage of new code paths.

## Open Questions

No open questions at this time. All requirements have been clarified through the questions process.
