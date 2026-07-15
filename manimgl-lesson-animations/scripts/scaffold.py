#!/usr/bin/env python3
"""Create an approval-gated, versioned ManimGL lesson scaffold."""

import argparse
import io
import json
import keyword
import re
import shutil
import sys
import tempfile
import tokenize
import unicodedata
import uuid
from pathlib import Path
from typing import Optional

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from workflow_state import (
    DEFAULT_VERIFICATION_CONTRACT,
    sha256_file,
    storyboard_approval,
    utc_now,
)


CLASS_SENTINEL = "TemplateLesson"
TITLE_SENTINEL = '"{{TITLE}}"'
VERSION_RE = re.compile(r"v\d{3}$")
ASSETS_ROOT = Path(__file__).resolve().parents[1] / "assets"


def slugify(value: str) -> str:
    """Return a lowercase ASCII slug suitable for an output directory."""
    ascii_value = (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    )
    slug = re.sub(r"[^A-Za-z0-9]+", "-", ascii_value).strip("-").lower()
    if not slug:
        raise ValueError("topic must produce a non-empty slug")
    return slug


def class_name(value: str) -> str:
    """Return a validated PascalCase ManimGL scene class ending in Lesson."""
    ascii_value = (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    )
    words = re.findall(r"[A-Za-z0-9]+", ascii_value)
    if not words:
        raise ValueError("topic must produce a valid Python class name")

    identifier = "".join(word[0].upper() + word[1:] for word in words) + "Lesson"
    if identifier[0].isdigit():
        identifier = "Topic" + identifier
    if not identifier.isidentifier() or keyword.iskeyword(identifier):
        raise ValueError(
            f"generated class name is not a valid Python identifier: {identifier}"
        )
    return identifier


def is_approved(text: str) -> bool:
    """Return whether text has one exact top-level Markdown approval field."""
    return storyboard_approval(text) == "APPROVED"


def _render_scene(template: str, topic_name: str, scene_name: str) -> str:
    lines = template.splitlines(keepends=True)
    line_offsets = []
    offset = 0
    for line in lines:
        line_offsets.append(offset)
        offset += len(line)

    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(template).readline))
    except (IndentationError, tokenize.TokenError) as error:
        raise ValueError(f"scene template could not be tokenized: {error}") from error

    class_tokens = [
        token
        for token in tokens
        if token.type == tokenize.NAME and token.string == CLASS_SENTINEL
    ]
    title_tokens = [
        token
        for token in tokens
        if token.type == tokenize.STRING and token.string == TITLE_SENTINEL
    ]
    if len(class_tokens) != 1:
        raise ValueError(
            "scene template must contain exactly one TemplateLesson identifier"
        )
    if len(title_tokens) != 1:
        raise ValueError(
            'scene template must contain exactly one quoted "{{TITLE}}" sentinel'
        )

    replacements = [
        (class_tokens[0], scene_name),
        (title_tokens[0], repr(topic_name)),
    ]
    rendered = template
    for token, replacement in sorted(
        replacements,
        key=lambda item: item[0].start,
        reverse=True,
    ):
        start = line_offsets[token.start[0] - 1] + token.start[1]
        end = line_offsets[token.end[0] - 1] + token.end[1]
        rendered = rendered[:start] + replacement + rendered[end:]
    try:
        compile(rendered, "scene.py", "exec")
    except SyntaxError as error:
        raise ValueError(
            f"scene template generated scene does not compile: {error.msg}"
        ) from error
    return rendered


def _next_version(topic_root: Path) -> Path:
    for number in range(1, 1000):
        candidate = topic_root / f"v{number:03d}"
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"no unused vNNN output remains under {topic_root}")


def _force_target(project: Path, slug: str, output_path: Path) -> Path:
    candidate = Path(output_path).expanduser()
    if not candidate.is_absolute():
        candidate = project / candidate
    candidate = candidate.absolute()
    if candidate.is_symlink():
        raise ValueError(
            "force-overwrite target must be a real versioned output directory"
        )
    resolved_candidate = candidate.resolve()
    expected_parent = (project / "animations" / slug).resolve()
    if (
        resolved_candidate.parent != expected_parent
        or VERSION_RE.fullmatch(resolved_candidate.name) is None
    ):
        raise ValueError(
            "force-overwrite may target only an exact versioned animations output path"
        )
    if not candidate.is_dir():
        raise FileNotFoundError(
            f"force-overwrite target must be an existing output directory: {candidate}"
        )
    return candidate


def _validate_output_root(topic_root: Path) -> None:
    animations_root = topic_root.parent
    if animations_root.is_symlink() or topic_root.is_symlink():
        raise ValueError("refusing to write through a symlinked animations output root")


