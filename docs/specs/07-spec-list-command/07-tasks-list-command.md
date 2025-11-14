# 07-tasks-list-command

## Tasks

> **Execution Note:** Run every manual demo, CLI proof, and artifact capture inside the project's Docker test container (e.g., `docker run --rm slash-man-test …`) so local files remain untouched.

### Testing Notes

**GitHub Source Testing:** When testing GitHub source functionality, use the following command to generate prompts from a remote repository:

```bash
slash-man generate \
  --github-repo liatrio-labs/spec-driven-workflow \
  --github-branch main \
  --github-path prompts
```

This command should be used whenever GitHub source metadata display or handling needs to be verified.

## Relevant Files

- `slash_commands/generators.py` - Contains `MarkdownCommandGenerator._build_meta()` and `TomlCommandGenerator.generate()` methods that need `managed_by: slash-man` field added to metadata
- `tests/test_generators.py` - Unit tests for generators; add tests verifying `managed_by` field is included
- `tests/integration/test_generate_command.py` - Integration tests for generate command; add test verifying generated files contain `managed_by` field
- `slash_commands/list_discovery.py` - New file containing prompt discovery logic, backup counting, source metadata extraction, and unmanaged prompt detection
- `tests/test_list_discovery.py` - New file containing unit tests for list discovery logic
- `slash_commands/cli.py` - CLI entry point; add `list` command with flags (`--agent`, `--target-path`, `--detection-path`) and empty state handling
- `tests/integration/test_list_command.py` - New file containing integration tests for list command
- `slash_commands/cli_utils.py` - New file containing shared utilities extracted from `generate` and `list` commands (agent detection/validation, path resolution, Rich rendering, frontmatter/TOML parsing, source metadata formatting)
- `tests/test_cli_utils.py` - New file containing unit tests for shared CLI utilities
- `mcp_server/prompt_utils.py` - Contains `parse_frontmatter()` function; may need to extend for TOML parsing utilities

### Notes

- Unit tests should typically be placed alongside the code files they are testing (e.g., `list_discovery.py` and `test_list_discovery.py` in the same directory)
- Integration tests should be placed in `tests/integration/` directory following existing patterns
- Use the repository's established testing command: `pytest [path]` or `pytest tests/`
- Follow the repository's existing code organization, naming conventions, and style guidelines (enforced by `ruff format` and `ruff check`)
- Adhere to identified quality gates and pre-commit hooks (`pre-commit run --all-files`)
- Execute implementation with strict TDD workflow: write failing tests first, implement only enough code to make them pass, iterate until all acceptance criteria are covered, and refactor while keeping tests green

### [x] 1.0 Add `managed_by: slash-man` Metadata Field to Generated Command Files

#### 1.0 Demo Criteria

- Run `slash-man generate` to create a command file (test with both local and GitHub sources)
- For GitHub sources, use the GitHub source testing command (see Testing Notes above)
- Verify the generated file contains `managed_by: slash-man` in the `meta` section of frontmatter (Markdown) or TOML structure
- Confirm both Markdown and TOML format generators include the field
- Verify existing metadata fields are preserved

#### 1.0 Proof Artifact(s)

- Unit test: `test_build_meta_includes_managed_by()` verifying `MarkdownCommandGenerator._build_meta()` includes `managed_by: slash-man`
- Unit test: `test_toml_generator_includes_managed_by()` verifying `TomlCommandGenerator.generate()` includes `managed_by: slash-man` in meta section
- Integration test: `test_generate_creates_managed_by_field()` confirming generated files contain the metadata
- CLI transcript: `cat` output showing `managed_by: slash-man` in generated file's frontmatter/TOML

#### 1.0 Tasks

