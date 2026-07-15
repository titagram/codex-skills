#!/usr/bin/env python3
"""Verify rendered lesson artifacts with FFprobe metadata."""

import argparse
import json
import math
import shutil
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from workflow_state import DEFAULT_VERIFICATION_CONTRACT, atomic_write_json, utc_now


def _resolve_ffprobe(ffprobe, which=shutil.which):
    resolved = which(str(ffprobe))
    if resolved is None:
        raise FileNotFoundError(f"ffprobe executable not found: {ffprobe}")
    return str(Path(resolved).resolve())


def probe(path, ffprobe, runner=subprocess.run, which=shutil.which):
    """Return parsed FFprobe JSON for a regular non-empty artifact file."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"artifact does not exist: {path}")
    if not path.is_file():
        raise ValueError(f"artifact is not a regular file: {path}")
    if path.stat().st_size == 0:
        raise ValueError(f"artifact is empty: {path}")

    executable = _resolve_ffprobe(ffprobe, which=which)
    command = [
        executable,
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-show_entries",
        "stream=codec_type,width,height,r_frame_rate",
        "-of",
        "json",
        str(path),
    ]
    completed = runner(command, check=True, capture_output=True, text=True)
    try:
        metadata = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise ValueError(f"ffprobe returned invalid JSON: {error.msg}") from error
    if not isinstance(metadata, dict):
        raise ValueError("ffprobe JSON must contain an object")
    return metadata


def _positive_frame_rate(value):
    try:
        return Fraction(str(value)) > 0
    except (ValueError, ZeroDivisionError):
        return False


def validate(
    metadata,
    expected_resolution=None,
    min_duration=None,
    expected_media_type="video",
    expected_frame_rate=None,
):
    """Return human-readable validation errors for FFprobe metadata."""
    errors = []
    if not isinstance(metadata, dict):
        return ["metadata must be a JSON object"]

    streams = metadata.get("streams")
    if not isinstance(streams, list) or not streams:
        errors.append("metadata contains no streams")
        matching_streams = []
    else:
        matching_streams = [
            stream
            for stream in streams
            if isinstance(stream, dict)
            and stream.get("codec_type") == expected_media_type
        ]
        if not matching_streams:
            errors.append(f"metadata contains no {expected_media_type} stream")

    if matching_streams:
        stream = matching_streams[0]
        if expected_resolution is not None:
            actual_resolution = (stream.get("width"), stream.get("height"))
            if actual_resolution != tuple(expected_resolution):
                errors.append(
                    "resolution mismatch: expected "
                    f"{expected_resolution[0]}x{expected_resolution[1]}, got "
                    f"{actual_resolution[0]}x{actual_resolution[1]}"
                )
        if not _positive_frame_rate(stream.get("r_frame_rate")):
            errors.append("video frame rate must be positive")
        elif expected_frame_rate is not None:
            try:
                actual_rate = Fraction(str(stream.get("r_frame_rate")))
                wanted_rate = Fraction(str(expected_frame_rate))
            except (ValueError, ZeroDivisionError):
                errors.append("expected frame rate is invalid")
            else:
                if actual_rate != wanted_rate:
                    errors.append(
                        "frame rate mismatch: expected "
                        f"{expected_frame_rate}, got {stream.get('r_frame_rate')}"
                    )

    if min_duration is not None:
        format_metadata = metadata.get("format")
        duration_value = (
            format_metadata.get("duration")
            if isinstance(format_metadata, dict)
            else None
        )
        try:
            duration = float(duration_value)
        except (TypeError, ValueError):
            errors.append("duration is missing or invalid")
        else:
            if not math.isfinite(duration) or duration < min_duration:
                errors.append(
                    f"duration must be at least {min_duration} seconds; got {duration_value}"
                )
    return errors


def load_manifest(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError("manifest must be a regular non-symlinked file")
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"manifest is not valid JSON: {error.msg}") from error
    if not isinstance(manifest, dict):
        raise ValueError("manifest must contain a JSON object")
    output_value = manifest.get("output_path")
    if not isinstance(output_value, str) or not output_value:
        raise ValueError("manifest output_path is missing")
    root = Path(output_value)
    if not root.is_absolute() or root.is_symlink():
        raise ValueError("manifest output_path must be canonical and non-symlinked")
    try:
        canonical_root = root.resolve(strict=True)
        canonical_manifest = path.resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise ValueError("manifest paths do not exist") from error
    if root != canonical_root or not canonical_root.is_dir():
        raise ValueError("manifest output_path must be a canonical directory")
    if canonical_manifest != canonical_root / "manifest.json":
        raise ValueError("manifest must be the exact <output_path>/manifest.json")
    if not isinstance(manifest.get("render_history"), list):
        raise ValueError("manifest render_history is invalid")
    if not isinstance(manifest.get("verification_history"), list):
        raise ValueError("manifest verification_history is invalid")
    contract = manifest.get("verification_contract")
    if contract != DEFAULT_VERIFICATION_CONTRACT:
        raise ValueError("manifest verification_contract has invalid expectations")
    return manifest, canonical_root


def authorize_artifact(manifest, root, artifact):
    artifact = Path(artifact)
    if artifact.is_symlink() or not artifact.is_file():
        raise ValueError("artifact must be a regular non-symlinked file")
    try:
        canonical = artifact.resolve(strict=True)
        videos = (root / "videos").resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise ValueError("artifact or videos directory does not exist") from error
    if (root / "videos").is_symlink() or videos != root / "videos":
        raise ValueError("videos directory must be canonical and non-symlinked")
    try:
        canonical.relative_to(videos)
    except ValueError as error:
        raise ValueError("artifact must be inside the scaffold videos directory") from error
    final_candidates = {
        candidate
        for entry in manifest["render_history"]
        if isinstance(entry, dict)
        and entry.get("mode") == "final"
        and entry.get("status") == "completed"
        and isinstance(entry.get("candidates"), list)
        for candidate in entry["candidates"]
        if isinstance(candidate, str)
    }
    if str(canonical) not in final_candidates:
        raise ValueError("artifact is not a successful final render candidate")
    return canonical


def metadata_summary(metadata, media_type):
    streams = metadata.get("streams") if isinstance(metadata, dict) else None
    stream = next(
        (
            item
            for item in streams or []
            if isinstance(item, dict) and item.get("codec_type") == media_type
        ),
        {},
    )
    format_metadata = metadata.get("format") if isinstance(metadata, dict) else None
    return {
        "media_type": stream.get("codec_type"),
        "width": stream.get("width"),
        "height": stream.get("height"),
        "frame_rate": stream.get("r_frame_rate"),
        "duration_seconds": (
            format_metadata.get("duration")
            if isinstance(format_metadata, dict)
            else None
        ),
    }


def _resolution(value):
    try:
        width, height = value.lower().split("x", 1)
        resolution = (int(width), int(height))
    except (AttributeError, TypeError, ValueError) as error:
        raise argparse.ArgumentTypeError(
            "resolution must use WIDTHxHEIGHT, for example 1920x1080"
        ) from error
    if resolution[0] <= 0 or resolution[1] <= 0:
        raise argparse.ArgumentTypeError("resolution dimensions must be positive")
    return resolution


def build_parser():
    parser = argparse.ArgumentParser(
        description="Verify a rendered lesson artifact with FFprobe."
    )
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--ffprobe", default="ffprobe")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    metadata = None
    manifest = None
    canonical_artifact = None
    try:
        if args.manifest is None:
            raise ValueError("--manifest is required for workflow verification")
        manifest, root = load_manifest(args.manifest)
        canonical_artifact = authorize_artifact(manifest, root, args.artifact)
        contract = manifest["verification_contract"]
        metadata = probe(canonical_artifact, args.ffprobe)
        errors = validate(
            metadata,
            expected_resolution=(contract["width"], contract["height"]),
            min_duration=contract["min_duration_seconds"],
            expected_media_type=contract["media_type"],
            expected_frame_rate=contract["frame_rate"],
        )
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        errors = [str(error)]
    report = {"ok": not errors, "metadata": metadata, "errors": errors}
    if manifest is not None and canonical_artifact is not None:
        manifest["verification_history"].append(
            {
                "artifact": str(canonical_artifact),
                "status": "passed" if report["ok"] else "failed",
                "metadata": metadata,
                "observed": metadata_summary(
                    metadata, manifest["verification_contract"]["media_type"]
                ),
                "errors": list(errors),
                "expectations": dict(manifest["verification_contract"]),
                "verified_at": utc_now(),
            }
        )
        try:
            atomic_write_json(args.manifest, manifest)
        except (OSError, ValueError) as error:
            report["ok"] = False
            report["errors"].append(f"could not record verification: {error}")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
