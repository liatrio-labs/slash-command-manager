# Task 1.0 Proof Artifacts: GitHub Repository Flag Integration and Validation

## CLI Output

### Help Output Showing New Flags

```bash
uv run slash-man generate --help
```

```text
│ --github-repo             TEXT  GitHub repository in format owner/repo       │
│ --github-branch           TEXT  GitHub branch name (e.g., main,              │
│                                 release/v1.0)                                │
│ --github-path             TEXT  Path to prompts directory or single prompt   │
│                                 file within repository (e.g., 'prompts' for  │
│                                 directory, 'prompts/my-prompt.md' for file)  │
```

### Invalid Repository Format Error

```bash
uv run slash-man generate --github-repo invalid-format --github-branch main --github-path prompts --target-path /tmp/test-output
```

```text
Error: Repository must be in format owner/repo, got: 'invalid-format'. Example: liatrio-labs/spec-driven-workflow
```

### Missing Required Flags Error

```bash
uv run slash-man generate --github-repo owner/repo --target-path /tmp/test-output
```

```text
Error: All GitHub flags must be provided together. Missing: --github-branch, --github-path

To fix this:
  - Provide all three flags: --github-repo, --github-branch, --github-path
```

## Test Results

### Test Execution

```bash
uv run pytest tests/test_github_utils.py tests/test_cli.py::test_cli_github_flags_validation tests/test_cli.py::test_validate_github_repo_invalid_format tests/test_cli.py::test_cli_github_flags_missing_required -v
```

```text
============================= test session starts ==============================
platform linux -- Python 3.12.6, pytest-8.4.2, pluggy-1.5.0
collected 6 items

tests/test_github_utils.py::test_validate_github_repo_valid_formats PASSED [ 16%]
tests/test_github_utils.py::test_validate_github_repo_invalid_format PASSED [ 33%]
tests/test_github_utils.py::test_validate_github_repo_error_message_includes_example PASSED [ 50%]
tests/test_cli.py::test_cli_github_flags_validation PASSED               [ 66%]
tests/test_cli.py::test_validate_github_repo_invalid_format PASSED       [ 83%]
tests/test_cli.py::test_cli_github_flags_missing_required PASSED         [100%]

============================== 6 passed in 0.15s ===============================
```

### Full Test Suite

```bash
uv run pytest tests/ -v --tb=short
```

```text
============================= test session starts ==============================
platform linux -- Python 3.12.6, pytest-8.4.2, pluggy-1.5.0
collected 132 items

... (all tests pass)

============================= 132 passed in 1.08s ==============================
```

## Configuration

### Dependencies Added

```toml
dependencies = [
    "fastmcp",
    "questionary>=1.10.0",
    "requests>=2.31.0",  # Added for GitHub API support
    "tomli-w>=1.0.0",
    "rich>=13.0.0",
    "typer>=0.9.0",
    "pyyaml>=6.0",
]
```

## Demo Validation

### Demo Criteria Met

✅ **CLI help shows new flags**: `--github-repo`, `--github-branch`, `--github-path` are visible in help output

✅ **Invalid format validation**: Running `uv run slash-man generate --github-repo invalid-format --github-branch main --github-path prompts --target-path /tmp/test-output` shows clear error: "Repository must be in format owner/repo, got: 'invalid-format'. Example: liatrio-labs/spec-driven-workflow"

✅ **Missing flags validation**: Running with partial GitHub flags shows clear error message listing missing flags

✅ **Test coverage**: All required tests (`test_cli_github_flags_validation`, `test_validate_github_repo_invalid_format`, `test_cli_github_flags_missing_required`) are implemented and passing

## Files Created/Modified

- `pyproject.toml` - Added `requests>=2.31.0` dependency
- `slash_commands/github_utils.py` - New file with `validate_github_repo()` function
- `tests/test_github_utils.py` - New file with GitHub utility tests
- `slash_commands/cli.py` - Added GitHub flags and validation logic
- `tests/test_cli.py` - Added CLI tests for GitHub flag validation
