## Relevant Files

- `slash_commands/cli.py` – CLI entry point managing `generate` flags, `--yes` handling, and summary output wiring.
- `slash_commands/writer.py` – Core writer responsible for prompt loading, overwrite policy, backup creation, and result metadata.
- `slash_commands/generators.py` – Provides command generators; may need tweaks if metadata for Rich summary changes.
- `slash_commands/github_utils.py` – Downloads prompts from GitHub; required for zero-prompt guardrails covering remote sources.
- `tests/test_writer.py` – Existing unit tests for writer behavior and backup logic.
- `tests/test_cli.py` – Covers CLI flag handling, output summaries, and user interactions.
- `tests/integration/test_prompt_discovery.py` – Integration coverage for prompt discovery workflows; extend for zero prompts.
- `tests/integration/test_generate_output.py` – Ideal home for Rich summary snapshot/smoke tests.
- `tests/conftest.py` – Shared fixtures (temporary directories, CLI helpers) supporting new tests.
- `Dockerfile` – Defines the container image used for manual demos/proofs without touching the host filesystem.

## Tasks

> **Execution Note:** Run every manual demo, CLI proof, and artifact capture inside the project’s Docker test container (e.g., `docker run --rm slash-man-test …`) so local files remain untouched.

### [x] 1.0 Enforce Backup-First Writes Across Generators

#### 1.0 Demo Criteria

- Inside the Docker test container, run `slash-man generate --agents claude-code --yes` against seeded files and show `.bak` files created before overwrites.
- Containerized dry-run output clearly states that backups *would* be created without touching the filesystem.
- Acceptance: File diffs confirm only backed-up copies precede updates.

#### 1.0 Proof Artifact(s)

- CLI: `slash-man generate --agents claude-code --yes --prompts-dir tests/fixtures/prompts` (captured stdout/stderr showing backup messaging).
- Test: `tests/unit/test_file_writer.py::test_backup_default`.
- File listing snippet (e.g., `ls -l ~/.claude/commands`) showing `.bak` suffixes.

#### 1.0 Tasks

- [x] 1.1 Add failing unit tests in `tests/test_writer.py` that expect non-dry-run writes (including `--yes`) to call `create_backup` before overwriting and to record paths in `backups_created`.
- [x] 1.2 Add failing CLI/dry-run tests (e.g., in `tests/test_cli.py`) asserting the output explicitly states backups *would* be created even when no files are touched.
- [x] 1.3 Update `slash_commands/writer.py` to make backups the default overwrite action (unless interactive skip selected), ensure dry-run metadata exposes pending backups, and keep logic TDD-aligned by only writing code needed for the new tests.
- [x] 1.4 Propagate backup counts/paths into the CLI summary payload so later Rich rendering can display them accurately.
- [x] 1.5 From inside the Docker test container, run `slash-man generate --agents claude-code --yes` against seeded prompts to capture proof of `.bak` creation plus corresponding `ls -l` output.

### [x] 2.0 Align `--yes` and Interactive Choices With Safety Policy

#### 2.0 Demo Criteria

- Automated test demonstrates `--yes` forces `backup` overwrite action and never `overwrite`.
- Interactive recording shows user selecting “skip backups” and confirms it is the only path without backups.
- Acceptance: CLI logs indicate `--yes` mode flagged as non-interactive and mentions backups explicitly.

#### 2.0 Proof Artifact(s)

- Test: `tests/unit/test_cli_flags.py::test_yes_flag_sets_backup_action`.
- Integration test log (pytest + pexpect) showing simulated interactive menu selection leading to the skip-backups branch.
- Screenshot/snippet of help text if updated to mention safety behavior, captured from inside the Docker container.

#### 2.0 Tasks

- [x] 2.1 Create failing tests in `tests/test_cli.py` (and/or a new `tests/test_cli_flags.py`) to assert `--yes` always injects the `backup` action and surfaces a “non-interactive safe mode” indicator.
- [x] 2.2 Add a pexpect-driven integration test (Docker-compatible) that walks the interactive overwrite prompt, selects “skip backups,” and verifies it is the only route that avoids backups.
- [x] 2.3 Update `slash_commands/cli.py` flag handling so `--yes` sets `overwrite_action="backup"` while interactive flows continue to honor user choices; include new help text describing the safety policy.
- [x] 2.4 Ensure questionary menu options label the skip-backups path clearly and log the selection for auditability.
- [x] 2.5 Capture containerized CLI help/output demonstrating the updated messaging for proof artifacts (no local file changes).

### [x] 3.0 Guard Against Missing Prompts With Actionable Errors

#### 3.0 Demo Criteria

- Inside the Docker test container, running `slash-man generate --prompts-dir /tmp/empty` exits 1 with guidance referencing prompts/GitHub flags.
- Integration test covers both local and GitHub discovery returning zero prompts.
- Acceptance: Error output also appears in Rich summary block (if applicable) without masking exit status.

#### 3.0 Proof Artifact(s)

- Test: `tests/integration/test_prompt_discovery.py::test_zero_prompts_errors`.
- Containerized CLI capture (stdout/stderr) showing actionable message and exit code snippet.
- Log excerpt (if applicable) verifying structured error logging.

#### 3.0 Tasks

- [x] 3.1 Add failing tests in `tests/integration/test_prompt_discovery.py` (and GitHub-focused fixtures) that expect a zero-prompt run to exit with code 1 and actionable messaging.
- [x] 3.2 Extend `slash_commands/writer.py` (or discovery helpers) to raise a descriptive exception when no prompts are loaded, including hints about `--prompts-dir` and GitHub flags; wire this into the CLI error pathway.
- [x] 3.3 Update the Rich summary builder to surface the zero-prompt condition (e.g., show `Prompts loaded: 0` plus guidance) without suppressing the failing exit code.
- [x] 3.4 Execute the empty-dir scenario inside the Docker container to capture stderr/stdout proving the guidance text and non-zero exit status.

### [x] 4.0 Deliver Rich YAML-Style Summary With Accurate Metrics

#### 4.0 Demo Criteria

- Containerized dry-run and real-run outputs render the Rich YAML-style tree from the spec, showing detected vs selected agents, file counts, backup indicators, and `--yes` status.
- Snapshot test (text or Rich console capture) passes, proving stable structure.
- Acceptance: Manual transcript/screenshot included in proofs.

#### 4.0 Proof Artifact(s)

- Test: `tests/integration/test_generate_output.py::test_rich_summary_structure`.
- Containerized CLI screenshot or text capture of Rich output for both dry-run and real run.
- Artifact: Stored Rich snapshot fixture for regression detection.

#### 4.0 Tasks

- [x] 4.1 Draft snapshot-focused tests (unit or integration) that describe the target Rich YAML tree (detected vs selected agents, file counts, backup indicators, `--yes` flag visibility).
- [x] 4.2 Implement a dedicated summary builder (e.g., helper in `slash_commands/cli.py`) that produces structured data which the Rich Tree/Table renders; ensure data shape matches tests before coding the Rich output.
- [x] 4.3 Add tests verifying counts stay accurate for dry-run vs real run and that backup indicators reflect the new metadata from Task 1.0.
- [x] 4.4 Generate and store Rich snapshot artifacts/fixtures for regression checks (e.g., using `pytest-approvaltests` style or string compare).
- [x] 4.5 Capture both dry-run and real-run Rich output from the Docker container (screenshots or text logs) for inclusion in proofs.