- [x] 1.1 Write failing unit test `test_build_meta_includes_managed_by()` in `tests/test_generators.py` that verifies `MarkdownCommandGenerator._build_meta()` includes `managed_by: slash-man` in returned metadata dict
- [x] 1.2 Modify `MarkdownCommandGenerator._build_meta()` in `slash_commands/generators.py` to add `managed_by: slash-man` to the metadata dict before returning it
- [x] 1.3 Run test to verify it passes, then commit with message: `feat(generators): add managed_by field to Markdown generator metadata`
- [x] 1.4 Write failing unit test `test_toml_generator_includes_managed_by()` in `tests/test_generators.py` that verifies `TomlCommandGenerator.generate()` includes `managed_by: slash-man` in the `meta` section of generated TOML
- [x] 1.5 Modify `TomlCommandGenerator.generate()` in `slash_commands/generators.py` to add `managed_by: slash-man` to the `meta` dict before converting to TOML
- [x] 1.6 Run test to verify it passes, then commit with message: `feat(generators): add managed_by field to TOML generator metadata`
- [x] 1.7 Write failing integration test `test_generate_creates_managed_by_field()` in `tests/integration/test_generate_command.py` that runs `slash-man generate` and verifies generated files contain `managed_by: slash-man` in metadata (test both Markdown and TOML formats)
- [x] 1.8 Run integration test to verify it passes, then commit with message: `test(integration): verify generate command creates managed_by field`
- [x] 1.9 Verify existing metadata fields are preserved by running existing generator tests and confirming no regressions
- [x] 1.10 Create CLI transcript proof artifact: run `slash-man generate` with test prompts, then `cat` generated file to show `managed_by: slash-man` in frontmatter/TOML

### [x] 2.0 Implement Prompt Discovery and Filtering Logic

#### 2.0 Demo Criteria

- Run `slash-man list` and verify it discovers all managed prompts across detected agent locations
- Confirm command files without `managed_by` field are excluded from managed results
- Verify files without `managed_by` field are counted as unmanaged if they are valid prompt files
- Confirm both Markdown and TOML format files are handled correctly
- Verify backup files are excluded from discovery and unmanaged counts
- Test discovery across multiple agent directories

#### 2.0 Proof Artifact(s)

- Unit tests for prompt discovery logic covering:
  - Files with `managed_by: slash-man` are discovered
  - Files without `managed_by` field are excluded from managed results
  - Valid prompt files without `managed_by` are counted as unmanaged
  - Backup files are excluded from both managed and unmanaged counts
  - Markdown frontmatter parsing works correctly
  - TOML parsing works correctly
  - Empty directories are handled gracefully
  - Multiple agents are discovered correctly
- Unit tests for unmanaged prompt detection logic
- Unit tests for error handling scenarios (malformed frontmatter, permission errors, Unicode errors)
- Integration test: `test_list_discovers_managed_prompts()` verifying discovery across multiple agent directories
- CLI transcript showing discovery working correctly

#### 2.0 Tasks

- [x] 2.1 Create new file `slash_commands/list_discovery.py` with function `discover_managed_prompts(base_path: Path, agents: list[str]) -> list[dict[str, Any]]` that takes base_path and agents list, and returns list of dicts with prompt metadata. Each dict should contain: `name` (str), `agent` (str), `agent_display_name` (str), `file_path` (Path), `meta` (dict), `format` (str). Function signature: `def discover_managed_prompts(base_path: Path, agents: list[str]) -> list[dict[str, Any]]:`
- [x] 2.2 Write failing unit test `test_discover_managed_prompts_finds_files_with_managed_by()` in `tests/test_list_discovery.py` that verifies files with `managed_by: slash-man` are discovered
- [x] 2.3 Implement `discover_managed_prompts()` to scan agent command directories, parse frontmatter/TOML, and filter for files with `meta.managed_by == "slash-man"`
- [x] 2.4 Run test to verify it passes, then commit with message: `feat(list): implement managed prompt discovery`
- [x] 2.5 Write failing unit test `test_discover_managed_prompts_excludes_files_without_managed_by()` verifying files without `managed_by` field are excluded from managed results
- [x] 2.6 Update `discover_managed_prompts()` to exclude files without `managed_by` field, run test to verify it passes
- [x] 2.7 Write failing unit test `test_discover_managed_prompts_handles_markdown_format()` and `test_discover_managed_prompts_handles_toml_format()` verifying both formats are handled correctly
- [x] 2.8 Update discovery logic to handle both Markdown (using `parse_frontmatter()`) and TOML (using `tomllib`) formats. Handle parsing errors gracefully: catch `yaml.YAMLError` and `tomllib.TOMLDecodeError`, skip malformed files silently (per spec assumption), run tests to verify they pass
- [x] 2.9 Write failing unit test `test_discover_managed_prompts_excludes_backup_files()` verifying backup files matching pattern `*.{extension}.{timestamp}.bak` (e.g., `command.md.20250115-123456.bak`) are excluded
- [x] 2.10 Update discovery logic to exclude backup files, run test to verify it passes, then commit with message: `feat(list): exclude backup files from discovery`
- [x] 2.11 Write failing unit test `test_discover_managed_prompts_handles_empty_directories()` verifying empty directories are handled gracefully
- [x] 2.12 Update discovery logic to handle empty directories, run test to verify it passes
- [x] 2.13 Write failing unit test `test_discover_managed_prompts_handles_multiple_agents()` verifying multiple agents are discovered correctly
- [x] 2.14 Update discovery logic to handle multiple agents, run test to verify it passes, then commit with message: `feat(list): support multiple agent discovery`
- [x] 2.15 Create function `count_unmanaged_prompts()` in `slash_commands/list_discovery.py` that counts valid prompt files without `managed_by` field
- [x] 2.16 Write failing unit tests for unmanaged prompt detection:
  - `test_count_unmanaged_prompts_counts_valid_prompts_without_managed_by()` - counts valid prompt files without `managed_by`
  - `test_count_unmanaged_prompts_excludes_backup_files()` - excludes backup files
  - `test_count_unmanaged_prompts_excludes_managed_files()` - excludes managed files
  - `test_count_unmanaged_prompts_excludes_invalid_files()` - excludes files that aren't valid prompts
