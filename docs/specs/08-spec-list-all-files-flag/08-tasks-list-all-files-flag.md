# 08 Tasks - List All Files Flag

## Relevant Files

- `slash_commands/list_discovery.py` - Contains file discovery and classification logic. Will add `discover_all_files()` function and `classify_file_type()` helper function. Also contains rendering functions, will add `render_all_files_tables()` function.
- `tests/test_list_discovery.py` - Unit tests for list discovery functions. Will add tests for file discovery, classification, and table rendering.
- `slash_commands/cli.py` - Contains the `list_cmd()` function. Will add `--all-files` flag parameter and conditional logic to call new rendering function.
- `tests/integration/test_list_command.py` - Integration tests for list command. Will add tests for `--all-files` flag integration and flag combinations.

### Notes

- Follow TDD workflow: write failing tests first, then implement minimal code to pass, iterate.
- Reuse existing patterns from `list_discovery.py` (e.g., `_parse_command_file()`, `_is_backup_file()`).
- Use Rich library `Table` and `Panel` components similar to existing `render_list_tree()` function.
- Use `cli_utils.py` utilities (`relative_to_candidates()`) for path resolution.
- Follow existing error handling patterns (skip malformed files silently, classify as "other").
- All new functions should have type hints and docstrings following PEP 8 style.
- Maximum line length is 100 characters (enforced by ruff).

## Tasks

### [x] 1.0 File Discovery and Classification

#### 1.0 Proof Artifact(s)

- Test: `test_discover_all_files_classifies_managed_files()` passes demonstrates managed file classification works
- Test: `test_discover_all_files_classifies_unmanaged_files()` passes demonstrates unmanaged file classification works
- Test: `test_discover_all_files_classifies_backup_files()` passes demonstrates backup file classification works
- Test: `test_discover_all_files_classifies_other_files()` passes demonstrates invalid/malformed files are classified as "other"
- CLI: `slash-man list --all-files` shows files correctly classified by type demonstrates end-to-end file discovery and classification

#### 1.0 Tasks

- [x] 1.1 Write failing test `test_discover_all_files_finds_all_matching_files()` in `tests/test_list_discovery.py` that verifies `discover_all_files()` finds all files matching `command_file_extension` pattern (not just managed ones)
- [x] 1.2 Write failing test `test_discover_all_files_classifies_managed_files()` that verifies files with `meta.managed_by == "slash-man"` are classified as "managed"
- [x] 1.3 Write failing test `test_discover_all_files_classifies_unmanaged_files()` that verifies valid prompt files without `managed_by` metadata are classified as "unmanaged"
- [x] 1.4 Write failing test `test_discover_all_files_classifies_backup_files()` that verifies files matching backup pattern `*.{extension}.{timestamp}.bak` are classified as "backup"
- [x] 1.5 Write failing test `test_discover_all_files_classifies_other_files()` that verifies invalid/malformed files are classified as "other"
- [x] 1.6 Write failing test `test_discover_all_files_handles_parsing_errors()` that verifies parsing errors are handled gracefully (files classified as "other")
- [x] 1.7 Implement `classify_file_type()` helper function in `slash_commands/list_discovery.py` that takes a file path and agent config, returns classification string ("managed", "unmanaged", "backup", "other"). Reuse `_parse_command_file()` and `_is_backup_file()` functions
- [x] 1.8 Implement `discover_all_files()` function in `slash_commands/list_discovery.py` that scans all files matching `command_file_extension` pattern for each agent, calls `classify_file_type()` for each file, returns list of dicts with structure: `{"file_path": Path, "type": str, "agent": str, "agent_display_name": str}`
- [x] 1.9 Run tests and verify all classification tests pass
- [x] 1.10 Run `ruff check` and `ruff format` to ensure code quality

### [x] 2.0 Table Output Format

#### 2.0 Proof Artifact(s)

- Test: `test_render_all_files_tables_creates_correct_structure()` passes demonstrates table structure is correct
- Test: `test_render_all_files_tables_sorts_files_correctly()` passes demonstrates files are sorted by type then alphabetically
- Test: `test_render_all_files_tables_applies_color_coding()` passes demonstrates color coding (green/red/default) is applied correctly
- CLI: `slash-man list --all-files` shows formatted tables with summary panels demonstrates Rich table output with proper formatting

#### 2.0 Tasks

