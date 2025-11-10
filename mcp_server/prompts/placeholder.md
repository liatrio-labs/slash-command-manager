---
name: placeholder
description: A placeholder prompt for testing the slash command generator and MCP server
tags:
  - placeholder
  - testing
  - example
arguments:
  - name: input
    description: Input text or content to process
    required: true
    type: string
  - name: format
    description: Output format (markdown, json, plain text)
    required: false
    type: string
    default: markdown
enabled: true
---

# Placeholder Prompt

This is a placeholder prompt that demonstrates the structure and format expected by the slash command generator and MCP server.

## Purpose

This prompt serves as a template and testing placeholder for:

- Slash command generation across different AI assistants
- MCP server prompt registration and serving
- Development and testing workflows

## Usage

Use this prompt to process and transform input content into the desired output format.

### Parameters

- **input** (required): The text or content you want to process
- **format** (optional): Output format - choose from:
  - `markdown` (default): Structured Markdown output
  - `json`: JSON-formatted response
  - `plain`: Plain text output

## Instructions

When processing user input:

1. Analyze the provided input content
2. Apply appropriate transformations based on the format parameter
3. Generate structured output that maintains the original meaning
4. Follow best practices for the requested output format

### Output Formats

**Markdown Format:**

- Use proper headings and structure
- Include code blocks for technical content
- Add lists and emphasis for readability

**JSON Format:**

- Provide valid JSON structure
- Include relevant metadata about the processing
- Ensure proper escaping and formatting

**Plain Text Format:**

- Clean, readable text without markup
- Logical paragraph structure
- Clear separation of ideas

## Example

For input "Hello world" with format "markdown", you might generate:

```markdown
# Processed Content

The input "Hello world" has been processed and structured according to markdown formatting standards.

## Analysis
- Content type: Greeting
- Language: English
- Complexity: Simple

## Result
Hello world! This content has been successfully processed.
```

---

*This is a placeholder prompt. Replace this with your actual prompt content for production use.*
