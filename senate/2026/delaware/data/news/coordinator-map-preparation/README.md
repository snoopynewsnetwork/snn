# Delaware original map preparation

Observed October19,2026 Eastern / October20 UTC. This optional coordinator
preparation supplies exact acquired originals. It is not an assignment finish,
a current geographic crosswalk, or a required worker build dependency.

The actual [Department maps page](https://elections.delaware.gov/maps/) links
the [ED map index](https://elections.delaware.gov/maps/ed/index.html) and
[FirstMap Election Districts](https://de-firstmap-delaware.hub.arcgis.com/maps/delaware::election-districts-1).
The Hub's complete original HTML exposes its dataset identifier. Its acquired
public JavaScript exposes the dataset metadata constructor. The returned
complete metadata explicitly identifies
[FeatureServer layer0](https://enterprise.firstmap.delaware.gov/arcgis/rest/services/Boundaries/DE_Political_Boundaries/FeatureServer/0).
Every request and source constructor is retained in the immutable
[acquisition inventory](acquisition-complete-v1.json).

Eleven batches of at most50 explicitly requested IDs return all531 features,
all six attributes,533 linear rings and169,245 native coordinate positions.
Fresh pre/post layer metadata, counts and complete ID sets are equal. Complete
response bodies preserve native geometry; no outputCRS, coordinate precision,
quantization, simplification or repair was requested. The
[independent replay](native-acquisition-review.json) checks each returned ID,
complete attribute set and original coordinate position. No curves or empty
geometries were returned in this acquisition. This is not a legal topology
certification.

The metadata's full spatial reference contains precision/tolerance properties
omitted from query response spatial-reference envelopes. Both remain intact;
matching WKIDs does not imply byte-identical metadata objects. The initial
overly strict checker and finding remain under
`history/initial-spatial-reference-assumption/`.

Source vintages differ: the Hub description refers to2010 districts, the
template says2022, and the server description explicitly mentions an election
RD-ED update in November2023. None independently establishes current legal
effectiveness. In particular,531 geographic features are not a crosswalk to
530 historical Senate source observations or537 structure rows.

Five complete original PDF pages were rendered and actually viewed; see the
[render receipts](render-receipts.json) and
[manual visual record](visual-review.json). The District11 overview explicitly
names both NewCastle and Kent despite its Kent URL directory. Distinct actual
ED maps07-08 and08-07 both print March8,2023. Their filenames do not authorize
reversing historical result key0807 or allocating votes spatially.

Reproduce the raw integrity and complete native acquisition review with:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B -S senate/2026/delaware/data/news/review_map_preparation.py
```

The acquisition helper and seven exact job files remain one directory above
and here, respectively. Original bodies are stored once as lossless gzip
objects or reused by exact hash. A later map worker can independently verify
and freeze individual receipt references without depending on this optional
README or coordinator proof. Producers and the external historical acceptance
are unchanged. No current or historical reporting-unit join is approved.
