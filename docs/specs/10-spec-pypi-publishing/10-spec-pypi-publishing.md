# 10-spec-pypi-publishing.md

## Introduction/Overview

This specification enables automated publishing of the `slash-man` Python package to PyPI (Python Package Index), making it available for installation via `pip` and `uvx`. The feature adds build documentation to the repository and creates a CI/CD workflow that automatically publishes to PyPI when new GitHub releases are created. This enables users to install and use `slash-man` directly from PyPI without needing to clone the repository or build from source.

## Goals

1. **Enable PyPI Distribution** - Make `slash-man` installable via `pip install slash-man` and `uvx slash-man`
2. **Automate Publishing** - Create CI/CD workflow that publishes to PyPI automatically on GitHub releases
3. **Document Build Process** - Add clear build instructions to README.md for manual builds and contributor reference
4. **Support Test PyPI** - Enable testing publishing workflow on Test PyPI before production releases
5. **Integrate with Existing Release Workflow** - Coordinate with existing semantic-release process without disrupting it
6. **Enable Dev Release Testing** - Create CI job that generates dev releases with SHA-based versions on PRs for testing PyPI publishing workflow

## User Stories

**As a** Python developer using CLI tools, **I want to** install `slash-man` from PyPI using `pip install slash-man` or `uvx slash-man` **so that** I can use the tool without cloning the repository or managing dependencies manually.

**As a** release engineer, **I want** PyPI publishing to happen automatically when a GitHub release is created **so that** releases are consistent and require no manual intervention.

**As a** contributor, **I want** clear build instructions in the README **so that** I can test package builds locally and understand the release process.

**As a** project maintainer, **I want** to test PyPI publishing on Test PyPI first **so that** I can verify the publishing workflow before affecting production PyPI.

**As a** developer working on a pull request, **I want** dev releases to be automatically generated with SHA-based versions **so that** I can test the PyPI publishing workflow without affecting production releases.

## Demoable Units of Work

### [Unit 1]: Build Documentation

**Purpose:** Provide clear instructions for building the package locally, enabling contributors to test builds and understand the release process.

**Functional Requirements:**

- The README.md shall include a "Building the Package" section with build instructions
- The build instructions shall include the command `python -m build` to create distribution files
- The build instructions shall include the command `twine upload dist/*` for manual publishing (with note about PyPI credentials and publishing to test vs prd)
- The build instructions shall reference the existing `pyproject.toml` configuration
- The build instructions shall note that builds create both wheel (`.whl`) and source distribution (`.tar.gz`) files in the `dist/` directory

**Proof Artifacts:**

- `README.md`: Updated file demonstrates build instructions are documented
- `Screenshot`: README.md "Building the Package" section shows build commands

### [Unit 2]: PyPI Publishing CI Workflow

**Purpose:** Automate PyPI publishing when GitHub releases are created, eliminating manual publishing steps and ensuring consistent releases.

**Functional Requirements:**

- The system shall create a new GitHub Actions workflow file `.github/workflows/publish-to-pypi.yml`
- The workflow shall trigger on GitHub release events (`release: types: [published]`)
- The workflow shall use Trusted Publishing (OIDC) for PyPI authentication (no secrets required)
- The workflow shall build the package using `python -m build`
- The workflow shall verify the package builds successfully before publishing
- The workflow shall publish to Test PyPI first, then to Production PyPI
- The workflow shall use the `pypa/gh-action-pypi-publish@v1.13.0` action for publishing
- The workflow shall upload build artifacts (`.whl` and `.tar.gz` files) as GitHub release assets
- The workflow shall require `id-token: write` and `contents: read` permissions for OIDC
- The workflow shall use a PyPI environment named `pypi` for Trusted Publishing configuration

**Proof Artifacts:**

- `CLI`: `cat .github/workflows/publish-to-pypi.yml` demonstrates workflow file exists with correct configuration
- `GitHub Actions`: Workflow run triggered by test release shows successful build and publish steps
- `PyPI`: Package appears on Test PyPI and Production PyPI after workflow completion (separate, standalone validation - not necessary as part of CI)

### [Unit 3]: Package Metadata Updates

**Purpose:** Ensure package metadata in `pyproject.toml` is complete and optimized for PyPI publishing, improving discoverability and providing accurate package information.

**Functional Requirements:**

- The system shall review and update package metadata in `pyproject.toml` for PyPI publishing requirements
- The metadata shall include a proper license classifier matching the LICENSE file (Apache License 2.0)
- The metadata shall include `project.urls` section with homepage and repository URLs pointing to the GitHub repository
- The metadata shall include appropriate classifiers for the package type (CLI tool, MCP server)
- The metadata shall ensure all required fields are present and properly formatted for PyPI

