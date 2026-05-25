#!/usr/bin/env python3
"""Stop hook script that enforces documentation when source code is modified.

Reads the session transcript to detect code changes, checks if docs/ exists
and was updated alongside the code. Exits 0 to allow stop, exits 2 to block
with an actionable message telling Claude what documentation to create or update.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any

DOCS_DIR = "docs"

SOURCE_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".rb",
    ".c", ".cpp", ".h", ".hpp", ".cs", ".swift", ".kt", ".scala",
    ".php", ".lua", ".sh", ".bash", ".zsh", ".sql", ".html", ".css",
    ".scss", ".sass", ".less", ".vue", ".svelte",
}

IGNORE_PATTERNS = {"docs/", "node_modules/", ".git/", "__pycache__/", ".venv/"}


def is_source_file(filepath: str) -> bool:
    if any(pattern in filepath for pattern in IGNORE_PATTERNS):
        return False
    ext = os.path.splitext(filepath)[1].lower()
    if ext in SOURCE_EXTENSIONS:
        return True
    if filepath.endswith(".md"):
        return False
    return False


def is_doc_file(filepath: str, project_dir: str) -> bool:
    docs_path = os.path.join(project_dir, DOCS_DIR)
    abs_filepath = os.path.join(project_dir, filepath) if not os.path.isabs(filepath) else filepath
    try:
        return os.path.commonpath([abs_filepath, docs_path]) == docs_path
    except ValueError:
        return False


def extract_modified_files(transcript_path: str) -> tuple[set[str], set[str]]:
    """Parse transcript JSONL for Edit/Write tool calls. Returns (source_files, doc_files)."""
    source_files = set()
    doc_files = set()

    try:
        with open(transcript_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                file_path = extract_file_path(entry)
                if file_path:
                    if DOCS_DIR + "/" in file_path or file_path.startswith(DOCS_DIR):
                        doc_files.add(file_path)
                    elif is_source_file(file_path):
                        source_files.add(file_path)
    except (FileNotFoundError, PermissionError):
        pass

    return source_files, doc_files


def extract_file_path(entry: Any) -> str | None:
    """Extract file path from a transcript entry if it's an Edit or Write tool call."""
    if not isinstance(entry, dict):
        return None

    tool_name = None
    tool_input = None

    if entry.get("type") == "tool_use":
        tool_name = entry.get("name", "")
        tool_input = entry.get("input", {})
    elif entry.get("type") == "assistant" and "content" in entry:
        content = entry["content"]
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    tool_name = block.get("name", "")
                    tool_input = block.get("input", {})
                    break

    if tool_name in ("Edit", "Write") and isinstance(tool_input, dict):
        return tool_input.get("file_path", "")

    return None


def get_existing_docs(project_dir: str) -> list[str]:
    docs_path = Path(project_dir) / DOCS_DIR
    if not docs_path.is_dir():
        return []
    return [f.name for f in docs_path.iterdir() if f.is_file() and f.suffix == ".md"]


def build_enforcement_message(
    source_files: set[str],
    doc_files: set[str],
    existing_docs: list[str],
    docs_exist: bool,
) -> str | None:
    """Build the enforcement message or return None if no enforcement needed."""
    if not source_files:
        return None

    if not docs_exist:
        files_summary = ", ".join(sorted(source_files)[:5])
        if len(source_files) > 5:
            files_summary += f" and {len(source_files) - 5} more"
        return (
            f"Source code was modified ({files_summary}) but no docs/ directory exists. "
            f"Create a docs/ directory with project documentation. "
            f"Run /docshook:generate-docs to generate comprehensive documentation, "
            f"or create the docs manually. At minimum, create docs/README.md as an index "
            f"and the most relevant docs for this project from: architecture.md, "
            f"api-contracts.md, data-models.md, setup-deployment.md, configuration.md, "
            f"auth.md, error-handling.md, testing.md."
        )

    if not doc_files and existing_docs:
        files_summary = ", ".join(sorted(source_files)[:5])
        if len(source_files) > 5:
            files_summary += f" and {len(source_files) - 5} more"
        return (
            f"Source code was modified ({files_summary}) but no documentation in docs/ "
            f"was updated. Review and update the relevant docs in docs/ to reflect "
            f"your changes. Existing docs: {', '.join(sorted(existing_docs))}."
        )

    return None


def main():
    raw_input = sys.stdin.read()
    try:
        hook_input = json.loads(raw_input)
    except json.JSONDecodeError:
        sys.exit(0)

    project_dir = hook_input.get("cwd", ".")
    transcript_path = hook_input.get("transcript_path", "")
    stop_hook_active = hook_input.get("stop_hook_active", False)

    docs_path = Path(project_dir) / DOCS_DIR
    docs_exist = docs_path.is_dir()

    if stop_hook_active and docs_exist:
        existing = get_existing_docs(project_dir)
        if len(existing) >= 2:
            sys.exit(0)

    if not transcript_path:
        sys.exit(0)

    source_files, doc_files = extract_modified_files(transcript_path)

    message = build_enforcement_message(
        source_files, doc_files, get_existing_docs(project_dir), docs_exist
    )

    if message:
        print(json.dumps({"decision": "block", "reason": message}))
        print(message, file=sys.stderr)
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
