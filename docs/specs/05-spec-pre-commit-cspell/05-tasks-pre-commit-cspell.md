# 05-tasks-pre-commit-cspell.md

## Relevant Files

- `.cspell.json` - New file at repository root containing cspell configuration with project-specific dictionary, file patterns, and exclusions
- `.pre-commit-config.yaml` - Existing pre-commit configuration file that needs cspell hook added after file format checks but before code linting hooks
- `CONTRIBUTING.md` - Existing contributing guide that needs spell checking section added

### Notes

- The `.cspell.json` file should be created at the repository root following standard cspell configuration format
- The cspell hook should be added to `.pre-commit-config.yaml` using the official repository: `https://github.com/streetsidesoftware/cspell-pre-commit`
- Hook execution order: cspell should run after file format checks (check-yaml, check-json, check-toml) but before code linting hooks (ruff-check, ruff-format)
- The cspell configuration should exclude `CHANGELOG.md` from spell checking (similar to how markdownlint excludes it)
- Project-specific terms should include: Liatrio, slash-man, SDD, MCP, and dependency names from pyproject.toml (pytest, ruff, typer, fastmcp, questionary, uvx, uv, etc.)
- Technical terms should use proper capitalization: GitHub, Python, JSON, YAML, CLI, MCP
- Use standard English (en_US) dictionary provided by cspell
- Configure exclusions for code blocks, URLs, and file paths to reduce false positives
- Follow existing CONTRIBUTING.md structure and style when adding spell checking documentation

## Tasks

