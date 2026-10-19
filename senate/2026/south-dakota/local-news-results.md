# South Dakota regional results and NYT backstops

Coordinator preparation observed **October18,2026 UTC**, with a separate **October19** bounded recheck. [Original35 captures](data/news/manifest.json) remain unchanged; the [six newer observations](data/news/coordinator-oct19-recheck/review.json) preserve complete individual bodies/errors, headers, retrieval UTC and hashes. All four research questions and independent integration review are complete with explicit source limits. No genuine November vote sequence or calibrated model is claimed.

| Region / source | Inspected channel | Finding and use |
| --- | --- | --- |
| Sioux Falls / east — Dakota News Now | [Results](https://www.dakotanewsnow.com/politics/election-results/) linked from its homepage | HTTP 200; raw GSync selection is null with `displayTestData:true`. Current newsroom reporting is available, but a November count product, upstream supplier and cadence remain unverified. |
| Sioux Falls / statewide — KELOLAND | [Homepage](https://www.keloland.com/) | HTTP 403. A November Senate scoreboard, county detail and supplier were not established; keep a manual reporting lane and verify actual access in preflight. |
| Rapid City / Black Hills — NewsCenter1 | [Homepage](https://www.newscenter1.tv/) | HTTP 200 with actual current November election-story links. No parseable Senate count dataset or publication cadence established. Useful regional original reporting/manual candidate. |
| National — New York Times | [Elections hub](https://www.nytimes.com/section/politics/elections) | HTTP 403 challenge. Verify the actual November South Dakota Senate page manually until access, geographic detail and supplier are established. |

The official [results media page](https://electionresults.sd.gov/ResultsMedia.aspx) returned 200 selecting **November 3, 2026 general election**, displaying zero ballots and zero fully/partially reported precincts, with **673** total and explicit **Testing In Progress**. Its displayed source update is October 15, 12:24 p.m. CT. The page actually links a [statewide CSV export](https://electionresults.sd.gov/resultsCSV.aspx?text=All&type=SWR&map=CTY), which was downloaded, rather than guessed from a URL pattern.

The export's Senate setup has race `14412`, candidate `24967` Mike Rounds (`REP`) and `24887` Brian L Bengs (`IND`), zero votes and `0/656` reporting. Preserve exact raw whitespace and labels. Independent original OOXML review of all39 tested public exports finds the same statewide65-sheet/654-leaf scope, with Charles Mix absent. County form requests return statewide data. The turnout service separately has66 county objects and673 total precincts; Brookings10versus5, Hughes6versus3 and absent Charles Mix11 explain its19-unit difference from654, but do not explain the656 Senate banner. The actual autocomplete uses shared Senate search ID215, distinct from race/choice IDs. See the [complete raw-source review](data/coordinator-finished-official-review.json). The generated export clock has no confirmed timezone and is not a vote update. Quoted spreadsheet completion cells and trailing empty CSV fields need explicit parsing.

The **Independent** label matters. Actual linked [Lincoln publication ballot](https://www.lincolncountysd.gov/DocumentCenter/View/1989/Sample-Ballot-2026-PDF) and [Hanson sample ballot](https://www.hansoncountysd.gov/wp-content/uploads/2026/09/Ballot.pdf) originals now return200 and independently viewed first pages show Rounds Republican/Bengs Independent. [Exact original and visual pins](data/coordinator-current-ballot-law-visual-review.json) preserve this stronger later observation; earlier first-pair Lincoln404 evidence remains unchanged. These bounded samples do not exhaust later signed statewide ballot scope. Do not carry a prior-cycle Democratic nomination into current identity. The [baseline report](county-partisanship.md) separates historical party labels, named candidate preferences and current coalition assumptions.

Keep all **66 counties** in statewide arithmetic; the [turnout](turnout.md) and [official-source](official-results.md) reports retain complete native coverage and the qualified source-only priority. County administrative relationships and reporting-unit changes need explicit treatment, including historical Shannon/Oglala Lakota labels where relevant; do not join names blindly. Central-state, reservation-specific and other local original newsroom reporting inspections remain gaps beyond the regional candidates above. South Dakota spans Central/Mountain time; preserve local timezone and closing/extension evidence.

Retain source/supplier, election/contest, county FIPS/native unit/method, candidate key, unofficial/certified status, publisher time/timezone, retrieval UTC and raw evidence. Compare matched geography and compatible releases. State/county/newsroom totals, repeated cumulative snapshots and shared suppliers overlap; fallback replaces matching coverage with a documented reason, never adds duplicate votes. Preserve decreases, candidate reassignment and unmatched units.

Original regional reports about processing, delayed batches or board estimates can inform remaining-vote ranges with attribution/time; completion percentages and generated clocks cannot supply exact votes remaining. Keep race calls and NYT/model forecasts separate from counts. The live strategy will integrate current rules and actual official-worker findings. No continuous collector or measured November cadence is claimed.

The [primary candidate-status audit](data/coordinator-candidate-preflight.json) now retains current SOS general-list rows showing BengsIndependent/RoundsRepublican active and the Democratic nominee withdrawnAugust4. This repairs reliance on a test result label alone; it does not convert setup into counts or exhaust later ballot/write-in changes. April primary-petition validation remains a separately dated source.


The separate October19 recheck again found Dakota News Now selected-election
null with global test data enabled, KELO/NYT403, and NewsCenter1's homepage200
without an admitted Senate count product. The actual state-linked CSV retained
19 raw rows, a14-cell header and15-cell data rows including the trailing empty
field. Senate14412's two zero choice rows still have0/656, while the media
page overall denominator is673. Its `CurrentDateTime` literal
`10/19/2026 9:22:39 PM` is a generated download clock with unconfirmed zone,
not a new vote publication; the media source clock remains October15,12:24PM CT.
The [recheck README](data/news/coordinator-oct19-recheck/README.md) explains
the exact old-ledger scope and preserved initial label-parser correction.

The accepted [304-row priority](data/coordinator-priority-acceptance.json) is
strictly the historical public2024 presidential source, with691 rows/all66
parents and387 remainder. Its194-vote gap from signed totals prevents certified
native membership robustness. Keep this source limit visible in any coverage
comparison; the21-county concentration sensitivity cannot replace it.
