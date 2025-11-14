# Task 2.0 Proof Artifacts: GitHub and Local Directory Mutual Exclusivity

## CLI Output

### Mutual Exclusivity Error Message

```bash
uv run slash-man generate --prompts-dir ./prompts --github-repo owner/repo --github-branch main --github-path prompts --target-path /tmp/test-output
```

```text
Error: Cannot specify both --prompts-dir and GitHub repository flags (--github-repo, --github-branch, --github-path) simultaneously

To fix this:
  - Use either --prompts-dir for local prompts, or
  - Use --github-repo, --github-branch, and --github-path for GitHub prompts
```

## Test Results

### Test Execution

```bash
uv run pytest tests/test_cli.py::test_cli_github_and_local_mutually_exclusive -v
```

```text
============================= test session starts ==============================
platform linux -- Python 3.12.6, pytest-8.4.2, pluggy-1.5.0
collected 1 item

tests/test_cli.py::test_cli_github_and_local_mutually_exclusive PASSED   [100%]

============================== 1 passed in 0.08s ===============================
```

### Full Test Suite

```bash
uv run pytest tests/ -v --tb=short
```

```text
============================= test session starts ==============================
platform linux -- Python 3.12.6, pytest-8.4.2, pluggy-1.5.0
collected 133 items

... (all tests pass)

============================= 133 passed in 1.10s ==============================
```

## Demo Validation

### Demo Criteria Met

✅ **Mutual exclusivity validation**: Running `uv run slash-man generate --prompts-dir ./prompts --github-repo owner/repo --github-branch main --github-path prompts --target-path /tmp/test-output` shows clear error explaining mutual exclusivity

✅ **Test coverage**: Test `test_cli_github_and_local_mutually_exclusive()` is implemented and passing

## Files Modified

- `slash_commands/cli.py` - Added mutual exclusivity validation between `--prompts-dir` and GitHub flags
- `tests/test_cli.py` - Added test for mutual exclusivity validation
