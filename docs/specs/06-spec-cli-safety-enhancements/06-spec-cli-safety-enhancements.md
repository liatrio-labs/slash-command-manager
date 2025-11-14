# 06-spec-cli-safety-enhancements

## Introduction/Overview

This feature hardens the `slash-man generate` experience by making backups the default for all real writes, ensuring the `--yes` path never overwrites without recovery, surfacing clear failures when no prompts exist, and upgrading the CLI summary output with Rich for better situational awareness. Together, these changes prevent accidental data loss and make generation results easier to audit.

## Goals

- Always create timestamped backups for any non-dry-run write unless the user explicitly skips backups during interactive confirmation.
- Ensure the `--yes` shortcut follows the safest path (backups + confirmation of non-interactive state) with no silent overwrites.
- Fail fast when zero prompts are discovered and guide users toward corrective actions.
- Present an accurate, visually grouped Rich summary showing detected vs selected agents, file counts, backup status, and relevant flags.
- Capture automated and manual proof artifacts (tests + transcript) that demonstrate the new behavior.

## User Stories

- **As a CLI user running unattended automation**, I want the `--yes` path to create backups before overwriting so that I can recover previous commands if something goes wrong.
- **As a prompt maintainer**, I want an explicit error when no prompts are found so that I can correct my flags instead of assuming success.
- **As a developer reviewing generate output**, I want a Rich-formatted summary that highlights selected agents, file counts, and backup status so that I can quickly assess what happened.

## Demoable Units of Work

### [Unit 1]: Backup-First File Writes

**Purpose:** Guarantee every non-dry-run write path produces `.bak` files before overwriting, regardless of prompt source or agent.
**Demo Criteria:** Running `slash-man generate --yes --agents claude-code` on existing files shows backup files with timestamp suffixes, and file content matches expectations.
**Proof Artifacts:** Pytest unit tests covering writer logic; integration test verifying backup files exist; CLI transcript snippet of `ls` output showing `.bak` files.

### [Unit 2]: `--yes` Safety & Interactive Overrides

**Purpose:** Ensure `--yes` always behaves as “safe non-interactive mode” while still allowing interactive sessions to skip backups explicitly.
**Demo Criteria:** Automated test proves `--yes` sets overwrite action to backup; interactive session demonstrates backup skip only when user picks the “skip backups” option.
**Proof Artifacts:** Unit tests validating flag handling; integration test (or recorded CLI session) showing interactive choice prevents backups only when selected.

### [Unit 3]: No-Source Prompt Guardrails

**Purpose:** Detect when prompt discovery returns zero files and return a helpful error.
**Demo Criteria:** Running `slash-man generate --prompts-dir /tmp/empty` exits with code 1 and emits actionable guidance referencing `--prompts-dir` or GitHub flags.
**Proof Artifacts:** Unit/integration test asserting error message; CLI transcript showing stderr/stdout text.

### [Unit 4]: Rich Output Enhancements

**Purpose:** Replace the plain-text summary with a Rich-rendered YAML-like structure that separates detected vs selected agents and shows accurate file metrics and backup indicators.
**Demo Criteria:** Dry-run and real-run outputs display the new structure, including `--yes` indicator and counts of planned/written/backed-up files.
**Proof Artifacts:** Snapshot/CLI transcript or screenshot of terminal output; integration test verifying structured data feeding Rich table/tree.

## Functional Requirements

1. **The system shall create backups for every non-dry-run file write** by default, generating files that follow the existing `filename.ext.YYYYMMDD-HHMMSS.bak` pattern whenever a target already exists.
2. **The system shall ensure the `--yes` flag forces backup behavior** and shall never overwrite without backup when running non-interactively.
3. **The system shall only skip backups when the interactive user explicitly selects “skip backups,”** leaving all other flows (including config/env-controlled runs) in backup mode.
4. **The system shall detect when zero prompts are found** across local directories or GitHub sources and exit with a non-zero status plus actionable guidance.
5. **The system shall render Rich-formatted output** that includes (at minimum):
   - Separate sections for detected vs selected agents
   - Accurate counts of files planned, written, and backed up
   - Indicators showing whether backups occurred and if `--yes` was passed
   - YAML-like grouped file listings such as:

     ```yaml
     Files:
       - claude-code:
         Agent: Claude Code
         Files:
           - /home/damien/.claude/commands/generate-spec.md
           - /home/damien/.claude/commands/generate-task-list-from-spec.md
           - /home/damien/.claude/commands/manage-tasks.md
           - /home/damien/.claude/commands/validate-spec-implementation.md
       - cursor:
         Agent: Cursor
         Files:
           - /home/damien/.cursor/commands/generate-spec.md
           - /home/damien/.cursor/commands/generate-task-list-from-spec.md
           - /home/damien/.cursor/commands/manage-tasks.md
           - /home/damien/.cursor/commands/validate-spec-implementation.md
     ```

6. **The system shall provide automated test coverage** (unit + integration) demonstrating the behaviors above and shall capture at least one CLI transcript/screenshot artifact of the new output.

## Non-Goals (Out of Scope)

1. **Introducing new prompt sources or agent types**—scope is limited to safety/error/output improvements for existing flows.
2. **Changing cleanup or MCP commands**—only the `generate` command behavior is affected.
3. **Implementing configurable backup storage locations**—backups continue to live alongside generated files with the existing naming pattern.

## Design Considerations

- Use Rich components (Tree/Table/Text) to mimic the YAML-style structure from the notes while preserving readability in standard terminals.
- Preserve current CLI messaging tone; add new sections without removing core success counts users rely on.
- Ensure backup indicators and counts remain accurate in dry-run mode (e.g., clearly label “would create” vs “created”).
- No separate UI mockups are required beyond aligning with the provided YAML example.

## Repository Standards

- Follow the established Python style enforced by `ruff format` and `ruff check`.
- Place tests under `tests/` (unit logic near current file-writer tests, integration tests under `tests/integration/`), mirroring the structure used in previous specs.
- Update documentation/spec artifacts inside `docs/specs/` and provide proofs similar to prior specs (e.g., `05-proofs/` patterns).
- Use conventional commits and ensure `pre-commit run --all-files` succeeds before submission.
- Execute the implementation with strict TDD: write failing tests first, implement only enough code to make them pass, and iterate until all acceptance criteria are covered.

## Technical Considerations

- Centralize backup creation in the file-writing layer so both interactive and non-interactive flows share the same safety defaults.
- Inject Rich rendering at the summary step after generation completes; consider emitting structured data (dict/list) first, then passing to Rich to ease testing.
- Ensure prompt discovery functions return counts that can be reused both for error handling (zero case) and for the Rich summary metrics.
- Guard error exits so they still produce Rich context (e.g., show zero files section plus guidance) without masking the non-zero exit code.
- Maintain compatibility with existing logging/telemetry; avoid introducing dependencies beyond Rich (already used elsewhere) unless approved.

## Success Metrics

1. **Backup Coverage:** 100% of overwrite scenarios (non-dry-run) generate `.bak` files unless the interactive user opted out.
2. **Prompt Guardrail:** Zero-prompt situations consistently exit with code 1 and an actionable message, verified via automated test.
3. **Output Adoption:** Rich summary appears for 100% of generate runs, showing accurate counts (validated by integration snapshot test and manual transcript).

## Open Questions

No open questions at this time.
