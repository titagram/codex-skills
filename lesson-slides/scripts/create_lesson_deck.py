#!/usr/bin/env python3
import argparse
import html
import shutil
from pathlib import Path


def render_template(text, values):
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", html.escape(value, quote=True))
    return text


def main():
    parser = argparse.ArgumentParser(
        description="Create a lesson slide deck from the lesson-slides HTML template."
    )
    parser.add_argument("output_dir", help="Directory where the deck files should be created.")
    parser.add_argument("--title", required=True, help="Deck title.")
    parser.add_argument("--subtitle", default="Lezione operativa con esempi, metodo e verifiche")
    parser.add_argument("--meta", default="Slide didattiche")
    parser.add_argument("--description", default=None)
    parser.add_argument("--force", action="store_true", help="Allow writing into a non-empty directory.")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    skill_dir = script_dir.parent
    template_dir = skill_dir / "assets" / "template"
    output_dir = Path(args.output_dir).expanduser().resolve()

    if not template_dir.is_dir():
        raise SystemExit(f"Template directory not found: {template_dir}")

    if output_dir.exists() and not output_dir.is_dir():
        raise SystemExit(f"Output path exists and is not a directory: {output_dir}")
    if output_dir.exists() and any(output_dir.iterdir()) and not args.force:
        raise SystemExit(f"Output directory is not empty, pass --force to write into it: {output_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    description = args.description or f"Slide didattiche su {args.title}."
    html_template = (template_dir / "index.html").read_text(encoding="utf-8")
    rendered = render_template(
        html_template,
        {
            "DECK_TITLE": args.title,
            "DECK_SUBTITLE": args.subtitle,
            "DECK_META": args.meta,
            "DECK_DESCRIPTION": description,
        },
    )

    (output_dir / "index.html").write_text(rendered, encoding="utf-8")
    shutil.copy2(template_dir / "style.css", output_dir / "style.css")
    shutil.copy2(template_dir / "script.js", output_dir / "script.js")

    print(f"Created lesson deck at {output_dir}")
    print(f"Open {output_dir / 'index.html'}")


if __name__ == "__main__":
    main()
