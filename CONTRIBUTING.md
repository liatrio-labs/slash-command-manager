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

## Pull Request Process

1. Ensure all tests pass
2. Ensure linting and formatting checks pass
3. Update documentation if needed
4. Create a descriptive pull request with:
   - Clear description of changes
   - Reference to related issues
   - Example usage if applicable

## Reference Files

Reference files and archived documentation from the original repository extraction should be placed in the `docs/reference/` directory. This includes:

- Original workflow configurations (e.g., `original-spec-driven-workflow-repo-before-extraction.xml`)
- Historical snapshots or analysis files
- Other reference materials needed for documentation

When referencing these files in documentation or specifications, use repository-relative paths (e.g., `docs/reference/filename.xml`) rather than absolute paths to ensure the documentation works across all contributor environments.

## Questions?

If you have questions, please open an issue or contact the maintainers.

Thank you for contributing!
