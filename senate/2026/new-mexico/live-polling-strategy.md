# New Mexico collection and remaining-vote strategy

Prepared **2026-10-18 UTC / 2026-10-17 Central**. The historical first pair is now reviewed; official-source integration is now reviewed; map integration is complete. Read the [newsroom survey](local-news-results.md). No live collector or calibrated probability model is implemented.

## New Mexico-specific preflight

The [official 2026 index](https://www.sos.nm.gov/voting-and-elections/election-results/2026-election-results/) links separate statewide primary, Rio Rancho runoff and municipal elections. The observed primary is actual election 2911, June 2, official results updated June 23, 2:26 p.m. MT. Generic page text still references November 2021. Require the actual November 3 Senate contest/date rather than trusting a 2026 title, arbitrary election ID or generic prose. The historical elections database is not a live count channel.

Retain all 33 counties and native precinct/method identities in statewide coverage. County and statewide releases overlap; preserve whether absentee/early/Election Day/provisional records are disjoint rows or alternate summaries. The source investigation covers all33parents and every protected/admin case; certified native80%membership remains unknown. Map compatibility requires separate evidence. Statewide contest totals and ballots are different denominators. No map allocation through a presumed unchanged precinct number.

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

Before live use, replay genuine dated releases and test idempotent retries, missing units, corrections/decreases, overlapping aggregates, candidate identity and manual recovery. Keep original counts and derivatives auditable. A calibrated win probability additionally requires a dated prior, genuine historical release sequences, remaining-ballot assumptions and held-out calibration under the [root plan](../../../ELECTION_NIGHT_PLAN.md). No live collector or calibrated Needle is implemented here. The reviewed official inventory and map context now cover all33parents. Protected cells prevent a certified native priority set, and acquired geometry has no approved historical/current result crosswalk.


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

Official-source research is complete across all33authorities and2,201source
investigations. The [map atlas](maps/index.html) is reviewed for qualified geographic context. [Coordinator review](research-review.md)
links the audits and source limits. Actual primary 2911, general candidate
portal 2917 and historical ElectionStats IDs remain distinct.


## Reviewed current-publication controls

The [official report](official-results.md) and [independent review](data/coordinator-official-final-review.json)
retain257bounded requests and whole public response structures. State archive
2911 is the June primary; candidate portal2917 is a different namespace.
DeBaca's directory lacks a website href. Preserve that blank and every blocked
county route rather than guessing a local endpoint. A public state export
returned an empty worksheet, which establishes no zero votes or completion.

Bernalillo's separately indexed primary product has72centers/zero beside a
different74/74completion display, raw write-in8564 and a client-hidden resolved
write-in field. Keep these scopes and raw/presentation values distinct. SanJuan's
complete XML has45contests and blank/duplicate choiceIDs; its client polls
Last-Modified every30seconds. That timer is not measured vote cadence, and its
America/Denver HTTP-clock conversion does not supply the XML publisher timezone.
Neither county product has an established clerk outbound chain where the
clerk page was inaccessible. Both remain bounded indexed source observations.

The retained [current Chapter1 original](https://nmonesource.com/nmos/nmsa/en/4351/1/document.do)
requires completed mailed ballots received by7PM ElectionDay. Signature presence
and matching last4SSN digits, missing-information notice/cure and federal first-
time-mail identification have distinct scopes. The provisional rule's Friday
before state canvass is distinct from Friday-after-election handling. Current
state meeting arithmetic givesNovember24; certificates cannot issue before
day31,December4. Senate automatic recount is strictly below0.25%of officevotes;
its state-law procedure remains separate from the Senate's ArticleI§5authority.
The [full bounded legal audit](official-results.md#operative-rules-and-source-vintage)
preserves enactment dates, replacement rules, proposed-rule adoption uncertainty
and selected signed court orders. Later amendments/dockets and complete signed
ballot/write-in scope remain external qualifications.

Use the [five selected original-page review](data/coordinator-official-visual-review/review.json)
within its stated scope. It does not certify every code page or later court
action. No new collector, exact eligible remainder or probability is admitted.


The map package preserves complete2024/2026RGIS releases and a2,177-feature
native service, plus county originals. SantaFe's actual2026map names new
precincts180–185 effectiveJanuary1, while July2026RGIS/service retain179features.
Treat that as a currency warning. Statewide and county result labels, privacy
aggregates, physical sites, ballot styles and polygonIDs require independent
current dictionaries. Matching counts or names supply no allocation authority.
No protected residual or VoterPrivacy record can be spatially distributed from
these references. All33parents/all2,201source observations remain in research
coverage; neither observed1,392-prefix nor county10 sensitivity is live dispatch.
