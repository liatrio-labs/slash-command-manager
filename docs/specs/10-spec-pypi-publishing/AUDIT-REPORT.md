# Audit Report: PyPI Publishing Spec and Tasks

**Date**: 2025-01-15
**Auditor**: AI Assistant
**Scope**: `10-spec-pypi-publishing.md` and `10-tasks-pypi-publishing.md`

## Executive Summary

The spec and tasks are generally well-structured and comprehensive, but several issues were identified that need to be addressed before implementation:

1. **Critical**: Unit numbering inconsistency in spec (Units 1, 2, 4, 3 instead of sequential)
2. **Important**: Artifact upload action not specified
3. **Minor**: Several task details need clarification

## Critical Issues

### 1. Unit Numbering Inconsistency in Spec

**Location**: `10-spec-pypi-publishing.md`

**Issue**: Units are numbered 1, 2, 4, 3 instead of sequential 1, 2, 3, 4.

**Current Order**:

- Unit 1: Build Documentation
- Unit 2: PyPI Publishing CI Workflow
- Unit 4: Dev Release Testing Job
- Unit 3: Package Metadata Updates

**Impact**: Confusing for readers and breaks sequential ordering convention.

**Recommendation**: Reorder units to be sequential:

- Unit 1: Build Documentation
- Unit 2: PyPI Publishing CI Workflow
- Unit 3: Package Metadata Updates
- Unit 4: Dev Release Testing Job

**Action Required**: Update spec file to reorder Unit 3 and Unit 4 sections.

## Important Issues

### 2. Repository Variable Syntax Verification

**Location**: `10-tasks-pypi-publishing.md`, Task 4.3

**Issue**: Uses `vars.RUN_DEV_RELEASE_JOBS` syntax which may not be correct for GitHub Actions.

**Current Syntax**: `if: vars.RUN_DEV_RELEASE_JOBS == 'true'`

**Research Result**: According to GitHub Actions documentation, repository variables are accessed via `${{ vars.VARIABLE_NAME }}` syntax in expressions. For conditions, the syntax `if: ${{ vars.USE_VARIABLES == 'true' }}` is correct with quotes around the string value.

**Current Syntax**: `if: vars.RUN_DEV_RELEASE_JOBS == 'true'`

**Verification**: The syntax is correct. GitHub Actions requires:

- Quotes around string values (`'true'`)
- Use of `${{ }}` expression syntax in `if` conditions: `if: ${{ vars.RUN_DEV_RELEASE_JOBS == 'true' }}`

**Recommendation**: Update task to use proper expression syntax:

```yaml
if: ${{ vars.RUN_DEV_RELEASE_JOBS == 'true' }}
```

**Action Required**: Update task to use `${{ }}` expression syntax for the condition.

### 3. Artifact Upload Action Not Specified

**Location**: `10-tasks-pypi-publishing.md`, Task 2.15

**Issue**: Task mentions two options (`actions/upload-release-asset` or `softprops/action-gh-release@v1`) but doesn't specify which one to use.

**Current Task**: "Add step to upload build artifacts (`.whl` and `.tar.gz` files) as GitHub release assets using `actions/upload-release-asset` or `softprops/action-gh-release@v1`"

**Impact**: Implementer must choose without guidance.

**Research Result**: Based on GitHub Actions best practices and marketplace analysis:

- `softprops/action-gh-release@v2` is the current, actively maintained version (v1 is outdated)
- `softprops/action-gh-release` is the modern, feature-rich solution for creating releases and uploading assets
- `actions/upload-release-asset` is deprecated and not recommended
- `softprops/action-gh-release` supports uploading multiple files, release notes, and is widely adopted

**Recommendation**: Use `softprops/action-gh-release@v2` for uploading release assets. Example configuration:

```yaml
- name: Upload release assets
  uses: softprops/action-gh-release@v2
  with:
    files: |
      dist/*.whl
      dist/*.tar.gz
```

**Action Required**: Update task to specify `softprops/action-gh-release@v2` with example configuration.

### 4. Workflow Trigger Syntax Verification

**Location**: `10-spec-pypi-publishing.md`, Unit 2, and `10-tasks-pypi-publishing.md`, Task 2.2

**Issue**: Spec says `release: types: [published]` but GitHub Actions syntax should be verified.

**Current**: `release: types: [published]`

**Verification**: GitHub Actions workflow trigger syntax should be:

```yaml
on:
  release:
    types: [published]
```

**Action Required**: Verify syntax is correct (appears correct, but should be confirmed).

## Minor Issues and Gaps

### 6. Build Artifact Verification Method

**Location**: `10-tasks-pypi-publishing.md`, Tasks 2.12 and 4.15

**Issue**: Tasks say "list `dist/` directory contents" but don't specify how to verify artifacts exist properly.

**Current**: "Add step to verify build artifacts exist (list `dist/` directory contents)"

**Recommendation**: Specify verification method:

```yaml
- name: Verify build artifacts
  run: |
    ls -lh dist/
    test -f dist/*.whl || exit 1
    test -f dist/*.tar.gz || exit 1
```

**Action Required**: Add specific verification commands to tasks.

### 7. Dev Release Version Capture Method

**Location**: `10-tasks-pypi-publishing.md`, Task 4.12

**Issue**: Task says "capture output" but doesn't specify how to capture the version string.

