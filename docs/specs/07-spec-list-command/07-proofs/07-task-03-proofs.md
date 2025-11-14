# Task 3.0 Proof Artifacts: Backup Counting and Source Metadata Extraction

## Test Results

### Unit Tests - Backup Counting

```bash
pytest tests/test_list_discovery.py::test_count_backups_returns_zero_for_no_backups tests/test_list_discovery.py::test_count_backups_counts_matching_backups tests/test_list_discovery.py::test_count_backups_handles_multiple_backups tests/test_list_discovery.py::test_count_backups_excludes_non_matching_files -v
```

Output:

```text
============================= test session starts ==============================
platform linux -- Python 3.12.6, pytest-8.4.2, pluggy-1.5.0
collecting ... collected 4 items

tests/test_list_discovery.py::test_count_backups_returns_zero_for_no_backups PASSED [ 25%]
tests/test_list_discovery.py::test_count_backups_counts_matching_backups PASSED [ 50%]
tests/test_list_discovery.py::test_count_backups_handles_multiple_backups PASSED [ 75%]
tests/test_list_discovery.py::test_count_backups_excludes_non_matching_files PASSED [100%]

============================== 4 passed in 0.02s ===============================
```

**Backup Counting Test Coverage:**

- ✅ Counts backups matching pattern `{filename}.{extension}.{timestamp}.bak` (e.g., `command.md.20250115-123456.bak`)
- ✅ Handles files with no backups (count = 0)
- ✅ Handles files with multiple backups
- ✅ Excludes files that don't match backup pattern (e.g., `command.md.bak` without timestamp)

### Unit Tests - Source Metadata Consolidation

```bash
pytest tests/test_list_discovery.py::test_format_source_info_local_source tests/test_list_discovery.py::test_format_source_info_github_source tests/test_list_discovery.py::test_format_source_info_missing_fields -v
```

Output:

```text
============================= test session starts ==============================
platform linux -- Python 3.12.6, pytest-8.4.2, pluggy-1.5.0
collecting ... collected 3 items

tests/test_list_discovery.py::test_format_source_info_local_source PASSED [ 33%]
tests/test_list_discovery.py::test_format_source_info_github_source PASSED [ 66%]
tests/test_list_discovery.py::test_format_source_info_missing_fields PASSED [100%]

============================== 3 passed in 0.02s ===============================
```

**Source Metadata Test Coverage:**

- ✅ Local source formatting: "local: /path/to/prompts" (uses `source_dir` or `source_path`)
- ✅ GitHub source formatting: "github: owner/repo@branch:path"
- ✅ Missing field handling: Returns "Unknown" for missing or invalid source types

### Integration Tests

```bash
pytest tests/integration/test_list_command.py::test_list_shows_backup_counts tests/integration/test_list_command.py::test_list_shows_source_info -v -m integration
```

Output:

```text
============================= test session starts ==============================
platform linux -- Python 3.12.6, pytest-8.4.2, pluggy-1.5.0
collecting ... collected 2 items

tests/integration/test_list_command.py::test_list_shows_backup_counts PASSED [ 50%]
tests/integration/test_list_command.py::test_list_shows_source_info PASSED [100%]

============================== 2 passed in 3.22s ===============================
```

**Integration Test Verification:**

- ✅ `test_list_shows_backup_counts()`: Creates backups using the same pattern as `writer.py` and verifies counts are calculated correctly
- ✅ `test_list_shows_source_info()`: Generates prompts from local source and verifies source information is formatted correctly

## Function Usage Examples

### Example 1: Count Backups

```python
from pathlib import Path
from slash_commands.list_discovery import count_backups

# Count backups for a command file
command_file = Path("/home/user/.cursor/commands/test-command.md")
backup_count = count_backups(command_file)

# Returns number of backup files matching pattern:
# test-command.md.{timestamp}.bak
# e.g., test-command.md.20250115-123456.bak
```

### Example 2: Format Source Info - Local Source

```python
from slash_commands.list_discovery import format_source_info

# Local source with source_dir
meta_local = {
    "source_type": "local",
    "source_dir": "/path/to/prompts",
}
result = format_source_info(meta_local)
# Returns: "local: /path/to/prompts"

# Local source with source_path (fallback)
meta_path = {
    "source_type": "local",
    "source_path": "/path/to/prompt.md",
}
result = format_source_info(meta_path)
# Returns: "local: /path/to/prompt.md"
```

### Example 3: Format Source Info - GitHub Source

