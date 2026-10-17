# Michigan’s big turnout counties

Research date: **2026-10-17**. Ranking denominator: **2024 U.S. Senate votes for all candidates**, including reported named write-ins. This measures vote volume, not turnout rate.

**Exact top 15, in descending order:** Wayne, Oakland, Macomb, Kent, Genesee, Washtenaw, Ottawa, Ingham, Kalamazoo, Livingston, Saginaw, St. Clair, Muskegon, Monroe, Berrien. They contribute **3,968,745 / 5,577,187 = 71.16033585%** of statewide Senate votes.

**Exact smallest set reaching at least 80% (23 counties):** Wayne, Oakland, Macomb, Kent, Genesee, Washtenaw, Ottawa, Ingham, Kalamazoo, Livingston, Saginaw, St. Clair, Muskegon, Monroe, Berrien, Jackson, Allegan, Calhoun, Eaton, Grand Traverse, Bay, Lapeer, Lenawee. They contribute **4,484,963 / 5,577,187 = 80.41622058%**. The first 22 contribute **4,431,179 = 79.45186346%**; Lenawee crosses the threshold. Because counties are sorted largest first, no set of only 22 can reach 80%. These are the project’s priority counties: the top 15 are already contained within the 23. Detroit should be examined inside Wayne, without counting it again as a separate county.

