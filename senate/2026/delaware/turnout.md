# Delaware historical vote volume and turnout controls

Research observed **2026-10-19 UTC** (some acquisition/verification completed 2026-10-20 UTC). Priority contest: **November 5, 2024 U.S. Senator, Lisa Blunt Rochester–Eric Hansen–Michael “Dr. Mike” Katz**, the other, Class I seat. **500,606 is reported Senate candidate votes, not ballots cast.** The disjoint ranking uses every one of the official report’s **530 Senate election districts**, including explicit zero rows and statutory administrative districts. County, representative-district, Wilmington and state views are controls that overlap this geography. [Official report](https://elections.delaware.gov/reports/GE2024.html), [state CSV](https://elections.delaware.gov/reports/GE2024.csv).

**Top 15: 35,875 / 500,606 = 7.1663144269%. Minimum descending set reaching 80%: 311 districts, 400,539 / 500,606 = 80.0108268778%.** The preceding 310 contribute 399,708 = 79.8448280684%; **ElectionDistrict0807 (08-07), 831 votes, crosses** the integer threshold **400,485**. Since this is descending volume, no set of only 310 can reach 80%. The remaining **219 districts / 100,067 votes (19.9891731222%)** remain in statewide arithmetic. Ties use ascending literal native key. These calculations use the [official native tables](https://elections.delaware.gov/reports/GE2024.html); the exact ordered set and complete remainder are in [priority-set.json](data/turnout/priority-set.json), [CSV](data/county-turnout.csv), and the full order below.

| Rank | Native ED key | County | Senate votes | State share % |
| --- | --- | --- | --- | --- |
| 1 | ElectionDistrict0404 | SUSSEX | 3,722 | 0.7434988794 |
| 2 | ElectionDistrict1404 | SUSSEX | 2,724 | 0.5441405017 |
| 3 | ElectionDistrict4108 | SUSSEX | 2,471 | 0.4936017547 |
| 4 | ElectionDistrict3807 | SUSSEX | 2,443 | 0.4880085337 |
| 5 | ElectionDistrict3804 | SUSSEX | 2,423 | 0.4840133758 |
| 6 | ElectionDistrict0912 | NEW CASTLE | 2,311 | 0.4616404917 |
| 7 | ElectionDistrict1408 | SUSSEX | 2,304 | 0.4602421865 |
| 8 | ElectionDistrict3802 | SUSSEX | 2,283 | 0.4560472707 |
| 9 | ElectionDistrict0913 | NEW CASTLE | 2,277 | 0.4548487233 |
| 10 | ElectionDistrict3509 | SUSSEX | 2,256 | 0.4506538076 |
| 11 | ElectionDistrict2005 | SUSSEX | 2,188 | 0.4370702708 |
| 12 | ElectionDistrict1102 | NEW CASTLE | 2,183 | 0.4360714814 |
| 13 | ElectionDistrict3706 | SUSSEX | 2,173 | 0.4340739024 |
| 14 | ElectionDistrict2903 | KENT | 2,091 | 0.4176937552 |
| 15 | ElectionDistrict3810 | SUSSEX | 2,026 | 0.4047094921 |


The [machine-readable contract](data/turnout/priority-set.json) contains all 530 ranks and votes, ordered top-15/311 priority/219 remainder keys, all-year source-native constituents, three county parents, 41 RD controls per contest, and explicit unavailable/administrative cases. It remains **historical research awaiting coordinator acceptance**. It grants no current geometry or November 2026 identity approval. The compatibility filename `county-turnout.csv` contains **native election districts**; it does not replace them with counties. Source identity and scope derive from the [official report](https://elections.delaware.gov/reports/GE2024.html), [participation report](https://elections.delaware.gov/voter/registrationtotals/reports/agprpt_2024.txt), and dated [district structure](https://elections.delaware.gov/maps/pdfs/DEDistrictStructure_2022_2032_v4.pdf).

## Election schedule, authorities and source status

The general election is **November 3, 2026**, and the observed current results index links the **September 15 primary**. Those primary election IDs, totals, completion labels and clocks are not November metadata. The 2026 regular seat is Class II; **2020 Coons–Witzke** is the same-seat context, while the 2024 Blunt Rochester contest is Class I. **No U.S. Senate or governor contest occurred in Delaware in 2022**; the actual **November 8 at-large House** contest is the midterm comparator. Sources: [2026 calendar](https://elections.delaware.gov/public/calendar/pdfs/2026ElectionCalendar.pdf), [current results index](https://elections.delaware.gov/results/), [Senate Class II](https://www.senate.gov/senators/Class_II.htm), [Class I](https://www.senate.gov/senators/Class_I.htm), [2020 report](https://elections.delaware.gov/reports/GE2020.html), [complete 2022 report and office inventory](https://elections.delaware.gov/reports/GE2022.html).

The Delaware Department of Elections’ **county offices** conduct elections, registration and voter education; the **State Election Commissioner** collects and reports results. The three county controls on the state website are state publications of county results, not three independently retrieved county canvasses. The agency’s [authority description](https://elections.delaware.gov/aboutagency.shtml) distinguishes these responsibilities. No individual county signed canvass or exhaustive later legal/certification product is claimed here.

The complete [official archive](https://elections.delaware.gov/elections/election_archive.html) links the 2020/2022/2024 reports and separate write-in PDFs; each report links its own state CSV. All returned HTTP 200 in fresh acquisitions and matched the retained original entity hashes exactly. Report status is **OFFICIAL RESULTS**, with printed clocks **2024-11-12 12:59:37**, **2022-11-12 00:25:01**, and **2020-11-11 14:45:36**, timezone unprinted. The 2024 write-in sheet separately prints **2024-11-12 10:06 AM**; the 2020 sheet has no clock. The 2022 sheet literally says **“2020 General Election”**, but also **November 8, 2022** and **2022-11-11 7:23 PM**; the archive/candidates/contest match establishes its retained 2022 context without correcting the original. [2024 tally](https://elections.delaware.gov/elections/resultsarchive/elect24/elect24_general/GE2024_Official_WriteInVotes_Statewide.pdf), [2022 tally](https://elections.delaware.gov/elections/resultsarchive/elect22/elect22_general/GE2022_Official_WriteInVotes_Statewide.pdf), [2020 tally](https://elections.delaware.gov/elections/resultsarchive/elect20/elect20_general/pdf/GE2020%20Official%20Write-In%20Votes-Statewide.pdf).

## Candidate universe and whole-state reconciliation

Every required contest row is retained with exact source party, candidate spelling, original field labels, table/row character positions and method values. All named ED **and RD** sums reconcile to each separate state CSV candidate/method control. There are **10,699 candidate rows across the five contexts and five overlapping views**. No candidate key is deduplicated or rescaled. The table below is from the [2024 CSV](https://elections.delaware.gov/reports/GE2024.csv), [2022 CSV](https://elections.delaware.gov/reports/GE2022.csv), and [2020 CSV](https://elections.delaware.gov/reports/GE2020.csv); the full controls and source positions are [retained](data/turnout/extracts/state-controls.json).

| Year / contest | Candidate | Party (source) | Machine | Absentee | Early (state CSV) | Total |
| --- | --- | --- | --- | --- | --- | --- |
| 2024 / PresidentandVicePresident | KAMALA D. HARRIS AND TIM WALZ | Democratic Party | 148,264 | 27,705 | 113,789 | 289,758 |
| 2024 / PresidentandVicePresident | DONALD J. TRUMP AND JD VANCE | Republican Party | 111,374 | 10,454 | 92,523 | 214,351 |
| 2024 / PresidentandVicePresident | VERMIN SUPREME AND JONATHAN REALZ | Conservative Party | 600 | 47 | 267 | 914 |
| 2024 / PresidentandVicePresident | ROBERT F. KENNEDY JR. AND NICOLE SHANAHAN | Independent Party of Delaware | 3,266 | 255 | 1,115 | 4,636 |
| 2024 / PresidentandVicePresident | CHASE OLIVER AND MIKE TER MAAT | Libertarian Party | 1,396 | 121 | 521 | 2,038 |
| 2024 / USSenator | LISA BLUNT ROCHESTER | Democratic Party | 145,831 | 26,714 | 110,753 | 283,298 |
| 2024 / USSenator | ERIC HANSEN | Republican Party | 100,893 | 9,926 | 86,934 | 197,753 |
| 2024 / USSenator | MICHAEL "DR. MIKE" KATZ | Independent Party of Delaware | 10,986 | 1,737 | 6,832 | 19,555 |
| 2022 / RepresentativeinCongress | LISA BLUNT ROCHESTER | Democratic Party | 127,059 | 16,736 | 34,621 | 178,416 |
| 2022 / RepresentativeinCongress | LEE MURPHY | Republican Party | 112,482 | 5,706 | 20,013 | 138,201 |
| 2022 / RepresentativeinCongress | CODY MCNUTT | Libertarian Party | 2,726 | 129 | 219 | 3,074 |
| 2022 / RepresentativeinCongress | DAVID ROGERS | Non-Partisan Delaware | 1,565 | 168 | 225 | 1,958 |
| 2020 / PresidentandVicePresident | JOSEPH R. BIDEN JR. AND KAMALA D. HARRIS | Democratic Party | 168,371 | 127,897 | 0 | 296,268 |
| 2020 / PresidentandVicePresident | DONALD J. TRUMP AND MICHAEL R. PENCE | Republican Party | 168,579 | 32,024 | 0 | 200,603 |
| 2020 / PresidentandVicePresident | HOWIE HAWKINS AND ANGELA NICOLE WALKER | Green Party Of Delaware | 1,427 | 712 | 0 | 2,139 |
| 2020 / PresidentandVicePresident | JO JORGENSEN AND JEREMY "SPIKE" COHEN | Libertarian Party | 3,761 | 1,239 | 0 | 5,000 |
| 2020 / USSenator | CHRISTOPHER A. COONS | Democratic Party | 164,748 | 127,056 | 0 | 291,804 |
| 2020 / USSenator | LAUREN WITZKE | Republican Party | 156,333 | 29,721 | 0 | 186,054 |
| 2020 / USSenator | MARK W. TURLEY | Independent Party Of Delaware | 5,158 | 2,675 | 0 | 7,833 |
| 2020 / USSenator | NADINE M. FROST | Libertarian Party | 3,663 | 1,581 | 0 | 5,244 |


For **2024 Senate**, the archived qualified list has the same three candidates, and the complete declared-write-in list has **no U.S. Senator entry**. The separate official write-in sheet also has no U.S. Senate section. Thus 500,606 is the complete **reported named Senate candidate universe in these sources**. Generic/invalid/undeclared write-in counts are **unavailable**, not an invented zero; no legal claim that every attempted write-in is absent is made. The same independent checks identify **four qualified 2020 Senate candidates** and no declared/tallied Senate write-in row. Source party labels remain literal: Katz and Turley are independent-party candidates, not reassigned D/R coalitions. [2024 qualified list](https://elections.delaware.gov/candidates/candidatelist/genl_fcddt_2024.html), [2024 declared list](https://elections.delaware.gov/candidates/candidatelist/genl_wcddt_2024.html), [2020 qualified list](https://elections.delaware.gov/candidates/candidatelist/genl_fcddt_2020.html), [2020 declared list](https://elections.delaware.gov/candidates/candidatelist/genl_wcddt_2020.html), and the official write-in sheets cited above.

The other contexts need additional source-scoped write-ins. The 2024 presidential report has five named tickets; its separate sheet has **24 county rows / 11 printed ticket identities / 1,215 votes**, yielding **512,912** as arithmetic combined presidential context. It reports county/method counts, **no ED allocation**. The 2020 presidential sheet has **17 statewide rows / 336 votes**, giving **504,346** combined. The actual 2022 House qualified list has Blunt Rochester, Murphy, McNutt and Rogers, while the declared/tallied write-ins are **Edward Shlikas 3** and **Scott Walker 15**, giving **321,667** combined. Both latter sheets are statewide only. Missing declared names on a tally are not fabricated zero rows; source spellings such as “DR. SHIVA” remain literal rather than silently aliasing names. [2024 tally](https://elections.delaware.gov/elections/resultsarchive/elect24/elect24_general/GE2024_Official_WriteInVotes_Statewide.pdf), [2020 tally](https://elections.delaware.gov/elections/resultsarchive/elect20/elect20_general/pdf/GE2020%20Official%20Write-In%20Votes-Statewide.pdf), [2022 tally](https://elections.delaware.gov/elections/resultsarchive/elect22/elect22_general/GE2022_Official_WriteInVotes_Statewide.pdf), [2022 qualified list](https://elections.delaware.gov/candidates/candidatelist/genl_fcddt_2022.html), [declared list](https://elections.delaware.gov/candidates/candidatelist/genl_wcddt_2022.html).

| 2024 president write-ins by inclusive county | Absentee numeric cells | Early numeric cells | Machine numeric cells | Provisional | Total |
| --- | --- | --- | --- | --- | --- |
| KENT | 18 | 43 | 87 | blank / null | 148 |
| NEW CASTLE | 73 | 178 | 691 | blank / null | 942 |
| SUSSEX | 17 | 42 | 66 | blank / null | 125 |


The preceding table sums only printed numeric method cells; each blank cell remains null in [43 required write-in rows](data/turnout/extracts/writein-rows.json). The 2024 sheet’s Wilmington city-council and state-Senate sections are different offices. They are retained in the original PDF and excluded from presidential/Senate arithmetic. Original pages were visually checked; [review ledger](data/turnout/source/visual-review.json) and PNGs retain the evidence. Primary source: [official 2024 write-in tally](https://elections.delaware.gov/elections/resultsarchive/elect24/elect24_general/GE2024_Official_WriteInVotes_Statewide.pdf).

## Complete hierarchy and non-additive views

County parents are recovered from explicit **same-year county/RD/ED nesting** in each participation report and independently checked against membership in county-office result tables. For 2024, the structure PDF supplies **537 explicit county/RD/ED identities**, with a **February 13, 2024** update date. Its title says 2022 through 2032, while its note says use through the 2030 general election; both source statements are retained. It is historical administrative evidence, not accepted current polygons. The Department describes EDs as voters sharing districts, ballot style and polling place; an ED is not automatically a distinct polling building, vote center, VTD or central counting board. [2024 structure](https://elections.delaware.gov/maps/pdfs/DEDistrictStructure_2022_2032_v4.pdf), [registration/ED explanation](https://elections.delaware.gov/candidates/pdfs/RegistrationTotalsPageInformation.pdf), [2024 participation](https://elections.delaware.gov/voter/registrationtotals/reports/agprpt_2024.txt), [2022 participation](https://elections.delaware.gov/voter/registrationtotals/reports/agprpt_2022.txt), [2020 participation](https://elections.delaware.gov/voter/registrationtotals/reports/agprpt_2020.txt).

The structure explicitly marks **02-27 (New Castle), 31-16 (Kent), 41-16 (Sussex)** with footnote 1, assigned under **15 Del. C. §1901(b)(3)**. These administrative units are present in Senate/House federal-contest results, including **651 / 76 / 188 Senate votes** in 2024. **02-28, 31-17, 41-17** have footnote 2, assigned under **42 U.S.C. §1973aa-1**; the 2024 report prints presidential zero rows and **no Senate rows**. No Senate identities or method zeros are fabricated for them. Early/absentee are candidate columns; no separately named central early/absentee board IDs are supplied by these tables. [Structure pages 2, 5, 16](https://elections.delaware.gov/maps/pdfs/DEDistrictStructure_2022_2032_v4.pdf), [2024 native report](https://elections.delaware.gov/reports/GE2024.html).

Coverage is explicitly source-scoped. **2024:** 533 all-office ED IDs / 530 Senate tables; the participation/structure sources have 537, adding **0117, 0222, 0223, 0616**, each with explicit zero Registered/Voted totals but no candidate report table. **2022:** 516 House/report ED IDs versus 519 participation EDs; **0228, 3117, 4117** occur only in the participation scope, with no House results fabricated. **2020:** 439 president/report IDs, 436 Senate IDs, and 435 participation EDs. Report-only **1314** has county-office parent evidence and zero target-contest votes; **0218, 3117, 4117** have presidential tables but no Senate tables and no independently established 2020 county parent. **0218 contains Biden 1 Machine vote**; the other two print presidential zero rows. The unparented one vote stays in state totals and is not allocated by residual or number range. [2024 report](https://elections.delaware.gov/reports/GE2024.html), [2022 report](https://elections.delaware.gov/reports/GE2022.html), [2020 report](https://elections.delaware.gov/reports/GE2020.html), and the year-specific participation originals above; [full source coverage](data/turnout/extracts/native-coverage.json).

The historical [2024 sample-ballot index](https://elections.delaware.gov/elections/general/sampleballots/ge2024/index.html) independently prints county, RD and ED for **533 rows**, exactly the original candidate report’s all-office native IDs. Those links and source positions are retained in [sample-ballot identities](data/turnout/extracts/sample-ballot-identities.json) and the dispatch contract. This is an inspected original index; its individual ballot PDFs were not downloaded, and no current polling-site or geometry approval follows.

All three counties are retained with [Census county identifiers](https://tigerweb.geo.census.gov/tigerwebmain/Files/acs25/tigerweb_acs25_county_2024_acs24_de.html) **New Castle 10003, Sussex 10005, Kent 10001**; FIPS apply to the county parents, not to native ED IDs. Their 2024 Senate control order is **270,005 / 144,333 / 86,268**. The largest two supply **414,338 / 500,606 = 82.7672860493%**, versus New Castle alone 53.9356300164%. A county-only top 15 necessarily contains all three counties and 100%; that supplementary view does not replace the native ranking. Every candidate’s county vector reconciles the state control. The **ByCounty** New Castle count is inclusive. **ByCounty W/ Wilmington** splits it into Wilmington + Rest of New Castle: never add Wilmington to inclusive New Castle, nor combine the alternative views. This also holds in the actual 2022 report. [2024 county and Wilmington views](https://elections.delaware.gov/reports/GE2024.html), [2022 views](https://elections.delaware.gov/reports/GE2022.html), [county controls](data/turnout/extracts/county-controls.csv).

## Historical and denominator sensitivities

These are separate historical volume distributions; they do not establish a cross-year ED join or a 2026 forecast. The **2022 at-large House** comparison changes election year, office, candidates, registered population and district vintage. Its 18 separately reported statewide write-in votes remain unallocated: the exact native House ranking below covers the 321,649 named report votes, while 321,667 is the combined statewide context. Presidential combined-scope rankings likewise cannot allocate the separate 1,215 / 336 write-ins to native districts. [2022 official report](https://elections.delaware.gov/reports/GE2022.html), [2024 report](https://elections.delaware.gov/reports/GE2024.html), [2020 report](https://elections.delaware.gov/reports/GE2020.html), and their separate tally sheets above.

| Context (report named votes) | EDs | State votes | Top15 votes / share % | Minimum80 EDs | Before crossing | At crossing | Crossing native key |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2024 USSenator | 530 | 500,606 | 35,875 / 7.1663144269 | 311 | 399,708 | 400,539 | ElectionDistrict0807 |
| 2024 PresidentandVicePresident | 533 | 511,697 | 36,535 / 7.1399675980 | 312 | 408,814 | 409,661 | ElectionDistrict0711 |
| 2022 RepresentativeinCongress | 516 | 321,649 | 25,290 / 7.8626079982 | 290 | 257,191 | 257,721 | ElectionDistrict0704 |
| 2020 USSenator | 436 | 490,935 | 46,762 / 9.5250898795 | 266 | 392,457 | 393,418 | ElectionDistrict0505 |
| 2020 PresidentandVicePresident | 439 | 504,010 | 47,687 / 9.4615186207 | 267 | 402,853 | 403,843 | ElectionDistrict3211 |


On the three-county reporting scope the recent midterm House volumes are New Castle 169,543, Sussex 98,030, Kent 54,076. All county/native contexts retain every candidate and source method; full orders are in [historical rankings](data/turnout/extracts/historical-rankings.json) and [county rankings](data/turnout/extracts/county-rankings.json), derived from the [2022 report](https://elections.delaware.gov/reports/GE2022.html), [2020 report](https://elections.delaware.gov/reports/GE2020.html) and [2024 report](https://elections.delaware.gov/reports/GE2024.html).

The results-page header, the separate Registered/Voted report and the November 1 registration stock are different source observations. The table below preserves those scopes. The header’s literal “Registered Votes” presentation does not independently establish an exact cast-ballot accounting definition. Neither its difference from Senate votes nor a registration-minus-voted calculation is labelled blank/under/over/remaining ballots. Active/inactive registration status and the participation extract’s stock date are not printed; the November stock date is explicit. [Results reports](https://elections.delaware.gov/elections/election_archive.html), [2024 participation](https://elections.delaware.gov/voter/registrationtotals/reports/agprpt_2024.txt), [2022 participation](https://elections.delaware.gov/voter/registrationtotals/reports/agprpt_2022.txt), [2020 participation](https://elections.delaware.gov/voter/registrationtotals/reports/agprpt_2020.txt), [2024 November stock](https://elections.delaware.gov/voter/registrationtotals/pdfs/vrt_RD20241101.pdf), [2022 stock](https://elections.delaware.gov/voter/registrationtotals/pdfs/vrt_RD20221101.pdf), [2020 stock](https://elections.delaware.gov/voter/registrationtotals/reports/e70r2601rd_20201101.html).

| Year | Results header participation / registration | Separate report Voted / Registered | Difference header minus report (V/R) | Nov1 registered stock |
| --- | --- | --- | --- | --- |
| 2024 | 518,330 / 788,441 | 518,086 / 788,864 | 244 / -423 | 790,955 |
| 2022 | 325,632 / 762,908 | 325,558 / 763,088 | 74 / -180 | 764,765 |
| 2020 | 509,241 / 739,570 | 508,955 / 740,150 | 286 / -580 | 739,557 |


All **1,631** participation total rows, including **1,491 ED rows**, reconcile each year’s ED/RD/county registered and voted sums to its statewide total. Only the required `i. Total` rows were derived; the original complete age/party report bytes remain intact. The 2024 and 2022 monthly RD CSVs have **two blank party cells each** (02-21 Republican, 07-13 Others), preserved as missing; their native total remains null where no full total is printed. Numeric-cell sums reconcile to printed statewide stocks **790,955 / 764,765**, without assigning zero to a missing party field. The 2020 stock prints **739,557**. Source-native registration universes differ from candidate-report universes; an absent registration row is not zero. [Participation extracts](data/turnout/extracts/participation-totals.json), [monthly controls](data/turnout/extracts/monthly-registration-controls.json), from the participation originals and November stock sources cited immediately above.

| Year / participation report field | Full ED universe | Total | Top15 votes or records | Minimum80 EDs | Before | At crossing |
| --- | --- | --- | --- | --- | --- | --- |
| 2024 registered | 537 | 788,864 | 48,462 | 320 | 630,747 | 632,077 |
| 2024 voted | 537 | 518,086 | 36,959 | 312 | 413,951 | 414,810 |
| 2022 registered | 519 | 763,088 | 45,030 | 310 | 609,678 | 611,042 |
| 2022 voted | 519 | 325,558 | 25,567 | 290 | 260,162 | 260,699 |
| 2020 registered | 435 | 740,150 | 62,588 | 273 | 591,771 | 593,236 |
| 2020 voted | 435 | 508,955 | 48,155 | 267 | 406,679 | 407,678 |


The participation sensitivity table above ranks each source’s complete own universe, not just Senate priority districts. Separate report registration weights measure registered records, while `Voted` weights measure reported participation. They are not voter-eligible population or candidate-vote weights. Exact ballots-cast, blank-ballot, contest-under/overvote fields remain unavailable in these retained whole-state historical products; no count is inferred from subtraction. The state’s [results notes](https://elections.delaware.gov/results/) define blank/under/overvote concepts separately. No observed historical product establishes 2026 outstanding votes or live cadence.

For 2024 Senate, ranking each method separately changes the geographic concentration. The table below uses all 530 EDs and all three candidates for each method. **2020 native Early Voting is absent, not zero**: all 3,500 required ED candidate positions are null, although the separate state CSV prints statewide early-voting zeros. Also, 2020 “Absentee Votes” explicitly includes absentee and vote-by-mail; no further mode split is invented. [2024 report/CSV](https://elections.delaware.gov/reports/GE2024.html), [2020 report](https://elections.delaware.gov/reports/GE2020.html), [2020 state CSV](https://elections.delaware.gov/reports/GE2020.csv).

| 2024 Senate method | State candidate votes | Top15 votes | Minimum80 EDs | Before | At crossing |
| --- | --- | --- | --- | --- | --- |
| Machine Votes | 257,710 | 15,960 | 304 | 206,030 | 206,450 |
| Absentee Votes | 38,377 | 4,368 | 283 | 30,681 | 30,739 |
| Early Voting Votes | 204,519 | 23,853 | 273 | 163,479 | 163,771 |


## Reproduction, independent agreement and limits

The actual independent partisanship worker **4724b2aa-c338-4708-8044-c4b606bfaaeb** stabilized an original-first extraction before either worker opened the other’s numeric derivatives. Immutable reciprocal captures support [10,699-row raw/position agreement](data/turnout/peer/reconciliation-v1.json) and [all five full descending native orders and exact threshold/top15 agreement](data/turnout/peer/rank-reconciliation.json). Supplemental hierarchy, Registered/Voted, monthly-stock and write-in comparisons are recorded in [supplement reconciliation](data/turnout/peer/supplement-reconciliation.json). Primary originals remain the authority; agreement does not grant current geographic approval. The [offline validation](data/turnout/validation.json) and [complete asset manifest](data/turnout/asset-manifest.json) record checks and bounded artifacts.

Run from the repo root with `PYTHONDONTWRITEBYTECODE=1`: `python3 senate/2026/delaware/data/turnout/extract.py`, `render_sources.py`, `supplement.py`, `build_turnout.py`, `compare_peer.py`, `compare_supplement.py`, `report.py`, then `validate_turnout.py --check` (each latter script has the same directory prefix). `validate_turnout.py --seal` refreshes the owned proof and asset manifest after reviewed changes. The source-safe preparation-helper replay is retained separately and wrote only inside this assignment. [Schema and source definitions](data/turnout/source/SCHEMA.md) explain exact offsets, nulls, original reconstruction and acquisition receipts. All original HTTP entities are gzip-lossless; fresh identical report/PDF downloads reuse read-only shared originals by exact hash. Full redirect header blocks and requested/final URLs are retained in this worker’s fresh receipts; older preparation receipts alone did not preserve intermediate redirects. No artifact reaches 40,000,000 bytes.

Remaining qualifications are specific: exact cast-ballot/blank/under/over totals are not supplied by the retained whole-state products; 2020 president-only county parents remain unavailable; separately published presidential/2022 House write-ins have no ED allocation; native revisions and monthly/participation stock differences remain source-scoped. These do not remove any reported native unit or vote from state arithmetic. This package is complete historical source research with those bounds, not an implemented collector, calibrated Needle, real 2026 turnout forecast, approved current crosswalk or measured publication cadence. Authority for the historical counts remains the [official archive](https://elections.delaware.gov/elections/election_archive.html); the [current results index](https://elections.delaware.gov/results/) still concerns the September primary.

## Full 530-unit Senate order and complete remainder

All rows below come from the [official 2024 native Senate tables](https://elections.delaware.gov/reports/GE2024.html), reconciled to the [state CSV](https://elections.delaware.gov/reports/GE2024.csv). Rows **1–311** are the exact minimum 80% set (and include all top 15); rows **312–530** are the complete ordered remainder. Printed RD–ED labels retain leading zeros. The CSV and JSON retain full native IDs, source positions, FIPS parents and separate method/stat fields.

| Rank | Native key | County | Candidate votes | Cumulative votes | Cumulative % | 80% set |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | ElectionDistrict0404 | SUSSEX | 3,722 | 3,722 | 0.7434988794 | yes |
| 2 | ElectionDistrict1404 | SUSSEX | 2,724 | 6,446 | 1.2876393811 | yes |
| 3 | ElectionDistrict4108 | SUSSEX | 2,471 | 8,917 | 1.7812411357 | yes |
| 4 | ElectionDistrict3807 | SUSSEX | 2,443 | 11,360 | 2.2692496694 | yes |
| 5 | ElectionDistrict3804 | SUSSEX | 2,423 | 13,783 | 2.7532630452 | yes |
| 6 | ElectionDistrict0912 | NEW CASTLE | 2,311 | 16,094 | 3.2149035369 | yes |
| 7 | ElectionDistrict1408 | SUSSEX | 2,304 | 18,398 | 3.6751457234 | yes |
| 8 | ElectionDistrict3802 | SUSSEX | 2,283 | 20,681 | 4.1311929941 | yes |
| 9 | ElectionDistrict0913 | NEW CASTLE | 2,277 | 22,958 | 4.5860417174 | yes |
| 10 | ElectionDistrict3509 | SUSSEX | 2,256 | 25,214 | 5.0366955250 | yes |
| 11 | ElectionDistrict2005 | SUSSEX | 2,188 | 27,402 | 5.4737657959 | yes |
| 12 | ElectionDistrict1102 | NEW CASTLE | 2,183 | 29,585 | 5.9098372772 | yes |
| 13 | ElectionDistrict3706 | SUSSEX | 2,173 | 31,758 | 6.3439111797 | yes |
| 14 | ElectionDistrict2903 | KENT | 2,091 | 33,849 | 6.7616049348 | yes |
| 15 | ElectionDistrict3810 | SUSSEX | 2,026 | 35,875 | 7.1663144269 | yes |
| 16 | ElectionDistrict0805 | NEW CASTLE | 1,995 | 37,870 | 7.5648314243 | yes |
| 17 | ElectionDistrict2009 | SUSSEX | 1,982 | 39,852 | 7.9607515691 | yes |
| 18 | ElectionDistrict2008 | SUSSEX | 1,980 | 41,832 | 8.3562721981 | yes |
| 19 | ElectionDistrict3305 | KENT | 1,957 | 43,789 | 8.7471983955 | yes |
| 20 | ElectionDistrict3606 | SUSSEX | 1,914 | 45,703 | 9.1295350036 | yes |
| 21 | ElectionDistrict1403 | SUSSEX | 1,909 | 47,612 | 9.5108728221 | yes |
| 22 | ElectionDistrict0808 | NEW CASTLE | 1,905 | 49,517 | 9.8914116091 | yes |
| 23 | ElectionDistrict4002 | SUSSEX | 1,902 | 51,419 | 10.2713511224 | yes |
| 24 | ElectionDistrict1402 | SUSSEX | 1,892 | 53,311 | 10.6492930568 | yes |
| 25 | ElectionDistrict0911 | NEW CASTLE | 1,889 | 55,200 | 11.0266357175 | yes |
| 26 | ElectionDistrict0401 | SUSSEX | 1,848 | 57,048 | 11.3957883046 | yes |
| 27 | ElectionDistrict2003 | SUSSEX | 1,831 | 58,879 | 11.7615450075 | yes |
| 28 | ElectionDistrict0409 | SUSSEX | 1,830 | 60,709 | 12.1271019524 | yes |
| 29 | ElectionDistrict2205 | NEW CASTLE | 1,826 | 62,535 | 12.4918598658 | yes |
| 30 | ElectionDistrict4106 | SUSSEX | 1,822 | 64,357 | 12.8558187477 | yes |
| 31 | ElectionDistrict2701 | NEW CASTLE | 1,818 | 66,175 | 13.2189785979 | yes |
| 32 | ElectionDistrict3603 | SUSSEX | 1,813 | 67,988 | 13.5811396587 | yes |
| 33 | ElectionDistrict2904 | KENT | 1,800 | 69,788 | 13.9407038669 | yes |
| 34 | ElectionDistrict0903 | NEW CASTLE | 1,794 | 71,582 | 14.2990695277 | yes |
| 35 | ElectionDistrict1409 | SUSSEX | 1,791 | 73,373 | 14.6568359149 | yes |
| 36 | ElectionDistrict2906 | KENT | 1,770 | 75,143 | 15.0104073862 | yes |
| 37 | ElectionDistrict1204 | NEW CASTLE | 1,747 | 76,890 | 15.3593844261 | yes |
| 38 | ElectionDistrict3602 | SUSSEX | 1,738 | 78,628 | 15.7065636449 | yes |
| 39 | ElectionDistrict4004 | SUSSEX | 1,704 | 80,332 | 16.0469510953 | yes |
| 40 | ElectionDistrict1503 | NEW CASTLE | 1,681 | 82,013 | 16.3827441141 | yes |
| 41 | ElectionDistrict3403 | KENT | 1,670 | 83,683 | 16.7163397962 | yes |
| 42 | ElectionDistrict3704 | SUSSEX | 1,664 | 85,347 | 17.0487369308 | yes |
| 43 | ElectionDistrict1217 | NEW CASTLE | 1,661 | 87,008 | 17.3805347918 | yes |
| 44 | ElectionDistrict3803 | SUSSEX | 1,653 | 88,661 | 17.7107345897 | yes |
| 45 | ElectionDistrict0405 | SUSSEX | 1,652 | 90,313 | 18.0407346296 | yes |
| 46 | ElectionDistrict1702 | NEW CASTLE | 1,651 | 91,964 | 18.3705349117 | yes |
| 47 | ElectionDistrict2002 | SUSSEX | 1,651 | 93,615 | 18.7003351937 | yes |
| 48 | ElectionDistrict1105 | KENT | 1,635 | 95,250 | 19.0269393495 | yes |
| 49 | ElectionDistrict0402 | SUSSEX | 1,623 | 96,873 | 19.3511464106 | yes |
| 50 | ElectionDistrict4006 | SUSSEX | 1,611 | 98,484 | 19.6729563769 | yes |
| 51 | ElectionDistrict3604 | SUSSEX | 1,609 | 100,093 | 19.9943668274 | yes |
| 52 | ElectionDistrict3303 | KENT | 1,607 | 101,700 | 20.3153777622 | yes |
| 53 | ElectionDistrict3905 | SUSSEX | 1,607 | 103,307 | 20.6363886969 | yes |
| 54 | ElectionDistrict1406 | SUSSEX | 1,598 | 104,905 | 20.9556018106 | yes |
| 55 | ElectionDistrict1511 | NEW CASTLE | 1,597 | 106,502 | 21.2746151664 | yes |
| 56 | ElectionDistrict2713 | NEW CASTLE | 1,595 | 108,097 | 21.5932290064 | yes |
| 57 | ElectionDistrict1401 | SUSSEX | 1,585 | 109,682 | 21.9098452675 | yes |
| 58 | ElectionDistrict2210 | NEW CASTLE | 1,584 | 111,266 | 22.2262617707 | yes |
| 59 | ElectionDistrict2901 | KENT | 1,569 | 112,835 | 22.5396819055 | yes |
| 60 | ElectionDistrict1104 | NEW CASTLE | 1,568 | 114,403 | 22.8529022824 | yes |
| 61 | ElectionDistrict2007 | SUSSEX | 1,561 | 115,964 | 23.1647243541 | yes |
| 62 | ElectionDistrict3408 | KENT | 1,558 | 117,522 | 23.4759471521 | yes |
| 63 | ElectionDistrict0508 | NEW CASTLE | 1,555 | 119,077 | 23.7865706763 | yes |
| 64 | ElectionDistrict3809 | SUSSEX | 1,554 | 120,631 | 24.0969944427 | yes |
| 65 | ElectionDistrict2708 | NEW CASTLE | 1,550 | 122,181 | 24.4066191776 | yes |
| 66 | ElectionDistrict3409 | KENT | 1,546 | 123,727 | 24.7154448808 | yes |
| 67 | ElectionDistrict0806 | NEW CASTLE | 1,542 | 125,269 | 25.0234715525 | yes |
| 68 | ElectionDistrict3304 | KENT | 1,541 | 126,810 | 25.3312984663 | yes |
| 69 | ElectionDistrict3411 | KENT | 1,540 | 128,350 | 25.6389256221 | yes |
| 70 | ElectionDistrict3902 | SUSSEX | 1,513 | 129,863 | 25.9411593149 | yes |
| 71 | ElectionDistrict3601 | SUSSEX | 1,507 | 131,370 | 26.2421944603 | yes |
| 72 | ElectionDistrict3401 | KENT | 1,498 | 132,868 | 26.5414317847 | yes |
| 73 | ElectionDistrict2304 | NEW CASTLE | 1,482 | 134,350 | 26.8374729827 | yes |
| 74 | ElectionDistrict3702 | SUSSEX | 1,482 | 135,832 | 27.1335141808 | yes |
| 75 | ElectionDistrict4105 | SUSSEX | 1,477 | 137,309 | 27.4285565894 | yes |
| 76 | ElectionDistrict2105 | NEW CASTLE | 1,476 | 138,785 | 27.7233992401 | yes |
| 77 | ElectionDistrict3801 | SUSSEX | 1,475 | 140,260 | 28.0180421329 | yes |
| 78 | ElectionDistrict1808 | NEW CASTLE | 1,473 | 141,733 | 28.3122855100 | yes |
| 79 | ElectionDistrict2902 | KENT | 1,471 | 143,204 | 28.6061293712 | yes |
| 80 | ElectionDistrict0902 | NEW CASTLE | 1,470 | 144,674 | 28.8997734745 | yes |
| 81 | ElectionDistrict2111 | NEW CASTLE | 1,468 | 146,142 | 29.1930180621 | yes |
| 82 | ElectionDistrict1405 | SUSSEX | 1,466 | 147,608 | 29.4858631339 | yes |
| 83 | ElectionDistrict1903 | NEW CASTLE | 1,466 | 149,074 | 29.7787082057 | yes |
| 84 | ElectionDistrict1205 | NEW CASTLE | 1,464 | 150,538 | 30.0711537616 | yes |
| 85 | ElectionDistrict0910 | NEW CASTLE | 1,459 | 151,997 | 30.3626005282 | yes |
| 86 | ElectionDistrict3903 | SUSSEX | 1,458 | 153,455 | 30.6538475368 | yes |
| 87 | ElectionDistrict1510 | NEW CASTLE | 1,453 | 154,908 | 30.9440957559 | yes |
| 88 | ElectionDistrict0403 | SUSSEX | 1,432 | 156,340 | 31.2301490593 | yes |
| 89 | ElectionDistrict1806 | NEW CASTLE | 1,416 | 157,756 | 31.5130062364 | yes |
| 90 | ElectionDistrict0408 | SUSSEX | 1,401 | 159,157 | 31.7928670451 | yes |
| 91 | ElectionDistrict3906 | SUSSEX | 1,394 | 160,551 | 32.0713295486 | yes |
| 92 | ElectionDistrict2807 | KENT | 1,387 | 161,938 | 32.3483937468 | yes |
| 93 | ElectionDistrict0609 | NEW CASTLE | 1,382 | 163,320 | 32.6244591555 | yes |
| 94 | ElectionDistrict2106 | NEW CASTLE | 1,381 | 164,701 | 32.9003248063 | yes |
| 95 | ElectionDistrict0501 | NEW CASTLE | 1,378 | 166,079 | 33.1755911835 | yes |
| 96 | ElectionDistrict0612 | NEW CASTLE | 1,372 | 167,451 | 33.4496590133 | yes |
| 97 | ElectionDistrict0905 | NEW CASTLE | 1,370 | 168,821 | 33.7233273273 | yes |
| 98 | ElectionDistrict4007 | SUSSEX | 1,367 | 170,188 | 33.9963963676 | yes |
| 99 | ElectionDistrict1608 | NEW CASTLE | 1,365 | 171,553 | 34.2690658921 | yes |
| 100 | ElectionDistrict1805 | NEW CASTLE | 1,360 | 172,913 | 34.5407366272 | yes |
| 101 | ElectionDistrict3501 | SUSSEX | 1,358 | 174,271 | 34.8120078465 | yes |
| 102 | ElectionDistrict0802 | NEW CASTLE | 1,356 | 175,627 | 35.0828795500 | yes |
| 103 | ElectionDistrict1103 | NEW CASTLE | 1,356 | 176,983 | 35.3537512535 | yes |
| 104 | ElectionDistrict1010 | NEW CASTLE | 1,355 | 178,338 | 35.6244231991 | yes |
| 105 | ElectionDistrict1201 | NEW CASTLE | 1,337 | 179,675 | 35.8914995026 | yes |
| 106 | ElectionDistrict2311 | NEW CASTLE | 1,336 | 181,011 | 36.1583760482 | yes |
| 107 | ElectionDistrict2806 | KENT | 1,336 | 182,347 | 36.4252525939 | yes |
| 108 | ElectionDistrict2908 | KENT | 1,336 | 183,683 | 36.6921291395 | yes |
| 109 | ElectionDistrict2905 | KENT | 1,334 | 185,017 | 36.9586061693 | yes |
| 110 | ElectionDistrict2808 | KENT | 1,329 | 186,346 | 37.2240844097 | yes |
| 111 | ElectionDistrict2607 | NEW CASTLE | 1,324 | 187,670 | 37.4885638606 | yes |
| 112 | ElectionDistrict2712 | NEW CASTLE | 1,323 | 188,993 | 37.7528435536 | yes |
| 113 | ElectionDistrict3405 | KENT | 1,322 | 190,315 | 38.0169234887 | yes |
| 114 | ElectionDistrict2306 | NEW CASTLE | 1,320 | 191,635 | 38.2806039081 | yes |
| 115 | ElectionDistrict2705 | NEW CASTLE | 1,319 | 192,954 | 38.5440845695 | yes |
| 116 | ElectionDistrict1801 | NEW CASTLE | 1,311 | 194,265 | 38.8059671678 | yes |
| 117 | ElectionDistrict1106 | KENT | 1,310 | 195,575 | 39.0676500082 | yes |
| 118 | ElectionDistrict2802 | KENT | 1,304 | 196,879 | 39.3281343012 | yes |
| 119 | ElectionDistrict2213 | NEW CASTLE | 1,302 | 198,181 | 39.5882190785 | yes |
| 120 | ElectionDistrict0602 | NEW CASTLE | 1,300 | 199,481 | 39.8479043399 | yes |
| 121 | ElectionDistrict0610 | NEW CASTLE | 1,298 | 200,779 | 40.1071900856 | yes |
| 122 | ElectionDistrict3806 | SUSSEX | 1,289 | 202,068 | 40.3646780103 | yes |
| 123 | ElectionDistrict2509 | NEW CASTLE | 1,283 | 203,351 | 40.6209673875 | yes |
| 124 | ElectionDistrict2309 | NEW CASTLE | 1,281 | 204,632 | 40.8768572490 | yes |
| 125 | ElectionDistrict3808 | SUSSEX | 1,281 | 205,913 | 41.1327471105 | yes |
| 126 | ElectionDistrict0606 | NEW CASTLE | 1,276 | 207,189 | 41.3876381825 | yes |
| 127 | ElectionDistrict2402 | NEW CASTLE | 1,275 | 208,464 | 41.6423294967 | yes |
| 128 | ElectionDistrict0901 | NEW CASTLE | 1,273 | 209,737 | 41.8966212950 | yes |
| 129 | ElectionDistrict1703 | NEW CASTLE | 1,272 | 211,009 | 42.1507133354 | yes |
| 130 | ElectionDistrict0406 | SUSSEX | 1,271 | 212,280 | 42.4046056180 | yes |
| 131 | ElectionDistrict2212 | NEW CASTLE | 1,269 | 213,549 | 42.6580983848 | yes |
| 132 | ElectionDistrict3005 | KENT | 1,266 | 214,815 | 42.9109918778 | yes |
| 133 | ElectionDistrict2201 | NEW CASTLE | 1,261 | 216,076 | 43.1628865815 | yes |
| 134 | ElectionDistrict3012 | KENT | 1,260 | 217,336 | 43.4145815272 | yes |
| 135 | ElectionDistrict1005 | NEW CASTLE | 1,257 | 218,593 | 43.6656771992 | yes |
| 136 | ElectionDistrict1209 | NEW CASTLE | 1,255 | 219,848 | 43.9163733555 | yes |
| 137 | ElectionDistrict1011 | NEW CASTLE | 1,252 | 221,100 | 44.1664702381 | yes |
| 138 | ElectionDistrict1216 | NEW CASTLE | 1,250 | 222,350 | 44.4161676049 | yes |
| 139 | ElectionDistrict1913 | NEW CASTLE | 1,250 | 223,600 | 44.6658649717 | yes |
| 140 | ElectionDistrict1507 | NEW CASTLE | 1,244 | 224,844 | 44.9143637911 | yes |
| 141 | ElectionDistrict3701 | SUSSEX | 1,244 | 226,088 | 45.1628626105 | yes |
| 142 | ElectionDistrict1509 | NEW CASTLE | 1,242 | 227,330 | 45.4109619142 | yes |
| 143 | ElectionDistrict3009 | KENT | 1,241 | 228,571 | 45.6588614599 | yes |
| 144 | ElectionDistrict0809 | NEW CASTLE | 1,240 | 229,811 | 45.9065612478 | yes |
| 145 | ElectionDistrict2001 | SUSSEX | 1,240 | 231,051 | 46.1542610356 | yes |
| 146 | ElectionDistrict3308 | KENT | 1,236 | 232,287 | 46.4011617919 | yes |
| 147 | ElectionDistrict1211 | NEW CASTLE | 1,232 | 233,519 | 46.6472635166 | yes |
| 148 | ElectionDistrict1006 | NEW CASTLE | 1,229 | 234,748 | 46.8927659676 | yes |
| 149 | ElectionDistrict3508 | SUSSEX | 1,228 | 235,976 | 47.1380686608 | yes |
| 150 | ElectionDistrict4102 | SUSSEX | 1,227 | 237,203 | 47.3831715960 | yes |
| 151 | ElectionDistrict2203 | NEW CASTLE | 1,226 | 238,429 | 47.6280747734 | yes |
| 152 | ElectionDistrict2507 | NEW CASTLE | 1,226 | 239,655 | 47.8729779507 | yes |
| 153 | ElectionDistrict2302 | NEW CASTLE | 1,224 | 240,879 | 48.1174816123 | yes |
| 154 | ElectionDistrict0810 | NEW CASTLE | 1,218 | 242,097 | 48.3607867265 | yes |
| 155 | ElectionDistrict2605 | NEW CASTLE | 1,217 | 243,314 | 48.6038920828 | yes |
| 156 | ElectionDistrict1804 | NEW CASTLE | 1,214 | 244,528 | 48.8463981654 | yes |
| 157 | ElectionDistrict2204 | NEW CASTLE | 1,214 | 245,742 | 49.0889042481 | yes |
| 158 | ElectionDistrict2609 | NEW CASTLE | 1,214 | 246,956 | 49.3314103307 | yes |
| 159 | ElectionDistrict2601 | NEW CASTLE | 1,210 | 248,166 | 49.5731173817 | yes |
| 160 | ElectionDistrict2805 | KENT | 1,206 | 249,372 | 49.8140254012 | yes |
| 161 | ElectionDistrict1304 | NEW CASTLE | 1,205 | 250,577 | 50.0547336628 | yes |
| 162 | ElectionDistrict0412 | SUSSEX | 1,203 | 251,780 | 50.2950424086 | yes |
| 163 | ElectionDistrict2710 | NEW CASTLE | 1,193 | 252,973 | 50.5333535755 | yes |
| 164 | ElectionDistrict2010 | SUSSEX | 1,191 | 254,164 | 50.7712652265 | yes |
| 165 | ElectionDistrict3503 | SUSSEX | 1,179 | 255,343 | 51.0067797829 | yes |
| 166 | ElectionDistrict2012 | SUSSEX | 1,174 | 256,517 | 51.2412955498 | yes |
| 167 | ElectionDistrict3309 | KENT | 1,162 | 257,679 | 51.4734142220 | yes |
| 168 | ElectionDistrict0108 | NEW CASTLE | 1,161 | 258,840 | 51.7053331362 | yes |
| 169 | ElectionDistrict0705 | NEW CASTLE | 1,156 | 259,996 | 51.9362532610 | yes |
| 170 | ElectionDistrict3703 | SUSSEX | 1,152 | 261,148 | 52.1663743543 | yes |
| 171 | ElectionDistrict4111 | SUSSEX | 1,151 | 262,299 | 52.3962956896 | yes |
| 172 | ElectionDistrict3211 | KENT | 1,150 | 263,449 | 52.6260172671 | yes |
| 173 | ElectionDistrict1506 | NEW CASTLE | 1,142 | 264,591 | 52.8541407814 | yes |
| 174 | ElectionDistrict4104 | SUSSEX | 1,139 | 265,730 | 53.0816650220 | yes |
| 175 | ElectionDistrict1306 | NEW CASTLE | 1,137 | 266,867 | 53.3087897468 | yes |
| 176 | ElectionDistrict3106 | KENT | 1,136 | 268,003 | 53.5357147138 | yes |
| 177 | ElectionDistrict2604 | NEW CASTLE | 1,134 | 269,137 | 53.7622401649 | yes |
| 178 | ElectionDistrict0707 | NEW CASTLE | 1,131 | 270,268 | 53.9881663424 | yes |
| 179 | ElectionDistrict1002 | NEW CASTLE | 1,129 | 271,397 | 54.2136930041 | yes |
| 180 | ElectionDistrict0105 | NEW CASTLE | 1,127 | 272,524 | 54.4388201500 | yes |
| 181 | ElectionDistrict2506 | NEW CASTLE | 1,124 | 273,648 | 54.6633480222 | yes |
| 182 | ElectionDistrict1210 | NEW CASTLE | 1,123 | 274,771 | 54.8876761365 | yes |
| 183 | ElectionDistrict2907 | KENT | 1,119 | 275,890 | 55.1112052193 | yes |
| 184 | ElectionDistrict2104 | NEW CASTLE | 1,113 | 277,003 | 55.3335357547 | yes |
| 185 | ElectionDistrict2405 | NEW CASTLE | 1,113 | 278,116 | 55.5558662901 | yes |
| 186 | ElectionDistrict3105 | KENT | 1,112 | 279,228 | 55.7779970676 | yes |
| 187 | ElectionDistrict3904 | SUSSEX | 1,110 | 280,338 | 55.9997283293 | yes |
| 188 | ElectionDistrict1904 | NEW CASTLE | 1,108 | 281,446 | 56.2210600752 | yes |
| 189 | ElectionDistrict2606 | NEW CASTLE | 1,108 | 282,554 | 56.4423918211 | yes |
| 190 | ElectionDistrict2110 | NEW CASTLE | 1,107 | 283,661 | 56.6635238091 | yes |
| 191 | ElectionDistrict4107 | SUSSEX | 1,106 | 284,767 | 56.8844560393 | yes |
| 192 | ElectionDistrict3001 | KENT | 1,103 | 285,870 | 57.1047889957 | yes |
| 193 | ElectionDistrict3814 | SUSSEX | 1,102 | 286,972 | 57.3249221943 | yes |
| 194 | ElectionDistrict2408 | NEW CASTLE | 1,099 | 288,071 | 57.5444561192 | yes |
| 195 | ElectionDistrict2209 | NEW CASTLE | 1,091 | 289,162 | 57.7623919809 | yes |
| 196 | ElectionDistrict2505 | NEW CASTLE | 1,089 | 290,251 | 57.9799283269 | yes |
| 197 | ElectionDistrict2207 | NEW CASTLE | 1,088 | 291,339 | 58.1972649149 | yes |
| 198 | ElectionDistrict1001 | NEW CASTLE | 1,087 | 292,426 | 58.4144017451 | yes |
| 199 | ElectionDistrict0801 | NEW CASTLE | 1,086 | 293,512 | 58.6313388174 | yes |
| 200 | ElectionDistrict1802 | NEW CASTLE | 1,086 | 294,598 | 58.8482758896 | yes |
| 201 | ElectionDistrict1601 | NEW CASTLE | 1,082 | 295,680 | 59.0644139303 | yes |
| 202 | ElectionDistrict3104 | KENT | 1,075 | 296,755 | 59.2791536658 | yes |
| 203 | ElectionDistrict3505 | SUSSEX | 1,075 | 297,830 | 59.4938934012 | yes |
| 204 | ElectionDistrict0803 | NEW CASTLE | 1,072 | 298,902 | 59.7080338630 | yes |
| 205 | ElectionDistrict3101 | KENT | 1,070 | 299,972 | 59.9217748089 | yes |
| 206 | ElectionDistrict2208 | NEW CASTLE | 1,069 | 301,041 | 60.1353159970 | yes |
| 207 | ElectionDistrict1012 | NEW CASTLE | 1,065 | 302,106 | 60.3480581535 | yes |
| 208 | ElectionDistrict4001 | SUSSEX | 1,062 | 303,168 | 60.5602010363 | yes |
| 209 | ElectionDistrict0611 | NEW CASTLE | 1,060 | 304,228 | 60.7719444034 | yes |
| 210 | ElectionDistrict2912 | KENT | 1,060 | 305,288 | 60.9836877704 | yes |
| 211 | ElectionDistrict1202 | NEW CASTLE | 1,059 | 306,347 | 61.1952313796 | yes |
| 212 | ElectionDistrict0302 | NEW CASTLE | 1,056 | 307,403 | 61.4061757150 | yes |
| 213 | ElectionDistrict3102 | KENT | 1,048 | 308,451 | 61.6155219874 | yes |
| 214 | ElectionDistrict1101 | NEW CASTLE | 1,046 | 309,497 | 61.8244687439 | yes |
| 215 | ElectionDistrict1908 | NEW CASTLE | 1,045 | 310,542 | 62.0332157425 | yes |
| 216 | ElectionDistrict1003 | NEW CASTLE | 1,042 | 311,584 | 62.2413634675 | yes |
| 217 | ElectionDistrict1605 | NEW CASTLE | 1,042 | 312,626 | 62.4495111924 | yes |
| 218 | ElectionDistrict3811 | SUSSEX | 1,041 | 313,667 | 62.6574591595 | yes |
| 219 | ElectionDistrict2502 | NEW CASTLE | 1,040 | 314,707 | 62.8652073687 | yes |
| 220 | ElectionDistrict1410 | SUSSEX | 1,036 | 315,743 | 63.0721565463 | yes |
| 221 | ElectionDistrict1214 | NEW CASTLE | 1,034 | 316,777 | 63.2787062081 | yes |
| 222 | ElectionDistrict3008 | KENT | 1,033 | 317,810 | 63.4850561120 | yes |
| 223 | ElectionDistrict0906 | NEW CASTLE | 1,032 | 318,842 | 63.6912062580 | yes |
| 224 | ElectionDistrict1711 | NEW CASTLE | 1,030 | 319,872 | 63.8969568883 | yes |
| 225 | ElectionDistrict2202 | NEW CASTLE | 1,030 | 320,902 | 64.1027075185 | yes |
| 226 | ElectionDistrict1901 | NEW CASTLE | 1,024 | 321,926 | 64.3072596014 | yes |
| 227 | ElectionDistrict2211 | NEW CASTLE | 1,024 | 322,950 | 64.5118116842 | yes |
| 228 | ElectionDistrict3013 | KENT | 1,022 | 323,972 | 64.7159642513 | yes |
| 229 | ElectionDistrict3205 | KENT | 1,021 | 324,993 | 64.9199170605 | yes |
| 230 | ElectionDistrict3302 | KENT | 1,019 | 326,012 | 65.1234703539 | yes |
| 231 | ElectionDistrict2410 | NEW CASTLE | 1,017 | 327,029 | 65.3266241316 | yes |
| 232 | ElectionDistrict3406 | KENT | 1,017 | 328,046 | 65.5297779092 | yes |
| 233 | ElectionDistrict2102 | NEW CASTLE | 1,013 | 329,059 | 65.7321326552 | yes |
| 234 | ElectionDistrict1909 | NEW CASTLE | 1,008 | 330,067 | 65.9334886118 | yes |
| 235 | ElectionDistrict2103 | NEW CASTLE | 1,007 | 331,074 | 66.1346448105 | yes |
| 236 | ElectionDistrict2714 | NEW CASTLE | 1,005 | 332,079 | 66.3354014934 | yes |
| 237 | ElectionDistrict2113 | NEW CASTLE | 1,004 | 333,083 | 66.5359584184 | yes |
| 238 | ElectionDistrict0102 | NEW CASTLE | 1,003 | 334,086 | 66.7363155855 | yes |
| 239 | ElectionDistrict1007 | NEW CASTLE | 1,001 | 335,087 | 66.9362732368 | yes |
| 240 | ElectionDistrict1308 | NEW CASTLE | 997 | 336,084 | 67.1354318566 | yes |
| 241 | ElectionDistrict3103 | KENT | 996 | 337,080 | 67.3343907184 | yes |
| 242 | ElectionDistrict2307 | NEW CASTLE | 991 | 338,071 | 67.5323507908 | yes |
| 243 | ElectionDistrict1009 | NEW CASTLE | 985 | 339,056 | 67.7291123159 | yes |
| 244 | ElectionDistrict2303 | NEW CASTLE | 971 | 340,027 | 67.9230772304 | yes |
| 245 | ElectionDistrict1301 | NEW CASTLE | 970 | 340,997 | 68.1168423870 | yes |
| 246 | ElectionDistrict0607 | NEW CASTLE | 968 | 341,965 | 68.3102080279 | yes |
| 247 | ElectionDistrict4005 | SUSSEX | 968 | 342,933 | 68.5035736687 | yes |
| 248 | ElectionDistrict3210 | KENT | 967 | 343,900 | 68.6967395517 | yes |
| 249 | ElectionDistrict0407 | SUSSEX | 965 | 344,865 | 68.8895059188 | yes |
| 250 | ElectionDistrict1004 | NEW CASTLE | 959 | 345,824 | 69.0810737386 | yes |
| 251 | ElectionDistrict2108 | NEW CASTLE | 959 | 346,783 | 69.2726415584 | yes |
| 252 | ElectionDistrict2504 | NEW CASTLE | 959 | 347,742 | 69.4642093782 | yes |
| 253 | ElectionDistrict1305 | NEW CASTLE | 957 | 348,699 | 69.6553776822 | yes |
| 254 | ElectionDistrict4109 | SUSSEX | 952 | 349,651 | 69.8455471968 | yes |
| 255 | ElectionDistrict3312 | KENT | 951 | 350,602 | 70.0355169535 | yes |
| 256 | ElectionDistrict0309 | NEW CASTLE | 944 | 351,546 | 70.2240884049 | yes |
| 257 | ElectionDistrict0506 | NEW CASTLE | 942 | 352,488 | 70.4122603405 | yes |
| 258 | ElectionDistrict2305 | NEW CASTLE | 938 | 353,426 | 70.5996332445 | yes |
| 259 | ElectionDistrict0601 | NEW CASTLE | 937 | 354,363 | 70.7868063907 | yes |
| 260 | ElectionDistrict1203 | NEW CASTLE | 937 | 355,300 | 70.9739795368 | yes |
| 261 | ElectionDistrict2401 | NEW CASTLE | 936 | 356,236 | 71.1609529251 | yes |
| 262 | ElectionDistrict0804 | NEW CASTLE | 935 | 357,171 | 71.3477265554 | yes |
| 263 | ElectionDistrict1602 | NEW CASTLE | 934 | 358,105 | 71.5343004279 | yes |
| 264 | ElectionDistrict0704 | NEW CASTLE | 932 | 359,037 | 71.7204747846 | yes |
| 265 | ElectionDistrict0207 | NEW CASTLE | 930 | 359,967 | 71.9062496255 | yes |
| 266 | ElectionDistrict3201 | KENT | 930 | 360,897 | 72.0920244663 | yes |
| 267 | ElectionDistrict0113 | NEW CASTLE | 926 | 361,823 | 72.2770002757 | yes |
| 268 | ElectionDistrict0307 | NEW CASTLE | 926 | 362,749 | 72.4619760850 | yes |
| 269 | ElectionDistrict1309 | NEW CASTLE | 924 | 363,673 | 72.6465523785 | yes |
| 270 | ElectionDistrict3502 | SUSSEX | 918 | 364,591 | 72.8299301247 | yes |
| 271 | ElectionDistrict1504 | NEW CASTLE | 915 | 365,506 | 73.0127085972 | yes |
| 272 | ElectionDistrict1712 | NEW CASTLE | 915 | 366,421 | 73.1954870697 | yes |
| 273 | ElectionDistrict2703 | NEW CASTLE | 915 | 367,336 | 73.3782655422 | yes |
| 274 | ElectionDistrict3901 | SUSSEX | 910 | 368,246 | 73.5600452252 | yes |
| 275 | ElectionDistrict0605 | NEW CASTLE | 908 | 369,154 | 73.7414253924 | yes |
| 276 | ElectionDistrict3711 | SUSSEX | 908 | 370,062 | 73.9228055597 | yes |
| 277 | ElectionDistrict1502 | NEW CASTLE | 906 | 370,968 | 74.1037862111 | yes |
| 278 | ElectionDistrict1008 | NEW CASTLE | 904 | 371,872 | 74.2843673468 | yes |
| 279 | ElectionDistrict0504 | NEW CASTLE | 901 | 372,773 | 74.4643492088 | yes |
| 280 | ElectionDistrict0505 | NEW CASTLE | 901 | 373,674 | 74.6443310707 | yes |
| 281 | ElectionDistrict3307 | KENT | 897 | 374,571 | 74.8235139012 | yes |
| 282 | ElectionDistrict1607 | NEW CASTLE | 896 | 375,467 | 75.0024969737 | yes |
| 283 | ElectionDistrict3610 | SUSSEX | 895 | 376,362 | 75.1812802883 | yes |
| 284 | ElectionDistrict1701 | NEW CASTLE | 894 | 377,256 | 75.3598638450 | yes |
| 285 | ElectionDistrict3410 | KENT | 894 | 378,150 | 75.5384474017 | yes |
| 286 | ElectionDistrict3212 | KENT | 893 | 379,043 | 75.7168312006 | yes |
| 287 | ElectionDistrict0709 | NEW CASTLE | 891 | 379,934 | 75.8948154836 | yes |
| 288 | ElectionDistrict2004 | SUSSEX | 886 | 380,820 | 76.0718009772 | yes |
| 289 | ElectionDistrict4003 | SUSSEX | 884 | 381,704 | 76.2483869550 | yes |
| 290 | ElectionDistrict0110 | NEW CASTLE | 883 | 382,587 | 76.4247731749 | yes |
| 291 | ElectionDistrict3608 | SUSSEX | 880 | 383,467 | 76.6005601211 | yes |
| 292 | ElectionDistrict0109 | NEW CASTLE | 877 | 384,344 | 76.7757477937 | yes |
| 293 | ElectionDistrict0308 | NEW CASTLE | 874 | 385,218 | 76.9503361925 | yes |
| 294 | ElectionDistrict0104 | NEW CASTLE | 871 | 386,089 | 77.1243253177 | yes |
| 295 | ElectionDistrict0702 | NEW CASTLE | 868 | 386,957 | 77.2977151692 | yes |
| 296 | ElectionDistrict0701 | NEW CASTLE | 867 | 387,824 | 77.4709052628 | yes |
| 297 | ElectionDistrict2803 | KENT | 867 | 388,691 | 77.6440953564 | yes |
| 298 | ElectionDistrict0216 | NEW CASTLE | 863 | 389,554 | 77.8164864185 | yes |
| 299 | ElectionDistrict1705 | NEW CASTLE | 862 | 390,416 | 77.9886777226 | yes |
| 300 | ElectionDistrict3707 | SUSSEX | 858 | 391,274 | 78.1600699952 | yes |
| 301 | ElectionDistrict1407 | SUSSEX | 853 | 392,127 | 78.3304634783 | yes |
| 302 | ElectionDistrict3812 | SUSSEX | 853 | 392,980 | 78.5008569614 | yes |
| 303 | ElectionDistrict0510 | NEW CASTLE | 851 | 393,831 | 78.6708509287 | yes |
| 304 | ElectionDistrict2804 | KENT | 850 | 394,681 | 78.8406451381 | yes |
| 305 | ElectionDistrict0101 | NEW CASTLE | 845 | 395,526 | 79.0094405580 | yes |
| 306 | ElectionDistrict0604 | NEW CASTLE | 842 | 396,368 | 79.1776367043 | yes |
| 307 | ElectionDistrict0507 | NEW CASTLE | 837 | 397,205 | 79.3448340611 | yes |
| 308 | ElectionDistrict2503 | NEW CASTLE | 837 | 398,042 | 79.5120314179 | yes |
| 309 | ElectionDistrict1912 | NEW CASTLE | 833 | 398,875 | 79.6784297432 | yes |
| 310 | ElectionDistrict2706 | NEW CASTLE | 833 | 399,708 | 79.8448280684 | yes |
| 311 | ElectionDistrict0807 | NEW CASTLE | 831 | 400,539 | 80.0108268778 | yes |
| 312 | ElectionDistrict0908 | NEW CASTLE | 831 | 401,370 | 80.1768256873 | remainder |
| 313 | ElectionDistrict4101 | SUSSEX | 829 | 402,199 | 80.3424249809 | remainder |
| 314 | ElectionDistrict1603 | NEW CASTLE | 820 | 403,019 | 80.5062264535 | remainder |
| 315 | ElectionDistrict3015 | KENT | 816 | 403,835 | 80.6692288946 | remainder |
| 316 | ElectionDistrict3002 | KENT | 815 | 404,650 | 80.8320315777 | remainder |
| 317 | ElectionDistrict0711 | NEW CASTLE | 814 | 405,464 | 80.9946345030 | remainder |
| 318 | ElectionDistrict2602 | NEW CASTLE | 811 | 406,275 | 81.1566381546 | remainder |
| 319 | ElectionDistrict0613 | NEW CASTLE | 810 | 407,085 | 81.3184420482 | remainder |
| 320 | ElectionDistrict1709 | NEW CASTLE | 809 | 407,894 | 81.4800461840 | remainder |
| 321 | ElectionDistrict3407 | KENT | 809 | 408,703 | 81.6416503198 | remainder |
| 322 | ElectionDistrict4008 | SUSSEX | 804 | 409,507 | 81.8022556661 | remainder |
| 323 | ElectionDistrict1707 | NEW CASTLE | 794 | 410,301 | 81.9608634335 | remainder |
| 324 | ElectionDistrict1606 | NEW CASTLE | 791 | 411,092 | 82.1188719272 | remainder |
| 325 | ElectionDistrict1902 | NEW CASTLE | 790 | 411,882 | 82.2766806630 | remainder |
| 326 | ElectionDistrict2403 | NEW CASTLE | 788 | 412,670 | 82.4340898831 | remainder |
| 327 | ElectionDistrict0509 | NEW CASTLE | 783 | 413,453 | 82.5905003136 | remainder |
| 328 | ElectionDistrict3110 | KENT | 783 | 414,236 | 82.7469107442 | remainder |
| 329 | ElectionDistrict1710 | NEW CASTLE | 775 | 415,011 | 82.9017231116 | remainder |
| 330 | ElectionDistrict3506 | SUSSEX | 775 | 415,786 | 83.0565354790 | remainder |
| 331 | ElectionDistrict1311 | NEW CASTLE | 774 | 416,560 | 83.2111480885 | remainder |
| 332 | ElectionDistrict3203 | KENT | 772 | 417,332 | 83.3653611822 | remainder |
| 333 | ElectionDistrict3805 | SUSSEX | 769 | 418,101 | 83.5189750023 | remainder |
| 334 | ElectionDistrict3607 | SUSSEX | 766 | 418,867 | 83.6719895487 | remainder |
| 335 | ElectionDistrict1807 | NEW CASTLE | 765 | 419,632 | 83.8248043371 | remainder |
| 336 | ElectionDistrict2206 | NEW CASTLE | 762 | 420,394 | 83.9770198519 | remainder |
| 337 | ElectionDistrict2510 | NEW CASTLE | 759 | 421,153 | 84.1286360931 | remainder |
| 338 | ElectionDistrict2411 | NEW CASTLE | 756 | 421,909 | 84.2796530605 | remainder |
| 339 | ElectionDistrict0503 | NEW CASTLE | 752 | 422,661 | 84.4298709964 | remainder |
| 340 | ElectionDistrict0608 | NEW CASTLE | 750 | 423,411 | 84.5796894164 | remainder |
| 341 | ElectionDistrict1302 | NEW CASTLE | 750 | 424,161 | 84.7295078365 | remainder |
| 342 | ElectionDistrict1907 | NEW CASTLE | 744 | 424,905 | 84.8781277092 | remainder |
| 343 | ElectionDistrict1609 | NEW CASTLE | 743 | 425,648 | 85.0265478240 | remainder |
| 344 | ElectionDistrict1612 | NEW CASTLE | 741 | 426,389 | 85.1745684231 | remainder |
| 345 | ElectionDistrict1505 | NEW CASTLE | 736 | 427,125 | 85.3215902326 | remainder |
| 346 | ElectionDistrict3014 | KENT | 733 | 427,858 | 85.4680127685 | remainder |
| 347 | ElectionDistrict2603 | NEW CASTLE | 732 | 428,590 | 85.6142355465 | remainder |
| 348 | ElectionDistrict4110 | SUSSEX | 731 | 429,321 | 85.7602585666 | remainder |
| 349 | ElectionDistrict1501 | NEW CASTLE | 729 | 430,050 | 85.9058820709 | remainder |
| 350 | ElectionDistrict0410 | SUSSEX | 724 | 430,774 | 86.0505067858 | remainder |
| 351 | ElectionDistrict2006 | SUSSEX | 717 | 431,491 | 86.1937331954 | remainder |
| 352 | ElectionDistrict3907 | SUSSEX | 716 | 432,207 | 86.3367598471 | remainder |
| 353 | ElectionDistrict4113 | SUSSEX | 716 | 432,923 | 86.4797864988 | remainder |
| 354 | ElectionDistrict2407 | NEW CASTLE | 715 | 433,638 | 86.6226133926 | remainder |
| 355 | ElectionDistrict0708 | NEW CASTLE | 711 | 434,349 | 86.7646412548 | remainder |
| 356 | ElectionDistrict0304 | NEW CASTLE | 703 | 435,052 | 86.9050710539 | remainder |
| 357 | ElectionDistrict1910 | NEW CASTLE | 703 | 435,755 | 87.0455008530 | remainder |
| 358 | ElectionDistrict0710 | NEW CASTLE | 700 | 436,455 | 87.1853313784 | remainder |
| 359 | ElectionDistrict0206 | NEW CASTLE | 686 | 437,141 | 87.3223652933 | remainder |
| 360 | ElectionDistrict2101 | NEW CASTLE | 671 | 437,812 | 87.4564028398 | remainder |
| 361 | ElectionDistrict3504 | SUSSEX | 665 | 438,477 | 87.5892418389 | remainder |
| 362 | ElectionDistrict0114 | NEW CASTLE | 660 | 439,137 | 87.7210820486 | remainder |
| 363 | ElectionDistrict3507 | SUSSEX | 660 | 439,797 | 87.8529222582 | remainder |
| 364 | ElectionDistrict0703 | NEW CASTLE | 659 | 440,456 | 87.9845627100 | remainder |
| 365 | ElectionDistrict0111 | NEW CASTLE | 657 | 441,113 | 88.1158036460 | remainder |
| 366 | ElectionDistrict1215 | NEW CASTLE | 657 | 441,770 | 88.2470445820 | remainder |
| 367 | ElectionDistrict3108 | KENT | 655 | 442,425 | 88.3778860022 | remainder |
| 368 | ElectionDistrict0811 | NEW CASTLE | 653 | 443,078 | 88.5083279066 | remainder |
| 369 | ElectionDistrict0227 | NEW CASTLE | 651 | 443,729 | 88.6383702952 | remainder |
| 370 | ElectionDistrict0211 | NEW CASTLE | 650 | 444,379 | 88.7682129259 | remainder |
| 371 | ElectionDistrict2109 | NEW CASTLE | 649 | 445,028 | 88.8978557988 | remainder |
| 372 | ElectionDistrict2406 | NEW CASTLE | 647 | 445,675 | 89.0270991558 | remainder |
| 373 | ElectionDistrict0103 | NEW CASTLE | 644 | 446,319 | 89.1557432392 | remainder |
| 374 | ElectionDistrict0712 | NEW CASTLE | 643 | 446,962 | 89.2841875647 | remainder |
| 375 | ElectionDistrict0303 | NEW CASTLE | 635 | 447,597 | 89.4110338270 | remainder |
| 376 | ElectionDistrict1206 | NEW CASTLE | 631 | 448,228 | 89.5370810578 | remainder |
| 377 | ElectionDistrict0502 | NEW CASTLE | 630 | 448,858 | 89.6629285306 | remainder |
| 378 | ElectionDistrict0904 | NEW CASTLE | 629 | 449,487 | 89.7885762456 | remainder |
| 379 | ElectionDistrict2813 | KENT | 628 | 450,115 | 89.9140242027 | remainder |
| 380 | ElectionDistrict3513 | SUSSEX | 626 | 450,741 | 90.0390726440 | remainder |
| 381 | ElectionDistrict1611 | NEW CASTLE | 625 | 451,366 | 90.1639213274 | remainder |
| 382 | ElectionDistrict2112 | NEW CASTLE | 625 | 451,991 | 90.2887700107 | remainder |
| 383 | ElectionDistrict2013 | SUSSEX | 617 | 452,608 | 90.4120206310 | remainder |
| 384 | ElectionDistrict1108 | KENT | 615 | 453,223 | 90.5348717355 | remainder |
| 385 | ElectionDistrict0204 | NEW CASTLE | 613 | 453,836 | 90.6573233241 | remainder |
| 386 | ElectionDistrict2715 | NEW CASTLE | 609 | 454,445 | 90.7789758812 | remainder |
| 387 | ElectionDistrict3109 | KENT | 608 | 455,053 | 90.9004286804 | remainder |
| 388 | ElectionDistrict1704 | NEW CASTLE | 604 | 455,657 | 91.0210824481 | remainder |
| 389 | ElectionDistrict1803 | NEW CASTLE | 603 | 456,260 | 91.1415364578 | remainder |
| 390 | ElectionDistrict2409 | NEW CASTLE | 598 | 456,858 | 91.2609916781 | remainder |
| 391 | ElectionDistrict2312 | NEW CASTLE | 594 | 457,452 | 91.3796478668 | remainder |
| 392 | ElectionDistrict3605 | SUSSEX | 591 | 458,043 | 91.4977047818 | remainder |
| 393 | ElectionDistrict0301 | NEW CASTLE | 580 | 458,623 | 91.6135643600 | remainder |
| 394 | ElectionDistrict0305 | NEW CASTLE | 580 | 459,203 | 91.7294239382 | remainder |
| 395 | ElectionDistrict3310 | KENT | 580 | 459,783 | 91.8452835164 | remainder |
| 396 | ElectionDistrict0208 | NEW CASTLE | 577 | 460,360 | 91.9605438209 | remainder |
| 397 | ElectionDistrict1809 | NEW CASTLE | 576 | 460,936 | 92.0756043675 | remainder |
| 398 | ElectionDistrict1307 | NEW CASTLE | 573 | 461,509 | 92.1900656404 | remainder |
| 399 | ElectionDistrict3813 | SUSSEX | 573 | 462,082 | 92.3045269134 | remainder |
| 400 | ElectionDistrict1314 | NEW CASTLE | 572 | 462,654 | 92.4187884284 | remainder |
| 401 | ElectionDistrict3017 | KENT | 569 | 463,223 | 92.5324506698 | remainder |
| 402 | ElectionDistrict3404 | KENT | 566 | 463,789 | 92.6455136375 | remainder |
| 403 | ElectionDistrict0706 | NEW CASTLE | 561 | 464,350 | 92.7575778157 | remainder |
| 404 | ElectionDistrict1508 | NEW CASTLE | 554 | 464,904 | 92.8682436886 | remainder |
| 405 | ElectionDistrict2404 | NEW CASTLE | 540 | 465,444 | 92.9761129511 | remainder |
| 406 | ElectionDistrict3402 | KENT | 538 | 465,982 | 93.0835826978 | remainder |
| 407 | ElectionDistrict1113 | KENT | 535 | 466,517 | 93.1904531708 | remainder |
| 408 | ElectionDistrict1213 | NEW CASTLE | 533 | 467,050 | 93.2969241280 | remainder |
| 409 | ElectionDistrict3107 | KENT | 533 | 467,583 | 93.4033950852 | remainder |
| 410 | ElectionDistrict2812 | KENT | 532 | 468,115 | 93.5096662845 | remainder |
| 411 | ElectionDistrict2811 | KENT | 530 | 468,645 | 93.6155379680 | remainder |
| 412 | ElectionDistrict1411 | SUSSEX | 513 | 469,158 | 93.7180137673 | remainder |
| 413 | ElectionDistrict3311 | KENT | 511 | 469,669 | 93.8200900509 | remainder |
| 414 | ElectionDistrict2810 | KENT | 510 | 470,179 | 93.9219665765 | remainder |
| 415 | ElectionDistrict2716 | NEW CASTLE | 507 | 470,686 | 94.0232438285 | remainder |
| 416 | ElectionDistrict0411 | SUSSEX | 506 | 471,192 | 94.1243213226 | remainder |
| 417 | ElectionDistrict3908 | SUSSEX | 506 | 471,698 | 94.2253988166 | remainder |
| 418 | ElectionDistrict1911 | NEW CASTLE | 505 | 472,203 | 94.3262765528 | remainder |
| 419 | ElectionDistrict3010 | KENT | 505 | 472,708 | 94.4271542890 | remainder |
| 420 | ElectionDistrict1905 | NEW CASTLE | 490 | 473,198 | 94.5250356568 | remainder |
| 421 | ElectionDistrict0209 | NEW CASTLE | 486 | 473,684 | 94.6221179930 | remainder |
| 422 | ElectionDistrict1708 | NEW CASTLE | 485 | 474,169 | 94.7190005713 | remainder |
| 423 | ElectionDistrict2011 | SUSSEX | 483 | 474,652 | 94.8154836338 | remainder |
| 424 | ElectionDistrict4009 | SUSSEX | 483 | 475,135 | 94.9119666964 | remainder |
| 425 | ElectionDistrict3712 | SUSSEX | 482 | 475,617 | 95.0082500010 | remainder |
| 426 | ElectionDistrict2501 | NEW CASTLE | 477 | 476,094 | 95.1035345162 | remainder |
| 427 | ElectionDistrict3301 | KENT | 476 | 476,570 | 95.1986192734 | remainder |
| 428 | ElectionDistrict3207 | KENT | 475 | 477,045 | 95.2935042728 | remainder |
| 429 | ElectionDistrict3011 | KENT | 470 | 477,515 | 95.3873904827 | remainder |
| 430 | ElectionDistrict3611 | SUSSEX | 465 | 477,980 | 95.4802779032 | remainder |
| 431 | ElectionDistrict2508 | NEW CASTLE | 463 | 478,443 | 95.5727658078 | remainder |
| 432 | ElectionDistrict1110 | KENT | 462 | 478,905 | 95.6650539546 | remainder |
| 433 | ElectionDistrict1310 | NEW CASTLE | 462 | 479,367 | 95.7573421014 | remainder |
| 434 | ElectionDistrict3007 | KENT | 457 | 479,824 | 95.8486314587 | remainder |
| 435 | ElectionDistrict0205 | NEW CASTLE | 448 | 480,272 | 95.9381229949 | remainder |
| 436 | ElectionDistrict3705 | SUSSEX | 447 | 480,719 | 96.0274147733 | remainder |
| 437 | ElectionDistrict3016 | KENT | 446 | 481,165 | 96.1165067938 | remainder |
| 438 | ElectionDistrict1107 | KENT | 444 | 481,609 | 96.2051992985 | remainder |
| 439 | ElectionDistrict2707 | NEW CASTLE | 443 | 482,052 | 96.2936920452 | remainder |
| 440 | ElectionDistrict0210 | NEW CASTLE | 438 | 482,490 | 96.3811860026 | remainder |
| 441 | ElectionDistrict3209 | KENT | 435 | 482,925 | 96.4680806862 | remainder |
| 442 | ElectionDistrict0714 | NEW CASTLE | 431 | 483,356 | 96.5541763383 | remainder |
| 443 | ElectionDistrict0106 | NEW CASTLE | 430 | 483,786 | 96.6400722325 | remainder |
| 444 | ElectionDistrict4112 | SUSSEX | 428 | 484,214 | 96.7255686108 | remainder |
| 445 | ElectionDistrict0217 | NEW CASTLE | 422 | 484,636 | 96.8098664419 | remainder |
| 446 | ElectionDistrict3710 | SUSSEX | 422 | 485,058 | 96.8941642729 | remainder |
| 447 | ElectionDistrict3202 | KENT | 406 | 485,464 | 96.9752659776 | remainder |
| 448 | ElectionDistrict2809 | KENT | 397 | 485,861 | 97.0545698613 | remainder |
| 449 | ElectionDistrict3204 | KENT | 390 | 486,251 | 97.1324754398 | remainder |
| 450 | ElectionDistrict3909 | SUSSEX | 374 | 486,625 | 97.2071848919 | remainder |
| 451 | ElectionDistrict4103 | SUSSEX | 368 | 486,993 | 97.2806957967 | remainder |
| 452 | ElectionDistrict1109 | KENT | 362 | 487,355 | 97.3530081541 | remainder |
| 453 | ElectionDistrict1207 | NEW CASTLE | 358 | 487,713 | 97.4245214800 | remainder |
| 454 | ElectionDistrict3003 | KENT | 357 | 488,070 | 97.4958350479 | remainder |
| 455 | ElectionDistrict1111 | KENT | 355 | 488,425 | 97.5667491001 | remainder |
| 456 | ElectionDistrict3004 | KENT | 352 | 488,777 | 97.6370638786 | remainder |
| 457 | ElectionDistrict1114 | KENT | 349 | 489,126 | 97.7067793834 | remainder |
| 458 | ElectionDistrict3709 | SUSSEX | 342 | 489,468 | 97.7750965829 | remainder |
| 459 | ElectionDistrict2814 | KENT | 336 | 489,804 | 97.8422152351 | remainder |
| 460 | ElectionDistrict0201 | NEW CASTLE | 328 | 490,132 | 97.9077358242 | remainder |
| 461 | ElectionDistrict2114 | NEW CASTLE | 314 | 490,446 | 97.9704598027 | remainder |
| 462 | ElectionDistrict4114 | SUSSEX | 312 | 490,758 | 98.0327842655 | remainder |
| 463 | ElectionDistrict0306 | NEW CASTLE | 307 | 491,065 | 98.0941099388 | remainder |
| 464 | ElectionDistrict1604 | NEW CASTLE | 306 | 491,371 | 98.1552358541 | remainder |
| 465 | ElectionDistrict2910 | KENT | 304 | 491,675 | 98.2159622537 | remainder |
| 466 | ElectionDistrict0603 | NEW CASTLE | 297 | 491,972 | 98.2752903481 | remainder |
| 467 | ElectionDistrict0202 | NEW CASTLE | 287 | 492,259 | 98.3326208635 | remainder |
| 468 | ElectionDistrict1613 | NEW CASTLE | 271 | 492,530 | 98.3867552526 | remainder |
| 469 | ElectionDistrict2704 | NEW CASTLE | 263 | 492,793 | 98.4392915786 | remainder |
| 470 | ElectionDistrict3306 | KENT | 254 | 493,047 | 98.4900300835 | remainder |
| 471 | ElectionDistrict2911 | KENT | 245 | 493,292 | 98.5389707674 | remainder |
| 472 | ElectionDistrict1112 | KENT | 243 | 493,535 | 98.5875119355 | remainder |
| 473 | ElectionDistrict2308 | NEW CASTLE | 239 | 493,774 | 98.6352540721 | remainder |
| 474 | ElectionDistrict1303 | NEW CASTLE | 236 | 494,010 | 98.6823969349 | remainder |
| 475 | ElectionDistrict1906 | NEW CASTLE | 220 | 494,230 | 98.7263436715 | remainder |
| 476 | ElectionDistrict0311 | NEW CASTLE | 218 | 494,448 | 98.7698908922 | remainder |
| 477 | ElectionDistrict0310 | NEW CASTLE | 216 | 494,664 | 98.8130385972 | remainder |
| 478 | ElectionDistrict1208 | NEW CASTLE | 216 | 494,880 | 98.8561863022 | remainder |
| 479 | ElectionDistrict0107 | NEW CASTLE | 214 | 495,094 | 98.8989344914 | remainder |
| 480 | ElectionDistrict0909 | NEW CASTLE | 206 | 495,300 | 98.9400846174 | remainder |
| 481 | ElectionDistrict3206 | KENT | 204 | 495,504 | 98.9808352277 | remainder |
| 482 | ElectionDistrict2711 | NEW CASTLE | 193 | 495,697 | 99.0193885011 | remainder |
| 483 | ElectionDistrict3609 | SUSSEX | 188 | 495,885 | 99.0569429851 | remainder |
| 484 | ElectionDistrict4116 | SUSSEX | 188 | 496,073 | 99.0944974691 | remainder |
| 485 | ElectionDistrict2702 | NEW CASTLE | 187 | 496,260 | 99.1318521951 | remainder |
| 486 | ElectionDistrict0212 | NEW CASTLE | 183 | 496,443 | 99.1684078896 | remainder |
| 487 | ElectionDistrict2310 | NEW CASTLE | 183 | 496,626 | 99.2049635841 | remainder |
| 488 | ElectionDistrict3512 | SUSSEX | 183 | 496,809 | 99.2415192786 | remainder |
| 489 | ElectionDistrict1313 | NEW CASTLE | 180 | 496,989 | 99.2774756995 | remainder |
| 490 | ElectionDistrict3511 | SUSSEX | 174 | 497,163 | 99.3122335729 | remainder |
| 491 | ElectionDistrict0314 | NEW CASTLE | 169 | 497,332 | 99.3459926569 | remainder |
| 492 | ElectionDistrict3708 | SUSSEX | 167 | 497,499 | 99.3793522251 | remainder |
| 493 | ElectionDistrict2608 | NEW CASTLE | 162 | 497,661 | 99.4117130038 | remainder |
| 494 | ElectionDistrict1212 | NEW CASTLE | 159 | 497,820 | 99.4434745089 | remainder |
| 495 | ElectionDistrict0203 | NEW CASTLE | 158 | 497,978 | 99.4750362561 | remainder |
| 496 | ElectionDistrict2709 | NEW CASTLE | 158 | 498,136 | 99.5065980032 | remainder |
| 497 | ElectionDistrict2301 | NEW CASTLE | 154 | 498,290 | 99.5373607188 | remainder |
| 498 | ElectionDistrict3208 | KENT | 150 | 498,440 | 99.5673244028 | remainder |
| 499 | ElectionDistrict0112 | NEW CASTLE | 137 | 498,577 | 99.5946912342 | remainder |
| 500 | ElectionDistrict1706 | NEW CASTLE | 135 | 498,712 | 99.6216585498 | remainder |
| 501 | ElectionDistrict0615 | NEW CASTLE | 126 | 498,838 | 99.6468280444 | remainder |
| 502 | ElectionDistrict3510 | SUSSEX | 125 | 498,963 | 99.6717977811 | remainder |
| 503 | ElectionDistrict2801 | NEW CASTLE | 124 | 499,087 | 99.6965677599 | remainder |
| 504 | ElectionDistrict2909 | KENT | 123 | 499,210 | 99.7211379808 | remainder |
| 505 | ElectionDistrict2412 | NEW CASTLE | 117 | 499,327 | 99.7445096543 | remainder |
| 506 | ElectionDistrict0215 | NEW CASTLE | 108 | 499,435 | 99.7660835068 | remainder |
| 507 | ElectionDistrict0614 | NEW CASTLE | 108 | 499,543 | 99.7876573593 | remainder |
| 508 | ElectionDistrict0511 | NEW CASTLE | 102 | 499,645 | 99.8080326644 | remainder |
| 509 | ElectionDistrict2107 | NEW CASTLE | 102 | 499,747 | 99.8284079695 | remainder |
| 510 | ElectionDistrict0218 | NEW CASTLE | 96 | 499,843 | 99.8475847273 | remainder |
| 511 | ElectionDistrict1315 | NEW CASTLE | 80 | 499,923 | 99.8635653588 | remainder |
| 512 | ElectionDistrict3116 | KENT | 76 | 499,999 | 99.8787469587 | remainder |
| 513 | ElectionDistrict0213 | NEW CASTLE | 74 | 500,073 | 99.8935290428 | remainder |
| 514 | ElectionDistrict0214 | NEW CASTLE | 71 | 500,144 | 99.9077118532 | remainder |
| 515 | ElectionDistrict0312 | NEW CASTLE | 68 | 500,212 | 99.9212953900 | remainder |
| 516 | ElectionDistrict1610 | NEW CASTLE | 68 | 500,280 | 99.9348789267 | remainder |
| 517 | ElectionDistrict0313 | NEW CASTLE | 59 | 500,339 | 99.9466646425 | remainder |
| 518 | ElectionDistrict1713 | NEW CASTLE | 53 | 500,392 | 99.9572518108 | remainder |
| 519 | ElectionDistrict3006 | KENT | 45 | 500,437 | 99.9662409160 | remainder |
| 520 | ElectionDistrict0116 | NEW CASTLE | 41 | 500,478 | 99.9744309896 | remainder |
| 521 | ElectionDistrict2511 | NEW CASTLE | 32 | 500,510 | 99.9808232422 | remainder |
| 522 | ElectionDistrict0907 | NEW CASTLE | 29 | 500,539 | 99.9866162211 | remainder |
| 523 | ElectionDistrict0220 | NEW CASTLE | 26 | 500,565 | 99.9918099264 | remainder |
| 524 | ElectionDistrict2115 | NEW CASTLE | 16 | 500,581 | 99.9950060527 | remainder |
| 525 | ElectionDistrict0115 | NEW CASTLE | 11 | 500,592 | 99.9972033895 | remainder |
| 526 | ElectionDistrict0219 | NEW CASTLE | 5 | 500,597 | 99.9982021790 | remainder |
| 527 | ElectionDistrict1312 | NEW CASTLE | 5 | 500,602 | 99.9992009684 | remainder |
| 528 | ElectionDistrict0221 | NEW CASTLE | 3 | 500,605 | 99.9998002421 | remainder |
| 529 | ElectionDistrict0713 | NEW CASTLE | 1 | 500,606 | 100.0000000000 | remainder |
| 530 | ElectionDistrict1714 | NEW CASTLE | 0 | 500,606 | 100.0000000000 | remainder |


