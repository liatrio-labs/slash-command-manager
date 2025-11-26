# 07 Tasks - VS Code macOS Detection Fix

## Relevant Files

- `slash_commands/config.py` - AgentConfig dataclass and VS Code agent configuration tuple; will need `platform_command_dirs` field addition
- `slash_commands/detection.py` - Detection logic using `iter_detection_dirs()`; may need minor updates to leverage new field
- `tests/test_detection.py` - Existing detection tests; will be extended with platform-specific test cases
- `README.md` - Documentation showing supported agents and install paths; will need updating for cross-platform clarity

### Notes

- VS Code agent config is located in `_SUPPORTED_AGENT_DATA` tuple (line 36-42 in config.py)
- Windsurf agent (line 54-60) provides precedent for multiple detection directories
- Detection tests use pytest parametrization and fixtures; extend using same pattern with mocked `sys.platform`
- All path handling uses `pathlib.Path` with `expanduser()` for cross-platform compatibility
- Use `sys.platform` values: `'linux'`, `'darwin'` (macOS), `'win32'` (Windows)
- **ALWAYS use `uv run` prefix for all Python commands** (e.g., `uv run pytest`, `uv run python -c`)
- Run unit tests with: `uv run pytest tests/ -v -m "not integration"`
- Run integration tests ONLY through: `uv run scripts/run_integration_tests.py` (never directly with pytest - runs in Docker)

## Tasks

### [x] 1.0 Write Parametrized Tests for Cross-Platform VS Code Detection (TDD Phase 1)

#### 1.0 Proof Artifact(s)

- Test file: `tests/test_detection.py` includes new test functions parametrized for Linux, macOS, Windows demonstrates test creation
- Test output: `uv run pytest tests/test_detection.py::test_vs_code_platform_detection -v` shows tests initially failing (red) before implementation demonstrates TDD approach
- Test output: `uv run pytest tests/test_detection.py -v -k "vs_code" -m "not integration"` shows test names and parametrization for all three platforms demonstrates comprehensive test coverage
- Code review: New test functions use `@pytest.mark.parametrize()` with mocked `sys.platform` and fixture-based path setup demonstrates proper testing approach

#### 1.0 Tasks

- [ ] 1.1 Create parametrized test function `test_vs_code_detection_multiplatform` in `tests/test_detection.py`
  - Use `@pytest.mark.parametrize()` with three cases: `('linux', '.config/Code')`, `('darwin', 'Library/Application Support/Code')`, `('win32', 'AppData/Roaming/Code')`
  - Mock `sys.platform` using `monkeypatch.setattr('sys.platform', platform_value)`
  - Create temporary VS Code directory in `tmp_path` at the platform-appropriate path
  - Call `detect_agents(tmp_path)` and verify VS Code agent is detected in returned list
  - This test will initially fail (RED phase) because `AgentConfig` doesn't yet have all three detection paths

- [ ] 1.2 Create parametrized test function `test_vs_code_detection_empty_when_no_directories` in `tests/test_detection.py`
  - Use `@pytest.mark.parametrize()` with three platform values: `'linux'`, `'darwin'`, `'win32'`
  - Mock `sys.platform` for each platform
  - Pass empty `tmp_path` (no VS Code directories created)
  - Call `detect_agents(tmp_path)` and verify returns empty list or list without vs-code agent
  - Ensures detection correctly returns nothing when paths don't exist on each platform

- [ ] 1.3 Run new tests to confirm they fail (RED phase)
  - Execute: `uv run pytest tests/test_detection.py::test_vs_code_detection_multiplatform -v -m "not integration"`
  - Verify tests show FAILED status and error about missing detection paths
  - Execute: `uv run pytest tests/test_detection.py::test_vs_code_detection_empty_when_no_directories -v -m "not integration"`
  - Verify tests pass (they should, since detection returns empty on empty paths regardless of platform)

### [x] 2.0 Write Test for get_command_dir() Method and Platform-Specific Paths (TDD Phase 1)

#### 2.0 Proof Artifact(s)

- Test file: `tests/test_detection.py` includes test function `test_vs_code_get_command_dir_platform_specific` parametrized for all three platforms demonstrates test coverage
- Test output: `uv run pytest tests/test_detection.py::test_vs_code_get_command_dir_platform_specific -v -m "not integration"` shows tests failing (red) because method doesn't exist yet demonstrates TDD-first approach
- Code review: Test uses `monkeypatch.setattr('sys.platform', platform_value)` to mock platform and verifies correct path returned for each platform demonstrates proper mocking approach

#### 2.0 Tasks

