# Exact offline reconstruction

From the repository root, Python 3 with installed requests, PyShp, Shapely,
Pillow and PyMuPDF is sufficient. No package/environment directory is retained.
Source verification is independent of a browser or current network availability.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/illinois/maps/replay_contract.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/illinois/maps/audit_gis.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/illinois/maps/build_atlas.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/illinois/maps/validate_maps.py
```

The final command is read-only and checks the exact seal, source receipts,
complete observation/parent ordering, every persisted native county coordinate,
and the independent binary audit. `--full --seal` also reruns negative cases,
rebuilds deterministic outputs and creates a new owned membership seal. This
is a deliberate researcher operation for this owned package; it does not seal
or approve any producer, external acceptance, legal/current geography or feed.
The external authority remains a path-only dependency, read in full at runtime.

For one complete original, use the exact receipt path from the inventory:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/illinois/maps/reconstruct.py \
  --receipt maps/source/census-illinois-vtd2020.receipt.json \
  --output /private/tmp/illinois-original-vtd2020.zip
```

Concatenate `stored_parts` in order and `gzip.decompress` exactly once. The raw
entity length/hash in the receipt must match. All ZIP members remain inside the
original with their original names, CRCs and bytes. County JSON slices preserve
every native source XY bit through decimal binary64 roundtrip and retain every
literal DBF row as hex; they do not replace the original shapefile. The exact
original SHP content can be recovered with each record offset/length from that
ZIP, with original record numbers, headers and original SHX/DBF untouched.

For the full historical source closure, `replay_contract.py` reads all external
acceptance declarations at runtime, checks immutable producer seals, resolves
all complete root fields and companions, and streams every reference ledger
line in order. JSON pointers unescape `~1` and `~0`; JSONL records are 1-based;
CSV positions include the header where the reference says so. It compares full
recursive values including schema, category, original strings, nulls, positions
and every child field, not selected vote totals. The 2024/2022/2020 original
record streams retain all 146,370 records and all 1,756,440 field positions.

Original first-pair receipts already freeze appendable aggregate records; the
complete producer registry/shared-original reference files are sealed inputs.
No mutable newsroom aggregate or aggregate writer is a build input. Exact
legacy original bodies stay in their original read-only paths. The accepted
lossless full-object ledger is streamed as declared rather than copied or
sampled. No enormous duplicate acceptance/ledger body is stored here.

The atlas opens as a local HTML file. Priority mode shows the exact first
5,540 order; full and remainder modes preserve full rank order. Authority and
literal-label filters only change display, not source objects or geometry.
The entire parent hierarchy is embedded and available in the details section.
Clicking a row shows the inherited county-context preview, originals and gaps.
It does not select or highlight a purported matching polygon.
