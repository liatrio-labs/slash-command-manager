# Operations Guide

This guide covers deployment, configuration, and operation of the Slash Command Manager CLI tool.

## Local Development

### Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) package manager

### Setup

1. Clone the repository and navigate to the project directory
2. Install dependencies:

```bash
uv sync
```

1. Run tests to verify setup:

```bash
uv run pytest
```

## Slash Command Generation

The slash command generator can create native commands for various AI tools:

### Basic Usage

Generate commands for all auto-detected agents:

```bash
slash-man generate
```

### Specific Agents

Generate commands for specific tools:

```bash
slash-man generate --agent claude-code --agent cursor
```

### Dry Run

Preview changes without writing files:

```bash
slash-man generate --dry-run
```

### Cleanup

Remove generated command files:

```bash
slash-man cleanup --yes
```

## Testing

### Run All Tests

```bash
uv run pytest
```

### Run Unit Tests Only

```bash
uv run pytest -m "not integration"
```

### Run Integration Tests

```bash
uv run scripts/run_integration_tests.py
```

### Run with Coverage

```bash
uv run pytest --cov=slash_commands --cov-report=html
```

Open `htmlcov/index.html` in your browser to view the detailed coverage report.

### Specific Test Files

```bash
uv run pytest tests/test_prompts.py -v
```

## Troubleshooting

### CLI Won't Run

1. Verify Python version: `python --version` (should be 3.12+)
2. Reinstall dependencies: `uv sync`
3. Verify installation: `uv run slash-man --version`

### Prompts Not Loading

1. Verify prompts directory exists and contains `.md` files
2. Check that prompt files have valid YAML frontmatter
3. Use `--dry-run` to preview what would be generated

### Tests Failing

1. Ensure all dependencies are installed: `uv sync`
2. Run tests with verbose output: `uv run pytest -v`
3. Check for environment variable conflicts

### Slash Commands Not Working

1. Verify the target directory exists and is writable
2. Check that the AI tool is properly configured
3. Review generated command files for correct syntax
4. Ensure prompts have valid frontmatter with required fields

## Deployment

### Docker Deployment

Build and run the Docker container:

```bash
docker build -t slash-command-manager .
docker run slash-command-manager slash-man generate --list-agents
```

## Building Package

```bash
# Build wheel and source distribution
uv run python -m build

# Install built package locally
pip install dist/*.whl
```
