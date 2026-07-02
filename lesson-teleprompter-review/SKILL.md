---
name: lesson-teleprompter-review
description: Review, annotate, and correct one or more Italian lesson teleprompter text files. Use when Codex is asked to judge whether a teleprompter script sufficiently covers a lesson topic, whether it is suitable to be read aloud by a teacher recording a lesson, whether the Italian is natural and correct, whether pauses and transitions are adequate, and then plan and apply corrections while preserving slide markers and file structure.
---

# Lesson Teleprompter Review

## Goal

Turn one or more draft teleprompter files into recording-ready Italian lesson scripts. Always do
both jobs unless the user asks otherwise: evaluate the script, then correct it.

## Workflow

1. Identify the target text files. If the user provides directories or vague names, search for
   likely files such as `teleprompter.txt`, `*_teleprompter.txt`, `.md`, or `.txt`.
2. Read every target file completely. Also read nearby context when available: slide markdown,
   lesson outline, source notes, `stile_narrativo.md`, or existing chapter files.
3. Run the stats helper before editing:

   ```bash
   python3 scripts/teleprompter_stats.py FILE...
   ```

4. Assess content quality: decide whether the script would be sufficient to cover the topic for
   the intended lesson, using available context. Mark uncertainty explicitly when no source or
   outline exists.
5. Assess spoken form: decide whether a professor could read it naturally while recording. Check
   Italian correctness, oral rhythm, pauses, paragraphing, transitions, repetition, and whether the
   language sounds human rather than generated or translated.
6. Create a correction map before editing. Use concrete locations: `file:line`, marker names such
   as `[CAMBIO SLIDE 12]`, or paragraph ranges. Include only corrections that matter.
7. Apply the corrections to the target files. Preserve slide markers, ordering, meaning, and local
   formatting conventions.
8. Rerun the stats helper and targeted checks. Report what changed and any remaining uncertainty.

## Evaluation Criteria

For content, check:

- coverage of the declared topic, prerequisites, key definitions, mechanisms, examples, and likely
  misconceptions;
- conceptual accuracy and consistency with nearby slides or source material;
- useful sequencing from simple to complex, not a list of disconnected points;
- enough concrete examples for a student to follow the reasoning;
- transitions between slides or sections, especially when the argument changes direction.

For spoken form, check:

- natural classroom Italian, not textbook prose and not literal translation from English;
- sentence length suitable for reading aloud, with a preference for short and medium sentences;
- clear pauses through blank lines, paragraph breaks, and punctuation;
- direct teacherly transitions such as `Vediamo`, `A questo punto`, `Qui bisogna fare attenzione`;
- no filler, generic motivation, repeated boilerplate, or overdramatic emphasis;
- accent and encoding style consistent with the file. If the file is ASCII-only, keep ASCII unless
  the user asks for accents.

## Correction Map

Before editing, keep a compact working table like this:

```text
file | location | issue | planned correction
teleprompter.txt | [CAMBIO SLIDE 8], lines 122-138 | Long abstract block, weak example | Split into two spoken paragraphs and add a concrete state transition
```

Use the map to guide edits. In the final answer, summarize the most important corrections rather
than dumping the entire table unless the user asked for a full audit report.

## Editing Rules

- Preserve lines like `[CAMBIO SLIDE 13]` exactly and keep them isolated.
- Do not silently delete content markers, TODOs, slide separators, or section anchors.
- Do not add Markdown headings inside a plain teleprompter unless the file already uses headings.
- Keep paragraphs separated by blank lines. Prefer readable line wrapping around 90-100 characters
  when the file already wraps lines.
- Fix Italian grammar, agreement, punctuation, word order, and unnatural phrasing.
- Convert dense explanations into spoken teaching: start from a situation, show what changes, name
  the concept, give a small example, then close with the point to remember.
- Add missing content only when it is inferable from the file or nearby context. If an important
  gap cannot be filled responsibly, leave the file coherent and report the gap.
- Avoid rewriting everything when targeted edits solve the problem. Preserve the teacher's useful
  voice and the lesson's intended structure.

## Verification

After editing, run the helper again and compare the before/after signal. Then run targeted checks
appropriate to the files, for example:

```bash
rg -n "Questo punto va letto|Fermiamoci ancora|diventa comprensibile solo" FILE...
awk 'length($0)>110 {print FILENAME ":" FNR ":" length($0)}' FILE...
```

If slide markers exist, verify that their count and order did not change unless the user explicitly
requested structural changes.

Final response should include:

- files changed;
- the main content and form problems corrected;
- verification performed;
- remaining gaps that need source material or human subject-matter judgment.
