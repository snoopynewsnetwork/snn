# Oklahoma turnout volume and exact county priority

Research retrieval: **2026-10-18 UTC** (16:46:49–16:47:23 for the retained evidence set). **All 77 counties are included.** Oklahoma had **no 2024 U.S. Senate contest**, so the primary recent statewide volume measure is the **2024 presidential contest**: all five official tickets, **1,566,173 votes**. The ranking measures vote volume, not turnout rate. Counts come from the Oklahoma State Election Board's (OSEB) official results application (OKER), from its own "County Level Results - CSV" export. That export is retained as a one-time capture made 2026-10-18 (see access notes). The 2024 statewide totals match the Governor's certificate of ascertainment exactly. [County extract](data/county-turnout.csv), [OSEB 2024 general results page](https://oklahoma.gov/elections/elections-results/election-results/2024-election-results/november-general-election.html), [OKER 2024 results](https://results.okelections.us/OKER/?elecDate=20241105).

**Top 15, in descending order:** Oklahoma, Tulsa, Cleveland, Canadian, Rogers, Wagoner, Comanche, Creek, Payne, Pottawatomie, Grady, Muskogee, Logan, Washington, Garfield. Together they cast **1,066,089 / 1,566,173 = 68.0696832342%** of the 2024 presidential vote.

**Smallest set reaching 80%: 25 counties, 1,253,665 / 1,566,173 = 80.0463933422%.** The first 24 counties hold **1,236,291 = 78.9370650624%**. Mayes (FIPS 40097) adds **17,374** and crosses the threshold. Integer proof: `5 × 1,236,291 = 6,181,455 < 4 × 1,566,173 = 6,264,692 ≤ 5 × 1,253,665 = 6,268,325`. Counties are sorted largest first, so no 24-county selection can reach 80%. The other **52 counties hold 312,508 votes = 19.9536066578%**. Ties would break by ascending FIPS, but no tie touches either boundary, and no rounding enters the selection. [Machine contract](data/turnout/priority-set.json).

**Exact 25, in order:** Oklahoma, Tulsa, Cleveland, Canadian, Rogers, Wagoner, Comanche, Creek, Payne, Pottawatomie, Grady, Muskogee, Logan, Washington, Garfield, McClain, Osage, Carter, Le Flore, Stephens, Delaware, Cherokee, Bryan, Pittsburg, Mayes. The top 15 fall inside this set.

## Midterm comparator: 2022, two Senate contests kept separate

Oklahoma held two U.S. Senate contests on 2022-11-08. The **special election** (OKER title `FOR UNITED STATES SENATOR (UNEXPIRED TERM)`; the House Clerk prints "For unexpired term ending January 3, 2027") filled **the same Class II seat that is on the 2026 ballot**. It is the same-seat midterm comparator. The **regular election** filled the other (Class III) seat. Neither is substituted for the other, and the governor's race is shown only as context. [2022 OKER results](https://results.okelections.us/OKER/?elecDate=20221108), [House Clerk 2022 statistics, PDF p.41](https://clerk.house.gov/member_info/electionInfo/2022/statistics2022.pdf).

| Measure | Denominator | Top-15 share | Minimum 80% set | Crossing county | Change from the 2024 set |
| --- | ---: | ---: | --- | --- | --- |
| **2024 president** (primary) | 1,566,173 | 68.0696832342% | **25**, 80.0463933422% (first 24: 78.9370650624%) | Mayes, 17,374 | none |
| **2022 Senate special, same seat** | 1,150,481 | 68.7971378928% | **25**, 80.3788154694% (first 24: 79.3252561320%) | Le Flore, 12,121 | adds **Kay**, drops **Bryan** |
| 2022 Senate regular, other seat | 1,150,732 | 68.8148934765% | 25, 80.3905687858% (first 24: 79.3386296722%) | Le Flore, 12,105 | adds Kay, drops Bryan |
| 2022 governor (context) | 1,153,284 | 68.8235508340% | 25, 80.3950284579% | Le Flore, 12,141 | adds Kay, drops Bryan |
| 2020 Senate regular, same seat (context) | 1,556,361 | 68.1375978966% | 26, 80.9302597534% (first 25: 79.9081961062%) | Bryan, 15,907 | adds Kay |
| 2020 president (context) | 1,560,699 | 68.0898751137% | 26, 80.8949707791% | Bryan, 15,976 | adds Kay |

The **top 15 are the same 15 counties under every measure**; only Washington and Logan swap places 13–14 in 2022. The 2022 special-Senate 80% set is, in order: Oklahoma, Tulsa, Cleveland, Canadian, Rogers, Wagoner, Comanche, Creek, Payne, Pottawatomie, Grady, Muskogee, Washington, Logan, Garfield, Osage, McClain, Cherokee, Carter, Delaware, Stephens, Pittsburg, Mayes, Kay, Le Flore. Its integer proof is `5 × 912,622 = 4,563,110 < 4 × 1,150,481 = 4,601,924 ≤ 5 × 924,743 = 4,623,715`. Kay ranks 26th in 2024 (16,913) but 24th in the 2022 special (12,499). Bryan ranks 23rd in 2024 (17,812) but 26th in the 2022 special (11,457).

The fixed 2024 25-county set still holds **923,701 / 1,150,481 = 80.2882446559%** of 2022 special-Senate votes. It holds 80.2988880122% of 2022 regular-Senate votes but only 79.8255032091% of 2020 Senate votes. The 25 counties plus Kay make **26 counties**: the union of the 2024 and both 2022 Senate minimum sets, and exactly the 2020 Senate minimum set. That union covers 81.1262868151% of 2024 president, 81.3746598162% of the 2022 special and 81.3856745098% of the 2022 regular Senate votes. **Suggested research priority for the coordinator to decide:** the 26-county union, because Kay belongs to the minimum 80% set of every 2022 and 2020 measure. The strict 2024 answer remains the 25 counties above. [Comparisons and fixed-set coverage](data/turnout/priority-set.json).

## Denominators and certified controls

Each denominator is the sum of every official candidate or ticket in OKER's statewide race export. No write-in category appears in any of these six race exports. Every county row satisfies total = absentee mail + early + election day. The 77 county rows sum exactly to the statewide export for every candidate and method. [Statewide controls](data/turnout/statewide-controls.csv), [all county × candidate × method cells](data/turnout/county-candidate-method.csv).

| Contest (OKER race ID) | Candidates, party: total votes | Total | Absentee mail / early / election day | Independent certified control |
| --- | --- | ---: | --- | --- |
| 2024 president (10001) | Trump/Vance REP 1,036,213; Harris/Walz DEM 499,599; Kennedy/Shanahan IND 16,020; Oliver/ter Maat LIB 9,198; Garrity/Ballard IND 5,143 | 1,566,173 | 103,084 / 293,206 / 1,169,883 | [NARA certificate of ascertainment](https://www.archives.gov/files/electoral-college/2024/ascertainment-oklahoma.pdf), signed 2024-12-05 "as appears by the certified returns of the Oklahoma State Election Board": all 5 equal |
| 2022 Senate special (10011) | Mullin REP 710,643; K. Horn DEM 405,389; Murphy LIB 17,386; Woods IND 17,063 | 1,150,481 | 70,570 / 132,087 / 947,824 | [House Clerk 2022](https://clerk.house.gov/member_info/electionInfo/2022/statistics2022.pdf), PDF p.41: all 4 equal |
| 2022 Senate regular (10010) | Lankford REP 739,960; M. Horn DEM 369,370; Delaney IND 20,907; Blevins LIB 20,495 | 1,150,732 | 70,598 / 132,060 / 948,074 | House Clerk 2022, PDF p.41: all 4 equal |
| 2022 governor (10001) | Stitt REP 639,484; Hofmeister DEM 481,904; Bruno LIB 16,243; Yen IND 15,653 | 1,153,284 | 70,738 / 132,242 / 950,304 | none retrieved (OKER only) |
| 2020 Senate (10003) | Inhofe REP 979,140; Broyles DEM 509,763; Murphy LIB 34,435; Farr IND 21,652; Nesbit IND 11,371 | 1,556,361 | 280,846 / 166,717 / 1,108,798 | [House Clerk 2020](https://clerk.house.gov/member_info/electionInfo/2020/statistics2020.pdf), PDF p.59: all 5 equal |
| 2020 president (10001) | Trump/Pence REP 1,020,280; Biden/Harris DEM 503,890; Jorgensen/Cohen LIB 24,731; three IND tickets 11,798 | 1,560,699 | 280,885 / 167,185 / 1,112,629 | House Clerk 2020, PDF p.59: all 4 party groups equal |

OKER labels all three elections "Official Results" (`isOfficial: true`). Its server last-update stamps are 2024-11-08T17:49:51.517, 2022-12-05T15:59:50.77 and 2020-11-06T18:33:42.417, with no timezone printed. The 2022 stamp is later than the others; its Senate totals still equal the House Clerk's, and no cause is assigned. County certification was not checked separately against 77 county election board certificates.

## Contest votes, voter-history credits and registration are different measures

**Contest votes** are OKER candidate totals, split by OSEB's three methods: absentee mail, early (in-person absentee) and election day. OKER's exports and JSON carry **no ballots-cast, undervote, overvote or registration counts at any geography**. The fields inspected were candidate votes by method and precinct counts. OKER's "STATEWIDE TURNOUT" pie shows 64.42007% (2024), 50.34662% (2022) and 69.34186% (2020). It defines neither numerator nor denominator. The one county view tested (Oklahoma County, code 55; response not retained) repeated the statewide value. It is retained as a display value only and is not used. [Validation: field checks](data/turnout/validation.json).

**Voter-history credits** come from OSEB's Interactive Statistics (EIS) "Voter History Credit By County" dashboard. They are the closest official county participation count retrieved. The [EIS Guide (10/2023)](https://stats.okelections.gov/Home/EISGuide) defines a credit as "the record of a voter's participation in an election", attributed to the county where the voter was assigned when the credit was recorded. EIS statistics are recalculated monthly, so these values are the 2026-10-18 vintage. **They are not tabulated ballots.** In several counties the contest votes exceed the credits: in the 2022 special Senate, Noble has 3,804 votes against 3,144 credits (−660) and Payne −321, among 9 such counties. Never subtract contest votes from credits to estimate undervotes. [Differences ledger](data/turnout/participation-differences.json).

| Election | EIS credits | Absentee / Early Voting / Election Day | Credits minus highest-volume contest |
| --- | ---: | --- | --- |
| 2024-11-05 | 1,575,048 | 107,549 / 293,918 / 1,173,581 | +8,875 vs president; 4 counties below president votes |
| 2022-11-08 | 1,153,911 | 71,680 / 132,402 / 949,829 | +627 vs governor (16 counties below); +3,430 vs special Senate (9 below) |
| 2020-11-03 | 1,569,307 | 287,010 / 167,132 / 1,115,165 | +8,608 vs president; 9 counties below |

Ranking by credits reproduces each election's contest-vote sets exactly. The 2024 credits give the same 25 counties (80.1064475495%). The 2022 credits give the same 25 as the 2022 Senate contests (80.4224069274%). The 2020 credits give the same 26 as 2020 (80.9536948475%).

**Registration** comes from OSEB's official pre-election "Current Registration Statistics by County" reports, as of November 1 of each year. All three were located through the [registration-statistics archive](https://oklahoma.gov/elections/voter-registration/voter-registration-statistics/voter-registration-statistics-archive.html). The reports give **2,442,211** (2024, run 11/1/2024 9:39 AM), **2,295,906** (2022, run 3:09 AM) and **2,259,113** (2020, run 3:07 AM). **Every county total equals the EIS month-end (10/31) active + inactive snapshot.** EIS supplies the status split: 2,095,952 active + 346,259 inactive in 2024; 2,021,787 + 274,119 in 2022; 2,021,852 + 237,261 in 2020. OSEB's [November 4, 2024 release](https://oklahoma.gov/elections/newsroom/2024/november/oklahoma-voter-registration-numbers-surpass-2-4-million-ahead-of.html) prints the same 2024 and 2020 totals. The latest EIS snapshot, **2026-09-30**, shows 2,070,978 active + 375,647 inactive = 2,446,625. It predates the 2026 pre-election report and is not an election-day roll. Registration is a stock of records at a date, not the eligible population. No turnout rate is computed from it. [2024 county report](https://oklahoma.gov/content/dam/ok/en/elections/voter-registration-statistics/2024-vr-statistics/vrstats-county-nov1-2024.pdf), [2022](https://oklahoma.gov/content/dam/ok/en/elections/voter-registration-statistics/2022-vr-statistics/vrstats-county-nov1-2022.pdf), [2020](https://oklahoma.gov/content/dam/ok/en/elections/voter-registration-statistics/2020-vr-statistics/vrstatsbycounty-11012020.pdf).

## Reporting units: two countywide absentee/early units

OKER's precinct exports also reconcile exactly to the county totals for every county, candidate and method. Each precinct export has two more units than the race's precinct count: 1,986 vs 1,984 in 2024 and 2022, and 1,950 vs 1,948 in 2020. The two extras are **`559999` (Oklahoma County)** and **`729999` (Tulsa County)**. Each holds **all of its county's absentee-mail and early votes and zero election-day votes**, and the geographic precincts in those two counties carry election-day votes only. In the other 75 counties, absentee and early votes sit on the precinct rows. These two units have no precinct polygon. Live or historical comparisons in the two largest counties must therefore pair like slices: precinct rows are election-day-only, and the 9999 unit holds the county's absentee and early votes. [Unit ledger](data/turnout/reporting-units.json).

| Contest | 559999 Oklahoma County (absentee / early = total) | 729999 Tulsa County (absentee / early = total) |
| --- | --- | --- |
| 2024 president | 34,598 / 30,995 = 65,593 | 18,158 / 25,947 = 44,105 |
| 2022 Senate special | 23,476 / 20,928 = 44,404 | 12,856 / 16,278 = 29,134 |
| 2020 Senate | 86,652 / 16,080 = 102,732 | 60,568 / 13,297 = 73,865 |

## Files, provenance and reproduction

- [county-turnout.csv](data/county-turnout.csv): 77 rows ordered by 2024 rank, keyed by five-character `county_fips`. Columns:
  - Identity: `county`, `census_county_name`, `oseb_county_code` (OSEB 01–77), `oker_county_label`, `eis_county_label`.
  - Contest votes: `<contest>_contest_votes` with method splits. Contests are `pres2024`, `sen2022s` (special, same seat), `sen2022r` (regular, other seat), `gov2022`, `sen2020` and `pres2020`. Also exact `_share_pct`/`_cumulative_pct` strings at 10 decimals, `_rank`, and `_top15`/`_min80` flags.
  - Voter-history credits: `vh<year>_*` with method splits.
  - Registration: `reg<yyyymmdd>_active/_inactive/_total` from EIS month-end snapshots. The 10/31 totals equal the official November 1 reports county by county.
  - Blank never stands for zero; no blanks occur.
- [county-candidate-method.csv](data/turnout/county-candidate-method.csv): all 2,156 county × candidate rows for the six contests, with native OKER labels.
- [priority-set.json](data/turnout/priority-set.json): full order, cumulative sums, top 15, minimum 80% set with proof and remainder, comparisons, union and fixed-set coverage for nine measures.
- [validation.json](data/turnout/validation.json): **164 checks, all passing.** They cover:
  - SHA-256 and size of every stored file, all under 40 MB.
  - A 77-county Census FIPS join by normalized name. The only label difference is OKER/EIS `LeFlore` vs Census `Le Flore County`. Census county code = 2 × OSEB code − 1 holds for all 77 as a consistency check, not a join key.
  - Method arithmetic, county-to-state sums and the separate county-results JSON.
  - Precinct-to-county reconciliation and the 9999-unit allocation.
  - Federal certified totals, re-extracted from the PDFs.
  - EIS card, pie, method, affiliation and county totals.
  - Official November 1 report county totals against EIS.
  - Exact 80% integer proofs, and this report's embedded table and relative links.
- [source-manifest.json](data/turnout/source-manifest.json): 73 records with requested URLs, redirect chains (`results.okelections.us` → `.gov`, `stats.okelections.us` → `.gov`), status, headers (cookies and CloudFront request IDs/edge locations removed), UTC times and original/stored SHA-256 and sizes. The 21 OKER export and app-data records carry a `capture` field marking them as the retained one-time capture. Raw bytes are in [raw/](data/turnout/raw/): text types are gzip with mtime 0; ZIP and PDF files are stored as downloaded. The total is 5.9 MB (5,870,031 bytes).
- [acquire.py](data/turnout/acquire.py) re-fetches the public sources: OSEB pages, the public OKER app page, EIS, Census, NARA and the House Clerk. **It does not re-acquire the 21 OKER export and app-data records.** Those are a retained one-time capture (2026-10-18). A fresh run verifies them by SHA-256, carries their manifest records forward and prints a SKIP line for each. Re-acquisition by script is intentionally not supported; a person can re-download the exports by hand from the app's Export tab in a browser. [build.py](data/turnout/build.py) rebuilds and validates offline from the retained files. Run from the repository root:
  - `PYTHONDONTWRITEBYTECODE=1 uv run python3 -I senate/2026/oklahoma/data/turnout/acquire.py --verify` (offline hash check of every file)
  - `PYTHONDONTWRITEBYTECODE=1 uv run python3 -I senate/2026/oklahoma/data/turnout/acquire.py` (refetch public sources only)
  - `PYTHONDONTWRITEBYTECODE=1 uv run --with pypdf==6.21.1 python3 -I senate/2026/oklahoma/data/turnout/build.py`

  Acquisition uses only the standard library. pypdf is used only to re-read the certified PDFs and the registration reports.

**Access notes, as tested 2026-10-18.** These matter for election-night automation:
- OKER and EIS sit behind load balancers that return 403 to non-browser user agents. `Mozilla/5.0 (compatible; election-research/1.0)` is accepted.
- The OKER app's exports are behind an app-level sign-in. This package fetches public pages only; the OKER exports are the retained one-time capture described above.
- Export ZIPs are generated per request. Their containers change each time, but member CSVs were byte-identical across two requests about 18 minutes apart (member hashes are in `validation.json`).
- EIS data is reached through its DevExpress dashboard endpoint with an explicit Election Date or Statistics Date master filter. Each request's query is retained in the manifest.

None of this is a demonstrated November 2026 publication channel or cadence.

## Gaps and limits

- **No official county ballots-cast integer** was found in OKER, the election pages or EIS. Voter-history credits are a different, revisable measure (see above). Undervotes and overvotes are not published in these exports and are not inferred.
- Registration is a pre-election (November 1) snapshot, not an election-day roll. The 2026 pre-election report did not yet exist at retrieval, so 2026-09-30 is the latest snapshot.
- Statewide totals have federal certified controls, but **county allocations rest on OSEB's official OKER exports alone**. Three OKER paths agree: county CSV, precinct CSV and county JSON. The 77 county election board certificates and OSEB's own certification document were not retrieved.
- The 2022 governor's race has no independent statewide control here.
- The OKER exports cannot be refreshed by script. A later refresh, or any check for post-capture revisions, needs a person to re-download them by hand from the app's Export tab.
- 2020 contests are context only. Current 2026 precinct geography and crosswalks are outside this assignment. The two 9999 units will need explicit handling by the maps and official-results work.

## Complete descending order

All values are exact official integers. Share and cumulative percentages are rounded for display only; the CSV keeps 10 decimals and raw integers. "80% set" marks the 2024 minimum set. Kay (rank 26) belongs to every 2022 and 2020 minimum set. Registration is the EIS 2024-10-31 snapshot, which equals the official November 1, 2024 county report.

| Rank | County | FIPS | 2024 president votes | Share | Cumulative | 80% set | 2022 special Senate votes | 2022 special rank | 2022 regular Senate votes | 2024 voter-history credits | Registered 2024-10-31 (active + inactive) |
| ---: | --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | Oklahoma | 40109 | 288,923 | 18.4477% | 18.4477% | yes | 221,862 | 1 | 221,996 | 290,868 | 471,129 |
| 2 | Tulsa | 40143 | 256,939 | 16.4055% | 34.8532% | yes | 193,425 | 2 | 193,538 | 258,892 | 402,547 |
| 3 | Cleveland | 40027 | 119,294 | 7.6169% | 42.4701% | yes | 91,035 | 3 | 91,085 | 120,932 | 183,522 |
| 4 | Canadian | 40017 | 73,074 | 4.6658% | 47.1359% | yes | 50,059 | 4 | 50,097 | 73,443 | 107,072 |
| 5 | Rogers | 40131 | 46,902 | 2.9947% | 50.1306% | yes | 33,894 | 5 | 33,876 | 47,025 | 66,543 |
| 6 | Wagoner | 40145 | 38,501 | 2.4583% | 52.5889% | yes | 26,841 | 6 | 26,823 | 38,680 | 54,510 |
| 7 | Comanche | 40031 | 34,284 | 2.1890% | 54.7779% | yes | 23,500 | 7 | 23,550 | 34,475 | 63,933 |
| 8 | Creek | 40037 | 31,312 | 1.9993% | 56.7772% | yes | 22,304 | 8 | 22,303 | 31,452 | 45,861 |
| 9 | Payne | 40119 | 29,279 | 1.8695% | 58.6467% | yes | 22,073 | 9 | 22,098 | 29,454 | 46,729 |
| 10 | Pottawatomie | 40125 | 28,774 | 1.8372% | 60.4839% | yes | 20,675 | 10 | 20,684 | 28,933 | 43,772 |
| 11 | Grady | 40051 | 25,283 | 1.6143% | 62.0982% | yes | 17,804 | 11 | 17,798 | 25,326 | 36,895 |
| 12 | Muskogee | 40101 | 24,357 | 1.5552% | 63.6534% | yes | 17,782 | 12 | 17,764 | 24,418 | 39,147 |
| 13 | Logan | 40083 | 24,149 | 1.5419% | 65.1953% | yes | 16,977 | 14 | 16,979 | 24,342 | 34,849 |
| 14 | Washington | 40147 | 23,174 | 1.4797% | 66.6749% | yes | 17,086 | 13 | 17,098 | 23,324 | 35,916 |
| 15 | Garfield | 40047 | 21,844 | 1.3947% | 68.0697% | yes | 16,181 | 15 | 16,186 | 21,947 | 34,703 |
| 16 | McClain | 40087 | 21,397 | 1.3662% | 69.4359% | yes | 15,012 | 17 | 15,028 | 21,434 | 29,967 |
| 17 | Osage | 40113 | 20,628 | 1.3171% | 70.7530% | yes | 15,084 | 16 | 15,078 | 20,732 | 30,264 |
| 18 | Carter | 40019 | 19,488 | 1.2443% | 71.9973% | yes | 13,385 | 19 | 13,381 | 19,508 | 32,101 |
| 19 | Le Flore | 40079 | 18,754 | 1.1974% | 73.1947% | yes | 12,121 | 25 | 12,105 | 18,798 | 30,315 |
| 20 | Stephens | 40137 | 18,620 | 1.1889% | 74.3836% | yes | 13,092 | 21 | 13,107 | 18,690 | 28,707 |
| 21 | Delaware | 40041 | 18,108 | 1.1562% | 75.5398% | yes | 13,205 | 20 | 13,191 | 18,211 | 28,200 |
| 22 | Cherokee | 40021 | 17,823 | 1.1380% | 76.6778% | yes | 13,517 | 18 | 13,511 | 17,935 | 28,909 |
| 23 | Bryan | 40013 | 17,812 | 1.1373% | 77.8151% | yes | 11,457 | 26 | 11,451 | 17,827 | 29,178 |
| 24 | Pittsburg | 40121 | 17,572 | 1.1220% | 78.9371% | yes | 12,688 | 22 | 12,671 | 17,631 | 28,116 |
| 25 | Mayes | 40097 | 17,374 | 1.1093% | 80.0464% | yes | 12,642 | 23 | 12,627 | 17,438 | 25,684 |
| 26 | Kay | 40071 | 16,913 | 1.0799% | 81.1263% |  | 12,499 | 24 | 12,506 | 16,953 | 26,794 |
| 27 | Sequoyah | 40135 | 15,583 | 0.9950% | 82.1213% |  | 10,256 | 30 | 10,244 | 15,635 | 25,238 |
| 28 | Lincoln | 40081 | 15,465 | 0.9874% | 83.1087% |  | 11,085 | 28 | 11,084 | 15,540 | 22,196 |
| 29 | Pontotoc | 40123 | 15,174 | 0.9689% | 84.0776% |  | 11,166 | 27 | 11,191 | 15,208 | 23,956 |
| 30 | Okmulgee | 40111 | 14,349 | 0.9162% | 84.9937% |  | 10,624 | 29 | 10,619 | 14,382 | 22,238 |
| 31 | McCurtain | 40089 | 11,309 | 0.7221% | 85.7158% |  | 8,256 | 31 | 8,230 | 11,350 | 17,754 |
| 32 | Ottawa | 40115 | 11,178 | 0.7137% | 86.4295% |  | 7,678 | 33 | 7,670 | 11,228 | 18,947 |
| 33 | Garvin | 40049 | 10,991 | 0.7018% | 87.1313% |  | 8,114 | 32 | 8,108 | 10,990 | 16,683 |
| 34 | Custer | 40039 | 10,168 | 0.6492% | 87.7805% |  | 7,487 | 34 | 7,493 | 10,175 | 15,949 |
| 35 | Caddo | 40015 | 9,496 | 0.6063% | 88.3869% |  | 7,052 | 35 | 7,052 | 9,530 | 14,716 |
| 36 | McIntosh | 40091 | 8,439 | 0.5388% | 88.9257% |  | 6,460 | 36 | 6,444 | 8,478 | 13,054 |
| 37 | Jackson | 40065 | 8,053 | 0.5142% | 89.4399% |  | 5,486 | 38 | 5,497 | 8,033 | 13,789 |
| 38 | Seminole | 40133 | 8,044 | 0.5136% | 89.9535% |  | 5,864 | 37 | 5,858 | 8,062 | 13,184 |
| 39 | Beckham | 40009 | 7,678 | 0.4902% | 90.4437% |  | 5,470 | 39 | 5,468 | 7,684 | 12,082 |
| 40 | Woodward | 40153 | 7,312 | 0.4669% | 90.9106% |  | 5,374 | 40 | 5,383 | 7,322 | 11,440 |
| 41 | Adair | 40001 | 7,256 | 0.4633% | 91.3739% |  | 5,227 | 41 | 5,195 | 7,272 | 11,667 |
| 42 | Pawnee | 40117 | 6,880 | 0.4393% | 91.8132% |  | 5,047 | 42 | 5,049 | 6,885 | 10,219 |
| 43 | Kingfisher | 40073 | 6,754 | 0.4312% | 92.2444% |  | 4,873 | 43 | 4,875 | 6,777 | 9,421 |
| 44 | Marshall | 40095 | 6,589 | 0.4207% | 92.6651% |  | 4,385 | 45 | 4,388 | 6,601 | 10,169 |
| 45 | Craig | 40035 | 6,056 | 0.3867% | 93.0518% |  | 4,481 | 44 | 4,472 | 6,078 | 8,800 |
| 46 | Murray | 40099 | 5,885 | 0.3758% | 93.4275% |  | 4,248 | 46 | 4,242 | 5,896 | 8,760 |
| 47 | Atoka | 40005 | 5,662 | 0.3615% | 93.7891% |  | 3,923 | 48 | 3,909 | 5,674 | 8,331 |
| 48 | Choctaw | 40023 | 5,639 | 0.3600% | 94.1491% |  | 4,040 | 47 | 4,036 | 5,649 | 9,355 |
| 49 | Texas | 40139 | 5,206 | 0.3324% | 94.4815% |  | 3,651 | 50 | 3,652 | 5,222 | 9,352 |
| 50 | Noble | 40103 | 4,957 | 0.3165% | 94.7980% |  | 3,804 | 49 | 3,811 | 4,963 | 7,135 |
| 51 | Haskell | 40061 | 4,936 | 0.3152% | 95.1132% |  | 3,386 | 53 | 3,385 | 4,952 | 7,240 |
| 52 | Pushmataha | 40127 | 4,702 | 0.3002% | 95.4134% |  | 3,287 | 55 | 3,282 | 4,709 | 7,222 |
| 53 | Hughes | 40063 | 4,659 | 0.2975% | 95.7109% |  | 3,548 | 52 | 3,538 | 4,666 | 7,286 |
| 54 | Washita | 40149 | 4,652 | 0.2970% | 96.0079% |  | 3,567 | 51 | 3,571 | 4,664 | 6,905 |
| 55 | Nowata | 40105 | 4,561 | 0.2912% | 96.2991% |  | 3,321 | 54 | 3,312 | 4,566 | 6,705 |
| 56 | Love | 40085 | 4,260 | 0.2720% | 96.5711% |  | 2,731 | 60 | 2,735 | 4,275 | 6,890 |
| 57 | Johnston | 40069 | 4,230 | 0.2701% | 96.8412% |  | 2,961 | 58 | 2,958 | 4,234 | 6,324 |
| 58 | Latimer | 40077 | 4,079 | 0.2604% | 97.1017% |  | 3,063 | 56 | 3,057 | 4,077 | 6,292 |
| 59 | Okfuskee | 40107 | 3,988 | 0.2546% | 97.3563% |  | 2,938 | 59 | 2,937 | 4,022 | 6,353 |
| 60 | Blaine | 40011 | 3,786 | 0.2417% | 97.5980% |  | 2,965 | 57 | 2,969 | 3,805 | 5,621 |
| 61 | Woods | 40151 | 3,638 | 0.2323% | 97.8303% |  | 2,699 | 61 | 2,699 | 3,654 | 5,139 |
| 62 | Major | 40093 | 3,478 | 0.2221% | 98.0524% |  | 2,688 | 62 | 2,690 | 3,494 | 4,716 |
| 63 | Kiowa | 40075 | 3,278 | 0.2093% | 98.2617% |  | 2,455 | 63 | 2,458 | 3,284 | 4,975 |
| 64 | Coal | 40029 | 2,538 | 0.1621% | 98.4237% |  | 1,891 | 64 | 1,885 | 2,549 | 3,945 |
| 65 | Tillman | 40141 | 2,533 | 0.1617% | 98.5855% |  | 1,840 | 65 | 1,844 | 2,543 | 4,114 |
| 66 | Cotton | 40033 | 2,506 | 0.1600% | 98.7455% |  | 1,830 | 66 | 1,843 | 2,517 | 3,883 |
| 67 | Jefferson | 40067 | 2,375 | 0.1516% | 98.8971% |  | 1,599 | 70 | 1,608 | 2,389 | 3,645 |
| 68 | Dewey | 40043 | 2,215 | 0.1414% | 99.0385% |  | 1,757 | 67 | 1,764 | 2,227 | 3,108 |
| 69 | Alfalfa | 40003 | 2,160 | 0.1379% | 99.1765% |  | 1,733 | 68 | 1,735 | 2,176 | 3,065 |
| 70 | Grant | 40053 | 2,125 | 0.1357% | 99.3121% |  | 1,594 | 71 | 1,596 | 2,128 | 2,954 |
| 71 | Beaver | 40007 | 2,124 | 0.1356% | 99.4478% |  | 1,690 | 69 | 1,681 | 2,123 | 3,254 |
| 72 | Greer | 40055 | 1,836 | 0.1172% | 99.5650% |  | 1,339 | 73 | 1,342 | 1,840 | 2,954 |
| 73 | Ellis | 40045 | 1,812 | 0.1157% | 99.6807% |  | 1,484 | 72 | 1,486 | 1,818 | 2,603 |
| 74 | Roger Mills | 40129 | 1,733 | 0.1107% | 99.7913% |  | 1,317 | 74 | 1,314 | 1,745 | 2,428 |
| 75 | Harper | 40059 | 1,451 | 0.0926% | 99.8840% |  | 1,167 | 75 | 1,166 | 1,461 | 1,961 |
| 76 | Cimarron | 40025 | 935 | 0.0597% | 99.9437% |  | 731 | 76 | 729 | 942 | 1,406 |
| 77 | Harmon | 40057 | 882 | 0.0563% | 100.0000% |  | 649 | 77 | 647 | 886 | 1,425 |
