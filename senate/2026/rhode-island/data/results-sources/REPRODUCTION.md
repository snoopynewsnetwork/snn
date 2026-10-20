# Offline reproduction and exact originals

Run from `senate/2026/rhode-island/`. Python standard library and existing Poppler are sufficient. All Python invocations disable bytecode. No dependency/cache directory or network access is required.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B data/results-sources/scripts/reproduce.py
PYTHONDONTWRITEBYTECODE=1 python3 -B data/results-sources/scripts/audit.py
```

`build.py --check` reconstructs every generated inventory, source-schema, HTML representation, primary export check, complete-reference investigation and CSV byte-for-byte in memory. It reads only exact receipt pins in `inputs.json`, their immutable entities and fixed producer contract/source files; it imports no producer code. Primary data is research-only. `validate.py` independently verifies all investigation references/coverage and meaningful negative fixtures. `original_audit.py` checks all whole original technical members/long fields and original write-in cells/relationships. `replay.py` consumes the whole path-only authority and replays all ordered objects and exact history. It never persists the authority body or digest.

Every underlying first-pair file is read-only and exactly pinned in `external-inputs.json`. All original receipts/entities, full historical bodies, model outcomes and original pending flags remain preserved. Earlier path+SHA pairs resolve to their actual immutable tar members or ordered parts, never newer current files. No optional producer/coordinator helper or mutable news/peer discovery runs.

To reconstruct the first priority context's **entire** native object:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B data/results-sources/scripts/reconstruct.py --object data/results-sources/derived/priority-investigations.json /0/whole_native
```

The resolver also accepts `STATE_RELATIVE_PATH SHA256 BYTES` and writes the exact full stored body to stdout. For an original entity stored as gzip, decompress the complete returned body; for an archive member, use the recorded exact member name. The retained originals include every unrelated workbook member/field rather than a projected reconstruction. JSON pointer reconstruction returns the complete semantic object; exact original enclosing-file bytes remain separately available. The hash/size supplied to the CLI must come from an underlying source reference, never from external acceptance authority.

Acquisition is deliberately separate. `acquire.py NEW_NAME EXACT_PUBLIC_URL PARENT LITERAL_PROVENANCE` creates a new immutable observation; `batch.py` deduplicates exact request IDs before bounded concurrency. Do not rerun acquisition during reproduction. The initial sandbox DNS failure, later successful request, HTTP challenge bodies and TLS failure are separate original observations. Earlier lost duplicate-request metadata is explicitly unavailable in history. No source clock is reconstructed from HTTP/cache or PDF metadata.

`seal.py` is an authoring-only terminal step that refuses replacement: it captures complete preterminal owned bodies in a deterministic tar+gzip witness, refers to content-addressed acquired bodies once, writes the witness index and fixed final seal, then writes the complete manifest LAST. Neither validation nor seal reverse-pins that manifest. `audit.py` checks exact self-only manifest membership, every owned/source raw/stored hash/size, whole witness members, full references/hierarchy/links/coverage, original archive/cell checks, full authority replay and deterministic reconstruction without any write. The shell transcript of its final result is the terminal read-only evidence; no post-seal file records its own current digest.
