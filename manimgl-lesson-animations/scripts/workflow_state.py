#!/usr/bin/env python3
"""Shared, dependency-free state helpers for the ManimGL workflow."""

import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path


SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
FENCE_OPEN_RE = re.compile(r"^ {0,3}(?P<fence>`{3,}|~{3,})(?P<info>.*)$")
FENCE_CLOSE_RE = re.compile(r"^ {0,3}(?P<fence>`{3,}|~{3,})[ \t]*$")
DEFAULT_VERIFICATION_CONTRACT = {
    "media_type": "video",
    "width": 1920,
    "height": 1080,
    "frame_rate": "30/1",
    "min_duration_seconds": 0.5,
}


def utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def storyboard_approval(text):
    """Return one exact top-level Markdown approval value, else ``None``."""
    if text.count("Approval:") != 1:
        return None
    in_fence = None
    for line in text.splitlines():
        if in_fence is not None:
            closing = FENCE_CLOSE_RE.fullmatch(line)
            if closing:
                run = closing.group("fence")
                if run[0] == in_fence[0] and len(run) >= in_fence[1]:
                    in_fence = None
            continue
        opening = FENCE_OPEN_RE.match(line)
        if opening:
            run = opening.group("fence")
            in_fence = (run[0], len(run))
            continue
        if line in {"Approval: APPROVED", "Approval: PENDING"}:
            return line.split(": ", 1)[1]
    return None


def sha256_file(path):
    path = Path(path)
    if path.is_symlink():
        raise ValueError(f"content file must not be a symlink: {path}")
    if not path.is_file():
        raise ValueError(f"content file is not a regular file: {path}")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write_json(path, payload):
    """Atomically replace one existing, non-symlinked manifest."""
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError("manifest must not be a symlink")
    try:
        path = path.resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise ValueError("manifest must exist") from error
    parent = path.parent
    if parent.is_symlink() or not parent.is_dir():
        raise ValueError("manifest parent must be a real directory")
    canonical_parent = parent.resolve(strict=True)
    serialized = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    temporary_name = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            prefix=".manifest-",
            suffix=".json.tmp",
            dir=str(canonical_parent),
            delete=False,
        ) as stream:
            temporary_name = stream.name
            stream.write(serialized)
            stream.flush()
            os.fsync(stream.fileno())
        if path.is_symlink():
            raise ValueError("manifest must not be a symlink")
        os.replace(temporary_name, str(path))
        temporary_name = None
    finally:
        if temporary_name is not None:
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass
