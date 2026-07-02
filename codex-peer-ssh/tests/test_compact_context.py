import importlib.util
import json
import pathlib
import tempfile
import unittest


SKILL_DIR = pathlib.Path(__file__).resolve().parents[1]
COMPACT_CONTEXT_PATH = SKILL_DIR / "scripts" / "compact_context.py"


def load_compact_context():
    spec = importlib.util.spec_from_file_location("compact_context", COMPACT_CONTEXT_PATH)
    module = importlib.util.module_from_spec(spec)
    if spec.loader is None:
        raise RuntimeError(f"Unable to load compact context helper from {COMPACT_CONTEXT_PATH}")
    spec.loader.exec_module(module)
    return module


class CompactContextTests(unittest.TestCase):
    def setUp(self):
        self.helper = load_compact_context()

    def test_builds_bounded_context_from_structured_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            session_dir = pathlib.Path(tmp)
            (session_dir / "session.json").write_text(
                json.dumps(
                    {
                        "session_id": "s1",
                        "ssh_target": "u@h",
                        "remote_workspace": "/repo",
                        "runtime_provider": "tmux",
                        "runtime_session": "codex-peer-s1",
                        "ignored": "large-value",
                    }
                ),
                encoding="utf-8",
            )
            (session_dir / "machine.jsonl").write_text(
                "\n".join(
                    [
                        '["H",1,0,[],{"side":"local"},{"codec":"ipc-ast-v1"}]',
                        '["C",2,1,[],["contract"],{"workspace":"/repo"}]',
                        '["K",3,2,[],["max_len",4096],{"dict":true}]',
                        '["D",4,3,[],{"f1":"a.py"},{"scope":"session"}]',
                        '["D",5,4,[],{"f2":"b.py"},{"scope":"session"}]',
                        '["S",6,5,[],["checkpoint","inventory"],{"phase":"scan"}]',
                        '["A",7,6,[],["old_task"],{}]',
                        '["R",8,7,[],["old_result"],{}]',
                    ]
                ),
                encoding="utf-8",
            )
            (session_dir / "journal.md").write_text("a" * 40 + "\nlatest note", encoding="utf-8")

            text = self.helper.build_context(
                session_dir,
                task_frame='A(9,8,[F("f1",1,20,"abc")],Q("review"),M(budget=100))',
                max_dict_frames=1,
                max_checkpoints=1,
                max_journal_chars=12,
            )

            payload = json.loads(text)
            self.assertEqual(payload["mode"], "compact-resume-v1")
            self.assertEqual(payload["session"]["session_id"], "s1")
            self.assertNotIn("ignored", payload["session"])
            self.assertEqual(payload["dictionary"], [["D", 5, 4, [], {"f2": "b.py"}, {"scope": "session"}]])
            self.assertEqual(payload["checkpoints"], [["S", 6, 5, [], ["checkpoint", "inventory"], {"phase": "scan"}]])
            self.assertEqual(payload["task"], ["A", 9, 8, [["F", "f1", 1, 20, "abc"]], ["review"], {"budget": 100}])
            self.assertTrue(payload["journal_tail"].endswith("latest note"))
            self.assertNotIn("old_task", text)
            self.assertNotIn("old_result", text)

    def test_invalid_task_frame_raises_codec_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(Exception, "unknown top-level op"):
                self.helper.build_context(pathlib.Path(tmp), task_frame="BAD(1,0,[],Q(),M())")


if __name__ == "__main__":
    unittest.main()
