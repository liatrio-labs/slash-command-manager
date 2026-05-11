# 09-spec-pi-subagent-support.md

## Introduction/Overview

The slash-command-manager currently supports 11 AI coding assistants but does not support Pi (`@mariozechner/pi-coding-agent`), a terminal-based AI coding agent. This spec adds Pi as a supported agent so that `slash-man generate` produces correctly formatted prompt template files in `.pi/prompts/`. Pi uses a minimal frontmatter format (only `description` and `argument-hint`) that differs significantly from the existing Markdown generator output, requiring a new `CommandFormat.PI` enum value and a dedicated `PiCommandGenerator`.

## Goals

- Register Pi as a supported agent in the static agent configuration
- Implement a `PiCommandGenerator` that produces Pi-compatible prompt template files with only `description` and `argument-hint` frontmatter fields
- Auto-detect Pi projects via the `.pi/` directory
- Ensure all existing tests pass and new tests cover Pi-specific behavior
- Update documentation to list Pi as a supported tool

## User Stories

- **As a developer using Pi**, I want to run `slash-man generate --agent pi` so that my shared prompt files are converted into Pi-compatible prompt templates in `.pi/prompts/`.
- **As a developer using multiple AI tools**, I want Pi to appear in `slash-man generate --list-agents` and be auto-detected when `.pi/` exists, so that my workflow is consistent across all my coding assistants.
- **As a developer writing prompts**, I want Pi's generated files to contain only the frontmatter fields Pi understands (`description` and `argument-hint`), so that Pi doesn't encounter unexpected metadata.

## Demoable Units of Work

### Unit 1: Agent Registration and Detection

**Purpose:** Make Pi a recognized agent that can be selected and auto-detected by the CLI.

**Functional Requirements:**
- The system shall include a `"pi"` entry in `_SUPPORTED_AGENT_DATA` with key `"pi"`, display name `"Pi"`, command directory `.pi/prompts`, format `CommandFormat.PI`, extension `.md`, and detection directories `(".pi",)`
- The system shall add a `PI` value to the `CommandFormat` enum
- The system shall detect Pi when a `.pi/` directory exists in the target project directory
- The system shall list `"pi"` in the output of `slash-man generate --list-agents`

**Proof Artifacts:**
- CLI: `slash-man generate --list-agents` output includes `pi` demonstrates agent is registered
- CLI: `slash-man generate --agent pi --dry-run` in a directory with `.pi/` demonstrates detection and selection work

### Unit 2: Pi Command Generator

**Purpose:** Generate correctly formatted Pi prompt template files that contain only the frontmatter fields Pi supports.