- [x] 2.17 Implement `count_unmanaged_prompts()` logic: scan files matching agent's `command_file_extension`, exclude backups (matching pattern `*.{extension}.{timestamp}.bak`) and managed files, attempt to parse remaining files, count only valid prompt files. Handle parsing errors gracefully (skip malformed files silently per spec assumption)
- [x] 2.18 Run tests to verify they pass, then commit with message: `feat(list): implement unmanaged prompt counting`
- [x] 2.19 Write failing integration test `test_list_discovers_managed_prompts()` in `tests/integration/test_list_command.py` that creates managed prompts across multiple agent directories and verifies discovery works
- [x] 2.20 Run integration test to verify it passes, then commit with message: `test(integration): verify list discovers managed prompts across agents`
- [x] 2.21 Write failing unit tests for error handling scenarios:
  - `test_discover_managed_prompts_handles_malformed_frontmatter()` - skips files with malformed frontmatter silently (per spec assumption)
  - `test_discover_managed_prompts_handles_permission_errors()` - handles permission errors gracefully (skip inaccessible files)
  - `test_discover_managed_prompts_handles_unicode_errors()` - handles Unicode decode errors gracefully
- [x] 2.22 Implement error handling in discovery logic: catch parsing errors, permission errors, and Unicode errors, skip problematic files silently (log warnings in debug mode per spec), run tests to verify they pass
- [x] 2.23 Commit with message: `feat(list): add error handling for malformed files and permission errors`
- [ ] 2.24 Create CLI transcript proof artifact: run `slash-man list` and show discovery working correctly
  - **Note:** This task depends on Task 5.0 (CLI command implementation). Cannot be completed until `list` command is implemented.

### [x] 3.0 Implement Backup Counting and Source Metadata Extraction

#### 3.0 Demo Criteria

- Run `slash-man list` and verify accurate backup counts are shown for each prompt file
- Create additional backups and re-run list to verify updated counts
- Verify source information is consolidated into a single display line:
  - Local sources show path (e.g., "local: /path/to/prompts")
  - GitHub sources show format (e.g., "github: owner/repo@branch:path")
- Test GitHub source display by generating prompts from GitHub using the GitHub source testing command (see Testing Notes above), then run `slash-man list` and verify GitHub source information is displayed correctly
- Verify missing source fields are handled gracefully

#### 3.0 Proof Artifact(s)

- Unit tests for backup counting logic:
  - Counts backups matching pattern `{filename}.{extension}.{timestamp}.bak` (e.g., `command.md.20250115-123456.bak`) - matches actual backup creation pattern from `writer.py`
  - Handles files with no backups (count = 0)
  - Handles files with multiple backups
