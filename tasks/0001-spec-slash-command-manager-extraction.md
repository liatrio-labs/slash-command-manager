# Specification: Slash Command Manager Extraction & SDD Workflow Refactoring

**Date:** 2025-10-29
**Author:** Cascade (with Damien)
**Spec Version:** 1.0

---

## Overview

This specification outlines the complete extraction and refactoring of the Slash Command Generator tooling into a dedicated repository called **Slash Command Manager**, while refocusing the original SDD workflow repository on core prompts, MCP server, and documentation.

Currently, both the Slash Command Generator and the SDD workflow components live in the same repository. This project separates them into two focused projects, each with a clear mission, independent release cycle, and maintained quality standards.

**Goal:** Successfully extract the generator into Slash Command Manager while preserving functionality, quality, and minimizing disruption to downstream automation and users.

---

## Goals

1. **Establish Slash Command Manager as a standalone, production-ready project** with independent versioning, CI/CD, and packaging.
2. **Refocus the SDD workflow repository** on core Spec-Driven Development prompts, MCP server implementation, and related documentation.
3. **Preserve code quality, test coverage, and release automation** standards across both projects.
4. **Enable independent release cycles** for generator tooling and workflow prompts.
5. **Minimize migration friction** for users currently consuming both components.
6. **Provide clear migration guidance** to users transitioning from the old setup to the new split.

---

## User Stories

1. **As a** CLI user of the generator
   **I want to** install Slash Command Manager independently from SDD workflow
   **So that** I can use just the generator without taking a dependency on workflow updates.

2. **As a** SDD workflow maintainer
   **I want to** maintain core prompts and MCP server without managing generator code
   **So that** I can focus on improving the workflow itself without generator-related changes blocking releases.

3. **As a** Slash Command Manager maintainer
   **I want to** release the generator on its own cadence
   **So that** bug fixes and features in the generator don't wait for workflow changes.

4. **As a** downstream automation consumer
   **I want to** migrate from the old `sdd-commands` entry point to `slash-man`
   **So that** I can use the new, clearer CLI naming convention.

5. **As a** contributor
   **I want to** understand which repository contains which code
   **So that** I can contribute to the right project and quickly onboard to either codebase.

---

## Demoable Units of Work

### Unit 1: Slash Command Manager Repository Prepared & Functional

**Purpose:** Demonstrate that Slash Command Manager is a self-contained, working repository with all generator code, tests, and packaging in place.

**Demo Criteria:**
- [ ] Repository created at `/home/damien/Liatrio/repos/slash-command-manager`
- [ ] `slash_commands/` package ported with all modules (CLI, config, writer, detection)
- [ ] All generator tests pass: `pytest tests/test_cli.py tests/test_generators.py tests/test_detection.py tests/test_config.py`
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

**Purpose:** Demonstrate that the original repository is now focused solely on SDD workflow components without generator code.

**Demo Criteria:**
- [ ] `slash_commands/` directory removed
- [ ] Generator-related tests removed (`test_cli.py`, `test_generators.py`, `test_detection.py`)
- [ ] Generator-only dependencies removed from `pyproject.toml` (e.g., `questionary`, `tomli-w`, removed)
- [ ] VHS demos and generator docs removed
- [ ] CI/CD workflows updated to exclude generator tests and coverage targets
- [ ] All SDD workflow tests still pass: `pytest tests/`
- [ ] README updated with link to Slash Command Manager
- [ ] Pre-commit passes: `pre-commit run --all-files`

**Proof Artifacts:**
- Git diff showing removed files and dependencies
- Updated README snippet with Slash Command Manager link
- Test run output showing remaining tests passing
- Coverage report showing updated targets

---

### Unit 3: Release & Migration Artifacts Created

**Purpose:** Demonstrate that users have clear guidance for migration and can access both projects via official channels.

**Demo Criteria:**
- [ ] Slash Command Manager tagged with initial semantic version (e.g., `v1.0.0`)
- [ ] SDD workflow tagged with breaking-change release (e.g., next major version)
- [ ] CHANGELOG entries in both repos documenting the split
- [ ] Migration guide published in SDD workflow README/docs
- [ ] Upgrade notes available explaining:
  - How to install Slash Command Manager separately
  - Migration from `sdd-commands` entry point to `slash-man`
  - Compatibility notes for old scripts/CI
- [ ] Both packages published to PyPI (or marked as ready for publication)
- [ ] GitHub project metadata updated (topics, links, documentation)

