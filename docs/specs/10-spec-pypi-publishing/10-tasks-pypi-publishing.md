# 10-tasks-pypi-publishing.md

## Relevant Files

- `README.md` - Contains the main project documentation. Will add a "Building the Package" section with build and publishing instructions.
- `.github/workflows/publish-to-pypi.yml` - New GitHub Actions workflow file for publishing to PyPI on GitHub releases. Will use Trusted Publishing (OIDC) and publish to both Test PyPI and Production PyPI.
- `.github/workflows/ci.yml` - Existing CI workflow file. Will add a new `dev-release` job for generating dev releases with SHA-based versions on pull requests.
- `pyproject.toml` - Python project configuration file. Will update package metadata including license classifier, project URLs, and topic classifiers for PyPI publishing.

### Notes

- Follow the repository's established workflow patterns from `ci.yml` and `release.yml` (use `uv` for dependency management, Python 3.12, `astral-sh/setup-uv@v6` action).
- Use the repository's existing code organization, naming conventions, and style guidelines.
- Adhere to identified quality gates and pre-commit hooks.
- Workflow files should follow YAML formatting standards and match existing workflow structure.

## Tasks

### [x] 1.0 Add Build Documentation to README.md

#### 1.0 Proof Artifact(s)

- `README.md`: Updated file demonstrates build instructions are documented in a new "Building the Package" section
- Screenshot: README.md "Building the Package" section shows build commands (`python -m build`) and manual publishing instructions (`twine upload dist/*`) with notes about PyPI credentials and Test PyPI vs Production PyPI

#### 1.0 Tasks

- [x] 1.1 Locate the appropriate section in `README.md` for build documentation (after the "Development" section, before "SDD Workflow Integration")
- [x] 1.2 Create a new "Building the Package" section header with appropriate markdown formatting
- [x] 1.3 Add build instructions explaining the `python -m build` command and its purpose (creates distribution files)
- [x] 1.4 Document that builds create both wheel (`.whl`) and source distribution (`.tar.gz`) files in the `dist/` directory
- [x] 1.5 Add manual publishing instructions using `twine upload dist/*` command
- [x] 1.6 Include note about PyPI credentials requirement for manual publishing (API token or username/password)
- [x] 1.7 Add note about Test PyPI vs Production PyPI for manual publishing (use `--repository testpypi` flag for Test PyPI, omit for Production)
- [x] 1.8 Reference the existing `pyproject.toml` configuration file in the build instructions
- [x] 1.9 Verify markdown formatting is correct and consistent with existing README.md style
- [x] 1.10 Run markdownlint to ensure formatting compliance

### [ ] 2.0 Create PyPI Publishing GitHub Actions Workflow

#### 2.0 Proof Artifact(s)

- `CLI`: `cat .github/workflows/publish-to-pypi.yml` demonstrates workflow file exists with correct configuration including Trusted Publishing (OIDC), Test PyPI and Production PyPI publishing, and artifact uploads
- GitHub Actions: Workflow run triggered by test release shows successful build (`python -m build`), publish to Test PyPI, publish to Production PyPI, and upload of `.whl` and `.tar.gz` files as GitHub release assets

#### 2.0 Tasks

- [ ] 2.1 Create new file `.github/workflows/publish-to-pypi.yml` with workflow name "Publish to PyPI"
- [ ] 2.2 Configure workflow trigger to run on `release: types: [published]` events
- [ ] 2.3 Set workflow-level permissions: `id-token: write` and `contents: write` for OIDC Trusted Publishing and release asset uploads
- [ ] 2.4 Create a single job named `publish` that runs on `ubuntu-latest`
- [ ] 2.5 Add job-level permissions matching workflow-level permissions (`id-token: write`, `contents: write`)
- [ ] 2.6 Add checkout step using `actions/checkout@v4` with `fetch-depth: 0` and `fetch-tags: true`
- [ ] 2.7 Add step to install uv using `astral-sh/setup-uv@v6` with cache enabled for `pyproject.toml` and `uv.lock`
- [ ] 2.8 Add step to install Python 3.12 using `uv python install 3.12`
- [ ] 2.9 Add step to sync dependencies using `uv sync --all-groups --extra dev --frozen`
- [ ] 2.10 Add step to install build package using `uv pip install --system build`
- [ ] 2.11 Add step to build package using `uv run python -m build --wheel --sdist`
- [ ] 2.12 Add step to verify build artifacts exist (list `dist/` directory contents)
- [ ] 2.13 Add step to publish to Test PyPI using `pypa/gh-action-pypi-publish@v1.13.0` action with `pypi-url: https://test.pypi.org/legacy/` and `packages-dir: dist/`
- [ ] 2.14 Add step to publish to Production PyPI using `pypa/gh-action-pypi-publish@v1.13.0` action with `packages-dir: dist/` (default PyPI URL)
- [ ] 2.15 Add step to upload build artifacts (`.whl` and `.tar.gz` files) as GitHub release assets using `softprops/action-gh-release@v2` with `files` parameter set to `dist/*.whl` and `dist/*.tar.gz` (requires `contents: write` permission)
- [ ] 2.16 Verify workflow YAML syntax is valid and follows existing workflow patterns
- [ ] 2.17 Ensure workflow uses Trusted Publishing (OIDC) - no secrets required, only `id-token: write` permission

