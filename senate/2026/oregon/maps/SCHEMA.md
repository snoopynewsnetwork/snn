# Oregon map evidence schema and reproduction

This package is qualified, bounded geographic research. The external [source authority](../data/coordinator-source-research-acceptance.json) is consumed fully in memory and referenced by **path only**. Its bytes/hash/body are never copied or reverse-pinned into owned outputs. The [frozen turnout contract](../data/turnout/priority-set.json) and every other original retain their own exact independent byte pins. Producer files and false/null approval flags remain untouched.

## Full original source tree

[Source replay](qa/source-replay.json) independently checks all23 contract roots,1994 whole companions,495672 recursive objects across four complete ordered ledger partitions,5029 fixed whole-file pins and5261 historical records (4961 distinct original path+hash identities). The map implementation records1012011 checks; this is its own check accounting, excluding optional coordinator review-file dependencies. No full body is replaced by a vote-only/priority projection. JSON preserves whole dictionaries/arrays, candidates, parties, headers, nulls, masks, methods, admin, controls, hierarchy and raw positions. CSV is parsed as a full header+ordered-row array with every cell; JSONL preserves every ordered complete record. Each ledger's complete decoded bytes/hash and every container's pointer/type/length/recursive semantics are verified.

[Original reconstruction](qa/original-reconstruction.json) independently restores113 complete original entities from48 fixed receipts, including72 ZIP members, and reconstitutes37 individual original receipt bodies. ZIP archives and all members are byte/CRC checked. Ordered2022 abstract ranges reconstruct the whole original; a range alone is not labeled the whole PDF. Complete ZIP membership is not historical normalization closure. The separate262-page Benton2020 federal original and189-page2022 original remain separate from the115-page2020 ZIP state-office member. Source scans/OCR/visual transcriptions remain original-position evidence, not spatial IDs or newly repeated OCR reads. Both producers' exact historical unavailable/closure objects and Douglas differences remain available through the full original tree.

[The resolver](scripts/resolve.py) first locates an exact captured historical **original path+expectedSHA**, including ordered tar/gzip containers, rather than substituting a later current file. Current files are used only when their own exact authority pin matches the requested identity. Its optional JSON pointer returns the entire object; CSV headers/rows and full JSONL records are supported. No producer imports/writers, mutable news aggregate, current helper, optional current review or unfinished peer directory is required.

## Inventory and full objects

[inventory.json.gz](inventory.json.gz) is deterministic UTF-8 JSON in gzip with mtime0. It has36 parent records,510 known-source context references and31 separate unavailable parent cases. No541-unit inventory exists. Each reference has the full contract file's exact path/bytes/hash, an RFC6901 pointer and an independently calculated full-object semantic SHA256. Parent arrays preserve every source constituent and nonadditive administrative companion. A source context's entire original object and the whole original parent are displayed in the [static atlas](index.html); none is reduced to candidate vote totals.

The full source tree is referenced through the external authority path and four independently verified original ledger references. Referenced huge entities remain stored once in their original ownership scope. The atlas's JSON text is an escaped display derivative. Its40 static HTML documents include36 county pages, all-parent, known-only510, unavailable31 and full-PDF-page views. County/source-scope navigation supplies static filters; [known.html](known.html) preserves the entire qualified known-only order. This order is not canonical statewide priority. No JavaScript, HTTP server, remote fetch or browser rendering is required. Offline HTML parsing tests actual generated nodes, filter membership, ordering, full-object equality, local links/fragments and escaping. No browser-specific layout or JavaScript execution claim is made.

Each parent and source-specific context retains access/vintage/CRS/physical/legal/finer-ID limitations. Unknown native membership stays null, not zero. The canonical complete statewide order, top15,minimum80,priority,remainder stay null. All current/legal/leaf/result-ID/eligible-write-in/live/cadence/outstanding/forecast/calibration qualifications remain false or unknown.

## Acquisition and exact bytes

[requests/](requests/) holds404 map-owned observations, including failures and full redirect chains. [references/navigation-fixed.json](references/navigation-fixed.json) fixes115 individually original-verified public state/county navigation observations reused read-only. The offline build reads only these exact individual receipts/bodies, never the optional official package's current aggregate, writer or report.

