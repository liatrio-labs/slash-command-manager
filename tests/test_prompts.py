"""Tests for prompt parsing utilities."""

from slash_commands.prompt_utils import parse_frontmatter


class TestFrontmatterParsing:
    """Tests for YAML frontmatter parsing."""

    def test_parse_frontmatter_with_valid_yaml(self):
        """Test parsing valid YAML frontmatter."""
        content = """---
description: Test prompt
tags:
  - test
  - example
---

# Prompt Body

This is the body."""
        frontmatter, body = parse_frontmatter(content)

        assert frontmatter["description"] == "Test prompt"
        assert frontmatter["tags"] == ["test", "example"]
        assert body.startswith("# Prompt Body")

    def test_parse_frontmatter_without_frontmatter(self):
        """Test parsing content without frontmatter."""
        content = "# Just a heading\n\nSome content"
        frontmatter, body = parse_frontmatter(content)

        assert frontmatter == {}
        assert body == content

    def test_parse_frontmatter_with_invalid_yaml(self):
        """Test parsing invalid YAML frontmatter."""
        content = """---
invalid: yaml: content:
---

Body"""
        frontmatter, body = parse_frontmatter(content)

        assert frontmatter == {}
        assert "Body" in body
