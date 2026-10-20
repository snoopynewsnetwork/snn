# Reproduce the Rhode Island baseline package

Run from `senate/2026/rhode-island/` with Python 3 and Poppler `pdftotext` on PATH. Only Python standard-library modules are used; no dependency/cache tree is retained.

```sh
python -B data/baselines/scripts/reproduce.py
python -B data/baselines/scripts/validate.py --read-only
python -B data/baselines/scripts/calculate.py data/baselines/scenarios/fixtures/known-final-denominator.json
python -B data/baselines/scripts/calculate.py data/baselines/scenarios/2024-senate-historical-tie.input.json
python -B data/baselines/scripts/audit.py
```

The reproducer makes an isolated temporary state tree, references each fixed original gzip body by exact receipt path/hash, and reruns original ZIP/PDF/XLSX extraction, municipal/Board reconciliation, native baselines, targets and supplements. It compares exact deterministic bytes against the retained outputs, then deletes the temporary tree. It does not reacquire originals, modify production evidence, rerun peer capture, or rewrite the seal/manifest. [qa/reproduction.json](qa/reproduction.json) records the completed comparison.

Source acquisition is separately reproducible with `scripts/acquire.py NEW_OBSERVATION_NAME EXACT_PUBLIC_URL [PARENT_ID]`. A new observation name is mandatory; existing receipts never overwrite. Original URLs/status/clocks/headers/hashes and paths are in [source/inputs.json](source/inputs.json), [source/current-inputs.json](source/current-inputs.json), [source/chains.json](source/chains.json) and [source/SCHEMA.md](source/SCHEMA.md). Future downloads can change; never replace the original baseline with a new body silently. `freeze_inputs.py` documents the original one-time receipt selection but is intentionally refusing to replace an existing freeze.

`extract_originals.py` preserves selected full raw records across every source view and all ZIP member hashes/CRCs; whole unrelated offices stay in the original bytes. `publications.py` parses every municipality's original HTML and Board selected cells. `controls.py` reconciles independent PDF statewide totals, all native statistic scopes, and literal 2024 Senate write-in details. `build.py` uses only those own original-derived data. `calculate.py` is entirely offline. `fixtures.py` saves actual CLI inputs/results; negative fixtures return code 2. The invalid NaN/Infinity token examples are deliberately text files, and their results are strict JSON.

`reciprocal.py` reads only frozen captured turnout bodies. It does not read a mutable peer aggregate or change any peer output. Source-anchor tuples handle the delimiter difference; raw labels remain unequal at 11 whitespace positions, explicitly recorded. [reciprocal/reconciliation.json](reciprocal/reconciliation.json) is scoped to those captured bodies, with acceptance/current geography still false.

`validate.py` default mode writes validation plus independent roots/denominator evidence for authoring; use `--read-only` after sealing. `seal.py` is an authoring finalization command, writes seal first and manifest last, and refuses replacement of an existing seal. `audit.py` is read-only and verifies every owned/reference byte against the sealed manifest, all frozen pre-peer bodies, full source/order/coverage/links/bounds, and the standalone validator. No owned files were written after the final manifest and audit.
