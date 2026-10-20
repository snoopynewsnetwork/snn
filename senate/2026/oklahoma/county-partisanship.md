# Oklahoma county partisanship and conditional targets

Research snapshot: 2026-10-18 UTC (sources retrieved 2026-10-18T16:42:53Z to 2026-10-18T16:43:41Z). **Every recent Oklahoma baseline is Republican, and none is close.** In the same-seat 2022 special Senate contest, Markwayne Mullin led Kendra Horn by **305,254** votes on **1,116,032** D+R votes, a D-minus-R pair margin of **-27.3517 margin points**. At those county weights, a uniform **+13.675862 D-share points** ties, and **+14.175862 share points** gives an illustrative **D+1 pair margin**. In margin terms that is 27.3517 points to tie and 28.3517 points for D+1. Oklahoma County was the only county Horn carried. These are deterministic what-if calculations on historical counts (secondary county transcriptions reconciled to official statewide totals), not a 2026 forecast. A gain in one county can offset a shortfall in another, so no county target is a necessary condition on its own. Statewide totals: [House Clerk 2022](https://clerk.house.gov/member_info/electionInfo/2022/statistics2022.pdf); county values: [county-contests.csv](data/baselines/county-contests.csv).

Oklahoma had **no 2024 Senate contest**. 2022 had two distinct Senate contests on one ballot: the **special** election for the Class II unexpired term ending January 3, 2027 (Mullin–Kendra Horn), which is the same seat as 2026, and the **regular** Class III election (Lankford–Madison Horn). They are kept as separate contests here and never added together. The 2020 Inhofe–Broyles contest is the previous regular election for the same Class II seat and is labeled as history. The 2024 presidential and 2022 governor results are comparators, not Senate results.

## 2026 contest and verified slate

The U.S. Senate [Class II roster](https://www.senate.gov/senators/Class_II.htm) (retrieved 2026-10-18T16:43:41Z) lists **Armstrong, Alan (R-OK)** as the current holder. News 9 reports that the Senate confirmed Mullin as Secretary of Homeland Security on March 23, 2026; that Gov. Kevin Stitt appointed Armstrong on an interim basis; and that Armstrong cannot run for the seat ([News 9, Oct. 2, 2026](https://www.news9.com/oklahoma-politics/oklahoma-us-senate-election-candidates-2026)). The State Election Board's [UOCAVA notice for November 3, 2026](https://oklahoma.gov/elections/voters/military-overseas-voters/2026-election-notice-general-election.html) lists **"U.S. Senator (1 office)"** without the special-election label it gives State Senate District 17. News 9 writes that the November election fills both the remainder of the vacancy and the next six-year term. This package does not resolve that statutory point. It does not affect the vote arithmetic below.

Official filings: the SEB [2026 candidate list book](https://oklahoma.gov/content/dam/ok/en/elections/candidate-filing-archives/2026-candidate-filing-archives/2026-candidate-list-book.pdf) (filings April 1–3, 2026; page 3) and the SEB [filing portal](https://filings.okelections.gov/ViewCandidates/2026040120260403/99/all) ([U.S. Senator JSON](data/baselines/raw/seb-filings-us-senator/GetCandList-OfficeID-2257.json.gz), retrieved 2026-10-18T16:43:40Z) both list the same **13 filers**. No filer is marked removed. The SEB [withdrawal list](https://oklahoma.gov/elections/candidates/2026-candidate-filing-information/2026-candidate-withdrawals.html) and [contest-of-candidacy list](https://oklahoma.gov/elections/candidates/2026-candidate-filing-information/2026-contests-of-candidacy.html) contain no U.S. Senator entries.

| Filing ID | Candidate | Filed affiliation | Route to November ballot | Evidence |
| --- | --- | --- | --- | --- |
| 274 | Kevin Hern | Republican | Won June 16 Republican primary outright | SEB filings; newsroom primary/runoff reports |
| 374 | Sean Buckner | Republican | Did not advance from June 16 primary | SEB filings; newsroom primary/runoff reports |
| 387 | Brian Ragain | Republican | Did not advance from June 16 primary | SEB filings; newsroom primary/runoff reports |
| 492 | Nick Hankins | Republican | Did not advance from June 16 primary | SEB filings; newsroom primary/runoff reports |
| 601 | Gary Ty England | Republican | Did not advance from June 16 primary | SEB filings; newsroom primary/runoff reports |
| 443 | Troy W. Green | Democrat | Did not advance from June 16 primary | SEB filings; newsroom primary/runoff reports |
| 475 | Jim Priest | Democrat | Lost August 25 Democratic runoff | SEB filings; newsroom primary/runoff reports |
| 539 | R.O. Joe Cassity Jr. | Democrat | Did not advance from June 16 primary | SEB filings; newsroom primary/runoff reports |
| 559 | N'Kiyla Jasmine Thomas | Democrat | Won August 25 Democratic runoff over Jim Priest | SEB filings; newsroom primary/runoff reports |
| 605 | Ervin Stone Yen | Democrat | Did not advance from June 16 primary | SEB filings; newsroom primary/runoff reports |
| 592 | Sevier White | Libertarian | Sole Libertarian filer; no primary | SEB filings |
| 497 | Curtis Stinnett | Independent | Independent; no primary | SEB filings |
| 565 | Ron Meinhardt | Independent | Independent; no primary | SEB filings |

**Expected November ballot: Kevin Hern (REP), N'Kiyla Jasmine Thomas (DEM), Sevier White (LIB), Curtis Stinnett (IND), Ron Meinhardt (IND).** The nomination results are from newsrooms, not from official counts retrieved here. KOKH reports the AP call for Thomas over Priest on August 25 ([KOKH](https://okcfox.com/news/local/nkiyla-thomas-wins-democratic-nomination-for-us-senate-in-oklahoma)). News 9 reports Thomas at 61.2% in the runoff and 45.2% in the June primary, Hern's outright primary win, and the five-candidate November field ([News 9](https://www.news9.com/oklahoma-politics/oklahoma-us-senate-election-candidates-2026)). Official primary and runoff counts are published only through the SEB OK Election Results application, which this package did not query (see Gaps).

Coalition caveats for 2026:

- **Two independents and a Libertarian are on the ballot.** None is assigned to either party. News 9 describes Meinhardt as a registered Republican running as an independent against the Republican nominee. Any 2026 vote he wins is a separate 'other' quantity, not R and not D.
- Kevin Hern won Oklahoma's 1st District House seat in 2024; the House Clerk 2024 publication lists him with 188,832 votes. News 9 describes Thomas as making her first run for public office. No historical Oklahoma statewide contest had either candidate, so candidate effects are not carried into the scenarios.
- Kendra Horn, the 2022 special Democrat, appears as the 2020 District 5 Democrat ("Kendra S. Horn") in the [House Clerk 2020 publication](https://clerk.house.gov/member_info/electionInfo/2020/statistics2020.pdf). Madison Horn, the 2022 regular Democrat, appears as the 2024 District 5 Democrat in [Clerk 2024](https://clerk.house.gov/member_info/electionInfo/2024/statistics2024.pdf).
- Joy Hofmeister, the 2022 Democratic governor nominee, was the sitting State Superintendent and left the Republican Party in October 2021 to run as a Democrat ([Public Radio Tulsa](https://www.publicradiotulsa.org/post/state-superintendent-hofmeister-switches-parties-run-governor)). Her result is a candidate-specific midterm comparator, not evidence of a Democratic Senate floor.
- Ervin Stone Yen ran for governor in 2022 as an independent (15,653 votes) and filed as a Democrat for Senate in 2026. His 2022 votes stay 'other'.

## Sources, access and status

The SEB year pages for [2020](https://oklahoma.gov/elections/elections-results/election-results/2020-election-results/2020-november-general-election.html), [2022](https://oklahoma.gov/elections/elections-results/election-results/2022-election-results/2022-november-general-election.html) and [2024](https://oklahoma.gov/elections/elections-results/election-results/2024-election-results/november-general-election.html) link only to the OK Election Results (OKER) application. The 2022 page says downloadable data come from that application's Export tab. OKER is a JavaScript client. It loads results, including the county and precinct CSV/XML exports, from an API only after an application login. **This package does not use that API.** As a result, no county count here is a newly downloaded SEB export.

County counts come from pinned secondary transcriptions of SEB exports. In each case, statewide candidate totals are reconciled to official publications:

- **2022 (both Senate contests and governor):** [MEDSL 2022 Oklahoma precinct file](https://raw.githubusercontent.com/MEDSL/2022-elections-official/a8126c5790b8d1f438a3e63c3506cdcdc7406d9f/individual_states/2022-ok-local-precinct-general.zip), commit `a8126c5`. The MEDSL README says it was added 2022-12-27, with source `results.okelections.us/OKER/?elecDate=20221108`. Methods are ABSENTEE, EARLY and IN-PERSON; there is no TOTAL row, so all three are summed.
- **2024 president:** [MEDSL 2024 Oklahoma file](https://raw.githubusercontent.com/MEDSL/2024-elections-official/df531089c78e6d0098db1a6bfb3849a066a06995/individual_states/ok24.zip), commit `df53108`. The README says it was added 2024-11-14 from `results.okelections.gov/OKER/?elecDate=20241105`; the CSV inside the ZIP is dated 2026-04-28. The file has both split modes and a TOTAL row. Only TOTAL is used. Every one of the 9,930 precinct-candidate TOTAL values equals the sum of its three split modes.
- **2020 Senate:** [OpenElections 2020 county file](https://raw.githubusercontent.com/openelections/openelections-data-ok/76320f6588780002f8c0beb4acd641cf019b0489/2020/20201103__ok__general__county.csv), commit `76320f6`, with absentee, early and election-day columns. Its [precinct file](https://raw.githubusercontent.com/openelections/openelections-data-ok/76320f6588780002f8c0beb4acd641cf019b0489/2020/20201103__ok__general__precinct.csv) aggregates exactly to the county file in all 385 county-candidate cells.

Official statewide controls:

- **House Clerk** statistics of the [2020](https://clerk.house.gov/member_info/electionInfo/2020/statistics2020.pdf) (PDF page 59), [2022](https://clerk.house.gov/member_info/electionInfo/2022/statistics2022.pdf) (page 41) and [2024](https://clerk.house.gov/member_info/electionInfo/2024/statistics2024.pdf) (page 57) elections. These print every Senate candidate. For 2024 president they print party lines, with all independent tickets combined.
- **SEB OKER statewide JSON, as archived by the Internet Archive:** [2020](https://web.archive.org/web/20250629165738id_/https://results.okelections.gov/OKERS/enrapi/getelec/20201103/SW/xx) is labeled `Official Results` with `isOfficial=True` and server time 2020-11-06T18:33:42.417. It includes absentee, early and election-day columns. [2024](https://web.archive.org/web/20241106133100id_/https://results.okelections.gov/OKERS/enrapi/getelec/20241105/SW/xx) is the election-night `Unofficial Results` capture (`isOfficial=False`, server time 2024-11-06T00:45:47.467). It is kept only as a vintage comparison.

Agreement on statewide totals is necessary but does not prove that each county allocation is right. The 2020 precinct file is from the same project, so it is an internal check, not an independent county source. There is **no primary statewide control for the 2022 governor contest**; its county counts are unreconciled secondary data, used as context only. Every URL, retrieval time, HTTP status, header subset, byte count and SHA-256 is in [sources.json](data/baselines/sources.json). Raw bytes are under [raw/](data/baselines/raw/).

## Statewide reconciliation and baselines

Counts below are votes for named candidates in each contest. Oklahoma prints no write-in line, and these files do not report under- or overvotes or ballots cast. D share and pair margin use D+R only. 'D counties' is the number of counties where the Democrat led in that contest.

| Contest | D candidate | R candidate | D | R | Other | All candidates | Clerk diff | SEB archive diff | D pair share % | D−R pair margin pp | D counties |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- | ---: | ---: | ---: |
| 2022 Senate special (Class II) | Kendra Horn | Markwayne Mullin | 405,389 | 710,643 | 34,449 | 1,150,481 | 0 for all 4 | not archived | 36.3241 | -27.3517 | 1 |
| 2022 Senate regular (Class III) | Madison Horn | James Lankford | 369,370 | 739,960 | 41,402 | 1,150,732 | 0 for all 4 | not archived | 33.2967 | -33.4067 | 0 |
| 2020 Senate (Class II history) | Abby Broyles | Jim Inhofe | 509,763 | 979,140 | 67,458 | 1,556,361 | 0 for all 5 | 0 for all 5, incl. methods | 34.2375 | -31.5250 | 0 |
| 2024 president | Kamala D. Harris | Donald J. Trump | 499,599 | 1,036,213 | 30,361 | 1,566,173 | 0 for D, R, LIB and combined IND | election-night vintage; see CSV | 32.5300 | -34.9401 | 0 |
| 2022 governor | Joy Hofmeister | Kevin Stitt | 481,904 | 639,484 | 31,896 | 1,153,284 | no control | not archived | 42.9739 | -14.0522 | 3 |

Every named candidate is kept separately in [county-candidates.csv](data/baselines/county-candidates.csv) with absentee, early, election-day and total columns:

- **2022 Senate special (Class II):** Kendra Horn (DEM) 405,389; Markwayne Mullin (REP) 710,643; Ray Woods (IND) 17,063; Robert Murphy (LIB) 17,386.
- **2022 Senate regular (Class III):** Madison Horn (DEM) 369,370; James Lankford (REP) 739,960; Michael L. Delaney (IND) 20,907; Kenneth D. Blevins (LIB) 20,495.
- **2020 Senate (Class II history):** Abby Broyles (DEM) 509,763; Jim Inhofe (REP) 979,140; A. D. Nesbit (IND) 11,371; Joan Farr (IND) 21,652; Robert Murphy (LIB) 34,435.
- **2024 president:** Kamala D. Harris (DEM) 499,599; Donald J. Trump (REP) 1,036,213; Chris Garrity (IND) 5,143; Robert F. Kennedy Jr. (IND) 16,020; Chase Oliver (LIB) 9,198.
- **2022 governor:** Joy Hofmeister (DEM) 481,904; Kevin Stitt (REP) 639,484; Ervin Stone Yen (IND) 15,653; Natalie Bruno (LIB) 16,243.

Against the election-night 2024 SEB capture, the final county sums are higher by Kamala D. Harris +556, Donald J. Trump +996, Chris Garrity +6, Robert F. Kennedy Jr. +28, Chase Oliver +14. These gaps are the expected difference between an unofficial election-night count and the final one. They are not treated as errors, and the final MEDSL sums match the Clerk. Machine-readable controls are in [state-controls.csv](data/baselines/state-controls.csv).

SEB county codes are the leading digits of SEB precinct IDs (`precinct // 10000`). They form one consistent one-to-one map onto 01–77 in all three precinct files. SEB numbering puts the Mc- counties before Major, so six codes differ from strict A–Z order: Major 47, Marshall 48, Mayes 49, McClain 44, McCurtain 45, McIntosh 46. The Census FIPS key comes from the [Census 2020 county list](https://www2.census.gov/geo/docs/reference/codes2020/cou/st40_ok_cou2020.txt). Precinct-ID counts in the transcriptions (2022: 1,986; 2024: 1,986; 2020: 1,950) include a few zero-vote IDs. They differ slightly from the archived SEB precinct counts (2020: 1,948; 2024 election night: 1,984). This package uses those counts only as context, not as geography.

## Share points, margin points and turnout

For county `c`, let `s_c = D_c/(D_c+R_c)`, `T_c` the scenario's D+R pool, and `M0 = Σ T_c(2s_c−1)` the baseline D−R net. A uniform additive D-share change `δ` gives net `M0 + 2δΣT_c`. Setting that to zero gives the tie shift `δ = −M0/(2ΣT) = (R−D)/(2(D+R))` at native weights. A **D+1 pair margin** needs net `0.01ΣT`, which is **0.5 share points more** than a tie. One D-share point equals **two D−R margin points**, which is `0.02·T_c` net votes in county `c`: each vote moved from R to D changes the net by two. The **all-candidate D+1** goal needs net `0.01ΣV`, where `V` includes the fixed Libertarian and independent votes, so it needs slightly more share than the pair D+1. Other candidates are held at their baseline county shares and are never reassigned. No baseline here is already Democratic, so every required shift is positive. If one were, the solver would report a zero or negative shift. The solver applies `clip(s_c+δ, 0, 1)` and re-solves if any county would leave [0, 1]. No actual scenario here clips; synthetic tests in the validator exercise clipping.

Turnout weights are kept separate from preferences. 'Native' uses each contest's own D+R counts. A cross mix uses another contest's actual all-candidate county volume `V_c`, times the preference contest's own county pair participation `(D+R)/A`. These are observed historical volume mixes, not 2026 turnout projections.

| Preference baseline | Volume mix | Pair pool | Baseline D−R net | Pair margin pp | Tie D-share shift pp | D+1 pair shift pp | D+1 all-candidate shift pp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2022 Senate special (Class II) | native-pair | 1,116,032.0 | -305,254.0 | -27.3517 | +13.675862 | +14.175862 | +14.191296 |
| 2022 Senate special (Class II) | 2024-president-volume | 1,519,247.1 | -426,526.0 | -28.0748 | +14.037413 | +14.537413 | +14.552857 |
| 2022 Senate special (Class II) | 2020-senate-volume | 1,509,746.4 | -416,654.0 | -27.5976 | +13.798806 | +14.298806 | +14.314244 |
| 2022 Senate regular (Class III) | native-pair | 1,109,330.0 | -370,590.0 | -33.4067 | +16.703325 | +17.203325 | +17.221986 |
| 2022 Senate regular (Class III) | 2022-senate-special-volume | 1,109,089.4 | -370,602.2 | -33.4150 | +16.707497 | +17.207497 | +17.226157 |
| 2022 Senate regular (Class III) | 2024-president-volume | 1,509,773.0 | -514,520.3 | -34.0793 | +17.039658 | +17.539658 | +17.558336 |
| 2022 Senate regular (Class III) | 2020-senate-volume | 1,500,375.4 | -504,372.4 | -33.6164 | +16.808206 | +17.308206 | +17.326863 |
| 2020 Senate (Class II history) | native-pair | 1,488,903.0 | -469,377.0 | -31.5250 | +15.762511 | +16.262511 | +16.285165 |
| 2020 Senate (Class II history) | 2022-senate-special-volume | 1,100,605.1 | -344,780.5 | -31.3264 | +15.663225 | +16.163225 | +16.185883 |
| 2020 Senate (Class II history) | 2024-president-volume | 1,498,323.5 | -479,521.7 | -32.0039 | +16.001940 | +16.501940 | +16.524582 |
| 2024 president | native-pair | 1,535,812.0 | -536,614.0 | -34.9401 | +17.470042 | +17.970042 | +17.979926 |
| 2024 president | 2022-senate-special-volume | 1,128,068.3 | -386,256.7 | -34.2405 | +17.120272 | +17.620272 | +17.630206 |
| 2024 president | 2020-senate-volume | 1,526,118.8 | -525,684.3 | -34.4458 | +17.222916 | +17.722916 | +17.732824 |
| 2022 governor | native-pair | 1,121,388.0 | -157,580.0 | -14.0522 | +7.026114 | +7.526114 | +7.540336 |
| 2022 governor | 2022-senate-special-volume | 1,118,660.6 | -157,351.3 | -14.0660 | +7.033021 | +7.533021 | +7.547244 |
| 2022 governor | 2024-president-volume | 1,522,657.3 | -223,613.1 | -14.6857 | +7.342856 | +7.842856 | +7.857146 |
| 2022 governor | 2020-senate-volume | 1,513,161.3 | -215,759.2 | -14.2588 | +7.129420 | +7.629420 | +7.643695 |

Changing the county volume mix moves the same-seat tie threshold by +0.1229 to +0.3616 share points (from +13.6759 at native 2022 weights to +14.0374 at the 2024 presidential mix and +13.7988 at the 2020 Senate mix). Composition matters far less than preference. The 2022 governor comparator, with a different Democratic candidate on the same 2022 ballot, sits about half as far from a tie (+7.0261). Treat this as a candidate effect, not a transferable floor. All 60 statewide scenarios are in [state-scenarios.csv](data/baselines/state-scenarios.csv); the 4,620 county targets are in [county-target-scenarios.csv](data/baselines/county-target-scenarios.csv).

Synthetic turnout sensitivity, holding 2022 special county preferences fixed. The multipliers are arbitrary, not researched 2026 turnout:

| Turnout scenario | Pair pool | Baseline net | Pair margin pp | Metro-3 pair weight % | Tie shift pp | D+1 shift pp |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| observed 2022 special pair volumes | 1,116,032.0 | -305,254.0 | -27.3517 | 44.017 | +13.675862 | +14.175862 |
| all counties x0.80 (uniform) | 892,825.6 | -244,203.2 | -27.3517 | 44.017 | +13.675862 | +14.175862 |
| all counties x1.20 (uniform) | 1,339,238.4 | -366,304.8 | -27.3517 | 44.017 | +13.675862 | +14.175862 |
| Oklahoma+Tulsa+Cleveland x1.10, others x1.00 | 1,165,156.8 | -306,742.2 | -26.3263 | 46.378 | +13.163130 | +13.663130 |
| Oklahoma+Tulsa+Cleveland x0.90, others x1.00 | 1,066,907.2 | -303,765.8 | -28.4716 | 41.440 | +14.235812 | +14.735812 |
| all except Oklahoma+Tulsa+Cleveland x1.10 | 1,178,510.4 | -334,291.2 | -28.3656 | 41.684 | +14.182785 | +14.682785 |
| all except Oklahoma+Tulsa+Cleveland x0.90 | 1,053,553.6 | -276,216.8 | -26.2176 | 46.628 | +13.108816 | +13.608816 |

Scaling every county by the same factor changes the net votes but not the share threshold. A 10% relative turnout change in Oklahoma, Tulsa and Cleveland counties ('metro-3') moves the tie threshold by -0.5127 to +0.5599 share points; the same change in the other 74 counties moves it -0.5670 to +0.5069. Both are small next to the 13.7-point gap. Metro-3 combined was close to even in the special (net -14,882), so extra metro votes mostly dilute the statewide margin rather than add Democratic net votes. See [turnout-sensitivity.csv](data/baselines/turnout-sensitivity.csv).

## Where the Republican margin comes from

- **2022 Senate special (Class II):** metro-3 (Oklahoma, Tulsa, Cleveland) supplied 44.02% of D+R votes and a net of -14,882. The other 74 counties supplied net -290,372, or 95.1% of the statewide net.
- **2020 Senate (Class II history):** metro-3 (Oklahoma, Tulsa, Cleveland) supplied 43.66% of D+R votes and a net of -53,941. The other 74 counties supplied net -415,436, or 88.5% of the statewide net.
- **2024 president:** metro-3 (Oklahoma, Tulsa, Cleveland) supplied 42.35% of D+R votes and a net of -61,778. The other 74 counties supplied net -474,836, or 88.5% of the statewide net.

In the 2022 special, the Republican net margin is spread widely. It takes the 16 largest Republican-net counties to pass 50% of it; the first 15 are listed below. Oklahoma County (D +4.41) offsets 9,513 votes. The contribution in points is county net divided by statewide D+R; the 77 values sum to the statewide pair margin.

| Rank | County | FIPS | D+R votes | Pair weight % | D−R net | Pair margin pp | Contribution to statewide margin pp | Share of statewide net % | Cumulative % |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Tulsa | 40143 | 187,595 | 16.809 | -19,561 | -10.43 | -1.7527 | 6.41 | 6.41 |
| 2 | Canadian | 40017 | 48,366 | 4.334 | -16,674 | -34.47 | -1.4940 | 5.46 | 11.87 |
| 3 | Rogers | 40131 | 32,858 | 2.944 | -16,416 | -49.96 | -1.4709 | 5.38 | 17.25 |
| 4 | Wagoner | 40145 | 26,061 | 2.335 | -11,893 | -45.64 | -1.0657 | 3.90 | 21.14 |
| 5 | Creek | 40037 | 21,631 | 1.938 | -10,859 | -50.20 | -0.9730 | 3.56 | 24.70 |
| 6 | Grady | 40051 | 17,332 | 1.553 | -9,174 | -52.93 | -0.8220 | 3.01 | 27.71 |
| 7 | Garfield | 40047 | 15,674 | 1.404 | -7,858 | -50.13 | -0.7041 | 2.57 | 30.28 |
| 8 | Washington | 40147 | 16,584 | 1.486 | -7,680 | -46.31 | -0.6882 | 2.52 | 32.80 |
| 9 | McClain | 40087 | 14,607 | 1.309 | -7,607 | -52.08 | -0.6816 | 2.49 | 35.29 |
| 10 | Stephens | 40137 | 12,649 | 1.133 | -7,565 | -59.81 | -0.6778 | 2.48 | 37.77 |
| 11 | Pottawatomie | 40125 | 20,014 | 1.793 | -7,560 | -37.77 | -0.6774 | 2.48 | 40.24 |
| 12 | Logan | 40083 | 16,452 | 1.474 | -7,356 | -44.71 | -0.6591 | 2.41 | 42.65 |
| 13 | Le Flore | 40079 | 11,813 | 1.058 | -7,267 | -61.52 | -0.6511 | 2.38 | 45.03 |
| 14 | Delaware | 40041 | 12,866 | 1.153 | -6,990 | -54.33 | -0.6263 | 2.29 | 47.32 |
| 15 | Pittsburg | 40121 | 12,391 | 1.110 | -6,433 | -51.92 | -0.5764 | 2.11 | 49.43 |
| 77 | Oklahoma | 40109 | 215,551 | 19.314 | +9,513 | +4.41 | +0.8524 | -3.12 | — |

Closeness bands use the absolute pair margin (≤5, >5–10, >10 pp) and appear in the CSVs. In the 2022 special, the only counties within 10 points were Oklahoma (+4.41) and Cleveland (-5.49).

## One county at a time, all others fixed

This holds every other county at its baseline preference and volume and solves for the D share the selected county alone would need: `(target − other_net + T_sel)/(2·T_sel)`. A value above 100% is impossible under those fixed assumptions. It shows that no single county can close the gap; it is not a plausible path.

| Preference / mix | County | Pair pool | Baseline D % | Tie D % needed | D+1 D % needed | Status |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 2022 Senate special (Class II) / native-pair | Oklahoma | 215,551.0 | 52.21 | 123.01 | 125.60 | impossible |
| 2022 Senate special (Class II) / native-pair | Tulsa | 187,595.0 | 44.79 | 126.15 | 129.12 | impossible |
| 2022 Senate special (Class II) / native-pair | Cleveland | 88,102.0 | 47.26 | 220.50 | 226.83 | impossible |
| 2022 Senate special (Class II) / native-pair | Canadian | 48,366.0 | 32.76 | 348.33 | 359.87 | impossible |
| 2022 Senate special (Class II) / 2024-president-volume | Oklahoma | 280,704.4 | 52.21 | 128.18 | 130.89 | impossible |
| 2022 Senate special (Class II) / 2024-president-volume | Tulsa | 249,194.6 | 44.79 | 130.37 | 133.42 | impossible |
| 2022 Senate special (Class II) / 2024-president-volume | Cleveland | 115,450.5 | 47.26 | 231.98 | 238.56 | impossible |
| 2022 Senate special (Class II) / 2024-president-volume | Canadian | 70,602.6 | 32.76 | 334.82 | 345.58 | impossible |
| 2020 Senate (Class II history) / native-pair | Oklahoma | 281,651.0 | 49.55 | 132.88 | 135.52 | impossible |
| 2020 Senate (Class II history) / native-pair | Tulsa | 254,238.0 | 42.82 | 135.13 | 138.06 | impossible |
| 2020 Senate (Class II history) / native-pair | Cleveland | 114,172.0 | 43.47 | 249.03 | 255.55 | impossible |
| 2020 Senate (Class II history) / native-pair | Canadian | 58,905.0 | 29.52 | 427.93 | 440.57 | impossible |

All rows are in [selected-county-break-even.csv](data/baselines/selected-county-break-even.csv). Because every baseline is far from a tie, live-night use should track the statewide pace across many counties, not wait on a single county.

## All 77 counties

Signed margins are observed **D−R pair-margin points**; positive means the Democrat led that historical contest. The scenario columns use 2022 special preferences at native 2022 special pair weights. '+1 pp gain' is the net-vote value of one D-share point. The D+1 targets form one uniform statewide combination; they are not separate necessary conditions. Full integers, other-candidate votes, weights, sources and statuses are in [county-baselines.csv](data/county-baselines.csv).

| County | FIPS | SEB | 2022 special pp | 2022 regular pp | 2020 Senate pp | 2024 pres pp | 2022 gov pp | Special pair weight % | Special net | +1 pp gain | D+1 target D % | D+1 target net |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Adair | 40001 | 01 | -53.80 | -45.27 | -52.14 | -63.94 | -24.63 | 0.4503 | -2,704 | 100.52 | 37.2757 | -1,279.04 |
| Alfalfa | 40003 | 02 | -71.60 | -79.19 | -75.75 | -77.81 | -53.95 | 0.1514 | -1,210 | 33.80 | 28.3770 | -730.86 |
| Atoka | 40005 | 03 | -67.46 | -68.23 | -69.18 | -72.23 | -46.80 | 0.3436 | -2,587 | 76.70 | 30.4470 | -1,499.71 |
| Beaver | 40007 | 04 | -81.51 | -83.15 | -81.29 | -84.92 | -69.47 | 0.1463 | -1,331 | 32.66 | 23.4226 | -868.02 |
| Beckham | 40009 | 05 | -63.45 | -69.63 | -68.58 | -71.11 | -53.69 | 0.4780 | -3,385 | 106.70 | 32.4514 | -1,872.44 |
| Blaine | 40011 | 06 | -54.03 | -62.13 | -59.82 | -63.97 | -38.28 | 0.2577 | -1,554 | 57.52 | 37.1592 | -738.60 |
| Bryan | 40013 | 07 | -55.24 | -57.92 | -56.30 | -59.37 | -28.89 | 0.9976 | -6,150 | 222.68 | 36.5578 | -2,993.32 |
| Caddo | 40015 | 08 | -36.73 | -47.40 | -43.45 | -48.09 | -21.92 | 0.6146 | -2,519 | 137.18 | 45.8131 | -574.36 |
| Canadian | 40017 | 09 | -34.47 | -42.31 | -40.97 | -41.23 | -20.84 | 4.3337 | -16,674 | 967.32 | 46.9385 | -2,961.40 |
| Carter | 40019 | 10 | -49.09 | -52.33 | -53.44 | -55.50 | -33.11 | 1.1622 | -6,367 | 259.42 | 39.6327 | -2,689.50 |
| Cherokee | 40021 | 11 | -21.58 | -24.60 | -22.24 | -33.28 | -1.36 | 1.1709 | -2,820 | 261.36 | 53.3861 | +885.00 |
| Choctaw | 40023 | 12 | -64.95 | -65.88 | -61.96 | -66.15 | -44.15 | 0.3522 | -2,553 | 78.62 | 31.7032 | -1,438.49 |
| Cimarron | 40025 | 13 | -85.63 | -88.97 | -87.35 | -85.75 | -82.34 | 0.0636 | -608 | 14.20 | 21.3590 | -406.70 |
| Cleveland | 40027 | 14 | -5.49 | -12.85 | -13.06 | -15.25 | +6.74 | 7.8942 | -4,834 | 1,762.04 | 61.4325 | +20,144.44 |
| Coal | 40029 | 15 | -65.09 | -63.61 | -64.08 | -72.40 | -40.23 | 0.1648 | -1,197 | 36.78 | 31.6310 | -675.61 |
| Comanche | 40031 | 16 | -23.05 | -28.90 | -24.74 | -23.78 | -8.56 | 2.0171 | -5,189 | 450.22 | 52.6504 | +1,193.26 |
| Cotton | 40033 | 17 | -64.55 | -71.20 | -71.04 | -68.12 | -37.07 | 0.1567 | -1,129 | 34.98 | 31.9003 | -633.13 |
| Craig | 40035 | 18 | -52.09 | -54.79 | -49.48 | -59.27 | -31.75 | 0.3908 | -2,272 | 87.24 | 38.1328 | -1,035.30 |
| Creek | 40037 | 19 | -50.20 | -53.86 | -52.12 | -56.78 | -37.56 | 1.9382 | -10,859 | 432.62 | 39.0753 | -4,726.24 |
| Custer | 40039 | 20 | -46.80 | -56.86 | -51.83 | -54.29 | -32.70 | 0.6531 | -3,411 | 145.78 | 40.7776 | -1,344.44 |
| Delaware | 40041 | 21 | -54.33 | -57.52 | -55.23 | -61.13 | -38.35 | 1.1528 | -6,990 | 257.32 | 37.0112 | -3,342.27 |
| Dewey | 40043 | 22 | -74.65 | -81.11 | -77.98 | -80.94 | -62.70 | 0.1527 | -1,272 | 34.08 | 26.8519 | -788.89 |
| Ellis | 40045 | 23 | -73.64 | -79.02 | -79.31 | -77.89 | -61.19 | 0.1298 | -1,067 | 28.98 | 27.3574 | -656.18 |
| Garfield | 40047 | 24 | -50.13 | -57.49 | -53.02 | -54.77 | -37.06 | 1.4044 | -7,858 | 313.48 | 39.1089 | -3,414.15 |
| Garvin | 40049 | 25 | -54.91 | -61.22 | -62.03 | -66.83 | -41.76 | 0.7071 | -4,333 | 157.82 | 36.7205 | -2,095.77 |
| Grady | 40051 | 26 | -52.93 | -60.92 | -59.44 | -63.59 | -40.41 | 1.5530 | -9,174 | 346.64 | 37.7104 | -4,260.08 |
| Grant | 40053 | 27 | -64.76 | -72.91 | -71.58 | -71.76 | -51.80 | 0.1378 | -996 | 30.76 | 31.7961 | -559.95 |
| Greer | 40055 | 28 | -55.54 | -62.64 | -63.10 | -66.50 | -39.20 | 0.1165 | -722 | 26.00 | 36.4066 | -353.43 |
| Harmon | 40057 | 29 | -56.54 | -64.47 | -60.09 | -62.24 | -43.80 | 0.0569 | -359 | 12.70 | 35.9081 | -178.97 |
| Harper | 40059 | 30 | -75.20 | -79.98 | -79.92 | -79.45 | -43.69 | 0.1004 | -843 | 22.42 | 26.5755 | -525.18 |
| Haskell | 40061 | 31 | -59.29 | -61.73 | -61.56 | -70.54 | -40.70 | 0.2976 | -1,969 | 66.42 | 34.5312 | -1,027.44 |
| Hughes | 40063 | 32 | -51.34 | -57.38 | -57.01 | -63.67 | -36.55 | 0.3082 | -1,766 | 68.80 | 38.5073 | -790.70 |
| Jackson | 40065 | 33 | -60.65 | -65.48 | -63.15 | -59.43 | -45.36 | 0.4754 | -3,218 | 106.12 | 33.8517 | -1,713.66 |
| Jefferson | 40067 | 34 | -64.06 | -67.01 | -71.49 | -72.72 | -42.41 | 0.1386 | -991 | 30.94 | 32.1461 | -552.40 |
| Johnston | 40069 | 35 | -64.25 | -65.77 | -63.17 | -67.00 | -39.22 | 0.2572 | -1,844 | 57.40 | 32.0504 | -1,030.31 |
| Kay | 40071 | 36 | -43.22 | -49.48 | -49.21 | -50.23 | -30.69 | 1.0838 | -5,228 | 241.92 | 42.5654 | -1,798.58 |
| Kingfisher | 40073 | 37 | -65.98 | -73.26 | -71.25 | -72.32 | -52.98 | 0.4256 | -3,134 | 95.00 | 31.1864 | -1,787.29 |
| Kiowa | 40075 | 38 | -48.94 | -58.87 | -56.05 | -59.22 | -36.65 | 0.2159 | -1,179 | 48.18 | 39.7051 | -496.01 |
| Latimer | 40077 | 39 | -57.27 | -59.02 | -56.45 | -66.26 | -34.80 | 0.2667 | -1,705 | 59.54 | 35.5397 | -860.97 |
| Le Flore | 40079 | 40 | -61.52 | -61.85 | -61.42 | -65.61 | -41.99 | 1.0585 | -7,267 | 236.26 | 33.4174 | -3,917.81 |
| Lincoln | 40081 | 41 | -55.84 | -62.74 | -61.06 | -64.33 | -41.57 | 0.9635 | -6,005 | 215.06 | 36.2534 | -2,956.34 |
| Logan | 40083 | 42 | -44.71 | -51.09 | -46.16 | -50.10 | -33.54 | 1.4742 | -7,356 | 329.04 | 41.8199 | -2,691.57 |
| Love | 40085 | 43 | -62.48 | -64.26 | -64.33 | -67.18 | -47.02 | 0.2374 | -1,655 | 52.98 | 32.9377 | -903.96 |
| Major | 40093 | 47 | -76.75 | -81.45 | -79.16 | -80.84 | -64.14 | 0.2320 | -1,987 | 51.78 | 25.8020 | -1,252.97 |
| Marshall | 40095 | 48 | -61.01 | -63.11 | -62.85 | -64.12 | -38.55 | 0.3824 | -2,604 | 85.36 | 33.6698 | -1,393.95 |
| Mayes | 40097 | 49 | -49.49 | -52.91 | -49.71 | -58.59 | -31.27 | 1.0963 | -6,055 | 244.70 | 39.4313 | -2,586.17 |
| McClain | 40087 | 44 | -52.08 | -58.81 | -58.18 | -61.68 | -39.01 | 1.3088 | -7,607 | 292.14 | 38.1370 | -3,465.66 |
| McCurtain | 40089 | 45 | -66.58 | -66.73 | -64.59 | -69.66 | -41.32 | 0.7211 | -5,358 | 160.96 | 30.8881 | -3,076.25 |
| McIntosh | 40091 | 46 | -42.65 | -46.48 | -43.90 | -53.46 | -27.31 | 0.5634 | -2,682 | 125.76 | 42.8495 | -899.24 |
| Murray | 40099 | 50 | -52.84 | -59.12 | -55.70 | -62.56 | -32.07 | 0.3697 | -2,180 | 82.52 | 37.7580 | -1,010.21 |
| Muskogee | 40101 | 51 | -30.32 | -34.20 | -29.90 | -38.20 | -13.36 | 1.5488 | -5,241 | 345.70 | 49.0153 | -340.40 |
| Noble | 40103 | 52 | -49.92 | -57.02 | -53.29 | -58.49 | -32.99 | 0.3303 | -1,840 | 73.72 | 39.2166 | -794.96 |
| Nowata | 40105 | 53 | -62.21 | -63.80 | -61.13 | -67.96 | -43.07 | 0.2907 | -2,018 | 64.88 | 33.0723 | -1,098.27 |
| Okfuskee | 40107 | 54 | -44.72 | -48.29 | -48.60 | -56.58 | -25.18 | 0.2555 | -1,275 | 57.02 | 41.8153 | -466.69 |
| Oklahoma | 40109 | 55 | +4.41 | -4.51 | -0.90 | -1.72 | +13.64 | 19.3141 | +9,513 | 4,311.02 | 66.3825 | +70,625.43 |
| Okmulgee | 40111 | 56 | -33.31 | -36.50 | -33.79 | -43.48 | -19.29 | 0.9250 | -3,439 | 206.46 | 47.5189 | -512.25 |
| Osage | 40113 | 57 | -34.28 | -37.58 | -35.39 | -42.11 | -23.09 | 1.3154 | -5,032 | 293.60 | 47.0369 | -869.97 |
| Ottawa | 40115 | 58 | -48.50 | -50.05 | -37.86 | -54.35 | -28.08 | 0.6649 | -3,599 | 148.42 | 39.9271 | -1,495.02 |
| Pawnee | 40117 | 59 | -51.48 | -55.07 | -54.38 | -59.91 | -36.67 | 0.4388 | -2,521 | 97.94 | 38.4356 | -1,132.62 |
| Payne | 40119 | 60 | -14.40 | -23.27 | -21.70 | -25.95 | -2.17 | 1.9150 | -3,078 | 427.44 | 56.9749 | +2,981.33 |
| Pittsburg | 40121 | 61 | -51.92 | -53.80 | -52.94 | -59.88 | -35.37 | 1.1103 | -6,433 | 247.82 | 38.2175 | -2,919.94 |
| Pontotoc | 40123 | 62 | -32.60 | -39.90 | -42.85 | -47.58 | -6.29 | 0.9697 | -3,528 | 216.44 | 47.8757 | -459.78 |
| Pottawatomie | 40125 | 63 | -37.77 | -45.81 | -43.16 | -48.43 | -23.74 | 1.7933 | -7,560 | 400.28 | 45.2891 | -1,885.69 |
| Pushmataha | 40127 | 64 | -66.91 | -66.62 | -68.62 | -73.45 | -45.27 | 0.2881 | -2,151 | 64.30 | 30.7233 | -1,239.49 |
| Roger Mills | 40129 | 65 | -75.00 | -81.08 | -73.54 | -81.26 | -70.23 | 0.1147 | -960 | 25.60 | 26.6759 | -597.10 |
| Rogers | 40131 | 66 | -49.96 | -53.82 | -51.69 | -55.97 | -36.41 | 2.9442 | -16,416 | 657.16 | 39.1956 | -7,100.19 |
| Seminole | 40133 | 67 | -39.39 | -47.66 | -42.79 | -50.62 | -27.97 | 0.5115 | -2,249 | 114.18 | 44.4789 | -630.40 |
| Sequoyah | 40135 | 68 | -54.05 | -55.04 | -54.73 | -62.24 | -32.37 | 0.8924 | -5,383 | 199.18 | 37.1501 | -2,559.45 |
| Stephens | 40137 | 69 | -59.81 | -63.99 | -65.95 | -64.69 | -42.89 | 1.1334 | -7,565 | 252.98 | 34.2723 | -3,978.79 |
| Texas | 40139 | 70 | -71.20 | -73.90 | -67.32 | -68.97 | -59.52 | 0.3142 | -2,497 | 70.14 | 28.5756 | -1,502.71 |
| Tillman | 40141 | 71 | -55.87 | -62.80 | -58.67 | -60.10 | -36.09 | 0.1596 | -995 | 35.62 | 36.2421 | -490.06 |
| Tulsa | 40143 | 72 | -10.43 | -16.33 | -14.36 | -15.57 | +0.22 | 16.8091 | -19,561 | 3,751.90 | 58.9622 | +33,625.42 |
| Wagoner | 40145 | 73 | -45.64 | -49.61 | -47.49 | -50.66 | -32.68 | 2.3351 | -11,893 | 521.22 | 41.3582 | -4,504.26 |
| Washington | 40147 | 74 | -46.31 | -51.33 | -47.14 | -48.80 | -33.32 | 1.4860 | -7,680 | 331.68 | 41.0210 | -2,978.15 |
| Washita | 40149 | 75 | -62.96 | -73.12 | -69.41 | -75.94 | -51.58 | 0.3111 | -2,186 | 69.44 | 32.6954 | -1,201.63 |
| Woods | 40151 | 76 | -56.02 | -64.23 | -62.08 | -65.59 | -38.63 | 0.2343 | -1,465 | 52.30 | 36.1644 | -723.60 |
| Woodward | 40153 | 77 | -65.76 | -71.51 | -70.23 | -73.13 | -53.12 | 0.4694 | -3,445 | 104.78 | 31.2975 | -1,959.65 |

## Files, reproduction and checks

- [acquire.py](data/baselines/acquire.py): network fetch of every source into its own `raw/<source_id>/` directory. Text is gzip-compressed losslessly; ZIP and PDF are stored as-is. Writes [sources.json](data/baselines/sources.json).
- [build.py](data/baselines/build.py): offline. It verifies each raw hash, then writes the long tables, controls, scenarios, [slate-2026.json](data/baselines/slate-2026.json), [build-checks.json](data/baselines/build-checks.json) (425 checks, 0 failed) and the wide county CSV. Run with `uv run --with pypdf==5.1.0 python3 -I build.py`.
- [render_report.py](data/baselines/render_report.py): writes this page from those outputs.
- [validate.py](data/baselines/validate.py): independent offline checks, written to [validation.json](data/baselines/validation.json), plus the [asset manifest](data/baselines/asset-manifest.json). It covers: 77 unique counties, FIPS and SEB codes per contest; D+R+other balances; candidate and method sums; Clerk and SEB controls; weights summing to one; scenario tie and D+1 arithmetic, including the +0.5-point step; summed county target nets; selected-county equations; synthetic clipping, impossible and already-winning cases; uniform-scaling invariance; raw-file hashes; file sizes under 40 MB; and relative links on this page.
- Column definitions are in [SCHEMA.md](data/baselines/SCHEMA.md).

## Gaps

- **No SEB county export was downloaded.** The official OKER application serves county and precinct exports only after an application login, which this package did not perform. County counts are MEDSL or OpenElections transcriptions of those exports, reconciled to official statewide totals. Before live use, re-verify them against SEB exports obtained by a person in a browser, or against county election board canvass reports.
- The MEDSL 2020 Oklahoma file on Harvard Dataverse requires a guestbook response, and the VEST 2022 Oklahoma file requires a login. Neither was used, so there is no fully independent second county transcription for 2020 or 2022.
- The 2022 governor contest has no primary statewide control here and is context only.
- Official certified June 16 primary and August 25 runoff counts were not retrieved. The Hern and Thomas nominations rest on newsroom reports plus the official filing list. The unexpired-term question (whether November also fills the rest of the vacancy) is not resolved from statute.
- Ballots cast, under/overvotes and registration are not in these contest files. The turnout worker owns those measures in `turnout.md`.
- Historical precinct IDs are not current 2026 reporting units. No geographic crosswalk is implied.
- These are deterministic scenarios. There are no probabilities, no 2026 turnout projection and no live collector.
