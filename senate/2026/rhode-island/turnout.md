# Rhode Island vote-volume ranking and turnout controls

Research: 2026-10-20 UTC. **Canonical priority ranks all 458 actual 2024 Senate source reporting codes**, using printed-candidate votes plus the source's generic Write-in. This is reported vote volume, not ballots cast, a turnout rate, a verified eligible-write-in universe or a 2026 forecast. The 43 municipality/state-administrative parent ranking is a separate sensitivity.

**Native top 15:** 0707 Cranston 0707, 1801 Little Compton 1801, 0725 Cranston 0725, 0705 Cranston 0705, 2002 Narragansett 2002, 3522 Warwick 3522, 3002 Scituate 3002, 3521 Warwick 3521, 0711 Cranston 0711, 0718 Cranston 0718, 3804 West Warwick 3804, 3101 Smithfield 3101, 2309 North Kingstown 2309, 2501 North Smithfield 2501, 0610 Coventry 0610. They supply **34,697 / 491,948 = 7.0529812094%**.

**Minimum descending set reaching 80%: 242 native contexts**, totaling **394,072 / 491,948 = 80.1044012782%**. The preceding **241 total 393,066 = 79.8999081204%**. **Cumberland 0804 (code 0804), 1,006 votes, crosses at rank 242**. Its anchor is root `rigen2024l.txt`, line 4061, zero-based byte 1,075,900, in archive SHA-256 `a2fd599d247e1e7b5d5e0d8de1dcf43491500532f47310284df548ac9848e444`. The **216-context remainder contributes 97,876 = 19.8955987218%**, including 15 explicitly published zero-total Senate contexts. Sorting largest first proves that no set of only 241 contexts reaches 80%. The integer test is `5*cumulative >= 4*491948`; the required integer total is 393,559. Ties use ascending first Senate record byte position within the root member. [Original long ZIP](https://www.ri.gov/election/results/2024/general_election/data/rigen2024l.zip), [Board official summary, pp. 1–2](https://elections.ri.gov/sites/g/files/xkgbur756/files/2024-12/Gen24SummaryReport.pdf).

The [dispatch contract](data/turnout/priority-set.json) contains all 458 ordered native source-position keys, the exact ordered priority keys, preceding/crossing/remainder arithmetic, all 497 available native inventory entries, complete candidate constituent positions and all 14 method slots. [The compatibility CSV](data/county-turnout.csv) has **458 native rows**; its filename does not authorize county or municipal substitution. The complete order below defines the exact set as ranks 1–242 and the remainder as ranks 243–458. **Bounded source-core agreement with the captured finished peer is verified after the original-first freeze; coordinator acceptance remains pending.** Peer calculators, scenarios, reports and outcomes are outside this agreement. This is research, not accepted current geographic dispatch or publication approval.

## Exact 242-code priority set

Order is significant; names, source positions, parents, candidate rows and counts are in the full table and contract.

`0707, 1801, 0725, 0705, 2002, 3522, 3002, 3521, 0711, 0718, 3804, 3101, 2309, 2501, 0610, 3807, 0901, 2004, 3209, 2003, 3001, 1401, 0905, 2001, 1011, 1001, 3507, 3605, 3518, 2301, 3604, 3504, 3526, 2707, 3104, 3105, 3003, 2706, 0812, 2308, 3505, 3401, 0704, 1502, 3208, 0723, 0104, 0202, 2703, 0102, 0807, 1103, 0722, 0604, 3603, 2702, 0106, 1402, 1704, 0103, 0617, 3516, 0803, 0805, 1501, 2819, 1705, 0902, 1706, 2310, 0611, 3509, 1302, 3602, 2502, 2601, 3525, 3204, 0810, 3502, 3301, 3524, 1609, 0609, 2303, 3606, 2901, 3102, 2102, 3808, 0724, 2401, 3404, 0708, 1201, 2503, 2411, 0207, 1905, 2813, 2619, 3302, 1017, 1904, 3531, 1014, 1301, 3203, 3701, 3103, 0802, 3910, 2108, 0714, 0306, 3911, 0101, 3528, 3514, 3305, 1007, 2830, 2412, 0709, 0206, 0303, 0616, 2109, 3106, 2902, 2402, 2818, 2307, 1605, 1008, 1902, 2305, 2820, 3207, 2903, 1016, 3211, 0801, 3809, 0208, 2605, 2302, 1608, 3607, 0713, 0904, 0301, 1002, 0602, 1607, 0205, 2403, 2817, 2611, 2106, 1903, 2407, 2814, 0706, 1610, 0701, 0503, 3205, 0712, 3907, 2804, 2620, 2862, 3206, 3523, 2613, 0502, 0302, 1901, 0721, 0808, 2861, 1708, 1604, 0806, 1602, 1012, 1303, 3515, 1603, 3513, 3801, 0305, 0501, 2413, 3909, 2705, 2606, 2304, 2101, 2627, 1009, 3503, 3810, 1612, 0716, 3912, 1702, 1004, 0702, 1005, 3210, 0717, 3530, 2602, 1102, 3307, 2806, 1202, 2406, 2857, 2856, 3527, 1013, 2622, 1703, 2822, 0504, 0606, 0304, 2306, 0603, 3403, 2863, 2625, 3908, 3402, 0105, 3904, 3802, 0201, 0804`

## Primary authority and original publication scope

The [current RI.gov technical index](https://www.ri.gov/election/results/2024/general_election/data/) calls the downloads courtesy technical data supplied by the Board, disclaims suitability, and directs users to the Board website for official results. RI.gov's technical surface is not an independent Secretary-certified canvass. The [current Board previous-results page](https://elections.ri.gov/elections/previous-election-results) independently links the RI.gov historical pages, original summary PDFs and XLSX publications. The complete original response graph, requested/final URLs, UTC retrieval, headers, statuses, raw/stored hashes and literal anchors are retained in [source graph](data/turnout/source/source-graph.json) and [frozen original receipts](data/turnout/source/inputs/original-receipts.json). Earlier 403 responses and sandbox DNS failures survive alongside successful later requests; a failure is not a declaration that the public source does not exist.

The 2024 technical HTML/index prints **November 22, 2024 05:31 PM**. The Board summary prints **OFFICIAL RESULTS**, election November 5, 2024, and **12/03/2024 11:19AM**. The 2022 Board summary prints **OFFICIAL RESULTS**, November 8 election and **11/22/2022 12:14PM**; technical HTML prints November 22, 2022 02:54 PM. The Board's 2020 summary prints **Run Date 11/24/20 02:26 PM**, while its linked technical HTML labels official results updated November 30, 2020 12:49 PM. Those clocks have no stated timezone here. The [Board FAQ](https://elections.ri.gov/faq) distinguishes official/certified stages from preliminary totals. This package verifies the Board publication labels and numerical controls; it does not supply a separately signed certification instrument or establish an exhaustive later-amendment history. The current linked XLSX publication is a separate observation whose numeric agreement is tested, not a date inferred from its URL. [2022 Board summary](https://elections.ri.gov/sites/g/files/xkgbur756/files/2023-06/STATEWIDE%20SUMMARY.pdf), [2020 Board summary](https://elections.ri.gov/sites/g/files/xkgbur756/files/2022-02/statewidesummary2020gen.pdf).

Every member of all six technical ZIPs, including Mac metadata, is retained once in the original ZIP reference and inventoried with CRC/hash/size. Root short/long prefixes agree on **20,921 records (2024), 24,973 (2022), 16,573 (2020)**. Root, nested results and setup are nonadditive views. Selected root/nested differences affect **57 candidate/context rows and 114 numeric fields in 2024; 2,712 rows and 9,706 fields in 2022; 4,829 rows and 16,072 fields in 2020**. Setup fields are explicit zeros. Root is selected because it agrees exactly with Board controls and municipal HTML, not from filename or ZIP clock. No test designation, correction cause or chronology is inferred. [All view differences](data/turnout/extracts/archive-view-comparison.json), [ZIP inventory](data/turnout/source/zip-members.json), [all full long rows](data/turnout/extracts/all-long-rows.jsonl.gz).

## Candidate universe and whole-state reconciliation

The tables preserve source party and candidate strings, including party prefixes within names. Generic Write-in is a separate published bucket. No named entries are added to it. Each candidate's sum over all applicable native codes agrees exactly with its independent Board PDF control, Board XLSX total and first-three-method vector, and technical statewide HTML. Every municipality's candidate/method vector also agrees with its linked HTML. [Candidate reconciliation](data/turnout/candidate-reconciliation.json), [PDF positions](data/turnout/extracts/pdf-controls.json), [HTML positions](data/turnout/extracts/html-controls.json), [XLSX source cells](data/turnout/extracts/workbook-selected-rows.jsonl.gz).

| Year/contest | Native candidate code | Party, verbatim | Candidate, verbatim trimmed | Native sum = Board control | First / second / third method totals |
| --- | --- | --- | --- | ---: | --- |
| 2020 / Presidential Electors For: | 001 | `REP` | Donald J. Trump | 199,922 | 107,500 / 32,326 / 60,096 |
| 2020 / Presidential Electors For: | 002 | `DEM` | Joseph R. Biden | 307,486 | 87,295 / 133,474 / 86,717 |
| 2020 / Presidential Electors For: | 003 | `All` | Roque "Rocky" De La Fuente | 923 | 463 / 272 / 188 |
| 2020 / Presidential Electors For: | 004 | `AS ` | Brian Carroll | 767 | 346 / 257 / 164 |
| 2020 / Presidential Electors For: | 005 | `S&L` | Gloria La Riva | 847 | 389 / 319 / 139 |
| 2020 / Presidential Electors For: | 006 | `Lib` | Jo Jorgensen | 5,053 | 2,815 / 1,210 / 1,028 |
| 2020 / Presidential Electors For: | 007 | `NON` | WRITE-IN | 2,759 | 1,286 / 937 / 536 |
| 2020 / Senator in Congress | 001 | `REP` | Allen R. Waters | 164,855 | 88,083 / 25,122 / 51,650 |
| 2020 / Senator in Congress | 002 | `DEM` | John F. Reed | 328,574 | 97,823 / 138,365 / 92,386 |
| 2020 / Senator in Congress | 003 | `NON` | WRITE-IN | 833 | 398 / 258 / 177 |
| 2022 / Governor | 001 | `REP` | REP Ashley Marie Kalus | 139,001 | 108,123 / 6,914 / 23,964 |
| 2022 / Governor | 002 | `DEM` | DEM Daniel J. McKee | 207,166 | 136,354 / 25,449 / 45,363 |
| 2022 / Governor | 003 | `Ind` | Ind Zachary Baker Hurwitz | 4,512 | 3,384 / 429 / 699 |
| 2022 / Governor | 004 | `Ind` | Ind Paul A. Rianna, Jr. | 3,123 | 2,286 / 322 / 515 |
| 2022 / Governor | 005 | `Lib` | Lib Elijah J. Gizzarelli | 2,811 | 2,246 / 212 / 353 |
| 2022 / Governor | 006 | `NON` | Write-in | 1,057 | 668 / 179 / 210 |
| 2024 / Presidential Electors For: | 001 | `DEM` | Kamala D. Harris | 285,156 | 144,676 / 41,699 / 98,781 |
| 2024 / Presidential Electors For: | 002 | `REP` | Donald J. Trump | 214,406 | 133,245 / 12,215 / 68,946 |
| 2024 / Presidential Electors For: | 003 | `Ken` | Robert F. Kennedy, Jr. | 5,045 | 3,564 / 420 / 1,061 |
| 2024 / Presidential Electors For: | 004 | `Par` | Robert "Robby" Wells | 359 | 232 / 45 / 82 |
| 2024 / Presidential Electors For: | 005 | `Lib` | Chase Oliver | 1,617 | 1,140 / 135 / 342 |
| 2024 / Presidential Electors For: | 006 | `Grn` | Jill Stein | 2,900 | 2,022 / 279 / 599 |
| 2024 / Presidential Electors For: | 007 | `S&L` | Claudia De la Cruz | 1,176 | 817 / 139 / 220 |
| 2024 / Presidential Electors For: | 008 | `NON` | Write-in | 2,727 | 1,729 / 279 / 719 |
| 2024 / Senator in Congress | 001 | `DEM` | DEM Sheldon Whitehouse | 294,665 | 152,053 / 41,750 / 100,862 |
| 2024 / Senator in Congress | 002 | `REP` | REP Patricia Morgan | 196,039 | 117,701 / 11,535 / 66,803 |
| 2024 / Senator in Congress | 003 | `NON` | Write-in | 1,244 | 847 / 108 / 289 |

2024 Senate is **Whitehouse–Morgan, the other Class I seat**; 2020 Reed–Waters is the relevant same Class II seat. **2022 governor is the actual recent midterm comparator.** No 2022 Rhode Island Senate or 2024 governor contest is invented. Historical elections and candidate effects are separate. [2024 state summary](https://www.ri.gov/election/results/2024/general_election/), [2020 state summary](https://www.ri.gov/election/results/2020/general_election/), [2022 state summary](https://www.ri.gov/election/results/2022/general_election/).

The [Board's 2024 federal/state write-in workbook](https://elections.ri.gov/sites/g/files/xkgbur756/files/2025-04/Write%20In%20Report%20City%20Totals%20RQ.xlsx), linked from its [publications page](https://elections.ri.gov/elections/publications), has 39 municipal Senate headline totals summing **1,239**, exactly the technical municipal generic total. The four federal-admin generic buckets contribute another **5**, producing **1,244 statewide**. The complete workbook literal detail cells sum **1,227**; eight municipal detail/headline differences are retained individually in [write-in scope comparison](data/turnout/extracts/writein-scope-comparison.json). Repeated spellings and `Blank`/`None` entries are not deduplicated or treated as valid named candidates. Details have no method or native precinct allocation. These differences remain unallocated. The original row6-only summary was **1,226 / nine discrepancies** because it omitted Cranston `D5=Mario Frioli ` (trailing space) / `E5=1`. A structural header/headline criterion now includes that row without a fixed detail start row. This is an extractor-summary correction, not a source publication or native-vote change. Both scopes and all 1,955 D/E cells with raw OOXML attributes/positions are retained in [original-detail proof](data/turnout/extracts/writein-original-detail-proof.json); the full prior 362-file package is [historically reconstructable](data/turnout/history/pre-repair-v1/capture.json). The independent baseline included row5 from its original extraction and was not repaired. [All literal selected cells and formulas](data/turnout/extracts/2024-senate-writein-cells.json). The separately linked historical write-in PDFs are retained in full; 2020's Senate scan lacks a usable text layer and its first page is explicitly a state Senate in General Assembly District4 tally, not a U.S. Senate eligible-candidate roster. Generic eligibility and valid named write-in coverage remain unresolved, not a finish gate.

A **named printed candidates only arithmetic sensitivity** excludes every generic bucket: **490,704 statewide**, native top 15 **34,630 (7.0572076038%)**, minimum **242 contexts / 393,148 (80.1191757149%)**, preceded by **392,143**. Its own full order and membership are retained in `rankings.json` and the contract. This deliberately extreme alternative does not assert legal 80% membership robustness under unknown write-in eligibility.

## Native inventory and disjoint parents

Municipal parentage comes from each original city/town page's literal child links, independently acquired for all **39 municipalities in all three years**. It is not inferred from matching names or numeric ranges. [All 117 parent pages and complete child arrays](data/turnout/extracts/municipal-hierarchy.json). The [official Census 2020 county-subdivision table](https://tigerweb.geo.census.gov/tigerwebmain/Files/acs26/tigerweb_acs26_cousub_2020_tab20_ri.html) supplies municipal 10-digit GEOIDs and county context only; its nonmunicipal undefined-water entry is not an election geography. These historical identification labels do not approve current boundaries or a 2026 precinct crosswalk.

| Source scope | Municipal linked native contexts | Separate state-admin contexts | Senate/governor contexts | President contexts | Ballot contexts | Registration contexts |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2024 | 493 | 4 | 458 Senate | 497 | 497 | 483 |
| 2022 | 454 | 4 in statistics only | 454 governor | No presidential election | 458 | 442 |
| 2020 | 500 | 4 | 465 Senate | 504 | 504 | 504 |

In 2024, **39 presidential-only contexts are absent from Senate**, not zero Senate votes. The 458 actual Senate contexts include 15 source-published zero totals; these are different from unavailable rows. The [497-entry native inventory](data/turnout/native-inventory.json) is year scoped (the full file also contains the separate 2020 and 2022 inventories); each entry retains literal code/name, parent-link evidence, administrative/limited/presidential role, raw row keys, source fields and null availability. The complete primary dispatch inventory is repeated in the contract. Native keys and the source-position anchors are not assertions that equal labels across years refer to the same boundaries, split styles, scanners, sites, vote centers or VTDs.

**9001 Federal Precinct #1, 9002 Federal Precinct #2, 9011 Federal Precinct #1S and 9012 Federal Precinct #2S** have no municipal parent in the published hierarchy. They remain under the state, with no municipality, municipal FIPS or polygon allocation. Their 2024 Senate votes are **487, 526, 378, 82** (sum **1,473**). All are included in the canonical native denominator and order. Their published mail vector does not authorize a speculative municipal or physical join. The municipal-only Senate sum **490,475** plus these four entries closes **491,948**. [Root long ZIP](https://www.ri.gov/election/results/2024/general_election/data/rigen2024l.zip), [Board XLSX](https://elections.ri.gov/sites/g/files/xkgbur756/files/2025-01/Gen24EX%20%281%29.xlsx).

## Ballots, registration, blanks and method scope

| Year and scope | Candidate + generic votes | Under | Over | Contest ballot scope | State Election Ballots Cast | Registered Voters – Total | Election blank ballots |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2024 Senate | 491,948 | 15,770 | 143 | 507,861 published | 517,231 | 787,559 | 6,171 |
| 2024 president | 513,386 | 2,824 | 1,021 | 517,231 published | 517,231 | 787,559 | 6,171 |
| 2022 governor | 357,670 | 3,485 | 119 | 361,274, arithmetic sum of candidate/under/over | 361,449 | 815,417 | unavailable |
| 2020 Senate | 494,262 | 20,539 | 162 | 514,963, arithmetic sum of candidate/under/over | 521,185 | 808,953 | 3,342 |
| 2020 president | 517,757 | 2,217 | 1,211 | 521,185, arithmetic sum of candidate/under/over | 521,185 | 808,953 | 3,342 |

Sources: [2024 Board summary pp. 1–2](https://elections.ri.gov/sites/g/files/xkgbur756/files/2024-12/Gen24SummaryReport.pdf), [2022 Board summary pp. 1–2](https://elections.ri.gov/sites/g/files/xkgbur756/files/2023-06/STATEWIDE%20SUMMARY.pdf), [2020 Board summary p. 1](https://elections.ri.gov/sites/g/files/xkgbur756/files/2022-02/statewidesummary2020gen.pdf). All retained PDF numeric controls include page, line and original line text. The five contest identities above are separate; 2020 president is retained for source closure, not substituted for same-seat Senate.

The 2024 Senate under/over gap is **15,913 within its own 507,861 contest-ballot scope**. The remaining **9,370** between that scope and state election ballots equals the published ballot total in the 39 absent-Senate presidential contexts. The analogous 2020 difference is **6,222**, again exactly those 39 contexts' ballots. In 2022 the separate four federal administrative statistical contexts have **175 ballots**, exactly the difference between state ballots and the governor candidate/under/over sum; there are no governor rows for those contexts, so no governor zeros are fabricated. These are verified source coverage reconciliations, not residual allocations. [Native statistics and controls](data/turnout/native-inventory.json), [state controls](data/turnout/state-controls.json).

Election `Ballots Cast - Blank` is a separate source statistic, not another candidate or a field to add to contest under/over totals. Municipal/native contest under/over and contest-ballot fields are unavailable in the acquired candidate exports and remain null; no statewide total is allocated downward. Ballot and registration row universes differ: in 2024, 14 native contexts lack registration rows; in 2022, 16 do. Explicit administrative registration zeroes are preserved. Registration totals sum over available rows and reconcile exactly to the Board summary, but active/inactive status and exact registration extract date are not specified beyond the election/publication scope. The published rounded statewide ballot/registration rates are 65.68% (2024), 44.33% (2022) and 64.43% (2020); none is a voting-eligible-population rate. No missing registration is filled with zero. [Board XLSX 2024](https://elections.ri.gov/sites/g/files/xkgbur756/files/2025-01/Gen24EX%20%281%29.xlsx), [2022](https://elections.ri.gov/sites/g/files/xkgbur756/files/2023-06/RIGEN22%20%282%29.xlsx), [2020](https://elections.ri.gov/sites/g/files/xkgbur756/files/2022-02/rigen20.xlsx).

All 14 method slots are preserved per raw candidate row. The 2022 description labels groups 1–3 Election Day / Mail Ballots / Early Voting; the same linked description is used by the 2024 technical index. The 2020 index links the 2016 description, whose third slot is **unlabelled**; 2020 HTML calls the matching vector **Emergency ballots**, and its XLSX says **Emergency**. Groups 4–14 remain unlabelled even where their reported values are zero. Source labels are retained separately rather than mapped to a current method by position. Registration's method zeroes do not define registration by voting method. [2022/2024 format](https://www.ri.gov/election/results/20220819_data_description.pdf), [2020-linked format](https://www.ri.gov/election/results/20160902_data_description.pdf), [method scope metadata](data/turnout/source/method-scopes.json).

The 2024 official PDF's **414 of 458 Senate** and **453 of 497 president** reporting flags do not mean percentages of votes completed or exact outstanding pools. The technical pages warn that a precinct with several scanners can show 100% reported after one scanner. This package establishes no current November feed, collection implementation, live cadence, feed exhaustion, exact remaining votes, probability calibration or approved current geometry. Historical five-minute technical-page language is not a 2026 contract. [Board summary](https://elections.ri.gov/sites/g/files/xkgbur756/files/2024-12/Gen24SummaryReport.pdf), [technical Senate page](https://www.ri.gov/election/results/2024/general_election/races/2.html).

## Separate native sensitivity orders

Each row independently ranks its own original reporting universe. These are historical volume/denominator sensitivities, not cross-year native identity joins. Registration covers its published rows only; the 497-ballot sensitivity includes the 39 unavailable Senate contexts.

| Ranking basis | Reporting contexts | State volume | Top 15 votes/records | Top 15 % | Minimum 80% count | Preceding votes | Crossing cumulative |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2024 Senate reported candidate + generic | 458 | 491,948 | 34,697 | 7.05298121 | 242 | 393,066 | 394,072 |
| 2024 Senate printed candidates only | 458 | 490,704 | 34,630 | 7.05720760 | 242 | 392,143 | 393,148 |
| 2024 president candidate + generic | 497 | 513,386 | 35,176 | 6.85176456 | 250 | 410,483 | 411,498 |
| 2022 governor candidate + generic | 454 | 357,670 | 28,122 | 7.86255487 | 231 | 285,488 | 286,230 |
| 2020 same-seat Senate candidate + generic | 465 | 494,262 | 35,356 | 7.15329117 | 243 | 395,404 | 396,444 |
| 2024 election ballots | 497 | 517,231 | 35,451 | 6.85399754 | 250 | 413,649 | 414,675 |
| 2024 registration records | 483 | 787,559 | 49,786 | 6.32155813 | 251 | 628,560 | 630,251 |

All full sensitivity orders, crossings and remainders are in [rankings.json](data/turnout/rankings.json), calculated from the primary originals cited above. The primary 242-context set is not replaced by any sensitivity.

## Municipality and administrative parent sensitivity only

The 43 disjoint parent entries retain all 39 municipalities and the four separate state-admin entries, with full child arrays and FIPS evidence in [parent sensitivity](data/turnout/parent-sensitivity.json) and [43-row CSV](data/turnout/parent-sensitivity.csv). They are **not canonical native dispatch**.

Parent top 15 contribute **333,390 / 491,948 = 67.7693577370%**. The minimum parent set is **21 municipalities / 395,379 = 80.3700797645%**, preceded by **20 / 386,501 = 78.5654174831%**, crossing at Tiverton; parent remainder **96,569**. Exact parent order through crossing: **Providence, Warwick, Cranston, Pawtucket, East Providence, Coventry, Cumberland, North Kingstown, South Kingstown, North Providence, Johnston, West Warwick, Woonsocket, Lincoln, Westerly, Smithfield, Bristol, Portsmouth, Barrington, Newport, Tiverton**. Native prioritization may select contexts in municipalities outside this parent set.

The actual **2022 governor** comparator totals **357,670**. Its parent top 15 contribute **239,262 (66.89462354%)**. The parent minimum is **22 / 292,789 (81.86009450%)**, versus **21 / 286,002 (79.96253530%)**, crossing at East Greenwich. Native governor priority instead needs 231 contexts; these are different geographic questions. All four federal-admin governor cells remain unavailable while their published election ballots survive. [Original governor HTML](https://www.ri.gov/election/results/2022/general_election/), [Board summary](https://elections.ri.gov/sites/g/files/xkgbur756/files/2023-06/STATEWIDE%20SUMMARY.pdf).

| Parent rank | Municipality or state-admin entry | 2024 Senate | Cumulative | 2020 Senate | 2022 governor | 2024 president | 2024 election ballots | 2024 registration |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Providence | 51,663 | 51,663 | 53,612 | 33,298 | 56,395 | 56,733 | 110,066 |
| 2 | Warwick | 44,860 | 96,523 | 45,067 | 34,234 | 45,984 | 46,310 | 67,299 |
| 3 | Cranston | 39,234 | 135,757 | 39,546 | 29,125 | 40,806 | 41,094 | 61,130 |
| 4 | Pawtucket | 22,771 | 158,528 | 23,616 | 13,569 | 24,660 | 24,878 | 46,586 |
| 5 | East Providence | 22,019 | 180,547 | 22,073 | 15,894 | 22,996 | 23,180 | 35,872 |
| 6 | Coventry | 19,685 | 200,232 | 19,253 | 14,513 | 20,332 | 20,441 | 28,550 |
| 7 | Cumberland | 18,713 | 218,945 | 18,755 | 13,398 | 19,405 | 19,587 | 27,617 |
| 8 | North Kingstown | 16,945 | 235,890 | 17,123 | 13,494 | 17,368 | 17,497 | 23,710 |
| 9 | South Kingstown | 16,178 | 252,068 | 16,182 | 13,068 | 16,688 | 16,785 | 21,938 |
| 10 | North Providence | 15,649 | 267,717 | 15,910 | 10,788 | 16,351 | 16,469 | 25,702 |
| 11 | Johnston | 15,092 | 282,809 | 14,542 | 10,796 | 15,717 | 15,831 | 24,164 |
| 12 | West Warwick | 13,694 | 296,503 | 13,490 | 9,786 | 14,203 | 14,302 | 22,194 |
| 13 | Woonsocket | 12,495 | 308,998 | 12,576 | 8,012 | 13,370 | 13,484 | 26,430 |
| 14 | Lincoln | 12,263 | 321,261 | 12,258 | 9,155 | 12,603 | 12,695 | 17,885 |
| 15 | Westerly | 12,129 | 333,390 | 12,278 | 9,592 | 12,621 | 12,769 | 19,285 |
| 16 | Smithfield | 11,365 | 344,755 | 11,146 | 8,552 | 11,757 | 11,848 | 15,932 |
| 17 | Bristol | 11,178 | 355,933 | 11,182 | 8,371 | 11,616 | 11,712 | 16,002 |
| 18 | Portsmouth | 10,418 | 366,351 | 10,565 | 7,704 | 10,708 | 10,784 | 14,803 |
| 19 | Barrington | 10,409 | 376,760 | 10,524 | 8,116 | 10,607 | 10,715 | 14,281 |
| 20 | Newport | 9,741 | 386,501 | 10,205 | 7,285 | 10,160 | 10,255 | 15,196 |
| 21 | Tiverton | 8,878 | 395,379 | 8,785 | 6,206 | 9,210 | 9,265 | 13,353 |
| 22 | Narragansett | 8,797 | 404,176 | 8,754 | 7,252 | 9,100 | 9,186 | 12,169 |
| 23 | Burrillville | 8,427 | 412,603 | 8,189 | 6,018 | 8,724 | 8,772 | 12,755 |
| 24 | East Greenwich | 8,412 | 421,015 | 8,448 | 6,787 | 8,549 | 8,634 | 11,467 |
| 25 | Middletown | 7,733 | 428,748 | 8,162 | 5,910 | 8,032 | 8,099 | 11,803 |
| 26 | North Smithfield | 6,983 | 435,731 | 6,927 | 5,119 | 7,205 | 7,238 | 10,233 |
| 27 | Scituate | 6,513 | 442,244 | 6,464 | 5,072 | 6,679 | 6,727 | 9,057 |
| 28 | Glocester | 6,184 | 448,428 | 5,890 | 4,657 | 6,380 | 6,417 | 8,917 |
| 29 | Warren | 5,902 | 454,330 | 5,653 | 4,088 | 6,112 | 6,167 | 8,813 |
| 30 | Charlestown | 5,197 | 459,527 | 4,989 | 4,187 | 5,354 | 5,408 | 7,302 |
| 31 | Richmond | 4,856 | 464,383 | 4,656 | 3,677 | 4,971 | 5,002 | 6,848 |
| 32 | Hopkinton | 4,846 | 469,229 | 4,639 | 3,719 | 4,992 | 5,040 | 7,014 |
| 33 | West Greenwich | 3,978 | 473,207 | 3,867 | 3,125 | 4,080 | 4,107 | 5,484 |
| 34 | Exeter | 3,975 | 477,182 | 3,951 | 3,219 | 4,074 | 4,108 | 5,611 |
| 35 | Jamestown | 3,886 | 481,068 | 3,986 | 3,192 | 3,946 | 3,976 | 5,029 |
| 36 | Central Falls | 3,146 | 484,214 | 3,668 | 1,636 | 3,683 | 3,710 | 8,555 |
| 37 | Foster | 2,878 | 487,092 | 2,739 | 2,217 | 2,948 | 2,970 | 4,012 |
| 38 | Little Compton | 2,527 | 489,619 | 2,455 | 2,101 | 2,562 | 2,589 | 3,317 |
| 39 | New Shoreham | 856 | 490,475 | 909 | 738 | 868 | 870 | 1,178 |
| 40 | Federal Precinct #2 | 526 | 491,001 | 459 | unavailable | 559 | 561 | 0 |
| 41 | Federal Precinct #1 | 487 | 491,488 | 497 | unavailable | 522 | 524 | 0 |
| 42 | Federal Precinct #1S | 378 | 491,866 | 224 | unavailable | 402 | 405 | 0 |
| 43 | Federal Precinct #2S | 82 | 491,948 | 48 | unavailable | 87 | 87 | 0 |

## Complete canonical 458-native order

Source: root [2024 long ZIP](https://www.ri.gov/election/results/2024/general_election/data/rigen2024l.zip), every candidate/method row independently reconciled to [Board XLSX](https://elections.ri.gov/sites/g/files/xkgbur756/files/2025-01/Gen24EX%20%281%29.xlsx) and [Board summary](https://elections.ri.gov/sites/g/files/xkgbur756/files/2024-12/Gen24SummaryReport.pdf). Native source code/name and source-position keys are separate; byte offsets and all raw fields are in the CSV/contract. `P` denotes ranks 1–242; `R` denotes the full remainder. Source-published zeroes remain in order. All contexts retain their municipal parent or explicit state-admin role in the contract.

| Rank | Native code | Source name | Votes | State % | Cumulative votes | Cumulative % | Set |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `0707` | Cranston 0707 | 2,585 | 0.525462 | 2,585 | 0.525462 | P |
| 2 | `1801` | Little Compton 1801 | 2,527 | 0.513672 | 5,112 | 1.039134 | P |
| 3 | `0725` | Cranston 0725 | 2,357 | 0.479116 | 7,469 | 1.518250 | P |
| 4 | `0705` | Cranston 0705 | 2,323 | 0.472204 | 9,792 | 1.990454 | P |
| 5 | `2002` | Narragansett 2002 | 2,299 | 0.467326 | 12,091 | 2.457780 | P |
| 6 | `3522` | Warwick 3522 | 2,296 | 0.466716 | 14,387 | 2.924496 | P |
| 7 | `3002` | Scituate 3002 | 2,292 | 0.465903 | 16,679 | 3.390399 | P |
| 8 | `3521` | Warwick 3521 | 2,284 | 0.464277 | 18,963 | 3.854676 | P |
| 9 | `0711` | Cranston 0711 | 2,279 | 0.463260 | 21,242 | 4.317936 | P |
| 10 | `0718` | Cranston 0718 | 2,270 | 0.461431 | 23,512 | 4.779367 | P |
| 11 | `3804` | West Warwick 3804 | 2,266 | 0.460618 | 25,778 | 5.239985 | P |
| 12 | `3101` | Smithfield 3101 | 2,238 | 0.454926 | 28,016 | 5.694911 | P |
| 13 | `2309` | North Kingstown 2309 | 2,231 | 0.453503 | 30,247 | 6.148414 | P |
| 14 | `2501` | North Smithfield 2501 | 2,228 | 0.452893 | 32,475 | 6.601307 | P |
| 15 | `0610` | Coventry 0610 | 2,222 | 0.451674 | 34,697 | 7.052981 | P |
| 16 | `3807` | West Warwick 3807 | 2,211 | 0.449438 | 36,908 | 7.502419 | P |
| 17 | `0901` | East Greenwich 0901 | 2,205 | 0.448218 | 39,113 | 7.950637 | P |
| 18 | `2004` | Narragansett 2004 | 2,195 | 0.446185 | 41,308 | 8.396822 | P |
| 19 | `3209` | South Kingstown 3209 | 2,172 | 0.441510 | 43,480 | 8.838333 | P |
| 20 | `2003` | Narragansett 2003 | 2,158 | 0.438664 | 45,638 | 9.276997 | P |
| 21 | `3001` | Scituate 3001 | 2,153 | 0.437648 | 47,791 | 9.714645 | P |
| 22 | `1401` | Hopkinton 1401 | 2,147 | 0.436428 | 49,938 | 10.151073 | P |
| 23 | `0905` | East Greenwich 0905 | 2,141 | 0.435209 | 52,079 | 10.586281 | P |
| 24 | `2001` | Narragansett 2001 | 2,141 | 0.435209 | 54,220 | 11.021490 | P |
| 25 | `1011` | East Providence 1011 | 2,134 | 0.433786 | 56,354 | 11.455276 | P |
| 26 | `1001` | East Providence 1001 | 2,124 | 0.431753 | 58,478 | 11.887029 | P |
| 27 | `3507` | Warwick 3507 | 2,121 | 0.431143 | 60,599 | 12.318172 | P |
| 28 | `3605` | Westerly 3605 | 2,118 | 0.430533 | 62,717 | 12.748705 | P |
| 29 | `3518` | Warwick 3518 | 2,117 | 0.430330 | 64,834 | 13.179035 | P |
| 30 | `2301` | North Kingstown 2301 | 2,102 | 0.427281 | 66,936 | 13.606316 | P |
| 31 | `3604` | Westerly 3604 | 2,101 | 0.427078 | 69,037 | 14.033394 | P |
| 32 | `3504` | Warwick 3504 | 2,094 | 0.425655 | 71,131 | 14.459049 | P |
| 33 | `3526` | Warwick 3526 | 2,084 | 0.423622 | 73,215 | 14.882671 | P |
| 34 | `2707` | Portsmouth 2707 | 2,083 | 0.423419 | 75,298 | 15.306089 | P |
| 35 | `3104` | Smithfield 3104 | 2,077 | 0.422199 | 77,375 | 15.728288 | P |
| 36 | `3105` | Smithfield 3105 | 2,074 | 0.421589 | 79,449 | 16.149878 | P |
| 37 | `3003` | Scituate 3003 | 2,068 | 0.420370 | 81,517 | 16.570247 | P |
| 38 | `2706` | Portsmouth 2706 | 2,066 | 0.419963 | 83,583 | 16.990210 | P |
| 39 | `0812` | Cumberland 0812 | 2,053 | 0.417321 | 85,636 | 17.407531 | P |
| 40 | `2308` | North Kingstown 2308 | 2,048 | 0.416304 | 87,684 | 17.823835 | P |
| 41 | `3505` | Warwick 3505 | 2,048 | 0.416304 | 89,732 | 18.240139 | P |
| 42 | `3401` | Warren 3401 | 2,035 | 0.413662 | 91,767 | 18.653801 | P |
| 43 | `0704` | Cranston 0704 | 2,026 | 0.411832 | 93,793 | 19.065633 | P |
| 44 | `1502` | Jamestown 1502 | 2,009 | 0.408376 | 95,802 | 19.474009 | P |
| 45 | `3208` | South Kingstown 3208 | 1,998 | 0.406140 | 97,800 | 19.880150 | P |
| 46 | `0723` | Cranston 0723 | 1,986 | 0.403701 | 99,786 | 20.283851 | P |
| 47 | `0104` | Barrington 0104 | 1,982 | 0.402888 | 101,768 | 20.686739 | P |
| 48 | `0202` | Bristol 0202 | 1,974 | 0.401262 | 103,742 | 21.088001 | P |
| 49 | `2703` | Portsmouth 2703 | 1,972 | 0.400855 | 105,714 | 21.488857 | P |
| 50 | `0102` | Barrington 0102 | 1,965 | 0.399432 | 107,679 | 21.888289 | P |
| 51 | `0807` | Cumberland 0807 | 1,963 | 0.399026 | 109,642 | 22.287315 | P |
| 52 | `1103` | Exeter 1103 | 1,952 | 0.396790 | 111,594 | 22.684105 | P |
| 53 | `0722` | Cranston 0722 | 1,929 | 0.392115 | 113,523 | 23.076219 | P |
| 54 | `0604` | Coventry 0604 | 1,926 | 0.391505 | 115,449 | 23.467724 | P |
| 55 | `3603` | Westerly 3603 | 1,920 | 0.390285 | 117,369 | 23.858009 | P |
| 56 | `2702` | Portsmouth 2702 | 1,911 | 0.388456 | 119,280 | 24.246465 | P |
| 57 | `0106` | Barrington 0106 | 1,907 | 0.387643 | 121,187 | 24.634108 | P |
| 58 | `1402` | Hopkinton 1402 | 1,907 | 0.387643 | 123,094 | 25.021750 | P |
| 59 | `1704` | Lincoln 1704 | 1,907 | 0.387643 | 125,001 | 25.409393 | P |
| 60 | `0103` | Barrington 0103 | 1,903 | 0.386830 | 126,904 | 25.796222 | P |
| 61 | `0617` | Coventry 0617 | 1,899 | 0.386016 | 128,803 | 26.182239 | P |
| 62 | `3516` | Warwick 3516 | 1,893 | 0.384797 | 130,696 | 26.567036 | P |
| 63 | `0803` | Cumberland 0803 | 1,879 | 0.381951 | 132,575 | 26.948986 | P |
| 64 | `0805` | Cumberland 0805 | 1,877 | 0.381544 | 134,452 | 27.330531 | P |
| 65 | `1501` | Jamestown 1501 | 1,875 | 0.381138 | 136,327 | 27.711669 | P |
| 66 | `2819` | Providence 2819 | 1,857 | 0.377479 | 138,184 | 28.089148 | P |
| 67 | `1705` | Lincoln 1705 | 1,849 | 0.375853 | 140,033 | 28.465000 | P |
| 68 | `0902` | East Greenwich 0902 | 1,847 | 0.375446 | 141,880 | 28.840447 | P |
| 69 | `1706` | Lincoln 1706 | 1,847 | 0.375446 | 143,727 | 29.215893 | P |
| 70 | `2310` | North Kingstown 2310 | 1,847 | 0.375446 | 145,574 | 29.591339 | P |
| 71 | `0611` | Coventry 0611 | 1,834 | 0.372804 | 147,408 | 29.964143 | P |
| 72 | `3509` | Warwick 3509 | 1,827 | 0.371381 | 149,235 | 30.335523 | P |
| 73 | `1302` | Glocester 1302 | 1,820 | 0.369958 | 151,055 | 30.705481 | P |
| 74 | `3602` | Westerly 3602 | 1,819 | 0.369755 | 152,874 | 31.075236 | P |
| 75 | `2502` | North Smithfield 2502 | 1,816 | 0.369145 | 154,690 | 31.444380 | P |
| 76 | `2601` | Pawtucket 2601 | 1,807 | 0.367315 | 156,497 | 31.811696 | P |
| 77 | `3525` | Warwick 3525 | 1,807 | 0.367315 | 158,304 | 32.179011 | P |
| 78 | `3204` | South Kingstown 3204 | 1,803 | 0.366502 | 160,107 | 32.545513 | P |
| 79 | `0810` | Cumberland 0810 | 1,794 | 0.364673 | 161,901 | 32.910186 | P |
| 80 | `3502` | Warwick 3502 | 1,787 | 0.363250 | 163,688 | 33.273435 | P |
| 81 | `3301` | Tiverton 3301 | 1,785 | 0.362843 | 165,473 | 33.636279 | P |
| 82 | `3524` | Warwick 3524 | 1,785 | 0.362843 | 167,258 | 33.999122 | P |
| 83 | `1609` | Johnston 1609 | 1,778 | 0.361420 | 169,036 | 34.360542 | P |
| 84 | `0609` | Coventry 0609 | 1,776 | 0.361014 | 170,812 | 34.721556 | P |
| 85 | `2303` | North Kingstown 2303 | 1,766 | 0.358981 | 172,578 | 35.080537 | P |
| 86 | `3606` | Westerly 3606 | 1,760 | 0.357761 | 174,338 | 35.438298 | P |
| 87 | `2901` | Richmond 2901 | 1,759 | 0.357558 | 176,097 | 35.795856 | P |
| 88 | `3102` | Smithfield 3102 | 1,757 | 0.357152 | 177,854 | 36.153008 | P |
| 89 | `2102` | Newport 2102 | 1,753 | 0.356338 | 179,607 | 36.509347 | P |
| 90 | `3808` | West Warwick 3808 | 1,751 | 0.355932 | 181,358 | 36.865278 | P |
| 91 | `0724` | Cranston 0724 | 1,747 | 0.355119 | 183,105 | 37.220397 | P |
| 92 | `2401` | North Providence 2401 | 1,739 | 0.353493 | 184,844 | 37.573890 | P |
| 93 | `3404` | Warren 3404 | 1,737 | 0.353086 | 186,581 | 37.926976 | P |
| 94 | `0708` | Cranston 0708 | 1,732 | 0.352070 | 188,313 | 38.279046 | P |
| 95 | `1201` | Foster 1201 | 1,731 | 0.351866 | 190,044 | 38.630912 | P |
| 96 | `2503` | North Smithfield 2503 | 1,726 | 0.350850 | 191,770 | 38.981762 | P |
| 97 | `2411` | North Providence 2411 | 1,721 | 0.349834 | 193,491 | 39.331596 | P |
| 98 | `0207` | Bristol 0207 | 1,712 | 0.348004 | 195,203 | 39.679600 | P |
| 99 | `1905` | Middletown 1905 | 1,696 | 0.344752 | 196,899 | 40.024352 | P |
| 100 | `2813` | Providence 2813 | 1,695 | 0.344549 | 198,594 | 40.368901 | P |
| 101 | `2619` | Pawtucket 2619 | 1,691 | 0.343736 | 200,285 | 40.712636 | P |
| 102 | `3302` | Tiverton 3302 | 1,680 | 0.341500 | 201,965 | 41.054136 | P |
| 103 | `1017` | East Providence 1017 | 1,667 | 0.338857 | 203,632 | 41.392993 | P |
| 104 | `1904` | Middletown 1904 | 1,667 | 0.338857 | 205,299 | 41.731850 | P |
| 105 | `3531` | Warwick 3531 | 1,666 | 0.338654 | 206,965 | 42.070503 | P |
| 106 | `1014` | East Providence 1014 | 1,665 | 0.338450 | 208,630 | 42.408954 | P |
| 107 | `1301` | Glocester 1301 | 1,664 | 0.338247 | 210,294 | 42.747201 | P |
| 108 | `3203` | South Kingstown 3203 | 1,664 | 0.338247 | 211,958 | 43.085448 | P |
| 109 | `3701` | West Greenwich 3701 | 1,659 | 0.337231 | 213,617 | 43.422679 | P |
| 110 | `3103` | Smithfield 3103 | 1,656 | 0.336621 | 215,273 | 43.759300 | P |
| 111 | `0802` | Cumberland 0802 | 1,650 | 0.335401 | 216,923 | 44.094701 | P |
| 112 | `3910` | Woonsocket 3910 | 1,634 | 0.332149 | 218,557 | 44.426850 | P |
| 113 | `2108` | Newport 2108 | 1,631 | 0.331539 | 220,188 | 44.758389 | P |
| 114 | `0714` | Cranston 0714 | 1,626 | 0.330523 | 221,814 | 45.088912 | P |
| 115 | `0306` | Burrillville 0306 | 1,623 | 0.329913 | 223,437 | 45.418825 | P |
| 116 | `3911` | Woonsocket 3911 | 1,622 | 0.329710 | 225,059 | 45.748534 | P |
| 117 | `0101` | Barrington 0101 | 1,610 | 0.327270 | 226,669 | 46.075805 | P |
| 118 | `3528` | Warwick 3528 | 1,602 | 0.325644 | 228,271 | 46.401449 | P |
| 119 | `3514` | Warwick 3514 | 1,583 | 0.321782 | 229,854 | 46.723231 | P |
| 120 | `3305` | Tiverton 3305 | 1,581 | 0.321375 | 231,435 | 47.044606 | P |
| 121 | `1007` | East Providence 1007 | 1,570 | 0.319139 | 233,005 | 47.363746 | P |
| 122 | `2830` | Providence 2830 | 1,568 | 0.318733 | 234,573 | 47.682479 | P |
| 123 | `2412` | North Providence 2412 | 1,567 | 0.318530 | 236,140 | 48.001008 | P |
| 124 | `0709` | Cranston 0709 | 1,566 | 0.318326 | 237,706 | 48.319335 | P |
| 125 | `0206` | Bristol 0206 | 1,565 | 0.318123 | 239,271 | 48.637458 | P |
| 126 | `0303` | Burrillville 0303 | 1,565 | 0.318123 | 240,836 | 48.955581 | P |
| 127 | `0616` | Coventry 0616 | 1,565 | 0.318123 | 242,401 | 49.273704 | P |
| 128 | `2109` | Newport 2109 | 1,563 | 0.317717 | 243,964 | 49.591420 | P |
| 129 | `3106` | Smithfield 3106 | 1,562 | 0.317513 | 245,526 | 49.908933 | P |
| 130 | `2902` | Richmond 2902 | 1,560 | 0.317107 | 247,086 | 50.226040 | P |
| 131 | `2402` | North Providence 2402 | 1,557 | 0.316497 | 248,643 | 50.542537 | P |
| 132 | `2818` | Providence 2818 | 1,557 | 0.316497 | 250,200 | 50.859034 | P |
| 133 | `2307` | North Kingstown 2307 | 1,555 | 0.316090 | 251,755 | 51.175124 | P |
| 134 | `1605` | Johnston 1605 | 1,554 | 0.315887 | 253,309 | 51.491011 | P |
| 135 | `1008` | East Providence 1008 | 1,552 | 0.315480 | 254,861 | 51.806492 | P |
| 136 | `1902` | Middletown 1902 | 1,545 | 0.314058 | 256,406 | 52.120549 | P |
| 137 | `2305` | North Kingstown 2305 | 1,543 | 0.313651 | 257,949 | 52.434200 | P |
| 138 | `2820` | Providence 2820 | 1,543 | 0.313651 | 259,492 | 52.747851 | P |
| 139 | `3207` | South Kingstown 3207 | 1,541 | 0.313244 | 261,033 | 53.061096 | P |
| 140 | `2903` | Richmond 2903 | 1,537 | 0.312431 | 262,570 | 53.373527 | P |
| 141 | `1016` | East Providence 1016 | 1,535 | 0.312025 | 264,105 | 53.685552 | P |
| 142 | `3211` | South Kingstown 3211 | 1,514 | 0.307756 | 265,619 | 53.993308 | P |
| 143 | `0801` | Cumberland 0801 | 1,510 | 0.306943 | 267,129 | 54.300251 | P |
| 144 | `3809` | West Warwick 3809 | 1,510 | 0.306943 | 268,639 | 54.607194 | P |
| 145 | `0208` | Bristol 0208 | 1,505 | 0.305927 | 270,144 | 54.913121 | P |
| 146 | `2605` | Pawtucket 2605 | 1,500 | 0.304910 | 271,644 | 55.218031 | P |
| 147 | `2302` | North Kingstown 2302 | 1,495 | 0.303894 | 273,139 | 55.521925 | P |
| 148 | `1608` | Johnston 1608 | 1,487 | 0.302268 | 274,626 | 55.824193 | P |
| 149 | `3607` | Westerly 3607 | 1,484 | 0.301658 | 276,110 | 56.125851 | P |
| 150 | `0713` | Cranston 0713 | 1,481 | 0.301048 | 277,591 | 56.426899 | P |
| 151 | `0904` | East Greenwich 0904 | 1,481 | 0.301048 | 279,072 | 56.727947 | P |
| 152 | `0301` | Burrillville 0301 | 1,476 | 0.300032 | 280,548 | 57.027979 | P |
| 153 | `1002` | East Providence 1002 | 1,467 | 0.298202 | 282,015 | 57.326181 | P |
| 154 | `0602` | Coventry 0602 | 1,463 | 0.297389 | 283,478 | 57.623570 | P |
| 155 | `1607` | Johnston 1607 | 1,456 | 0.295966 | 284,934 | 57.919536 | P |
| 156 | `0205` | Bristol 0205 | 1,454 | 0.295560 | 286,388 | 58.215096 | P |
| 157 | `2403` | North Providence 2403 | 1,454 | 0.295560 | 287,842 | 58.510656 | P |
| 158 | `2817` | Providence 2817 | 1,454 | 0.295560 | 289,296 | 58.806215 | P |
| 159 | `2611` | Pawtucket 2611 | 1,453 | 0.295356 | 290,749 | 59.101572 | P |
| 160 | `2106` | Newport 2106 | 1,451 | 0.294950 | 292,200 | 59.396522 | P |
| 161 | `1903` | Middletown 1903 | 1,448 | 0.294340 | 293,648 | 59.690862 | P |
| 162 | `2407` | North Providence 2407 | 1,440 | 0.292714 | 295,088 | 59.983575 | P |
| 163 | `2814` | Providence 2814 | 1,439 | 0.292511 | 296,527 | 60.276086 | P |
| 164 | `0706` | Cranston 0706 | 1,430 | 0.290681 | 297,957 | 60.566767 | P |
| 165 | `1610` | Johnston 1610 | 1,429 | 0.290478 | 299,386 | 60.857245 | P |
| 166 | `0701` | Cranston 0701 | 1,428 | 0.290275 | 300,814 | 61.147520 | P |
| 167 | `0503` | Charlestown 0503 | 1,421 | 0.288852 | 302,235 | 61.436371 | P |
| 168 | `3205` | South Kingstown 3205 | 1,421 | 0.288852 | 303,656 | 61.725223 | P |
| 169 | `0712` | Cranston 0712 | 1,416 | 0.287835 | 305,072 | 62.013058 | P |
| 170 | `3907` | Woonsocket 3907 | 1,410 | 0.286616 | 306,482 | 62.299674 | P |
| 171 | `2804` | Providence 2804 | 1,406 | 0.285803 | 307,888 | 62.585477 | P |
| 172 | `2620` | Pawtucket 2620 | 1,397 | 0.283973 | 309,285 | 62.869450 | P |
| 173 | `2862` | Providence 2862 | 1,392 | 0.282957 | 310,677 | 63.152406 | P |
| 174 | `3206` | South Kingstown 3206 | 1,389 | 0.282347 | 312,066 | 63.434753 | P |
| 175 | `3523` | Warwick 3523 | 1,387 | 0.281940 | 313,453 | 63.716694 | P |
| 176 | `2613` | Pawtucket 2613 | 1,383 | 0.281127 | 314,836 | 63.997821 | P |
| 177 | `0502` | Charlestown 0502 | 1,381 | 0.280721 | 316,217 | 64.278542 | P |
| 178 | `0302` | Burrillville 0302 | 1,376 | 0.279704 | 317,593 | 64.558246 | P |
| 179 | `1901` | Middletown 1901 | 1,374 | 0.279298 | 318,967 | 64.837544 | P |
| 180 | `0721` | Cranston 0721 | 1,364 | 0.277265 | 320,331 | 65.114809 | P |
| 181 | `0808` | Cumberland 0808 | 1,362 | 0.276859 | 321,693 | 65.391667 | P |
| 182 | `2861` | Providence 2861 | 1,358 | 0.276045 | 323,051 | 65.667713 | P |
| 183 | `1708` | Lincoln 1708 | 1,354 | 0.275232 | 324,405 | 65.942945 | P |
| 184 | `1604` | Johnston 1604 | 1,347 | 0.273809 | 325,752 | 66.216755 | P |
| 185 | `0806` | Cumberland 0806 | 1,339 | 0.272183 | 327,091 | 66.488938 | P |
| 186 | `1602` | Johnston 1602 | 1,338 | 0.271980 | 328,429 | 66.760918 | P |
| 187 | `1012` | East Providence 1012 | 1,332 | 0.270760 | 329,761 | 67.031678 | P |
| 188 | `1303` | Glocester 1303 | 1,325 | 0.269337 | 331,086 | 67.301016 | P |
| 189 | `3515` | Warwick 3515 | 1,318 | 0.267914 | 332,404 | 67.568930 | P |
| 190 | `1603` | Johnston 1603 | 1,314 | 0.267101 | 333,718 | 67.836031 | P |
| 191 | `3513` | Warwick 3513 | 1,307 | 0.265678 | 335,025 | 68.101710 | P |
| 192 | `3801` | West Warwick 3801 | 1,304 | 0.265069 | 336,329 | 68.366779 | P |
| 193 | `0305` | Burrillville 0305 | 1,300 | 0.264256 | 337,629 | 68.631034 | P |
| 194 | `0501` | Charlestown 0501 | 1,295 | 0.263239 | 338,924 | 68.894273 | P |
| 195 | `2413` | North Providence 2413 | 1,284 | 0.261003 | 340,208 | 69.155277 | P |
| 196 | `3909` | Woonsocket 3909 | 1,280 | 0.260190 | 341,488 | 69.415467 | P |
| 197 | `2705` | Portsmouth 2705 | 1,273 | 0.258767 | 342,761 | 69.674234 | P |
| 198 | `2606` | Pawtucket 2606 | 1,272 | 0.258564 | 344,033 | 69.932798 | P |
| 199 | `2304` | North Kingstown 2304 | 1,267 | 0.257548 | 345,300 | 70.190345 | P |
| 200 | `2101` | Newport 2101 | 1,256 | 0.255312 | 346,556 | 70.445657 | P |
| 201 | `2627` | Pawtucket 2627 | 1,253 | 0.254702 | 347,809 | 70.700359 | P |
| 202 | `1009` | East Providence 1009 | 1,245 | 0.253076 | 349,054 | 70.953434 | P |
| 203 | `3503` | Warwick 3503 | 1,242 | 0.252466 | 350,296 | 71.205900 | P |
| 204 | `3810` | West Warwick 3810 | 1,236 | 0.251246 | 351,532 | 71.457146 | P |
| 205 | `1612` | Johnston 1612 | 1,216 | 0.247181 | 352,748 | 71.704326 | P |
| 206 | `0716` | Cranston 0716 | 1,214 | 0.246774 | 353,962 | 71.951101 | P |
| 207 | `3912` | Woonsocket 3912 | 1,191 | 0.242099 | 355,153 | 72.193199 | P |
| 208 | `1702` | Lincoln 1702 | 1,190 | 0.241895 | 356,343 | 72.435095 | P |
| 209 | `1004` | East Providence 1004 | 1,185 | 0.240879 | 357,528 | 72.675974 | P |
| 210 | `0702` | Cranston 0702 | 1,179 | 0.239659 | 358,707 | 72.915633 | P |
| 211 | `1005` | East Providence 1005 | 1,179 | 0.239659 | 359,886 | 73.155293 | P |
| 212 | `3210` | South Kingstown 3210 | 1,177 | 0.239253 | 361,063 | 73.394546 | P |
| 213 | `0717` | Cranston 0717 | 1,176 | 0.239050 | 362,239 | 73.633595 | P |
| 214 | `3530` | Warwick 3530 | 1,174 | 0.238643 | 363,413 | 73.872239 | P |
| 215 | `2602` | Pawtucket 2602 | 1,170 | 0.237830 | 364,583 | 74.110069 | P |
| 216 | `1102` | Exeter 1102 | 1,165 | 0.236814 | 365,748 | 74.346882 | P |
| 217 | `3307` | Tiverton 3307 | 1,160 | 0.235797 | 366,908 | 74.582679 | P |
| 218 | `2806` | Providence 2806 | 1,155 | 0.234781 | 368,063 | 74.817460 | P |
| 219 | `1202` | Foster 1202 | 1,147 | 0.233155 | 369,210 | 75.050615 | P |
| 220 | `2406` | North Providence 2406 | 1,144 | 0.232545 | 370,354 | 75.283160 | P |
| 221 | `2857` | Providence 2857 | 1,143 | 0.232342 | 371,497 | 75.515502 | P |
| 222 | `2856` | Providence 2856 | 1,126 | 0.228886 | 372,623 | 75.744388 | P |
| 223 | `3527` | Warwick 3527 | 1,124 | 0.228479 | 373,747 | 75.972867 | P |
| 224 | `1013` | East Providence 1013 | 1,116 | 0.226853 | 374,863 | 76.199720 | P |
| 225 | `2622` | Pawtucket 2622 | 1,115 | 0.226650 | 375,978 | 76.426370 | P |
| 226 | `1703` | Lincoln 1703 | 1,102 | 0.224007 | 377,080 | 76.650378 | P |
| 227 | `2822` | Providence 2822 | 1,101 | 0.223804 | 378,181 | 76.874182 | P |
| 228 | `0504` | Charlestown 0504 | 1,100 | 0.223601 | 379,281 | 77.097783 | P |
| 229 | `0606` | Coventry 0606 | 1,093 | 0.222178 | 380,374 | 77.319961 | P |
| 230 | `0304` | Burrillville 0304 | 1,086 | 0.220755 | 381,460 | 77.540716 | P |
| 231 | `2306` | North Kingstown 2306 | 1,086 | 0.220755 | 382,546 | 77.761471 | P |
| 232 | `0603` | Coventry 0603 | 1,084 | 0.220348 | 383,630 | 77.981819 | P |
| 233 | `3403` | Warren 3403 | 1,083 | 0.220145 | 384,713 | 78.201964 | P |
| 234 | `2863` | Providence 2863 | 1,074 | 0.218316 | 385,787 | 78.420280 | P |
| 235 | `2625` | Pawtucket 2625 | 1,073 | 0.218112 | 386,860 | 78.638393 | P |
| 236 | `3908` | Woonsocket 3908 | 1,055 | 0.214454 | 387,915 | 78.852846 | P |
| 237 | `3402` | Warren 3402 | 1,047 | 0.212827 | 388,962 | 79.065674 | P |
| 238 | `0105` | Barrington 0105 | 1,041 | 0.211608 | 390,003 | 79.277281 | P |
| 239 | `3904` | Woonsocket 3904 | 1,032 | 0.209778 | 391,035 | 79.487060 | P |
| 240 | `3802` | West Warwick 3802 | 1,020 | 0.207339 | 392,055 | 79.694399 | P |
| 241 | `0201` | Bristol 0201 | 1,011 | 0.205510 | 393,066 | 79.899908 | P |
| 242 | `0804` | Cumberland 0804 | 1,006 | 0.204493 | 394,072 | 80.104401 | P |
| 243 | `0703` | Cranston 0703 | 1,003 | 0.203883 | 395,075 | 80.308285 | R |
| 244 | `0203` | Bristol 0203 | 1,002 | 0.203680 | 396,077 | 80.511965 | R |
| 245 | `2829` | Providence 2829 | 997 | 0.202664 | 397,074 | 80.714628 | R |
| 246 | `0715` | Cranston 0715 | 994 | 0.202054 | 398,068 | 80.916682 | R |
| 247 | `2704` | Portsmouth 2704 | 986 | 0.200428 | 399,054 | 81.117110 | R |
| 248 | `0811` | Cumberland 0811 | 985 | 0.200224 | 400,039 | 81.317334 | R |
| 249 | `2877` | Providence 2877 | 982 | 0.199615 | 401,021 | 81.516949 | R |
| 250 | `3906` | Woonsocket 3906 | 980 | 0.199208 | 402,001 | 81.716157 | R |
| 251 | `1601` | Johnston 1601 | 978 | 0.198801 | 402,979 | 81.914958 | R |
| 252 | `3303` | Tiverton 3303 | 967 | 0.196565 | 403,946 | 82.111524 | R |
| 253 | `2828` | Providence 2828 | 964 | 0.195956 | 404,910 | 82.307480 | R |
| 254 | `3805` | West Warwick 3805 | 963 | 0.195752 | 405,873 | 82.503232 | R |
| 255 | `2604` | Pawtucket 2604 | 958 | 0.194736 | 406,831 | 82.697968 | R |
| 256 | `0204` | Bristol 0204 | 946 | 0.192297 | 407,777 | 82.890265 | R |
| 257 | `2855` | Providence 2855 | 936 | 0.190264 | 408,713 | 83.080529 | R |
| 258 | `2410` | North Providence 2410 | 930 | 0.189044 | 409,643 | 83.269573 | R |
| 259 | `3601` | Westerly 3601 | 925 | 0.188028 | 410,568 | 83.457601 | R |
| 260 | `1304` | Glocester 1304 | 921 | 0.187215 | 411,489 | 83.644816 | R |
| 261 | `2870` | Providence 2870 | 916 | 0.186199 | 412,405 | 83.831015 | R |
| 262 | `0726` | Cranston 0726 | 912 | 0.185385 | 413,317 | 84.016400 | R |
| 263 | `3905` | Woonsocket 3905 | 904 | 0.183759 | 414,221 | 84.200159 | R |
| 264 | `3304` | Tiverton 3304 | 897 | 0.182336 | 415,118 | 84.382496 | R |
| 265 | `2810` | Providence 2810 | 884 | 0.179694 | 416,002 | 84.562189 | R |
| 266 | `2801` | Providence 2801 | 881 | 0.179084 | 416,883 | 84.741273 | R |
| 267 | `2867` | Providence 2867 | 877 | 0.178271 | 417,760 | 84.919544 | R |
| 268 | `2107` | Newport 2107 | 876 | 0.178068 | 418,636 | 85.097612 | R |
| 269 | `2805` | Providence 2805 | 875 | 0.177864 | 419,511 | 85.275476 | R |
| 270 | `2603` | Pawtucket 2603 | 874 | 0.177661 | 420,385 | 85.453137 | R |
| 271 | `2827` | Providence 2827 | 872 | 0.177255 | 421,257 | 85.630392 | R |
| 272 | `0613` | Coventry 0613 | 867 | 0.176238 | 422,124 | 85.806630 | R |
| 273 | `2831` | Providence 2831 | 866 | 0.176035 | 422,990 | 85.982665 | R |
| 274 | `2878` | Providence 2878 | 865 | 0.175832 | 423,855 | 86.158496 | R |
| 275 | `2811` | Providence 2811 | 863 | 0.175425 | 424,718 | 86.333921 | R |
| 276 | `0607` | Coventry 0607 | 859 | 0.174612 | 425,577 | 86.508533 | R |
| 277 | `1101` | Exeter 1101 | 858 | 0.174409 | 426,435 | 86.682942 | R |
| 278 | `2201` | New Shoreham 2201 | 856 | 0.174002 | 427,291 | 86.856944 | R |
| 279 | `2409` | North Providence 2409 | 848 | 0.172376 | 428,139 | 87.029320 | R |
| 280 | `2854` | Providence 2854 | 848 | 0.172376 | 428,987 | 87.201696 | R |
| 281 | `3529` | Warwick 3529 | 840 | 0.170750 | 429,827 | 87.372446 | R |
| 282 | `3519` | Warwick 3519 | 825 | 0.167701 | 430,652 | 87.540147 | R |
| 283 | `3806` | West Warwick 3806 | 818 | 0.166278 | 431,470 | 87.706424 | R |
| 284 | `3306` | Tiverton 3306 | 808 | 0.164245 | 432,278 | 87.870669 | R |
| 285 | `2832` | Providence 2832 | 798 | 0.162212 | 433,076 | 88.032882 | R |
| 286 | `2802` | Providence 2802 | 797 | 0.162009 | 433,873 | 88.194891 | R |
| 287 | `2628` | Pawtucket 2628 | 794 | 0.161399 | 434,667 | 88.356290 | R |
| 288 | `1403` | Hopkinton 1403 | 792 | 0.160993 | 435,459 | 88.517282 | R |
| 289 | `3702` | West Greenwich 3702 | 791 | 0.160789 | 436,250 | 88.678072 | R |
| 290 | `2405` | North Providence 2405 | 782 | 0.158960 | 437,032 | 88.837032 | R |
| 291 | `1003` | East Providence 1003 | 770 | 0.156521 | 437,802 | 88.993552 | R |
| 292 | `2839` | Providence 2839 | 770 | 0.156521 | 438,572 | 89.150073 | R |
| 293 | `1709` | Lincoln 1709 | 767 | 0.155911 | 439,339 | 89.305984 | R |
| 294 | `3703` | West Greenwich 3703 | 764 | 0.155301 | 440,103 | 89.461285 | R |
| 295 | `2614` | Pawtucket 2614 | 763 | 0.155098 | 440,866 | 89.616382 | R |
| 296 | `3517` | Warwick 3517 | 762 | 0.154894 | 441,628 | 89.771277 | R |
| 297 | `3704` | West Greenwich 3704 | 761 | 0.154691 | 442,389 | 89.925968 | R |
| 298 | `3202` | South Kingstown 3202 | 751 | 0.152658 | 443,140 | 90.078626 | R |
| 299 | `3506` | Warwick 3506 | 747 | 0.151845 | 443,887 | 90.230472 | R |
| 300 | `3501` | Warwick 3501 | 746 | 0.151642 | 444,633 | 90.382114 | R |
| 301 | `3201` | South Kingstown 3201 | 741 | 0.150626 | 445,374 | 90.532739 | R |
| 302 | `0615` | Coventry 0615 | 737 | 0.149813 | 446,111 | 90.682552 | R |
| 303 | `0903` | East Greenwich 0903 | 736 | 0.149609 | 446,847 | 90.832161 | R |
| 304 | `2865` | Providence 2865 | 735 | 0.149406 | 447,582 | 90.981567 | R |
| 305 | `1010` | East Providence 1010 | 719 | 0.146154 | 448,301 | 91.127721 | R |
| 306 | `2853` | Providence 2853 | 716 | 0.145544 | 449,017 | 91.273265 | R |
| 307 | `3520` | Warwick 3520 | 701 | 0.142495 | 449,718 | 91.415759 | R |
| 308 | `3533` | Warwick 3533 | 696 | 0.141478 | 450,414 | 91.557238 | R |
| 309 | `0401` | Central Falls 0401 | 691 | 0.140462 | 451,105 | 91.697700 | R |
| 310 | `2404` | North Providence 2404 | 684 | 0.139039 | 451,789 | 91.836739 | R |
| 311 | `3532` | Warwick 3532 | 684 | 0.139039 | 452,473 | 91.975778 | R |
| 312 | `3902` | Woonsocket 3902 | 671 | 0.136397 | 453,144 | 92.112174 | R |
| 313 | `2505` | North Smithfield 2505 | 666 | 0.135380 | 453,810 | 92.247555 | R |
| 314 | `1015` | East Providence 1015 | 660 | 0.134161 | 454,470 | 92.381715 | R |
| 315 | `1611` | Johnston 1611 | 653 | 0.132738 | 455,123 | 92.514453 | R |
| 316 | `1711` | Lincoln 1711 | 647 | 0.131518 | 455,770 | 92.645971 | R |
| 317 | `2823` | Providence 2823 | 630 | 0.128062 | 456,400 | 92.774033 | R |
| 318 | `0608` | Coventry 0608 | 620 | 0.126030 | 457,020 | 92.900063 | R |
| 319 | `0814` | Cumberland 0814 | 618 | 0.125623 | 457,638 | 93.025686 | R |
| 320 | `0614` | Coventry 0614 | 615 | 0.125013 | 458,253 | 93.150699 | R |
| 321 | `3803` | West Warwick 3803 | 615 | 0.125013 | 458,868 | 93.275712 | R |
| 322 | `2850` | Providence 2850 | 614 | 0.124810 | 459,482 | 93.400522 | R |
| 323 | `3534` | Warwick 3534 | 611 | 0.124200 | 460,093 | 93.524722 | R |
| 324 | `1710` | Lincoln 1710 | 607 | 0.123387 | 460,700 | 93.648109 | R |
| 325 | `3511` | Warwick 3511 | 596 | 0.121151 | 461,296 | 93.769260 | R |
| 326 | `0403` | Central Falls 0403 | 579 | 0.117695 | 461,875 | 93.886956 | R |
| 327 | `2849` | Providence 2849 | 579 | 0.117695 | 462,454 | 94.004651 | R |
| 328 | `0710` | Cranston 0710 | 577 | 0.117289 | 463,031 | 94.121940 | R |
| 329 | `2845` | Providence 2845 | 573 | 0.116476 | 463,604 | 94.238415 | R |
| 330 | `1701` | Lincoln 1701 | 560 | 0.113833 | 464,164 | 94.352249 | R |
| 331 | `2809` | Providence 2809 | 555 | 0.112817 | 464,719 | 94.465065 | R |
| 332 | `3903` | Woonsocket 3903 | 555 | 0.112817 | 465,274 | 94.577882 | R |
| 333 | `2803` | Providence 2803 | 549 | 0.111597 | 465,823 | 94.689479 | R |
| 334 | `2836` | Providence 2836 | 546 | 0.110987 | 466,369 | 94.800467 | R |
| 335 | `2504` | North Smithfield 2504 | 544 | 0.110581 | 466,913 | 94.911048 | R |
| 336 | `2616` | Pawtucket 2616 | 544 | 0.110581 | 467,457 | 95.021628 | R |
| 337 | `1606` | Johnston 1606 | 542 | 0.110174 | 467,999 | 95.131803 | R |
| 338 | `2834` | Providence 2834 | 532 | 0.108142 | 468,531 | 95.239944 | R |
| 339 | `2879` | Providence 2879 | 528 | 0.107328 | 469,059 | 95.347272 | R |
| 340 | `9002` | Federal Precinct #2 | 526 | 0.106922 | 469,585 | 95.454194 | R |
| 341 | `2874` | Providence 2874 | 522 | 0.106109 | 470,107 | 95.560303 | R |
| 342 | `0402` | Central Falls 0402 | 519 | 0.105499 | 470,626 | 95.665802 | R |
| 343 | `2105` | Newport 2105 | 518 | 0.105296 | 471,144 | 95.771098 | R |
| 344 | `2835` | Providence 2835 | 499 | 0.101433 | 471,643 | 95.872531 | R |
| 345 | `2612` | Pawtucket 2612 | 495 | 0.100620 | 472,138 | 95.973152 | R |
| 346 | `2869` | Providence 2869 | 494 | 0.100417 | 472,632 | 96.073569 | R |
| 347 | `2408` | North Providence 2408 | 492 | 0.100011 | 473,124 | 96.173579 | R |
| 348 | `9001` | Federal Precinct #1 | 487 | 0.098994 | 473,611 | 96.272574 | R |
| 349 | `2860` | Providence 2860 | 470 | 0.095539 | 474,081 | 96.368112 | R |
| 350 | `2617` | Pawtucket 2617 | 463 | 0.094116 | 474,544 | 96.462228 | R |
| 351 | `0612` | Coventry 0612 | 462 | 0.093912 | 475,006 | 96.556140 | R |
| 352 | `1305` | Glocester 1305 | 453 | 0.092083 | 475,459 | 96.648223 | R |
| 353 | `2881` | Providence 2881 | 451 | 0.091676 | 475,910 | 96.739899 | R |
| 354 | `0720` | Cranston 0720 | 442 | 0.089847 | 476,352 | 96.829746 | R |
| 355 | `2626` | Pawtucket 2626 | 439 | 0.089237 | 476,791 | 96.918983 | R |
| 356 | `0813` | Cumberland 0813 | 437 | 0.088831 | 477,228 | 97.007814 | R |
| 357 | `1707` | Lincoln 1707 | 431 | 0.087611 | 477,659 | 97.095425 | R |
| 358 | `2880` | Providence 2880 | 408 | 0.082936 | 478,067 | 97.178360 | R |
| 359 | `2610` | Pawtucket 2610 | 397 | 0.080700 | 478,464 | 97.259060 | R |
| 360 | `0601` | Coventry 0601 | 393 | 0.079886 | 478,857 | 97.338946 | R |
| 361 | `2840` | Providence 2840 | 385 | 0.078260 | 479,242 | 97.417207 | R |
| 362 | `3510` | Warwick 3510 | 385 | 0.078260 | 479,627 | 97.495467 | R |
| 363 | `2104` | Newport 2104 | 382 | 0.077650 | 480,009 | 97.573117 | R |
| 364 | `0405` | Central Falls 0405 | 378 | 0.076837 | 480,387 | 97.649955 | R |
| 365 | `9011` | Federal Precinct #1S | 378 | 0.076837 | 480,765 | 97.726792 | R |
| 366 | `3512` | Warwick 3512 | 374 | 0.076024 | 481,139 | 97.802817 | R |
| 367 | `2848` | Providence 2848 | 364 | 0.073992 | 481,503 | 97.876808 | R |
| 368 | `0406` | Central Falls 0406 | 358 | 0.072772 | 481,861 | 97.949580 | R |
| 369 | `2615` | Pawtucket 2615 | 353 | 0.071756 | 482,214 | 98.021336 | R |
| 370 | `2826` | Providence 2826 | 344 | 0.069926 | 482,558 | 98.091262 | R |
| 371 | `3508` | Warwick 3508 | 342 | 0.069520 | 482,900 | 98.160781 | R |
| 372 | `2858` | Providence 2858 | 336 | 0.068300 | 483,236 | 98.229081 | R |
| 373 | `0407` | Central Falls 0407 | 333 | 0.067690 | 483,569 | 98.296771 | R |
| 374 | `2852` | Providence 2852 | 328 | 0.066674 | 483,897 | 98.363445 | R |
| 375 | `2608` | Pawtucket 2608 | 312 | 0.063421 | 484,209 | 98.426866 | R |
| 376 | `2103` | Newport 2103 | 307 | 0.062405 | 484,516 | 98.489271 | R |
| 377 | `2821` | Providence 2821 | 304 | 0.061795 | 484,820 | 98.551066 | R |
| 378 | `2618` | Pawtucket 2618 | 295 | 0.059966 | 485,115 | 98.611032 | R |
| 379 | `2837` | Providence 2837 | 295 | 0.059966 | 485,410 | 98.670998 | R |
| 380 | `0404` | Central Falls 0404 | 286 | 0.058136 | 485,696 | 98.729134 | R |
| 381 | `2815` | Providence 2815 | 284 | 0.057730 | 485,980 | 98.786864 | R |
| 382 | `2833` | Providence 2833 | 277 | 0.056307 | 486,257 | 98.843170 | R |
| 383 | `0605` | Coventry 0605 | 270 | 0.054884 | 486,527 | 98.898054 | R |
| 384 | `2621` | Pawtucket 2621 | 268 | 0.054477 | 486,795 | 98.952532 | R |
| 385 | `2807` | Providence 2807 | 244 | 0.049599 | 487,039 | 99.002130 | R |
| 386 | `2824` | Providence 2824 | 244 | 0.049599 | 487,283 | 99.051729 | R |
| 387 | `2859` | Providence 2859 | 236 | 0.047973 | 487,519 | 99.099702 | R |
| 388 | `0809` | Cumberland 0809 | 231 | 0.046956 | 487,750 | 99.146658 | R |
| 389 | `2851` | Providence 2851 | 229 | 0.046550 | 487,979 | 99.193207 | R |
| 390 | `2872` | Providence 2872 | 223 | 0.045330 | 488,202 | 99.238537 | R |
| 391 | `2623` | Pawtucket 2623 | 206 | 0.041874 | 488,408 | 99.280412 | R |
| 392 | `2607` | Pawtucket 2607 | 196 | 0.039842 | 488,604 | 99.320253 | R |
| 393 | `2876` | Providence 2876 | 187 | 0.038012 | 488,791 | 99.358266 | R |
| 394 | `0719` | Cranston 0719 | 180 | 0.036589 | 488,971 | 99.394855 | R |
| 395 | `2825` | Providence 2825 | 168 | 0.034150 | 489,139 | 99.429005 | R |
| 396 | `3901` | Woonsocket 3901 | 161 | 0.032727 | 489,300 | 99.461732 | R |
| 397 | `2624` | Pawtucket 2624 | 160 | 0.032524 | 489,460 | 99.494255 | R |
| 398 | `2844` | Providence 2844 | 160 | 0.032524 | 489,620 | 99.526779 | R |
| 399 | `2842` | Providence 2842 | 157 | 0.031914 | 489,777 | 99.558693 | R |
| 400 | `2816` | Providence 2816 | 149 | 0.030288 | 489,926 | 99.588981 | R |
| 401 | `2875` | Providence 2875 | 149 | 0.030288 | 490,075 | 99.619269 | R |
| 402 | `2812` | Providence 2812 | 140 | 0.028458 | 490,215 | 99.647727 | R |
| 403 | `2847` | Providence 2847 | 138 | 0.028052 | 490,353 | 99.675779 | R |
| 404 | `2868` | Providence 2868 | 132 | 0.026832 | 490,485 | 99.702611 | R |
| 405 | `2609` | Pawtucket 2609 | 131 | 0.026629 | 490,616 | 99.729240 | R |
| 406 | `2871` | Providence 2871 | 129 | 0.026222 | 490,745 | 99.755462 | R |
| 407 | `2808` | Providence 2808 | 128 | 0.026019 | 490,873 | 99.781481 | R |
| 408 | `2701` | Portsmouth 2701 | 120 | 0.024393 | 490,993 | 99.805874 | R |
| 409 | `2873` | Providence 2873 | 119 | 0.024190 | 491,112 | 99.830063 | R |
| 410 | `2843` | Providence 2843 | 99 | 0.020124 | 491,211 | 99.850187 | R |
| 411 | `1006` | East Providence 1006 | 96 | 0.019514 | 491,307 | 99.869702 | R |
| 412 | `2846` | Providence 2846 | 95 | 0.019311 | 491,402 | 99.889013 | R |
| 413 | `2864` | Providence 2864 | 94 | 0.019108 | 491,496 | 99.908120 | R |
| 414 | `2866` | Providence 2866 | 85 | 0.017278 | 491,581 | 99.925399 | R |
| 415 | `2882` | Providence 2882 | 82 | 0.016668 | 491,663 | 99.942067 | R |
| 416 | `9012` | Federal Precinct #2S | 82 | 0.016668 | 491,745 | 99.958735 | R |
| 417 | `2841` | Providence 2841 | 49 | 0.009960 | 491,794 | 99.968696 | R |
| 418 | `2838` | Providence 2838 | 43 | 0.008741 | 491,837 | 99.977437 | R |
| 419 | `0728` | Cranston Limited | 12 | 0.002439 | 491,849 | 99.979876 | R |
| 420 | `0209` | Bristol Limited | 9 | 0.001829 | 491,858 | 99.981705 | R |
| 421 | `0815` | Cumberland Limited | 9 | 0.001829 | 491,867 | 99.983535 | R |
| 422 | `2629` | Pawtucket Limited | 9 | 0.001829 | 491,876 | 99.985364 | R |
| 423 | `2414` | North Providence Limited | 7 | 0.001423 | 491,883 | 99.986787 | R |
| 424 | `2708` | Portsmouth Limited | 7 | 0.001423 | 491,890 | 99.988210 | R |
| 425 | `2884` | Providence Limited 2 | 7 | 0.001423 | 491,897 | 99.989633 | R |
| 426 | `3212` | South Kingstown Limited | 7 | 0.001423 | 491,904 | 99.991056 | R |
| 427 | `2311` | North Kingstown Limited | 5 | 0.001016 | 491,909 | 99.992072 | R |
| 428 | `3535` | Warwick Limited | 5 | 0.001016 | 491,914 | 99.993089 | R |
| 429 | `2005` | Narragansett Limited | 4 | 0.000813 | 491,918 | 99.993902 | R |
| 430 | `2110` | Newport Limited | 4 | 0.000813 | 491,922 | 99.994715 | R |
| 431 | `1018` | East Providence Limited | 3 | 0.000610 | 491,925 | 99.995325 | R |
| 432 | `1906` | Middletown Limited | 3 | 0.000610 | 491,928 | 99.995935 | R |
| 433 | `2506` | North Smithfield Limited | 3 | 0.000610 | 491,931 | 99.996544 | R |
| 434 | `3705` | West Greenwich Limited | 3 | 0.000610 | 491,934 | 99.997154 | R |
| 435 | `0408` | Central Falls Limited | 2 | 0.000407 | 491,936 | 99.997561 | R |
| 436 | `0906` | East Greenwich Limited | 2 | 0.000407 | 491,938 | 99.997967 | R |
| 437 | `1503` | Jamestown Limited | 2 | 0.000407 | 491,940 | 99.998374 | R |
| 438 | `1712` | Lincoln Limited | 2 | 0.000407 | 491,942 | 99.998780 | R |
| 439 | `3608` | Westerly Limited | 2 | 0.000407 | 491,944 | 99.999187 | R |
| 440 | `0107` | Barrington Limited | 1 | 0.000203 | 491,945 | 99.999390 | R |
| 441 | `0307` | Burrillville Limited | 1 | 0.000203 | 491,946 | 99.999593 | R |
| 442 | `1306` | Glocester Limited | 1 | 0.000203 | 491,947 | 99.999797 | R |
| 443 | `3107` | Smithfield Limited | 1 | 0.000203 | 491,948 | 100.000000 | R |
| 444 | `0505` | Charlestown Limited | 0 | 0.000000 | 491,948 | 100.000000 | R |
| 445 | `0618` | Coventry Limited | 0 | 0.000000 | 491,948 | 100.000000 | R |
| 446 | `1104` | Exeter Limited | 0 | 0.000000 | 491,948 | 100.000000 | R |
| 447 | `1203` | Foster Limited | 0 | 0.000000 | 491,948 | 100.000000 | R |
| 448 | `1404` | Hopkinton Limited | 0 | 0.000000 | 491,948 | 100.000000 | R |
| 449 | `1613` | Johnston Limited | 0 | 0.000000 | 491,948 | 100.000000 | R |
| 450 | `1802` | Little Compton Limited | 0 | 0.000000 | 491,948 | 100.000000 | R |
| 451 | `2202` | New Shoreham Limited | 0 | 0.000000 | 491,948 | 100.000000 | R |
| 452 | `2883` | Providence Limited 1 | 0 | 0.000000 | 491,948 | 100.000000 | R |
| 453 | `2904` | Richmond Limited | 0 | 0.000000 | 491,948 | 100.000000 | R |
| 454 | `3004` | Scituate Limited | 0 | 0.000000 | 491,948 | 100.000000 | R |
| 455 | `3308` | Tiverton Limited | 0 | 0.000000 | 491,948 | 100.000000 | R |
| 456 | `3405` | Warren Limited | 0 | 0.000000 | 491,948 | 100.000000 | R |
| 457 | `3811` | West Warwick Limited | 0 | 0.000000 | 491,948 | 100.000000 | R |
| 458 | `3913` | Woonsocket Limited | 0 | 0.000000 | 491,948 | 100.000000 | R |

## Reproduction, offline QA and review status

Run `python3 -B senate/2026/rhode-island/data/turnout/rebuild.py` from the repository root to reproduce acquisition-independent extracts, reconciliation, CSV and report. Then run `python3 -B senate/2026/rhode-island/data/turnout/validate_turnout.py` for read-only verification. No network, mutable shared-manifest selection, peer-directory glob, dependency install or cache is required. Python standard library and Poppler `pdftotext` are used. Original raw ZIP/PDF objects are reused once through exact-hash references; the full unused content remains available without extracting an unrelated-office assignment. See [schema](data/turnout/source/SCHEMA.md).

[Validation](data/turnout/validation.json) records full primary state/candidate/method/native/parent closure, source positions, null/administrative coverage, native ordering and integer minimum crossing, and intentional corruption cases. [Repair history](data/turnout/history/repair-history.json) records the initial PDF decimal parsing failure and the steering that separated parent sensitivity from native dispatch. [Original-first body witness](data/turnout/qa/pre-peer-body-witness.json) freezes exact full bodies (including report/scripts/CSV/full source objects by immutable references), with byte-exact reconstruction. [Final seal](data/turnout/final-seal.json) precedes the [complete owned asset manifest](data/turnout/asset-manifest.json); the manifest excludes only itself. The original227-body witness remains unchanged and is validated against reconstructed historical bodies. The repaired package adds [bounded source-core comparison](data/turnout/reciprocal/source-core-comparison.json), [finished peer235-body capture](data/turnout/reciprocal/peer-finished-capture/capture.json), [row5/corruption/protected-body QA](data/turnout/qa/repair-validation.json), and a [complete repaired-body witness](data/turnout/qa/repaired-body-witness.json). Both sides' five full native/parent orders and integer thresholds are independently recomputed from their own source counts. Eleven child-label whitespace differences and exact percentage-token/administrative-key representation differences survive explicitly. Peer reverse proof is captured as historical original-phase evidence only; peer writers/calculators/scenarios/reproduction/outcomes/later final bytes are not claimed equal. A final read-only full membership/hash/size/witness/hierarchy audit follows sealing, with no subsequent owned writes. No reverse current-manifest pin or digest cycle is used.

**Pending external review:** actual peer `5d9f9b63-0cf2-4b55-b52b-579cbc1d76d1` has completed. Bounded original-first source-core reciprocal agreement is complete against the exact captured finished baseline pins. Coordinator acceptance/publication remain pending. The unchanged priority contract's pending-agreement metadata is preserved as original-phase historical dispatch metadata; the scoped current agreement is the separate comparison proof, not broader peer model approval. This bounded repair/review turn ends after offline QA and complete acyclic sealing. Legal write-in eligibility, exhaustive later certification/amendment history, current native identities/geometry, November feed availability/cadence and remaining-vote/probability claims remain qualified as described above.
