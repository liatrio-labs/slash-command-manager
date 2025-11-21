# Task 4.0 Proof Artifacts: Add Dev Release Job to CI Workflow for Test PyPI Publishing

## CLI Output

### dev-release job in ci.yml

```bash
$ bat .github/workflows/ci.yml | grep -A 60 "dev-release:"
  dev-release:
    name: Dev Release (Test PyPI)
    runs-on: ubuntu-latest
    if: ${{ github.event_name == 'pull_request' && vars.RUN_DEV_RELEASE_JOBS == 'true' }}
    permissions:
      id-token: write
      contents: read
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          fetch-tags: true

      - name: Install uv (with cache)
        uses: astral-sh/setup-uv@v6
        with:
          enable-cache: true
          cache-dependency-glob: |
            **/pyproject.toml
            **/uv.lock

      - name: Install Python
        run: uv python install 3.12

      - name: Sync dependencies (frozen)
        run: uv sync --all-groups --extra dev --frozen

      - name: Install python-semantic-release
        run: uv pip install --system "python-semantic-release>=10.0.0,<11.0.0"

      - name: Install build package
        run: uv pip install --system build

      - name: Generate dev version
        id: dev-version
        run: |
          VERSION=$(semantic-release -c .releaserc.toml version --as-prerelease --prerelease-token dev --build-metadata ${{ github.sha }} --no-push --no-vcs-release --no-commit --no-tag --print)
          echo "Generated version: $VERSION"
          echo "version=$VERSION" >> $GITHUB_OUTPUT

      - name: Verify version was generated
        run: |
          VERSION="${{ steps.dev-version.outputs.version }}"
          SHA_SHORT="${{ github.sha }}"
          SHA_SHORT="${SHA_SHORT:0:7}"
          if [[ ! "$VERSION" =~ dev ]] || [[ ! "$VERSION" =~ $SHA_SHORT ]]; then
            echo "❌ Version verification failed: $VERSION"
            echo "Expected version to contain 'dev' and SHA prefix '$SHA_SHORT'"
            exit 1
          fi
          echo "✅ Version verified: $VERSION"

      - name: Build package
        run: uv run python -m build --wheel --sdist

      - name: Verify build artifacts
        run: |
          echo "Build artifacts:"
          ls -lh dist/
          if [ -z "$(ls -A dist/*.whl 2>/dev/null)" ] || [ -z "$(ls -A dist/*.tar.gz 2>/dev/null)" ]; then
            echo "❌ Build artifacts missing!"
            exit 1
          fi
          echo "✅ Build artifacts verified"

      - name: Publish to Test PyPI
        uses: pypa/gh-action-pypi-publish@v1.13.0
        with:
          pypi-url: https://test.pypi.org/legacy/
          packages-dir: dist/
```

### YAML syntax validation

```bash
$ python3 -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))" && echo "✅ YAML syntax valid"
✅ YAML syntax valid
```

## Test Results

### Pre-commit hooks

```bash
$ uv run pre-commit run --files .github/workflows/ci.yml
trim trailing whitespace.................................................Passed
fix end of files.........................................................Passed
check yaml...............................................................Passed
check for added large files..............................................Passed
check for merge conflicts................................................Passed
mixed line ending........................................................Passed
```

## Configuration

### Dev Release Job Configuration

- **Job Name**: `dev-release` (display name: "Dev Release (Test PyPI)")
- **Trigger Condition**: `if: ${{ github.event_name == 'pull_request' && vars.RUN_DEV_RELEASE_JOBS == 'true' }}`
  - Only runs on pull request events
  - Gated behind repository variable `RUN_DEV_RELEASE_JOBS` (must be set to `'true'`)
  - Will skip when variable is not set or set to false
- **Permissions**:
  - `id-token: write` - Required for OIDC Trusted Publishing to PyPI
  - `contents: read` - Required for checkout
- **Version Generation**:
  - Uses `python-semantic-release` with `--as-prerelease --prerelease-token dev`
  - Adds build metadata with `--build-metadata ${{ github.sha }}`
  - Uses `--no-push --no-vcs-release --no-commit --no-tag` to avoid creating Git tags or commits
  - Uses `--print` flag to output version to stdout
  - Captures version output to `$GITHUB_OUTPUT` as `version`
  - Updates `pyproject.toml` in-place even with `--no-commit` flag
- **Version Verification**: Checks that generated version contains:
  - `dev` prerelease token
  - SHA prefix (first 7 characters of commit SHA)
- **Build and Publish**:
  - Builds package using `uv run python -m build --wheel --sdist`
  - Verifies build artifacts exist
  - Publishes to Test PyPI using `pypa/gh-action-pypi-publish@v1.13.0`

### Trusted Publishing (OIDC) Configuration

- **No secrets required**: Job uses OIDC Trusted Publishing
- **Permission**: Only `id-token: write` permission needed (no API tokens or passwords)
- **PyPI Environment**: Uses default `pypi` environment name (configured in PyPI account settings)

## Verification

### Proof Artifacts Demonstrate Required Functionality

✅ **Job Created**: `dev-release` job exists in `.github/workflows/ci.yml`

✅ **Job Condition**: Configured with `if: ${{ github.event_name == 'pull_request' && vars.RUN_DEV_RELEASE_JOBS == 'true' }}`

- Only runs on pull request events
- Gated behind `RUN_DEV_RELEASE_JOBS` repository variable
- Will skip when variable is not set or set to false

✅ **Semantic-Release Version Generation**: Uses semantic-release to generate dev prerelease version with SHA-based build metadata:

- Command: `semantic-release -c .releaserc.toml version --as-prerelease --prerelease-token dev --build-metadata ${{ github.sha }} --no-push --no-vcs-release --no-commit --no-tag --print`
- Captures output to `$GITHUB_OUTPUT` as `version`
- Updates `pyproject.toml` in-place

✅ **Version Verification**: Step verifies generated version contains:

- `dev` prerelease token
- SHA prefix from commit SHA

✅ **Build and Publish**: Builds package and publishes to Test PyPI using Trusted Publishing (OIDC)

✅ **YAML Syntax**: Validated with Python yaml parser - no syntax errors

✅ **Pattern Compliance**: Follows existing workflow patterns from `ci.yml`:

- Uses `astral-sh/setup-uv@v6` with cache
- Uses `actions/checkout@v4` with `fetch-depth: 0` and `fetch-tags: true`
- Uses Python 3.12
- Uses `uv sync --all-groups --extra dev --frozen`
- Uses `uv pip install --system` for system packages

✅ **Pre-commit Hooks**: All hooks pass (YAML check, trailing whitespace, end of file)

✅ **Trusted Publishing**: Uses `id-token: write` permission, no secrets required
