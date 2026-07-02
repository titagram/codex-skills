#!/usr/bin/env python3
"""Print compact readability stats for Italian lesson teleprompter files."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


WORD_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]+(?:['-][A-Za-zÀ-ÖØ-öø-ÿ0-9]+)?")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
MARKER_RE = re.compile(r"^\[(?:CAMBIO SLIDE|SLIDE)\s+\d+[^\]]*\]$", re.IGNORECASE)


def words(text: str) -> list[str]:
    return WORD_RE.findall(text)


def paragraph_ranges(lines: list[str]) -> list[tuple[int, int, str]]:
    ranges: list[tuple[int, int, str]] = []
    start: int | None = None
    current: list[str] = []

    for idx, line in enumerate(lines, start=1):
        if line.strip():
            if start is None:
                start = idx
            current.append(line.strip())
            continue

        if start is not None:
            ranges.append((start, idx - 1, " ".join(current)))
            start = None
            current = []

    if start is not None:
        ranges.append((start, len(lines), " ".join(current)))

    return ranges


def sentence_word_counts(text: str) -> list[int]:
    compact = " ".join(line.strip() for line in text.splitlines() if line.strip())
    sentences = [part.strip() for part in SENTENCE_SPLIT_RE.split(compact) if part.strip()]
    return [len(words(sentence)) for sentence in sentences]


def format_locations(items: list[tuple[int, int]], limit: int = 8) -> str:
    if not items:
        return "none"
    shown = ", ".join(f"{line}({value})" for line, value in items[:limit])
    if len(items) > limit:
        shown += f", +{len(items) - limit} more"
    return shown


def analyze(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="replace")

    lines = text.splitlines()
    token_count = len(words(text))
    reading_minutes = token_count / 135 if token_count else 0
    paragraphs = paragraph_ranges(lines)
    sentence_counts = sentence_word_counts(text)

    long_lines = [(i, len(line)) for i, line in enumerate(lines, start=1) if len(line) > 100]
    very_long_sentences = sum(1 for count in sentence_counts if count > 35)
    max_sentence = max(sentence_counts, default=0)

    long_paragraphs = [
        (start, len(words(body)))
        for start, _end, body in paragraphs
        if len(words(body)) > 140
    ]
    markers = [(i, line.strip()) for i, line in enumerate(lines, start=1) if MARKER_RE.match(line.strip())]
    punctuated_paragraphs = sum(
        1 for _start, _end, body in paragraphs if body.rstrip().endswith((".", "!", "?", ":"))
    )
    non_ascii = sum(1 for char in text if ord(char) > 127)

    result = [
        f"== {path} ==",
        f"words: {token_count}",
        f"estimated_reading_time: {reading_minutes:.1f} min @ 135 wpm",
        f"lines: {len(lines)} total, {sum(1 for line in lines if line.strip())} non-empty",
        f"paragraphs: {len(paragraphs)} ({punctuated_paragraphs} end with . ! ? or :)",
        f"slide_markers: {len(markers)}",
        f"long_lines_gt_100: {format_locations(long_lines)}",
        f"long_sentences_gt_35_words: {very_long_sentences}; max_sentence_words: {max_sentence}",
        f"long_paragraphs_gt_140_words: {format_locations(long_paragraphs)}",
        f"non_ascii_chars: {non_ascii}",
    ]

    if markers:
        result.append(f"first_marker: line {markers[0][0]} {markers[0][1]}")
        result.append(f"last_marker: line {markers[-1][0]} {markers[-1][1]}")

    return "\n".join(result)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", help="Teleprompter .txt/.md files to inspect")
    args = parser.parse_args(argv)

    exit_code = 0
    outputs: list[str] = []
    for raw_path in args.files:
        path = Path(raw_path)
        if not path.is_file():
            outputs.append(f"== {path} ==\nerror: not a file")
            exit_code = 1
            continue
        outputs.append(analyze(path))

    print("\n\n".join(outputs))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
