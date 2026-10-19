# Reproduce Nebraska official-source research

Ownership: `official-results.md`, `data/official-results-sources.csv`, this directory only. No Git, peer/coordinator writes, outreach, delegation or collector is used. Coordinator alone publishes. [SCHEMA.md](SCHEMA.md) describes exact originals, nulls and complete recursive references.

Offline sequence, from repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/nebraska/data/results-sources/freeze_inputs.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/nebraska/data/results-sources/inspect.py
PYTHONDONTWRITEBYTECODE=1 NE_XLRD_PATH=/tmp/snn-xls-reading-libs python3 senate/2026/nebraska/data/results-sources/replay_history.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/nebraska/data/results-sources/build.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/nebraska/data/results-sources/report.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/nebraska/data/results-sources/validate.py --write-validation
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/nebraska/data/results-sources/manifest.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/nebraska/data/results-sources/validate.py
```

Python3 stdlib and system Poppler (`pdftotext`, `pdftoppm`) are required. `xlrd` is only needed for original BIFF replay; install outside this delivered directory or point `NE_XLRD_PATH` at an existing temporary environment. No dependency/cache directories are delivered. Nothing rewrites frozen originals or first-pair outputs.

Acquisition is an explicit finite source audit. `acquire.py ID URL PARENT_ID DISCOVERY_BASIS` retains one original response and full receipt; it never overwrites a receipt. A new observation must use a new ID. Every included `*-plan.json`/`*-plan-follow.json` records exact requested URLs and their observed parent links or public constructor evidence. Review a plan, then use `discover.py fetch <planfilename>`; existing receipts are reused. This does not refresh them or establish a measured cadence. Network access is needed only for a deliberately new observation.

Seeds were actual official directory, county portal, current state ENR, SOS election parent and complete Legislature chapter. `discover.py seeds` parses all93literal directory website links and complete portal rows. `discover.py follow landing-plan.json` derives the bounded priority county-linked publication plan. Further public route/JS/version plans preserve the actual source constructors/returned IDs. No paths are found by guessing county/race/candidate IDs. Current native IDs come from complete state county results and inspected `BuildPrecincts` code; Clarity versions and config parameters come from actually returned originals. Sandbox DNS failures remain separate receipts before successful authorized-network requests.

Every complete raw/error response can be reconstructed using receipt `stored_parts` in order, then gzip decompression. Verify stored and raw lengths/SHA256 before using it. Some publishers return gzip-encoded HTTP content even when `.js`/`.html` is requested; `acquire.decoded` performs a separate content-decoding derivation without changing entity pins. TLS/DNS failures do not fabricate a response body. HTTP200 challenge/application shells are not result admission.

`replay_history.py` freshly reads all91complete HTML partitions, local BIFF and complete1431page Lancaster original plus original canvass controls. It independently checks full order/candidate controls, raw cell values/types, all595method contexts/199statistics and observed-generic membership sensitivity. It imports no worker/coordinator parser and writes only owned derivatives. `freeze_inputs.py` recursively verifies the external acceptance's listed frozen inputs/reviews/reports/manifests/validation/proofs and exact source references. External acceptance is cited by path only, never hashed back into the contract or used for self-approval.

The complete old233source receipt ledger is a frozen exact-hash original dependency. A one-time read checked the later239ledger preserved that prefix and saved only the six additional complete individual receipts as optional evidence. Subsequent builds/validation do not read the mutable news ledger or map/coordinator aggregates. Optional source files are individually pinned in the manifest; no newsroom test setup is official results.

To reproduce the six saved full-page visual derivatives, use the source/page list in `visual-source-pages.json`, reconstruct the original to a temporary file, and run `pdftoppm -f PAGE -l PAGE -scale-to 1600 -singlefile -png INPUT OUTPUT_PREFIX`. They were actually viewed. The full original remains distinct from a render/text derivative.

The manifest excludes itself only and includes the deterministic saved validation. Validation has no reverse manifest hash, avoiding cycles. Final immutable manifest/validation/report pins are external coordinator evidence. Rebuilds should preserve all owned artifact bytes unless code or observations deliberately change. Current live ballots/eligibility, later court orders, current geography joins, genuine returns, remaining votes, measured cadence and calibration remain external qualifications, not inferred from successful research checks.
