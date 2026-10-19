# Offline reconstruction and deterministic replay

From the checkout root, use the installed Python3 environment (requests for acquisition; Pillow, PyMuPDF, Shapely, PyProj and PyShp3.1.6 for map QA). Source/reconstruction validation has no network dependency and never imports producer scripts.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/idaho/maps/scripts/validate.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/idaho/maps/scripts/build.py --check
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/idaho/maps/scripts/reconstruct.py --source state-precinct-native-page01
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/idaho/maps/scripts/reconstruct.py --source franklin-complete-atlas
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/idaho/maps/scripts/reconstruct.py --source data/turnout/source/2024-races-rows.json.gz
```

Those commands reconstruct complete original bytes in memory and print exact SHA/size/ordered chunk witnesses without writing them. `--parts-dir /tmp/idaho-original-parts` optionally emits ordered16MB chunks and a reconstruction manifest. Concatenating chunks in manifest order yields the exact original entity, including PDFs exceeding40MB and the54MB full historical OOXML-cell JSON. Do not write a large combined file into the research package. `--pointer /all_county_constituents/0` with the whole contract path optionally emits a complete source object; this is labeled a semantic derivative, not original whole-file bytes. Entire referenced files remain authoritative and reconstructable.

`verify_history.py` checks all frozen contract/first-pair/review/complete-companion pins, both full producer seals,42 complete root semantics and5169 complete recursive object references, not selected vote fields. The original whole compressed bodies and reconstructed hashes are checked before semantics. `native.py` checks all original native pages, attributes, IDs/metadata/CRS and coordinates. `shapefile_qa.py` checks every original ZIP binary record/attribute/double. `geometry.py` creates the separately labeled native SVG/PNG derivatives and diagnostic topology. `pdf_qa.py` renders every page of each acquired PDF; all originals remain unchanged. These write QA outputs only when deliberately invoked as authoring scripts; final `validate.py` is read-only.

`build.py --check` regenerates the full inventory and offline HTML in memory, requiring byte-identical output. `--write` is an explicit pre-seal authoring operation. Source receipt times are immutable observations; new online downloads should use new receipt IDs rather than modifying originals. Optional preparation freezing and online acquisition scripts are historical/reacquisition aids, not build prerequisites. No current peer worker or mutable source/news ledger is required.

`manifest.json` seals every owned physical file, including this report's parent `precinct-maps.md`, scripts, receipts, full original bodies/chunks, all previews and QA/negative fixtures. Only the manifest itself is excluded from owned membership. Frozen external individual references have separate pins; the acceptance authority remains path-only. Run final validation after seal without writing another QA file; its stdout is the final read-only witness.

The historical baseline seal includes an original30714-byte newsroom receipt-ledger pin. Its entire exact pinned body is frozen once as `source/frozen-original-receipt-ledger-*.json.gz`, with explicit mapping in `source/frozen-reference-overrides.json`. Full first-pair reference validation uses that immutable witness rather than reading the current ledger. This is complete byte-preserving metadata, not a selected projection; source producers and the live ledger are untouched. Individual original source bodies remain separately pinned.
