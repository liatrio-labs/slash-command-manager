## Relevant Files

**Reference**: All file configurations and patterns should be copied/adapted from `docs/reference/original-spec-driven-workflow-repo-before-extraction.xml` (see CONTRIBUTING.md for reference file location guidelines)

- `pyproject.toml` - Core configuration file that needs semantic-release section, build system change to hatchling, license update to Apache-2.0, and dependency management updates
- `.github/workflows/release.yml` - Release workflow that needs to be restored to automated semantic-release pattern instead of manual tag-based releases
- `.github/chainguard/main-semantic-release.sts.yaml` - Missing authentication configuration file for GitHub OIDC/STS that needs to be created
- `.github/workflows/ci.yml` - CI workflow that needs uv installation step and coverage reporting restoration
- `.pre-commit-config.yaml` - Pre-commit configuration that needs commitlint hook and tool version updates
- `uv.lock` - Dependency lock file that exists but needs verification and consistency checks
- `LICENSE` - License file that needs to be changed from MIT to Apache-2.0
- `docs/` directory - Missing documentation files that need to be copied and updated from original repository
- `__version__.py` - Version file that needs integration with semantic-release
- `server.py` - Server file that needs to be included in package distribution
- `prompts/` directory - Directory with prompt files that need to be included in package distribution
- `README.md` - Documentation that needs repository reference updates

### Notes

- Current build system uses setuptools but needs to switch to hatchling for better package data handling
- The repository already has uv.lock but CI workflows still use pip instead of uv
- Package data inclusion is not properly configured - prompts/ and server.py are missing from built wheels
- Current release workflow is manual tag-based instead of automated semantic-release
- License is MIT but needs to be Apache-2.0 to match original specification
- Pre-commit configuration is missing commitlint hook
- Documentation files are missing from docs/ directory

## Tasks

- [x] 1.0 Critical Infrastructure Restoration
  - Demo Criteria: "Semantic release configuration functional; release workflow automated; GitHub authentication working"
  - Proof Artifact(s): "CLI: semantic-release --help; Diff: release.yml vs original; File: chainguard config present"
  - [x] 1.1 Add complete `[tool.semantic_release]` configuration to pyproject.toml by copying from original repository
  - [x] 1.2 Restore release workflow to use automated `workflow_run` trigger pattern by copying exact content from original repository
  - [x] 1.3 Create missing `.github/chainguard/main-semantic-release.sts.yaml` by copying from original repository
  - [x] 1.4 Configure semantic-release integration with `__version__.py` based on original repository pattern

- [x] 2.0 Package Production Readiness
  - Demo Criteria: "Package builds with hatchling; wheel includes all assets; slash-man command works after installation"
  - Proof Artifact(s): "CLI: python -m build && unzip -l dist/*.whl; Test: clean install test; CLI: slash-man --help"
  - [x] 2.1 Switch build system from setuptools to hatchling in pyproject.toml based on original repository configuration
  - [x] 2.2 Configure hatchling package data inclusion to include prompts/ directory and server.py based on original repository pattern
  - [x] 2.3 Verify and fix slash-man console script entry point configuration based on original repository
  - [x] 2.4 Test package building and installation in clean environment (docker container)

- [x] 3.0 Development Workflow Consistency
  - Demo Criteria: "uv.lock consistent; pre-commit hooks working; CI using uv with coverage"
  - Proof Artifact(s): "File: uv.lock present; CLI: pre-commit run --all-files; CI: workflow showing uv usage"
  - [x] 3.1 Update CI workflow to use `astral-sh/setup-uv@v6` installation step instead of pip by copying from original repository
  - [x] 3.2 Restore coverage reporting with Codecov integration in CI workflow based on original repository
  - [x] 3.3 Add commitlint hook to pre-commit configuration by copying from original repository
  - [x] 3.4 Run `pre-commit autoupdate` to get latest versions

- [x] 4.0 Documentation and Compliance
  - Demo Criteria: "All docs present; license Apache-2.0; references updated"
  - Proof Artifact(s): "Files: docs/ directory complete; File: LICENSE Apache-2.0; Diff: updated references"
  - [x] 4.1 Replace LICENSE file with Apache-2.0 license from original repository
  - [x] 4.2 Copy missing documentation files from original repository (mcp-prompt-support.md, operations.md, slash-command-generator.md)
  - [x] 4.3 Update repository references in README.md and configuration files for standalone operation based on original repository patterns
  - [x] 4.4 Verify all documented functionality works as advertised

- [x] 5.0 Repository Cleanup and Finalization
  - Demo Criteria: "Clean repository structure; cross-references correct; version management configured"
  - Proof Artifact(s): "CLI: ls -la showing clean structure; Test: reference validation; CLI: version check"
  - [x] 5.1 Update Python version consistency in pyproject.toml to match original repository
  - [x] 5.2 Verify all cross-references and repository links are updated correctly based on original repository patterns
  - [x] 5.3 Final testing and validation of all fixes in clean environment
