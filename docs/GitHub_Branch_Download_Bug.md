# GitHub Branch Download Bug

## Issue

This command:

```bash
uv run slash-man generate \
  --github-repo liatrio-labs/spec-driven-workflow \
  --github-branch damien-test \
  --github-path prompts \
  --agent claude-code \
  --target-path /tmp/test-output
```

is downloading the prompts from the `main` branch instead of the `damien-test` branch.

## Goal

Fully reproduce the bug in a clean environment and fix it using strict Test-Driven Development (TDD).

## ⚠️ CRITICAL WARNING: Integration Tests MUST Run in Docker Only

**NEVER run integration tests locally.** Running integration tests locally will disrupt and modify your local development environment configuration.

### Integration Test Rules

- ❌ **DO NOT** run `pytest tests/integration/` locally
- ❌ **DO NOT** run `uv run pytest tests/integration/` locally
- ❌ **DO NOT** run integration tests with any local test runner
- ✅ **ONLY** run integration tests using `uv run scripts/run_integration_tests.py` (which runs them in Docker)
- ✅ **ONLY** run unit tests locally: `uv run pytest tests/ -m "not integration"`
- ✅ **ONLY** run specific unit test files locally: `uv run pytest tests/test_github_utils.py`

### Why This Matters

Integration tests may:

- Modify local file system configurations
- Create or modify files in your home directory
- Interfere with your local development setup
- Cause conflicts with your existing configuration

**All integration testing MUST happen in isolated Docker containers.**

### Primary Goals

1. **Reproduce the Bug**: Fully reproduce the bug in a clean Docker environment following the steps outlined below.

2. **Analyze Test Suite Gap**: Investigate why the existing test suite didn't catch this bug:
   - Review `tests/test_github_utils.py::test_download_prompts_from_github_directory` and related tests
   - Identify why tests using mocked `download_url` values didn't expose the branch mismatch issue
   - Document the specific test coverage gaps that allowed this bug to slip through

3. **Improve Test Suite**: Enhance the test suite to prevent similar issues:
   - Add integration tests that verify branch-specific downloads work correctly
   - Add tests that verify `download_url` values respect the requested branch parameter
   - Add tests that use different branch names (not just `main`) to ensure branch handling is correct
   - Consider adding tests that verify the actual content downloaded matches the expected branch
   - Document test improvements and ensure they catch this specific bug pattern

4. **Fix Implementation**: Implement the fix using strict TDD methodology:
   - **MUST** write failing tests first that reproduce the bug
   - **MUST** verify tests fail for the correct reason (branch mismatch)
   - **MUST** implement minimal code changes to make tests pass
   - **MUST** ensure all existing tests continue to pass
   - **MUST** add new tests to prevent regression

## Expected Behavior

When specifying `--github-branch damien-test`, the system should download all markdown files from the `prompts` directory on the `damien-test` branch of the `liatrio-labs/spec-driven-workflow` repository. Specifically, the `generate_spec.md` file should contain "THIS IS A TEST" (the content from the `damien-test` branch).

## Actual Behavior

The system downloads files from the `main` branch instead of the specified `damien-test` branch. The `generate_spec.md` file contains the content from the `main` branch, not "THIS IS A TEST".

## Root Cause Analysis

The issue occurs in the `download_prompts_from_github()` function in `slash_commands/github_utils.py`. When downloading from a directory:

1. The initial directory listing API call correctly uses the `ref` parameter to request the specified branch (line 180: `params = {"ref": branch}`).
2. However, when processing directory listings, the code uses the `download_url` field from the GitHub API response (line 234).
3. The `download_url` values returned by GitHub contain the branch name hardcoded in the URL (e.g., `https://raw.githubusercontent.com/owner/repo/main/prompts/file.md`).
4. Even though the directory listing was requested with `ref=damien-test`, GitHub may return `download_url` values that point to the default branch (`main`) instead of the requested branch.
5. The code then fetches files directly from these `download_url` values without ensuring they point to the correct branch (line 241).

**Affected Code Path:**

```217:247:slash_commands/github_utils.py
        elif isinstance(data, list):
            # Directory response - filter for .md files only in immediate directory
            for item in data:
                if item.get("type") == "file" and item.get("name", "").endswith(".md"):
                    filename = item["name"]
                    content_encoded = item.get("content", "")

                    if content_encoded:
                        # Single file requests include base64-encoded content
                        try:
                            content = base64.b64decode(content_encoded).decode("utf-8")
                            prompts.append((filename, content))
                        except Exception:
                            # Skip files that can't be decoded
                            continue
                    else:
                        # Directory listings don't include content, use download_url
                        download_url = item.get("download_url")
                        if not download_url:
                            continue

                        _validate_raw_github_download_url(download_url)
                        try:
                            # Fetch file content from download_url
                            file_response = requests.get(download_url, timeout=30)
                            file_response.raise_for_status()
                            content = file_response.text
                            prompts.append((filename, content))
                        except requests.exceptions.RequestException:
                            # Skip files that can't be downloaded
                            continue
```

