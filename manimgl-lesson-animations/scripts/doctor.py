#!/usr/bin/env python3

import argparse
from dataclasses import dataclass
import importlib.util
import json
import shutil
import sys
from typing import Optional


@dataclass(frozen=True)
class Check:
    name: str
    status: str  # OK, WARNING, BLOCKER
    message: str


def collect_checks(
    which=shutil.which,
    find_spec=importlib.util.find_spec,
    version=sys.version_info,
) -> list[Check]:
    python_version = tuple(version[:3])
    python_compatible = python_version[:2] >= (3, 9)
    manimlib_available = find_spec("manimlib") is not None
    renderer = which("manimgl") or which("manim-render")
    ffmpeg = which("ffmpeg")
    ffprobe = which("ffprobe")
    latex = which("latex")
    moderngl_available = find_spec("moderngl") is not None

    return [
        Check(
            "python",
            "OK" if python_compatible else "BLOCKER",
            f"Python {'.'.join(map(str, python_version))}"
            + ("" if python_compatible else "; Python 3.9 or newer is required."),
        ),
        Check(
            "manimlib",
            "OK" if manimlib_available else "BLOCKER",
            "Python import is available."
            if manimlib_available
            else "Python cannot import manimlib.",
        ),
        Check(
            "manimgl",
            "OK" if renderer else "BLOCKER",
            renderer or "Neither manimgl nor manim-render was found.",
        ),
        Check(
            "ffmpeg",
            "OK" if ffmpeg else "BLOCKER",
            ffmpeg or "FFmpeg was not found on PATH.",
        ),
        Check(
            "ffprobe",
            "OK" if ffprobe else "BLOCKER",
            ffprobe or "FFprobe was not found on PATH.",
        ),
        Check(
            "latex",
            "OK" if latex else "WARNING",
            latex or "LaTeX was not found; formula scenes may need it.",
        ),
        Check(
            "moderngl",
            "OK" if moderngl_available else "WARNING",
            "Python import is available."
            if moderngl_available
            else "Python cannot import moderngl; rendering may need it.",
        ),
    ]


def exit_code(checks: list[Check]) -> int:
    return int(any(check.status == "BLOCKER" for check in checks))


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Diagnose prerequisites for 3Blue1Brown ManimGL."
    )
    parser.add_argument("--json", action="store_true", help="Print checks as JSON.")
    args = parser.parse_args(argv)
    checks = collect_checks()

    if args.json:
        print(
            json.dumps(
                [
                    {
                        "name": check.name,
                        "status": check.status,
                        "message": check.message,
                    }
                    for check in checks
                ],
                indent=2,
            )
        )
    else:
        name_width = max(len(check.name) for check in checks)
        status_width = max(len(check.status) for check in checks)
        for check in checks:
            print(
                f"{check.name:<{name_width}}  "
                f"{check.status:<{status_width}}  {check.message}"
            )

    return exit_code(checks)


if __name__ == "__main__":
    raise SystemExit(main())
