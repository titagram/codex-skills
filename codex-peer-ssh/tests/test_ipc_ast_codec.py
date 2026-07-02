import importlib.util
import json
import pathlib
import unittest


SKILL_DIR = pathlib.Path(__file__).resolve().parents[1]
CODEC_PATH = SKILL_DIR / "scripts" / "ipc_ast_codec.py"


def load_codec():
    spec = importlib.util.spec_from_file_location("ipc_ast_codec", CODEC_PATH)
    module = importlib.util.module_from_spec(spec)
    if spec.loader is None:
        raise RuntimeError(f"Unable to load codec from {CODEC_PATH}")
    spec.loader.exec_module(module)
    return module


class IpcAstCodecTests(unittest.TestCase):
    def setUp(self):
        self.codec = load_codec()

    def test_valid_ask_frame_canonicalizes_to_compact_json(self):
        source = 'A(7,6,[F("f1",20,45,"91be22aa")],Q("why","test_fail","cmd0"),M(want="diagnosis",budget=500))'

        canonical = self.codec.canonical_json(source)

        self.assertEqual(
            canonical,
            '["A",7,6,[["F","f1",20,45,"91be22aa"]],["why","test_fail","cmd0"],{"want":"diagnosis","budget":500}]',
        )

    def test_meta_can_be_a_dict(self):
        source = 'S(2,1,[],{"phase":"bootstrap"},{"ok":True,"note":None})'

        frame = self.codec.parse_frame(source)

        self.assertEqual(frame, ["S", 2, 1, [], {"phase": "bootstrap"}, {"ok": True, "note": None}])

    def test_role_and_art_nested_calls_are_canonicalized(self):
        source = 'H(1,0,[ART("boot","abc123")],ROLE(side="local",mode="human-facing"),M(codec="ipc-ast-v1"))'

        frame = self.codec.parse_frame(source)

        self.assertEqual(
            frame,
            [
                "H",
                1,
                0,
                [["ART", "boot", "abc123"]],
                {"side": "local", "mode": "human-facing"},
                {"codec": "ipc-ast-v1"},
            ],
        )

    def test_value_call_supports_varargs(self):
        source = 'K(3,2,[],V("max_len",4096,"max_depth",20),M(ok=True))'

        frame = self.codec.parse_frame(source)

        self.assertEqual(frame, ["K", 3, 2, [], ["max_len", 4096, "max_depth", 20], {"ok": True}])

    def test_invalid_input_returns_deterministic_error_object(self):
        result = self.codec.parse_or_error('A(1,0,[],x[0],M())')

        self.assertEqual(result["ok"], False)
        self.assertEqual(result["error"]["code"], "disallowed_node")
        self.assertIn("Subscript", result["error"]["message"])

    def test_parse_or_error_handles_actual_surrogate_source_deterministically(self):
        source = 'A(1,0,[],Q("' + chr(0xD800) + '"),M())'

        result = self.codec.parse_or_error(source)

        self.assertEqual(result["ok"], False)
        self.assertEqual(result["error"]["code"], "bad_unicode")

    def test_rejects_escaped_surrogate_literal(self):
        with self.assertRaisesRegex(self.codec.IpcAstCodecError, "surrogate"):
            self.codec.parse_frame('A(1,0,[],Q("\\ud800"),M())')

    def test_rejects_duplicate_dict_keys(self):
        with self.assertRaisesRegex(self.codec.IpcAstCodecError, "duplicate dict key"):
            self.codec.parse_frame('A(1,0,[],{"a":1,"a":2},M())')

    def test_duplicate_keywords_are_deterministic_errors(self):
        result = self.codec.parse_or_error("A(1,0,[],Q(),M(a=1,a=2))")

        self.assertEqual(result["ok"], False)
        self.assertEqual(result["error"]["code"], "duplicate_keyword")

    def test_make_nack_returns_canonical_n_frame(self):
        nack = self.codec.make_nack(seq=4, ack=9, code="bad_frame", message="invalid syntax")

        self.assertEqual(nack, '["N",4,9,[],["bad_frame","invalid syntax"],{}]')
        self.assertEqual(json.loads(nack), ["N", 4, 9, [], ["bad_frame", "invalid syntax"], {}])

    def test_rejects_attribute_calls(self):
        with self.assertRaisesRegex(self.codec.IpcAstCodecError, "Attribute"):
            self.codec.parse_frame('__import__("os").system("rm -rf /")')

    def test_rejects_unknown_top_level_call(self):
        with self.assertRaisesRegex(self.codec.IpcAstCodecError, "unknown top-level op"):
            self.codec.parse_frame("BAD(1,0,[],Q(),M())")

    def test_rejects_wrong_top_level_arity(self):
        with self.assertRaisesRegex(self.codec.IpcAstCodecError, "top-level frame requires exactly five arguments"):
            self.codec.parse_frame("A(1,0,[],Q())")

    def test_rejects_non_integer_sequence(self):
        with self.assertRaisesRegex(self.codec.IpcAstCodecError, "seq must be a non-negative integer"):
            self.codec.parse_frame("A(True,0,[],Q(),M())")

    def test_rejects_non_integer_ack(self):
        with self.assertRaisesRegex(self.codec.IpcAstCodecError, "ack must be a non-negative integer"):
            self.codec.parse_frame("A(1,True,[],Q(),M())")

    def test_rejects_meta_that_is_not_dict_like(self):
        with self.assertRaisesRegex(self.codec.IpcAstCodecError, "meta must canonicalize to a dict"):
            self.codec.parse_frame("A(1,0,[],Q(),V(1))")

    def test_rejects_attribute_payload(self):
        with self.assertRaisesRegex(self.codec.IpcAstCodecError, "Attribute"):
            self.codec.parse_frame("A(1,0,[],foo.bar,M())")

    def test_rejects_subscript_payload(self):
        with self.assertRaisesRegex(self.codec.IpcAstCodecError, "Subscript"):
            self.codec.parse_frame("A(1,0,[],foo[0],M())")

    def test_rejects_lambda_payload(self):
        with self.assertRaisesRegex(self.codec.IpcAstCodecError, "Lambda"):
            self.codec.parse_frame("A(1,0,[],lambda: 1,M())")

    def test_rejects_comprehension_payload(self):
        with self.assertRaisesRegex(self.codec.IpcAstCodecError, "ListComp"):
            self.codec.parse_frame("A(1,0,[],[x for x in y],M())")

    def test_rejects_binary_operator_payload(self):
        with self.assertRaisesRegex(self.codec.IpcAstCodecError, "BinOp"):
            self.codec.parse_frame("A(1,0,[],1+2,M())")

    def test_rejects_boolean_operator_payload(self):
        with self.assertRaisesRegex(self.codec.IpcAstCodecError, "BoolOp"):
            self.codec.parse_frame("A(1,0,[],True or False,M())")

    def test_rejects_comparison_payload(self):
        with self.assertRaisesRegex(self.codec.IpcAstCodecError, "Compare"):
            self.codec.parse_frame("A(1,0,[],1 < 2,M())")

    def test_rejects_f_string_payload(self):
        with self.assertRaisesRegex(self.codec.IpcAstCodecError, "JoinedStr"):
            self.codec.parse_frame('A(1,0,[],f"{1}",M())')

    def test_rejects_starred_args(self):
        with self.assertRaisesRegex(self.codec.IpcAstCodecError, "Starred"):
            self.codec.parse_frame("A(1,0,[],Q(*[1]),M())")

    def test_rejects_keyword_unpacking(self):
        with self.assertRaisesRegex(self.codec.IpcAstCodecError, "keyword unpacking is not allowed"):
            self.codec.parse_frame('A(1,0,[],Q(),M(**{"want":"diagnosis"}))')

    def test_rejects_unknown_nested_call(self):
        with self.assertRaisesRegex(self.codec.IpcAstCodecError, "unknown nested call"):
            self.codec.parse_frame("A(1,0,[],X(1),M())")

    def test_rejects_too_long_input(self):
        with self.assertRaisesRegex(self.codec.IpcAstCodecError, "exceeds max length"):
            self.codec.parse_frame("A(" + "1" * 5000 + ",0,[],Q(),M())", max_length=128)

    def test_rejects_too_long_multiline_input_by_total_length(self):
        source = "A(\n1,\n0,\n[],\nQ(),\nM()\n)"

        with self.assertRaisesRegex(self.codec.IpcAstCodecError, "exceeds max length"):
            self.codec.parse_frame(source, max_length=8)

    def test_rejects_excessive_depth(self):
        source = "A(1,0,[]," + ("[" * 25) + "1" + ("]" * 25) + ",M())"

        with self.assertRaisesRegex(self.codec.IpcAstCodecError, "AST exceeds max depth"):
            self.codec.parse_frame(source, max_depth=10)

    def test_rejects_excessive_node_count(self):
        source = "A(1,0,[]," + "[" + ",".join(["1"] * 100) + "]" + ",M())"

        with self.assertRaisesRegex(self.codec.IpcAstCodecError, "AST exceeds max node count"):
            self.codec.parse_frame(source, max_nodes=40)


if __name__ == "__main__":
    unittest.main()
