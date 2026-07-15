import importlib.util
import json
import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


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


if __name__ == "__main__":
    unittest.main()
