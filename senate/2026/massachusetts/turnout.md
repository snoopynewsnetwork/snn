# Massachusetts vote-volume ranking

Research completed October 19 Central / October 20, 2026 UTC. **Primary dispatch: all 2,394 literal 2024 Senate City/Town, Ward, Pct source contexts, ranked by Elizabeth Ann Warren plus John Deaton votes.** This exact named-source universe totals **3,407,108**. The top 15 contribute **58,012 / 3,407,108 = 1.702675700330016%** (reduced share 14,503/851,777). The minimum descending set reaching 80% contains **1,470 contexts**, contributing **2,726,450 / 3,407,108 = 80.022411969330%** (share 1,363,225/1,703,554). These are calculations from the [official native CSV](https://electionstats.state.ma.us/elections/download/165304/precincts_include:1/), independently extracted from its complete original bytes.

The preceding **1,469** contexts contribute **2,725,231 = 79.986633825520%**. **Northampton, Ward `3`, Pct `B`**, with **1,219** named votes, crosses the threshold. Integer proof: `5 × 2,725,231 < 4 × 3,407,108 ≤ 5 × 2,726,450`. Because the contexts are sorted largest first, no 1,469-context set can reach 80%. The **924-context remainder contributes 680,658** votes and remains in every state sum. The exact ordered priority and remainder are in [priority-set.json](data/turnout/priority-set.json), [priority CSV](data/turnout/ordered-priority-native.csv), [remainder CSV](data/turnout/ordered-remainder-native.csv), and the [complete 2,394-row order](data/turnout/all-native-order.md). [Primary source](https://electionstats.state.ma.us/elections/download/165304/precincts_include:1/).

The source's **All Others 6,221** is retained separately. The selected exports do not allocate it to named or legally eligible write-ins. The primary named ranking is therefore source-exact, not an exhaustive eligible-write-in ranking. The separately complete named-plus-generic sensitivity is **3,413,329**. Blanks **99,601** bring source **Total Votes Cast to 3,512,930**. Candidate votes are not ballots cast. No legal/write-in robustness follows from the sensitivity's matching membership. [Official contest presentation](https://electionstats.state.ma.us/elections/view/165304/).

## Exact top 15 native contexts

The literal Ward dash and precinct letters are source strings. Their presentation does not establish physical precinct size, a polling site, an absentee board or current boundaries. Sort ties by exact original City/Town, Ward, Pct tuple lexicographically, then original record ordinal only if needed. All raw strings and positions survive. [Official native export](https://electionstats.state.ma.us/elections/download/165304/precincts_include:1/).

| Rank | City/Town | Ward | Pct | Named votes | Cumulative votes |
| ---: | --- | --- | --- | ---: | ---: |
| 1 | Nantucket | `-` | `1` | 6,992 | 6,992 |
| 2 | Eastham | `-` | `1` | 4,088 | 11,080 |
| 3 | Rowley | `-` | `1` | 4,035 | 15,115 |
| 4 | Harvard | `-` | `1` | 3,958 | 19,073 |
| 5 | Rochester | `-` | `1` | 3,945 | 23,018 |
| 6 | Dover | `-` | `1` | 3,667 | 26,685 |
| 7 | Bolton | `-` | `1` | 3,649 | 30,334 |
| 8 | Shirley | `-` | `1` | 3,613 | 33,947 |
| 9 | Marion | `-` | `1` | 3,604 | 37,551 |
| 10 | Manchester-by-the-Sea | `-` | `1` | 3,566 | 41,117 |
| 11 | Hopedale | `-` | `1` | 3,525 | 44,642 |
| 12 | Plymouth | `-` | `15` | 3,397 | 48,039 |
| 13 | Carlisle | `-` | `1` | 3,381 | 51,420 |
| 14 | Boylston | `-` | `1` | 3,315 | 54,735 |
| 15 | Hadley | `-` | `1` | 3,277 | 58,012 |

The primary priority contexts span **287** literal municipal names; that does not expand the native priority into all children of those municipalities. Every child, including nonpriority children, appears in the contract's full **351-parent map**. [Source export](https://electionstats.state.ma.us/elections/download/165304/precincts_include:1/).

## Historical election and candidate controls

The 2026 regular race is **Class II**. The [Senate Class II roster](https://www.senate.gov/senators/Class_II.htm) identifies Markey and the 2020 term cycle. [2020 Markey–O'Connor–Ayyadurai](https://electionstats.state.ma.us/elections/view/140755/) is the same-seat baseline; [2024 Warren–Deaton](https://electionstats.state.ma.us/elections/view/165304/) is the other Class I seat and the requested recent priority contest. [2024 president](https://electionstats.state.ma.us/elections/view/165300/) is separate. The actual recent midterm comparator is [2022 governor](https://electionstats.state.ma.us/elections/view/154338/), not a nonexistent 2022 Massachusetts Senate contest. The observed [official 2022 Senate General search](https://electionstats.state.ma.us/elections/search/?year_from=2022&year_to=2022&office_id=6&stage=General) is retained separately. Future ballot/current geometry/feed approval is external to this historical ranking.

Every named candidate/ticket, generic category and control in both original CSVs is retained. All **351** parents occur in every contest. For every column, native sums match their municipal parent, municipal sums match the state CSV footer, and that footer matches the same HTML page's state footer. The four contests provide **9,828 municipal-to-native field comparisons**, with no rescaling, residual allocation, guessed zeros or candidate-key deduplication. Both original state footer records are retained. [2024 Senate exports](https://electionstats.state.ma.us/elections/view/165304/), [2020 Senate exports](https://electionstats.state.ma.us/elections/view/140755/), [2022 governor exports](https://electionstats.state.ma.us/elections/view/154338/), [2024 president exports](https://electionstats.state.ma.us/elections/view/165300/).

| Contest | Native contexts | Named source votes | All Others | Named + All Others | Blanks | Source Total Votes Cast |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2024 Senate (other Class I seat) | 2,394 | 3,407,108 | 6,221 | 3,413,329 | 99,601 | 3,512,930 |
| 2020 Senate (same Class II seat) | 2,173 | 3,556,708 | 7,428 | 3,564,136 | 93,869 | 3,658,005 |
| 2022 Governor (recent midterm) | 2,390 | 2,482,990 | 2,806 | 2,485,796 | 25,665 | 2,511,461 |
| 2024 President (separate contest) | 2,394 | 3,453,931 | 19,737 | 3,473,668 | 39,262 | 3,512,930 |

**2024-senate.** [Official view](https://electionstats.state.ma.us/elections/view/165304/), [municipal CSV](https://electionstats.state.ma.us/elections/download/165304/precincts_include:0/), [native CSV](https://electionstats.state.ma.us/elections/download/165304/precincts_include:1/).

| Literal CSV candidate/ticket | CSV party text | HTML display | State votes |
| --- | --- | --- | ---: |
| Elizabeth Ann Warren | Democratic | Democratic | 2,041,668 |
| John Deaton | Republican | Republican | 1,365,440 |

**2020-senate.** [Official view](https://electionstats.state.ma.us/elections/view/140755/), [municipal CSV](https://electionstats.state.ma.us/elections/download/140755/precincts_include:0/), [native CSV](https://electionstats.state.ma.us/elections/download/140755/precincts_include:1/).

| Literal CSV candidate/ticket | CSV party text | HTML display | State votes |
| --- | --- | --- | ---: |
| Edward J. Markey | Democratic | Democratic | 2,357,809 |
| Kevin J. O'Connor | Republican | Republican | 1,177,765 |
| Shiva Ayyadurai | Republican | Write-In | 21,134 |

**2022-governor.** [Official view](https://electionstats.state.ma.us/elections/view/154338/), [municipal CSV](https://electionstats.state.ma.us/elections/download/154338/precincts_include:0/), [native CSV](https://electionstats.state.ma.us/elections/download/154338/precincts_include:1/).

| Literal CSV candidate/ticket | CSV party text | HTML display | State votes |
| --- | --- | --- | ---: |
| Maura Healey | Democratic | Democratic | 1,584,403 |
| Geoff Diehl | Republican | Republican | 859,343 |
| Kevin Reed | Libertarian | Libertarian | 39,244 |

**2024-president.** [Official view](https://electionstats.state.ma.us/elections/view/165300/), [municipal CSV](https://electionstats.state.ma.us/elections/download/165300/precincts_include:0/), [native CSV](https://electionstats.state.ma.us/elections/download/165300/precincts_include:1/).

| Literal CSV candidate/ticket | CSV party text | HTML display | State votes |
| --- | --- | --- | ---: |
| Harris/ Walz | Democratic | Democratic | 2,126,518 |
| Trump/ Vance | Republican | Republican | 1,251,303 |
| Stein/ Caballero-Roca | Unenrolled | Unenrolled | 26,545 |
| Ayyadurai/ Ellis | Unenrolled | Unenrolled | 18,418 |
| Oliver/ Ter Maat | Libertarian | Libertarian | 17,735 |
| De La Cruz/ Garcia | Unenrolled | Unenrolled | 12,889 |
| Sonski/ Onak | Unenrolled | Write-In | 280 |
| West/ Abdullah | Unenrolled | Write-In | 243 |

The 2024 [printed-candidate page](https://www.sec.state.ma.us/divisions/elections/research-and-statistics/2024_state_election_candidates.htm) lists Warren (Democratic) and Deaton (Republican) for Senate. Source-specific metadata remains intact: 2020 Shiva is **Republican in the CSV party row, Write-In in the HTML**; 2024 Sonski and West are **Unenrolled in CSV, Write-In in HTML**. The 2024 presidential printed ballot labels also differ from some PD43 Unenrolled labels (for example Stein, Ayyadurai and De La Cruz). These are separate source fields, not inferred coalitions or changes to raw votes. No Senate named-write-in allocation has been manufactured from All Others.

## Disjoint hierarchy and source discrepancies

The [municipal CSV](https://electionstats.state.ma.us/elections/download/165304/precincts_include:0/) supplies 351 overlapping parent controls. The [native CSV](https://electionstats.state.ma.us/elections/download/165304/precincts_include:1/) supplies the disjoint state sum used for dispatch. City totals, ward groups and precinct/detail contexts cannot be added together. The compatibility filename [county-turnout.csv](data/county-turnout.csv) contains **2,394 native rows and zero county substitutions**. Its blank optional fields mean unavailable. State FIPS `25` is meaningful; no municipal/native FIPS or numeric native ID is supplied by the selected CSV. HTML county locality IDs and candidate-ID-bearing headers are preserved separately in extraction assets.

Native rosters are **2,173 (2020), 2,390 (2022), 2,394 (2024)**. In the 2022 native export, **118 rows leave both Ward and Pct empty**; each is that municipality's sole native context. They remain explicit unallocated municipal cases. The 2024 contexts all have nonempty Ward/Pct strings. Ward `-`, letter wards/precincts, `AN`, `AS`, `BE`, `BW`, suffixes such as `1A` and `21C`, and other literal strings remain untouched. These exports do not distinguish polling sites, ballot styles, central absentee/early groups, or administrative allocations. No separately labeled administrative row is exposed; this does not prove administrative votes are absent. Numeric method/native IDs, native registration and separate under/over counts remain null. [2022 native source](https://electionstats.state.ma.us/elections/download/154338/precincts_include:1/), [2024 native source](https://electionstats.state.ma.us/elections/download/165304/precincts_include:1/).

The [2022 governor HTML county rows](https://electionstats.state.ma.us/elections/view/154338/) have a material independent source discrepancy. Their sum is **Healey 1,581,214; Diehl 859,433; Reed 39,205; All Others 2,794; Blanks 25,652; Total 2,508,298**. County-sum minus that same page's state footer (and both reconciled CSVs) is **[-3,189, +90, -39, -12, -13, -3,163]** in that order. All 14 rows and their original positions survive. No cause, chronology, corrected local allocation, or county substitution is inferred. The other three selected HTML county presentations balance their own state footers.

Source labels/counts alone do not establish equal historical boundaries, a current legal precinct or a November 2026 reporting identity. No cross-year native join is used. Repeated municipal labels support a separately labeled source-level municipal comparison only, without an asserted geometry crosswalk.

## Full volume sensitivities and recent midterm comparison

Each row below has its own complete descending order in [orders/](data/turnout/orders/) and exact summary in [ranking-summaries.json](data/turnout/ranking-summaries.json). Primary source [municipal/native exports](https://electionstats.state.ma.us/elections/view/165304/) remain independent overlapping levels.

| Scope/universe | State denominator | Top 15 votes (%) | Preceding count / votes | Minimum80 count / votes (%) | Crossing literal tuple |
| --- | ---: | ---: | ---: | ---: | --- |
| Primary native named | 3,407,108 | 58,012 (1.7026757003%) | 1,469 / 2,725,231 | 1,470 / 2,726,450 (80.0224119693%) | `["Northampton", "3", "B"]` |
| Native named + generic All Others | 3,413,329 | 58,115 (1.7025900521%) | 1,469 / 2,729,603 | 1,470 / 2,730,825 (80.0047402404%) | `["Northampton", "3", "B"]` |
| Native source Total Votes Cast | 3,512,930 | 59,382 (1.6903838107%) | 1,474 / 2,809,408 | 1,475 / 2,810,661 (80.0090238063%) | `["Methuen", "-", "15"]` |
| Municipal named sensitivity | 3,407,108 | 806,406 (23.6683427705%) | 146 / 2,724,336 | 147 / 2,732,538 (80.2010972355%) | `["Chelsea", "", ""]` |
| Municipal named + All Others | 3,413,329 | 808,775 (23.6946101592%) | 146 / 2,729,748 | 147 / 2,737,950 (80.2134807398%) | `["Chelsea", "", ""]` |
| Municipal source Total Votes Cast | 3,512,930 | 836,454 (23.8107221038%) | 145 / 2,804,372 | 146 / 2,812,907 (80.0729590399%) | `["Medway", "", ""]` |

Adding the reported generic All Others changes **1,820 rank positions** but leaves the primary min80 membership unchanged. Ranking source TBC changes **2,255 positions**; its min80 adds nine contexts and removes four (net +5). Full added/removed lists and primary-set volume under each sensitivity are in [sensitivity-impacts.json](data/turnout/sensitivity-impacts.json). These are measured source-universe effects, not an eligible-write-in guarantee or an independent native ballot audit. The source-ordinal tie alternative changes **39 positions**, with **0 added / 0 removed** priority keys, and the same minimum count/volume; its complete order is [explicitly preserved](data/turnout/alternative-order-presentation.json).

Independent extraction splits the observed **6,221 All Others into 4,375 inside the fixed 1,470-context priority and 1,846 outside**. Conditional integer algebra shows that **955 additional genuinely eligible votes wholly outside that fixed set, with none inside, would break its 80% coverage**: 954 would not. Separately, **2,277 additional genuinely eligible votes wholly inside the fixed first 1,469 contexts, with none outside, would let those 1,469 reach 80%**: 2,276 would not. These are counterfactual bounds, not actual eligibility/allocation, a recomputed eligible-vote order, or a claim about the legal minimum cardinality. The source-known named order remains exact. [Independent calculation](data/turnout/writein-scope-bounds.json), from the [original native CSV](https://electionstats.state.ma.us/elections/download/165304/precincts_include:1/).

The separate **351-municipality named sensitivity** has top15 **806,406 / 3,407,108 = 23.668342770467%**; **147** municipalities reach **2,732,538 = 80.201097235544%**. The preceding **146** contribute **2,724,336 = 79.960365212961%**; **Chelsea (8,202)** crosses. Its ordered top15 is Boston, Worcester, Springfield, Cambridge, Newton, Quincy, Plymouth, Somerville, Brockton, New Bedford, Lowell, Weymouth, Lynn, Haverhill, Fall River. This municipal order is not the primary dispatch substitute. Every municipality and child remains in the complete map. [Official municipal source](https://electionstats.state.ma.us/elections/download/165304/precincts_include:0/).

Historical native rankings use each contest's own source roster and named universe:

| Contest | Contexts | Top15 votes (%) | Preceding count / votes | Minimum80 count / votes (%) | Crossing tuple |
| --- | ---: | ---: | ---: | ---: | --- |
| 2020-senate | 2,173 | 67,695 (1.9033049663%) | 1,408 / 2,845,033 | 1,409 / 2,846,374 (80.0283295677%) | `["Chicopee", "8", "B"]` |
| 2022-governor | 2,390 | 44,905 (1.8085050685%) | 1,408 / 1,985,619 | 1,409 / 1,986,515 (80.0049537050%) | `["Holbrook", "-", "4"]` |
| 2024-president | 2,394 | 58,274 (1.6871790432%) | 1,475 / 2,762,216 | 1,476 / 2,763,448 (80.0087784035%) | `["Westhampton", "-", "1"]` |

The actual 2022 governor named volume is **2,482,990**, or **924,118 fewer** than 2024 Senate named volume. This compares different contests, candidates, years and source rosters; it does not isolate participation effects. Its full native min80 has **1,409 contexts**, with **1,985,619** votes before Holbrook `-`/`4` adds **896**, reaching **1,986,515**. Its separate municipal min80 is **148**, crossing Lynnfield at **1,986,761 / 2,482,990 = 80.014861115027%**. No 2024 native priority is forced onto 2022 units. [Actual 2022 governor native and municipal downloads](https://electionstats.state.ma.us/elections/view/154338/).

## Ballots, methods and registration retain source scope

The [Secretary's turnout table](https://www.sec.state.ma.us/divisions/elections/research-and-statistics/voter-turnout-statistics.htm) and [ballot-method page](https://www.sec.state.ma.us/divisions/elections/research-and-statistics/early-voting-statistics.htm) were inspected in the research browser. Direct HTML, XLSX and registration PDF requests returned 403; alternate official bare-host requests timed out and the accessible registration route also returned 403. Complete error bodies/receipts and browser text observations are retained. **The original statistical workbooks/PDFs were not downloaded successfully.** No local method/registration table or ranking is claimed from those blocked files.

| Year | Registration date | Registered voters | Turnout table total | Printed rate | Method page ballots | PD43 contest TBC |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2020 | 2020-10-24 | 4,812,909 | 3,657,972 | 76.00% | 3,657,972 | 3,658,005 |
| 2022 | 2022-10-29 | 4,884,076 | 2,511,461 | 51.42% | 2,511,461 | 2,511,461 |
| 2024 | 2024-10-26 | 5,142,343 | 3,512,930 | 68.31% | 3,512,866 | 3,512,930 |

Registration dates are independently visible in the primary [2020 PDF title](https://www.sec.state.ma.us/divisions/elections/download/registration/enrollment_count_20201024.pdf), [2022 PDF title](https://www.sec.state.ma.us/divisions/elections/download/research-and-statistics/enrollment_count_20221029.pdf), and [2024 PDF title](https://www.sec.state.ma.us/divisions/elections/download/research-and-statistics/enrollment_count_20241105.pdf). These are registered-voter stocks, without an inferred active-only or voting-eligible population definition. The statewide rates are printed source rates; no rounded rate is used to derive an integer count or local allocation.

The ballot-method page prints mail/early/Election Day shares **41.7% / 23.1% / 35.2% (2020)**, **37.3% / 7.5% / 55.2% (2022)** and **34.2% / 17.0% / 48.8% (2024)**. They remain rounded percentages, with exact method integers unavailable. Its 2024 ballots are **64 below PD43/TBC and the turnout table**. In 2020, PD43/TBC is **33 above both the turnout and method pages**. In 2022 these totals agree. Differences remain source-scoped and unallocated. The 2024 named-to-TBC gap **105,822** comprises the reported **6,221 All Others plus 99,601 Blanks**; only the latter is a published blank category. Separate undervotes/overvotes are unavailable. [Source method publication](https://www.sec.state.ma.us/divisions/elections/research-and-statistics/early-voting-statistics.htm).

## Publication authority, provenance and completion gates

The [Secretary's current election page](https://www.sec.state.ma.us/divisions/elections/elections-and-voting.htm) says results are published after certification, not on Election Night. The [certification explanation](https://www.sec.state.ma.us/divisions/elections/voting-information/announcing-certifying.htm) identifies local clerks as certifiers and describes local unofficial releases, which are not submitted to the state as an ENR feed. It says election-night totals combine methods and can omit unresolved ballot categories. The PD43 service is therefore a historical certified-result publication, not a demonstrated live collector. Exact certification/revision dates for these particular downloads are not supplied in the CSV. HTTP retrieval/cache clocks are not result-update clocks.

Actual municipal authority/access is demonstrated by [Worcester's official results inventory](https://www.worcesterma.gov/elections/election-results): its Election Office publishes linked election-night reports as PDFs, including the acquired [November 5, 2024 original](https://www.worcesterma.gov/election-results/20241105.pdf). Its [stream page](https://www.worcesterma.gov/results) currently embeds a video explicitly titled State Primary Election Results. Independent inspection of the pinned original HTML confirms those literal links/title. This is a municipal channel example, not verified November availability, a full 351-municipality live-source inventory or a known cadence. Those require the separate official-results assignment after coordinator priority acceptance.

The [frozen source receipts](data/turnout/source/shared-originals.json), [municipal authority pins](data/turnout/source/municipal-authority-originals.json), new source receipt files, [schema](data/turnout/source/SCHEMA.md), [asset manifest](data/turnout/asset-manifest.json), [offline validation](data/turnout/validation.json), and [final seal](data/turnout/final-seal.json) provide source/download chains, exact URLs, UTC/HTTP evidence where available, hashes/sizes, raw positions, original scope and reproducible calculations. New current official Senate municipal/native CSV observations match the launch originals byte-for-byte. All full original bytes, including fields outside the selected scope, remain intact. Gzip is lossless, with no object at or above 40,000,000 bytes.

Run the commands in [SCHEMA.md](data/turnout/source/SCHEMA.md) for an offline rebuild and seal. The independent validator re-parses original CSVs, checks every candidate/control/native/parent position, all 24 complete orders, exact weights, integer crossings, null semantics, source discrepancies, mutable-input failures, links and hashes. The reviewed shared primary preflight was replayed with its only output directory redirected into `data/turnout/preflight-replay/`; its 1,755 comparisons agree, but that preparation is not an independent peer.

## Bounded reciprocal review and final packaging

Actual baseline worker **41e0bf1a-4609-4a2a-b901-568567431a57** finished before this same turnout worker resumed. Before any owned edit or peer comparison, this worker captured its [exact current pre-review bodies](data/turnout/peer-review-freeze/reciprocal-resume-v1/snapshot-manifest.json), preserving the earlier [original-first witness](data/turnout/peer-review-freeze/original-first-v1/snapshot-manifest.json) byte-exact (manifest SHA256 `707dcec048f01fa8d557087c142e0f50fce924b7ff089ea97a384d3d16860846`). The [actual final baseline capture](data/turnout/peer-review-freeze/baseline-final-v1/snapshot-manifest.json) freezes **all 257 owned baseline assets plus its manifest**, with **18 read-only original input pins**. Its captured baseline manifest SHA256 is `1121b89786ec0e5decaed86116d18f8e6aef7f28003f5224a976f742a2ce2c40`; captured baseline report is `8b34a7917a4e5eb0a0ca553d6319dcdc21af95e5e87610b370a68e468fd847ab` and CSV is `dd78ad8968c56a6375e267cdcd2c05db223d3940a9b9f0bdf2cc0879b3effa72`. These identify compared bodies, not an implied later-current byte equality.

The independent [reciprocal audit](data/turnout/peer-audit/comparison.json), reproducible with [audit_peer.py](data/turnout/audit_peer.py), passes **10,755 complete native/municipal objects**, **75,510 candidate/control fields**, **75,566 source-position objects**, all candidate/header/ragged-party/HTML metadata and shared null/method fields, all **9,351 native baseline CSV records**, all four contests' **351-parent child/ward maps**, and all **24 shared full descending orders**. Turnout `named_source_votes` maps explicitly to baseline `all_named`, not its narrower `named_pair` in contests with additional named candidates. The eight extra baseline pair orders and calculator/scenario outputs are outside this shared turnout audit. Source-position object arrays have a preserved presentation difference: baseline places each scope footer beside its scope; turnout appends both footers. All unique scope/record/column objects match completely. Original arrays are retained without rewriting.

The primary **2,394-context order, 1,470-context priority, 924-context remainder and all 351 parent/child maps agree exactly**. The captured baseline's own reciprocal witness explicitly audited turnout's original-first-v1 bodies. This review verifies that limited reverse scope, without claiming it compared later turnout metadata. Turnout's source counts, original extraction objects, 24 orders and compatibility CSV remain byte-exact original-first. Only review/report/reproduction/sealing metadata changed. Baseline supplemental browser registration observations, including its 347 municipal records, remain separately scoped peer evidence and are not imported as this worker's direct original reading.

The final manifest includes **every owned file except `asset-manifest.json` itself**, including validation and final seal. Neither validation nor final seal embeds the current manifest digest, so there is no reverse hash cycle. Earlier excluded/cyclic-phase manifests, validations and seals remain exact in the frozen history. Offline sealing performs complete membership/hash/byte/link/no-cache checks after constructing the final manifest, and an external handoff pins that manifest.

**Bounded independent peer agreement is established; formal coordinator acceptance and current geometry approval remain false.** This historical agreement does not authorize current/legal native IDs, eligible-write-in allocation, a live feed or second-wave dispatch. Material gaps remain the named/eligible allocation inside All Others, separate native methods/under/over/registration, original blocked statistical downloads/local controls, historical/current boundary equivalence, and full municipal November access/cadence. No implemented collector, calibrated Needle or real 2026 turnout forecast is claimed.
