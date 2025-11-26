# 07-spec-vs-code-macos-detection.md

## Introduction/Overview

Visual Studio Code stores user data and settings in platform-specific locations: `~/.config/Code` on Linux, `~/Library/Application Support/Code` on macOS, and `%APPDATA%\Code` on Windows. The current VS Code agent detection only checks for the Linux path, which causes detection to fail on macOS and Windows default installations. This spec implements cross-platform path detection and platform-specific command installation directories so slash commands work correctly regardless of the user's OS.

## Goals

- Add detection support for VS Code paths on macOS, Linux, and Windows
- Update command installation to use platform-specific directories for each OS
- Ensure backward compatibility without requiring migration of existing commands
- Provide comprehensive test coverage for all three platforms
- Maintain consistency with how other multi-platform agents (like Windsurf) handle path detection

## User Stories

- **As a macOS user**, I want the slash command manager to detect my VS Code installation in the standard macOS location so that I can generate and use slash commands without manual configuration.
- **As a Windows user**, I want the slash command manager to detect my VS Code installation in the standard Windows location so that I can use slash commands alongside other agents.
- **As a Linux user**, I want the slash command manager to continue detecting my VS Code installation in `~/.config/Code` so that existing configurations remain unaffected.
- **As a developer**, I want comprehensive test coverage for all platform paths so that cross-platform detection reliability is verified before releases.

## Demoable Units of Work

### Unit 1: Test Coverage for Cross-Platform VS Code Detection (TDD - Tests First)

**Purpose:** Create comprehensive test coverage that verifies VS Code detection works correctly on macOS, Linux, and Windows using mocked `sys.platform` and parametrized tests.

**Functional Requirements:**

- The system shall include unit tests with mocked `sys.platform` for macOS, Linux, and Windows detection directories
- The system shall verify detection returns empty list when no VS Code directories exist
- The system shall verify detection correctly identifies VS Code when platform-specific directories exist
- The system shall verify platform-specific paths are correctly resolved (not reversed or mixed)
- Tests shall parametrize across all three platforms using `@pytest.mark.parametrize()` with mocked `sys.platform`
- Tests shall not rely on actual filesystem operations; all paths are mocked via fixtures
- Tests shall verify `get_command_dir()` method returns correct platform-specific paths for each OS

**Proof Artifacts:**

- Test file: `tests/test_detection.py` includes new parametrized tests for platform-specific VS Code detection demonstrates test coverage
- Test output: `pytest tests/test_detection.py -v -k "vs_code"` shows all platform-specific tests passing demonstrates test execution
- Coverage report: `pytest tests/test_detection.py --cov=slash_commands.detection --cov-report=term-missing` shows test paths exercised demonstrates coverage
- Test failures: Initially failing tests (before implementation) demonstrate tests are written first, then code implements to pass

### Unit 2: Extend AgentConfig with Platform-Aware Command Directory Support (TDD - Implementation)

**Purpose:** Implement the `AgentConfig` dataclass extension to support platform-specific command directories, making tests from Unit 1 pass.

**Functional Requirements:**

- The system shall add optional `platform_command_dirs: dict[str, str] | None` field to `AgentConfig` dataclass
- The system shall implement `get_command_dir()` method that returns platform-appropriate path using `sys.platform`
- The system shall default to single `command_dir` for agents without `platform_command_dirs` (backward compatible)
- The method shall return correct paths: Linux `.config/Code/User/prompts`, macOS `Library/Application Support/Code/User/prompts`, Windows `AppData/Roaming/Code/User/prompts`
- Path handling shall use `pathlib.Path` for cross-platform compatibility

**Proof Artifacts:**

- Code diff: `slash_commands/config.py` shows `platform_command_dirs` field added to `AgentConfig` demonstrates field extension
- Code diff: `slash_commands/config.py` shows `get_command_dir()` method implementation demonstrates platform resolution logic
- Test output: `pytest tests/test_detection.py -v -k "vs_code"` shows all parametrized tests now passing demonstrates implementation correctness
- CLI: `python -c "from slash_commands.config import get_agent_config; import sys; cfg = get_agent_config('vs-code'); print(cfg.get_command_dir())"` returns platform-appropriate path demonstrates method works

### Unit 3: Update VS Code Agent Configuration with Multi-Platform Paths (TDD - Implementation)

**Purpose:** Update the VS Code agent configuration in `_SUPPORTED_AGENT_DATA` to detect all three platforms and install commands to platform-specific directories.

**Functional Requirements:**

- The system shall update VS Code agent `detection_dirs` tuple to include all three platform paths
- The system shall add `platform_command_dirs` dictionary mapping `sys.platform` values to command installation paths
- The system shall maintain existing detection order and priority from `SUPPORTED_AGENTS`
- The system shall continue supporting existing Linux installations without migration
- Detection directories: Linux `.config/Code`, macOS `Library/Application Support/Code`, Windows `AppData/Roaming/Code`
- Installation paths: Linux `.config/Code/User/prompts`, macOS `Library/Application Support/Code/User/prompts`, Windows `AppData/Roaming/Code/User/prompts`

**Proof Artifacts:**

- Code diff: `slash_commands/config.py` shows VS Code agent tuple updated with all three platform paths demonstrates configuration change
- CLI: `python -c "from slash_commands.config import get_agent_config; cfg = get_agent_config('vs-code'); print('Detection:', cfg.detection_dirs); print('Commands:', cfg.platform_command_dirs)"` shows all platform paths configured demonstrates configuration completeness
- Test output: `pytest tests/ -v` shows all tests passing including backward compatibility tests demonstrates no regressions

