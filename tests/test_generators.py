from __future__ import annotations

import tomllib

import pytest

from mcp_server.prompt_utils import parse_frontmatter
from slash_commands.config import get_agent_config
from slash_commands.generators import (
    MarkdownCommandGenerator,
    TomlCommandGenerator,
)


def _extract_frontmatter_and_body(content: str) -> tuple[dict, str]:
    frontmatter, body = parse_frontmatter(content)
    if not frontmatter:
        pytest.fail("Generated markdown is missing YAML frontmatter")
    return frontmatter, body


def _parse_toml(content: str) -> dict:
    try:
        return tomllib.loads(content)
    except tomllib.TOMLDecodeError as exc:  # pragma: no cover - defensive
        pytest.fail(f"Generated TOML is invalid: {exc}")


def _normalize_for_comparison(text: str) -> str:
    """Normalize text for comparison (remove extra whitespace, normalize line endings)."""
    lines = [line.rstrip() for line in text.splitlines()]
    return "\n".join(lines) + "\n"


def test_markdown_generator_applies_agent_overrides(sample_prompt):
    agent = get_agent_config("claude-code")
    generator = MarkdownCommandGenerator()

    generated = generator.generate(sample_prompt, agent)
    frontmatter, body = _extract_frontmatter_and_body(generated)

    assert frontmatter["name"] == "sdd-sample-prompt"
    assert frontmatter["description"] == "Sample prompt tailored for Claude Code"
    assert sorted(frontmatter["tags"]) == ["generators", "testing"]
    assert frontmatter["enabled"] is True

    assert frontmatter["arguments"] == [
        {
            "name": "primary_input",
            "description": "Main instruction for the command",
            "required": True,
        },
        {
            "name": "secondary_flag",
            "description": "Toggle additional behaviour",
            "required": False,
        },
    ]

    meta = frontmatter["meta"]
    assert meta["category"] == "generator-tests"
    assert meta["agent"] == "claude-code"
    assert meta["agent_display_name"] == agent.display_name
    assert meta["command_dir"] == agent.command_dir
    assert meta["command_format"] == agent.command_format.value
    assert meta["command_file_extension"] == agent.command_file_extension
    assert meta["source_prompt"] == "sample-prompt"
    assert meta["source_path"].endswith("sample-prompt.md")
    assert "version" in meta
    assert isinstance(meta["version"], str)
    assert "updated_at" in meta
    assert isinstance(meta["updated_at"], str)

    assert "Use the provided instructions" in body
    assert "$ARGUMENTS" not in body


def test_markdown_generator_replaces_arguments_placeholder(prompt_with_placeholder_body):
    agent = get_agent_config("claude-code")
    generator = MarkdownCommandGenerator()

    generated = generator.generate(prompt_with_placeholder_body, agent)
    frontmatter, body = _extract_frontmatter_and_body(generated)

    assert frontmatter["name"] == "sdd-prompt-with-placeholders"
    assert frontmatter["description"] == "Prompt for validating placeholder substitution"

    assert "$ARGUMENTS" not in body
    assert "{{args}}" in body

    lines = [line.strip() for line in body.splitlines() if line.strip()]
    argument_lines = [line for line in lines if line.startswith("-")]

    assert "- `<query>` (required): Search query to send to the agent" in argument_lines
    assert "- `[format]` (optional): Preferred response format" in argument_lines, argument_lines


def test_toml_generator_applies_agent_overrides(sample_prompt):
    agent = get_agent_config("gemini-cli")
    generator = TomlCommandGenerator()

    generated = generator.generate(sample_prompt, agent)
    data = _parse_toml(generated)

    # Gemini CLI spec has 'prompt' (required) and 'description' (optional)
    # We also add 'meta' for version tracking
    assert "prompt" in data
    assert data["description"] == "Sample prompt tailored for Gemini CLI"
    assert "meta" in data

    # Check meta fields
    meta = data["meta"]
    assert "version" in meta
    assert "updated_at" in meta
    assert meta["source_prompt"] == "sample-prompt"
    assert meta["agent"] == "gemini-cli"

    prompt_text = data["prompt"]
    assert prompt_text.startswith("# Sample Prompt")
    assert "Use the provided instructions" in prompt_text

    # Gemini CLI expects {{args}} to be preserved, not replaced
    # Check that it's still present if we have a placeholder
    assert "$ARGUMENTS" not in prompt_text


def test_toml_generator_substitutes_argument_placeholders(prompt_with_placeholder_body):
    agent = get_agent_config("gemini-cli")
    generator = TomlCommandGenerator()

    generated = generator.generate(prompt_with_placeholder_body, agent)
    data = _parse_toml(generated)

    # Gemini CLI spec has 'prompt' (required) and 'description' (optional)
    # We also add 'meta' for version tracking
    assert "prompt" in data
    assert data["description"] == "Prompt with TOML specific placeholder"
    assert "meta" in data

    prompt_text = data["prompt"]

    # Gemini CLI expects {{args}} to be preserved for context-aware injection
    # Check that $ARGUMENTS was replaced but {{args}} is preserved
    assert "{{args}}" in prompt_text
    assert "$ARGUMENTS" not in prompt_text

    # The body should contain the argument documentation replacement
    assert "query" in prompt_text
    assert "[format]" in prompt_text


