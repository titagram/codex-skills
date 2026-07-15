#!/usr/bin/env python3
"""Build and optionally execute approval-gated ManimGL render commands."""

import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path


MODE_FLAGS = {
    "frame": ["-so"],
    "preview": ["-w", "-l"],
    "final": ["-w", "--hd", "--fps", "30"],
}
ALLOWED_EXECUTABLES = {"manimgl", "manim-render"}
OUTPUT_CHOICES = {"new-version", "force-overwrite"}


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
    if not isinstance(manifest.get("output_path"), str) or not manifest["output_path"]:
        raise ValueError("topic manifest must record its output path")
    source_paths = manifest.get("source_paths")
    scaffold_fields_are_valid = (
        all(
            isinstance(manifest.get(field), str) and manifest[field]
            for field in ("topic", "slug", "scene_name")
        )
        and isinstance(source_paths, dict)
        and isinstance(source_paths.get("storyboard"), str)
        and bool(source_paths["storyboard"])
        and isinstance(manifest.get("render_history"), list)
    )
    if not scaffold_fields_are_valid:
        raise ValueError("topic manifest does not match the scaffold manifest contract")
    if mode == "final" and manifest.get("preview_approval") != "APPROVED":
        raise ValueError(
            "final execution requires preview_approval: 'APPROVED' in the manifest"
        )
    return manifest


def load_manifest(path, mode):
    """Load and validate a scaffold topic manifest for the requested mode."""
    path = Path(path)
    if not path.is_file():
        raise ValueError(f"topic manifest is not a regular file: {path}")
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"topic manifest is not valid JSON: {error.msg}") from error
    return validate_manifest(manifest, mode)


def _snapshot(output):
    output = Path(output)
    if not output.is_dir():
        return {}
    snapshot = {}
    for candidate in output.rglob("*"):
        if candidate.is_file():
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


def build_parser():
    parser = argparse.ArgumentParser(
        description="Print or execute an approval-gated ManimGL render command."
    )
    parser.add_argument("--executable", default="manimgl")
    parser.add_argument("--scene", required=True, type=Path)
    parser.add_argument("--scene-class", required=True)
    parser.add_argument("--mode", required=True, choices=sorted(MODE_FLAGS))
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="run only after validating the scaffold topic manifest",
    )
    return parser


def main(argv=None, runner=subprocess.run):
    args = build_parser().parse_args(argv)
    try:
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
        load_manifest(args.manifest, args.mode)
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    report = execute(command, args.output, runner=runner)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["exit_state"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