- [x] 2.1 Write failing test `test_render_all_files_tables_creates_correct_structure()` in `tests/test_list_discovery.py` that verifies `render_all_files_tables()` creates Rich Table with "Type" and "File Path" columns
- [x] 2.2 Write failing test `test_render_all_files_tables_sorts_files_correctly()` that verifies files are sorted first by type (managed, unmanaged, backup, other), then alphabetically by filename
- [x] 2.3 Write failing test `test_render_all_files_tables_applies_color_coding()` that verifies managed files are green, unmanaged/other files are red, backup files use default color
- [x] 2.4 Write failing test `test_render_all_files_tables_shows_summary_panel()` that verifies summary panel shows agent display name, agent key, command directory path (relative to target-path), total file count, and breakdown by type
- [x] 2.5 Write failing test `test_render_all_files_tables_shows_relative_paths()` that verifies file paths are displayed relative to target-path using `relative_to_candidates()` utility
- [x] 2.6 Implement `_build_agent_summary_panel()` helper function in `slash_commands/list_discovery.py` that creates Rich Panel with agent info and file counts. Takes agent config, file list, and target_path, returns Panel
- [x] 2.7 Implement `_build_agent_file_table()` helper function that creates Rich Table for a single agent's files. Takes file list, target_path, returns Table with proper sorting and color coding
- [x] 2.8 Implement `render_all_files_tables()` function in `slash_commands/list_discovery.py` that takes discovered files dict (grouped by agent), target_path, and optional `record` parameter. Creates summary panel and table for each agent, prints them using Rich Console
- [x] 2.9 Run tests and verify all table rendering tests pass
- [x] 2.10 Run `ruff check` and `ruff format` to ensure code quality

### [x] 3.0 Flag Integration and Output Replacement

#### 3.0 Proof Artifact(s)

- Test: `test_list_cmd_with_all_files_flag()` passes demonstrates flag parsing works correctly
- Test: `test_list_cmd_all_files_respects_existing_flags()` passes demonstrates `--agent`, `--target-path`, `--detection-path` work with `--all-files`
- CLI: `slash-man list --all-files --help` shows flag documentation demonstrates flag is properly integrated
- CLI: `slash-man list --all-files --agent cursor` shows only cursor files demonstrates agent filtering works
- CLI: `slash-man list --all-files` replaces standard tree output demonstrates output replacement works

#### 3.0 Tasks

- [x] 3.1 Write failing test `test_list_cmd_with_all_files_flag()` in `tests/integration/test_list_command.py` that verifies `slash-man list --all-files` executes successfully and shows table output instead of tree output
- [x] 3.2 Write failing test `test_list_cmd_all_files_respects_agent_flag()` that verifies `slash-man list --all-files --agent cursor` shows only cursor files
- [x] 3.3 Write failing test `test_list_cmd_all_files_respects_target_path_flag()` that verifies `--target-path` flag works with `--all-files`
- [x] 3.4 Write failing test `test_list_cmd_all_files_respects_detection_path_flag()` that verifies `--detection-path` flag works with `--all-files`
- [x] 3.5 Add `all_files` parameter to `list_cmd()` function in `slash_commands/cli.py` using `typer.Option("--all-files", help="List all files in agent command directories, not just managed prompts")`
- [x] 3.6 Add conditional logic in `list_cmd()` to call `discover_all_files()` and `render_all_files_tables()` when `all_files` flag is True, otherwise use existing `discover_managed_prompts()` and `render_list_tree()` logic
- [x] 3.7 Ensure agent detection logic (using `detect_agents()` and filtering) works the same way for both standard and `--all-files` modes
- [x] 3.8 Run integration tests and verify all flag combination tests pass
- [x] 3.9 Test CLI help output: `slash-man list --help` should show `--all-files` flag documentation
- [x] 3.10 Run `ruff check` and `ruff format` to ensure code quality

### [x] 4.0 Empty State and Directory Handling

#### 4.0 Proof Artifact(s)

- Test: `test_render_all_files_tables_handles_empty_directory()` passes demonstrates empty directory shows appropriate message
- Test: `test_render_all_files_tables_handles_missing_directory()` passes demonstrates missing directory shows appropriate message
- CLI: `slash-man list --all-files` with empty directories shows directory info and "No files found" demonstrates empty state handling works
- CLI: `slash-man list --all-files` with missing directories shows "Directory does not exist" demonstrates missing directory handling works

#### 4.0 Tasks

- [x] 4.1 Write failing test `test_render_all_files_tables_handles_empty_directory()` in `tests/test_list_discovery.py` that verifies when directory exists but is empty, shows summary panel with "No files found" message
- [x] 4.2 Write failing test `test_render_all_files_tables_handles_missing_directory()` that verifies when directory doesn't exist, shows summary panel with "Directory does not exist" message and expected path
- [x] 4.3 Write failing test `test_render_all_files_tables_shows_directory_info_for_all_agents()` that verifies directory information is shown for each agent even when no files are found
- [x] 4.4 Modify `discover_all_files()` function to return directory existence status. Update return structure to include `{"directory_exists": bool}` for each agent
- [x] 4.5 Modify `render_all_files_tables()` function to handle empty file lists. When files list is empty, show summary panel with appropriate message ("No files found" if directory exists, "Directory does not exist" if missing)
- [x] 4.6 Ensure empty state handling works correctly when `--all-files` flag is used with empty or missing directories. Command should exit with code 0 (success, not error)
- [x] 4.7 Run tests and verify all empty state tests pass
- [x] 4.8 Test CLI output: `slash-man list --all-files` with empty directories should show directory info and appropriate messages
- [x] 4.9 Run `ruff check` and `ruff format` to ensure code quality
- [x] 4.10 Run full test suite (`pytest tests/`) to ensure no regressions
