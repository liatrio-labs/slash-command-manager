# Slash Command Manager Architecture

This document provides a comprehensive overview of the slash-command-manager architecture, its components, and how they interact.

## Overview

Slash Command Manager is a Python CLI tool for generating and managing slash commands across multiple AI coding assistants. The tool supports multiple AI agents and provides both local and GitHub-based prompt sources.

## High-Level Architecture

```mermaid
flowchart LR
    subgraph "Entry Point"
        CLI[slash-man CLI]
    end

    subgraph "External Sources"
        LOCAL[Local Prompts]
        GITHUB[GitHub Repository]
    end

    subgraph "Output Targets"
        CLAUDE[Claude Code]
        CURSOR[Cursor]
        VSCODE[VS Code]
        GEMINI[Gemini CLI]
        WINDSURF[Windsurf]
        CODEX[Codex CLI]
        OPENCODE[OpenCode]
        AMAZONQ[Amazon Q]
    end

    subgraph "Core Package: slash_commands"
        CLI_MOD[cli.py]
        CONFIG[config.py]
        DETECT[detection.py]
        WRITER[writer.py]
        GEN[generators.py]
        PUTIL[prompt_utils.py]
        GH[github_utils.py]
    end

    CLI --> CLI_MOD

    CLI_MOD --> CONFIG
    CLI_MOD --> DETECT
    CLI_MOD --> WRITER

    WRITER --> CONFIG
    WRITER --> GEN
    WRITER --> PUTIL
    WRITER --> GH

    GEN --> CONFIG
    GEN --> PUTIL

    DETECT --> CONFIG

    LOCAL --> WRITER
    GITHUB --> GH
    GH --> WRITER

    WRITER --> CLAUDE
    WRITER --> CURSOR
    WRITER --> VSCODE
    WRITER --> GEMINI
    WRITER --> WINDSURF
    WRITER --> CODEX
    WRITER --> OPENCODE
    WRITER --> AMAZONQ

    style CLI fill:#e1f5fe,stroke:#01579b
    style WRITER fill:#fff3e0,stroke:#ef6c00
    style GEN fill:#fff3e0,stroke:#ef6c00
    style CONFIG fill:#c8e6c9,stroke:#2e7d32
```

## Package Structure

The project is organized into two main packages:

```text
slash-command-manager/
├── slash_commands/          # Core CLI and generation logic
│   ├── __init__.py          # Package exports
│   ├── __version__.py       # Version management with git SHA
│   ├── cli.py               # Typer CLI application
│   ├── config.py            # Agent configurations
│   ├── detection.py         # Agent auto-detection
│   ├── generators.py        # Format-specific generators
│   ├── github_utils.py      # GitHub API integration
│   ├── prompt_utils.py      # Markdown prompt parsing utilities
│   └── writer.py            # Command generation orchestrator
├── scripts/
│   └── run_integration_tests.py  # Docker-based integration tests
└── tests/                   # Unit and integration tests
```

## Component Details

### CLI Module (`slash_commands/cli.py`)

