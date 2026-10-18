# Ohio turnout geography for the 2026 Senate special election

Research local date: **2026-10-17 (America/Chicago)**; source retrievals: **2026-10-18 UTC**. The baseline is the **November 5, 2024 general-election U.S. Senator contest**, all seven certified candidates. All 88 counties remain in every statewide denominator.

The **top 15 supply 3,525,320 / 5,704,620 votes (61.797631%)**. The exact smallest set reaching 80% is **32 counties, 4,581,738 votes (80.316270%)**. The first 31 supply 4,542,798 (79.633665%), below the threshold. The integer tests are `5*4,581,738 >= 4*5,704,620` and `5*4,542,798 < 4*5,704,620`. Descending volume maximizes coverage for each county count; therefore no smaller county set can reach 80%.

The ordered 80% geography is: **Franklin, Cuyahoga, Hamilton, Summit, Montgomery, Lucas, Stark, Butler, Lorain, Warren, Delaware, Lake, Clermont, Mahoning, Medina, Trumbull, Licking, Greene, Fairfield, Portage, Wood, Clark, Miami, Richland, Geauga, Wayne, Columbiana, Allen, Ashtabula, Tuscarawas, Erie, Muskingum**. The top-15/80% union is this same 32-county set. [priority-set.json](data/turnout/priority-set.json) retains the ordered FIPS keys, all 88 county records, native unit codes and names, source rows and source paths for both vintages.

## Baseline choice and primary evidence

