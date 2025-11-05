# 05-spec-github-repository-support.md

## Introduction/Overview

This specification adds GitHub repository support to the slash command manager, enabling users to download prompt files directly from public GitHub repositories instead of being limited to local directories. The feature will function as an extension to the existing `--prompts-dir` functionality, maintaining full backward compatibility while providing a seamless way to consume remote prompt collections. The primary goal is to make prompt distribution and sharing easier across teams and organizations.

## Goals

- Enable downloading prompt files from public GitHub repositories
- Support GitHub URLs with tree/branch paths for precise prompt directory specification
- Auto-detect branch information from GitHub URLs when provided
- Maintain backward compatibility with existing local directory functionality
- Provide clear error messages for GitHub repository access issues
- Support demonstration using multiple branches from the spec-driven-workflow repository

## User Stories

**As a developer**, I want to download prompts from a GitHub repository so that I can easily use shared prompt collections without manual file management.

**As a team lead**, I want to point to a specific branch of a prompts repository so that my team can use consistent prompt versions across different environments.

**As a prompt author**, I want to distribute my prompts via GitHub so that others can consume them directly without cloning repositories manually.

**As a DevOps engineer**, I want to use different prompt sets from different branches so that I can test prompt variations in CI/CD pipelines.

## Demoable Units of Work

### Unit 1: GitHub URL Parsing and Validation

**Purpose:** Parse and validate GitHub repository URLs with tree/branch paths
**Demo Criteria:** Show successful parsing of https://github.com/liatrio-labs/spec-driven-workflow/tree/main/prompts and rejection of invalid URLs
**Proof Artifacts:** CLI output showing parsed owner/repo/branch/path, error messages for invalid URLs

### Unit 2: GitHub API Integration for Directory Listing

**Purpose:** List and download markdown files from GitHub repository directories
**Demo Criteria:** Successfully list and download .md files from the spec-driven-workflow repository prompts directory
**Proof Artifacts:** Downloaded files in temp directory, CLI output showing file count and names

### Unit 3: CLI Integration with Generate Command

**Purpose:** Integrate GitHub repository support into the existing generate command
**Demo Criteria:** Run `slash-man generate --github-url https://github.com/liatrio-labs/spec-driven-workflow/tree/main/prompts` and generate slash commands successfully
**Proof Artifacts:** Generated command files, CLI summary showing prompts loaded from GitHub

### Unit 4: Multi-Branch Support and Error Handling

**Purpose:** Demonstrate branch auto-detection and proper error handling
**Demo Criteria:** Test with different branches (main, develop) and invalid repository URLs
**Proof Artifacts:** CLI output showing branch detection, error messages for invalid repositories

### Unit 5: Source Metadata Generation

**Purpose:** Generate and verify source metadata in generated command files for both GitHub and local sources
**Demo Criteria:** Generate commands from GitHub and local directory, then verify metadata includes appropriate source information (URL/branch for GitHub, directory path for local)
**Proof Artifacts:** Generated command files with GitHub source metadata, generated command files with local directory source metadata, CLI output showing source attribution for both types

### Unit 6: Option Conflict Handling

**Purpose:** Demonstrate proper error handling when both prompt source options are specified
**Demo Criteria:** Run command with both `--prompts-dir` and `--github-url` to verify clear error message
**Proof Artifacts:** CLI error message explaining mutual exclusivity and directing user to choose one option

### Unit 7: Required Source Validation

**Purpose:** Demonstrate error handling when no prompt source is specified
**Demo Criteria:** Run command without either `--prompts-dir` or `--github-url` to verify clear error message requiring a source
**Proof Artifacts:** CLI error message explaining that a prompt source is required and showing usage examples

## Functional Requirements

1. **GitHub URL Parsing**: The system shall parse GitHub URLs in the format `https://github.com/owner/repo/tree/branch/path` and extract owner, repository, branch, and prompt directory path components.

2. **Branch Auto-Detection**: The system shall automatically detect the branch name from GitHub URLs containing tree/branch paths and use it for downloading files.

3. **GitHub API Integration**: The system shall use the GitHub Contents API to list files in the specified repository directory and filter for .md files.

4. **File Download**: The system shall download all .md files from the specified GitHub repository directory to a temporary local location for processing.

5. **CLI Option Integration**: The system shall add a `--github-url` option to the generate command that accepts GitHub repository URLs with tree/branch paths.

6. **Backward Compatibility**: The system shall maintain full backward compatibility with the existing `--prompts-dir` option and local directory functionality.

7. **Error Handling**: The system shall provide clear, actionable error messages when GitHub repositories are inaccessible, URLs are invalid, no .md files are found, or when conflicting prompt source options are provided.

8. **Option Mutual Exclusivity**: The system shall validate that `--github-url` and `--prompts-dir` options are not specified together and provide a clear error message directing the user to choose one source.

9. **Required Prompt Source**: The system shall require either `--prompts-dir` or `--github-url` to be specified and provide a clear error message if neither is provided, since prompts are no longer bundled within the application.

10. **Network Timeout and Retry**: The system shall implement industry-standard timeout values (30 seconds for API calls) and retry logic (up to 3 retries with exponential backoff) for transient network failures.

11. **File Size Limits**: The system shall reject individual prompt files larger than 1MB and warn about repositories with more than 100 prompt files to prevent performance issues.

12. **Temporary File Management**: The system shall create temporary directories for downloaded prompts and clean them up after processing, without persistent caching.

13. **Public Repository Support**: The system shall support downloading from public GitHub repositories without requiring authentication.

14. **Progress Reporting**: The system shall report the number of prompts loaded from GitHub and provide feedback during the download process.

