# Acquisition and authority

The [complete receipts](acquisition.json) are the authoritative request log.
The [shared reference ledger](shared-map-references.json) copies complete
receipts and pins the exact existing original bytes before read-only reuse;
later changes to the coordinator ledger are not a build input. No historical
PDF, ZIP or canonical source body is duplicated into this directory.

MARIS's [political index](https://maris.mississippi.edu/HTML/DATA/Political.html)
links its [post-2020 precinct page](https://maris.mississippi.edu/HTML/DATA/data_Political/UpdatedVotingPrecincts.html).
Only 13 county archive links are active. All 13 actual ZIPs are present in the
shared originals, including the successful Choctaw retry. Exact disabled links
in the raw primary HTML were attempted separately: 68 attempts, 64 HTTP404 and
four connection failures. Pearl River has no county archive link in that list.
Disabled links are discovery evidence, not advertised coverage or adoption.
MARIS's statewide 2020 archive is an actual 1,834-feature Census VTD reference.
Its metadata PDF credits Census and explicitly distinguishes statistical
boundaries from legal descriptions. The post-2020 page also contains unrelated
DFIRM boilerplate; that text is not precinct-specific metadata.

County followups were bounded. DeSoto's official elections page links the app
whose complete configuration names the working `Election_Info/MapServer/1`.
The similarly named FeatureServer returns an HTTP200 error. Harrison's service
is county-hosted and credits the county Board, Circuit Clerk and GIS; its
description is tied to the 2010 Census. Lamar's county page links its webmap,
which contains a complete embedded precinct collection; the underlying original
shapefile and precision history were not obtained. Lafayette and Pearl River
supplied actual polling-location PDFs, not polygons. Specific failures and
uncompleted downstream discovery for other county apps remain in the index.

`acquire_service.py` records metadata/count/allIDs first, then complete batches
of at most 50 IDs with `outFields=*`, `returnGeometry=true`, `returnZ=true`,
`returnM=true` and `returnTrueCurves=true`. It requests no `outSR`,
`geometryPrecision`, `maxAllowableOffset` or quantization. It rejects JSON
errors/transfer-limit flags, checks exact IDs/attributes, and records post-ID,
count and metadata snapshots. DeSoto154 and Harrison49 reconcile. Unavailable
edit clocks and server default-precision fidelity remain explicit; stable
metadata/IDs do not rule out unclocked concurrent coordinate edits.

`acquire.py` is append-only by receipt ID, with complete lossless bodies,
errors and deduplication against existing exact hashes. Refreshes must use a
new ID and preserve the old receipt. It has no scheduler or live collector.
The successful network requests required the authorized network-capable shell;
the initial sandbox DNS failures are retained. No access challenge was bypassed.