Requests retain method, requested and final URL, literal parent relation, role, start/finish/entity UTC times, supplied request headers, status, complete response headers/source clocks, errors and complete body references. Reused observations keep their original capture times; reuse does not claim a fresh HTTP observation. HTTP Date/Last-Modified, ArcGIS editing/item time, ZIP member time and printed map date are distinct clocks; an unspecified source timezone remains unspecified. No source clock is silently converted into an election/legal vintage. TLS/DNS/no-response failures have no invented headers or bodies. The Columbia countywide PDF stream-read timeout occurred before entity persistence: its HTTP status/headers were not retained, no complete body was acquired, and this metadata limit remains explicit. No TLS bypass, credentials, login/challenge retries, endpoint/ID guessing or outreach occurred. Literal href spaces were percent-encoded solely for HTTP URL syntax.

Each complete body is gzip encoded losslessly with ordered parts, each **strictly less than40000000 bytes**. `raw_bytes/raw_sha256` describe original response-body bytes; `stored_bytes/stored_sha256` describe the complete compressed stream. Each part has path/bytes/SHA256. Join parts in listed order, verify stream size/hash, decompress once and verify raw size/hash. Identical body streams share content-addressed parts. No partial/oversized/HTML download is labeled an acquired SHP/PDF/native geometry; HTML authority/error entities are labeled by role. The transformed Wheeler image is only a literal display derivative; no full-size URL was invented. The linked Multnomah2024 Drive page is HTML, not an acquired SHP ZIP.

```sh
# From the repository root: restore a complete map original into temporary storage.
PYTHONDONTWRITEBYTECODE=1 python -B senate/2026/oregon/maps/scripts/restore.py \
  maps/requests/mapchain-032-net.json --output /tmp/oregon-union-precincts.zip
# A complete individual PDF inside the retained original107-member ZIP:
PYTHONDONTWRITEBYTECODE=1 python -B senate/2026/oregon/maps/scripts/restore.py \
  maps/requests/follow-search-multnomah-precincts-40.json \
  --member '2024 Precinct pdfs/pct_4501_2024.pdf' --output /tmp/oregon-pct4501.pdf
# Resolve any exact historical original reference; values come from its original pin:
# PYTHONDONTWRITEBYTECODE=1 python -B senate/2026/oregon/maps/scripts/resolve.py \
#   ORIGINAL_PATH EXPECTED_SHA256 --output /tmp/restored-original
```

`navigate.py`, `native.py` and `fallback.py` are research acquisition writers, **not** offline build dependencies. Their fixed plans/actual receipts preserve the literal county/GIS/app/item/webmap/service/layer chain. No automatic network refresh is part of reproduction.

## Native service and geometry roles

All18 complete native snapshots retain full pre/post service **and** layer metadata, count and allIDs. Complete geometry/attribute queries request `outFields=*`, geometry, Z, M and true curves with explicit object-ID pages of at most50. All54 page requested/returned ID sets, uniqueness, count and attributes independently reconcile;2174 feature records are **nonadditive across overlapping layers/vintages**, not a unique precinct count. No outSR/outCRS, coordinate precision, quantization, simplification, generalization, offset paging or source repair was used. Full pre/post comparisons include service extents; all18 observed comparisons are unchanged. These bounded intervals are not atomic snapshots or November approval.

Exact native JSON bodies retain original numeric spellings, all attributes, null/empty geometries, Z/M and true-curve structures. CRS is the complete original layer/service spatialReference; a query may repeat only its WKID/WKT identity and omit service tolerances. Such metadata is retained, not rewritten. Benton split layer returned66 complete attribute records with no geometry or query CRS; that absence is preserved, not filled from another layer.

[Geographic diagnostics](qa/geography.json.gz) preserve every linear source ring position/multiplicity and test finite XY, closure, short rings and closed-ring simplicity.246 curved feature records,66 null/missing geometries and4 empty/nonpolygon geometries are excluded from unavailable linear preview/topology scopes; these totals include overlapping source layers.38 nonsimple **rings**, including six in the historical Multnomah SHP, are diagnostics, not counts of legally invalid precincts. Source rings are never closed, repaired or reinterpreted as orphan holes. No polygon-intersection/legal-outline test or certification of gaps, overlaps or slivers was performed. Historical county outlines are not same-vintage legal precinct outlines. No spatial allocation of any vote, registration, ballot or returned-ballot scope occurs.

