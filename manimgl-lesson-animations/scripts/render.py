#!/usr/bin/env python3
"""Build and optionally execute approval-gated ManimGL render commands."""

import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from workflow_state import (
    DEFAULT_VERIFICATION_CONTRACT,
    SHA256_RE,
    atomic_write_json,
    sha256_file,
    storyboard_approval,
    utc_now,
)


MODE_FLAGS = {
    "frame": ["-so"],
    "preview": ["-w", "-l"],
    "final": ["-w", "--hd", "--fps", "30"],
}
ALLOWED_EXECUTABLES = {"manimgl", "manim-render"}
OUTPUT_CHOICES = {"new-version", "force-overwrite"}
MODE_OUTPUT_DIRECTORIES = {
    "frame": "images",
    "preview": "previews",
    "final": "videos",
}
SCAFFOLD_STRING_FIELDS = ("topic", "slug", "scene_name", "output_path", "created_at")
SOURCE_PATH_FIELDS = ("storyboard", "scene_template", "custom_config")


def build_command(executable, scene, scene_class, mode, config, output):
    """Return a ManimGL command without executing it or changing the filesystem."""
    executable = str(executable)
    basename = Path(executable).name
    if basename == "manim":
        raise ValueError("Manim Community executable 'manim' is not supported")
    if basename not in ALLOWED_EXECUTABLES:
        raise ValueError(
            "renderer executable must be named 'manimgl' or 'manim-render'"
        )
    if mode not in MODE_FLAGS:
        raise ValueError(f"unknown render mode: {mode}")
    return [
        executable,
        str(scene),
        str(scene_class),
        *MODE_FLAGS[mode],
        "--config_file",
        str(config),
        "--video_dir",
        str(output),
    ]


def validate_manifest(manifest, mode):
    """Validate the scaffold approvals required before renderer execution."""
    if not isinstance(manifest, dict):
        raise ValueError("topic manifest must contain a JSON object")
    if manifest.get("approval") != "APPROVED":
        raise ValueError("topic manifest must record approved storyboard status")
    if manifest.get("output_choice") not in OUTPUT_CHOICES:
        raise ValueError("topic manifest must record an explicit output choice")
    source_paths = manifest.get("source_paths")
    scaffold_fields_are_valid = (
        all(
            isinstance(manifest.get(field), str) and manifest[field]
            for field in SCAFFOLD_STRING_FIELDS
        )
        and isinstance(source_paths, dict)
        and all(
            isinstance(source_paths.get(field), str) and source_paths[field]
            for field in SOURCE_PATH_FIELDS
        )
        and isinstance(manifest.get("render_history"), list)
        and isinstance(manifest.get("verification_history"), list)
        and isinstance(manifest.get("storyboard_sha256"), str)
        and SHA256_RE.fullmatch(manifest["storyboard_sha256"]) is not None
        and isinstance(manifest.get("verification_contract"), dict)
        and manifest["verification_contract"] == DEFAULT_VERIFICATION_CONTRACT
    )
    if not scaffold_fields_are_valid:
        raise ValueError("topic manifest does not match the scaffold manifest contract")
    if mode == "final":
        preview = manifest.get("preview_approval")
        if not isinstance(preview, dict) or preview.get("status") != "APPROVED":
            raise ValueError("final execution requires approved preview content")
        if not isinstance(preview.get("approved_content_hashes"), dict):
            raise ValueError("approved preview must be bound to content hashes")
    return manifest


def _scaffold_root(manifest):
    root = Path(manifest["output_path"])
    if not root.is_absolute():
        raise ValueError("scaffold output_path must be absolute")
    if root.is_symlink():
        raise ValueError("scaffold output_path must not be a symlink")
    try:
        canonical = root.resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise ValueError(f"scaffold output path does not exist: {root}") from error
    if not canonical.is_dir():
        raise ValueError(f"scaffold output path is not a directory: {root}")
    if root != canonical:
        raise ValueError("scaffold output_path must be canonical")
    return canonical


