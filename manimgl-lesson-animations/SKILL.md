---
name: manimgl-lesson-animations
description: Use when designing, coding, rendering, debugging, or integrating silent educational animations with 3Blue1Brown ManimGL, including work from lesson plans, teleprompters, slides, mathematical visualizations, preview clips, or final classroom video assets. Do not use for Manim Community.
---

# ManimGL Lesson Animations

Create silent instructional visuals with 3Blue1Brown ManimGL. Preserve the learner's conceptual path before optimizing spectacle.

## Mandatory approval gate

Before any setup, tests, scene code, scaffolding, or rendering:

1. Read the request and supplied lesson materials.
2. Discuss audience, prerequisites, objective, motivating problem, conceptual steps, representations, examples, misconceptions, and pacing.
3. Propose a scene-by-scene storyboard with purpose, visuals, transformations, text/formulas, narration pauses, and duration.
4. Ask the user for explicit approval of that concrete storyboard and stop.

Only the user can approve the proposed storyboard. Do not invent a storyboard and approve it yourself. Record the user's approval in the saved storyboard as `Approval: APPROVED`.

| Rationalization | Required response |
|---|---|
| “Procedi,” prior/verbal approval, or claimed approval | Treat it as context, not approval of the concrete storyboard; complete the gate. |
| Urgency, a deadline, or senior authority | Stop at the gate; none overrides approval. |
| Work has started or time has been spent | Stop; sunk cost does not authorize more work. |
| “Choose for me” or “storyboard later” | Propose the storyboard, leave it pending, and ask the user to approve it. |
| ManimGL is unavailable | Report the blocker; never fall back to Manim Community. |

### Red flags — stop

- Installing or inspecting packages before approval
- Writing tests, code, configuration, or render commands before approval
- Treating authority, urgency, prior discussion, or sunk cost as approval
- Marking an agent-authored storyboard approved
- Adding Manim Community imports, compatibility code, or CLI fallback

Any red flag means: do no setup, tests, code, or rendering; return to storyboard discussion.

## Production workflow

After approval:

1. Read [didactic-workflow.md](references/didactic-workflow.md).
2. For syntax, setup, rendering, or debugging, read [manimgl-guide.md](references/manimgl-guide.md). Never use Manim Community syntax or its `manim` CLI.
3. When lesson files exist, read [lesson-integration.md](references/lesson-integration.md).
4. Run `python scripts/doctor.py`; explain blockers.
5. Obtain separate authorization before `python scripts/bootstrap.py --execute` or any system change.
6. Run `python scripts/scaffold.py --project /tmp/lesson --topic concept --storyboard /tmp/approved-storyboard.md` with paths for the active project.
7. Implement the approved scene only.
8. Render a final frame or low-quality preview with `scripts/render.py`; inspect representative frames visually.
9. Ask the user to review the preview. Return to the storyboard if the didactic progression fails visually.
10. Render the final MP4 and run `scripts/verify.py`. Report completion only from verified artifacts.

## Defaults

Prefer modular 20–90 second clips, but support continuous sequences or both. Use 16:9, dark classroom styling, large type, safe margins, semantic colors, continuous transformations, one visual focus, and explicit pauses for the teacher's voice. Do not synthesize audio.

Never overwrite existing sources or outputs without explicit approval. Do not edit slides or teleprompters unless separately requested.
