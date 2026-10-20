# Reproduce the Virginia official-source research

Run from `/Users/tqbf/codebase/snn`. Python 3 standard library and installed Poppler `pdftotext`/`pdfinfo` are sufficient; no packages, producer imports, network, newsroom aggregate, optional peer proof or maps build is required. Use `-B` and `PYTHONDONTWRITEBYTECODE=1` to prevent cache directories.

External historical authority: `senate/2026/virginia/data/coordinator-priority-acceptance.json` (path only). The independent launch read/size/hash checks were completed before consuming its roots and the frozen turnout contract. Reproduction obtains its expected input evidence from the complete external authority at runtime; it does not create a replacement authority or persist its digest/body. Missing or mismatching exact inputs fail the checks. Old path references resolve their original pinned body/archive member, never a newer body now at that path.

Read-only full verification after sealing:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B senate/2026/virginia/data/results-sources/audit.py --final
```

This reads every owned file, verifies exact manifest membership/hash/size, request/body integrity, all historical/current full references, all orders/hierarchies, CSV coverage and local Markdown file targets. It independently rebuilds reporting/schema/format products into a temporary directory with socket creation/connection forbidden, compares them byte-for-byte, reruns source-derived negative mutations, and replays the complete historical acceptance. It makes no owned writes. Its stdout is the final audit result; no post-manifest proof is written into the package.

The independent historical replay can also run alone, read-only:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B senate/2026/virginia/data/results-sources/replay.py
PYTHONDONTWRITEBYTECODE=1 python3 -B senate/2026/virginia/data/results-sources/test_research.py
PYTHONDONTWRITEBYTECODE=1 python3 -B senate/2026/virginia/data/results-sources/reproduce.py
```

Replay checks the complete 25-root contract, 721 fixed files, 471 whole structured companions, all 3,474,062 full recursive objects in 24 ordered partitions, 1,172 historical original-body resolvers, six complete archive member sets, both producer seals/self exclusions, 166 source receipts, nine shared originals and the final candidate workbook. It independently decodes every original Senate CSV header/control/parent/native cell and validates byte spans. Opaque intentionally invalid CLI fixtures remain raw verified entities and are strict-rejected where applicable. Models/scenarios are preserved; no new scenarios or outcome equality are tested.

`reproduce.py` rebuilds the full parent/hierarchy/priority/remainder/current-native/schema/acquisition products, source CSV, 108-parent review, summary and final report using `build.py`. It rebuilds all automatic PDF/CSV format products with `format_inventory.py`. All returned products must be byte-identical. Original HTTP responses, search snapshots, human annotations and manually viewed PNGs are evidence inputs, not simulated or re-requested. Older inspection files are verified against their complete raw HTML/OOXML; all 41 distinct PDF bodies have complete automatic extraction in the format inventory. No manual all-pages PDF review is claimed.

For a new intentionally revised pre-seal package only, the production sequence is:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B senate/2026/virginia/data/results-sources/format_inventory.py
PYTHONDONTWRITEBYTECODE=1 python3 -B senate/2026/virginia/data/results-sources/build.py
PYTHONDONTWRITEBYTECODE=1 python3 -B senate/2026/virginia/data/results-sources/replay.py --write
PYTHONDONTWRITEBYTECODE=1 python3 -B senate/2026/virginia/data/results-sources/test_research.py --write
PYTHONDONTWRITEBYTECODE=1 python3 -B senate/2026/virginia/data/results-sources/reproduce.py --write
PYTHONDONTWRITEBYTECODE=1 python3 -B senate/2026/virginia/data/results-sources/audit.py --write
PYTHONDONTWRITEBYTECODE=1 python3 -B senate/2026/virginia/data/results-sources/seal.py
PYTHONDONTWRITEBYTECODE=1 python3 -B senate/2026/virginia/data/results-sources/audit.py --final
```

The handoff must already exist before this sequence's validation/seal. `seal.py` writes the final seal and manifest last. After a passing final audit, make no owned writes. A substantive revision requires a new explicit build/validation/seal/audit cycle; it is not an amendment to a supposedly immutable completed seal. Final audit stdout/delivery may state the manifest digest externally; no owned file reverse-pins it.

Acquisition scripts document the already performed bounded actual requests and immutable receipts. They are not part of offline reproduction, not a scheduler/collector and not authorization to repeat or extend research. The directory selector POST uses only observed public locality fields. No contact/auth/admin/challenge action was used. One unavailable browser attempt led to static fallback; no unseen browser result is claimed. Failed HTTP bodies and unavailable metadata remain explicit.

The coordinator alone reviews, accepts and publishes. Current legality/eligible write-ins, native IDs/geometry, genuine November counts, cadence, exact remaining pool and collector/forecast/calibration remain false or unknown external qualifications.
