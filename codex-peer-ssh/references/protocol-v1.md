# ipc-ast-v1 Protocol

Use this reference when composing, validating, debugging, or recovering Codex peer-to-peer messages.

## Goal

Use compact structured frames between Codex agents to reduce token use, ambiguity, and retries. Do not optimize for human readability. The human-facing Codex instance translates between normal human language and this protocol.

## Frame Shape

Every top-level message is one Python-like call expression:

```text
OP(seq, ack, refs, payload, meta)
```

The codec canonicalizes each valid expression to compact JSON:

```json
["OP",seq,ack,refs,payload,meta]
```

The codec validates only that `seq` and `ack` are non-negative integers. Monotonic `seq` ordering per sender and "highest remote `seq` processed" semantics for `ack` are protocol/session responsibilities.

## Literal Subset

The codec accepts only strings without surrogate code points, non-negative integers, booleans, `None`, lists, string-keyed dictionaries without duplicate keys, and allowed calls. It rejects floats, negative integers, tuples, attributes, subscripts, operators, comprehensions, f-strings, and other unsupported AST nodes.

Hardening rules:

- Duplicate dictionary keys are rejected.
- Duplicate `M(...)` or `ROLE(...)` keywords are rejected when exposed by the parser.
- Keyword unpacking and dictionary unpacking are rejected.
- Source text and string literals containing surrogate Unicode code points are rejected.

## Operations

- `H`: handshake. Exchange side, role, supported protocol versions, session id, and resume hints.
- `C`: contract. Record workspace, autonomy, guardrails, approval thresholds, and verification expectations.
- `K`: codec negotiation. Record max length, max depth, max nodes, dictionary mode, and base fallback.
- `D`: dictionary update. Define short symbols for repeated terms, files, commands, artifacts, and task labels.
- `S`: state checkpoint. Record current phase, last stable result, last verified command, and recovery anchor.
- `A`: ask. Request diagnosis, action, review, clarification, local-side help, or verification.
- `R`: result. Return findings, answers, verification output, or completed action summaries.
- `P`: patch. Reference or propose a patch, diff, file edit, or artifact.
- `N`: nack. Reject a frame or request with deterministic code and minimal explanation.
- `Z`: close. End or pause a session with final state and resume information.

## Nested Calls

- `F(id, start, end, hash)`: file reference. Use stable short ids and include a content hash when available.
- `ART(id, sha)`: artifact reference. Use for generated files, patches, logs, screenshots, or bundles.
- `Q(...)`: compact request payload. Use positional terms such as `Q("why","test_fail","cmd0")`.
- `M(key=value, ...)`: metadata dictionary. Use for budgets, response shape, confidence, risk, and verification constraints.
- `V(...)`: compact value vector. Use for negotiated numeric or string parameters.
- `ROLE(key=value, ...)`: role declaration. Use during handshake and contract setup.

Nested canonical JSON shapes:

- `F(id, start, end, hash)` -> `["F",id,start,end,hash]`
- `ART(id, sha)` -> `["ART",id,sha]`
- `Q(...)` and `V(...)` -> bare arrays of their values, such as `["why","test_fail","cmd0"]`
- `M(...)` and `ROLE(...)` -> objects/dicts, such as `{"codec":"ipc-ast-v1"}`

## Handshake Sequence

Start every new session with:

```text
H(1,0,[],ROLE(side="local",mode="human-facing"),M(codec="ipc-ast-v1",session="sid"))
H(1,1,[],ROLE(side="remote",mode="worker-peer"),M(codec="ipc-ast-v1",session="sid"))
C(2,1,[],Q("contract","workspace","guardrails"),M(workspace="/remote/project",autonomy="flag-bound"))
K(3,2,[],V("max_len",4096,"max_depth",32,"max_nodes",512),M(dict=True,fallback="ipc-ast-v1"))
```

The exact payload can vary, but `H`, `C`, and `K` must complete before task traffic starts.

## Dictionary Updates

Use `D` to reduce repeated tokens:

```text
D(4,3,[],{"f1":"src/app.py","cmd0":"python3 -m unittest","t1":"test_fail"},M(scope="session"))
```

After a dictionary update is acknowledged, both peers may use the short ids. If dictionary-compressed traffic causes repeated `N` frames, return to base `ipc-ast-v1` without dictionary compression.

## Error Rules

If a frame fails validation, do not infer intent from prose or partial syntax. Reply with `N`:

```text
N(8,7,[],Q("bad_frame","disallowed_node","Subscript"),M(action="resend_base"))
```

The `make_nack()` helper emits canonical JSON in this shape:

```json
["N",seq,ack,[],[code,message],{}]
```

Use stable error codes from the codec when possible: `invalid_type`, `source_too_long`, `invalid_syntax`, `bad_unicode`, `parse_error`, `max_nodes_exceeded`, `max_depth_exceeded`, `disallowed_node`, `invalid_root`, `unknown_top_level_op`, `invalid_arity`, `invalid_integer`, `invalid_refs`, `invalid_meta`, `invalid_literal`, `duplicate_dict_key`, `unknown_nested_call`, `invalid_string`, `keyword_unpacking`, and `duplicate_keyword`.

## Guardrail Messages

Represent risky-action preflight as structured messages:

```text
A(12,11,[],Q("approval","risky_action","sudo"),M(cmd="sudo apt install nodejs",scope="system",risk="global_runtime_change",rollback="documented",verify="node --version"))
R(13,12,[],Q("denied","use_project_local_tooling"),M(reason="outside_workspace"))
```

Ordinary workspace actions such as `mkdir`, local dependency install, tests, lint, and build do not need approval. They should still be logged when they change project state.

## Recovery

Use `S` after stable milestones:

```text
S(20,19,[],Q("checkpoint","tests_passed","cmd0"),M(phase="verification",resume="runtime:codex-peer-sid"))
```

After reconnect, compare the last local and remote `seq` and `ack`. Resume from the newest shared checkpoint. If logs diverge, prefer the last acknowledged frame and summarize divergence in `journal.md`.

## Compact Resume

Use compact resume when token budget matters. Rebuild the next peer prompt from durable state instead of replaying or resuming a full transcript:

- selected session metadata from `session.json`
- latest acknowledged `C` and `K`
- recent `D` dictionary frames
- recent `S` checkpoints
- a bounded `journal.md` tail
- the new `A(...)` task frame

Do not include old `A/R` traffic by default. If old task/result content is required, first summarize it into `S(...)` or define a compact `D(...)` symbol. Full transcript resume is a fallback for unstructured reasoning continuity, not the default steady-state path.

## Prose Fallback

Free prose between peers is an emergency bridge only. If used, log it in `journal.md`, summarize it with `S`, and return to structured frames immediately.
