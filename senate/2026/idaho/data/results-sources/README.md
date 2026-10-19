# Idaho official-source evidence package

Completed bounded research for coordinator review; no November feed/roster/geography/cadence/remainder/probability approval. The [report](../../official-results.md) and [45-row state/county inventory](../official-results-sources.csv) explain the findings. Research scope is fixed by [external path-only acceptance](../coordinator-priority-acceptance.json).

## Source organization

- [source-index.json](source-index.json): all451 actual observations, discovery/parent/constructor and immutable receipt/body references. Full headers/redirects/error fields remain in `receipts/<id>.json`; gzip bodies are content-addressed by reconstructed SHA256. The451 observation count includes all failures and intentionally retained researcher errors, not451 working sources.
- [initial-jobs.json](initial-jobs.json) and other `*-jobs.json`: bounded request specifications. Run them only deliberately for a new dated research capture; this package is not a polling loop. Existing receipt IDs are immutable and acquisition reuses them. New captures need new IDs.
- [navigation.json.gz](navigation.json.gz): complete base-aware HTML anchor navigation and main text. Raw original HTML remains authoritative. Initial receipt convenience links/scripts did not honor every HTML base; [document-base-corrections.json](document-base-corrections.json) identifies malformed Gem requests. [constructor-corrections.json](constructor-corrections.json) separates the33 incorrectly election-UUID-based404 download attempts from correct successful jurisdiction-UUID downloads. [search-form-correction.json](search-form-correction.json) records the inferred initial search action and the actual named-input public search followup. These are researcher errors, not publisher outages.
- [extraction-index.json](extraction-index.json):62 complete PDF text/OOXML derivations. Raw PDF/XLSX entities remain complete. Extracted native exports retain every sheet, ZIP member inventory, shared string and original row/cell/header/type/style/raw value/formula/null. The state export is fully retained, not a selected-field sample. PDF text is an aid, with page boundaries; visual readings below establish layout/strikeout meaning.
- [parent-investigations.json](parent-investigations.json): state plus44 complete county research records;32 have full native exports. [priority-investigations.json](priority-investigations.json) has exactly528 investigations in accepted canonical order; [remainder-monitoring.json](remainder-monitoring.json) retains457. [all985-hierarchy.json](all985-hierarchy.json) preserves all985 identities and44 grouping maps. [coverage.json](coverage.json) distinguishes source-native dispatch from county sensitivities.
- [historical-source-graph.json](historical-source-graph.json): complete immutable individual references, reconstructed/semantic identities,42 root fields and5,169 full source/admin object pointers. It preserves every29 actual acceptance-listed companion (20 turnout +9 baseline) and the complete frozen producer graph. No copied acceptance hash, reverse pin or approval cycle is created.
- [reused-ballot-receipts.json](reused-ballot-receipts.json): four complete individual observations snapshotted from existing preparation, with exact immutable body references. No duplicate592,959-byte LD24 original. Historical producer provenance may mention old aggregate/review paths, but appendable news aggregates/optional coordinator reviews are not active build dependencies. The relevant individual receipts and complete original bodies suffice.
- [current-candidate-scope.json](current-candidate-scope.json): four printed LD24 sample names, legal references and explicit false statewide/exhaustiveness/ID flags, separate from historical candidate data.
- [public-response-schema.json](public-response-schema.json), [SCHEMA.md](SCHEMA.md): full observed JSON paths/types and interpretation rules. Original arbitrary keys, nulls, administrative scopes and errors remain in bodies, not silently discarded.

## Independently viewed primary pages

[LD24 page1](rendered/TwinFalls-LD24-page1.png) was rendered from the exact reused original and visually checked. The2023 student-ID deletion is struck through in the actual [enacted chapter27 page](rendered/enacted-2023-vol1-effective.png), rather than a current option inferred from extracted text. [2024 state-canvass effective clause](rendered/enacted-2024-vol2-effective.png) and [2025 county-canvass effective clause](rendered/enacted-2025-vol1-effective.png) were also viewed. [Enacted review](enacted-effective-review.json) records complete bounded chapter text and exact PDF page numbers; the full volumes remain in acquired bodies.

Source clocks differ: retrieval UTC, HTTP Date/Last-Modified and publisher asOf/lastUpdated are separate. The primary API uses explicitZ timestamps and null next-update/method fields. Browser rendering may be local time. An HTTP200 shell, challenge, meta refresh or old election does not establish current returns. Full bodies preserve these cases.

## Reproduce offline and validate

From repository root, using Python3.11+:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/idaho/data/results-sources/rebuild.py --check
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/idaho/data/results-sources/validate.py --sealed
```

`rebuild.py` delegates to owned `build.py` and compares every generated byte, without network or mutation. Omit `--check` only before sealing to rebuild the9 deterministic products from retained evidence. `validate.py` independently parses original OOXML, native export XML, exact source receipts, complete recursively pinned companion/root/object semantics, all44/32/528/457 coverage, links, negative fixtures and final owned membership/hash seal. It imports no first-pair producer code. Default validation and `--sealed` are read-only; `--write` writes a dated-stage QA result before sealing. [validation.json](validation.json) is the last written pre-seal result; final post-seal verification prints its result without modifying that sealed report.

For new acquisition, `acquire.py` requires `requests` and `beautifulsoup4` in an external environment. The session used requests2.32.5 and BeautifulSoup4.15.0; no dependency or cache directory is delivered. `navigation.py` uses BeautifulSoup. `extract.py` uses the standard library plus system `pdftotext -layout`; renders used `pdftoppm`. Neither network nor those optional HTML/PDF executables is required for final read-only validation of retained bodies/OOXML or deterministic research-output replay. `freeze_inputs.py` writes only owned reference snapshots; frozen source bytes are read-only. Existing extraction entries are checked against their original hash and reused; the independent validator replays original fields independently of that cache path.

Full raw entity reconstruction:

```python
import gzip, hashlib, json
from pathlib import Path
root = Path('senate/2026/idaho/data/results-sources')
r = json.loads((root/'receipts/data-ada-county-id.json').read_bytes())
stored = (root/r['stored_path']).read_bytes()
raw = gzip.decompress(stored)
assert len(raw) == r['raw_bytes']
assert hashlib.sha256(raw).hexdigest() == r['raw_sha256']
assert hashlib.sha256(stored).hexdigest() == r['stored_sha256']
```

All stored files, including compressed raw bodies, are strictly below40,000,000 bytes. Reconstruction can exceed that limit; it never substitutes a reduced projection for a full original. [manifest.json](manifest.json) seals exact owned membership and individual complete external references; the manifest excludes only itself to avoid a self-hash cycle. Seal only after substantive outputs and QA are complete, then run `validate.py --sealed` and `rebuild.py --check` read-only. Coordinator alone reviews/publishes.
