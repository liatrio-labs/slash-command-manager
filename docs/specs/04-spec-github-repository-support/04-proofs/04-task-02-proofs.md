# 04-task-02-proofs.md

## Task 2.0: GitHub and Local Directory Mutual Exclusivity

This document contains proof artifacts demonstrating the implementation of mutual exclusivity validation between `--prompts-dir` and GitHub repository flags.

## CLI Error Message Output

The CLI correctly detects when both `--prompts-dir` and GitHub flags are provided simultaneously and shows a clear error message:

```bash
uv run slash-man generate --prompts-dir ./prompts --github-repo owner/repo --github-branch main --github-path prompts --target-path /tmp/test-output
```

**Output:**

```text
Error: Cannot specify both --prompts-dir and GitHub repository flags (--github-repo, --github-branch, --github-path) simultaneously.

To fix this:
  - Use either --prompts-dir for local prompts, or
  - Use --github-repo, --github-branch, and --github-path for GitHub prompts
```

**Exit Code:** 2 (Validation error)

## Test Results

The test `test_cli_github_and_local_mutually_exclusive()` verifies mutual exclusivity:

```bash
uv run pytest tests/test_cli.py::test_cli_github_and_local_mutually_exclusive -v
```

**Results:**

```text
tests/test_cli.py::test_cli_github_and_local_mutually_exclusive PASSED
```

### Full Test Suite

All tests pass successfully:

```bash
uv run pytest tests/ -v
```

**Results:**

```text
============================= test session starts ==============================
... (116 tests total)
tests/test_cli.py::test_cli_github_and_local_mutually_exclusive PASSED
... (all 116 tests passed)
============================= 116 passed in 0.60s ==============================
```

## Code Quality

### Linting

```bash
uv run ruff check slash_commands/cli.py tests/test_cli.py
```

**Output:**

```text
All checks passed!
```

## Implementation Summary

### Files Modified

- `slash_commands/cli.py` - Added mutual exclusivity validation logic (lines 234-244)
- `tests/test_cli.py` - Added `test_cli_github_and_local_mutually_exclusive()` test function

### Key Features Implemented

1. ✅ Validation logic checks if both `--prompts-dir` and any GitHub flag are provided
2. ✅ Clear error message explaining mutual exclusivity
3. ✅ Exit code 2 (validation error) when both are detected
4. ✅ Comprehensive test coverage for mutual exclusivity scenario

## Demo Criteria Verification

✅ **Demo Criteria:** Running `uv run slash-man generate --prompts-dir ./prompts --github-repo owner/repo --github-branch main --github-path prompts --target-path /tmp/test-output` shows error explaining mutual exclusivity with clear message

- Verified: Error message clearly states "Cannot specify both --prompts-dir and GitHub repository flags"
- Verified: Error message includes helpful guidance on how to fix the issue
- Verified: Exit code is 2 (validation error)

## Test Coverage

- `test_cli_github_and_local_mutually_exclusive()` - Verifies mutual exclusivity error is raised with clear message when both `--prompts-dir` and all three GitHub flags are provided

The test passes and provides comprehensive coverage of the mutual exclusivity validation logic.