The CLI is built with [Typer](https://typer.tiangolo.com/) and provides two
main commands:

```mermaid
flowchart LR
    subgraph "slash-man CLI"
        MAIN[slash-man]
        GEN_CMD[generate]
        CLEAN_CMD[cleanup]
        MCP_CMD[mcp]
    end

    MAIN --> GEN_CMD
    MAIN --> CLEAN_CMD

    GEN_CMD --> |"--prompts-dir"| LOCAL[Local Source]
    GEN_CMD --> |"--github-*"| GITHUB[GitHub Source]
    GEN_CMD --> |"--agent"| AGENTS[Agent Selection]
    GEN_CMD --> |"--dry-run"| PREVIEW[Preview Mode]
    GEN_CMD --> |"--yes"| AUTO[Auto-confirm + Backup]

    CLEAN_CMD --> |"--agent"| CLEAN_AGENTS[Target Agents]
    CLEAN_CMD --> |"--include-backups"| BACKUPS[Include Backups]

    style MAIN fill:#e1f5fe,stroke:#01579b
    style GEN_CMD fill:#c8e6c9,stroke:#2e7d32
    style CLEAN_CMD fill:#ffcdd2,stroke:#c62828
```

**Key Features:**

- **Version callback**: Displays version with git commit SHA
- **Project root detection**: Finds project root via `PROJECT_ROOT` env var, `.git`, `pyproject.toml`, or `setup.py`
- **Interactive agent selection**: Uses questionary for multi-select (all detected agents pre-selected)
- **Rich output**: Summary panels, tables, and tree views
- **Error handling**: Categorized exit codes (1=user, 2=validation, 3=I/O)
- **GitHub integration**: Supports downloading prompts from GitHub repositories (requires all three flags: `--github-repo`, `--github-branch`, `--github-path`)

### Configuration Module (`slash_commands/config.py`)

Defines the supported AI agents and their configuration:

```mermaid
classDiagram
    class AgentConfig {
        +str key
        +str display_name
        +str command_dir
        +CommandFormat command_format
        +str command_file_extension
        +tuple[str] detection_dirs
        +dict platform_command_dirs
        +iter_detection_dirs() Iterable
        +get_command_dir() str
    }

    class CommandFormat {
        <<enumeration>>
        MARKDOWN
        TOML
    }

    AgentConfig --> CommandFormat

    class SupportedAgents {
        +claude-code
        +cursor
        +vs-code
        +gemini-cli
        +windsurf
        +codex-cli
        +opencode
        +amazon-q
    }

    SupportedAgents ..> AgentConfig : creates
```

**Supported Agents:**

Agents are sorted alphabetically by key. Paths shown are relative to the user's home directory:

| Agent Key    | Format   | Command Directory (relative to ~)     | Extension    |
|--------------|----------|---------------------------------------|--------------|
| amazon-q     | Markdown | `.aws/amazonq/prompts`                | `.md`        |
| claude-code  | Markdown | `.claude/commands`                    | `.md`        |
| codex-cli    | Markdown | `.codex/prompts`                      | `.md`        |
| cursor       | Markdown | `.cursor/commands`                    | `.md`        |
| gemini-cli   | TOML     | `.gemini/commands`                    | `.toml`      |
| opencode     | Markdown | `.config/opencode/command`            | `.md`        |
| vs-code      | Markdown | Platform-specific (see below)         | `.prompt.md` |
| windsurf     | Markdown | `.codeium/windsurf/global_workflows`  | `.md`        |

**VS Code Platform Paths:**

These paths are relative to the user's home directory:

- **Linux**: `.config/Code/User/prompts` (resolves to `~/.config/Code/User/prompts`)
- **macOS**: `Library/Application Support/Code/User/prompts` (resolves to `~/Library/Application Support/Code/User/prompts`)
- **Windows**: `AppData/Roaming/Code/User/prompts` (resolves to `%APPDATA%/Code/User/prompts`)

### Detection Module (`slash_commands/detection.py`)

Auto-detects installed AI agents by checking for their configuration
directories:

```mermaid
flowchart TD
    START[detect_agents] --> ITERATE[Iterate SUPPORTED_AGENTS]
    ITERATE --> CHECK{Detection dir exists?}
    CHECK -->|Yes| ADD[Add to detected list]
    CHECK -->|No| SKIP[Skip agent]
    ADD --> NEXT{More agents?}
    SKIP --> NEXT
    NEXT -->|Yes| ITERATE
    NEXT -->|No| RETURN[Return detected list]

    style START fill:#e1f5fe,stroke:#01579b
    style RETURN fill:#c8e6c9,stroke:#2e7d32
    style CHECK fill:#fff3e0,stroke:#ef6c00
```

**Detection Strategy:**

1. Accepts a base path (default: user's home directory)
2. Iterates through all supported agents in alphabetical order (by key)
3. Checks if any detection directory exists for each agent
4. Returns list preserving the alphabetical ordering

### Writer Module (`slash_commands/writer.py`)

The central orchestrator for prompt loading and command generation:

```mermaid
flowchart TD
    subgraph "Initialization"
        INIT[SlashCommandWriter.__init__]
        INIT --> CONFIG_SOURCE[Configure Source]
        CONFIG_SOURCE --> LOCAL_SRC[Local Directory]
        CONFIG_SOURCE --> GITHUB_SRC[GitHub Repository]
        CONFIG_SOURCE --> BUNDLED[Bundled Prompts]
    end

    subgraph "Generation Flow"
        GEN[generate]
        GEN --> LOAD[_load_prompts]
        LOAD --> PARSE[Parse Markdown Files]
        PARSE --> CHECK_EXIST[_find_existing_files]
        CHECK_EXIST --> PROMPT_USER{Files exist?}
        PROMPT_USER -->|Yes| ASK[_prompt_for_all_existing_files]
        ASK --> BACKUP_CHOICE{User choice}
        BACKUP_CHOICE -->|Cancel| ABORT[Raise RuntimeError]
        BACKUP_CHOICE -->|Backup| SET_BACKUP[Set backup mode]
        BACKUP_CHOICE -->|Skip-backups| SET_OVERWRITE[Set overwrite mode]
        PROMPT_USER -->|No| GENERATE_FILES
        SET_BACKUP --> GENERATE_FILES
        SET_OVERWRITE --> GENERATE_FILES
        GENERATE_FILES[_generate_file for each prompt × agent]
        GENERATE_FILES --> WRITE[Write to filesystem]
        WRITE --> RESULT[Return result dict]
    end

    INIT --> GEN

    style INIT fill:#e1f5fe,stroke:#01579b
    style GEN fill:#fff3e0,stroke:#ef6c00
    style RESULT fill:#c8e6c9,stroke:#2e7d32
    style ABORT fill:#ffcdd2,stroke:#c62828
```

**Key Responsibilities:**

- **Prompt loading**: From local directory, GitHub, or bundled prompts
- **Conflict detection**: Finds existing files before generation
- **User interaction**: Single prompt for all conflicts (offers: cancel, backup, skip-backups)
- **Backup creation**: Timestamped backups before overwrite (format: `filename.ext.YYYYMMDD-HHMMSS.bak`)
- **File writing**: Creates directories and writes formatted content
- **Cleanup**: Finds and removes generated files (by checking metadata or backup pattern)

### Generators Module (`slash_commands/generators.py`)

Format-specific command file generators:

```mermaid
classDiagram
    class CommandGenerator {
        <<factory>>
        +create(format) CommandGeneratorProtocol$
    }

    class CommandGeneratorProtocol {
        <<protocol>>
        +generate(prompt, agent, source_metadata) str
    }

    class MarkdownCommandGenerator {
        +generate(prompt, agent, source_metadata) str
        -_get_command_name(prompt, agent) str
        -_build_meta(prompt, agent, source_metadata) dict
    }

    class TomlCommandGenerator {
        +generate(prompt, agent, source_metadata) str
        -_dict_to_toml(data) str
    }

    CommandGenerator ..> MarkdownCommandGenerator : creates
    CommandGenerator ..> TomlCommandGenerator : creates
    MarkdownCommandGenerator ..|> CommandGeneratorProtocol : implements
    TomlCommandGenerator ..|> CommandGeneratorProtocol : implements
```

**Generation Process:**

```mermaid
sequenceDiagram
    participant Writer as SlashCommandWriter
    participant Factory as CommandGenerator
    participant Gen as Generator
    participant Utils as _apply_agent_overrides

    Writer->>Factory: create(agent.command_format)
    Factory-->>Writer: generator instance

    Writer->>Gen: generate(prompt, agent, metadata)
    Gen->>Utils: _apply_agent_overrides(prompt, agent)
    Utils-->>Gen: (description, arguments, enabled)

    alt Markdown Format
        Gen->>Gen: Build YAML frontmatter
        Gen->>Gen: Replace placeholders in body
        Gen->>Gen: Combine frontmatter + body
    else TOML Format
        Gen->>Gen: Build TOML structure
        Gen->>Gen: Add description and prompt
        Gen->>Gen: Convert to TOML string
    end

    Gen->>Gen: _normalize_output()
    Gen-->>Writer: formatted content
```

**Markdown Output Structure:**

```yaml
---
name: command-name
description: Command description
tags: [tag1, tag2]
enabled: true
arguments:
  - name: arg1
    description: Argument description
    required: true
meta:
  agent: cursor
  agent_display_name: Cursor
  command_dir: .cursor/commands
  command_format: markdown
  command_file_extension: .md
  source_prompt: original-prompt
  source_path: prompt.md
  version: 0.1.0
  updated_at: 2025-01-15T10:30:00+00:00
  source_type: local
  source_dir: /path/to/prompts
---

# Prompt Body

The actual prompt content goes here.
```

### GitHub Utils (`slash_commands/github_utils.py`)

Handles downloading prompts from GitHub repositories:

```mermaid
sequenceDiagram
    participant CLI as CLI
    participant Writer as SlashCommandWriter
    participant GH as github_utils
    participant API as GitHub API
    participant Raw as raw.githubusercontent.com

    CLI->>Writer: generate()
    Writer->>GH: _download_github_prompts_to_temp_dir()
    GH->>GH: validate_github_repo(repo)
    GH->>GH: _validate_github_branch(branch)
    GH->>GH: _validate_github_path(path)

    GH->>API: GET /repos/{owner}/{repo}/contents/{path}?ref={branch}
    API-->>GH: Directory listing or file content

    alt Single File
        GH->>GH: Decode base64 content
        GH-->>Writer: [(filename, content)]
    else Directory
        loop For each .md file
            GH->>GH: _construct_raw_github_url()
            GH->>Raw: GET file content
            Raw-->>GH: File content
        end
        GH-->>Writer: [(filename, content), ...]
    end

    Writer->>Writer: Write to temp directory
    Writer->>Writer: Load and process prompts
```

**Security Features:**

- Input validation for owner, repo, branch, and path
- Path traversal prevention (`..` detection)
- URL scheme validation (HTTPS only)
- Host validation (only `api.github.com` and `raw.githubusercontent.com`)
- Null byte rejection
- Whitelist character validation

### Prompt Utilities (`slash_commands/prompt_utils.py`)

Utility module for parsing markdown prompts with YAML frontmatter. Used by the writer and generators:

Parses markdown prompts with YAML frontmatter:

```mermaid
classDiagram
    class MarkdownPrompt {
        +Path path
        +str name
        +str description
        +set[str] tags
        +dict meta
        +bool enabled
        +list[PromptArgumentSpec] arguments
        +str body
        +dict agent_overrides
    }

    class PromptArgumentSpec {
        +str name
        +str description
        +bool required
    }

    MarkdownPrompt --> PromptArgumentSpec

    class Functions {
        +load_markdown_prompt(path) MarkdownPrompt
        +parse_frontmatter(content) tuple
        +normalize_arguments(raw) list
    }

    Functions ..> MarkdownPrompt : creates
```

**Frontmatter Fields:**

- `name`: Command name (defaults to filename stem)
- `description`: Human-readable description
- `tags`: List of categorization tags
- `enabled`: Whether command is active (default: true)
- `arguments`: List of argument specifications
- `meta`: Additional metadata
- `agent_overrides`: Per-agent configuration overrides

### Version Management (`slash_commands/__version__.py`)

Provides version tracking with git commit SHA:

```mermaid
flowchart TD
    subgraph "Version Resolution"
        START[Get Version]
        START --> CHECK_PYPROJECT{pyproject.toml exists?}
        CHECK_PYPROJECT -->|Yes| READ_TOML[Read from pyproject.toml]
        CHECK_PYPROJECT -->|No| PKG_META[Get from package metadata]
    end

    subgraph "Commit SHA Resolution"
        COMMIT[Get Commit SHA]
        COMMIT --> BUILD_TIME{Build-time file exists?}
        BUILD_TIME -->|Yes| USE_BUILD[Use _git_commit.py]
        BUILD_TIME -->|No| RUNTIME{Git available?}
        RUNTIME -->|Yes| GIT_REV[Run git rev-parse]
        RUNTIME -->|No| NO_COMMIT[Return None]
    end

    subgraph "Final Version"
        COMBINE[Combine Version + SHA]
        READ_TOML --> COMBINE
        PKG_META --> COMBINE
        USE_BUILD --> COMBINE
        GIT_REV --> COMBINE
        NO_COMMIT --> COMBINE
        COMBINE --> RESULT["1.0.0+abc1234"]
    end

    style START fill:#e1f5fe,stroke:#01579b
    style RESULT fill:#c8e6c9,stroke:#2e7d32
```

**Build Hook (`hatch_build.py`):**

During package building, the custom Hatch build hook:

1. Retrieves current git commit SHA
2. Creates `slash_commands/_git_commit.py` with embedded SHA
3. Includes file in the built package
4. Cleans up temporary file after build

## Data Flow

### Generate Command Flow

```mermaid
sequenceDiagram
    participant User as User
    participant CLI as CLI
    participant Writer as SlashCommandWriter
    participant Loader as Prompt Loader
    participant Gen as Generator
    participant FS as File System

    User->>CLI: slash-man generate --agent cursor

    CLI->>CLI: Validate arguments
    CLI->>CLI: detect_agents() if no --agent

    CLI->>Writer: SlashCommandWriter(prompts_dir, agents, ...)
    Writer->>Writer: Configure source metadata

    CLI->>Writer: generate()
    Writer->>Loader: _load_prompts()

    alt GitHub Source
        Loader->>Loader: Download from GitHub to temp dir
    else Local Source
        Loader->>Loader: Glob *.md files
    end

    loop For each prompt file
        Loader->>Loader: load_markdown_prompt(file)
        Loader->>Loader: parse_frontmatter()
        Loader->>Loader: normalize_arguments()
    end

    Loader-->>Writer: List[MarkdownPrompt]

    Writer->>Writer: _find_existing_files()

    alt Files exist and not --yes
        Writer->>User: Prompt for action
        User-->>Writer: backup/skip-backups/cancel
    end

    loop For each prompt × agent
        Writer->>Gen: CommandGenerator.create(format)
        Writer->>Gen: generate(prompt, agent, metadata)
        Gen-->>Writer: formatted content

        alt File exists
            Writer->>FS: create_backup() if backup mode
        end

        Writer->>FS: mkdir -p (parent dirs)
        Writer->>FS: write_text(content)
    end

    Writer-->>CLI: Result dict
    CLI->>CLI: _render_rich_summary()
    CLI-->>User: Summary panel
```

### Cleanup Command Flow

```mermaid
sequenceDiagram
    participant User as User
    participant CLI as CLI
    participant Writer as SlashCommandWriter
    participant FS as File System

    User->>CLI: slash-man cleanup --agent cursor

    CLI->>Writer: SlashCommandWriter(...)
    CLI->>Writer: find_generated_files(agents)

    loop For each agent
        Writer->>FS: Glob command files
        loop For each file
            Writer->>Writer: _is_generated_file()
            Writer->>Writer: Check YAML/TOML meta
        end
        Writer->>FS: Glob backup files (pattern: *.ext.YYYYMMDD-HHMMSS.bak)
    end

    Writer-->>CLI: List of found files

    alt Files found and not --yes
        CLI->>User: Display table + confirm
        User-->>CLI: Confirm/Cancel
    end

    CLI->>Writer: cleanup(agents, include_backups, dry_run)

    loop For each file
        alt Not dry run
            Writer->>FS: unlink(file)
        end
    end

    Writer-->>CLI: Cleanup result
    CLI-->>User: Summary panel
```

## Testing Architecture

```mermaid
flowchart TD
    subgraph "Test Organization"
        UNIT[Unit Tests]
        INT[Integration Tests]
    end

    subgraph "Unit Tests (tests/)"
        T_CLI[test_cli.py]
        T_CONFIG[test_config.py]
        T_DETECT[test_detection.py]
        T_GEN[test_generators.py]
        T_GH[test_github_utils.py]
        T_WRITER[test_writer.py]
        T_PROMPTS[test_prompts.py]
    end

    subgraph "Integration Tests (tests/integration/)"
        I_GEN[test_generate_command.py]
        I_OUT[test_generate_output.py]
        I_CLEAN[test_cleanup_command.py]
        I_FS[test_filesystem_and_errors.py]
        I_OVER[test_overwrite_prompt.py]
        I_DISC[test_prompt_discovery.py]
    end

    subgraph "Execution"
        UV_UNIT[uv run pytest tests/ -m 'not integration']
        UV_INT[scripts/run_integration_tests.py]
        DOCKER[Docker Container]
    end

    UNIT --> UV_UNIT
    INT --> UV_INT
    UV_INT --> DOCKER
    DOCKER --> I_GEN
    DOCKER --> I_OUT
    DOCKER --> I_CLEAN
    DOCKER --> I_FS
    DOCKER --> I_OVER
    DOCKER --> I_DISC

    style UNIT fill:#e1f5fe,stroke:#01579b
    style INT fill:#fff3e0,stroke:#ef6c00
    style DOCKER fill:#c8e6c9,stroke:#2e7d32
```

**Why Docker for Integration Tests:**

Integration tests write to the filesystem in agent-specific directories
(e.g., `~/.cursor/commands`). Running them in Docker:

1. Prevents overwriting user's actual prompt files
2. Provides isolated, repeatable test environment
3. Ensures tests don't interfere with each other

## Error Handling

The CLI uses categorized exit codes:

| Exit Code | Category     | Description                              |
|-----------|--------------|------------------------------------------|
| 0         | Success      | Operation completed successfully         |
| 1         | User Action  | User cancelled or no selection made      |
| 2         | Validation   | Invalid arguments or configuration       |
| 3         | I/O Error    | File system, network, or permission error|

## Configuration Hierarchy

### CLI Configuration

```mermaid
flowchart TD
    subgraph "CLI Options (Highest Priority)"
        CLI_PROMPTS[--prompts-dir]
        CLI_AGENT[--agent]
        CLI_TARGET[--target-path]
        CLI_DETECT[--detection-path]
    end

    subgraph "Environment Variables"
        ENV_PROJECT_ROOT[PROJECT_ROOT]
    end

    subgraph "Defaults (Lowest Priority)"
        DEF_PROMPTS[Bundled prompts]
        DEF_TARGET[Home directory]
        DEF_DETECT[Home directory]
    end

    CLI_PROMPTS --> |overrides| DEF_PROMPTS
    CLI_TARGET --> |overrides| DEF_TARGET
    CLI_DETECT --> |overrides| DEF_DETECT
    ENV_PROJECT_ROOT --> |used for| PROJECT_ROOT[Project root detection]

    style CLI_PROMPTS fill:#e1f5fe,stroke:#01579b
    style CLI_AGENT fill:#e1f5fe,stroke:#01579b
    style CLI_TARGET fill:#e1f5fe,stroke:#01579b
    style CLI_DETECT fill:#e1f5fe,stroke:#01579b
    style DEF_PROMPTS fill:#c8e6c9,stroke:#2e7d32
    style DEF_TARGET fill:#c8e6c9,stroke:#2e7d32
```

## Dependencies

```mermaid
flowchart LR
    subgraph "Core Dependencies"
        TYPER[typer]
        RICH[rich]
        QUEST[questionary]
        REQ[requests]
        YAML[pyyaml]
        TOML_W[tomli-w]
    end

    subgraph "Build Dependencies"
        HATCH[hatchling]
    end

    CLI_MOD[cli.py] --> TYPER
    CLI_MOD --> RICH
    CLI_MOD --> QUEST

    WRITER_MOD[writer.py] --> REQ
    WRITER_MOD --> QUEST
    WRITER_MOD --> YAML

    GEN_MOD[generators.py] --> YAML
    GEN_MOD --> TOML_W

    GH_MOD[github_utils.py] --> REQ

    BUILD[hatch_build.py] --> HATCH

    style TYPER fill:#e1f5fe,stroke:#01579b
    style HATCH fill:#c8e6c9,stroke:#2e7d32
```

## Extension Points

### Adding a New Agent

1. Add configuration tuple to `_SUPPORTED_AGENT_DATA` in `config.py`:

   ```python
   (
       "new-agent",           # key
       "New Agent",           # display_name
       ".new-agent/commands", # command_dir
       CommandFormat.MARKDOWN,# command_format
       ".md",                 # command_file_extension
       (".new-agent",),       # detection_dirs
       None,                  # platform_command_dirs (or dict for platform-specific)
   ),
   ```

2. The agent will automatically be:
   - Available in `--agent` option
   - Detected if its directory exists
   - Listed in `--list-agents` output

### Adding a New Command Format

1. Add new value to `CommandFormat` enum in `config.py`
2. Create new generator class in `generators.py` implementing
   `CommandGeneratorProtocol`
3. Update `CommandGenerator.create()` factory method
4. Add corresponding `_is_generated_*` method in `writer.py`

## Related Documentation

- [Generator Documentation](slash-command-generator.md) - Detailed generator usage
- [Contributing Guidelines](../CONTRIBUTING.md) - Development guidelines
