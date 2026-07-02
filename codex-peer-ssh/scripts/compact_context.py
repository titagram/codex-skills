#!/usr/bin/env python3
"""Build a bounded compact-resume prompt from codex-peer-ssh session state."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
CODEC_PATH = SCRIPT_DIR / "ipc_ast_codec.py"


def _load_codec():
    spec = importlib.util.spec_from_file_location("ipc_ast_codec", CODEC_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load codec from {CODEC_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _read_text_tail(path: Path, max_chars: int) -> str:
    if max_chars <= 0 or not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text) <= max_chars:
        return text
    return text[-max_chars:]


def _frame_from_line(line: str) -> list | None:
    try:
        value = json.loads(line)
    except json.JSONDecodeError:
        return None
    if _is_frame(value):
        return value
    if isinstance(value, dict) and _is_frame(value.get("frame")):
        return value["frame"]
    return None


def _is_frame(value: Any) -> bool:
    return isinstance(value, list) and len(value) == 6 and isinstance(value[0], str)


def _load_frames(machine_path: Path) -> list[list]:
    if not machine_path.exists():
        return []
    frames = []
    for line in machine_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        frame = _frame_from_line(line)
        if frame is not None:
            frames.append(frame)
    return frames


def _select_session_fields(session: dict) -> dict:
    keys = [
        "session_id",
        "ssh_target",
        "remote_workspace",
        "local_workspace",
        "runtime_provider",
        "runtime_session",
        "codec",
        "guardrails",
        "last_seq",
        "last_ack",
    ]
    return {key: session[key] for key in keys if key in session}


def build_context(
    session_dir: Path,
    *,
    task_frame: str | None = None,
    max_dict_frames: int = 4,
    max_checkpoints: int = 4,
    max_journal_chars: int = 1200,
) -> str:
    """Return a deterministic compact-resume prompt."""

    codec = _load_codec()
    session_dir = session_dir.resolve()
    session = _select_session_fields(_read_json(session_dir / "session.json"))
    frames = _load_frames(session_dir / "machine.jsonl")

    dictionary_frames = [frame for frame in frames if frame[0] == "D"][-max_dict_frames:]
    checkpoint_frames = [frame for frame in frames if frame[0] == "S"][-max_checkpoints:]
    contract_frames = [frame for frame in frames if frame[0] in {"C", "K"}][-2:]
    journal_tail = _read_text_tail(session_dir / "journal.md", max_journal_chars).strip()

    task = None
    if task_frame:
        task = codec.parse_frame(task_frame)

    payload = {
        "mode": "compact-resume-v1",
        "instruction": "Use codex-peer-ssh. Reconstruct context only from this bounded state. Do not request or rely on a full transcript unless explicitly asked.",
        "session": session,
        "contract": contract_frames,
        "dictionary": dictionary_frames,
        "checkpoints": checkpoint_frames,
        "journal_tail": journal_tail,
        "task": task,
    }
    return _compact_json(payload)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a compact codex-peer-ssh resume prompt.")
    parser.add_argument("session_dir", type=Path)
    parser.add_argument("--task-frame", default=None, help="IPC AST task frame to validate and include.")
    parser.add_argument("--max-dict-frames", type=int, default=4)
    parser.add_argument("--max-checkpoints", type=int, default=4)
    parser.add_argument("--max-journal-chars", type=int, default=1200)
    args = parser.parse_args(argv)

    print(
        build_context(
            args.session_dir,
            task_frame=args.task_frame,
            max_dict_frames=args.max_dict_frames,
            max_checkpoints=args.max_checkpoints,
            max_journal_chars=args.max_journal_chars,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
