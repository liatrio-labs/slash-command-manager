# Task 2.0 Proof Artifacts: Cross-Platform Detection Tests

## Test Code

Three new parametrized test functions added to `tests/test_detection.py`:

### 1. test_vs_code_insiders_detection_multiplatform

```python
@pytest.mark.parametrize(
    "platform_value,expected_dir",
    [
        ("linux", ".config/Code - Insiders"),
        ("darwin", "Library/Application Support/Code - Insiders"),
        ("win32", "AppData/Roaming/Code - Insiders"),
    ],
)
def test_vs_code_insiders_detection_multiplatform(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, platform_value: str, expected_dir: str
) -> None:
    """Test VS Code Insiders detection works on all platforms."""
    monkeypatch.setattr(sys, "platform", platform_value)
    (tmp_path / expected_dir).mkdir(parents=True, exist_ok=True)

    detected = detect_agents(tmp_path)
    detected_keys = [agent.key for agent in detected]

    assert "vs-code-insiders" in detected_keys
```

### 2. test_vs_code_insiders_detection_empty_when_no_directories

```python
@pytest.mark.parametrize("platform_value", ["linux", "darwin", "win32"])
def test_vs_code_insiders_detection_empty_when_no_directories(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, platform_value: str
) -> None:
    """Test VS Code Insiders detection returns nothing when paths don't exist."""
    monkeypatch.setattr(sys, "platform", platform_value)

    detected = detect_agents(tmp_path)
    detected_keys = [agent.key for agent in detected]

    assert "vs-code-insiders" not in detected_keys
```

### 3. test_vs_code_insiders_get_command_dir_platform_specific

```python
@pytest.mark.parametrize(
    "platform_value,expected_command_dir",
    [
        ("linux", ".config/Code - Insiders/User/prompts"),
        ("darwin", "Library/Application Support/Code - Insiders/User/prompts"),
        ("win32", "AppData/Roaming/Code - Insiders/User/prompts"),
    ],
)
def test_vs_code_insiders_get_command_dir_platform_specific(
    monkeypatch: pytest.MonkeyPatch, platform_value: str, expected_command_dir: str
) -> None:
    """Test get_command_dir() returns correct platform-specific path for VS Code Insiders."""
    monkeypatch.setattr(sys, "platform", platform_value)

    vs_code_insiders_agent = get_agent_config("vs-code-insiders")
    actual_dir = vs_code_insiders_agent.get_command_dir()

    assert actual_dir == expected_command_dir
```

## Test Results - VS Code Insiders Tests Only

Command: `uv run pytest tests/test_detection.py -v -k insiders`

```
=========================== test session starts ===========================
platform darwin -- Python 3.13.4, pytest-8.4.2, pluggy-1.6.0 -- /Users/mitchschaller/Liatrio/slash-command-manager/.venv/bin/python3
cachedir: .pytest_cache
rootdir: /Users/mitchschaller/Liatrio/slash-command-manager
configfile: pyproject.toml
plugins: anyio-4.11.0, httpx-0.35.0, cov-7.0.0
collected 23 items / 14 deselected / 9 selected

tests/test_detection.py::test_vs_code_insiders_detection_multiplatform[linux-.config/Code - Insiders] PASSED [ 11%]
tests/test_detection.py::test_vs_code_insiders_detection_multiplatform[darwin-Library/Application Support/Code - Insiders] PASSED [ 22%]
tests/test_detection.py::test_vs_code_insiders_detection_multiplatform[win32-AppData/Roaming/Code - Insiders] PASSED [ 33%]
tests/test_detection.py::test_vs_code_insiders_detection_empty_when_no_directories[linux] PASSED [ 44%]
tests/test_detection.py::test_vs_code_insiders_detection_empty_when_no_directories[darwin] PASSED [ 55%]
tests/test_detection.py::test_vs_code_insiders_detection_empty_when_no_directories[win32] PASSED [ 66%]
tests/test_detection.py::test_vs_code_insiders_get_command_dir_platform_specific[linux-.config/Code - Insiders/User/prompts] PASSED [ 77%]
tests/test_detection.py::test_vs_code_insiders_get_command_dir_platform_specific[darwin-Library/Application Support/Code - Insiders/User/prompts] PASSED [ 88%]
tests/test_detection.py::test_vs_code_insiders_get_command_dir_platform_specific[win32-AppData/Roaming/Code - Insiders/User/prompts] PASSED [100%]

==================== 9 passed, 14 deselected in 0.02s ====================
```

### Verification

