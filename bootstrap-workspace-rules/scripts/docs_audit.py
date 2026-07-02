#!/usr/bin/env python3
"""Lightweight audit for workspace operating documentation."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote


CORE_FILES = [
    "AGENTS.md",
    "docs/README.md",
    "docs/PROJECT_OVERVIEW.md",
    "docs/ARCHITECTURE.md",
    "docs/CODING_STYLE.md",
    "docs/RUNTIME.md",
    "docs/TESTING.md",
    "docs/SOURCE_OF_TRUTH.md",
    "docs/MAINTENANCE.md",
    "docs/LOGBOOK.md",
]

INDEX_FILES = [
    "docs/indexes/README.md",
    "docs/indexes/ROUTES_OR_ENTRYPOINTS.md",
    "docs/indexes/DATA_MODEL.md",
    "docs/indexes/SIDE_EFFECTS.md",
    "docs/indexes/DEPENDENCIES.md",
    "docs/indexes/SECURITY.md",
]

LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
PLACEHOLDER_RE = re.compile(
    r"\b(TBD|TODO|FIXME|PLACEHOLDER|INSERISCI|CHANGEME)\b|\[TODO[:\]]",
    re.IGNORECASE,
)
LOGBOOK_RE = re.compile(r"^###\s+\d{4}-\d{2}-\d{2}", re.MULTILINE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Workspace root to audit")
    parser.add_argument(
        "--allow-missing-indexes",
        action="store_true",
        help="Do not fail when docs/indexes files are absent",
    )
    parser.add_argument(
        "--allow-placeholders",
        action="store_true",
        help="Do not fail on unresolved placeholder tokens",
    )
    return parser.parse_args()


def is_external_link(target: str) -> bool:
    lowered = target.lower()
    return lowered.startswith(("http://", "https://", "mailto:", "tel:", "#"))


def markdown_files(root: Path) -> list[Path]:
    ignored = {".git", "node_modules", "vendor", ".venv", "venv"}
    result: list[Path] = []
    for path in root.rglob("*.md"):
        if ignored.intersection(path.relative_to(root).parts):
            continue
        result.append(path)
    return sorted(result)


def check_required_files(root: Path, allow_missing_indexes: bool) -> list[str]:
    issues: list[str] = []
    required = CORE_FILES if allow_missing_indexes else CORE_FILES + INDEX_FILES
    for rel in required:
        if not (root / rel).is_file():
            issues.append(f"missing required file: {rel}")
    return issues


def check_links(root: Path) -> list[str]:
    issues: list[str] = []
    for md in markdown_files(root):
        text = md.read_text(encoding="utf-8", errors="replace")
        for match in LINK_RE.finditer(text):
            raw_target = match.group(1).strip()
            if is_external_link(raw_target):
                continue
            target = raw_target.split("#", 1)[0].strip()
            if not target:
                continue
            target = unquote(target)
            candidate = (md.parent / target).resolve()
            try:
                candidate.relative_to(root.resolve())
            except ValueError:
                issues.append(f"{md.relative_to(root)} links outside root: {raw_target}")
                continue
            if not candidate.exists():
                issues.append(f"{md.relative_to(root)} has broken link: {raw_target}")
    return issues


def check_placeholders(root: Path, allow_placeholders: bool) -> list[str]:
    if allow_placeholders:
        return []
    issues: list[str] = []
    for md in markdown_files(root):
        text = md.read_text(encoding="utf-8", errors="replace")
        if PLACEHOLDER_RE.search(text):
            issues.append(f"{md.relative_to(root)} contains unresolved placeholder text")
    return issues


def check_logbook(root: Path) -> list[str]:
    path = root / "docs/LOGBOOK.md"
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    if not LOGBOOK_RE.search(text):
        return ["docs/LOGBOOK.md has no dated entry heading like '### YYYY-MM-DD'"]
    return []


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"ERROR: root is not a directory: {root}", file=sys.stderr)
        return 2

    issues: list[str] = []
    issues.extend(check_required_files(root, args.allow_missing_indexes))
    issues.extend(check_links(root))
    issues.extend(check_placeholders(root, args.allow_placeholders))
    issues.extend(check_logbook(root))

    if issues:
        print("Documentation audit failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print(f"Documentation audit OK: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
