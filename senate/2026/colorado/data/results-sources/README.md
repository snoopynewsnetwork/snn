# Colorado official-source evidence and deterministic replay

This is a source-only research package for external coordinator review. Current counts admitted, current geography/choice-ID approval, live collection, cadence measurement and probability approval are all false. The [external acceptance](../coordinator-priority-acceptance.json) is an authority **path only**; no hash, copy, reverse producer write or optional coordinator review is required here.

From the repository root, with Python3 standard library and Poppler `pdftotext` available:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/colorado/data/results-sources/inspect_sources.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/colorado/data/results-sources/extract_documents.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/colorado/data/results-sources/extract_directory.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/colorado/data/results-sources/build.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/colorado/data/results-sources/render_report.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/colorado/data/results-sources/validate.py
```

These steps read the frozen whole originals and do no network work. Build/inspection writes only owned derived files. All required complete semantic companions and immutable source bodies must be present in the shared checkout. `validate.py` independently reparses original CSV/SSR/OOXML, all contract objects, arrays, schemas, contacts and acquired bytes; it imports neither build nor producer modules. `--write` writes its dated-free pre-seal result. After changes and successful QA, `seal.py` writes the complete manifest; the final command is strictly read-only:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/colorado/data/results-sources/validate.py --sealed
```

The [deterministic replay check](replay-validation.json) verifies17 byte-identical derived files and complete Denver/split-original/full-object reconstruction. Re-run it offline with `PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/colorado/data/results-sources/replay_check.py`. The [document visual review](visual-review.json) records the original calendar row alignment and actual court disposition checks.

Reconstruction writes exact complete original bytes, or a full recursively referenced source object:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/colorado/data/results-sources/reconstruct.py --receipt denver-november-payload --output /private/tmp/co-denver-original.json
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/colorado/data/results-sources/reconstruct.py --reference 1 --output /private/tmp/co-complete-first-source-object.json
```

For a receipt, outer storage gzip is decompressed after stored-stream hashes/sizes are checked. Where `body_parts` exists, concatenate its exact ordered parts first; verify the original complete stored-stream checksum, then decompress. `--decode-http` additionally decodes an actual gzip/deflate HTTP Content-Encoding. Raw receipt hashes describe exact urllib bytes before this HTTP decoding. Existing producer originals referenced read-only use their preserved decoded-entity convention and original receipts. No truncation or original duplication is needed. One large acquired Lincoln sample PDF uses ordered splits; complete bytes survive and each part is below40MB.

`acquire.py REQUEST_PLAN.json` is a bounded **research acquisition**, not a collector. It sends at most four simultaneous public GETs, records failures/full bodies, and follows no link automatically. Historical request plans are retained; the complete final acquisition includes every actual URL/parent/constructor/GET query. The plan builders show actual HTML/JS/tuple dependencies. They must not be used to invent a November endpoint, enumerate IDs, call authenticated/admin endpoints, or imply measured cadence. No POST was used. Reacquiring mutable pages would be new research with new evidence, not deterministic replay of this seal.

The [schema](SCHEMA.md) identifies complete originals, full-object references, current sample and historical namespaces. See the [report](../../official-results.md), [authority inventory](../official-results-sources.csv), [full parent findings](parent-findings.json), [legal qualifications](legal-qualifications.json), [pre-seal validation](validation.json) and [asset manifest](asset-manifest.json). Research QA does not authorize publication or live admission.