- [ ] 2.1 Create parametrized test function `test_vs_code_get_command_dir_platform_specific` in `tests/test_detection.py`
  - Use `@pytest.mark.parametrize()` with data: `[('linux', '.config/Code/User/prompts'), ('darwin', 'Library/Application Support/Code/User/prompts'), ('win32', 'AppData/Roaming/Code/User/prompts')]`
  - Mock `sys.platform` using `monkeypatch.setattr('sys.platform', platform_value)`
  - Get VS Code agent config: `vs_code_agent = get_agent_config('vs-code')`
  - Call `vs_code_agent.get_command_dir()` and verify it returns the expected path for the mocked platform
  - This test will initially fail (RED) because `get_command_dir()` method doesn't exist yet

- [ ] 2.2 Create test function `test_vs_code_get_command_dir_fallback_to_default` in `tests/test_detection.py`
  - Create a mock agent config without `platform_command_dirs` field (or with None value)
  - Verify `get_command_dir()` returns the single `command_dir` value, not failing on None
  - Ensures backward compatibility for agents that don't use platform-specific paths

- [ ] 2.3 Run get_command_dir() tests to confirm they fail (RED phase)
  - Execute: `uv run pytest tests/test_detection.py::test_vs_code_get_command_dir_platform_specific -v -m "not integration"`
  - Verify tests fail with AttributeError (method doesn't exist)
  - Execute: `uv run pytest tests/test_detection.py::test_vs_code_get_command_dir_fallback_to_default -v -m "not integration"`
  - Verify test also fails

### [x] 3.0 Implement AgentConfig.get_command_dir() Method (TDD Phase 2 - Implementation)

#### 3.0 Proof Artifact(s)

- Code diff: `slash_commands/config.py` shows `get_command_dir()` method added to `AgentConfig` class demonstrates method implementation
- Code diff: `slash_commands/config.py` shows method returns correct platform-specific path using `sys.platform` and `platform_command_dirs` dict demonstrates logic
- Test output: `uv run pytest tests/test_detection.py::test_vs_code_get_command_dir_platform_specific -v -m "not integration"` shows tests now passing (green) after implementation demonstrates test success
- Type checking: Method includes proper type hints and handles None case for agents without `platform_command_dirs` demonstrates robustness

#### 3.0 Tasks

- [ ] 3.1 Add `platform_command_dirs: dict[str, str] | None = None` field to `AgentConfig` dataclass in `slash_commands/config.py`
  - Update the frozen dataclass field list to include the new optional field
  - Maintain alphabetical or logical ordering with other fields
  - Update the `AgentConfig` creation in the tuple comprehension to pass `platform_command_dirs=None` for all existing agents

- [ ] 3.2 Implement `get_command_dir(self) -> str` method in `AgentConfig` class in `slash_commands/config.py`
  - Method logic: if `self.platform_command_dirs` is not None, use `sys.platform` to look up platform-specific path; otherwise return `self.command_dir`
  - Import `sys` at the top of config.py if not already imported
  - Add proper type hints: `from typing import ...` (if needed)
  - Example implementation structure:

    ```python
    def get_command_dir(self) -> str:
        if self.platform_command_dirs is not None:
            return self.platform_command_dirs.get(sys.platform, self.command_dir)
        return self.command_dir
    ```

- [ ] 3.3 Run get_command_dir() tests again to verify they now pass (GREEN phase)
  - Execute: `uv run pytest tests/test_detection.py::test_vs_code_get_command_dir_platform_specific -v -m "not integration"`
  - Verify all parametrized test cases pass (green)
  - Execute: `uv run pytest tests/test_detection.py::test_vs_code_get_command_dir_fallback_to_default -v -m "not integration"`
  - Verify fallback test passes

### [x] 4.0 Add platform_command_dirs Field to AgentConfig (TDD Phase 2 - Implementation)

#### 4.0 Proof Artifact(s)

- Code diff: `slash_commands/config.py` shows `platform_command_dirs: dict[str, str] | None = None` field added to `AgentConfig` dataclass demonstrates field addition
- Type checking: Dataclass properly annotates new field as optional demonstrates type safety
- Test output: `uv run pytest tests/test_detection.py -v -k "vs_code" -m "not integration"` shows detection tests still passing with new field demonstrates backward compatibility

#### 4.0 Tasks

- [ ] 4.1 Verify dataclass field addition doesn't break existing tests
  - Execute: `uv run pytest tests/test_detection.py -v -m "not integration"`
  - Verify all existing detection tests pass with new field present
  - Confirm no changes needed to `iter_detection_dirs()` method (it should still work as-is)

- [ ] 4.2 Commit progress after field addition
  - Stage changes to `slash_commands/config.py`
  - Create commit: `test(config): add platform_command_dirs field and get_command_dir() method`
  - This marks completion of core implementation infrastructure

### [x] 5.0 Update VS Code Agent Configuration with Multi-Platform Paths (TDD Phase 2 - Implementation)

#### 5.0 Proof Artifact(s)

- Code diff: `slash_commands/config.py` line 36-42 shows VS Code agent tuple updated with all three `detection_dirs` demonstrates detection configuration
- Code diff: `slash_commands/config.py` shows new `platform_command_dirs` dict mapping `sys.platform` values to installation paths demonstrates command directory configuration
- Test output: `uv run pytest tests/test_detection.py -v -k "vs_code" -m "not integration"` shows all parametrized detection tests now passing demonstrates implementation correctness
- Test output: `uv run pytest tests/test_detection.py::test_vs_code_get_command_dir_platform_specific -v -m "not integration"` shows all platform-specific path tests passing demonstrates path resolution works

#### 5.0 Tasks

- [ ] 5.1 Update VS Code agent entry in `_SUPPORTED_AGENT_DATA` tuple in `slash_commands/config.py`
  - Locate VS Code agent tuple (currently around line 36-42)
  - Update `detection_dirs` from `(".config/Code",)` to `(".config/Code", "Library/Application Support/Code", "AppData/Roaming/Code")`
  - Add new `platform_command_dirs` dict parameter mapping platforms to command install paths:

    ```python
    {
        'linux': '.config/Code/User/prompts',
        'darwin': 'Library/Application Support/Code/User/prompts',
        'win32': 'AppData/Roaming/Code/User/prompts'
    }
    ```

- [ ] 5.2 Update tuple unpacking in `AgentConfig` creation to handle new platform_command_dirs parameter
  - Locate the tuple comprehension that creates AgentConfig instances
  - Add `platform_command_dirs=platform_command_dirs` (or appropriate variable name) to the AgentConfig() call
  - Ensure all agents except VS Code pass `platform_command_dirs=None`

- [ ] 5.3 Run detection tests to verify all detection paths now work (GREEN phase)
  - Execute: `uv run pytest tests/test_detection.py::test_vs_code_detection_multiplatform -v -m "not integration"`
  - Verify all three platform parametrization cases now pass (previously failing)
  - Execute: `uv run pytest tests/test_detection.py -v -k "vs_code" -m "not integration"`
  - Verify all VS Code related tests pass

- [ ] 5.4 Commit configuration changes
  - Stage changes to `slash_commands/config.py`
  - Create commit: `feat(config): add multi-platform detection and installation paths for VS Code`
  - Include proof of passing tests in commit message

### [x] 6.0 Verify Full Test Suite Passes and Backward Compatibility Maintained (Integration Verification)

#### 6.0 Proof Artifact(s)

- Test output: `uv run pytest tests/ -v -m "not integration"` shows all tests passing including new and existing tests demonstrates no regressions
- Coverage report: `uv run pytest tests/ --cov=slash_commands --cov-report=term-missing -m "not integration"` shows 100% coverage on modified code demonstrates comprehensive testing
- CLI: `uv run slash-man generate --list-agents` succeeds and includes `vs-code` demonstrates end-to-end functionality
- CLI: `uv run slash-man generate --agent vs-code --dry-run` shows commands would install to correct platform-specific directory demonstrates path resolution works correctly

#### 6.0 Tasks

- [ ] 6.1 Run full test suite to verify no regressions
  - Execute: `uv run pytest tests/ -v -m "not integration"`
  - Verify all tests pass (new and existing)
  - Verify no skipped or error tests

- [ ] 6.2 Generate and verify coverage report
  - Execute: `uv run pytest tests/ --cov=slash_commands --cov-report=term-missing -m "not integration"`
  - Verify coverage shows 100% on `config.py` changes
  - Verify coverage shows 100% on `detection.py` (or no changes if detection logic unchanged)
  - Document coverage numbers for proof artifact

- [ ] 6.3 Test end-to-end CLI functionality
  - Execute: `uv run slash-man generate --list-agents`
  - Verify output shows "VS Code" agent is detected and listed
  - Execute: `uv run slash-man generate --agent vs-code --dry-run`
  - Verify dry-run shows commands would be installed to platform-appropriate directory
  - Capture CLI output for proof artifacts

- [ ] 6.4 Verify backward compatibility with existing agents
  - Execute: `uv run slash-man generate --agent claude-code --dry-run`
  - Verify Claude Code agent still works correctly
  - Execute: `uv run slash-man generate --agent cursor --dry-run`
  - Verify Cursor agent still works correctly
  - Confirm other agents unaffected by changes

- [ ] 6.5 Final cleanup and documentation commit
  - Review all changes for any leftover debug statements or comments
  - Ensure all code follows repository style guidelines
  - Create final commit: `fix(config): finalize VS Code cross-platform detection implementation`
  - Include all proof artifacts in commit message (test output, coverage, CLI verification)
