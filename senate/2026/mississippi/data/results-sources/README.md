# Mississippi official source evidence

Read the [report](../../official-results.md), [schema](SCHEMA.md), [parent notes](parent-publication-notes.md), [validation](validation.json) and [manifest](asset-manifest.json).

Offline frozen audit from the repository root:

```sh
python3 -B senate/2026/mississippi/data/results-sources/reproduce.py
```

The raw source receipts and original entities are already retained. No network
is needed for the offline audit. The audit uses system Poppler for original PDF
controls and Node's built-in decoder for Brotli entities; no package dependencies
were installed.

Development/review reconstruction, only while this owned package is unfrozen:

```sh
python3 -B senate/2026/mississippi/data/results-sources/frozen_scope.py
python3 -B senate/2026/mississippi/data/results-sources/check_samples.py --render
python3 -B senate/2026/mississippi/data/results-sources/build_inventory.py
python3 -B senate/2026/mississippi/data/results-sources/write_notes.py
python3 -B senate/2026/mississippi/data/results-sources/reproduce.py --write-validation
python3 -B senate/2026/mississippi/data/results-sources/seal_manifest.py
python3 -B senate/2026/mississippi/data/results-sources/reproduce.py
```

Acquisition replay uses `acquire.py jobs-*.json` in the documented dependent
stage order in [acquisition replay](acquisition-replay.json). Those jobs preserve literal source links
and the sole public read-only POST. New retrievals require new receipt IDs; the
existing originals must not be overwritten. Existing IDs resolve retained bytes,
so running old job files is not evidence of a fresh retrieval. This is a one-shot
research package, not a running collection service. The optional coordinator
newsroom update is referenced in the report by path and is not a new build pin.