def load_manifest(path, mode):
    """Load and validate a scaffold topic manifest for the requested mode."""
    path = Path(path)
    if path.is_symlink():
        raise ValueError("scaffold manifest must not be a symlink")
    if not path.is_file():
        raise ValueError(f"topic manifest is not a regular file: {path}")
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"topic manifest is not valid JSON: {error.msg}") from error
    manifest = validate_manifest(manifest, mode)
    root = _scaffold_root(manifest)
    try:
        canonical_manifest = path.resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise ValueError(f"scaffold manifest does not exist: {path}") from error
    if canonical_manifest != root / "manifest.json":
        raise ValueError(
            "manifest must be the exact <output_path>/manifest.json scaffold file"
        )
    return manifest


def _require_exact_path(value, expected, label, directory=False):
    candidate = Path(value)
    if candidate.is_symlink():
        raise ValueError(f"{label} must not be a symlink")
    try:
        canonical = candidate.resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise ValueError(f"{label} does not exist: {candidate}") from error
    if canonical != expected:
        raise ValueError(f"{label} must be the scaffold path {expected}")
    expected_type = candidate.is_dir() if directory else candidate.is_file()
    if not expected_type:
        kind = "directory" if directory else "regular file"
        raise ValueError(f"{label} is not a {kind}: {candidate}")


def authorize_execution(manifest, scene, scene_class, mode, config, output):
    """Bind executable inputs to the exact files in one scaffold manifest."""
    root = _scaffold_root(manifest)
    _validate_saved_storyboard(manifest, root)
    _require_exact_path(scene, root / "scene.py", "scene")
    _require_exact_path(config, root / "custom_config.yml", "config")
    if scene_class != manifest["scene_name"]:
        raise ValueError(
            f"scene class must match manifest scene_name: {manifest['scene_name']}"
        )
    _require_exact_path(
        output,
        root / MODE_OUTPUT_DIRECTORIES[mode],
        "output",
        directory=True,
    )
    hashes = content_hashes(root)
    if mode == "final":
        approved = manifest["preview_approval"]["approved_content_hashes"]
        if approved != hashes:
            raise ValueError(
                "scene, config, or storyboard changed after preview approval"
            )
    return hashes


def _validate_saved_storyboard(manifest, root):
    storyboard = root / "storyboard.md"
    _require_exact_path(storyboard, storyboard, "storyboard")
    storyboard_text = storyboard.read_text(encoding="utf-8")
    if storyboard_approval(storyboard_text) != "APPROVED":
        raise ValueError(
            "saved storyboard must contain one exact top-level Approval: APPROVED"
        )
    if sha256_file(storyboard) != manifest["storyboard_sha256"]:
        raise ValueError("saved storyboard hash differs from the scaffold approval")


def content_hashes(root):
    """Hash the exact saved storyboard, scene, and config regular files."""
    root = Path(root)
    return {
        "storyboard": sha256_file(root / "storyboard.md"),
        "scene": sha256_file(root / "scene.py"),
        "config": sha256_file(root / "custom_config.yml"),
    }


def record_preview_approval(manifest_path):
    """Bind an explicit preview approval to the last successful preview inputs."""
    manifest = load_manifest(manifest_path, "preview")
    root = _scaffold_root(manifest)
    _validate_saved_storyboard(manifest, root)
    current = content_hashes(root)
    preview = manifest.get("preview_approval")
    if not isinstance(preview, dict) or preview.get("status") != "PENDING":
        raise ValueError("a successful pending preview is required before approval")
    if preview.get("content_hashes") != current:
        raise ValueError("preview inputs changed; render and review a new preview")
    preview["status"] = "APPROVED"
    preview["approved_content_hashes"] = dict(current)
    preview["approved_at"] = utc_now()
    atomic_write_json(manifest_path, manifest)
    return preview


def _snapshot(output):
    output = Path(output)
    if not output.is_dir():
        return {}
    try:
        output = output.resolve(strict=True)
    except (OSError, RuntimeError):
        return {}
    snapshot = {}
    for candidate in output.rglob("*"):
        if candidate.is_file() and not candidate.is_symlink():
            stat = candidate.stat()
            snapshot[str(candidate)] = (stat.st_size, stat.st_mtime_ns)
    return snapshot


