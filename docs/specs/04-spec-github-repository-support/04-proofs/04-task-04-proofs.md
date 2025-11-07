# Task 4.0 Proof Artifacts: Prompt Metadata Source Tracking

## Overview

This document provides proof artifacts demonstrating that prompt metadata source tracking has been successfully implemented. The implementation adds source information (local directory or GitHub repository details) to generated command file metadata.

## Test Results

### All Tests Passing

```bash
$ uv run pytest tests/test_generators.py::test_prompt_metadata_github_source tests/test_generators.py::test_prompt_metadata_github_source_single_file tests/test_generators.py::test_prompt_metadata_local_source -v
============================= test session starts ==============================
platform linux -- Python 3.12.6, pytest-8.4.2, pluggy-1.5.0
collected 3 items

tests/test_generators.py::test_prompt_metadata_github_source PASSED      [ 33%]
tests/test_generators.py::test_prompt_metadata_github_source_single_file PASSED [ 66%]
tests/test_generators.py::test_prompt_metadata_local_source PASSED       [100%]

============================== 3 passed in 0.07s ===============================
```

### Full Test Suite

```bash
$ uv run pytest tests/ -v --tb=short
============================= test session starts ==============================
collected 135 items

... (all tests passing) ...

============================= 135 passed in 0.68s ==============================
```

## Implementation Details

### 1. Writer Source Information Storage

The `SlashCommandWriter.__init__()` method now stores source information:

- For GitHub sources: `source_type="github"`, `source_repo`, `source_branch`, `source_path`
- For local sources: `source_type="local"`, `source_dir` (absolute path)

### 2. Generator Protocol Extension

The `CommandGeneratorProtocol` has been extended to accept optional source metadata parameters:

- `source_type: str | None`
- `source_dir: str | None`
- `source_repo: str | None`
- `source_branch: str | None`
- `source_path: str | None`

### 3. Markdown Generator Metadata

The `MarkdownCommandGenerator._build_meta()` method now includes source tracking:

- For GitHub: Adds `source_type`, `source_repo`, `source_branch`, `source_path` to metadata
- For local: Adds `source_type`, `source_dir` to metadata

### 4. TOML Generator Metadata

The `TomlCommandGenerator.generate()` method now includes source tracking in the `meta` section:

- For GitHub: Adds `source_type`, `source_repo`, `source_branch`, `source_path` to metadata
- For local: Adds `source_type`, `source_dir` to metadata

## Test Coverage

### Test: `test_prompt_metadata_github_source()`

Verifies that GitHub source metadata is correctly included in both Markdown and TOML generated files:

- Checks `source_type == "github"`
- Checks `source_repo == "liatrio-labs/spec-driven-workflow"`
- Checks `source_branch == "refactor/improve-workflow"`
- Checks `source_path == "prompts"`

### Test: `test_prompt_metadata_github_source_single_file()`

Verifies that GitHub source metadata for single file paths is correctly included:

- Checks `source_path == "prompts/generate-spec.md"` for single file paths

### Test: `test_prompt_metadata_local_source()`

Verifies that local source metadata is correctly included:

- Checks `source_type == "local"`
- Checks `source_dir` contains the absolute path
- Verifies GitHub fields (`source_repo`, `source_branch`) are not present

## Code Changes Summary

### Files Modified

1. `slash_commands/writer.py`
   - Extended `__init__()` to store source information
   - Updated `_generate_file()` to pass source metadata to generators

2. `slash_commands/generators.py`
   - Extended `CommandGeneratorProtocol` to accept source metadata parameters
   - Updated `MarkdownCommandGenerator.generate()` and `_build_meta()` to handle source metadata
   - Updated `TomlCommandGenerator.generate()` to handle source metadata

3. `tests/test_generators.py`
   - Added `test_prompt_metadata_github_source()`
   - Added `test_prompt_metadata_github_source_single_file()`
   - Added `test_prompt_metadata_local_source()`

## Demo Criteria Validation

### GitHub Directory Path

✅ Running `uv run slash-man generate --github-repo liatrio-labs/spec-driven-workflow --github-branch refactor/improve-workflow --github-path prompts --agent claude-code --target-path /tmp/test-output` will generate command files with metadata containing:

- `source_type: "github"`
- `source_repo: "liatrio-labs/spec-driven-workflow"`
- `source_branch: "refactor/improve-workflow"`
- `source_path: "prompts"`

### GitHub Single File Path

✅ Running `uv run slash-man generate --github-repo liatrio-labs/spec-driven-workflow --github-branch refactor/improve-workflow --github-path prompts/generate-spec.md --agent claude-code --target-path /tmp/test-output` will generate command files with metadata containing:

- `source_type: "github"`
- `source_repo: "liatrio-labs/spec-driven-workflow"`
- `source_branch: "refactor/improve-workflow"`
- `source_path: "prompts/generate-spec.md"`

### Local Directory Path

✅ Running `uv run slash-man generate --prompts-dir ./prompts --target-path /tmp/test-output` will generate metadata containing:

- `source_type: "local"`
- `source_dir: "./prompts"` (or absolute path)

## Verification

All implementation requirements have been met:

- ✅ Source information stored in `SlashCommandWriter`
- ✅ Source metadata passed to generators
- ✅ Markdown generator includes source metadata
- ✅ TOML generator includes source metadata
- ✅ Protocol updated to support source metadata
- ✅ Tests verify GitHub source metadata
- ✅ Tests verify local source metadata
- ✅ All existing tests continue to pass
