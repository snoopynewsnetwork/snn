# Build and offline checks

All scripts write only the map report and maps directory. No Git, producer,
coordinator, dispatch, shared data or peer writes occur. No agent or collector
is launched. The external historical acceptance is read at its path at runtime;
its hash/body is never reverse-pinned into this package. Source maps and GIS
are independent originals, and the complete frozen first-pair source closure
is immutable read-only evidence rather than a mutable newsroom input.

Build sequence from repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/illinois/maps/replay_contract.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/illinois/maps/audit_gis.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/illinois/maps/build_atlas.py
node senate/2026/illinois/maps/test_atlas.cjs
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/illinois/maps/write_report.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/illinois/maps/validate_maps.py --full --seal
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/illinois/maps/validate_maps.py
```

The native binary audit checks ZIP membership/CRC, complete native DBF schema
and literal padded rows, all SHP/SHX indices and record lengths, every bbox/part
and IEEE754 XY bit against installed PyShp. Its constructor was inspected before
the points/parts adapter was written. No shell/hole GeoJSON reinterpretation,
auto-closure, source repairs or coordinate transforms occur. Original null,
empty or invalid records would remain in source rather than be repaired/dropped;
none occurred in this Census original. Individual-ring simplicity is unitless;
no area/adjacency/legal sliver/overlap/gap calculation is claimed.

All102native county slices are rechecked against full original SHP content and
DBF bytes after JSON roundtrip. The rank validator compares all complete source
observations and all108complete authority objects/child arrays, exact primary
threshold/crossing/remainder, nulls and parent identities. It verifies every
acquisition receipt, parent and stored source part. The source GIS count is
10084, not10062; the validator never expects label/count equality or uses spatial
matching to force a join. The external ledger replay verifies every554096full
recursive object and all31root fields/116bodies before map construction.

The actual generated JavaScript is evaluated with a minimal DOM. This checks
display/filter/detail functions and HTML escaping, and is explicitly not a
browser rendering assertion. All71PDFs/118pages are automatically parsed; the
seven actually viewed PDF pages and four actually viewed affine previews are
recorded only in `qa/visual-review.json`. Original PDFs keep every original page.
Automatic SVG/PDF raster generation is separate from actual image inspection.

Negative fixtures mutate actual accepted data/original binary in memory rather
than retaining duplicated giant source ZIPs. They must be rejected for exact
order, schema/null preservation, no fabricated polygon, no county replacement
of a city reporting parent, complete remainder, SHX index, DBF field width, SHP
bbox and part integrity. No successful fixture approves live or legal input.

Deterministic replay rebuilds full/priority/remainder objects, parents, all county
full-point SVGs and exact native derived outputs, original page metadata/text,
selected automatic PNGs and the atlas. It compares entire output bytes and
membership, and reruns the generated JavaScript check. There is no network in
this phase. The visual review is a separate record of actual observations, not
a newly fabricated inspection during each automatic rebuild.

The seal then includes the report and every owned file except the seal itself.
A normal validation run checks exact membership/bytes/hashes and the full native
original/persisted coordinate checks without changing files. Approval for current
geography, legal80coverage, result IDs, cadence, exact outstanding ballots and
probability remains false and outside these structural/replay checks.
