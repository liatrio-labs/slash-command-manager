from __future__ import annotations

import tomllib

import pytest

from mcp_server.prompt_utils import parse_frontmatter
from slash_commands.config import get_agent_config
from slash_commands.generators import (
    KiroCommandGenerator,
    KiroIdeCommandGenerator,
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
    assert meta["command_dir"] == agent.get_command_dir()
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


# -- Kiro CLI prompt generator tests -------------------------------------------


def test_kiro_generator_produces_plain_markdown(sample_prompt):
    """Test that KiroCommandGenerator produces plain markdown with no frontmatter."""
    agent = get_agent_config("kiro-cli")
    generator = KiroCommandGenerator()

    generated = generator.generate(sample_prompt, agent)

    # Should NOT have YAML frontmatter
    assert not generated.startswith("---")
    # Should contain prompt body
    assert "# Sample Prompt" in generated
    assert "Use the provided instructions" in generated


def test_kiro_generator_includes_tracking_comment(sample_prompt):
    """Test that tracking metadata is appended as a trailing HTML comment."""
    agent = get_agent_config("kiro-cli")
    generator = KiroCommandGenerator()

    generated = generator.generate(sample_prompt, agent)

    assert "<!-- slash-command-manager:" in generated
    assert "source: sample-prompt" in generated
    assert "version:" in generated
    assert "updated:" in generated


def test_kiro_generator_replaces_placeholders(prompt_with_placeholder_body):
    """Test that argument placeholders are replaced in the prompt body."""
    agent = get_agent_config("kiro-cli")
    generator = KiroCommandGenerator()

    generated = generator.generate(prompt_with_placeholder_body, agent)

    assert "$ARGUMENTS" not in generated
    # Kiro replaces {{args}} with comma-separated names
    assert "{{args}}" not in generated
    assert "query" in generated


def test_kiro_generator_rewrites_command_references(tmp_path):
    """Test that /SDD-N-name command references are rewritten to @name for Kiro."""
    from mcp_server.prompt_utils import load_markdown_prompt

    prompt_path = tmp_path / "workflow-prompt.md"
    prompt_path.write_text(
        "---\n"
        "name: SDD-1-generate-spec\n"
        "description: Generate a spec\n"
        "arguments: []\n"
        "---\n\n"
        "# Generate Spec\n\n"
        "When done, run `/SDD-2-generate-task-list-from-spec` to continue.\n"
        "Then use `/SDD-3-manage-tasks` for implementation.\n"
        "Finally run `/SDD-4-validate-spec-implementation` to verify.\n",
        encoding="utf-8",
    )
    prompt = load_markdown_prompt(prompt_path)
    agent = get_agent_config("kiro-cli")
    generator = KiroCommandGenerator()

    generated = generator.generate(prompt, agent)

    assert "/SDD-2-" not in generated
    assert "/SDD-3-" not in generated
    assert "/SDD-4-" not in generated
    assert "@generate-task-list-from-spec" in generated
    assert "@manage-tasks" in generated
    assert "@validate-spec-implementation" in generated


def test_kiro_generator_github_source_metadata(sample_prompt):
    """Test that GitHub repo is included in tracking comment."""
    agent = get_agent_config("kiro-cli")
    generator = KiroCommandGenerator()

    source_metadata = {
        "source_repo": "liatrio-labs/spec-driven-workflow",
    }

    generated = generator.generate(sample_prompt, agent, source_metadata)

    assert "repo: liatrio-labs/spec-driven-workflow" in generated


def test_kiro_generator_snapshot_regression(sample_prompt):
    """Snapshot-style test to catch unintended changes in Kiro output format."""
    agent = get_agent_config("kiro-cli")
    generator = KiroCommandGenerator()

    generated = generator.generate(sample_prompt, agent)

    # Must end with newline
    assert generated.endswith("\n")

    # No trailing whitespace in lines
    for line in generated.splitlines():
        assert line == line.rstrip(), "Line contains trailing whitespace"

    # Consistent line endings (LF only)
    assert "\r" not in generated

    # Must have tracking comment at end
    assert generated.strip().endswith("-->")

    # Must NOT have frontmatter
    assert not generated.startswith("---")


# -- Kiro IDE agent generator tests --------------------------------------------


def test_kiro_ide_generator_produces_frontmatter_with_tools(sample_prompt):
    """Test that KiroIdeCommandGenerator produces markdown with Kiro IDE steering frontmatter."""
    agent = get_agent_config("kiro-ide")
    generator = KiroIdeCommandGenerator()

    generated = generator.generate(sample_prompt, agent)
    frontmatter, body = _extract_frontmatter_and_body(generated)

    # Check that inclusion is first, then name, description, tools
    assert frontmatter["inclusion"] == "manual"
    assert frontmatter["name"] == "sample-prompt"
    assert "description" in frontmatter
    assert frontmatter["tools"] == ["*"]
    # Should NOT have markdown-generator fields
    assert "tags" not in frontmatter
    assert "arguments" not in frontmatter
    assert "meta" not in frontmatter
    assert "enabled" not in frontmatter

    assert "# Sample Prompt" in body


def test_kiro_ide_generator_includes_tracking_comment(sample_prompt):
    """Test that tracking metadata is appended as a trailing HTML comment."""
    agent = get_agent_config("kiro-ide")
    generator = KiroIdeCommandGenerator()

    generated = generator.generate(sample_prompt, agent)

    assert "<!-- slash-command-manager:" in generated
    assert "source: sample-prompt" in generated
    assert "version:" in generated
    assert "updated:" in generated


def test_kiro_ide_generator_rewrites_command_references(tmp_path):
    """Test that /SDD-N-name references are rewritten to /name for steering files."""
    from mcp_server.prompt_utils import load_markdown_prompt

    prompt_path = tmp_path / "workflow-prompt.md"
    prompt_path.write_text(
        "---\n"
        "name: SDD-1-generate-spec\n"
        "description: Generate a spec\n"
        "arguments: []\n"
        "---\n\n"
        "# Generate Spec\n\n"
        "When done, run `/SDD-2-generate-task-list-from-spec` to continue.\n",
        encoding="utf-8",
    )
    prompt = load_markdown_prompt(prompt_path)
    agent = get_agent_config("kiro-ide")
    generator = KiroIdeCommandGenerator()

    generated = generator.generate(prompt, agent)

    assert "/SDD-2-" not in generated
    assert "/generate-task-list-from-spec" in generated

    # Frontmatter name should have ordering prefix stripped
    frontmatter, _ = _extract_frontmatter_and_body(generated)
    assert frontmatter["name"] == "generate-spec"


def test_kiro_ide_generator_replaces_placeholders(prompt_with_placeholder_body):
    """Test that argument placeholders are replaced."""
    agent = get_agent_config("kiro-ide")
    generator = KiroIdeCommandGenerator()

    generated = generator.generate(prompt_with_placeholder_body, agent)

    assert "$ARGUMENTS" not in generated
    assert "{{args}}" not in generated
    assert "query" in generated


def test_kiro_ide_generator_github_source_metadata(sample_prompt):
    """Test that GitHub repo is included in tracking comment."""
    agent = get_agent_config("kiro-ide")
    generator = KiroIdeCommandGenerator()

    source_metadata = {
        "source_repo": "liatrio-labs/spec-driven-workflow",
    }

    generated = generator.generate(sample_prompt, agent, source_metadata)

    assert "repo: liatrio-labs/spec-driven-workflow" in generated


def test_kiro_ide_generator_snapshot_regression(sample_prompt):
    """Snapshot-style test to catch unintended changes in Kiro IDE output format."""
    agent = get_agent_config("kiro-ide")
    generator = KiroIdeCommandGenerator()

    generated = generator.generate(sample_prompt, agent)

    # Must have frontmatter
    assert generated.startswith("---\n")
    assert "\n---\n" in generated

    # Must end with newline
    assert generated.endswith("\n")

    # No trailing whitespace in lines
    for line in generated.splitlines():
        assert line == line.rstrip(), "Line contains trailing whitespace"

    # Consistent line endings (LF only)
    assert "\r" not in generated

    # Must have tracking comment at end
    assert generated.strip().endswith("-->")
