# Kansas turnout concentration

Research snapshot: **October 18, 2026 UTC**. The priority baseline is the **November 5, 2024 presidential contest**, using the four tickets actually reported in the Kansas Secretary of State (SOS) statewide canvass. Kansas held no U.S. Senate election in 2024. Roger Marshall–Barbara Bollier–Jason Buckley in **2020** is the prior election for the **Class II seat** contested in 2026; Jerry Moran–Mark R. Holland–David C Graham in **2022** is the other **Class III seat** and the actual recent midterm comparator. The [SOS results index](https://www.sos.ks.gov/elections/election-results.html) presents those elections separately, and the Senate's [Class II](https://www.senate.gov/senators/Class_II.htm) and [Class III](https://www.senate.gov/senators/Class_III.htm) rosters confirm the seat cycles. The [current SOS dates page](https://www.sos.ks.gov/elections/important-election-dates.html) identifies November 3, 2026 as the general election. No nonexistent 2024 Senate or governor contest is substituted.

**Top 15:** Johnson, Sedgwick, Shawnee, Douglas, Wyandotte, Leavenworth, Butler, Reno, Riley, Saline, Miami, Crawford, Harvey, McPherson and Ellis supply **970,376 / 1,327,591 = 73.0929932487%** of the source-reported presidential candidate votes.

**Minimum descending set reaching 80%: 23 counties**, in this exact order: **Johnson, Sedgwick, Shawnee, Douglas, Wyandotte, Leavenworth, Butler, Reno, Riley, Saline, Miami, Crawford, Harvey, McPherson, Ellis, Cowley, Pottawatomie, Lyon, Franklin, Montgomery, Finney, Barton, Sumner**. They supply **1,067,659 / 1,327,591 = 80.4207771821%**. The preceding **22 counties supply 1,057,110 = 79.6261800509%**. **Sumner (FIPS 20191), 10,549 votes, crosses the threshold.** Integer checks are `5 × 1,057,110 < 4 × 1,327,591 ≤ 5 × 1,067,659`; therefore no set of only 22 counties can reach 80%. The top 15 are already in this set. The **82 remaining counties supply 259,932 votes, 19.5792228179%**, and remain in every statewide total. Counts derive from the [broader SOS presidential workbook](https://www.sos.ks.gov/elections/24elec/2024-Presidential-Results.xlsx), independently checked county by county and candidate by candidate against the [SOS precinct workbook](https://www.sos.ks.gov/elections/24elec/2024-General-Election-President-Precinct-Level-Results.xlsx) and [statewide official canvass](https://www.sos.ks.gov/elections/24elec/2024-General-Election-Official-Vote-Totals.pdf).

The [dispatch contract](data/turnout/priority-set.json) contains all 105 ordered county keys, ordered priority/remainder keys, every retained source-native constituent and explicit unavailable cases. **Primary reconciliation and independent peer agreement are complete. The coordinator has accepted this research dispatch in the authoritative [external acceptance record](data/coordinator-priority-acceptance.json).** This historical research set does not approve current precinct boundaries or a November results crosswalk. [Peer agreement](data/turnout/peer-agreement.json) records the actual independent worker ID and the exact compared assets.

## Denominator and candidate universe

Candidate votes are not ballots cast. The primary denominator is **1,327,591**, comprising Harris/Walz **544,853**, Trump/Vance **758,802**, Kennedy/Shanahan **16,322**, and Oliver/ter Maat **7,614**. The [SOS canvass](https://www.sos.ks.gov/elections/24elec/2024-General-Election-Official-Vote-Totals.pdf) and [House Clerk publication](https://clerk.house.gov/member_info/electionInfo/2024/statistics2024.pdf) report these same four tickets. Every one of the 105 counties agrees between the two SOS Excel presentations for each ticket; the county sums exactly reproduce each statewide PDF control. Source party capitalization and ticket spelling remain intact in raw extracts.

The statewide source files do **not** publish a presidential write-in category, named write-in list, under/overvotes or blank ballots. Those fields are **unavailable**, not zero. The exact percentage and order above apply to this four-ticket universe; they are not represented as an independently established ranking including every county's generic or legally valid write-in vote. A generic tabulator write-in is not automatically a valid vote for a filed write-in candidate. [K.S.A. 25-3002(b)(5)–(6)](https://www.kslegislature.gov/b2025_26/laws/025_000_0000_chapter/025_030_0000_article/025_030_0002_section/025_030_0002_k/) requires filed candidacy and other applicable conditions. A complete statewide 2024 named-valid/generic write-in reconciliation remains a precise scope gap, without allocating any ballot residual to it.

The [2020 Senate workbook](https://www.sos.ks.gov/elections/20elec/2020_General_Election_US_Senate_results_by_precinct.xlsx) separately publishes generic write-ins in Shawnee (**94**), Sedgwick (**242**) and Wyandotte (**120**). These **456** partial-state generic votes are retained alongside their native rows and footer observations, outside the three named candidates' statewide **1,367,755** denominator. The other 102 counties have no generic-write-in field in that workbook, so 456 is not a statewide valid-write-in control. Sedgwick's contest-specific `Total Votes Cast` is **222,419 = 222,177 named + 242 generic write-ins**, not a county ballot count. Johnson's 2020 header code `NON` is retained separately from the verified D/R/L candidate identities. Wyandotte's comma-formatted `Totals` row 131 is retained, as are its unrelated presidential column and repeated headers in the lossless row extract.

All named candidate controls, independently extracted from the [2024](https://www.sos.ks.gov/elections/24elec/2024-General-Election-Official-Vote-Totals.pdf), [2022](https://www.sos.ks.gov/elections/22elec/2022-General-Official-Vote-Totals.pdf), [2020](https://www.sos.ks.gov/elections/20elec/2020_General_Official_Vote_Totals.pdf) and [2026 primary](https://www.sos.ks.gov/elections/26elec/2026-Primary-Election-Official-Vote-Totals.pdf) canvasses:

| Contest | Source candidate label | Party | State PDF control | Sum of 105 counties | Difference |
| --- | --- | --- | ---: | ---: | ---: |
| president_2024 | Donald J. Trump / JD Vance | R | 758,802 | 758,802 | 0 |
| president_2024 | Kamala D. Harris / Tim Walz | D | 544,853 | 544,853 | 0 |
| president_2024 | Robert F. Kennedy Jr./ Nicole Shanahan | i | 16,322 | 16,322 | 0 |
| president_2024 | Chase Oliver / Mike ter Maat | L | 7,614 | 7,614 | 0 |
| senate_2022 | Jerry Moran | R | 602,976 | 602,976 | 0 |
| senate_2022 | Mark R. Holland | D | 372,214 | 372,214 | 0 |
| senate_2022 | David C Graham | L | 29,766 | 29,766 | 0 |
| senate_2020 | Roger Marshall | R | 727,962 | 727,962 | 0 |
| senate_2020 | Barbara Bollier | D | 571,530 | 571,530 | 0 |
| senate_2020 | Jason Buckley | L | 68,263 | 68,263 | 0 |
| senate_primary_2026 | Damon Anderson | D | 5,879 | 5,879 | 0 |
| senate_primary_2026 | Christy Davis | D | 31,857 | 31,857 | 0 |
| senate_primary_2026 | Adam Hamilton | D | 77,607 | 77,607 | 0 |
| senate_primary_2026 | Jason Hart | D | 12,412 | 12,412 | 0 |
| senate_primary_2026 | Kevin Latz | D | 4,110 | 4,110 | 0 |
| senate_primary_2026 | Erik Murray | D | 15,177 | 15,177 | 0 |
| senate_primary_2026 | Sandy Spidel Neumann | D | 12,717 | 12,717 | 0 |
| senate_primary_2026 | Anne Parelkar | D | 16,836 | 16,836 | 0 |
| senate_primary_2026 | Patrick C. Schmidt | D | 13,403 | 13,403 | 0 |
| senate_primary_2026 | Michael "Mike" Soetaert | D | 3,716 | 3,716 | 0 |
| senate_primary_2026 | Noah Taylor | D | 30,362 | 30,362 | 0 |
| senate_primary_2026 | Roger Marshall | R | 270,632 | 270,632 | 0 |
| senate_primary_2026 | Pond Naramore | R | 68,100 | 68,100 | 0 |

## Complete county order

The compatibility filename [county-turnout.csv](data/county-turnout.csv) genuinely contains county parents here: all **105 Kansas counties**, with five-character [Census county FIPS](https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt) and `US-KS-<FIPS>` keys. Municipal/city/ward/township labels in native precinct files remain constituents; they are not substituted for counties. Kansas City, Missouri election authorities have no role in these Kansas totals. Ordering is descending integer votes, with ascending FIPS as the documented tie-break; there are no county ties. Source: [SOS broader workbook](https://www.sos.ks.gov/elections/24elec/2024-Presidential-Results.xlsx).

| Rank | County | FIPS | 2024 presidential votes | Cumulative votes | Cumulative share | Membership |
| ---: | --- | --- | ---: | ---: | ---: | --- |
| 1 | Johnson | 20091 | 343,780 | 343,780 | 25.89502339% | top15 / priority |
| 2 | Sedgwick | 20173 | 214,152 | 557,932 | 42.02589502% | top15 / priority |
| 3 | Shawnee | 20177 | 81,819 | 639,751 | 48.18886238% | top15 / priority |
| 4 | Douglas | 20045 | 58,041 | 697,792 | 52.56076608% | top15 / priority |
| 5 | Wyandotte | 20209 | 50,602 | 748,394 | 56.37233154% | top15 / priority |
| 6 | Leavenworth | 20103 | 36,547 | 784,941 | 59.12521251% | top15 / priority |
| 7 | Butler | 20015 | 32,236 | 817,177 | 61.55336998% | top15 / priority |
| 8 | Reno | 20155 | 26,940 | 844,117 | 63.58260940% | top15 / priority |
| 9 | Riley | 20161 | 24,313 | 868,430 | 65.41397162% | top15 / priority |
| 10 | Saline | 20169 | 23,226 | 891,656 | 67.16345622% | top15 / priority |
| 11 | Miami | 20121 | 18,685 | 910,341 | 68.57089269% | top15 / priority |
| 12 | Crawford | 20037 | 16,334 | 926,675 | 69.80124150% | top15 / priority |
| 13 | Harvey | 20079 | 16,086 | 942,761 | 71.01290985% | top15 / priority |
| 14 | McPherson | 20113 | 14,104 | 956,865 | 72.07528523% | top15 / priority |
| 15 | Ellis | 20051 | 13,511 | 970,376 | 73.09299325% | top15 / priority |
| 16 | Cowley | 20035 | 13,505 | 983,881 | 74.11024932% | priority |
| 17 | Pottawatomie | 20149 | 13,472 | 997,353 | 75.12501968% | priority |
| 18 | Lyon | 20111 | 13,256 | 1,010,609 | 76.12351997% | priority |
| 19 | Franklin | 20059 | 12,708 | 1,023,317 | 77.08074249% | priority |
| 20 | Montgomery | 20125 | 12,441 | 1,035,758 | 78.01785339% | priority |
| 21 | Finney | 20055 | 10,782 | 1,046,540 | 78.83000111% | priority |
| 22 | Barton | 20009 | 10,570 | 1,057,110 | 79.62618005% | priority |
| 23 | Sumner | 20191 | 10,549 | 1,067,659 | 80.42077718% | priority |
| 24 | Jefferson | 20087 | 9,927 | 1,077,586 | 81.16852253% | remainder |
| 25 | Geary | 20061 | 9,163 | 1,086,749 | 81.85872004% | remainder |
| 26 | Dickinson | 20041 | 9,144 | 1,095,893 | 82.54748639% | remainder |
| 27 | Cherokee | 20021 | 8,717 | 1,104,610 | 83.20408921% | remainder |
| 28 | Ford | 20057 | 8,224 | 1,112,834 | 83.82355710% | remainder |
| 29 | Labette | 20099 | 7,921 | 1,120,755 | 84.42020170% | remainder |
| 30 | Osage | 20139 | 7,892 | 1,128,647 | 85.01466190% | remainder |
| 31 | Atchison | 20005 | 7,255 | 1,135,902 | 85.56114044% | remainder |
| 32 | Neosho | 20133 | 6,784 | 1,142,686 | 86.07214119% | remainder |
| 33 | Bourbon | 20011 | 6,572 | 1,149,258 | 86.56717317% | remainder |
| 34 | Jackson | 20085 | 6,474 | 1,155,732 | 87.05482336% | remainder |
| 35 | Marion | 20115 | 5,870 | 1,161,602 | 87.49697761% | remainder |
| 36 | Nemaha | 20131 | 5,620 | 1,167,222 | 87.92030076% | remainder |
| 37 | Allen | 20001 | 5,600 | 1,172,822 | 88.34211741% | remainder |
| 38 | Linn | 20107 | 5,016 | 1,177,838 | 88.71994462% | remainder |
| 39 | Marshall | 20117 | 4,968 | 1,182,806 | 89.09415626% | remainder |
| 40 | Seward | 20175 | 4,565 | 1,187,371 | 89.43801216% | remainder |
| 41 | Coffey | 20031 | 4,377 | 1,191,748 | 89.76770707% | remainder |
| 42 | Brown | 20013 | 4,258 | 1,196,006 | 90.08843838% | remainder |
| 43 | Clay | 20027 | 4,113 | 1,200,119 | 90.39824765% | remainder |
| 44 | Pratt | 20151 | 4,082 | 1,204,201 | 90.70572187% | remainder |
| 45 | Cloud | 20029 | 4,047 | 1,208,248 | 91.01055973% | remainder |
| 46 | Rice | 20159 | 3,966 | 1,212,214 | 91.30929631% | remainder |
| 47 | Kingman | 20095 | 3,947 | 1,216,161 | 91.60660173% | remainder |
| 48 | Wabaunsee | 20197 | 3,836 | 1,219,997 | 91.89554614% | remainder |
| 49 | Anderson | 20003 | 3,791 | 1,223,788 | 92.18110096% | remainder |
| 50 | Thomas | 20193 | 3,664 | 1,227,452 | 92.45708957% | remainder |
| 51 | Wilson | 20205 | 3,603 | 1,231,055 | 92.72848340% | remainder |
| 52 | Doniphan | 20043 | 3,577 | 1,234,632 | 92.99791879% | remainder |
| 53 | Russell | 20167 | 3,301 | 1,237,933 | 93.24656464% | remainder |
| 54 | Mitchell | 20123 | 3,172 | 1,241,105 | 93.48549365% | remainder |
| 55 | Ottawa | 20143 | 3,003 | 1,244,108 | 93.71169283% | remainder |
| 56 | Greenwood | 20073 | 2,884 | 1,246,992 | 93.92892841% | remainder |
| 57 | Morris | 20127 | 2,792 | 1,249,784 | 94.13923415% | remainder |
| 58 | Ellsworth | 20053 | 2,758 | 1,252,542 | 94.34697885% | remainder |
| 59 | Phillips | 20147 | 2,747 | 1,255,289 | 94.55389499% | remainder |
| 60 | Washington | 20201 | 2,700 | 1,257,989 | 94.75727088% | remainder |
| 61 | Pawnee | 20145 | 2,675 | 1,260,664 | 94.95876366% | remainder |
| 62 | Sherman | 20181 | 2,593 | 1,263,257 | 95.15407983% | remainder |
| 63 | Harper | 20077 | 2,555 | 1,265,812 | 95.34653368% | remainder |
| 64 | Rooks | 20163 | 2,534 | 1,268,346 | 95.53740572% | remainder |
| 65 | Republic | 20157 | 2,443 | 1,270,789 | 95.72142324% | remainder |
| 66 | Norton | 20137 | 2,270 | 1,273,059 | 95.89240964% | remainder |
| 67 | Grant | 20067 | 2,220 | 1,275,279 | 96.05962981% | remainder |
| 68 | Gray | 20069 | 2,193 | 1,277,472 | 96.22481623% | remainder |
| 69 | Barber | 20007 | 2,170 | 1,279,642 | 96.38827018% | remainder |
| 70 | Scott | 20171 | 2,135 | 1,281,777 | 96.54908778% | remainder |
| 71 | Smith | 20183 | 2,006 | 1,283,783 | 96.70018854% | remainder |
| 72 | Stafford | 20185 | 1,909 | 1,285,692 | 96.84398282% | remainder |
| 73 | Stevens | 20189 | 1,835 | 1,287,527 | 96.98220310% | remainder |
| 74 | Osborne | 20141 | 1,774 | 1,289,301 | 97.11582859% | remainder |
| 75 | Meade | 20119 | 1,695 | 1,290,996 | 97.24350346% | remainder |
| 76 | Rush | 20165 | 1,606 | 1,292,602 | 97.36447445% | remainder |
| 77 | Trego | 20195 | 1,587 | 1,294,189 | 97.48401428% | remainder |
| 78 | Jewell | 20089 | 1,574 | 1,295,763 | 97.60257489% | remainder |
| 79 | Chautauqua | 20019 | 1,527 | 1,297,290 | 97.71759525% | remainder |
| 80 | Lincoln | 20105 | 1,507 | 1,298,797 | 97.83110913% | remainder |
| 81 | Woodson | 20207 | 1,506 | 1,300,303 | 97.94454768% | remainder |
| 82 | Chase | 20017 | 1,462 | 1,301,765 | 98.05467196% | remainder |
| 83 | Decatur | 20039 | 1,452 | 1,303,217 | 98.16404299% | remainder |
| 84 | Cheyenne | 20023 | 1,422 | 1,304,639 | 98.27115429% | remainder |
| 85 | Rawlins | 20153 | 1,403 | 1,306,042 | 98.37683443% | remainder |
| 86 | Logan | 20109 | 1,400 | 1,307,442 | 98.48228860% | remainder |
| 87 | Gove | 20063 | 1,396 | 1,308,838 | 98.58744146% | remainder |
| 88 | Sheridan | 20179 | 1,373 | 1,310,211 | 98.69086187% | remainder |
| 89 | Ness | 20135 | 1,363 | 1,311,574 | 98.79352903% | remainder |
| 90 | Elk | 20049 | 1,338 | 1,312,912 | 98.89431308% | remainder |
| 91 | Kearny | 20093 | 1,301 | 1,314,213 | 98.99231013% | remainder |
| 92 | Graham | 20065 | 1,287 | 1,315,500 | 99.08925264% | remainder |
| 93 | Haskell | 20081 | 1,278 | 1,316,778 | 99.18551723% | remainder |
| 94 | Edwards | 20047 | 1,269 | 1,318,047 | 99.28110389% | remainder |
| 95 | Kiowa | 20097 | 1,107 | 1,319,154 | 99.36448801% | remainder |
| 96 | Morton | 20129 | 1,060 | 1,320,214 | 99.44433188% | remainder |
| 97 | Clark | 20025 | 1,014 | 1,321,228 | 99.52071082% | remainder |
| 98 | Hodgeman | 20083 | 966 | 1,322,194 | 99.59347419% | remainder |
| 99 | Comanche | 20033 | 874 | 1,323,068 | 99.65930772% | remainder |
| 100 | Wichita | 20203 | 860 | 1,323,928 | 99.72408671% | remainder |
| 101 | Lane | 20101 | 843 | 1,324,771 | 99.78758518% | remainder |
| 102 | Hamilton | 20075 | 815 | 1,325,586 | 99.84897457% | remainder |
| 103 | Wallace | 20199 | 748 | 1,326,334 | 99.90531723% | remainder |
| 104 | Stanton | 20187 | 664 | 1,326,998 | 99.95533263% | remainder |
| 105 | Greeley | 20071 | 593 | 1,327,591 | 100.00000000% | remainder |

## Native identities and disjoint arithmetic

The broad workbook is **not** a county-only table: its first sheet contains **18,268 candidate rows**, four per **4,567 exact A:F contexts** (Congressional district, Kansas Senate district, Kansas House district, location, literal county and precinct). All integers, including **828 zero-total contexts**, remain present. The literal county `Comanche ` has a trailing space; only the explicit alias `Comanche ` → `Comanche` is used for the county join. Both original spellings remain inspectable. Those contexts form one complete additive view of the four-ticket vote count. Source: [original broad workbook](https://www.sos.ks.gov/elections/24elec/2024-Presidential-Results.xlsx).

An alternative descending ranking at that native-context granularity has **36,633 / 1,327,591 = 2.7593588688%** in its top 15. The minimum **1,477** contexts reach **1,062,208 = 80.0101838593%**; the preceding **1,476** have **1,061,886**. Saline's **Elm Creek H107**, **322** votes (broad rows **12942–12945**), is the crossing context under the documented tie rule. The remaining **3,090** contexts contain **265,383** votes. [Exact native ranking](data/turnout/native-ranking-2024.json) and [all-source native order](data/turnout/extracts/native-unit-order.csv.gz) retain the entire order. This is an alternative partition, never added to county totals or used to claim 4,567 approved 2026 polygons.

Each precinct workbook's main sheet covers **101 counties**. Johnson, Sedgwick, Shawnee and Wyandotte are supplied by **four complementary sheets**; `COUNTY TOTALS`/`Totals` rows are source controls and are excluded from native detail sums. The combined county controls reconcile every statewide candidate. Alternative presentations and different years remain separate source families. Native source code, VTD, label, sheet, row and column are retained; no cross-year or November 2026 identity/geometry equivalence is inferred from matching names or counts. The [native inventory](data/turnout/native-inventory.json), [candidate observations](data/turnout/extracts/candidate-observations.jsonl.gz) and [native county reconciliation](data/turnout/extracts/native-county-reconciliation.csv) expose the complete source scope.

| Original source family | Retained identities | Complete integer units | Units with blank/redacted cells | Complete zero-total units |
| --- | ---: | ---: | ---: | ---: |
| 2024 broad A:F contexts | 4,567 | 4,567 | 0 | 828 |
| 2024 precinct workbook | 4,566 | 4,553 | 13 | 815 |
| 2022 Senate precinct workbook | 4,535 | 4,523 | 12 | 786 |
| 2020 Senate precinct workbook | 3,867 | 3,848 | 19 | 444 |
| 2026 Senate primary precinct workbook | 4,496 | 4,465 | 31 | 790 |

The **22,031 identities** above are across overlapping source families, not 22,031 disjoint precincts. In the [2024 precinct file](https://www.sos.ks.gov/elections/24elec/2024-General-Election-President-Precinct-Level-Results.xlsx), numeric native detail is **44 votes below Shawnee's footer** (Harris 17, Trump 27); eight Shawnee rows cite `KSA 25-2701(a)(2)`. Five further main-sheet identities have blank candidate cells. The [2022 file](https://www.sos.ks.gov/elections/22elec/2022-General-Election-US-Senate-Results-By-Precinct.xlsx) has an **8-vote Wyandotte difference** (Holland 3, Moran 5) across four redacted identities, plus eight blank main-sheet identities. The [2020 file](https://www.sos.ks.gov/elections/20elec/2020_General_Election_US_Senate_results_by_precinct.xlsx) has 19 blank identities with no positive aggregate residual. The [2026 primary file](https://www.sos.ks.gov/elections/26elec/2026-Primary-Election-United-States-Senate-Precinct-Level-Results.xlsx) has a **22-vote Shawnee difference** (Davis 1, Hamilton 7, Schmidt 3, Taylor 2, Marshall 8, Naramore 1) and 31 unavailable identities. These differences stay at county-control level, unallocated. Even a zero aggregate residual does not turn individual blank cells into published zeros. Incomplete native units remain explicitly unranked in the numerical native order.

These statewide contest files provide combined voting-method totals, without separate central absentee, advance, Election Day or provisional candidate groups. A precinct named `Central` is not classified as a counting board from its name. Polling locations, vote centers, ballot styles and VTD polygons are not asserted equivalent to a source reporting row. The contract explicitly records unavailable administrative/method identities and unverified geometry. Historical identity inventory is complete within the retained original files; a current approved crosswalk remains a separate assignment.

## Actual midterm and denominator sensitivities

The [2022 Senate comparator](https://www.sos.ks.gov/elections/22elec/2022-General-Election-US-Senate-Results-By-Precinct.xlsx) totals **1,004,956 named votes**: Moran 602,976, Holland 372,214, Graham 29,766. Its independently ranked top 15 contribute **730,579 = 72.6976106417%**. Its minimum 23 counties contribute **804,164 = 80.0198217633%**; the preceding 22 have **796,570**, and **Jefferson's 7,594** crosses. Compared with the 2024 presidential priority, this midterm minimum replaces **Finney with Jefferson**. Holding the 2024 priority membership fixed gives **803,730 / 1,004,956 = 79.9766357930%** in 2022. County composition changes even when the minimum count remains 23.

The [2020 Class II Senate baseline](https://www.sos.ks.gov/elections/20elec/2020_General_Election_US_Senate_results_by_precinct.xlsx) totals **1,367,755 named votes**; its top 15 contribute **997,566 = 72.9345533374%**, and its minimum 23 supply **1,097,741 = 80.2585989450%**. The first 22 have **1,086,829**; Sumner's **10,912** crosses. Its 23-county membership equals the 2024 presidential set, with a different internal order. These comparisons change election year, candidates and contest; they do not isolate participation effects or forecast 2026.

Each following line is independently ranked on its stated denominator. Full orders and all preceding/crossing/remainder arithmetic are in [rankings.json](data/turnout/rankings.json). The 2024 ballot/registration inputs come from the [broad workbook](https://www.sos.ks.gov/elections/24elec/2024-Presidential-Results.xlsx); the raw 2022 measures from the [SOS turnout workbook](https://www.sos.ks.gov/elections/22elec/2022-General-Election-Turnout-Information.xlsx); and the separate registration vintages from [November 2024](https://www.sos.ks.gov/elections/vr-statistics/2024/11-2024-Voter-Registration-Numbers-by-County.xlsx), [October 2026 registration](https://www.sos.ks.gov/elections/vr-statistics/2026/10-2026-Voter-Registration-Numbers-by-County.xlsx) and [October 2026 active/inactive](https://www.sos.ks.gov/elections/vr-statistics/2026/Inactive-Voters/2026-10-01-Percentage-of-Inactive-Voters-by-County.xlsx) publications.

| Measure / source scope | State total | Top-15 volume | Top-15 share | Minimum 80% count | Crossing cumulative volume | Crossing share |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2024 president, four reported tickets | 1,327,591 | 970,376 | 73.0929932487% | 23 | 1,067,659 | 80.4207771821% |
| 2022 Senate, three reported candidates | 1,004,956 | 730,579 | 72.6976106417% | 23 | 804,164 | 80.0198217633% |
| 2020 Senate, three reported candidates | 1,367,755 | 997,566 | 72.9345533374% | 23 | 1,097,741 | 80.2585989450% |
| 2024 ballots, broad workbook vintage | 1,343,020 | 982,420 | 73.1500647794% | 23 | 1,080,577 | 80.4587422376% |
| 2022 ballots, inconsistent raw workbook only | 1,020,208 | 740,917 | 72.6241119458% | 23 | 816,652 | 80.0475981369% |
| November 2024 registration | 2,031,132 | 1,468,036 | 72.2767402611% | 24 | 1,641,501 | 80.8170517721% |
| October 1, 2026 total registration | 2,027,520 | 1,468,058 | 72.4065853851% | 23 | 1,624,936 | 80.1440183081% |
| October 1, 2026 active registration | 1,752,611 | 1,265,185 | 72.1885803524% | 24 | 1,414,545 | 80.7107224592% |

The **2024 ballot** minimum has the same 23-county membership as the candidate priority but swaps Ellis/Cowley within its top 15. Its denominator **1,343,020** is **15,429** above the reported-ticket count; that subtraction is an unresolved denominator difference, not an estimated undervote or write-in count. The broad sheet labels registration **2,031,120**, without a registration-status breakdown or explicit as-of date. It must not be called active or voting-eligible registration.

The **December 3, 2024 SOS certification release**, describing the December 2 canvass, reports **1,344,147** voters/ballots (**137,644 by mail + 557,209 advance in person + 649,294 Election Day**) and **2,031,132 registered voters**. Those are respectively **1,127 ballots and 12 registrations above** the broad workbook. The separate November registration table's 105 counties sum to **2,031,132**, matching the release's registration total; county values still differ from the broad sheet and no common registration date/status is assumed. Both original vintages are retained. No county ballot allocation or cause is invented. A clean county allocation of the release's **1,344,147** total remains unavailable. Source: [official certification announcement](https://sos.ks.gov/media/press-releases/2024/12-03-24-state-board-of-canvassers-certifies-kansas-general-election-results.html).

The **2022 turnout workbook is internally inconsistent** despite exact column/footer sums (**1,020,208 ballots; 1,975,535 registrations**). Stevens lists **7,979 ballots > 3,246 registrations**. Sumner lists **1,403 ballots < 7,869 named Senate votes**. The candidate count also exceeds the listed ballots in **Rice (3,096 > 3,027), Wilson (3,322 > 3,107), Phillips (2,199 > 2,191), and Washington (2,240 > 2,002)**. Its raw ballot ranking is retained for reproducibility and explicitly excluded as a clean midterm turnout weight. No apparent county swap or other correction is imposed. The mail-return column sums its available integers to the printed **129,973**, but **Bourbon, Cherokee, Osage and Rice say `N/A`**; these are not zeros or a complete 105-county mail control. Source: [unaltered SOS 2022 turnout workbook](https://www.sos.ks.gov/elections/22elec/2022-General-Election-Turnout-Information.xlsx).

A supplemental primary county check resolves **Sumner alone**: the actual [county archive](https://co.sumner.ks.us/elected_officials/county_clerk_and_election_officer/election_results.php) links its [official November 8, 2022 summary](https://webgen1files1.revize.com/sumnercountryks/Documents/Elected%20Officials/County%20Clerk%20and%20Election%20Officer/Election%20Results/official%20election%20summary%20w%20writeins.pdf?t=202309010533350), timestamped **November 17, 2022, 1:11 PM** (timezone unspecified). Independently reading pages 1–2 confirms **7,932 ballots**, **four blank ballots**, and the same named Senate counts (**Moran 5,896; Graham 281; Holland 1,692 = 7,869**). It reports **three generic write-ins**, **60 undervotes**, **zero overvotes**, **7,872 Total Votes Cast** and **7,932 Contest Totals**. Its six literal method labels—**Election Day, Absentee, Wednesday, Thursday, Monday, Provisional**—have ballot/contest totals **6,117; 1,720; 4; 5; 1; 85**, summing to 7,932; `Absentee` is not silently renamed mail. The [external supplemental control](data/news/sumner-2022-control.json) retains those distinctions and the original authority/download chain. This directly conflicts with the SOS turnout workbook's 1,403, but does not explain its error, establish a Sumner/Stevens swap, repair other counties or change the accepted statewide native-family contract.

The [SOS historical statistics table](https://www.sos.ks.gov/elections/election-statistics-data.html) separately reports **1,375,125** 2020 participating voters/ballots and **1,938,560** registered voters, with **459,229 mail + 371,854 advance in person + 544,042 Election Day = 1,375,125**. Its **45,671 provisional ballots cast** are a separate administrative field, not an additional nonoverlapping term to add. The 2020 ballot-type total is **7,370** above the named Senate denominator, without a published statewide decomposition into write-ins/under/over. This is statewide context; no county ballot vector is manufactured from it.

The October 2026 workbooks internally date their records **2026-10-01**: **2,027,520 total registered = 1,752,611 active + 274,909 inactive**, reconciled across all 105 counties. Their party columns are registration affiliations, not cast-vote choices. Total and active registration produce different geographic priorities, as the table shows. Registration is a dated stock of records, not future turnout or a population/eligibility estimate. No historical ballot count is divided by a mismatched current registration stock and described as observed turnout. [Sources and status context](https://www.sos.ks.gov/elections/voter-registration-statistics.html).

## Current primary and receipt-rule context

The official [2026 Senate primary workbook](https://www.sos.ks.gov/elections/26elec/2026-Primary-Election-United-States-Senate-Precinct-Level-Results.xlsx) and [statewide canvass](https://www.sos.ks.gov/elections/26elec/2026-Primary-Election-Official-Vote-Totals.pdf) reconcile all **13 candidates**, **224,076 Democratic** and **338,732 Republican** votes. These party primaries are distinct electorates, not 2026 general-election turnout. The earlier [NPR/AP state snapshot](https://apps.npr.org/primary-election-results-2026/data/KS_S_8_4_2026.json) and [county snapshot](https://apps.npr.org/primary-election-results-2026/data/KS_S_8_4_2026_counties.json), retained in coordinator news evidence, report **220,803 / 335,479**. Differences are **3,273 / 3,253**, with no scaling or inferred correction cause. The August primary files do not establish a November endpoint, cadence or live forecast. [Coordinator source/news evidence](data/news/manifest.json) retains the distinct vintages.

The retained statutory text of [K.S.A. 25-1132](https://www.kslegislature.gov/b2025_26/laws/025_000_0000_chapter/025_011_0000_article/025_011_0032_section/025_011_0032_k/) states an Election Day receipt deadline, effective January 1, 2026. **That text and the older SOS calendar do not establish the operative November rule by themselves.** The coordinator's [current legal alert](data/news/legal-web-observations.json) records a [Russell County November page](https://russellcountykansas.com/322/Advance-Voting-by-Mail) describing an injunction restoring a postmark/three-day receipt window and a rejected stay, alongside an older conflicting paragraph. The official-results assignment must verify the signed orders and later docket; this report does not resolve that legal gate or infer zero outstanding ballots at poll close.

Federal-services ballots have separate statutory treatment: [25-1221](https://www.kslegislature.gov/b2025_26/laws/025_000_0000_chapter/025_012_0000_article/025_012_0021_section/025_012_0021_k/) discusses receipt by poll close, while [25-1216(b)](https://www.kslegislature.gov/b2025_26/laws/025_000_0000_chapter/025_012_0000_article/025_012_0016_section/025_012_0016_k/) permits qualifying electronic transmission. [25-1136](https://www.kslegislature.gov/b2025_26/laws/025_000_0000_chapter/025_011_0000_article/025_011_0036_section/025_011_0036_k/) preserves provisional/challenge/canvass procedures. Those are distinct administrative categories, not generic three-day exceptions established by this research. Current court effects and any election-specific exceptions remain for the official-results review. These issues do not change the historical integer ranking.

## Reproduction and checks

Run from the repository root, with Python 3 and Poppler `pdftotext`:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/kansas/data/turnout/build_turnout.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/kansas/data/turnout/compare_peer.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/kansas/data/turnout/write_report.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/kansas/data/turnout/validate_turnout.py
```

[Acquisition](data/turnout/acquire.py) is explicit and bounded; offline rebuilding does not re-download or mutate shared originals. [Shared references](data/turnout/source/shared-references.json) pin exact original/stored hashes and bytes, requested/final URLs, UTC retrieval and HTTP metadata. [New acquisitions](data/turnout/source/acquisition.json) retain redirect chains and failures. Gzip preserves full original bytes; there are no truncated originals or reconstructed allocations. [Schema](data/turnout/source/SCHEMA.md) defines every source family and unavailable field. [Owned asset manifest](data/turnout/asset-manifest.json) covers the report, CSV and turnout assets; every individual stored asset is strictly below 40,000,000 bytes.

[Offline validation](data/turnout/validation.json) checks complete identities, raw/source hashes and positions, all statewide named-candidate balances, exact weights/minimum integer 80% crossing, all orders and remainder, native coverage, administrative bounds and known source anomalies, peer agreement, and relative links. The peer comparison checks **all 105 counties**, **22,031 exact source-native contexts**, **120,879 shared named/generic/footer cells**, and **94,008 original worksheet rows**, including literal header codes and blanks. The additional **269 Sedgwick contest-total cells plus its footer** remain separately retained. The peer uses a different native key encoding; [the complete key crosswalk](data/turnout/extracts/peer-native-key-crosswalk.csv.gz) is based on original source coordinates, not inferred geometry. The [external coordinator record](data/coordinator-priority-acceptance.json) accepts this historical research dispatch; it does not approve current geography. No implemented collector, approved current precinct layer, measured November live cadence or calibrated 2026 forecast is claimed.
