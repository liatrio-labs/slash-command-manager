# 05-spec-pre-commit-cspell.md

## Introduction/Overview

This specification adds a pre-commit hook for cspell (Code Spell Checker) to enforce spelling consistency across markdown documentation files in the repository. The hook will check all markdown files during commits, fail on spelling errors, and provide suggestions for corrections while requiring manual dictionary updates for project-specific terms. This ensures documentation quality and consistency while maintaining developer control over technical terminology.

## Goals

- Integrate cspell as a pre-commit hook to check markdown files automatically
- Create a shared `.cspell.json` configuration file at the repository root
- Provide clear error messages with spelling suggestions when errors are detected
- Include common project-specific terms in the initial dictionary to reduce false positives
- Fail commits when spelling errors are found to maintain documentation quality
- Enable manual dictionary management for project-specific terminology

## User Stories

**As a documentation maintainer**, I want markdown files to be spell-checked automatically so that typos and spelling errors are caught before they reach the repository.

**As a developer**, I want clear feedback on spelling errors with suggestions so that I can quickly fix documentation issues without guessing correct spellings.

**As a project maintainer**, I want project-specific terms (like "Liatrio", "slash-man", "SDD") to be recognized as valid words so that technical terminology doesn't trigger false positives.

**As a contributor**, I want the spell checker to run consistently across all commits so that documentation quality standards are maintained automatically.

## Demoable Units of Work

### [Unit 1]: cspell Pre-commit Hook Integration

**Purpose:** Add cspell hook to the existing pre-commit configuration to check markdown files
**Demo Criteria:** Running `pre-commit run cspell --all-files` successfully checks all markdown files and reports spelling errors (if any exist)
**Proof Artifacts:** Updated `.pre-commit-config.yaml` with cspell hook, successful hook execution output, test: verify hook runs on commit attempt

### [Unit 2]: cspell Configuration File Creation

**Purpose:** Create `.cspell.json` configuration file with project-specific dictionary and markdown file patterns
**Demo Criteria:**

- File `.cspell.json` exists at repository root
- Configuration includes project-specific terms (Liatrio, slash-man, SDD, MCP, etc.)
- Configuration specifies markdown file patterns (`.md` files)
- Running `cspell --config .cspell.json README.md` validates configuration works
**Proof Artifacts:** Created `.cspell.json` file, cspell command output showing configuration loaded, dictionary terms visible in config

### [Unit 3]: Pre-commit Hook Failure Behavior

**Purpose:** Verify that commits fail when spelling errors are detected in markdown files
**Demo Criteria:**

- Create a test markdown file with intentional spelling error (e.g., "teh" instead of "the")
- Attempt to commit the file: `git add test.md && git commit -m "test: add file with spelling error"`
- Commit fails with cspell error message showing the misspelled word and suggestions
**Proof Artifacts:** Git commit failure output, cspell error message with suggestions, test: verify commit fails on spelling error

### [Unit 4]: Dictionary Management Workflow

**Purpose:** Demonstrate manual dictionary update process for adding project-specific terms
**Demo Criteria:**

- Add a new project-specific term to `.cspell.json` dictionary (e.g., "uvx")
- Verify term is recognized: `cspell --config .cspell.json --words-only "uvx"` returns no errors
- Commit the updated dictionary file successfully
**Proof Artifacts:** Updated `.cspell.json` with new dictionary entry, cspell validation output, successful commit of dictionary changes

## Functional Requirements

1. **The system shall** check all markdown files (`.md` extension) during pre-commit hook execution, excluding `CHANGELOG.md`
2. **The system shall** use a shared `.cspell.json` configuration file located at the repository root
3. **The system shall** fail the commit when spelling errors are detected in markdown files
4. **The system shall** provide spelling suggestions in error messages when misspellings are found
5. **The system shall** recognize project-specific terms defined in the `.cspell.json` dictionary
6. **The system shall** run on all files in the commit (not just changed files) to ensure consistency
7. **The system shall** integrate with the existing pre-commit hook framework without breaking other hooks
8. **The system shall** allow manual updates to the dictionary file for adding new project-specific terms
9. **The system shall** exclude common false-positive patterns (code blocks, URLs, file paths) from spell checking
10. **The system shall** provide clear error output indicating which files contain spelling errors and which words are misspelled
11. **The system shall** use standard English (en_US) dictionary and proper capitalization for technical terms

