# Kansas original-source preflight

The official [results index](https://www.sos.ks.gov/elections/election-results.html) links the nine additional primary files retained here: 2024 broader presidential data, the 2024 president precinct workbook, 2022 and 2020 Senate precinct workbooks, three corresponding general-election statewide canvass PDFs, and 2026 primary statewide/precinct results. All returned HTTP 200. The [manifest](news/manifest.json) retains requested/final URLs, status, headers, UTC retrieval and raw/stored hashes. Generic `.html.gz` capture suffixes preserve actual XLSX/PDF bytes.

[Offline preflight](coordinator-primary-preflight.json) verifies hashes, ZIP CRCs and worksheet inventories. The broader 2024 file contains 18,268 rows across 105 literal county labels, with district/location/precinct/candidate fields. Its four named candidate sums exactly match the statewide canvass: Harris 544,853; Trump 758,802; Kennedy 16,322; Oliver 7,614; total 1,327,591. Unreported write-in, under-vote and over-vote categories remain unknown. Named candidate votes are distinct from ballots cast.

Provisional largest-first figures are top 15 = 970,376; first 22 = 1,057,110; minimum 23 = 1,067,659. Sumner’s 10,549 crosses 80%. This is source preflight, not accepted dispatch geography. Question agents must independently reconcile all counties/FIPS, candidate controls, native scope and exact order. Native `Comanche ` retains its trailing space; the turnout sheet uses `Comanche`. The explicit alias preserves both originals. The turnout sheet’s 105 county sums match its printed footer: 1,343,020 ballots and 2,031,120 registered voters. Definitions and vintage still require review.

Each precinct workbook has a main sheet plus separate Johnson, Sedgwick, Shawnee and Wyandotte sheets. Establish overlap or complementary coverage before aggregation. Preserve sheet/row/column positions, native precinct/VTD codes, leading zeros and source party headers. The 2020 Johnson supplemental header says NON for all three candidates, while the main sheet supplies party labels. Source coding and verified candidate identity stay separate. VTD assignments and district intersections do not establish approved November 2026 precinct geometry.

The 2026 primary statewide canvass contains all 13 Senate candidates: 11 Democrats total 224,076; two Republicans total 338,732. Earlier retained NPR/AP snapshots sum 220,803 and 335,479. Preserve both observed vintages without rescaling or claiming a cause. Those historical products establish no November feed or cadence.

Reproduce with `PYTHONDONTWRITEBYTECODE=1 python3 -S senate/2026/kansas/data/preflight_primary_sources.py`. Acquisition links remain in `data/news/fetch_evidence.py`; its whole-manifest entry point should not run during another acquisition. No Kansas agent has launched. Current geographic approval, exact outstanding votes and a calibrated forecast remain unestablished.


## Current rules alert, separate from historical controls

The current Russell County November page and October 7 regional reporting describe an injunction restoring a postmark/three-day receipt window and rejection of the stay; older SOS statutory calendar/newsletters describe its removal. Direct capture failures versus web-rendered primary observations are retained in `news/legal-web-observations.json`. The official-results assignment must recover signed orders and check subsequent disposition. Do not make the statutory calendar an operative no-grace instruction without that review. First-wave historical controls are unchanged.


## Supplemental primary ballot control

Coordinator recovered Sumner’s actual linked 24-page official2022 summary through countyhome→electionoffice→archive (all200). Exact originalSHA05018ae6d6a87e84778f0e34238fe6bca4c407a66dd99e4d5d2d418329b7be6e. `news/sumner-2022-control.json` records7932ballots,4blank; namedSenate5896Moran/281Graham/1692Holland=7869matchesSOS, plus3genericwriteins+60under+0over=7932. Six literalmethodcolumns balance. SOSturnout workbook1403remains a conflicting retained field, no inferred swap/errorcause/statewide repair. Original actual-linked entity exactly matches separately discovered public-host copy.
