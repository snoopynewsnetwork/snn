# Offline reconstruction and deterministic replay

Run from repository root with the installed Python3.11 environment. Runtime dependencies are Requests for acquisition only, PyShp3.1.6, Shapely, PyMuPDF and Pillow. No dependency/cache directory is stored. Online acquisition scripts are historical one-shot tools and are not needed for offline validation. Re-running acquisition would create new source evidence and requires new IDs; never overwrite an existing original.

A receipt's `parts` array is ordered. Concatenate those exact stored gzip parts, verify their sizes/hashes, gzip-decompress once, and verify raw entity bytes/hash. Keep responses in memory or reconstruct to a temporary destination outside the sealed package. `scripts/acquire.py` exposes `body(id)` for this exact operation. A PDF convenience reconstruction is byte-identical to the response, or the identified member of a CRC-verified ZIP. SHP/SHX/DBF/PRJ and all unknown sidecar bytes remain inside the original ZIP; inspect with Python zipfile without rewriting them.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/colorado/maps/scripts/validate.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/colorado/maps/scripts/build.py --check
```

Both commands are read-only. The validator compares complete historical source bytes/semantics, full maps inventory/order/hierarchy, geometry/attribute/binary/page conservation, every stored receipt/part, all local HTML/Markdown links, strict stored sizes, negative fixtures and exact seal membership/hashes. `build.py --check` reconstructs expected PDF/text/page PNG/SVG/HTML/index/inventory outputs in memory and compares exact bytes. It uses no network or browser. Automated map renders are distinct from the actual selected image-view record.

Preparation commands, used before the final seal, write owned derivatives and QA only:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/colorado/maps/scripts/conservation.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/colorado/maps/scripts/geometry.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/colorado/maps/scripts/service_audit.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/colorado/maps/scripts/build.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/colorado/maps/scripts/visual_samples.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/colorado/maps/scripts/validate.py --write-fixtures
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/colorado/maps/scripts/validate.py --write-report
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/colorado/maps/scripts/seal.py
```

The final step is read-only `validate.py` and `build.py --check` after sealing, with no owned writes afterward. The manifest excludes only itself; no acceptance hash cycle is introduced. `historical-conservation.json` provides complete individual immutable dependencies, not mutable news ledgers or optional coordinator proof. The coordinator alone reviews/publishes; passing worker QA is not self-acceptance.

Native geometry diagnostics do not repair, simplify or delete any original. PyShp points/parts versus lines behavior was explicitly tested before adaptation. Every sourceXY double/part/DBFdescriptor/raw field byte/SHXoffset is audited. Curves are preserved unchanged in complete JSON pages and excluded explicitly from linear-only topology/preview. Positive-area native-unit intersections cannot certify legal slivers/gaps/overlaps without a same-vintage legal outline. Development errors, renderer warnings and source href-resolution alternatives remain in QA/history and source qualifications.

For a single actual response or ZIP member, `scripts/reconstruct.py ACQUISITION_ID /private/tmp/new-file --member EXACT_MEMBER_NAME` verifies complete hashes/CRC and refuses to overwrite a file or write into the sealed package. Omit `--member` for the original entity. Inspect the receipt first: a failed or partial response reconstructs its actual error/HTML/JavaScript body, never a fabricated map.
