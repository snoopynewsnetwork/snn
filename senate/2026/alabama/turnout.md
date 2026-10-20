# Alabama reported vote volume

Observed 2026-10-20 UTC. **Complete historical native reporting coverage is recovered: 2,085 labeled 2024 columns across all 67 counties.** The priority denominator is **2,265,090 reported 2024 presidential candidate and generic write-in votes**, independently extracted from the [official statewide precinct archive](https://www.sos.alabama.gov/sites/default/files/election-data/2024-12/2024-General%20Precinct%20Level%20Results.zip) and reconciled for every county/candidate to the [certified November 26 canvass, PDF pages 5–6](https://www.sos.alabama.gov/sites/default/files/election-2024/State%20Certification%20of%202024%20General%20Election.pdf). Alabama had no 2024 U.S. Senate election. These columns are the native historical reporting geography, including absentee and provisional contexts, rather than 2,085 approved physical precinct polygons.

**Top 15: 115,428 / 2,265,090 = 5.0959564521%. Minimum descending 80% set: 887 units, 1,812,818 / 2,265,090 = 80.0329346737%.** The preceding 886 units have 1,811,981 votes (79.9959824996%). Calhoun’s **OAK GROVE BAPT**, source column 30, adds 837 and crosses the threshold. The remaining **1,198 units / 452,272 votes** remain in statewide arithmetic. No crossing tie occurs. Full [descending order](data/turnout/native-order-2024.csv), [ordered 887-unit set](data/turnout/priority-native-2024.csv), [ordered remainder](data/turnout/remainder-native-2024.csv) and [exact dispatch contract](data/turnout/priority-set.json) retain every literal label, parent FIPS and source column. All these calculations use the [original precinct archive](https://www.sos.alabama.gov/sites/default/files/election-data/2024-12/2024-General%20Precinct%20Level%20Results.zip).

The contract is a measured **historical** priority. **Bounded independent peer agreement is verified against the captured final historical baseline evidence; coordinator acceptance remains false/pending.** No peer existed at the original turnout launch; the exact original report and all 146 original-phase files remain captured. No dispatch acceptance, November 2026 geographic approval or cross-year unit equivalence is claimed. The compatibility file [county-turnout.csv](data/county-turnout.csv) contains the separate 67-county parent sensitivity for three elections; it never substitutes county totals for native reporting columns.

## Exact top 15 native contexts

| Rank | County | Literal native reporting label | Candidate/write-in votes |
| ---: | --- | --- | ---: |
| 1 | Madison | ABSENTEE | 15,691 |
| 2 | Jefferson | BIRMINGHAM ABSENTEE | 11,383 |
| 3 | Mobile | ABSENTEE | 8,595 |
| 4 | Shelby | PELHAM CIVIC COMPLEX | 7,921 |
| 5 | Baldwin | ABSENTEE | 7,787 |
| 6 | Shelby | HELENA COMM_ CTR_ | 7,544 |
| 7 | Shelby | KINGWOOD CHURCH | 7,403 |
| 8 | Lee | SMITHS JR_ HIGH | 7,095 |
| 9 | Montgomery | ABSENTEE | 6,776 |
| 10 | Tuscaloosa | BOBBY MILLER ACTIVITY | 6,196 |
| 11 | Jackson | SCOTTSBORO REC COMM BLDG | 5,894 |
| 12 | Shelby | ABSENTEE | 5,875 |
| 13 | Limestone | JAMES CLEMENS HIGH SCHOOL | 5,848 |
| 14 | Montgomery | 512 ST JAMES METHODIST | 5,752 |
| 15 | Baldwin | FAIRHOPE 3 CIRCLE CH | 5,668 |

Source: [official 2024 precinct workbooks](https://www.sos.alabama.gov/sites/default/files/election-data/2024-12/2024-General%20Precinct%20Level%20Results.zip), `Precinct Results` sheet, each candidate row and the header column pinned in [native-units-2024.json](data/turnout/native-units-2024.json). The largest context is Madison ABSENTEE, 15,691 candidate votes; its separate source ballot field is 15,310, demonstrating why the two measures cannot be interchanged.

## Integer threshold, hierarchy and candidate universe

Sort by reported candidate/write-in votes descending, then the complete source-scoped key ascending for reproducible ties. The smallest k satisfies `5 × cumulative(k) >= 4 × statewide_votes`. Here `5 × 1,811,981 = 9,059,905 < 9,060,360 = 4 × 2,265,090 <= 9,064,090 = 5 × 1,812,818`. Since the largest 886 units cannot reach 80%, no smaller set can. Exact rational weights and cumulative fractions are retained without rounded-threshold decisions. [Source archive](https://www.sos.alabama.gov/sites/default/files/election-data/2024-12/2024-General%20Precinct%20Level%20Results.zip); [calculation](data/turnout/scripts/build.py).

The disjoint arithmetic layer is the set of labeled columns within each county workbook. County and statewide controls are overlapping parents and are never added to their constituents. In 2024 there are 1,947 ordinary precinct/site reporting columns, 68 absentee columns, 67 provisional columns and 3 combined provisional/absentee columns. Classification uses explicit method words, including the literal misspelling `PROVSIONAL`; a church or school named “Central” is not a central-counting method. Ordinary columns have **unspecified method**, not proven Election Day exclusivity. Native column labels can represent combined precincts (for example Jefferson `PREC 1065/4060 - CENTER POINT`), sites, split names or administrative contexts. We do not merge them by similar names. [All original headers](https://www.sos.alabama.gov/sites/default/files/election-data/2024-12/2024-General%20Precinct%20Level%20Results.zip); [complete typed extracts](data/turnout/source/workbooks-2024.json.gz); [coverage](data/turnout/native-coverage.json).

Keys preserve election, county FIPS, original 1-based source column and percent-encoded literal header. The source has no separate statewide numeric precinct-ID field; `native_id` therefore retains the source header, with standalone numeric ID null. County FIPS is verified against the [Census reference](https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt); it does not validate precinct geography. All 67 parents have complete constituent arrays, explicit administrative geometry cases and unavailable current-ID/write-in-detail cases in the contract. The 887-unit set touches 63 counties; Conecuh, Greene, Lowndes, Washington have no priority unit but every one of their units remains in the order and denominator.

| Contest and source status | Published candidate / ballot identity | Native statewide votes | Canvass control |
| --- | --- | ---: | ---: |
| 2024 President | Kamala D. Harris (D / DEM) | 772,412 | 772,412 |
| 2024 President | Donald J. Trump (R / REP) | 1,462,616 | 1,462,616 |
| 2024 President | Robert F. Kennedy Jr. (I / IND) | 12,075 | 12,075 |
| 2024 President | Jill Stein (I / IND) | 4,319 | 4,319 |
| 2024 President | Chase Oliver (I / IND) | 4,930 | 4,930 |
| 2024 President | Write-In (generic Write-In / NON) | 8,738 | 8,738 |
| 2022 U.S. Senate | Will Boyd (D / DEM) | 436,746 | 436,746 |
| 2022 U.S. Senate | Katie Britt (R / REP) | 942,154 | 942,154 |
| 2022 U.S. Senate | John Sophocleus (L / LIB) | 32,879 | 32,879 |
| 2022 U.S. Senate | Write-In (generic Write-In / NON) | 2,459 | 2,459 |
| 2020 U.S. Senate | Doug Jones (D / DEM) | 920,478 | 920,478 |
| 2020 U.S. Senate | Tommy Tuberville (R / REP) | 1,392,076 | 1,392,076 |
| 2020 U.S. Senate | Write-In (generic Write-In / NON) | 3,891 | 3,891 |

Sources: [2024 canvass PDF 5–6](https://www.sos.alabama.gov/sites/default/files/election-2024/State%20Certification%20of%202024%20General%20Election.pdf), [2022 canvass PDF 4–5](https://www.sos.alabama.gov/sites/default/files/election-data/2022-11/Final%20Canvass%20of%20Results%20%28canvassed%20by%20state%20canvassing%20board%2011-28-2022%29.pdf), [2020 canvass PDF 3–4](https://www.sos.alabama.gov/sites/default/files/election-2020/Final%20Canvass%20of%20Results-Merged.pdf); independently extracted [2024](https://www.sos.alabama.gov/sites/default/files/election-data/2024-12/2024-General%20Precinct%20Level%20Results.zip), [2022](https://www.sos.alabama.gov/sites/default/files/election-data/2022-11/2022%20General%20Precinct%20Level%20Results.zip) and [2020](https://www.sos.alabama.gov/sites/default/files/election-data/2020-12/2020%20General%20Precinct%20Results.zip) native archives. The 2022 Senate is the actual **Class III midterm/other seat**, Boyd–Britt–Sophocleus. The 2020 Jones–Tuberville Senate is the previous **Class II** election. No nonexistent 2024 Senate or governor contest is introduced. Each native candidate’s raw padded name, party, contest string and source row is preserved in [candidate-universe.json](data/turnout/candidate-universe.json). The canonical name used for comparison is an explicit whitespace-trimmed presentation value; no source candidate rows are deduplicated. “NON” is the archive label on a generic Write-In row, not a named independent candidate or proof of eligible/valid write-in adjudication.

Every native candidate sum matches every **numeric** county canvass cell, and all candidate statewide sums match printed totals. Three PDF exceptions stay source-scoped: Wilcox 2024 Stein is blank; Washington 2022 Senate Write-In is blank; Perry 2020 Senate Write-In is a printed dash. They remain null in [canvass-cells.json](data/turnout/canvass-cells.json). Independently downloaded native XLS cells for these scopes are explicit numeric zeros, so native candidate coverage closes without assigning a residual or modifying any PDF null. Legal named/valid write-in allocation remains unavailable. [Candidate reconciliation](data/turnout/candidate-reconciliation.json); [full page visual transcriptions](data/turnout/source/visual-transcriptions.json).

The damaged 2024 embedded OCR was not silently repaired: Hale’s six cells (3,868 / 3,369 / 30 / 10 / 13 / 15) and Winston’s (884 / 10,191 / 36 / 8 / 10 / 20) were read on the complete original page renders. Henry 2022’s numeric row is mistakenly separated under `Total` by text extraction; the printed row is Henry. Exact OCR aliases and raw lines survive alongside explicit joins, character positions and page numbers. Adjacent 2022 Lieutenant Governor and 2020 presidential columns are not added to Senate. All unrelated original PDF pages and XLS rows remain available without a second analytical model of unrelated offices. [Unaltered extraction and warnings](data/turnout/source/SCHEMA.md); [visual evidence](data/turnout/source/visual-transcriptions.json).

## Actual midterm and same-seat comparators

| Native reporting scope | Units | Candidate votes | Top 15 votes / share | Minimum 80% units / votes | Preceding units / votes | Crossing unit | Remainder votes |
| --- | ---: | ---: | --- | --- | --- | --- | ---: |
| 2024 President | 2085 | 2,265,090 | 115,428 / 5.0959564521% | 887 / 1,812,818 | 886 / 1,811,981 | Calhoun: OAK GROVE BAPT (837) | 452,272 |
| 2022 Senate | 2074 | 1,414,238 | 60,242 / 4.2596790639% | 893 / 1,131,580 | 892 / 1,131,060 | Tallapoosa: HACKNEYVILLE COMM CTR (520) | 282,658 |
| 2020 Senate | 2111 | 2,316,445 | 226,674 / 9.7854255119% | 874 / 1,853,909 | 873 / 1,853,059 | Tallapoosa: MANOY V_ H_ (850) | 462,536 |

The comparator orders, exact fractions, full priority and remainder arrays are retained in [native-rank-summary.json](data/turnout/native-rank-summary.json), with complete [2022 order](data/turnout/native-order-2022.csv) and [2020 order](data/turnout/native-order-2020.csv). These are independent election-vintage universes: 2,074 and 2,111 units. The different counts and matching labels establish no crosswalk. Sources: [2022 native archive](https://www.sos.alabama.gov/sites/default/files/election-data/2022-11/2022%20General%20Precinct%20Level%20Results.zip), [2020 native archive](https://www.sos.alabama.gov/sites/default/files/election-data/2020-12/2020%20General%20Precinct%20Results.zip).

## Ballots, registration and method sensitivity

Candidate votes are not ballots cast. Published blank-ballot, contest undervote and overvote fields remain separate and are never inserted into the candidate denominator. Absentee is a method/context or a report statistic, not extra votes to add to county totals. The source’s Democratic/Republican ballot statistics are preserved with their original headers; 2020/2022 explicitly label straight-party ballots, while the 2024 report says Democrat Ballots / Republican Ballots. They are not candidate totals or party registration.

| Election | Official county ballot-report total | Native ballot-field sum | Report registered voters | Report absentee ballots | Raw native registration sum |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2024 | 2,272,911 | 2,272,731 | 3,861,929 | 126,055 | 2,615,488 |
| 2022 | 1,423,409 | 1,423,499 | 3,687,753 | 45,756 | 2,315,170 |
| 2020 | 2,329,114 | 2,329,114 | 3,708,804 | 305,663 | 2,594,783 |

Sources: current linked [2024 Official Total Ballots Cast](https://www.sos.alabama.gov/sites/default/files/election-data/2025-01/2024GeneralElectionTotalBallotsCast.pdf), [2022 Official Total Ballots Cast](https://www.sos.alabama.gov/sites/default/files/election-data/2023-05/General%20Election%202022%20Official%20Total%20Ballots%20Cast.pdf), retained [2020 Total Ballots Cast report](https://www.sos.alabama.gov/sites/default/files/election-2020/2020_General_Total_Ballots_Cast_Report.pdf) and the separate original native archives. Each report’s 67 county sums closes its own statewide footer for all five integer columns. “Registered Voters” is the printed denominator; these reports do not specify active/inactive composition, a registration extract clock, or voting-eligible population. Election date is not an invented registration-as-of timestamp. Report turnout percentages are retained as printed and recomputed from integer totals only for that scope. All 204 county/footer turnout and absentee percentage pairs agree at their displayed precision; [turnout-rates.json](data/turnout/turnout-rates.json) retains exact rational rates and the rounding check.

**Unrepaired source discrepancies:** 2024 Cleburne native ballot sum is 180 below its report; 2022 Cullman native sum is 90 above its report. The 2024 native sum is 2,272,731 versus report 2,272,911; 2022 is 1,423,499 versus 1,423,409. All other county ballot-report comparisons close, including all 67 in 2020. Candidate sums close independently in each election. We do not allocate these discrepancies to candidates, provisional ballots, rejected ballots or a particular unit. Published fields can also fail within-unit identities: 24 native units in 2024 have more candidate votes than their ballot-field value. These are retained source discrepancies, not evidence of a particular cause. [Full county differences](data/turnout/source-discrepancies.json); [every unit arithmetic exception](data/turnout/field-audit.json).

The raw registration fields sum to substantially less than the report totals. Many counties publish zeros throughout their native registration rows; 2024 Madison PROVISIONAL ABSENTEE has a blank registration cell, as do Hale, Henry and Macon PROVISIONAL in 2022. Missing stays null and printed zero stays zero. A 2020 numeric native registration ranking is retained only as a **raw-field sensitivity**, not a complete statewide registration geography. A certified native registration-based priority cannot be established from these fields.

| Source-scoped field | 2024 | 2022 | 2020 |
| --- | --- | --- | --- |
| blank_ballots_source | 611 known sum; 0 unknown cells | 79 known sum; 0 unknown cells | 180 known sum; 28 unknown cells |
| under_votes_source | 4,984 known sum; 47 unknown cells | 8,498 known sum; 99 unknown cells | 13,753 known sum; 0 unknown cells |
| over_votes_source | 3,337 known sum; 47 unknown cells | 414 known sum; 99 unknown cells | 791 known sum; 0 unknown cells |

Walker’s 2024 presidential under/over rows are unavailable for all 47 source units; 2022 Senate under/over rows are unavailable in Butler (23), Dale (20), Tuscaloosa (56). Randolph’s 2020 blank-ballot row is unavailable for 28 units. Unknown rows do not become zeros. Method/context totals and constituent keys for all counties and years are in [field-audit.json](data/turnout/field-audit.json), directly derived from the [2024](https://www.sos.alabama.gov/sites/default/files/election-data/2024-12/2024-General%20Precinct%20Level%20Results.zip), [2022](https://www.sos.alabama.gov/sites/default/files/election-data/2022-11/2022%20General%20Precinct%20Level%20Results.zip) and [2020](https://www.sos.alabama.gov/sites/default/files/election-data/2020-12/2020%20General%20Precinct%20Results.zip) original fields.

| Sensitivity denominator | Total | Top-15 share | Minimum 80% count | Crossing cumulative / preceding cumulative |
| --- | ---: | ---: | ---: | --- |
| 2024 Native ballot fields | 2,272,731 | 5.0726196809% | 887 | 1,818,741 / 1,817,901 |
| 2022 Native ballot fields | 1,423,499 | 4.2532520220% | 895 | 1,139,224 / 1,138,702 |
| 2020 Native ballot fields | 2,329,114 | 9.7604067469% | 875 | 1,863,673 / 1,862,822 |
| 2024 County ballot report | 2,272,911 | 65.7607359021% | 25 | 1,820,610 / 1,796,960 |
| 2022 County ballot report | 1,423,409 | 64.9681152782% | 27 | 1,150,935 / 1,137,490 |
| 2020 County ballot report | 2,329,114 | 65.6874244885% | 26 | 1,877,456 / 1,855,186 |
| 2024 County registered voters report | 3,861,929 | 66.0134093610% | 26 | 3,128,755 / 3,087,768 |
| 2022 County registered voters report | 3,687,753 | 65.7362084717% | 26 | 2,977,022 / 2,937,891 |
| 2020 County registered voters report | 3,708,804 | 65.5917918553% | 26 | 2,983,986 / 2,944,461 |

Full field orders, crossing keys, exact fractions and remainders are in [native ballot sensitivity](data/turnout/native-ballot-registration-sensitivity.json) and [county ballot/registration/absentee sensitivity](data/turnout/ballot-registration-sensitivity.json). These compare source-scoped volume mixes; they are not 2026 forecasts. Native ballot minima use raw native fields and inherit their discrepancies. County registration sensitivity uses each report’s stated registered-voter denominator, not the incomplete native fields. The same official ballot reports and archives cited above supply these calculations.

## All 67 county parents, separate sensitivity

At county aggregation only, the 2024 top 15 contribute **1,489,790 / 2,265,090 = 65.7717794878%**. The smallest county set has **25 counties / 1,814,804 votes = 80.1206133090%**; the preceding 24 have 1,791,248 and Jackson adds 23,556. These are the overlapping parent controls of the [native archive](https://www.sos.alabama.gov/sites/default/files/election-data/2024-12/2024-General%20Precinct%20Level%20Results.zip) reconciled to the [canvass](https://www.sos.alabama.gov/sites/default/files/election-2024/State%20Certification%20of%202024%20General%20Election.pdf), not the native dispatch set.

Ordered 25-county sensitivity: Jefferson, Madison, Mobile, Baldwin, Shelby, Montgomery, Tuscaloosa, Lee, Morgan, Limestone, Calhoun, Etowah, Houston, Lauderdale, St. Clair, Cullman, Elmore, Marshall, Talladega, Walker, DeKalb, Autauga, Blount, Colbert, Jackson. All 42 remainder counties supply 450,286 votes. The 2022 county minimum is 27 (1,144,634 / 1,414,238); 2020 is 26 (1,868,545 / 2,316,445). Complete county orders and remainders are retained in [county-rank-sensitivity.json](data/turnout/county-rank-sensitivity.json); source rows and all separate ballot/registration fields are in the [201-row county CSV](data/county-turnout.csv).

| 2024 county rank | FIPS | County | 2024 president votes | Native contexts | 2024 report ballots | 2024 report registration |
| ---: | --- | --- | ---: | ---: | ---: | ---: |
| 1 | 01073 | Jefferson | 298,704 | 179 | 299,855 | 496,710 |
| 2 | 01089 | Madison | 197,617 | 82 | 197,868 | 333,256 |
| 3 | 01097 | Mobile | 175,164 | 82 | 176,019 | 322,535 |
| 4 | 01003 | Baldwin | 122,249 | 61 | 122,542 | 207,643 |
| 5 | 01117 | Shelby | 114,698 | 40 | 114,957 | 178,381 |
| 6 | 01101 | Montgomery | 89,798 | 53 | 90,268 | 163,649 |
| 7 | 01125 | Tuscaloosa | 85,256 | 56 | 85,509 | 154,607 |
| 8 | 01081 | Lee | 73,127 | 27 | 73,353 | 134,144 |
| 9 | 01103 | Morgan | 53,543 | 41 | 53,721 | 88,627 |
| 10 | 01083 | Limestone | 53,332 | 27 | 53,500 | 82,638 |
| 11 | 01015 | Calhoun | 48,653 | 44 | 48,819 | 84,074 |
| 12 | 01055 | Etowah | 46,137 | 33 | 46,281 | 76,956 |
| 13 | 01069 | Houston | 44,349 | 30 | 44,554 | 82,248 |
| 14 | 01077 | Lauderdale | 43,637 | 33 | 43,816 | 70,858 |
| 15 | 01115 | St. Clair | 43,526 | 32 | 43,621 | 73,065 |
| 16 | 01043 | Cullman | 43,146 | 51 | 43,311 | 66,582 |
| 17 | 01051 | Elmore | 41,624 | 31 | 41,729 | 63,582 |
| 18 | 01095 | Marshall | 40,388 | 31 | 40,499 | 67,826 |
| 19 | 01121 | Talladega | 33,250 | 28 | 33,329 | 61,345 |
| 20 | 01127 | Walker | 29,786 | 47 | 29,888 | 49,215 |
| 21 | 01049 | DeKalb | 29,660 | 46 | 29,756 | 48,071 |
| 22 | 01001 | Autauga | 28,281 | 21 | 28,388 | 46,291 |
| 23 | 01009 | Blount | 28,163 | 26 | 28,138 | 43,601 |
| 24 | 01033 | Colbert | 27,160 | 36 | 27,239 | 45,322 |
| 25 | 01071 | Jackson | 23,556 | 32 | 23,650 | 40,987 |
| 26 | 01031 | Coffee | 22,319 | 29 | 22,367 | 39,771 |
| 27 | 01113 | Russell | 20,718 | 20 | 20,794 | 46,542 |
| 28 | 01123 | Tallapoosa | 20,023 | 28 | 20,127 | 32,576 |
| 29 | 01021 | Chilton | 19,763 | 20 | 19,824 | 31,677 |
| 30 | 01045 | Dale | 19,139 | 20 | 19,207 | 37,101 |
| 31 | 01039 | Covington | 17,095 | 27 | 17,165 | 29,306 |
| 32 | 01079 | Lawrence | 16,122 | 31 | 16,173 | 25,910 |
| 33 | 01047 | Dallas | 15,547 | 31 | 15,631 | 29,534 |
| 34 | 01053 | Escambia | 14,957 | 31 | 15,009 | 28,268 |
| 35 | 01017 | Chambers | 14,245 | 18 | 14,380 | 26,794 |
| 36 | 01093 | Marion | 13,543 | 17 | 13,587 | 22,678 |
| 37 | 01109 | Pike | 13,234 | 36 | 13,292 | 24,517 |
| 38 | 01019 | Cherokee | 13,006 | 25 | 13,030 | 21,383 |
| 39 | 01061 | Geneva | 12,401 | 23 | 12,444 | 20,768 |
| 40 | 01059 | Franklin | 12,097 | 26 | 12,159 | 19,931 |
| 41 | 01025 | Clarke | 11,958 | 31 | 11,993 | 19,143 |
| 42 | 01133 | Winston | 11,149 | 20 | 11,188 | 17,532 |
| 43 | 01111 | Randolph | 11,091 | 22 | 11,128 | 19,342 |
| 44 | 01005 | Barbour | 9,855 | 18 | 9,919 | 17,666 |
| 45 | 01099 | Monroe | 9,815 | 29 | 9,860 | 16,351 |
| 46 | 01091 | Marengo | 9,682 | 20 | 9,719 | 15,710 |
| 47 | 01067 | Henry | 9,320 | 16 | 9,355 | 14,762 |
| 48 | 01007 | Bibb | 9,257 | 10 | 9,278 | 15,152 |
| 49 | 01107 | Pickens | 8,912 | 21 | 8,929 | 14,037 |
| 50 | 01013 | Butler | 8,480 | 23 | 8,530 | 14,530 |
| 51 | 01129 | Washington | 8,441 | 21 | 8,489 | 13,788 |
| 52 | 01057 | Fayette | 8,369 | 26 | 8,417 | 12,897 |
| 53 | 01087 | Macon | 7,834 | 16 | 7,876 | 16,972 |
| 54 | 01029 | Cleburne | 7,651 | 16 | 7,860 | 12,193 |
| 55 | 01065 | Hale | 7,305 | 16 | 7,298 | 12,162 |
| 56 | 01075 | Lamar | 6,890 | 27 | 6,923 | 11,087 |
| 57 | 01027 | Clay | 6,767 | 17 | 6,759 | 10,603 |
| 58 | 01023 | Choctaw | 6,656 | 34 | 6,692 | 10,767 |
| 59 | 01041 | Crenshaw | 6,486 | 17 | 6,516 | 10,851 |
| 60 | 01035 | Conecuh | 6,051 | 29 | 6,105 | 9,820 |
| 61 | 01085 | Lowndes | 5,655 | 14 | 5,708 | 9,668 |
| 62 | 01119 | Sumter | 5,307 | 15 | 5,330 | 9,632 |
| 63 | 01037 | Coosa | 5,268 | 14 | 5,276 | 8,354 |
| 64 | 01131 | Wilcox | 5,263 | 22 | 5,287 | 8,557 |
| 65 | 01105 | Perry | 4,465 | 14 | 4,477 | 7,631 |
| 66 | 01011 | Bullock | 4,111 | 10 | 4,144 | 7,181 |
| 67 | 01063 | Greene | 4,039 | 16 | 4,056 | 6,572 |

Sources for every row: [2024 original archive](https://www.sos.alabama.gov/sites/default/files/election-data/2024-12/2024-General%20Precinct%20Level%20Results.zip), [2024 certified canvass](https://www.sos.alabama.gov/sites/default/files/election-2024/State%20Certification%20of%202024%20General%20Election.pdf), [official ballot report](https://www.sos.alabama.gov/sites/default/files/election-data/2025-01/2024GeneralElectionTotalBallotsCast.pdf), [Census county FIPS](https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt). No population/VTD/name-based allocation was used.

## Current context and bounded qualifications

The current [2026 SOS authority page](https://www.sos.alabama.gov/alabama-votes/voter/election-information/2026) was downloaded in full on October 20. Its signed August 26 [Democratic state certification](https://www.sos.alabama.gov/sites/default/files/election-2026/2026GeneralElectionStateCertificationofDemocraticCandidates.pdf) (PDF 3) lists Everett Wess for U.S. Senate; the [Republican state certification](https://www.sos.alabama.gov/sites/default/files/election-2026/2026GeneralElectionStateCertificationofRepublicanCandidates.pdf) (PDF 2) lists Barry Moore. The complete one-page [independent certification](https://www.sos.alabama.gov/sites/default/files/election-2026/2026GeneralElection-StateCertificationofIndependentCandidate.pdf) has state legislative entries and no U.S. Senate entry. The linked [Autauga common sample](https://www.sos.alabama.gov/sites/default/files/sample-ballots/2026/gen/Autauga-Sample.pdf) visibly displays Everett Wess (Democrat), Barry Moore (Republican), and a separate Write-in line for November 3. These are dated bounded observations; one sample and the retained certifications do not exhaust later amendments, legal eligibility, write-in adjudication or all county ballot styles. They do not change the historical ranking universe. Images and page regions are pinned in [visual-transcriptions.json](data/turnout/source/visual-transcriptions.json).

The linked [2026 Voter Guide](https://www.sos.alabama.gov/sites/default/files/election-2026/2026-VoterGuide.pdf) gives 7 a.m.–7 p.m. polling hours with Eastern-time qualification (PDF 7), separates provisional procedures (PDF 9–10), and gives general absentee application/delivery deadlines with a UOCAVA exception (PDF 3 and later absentee sections). These are method/eligibility context, not a current count of accepted ballots. The guide’s general-election description permits straight-party or individual candidate marking (PDF 11). This assignment has not exhausted later law/dockets, approved November native IDs/geometry, November vote counts, publication cadence, exact outstanding votes or probability calibration. No live collector or calibrated Needle is implemented or claimed.

## Reproduction, original bytes and QA

The [original-first witness](data/turnout/source/original-first-witness.json) pins every complete original body and all 201 ZIP-member hashes, before any peer derivative. Original retained canvasses are reused read-only by individual immutable hash and receipt; the 46,116,016-byte 2024 PDF reconstructs losslessly from its single 29,769,765-byte shared gzip. Every stored artifact is strictly below 40,000,000 bytes. Requested/final URLs, UTC retrieval, status, headers and redirects are retained for fresh downloads; [download-chains.json](data/turnout/source/download-chains.json) pins each actual authority hyperlink with original parent hash and HTML position; ZIP member names, sizes, CRCs and source timestamps are pinned. Existing shared receipt limitations and the failed Census API / successful direct Census recovery remain explicit in [acquisition qualifications](data/turnout/source/acquisition-qualifications.json). No protected data or private-cell reconstruction is used.

Run the offline sequence in [SCHEMA.md](data/turnout/source/SCHEMA.md). [validation.json](data/turnout/validation.json) records comparison of 6,246,656 raw cells and 85,129 target candidate/method/administrative cells against all 201 original XLS members, plus identity checks, primary statewide/county candidate reconciliation, disjoint coverage, exact rank/threshold proofs, source and asset hashes, missing-field semantics and link/bounds checks. [final-seal.json](data/turnout/final-seal.json) records the bounded completion state; [asset-manifest.json](data/turnout/asset-manifest.json) inventories every owned artifact except itself, including scripts, histories, receipts, report, validation and seal. It also pins shared originals separately. Manifest is written last; a read-only membership/hash/size audit follows. The manifest is not hashed back into validation or seal.

**Research/offline QA and the bounded captured-final historical peer reciprocal are complete. Coordinator acceptance remains pending, separately and explicitly.** Future geographic/legal/live-count qualifications do not justify inventing missing data or holding this worker open indefinitely.


## Bounded captured-final reciprocal

The same turnout worker completed this separately authorized bounded check against frozen baseline worker `f2db457b-3e3c-47d0-a65c-7d6be8bbe5c7`. No peer was contacted/restarted and no new source, ballot/legal/feed research or calculator/model outcome was adopted. **Agreement applies only to the actually captured historical source evidence and volume orders described below.** Coordinator acceptance, current legal/native-80/geography admission and collector/cadence/pool/probability admission remain false or unknown.

Before any owned mutation or peer derivative comparison, all 145 original turnout manifest targets plus the manifest (146 files) and all nine read-only original references verified. The complete [original-phase capture](data/turnout/reciprocal/turnout-original-phase.tar.gz) preserves every old report, script, source, contract, witness, validation, seal, manifest and history body at its original path. Original manifest: 34,170 bytes, SHA256 `4e2a1f5ab3c66508444c112f9e6430006dce94f795a172837c7b95eaee557207`; original contract: 15,256,104 bytes, SHA256 `16d89ba0e4568d94c9ffe33abe52c451e14f88b5e00b3fd7c868615de0f5a9da`. Original first witness stays unchanged at SHA256 `b8a4bba1c934beb847166e79d5ca75e1d8b0a5757da5bdbb80abda490b7d7ce5`. [Capture proof](data/turnout/reciprocal/own-capture-proof.json).

Before comparison, all 306 final baseline manifest targets plus the manifest (307 files) verified. [Actual-final peer capture](data/turnout/reciprocal/baseline-actual-final.tar.gz) contains 306 complete bodies; one large original entity is reused by its exact individual stored/raw pin and retained receipt role, without duplication. Peer manifest: 60,279 bytes, SHA256 `13ec2553cbeafdbf4111f1decd6c686e14d5fbfb8c196c70d3e95836f7016254`. Its original-first v1 witness SHA256 `941f8c78065a55966c2514b6e99bc1e148ec200d9cc1b269cf461146e83b940d` is independently found unchanged within its captured `history/original-first-v1.tar.gz`. [Complete peer capture proof](data/turnout/reciprocal/peer-capture-proof.json) and [path/hash/body reconstruction audit](data/turnout/reciprocal/capture-reconstruction-validation.json) distinguish original-phase bodies from revised current bytes.

The [scoped comparison](data/turnout/reciprocal/comparison.json) checks all 201 XLS members, 610,064 selected typed cells plus 90,096 descriptor cells, all 6,270 native keys and candidate/admin observations, 871 parent candidate and 1,861 parent administrative controls, 204 ballot/registration rows and 1,020 numeric positions, every native/county candidate order and 13 field-sensitivity orders, and all 67 primary parent/full/887-priority/1,198-remainder arrays. PDF source positions/values and three null/dash cells agree; native explicit zero observations remain separate. All original source contexts and companion receipts remain pinned. Counts, source keys, native CSVs, masks and all non-peer-status contract semantics are unchanged.

Representational differences are explicit: peer final vectors use a consistent candidate identity order while original Jefferson rows reverse Stein/Oliver; parent display labels can be `StClair` or `St_ Clair` versus Census `St. Clair`; county parent keys add a `:county` suffix; PDF evidence uses full column regions versus numeric-token spans. Exact native identities are never normalized. The peer’s corrected statewide inventory is label-keyed and agrees with the already-correct raw per-native/county observations. Jefferson literal row 12 is Stein 994 and row 13 Oliver 731. No turnout counts were changed and no false publication conflict is revived. All failed checker/adapter code, errors and complete pinned inputs are retained in the reciprocal directory.

The [isolated offline reproduction](data/turnout/reciprocal/offline-reproduction.json) sources exact captured originals only, denies network/mutable-repository/peer-discovery/producer-helper/writer routes, and rebuilds the complete original package in temporary outputs. All 146 original bodies independently reconstruct; 144 regenerated original targets match byte-for-byte. The only regenerated audit difference is its history count, 16 versus 17: the sealed original includes the preceding validation body frozen after that check. This is retained explicitly in [the audit difference](data/turnout/reciprocal/offline-validation-difference.json), not hidden or compared to revised current bytes. Source counts/identities/orders and original witness remain exact. The [30 actual corruption fixtures](data/turnout/reciprocal/corruption-validation.json) reject missing native/admin/candidate/null/header/context/companion data, wrong source type/position, wrong 80%/order/cumulative/duplicate keys, residual allocation, county dispatch substitution and current admission. These tests check original cells and relationships rather than stored success flags.

Final validation, seal and manifest include every new capture, proof, failed checker, input patch, history and current artifact. The manifest excludes only itself, is written last, and has no reverse digest in validation/seal. Final read-only membership/hash/raw-original/history/source/link/type/size audit follows; no owned writes follow its pass.
