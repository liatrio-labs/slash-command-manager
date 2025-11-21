# 08 Questions Round 1 - List All Files Flag Feature

Please answer each question below (select one or more options, or add your own notes). Feel free to add additional context under any question.

## 1. Flag Name and Behavior

What should the new flag be named and what exactly should it list?

- [x] (a) `--all-files` - Lists ALL files in agent command directories (including managed, unmanaged, backups, and any other files)
- [ ] (b) `--show-all` - Lists all files but excludes backup files
- [ ] (c) `--verbose` - Shows additional file-level details for each managed prompt
- [ ] (d) `--list-files` - Lists all files found in prompt directories (clarify what "prompt directories" means)
- [ ] (e) Other (describe)

## 2. File Scope

What files should be included when the flag is used?

- [x] (a) All files in agent command directories (managed prompts, unmanaged prompts, backup files, and any other files)
- [ ] (b) All valid prompt files (managed + unmanaged, excluding backups and invalid files)
- [ ] (c) All files matching the agent's command_file_extension (e.g., `*.md` for Cursor, `*.toml` for Gemini)
- [ ] (d) Only files that can be parsed as prompts (valid frontmatter/TOML structure)
- [ ] (e) Other (describe)

## 3. Output Format

How should the files be displayed when using this flag?

- [ ] (a) Modify existing tree output to show all files - Add a new section showing all files per agent directory
- [ ] (b) Replace tree output with a simple list of file paths (one per line)
- [ ] (c) Show files grouped by agent directory with counts
- [x] (d) Show files in a table format with columns: Type (managed/unmanaged/backup/invalid), File Path (relative to agent directory)
  - show each agent folder as a separate table. show a summary of the agent folder above the table with info like agent name, agent prompt folder, file count in prompt folder, etc.

- [ ] (e) Other (describe)

## 4. File Classification

Should files be classified/categorized in the output?

- [x] (a) Yes, show file type - Mark each file as "managed", "unmanaged", "backup", or "other". sort the files in this order first, then by filename
- [ ] (b) Yes, show status indicators - Use symbols or colors (✓ for managed, ⚠ for unmanaged, etc.)
- [ ] (c) No, just list file paths - Simple list without classification
- [ ] (d) Group by type - Show separate sections for managed, unmanaged, backups, etc.
- [ ] (e) Other (describe)

## 5. Integration with Existing Output

How should this flag interact with the existing `list` command output?

- [ ] (a) Add a new section - Keep existing managed prompts tree, add a new "All Files" section below
- [x] (b) Replace output entirely - When flag is used, show only the file list (no managed prompts tree)
- [ ] (c) Show both views - Display managed prompts tree first, then all files list
- [ ] (d) Make it mutually exclusive - Flag changes behavior completely (no managed prompts shown)
- [ ] (e) Other (describe)

## 6. Backup File Handling

How should backup files be handled?

- [x] (a) Include all backup files - Show all `.bak` files matching the backup pattern
- [ ] (b) Include but mark separately - Show backups but clearly indicate they are backups
- [ ] (c) Exclude backup files - Don't show backup files at all
- [ ] (d) Show backup count only - Don't list individual backups, just show count per command file
- [ ] (e) Other (describe)

## 7. File Path Display

How should file paths be displayed?

- [ ] (a) Full absolute paths - Show complete file paths
- [x] (b) Relative to target-path - Show paths relative to the `--target-path` directory for each agent
- [ ] (c) Relative to home directory - Show paths relative to `~`
- [ ] (d) Just filename - Show only the filename
- [ ] (e) Other (describe)

## 8. Grouping and Organization

How should files be organized in the output?

- [ ] (a) Group by agent - Show all files for each agent together
- [ ] (b) Group by file type - Group managed, unmanaged, backups separately
- [x] (c) Group by agent, then by type - Show agents, then within each agent show files by type
- [ ] (d) Flat list - Simple list of all files, no grouping
- [ ] (e) Other (describe)

## 9. Empty State

What should happen when no files are found?

- [ ] (a) Show message "No files found" - Similar to current empty state handling
- [ ] (b) Show message with directory paths searched - Include which directories were checked
- [ ] (c) Exit silently with code 0 - No output if no files found
- [x] (d) Show directory structure - Show that directories exist but are empty. if directory doesn't exist, note that
- [ ] (e) Other (describe)

## 10. Filtering and Flags

Should the new flag work with existing filtering flags?

- [x] (a) Yes, respect all existing flags - `--agent`, `--target-path`, `--detection-path` all work with the new flag
- [ ] (b) Yes, but some flags may not apply - Some flags might not make sense with file listing
- [ ] (c) No, flag is standalone - When used, ignores other filtering flags
- [ ] (d) Other (describe)

## 11. Performance Considerations

Are there any performance concerns with listing all files?

- [x] (a) No special handling needed - Current approach is fine
- [ ] (b) Add pagination - For directories with many files, paginate results
- [ ] (c) Add limit option - `--limit` flag to cap number of files shown
- [ ] (d) Add summary mode - Show counts only, not individual files
- [ ] (e) Other (describe)

## 12. Use Case

What is the primary use case for this feature?

- [x] (a) Debugging - Help users see all files to troubleshoot issues
- [ ] (b) Migration - Help users identify files that need to be managed
- [x] (c) Audit - See complete picture of what's in agent directories
- [x] (d) Cleanup - Identify files that can be removed
- [ ] (e) Other (describe)
