# New Jersey map evidence package

Bounded original-source research is complete, with current/physical/legal equivalence expressly unestablished. Open [atlas.html](atlas.html) directly from disk. It requires no server, account, CDN, network request or installed browser automation. The [report](../precinct-maps.md), [575-row inventory](manifest.csv), [complete inventory objects](inventory.json), [21 full parents](parents.json), [schema](SCHEMA.md) and [validation](qa/validation.json) explain scope.

The atlas retains all 575 source objects and all 24 frozen contract fields, 233 priority / 342 remainder, complete parent objects and source/rank/priority/remainder child arrays, all four original-derived historical candidate scopes, complete local map/companion catalogs and receipts, and all 6,749 native attribute records. Source and parent buttons display complete JSON, without truncation. Native geometry remains in complete original responses. The local gzip picker displays the complete JSON original, including all geometry; [the offline inspector](scripts/inspect_original.py) also reconstructs it. Browser layout/native file-selection UI were not exercised; 14 tests run the actual JavaScript with a minimal Node DOM harness, including actual gzip decoding/full original display. There was no Chrome permission loop.

`originals/` contains complete response bodies once by SHA-256, losslessly gzipped. Receipts retain all redirects, URLs, literal href/parent, query/body, UTC, full returned header lists, HTTP status and errors. Transport identity was requested. `raw` means the complete received response body, excluding HTTP transfer framing; content encodings are retained in headers and decoded only for parsing. Body splits, if necessary, are ordered exact gzip-stream chunks below 40,000,000 bytes. No completed response is truncated. One initial pre-instrumentation DNS probe is separately retained in `qa/bootstrap-observations.json`; its missing UTC/headers are explicitly unrecorded, not invented. Original dependency bodies outside this ownership are reused read-only by individual hash, with complete 417-entry receipt bodies frozen in `original-dependencies.json.gz`; no mutable news manifest or producer writer is imported.

The full Census ZIP has seven members and 6,361 records; its independent binary audit checks all members/CRC/schema/DBF rows/SHP-SHX offsets/bounds/parts and every 2,302,234 XY IEEE754 value against the inspected installed reader's explicit points/parts path. That path does not use the constructor's optional ring-closing `lines=` branch. Null/empty/orphan/curve cases are preserved, never repaired. Native service acquisition retains complete pre/post service and layer metadata, counts/all IDs and 136 exact batches of at most 50 IDs. State and Burlington SR forms are preserved separately: Burlington extent metadata has tolerance/origin/unit fields absent from returned batch SR; all returned SR fields agree. Diagnostics are linear/native-unit diagnostics, not legal gap/overlap/sliver certification.

All 215 bounded acquired PDFs / 323 physical pages have complete automatic previews and text. Scanned empty extraction is not missing pages or zero data. [Visual review](qa/visual-review.json) states exactly which complete pages, footnotes and native previews were actually viewed; other renders are automatic only. MuPDF emitted color-profile warnings while producing complete page images; no original was changed. Upload date, printed map date, revision date, signature date, HTTP Last-Modified and retrieval UTC remain distinct.

Run from this directory with Python 3.11, requests, PyShp 3.1.6, PyMuPDF, Pillow and Node available:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/reproduce.py
PYTHONDONTWRITEBYTECODE=1 python3 scripts/seal.py
PYTHONDONTWRITEBYTECODE=1 python3 scripts/verify_seal.py
```

Reproduction is offline and reads originals plus complete external historical inputs; it never runs a producer writer. Network scripts are historical acquisition recipes only and are not called by reproduction. They reuse existing immutable receipts; a new observation requires a new ID. Acquisition order was initial/state/county navigation, bounded linked map libraries, advertised service metadata/query forms, complete native batches, full item metadata and bounded final observed links. Acquisition is now closed. Do not turn these scripts into a collector.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/inspect_original.py receipt state-election-service-batch-0000
PYTHONDONTWRITEBYTECODE=1 python3 scripts/inspect_original.py native state-election-service-batch-0000 0
PYTHONDONTWRITEBYTECODE=1 python3 scripts/inspect_original.py materialize map-original-045 /tmp/paramus.pdf
```

`qa/reproduction.json` records exact before/after deterministic product hashes. `qa/negative-fixtures.json` records 25 meaningful corruption, unsafe-parameter and invalid-geometry preservation fixtures. `final-seal.json` includes validation/reproduction hashes without a manifest reverse pin. `asset-manifest.json` lists every owned file, including report, validation, reproduction and final seal, excluding only itself. The final read-only verifier checks the exact complete set.

Authority is external path only: `data/coordinator-priority-acceptance.json`. Its body/hash is not copied or reverse pinned. The optional coordinator native-map proof is not a build dependency. Coordinator alone reviews, accepts and publishes; no Git action occurred here. Current/legal/finer crosswalk exhaustion is an explicit external qualification, not unfinished owned research.