def test_markdown_generator_snapshot_regression(sample_prompt):
    """Snapshot-style test to catch unintended changes in Markdown output format."""
    agent = get_agent_config("claude-code")
    generator = MarkdownCommandGenerator()

    generated = generator.generate(sample_prompt, agent)

    # Verify the output structure is consistent
    assert generated.startswith("---\n")
    assert "\n---\n" in generated
    assert generated.endswith("\n")

    # Verify no trailing whitespace in lines
    lines = generated.splitlines()
    for line in lines:
        assert line == line.rstrip(), "Line contains trailing whitespace"

    # Verify consistent line endings (LF only)
    assert "\r" not in generated


def test_toml_generator_snapshot_regression(sample_prompt):
    """Snapshot-style test to catch unintended changes in TOML output format."""
    agent = get_agent_config("gemini-cli")
    generator = TomlCommandGenerator()

    generated = generator.generate(sample_prompt, agent)

    # Verify the output structure follows Gemini CLI spec
    assert "prompt = " in generated
    assert "description = " in generated
    assert "[meta]" in generated
    assert generated.endswith("\n")

    # Verify no trailing whitespace in lines
    lines = generated.splitlines()
    for line in lines:
        assert line == line.rstrip(), "Line contains trailing whitespace"

    # Verify consistent line endings (LF only)
    assert "\r" not in generated

    # Verify valid TOML structure
    data = _parse_toml(generated)
    assert "prompt" in data
    assert isinstance(data["prompt"], str)
    assert "meta" in data
    assert isinstance(data["meta"], dict)


def test_prompt_metadata_github_source(sample_prompt):
    """Test that generated files contain correct GitHub source metadata."""
    agent_md = get_agent_config("claude-code")
    agent_toml = get_agent_config("gemini-cli")

    source_metadata = {
        "source_type": "github",
        "source_repo": "liatrio-labs/spec-driven-workflow",
        "source_branch": "refactor/improve-workflow",
        "source_path": "prompts",
    }

    # Test Markdown generator
    md_generator = MarkdownCommandGenerator()
    md_generated = md_generator.generate(sample_prompt, agent_md, source_metadata)
    md_frontmatter, _ = _extract_frontmatter_and_body(md_generated)

    md_meta = md_frontmatter["meta"]
    assert md_meta["source_type"] == "github"
    assert md_meta["source_repo"] == "liatrio-labs/spec-driven-workflow"
    assert md_meta["source_branch"] == "refactor/improve-workflow"
    assert md_meta["source_path"] == "prompts"

    # Test TOML generator
    toml_generator = TomlCommandGenerator()
    toml_generated = toml_generator.generate(sample_prompt, agent_toml, source_metadata)
    toml_data = _parse_toml(toml_generated)

    toml_meta = toml_data["meta"]
    assert toml_meta["source_type"] == "github"
    assert toml_meta["source_repo"] == "liatrio-labs/spec-driven-workflow"
    assert toml_meta["source_branch"] == "refactor/improve-workflow"
    assert toml_meta["source_path"] == "prompts"


def test_prompt_metadata_github_single_file_source(sample_prompt):
    """Test that generated files contain correct GitHub source metadata for single file."""
    agent = get_agent_config("claude-code")

    source_metadata = {
        "source_type": "github",
        "source_repo": "liatrio-labs/spec-driven-workflow",
        "source_branch": "refactor/improve-workflow",
        "source_path": "prompts/generate-spec.md",
    }

    generator = MarkdownCommandGenerator()
    generated = generator.generate(sample_prompt, agent, source_metadata)
    frontmatter, _ = _extract_frontmatter_and_body(generated)

    meta = frontmatter["meta"]
    assert meta["source_type"] == "github"
    assert meta["source_repo"] == "liatrio-labs/spec-driven-workflow"
    assert meta["source_branch"] == "refactor/improve-workflow"
    assert meta["source_path"] == "prompts/generate-spec.md"


def test_prompt_metadata_local_source(sample_prompt, tmp_path):
    """Test that generated files contain correct local source metadata."""
    agent_md = get_agent_config("claude-code")
    agent_toml = get_agent_config("gemini-cli")

    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    source_metadata = {
        "source_type": "local",
        "source_dir": str(prompts_dir.resolve()),
    }

    # Test Markdown generator
    md_generator = MarkdownCommandGenerator()
    md_generated = md_generator.generate(sample_prompt, agent_md, source_metadata)
    md_frontmatter, _ = _extract_frontmatter_and_body(md_generated)

    md_meta = md_frontmatter["meta"]
    assert md_meta["source_type"] == "local"
    assert md_meta["source_dir"] == str(prompts_dir.resolve())

    # Test TOML generator
    toml_generator = TomlCommandGenerator()
    toml_generated = toml_generator.generate(sample_prompt, agent_toml, source_metadata)
    toml_data = _parse_toml(toml_generated)

    toml_meta = toml_data["meta"]
    assert toml_meta["source_type"] == "local"
    assert toml_meta["source_dir"] == str(prompts_dir.resolve())


def test_prompt_metadata_no_source_metadata(sample_prompt):
    """Test that generated files work correctly without source metadata."""
    agent = get_agent_config("claude-code")
    generator = MarkdownCommandGenerator()

    # Generate without source metadata
    generated = generator.generate(sample_prompt, agent, None)
    frontmatter, _ = _extract_frontmatter_and_body(generated)

    meta = frontmatter["meta"]
    # Should not have source_type or source_dir/source_repo fields
    assert "source_type" not in meta
    assert "source_dir" not in meta
    assert "source_repo" not in meta
    # But should still have other metadata
    assert "source_prompt" in meta
    assert "agent" in meta
