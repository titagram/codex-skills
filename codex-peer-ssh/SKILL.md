---
name: codex-peer-ssh
description: Use when the user explicitly wants Codex to start, resume, or coordinate with a persistent remote Codex peer over SSH using a persistent runtime provider such as tmux or screen, mirrored session logs, remote skill bootstrap, and compact IPC frames. Trigger for Codex-to-Codex collaboration across machines, remote peer sessions, SSH runtime Codex delegation, or requests to reduce inter-agent token use with structured protocol messages. Do not trigger for ordinary SSH commands or one-off remote shell execution.
---

# Codex Peer SSH

Coordinate with a persistent remote Codex instance over SSH. Keep the local Codex instance human-facing. Treat the remote Codex instance as an operational peer in the declared remote workspace. Prefer `tmux` as the remote runtime provider, fall back to `screen`, and do not claim persistence when neither is available.

## Intake

Ask for missing values one at a time:

1. SSH target, preferably an SSH config alias or `user@host`. Reject targets that start with `-`.
2. Remote working directory.
3. Remote Codex startup flags, such as `--yolo`, `--resume`, `--model`, or none.
4. Session name, or permission to generate one.

Ask for a remote Codex command or path only if automatic resolution fails.

Assume SSH keys are already exchanged. Do not ask the user for SSH passwords or private keys.

## Session Layout

Create mirrored state under:

```text
.codex-peer/$SESSION_ID/
├── session.json
├── machine.jsonl
└── journal.md
```

Use `session.json` for target, workspaces, runtime provider, runtime session name, resolved Codex command, command resolution method, codec version, guardrails, flags, timestamps, compact resume policy, and last known `seq` and `ack`.

Use `machine.jsonl` for canonical IPC frames and transport events.

Use `journal.md` for human-readable goals, decisions, approvals, failures, verification, and outcome.

## Bootstrap Workflow

Run preflight in this order:

1. Verify SSH with an argv invocation such as `["ssh", "--", SSH_TARGET, "true"]` when the local SSH supports `--`; otherwise reject option-looking targets before invoking `ssh`.
2. Verify or create the remote workspace with `mkdir -p`.
3. Select the remote runtime provider: prefer `tmux` from `command -v tmux`; otherwise fall back to `screen` from `command -v screen`.
4. If neither `tmux` nor `screen` exists, enter the no-persistent-runtime path in Runtime Selection. Do not continue as a persistent peer session.
5. Resolve the remote Codex command with Remote Codex Resolution. A plain non-interactive `command -v codex` miss is not final.
6. Check whether `codex-peer-ssh` exists in `${CODEX_HOME:-$HOME/.codex}/skills/codex-peer-ssh` on the remote host. Expand `${CODEX_HOME:-$HOME/.codex}` on the remote host, not locally.
7. If missing or stale, copy the local skill folder to the remote skill path.
8. Create local and remote `.codex-peer/$SESSION_ID/`.
9. Start or attach to remote runtime session `codex-peer-$SESSION_ID` with the selected provider.
10. Launch remote Codex in the remote workspace with the user-provided flags.

Log every bootstrap action. Do not hide remote installation or updates.

## Runtime Selection

Select one runtime provider for the session and persist it in `session.json`.

1. Prefer `tmux` when available. It supports durable attach/reconnect and pane interaction.
2. Use `screen` when `tmux` is missing. It still gives a durable session, but log output to files more aggressively because capture behavior is less uniform.
3. If neither `tmux` nor `screen` is available, do not start a persistent peer session. Offer these options:
   - Install a runtime only with the guardrails below. User-local or workspace-local installs may proceed after low-risk preflight logging; `sudo` or system package manager installs require human approval.
   - Run a degraded direct-SSH/log-only diagnostic mode only if the human explicitly accepts that it is not a persistent peer session.

Runtime command shapes:

```text
tmux:   tmux new-session -A -s <session> <shell-safe-codex-command>
screen: screen -S <session> -dm sh -lc <shell-safe-codex-command>
```

For both providers, build `<shell-safe-codex-command>` from an argv list and quote each token. Do not pass raw flags through the provider shell.

## Remote Codex Resolution

Resolve the remote Codex command before launch and persist the result in `session.json`.

Try these strategies in order:

