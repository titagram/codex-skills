---
name: lesson-teleprompter
description: Write, rewrite, expand, translate, or adapt Italian lesson teleprompter scripts in a clear, patient, concrete, technically precise spoken style for high-school students. Use when asked to improve teleprompter.txt, slide narration, speaker notes, narrated lessons, didactic scripts, or source material that must become readable aloud without repetition, especially when following a stile_narrativo.md-like style.
---

# Lesson Teleprompter

## Goal

Produce a spoken lesson script that sounds like a well-prepared teacher: clear, patient, concrete,
technically precise, and easy to read aloud. Guide the student through reasoning instead of
reciting definitions.

## Workflow

1. Read the existing teleprompter, nearby slide content, and any local style file such as
   `stile_narrativo.md`.
2. Preserve structure markers exactly, especially lines like `[CAMBIO SLIDE 13]`. Keep markers on
   isolated lines and do not treat them as spoken text.
3. Identify the role of the requested slide or block in the lesson: introduction, concept,
   mechanism, example, misconception, synthesis, or transition.
4. Translate and reorganize source material before writing. Do not paste table-like source text as
   prose.
5. Rewrite as natural Italian spoken narration, not as manual prose.
6. Keep technical precision. Correct source inaccuracies when needed and mention the correction only
   if it matters for the user.
7. For technical blocks, self-check that the explanation teaches the mechanism instead of merely
   naming the concept. If the text would not help a confused student predict the next state of a
   register, memory cell, pointer, flag, or output, rewrite it before finishing.
8. Verify marker count, line readability, and residue from generated/repetitive text before
   claiming completion.

## Voice

Use this tone:

- clear and calm;
- teacherly but not academic;
- concrete before abstract;
- patient with technical terms;
- suitable for upper-secondary students;
- exact enough for technical subjects;
- free of motivational filler, jokes, and dramatic emphasis.

Prefer:

- short or medium-short sentences;
- present indicative;
- direct transitions: `Vediamo`, `A questo punto`, `Qui bisogna fare attenzione`,
  `Il punto importante e`;
- questions that guide the reasoning;
- examples close to students' experience;
- one clear takeaway per block.

Avoid:

- textbook definitions detached from examples;
- Italian that sounds translated from English, such as stacked nouns, abstract labels, or phrases
  like `il registro indica dove guardare dentro il segmento` when a concrete sentence would work
  better;
- long source-like paragraphs;
- repeated boilerplate across slides;
- phrases such as `Questo punto va letto in relazione...`, `Fermiamoci ancora un istante...`
  when they become mechanical;
- saying the same learning objective on every slide;
- overloading a slide with every detail from the source.

## Block Pattern

For each slide or narrative block, usually follow this order:

1. Open with a concrete situation or a transition from the previous idea.
2. Show why the intuitive explanation is incomplete.
3. Name the correct concept.
4. Explain the mechanism or rule.
5. Give a small example.
6. Correct a plausible misconception.
7. Close with the idea to remember or a bridge to the next slide.

Not every block needs all seven moves. Keep the flow natural.

## Technical Explanation Gate

For dense technical lessons, especially assembly, networking, operating systems, databases, and
programming, do not write a compressed summary of slide labels. Write a guided explanation that a
student can follow while looking at the tool or code.

Before accepting a block, check that it includes enough of these elements:

- a concrete starting state, for example `SP = 0100`, `AX = 1234`, `SI punta all'inizio`;
- the operation being executed, for example `PUSH AX`, `CALL doppio`, `byte [SI]`;
- the visible effect, for example `SP scende di 2`, `BX torna 7777`, `SI passa al byte successivo`;
- the reason behind the effect, not only the name of the concept;
- one misconception corrected in ordinary Italian.

Prefer sentences like:

`Se SI contiene l'offset dell'inizio dell'array, byte [SI] legge il primo byte. Se poi facciamo INC
SI, non cambiamo il dato: cambiamo la posizione.`

Avoid sentences like:

`DS:SI e la coppia normale per leggere dati e array.`

That kind of sentence can appear on a slide, but in the teleprompter it must be expanded into a
spoken explanation.

## Anti-Translation Check

After drafting, reread each block aloud. If it sounds like English technical prose translated into
Italian, rewrite it.

Watch especially for:

- abstract openings that do not create a situation;
- chains of nouns instead of verbs;
- `concetto`, `meccanismo`, `informazione`, `riferimento` repeated without examples;
- sentences that state a relation but do not show what changes in practice;
- endings like generic takeaways that could fit any slide.

Use plain classroom Italian instead:

- `Partiamo da...`;
- `Supponiamo che...`;
- `Qui succede una cosa importante...`;
- `Il dato non cambia; cambia la posizione.`;
- `Dopo questa istruzione, che cosa mi aspetto di vedere?`.

## Adapting Dense Source Material

When the user provides long English or technical source text:

- translate the concepts, not the paragraph structure;
- group related ideas into a few spoken sections;
- preserve important terms in Italian with the English acronym when useful, for example
  `unita di controllo, o CU`;
- define acronyms at first use;
- include examples only when they clarify the mechanism;
- turn tables into explanatory comparisons;
- keep caveats when they prevent a wrong simplification.

For technical lessons, distinguish carefully:

- CPU vs whole computer;
- clock cycle vs instruction cycle;
- ISA vs assembly syntax vs microarchitecture;
- cache vs RAM vs storage;
- registers vs memory;
- data movement vs computation vs control.

## Teleprompter Formatting

When editing an existing `teleprompter.txt`:

- Keep slide markers unchanged and in order.
- Keep paragraphs separated by blank lines.
- Wrap long lines for readability, usually around 90-100 characters.
- Match the file's character style. If the file is ASCII-only Italian, keep forms like `e`,
  `perche`, `piu`, `unita`, unless the user asks for accents.
- Do not add Markdown headings inside the teleprompter unless the existing file already uses them.

## Quality Bar

A good output should be readable aloud without stumbling. It should sound like one continuous
lesson, not a stitched summary. It should remove repetition while preserving the technical
substance.

Before finishing, run checks appropriate to the file:

```bash
awk '/^\[CAMBIO SLIDE [0-9][0-9]\]$/ {n++} END {print n}' teleprompter.txt
awk 'length($0)>100 {print NR ":" length($0); bad=1} END {exit bad}' teleprompter.txt
rg -n "Questo punto va letto|Fermiamoci ancora|diventa comprensibile solo" teleprompter.txt
LC_ALL=C rg -n "[^[:ascii:]]" teleprompter.txt
```

Use the checks as evidence, not as ritual. Adjust paths and patterns to the actual file.
