# New Hampshire turnout volume: towns, city wards and retained administrative labels

Research observed 2026-10-18 UTC. **Priority basis: November 5, 2024 president, four printed tickets plus the source's generic Write-Ins.** The complete original contains 320 native labels. This report ranks their reported numeric candidate/write-in subtotals, not ballots cast or participation rates. No county summary or city parent is added to its component rows. Primary basis: [SOS original `_3` workbook, archived 2024-12-19](https://web.archive.org/web/20241219142947id_/https://www.sos.nh.gov/sites/g/files/ehbemt561/files/inline-documents/sonh/2024-ge-president_3.xls); [independent extraction and controls](data/turnout/reconciliation.json).

**Top 15:** Salem, Derry, Merrimack, Londonderry, Bedford, Hudson, Goffstown, Hampton, Exeter, Windham, Milford, Pelham, Hooksett, Durham, Amherst. Their exact share is **185,659 / 826,189 = 22.4717346757219%**.

**Minimum descending set reaching 80%: the first 143 native rows in the complete order below.** They contribute **662,624 / 826,189 = 80.2024718315059%**. The first **142** contribute **660,378 / 826,189 = 79.930621201686%**. **Tilton, 2,246 votes, crosses at rank 143.** The integer threshold is 660,952: `5 * 660378 < 4 * 826189 <= 5 * 662624`. Since the largest 142 rows fall short, no set of 142 rows can reach 80%. The remaining **177 labels supply 163,565 votes (19.797528168494%)** and remain in every state total. Top 15 is contained within the 143-row priority. [Exact ordered dispatch contract](data/turnout/priority-set.json); [all 320 rows](data/county-turnout.csv).

## Correct election and seat context

The Senate identifies Shaheen's seat as Class II, elected in November 2020 for the term ending January 2027; Hassan's Class III seat was elected in November 2022. Thus 2020 Shaheen–Messner–O'Donnell is the same-seat baseline, and 2022 Hassan–Bolduc–Kauffman is the actual recent midterm comparator. New Hampshire had no 2024 Senate election; its 2024 official index lists president and governor, and its House Clerk federal table has president and House contests. The current SOS calendar gives September 8, 2026 primary and November 3, 2026 general. Sources: [Senate Class II](https://www.senate.gov/senators/Class_II.htm), [Class III](https://www.senate.gov/senators/Class_III.htm), [SOS 2026 calendar](https://www.sos.nh.gov/elections/2026-2027-political-calendar), [actual official 2024 index, archived September 2026](https://web.archive.org/web/20260917180704id_/https://www.sos.nh.gov/2024-general-election-results), [House Clerk 2024](https://clerk.house.gov/member_info/electionInfo/2024/statistics2024.pdf). Fresh direct SOS index/calendar requests returned 403; current indexed official text was inspected, and original archived publications were recovered separately. No 2024 Senate figures or 2022 presidential figures are fabricated.

## Disjoint accounting and native identity