def _manifest(
    topic_name: str,
    slug: str,
    scene_name: str,
    storyboard: Path,
    scene_template: Path,
    config_template: Path,
    output_choice: str,
    output_path: Path,
) -> dict:
    return {
        "approval": "APPROVED",
        "topic": topic_name,
        "slug": slug,
        "scene_name": scene_name,
        "source_paths": {
            "storyboard": str(storyboard),
            "scene_template": str(scene_template),
            "custom_config": str(config_template),
        },
        "output_choice": output_choice,
        "output_path": str(output_path.resolve()),
        "storyboard_sha256": sha256_file(storyboard),
        "verification_contract": dict(DEFAULT_VERIFICATION_CONTRACT),
        "render_history": [],
        "verification_history": [],
        "created_at": utc_now(),
    }


def _populate_staging(
    staging: Path,
    storyboard: Path,
    rendered_scene: str,
    config_template: Path,
    manifest: dict,
) -> None:
    shutil.copy2(storyboard, staging / "storyboard.md")
    (staging / "scene.py").write_text(rendered_scene, encoding="utf-8")
    shutil.copy2(config_template, staging / "custom_config.yml")
    for directory in ("previews", "images", "videos"):
        (staging / directory).mkdir()
    (staging / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _publish_overwrite(staging: Path, output_path: Path) -> None:
    backup = output_path.parent / f".{output_path.name}.backup-{uuid.uuid4().hex}"
    output_path.rename(backup)
    try:
        staging.rename(output_path)
    except BaseException:
        backup.rename(output_path)
        raise
    shutil.rmtree(backup)


def _remove_empty_output_parents(project: Path, topic_root: Path) -> None:
    animations_root = project / "animations"
    for directory in (topic_root, animations_root):
        try:
            directory.rmdir()
        except OSError:
            pass


def scaffold(
    project: Path,
    topic_name: str,
    storyboard: Path,
    force: bool = False,
    output_path: Optional[Path] = None,
) -> Path:
    """Create the next version or explicitly replace one named existing output."""
    project = Path(project).expanduser().absolute()
    storyboard = Path(storyboard).expanduser().resolve()

    storyboard_text = storyboard.read_text(encoding="utf-8")
    if not is_approved(storyboard_text):
        raise ValueError("storyboard must be explicitly approved before scaffolding")

    slug = slugify(topic_name)
    scene_name = class_name(topic_name)
    scene_template = ASSETS_ROOT / "scene-template.py"
    config_template = ASSETS_ROOT / "custom_config.yml"
    rendered_scene = _render_scene(
        scene_template.read_text(encoding="utf-8"), topic_name, scene_name
    )
    config_template.read_bytes()

    topic_root = project / "animations" / slug
    _validate_output_root(topic_root)
    if force:
        if output_path is None:
            raise ValueError("force-overwrite requires the exact output path")
        output = _force_target(project, slug, output_path)
        output_choice = "force-overwrite"
    else:
        if output_path is not None:
            raise ValueError(
                "an output path is accepted only with an explicit "
                "force-overwrite choice"
            )
        output = _next_version(topic_root)
        output_choice = "new-version"

    manifest = _manifest(
        topic_name,
        slug,
        scene_name,
        storyboard,
        scene_template.resolve(),
        config_template.resolve(),
        output_choice,
        output,
    )

    topic_root_existed = topic_root.exists()
    topic_root.mkdir(parents=True, exist_ok=True)
    published = False
    try:
        with tempfile.TemporaryDirectory(
            prefix=".scaffold-", dir=topic_root
        ) as temporary:
            staging = Path(temporary)
            _populate_staging(
                staging,
                storyboard,
                rendered_scene,
                config_template,
                manifest,
            )
            if force:
                _publish_overwrite(staging, output)
            else:
                if output.exists():
                    raise FileExistsError(f"output already exists: {output}")
                staging.rename(output)
            published = True
    finally:
        if not published and not topic_root_existed:
            _remove_empty_output_parents(project, topic_root)

    return output


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create an approval-gated ManimGL lesson scaffold."
    )
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--topic", required=True)
    parser.add_argument("--storyboard", required=True, type=Path)
    parser.add_argument(
        "--force-overwrite",
        type=Path,
        metavar="EXACT_OUTPUT_PATH",
        help="replace only the named existing animations/<slug>/vNNN output",
    )
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        output = scaffold(
            args.project,
            args.topic,
            args.storyboard,
            force=args.force_overwrite is not None,
            output_path=args.force_overwrite,
        )
    except (OSError, RuntimeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
