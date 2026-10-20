# Offline reproduction

From the checkout root, with Python3, PyShp3.1.6, Shapely, Poppler and librsvg installed:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B senate/2026/new-mexico/maps/run_offline.py
PYTHONDONTWRITEBYTECODE=1 python3 -B senate/2026/new-mexico/maps/run_offline.py --audit
```

The first command independently reconstructs/pins the whole frozen source graph, verifies complete acquisitions including redirects/failures/splits, repeats the native binary reader/PyShp audit, checks all native service batches/pre-post metadata, verifies/recreates complete PDF text/renders, rebuilds the static full inventory/atlas, runs DOM/filter/full-object/escaping and negative checks, validates and seals. It imports only code in maps plus installed libraries; no producer/coordinator writer is imported. The authority is read by path only. Captured producer and historical bodies resolve exact original path+hash, not a repaired current replacement.

`--audit` performs no writes. It checks exact self-only-excluded ownership coverage, every stored file hash/size, all immutable body references, every original response entity/reconstruction and current contract equality. It prints the actual final audit result. Do not add a file after sealing without resealing; do not insert the current manifest hash into validation/final-seal.

Acquisition was a separate one-time bounded source observation, not part of offline replay. `acquire.py` without flags verifies receipts offline. `--roots` downloads only roots if no matching receipt exists. The other acquisition scripts retain the specific literal source constructors/hops used. They do not refresh existing receipts silently; archive a prior receipt with its original context before making any new observation. Historical failures must remain. Network access requires the public-download authorization supplied for this assignment; no browser/account/TLS/challenge workaround is part of reproduction.

The full Cibola155MBPDF is reconstructed in a temporary directory solely for Poppler and removed afterward. No extra huge duplicate original, dependency or cache directory belongs in this package. Every `.gz` and multipart entity is reconstructed without loss, not read as an acquired partial file. Opening `index.html` locally needs no server or JavaScript; category links point to complete static filtered inventories. Browser rendering was optional and unavailable after an interrupted attempt, as recorded in `browser-attempt.json`.