```python
from slash_commands.list_discovery import format_source_info

# GitHub source with all fields
meta_github = {
    "source_type": "github",
    "source_repo": "owner/repo",
    "source_branch": "main",
    "source_path": "prompts",
}
result = format_source_info(meta_github)
# Returns: "github: owner/repo@main:prompts"

# GitHub source with missing fields
meta_incomplete = {
    "source_type": "github",
    "source_repo": "owner/repo",
    # Missing branch and path
}
result = format_source_info(meta_incomplete)
# Returns: "github: owner/repo"
```

### Example 4: Format Source Info - Missing Fields

```python
from slash_commands.list_discovery import format_source_info

# Missing source_type
meta_no_type = {
    "source_dir": "/path/to/prompts",
}
result = format_source_info(meta_no_type)
# Returns: "Unknown"

# Empty metadata
result = format_source_info({})
# Returns: "Unknown"
```

## Code Implementation Verification

### Key Functions Implemented

1. **`count_backups(file_path: Path) -> int`** - Counts backup files for a given command file
   - Matches pattern: `{filename}.{extension}.{timestamp}.bak`
   - Validates timestamp format: `YYYYMMDD-HHMMSS`
   - Uses regex pattern similar to `writer.py` line 474
   - Returns 0 if no backups found

2. **`format_source_info(meta: dict[str, Any]) -> str`** - Consolidates source metadata into display line
   - Local sources: "local: /path/to/prompts" (prefers `source_dir`, falls back to `source_path`)
   - GitHub sources: "github: owner/repo@branch:path" (handles missing fields gracefully)
   - Missing fields: Returns "Unknown"

### File Structure

```text
slash_commands/list_discovery.py
├── count_backups()              # Backup counting function
└── format_source_info()         # Source metadata formatting function
```

## Backup Pattern Matching

The backup counting function matches the exact pattern used by `writer.py`:

- **Pattern**: `{filename}.{extension}.{timestamp}.bak`
- **Example**: `command.md.20250115-123456.bak`
- **Timestamp Format**: `YYYYMMDD-HHMMSS` (8 digits, hyphen, 6 digits)
- **Validation**: Uses regex pattern `^{filename}{extension}\.\d{8}-\d{6}\.bak$`

This ensures consistency with the backup creation logic in `writer.py` line 105:

```python
backup_path = file_path.with_suffix(f"{file_path.suffix}.{timestamp}.bak")
```

## Source Metadata Formatting

### Local Sources

- **Preferred**: Uses `meta.source_dir` if present
- **Fallback**: Uses `meta.source_path` if `source_dir` not available
- **Format**: `"local: {path}"`

### GitHub Sources

- **Format**: `"github: {repo}@{branch}:{path}"`
- **Handles Missing Fields**:
  - If `source_branch` missing: `"github: {repo}"`
  - If `source_path` missing: `"github: {repo}@{branch}"`
  - If `source_repo` missing: Returns `"Unknown"`

### Missing or Invalid Sources

- Returns `"Unknown"` for:
  - Missing `source_type`
  - Unknown `source_type` values
  - Empty metadata dict

## Demo Validation

✅ **Demo Criteria Met (as verified by unit and integration tests):**

1. ✅ Backup counting logic counts backups matching pattern `{filename}.{extension}.{timestamp}.bak`
2. ✅ Handles files with no backups (count = 0)
3. ✅ Handles files with multiple backups
4. ✅ Source information is consolidated into single display line
5. ✅ Local sources show path format: "local: /path/to/prompts"
6. ✅ GitHub sources show format: "github: owner/repo@branch:path"
7. ✅ Missing source fields are handled gracefully (returns "Unknown")
8. ✅ Integration tests verify functions work correctly with generated prompts

## Pending Proof Artifacts

The following proof artifacts require the CLI command implementation (Task 5.0):

- ⏳ **CLI Transcript**: Running `slash-man list` and showing backup counts in output
- ⏳ **CLI Transcript**: Running `slash-man list` and showing source information in output
- ⏳ **CLI Transcript**: Showing GitHub source display after generating from GitHub source testing command

These will be completed once Task 5.0 (CLI command implementation) is finished.

## Notes

- All unit tests pass (7/7 for backup counting and source formatting)
- Integration tests verify functions work correctly with real generated prompts
- Backup pattern matching exactly matches `writer.py` backup creation pattern
- Source metadata formatting handles all edge cases gracefully
- Functions are ready to be used by the `list` CLI command (Task 5.0)