- ✅ 9 VS Code Insiders tests created and passing
- ✅ 3 tests for multiplatform detection (linux, darwin, win32)
- ✅ 3 tests for empty detection when directories don't exist
- ✅ 3 tests for get_command_dir() platform-specific paths
- ✅ All tests use monkeypatch fixture to simulate different platforms

## Test Results - All Detection Tests (No Regressions)

Command: `uv run pytest tests/test_detection.py -v`

```
=========================== test session starts ===========================
platform darwin -- Python 3.13.4, pytest-8.4.2, pluggy-1.6.0 -- /Users/mitchschaller/Liatrio/slash-command-manager/.venv/bin/python3
cachedir: .pytest_cache
rootdir: /Users/mitchschaller/Liatrio/slash-command-manager
configfile: pyproject.toml
plugins: anyio-4.11.0, httpx-0.35.0, cov-7.0.0
collected 23 items

tests/test_detection.py::test_detect_agents_returns_empty_when_no_matching_directories PASSED [  4%]
tests/test_detection.py::test_detect_agents_identifies_configured_directories PASSED [  8%]
tests/test_detection.py::test_detect_agents_deduplicates_and_orders_results PASSED [ 13%]
tests/test_detection.py::test_vs_code_detection_multiplatform[linux-.config/Code] PASSED [ 17%]
tests/test_detection.py::test_vs_code_detection_multiplatform[darwin-Library/Application Support/Code] PASSED [ 21%]
tests/test_detection.py::test_vs_code_detection_multiplatform[win32-AppData/Roaming/Code] PASSED [ 26%]
tests/test_detection.py::test_vs_code_detection_empty_when_no_directories[linux] PASSED [ 30%]
tests/test_detection.py::test_vs_code_detection_empty_when_no_directories[darwin] PASSED [ 34%]
tests/test_detection.py::test_vs_code_detection_empty_when_no_directories[win32] PASSED [ 39%]
tests/test_detection.py::test_vs_code_insiders_detection_multiplatform[linux-.config/Code - Insiders] PASSED [ 43%]
tests/test_detection.py::test_vs_code_insiders_detection_multiplatform[darwin-Library/Application Support/Code - Insiders] PASSED [ 47%]
tests/test_detection.py::test_vs_code_insiders_detection_multiplatform[win32-AppData/Roaming/Code - Insiders] PASSED [ 52%]
tests/test_detection.py::test_vs_code_insiders_detection_empty_when_no_directories[linux] PASSED [ 56%]
tests/test_detection.py::test_vs_code_insiders_detection_empty_when_no_directories[darwin] PASSED [ 60%]
tests/test_detection.py::test_vs_code_insiders_detection_empty_when_no_directories[win32] PASSED [ 65%]
tests/test_detection.py::test_vs_code_get_command_dir_platform_specific[linux-.config/Code/User/prompts] PASSED [ 69%]
tests/test_detection.py::test_vs_code_get_command_dir_platform_specific[darwin-Library/Application Support/Code/User/prompts] PASSED [ 73%]
tests/test_detection.py::test_vs_code_get_command_dir_platform_specific[win32-AppData/Roaming/Code/User/prompts] PASSED [ 78%]
tests/test_detection.py::test_vs_code_insiders_get_command_dir_platform_specific[linux-.config/Code - Insiders/User/prompts] PASSED [ 82%]
tests/test_detection.py::test_vs_code_insiders_get_command_dir_platform_specific[darwin-Library/Application Support/Code - Insiders/User/prompts] PASSED [ 86%]
tests/test_detection.py::test_vs_code_insiders_get_command_dir_platform_specific[win32-AppData/Roaming/Code - Insiders/User/prompts] PASSED [ 91%]
tests/test_detection.py::test_vs_code_get_command_dir_fallback_to_default PASSED [ 95%]
tests/test_detection.py::test_vs_code_get_command_dir_unknown_platform_fallback PASSED [100%]

=========================== 23 passed in 0.02s ============================
```

### Verification

- ✅ All 23 detection tests pass (14 original + 9 new)
- ✅ No regressions in existing tests
- ✅ VS Code Insiders tests run alongside VS Code tests

## Summary

Task 2.0 successfully completed:

1. ✅ Three parametrized test functions added for VS Code Insiders
2. ✅ Detection tests cover all three platforms (linux, darwin, win32)
3. ✅ Tests verify detection works when directories exist
4. ✅ Tests verify no detection when directories don't exist
5. ✅ Tests verify get_command_dir() returns correct platform-specific paths
6. ✅ All tests use monkeypatch fixture to simulate different platforms
7. ✅ All 9 VS Code Insiders tests pass
8. ✅ No regressions in existing 14 detection tests
