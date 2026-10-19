# Bounded coordinator map preparation

These sources prepare the eventual independent map assignment. They are not
the completed maps package, and establish no reporting-unit/geographic match.
The accepted historical dispatch remains
[the external named-canvass record](../coordinator-priority-acceptance.json).

[The immutable 38-observation receipt snapshot](acquisition-native-stage-v1.json)
pins complete original/error entities, requested/final URLs, headers, redirect
chains, retrieval UTC, parent links and literal app/webmap/item IDs. Original
HTTP entity bytes are losslessly gzip-stored once; identical observations reuse
exact earlier bodies. The live acquisition journal is not an input pin for a
finished worker. [Acquisition code](../acquire_map_preparation.py) accepts only
explicit observed URLs or documented public item/query constructors with exact
observed item IDs. It does not discover IDs by guessing.

Douglas's actual [election map parent](https://www.votedouglascounty-ne.gov/maps.aspx)
links an Experience application. Its complete public item configuration selects
the precinct webmap `cea5c9697dea45309b64c98b671e545f`; that webmap links
`Precincts_2026_Combined_View/FeatureServer/145`. Complete native acquisition
retains **234 features**, all attributes and native coordinate rings in
WKID102704/latest26852. This is distinct from the historical 233 BIFF reporting
rows and supplies no identity equivalence.

The [Lancaster county parent](https://www.lancaster.ne.gov/488/Precinct-Maps)
was readable through the separate web-reader surface while the raw request
returned403. Its actual linked lookup app points to webmap
`d4c7b1b50de646eab6c943e05de26a4b`, whose `Voting Precincts` layer is
`Planning/Elections/MapServer/7` on `gis.lincoln.ne.gov`. Complete native
acquisition retains **222 features**, all attributes and native coordinate rings
in WKID102100/latest3857. This is distinct from the historical 198 Senate
reporting contexts. Both March2025 linked PDF raw requests returned403; those
error entities remain, with the web-reader's readable rural PDF observation
separate. No PDF original was downloaded by those blocked requests.

For both native layers, five pages of at most50 literal IDs cover the complete
pre/post count and ID sets. Metadata is exactly equal pre/post; no transfer
limit or response error is present. Requests ask for all attributes, geometry,
Z/M and true curves without output CRS, precision reduction, rounding or
quantization. Full originals remain unmodified. Topology, legal vintage and
the relationship to current or historical reporting units remain for the map
worker to investigate independently.

The actual [Census directory](https://www2.census.gov/geo/tiger/TIGER2020PL/STATE/31_NEBRASKA/31/)
links `tl_2020_31_vtd20.zip`. The retained complete ZIP is3,294,509 bytes,
SHA256 `2d22bbc8fcd115105fec245ba212dcfc134625a31287f87a5eb91c73d7a9f564`.
ZIP CRCs/member hashes, DBF fields and full source shape/part counts pass:
**1,402 VTD features /93 counties /383,061 native XY positions**. This is a
federal **2020 historical fallback**, not a current precinct source or a
crosswalk to the 1,326 historical reporting observations. A prior wrong Census
directory404 remains a separate retained observation.

[Native batch review](../coordinator-map-native-preparation-review.json) and
[its independent replay](../review_map_preparation.py) retain source-native
feature/attribute fingerprints, full original page pins, all field names,
CRS, pagination and pre/post evidence. The initial review's misleading
`unapproved_*` counter name was changed to `approved_*` (zero); its exact older
body remains separately retained. No source bytes, feature attributes or
geometry changed. No additional research worker was launched for preparation.
