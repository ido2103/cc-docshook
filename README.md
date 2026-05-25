# DocsHook

A Claude Code plugin that enforces documentation practices. When Claude modifies source code, it must create and maintain project documentation before it can finish responding.

## How it works

DocsHook uses a Stop hook that fires every time Claude finishes a response:

1. **No code changes?** → Hook passes instantly (zero overhead for Q&A, planning, etc.)
2. **Code modified + no `docs/` directory?** → Blocks Claude and instructs it to create documentation
3. **Code modified + `docs/` exists but no docs updated?** → Blocks Claude and instructs it to update relevant docs
4. **Code modified + docs also updated?** → Passes through

## Installation

```bash
claude plugin add /path/to/DocsHook
```

Or test locally:

```bash
claude --plugin-dir /path/to/DocsHook
```

## Documentation Structure

All documentation is created in a `docs/` folder at the project root. The plugin enforces two layers:

**Universal categories** (the hook picks which apply to the project):

| File | Covers |
|------|--------|
| `architecture.md` | System design, components, tech stack, patterns |
| `api-contracts.md` | Endpoints, schemas, auth, error responses |
| `data-models.md` | Database schemas, entity relationships |
| `setup-deployment.md` | Dev environment, build, deploy |
| `configuration.md` | Env vars, config files, feature flags |
| `auth.md` | Auth flows, roles, permissions |
| `error-handling.md` | Error taxonomy, codes, logging |
| `testing.md` | Test types, how to run, coverage |

**Project-specific docs** are auto-detected based on the codebase (e.g., hooks documentation for a hooks-based project, CLI reference for a CLI tool).

## Skills

| Skill | Trigger | Description |
|-------|---------|-------------|
| `/docshook:check-docs` | Manual | Audit documentation coverage — shows what exists, what's missing, what's stale |
| `/docshook:generate-docs` | Manual | Generate comprehensive docs for the project from scratch |

## Configuration

The stop hook has an 8-consecutive-block cap (prevents infinite loops). The hook checks `stop_hook_active` and becomes lenient if docs already exist with at least 2 files.

To adjust the block cap:

```bash
export CLAUDE_CODE_STOP_HOOK_BLOCK_CAP=4
```
