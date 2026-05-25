---
description: Audit documentation coverage for the current project. Shows which docs exist in docs/, which universal categories are missing, whether existing docs appear current or stale relative to the code, and suggests project-specific docs that should exist. Use this skill when you want to check documentation health, see what's missing, or get a status report before starting work.
disable-model-invocation: true
---

Perform a documentation audit of the current project.

## Steps

1. Check if `docs/` exists at the project root. If not, report that no documentation directory exists and recommend running `/docshook:generate-docs`.

2. List all files in `docs/` and categorize them.

3. Evaluate coverage against the 8 universal documentation categories:
   - Architecture Overview (`architecture.md`)
   - API Contracts (`api-contracts.md`)
   - Data Models & Schemas (`data-models.md`)
   - Setup & Deployment (`setup-deployment.md`)
   - Configuration Reference (`configuration.md`)
   - Authentication & Authorization (`auth.md`)
   - Error Handling (`error-handling.md`)
   - Testing Strategy (`testing.md`)

4. For each universal category, determine if it's **applicable** to this project (skip categories that don't make sense — e.g., no API docs for a pure CLI utility with no server).

5. Scan the codebase to identify project-specific documentation that should exist but doesn't. Examples: hooks documentation for a hooks-based project, CLI command reference for a CLI tool, plugin development guide for a plugin system.

6. For each existing doc, briefly assess whether it appears current (references actual code paths, matches the current structure) or potentially stale.

## Output Format

Present a clear status report:

```
## Documentation Status: [project name]

### Coverage: X/Y applicable categories covered

| Category | Status | Notes |
|----------|--------|-------|
| Architecture | Present / Missing / N/A | ... |
| ... | ... | ... |

### Project-Specific Docs
- [existing or suggested docs]

### Staleness Check
- [any docs that look outdated]

### Recommendation
[One-line summary: what to do next]
```