These are reproducible calculations from the pinned [MEDSL county extract](https://github.com/MEDSL/2024-elections-official/blob/df531089c78e6d0098db1a6bfb3849a066a06995/2024-senate-county.csv), retrieved 2026-10-17, with every candidate’s statewide sum reconciled below to the [U.S. House Clerk’s official statistics](https://clerk.house.gov/member_info/electionInfo/2024/statistics2024.pdf), retrieved 2026-10-17. **County-source limitation:** this is an official-returns derivative published by MEDSL, not a successfully downloaded state county export. Its county allocation has not been independently verified against all 83 county certificates. The set is actionable for research prioritization with that provenance limitation visible.

## Certified baseline and reconciliation

MDOS [announced certification on 2024-11-22](https://www.michigan.gov/sos/resources/news/2024/11/22/michigan-board-of-state-canvassers-certifies-the-2024-general-election); checked 2026-10-17. The [MDOS results index](https://www.michigan.gov/sos/elections/election-results-and-data), checked 2026-10-17, links the [2024 statewide county-results interface](https://mvic.sos.state.mi.us/votehistory/Index?type=C&electionDate=11-5-2024). That interface returned a Cloudflare challenge through curl and was inaccessible through the web tool. The legacy [official results host](https://mielections.us/election/results/) cited by MEDSL also failed to return usable data in bounded attempts. These failures do not establish that the sites are unavailable to human users.

The [pinned MEDSL provenance notes](https://github.com/MEDSL/2024-elections-official/blob/df531089c78e6d0098db1a6bfb3849a066a06995/README.md#michigan), retrieved 2026-10-17, say Michigan was added 2025-10-24 and cite that official host; they also warn of negative correction artifacts in the broader precinct data. The selected county Senate rows have `mode=TOTAL`, `unofficial=FALSE`, version `2025-11-21`, and no negative counts. The version is the derivative’s metadata, not a state certification date. The exact source publication/revision chronology beyond those labels is not independently established.

The saved 747 Michigan rows comprise nine candidates in each of 83 counties. Candidate sums match the House Clerk’s Michigan “For United States Senator” table exactly:

| Candidate | Sum of county votes | House Clerk | Difference |
| --- | ---: | ---: | ---: |
| Elissa Slotkin (D) | 2,712,686 | 2,712,686 | 0 |
| Mike Rogers (R) | 2,693,680 | 2,693,680 | 0 |
| Joseph Solis-Mullen | 56,697 | 56,697 | 0 |
| Douglas P. Marsh | 53,978 | 53,978 | 0 |
| Dave Stein | 41,363 | 41,363 | 0 |
| Doug Dern | 18,779 | 18,779 | 0 |
| Valerie Lee Willis (write-in) | 2 | 2 | 0 |
| James Chapman (write-in) | 1 | 1 | 0 |
| Marcus A. Irvine (write-in) | 1 | 1 | 0 |
| **All candidates** | **5,577,187** | **5,577,187 (sum)** | **0** |

Other candidates together account for **170,821**; D+R is **5,406,366**; D−R is **19,006**. All statewide totals here use the same candidate universe and county vintage. Source: [House Clerk 2024 statistics](https://clerk.house.gov/member_info/electionInfo/2024/statistics2024.pdf), retrieved 2026-10-17; local PDF and text are retained.

**Conflicting remembered figures:** the review supplied Slotkin 2,708,668 and Rogers 2,689,965. They are respectively 4,018 and 3,715 below the current primary-source counts; their implied D−R lead is 18,703, versus 19,006 here (a 303-vote difference). Searches on 2026-10-17 did not establish their source or vintage, so they must not be called certified, early, or unofficial as an established fact. They are excluded from every baseline calculation. No county table has been rescaled to force a match: the MEDSL county integers already sum exactly to each current House Clerk candidate count. Statewide reconciliation is necessary but does not alone prove every county allocation correct.

## Ballots, registration, and population

The July 2025 MDOS [Access Matters report](https://www.michigan.gov/sos/-/media/Project/Websites/sos/Press-releases/2025/documents/MDOS-2024-Elections-Report.pdf), retrieved 2026-10-17, reports **5,706,503 total 2024 voters** and explains in its page 3 footnote that this comes from official county tabulator totals. Thus statewide ballots exceed the Senate contest total by **129,316**. That subtraction is a denominator difference; this research cannot split it into Senate undervotes, overvotes, or other categories. The report supplies county rates and method percentages, not the exact county ballot integers needed here. County `ballots_cast_2024` is therefore blank, not zero. A separate ballots-cast county ranking remains a gap.

The same report distinguishes tabulator totals from Qualified Voter File voter-history counts. Its county active-registration turnout rates use the QVF-based dashboard; do not multiply rounded rates by registration snapshots to manufacture exact ballot counts. The [Michigan Voting Dashboard documentation](https://www.michigan.gov/sos/elections/election-results-and-data/voter-participation-dashboard), checked 2026-10-17, likewise warns that voter-history counts will not match tabulator-based official or unofficial results.

A registration count is a stock of records at a specified date and status; ballots cast is participation in one election; valid Senate votes are participation in one contest. Total population also includes children and people ineligible to vote. These denominators answer different questions. “Total voters” in this particular MDOS report is a tabulator-based count for this election, not population, registered voters, or a reusable eligible-voter denominator. A county with a high participation percentage can contribute few statewide votes; this report ranks actual contest volume.

## Historical comparison and completeness

**2022 midterm context:** the CSV includes `governor_2022_total` for every county, explicitly a Governor contest total rather than Senate votes or ballots cast. The [pinned OpenElections county data](https://github.com/openelections/openelections-data-mi/blob/2103114f669c2bb25f19792bf5ca290300381396/2022/20221108__mi__general__county.csv), retrieved 2026-10-17, supplies 1,411 Governor candidate rows across 83 counties, including zero-count write-ins. Their sum is **4,461,972**, agreeing with the [Michigan Legislature’s analysis of HB 5571](https://legislature.mi.gov/documents/2023-2024/billanalysis/House/pdf/2023-HLA-5571-211FCAD0.pdf), retrieved 2026-10-17. This is a secondary county compilation reconciled to a primary statewide volume; individual county allocations have not all been independently checked. The 2022 ballot fields remain blank. Comparing these values with 2024 Senate volume changes both the election year and contest; it cannot identify pure participation changes or candidate effects.

**2020 Senate:** the inspected [OpenElections county extract](https://github.com/openelections/openelections-data-mi/blob/2103114f669c2bb25f19792bf5ca290300381396/2020/20201103__mi__general__county.csv), retrieved 2026-10-17, has Senate rows for only **43 counties**, and its office rows include noncandidate categories such as under/overvotes and unresolved write-ins. Ballot rows cover only three counties. It is retained as evidence of incompleteness, not used as a statewide baseline. All 2020 comparison cells remain blank. Do not sum that raw file indiscriminately. A complete, consistently certified 2020 all-county extract remains outstanding.

The 2022 source's county label `Gd. Traverse` is normalized to `Grand Traverse`
before joining. Coordinator review checks all 83 output county volumes against
the independent partisanship extract, including Grand Traverse's 52,302 votes;
the completed output sums to 4,461,972. The rebuild rejects missing or zero
county volumes rather than allowing an unmatched county to become zero.

## Files and reproduction

- [All 83 counties, D/R/other, volumes, shares, flags](data/county-turnout.csv). County FIPS values are five-character strings. Blank optional counts mean unavailable, never zero.
- [Saved 2024 Michigan candidate input](data/turnout/medsl-mi2024-senate.csv); the upstream national file is filtered to Michigan without changing counts.
- [Calculation and assertions](data/turnout/build_turnout.py), [machine-readable checks](data/turnout/checks.json), and [primary-evidence downloader](data/turnout/fetch_evidence.py).
- [Evidence URL, retrieval time, HTTP status, and SHA-256 manifest](data/turnout/evidence-manifest.json); each refreshed CSV also has a `.retrieval.json` with pinned URL and upstream/saved checksums. HTTP headers and original small public PDFs are saved beside it. PDF text extracts were produced with `pdftotext -layout`.

Run `python3 senate/2026/michigan/data/turnout/build_turnout.py` for an offline rebuild. Add `--refresh` to retrieve the commit-pinned CSVs and regenerate their retrieval metadata. Run `fetch_evidence.py` separately to refresh primary evidence and HTTP metadata. The calculation checks 83 unique county FIPS, nine unique candidates per county, county sums against the derivative’s stated totals, every statewide candidate against the primary table, and 2022 county count/total. Percentages are calculated from unrounded integer counts; flags use integer arithmetic (`5*cumulative >= 4*statewide`).

The unresolved primary-state county download and exact county ballots are material gaps. The completed deliverable is an all-county official-returns-derived contest ranking with exact primary statewide reconciliation, not a claim that the blocked state export was successfully retrieved.

## All-county volume ranking

The table below is generated from the saved inputs by `build_turnout.py`; sources and vintages are described above. The CSV additionally retains D/R/other and both priority flags.

| Rank | County | Senate votes 2024 | State % | Cumulative % | Governor votes 2022 |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | Wayne | 838,859 | 15.0409 | 15.0409 | 645,739 |
| 2 | Oakland | 763,454 | 13.6889 | 28.7298 | 630,205 |
| 3 | Macomb | 498,724 | 8.9422 | 37.6720 | 384,544 |
| 4 | Kent | 368,158 | 6.6011 | 44.2731 | 299,872 |
| 5 | Genesee | 219,459 | 3.9349 | 48.2081 | 171,594 |
| 6 | Washtenaw | 219,069 | 3.9279 | 52.1360 | 180,848 |
| 7 | Ottawa | 177,092 | 3.1753 | 55.3113 | 146,432 |
| 8 | Ingham | 146,816 | 2.6324 | 57.9437 | 119,042 |
| 9 | Kalamazoo | 143,934 | 2.5808 | 60.5245 | 116,776 |
| 10 | Livingston | 131,252 | 2.3534 | 62.8779 | 108,839 |
| 11 | Saginaw | 101,936 | 1.8277 | 64.7056 | 81,550 |
| 12 | St. Clair | 94,432 | 1.6932 | 66.3988 | 74,505 |
| 13 | Muskegon | 93,438 | 1.6754 | 68.0742 | 73,836 |
| 14 | Monroe | 88,962 | 1.5951 | 69.6693 | 68,997 |
| 15 | Berrien | 83,160 | 1.4911 | 71.1603 | 64,024 |
| 16 | Jackson | 82,405 | 1.4775 | 72.6379 | 64,705 |
| 17 | Allegan | 71,370 | 1.2797 | 73.9176 | 57,342 |
| 18 | Calhoun | 67,202 | 1.2049 | 75.1225 | 51,576 |
| 19 | Eaton | 64,629 | 1.1588 | 76.2813 | 53,558 |
| 20 | Grand Traverse | 62,022 | 1.1121 | 77.3934 | 52,302 |
| 21 | Bay | 60,151 | 1.0785 | 78.4719 | 49,209 |
| 22 | Lapeer | 54,655 | 0.9800 | 79.4519 | 43,802 |
| 23 | Lenawee | 53,784 | 0.9644 | 80.4162 | 42,857 |
| 24 | Midland | 49,601 | 0.8894 | 81.3056 | 41,224 |
| 25 | Clinton | 49,545 | 0.8884 | 82.1939 | 41,204 |
| 26 | Van Buren | 40,596 | 0.7279 | 82.9218 | 31,922 |
| 27 | Shiawassee | 40,103 | 0.7191 | 83.6409 | 32,402 |
| 28 | Marquette | 38,389 | 0.6883 | 84.3292 | 31,369 |
| 29 | Barry | 38,132 | 0.6837 | 85.0129 | 30,697 |
| 30 | Montcalm | 34,328 | 0.6155 | 85.6284 | 26,395 |
| 31 | Ionia | 33,553 | 0.6016 | 86.2300 | 27,208 |
| 32 | Isabella | 30,256 | 0.5425 | 86.7725 | 23,957 |
| 33 | Tuscola | 30,140 | 0.5404 | 87.3129 | 24,007 |
| 34 | Newaygo | 28,837 | 0.5171 | 87.8300 | 22,761 |
| 35 | St. Joseph | 28,762 | 0.5157 | 88.3457 | 21,910 |
| 36 | Cass | 27,415 | 0.4916 | 88.8373 | 20,353 |
| 37 | Hillsdale | 24,405 | 0.4376 | 89.2748 | 18,650 |
| 38 | Sanilac | 23,007 | 0.4125 | 89.6874 | 18,804 |
| 39 | Emmet | 22,668 | 0.4064 | 90.0938 | 19,195 |
| 40 | Mecosta | 22,159 | 0.3973 | 90.4911 | 17,510 |
| 41 | Delta | 21,478 | 0.3851 | 90.8762 | 17,341 |
| 42 | Branch | 20,792 | 0.3728 | 91.2490 | 16,130 |
| 43 | Gratiot | 19,510 | 0.3498 | 91.5988 | 15,324 |
| 44 | Wexford | 19,214 | 0.3445 | 91.9434 | 15,105 |
| 45 | Houghton | 19,126 | 0.3429 | 92.2863 | 15,480 |
| 46 | Huron | 18,550 | 0.3326 | 92.6189 | 15,006 |
| 47 | Chippewa | 18,013 | 0.3230 | 92.9419 | 14,537 |
| 48 | Mason | 17,857 | 0.3202 | 93.2621 | 14,761 |
| 49 | Leelanau | 17,555 | 0.3148 | 93.5768 | 15,474 |
| 50 | Charlevoix | 17,384 | 0.3117 | 93.8885 | 14,669 |
| 51 | Clare | 16,993 | 0.3047 | 94.1932 | 13,198 |
| 52 | Alpena | 16,877 | 0.3026 | 94.4958 | 13,980 |
| 53 | Antrim | 16,732 | 0.3000 | 94.7958 | 14,014 |
| 54 | Cheboygan | 16,164 | 0.2898 | 95.0856 | 13,334 |
| 55 | Roscommon | 15,841 | 0.2840 | 95.3697 | 12,951 |
| 56 | Otsego | 15,739 | 0.2822 | 95.6519 | 12,505 |
| 57 | Iosco | 15,423 | 0.2765 | 95.9284 | 12,631 |
| 58 | Gladwin | 15,193 | 0.2724 | 96.2008 | 12,025 |
| 59 | Manistee | 15,125 | 0.2712 | 96.4720 | 12,646 |
| 60 | Dickinson | 15,102 | 0.2708 | 96.7428 | 11,986 |
| 61 | Oceana | 14,653 | 0.2627 | 97.0055 | 12,086 |
| 62 | Osceola | 13,008 | 0.2332 | 97.2388 | 10,379 |
| 63 | Benzie | 12,739 | 0.2284 | 97.4672 | 10,689 |
| 64 | Menominee | 12,703 | 0.2278 | 97.6949 | 9,676 |
| 65 | Ogemaw | 12,311 | 0.2207 | 97.9157 | 9,892 |
| 66 | Kalkaska | 11,315 | 0.2029 | 98.1186 | 8,854 |
| 67 | Missaukee | 9,018 | 0.1617 | 98.2803 | 7,448 |
| 68 | Arenac | 8,938 | 0.1603 | 98.4405 | 7,170 |
| 69 | Presque Isle | 8,606 | 0.1543 | 98.5948 | 7,298 |
| 70 | Crawford | 8,331 | 0.1494 | 98.7442 | 6,531 |
| 71 | Gogebic | 8,050 | 0.1443 | 98.8885 | 6,466 |
| 72 | Alcona | 7,367 | 0.1321 | 99.0206 | 5,981 |
| 73 | Mackinac | 7,104 | 0.1274 | 99.1480 | 5,999 |
| 74 | Iron | 6,904 | 0.1238 | 99.2718 | 5,620 |
| 75 | Lake | 6,767 | 0.1213 | 99.3931 | 5,260 |
| 76 | Montmorency | 6,271 | 0.1124 | 99.5056 | 5,119 |
| 77 | Alger | 5,158 | 0.0925 | 99.5981 | 4,326 |
| 78 | Oscoda | 5,072 | 0.0909 | 99.6890 | 4,012 |
| 79 | Schoolcraft | 4,794 | 0.0860 | 99.7750 | 3,888 |
| 80 | Baraga | 4,246 | 0.0761 | 99.8511 | 3,444 |
| 81 | Ontonagon | 3,774 | 0.0677 | 99.9188 | 3,259 |
| 82 | Luce | 2,946 | 0.0528 | 99.9716 | 2,366 |
| 83 | Keweenaw | 1,585 | 0.0284 | 100.0000 | 1,390 |