**Current**: "Add step to generate dev version using semantic-release: `semantic-release -c .releaserc.toml version --as-prerelease --prerelease-token dev --build-metadata ${{ github.sha }} --no-push --no-vcs-release --no-commit --no-tag --print` and capture output"

**Recommendation**: Specify how to capture output:

```yaml
- name: Generate dev version
  id: dev-version
  run: |
    VERSION=$(semantic-release -c .releaserc.toml version --as-prerelease --prerelease-token dev --build-metadata ${{ github.sha }} --no-push --no-vcs-release --no-commit --no-tag --print)
    echo "version=$VERSION" >> $GITHUB_OUTPUT
    echo "Generated version: $VERSION"
```

**Action Required**: Add specific method for capturing version output.

### 8. PyPI Action Version Verification

**Location**: `10-spec-pypi-publishing.md`, Unit 2, and `10-tasks-pypi-publishing.md`, Tasks 2.13, 2.14, 4.16

**Issue**: Specifies `pypa/gh-action-pypi-publish@v1.13.0` but should verify this is the latest/appropriate version.

**Recommendation**: Check PyPI action releases and use latest stable version, or use major version pin (`@v1`) for automatic updates.

**Action Required**: Verify and update version if needed.

### 9. Missing Build Verification in Dev Release

**Location**: `10-tasks-pypi-publishing.md`, Task 4.14

**Issue**: Task says "build package using `uv run python -m build --wheel --sdist` with the generated dev version" but doesn't explain how the dev version is applied.

**Clarification Needed**:

- Does semantic-release update `pyproject.toml` even with `--no-commit`?
- How is the version applied to the build?

**Evidence**: Looking at `release.yml`, semantic-release updates `pyproject.toml` via `version_variables` configuration, so it should work even with `--no-commit` (changes file but doesn't commit).

**Action Required**: Add clarification that semantic-release updates `pyproject.toml` in-place even with `--no-commit` flag.

### 10. Task 4.4 Condition Logic

**Location**: `10-tasks-pypi-publishing.md`, Task 4.4

**Issue**: Task says "combine with variable check" but doesn't specify how to combine conditions.

**Current**: Two separate `if` conditions mentioned.

**Recommendation**: Use logical AND:

```yaml
if: github.event_name == 'pull_request' && vars.RUN_DEV_RELEASE_JOBS == 'true'
```

**Action Required**: Specify exact condition syntax.

## Consistency Issues

### 11. Build Command Consistency

**Location**: Multiple locations

**Status**: ✅ **Consistent** - All tasks use `uv run python -m build --wheel --sdist` which matches existing workflows.

### 12. Python Version Consistency

**Location**: Multiple locations

**Status**: ✅ **Consistent** - All tasks specify Python 3.12 which matches project requirements.

### 13. UV Usage Consistency

**Location**: Multiple locations

**Status**: ✅ **Consistent** - All tasks use `uv` for dependency management matching repository patterns.

## Missing Information

### 14. Trusted Publishing Setup Instructions

**Location**: `10-spec-pypi-publishing.md`, Technical Considerations #7

**Issue**: Spec mentions "Trusted Publishing setup instructions are already documented elsewhere" but doesn't provide reference.

**Recommendation**: Add link to PyPI Trusted Publishing documentation or internal documentation.

**Action Required**: Add reference to Trusted Publishing setup documentation.

### 15. Test PyPI vs Production PyPI URLs

**Location**: `10-tasks-pypi-publishing.md`, Tasks 2.13, 2.14, 4.16

**Status**: ✅ **Correct** - URLs are specified correctly:

- Test PyPI: `https://test.pypi.org/legacy/`
- Production PyPI: (default, no URL needed)

## Positive Observations

1. ✅ **Comprehensive Coverage**: Spec covers all necessary aspects of PyPI publishing
2. ✅ **Clear Proof Artifacts**: Each unit has well-defined proof artifacts
3. ✅ **Follows Repository Patterns**: Tasks reference existing workflow patterns correctly
4. ✅ **Non-Goals Section**: Clear about what's out of scope
5. ✅ **Technical Considerations**: Good coverage of technical details
6. ✅ **Integration Planning**: Thoughtful consideration of semantic-release integration

## Recommendations Summary

### Immediate Actions Required

1. **Reorder spec units** to be sequential (1, 2, 3, 4)
2. **Specify artifact upload action** (use `softprops/action-gh-release@v2`)
3. **Add version capture method** for dev release job
4. **Update repository variable syntax** to use `${{ }}` expression syntax

### Should Address Before Implementation

1. Add specific build artifact verification commands
2. Clarify how dev version is applied to build
3. Specify exact condition syntax for Task 4.4
4. Verify PyPI action version is current
5. Add reference to Trusted Publishing documentation

### Nice to Have

1. Add more detailed examples in tasks
2. Add troubleshooting section to spec
3. Add rollback procedures if publishing fails

## Conclusion

The spec and tasks are well-structured overall, but the critical issue (unit numbering) must be addressed before implementation. The important issues should also be resolved to prevent implementation confusion. The minor issues can be addressed during implementation but would benefit from clarification upfront.

**Note**: The dev release job's GitHub token requirement is handled by Octo-STS (as used in `release.yml`), so no additional configuration is needed beyond ensuring the job has proper OIDC permissions.

**Overall Assessment**: ✅ **Good** - Needs minor fixes before implementation

**Risk Level**: 🟡 **Medium** - Critical issues could cause implementation failures
