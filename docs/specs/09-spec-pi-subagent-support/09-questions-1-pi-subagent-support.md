# 09 Questions Round 1 - Pi Subagent Support

Please answer each question below (select one or more options, or add your own notes). Feel free to add additional context under any question.

## 1. What Is Pi?

I couldn't find an AI coding assistant called "Pi" with a documented slash command system. Can you clarify what Pi is?

- [ ] (A) Pi by Inflection AI (conversational AI assistant)
- [ ] (B) A new/beta AI coding tool with its own CLI or IDE integration
- [ ] (C) An internal or custom tool you've built or are building
- [ ] (D) A tool known by another name that you're referring to as "Pi"

**Recommended answer(s):** None — I genuinely don't know which tool this is. Your answer drives the entire spec.

## 2. Pi's Command Directory

Where does Pi expect slash command files to be placed?

- [ ] (A) `~/.pi/commands/` or similar dot-directory under home
- [ ] (B) A project-local directory (e.g., `.pi/commands/` relative to workspace)
- [ ] (C) Platform-specific paths (different on macOS/Linux/Windows)
- [ ] (D) I'm not sure yet — needs research

**Recommended answer(s):** [(B)]

**Why this is recommended:**

- Most agents in this project use project-local directories (e.g., `.claude/commands`, `.cursor/commands`)
- Project-local is the most common pattern for AI coding assistants with slash commands

## 3. Command File Format

What format does Pi expect for its command/prompt files?

- [ ] (A) Markdown with YAML frontmatter (like Claude Code, Cursor, Codex)
- [ ] (B) TOML (like Gemini CLI)
- [ ] (C) Plain markdown without frontmatter (like Kiro CLI)
- [ ] (D) A custom/unique format (please describe)
- [ ] (E) I'm not sure yet — needs research

**Recommended answer(s):** [(A)]

**Why this is recommended:**

- YAML frontmatter + Markdown is the most common format across supported agents (7 of 11 use it)
- Reusing `CommandFormat.MARKDOWN` means no new generator code is needed, keeping scope minimal

## 4. File Extension

What file extension does Pi use for command files?

- [ ] (A) `.md` (like Claude Code, Cursor, Codex, etc.)
- [ ] (B) `.prompt.md` (like VS Code)
- [ ] (C) `.toml` (like Gemini CLI)
- [ ] (D) Something else (please specify)

**Recommended answer(s):** [(A)]

**Why this is recommended:**

- `.md` is the most common extension across supported agents
- Reduces friction and follows established patterns

## 5. Detection Directories

Which directory presence indicates Pi is installed in a project?

- [ ] (A) `.pi/` directory in project root
- [ ] (B) Multiple directories (like Windsurf's `.codeium/` + `.codeium/windsurf/`)
- [ ] (C) A config file rather than a directory
- [ ] (D) I'm not sure — needs research

**Recommended answer(s):** [(A)]

**Why this is recommended:**

- Single detection directory is the simplest and most common pattern
- Follows the convention of most existing agents

## 6. Agent-Specific Overrides or Special Behavior

Does Pi require any special handling compared to standard markdown agents?

- [ ] (A) No special handling — standard markdown format works fine
- [ ] (B) Pi needs agent-specific frontmatter fields (please describe)
- [ ] (C) Pi has unique metadata or comment-based annotations
- [ ] (D) Pi has tool-permission or capability declarations in commands
- [ ] (E) I'm not sure yet

**Recommended answer(s):** [(A)]

**Why this is recommended:**

- Starting without special handling keeps scope minimal
- Special behavior can be added in a follow-up spec if needed
- The existing override system in `MarkdownPrompt` already supports per-agent customization via frontmatter

## 7. Reference Documentation

Do you have a link to Pi's documentation for its command/prompt system?

- [ ] (A) Yes — I'll provide the URL
- [ ] (B) No public docs yet, but I can describe the format
- [ ] (C) I'll research and get back to you
