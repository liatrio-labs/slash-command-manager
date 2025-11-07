# Contributing to Slash Command Manager

Thank you for your interest in contributing to Slash Command Manager! This document provides guidelines and instructions for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/slash-command-manager.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Set up the development environment:

   ```bash
   uv pip install -e ".[dev]"
   pre-commit install
   ```

## Development Workflow

1. Make your changes
2. Run tests: `pytest tests/`
3. Run linting: `ruff check .`
4. Run formatting: `ruff format .`
5. Run pre-commit hooks: `pre-commit run --all-files`
6. Commit your changes with a conventional commit message
7. Push to your fork and create a pull request

## Code Style

- Follow PEP 8 style guidelines
- Use `ruff` for linting and formatting
- Maximum line length: 100 characters
- Type hints are encouraged but not required

## Testing

- Write tests for new features and bug fixes
- Ensure all tests pass: `pytest tests/`
- Aim for high test coverage
- Tests should be in the `tests/` directory

## Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```text
feat: add new command generation feature
fix: resolve issue with file detection
docs: update installation instructions
refactor: simplify configuration logic
```

## Pre-commit Hooks

Pre-commit hooks are installed automatically and will run on commit. They check:

- Trailing whitespace
- File endings
- YAML/JSON/TOML syntax
- Code formatting (ruff)
- Code linting (ruff)
- Spell checking (cspell)

### Spell Checking

The repository uses [cspell](https://cspell.org/) to check spelling in markdown files. The spell checker runs automatically as a pre-commit hook and will fail commits if spelling errors are detected.

**How it works:**

- Checks all markdown files (`.md`) during commits
- Uses the `.cspell.json` configuration file at the repository root
- Fails commits when spelling errors are found
- Provides suggestions for misspelled words in error messages

**Adding new terms to the dictionary:**

If you encounter a false positive (a valid word that cspell flags as misspelled), you can add it to the dictionary by editing `.cspell.json` and adding the term to the `words` array:

```json
{
  "words": [
    "existing-terms",
    "your-new-term"
  ]
}
```

**Verifying spell checking:**

- Run manually: `pre-commit run cspell --all-files`
- Runs automatically: The hook runs automatically on every commit
- Note: `CHANGELOG.md` is excluded from spell checking

## Pull Request Process

1. Ensure all tests pass
2. Ensure linting and formatting checks pass
3. Update documentation if needed
4. Create a descriptive pull request with:
   - Clear description of changes
   - Reference to related issues
   - Example usage if applicable

## Questions?

If you have questions, please open an issue or contact the maintainers.

Thank you for contributing!
