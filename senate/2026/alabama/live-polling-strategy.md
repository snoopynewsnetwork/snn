# Alabama collection and remaining-vote strategy

Prepared **2026-10-18 UTC / 2026-10-17 Central**. Historical first-pair/source authority review is complete; original official-results/maps workers are active and final integration remains pending. Read the [newsroom survey](local-news-results.md). No live collector or calibrated probability model is implemented.

## Alabama-specific preflight

The [SOS announcement](https://www.sos.alabama.gov/newsroom/secretary-state-wes-allen-announces-unofficial-primary-election-results-are-available) describes county-submitted **May 19 primary** returns, not November setup. Follow the current state/county election authority chain, actual Senate contest/date, complete candidate identities and source status. Parliamentary/district special-primary or redistricting changes do not automatically define the statewide Senate election or current precinct geometry; verify the actual legal/current source evidence.

All 67 counties and their native precinct/method units remain in statewide arithmetic. The reviewed source-known native80 set is887of2085records; downloaded boundary compatibility remains a separate maps question. Preserve county probate/election-official authority roles, native administrative records and overlap between county and state summaries. County/FIPS/name alone does not establish a valid precinct boundary crosswalk. Voting-method-specific partial returns require same-scope historical comparisons rather than a county average substituted for an early batch.

Alabama held no 2024 Senate contest. Distinguish 2024 president, 2022 Senate recent midterm/other seat and 2020 same-seat Senate, complete all-candidate counts and separate observed turnout anchors. Historical candidate and coalition effects remain conditional. The results question must verify current poll hours/timezone, absentee application versus return/receipt requirements, military/overseas exceptions, provisional/cure rules, canvass/certification and later controlling orders. Do not infer those from old newsroom captions.

WBRC has an empty/unselected cache; WSFA selects inactive general2743 with48races/97allzerochoices, including a zero Senate object. Both backend requests exclude testresults; separate UI displayTestData=true does not prove returned test votes. WTVY has a separate inactive24-race Alabama setup, not an independent official source or complete legal roster. Treat both as preflight state, not votes. WAFF's accessible homepage is reporting access only; Reflector/WKRG direct access failed. A November title, nonzero test tally or source transport timestamp cannot validate the election or remaining-ballot inventory.

## Proposed collection and revision handling

Start with 2-minute checks of a verified official release index/version around an announced election-night publication, fetching details only after a change. Use 5-minute checks for verified newsroom backstops and manual NYT observation where automated access fails. Outside announced windows, back off to 15 minutes or hourly during counting and daily through canvass/certification. These are implementation proposals, not observed publisher cadence. Use timeouts, bounded concurrency, jitter, conditional requests where supported and exponential backoff. A quiet source is not automatically an outage.

Resolve actual November navigation and verify election date, Senate title, complete candidate identities, zero/test status, unit/method coverage and source status before importing counts. HTTP 200, a current pathname, an old widget ID or visible candidate numbers is insufficient. Store original bytes, URL, UTC retrieval, HTTP/cache headers, hash, parser version, publisher timestamp/timezone and native election/contest/unit IDs. Reject challenge HTML and app shells. Keep a source-health ledger with last successful fetch, last genuine vote change, expected versus observed units, and manual-fallback reason.

Replace cumulative snapshots; derive compatible changes afterward and retain decreases, corrections and status changes. State, county, municipality/authority, precinct and method views may overlap. Pick a consistent authoritative scope rather than summing every product or averaging disagreements. External calls, estimated completion and probabilities remain separately attributed fields. Multiple AP products or shared newsroom reports are one upstream chain. Preserve a conflicting observation until scope/time/status explains it.

For a failed primary channel, capture the same official election page or linked PDF/export manually with URL, observation time, source status and original file/screenshot. Use newsroom figures only as an explicit temporary substitution for the same unit/method. Reconcile and replace with official counts once available; never silently combine different vintages. NYT access and actual November Senate product remain unverified in this preparation.

## Remaining votes and scenario readiness

Counted votes remain fixed. Estimate only uncounted ballots using documented unit/method inventories and explicit low/base/high ranges, with source/time and acceptance/counting status. Issued minus returned, registration minus turnout and reporting-precinct percentages do not equal remaining candidate votes. If accepted-unprocessed detail is absent, uncertainty remains unknown or bounded by stated assumptions; do not manufacture an exact total. Processed ballots, eligibility review, published candidate counts and certification are different stages.

Compare partial returns with the same historical geography/method and boundary vintage. No allocation through an unvalidated map crosswalk. Historical turnout volumes are sensitivity anchors, not 2026 projections. Tie/+1 conditional scenarios require complete statewide weights and candidate/other-vote reconciliation; distinguish share-point shifts from margin-point shifts. Do not substitute an independent candidate into a D/R coalition without explicit identity and assumptions.

Before live use, replay genuine dated releases and test idempotent retries, missing units, corrections/decreases, overlapping aggregates, candidate identity and manual recovery. Keep original counts and derivatives auditable. A calibrated win probability additionally requires a dated prior, genuine historical release sequences, remaining-ballot assumptions and held-out calibration under the [root plan](../../../ELECTION_NIGHT_PLAN.md). No live collector or calibrated Needle is implemented here. Final integration must insert the measured priority set, complete official inventory, downloaded map compatibility and verified current rules from the four state question assignments.


## Reviewed historical source scope

2024president has2085native source records/all67counties and2265090reported
candidate/generic marks. Top15=115428; preceding886=1811981; minimum887=1812818
crosses at Calhoun OAK GROVE BAPT+837. All1198remainder/452272marks and63priority
parents remain; county25sensitivity is not dispatch.2022Senate2074/1414238 and
2020same-seatSenate2111/2316445 retain separate candidates and source vintages.
The full201originalXLSmembers preserve raw typed cells, headers, named/generic
and administration. Generic8738 remains legally unallocated. Three PDFblank/dash
cells stay null despite independently observed nativeXLS0. Cleburne2024ballots−180,
Cullman2022+90 and registration/under-over gaps stay unallocated. Historical
labels/columns/FIPS do not approve2026reporting IDs, physical sites or geography.

The [complete historical source authority](data/coordinator-priority-acceptance.json)
and [independent exhaustive replay](data/coordinator-priority-validation.json)
freeze every full source object, hierarchy and preservation history. They
approve bounded source research only; no current/legal/eligiblewritein/native80/
leaf/polygon/cadence/pool/forecast/calibration admission follows. Official current
rules, channels and map compatibility remain separate assignments. Proposed
cadences above are proposals, not demonstrated release intervals.