- Unit tests for source metadata consolidation:
  - Local source formatting
  - GitHub source formatting
  - Missing field handling
- Integration test: `test_list_shows_backup_counts()` creating backups and verifying counts
- Integration test: `test_list_shows_source_info()` verifying source information display (test both local and GitHub sources)
- CLI transcript showing backup counts and source information in output
- CLI transcript showing GitHub source display after generating from GitHub source testing command (see Testing Notes above)

#### 3.0 Tasks

- [x] 3.1 Create function `count_backups(file_path: Path) -> int` in `slash_commands/list_discovery.py` that takes a file path and returns count of backup files matching pattern `{filename}.{extension}.{timestamp}.bak` (e.g., `command.md.20250115-123456.bak`). This matches the actual backup creation pattern from `writer.py` line 105: `backup_path = file_path.with_suffix(f"{file_path.suffix}.{timestamp}.bak")`
- [x] 3.2 Write failing unit tests for backup counting:
  - `test_count_backups_returns_zero_for_no_backups()` - handles files with no backups
  - `test_count_backups_counts_matching_backups()` - counts backups matching pattern `{filename}.{extension}.{timestamp}.bak` (e.g., `command.md.20250115-123456.bak`)
  - `test_count_backups_handles_multiple_backups()` - handles files with multiple backups
  - `test_count_backups_excludes_non_matching_files()` - excludes files that don't match backup pattern (e.g., `command.md.bak` without timestamp)
- [x] 3.3 Implement `count_backups()` using `Path.glob()` with pattern `{filename}.{extension}.*.bak` and validate timestamp format (`YYYYMMDD-HHMMSS`) to ensure only valid backups are counted. Use regex pattern `.*\{extension\}\.\d{8}-\d{6}\.bak$` similar to `writer.py` line 474, run tests to verify they pass
- [x] 3.4 Commit with message: `feat(list): implement backup counting logic`
- [x] 3.5 Create function `format_source_info()` in `slash_commands/list_discovery.py` that consolidates source metadata into a single display line
- [x] 3.6 Write failing unit tests for source metadata consolidation:
  - `test_format_source_info_local_source()` - formats local source as "local: /path/to/prompts" using `meta.source_dir` or `meta.source_path`
  - `test_format_source_info_github_source()` - formats GitHub source as "github: owner/repo@branch:path" using `meta.source_repo`, `meta.source_branch`, `meta.source_path`
  - `test_format_source_info_missing_fields()` - handles missing fields gracefully (shows "Unknown" or omits)
- [x] 3.7 Implement `format_source_info()` logic: check `meta.source_type`, format accordingly, handle missing fields, run tests to verify they pass
- [x] 3.8 Commit with message: `feat(list): implement source metadata consolidation`
- [x] 3.9 Write failing integration test `test_list_shows_backup_counts()` in `tests/integration/test_list_command.py` that creates backups using the same pattern as `writer.py` (e.g., `command.md.20250115-123456.bak`) and verifies counts are shown correctly
- [x] 3.10 Run integration test to verify it passes
- [x] 3.11 Write failing integration test `test_list_shows_source_info()` in `tests/integration/test_list_command.py` that generates prompts from both local and GitHub sources and verifies source information is displayed correctly
- [x] 3.12 Run integration test to verify it passes, then commit with message: `test(integration): verify backup counts and source info display`
- [x] 3.13 Create CLI transcript proof artifacts:
  - Show backup counts in output after creating backups
  - Show GitHub source display after generating from GitHub source testing command (see Testing Notes above)

### [x] 4.0 Implement Rich Output Display with Tree Structure

#### 4.0 Demo Criteria

- Run `slash-man list` and verify formatted tree structure displays all managed prompts
- Verify output is grouped by prompt name (not by agent)
- Confirm each prompt shows:
  - Agent(s) where installed (agent key and display name)
  - File path(s) for each agent
  - Backup count per file
  - Consolidated source information (single line)
  - Last updated timestamp
- Verify unmanaged prompt counts are shown per agent directory
- Confirm output style matches `generate` command summary structure

