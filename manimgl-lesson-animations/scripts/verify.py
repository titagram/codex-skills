#!/usr/bin/env python3
"""Verify rendered lesson artifacts with FFprobe metadata."""

import argparse
import json
import math
import shutil
import subprocess
from fractions import Fraction
from pathlib import Path


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
    parser.add_argument("--ffprobe", default="ffprobe")
    parser.add_argument("--media-type", default="video")
    parser.add_argument("--expected-resolution", type=_resolution)
    parser.add_argument("--min-duration", type=float)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    metadata = None
    try:
        metadata = probe(args.artifact, args.ffprobe)
        errors = validate(
            metadata,
            expected_resolution=args.expected_resolution,
            min_duration=args.min_duration,
            expected_media_type=args.media_type,
        )
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        errors = [str(error)]
    report = {"ok": not errors, "metadata": metadata, "errors": errors}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