1. Non-interactive SSH path: `command -v codex`.
2. The remote login or interactive shell, because managers such as `nvm`, `pyenv`, `asdf`, or shell profile snippets may expose `codex` only there. For bash or zsh, try `"$SHELL" -lic 'command -v codex'`; if `$SHELL` is not usable, try `bash -lic` and `zsh -lic` when present.
3. Common user-local bin locations such as `$HOME/.local/bin`, `$HOME/.npm-global/bin`, `$HOME/.bun/bin`, and `$HOME/.nvm/versions/node/*/bin`.
4. A human-provided absolute path or command.

When resolution returns an absolute path, prefer launching that path instead of the bare `codex` token. If the path was discovered through a shell-managed environment, verify with a cheap command such as `codex --version` using the same strategy when possible. If direct execution fails because the launcher depends on PATH, preserve the needed bin directory with `PATH=<codex-bin>:$PATH` or launch through the same login shell strategy.

Treat successful `codex --version` or `codex --help` output as proof that Codex is present even if the shell prints non-fatal warnings. If startup shows an update prompt, login prompt, migration prompt, or other first-run interstitial, classify it as an interactive startup state rather than command absence.

Do not auto-update Codex to clear an update prompt. Continue without updating when Codex allows it. Ask the human before any update that changes a global or user-local Codex install, even when the install lives under `nvm`, `npm`, `brew`, or another user-managed toolchain.

Do not edit remote shell profiles just to expose `codex`; that is a risky environment change and requires human approval.

## Remote Launch Pattern

Do not concatenate raw user input into an SSH command. Build the remote command as data, quote every user-controlled value, then pass exactly one remote command string to `ssh`.

Prefer SSH config aliases or `user@host` targets. Reject `SSH_TARGET` values that start with `-`. Invoke SSH as an argv list, not by concatenating a local shell string. Use `ssh -- SSH_TARGET remote_cmd` when the local SSH supports `--`; otherwise reject option-looking targets before invoking `ssh`.

Preferred construction:

```text
if SSH_TARGET starts with "-": reject it
resolved_codex = resolve_remote_codex()
codex_argv = [resolved_codex.command] + shlex_split(CODEX_FLAGS)
codex_command = " ".join(quote(arg) for arg in codex_argv)
if resolved_codex.needs_path_prefix:
    codex_command = "PATH=" + quote(resolved_codex.bin_dir) + ":$PATH " + codex_command
if resolved_codex.needs_login_shell:
    codex_command = quote(resolved_codex.shell) + " -lic " + quote(codex_command)
runtime_session = "codex-peer-" + SESSION_ID
runtime_cmd = runtime_launch_command(provider, runtime_session, codex_command)
remote_cmd = "cd " + quote(REMOTE_WORKSPACE) + " && " + runtime_cmd
run(["ssh", "--", SSH_TARGET, remote_cmd])
```

Here `shlex_split(...)` means parse user-provided flags into argv tokens before launch, and `quote(...)` means shell-safe quoting such as Python `shlex.quote`. Quoting the whole `codex_command` string is not enough; quote each argv token before joining it, because runtime providers execute through a shell layer. Treat `SSH_TARGET`, `REMOTE_WORKSPACE`, `SESSION_ID`, runtime provider name, and every Codex flag token as untrusted until validated or quoted. The `&&` belongs inside `remote_cmd`; do not let the local shell parse it.

If flags are complex, prefer starting or attaching the runtime session first, then send the Codex launch command through the controlled runtime channel or a remote stdin script.

If a runtime session already exists, attach or send a resume instruction instead of starting a duplicate peer.

## IPC Protocol

Use `references/protocol-v1.md` when composing or debugging peer messages.

Use `scripts/ipc_ast_codec.py` to validate and canonicalize peer frames when possible:

```bash
python3 scripts/ipc_ast_codec.py 'A(7,6,[F("f1",20,45,"91be22aa")],Q("why","test_fail","cmd0"),M(want="diagnosis",budget=500))'
```

The goal is lower token use, higher precision, and fewer retries than prose. Do not default to free-form peer chat. Use structured frames for peer traffic after handshake.

Required before task traffic:

1. `H`: exchange role, side, session id, and protocol version.
2. `C`: record workspace, autonomy, flags, and guardrail terms.
3. `K`: record codec limits and dictionary feature status.

Conditional messages:

- `D`: define session abbreviations when repeated terms appear.
- `S`: checkpoint stable milestones and recovery anchors.

In persistent sessions, send `H`, `C`, `K`, and broad `D` setup frames once per negotiated session or resume event, not before every task. For normal task traffic, prefer short `A`, `R`, `P`, and `S` frames that reference established dictionary ids. A one-shot prompt containing the full handshake is a bootstrap test, not evidence of steady-state token savings.