SVG previews are stroke-only, fitted independently within1200x900, with displayed coordinates rounded to0.01 viewBox units and no basemap. Every source position is still processed, including consecutive repeats; no source geometry is simplified. The original native data remains separate and exact. Curved features are excluded whole, so blank areas do not represent legal geographic gaps. Selected SVGs are rasterized through PyMuPDF only as inspection derivatives.

## Actual binary originals

[binary-summary.json](qa/binary-summary.json) references four actual ZIP originals with128 members. Three ZIPs contain actual SHP layers: Census2010 Oregon county36 records, Multnomah2022 splits196 and Union21. The fourth contains107 complete map PDFs. Every member CRC and decoded size/hash is checked. For all253 SHP records the independent parser checks SHP/SHX headers/file lengths, every record/index offset/content length, shape type, part indices and every bbox; PyShp comparison checks every XY double by its raw IEEE754 bytes.416896 XY values and5183 DBF cells are checked. DBF schema, record/deletion positions, cell raw hashes/values and trailer bytes are retained; raw original bytes are reconstructable exactly.

[Installed PyShp3.1.6 constructor](history/pyshp-constructor.txt) was inspected before adaptation: `points`/`parts` preserve raw positions/multiplicity, while `lines` auto-closes polygon rings. The adapter uses only points/parts, never GeoJSON orphan-hole conversion. Open/short/null source geometry would remain unmodified; no such SHP rings were found in these actual three layers. The negative fixture demonstrates the installed constructor distinction on an open ring. **JSON-only layers have no SHP/DBF/SHX audit claim.**

## PDFs and actual manual scope

[renders/index.json](renders/index.json) preserves each complete PDF's request/member identity, raw size/hash, full metadata/text, page dimensions and every render's exact pin.135 whole acquired PDFs, including all107 map-archive members, are automatically rendered in full:416 pages with Poppler at max1600pixel side. Every source PDF and rendered page is independently re-opened/count/dimension/hash checked offline. [All pages](publications.html) are directly viewable. Full originals and previews are separate.

[visual-review.json](qa/visual-review.json) records the exact six original map pages and five geographic previews actually inspected. All other pages were automatically rendered and checked, not manually viewed. Dense pages were inspected at max1600pixel side; not every small label/cell was manually read. There was no browser render or permission-loop claim.

## Deterministic replay, fixtures and seal

Python3.11, Poppler, PyMuPDF, Pillow, Shapely/GEOS and installed PyShp are used as recorded in proofs; no dependency/cache directories are created. Every Python command uses `-B` and `PYTHONDONTWRITEBYTECODE=1`.

```sh
# Complete read-only offline reproduction after sealing; no network, no producer writers.
PYTHONDONTWRITEBYTECODE=1 python -B senate/2026/oregon/maps/scripts/audit.py
```

The audit replays the full original source tree and historical bodies, all original map response parts,113 source-original roles/72 archive members, all native pages/metadata, every binary member/cell/XY, complete PDF/text/page assets, full parent/context inventory, actual static DOM filters/order/full objects/escaping, deterministic atlas/previews and every owned file/link/size/hash. [Fixtures](qa/fixtures.json) mutate only memory and exercise omitted methods/admin fields, missing source contexts, null-to-empty dispatch, eleven/213/synthetic541 substitutions, old-body substitution, missing/duplicate IDs, omitted non-ID attributes, forbidden output transformation, service-extent-only changes, corrupt ZIP CRC/SHP index offsets and omitted history membership.

Packaging order is acyclic: generate report/docs/proofs/history/validation, write `finalseal.json` pinning fixed proofs, then write `asset-manifest.json` **last**. The manifest enumerates every owned report, original part, script, atlas, render, validation, history, proof and finalseal, excluding **only itself**. Finalseal/validation do not reverse-pin the manifest. The final command is the read-only membership/hash/reconstruction audit; its actual stdout/manifest pin is sent externally, with no owned write afterward. Coordinator alone reviews, accepts and publishes.
