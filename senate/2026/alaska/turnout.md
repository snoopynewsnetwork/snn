# Alaska's high-volume election reporting units

Research retrieved **2026-10-18 UTC / 2026-10-17 America/Chicago**. The baseline is **2024 presidential votes for all eight candidates in the official publication**, not ballots cast or registration. **Alaska had no 2024 U.S. Senate election.** The [Division's official archive](https://www.elections.alaska.gov/election-results/e/?id=24genr) supplies the presidential summary, statewide precinct CSV, and house-district statements used here.

**Exact top 15 house districts, descending presidential volume:** **6, 9, 3, 8, 23, 29, 25, 30, 24, 34, 11, 35, 16, 7, 36**. They contribute **156,277 / 338,177 = 46.21159925%**.

**Exact smallest district set reaching 80% (28 units), in rank order:** **6, 9, 3, 8, 23, 29, 25, 30, 24, 34, 11, 35, 16, 7, 36, 2, 26, 15, 28, 4, 21, 27, 33, 10, 1, 12, 5, 17**. These contribute **271,492 / 338,177 = 80.28103626%**. The largest 27 contribute **263,774 = 77.99879945%**; HD17 crosses the threshold. The integer threshold is 270,542 votes (`5*cumulative >= 4*338177`). Since the 27 largest units fall short, no other set of 27 can reach 80%. The top 15 are contained in this 28-unit research priority set.

The [exact dispatch JSON](data/turnout/priority-set.json) preserves the ordered district keys, native district numbers, official results-PDF URLs, observed map links, and every constituent source-unit key. For example, project key `24GENR:HD06` refers to native district `6` and official `HD6.pdf`. Map links identify the April 2024/May 2023 Final Proclamation assets; they do not establish approved November 2026 reporting boundaries. HD99 is outside the priority set but is always retained in statewide arithmetic.

## Complete native geography, without invented counties

The ranking has **41 nonoverlapping groups: House Districts 1-40 and the separate HD99 federal-overseas administrative unit**. Each HD1-40 total includes its physical precincts and its separately reported district Absentee, Early Voting, and Question units. These are actual native district statements, checked candidate by candidate against all 41 official PDFs; the [HD1 statement](https://www.elections.alaska.gov/results/24GENR/HD1.pdf), for example, explicitly includes all three administrative categories. The [HD99 statement](https://www.elections.alaska.gov/results/24GENR/HD99.pdf) contributes **401 presidential votes / 401 ballots / 806 registered voters**, rather than being allocated by assumption to a geographic district.

The project keeps the compatibility filename [county-turnout.csv](data/county-turnout.csv), but its rows are **Alaska native election reporting groups, not boroughs or census areas**. `reporting_geography`, `geography_type`, `native_house_district`, `district_key`, election, contest and boundary vintage describe each row. `county_fips` is blank; `state_fips=02` is meaningful. No county-equivalent totals or county polygons have been manufactured from unmatched districts.

The complete finer-level rankings are retained separately: **[all 523 units in 2024](data/turnout/reporting-units-2024.csv)** and **[all 522 units in 2022](data/turnout/reporting-units-2022.csv)**. Each is ranked by that year's all-candidate contest volume and has its own cumulative percentages and priority flags. Their `district_in_priority_set` flag identifies membership in the district research set; their generic `top15`/`smallest_80pct_set` flags instead refer to the finer-level ranking. Never add the district-summary and constituent-unit tables together.

| Coverage | 2024 president | 2022 Senate first choices |
| --- | ---: | ---: |
| Physical polling-place precincts | 402 | 401 |
| District Absentee administrative units | 40 | 40 |
| District Early Voting administrative units | 40 | 40 |
| District Question administrative units | 40 | 40 |
| Separate HD99 federal-overseas absentee unit | 1 | 1 |
| **All nonoverlapping reporting units** | **523** | **522** |
| Official summary's reported precinct denominator, including HD99 | 403 | 402 |
| District-level groups, including HD99 | 41 | 41 |

The official precinct denominator excludes the additional 120 district administrative records. It is not the number of records in the detailed reporting-unit table and is not the fraction of eventual votes counted. The source includes a Remote method column/category with zero votes and ballots in these contests; it does not create extra reporting units.

The 2024 CSV's `Pct_seq_nbr` is unique across all 523 units. The source has **80 blank `Pct_Id` values** (the early and question records); these stay blank. Derived key `24GENR:4:seq:<Pct_seq_nbr>` identifies a unit without inventing a precinct ID. Native `Pct_Id`, sequence, aggregation ID, reporting flag and exact label are preserved, including unusual administrative ID formats and doubled spaces in Question labels. The 2022 UTF-16 export has labels but no separate sequence/administrative-ID fields; its derived key records the election, contest and original TSV record ordinal, while literal precinct-ID prefixes and exact labels remain available. No region identifier is inferred from a numeric suffix.

## Statewide counts and candidate reconciliation

The [2024 official statewide summary](https://www.elections.alaska.gov/results/24GENR/ElectionSummaryReport.pdf), dated 2024-11-30 4:00:37 PM as printed (timezone unstated), reports **338,177 presidential votes, 340,981 voters/ballots cast and 611,078 registered voters**. It reports **1,996 undervotes and 808 overvotes** through the linked detailed CSV, exactly explaining the **2,804-ballot** difference. The official presidential table has eight named tickets and no separate write-in row; no extra presidential write-in count is invented.

The [2022 official statewide summary](https://elections.alaska.gov/results/22GENR/ElectionSummaryReportRPT.pdf), dated 2022-11-30 2:03:20 PM as printed (timezone unstated), reports **261,705 Senate first-choice votes including write-ins, 267,047 ballots and 601,795 registered voters**. The linked [official summary text export](https://elections.alaska.gov/results/22GENR/ElectionSummaryReportRPT.txt) supplies **4,857 undervotes and 485 overvotes**, exactly explaining the **5,342-ballot** difference. The PDF's header confusingly says “Registered Voters” before `267,047 of 601,795`; its explicit Ballots Cast line and the district statements establish which number is participation and which is registration.

| Election / candidate | Sum across every reporting unit | Official statewide summary | Difference |
| --- | ---: | ---: | ---: |
| 2024 Harris/Walz | 140,026 | 140,026 | 0 |
| 2024 Kennedy/Shanahan | 5,670 | 5,670 | 0 |
| 2024 Oliver/Maat | 3,040 | 3,040 | 0 |
| 2024 Sonski/Onak | 702 | 702 | 0 |
| 2024 Stein/Ware | 2,342 | 2,342 | 0 |
| 2024 Terry/Broden | 812 | 812 | 0 |
| 2024 Trump/Vance | 184,458 | 184,458 | 0 |
| 2024 West/Abdullah | 1,127 | 1,127 | 0 |
| **2024 all candidates** | **338,177** | **338,177** | **0** |
| 2022 Chesbro, Patricia R. | 27,145 | 27,145 | 0 |
| 2022 Kelley, Buzz A. | 7,557 | 7,557 | 0 |
| 2022 Murkowski, Lisa | 113,495 | 113,495 | 0 |
| 2022 Tshibaka, Kelly C. | 111,480 | 111,480 | 0 |
| 2022 Write-in | 2,028 | 2,028 | 0 |
| **2022 all first choices** | **261,705** | **261,705** | **0** |

The first-choice [2022 precinct export](https://elections.alaska.gov/results/22GENR/Results_per_Precinct_2022_11_30T14_17_52_To%20Excel.txt) retains an **“Unofficial” header** despite residing in the certified archive. This label is not silently removed or promoted into a certification claim. Every candidate total in every district independently matches that district's PDF labeled **OFFICIAL RESULTS**; statewide candidate totals also match the official summary. All 522 unit ballot and registration counts are separately extracted from the district PDFs' turnout tables. No counts have been rescaled.

Ballots cast records election participation; contest votes record valid choices in one contest; registration is a stock at the source's election snapshot. They are not interchangeable. The same district CSV provides a separate **ballots ranking** using `ballots_rank` and `ballots_*` cumulative/priority fields. For 2024 the ballot top 15 have the same membership (HD36 and HD7 swap order) and contribute **157,424 / 340,981 = 46.16796830%**. The smallest ballot set is also the same 28 districts, contributing **273,521 = 80.21590646%**; the largest 27 have **265,728 = 77.93044187%**. Ranking by valid presidential votes remains the dispatch default.

## Voting methods: source columns versus administrative labels

These statewide method totals use the 2024 CSV's actual method columns and the 2022 statewide summary text's explicit counting-group totals. They include HD99 in Absentee. [Method reconciliation](data/turnout/method-reconciliation.csv) retains the named-unit-category totals alongside the actual method totals.

| Election | Actual method | Contest votes | Ballots | Undervotes | Overvotes |
| --- | --- | ---: | ---: | ---: | ---: |
| 2024 president | Election Day | 175,911 | 177,498 | 1,143 | 444 |
| 2024 president | Absentee | 76,871 | 77,510 | 498 | 141 |
| 2024 president | Early Voting | 70,825 | 71,187 | 253 | 109 |
| 2024 president | Question | 14,570 | 14,786 | 102 | 114 |
| 2024 president | Remote | 0 | 0 | 0 | 0 |
| 2022 Senate | Election Day | 163,641 | 167,836 | 3,956 | 239 |
| 2022 Senate | Absentee | 54,108 | 54,433 | 200 | 125 |
| 2022 Senate | Early Voting | 36,887 | 37,562 | 606 | 69 |
| 2022 Senate | Question | 7,069 | 7,216 | 95 | 52 |
| 2022 Senate | Remote | 0 | 0 | 0 | 0 |

**A material 2024 classification exception:** the units named `District 6 - Early Voting`, `District 7 - Early Voting`, `District 8 - Early Voting` and `District 37 - Early Voting` contain both Election Day and Early Voting columns. Together they contain **1,958 Election Day votes / 1,965 Election Day ballots** in addition to their Early Voting components. Thus the 40 units named Early Voting total **72,783 votes / 73,152 ballots**, while the actual Early Voting column totals **70,825 / 71,187**. The physical-precinct labels total **173,953 / 175,533**, while the actual Election Day column totals **175,911 / 177,498**. This is retained as a source classification difference, with exact source keys and components in `checks.json`; no cause is asserted.

The finer-level CSV's `method` field denotes the **source-label category**. In 2024, the additional `election_day_*`, `early_voting_*`, etc. fields denote the actual method columns; use those for method analysis. The main district CSV explicitly distinguishes `*_label_category_*` and actual `*_votes`/`*_ballots`. District and statewide total votes remain unchanged whichever compatible view is selected. Do not add a unit total to its method components.

For 2022, named-unit categories reconcile exactly to all five statewide method totals and all **25 candidate-by-method** published cells. The precinct export does not provide a separately verified method matrix for each district/precinct, so actual-method district fields and per-unit under/overvotes remain blank. Named-category counts are preserved; their statewide agreement alone does not independently establish every finer method allocation. The formatted summary text repeats candidate display rows; the transformation verifies identical duplicate cells rather than adding those displays twice.

## Recent midterm comparator and RCV context

The comparator is **2022 U.S. Senate FIRST CHOICES, including the published Write-in category**. Its [41 native-group ranking](data/turnout/district-turnout-2022.csv) and [readable full table](data/turnout/ranking-table-2022.md) use their own election-specific keys. HD99 contributes **104 votes / 104 ballots / 634 registered voters**. The largest 15 contribute **124,122 / 261,705 = 47.42821115%**. The smallest 80% set has 28 groups and contributes **212,933 = 81.36374926%**; the largest 27 contribute **206,943 = 79.07491259%**. This is a midterm/contest comparison, not a pure estimate of turnout change or a 2026 participation forecast.

The Division's [district-map documentation](https://www.elections.alaska.gov/research/district-maps/) describes precincts approved in April 2024 conforming to the **May 15, 2023 Final Proclamation**. The 2022 returns retain their 2022 reporting vintage. **Neither 2020-to-2022 nor 2022-to-2024 district-number/precinct-number joins are performed here.** No validated crosswalk has been supplied. Matching district numbers across these elections is not evidence of identical boundaries, and no 2020 baseline is manufactured.

The current [official election information](https://www.elections.alaska.gov/election-information/) describes general-election ranked choice voting. The [2022 official Senate RCV report](https://elections.alaska.gov/results/22GENR/US%20SEN.pdf) is retained separately from the complete first-choice publication:

| RCV round | Chesbro | Kelley | Murkowski | Tshibaka | Continuing | Blanks | Exhausted | Overvotes | Nontransferable |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 28,233 | 8,575 | 114,118 | 112,101 | 263,027 | 3,271 | 0 | 499 | 3,770 |
| 2 | 29,134 | 0 | 115,759 | 115,310 | 260,203 | 3,271 | 2,806 | 517 | 6,594 |
| 3 | 0 | 0 | 136,330 | 117,534 | 253,864 | 3,271 | 9,107 | 555 | 12,933 |

Every round accounts for **266,797 ballots** (`continuing + nontransferable`), **250 fewer** than the complete first-choice publication's **267,047 ballots**. The report explicitly excludes unresolved write-ins and uses continuing ballots for its threshold. Its first RCV allocation is not the raw first-choice table: for example, Murkowski is 114,118 rather than 113,495. The final 53.70%/46.30% percentages use **253,864 continuing ballots**, not all ballots cast or all first choices. Both finalists are Republicans.

This turnout evidence independently verifies the published 250-ballot population difference and retains it in [parsed RCV checks](data/turnout/senate-rcv2022-parsed.json); it does not splice scanner/manual or later preferences into first-choice geography. The companion worker's [CVR coverage audit](data/baselines/cvr-ballot-coverage-gaps.csv) identifies five wholly absent precincts (37-750 St. George Island; 40-002 Ambler; 40-018 Kiana; 40-022 Kobuk; 40-028 Noorvik) and six additional missing ballots in partially covered 37-730 Levelock. Those six rows account for 250 missing ballots and 237 missing candidate votes; the companion audit attributes the remaining 13 to undervotes. The full-ballot cells for these units independently match our official HD-PDF extraction; the scanner/CVR side belongs to that separately retained audit, not this turnout parser. Our [peer check metadata](data/turnout/peer-hd-cross-check.json) pins the observed audit hash. A successful replay of the published RCV population does not fill missing CVR sessions. **Never add the three rounds together, substitute final continuing votes for turnout, or present the first-choice table as the final-round allocation.**

## Evidence, reproduction and validation

All underlying responses are primary Division publications. [The manifest](data/turnout/evidence-manifest.json) records **96 successful default-TLS-verified responses**, UTC retrieval start/end times, exact URLs, HTTP status/effective URLs, response headers and SHA-256 hashes. Original CSV, UTF-16 text and HTML responses are stored losslessly as `.gz`; both original-response and stored-archive hashes are retained. All **82 original HD PDFs**, both statewide summaries, the 2022 RCV report, and additional official evidence remain under [data/turnout](data/turnout/README.md). Each response has its own `.headers` and `.retrieval.json`. The source bytes, not browser/search snippets, drive the calculations. Read-only PDF inspection includes saved rendered statewide/RCV pages and text extracts.

Run:

```sh
python3 senate/2026/alaska/data/turnout/build_turnout.py
```

The offline rebuild requires Python's standard library and Poppler `pdftotext`. [The transformation](data/turnout/build_turnout.py) selects 2024 contest ID `4`, preserves all eight candidate rows per source unit, decodes the 2022 TSV as UTF-16, selects only U.S. Senator first choices, removes the explicit statewide Total row from geographic addition, and validates native district aggregation against every district PDF. It reads each unit's repeated ballot/registration/under/over fields once, rather than once per candidate. It sorts integer volumes and only then calculates displayed percentages. Ranking ties use the election-specific source/district key as a deterministic tie break.

[Machine-readable checks](data/turnout/checks.json), [statewide candidate reconciliation](data/turnout/candidate-reconciliation.csv), [697 district comparisons](data/turnout/district-reconciliation.csv), [method reconciliation](data/turnout/method-reconciliation.csv), and [25 2022 candidate/method comparisons](data/turnout/method-candidate-reconciliation-2022.csv) pass. The rebuild verifies complete/unique geography, nonnegative counts, every statewide candidate, all district candidate/ballot/registration totals, all 2024 unit and method ballot identities, all 2022 unit ballots from PDFs, method coverage, exact 80% minimality, RCV population identities and every successful saved primary/HTTP-header hash. There are **zero district or statewide first-choice reconciliation differences**. The separate RCV population difference and 2024 label/method classification difference remain explicit.

An additional [independent peer HD comparison](data/turnout/peer-hd-cross-check.csv) matches the partisanship worker's separately collected baseline in **all 82 year/district totals**, including HD99. [Its script](data/turnout/cross_check_peer.py) and [observed file hashes](data/turnout/peer-hd-cross-check.json) are retained. It compares HD numbers only within the same election; it does not create a cross-year join or make the peer files a dependency of the primary turnout rebuild.

[The downloader](data/turnout/fetch_evidence.py) uses system curl with default certificate validation, never an insecure TLS override. `--refresh` re-fetches the manifest's successful sources; an individual `NAME URL` pair refreshes one source. Refreshes replace research observations, so preserve a snapshot before changing a reviewed baseline. The [2024 combined ballot-count link](https://www.elections.alaska.gov/results/24GENR/20241204_Combined-Ballot-Count-Report.html) returned HTTP 405 in this bounded attempt; its headers and failure metadata are retained. It is not needed for the fully reconciled contest/ballot ranking and is not claimed downloaded.

Substantive limits remain: no approved November 2026 precinct/results crosswalk or map vintage, no cross-year district-number join, no independent per-unit 2022 method/under/over matrix, and a distinct 250-ballot first-choice/RCV coverage difference. These are historical volume priorities, not a demonstrated live feed, an election-night completion estimate, or a calibrated probability.

## All-group 2024 volume ranking

The following table is regenerated from the retained primary evidence; its district summaries include the separately preserved administrative categories.

<!-- BEGIN GENERATED RANKING -->
| Rank | Native reporting geography | President votes 2024 | State % | Cumulative % | Ballots 2024 |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | House District 6 | 12,000 | 3.5484 | 3.5484 | 12,063 |
| 2 | House District 9 | 11,836 | 3.4999 | 7.0484 | 11,938 |
| 3 | House District 3 | 11,107 | 3.2844 | 10.3328 | 11,170 |
| 4 | House District 8 | 10,805 | 3.1951 | 13.5278 | 10,868 |
| 5 | House District 23 | 10,685 | 3.1596 | 16.6874 | 10,742 |
| 6 | House District 29 | 10,500 | 3.1049 | 19.7923 | 10,570 |
| 7 | House District 25 | 10,460 | 3.0931 | 22.8854 | 10,532 |
| 8 | House District 30 | 10,306 | 3.0475 | 25.9329 | 10,389 |
| 9 | House District 24 | 10,118 | 2.9919 | 28.9248 | 10,182 |
| 10 | House District 34 | 10,012 | 2.9606 | 31.8854 | 10,092 |
| 11 | House District 11 | 9,840 | 2.9097 | 34.7951 | 9,928 |
| 12 | House District 35 | 9,732 | 2.8778 | 37.6729 | 9,797 |
| 13 | House District 16 | 9,669 | 2.8592 | 40.5320 | 9,746 |
| 14 | House District 7 | 9,609 | 2.8414 | 43.3734 | 9,687 |
| 15 | House District 36 | 9,598 | 2.8382 | 46.2116 | 9,720 |
| 16 | House District 2 | 9,563 | 2.8278 | 49.0394 | 9,666 |
| 17 | House District 26 | 9,448 | 2.7938 | 51.8332 | 9,492 |
| 18 | House District 15 | 9,293 | 2.7480 | 54.5812 | 9,381 |
| 19 | House District 28 | 9,279 | 2.7438 | 57.3250 | 9,331 |
| 20 | House District 4 | 9,270 | 2.7412 | 60.0662 | 9,335 |
| 21 | House District 21 | 9,043 | 2.6740 | 62.7402 | 9,108 |
| 22 | House District 27 | 8,860 | 2.6199 | 65.3602 | 8,912 |
| 23 | House District 33 | 8,859 | 2.6196 | 67.9798 | 8,900 |
| 24 | House District 10 | 8,763 | 2.5912 | 70.5710 | 8,844 |
| 25 | House District 1 | 8,584 | 2.5383 | 73.1093 | 8,669 |
| 26 | House District 12 | 8,515 | 2.5179 | 75.6273 | 8,569 |
| 27 | House District 5 | 8,020 | 2.3715 | 77.9988 | 8,097 |
| 28 | House District 17 | 7,718 | 2.2822 | 80.2810 | 7,793 |
| 29 | House District 13 | 7,577 | 2.2405 | 82.5216 | 7,632 |
| 30 | House District 14 | 7,426 | 2.1959 | 84.7175 | 7,495 |
| 31 | House District 20 | 7,267 | 2.1489 | 86.8663 | 7,327 |
| 32 | House District 31 | 7,003 | 2.0708 | 88.9372 | 7,084 |
| 33 | House District 32 | 5,864 | 1.7340 | 90.6712 | 5,901 |
| 34 | House District 22 | 5,463 | 1.6154 | 92.2866 | 5,521 |
| 35 | House District 19 | 5,025 | 1.4859 | 93.7725 | 5,066 |
| 36 | House District 18 | 4,816 | 1.4241 | 95.1966 | 4,840 |
| 37 | House District 37 | 4,350 | 1.2863 | 96.4829 | 4,444 |
| 38 | House District 39 | 4,206 | 1.2437 | 97.7266 | 4,308 |
| 39 | House District 38 | 3,994 | 1.1810 | 98.9077 | 4,079 |
| 40 | House District 40 | 3,293 | 0.9738 | 99.8814 | 3,362 |
| 41 | HD99 Fed Overseas Absentee | 401 | 0.1186 | 100.0000 | 401 |
<!-- END GENERATED RANKING -->
