# Offline Mississippi map schema

`index.json` has exactly 887 `priority_entries`, in the frozen
`ordered_priority_keys` order, plus 1,736 `full_preferred_native_entries` and
`all82parents`. `rank` is historical named-Senate volume rank. It is not a
precinct number. `source_page` is the original PDF page and `physical_column`
is the original grid position, independent of a printed label/code.

Every entry preserves the literal label, nullable source-only printed code,
source role and raw source hash. `complete_native_object_reference` is a JSON
Pointer into the **complete** pinned contract; its canonical object hash uses
UTF-8 JSON, sorted keys, compact separators and `ensure_ascii=False`.
The pointer resolves the entire object, including separate candidate/contest,
method/admin/null/evidence fields. No source label is normalized into an
approved identity. `geometry_feature_ids` and `approved_current_crosswalk`
are explicitly null. Shared parent references are not child polygons.

`all82parents` preserves the complete ordered priority-child arrays from the
contract. Full and remainder child arrays use complete preferred volume-rank
order. All five parents without priority children remain visible. Each parent
records actual attempted sources, qualified acquired references, discovery
depth and access/vintage/finer-geography gaps. A source failure does not mean
the jurisdiction has no map.

`compatibility.json` references the complete 13,065,430-byte root contract at
`data/turnout/priority-set.json`, SHA256
`782ca7899236ba06e53effee549c4e6845f936c9b4ceea3fecc8828dd9a08c32`.
It is not a projection of selected keys. It retains complete immutable
components, original PDF receipts, full source objects, historical partitions
and all 17 field-companion bodies through exact references. `canonical_resolution`
maps historical logical paths to complete frozen bodies without depending on
mutable peer aggregates. Multiple frozen versions remain explicit. Paths in
the registry are relative to the Mississippi state root; the historical
dependency path printed in the main contract is relative to `data/turnout`.
See [reconstruction](RECONSTRUCTION.md).

`acquisition.json` contains full request/final URLs, redirect chains, response
headers, HTTP status or connection error, UTC retrieval and raw/stored byte/hash
records. `source/*.receipt.json` retain each individual attempt. Body paths can
refer to exact shared originals, which stay read-only. A 200 response can still
be an error, inaccessible-item object or HTML shell. Segments, if present, are
ordered raw bytes with complete reconstruction hashes; no source is truncated.

`geometry-audit.json` separates full archives, native service snapshots and the
Lamar embedded feature collection. Native originals remain authoritative. ZIP
members, CRCs, SHP/SHX offsets, DBF fields/attributes and raw geometry content
hashes are measured. Planar diagnostics use full XY rings in native CRS units;
they do not allocate votes or certify boundaries. Z/M and native true-curve
JSON remain in originals. Curves are not densified. Empty/invalid features and
all attributes remain in the source inventory. `parts` and `positions` count
linear rings/positions; curve geometry is retained by its complete original
JSON plus fingerprint, not represented as zero-sized legal geometry.

Validity is tri-state: true, false or null (unavailable). `topology_evaluated`
includes both valid and invalid linear records. `topology_unavailable` includes
the two true-curve records and one empty Lamar record. Pairwise intersections
use valid, nonempty linear geometry only; skipped records are listed.
Positive areas have no sliver tolerance and are in each dataset's stated
native units squared. No same-vintage certified county outline was obtained,
so legal gaps and legal overlaps remain unknown. Feature labels/IDs and lexical
duplicates are diagnostics, never result-to-geometry crosswalks.

`history/adapter-failure-v1/` preserves the exact failed code and audit.
`adapter-repair.json` documents the constructor fix, unchanged raw fingerprints
and attributes, full-ring preservation and multipart/hole/open-ring controls.
The superseded audit's empty invalid/overlap lists did **not** establish zero
defects: all linear geometry had been skipped by an adapter exception.

`previews/` contains display-only SVG/PNG and a PDF contact atlas. Display
coordinates are rounded to 0.01 viewBox units; source coordinates are unchanged.
The two DeSoto curves and empty Lamar feature are explicitly omitted from
drawings and remain in originals. Contact sheets show 98 shared references,
not 887 invented polygons. HTML has no remote embeds. External primary links
are navigation links only.

`manifest.json` inventories every owned file in `maps/**` and
`precinct-maps.md`, excluding only itself, with exact bytes and SHA256.
`validation.json` records the actual offline checks; default `validate.py`
does not write. No acceptance or mutable coordinator aggregate is a build
dependency. Historical dispatch authority remains external to owned files.