def execute(command, output, runner=subprocess.run):
    """Execute one renderer command and report changed output candidates."""
    before = _snapshot(output)
    error_text = None
    try:
        completed = runner(command, check=True)
        returncode = completed.returncode
        exit_state = "completed"
    except subprocess.CalledProcessError as error:
        returncode = error.returncode
        exit_state = "failed"
        error_text = str(error)
    except OSError as error:
        returncode = None
        exit_state = "failed"
        error_text = str(error)
    after = _snapshot(output)
    report = {
        "command": command,
        "exit_state": exit_state,
        "returncode": returncode,
        "candidates": sorted(
            path for path, signature in after.items() if before.get(path) != signature
        ),
    }
    if error_text is not None:
        report["error"] = error_text
    return report


def record_render(manifest_path, manifest, mode, output, report, before_hashes):
    """Atomically persist one render attempt and any resulting preview state."""
    root = _scaffold_root(manifest)
    current_hashes = (
        content_hashes(root)
        if report["exit_state"] == "completed"
        else before_hashes
    )
    if report["exit_state"] == "completed" and current_hashes != before_hashes:
        report["exit_state"] = "invalidated"
        report["error"] = "render inputs changed during execution"
    if report["exit_state"] == "completed" and not report["candidates"]:
        report["exit_state"] = "no-artifact"
        report["error"] = "renderer completed without creating or changing an artifact"
    entry = {
        "command": list(report["command"]),
        "mode": mode,
        "output": str(Path(output).resolve()),
        "candidates": list(report["candidates"]),
        "status": report["exit_state"],
        "returncode": report["returncode"],
        "content_hashes": dict(current_hashes),
        "recorded_at": utc_now(),
    }
    if "error" in report:
        entry["error"] = report["error"]
    manifest["render_history"].append(entry)
    if mode == "preview" and report["exit_state"] == "completed":
        manifest["preview_approval"] = {
            "status": "PENDING",
            "content_hashes": dict(current_hashes),
            "rendered_at": entry["recorded_at"],
        }
    atomic_write_json(manifest_path, manifest)
    return report


def build_parser():
    parser = argparse.ArgumentParser(
        description="Print or execute an approval-gated ManimGL render command."
    )
    parser.add_argument("--executable", default="manimgl")
    parser.add_argument("--scene", type=Path)
    parser.add_argument("--scene-class")
    parser.add_argument("--mode", choices=sorted(MODE_FLAGS))
    parser.add_argument("--config", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument(
        "--record-preview-approval",
        choices=("APPROVED",),
        help="record explicit user approval of the current successful preview",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="run only after validating the scaffold topic manifest",
    )
    return parser


def main(argv=None, runner=subprocess.run):
    args = build_parser().parse_args(argv)
    try:
        if args.record_preview_approval is not None:
            if args.manifest is None:
                raise ValueError("preview approval requires --manifest")
            if args.execute or any(
                value is not None
                for value in (
                    args.scene,
                    args.scene_class,
                    args.mode,
                    args.config,
                    args.output,
                )
            ):
                raise ValueError(
                    "preview approval must be a standalone manifest operation"
                )
            preview = record_preview_approval(args.manifest)
            print(json.dumps(preview, ensure_ascii=False, indent=2))
            return 0
        missing = [
            name
            for name in ("scene", "scene_class", "mode", "config", "output")
            if getattr(args, name) is None
        ]
        if missing:
            raise ValueError(
                "render command requires: "
                + ", ".join("--" + n.replace("_", "-") for n in missing)
            )
        command = build_command(
            args.executable,
            args.scene,
            args.scene_class,
            args.mode,
            args.config,
            args.output,
        )
        if not args.execute:
            print(shlex.join(command))
            return 0
        if args.manifest is None:
            raise ValueError("--execute requires an approved scaffold topic manifest")
        manifest = load_manifest(args.manifest, args.mode)
        input_hashes = authorize_execution(
            manifest,
            args.scene,
            args.scene_class,
            args.mode,
            args.config,
            args.output,
        )
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    report = execute(command, args.output, runner=runner)
    try:
        report = record_render(
            args.manifest,
            manifest,
            args.mode,
            args.output,
            report,
            input_hashes,
        )
    except (OSError, ValueError) as error:
        report["exit_state"] = "state-write-failed"
        report["error"] = str(error)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["exit_state"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
