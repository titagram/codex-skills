import importlib.util
import io
import json
import shlex
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
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

    def test_bootstrap_reuse_rejects_nonlocal_or_non_directory_venv(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            external = root / "external-venv"
            external.mkdir()
            cases = ("symlink", "file")
            for case in cases:
                with self.subTest(case=case):
                    project = root / case
                    project.mkdir()
                    environment = project / ".venv"
                    if case == "symlink":
                        environment.symlink_to(external, target_is_directory=True)
                    else:
                        environment.write_text("not a venv", encoding="utf-8")
                    result = subprocess.run(
                        [
                            sys.executable,
                            str(SKILL_ROOT / "scripts" / "bootstrap.py"),
                            "--project",
                            str(project),
                            "--reuse",
                        ],
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("local directory", result.stderr.lower())

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

        for name in ("doctor", "bootstrap", "render", "verify"):
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

    def test_approval_rejects_ambiguous_or_non_top_level_markers(self):
        rejected = {
            "duplicate": "Approval: APPROVED\nApproval: APPROVED\n",
            "mixed": "Approval: PENDING\nApproval: APPROVED\n",
            "indented": "    Approval: APPROVED\n",
            "blockquote": "> Approval: APPROVED\n",
            "fenced": "```markdown\nApproval: APPROVED\n```\n",
            "example plus field": (
                "Approval: APPROVED\n\nExample: `Approval: PENDING`\n"
            ),
        }
        for label, text in rejected.items():
            with self.subTest(label=label):
                self.assertFalse(self.scaffold.is_approved(text))

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
            self.assertEqual(
                manifest["storyboard_sha256"],
                self.scaffold.sha256_file(second / "storyboard.md"),
            )
            self.assertEqual(
                manifest["verification_contract"],
                {
                    "media_type": "video",
                    "width": 1920,
                    "height": 1080,
                    "frame_rate": "30/1",
                    "min_duration_seconds": 0.5,
                },
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


class RenderTests(unittest.TestCase):
    def setUp(self):
        self.render = load_script("render")
        self.scaffold = load_script("scaffold")

    @staticmethod
    def base_arguments(
        root: Path,
        mode: str = "preview",
        scene_class: str = "TriangleLesson",
    ):
        return [
            "--executable",
            "manimgl",
            "--scene",
            str(root / "scene.py"),
            "--scene-class",
            scene_class,
            "--mode",
            mode,
            "--config",
            str(root / "custom_config.yml"),
            "--output",
            str(root / {"frame": "images", "preview": "previews", "final": "videos"}[mode]),
        ]

    def create_scaffold(
        self,
        root: Path,
        topic: str = "Triangoli",
        project_name: str = "lesson",
    ):
        project = root / project_name
        project.mkdir(parents=True)
        storyboard = root / f"{project_name}-storyboard.md"
        storyboard.write_text(
            f"# {topic}\n\nApproval: APPROVED\n",
            encoding="utf-8",
        )
        output = self.scaffold.scaffold(project, topic, storyboard)
        manifest = output / "manifest.json"
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        return output, manifest, payload

    def execution_arguments(self, output, manifest, payload, mode="preview"):
        return [
            *self.base_arguments(output, mode, payload["scene_name"]),
            "--manifest",
            str(manifest),
            "--execute",
        ]

    @staticmethod
    def replace_option(arguments, option, value):
        changed = list(arguments)
        changed[changed.index(option) + 1] = str(value)
        return changed

    def assert_execution_blocked(self, arguments, expected_error):
        calls = []

        def forbidden_runner(*args, **kwargs):
            calls.append((args, kwargs))
            raise AssertionError("renderer must not run")

        stderr = io.StringIO()
        with redirect_stderr(stderr):
            result = self.render.main(arguments, runner=forbidden_runner)

        self.assertEqual(result, 1)
        self.assertIn(expected_error, stderr.getvalue().lower())
        self.assertEqual(calls, [])

    def test_render_modes_use_manimgl_not_community_cli(self):
        base = dict(
            executable="manimgl",
            scene=Path("scene.py"),
            scene_class="TriangleLesson",
            config=Path("custom_config.yml"),
        )

        frame = self.render.build_command(
            mode="frame", output=Path("images"), **base
        )
        preview = self.render.build_command(
            mode="preview", output=Path("previews"), **base
        )
        final = self.render.build_command(
            mode="final", output=Path("videos"), **base
        )

        self.assertEqual(
            frame,
            [
                "manimgl",
                "scene.py",
                "TriangleLesson",
                "-so",
                "--config_file",
                "custom_config.yml",
                "--video_dir",
                "images",
            ],
        )
        self.assertIn("-w", preview)
        self.assertIn("-l", preview)
        self.assertIn("--hd", final)
        self.assertEqual(final[0], "manimgl")
        with self.assertRaisesRegex(ValueError, "Manim Community"):
            self.render.build_command(
                executable="manim",
                mode="preview",
                output=Path("previews"),
                **{key: value for key, value in base.items() if key != "executable"},
            )

    def test_render_dry_run_prints_command_without_manifest_or_mutation(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory) / "topic with spaces"
            output = root / "previews"
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                result = self.render.main(self.base_arguments(root))

            self.assertEqual(result, 0)
            self.assertEqual(
                shlex.split(stdout.getvalue().strip()),
                self.render.build_command(
                    "manimgl",
                    root / "scene.py",
                    "TriangleLesson",
                    "preview",
                    root / "custom_config.yml",
                    output,
                ),
            )
            self.assertFalse(root.exists())

    def test_render_execute_requires_approved_manifest_and_output_choice(self):
        cases = (
            ({"approval": "PENDING"}, "approved"),
            ({"output_choice": None}, "output choice"),
            ({"render_history": None}, "scaffold"),
            ({"verification_contract": {}}, "scaffold"),
        )
        for updates, expected_error in cases:
            with self.subTest(updates=updates), tempfile.TemporaryDirectory() as temporary_directory:
                root = Path(temporary_directory)
                output, manifest, payload = self.create_scaffold(root)
                payload.update(updates)
                manifest.write_text(json.dumps(payload), encoding="utf-8")

                self.assert_execution_blocked(
                    self.execution_arguments(output, manifest, payload),
                    expected_error,
                )

    def test_render_execute_rejects_partial_scaffold_manifest(self):
        cases = (
            ("created_at", lambda payload: payload.pop("created_at")),
            (
                "source custom_config",
                lambda payload: payload["source_paths"].pop("custom_config"),
            ),
            (
                "source scene_template",
                lambda payload: payload["source_paths"].pop("scene_template"),
            ),
        )
        for label, make_partial in cases:
            with self.subTest(label=label), tempfile.TemporaryDirectory() as temporary_directory:
                root = Path(temporary_directory)
                output, manifest, payload = self.create_scaffold(root)
                make_partial(payload)
                manifest.write_text(json.dumps(payload), encoding="utf-8")

                self.assert_execution_blocked(
                    self.execution_arguments(output, manifest, payload),
                    "scaffold",
                )

    def test_render_execute_binds_to_exact_scaffold_manifest_and_paths(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            first, first_manifest, first_payload = self.create_scaffold(
                root,
                topic="Triangoli",
                project_name="first",
            )
            second, second_manifest, second_payload = self.create_scaffold(
                root,
                topic="Rettangoli",
                project_name="second",
            )
            valid = self.execution_arguments(first, first_manifest, first_payload)
            copied_manifest = root / "copied-manifest.json"
            copied_manifest.write_bytes(first_manifest.read_bytes())
            cases = (
                (
                    "copied manifest",
                    self.replace_option(valid, "--manifest", copied_manifest),
                    "manifest",
                ),
                (
                    "manifest from another scaffold",
                    self.replace_option(valid, "--manifest", second_manifest),
                    "scene",
                ),
                (
                    "foreign scene",
                    self.replace_option(valid, "--scene", second / "scene.py"),
                    "scene",
                ),
                (
                    "foreign config",
                    self.replace_option(
                        valid,
                        "--config",
                        second / "custom_config.yml",
                    ),
                    "config",
                ),
                (
                    "foreign scene class",
                    self.replace_option(
                        valid,
                        "--scene-class",
                        second_payload["scene_name"],
                    ),
                    "scene class",
                ),
                (
                    "wrong mode output",
                    self.replace_option(valid, "--output", first / "videos"),
                    "output",
                ),
            )

            for label, arguments, expected_error in cases:
                with self.subTest(label=label):
                    self.assert_execution_blocked(arguments, expected_error)

    def test_render_execute_rejects_missing_or_symlinked_scaffold_paths(self):
        cases = ("missing scene", "missing output", "symlink scene", "symlink output")
        for label in cases:
            with self.subTest(label=label), tempfile.TemporaryDirectory() as temporary_directory:
                root = Path(temporary_directory)
                output, manifest, payload = self.create_scaffold(root)
                expected_error = "scene" if "scene" in label else "output"
                external = root / "external"
                if label == "missing scene":
                    (output / "scene.py").unlink()
                elif label == "missing output":
                    (output / "previews").rmdir()
                elif label == "symlink scene":
                    external.write_text("external", encoding="utf-8")
                    (output / "scene.py").unlink()
                    (output / "scene.py").symlink_to(external)
                else:
                    external.mkdir()
                    (output / "previews").rmdir()
                    (output / "previews").symlink_to(
                        external,
                        target_is_directory=True,
                    )

                self.assert_execution_blocked(
                    self.execution_arguments(output, manifest, payload),
                    expected_error,
                )

    def test_render_final_execute_requires_explicit_preview_approval(self):
        for preview_approval in (None, "PENDING"):
            with self.subTest(preview_approval=preview_approval), tempfile.TemporaryDirectory() as temporary_directory:
                root = Path(temporary_directory)
                output, manifest, payload = self.create_scaffold(root)
                if preview_approval is not None:
                    payload["preview_approval"] = preview_approval
                manifest.write_text(json.dumps(payload), encoding="utf-8")

                self.assert_execution_blocked(
                    self.execution_arguments(
                        output,
                        manifest,
                        payload,
                        mode="final",
                    ),
                    "preview",
                )

    def test_render_rechecks_saved_storyboard_marker_and_scaffold_hash(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            output, manifest, payload = self.create_scaffold(root)
            storyboard = output / "storyboard.md"

            storyboard.write_text(
                "# Triangoli\n\nApproval: APPROVED\nApproval: PENDING\n",
                encoding="utf-8",
            )
            self.assert_execution_blocked(
                self.execution_arguments(output, manifest, payload),
                "storyboard",
            )

            storyboard.write_text(
                "# Triangoli changed\n\nApproval: APPROVED\n",
                encoding="utf-8",
            )
            self.assert_execution_blocked(
                self.execution_arguments(output, manifest, payload),
                "hash",
            )

    def test_preview_approval_is_bound_to_successful_render_content_hashes(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            output, manifest, payload = self.create_scaffold(root)
            preview = output / "previews" / "preview.mp4"

            def renderer(command, check):
                preview.write_bytes(b"preview")
                return subprocess.CompletedProcess(command, 0)

            self.assertEqual(
                self.render.main(
                    self.execution_arguments(output, manifest, payload),
                    runner=renderer,
                ),
                0,
            )
            rendered = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(rendered["preview_approval"]["status"], "PENDING")
            self.assertEqual(
                set(rendered["preview_approval"]["content_hashes"]),
                {"storyboard", "scene", "config"},
            )
            self.assertEqual(rendered["render_history"][-1]["mode"], "preview")
            self.assertEqual(rendered["render_history"][-1]["status"], "completed")

            self.assertEqual(
                self.render.main(
                    [
                        "--manifest",
                        str(manifest),
                        "--record-preview-approval",
                        "APPROVED",
                    ]
                ),
                0,
            )
            approved = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(approved["preview_approval"]["status"], "APPROVED")
            self.assertEqual(
                approved["preview_approval"]["approved_content_hashes"],
                approved["preview_approval"]["content_hashes"],
            )

            (output / "scene.py").write_text("# changed\n", encoding="utf-8")
            self.assert_execution_blocked(
                self.execution_arguments(output, manifest, approved, mode="final"),
                "changed",
            )

    def test_render_history_records_failed_render_as_failed(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            output, manifest, payload = self.create_scaffold(root)

            def failed_renderer(command, check):
                raise subprocess.CalledProcessError(7, command)

            self.assertEqual(
                self.render.main(
                    self.execution_arguments(output, manifest, payload, mode="frame"),
                    runner=failed_renderer,
                ),
                1,
            )
            updated = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(updated["render_history"][-1]["mode"], "frame")
            self.assertEqual(updated["render_history"][-1]["status"], "failed")

    def test_render_execute_reports_created_and_modified_candidates(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            scaffold, manifest, payload = self.create_scaffold(root)
            output = scaffold / "previews"
            existing = output / "existing.mp4"
            existing.write_bytes(b"before")
            created = output / "created.mp4"

            def renderer(command, check):
                self.assertTrue(check)
                existing.write_bytes(b"modified content")
                created.write_bytes(b"new content")
                return subprocess.CompletedProcess(command, 0)

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                result = self.render.main(
                    self.execution_arguments(scaffold, manifest, payload),
                    runner=renderer,
                )

            report = json.loads(stdout.getvalue())
            self.assertEqual(result, 0)
            self.assertEqual(report["exit_state"], "completed")
            self.assertEqual(report["returncode"], 0)
            self.assertEqual(
                report["candidates"], sorted([str(created), str(existing)])
            )


class VerifyTests(unittest.TestCase):
    def setUp(self):
        self.verify = load_script("verify")

    def test_verify_reports_wrong_resolution(self):
        metadata = {
            "streams": [
                {
                    "codec_type": "video",
                    "width": 854,
                    "height": 480,
                    "r_frame_rate": "30/1",
                }
            ],
            "format": {"duration": "2.0"},
        }

        errors = self.verify.validate(
            metadata,
            expected_resolution=(1920, 1080),
            min_duration=1.0,
        )

        self.assertTrue(any("resolution" in error.lower() for error in errors))

    def test_verify_validates_stream_type_duration_and_positive_frame_rate(self):
        no_video = {
            "streams": [{"codec_type": "audio", "r_frame_rate": "0/0"}],
            "format": {"duration": "0.5"},
        }
        stopped_video = {
            "streams": [
                {
                    "codec_type": "video",
                    "width": 1920,
                    "height": 1080,
                    "r_frame_rate": "0/0",
                }
            ],
            "format": {"duration": "0.5"},
        }

        no_video_errors = self.verify.validate(no_video, None, 1.0)
        stopped_errors = self.verify.validate(stopped_video, (1920, 1080), 1.0)

        self.assertTrue(any("video" in error.lower() for error in no_video_errors))
        self.assertTrue(any("duration" in error.lower() for error in stopped_errors))
        self.assertTrue(any("frame rate" in error.lower() for error in stopped_errors))

    def test_verify_requires_exact_expected_frame_rate(self):
        metadata = {
            "streams": [
                {
                    "codec_type": "video",
                    "width": 1920,
                    "height": 1080,
                    "r_frame_rate": "24/1",
                }
            ],
            "format": {"duration": "2.0"},
        }
        errors = self.verify.validate(
            metadata,
            expected_resolution=(1920, 1080),
            min_duration=0.5,
            expected_frame_rate="30/1",
        )
        self.assertTrue(any("frame rate" in error.lower() for error in errors))

    def test_verify_manifest_workflow_checks_contract_and_records_result(self):
        scaffold = load_script("scaffold")
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            project = root / "lesson"
            project.mkdir()
            storyboard = root / "storyboard.md"
            storyboard.write_text(
                "# Triangoli\n\nApproval: APPROVED\n", encoding="utf-8"
            )
            output = scaffold.scaffold(project, "Triangoli", storyboard)
            manifest = output / "manifest.json"
            artifact = output / "videos" / "final.mp4"
            artifact.write_bytes(b"video")
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["render_history"].append(
                {
                    "command": ["manimgl", "scene.py", "TriangoliLesson"],
                    "mode": "final",
                    "output": str((output / "videos").resolve()),
                    "candidates": [str(artifact.resolve())],
                    "status": "completed",
                    "returncode": 0,
                }
            )
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            metadata = {
                "streams": [
                    {
                        "codec_type": "video",
                        "width": 1920,
                        "height": 1080,
                        "r_frame_rate": "30/1",
                    }
                ],
                "format": {"duration": "2.0"},
            }
            stdout = io.StringIO()
            with mock.patch.object(self.verify, "probe", return_value=metadata):
                with redirect_stdout(stdout):
                    result = self.verify.main(
                        [str(artifact), "--manifest", str(manifest)]
                    )
            self.assertEqual(result, 0, stdout.getvalue())
            report = json.loads(stdout.getvalue())
            self.assertTrue(report["ok"])
            recorded = json.loads(manifest.read_text(encoding="utf-8"))
            verification = recorded["verification_history"][-1]
            self.assertEqual(verification["artifact"], str(artifact.resolve()))
            self.assertEqual(verification["status"], "passed")
            self.assertEqual(verification["metadata"], metadata)
            self.assertEqual(verification["observed"]["width"], 1920)
            self.assertEqual(verification["observed"]["height"], 1080)
            self.assertEqual(verification["observed"]["frame_rate"], "30/1")
            self.assertEqual(verification["observed"]["duration_seconds"], "2.0")

    def test_verify_cli_cannot_succeed_without_manifest_or_full_expectations(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            artifact = Path(temporary_directory) / "video.mp4"
            artifact.write_bytes(b"video")
            metadata = {
                "streams": [
                    {
                        "codec_type": "video",
                        "width": 1920,
                        "height": 1080,
                        "r_frame_rate": "30/1",
                    }
                ],
                "format": {"duration": "2.0"},
            }
            stdout = io.StringIO()
            with mock.patch.object(self.verify, "probe", return_value=metadata):
                with redirect_stdout(stdout):
                    result = self.verify.main([str(artifact)])
            self.assertEqual(result, 1)
            self.assertIn("manifest", stdout.getvalue().lower())

    def test_verify_rejects_weakened_contract_and_symlinked_artifact(self):
        scaffold = load_script("scaffold")
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            project = root / "lesson"
            project.mkdir()
            storyboard = root / "storyboard.md"
            storyboard.write_text(
                "# Triangoli\n\nApproval: APPROVED\n", encoding="utf-8"
            )
            output = scaffold.scaffold(project, "Triangoli", storyboard)
            manifest = output / "manifest.json"
            external = root / "external.mp4"
            external.write_bytes(b"video")
            artifact = output / "videos" / "final.mp4"
            artifact.symlink_to(external)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["render_history"].append(
                {
                    "command": ["manimgl"],
                    "mode": "final",
                    "output": str((output / "videos").resolve()),
                    "candidates": [str(artifact.absolute())],
                    "status": "completed",
                    "returncode": 0,
                }
            )
            manifest.write_text(json.dumps(payload), encoding="utf-8")

            with mock.patch.object(self.verify, "probe") as probe:
                self.assertEqual(
                    self.verify.main([str(artifact), "--manifest", str(manifest)]),
                    1,
                )
                probe.assert_not_called()

            artifact.unlink()
            artifact.write_bytes(b"video")
            payload["verification_contract"]["width"] = 1
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            with mock.patch.object(self.verify, "probe") as probe:
                self.assertEqual(
                    self.verify.main([str(artifact), "--manifest", str(manifest)]),
                    1,
                )
                probe.assert_not_called()

    def test_verify_reports_null_format_as_validation_error(self):
        metadata = {
            "streams": [
                {
                    "codec_type": "video",
                    "width": 1920,
                    "height": 1080,
                    "r_frame_rate": "30/1",
                }
            ],
            "format": None,
        }

        errors = self.verify.validate(metadata, (1920, 1080), 1.0)

        self.assertTrue(any("duration" in error.lower() for error in errors))

    def test_probe_rejects_empty_file_before_running_ffprobe(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            artifact = Path(temporary_directory) / "empty.mp4"
            artifact.touch()
            calls = []

            def forbidden_runner(*args, **kwargs):
                calls.append((args, kwargs))
                raise AssertionError("ffprobe must not run")

            with self.assertRaisesRegex(ValueError, "empty"):
                self.verify.probe(artifact, sys.executable, runner=forbidden_runner)

            self.assertEqual(calls, [])

    def test_probe_uses_exact_ffprobe_entries_and_parses_json(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            artifact = Path(temporary_directory) / "lesson.mp4"
            artifact.write_bytes(b"not empty")
            metadata = {
                "streams": [
                    {
                        "codec_type": "video",
                        "width": 1920,
                        "height": 1080,
                        "r_frame_rate": "30/1",
                    }
                ],
                "format": {"duration": "2.0"},
            }
            observed = {}

            def ffprobe_runner(command, check, capture_output, text):
                observed["command"] = command
                self.assertTrue(check)
                self.assertTrue(capture_output)
                self.assertTrue(text)
                return subprocess.CompletedProcess(
                    command,
                    0,
                    stdout=json.dumps(metadata),
                    stderr="",
                )

            result = self.verify.probe(
                artifact,
                sys.executable,
                runner=ffprobe_runner,
            )

            self.assertEqual(result, metadata)
            self.assertEqual(
                observed["command"],
                [
                    str(Path(sys.executable).resolve()),
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration",
                    "-show_entries",
                    "stream=codec_type,width,height,r_frame_rate",
                    "-of",
                    "json",
                    str(artifact),
                ],
            )

    def test_verify_cli_rejects_empty_file_with_json_evidence(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            scaffold = load_script("scaffold")
            project = root / "lesson"
            project.mkdir()
            storyboard = root / "storyboard.md"
            storyboard.write_text(
                "# Empty\n\nApproval: APPROVED\n", encoding="utf-8"
            )
            output = scaffold.scaffold(project, "Empty", storyboard)
            manifest = output / "manifest.json"
            artifact = output / "videos" / "empty.mp4"
            artifact.touch()
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["render_history"].append(
                {
                    "command": ["manimgl"],
                    "mode": "final",
                    "output": str((output / "videos").resolve()),
                    "candidates": [str(artifact.resolve())],
                    "status": "completed",
                    "returncode": 0,
                }
            )
            manifest.write_text(json.dumps(payload), encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(SKILL_ROOT / "scripts" / "verify.py"),
                    str(artifact),
                    "--manifest",
                    str(manifest),
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            report = json.loads(result.stdout)
            self.assertEqual(result.returncode, 1)
            self.assertFalse(report["ok"])
            self.assertIsNone(report["metadata"])
            self.assertTrue(any("empty" in error.lower() for error in report["errors"]))


if __name__ == "__main__":
    unittest.main()