The selected workbook supplies **73 explicitly labeled city-ward rows**, **Berlin as one city row**, and **246 other town/territory labels**. It has 12 distinct explicitly named warded city parents. County summaries and ten county footers are controls, not extra reporting leaves. Berlin is not expanded into guessed wards; Derry is not split into invented districts. Polling sites, ballot styles, VTDs, absentee counting groups and 2026 precinct geometry are not supplied by this source. [Native hierarchy and source locators](data/turnout/geography.json); [original workbook](https://web.archive.org/web/20241219142947id_/https://www.sos.nh.gov/sites/g/files/ehbemt561/files/inline-documents/sonh/2024-ge-president_3.xls).

`county-turnout.csv` is a compatibility filename: each of its 320 rows is a native accounting leaf, not one of ten county aggregates. `geography_key` is a project key made from the 2024 contest, verified county FIPS and percent-encoded, whitespace-trimmed literal label. It is **not a source-native numeric ID**. The original supplies labels, sheet names and row positions, not numeric precinct IDs; these positions and literal labels survive separately. Ward numbers are always qualified by their explicit city parent. The contract inventories every available native row in all retained result/administrative vintages, including blank/dash cases and unavailable finer constituents.

County FIPS are verified against [the Census 2020 official subdivision code list](https://www2.census.gov/geo/docs/reference/codes2020/cousub/st33_nh_cousub2020.txt). Exact county-scoped town/city/township name matches provide parent Census GEOIDs for 302 native rows. **18 administrative/abbreviated labels remain without a parent GEOID**; no name-similarity crosswalk is guessed. A Census parent identifier is not a ward FIPS, approved precinct boundary, election authority, or proof of cross-year geometry. All 18 stay in the accounting and dispatch roster. Actual clerk channels must be established from actual official publications; a county or town name alone conveys no clerk authority.

There are **20 rows with at least one unpopulated candidate field**; **16 have all four printed-ticket fields blank and generic Write-Ins numerically 0**. Their reported numeric subtotal is 0, but their candidate cells are null/blank, not invented zeros. Four other partly populated candidate rows are Springfield (Oliver and Stein blank), Milan (Stein blank), Waterville Valley (Stein blank), and Millsfield (Oliver and Stein blank). Three additional rows have only missing under/over fields: Manchester Ward 7, Wentworth and Monroe. All seven statewide numeric columns reconcile despite those literals. No unexplained candidate residual is distributed. The bottom-of-order tie rule is county FIPS then trimmed literal label. [Original BIFF source](https://web.archive.org/web/20241219142947id_/https://www.sos.nh.gov/sites/g/files/ehbemt561/files/inline-documents/sonh/2024-ge-president_3.xls); [explicit missing-cell audit](data/turnout/reconciliation.json).

## Candidate universe and whole-state primary reconciliation

The source's printed tickets are Harris/Walz (Democratic), Trump/Vance (Republican), Oliver/ter Maat (Libertarian), and Stein/Ware (Green). It reports one generic `Write-Ins` column, not a named or legally validated write-in allocation. Those five categories are the complete reported priority universe. Generic write-ins must not be added again as named write-ins. The [FEC January 16, 2025 compilation](https://www.fec.gov/documents/5644/2024presgeresults.pdf) reports the same four tickets plus 4,073 scattered write-ins and 826,189 total. Neither it nor the original establishes named write-in totals or the legal validity of every generic mark. A separate named/valid write-in allocation remains unavailable for this source scope. [Candidate/party identities and literal header positions](data/turnout/contest-candidates.json).

| 2024 source category | Sum of all native rows | County footers/summary/state | House Clerk | FEC |
| --- | ---: | ---: | ---: | ---: |
| Harris / Walz, d | 418,488 | 418,488 | 418,488 | 418,488 |
| Trump / Vance, r | 395,523 | 395,523 | 395,523 | 395,523 |
| Oliver / ter Maat, l | 4,425 | 4,425 | 4,425 | 4,425 |
| Stein / Ware, g | 3,680 | 3,680 | 3,680 | 3,680 |
| Generic Write-Ins / scattered | 4,073 | 4,073 | 4,073 | 4,073 |
| **Candidate/write-in subtotal** | **826,189** | **826,189** | **826,189, calculated** | **826,189** |
| Undervotes, separate | 4,482 | 4,482 | 4,482 | Not this table's candidate total |
| Overvotes, separate | 362 | 362 | 362 | Not this table's candidate total |

Every county balances for every column; no county is omitted. The named-ticket sum is 822,116; D+R is 814,011; the two minor tickets plus generic write-ins total 12,178. Candidate/write-in votes plus under/over total **831,033**, a contest-category sum, **not the separate ballots-cast report**. Sources: [SOS `_3`](https://web.archive.org/web/20241219142947id_/https://www.sos.nh.gov/sites/g/files/ehbemt561/files/inline-documents/sonh/2024-ge-president_3.xls), [House Clerk federal statistics](https://clerk.house.gov/member_info/electionInfo/2024/statistics2024.pdf), [FEC candidate table](https://www.fec.gov/documents/5644/2024presgeresults.pdf); [checks and full county controls](data/turnout/reconciliation.json).

The retained NARA certificate repeats four electors per slate and two certificate pages: its four slate totals are counted once (822,116), not four times or twice. One page is marked Amended with testimony year 2024; the other literally prints 2020 with a 2024 election header, and the four totals agree. Its release/correction chronology is unproved. It cannot control generic write-ins or municipal/ward allocations. [Original NARA New Hampshire ascertainment](https://www.archives.gov/files/electoral-college/2024/ascertainment-new-hampshire.pdf); [coordinator's read-only visual evidence](data/news/nara-state-control.json).

## Same-seat 2020 and actual 2022 midterm

Each selected Senate original independently retains **320 native labels, ten county footers and ten county summaries**. All numeric native, county and statewide candidate sums agree. In 2020, source dashes remain dashes/null: Coos scatter is a dash in its controls, while its populated rows have numeric 0; neither is silently recoded to the other. `Keene Ward 3*` and `Millsfield*` retain their literal asterisks and the source's correction footnotes. The 2022 remediated PDF and `_5` have identical candidate count vectors in county-table order; administrative abbreviations remain literal and are not used as a geographic crosswalk. [2020 original Senate PDF](https://web.archive.org/web/20221106132236id_/https://www.sos.nh.gov/sites/g/files/ehbemt561/files/documents/2020%20GE%20Election%20Tallies/2020-ge-united-states-senate.pdf), [2022 `_5` Senate original](https://web.archive.org/web/20240114224201id_/https://www.sos.nh.gov/sites/g/files/ehbemt561/files/inline-documents/sonh/2022-ge-us-senator_5.xls), [2022 remediated Senate PDF](https://web.archive.org/web/20230322192318id_/https://www.sos.nh.gov/sites/g/files/ehbemt561/files/inline-documents/sonh/2022-ge-us-senator-remediated_1.pdf).

| Contest | Democrat | Republican | Libertarian | Scatter | All reported candidate/scatter votes |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2020 Senate, same Class II seat | Jeanne Shaheen 450,778 | Corky Messner 326,229 | Justin O'Donnell 18,421 | 486 | **795,914** |
| 2022 Senate, other Class III seat, selected later SOS version | Maggie Hassan 332,490 | Donald C. Bolduc 275,631 | Jeremy Kauffman 12,390 | 464 | **620,975** |

The 2022 `_5` **summary** orders Hassan then Bolduc, while its **detail** orders Bolduc then Hassan. Candidate identity comes from each actual header, not a fixed column or the worksheets' misleading `gov` suffix. Earlier originals remain intact. The base workbook reports Hassan 333,217 / Bolduc 275,930 / Kauffman 12,280 / Scatter 459; `_1`: 333,193 / 275,928 / 12,390 / 464; `_2`: 332,193 / 275,928 / 12,390 / 464. `_5` and the remediated PDF report the table above. The freshly retrieved [House Clerk 2022 PDF](https://clerk.house.gov/member_info/electionInfo/2022/statistics2022.pdf) still matches `_2`, with 297 fewer Hassan votes and 297 more Bolduc votes than the selected later SOS version. Both sum to 620,975. No source is rescaled or mixed, and archive capture/suffix/Last-Modified clocks do not prove the cause or precise public release sequence. [Every retained vintage and row-level disagreement](data/turnout/vintage-differences.json).

The 2024 `_0` presidential workbook reports 418,351 / 395,397 / 4,424 / 3,676 / 4,070 generic marks (plus 4,473 under / 353 over). The unsuffixed workbook captured in June 2025 reports 418,354 / 395,408 / 4,423 / 3,676 / 3,934 (plus 4,400 / 353). Later capture alone does not make it the accepted replacement: the [actual SOS index archived September 17, 2026](https://web.archive.org/web/20260917180704id_/https://www.sos.nh.gov/2024-general-election-results) specifically links `_3`, `_14` ballots and `_7` checklist. `_3` also agrees with the national primary controls. All indexed originals recovered here remain in provenance. [Full source-scoped states](data/turnout/controls.json).

## Ballots, registration and method sensitivity

These are separate official administrative products. `Regular` and `Absentee` are their actual method labels; no candidate-by-method allocation, central absentee board, early-vote subdivision, blank count or Senate under/over count is synthesized. They have all 320 native labels, with original cells and positions retained. Checklist is the source's registration stock for the named general election, by Republican/Democratic/Undeclared, with polling-place registrations reported separately. The workbooks do not establish an active/inactive split or a precise statewide snapshot hour; amendment/capture dates are not registration as-of dates. Polling-place registrations are not added to checklist totals. Sources: [2020 ballots](https://web.archive.org/web/20240717182706id_/https://www.sos.nh.gov/sites/g/files/ehbemt561/files/documents/2020%20GE%20Election%20Tallies/2020-ge-ballots-cast.xls), [2020 checklist](https://web.archive.org/web/20240717182711id_/https://www.sos.nh.gov/sites/g/files/ehbemt561/files/documents/2020%20GE%20Election%20Tallies/2020-ge-names-on-checklist.xlsx), [2022 ballots `_3`](https://web.archive.org/web/20230125001254id_/https://www.sos.nh.gov/sites/g/files/ehbemt561/files/inline-documents/sonh/2022-ge-ballots-cast_3.xls), [2022 checklist `_2`](https://web.archive.org/web/20240114224201id_/https://www.sos.nh.gov/sites/g/files/ehbemt561/files/inline-documents/sonh/2022-ge-names-on-checklist_2.xlsx), [2024 ballots `_14`](https://web.archive.org/web/20250611055417id_/https://www.sos.nh.gov/sites/g/files/ehbemt561/files/inline-documents/sonh/2024-ge-ballots-cast_14.xls), [2024 checklist `_7`](https://web.archive.org/web/20250611055423id_/https://www.sos.nh.gov/sites/g/files/ehbemt561/files/inline-documents/sonh/2024-ge-names-on-checklist_7.xlsx).

| Measure | 2020 general | 2022 general, actual midterm | 2024 general |
| --- | ---: | ---: | ---: |
| Selected Senate/president candidate + generic/scatter | 795,914 Senate | 620,975 Senate | 826,189 president |
| Ballots, source statewide summary | 814,499 | 626,931 | 831,467 |
| Ballots, sum of native Total cells | 814,499 | 626,931 | **831,468** |
| Regular, native sum | 554,282 | 568,276 | 731,944 |
| Absentee, native sum | 260,217 | 58,655 | **99,525** |
| Checklist total, native and state | 1,119,232 | 925,398 | 1,013,075 |
| Polling-place registrations, source Total column | 75,611 | 48,615 | 96,623 |

**Known administrative disagreements are retained, not repaired.** In 2024 `_14`, Coos native/footer Absentee is 1,968 and Total 17,511, versus summary 1,967 and 17,510. Somersworth Ward 3 has Regular 1,119 + Absentee 103 = 1,222, versus its literal Total 1,221. Thus native method components sum to 831,469, native Total to 831,468, state summary Total to 831,467, and state summary method components to 831,468. These are four specified scopes, not one interchangeable exact ballot figure. Hopkinton's polling-place registration components 55 + 46 + 195 = 296, but its literal Total is 3; the state component sum is 96,916 versus Total 96,623, a 293 difference. The separately reported checklist party stock does balance exactly. [2024 ballot original](https://web.archive.org/web/20250611055417id_/https://www.sos.nh.gov/sites/g/files/ehbemt561/files/inline-documents/sonh/2024-ge-ballots-cast_14.xls); [2024 checklist original](https://web.archive.org/web/20250611055423id_/https://www.sos.nh.gov/sites/g/files/ehbemt561/files/inline-documents/sonh/2024-ge-names-on-checklist_7.xlsx); [complete field/row audits](data/turnout/administrative-audit.json).

The earlier 2024 ballot `_6` summary is 832,518; native Totals sum to 832,517 (Strafford footer/native 77,188 versus summary 77,189). It retains its own arithmetic and is not blended into `_14`. Earlier ballot/checklist originals and every original amendment byte remain recoverable. In 2022 `_3`, all native method/Total fields and county/state controls agree at 626,931, and the workbook literally notes an update on 12.8.22. The 2020 total is 814,499 with a literal update note 11.19.20; its original places paired county tables side by side, so source column A or G is retained as part of each locator. [2024 `_6` original](https://web.archive.org/web/20241219122521id_/https://www.sos.nh.gov/sites/g/files/ehbemt561/files/inline-documents/sonh/2024-ge-ballots-cast_6.xls), [2022 `_3` original](https://web.archive.org/web/20230125001254id_/https://www.sos.nh.gov/sites/g/files/ehbemt561/files/inline-documents/sonh/2022-ge-ballots-cast_3.xls), [2020 original](https://web.archive.org/web/20240717182706id_/https://www.sos.nh.gov/sites/g/files/ehbemt561/files/documents/2020%20GE%20Election%20Tallies/2020-ge-ballots-cast.xls).

2024 native ballots exceed candidate/write-in marks by 5,279 and the contest-category sum including under/over by 435. The corresponding ballot-minus-Senate-mark gaps are 18,585 in 2020 and 5,956 in 2022. These subtractions **do not identify blank ballots, invalid write-ins, unreported undervotes or voter eligibility**, since the products have distinct source vintages and definitions. Blank/under/over fields absent from Senate originals remain unavailable. Ballots divided by checklist are descriptive source-product ratios, not voting-eligible turnout or a 2026 forecast: 2020 72.77302650%, 2022 67.74717473%, and 2024 82.07368655% using native Total cells (the 831,467 summary gives 82.07358784%).

Re-ranking each complete source by its own reported measure produces the sensitivities below. Each has its own complete order in [sensitivity.json](data/turnout/sensitivity.json); no current or cross-year geographic equivalence is inferred. The fixed 143-row priority has exact literal county/label matches in the selected 2024 administrative files: it contains 666,554 / 831,468 = 80.16592340% of native ballot Total cells, and 817,376 / 1,013,075 = 80.68267404% of checklist stock. It also has exact literal county/label matches in the 2022 Senate original and contributes 495,056 / 620,975 = 79.72237208% there. These are source-label comparisons, not ward-boundary crosswalks. No partial matching sample is presented as a complete fixed-set ballot comparison.

| Source-scoped measure | State native sum | Top-15 votes / share | Minimum 80% count | Preceding votes | Crossing label | Crossing cumulative | Remainder votes |
| --- | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| 2022 Senate | 620,975 | 137,357 / 22.11957003% | 144 | 495,676 | Concord Ward 2 | 497,331 | 123,644 |
| 2020 Senate | 795,914 | 180,133 / 22.63221906% | 141 | 634,898 | Haverhill | 637,021 | 158,893 |
| 2024 ballot Total cells (summary differs) | 831,468 | 186,531 / 22.43393612% | 143 | 664,305 | Tilton | 666,554 | 164,914 |
| 2022 ballot Total | 626,931 | 138,389 / 22.07404005% | 145 | 501,502 | Laconia Ward 1 | 503,147 | 123,784 |
| 2020 ballot Total | 814,499 | 184,847 / 22.69456439% | 142 | 651,297 | Concord Ward 4 | 653,438 | 161,061 |
| 2024 checklist Total | 1,013,075 | 228,463 / 22.55143992% | 141 | 809,148 | Walpole | 811,982 | 201,093 |
| 2022 checklist Total | 925,398 | 207,090 / 22.37847931% | 141 | 738,801 | Concord Ward 2 | 741,413 | 183,985 |
| 2020 checklist Total | 1,119,232 | 260,449 / 23.27033180% | 139 | 894,823 | Winchester | 898,065 | 221,167 |

## Provenance, publication status and reproduction

These are official historical result/administrative publications recovered as complete archived original files after current SOS access failures, with the selected 2024 index chain recovered independently. National certificate/statistics controls corroborate specified scopes. The worksheets are not timestamped live snapshots, and this work does not assign a certification date or legal status to every generic write-in. The [official 2024 media guide](https://web.archive.org/web/20241030010219id_/https://www.sos.nh.gov/sites/g/files/ehbemt561/files/documents/2024-10/2024-state-general-election-media-guide.pdf) describes moderator announcements, Return of Votes delivery to SOS, post-election certificates and the state's certification process. It does not establish actual November 2026 cadence. Current local-clerk authority/feeds remain separate research work.

Newsroom/volunteer preparation stays outside the baseline. The [retained coordinator newsroom evidence](local-news-results.md) distinguishes NHPR/WMUR historical/primary products, shared AP suppliers and `nhelectionresults.org`'s expressly unofficial clerk/volunteer returns and statistical projections. A volunteer site's 317/320 polling-place flag or a newsroom's 318 flag is not proof of this source's reporting geography, complete certified returns or a November roster. No projections are added to reported votes. No collector, calibrated Needle, 2026 turnout forecast, approved current precinct map or live cadence is claimed.

- [Source schema, exact decoding/rebuild instructions and known gaps](data/turnout/source/SCHEMA.md).
- [Lossless shared-original references, hashes, HTTP metadata and original/download chains](data/turnout/source/shared-originals.json); new captures have individual `.json`, `.headers.txt` and `.body.gz` under `data/turnout/source/`. The shared news originals are reused read-only, not duplicated. Source UTC retrieval, archive capture, election header, HTTP Last-Modified and document update notes are distinct clocks.
- [Original-byte extraction](data/turnout/extract.py), [calculation](data/turnout/build_turnout.py), [report generator](data/turnout/report.py), [offline validator](data/turnout/validate_turnout.py), [acquisition](data/turnout/acquire.py).
- [All candidate/method/registration source-native field records](data/turnout/native-fields.jsonl.gz), [primary balances](data/turnout/reconciliation.json), [vintage differences](data/turnout/vintage-differences.json), [validation](data/turnout/validation.json), [complete owned asset manifest](data/turnout/asset-manifest.json).

The [actual reciprocal peer agreement](data/turnout/peer-agreement.json) records **agreed_after_independent_full_comparison** for peer `d272caf4-db4f-4c84-8950-c5e0fabe93e7`. [Reproducible read-only comparison](data/turnout/compare_peer.py) checks all 23 × 320 native rows, all 34,880 parsed fields and raw values, source positions, shared BIFF types, primary original hashes, county/state controls, the 960-row baseline CSV, and every priority row/key/order/threshold. It reports zero disagreements. Each worker extracted originals independently; peer outputs were not used as count/build inputs or edited to match.

The **frozen** dispatch contract refers only by path to `data/coordinator-priority-acceptance.json`, relative to this state directory. That external, coordinator-owned record alone grants historical acceptance; the contract's worker flag remains provisional/false. It contains no reverse acceptance hash. Acceptance and current-boundary approval are separate: arithmetic agreement does not approve legal geography, clerk authority or future reporting equivalence.

**Historical dispatch formally accepted at 2026-10-18T18:25:45.184946+00:00** in the [coordinator-owned acceptance record](data/coordinator-priority-acceptance.json). Its scope is historical research dispatch only. Current geometry, clerk authority, live feeds, valid/named write-in allocation and calibrated models remain unapproved. A [separate reciprocal control supplement](data/turnout/peer-control-agreement.json) additionally compares all 483 county-summary, county-footer and state-summary records (2,289 fields) with zero disagreements; the accepted peer record stays byte-for-byte unchanged.

## Complete native order and remainder

Every row below comes from [the selected official `_3` presidential workbook](https://web.archive.org/web/20241219142947id_/https://www.sos.nh.gov/sites/g/files/ehbemt561/files/inline-documents/sonh/2024-ge-president_3.xls). Votes exclude under/over and are numeric reported subtotals; `†` marks at least one blank candidate field, with literal cells retained in the CSV/native extracts. City parents and county controls are never extra rows. `Priority` is the union of top 15 and minimum-80%; **ranks 144–320 are the full remainder**, including 16 unpopulated printed-ticket rows with generic numeric 0. Percentage displays are rounded; exact integer counts govern membership.

| Rank | County context | Native label | Reported candidate/write-in votes | Cumulative votes | Cumulative % | Priority |
| ---: | --- | --- | ---: | ---: | ---: | --- |
| 1 | Rockingham | Salem | 18,606 | 18,606 | 2.25202708 | Yes |
| 2 | Rockingham | Derry | 18,053 | 36,659 | 4.43712032 | Yes |
| 3 | Hillsborough | Merrimack | 17,642 | 54,301 | 6.57246707 | Yes |
| 4 | Rockingham | Londonderry | 16,274 | 70,575 | 8.54223428 | Yes |
| 5 | Hillsborough | Bedford | 14,682 | 85,257 | 10.31930950 | Yes |
| 6 | Hillsborough | Hudson | 14,667 | 99,924 | 12.09456916 | Yes |
| 7 | Hillsborough | Goffstown | 10,539 | 110,463 | 13.37018527 | Yes |
| 8 | Rockingham | Hampton | 10,447 | 120,910 | 14.63466592 | Yes |
| 9 | Rockingham | Exeter | 10,357 | 131,267 | 15.88825317 | Yes |
| 10 | Rockingham | Windham | 10,086 | 141,353 | 17.10903921 | Yes |
| 11 | Hillsborough | Milford | 9,477 | 150,830 | 18.25611331 | Yes |
| 12 | Hillsborough | Pelham | 9,223 | 160,053 | 19.37244384 | Yes |
| 13 | Merrimack | Hooksett | 8,987 | 169,040 | 20.46020947 | Yes |
| 14 | Strafford | Durham | 8,452 | 177,492 | 21.48321994 | Yes |
| 15 | Hillsborough | Amherst | 8,167 | 185,659 | 22.47173468 | Yes |
| 16 | Grafton | Hanover | 7,179 | 192,838 | 23.34066418 | Yes |
| 17 | Hillsborough | Nashua Ward 5 | 6,546 | 199,384 | 24.13297684 | Yes |
| 18 | Rockingham | Raymond | 6,348 | 205,732 | 24.90132403 | Yes |
| 19 | Strafford | Barrington | 6,320 | 212,052 | 25.66628217 | Yes |
| 20 | Hillsborough | Nashua Ward 1 | 6,180 | 218,232 | 26.41429503 | Yes |
| 21 | Rockingham | Hampstead | 6,072 | 224,304 | 27.14923583 | Yes |
| 22 | Rockingham | Newmarket | 6,015 | 230,319 | 27.87727748 | Yes |
| 23 | Carroll | Conway | 5,972 | 236,291 | 28.60011450 | Yes |
| 24 | Hillsborough | Hollis | 5,867 | 242,158 | 29.31024257 | Yes |
| 25 | Hillsborough | Nashua Ward 2 | 5,732 | 247,890 | 30.00403055 | Yes |
| 26 | Hillsborough | Weare | 5,731 | 253,621 | 30.69769750 | Yes |
| 27 | Hillsborough | Nashua Ward 9 | 5,730 | 259,351 | 31.39124341 | Yes |
| 28 | Hillsborough | Manchester Ward 1 | 5,689 | 265,040 | 32.07982677 | Yes |
| 29 | Rockingham | Stratham | 5,565 | 270,605 | 32.75340146 | Yes |
| 30 | Hillsborough | Litchfield | 5,519 | 276,124 | 33.42140842 | Yes |
| 31 | Hillsborough | Manchester Ward 8 | 5,477 | 281,601 | 34.08433179 | Yes |
| 32 | Merrimack | Bow | 5,429 | 287,030 | 34.74144536 | Yes |
| 33 | Hillsborough | Manchester Ward 6 | 5,312 | 292,342 | 35.38439752 | Yes |
| 34 | Belknap | Gilford | 5,287 | 297,629 | 36.02432373 | Yes |
| 35 | Hillsborough | Manchester Ward 2 | 5,243 | 302,872 | 36.65892429 | Yes |
| 36 | Rockingham | Seabrook | 5,207 | 308,079 | 37.28916749 | Yes |
| 37 | Rockingham | Atkinson | 5,159 | 313,238 | 37.91360088 | Yes |
| 38 | Rockingham | Epping | 4,925 | 318,163 | 38.50971146 | Yes |
| 39 | Hillsborough | Nashua Ward 8 | 4,859 | 323,022 | 39.09783355 | Yes |
| 40 | Carroll | Wolfeboro | 4,828 | 327,850 | 39.68220347 | Yes |
| 41 | Rockingham | Plaistow | 4,739 | 332,589 | 40.25580103 | Yes |
| 42 | Hillsborough | Nashua Ward 3 | 4,656 | 337,245 | 40.81935247 | Yes |
| 43 | Belknap | Meredith | 4,647 | 341,892 | 41.38181457 | Yes |
| 44 | Hillsborough | Manchester Ward 12 | 4,590 | 346,482 | 41.93737752 | Yes |
| 45 | Merrimack | Pembroke | 4,519 | 351,001 | 42.48434680 | Yes |
| 46 | Hillsborough | Peterborough | 4,458 | 355,459 | 43.02393278 | Yes |
| 47 | Rockingham | Rye | 4,418 | 359,877 | 43.55867725 | Yes |
| 48 | Hillsborough | Nashua Ward 6 | 4,417 | 364,294 | 44.09330069 | Yes |
| 49 | Belknap | Belmont | 4,324 | 368,618 | 44.61666761 | Yes |
| 50 | Hillsborough | Manchester Ward 10 | 4,276 | 372,894 | 45.13422474 | Yes |
| 51 | Hillsborough | Nashua Ward 7 | 4,240 | 377,134 | 45.64742450 | Yes |
| 52 | Cheshire | Swanzey | 4,228 | 381,362 | 46.15917181 | Yes |
| 53 | Rockingham | Sandown | 4,228 | 385,590 | 46.67091912 | Yes |
| 54 | Belknap | Alton | 4,224 | 389,814 | 47.18218229 | Yes |
| 55 | Merrimack | Hopkinton | 4,205 | 394,019 | 47.69114573 | Yes |
| 56 | Hillsborough | Manchester Ward 9 | 4,165 | 398,184 | 48.19526767 | Yes |
| 57 | Rockingham | Kingston | 4,150 | 402,334 | 48.69757404 | Yes |
| 58 | Rockingham | Auburn | 4,057 | 406,391 | 49.18862391 | Yes |
| 59 | Coos | Berlin | 4,047 | 410,438 | 49.67846340 | Yes |
| 60 | Hillsborough | New Boston | 4,026 | 414,464 | 50.16576110 | Yes |
| 61 | Carroll | Moultonborough | 3,926 | 418,390 | 50.64095504 | Yes |
| 62 | Hillsborough | Manchester Ward 7 | 3,870 | 422,260 | 51.10937086 | Yes |
| 63 | Cheshire | Rindge | 3,772 | 426,032 | 51.56592499 | Yes |
| 64 | Strafford | Dover Ward 3 | 3,761 | 429,793 | 52.02114770 | Yes |
| 65 | Merrimack | Loudon | 3,728 | 433,521 | 52.47237618 | Yes |
| 66 | Hillsborough | Brookline | 3,692 | 437,213 | 52.91924729 | Yes |
| 67 | Rockingham | Nottingham | 3,675 | 440,888 | 53.36406077 | Yes |
| 68 | Hillsborough | Manchester Ward 11 | 3,670 | 444,558 | 53.80826905 | Yes |
| 69 | Hillsborough | Manchester Ward 4 | 3,668 | 448,226 | 54.25223526 | Yes |
| 70 | Strafford | Farmington | 3,668 | 451,894 | 54.69620147 | Yes |
| 71 | Strafford | Dover Ward 4 | 3,555 | 455,449 | 55.12649043 | Yes |
| 72 | Rockingham | Chester | 3,541 | 458,990 | 55.55508485 | Yes |
| 73 | Carroll | Wakefield | 3,533 | 462,523 | 55.98271098 | Yes |
| 74 | Hillsborough | Manchester Ward 3 | 3,494 | 466,017 | 56.40561663 | Yes |
| 75 | Grafton | Plymouth | 3,483 | 469,500 | 56.82719087 | Yes |
| 76 | Hillsborough | Hillsborough | 3,442 | 472,942 | 57.24380257 | Yes |
| 77 | Rockingham | North Hampton | 3,436 | 476,378 | 57.65968804 | Yes |
| 78 | Rockingham | Deerfield | 3,388 | 479,766 | 58.06976370 | Yes |
| 79 | Sullivan | Newport | 3,325 | 483,091 | 58.47221398 | Yes |
| 80 | Grafton | Littleton | 3,319 | 486,410 | 58.87393805 | Yes |
| 81 | Hillsborough | New Ipswich | 3,304 | 489,714 | 59.27384654 | Yes |
| 82 | Rockingham | Portsmouth Ward 2 | 3,239 | 492,953 | 59.66588759 | Yes |
| 83 | Strafford | Dover Ward 1 | 3,236 | 496,189 | 60.05756552 | Yes |
| 84 | Cheshire | Jaffrey | 3,220 | 499,409 | 60.44730685 | Yes |
| 85 | Merrimack | New London | 3,174 | 502,583 | 60.83148045 | Yes |
| 86 | Belknap | Barnstead | 3,138 | 505,721 | 61.21129669 | Yes |
| 87 | Rockingham | Fremont | 3,136 | 508,857 | 61.59087085 | Yes |
| 88 | Rockingham | Brentwood | 3,118 | 511,975 | 61.96826634 | Yes |
| 89 | Merrimack | Concord Ward 10 | 3,108 | 515,083 | 62.34445145 | Yes |
| 90 | Strafford | Dover Ward 2 | 3,106 | 518,189 | 62.72039449 | Yes |
| 91 | Strafford | Dover Ward 6 | 3,091 | 521,280 | 63.09452196 | Yes |
| 92 | Rockingham | Newton | 3,050 | 524,330 | 63.46368688 | Yes |
| 93 | Merrimack | Epsom | 3,038 | 527,368 | 63.83139935 | Yes |
| 94 | Rockingham | Portsmouth Ward 3 | 3,033 | 530,401 | 64.19850664 | Yes |
| 95 | Hillsborough | Nashua Ward 4 | 3,032 | 533,433 | 64.56549288 | Yes |
| 96 | Strafford | Rochester Ward 5 | 3,030 | 536,463 | 64.93223705 | Yes |
| 97 | Strafford | Rochester Ward 2 | 3,021 | 539,484 | 65.29789189 | Yes |
| 98 | Strafford | Rochester Ward 1 | 3,009 | 542,493 | 65.66209427 | Yes |
| 99 | Strafford | Rochester Ward 3 | 3,001 | 545,494 | 66.02532834 | Yes |
| 100 | Strafford | Strafford | 2,992 | 548,486 | 66.38747308 | Yes |
| 101 | Rockingham | Greenland | 2,955 | 551,441 | 66.74513943 | Yes |
| 102 | Rockingham | Northwood | 2,955 | 554,396 | 67.10280577 | Yes |
| 103 | Rockingham | Candia | 2,953 | 557,349 | 67.46023004 | Yes |
| 104 | Merrimack | Concord Ward 7 | 2,941 | 560,290 | 67.81620186 | Yes |
| 105 | Rockingham | Portsmouth Ward 1 | 2,924 | 563,214 | 68.17011604 | Yes |
| 106 | Strafford | Lee | 2,922 | 566,136 | 68.52378814 | Yes |
| 107 | Merrimack | Henniker | 2,911 | 569,047 | 68.87612883 | Yes |
| 108 | Strafford | Dover Ward 5 | 2,911 | 571,958 | 69.22846951 | Yes |
| 109 | Cheshire | Keene Ward 5 | 2,880 | 574,838 | 69.57705803 | Yes |
| 110 | Merrimack | Concord Ward 5 | 2,875 | 577,713 | 69.92504136 | Yes |
| 111 | Rockingham | Portsmouth Ward 5 | 2,869 | 580,582 | 70.27229847 | Yes |
| 112 | Rockingham | Danville | 2,867 | 583,449 | 70.61931350 | Yes |
| 113 | Grafton | Lebanon Ward 2 | 2,859 | 586,308 | 70.96536023 | Yes |
| 114 | Hillsborough | Manchester Ward 5 | 2,804 | 589,112 | 71.30474988 | Yes |
| 115 | Strafford | Rochester Ward 4 | 2,800 | 591,912 | 71.64365539 | Yes |
| 116 | Merrimack | Northfield | 2,781 | 594,693 | 71.98026118 | Yes |
| 117 | Grafton | Lebanon Ward 3 | 2,779 | 597,472 | 72.31662489 | Yes |
| 118 | Grafton | Enfield | 2,741 | 600,213 | 72.64838917 | Yes |
| 119 | Strafford | Milton | 2,726 | 602,939 | 72.97833789 | Yes |
| 120 | Carroll | Ossipee | 2,696 | 605,635 | 73.30465547 | Yes |
| 121 | Belknap | Gilmanton | 2,661 | 608,296 | 73.62673674 | Yes |
| 122 | Rockingham | Portsmouth Ward 4 | 2,654 | 610,950 | 73.94797074 | Yes |
| 123 | Merrimack | Allenstown | 2,653 | 613,603 | 74.26908371 | Yes |
| 124 | Cheshire | Keene Ward 2 | 2,635 | 616,238 | 74.58801800 | Yes |
| 125 | Merrimack | Concord Ward 1 | 2,580 | 618,818 | 74.90029521 | Yes |
| 126 | Grafton | Lebanon Ward 1 | 2,569 | 621,387 | 75.21124101 | Yes |
| 127 | Hillsborough | Wilton | 2,553 | 623,940 | 75.52025021 | Yes |
| 128 | Cheshire | Keene Ward 4 | 2,549 | 626,489 | 75.82877526 | Yes |
| 129 | Sullivan | Charlestown | 2,530 | 629,019 | 76.13500059 | Yes |
| 130 | Strafford | Rochester Ward 6 | 2,517 | 631,536 | 76.43965243 | Yes |
| 131 | Sullivan | Sunapee | 2,514 | 634,050 | 76.74394116 | Yes |
| 132 | Cheshire | Keene Ward 3 | 2,496 | 636,546 | 77.04605121 | Yes |
| 133 | Sullivan | Grantham | 2,466 | 639,012 | 77.34453013 | Yes |
| 134 | Cheshire | Chesterfield | 2,458 | 641,470 | 77.64204074 | Yes |
| 135 | Grafton | Haverhill | 2,438 | 643,908 | 77.93713061 | Yes |
| 136 | Merrimack | Concord Ward 4 | 2,400 | 646,308 | 78.22762104 | Yes |
| 137 | Cheshire | Keene Ward 1 | 2,395 | 648,703 | 78.51750628 | Yes |
| 138 | Merrimack | Concord Ward 8 | 2,395 | 651,098 | 78.80739153 | Yes |
| 139 | Cheshire | Walpole | 2,369 | 653,467 | 79.09412979 | Yes |
| 140 | Merrimack | Pittsfield | 2,337 | 655,804 | 79.37699485 | Yes |
| 141 | Merrimack | Concord Ward 2 | 2,288 | 658,092 | 79.65392906 | Yes |
| 142 | Sullivan | Claremont Ward 2 | 2,286 | 660,378 | 79.93062120 | Yes |
| 143 | Belknap | Tilton | 2,246 | 662,624 | 80.20247183 | Yes |
| 144 | Grafton | Canaan | 2,191 | 664,815 | 80.46766539 | Remainder |
| 145 | Merrimack | Concord Ward 9 | 2,185 | 667,000 | 80.73213272 | Remainder |
| 146 | Merrimack | Boscawen | 2,173 | 669,173 | 80.99514760 | Remainder |
| 147 | Grafton | Campton | 2,169 | 671,342 | 81.25767833 | Remainder |
| 148 | Belknap | Sanbornton | 2,139 | 673,481 | 81.51657793 | Remainder |
| 149 | Merrimack | Concord Ward 6 | 2,119 | 675,600 | 81.77305677 | Remainder |
| 150 | Carroll | Bartlett | 2,113 | 677,713 | 82.02880939 | Remainder |
| 151 | Merrimack | Dunbarton | 2,109 | 679,822 | 82.28407786 | Remainder |
| 152 | Cheshire | Winchester | 2,077 | 681,899 | 82.53547312 | Remainder |
| 153 | Belknap | Laconia Ward 1 | 2,062 | 683,961 | 82.78505281 | Remainder |
| 154 | Grafton | Bristol | 2,045 | 686,006 | 83.03257487 | Remainder |
| 155 | Carroll | Tuftonboro | 1,995 | 688,001 | 83.27404504 | Remainder |
| 156 | Sullivan | Claremont Ward 3 | 1,961 | 689,962 | 83.51139993 | Remainder |
| 157 | Strafford | New Durham | 1,944 | 691,906 | 83.74669718 | Remainder |
| 158 | Belknap | Laconia Ward 6 | 1,921 | 693,827 | 83.97921057 | Remainder |
| 159 | Cheshire | Hinsdale | 1,914 | 695,741 | 84.21087669 | Remainder |
| 160 | Merrimack | Warner | 1,909 | 697,650 | 84.44193762 | Remainder |
| 161 | Hillsborough | Mont Vernon | 1,875 | 699,525 | 84.66888327 | Remainder |
| 162 | Carroll | Tamworth | 1,855 | 701,380 | 84.89340817 | Remainder |
| 163 | Merrimack | Chichester | 1,843 | 703,223 | 85.11648061 | Remainder |
| 164 | Grafton | Thornton | 1,836 | 705,059 | 85.33870579 | Remainder |
| 165 | Coos | Lancaster | 1,804 | 706,863 | 85.55705777 | Remainder |
| 166 | Carroll | Madison | 1,784 | 708,647 | 85.77298899 | Remainder |
| 167 | Merrimack | Canterbury | 1,755 | 710,402 | 85.98541012 | Remainder |
| 168 | Strafford | Rollinsford | 1,749 | 712,151 | 86.19710502 | Remainder |
| 169 | Rockingham | Hampton Falls | 1,741 | 713,892 | 86.40783162 | Remainder |
| 170 | Sullivan | Claremont Ward 1 | 1,735 | 715,627 | 86.61783200 | Remainder |
| 171 | Rockingham | East Kingston | 1,713 | 717,340 | 86.82516954 | Remainder |
| 172 | Merrimack | Newbury | 1,701 | 719,041 | 87.03105464 | Remainder |
| 173 | Sullivan | Plainfield | 1,700 | 720,741 | 87.23681869 | Remainder |
| 174 | Hillsborough | Antrim | 1,691 | 722,432 | 87.44149341 | Remainder |
| 175 | Grafton | Bethlehem | 1,677 | 724,109 | 87.64447360 | Remainder |
| 176 | Coos | Gorham | 1,670 | 725,779 | 87.84660653 | Remainder |
| 177 | Belknap | New Hampton | 1,668 | 727,447 | 88.04849738 | Remainder |
| 178 | Merrimack | Andover | 1,612 | 729,059 | 88.24361012 | Remainder |
| 179 | Rockingham | Kensington | 1,582 | 730,641 | 88.43509173 | Remainder |
| 180 | Merrimack | Franklin Ward 3 | 1,573 | 732,214 | 88.62548400 | Remainder |
| 181 | Belknap | Laconia Ward 3 | 1,532 | 733,746 | 88.81091373 | Remainder |
| 182 | Merrimack | Franklin Ward 1 | 1,504 | 735,250 | 88.99295440 | Remainder |
| 183 | Grafton | Holderness | 1,481 | 736,731 | 89.17221120 | Remainder |
| 184 | Coos | Whitefield | 1,466 | 738,197 | 89.34965244 | Remainder |
| 185 | Cheshire | Fitzwilliam | 1,465 | 739,662 | 89.52697264 | Remainder |
| 186 | Strafford | Somersworth Ward 1 | 1,463 | 741,125 | 89.70405077 | Remainder |
| 187 | Strafford | Somersworth Ward 4 | 1,450 | 742,575 | 89.87955540 | Remainder |
| 188 | Merrimack | Sutton | 1,432 | 744,007 | 90.05288136 | Remainder |
| 189 | Merrimack | Franklin Ward 2 | 1,424 | 745,431 | 90.22523902 | Remainder |
| 190 | Merrimack | Concord Ward 3 | 1,378 | 746,809 | 90.39202894 | Remainder |
| 191 | Belknap | Laconia Ward 4 | 1,366 | 748,175 | 90.55736641 | Remainder |
| 192 | Belknap | Laconia Ward 2 | 1,363 | 749,538 | 90.72234077 | Remainder |
| 193 | Hillsborough | Hancock | 1,315 | 750,853 | 90.88150532 | Remainder |
| 194 | Strafford | Madbury | 1,309 | 752,162 | 91.03994364 | Remainder |
| 195 | Merrimack | Webster | 1,296 | 753,458 | 91.19680848 | Remainder |
| 196 | Cheshire | Marlborough | 1,287 | 754,745 | 91.35258397 | Remainder |
| 197 | Belknap | Laconia Ward 5 | 1,284 | 756,029 | 91.50799635 | Remainder |
| 198 | Rockingham | Newfields | 1,272 | 757,301 | 91.66195628 | Remainder |
| 199 | Grafton | Ashland | 1,265 | 758,566 | 91.81506895 | Remainder |
| 200 | Grafton | Lyme | 1,243 | 759,809 | 91.96551879 | Remainder |
| 201 | Hillsborough | Francestown | 1,224 | 761,033 | 92.11366891 | Remainder |
| 202 | Cheshire | Alstead | 1,215 | 762,248 | 92.26072969 | Remainder |
| 203 | Strafford | Somersworth Ward 3 | 1,214 | 763,462 | 92.40766943 | Remainder |
| 204 | Carroll | Sandwich | 1,208 | 764,670 | 92.55388295 | Remainder |
| 205 | Carroll | Freedom | 1,195 | 765,865 | 92.69852298 | Remainder |
| 206 | Hillsborough | Lyndeborough | 1,186 | 767,051 | 92.84207367 | Remainder |
| 207 | Strafford | Somersworth Ward 2 | 1,173 | 768,224 | 92.98405086 | Remainder |
| 208 | Hillsborough | Deering | 1,153 | 769,377 | 93.12360731 | Remainder |
| 209 | Coos | Colebrook | 1,145 | 770,522 | 93.26219545 | Remainder |
| 210 | Strafford | Middleton | 1,142 | 771,664 | 93.40042048 | Remainder |
| 211 | Sullivan | Cornish | 1,142 | 772,806 | 93.53864552 | Remainder |
| 212 | Cheshire | Troy | 1,138 | 773,944 | 93.67638640 | Remainder |
| 213 | Coos | Northumberland | 1,138 | 775,082 | 93.81412728 | Remainder |
| 214 | Cheshire | Dublin | 1,128 | 776,210 | 93.95065778 | Remainder |
| 215 | Strafford | Somersworth Ward 5 | 1,126 | 777,336 | 94.08694621 | Remainder |
| 216 | Grafton | Alexandria | 1,123 | 778,459 | 94.22287152 | Remainder |
| 217 | Merrimack | Bradford | 1,111 | 779,570 | 94.35734438 | Remainder |
| 218 | Cheshire | Westmoreland | 1,110 | 780,680 | 94.49169621 | Remainder |
| 219 | Hillsborough | Greenfield | 1,090 | 781,770 | 94.62362728 | Remainder |
| 220 | Grafton | Rumney | 1,044 | 782,814 | 94.74999062 | Remainder |
| 221 | Hillsborough | Greenville | 1,031 | 783,845 | 94.87478047 | Remainder |
| 222 | Carroll | Effingham | 1,011 | 784,856 | 94.99714956 | Remainder |
| 223 | Merrimack | Wilmot | 1,006 | 785,862 | 95.11891347 | Remainder |
| 224 | Merrimack | Salisbury | 1,005 | 786,867 | 95.24055634 | Remainder |
| 225 | Hillsborough | Mason | 962 | 787,829 | 95.35699459 | Remainder |
| 226 | Hillsborough | Temple | 956 | 788,785 | 95.47270661 | Remainder |
| 227 | Grafton | Lincoln | 948 | 789,733 | 95.58745033 | Remainder |
| 228 | Cheshire | Stoddard | 947 | 790,680 | 95.70207301 | Remainder |
| 229 | Sullivan | Springfield † | 931 | 791,611 | 95.81475909 | Remainder |
| 230 | Sullivan | Unity | 910 | 792,521 | 95.92490338 | Remainder |
| 231 | Hillsborough | Bennington | 892 | 793,413 | 96.03286899 | Remainder |
| 232 | Sullivan | Washington | 886 | 794,299 | 96.14010838 | Remainder |
| 233 | Grafton | Bridgewater | 879 | 795,178 | 96.24650050 | Remainder |
| 234 | Grafton | Orford | 872 | 796,050 | 96.35204536 | Remainder |
| 235 | Grafton | Woodstock | 860 | 796,910 | 96.45613776 | Remainder |
| 236 | Rockingham | New Castle | 858 | 797,768 | 96.55998809 | Remainder |
| 237 | Grafton | Lisbon | 857 | 798,625 | 96.66371738 | Remainder |
| 238 | Merrimack | Danbury | 829 | 799,454 | 96.76405762 | Remainder |
| 239 | Grafton | Franconia | 828 | 800,282 | 96.86427682 | Remainder |
| 240 | Coos | Milan † | 819 | 801,101 | 96.96340668 | Remainder |
| 241 | Belknap | Center Harbor | 814 | 801,915 | 97.06193135 | Remainder |
| 242 | Grafton | Grafton | 790 | 802,705 | 97.15755112 | Remainder |
| 243 | Carroll | Jackson | 776 | 803,481 | 97.25147636 | Remainder |
| 244 | Cheshire | Harrisville | 772 | 804,253 | 97.34491745 | Remainder |
| 245 | Sullivan | Lempster | 763 | 805,016 | 97.43726920 | Remainder |
| 246 | Cheshire | Richmond | 754 | 805,770 | 97.52853161 | Remainder |
| 247 | Grafton | Bath | 698 | 806,468 | 97.61301591 | Remainder |
| 248 | Coos | Jefferson | 685 | 807,153 | 97.69592672 | Remainder |
| 249 | Merrimack | Hill | 665 | 807,818 | 97.77641678 | Remainder |
| 250 | Grafton | Wentworth | 633 | 808,451 | 97.85303363 | Remainder |
| 251 | Rockingham | South Hampton | 633 | 809,084 | 97.92965048 | Remainder |
| 252 | Rockingham | Newington | 624 | 809,708 | 98.00517799 | Remainder |
| 253 | Coos | Dalton | 616 | 810,324 | 98.07973720 | Remainder |
| 254 | Coos | Pittsburg | 601 | 810,925 | 98.15248085 | Remainder |
| 255 | Sullivan | Acworth | 592 | 811,517 | 98.22413516 | Remainder |
| 256 | Carroll | Brookfield | 580 | 812,097 | 98.29433701 | Remainder |
| 257 | Sullivan | Croydon | 577 | 812,674 | 98.36417575 | Remainder |
| 258 | Cheshire | Surry | 575 | 813,249 | 98.43377242 | Remainder |
| 259 | Grafton | Hebron | 559 | 813,808 | 98.50143248 | Remainder |
| 260 | Coos | Carroll | 549 | 814,357 | 98.56788217 | Remainder |
| 261 | Grafton | Monroe | 546 | 814,903 | 98.63396874 | Remainder |
| 262 | Cheshire | Gilsum | 517 | 815,420 | 98.69654522 | Remainder |
| 263 | Grafton | Warren | 514 | 815,934 | 98.75875859 | Remainder |
| 264 | Grafton | Sugar Hill | 498 | 816,432 | 98.81903535 | Remainder |
| 265 | Sullivan | Goshen | 477 | 816,909 | 98.87677033 | Remainder |
| 266 | Grafton | Piermont | 472 | 817,381 | 98.93390011 | Remainder |
| 267 | Cheshire | Marlow | 458 | 817,839 | 98.98933537 | Remainder |
| 268 | Carroll | Albany | 452 | 818,291 | 99.04404440 | Remainder |
| 269 | Cheshire | Nelson | 447 | 818,738 | 99.09814824 | Remainder |
| 270 | Coos | Stewartstown | 439 | 819,177 | 99.15128379 | Remainder |
| 271 | Cheshire | Sullivan | 433 | 819,610 | 99.20369310 | Remainder |
| 272 | Grafton | Waterville Valley † | 428 | 820,038 | 99.25549723 | Remainder |
| 273 | Sullivan | Langdon | 426 | 820,464 | 99.30705928 | Remainder |
| 274 | Coos | Columbia | 417 | 820,881 | 99.35753199 | Remainder |
| 275 | Grafton | Groton | 389 | 821,270 | 99.40461565 | Remainder |
| 276 | Grafton | Lyman | 387 | 821,657 | 99.45145723 | Remainder |
| 277 | Coos | Stratford | 352 | 822,009 | 99.49406250 | Remainder |
| 278 | Coos | Stark | 328 | 822,337 | 99.53376286 | Remainder |
| 279 | Carroll | Eaton | 322 | 822,659 | 99.57273699 | Remainder |
| 280 | Grafton | Landaff | 298 | 822,957 | 99.60880622 | Remainder |
| 281 | Hillsborough | Sharon | 294 | 823,251 | 99.64439130 | Remainder |
| 282 | Coos | Shelburne | 289 | 823,540 | 99.67937119 | Remainder |
| 283 | Coos | Randolph | 280 | 823,820 | 99.71326174 | Remainder |
| 284 | Grafton | Dorchester | 245 | 824,065 | 99.74291597 | Remainder |
| 285 | Grafton | Easton | 242 | 824,307 | 99.77220709 | Remainder |
| 286 | Carroll | Chatham | 234 | 824,541 | 99.80052990 | Remainder |
| 287 | Grafton | Benton | 234 | 824,775 | 99.82885272 | Remainder |
| 288 | Coos | Errol | 233 | 825,008 | 99.85705450 | Remainder |
| 289 | Grafton | Orange | 203 | 825,211 | 99.88162515 | Remainder |
| 290 | Coos | Clarksville | 195 | 825,406 | 99.90522750 | Remainder |
| 291 | Coos | Dummer | 187 | 825,593 | 99.92786154 | Remainder |
| 292 | Cheshire | Roxbury | 150 | 825,743 | 99.94601719 | Remainder |
| 293 | Carroll | Hale's Location | 132 | 825,875 | 99.96199417 | Remainder |
| 294 | Hillsborough | Windsor | 132 | 826,007 | 99.97797114 | Remainder |
| 295 | Grafton | Ellsworth | 74 | 826,081 | 99.98692793 | Remainder |
| 296 | Carroll | Hart's Location | 46 | 826,127 | 99.99249566 | Remainder |
| 297 | Coos | Wentworth's Loc. | 23 | 826,150 | 99.99527953 | Remainder |
| 298 | Coos | Millsfield † | 13 | 826,163 | 99.99685302 | Remainder |
| 299 | Coos | Pinkham's Grant | 10 | 826,173 | 99.99806340 | Remainder |
| 300 | Coos | Dixville | 6 | 826,179 | 99.99878962 | Remainder |
| 301 | Coos | Cambridge | 5 | 826,184 | 99.99939481 | Remainder |
| 302 | Coos | Martin's Location | 2 | 826,186 | 99.99963689 | Remainder |
| 303 | Coos | Success | 2 | 826,188 | 99.99987896 | Remainder |
| 304 | Coos | Green's Grant | 1 | 826,189 | 100.00000000 | Remainder |
| 305 | Coos | Atk. & Gilm. Ac. Gt. † | 0 | 826,189 | 100.00000000 | Remainder |
| 306 | Coos | Bean's Grant † | 0 | 826,189 | 100.00000000 | Remainder |
| 307 | Coos | Bean's Purchase † | 0 | 826,189 | 100.00000000 | Remainder |
| 308 | Coos | Chandler's Purchase † | 0 | 826,189 | 100.00000000 | Remainder |
| 309 | Coos | Crawford's Purchase † | 0 | 826,189 | 100.00000000 | Remainder |
| 310 | Coos | Cutt's Grant † | 0 | 826,189 | 100.00000000 | Remainder |
| 311 | Coos | Dix's Grant † | 0 | 826,189 | 100.00000000 | Remainder |
| 312 | Coos | Erving's Location † | 0 | 826,189 | 100.00000000 | Remainder |
| 313 | Coos | Hadley's Purchase † | 0 | 826,189 | 100.00000000 | Remainder |
| 314 | Coos | Kilkenny † | 0 | 826,189 | 100.00000000 | Remainder |
| 315 | Coos | Low & Burbank's Gt. † | 0 | 826,189 | 100.00000000 | Remainder |
| 316 | Coos | Odell † | 0 | 826,189 | 100.00000000 | Remainder |
| 317 | Coos | Sargent's Purchase † | 0 | 826,189 | 100.00000000 | Remainder |
| 318 | Coos | Second College Gt. † | 0 | 826,189 | 100.00000000 | Remainder |
| 319 | Coos | Thompson & Mes's Pur. † | 0 | 826,189 | 100.00000000 | Remainder |
| 320 | Grafton | Livermore † | 0 | 826,189 | 100.00000000 | Remainder |
