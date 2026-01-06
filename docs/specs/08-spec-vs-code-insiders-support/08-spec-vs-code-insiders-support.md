# 08-spec-vs-code-insiders-support.md

## Introduction/Overview

Add support for VS Code Insiders as an allowed agent in the slash command manager. This enables users running the Insiders (pre-release) edition of Visual Studio Code to generate and manage slash commands using the same workflow as the stable VS Code release. The implementation will mirror the existing VS Code support with appropriate path adjustments for the Insiders installation directories.

## Goals

1. Add VS Code Insiders as a fully supported agent with cross-platform compatibility (Linux, macOS, Windows)
2. Enable automatic detection of VS Code Insiders installations via configuration directory presence
3. Support independent operation alongside regular VS Code without conflicts or shared state
4. Maintain consistency with existing agent patterns and the regular VS Code implementation
5. Provide comprehensive test coverage matching the quality standards of spec 07 (VS Code regular)

## User Stories

**As a VS Code Insiders user**, I want to generate slash commands for my Insiders installation so that I can use the latest pre-release features with my custom prompts.

**As a developer running both VS Code and VS Code Insiders**, I want each installation to have independent prompt directories so that I can test different prompt configurations without conflicts.

**As a cross-platform user**, I want VS Code Insiders support to work on Linux, macOS, and Windows so that I have a consistent experience regardless of my operating system.

**As a CLI user**, I want VS Code Insiders to appear in `--list-agents` output so that I can discover and use it like any other supported agent.

## Demoable Units of Work

### Unit 1: VS Code Insiders Agent Configuration

**Purpose:** Add VS Code Insiders to the supported agents list with correct cross-platform paths and detection directories.

**Functional Requirements:**
- The system shall add a `vs-code-insiders` entry to `_SUPPORTED_AGENT_DATA` in `slash_commands/config.py`
- The system shall use display name "VS Code Insiders" for human-readable output
- The system shall use `.prompt.md` file extension matching regular VS Code
- The system shall configure platform-specific command directories:
  - Linux: `.config/Code - Insiders/User/prompts`
  - macOS: `Library/Application Support/Code - Insiders/User/prompts`
  - Windows: `AppData/Roaming/Code - Insiders/User/prompts`
- The system shall configure platform-specific detection directories:
  - Linux: `.config/Code - Insiders`
  - macOS: `Library/Application Support/Code - Insiders`
  - Windows: `AppData/Roaming/Code - Insiders`
- The agent configuration shall use `CommandFormat.MARKDOWN` format
- The configuration shall maintain alphabetical sorting in `SUPPORTED_AGENTS` tuple

**Proof Artifacts:**
- Code: Configuration entry in `slash_commands/config.py` demonstrates agent added to system
- CLI: `slash-man generate --list-agents` output includes "vs-code-insiders" demonstrates discoverability
- Test: Unit tests pass demonstrates configuration validity

### Unit 2: Cross-Platform Detection Tests

**Purpose:** Validate VS Code Insiders detection works correctly on all three platforms using the same TDD patterns as regular VS Code.

**Functional Requirements:**
- The system shall detect VS Code Insiders when any platform-specific detection directory exists
- The system shall return platform-appropriate command directories via `get_command_dir()` method
- The system shall not detect VS Code Insiders when no detection directories exist
- Tests shall use pytest parametrization for all three platforms (linux, darwin, win32)
- Tests shall use monkeypatch to simulate different platform environments
- Tests shall follow the naming and structure patterns from `tests/test_detection.py`

**Proof Artifacts:**
- Test: Parametrized detection tests for all platforms demonstrate cross-platform support
- Test: `get_command_dir()` tests verify correct platform-specific paths
- CLI: `uv run pytest tests/test_detection.py -v -k insiders` passes demonstrates detection logic works

### Unit 3: Integration Testing and Documentation

**Purpose:** Ensure end-to-end functionality works and all documentation reflects the new agent.

**Functional Requirements:**
- The integration test suite shall include `vs-code-insiders` in the list of tested agents
- The system shall successfully generate `.prompt.md` files in the correct Insiders directory
- The README.md shall list VS Code Insiders in the supported agents section
- The `docs/slash-command-generator.md` shall include VS Code Insiders in the agents table
- Integration tests shall run via `uv run scripts/run_integration_tests.py` in Docker
- Documentation shall note that VS Code and VS Code Insiders operate independently

**Proof Artifacts:**
- Test: `test_generate_all_supported_agents` includes and passes for `vs-code-insiders` demonstrates end-to-end functionality
- Documentation: README.md and slash-command-generator.md include VS Code Insiders demonstrates discoverability
- CLI: Generated file exists in correct Insiders directory (in test environment) demonstrates correct path resolution
- Test: All integration tests pass demonstrates no regressions
- **Note**: Actual VS Code Insiders installation not required - tests use mock directories and Docker isolation

