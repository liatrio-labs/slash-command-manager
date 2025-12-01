# 07 Questions Round 1 - VS Code macOS Detection Fix

Please answer each question below (select one or more options, or add your own notes). Feel free to add additional context under any question.

## 1. Scope of VS Code Path Detection

What should the VS Code agent detection cover on different platforms?

- [ ] (A) Only detect the macOS default path (`~/Library/Application Support/Code`) without changing the command installation directory
- [ ] (B) Detect both macOS (`~/Library/Application Support/Code`) and Linux (`~/.config/Code`) paths, but keep command installation in the Linux path only
- [ ] (C) Detect both macOS and Linux paths, and update the command installation directory to use the platform-specific path for each OS
- [x] (D) Add support for Windows path detection as well (`%APPDATA%\Code`) in addition to macOS and Linux
- [ ] (E) Other (describe)

## 2. Command Installation Behavior

Where should generated VS Code commands be installed?

- [ ] (A) Always use `~/.config/Code/User/prompts` regardless of OS (current behavior, may not work on macOS default installs)
- [x] (B) Use platform-specific paths: Linux uses `~/.config/Code/User/prompts`, macOS uses `~/Library/Application Support/Code/User/prompts`
- [ ] (C) Allow users to configure the installation path via a preference or environment variable
- [ ] (D) Other (describe)

## 3. Backward Compatibility

How should this change handle existing installations and configurations?

- [x] (A) Simply fix the path for new detections/installations (no migration needed)
- [ ] (B) Add a migration mechanism that helps users move existing commands from old locations to new platform-specific paths
- [ ] (C) Support both paths for detection during a transition period, then deprecate the old Linux-only path
- [ ] (D) Other (describe)

## 4. Testing Requirements

What testing should verify the VS Code detection works across platforms?

- [ ] (A) Unit tests with mocked filesystem paths for both macOS and Linux
- [ ] (B) Add integration tests that actually create VS Code directories and verify detection works
- [ ] (C) Update existing tests to cover both platform paths explicitly
- [x] (D) All of the above
- [ ] (E) Other (describe)

## 5. Other Platforms

Should we also address detection for Windows users?

- [ ] (A) Not in this spec; focus only on macOS fix
- [x] (B) Yes, add Windows path detection (`%APPDATA%\Code`) in this same spec
- [ ] (C) Create a separate spec for Windows path support; this spec focuses on macOS only
- [ ] (D) Other (describe)
