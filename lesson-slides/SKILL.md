---
name: lesson-slides
description: >-
  Create, update, or restyle HTML lesson slide decks that must strictly match Gabriele's dark classroom slide style: full-screen web presentation, Inter/Fira Code typography, dark slate background, violet accents, two-column explanatory slides, diagram containers, SQL/code boxes, comparison tables, cards, warnings, guided examples, mini-checks, and session-based teaching rhythm. Use when the user asks in Italian or English to create lesson slides, course slides, educational decks, teleprompter-to-slides outputs, or slides "in questo stile", "seguendo questo stile", or with the lesson-slides style.
---

# Lesson Slides

## Workflow

1. For a new deck, run `scripts/create_lesson_deck.py <output-dir> --title "<title>"`.
2. Read `references/style-guide.md` before writing or changing slide content.
3. Keep `assets/template/style.css` and `assets/template/script.js` as the canonical style and navigation files. Copy them unchanged unless the user explicitly asks for a style evolution.
4. Build all slides as direct `.slide` children of `#presentation-container`, then keep `#controls` and `<script src="script.js"></script>` at the end of `body`.
5. Use the established teaching rhythm: title, concept, "Operativamente", "Esempio guidato", "Errori da evitare", "Mini-check", and session divider slides where useful.
6. Verify the deck in a browser or with a local static server. Check slide navigation, counter, text fit, and that visual content does not overflow the 80vh slide frame.

## Style Contract

- Use the provided template. Do not start from a generic slide framework, a marketing page, Reveal.js, Bootstrap, Tailwind, or a new visual theme.
- Preserve the dark slate palette, violet accent, soft glow, compact rounded cards, and code-first didactic look.
- Prefer the canonical layout: left column with explanation and bullets; right column with `.diagram-container`, `.chart-container`, a table, code block, flowchart, card stack, or warning.
- Keep slides dense but readable: one clear paragraph plus 3-5 bullets is the default.
- Keep headings concrete and lesson-oriented. Use Italian labels such as `Operativamente:`, `Esempio guidato:`, `Errori da evitare:`, `Mini-check:` when the deck is in Italian.
- Use `<code>` for inline technical terms and `.code-example` with `<span class="label-lang">SQL</span>` or another language label for blocks.
- Use only the component classes documented in the style guide unless a new component is genuinely needed.

## Resources

- `scripts/create_lesson_deck.py`: scaffold a deck directory from the canonical template and set title metadata.
- `assets/template/`: canonical `index.html`, `style.css`, and `script.js` copied into new decks.
- `references/style-guide.md`: exact visual rules, layout patterns, and HTML snippets to follow.
