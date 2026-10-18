# Ohio county partisanship and conditional Senate targets

Research date: **2026-10-17 America/Chicago**; downloads extend into **2026-10-18 UTC**. Ohio’s 2026 race is a **special U.S. Senate election**, November 3, to fill the term ending January 3, 2029. The [official special-election directive](https://www.ohiosos.gov/assets/directive-2025-54-writ-of-special-election-for-united-states-senate-election.pdf), checked during this research, establishes that context. **2022 Ryan–Vance is the recent midterm and same-seat comparison; 2024 Brown–Moreno is the most recent Senate comparison, for the other seat. Ohio held no 2020 Senate election.** Historical candidates do not establish a current coalition or a 2026 forecast.

With **2024 Senate county major-party weights**, Brown’s 206,434-vote deficit requires a uniform **+1.873834 percentage-point Democratic two-party-share shift** to tie. An illustrative **D+1 two-party margin** requires **+2.373834 share points**, yielding **55,083.32 net D−R votes** at that observed volume. Every county’s uniform target is one sufficient joint scenario, not an individually necessary winning threshold.

## Evidence, status and independent totals

The [old 2024 archive](https://www.ohiosos.gov/elections/election-results-and-data/2024-official-election-results/) and [2022 archive](https://www.ohiosos.gov/elections/election-results-and-data/2022-official-election-results/) redirect to the new SOS portal in primary browsing. Direct requests here returned HTTP 403 challenge/maintenance HTML. Those responses, status, URLs, UTC timestamps, redirect history and response hashes remain in [raw metadata](data/baselines/evidence-manifest.json). Native Chrome opened the replacement archive; its saved published JavaScript identifies the official `publicfiles.ohiosos.gov` index, but that direct endpoint also returned 403. No invented API or live cadence is used.

The turnout worker recovered **original official canvass XLSX bytes through Internet Archive**. This assignment reads those originals without modifying or duplicating them: [2024 county summary](data/turnout/raw/2024-summary-archive.xlsx), [2024 precinct workbook](data/turnout/raw/2024-statewide-races-precint-level.xlsx), [2022 county summary](data/turnout/raw/2022-statewide-races-summary.xlsx), [2022 precinct workbook](data/turnout/raw/2022-statewide-races-by-precinct.xlsx). The misspelling `precint` is the real source filename. [Shared input manifest](data/baselines/shared-input-manifest.json) pins original/archive URLs, archive timestamps, retrieval UTC, HTTP 200 headers, original headers and SHA-256 hashes. These are archived certified publications, not newly fetched current SOS archive revisions and not election-night returns. Original [2024 download](https://www.ohiosos.gov/globalassets/elections/2024/gen/official/statewide-race-summary.xlsx); successful [archived capture](https://web.archive.org/web/20241207004035if_/https://www.ohiosos.gov/globalassets/elections/2024/gen/official/statewide-race-summary.xlsx). Original [2022 download](https://www.ohiosos.gov/globalassets/elections/2022/gen/statewide-races-summary.xlsx); successful [archived capture](https://web.archive.org/web/20221229143511if_/https://www.ohiosos.gov/globalassets/elections/2022/gen/statewide-races-summary.xlsx).

All county/candidate cells match the separate contest sheet within each workbook. Independent downloads of the [House Clerk 2024 publication](https://clerk.house.gov/member_info/electionInfo/2024/statistics2024.pdf), [2022 publication](https://clerk.house.gov/member_info/electionInfo/2022/statistics2022.pdf) and [2018 publication](https://clerk.house.gov/member_info/electionInfo/2018/statistics2018.pdf) check every published Senate candidate and presidential party-group total. The House presidential table groups minor tickets; it independently checks their combined denominators, while the SOS canvass and ballot directives establish individual tickets. [Machine-readable independent reconciliation](data/baselines/house-reconciliation.csv) retains every comparison. The [2024 certification announcement](https://www.ohiosos.gov/office/media-center/categories/press-releases/2024-12-02) confirms certification on December 2 and 5,851,387 ballots; the [2022 announcement](https://www.ohiosos.gov/office/media-center/categories/press-releases/2022-12-09) confirms December 9 certification.

| Comparison / vintage | D | R | Other | All candidate votes | D+R | D share of D+R % | D−R two-party margin pp |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024_senate | 2,650,949 | 2,857,383 | 196,288 | 5,704,620 | 5,508,332 | 48.1262 | -3.7477 |
| 2022_senate | 1,939,489 | 2,192,114 | 1,739 | 4,133,342 | 4,131,603 | 46.9428 | -6.1145 |
| 2024_president | 2,533,699 | 3,180,116 | 53,973 | 5,767,788 | 5,713,815 | 44.3434 | -11.3132 |
| 2018_senate_original | 2,355,923 | 2,053,963 | 1,012 | 4,410,898 | 4,409,886 | 53.4237 | +6.8473 |
| 2018_senate_amended | 2,358,508 | 2,057,559 | 1,017 | 4,417,084 | 4,416,067 | 53.4074 | +6.8149 |

“Other” retains every published minor-party and write-in count, including zero-vote candidate rows. Ballots, votes in the contest and D+R are separate denominators. The all-candidate Senate total is 146,767 below ballots in 2024 and 68,026 below ballots in 2022; president is 83,599 below 2024 ballots. Those residuals are **unclassified ballots-minus-counted-contest-votes**, not an inferred undervote or invalid-ballot count.

## Candidate universe and source labels

[candidate-universe.csv](data/baselines/candidate-universe.csv) preserves original labels/column coordinates and full statewide sums; [candidate-votes.csv](data/baselines/candidate-votes.csv) preserves **2,992 county/candidate rows across 34 candidate-vintages**, covering five comparison vintages ×88 counties. Write-ins remain write-ins with unspecified party; they are not assigned to D or R.

The [2024 certified ballot directive](https://www.ohiosos.gov/assets/dir2024-23.pdf) independently lists the major Senate candidates and four valid Senate write-ins, and the original five presidential write-in tickets. [Directive2024-26](https://www.ohiosos.gov/assets/dir2024-26.pdf) adds four presidential write-in tickets, yielding nine. Source aliases are preserved: e.g. Jay J. Bowman/De D. Bowman versus canvass Jay Bowman/De D Bowman; Tariq Shabazz versus canvass Tariq K. Shabazz;2018 Jim Renacci versus House James B. Renacci. Duncan’s ballot designation is **Nonparty candidate** and Sonski’s **Other-party candidate**, despite neither having a party marker in the canvass. The House groups them together as No Party. Do not silently relabel either as a Democrat or a Green.

| Comparison | Candidate / presidential ticket | Published party or status | Counted votes |
|---|---|---|---:|
| 2024_senate | Sherrod Brown | Democratic | 2,650,949 |
| 2024_senate | Stephen Faris | write-in; party not published | 84 |
| 2024_senate | Don Kissick | Libertarian | 195,648 |
| 2024_senate | Bernie Moreno | Republican | 2,857,383 |
| 2024_senate | David Allen Pastorius | write-in; party not published | 13 |
| 2024_senate | Nathan Russell | write-in; party not published | 19 |
| 2024_senate | Tariq K. Shabazz | write-in; party not published | 524 |
| 2022_senate | John Cheng | write-in; party not published | 702 |
| 2022_senate | Matthew R. Esh | write-in; party not published | 78 |
| 2022_senate | Stephen Faris | write-in; party not published | 194 |
| 2022_senate | Shane Hoffman | write-in; party not published | 403 |
| 2022_senate | Tim Ryan | Democratic | 1,939,489 |
| 2022_senate | LaShondra Tinsley | write-in; party not published | 362 |
| 2022_senate | JD Vance | Republican | 2,192,114 |
| 2024_president | Shiva Ayyadurai and Crystal Ellis | write-in; party not published | 74 |
| 2024_president | Jay Bowman and De D Bowman | write-in; party not published | 7 |
| 2024_president | John Cheng and Wayne Waligorski | write-in; party not published | 24 |
| 2024_president | Claudia De la Cruz and Karina Garcia | write-in; party not published | 1,794 |
| 2024_president | Richard Duncan and Mitchell Preston Bupp | party not displayed in canvass | 12,805 |
| 2024_president | Cherunda Fox and Harlan McVay | write-in; party not published | 0 |
| 2024_president | Chris Garrity and Cody Ballard | write-in; party not published | 13 |
| 2024_president | Kamala D. Harris and Tim Walz | Democratic | 2,533,699 |
| 2024_president | Brian Kienitz and Christina Johnston | write-in; party not published | 4 |
| 2024_president | William Nalbach and Willis Butts | write-in; party not published | 3 |
| 2024_president | Chase Oliver and Mike ter Maat | Libertarian | 28,200 |
| 2024_president | Peter Sonski and Lauren Onak | party not displayed in canvass | 10,197 |
| 2024_president | Donald J. Trump and JD Vance | Republican | 3,180,116 |
| 2024_president | Cornel West and Melina Abdullah | write-in; party not published | 852 |
| 2018_senate_amended | Sherrod Brown | Democratic | 2,358,508 |
| 2018_senate_amended | Stephen Faris | write-in; party not published | 1,017 |
| 2018_senate_amended | Jim Renacci | Republican | 2,057,559 |

The earlier 2024 ballot sample includes **Jill Stein/Anita Rios**, while the certified canvass omits them. The [primary Warren BOE page](https://liveresults.boe.ohio.gov/ENR/warrenohenr/14/en/Index_14.html), checked in primary browsing, says the ticket withdrew and votes for it would not count, even though some displayed precinct rows retain marks. No such marks enter this certified denominator. This is a ballot-vintage exclusion, not an invented zero-vote valid candidacy. Robert F. Kennedy Jr./Nicole Shanahan appear in the [August qualification announcement](https://www.ohiosos.gov/office/media-center/categories/press-releases/2024-08-23), but are absent from the September revised certified ballot and final canvass; they likewise are not inserted as counted candidates. Exact rejected-mark totals were not established. Direct downloads of these current explanatory pages were blocked; [primary-web-observations.json](data/baselines/primary-web-observations.json) distinguishes primary browsing from saved HTTP evidence.

## Retained 2018 amendment

This assignment independently recovered the [original2018 county canvass](data/baselines/raw/2018-statewidecounty.xlsx), [Miami-amended county canvass](data/baselines/raw/2018-statewidecounty-miami-recovered.xlsx) and [official archive index](data/baselines/raw/archive-2018-index.html.gz). The [archived primary index](https://web.archive.org/web/20250305100623if_/https://www.ohiosos.gov/elections/election-results-and-data/2018-official-elections-results/) explains that **6,282 early in-person absentee ballots in Miami had not been counted**, and the board certified amended results on **January 22, 2019**. The amendment changes only Miami in the relevant columns: Brown+2,585, Renacci+3,596, Faris+5; Senate total+6,186; total voters+6,282. Registration does not change. [2018-revisions.csv](data/baselines/2018-revisions.csv) preserves each difference. The earlier House 2018 publication agrees exactly with the original vintage; its difference from the amended total is therefore explained and retained. The amended file supplies the additional volume anchor; it does not supersede 2024/2022 as the recent baseline.

## Geography, coverage and priority reconciliation

[county-baselines.csv](data/county-baselines.csv) contains **440 rows**, all 88 counties for each of 2024 Senate, 2024 president, 2022 Senate, 2018 original Senate and 2018 amended Senate. [Census2020 national county codes](https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt) provide FIPS and COUNTYNS, joined by exact county name after stripping the Census suffix. The SOS county source’s native key is **County Name**; it publishes no numeric county, election, contest or candidate ID in these workbooks. [source-schema.json](data/baselines/source-schema.json) records native contest text and workbook/worksheet/column/row coordinates; local comparison keys are explicitly derivatives.

[native-reporting-units.csv.gz](data/baselines/native-reporting-units.csv.gz) retains **8,878 precinct rows for 2024** and **8,933 for 2022**, with county/FIPS, native three-letter SOS Precinct Code, Precinct Name, source row, voter-registration and ballot denominators, and vintage. The 2024 ballot directive independently defines those three-letter codes. **926 codes in 2024 and 936 in 2022 recur across multiple counties**: code alone is unsafe as a key. Use election vintage + county FIPS + native code. Identical codes across years do not establish compatible boundaries. No cross-year precinct join or 2026 map/reporting-unit approval is asserted;2018 precinct evidence was not acquired. County-level named/FIPS aggregation is compatible for these calculations; it is not a geometric boundary audit.

Both precinct workbooks explicitly say write-in detail is unavailable. Their write-in zero cells represent **omission**, not certified zero votes. Same-election non-write-in precinct sums match every county summary exactly; the separately retained summary supplies **640 Senate write-ins and 2,771 presidential write-ins in 2024, and 1,739 Senate write-ins in 2022**. No write-ins are allocated to precinct polygons. See [2,464 candidate/county precinct checks](data/baselines/precinct-county-checks.csv); all precinct registration and ballot sums also reconcile countywide.

The independently computed ranking agrees with turnout’s exact supplied order. Top 15: **3,525,320 /5,704,620 =61.797631%**. Minimum 80%: **32 counties,4,581,738 /5,704,620 =80.316270%**; first 31 supply 4,542,798 =79.633665%. Thus the union with top 15 remains 32. [priority-set.json](data/baselines/priority-set.json) and [all 88 ranking](data/baselines/priority-reconciliation.csv) preserve the exact set and nonpriority remainder. In that set 2024 Senate D−R is+231,974; the other 56 counties contribute−438,408, producing the statewide−206,434. The priority set is a research allocation, not the entire statewide electorate. Final worker-to-worker CSV status: **exact_all 88_confirmed_schema**. [Reconciliation summary with stable file hashes](data/baselines/turnout-worker-reconciliation.json) records **zero differences**: [1,936 county field comparisons](data/baselines/turnout-worker-reconciliation.csv), [all2,464 common candidate cells](data/baselines/turnout-worker-candidate-reconciliation.csv), all 88 rank/FIPS/native county keys, every historical count and five comparison rank fields, priority flags, all 17,811 native unit identities ([176 county/year checks](data/baselines/turnout-worker-unit-reconciliation.csv)), and the exact 32-county priority order. Statewide sums are 5,704,620 Senate 2024;5,767,788 president 2024;4,133,342 Senate 2022 in both workers.

## County leaning, mixedness and contributions

The 2024 Senate D counties are **Athens, Cuyahoga, Franklin, Hamilton, Lorain, Lucas, Montgomery and Summit**; the other 80 voted R. Ryan won the same eight in 2022; Harris won seven in 2024. These labels describe the named election. “Mixed” means absolute two-party margin≤5 pp: Delaware, Erie, Lake, Lorain, Mahoning and Wood. The next band>5–10 pp contains Montgomery, Portage and Trumbull. Full machine data include each contest’s bands, all-vote margins, candidate counts, contributions and other shares. Brown’s two-party D share exceeded Harris’s in **all 88 counties**, with statewide difference **3.782781 share points**; that observed candidate/contest difference is not a transferable 2026 effect.

Table order uses 2024 Senate **all-candidate vote volume**. An asterisk marks the 32 priority counties. Signed margins are D−R, weight is county share of statewide 2024 Senate **D+R**; net contribution is raw D−R. D+1 target is the uniform 2024 Senate scenario. CSVs retain unrounded values and 1 pp-share net-vote effects.

| Rank | County (FIPS) | Senate D share % | Senate margin pp | President margin pp | 2022 Senate margin pp | Major-party weight % | Net D−R | D+1 target D share % |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1* | Franklin (39049) | 67.42 | +34.844 | +28.695 | +32.545 | 10.390 | +199,409 | 69.796 |
| 2* | Cuyahoga (39035) | 69.23 | +38.465 | +31.707 | +35.648 | 10.070 | +213,371 | 71.606 |
| 3* | Hamilton (39061) | 59.80 | +19.602 | +15.034 | +15.454 | 7.159 | +77,302 | 62.175 |
| 4* | Summit (39153) | 57.43 | +14.859 | +7.048 | +13.204 | 4.758 | +38,944 | 59.803 |
| 5* | Montgomery (39113) | 53.74 | +7.472 | +0.476 | +1.684 | 4.408 | +18,140 | 56.110 |
| 6* | Lucas (39095) | 59.77 | +19.542 | +12.676 | +19.522 | 3.274 | +35,239 | 62.145 |
| 7* | Stark (39151) | 43.15 | -13.691 | -22.122 | -15.784 | 3.173 | -23,931 | 45.529 |
| 8* | Butler (39017) | 39.92 | -20.161 | -26.505 | -23.796 | 3.171 | -35,218 | 42.293 |
| 9* | Lorain (39093) | 52.50 | +4.996 | -5.771 | +2.420 | 2.742 | +7,548 | 54.872 |
| 10* | Warren (39165) | 36.79 | -26.423 | -31.827 | -29.011 | 2.435 | -35,446 | 39.162 |
| 11* | Delaware (39041) | 49.22 | -1.559 | -6.655 | -6.292 | 2.349 | -2,018 | 51.594 |
| 12* | Lake (39085) | 47.56 | -4.880 | -14.473 | -8.212 | 2.219 | -5,964 | 49.934 |
| 13* | Clermont (39025) | 34.89 | -30.223 | -36.106 | -32.266 | 1.968 | -32,767 | 37.262 |
| 14* | Mahoning (39099) | 49.90 | -0.204 | -9.486 | -3.468 | 1.959 | -220 | 52.272 |
| 15* | Medina (39103) | 42.29 | -15.420 | -25.016 | -17.938 | 1.853 | -15,742 | 44.664 |
| 16* | Trumbull (39155) | 46.97 | -6.066 | -16.947 | -7.115 | 1.669 | -5,577 | 49.341 |
| 17* | Licking (39089) | 39.00 | -21.994 | -30.286 | -25.312 | 1.646 | -19,947 | 41.377 |
| 18* | Greene (39057) | 43.00 | -13.997 | -20.033 | -19.335 | 1.576 | -12,150 | 45.375 |
| 19* | Fairfield (39045) | 41.58 | -16.838 | -24.260 | -21.308 | 1.471 | -13,645 | 43.955 |
| 20* | Portage (39133) | 46.79 | -6.412 | -15.674 | -6.781 | 1.439 | -5,081 | 49.168 |
| 21* | Wood (39173) | 48.78 | -2.434 | -10.257 | -3.294 | 1.163 | -1,559 | 51.157 |
| 22* | Clark (39023) | 39.23 | -21.548 | -29.809 | -22.565 | 1.094 | -12,981 | 41.600 |
| 23* | Miami (39109) | 30.88 | -38.238 | -45.541 | -43.036 | 1.030 | -21,700 | 33.255 |
| 24* | Richland (39139) | 33.10 | -33.801 | -42.680 | -38.134 | 1.014 | -18,880 | 35.473 |
| 25* | Geauga (39055) | 41.87 | -16.270 | -24.317 | -18.705 | 0.968 | -8,672 | 44.239 |
| 26* | Wayne (39169) | 34.05 | -31.899 | -39.622 | -33.221 | 0.923 | -16,219 | 36.424 |
| 27* | Columbiana (39029) | 30.45 | -39.105 | -49.386 | -39.748 | 0.829 | -17,855 | 32.821 |
| 28* | Allen (39003) | 31.85 | -36.293 | -44.494 | -42.260 | 0.805 | -16,088 | 34.227 |
| 29* | Ashtabula (39007) | 41.04 | -17.926 | -28.630 | -18.536 | 0.743 | -7,332 | 43.411 |
| 30* | Tuscarawas (39157) | 33.01 | -33.974 | -43.623 | -32.318 | 0.742 | -13,894 | 35.387 |
| 31* | Erie (39043) | 47.97 | -4.069 | -14.282 | -6.057 | 0.686 | -1,537 | 50.339 |
| 32* | Muskingum (39119) | 31.81 | -36.382 | -44.266 | -36.723 | 0.676 | -13,556 | 34.183 |
| 33 | Hancock (39063) | 33.83 | -32.338 | -38.874 | -35.606 | 0.653 | -11,633 | 36.205 |
| 34 | Union (39159) | 38.49 | -23.024 | -29.927 | -28.529 | 0.647 | -8,207 | 40.862 |
| 35 | Ross (39141) | 35.29 | -29.426 | -39.682 | -30.417 | 0.572 | -9,277 | 37.661 |
| 36 | Knox (39083) | 30.86 | -38.272 | -45.313 | -39.592 | 0.561 | -11,826 | 33.238 |
| 37 | Jefferson (39081) | 33.16 | -33.687 | -44.405 | -30.834 | 0.538 | -9,976 | 35.530 |
| 38 | Belmont (39013) | 31.99 | -36.021 | -47.597 | -34.686 | 0.538 | -10,670 | 34.364 |
| 39 | Scioto (39145) | 30.35 | -39.309 | -48.250 | -39.137 | 0.535 | -11,574 | 32.720 |
| 40 | Washington (39167) | 31.83 | -36.342 | -44.085 | -39.007 | 0.529 | -10,590 | 34.203 |
| 41 | Sandusky (39143) | 38.88 | -22.244 | -31.144 | -23.051 | 0.503 | -6,169 | 41.252 |
| 42 | Pickaway (39129) | 30.12 | -39.768 | -48.993 | -41.744 | 0.510 | -11,161 | 32.490 |
| 43 | Darke (39037) | 20.63 | -58.736 | -65.820 | -61.792 | 0.472 | -15,256 | 23.006 |
| 44 | Huron (39077) | 33.09 | -33.819 | -44.433 | -34.790 | 0.464 | -8,638 | 35.464 |
| 45 | Marion (39101) | 34.49 | -31.027 | -41.728 | -33.599 | 0.465 | -7,939 | 36.860 |
| 46 | Lawrence (39087) | 28.46 | -43.076 | -50.888 | -45.192 | 0.459 | -10,885 | 30.836 |
| 47 | Ashland (39005) | 28.92 | -42.163 | -50.437 | -45.283 | 0.457 | -10,614 | 31.293 |
| 48 | Athens (39009) | 59.48 | +18.953 | +10.842 | +21.490 | 0.449 | +4,683 | 61.850 |
| 49 | Auglaize (39011) | 21.32 | -57.352 | -65.065 | -60.982 | 0.447 | -14,115 | 23.698 |
| 50 | Seneca (39147) | 35.56 | -28.881 | -37.895 | -29.521 | 0.434 | -6,911 | 37.933 |
| 51 | Shelby (39149) | 20.36 | -59.284 | -65.325 | -61.057 | 0.439 | -14,348 | 22.732 |
| 52 | Ottawa (39123) | 41.53 | -16.934 | -25.301 | -15.775 | 0.414 | -3,857 | 43.907 |
| 53 | Mercer (39107) | 19.05 | -61.904 | -67.211 | -61.876 | 0.413 | -14,095 | 21.422 |
| 54 | Logan (39091) | 25.09 | -49.823 | -56.681 | -52.605 | 0.406 | -11,149 | 27.462 |
| 55 | Fulton (39051) | 31.88 | -36.231 | -42.749 | -34.600 | 0.385 | -7,686 | 34.258 |
| 56 | Preble (39135) | 23.81 | -52.376 | -59.579 | -54.962 | 0.377 | -10,866 | 26.186 |
| 57 | Brown (39015) | 22.79 | -54.429 | -61.840 | -53.297 | 0.367 | -11,012 | 25.160 |
| 58 | Clinton (39027) | 26.21 | -47.587 | -55.057 | -49.393 | 0.357 | -9,359 | 28.580 |
| 59 | Madison (39097) | 32.14 | -35.716 | -44.127 | -38.355 | 0.357 | -7,025 | 34.516 |
| 60 | Champaign (39021) | 28.50 | -43.002 | -51.238 | -42.919 | 0.353 | -8,370 | 30.873 |
| 61 | Crawford (39033) | 27.92 | -44.151 | -53.368 | -46.659 | 0.351 | -8,538 | 30.298 |
| 62 | Highland (39071) | 21.81 | -56.377 | -63.688 | -55.378 | 0.346 | -10,732 | 24.185 |
| 63 | Putnam (39137) | 18.65 | -62.694 | -69.385 | -64.438 | 0.348 | -12,009 | 21.027 |
| 64 | Defiance (39039) | 32.83 | -34.331 | -40.250 | -32.308 | 0.325 | -6,148 | 35.208 |
| 65 | Morrow (39117) | 25.89 | -48.223 | -56.171 | -50.286 | 0.323 | -8,587 | 28.263 |
| 66 | Williams (39171) | 29.53 | -40.945 | -48.699 | -39.196 | 0.310 | -6,993 | 31.901 |
| 67 | Guernsey (39059) | 29.02 | -41.961 | -52.439 | -42.461 | 0.303 | -6,997 | 31.393 |
| 68 | Perry (39127) | 27.87 | -44.261 | -54.928 | -43.827 | 0.293 | -7,134 | 30.243 |
| 69 | Coshocton (39031) | 28.81 | -42.371 | -52.646 | -42.267 | 0.281 | -6,554 | 31.188 |
| 70 | Van Wert (39161) | 22.84 | -54.326 | -58.949 | -57.060 | 0.255 | -7,622 | 25.211 |
| 71 | Henry (39069) | 31.02 | -37.953 | -47.151 | -38.010 | 0.255 | -5,329 | 33.397 |
| 72 | Jackson (39079) | 24.52 | -50.956 | -58.414 | -48.559 | 0.248 | -6,953 | 26.896 |
| 73 | Carroll (39019) | 27.09 | -45.828 | -55.184 | -45.764 | 0.238 | -5,998 | 29.460 |
| 74 | Hocking (39073) | 32.42 | -35.162 | -44.646 | -33.860 | 0.231 | -4,474 | 34.793 |
| 75 | Hardin (39065) | 27.58 | -44.830 | -55.175 | -45.040 | 0.222 | -5,472 | 29.959 |
| 76 | Gallia (39053) | 23.81 | -52.372 | -59.833 | -53.540 | 0.222 | -6,404 | 26.188 |
| 77 | Fayette (39047) | 26.91 | -46.187 | -55.557 | -49.887 | 0.216 | -5,505 | 29.280 |
| 78 | Holmes (39075) | 17.92 | -64.167 | -69.701 | -63.712 | 0.215 | -7,582 | 20.290 |
| 79 | Adams (39001) | 20.79 | -58.427 | -66.071 | -54.705 | 0.214 | -6,878 | 23.160 |
| 80 | Pike (39131) | 28.93 | -42.140 | -54.006 | -40.448 | 0.211 | -4,900 | 31.304 |
| 81 | Wyandot (39175) | 27.72 | -44.565 | -51.642 | -44.086 | 0.196 | -4,817 | 30.091 |
| 82 | Meigs (39105) | 24.96 | -50.086 | -57.363 | -49.759 | 0.179 | -4,929 | 27.331 |
| 83 | Paulding (39125) | 23.54 | -52.920 | -56.757 | -50.867 | 0.159 | -4,622 | 25.914 |
| 84 | Harrison (39067) | 27.52 | -44.961 | -55.729 | -43.890 | 0.123 | -3,034 | 29.893 |
| 85 | Monroe (39111) | 26.79 | -46.429 | -60.309 | -43.257 | 0.117 | -2,990 | 29.160 |
| 86 | Morgan (39115) | 28.20 | -43.591 | -53.627 | -45.250 | 0.116 | -2,785 | 30.579 |
| 87 | Noble (39121) | 22.42 | -55.169 | -65.060 | -52.934 | 0.107 | -3,239 | 24.789 |
| 88 | Vinton (39163) | 25.29 | -49.424 | -58.982 | -48.779 | 0.098 | -2,658 | 27.662 |

## Share points, third candidates and conditional targets

For each county, `s=D/(D+R)` and scenario major-party volume `T_c`. With `M0=sum(T_c*(2*s_c-1))`, total `T=sum(T_c)`, the uniform tie shift is `-M0/(2*T)`; at observed weights this is `(R-D)/(2*(D+R))`. A target margin `m` uses `(m*T-M0)/(2*T)`. Set `m=.01` for D+1. One D-share point transfers 1% ofT from R to D, changing the **D−R margin by 2 points** and net votes by`.02*T`. Fractional target votes are expected-value arithmetic; no integer ballot allocation is implied.

2024 Senate includes **196,288 other votes (3.440860% of all counted candidate votes)**, primarily 195,648 for Libertarian Don Kissick. Two-party D+1 at fixed other votes equals only **0.965591 all-candidate margin points**. To demand a full 1 pp all-candidate margin at the same fixed third-candidate count instead requires+2.391651 D-share points and 57,046.20 net votes. [third-candidate-denominators.csv](data/baselines/third-candidate-denominators.csv) makes that distinction explicit for every main comparison. Changes in third-candidate support, candidate identity or turnout composition require different assumptions; no conversion from ballots to major-party votes is assumed. A D−R tie is not a certified win, and a two-party target does not establish plurality against a potentially stronger third candidate.

The amended 2018 Brown baseline already wins. At its own observed weights, its tie shift is **−3.407432 D-share points** and D+1 shift **−2.907432**. A positive improvement is unnecessary there. All historical uniform scenarios saved here remain within[0,1]; the calculator does not silently clip infeasible shares. For other inputs, a target outside[0,1] must be labeled infeasible and recomputed with bounded shares before use.

For one selected county, hold every other county at its explicit baseline D share (or supplied override), and solve:

`required_selected_share=(m*T - sum_other(T_j*(2*s_j-1)) + T_selected)/(2*T_selected)`.

At 2024 Senate volume with all other counties at their Brown–Moreno shares, **Franklin alone needs 85.457748% D share to tie, or 90.270275% for statewide D+1**, versus 67.421993% observed. These are conditional alternatives, not county-level necessary targets. [selected-county-targets.csv](data/baselines/selected-county-targets.csv) provides all 88 counties for all 24 scenario/target combinations, including below 0% (`already_secured` under the other-county assumptions) and above 100% (`impossible`) requirements. Exact 0/100% are feasible boundary ties. Nonpositive selected turnout is rejected. No clipping hides impossible cases.

## Historical low/base/high volume and composition sensitivity

The labels **low=2022 Senate**, **base=2018 Miami-amended Senate**, **high=2024 Senate** are simply the ordered observed major-party volumes: **4,131,603 /4,416,067 /5,508,332**. Base is the middle observed volume, not a 2026 central estimate. Corresponding historical ballots/total voters are 4,201,368 /4,503,116 /5,851,387; all-candidate Senate votes are 4,133,342 /4,417,084 /5,704,620. Each volume has a different candidate field and political environment. None is an invented special-election turnout projection.

The table keeps 2024 Senate county D shares fixed and independently crosses three observed county weight patterns with the three observed statewide D+R volumes. Uniform statewide volume changes multiply net votes but leave the tie share shift unchanged. A 1 pp uniform D-share gain has 82,632.06 /88,321.34 /110,166.64 net-vote effect at low/base/high volume. Geographic composition changes alter weighted leaning even at the same statewide volume: at high volume, 2022 weights reduce the baseline deficit from 206,434 to 204,095.90; amended 2018 weights reduce it to 131,466.48. That is a composition experiment, not evidence that 2026 will reproduce those weights.

| County turnout mix | Statewide D+R volume | Baseline D−R net | Tie D-share shift pp | D+1 D-share shift pp |
|---|---:|---:|---:|---:|
| 2024_senate | 5,508,332 | -206,434.00 | +1.873834 | +2.373834 |
| 2024_senate | 4,131,603 | -154,838.77 | +1.873834 | +2.373834 |
| 2024_senate | 4,416,067 | -165,499.53 | +1.873834 | +2.373834 |
| 2022_senate | 5,508,332 | -204,095.90 | +1.852611 | +2.352611 |
| 2018_senate_amended | 5,508,332 | -131,466.48 | +1.193342 | +1.693342 |
| 2022_senate | 4,131,603 | -153,085.04 | +1.852611 | +2.352611 |
| 2022_senate | 4,416,067 | -163,625.06 | +1.852611 | +2.352611 |
| 2018_senate_amended | 4,131,603 | -98,608.31 | +1.193342 | +1.693342 |
| 2018_senate_amended | 4,416,067 | -105,397.56 | +1.193342 | +1.693342 |

The [12 scenario definitions](data/baselines/scenario-definitions.json) include the nine 2024-share volume/composition combinations plus each other main comparison at its own observed volume and shares. [state-scenarios.csv](data/baselines/state-scenarios.csv) has 24 tie/cushion rows; [county-target-scenarios.csv](data/baselines/county-target-scenarios.csv) has 2,112 county contribution/weight/target rows. All 88 counties enter every statewide sum.

## Reproduction, validation and substantive gaps

From the repository root:

```sh
python3 senate/2026/ohio/data/baselines/calculate.py
python3 senate/2026/ohio/data/baselines/validate.py --require-turnout
python3 senate/2026/ohio/data/baselines/render_report.py
python3 senate/2026/ohio/data/baselines/finalize.py
python3 senate/2026/ohio/data/baselines/calculate.py --selected-county Franklin --target-margin .01
```

The calculator also accepts `--comparison`, `--turnout-mix`, `--total-major-votes`, and `--hold-shares-json PATH` (county→fractional D-share overrides; unlisted counties remain at their observed shares). `fetch.py NAME URL` retains exact decoded responses plus headers/status, retrieval UTC and stored/decoded hashes for new evidence; an HTTP 200 alone is not proof of usable election data. All downloads above are stored originals or explicitly labeled failed responses.

The independent audit reads raw Excel XML through a separate DOM implementation, checks 2,992 source cells and labels against the exports, independent House identities/totals, all 440 FIPS/denominator balances, same-election precinct sums and declared write-in omissions, all county weights, minimum 80%, Miami revisions, uniform and conditional target arithmetic, physically impossible/already-secured cases, and a zero-denominator rejection. Current core/final check result: **PASS**, 60,881 checks. [validation.json](data/baselines/validation.json) states scope; [SHA256SUMS](data/baselines/SHA256SUMS) pins retained assets. These checks establish deterministic historical/scenario readiness, not calibration of live probabilities.

Substantive limits: current SOS historical endpoints are blocked for direct fetching; archived originals may precede a later unobserved revision. Known 2018 revision is retained explicitly; no unexplained county-total discrepancy was found in the selected 2024/2022 captures. Precinct-level write-in distribution remains unavailable; finer-unit partial returns therefore cannot automatically be compared with complete county shares. No validated cross-year/November 2026 precinct crosswalk, approved current map, voting-method-specific partisan baseline, exact outstanding-vote estimate, live collection cadence, current candidate coalition, calibrated probability or live Needle is supplied. The coordinator’s MOCK/test/primary source warnings remain applicable; none of those products supplies the historical certified counts here.
