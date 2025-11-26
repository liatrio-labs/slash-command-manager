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

### [ ] 1.0 Write Parametrized Tests for Cross-Platform VS Code Detection (TDD Phase 1)

#### 1.0 Proof Artifact(s)

- Test file: `tests/test_detection.py` includes new test functions parametrized for Linux, macOS, Windows demonstrates test creation
- Test output: `uv run pytest tests/test_detection.py::test_vs_code_platform_detection -v` shows tests initially failing (red) before implementation demonstrates TDD approach
- Test output: `uv run pytest tests/test_detection.py -v -k "vs_code" -m "not integration"` shows test names and parametrization for all three platforms demonstrates comprehensive test coverage
- Code review: New test functions use `@pytest.mark.parametrize()` with mocked `sys.platform` and fixture-based path setup demonstrates proper testing approach

#### 1.0 Tasks

TBD

### [ ] 2.0 Write Test for get_command_dir() Method and Platform-Specific Paths (TDD Phase 1)

#### 2.0 Proof Artifact(s)

- Test file: `tests/test_detection.py` includes test function `test_vs_code_get_command_dir_platform_specific` parametrized for all three platforms demonstrates test coverage
- Test output: `uv run pytest tests/test_detection.py::test_vs_code_get_command_dir_platform_specific -v -m "not integration"` shows tests failing (red) because method doesn't exist yet demonstrates TDD-first approach
- Code review: Test uses `monkeypatch.setattr('sys.platform', platform_value)` to mock platform and verifies correct path returned for each platform demonstrates proper mocking approach

#### 2.0 Tasks

TBD

### [ ] 3.0 Implement AgentConfig.get_command_dir() Method (TDD Phase 2 - Implementation)

#### 3.0 Proof Artifact(s)

- Code diff: `slash_commands/config.py` shows `get_command_dir()` method added to `AgentConfig` class demonstrates method implementation
- Code diff: `slash_commands/config.py` shows method returns correct platform-specific path using `sys.platform` and `platform_command_dirs` dict demonstrates logic
- Test output: `uv run pytest tests/test_detection.py::test_vs_code_get_command_dir_platform_specific -v -m "not integration"` shows tests now passing (green) after implementation demonstrates test success
- Type checking: Method includes proper type hints and handles None case for agents without `platform_command_dirs` demonstrates robustness

#### 3.0 Tasks

TBD

### [ ] 4.0 Add platform_command_dirs Field to AgentConfig (TDD Phase 2 - Implementation)

#### 4.0 Proof Artifact(s)

- Code diff: `slash_commands/config.py` shows `platform_command_dirs: dict[str, str] | None = None` field added to `AgentConfig` dataclass demonstrates field addition
- Type checking: Dataclass properly annotates new field as optional demonstrates type safety
- Test output: `uv run pytest tests/test_detection.py -v -k "vs_code" -m "not integration"` shows detection tests still passing with new field demonstrates backward compatibility

#### 4.0 Tasks

TBD

### [ ] 5.0 Update VS Code Agent Configuration with Multi-Platform Paths (TDD Phase 2 - Implementation)

#### 5.0 Proof Artifact(s)

- Code diff: `slash_commands/config.py` line 36-42 shows VS Code agent tuple updated with all three `detection_dirs` demonstrates detection configuration
- Code diff: `slash_commands/config.py` shows new `platform_command_dirs` dict mapping `sys.platform` values to installation paths demonstrates command directory configuration
- Test output: `uv run pytest tests/test_detection.py -v -k "vs_code" -m "not integration"` shows all parametrized detection tests now passing demonstrates implementation correctness
- Test output: `uv run pytest tests/test_detection.py::test_vs_code_get_command_dir_platform_specific -v -m "not integration"` shows all platform-specific path tests passing demonstrates path resolution works

#### 5.0 Tasks

TBD

### [ ] 6.0 Verify Full Test Suite Passes and Backward Compatibility Maintained (Integration Verification)

#### 6.0 Proof Artifact(s)

- Test output: `uv run pytest tests/ -v -m "not integration"` shows all tests passing including new and existing tests demonstrates no regressions
- Coverage report: `uv run pytest tests/ --cov=slash_commands --cov-report=term-missing -m "not integration"` shows 100% coverage on modified code demonstrates comprehensive testing
- CLI: `uv run slash-man generate --list-agents` succeeds and includes `vs-code` demonstrates end-to-end functionality
- CLI: `uv run slash-man generate --agent vs-code --dry-run` shows commands would install to correct platform-specific directory demonstrates path resolution works correctly

#### 6.0 Tasks

TBD
