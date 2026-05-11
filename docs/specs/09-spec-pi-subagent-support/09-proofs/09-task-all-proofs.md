# Task Proofs - Pi Subagent Support (Spec 09)

## Task Summary

This spec adds Pi as a fully supported agent in slash-command-manager. Three parent tasks were completed:

1. **Task 1.0** — Registered `CommandFormat.PI` enum value and Pi agent tuple in `_SUPPORTED_AGENT_DATA`
2. **Task 2.0** — Implemented `PiCommandGenerator` class with minimal YAML frontmatter (`description` + optional `argument-hint`), `$ARGUMENTS` preservation, and factory registration
3. **Task 3.0** — Added 7 Pi unit tests, updated integration test fixtures, and updated README + docs

## What This Proves

- Pi is registered as a discoverable agent (`--list-agents` shows it)
- `PiCommandGenerator` produces correct Pi-format files (only `description`/`argument-hint` in frontmatter, no `name`/`enabled`/`tags`/`arguments`/`meta`)
- `$ARGUMENTS` is preserved as-is in Pi output (Pi handles it natively)
- All 236 unit tests pass with no regressions
- Integration test fixtures include Pi for Docker-isolated testing

---

## Artifact: Pi appears in --list-agents

**What it proves:** Pi is registered in `_SUPPORTED_AGENT_DATA` and discoverable via CLI.

**Why it matters:** This is the primary user-facing proof that the agent is available.

**Command:**

```bash
uv run slash-man generate --list-agents
```

**Result summary:** Pi row appears in the agents table with `~/.pi/prompts` as the target directory.

```
│ pi               │ Pi               │ ~/.pi/prompts                                              │    ✗     │
```

---

## Artifact: Pi unit tests — 7/7 passing

**What it proves:** `PiCommandGenerator` correctly handles all required behaviors: basic generation, agent overrides, argument-hint, no-args omission, `$ARGUMENTS` preservation, snapshot regression, and factory dispatch.

**Why it matters:** These tests are the authoritative spec for Pi's output format.

**Command:**

```bash
uv run pytest tests/test_generators.py -v -m "not integration" -k pi
```

**Result summary:** All 7 Pi-specific tests pass.

```
tests/test_generators.py::test_pi_generator_basic_generation PASSED
tests/test_generators.py::test_pi_generator_applies_agent_overrides PASSED
tests/test_generators.py::test_pi_generator_argument_hint_with_args PASSED
tests/test_generators.py::test_pi_generator_no_argument_hint_when_no_args PASSED
tests/test_generators.py::test_pi_generator_preserves_arguments_placeholder PASSED
tests/test_generators.py::test_pi_generator_snapshot_regression PASSED
tests/test_generators.py::test_command_generator_factory_creates_pi_generator PASSED

7 passed, 20 deselected in 0.01s
```

---

## Artifact: Full unit test suite — 236/236 passing

**What it proves:** No regressions introduced by the Pi implementation.

**Why it matters:** Confirms all existing generators, config, and writer tests still pass.

**Command:**

```bash
uv run pytest tests/ -v -m "not integration"
```

**Result summary:** 236 passed, 35 deselected (integration tests skipped as expected).

```
====================== 236 passed, 35 deselected in 0.82s ======================
```

---

## Artifact: End-to-end Pi generation

**What it proves:** `PiCommandGenerator` produces correctly formatted files with only `description` and `argument-hint` in frontmatter.

**Why it matters:** Confirms Pi compatibility — no `name`, `enabled`, `tags`, `arguments`, or `meta` fields leak into the output.

**Command:**

```bash
uv run slash-man generate --agent pi --prompts-dir tests/integration/fixtures/prompts --target-path /tmp/pi-test --yes
cat /tmp/pi-test/.pi/prompts/test-prompt-1.md
```

**Result summary:** 3 files written to `.pi/prompts/`. Frontmatter contains only `description` and `argument-hint`.

```
---
description: First test prompt for integration testing
argument-hint: <input_arg>
---

# Test Prompt 1

This is the first test prompt file used for integration testing.
...
```

---

## Artifact: Documentation updated

**What it proves:** README and docs/slash-command-generator.md both list Pi.

**Why it matters:** User-facing and contributor-facing documentation is accurate.

- `README.md` "Supported AI Tools" section: `- **Pi**: Commands installed to ~/.pi/prompts`
- `docs/slash-command-generator.md` agents table: `| pi | Pi | Pi | .md | .pi/prompts | [Home](https://pi.ai/) |`

---

## Reviewer Conclusion

All three parent tasks are complete. Pi is fully registered, implemented, tested (7 unit tests + integration fixture updates), and documented. The full unit suite passes with no regressions. Integration tests include Pi in `test_generate_all_supported_agents` and will be verified via `uv run scripts/run_integration_tests.py` (Docker-isolated).