#### 4.0 Proof Artifact(s)

- Unit tests for data structure building logic:
  - Grouping prompts by name
  - Aggregating agent information per prompt
  - Building tree structure data
- Unit tests for Rich rendering logic
- Integration test: `test_list_output_structure()` verifying output format (test with both local and GitHub sources)
- CLI transcript or screenshot showing formatted tree output
- Test verifying source consolidation logic in display
- CLI transcript showing GitHub source display in tree structure after generating from GitHub source testing command (see Testing Notes above)

#### 4.0 Tasks

- [x] 4.1 Create function `build_list_data_structure(discovered_prompts: list[dict[str, Any]], unmanaged_counts: dict[str, int]) -> dict[str, Any]` in `slash_commands/list_discovery.py` that groups discovered prompts by name and aggregates agent information per prompt. Expected return structure: `{"prompts": {prompt_name: {"name": str, "agents": [{"agent": str, "display_name": str, "file_path": Path, "backup_count": int}], "source_info": str, "updated_at": str}}, "unmanaged_counts": {agent_key: int}}`. Function takes list of prompt dicts from `discover_managed_prompts()` and unmanaged counts dict, returns structured data for rendering
- [x] 4.2 Write failing unit tests for data structure building:
  - `test_build_list_data_structure_groups_by_prompt_name()` - groups prompts by name (not by agent)
  - `test_build_list_data_structure_aggregates_agent_info()` - aggregates agent information per prompt
  - `test_build_list_data_structure_includes_all_fields()` - includes agent keys, display names, file paths, backup counts, source info, timestamps
- [x] 4.3 Implement `build_list_data_structure()` to group by prompt name, aggregate agent info, include all required fields, run tests to verify they pass
- [x] 4.4 Commit with message: `feat(list): implement data structure building for list output`
- [x] 4.5 Create function `render_list_tree()` in `slash_commands/list_discovery.py` that takes data structure and renders Rich tree format similar to `generate` command summary
- [x] 4.6 Write failing unit tests for Rich rendering:
  - `test_render_list_tree_creates_tree_structure()` - creates Rich Tree with correct structure
  - `test_render_list_tree_groups_by_prompt_name()` - groups output by prompt name
  - `test_render_list_tree_shows_agent_info()` - shows agent(s) where installed
  - `test_render_list_tree_shows_file_paths()` - shows file path(s) for each agent
  - `test_render_list_tree_shows_backup_counts()` - shows backup count per file
  - `test_render_list_tree_shows_source_info()` - shows consolidated source information
  - `test_render_list_tree_shows_timestamps()` - shows last updated timestamp
  - `test_render_list_tree_shows_unmanaged_counts()` - shows unmanaged prompt counts per agent directory
- [x] 4.7 Implement `render_list_tree()` using Rich Tree structure similar to `_render_rich_summary()` in `cli.py`, run tests to verify they pass
- [x] 4.8 Commit with message: `feat(list): implement Rich tree rendering for list output`
- [x] 4.9 Write failing integration test `test_list_output_structure()` in `tests/integration/test_list_command.py` that verifies output format matches expected structure (test with both local and GitHub sources)
- [x] 4.10 Run integration test to verify it passes, then commit with message: `test(integration): verify list output structure`
- [x] 4.11 Create CLI transcript or screenshot proof artifact showing formatted tree output
- [x] 4.12 Create CLI transcript showing GitHub source display in tree structure after generating from GitHub source testing command (see Testing Notes above)

### [x] 5.0 Add `list` CLI Command with Flags and Empty State Handling

#### 5.0 Demo Criteria

- Run `slash-man list` and verify command executes successfully
- Run `slash-man list --agent cursor` and verify only Cursor prompts are shown
- Run `slash-man list --target-path /custom/path` and verify search location is modified
- Run `slash-man list --detection-path /custom/path` and verify detection location is modified
- Run `slash-man list` with no managed prompts and verify informative empty state message:
  - Clear statement that no managed prompts were found
  - Explanation that only files with `managed_by: slash-man` metadata are detected
  - Note that files generated by older versions won't appear until regenerated
  - Exit code 0 (success, not error)

#### 5.0 Proof Artifact(s)

