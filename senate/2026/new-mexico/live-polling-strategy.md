# New Mexico collection and remaining-vote strategy

Prepared **2026-10-18 UTC / 2026-10-17 Central**. The historical first pair is now reviewed; official-source and maps integration remains pending. Read the [newsroom survey](local-news-results.md). No live collector or calibrated probability model is implemented.

## New Mexico-specific preflight

The [official 2026 index](https://www.sos.nm.gov/voting-and-elections/election-results/2026-election-results/) links separate statewide primary, Rio Rancho runoff and municipal elections. The observed primary is actual election 2911, June 2, official results updated June 23, 2:26 p.m. MT. Generic page text still references November 2021. Require the actual November 3 Senate contest/date rather than trusting a 2026 title, arbitrary election ID or generic prose. The historical elections database is not a live count channel.

Retain all 33 counties and native precinct/method identities in statewide coverage. County and statewide releases overlap; preserve whether absentee/early/Election Day/provisional records are disjoint rows or alternate summaries. The measured 80% set and downloaded map compatibility must come from the state questions, not population assumptions. Statewide contest totals and ballots are different denominators. No map allocation through a presumed unchanged precinct number.

2024 Senate/president and 2020 same-seat Senate have distinct candidate fields. Use an actual 2022 statewide midterm contest such as the certified governor election for the comparator; New Mexico had no 2022 Senate contest. Historical volume anchors and preference/coalition changes stay conditional rather than becoming 2026 turnout predictions. Current ordinary poll hours/timezone, mail receipt/eligibility, curing/provisional rules, canvass and certification require primary verification and current orders before operation.

KOB/KOAT newsroom homepages are accessible; KRQE and Source NM direct captures failed. KVIA's actual results still show June New Mexico primary returns, despite its Texas base. The June 10 timestamp lacks a verified timezone. Require state/election/candidate and method identity for every newsroom fallback. Northern/northwestern and eastern-region product coverage remains a gap; do not claim those regions have independent verified scoreboards.

## Proposed collection and revision handling

Start with 2-minute checks of a verified official release index/version around an announced election-night publication, fetching details only after a change. Use 5-minute checks for verified newsroom backstops and manual NYT observation where automated access fails. Outside announced windows, back off to 15 minutes or hourly during counting and daily through canvass/certification. These are implementation proposals, not observed publisher cadence. Use timeouts, bounded concurrency, jitter, conditional requests where supported and exponential backoff. A quiet source is not automatically an outage.

Resolve actual November navigation and verify election date, Senate title, complete candidate identities, zero/test status, unit/method coverage and source status before importing counts. HTTP 200, a current pathname, an old widget ID or visible candidate numbers is insufficient. Store original bytes, URL, UTC retrieval, HTTP/cache headers, hash, parser version, publisher timestamp/timezone and native election/contest/unit IDs. Reject challenge HTML and app shells. Keep a source-health ledger with last successful fetch, last genuine vote change, expected versus observed units, and manual-fallback reason.

Replace cumulative snapshots; derive compatible changes afterward and retain decreases, corrections and status changes. State, county, municipality/authority, precinct and method views may overlap. Pick a consistent authoritative scope rather than summing every product or averaging disagreements. External calls, estimated completion and probabilities remain separately attributed fields. Multiple AP products or shared newsroom reports are one upstream chain. Preserve a conflicting observation until scope/time/status explains it.

For a failed primary channel, capture the same official election page or linked PDF/export manually with URL, observation time, source status and original file/screenshot. Use newsroom figures only as an explicit temporary substitution for the same unit/method. Reconcile and replace with official counts once available; never silently combine different vintages. NYT access and actual November Senate product remain unverified in this preparation.

## Remaining votes and scenario readiness

Counted votes remain fixed. Estimate only uncounted ballots using documented unit/method inventories and explicit low/base/high ranges, with source/time and acceptance/counting status. Issued minus returned, registration minus turnout and reporting-precinct percentages do not equal remaining candidate votes. If accepted-unprocessed detail is absent, uncertainty remains unknown or bounded by stated assumptions; do not manufacture an exact total. Processed ballots, eligibility review, published candidate counts and certification are different stages.

Compare partial returns with the same historical geography/method and boundary vintage. No allocation through an unvalidated map crosswalk. Historical turnout volumes are sensitivity anchors, not 2026 projections. Tie/+1 conditional scenarios require complete statewide weights and candidate/other-vote reconciliation; distinguish share-point shifts from margin-point shifts. Do not substitute an independent candidate into a D/R coalition without explicit identity and assumptions.

Before live use, replay genuine dated releases and test idempotent retries, missing units, corrections/decreases, overlapping aggregates, candidate identity and manual recovery. Keep original counts and derivatives auditable. A calibrated win probability additionally requires a dated prior, genuine historical release sequences, remaining-ballot assumptions and held-out calibration under the [root plan](../../../ELECTION_NIGHT_PLAN.md). No live collector or calibrated Needle is implemented here. Final integration must insert the measured priority set, complete official inventory, downloaded map compatibility and verified current rules from the four state question assignments.


## Independently reviewed historical scope

The [source authority](data/coordinator-source-research-acceptance.json) retains
all 2,201 Senate observations and 33 county parents, with 31 complete contract
fields, 68 companions and 403,993 recursive objects. Privacy masks leave the
certified native order, top-15 share and minimum 80% set unknown. Investigate
all 33 parent chains, including every unknown and administrative case. The
1,392-row fully observed prefix and ten-county sensitivity remain descriptive.

The 2020 Class II Senate, 2024 Class I Senate, 2024 president and 2022 governor
contests remain separate historical anchors. Independent source, formula and
repaired CLI checks pass. Counted candidates remain fixed in synthetic remainder
cases; historical volumes are sensitivities. Registration, ballot returns and
a masked-total zero do not establish eligible unprocessed Senate votes.

Official-source research is active across all 33 authorities and 2,201 source
investigations. Maps are prepared for the next available slot. [Coordinator review](research-review.md)
links the audits and source limits. Actual primary 2911, general candidate
portal 2917 and historical ElectionStats IDs remain distinct.
