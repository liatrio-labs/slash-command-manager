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

### Unit 1: Cross-Platform Path Detection

**Purpose:** Enable the VS Code agent to detect VS Code installations on macOS, Linux, and Windows by checking for platform-specific configuration directories.

**Functional Requirements:**

- The system shall detect VS Code on Linux when `~/.config/Code` exists
- The system shall detect VS Code on macOS when `~/Library/Application Support/Code` exists
- The system shall detect VS Code on Windows when `%APPDATA%\Code` exists (or equivalent path resolution on Windows)
- The system shall maintain the existing detection order and priority defined in `SUPPORTED_AGENTS`
- The detection logic shall use Python's `pathlib.Path` for cross-platform path handling

**Proof Artifacts:**

- Code change: Updated `config.py` AgentConfig for `vs-code` with multi-platform detection directories demonstrates platform-aware path detection
- Test output: `test_detection.py` passing tests for macOS, Linux, and Windows paths demonstrate detection works across all platforms
- CLI output: `slash-man generate --list-agents` successfully detects VS Code on each platform (verified in isolated test environments)

### Unit 2: Platform-Specific Command Installation

**Purpose:** Update the VS Code agent configuration to install generated commands in the correct platform-specific directory for command storage and retrieval.

**Functional Requirements:**

- The system shall install commands to `~/.config/Code/User/prompts` on Linux
- The system shall install commands to `~/Library/Application Support/Code/User/prompts` on macOS
- The system shall install commands to `%APPDATA%\Code\User\prompts` on Windows (or equivalent resolved path)
- The installation directory shall match the detected configuration directory structure for each platform
- The system shall use the appropriate path separator for each platform (forward slash on Unix, backslash on Windows)

**Proof Artifacts:**

- Code change: Updated `config.py` `command_dir` field (or new platform-aware logic) for `vs-code` agent demonstrates correct installation paths
- Test output: Unit tests verifying path construction for each platform demonstrate correct path resolution
- Integration test: Commands successfully generated and installed to correct platform-specific directories demonstrate end-to-end functionality

### Unit 3: Test Coverage for All Platforms

**Purpose:** Add comprehensive test coverage to verify VS Code detection and installation work correctly on all three supported platforms.

**Functional Requirements:**

- The system shall include unit tests with mocked filesystem paths for macOS, Linux, and Windows detection directories
- The system shall verify detection returns empty list when no VS Code directories exist
- The system shall verify detection correctly identifies VS Code when platform-specific directories exist
- The system shall verify platform-specific paths are correctly resolved (not reversed or mixed)
- Existing tests in `test_detection.py` shall be updated to include Windows and macOS paths alongside Linux paths
- Integration tests shall validate actual filesystem operations for each platform (in isolated test environments)

**Proof Artifacts:**

- Test file: `tests/test_detection.py` updated with platform-specific test cases demonstrates comprehensive coverage
- Test output: `pytest` run shows all platform-specific tests passing demonstrates correctness
- Coverage report: Coverage metrics show all new code paths exercised demonstrates test adequacy

## Non-Goals (Out of Scope)

1. **User migration tooling**: This spec does not include automatic migration of existing commands from `~/.config/Code/User/prompts` to platform-specific paths. Users on non-Linux platforms will need to manually regenerate commands after updating.
2. **VS Code settings sync**: This spec does not address VS Code's cloud settings sync functionality or how it interacts with command storage locations.
3. **Environment variable configuration**: This spec does not add support for user-configurable paths via environment variables; paths are platform-determined only.
4. **GitHub Actions/CI platform detection**: This spec focuses on user machines (macOS, Linux, Windows) and does not address CI environment-specific paths.

## Design Considerations

No specific UI/UX or visual design changes are required for this feature. The implementation is transparent to end users—they will simply see VS Code detected and commands installed to the correct location. The CLI output remains the same; only the underlying path logic changes.

## Repository Standards

Based on the codebase review:

- **Code style**: Follow existing Python conventions in `slash_commands/config.py` and `slash_commands/detection.py`
- **Data structures**: Use tuple-based configuration pattern from `_SUPPORTED_AGENT_DATA` in `config.py`
- **Testing**: Follow pytest patterns used in `tests/test_detection.py` with fixtures and parametrized tests
- **Path handling**: Use `pathlib.Path` for cross-platform compatibility (already used in `detection.py`)
- **Naming**: Use underscore-prefixed names for private functions (`_agent_configured`)
- **Type hints**: Include type annotations for all functions and parameters
- **Commit messages**: Follow Conventional Commits pattern (e.g., `fix(config): add cross-platform VS Code path support`)

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
