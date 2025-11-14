# 06 Questions Round 1 - CLI Safety Enhancements

Please answer each question below (select one or more options, or add your own notes). Feel free to add additional context under any question.

## 1. Scope Focus

Which items from `docs/specs/spec-notes.md` should this spec cover end-to-end?

1. (a) Only the backup-default behavior
2. (b) Backup defaults plus the `--yes` flag behavior
3. * (c) All items in the notes (backup defaults, `--yes` flag, no-source error, Rich output updates)
4. (d) Something else (describe)

## 2. Default Backup Behavior

When we "make backup the default," what actions should take backups automatically?

1. (a) Only interactive overwrite confirmations
2. * (b) All non-dry-run writes, regardless of interaction
3. (c) Only when a target file already exists
4. (d) Other (describe rules/conditions)

## 3. `--yes` Flag Expectations

If we force backups when `--yes` is used, do we still need an override to skip backups?

1. (a) No override—`--yes` always backs up existing files
2. (b) Provide a new explicit flag (e.g., `--overwrite`) to skip backups
3. (c) Allow an environment variable or config toggle to control this
4. * (d) Other (describe): the only time backups are not created is during the interactive flow when the user chooses the option to skip backups

## 4. No-Source-Prompts Error Handling

What behavior should occur when no prompts are found?

1. (a) Hard error with exit code 1 and concise message
2. * (b) Error plus actionable guidance (e.g., "check --prompts-dir or GitHub flags")
3. (c) Offer interactive retry/selection if running without `--yes`
4. (d) Other (describe)

## 5. Improved CLI Output with Rich

Which enhancements are required for the generate command output?

1. * (a) Show detected agents vs. selected agents in separate sections
2. * (b) Show accurate file counts (planned vs. actually written/backed up)
3. * (c) Indicate if backups were created and whether `--yes` was passed
4. * (d) Display YAML-like grouped structure exactly as in the notes
5. (e) Other formatting requirements (describe)

## 6. Success Criteria & Proof Artifacts

How should we prove the feature works end-to-end?

1. * (a) Unit tests covering backup defaults, `--yes`, and error cases
2. * (b) Integration tests demonstrating Rich output and backup files
3. * (c) CLI transcript or screenshot showing new output
4. (d) Other (describe)
