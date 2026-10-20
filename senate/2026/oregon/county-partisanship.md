**Oregon historical partisanship and conditional paths — research snapshot 2026-10-20**

The complete **36-county** controls support historical conditional arithmetic. They do not establish a 2026 forecast. Harris's 2024 presidential pair led Trump by 321,120 votes; repeating those county pair weights gives a tie after a **−7.433058 A-share-point** shift, or an illustrative A+1 pair margin after **−6.933058 points**. Negative shifts mean the historical baseline already wins that pair comparison. They are alternative statewide combinations, not required improvements in every county. The complete [official 2024 abstract, archived December 12](https://web.archive.org/web/20241212212240id_/https://sos.oregon.gov/elections/Documents/results/november-general-2024-results.pdf), page 1, supplies all eight columns. [County baselines](data/county-baselines.csv) retain every parent and denominator.

The native geography is **partial**: five recovered 2024 county publications close 510 literal presidential rows, while 31 parents lack a closed native universe. Canonical statewide native order/top 15/minimum 80 and approved dispatch remain **unavailable/null**. County sensitivities never substitute for native dispatch. All current-source, current-geography and acceptance flags remain false pending coordinator review. No old contest/result ID or geometry follows from an archived label.

Oregon's 2026 regular election is Class II. 2020 Merkley is the same Senate seat; 2022 Wyden is the other Class III seat and a midterm. Oregon held no 2024 Senate contest. 2024 president is the priority basis; 2022 governor is a distinct substantial three-candidate sensitivity. These are separate electorates/contests, with no inferred candidate effect, lower preference, cross-year native join or 2026 boundary equivalence. The [2020 candidate abstract](https://records.sos.state.or.us/ORSOSCMSearch/Search/DocumentStream.ashx?uri=13735450), page 2, and [2022 candidate abstract](https://records.sos.state.or.us/ORSOSWebDrawer/Record/13735454/File/document), pages 1/4, are independently extracted from retained complete originals. The latter reconstructs from three contiguous HTTP 206 ranges; partial 500 prefixes are not full PDFs. [Source receipts and byte chains](data/baselines/source/original-read-receipts.json) retain all qualifications.

**Complete statewide candidates and denominators**

A/B below are named source candidates, not a coalition of all non-Republicans. Party abbreviations remain the source labels: D Democratic, R Republican, PG Pacific Green, P Progressive, L Libertarian, C Constitution, NAV Nonaffiliated, WTP We The People. Misc. is a generic reported scope, not proved legally valid named write-ins. Native source aliases/slate labels and party headers remain unchanged in [raw evidence](data/baselines/source/raw-native-rows.jsonl.gz) and [abstract headings](data/baselines/source/abstract-evidence.json). The overlapping six-column vice-president table is [retained nonadditively](data/baselines/nonadditive-vice-president.csv); no absent West/Terry partner column is invented.

| Contest | Complete candidate/Misc. vector in original column order | Reported all-choice total | Named-only total | A/B pair total | A−B net |
| --- | --- | ---: | ---: | ---: | ---: |
| 2024-president | Robert F Kennedy Jr (WTP) 33,733; Cornel West (P) 5,644; Chase Oliver (L) 9,061; Randall Terry (C) 1,850; Donald J Trump (R) 919,480; Jill Stein (PG) 19,099; Kamala D Harris (D) 1,240,600; Misc. 15,026 | 2,244,493 | 2,229,467 | 2,160,080 | +321,120 |
| 2020-senate | Jo Rae Perkins (R) 912,814; Jeff Merkley (D) 1,321,047; Ibrahim A Taher (PG) 42,239; Gary Dye (L) 42,747; Misc. 2,402 | 2,321,249 | 2,318,847 | 2,233,861 | +408,233 |
| 2022-senate | Jo Rae Perkins (R) 788,991; Dan Pulju (PG) 23,454; Ron Wyden (D) 1,076,424; Chris Henry (P) 36,883; Misc. 2,197 | 1,927,949 | 1,925,752 | 1,865,415 | +287,433 |
| 2022-governor | Tina Kotek (D) 917,074; Donice Noelle Smith (C) 8,051; R Leon Noble (L) 6,867; Betsy Johnson (NAV) 168,431; Christine Drazan (R) 850,347; Misc. 2,113 | 1,952,883 | 1,950,770 | 1,767,421 | +66,727 |

