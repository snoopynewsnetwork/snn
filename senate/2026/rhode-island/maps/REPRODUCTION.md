# Offline reproduction and final audit

From `senate/2026/rhode-island/`, with the existing Python3/Pillow/Shapely/Poppler environment:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B maps/scripts/replay.py
PYTHONDONTWRITEBYTECODE=1 python3 -B maps/scripts/audit_historical.py
PYTHONDONTWRITEBYTECODE=1 python3 -B maps/scripts/audit_publications.py
PYTHONDONTWRITEBYTECODE=1 python3 -B maps/scripts/reproduce.py
PYTHONDONTWRITEBYTECODE=1 python3 -B maps/scripts/validate.py
PYTHONDONTWRITEBYTECODE=1 python3 -B maps/scripts/final_audit.py
```

All are read-only for production when invoked as above. `reproduce.py` makes an isolated temporary state tree; exact individual originals, frozen external source inputs and owned request/configuration/manual-scope files are copied or referenced there. It independently rebuilds native audits/linear previews, everyPDF page/layout/metadata, full source observations/static atlas/report, compares every deterministic generated output byte, and deletes the temporary tree. It does not reacquire URLs, run a producer writer/import, load current active-peer files or optional coordinator review aggregates, change source flags, install dependencies, or write caches. Full external authority is read only from its fixed path, wholly in memory. The authority body/digest is never a downstream file or reverse pin.

`replay.py --write`, `audit_historical.py --write`, `audit_publications.py --write`, `validate.py --write`, `reproduce.py --write`, `audit_native.py`, `render_pdfs.py`, `build.py` and `make_report.py` are authoring commands, **not post-seal commands**. `seal.py` writes `final-seal.json` first and `manifest.json` last once, refusing an existing seal/manifest. No owned bytes are changed after the final read-only audit. The manifest includes every owned file plus `precinct-maps.md`, excluding only itself. No validation/seal object reverse-pins the current manifest.

Network acquisition is deliberately separate in `acquire.py`, `discover.py`, `follow.py`, `local_deepen.py`, `native.py`, `supplement.py` and `finish_links.py`; their original request objects preserve actual operation provenance. Scripts never overwrite an existing named request. Future retrievals may differ and require a new observation name. Bounded exploration included error/403/timeout entities and incidental material, all classified honestly; no whole entity was truncated or silently converted to geometry. No browser was attempted. The acquisition index is an index, not a replacement for complete requests/entities.

To reconstruct one complete publication without storing another original in this package, call `original(last(request))` from `common.py`/`acquire.py`, or concatenate the `gzip.decompress` result of its ordered part paths in `requests/ID.json`. Check raw bytes/SHA against that exact hop. Every stored part is strictly<40,000,000 bytes; originals appear once by content hash. Full original PDF bytes existed only in temporary rendering directories, which are removed. Rendered PNGs and complete layout text are separately labelled derivatives.

Native metadata/IDs/counts are paired before/after, requests are<=50 IDs, exact requested/returned sets are recorded, and original native fields/coordinates are preserved. `qa/native-audit.json` documents geometric exclusions and source differences. No acquiredSHP/DBF/SHX originals means no binary audit claim. No ring closure/repair/hole reassignment, outputCRS, precision setting, quantization, simplification or offset paging is used. GEOS diagnostics are confined to already-closed finite valid single-ring polygons; stroke previews preserve all linear native vertices. Installed PyShp constructor inspection remains evidence only.

[Schema](SCHEMA.md), [source graph replay](qa/authority-replay.json), [original reconstruction](qa/historical-reconstruction.json), [native audit](qa/native-audit.json), [allPDF rendering](qa/pdf-rendering.json) and [actual manual visual scope](qa/manual-visual-review.json) explain the exact limits. The full historical external source packages must be present at their individually pinned paths for reproduction; this maps directory is not a portable replacement for148 original entities or the877 historical bodies. No county or label join, November approval, legalnative80/write-in inference or live probability model is supplied.
