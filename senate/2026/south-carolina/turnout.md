# South Carolina: complete historical vote-volume geography

Research observed **2026-10-18 UTC**. Fractions and integer counts are exact; decimal percentages are rounded displays. The **2024 presidential** baseline is **2,548,140 reported candidate votes**, supported by all seven slates in the signed state certificate and independently reconciled official state/county originals. The top 15 counties contribute **1,974,167 / 2,548,140 = 77.47482477414898%**. The minimum descending county prefix reaching 80% has **17 counties**, ending at **Oconee**: **2,061,601 / 2,548,140 = 80.90611190907877%**. [Signed SC certificate](https://www.archives.gov/files/electoral-college/2024/ascertainment-south-carolina.pdf), [official original XML ZIP](https://www.enr-scvotes.org/SC/122436/359624/reports/detailxml.zip), [exact contract](data/turnout/priority-set.json).

The exact integer threshold is **2,038,512**. The preceding **16 counties have 2,019,337 votes**, 19,175 short; Oconee adds **42,264**. The remaining **29 counties contribute 486,539 votes (19.09388809092123%)**, all retained in state arithmetic. Sort is votes descending, then full geography key ascending for ties; no rounded percentage determines the crossing. The dispatch union of top 15 and minimum 80 is this same 17-county set.

The complete [county table](data/county-turnout.csv) has every candidate, generic write-in and separate control. The [native orders](data/turnout/extracts/2024-pres-native-order.csv) and [original combined-native order](data/turnout/extracts/2024-pres-original-combined-native-order.csv) preserve every finer reporting identity. The contract is a research dispatch artifact; geographic/legal acceptance is controlled only by its state-relative `coordinator_acceptance_path`, with no reverse hash or self-acceptance.

## Actual elections and outcome rules

South Carolina had **no 2024 Senate general election**; 2024 president is the stated priority. **2020 Graham–Harrison–Bledsoe** is the previous **Class II** election for this seat. **2022 Scott–Matthews** is the other **Class III** seat and the actual recent midterm; the **2022 governor/lieutenant-governor tickets** are separate context. Original event dates are November 5, 2024; November 3, 2020; and November 8, 2022. The regular Class II general election is **November 3, 2026**. [Class II](https://www.senate.gov/senators/Class_II.htm), [Class III](https://www.senate.gov/senators/Class_III.htm), [official calendars](https://scvotes.gov/elections-statistics/general-election-calendars/), [2020 original](https://www.enr-scvotes.org/SC/106502/277849/reports/detailxml.zip), [2022 original](https://www.enr-scvotes.org/SC/115412/313728/reports/detailxml.zip).

The November federal contest uses **plurality**. A tie can require a separate tie-breaking election under SC 7-13-2210. A primary requires a majority for nomination (7-17-600/610); its ordinary second primary is two weeks later under 7-13-50. These are different rules. The 1%-or-less statutory recount provision is 7-17-280 and is not a majority runoff. Historical or current primary candidates/counts are not November votes. [Official county 2026 federal election rules](https://cherokeecountysc.gov/voter-registration-election-board/2026-election-dates/), [chapter 13](https://www.scstatehouse.gov/code/t07c013.php), [chapter 17](https://www.scstatehouse.gov/code/t07c017.php).

## Complete county order

All counts below are contest candidate/write-in votes, including minor candidates. The 2024 values reconcile independently to every candidate in the official state original and all 46 county originals; the 2020/2022 columns reconcile to their own separate originals. County FIPS are from the [Census county code original](https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt). The compatibility filename is legitimate for these actual county parents; finer units remain separate. [2024 original general results](https://www.enr-scvotes.org/SC/122436/359624/reports/detailxml.zip), [2020 original general results](https://www.enr-scvotes.org/SC/106502/277849/reports/detailxml.zip), [2022 original general results](https://www.enr-scvotes.org/SC/115412/313728/reports/detailxml.zip).

| Rank | County | FIPS | 2024 president | Cumulative | Cumulative % | 2020 Senate | 2022 Senate | 2022 governor |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Greenville | 45045 | 263,316 | 263,316 | 10.333655 | 258,406 | 177,399 | 178,134 |
| 2 | Charleston | 45019 | 214,521 | 477,837 | 18.752384 | 219,297 | 151,799 | 153,488 |
| 3 | Horry | 45051 | 205,954 | 683,791 | 26.834907 | 179,644 | 133,205 | 133,661 |
| 4 | Richland | 45079 | 182,411 | 866,202 | 33.993501 | 194,187 | 126,355 | 127,368 |
| 5 | Spartanburg | 45083 | 155,597 | 1,021,799 | 40.099798 | 148,651 | 96,822 | 97,051 |
| 6 | York | 45091 | 150,059 | 1,171,858 | 45.988760 | 143,998 | 95,765 | 95,978 |
| 7 | Lexington | 45063 | 146,903 | 1,318,761 | 51.753868 | 144,681 | 99,109 | 99,656 |
| 8 | Berkeley | 45015 | 112,834 | 1,431,595 | 56.181960 | 104,486 | 71,104 | 71,400 |
| 9 | Beaufort | 45013 | 104,403 | 1,535,998 | 60.279184 | 97,977 | 71,405 | 71,706 |
| 10 | Anderson | 45007 | 98,296 | 1,634,294 | 64.136743 | 96,133 | 63,264 | 63,419 |
| 11 | Aiken | 45003 | 86,091 | 1,720,385 | 67.515325 | 85,243 | 54,779 | 54,860 |
| 12 | Dorchester | 45035 | 77,764 | 1,798,149 | 70.567120 | 77,238 | 49,512 | 49,794 |
| 13 | Florence | 45041 | 61,140 | 1,859,289 | 72.966517 | 64,651 | 41,323 | 41,439 |
| 14 | Pickens | 45077 | 60,451 | 1,919,740 | 75.338875 | 57,542 | 40,083 | 40,205 |
| 15 | Lancaster | 45057 | 54,427 | 1,974,167 | 77.474825 | 49,849 | 34,488 | 34,551 |
| 16 | Sumter | 45085 | 45,170 | 2,019,337 | 79.247490 | 48,960 | 30,566 | 30,677 |
| 17 | Oconee | 45073 | 42,264 | 2,061,601 | 80.906112 | 40,697 | 28,919 | 28,965 |
| 18 | Georgetown | 45043 | 37,754 | 2,099,355 | 82.387742 | 36,724 | 27,357 | 27,501 |
| 19 | Orangeburg | 45075 | 36,970 | 2,136,325 | 83.838604 | 41,259 | 26,136 | 26,191 |
| 20 | Kershaw | 45055 | 33,533 | 2,169,858 | 85.154583 | 33,634 | 22,308 | 22,402 |
| 21 | Greenwood | 45047 | 30,888 | 2,200,746 | 86.366762 | 32,033 | 21,765 | 21,801 |
| 22 | Darlington | 45031 | 30,331 | 2,231,077 | 87.557081 | 32,446 | 20,026 | 20,038 |
| 23 | Laurens | 45059 | 30,213 | 2,261,290 | 88.742769 | 30,508 | 19,756 | 19,821 |
| 24 | Cherokee | 45021 | 24,839 | 2,286,129 | 89.717559 | 25,247 | 16,120 | 16,142 |
| 25 | Chesterfield | 45025 | 18,391 | 2,304,520 | 90.439301 | 18,874 | 12,538 | 12,557 |
| 26 | Colleton | 45029 | 18,276 | 2,322,796 | 91.156530 | 19,293 | 12,507 | 12,545 |
| 27 | Jasper | 45053 | 18,227 | 2,341,023 | 91.871836 | 14,416 | 11,090 | 11,128 |
| 28 | Newberry | 45071 | 18,129 | 2,359,152 | 92.583296 | 18,626 | 12,752 | 12,835 |
| 29 | Clarendon | 45027 | 16,320 | 2,375,472 | 93.223763 | 16,727 | 11,410 | 11,457 |
| 30 | Chester | 45023 | 15,556 | 2,391,028 | 93.834248 | 15,750 | 9,579 | 9,583 |
| 31 | Williamsburg | 45089 | 14,330 | 2,405,358 | 94.396619 | 16,018 | 9,744 | 9,792 |
| 32 | Edgefield | 45037 | 13,919 | 2,419,277 | 94.942860 | 13,317 | 8,807 | 8,806 |
| 33 | Marion | 45067 | 13,388 | 2,432,665 | 95.468263 | 14,728 | 8,377 | 8,416 |
| 34 | Union | 45087 | 12,289 | 2,444,954 | 95.950536 | 13,237 | 8,639 | 8,665 |
| 35 | Abbeville | 45001 | 12,048 | 2,457,002 | 96.423352 | 12,450 | 8,573 | 8,601 |
| 36 | Dillon | 45033 | 11,861 | 2,468,863 | 96.888829 | 13,096 | 7,882 | 7,915 |
| 37 | Fairfield | 45039 | 11,215 | 2,480,078 | 97.328954 | 12,139 | 8,334 | 8,413 |
| 38 | Marlboro | 45069 | 10,152 | 2,490,230 | 97.727362 | 11,462 | 6,486 | 6,537 |
| 39 | Barnwell | 45011 | 9,803 | 2,500,033 | 98.112074 | 10,320 | 6,265 | 6,257 |
| 40 | Saluda | 45081 | 9,014 | 2,509,047 | 98.465822 | 9,286 | 6,545 | 6,560 |
| 41 | Hampton | 45049 | 8,233 | 2,517,280 | 98.788921 | 9,301 | 5,626 | 5,630 |
| 42 | Lee | 45061 | 8,076 | 2,525,356 | 99.105858 | 8,438 | 5,240 | 5,255 |
| 43 | Calhoun | 45017 | 7,914 | 2,533,270 | 99.416437 | 8,304 | 5,599 | 5,622 |
| 44 | McCormick | 45065 | 6,153 | 2,539,423 | 99.657907 | 5,725 | 4,566 | 4,567 |
| 45 | Bamberg | 45009 | 5,694 | 2,545,117 | 99.881364 | 6,479 | 3,969 | 3,983 |
| 46 | Allendale | 45005 | 3,023 | 2,548,140 | 100.000000 | 3,627 | 1,809 | 1,820 |

## Candidate universe and primary control disagreements

The following are the source-preserved named/ballot identities. Source spellings, candidate IDs, parties, flags and pseudocandidates remain in [complete metadata](data/turnout/candidate-universe.json) and [original choice identities](data/turnout/legacy-candidate-identities.json). The historical database is an official-linked presentation, with its own import/verification metadata, not a replacement for original party labels. [History database authority](https://scvotes.gov/elections-statistics/election-database/), [2024 signed certificate](https://www.archives.gov/files/electoral-college/2024/ascertainment-south-carolina.pdf), [2020/2022 originals](https://scvotes.gov/elections-statistics/election-results/).

| Contest | Named candidate/slate or generic scope | DB party | Votes |
| --- | --- | --- | ---: |
| 2024-pres | Donald J. Trump and JD Vance | Republican | 1,483,747 |
| 2024-pres | Kamala D. Harris and Tim Walz | Democratic | 1,028,452 |
| 2024-pres | Chase Oliver and Mike ter Maat | Libertarian | 12,669 |
| 2024-pres | Jill Stein and Rudolph Butch Ware | Green | 8,117 |
| 2024-pres | Cornel West and Melina Abdulla | United Citizens | 6,744 |
| 2024-pres | Randall A. Terry and Stephen E. Broden | Constitution | 5,352 |
| 2024-pres | Claudia De La Cruz and Karina Garcia | Workers | 3,059 |
| 2020-senate | Lindsey Graham | Republican | 1,369,137 |
| 2020-senate | Jaime Harrison | Democratic | 1,110,828 |
| 2020-senate | Bill Bledsoe | Conservative | 32,845 |
| 2020-senate | Write-In | generic Write-In | 2,294 |
| 2022-senate | Tim Scott | Republican | 1,066,274 |
| 2022-senate | Krystle Matthews | Democratic | 627,616 |
| 2022-senate | Write-In | generic Write-In | 1,812 |
| 2022-governor | Henry McMaster and Pamela Evette | Republican | 988,501 |
| 2022-governor | Joe Cunningham/Tally Parham Casey | Democratic | 692,691 |
| 2022-governor | Bruce Reeves/Jessica Ethridge | Libertarian | 20,826 |
| 2022-governor | Write-In | generic Write-In | 1,174 |

The signed December 9, 2024 certificate includes **Terry/Broden 5,352**, matching the official original XML and database. The [House Clerk 2024 PDF](https://clerk.house.gov/member_info/electionInfo/2024/statistics2024.pdf), PDF page 64/printed 62, actually prints six presidential party rows and omits that slate: its listed sum is **2,542,788**, not the complete 2,548,140. Both actual pages were visually checked; no omission cause or release chronology is inferred. Presidential/vice-presidential repeated totals and elector names are not additional votes.

The [House Clerk 2020 PDF](https://clerk.house.gov/member_info/electionInfo/2020/statistics2020.pdf), PDF page 62/printed 60, prints three SC Senate named candidates totaling **2,512,810** and omits the original/database generic **2,294 Write-In**; the full contest is **2,515,104**. It labels Bledsoe **Constitution**, corroborated by original ENR party **CON**. The database instead labels party 274 **Conservative**; both identities are retained. The [2022 Clerk PDF](https://clerk.house.gov/member_info/electionInfo/2022/statistics2022.pdf), PDF page 44/printed 42, includes Scott, Matthews and **1,812 generic Write-In**, matching **1,695,702**. Neither omitted scope is forced to zero.

Generic `ALL_OTHER_CANDIDATES` is not an independently identified named or legally valid write-in subset; none is supplied. Presidential write-in space is excluded by **SC 7-13-360**, consistent with the seven-slate universe and absence of a generic presidential option. `TOTAL_VOTES`, `TOTAL_BALLOTS` and combined `Overvotes/Undervotes` are overlapping controls, never extra candidates. [SC chapter13](https://www.scstatehouse.gov/code/t07c013.php), [source schema](data/turnout/source/SCHEMA.md).

## Native reporting geography and original coverage

Every returned hierarchy is preserved: state → all 46 counties → **2,446 native 2024 president, 2,399 native 2020 Senate, and 2,395 each 2022 Senate/governor**. Their combined candidate vectors reconcile exactly at every level. There are **138 explicitly named Failsafe/Provisional/Failsafe Provisional administrative contexts per contest**, plus all other names, zero-vote and Central identities. The original reports count participating precincts **2,308 / 2,261 / 2,257**, a different field from identity counts. Do not infer polygons or a crosswalk from those differences. Database native IDs, original JSON row ordinals/labels, and VHM codes are separate source systems. [Official history](https://electionhistory.scvotes.gov/), [original 2024](https://www.enr-scvotes.org/SC/122436/359624/reports/detailxml.zip), [original 2020](https://www.enr-scvotes.org/SC/106502/277849/reports/detailxml.zip), [original 2022](https://www.enr-scvotes.org/SC/115412/313728/reports/detailxml.zip).

At the finest 2024 native level, the top 15 have **63,074 / 2,548,140 = 2.4752957058874316%**. The first **1,380 have 2,038,464**; **Congaree 02, Lexington, DB 11109**, adds **819**, crossing at **1,381 units with 2,039,283 votes (80.03025736419507%)**. The native remainder has **508,857 votes**. Full orders include zero units and stable key ties. The [database order](data/turnout/extracts/2024-pres-native-order.csv) and [original combined order](data/turnout/extracts/2024-pres-original-combined-native-order.csv) remain separate. Same-year equal candidate-vector multisets are numerical corroboration, not a geographic join.

All 138 county original combined JSON/English summary pairs were independently extracted read-only from exact-hash originals. Original method sources cover **137 county XMLs plus Clarendon 2022 TXT**, and three state XMLs. Clarendon explicitly disables XML; pinned/current XML 404 responses remain, while enabled original TXT/XLS downloads provide the methods. Its pinned registration fields are zero; a later current version has different registration, preserved without substitution. Original method labels include Charleston **Provionsal**; comparison-only aliases and Newberry’s missing Write-In party attribute are documented. [Exact source observations](data/turnout/legacy-observations.json), [combined JSON/TXT observations](data/turnout/legacy-json-observations.json), [full original reconciliation](data/turnout/legacy-json-reconciliation.json), [Clarendon original TXT](https://www.enr-scvotes.org/SC/Clarendon/115426/313514/reports/detailtxt.zip).

The historical database has **95 positive candidate-method differences in 26 2020 precinct contexts** (Horry 7, Lancaster 6, Spartanburg 13) and **51 method hierarchy residual cells**. Its own state/county method controls still reconcile to the original reports. The complete original finer methods are retained independently, with exact method-parent/native-child balances; this provides a usable historical source scope without allocating the database gaps or asserting their cause. Separate original and database raw rows remain visible in [controls](data/turnout/controls.json), [original XML cells](data/turnout/extracts/legacy-candidate-methods.csv.gz) and [Clarendon TXT cells](data/turnout/extracts/clarendon-2022-txt-candidate-methods.csv).

## Ballots, registration and method sensitivity

Candidate votes are not ballots cast. Separate blank, undervote and overvote fields are unavailable in these statewide history/XML/JSON scopes; the database publishes combined under/over controls. Original native election-ballot and registration fields are retained where supplied, including omitted/zero administrative cases; a difference between election ballots and candidate votes is not relabeled as a measured undervote count. [Original election controls](data/turnout/extracts/legacy-turnout-controls.csv.gz), [published participation summary](https://scvotes.gov/wp-content/uploads/2026/10/Voter-Participation-History-1998-2026.pdf).

| Scope | 2024 | 2022 | 2020 |
| --- | ---: | ---: | ---: |
| Original ENR election ballots | 2,566,404 | 1,718,626 | 2,533,010 |
| Original ENR election totalVoters | 3,343,423 | 3,379,089 | 3,513,225 |
| BCM summary Total Registered | 3,414,652 | 3,379,089 | 3,513,225 |
| VHM printed-list registered | 3,851,932 | 3,740,742 | 3,733,793 |
| VHM participating | 2,553,186 | 1,720,378 | 2,521,038 |

The [BCM summary](https://scvotes.gov/wp-content/uploads/2026/10/Voter-Participation-History-1998-2026.pdf) labels Total Registered without specifying historical active/inactive status. The [VHM authority](https://vrems.scvotes.sc.gov/Statistics/VoterHistoryResults) explicitly includes all active and some inactive voters printed on election lists; participants come from list markings/returns, which can differ from tabulation. **2024 original ENR registration differs from the BCM summary by 71,229**; definition/cause is unresolved. The **2022 original state registration parent is 3,379,089 but its 46 county attributes sum 3,379,129, a 40-registration discrepancy**; election ballots still sum exactly 1,718,626. Both registration values remain in the [state/child ledger](data/turnout/legacy-state-election-reconciliation.json), with no allocation or inferred cause. The **2020 Senate database ballot control is 2,532,829**, with **17,725 combined under/over**, while the election-wide original/BCM has **2,533,010**, difference 181. The separately observed 2020 presidential database control 2,532,830 is another contest scope. These values are not rescaled.

VHM includes all 46 requested counties and **2,343 / 2,270 / 2,465 returned native labels** for 2024/2022/2020; every county rollup is exact. Its 2024 unnamed administrative county row contributes **2 registrations/1 participant** outside named counties. REG and VOT views overlap; REG’s structural participation zero is retained raw but interpreted as unavailable participation. Returned precinct rows have county=null; the county is the explicit request context. Sparse Greenville rows named Barksdale-Narnie, Keowee and `Monarch Box1` remain literally preserved. The authority does not explain whether these labels represent election-day physical membership versus later voter-history/address context; that geographic meaning remains unresolved. **No VHM-to-results or cross-year precinct join is made.** [Actual parent/JS/request provenance](data/turnout/source/voter-history.meta.json), [registration reconciliation](data/turnout/registration-reconciliation.json).

| Independently ranked basis | Total | Top 15 % | Minimum 80 units | Crossing |
| --- | ---: | ---: | ---: | --- |
| 2024-pres candidate votes | 2,548,140 | 77.474825 | 17 | Oconee |
| 2020-senate candidate votes | 2,515,104 | 76.417635 | 17 | Orangeburg |
| 2022-senate candidate votes | 1,695,702 | 77.042546 | 17 | Oconee |
| 2022-governor candidate votes | 1,703,192 | 77.073518 | 17 | Oconee |
| 2024 original ENR election registered | 3,343,423 | 77.310289 | 17 | Oconee |
| 2024 original ENR election ballots | 2,566,404 | 77.477825 | 17 | Oconee |
| 2022 original ENR election registered | 3,379,129 | 76.904907 | 17 | Oconee |
| 2022 original ENR election ballots | 1,718,626 | 76.978354 | 17 | Oconee |
| 2020 original ENR election registered | 3,513,225 | 76.591764 | 17 | Orangeburg |
| 2020 original ENR election ballots | 2,533,010 | 76.359706 | 18 | Oconee |
| vhm-2024 totalRegistered | 3,851,932 | 77.438049 | 17 | OCONEE |
| vhm-2024 totalVoting | 2,553,186 | 77.544135 | 17 | OCONEE |
| vhm-2022 totalRegistered | 3,740,742 | 77.182174 | 17 | ORANGEBURG |
| vhm-2022 totalVoting | 1,720,378 | 77.039348 | 17 | OCONEE |
| vhm-2020 totalRegistered | 3,733,793 | 76.628378 | 17 | ORANGEBURG |
| vhm-2020 totalVoting | 2,521,038 | 76.444465 | 17 | ORANGEBURG |

All 182 available required county XML native-ballot rollups are exact. Native registration sums disagree with their county VoterTurnout controls in 151 of 182 contexts; both sides remain separate, with no allocation or assumed definition. These are separate observed volume/registration sensitivities, not 2026 turnout forecasts. Complete orders, preceding prefixes, crossings and remainders are in [source-volume sensitivity](data/turnout/legacy-volume-sensitivity.json), [other sensitivities](data/turnout/sensitivity.json) and [all-county rankings](data/turnout/extracts/county-rankings.csv). The midterm comparator is the actual 2022 electorate, not an invented 2024 Senate/governor contest.

Raw state candidate-method votes are preserved by source labels. In 2024: mail 106,800; early 1,467,109; Election Day 967,968; Failsafe 1,782; Provisional 2,585; Failsafe Provisional 1,896. In 2022 Senate: mail 69,426; early 539,914; Election Day 1,080,308; Failsafe 2,235; Provisional 1,628; Failsafe Provisional 2,191. Both the original reports and database match those candidate-channel values. However, the [published absentee/early ballot history](https://scvotes.gov/wp-content/uploads/2026/10/Voter-History-Absentee-History-1998-2026.pdf) lists 2022 absentee ballots 58,062 and early ballots 561,563: the mail candidate total exceeds that separately published ballot statistic. The source-scope discrepancy remains unresolved; method labels are not silently swapped. Its 2024 ballot figures 108,970 mail/1,471,663 early and 2020 absentee 1,333,972 are separate controls.

## Reproduction, provenance and review

Run, in order, `PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/south-carolina/data/turnout/build_turnout.py`, then `extract_legacy.py`, `extract_legacy_json.py`, `write_report.py`, `compare_peer.py`, and `validate_turnout.py --seal` at that same directory path. Default `validate_turnout.py` verifies the sealed package offline. Acquisition is in [acquire.py](data/turnout/acquire.py); exact URLs/requests, redirects/headers, UTC clocks, complete raw originals and stored/original hashes remain in source metadata and [asset manifest](data/turnout/asset-manifest.json). ZIP members and gzip originals reconstruct complete ordered bytes; no file is truncated or simplified, and every stored object is strictly below 40,000,000 bytes.

The [schema](data/turnout/source/SCHEMA.md), [offline validation](data/turnout/validation.json) and [independent peer comparison](data/turnout/peer-agreement.json) document complete fields, coverage, denominators, source gaps, full orders, minimum integer 80 and hash/link checks. Peer work is read-only and independent; coordinator acceptance is separate. Source/native IDs have no implied Georgia/North Carolina equivalence: cross-border newsroom scopes stay intact in the read-only preparation and only verified SC election/contest/geography rows enter these historical totals. No implemented collector, measured November cadence, calibrated Needle, real 2026 turnout forecast or approved current precinct geometry is claimed.
