# Wyoming turnout volume and county priority

Research retrieval: **2026-10-18** (16:34-16:40 UTC; [retrieval manifest](data/turnout/source-manifest.json)). **All 23 counties are included.** Wyoming reports by county and precinct. Counties are the reporting geography, and Census FIPS codes apply directly; there are no independent cities or towns that report outside counties.

**Ranking measure:** certified **2024 U.S. Senate contest votes**. This is John Barrasso (R) plus Scott D Morrow (D) plus the SOS's aggregated Write-Ins column: **264,162**. It excludes the 101 overvotes and 6,860 undervotes, which the SOS prints separately. This 2024 contest was for the other seat (Class I), not the Class II seat on the 2026 ballot. The ranking measures vote volume, not a turnout rate. [2024 Statewide Candidates Official Summary, p.3](https://sos.wyo.gov/Elections/Docs/2024/Results/General/2024_General_Statewide_Candidates_Summary.pdf), [official results ZIP](https://sos.wyo.gov/Elections/Docs/2024/Results/General/2024_Wyoming_General_Results.zip), [2024 results page](https://sos.wyo.gov/Elections/Docs/2024/2024GeneralResults.aspx).

**Top 15 in descending order:** Laramie, Natrona, Campbell, Albany, Fremont, Sweetwater, Park, Sheridan, Teton, Lincoln, Uinta, Converse, Carbon, Goshen, Big Horn. Together they have **234,538 / 264,162 = 88.7857%** of the 2024 Senate contest votes.

**Smallest set reaching 80%: 12 counties, 216,487 / 264,162 = 81.9524%.** In order: Laramie, Natrona, Campbell, Albany, Fremont, Sweetwater, Park, Sheridan, Teton, Lincoln, Uinta, Converse. The first 11 have **209,934 = 79.4717%**. Converse (**FIPS 56009**) adds 6,553 and crosses the threshold. Integer proof: `5 * 209,934 = 1,049,670 < 4 * 264,162 = 1,056,648 <= 5 * 216,487 = 1,082,435`. Counties are sorted largest first, so no 11 counties can reach 80%. The other 11 counties have 47,675 votes (18.0476%). No two county values are equal; ties would be broken by ascending FIPS. Sublette (4,829) and Johnson (4,828) differ by one vote at ranks 16 and 17, outside the priority set. [All-county CSV](data/county-turnout.csv), [machine-readable rankings](data/turnout/rankings.json).

**Priority union:** the top 15 contain all 12 counties of the 80% set, so the union is the **15 counties** of the top 15 (88.7857%). This research priority is not a reason to leave the other eight counties out of statewide arithmetic.

## Robustness across elections and denominators

The general-election measures below give the **same 12-county 80% set** and the **same top-15 set**. Only the order within each set changes. Every measure is computed from the SOS integers, with ties broken by ascending FIPS. [Rankings](data/turnout/rankings.json), [validation](data/turnout/validation.json).

