# Specification: Slash Command Manager Extraction & SDD Workflow Refactoring

**Date:** 2025-10-29
**Author:** Cascade (with Damien)
**Spec Version:** 1.0

---

## Overview

This specification outlines the complete extraction and refactoring of the Slash Command Generator tooling and MCP server into a dedicated repository called **Slash Command Manager**, while refocusing the original SDD workflow repository on core prompts and documentation only.

Currently, the Slash Command Generator, MCP server, and SDD workflow components all live in the same repository. This project separates the generator and MCP server into a new focused **Slash Command Manager** project, leaving the original repo with only workflow prompts and documentation.

**Goal:** Successfully extract the generator and MCP server into Slash Command Manager while preserving functionality, quality, and minimizing disruption to downstream automation and users.

---

## Goals

1. **Establish Slash Command Manager as a standalone, production-ready project** with independent versioning, CI/CD, and packaging, containing both the generator and MCP server.
2. **Refocus the SDD workflow repository** on core Spec-Driven Development prompts and documentation only (no code).
3. **Preserve code quality, test coverage, and release automation** standards across both projects.
4. **Enable independent release cycles** for the Slash Command Manager (generator + MCP) and workflow prompts.
5. **Minimize migration friction** for users currently consuming both components.
6. **Provide clear migration guidance** to users transitioning from the old setup to the new split.

---

## User Stories

1. **As a** CLI user of the generator
   **I want to** install Slash Command Manager independently from SDD workflow
   **So that** I can use just the generator without taking a dependency on workflow updates.

2. **As a** SDD workflow maintainer
   **I want to** maintain core prompts without managing generator or MCP server code
   **So that** I can focus on improving the workflow itself without generator or MCP-related changes blocking releases.

3. **As a** Slash Command Manager maintainer
   **I want to** release the generator and MCP server on their own cadence
   **So that** bug fixes and features don't wait for workflow prompt changes.

4. **As a** downstream automation consumer
   **I want to** migrate from the old `sdd-commands` entry point to `slash-man`
   **So that** I can use the new, clearer CLI naming convention.

5. **As a** contributor
   **I want to** understand which repository contains which code
   **So that** I can contribute to the right project and quickly onboard to either codebase.

---

## Demoable Units of Work

> **Note:** All proof artifacts and demo files generated during implementation should be stored in `./docs/artifacts/<spec-number>/task-<task-number>/` (e.g., `./docs/artifacts/0001/task-1.0/`) for review and documentation purposes. This organization ensures artifacts are properly categorized by specification and task.

### Unit 1: Slash Command Manager Repository Prepared & Functional

**Purpose:** Demonstrate that Slash Command Manager is a self-contained, working repository with all generator code, MCP server code, tests, and packaging in place.

**Demo Criteria:**

- [ ] Repository created at `/home/damien/Liatrio/repos/slash-command-manager`
- [ ] `slash_commands/` package ported with all modules (CLI, config, writer, detection)
- [ ] `mcp_server/` package ported with all MCP functionality
- [ ] `server.py` entry point ported for MCP server
- [ ] `prompts/` directory ported (reference data for MCP)
- [ ] All generator and MCP tests pass: `pytest tests/`
- [ ] Pre-commit hooks pass: `pre-commit run --all-files`
- [ ] `slash-man --help` displays usage without errors
- [ ] Dry-run wheel build succeeds: `python -m build --wheel`
- [ ] Package installable via `uvx --from ./dist slash-man generate --help`

**Proof Artifacts:**

- CLI invocation output: `$ slash-man --help` (screenshot or log)
- Test run output: `pytest` summary showing all tests passing
- Wheel build log showing successful build
- `uvx` test output showing CLI working from locally-built wheel

---

### Unit 2: SDD Workflow Repository Refocused & Clean

**Purpose:** Demonstrate that the original repository is now focused solely on workflow prompts and documentation (details will be polished in a follow-up task).

**Demo Criteria:**

- [ ] `slash_commands/` directory removed
- [ ] `mcp_server/` directory removed
- [ ] `server.py` removed
- [ ] Generator and MCP-related tests removed
- [ ] Generator and MCP dependencies removed from `pyproject.toml`
- [ ] VHS demos and related scripts removed
- [ ] `prompts/` directory retained for reference
- [ ] README updated with link to Slash Command Manager
- [ ] CI/CD workflows updated appropriately
- [ ] Pre-commit passes: `pre-commit run --all-files`

**Proof Artifacts:**

- Git diff showing removed files and dependencies
- Updated README snippet with Slash Command Manager link

---

### Unit 3: Release & Migration Artifacts Created

**Purpose:** Demonstrate that users have clear guidance for migration and Slash Command Manager is published.

**Demo Criteria:**

- [ ] Slash Command Manager tagged with initial semantic version (e.g., `v1.0.0`)
- [ ] CHANGELOG entry in Slash Command Manager documenting the project launch
- [ ] Migration guide published in SDD workflow README/docs
- [ ] Upgrade notes available explaining:
  - How to install Slash Command Manager separately (via `uvx` or `pip`)
  - Migration from old `sdd-commands` entry point to `slash-man`
  - Compatibility notes for old scripts/CI
