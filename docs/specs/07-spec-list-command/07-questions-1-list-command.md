# 07 Questions Round 1 - List Command Feature

Please answer each question below (select one or more options, or add your own notes). Feel free to add additional context under any question.

## 1. Managed By Field Implementation

How should the `managed_by: slash-man` field be added to prompts?

1. **(a) Automatically added when `generate` command creates/updates a command file**
2. (b) Manually added to source prompt files in the prompts directory
3. (c) Both: automatically added to generated command files AND stored in source prompts
4. (d) Other (describe)

## 2. Managed By Field Value

What exact value should be used for the `managed_by` field?

1. **(a) `"slash-man"` (as mentioned)**
2. (b) `"slash-command-manager"` (full package name)
3. (c) `"scm"` (abbreviation)
4. (d) Configurable value (describe how)
5. (e) Other (specify)

## 3. List Command Output Format

What format should the `list` command output use?

1. **(a) Rich tree format similar to `generate` command summary**
2. (b) Simple table format (tabular)
3. (c) JSON output (with optional `--json` flag)
4. (d) Plain text list (one per line)
5. (e) Other (describe)

## 4. Information Displayed Per Prompt

What information should be shown for each managed prompt in the list?

1. (a) Prompt name, agent(s), file path(s), backup count
2. (b) Prompt name, agent(s), file path(s), backup count, last updated timestamp
3. **(c) Prompt name, agent(s), file path(s), backup count, source prompt path, last updated timestamp**
4. (d) All of the above (comprehensive view)
5. (e) Other (specify what fields)

## 5. Backup Counting

How should backup versions be counted?

1. **(a) Count all `.bak` files matching the pattern `{filename}.{timestamp}.bak` in the same directory**
2. (b) Count backups across all agent directories for the same prompt name
3. (c) Count backups per agent location (show backup count per agent)
4. (d) Show total backups plus breakdown by agent
5. (e) Other (describe)

## 6. Agent Filtering

Should the `list` command support filtering by agent?

1. **(a) Yes, support `--agent` flag (can specify multiple times) like `generate` command**
2. (b) Yes, support `--agent` flag but only show prompts for specified agents
3. (c) No, always show all managed prompts across all agents
4. (d) Other (describe)

## 7. Search Scope

Where should the `list` command search for managed prompts?

1. (a) Only in detected agent locations (same as `generate` uses for detection)
2. (b) All supported agent locations (check all possible locations, not just detected)
3. **(c) Configurable via `--target-path` and `--detection-path` flags (like `generate`)**
4. (d) Other (describe)

## 8. Empty State Handling

What should happen when no managed prompts are found?

1. **(a) Print message "No managed prompts found" and exit with code 0. Also include a note about how detection works for the case where there may be prompts that were installed by previous versions but don't have the new `managed_by` field so users know what to expect**
2. (b) Print message "No managed prompts found" and exit with code 1
3. (c) Print empty list/tree structure
4. (d) Other (describe)

## 9. Command Flags

What flags should the `list` command support?

1. **(a) `--target-path` / `-t` (like generate)**
2. **(b) `--detection-path` / `-d` (like generate)**
3. **(c) `--agent` / `-a` (filter by agent, like generate)**
4. (d) `--json` (output as JSON)
5. (e) All of the above
6. (f) Other (specify)

## 10. Backward Compatibility

How should we handle command files that were generated before `managed_by` field was added?

1. **(a) Only list prompts with `managed_by` field present**
2. (b) Include prompts without `managed_by` field but mark them differently
3. (c) Provide a migration command or flag to add `managed_by` to existing files
4. (d) Other (describe)

## 11. Grouping in Output

How should prompts be grouped in the output?

1. (a) Group by prompt name (show all agents for each prompt together)
2. (b) Group by agent (show all prompts for each agent together)
3. (c) Flat list (no grouping)
4. **(d) Other (describe): whatever matches with `generate` and involves the least code changes. i'd like to reuse/consolidate code from `generate` as much as possible**

## 12. Success Criteria & Proof Artifacts

How should we prove the feature works end-to-end?

1. (a) Unit tests for prompt discovery and filtering logic
2. (b) Integration tests demonstrating list output with various scenarios
3. (c) CLI transcript or screenshot showing list command output
4. (d) Tests for backup counting logic
5. **(e) All of the above**
6. (f) Other (describe)