## Non-Goals (Out of Scope)

1. **Spell checking code files** - This feature only checks markdown documentation files, not Python code, comments, or docstrings
2. **Automatic dictionary updates** - Dictionary updates must be manual; the system will not auto-add words to the dictionary
3. **Spell checking during CI/CD** - This is a pre-commit hook only; CI/CD spell checking is out of scope
4. **Integration with IDE spell checkers** - IDE-specific spell checking configuration is not included
5. **Multi-language support** - Only English spell checking is supported
6. **Auto-fixing spelling errors** - The hook reports errors but does not automatically fix them
7. **Spell checking of generated files** - Only source markdown files are checked, not generated documentation
8. **Spell checking CHANGELOG.md** - CHANGELOG.md is excluded from spell checking as it may contain inconsistent formatting and auto-generated content

## Design Considerations

No specific design requirements identified. This is a command-line tool integration with no UI components.

## Repository Standards

- **Pre-commit Configuration**: Follow existing `.pre-commit-config.yaml` structure and hook ordering patterns
- **Configuration Files**: Place `.cspell.json` at repository root following standard cspell configuration location
- **Dictionary Management**: Use standard cspell dictionary format with `words` array in JSON configuration
- **Documentation**: Update `CONTRIBUTING.md` to include information about the spell checker and dictionary management
- **Testing**: Follow existing test patterns; add tests to verify hook integration and configuration
- **Commit Messages**: Use conventional commit format (already established in repository)

## Technical Considerations

- **cspell Installation**: cspell will be installed via pre-commit hook framework (no manual installation required)
- **Pre-commit Hook Repository**: Use official cspell pre-commit hook repository: `https://github.com/streetsidesoftware/cspell-pre-commit`
- **Configuration Format**: Use JSON format for `.cspell.json` (standard cspell configuration format)
- **File Patterns**: Configure cspell to check only `.md` files using `files` or `include` patterns in configuration
- **File Exclusions**: Exclude `CHANGELOG.md` from spell checking (auto-generated content with potentially inconsistent formatting)
- **Dictionary Format**: Use `words` array in `.cspell.json` for project-specific terms
- **Initial Dictionary**: Include common project-specific terms (Liatrio, slash-man, SDD, MCP, etc.) and dependency names (pytest, ruff, typer, fastmcp, questionary, uvx, uv, etc.)
- **Technical Term Capitalization**: Use standard proper capitalization for technical terms (e.g., "GitHub", "Python", "JSON", "YAML", "CLI", "MCP")
- **Language Dictionary**: Use default English (en_US) dictionary provided by cspell
- **Exclusion Patterns**: Configure exclusions for code blocks, URLs, and file paths to reduce false positives
- **Hook Execution Order**: Place cspell hook after file format checks but before code linting hooks
- **Performance**: cspell should run efficiently on markdown files; consider excluding large generated files if needed
- **Dependencies**: No additional Python dependencies required; cspell runs via pre-commit framework

## Success Metrics

1. **Hook Integration**: Pre-commit hook successfully runs cspell on all markdown files during commit attempts
2. **Error Detection**: Spelling errors in markdown files cause commits to fail with clear error messages
3. **False Positive Reduction**: Initial dictionary includes sufficient project-specific terms to minimize false positives (target: <5% false positive rate on existing markdown files)
4. **Developer Experience**: Developers can successfully add new terms to dictionary and commit changes
5. **Documentation Quality**: All existing markdown files pass spell checking after dictionary configuration

## Open Questions

No open questions at this time.