Every county candidate column sums exactly to the corresponding primary footer:864 source cells across the four contests. [Full county candidates](data/baselines/county-candidates.csv), [state controls](data/baselines/state-controls.json), source page/line/raw text, original SHA256 and retrieval clocks are retained. No rescaling, zero-filling, residual allocation or candidate-key deduplication is used.

The current [ORS 254.065 official publication](https://www.oregonlegislature.gov/bills_laws/ors/ors254.html), independently downloaded in [current receipts](data/baselines/source/current/network-ors254.receipt.json), specifies the highest vote count for a single office, subject to its stated exception. Pair tie/+1 arithmetic does not replace full-field plurality. Johnson's 168,431 NAV votes in 2022 governor remain separate from Kotek and Drazan; Smith and Noble also remain separate. Kotek's actual 917,074 of 1,952,883 reported choices is below 50% but above each named opponent. No RCV redistribution, runoff electorate or lower-preference estimate is inferred. Actual 2026 ballot candidates/labels must be mapped from final official publications; the [current filings page](https://sos.oregon.gov/elections/pages/candidate-filings-local-measures.aspx) inspected here does not establish a final complete Senate ballot. [Current-election navigation](https://sos.oregon.gov/elections/Pages/current-election.aspx) and primary nominees/old IDs are not substituted.

**Every county, including the nonpriority remainder**

Margins are historical **A−B pair-margin percentage points** for the named Democratic/Republican pair in that contest; other candidates are retained in the linked full-field table. A positive value describes that election's Democratic pair lead, not a permanent county identity. 2024 volume includes generic Misc. The table derives directly from the three cited official abstracts.

| County |2024 reported choices|2024 president pair margin|2020 same-seat Senate|2022 other-seat Senate|2022 governor|2024 native closed rows|
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Baker | 9,694 | -50.16 | -44.55 | -39.97 | -62.03 | unknown |
| Benton | 50,232 | +41.01 | +40.56 | +38.16 | +29.84 | unknown |
| Clackamas | 246,240 | +10.21 | +11.58 | +8.79 | -5.06 | 118 |
| Clatsop | 23,290 | +11.67 | +15.12 | +15.63 | +4.38 | unknown |
| Columbia | 31,334 | -14.38 | -5.19 | -9.26 | -25.09 | unknown |
| Coos | 35,735 | -20.58 | -14.79 | -16.70 | -32.71 | unknown |
| Crook | 16,297 | -51.59 | -44.00 | -45.26 | -64.86 | unknown |
| Curry | 14,200 | -16.47 | -12.87 | -14.91 | -27.41 | unknown |
| Deschutes | 127,375 | +10.78 | +10.10 | +10.48 | -3.73 | unknown |
| Douglas | 61,807 | -38.66 | -31.82 | -34.18 | -51.22 | unknown |
| Gilliam | 1,134 | -46.90 | -34.45 | -29.74 | -62.45 | unknown |
| Grant | 4,456 | -62.10 | -49.04 | -46.71 | -69.04 | unknown |
| Harney | 4,255 | -61.16 | -50.56 | -46.81 | -71.95 | unknown |
| Hood River | 12,707 | +36.91 | +38.57 | +34.93 | +24.88 | unknown |
| Jackson | 119,572 | -6.63 | -1.60 | -4.61 | -17.45 | unknown |
| Jefferson | 11,750 | -30.83 | -19.46 | -25.68 | -44.92 | unknown |
| Josephine | 49,628 | -29.55 | -22.71 | -25.52 | -40.75 | unknown |
| Klamath | 35,515 | -42.92 | -35.45 | -38.51 | -57.26 | unknown |
| Lake | 4,213 | -66.80 | -56.44 | -55.51 | -76.83 | unknown |
| Lane | 211,285 | +23.82 | +27.56 | +25.53 | +14.15 | unknown |
| Lincoln | 29,804 | +19.01 | +20.12 | +20.84 | +11.07 | unknown |
| Linn | 71,429 | -25.18 | -20.27 | -25.01 | -38.85 | unknown |
| Malheur | 10,945 | -45.55 | -40.31 | -46.94 | -61.39 | unknown |
| Marion | 156,691 | -2.06 | +2.62 | -3.95 | -15.99 | 118 |
| Morrow | 4,732 | -49.93 | -36.17 | -41.24 | -66.49 | unknown |
| Multnomah | 414,250 | +64.32 | +63.87 | +64.23 | +57.30 | 107 |
| Polk | 47,593 | -3.79 | -0.08 | -4.60 | -16.89 | unknown |
| Sherman | 1,163 | -58.50 | -47.34 | -49.75 | -73.39 | unknown |
| Tillamook | 16,252 | -1.43 | +3.47 | +1.90 | -11.47 | unknown |
| Umatilla | 31,225 | -38.78 | -27.70 | -36.27 | -53.17 | unknown |
| Union | 14,574 | -41.53 | -36.07 | -35.60 | -54.24 | unknown |
| Wallowa | 5,108 | -36.30 | -31.50 | -31.46 | -47.53 | unknown |
| Wasco | 13,391 | -5.95 | +1.08 | -1.64 | -18.91 | 12 |
| Washington | 297,949 | +35.16 | +34.77 | +31.85 | +21.50 | 155 |
| Wheeler | 868 | -49.28 | -42.29 | -39.46 | -60.89 | unknown |
| Yamhill | 57,800 | -6.35 | -2.33 | -6.26 | -19.16 | unknown |

**Historical volume, mix and preference sensitivities**

Low uses the actual 2022 Senate all-choice county volume 1,927,949; base uses actual 2024 president 2,244,493; high uses actual 2020 Senate 2,321,249. These settings deliberately change both historical total and county mix; their labels describe these selected historical anchors, not 2026 turnout forecasts or confidence bounds. A fourth actual-governor-volume case uses 1,952,883. Each preference anchor is separately 2024 president,2020 Senate,2022 Senate or 2022 governor. Within every county V is the selected source volume and pair volume is **V × that preference contest's county pair participation**. Other named/generic candidate fractions remain those of the preference contest. The full report settings match [calculator inputs and 26 scenarios](data/baselines/historical-scenarios.json).

| Preference anchor | Historical volume/mix | Expected pair pool | Baseline A−B net | Tie A-share shift points | A+1 A-share shift points |
| --- | --- | ---: | ---: | ---: | ---: |
| 2024-president | low: 2022-senate | 1,855,392.568 | +281,029.441 | -7.573315 | -7.073315 |
| 2024-president | base: 2024-president | 2,160,080.000 | +321,120.000 | -7.433058 | -6.933058 |
| 2024-president | high: 2020-senate | 2,233,729.905 | +351,437.256 | -7.866601 | -7.366601 |
| 2020-senate | low: 2022-senate | 1,855,512.058 | +328,665.603 | -8.856466 | -8.356466 |
| 2020-senate | base: 2024-president | 2,160,188.176 | +377,031.425 | -8.726819 | -8.226819 |
| 2020-senate | high: 2020-senate | 2,233,861.000 | +408,233.000 | -9.137386 | -8.637386 |
| 2022-senate | low: 2022-senate | 1,865,415.000 | +287,433.000 | -7.704264 | -7.204264 |
| 2022-senate | base: 2024-president | 2,171,764.436 | +328,344.496 | -7.559395 | -7.059395 |
| 2022-senate | high: 2020-senate | 2,245,718.987 | +358,430.043 | -7.980296 | -7.480296 |
| 2022-governor | low: 2022-senate | 1,744,922.124 | +67,820.585 | -1.943370 | -1.443370 |
| 2022-governor | base: 2024-president | 2,031,265.483 | +72,390.977 | -1.781918 | -1.281918 |
| 2022-governor | high: 2020-senate | 2,101,641.243 | +94,787.631 | -2.255086 | -1.755086 |
| 2022-governor | actual-governor: 2022-governor | 1,767,421.000 | +66,727.000 | -1.887694 | -1.387694 |

For fixed weights, unbounded tie shift=(B−A)/(2(A+B)); an A+1 pair-margin target adds. 005 share fraction, **0.5 share points**. A 1-point share gain creates 2 pair-margin points and. 02×pair-volume net votes. Share points, margin points and net votes are different outputs. For 2024 president the A+1 target is 21,600.8 net votes on 2,160,080 pair votes; its reported-all-choice margin is about 0.9624 points on 2,244,493, not 1 point on that denominator. The actual 2022 governor pair-volume tie shift is−1.887694 share points; +1 pair margin is−1.387694, while its all-choice margin is 0.905032 points. All other candidates remain explicit in each scenario, and the full-field named-opponent checks are saved separately.

The solver first displays the unbounded shift, clips every unit share to[0,1], then solves a feasible bounded shift with a residual check. These historical cases require no clipping, but executed synthetic fixtures exercise clipping. [936 county contribution rows](data/baselines/county-contributions.csv) retain all 36 parents, expected volumes, pair participation, weights, baseline/target net contributions and net-vote gains. [Every local native/county tie and +1 target](data/baselines/local-pair-targets.csv) remains source-scoped; unknown preference/volume is null. [Known-source native scenarios](data/baselines/known-native-scenarios.json) model only their explicitly stated closed historical pool, never an incomplete statewide native electorate.

**Selected-unit-only paths**

There is no unique required performance in a county. [County selected-only targets](data/baselines/county-selected-targets.csv) change only the selected county, holding every other county at its named historical preference, volume, mix and participation. [Native selected-only state targets](data/baselines/native-selected-state-targets.csv) change one column-closed source-local unit, with all 36 same-contest county totals and every other vote fixed at explicit aggregate historical assumptions. Unknown native rows stay unknown; no residual is assigned to an invented unit. Requirements below 0 remain secured-even-at-zero; above 1 remain impossible-even-at-one, alongside unbounded and clipped display shares. No-positive-pool and unknown cases remain separate.

For the base 2024 presidential tie, illustrative selected-county results are:

| Selected county only | Historical A pair share | Other-county net votes fixed | Required A share, unbounded | Status |
| --- | ---: | ---: | ---: | --- |
| Multnomah | 82.1625% | +65,952 | 41.6871% | feasible |
| Washington | 67.5809% | +220,697 | 11.3630% | feasible |
| Baker | 24.9176% | +325,837 | -1682.6226% | secured_even_at_zero |

**Native coverage, source scopes and exact 80 contract**

The [Multnomah original CSV](https://multco.us/file/sovc2_-_election20241105general.csv/download) gives 107 precinct vectors; its [presidential PDF](https://multco.us/file/2024-11_pres_vp.pdf/download) independently matches all 107 and supplies separate ballot/registration/nonvote controls. The [Clackamas complete canvass](https://dochub.clackamas.us/documents/drupal/3a834f56-37f7-4942-84da-8b0c38e90021) gives 118 literal rows although the header prints 119 precincts:115/116 is one combined row, with no split allocation. [Marion's complete canvass](https://www.co.marion.or.us/CO/elections/Results/Documents/20241105/Canvass%20Results-12-2-2024%2007-24-08%20PM.pdf) gives 118 rows. [Washington's scanned original](https://www.washingtoncountyor.gov/elections/documents/november-5-2024-ballots-cast-contest-precincts/download?inline) gives 155, with explicit raster readings retained. [Wasco's full 46-page original](https://records.sos.state.or.us/ORSOSWebDrawer/Record/10575034/File/document) gives 12. All 510 rows close all eight county columns, and [all ballot/over/under identities](data/baselines/known-native-controls.csv) balance. Their reporting keys are historical source-local identities, not geometry.

Washington's table ballots 301,104 equals 297,949 choices+170 overvotes+2,985 undervotes; its overall header prints 301,105. No one-ballot residual is allocated. Wasco Precinct 01 president has 1,831 ballots, whereas some other offices print 1,830. Clackamas Cast Votes excludes its separate Miscellaneous Write-In lane; Marion Cast Votes includes its generic write-in. Multnomah CSV overvote fields are candidate-specific; they do not become contest overvote-ballot totals. AB/ED/EV, Absentee Voting, Vote by Mail, central/reporting-group and Total presentations remain source-specific and nonadditive. The [raw method evidence](data/baselines/native-method-lanes.json), [nonadditive bindings](data/baselines/source/nonadditive-presentation-bindings.json), full original page index and source rows preserve all available lanes and unresolved identities.

The complete 2020/2022 ZIP publications contain 72 county-labeled original members:2020 has 33 PDFs and three CSVs; 2022 has 36 PDFs. Their full bytes/member hashes/CRCs are retained once, but county filename is not contest completeness. The original 2020 Benton 115-page ZIP member is a distinct state-office publication; its separately recovered [262-page federal county original](https://re.bentoncountyor.gov/wp-content/uploads/2023/12/2020Nov03_Precinct-Results.pdf) is retained independently, as is the [189-page 2022 original](https://re.bentoncountyor.gov/wp-content/uploads/2023/12/2022Nov08-Precinct-Results.pdf). [Every county/source/contest reconciliation](data/baselines/native-reconciliation.json) states missing columns, vectors and exact differences; [every original PDF page](data/baselines/source/whole-original-page-index.jsonl.gz) and required raw candidate/admin evidence remain available. Normalized historical closure is 16 parents for 2020 Senate,13 for 2022 Senate,13 for 2022 governor. Unclosed/OCR/identity/method cells are unknown, not zeros; raw text search absence is not proof of source absence.

The current [SOS historical-data page](https://sos.oregon.gov/elections/pages/historical-data.aspx) was refreshed and its literal 2024 precinct search again returned no records for that particular query. Earlier observed public form responses returned older ZIPs and did not preserve requested filters; no guessed record enumeration or exhaustive absence claim follows. [Lane's official archive](https://www.lanecounty.org/government/county_departments/county_administration/general_county_administration/operations/county_clerk/elections/historical_election_details) says precinct results beginning 2023 require request/redaction and may incur a fee. Its earlier complete 200 body is retained; this worker's fresh request returned 403. No outreach is authorized/performed. Bounded public recovery ends with these precise gaps.

The five-parent known-source universe has 1,128,521 reported presidential choices; the other 31 parents retain 1,115,972 in complete county/state arithmetic, with unknown native membership. In the known-only [full descending order](data/baselines/known-native-order.csv), top 15=112,024/1,128,521=9.926621%; first 213 rows reach 904,600, with predecessor 902,447 below the exact integer threshold 902,817. This is not statewide 80%. Separately, [all 36 county sensitivities](data/baselines/county-priority-order.csv) have top 15=1,983,101/2,244,493=88.354074%; first 11 reach 1,814,630, while the preceding 10 total 1,764,398 below threshold 1,795,595. Neither county order nor provisional known-only order is an approved native dispatch. [Contract and 31 explicit unavailable parents](data/baselines/priority-contract.json) retain null canonical order/top 15/minimum 80.

**Turnout, registration and source disagreements**

| Election-specific statistical publication | Number Eligible/registration | Ballots Returned | Separate contest totals |
| --- | ---: | ---: | --- |
|2020|2,944,588|2,413,890|Senate 2,321,249 reported choices|
|2022|2,985,820|1,997,689|Senate 1,927,949; governor 1,952,883|
|2024|3,060,374|2,308,256|President 2,244,493|

All 36 county participation columns close independently to their source footers. The complete archived primary statistical publications are [2020](https://web.archive.org/web/20210101093606id_/https://sos.oregon.gov/elections/Documents/statistics/november-2020-statistical-summary-participation.pdf), [2022](https://web.archive.org/web/20221221182416id_/https://sos.oregon.gov/elections/Documents/statistics/november-2022-statistical-summary-participation.pdf) and [2024](https://web.archive.org/web/20241227170225id_/https://sos.oregon.gov/elections/Documents/statistics/November-general-2024-statistical-summary-participation.pdf). [Party/county participation rows](data/baselines/participation-controls.csv) retain printed labels, zeros and anomalies. 2024's General Election statistical heading coexists with repeated Primary Election wording on page 1; Jefferson's We The People row prints 0 Number Eligible and 1 returned ballot. Those source values remain unchanged.

The separate [current general-turnout-history PDF](https://sos.oregon.gov/elections/Documents/History/Voter_Turnout_History_General_Election.pdf), generated 09/12/2025, prints 2020 Total Votes Cast 2,317,965 and registration 2,951,428, below the Senate contest's 2,321,249 choices and different from the election-specific participation stock. The [November monthly registration publications](data/baselines/monthly-registration.csv) are yet another dated stock. Returned ballots, accepted/cast ballots, contest votes, blank/under/over counts and registration definitions cannot be forced equal. All statewide canvass ballot/blank/nonvote native controls remain unavailable outside verified source scopes; no county/native allocation is invented. Historical totals do not project 2026 turnout or remaining votes.

**Offline conditional live remainder calculator**

Run `python3 -B senate/2026/oregon/data/baselines/scripts/calculator.py INPUT.json` from the repository root. [Schema and reproduction contract](data/baselines/source/SCHEMA.md) describes county/native/uniform/selected/live modes, actual source-key checks, finite scalar validation, supported denominators and unknown inputs. For a historical run use [a saved county fixture](data/baselines/fixtures/county-positive-historical-mix.input.json); for a live run use [the final-all-choice fixture](data/baselines/fixtures/live-final-all-choice.input.json). No network connection is needed.

Counted A/B/each other candidate remain fixed. Only a stated remaining pool, its pair participation, pair preference and nonpair allocation are forecast. Final pair denominator=countedA+countedB+remaining pair; final all-choice adds counted and remaining other votes. For target margin m, final denominator F, counted lead L and remaining pair U, required A share=(mF−L+U)/(2 U). Selected-only adds every other remaining unit at its explicit fixed preference. Unknown, no-pool, negative-invalid, already-secured, impossible and clipped cases are saved as meaningful [executed CLI fixtures](data/baselines/fixtures/results.json), with separate full-field arithmetic plurality. They are not calibrated probabilities or inferred source preferences.

The synthetic live example fixes counted A 40/B 60/Named C 10 and supplies 100 remaining all-choice votes,80% pair participation,60% remaining A pair share and all nonpair votes to Named C. Final arithmetic is A 88/B 92/C 30. Final pair denominator 180 gives a+1 pair-margin threshold 63.625% A among remaining pair votes; final all-choice denominator 210 gives 63.8125%. A different saved case lets Named C win despite an A/B pair threshold. Bool/null/text/nonfinite/malformed numeric targets, invalid mix/key/denominator surfaces and negative counted/remaining inputs return structured strictJSON errors; unknown source inputs remain explicitly unknown.

**Independent reconciliation and checks**

The immutable [pre-peer witness](data/baselines/source/pre-peer-witness.json), SHA256`208a3ad98dfb055eea0f895c0c0faf9881f684214e7d5a34c41e01f4df123b7f`, and [frozen independent bodies](data/baselines/source/pre-peer-body-map.json) precede opening turnout parsed counts/order/transcriptions. Actual turnout worker bd 151 c 4 c-70 ea-4 b 72-9063-2012086 b 07 e 6 was already finished and was not contacted/restarted. [Read-only captured peer comparison](data/baselines/peer-reconciliation.json) matches all 864 county source cells/parties/raw positions,144 county totals, participation/monthly stocks, all 4,080 known native presidential cells and the complete 510-row order using the peer's versioned FIPS/native-key tie rule. The [peer-compatible re-expression](data/baselines/source/peer-contract-native-order.json) preserves our source-local keys alongside that contract; equal-volume tie ordering is declared, not a changed count.

The comparison also matches 1,827 full original CSV candidate/method-counter dictionaries. It preserves one shared candidate and 16 control disagreements in **unclosed Douglas 2022 normalization**, rather than importing peer values. 2020 closed-parent sets differ: our original-raster Coos closes while peer Harney closes; 2022 governor our independently read Wasco closes beyond the peer's set. Tillamook was independently reparsed from its original named-unit headings after the initial comparison exposed an extraction gap. Source repairs and earlier bodies are both retained. These are scope/normalization findings, not mutual or coordinator acceptance.

The package executes 63 real CLI fixtures and 120 independent analytic piecewise-linear bounded-root checks. [Validation](data/baselines/validation.json) audits identities, uniqueness, candidate controls, raw/source hashes, complete/partial coverage, volumes/weights/denominators, exact 80/predecessor/order, bounds, links and asset sizes. [Reproduction script](data/baselines/scripts/reproduce.py) rebuilds the source extraction, calculations, report and QA offline; acquisition is a separate bounded explicit action. The [asset manifest](data/baselines/asset-manifest.json) and [acyclic seal](data/baselines/seal.json) pin the finished owned package. No dependency/cache directory, Git mutation, delegated research, implemented live collector, approved current precinct map, measured live cadence or calibrated Needle is claimed. Future final-ballot/legal/feed/geometry/private-source exhaustion is a qualification, not an unfinished recovery loop.
