---
description: Generate comprehensive project documentation in the docs/ folder. Analyzes the codebase to determine which documentation categories apply, then creates substantive docs with real content — not placeholder text. Use this skill when starting a new project, when docs/ doesn't exist yet, or when you want to regenerate all documentation from scratch.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

Generate comprehensive documentation for the current project in `docs/`.

## Process

1. **Analyze the codebase** — Scan the project structure, read key files, and understand what this project does, how it's built, and what technologies it uses.

2. **Determine applicable categories** — From the universal list below, select only those that are relevant. A pure library doesn't need deployment docs. A CLI tool doesn't need API contract docs. Be selective.

3. **Detect project-specific docs** — Based on what the codebase does, identify additional documentation topics. Examples: a hooks-based system needs hooks documentation, a plugin system needs a plugin development guide, a CLI needs a command reference.

4. **Create `docs/` directory** if it doesn't exist.

5. **Write each document** with substantive content derived from the actual codebase. Reference real file paths, real function names, real configuration options. Every doc should be immediately useful to someone maintaining this code.

6. **Create `docs/README.md`** as an index listing all documentation with one-line descriptions.

## Universal Categories

Create those that apply to this project:

| File | Covers |
|------|--------|
| `architecture.md` | System design, component relationships, tech stack choices, design patterns used, data flow |
| `api-contracts.md` | All endpoints, request/response schemas, authentication, error responses, versioning |
| `data-models.md` | Database schemas, entity relationships, migrations strategy, data validation rules |
| `setup-deployment.md` | Prerequisites, installation steps, dev environment setup, build process, deployment |
| `configuration.md` | Every env var, config file, feature flag — what each does, valid values, defaults |
| `auth.md` | Authentication flow, token lifecycle, roles and permissions, security considerations |
| `error-handling.md` | Error taxonomy, error codes, how errors propagate, logging and monitoring |
| `testing.md` | Test framework, how to run tests, coverage expectations, testing patterns used |

## Quality Standards

- Each doc must contain real, specific information from this codebase — not generic templates
- Include code examples and file path references where they help understanding
- Write for someone who will maintain this code after the original team is gone
- Keep docs concise but complete — aim for clarity over length
- Use consistent formatting: h2 for major sections, h3 for subsections, code blocks for examples
