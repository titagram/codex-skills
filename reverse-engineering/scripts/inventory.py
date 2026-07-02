#!/usr/bin/env python3
"""Read-only inventory helper for reverse engineering targets."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_IGNORE_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    ".cache",
    ".venv",
    "venv",
    "node_modules",
    "target",
    "build",
    "dist",
}

MARKERS = {
    "package.json": ("source", "node/javascript"),
    "pyproject.toml": ("source", "python"),
    "requirements.txt": ("source", "python"),
    "setup.py": ("source", "python"),
    "Cargo.toml": ("compiled-source", "rust"),
    "go.mod": ("compiled-source", "go"),
    "pom.xml": ("compiled-source", "java/maven"),
    "build.gradle": ("compiled-source", "java/gradle"),
    "CMakeLists.txt": ("compiled-source", "cmake/c-cpp"),
    "Makefile": ("compiled-source", "make"),
    "platformio.ini": ("embedded", "platformio"),
    "boards.txt": ("embedded", "arduino"),
    "Kconfig": ("embedded", "kconfig"),
    "app.json": ("source", "app metadata"),
    "Dockerfile": ("runtime", "container"),
}

BINARY_EXTENSIONS = {
    ".apk",
    ".bin",
    ".dex",
    ".dll",
    ".dylib",
    ".elf",
    ".exe",
    ".hex",
    ".ipa",
    ".jar",
    ".ko",
    ".o",
    ".obj",
    ".so",
    ".srec",
    ".uf2",
    ".wasm",
}

TOOLS = [
    "file",
    "strings",
    "nm",
    "objdump",
    "readelf",
    "otool",
    "lipo",
    "dwarfdump",
    "binwalk",
    "rizin",
    "radare2",
    "ghidra",
    "jadx",
    "apktool",
    "tcpdump",
    "tshark",
    "wireshark",
    "bluetoothctl",
    "btmon",
    "lsusb",
    "lspci",
    "system_profiler",
    "ioreg",
    "dmesg",
    "strace",
    "dtruss",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a read-only inventory and first-pass classification for a target path."
    )
    parser.add_argument("target", help="Target file or directory to inspect")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown")
    parser.add_argument("--max-files", type=int, default=5000, help="Maximum files to include")
    parser.add_argument(
        "--hash-bytes",
        type=int,
        default=16 * 1024 * 1024,
        help="Hash files up to this size in bytes; larger files get a partial hash",
    )
    parser.add_argument(
        "--no-default-ignore",
        action="store_true",
        help="Do not skip common dependency/build/cache directories",
    )
    return parser.parse_args()


def run_file(path: Path) -> str | None:
    tool = shutil.which("file")
    if not tool:
        return None
    try:
        result = subprocess.run(
            [tool, "-b", str(path)],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=5,
        )
    except Exception:
        return None
    return result.stdout.strip() if result.stdout else None


def sample_bytes(path: Path, limit: int = 4096) -> bytes:
    try:
        with path.open("rb") as handle:
            return handle.read(limit)
    except OSError:
        return b""


def classify_magic(data: bytes) -> str | None:
    if data.startswith(b"\x7fELF"):
        return "ELF"
    if data.startswith(b"MZ"):
        return "PE/COFF"
    if data[:4] in {
        b"\xfe\xed\xfa\xce",
        b"\xfe\xed\xfa\xcf",
        b"\xce\xfa\xed\xfe",
        b"\xcf\xfa\xed\xfe",
        b"\xca\xfe\xba\xbe",
    }:
        return "Mach-O/Fat Mach-O"
    if data.startswith(b"dex\n"):
        return "Android DEX"
    if data.startswith(b"\x00asm"):
        return "WebAssembly"
    if data.startswith(b"UF2\n"):
        return "UF2 firmware"
    if data.startswith(b"PK\x03\x04"):
        return "ZIP/JAR/APK container"
    if data.startswith(b"SQLite format 3\x00"):
        return "SQLite database"
    if data.lstrip().startswith(b":"):
        return "possible Intel HEX"
    return None


def is_probably_text(data: bytes) -> bool:
    if not data:
        return True
    if b"\x00" in data:
        return False
    try:
        data.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False


def hash_file(path: Path, hash_bytes: int) -> tuple[str, bool] | tuple[None, bool]:
    digest = hashlib.sha256()
    total = 0
    truncated = False
    try:
        with path.open("rb") as handle:
            while True:
                chunk = handle.read(1024 * 1024)
                if not chunk:
                    break
                if total + len(chunk) > hash_bytes:
                    digest.update(chunk[: max(0, hash_bytes - total)])
                    truncated = True
                    break
                digest.update(chunk)
                total += len(chunk)
    except OSError:
        return None, False
    return digest.hexdigest(), truncated


def iter_paths(root: Path, max_files: int, ignore_default: bool) -> tuple[list[Path], list[str]]:
    skipped: list[str] = []
    if root.is_file() or root.is_symlink():
        return [root], skipped

    paths: list[Path] = []
    ignore_dirs = set() if ignore_default else DEFAULT_IGNORE_DIRS
    for current, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        skipped.extend(str(Path(current, d).relative_to(root)) for d in set(os.listdir(current)) & ignore_dirs if Path(current, d).is_dir())
        for name in files:
            paths.append(Path(current, name))
            if len(paths) >= max_files:
                return paths, skipped
    return paths, skipped


def inspect_file(path: Path, root: Path, hash_bytes: int) -> dict[str, Any]:
    try:
        stat = path.lstat()
    except OSError as exc:
        return {"path": str(path), "error": str(exc)}

    rel = str(path.relative_to(root)) if root.is_dir() else path.name
    item: dict[str, Any] = {
        "path": rel,
        "size": stat.st_size,
        "suffix": path.suffix.lower(),
        "executable": bool(stat.st_mode & 0o111),
        "symlink": path.is_symlink(),
    }
    if path.is_symlink():
        return item

    data = sample_bytes(path)
    item["text"] = is_probably_text(data)
    magic = classify_magic(data)
    if magic:
        item["magic"] = magic
    file_type = run_file(path)
    if file_type:
        item["file_type"] = file_type
    digest, truncated = hash_file(path, hash_bytes)
    if digest:
        item["sha256"] = digest
        item["sha256_partial"] = truncated
    return item


def classify(files: list[dict[str, Any]]) -> dict[str, Any]:
    evidence: list[str] = []
    categories = Counter()
    languages = Counter()
    binary_candidates = []

    for item in files:
        name = Path(item.get("path", "")).name
        suffix = item.get("suffix", "")
        if name in MARKERS:
            category, language = MARKERS[name]
            categories[category] += 1
            languages[language] += 1
            evidence.append(f"{item['path']} -> {category}/{language}")
        if suffix in BINARY_EXTENSIONS or item.get("magic"):
            categories["binary-artifact"] += 1
            binary_candidates.append(item["path"])
        if suffix in {".c", ".cc", ".cpp", ".h", ".hpp", ".rs", ".go", ".swift"}:
            categories["compiled-source"] += 1
        if suffix in {".py", ".js", ".ts", ".rb", ".php", ".lua", ".sh"}:
            categories["interpreted-source"] += 1
        if suffix in {".dts", ".dtsi", ".ld", ".map"}:
            categories["embedded"] += 1
        if suffix in {".pcap", ".pcapng"}:
            categories["network-capture"] += 1

    if not categories:
        primary = "unknown"
    else:
        primary = categories.most_common(1)[0][0]

    return {
        "primary": primary,
        "categories": dict(categories),
        "languages_or_ecosystems": dict(languages),
        "binary_candidates": binary_candidates[:50],
        "evidence": evidence[:100],
    }


def inventory(target: Path, max_files: int, hash_bytes: int, no_default_ignore: bool) -> dict[str, Any]:
    root = target.resolve()
    paths, skipped = iter_paths(root, max_files, no_default_ignore)
    files = [inspect_file(path, root, hash_bytes) for path in paths]
    extensions = Counter(item.get("suffix", "") or "<none>" for item in files)
    largest = sorted(files, key=lambda item: item.get("size", 0), reverse=True)[:20]

    return {
        "tool": "reverse-engineering/scripts/inventory.py",
        "read_only": True,
        "host": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "python": sys.version.split()[0],
            "cwd": os.getcwd(),
        },
        "target": {
            "input": str(target),
            "resolved": str(root),
            "is_file": root.is_file(),
            "is_dir": root.is_dir(),
        },
        "available_tools": {name: shutil.which(name) for name in TOOLS if shutil.which(name)},
        "counts": {
            "files_scanned": len(files),
            "max_files": max_files,
            "skipped_default_dirs": len(skipped),
        },
        "skipped_dirs": skipped[:200],
        "extensions": dict(extensions.most_common(30)),
        "largest_files": [
            {k: item.get(k) for k in ("path", "size", "suffix", "magic", "file_type")}
            for item in largest
        ],
        "classification": classify(files),
        "files": files,
    }


def render_markdown(data: dict[str, Any]) -> str:
    lines = [
        "# Reverse Engineering Inventory",
        "",
        f"- Target: `{data['target']['resolved']}`",
        f"- Host: `{data['host']['platform']}` `{data['host']['machine']}`",
        f"- Files scanned: {data['counts']['files_scanned']} / max {data['counts']['max_files']}",
        f"- Primary classification: `{data['classification']['primary']}`",
        "",
        "## Available Tools",
        "",
    ]
    tools = data["available_tools"]
    if tools:
        lines.extend(f"- `{name}`: `{path}`" for name, path in sorted(tools.items()))
    else:
        lines.append("- No known reverse-engineering tools found on PATH.")

    lines.extend(["", "## Classification Evidence", ""])
    evidence = data["classification"]["evidence"]
    if evidence:
        lines.extend(f"- {item}" for item in evidence)
    else:
        lines.append("- No strong project markers found.")

    lines.extend(["", "## Categories", ""])
    for name, count in sorted(data["classification"]["categories"].items()):
        lines.append(f"- `{name}`: {count}")

    lines.extend(["", "## Top Extensions", ""])
    for suffix, count in data["extensions"].items():
        lines.append(f"- `{suffix}`: {count}")

    lines.extend(["", "## Largest Files", ""])
    for item in data["largest_files"]:
        desc = item.get("magic") or item.get("file_type") or item.get("suffix") or "unknown"
        lines.append(f"- `{item['path']}` ({item['size']} bytes): {desc}")

    binaries = data["classification"]["binary_candidates"]
    lines.extend(["", "## Binary/Firmware Candidates", ""])
    if binaries:
        lines.extend(f"- `{path}`" for path in binaries)
    else:
        lines.append("- None detected in first pass.")

    if data["skipped_dirs"]:
        lines.extend(["", "## Skipped Default Directories", ""])
        lines.extend(f"- `{path}`" for path in data["skipped_dirs"][:50])

    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    target = Path(args.target)
    if not target.exists():
        print(f"error: target does not exist: {target}", file=sys.stderr)
        return 2
    data = inventory(target, args.max_files, args.hash_bytes, args.no_default_ignore)
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(render_markdown(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