**Proof Artifacts:**
- Git tags and release notes
- CHANGELOG entries (text snippets)
- Migration guide document
- PyPI package pages (or build logs showing readiness)
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
2. **CLI Entry Point:** Must provide `slash-man` as the primary CLI entry point (replaces `sdd-commands`).
3. **Test Suite:** Must include all generator-related tests with passing status.
4. **Packaging:** Must produce a valid Python wheel with `slash-man` entry point via `python -m build`.
5. **Installation:** Must be installable via `uvx` and `pip` workflows.
6. **CI/CD:** Must have GitHub Actions workflows for linting, testing, and release automation.
7. **Dependencies:** Must declare only generator-specific dependencies (e.g., `questionary`, `tomli-w`, `rich`, Typer).
8. **Versioning:** Must use semantic versioning with independent `__version__.py` or equivalent.
9. **Documentation:** Must include README, contributing guidelines, and generator-specific docs.
10. **Licensing:** Must include appropriate licensing files (matching original repo's license).

### SDD Workflow Repository (Refocused)

11. **Removed Code:** Must not contain `slash_commands/`, generator tests, or generator-only dependencies.
12. **Core Components:** Must retain prompts, MCP server code, and related documentation.
13. **Updated Docs:** Must update README and docs to link to Slash Command Manager for generator functionality.
14. **Tests:** Must retain all SDD workflow-specific tests with passing status.
15. **Dependencies:** Must have generator-only dependencies removed from `pyproject.toml` and lock files.
16. **CI/CD:** Must have updated GitHub Actions with corrected coverage targets and test paths.
17. **Versioning:** Must maintain independent semantic versioning.

### Release & Migration

18. **CHANGELOG:** Both repos must document the split with clear version markers and migration guidance.
19. **Migration Guide:** SDD workflow repo must include instructions for installing Slash Command Manager.
20. **Backward Compatibility Notes:** Must provide guidance for scripts/CI using old `sdd-commands` entry point.
21. **PyPI Distribution:** Both packages must be published with clear, distinct names and purposes.

---

## Non-Goals (Out of Scope)

- **Shared submodules:** Test fixtures and docs will be copied, not shared via submodules.
- **Version synchronization:** Workflow prompts and generator releases will not be coordinated or synchronized.
- **Combined CI/CD:** The two projects will have independent CI/CD pipelines (no single unified pipeline).
- **Shared test fixtures:** Each repo maintains its own test fixtures (copies made as needed).
- **Retroactive versioning:** Previous releases will not be re-versioned; the split is a forward-looking change.
- **Automation consumer updates:** We will not automatically update downstream automation; migration guidance is provided.

---

## Design Considerations

### Repository Structure – Slash Command Manager

```
slash-command-manager/
├── slash_commands/
│   ├── __init__.py
│   ├── cli.py
│   ├── config.py
│   ├── writer.py
│   ├── detection.py
│   └── ...
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
├── pyproject.toml (generator-specific)
├── __version__.py
├── README.md (tailored for generator)
├── CONTRIBUTING.md
├── LICENSE
└── .github/workflows/
    ├── ci.yml
    ├── release.yml
    └── ...
```

### Repository Structure – SDD Workflow (Refocused)

```
sdd-workflow/
├── prompts/
│   └── ... (SDD workflow prompts)
├── mcp_server/
│   └── ... (MCP server code)
├── docs/
│   └── (updated to link to Slash Command Manager)
├── tests/
│   └── (workflow-specific tests only)
├── pyproject.toml (generator deps removed)
├── README.md (updated with SCM link)
├── CONTRIBUTING.md
├── LICENSE
└── .github/workflows/
    └── (updated CI/CD)
```

### Naming & Branding

- **Repository name:** `slash-command-manager`
- **Package name:** Likely remains `slash_commands` (internal Python package)
- **CLI entry point:** `slash-man` (replaces `sdd-commands`)
- **Documentation:** Clear distinction between "Slash Command Manager" (the tool) and "SDD Workflow" (the prompts/MCP components)

---

## Technical Considerations

### Dependency Audit

**Generator-only dependencies (move to SCM):**
- `questionary` (interactive CLI prompts)
- `tomli-w` (TOML writing)
- `rich` (terminal formatting)
- `Typer` (CLI framework)

**Shared dependencies (keep in both):**
- `pytest` (testing)
- `ruff` (linting)
- `pre-commit` (pre-commit hooks)
- Others TBD after full audit

### Import Path Updates

- Adjust any imports that reference the old repo structure
- Ensure `__version__.py` or equivalent is correctly placed in SCM repo
- Update any internal references to package paths in tests and docs

### CI/CD Pipeline

- Copy GitHub Actions workflows from original repo
- Update test paths and coverage targets in SCM's CI
- Update coverage targets and test exclusions in SDD workflow's CI
- Ensure both repos have independent semantic versioning and release automation

### Release Coordination

- **Initial release:** SCM publishes first (e.g., `v1.0.0`)
- **Follow-up:** SDD workflow publishes breaking-change release (next major version)
- **PyPI:** Both published as separate packages with clear distinctions
- **Entry point:** SCM registers `slash-man` CLI; SDD workflow no longer registers `sdd-commands`

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

- **Estimated Scope:** Full extraction across both repos (5 phases, ~40-60 engineering hours)
- **Risk Level:** Medium – involves restructuring repos and release automation
- **Testing Strategy:** End-to-end testing at each demoable unit; integration testing post-split
- **Rollback Plan:** Git history preserved; can revert if critical issues discovered post-release
- **Communication:** Coordinate with team before cutover; announce changes on completion

---

## Sign-Off

- **Spec Approved By:** [Pending user confirmation]
- **Date Approved:** [Pending user confirmation]
- **Next Steps:** Implementation planning and task breakdown

