#!/usr/bin/env python3

import argparse
import os
from pathlib import Path
import shlex
import subprocess
import sys
from typing import Optional


def venv_python(project: Path) -> Path:
    if os.name == "nt":
        return project / ".venv" / "Scripts" / "python.exe"
    return project / ".venv" / "bin" / "python"


def build_commands(
    project: Path, python: str, spec: str = "manimgl"
) -> list[list[str]]:
    return [
        [python, "-m", "venv", str(project / ".venv")],
        [str(venv_python(project)), "-m", "pip", "install", "--upgrade", "pip"],
        [str(venv_python(project)), "-m", "pip", "install", spec],
    ]


def execute(commands: list[list[str]]) -> None:
    for command in commands:
        subprocess.run(command, check=True)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Prepare a project-local ManimGL virtual environment."
    )
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--spec", default="manimgl")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Run the printed commands. Without this flag, this is a dry run.",
    )
    parser.add_argument(
        "--reuse",
        action="store_true",
        help="Allow an existing project-local .venv.",
    )
    args = parser.parse_args(argv)

    environment = args.project / ".venv"
    environment_present = os.path.lexists(str(environment))
    if environment_present and not args.reuse:
        parser.error(f"{environment} already exists; pass --reuse to keep using it.")
    if environment_present and args.reuse:
        local_directory = (
            not environment.is_symlink()
            and environment.is_dir()
            and environment.resolve().parent == args.project.resolve()
        )
        if not local_directory:
            parser.error(
                f"{environment} must be a real project-local directory for --reuse."
            )

    commands = build_commands(args.project, args.python, args.spec)
    for command in commands:
        print(shlex.join(command))

    if args.execute:
        execute(commands)
        subprocess.run(
            [str(venv_python(args.project)), "-c", "import manimlib"],
            check=True,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
