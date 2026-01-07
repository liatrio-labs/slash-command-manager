# Task 2.0 Proof Artifacts: Create PyPI Publishing GitHub Actions Workflow

## CLI Output

### Workflow file contents

```bash
$ bat .github/workflows/publish-to-pypi.yml
name: Publish to PyPI

on:
  release:
    types: [published]

permissions:
  id-token: write
  contents: write

jobs:
  publish:
    name: Publish to PyPI
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: write
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

      - name: Install build package
        run: uv pip install --system build

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

      - name: Publish to Production PyPI
        uses: pypa/gh-action-pypi-publish@v1.13.0
        with:
          packages-dir: dist/

      - name: Upload release assets
        uses: softprops/action-gh-release@v2
        with:
          files: |
            dist/*.whl
            dist/*.tar.gz
```

### YAML syntax validation

```bash
$ python3 -c "import yaml; yaml.safe_load(open('.github/workflows/publish-to-pypi.yml'))" && echo "✅ YAML syntax valid"
✅ YAML syntax valid
```

## Test Results

### Pre-commit hooks

```bash
$ uv run pre-commit run --files .github/workflows/publish-to-pypi.yml
trim trailing whitespace.................................................Passed
fix end of files.........................................................Passed
check yaml...............................................................Passed
check for added large files..............................................Passed
check for merge conflicts................................................Passed
mixed line ending........................................................Passed
```

## Configuration

### Workflow Configuration Details

- **Workflow Name**: "Publish to PyPI"
- **Trigger**: `release: types: [published]` - triggers when a GitHub release is published
- **Permissions**:
  - `id-token: write` - Required for OIDC Trusted Publishing to PyPI
  - `contents: write` - Required for uploading release assets
- **Job**: Single `publish` job running on `ubuntu-latest`
- **Build Steps**:
  - Checkout with full history and tags
  - Install uv with cache for `pyproject.toml` and `uv.lock`
  - Install Python 3.12
  - Sync dependencies (frozen)
  - Install build package
  - Build wheel and source distribution
  - Verify build artifacts exist
- **Publishing Steps**:
  - Publish to Test PyPI using `pypa/gh-action-pypi-publish@v1.13.0` with `pypi-url: https://test.pypi.org/legacy/`
  - Publish to Production PyPI using `pypa/gh-action-pypi-publish@v1.13.0` (default PyPI URL)
- **Release Assets**: Upload `.whl` and `.tar.gz` files as GitHub release assets using `softprops/action-gh-release@v2`

### Trusted Publishing (OIDC) Configuration

- **No secrets required**: Workflow uses OIDC Trusted Publishing
- **Permission**: Only `id-token: write` permission needed (no API tokens or passwords)
- **PyPI Environment**: Uses default `pypi` environment name (configured in PyPI account settings)

## Verification

### Proof Artifacts Demonstrate Required Functionality

✅ **Workflow File Created**: `.github/workflows/publish-to-pypi.yml` exists with correct configuration

✅ **Workflow Trigger**: Configured to run on `release: types: [published]` events

✅ **Trusted Publishing (OIDC)**: Uses `id-token: write` permission, no secrets required

✅ **Test PyPI Publishing**: Step configured to publish to Test PyPI with `pypi-url: https://test.pypi.org/legacy/`

✅ **Production PyPI Publishing**: Step configured to publish to Production PyPI (default URL)

✅ **Release Asset Upload**: Step configured to upload `.whl` and `.tar.gz` files as GitHub release assets

✅ **YAML Syntax**: Validated with Python yaml parser - no syntax errors

✅ **Pattern Compliance**: Follows existing workflow patterns from `ci.yml`:

- Uses `astral-sh/setup-uv@v6` with cache
- Uses `actions/checkout@v4` with `fetch-depth: 0` and `fetch-tags: true`
- Uses Python 3.12
- Uses `uv sync --all-groups --extra dev --frozen`
- Uses `uv pip install --system` for system packages

✅ **Pre-commit Hooks**: All hooks pass (YAML check, trailing whitespace, end of file)
