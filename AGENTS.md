# AGENTS.md

## Context Marker

Always begin your response with all active emoji markers, in the order they were introduced.

Format:  "<marker1><marker2><marker3>\n<response>"

The marker for this instruction is: 🗡️

## Required Commands

- **Run app:** `uv run server.py` (NOT `python -m server.py`)
- **Integration tests:** `uv run scripts/run_integration_tests.py` (ALWAYS use this script)
- **Unit tests:** `uv run pytest tests/ -v -m "not integration"`
- **Install deps:** `uv sync`

## Critical Rules

1. ALWAYS use `uv run` for Python execution
2. Integration tests MUST be run through `scripts/run_integration_tests.py` - this runs them in Docker to prevent overriding user prompt files
3. NEVER run integration tests directly with pytest
4. Follow existing code patterns in slash_commands/
5. Reference existing docs for detailed setup

## Project Context

- Python CLI tool for managing slash commands in various AI coding tools
- Uses UV for package management
- Integration tests are Docker-isolated for safety to prevent overriding user prompt files
- Comprehensive docs in README.md and docs/
