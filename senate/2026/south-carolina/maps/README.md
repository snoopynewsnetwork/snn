# South Carolina offline precinct-map package

Open [index.html](index.html) directly from disk. It has exactly 17 ordered county preview/download entries and all 46 counties in the inventory. Actual PDF maps, native Esri JSON entities and separate preview derivatives are local; no remote viewer is required.

The complete frozen contract is preserved as a parsed object in `contract-compatibility.json.gz`. The exact original bytes remain at `../data/turnout/priority-set.json`, pinned by the external acceptance record. All county/source objects, ordering, raw locators, nulls and unavailable/administrative scopes remain unchanged. Literal-name comparisons are diagnostics, never geographic joins.

Rebuild and validate offline from repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/south-carolina/maps/scripts/rebuild.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/south-carolina/maps/scripts/validate.py --verify-manifest
```

`acquire_all.py` reproduces the named public acquisition chain and reuses existing captures. It does not refresh an existing capture, run a collector or overwrite a historical response. New observations require new names and a reviewed snapshot. `acquire.py` records GET URLs, redirects, UTC retrieval, status/headers/errors, decoded entity byte hashes and stored lossless bytes. Large entities are split only at documented byte offsets and reconstructed in recorded order. Current stored entities need no splitting. Already retained identical peer bytes are reused by reference in the capture metadata; Lexington's November notice is an external immutable original.

`build_geometry.py` records exact original feature slices, byte offsets and hashes, complete count/ID sets and topology; subsets copy feature lexemes unchanged. Native CRS is EPSG:6570 / ArcGIS103146, international feet, with area in square international feet. `build_alternatives.py` audits three separate county services and their own CRS/units. No geometry repair, curve linearization, vote allocation or county reassignment occurs. `inspect_sources.py` inventories and renders every actual RFA PDF page; `build_supplements.py` renders current/historical rosters, which do not constitute polygon maps.

`manifest.json` inventories every owned file plus `../precinct-maps.md`, excluding only the manifest itself. Its external inputs are pinned individually. `validation.json` is deterministic and has no manifest-hash dependency. Rebuilding first validates, seals the manifest, then independently verifies it. Original gzip CRC/trailers and both original/stored hashes are checked. No asset reaches 40,000,000 bytes. Dependencies use existing Python requests, Shapely, pyproj, PyMuPDF, Pillow and Poppler; no dependency tree or bytecode cache is shipped.

Read [the report](../precinct-maps.md), `scope-notes.json` and `qa/visual-review.json` for remaining baseline/current/November scope gaps, source-specific administrative and unavailable cases, blocked URLs, publication-label discrepancies and retained geometry defects. Actual current publication does not establish legally approved November reporting membership. No Census VTD substitute, exact outstanding-vote estimate or approved result-unit crosswalk is supplied.
