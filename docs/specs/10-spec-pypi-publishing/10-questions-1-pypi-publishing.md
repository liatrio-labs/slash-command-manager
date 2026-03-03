# 10 Questions Round 1 - PyPI Publishing

Please answer each question below (select one or more options, or add your own notes). Feel free to add additional context under any question.

## 1. PyPI Publishing Authentication Method

What authentication method should we use for PyPI publishing in CI?

- [x] (A) Trusted Publishing (OIDC) - Modern, secure, no secrets to manage. Requires PyPI account configuration.
- [ ] (B) API Token via GitHub Secrets - Traditional approach, requires storing PyPI API token as a secret.
- [ ] (C) Other (describe)

**Additional Notes:**

## 2. Release Trigger

When should the PyPI publishing workflow run?

- [x] (A) On GitHub Releases (when a release is published) - Matches existing semantic-release workflow
- [ ] (B) On git tags (when a tag matching version pattern is pushed) - More direct trigger
- [ ] (C) Both GitHub Releases AND git tags - Maximum flexibility
- [ ] (D) Other (describe)

**Additional Notes:**

## 3. Build Instructions Location

Where should build instructions be documented?

- [x] (A) In README.md - Most visible to contributors
- [ ] (B) In CONTRIBUTING.md - Standard location for contributor docs
- [ ] (C) In a new BUILDING.md or docs/BUILDING.md - Dedicated build documentation
- [ ] (D) Multiple locations (specify which)

**Additional Notes:**

## 4. Build Instructions Scope

What should the build instructions include?

- [x] (A) Basic build commands only (`python -m build`, `twine upload`)
- [ ] (B) Full workflow including prerequisites, testing, and verification steps
- [ ] (C) Both local manual builds AND CI/CD context
- [ ] (D) Other (describe)

**Additional Notes:**

## 5. PyPI Index Selection

Which PyPI index should we publish to?

- [ ] (A) Production PyPI (pypi.org) - Standard public index
- [ ] (B) Test PyPI (test.pypi.org) - For testing the publishing process first
- [x] (C) Both - Test first, then production
- [ ] (D) Other (describe)

**Additional Notes:**

## 6. Package Verification

What verification should happen before publishing?

- [x] (A) Build verification only (ensure package builds successfully)
- [ ] (B) Build + install test (install built package and verify CLI works)
- [ ] (C) Build + install test + basic functionality test (run a simple command)
- [ ] (D) Other (describe)

**Additional Notes:**

## 7. Integration with Existing Release Workflow

How should PyPI publishing integrate with the existing semantic-release workflow?

- [ ] (A) Add PyPI publishing step to existing release.yml workflow
- [x] (B) Create separate publish-to-pypi.yml workflow triggered by releases
- [ ] (C) Both - separate workflow but coordinated with semantic-release
- [ ] (D) Other (describe)

**Additional Notes:**

## 8. Error Handling and Rollback

What should happen if PyPI publishing fails?

- [x] (A) Fail the workflow and notify (standard CI behavior)
- [ ] (B) Fail workflow + create GitHub issue automatically
- [ ] (C) Retry mechanism with exponential backoff
- [ ] (D) Other (describe)

**Additional Notes:**
