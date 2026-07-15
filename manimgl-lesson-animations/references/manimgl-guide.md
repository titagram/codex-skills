# ManimGL guide

Use only 3Blue1Brown ManimGL:

- repository: https://github.com/3b1b/manim
- documentation: https://3b1b.github.io/manim/
- package: `manimgl`
- import: `from manimlib import *`
- CLI: `manimgl scene.py SceneName -w -l` or `manim-render scene.py SceneName -w -l`

Never use Manim Community imports (`from manim import *`) or its `manim` CLI.

## Render modes

| Purpose | Flags |
|---|---|
| Final frame | `-so` |
| Fast preview | `-w -l` |
| Full HD final | `-w --hd --fps 30` |

Use `--config_file` for the topic configuration and `--video_dir` for explicit output directories.

## Manifest-backed commands

After scaffolding, execute a preview with exact scaffold paths (substitute the topic, version, and scene class):

```sh
python scripts/render.py --scene animations/concept/v001/scene.py --scene-class ConceptLesson --mode preview --config animations/concept/v001/custom_config.yml --output animations/concept/v001/previews --manifest animations/concept/v001/manifest.json --execute
```

After the user explicitly approves that preview, record the approval:

```sh
python scripts/render.py --manifest animations/concept/v001/manifest.json --record-preview-approval APPROVED
```

Then render and verify the final artifact:

```sh
python scripts/render.py --scene animations/concept/v001/scene.py --scene-class ConceptLesson --mode final --config animations/concept/v001/custom_config.yml --output animations/concept/v001/videos --manifest animations/concept/v001/manifest.json --execute
python scripts/verify.py animations/concept/v001/videos/final.mp4 --manifest animations/concept/v001/manifest.json
```

The final contract requires a video stream, 1920x1080 resolution, exactly 30 fps, and at least 0.5 seconds duration. `verify.py` accepts only a canonical artifact recorded as a successful final candidate and writes the observed duration, resolution, frame rate, media type, and result back to the manifest.

## Minimal scene

```python
from manimlib import *

class ConceptPreview(Scene):
    def construct(self):
        title = Text("Concetto", font_size=54)
        self.play(Write(title))
        self.wait()
```

## Scaffold template contract

Keep `assets/scene-template.py` valid Python before scaffolding. Require exactly one `TemplateLesson` identifier in the template and replace it with a validated, non-keyword Python class identifier. Require exactly one quoted title token, `"{{TITLE}}"`, and replace that entire literal with `repr(title)`. Fail instead of writing a partial scaffold when either sentinel is missing or duplicated, then compile the generated scene.

## Failure classes

- Environment: missing interpreter, `manimgl`, `manimlib`, FFmpeg/FFprobe.
- LaTeX: use `Text` when formulas are unnecessary; install LaTeX only after approval when `Tex` is required.
- OpenGL/windowing: run the diagnostic under the same interpreter and environment as the renderer.
- API/import: compare against current 3b1b examples, not Community Edition answers.
- Scene execution: preserve the traceback and isolate the first failing object/animation.
- FFmpeg/artifacts: verify the generated file with FFprobe; do not trust exit status alone.
