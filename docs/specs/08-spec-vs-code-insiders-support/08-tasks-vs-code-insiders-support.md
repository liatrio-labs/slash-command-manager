# 08-tasks-vs-code-insiders-support.md

## Relevant Files

- `slash_commands/config.py` - Contains `_SUPPORTED_AGENT_DATA` tuple where VS Code Insiders configuration must be added
- `tests/test_config.py` - Unit tests for configuration validation (existing tests should pass with new agent)
- `tests/test_detection.py` - Unit tests for agent detection; needs new parametrized tests for VS Code Insiders
- `tests/integration/test_generate_command.py` - Integration tests that validate end-to-end generation; needs `vs-code-insiders` added to agents list in `test_generate_all_supported_agents`
- `README.md` - User-facing documentation listing supported agents and their installation paths
- `docs/slash-command-generator.md` - Comprehensive agent documentation with detailed agent table and platform notes

### Notes

- Unit tests should be placed in `tests/` directory following existing pytest patterns
- Integration tests are located in `tests/integration/` and must be run via `uv run scripts/run_integration_tests.py` (NEVER directly with pytest)
- Use `uv run pytest tests/ -v -m "not integration"` for unit tests only
- [x] 1.1 Add VS Code Insiders tuple entry to `_SUPPORTED_AGENT_DATA` in `slash_commands/config.py` following the exact structure of the `vs-code` entry with updated paths (`Code - Insiders` instead of `Code`)
- [x] 1.2 Verify the configuration uses correct values: key=`vs-code-insiders`, display_name=`VS Code Insiders`, file_extension=`.prompt.md`, format=`CommandFormat.MARKDOWN`
- [x] 1.3 Set platform-specific command directories: Linux=`.config/Code - Insiders/User/prompts`, macOS=`Library/Application Support/Code - Insiders/User/prompts`, Windows=`AppData/Roaming/Code - Insiders/User/prompts`
- [x] 1.4 Set detection directories tuple: `.config/Code - Insiders`, `Library/Application Support/Code - Insiders`, `AppData/Roaming/Code - Insiders`
- [x] 1.5 Run `uv run pytest tests/test_config.py -v` to verify configuration is valid and no regressions introducedollow pytest parametrization patterns from existing VS Code tests in `test_detection.py`
- Maintain alphabetical ordering in `_SUPPORTED_AGENT_DATA` (automatic via `_SORTED_AGENT_DATA` mechanism)
- Use `sys.platform` values: `linux`, `darwin`, `win32` for platform detection
- Follow repository's PEP 8 style guidelines with 100 character line limit
- All Python execution must use `uv run` prefix

## Tasks

### [x] 1.0 Add VS Code Insiders Agent Configuration

- [x] 2.1 Add parametrized test `test_vs_code_insiders_detection_multiplatform` to `tests/test_detection.py` that tests detection on linux, darwin, and win32 platforms (mirror existing `test_vs_code_detection_multiplatform`)
- [x] 2.2 Add parametrized test `test_vs_code_insiders_detection_empty_when_no_directories` to verify VS Code Insiders is not detected when directories don't exist
- [x] 2.3 Add parametrized test `test_vs_code_insiders_get_command_dir_platform_specific` to verify `get_command_dir()` returns correct platform-specific paths for linux, darwin, and win32
- [x] 2.4 Use `monkeypatch` fixture to simulate different `sys.platform` values in tests
- [x] 2.5 Run `uv run pytest tests/test_detection.py -v -k insiders` to verify all VS Code Insiders tests pass
- [x] 2.6 Run `uv run pytest tests/test_detection.py -v` to ensure no regressions in existing detection tests VS Code Insiders to the supported agents list in `slash_commands/config.py` with cross-platform path support following the exact pattern used for regular VS Code.

#### 1.0 Proof Artifact(s)

- Code: New agent configuration entry in `slash_commands/config.py` demonstrates VS Code Insiders added to system
- CLI: `uv run slash-man generate --list-agents` output includes "vs-code-insiders" demonstrates discoverability
- Test: `uv run pytest tests/test_config.py -v` passes demonstrates configuration validity

#### 1.0 Tasks

TBD

### [x] 2.0 Implement Cross-Platform Detection Tests

Create comprehensive unit tests for VS Code Insiders detection across all platforms (Linux, macOS, Windows) using pytest parametrization and the same TDD patterns as regular VS Code.

#### 2.0 Proof Artifact(s)

- Test: `uv run pytest tests/test_detection.py -v -k insiders` passes demonstrates detection logic works for all platforms
- Test: Parametrized tests cover linux, darwin, and win32 platforms demonstrates cross-platform support
- Test: `get_command_dir()` tests verify platform-specific paths demonstrates correct path resolution

#### 2.0 Tasks

TBD

### [x] 3.0 Add Integration Tests and Validate End-to-End Functionality

Extend integration test suite to include VS Code Insiders in the list of agents validated during Docker-isolated tests, ensuring end-to-end file generation works correctly.
- [x] 3.1 Add `"vs-code-insiders"` to the agents list in `test_generate_all_supported_agents` function in `tests/integration/test_generate_command.py`
- [x] 3.2 Ensure the agent is added in alphabetical order within the list (should be after `"vs-code"`)
- [x] 3.3 Run `uv run scripts/run_integration_tests.py` to execute all integration tests in Docker environment
- [x] 3.4 Verify integration test output shows successful file generation for vs-code-insiders
- [x] 3.5 Confirm no test failures or regressions in existing integration tests
#### 3.0 Proof Artifact(s)

- Test: `uv run scripts/run_integration_tests.py` passes demonstrates no regressions
- Test: `test_generate_all_supported_agents` includes `vs-code-insiders` demonstrates integration testing coverage
- Log: Integration test output shows successful file generation for vs-code-insiders demonstrates end-to-end functionality

#### 3.0 Tasks

TBD

- [x] 4.1 Update `README.md` to add VS Code Insiders to the platform-specific directories section (near line 191 where VS Code is mentioned)
- [x] 4.2 Add VS Code Insiders entry to the agents table in `docs/slash-command-generator.md` (after the `vs-code` row around line 197)
- [x] 4.3 Include VS Code Insiders platform-specific path information in the documentation notes section (mirror the VS Code note pattern)
- [x] 4.4 Verify documentation mentions that VS Code and VS Code Insiders operate independently with separate prompt directories
- [x] 4.5 Review all documentation changes for consistency, accuracy, and proper markdown formatting [ ] 4.0 Update Documentation

Update all user-facing documentation to include VS Code Insiders as a supported agent, ensuring users can discover and use the new agent through documentation.

#### 4.0 Proof Artifact(s)

- Documentation: README.md includes VS Code Insiders in supported agents list demonstrates user discoverability
- Documentation: `docs/slash-command-generator.md` agents table includes vs-code-insiders entry demonstrates comprehensive documentation
- Documentation: Platform-specific path notes mention VS Code Insiders demonstrates installation guidance
- Diff: Documentation changes show VS Code Insiders added alongside VS Code demonstrates consistency

#### 4.0 Tasks

TBD
