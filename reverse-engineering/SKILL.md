---
name: reverse-engineering
description: Read-only reverse engineering workflow for unknown software, firmware, binaries, drivers, hardware interfaces, Bluetooth interfaces, network protocols, and syscall behavior. Use when Codex must inspect an unfamiliar project or artifact from first principles, classify the environment and project type, create temporary analysis tooling, decompile or disassemble when useful, document evidence, and produce a structured report without modifying the target project.
---

# Reverse Engineering

## Overview

Use this skill to analyze an unknown target from evidence rather than assumptions. Treat the target as read-only, create any helper tools outside the target, and produce a structured report before adding any broader interpretation from general knowledge.

## Operating Rules

- Assume no prior knowledge about the project. Start from filesystem, metadata, manifests, binaries, interfaces, traces, and observed behavior.
- Do not modify the target project or device state. Do not edit files, run formatters, install dependencies into the target, commit changes, flash firmware, pair devices, write registers, send mutating commands, or run tests that may alter state unless the user explicitly changes the scope.
- Write notes, extracted metadata, generated scripts, and reports only outside the target root unless the user explicitly asks to place documentation in the project.
- Prefer passive inspection first: file metadata, manifests, strings, symbols, headers, packet captures supplied by the user, logs, documentation, build files, and read-only OS queries.
- Label every conclusion as observed, inferred, or unknown. Keep a trail of commands, scripts, inputs, outputs, hashes, and file paths sufficient for reproduction.
- When direct hardware, Bluetooth, network, or driver interaction is requested, treat every call as potentially mutating. Use documented read-only queries or passive capture first; ask before privileged live probing if read-only behavior is uncertain.
- Place any prior-knowledge explanation at the end of the final report in a section named `Prior-Knowledge Interpretation`. Do not let it replace the evidence-backed analysis.

## Workflow

1. Scope the target.
   - Identify the target root, artifacts, devices, captures, or remote endpoints that are in scope.
   - Create an external analysis directory such as `/tmp/reverse-engineering-<target>-<timestamp>` for generated tools and reports.
   - Capture host context: OS, architecture, shell, available compilers, decompilers, disassemblers, packet tools, Bluetooth tools, and hardware enumeration tools.

2. Build a read-only inventory.
   - Run `scripts/inventory.py <target>` when the target is a filesystem path.
   - Supplement it with `rg --files`, `file`, checksums, manifest inspection, and source tree sampling.
   - Classify the target as interpreted source, compiled source, binary-only, firmware, embedded, driver/kernel, protocol/interface, mixed, or unknown.

3. Route to the relevant technical checklists.
   - Read `references/domain-checklists.md` when the target involves binaries, firmware, drivers, hardware interfaces, Bluetooth, network protocols, or syscalls.
   - Read `references/tooling.md` before creating custom parsers, decompilation helpers, trace summarizers, packet decoders, or hardware query scripts.
   - Read `references/report-structure.md` before writing the final report.

4. Analyze from the lowest reliable layer upward.
   - For source projects, map entrypoints, dependency boundaries, build/runtime commands, generated files, configuration, and external interfaces.
   - For compiled artifacts, identify format, architecture, sections, imports, exports, symbols, strings, debug data, call graph hints, and decompiler output when tools are available.
   - For firmware or embedded targets, identify container format, CPU/MCU family, memory layout, boot flow, peripheral references, register maps, protocol handlers, and update mechanisms.
   - For drivers and hardware interfaces, map device nodes, buses, IOCTLs, sysfs/procfs paths, registers, descriptors, permissions, and safe read-only probes.
   - For Bluetooth and network interfaces, inspect captures, descriptors, service UUIDs, endpoints, message framing, state machines, authentication, and command semantics.
   - For syscall behavior, map call sites, arguments, error handling, privilege boundaries, sandboxing assumptions, and OS-specific behavior.

5. Create custom tools as needed.
   - Build small Python, shell, or language-specific tools in the external analysis directory.
   - Make each tool accept explicit input paths and write outputs only to the external analysis directory or stdout.
   - Prefer structured parsers over ad hoc string slicing when formats are known.
   - Record tool source, command lines, versions, and limitations in the report.

6. Produce documentation.
   - Create a structured report plus any detailed appendices needed for architecture, binary layout, protocols, hardware interfaces, or syscall traces.
   - Put evidence-backed findings first. Add `Prior-Knowledge Interpretation` only after the report body and clearly separate it from observed facts.

## Resource Guide

- `scripts/inventory.py`: read-only filesystem inventory and project classification helper. Run it first for local targets.
- `references/domain-checklists.md`: domain-specific probes and evidence to collect for source, binaries, firmware, embedded, drivers, hardware, Bluetooth, network protocols, and syscalls.
- `references/tooling.md`: rules for creating temporary reverse-engineering tools without touching the target.
- `references/report-structure.md`: report and documentation template.

## Output Expectations

- Start with a concise classification of the target and environment.
- Include an evidence index with commands, files, hashes, captures, and generated helper tools.
- Document architecture, entrypoints, data/control flow, interfaces, protocols, binary/firmware structure, hardware surfaces, and syscall behavior as applicable.
- Include unknowns, confidence, reproduction steps, and suggested next read-only analyses.
- End with `Prior-Knowledge Interpretation` and keep it explicitly separate from the evidence-backed report.