## Non-Goals (Out of Scope)

1. **Shared prompt directories**: VS Code and VS Code Insiders will NOT share the same prompt directory - they remain completely independent
2. **Binary/executable detection**: Will NOT check for the presence of the VS Code Insiders executable, only configuration directories (consistent with other agents)
3. **Automatic migration**: Will NOT automatically copy prompts from regular VS Code to Insiders or vice versa
4. **Priority/preference system**: Will NOT implement any logic to prefer one over the other when both are installed
5. **Custom Insiders-specific features**: Will NOT add any features unique to Insiders beyond the standard slash command generation
6. **Backward compatibility concerns**: This is a new agent addition with no breaking changes to existing functionality

## Design Considerations

No specific design requirements identified. This is a backend configuration change with CLI output implications only. The UX follows existing patterns from the `--list-agents` and file generation flows.

## Repository Standards

Based on codebase review and AGENTS.md, implementation shall follow:

- **Code style**: PEP 8 guidelines, ruff for linting/formatting, 100 character line limit
- **Data structures**: Use tuple-based configuration pattern from `_SUPPORTED_AGENT_DATA` in `config.py`
- **Testing**: Follow pytest patterns from `tests/test_detection.py` with fixtures and parametrized tests
- **Type hints**: Include type annotations for functions and parameters
- **Path handling**: Use `pathlib.Path` for cross-platform compatibility at point-of-use
- **Naming**: Private variables prefixed with `_`, public methods use snake_case
- **Test execution**:
  - Unit tests: `uv run pytest tests/ -v -m "not integration"`
  - Integration tests: `uv run scripts/run_integration_tests.py` (NEVER run directly with pytest)
- **Python execution**: ALWAYS use `uv run` prefix for all Python commands
- **Commit messages**: Follow Conventional Commits (e.g., `feat(config): add VS Code Insiders agent support`)
- **Alphabetical ordering**: Maintain sorted order in `SUPPORTED_AGENTS` tuple by agent key

## Technical Considerations

**Implementation Approach:**
- Add new tuple entry to `_SUPPORTED_AGENT_DATA` following the exact structure of the `vs-code` entry
- The `_SORTED_AGENT_DATA` mechanism will automatically maintain alphabetical ordering
- Use the same `platform_command_dirs` dictionary pattern with `linux`, `darwin`, `win32` keys
- Leverage existing `get_command_dir()` method from spec 07 - no new methods needed

**Dependencies:**
- No new external dependencies required
- Relies on existing `AgentConfig` dataclass and `get_command_dir()` method from spec 07
- Detection logic in `slash_commands/detection.py` requires no modifications

**Testing Strategy:**
- Follow TDD workflow: write tests first, implement to make them pass, then refactor
- Mirror the test structure from `test_vs_code_detection_multiplatform()` and related VS Code tests
- Use monkeypatch for `sys.platform` to test all platforms without platform-specific test environments
- Integration tests will validate actual file generation in Docker environment

**File Modifications Required:**
- `slash_commands/config.py`: Add agent configuration tuple entry
- `tests/test_detection.py`: Add parametrized detection tests for VS Code Insiders
- `tests/integration/test_generate_command.py`: Add `vs-code-insiders` to agents list
- `README.md`: Add VS Code Insiders to supported agents list
- `docs/slash-command-generator.md`: Add VS Code Insiders to agents table

## Security Considerations

No specific security considerations identified. VS Code Insiders uses the same security model as regular VS Code:
- Prompts are stored in user-specific directories with standard file permissions
- No credentials or API keys are involved in this agent configuration
- Proof artifacts will be code and test output - no sensitive data

## Success Metrics

1. **Functionality**: `slash-man generate --agent vs-code-insiders` successfully creates `.prompt.md` files in the correct Insiders directory structure (verified in test environments)
2. **Test Coverage**: 100% of VS Code Insiders-related code paths covered by unit and integration tests (matching spec 07 coverage)
3. **Discoverability**: `slash-man generate --list-agents` displays VS Code Insiders with appropriate detection status
4. **No Regressions**: All existing tests continue to pass (unit + integration)
5. **Documentation**: VS Code Insiders appears in all relevant documentation with correct information

**Note**: Success does not require actual VS Code Insiders installation - all validation occurs via automated tests with mock directory structures.

## Open Questions

No open questions at this time. All requirements are clearly defined based on the regular VS Code implementation pattern.

---

## Next Steps

Once this specification is approved, run `/generate-task-list-from-spec` to create the TDD-driven task breakdown for implementation.
