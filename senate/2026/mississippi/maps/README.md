# Mississippi offline maps

Open [the887-entry index](index.html), [full inventory](inventory.html), or
[preview atlas](previews/map-preview-atlas.pdf). Read [the report](../precinct-maps.md)
for authority, dates and gaps. These are qualified shared map references;
there is no approved native reporting-unit crosswalk or allocation.

The complete source contract and source originals are reused read-only by
exact hashes. Keep their referenced state-relative paths when copying this
package. The owned directory alone is not a substitute for those canonical
dependencies. See [schema](SCHEMA.md), [acquisition](ACQUISITION.md) and
[reconstruction](RECONSTRUCTION.md).

Default offline validation, from repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python -B senate/2026/mississippi/maps/validate.py
```

Intentional owned-derivative rebuild, no network or historical source rebuild:

```sh
PYTHONDONTWRITEBYTECODE=1 python -B senate/2026/mississippi/maps/geometry.py
PYTHONDONTWRITEBYTECODE=1 python -B senate/2026/mississippi/maps/previews.py
PYTHONDONTWRITEBYTECODE=1 python -B senate/2026/mississippi/maps/build.py
PYTHONDONTWRITEBYTECODE=1 python -B senate/2026/mississippi/maps/report.py
PYTHONDONTWRITEBYTECODE=1 python -B senate/2026/mississippi/maps/validate.py --write
PYTHONDONTWRITEBYTECODE=1 python -B senate/2026/mississippi/maps/validate.py
```

Dependencies used here: Python, requests (acquisition only), PyShp3.1.6,
Shapely2.2.0/GEOS, pyproj3.7.2, PyMuPDF1.27.2.3 and Pillow12.3.0. Exact versions
are recorded in outputs. No install/cache tree is stored here. Original
retrieval is separate and should not run during validation. Frozen history,
compatibility references and actual visual-QA observations are not regenerated
by a routine geometry/index build. A changed preview requires new visual review.