**Note:** Single file downloads work correctly because they use the Contents API with the `ref` parameter and decode base64 content directly from the response (lines 197-215).

## Why Existing Tests Didn't Catch This Bug

### Test Coverage Analysis

The existing test suite has a critical gap that allowed this bug to go undetected:

1. **`test_download_prompts_from_github_directory` (tests/test_github_utils.py:133-198)**:
   - Tests directory downloads but only uses `"main"` as the branch parameter
   - Mocks `download_url` values that also point to `main` branch (lines 143, 150)
   - Verifies that the `ref` parameter is passed correctly to the directory listing API call (line 193)
   - **Does NOT verify** that file downloads actually use the correct branch
   - **Does NOT test** with a different branch name to ensure branch handling works correctly
   - The test passes because the mocked `download_url` matches what the buggy code does (incorrectly using hardcoded branch in URL)

2. **`test_writer_loads_prompts_from_github` (tests/test_writer.py:717-777)**:
   - Mocks the entire download function, bypassing the actual GitHub API logic
   - Does not test the actual branch parameter handling
   - Only verifies that prompts are loaded after a successful download

3. **Missing Test Coverage**:
   - No tests verify that `download_url` values respect the requested branch parameter
   - No tests use branch names other than `main` to verify branch-specific behavior
   - No integration tests that actually download from different branches and verify content matches
   - No tests that verify the branch name in `download_url` matches the requested branch

### Test Gap Summary

The tests verify:

- ✅ The `ref` parameter is passed to the directory listing API call
- ✅ Files are downloaded successfully
- ✅ The correct files are returned

The tests do NOT verify:

- ❌ That `download_url` values contain the correct branch name
- ❌ That files downloaded from `download_url` match the requested branch
- ❌ That different branch names work correctly (only `main` is tested)
- ❌ That the actual content downloaded matches the expected branch

### Required Test Improvements

To prevent this bug from recurring, the test suite should include:

1. **Branch-Specific URL Verification**: Tests that verify `download_url` values contain the correct branch name when a non-default branch is requested
2. **Multi-Branch Testing**: Tests using different branch names (e.g., `damien-test`, `feature/test-branch`) to ensure branch handling works for all branches
3. **Content Verification**: Integration tests that download from different branches and verify the actual content matches the expected branch
4. **URL Parsing Tests**: Tests that verify the code correctly parses and replaces branch names in `download_url` values

## Steps to Reproduce

### Prerequisites

1. Ensure Docker is installed and running
1. Ensure the `damien-test` branch exists in `liatrio-labs/spec-driven-workflow` repository with different content than `main` branch
1. The `prompts/generate_spec.md` file should exist on both branches with different content:
   - `main` branch: original content
   - `damien-test` branch: "THIS IS A TEST"

### Reproduction Steps

1. Build the Docker image:

```bash
docker build -t slash-command-manager .
```

1. Run the command with `damien-test` branch:

```bash
docker run --rm slash-command-manager bash -c "
  uv run slash-man generate \
    --github-repo liatrio-labs/spec-driven-workflow \
    --github-branch damien-test \
    --github-path prompts \
    --agent claude-code \
    --target-path /tmp/test-output
"
```

1. Check the content of the downloaded file:

```bash
docker run --rm slash-command-manager bash -c "
  cat /tmp/test-output/claude-code/generate_spec.md
"
```

1. Compare with the `main` branch:

```bash
docker run --rm slash-command-manager bash -c "
  uv run slash-man generate \
    --github-repo liatrio-labs/spec-driven-workflow \
    --github-branch main \
    --github-path prompts \
    --agent claude-code \
    --target-path /tmp/test-output-main
"
```

```bash
docker run --rm slash-command-manager bash -c "
  cat /tmp/test-output-main/claude-code/generate_spec.md
"
```

### Expected vs Actual

- **Expected:** The file from `damien-test` branch should contain "THIS IS A TEST"
- **Actual:** The file contains the same content as the `main` branch

## Environment