### [ ] 3.0 Update Package Metadata in pyproject.toml

#### 3.0 Proof Artifact(s)

- `pyproject.toml`: Updated file demonstrates complete metadata with Apache License 2.0 classifier (`License :: OSI Approved :: Apache Software License`), `project.urls` section with homepage, repository, documentation, and issues URLs, and appropriate topic classifiers for CLI tool and AI coding assistant
- CLI: `python -m build` succeeds without metadata warnings, confirming all required PyPI metadata fields are present and properly formatted

#### 3.0 Tasks

- [ ] 3.1 Review current `pyproject.toml` metadata to identify missing PyPI publishing requirements
- [ ] 3.2 Add Apache License 2.0 classifier: `"License :: OSI Approved :: Apache Software License"` to the `classifiers` list
- [ ] 3.3 Create `[project.urls]` section in `pyproject.toml` with the following keys:
  - `Homepage = "https://github.com/liatrio-labs/slash-command-manager"`
  - `Repository = "https://github.com/liatrio-labs/slash-command-manager"`
  - `Documentation = "https://github.com/liatrio-labs/slash-command-manager#readme"`
  - `Issues = "https://github.com/liatrio-labs/slash-command-manager/issues"`
- [ ] 3.4 Add topic classifier `"Topic :: Scientific/Engineering :: Artificial Intelligence"` to classifiers list
- [ ] 3.5 Add topic classifier `"Topic :: Software Development :: Code Generators"` to classifiers list
- [ ] 3.6 Add topic classifier `"Topic :: Software Development :: Build Tools"` to classifiers list
- [ ] 3.7 Add environment classifier `"Environment :: Console"` to classifiers list
- [ ] 3.8 Verify `license = { file = "LICENSE" }` is correctly configured (already present)
- [ ] 3.9 Run `python -m build` locally to verify no metadata warnings are generated
- [ ] 3.10 Verify TOML syntax is valid and properly formatted

### [ ] 4.0 Add Dev Release Job to CI Workflow for Test PyPI Publishing

#### 4.0 Proof Artifact(s)

- `CLI`: `cat .github/workflows/ci.yml` demonstrates new `dev-release` job exists with semantic-release dev version generation using SHA-based build metadata and is gated behind `RUN_DEV_RELEASE_JOBS` repository variable
- GitHub Actions: Workflow run on PR with `RUN_DEV_RELEASE_JOBS=true` shows dev release job generates version like `0.1.0-dev.1+abc123def`, builds package, and publishes to Test PyPI successfully
- GitHub Actions: Workflow run on PR with `RUN_DEV_RELEASE_JOBS` unset or false shows dev release job is skipped
- Test PyPI: Dev release package appears on Test PyPI with SHA-based version, demonstrating workflow testing capability

#### 4.0 Tasks

- [ ] 4.1 Open `.github/workflows/ci.yml` and locate the end of the existing jobs section
- [ ] 4.2 Create new job named `dev-release` that runs on `ubuntu-latest`
- [ ] 4.3 Add job condition combining pull request check and repository variable gate: `if: ${{ github.event_name == 'pull_request' && vars.RUN_DEV_RELEASE_JOBS == 'true' }}`
- [ ] 4.5 Set job permissions: `id-token: write` and `contents: read` for OIDC Trusted Publishing
- [ ] 4.6 Add checkout step using `actions/checkout@v4` with `fetch-depth: 0` and `fetch-tags: true`
- [ ] 4.7 Add step to install uv using `astral-sh/setup-uv@v6` with cache enabled for `pyproject.toml` and `uv.lock`
- [ ] 4.8 Add step to install Python 3.12 using `uv python install 3.12`
- [ ] 4.9 Add step to sync dependencies using `uv sync --all-groups --extra dev --frozen`
- [ ] 4.10 Add step to install python-semantic-release using `uv pip install --system "python-semantic-release>=10.0.0,<11.0.0"`
- [ ] 4.11 Add step to install build package using `uv pip install --system build`
- [ ] 4.12 Add step to generate dev version using semantic-release with output capture: create step with `id: dev-version` that runs `semantic-release -c .releaserc.toml version --as-prerelease --prerelease-token dev --build-metadata ${{ github.sha }} --no-push --no-vcs-release --no-commit --no-tag --print`, captures output to `$GITHUB_OUTPUT` as `version`, and echoes the generated version (semantic-release updates `pyproject.toml` in-place even with `--no-commit` flag)
- [ ] 4.13 Add step to verify version was generated correctly (check that `${{ steps.dev-version.outputs.version }}` contains dev prerelease token and SHA)
- [ ] 4.14 Add step to build package using `uv run python -m build --wheel --sdist` with the generated dev version
- [ ] 4.15 Add step to verify build artifacts exist (list `dist/` directory contents)
- [ ] 4.16 Add step to publish to Test PyPI using `pypa/gh-action-pypi-publish@v1.13.0` action with `pypi-url: https://test.pypi.org/legacy/` and `packages-dir: dist/`
- [ ] 4.17 Verify workflow YAML syntax is valid and follows existing workflow patterns
- [ ] 4.18 Ensure job uses Trusted Publishing (OIDC) - no secrets required, only `id-token: write` permission
- [ ] 4.19 Verify job is properly gated and will skip when `RUN_DEV_RELEASE_JOBS` variable is not set or set to false
