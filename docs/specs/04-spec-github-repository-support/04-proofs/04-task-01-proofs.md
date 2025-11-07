# 04-task-01-proofs.md

## Task 1.0: GitHub Repository Flag Integration and Validation

This document contains proof artifacts demonstrating the implementation of GitHub repository flag integration and validation.

## CLI Help Output

The CLI help now shows the three new GitHub flags:

```bash
uv run slash-man generate --help
```

Output includes:

```text
│ --github-repo             TEXT  GitHub repository in format owner/repo       │
│ --github-branch           TEXT  GitHub branch name (e.g., main,              │
│                                 release/v1.0)                                │
│ --github-path             TEXT  Path to prompts directory or single prompt   │
│                                 file within repository (e.g., 'prompts' for  │
│                                 directory, 'prompts/my-prompt.md' for file)  │
```

## Validation Error Messages

### Invalid Repository Format

```bash
uv run slash-man generate --github-repo invalid-format --github-branch main --github-path prompts --target-path /tmp/test-output
```

**Output:**

```text
Error: Repository must be in format owner/repo, got: invalid-format. Example: liatrio-labs/spec-driven-workflow
```

**Exit Code:** 2 (Validation error)

### Missing Required Flags

```bash
uv run slash-man generate --github-repo owner/repo --github-path prompts --target-path /tmp/test-output
```

**Output:**

```text
Error: All three GitHub flags (--github-repo, --github-branch, --github-path) must be provided together.

To fix this:
  - Provide all three flags: --github-repo, --github-branch, --github-path
  - Example: --github-repo owner/repo --github-branch main --github-path prompts
```

**Exit Code:** 2 (Validation error)

## Test Results

All tests pass successfully:

### GitHub Utils Tests

```bash
uv run pytest tests/test_github_utils.py -v
```

**Results:**

```text
tests/test_github_utils.py::test_validate_github_repo_valid_formats PASSED
tests/test_github_utils.py::test_validate_github_repo_invalid_formats PASSED
tests/test_github_utils.py::test_validate_github_repo_error_message_includes_example PASSED
```

### CLI Tests

```bash
uv run pytest tests/test_cli.py::test_cli_github_flags_validation tests/test_cli.py::test_validate_github_repo_invalid_format tests/test_cli.py::test_cli_github_flags_missing_required -v
```

**Results:**

```text
tests/test_cli.py::test_cli_github_flags_validation PASSED
tests/test_cli.py::test_validate_github_repo_invalid_format PASSED
tests/test_cli.py::test_cli_github_flags_missing_required PASSED
```

## Code Quality

### Linting

```bash
uv run ruff check slash_commands/ tests/test_github_utils.py tests/test_cli.py
```

**Output:**

```text
All checks passed!
```

## Implementation Summary

### Files Created

- `slash_commands/github_utils.py` - GitHub utilities module with `validate_github_repo()` function

### Files Modified

- `pyproject.toml` - Added `requests>=2.31.0` dependency
- `slash_commands/cli.py` - Added three GitHub flags and validation logic
- `tests/test_cli.py` - Added three new test functions
- `tests/test_github_utils.py` - New test file for GitHub utilities

### Key Features Implemented

1. ✅ Three CLI flags: `--github-repo`, `--github-branch`, `--github-path`
2. ✅ Repository format validation with helpful error messages
3. ✅ Requirement that all three flags must be provided together
4. ✅ Comprehensive test coverage for all validation scenarios

## Demo Criteria Verification

✅ **Demo Criteria 1:** Running `uv run slash-man generate --github-repo owner/repo --github-branch main --github-path prompts --agent claude-code --dry-run --target-path /tmp/test-output` successfully validates flags

- Note: Full implementation requires Task 3.0 (GitHub prompt download), but flag validation works correctly

✅ **Demo Criteria 2:** Running `uv run slash-man generate --github-repo invalid-format --target-path /tmp/test-output` shows clear error

- Verified: Error message includes format requirement and example

## Test Coverage

- `test_validate_github_repo()` - Tests valid and invalid repository formats
- `test_cli_github_flags_validation()` - Verifies CLI help shows new flags
- `test_validate_github_repo_invalid_format()` - Verifies invalid format error
- `test_cli_github_flags_missing_required()` - Verifies missing flags error

All tests pass and provide comprehensive coverage of the validation logic.