- Integration tests for each flag combination:
  - `--agent` / `-a` flag filtering
  - `--target-path` / `-t` flag
  - `--detection-path` / `-d` flag
  - Multiple `--agent` flags
- Integration test: `test_list_empty_state()` verifying empty state message and exit code
- Unit tests for flag parsing and validation
- CLI transcript demonstrating flag usage
- CLI transcript showing empty state message

#### 5.0 Tasks

- [x] 5.1 Add `list` command function to `slash_commands/cli.py` using `@app.command()` decorator with basic structure (no flags yet)
- [x] 5.2 Write failing integration test `test_list_command_executes_successfully()` in `tests/integration/test_list_command.py` that runs `slash-man list` and verifies exit code is 0
- [x] 5.3 Implement basic `list` command that calls discovery functions and renders output, run test to verify it passes
- [x] 5.4 Commit with message: `feat(cli): add basic list command`
- [x] 5.5 Add `--agent` / `-a` flag to `list` command in `slash_commands/cli.py` (can be specified multiple times, matches `generate` command behavior)
- [x] 5.6 Write failing integration test `test_list_agent_flag_filters_results()` in `tests/integration/test_list_command.py` that runs `slash-man list --agent cursor` and verifies only Cursor prompts are shown
- [x] 5.7 Implement agent filtering logic in `list` command, run test to verify it passes
- [x] 5.8 Commit with message: `feat(cli): add --agent flag to list command`
- [x] 5.9 Add `--target-path` / `-t` flag to `list` command in `slash_commands/cli.py` (defaults to home directory, matches `generate` behavior)
- [x] 5.10 Write failing integration test `test_list_target_path_flag()` in `tests/integration/test_list_command.py` that runs `slash-man list --target-path /custom/path` and verifies search location is modified
- [x] 5.11 Implement target path logic in `list` command, run test to verify it passes
- [x] 5.12 Commit with message: `feat(cli): add --target-path flag to list command`
- [x] 5.13 Add `--detection-path` / `-d` flag to `list` command in `slash_commands/cli.py` (defaults to home directory, matches `generate` behavior)
- [x] 5.14 Write failing integration test `test_list_detection_path_flag()` in `tests/integration/test_list_command.py` that runs `slash-man list --detection-path /custom/path` and verifies detection location is modified
- [x] 5.15 Implement detection path logic in `list` command, run test to verify it passes
- [x] 5.16 Commit with message: `feat(cli): add --detection-path flag to list command`
- [x] 5.17 Write failing integration test `test_list_multiple_agent_flags()` in `tests/integration/test_list_command.py` that runs `slash-man list --agent cursor --agent claude-code` and verifies both agents are shown
- [x] 5.18 Update agent filtering logic to handle multiple `--agent` flags, run test to verify it passes
- [x] 5.19 Commit with message: `feat(cli): support multiple --agent flags in list command`
- [x] 5.20 Write failing integration test `test_list_empty_state()` in `tests/integration/test_list_command.py` that runs `slash-man list` with no managed prompts and verifies:
  - Informative empty state message is displayed
  - Message explains that only files with `managed_by: slash-man` metadata are detected
  - Message notes that files generated by older versions won't appear until regenerated
  - Exit code is 0 (success, not error)
- [x] 5.21 Implement empty state handling in `list` command: check if no managed prompts found, display informative message, exit with code 0, run test to verify it passes
- [x] 5.22 Commit with message: `feat(cli): add empty state handling to list command`
- [x] 5.23 Write unit tests for flag parsing and validation in `tests/test_cli.py` or `tests/integration/test_list_command.py`
- [x] 5.24 Run tests to verify flag parsing works correctly
- [x] 5.25 Create CLI transcript proof artifacts:
  - Demonstrate flag usage (`--agent`, `--target-path`, `--detection-path`, multiple `--agent` flags)
  - Show empty state message when no managed prompts found

### [x] 6.0 Extract Shared Utilities and Refactor for DRY Principles

#### 6.0 Demo Criteria

- Verify `generate` and `list` commands use shared utilities for:
  - Agent detection and validation
  - Path resolution and display
  - Rich rendering helpers
  - Frontmatter/TOML parsing
  - Source metadata extraction and formatting
