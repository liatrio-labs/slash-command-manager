# CHANGELOG

<!-- version list -->

## v0.6.0 (2025-11-18)

### Bug Fixes

- **ci**: Remove changelog so it can be regenerated
  ([`384cc45`](https://github.com/liatrio-labs/slash-command-manager/commit/384cc4564da72f03c3a859bddc1155676d92a4f0))

- **docs**: Address OSS readiness audit feedback
  ([#11](https://github.com/liatrio-labs/slash-command-manager/pull/11),
  [`337c89e`](https://github.com/liatrio-labs/slash-command-manager/commit/337c89ef3db896317e75c08c0f8ca364c1fad9fe))

### Chores

- Add bypass actors to branch protection ruleset
  ([#11](https://github.com/liatrio-labs/slash-command-manager/pull/11),
  [`337c89e`](https://github.com/liatrio-labs/slash-command-manager/commit/337c89ef3db896317e75c08c0f8ca364c1fad9fe))

- Address OSS readiness audit feedback
  ([#11](https://github.com/liatrio-labs/slash-command-manager/pull/11),
  [`337c89e`](https://github.com/liatrio-labs/slash-command-manager/commit/337c89ef3db896317e75c08c0f8ca364c1fad9fe))

- Create branch protection ruleset
  ([#11](https://github.com/liatrio-labs/slash-command-manager/pull/11),
  [`337c89e`](https://github.com/liatrio-labs/slash-command-manager/commit/337c89ef3db896317e75c08c0f8ca364c1fad9fe))

- Update repository settings for template compliance
  ([#11](https://github.com/liatrio-labs/slash-command-manager/pull/11),
  [`337c89e`](https://github.com/liatrio-labs/slash-command-manager/commit/337c89ef3db896317e75c08c0f8ca364c1fad9fe))

### Features

- Add GitHub configuration files and documentation
  ([#11](https://github.com/liatrio-labs/slash-command-manager/pull/11),
  [`337c89e`](https://github.com/liatrio-labs/slash-command-manager/commit/337c89ef3db896317e75c08c0f8ca364c1fad9fe))


## v0.5.1 (2025-11-17)

### Bug Fixes

- **github**: Add path validation and fix branch download handling
  ([#10](https://github.com/liatrio-labs/slash-command-manager/pull/10),
  [`3c4ce3b`](https://github.com/liatrio-labs/slash-command-manager/commit/3c4ce3bc21b0f88bde88f1f05850bf1dda7f107e))

- **github**: Add path validation and fix logging bug
  ([#10](https://github.com/liatrio-labs/slash-command-manager/pull/10),
  [`3c4ce3b`](https://github.com/liatrio-labs/slash-command-manager/commit/3c4ce3bc21b0f88bde88f1f05850bf1dda7f107e))

- **github**: Correct branch name in download URLs for directory downloads
  ([#10](https://github.com/liatrio-labs/slash-command-manager/pull/10),
  [`3c4ce3b`](https://github.com/liatrio-labs/slash-command-manager/commit/3c4ce3bc21b0f88bde88f1f05850bf1dda7f107e))

- **github**: Replace URL parsing with direct construction for branch handling
  ([#10](https://github.com/liatrio-labs/slash-command-manager/pull/10),
  [`3c4ce3b`](https://github.com/liatrio-labs/slash-command-manager/commit/3c4ce3bc21b0f88bde88f1f05850bf1dda7f107e))

- **test**: Replace substring checks with startswith for URL validation
  ([#10](https://github.com/liatrio-labs/slash-command-manager/pull/10),
  [`3c4ce3b`](https://github.com/liatrio-labs/slash-command-manager/commit/3c4ce3bc21b0f88bde88f1f05850bf1dda7f107e))


## v0.5.0 (2025-11-14)

### Bug Fixes

- **cli**: Preserve empty detection summary
  ([#8](https://github.com/liatrio-labs/slash-command-manager/pull/8),
  [`cc874d8`](https://github.com/liatrio-labs/slash-command-manager/commit/cc874d81f1f8e8cce39a7b61e0b2e76912881645))

- **cli**: Stabilize summary path resolution
  ([#8](https://github.com/liatrio-labs/slash-command-manager/pull/8),
  [`cc874d8`](https://github.com/liatrio-labs/slash-command-manager/commit/cc874d81f1f8e8cce39a7b61e0b2e76912881645))

### Documentation

- **specs**: Add cli safety enhancements spec
  ([#8](https://github.com/liatrio-labs/slash-command-manager/pull/8),
  [`cc874d8`](https://github.com/liatrio-labs/slash-command-manager/commit/cc874d81f1f8e8cce39a7b61e0b2e76912881645))

- **specs**: Add CLI safety enhancements validation document
  ([#8](https://github.com/liatrio-labs/slash-command-manager/pull/8),
  [`cc874d8`](https://github.com/liatrio-labs/slash-command-manager/commit/cc874d81f1f8e8cce39a7b61e0b2e76912881645))

### Features

- Deliver rich summary ([#8](https://github.com/liatrio-labs/slash-command-manager/pull/8),
  [`cc874d8`](https://github.com/liatrio-labs/slash-command-manager/commit/cc874d81f1f8e8cce39a7b61e0b2e76912881645))

- Enforce backup-first writes ([#8](https://github.com/liatrio-labs/slash-command-manager/pull/8),
  [`cc874d8`](https://github.com/liatrio-labs/slash-command-manager/commit/cc874d81f1f8e8cce39a7b61e0b2e76912881645))

- Guard zero-prompt runs ([#8](https://github.com/liatrio-labs/slash-command-manager/pull/8),
  [`cc874d8`](https://github.com/liatrio-labs/slash-command-manager/commit/cc874d81f1f8e8cce39a7b61e0b2e76912881645))

- Harden yes-mode safety ([#8](https://github.com/liatrio-labs/slash-command-manager/pull/8),
  [`cc874d8`](https://github.com/liatrio-labs/slash-command-manager/commit/cc874d81f1f8e8cce39a7b61e0b2e76912881645))

- **cli**: Harden generate safety
  ([#8](https://github.com/liatrio-labs/slash-command-manager/pull/8),
  [`cc874d8`](https://github.com/liatrio-labs/slash-command-manager/commit/cc874d81f1f8e8cce39a7b61e0b2e76912881645))

### Refactoring

- **cli**: Standardize summary panel width and improve code organization
  ([#8](https://github.com/liatrio-labs/slash-command-manager/pull/8),
  [`cc874d8`](https://github.com/liatrio-labs/slash-command-manager/commit/cc874d81f1f8e8cce39a7b61e0b2e76912881645))

### Testing

- Improve test assertions and mocking
  ([#8](https://github.com/liatrio-labs/slash-command-manager/pull/8),
  [`cc874d8`](https://github.com/liatrio-labs/slash-command-manager/commit/cc874d81f1f8e8cce39a7b61e0b2e76912881645))


## v0.4.0 (2025-11-14)

### Bug Fixes

- Remove pre-commit hook for running integration tests on push
  ([#7](https://github.com/liatrio-labs/slash-command-manager/pull/7),
  [`d6d17fe`](https://github.com/liatrio-labs/slash-command-manager/commit/d6d17feeca14d86a104bca527504e0d415a4063c))

- **ci**: Use uv run directly in integration tests
  ([#7](https://github.com/liatrio-labs/slash-command-manager/pull/7),
  [`d6d17fe`](https://github.com/liatrio-labs/slash-command-manager/commit/d6d17feeca14d86a104bca527504e0d415a4063c))

### Documentation

- **specs**: Add Docker integration tests specification and task list
  ([#7](https://github.com/liatrio-labs/slash-command-manager/pull/7),
  [`d6d17fe`](https://github.com/liatrio-labs/slash-command-manager/commit/d6d17feeca14d86a104bca527504e0d415a4063c))

- **specs**: Improve integration test tasks based on review feedback
  ([#7](https://github.com/liatrio-labs/slash-command-manager/pull/7),
  [`d6d17fe`](https://github.com/liatrio-labs/slash-command-manager/commit/d6d17feeca14d86a104bca527504e0d415a4063c))

- **specs**: Update proof artifacts and add validation report
  ([#7](https://github.com/liatrio-labs/slash-command-manager/pull/7),
  [`d6d17fe`](https://github.com/liatrio-labs/slash-command-manager/commit/d6d17feeca14d86a104bca527504e0d415a4063c))

### Features

- Add basic CLI command integration tests
  ([#7](https://github.com/liatrio-labs/slash-command-manager/pull/7),
  [`d6d17fe`](https://github.com/liatrio-labs/slash-command-manager/commit/d6d17feeca14d86a104bca527504e0d415a4063c))

- Add Docker test environment setup and infrastructure
  ([#7](https://github.com/liatrio-labs/slash-command-manager/pull/7),
  [`d6d17fe`](https://github.com/liatrio-labs/slash-command-manager/commit/d6d17feeca14d86a104bca527504e0d415a4063c))

- Add file system and error scenario integration tests
  ([#7](https://github.com/liatrio-labs/slash-command-manager/pull/7),
  [`d6d17fe`](https://github.com/liatrio-labs/slash-command-manager/commit/d6d17feeca14d86a104bca527504e0d415a4063c))

- Add generate command integration tests
  ([#7](https://github.com/liatrio-labs/slash-command-manager/pull/7),
  [`d6d17fe`](https://github.com/liatrio-labs/slash-command-manager/commit/d6d17feeca14d86a104bca527504e0d415a4063c))

- **test**: Add Docker-based integration tests
  ([#7](https://github.com/liatrio-labs/slash-command-manager/pull/7),
  [`d6d17fe`](https://github.com/liatrio-labs/slash-command-manager/commit/d6d17feeca14d86a104bca527504e0d415a4063c))

### Refactoring

- **test**: Address review feedback and improve test infrastructure
  ([#7](https://github.com/liatrio-labs/slash-command-manager/pull/7),
  [`d6d17fe`](https://github.com/liatrio-labs/slash-command-manager/commit/d6d17feeca14d86a104bca527504e0d415a4063c))


## v0.3.0 (2025-11-14)

### Bug Fixes

- **github**: Add comprehensive input validation to prevent SSRF attacks
  ([#6](https://github.com/liatrio-labs/slash-command-manager/pull/6),
  [`c5cc7fa`](https://github.com/liatrio-labs/slash-command-manager/commit/c5cc7fa273cc0c4d72614dc9db88f1bb44f0e8db))

- **github**: Add URL validation to prevent SSRF attacks
  ([#6](https://github.com/liatrio-labs/slash-command-manager/pull/6),
  [`c5cc7fa`](https://github.com/liatrio-labs/slash-command-manager/commit/c5cc7fa273cc0c4d72614dc9db88f1bb44f0e8db))

- **github**: Use download_url for directory file downloads
  ([#6](https://github.com/liatrio-labs/slash-command-manager/pull/6),
  [`c5cc7fa`](https://github.com/liatrio-labs/slash-command-manager/commit/c5cc7fa273cc0c4d72614dc9db88f1bb44f0e8db))

- **tests**: Strip ANSI codes in GitHub flag validation tests
  ([#6](https://github.com/liatrio-labs/slash-command-manager/pull/6),
  [`c5cc7fa`](https://github.com/liatrio-labs/slash-command-manager/commit/c5cc7fa273cc0c4d72614dc9db88f1bb44f0e8db))

### Chores

- **docs**: Reorganize artifacts into specs structure
  ([#6](https://github.com/liatrio-labs/slash-command-manager/pull/6),
  [`c5cc7fa`](https://github.com/liatrio-labs/slash-command-manager/commit/c5cc7fa273cc0c4d72614dc9db88f1bb44f0e8db))

- **specs**: Migrate and reorganize specs for GitHub repository support
  ([#6](https://github.com/liatrio-labs/slash-command-manager/pull/6),
  [`c5cc7fa`](https://github.com/liatrio-labs/slash-command-manager/commit/c5cc7fa273cc0c4d72614dc9db88f1bb44f0e8db))

### Features

- Add documentation and CI updates for GitHub support
  ([#6](https://github.com/liatrio-labs/slash-command-manager/pull/6),
  [`c5cc7fa`](https://github.com/liatrio-labs/slash-command-manager/commit/c5cc7fa273cc0c4d72614dc9db88f1bb44f0e8db))

- Add GitHub prompt download and loading functionality
  ([#6](https://github.com/liatrio-labs/slash-command-manager/pull/6),
  [`c5cc7fa`](https://github.com/liatrio-labs/slash-command-manager/commit/c5cc7fa273cc0c4d72614dc9db88f1bb44f0e8db))

- Add GitHub repository flag integration and validation
  ([#6](https://github.com/liatrio-labs/slash-command-manager/pull/6),
  [`c5cc7fa`](https://github.com/liatrio-labs/slash-command-manager/commit/c5cc7fa273cc0c4d72614dc9db88f1bb44f0e8db))

- Add mutual exclusivity validation for GitHub and local prompts
  ([#6](https://github.com/liatrio-labs/slash-command-manager/pull/6),
  [`c5cc7fa`](https://github.com/liatrio-labs/slash-command-manager/commit/c5cc7fa273cc0c4d72614dc9db88f1bb44f0e8db))

- Add prompt metadata source tracking
  ([#6](https://github.com/liatrio-labs/slash-command-manager/pull/6),
  [`c5cc7fa`](https://github.com/liatrio-labs/slash-command-manager/commit/c5cc7fa273cc0c4d72614dc9db88f1bb44f0e8db))

- **github**: Add GitHub repository support for prompt downloads
  ([#6](https://github.com/liatrio-labs/slash-command-manager/pull/6),
  [`c5cc7fa`](https://github.com/liatrio-labs/slash-command-manager/commit/c5cc7fa273cc0c4d72614dc9db88f1bb44f0e8db))


## v0.2.0 (2025-11-13)

### Features

- Add enhanced configuration options to MCP subcommand
  ([#2](https://github.com/liatrio-labs/slash-command-manager/pull/2),
  [`2c00e6f`](https://github.com/liatrio-labs/slash-command-manager/commit/2c00e6f3131b551a43578eefd16cbeb1b24b5e78))

- Add MCP server subcommand integration
  ([#2](https://github.com/liatrio-labs/slash-command-manager/pull/2),
  [`2c00e6f`](https://github.com/liatrio-labs/slash-command-manager/commit/2c00e6f3131b551a43578eefd16cbeb1b24b5e78))

- Add mcp subcommand ([#2](https://github.com/liatrio-labs/slash-command-manager/pull/2),
  [`2c00e6f`](https://github.com/liatrio-labs/slash-command-manager/commit/2c00e6f3131b551a43578eefd16cbeb1b24b5e78))

- Complete testing and validation for unified CLI consolidation
  ([#2](https://github.com/liatrio-labs/slash-command-manager/pull/2),
  [`2c00e6f`](https://github.com/liatrio-labs/slash-command-manager/commit/2c00e6f3131b551a43578eefd16cbeb1b24b5e78))

- Remove slash-command-manager entry point and update documentation
  ([#2](https://github.com/liatrio-labs/slash-command-manager/pull/2),
  [`2c00e6f`](https://github.com/liatrio-labs/slash-command-manager/commit/2c00e6f3131b551a43578eefd16cbeb1b24b5e78))

- **specs**: Add unified CLI consolidation specification and task list
  ([#2](https://github.com/liatrio-labs/slash-command-manager/pull/2),
  [`2c00e6f`](https://github.com/liatrio-labs/slash-command-manager/commit/2c00e6f3131b551a43578eefd16cbeb1b24b5e78))

### Refactoring

- **cli**: Improve MCP subcommand error handling and validation
  ([#2](https://github.com/liatrio-labs/slash-command-manager/pull/2),
  [`2c00e6f`](https://github.com/liatrio-labs/slash-command-manager/commit/2c00e6f3131b551a43578eefd16cbeb1b24b5e78))

- **cli**: Remove redundant transport validation
  ([#2](https://github.com/liatrio-labs/slash-command-manager/pull/2),
  [`2c00e6f`](https://github.com/liatrio-labs/slash-command-manager/commit/2c00e6f3131b551a43578eefd16cbeb1b24b5e78))

### Testing

- **cli**: Fix ANSI escape code handling in help output test
  ([#2](https://github.com/liatrio-labs/slash-command-manager/pull/2),
  [`2c00e6f`](https://github.com/liatrio-labs/slash-command-manager/commit/2c00e6f3131b551a43578eefd16cbeb1b24b5e78))


## v0.1.0 (2025-11-12)

- Initial Release
