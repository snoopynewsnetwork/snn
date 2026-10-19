# Bounded coordinator map preparation

This optional preparation is separate from the actual maps assignment. The
immutable `acquisition-native-stage-v1.json` preserves complete raw/error
entities, all response headers, redirects, request URLs, retrieval UTC and
stored/original hashes. Seven `jobs-*.json` files reproduce the exact observed
public routes. Do not rerun the acquisition writer when checking frozen inputs.
Run `python3 -B -S data/review_map_preparation.py` for a read-only replay.

Minnehaha's official precinct parent returned a raw403, while the primary web
reader exposed its actual mapbook and app links. Both complete original PDF
mapbooks were acquired: county10,937,333 bytes and city19,816,943 bytes.
The county-linked app `83db20af25c2402a8390082f51baa059` selects webmap
`7cc5bcba864d4d4781b83b229f2b8819`. Its actual Voting Precincts layer is
`gis.minnehahacounty.gov/minnemap/rest/services/Election/Redistricting_2022/MapServer/4`.
The complete81 features include six true curves. Native CRS is the published
custom NAD1983 UTM14N in US survey feet; preserve its complete WKT and units,
without substituting an assumed EPSG or the display webmap's Mercator extent.

Pennington's actual district-map parent returned200 and linked two PDFs that
returned403 and Experience `b03eeb32869e421fa0e92864794728f5`.
Its embedded old child-service URL returned404 and remains preserved. The
actual configured webmap `fe799037ba7240e1a5f8c16f12c9ecc0` instead supplies
`gis.rcgov.org/server/rest/services/AGOL/Voting/MapServer/13`, titled Precincts.
This complete53-feature native snapshot contains one true curve. Original
metadata/attributes and each response CRS remain intact, with no inferred
equivalence between the old and current service paths.

Both native snapshots use returned IDs in bounded batches of at most50,
all attributes, native geometry and requested Z/M/true curves. Exact pre/post
metadata, count and ID sets match; no output CRS, geometry precision,
quantization, rounding or geometry repair was requested. Source display
generalization is not otherwise certified. Curves are retained, not flattened.
No current legal or historical reporting-to-polygon match is approved.

Lincoln's original election/GIS/roster routes returned404/empty raw entities;
the primary web reader separately exposed current roster and map links.
Those observations do not supply retained original bodies. All failed raw
routes remain explicit alongside successful bodies. The actual39-parent maps
investigation must still cover every304 priority entry and full691/all66
inventory with qualified shared-parent assets and precise finer-unit gaps.

A later separate immutable `acquisition-Census-stage-v2.json` adds the actual
Census parent directory chain and complete2020VTD ZIP, raw4,315,722 bytes
SHA256`b48632cb589f4b6c45b5a353fd04e3e9426bbb08503440687960a0498ac06edb`.
Its785 original features cover all66 county FIPS, retaining505985 native XY
positions. `Census2020-native-structure.json.gz` checks every original record,
SHP/SHX offset/part/position bytes, DBF attribute and ZIP member CRC/hash.
This is a historical fallback, with no reporting/current identity approval.
Earlier32-observation native-stage snapshot and native review remain unchanged.
