# Delaware offline map research package

Open [index.html](index.html). It contains the exact ordered 311 priority observations, all 530 Senate observations, 219 remainder observations, all 537 historical structure rows, 533 historical sample-index identities, all six statutory cases, all ten unavailable cases, all 531 unjoined native feature attributes, three parent investigations and every acquisition receipt. It works from local files without external scripts, tiles, fonts or network data. Browser rendering was **not observed**; structural/link QA and actual static image inspection are recorded separately.

Actual originals were acquired along Department Maps → county map index/overviews and Department Maps → FirstMap Hub → public JavaScript dataset constructor → dataset metadata → native FeatureServer. All three counties were investigated by actual requests. Complete state native geometry and complete historical Census county VTD ZIPs are present or referenced by exact immutable original hash. No individual result observation has an approved polygon match. Shared state/parent/PDF/Census references provide research coverage for every row, with the finer/current/legal gaps visible.

The 2024 Senate denominator is the three reported candidates' 500,606 votes. The first 311 contribute 400,539; the preceding 310 contribute 399,708; 0807 adds 831. Top15 is 35,875; remainder219 is 100,067. County minimum2 sensitivity is New Castle+Sussex414,338; it does not replace the literal ED dispatch. The contract's full three parent hierarchies are retained.

[SCHEMA.md](SCHEMA.md) explains exact reconstruction, all fields and reference scopes. [manifest.csv](manifest.csv) inventories acquired entities. [asset-manifest.json](asset-manifest.json) seals every owned file except itself and every used external original/full-body reference. [source-inventory.json](source-inventory.json), [parent-inventory.json](parent-inventory.json), [gaps.json](gaps.json) and [qa/validation.json](qa/validation.json) are machine-readable.

Run from the repository root, with Python 3.11, Requests, PyShp 3.1.6, Shapely and Pillow installed. PDF rendering needs Poppler (`pdfinfo`, `pdftotext`, `pdftoppm`). Recorded versions and constructor source accompany the geometry audit. No dependency/cache directory is stored.

```sh
# Read-only offline checks; never consults external acceptance or network.
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/delaware/maps/validate.py --check
# Exact whole-body reconstruction checks.
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/delaware/maps/reconstruct.py --verify
# Export one exact source entity; output must not already exist.
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/delaware/maps/reconstruct.py --source county-kent-overview --output /tmp/delaware-rd11-original.pdf
# Deterministic offline derivative replay and hash comparison, no seal rewrite.
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/delaware/maps/replay.py
```

Acquisition is separate: `acquire.py ID URL PARENT_ID LITERAL_HREF` saves complete HTTP entities/redirects/errors; `acquire_chains.py` and `acquire_supplements.py` follow the saved observed chains. Request IDs are immutable and reject a different URL. To obtain a later snapshot use new IDs/directory and preserve the existing snapshot. `freeze.py` is a launch-only operation; offline replay never reruns it or reads the external acceptance. Legacy producer scripts referring to a mutable newsroom manifest are not executed. Their discovery role is explicitly replaced by full individually frozen receipts/producer-sealed source bodies in `source/reconstruction-override.json`.

All current geometry, legal/result identity, live cadence, exact remaining pool, collector and forecast/probability approvals remain false. Future signed/current/live evidence is an external qualification, not an unfinished historical-research build step. Coordinator alone reviews, accepts and publishes.
