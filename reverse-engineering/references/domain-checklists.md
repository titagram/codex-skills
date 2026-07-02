# Domain Checklists

Use only the sections relevant to the target. Keep all probes read-only unless the user explicitly expands scope.

## Environment Classification

- Identify host OS, CPU architecture, shell, permissions, virtualization/container status, connected devices, network interfaces, Bluetooth adapters, and available analysis tools.
- Identify target OS/runtime/architecture from manifests, binaries, firmware metadata, shebangs, file headers, package metadata, debug symbols, and strings.
- Record uncertainty when markers conflict.

## Project Type Classification

- Interpreted source: shebangs, package manifests, lockfiles, entry scripts, runtime config, dynamic imports.
- Compiled source: build systems, compiler flags, generated artifacts, link maps, object files, debug info, target triples.
- Binary-only: file format, architecture, imports, exports, sections, resources, signatures, packers, debug symbols.
- Firmware/embedded: image headers, bootloader markers, vector tables, S-record/Intel HEX/UF2, partition tables, device trees, RTOS strings.
- Driver/kernel: kernel module format, device IDs, IOCTL definitions, sysfs/procfs paths, interrupt/DMA references, privilege assumptions.
- Protocol/interface: packet captures, schemas, message examples, endpoint descriptors, service UUIDs, socket use, serial framing.

## Source Projects

- Map entrypoints before internals.
- Identify build/run commands without executing mutating tasks.
- Separate handwritten code from generated/vendor code.
- Track external interfaces: CLI, HTTP, sockets, serial, BLE, USB, files, database, kernel, cloud APIs.
- Document configuration precedence, feature flags, and environment variables.

## Compiled Binaries

- Use `file`, checksums, `strings`, `nm`, `readelf`, `objdump`, `otool`, `lipo`, `dumpbin`, `rabin2`, `rizin`, `radare2`, Ghidra, Binary Ninja, IDA, JADX, apktool, or language-specific tooling as available.
- Record format, architecture, endianness, ABI, interpreter/loader, linked libraries, relocations, sections, symbols, imports, exports, resources, and debug data.
- Prefer non-executing static analysis first.
- If dynamic analysis is needed, explain why and use a sandbox or isolated environment that does not alter the target.

## Firmware and Embedded

- Preserve original images and compute hashes before extraction.
- Identify container vs raw image, compression, encryption, signatures, partition tables, boot vectors, filesystem images, update metadata, and version strings.
- Search for MCU/SoC identifiers, linker scripts, memory addresses, peripheral names, RTOS markers, task names, interrupt handlers, and register constants.
- Treat flashing, pairing, unlock commands, NVM writes, calibration changes, and bootloader commands as mutating.

## Drivers and Hardware Interfaces

- Prefer passive enumeration: `lsusb`, `lspci`, `ioreg`, `system_profiler`, `dmesg`, `udevadm info`, sysfs reads, descriptor dumps, and existing logs.
- Identify bus, vendor/product IDs, class, endpoints, interfaces, kernel module, device nodes, permissions, IOCTLs, MMIO/port IO references, DMA, interrupts, and firmware loading paths.
- For direct calls, use only documented read-only operations or calls proven read-only by source/docs. Record the proof.
- Do not write registers, send reset/configuration commands, flash firmware, change pairing/bonding, or alter device mode without explicit approval.

## Bluetooth Interfaces

- Start with passive artifacts: provided captures, logs, service dumps, app source, firmware strings, UUID lists, and OS cache files.
- Classify BR/EDR vs BLE, profiles, GATT services, characteristics, descriptors, properties, notifications, indications, L2CAP/RFCOMM channels, and pairing requirements.
- Treat scanning as low risk but still environment-dependent. Treat connecting, pairing, bonding, writing characteristics, enabling notifications, and vendor commands as potentially mutating unless proven otherwise.

## Network Protocols

- Prefer supplied packet captures, logs, schemas, source, binaries, and config files.
- Identify transport, ports, TLS/plaintext, framing, compression, serialization, message types, state machine, authentication, replay behavior, and error handling.
- Do not send traffic to third-party systems without explicit authorization. For live targets, prefer localhost, test fixtures, or offline decoders.

## Syscalls and OS Interfaces

- Identify syscall use through source, decompiler output, imports, traces supplied by the user, `strace`/`dtruss`/`ktrace` where safe, seccomp/sandbox policies, and OS-specific wrappers.
- Record syscall names/numbers, arguments, flags, return/error paths, file descriptors, paths, capabilities, entitlements, and privilege boundaries.
- Treat tracing a live process as potentially invasive; prefer offline logs or controlled local runs.

## Evidence Quality

- Mark findings as observed when directly supported by artifact content or command output.
- Mark findings as inferred when they follow from patterns or partial evidence.
- Mark findings as unknown when evidence is absent or contradictory.