If a frame is invalid, send `N` with a deterministic error. Do not infer intent from malformed syntax.

## Compact Resume

Prefer compact resume for long-running peer work, benchmarks, and any session where token savings matter. Do not use `codex exec resume` as the default memory mechanism: it can reload a large transcript even when the new peer message is a tiny `A(...)` frame.

Compact resume means:

1. Keep durable memory in `.codex-peer/$SESSION_ID/session.json`, `machine.jsonl`, and `journal.md`.
2. Record useful shared state as acknowledged `D(...)` dictionary frames and `S(...)` checkpoints.
3. Start a fresh remote Codex turn or prompt from only the bounded state: selected `C/K`, recent `D`, recent `S`, a short journal tail, and the new task frame.
4. Use full thread resume only when continuity of unstructured reasoning is explicitly more important than token budget.

Use the helper when available:

```bash
python3 scripts/compact_context.py .codex-peer/$SESSION_ID \
  --task-frame 'A(9,8,[F("f1",1,120,"abc")],Q("review","risk"),M(budget=500))'
```

Send the helper output as the next remote prompt. It validates the task frame, excludes old `A/R` traffic by default, and bounds journal text. If a required fact is not in a checkpoint or dictionary, create a new `S(...)` or `D(...)` before compact resume instead of relying on transcript recall.

## Guardrails

The remote peer may operate autonomously according to the Codex flags provided by the user, including permissive flags. Still enforce these guardrails.

Proceed without human approval for:

- Reading and editing files inside the remote workspace.
- Creating files and directories inside the remote workspace.
- Installing project-local dependencies.
- Running tests, lint, typecheck, build, and project scripts.
- Creating logs, patches, and artifacts under `.codex-peer/`.

Log preflight without asking approval for:

- Project-local dependency changes that update lockfiles or local environments.
- Dependency upgrades.
- Tool downloads into the workspace.
- Long-running or potentially expensive project commands.

Ask human approval only for:

- `sudo` or system package manager use.
- Global runtime changes.
- Shell profile, SSH config, credential, keychain, daemon, or service changes.
- Any action outside the declared workspace.
- Killing or restarting processes not created by this peer session.
- Non-recoverable destructive operations.
- Sending secrets or sensitive data to unapproved external hosts.

For risky preflight, record intent, command or command class, scope, risk, rollback or verification plan, and approval status in `machine.jsonl` and `journal.md`.

Do not ask for harmless workspace actions such as `mkdir`.

## Peer Direction

Allow the remote peer to initiate structured requests toward the local peer. The remote peer must not directly operate on the local machine. The local agent evaluates each request, applies guardrails, and decides whether to execute, ask the human, or refuse.

## Recovery

If SSH drops, reconnect to the existing runtime session with the selected provider.

For `tmux`, attach to or send commands to `codex-peer-$SESSION_ID`. For `screen`, attach with `screen -r codex-peer-$SESSION_ID` or use `screen -S codex-peer-$SESSION_ID -X ...` where appropriate.

If remote Codex exits, prefer compact resume from `session.json`, `machine.jsonl`, `journal.md`, recent `D(...)` frames, and the latest `S(...)` checkpoint. Use `--resume` only when compact state is insufficient or the human accepts the larger token cost.

If local and remote logs diverge, compare last known `seq` and `ack` values and resume from the newest shared checkpoint.

If dictionary-compressed messages repeatedly produce `N`, return to base `ipc-ast-v1`.

Free prose between peers is an emergency bridge only. Log it, summarize it with `S`, and return to structured frames.

## Verification

Before claiming the skill or a peer session works:

1. Run the codec unit tests.
2. Run compact context helper tests when compact resume changed.
3. Run skill validation with `quick_validate.py`.
4. Test a local or real SSH launch path with the selected runtime provider.
5. Confirm `H/C/K` handshake is represented in logs.
6. Confirm valid `A -> R` and invalid frame `N` behavior.
7. Confirm compact resume can reconstruct a task prompt without old transcript traffic.
8. Confirm ordinary workspace operations do not ask approval.
9. Confirm risky operations do ask approval.

When benchmarking token savings, report one-shot end-to-end Codex usage, full thread resume usage, compact resume usage, cached input tokens, and steady-state peer message size separately. Before asking a peer for a diff, detect whether the workspace is a Git repository; in non-Git workspaces, use direct file ranges, saved baseline artifacts, or `diff --no-index`.

Report exactly what was tested and what could not be tested.
