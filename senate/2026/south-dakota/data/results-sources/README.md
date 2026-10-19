# Official-results source package

Owned report: [official-results.md](../../official-results.md). Inventory: [state plus66 counties](../official-results-sources.csv). [SCHEMA](SCHEMA.md) defines exact original/reference/null semantics. External [acceptance](../coordinator-priority-acceptance.json) is authority by path only; no reverse hash or frozen edits.

This directory contains completed bounded research, not an election-night collector. Acquisition uses Python3 `requests`; extraction/build/validation use the standard library and Poppler for original-PDF checks. No dependency tree/cache is stored. All commands below run from repository root; set `PYTHONDONTWRITEBYTECODE=1` to avoid generated cache files.

Offline rebuild and checks:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/south-dakota/data/results-sources/dependencies.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/south-dakota/data/results-sources/inspect_sources.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/south-dakota/data/results-sources/build.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/south-dakota/data/results-sources/historical_qa.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/south-dakota/data/results-sources/validate.py --write
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/south-dakota/data/results-sources/asset_manifest.py --write
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/south-dakota/data/results-sources/validate.py
```

The final validation is read-only. The manifest excludes only its own file; it includes validation, report, CSV, scripts, plans, complete receipts/parts, parsed derivatives, previews and schema. It separately lists exact frozen read-only dependencies; the authority acceptance is path-only. Hashes are over exact stored bytes. All stored files must be strictly below40,000,000 bytes. Do not regenerate acquisition times or overwrite original receipts to force determinism.

Complete reconstruction, including the large original stored once:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/south-dakota/data/results-sources/reconstruct.py --shared sos-2020-general-county-canvass
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/south-dakota/data/results-sources/reconstruct.py --owned lincoln-ballot --output /tmp/sd-lincoln-ballot.pdf
```

The first command verifies all ordered parts, full gzip and149,141,181 raw bytes without materializing another repo original. `--output /tmp/original.pdf` is available for any original. Full2024 county groups/2022 precinct/recount originals remain in the frozen source graph. The reconstruction script never assumes `asset` exists when `asset_parts` is present.

`render_evidence.py` reproduces the eight bounded whole-page previews from original bytes with Poppler. They were actually viewed; this is not complete statewide scan transcription. The2024 Lincoln PDF has empty text extraction but a readable original image. Raw metadata pins and explicit page/scope notes remain in the historical QA. No OCR repair/rescaling is performed.

Acquisition plans `jobs-01.json` through `jobs-14.json` preserve finite observed URLs/parents and literal form/client constructors. To revisit a plan:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/south-dakota/data/results-sources/acquire.py senate/2026/south-dakota/data/results-sources/jobs-01.json
```

Existing receipts are immutable and skipped, so this does not refresh the evidence. New observations require a new explicit ID/plan and preserve the earlier observation. Three requests maximum run concurrently, with connect/read timeouts15/75seconds. Complete response entities/errors are compressed/split, never capped/truncated. No continuously scheduled request loop is implemented. The POST forms only request public export downloads.

All39 priority-parent HTML requests,38 available county Senate native forms, the statewide Senate form,36 local root links and available election/auditor/detail routes were actually investigated. County form outputs have statewide654-leaf/65-sheet scope despite a656 banner; current turnout JSON sums673. Native identifiers/current joins/cadence/exact remainder remain unknown. Discovery-only rows for the remaining27 county parents are expressly shallower. Both ordinary source failure and HTTP200 challenge/shell conditions are retained. The eight page previews and local history samples do not exhaust later signed ballot/current legal docket scope.
