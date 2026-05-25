# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DocsHook is a Claude Code plugin that enforces documentation practices. It uses hooks to ensure Claude creates and maintains documentation for projects it works on.

## Commands

- `uv run python download_docs.py` — Re-download all Claude Code docs into `anthropic_docs/`
- `claude --plugin-dir .` — Test this plugin locally
- `claude plugin validate .` — Validate the plugin manifest and structure
- `/reload-plugins` — Reload plugins mid-session after changes

## Repository Structure

- `anthropic_docs/` — Complete Claude Code documentation (gitignored, 140 markdown files). **Read these files when you need details about hooks, plugins, skills, agents, permissions, settings, or any Claude Code feature.** Key files:
  - `anthropic_docs/plugins.md` / `plugins-reference.md` — Plugin creation and full schema reference
  - `anthropic_docs/hooks.md` / `hooks-guide.md` — Hook events, JSON I/O, all hook types
  - `anthropic_docs/skills.md` — Skill authoring, frontmatter, dynamic context
  - `anthropic_docs/sub-agents.md` — Subagent definitions and configuration
  - `anthropic_docs/claude-directory.md` — Full .claude/ directory structure reference
  - `anthropic_docs/settings.md` / `permissions.md` — Settings and permission rules
  - `anthropic_docs/features-overview.md` — When to use hooks vs skills vs plugins vs MCP
  - `anthropic_docs/agent-sdk/` — Agent SDK docs (overview, hooks, plugins, sessions, etc.)
- `.claude-plugin/plugin.json` — Plugin manifest (name, version, description)
- `hooks/hooks.json` — Hook configurations for doc enforcement
- `skills/` — Skill definitions (each skill is a folder with `SKILL.md`)
- `agents/` — Subagent definitions (markdown files with frontmatter)
- `scripts/` — Hook and utility scripts

## Claude Code Plugin Architecture

### Plugin Structure

A plugin is a directory with `.claude-plugin/plugin.json` at the root. All component directories (`skills/`, `hooks/`, `agents/`, `bin/`) live at the **plugin root**, NOT inside `.claude-plugin/`.

```
DocsHook/
├── .claude-plugin/
│   └── plugin.json          # Only manifest here
├── skills/                  # skills/<name>/SKILL.md
├── agents/                  # agents/*.md
├── hooks/
│   └── hooks.json           # Hook configurations
├── scripts/                 # Hook scripts
├── settings.json            # Default settings (optional)
└── .mcp.json                # MCP servers (optional)
```

Plugin skills are namespaced: a skill `enforce-docs` in plugin `docshook` becomes `/docshook:enforce-docs`.

### Hook System

Hooks fire at lifecycle points and receive JSON on stdin. They communicate via exit codes and stdout JSON.

**Key events for this plugin:**
- `Stop` — Fires when Claude finishes responding. Exit code 2 prevents stopping (forces continuation). Can use `prompt` or `agent` type hooks for LLM-based verification.
- `TaskCompleted` — Fires when a task is marked completed. Exit code 2 prevents completion.
- `PostToolUse` — Fires after tool calls. Matcher `Edit|Write` catches file changes.
- `SessionStart` — Fires on session start/resume. Good for injecting context.

**Hook types:**
- `command` — Shell script. Receives JSON stdin, returns via exit code + stdout JSON.
- `prompt` — Single-turn LLM call. Returns `{"ok": true/false, "reason": "..."}`.
- `agent` — Multi-turn subagent with tool access (Read, Grep, Glob). Same output format as prompt.
- `http` — POST to URL. Response body uses same JSON format as command hooks.

**Exit codes:** 0 = no objection (proceed), 2 = block action (stderr → feedback to Claude), other = non-blocking error.

**JSON output for decisions (on stdout with exit 0):**
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Reason shown to Claude"
  }
}
```

For `Stop`/`PostToolUse`/`TaskCompleted` blocking:
```json
{
  "decision": "block",
  "reason": "Documentation not yet created"
}
```

**Hook config format (`hooks/hooks.json`):**
```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Check if docs exist. $ARGUMENTS"
          }
        ]
      }
    ]
  }
}
```

**Path variables in hooks:**
- `${CLAUDE_PLUGIN_ROOT}` — Plugin install directory (changes on update)
- `${CLAUDE_PLUGIN_DATA}` — Persistent data directory (survives updates)
- `${CLAUDE_PROJECT_DIR}` — Project root

### Skills

Each skill is a folder with `SKILL.md` containing YAML frontmatter + markdown body. Key frontmatter fields:
- `description` — When Claude should use this skill
- `disable-model-invocation: true` — User-only, prevent auto-invocation
- `allowed-tools` — Tools pre-approved while skill is active
- `context: fork` — Run in isolated subagent
- `hooks` — Hooks scoped to this skill's lifecycle

Dynamic context: `` !`command` `` runs shell commands before content reaches Claude.

### Agents (Subagents)

Markdown files in `agents/` with frontmatter: `name`, `description`, `model`, `tools`, `disallowedTools`, `maxTurns`, `memory`, `isolation`.

## Design Notes for Doc Enforcement

The `Stop` hook with `type: "prompt"` or `type: "agent"` is the primary enforcement mechanism. A prompt hook can check whether documentation exists/is current and return `{"ok": false, "reason": "Create documentation for X"}` to force Claude to continue working. The `Stop` hook has an 8-consecutive-block cap (configurable via `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`). Check `stop_hook_active` field in input JSON to avoid infinite loops.
