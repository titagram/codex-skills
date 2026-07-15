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

Only the user can approve the proposed storyboard. Do not invent a storyboard and approve it yourself. Record the user's approval as the single exact top-level Markdown line `Approval: APPROVED`; duplicates, mixed states, indentation, blockquotes, fences, and example markers invalidate it.

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
6. Resolve the next unused `animations/<topic>/vNNN/` path, starting with `v001`. Present the exact path and require the user to choose explicitly between writing there and force-overwriting a named existing output path. Stop until the user chooses; generic or storyboard approval does not count.
7. Run `python scripts/scaffold.py --project /tmp/lesson --topic concept --storyboard /tmp/approved-storyboard.md` with paths for the active project.
8. Implement the approved scene only.
9. Render a low-quality preview with `python scripts/render.py --scene animations/concept/v001/scene.py --scene-class ConceptLesson --mode preview --config animations/concept/v001/custom_config.yml --output animations/concept/v001/previews --manifest animations/concept/v001/manifest.json --execute`; inspect representative frames visually.
10. Ask the user to review the preview. Return to the storyboard if the didactic progression fails visually. Only after explicit approval, bind it to the rendered inputs with `python scripts/render.py --manifest animations/concept/v001/manifest.json --record-preview-approval APPROVED`.
11. Render the final with the same command using `--mode final` and `--output animations/concept/v001/videos`, then run `python scripts/verify.py animations/concept/v001/videos/final.mp4 --manifest animations/concept/v001/manifest.json`. Report completion only when manifest-backed verification passes.

Every executable render rereads the saved storyboard and checks its scaffold hash. Preview approval is bound to the current storyboard, scene, and config hashes; changing any of them requires a new preview and explicit approval. Render and verification attempts are recorded atomically in the manifest. Dry-run rendering (without `--execute`) remains non-mutating and does not require a manifest.

## Defaults

Prefer modular 20–90 second clips, but support continuous sequences or both. Use 16:9, dark classroom styling, large type, safe margins, semantic colors, continuous transformations, one visual focus, and explicit pauses for the teacher's voice. Do not synthesize audio.

Never overwrite lesson sources. Overwrite an existing output only when the user explicitly chooses force-overwrite for that exact path. Do not edit slides or teleprompters unless separately requested.