- [x] 1.0 Create cspell Configuration File
  - Demo Criteria: File `.cspell.json` exists at repository root with project-specific dictionary terms (Liatrio, slash-man, SDD, MCP, etc.), dependency names (pytest, ruff, typer, fastmcp, questionary, uvx, uv, etc.), proper technical term capitalization (GitHub, Python, JSON, YAML, CLI, MCP), markdown file patterns configured, CHANGELOG.md excluded, and code block/URL/file path exclusions configured. Running `cspell --config .cspell.json README.md` validates configuration works without false positives
  - Proof Artifact(s): Created `.cspell.json` file at repository root, cspell command output showing configuration loaded successfully, dictionary terms visible in config file
  - [x] 1.1 Create `.cspell.json` file at repository root with basic structure including `version`, `language`, `files`, `ignorePaths`, `words`, and `flagWords` fields
  - [x] 1.2 Configure `language` field to use `["en"]` for English dictionary
  - [x] 1.3 Configure `files` field to include markdown file patterns: `["**/*.md"]`
  - [x] 1.4 Configure `ignorePaths` field to exclude `CHANGELOG.md` from spell checking
  - [x] 1.5 Add project-specific terms to `words` array: "Liatrio", "slash-man", "SDD", "MCP", "spec-driven", "liatrio-labs"
  - [x] 1.6 Add dependency names to `words` array: "pytest", "ruff", "typer", "fastmcp", "questionary", "uvx", "uv", "pyyaml", "tomli", "hatchling", "semantic-release", "commitlint", "markdownlint"
  - [x] 1.7 Add properly capitalized technical terms to `words` array: "GitHub", "Python", "JSON", "YAML", "CLI", "MCP", "HTTP", "STDIO", "PyPI", "CI", "CD", "API", "REST"
  - [x] 1.8 Configure `flagWords` or use regex patterns to exclude common false positives: code blocks (backtick blocks), URLs (http://, https://), file paths (absolute and relative paths), email addresses
  - [x] 1.9 Test configuration by running `cspell --config .cspell.json README.md` and verify no false positives are reported for existing markdown files
  - [x] 1.10 Verify configuration file is valid JSON by running `python -m json.tool .cspell.json` or using `check-json` pre-commit hook

- [x] 2.0 Add cspell Hook to Pre-commit Configuration
  - Demo Criteria: Running `pre-commit run cspell --all-files` successfully checks all markdown files (excluding CHANGELOG.md) and reports spelling errors (if any exist). Hook is placed after file format checks but before code linting hooks in `.pre-commit-config.yaml`. Hook uses official cspell-pre-commit repository
  - Proof Artifact(s): Updated `.pre-commit-config.yaml` with cspell hook entry, successful hook execution output showing markdown files checked, hook execution order verified in config file
  - [x] 2.1 Add new repository entry to `.pre-commit-config.yaml` for cspell using `repo: https://github.com/streetsidesoftware/cspell-pre-commit` with appropriate `rev` tag (check latest version)
  - [x] 2.2 Add cspell hook entry with `id: cspell` in the hooks list, placing it after the `pre-commit-hooks` repository section (after file format checks) but before the `ruff-pre-commit` repository section (before code linting)
  - [x] 2.3 Configure hook to check only markdown files by adding `files: \.md$` pattern or using appropriate file filtering
  - [x] 2.4 Configure hook to exclude `CHANGELOG.md` using `exclude: CHANGELOG\.md` pattern (matching markdownlint exclusion pattern)
  - [x] 2.5 Verify hook placement in config file: cspell hook should appear after `check-toml` hook and before `ruff-check` hook
  - [x] 2.6 Test hook installation by running `pre-commit install` (or verify it's already installed)
  - [x] 2.7 Test hook execution by running `pre-commit run cspell --all-files` and verify it checks markdown files successfully
  - [x] 2.8 Verify hook execution order by running `pre-commit run --all-files` and confirming cspell runs after file format checks and before code linting

- [x] 3.0 Verify Pre-commit Hook Failure Behavior
  - Demo Criteria: Create a test markdown file with intentional spelling error (e.g., "teh" instead of "the"). Attempt to commit the file: `git add test.md && git commit -m "test: add file with spelling error"`. Commit fails with cspell error message showing the misspelled word and suggestions. Error output clearly indicates which file contains spelling errors and which words are misspelled
  - Proof Artifact(s): Git commit failure output showing cspell error, cspell error message with spelling suggestions displayed, test markdown file with intentional error
  - [x] 3.1 Create a temporary test markdown file `test-spell-check.md` with intentional spelling errors (e.g., "teh" instead of "the", "receive" instead of "receive")
  - [x] 3.2 Stage the test file: `git add test-spell-check.md`
  - [x] 3.3 Attempt to commit the file: `git commit -m "test: verify cspell hook failure behavior"`
  - [x] 3.4 Verify commit fails with cspell error message showing misspelled words and suggestions
  - [x] 3.5 Verify error output clearly indicates which file contains spelling errors and lists misspelled words
  - [x] 3.6 Fix spelling errors in test file and verify commit succeeds
  - [x] 3.7 Remove test file after verification: `git rm test-spell-check.md && git commit -m "test: remove spell check test file"`
  - [x] 3.8 Document the failure behavior verification process (can be included in CONTRIBUTING.md update)

- [ ] 4.0 Update Documentation for Spell Checker
  - Demo Criteria: `CONTRIBUTING.md` includes new "Spell Checking" section explaining the cspell hook, how to add new terms to the dictionary, and how to verify spell checking works. Documentation follows existing CONTRIBUTING.md structure and style. Running `pre-commit run cspell --all-files` confirms all existing markdown files pass spell checking after dictionary configuration
  - Proof Artifact(s): Updated `CONTRIBUTING.md` with spell checking section, all existing markdown files pass spell checking (no false positives)
  - [ ] 4.1 Add new "Spell Checking" subsection under "Pre-commit Hooks" section in `CONTRIBUTING.md` (after existing hook descriptions)
  - [ ] 4.2 Document that cspell checks markdown files for spelling errors and fails commits on errors
  - [ ] 4.3 Explain how to add new project-specific terms to `.cspell.json` dictionary: edit the `words` array and add the term
  - [ ] 4.4 Document how to verify spell checking works: run `pre-commit run cspell --all-files` or let it run automatically on commit
  - [ ] 4.5 Mention that `CHANGELOG.md` is excluded from spell checking
  - [ ] 4.6 Update the "Pre-commit Hooks" section summary to include spell checking in the list of checks
  - [ ] 4.7 Verify all existing markdown files pass spell checking by running `pre-commit run cspell --all-files` and addressing any false positives by adding terms to dictionary
  - [ ] 4.8 Ensure documentation follows existing CONTRIBUTING.md style and formatting conventions
