# 08 Questions Round 1 - VS Code Insiders Support

Please answer each question below (select one or more options, or add your own notes). Feel free to add additional context under any question.

## 1. Platform Support

Which platforms should VS Code Insiders support?

- [x] (A) All three platforms (Linux, macOS, Windows) - same as regular VS Code
- [ ] (B) Only Linux and macOS
- [ ] (C) Only macOS and Windows
- [ ] (D) Only the platform I'm currently using
- [ ] (E) Other (describe)

**Additional context:** Following the exact same cross-platform support as regular VS Code.

## 2. File Extension and Format

What file format should VS Code Insiders use for slash commands?

- [x] (A) Same as regular VS Code (`.prompt.md` markdown files)
- [ ] (B) Different extension to avoid conflicts (e.g., `.insiders.prompt.md`)
- [ ] (C) Plain `.md` files
- [ ] (D) TOML format instead
- [ ] (E) Other (describe)

**Additional context:** Maintaining consistency with regular VS Code format. Directories are separate so no conflicts.

## 3. Installation Directory Paths

VS Code Insiders typically uses "Code - Insiders" in directory names. Should we use:

- [x] (A) Standard Insiders paths:
  - Linux: `.config/Code - Insiders/User/prompts`
  - macOS: `Library/Application Support/Code - Insiders/User/prompts`
  - Windows: `AppData/Roaming/Code - Insiders/User/prompts`
- [ ] (B) Custom paths (specify below)
- [ ] (C) Need to verify actual paths on my system first
- [ ] (D) Other (describe)

**Actual paths on your system (if known):** Standard VS Code Insiders installation paths on all three platforms.

## 4. Agent Key Name

What CLI identifier should be used for VS Code Insiders?

- [x] (A) `vs-code-insiders` (follows pattern: tool-variant)
- [ ] (B) `vscode-insiders` (no hyphen in "vscode")
- [ ] (C) `code-insiders` (shorter)
- [ ] (D) `insiders` (simplest)
- [ ] (E) Other (describe)

**Additional context:** Consistent with `vs-code` naming pattern.

## 5. Display Name

What human-readable name should be shown in CLI output?

- [x] (A) "VS Code Insiders" (consistent with regular "VS Code")
- [ ] (B) "Visual Studio Code Insiders" (full name)
- [ ] (C) "Code Insiders" (shorter)
- [ ] (D) "VSCode Insiders" (one word)
- [ ] (E) Other (describe)

**Additional context:** Maintains consistency with the "VS Code" display name.

## 6. Detection Strategy

How should the tool detect VS Code Insiders installation?

- [x] (A) Check for existence of configuration directories (same strategy as regular VS Code)
- [ ] (B) Also check for executable/binary presence
- [ ] (C) Check for both directories AND executables
- [ ] (D) Only detect if user explicitly enables it
- [ ] (E) Other (describe)

**Additional context:** Using the same detection mechanism as all other agents - directory-based detection.

## 7. Coexistence with Regular VS Code

If both VS Code and VS Code Insiders are installed, how should they interact?

- [x] (A) Completely independent - each has its own prompts directory
- [ ] (B) Share prompts between them (same directory)
- [ ] (C) User should choose which one to use
- [ ] (D) Prioritize one over the other in detection
- [ ] (E) Other (describe)

**Additional context:** Separate installations = separate prompt directories. Users can generate for both if desired.

## 8. Testing Requirements

What level of testing is needed?

- [x] (A) Full test coverage matching regular VS Code (cross-platform detection, command dir, integration tests)
- [ ] (B) Basic tests only (config validation)
- [ ] (C) Skip tests, just add configuration
- [ ] (D) Only test on platforms I have access to
- [ ] (E) Other (describe)

**Additional context:** Following TDD patterns from spec 07 (VS Code regular) for consistency and quality.

## 9. Documentation Updates

Which documentation should be updated?

- [x] (A) All relevant docs (README.md, slash-command-generator.md, integration test expectations)
- [ ] (B) Only README.md
- [ ] (C) Only code comments
- [ ] (D) No documentation needed
- [ ] (E) Other (describe)

**Additional context:** Comprehensive documentation ensures discoverability and proper usage.

## 10. Proof Artifacts

What should demonstrate this feature works?

- [ ] (A) CLI output showing `vs-code-insiders` in `--list-agents`
- [ ] (B) Successful generation of `.prompt.md` file in Insiders directory
- [ ] (C) All tests passing (unit + integration)
- [ ] (D) Screenshot of working command in VS Code Insiders
- [x] (E) All of the above
- [ ] (F) Other (describe)

**Additional context:** Comprehensive proof artifacts demonstrate complete feature implementation.
