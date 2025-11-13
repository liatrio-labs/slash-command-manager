# Task 4.0 Proof Artifacts: Prompt Metadata Source Tracking

## Test Results

### Source Metadata Tests

```bash
uv run pytest tests/test_generators.py::test_prompt_metadata_github_source tests/test_generators.py::test_prompt_metadata_github_single_file_source tests/test_generators.py::test_prompt_metadata_local_source tests/test_generators.py::test_prompt_metadata_no_source_metadata -v
```

```text
============================= test session starts ==============================
platform linux -- Python 3.12.6, pytest-8.4.2, pluggy-1.5.0
collected 4 items

tests/test_generators.py::test_prompt_metadata_github_source PASSED      [ 25%]
tests/test_generators.py::test_prompt_metadata_github_single_file_source PASSED [ 50%]
tests/test_generators.py::test_prompt_metadata_local_source PASSED       [ 75%]
tests/test_generators.py::test_prompt_metadata_no_source_metadata PASSED [100%]

============================== 4 passed in 0.06s ===============================
```

### Full Test Suite

```bash
uv run pytest tests/ -v --tb=short
```

```text
============================= test session starts ==============================
platform linux -- Python 3.12.6, pytest-8.4.2, pluggy-1.5.0
collected 150 items

... (all tests pass)

============================= 150 passed in 0.85s ==============================
```

## Implementation Details

### Generator Updates

- Extended `CommandGeneratorProtocol` to accept optional `source_metadata` parameter
- Updated `MarkdownCommandGenerator._build_meta()` to accept and include source metadata
- Updated `TomlCommandGenerator.generate()` to accept and include source metadata in `meta` dict
- Both generators add source metadata fields when provided

### Writer Updates

- `SlashCommandWriter.__init__()` determines source metadata based on GitHub parameters or local directory
- For GitHub: Sets `source_type: "github"`, `source_repo`, `source_branch`, `source_path`
- For local: Sets `source_type: "local"`, `source_dir` (absolute path)
- `_generate_file()` passes source metadata to generator

### Source Metadata Fields

**GitHub Source:**

- `source_type: "github"`
- `source_repo: "owner/repo"`
- `source_branch: "branch-name"`
- `source_path: "path/to/prompts"` or `"path/to/file.md"`

**Local Source:**

- `source_type: "local"`
- `source_dir: "/absolute/path/to/prompts"`

## Demo Validation

### Demo Criteria Met

✅ **GitHub directory metadata**: Generated files contain `source_type: "github"`, `source_repo`, `source_branch`, `source_path` for directory paths

✅ **GitHub single file metadata**: Generated files contain correct metadata for single file paths

✅ **Local directory metadata**: Generated files contain `source_type: "local"` and `source_dir` for local prompts

✅ **Test coverage**: All required tests implemented and passing

## Files Modified

- `slash_commands/generators.py` - Extended generators to accept and include source metadata
- `slash_commands/writer.py` - Added source metadata determination and passing to generators
- `tests/test_generators.py` - Added tests for source metadata tracking