### Unit 4: Verify Cross-Platform Integration and Backward Compatibility

**Purpose:** Verify end-to-end that VS Code detection and command installation works across all platforms and that existing Linux installations remain unaffected.

**Functional Requirements:**

- The system shall detect VS Code on all three platforms when appropriate directories exist
- The system shall install commands to the correct platform-specific directory
- The system shall maintain backward compatibility with existing Linux installations
- All existing tests shall pass without modification or migration

**Proof Artifacts:**

- CLI: `slash-man generate --list-agents` succeeds and includes `vs-code` with correct display name demonstrates agent detection works end-to-end
- CLI: `slash-man generate --agent vs-code --dry-run` shows commands would install to correct platform-specific path demonstrates installation path resolution
- Test output: `pytest tests/ -v` shows all tests passing including existing tests demonstrates backward compatibility maintained
- Coverage: `pytest tests/ --cov=slash_commands --cov-report=term-missing` shows 100% coverage on modified code demonstrates comprehensive testing

## Non-Goals (Out of Scope)

1. **User migration tooling**: This spec does not include automatic migration of existing commands from `~/.config/Code/User/prompts` to platform-specific paths. Users on non-Linux platforms will need to manually regenerate commands after updating.
2. **VS Code settings sync**: This spec does not address VS Code's cloud settings sync functionality or how it interacts with command storage locations.
3. **Environment variable configuration**: This spec does not add support for user-configurable paths via environment variables; paths are platform-determined only.
4. **GitHub Actions/CI platform detection**: This spec focuses on user machines (macOS, Linux, Windows) and does not address CI environment-specific paths.

## Design Considerations

No specific UI/UX or visual design changes are required for this feature. The implementation is transparent to end users—they will simply see VS Code detected and commands installed to the correct location. The CLI output remains the same; only the underlying path logic changes.

## Repository Standards

Based on the codebase review and AGENTS.md:

- **Code style**: Follow existing Python conventions in `slash_commands/config.py` and `slash_commands/detection.py`
- **Data structures**: Use tuple-based configuration pattern from `_SUPPORTED_AGENT_DATA` in `config.py`
- **Testing**: Follow pytest patterns used in `tests/test_detection.py` with fixtures and parametrized tests
- **Test execution**:
  - Unit tests: `uv run pytest tests/ -v -m "not integration"` (excludes integration tests)
  - Integration tests: `uv run scripts/run_integration_tests.py` (ALWAYS use this script, NEVER run directly with pytest - runs in Docker to prevent overriding user prompt files)
- **Python execution**: ALWAYS use `uv run` prefix for all Python commands (e.g., `uv run pytest`, `uv run python -c`)
- **Path handling**: Use `pathlib.Path` for cross-platform compatibility (already used in `detection.py`)
- **Naming**: Use underscore-prefixed names for private functions (`_agent_configured`)
- **Type hints**: Include type annotations for all functions and parameters
- **Commit messages**: Follow Conventional Commits pattern (e.g., `fix(config): add cross-platform VS Code path support`)
- **Dependency management**: Use `uv sync` for installing/updating dependencies; never manually edit dependency files

## Technical Considerations

- **Platform detection**: Use `sys.platform` (not `platform.system()`) because it's determined at compile time with well-defined values: `'linux'`, `'darwin'` (macOS), and `'win32'` (Windows). This is faster and more reliable than runtime system calls.
- **Path resolution**: Windows paths use environment variable expansion (`%APPDATA%`) while Unix paths use tilde expansion (`~`). Python's `pathlib.Path` with `expanduser()` handles both automatically.
- **Detection directories**: Update the `detection_dirs` tuple in `AgentConfig` to include all three platform paths:
  - Linux: `.config/Code`
  - macOS: `Library/Application Support/Code`
  - Windows: `AppData/Roaming/Code`
- **Command directory logic**: Extend `AgentConfig` dataclass with platform-specific command directories:
  - Add optional `platform_command_dirs: dict[str, str]` field to map `sys.platform` values to command installation paths
  - Implement `get_command_dir()` method that returns the platform-appropriate path
  - VS Code config specifies all three paths; other agents continue using single `command_dir` (backward compatible)
- **Testing approach**: Mock `sys.platform` using `monkeypatch.setattr()` rather than filesystem operations. Use `@pytest.mark.parametrize()` to test all three platform paths in a single test run on any host OS. This enables comprehensive cross-platform testing without requiring multiple machines or OS-specific test runners.
- **Tilde and environment variable expansion**: Defer expansion to point-of-use (generation time) so that `~/` and `%APPDATA%` are resolved when commands are actually being generated, not during detection.

## Success Metrics

1. **Specification metric**: VS Code agent detects installations on all three platforms (macOS, Linux, Windows) with 100% accuracy in test environments
2. **Test coverage metric**: All new code paths have test coverage (minimum 100% for new functionality, maintain existing coverage levels)
3. **Backward compatibility metric**: Existing Linux installations continue to work without requiring migration or reconfiguration
4. **Cross-platform verification**: All platform paths tested on a single Linux host using parametrized tests with mocked `sys.platform`

## Open Questions

None at this time. All technical and scope decisions have been clarified.
