# Rhode Island collection and remaining-vote strategy

Prepared **2026-10-18 UTC / 2026-10-17 Central**. Both original-first source assignments, the narrow Cranston detail correction and bounded reciprocal review are complete. Qualified historical dispatch is accepted; official-source research is active and maps queued. Read the [news survey](local-news-results.md); no live implementation or calibrated forecast is supplied.

## Rhode Island-specific preflight

Use the [Board of Elections navigation](https://electionresults.ri.gov/) to resolve actual November data. Current primary routes return a successful Angular shell; a shell is not parsed candidate data. Research-browser primary text has September official results, but no November identifier is established. Do not replace the primary slug with a guessed general-election name. Preserve exact status, source timestamp, original native election/candidate/unit keys and transport response type.

Retain actual municipalities/wards/precincts and board-administered counting categories; county-style names do not establish the reporting authority. All reporting geographies, including island communities, remain in state totals. The source-known reported-candidate/generic minimum is242of458Senate source codes; legal write-in/native80robustness and all current map crosswalks remain unapproved. A municipality filter and statewide summary may be overlapping views of the same ballots, not disjoint additions. Equal precinct labels across vintages do not prove compatible boundaries.

The Journal explicitly derives counts from the state board. Its dated configuration is September 9 primary, with a 60-second browser check and cutoff after that election window; the observed state summary is historical primary data. Senate completion uses 402 units while governor uses 398 in that retained view. Never replace contest-specific unit coverage with a generic denominator or treat 100% precincts as all final valid votes. Preserve browser timer, source count time and October retrieval separately. WPRI direct access failed; WJAR/Public's Radio homepages establish current newsroom access, not November numeric channels.

Distinguish 2024 Senate/president, 2020 same-seat Senate and an actual 2022 statewide midterm contest such as governor; no 2022 Rhode Island Senate baseline exists. Verify current municipal polling hours, including opening differences and any island exception, mail/provisional/early handling, cure/receipt deadlines and canvass/certification from controlling primary sources before operations. Missing accepted-unprocessed ballot evidence remains uncertainty rather than an inferred exact remaining total.

## Proposed collection and revision handling

Start with 2-minute checks of a verified official release index/version around an announced election-night publication, fetching details only after a change. Use 5-minute checks for verified newsroom backstops and manual NYT observation where automated access fails. Outside announced windows, back off to 15 minutes or hourly during counting and daily through canvass/certification. These are implementation proposals, not observed publisher cadence. Use timeouts, bounded concurrency, jitter, conditional requests where supported and exponential backoff. A quiet source is not automatically an outage.

Resolve actual November navigation and verify election date, Senate title, complete candidate identities, zero/test status, unit/method coverage and source status before importing counts. HTTP 200, a current pathname, an old widget ID or visible candidate numbers is insufficient. Store original bytes, URL, UTC retrieval, HTTP/cache headers, hash, parser version, publisher timestamp/timezone and native election/contest/unit IDs. Reject challenge HTML and app shells. Keep a source-health ledger with last successful fetch, last genuine vote change, expected versus observed units, and manual-fallback reason.

Replace cumulative snapshots; derive compatible changes afterward and retain decreases, corrections and status changes. State, county, municipality/authority, precinct and method views may overlap. Pick a consistent authoritative scope rather than summing every product or averaging disagreements. External calls, estimated completion and probabilities remain separately attributed fields. Multiple AP products or shared newsroom reports are one upstream chain. Preserve a conflicting observation until scope/time/status explains it.

For a failed primary channel, capture the same official election page or linked PDF/export manually with URL, observation time, source status and original file/screenshot. Use newsroom figures only as an explicit temporary substitution for the same unit/method. Reconcile and replace with official counts once available; never silently combine different vintages. NYT access and actual November Senate product remain unverified in this preparation.

## Remaining votes and scenario readiness

Counted votes remain fixed. Estimate only uncounted ballots using documented unit/method inventories and explicit low/base/high ranges, with source/time and acceptance/counting status. Issued minus returned, registration minus turnout and reporting-precinct percentages do not equal remaining candidate votes. If accepted-unprocessed detail is absent, uncertainty remains unknown or bounded by stated assumptions; do not manufacture an exact total. Processed ballots, eligibility review, published candidate counts and certification are different stages.

Compare partial returns with the same historical geography/method and boundary vintage. No allocation through an unvalidated map crosswalk. Historical turnout volumes are sensitivity anchors, not 2026 projections. Tie/+1 conditional scenarios require complete statewide weights and candidate/other-vote reconciliation; distinguish share-point shifts from margin-point shifts. Do not substitute an independent candidate into a D/R coalition without explicit identity and assumptions.

Before live use, replay genuine dated releases and test idempotent retries, missing units, corrections/decreases, overlapping aggregates, candidate identity and manual recovery. Keep original counts and derivatives auditable. A calibrated win probability additionally requires a dated prior, genuine historical release sequences, remaining-ballot assumptions and held-out calibration under the [root plan](../../../ELECTION_NIGHT_PLAN.md). No live collector or calibrated Needle is implemented here. Final integration must insert the measured priority set, complete official inventory, downloaded map compatibility and verified current rules from the four state question assignments.


## Reviewed historical source geography

The [source contract](data/turnout/priority-set.json) preserves458Senate source
contexts, all497nativeinventory entries and43complete parent records. Four
federal-admin codes have1,473Senatevotes outside municipal totals and must not
be distributed geographically. The primary242-row prefix has394,072/491,948
reported votes; the21parent set is sensitivityonly. Fifteen explicit zero Senate
contexts differ from39president-only unavailableSenate cases. Keep raw first
Senate row's archive/member/byteoffset key separate from literalnativecode and
current legal/reporting identities.

Technical root/nested/setup are nonadditive export views, not successive snapshots
with a proven correction chronology. Board official controls and courtesy
download roles remain distinct. Bounded independent baseline/reciprocal source agreement and external historical dispatch are
accepted; current/legal/eligible-writein approval remains unavailable. Complete candidates/methods/nulls/ballot-registration availability and
write-in publication discrepancies survive; no exact eligible pool or November
preference can be inferred from them.


[Full historical authority replay](data/coordinator-priority-validation.json) passes1,702,375checks across every complete root,384companions and1,699,508recursive objects. Deep official/map research targets242ordered historical source contexts under37municipal parents, while every458Senate/497inventory/39municipal+fouradmin scope remains in statewide coverage. The full parent set is43; retain its municipal and administrative roles rather than synthesizing county reporting units. The producer contract remains byte-frozen, including its original pending-peer descriptive string; external captured-source proofs establish bounded agreement without changing producer flags.

The original Board write-in detail is now correctly1,227/eight local discrepancies; the old row6-only1,226/nine remains historical evidence. Both stay separate from municipal generic1,239/state1,244 and from a legally eligible named-writein universe. No ballot or choice is added/allocated. Historical2020sameClassII and2024otherClassI Senate preferences and source-specific volume/methods are conditional anchors, not2026candidate/turnout predictions. The16saved scenarios include all nonpriority/federal source votes, and the47independentCLI cases verify counted-fixed/final-denominator/unknown/no-pool and bounded arithmetic; they do not supply remaining-ballot estimates or calibrated win probabilities.
