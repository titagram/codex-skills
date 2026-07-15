# Didactic workflow

## Context questions

Ask only for missing context, then confirm the answers before proposing scenes:

- Who are the learners, and what can they already do?
- What single understanding or ability should they gain?
- Which motivating problem makes the concept necessary?
- Which conceptual steps, representations, and examples form the shortest sound path?
- Which misconception should the animation expose or prevent?
- How should the teacher pace the explanation, pauses, and transitions?

## Progression rubric

Check the proposed progression against every criterion:

| Criterion | Pass condition |
|---|---|
| Motivation | Begin from a question or problem the learner can recognize. |
| Prerequisites | Introduce no unexplained notation, object, or operation. |
| Conceptual steps | Make each transformation follow visibly from the previous state. |
| Representation | Use position, motion, color, labels, and formulas consistently. |
| Cognitive load | Keep one visual focus and remove decorative competition. |
| Misconception | Show the likely wrong interpretation and the visual evidence that corrects it. |
| Understanding | End with a check that requires applying the idea, not repeating a slogan. |

Revise any scene that does not pass before asking for approval.

## Storyboard contract

Save the storyboard as Markdown with all of these fields:

- `Approval: PENDING|APPROVED`
- Audience and prerequisites
- One learning objective
- Motivating question
- One likely misconception
- Source links when lesson materials exist
- A scene table with didactic purpose, visuals and transformations, text/formulas, voice pause, and duration
- A final understanding check

Keep `Approval: PENDING` while proposing or revising the storyboard. Change it to `Approval: APPROVED` only after the user explicitly approves that concrete storyboard. Approval applies only to the described storyboard; obtain reapproval for material changes to its objective, progression, examples, representations, or timing.

## Clip sizing

Prefer one 20–90 second clip per conceptual move. Split a sequence when its objective, representation, or understanding check changes. Use a continuous animation when continuity itself teaches the relationship. Offer both modular clips and a continuous sequence when the lesson needs flexible classroom pacing.

## Preview review

Render a final frame or low-quality preview first. Inspect representative frames for legibility, safe margins, continuity, semantic color, visual focus, and sufficient voice pauses. Ask the user to review the preview against the approved learning objective. If the visual progression changes the teaching logic or obscures it, return to `Approval: PENDING`, revise the storyboard, and obtain reapproval before continuing.
