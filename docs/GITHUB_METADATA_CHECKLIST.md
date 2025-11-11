# GitHub Repository Metadata Checklist

This document outlines the GitHub repository metadata updates that should be completed manually for the Slash Command Manager repository.

## Repository Settings (via GitHub Web UI)

### Description

Update the repository description to:

```text
A standalone CLI tool and MCP server for generating and managing slash commands for AI coding assistants. Extracted from SDD Workflow.
```

### Topics/Tags

Add the following topics to the repository:

- `cli`
- `mcp-server`
- `slash-commands`
- `ai-assistants`
- `cursor`
- `claude-code`
- `windsurf`
- `spec-driven-development`
- `sdd-workflow`
- `python`
- `typer`
- `fastmcp`

### Website

Set the website URL to: `https://github.com/liatrio-labs/slash-command-manager` (or primary documentation link if available)

### Social Preview

Ensure the repository has an appropriate social preview image (if custom branding is desired)

## GitHub Release

### Create Release for v1.0.0

1. Go to the Releases page
2. Click "Draft a new release"
3. **Tag:** `v1.0.0`
4. **Title:** `Slash Command Manager v1.0.0 - Initial Release`
5. **Description:** Copy content from `RELEASE_NOTES_v1.0.0.md`
6. **Release Notes:** Include key highlights:
   - Initial release extracted from SDD Workflow
   - CLI generator (`slash-man`)
   - MCP server support
   - Installation and migration instructions
7. **Attachments:** Attach the wheel file: `dist/slash_command_manager-1.0.0-py3-none-any.whl`

## README Badges (Optional Enhancements)

Consider adding badges to the README:

- CI status badge (if GitHub Actions workflow is public)
- License badge
- PyPI version badge (once published)
- Code coverage badge (if applicable)

## Related Links

Ensure cross-references are updated:

- SDD Workflow repository links point to the correct location
- Documentation links are valid and accessible
- Installation instructions reference correct package names

---

**Note:** These updates require manual configuration through the GitHub web interface and cannot be automated via the repository's codebase.
