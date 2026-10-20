# Illinois turnout and reporting-volume research

Observed October 19–20, 2026 UTC. **Primary ranking: 2024 president, the exact recorded votes for Harris, Trump and Kennedy where present in the original native export.** Illinois had no 2024 Senate election. This is a printed-known candidate source scope, not all valid presidential votes or ballots cast. It ranks authority ID plus literal precinct-name observations, not physical/current precincts. Four administrative-only named pools remain unavailable; 15 Kennedy cells in otherwise observed groups remain null. [Official native export](https://www.elections.il.gov/Downloads/ElectionOperations/ElectionResults/ByOffice/66/66-120-PRESIDENT%20AND%20VICE%20PRESIDENT-2024GE.csv), [official statewide presentation](https://www.elections.il.gov/electionoperations/ElectionVoteTotals.aspx?ID=9huvqbsiUWA%3D&OfficeType=LpWf6lpbWOfBN3kEuxRi3A%3D%3D).

**Exact top-15 share: 29,572 / 5,592,368 = 0.52879210%. Exact minimum descending set reaching 80%: 5,540 source observation groups, totaling 4,474,312 / 5,592,368 = 80.00746732%.** The preceding 5,539 contribute 4,473,789 (79.99811529%); St. Clair authority 88, literal `O FALLON 3`, adds 523. Integer proof: `5*4,473,789 < 4*5,592,368 <= 5*4,474,312`. Descending order makes this the smallest cardinality for this source scope. The remainder is 4,522 contexts with 1,118,056 recorded printed-known votes, including four unavailable named pools with no invented candidate zeros. [Full native order](data/turnout/extract/native-2024-order-printed_observed_sum.csv.gz), [complete dispatch contract](data/turnout/priority-set.json).

The ordered 5,540 priority keys, every one of the 10,062 observation keys, complete remainder, all 108 authority parents and 11,535 full presentation/context references are in the contract. Each constituent identifies original record positions and container/name variants, with a lossless reference to all 12 original fields. Every geography outside priority remains in the statewide sums. No county substitution or legal/current-geography approval is implied. [Raw record objects](data/turnout/extract/original-native-records.jsonl.gz), [full original source contexts](data/turnout/extract/source-contexts-2024.jsonl.gz).

| Rank | Authority ID / literal precinct observation | Known printed votes | Cumulative votes |
| ---: | --- | ---: | ---: |
| 1 | COOK (16) / 7600027 | 2,415 | 2,415 |
| 2 | CHAMPAIGN (10) / MAHOMET 4 | 2,337 | 4,752 |
| 3 | CHAMPAIGN (10) / MAHOMET 1 | 2,236 | 6,988 |
| 4 | COOK (16) / 9000001 | 2,153 | 9,141 |
| 5 | CHAMPAIGN (10) / CITY OF CHAMPAIGN 34 | 2,094 | 11,235 |
| 6 | WILL (99) / PLAINFIELD PCT 013-STYLE 307 | 2,048 | 13,283 |
| 7 | COOK (16) / 8300051 | 1,982 | 15,265 |
| 8 | WILL (99) / TROY PCT 001-STYLE 344 | 1,910 | 17,175 |
| 9 | MACON (55) / MT. ZION 2 | 1,811 | 18,986 |
| 10 | CHAMPAIGN (10) / CHAMPAIGN 4 | 1,810 | 20,796 |
| 11 | WILL (99) / NEW LENOX PCT 020-STYLE 283 | 1,780 | 22,576 |
| 12 | CITY OF CHICAGO (105) / Ward 43 Precinct 09 | 1,767 | 24,343 |
| 13 | CITY OF CHICAGO (105) / Ward 27 Precinct 16 | 1,760 | 26,103 |
| 14 | CITY OF CHICAGO (105) / Ward 44 Precinct 17 | 1,751 | 27,854 |
| 15 | CITY OF CHICAGO (105) / Ward 46 Precinct 06 | 1,718 | 29,572 |

Ties use descending exact integer count, then literal authority ID as a string and literal precinct name. Unavailable named pools follow observed numeric zeros and have null rank. A separate observed-mark scope adds generic write-in marks: N=5,649,779; top 15=29,935 (0.52984373%); minimum 5,535; preceding 5,534 / 4,519,675; crossing il:2024:authority:107:label:PRECINCT%201 adds 527 to 4,520,202. Remainder 4,527 / 1,129,577. [Complete alternate order](data/turnout/extract/native-2024-order-printed_plus_generic_observed.csv.gz). Generic marks do not establish legal write-in votes, and this comparison proves no robustness of an unavailable legal native ranking.

**Candidate universe and primary reconciliation.** All 27 literal statewide 2024 reporting rows sum 5,633,310. The three printed candidates sum 5,592,368 and match the native export candidate by candidate;24 additional named rows sum 40,942. Native generic write-in case variants sum 57,411 (recorded source marks only; no generic category is published for Kane or Morgan, so absent observations stay null and any empty recorded aggregation is separately labeled), leaving 16,469 unallocated between source scopes. No rescaling, name/VP merging, CandidateID 0 deduplication or allocation of that difference occurs. The statewide table includes raw names such as Rudolph Ware, Mike ter Maat and Melina Abdullah as separate reporting entries;27 source rows are not a claim of 27 presidential tickets. Blank party cells remain blank. Historical detail pages identify write-in records but contain no vote allocations; their post-election database dates do not establish legal filing eligibility. [State table](https://www.elections.il.gov/electionoperations/ElectionVoteTotals.aspx?ID=9huvqbsiUWA%3D&OfficeType=LpWf6lpbWOfBN3kEuxRi3A%3D%3D), [all raw named rows/parties/percentages/detail links](data/turnout/extract/statewide-source-rows.csv), [40 independently inspected detail records](data/turnout/extract/candidate-detail-metadata.json).

The [FEC2024 publication](https://www.fec.gov/resources/cms-content/documents/2024presgeresults.pdf), independently re-extracted from its retained original, prints IL West 1,569, scattered 518 and total 5,633,310. Three printed names plus seven other source names contribute 5,632,792; the remaining 17 state rows sum 518. That aggregate agreement permits no alias or running-mate joins. FEC is a separate publication of state-provided returns, not independent underlying vote counting. The [NARA certificate of ascertainment](https://www.archives.gov/files/electoral-college/2024/ascertainment-illinois.pdf) describes the December 2,2024 state canvass and certifies elector slates; elector votes are repeated across individual electors and are never summed as extra presidential votes. [Independent PDF text and review](data/turnout/extract/federal-local-evidence-review.json).

| 2024 statewide literal reporting name | Party literal (empty shown —) | Reported votes |
| --- | --- | ---: |
| Kamala D. Harris | DEMOCRATIC | 3,062,863 |
| Donald J. Trump | REPUBLICAN | 2,449,079 |
| Robert F. Kennedy Jr. | INDEPENDENT | 80,426 |
| Jill Stein | — | 31,023 |
| Chase Oliver | — | 3,510 |
| Claudia De La Cruz | — | 2,877 |
| Cornel West | — | 1,569 |
| Peter Sonski | — | 1,391 |
| Rudolph Ware | — | 322 |
| Mike ter Maat | — | 90 |
| Shiva Ayyadurai | — | 42 |
| Heather Lynn Stone | — | 30 |
| Melina Abdullah | — | 21 |
| Joseph Kishore | — | 12 |
| Future Madame Potus | — | 12 |
| James T. Struck | — | 8 |
| Andre Ramon McNeil Sr | — | 7 |
| Gordan Hlavenka | — | 5 |
| David J Nash | — | 4 |
| Kevin McKee | — | 4 |
| Cherunda Fox | — | 3 |
| John P Albers | — | 3 |
| Garry Hubbard | — | 3 |
| Jerry White | — | 2 |
| Brian Larry Kienitz | — | 2 |
| Richard Mayers | — | 1 |
| Susan Maude Buchser | — | 1 |

Source minor percentages such as Stein 31,023 with `< .01%` are contradictory to the counts. Exact source percentage strings remain in the extraction and are unused for weights. Candidate and category totals use integer counts from source rows, never those percentages.

**Disjoint hierarchy and native units.** The 108 native authority IDs are 102 county authorities plus Bloomington 104, Chicago 105, Danville 106, East St. Louis 107, Galesburg 108 and Rockford 110. There is no 103 rd county. Historical source containers explicitly associate these cities with county IDs 64/16/92/88/48/101. The county web presentation combines those city counts; it is a separate aggregation view. For example, Cook county Harris 1,447,821 equals suburban authority 16 672,122 plus Chicago 105 775,699. McLean county Harris 44,495 equals clerk authority 64 23,261 plus Bloomington 104 21,234. Every printed candidate reconciles in all 102 counties in all three years, and every county named-candidate sum matches its statewide control. [County candidate source positions](data/turnout/extract/county-candidate-source-rows.csv), [108-authority inventory](data/turnout/extract/authority-inventory.json).

Six city authorities use both container 0 and their county-container ID across 2024 categories. Those are preserved source presentations of the same authority, not six extra vote pools. Four blank-label groups in Lawrence 51, Marshall 59, Menard 65 and Galesburg 108 publish only generic/nonvote categories; they are retained as unavailable named pools. Will labels include ballot `STYLE` splits and `FED` labels; Peoria includes `FED ONLY` observations. No aggregation to polling sites, vote centers, wards, VTDs or polygons is invented. `PrecinctName` is the literal source label; there is no separate precinct-ID or voting-method column in these three exports. All central/early/absentee-looking labels remain literal with method unavailable. [Native objects](data/turnout/extract/native-units-2024.jsonl.gz), [schema](data/turnout/source/SCHEMA.md).

County FIPS use the independently parsed [Census2024 county identifier file](https://www.census.gov/geographies/reference-files/2024/geo/gazetter-file.html), not an authority-ID formula. The current [McLean clerk page](https://mcleancountyil.gov/1218/Polling-Locations) explicitly excludes Bloomington city and warns of precinct-line changes. Current office names/IDs and historical counts therefore do not prove November 2026 identity, legal exhaustiveness or geometry compatibility. The [city Chicago proclamation](https://cboeprod.blob.core.usgovcloudapi.net/prod/2024-11/Proclamation%20of%20Official%20Results%20%28November%205%2C%202024%29.pdf) confirms printed totals and its named total 1,001,481; the [Bloomington official write-in report](https://bloomingtonelectionsil.gov/wp-content/uploads/2024/11/2024-General-Election-Write-In-Official-Report.pdf) totals 204 using some combined ticket labels. These bounded local checks do not allocate the statewide valid write-in universe across native units. Galesburg’s retained official scanned canvass shows genericwrite-in 72 rather than named allocation. Local counts and vintages remain source-scoped; no blanket valid-native inference follows.

**County aggregation sensitivity, kept separate from the primary finer order.** All 102 combined county named totals reconcile exactly to 5,633,310. Top 15 contribute 4,423,672 (78.52704715%). The minimum 17 contribute 4,539,638 (80.58562373%); the first 16 contribute 4,487,130 (79.65352519%); LaSalle adds 52,508. Remainder 85 counties /1,093,672 votes. Ordered 17: Cook, DuPage, Will, Lake, Kane, McHenry, Madison, Winnebago, St. Clair, Sangamon, Champaign, McLean, Peoria, Tazewell, Kendall, Rock Island, LaSalle. The contract expands these to all constituent authority keys; Chicago/Rockford/East St. Louis/Bloomington are never silently omitted or counted again. [Complete102county order](data/turnout/extract/county-2024-order-all_named_votes.csv). The official county selector produces no-information bodies for all six city selections; unchanged-default Adams POST clears grids, so the populated initial Adams GET is used and both observations retained. HTTP 200 alone is never evidence of numeric coverage.

**Actual election comparisons and denominator controls.** The 2026 regular Class II election is November 3,2026. The 2020 Durbin–Curran Senate contest is this Class II seat; the 2022 Duckworth–Salvi Senate contest is the separate Class III seat and recent actual midterm. The 2024 comparison is president. [ISBE historical search](https://www.elections.il.gov/electionoperations/votetotalsearch.aspx), [FEC2020 official results](https://www.fec.gov/documents/4227/federalelections2020.pdf), [FEC2022 official results](https://www.fec.gov/documents/5675/federalelections2022.pdf), [ISBE schedule/authority originals and source receipts](data/turnout/source/external-originals.json). Each historical native universe is independently retained and ranked, without joining labels across years.

| Contest | Printed native votes | Additional statewide named votes | All named source votes | Native generic marks | Ballots cast | Turnout-table “Total Voters” |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2024 president | 5,592,368 | 40,942 | 5,633,310 | 57,411 | 5,705,246 | 8,101,424 |
| 2022 Senate, Class III midterm | 4,098,862 | 34 | 4,098,896 | 1,911 | 4,144,125 | 8,115,751 |
| 2020 Senate, same Class II | 5,968,883 | 18 | 5,968,901 | 2,530 | 6,098,729 | 8,364,099 |

The 2020 five printed candidates are Durbin 3,278,930; Curran 2,319,870; Wilson 237,699 (WILLIE WILSON PARTY); Malouf 75,673 (LIBERTARIAN); Black 56,711 (GREEN). Named write-ins Keely 10, Seida 6 and Schaal 2 are separate from generic 2,530. The 2022 printed candidates are Duckworth 2,329,136 (DEMOCRATIC), Salvi 1,701,055 (REPUBLICAN), Redpath 68,671 (LIBERTARIAN); named Seida 23 and Vlakancic 11 are separate from generic 1,911. All 40 statewide raw name/party/count/detail-link records remain in the source-row CSV. No 2024 Senate or nonexistent comparator governor contest is used.

The [official turnout interface](https://www.elections.il.gov/ElectionOperations/VoterTurnout.aspx?MID=fVf30XCcBCY%3D&T=637204911330922199), selected through observed public events, supplies 102 combined county rows plus a statewide control for each year. “Total Voters” is the source field label used as a historical registration sensitivity; the inspected table does not define its snapshot/status fully, so it is not voting-eligible population. The native `Registration` field repeats on candidate/category rows. It is retained once per authority/literal-label observation only for a separate source-field diagnostic, never summed across candidates or assumed identical to the turnout table. Totals are 7,210,422 /7,973,061 /7,980,411 in 2024/2022/2020, versus the distinct table controls above. Zero native Registration literals do not prove zero registered people. [All306 registration comparisons](data/turnout/extract/registration-source-reconciliation.csv).

A separate suburban Cook [official post-election report](https://www.cookcountyclerkil.gov/sites/default/files/pdfs/Post-Election%20Report%20%20-%20%20110524.pdf), printedpage 5, reports 2024 Early Voting 451,654; Grace Period/In-Person Absentee 14,742; Mail Voting 192,412; Election Day 431,134, totaling 1,089,942 ballots. These method volumes are separately retained with 2020 comparisons and reconcile; they are not presidential candidate counts, statewide method coverage or a live remaining-vote estimate. [Source-scoped local method controls](data/turnout/extract/local-ballot-method-controls.json). Candidate votes are not ballots. In 2024 ballots exceed all named source votes by 71,936. Native published nonvote categories sum Under Votes 47,666 / Over Votes 4,821 / Blank Ballots 510, with absence left null outside rows that actually publish them. Printed votes + generic marks + all these native categories total 5,702,776, which remains 2,470 below the separate ballot control 5,705,246. This residual is unallocated, not labeled as extra undervotes, blank ballots or valid write-ins. Senate 2022 and 2020 native exports contain no under/over/blank categories; the corresponding ballots-minus-all-native-category differences 43,352 and 127,316 are denominator gaps, not observed nonvote allocations. [Exact reconciliation](data/turnout/extract/denominator-reconciliation.json), [literal category totals](data/turnout/extract/native-category-controls.csv).

The [current registration page](https://www.elections.il.gov/VotingAndRegistrationSystems/RegistrationCounts.aspx) describes unofficial jurisdiction-supplied statewide-database counts that fluctuate daily and prints 10/19/2026 10:18 AM (timezone unstated). Its actual linked CSV contains 108 IDs and literal columns`A` and`I`, summing 8,306,489 and 730,052. These literal category letters are retained; the inspected CSV/page does not itself expand their definitions. They are not historical ballots, an approved boundary join, or a 2026 turnout forecast. The compatibility CSV retains the exact current source fields and clock separately from historical counts.

| Separate county sensitivity | Denominator | Top 15 count volume/share | Minimum 80 count | Preceding cumulative | Crossing cumulative |
| --- | ---: | --- | ---: | ---: | ---: |
| 2024 named presidential votes | 5,633,310 | 4,423,672 / 78.52704715% | 17 | 4,487,130 | 4,539,638 |
| 2024 printed presidential votes | 5,592,368 | 4,384,426 / 78.40016966% | 17 | 4,447,693 | 4,500,125 |
| 2024 printed+generic marks | 5,649,779 | 4,435,878 / 78.51418613% | 17 | 4,499,557 | 4,552,245 |
| 2024 ballots | 5,705,246 | 4,483,455 / 78.58477969% | 17 | 4,547,501 | 4,600,573 |
| 2024 Total Voters field | 8,101,424 | 6,408,816 / 79.10727793% | 16 | 6,408,816 | 6,499,092 |
| 2022 named Senate votes | 4,098,896 | 3,165,824 / 77.23601672% | 18 | 3,250,667 | 3,285,910 |
| 2022 ballots | 4,144,125 | 3,196,079 / 77.12313214% | 18 | 3,281,530 | 3,317,398 |
| 2020 named Senate votes | 5,968,901 | 4,733,075 / 79.29558557% | 16 | 4,733,075 | 4,796,421 |

The 2022 named Senate volume is 72.76176884% of 2024 named presidential volume. Historical changes mix candidate/contest/year effects with participation. These are volume/denominator sensitivity anchors with complete statewide weights, not low/base/high 2026 forecasts. Full orders for every listed scope/year are retained; no unavailable native voting-method distribution is invented.

**Reproduction and QA.** `build_turnout.py` independently parses original state bodies, `enrich_evidence.py` re-extracts primary PDFs/detail metadata, `compare_peer.py` freezes immutable reciprocal captures, `write_report.py` generates this report, and `validate_turnout.py --seal` checks and seals the owned assets. Run these offline in that order, using Python 3 with beautifulsoup 4 and Poppler; acquisition separately requires requests. Own reciprocal reconciliation: **2,232,689 checks,0 errors**. It compares all 146,370 rawrecords×12 fields+positions,306 countycontrols,1462 literal candidate rows, native candidates/missingness/categories/registration/contexts, all 108 authority categories/year, full county orders/integer 80 and native printed order. Only the explicit placement of four unavailable named pools after observed zeros differs from the peer’s empty-recorded-sum ordering; both immutable raw captures remain. [Reciprocal evidence](data/turnout/peer-reconciliation.json), [offline validation](data/turnout/validation.json), [owned asset manifest](data/turnout/asset-manifest.json), [source schema](data/turnout/source/SCHEMA.md).

Every numeric-source original is retained losslessly below 40,000,000 stored bytes, or referenced read-only by exact original/stored SHA 256 and size. Complete response headers, requested/final URLs, parent chains, public form fields, redirects, UTC and source clocks live in receipts. Shared original news and peer primary bodies are references, not numeric derivative dependencies. All unrelated offices in downloaded county pages remain in original bytes; no extra demographic extraction is required. No live collector, measured November cadence, calibrated Needle, current precinct approval or complete legal-native write-in universe is claimed. Coordinator acceptance remains pending.

**Complete 108-authority reported-mark order (secondary scope).** This table uses printed-known+generic recorded marks only (N 5,649,779), preserving commission boundaries. It does not replace the primary finer order or claim a legal named-vote ranking. Its top 15=4,290,100 /5,649,779; minimum 20=4,555,873; preceding 19=4,508,088; Kankakee 46 crosses; remainder 88=1,093,906. The compatibility filename`county-turnout.csv` contains these 108 authorities, never 102 substituted counties. [Full machine table](data/county-turnout.csv).

| Rank | Actual authority (ID) | Parent county FIPS | Reported printed+generic marks | Cumulative |
| ---: | --- | --- | ---: | ---: |
| 1 | COOK (16) | 17031 | 1,077,758 | 1,077,758 |
| 2 | CITY OF CHICAGO (105) | 17031 | 1,001,481 | 2,079,239 |
| 3 | DuPAGE (22) | 17043 | 460,668 | 2,539,907 |
| 4 | WILL (99) | 17197 | 328,937 | 2,868,844 |
| 5 | LAKE (49) | 17097 | 313,558 | 3,182,402 |
| 6 | KANE (45) | 17089 | 222,364 | 3,404,766 |
| 7 | McHENRY (63) | 17111 | 163,082 | 3,567,848 |
| 8 | MADISON (57) | 17119 | 133,583 | 3,701,431 |
| 9 | ST. CLAIR (88) | 17163 | 113,913 | 3,815,344 |
| 10 | SANGAMON (83) | 17167 | 99,773 | 3,915,117 |
| 11 | CHAMPAIGN (10) | 17019 | 90,256 | 4,005,373 |
| 12 | PEORIA (72) | 17143 | 79,722 | 4,085,095 |
| 13 | WINNEBAGO (101) | 17201 | 70,014 | 4,155,109 |
| 14 | TAZEWELL (90) | 17179 | 68,442 | 4,223,551 |
| 15 | KENDALL (47) | 17093 | 66,549 | 4,290,100 |
| 16 | ROCK ISLAND (81) | 17161 | 63,679 | 4,353,779 |
| 17 | LaSALLE (50) | 17099 | 52,688 | 4,406,467 |
| 18 | CITY OF ROCKFORD (110) | 17201 | 52,004 | 4,458,471 |
| 19 | McLEAN (64) | 17113 | 49,617 | 4,508,088 |
| 20 | KANKAKEE (46) | 17091 | 47,785 | 4,555,873 |
| 21 | DeKALB (19) | 17037 | 47,570 | 4,603,443 |
| 22 | MACON (55) | 17115 | 45,509 | 4,648,952 |
| 23 | CITY OF BLOOMINGTON (104) | 17113 | 37,498 | 4,686,450 |
| 24 | WILLIAMSON (100) | 17199 | 33,174 | 4,719,624 |
| 25 | ADAMS (1) | 17001 | 31,900 | 4,751,524 |
| 26 | GRUNDY (32) | 17063 | 26,668 | 4,778,192 |
| 27 | WHITESIDE (98) | 17195 | 26,550 | 4,804,742 |
| 28 | OGLE (71) | 17141 | 25,900 | 4,830,642 |
| 29 | HENRY (37) | 17073 | 25,181 | 4,855,823 |
| 30 | BOONE (4) | 17007 | 24,357 | 4,880,180 |
| 31 | MACOUPIN (56) | 17117 | 23,503 | 4,903,683 |
| 32 | JACKSON (39) | 17077 | 22,582 | 4,926,265 |
| 33 | COLES (15) | 17029 | 21,613 | 4,947,878 |
| 34 | WOODFORD (102) | 17203 | 21,258 | 4,969,136 |
| 35 | STEPHENSON (89) | 17177 | 21,076 | 4,990,212 |
| 36 | MONROE (67) | 17133 | 21,014 | 5,011,226 |
| 37 | VERMILION (92) | 17183 | 20,719 | 5,031,945 |
| 38 | CLINTON (14) | 17027 | 19,306 | 5,051,251 |
| 39 | EFFINGHAM (25) | 17049 | 19,155 | 5,070,406 |
| 40 | FRANKLIN (28) | 17055 | 17,739 | 5,088,145 |
| 41 | MARION (58) | 17121 | 16,803 | 5,104,948 |
| 42 | JEFFERSON (41) | 17081 | 16,704 | 5,121,652 |
| 43 | LIVINGSTON (53) | 17105 | 16,621 | 5,138,273 |
| 44 | FULTON (29) | 17057 | 16,212 | 5,154,485 |
| 45 | LEE (52) | 17103 | 16,172 | 5,170,657 |
| 46 | BUREAU (6) | 17011 | 16,071 | 5,186,728 |
| 47 | CHRISTIAN (11) | 17021 | 15,600 | 5,202,328 |
| 48 | MORGAN (69) | 17137 | 14,649 | 5,216,977 |
| 49 | RANDOLPH (79) | 17157 | 14,373 | 5,231,350 |
| 50 | IROQUOIS (38) | 17075 | 13,354 | 5,244,704 |
| 51 | MONTGOMERY (68) | 17135 | 13,246 | 5,257,950 |
| 52 | LOGAN (54) | 17107 | 12,621 | 5,270,571 |
| 53 | JoDAVIESS (43) | 17085 | 12,472 | 5,283,043 |
| 54 | McDONOUGH (62) | 17109 | 12,025 | 5,295,068 |
| 55 | JERSEY (42) | 17083 | 11,743 | 5,306,811 |
| 56 | SHELBY (86) | 17173 | 11,703 | 5,318,514 |
| 57 | CITY OF GALESBURG (108) | 17095 | 11,639 | 5,330,153 |
| 58 | KNOX (48) | 17095 | 10,656 | 5,340,809 |
| 59 | SALINE (82) | 17165 | 10,629 | 5,351,438 |
| 60 | FAYETTE (26) | 17051 | 9,626 | 5,361,064 |
| 61 | PIATT (74) | 17147 | 9,546 | 5,370,610 |
| 62 | PERRY (73) | 17145 | 9,265 | 5,379,875 |
| 63 | HANCOCK (34) | 17067 | 9,106 | 5,388,981 |
| 64 | CRAWFORD (17) | 17033 | 8,954 | 5,397,935 |
| 65 | CITY OF DANVILLE (106) | 17183 | 8,932 | 5,406,867 |
| 66 | DOUGLAS (21) | 17041 | 8,448 | 5,415,315 |
| 67 | MERCER (66) | 17131 | 8,373 | 5,423,688 |
| 68 | WAYNE (96) | 17191 | 8,291 | 5,431,979 |
| 69 | UNION (91) | 17181 | 8,268 | 5,440,247 |
| 70 | CLARK (12) | 17023 | 8,228 | 5,448,475 |
| 71 | BOND (3) | 17005 | 8,016 | 5,456,491 |
| 72 | EDGAR (23) | 17045 | 7,928 | 5,464,419 |
| 73 | CARROLL (8) | 17015 | 7,857 | 5,472,276 |
| 74 | RICHLAND (80) | 17159 | 7,772 | 5,480,048 |
| 75 | DeWITT (20) | 17039 | 7,768 | 5,487,816 |
| 76 | WASHINGTON (95) | 17189 | 7,596 | 5,495,412 |
| 77 | PIKE (75) | 17149 | 7,525 | 5,502,937 |
| 78 | WARREN (94) | 17187 | 7,470 | 5,510,407 |
| 79 | WHITE (97) | 17193 | 7,085 | 5,517,492 |
| 80 | CLAY (13) | 17025 | 6,778 | 5,524,270 |
| 81 | MASSAC (61) | 17127 | 6,703 | 5,530,973 |
| 82 | CITY OF EAST ST. LOUIS (107) | 17163 | 6,659 | 5,537,632 |
| 83 | FORD (27) | 17053 | 6,575 | 5,544,207 |
| 84 | MOULTRIE (70) | 17139 | 6,547 | 5,550,754 |
| 85 | MENARD (65) | 17129 | 6,456 | 5,557,210 |
| 86 | MASON (60) | 17125 | 6,402 | 5,563,612 |
| 87 | MARSHALL (59) | 17123 | 6,154 | 5,569,766 |
| 88 | LAWRENCE (51) | 17101 | 6,126 | 5,575,892 |
| 89 | JOHNSON (44) | 17087 | 6,103 | 5,581,995 |
| 90 | GREENE (31) | 17061 | 6,075 | 5,588,070 |
| 91 | CUMBERLAND (18) | 17035 | 5,792 | 5,593,862 |
| 92 | JASPER (40) | 17079 | 5,438 | 5,599,300 |
| 93 | WABASH (93) | 17185 | 5,393 | 5,604,693 |
| 94 | CASS (9) | 17017 | 5,241 | 5,609,934 |
| 95 | HAMILTON (33) | 17065 | 4,194 | 5,614,128 |
| 96 | SCHUYLER (84) | 17169 | 3,767 | 5,617,895 |
| 97 | HENDERSON (36) | 17071 | 3,470 | 5,621,365 |
| 98 | PUTNAM (78) | 17155 | 3,348 | 5,624,713 |
| 99 | EDWARDS (24) | 17047 | 3,295 | 5,628,008 |
| 100 | STARK (87) | 17175 | 2,765 | 5,630,773 |
| 101 | CALHOUN (7) | 17013 | 2,684 | 5,633,457 |
| 102 | SCOTT (85) | 17171 | 2,592 | 5,636,049 |
| 103 | GALLATIN (30) | 17059 | 2,535 | 5,638,584 |
| 104 | BROWN (5) | 17009 | 2,465 | 5,641,049 |
| 105 | PULASKI (77) | 17153 | 2,386 | 5,643,435 |
| 106 | ALEXANDER (2) | 17003 | 2,276 | 5,645,711 |
| 107 | POPE (76) | 17151 | 2,135 | 5,647,846 |
| 108 | HARDIN (35) | 17069 | 1,933 | 5,649,779 |

**Complete 102 county named-vote aggregation order (separate sensitivity).** City observations are already inside these totals and are not added again. The native primary order and remainder remain in the linked full-order files above.

| Rank | County / FIPS | Named votes 2024 | Cumulative | Senate named votes 2022 | Ballots 2024 |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | COOK / 17031 | 2,079,239 | 2,079,239 | 1,441,922 | 2,108,301 |
| 2 | DuPAGE / 17043 | 456,882 | 2,536,121 | 341,740 | 464,364 |
| 3 | WILL / 17197 | 327,604 | 2,863,725 | 233,321 | 331,367 |
| 4 | LAKE / 17097 | 310,913 | 3,174,638 | 229,413 | 315,616 |
| 5 | KANE / 17089 | 223,534 | 3,398,172 | 157,941 | 225,945 |
| 6 | McHENRY / 17111 | 162,283 | 3,560,455 | 116,350 | 163,996 |
| 7 | MADISON / 17119 | 133,072 | 3,693,527 | 98,014 | 134,246 |
| 8 | WINNEBAGO / 17201 | 121,347 | 3,814,874 | 88,002 | 122,756 |
| 9 | ST. CLAIR / 17163 | 119,962 | 3,934,836 | 88,603 | 121,346 |
| 10 | SANGAMON / 17167 | 99,171 | 4,034,007 | 79,666 | 100,675 |
| 11 | CHAMPAIGN / 17019 | 89,581 | 4,123,588 | 67,794 | 91,038 |
| 12 | McLEAN / 17113 | 86,522 | 4,210,110 | 64,827 | 87,741 |
| 13 | PEORIA / 17143 | 79,138 | 4,289,248 | 59,035 | 80,332 |
| 14 | TAZEWELL / 17179 | 68,027 | 4,357,275 | 51,224 | 68,924 |
| 15 | KENDALL / 17093 | 66,397 | 4,423,672 | 45,265 | 66,808 |
| 16 | ROCK ISLAND / 17161 | 63,458 | 4,487,130 | 47,972 | 64,046 |
| 17 | LaSALLE / 17099 | 52,508 | 4,539,638 | 39,578 | 53,072 |
| 18 | KANKAKEE / 17091 | 47,569 | 4,587,207 | 35,108 | 48,173 |
| 19 | DeKALB / 17037 | 47,401 | 4,634,608 | 34,498 | 47,842 |
| 20 | MACON / 17115 | 45,341 | 4,679,949 | 35,243 | 45,791 |
| 21 | WILLIAMSON / 17199 | 33,068 | 4,713,017 | 25,112 | 33,346 |
| 22 | ADAMS / 17001 | 31,766 | 4,744,783 | 24,936 | 32,032 |
| 23 | VERMILION / 17183 | 29,549 | 4,774,332 | 21,962 | 29,819 |
| 24 | GRUNDY / 17063 | 26,589 | 4,800,921 | 19,370 | 26,788 |
| 25 | WHITESIDE / 17195 | 26,447 | 4,827,368 | 19,944 | 26,742 |
| 26 | OGLE / 17141 | 25,799 | 4,853,167 | 19,402 | 26,096 |
| 27 | HENRY / 17073 | 25,092 | 4,878,259 | 19,652 | 25,346 |
| 28 | BOONE / 17007 | 24,256 | 4,902,515 | 17,517 | 24,491 |
| 29 | MACOUPIN / 17117 | 23,425 | 4,925,940 | 17,748 | 23,647 |
| 30 | JACKSON / 17077 | 22,465 | 4,948,405 | 17,089 | 22,770 |
| 31 | KNOX / 17095 | 22,191 | 4,970,596 | 17,566 | 22,472 |
| 32 | COLES / 17029 | 21,507 | 4,992,103 | 16,487 | 21,733 |
| 33 | WOODFORD / 17203 | 21,123 | 5,013,226 | 16,873 | 21,390 |
| 34 | STEPHENSON / 17177 | 20,995 | 5,034,221 | 16,644 | 21,227 |
| 35 | MONROE / 17133 | 20,902 | 5,055,123 | 15,670 | 21,117 |
| 36 | CLINTON / 17027 | 19,230 | 5,074,353 | 14,773 | 19,425 |
| 37 | EFFINGHAM / 17049 | 19,084 | 5,093,437 | 15,842 | 19,266 |
| 38 | FRANKLIN / 17055 | 17,692 | 5,111,129 | 13,681 | 17,848 |
| 39 | MARION / 17121 | 16,762 | 5,127,891 | 12,898 | 16,895 |
| 40 | JEFFERSON / 17081 | 16,662 | 5,144,553 | 13,116 | 16,798 |
| 41 | LIVINGSTON / 17105 | 16,549 | 5,161,102 | 12,798 | 16,736 |
| 42 | FULTON / 17057 | 16,144 | 5,177,246 | 13,007 | 16,295 |
| 43 | LEE / 17103 | 16,113 | 5,193,359 | 12,002 | 16,290 |
| 44 | BUREAU / 17011 | 15,999 | 5,209,358 | 12,670 | 16,197 |
| 45 | CHRISTIAN / 17021 | 15,545 | 5,224,903 | 12,417 | 15,683 |
| 46 | MORGAN / 17137 | 14,677 | 5,239,580 | 11,027 | 14,830 |
| 47 | RANDOLPH / 17157 | 14,333 | 5,253,913 | 11,327 | 14,476 |
| 48 | IROQUOIS / 17075 | 13,324 | 5,267,237 | 10,438 | 13,428 |
| 49 | MONTGOMERY / 17135 | 13,203 | 5,280,440 | 10,589 | 13,350 |
| 50 | LOGAN / 17107 | 12,564 | 5,293,004 | 9,668 | 12,725 |
| 51 | JoDAVIESS / 17085 | 12,414 | 5,305,418 | 9,465 | 12,543 |
| 52 | McDONOUGH / 17109 | 11,972 | 5,317,390 | 9,386 | 12,132 |
| 53 | JERSEY / 17083 | 11,694 | 5,329,084 | 9,260 | 11,792 |
| 54 | SHELBY / 17173 | 11,670 | 5,340,754 | 9,667 | 11,775 |
| 55 | SALINE / 17165 | 10,605 | 5,351,359 | 8,047 | 10,714 |
| 56 | FAYETTE / 17051 | 9,601 | 5,360,960 | 8,005 | 9,681 |
| 57 | PIATT / 17147 | 9,508 | 5,370,468 | 7,615 | 9,612 |
| 58 | PERRY / 17145 | 9,248 | 5,379,716 | 7,759 | 9,329 |
| 59 | HANCOCK / 17067 | 9,065 | 5,388,781 | 7,202 | 9,166 |
| 60 | CRAWFORD / 17033 | 8,935 | 5,397,716 | 6,943 | 9,027 |
| 61 | DOUGLAS / 17041 | 8,410 | 5,406,126 | 6,451 | 8,493 |
| 62 | MERCER / 17131 | 8,346 | 5,414,472 | 6,732 | 8,422 |
| 63 | WAYNE / 17191 | 8,275 | 5,422,747 | 6,765 | 8,326 |
| 64 | UNION / 17181 | 8,226 | 5,430,973 | 6,965 | 8,333 |
| 65 | CLARK / 17023 | 8,206 | 5,439,179 | 6,316 | 8,261 |
| 66 | BOND / 17005 | 7,991 | 5,447,170 | 6,393 | 8,087 |
| 67 | EDGAR / 17045 | 7,912 | 5,455,082 | 6,052 | 7,991 |
| 68 | CARROLL / 17015 | 7,840 | 5,462,922 | 5,953 | 7,922 |
| 69 | DeWITT / 17039 | 7,758 | 5,470,680 | 6,080 | 7,815 |
| 70 | RICHLAND / 17159 | 7,755 | 5,478,435 | 6,205 | 7,819 |
| 71 | WASHINGTON / 17189 | 7,562 | 5,485,997 | 5,963 | 7,661 |
| 72 | PIKE / 17149 | 7,509 | 5,493,506 | 6,024 | 7,560 |
| 73 | WARREN / 17187 | 7,447 | 5,500,953 | 5,854 | 7,517 |
| 74 | WHITE / 17193 | 7,067 | 5,508,020 | 5,679 | 7,120 |
| 75 | CLAY / 17025 | 6,769 | 5,514,789 | 5,737 | 6,810 |
| 76 | MASSAC / 17127 | 6,676 | 5,521,465 | 4,862 | 6,736 |
| 77 | FORD / 17053 | 6,553 | 5,528,018 | 5,134 | 6,615 |
| 78 | MOULTRIE / 17139 | 6,528 | 5,534,546 | 5,250 | 6,586 |
| 79 | MENARD / 17129 | 6,431 | 5,540,977 | 5,284 | 6,499 |
| 80 | MASON / 17125 | 6,374 | 5,547,351 | 4,967 | 6,445 |
| 81 | MARSHALL / 17123 | 6,127 | 5,553,478 | 4,738 | 6,199 |
| 82 | LAWRENCE / 17101 | 6,110 | 5,559,588 | 5,025 | 6,159 |
| 83 | JOHNSON / 17087 | 6,103 | 5,565,691 | 4,813 | 6,164 |
| 84 | GREENE / 17061 | 6,056 | 5,571,747 | 4,523 | 6,135 |
| 85 | CUMBERLAND / 17035 | 5,769 | 5,577,516 | 4,763 | 5,810 |
| 86 | JASPER / 17079 | 5,425 | 5,582,941 | 4,575 | 5,468 |
| 87 | WABASH / 17185 | 5,377 | 5,588,318 | 4,039 | 5,423 |
| 88 | CASS / 17017 | 5,241 | 5,593,559 | 3,932 | 5,286 |
| 89 | HAMILTON / 17065 | 4,181 | 5,597,740 | 3,398 | 4,234 |
| 90 | SCHUYLER / 17169 | 3,759 | 5,601,499 | 3,122 | 3,794 |
| 91 | HENDERSON / 17071 | 3,464 | 5,604,963 | 2,909 | 3,494 |
| 92 | PUTNAM / 17155 | 3,334 | 5,608,297 | 2,745 | 3,389 |
| 93 | EDWARDS / 17047 | 3,289 | 5,611,586 | 2,783 | 3,311 |
| 94 | STARK / 17175 | 2,761 | 5,614,347 | 2,310 | 2,782 |
| 95 | CALHOUN / 17013 | 2,680 | 5,617,027 | 2,331 | 2,704 |
| 96 | SCOTT / 17171 | 2,587 | 5,619,614 | 2,083 | 2,606 |
| 97 | GALLATIN / 17059 | 2,530 | 5,622,144 | 2,165 | 2,570 |
| 98 | BROWN / 17009 | 2,455 | 5,624,599 | 1,897 | 2,487 |
| 99 | PULASKI / 17153 | 2,381 | 5,626,980 | 1,986 | 2,406 |
| 100 | ALEXANDER / 17003 | 2,271 | 5,629,251 | 1,707 | 2,293 |
| 101 | POPE / 17151 | 2,133 | 5,631,384 | 1,646 | 2,151 |
| 102 | HARDIN / 17069 | 1,926 | 5,633,310 | 1,650 | 1,955 |