- Confirm code duplication is reduced (at least 3 shared utilities extracted)
- Verify both commands maintain existing functionality after refactoring
- Confirm test coverage remains >90% for refactored code

#### 6.0 Proof Artifact(s)

- Code review showing extracted shared utilities:
  - Agent detection/validation utility
  - Path resolution utility
  - Rich rendering utility
  - Frontmatter/TOML parsing utility
  - Source metadata formatting utility
- Unit tests verifying shared utilities work correctly
- Integration tests confirming both commands work after refactoring
- Test coverage report showing >90% coverage
- Diff showing code reduction and consolidation

#### 6.0 Tasks

- [x] 6.1 Analyze `slash_commands/cli.py` and `slash_commands/list_discovery.py` to identify shared functionality between `generate` and `list` commands. **Note:** Some utilities (e.g., path resolution) may be needed earlier by `list` command, but can be extracted incrementally during Task 6.0 refactoring:
  - Agent detection and validation logic
  - Path resolution and display utilities (`_display_local_path()`, `_relative_to_candidates()`)
  - Rich rendering helpers (`_render_rich_summary()` patterns)
  - Frontmatter/TOML parsing utilities
  - Source metadata extraction and formatting
- [x] 6.2 Create new file `slash_commands/cli_utils.py` with shared utility functions
- [x] 6.3 Extract agent detection/validation utility function from `generate` command logic, place in `cli_utils.py`
- [x] 6.4 Write failing unit test `test_agent_detection_utility()` in `tests/test_cli_utils.py` verifying extracted utility works correctly
- [x] 6.5 Run test to verify it passes, update `generate` command to use shared utility, verify existing tests still pass
- [x] 6.6 Commit with message: `refactor(cli): extract agent detection utility`
- [x] 6.7 Extract path resolution utility functions (`_display_local_path()`, `_relative_to_candidates()`) from `cli.py` to `cli_utils.py`
- [x] 6.8 Write failing unit tests for path resolution utilities in `tests/test_cli_utils.py`
- [x] 6.9 Run tests to verify they pass, update `generate` and `list` commands to use shared utilities, verify existing tests still pass
- [x] 6.10 Commit with message: `refactor(cli): extract path resolution utilities`
- [x] 6.11 Extract Rich rendering helper functions (patterns from `_render_rich_summary()`) to `cli_utils.py`
- [x] 6.12 Write failing unit tests for Rich rendering utilities in `tests/test_cli_utils.py`
- [x] 6.13 Run tests to verify they pass, update `generate` and `list` commands to use shared utilities, verify existing tests still pass
- [x] 6.14 Commit with message: `refactor(cli): extract Rich rendering utilities`
- [x] 6.15 Extract frontmatter/TOML parsing utilities (may extend `mcp_server/prompt_utils.py` or create new utilities in `cli_utils.py`)
- [x] 6.16 Write failing unit tests for parsing utilities in `tests/test_cli_utils.py` or `tests/test_prompt_utils.py`
- [x] 6.17 Run tests to verify they pass, update `generate` and `list` commands to use shared utilities, verify existing tests still pass
- [x] 6.18 Commit with message: `refactor(cli): extract frontmatter/TOML parsing utilities`
- [x] 6.19 Extract source metadata formatting utility (`format_source_info()` or similar) to `cli_utils.py`
- [x] 6.20 Write failing unit tests for source metadata formatting utility in `tests/test_cli_utils.py`
- [x] 6.21 Run tests to verify they pass, update `generate` and `list` commands to use shared utility, verify existing tests still pass
- [x] 6.22 Commit with message: `refactor(cli): extract source metadata formatting utility`
- [x] 6.23 Run full test suite to verify both `generate` and `list` commands maintain existing functionality after refactoring
- [x] 6.24 Generate test coverage report and verify coverage remains >90% for refactored code
- [x] 6.25 Create code review diff showing extracted shared utilities and code reduction/consolidation
- [x] 6.26 Verify at least 3 shared utilities were extracted (as required by success metrics)
- [x] 6.27 Commit with message: `refactor(cli): consolidate shared utilities between generate and list commands`
