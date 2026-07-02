---
name: lesson-markdown
description: Turn a curriculum CSV or syllabus outline into one coordinator markdown per chapter for slide-generation and teleprompter production. Use when Codex must inspect local course files, ask the user up front how many minutes each lesson or session should last, segment long chapters into sessions, estimate teleprompter length at 120 words per minute, count slides, and write detailed Italian `coordinamento_agente.md` instructions for a downstream slide and teleprompter agent.
---

# Lesson Markdown

## Goal

Generate one `coordinamento_agente.md` per chapter from a local curriculum source, so another AI
agent can produce slides and a full teleprompter with explicit slide-change markers.

## Workflow

1. Inspect the workspace before writing.
2. Ask for lesson timing at the start if the user has not already specified it.
3. Normalize the source structure into chapters, subtopics, and optional lab blocks.
4. Build a didactic breakdown that respects prerequisites.
5. Compute minutes, words, and slide counts.
6. Write one coordinator markdown per chapter.
7. Verify arithmetic and chapter coverage before finishing.

## Step 1 - Inspect the local source

Read the actual files first. Prefer local truth over assumptions.

- Look for curriculum files such as `.csv`, `.tsv`, or other simple syllabus exports.
- Look for existing example folders for slide style, structure, or naming.
- Detect whether the source has:
  - chapter titles with explicit minutes;
  - detail rows that belong to the previous chapter;
  - separate `Laboratorio` rows;
  - inconsistent totals between header hours and row-by-row minutes.

If an example slide folder exists, reuse it as the required aesthetic and structural reference.
Mention its absolute path in every generated markdown.

## Step 2 - Ask for lesson duration first

If the user has not already specified lesson/session length, ask immediately before generating the
chapter markdowns.

Use one concise question. Ask for:

- the target duration of each lesson or session in minutes;
- whether the same duration applies to all chapters or whether there are exceptions.

If the user already provided durations, do not ask again.

## Step 3 - Interpret timing correctly

Use these defaults unless the user says otherwise:

- Treat the user-provided lesson/session duration as the target size for each teaching block.
- Treat source minutes in the CSV as content weight and existing planning intent.
- Keep one markdown file per chapter.
- Split chapters longer than the requested lesson duration into multiple internal sessions.
- Keep shorter chapters as a single session unless the user explicitly asks to merge chapters.
- Do not merge different chapters by default.
- If the source includes standalone lab rows, integrate them into the nearest compatible theory
  chapters and state the redistribution explicitly.

When the source minutes and the user timing conflict:

- obey the user timing for session sizing;
- use the source minutes to preserve content weight and ordering;
- state the assumption clearly in the generated files or final report.

## Step 4 - Build the didactic path

Preserve chapter order unless the user explicitly asks for a reorder.

Design each chapter from concrete to abstract:

- open with the problem or intuition;
- define the concept;
- show mechanism or rule;
- give a small example;
- warn about one common mistake;
- close with recap or bridge.

Do not introduce advanced material before its prerequisites.

For school technical subjects, prefer a patient, spoken, explanatory style in Italian. The target
tone for the downstream teleprompter is didactic, clear, concrete, and close to a Feynman-style
explanation.

## Step 5 - Compute the numeric targets

Use these formulas unless the user provides different rules:

- `parole_totali = minuti_totali * 120`
- `slide_totali = ceil(minuti_totali / 3)`

For internal sessions:

- `parole_sessione = minuti_sessione * 120`
- `slide_sessione = ceil(minuti_sessione / 3)`

For subchapters:

- allocate minutes first;
- derive words from the minute allocation;
- keep arithmetic exact at chapter level.

If a chapter duration is not divisible cleanly across subtopics, distribute the remainder in a way
that keeps the total exact and the explanation pedagogically coherent.

## Step 6 - Write the coordinator markdowns

Write one `coordinamento_agente.md` per chapter, inside numbered chapter folders. Reuse existing
folders when present; otherwise create new numbered folders near the source curriculum.

Each generated markdown must contain:

- chapter title;
- class/year;
- total duration in minutes;
- total words estimated at 120 wpm;
- total slides;
- required aesthetic reference path;
- `Mandato operativo`;
- `Output obbligatori`;
- `Vincoli non negoziabili`;
- `Prerequisiti`;
- `Obiettivi didattici`;
- `Errori tipici da prevenire`;
- `Deliverable richiesti`;
- `Mappa sessioni`;
- one section for each internal session with:
  - duration;
  - words;
  - slides;
  - didactic objective;
  - recommended analogies/examples;
  - visual suggestions;
  - required teleprompter marker range;
- a timed subchapter outline;
- `Checklist finale`.

Each markdown must instruct the downstream agent to generate:

1. the slide deck or slide folder;
2. a full teleprompter in Italian, also acceptable as `.txt`;
3. explicit marker lines such as `[CAMBIO SLIDE 07]`.

## Step 7 - Preserve source coverage

Map source rows carefully.

- Treat multiline bullet rows as details of the previous titled chapter unless the structure clearly
  indicates a new chapter.
- Ensure every bullet or subtopic from the source is covered exactly once.
- If you redistribute lab time, do not lose any lab topic.
- If a header total is inconsistent with the sum of the rows, state the discrepancy explicitly.

## Validation

Before finishing, verify:

- the number of generated markdown files matches the intended number of chapters;
- the sum of subchapter minutes equals the chapter total;
- the sum of session slides equals the chapter total slide count;
- total words equal `minutes * 120`;
- every source topic appears once and only once;
- every file asks for both slides and teleprompter;
- every file includes explicit slide-change markers and the example reference path.

If validation reveals a mismatch, fix the files before reporting completion.
