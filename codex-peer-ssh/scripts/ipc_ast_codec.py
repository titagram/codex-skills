#!/usr/bin/env python3
"""AST-backed codec for the codex-peer-ssh IPC frame syntax."""

from __future__ import annotations

import ast
import json
import sys
from typing import Any


TOP_LEVEL_OPS = frozenset("HCKDSARPNZ")
NESTED_CALLS = frozenset({"F", "ART", "Q", "M", "V", "ROLE"})
ALLOWED_NODE_TYPES = (
    ast.Expression,
    ast.Call,
    ast.Name,
    ast.Load,
    ast.Constant,
    ast.List,
    ast.Dict,
    ast.keyword,
)


class IpcAstCodecError(ValueError):
    """Deterministic validation error for invalid IPC AST frames."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def _error(code: str, message: str) -> IpcAstCodecError:
    return IpcAstCodecError(code, message)


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def parse_frame(source, *, max_length=4096, max_depth=32, max_nodes=512) -> list:
    """Parse one IPC AST frame and return its canonical list form."""

    if not isinstance(source, str):
        raise _error("invalid_type", "source must be a string")
    if len(source) > max_length:
        raise _error("source_too_long", "source exceeds max length")

    try:
        tree = ast.parse(source, mode="eval")
    except SyntaxError as exc:
        raise _error("invalid_syntax", "invalid syntax") from exc
    except UnicodeError as exc:
        raise _error("bad_unicode", "source contains invalid unicode") from exc
    except Exception as exc:
        raise _error("parse_error", f"parser error: {exc.__class__.__name__}") from exc

    _enforce_ast_limits_and_nodes(tree, max_depth=max_depth, max_nodes=max_nodes)

    if not isinstance(tree, ast.Expression):
        raise _error("invalid_root", "root must be ast.Expression")
    if not isinstance(tree.body, ast.Call):
        raise _error("invalid_root", "root expression must be one call")
    return _canonicalize_top_call(tree.body)


def canonical_json(source, *, max_length=4096, max_depth=32, max_nodes=512) -> str:
    """Parse a frame and return compact canonical JSON."""

    return _json(
        parse_frame(
            source,
            max_length=max_length,
            max_depth=max_depth,
            max_nodes=max_nodes,
        )
    )


def parse_or_error(source, *, max_length=4096, max_depth=32, max_nodes=512) -> dict:
    """Return a deterministic ok/error object instead of raising codec errors."""

    try:
        frame = parse_frame(
            source,
            max_length=max_length,
            max_depth=max_depth,
            max_nodes=max_nodes,
        )
    except IpcAstCodecError as exc:
        return {"ok": False, "error": {"code": exc.code, "message": exc.message}}
    return {"ok": True, "frame": frame}


def make_nack(*, seq, ack, code, message) -> str:
    """Return a canonical N frame JSON string for a protocol error."""

    return _json(["N", seq, ack, [], [code, message], {}])


def _enforce_ast_limits_and_nodes(node: ast.AST, *, max_depth: int, max_nodes: int) -> None:
    count = 0

    def visit(current: ast.AST, depth: int) -> None:
        nonlocal count
        count += 1
        if count > max_nodes:
            raise _error("max_nodes_exceeded", "AST exceeds max node count")
        if depth > max_depth:
            raise _error("max_depth_exceeded", "AST exceeds max depth")
        if not isinstance(current, ALLOWED_NODE_TYPES):
            name = current.__class__.__name__
            raise _error("disallowed_node", f"disallowed AST node: {name}")
        for child in ast.iter_child_nodes(current):
            visit(child, depth + 1)

    visit(node, 1)


def _canonicalize_top_call(node: ast.Call) -> list:
    op = _call_name(node)
    if op not in TOP_LEVEL_OPS:
        raise _error("unknown_top_level_op", f"unknown top-level op: {op}")
    if node.keywords:
        _reject_keywords(node.keywords)
        raise _error("invalid_arity", "top-level frame does not accept keywords")
    if len(node.args) != 5:
        raise _error("invalid_arity", "top-level frame requires exactly five arguments")

    seq = _non_negative_int(node.args[0], "seq")
    ack = _non_negative_int(node.args[1], "ack")
    refs = _canonicalize_value(node.args[2])
    payload = _canonicalize_value(node.args[3])
    meta = _canonicalize_value(node.args[4])

    if not isinstance(refs, list):
        raise _error("invalid_refs", "refs must canonicalize to a list")
    if not isinstance(meta, dict):
        raise _error("invalid_meta", "meta must canonicalize to a dict")
    return [op, seq, ack, refs, payload, meta]


def _canonicalize_value(node: ast.AST) -> Any:
    if isinstance(node, ast.Constant):
        return _canonicalize_constant(node.value)
    if isinstance(node, ast.List):
        return [_canonicalize_value(item) for item in node.elts]
    if isinstance(node, ast.Dict):
        result = {}
        for key_node, value_node in zip(node.keys, node.values):
            if key_node is None:
                raise _error("disallowed_node", "dictionary unpacking is not allowed")
            key = _canonicalize_value(key_node)
            if not isinstance(key, str):
                raise _error("invalid_literal", "dictionary keys must be strings")
            if key in result:
                raise _error("duplicate_dict_key", f"duplicate dict key: {key}")
            result[key] = _canonicalize_value(value_node)
        return result
    if isinstance(node, ast.Call):
        return _canonicalize_nested_call(node)
    name = node.__class__.__name__
    raise _error("disallowed_node", f"disallowed AST node: {name}")


def _canonicalize_constant(value: Any) -> Any:
    if isinstance(value, str):
        if _contains_surrogate(value):
            raise _error("bad_unicode", "string literal contains surrogate code point")
        return value
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, int):
        if value < 0:
            raise _error("invalid_literal", "integers must be non-negative")
        return value
    raise _error("invalid_literal", f"unsupported literal: {type(value).__name__}")


def _canonicalize_nested_call(node: ast.Call) -> Any:
    name = _call_name(node)
    if name not in NESTED_CALLS:
        raise _error("unknown_nested_call", f"unknown nested call: {name}")
    if name == "F":
        _reject_keywords(node.keywords)
        _require_arity(node, 4, "F")
        file_id = _string_arg(node.args[0], "F id")
        start = _non_negative_int(node.args[1], "F start")
        end = _non_negative_int(node.args[2], "F end")
        digest = _string_arg(node.args[3], "F hash")
        return ["F", file_id, start, end, digest]
    if name == "ART":
        _reject_keywords(node.keywords)
        _require_arity(node, 2, "ART")
        return ["ART", _string_arg(node.args[0], "ART id"), _string_arg(node.args[1], "ART sha")]
    if name in {"Q", "V"}:
        _reject_keywords(node.keywords)
        return [_canonicalize_value(arg) for arg in node.args]
    if name in {"M", "ROLE"}:
        if node.args:
            raise _error("invalid_arity", f"{name} accepts keyword arguments only")
        return _canonicalize_keywords(node.keywords, name)
    raise AssertionError(f"unhandled nested call {name}")


def _call_name(node: ast.Call) -> str:
    if not isinstance(node.func, ast.Name):
        name = node.func.__class__.__name__
        raise _error("disallowed_node", f"disallowed AST node: {name}")
    return node.func.id


def _canonicalize_keywords(keywords: list[ast.keyword], call_name: str) -> dict:
    result = {}
    for keyword in keywords:
        if keyword.arg is None:
            raise _error("keyword_unpacking", "keyword unpacking is not allowed")
        if keyword.arg in result:
            raise _error("duplicate_keyword", f"duplicate keyword in {call_name}: {keyword.arg}")
        result[keyword.arg] = _canonicalize_value(keyword.value)
    return result


def _reject_keywords(keywords: list[ast.keyword]) -> None:
    for keyword in keywords:
        if keyword.arg is None:
            raise _error("keyword_unpacking", "keyword unpacking is not allowed")
    if keywords:
        raise _error("invalid_arity", "keywords are not allowed for this call")


def _require_arity(node: ast.Call, expected: int, name: str) -> None:
    if len(node.args) != expected:
        raise _error("invalid_arity", f"{name} requires exactly {expected} arguments")


def _non_negative_int(node: ast.AST, label: str) -> int:
    if not isinstance(node, ast.Constant) or isinstance(node.value, bool) or not isinstance(node.value, int) or node.value < 0:
        raise _error("invalid_integer", f"{label} must be a non-negative integer")
    return node.value


def _string_arg(node: ast.AST, label: str) -> str:
    if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
        raise _error("invalid_string", f"{label} must be a string")
    if _contains_surrogate(node.value):
        raise _error("bad_unicode", f"{label} contains surrogate code point")
    return node.value


def _contains_surrogate(value: str) -> bool:
    return any(0xD800 <= ord(char) <= 0xDFFF for char in value)


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    source = args[0] if args else sys.stdin.read()
    result = parse_or_error(source)
    print(_json(result))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