**Proof Artifacts:**

- `pyproject.toml`: Updated file demonstrates complete metadata with license classifier, URLs, and appropriate classifiers
- `CLI`: `python -m build` succeeds without metadata warnings

### [Unit 4]: Dev Release Testing Job

**Purpose:** Enable automated testing of PyPI publishing workflow on pull requests by generating dev releases with SHA-based versions, allowing developers to validate the publishing process without affecting production releases.

**Functional Requirements:**

- The system shall add a new job `dev-release` to the existing `.github/workflows/ci.yml` workflow
- The job shall trigger only on pull request events (not on pushes to main)
- The job shall be gated behind a repository variable `RUN_DEV_RELEASE_JOBS` (job runs only when variable is set to `true`)
- The job shall use `python-semantic-release` to generate a dev prerelease version with SHA-based build metadata
- The version generation command shall use `--as-prerelease --prerelease-token dev --build-metadata ${{ github.sha }}` to create versions like `0.1.0-dev.1+abc123def`
- The version generation shall use `--no-push --no-vcs-release --no-commit --no-tag` to avoid creating Git tags or commits
- The job shall build the package using `python -m build` with the generated dev version
- The job shall publish the built package to Test PyPI using Trusted Publishing (OIDC)
- The job shall use the same Trusted Publishing configuration as the production workflow
- The job shall require `id-token: write` and `contents: read` permissions for OIDC

**Proof Artifacts:**

- `CLI`: `cat .github/workflows/ci.yml` demonstrates `dev-release` job exists with correct configuration
- `GitHub Actions`: Workflow run on PR shows dev release job generates version with SHA, builds package, and publishes to Test PyPI
- `Test PyPI`: Dev release package appears on Test PyPI with SHA-based version (e.g., `slash-man-0.1.0-dev.1+abc123def`)

## Non-Goals (Out of Scope)

1. **Homebrew Distribution** - Publishing to Homebrew is explicitly out of scope for this spec (may be addressed in a future spec)
2. **Scoop/Winget/Chocolatey Distribution** - Windows package manager distribution is out of scope
3. **Manual Publishing Instructions** - While build commands are documented, detailed manual publishing steps (API token setup, etc.) are not required beyond basic `twine upload` command (for test and prd)
4. **Package Version Management** - Version management is handled by existing semantic-release workflow and is not modified by this spec
5. **Pre-release Testing Workflow** - Automated testing on Test PyPI before production is included via dev release job, but manual pre-release validation workflows are out of scope
6. **Retry Logic** - Automatic retry mechanisms for failed publishes are out of scope (standard CI failure behavior is sufficient)
7. **PyPI Trusted Publishing Configuration Documentation** - Trusted Publishing setup instructions are already documented elsewhere and do not need to be added to this spec

## Design Considerations

No specific design requirements identified. The workflow will follow standard GitHub Actions patterns and PyPI publishing best practices.

## Repository Standards

Implementation shall follow established repository patterns and conventions:

- **Workflow Structure**: Follow existing `.github/workflows/` patterns (see `ci.yml` and `release.yml`)
- **Documentation Style**: Match README.md formatting and structure (see existing sections)
- **Python Tooling**: Use `uv` for dependency management (consistent with existing workflows)
- **Build System**: Use `hatchling` build backend (already configured in `pyproject.toml`)
- **Commit Messages**: Follow Conventional Commits specification (already established)
- **Code Style**: Follow PEP 8 and use `ruff` for linting (consistent with existing codebase)

## Technical Considerations

1. **Build Backend**: The project uses `hatchling` as the build backend (configured in `pyproject.toml`). The build process uses `python -m build` which works with any PEP 517-compliant backend.

2. **Custom Build Hook**: The project includes `hatch_build.py` with a custom build hook that embeds git commit SHA. This hook must continue to work correctly during CI builds.

3. **Package Name**: The package is named `slash-man` in `pyproject.toml` (not `slash-command-manager`). PyPI publishing will use this name.

4. **Existing Release Workflow**: The repository has a `release.yml` workflow that uses semantic-release. The new PyPI publishing workflow must not interfere with this process and should trigger independently on releases.

5. **Python Version**: The project requires Python >=3.12. The CI workflow should use Python 3.12 for builds.

6. **Dependencies**: The build process requires `build` package. The workflow should install this via `uv pip install build` or include it in workflow dependencies.

7. **Trusted Publishing Setup**: PyPI Trusted Publishing requires manual configuration in PyPI account settings. This is a one-time setup that cannot be automated.

