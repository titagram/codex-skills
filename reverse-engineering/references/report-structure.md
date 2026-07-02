# Reverse Engineering Report Structure

Use this structure for the final deliverable. Omit sections that are not applicable, but keep the evidence-first order.

## 1. Executive Summary

- Target name, path, artifact type, and analysis date.
- One-paragraph classification: environment, project type, execution model, and confidence.
- Key findings and highest-value unknowns.

## 2. Scope and Non-Modification Statement

- In-scope paths, artifacts, devices, interfaces, captures, and endpoints.
- Out-of-scope items.
- Confirmation that no target files or device state were modified.
- External analysis directory used for generated tools and reports.

## 3. Environment

- Host OS, architecture, shell, user privileges, relevant devices, and tool availability.
- Target OS/runtime/architecture if observed.
- Tool versions for decompilers, disassemblers, packet analyzers, compilers, and custom helpers.

## 4. Evidence Index

Use a table:

| Evidence ID | Type | Source | Command/tool | Hash or version | Notes |
| --- | --- | --- | --- | --- | --- |
| E-001 | file inventory | target root | `inventory.py` | tool hash/version | read-only |

## 5. Target Classification

- Observed project markers, manifests, binary formats, firmware containers, or interface descriptors.
- Interpreted vs compiled vs mixed vs binary-only.
- Software, hardware, embedded, driver, protocol, Bluetooth, syscall, or mixed scope.
- Confidence and reasons.

## 6. Architecture and Behavior

- Components, entrypoints, initialization flow, main loops, services, daemons, interrupts, tasks, or handlers.
- Dependency graph and external systems.
- Data flow and control flow.
- Configuration and persistence.
- Error handling and logging.

## 7. Low-Level Analysis

Include only relevant subsections:

- Binary/decompilation: format, architecture, sections, symbols, imports/exports, strings, call graph, decompiler findings.
- Firmware/embedded: image layout, boot chain, memory map, MCU/SoC evidence, peripherals, register references.
- Driver/hardware: bus/device identifiers, descriptors, device nodes, IOCTLs, sysfs/procfs, register access, safe probes.
- Bluetooth: controller/adapter context, pairing assumptions, service UUIDs, GATT characteristics, L2CAP/RFCOMM behavior, captures.
- Network protocol: endpoints, framing, message types, state machine, authentication, replay/error behavior from captures.
- Syscalls: syscall list, call sites, argument patterns, privilege boundaries, OS-specific behavior.

## 8. Generated Tools

- Tool names, paths outside the target, purpose, inputs, outputs, and limitations.
- Exact commands used.
- Whether tools are deterministic and read-only.

## 9. Reproduction

- Minimal command sequence to reproduce the inventory and findings.
- Required permissions or hardware access.
- Any commands intentionally not run because they might mutate state.

## 10. Unknowns and Next Read-Only Steps

- Unknown facts and why they remain unknown.
- Proposed passive or read-only follow-up analyses.
- Risks that would require explicit user approval before live probing.

## 11. Prior-Knowledge Interpretation

Add this section last. Explain what the evidence suggests in the context of general platform, protocol, hardware, or software knowledge. Clearly label this as interpretation and avoid presenting it as observed fact.
