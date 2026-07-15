from manimlib import *

BACKGROUND = "#0B1020"
KNOWN = BLUE_C
ACTIVE = YELLOW_C
RESULT = GREEN_C
ERROR = RED_C


class TemplateLesson(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BACKGROUND))
        title = Text("{{TITLE}}", font="Arial", font_size=54)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(1)