- [ ] Slash Command Manager package published to PyPI (or marked as ready)
- [ ] GitHub project metadata updated (topics, links, documentation)

**Proof Artifacts:**

- Git tag and release notes
- CHANGELOG entry
- Migration guide document
- PyPI package page (or build logs showing readiness)
- Updated GitHub repo metadata

---

### Unit 4: Stakeholder Communication & Coordination Complete

**Purpose:** Ensure all users, maintainers, and automation consumers are aware of the change.

**Demo Criteria:**

- [ ] Internal team notified (Slack, email, or documented meeting notes)
- [ ] GitHub topics/project board updated
- [ ] External documentation (if any) points to new repos
- [ ] Remaining open questions resolved or tracked in new repos' issue trackers
- [ ] Post-cutover support plan established (e.g., monitoring for early adopter issues)

**Proof Artifacts:**

- Slack messages or meeting notes
- Updated GitHub project board
- Issue tracker entries for post-migration tasks

---

## Functional Requirements

### Slash Command Manager Repository

1. **Package Structure:** Must contain the `slash_commands/` package with all modules (CLI, config, writer, detection).
2. **MCP Server:** Must contain the `mcp_server/` package with all MCP functionality and `server.py` entry point.
3. **Prompts Directory:** Must contain `prompts/` directory (required reference data for MCP server).
4. **CLI Entry Point:** Must provide `slash-man` as the primary CLI entry point (replaces `sdd-commands`).
5. **Test Suite:** Must include all generator and MCP-related tests with passing status.
6. **Packaging:** Must produce a valid Python wheel with both `slash-man` (CLI) and MCP server capabilities via `python -m build`.
7. **Installation:** Must be installable via `uvx` and `pip` workflows.
8. **CI/CD:** Must have GitHub Actions workflows for linting, testing, and release automation.
9. **Dependencies:** Must declare generator and MCP dependencies (e.g., `fastmcp`, `questionary`, `tomli-w`, `rich`, Typer).
10. **Versioning:** Must use semantic versioning with independent `__version__.py` or equivalent.
11. **Documentation:** Must include README, contributing guidelines, and generator/MCP-specific docs.
12. **Licensing:** Must include appropriate licensing files (matching original repo's license).
13. **Future MCP Subcommand:** Must be structured to support `slash-man mcp serve` as a future subcommand (within scope of future work, not this extraction).

### SDD Workflow Repository (Refocused)

1. **Removed Code:** Must not contain `slash_commands/`, `mcp_server/`, `server.py`, or any code package.
2. **Core Components:** Must retain `prompts/` directory for reference and workflow documentation.
3. **Updated Docs:** Must update README and docs to link to Slash Command Manager for generator and MCP functionality.
4. **No Package:** Must not be packaged/published as a Python package (prompts/docs only).
5. **Dependencies:** Must have all code-related dependencies removed from `pyproject.toml`.
6. **CI/CD:** Must have simplified GitHub Actions (if any CI is retained).

### Release & Migration

1. **CHANGELOG:** Slash Command Manager must document initial project launch and extracted components.
2. **Migration Guide:** SDD workflow repo must include instructions for installing Slash Command Manager.
3. **Backward Compatibility Notes:** Must provide guidance for scripts/CI using old `sdd-commands` entry point.
4. **PyPI Distribution:** Slash Command Manager package published to PyPI with clear, distinct name and purpose.

---

## Non-Goals (Out of Scope)

- **Shared submodules:** Test fixtures and docs will be copied, not shared via submodules.
- **Version synchronization:** Slash Command Manager and workflow prompts will not be coordinated or synchronized.
- **Combined CI/CD:** The two projects will have independent CI/CD pipelines (no single unified pipeline).
- **Shared test fixtures:** Each repo maintains its own test fixtures (copies made as needed).
- **Retroactive versioning:** Previous releases will not be re-versioned; the split is a forward-looking change.
- **Automation consumer updates:** We will not automatically update downstream automation; migration guidance is provided.
- **MCP Subcommand Integration:** Integrating MCP server as a `slash-man mcp serve` subcommand is future work (not part of this extraction).
- **SDD Workflow Repository Cleanup/Polish:** Cleanup and optimization of the refocused SDD workflow repo is a separate follow-up task.

---

## Design Considerations

### Repository Structure – Slash Command Manager

```text
slash-command-manager/
├── slash_commands/
│   ├── __init__.py
│   ├── cli.py
│   ├── config.py
│   ├── writer.py
│   ├── detection.py
│   └── ...
├── mcp_server/
│   ├── __init__.py
│   ├── config.py
│   ├── prompt_utils.py
│   ├── prompts_loader.py
│   └── ...
├── prompts/
│   └── ... (reference prompts for MCP server)
├── tests/
│   ├── test_cli.py
│   ├── test_generators.py
│   ├── test_detection.py
│   ├── test_config.py
│   ├── conftest.py
│   └── ...
├── docs/
│   ├── slash-command-generator.md
│   └── ...
├── pyproject.toml (generator + MCP specific)
├── server.py (MCP server entry point)
├── __version__.py
├── README.md (tailored for generator + MCP)
├── CONTRIBUTING.md
├── LICENSE
└── .github/workflows/
    ├── ci.yml
    ├── release.yml
    └── ...
```

### Repository Structure – SDD Workflow (Refocused)

```text
sdd-workflow/
├── prompts/
│   └── ... (SDD workflow prompts - reference only)
├── docs/
│   └── (updated to link to Slash Command Manager)
├── README.md (updated with Slash Command Manager links)
├── LICENSE
└── (minimal structure - no code, no tests, no packaging)
```

### Naming & Branding

- **Repository name:** `slash-command-manager`
- **Package names:**
  - `slash_commands` (CLI/generator Python package)
  - `mcp_server` (MCP server Python package)
- **CLI entry point:** `slash-man` (replaces `sdd-commands`)
- **MCP entry point:** `server.py` main function (currently `spec-driven-workflow`, will be updated)
- **Documentation:** Clear distinction between "Slash Command Manager" (the generator + MCP tool) and "SDD Workflow" (the prompts and workflow philosophy)

---

## Technical Considerations

### Dependency Audit

**Generator & MCP dependencies (move to SCM):**

- `fastmcp` (MCP server framework)
- `questionary` (interactive CLI prompts)
- `tomli-w` (TOML writing)
- `rich` (terminal formatting)
- `Typer` (CLI framework)
- `pyyaml` (YAML parsing for MCP config)

**Shared dependencies (keep in both):**

- `pytest` (testing)
- `ruff` (linting)
- `pre-commit` (pre-commit hooks)
- Others TBD after full audit

**SDD Workflow (removed):**

- All of the above; SDD workflow repo will have no code dependencies after extraction

### Import Path Updates

- Adjust any imports that reference the old repo structure
- Ensure `__version__.py` or equivalent is correctly placed in SCM repo
- Update any internal references to package paths in tests and docs

### CI/CD Pipeline

- Copy GitHub Actions workflows from original repo to SCM
- Update test paths and coverage targets in SCM's CI (include `mcp_server` and `slash_commands`)
- Simplify or remove CI/CD from SDD workflow repo (prompts/docs only)
- Ensure SCM has independent semantic versioning and release automation
- SDD workflow may retain minimal CI for documentation/validation if needed

### Release Coordination

- **Initial release:** SCM publishes first (e.g., `v1.0.0`) with both generator and MCP server
- **SDD workflow:** After extraction, SDD workflow repo is no longer published as a package (prompts/docs only)
- **PyPI:** Only SCM package published to PyPI
- **Entry points:** SCM registers:
  - `slash-man` CLI (replaces `sdd-commands`)
  - `server.py` for MCP server (entry point function, future: will become `slash-man mcp serve` subcommand)
- **SDD workflow updates:** Updated with links to SCM and migration guidance

---

## Success Metrics

1. **Functionality:** Both repos remain fully functional with all tests passing.
2. **Independence:** SCM and SDD workflow repos can be released, maintained, and updated independently.
3. **Code Quality:** Test coverage, linting, and pre-commit standards maintained in both repos.
4. **User Experience:** New CLI entry point (`slash-man`) is discoverable and well-documented.
5. **Migration Clarity:** Migration guide is clear, and users can easily transition to the new setup.
6. **Downstream Impact:** Minimal disruption to existing automation; clear compatibility notes provided.
7. **Documentation:** Both repos clearly explain their purpose and how they relate to each other.

---

## Open Questions & Decisions

1. **CLI Entry Point Name:** ✅ **Decided: `slash-man`**
   - Clear, pronounceable, and directly references "Slash Command Manager"
   - Provides migration path from old `sdd-commands` name

2. **Shared Test Fixtures/Docs:** ✅ **Decided: NO – Copy instead of submodule**
   - Each repo maintains independent test fixtures and docs
   - Simplifies CI/CD and reduces cross-repo dependencies

3. **Version Synchronization:** ✅ **Decided: NO synchronization across projects**
   - SCM and SDD workflow release independently
   - No coordinated versioning required

4. **Automation Consumers:** ✅ **Decided: NO – Provide migration guidance only**
   - Downstream automation will need to migrate from `sdd-commands` to `slash-man`
   - No automatic consumer updates; migration guide provided

---

## Execution Notes

- **Risk Level:** Medium – involves restructuring repos, moving code between projects, and release automation changes
- **Testing Strategy:** End-to-end testing at each demoable unit; integration testing post-split
- **Rollback Plan:** Git history preserved in both repos; can revert if critical issues discovered post-release
- **Communication:** Coordinate with team before cutover; announce changes on completion
- **Key Dates:** No hard deadline; coordination required to minimize disruption to users
- **Future Work:** MCP subcommand integration (`slash-man mcp serve`) and SDD workflow repository cleanup are separate follow-up tasks
