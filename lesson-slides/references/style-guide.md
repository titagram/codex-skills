# Lesson Slides Style Guide

Use this guide when creating or editing lesson decks with `$lesson-slides`. The canonical CSS and JS live in `assets/template/`; copy them rather than recreating them.

## Visual Identity

- Background: `#0f172a`, full viewport, no body scroll.
- Text: `#f8fafc` main, `#e2e8f0` body, `#94a3b8` muted.
- Accent: violet `#a78bfa`; dim violet `#7c3aed`; glow `rgba(167, 139, 250, 0.15)`.
- Semantic colors: green `#10b981`, yellow `#eab308`, red `#ef4444`, cyan `#38bdf8`.
- Fonts: Inter for text, Fira Code for code and counters.
- Mood: technical, compact, classroom-focused, not decorative or marketing-like.

## Page Structure

Keep this outer skeleton:

```html
<div id="presentation-container">
    <div class="slide slide-title active" id="slide-1">...</div>
    <div class="slide" id="slide-2">...</div>
</div>
<div id="controls">
    <button id="prevBtn" onclick="prevSlide()">&#8592; Precedente</button>
    <span id="slide-counter">1 / N</span>
    <button id="nextBtn" onclick="nextSlide()">Successiva &#8594;</button>
</div>
<script src="script.js"></script>
```

The script updates the counter at runtime. Keep slide ids sequential: `slide-1`, `slide-2`, etc.

## Slide Geometry

- `.slide`: width `85%`, max-width `1100px`, height `80vh`, centered in the viewport.
- Title slide: centered, large violet `h1`, grey subtitle and metadata.
- Normal slide: `h2` at top with violet color and bottom border.
- Default content layout: `.two-col` with left text and right visual.
- Left column: explanatory paragraph, then bullets or a code block. Keep 3-5 bullets.
- Right column: `.diagram-container` or `.chart-container`, never an empty decorative panel.

## Teaching Rhythm

For each concept block, prefer this sequence:

1. Concept slide: define the idea and show a flow, table, or small schema.
2. `Operativamente:` slide: convert the idea into steps.
3. `Esempio guidato:` slide: show a concrete, small, complete case.
4. `Errori da evitare:` slide: show pitfalls with warning/card visuals.
5. `Mini-check:` slide: close with checks students can use.

Use session dividers for long decks:

```html
<div class="slide" id="slide-N">
    <h2>Sessione 2 - Titolo della sessione</h2>
    <div class="two-col">...</div>
</div>
```

## Canonical Components

### Two-column Concept Slide

```html
<div class="slide" id="slide-N">
    <h2>Titolo concreto</h2>
    <div class="two-col">
        <div>
            <p>Spiegazione breve che collega concetto e uso pratico.</p>
            <ul>
                <li>Punto operativo 1.</li>
                <li>Punto operativo 2.</li>
                <li>Punto operativo 3.</li>
            </ul>
        </div>
        <div class="diagram-container">
            <!-- visual component -->
        </div>
    </div>
</div>
```

### Vertical Flowchart

```html
<div class="flowchart-css">
    <div class="fc-node fc-dark">Domanda</div>
    <div class="fc-arrow"></div>
    <div class="fc-node fc-blue fc-border-blue">Tabelle</div>
    <div class="fc-arrow"></div>
    <div class="fc-node fc-purple fc-border-purple">JOIN</div>
    <div class="fc-arrow"></div>
    <div class="fc-node fc-green fc-border-green">Risultato</div>
</div>
```

### Code Example

```html
<div class="code-example"><span class="label-lang">SQL</span>
SELECT colonna
FROM tabella
WHERE condizione;</div>
```

Rules: keep code short enough to fit. If a query is long, put explanation on the left and code on the right.

### Comparison Table

```html
<table class="comparison-table">
    <tr><th>Elemento</th><th>Esempio</th><th>Significato</th></tr>
    <tr><td>Tipo</td><td><code>VARCHAR(40)</code></td><td>testo fino a 40 caratteri</td></tr>
    <tr><td>Chiave primaria</td><td><code>PRIMARY KEY</code></td><td>ID univoco</td></tr>
</table>
```

### Card Stack

```html
<div class="card-row" style="flex-direction: column; gap: 10px;">
    <div class="info-card blue"><h4>Passo 1</h4><p>Descrizione breve.</p></div>
    <div class="info-card green"><h4>Passo 2</h4><p>Descrizione breve.</p></div>
    <div class="info-card yellow"><h4>Passo 3</h4><p>Descrizione breve.</p></div>
    <div class="info-card red"><h4>Passo 4</h4><p>Descrizione breve.</p></div>
</div>
```

### Warning Box

```html
<div class="warning-box">Prima controlla il filtro con SELECT, poi esegui UPDATE o DELETE.</div>
```

### Mini Table Cards

```html
<div class="table-card-grid">
    <div class="table-card">
        <h4>Studenti</h4>
        <table>
            <tr><th>id</th><th>nome</th></tr>
            <tr><td>1</td><td>Anna</td></tr>
        </table>
    </div>
</div>
```

## Content Rules

- Write in Italian when the surrounding course material is Italian.
- Use clear classroom phrasing: "Parto da...", "Controllo...", "Il risultato atteso...".
- Avoid long prose. The visual style depends on compact, scan-friendly content.
- Avoid emoji except those already injected by CSS pseudo-elements for warning/analogy boxes.
- Preserve technical terms with `<code>`: SQL commands, table names, attributes, types, functions.
- Use realistic tiny datasets and examples rather than abstract placeholders.
- Keep visual variation inside the established component library; do not introduce unrelated illustrations.

## Verification Checklist

- All slides are reachable with right arrow, left arrow, and space.
- `#slide-counter` displays the correct total after script initialization.
- No slide content overlaps the controls at the bottom.
- No code block or table forces horizontal body scroll.
- The palette still reads as dark slate + violet, with semantic accent colors only for meaning.
- The deck can be opened as a static `index.html` file or served from a simple local HTTP server.
