from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class PromptArgumentSpec:
    name: str
    description: str | None
    required: bool


@dataclass(frozen=True)
class MarkdownPrompt:
    path: Path
    name: str
    description: str | None
    tags: set[str] | None
    meta: dict[str, Any] | None
    enabled: bool
    arguments: list[PromptArgumentSpec]
    body: str
    agent_overrides: dict[str, Any] | None = None
    # Source metadata fields
    source_type: str | None = None
    source_github_url: str | None = None
    source_github_owner: str | None = None
    source_github_repo: str | None = None
    source_github_branch: str | None = None
    source_github_path: str | None = None
    source_local_path: str | None = None
    source_timestamp: str | None = None

    def decorator_kwargs(self) -> dict[str, Any]:
        kwargs: dict[str, Any] = {"name": self.name}
        if self.description:
            kwargs["description"] = self.description
        if self.tags:
            kwargs["tags"] = sorted(self.tags)
        if self.meta:
            kwargs["meta"] = self.meta
        if not self.enabled:
            kwargs["enabled"] = self.enabled
        return kwargs


def load_markdown_prompt(path: Path) -> MarkdownPrompt:
    if not path.exists():
        raise FileNotFoundError(f"Prompt file does not exist: {path}")

    content = path.read_text()
    frontmatter, body = parse_frontmatter(content)

    name = frontmatter.get("name") or path.stem
    description = frontmatter.get("description")
    tags = _ensure_tag_set(frontmatter.get("tags"))
    enabled = frontmatter.get("enabled", True)

    base_meta = frontmatter.get("meta") or {}
    additional_meta = {
        key: value
        for key, value in frontmatter.items()
        if key
        not in {
            "name",
            "description",
            "tags",
            "arguments",
            "meta",
            "enabled",
            "agent_overrides",
        }
    }
    meta = {**base_meta, **additional_meta} if additional_meta else base_meta or None

    arguments = normalize_arguments(frontmatter.get("arguments"))
    agent_overrides = frontmatter.get("agent_overrides")

    return MarkdownPrompt(
        path=path,
        name=name,
        description=description,
        tags=tags,
        meta=meta,
        enabled=bool(enabled),
        arguments=arguments,
        body=body,
        agent_overrides=agent_overrides,
        # Source metadata defaults (will be set by writer if needed)
        source_type=None,
        source_github_url=None,
        source_github_owner=None,
        source_github_repo=None,
        source_github_branch=None,
        source_github_path=None,
        source_local_path=None,
        source_timestamp=None,
    )


def parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    if not content.startswith("---"):
        return {}, content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content

    try:
        frontmatter = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        frontmatter = {}

    body = parts[2].strip()
    return frontmatter, body


def normalize_arguments(raw: Any) -> list[PromptArgumentSpec]:
    if not raw:
        return []

    if not isinstance(raw, list):
        raise ValueError("arguments metadata must be a list of argument definitions")

    normalized: list[PromptArgumentSpec] = []
    for entry in raw:
        if isinstance(entry, str):
            normalized.append(PromptArgumentSpec(name=entry, description=None, required=True))
            continue

        if not isinstance(entry, dict):
            raise ValueError("Each argument definition must be a string or mapping")

        name = entry.get("name")
        if not name or not isinstance(name, str):
            raise ValueError("Argument definitions must include a string 'name'")

        normalized.append(
            PromptArgumentSpec(
                name=name,
                description=entry.get("description"),
                required=entry.get("required", True),
            )
        )

    return normalized


def create_markdown_prompt_with_source(
    base_prompt: MarkdownPrompt, **source_metadata
) -> MarkdownPrompt:
    """Create a new MarkdownPrompt with source metadata."""
    return MarkdownPrompt(
        path=base_prompt.path,
        name=base_prompt.name,
        description=base_prompt.description,
        tags=base_prompt.tags,
        meta=base_prompt.meta,
        enabled=base_prompt.enabled,
        arguments=base_prompt.arguments,
        body=base_prompt.body,
        agent_overrides=base_prompt.agent_overrides,
        **source_metadata,
    )


def _ensure_tag_set(raw: Any) -> set[str] | None:
    if raw is None:
        return None

    if isinstance(raw, Iterable) and not isinstance(raw, str | bytes):
        tags = {str(tag) for tag in raw}
        return tags or None

    return {str(raw)}
