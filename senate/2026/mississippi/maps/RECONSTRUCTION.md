# Exact reconstruction without duplicate stored originals

All paths below are relative to the Mississippi state root. Do not overwrite
the source references or their historical logical paths. `compatibility.py`
and `acquire.py` load exact bytes in memory after verifying stored hashes.

For an existing gzip original, decompress to a temporary path only when an
external reader requires a file. Example from repository root:

```sh
python -B - <<'PY'
from pathlib import Path
import gzip, hashlib
state = Path('senate/2026/mississippi')
path = state / 'data/coordinator-map-preparation/maris-2020-precinct-zip.body.gz'
stored = path.read_bytes()
assert hashlib.sha256(stored).hexdigest() == 'a308781f318c4c2f9ca8212bd1fe38db8f47c9d367b62b3c7d943be6c866554b'
raw = gzip.decompress(stored)
assert len(raw) == 16944514
assert hashlib.sha256(raw).hexdigest() == 'b174e72bb3755780107725d200822a2338ee5e8974928f1361d84dd95d2d54ef'
Path('/tmp/ms-map-reference-2020.zip').write_bytes(raw)
PY
```

For a segmented receipt, verify each segment's byte count and hash, concatenate
the `segments` array in recorded order, then verify the receipt's complete
`raw_bytes` and `raw_sha256`. There are currently no segmented downloads in
this bounded acquisition; the protocol exists to enforce the strict
40,000,000-byte per-file limit without truncation or simplification.

The complete compatibility object is reconstructed by loading the exact pinned
root contract, then resolving its full preferred-all11 body and historical
dependency manifest. That manifest points to complete immutable 2020 and 2018
components. Their decompressed bytes must match original byte/hash controls.
Source objects are recovered from each full readings body's `sources` array;
canonical object hashes match every independently frozen source-object record.
All 104 publications and both actual 2018 stages/all164 remain separate.
`canonical_resolution` also retains complete v1/v2 and 17-field-companion bodies.
The validation checks recursive equality/hashes, not just source IDs or counts.

Service originals reconstruct to their exact native Esri JSON, including
two `curveRings` geometries. Do not convert them to GeoJSON as a replacement
for those originals. The Lamar embedded collection resolves through the
recorded JSON Pointer into the complete county-linked webmap body. Its empty
feature is retained. A preview PDF/SVG is never the original geometry.