- **Repository:** `liatrio-labs/spec-driven-workflow`
- **Test Branch:** `damien-test`
- **Test Path:** `prompts`
- **Test File:** `prompts/generate_spec.md`
- **Docker Environment:** Clean Docker container built from project Dockerfile
- **Python Version:** 3.12+ (as specified in project requirements)

## Testing Instructions

### ⚠️ CRITICAL: Integration Tests in Docker Only

**Integration tests MUST ONLY be run using the Docker script. Never run them locally.**

```bash
# ✅ CORRECT: Run integration tests in Docker
uv run scripts/run_integration_tests.py

# ❌ WRONG: Never run these commands locally
# pytest tests/integration/
# uv run pytest tests/integration/
# pytest -m integration
```

### Unit Tests (Safe to Run Locally)

Unit tests can be run locally without affecting your configuration:

```bash
# Run all unit tests (excluding integration tests)
uv run pytest tests/ -m "not integration"

# Run specific unit test file
uv run pytest tests/test_github_utils.py

# Run specific unit test
uv run pytest tests/test_github_utils.py::test_download_prompts_from_github_directory
```

### Manual Testing in Docker

Follow the `Testing in Clean Environment (Docker)` section of the README.md:

1. Build Docker image: `docker build -t slash-command-manager .`
2. Run interactively: `docker run -it --rm slash-command-manager bash`
3. Execute the failing command inside the container
4. Verify the content of `generate_spec.md` matches the expected branch content

### Validation

You can validate this by following the `Testing in Clean Environment (Docker)` section of the README.md. Run the command above as is in the docker container and note the content of `generate_spec.md`. It should just say "THIS IS A TEST". You can also run the command using `--github-branch main` to compare the content of the downloaded versions of `generate_spec.md`.

## Additional Context

- The bug only affects directory downloads, not single file downloads
- Single file downloads work correctly because they use the Contents API with base64-encoded content
- The GitHub Contents API documentation indicates that `download_url` in directory listings may not always reflect the requested branch
- The fix should ensure that `download_url` values are either:
  1. Parsed and the branch name replaced with the requested branch, or
  2. Individual files should be fetched using the Contents API with the `ref` parameter instead of using `download_url`

## Guidelines

### Testing Environment

**CRITICAL: Integration tests MUST NEVER be run locally.**

- ❌ **NEVER** run `pytest tests/integration/` or any integration tests locally
- ❌ **NEVER** run integration tests with any local test runner
- ✅ **ONLY** run integration tests using `uv run scripts/run_integration_tests.py` (Docker only)
- ✅ Unit tests (`tests/test_*.py` excluding `tests/integration/`) can be run locally safely
- ✅ Run unit tests locally: `uv run pytest tests/ -m "not integration"`
- ✅ All integration testing MUST happen in isolated Docker containers to protect local configuration

### TDD Requirements (MANDATORY)

**All fixes MUST follow strict Test-Driven Development (TDD) methodology:**

1. **Red Phase - Write Failing Test First**:
   - Write a test that reproduces the bug (should fail)
   - Verify the test fails for the correct reason (branch mismatch, not other errors)
   - Commit the failing test with message: `test: add failing test for branch download bug`

2. **Green Phase - Make Test Pass**:
   - Implement minimal code changes to make the test pass
   - Do not add unnecessary features or optimizations
   - Verify the new test passes
   - **Verify unit tests locally**: `uv run pytest tests/ -m "not integration"`
   - **Verify integration tests in Docker**: `uv run scripts/run_integration_tests.py` (NEVER run locally)

3. **Refactor Phase - Improve Code Quality**:
   - Refactor if needed while keeping all tests passing
   - Ensure code follows project conventions and patterns
   - Add additional tests if edge cases are discovered

4. **Test Coverage Requirements**:
   - Add unit tests that verify `download_url` branch handling works correctly (run locally)
   - Add unit tests using different branch names (not just `main`) (run locally)
   - Add integration tests that verify actual content matches expected branch (**run ONLY in Docker**)
   - Ensure new tests would have caught this bug if they existed before
   - **Remember**: Unit tests can be run locally; integration tests MUST run in Docker only

5. **Verification Checklist**:
   - [ ] Failing test written and committed first
   - [ ] Test fails for the correct reason (branch mismatch)
   - [ ] Implementation makes test pass
   - [ ] All unit tests pass locally: `uv run pytest tests/ -m "not integration"`
   - [ ] Integration tests pass in Docker: `uv run scripts/run_integration_tests.py` (**NEVER run locally**)
   - [ ] New tests prevent regression
   - [ ] Test improvements documented
   - [ ] **Confirmed**: No integration tests were run locally during development
