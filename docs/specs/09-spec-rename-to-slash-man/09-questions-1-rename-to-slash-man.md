# 09 Questions Round 1 - Rename to slash-man

Please answer each question below (select one or more options, or add your own notes). Feel free to add additional context under any question.

## 1. Package Name Format

What should the PyPI package name be? (Note: PyPI package names use hyphens, not underscores)

- [x] (A) `slash-man` (matches the CLI command name exactly)
- [ ] (B) `slash-manager` (keeps some of the original name)
- [ ] (C) `slashman` (single word, no hyphens)
- [ ] (D) Other (describe)

**Note:** The CLI entry point is already `slash-man`, so option (A) would create consistency between package name and CLI command.

## 2. Repository Name

Should the GitHub repository name also be changed?

- [ ] (A) Yes, rename repository to `slash-man` to match package name
- [x] (B) No, keep repository as `slash-command-manager` (package name can differ from repo name)
- [ ] (C) Other (describe)

## 3. Import Path Changes

The Python package directories (`slash_commands/` and `mcp_server/`) will remain unchanged. However, references to the package name in code (like `version("slash-command-manager")`) need updating. Should we:

- [x] (A) Update all code references to use the new package name
- [ ] (B) Keep some references for backward compatibility (if applicable)
- [ ] (C) Other (describe)

## 4. Documentation Updates

Which documentation files should be updated?

- [ ] (A) All documentation files (README.md, CHANGELOG.md, all docs/*.md files)
- [x] (B) Only user-facing documentation (README.md, main docs)
- [ ] (C) All docs including historical references in CHANGELOG.md
- [ ] (D) Other (describe)

## 5. Version Detection

The `__version__.py` file currently references `"slash-command-manager"` in the `get_package_version()` call. Should this:

- [x] (A) Be updated to the new package name immediately
- [ ] (B) Support both old and new names temporarily for migration
- [ ] (C) Other (describe)

## 6. Docker Image Naming

The Dockerfile currently doesn't specify an image name, but documentation references `slash-command-manager`. Should we:

- [x] (A) Update Docker image references to `slash-man` in documentation
- [ ] (B) Keep Docker references as-is (less critical)
- [ ] (C) Other (describe)

## 7. Testing Strategy

How should we verify the rename is complete?

- [x] (A) Run all existing tests to ensure nothing breaks
- [ ] (B) Add new tests specifically for package name references
- [x] (C) Manual verification: build package, install, run `uvx slash-man --help`
- [ ] (D) All of the above
- [x] (E) Other (describe) also run install tests in a clean environment of a docker container

## 8. Backward Compatibility

Do we need to maintain any backward compatibility?

- [x] (A) No backward compatibility needed - clean break to new name
- [ ] (B) Yes, support both names temporarily (e.g., in version detection)
- [ ] (C) Other (describe)

## 9. PyPI Publication

After the rename, should we:

- [ ] (A) Publish immediately to PyPI as `slash-man`
- [x] (B) Test locally first, then publish in a separate step
- [ ] (C) Other (describe)

## 10. Additional Considerations

Are there any other aspects of the rename we should consider?

- [x] (A) Update GitHub Actions workflows if they reference the package name
- [x] (B) Update any external references or integrations
- [x] (C) Update MCP server name/metadata (currently "slash-command-manager-mcp")
- [ ] (D) All of the above
- [ ] (E) Other (describe)
