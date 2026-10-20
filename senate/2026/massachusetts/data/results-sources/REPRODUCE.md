# Offline reconstruction and bounded source reproduction

From the repository root, Python3 standard library suffices for the independent
historical replay, owned build and validation:

```sh
python3 senate/2026/massachusetts/data/results-sources/reconstruct.py
python3 senate/2026/massachusetts/data/results-sources/build.py
python3 senate/2026/massachusetts/data/results-sources/validate.py
python3 senate/2026/massachusetts/data/results-sources/seal.py
python3 senate/2026/massachusetts/data/results-sources/validate.py --sealed
```

Run only `validate.py --sealed` to verify an already sealed package without
changing any output. The other commands write ONLY owned paths. They never
import a producer script or touch Git, maps, coordinator, news or producer files.
The external acceptance is consumed in memory from its path, never copied or
reverse-pinned. The replay rehashes every complete producer dependency and
materializes every complete ledger reference, not sampled references.

The optional source-structure rebuild requires `requests`, `beautifulsoup4` and
Poppler's `pdftotext`; the current run used the existing external
`/private/tmp/fl-official-venv/bin/python` environment. This directory contains
no dependency/cache installation. XLSX XML extraction uses standard `zipfile`
and `ElementTree`. There is no XLSX authoring or formula recalculation.

```sh
/private/tmp/fl-official-venv/bin/python senate/2026/massachusetts/data/results-sources/structure.py
```

`structure.py` reads complete saved bodies, not live endpoints. Its derivatives
can be reproduced offline and compared before resealing. `discover.py` derives
research-parent source choices from the saved directory/search evidence.
`follow.py directory` reconstructs actual clicked department/home destinations;
`follow.py municipal` adds a finite set of up to four actual links for each
previously unplanned priority parent. Current request plans preserve all earlier
requests and their literal source relation. Source matching is research
attribution only; wrong-state/party/irrelevant destinations remain negative
evidence, never Massachusetts result authorities.

For a deliberate network refresh, `acquire.py REQUESTS.json` takes an explicit
finite plan and records every response/redirect entity. Existing receipts are
reused by exact URL. Archive the frozen package first; changing source snapshots
changes research evidence and requires independent review and resealing.
`prepare_current.py` derives the public2026-General-U.S.-Senate query from actual
PD43 dropdowns (`office_id=6`, literal `stage=General`); the November date is
absent from its observed date dropdown. This historical publication probe is
not a live collector and creates no November returns or feed-ID approval.

Web-tool search/navigation responses are frozen representations with their
exact query/click context; rerunning a search may produce different indexed
fragments. They cannot reconstruct inaccessible original HTML/href attributes.
The Secretary local-office directory's403, calendar/advisory access errors,
stale municipal URLs, missing directory links, unsupported browser surface and
uninspected later docket/roster portions are explicit limitations, not zeros.

To reconstruct an original entity, load the indicated receipt, decompress its
`body.path` (or every ordered `body.parts` path), concatenate decompressed parts where present, and compare raw bytes/SHA256 and stored bytes/SHA256. The explicit oversize retry plan is the only cache-bypass retry: it applies only to a prior oversize-body error, retaining the earlier failed receipt. Shared
historical originals resolve state-relative via the frozen individual receipt.
All full tables, scripts, schemas, JSON/CSV/XML fields, PDF pages, original
candidate/control/null positions and nonpriority contexts remain materializable.
