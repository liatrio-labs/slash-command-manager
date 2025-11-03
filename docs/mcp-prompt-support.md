# MCP Prompt Support

This guide tracks how well popular IDEs, CLIs, and agent shells load the Spec Driven
Development (SDD) prompts exposed by the MCP server. Use it to choose the smoothest environment,
understand current limitations, and contribute new findings.

## Support Matrix

| Tool | Version<br>Tested | Loads MCP? | Prompt Actions | Experience | Workarounds / Notes |
| --- | --- | --- | --- | --- | --- |
| Claude Code CLI | TBD | Yes | Slash commands generated automatically | Ideal | Prompts appear as native slash commands. |
| Claude Code Desktop | TBD | Yes | TBD | Ideal | Loads successfully; verifying how quickly prompts become slash commands. |
| Claude Code IDE (JetBrains) | TBD | Yes | TBD | Ideal | Successful load; documenting slash-command behavior. |
| Cursor | TBD | Yes | Implicit trigger (no slash commands) | Ideal | Natural-language requests ("generate a spec") invoke the prompts. |
| Gemini CLI | TBD | Yes | Slash commands generated automatically | Ideal | Prompts appear as native slash commands. |
| OpenCode | TBD | Yes | Implicit trigger (no slash commands) | Ideal | Prompts are invoked through natural language requests. |
| Windsurf | TBD | Yes | No | Not good | MCP loads but returns `Error: no tools returned.` Adding a dummy tool unblocks basic use. |
| VS Code | TBD | Yes | Slash commands generated, but not executed | Not good | Prompts appear as commands but are inserted verbatim into chat; AI ignores them. |
| Codex CLI | TBD | Yes | No | Non-existent | Prompts not recognized; manual copy/paste required. |
| Codex IDE Plugin | TBD | Yes | No | Non-existent | Same as CLI—no prompt awareness. |
| Goose | TBD | Yes | TBD | TBD | Loads successfully; behavior still being evaluated. |
| Crush | TBD | TBD | TBD | TBD | Awaiting confirmation. |
| Q Developer CLI | TBD | TBD | TBD | TBD | Awaiting confirmation. |
| Q Developer IDE Plugin | TBD | TBD | TBD | TBD | Awaiting confirmation. |

## Interpretation

- **Ideal** environments either supply native slash commands or automatically invoke the
correct prompt flows from natural language requests.
- **Not good** means the MCP connection succeeds but prompt usage is clumsy or broken
without manual intervention.
- **Non-existent** indicates the tool ignores MCP prompts entirely today.
- **TBD** rows invite contributors to validate behavior and update this document.

## Field Notes & Tips

- Tools that surface the prompts as first-class slash commands (Claude Code CLI/Desktop,
Gemini CLI) provide the fastest path to running the SDD workflow without touching raw Markdown.
- When slash commands are absent but the tool still uses the MCP (Cursor, OpenCode),
instruct the assistant with the stage name ("generate spec", "generate task list from spec",
"manage tasks") to trigger the appropriate prompt flow.
- For environments that load prompts but don't execute them (VS Code), copy/paste the
prompt content into the chat manually.
- Windsurf users may need to wait for a fix or use an alternative client for the best
experience today.

## Contributing

To update this document:

1. Test the MCP server with your preferred AI tool
2. Update the matrix with your findings
3. Add detailed notes about workarounds or limitations
4. Submit a pull request with your changes

### Testing Steps

1. Install the slash-command-manager MCP server
2. Configure your AI tool to connect to the MCP server
3. Try each of the three prompts:
   - Generate a spec from an idea
   - Generate a task list from a spec
   - Manage tasks during implementation
4. Document the experience level and any workarounds needed

## Technical Details

### MCP Server Configuration

The MCP server exposes three main prompts:

- **generate-spec**: Creates detailed specifications from user ideas
- **generate-task-list-from-spec**: Converts specs into actionable task lists
- **manage-tasks**: Provides guidance for task execution and tracking

### Connection Methods

Different tools connect to MCP servers in various ways:

- **Claude Code**: Uses `mcpServers` configuration in settings
- **Cursor**: Integrates MCP through workspace settings
- **VS Code**: Requires MCP plugin and server configuration
- **CLI tools**: Often use command-line flags or config files

Refer to your tool's documentation for specific MCP connection instructions.
