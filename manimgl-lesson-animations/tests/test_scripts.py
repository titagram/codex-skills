import importlib.util
import json
import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SKILL_ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str):
    path = SKILL_ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"manimgl_{name}", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ScriptTests(unittest.TestCase):
    def setUp(self):
        self.doctor = load_script("doctor")
        self.bootstrap = load_script("bootstrap")

    def test_doctor_marks_missing_renderer_as_blocker(self):
        checks = self.doctor.collect_checks(
            which=lambda name: "/bin/" + name if name in {"ffmpeg", "ffprobe"} else None,
            find_spec=lambda name: None,
            version=(3, 13, 0),
        )
        self.assertEqual(self.doctor.exit_code(checks), 1)
        self.assertIn("manimgl", {c.name for c in checks if c.status == "BLOCKER"})

    def test_bootstrap_is_project_local_and_dry_run_friendly(self):
        commands = self.bootstrap.build_commands(
            Path("/tmp/lesson"), "/opt/homebrew/bin/python3.13", "manimgl"
        )
        self.assertEqual(
            commands[0],
            [
                "/opt/homebrew/bin/python3.13",
                "-m",
                "venv",
                "/tmp/lesson/.venv",
            ],
        )
        self.assertIn("/tmp/lesson/.venv", commands[0][-1])
        self.assertEqual(commands[1][-3:], ["install", "--upgrade", "pip"])
        self.assertEqual(commands[2][-2:], ["install", "manimgl"])

    def test_doctor_classifies_required_and_optional_dependencies(self):
        available_commands = {"manim-render"}
        checks = self.doctor.collect_checks(
            which=lambda name: f"/bin/{name}" if name in available_commands else None,
            find_spec=lambda name: object() if name == "manimlib" else None,
            version=(3, 8, 19),
        )
        by_name = {check.name: check for check in checks}

        self.assertEqual(by_name["python"].status, "BLOCKER")
        self.assertEqual(by_name["manimlib"].status, "OK")
        self.assertEqual(by_name["manimgl"].status, "OK")
        self.assertEqual(by_name["ffmpeg"].status, "BLOCKER")
        self.assertEqual(by_name["ffprobe"].status, "BLOCKER")
        self.assertEqual(by_name["latex"].status, "WARNING")
        self.assertEqual(by_name["moderngl"].status, "WARNING")

    def test_doctor_accepts_a_complete_environment(self):
        checks = self.doctor.collect_checks(
            which=lambda name: f"/bin/{name}",
            find_spec=lambda name: object(),
            version=(3, 9, 0),
        )

        self.assertEqual(
            {check.name for check in checks},
            {"python", "manimlib", "manimgl", "ffmpeg", "ffprobe", "latex", "moderngl"},
        )
        self.assertEqual(self.doctor.exit_code(checks), 0)

    def test_doctor_json_cli_emits_all_checks(self):
        result = subprocess.run(
            [sys.executable, str(SKILL_ROOT / "scripts" / "doctor.py"), "--json"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertIn(result.returncode, {0, 1})
        payload = json.loads(result.stdout)
        self.assertEqual(
            {item["name"] for item in payload},
            {"python", "manimlib", "manimgl", "ffmpeg", "ffprobe", "latex", "moderngl"},
        )

    def test_bootstrap_execute_stops_after_a_failed_command(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            marker = Path(temporary_directory) / "should-not-exist"
            commands = [
                [sys.executable, "-c", "pass"],
                [sys.executable, "-c", "raise SystemExit(7)"],
                [
                    sys.executable,
                    "-c",
                    f"from pathlib import Path; Path({str(marker)!r}).touch()",
                ],
            ]

            with self.assertRaises(subprocess.CalledProcessError):
                self.bootstrap.execute(commands)
            self.assertFalse(marker.exists())

    def test_bootstrap_cli_prints_quoted_commands_without_creating_venv(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory) / "lesson with spaces"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SKILL_ROOT / "scripts" / "bootstrap.py"),
                    "--project",
                    str(project),
                    "--spec",
                    "manimgl==1.7.2",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(len(result.stdout.splitlines()), 3)
            self.assertEqual(
                [shlex.split(line) for line in result.stdout.splitlines()],
                self.bootstrap.build_commands(project, sys.executable, "manimgl==1.7.2"),
            )
            self.assertFalse((project / ".venv").exists())

    def test_bootstrap_cli_requires_reuse_for_existing_venv(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory)
            venv = project / ".venv"
            venv.mkdir()
            marker = venv / "keep"
            marker.write_text("unchanged", encoding="utf-8")
            command = [
                sys.executable,
                str(SKILL_ROOT / "scripts" / "bootstrap.py"),
                "--project",
                str(project),
            ]

            rejected = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
            )
            reused = subprocess.run(
                [*command, "--reuse"],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("--reuse", rejected.stderr)
            self.assertEqual(reused.returncode, 0, reused.stderr)
            self.assertEqual(marker.read_text(encoding="utf-8"), "unchanged")

    def test_scripts_start_under_python_3_9(self):
        candidates = [Path("/usr/bin/python3"), Path(sys.executable)]
        python = next(
            (
                candidate
                for candidate in candidates
                if candidate.exists()
                and subprocess.run(
                    [
                        str(candidate),
                        "-c",
                        "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')",
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip()
                == "3.9"
            ),
            None,
        )
        if python is None:
            self.skipTest("Python 3.9 interpreter is not available")

        for name in ("doctor", "bootstrap"):
            result = subprocess.run(
                [str(python), str(SKILL_ROOT / "scripts" / f"{name}.py"), "--help"],
                check=False,
                capture_output=True,
                text=True,
            )
            with self.subTest(name=name):
                self.assertEqual(result.returncode, 0, result.stderr)


class ScaffoldTests(unittest.TestCase):
    def setUp(self):
        self.scaffold = load_script("scaffold")

    @staticmethod
    def write_storyboard(directory: Path, approval: str = "APPROVED") -> Path:
        storyboard = directory / "storyboard.md"
        storyboard.write_text(
            f"# Triangoli\n\nApproval: {approval}\n",
            encoding="utf-8",
        )
        return storyboard

    def test_scaffold_rejects_pending_storyboard_without_writing(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            project = root / "lesson"
            project.mkdir()
            storyboard = self.write_storyboard(root, "PENDING")

            with self.assertRaisesRegex(ValueError, "explicitly approved"):
                self.scaffold.scaffold(project, "Somma angoli", storyboard)

            self.assertFalse((project / "animations").exists())

    def test_approval_requires_a_standalone_approved_line(self):
        self.assertTrue(
            self.scaffold.is_approved("# Storyboard\n\nApproval: APPROVED\n")
        )
        self.assertFalse(
            self.scaffold.is_approved("# Storyboard\n\nNote: Approval: APPROVED\n")
        )
        self.assertFalse(
            self.scaffold.is_approved("# Storyboard\n\nApproval: APPROVED later\n")
        )

    def test_scaffold_creates_successive_versioned_outputs(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            project = root / "lesson"
            project.mkdir()
            storyboard = self.write_storyboard(root)

            first = self.scaffold.scaffold(project, "Somma angoli", storyboard)
            marker = first / "keep-from-v001"
            marker.write_text("unchanged", encoding="utf-8")
            second = self.scaffold.scaffold(project, "Somma angoli", storyboard)

            self.assertEqual(first, project / "animations" / "somma-angoli" / "v001")
            self.assertEqual(second, project / "animations" / "somma-angoli" / "v002")
            self.assertEqual(marker.read_text(encoding="utf-8"), "unchanged")
            self.assertEqual(
                {child.name for child in second.iterdir()},
                {
                    "storyboard.md",
                    "scene.py",
                    "custom_config.yml",
                    "manifest.json",
                    "previews",
                    "images",
                    "videos",
                },
            )

            manifest = json.loads(
                (second / "manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["approval"], "APPROVED")
            self.assertEqual(manifest["scene_name"], "SommaAngoliLesson")
            self.assertEqual(manifest["output_choice"], "new-version")
            self.assertEqual(manifest["output_path"], str(second.resolve()))
            self.assertEqual(
                manifest["source_paths"]["storyboard"], str(storyboard.resolve())
            )
            self.assertEqual(manifest["render_history"], [])

    def test_force_overwrite_requires_explicit_choice_and_exact_path(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            project = root / "lesson"
            project.mkdir()
            storyboard = self.write_storyboard(root)
            first = self.scaffold.scaffold(project, "Somma angoli", storyboard)
            marker = first / "old-output"
            marker.write_text("replace me", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "exact output path"):
                self.scaffold.scaffold(project, "Somma angoli", storyboard, force=True)
            with self.assertRaisesRegex(ValueError, "force-overwrite"):
                self.scaffold.scaffold(
                    project,
                    "Somma angoli",
                    storyboard,
                    output_path=first,
                )

            overwritten = self.scaffold.scaffold(
                project,
                "Somma angoli",
                storyboard,
                force=True,
                output_path=first,
            )

            self.assertEqual(overwritten, first)
            self.assertFalse(marker.exists())
            manifest = json.loads((first / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["output_choice"], "force-overwrite")
            self.assertEqual(manifest["output_path"], str(first.resolve()))

    def test_force_overwrite_cannot_target_lesson_sources(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            project = root / "lesson"
            project.mkdir()
            storyboard = self.write_storyboard(root)
            lesson_source = project / "teleprompter"
            lesson_source.mkdir()
            source_marker = lesson_source / "lesson.txt"
            source_marker.write_text("do not change", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "versioned animations"):
                self.scaffold.scaffold(
                    project,
                    "Somma angoli",
                    storyboard,
                    force=True,
                    output_path=lesson_source,
                )

            self.assertEqual(source_marker.read_text(encoding="utf-8"), "do not change")

    def test_force_overwrite_rejects_symlinked_animations_root(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            project = root / "lesson"
            project.mkdir()
            storyboard = self.write_storyboard(root)
            lesson_source = project / "teleprompter" / "somma-angoli" / "v001"
            lesson_source.mkdir(parents=True)
            source_marker = lesson_source / "lesson.txt"
            source_marker.write_text("do not change", encoding="utf-8")
            (project / "animations").symlink_to(
                project / "teleprompter",
                target_is_directory=True,
            )

            with self.assertRaisesRegex(ValueError, "symlinked"):
                self.scaffold.scaffold(
                    project,
                    "Somma angoli",
                    storyboard,
                    force=True,
                    output_path=project
                    / "animations"
                    / "somma-angoli"
                    / "v001",
                )

            self.assertEqual(source_marker.read_text(encoding="utf-8"), "do not change")

    def test_template_contract_failures_leave_no_partial_output(self):
        cases = {
            "missing class sentinel": (
                'class OtherLesson(Scene):\n    title = Text("{{TITLE}}")\n'
            ),
            "duplicate class sentinel": (
                'class TemplateLesson(Scene):\n    title = Text("{{TITLE}}")\n'
                "TemplateLesson = None\n"
            ),
            "missing title sentinel": (
                'class TemplateLesson(Scene):\n    title = Text("Fixed")\n'
            ),
            "duplicate title sentinel": (
                'class TemplateLesson(Scene):\n    title = Text("{{TITLE}}")\n'
                'OTHER = "{{TITLE}}"\n'
            ),
            "generated scene does not compile": (
                'class TemplateLesson(Scene):\n    title = Text("{{TITLE}}"\n'
            ),
        }

        for label, template in cases.items():
            with self.subTest(
                label=label
            ), tempfile.TemporaryDirectory() as temporary_directory:
                root = Path(temporary_directory)
                project = root / "lesson"
                project.mkdir()
                storyboard = self.write_storyboard(root)
                assets = root / "assets"
                assets.mkdir()
                (assets / "scene-template.py").write_text(template, encoding="utf-8")
                (assets / "custom_config.yml").write_text(
                    "camera: {}\n", encoding="utf-8"
                )

                with mock.patch.object(self.scaffold, "ASSETS_ROOT", assets):
                    with self.assertRaisesRegex(ValueError, "scene template"):
                        self.scaffold.scaffold(project, "Somma angoli", storyboard)

                self.assertFalse((project / "animations").exists())

    def test_template_contract_counts_code_sentinels_not_comment_mentions(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            project = root / "lesson"
            project.mkdir()
            storyboard = self.write_storyboard(root)
            assets = root / "assets"
            assets.mkdir()
            (assets / "scene-template.py").write_text(
                "# TemplateLesson and the quoted token \"{{TITLE}}\" "
                "are documented here.\n"
                "class TemplateLesson(Scene):\n"
                '    title = Text("{{TITLE}}")\n',
                encoding="utf-8",
            )
            (assets / "custom_config.yml").write_text("camera: {}\n", encoding="utf-8")

            with mock.patch.object(self.scaffold, "ASSETS_ROOT", assets):
                output = self.scaffold.scaffold(project, "Somma angoli", storyboard)

            scene = (output / "scene.py").read_text(encoding="utf-8")
            self.assertIn("# TemplateLesson", scene)
            self.assertIn("class SommaAngoliLesson", scene)
            self.assertIn("Text('Somma angoli')", scene)

    def test_generated_class_name_is_a_valid_identifier(self):
        generated = self.scaffold.class_name("3 proprietà dell'angolo")

        self.assertEqual(generated, "Topic3ProprietaDellAngoloLesson")
        self.assertTrue(generated.isidentifier())
        with self.assertRaisesRegex(ValueError, "class name"):
            self.scaffold.class_name("💥")


if __name__ == "__main__":
    unittest.main()