[Ohio Directive 2025-54](https://www.ohiosos.gov/assets/directive-2025-54-writ-of-special-election-for-united-states-senate-election.pdf), issued November 13, 2025 and checked October 17, 2026, specifies the November 3, 2026 special election for the unexpired term ending January 3, 2029. **2022 Senate is the recent midterm and same-seat comparator**. The 2024 Senate contest concerns Ohio's other seat and different candidates. Ohio had no 2020 U.S. Senate election; no such baseline is created.

The state certified the [2024 general election on December 2, 2024](https://www.ohiosos.gov/office/media-center/categories/press-releases/2024-12-02) and the [2022 general election on December 9, 2022](https://www.ohiosos.gov/office/media-center/categories/press-releases/2022-12-09). Original official-canvass workbooks were recovered from archived Ohio SOS URLs, not transcribed from a third-party result table:

- [2024 county summary, archived 2024-12-07](https://web.archive.org/web/20241207004035if_/https://www.ohiosos.gov/globalassets/elections/2024/gen/official/statewide-race-summary.xlsx): [retained XLSX](data/turnout/raw/2024-summary-archive.xlsx). `Master!AA:AG` is Senate, `G:T` is president; county rows 5-92, statewide controls row 3.
- [2024 precinct original, archived 2024-12-22](https://web.archive.org/web/20241222221124if_/https://www.ohiosos.gov/globalassets/elections/2024/gen/official/statewide-races-precint-level.xlsx): [retained XLSX](data/turnout/raw/2024-statewide-races-precint-level.xlsx). The source filename really spells `precint`. `Master!AC:AI` is Senate, `I:V` is president, rows 5-8882 are 8,878 reporting units.
- [2022 county summary, archived 2022-12-29](https://web.archive.org/web/20221229143511if_/https://www.ohiosos.gov/globalassets/elections/2022/gen/statewide-races-summary.xlsx): [retained XLSX](data/turnout/raw/2022-statewide-races-summary.xlsx). `Master!AB:AH` is Senate, county rows 5-92, statewide controls row 3.
- [2022 precinct original, archived 2025-03-12](https://web.archive.org/web/20250312114330if_/https://www.ohiosos.gov/globalassets/elections/2022/gen/statewide-races-by-precinct.xlsx): [retained XLSX](data/turnout/raw/2022-statewide-races-by-precinct.xlsx). `Master!AD:AJ` is Senate, rows 5-8937 are 8,933 reporting units.

The separate official county and precinct turnout workbooks for each year were also downloaded and checked against every corresponding county and native precinct code/name, registration and ballot count. Their archive timestamps, URLs, HTTP status/headers, retrieval UTC and original/stored SHA-256 hashes are in [source-manifest.json](data/turnout/source-manifest.json). Source titles say Official Canvass. Archive capture dates are not election dates or certification dates. Legacy state archive URLs now redirect to the new data portal in browsing; direct terminal requests returned maintenance/403 HTML. Those failures and the failed correctly spelled precinct URL are retained and excluded from arithmetic. The civic map page was used only to discover a URL; none of its counts enter a baseline.

[Census's 2020 county code reference](https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt), [retained locally](data/turnout/raw/national_county2020.txt), provides all 88 five-digit county FIPS. Source-native county IDs are the `County Name` strings; these workbooks publish no numeric county, election, contest or candidate ID. Native candidate identifiers are the exact header labels plus workbook/sheet/column. These absences are explicit nulls in the [candidate catalog](data/turnout/candidate-catalog.json), not invented numeric IDs.

## Candidate universe and reconciliation

All published county candidate cells sum exactly to each source's certified statewide row. Non-write-in precinct cells sum exactly to each county and state candidate control. The separate Ohio partisanship worker independently verified the 2024 Senate county values against the official `U.S. Congress` side sheet and all seven statewide values against the [House Clerk 2024 publication](https://clerk.house.gov/member_info/electionInfo/2024/statistics2024.pdf). The turnout validator also checks all seven 2024 and all seven 2022 Senate candidates against the independently downloaded [House Clerk 2022 publication](https://clerk.house.gov/member_info/electionInfo/2022/statistics2022.pdf); see [14 primary Senate controls](data/turnout/house-clerk-senate-reconciliation.csv). Those primary PDFs, their retrieval metadata and text extractions are retained read-only under `data/baselines/`. The [county candidate extract](data/turnout/county-candidate-votes.csv), [state candidate checks](data/turnout/state-candidate-reconciliation.csv) and [county/precinct checks](data/turnout/county-precinct-candidate-reconciliation.csv) retain every difference.

| Election/contest | Candidate native label | Certified votes |
| --- | --- | ---: |
| 2024 senate | Sherrod Brown (D) | 2,650,949 |
| 2024 senate | Stephen Faris (WI)* | 84 |
| 2024 senate | Don Kissick (L) | 195,648 |
| 2024 senate | Bernie Moreno (R) | 2,857,383 |
| 2024 senate | David Allen Pastorius (WI)* | 13 |
| 2024 senate | Nathan Russell (WI)* | 19 |
| 2024 senate | Tariq K. Shabazz (WI)* | 524 |
| 2024 president | Shiva  Ayyadurai and Crystal Ellis (WI)* | 74 |
| 2024 president | Jay Bowman and De D Bowman (WI)* | 7 |
| 2024 president | John Cheng and Wayne Waligorski (WI)* | 24 |
| 2024 president | Claudia De la Cruz and Karina Garcia (WI)* | 1,794 |
| 2024 president | Richard Duncan and Mitchell Preston Bupp | 12,805 |
| 2024 president | Cherunda Fox and Harlan McVay (WI)* | 0 |
| 2024 president | Chris Garrity and Cody Ballard (WI)* | 13 |
| 2024 president | Kamala D. Harris and Tim Walz (D) | 2,533,699 |
| 2024 president | Brian Kienitz and Christina Johnston (WI)* | 4 |
| 2024 president | William Nalbach and Willis Butts (WI)* | 3 |
| 2024 president | Chase Oliver and Mike  ter Maat (L) | 28,200 |
| 2024 president | Peter  Sonski and Lauren  Onak | 10,197 |
| 2024 president | Donald J. Trump and JD Vance (R) | 3,180,116 |
| 2024 president | Cornel West and Melina Abdullah (WI)* | 852 |
| 2022 senate | John Cheng (WI)* | 702 |
| 2022 senate | Matthew R.  Esh (WI)* | 78 |
| 2022 senate | Stephen Faris (WI)* | 194 |
| 2022 senate | Shane Hoffman (WI)* | 403 |
| 2022 senate | Tim Ryan (D) | 1,939,489 |
| 2022 senate | LaShondra Tinsley (WI)* | 362 |
| 2022 senate | JD Vance (R) | 2,192,114 |

Both precinct workbooks explicitly state that write-in results are unavailable at precinct level and direct readers to the summary workbook. The zeroes in those precinct candidate columns are placeholders, preserved in `native_export_value` while `votes_observed` is blank. They omit **640** 2024 Senate votes, **2,771** 2024 presidential votes and **1,739** 2022 Senate votes. County write-ins remain in the ranking and in statewide arithmetic; the residual is never assigned to an invented administrative unit. The county summary is selected because it preserves the full certified candidate universe. No discrepancy is forced to zero.

These are ordinary official county/precinct canvass exports, not a precinct-sorted model, a boundary allocation, or a 2026 live feed. The entire workbooks are retained, including all other contests and source sheets. Normalized compressed precinct candidate extracts preserve the selected contest cells, their native columns/rows and availability status.

## Denominators and independent volume comparisons

| Metric | Statewide denominator | Top-15 votes/ballots | Top-15 % | Minimum counties for 80% | 80% set share % |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2024 senate | 5,704,620 | 3,525,320 | 61.797631 | 32 | 80.316270 |
| 2024 president | 5,767,788 | 3,565,727 | 61.821395 | 32 | 80.290347 |
| 2022 senate | 4,133,342 | 2,565,223 | 62.061717 | 32 | 80.637871 |
| 2024 ballots | 5,851,387 | 3,621,261 | 61.887224 | 32 | 80.336748 |
| 2022 ballots | 4,201,368 | 2,606,368 | 62.036175 | 32 | 80.591536 |

All five independent rankings select the same 32-county 80% membership, although the orders and shares differ. Each comparison is independently ranked, never substituted for Senate votes. [ranking-comparisons.json](data/turnout/ranking-comparisons.json) retains all five full orders, cumulative integers and separate exact 80% sets. The [88-county CSV](data/county-turnout.csv) gives their ranks side by side. Registration totals are **8,159,946 (2024)** and **8,029,950 (2022)**. Ballots counted are **5,851,387** and **4,201,368**; Senate contest votes are **5,704,620** and **4,133,342**; 2024 president votes are **5,767,788**. These are distinct quantities.

The 2024 Senate ballot-minus-contest gap is **146,767**, the presidential gap **83,599**; the 2022 Senate gap is **68,026**. A subtraction is not a certified undervote, overvote or rejected-ballot classification. The archived statewide files do not publish voting-method splits or separate under/over counts for these contests; those normalized fields are blank. Missing is not zero. Ballots/registration is registered-voter participation, not voting-eligible-population turnout. The 2022 comparator reflects a midterm electorate and candidate effects; it is not a forecast of special-election turnout.

## Native units, vintages and handoff limits

Every source reporting row is retained exactly once: **8,878 in 2024 and 8,933 in 2022**, 88 counties each. Composite keys are `election_date|county_FIPS|Precinct Code`; county plus code is unique within each vintage. No rows with administrative labels, split precincts, zero registration or zero votes are filtered out. These particular statewide inventories have no missing code or duplicate county/code and all registration values are positive; the source calls each row a precinct and supplies no administrative-unit classification. County-level write-in residuals are a separate limitation, not extra precincts. Voting-method data cannot be inferred from precinct names.

The [2024 unit inventory](data/turnout/reporting-units-2024.csv.gz) and [2022 inventory](data/turnout/reporting-units-2022.csv.gz) preserve exact native names/codes, region/media market, source row and statistics. Names containing `CENTRAL` are retained as ordinary native labels, not reclassified as central-count boards. [Unit vintage comparison](data/turnout/reporting-unit-vintages.json) exposes codes added/removed and shared codes with changed names. It is only an identifier/name audit: equal codes do not establish equal geometry, and changed names do not prove a split. No approved 2026 boundary vintage or precinct crosswalk is asserted. Map/reporting workers must reconcile current units against this historical inventory before slice-level comparisons.

## Reproduction and checks

From the repository root, run:

```sh
python3 senate/2026/ohio/data/turnout/build_turnout.py
python3 senate/2026/ohio/data/turnout/validate_turnout.py
```

The builder uses only Python's standard library, reads cached XLSX scalar values without modifying the sources, and emits deterministic CSV/JSON and gzip (`mtime=0`). Validation reconstructs every generated byte from the archived inputs, checks hashes and archive status, all 88 FIPS/native county identities, unit uniqueness/coverage, every county/candidate and statewide control, independently published turnout workbooks, missing write-ins, exact rational weights summing to one, ordering, top15 and integer minimal-80% tests, relative links and the 40 MiB per-file bound. [validation.json](data/turnout/validation.json) records the executed results. The validator emits `artifact-manifest.json` with hashes/sizes for every turnout-owned source, script and product, and `partisanship-reconciliation.csv` for its read-only cross-worker comparisons. No live API, collection cadence, exact remaining count, current map approval or calibrated Needle is inferred.

The remaining substantive gaps are precinct allocation of named write-ins, voting-method and under/over counts, a verified 2026 reporting-unit/boundary crosswalk, and current live-feed testing. Historical county ranking and the exact priority geography are reconciled; these gaps limit finer live comparisons.

## All 88 counties

| Rank | County / FIPS | 2024 Senate votes | State % | Cumulative % | 2022 Senate votes |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | Franklin / 39049 | 589,081 | 10.326385 | 10.326385 | 425,060 |
| 2 | Cuyahoga / 39035 | 569,065 | 9.975511 | 20.301896 | 408,543 |
| 3 | Hamilton / 39061 | 407,742 | 7.147575 | 27.449471 | 302,486 |
| 4 | Summit / 39153 | 271,264 | 4.755163 | 32.204634 | 199,897 |
| 5 | Montgomery / 39113 | 251,934 | 4.416315 | 36.620949 | 186,002 |
| 6 | Lucas / 39095 | 189,030 | 3.313630 | 39.934579 | 131,765 |
| 7 | Stark / 39151 | 181,740 | 3.185839 | 43.120418 | 133,546 |
| 8 | Butler / 39017 | 181,243 | 3.177127 | 46.297545 | 128,052 |
| 9 | Lorain / 39093 | 156,181 | 2.737798 | 49.035343 | 111,727 |
| 10 | Warren / 39165 | 138,872 | 2.434378 | 51.469721 | 101,372 |
| 11 | Delaware / 39041 | 132,994 | 2.331338 | 53.801059 | 98,885 |
| 12 | Lake / 39085 | 126,259 | 2.213276 | 56.014336 | 94,071 |
| 13 | Clermont / 39025 | 113,066 | 1.982008 | 57.996343 | 80,006 |
| 14 | Mahoning / 39099 | 111,499 | 1.954539 | 59.950882 | 85,837 |
| 15 | Medina / 39103 | 105,350 | 1.846749 | 61.797631 | 77,974 |
| 16 | Trumbull / 39155 | 95,655 | 1.676799 | 63.474429 | 73,000 |
| 17 | Licking / 39089 | 94,309 | 1.653204 | 65.127633 | 66,371 |
| 18 | Greene / 39057 | 89,856 | 1.575144 | 66.702778 | 65,716 |
| 19 | Fairfield / 39045 | 83,858 | 1.470002 | 68.172779 | 59,258 |
| 20 | Portage / 39133 | 82,245 | 1.441726 | 69.614505 | 60,481 |
| 21 | Wood / 39173 | 66,801 | 1.170998 | 70.785504 | 48,148 |
| 22 | Clark / 39023 | 62,634 | 1.097952 | 71.883456 | 44,282 |
| 23 | Miami / 39109 | 58,789 | 1.030551 | 72.914007 | 42,131 |
| 24 | Richland / 39139 | 57,747 | 1.012285 | 73.926291 | 41,732 |
| 25 | Geauga / 39055 | 54,632 | 0.957680 | 74.883971 | 42,694 |
| 26 | Wayne / 39169 | 52,745 | 0.924601 | 75.808573 | 38,450 |
| 27 | Columbiana / 39029 | 47,594 | 0.834306 | 76.642879 | 35,545 |
| 28 | Allen / 39003 | 45,988 | 0.806154 | 77.449033 | 32,666 |
| 29 | Ashtabula / 39007 | 42,682 | 0.748201 | 78.197233 | 30,852 |
| 30 | Tuscarawas / 39157 | 42,636 | 0.747394 | 78.944627 | 30,350 |
| 31 | Erie / 39043 | 39,307 | 0.689038 | 79.633665 | 28,833 |
| 32 | Muskingum / 39119 | 38,940 | 0.682605 | 80.316270 | 27,307 |
| 33 | Hancock / 39063 | 37,520 | 0.657713 | 80.973982 | 27,088 |
| 34 | Union / 39159 | 36,960 | 0.647896 | 81.621878 | 25,399 |
| 35 | Ross / 39141 | 32,687 | 0.572992 | 82.194870 | 22,592 |
| 36 | Knox / 39083 | 31,961 | 0.560265 | 82.755135 | 23,080 |
| 37 | Jefferson / 39081 | 30,810 | 0.540089 | 83.295224 | 22,894 |
| 38 | Belmont / 39013 | 30,751 | 0.539054 | 83.834278 | 22,530 |
| 39 | Scioto / 39145 | 30,519 | 0.534987 | 84.369266 | 21,069 |
| 40 | Washington / 39167 | 30,201 | 0.529413 | 84.898679 | 22,751 |
| 41 | Sandusky / 39143 | 29,255 | 0.512830 | 85.411509 | 21,308 |
| 42 | Pickaway / 39129 | 29,051 | 0.509254 | 85.920762 | 19,562 |
| 43 | Darke / 39037 | 26,860 | 0.470846 | 86.391609 | 19,755 |
| 44 | Huron / 39077 | 26,831 | 0.470338 | 86.861947 | 18,404 |
| 45 | Marion / 39101 | 26,782 | 0.469479 | 87.331426 | 19,105 |
| 46 | Lawrence / 39087 | 26,329 | 0.461538 | 87.792964 | 17,490 |
| 47 | Ashland / 39005 | 26,193 | 0.459154 | 88.252118 | 18,409 |
| 48 | Athens / 39009 | 25,637 | 0.449408 | 88.701526 | 19,065 |
| 49 | Auglaize / 39011 | 25,472 | 0.446515 | 89.148041 | 18,671 |
| 50 | Seneca / 39147 | 25,092 | 0.439854 | 89.587895 | 17,958 |
| 51 | Shelby / 39149 | 25,070 | 0.439468 | 90.027364 | 18,028 |
| 52 | Ottawa / 39123 | 23,698 | 0.415418 | 90.442781 | 18,405 |
| 53 | Mercer / 39107 | 23,469 | 0.411403 | 90.854185 | 17,782 |
| 54 | Logan / 39091 | 23,358 | 0.409458 | 91.263642 | 16,454 |
| 55 | Fulton / 39051 | 22,082 | 0.387090 | 91.650732 | 16,207 |
| 56 | Preble / 39135 | 21,531 | 0.377431 | 92.028163 | 15,694 |
| 57 | Brown / 39015 | 20,980 | 0.367772 | 92.395935 | 14,137 |
| 58 | Clinton / 39027 | 20,554 | 0.360304 | 92.756240 | 14,084 |
| 59 | Madison / 39097 | 20,458 | 0.358622 | 93.114861 | 14,120 |
| 60 | Champaign / 39021 | 20,265 | 0.355238 | 93.470100 | 14,402 |
| 61 | Crawford / 39033 | 20,131 | 0.352889 | 93.822989 | 14,804 |
| 62 | Highland / 39071 | 19,728 | 0.345825 | 94.168814 | 13,112 |
| 63 | Putnam / 39137 | 19,704 | 0.345404 | 94.514218 | 15,004 |
| 64 | Defiance / 39039 | 18,730 | 0.328330 | 94.842549 | 13,336 |
| 65 | Morrow / 39117 | 18,534 | 0.324895 | 95.167443 | 13,290 |
| 66 | Williams / 39171 | 18,019 | 0.315867 | 95.483310 | 12,843 |
| 67 | Guernsey / 39059 | 17,387 | 0.304788 | 95.788098 | 12,192 |
| 68 | Perry / 39127 | 16,772 | 0.294007 | 96.082105 | 11,935 |
| 69 | Coshocton / 39031 | 16,185 | 0.283717 | 96.365823 | 11,281 |
| 70 | Van Wert / 39161 | 14,607 | 0.256056 | 96.621878 | 10,135 |
| 71 | Henry / 39069 | 14,603 | 0.255985 | 96.877864 | 10,294 |
| 72 | Jackson / 39079 | 14,117 | 0.247466 | 97.125330 | 8,885 |
| 73 | Carroll / 39019 | 13,659 | 0.239438 | 97.364768 | 10,122 |
| 74 | Hocking / 39073 | 13,296 | 0.233074 | 97.597842 | 9,495 |
| 75 | Hardin / 39065 | 12,791 | 0.224222 | 97.822064 | 8,997 |
| 76 | Gallia / 39053 | 12,724 | 0.223047 | 98.045111 | 9,114 |
| 77 | Fayette / 39047 | 12,393 | 0.217245 | 98.262356 | 8,389 |
| 78 | Holmes / 39075 | 12,197 | 0.213809 | 98.476165 | 8,624 |
| 79 | Adams / 39001 | 12,173 | 0.213388 | 98.689553 | 8,726 |
| 80 | Pike / 39131 | 12,043 | 0.211110 | 98.900663 | 7,815 |
| 81 | Wyandot / 39175 | 11,276 | 0.197664 | 99.098327 | 8,069 |
| 82 | Meigs / 39105 | 10,215 | 0.179065 | 99.277393 | 7,468 |
| 83 | Paulding / 39125 | 9,190 | 0.161097 | 99.438490 | 6,462 |
| 84 | Harrison / 39067 | 7,068 | 0.123900 | 99.562390 | 5,172 |
| 85 | Monroe / 39111 | 6,651 | 0.116590 | 99.678979 | 4,863 |
| 86 | Morgan / 39115 | 6,641 | 0.116414 | 99.795394 | 4,811 |
| 87 | Noble / 39121 | 6,073 | 0.106458 | 99.901851 | 4,606 |
| 88 | Vinton / 39163 | 5,599 | 0.098149 | 100.000000 | 4,016 |
