# 09-tasks-pi-subagent-support.md

## Relevant Files

| File | Why It Is Relevant |
| --- | --- |
| `slash_commands/config.py` | Add `CommandFormat.PI` enum value and Pi tuple to `_SUPPORTED_AGENT_DATA`. |
| `slash_commands/generators.py` | Implement `PiCommandGenerator` class and register it in `CommandGenerator.create()`. |
| `tests/test_config.py` | Update `test_command_format_defines_markdown_toml_and_kiro`, `test_supported_agents_have_valid_command_formats`, and `test_detection_dirs_cover_command_directory_roots` to include Pi. |
| `tests/test_generators.py` | Add Pi generator unit tests (basic generation, description overrides, argument-hint, no-args omission, metadata exclusion, snapshot regression). |
| `tests/integration/conftest.py` | Add `.pi` to the `clean_agent_dirs` fixture's `agent_dirs` list. |
| `tests/integration/test_generate_command.py` | Add `"pi"` to the `agents` list in `test_generate_all_supported_agents`. |
| `README.md` | Add Pi to the "Supported AI Tools" bullet list. |
| `docs/slash-command-generator.md` | Add `pi` row to the Supported Agents table. |

### Notes

- Unit tests live alongside source in `tests/` (e.g., `tests/test_generators.py`).
- Run unit tests with: `uv run pytest tests/ -v -m "not integration"`
- Run integration tests with: `uv run scripts/run_integration_tests.py` (Docker-isolated — never run directly with pytest)
- Follow existing code patterns in `slash_commands/` — new generator class mirrors `KiroCommandGenerator` structure.
- Conventional Commits: `feat(pi): ...`

## Tasks

### [x] 1.0 Register Pi Agent and Add `CommandFormat.PI` Enum Value

**Purpose:** Make Pi a recognized agent in the system — registered in `_SUPPORTED_AGENT_DATA`, enumerated in `CommandFormat`, and listable via `--list-agents`.

#### 1.0 Proof Artifact(s)

- CLI: `uv run slash-man generate --list-agents` output includes `pi` demonstrates agent is registered and discoverable
- CLI: `uv run slash-man generate --agent pi --dry-run --target-path /tmp/pi-test` in a directory with `.pi/` demonstrates detection and selection work without writing files
- Test: `uv run pytest tests/test_config.py -v -m "not integration"` passes (including updated `test_command_format_defines_markdown_toml_and_kiro` and `test_supported_agents_have_valid_command_formats`) demonstrates structural invariants hold for the new agent

#### 1.0 Tasks

- [ ] 1.1 In `slash_commands/config.py`, add `PI = "pi"` to the `CommandFormat` enum (after `KIRO_IDE`).
- [ ] 1.2 In `slash_commands/config.py`, add the Pi 7-element tuple to `_SUPPORTED_AGENT_DATA`:
  ```python
  ("pi", "Pi", ".pi/prompts", CommandFormat.PI, ".md", (".pi",), None)
  ```
  The tuple will be sorted alphabetically at runtime by `_SORTED_AGENT_DATA`, so insertion order does not matter.
- [ ] 1.3 In `tests/test_config.py`, update `test_command_format_defines_markdown_toml_and_kiro` to assert `CommandFormat.PI.value == "pi"` and add `"pi"` to the expected `{member.value for member in CommandFormat}` set. Rename the test to `test_command_format_defines_all_formats` if desired for clarity.
- [ ] 1.4 In `tests/test_config.py`, update `test_supported_agents_have_valid_command_formats` to add `CommandFormat.PI` to the `valid_formats` set.
- [ ] 1.5 Run `uv run pytest tests/test_config.py -v -m "not integration"` and confirm all tests pass.

---

### [x] 2.0 Implement `PiCommandGenerator`

**Purpose:** Produce correctly formatted Pi prompt template files — YAML frontmatter with only `description` (and optionally `argument-hint`) — and register it in the `CommandGenerator.create()` factory.

#### 2.0 Proof Artifact(s)

- Test: `uv run pytest tests/test_generators.py -v -m "not integration" -k pi` passes with all Pi generator tests demonstrates correct output format
- CLI: Generated `.pi/prompts/*.md` files contain only `description` (and optionally `argument-hint`) in frontmatter and no `name`, `enabled`, `tags`, `arguments`, or `meta` fields demonstrates Pi compatibility
- CLI: `uv run slash-man generate --agent pi --prompts-dir <local-prompts-dir> --target-path /tmp/pi-test --yes` exits 0 and creates files in `/tmp/pi-test/.pi/prompts/` demonstrates end-to-end generation works

#### 2.0 Tasks