15. **Source Metadata Generation**: The system shall generate metadata in generated command files that includes the source information: for GitHub sources, the repository URL, branch, commit hash (if available), and download timestamp; for local directory sources, the absolute directory path and generation timestamp.

16. **Metadata Preservation**: When prompts are processed, the generated slash command files shall include source attribution in their metadata to distinguish between GitHub-sourced and locally-sourced prompts.

17. **Enhanced Error Scenarios**: The system shall provide specific error messages for empty repository directories, repositories with no .md files, malformed markdown files, and permission denied errors.

## Non-Goals (Out of Scope)

1. **Private Repository Support**: Authentication for private GitHub repositories will not be implemented in this feature.
2. **Persistent Caching**: Downloaded prompts will not be cached persistently across sessions.
3. **Git Operations**: No git cloning or repository management operations will be performed.
4. **Other Git Hosting**: Support for GitLab, Bitbucket, or other git hosting platforms is excluded.
5. **Repository Search**: No functionality for searching GitHub repositories or browsing directory structures.
6. **Bulk Operations**: No support for downloading from multiple repositories simultaneously.
7. **File Upload**: No capability to upload or modify files in GitHub repositories.

## Design Considerations

The CLI interface should follow the existing pattern of the `--prompts-dir` option. The `--github-url` option should be mutually exclusive with `--prompts-dir` to avoid confusion. Help text should clearly show the expected URL format with examples. Error messages should be user-friendly and provide specific guidance for common issues like invalid URLs, inaccessible repositories, or empty prompt directories.

## Technical Considerations

- The implementation will use the `requests` library for GitHub API calls
- GitHub API rate limits for unauthenticated requests (60 requests/hour) should be considered
- Temporary directories will be managed using Python's `tempfile` module
- URL parsing will handle the specific GitHub tree/branch URL format
- Error handling will distinguish between network errors, invalid URLs, and repository access issues
- The existing `SlashCommandWriter` class will be extended to support GitHub sources
- No additional dependencies beyond `requests` will be required
- Metadata generation will extend existing prompt metadata structure to include source information for both GitHub and local directory sources
- The existing command generators (markdown, TOML) will be updated to include source metadata in their output formats
- Download timestamps and generation timestamps will be stored in ISO 8601 format for consistency
- Local directory paths will be stored as absolute paths for unambiguous identification
- Network timeouts will be set to 30 seconds for API calls with up to 3 retries using exponential backoff
- File size validation will reject files larger than 1MB and warn for repositories with more than 100 files
- Basic URL validation will ensure proper GitHub URL format without complex edge case handling

## Success Metrics

1. **Functionality**: 100% success rate for downloading and processing prompts from valid public GitHub repositories
2. **Performance**: Download and processing of typical prompt repositories (10-50 files) completes within 30 seconds
3. **Error Handling**: Clear, actionable error messages provided for 100% of failure scenarios
4. **Backward Compatibility**: All existing `--prompts-dir` functionality continues to work without modification
5. **User Experience**: Users can successfully generate commands from GitHub repositories with a single command

## Dependencies

- `requests>=2.31.0`: For GitHub API calls and file downloads
- Existing `typer`, `rich`, and `questionary` dependencies for CLI interface
- Standard library `tempfile` and `pathlib` for file management
- Existing `SlashCommandWriter` and prompt loading infrastructure

## Risks and Mitigations

**Risk**: GitHub API rate limiting may impact usage frequency
**Mitigation**: Efficient API usage with minimal calls, clear error messages for rate limits

**Risk**: Network connectivity issues may prevent repository access
**Mitigation**: Proper timeout handling, clear error messages, and graceful failure

**Risk**: Invalid or malformed GitHub URLs may cause confusion
**Mitigation**: Robust URL validation with specific error messages and format examples

**Risk**: Large prompt directories may cause performance issues
**Mitigation**: Progress reporting and reasonable timeouts for downloads

## Acceptance Criteria

- [ ] Users can specify a GitHub repository URL using `--github-url` option
- [ ] The system correctly parses owner, repo, branch, and path from GitHub URLs
- [ ] All .md files are downloaded from the specified repository directory
- [ ] Generated slash commands are created successfully from downloaded prompts
- [ ] Clear error messages are shown for invalid URLs or inaccessible repositories
- [ ] The feature works with different branches in the spec-driven-workflow repository
- [ ] Backward compatibility with `--prompts-dir` is maintained
- [ ] Temporary files are properly cleaned up after processing
- [ ] Generated command files include GitHub source metadata (URL, branch, timestamp)
- [ ] Generated command files include local directory source metadata (absolute path, timestamp)
- [ ] Source metadata distinguishes between GitHub-sourced and locally-sourced prompts
- [ ] System prevents and clearly reports conflicts when both `--prompts-dir` and `--github-url` are specified
- [ ] System requires either `--prompts-dir` or `--github-url` to be specified and provides clear error message if neither is provided
- [ ] Network timeouts and retries work correctly for transient failures
- [ ] File size limits prevent processing of overly large files (>1MB) and warn for large repositories (>100 files)
- [ ] Enhanced error scenarios provide specific messages for empty directories, no .md files, malformed files, and permission errors
- [ ] CLI help text includes proper usage examples and format requirements

## Testing Strategy

Unit tests will cover URL parsing, GitHub API integration, and error handling scenarios. Integration tests will use the spec-driven-workflow repository to test end-to-end functionality with different branches. Error condition testing will include invalid URLs, non-existent repositories, and network failures. Performance testing will ensure reasonable handling of typical prompt repository sizes.
