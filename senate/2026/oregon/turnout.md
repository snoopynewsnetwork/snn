# Oregon reporting-geography vote volume

**Research snapshot: 2026-10-20. The complete certified statewide native ranking, top-15 share and minimum 80% set are unavailable.** All 36 county presidential controls are complete, but only five 2024 native county universes have been recovered and reconciled. The [dispatch contract](data/turnout/priority-set.json) therefore keeps canonical order/priority keys/top15/min80 null and every approval false or pending. County aggregates are a separate sensitivity, not a replacement for unavailable precincts.

The priority contest is actual **2024 president**, with **2,244,493 reported votes**: seven printed named candidates plus **15,026 Misc.** The named-candidate-only total is **2,229,467**. Misc. is not proved legally valid named write-ins. Oregon had no 2024 U.S. Senate contest; 2020 Merkley Senate is the Class II comparison and 2022 Wyden Senate is the other Class III seat and recent midterm. Governor is an additional 2022 sensitivity. Source: [complete 2024 abstract, page 1](https://web.archive.org/web/20241212212240id_/https://sos.oregon.gov/elections/Documents/results/november-general-2024-results.pdf), [2020 Senate, page 2](https://records.sos.state.or.us/ORSOSCMSearch/Search/DocumentStream.ashx?uri=13735450), [2022 Senate/Governor, pages 1/4](https://records.sos.state.or.us/ORSOSWebDrawer/Record/13735454/File/document).

## Exact county-parent sensitivity

**Top 15, descending:** Multnomah, Washington, Clackamas, Lane, Marion, Deschutes, Jackson, Linn, Douglas, Yamhill, Benton, Josephine, Polk, Coos, Klamath.

They supply **1,983,101 / 2,244,493 = 88.35407373%**. The **minimum descending set reaching 80% is 11 counties**: Multnomah, Washington, Clackamas, Lane, Marion, Deschutes, Jackson, Linn, Douglas, Yamhill, Benton. The first **10** supply **1,764,398 = 78.61009145%**; **Benton (50,232)** crosses to **1,814,630 = 80.84810244%**. The remaining **25** counties retain **429,863** votes. These exact integers come from every county and every printed candidate/Misc. column in the [primary abstract](https://web.archive.org/web/20241212212240id_/https://sos.oregon.gov/elections/Documents/results/november-general-2024-results.pdf).

Largest-first ordering proves minimum cardinality: no ten-county set can exceed the largest ten. The threshold uses integers (`5*cumulative >= 4*statewide`), with ascending FIPS as the deterministic tie break. [Full orders and remainders for all sensitivities](data/turnout/county-sensitivities.json) include named-only alternatives. The compatibility [county-turnout.csv](data/county-turnout.csv) has 36 **county parent** rows and explicitly disclaims native dispatch.

## Qualified native universe: five counties, 510 rows

The disjoint recovered universe contains **1,128,521** candidate/generic-write-in votes, **50.27955088% of statewide reported votes**. The other **31** county parents retain **1,115,972** votes with unknown native membership. Even all 510 known rows cannot reach 80% of statewide votes. Their own universe is useful for a clearly qualified order; it cannot establish a statewide top 15 or geographic dispatch.

| Parent | Disjoint source rows | Original authority and qualification |
| --- | ---: | --- |
| Multnomah | 107 | [County precinct index](https://multco.us/info/precinct-results-november-2024-general-election) → [SOVC2 CSV](https://multco.us/file/sovc2_-_election20241105general.csv/download), [presidential PDF](https://multco.us/file/2024-11_pres_vp.pdf/download). Every eight-value CSV vector matches the PDF by the same printed precinct number. SOVC1/PDF summaries overlap. |
| Washington | 155 | [Official archive](https://www.washingtoncountyor.gov/elections/elections-archive) → [full certified scanned precinct original](https://www.washingtoncountyor.gov/elections/documents/november-5-2024-ballots-cast-contest-precincts/download?inline). Explicit original-row visual transcriptions repair OCR; no county residual allocation. |
| Clackamas | 118 | [County index](https://www.clackamas.us/elections/results.html) → [official canvass](https://dochub.clackamas.us/documents/drupal/3a834f56-37f7-4942-84da-8b0c38e90021). Source reports 119 precincts; combined **115/116** remains one disjoint row with both constituent IDs and unsplit counts. Explicit zero rows remain. |
| Marion | 118 | [County election page](https://www.co.marion.or.us/CO/elections/Results/Pages/November-5-2024-Presidential-Election.aspx) → [official canvass](https://www.co.marion.or.us/CO/elections/Results/Documents/20241105/Canvass%20Results-12-2-2024%2007-24-08%20PM.pdf). Cast Votes includes its separate generic-write-in candidate column. |
| Wasco | 12 | [Complete original record 10575034](https://records.sos.state.or.us/ORSOSWebDrawer/Record/10575034/File/document), signed certification and source text/raster. Presidential ballot/nonvote fields remain contest-specific. |

**Top 15 of this known-source universe only:**

| Rank | County / native precinct | Reported choices |
| ---: | --- | ---: |
| 1 | Multnomah / 4501 | 8,373 |
| 2 | Multnomah / 2806 | 7,757 |
| 3 | Multnomah / 2805 | 7,715 |
| 4 | Washington / 329 | 7,649 |
| 5 | Multnomah / 4502 | 7,633 |
| 6 | Washington / 389 | 7,604 |
| 7 | Multnomah / 4202 | 7,555 |
| 8 | Washington / 405 | 7,490 |
| 9 | Multnomah / 3803 | 7,473 |
| 10 | Multnomah / 4405 | 7,390 |
| 11 | Multnomah / 3304 | 7,338 |
| 12 | Multnomah / 4506 | 7,183 |
| 13 | Multnomah / 4503 | 7,047 |
| 14 | Multnomah / 4307 | 6,918 |
| 15 | Multnomah / 3302 | 6,899 |

Top 15: **112,024 / 1,128,521 = 9.92662077%** of known-source votes (not statewide native share). The minimum known-universe 80% set contains **213** rows. The first **212** total **902,447**; **Multnomah precinct 4906 (2,153)** crosses to **904,600 / 1,128,521 = 80.15801212%**. The remaining **297** known rows hold **223,921** votes. [All 510 rows, in full order](data/turnout/known-native-order.csv), [exact ordered 213 keys, predecessor, crossing and remainder](data/turnout/known-native-ranking.json), and [each parent/source constituent in the contract](data/turnout/priority-set.json) retain the complete known set. All figures are calculated directly from the five originals linked above.

## Candidate universe and statewide reconciliation

All **864** county candidate/Misc. positions reconcile to every selected printed statewide column footer. Totals below are sums of those columns, not ballots cast. Source labels are preserved in the [candidate universe](data/turnout/candidate-universe.json), [full county candidate rows](data/turnout/county-candidates.csv), and [source footers](data/turnout/source/statewide-footers.json).

| Contest | Printed candidate / party columns, statewide votes | Reported total |
| --- | --- | ---: |
| [2024-president, p. 1](https://web.archive.org/web/20241212212240id_/https://sos.oregon.gov/elections/Documents/results/november-general-2024-results.pdf) | Robert F Kennedy Jr (WTP) 33,733; Cornel West (P) 5,644; Chase Oliver (L) 9,061; Randall Terry (C) 1,850; Donald J Trump (R) 919,480; Jill Stein (PG) 19,099; Kamala D Harris (D) 1,240,600; Misc. 15,026 | 2,244,493 |
| [2020-senate, p. 2](https://records.sos.state.or.us/ORSOSCMSearch/Search/DocumentStream.ashx?uri=13735450) | Jo Rae Perkins (R) 912,814; Jeff Merkley (D) 1,321,047; Ibrahim A Taher (PG) 42,239; Gary Dye (L) 42,747; Misc. 2,402 | 2,321,249 |
| [2022-senate, p. 1](https://records.sos.state.or.us/ORSOSWebDrawer/Record/13735454/File/document) | Jo Rae Perkins (R) 788,991; Dan Pulju (PG) 23,454; Ron Wyden (D) 1,076,424; Chris Henry (P) 36,883; Misc. 2,197 | 1,927,949 |
| [2022-governor, p. 4](https://records.sos.state.or.us/ORSOSWebDrawer/Record/13735454/File/document) | Tina Kotek (D) 917,074; Donice Noelle Smith (C) 8,051; R Leon Noble (L) 6,867; Betsy Johnson (NAV) 168,431; Christine Drazan (R) 850,347; Misc. 2,113 | 1,952,883 |

The abstract’s separate **US Vice President** table has only six printed columns; [all 216 county positions](data/turnout/nonadditive-vice-president.csv) match their corresponding presidential columns and are **nonadditive**. No West/Terry vice-presidential column is invented. Native slates retain their full printed candidate/partner strings; source party abbreviations and generic/rejected/unassigned write-in scopes remain separate. [2024 original, pp. 1–2](https://web.archive.org/web/20241212212240id_/https://sos.oregon.gov/elections/Documents/results/november-general-2024-results.pdf).

## Midterm, ballot-return and registration sensitivity

The 2022 Governor universe includes **Betsy Johnson (NAV), 168,431 votes** in addition to Kotek, Drazan and the other printed candidates/Misc. That substantial third candidacy remains in the volume denominator. The 2022 Senate total is 1,927,949; Governor is 1,952,883. Comparing them with 2024 president changes both contest and year and does not isolate turnout or candidate effects. [2022 original, pp. 1/4](https://records.sos.state.or.us/ORSOSWebDrawer/Record/13735454/File/document).

| Complete 36-parent measure | State total | Top-15 votes / share | Minimum80 count | Preceding votes | Crossing parent | Crossing cumulative / share |
| --- | ---: | --- | ---: | ---: | --- | --- |
| 2020-senate reported votes | 2,321,249 | 2,056,417 / 88.59096978% | 11 | 1,834,530 | Benton | 1,886,573 / 81.27404686% |
| 2022-senate reported votes | 1,927,949 | 1,703,953 / 88.38164288% | 11 | 1,514,518 | Benton | 1,559,644 / 80.89653824% |
| 2022-governor reported votes | 1,952,883 | 1,726,309 / 88.39797366% | 11 | 1,534,872 | Benton | 1,580,191 / 80.91580499% |
| 2020 statistical ballots Returned | 2,413,890 | 2,138,859 / 88.60631595% | 11 | 1,908,074 | Benton | 1,961,912 / 81.27594878% |
| 2022 statistical ballots Returned | 1,997,689 | 1,766,386 / 88.42147101% | 11 | 1,570,281 | Benton | 1,616,983 / 80.94267927% |
| 2024 statistical ballots Returned | 2,308,256 | 2,040,583 / 88.40366926% | 11 | 1,815,401 | Benton | 1,867,565 / 80.90805353% |
| 2024 statistical registration Number Eligible | 3,060,374 | 2,694,547 / 88.04633029% | 11 | 2,394,825 | Josephine | 2,466,075 / 80.58083751% |

Ballot/registration rows use the election-specific statistical summaries’ **Ballots Returned** and registration **Number Eligible** total columns: [2020 p. 5](https://web.archive.org/web/20210101093606id_/https://sos.oregon.gov/elections/Documents/statistics/november-2020-statistical-summary-participation.pdf), [2022 p. 5](https://web.archive.org/web/20221221182416id_/https://sos.oregon.gov/elections/Documents/statistics/november-2022-statistical-summary-participation.pdf), [2024 p. 6](https://web.archive.org/web/20241227170225id_/https://sos.oregon.gov/elections/Documents/statistics/November-general-2024-statistical-summary-participation.pdf). All 36 county sums close both printed statewide controls: **2020 2,944,588 registered / 2,413,890 returned; 2022 2,985,820 / 1,997,689; 2024 3,060,374 / 2,308,256**. These registration records are not voting-eligible population. The 2024 PDF’s first-page prose erroneously says “Primary” despite its November general-election heading; the exact original is retained and the county table is explicitly general.

A returned ballot is not necessarily a canvass ballot or a vote for president. In 2024, statistical ballot returns exceed reported presidential choices by **63,763**; this is a cross-source denominator difference, not an allocation to blanks, overvotes, rejected or outstanding ballots. Monthly November registration comparisons are retained separately with their printed month/reference fields, not substituted for election-specific stocks. [2024 statistical summary](https://web.archive.org/web/20241227170225id_/https://sos.oregon.gov/elections/Documents/statistics/November-general-2024-statistical-summary-participation.pdf) and [abstract](https://web.archive.org/web/20241212212240id_/https://sos.oregon.gov/elections/Documents/results/november-general-2024-results.pdf).

Source discrepancies remain visible. The [current SOS historical-turnout PDF](https://sos.oregon.gov/elections/Documents/History/Voter_Turnout_History_General_Election.pdf), generated 09/12/2025, prints **2020 2,951,428 registered / 2,317,965 Total Votes Cast**, while the election-specific summary prints **2,944,588 / 2,413,890 ballots returned**. The history count is even below the 2,321,249 Senate reported choices. No rounding, rescaling or inferred date/status repair reconciles these scopes; the election-specific statistical series is the separately labeled sensitivity.

In Washington’s 2024 original, presidential-table ballots total **301,104**, whereas the repeated overall header says **301,105**. The table itself closes **297,949 choices + 170 overvotes + 2,985 undervotes = 301,104**. Wasco’s presidential ballots total **13,527**, with **13,391 choices + 8 overvotes + 128 undervotes**; precinct 01 explicitly has 1,831 presidential ballots while some other contests print 1,830. These are source/contest scopes, not residuals to distribute. Native ballot, registration, method and administrative fields are retained in [observations](data/turnout/native/observations.jsonl.gz), [source participation rows](data/turnout/native/participation-source-rows.jsonl.gz) and the [schema](data/turnout/source/SCHEMA.md). Originals: [Washington](https://www.washingtoncountyor.gov/elections/documents/november-5-2024-ballots-cast-contest-precincts/download?inline), [Wasco](https://records.sos.state.or.us/ORSOSWebDrawer/Record/10575034/File/document).

Multnomah’s choice-specific overvote counters are not contest overvote ballots. AB/ED/EV, Absentee Voting, Vote by Mail and Total views retain source-specific definitions and overlap. Explicit blank/invalid/rejected/unassigned fields remain separate from candidate votes; no missing field or private cell becomes zero. Source totals, county summaries, slates and method presentations must not be summed together. [Multnomah original SOVC2](https://multco.us/file/sovc2_-_election20241105general.csv/download), [retained 2020/2022 source inventories](data/turnout/source/original-inventory.json).

## Coverage and bounded recovery

The current [SOS history page](https://sos.oregon.gov/elections/pages/historical-data.aspx) links a literal 2024 public search that returned no records in this observation. Retained earlier public-form searches returned older archives with blanked terms; an anonymous SOAP request was 401. These results do not prove absence, repaired filters or permission to enumerate record IDs. This pass used the observed public search and linked official county alternatives; no IDs were guessed. [Acquisition receipts and complete response entities](data/turnout/source/acquired/), [read-only preparation qualifications](data/coordinator-source-preflight.md).

Lane’s [current official archive](https://www.lanecounty.org/government/county_departments/county_administration/general_county_administration/operations/county_clerk/elections/historical_election_details) states that since 2023 precinct results require a request and privacy redaction, potentially with a fee. No private-cell reconstruction or residual allocation was attempted. Deschutes’s [actual 2024 summary](https://webapps.deschutes.org/Elections/Home/Results/100?iframed=True) was observed but no native original was recovered in this bounded pass. The other unclosed parents below are **not acquired in this pass**, not proved unavailable to the public.

| County / FIPS | 2024 native coverage | Whole-county 2020 Senate native columns closed? | 2022 Senate / Governor native columns closed? |
| --- | --- | --- | --- |
| Baker / 41001 | not acquired in bounded pass | unclosed | unclosed / unclosed |
| Benton / 41003 | not acquired in bounded pass | yes (23 rows) | yes (21 rows) / yes (21 rows) |
| Clackamas / 41005 | 118 rows | unclosed | unclosed / unclosed |
| Clatsop / 41007 | not acquired in bounded pass | unclosed | yes (25 rows) / yes (25 rows) |
| Columbia / 41009 | not acquired in bounded pass | yes (33 rows) | yes (33 rows) / yes (33 rows) |
| Coos / 41011 | not acquired in bounded pass | unclosed | unclosed / unclosed |
| Crook / 41013 | not acquired in bounded pass | unclosed | unclosed / unclosed |
| Curry / 41015 | not acquired in bounded pass | yes (27 rows) | yes (27 rows) / yes (27 rows) |
| Deschutes / 41017 | summary observed native original not recovered in bounded pass | unclosed | unclosed / unclosed |
| Douglas / 41019 | not acquired in bounded pass | unclosed | unclosed / unclosed |
| Gilliam / 41021 | not acquired in bounded pass | unclosed | unclosed / unclosed |
| Grant / 41023 | not acquired in bounded pass | unclosed | unclosed / unclosed |
| Harney / 41025 | not acquired in bounded pass | yes (3 rows) | unclosed / unclosed |
| Hood River / 41027 | not acquired in bounded pass | yes (13 rows) | yes (13 rows) / yes (13 rows) |
| Jackson / 41029 | not acquired in bounded pass | yes (45 rows) | yes (50 rows) / yes (50 rows) |
| Jefferson / 41031 | not acquired in bounded pass | unclosed | unclosed / unclosed |
| Josephine / 41033 | not acquired in bounded pass | unclosed | unclosed / unclosed |
| Klamath / 41035 | not acquired in bounded pass | yes (43 rows) | yes (45 rows) / yes (45 rows) |
| Lake / 41037 | not acquired in bounded pass | unclosed | unclosed / unclosed |
| Lane / 41039 | public page says request redaction required since 2023 | yes (80 rows) | yes (66 rows) / yes (66 rows) |
| Lincoln / 41041 | not acquired in bounded pass | unclosed | unclosed / unclosed |
| Linn / 41043 | not acquired in bounded pass | yes (90 rows) | yes (84 rows) / yes (84 rows) |
| Malheur / 41045 | not acquired in bounded pass | unclosed | unclosed / unclosed |
| Marion / 41047 | 118 rows | yes (123 rows) | unclosed / unclosed |
| Morrow / 41049 | not acquired in bounded pass | unclosed | unclosed / unclosed |
| Multnomah / 41051 | 107 rows | yes (113 rows) | unclosed / unclosed |
| Polk / 41053 | not acquired in bounded pass | unclosed | unclosed / unclosed |
| Sherman / 41055 | not acquired in bounded pass | unclosed | unclosed / unclosed |
| Tillamook / 41057 | not acquired in bounded pass | yes (24 rows) | yes (29 rows) / yes (29 rows) |
| Umatilla / 41059 | not acquired in bounded pass | yes (45 rows) | yes (45 rows) / yes (45 rows) |
| Union / 41061 | not acquired in bounded pass | unclosed | unclosed / unclosed |
| Wallowa / 41063 | not acquired in bounded pass | unclosed | unclosed / unclosed |
| Wasco / 41065 | 12 rows | yes (14 rows) | yes (12 rows) / unclosed |
| Washington / 41067 | 155 rows | yes (145 rows) | yes (155 rows) / yes (155 rows) |
| Wheeler / 41069 | not acquired in bounded pass | unclosed | unclosed / unclosed |
| Yamhill / 41071 | not acquired in bounded pass | yes (58 rows) | unclosed / unclosed |

Complete original ZIP bytes for all **36 + 36** historical county members are preserved once, including all unrelated source offices; the [independent inventory](data/turnout/source/original-inventory.json) hashes every member and records exact ZIP paths/CRCs. **Historical native normalization remains partial.** “Closed” above means every extracted native candidate vector and county column closes to the abstract; it is not independent legal/geographic approval or a claim that all zero/admin rows and method semantics have been reviewed. Unclosed groups, ambiguous OCR, missing source axes and unavailable fields remain explicit in [native reconciliation](data/turnout/native/county-reconciliation.json) and [extraction issues](data/turnout/native/extraction-issues.json). Complete county controls come independently from the abstracts, not these incomplete native sums.

Benton’s 2020 ZIP member is a 115-page state-office report without Senate candidate pages; the [county-hosted full 262-page original](https://re.bentoncountyor.gov/wp-content/uploads/2023/12/2020Nov03_Precinct-Results.pdf) supplies all 23 Senate precinct vectors. Benton 2022’s archive includes an incomplete first federal block; the [full county-hosted 189-page original](https://re.bentoncountyor.gov/wp-content/uploads/2023/12/2022Nov08-Precinct-Results.pdf) is retained separately with its printed report clock. Source vintages are not silently merged.

## All 36 county parents, full priority-contest order

Primary counts: [2024 abstract p. 1](https://web.archive.org/web/20241212212240id_/https://sos.oregon.gov/elections/Documents/results/november-general-2024-results.pdf), [2020 Senate p. 2](https://records.sos.state.or.us/ORSOSCMSearch/Search/DocumentStream.ashx?uri=13735450), [2022 Senate/Governor pp. 1/4](https://records.sos.state.or.us/ORSOSWebDrawer/Record/13735454/File/document). Every parent outside the 11-county sensitivity threshold remains in state arithmetic.

| Rank | County | 2024 president reported | Cumulative | 2020 Senate | 2022 Senate | 2022 Governor |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | Multnomah | 414,250 | 414,250 | 454,418 | 362,953 | 366,043 |
| 2 | Washington | 297,949 | 712,199 | 312,618 | 253,059 | 255,882 |
| 3 | Clackamas | 246,240 | 958,439 | 250,640 | 212,448 | 214,889 |
| 4 | Lane | 211,285 | 1,169,724 | 217,158 | 182,053 | 183,669 |
| 5 | Marion | 156,691 | 1,326,415 | 162,014 | 130,496 | 134,850 |
| 6 | Deschutes | 127,375 | 1,453,790 | 122,690 | 107,893 | 109,678 |
| 7 | Jackson | 119,572 | 1,573,362 | 124,303 | 103,664 | 104,385 |
| 8 | Linn | 71,429 | 1,644,791 | 70,644 | 60,752 | 61,495 |
| 9 | Douglas | 61,807 | 1,706,598 | 62,685 | 52,840 | 54,553 |
| 10 | Yamhill | 57,800 | 1,764,398 | 57,360 | 48,360 | 49,428 |
| 11 | Benton | 50,232 | 1,814,630 | 52,043 | 45,126 | 45,319 |
| 12 | Josephine | 49,628 | 1,864,258 | 50,225 | 42,482 | 42,962 |
| 13 | Polk | 47,593 | 1,911,851 | 47,531 | 40,956 | 41,510 |
| 14 | Coos | 35,735 | 1,947,586 | 36,106 | 31,110 | 31,429 |
| 15 | Klamath | 35,515 | 1,983,101 | 35,982 | 29,761 | 30,217 |
| 16 | Columbia | 31,334 | 2,014,435 | 31,637 | 26,996 | 27,384 |
| 17 | Umatilla | 31,225 | 2,045,660 | 32,194 | 24,838 | 25,132 |
| 18 | Lincoln | 29,804 | 2,075,464 | 30,208 | 26,120 | 26,270 |
| 19 | Clatsop | 23,290 | 2,098,754 | 23,524 | 19,889 | 20,201 |
| 20 | Crook | 16,297 | 2,115,051 | 15,146 | 13,902 | 14,065 |
| 21 | Tillamook | 16,252 | 2,131,303 | 16,589 | 14,457 | 14,611 |
| 22 | Union | 14,574 | 2,145,877 | 14,605 | 12,388 | 12,544 |
| 23 | Curry | 14,200 | 2,160,077 | 14,608 | 12,606 | 12,679 |
| 24 | Wasco | 13,391 | 2,173,468 | 13,799 | 11,295 | 11,407 |
| 25 | Hood River | 12,707 | 2,186,175 | 12,885 | 10,727 | 10,805 |
| 26 | Jefferson | 11,750 | 2,197,925 | 11,752 | 9,900 | 9,977 |
| 27 | Malheur | 10,945 | 2,208,870 | 11,596 | 9,063 | 9,187 |
| 28 | Baker | 9,694 | 2,218,564 | 9,750 | 8,626 | 8,751 |
| 29 | Wallowa | 5,108 | 2,223,672 | 5,071 | 4,537 | 4,597 |
| 30 | Morrow | 4,732 | 2,228,404 | 5,035 | 4,041 | 4,089 |
| 31 | Grant | 4,456 | 2,232,860 | 4,513 | 4,114 | 4,170 |
| 32 | Harney | 4,255 | 2,237,115 | 4,377 | 3,744 | 3,834 |
| 33 | Lake | 4,213 | 2,241,328 | 4,265 | 3,948 | 4,008 |
| 34 | Sherman | 1,163 | 2,242,491 | 1,179 | 1,018 | 1,034 |
| 35 | Gilliam | 1,134 | 2,243,625 | 1,167 | 980 | 999 |
| 36 | Wheeler | 868 | 2,244,493 | 932 | 807 | 830 |

## Reproduction, checks and acceptance

Read [source/SCHEMA.md](data/turnout/source/SCHEMA.md) for scope, original reconstruction, field definitions, source-positioned extraction and the exact offline build sequence. [Scripts](data/turnout/scripts/), [validation.json](data/turnout/validation.json), [complete owned/shared asset manifest](data/turnout/asset-manifest.json), and [immutable pre-peer witness](data/turnout/pre-peer-witness-v1.json) make the package auditable. All stored artifacts are below 40,000,000 bytes; huge originals are restored only temporarily from documented shared byteparts.

Offline QA checks every county/candidate/footer balance, three full participation controls, native identity uniqueness and five native county vectors, local contest ballot/nonvote equations, all orders/remainders, exact top15/minimum80 predecessor/crossing, raw/stored/member hashes, path bounds and report links. It records incomplete native coverage as a material limitation rather than a false passing statewide-native claim. **The bounded reciprocal source-core review is complete; coordinator acceptance remains pending.** The original-first package is preserved byte-exact in the immutable history; no live collector, calibrated Needle, 2026 turnout forecast, approved current precinct boundaries or known live cadence is claimed.

## Bounded reciprocal source-core review — 20 October 2026

The actual independent baseline worker was `7c03df8c-f908-40a8-a289-369e4aa26e69`. Its completed, repaired final package was captured before comparison: manifest `c725c0069e8409d9667ef0ce674a14bea20456410bdee4e50eb0e44b4e5846b9`, original-first witness `208a3ad98dfb055eea0f895c0c0faf9881f684214e7d5a34c41e01f4df123b7f`. All 600 peer bodies are frozen as provenance. Agreement covers the source core described here; it does not cover every peer artifact, calculator, scenario, live output, report or future version. No peer writer was executed and no peer numeric derivative replaced turnout counts.

[Comparison summary](data/turnout/peer-reconciliation.json), [complete compressed field/object/source-position evidence](data/turnout/source/reciprocal-full-evidence.json.gz), [peer capture inventory](data/turnout/source/peer-capture-v1/inventory.json), and [prior turnout body inventory](data/turnout/source/history/pre-reciprocal-v1/inventory.json) retain exact tested scope and adapters. The latter restores every one of the 4,343 prior owned bodies, including the old manifest, validation, scripts and every original-first witness target. Original response entities remain once, pinned by stored/raw hashes.

| Source-core comparison | Actual tested scope |
|---|---:|
| Equal full original entities and full extracted texts | 91 (including all 72 ZIP members) |
| Equal full original receipt objects | 48 |
| County candidate/Misc. positions; statewide abstract footers | 864; 4 |
| Statistical participation source group records; monthly registration rows including totals | 1295; 111 |
| Shared native normalized objects examined under explicit schema adapter | 2793 |
| Shared candidate cells; mapped control comparisons | 16442; 12883 |
| Unique complete raw CSV records / original raw fields | 1872 / 25483 |
| Multnomah 2024 complete raw CSV records / fields (subset above) | 856 / 11,128 |
| Full source method lane objects checked against own original rows | 963 |
| Full known-source native order; complete county sensitivity orders independently recalculated from peer source counts | 510 rows; 14 orders |

Raw text checks cover 7,459 objects/nested rows: 6,748 match equal full original text, 432 match retained turnout source observations, and 279 match the exact frozen turnout OCR text and source-line positions. The OCR bindings were resolved from the literal extraction paths; they retain OCR uncertainty and do not establish equal parsing/normalization. These are comparison operations, not unique candidate/administrative fields. The full proof separately records unique raw rows. Every normalized object's schema, source positions, literal controls, methods, null/missing state, overlap and administrative disposition is examined or explicitly marked outside/unmapped. Source-only/unparsed objects remain in the inventories; archive completeness is distinct from native contest closure.

The full 2024 known-source vectors, candidate controls, overlapping Multnomah PDF/CSV presentations, all 36 county parent vectors, six nonadditive vice-presidential columns, 510 ballot/control rows, complete descending orders, top15, exact integer 80% predecessor/crossing and remainders agree under explicit adapters. Peer source-local tie keys and turnout's versioned FIPS/native keys are separately recalculated; the latter order agrees. The 115/116 combined Clackamas row remains indivisible. No current identity or polygon equivalence follows.

Historical closure is **16/13/12** parents in turnout versus **16/13/13** in the captured baseline (2020 Senate / 2022 Senate / 2022 governor). For 2020, turnout closes Harney while the peer closes Coos; the retained source-position maps show both original observations. The peer adds 2022 Wasco governor from a direct raster reading; turnout's incomplete normalization remains unchanged. Tillamook's named headings and all source-group rows are retained in the comparison. One candidate difference is confined to unclosed Douglas 2022. The broader control adapter records **17 unequal comparisons** there: the 16 literal control differences already documented by the reverse peer proof plus a repeated heading-undervote representation of the same source scope. This is not 17 newly discovered independent source fields. All affected raw positions and both values are preserved; these working groups remain excluded from closed native orders. No count/source/order repair was warranted by this bounded comparison.

Benton's 2020 ZIP member (115 state-office pages) remains separate from the recovered 262-page federal original and the separate full 189-page 2022 original. Washington text/OCR/word boxes/visual readings retain their positions and uncertainty. The Washington presidential 301,104 versus overall-header 301,105 ballot discrepancy, Wasco 1,831 versus 1,830 office-specific observation, statewide participation/current-history conflicts, generic Misc. scope and choice-specific Multnomah counters remain qualified. No residual allocation, named-write-in eligibility or missing-party inference was introduced.

[Offline rebuild evidence](data/turnout/source/offline-rebuild.json) records nine frozen original scripts executed in isolation without network or peer code and verifies **all 4,343 original-first bodies byte-exact**, with retained OCR/visual readings as inputs. The [negative-fixture proof](data/turnout/source/corruption-fixtures.json), [current validator](data/turnout/scripts/validate.py), [final seal](data/turnout/finalseal.json), and complete self-only-excluded manifest cover the final package. Failed checker versions and exact failures remain in [review-development](data/turnout/source/review-development/): Umatilla list/header representation, nested source-position arrays and the literal vice-presidential Rudolph Ware label required checker adapters, not producer vote changes. The premature preseal-link check and the cross-contest geography-key uniqueness check are also retained with their exact failures; the final observation identity is (source key, contest, literal unit, presentation).

Canonical complete statewide native order/top15/min80/priority/remainder remain **null**: the 31 unclosed parents still contain 1,115,972 votes and unknown native membership. The 510-row known-source and 36-county results remain separate qualified sensitivities. Coordinator acceptance, current source/geometry approval, November IDs/returns/cadence, eligible write-in scope and calibration remain false or unknown.