**Functional Requirements:**
- The system shall implement a `PiCommandGenerator` class that conforms to `CommandGeneratorProtocol`
- The generator shall produce YAML frontmatter containing only `description` (from the source prompt's description, with agent overrides applied)
- The generator shall include `argument-hint` in frontmatter when the source prompt defines arguments, formatted as a space-separated string of argument names in angle brackets for required args and square brackets for optional args (e.g., `<url> [options]`)
- The generator shall omit `argument-hint` from frontmatter when the source prompt has no arguments
- The generator shall not include `name`, `enabled`, `tags`, `arguments`, or `meta` fields in the frontmatter
- The generator shall preserve `$ARGUMENTS` placeholders in the body without replacement, since Pi natively supports this syntax
- The `CommandGenerator.create()` factory shall map `CommandFormat.PI` to `PiCommandGenerator`

**Proof Artifacts:**
- Test: `test_generators.py` Pi generator tests pass demonstrates correct output format
- CLI: Generated `.pi/prompts/*.md` files contain only `description` and optionally `argument-hint` in frontmatter demonstrates Pi compatibility

### Unit 3: Tests and Documentation

**Purpose:** Ensure Pi support is fully tested and documented for users and contributors.

**Functional Requirements:**
- The system shall include unit tests for `PiCommandGenerator` covering: basic generation, description from overrides, argument-hint generation, omission of argument-hint when no arguments, and source metadata exclusion from frontmatter
- The system shall include Pi in the integration test `test_generate_all_supported_agents` agent list
- The system shall include Pi's detection directory in the `clean_agent_dirs` integration test fixture
- The system shall update structural invariant tests in `test_config.py` if Pi has any special detection directory patterns
- The system shall document Pi in the README.md "Supported AI Tools" section
- The system shall document Pi in the `docs/slash-command-generator.md` agents table

**Proof Artifacts:**
- Test: `uv run pytest tests/ -v -m "not integration"` passes with Pi tests demonstrates unit test coverage
- Test: `uv run scripts/run_integration_tests.py` passes with Pi in the agent list demonstrates integration test coverage
- Docs: README.md lists Pi with `.pi/prompts` command directory demonstrates user-facing documentation

## Non-Goals (Out of Scope)

1. **Pi Skills support**: Pi has a separate Skills system (`.pi/skills/`) using the Agent Skills standard. This spec only covers Prompt Templates (the slash command equivalent).
2. **Global prompt directory**: Pi supports `~/.pi/agent/prompts/` for global templates. This spec targets project-local `.pi/prompts/` only, consistent with how other agents are handled.
3. **Pi-specific argument placeholder conversion**: Pi uses `$1`, `$2`, `${@:N}` syntax natively. No conversion from other placeholder formats is in scope.
4. **Pi settings.json generation**: No generation of Pi configuration files beyond prompt templates.

## Design Considerations

No specific design requirements identified. Pi is a terminal-based tool with no UI components relevant to this integration.

## Repository Standards

Implementation should follow these established patterns:

- **Agent registration**: Add a 7-element tuple to `_SUPPORTED_AGENT_DATA` in `config.py`, sorted alphabetically by key at runtime
- **Generator pattern**: New generator class implementing `CommandGeneratorProtocol` with a `generate()` method, registered in `CommandGenerator.create()` factory
- **Enum convention**: New `CommandFormat` values use UPPER_SNAKE_CASE (e.g., `PI`)
- **Test conventions**: Unit tests in `tests/test_*.py`, integration tests in `tests/integration/`, run via `uv run pytest` and `uv run scripts/run_integration_tests.py` respectively
- **Documentation**: Update both `README.md` (user-facing) and `docs/slash-command-generator.md` (contributor-facing)
- **Commit style**: Conventional Commits (`feat(pi): ...`)

## Technical Considerations

- **New `CommandFormat.PI` enum value**: Pi's frontmatter is too different from the existing `MARKDOWN` format (which produces `name`, `description`, `tags`, `enabled`, `arguments`, `meta`) to reuse `MarkdownCommandGenerator`. A dedicated format and generator follows the precedent set by Kiro (which also got its own format despite being markdown-based).
- **`argument-hint` mapping**: The source `MarkdownPrompt.arguments` list (structured `PromptArgumentSpec` objects) needs to be flattened into a single display string. Convention: `<name>` for required args, `[name]` for optional args, space-separated.
- **`$ARGUMENTS` placeholder preservation**: Pi natively supports `$ARGUMENTS` in template bodies. The generator should pass through body content with `_replace_placeholders()` configured to preserve `$ARGUMENTS` (similar to how `KiroCommandGenerator` handles placeholders).
- **No `meta` section**: Unlike other markdown generators, `PiCommandGenerator` should not emit source tracking metadata in frontmatter since Pi doesn't support arbitrary frontmatter fields.

## Security Considerations

No specific security considerations identified. Pi prompt templates contain no credentials or sensitive data. The generator produces plain markdown files with minimal frontmatter.

## Success Metrics

1. **Feature completeness**: `slash-man generate --agent pi` produces valid Pi prompt template files that work when invoked as `/commandname` in Pi
2. **Test coverage**: All new Pi-related unit and integration tests pass
3. **Zero regression**: All existing tests for the 11 currently supported agents continue to pass
4. **Documentation accuracy**: Pi appears in all agent listing surfaces (CLI `--list-agents`, README, generator docs)

## Open Questions

1. **`argument-hint` format preference**: Should the `argument-hint` string use the exact argument names from the source prompt (e.g., `<url> [options]`), or should it use a generic format (e.g., `<arguments>`)?  Current spec proposes using source argument names for maximum clarity.
2. **Body placeholder handling**: Should `$1`/`$2` positional placeholders be generated from the source prompt's argument list, or should only `$ARGUMENTS` be preserved as-is? Current spec proposes preserving existing placeholders without conversion.