| Measure (official SOS source) | Statewide | Top-15 share | 80% set size | 80% set share | First k-1 share | Crossing county |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| [2024 U.S. Senate contest votes](https://sos.wyo.gov/Elections/Docs/2024/Results/General/2024_General_Statewide_Candidates_Summary.pdf) | 264,162 | 88.7857% | 12 | 81.9524% | 79.4717% | Converse |
| [2024 President contest votes](https://sos.wyo.gov/Elections/Docs/2024/Results/General/2024_General_Statewide_Candidates_Summary.pdf) | 269,048 | 88.7849% | 12 | 81.9846% | 79.4799% | Converse |
| [2024 total ballots cast](https://sos.wyo.gov/Elections/Docs/2024/Results/General/2024_General_Statewide_Total_Ballots_Cast_Summary.pdf) | 271,123 | 88.7737% | 12 | 81.9694% | 79.4687% | Converse |
| [2022 Governor contest votes](https://sos.wyo.gov/Elections/Docs/2022/Results/General/2022_General_Statewide_Candidates_Summary.pdf) (midterm) | 194,000 | 87.8474% | 12 | 80.7572% | 78.1918% | Converse |
| [2022 total ballots cast](https://sos.wyo.gov/Elections/Docs/2022/Results/General/2022_General_Statewide_Total_Ballots_Cast_Summary.pdf) (midterm) | 198,198 | 87.7532% | 12 | 80.6658% | 78.0659% | Converse |
| [2020 U.S. Senate contest votes](https://sos.wyo.gov/Elections/Docs/2020/Results/General/2020_General_Statewide_Candidates_Summary.pdf) (same Class II seat) | 271,937 | 89.0353% | 12 | 82.2874% | 79.7858% | Converse |
| [2020 total ballots cast](https://sos.wyo.gov/Elections/Docs/2020/Results/General/2020_General_Statewide_Total_Ballots_Cast_Summary.pdf) | 278,503 | 89.0270% | 12 | 82.2903% | 79.7733% | Converse |
| *Context only:* [2026 primary total ballots](https://sos.wyo.gov/Elections/Docs/2026/Results/Primary/2026_Statewide_Total_Ballots_Cast_Summary.pdf) | 150,385 | 86.9854% | 13 | 82.2190% | 79.6462% | Converse |

**Write-in sensitivity:** the SOS publishes write-ins as one aggregate per county and does not name the candidates. Including or excluding them does not change the 2024 Senate result. Named candidates only give 262,145 votes, and the same 12 counties reach 81.9314%. The 2022 Governor contest had many more write-ins: 11,461 of 194,000 contest votes (5.9077%). By county this derived share runs from 0.5027% in Teton to 23.9733% in Niobrara. With named Governor candidates only (182,539), **Goshen replaces Converse** as the 12th county (81.2807%). Both counties are in the 15-county union. [Rankings, sensitivity entries](data/turnout/rankings.json).

**2026 primary context:** 150,385 ballots were cast on 2026-08-18: 132,725 Republican, 13,269 Democratic and 4,391 Non-Partisan party ballots. On this measure the 80% set needs 13 counties, adding Big Horn, and Sublette replaces Carbon in the top 15. A partisan primary is not a general-election turnout baseline, so these figures are context only. [2026 primary results page](https://sos.wyo.gov/Elections/Docs/2026/2026PrimaryResults.aspx), [2026 primary ZIP](https://sos.wyo.gov/Elections/Docs/2026/Results/Primary/2026_Wyoming_Primary_Results.zip).

## Contests, candidates and the midterm comparator

Wyoming had **no U.S. Senate contest in 2022**. The midterm comparator is therefore the 2022 Governor contest, the highest-office statewide contest that was actually held. It is labeled as a Governor contest everywhere and never used as a Senate result. Each comparator keeps every printed candidate, the aggregated write-ins, overvotes and undervotes separately.

| Election / contest | Printed candidates and write-ins | Contest votes | Over | Under | Total ballots cast |
| --- | --- | ---: | ---: | ---: | ---: |
| [2024 U.S. Senate (Class I)](https://sos.wyo.gov/Elections/Docs/2024/Results/General/2024_General_Statewide_Candidates_Summary.pdf) | John Barrasso (R) 198,418; Scott D Morrow (D) 63,727; Write-Ins 2,017 | 264,162 | 101 | 6,860 | 271,123 |
| [2024 President](https://sos.wyo.gov/Elections/Docs/2024/Results/General/2024_General_Statewide_Candidates_Summary.pdf) | Trump/Vance (R) 192,633; Harris/Walz (D) 69,527; Oliver/ter Maat (L) 4,193; Write-Ins 2,695 | 269,048 | 76 | 1,999 | 271,123 |
| [2022 Governor (midterm)](https://sos.wyo.gov/Elections/Docs/2022/Results/General/2022_General_Statewide_Candidates_Summary.pdf) | Mark Gordon (R) 143,696; Theresa A. Livingston (D) 30,686; Jared J. Baldes (L) 8,157; Write-Ins 11,461 | 194,000 | 91 | 4,107 | 198,198 |
| [2020 U.S. Senate (Class II, same seat as 2026)](https://sos.wyo.gov/Elections/Docs/2020/Results/General/2020_General_Statewide_Candidates_Summary.pdf) | Cynthia M. Lummis (R) 198,100; Merav Ben David (D) 72,766; Write-Ins 1,071 | 271,937 | 165 | 6,401 | 278,503 |

**Midterm result:** 2022 Governor contest votes were **73.4398%** of the 2024 Senate contest volume (194,000 / 264,162). 2022 ballots were 73.1026% of 2024 ballots. The same 12 counties are the 80% set in both years. In the midterm their share is 1.1951 points lower (80.7572% vs 81.9524%), and the top 15 hold 87.8474% instead of 88.7857%. Laramie's share falls from 16.3199% to 15.4180% and Natrona's from 12.5892% to 11.5933%. Fremont rises from 5th to 3rd and Park from 7th to 4th, while Campbell falls from 3rd to 6th. These comparisons change the year, the office and the candidates together. They do not isolate a pure participation effect. [Per-county shares and ranks](data/county-turnout.csv).

**2026 seat context:** the SOS [2026 general election candidate list](https://sos.wyo.gov/Elections/Docs/2026/2026_WY_General_Election_Candidates.csv), retrieved 2026-10-18, lists Harriet Hageman (REP) and James Byrd (DEM) for United States Senator. This file was hashed but not retained because it contains candidate contact details. Lummis, the 2020 winner for this Class II seat, is not on that list, so the 2020 candidate effects do not carry over. The coordinator owns ballot verification; this observation only qualifies the 2020 comparator.

## Contest votes, ballots cast and registration

These are three different quantities, and every CSV column says which one it holds:

- **Contest votes** are the named candidates plus aggregated write-ins for one contest.
- **Total ballots cast** is the SOS "Total Ballots Cast" summary for the whole election.
- **Registration** is a count of registration records at a stated date. It is a stock, not participation.

For all four contests in all 23 counties, **contest votes + overvotes + undervotes = total ballots cast exactly**. Statewide, for example, 264,162 + 101 + 6,860 = 271,123. Every ballot therefore counts once in each single-seat contest. [Validation](data/turnout/validation.json).

**Registration snapshots** come from the SOS monthly county statistics:

| Snapshot | Source page | Statewide total |
| --- | --- | ---: |
| 11/5/2024 "General Election Day" | [2024 statistics, p.13](https://sos.wyo.gov/Elections/Docs/VRStats/2024VR_stats.pdf) | 256,251 |
| 11/8/2022 "General Election Day" | [2022 statistics, p.13](https://sos.wyo.gov/Elections/Docs/VRStats/2022VR_stats.pdf) | 297,639 |
| 11/3/2020 "General Election Day" | [2020 statistics, p.12](https://sos.wyo.gov/Elections/Docs/VRStats/2020VR_stats.pdf) | 268,837 |
| 10/1/2026 monthly report | [October 2026 report](https://sos.wyo.gov/Elections/Docs/VRStats/2026/26OctVR_Stats.pdf) | 279,421 |

In each 2020-2024 snapshot, the party columns sum to each county's TOTAL, and the county TOTALs sum to the printed state TOTAL. Each election-day total equals the "Registered Voters" figure in the SOS [registration and turnout history](https://sos.wyo.gov/Elections/Docs/VoterProfile.pdf), revised 08/2026. That document's footnote says this count covers people registered **by close of business on the day before** the election. It **does not include election-day registrations** (W.S. 22-3-104). As a result, 2024 ballots (271,123) exceed this registration count statewide, and in 18 of 23 counties. The same happens in 18 counties in 2020, but in no county in 2022. This report therefore computes **no ballots-per-registration rate**. The history's voting-age-population estimates (454,508 for 2024) are Census-derived estimates and are not used. Its "Voter Turnout" figures (271,123 / 198,198 / 278,503) equal the Total Ballots Cast summaries. [County registration rows](data/turnout/registration-snapshots.csv).

The October 2026 snapshot is current context only. It is not a 2026 turnout estimate, and it does not include later or election-day registrations. The SOS summaries used here do not split ballots by voting method (absentee or early versus Election Day), so no method split is reported.

## Source chain, certification and reconciliation

**Authority chain:** the [SOS results index](https://sos.wyo.gov/Elections/ElectionResults.aspx) links each year's results page. Each results page links the statewide summary PDFs, a ZIP of Excel workbooks and county precinct-by-precinct files. The validation confirms offline that every retained child file is linked from its retained parent page. The 2024 [State Canvassing Board minutes](https://sos.wyo.gov/Elections/Docs/2024/Results/General/2024_General_State_Canvassing_Board_Minutes.pdf) are a scanned PDF. Page 9 is the Board's certification of the 2024 canvass, signed 2024-11-13. The 2022 and 2020 pages are titled "Official General Election Results" but link no canvass minutes, and none were retrieved for those years. The 2026 primary page is titled "Official Primary Election Results".

**Two official renderings agree:** `build.py` reads the county values from the Excel workbooks inside the ZIPs. `validate.py` reads the separately published statewide PDFs and finds every county cell identical. That covers each candidate, write-in, overvote and undervote for 2024 Senate, 2022 Governor and 2020 Senate, the 2024 President totals, and all three general-election ballots-cast summaries. In every contest, the county rows sum to the printed statewide Total. In the 2024 workbook, the ballots-cast county cells are cached results of IMPORTRANGE formulas that pulled values from a Google Sheet. The cached values are used, and the PDF rendering confirms them.

**Precinct workbooks:** for each of the four contests in all 23 counties, the precinct rows sum to the sheet's Total row, which equals the statewide county row. There are 432 precinct rows in 2024, 439 in 2022 and 480 in 2020. These are SOS reporting rows. They are not verified polygons or approved 2026 units, and labels change style between years in some counties (for example `1-1` in 2020 and `1-01` in 2022/2024). [Precinct reconciliation](data/turnout/precinct-reconciliation.csv). The source anomalies below are recorded, not altered:

- **Natrona 2022 precinct ballots:** the [precinct ballots PDF](https://sos.wyo.gov/Elections/Docs/2022/Results/General/2022_Natrona_County_General_PbP_TBC.pdf) and its workbook sheet both print a Total of **22,957**. Their 46 precinct rows sum to **22,955**, which equals the statewide Total Ballots Cast summary. Both files are dated 2022-12-14, after the canvass (workbook ZIP entry; PDF ModDate). The county baseline uses the statewide summary value of 22,955. The +2 is not attributed to any cause.
- **Johnson 2020:** at the precinct level, contest marks differ from ballots by one vote in two precincts. Precinct 4-8 has 871 marks against 872 ballots, and precinct 5-9 has 108 against 107. The differences offset, and the county totals reconcile.
- **Excel date coercion:** in the 2024 and 2022 contest workbooks, the Carbon, Converse and Crook sheets store precinct IDs such as `01-01` as dates (for example `2022-01-01`). For matching, these labels are rebuilt as `MM-DD`, and the raw values are listed in the [rankings metadata](data/turnout/rankings.json). The ballots sheets store the same IDs as text, and after repair every label matches.
- "Precincts Continue on Next Page" rows in four large-county sheets contain no counts and are skipped.

**2026 general channel:** the results index already links `/Elections/Docs/2026/2026GeneralResults.aspx`. On 2026-10-18 that URL returned **HTTP 404**; the 404 body is retained. The official-results worker owns any conclusion about the November publication format.

## Files and reproduction

- [All 23 counties](data/county-turnout.csv): every candidate, write-in, overvote and undervote count; contest-vote, ballots-cast and registration columns; shares, ranks, and top-15/80% flags for each measure. Blank never means zero; there are no blank counts. FIPS codes are five-character strings, with Census GNIS codes alongside.
- [Cell-level extract](data/turnout/extracted-county-results.csv): each county value with its workbook, sheet and cell. Also [registration rows](data/turnout/registration-snapshots.csv) and [precinct reconciliation](data/turnout/precinct-reconciliation.csv).
- [Source list](data/turnout/sources.json), [retrieval script](data/turnout/acquire.py) and [manifest](data/turnout/source-manifest.json). The manifest records the request/final URL, HTTP status, Last-Modified and other headers, UTC retrieval time, and SHA-256 and size of each original response and stored file. Originals are kept byte for byte under [originals/](data/turnout/originals/). The eight HTML landing pages are gzip-compressed with a fixed header, which is lossless. The 2026 primary canvass minutes (11.5 MB scan, not used for counts) and the candidate CSV are hash-only. All files are well below 40 MB; the originals total about 12 MB.
- [build.py](data/turnout/build.py) reads only the retained originals, writes every output above plus [build checks](data/turnout/build-checks.json) and the [generated ranking table](data/turnout/ranking-table.md). [validate.py](data/turnout/validate.py) writes [validation.json](data/turnout/validation.json).

```sh
uv run python3 -I senate/2026/wyoming/data/turnout/acquire.py            # optional live refresh
uv run --with openpyxl==3.1.5 --with pypdf==6.21.1 python3 -I senate/2026/wyoming/data/turnout/build.py
uv run --with pypdf==6.21.1 python3 -I senate/2026/wyoming/data/turnout/validate.py
```

Validation checks hashes and the link chain; 23 unique counties with Census FIPS/GNIS; every county value against the PDFs; contest totals against the official statewide totals; the ballot identity; ranks with the FIPS tie-break; and cumulative shares recomputed from integers. It checks the minimum-80% set in integer form (`5*cum(k-1) < 4*T <= 5*cum(k)`) for every measure, plus the top-15 flags, registration controls, file sizes, this page's relative links, and that the table below matches the CSV.

## Complete county order

All values are 2024 U.S. Senate contest votes unless labeled. Percentages are rounded for display only; the CSV keeps ten decimals computed from integers. The 2022 and 2020 columns show that year's contest votes and rank. The 2022 figures are for Governor, not Senate.

<!-- Generated by build.py from ../county-turnout.csv; display rounding only. -->
| Rank | County | FIPS | 2024 Senate contest votes | Share | Cumulative | 2024 ballots cast | 2022 Governor contest votes (rank) | 2022 share | 2020 Senate contest votes (rank) | Priority |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | Laramie | 56021 | 43,111 | 16.3199% | 16.3199% | 43,607 | 29,911 (1) | 15.4180% | 44,722 (1) | top 15, 80% set |
| 2 | Natrona | 56025 | 33,256 | 12.5892% | 28.9092% | 34,206 | 22,491 (2) | 11.5933% | 34,449 (2) | top 15, 80% set |
| 3 | Campbell | 56005 | 17,788 | 6.7337% | 35.6429% | 18,450 | 12,262 (6) | 6.3206% | 19,015 (3) | top 15, 80% set |
| 4 | Albany | 56001 | 17,596 | 6.6611% | 42.3040% | 17,993 | 12,600 (5) | 6.4948% | 18,328 (4) | top 15, 80% set |
| 5 | Fremont | 56013 | 16,870 | 6.3862% | 48.6902% | 17,396 | 13,398 (3) | 6.9062% | 17,735 (5) | top 15, 80% set |
| 6 | Sweetwater | 56037 | 16,351 | 6.1898% | 54.8800% | 16,819 | 11,917 (8) | 6.1428% | 16,274 (7) | top 15, 80% set |
| 7 | Park | 56029 | 16,287 | 6.1655% | 61.0455% | 16,876 | 12,698 (4) | 6.5454% | 16,376 (6) | top 15, 80% set |
| 8 | Sheridan | 56033 | 16,154 | 6.1152% | 67.1607% | 16,577 | 12,191 (7) | 6.2840% | 16,132 (8) | top 15, 80% set |
| 9 | Teton | 56039 | 13,059 | 4.9436% | 72.1042% | 13,424 | 10,146 (9) | 5.2299% | 14,434 (9) | top 15, 80% set |
| 10 | Lincoln | 56023 | 10,621 | 4.0206% | 76.1249% | 10,940 | 7,482 (10) | 3.8567% | 10,330 (10) | top 15, 80% set |
| 11 | Uinta | 56041 | 8,841 | 3.3468% | 79.4717% | 9,170 | 6,596 (11) | 3.4000% | 9,172 (11) | top 15, 80% set |
| 12 | Converse | 56009 | 6,553 | 2.4807% | 81.9524% | 6,780 | 4,977 (12) | 2.5655% | 6,803 (12) | top 15, 80% set |
| 13 | Carbon | 56007 | 6,284 | 2.3788% | 84.3312% | 6,446 | 4,703 (14) | 2.4242% | 6,552 (13) | top 15 |
| 14 | Goshen | 56015 | 6,103 | 2.3103% | 86.6415% | 6,214 | 4,813 (13) | 2.4809% | 6,143 (14) | top 15 |
| 15 | Big Horn | 56003 | 5,664 | 2.1441% | 88.7857% | 5,788 | 4,239 (15) | 2.1851% | 5,655 (15) | top 15 |
| 16 | Sublette | 56035 | 4,829 | 1.8280% | 90.6137% | 4,972 | 3,544 (18) | 1.8268% | 4,852 (17) |  |
| 17 | Johnson | 56019 | 4,828 | 1.8277% | 92.4414% | 4,955 | 3,865 (17) | 1.9923% | 4,832 (18) |  |
| 18 | Platte | 56031 | 4,704 | 1.7807% | 94.2221% | 4,805 | 3,921 (16) | 2.0211% | 4,870 (16) |  |
| 19 | Crook | 56011 | 4,244 | 1.6066% | 95.8287% | 4,368 | 3,248 (19) | 1.6742% | 4,043 (19) |  |
| 20 | Washakie | 56043 | 3,821 | 1.4465% | 97.2752% | 3,917 | 3,045 (20) | 1.5696% | 3,948 (20) |  |
| 21 | Weston | 56045 | 3,416 | 1.2931% | 98.5683% | 3,533 | 2,735 (21) | 1.4098% | 3,448 (21) |  |
| 22 | Hot Springs | 56017 | 2,589 | 0.9801% | 99.5484% | 2,643 | 2,171 (22) | 1.1191% | 2,532 (22) |  |
| 23 | Niobrara | 56027 | 1,193 | 0.4516% | 100.0000% | 1,244 | 1,047 (23) | 0.5397% | 1,292 (23) |  |
| | **Statewide** | 56 | **264,162** | 100% | | **271,123** | **194,000** | 100% | **271,937** | |

## Gaps and limits

- Write-ins are one aggregate per county, with no candidate identification or validity breakdown. Both treatments are reported above.
- The retrieved summaries have no split by voting method (absentee or early versus Election Day), and no county outstanding-ballot data.
- 2022 and 2020 certification documents (canvass minutes) were not retrieved. Those years rest on the SOS pages' "Official" labels.
- Registration excludes election-day registrants, so no rate is computed from it.
- The precinct rows are historical reporting rows. Current 2026 precinct geography and crosswalks belong to the maps worker and are not established here.
- The 2026 general results page did not exist at retrieval (HTTP 404). Nothing here describes November 2026 reporting cadence.
- This is research data. It contains no turnout forecast, live collector or probability.
