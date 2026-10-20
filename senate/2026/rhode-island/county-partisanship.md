# Rhode Island historical partisanship and conditional targets

Research observation: 2026-10-20. The **2024 Whitehouse–Morgan Senate election is the priority baseline for the other Class I seat**. The 2026 regular election is Class II; **2020 Reed–Waters is the same-seat comparison**, **2022 McKee–Kalus governor is the actual midterm**, and 2024 president remains a separate electorate. These historical anchors and arithmetic sensitivities are not 2026 turnout projections, candidate effects or probabilities. Original candidates, parties, method slots and reporting identities remain in the data. [Primary 2024 result page](https://www.ri.gov/election/results/2024/general_election/), [2020](https://www.ri.gov/election/results/2020/general_election/), [2022](https://www.ri.gov/election/results/2022/general_election/).

**No positive Democratic improvement is required in a repeat of these historical electorates.** Whitehouse's 2024 lead over Morgan is 98,626 votes. At the original 490,704 pair votes, the unbounded uniform A-share loss allowance is −10.049439 share points to tie; an illustrative A+1 pair margin uses −9.549439 share points. Explicit clipping produces −10.049521 and −9.549517 points, respectively. A+1 means a 1-point pair margin, not one vote or one share point. It is 4,907.04 net pair votes, equal to 0.997471 points on the 491,948 candidate+generic denominator. All units, including the nonpriority remainder and four federal administrative contexts, remain in the calculation. [Board official summary, page 2](https://elections.ri.gov/sites/g/files/xkgbur756/files/2024-12/Gen24SummaryReport.pdf); [calculated state scenarios](data/baselines/state-scenarios.csv).

## Authority, original evidence and complete geography

The [actual technical data index](https://www.ri.gov/election/results/2024/general_election/data/) calls the raw computer downloads courtesy data and directs reliance to the Board website. Independently, the [Board historical-results publication page](https://elections.ri.gov/elections/previous-election-results), successfully acquired for this worker, links the authoritative summary and workbook publications used as controls. Earlier challenge/error responses remain preserved. The 2022/2024 summaries print OFFICIAL RESULTS; a separate signed certification document was not acquired, so this package does not assert a signed certification date. Requested/final URLs, available redirects, UTC retrievals, HTTP status/headers, publication clocks, raw/stored SHA-256 and bytes are in the [fixed original receipts](data/baselines/source/inputs.json), [new observations](data/baselines/source/current-inputs.json), and [literal source chains](data/baselines/source/chains.json).

Rhode Island's actual reporting parents are **39 municipalities**, with four separate state-admin federal contexts `9001`, `9002`, `9011`, `9012` retained unallocated. Five counties are not reporting substitutes. The canonical finer priority is **all 458 original 2024 Senate source codes**, tied to exact original archive/member/first Senate byte. The full 497 presidential contexts remain available; 39 president-only contexts have **unavailable Senate**, not invented zero. Fifteen other Senate contexts are explicitly observed zero. The 39 literal municipal child pages enumerate 493 presidential contexts; the root/Board workbook add the four federal contexts. [Municipal navigation and child pages](https://www.ri.gov/election/results/2024/general_election/), [Board workbook](https://elections.ri.gov/sites/g/files/xkgbur756/files/2025-01/Gen24EX%20%281%29.xlsx), [complete native inventory](data/baselines/extracts/native-inventory.json).

The compatibility file [county-baselines.csv](data/county-baselines.csv) contains **2,460 year/contest/native rows**, with every original candidate, party and all 14 method slots. It does not create counties or join native codes across years. Inventories contain 504 source contexts in 2020, 458 in 2022 and 497 in 2024; selected contests observe respectively 465/504 Senate/president, 454 governor, and 458/497 Senate/president. The four 2022 Board statistic-only federal contexts have unavailable governor results. Polling sites, limited and presidential contexts, central labels, and federal administration remain distinct; names/counts/codes prove no current geometry. Full [schema](data/baselines/source/SCHEMA.md) and [source raw witnesses](data/baselines/witness/root-selected.jsonl.gz) preserve padded fields, source positions and nulls.

The original [short](https://www.ri.gov/election/results/2024/general_election/data/rigen2024.zip) and [long](https://www.ri.gov/election/results/2024/general_election/data/rigen2024l.zip) roots agree on all 20,921 numeric prefixes. The corresponding actual linked 2020 and 2022 archives agree on 16,573 and 24,973 prefixes. Root/nested/setup members are never added together. Nested selected rows differ from roots at 57 positions in 2024, 4,829 in 2020 and 2,712 in 2022; setup views are separate zeros. No correction cause or chronology is inferred from filenames/ZIP clocks. Every original member, including Mac metadata, remains reconstructable from complete ZIP bytes; [member hashes/CRCs](data/baselines/source/zip-members.json), [view discrepancies](data/baselines/witness/view-comparison.json), [view controls](data/baselines/witness/zip-view-controls.json).

The [format linked for 2020](https://www.ri.gov/election/results/20160902_data_description.pdf) leaves method slot 3 unlabeled, while actual 2020 HTML calls it Emergency ballots. The [2022/2024 linked format](https://www.ri.gov/election/results/20220819_data_description.pdf) and HTML call the matching slot Early Voting. All fourteen ordered slots are retained; no current method alias is inferred. Board totals, parties and first-three method counts match all **12,997 selected candidate rows**; municipal HTML matches all **1,053 candidate/method comparisons**. These are source-field reconciliations, not completion or collector tests. [Publication reconciliation](data/baselines/extracts/publication-controls.json).

## Complete statewide candidates and denominators

The following are reported printed-candidate plus **generic** write-in controls. Generic write-ins are not a single named eligible candidate. Preserve each Independent and Libertarian identity; no non-Republican coalition is labeled Democratic. All selected fields contain an actual Democrat. Primary controls: [2024 Board summary, page 2](https://elections.ri.gov/sites/g/files/xkgbur756/files/2024-12/Gen24SummaryReport.pdf), [2020 Board summary, page 1](https://elections.ri.gov/sites/g/files/xkgbur756/files/2022-02/statewidesummary2020gen.pdf), [2022 Board summary, page 2](https://elections.ri.gov/sites/g/files/xkgbur756/files/2023-06/STATEWIDE%20SUMMARY.pdf).

| Election | Full literal source candidate | Party | Votes | Candidate+generic denominator | Share of that denominator |
| --- | --- | --- | ---: | ---: | ---: |
| 2024-senate | DEM Sheldon Whitehouse | DEM | 294,665 | 491,948 | 59.8976% |
| 2024-senate | REP Patricia Morgan | REP | 196,039 | 491,948 | 39.8495% |
| 2024-senate | Write-in | NON | 1,244 | 491,948 | 0.2529% |
| 2024-president | Kamala D. Harris | DEM | 285,156 | 513,386 | 55.5442% |
| 2024-president | Donald J. Trump | REP | 214,406 | 513,386 | 41.7631% |
| 2024-president | Robert F. Kennedy, Jr. | Ken | 5,045 | 513,386 | 0.9827% |
| 2024-president | Robert "Robby" Wells | Par | 359 | 513,386 | 0.0699% |
| 2024-president | Chase Oliver | Lib | 1,617 | 513,386 | 0.3150% |
| 2024-president | Jill Stein | Grn | 2,900 | 513,386 | 0.5649% |
| 2024-president | Claudia De la Cruz | S&L | 1,176 | 513,386 | 0.2291% |
| 2024-president | Write-in | NON | 2,727 | 513,386 | 0.5312% |
| 2020-senate | Allen R. Waters | REP | 164,855 | 494,262 | 33.3538% |
| 2020-senate | John F. Reed | DEM | 328,574 | 494,262 | 66.4777% |
| 2020-senate | WRITE-IN | NON | 833 | 494,262 | 0.1685% |
| 2020-president | Donald J. Trump | REP | 199,922 | 517,757 | 38.6131% |
| 2020-president | Joseph R. Biden | DEM | 307,486 | 517,757 | 59.3881% |
| 2020-president | Roque "Rocky" De La Fuente | All | 923 | 517,757 | 0.1783% |
| 2020-president | Brian Carroll | AS | 767 | 517,757 | 0.1481% |
| 2020-president | Gloria La Riva | S&L | 847 | 517,757 | 0.1636% |
| 2020-president | Jo Jorgensen | Lib | 5,053 | 517,757 | 0.9759% |
| 2020-president | WRITE-IN | NON | 2,759 | 517,757 | 0.5329% |
| 2022-governor | REP Ashley Marie Kalus | REP | 139,001 | 357,670 | 38.8629% |
| 2022-governor | DEM Daniel J. McKee | DEM | 207,166 | 357,670 | 57.9210% |
| 2022-governor | Ind Zachary Baker Hurwitz | Ind | 4,512 | 357,670 | 1.2615% |
| 2022-governor | Ind Paul A. Rianna, Jr. | Ind | 3,123 | 357,670 | 0.8732% |
| 2022-governor | Lib Elijah J. Gizzarelli | Lib | 2,811 | 357,670 | 0.7859% |
| 2022-governor | Write-in | NON | 1,057 | 357,670 | 0.2955% |

| Election | A+B pair | All candidate+generic | Overvotes | Undervotes | Contest ballots | All election ballots |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2024-senate | 490,704 | 491,948 | 143 | 15,770 | 507,861 | 517,231 |
| 2024-president | 499,562 | 513,386 | 1,021 | 2,824 | 517,231 | 517,231 |
| 2020-senate | 493,429 | 494,262 | 162 | 20,539 | 514,963 | 521,185 |
| 2020-president | 507,408 | 517,757 | 1,211 | 2,217 | 521,185 | 521,185 |
| 2022-governor | 346,167 | 357,670 | 119 | 3,485 | 361,274 | 361,449 |

The 2024 Senate contest-ballot denominator is 507,861 versus 517,231 for president; the exact 9,370-ballot scope difference is in presidential contexts absent from Senate. The analogous 2020 difference is 6,222; the 2022 governor scope excludes 175 ballots in the four federal statistic-only contexts. These differences close against actual Board native election-ballot rows, without residual allocation. Native contest under/over/contest-ballot fields remain unavailable where not published; election ballots are not silently substituted. The 2024 PDF percentages (e.g. Whitehouse 58.02%) use contest ballots, while technical HTML Whitehouse 59.9% uses candidate+generic votes. [Board PDF](https://elections.ri.gov/sites/g/files/xkgbur756/files/2024-12/Gen24SummaryReport.pdf), [electorate reconciliation](data/baselines/extracts/electorate-ballot-reconciliation.json).

Historical election registration is 808,953 in 2020, 815,417 in 2022, and 787,559 in 2024. The native observed rows sum exactly to these Board controls; 2022 has 442 registration rows and 16 unavailable native entries, while 2024 has 483 rows and 14 unavailable entries. 2020 has all 504. Blank-ballot statistics are 3,342 in 2020 and 6,171 in 2024; the 2022 workbook does not publish that statistic. Active/inactive status and a separate registration snapshot date are unresolved. These are historical election registration and ballot definitions, not eligible-population turnout or a 2026 registration forecast. [2020 summary](https://elections.ri.gov/sites/g/files/xkgbur756/files/2022-02/statewidesummary2020gen.pdf), [2022 summary](https://elections.ri.gov/sites/g/files/xkgbur756/files/2023-06/STATEWIDE%20SUMMARY.pdf), [2024 summary](https://elections.ri.gov/sites/g/files/xkgbur756/files/2024-12/Gen24SummaryReport.pdf), [all missing native codes](data/baselines/extracts/statistic-coverage.json).

The Board's separately linked [2024 write-in publication](https://elections.ri.gov/sites/g/files/xkgbur756/files/2025-04/Write%20In%20Report%20City%20Totals%20RQ.xlsx) has municipal Senate header totals summing to 1,239, matching municipal generic 1,239. Its complete literal detail sums to **1,227**, with eight municipal discrepancies. The captured turnout peer’s row-6-onward detail scope sums to 1,226/nine discrepancies because it omits actual Cranston row 5 (`D5 Mario Frioli ` / `E5 1`). Both scopes remain separate; no actual row was dropped to force agreement. [Original cell XML/byte-position proof](data/baselines/extracts/writein-row5-source-proof.json), [full-versus-bounded scope comparison](data/baselines/extracts/writein-detail-scope-comparison.json). State generic 1,244 additionally includes federal administrative scope. Every literal Senate detail/footer/header/blank cell and source sheet/row is retained; names are not deduplicated, deemed eligible, assigned to native precincts or added to generic counts. The Board's [write-in guidance, revised June 2020](https://elections.ri.gov/sites/g/files/xkgbur756/files/2023-11/Guide%20to%20Write-Ins.pdf) explicitly distinguishes blank-name audit records from valid write-in votes. No eligible named universe is inferred from the generic number. [Independent discrepancy table](data/baselines/extracts/2024-senate-writein-reconciliation.json), [literal cells](data/baselines/extracts/2024-senate-writein-literal-cells.json). Historical 2020/2022 named write-in publications remain in complete original bytes/text with their own scopes; no native allocation is inferred.

## Every municipal and administrative parent

This table is a parent-level historical comparison only; the dispatch order remains the finer 458 native contexts. A/B are the named DEM/REP candidates in each separate contest. Pair margins below are A−B percentage points on A+B. Full candidate identities/other votes remain in the parent data. Each municipal label links its literal 2024 official page; [2020 municipal pages](https://www.ri.gov/election/results/2020/general_election/) and [2022 municipal pages](https://www.ri.gov/election/results/2022/general_election/) independently establish those years' child maps. [Complete parent candidates/children](data/baselines/extracts/parent-baselines.json).

| Parent | 2024 Senate A / B / other | 2024 Senate pair margin | 2024 president pair margin | 2020 Senate pair margin | 2022 governor pair margin |
| --- | ---: | ---: | ---: | ---: | ---: |
| [Barrington](https://www.ri.gov/election/results/2024/general_election/barrington/) | 7,282 / 3,105 / 22 | +40.214 | +44.119 | +47.997 | +40.133 |
| [Bristol](https://www.ri.gov/election/results/2024/general_election/bristol/) | 6,680 / 4,484 / 14 | +19.670 | +16.524 | +34.563 | +19.471 |
| [Burrillville](https://www.ri.gov/election/results/2024/general_election/burrillville/) | 3,480 / 4,934 / 13 | -17.281 | -26.007 | -5.174 | -19.206 |
| [Central Falls](https://www.ri.gov/election/results/2024/general_election/central_falls/) | 2,297 / 843 / 6 | +46.306 | +29.722 | +64.044 | +49.937 |
| [Charlestown](https://www.ri.gov/election/results/2024/general_election/charlestown/) | 2,901 / 2,290 / 6 | +11.770 | +9.910 | +22.151 | +14.236 |
| [Coventry](https://www.ri.gov/election/results/2024/general_election/coventry/) | 9,293 / 10,359 / 33 | -5.424 | -13.091 | +8.592 | -4.014 |
| [Cranston](https://www.ri.gov/election/results/2024/general_election/cranston/) | 22,671 / 16,452 / 111 | +15.896 | +6.356 | +29.581 | +13.195 |
| [Cumberland](https://www.ri.gov/election/results/2024/general_election/cumberland/) | 10,577 / 8,098 / 38 | +13.274 | +7.047 | +24.299 | +16.840 |
| [East Greenwich](https://www.ri.gov/election/results/2024/general_election/east_greenwich/) | 5,115 / 3,276 / 21 | +21.916 | +22.745 | +29.109 | +21.677 |
| [East Providence](https://www.ri.gov/election/results/2024/general_election/east_providence/) | 14,213 / 7,742 / 64 | +29.474 | +22.697 | +42.223 | +29.560 |
| [Exeter](https://www.ri.gov/election/results/2024/general_election/exeter/) | 1,885 / 2,085 / 5 | -5.038 | -5.196 | +9.620 | -1.741 |
| [Foster](https://www.ri.gov/election/results/2024/general_election/foster/) | 1,198 / 1,676 / 4 | -16.632 | -22.520 | -2.813 | -14.460 |
| [Glocester](https://www.ri.gov/election/results/2024/general_election/glocester/) | 2,615 / 3,558 / 11 | -15.276 | -20.973 | -1.037 | -16.811 |
| [Hopkinton](https://www.ri.gov/election/results/2024/general_election/hopkinton/) | 2,337 / 2,502 / 7 | -3.410 | -7.143 | +8.918 | -4.149 |
| [Jamestown](https://www.ri.gov/election/results/2024/general_election/jamestown/) | 2,659 / 1,221 / 6 | +37.062 | +38.819 | +48.342 | +36.739 |
| [Johnston](https://www.ri.gov/election/results/2024/general_election/johnston/) | 7,356 / 7,702 / 34 | -2.298 | -19.504 | +13.953 | -5.922 |
| [Lincoln](https://www.ri.gov/election/results/2024/general_election/lincoln/) | 6,705 / 5,519 / 39 | +9.702 | +2.176 | +22.828 | +12.228 |
| [Little Compton](https://www.ri.gov/election/results/2024/general_election/little_compton/) | 1,517 / 1,005 / 5 | +20.301 | +21.830 | +30.016 | +18.935 |
| [Middletown](https://www.ri.gov/election/results/2024/general_election/middletown/) | 4,965 / 2,759 / 9 | +28.560 | +27.385 | +41.035 | +28.922 |
| [Narragansett](https://www.ri.gov/election/results/2024/general_election/narragansett/) | 5,054 / 3,725 / 18 | +15.138 | +13.838 | +31.984 | +21.416 |
| [New Shoreham](https://www.ri.gov/election/results/2024/general_election/new_shoreham/) | 685 / 167 / 4 | +60.798 | +57.757 | +60.352 | +57.654 |
| [Newport](https://www.ri.gov/election/results/2024/general_election/newport/) | 6,985 / 2,734 / 22 | +43.739 | +43.678 | +55.342 | +46.391 |
| [North Kingstown](https://www.ri.gov/election/results/2024/general_election/north_kingstown/) | 10,156 / 6,757 / 32 | +20.097 | +20.645 | +30.534 | +23.239 |
| [North Providence](https://www.ri.gov/election/results/2024/general_election/north_providence/) | 9,325 / 6,281 / 43 | +19.505 | +6.802 | +33.195 | +11.898 |
| [North Smithfield](https://www.ri.gov/election/results/2024/general_election/north_smithfield/) | 3,521 / 3,455 / 7 | +0.946 | -4.961 | +12.816 | -4.110 |
| [Pawtucket](https://www.ri.gov/election/results/2024/general_election/pawtucket/) | 16,054 / 6,635 / 82 | +41.514 | +33.133 | +54.335 | +39.081 |
| [Portsmouth](https://www.ri.gov/election/results/2024/general_election/portsmouth/) | 6,265 / 4,141 / 12 | +20.411 | +22.340 | +32.430 | +21.307 |
| [Providence](https://www.ri.gov/election/results/2024/general_election/providence/) | 41,185 / 10,189 / 289 | +60.334 | +52.358 | +71.323 | +66.674 |
| [Richmond](https://www.ri.gov/election/results/2024/general_election/richmond/) | 2,428 / 2,422 / 6 | +0.124 | -3.358 | +10.026 | -0.198 |
| [Scituate](https://www.ri.gov/election/results/2024/general_election/scituate/) | 2,710 / 3,798 / 5 | -16.718 | -22.159 | +0.682 | -14.517 |
| [Smithfield](https://www.ri.gov/election/results/2024/general_election/smithfield/) | 5,623 / 5,725 / 17 | -0.899 | -8.371 | +15.884 | -0.266 |
| [South Kingstown](https://www.ri.gov/election/results/2024/general_election/south_kingstown/) | 10,628 / 5,514 / 36 | +31.681 | +33.271 | +43.884 | +35.665 |
| [Tiverton](https://www.ri.gov/election/results/2024/general_election/tiverton/) | 4,898 / 3,970 / 10 | +10.465 | +5.603 | +22.607 | +8.955 |
| [Warren](https://www.ri.gov/election/results/2024/general_election/warren/) | 3,590 / 2,299 / 13 | +21.922 | +17.118 | +35.247 | +22.317 |
| [Warwick](https://www.ri.gov/election/results/2024/general_election/warwick/) | 25,798 / 18,950 / 112 | +15.303 | +8.002 | +27.608 | +14.961 |
| [West Greenwich](https://www.ri.gov/election/results/2024/general_election/west_greenwich/) | 1,640 / 2,327 / 11 | -17.318 | -21.074 | -1.346 | -16.820 |
| [West Warwick](https://www.ri.gov/election/results/2024/general_election/west_warwick/) | 7,173 / 6,491 / 30 | +4.991 | -2.082 | +22.484 | +6.523 |
| [Westerly](https://www.ri.gov/election/results/2024/general_election/westerly/) | 6,918 / 5,199 / 12 | +14.187 | +8.030 | +24.334 | +16.313 |
| [Woonsocket](https://www.ri.gov/election/results/2024/general_election/woonsocket/) | 6,927 / 5,538 / 30 | +11.143 | -1.651 | +25.368 | +4.295 |
| state-admin-9001 | 440 / 45 / 2 | +81.443 | +81.854 | +85.513 | undefined / unavailable |
| state-admin-9002 | 478 / 46 / 2 | +82.443 | +83.240 | +86.928 | undefined / unavailable |
| state-admin-9011 | 363 / 14 / 1 | +92.573 | +90.816 | +89.286 | undefined / unavailable |
| state-admin-9012 | 75 / 7 / 0 | +82.927 | +85.882 | +87.500 | undefined / unavailable |

For every individual native context, the long-form [baseline CSV](data/county-baselines.csv) supplies named A/B/other counts, all-candidate and pair denominators, shares/margins, methods, parent and raw source anchor. Thus historical Republican-leading, Democratic-leading, tied and zero/undefined contexts can be inspected without assigning a permanent partisan identity to a municipality or a current precinct.

## Exact native priority and reciprocal scope

The independently ranked top 15 native contexts supply **34,697 / 491,948 = 7.052981%**. The minimum 80% crossing is **242 contexts / 394,072 votes = 80.104401%**; after 241 it is 393,066. Rank 242 is `0804 Cumberland`, root long line 4061, byte 1,075,900, adding 1,006 votes. The 216-context remainder contributes 97,876 votes and stays in every 2024 Senate scenario. [Full descending native order](data/baselines/witness/independent-native-priority.json), [complete 39+4 child contract](data/baselines/native-priority-contract.json), [primary long ZIP](https://www.ri.gov/election/results/2024/general_election/data/rigen2024l.zip).

| Rank | Native code and source name | Candidate+generic votes | State weight |
| ---: | --- | ---: | ---: |
| 1 | `0707` Cranston 0707 | 2,585 | 0.52546% |
| 2 | `1801` Little Compton 1801 | 2,527 | 0.51367% |
| 3 | `0725` Cranston 0725 | 2,357 | 0.47912% |
| 4 | `0705` Cranston 0705 | 2,323 | 0.47220% |
| 5 | `2002` Narragansett 2002 | 2,299 | 0.46733% |
| 6 | `3522` Warwick 3522 | 2,296 | 0.46672% |
| 7 | `3002` Scituate 3002 | 2,292 | 0.46590% |
| 8 | `3521` Warwick 3521 | 2,284 | 0.46428% |
| 9 | `0711` Cranston 0711 | 2,279 | 0.46326% |
| 10 | `0718` Cranston 0718 | 2,270 | 0.46143% |
| 11 | `3804` West Warwick 3804 | 2,266 | 0.46062% |
| 12 | `3101` Smithfield 3101 | 2,238 | 0.45493% |
| 13 | `2309` North Kingstown 2309 | 2,231 | 0.45350% |
| 14 | `2501` North Smithfield 2501 | 2,228 | 0.45289% |
| 15 | `0610` Coventry 0610 | 2,222 | 0.45167% |

The coarser 43-parent sensitivity reaches 80% at 21 parents/395,379 votes, after 20/386,501; it is never a substitute dispatch. Municipal votes total 490,475 and the four federal administrative contexts 1,473. [Separate parent sensitivity](data/baselines/parent-rank-sensitivity.csv).

After freezing complete own original-first evidence, this worker captured the actual completed turnout peer's stable final bodies read-only. **24,249 scoped reciprocal checks pass**, including complete raw selected root/nested/setup rows, all 14 methods and padded candidate/party fields, source anchors/positions, all-year native/statistic/null controls, 39+4 maps, full 458 descending order and the exact minimum-80 contract. Key delimiter # versus colon is a representation difference, compared by exact archive SHA/member/byte tuple. Eleven child labels collapse repeated whitespace in peer displayed text; literal own source strings/byte positions and the differences remain preserved. No peer votes feed the builder, no peer output was changed, and no future byte equality or coordinator acceptance is claimed. [Frozen capture](data/baselines/reciprocal/capture-additional.json), [comparison and representation differences](data/baselines/reciprocal/reconciliation.json), [own pre-peer proof](data/baselines/witness/pre-peer-body-witness.json).

## Tie, cushion and historical volume/mix sensitivities

At fixed two-candidate weights, tie shift is `(B−A)/(2*(A+B))` in fractional A share. One A-share point adds two pair-margin points and 0.02 times the pair pool in net votes. A+1 pair margin adds 0.5 A-share points to the **unbounded** tie shift. The implementation clips each share to [0,1], solves a feasible bounded common shift, retains raw/already-winning/unbounded cases, and never assigns neutral preference to a zero-pair unit. Tiny differences from the unbounded result arise when sparse one-sided contexts clip. [Implemented offline calculator](data/baselines/scripts/calculate.py), [independent Decimal piecewise roots](data/baselines/qa/independent-bounded-roots.json).

The five own-electorate runs use each historical contest's complete native volumes, pair participation and named A-share preference. The additional low/base/high settings keep **2024 Senate native preferences and pair participation**, with 2024 within-municipality all-vote weights. Municipal volume anchors are 2022 governor / 2024 Senate / 2020 president; all four federal contexts keep their actual 2024 Senate volumes. Thus low/base/high full volume is **359,143 / 491,948 / 517,856**, not the three entire historical statewide electorates. This explicit within-parent scaling is a conditional assumption; it neither reconstructs missing historical native counts nor joins old precincts to new ones. [Exact settings](data/baselines/scenario-settings.json), [all scenario input/result JSON](data/baselines/scenarios/2024-senate-low-historical-mix-tie.input.json).

| Scenario | Full volume | Pair volume | Tie shift, A-share pp (bounded) | A+1 shift, A-share pp (bounded) | A+1 net votes |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2024-senate-historical | 491,948.00 | 490,704.00 | -10.049521 | -9.549517 | 4,907.04 |
| 2024-president-historical | 513,386.00 | 499,562.00 | -7.081285 | -6.581251 | 4,995.62 |
| 2020-senate-historical | 494,262.00 | 493,429.00 | -16.590160 | -16.090153 | 4,934.29 |
| 2020-president-historical | 517,757.00 | 507,408.00 | -10.599631 | -10.099619 | 5,074.08 |
| 2022-governor-historical | 357,670.00 | 346,167.00 | -9.845824 | -9.345816 | 3,461.67 |
| 2024-senate-low-historical-mix | 359,143.00 | 358,256.28 | -9.712876 | -9.212872 | 3,582.56 |
| 2024-senate-base-historical-mix | 491,948.00 | 490,704.00 | -10.049521 | -9.549517 | 4,907.04 |
| 2024-senate-high-historical-mix | 517,856.00 | 516,532.95 | -10.334685 | -9.834680 | 5,165.33 |

All 16 runs retain their complete electorate; zero/low-volume, administrative and nonpriority units are not dropped. [Native target rows](data/baselines/native-targets.csv) include every contribution/weight/participation/gain, tie/A+1 share and clipping status, plus each selected-unit-only break-even with every other unit fixed at that scenario's baseline. [Parent contributions](data/baselines/parent-contributions.csv) preserve aggregated net effects and nominal/bounded +1-share-point gains; [selected-parent thresholds](data/baselines/parent-selected-targets.csv) retain impossible, secured and no-positive-pool cases without forcing raw shares into [0,1].

For example, at actual 2024 Senate volume and all other native units fixed at their observed preferences, Providence has 51,374 pair votes/10.469448% pair weight and contributes +30,996 net votes. All other units contribute +67,630. Its selected-only raw tie requirement is −15.821233% A share and its A+1 requirement is −11.045432%; these are **already secured under those fixed-rest assumptions**, not feasible negative vote shares. A nominal +1 A-share point in Providence is 1,027.48 net votes at fixed pair volume. Native rows solve the same conditional question at finer scope. None is a universal necessary target for winning Rhode Island. [Official Providence counts](https://www.ri.gov/election/results/2024/general_election/providence/), [selected-parent calculation](data/baselines/parent-selected-targets.csv).

## Offline counted-plus-remainder arithmetic and legal scope

`calculate.py` preserves counted A, B and every other candidate count. It forecasts only the explicitly supplied remaining all-candidate pool, partitions that pool using declared pair participation, and uses the correct **final** full and pair denominators. It returns unknown for positive-pool missing preference, preserves no-pool and raw secured/impossible thresholds, and validates finite numeric inputs/global unique string keys/allocations before those branches. No remaining pool is inferred from reporting percentages, source clocks, historical methods or turnout anchors. [Full input contract and CLI](data/baselines/source/SCHEMA.md), [known synthetic example](data/baselines/scenarios/fixtures/known-final-denominator.json), [its result](data/baselines/scenarios/fixtures/known-final-denominator.result.json).

The known example has counted A=100/B=130/other=15 and 150 remaining votes; final full denominator is 395 and final pair denominator 340. Its supplied remaining preferences yield A=168/B=172, while other votes remain separate. The saved 30 actual CLI fixtures include unknown, no-pool, negative/invalid volumes, secured/impossible, clipping, zero-pair undefined preference, duplicate/empty/nonstring keys, fractional/bool/null/text/nonfinite/out-of-range targets, unbalanced other allocation, and a pair leader losing to a supplied third candidate. Invalid numeric-token text is not emitted as JSON. These fixtures test arithmetic and input validation, not calibrated probabilities. [Fixture results](data/baselines/qa/cli-fixtures.json).

Rhode Island elects federal senators by **plurality of the full legal candidate field**, under [R.I. Gen. Laws §17-4-6](https://webserver.rilegislature.gov/Statutes/TITLE17/17-4/17-4-6.htm). The pair tie and illustrative A+1 cushion are deterministic benchmarks, not the legal victory rule or an RCV/runoff stage. The calculator separately reports plurality among supplied candidates and a full-field result only when the user declares a complete universe with no unallocated other votes. No legal declaration is made. Candidate effects, lower preferences and 2026 remaining-vote assumptions are not inferred from historical counts.

The [current official candidate lookup](https://vote.sos.ri.gov/Candidates/CandidateSearch) and general summary route returned retained HTTP403 bodies to this worker. The linked [declared-candidate workbook](https://vote.sos.ri.gov/Forms/elections/Reports/Candidates.xlsx) was downloaded, but it still includes primary records and cannot establish a final current ballot map. **Current final printed roster/ballot order/operational candidate IDs remain unresolved**; no primary winner, old historical ID or third-party roster is promoted into that map. [Exact observed scope](data/baselines/extracts/declared-candidate-scope.json), [access receipts](data/baselines/source/current-inputs.json). Current write-in eligibility, later amendments/signed certification and 2026 source/geometry approval remain qualified; those gaps do not change the preserved historical arithmetic.

## Reproduction and handoff

[Reproduction](data/baselines/REPRODUCTION.md) rebuilds from individual exact original bodies in an isolated temporary tree. The package includes acquisition/extraction/build/calculation scripts; [schema](data/baselines/source/SCHEMA.md); all-original/member hashes and raw source positions; complete native/candidate/method/ballot/registration controls; [validation](data/baselines/validation.json); [independent corruption/root evidence](data/baselines/qa/independent-bounded-roots.json); [reproduction comparison](data/baselines/qa/reproduction.json); a [final seal](data/baselines/final-seal.json); and [complete owned asset manifest](data/baselines/asset-manifest.json), excluding only itself. Every stored artifact is strictly below 40,000,000 bytes, with complete shared originals referenced by exact hash rather than duplicated. A final read-only body/hash/size/source/order/link audit follows sealing.

Acceptance of the canonical priority and current legal/geographic/feed use belongs to the coordinator. Historical reporting 414/458 Senate and 453/497 president in the official 2024 summary is **not a count of remaining votes**. No live collector, guaranteed cadence, exact outstanding pool, current boundary approval, calibrated Needle/probability or real 2026 turnout projection is claimed. [Primary official summary](https://elections.ri.gov/sites/g/files/xkgbur756/files/2024-12/Gen24SummaryReport.pdf).

