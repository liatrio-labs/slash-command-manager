# Task 2.0 Proof Artifacts: Prompt Discovery and Filtering Logic

## Test Results

### Unit Tests - All Passing

```bash
pytest tests/test_list_discovery.py -v
```

Output:

```text
============================= test session starts ==============================
platform linux -- Python 3.12.6, pytest-8.4.2, pluggy-1.5.0
collecting ... collected 14 items

tests/test_list_discovery.py::test_discover_managed_prompts_finds_files_with_managed_by PASSED [  7%]
tests/test_list_discovery.py::test_discover_managed_prompts_excludes_files_without_managed_by PASSED [ 14%]
tests/test_list_discovery.py::test_discover_managed_prompts_handles_markdown_format PASSED [ 21%]
tests/test_list_discovery.py::test_discover_managed_prompts_handles_toml_format PASSED [ 28%]
tests/test_list_discovery.py::test_discover_managed_prompts_excludes_backup_files PASSED [ 35%]
tests/test_list_discovery.py::test_discover_managed_prompts_handles_empty_directories PASSED [ 42%]
tests/test_list_discovery.py::test_discover_managed_prompts_handles_multiple_agents PASSED [ 50%]
tests/test_list_discovery.py::test_count_unmanaged_prompts_counts_valid_prompts_without_managed_by PASSED [ 57%]
tests/test_list_discovery.py::test_count_unmanaged_prompts_excludes_backup_files PASSED [ 64%]
tests/test_list_discovery.py::test_count_unmanaged_prompts_excludes_managed_files PASSED [ 71%]
tests/test_list_discovery.py::test_count_unmanaged_prompts_excludes_invalid_files PASSED [ 78%]
tests/test_list_discovery.py::test_discover_managed_prompts_handles_malformed_frontmatter PASSED [ 85%]
tests/test_list_discovery.py::test_discover_managed_prompts_handles_unicode_errors PASSED [ 92%]
tests/test_list_discovery.py::test_discover_managed_prompts_handles_permission_errors PASSED [100%]

============================== 14 passed in 0.06s ==============================
```

### Test Coverage Summary

**Discovery Logic Tests (7 tests):**

- ✅ Files with `managed_by: slash-man` are discovered
- ✅ Files without `managed_by` field are excluded from managed results
- ✅ Markdown format files are handled correctly
- ✅ TOML format files are handled correctly
- ✅ Backup files are excluded from discovery
- ✅ Empty directories are handled gracefully
- ✅ Multiple agents are discovered correctly

**Unmanaged Prompt Counting Tests (4 tests):**

- ✅ Valid prompt files without `managed_by` are counted
- ✅ Backup files are excluded from unmanaged counts
- ✅ Managed files are excluded from unmanaged counts
- ✅ Invalid files (not valid prompts) are excluded from counts

**Error Handling Tests (3 tests):**

- ✅ Malformed frontmatter is skipped silently
- ✅ Unicode decode errors are handled gracefully
- ✅ Permission errors are handled gracefully

## Function Usage Examples

### Example 1: Discover Managed Prompts

```python
from pathlib import Path
from slash_commands.list_discovery import discover_managed_prompts

# Discover managed prompts for cursor agent
base_path = Path("/home/user")
agents = ["cursor"]
result = discover_managed_prompts(base_path, agents)

# Result structure:
# [
#   {
#     "name": "command-name",
#     "agent": "cursor",
#     "agent_display_name": "Cursor",
#     "file_path": Path("/home/user/.cursor/commands/command-name.md"),
#     "meta": {"managed_by": "slash-man", ...},
#     "format": "markdown"
#   },
#   ...
# ]
```

### Example 2: Count Unmanaged Prompts

```python
from pathlib import Path
from slash_commands.list_discovery import count_unmanaged_prompts

# Count unmanaged prompts for multiple agents
base_path = Path("/home/user")
agents = ["cursor", "claude-code"]
result = count_unmanaged_prompts(base_path, agents)

# Result structure:
# {
#   "cursor": 2,      # 2 unmanaged prompts in cursor directory
#   "claude-code": 0  # 0 unmanaged prompts in claude-code directory
# }
```

## Code Implementation Verification

### Key Functions Implemented

1. **`discover_managed_prompts()`** - Scans agent command directories and discovers files with `managed_by: slash-man`
   - Supports Markdown (frontmatter) and TOML formats
   - Filters for `managed_by: slash-man` metadata
   - Excludes backup files automatically
   - Handles multiple agents

2. **`count_unmanaged_prompts()`** - Counts valid prompt files without `managed_by` field
   - Excludes backup files
   - Excludes managed files
   - Excludes invalid files (malformed prompts)
   - Returns counts per agent

3. **Error Handling** - Gracefully handles:
   - Malformed frontmatter/TOML (skipped silently)
   - Unicode decode errors (skipped silently)
   - Permission errors (skipped silently)

### File Structure

```text
slash_commands/list_discovery.py
├── discover_managed_prompts()      # Main discovery function
├── count_unmanaged_prompts()      # Unmanaged counting function
├── _is_backup_file()              # Backup file detection
├── _parse_command_file()          # File parsing dispatcher
├── _parse_markdown_file()         # Markdown frontmatter parsing
└── _parse_toml_file()             # TOML parsing
```

## Demo Validation

✅ **Demo Criteria Met (as verified by unit tests):**

1. ✅ Discovery logic finds files with `managed_by: slash-man` metadata
2. ✅ Files without `managed_by` field are excluded from managed results
3. ✅ Valid prompt files without `managed_by` are counted as unmanaged
4. ✅ Backup files are excluded from both managed and unmanaged counts
5. ✅ Both Markdown and TOML format files are handled correctly
6. ✅ Empty directories are handled gracefully
7. ✅ Multiple agents are discovered correctly
8. ✅ Error handling works for malformed files, Unicode errors, and permission errors

## Pending Proof Artifacts

The following proof artifacts require the CLI command implementation (Task 5.0):

- ⏳ **Integration Test**: `test_list_discovers_managed_prompts()` - Requires CLI command to be implemented
- ⏳ **CLI Transcript**: Running `slash-man list` and showing discovery working - Requires CLI command to be implemented

These will be completed once Task 5.0 (CLI command implementation) is finished.

## Notes

- All unit tests pass (14/14)
- Error handling follows spec assumption: errors are skipped silently (no logging in current implementation, can be added in debug mode per spec)
- Backup file detection matches the pattern from `writer.py`: `{filename}.{extension}.{timestamp}.bak`
- Both Markdown and TOML parsing reuse existing utilities (`parse_frontmatter()` and `tomllib`)
