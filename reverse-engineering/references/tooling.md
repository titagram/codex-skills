# Temporary Tooling Rules

Create custom tools when existing commands do not provide structured enough evidence. Keep tools small, auditable, and outside the target root.

## Placement

- Use an external analysis directory such as `/tmp/reverse-engineering-<target>-<timestamp>`.
- Do not create helper scripts, caches, extracted files, or reports inside the target unless the user explicitly requests it.
- If extraction is required, extract copies into the external analysis directory and keep hashes of originals.

## Tool Design

- Accept explicit input paths and output paths.
- Default to stdout for summaries.
- Fail closed if an output path points inside the target root.
- Avoid following symlinks unless the report records why it is safe.
- Keep raw bytes handling binary-safe.
- Prefer structured libraries for known formats: `plistlib`, `zipfile`, `tarfile`, `sqlite3`, `json`, `tomllib`, `configparser`, `xml.etree.ElementTree`, `construct`, `scapy`, or protocol-specific parsers when available.
- Record assumptions, parser limitations, and skipped data.

## Decompilation and Disassembly

- Use read-only analysis commands and write generated databases/projects outside the target.
- Record exact tool versions and import settings.
- Preserve original hashes before extraction or conversion.
- Treat decompiler output as an aid, not ground truth; verify with headers, sections, symbols, cross-references, and runtime/interface evidence.

## Hardware and Live Interface Tools

- Start by dumping descriptors, metadata, logs, and read-only status.
- Add a `--dry-run` mode for any tool that could touch hardware or send packets.
- Require explicit command-line flags for live probing.
- Log every request and response.
- Do not write registers, characteristics, NVM, firmware, config state, network state, or pairing state unless the user explicitly expands scope.

## Reporting Tool Output

For each custom tool, include:

- Purpose.
- Source path outside target.
- Inputs and outputs.
- Command line.
- Read-only guarantee or remaining risk.
- Summary of findings and raw output location.