8. **Test PyPI vs Production PyPI**: The workflow should publish to Test PyPI first, then Production PyPI. The `pypa/gh-action-pypi-publish` action supports this via configuration.

9. **Dev Release Testing**: A new `dev-release` job in `ci.yml` will use `python-semantic-release` to generate dev prerelease versions on pull requests:
   - Uses `semantic-release version --as-prerelease --prerelease-token dev --build-metadata ${{ github.sha }}` to create versions like `0.1.0-dev.1+abc123def`
   - Uses `--no-push --no-vcs-release --no-commit --no-tag` to avoid creating Git tags or commits
   - Builds and publishes to Test PyPI for workflow validation
   - Enables testing PyPI publishing workflow without affecting production releases
   - Each commit SHA gets a unique version via build metadata, ensuring test packages are distinguishable

10. **Semantic-Release Workflow Order**: The existing `release.yml` workflow uses `python-semantic-release` which:

- Updates `pyproject.toml` version via `version_variables` configuration (`pyproject.toml:project.version`)
- Commits `uv.lock` (listed in `assets` configuration) alongside version updates
- Generates and commits `CHANGELOG.md` (via `changelog.default_templates`)
- Creates a GitHub release after committing and tagging
- The PyPI publishing workflow triggers on `release: types: [published]`, ensuring it runs AFTER semantic-release has completed all commits and created the release
- **Current workflow order**: The `release.yml` workflow runs `uv lock` before semantic-release, stages `uv.lock`, then semantic-release updates `pyproject.toml` and commits everything together
- **Verification needed**: Ensure that `uv.lock` doesn't need to be updated AFTER the version change in `pyproject.toml`. If the package's own version affects the lock file, consider using `build_command` in `.releaserc.toml` to run `uv lock --upgrade-package slash-man` after version stamping, or use the two-step process documented in python-semantic-release uv integration guide
- **Files committed before release**: `pyproject.toml` (version), `uv.lock` (dependencies), `CHANGELOG.md` (release notes) - all committed in a single commit by semantic-release before the GitHub release is created

## Success Metrics

1. **Package Availability**: Package is successfully published to PyPI and installable via `pip install slash-man` within 5 minutes of release creation
2. **Workflow Reliability**: PyPI publishing workflow succeeds on 100% of release events (after initial Trusted Publishing configuration)
3. **Documentation Completeness**: Build instructions are present in README.md and enable contributors to build packages locally
4. **Zero Manual Steps**: After initial Trusted Publishing setup, releases require zero manual intervention for PyPI publishing
5. **Test PyPI Validation**: First release successfully publishes to Test PyPI before production, validating the workflow
6. **Dev Release Testing**: Dev release job successfully generates SHA-based versions and publishes to Test PyPI on pull requests, enabling workflow testing without production impact

## Open Questions

1. ~~Should the workflow publish to Test PyPI on every release, or only on the first release for validation?~~ **RESOLVED**: Dev release job in CI workflow publishes to Test PyPI on PR commits for testing. Production workflow publishes to both Test PyPI and Production PyPI on releases.
2. ~~Should build artifacts (`.whl` and `.tar.gz` files) be uploaded as GitHub release assets, or is PyPI distribution sufficient?~~ **RESOLVED**: Build artifacts will be uploaded as GitHub release assets in addition to PyPI distribution.
3. ~~Should the workflow include a step to verify the published package can be installed and the CLI works, or is build verification sufficient?~~ **RESOLVED**: Build verification is sufficient; integration tests handle install testing.

## Package Metadata Analysis

Based on review of `pyproject.toml`, the following metadata updates are recommended for PyPI publishing:

1. **License Classifier**: Currently missing. Should add `"License :: OSI Approved :: Apache Software License"` to match the Apache 2.0 LICENSE file.

2. **Project URLs**: Currently missing `[project.urls]` section. Should add:
   - `Homepage`: GitHub repository URL
   - `Repository`: GitHub repository URL
   - `Documentation`: Link to README or docs (if applicable)
   - `Issues`: GitHub issues URL

3. **Additional Classifiers**: Consider adding:
   - `"Topic :: Scientific/Engineering :: Artificial Intelligence"` (primary AI classifier - package is for AI coding assistants)
   - `"Topic :: Software Development :: Code Generators"` (generates slash command configurations)
   - `"Topic :: Software Development :: Build Tools"` (development tool for AI-assisted workflows)
   - `"Environment :: Console"` (CLI tool)

4. **License Field**: Currently uses `license = { file = "LICENSE" }` which is correct, but ensure LICENSE file is properly included in the package.

These updates will improve package discoverability on PyPI and provide users with better information about the package.
