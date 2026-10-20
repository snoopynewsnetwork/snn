# Reproduce the Massachusetts baseline package

Work from the repository root. Python3.11+ with `beautifulsoup4==4.15.0` is needed for original HTML extraction and `requests==2.34.2` only for acquisition verification/fetching. The arithmetic CLI itself uses the standard library. Create any environment outside the repository, for example under `/private/tmp`; retain no dependency/cache tree in these outputs. Recorded execution used `/private/tmp/fl-official-venv/bin/python`.

Run the entire offline rebuild, then validate the completed seal:

```sh
PYTHONDONTWRITEBYTECODE=1 /private/tmp/fl-official-venv/bin/python senate/2026/massachusetts/data/baselines/reproduce.py
PYTHONDONTWRITEBYTECODE=1 /private/tmp/fl-official-venv/bin/python senate/2026/massachusetts/data/baselines/validate.py --sealed
```

Offline reproduction uses exact source bodies pinned in `source/shared-originals.json`, frozen browser representations, and owned snapshots of the already compared actual turnout original-first-v1 bodies. It never fetches a mutable news/peer manifest. Original-source extraction precedes derivative comparisons; the immutable first-freeze hashes must remain unchanged. The reviewed shared primary preflight script is loaded read-only, with every output redirected here and a temporary manifest constructed from frozen receipts; no shared writer is run in place. Its script hash is pinned in final assets. Original source positions include every supplied candidate and control field, not just A/B. Native CSV headers/labels never establish current geometry.

`reproduce.py` independently extracts raw result files, verifies ancestor/download chains, builds all18settings/36targets, extracts the qualified supplementary statistics representations, runs synthetic calculator cases, checks the owned exact peer snapshots, regenerates the report and validates. Outputs are deterministic; gzip uses mtime0. It compares pre-existing output hashes rather than resealing changed data. The final asset manifest and immutable pre-peer witnesses are not rewritten by reproduction. A deliberate package revision needs a new reviewed seal, not silent acceptance of changed hashes.

`acquire.py` defaults to verifying already retained own HTTP responses. `--fetch` makes bounded GETs only when a receipt is absent, preserving redirects/headers/status/UTC/body hashes. New captures belong in a separately named `--folder`; never overwrite an immutable witness. Browser representations and blocked403 bodies are distinct. Historical public-form/view/download URLs are checked in `verify_chains.py`; the exact2024view was supplied as official launch context. No guessed2026feed exists. The original Secretary registration PDFs/XLSX/method bodies remain inaccessible; those gaps survive rebuilds.

The calculator runs offline:

```sh
python3 senate/2026/massachusetts/data/baselines/calculate.py live senate/2026/massachusetts/data/baselines/synthetic/known-final-denominator.input.json
python3 senate/2026/massachusetts/data/baselines/calculate.py historical senate/2026/massachusetts/data/baselines/scenarios/2024-senate-own-native-input.json.gz
```

The known live example fixes95counted candidate votes and forecasts only100remaining, giving195final candidate votes. The saved A+1pair case instead gives A101/B99/C200 at400final votes, so C leads despite A+1 against B. Neither is an actual election observation or probability. Global key/type/range validation applies before arithmetic even with zero/no selected pools. Targets, preference anchors, participation ratios and denominators are documented in source/SCHEMA.md and scenario settings.