- [ ] 2.1 In `slash_commands/generators.py`, implement the `PiCommandGenerator` class after `KiroIdeCommandGenerator`. The class must implement `CommandGeneratorProtocol` with a `generate(self, prompt, agent, source_metadata=None) -> str` method.
- [ ] 2.2 In `PiCommandGenerator.generate()`, call `_apply_agent_overrides(prompt, agent)` to get `description` and `arguments` (discard `enabled`).
- [ ] 2.3 Build the frontmatter dict with only `description`. Do **not** include `name`, `enabled`, `tags`, `arguments`, or `meta`.
- [ ] 2.4 If `arguments` is non-empty, compute the `argument-hint` string: join argument names space-separated, wrapping required args in `<name>` and optional args in `[name]` (e.g., `<url> [options]`). Add `argument-hint` to the frontmatter dict.
- [ ] 2.5 Pass the prompt body through `_replace_placeholders(prompt.body, arguments, replace_double_braces=False)` — this preserves `$ARGUMENTS` as-is (Pi natively supports it) while still processing any `{{args}}` if present.
- [ ] 2.6 Format the output as `---\n<yaml_frontmatter>---\n\n<body>\n` using `yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False)`, then call `_normalize_output(output)` before returning.
- [ ] 2.7 In `CommandGenerator.create()`, add an `elif format == CommandFormat.PI: return PiCommandGenerator()` branch before the final `else` raise.
- [ ] 2.8 Run `uv run pytest tests/test_generators.py -v -m "not integration"` and confirm existing tests still pass (no regressions).

---

### [x] 3.0 Tests and Documentation

**Purpose:** Ensure Pi support is fully tested (unit + integration) and documented in README and generator docs.

#### 3.0 Proof Artifact(s)

- Test: `uv run pytest tests/ -v -m "not integration"` passes with all Pi unit tests (including `test_config.py` structural invariant updates) demonstrates unit test coverage
- Test: `uv run scripts/run_integration_tests.py` passes with Pi included in `test_generate_all_supported_agents` agent list demonstrates integration test coverage
- Docs: `README.md` "Supported AI Tools" section lists Pi with `.pi/prompts` command directory demonstrates user-facing documentation is accurate
- Docs: `docs/slash-command-generator.md` agents table includes a `pi` row demonstrates contributor-facing documentation is accurate

#### 3.0 Tasks

- [ ] 3.1 In `tests/test_generators.py`, add the following Pi unit tests (import `PiCommandGenerator` at the top of the file alongside the other generator imports):
  - `test_pi_generator_basic_generation(sample_prompt)` — assert frontmatter contains `description`, does NOT contain `name`, `enabled`, `tags`, `arguments`, or `meta`, and body is present.
  - `test_pi_generator_applies_agent_overrides(sample_prompt)` — add a `pi` override to the `sample_prompt` fixture inline (or use a new fixture), assert the overridden description appears in frontmatter.
  - `test_pi_generator_argument_hint_with_args(prompt_with_placeholder_body)` — assert `argument-hint` is present in frontmatter and equals `"<query> [format]"` (required arg in `<>`, optional in `[]`).
  - `test_pi_generator_no_argument_hint_when_no_args(sample_prompt_no_args)` — use a prompt with no arguments; assert `argument-hint` is absent from frontmatter. (Create a minimal `sample_prompt_no_args` fixture in the test file if one doesn't exist.)
  - `test_pi_generator_preserves_arguments_placeholder(prompt_with_placeholder_body)` — assert `$ARGUMENTS` is still present in the generated body (Pi handles it natively).
  - `test_pi_generator_snapshot_regression(sample_prompt)` — assert output starts with `---\n`, contains `\n---\n`, ends with `\n`, has no trailing whitespace per line, and has LF-only line endings.
  - `test_command_generator_factory_creates_pi_generator()` — call `CommandGenerator.create(CommandFormat.PI)` and assert the returned object is an instance of `PiCommandGenerator`. (Import `CommandGenerator` and `CommandFormat` from `slash_commands.generators` and `slash_commands.config` respectively.)
- [ ] 3.2 In `tests/integration/conftest.py`, add `".pi"` to the `agent_dirs` list in the `clean_agent_dirs` fixture.
- [ ] 3.3 In `tests/integration/test_generate_command.py`, add `"pi"` to the `agents` list in `test_generate_all_supported_agents`.
- [ ] 3.4 Run `uv run pytest tests/ -v -m "not integration"` and confirm all unit tests pass.
- [ ] 3.5 In `README.md`, add a Pi bullet to the "Supported AI Tools" list (after the Kiro IDE bullet):
  ```
  - **Pi**: Commands installed to `~/.pi/prompts`
  ```
- [ ] 3.6 In `docs/slash-command-generator.md`, add a `pi` row to the Supported Agents table (the table is alphabetically sorted — insert between `opencode` and `vs-code`):
  ```
  | `pi` | Pi | Pi | `.md` | `.pi/prompts` | [Home](https://github.com/mariozechner/pi-coding-agent) |
  ```
- [ ] 3.7 Run `uv run scripts/run_integration_tests.py` and confirm all integration tests pass including the Pi agent.
