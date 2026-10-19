# South Dakota: reported vote concentration

Research observed October 19, 2026. **The complete primary ranking is the 691 displayed native reporting rows under all 66 counties in the official public 2024 Presidential Electors export.** No 2024 Senate election occurred. The workbook explicitly labels itself unofficial; its denominator is **428,728 reported candidate votes**, while the signed statewide canvass reports **428,922**. These are separate source scopes, neither ballots cast nor a 2026 turnout forecast. [Official 2024 history](https://sdsos.gov/elections-voting/election-resources/election-history/2024_Election_History.aspx), [actual historical statewide parent / published Precinct Level control](https://electionresults.sd.gov/resultsSW.aspx?type=SWR&map=CTY&eid=684), [signed 2024 canvass](https://sdsos.gov/elections-voting/assets/Archive/2024%20Assets/Recount-Canvass-and-Canvass-Docs-General/2024GeneralElectionCanvassWithCert.pdf).

**Exact top 15: 61,003 / 428,728 = 14.2288350656%. Minimum descending set reaching 80%: 304 native rows, 343,402 / 428,728 = 80.0978709112%.** The first 303 contribute 342,947 (79.9917430166%); Hamlin **Precinct-26**, worksheet 32, row 14, contributes **455** and crosses. The integer target is 342,983; `5 × 342947 < 4 × 428728 ≤ 5 × 343402`. A descending prefix maximizes the votes available in any fixed-size set, proving minimal cardinality. The remaining **387 rows supply 85,326 votes** and stay in every state total. The priority leaves have **39 county parents**. Arithmetic comes from the original workbook’s four literal candidate columns and verified county TOTAL rows; [full native CSV](data/county-turnout.csv), [exact dispatch contract](data/turnout/priority-set.json), [source-scoped parent balances](data/turnout/native-2024-parent-reconciliation.json).

Certification robustness is **unproved**. The signed denominator’s integer 80% target is **343,138**, and the observed first 303 native rows are **191 votes short** while the unresolved source difference is **194**. Observing the same 304-row crossing against a larger denominator does not establish the certified minimum or membership. County/candidate source differences are retained; no allocation or within-county redistribution is assumed.

Equal-volume rows sort by county FIPS, original worksheet ordinal, then numeric source row. Keys such as `sd:2024:pres:46057:sheet32:row14` are evidence locators, not official numeric precinct IDs. South Dakota FIPS is **46**. County FIPS comes from the [Census 2020 county code reference](https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt); the original workbook exposes county worksheet names, sheet IDs, literal unit labels and cell addresses. The compatibility filename `county-turnout.csv` contains all 691 native rows; it does not authorize county substitution. [Schema](data/turnout/source/SCHEMA.md).

| Rank | County parent | Literal native row | Candidate votes | Cumulative |
| ---: | --- | --- | ---: | ---: |
| 1 | Lawrence | Absentee Precinct | 9,096 | 9,096 |
| 2 | Brown | Absentee Precinct | 8,579 | 17,675 |
| 3 | Brookings | Absentee Precinct | 7,550 | 25,225 |
| 4 | Yankton | Absentee Precinct | 6,077 | 31,302 |
| 5 | Pennington | Precinct AW | 4,881 | 36,183 |
| 6 | Hughes | Absentee Precinct | 2,875 | 39,058 |
| 7 | Pennington | Precinct BE | 2,827 | 41,885 |
| 8 | Lincoln | Sioux Falls 2-16 | 2,792 | 44,677 |
| 9 | Pennington | Precinct 3-2 | 2,492 | 47,169 |
| 10 | Pennington | Precinct 3-3 | 2,435 | 49,604 |
| 11 | Lincoln | Sioux Falls 2-13 | 2,368 | 51,972 |
| 12 | Hughes | 2. New Life Assembly of God Church | 2,312 | 54,284 |
| 13 | Minnehaha | Precinct-0417 | 2,255 | 56,539 |
| 14 | Lincoln | Sioux Falls 2-11 | 2,236 | 58,775 |
| 15 | Brown | AmericInn Event Center | 2,228 | 61,003 |

## Candidate universe and reconciliation

The signed 2024 table has four tickets in this order: Kamala D. Harris / Tim Walz (DEM) **146,859**; Chase Oliver / Mike ter Maat (LIB) **2,778**; Donald J. Trump / JD Vance (REP) **272,081**; Robert F. Kennedy Jr. / Nicole Shanahan (IND) **7,204**. Independent extraction of every one of the 66 county vectors closes to those controls. The public native workbook instead sums to **146,811 / 2,777 / 271,938 / 7,202**. Its **−48 / −1 / −143 / −2 = −194** difference spans 24 counties, retained exactly and unallocated. Every public native-to-county footer closes. Neither 691/691 reporting nor the newly generated “Downloaded at” clock establishes certification, source-update time, or reporting cadence. [Signed controls](data/turnout/certified-controls.json), [native/certified differences](data/turnout/native-2024-parent-reconciliation.json), [original download/form chain](data/news/manifest.json).

All four original signed county-canvass PDF groups are retained once in the shared evidence store, including every page and unrelated office; complete text extracts and original-byte hashes are inventoried here. Scanned tables have imperfect embedded OCR. A close-looking OCR footer does not resolve a source discrepancy; this package does **not** assert an independently reconciled certified-native ranking. The [separate statewide all-race workbook](https://electionresults.sd.gov/ResultsExport.aspx?eid=684) literally labels presidential D7 as Trump and E7 as Trump1, omitting Oliver; the precise native export and separate Aurora export have the correct four headers. Literal XML/shared strings are preserved without relabeling by numerical resemblance. [Presentation audit](data/turnout/candidate-header-presentation.json), [county original inventory](data/turnout/county-original-inventory.json).

Write-in votes are not countable under SDCL 12-20-21.2; the [official 2026 offices page](https://www.sdsos.gov/elections-voting/upcoming-elections/general-information/2026%20Election%20Information/2026-offices-to-be-filled.aspx) reproduces that rule, and the [2024 presidential ballot-access page](https://www.sdsos.gov/elections-voting/upcoming-elections/general-information/2024/2024-Presidential-Ballot-Access.aspx) separately prohibits write-ins. The historical candidate sources publish no generic or named valid write-in vote columns. Missing write-in observations remain null with a legal-scope explanation, rather than fabricated source zeros. Blank ballots, undervotes and overvotes remain separate nullable fields.

The current [SOS general candidate list](https://vip.sdsos.gov/candidatelist.aspx?eid=774) shows Julian Beaudion (DEM), withdrawn August 4, 2026; Brian L Bengs (IND), active; and Mike Rounds (REP), active. Independent primary web inspection of Lincoln County’s [November 3, 2026 publication ballot](https://www.lincolncountysd.gov/DocumentCenter/View/1989/Sample-Ballot-2026-PDF), page 1, shows Rounds Republican Party and Bengs Independent as the two Senate choices. That PDF was read through the web tool; no exact original PDF bytes are claimed retained here (direct county downloads returned 404 for the peer). Current Bengs Independent and historical 2022 Bengs Democratic are separate election facts. No active Democratic Senate choice or current ENR candidate ID is invented. [Raw list/status audit](data/turnout/current-candidate-scope.json).

## Actual midterm and same-seat context

The **November 8, 2022 Senate election is the other Class III seat**, with Brian L. Bengs (DEM) **91,007**, Tamara J Lesnar (LIB) **14,697**, John R. Thune (REP) **242,316**, total **348,020**. All 66 signed county vectors close. The retained 1,420-page precinct canvass has **679 numeric native rows across 65 counties**: 66 Senate pages include a Minnehaha continuation, and there are no Yankton pages. All 65 available county native vectors close to signed controls. Yankton’s **2,462 / 340 / 6,051 = 8,853** remain in statewide arithmetic through its county control, never invented as a native residual. [Signed 2022 state canvass](https://sdsos.gov/elections-voting/assets/Archive/2022%20Assets/2022Generalcanvassreport.pdf), [precinct original](https://sdsos.gov/elections-voting/assets/Archive/2022%20Assets/2022PrecintCanvass.pdf), [PDF-specific reconciliation](data/turnout/native-2022-reconciliation.json).

A newly acquired **separate public 2022 Senate Precinct Level workbook**, followed from the [actual historical election](https://electionresults.sd.gov/Default.aspx?eid=471) to its observed statewide control, supplies **687 rows / 66 county parents**, including **eight Yankton rows**. Every county and candidate closes to the signed 2022 controls. It remains an explicitly unofficial source and does not retroactively fill the precinct PDF’s omission. Original worksheet rows, headers, clocks, numeric cell types, complete XML and ZIP member hashes are retained. [Exact request/form receipt](data/turnout/source/public-native-senate-2022.receipt.json), [complete public native CSV](data/turnout/native-2022-public.csv).

The **November 3, 2020 Senate election is the same Class II seat**: the printed source order is Mike Rounds (REP) **276,232**, then Dan Ahlers (DEM) **143,987**, total **420,219**. All 66 county vectors reconcile. Its independently downloaded [historical public native Senate export](https://electionresults.sd.gov/?eid=422) supplies **693 rows / 66 parents**, but **276,208 / 143,970**, a **−24 / −17 = −41** difference across 21 counties, unallocated. The complete signed county original is 149,141,181 bytes and retained as one exact gzip stream in four ordered parts; reconstruction verifies all stored-part, stored-stream and raw hashes. No duplicate large original is stored here. [Signed 2020 state canvass](https://sdsos.gov/elections-voting/assets/Archive/2020%20Assests/2020GeneralStateCanvassFinal%26Certificate.pdf), [public native CSV](data/turnout/native-2020-public.csv), [reconciliation](data/turnout/historical-public-native-reconciliation.json), [reconstruction tool](data/news/reconstruct_evidence.py).

No precinct, polling site, vote center, central counting unit or ballot-style equivalence is inferred across these years. Oglala Lakota is one current county (FIPS 46102); historical Shannon naming/code is a vintage-specific identity issue, not another county to add. All raw source names remain preserved.

The separate public native comparators also retain exact full-source rankings (no cross-year member matching). [Calculation/order file](data/turnout/sensitivities.json):

| Public native comparator | All units | Candidate-vote denominator | Top15 votes / % | Minimum80 rows / cumulative | Preceding cumulative | Crossing source locator |
| --- | ---: | ---: | --- | --- | ---: | --- |
| 2022 Senate | 687 | 348,020 | 44,602 / 12.8159301190% | 304 / 278,731 | 278,365 | sd:2022:senate:46127:public-sheet62:row8 |
| 2020 Senate | 693 | 420,178 | 72,780 / 17.3212305261% | 288 / 336,407 | 335,964 | sd:2020:senate:46103:public-sheet2:row31 |

## Ballot, registration and county sensitivities

The official [returns index](https://sdsos.gov/elections-voting/election-resources/election-history/official-election-returns.aspx) links the three retained books below. Their turnout tables call the volume “Votes Cast”; separate historical ENR headers call the same statewide volumes “Ballots Cast.” These volumes include participation that did not produce a counted vote in the selected contest. The difference is **unclassified contest nonparticipation/source scope**, not a measured undervote, overvote or blank-ballot count. No such residual is allocated to native rows.

| Election/contest | Candidate votes (signed) | Book Votes Cast | Difference | Turnout-table registration | Registration-table active | Registration-table inactive |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2024 president | 428,922 | 436,478 | 7,556 | 624,175 | 624,175 | 63,901 |
| 2022 Senate | 348,020 | 354,670 | 6,650 | 597,073 | 597,069 | 61,369 |
| 2020 Senate | 420,219 | 427,529 | 7,310 | 578,655 | 578,666 | 56,646 |

Primary book citations: [2024, registration pp.20–21 / precinct inventory p.22 / turnout p.23](https://sdsos.gov/elections-voting/assets/Archive/2024%20Assets/Post-Election-Audit-General/ElectionReturns2024.pdf); [2022, pp.22–25](https://sdsos.gov/elections-voting/assets/Archive/Prior%20to%202026/Election%20Returns%202022.pdf); [2020, pp.13–15](https://sdsos.gov/elections-voting/assets/Archive/Prior%20to%202026/ElectionReturns2020web.pdf). The dates are respectively November 5, 2024, November 8, 2022, and November 3, 2020. County sums separately reproduce each printed source table: the 2022 registration-table active total is four below its turnout denominator; the 2020 registration-table active total is eleven above its turnout denominator. These discrepancies remain explicit. Adding inactive to active is only a separate stock sensitivity, not a voting-eligible denominator. Party registration and inactive columns remain verbatim in the complete originals and retained source lines; empty cells are not invented zeros. [All-county controls](data/turnout/turnout-registration-controls.json), [198 county/contest sensitivity rows](data/turnout/county-sensitivities.csv).

The [2024 historical terminology page](https://electionresults.sd.gov/ElectionTerminology.aspx?eid=684) says turnout uses active voters; its observed header reports **436,478 ballots / 625,192 registered**, unlike the book’s **624,175** turnout denominator. The 2020 historical header reports **578,651** registered, unlike book turnout **578,655** and registration table **578,666**. The 2022 historical header agrees the turnout table **597,073**. Denominators are never silently swapped. Receipts retain requested/final URLs, UTC, headers and status, including the 404 unarchived-book routes and Census API’s HTTP-200 “Missing Key” HTML; only the successful linked archive PDFs and Census code text are accepted inputs.

County concentration is a separate sensitivity; it never replaces the 691-row priority. Exact comparisons follow, with complete descending orders in [sensitivities.json](data/turnout/sensitivities.json).

| County basis | Denominator | Top 15 votes/stock | Top 15 % | Minimum 80% counties | Preceding cumulative | Crossing cumulative | Crossing FIPS |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 2024 signed contest votes | 428,922 | 318,769 | 74.3186406853 | 21 | 342,469 | 346,205 | 46067 |
| 2024 book Votes Cast | 436,478 | 324,341 | 74.3086707692 | 21 | 348,453 | 352,243 | 46067 |
| 2024 turnout-table registration | 624,175 | 464,676 | 74.4464292867 | 20 | 493,872 | 500,068 | 46109 |
| 2024 registration active + inactive | 688,076 | 515,807 | 74.9636668042 | 20 | 548,627 | 555,318 | 46109 |
| 2022 signed contest votes | 348,020 | 254,495 | 73.1265444515 | 22 | 277,584 | 280,726 | 46067 |
| 2022 book Votes Cast | 354,670 | 259,335 | 73.1200834579 | 22 | 282,817 | 286,028 | 46067 |
| 2022 turnout-table registration | 597,073 | 440,876 | 73.8395472580 | 21 | 475,107 | 480,963 | 46125 |
| 2022 registration active + inactive | 658,438 | 489,012 | 74.2684960467 | 20 | 521,036 | 527,605 | 46047 |
| 2020 signed contest votes | 420,219 | 308,500 | 73.4141007427 | 22 | 335,367 | 339,121 | 46067 |
| 2020 book Votes Cast | 427,529 | 314,218 | 73.4963008357 | 22 | 341,459 | 345,258 | 46067 |
| 2020 turnout-table registration | 578,655 | 422,358 | 72.9896052052 | 22 | 461,423 | 466,835 | 46023 |
| 2020 registration active + inactive | 635,312 | 467,110 | 73.5245044954 | 21 | 504,208 | 510,205 | 46125 |

Method sensitivity retains the literal “Absentee Precinct” rows and the 2020 Yankton “Absentee ” row as administrative reporting groups. The other rows have unspecified method composition; “CENTRAL STURGIS,” for example, is a literal place/unit label and is not proof of central absentee counting. The [source terminology](https://electionresults.sd.gov/ElectionTerminology.aspx?eid=684) explains that vote-center counties allow voters to vote at any center; the historical book marks those counties. Polling sites, vote centers, combined precincts and absentee boards are not automatically disjoint physical precinct polygons. [Complete source-method controls](data/turnout/source-method-controls.json) retain candidate subtotals and every remaining row:

| Public native source | Explicitly labeled absentee rows | Votes in those rows | Votes in remaining, method-unspecified rows |
| --- | ---: | ---: | ---: |
| 2024 | 9 | 35,377 | 393,351 |
| 2022 | 10 | 22,775 | 325,245 |
| 2020 | 9 | 44,477 | 375,701 |

There is no complete statewide mail-versus-early-in-person-versus-Election-Day candidate or ballot split in these exported contest tables. Their unavailable fields remain null. Unit counters are not vote-completion percentages: the current 2026 mock overall 673 versus Senate 656 flags are setup observations, not a precinct crosswalk, genuine counts or a remaining-ballot estimate. Current test candidate setup values are excluded.

## Reproduction and review

Run `python data/turnout/extract.py`, `python data/turnout/extract_historical_native.py`, `python data/turnout/build_turnout.py`, `python data/turnout/compare_peer.py`, and `python data/turnout/validate_turnout.py` from this state directory. Offline extraction verifies complete raw/stored hashes and ZIP CRC/member hashes. Acquisition scripts retain observed public parent/control chains; they are reproducible research downloads, not an implemented live collector. [Acquisition/extraction schema](data/turnout/source/SCHEMA.md), [owned and reused asset manifest](data/turnout/asset-manifest.json), [offline validation](data/turnout/validation.json), [independent peer comparison](data/turnout/peer-agreement.json).

Coordinator acceptance remains an external review step. Independent peer arithmetic agreement does not approve November 2026 legal geography, physical precinct boundaries, reporting-method joins, source cadence, a calibrated Needle or any 2026 turnout forecast. Material retained gaps are the 194-vote 2024 and 41-vote 2020 unofficial/certified native-source differences, the original 2022 PDF’s missing Yankton pages, unavailable native ballot/registration/blank/under/over fields, and unapproved current joins. The separate public 2022 workbook supplies all 66 parents and reconciles fully. Owned historical research remains complete with these source scopes explicit.

## Complete 691-row native order

Rows 1–304 are the minimum 80% set; rows 305–691 are the complete remainder. Each raw literal, candidate count and source address is in the linked CSV/contract. Every county summary is an ancestor, never an extra additive row. The source for the entire order is the [original public 2024 Presidential Electors Precinct Level workbook control](https://electionresults.sd.gov/resultsSW.aspx?type=SWR&map=CTY&eid=684).

| Rank | County | Literal native row | Votes | Cumulative | Priority |
| ---: | --- | --- | ---: | ---: | --- |
| 1 | Lawrence | Absentee Precinct | 9,096 | 9,096 | 80% |
| 2 | Brown | Absentee Precinct | 8,579 | 17,675 | 80% |
| 3 | Brookings | Absentee Precinct | 7,550 | 25,225 | 80% |
| 4 | Yankton | Absentee Precinct | 6,077 | 31,302 | 80% |
| 5 | Pennington | Precinct AW | 4,881 | 36,183 | 80% |
| 6 | Hughes | Absentee Precinct | 2,875 | 39,058 | 80% |
| 7 | Pennington | Precinct BE | 2,827 | 41,885 | 80% |
| 8 | Lincoln | Sioux Falls 2-16 | 2,792 | 44,677 | 80% |
| 9 | Pennington | Precinct 3-2 | 2,492 | 47,169 | 80% |
| 10 | Pennington | Precinct 3-3 | 2,435 | 49,604 | 80% |
| 11 | Lincoln | Sioux Falls 2-13 | 2,368 | 51,972 | 80% |
| 12 | Hughes | 2. New Life Assembly of God Church | 2,312 | 54,284 | 80% |
| 13 | Minnehaha | Precinct-0417 | 2,255 | 56,539 | 80% |
| 14 | Lincoln | Sioux Falls 2-11 | 2,236 | 58,775 | 80% |
| 15 | Brown | AmericInn Event Center | 2,228 | 61,003 | 80% |
| 16 | Minnehaha | Precinct-0316 | 2,197 | 63,200 | 80% |
| 17 | Pennington | Precinct 5-5 | 2,154 | 65,354 | 80% |
| 18 | Minnehaha | Precinct-0319 | 2,126 | 67,480 | 80% |
| 19 | Hughes | 1. Faith Lutheran Church | 2,125 | 69,605 | 80% |
| 20 | Minnehaha | Precinct-VP15 | 2,089 | 71,694 | 80% |
| 21 | Minnehaha | Precinct-VP05 | 2,081 | 73,775 | 80% |
| 22 | Minnehaha | Precinct-VP07 | 2,061 | 75,836 | 80% |
| 23 | Minnehaha | Precinct-VP21 | 2,031 | 77,867 | 80% |
| 24 | Pennington | Precinct 2-2 | 2,019 | 79,886 | 80% |
| 25 | Minnehaha | Precinct-VP03 | 1,965 | 81,851 | 80% |
| 26 | Minnehaha | Precinct-0415 | 1,945 | 83,796 | 80% |
| 27 | Pennington | Precinct 3-4 | 1,920 | 85,716 | 80% |
| 28 | Brown | Best Western Ramkota Hotel and Convention Center | 1,897 | 87,613 | 80% |
| 29 | Yankton | Yankton Fire Station #2 | 1,878 | 89,491 | 80% |
| 30 | Brown | Courthouse Community Room | 1,863 | 91,354 | 80% |
| 31 | Lincoln | 27 | 1,849 | 93,203 | 80% |
| 32 | Minnehaha | Precinct-0217 | 1,788 | 94,991 | 80% |
| 33 | Pennington | Precinct 5-4 | 1,775 | 96,766 | 80% |
| 34 | Pennington | Precinct 1-3 | 1,761 | 98,527 | 80% |
| 35 | Minnehaha | Precinct-0117 | 1,760 | 100,287 | 80% |
| 36 | Pennington | Precinct VF | 1,753 | 102,040 | 80% |
| 37 | Minnehaha | Precinct-0416 | 1,747 | 103,787 | 80% |
| 38 | Minnehaha | Precinct-0310 | 1,742 | 105,529 | 80% |
| 39 | Pennington | Precinct 1-5 | 1,730 | 107,259 | 80% |
| 40 | Lincoln | Sioux Falls 2-10 | 1,728 | 108,987 | 80% |
| 41 | Lincoln | 29 | 1,663 | 110,650 | 80% |
| 42 | Lincoln | Sioux Falls 1-18 | 1,660 | 112,310 | 80% |
| 43 | Lincoln | Sioux Falls 1-11 | 1,653 | 113,963 | 80% |
| 44 | Minnehaha | Precinct-VP09 | 1,629 | 115,592 | 80% |
| 45 | Minnehaha | Precinct-VP10 | 1,616 | 117,208 | 80% |
| 46 | Davison | Precinct-03 (Precinct-04, Precinct-05) | 1,603 | 118,811 | 80% |
| 47 | Minnehaha | Precinct-0202 | 1,589 | 120,400 | 80% |
| 48 | Davison | Precinct-06 (Precinct-07, Precinct-08) | 1,586 | 121,986 | 80% |
| 49 | Brookings | Brookings Activity Center | 1,545 | 123,531 | 80% |
| 50 | Stanley | Precinct-01 | 1,542 | 125,073 | 80% |
| 51 | Minnehaha | Precinct-0214 | 1,535 | 126,608 | 80% |
| 52 | Pennington | Precinct 5-3 | 1,535 | 128,143 | 80% |
| 53 | Pennington | Precinct 1-1 | 1,532 | 129,675 | 80% |
| 54 | Minnehaha | Precinct-0309 | 1,497 | 131,172 | 80% |
| 55 | Custer | Precinct-09 | 1,496 | 132,668 | 80% |
| 56 | Pennington | Precinct 1-2 | 1,493 | 134,161 | 80% |
| 57 | Minnehaha | Precinct-0314 | 1,488 | 135,649 | 80% |
| 58 | Lincoln | Sioux Falls 2-15 | 1,479 | 137,128 | 80% |
| 59 | Minnehaha | Precinct-0412 | 1,472 | 138,600 | 80% |
| 60 | Minnehaha | Precinct-VP02 | 1,460 | 140,060 | 80% |
| 61 | Davison | Precinct-15 (Precinct-16, Precinct-18) | 1,453 | 141,513 | 80% |
| 62 | Yankton | Yankton City Hall | 1,447 | 142,960 | 80% |
| 63 | Minnehaha | Precinct-0110 | 1,436 | 144,396 | 80% |
| 64 | Pennington | Precinct 3-5 | 1,431 | 145,827 | 80% |
| 65 | Minnehaha | Precinct-0512 | 1,430 | 147,257 | 80% |
| 66 | Lincoln | Sioux Falls 1-12 | 1,413 | 148,670 | 80% |
| 67 | Codington | Precinct-E1 (LAKE, Precinct-E4) | 1,411 | 150,081 | 80% |
| 68 | Pennington | Precinct HR | 1,398 | 151,479 | 80% |
| 69 | Minnehaha | Precinct-0317 | 1,390 | 152,869 | 80% |
| 70 | Codington | Precinct-C3 (PELICAN, Precinct-C4) | 1,374 | 154,243 | 80% |
| 71 | Pennington | Precinct HC | 1,368 | 155,611 | 80% |
| 72 | Minnehaha | Precinct-0106 | 1,353 | 156,964 | 80% |
| 73 | Pennington | Precinct JS | 1,351 | 158,315 | 80% |
| 74 | Pennington | Precinct RV | 1,346 | 159,661 | 80% |
| 75 | Lake | Ward One | 1,334 | 160,995 | 80% |
| 76 | Pennington | Precinct 4-3 | 1,331 | 162,326 | 80% |
| 77 | Minnehaha | Precinct-0206 | 1,328 | 163,654 | 80% |
| 78 | Minnehaha | Precinct-0315 | 1,328 | 164,982 | 80% |
| 79 | Minnehaha | Precinct-0411 | 1,315 | 166,297 | 80% |
| 80 | Pennington | Precinct 4-2 | 1,308 | 167,605 | 80% |
| 81 | Brule | Precinct-01 | 1,301 | 168,906 | 80% |
| 82 | Union | Precinct-12 | 1,299 | 170,205 | 80% |
| 83 | Davison | Precinct-09 (Precinct-10, Precinct-11) | 1,295 | 171,500 | 80% |
| 84 | Lawrence | Precinct-10 | 1,293 | 172,793 | 80% |
| 85 | Pennington | Precinct VV | 1,288 | 174,081 | 80% |
| 86 | Lincoln | 15 | 1,282 | 175,363 | 80% |
| 87 | Pennington | Precinct WP | 1,277 | 176,640 | 80% |
| 88 | Minnehaha | Precinct-0109 | 1,275 | 177,915 | 80% |
| 89 | Minnehaha | Precinct-0203 | 1,275 | 179,190 | 80% |
| 90 | Minnehaha | Precinct-0218 | 1,268 | 180,458 | 80% |
| 91 | Davison | Precinct-19 (Precinct-20) | 1,264 | 181,722 | 80% |
| 92 | Custer | Precinct-01 | 1,263 | 182,985 | 80% |
| 93 | Minnehaha | Precinct-0201 | 1,238 | 184,223 | 80% |
| 94 | Minnehaha | Precinct-VP16 | 1,231 | 185,454 | 80% |
| 95 | Beadle | Precinct 5 | 1,223 | 186,677 | 80% |
| 96 | Minnehaha | Precinct-0518 | 1,213 | 187,890 | 80% |
| 97 | Meade | SUMMERSET #10 | 1,208 | 189,098 | 80% |
| 98 | Union | Precinct-03 | 1,207 | 190,305 | 80% |
| 99 | Davison | Precinct-12 (Precinct-13, Precinct-14) | 1,206 | 191,511 | 80% |
| 100 | Codington | Precinct-A1 | 1,204 | 192,715 | 80% |
| 101 | Minnehaha | Precinct-0504 | 1,202 | 193,917 | 80% |
| 102 | Minnehaha | Precinct-0418 | 1,197 | 195,114 | 80% |
| 103 | Codington | Precinct-E2 (Precinct-E3) | 1,195 | 196,309 | 80% |
| 104 | Fall River | JAC | 1,188 | 197,497 | 80% |
| 105 | Brookings | Volga Community Center | 1,180 | 198,677 | 80% |
| 106 | Minnehaha | Precinct-0312 | 1,172 | 199,849 | 80% |
| 107 | Minnehaha | Precinct-0519 | 1,172 | 201,021 | 80% |
| 108 | Minnehaha | Precinct-0209 | 1,171 | 202,192 | 80% |
| 109 | Lincoln | Sioux Falls 1-14 | 1,162 | 203,354 | 80% |
| 110 | Lincoln | 16 | 1,158 | 204,512 | 80% |
| 111 | Lincoln | 25 | 1,157 | 205,669 | 80% |
| 112 | Minnehaha | Precinct-0506 | 1,113 | 206,782 | 80% |
| 113 | Minnehaha | Precinct-0501 | 1,102 | 207,884 | 80% |
| 114 | Minnehaha | Precinct-VP04 | 1,099 | 208,983 | 80% |
| 115 | Pennington | Precinct 1-4 | 1,095 | 210,078 | 80% |
| 116 | Beadle | Precinct 1 | 1,089 | 211,167 | 80% |
| 117 | Pennington | Precinct 2-4 | 1,084 | 212,251 | 80% |
| 118 | Clay | Precinct-03 | 1,082 | 213,333 | 80% |
| 119 | Minnehaha | Precinct-0419 | 1,074 | 214,407 | 80% |
| 120 | Minnehaha | Precinct-0522 | 1,070 | 215,477 | 80% |
| 121 | Lincoln | 24-01 | 1,067 | 216,544 | 80% |
| 122 | Minnehaha | Precinct-0311 | 1,066 | 217,610 | 80% |
| 123 | Lincoln | 20 | 1,046 | 218,656 | 80% |
| 124 | Minnehaha | Precinct-0409 | 1,045 | 219,701 | 80% |
| 125 | Pennington | Precinct 4-1 | 1,033 | 220,734 | 80% |
| 126 | Minnehaha | Precinct-VP13 | 1,032 | 221,766 | 80% |
| 127 | Gregory | Precinct-1 | 1,030 | 222,796 | 80% |
| 128 | Meade | SOUTHEAST PIEDMONT #13 | 1,030 | 223,826 | 80% |
| 129 | Pennington | Precinct 5-2 | 1,023 | 224,849 | 80% |
| 130 | Lincoln | 24-02 | 1,013 | 225,862 | 80% |
| 131 | Minnehaha | Precinct-0520 | 1,001 | 226,863 | 80% |
| 132 | Lawrence | Precinct-03 | 979 | 227,842 | 80% |
| 133 | Pennington | Precinct 2-3 | 972 | 228,814 | 80% |
| 134 | Lincoln | Sioux Falls 1-15 | 970 | 229,784 | 80% |
| 135 | Minnehaha | Precinct-0508 | 966 | 230,750 | 80% |
| 136 | Brookings | Bethel Baptist Church Area 1 | 959 | 231,709 | 80% |
| 137 | Codington | Precinct-B3 (Precinct-C1) | 954 | 232,663 | 80% |
| 138 | Pennington | Precinct 2-5 | 941 | 233,604 | 80% |
| 139 | Hutchinson | Precinct-02 | 940 | 234,544 | 80% |
| 140 | Minnehaha | Precinct-VP08 | 939 | 235,483 | 80% |
| 141 | Brookings | Bethel Baptist Church Area 2 | 929 | 236,412 | 80% |
| 142 | Beadle | Precinct-7 | 927 | 237,339 | 80% |
| 143 | Codington | Precinct-B2 | 924 | 238,263 | 80% |
| 144 | Lincoln | Sioux Falls 2-12 | 918 | 239,181 | 80% |
| 145 | Codington | Precinct-B1 (Precinct-B4, Precinct-E5) | 916 | 240,097 | 80% |
| 146 | Brookings | Holy Life Tabernacle  | 915 | 241,012 | 80% |
| 147 | Union | Precinct-11 | 910 | 241,922 | 80% |
| 148 | Kingsbury | De Smet Precinct | 902 | 242,824 | 80% |
| 149 | Minnehaha | Precinct-0404 | 897 | 243,721 | 80% |
| 150 | Beadle | Precinct 2 | 895 | 244,616 | 80% |
| 151 | Turner | Precinct-01 | 895 | 245,511 | 80% |
| 152 | Minnehaha | Precinct-0313 | 888 | 246,399 | 80% |
| 153 | Minnehaha | Precinct-0301 | 885 | 247,284 | 80% |
| 154 | Minnehaha | Precinct-0521 | 877 | 248,161 | 80% |
| 155 | Lawrence | Precinct-02 | 874 | 249,035 | 80% |
| 156 | Lincoln | 24-03 | 870 | 249,905 | 80% |
| 157 | Union | Precinct-06 | 866 | 250,771 | 80% |
| 158 | Minnehaha | Precinct-VP01 | 863 | 251,634 | 80% |
| 159 | Turner | Precinct-02 | 860 | 252,494 | 80% |
| 160 | Brown | Groton Community Center | 858 | 253,352 | 80% |
| 161 | Minnehaha | Precinct-0104 | 856 | 254,208 | 80% |
| 162 | Union | Precinct-09 | 854 | 255,062 | 80% |
| 163 | Clay | Precinct-S1 | 852 | 255,914 | 80% |
| 164 | Meade | PIEDMONT CENTRAL #11A | 849 | 256,763 | 80% |
| 165 | Meade | CENTRAL BLACK HAWK #19 | 845 | 257,608 | 80% |
| 166 | Butte | Precinct-16 | 844 | 258,452 | 80% |
| 167 | Minnehaha | Precinct-0318 | 837 | 259,289 | 80% |
| 168 | Lincoln | Sioux Falls 1-16 | 824 | 260,113 | 80% |
| 169 | Minnehaha | Precinct-0408 | 818 | 260,931 | 80% |
| 170 | Minnehaha | Precinct-0523 | 817 | 261,748 | 80% |
| 171 | Hughes | 3. Capitol Lake Visitors Center | 816 | 262,564 | 80% |
| 172 | Meade | TILFORD #6 | 811 | 263,375 | 80% |
| 173 | Meade | NORTHEAST PIEDMONT #12 | 810 | 264,185 | 80% |
| 174 | Minnehaha | Precinct-0413 | 808 | 264,993 | 80% |
| 175 | Gregory | Precinct-2 | 807 | 265,800 | 80% |
| 176 | Hamlin | Precinct-21 | 805 | 266,605 | 80% |
| 177 | Lawrence | Precinct-01 | 803 | 267,408 | 80% |
| 178 | Roberts | Precinct-11 | 799 | 268,207 | 80% |
| 179 | Hamlin | Precinct-24 | 797 | 269,004 | 80% |
| 180 | Minnehaha | Precinct-0402 | 794 | 269,798 | 80% |
| 181 | Moody | Precinct-5 | 792 | 270,590 | 80% |
| 182 | Minnehaha | Precinct-0516 | 785 | 271,375 | 80% |
| 183 | Custer | Precinct-05 | 782 | 272,157 | 80% |
| 184 | Lincoln | Sioux Falls 1-20 | 782 | 272,939 | 80% |
| 185 | Minnehaha | Precinct-0119 | 782 | 273,721 | 80% |
| 186 | Lincoln | 23-13 | 778 | 274,499 | 80% |
| 187 | Beadle | Precinct 3 | 772 | 275,271 | 80% |
| 188 | Beadle | Precinct 6 | 771 | 276,042 | 80% |
| 189 | Pennington | Precinct 5-1 | 766 | 276,808 | 80% |
| 190 | Lincoln | Sioux Falls 1-13 | 763 | 277,571 | 80% |
| 191 | Hutchinson | Precinct-04 | 757 | 278,328 | 80% |
| 192 | Minnehaha | Precinct-VP17 | 754 | 279,082 | 80% |
| 193 | Pennington | Precinct NU | 740 | 279,822 | 80% |
| 194 | Union | Precinct-10 | 738 | 280,560 | 80% |
| 195 | Pennington | Precinct 4-4 | 735 | 281,295 | 80% |
| 196 | Lake | Ward Three | 732 | 282,027 | 80% |
| 197 | Minnehaha | Precinct-0305 | 725 | 282,752 | 80% |
| 198 | Pennington | Precinct CA | 722 | 283,474 | 80% |
| 199 | Minnehaha | Precinct-0407 | 720 | 284,194 | 80% |
| 200 | Beadle | Precinct 4 | 718 | 284,912 | 80% |
| 201 | Lake | Ward Two | 715 | 285,627 | 80% |
| 202 | Lawrence | Precinct-09 | 712 | 286,339 | 80% |
| 203 | Pennington | Precinct DT | 712 | 287,051 | 80% |
| 204 | Hutchinson | Precinct-01 | 709 | 287,760 | 80% |
| 205 | Lawrence | Precinct-04 | 706 | 288,466 | 80% |
| 206 | Bon Homme | Precinct-3 | 700 | 289,166 | 80% |
| 207 | Codington | Precinct-C2 (ELMIRA, Precinct-D4) | 696 | 289,862 | 80% |
| 208 | Hyde | Hyde County Memorial Auditorium-East Wing | 695 | 290,557 | 80% |
| 209 | Minnehaha | Precinct-0405 | 693 | 291,250 | 80% |
| 210 | Charles Mix | Precinct-11 | 691 | 291,941 | 80% |
| 211 | Clay | Precinct-W1 | 690 | 292,631 | 80% |
| 212 | Minnehaha | Precinct-0406 | 685 | 293,316 | 80% |
| 213 | Hanson | Precinct-1 | 684 | 294,000 | 80% |
| 214 | McCook | Precinct-05 | 667 | 294,667 | 80% |
| 215 | Potter | CC Bar (Gettysburg Legion Annex) | 663 | 295,330 | 80% |
| 216 | Union | Precinct-05 | 658 | 295,988 | 80% |
| 217 | McCook | Precinct-03 | 649 | 296,637 | 80% |
| 218 | Kingsbury | Arlington Precinct | 645 | 297,282 | 80% |
| 219 | Pennington | Precinct CL | 645 | 297,927 | 80% |
| 220 | Fall River | EDA | 642 | 298,569 | 80% |
| 221 | Meade | EAST ELK VALE #21A | 642 | 299,211 | 80% |
| 222 | Minnehaha | Precinct-0510 | 639 | 299,850 | 80% |
| 223 | Meade | BASE #23 | 634 | 300,484 | 80% |
| 224 | Pennington | Precinct KY | 631 | 301,115 | 80% |
| 225 | Custer | Precinct-04 | 628 | 301,743 | 80% |
| 226 | McCook | Precinct-01 | 628 | 302,371 | 80% |
| 227 | Bon Homme | Precinct-5 | 626 | 302,997 | 80% |
| 228 | Minnehaha | Precinct-0208 | 625 | 303,622 | 80% |
| 229 | Minnehaha | Precinct-0507 | 625 | 304,247 | 80% |
| 230 | Clay | Precinct-S2 | 608 | 304,855 | 80% |
| 231 | Turner | Precinct-08 | 605 | 305,460 | 80% |
| 232 | Codington | Precinct-A3 (Precinct-A4) | 603 | 306,063 | 80% |
| 233 | Lake | Wentworth-Rutland | 602 | 306,665 | 80% |
| 234 | Minnehaha | Precinct-0502 | 600 | 307,265 | 80% |
| 235 | Bon Homme | Precinct-1 | 596 | 307,861 | 80% |
| 236 | Minnehaha | Precinct-0105 | 596 | 308,457 | 80% |
| 237 | Pennington | Precinct 4-5 | 595 | 309,052 | 80% |
| 238 | Turner | Precinct-06 | 594 | 309,646 | 80% |
| 239 | Codington | Precinct-D1 | 590 | 310,236 | 80% |
| 240 | Lake | Lakeview | 589 | 310,825 | 80% |
| 241 | Moody | Precinct-3 | 584 | 311,409 | 80% |
| 242 | Lake | Chester-Franklin | 579 | 311,988 | 80% |
| 243 | Roberts | Precinct-06 (Precinct-07) | 577 | 312,565 | 80% |
| 244 | Turner | Precinct-03 | 572 | 313,137 | 80% |
| 245 | Meade | SOUTHEAST STURGIS #2 | 569 | 313,706 | 80% |
| 246 | Oglala Lakota | Sacred Heart Church Hall | 568 | 314,274 | 80% |
| 247 | Hamlin | Precinct-25 | 563 | 314,837 | 80% |
| 248 | Meade | RURAL STURGIS #7 | 562 | 315,399 | 80% |
| 249 | Union | Precinct-04 | 556 | 315,955 | 80% |
| 250 | Codington | Precinct-A2 | 553 | 316,508 | 80% |
| 251 | Brule | Precinct-02 | 547 | 317,055 | 80% |
| 252 | Oglala Lakota | Sacred Heart Church Hall | 546 | 317,601 | 80% |
| 253 | Bon Homme | Precinct-4 | 544 | 318,145 | 80% |
| 254 | Hutchinson | Precinct-03 | 540 | 318,685 | 80% |
| 255 | Minnehaha | Precinct-0320 | 538 | 319,223 | 80% |
| 256 | Brookings | Aurora Impact Church | 537 | 319,760 | 80% |
| 257 | Lincoln | 13-14 | 535 | 320,295 | 80% |
| 258 | McCook | Precinct-04 | 527 | 320,822 | 80% |
| 259 | Minnehaha | Precinct-VP11 | 527 | 321,349 | 80% |
| 260 | Bon Homme | Precinct-2 | 526 | 321,875 | 80% |
| 261 | Spink | Precinct-09 | 524 | 322,399 | 80% |
| 262 | Minnehaha | Precinct-0403 | 523 | 322,922 | 80% |
| 263 | Lincoln | 02-21 | 520 | 323,442 | 80% |
| 264 | Meade | NORTHWEST STURGIS #5 | 520 | 323,962 | 80% |
| 265 | Brookings | White McKnight Hall | 519 | 324,481 | 80% |
| 266 | Charles Mix | Precinct-03 | 514 | 324,995 | 80% |
| 267 | Roberts | Precinct-02 | 514 | 325,509 | 80% |
| 268 | Moody | Precinct-2 | 511 | 326,020 | 80% |
| 269 | Codington | Precinct-D2 | 509 | 326,529 | 80% |
| 270 | Haakon | Courthouse Community Room | 507 | 327,036 | 80% |
| 271 | Lincoln | 30 | 507 | 327,543 | 80% |
| 272 | Lincoln | 06 | 504 | 328,047 | 80% |
| 273 | Spink | Precinct-10 | 504 | 328,551 | 80% |
| 274 | Fall River | HS 1 | 502 | 329,053 | 80% |
| 275 | Lincoln | 26 | 502 | 329,555 | 80% |
| 276 | Moody | Precinct-1 | 498 | 330,053 | 80% |
| 277 | Custer | Precinct-08 | 497 | 330,550 | 80% |
| 278 | Edmunds | Precinct-1 | 497 | 331,047 | 80% |
| 279 | Meade | PIEDMONT WEST #11 | 497 | 331,544 | 80% |
| 280 | Kingsbury | Lake Preston Precinct | 494 | 332,038 | 80% |
| 281 | Minnehaha | Precinct-0509 | 494 | 332,532 | 80% |
| 282 | Roberts | Precinct-09 | 493 | 333,025 | 80% |
| 283 | Jerauld | Precinct-1 | 492 | 333,517 | 80% |
| 284 | Fall River | HS 2 | 487 | 334,004 | 80% |
| 285 | Oglala Lakota | Brother Renee Hall | 487 | 334,491 | 80% |
| 286 | Codington | Precinct-D3 | 485 | 334,976 | 80% |
| 287 | Lincoln | 12 | 485 | 335,461 | 80% |
| 288 | Lake | Herman-Winfred | 483 | 335,944 | 80% |
| 289 | Minnehaha | Precinct-0515 | 482 | 336,426 | 80% |
| 290 | Charles Mix | Precinct-01 | 481 | 336,907 | 80% |
| 291 | Butte | Precinct-25 | 477 | 337,384 | 80% |
| 292 | Spink | Precinct-07 | 477 | 337,861 | 80% |
| 293 | Turner | Precinct-05 | 476 | 338,337 | 80% |
| 294 | Union | Precinct-08 | 476 | 338,813 | 80% |
| 295 | Meade | RURAL BLACK HAWK #15 | 466 | 339,279 | 80% |
| 296 | Lincoln | 11-14 | 463 | 339,742 | 80% |
| 297 | Walworth | Precinct-06 | 462 | 340,204 | 80% |
| 298 | Minnehaha | Precinct-VP06 | 458 | 340,662 | 80% |
| 299 | Oglala Lakota | Little Wound School | 458 | 341,120 | 80% |
| 300 | Butte | Precinct-17 | 457 | 341,577 | 80% |
| 301 | Pennington | Precinct LS | 457 | 342,034 | 80% |
| 302 | Walworth | Precinct-07 | 457 | 342,491 | 80% |
| 303 | Yankton | Lewis and Clark Recreation Area | 456 | 342,947 | 80% |
| 304 | Hamlin | Precinct-26 | 455 | 343,402 | 80% |
| 305 | Sully | Phoenix Center | 455 | 343,857 | remainder |
| 306 | Union | Precinct-01 | 455 | 344,312 | remainder |
| 307 | Hutchinson | Precinct-05 | 454 | 344,766 | remainder |
| 308 | Day | Precinct-04 | 449 | 345,215 | remainder |
| 309 | Butte | Precinct-28 | 448 | 345,663 | remainder |
| 310 | Todd | Mission-N. Antelope | 448 | 346,111 | remainder |
| 311 | Brown | Warner Community Center | 439 | 346,550 | remainder |
| 312 | Clay | Precinct-W2 | 436 | 346,986 | remainder |
| 313 | Clay | Precinct-01 | 434 | 347,420 | remainder |
| 314 | Custer | Precinct-06 | 433 | 347,853 | remainder |
| 315 | Minnehaha | Precinct-0410 | 432 | 348,285 | remainder |
| 316 | Gregory | Precinct-3 | 430 | 348,715 | remainder |
| 317 | Grant | Precinct-33 | 428 | 349,143 | remainder |
| 318 | Fall River | HS 4 | 427 | 349,570 | remainder |
| 319 | Grant | Precinct-43 | 425 | 349,995 | remainder |
| 320 | Davison | Precinct-02 | 424 | 350,419 | remainder |
| 321 | Meade | EAST PIEDMONT #12A | 424 | 350,843 | remainder |
| 322 | Brookings | Bruce Community Room | 421 | 351,264 | remainder |
| 323 | Todd | Rosebud | 421 | 351,685 | remainder |
| 324 | Aurora | Precinct-3 | 420 | 352,105 | remainder |
| 325 | Brule | Precinct-03 | 418 | 352,523 | remainder |
| 326 | Hand | Precinct-01 | 418 | 352,941 | remainder |
| 327 | Spink | Precinct-01 | 416 | 353,357 | remainder |
| 328 | Walworth | Precinct-03 | 415 | 353,772 | remainder |
| 329 | Oglala Lakota | Christ The King Parish, Bill Pauly Hall | 414 | 354,186 | remainder |
| 330 | Fall River | HS 3 | 412 | 354,598 | remainder |
| 331 | Charles Mix | Precinct-09 | 410 | 355,008 | remainder |
| 332 | Clay | Precinct-E1 | 408 | 355,416 | remainder |
| 333 | Moody | Precinct-4 | 406 | 355,822 | remainder |
| 334 | Day | Precinct-11 | 404 | 356,226 | remainder |
| 335 | Meade | HARMONY #8 | 403 | 356,629 | remainder |
| 336 | Roberts | Precinct-05 | 402 | 357,031 | remainder |
| 337 | Union | Precinct-02 | 402 | 357,433 | remainder |
| 338 | Meade | SOUTH STURGIS #2A | 401 | 357,834 | remainder |
| 339 | Edmunds | Precinct-2 | 399 | 358,233 | remainder |
| 340 | Lawrence | Precinct-07 | 398 | 358,631 | remainder |
| 341 | Moody | Precinct-34 | 398 | 359,029 | remainder |
| 342 | Pennington | Precinct WL | 398 | 359,427 | remainder |
| 343 | Tripp | Colome Consolidated | 398 | 359,825 | remainder |
| 344 | Jones | Precinct-2 | 395 | 360,220 | remainder |
| 345 | Hanson | Precinct-2 | 392 | 360,612 | remainder |
| 346 | Pennington | Precinct 3-1 | 392 | 361,004 | remainder |
| 347 | Butte | Precinct-24 | 388 | 361,392 | remainder |
| 348 | Lake | Farmington-Leroy-Clarno-Orland | 387 | 361,779 | remainder |
| 349 | Day | Precinct-05 | 385 | 362,164 | remainder |
| 350 | McCook | Precinct-06 | 385 | 362,549 | remainder |
| 351 | Clay | Precinct-02 | 384 | 362,933 | remainder |
| 352 | Dewey | Precinct-04 Timber Lake | 384 | 363,317 | remainder |
| 353 | Brookings | Elkton Community Center | 383 | 363,700 | remainder |
| 354 | Yankton | Gayville Community Center | 381 | 364,081 | remainder |
| 355 | Edmunds | Precinct-5 | 375 | 364,456 | remainder |
| 356 | Ziebach | Precinct-5 North Dupree (Precinct-6 Redelm, Precinct-8 South Dupree) | 374 | 364,830 | remainder |
| 357 | Hand | Precinct-03 | 369 | 365,199 | remainder |
| 358 | Bennett | Martin Rural 26/27 Precinct | 368 | 365,567 | remainder |
| 359 | Clay | Precinct-C1 | 368 | 365,935 | remainder |
| 360 | Lyman | Precinct-12 | 366 | 366,301 | remainder |
| 361 | Meade | WEST BLACK HAWK #16 | 360 | 366,661 | remainder |
| 362 | McPherson | Precinct-4 | 359 | 367,020 | remainder |
| 363 | Meade | BLACK HAWK #14 | 357 | 367,377 | remainder |
| 364 | Pennington | Precinct 2-1 | 357 | 367,734 | remainder |
| 365 | Sanborn | Precinct-2 | 357 | 368,091 | remainder |
| 366 | Spink | Precinct-04 | 356 | 368,447 | remainder |
| 367 | Grant | Precinct-22 | 355 | 368,802 | remainder |
| 368 | Charles Mix | Precinct-05 | 354 | 369,156 | remainder |
| 369 | Minnehaha | Precinct-0503 | 354 | 369,510 | remainder |
| 370 | Spink | Precinct-03 | 353 | 369,863 | remainder |
| 371 | Union | Precinct-07 | 353 | 370,216 | remainder |
| 372 | Potter | Absentee Precinct | 348 | 370,564 | remainder |
| 373 | Hand | Precinct-05 | 347 | 370,911 | remainder |
| 374 | Davison | Precinct-01 | 346 | 371,257 | remainder |
| 375 | McPherson | Precinct-1 | 344 | 371,601 | remainder |
| 376 | Grant | Precinct-11 | 340 | 371,941 | remainder |
| 377 | Tripp | WINNER Consolidated-W 2ND | 340 | 372,281 | remainder |
| 378 | Walworth | Precinct-05 | 340 | 372,621 | remainder |
| 379 | Tripp | Lamro Consolidated | 332 | 372,953 | remainder |
| 380 | Haakon | Absentee Precinct | 330 | 373,283 | remainder |
| 381 | Hutchinson | Precinct-06 | 329 | 373,612 | remainder |
| 382 | Douglas | Absentee Precinct | 328 | 373,940 | remainder |
| 383 | Sanborn | Precinct-4 | 328 | 374,268 | remainder |
| 384 | Turner | Precinct-04 | 328 | 374,596 | remainder |
| 385 | Aurora | Precinct-7 | 327 | 374,923 | remainder |
| 386 | Hanson | Precinct-4 | 327 | 375,250 | remainder |
| 387 | Marshall | Precinct-A6 | 327 | 375,577 | remainder |
| 388 | Edmunds | Precinct-3 | 326 | 375,903 | remainder |
| 389 | Hanson | Precinct-3 | 324 | 376,227 | remainder |
| 390 | Hanson | Precinct-5 | 319 | 376,546 | remainder |
| 391 | Deuel | Precinct-03 | 318 | 376,864 | remainder |
| 392 | Hand | Precinct-02 | 315 | 377,179 | remainder |
| 393 | McPherson | Precinct-3 | 315 | 377,494 | remainder |
| 394 | Perkins | Precinct-12 | 315 | 377,809 | remainder |
| 395 | Deuel | Precinct-09 | 314 | 378,123 | remainder |
| 396 | Hand | Precinct-04 | 314 | 378,437 | remainder |
| 397 | Beadle | Precinct 9 | 313 | 378,750 | remainder |
| 398 | Meade | SOUTHWEST STURGIS #4A | 313 | 379,063 | remainder |
| 399 | Roberts | Precinct-12 (Precinct-14) | 313 | 379,376 | remainder |
| 400 | Kingsbury | Badger Precinct | 311 | 379,687 | remainder |
| 401 | Bennett | Martin City Precinct | 308 | 379,995 | remainder |
| 402 | Tripp | WINNER Consolidated-E 3RD | 308 | 380,303 | remainder |
| 403 | Codington | FULLER, FLORENCE | 307 | 380,610 | remainder |
| 404 | Lyman | Precinct-04 | 307 | 380,917 | remainder |
| 405 | Grant | Precinct-42 | 305 | 381,222 | remainder |
| 406 | Marshall | Precinct-A9 | 305 | 381,527 | remainder |
| 407 | Todd | Saint Francis | 305 | 381,832 | remainder |
| 408 | Deuel | Precinct-08 | 304 | 382,136 | remainder |
| 409 | Yankton | Mayfield Store | 304 | 382,440 | remainder |
| 410 | Beadle | Precinct 8 | 302 | 382,742 | remainder |
| 411 | Day | Precinct-03 | 299 | 383,041 | remainder |
| 412 | Douglas | Precinct-1 | 299 | 383,340 | remainder |
| 413 | Butte | Precinct-26 | 298 | 383,638 | remainder |
| 414 | Dewey | Precinct-14 Eagle Butte South | 295 | 383,933 | remainder |
| 415 | Meade | EAST STURGIS #1 | 295 | 384,228 | remainder |
| 416 | Douglas | Precinct-2 | 294 | 384,522 | remainder |
| 417 | Aurora | Precinct-1 | 291 | 384,813 | remainder |
| 418 | Day | Precinct-01 | 289 | 385,102 | remainder |
| 419 | Yankton | Lesterville Fire Hall | 288 | 385,390 | remainder |
| 420 | Edmunds | Precinct-4 | 287 | 385,677 | remainder |
| 421 | Hamlin | Precinct-23 | 287 | 385,964 | remainder |
| 422 | Potter | Hoven Legion Hall | 287 | 386,251 | remainder |
| 423 | Buffalo | Precinct-3 | 286 | 386,537 | remainder |
| 424 | Perkins | Precinct-03 | 285 | 386,822 | remainder |
| 425 | Butte | Precinct-14 | 281 | 387,103 | remainder |
| 426 | McPherson | Precinct-2 | 281 | 387,384 | remainder |
| 427 | Pennington | Precinct SR | 281 | 387,665 | remainder |
| 428 | Custer | Precinct-07 | 280 | 387,945 | remainder |
| 429 | Roberts | Precinct-13 | 280 | 388,225 | remainder |
| 430 | Butte | Precinct-21 | 279 | 388,504 | remainder |
| 431 | Dewey | Precinct-07 Eagle Butte East | 278 | 388,782 | remainder |
| 432 | Day | Precinct-02 | 277 | 389,059 | remainder |
| 433 | Lake | Concord-Badus-Wayne/Ramona | 277 | 389,336 | remainder |
| 434 | Meade | CENTRAL STURGIS #3 | 276 | 389,612 | remainder |
| 435 | Dewey | Precinct-12 Eagle Butte North (Precinct-13 Eagle Butte North) | 273 | 389,885 | remainder |
| 436 | Faulk | Precinct-7 | 273 | 390,158 | remainder |
| 437 | Perkins | Precinct-01 | 273 | 390,431 | remainder |
| 438 | Codington | KRANZBURG, KRANZBURG | 272 | 390,703 | remainder |
| 439 | Jackson | Precinct-3 | 268 | 390,971 | remainder |
| 440 | Pennington | Precinct QU | 268 | 391,239 | remainder |
| 441 | Marshall | Precinct-A4 | 266 | 391,505 | remainder |
| 442 | Sanborn | Precinct-1 | 265 | 391,770 | remainder |
| 443 | Meade | WEST ELK VALE #24 | 264 | 392,034 | remainder |
| 444 | Codington | SHERIDAN | 262 | 392,296 | remainder |
| 445 | Sanborn | Precinct-5 | 262 | 392,558 | remainder |
| 446 | Jackson | Precinct-7 | 260 | 392,818 | remainder |
| 447 | Todd | Parmelee | 260 | 393,078 | remainder |
| 448 | Codington | KAMPESKA (RICHLAND) | 259 | 393,337 | remainder |
| 449 | Butte | Precinct-23 | 258 | 393,595 | remainder |
| 450 | Meade | FAITH #31 | 258 | 393,853 | remainder |
| 451 | Bennett | Allen Precinct | 257 | 394,110 | remainder |
| 452 | Todd | S. Antelope | 257 | 394,367 | remainder |
| 453 | Douglas | Precinct-5 | 255 | 394,622 | remainder |
| 454 | Butte | Precinct-27 | 254 | 394,876 | remainder |
| 455 | Butte | Precinct-13 | 250 | 395,126 | remainder |
| 456 | Lyman | Precinct-09 | 248 | 395,374 | remainder |
| 457 | Lincoln | 08 | 246 | 395,620 | remainder |
| 458 | Oglala Lakota | Wound Knee District School Gym | 244 | 395,864 | remainder |
| 459 | Codington | GERMANTOWN (RAUVILLE) | 243 | 396,107 | remainder |
| 460 | Meade | STURGIS #5A | 243 | 396,350 | remainder |
| 461 | Douglas | Precinct-4 | 242 | 396,592 | remainder |
| 462 | Tripp | WINNER Consolidated-E 2ND | 242 | 396,834 | remainder |
| 463 | Brown | Frederick Community Center | 241 | 397,075 | remainder |
| 464 | Douglas | Precinct-3 | 240 | 397,315 | remainder |
| 465 | Marshall | Precinct-A8 | 239 | 397,554 | remainder |
| 466 | Brown | Columbia Legion | 237 | 397,791 | remainder |
| 467 | Kingsbury | Oldham Precinct | 237 | 398,028 | remainder |
| 468 | Mellette | Precinct-2 | 237 | 398,265 | remainder |
| 469 | Butte | Precinct-20 | 236 | 398,501 | remainder |
| 470 | Codington | GRACELAND, HENRY, HENRY | 236 | 398,737 | remainder |
| 471 | Spink | Precinct-05 | 236 | 398,973 | remainder |
| 472 | Grant | Precinct-47 | 231 | 399,204 | remainder |
| 473 | Faulk | Precinct-6 | 229 | 399,433 | remainder |
| 474 | Butte | Precinct-22 | 224 | 399,657 | remainder |
| 475 | Day | Precinct-08 | 224 | 399,881 | remainder |
| 476 | Grant | Precinct-41 | 224 | 400,105 | remainder |
| 477 | Grant | Precinct-46 | 220 | 400,325 | remainder |
| 478 | Miner | Precinct-6 | 220 | 400,545 | remainder |
| 479 | Custer | Precinct-03 | 219 | 400,764 | remainder |
| 480 | Marshall | Precinct-A1 | 219 | 400,983 | remainder |
| 481 | Deuel | Precinct-11 | 218 | 401,201 | remainder |
| 482 | Deuel | Precinct-05 | 217 | 401,418 | remainder |
| 483 | Lawrence | Precinct-05 | 216 | 401,634 | remainder |
| 484 | Brown | Hecla Community Center | 214 | 401,848 | remainder |
| 485 | Custer | Precinct-10 | 214 | 402,062 | remainder |
| 486 | Ziebach | Precinct-3 Davis | 214 | 402,276 | remainder |
| 487 | Day | Precinct-07 | 213 | 402,489 | remainder |
| 488 | Deuel | Precinct-07 | 212 | 402,701 | remainder |
| 489 | Fall River | Oelrichs Area | 212 | 402,913 | remainder |
| 490 | Kingsbury | Iroquois Precinct | 212 | 403,125 | remainder |
| 491 | Day | Precinct-09 | 209 | 403,334 | remainder |
| 492 | Lyman | Precinct-07 | 209 | 403,543 | remainder |
| 493 | Lake | Nunda-Summit | 208 | 403,751 | remainder |
| 494 | Meade | WEST STURGIS #4 | 208 | 403,959 | remainder |
| 495 | Turner | Precinct-07 | 208 | 404,167 | remainder |
| 496 | Aurora | Precinct-5 | 206 | 404,373 | remainder |
| 497 | Clay | Precinct-C2 | 206 | 404,579 | remainder |
| 498 | Fall River | CAS | 202 | 404,781 | remainder |
| 499 | Roberts | Precinct-03 | 202 | 404,983 | remainder |
| 500 | Clark | Precinct-06 | 201 | 405,184 | remainder |
| 501 | Dewey | Precinct-15 Eagle Butte West | 200 | 405,384 | remainder |
| 502 | Hughes | 5. Blunt City Hall | 200 | 405,584 | remainder |
| 503 | Campbell | Precinct-5 | 199 | 405,783 | remainder |
| 504 | Fall River | BEA | 199 | 405,982 | remainder |
| 505 | Corson | McIntosh Precinct | 198 | 406,180 | remainder |
| 506 | Charles Mix | Precinct-06 | 197 | 406,377 | remainder |
| 507 | Corson | Morristown Precinct | 196 | 406,573 | remainder |
| 508 | Brown | Westport Town Hall | 194 | 406,767 | remainder |
| 509 | Sully | Absentee Precinct | 194 | 406,961 | remainder |
| 510 | Corson | Lincoln Precinct | 193 | 407,154 | remainder |
| 511 | Deuel | Precinct-10 | 193 | 407,347 | remainder |
| 512 | Marshall | Precinct-A7 | 193 | 407,540 | remainder |
| 513 | Mellette | Precinct-5 | 193 | 407,733 | remainder |
| 514 | Roberts | Precinct-10 | 193 | 407,926 | remainder |
| 515 | Charles Mix | Precinct-02 | 192 | 408,118 | remainder |
| 516 | Marshall | Precinct-A2 | 190 | 408,308 | remainder |
| 517 | Miner | Precinct-7 | 189 | 408,497 | remainder |
| 518 | Clark | Precinct-08 | 188 | 408,685 | remainder |
| 519 | Clay | Precinct-E2 | 188 | 408,873 | remainder |
| 520 | Charles Mix | Precinct-08 | 187 | 409,060 | remainder |
| 521 | Marshall | Precinct-A5 | 187 | 409,247 | remainder |
| 522 | Clark | Precinct-07 | 185 | 409,432 | remainder |
| 523 | Custer | Precinct-02 | 184 | 409,616 | remainder |
| 524 | Clark | Precinct-11 | 182 | 409,798 | remainder |
| 525 | Deuel | Precinct-06 | 182 | 409,980 | remainder |
| 526 | Marshall | Precinct-A3 | 182 | 410,162 | remainder |
| 527 | Meade | NORTHEAST STURGIS #1-A | 176 | 410,338 | remainder |
| 528 | Clark | Precinct-13 | 175 | 410,513 | remainder |
| 529 | Hamlin | Precinct-02 | 175 | 410,688 | remainder |
| 530 | McCook | Precinct-02 | 175 | 410,863 | remainder |
| 531 | Corson | McLaughlin Precinct | 174 | 411,037 | remainder |
| 532 | Faulk | Precinct-1 | 174 | 411,211 | remainder |
| 533 | Meade | BEAR BUTTE #9 | 172 | 411,383 | remainder |
| 534 | Tripp | WINNER Consolidated-W 3RD | 172 | 411,555 | remainder |
| 535 | Walworth | Precinct-04 | 172 | 411,727 | remainder |
| 536 | Deuel | Precinct-04 | 171 | 411,898 | remainder |
| 537 | Clark | Precinct-12 | 170 | 412,068 | remainder |
| 538 | Lawrence | Precinct-06 | 170 | 412,238 | remainder |
| 539 | Pennington | Precinct NH | 170 | 412,408 | remainder |
| 540 | Deuel | Precinct-01 | 169 | 412,577 | remainder |
| 541 | Roberts | Precinct-01 | 169 | 412,746 | remainder |
| 542 | Tripp | Clearfield Consolidated | 169 | 412,915 | remainder |
| 543 | Meade | ALKALI #6A | 168 | 413,083 | remainder |
| 544 | Tripp | Lake Consolidated | 168 | 413,251 | remainder |
| 545 | Campbell | Precinct-3 | 166 | 413,417 | remainder |
| 546 | Clark | Precinct-09 | 166 | 413,583 | remainder |
| 547 | Sully | Bill Floyd Shop | 164 | 413,747 | remainder |
| 548 | Campbell | Precinct-2 | 163 | 413,910 | remainder |
| 549 | Campbell | Precinct-4 | 163 | 414,073 | remainder |
| 550 | Grant | Precinct-54 | 161 | 414,234 | remainder |
| 551 | Lawrence | Precinct-08 | 161 | 414,395 | remainder |
| 552 | Walworth | Precinct-10 | 161 | 414,556 | remainder |
| 553 | Mellette | Precinct-6 | 159 | 414,715 | remainder |
| 554 | Miner | Precinct-4 | 159 | 414,874 | remainder |
| 555 | Grant | Precinct-45 | 158 | 415,032 | remainder |
| 556 | Jackson | Precinct-4 | 158 | 415,190 | remainder |
| 557 | Jerauld | Precinct-2 | 158 | 415,348 | remainder |
| 558 | Brown | Stratford Communty Center | 157 | 415,505 | remainder |
| 559 | Brule | Precinct-04 | 157 | 415,662 | remainder |
| 560 | Bennett | Vetal/Tuthill Precinct | 155 | 415,817 | remainder |
| 561 | Grant | Precinct-21 | 155 | 415,972 | remainder |
| 562 | Jones | Precinct-1 | 155 | 416,127 | remainder |
| 563 | Spink | Precinct-08 | 155 | 416,282 | remainder |
| 564 | Charles Mix | Precinct-04 | 152 | 416,434 | remainder |
| 565 | Harding | Precinct-01 | 152 | 416,586 | remainder |
| 566 | Harding | Precinct-02 | 152 | 416,738 | remainder |
| 567 | Mellette | Precinct-3 | 151 | 416,889 | remainder |
| 568 | Walworth | Precinct-02 | 151 | 417,040 | remainder |
| 569 | Codington | EDEN, PHIPPS, WALLACE | 150 | 417,190 | remainder |
| 570 | Miner | Precinct-1 | 150 | 417,340 | remainder |
| 571 | Aurora | Precinct-2 | 149 | 417,489 | remainder |
| 572 | Clark | Precinct-01 | 149 | 417,638 | remainder |
| 573 | Haakon | Midland Fire Hall | 148 | 417,786 | remainder |
| 574 | Edmunds | Precinct-6 | 147 | 417,933 | remainder |
| 575 | Oglala Lakota | Bill Conquering Bear Gymnasium/Oglala Lakota County Schools | 146 | 418,079 | remainder |
| 576 | Perkins | Precinct-05 | 146 | 418,225 | remainder |
| 577 | Campbell | Precinct-1 | 145 | 418,370 | remainder |
| 578 | Grant | Precinct-44 | 145 | 418,515 | remainder |
| 579 | Hamlin | Precinct-22 | 144 | 418,659 | remainder |
| 580 | Lyman | Precinct-06 | 144 | 418,803 | remainder |
| 581 | Harding | Precinct-05 | 141 | 418,944 | remainder |
| 582 | Walworth | Precinct-01 | 137 | 419,081 | remainder |
| 583 | Codington | LEOLA, SOUTH SHORE | 136 | 419,217 | remainder |
| 584 | Tripp | WINNER Consolidated SE 1ST | 134 | 419,351 | remainder |
| 585 | Brown | Claremont City Hall | 133 | 419,484 | remainder |
| 586 | Jerauld | Precinct-3 | 132 | 419,616 | remainder |
| 587 | Charles Mix | Precinct-10 | 131 | 419,747 | remainder |
| 588 | Faulk | Precinct-2 | 131 | 419,878 | remainder |
| 589 | Miner | Precinct-2 | 130 | 420,008 | remainder |
| 590 | Perkins | Precinct-07 | 130 | 420,138 | remainder |
| 591 | Harding | Precinct-09 | 129 | 420,267 | remainder |
| 592 | Butte | Precinct-18 | 127 | 420,394 | remainder |
| 593 | Charles Mix | Precinct-07 | 127 | 420,521 | remainder |
| 594 | Dewey | Precinct-06 Isabel | 125 | 420,646 | remainder |
| 595 | Meade | CHALK BUTTE #27 | 124 | 420,770 | remainder |
| 596 | Perkins | Precinct-06 | 124 | 420,894 | remainder |
| 597 | Miner | Precinct-3 | 123 | 421,017 | remainder |
| 598 | Faulk | Precinct-3 | 122 | 421,139 | remainder |
| 599 | Todd | Lakeview | 121 | 421,260 | remainder |
| 600 | Clark | Precinct-02 | 120 | 421,380 | remainder |
| 601 | Jackson | Precinct-2 | 119 | 421,499 | remainder |
| 602 | Jackson | Precinct-6 | 118 | 421,617 | remainder |
| 603 | Miner | Precinct-8 | 118 | 421,735 | remainder |
| 604 | Spink | Precinct-06 | 118 | 421,853 | remainder |
| 605 | Codington | WAVERLY | 117 | 421,970 | remainder |
| 606 | Jerauld | Precinct-5 | 116 | 422,086 | remainder |
| 607 | Roberts | Precinct-08 | 115 | 422,201 | remainder |
| 608 | Codington | DEXTER | 114 | 422,315 | remainder |
| 609 | Meade | VIEWFIELD #17 | 114 | 422,429 | remainder |
| 610 | Oglala Lakota | Wakan Tiospaye #12 Community Building | 112 | 422,541 | remainder |
| 611 | Tripp | Sully Consolidated | 111 | 422,652 | remainder |
| 612 | Tripp | Witten Consolidated | 111 | 422,763 | remainder |
| 613 | Buffalo | Precinct-1 | 108 | 422,871 | remainder |
| 614 | Clark | Precinct-10 | 108 | 422,979 | remainder |
| 615 | Stanley | Precinct-03 | 107 | 423,086 | remainder |
| 616 | Grant | Precinct-49 | 106 | 423,192 | remainder |
| 617 | Hughes | 6. Harrold City Auditorium | 106 | 423,298 | remainder |
| 618 | Faulk | Precinct-5 | 105 | 423,403 | remainder |
| 619 | Perkins | Precinct-02 | 104 | 423,507 | remainder |
| 620 | Todd | OKreek | 104 | 423,611 | remainder |
| 621 | Day | Precinct-06 | 102 | 423,713 | remainder |
| 622 | Harding | Precinct-07 | 102 | 423,815 | remainder |
| 623 | Clark | Precinct-04 | 101 | 423,916 | remainder |
| 624 | Jerauld | Precinct-4 | 100 | 424,016 | remainder |
| 625 | Lyman | Precinct-13 | 100 | 424,116 | remainder |
| 626 | Charles Mix | Precinct-12 | 99 | 424,215 | remainder |
| 627 | Corson | Wakpala Precinct | 99 | 424,314 | remainder |
| 628 | Clark | Precinct-03 | 97 | 424,411 | remainder |
| 629 | Pennington | Precinct WS | 97 | 424,508 | remainder |
| 630 | Faulk | Precinct-4 | 96 | 424,604 | remainder |
| 631 | Meade | ELM SPRINGS #18 | 95 | 424,699 | remainder |
| 632 | Butte | Precinct-11 | 93 | 424,792 | remainder |
| 633 | Grant | Precinct-12 | 93 | 424,885 | remainder |
| 634 | Tripp | Hamill Consolidated | 93 | 424,978 | remainder |
| 635 | Butte | Precinct-12 | 92 | 425,070 | remainder |
| 636 | Haakon | Milesville Hall | 91 | 425,161 | remainder |
| 637 | Roberts | Precinct-04 | 91 | 425,252 | remainder |
| 638 | Dewey | Precinct-11 Swiftbird/LaPlant | 89 | 425,341 | remainder |
| 639 | Grant | Precinct-32 | 89 | 425,430 | remainder |
| 640 | Perkins | Precinct-09 | 89 | 425,519 | remainder |
| 641 | Sully | Agar Fire Hall | 88 | 425,607 | remainder |
| 642 | Meade | PINE #33 | 87 | 425,694 | remainder |
| 643 | Walworth | Precinct-08 | 87 | 425,781 | remainder |
| 644 | Stanley | Precinct-02 | 86 | 425,867 | remainder |
| 645 | Jackson | Precinct-5 | 85 | 425,952 | remainder |
| 646 | Todd | Jeanette | 84 | 426,036 | remainder |
| 647 | Corson | Little Eagle Precinct | 83 | 426,119 | remainder |
| 648 | Corson | Ridgeland Precinct | 83 | 426,202 | remainder |
| 649 | Meade | RED OWL #30 | 83 | 426,285 | remainder |
| 650 | Oglala Lakota | Red Shirt School | 83 | 426,368 | remainder |
| 651 | Grant | Precinct-52 | 82 | 426,450 | remainder |
| 652 | Walworth | Precinct-09 | 82 | 426,532 | remainder |
| 653 | Day | Precinct-10 | 81 | 426,613 | remainder |
| 654 | Meade | ELK VALE #21 | 81 | 426,694 | remainder |
| 655 | Miner | Precinct-5 | 78 | 426,772 | remainder |
| 656 | Jackson | Precinct-8 | 77 | 426,849 | remainder |
| 657 | Tripp | Ideal Consolidated | 76 | 426,925 | remainder |
| 658 | Charles Mix | Precinct-13 | 74 | 426,999 | remainder |
| 659 | Buffalo | Precinct-2 | 72 | 427,071 | remainder |
| 660 | Lyman | Precinct-01 | 72 | 427,143 | remainder |
| 661 | Dewey | Precinct-09 Promise | 68 | 427,211 | remainder |
| 662 | Todd | Bordeaux | 67 | 427,278 | remainder |
| 663 | Perkins | Precinct-08 | 64 | 427,342 | remainder |
| 664 | Dewey | Precinct-05 Firesteel | 63 | 427,405 | remainder |
| 665 | Ziebach | Precinct-4 Glad Valley | 63 | 427,468 | remainder |
| 666 | Meade | HEREFORD #20 | 62 | 427,530 | remainder |
| 667 | Corson | Kenel Precinct | 61 | 427,591 | remainder |
| 668 | Perkins | Precinct-04 | 61 | 427,652 | remainder |
| 669 | Harding | Precinct-08 | 60 | 427,712 | remainder |
| 670 | Todd | Fairgrounds-10 | 59 | 427,771 | remainder |
| 671 | Ziebach | Precinct-2 Cherry Creek | 59 | 427,830 | remainder |
| 672 | Grant | Precinct-31 | 57 | 427,887 | remainder |
| 673 | Grant | Precinct-53 | 56 | 427,943 | remainder |
| 674 | Pennington | Precinct RK | 56 | 427,999 | remainder |
| 675 | Corson | Bullhead Precinct | 55 | 428,054 | remainder |
| 676 | Dewey | Precinct-08 White Horse | 54 | 428,108 | remainder |
| 677 | Meade | MARCUS #41 | 54 | 428,162 | remainder |
| 678 | Harding | Precinct-03 | 53 | 428,215 | remainder |
| 679 | Meade | SULPHUR #35 | 50 | 428,265 | remainder |
| 680 | Meade | WHITE OWL #25 | 49 | 428,314 | remainder |
| 681 | Butte | Precinct-06 | 47 | 428,361 | remainder |
| 682 | Haakon | Deep Creek Church | 47 | 428,408 | remainder |
| 683 | Ziebach | Precinct-7 Red Scaffold | 46 | 428,454 | remainder |
| 684 | Jackson | Precinct-1 | 44 | 428,498 | remainder |
| 685 | Dewey | Precinct-02 Trail City | 42 | 428,540 | remainder |
| 686 | Meade | FAIRPOINT #29 | 37 | 428,577 | remainder |
| 687 | Meade | FORT MEADE #1A | 35 | 428,612 | remainder |
| 688 | Meade | UNION #40 | 32 | 428,644 | remainder |
| 689 | Harding | Precinct-06 | 31 | 428,675 | remainder |
| 690 | Butte | Precinct-08 | 28 | 428,703 | remainder |
| 691 | Ziebach | Precinct-1 Bridger | 25 | 428,728 | remainder |
