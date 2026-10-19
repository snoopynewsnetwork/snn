# Idaho historical partisanship and conditional winning paths

Research observation: **2026-10-19**. This package covers all **44 counties**, all **985 native 2024 presidential contexts**, 974 native rows each for 2020 Senate/president, and 999 each for 2022 Senate/governor. It supplies reproducible historical counts and conditional arithmetic. Historical turnout anchors are not 2026 projections. No live collector, measured outstanding pool, calibrated probability, current precinct join, or accepted November reporting universe is supplied.

The primary recent comparison is **2024 president**, since Idaho had **no 2024 U.S. Senate election**. Harris received **274,972** and Trump **605,246**; the other nine named candidates/write-ins received **24,839**, giving **905,057 valid named candidate votes**. At the observed Harris–Trump pair volume of **880,218**, the county-weighted tie requires **+18.760921 percentage points of A share**. An illustrative A+1 pair margin needs **+19.260921 share points**, yielding **8,802.18 net votes**, or **0.972555 points of the all-candidate denominator**. The bounded native-unit solution differs because five unit shares clip at 100%: **+18.778064** for a tie and **+19.281419** for A+1. These are conditional combinations, not necessary individual-county targets. [Official 2024 canvass, president pp.4–29](https://archive.sos.idaho.gov/elections/data/results/2024/2024_general_canvass.pdf), [original all-races workbook](https://archive.sos.idaho.gov/elections/data/results/2024/raw_races_general.xlsx).

## Election scope, ballot and legal threshold

The 2026 regular election is November 3 for the **Class II** seat held by Risch. The November 3, 2020 Risch–Jordan election is the same seat. The November 8, 2022 Crapo–Roth election is **Class III**, the other seat and an actual midterm. Governor is an additional 2022 comparison; the 2020 presidential field is separate. These electorates and candidate effects are not interchangeable. [Senate Class II](https://www.senate.gov/senators/Class_II.htm), [Class III](https://www.senate.gov/senators/Class_III.htm), [SOS historical archive](https://voteidaho.gov/election-results/), [2026 official calendar](https://archive.voteidaho.gov/download/2026-election-calendar.pdf).

Idaho elects the federal candidate with the highest vote count. A state/federal general-election tie is resolved by coin toss after canvass, not by declaring the arithmetic tie a win. This contest uses plurality, without a ranked-choice or runoff stage. Pair A+1 is illustrative and cannot replace the full-field plurality test. [Idaho Code 34-1215](https://legislature.idaho.gov/statutesrules/idstat/Title34/T34CH12/SECT34-1215/), [34-1216](https://legislature.idaho.gov/statutesrules/idstat/Title34/T34CH12/SECT34-1216/); complete directly retrieved statute responses and extracts are in [the acquisition ledger](data/baselines/source/acquisition.json).

The actual SOS → Twin Falls → Election Information → Sample Ballots chain leads to a published **November 3, 2026 LD24 sample ballot**. I independently decompressed the hash-verified complete original, extracted its text, rendered and viewed the whole first page. It prints **Todd Achilles (IND), Natalie M Fleming (IND), Matt Loesby (LIB), Jim Risch (REP)**. It prints no Senate write-in line. This bounded final-election sample is stronger than primary nominations or newsroom setup. It does **not** establish an exhaustive statewide signed certification, later eligible write-ins, current result-choice IDs, or geography. [Original printed sample](https://twinfallscounty.org/wp-content/uploads/LD24-Gen-Sample.pdf), [independent review](data/baselines/source/ballot-independent-review.json), [immutable original chain and receipts](data/news/coordinator-oct19-recheck/current-ballot-original-review.json).

Accordingly, the three **current-Achilles-Risch / current-Fleming-Risch / current-Loesby-Risch** scenario views use named opposition pairs separately. Their identical numerical starting points deliberately transport the historical Harris–Trump shares and pair participation as an **explicit hypothetical assumption**, not evidence of any current candidate's support. They hold the other two printed opposition candidates at half the residual candidate pool each, an arbitrary stated allocation. No current Democrat, Democratic coalition, candidate effect, lower preference, or transfer is inferred. Actual historical Fleming and Cleveland opposition pairs are additionally preserved with their own observed votes.

Poll hours are generally 8 a.m.–8 p.m. local time; county clerks may open at 7 a.m., and voters in line at 8 p.m. may vote. Idaho spans Mountain and Pacific zones. The federal boundary follows the Idaho–Lemhi county line to the Salmon River and then its main channel west to Oregon; municipalities on the boundary are assigned Mountain time by the regulation. Idaho County cannot safely receive one countywide timezone. On November 3, 2026, 8 p.m. MST is November 4 **03:00 UTC**, and 8 p.m. PST is **04:00 UTC**. These are closing-time conversions, not a publication-cadence promise. [34-1101](https://legislature.idaho.gov/statutesrules/idstat/Title34/T34CH11/SECT34-1101/), [current 49 CFR 71.9 web reading](https://www.ecfr.gov/current/title-49/subtitle-A/part-71/section-71.9), [retained official 2025 CFR PDF](https://www.govinfo.gov/content/pkg/CFR-2025-title49-vol1/pdf/CFR-2025-title49-vol1-sec71-9.pdf). Direct eCFR acquisition returned an HTTP200 challenge; that response is retained separately and is not the boundary authority.

The current SOS results index presents May 19 primary results. Historical displays, primary results and the pre-election KXLY zero/100% setup are not November returns or a final official ballot mapping. See the read-only [news evidence](local-news-results.md) and [proposed polling strategy](live-polling-strategy.md); no cadence is established here.

## Whole-state historical controls

Here A is the named historical Democrat and B the named Republican in each row. “Other” includes the entire remaining named field. Shares and margins in this table use **A+B**, not all candidate votes or ballots.

| Contest | A | B | Other | All candidate votes | A share % | A−B margin pp | Unclipped county tie shift pp |
|---|---|---|---|---|---|---|---|
| 2024-president | 274,972 | 605,246 | 24,839 | 905,057 | 31.239 | -37.522 | 18.760921 |
| 2020-senate-II | 285,864 | 538,446 | 35,517 | 859,827 | 34.679 | -30.642 | 15.320814 |
| 2022-senate-III | 169,808 | 358,539 | 62,543 | 590,890 | 32.139 | -35.721 | 17.860516 |
| 2022-governor | 120,160 | 358,598 | 113,866 | 592,624 | 25.098 | -49.803 | 24.901725 |
| 2020-president | 287,021 | 554,119 | 26,141 | 867,281 | 34.123 | -31.754 | 15.877143 |

All candidate totals below are independently summed from original source positions and reconciled to the 44 county controls and state controls. For 2020/2022, every known native sum and overlapping footer matches its separate county control; original nulls remain unknown in their individual cells. For 2024, the distinct canvass PDF agrees with all 985 native vectors and its 13-category statewide control, including the two explicitly documented apostrophe typography differences. [2020 original canvass ZIP](https://archive.sos.idaho.gov/elections/data/results/2020/2020_General_Canvass.zip), [2022 original canvass ZIP](https://archive.sos.idaho.gov/elections/data/results/2022/2022_General_Canvass.zip), [2024 PDF reconciliation](data/baselines/source/2024-pdf-reconciliation.json), [historical reconciliation](data/baselines/source/historical-reconciliation.json).

| Contest | Literal county candidate header | Raw party | Votes |
|---|---|---|---|
| 2024-president | Joel Skousen | Constitution | 1,577 |
| 2024-president | Kamala D. Harris | Democratic | 274,972 |
| 2024-president | Claudia De la Cruz | Independent | 1,230 |
| 2024-president | Jill Stein | Independent | 2,973 |
| 2024-president | Randall Terry | Independent | 1,026 |
| 2024-president | Robert F Kennedy Jr. | Independent | 12,812 |
| 2024-president | Shiva Ayyadurai | Independent | 514 |
| 2024-president | Chase Oliver | Libertarian | 4,462 |
| 2024-president | Donald J. Trump | Republican | 605,246 |
| 2024-president | Brian Larry Kienitz (Write-In) | Independent | 3 |
| 2024-president | Peter Sonski (Write-In) | Independent | 242 |
| 2020-senate-II | Natalie M Fleming | IND | 25,329 |
| 2020-senate-II | Paulette Jordan | DEM | 285,864 |
| 2020-senate-II | Jim Risch | REP | 538,446 |
| 2020-senate-II | Ray J. Writz | CON | 10,188 |
| 2022-senate-III | David Roth | DEM | 169,808 |
| 2022-senate-III | Mike Crapo | REP | 358,539 |
| 2022-senate-III | Ray J. Writz | CON | 8,500 |
| 2022-senate-III | Idaho Sierra Law | LIB | 4,126 |
| 2022-senate-III | Scott Oh Cleveland | IND | 49,917 |
| 2022-governor | Stephen Heidt | DEM | 120,160 |
| 2022-governor | Brad Little | REP | 358,598 |
| 2022-governor | Chantyrose Davison | CON | 5,250 |
| 2022-governor | Paul Sand | LIB | 6,714 |
| 2022-governor | Ammon Bundy | IND | 101,835 |
| 2022-governor | Lisa Marie (W/I) | IND | 67 |
| 2020-president | Joseph R. Biden | DEM | 287,021 |
| 2020-president | Don Blankenship | CON | 1,806 |
| 2020-president | Rocky "Rocky" De La Fuente | IND | 1,491 |
| 2020-president | Jo Jorgensen | LIB | 16,404 |
| 2020-president | Brock Pierce | IND | 2,808 |
| 2020-president | Donald J. Trump | REP | 554,119 |
| 2020-president | Kanye West | IND | 3,632 |

The 2024 named write-ins are Brian Larry Kienitz and Peter Sonski, **245 combined**, included once in 905,057. The workbook separately reports **1,215 overvotes** and **11,194 undervotes**; these are not valid candidate votes. The all-category 917,466 equals the House Clerk presidential total. The FEC valid total is 905,057, so their **12,409 difference exactly equals these noncandidate categories**. House Clerk aggregates independent/write-in identities; the native workbook preserves each name and its actual Idaho party label, including Skousen CON and Stein IND. No generic invalid-write-in or standalone blank-ballot category is supplied. [House Clerk 2024 statistics, Idaho p.21](https://clerk.house.gov/member_info/electionInfo/2024/statistics2024.pdf), [FEC 2024 president](https://www.fec.gov/documents/5644/2024presgeresults.pdf), [original references and complete PDF text](data/baselines/source/additional-reused-originals.json).

## Every county and native identity

County names, precinct labels and polling places are distinct. Native IDs here are **analytical source-position keys**. Literal numeric labels, leading zeros, named rows, central absentee/early/mail groups, and repeated labels remain source-bound. The statewide workbooks do not provide polling-place identities or approved 2026 geometry. Three separate 2020 Boise `90 Absentee` rows survive by source position. No cross-year precinct matching is inferred from names or counts. [Full native source records](data/baselines/source/native-units.json.gz), [all candidate source cells and control roles](data/baselines/source/candidate-positions.json.gz).

The table shows historical A−B **pair margin points**. Positive values favor the named Democrat in those historical contests, negative values the named Republican. The column names do not identify a current Democrat. Outcome labels describe each contest; close/mixed sensitivity can be read from absolute margin ≤5 pp or >5–10 pp, rather than treating counties as permanent party identities.

| County | Harris | Trump | Other 2024 | Pres24 margin | Sen20 margin | Sen22 margin | Gov22 margin | 2024 pair weight % | Net gain / +1pp share |
|---|---|---|---|---|---|---|---|---|---|
| Ada | 116,116 | 143,759 | 7,544 | -10.64 | -4.71 | -6.65 | -32.45 | 29.524 | 5,197.50 |
| Canyon | 25,669 | 72,755 | 2,606 | -47.84 | -37.89 | -47.65 | -57.59 | 11.182 | 1,968.48 |
| Kootenai | 22,113 | 72,059 | 2,193 | -53.04 | -45.52 | -51.71 | -60.92 | 10.699 | 1,883.44 |
| Bonneville | 14,458 | 40,053 | 1,925 | -46.95 | -44.79 | -51.51 | -64.40 | 6.193 | 1,090.22 |
| Bannock | 14,306 | 24,329 | 1,341 | -25.94 | -17.53 | -23.06 | -36.17 | 4.389 | 772.70 |
| Twin Falls | 9,064 | 27,304 | 1,015 | -50.15 | -42.71 | -51.46 | -60.40 | 4.132 | 727.36 |
| Bonner | 7,650 | 21,352 | 708 | -47.25 | -37.96 | -41.89 | -59.09 | 3.295 | 580.04 |
| Bingham | 3,878 | 16,188 | 585 | -61.35 | -54.50 | -68.86 | -74.53 | 2.280 | 401.32 |
| Latah | 9,039 | 10,669 | 753 | -8.27 | 4.39 | -4.20 | -24.16 | 2.239 | 394.16 |
| Nez Perce | 5,928 | 13,707 | 500 | -39.62 | -34.89 | -42.48 | -55.35 | 2.231 | 392.70 |
| Madison | 2,767 | 13,925 | 671 | -66.85 | -71.05 | -74.10 | -79.38 | 1.896 | 333.84 |
| Jefferson | 1,891 | 13,481 | 448 | -75.40 | -75.32 | -79.69 | -83.82 | 1.746 | 307.44 |
| Blaine | 8,424 | 4,281 | 384 | 32.61 | 34.81 | 31.61 | 12.29 | 1.443 | 254.10 |
| Payette | 2,064 | 9,458 | 239 | -64.17 | -57.24 | -67.24 | -74.16 | 1.309 | 230.44 |
| Elmore | 2,611 | 7,791 | 270 | -49.80 | -41.44 | -53.31 | -61.27 | 1.182 | 208.04 |
| Gem | 1,699 | 8,707 | 214 | -67.35 | -58.81 | -65.26 | -76.88 | 1.182 | 208.12 |
| Idaho | 1,460 | 8,148 | 259 | -69.61 | -66.55 | -71.30 | -76.71 | 1.092 | 192.16 |
| Cassia | 1,359 | 7,959 | 240 | -70.83 | -66.75 | -77.55 | -83.31 | 1.059 | 186.36 |
| Minidoka | 1,373 | 6,401 | 174 | -64.68 | -57.78 | -71.91 | -77.96 | 0.883 | 155.48 |
| Jerome | 1,742 | 6,012 | 192 | -55.07 | -46.74 | -62.73 | -70.82 | 0.881 | 155.08 |
| Valley | 2,869 | 4,214 | 157 | -18.99 | -12.83 | -17.80 | -40.99 | 0.805 | 141.66 |
| Franklin | 703 | 6,279 | 202 | -79.86 | -81.32 | -84.47 | -85.59 | 0.793 | 139.64 |
| Boundary | 1,145 | 5,794 | 171 | -67.00 | -59.68 | -68.66 | -75.18 | 0.788 | 138.78 |
| Fremont | 954 | 5,645 | 204 | -71.09 | -68.68 | -75.25 | -79.71 | 0.750 | 131.98 |
| Teton | 3,463 | 3,005 | 230 | 7.08 | 6.80 | 6.15 | -4.33 | 0.735 | 129.36 |
| Shoshone | 1,472 | 4,500 | 160 | -50.70 | -38.17 | -47.97 | -54.63 | 0.678 | 119.44 |
| Gooding | 1,100 | 4,676 | 142 | -61.91 | -53.78 | -65.69 | -70.22 | 0.656 | 115.52 |
| Washington | 1,010 | 4,429 | 116 | -62.86 | -55.86 | -67.38 | -74.72 | 0.618 | 108.78 |
| Benewah | 935 | 4,094 | 116 | -62.82 | -53.65 | -68.21 | -68.16 | 0.571 | 100.58 |
| Owyhee | 756 | 4,101 | 93 | -68.87 | -60.03 | -70.51 | -72.49 | 0.552 | 97.14 |
| Boise | 1,065 | 3,727 | 118 | -55.55 | -45.43 | -52.69 | -62.01 | 0.544 | 95.84 |
| Lemhi | 1,038 | 3,716 | 120 | -56.33 | -54.84 | -59.93 | -70.82 | 0.540 | 95.08 |
| Clearwater | 774 | 3,550 | 96 | -64.20 | -58.35 | -63.91 | -71.56 | 0.491 | 86.48 |
| Caribou | 445 | 2,906 | 105 | -73.44 | -70.97 | -78.87 | -82.65 | 0.381 | 67.02 |
| Bear Lake | 346 | 2,908 | 71 | -78.73 | -77.43 | -81.04 | -81.96 | 0.370 | 65.08 |
| Power | 785 | 2,146 | 90 | -46.43 | -40.18 | -54.55 | -65.22 | 0.333 | 58.62 |
| Adams | 577 | 2,037 | 67 | -55.85 | -49.04 | -59.04 | -68.68 | 0.297 | 52.28 |
| Custer | 586 | 1,998 | 66 | -54.64 | -53.27 | -60.24 | -68.22 | 0.294 | 51.68 |
| Oneida | 253 | 2,119 | 85 | -78.67 | -77.92 | -83.83 | -87.28 | 0.269 | 47.44 |
| Lincoln | 392 | 1,466 | 59 | -57.80 | -48.94 | -63.14 | -69.39 | 0.211 | 37.16 |
| Lewis | 305 | 1,503 | 38 | -66.26 | -59.82 | -72.35 | -78.35 | 0.205 | 36.16 |
| Butte | 185 | 1,268 | 41 | -74.54 | -66.92 | -74.58 | -79.13 | 0.165 | 29.06 |
| Camas | 153 | 547 | 28 | -56.29 | -51.55 | -58.87 | -69.35 | 0.080 | 14.00 |
| Clark | 50 | 280 | 3 | -69.70 | -71.62 | -78.89 | -84.71 | 0.037 | 6.60 |

Historical A-leading counties: 2024-president: Blaine, Teton; 2020-senate-II: Blaine, Latah, Teton; 2022-senate-III: Blaine, Teton; 2022-governor: Blaine. All other counties favored B in those comparisons. The [440-row county pair table](data/county-baselines.csv) contains every county for ten separate historical/named-opposition views, denominators, party identities, pair participation and source locators. The [native table](data/baselines/native-baselines.csv.gz) and [complete candidate table](data/baselines/complete-candidate-baselines.csv.gz) retain all native rows and full candidate identities.

The canonical priority order uses all eleven named candidates, descending votes, then lexical full `ID:2024:pres:<county FIPS>:<first original row>` key. Its top 15 have **65,391 / 905,057 = 7.225070%**. The minimum integer 80% set has **528 units / 724,515 votes = 80.051864%**. The previous 527 have **723,753 = 79.967671%**. Osburn, Shoshone County, original rows11741–11753, adds762. The other **457 units / 180,542 votes** stay in every statewide calculation. The 44 parents are grouping summaries, never additional native votes. [Full canonical order](data/baselines/native-priority-order.csv), [all 44 parent/full-child/priority/remainder arrays](data/baselines/priority-contract.json).

My originals-first extraction preceded reading turnout derivatives. Reciprocal QA independently performed **411,951 field comparisons**, with zero unresolved value differences, comparing complete raw source cell dictionaries and metadata, candidates, raw parties, nulls, control rows, statistics, method labels, full order and all 44 maps. My earlier label/row tie order survives as a dated [pre-peer witness](data/baselines/qa/pre-peer/witness.json). The canonical sort reorders **six tied pairs / twelve ranks** without changing priority membership or crossing. Five `ABS` abbreviation flags differ lexically, and turnout represents two all-null2020 appendix headings separately; raw labels/cells agree. Neither flag inventory is a method partition. CSV empty rate versus JSON null is a documented serialization difference, never a zero. [Reciprocal comparison and exact peer file pins](data/baselines/qa/peer-comparison.json), [source-position map](data/baselines/qa/source-position-map.json.gz). Coordinator acceptance is pending and is separate from historical arithmetic agreement.

## Turnout, registration and source disagreements

The 2024 statistics workbook contains986 native contexts plus44 overlapping county footers. It reports cutoff registration **1,057,735**, election-day registrations **121,015**, total registration **1,178,750**, and ballots **917,469**. All detail columns sum to each footer, and cutoff+day=total. The headers do not establish active/inactive status or an exact cutoff timestamp. These are historical statistics, not current registrations. The stats-only `Bingham County / BONNEVILLE 27`, row318, has four literal numeric zeros; it is not an inferred presidential zero and does not explain the three-ballot difference. [Original statistics workbook](https://archive.sos.idaho.gov/elections/data/results/2024/raw_stats_general.xlsx), [all original statistics positions](data/baselines/source/statistics-positions.json.gz).

Of985 literal race/statistics pairs,978 match presidential all-category totals. All seven nonzero residuals are Boundary County. Its absentee row has0 stats ballots against2,721 race categories; six geographic labels have2,724 more stats ballots combined. Net+3 is retained without reassigning absentee votes or claiming identical physical/method universes. [Exact residuals and positions](data/baselines/source/2024-statistics-disagreements.json).

| Literal context | Race source first row | Stats row | Pres all-category | Stats ballots | Stats minus race |
|---|---|---|---|---|---|
| Absentee | 5488 | 435 | 2721 | 0 | -2721 |
| Moyie Springs | 5449 | 432 | 1107 | 1852 | 745 |
| Naples | 5475 | 434 | 850 | 1275 | 425 |
| N. Bonners Ferry | 5436 | 433 | 824 | 1367 | 543 |
| Bonners Ferry/Kootenai | 5423 | 430 | 634 | 1029 | 395 |
| Valley View | 5462 | 429 | 573 | 950 | 377 |
| Copeland | 5410 | 431 | 548 | 787 | 239 |

The 2020 county controls give cutoff995,087 + day87,330 = registered1,082,417; ballots878,527. Native known sums match those controls, while cutoff/day/registered/ballots retain32/35/33/9 null cells. The 2020 Senate/president candidate cells retain8/42 nulls; closing known sums does not fill them. Over/under/blank ballot totals are not supplied by the selected2020/2022 candidate sheets. Ballots minus candidate votes is an accounting difference, not an invented undervote category. [2020 original ZIP, Amend & Stats sheets](https://archive.sos.idaho.gov/elections/data/results/2020/2020_General_Canvass.zip).

The 2022 general statistics table gives cutoff1,003,978 + day44,285 = registered1,048,263; ballots599,493. Its method table gives absentee129,210 and early61,048, with county dashes preserved as null and literal dash. These are county ballot controls, not candidate-method allocations; no remaining residual is labeled Election Day. The same public page’s separately presented **Write-In Totals** table reports **Lisa Marie46**, while both general governor workbooks report **Lisa Marie (W/I), IND,67**. This is an **unexplained publication/scope disagreement**. Generic page text and links do not establish that46 is a primary total. The actual separately linked **primary** governor write-in PDF names **Ryan Cole22, David Reilly21 and Shelby Rognstad6,712**, a distinct field that is not merged with this general baseline. [2022 statistics original page](https://voteidaho.gov/election-results/2022-election-stats/), [exact independent receipt](data/baselines/source/acquisition.json), [all table literals and positions](data/baselines/source/2022-statistics-tables.json), [precise original receipts and scope note](data/baselines/source/2022-writein-scope-disagreement.json), [actual primary PDF](https://archive.sos.idaho.gov/elections/data/results/2022/Primary/WriteIn_Governor.pdf), [general ZIP](https://archive.sos.idaho.gov/elections/data/results/2022/2022_General_Canvass.zip).

The 2022 ZIP has complementary county/precinct statewide and legislative/judicial workbooks, not duplicate native geographies to add. The 2020 county abstracts overlap statewide canvass rows and are retained intact once inside the 44-original archive (38XLSX/sixPDF). The 2020 final state/district/Ada appendix rows and2022 final controls are nonadditive. Governor2022 row1157 literally says `CO. TOTAL` but contains the statewide vector; it is not another Washington precinct. [Archive member CRC/hash inventory](data/baselines/source/archive-members.json), [reused original ledgers](data/baselines/source/reused-originals.json).

## Targets, bounds and historical sensitivity

For fixed pair volumes `T_i=A_i+B_i`, let `s_i=A_i/T_i`, `T=ΣT_i` and `M=ΣT_i(2s_i−1)`. The unbounded tie shift is `(B−A)/(2(A+B)) = −M/(2T)`. Target pair margin `g` requires `(gT−M)/(2T)`. Thus **A+1 pair margin adds 0.5 share points before clipping**, not one share point. A+1 margin is `0.01T` net votes; a+1pp A-share transfer gains `0.02T_i` net votes in unit i. All-candidate margin is net divided by the separate final valid-candidate denominator. The +1pp gain column is the unsaturated derivative; `bounded_gain_for_1pp_share` separately clips that proposed local increment at 100%. Counts, share points, margin points and cushions have separate columns.

The implemented bounded solve finds `δ` such that `ΣT_i[2 clip(s_i+δ,0,1)−1]=gT`. Raw unbounded targets remain visible. Native 2024 clipping changes the statewide root; merely clipping a precomputed unbounded answer would miss the tie. Zero-pair units remain present with no-positive-pool status and undefined shares; null pair preferences/pools remain unknown. Already-winning baselines retain signed negative tie shifts, and minimum nonnegative improvement is separate. Impossible targets retain their unbounded values. [Calculator implementation](data/baselines/calculate.py).

| Actual native preference/volume anchor | Rows | Unbounded tie pp | Bounded tie pp | Bounded A+1 pp | Tie clipped rows | Status |
|---|---|---|---|---|---|---|
| 2024-president | 985 | 18.760921 | 18.778064 | 19.281419 | 5 | feasible |
| 2020-senate-II | 974 | 15.320814 | 15.327177 | 15.828079 | 2 | feasible |
| 2020-president | 974 | 15.877143 | 15.886906 | 16.388613 | 2 | feasible |
| 2022-senate-III | 999 | 17.860516 | 17.864029 | 18.367579 | 3 | feasible |
| 2022-governor | 999 | 24.901725 | 24.901822 | 25.401858 | 1 | feasible |
| 2020-Fleming-Risch | 974 | unknown | unknown | unknown | unknown | unknown_preference_or_pair_pool |
| 2022-Cleveland-Crapo | 999 | 37.779100 | 37.779100 | 38.279100 | 0 | feasible |

The 2020 Fleming native scenario remains unknown because its candidate nulls cannot support a complete fixed-pair allocation. Its county controls support the complete county pair calculation. Each other repeat retains every source row, including zero-pair contexts. The [state scenario table](data/baselines/state-scenarios.csv) stores the pair and all-candidate volumes and full-field plurality check separately. In the actual 2020 county Fleming–Risch pair, **T=563,775**, a tie gives each 281,887.5, and A+1 gives Fleming 284,706.375. **Jordan’s fixed 285,864 still exceeds both**. This pair scenario cannot elect Fleming merely by tying or gaining one pair-margin point. [Original2020 Federal county controls](https://archive.sos.idaho.gov/elections/data/results/2020/2020_General_Canvass.zip).

Low/base/high are **observed historical volumes and county mixes**, not probabilistic ranges: low 2022 Senate590,890 valid candidate votes; intermediate/base 2020 Senate859,827; high 2024 president905,057. For each volume source, county V is its actual valid candidate total. For each preference anchor, `p_c=(A_c+B_c)/V_anchor,c` and scenario pair volume is `T_c=V_volume,c × p_c`. Thus the preference anchor’s **county-specific pair participation** is preserved rather than using one statewide multiplier. Pair preferences are held fixed separately. The primary repeat uses 2024 volumes and2024 preferences. The additional anchor-repeat setting uses each anchor’s own county volumes. [Exact settings](data/baselines/scenario-settings.json).

| Preference anchor | Historical volume/mix | All candidate V | Scenario pair T | Baseline margin pp | Tie share shift pp | A+1 shift pp |
|---|---|---|---|---|---|---|
| 2024-president | historical_low_2022 | 590,890 | 574,699.70 | -36.462 | 18.230846 | 18.730846 |
| 2024-president | historical_base_2020 | 859,827 | 836,184.89 | -37.159 | 18.579437 | 19.079437 |
| 2024-president | historical_high_2024 | 905,057 | 880,218.00 | -37.522 | 18.760921 | 19.260921 |
| 2020-senate-II | historical_low_2022 | 590,890 | 566,748.75 | -29.889 | 14.944597 | 15.444597 |
| 2020-senate-II | historical_base_2020 | 859,827 | 824,310.00 | -30.642 | 15.320814 | 15.820814 |
| 2020-senate-II | historical_high_2024 | 905,057 | 867,628.01 | -30.979 | 15.489331 | 15.989331 |
| 2022-senate-III | historical_low_2022 | 590,890 | 528,347.00 | -35.721 | 17.860516 | 18.360516 |
| 2022-senate-III | historical_base_2020 | 859,827 | 768,691.12 | -36.603 | 18.301351 | 18.801351 |
| 2022-senate-III | historical_high_2024 | 905,057 | 808,612.30 | -36.962 | 18.481080 | 18.981080 |
| 2022-governor | historical_low_2022 | 590,890 | 477,363.12 | -49.804 | 24.901775 | 25.401775 |
| 2022-governor | historical_base_2020 | 859,827 | 694,302.01 | -50.428 | 25.213994 | 25.713994 |
| 2022-governor | historical_high_2024 | 905,057 | 729,570.86 | -50.706 | 25.352851 | 25.852851 |

For native 2024 sensitivity, each historical county volume is distributed using that county’s **2024 all-candidate native proportions**, then multiplied by each native 2024 pair participation. This is a stated within-county scenario allocation, not a historical cross-year precinct join or current method forecast. Older native source repeats retain their actual pair counts. Fractional scenario votes are expectations; historical source integers remain unchanged. Preference anchors include all required comparisons plus named independent opposition pairs. No 2026 turnout, candidate or remaining-vote assumptions are estimated from these historical outcomes.

The [63,518-row unit target table](data/baselines/unit-targets.csv.gz) supplies county/native weights, pair participation, baseline and target net contributions, raw and bounded target shares, clipping changes, gains, and selected-unit-only break-even for both tie and A+1. All 44 counties and all nonpriority units remain in each applicable state scope.

For selected unit c, holding every other unit at its stated volume/share, `q_c=[T_c+gT−Σ_other T_j(2q_j−1)]/(2T_c)`. Below0 is already secured under those assumptions; above1 is impossible; no positive pair pool is a separate state. With all other counties at unchanged 2024 preferences, **Ada requires 108.226263%**, which is impossible. With every other county at an explicit **+10pp A-share** assumption and the same pair volumes, Ada’s tie threshold becomes **84.355440%**. This is an alternative conditional path, not a prediction or unique winning requirement. Any net gain anywhere offsets the same net loss elsewhere.

## Offline live remainder and reproduction

`live_remainder.py` keeps every counted named candidate vote fixed, models **only** the user-supplied remaining valid-candidate pool, and separates remaining pair participation from A preference and the named other-candidate allocation. For remaining pair pool U and counted lead L, the all-remaining pair tie is `(U−L)/(2U)`. A margin target uses the **FINAL** pair denominator `countedA+countedB+remainingPair`, or final all-candidate denominator `sum(counted)+remainingValid` when explicitly selected. A selected-unit solve holds all other remainder assumptions fixed. Its legal plurality threshold separately checks **every named opposing candidate**, requiring strictly greater votes; ties retain Idaho’s coin rule. Raw preferences outside[0,1] are clipped explicitly. Negative pools/counts are invalid; unknown pools remain unknown; zero pool is not inferred outstanding volume. [Implementation](data/baselines/live_remainder.py).

The saved [14 synthetic inputs](data/baselines/live-synthetic-inputs.json) and [results](data/baselines/live-synthetic-results.json) exercise unknown, no-pool, negative, impossible, secured, both clipping directions, final-pair versus final-all-candidate cushions, no-pair pool, another candidate winning, negative required tie shift and selected-unit assumptions. These are arithmetic examples, not calibrated probabilities or 2026 remaining-vote estimates.

From the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/idaho/data/baselines/reproduce.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/idaho/data/baselines/calculate.py --pair 2024-president --unit 'Ada County' --others-shift-pp 10 --target-margin-pp 0
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/idaho/data/baselines/calculate.py --scope native --pair 2024-president
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/idaho/data/baselines/live_remainder.py path/to/one-case.json
```

The offline build needs standard Python plus installed Poppler for independent PDF extraction/rendering; separate acquisition scripts require requests/network. It reuses complete original public bytes by exact hash, parses source positions independently, calculates, renders, validates and audits. No dependency/cache directories are retained. [Source/field schema and acquisition instructions](data/baselines/source/SCHEMA.md), [validation](data/baselines/validation.json), [complete owned asset manifest](data/baselines/asset-manifest.json). Every stored asset is strictly below40,000,000 bytes; gzip originals reconstruct byte-for-byte, with stored/raw sizes and hashes. Original complete workbooks/ZIPs retain unrelated offices and raw administrative rows without manufacturing additional unrelated baseline tables.

Remaining substantive gates are the unexplained Boundary scopes/net3, individual2020 nulls, Lisa Marie 46/67 scope disagreement, final statewide/later eligible-write-in certification and actual 2026 choice IDs, current reporting-unit/boundary joins, a measured remaining-pool model, actual November source/cadence tests and calibration. The turnout report’s unsupported HTML 46 primary attribution is queued for coordinator-managed correction; my reciprocal proof compares actual literals without accepting that stage attribution. Coordinator acceptance remains pending. Source dates, server Last-Modified, UTC retrieval and canvass status are separate; an archive object clock is not a certification timestamp or demonstrated live update schedule.
