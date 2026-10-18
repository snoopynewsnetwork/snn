# Maine’s native reporting-unit vote volume

Research date: **2026-10-17 America/Chicago**. Retained HTTP captures span **2026-10-18T02:11:31.317326+00:00 to 2026-10-18T02:22:03.321120+00:00 UTC**. The primary baseline is the current Maine SOS **corrected FINAL 2024 U.S. Senate municipal tabulation**, all four published candidates, **821,072 votes**. This is the King seat elected in 2024, a different seat from Collins’s Class II election on November 3, 2026. King and Cherry are **Independent**, Costello Democratic, and Kouzounas Republican. This is historical coverage research, not a forecast.

**Top 15:** Portland, Lewiston, Bangor, South Portland, Scarborough, Brunswick, Saco, Auburn, Windham, Biddeford, Gorham, Sanford, Westbrook, Augusta, York. They supply **215,627 / 821,072 = 26.26164332%**.

**The smallest ranked set reaching 80% contains 164 native units**, including **STATE UOCAVA** at rank 22. Their total is **658,029 / 821,072 = 80.14266715%**. The largest 163 total **656,778 = 79.99030536%**; **Pownal’s 1,251** crosses the threshold. Therefore no set of 163 can reach 80%. There can be other sets of 164; the exact deterministic prefix below is the accepted research set. The top 15 are contained in it. The other **348 units and 163,043 votes** remain in all statewide arithmetic.

The [all-unit CSV](data/county-turnout.csv), [priority JSON](data/turnout/priority-set.json), and [ordered exact keys](data/turnout/priority-keys.txt) are the dispatch contract. Ordered key bytes use UTF-8, one key per LF-terminated line, including the final LF. SHA-256: **`086b400b77792d763e93a5083c9ec8c92c71e44016743fc4e7f54bb2008db407`**. Both the actual partisanship worker’s separate parser/download and the coordinator’s independent reconciliation accepted all 512 raw names, county codes, source rows, candidate/blank/ballot counts and the ordered 164 keys. The worker’s retained [reconciliation](data/turnout/independent-reconciliation.json) records its source and hash.

## Native geography and stable keys

The compatibility filename `county-turnout.csv` contains **512 native reporting-unit rows**, not 16 county election authorities: 511 county-labeled towns, cities, plantations, townships, combined municipal/township labels and voting districts, plus a separately administered statewide UOCAVA row. Counties are contextual fields. The SOS [2024 results page](https://www3.maine.gov/sos/node/2479) links the municipal workbook; its 16 county footers and statewide footer are overlapping controls and are **never added to unit rows**. All 512 rows sum exactly to every candidate, BLANK and TBC statewide control.

Keys have the form `ME:SOS:2024-11-05:CUM:Portland`. They combine state, source family, election date, source-native three-letter county code, and percent-encoded **trimmed exact source MUNICIPALITY**. For the unallocated administrative row the county component is `STATE`: `ME:SOS:2024-11-05:STATE:STATE%20UOCAVA`. No native numeric municipality ID is published in these workbooks; its field is empty. The exact raw name remains in `unit_name`, including trailing spaces in `Winterport ` and `Madawaska Lake `. Trimming affects only the composite key and deterministic tie ordering. The 2024 keys are unique; names alone are not a general join contract. County FIPS come from the retained [Census county-code file](https://www2.census.gov/geo/docs/reference/codes/files/st23_me_cou.txt). UOCAVA has no assigned county/FIPS or invented polygon.

Slash labels are retained whole. For example, Ellsworth/Fletchers Landing Twp and Old Town/Argyle Twp are native combined returns, not separately allocated township estimates. A printed reporting-county code is not proof that every component of a combined return lies in that county. Individual unorganized units remain separate wherever the source publishes them.

The selected result workbooks have **no ward/precinct vote-return IDs**. The JSON therefore says so and supplies empty results-precinct arrays. It also retains matching **historical CVR registration ward/precinct and district-intersection tuples**, with source line numbers, for later investigation. A registration key includes county, municipality, W/P, CG, SS, SR and CC; W/P alone collides. Those are registration categories, not proven current reporting precincts. Of 164 priority units, 155 have conservative county/name registration links; the remaining nine are explicit unmatched entries: STATE UOCAVA and eight combined return labels. All original registration rows remain available. No year-to-year boundary equivalence, November 2026 approval, or current polygon correspondence has been established.

## Counts, certification status and ranked-choice stage

Current sources are the SOS-linked [corrected Senate workbook](https://www3.maine.gov/sos/sites/maine.gov.sos/files/inline-files/US%20Senator%20FINAL-Corrected%2020241205.xlsx), [corrected presidential workbook](https://www3.maine.gov/sos/sites/maine.gov.sos/files/inline-files/President%20and%20Vice%20President%20FINAL-Corrected%2020241205.xlsx), and [2022 governor workbook](https://www3.maine.gov/sos/sites/maine.gov.sos/files/inline-files/Governor.xlsx). Every row/candidate sum is reconciled to the same publication’s primary statewide control, with every county-section footer checked separately. The exact source rows, cells and controls are retained.

| Election / published candidate or category | Statewide count |
| --- | ---: |
| 2024 Senate — Cherry, Jason S. (Independent) | 20,193 |
| 2024 Senate — Costello, David Allen (Democratic) | 88,875 |
| 2024 Senate — King, Angus S. Jr. (Independent) | 427,570 |
| 2024 Senate — Kouzounas, Demi (Republican) | 284,434 |
| **2024 Senate all candidates** | **821,072** |
| 2024 Senate BLANK / TBC | 21,375 / 842,447 |
| 2024 president — Harris/Walz | 435,652 |
| 2024 president — Oliver/ter Maat | 5,286 |
| 2024 president — Stein/Ware | 8,967 |
| 2024 president — Trump/Vance | 377,977 |
| 2024 president — West/Abdullah | 2,912 |
| 2024 president — Others | 581 |
| **2024 president all published candidates/others** | **831,375** |
| 2024 president BLANK / TBC | 11,072 / 842,447 |
| 2022 governor — Hunkler, Sam (Independent-Unenrolled) | 12,581 |
| 2022 governor — LePage, Paul R. (Republican) | 287,304 |
| 2022 governor — Mills, Janet T. (Democratic) | 376,934 |
| **2022 governor all candidates** | **676,819** |
| 2022 governor BLANK / TBC | 4,090 / 680,909 |

The Senate universe is all four published candidates, not D+R. Its workbook has no additional write-in column. The [official 2024 declared-write-in notice](https://www.barharbormaine.gov/DocumentCenter/View/7855/November-2024-Declared-Write-in-Candidates-with-explanation?bidId=), inspected through the research browser, lists presidential and CD2 candidates and no Senate candidate; it states that undeclared write-ins are not valid. The original notice bytes were blocked on the direct download route, a retained supplementary-source gap. The presidential **581 Others** category is included in full; the corrected workbook does not split it into named write-ins. Do not manufacture that split or silently discard it. The official 2022 declared-write-in list, retained from the legislative library, has no governor write-in.

The [SOS’s September 24, 2024 process explanation](https://mobile.maine.gov/sos/news/general-election-day-2024-6-weeks-away) says municipal election-night reporting supplies first choices and a central RCV tabulation follows when needed. The final results page places president and Senate under its “Non-Ranked Choice Offices” tabulations and publishes a separate central RCV series for **CD2 only**. This ranking uses the published **initial municipal candidate tally**, with no elimination-round transfers added. It is not a sum of RCV rounds, active votes, exhausted ballots or final two-candidate counts. The files do not expose ballot-level literal markings or separate overvotes, inactive/exhausted counts, or detailed invalid-vote categories. Preserve the published **BLANK** label; do not infer that every such record was an intentional undervote. No first-choice plurality is represented here as an RCV winner.

The [Secretary’s December 18, 2024 final-results transmittal](https://legislature.maine.gov/uploads/visual_edit/s-20250108.pdf), printed January 8, 2025 at page 28, identifies the SOS municipal/county tabulations as final official results. The Senate and presidential filenames explicitly identify corrected FINAL versions. Their internal modified timestamps are December 9 and December 6, 2024 respectively; these are file metadata, **not certification dates**. The signed [December 9 presidential certificate](https://www.archives.gov/files/electoral-college/2024/ascertainment-maine.pdf) independently matches all five named presidential candidate totals; it does not publish the Others/BLANK categories. The [January 4, 2023 legislative record](https://legislature.maine.gov/uploads/visual_edit/02-01-04-2023r2-3.pdf) contains the Secretary’s certified governor candidate totals, all matching. The [official library’s historical governor PDF](https://lldc.mainelegislature.org/Open/Elections/Returns/2022/20221108/elec_20221108ad.pdf) independently matches **all 510 raw municipal/administrative rows and all five count columns**, including both Cranberry Isles rows. Library copies are archival publications retrieved now; no archive capture/accession date is supplied, and none is invented.

## Source-vintage discrepancy localized to Alfred

The [House Clerk’s 2024 statistics](https://clerk.house.gov/member_info/electionInfo/2024/statistics2024.pdf), page 29, differ from current corrected SOS counts. The official legislative library’s archived [Senate workbook](https://lldc.mainelegislature.org/Open/Elections/Returns/2024/20241105/elec_20241105b.xlsx) and [presidential workbook](https://lldc.mainelegislature.org/Open/Elections/Returns/2024/20241105/elec_20241105a.xlsx) reproduce the Clerk’s statewide values. Comparing **every cell** against the current SOS versions localizes all changed counts to **Alfred, York County**, and its York/state footers. All other unit cells are identical. Both versions retain Alfred TBC **2,076**.

| Alfred published category | Official archive / Clerk-compatible vintage | Current corrected SOS | Current minus archive |
| --- | ---: | ---: | ---: |
| Senate Cherry | 69 | 40 | -29 |
| Senate Costello | 219 | 203 | -16 |
| Senate King | 746 | 985 | +239 |
| Senate Kouzounas | 714 | 810 | +96 |
| Senate BLANK | 328 | 38 | -290 |
| President Harris | 680 | 981 | +301 |
| President Oliver | 31 | 13 | -18 |
| President Stein | 23 | 17 | -6 |
| President Trump | 891 | 1,031 | +140 |
| President West | 39 | 8 | -31 |
| President Others | 0 | 0 | 0 |
| President BLANK | 412 | 26 | -386 |

The Senate archive/Clerk statewide candidate values are Cherry 20,222; Costello 88,891; King 427,331; Kouzounas 284,338; BLANK 21,665. Its candidate denominator is **820,782**, while both publications’ TBC is 842,447. Presidential archive/Clerk values are Harris 435,351; Oliver 5,304; Stein 8,973; Trump 377,837; West 2,943; Others 581; BLANK 11,458, with candidate denominator **830,989**. These exact differences are accounted for by Alfred. **The correction mechanism and precise publication/certification chronology remain unestablished.** A filename, internal modified date or library directory timestamp cannot resolve them. The current SOS-linked corrected files govern this ranking; no votes are rescaled to force Clerk agreement. [Reproducible all-cell diff](data/turnout/source-vintage-diff.json) retains both vintages and original bytes.

## Independent ballot, presidential and midterm comparisons

The primary 2024 Senate candidate denominator differs from statewide ballots by **21,375**; presidential candidates/others differ from the same ballots by **11,072**. These are the published BLANK columns. STATE UOCAVA contributes **6,434 Senate candidate votes and 6,589 ballots**, retained exactly once. The sources combine voting methods within other rows; they do not support a statewide method-by-municipality turnout ranking. Absentee requests or returns must not be substituted for ballots actually cast.

| Independently ranked view | Units | State denominator | Top-15 volume / share | Smallest 80% set / volume |
| --- | ---: | ---: | --- | --- |
| 2024 Senate candidates | 512 | 821,072 | 215,627 / 26.26164332% | 164 / 658,029 |
| 2024 president candidates + Others | 513 | 831,375 | 218,173 / 26.24242971% | 164 / 665,920 |
| 2024 TBC ballots | 512 Senate view; 513 presidential view | 842,447 | 221,060 / 26.24022639% | 164 / 674,796 |
| 2022 governor candidates | 509 research labels; 510 source rows | 676,819 | 176,643 / 26.09900136% | 166 / 542,410 |
| 2022 governor TBC ballots | 509 research labels | 680,909 | 177,924 / 26.13036397% | 166 / 545,702 |

Separate [presidential rankings](data/turnout/president-2024-ranked.csv), [midterm rankings](data/turnout/governor-2022-ranked.csv), and [Senate/ballot rankings](data/turnout/senate-2024-ranked.csv) retain exact weights, cumulative volumes and flags for every unit. Presidential top-15 membership and order match Senate; the ballot top 15 put Gorham ahead of Biddeford. The 2024 ballot minimum-80 set replaces Pownal with Mexico; the presidential candidate minimum-80 set replaces Pownal with Milo/Orneville Twp after lexical aliases are allowed. These remain independent comparators, not substitutes for the Senate dispatch list.

Maine held **no 2022 Senate contest**. Governor is the actually held midterm comparator. Its top 15 are Portland, Lewiston, South Portland, Scarborough, Bangor, Brunswick, Saco, Auburn, Windham, Gorham, Biddeford, Westbrook, Sanford, York, Augusta. Comparing it to 2024 Senate changes both contest and election, so differences cannot be interpreted as pure participation or constant candidate effects. No fictional 2022 Senate baseline is created; 2020 same-seat context is handled separately by the partisanship worker.

The [label crosswalk](data/turnout/comparator-label-crosswalk.csv) links 509/512 Senate labels to presidential labels and 481/512 to governor labels using only county plus case, whitespace and explicit suffix/spelling normalization. **These are name links, not boundary crosswalks.** The unmatched 2024 cases are Caribou/Connor, Medway/Molunkus Twp and Wesley/Day Block Twp. The presidential file names Caribou/Connor Twp and Medway/Twps, and splits Wesley and Day Block into two rows; no guessed equivalence is inserted. All 513 presidential and 510 raw governor rows remain in their own statewide arithmetic.

**2022 defects:** Cranberry Isles has two positive, identically named rows (165 and 166), without ward IDs. Both are retained with distinct source-row keys and sum to one **115-vote / 117-ballot** municipal research label; neither is silently deduplicated. Governor row 190 has native code **PEN** for **T3 ND Twp** inside the Hancock section: Hunkler 0, LePage 3, Mills 1, BLANK 0, TBC 4. The 16 disjoint section footers match certified county controls, while grouping exclusively by the printed row county code shifts those four votes from HAN to PEN. Both native and section codes are preserved in source rows and checks; no polygon or silent county correction is invented. The [county context table](data/turnout/county-context.csv) explicitly aggregates native printed county codes, and its 2022 HAN/PEN values carry this limitation. It is not a replacement for the municipal ranking.

## Registration and linked municipal evidence

The SOS [previous enrollment index](https://www3.maine.gov/sos/elections-voting/voter-data/previous-enrollment-data) supplies active and inactive snapshots. All four original text files and companion PDFs survive; district/party counts and every statewide party total reconcile independently between text and PDF.

| Election as-of date | Active | Inactive | Sum of statuses | Rows per status / municipal labels |
| --- | ---: | ---: | ---: | --- |
| 2024-11-05 (report generated 2024-12-27) | 1,037,570 | 185,622 | 1,223,192 | 741 / 504 |
| 2022-11-08 (report generated 2023-01-27) | 929,017 | 216,035 | 1,145,052 | 743 / 504 |

Registration is a dated stock and status, not ballots, valid contest votes, total population or voting-eligible population. The CSV leaves unmatched registration values blank, not zero; the complete [native registration table](data/turnout/registration-native-rows.csv) retains all district tuples, including unmatched units. Do not sum the partial municipal joins to claim a statewide registration total. The current 2022 HTML layout page mistakenly displays an “05-Mar-2024” as-of field; the linked 2022 PDF explicitly says **08-Nov-2022**, and its statewide totals exactly match the retained text. That inconsistency is preserved rather than importing the wrong date.

For a genuinely separate municipal check, the [Union 2024 election page](https://www.union.maine.gov/?SEC=8C952516-4C84-40F7-985F-36ABF16789C2) links its signed warden return, labeled preliminary on the landing page. All four Senate candidates, Senate BLANK and TBC match the corrected SOS Union row. Its five named presidential candidate counts and TBC also match, but its handwritten presidential BLANK is **19**, versus **27** in current SOS; the local lines sum eight short of TBC. The unfilled write-in lines are not converted into asserted zeros. The [Union 2022 page](https://www.union.maine.gov/index.asp?SEC=5FCB72BB-5FAF-4E73-96B7-48D7BB5F4A51) links a signed return whose three governor candidates, BLANK and TBC all match. Both PDFs and inspected PNG renderings survive. This is a bounded independent sample, not a claim to have checked every municipal certificate.

## Reproduction, validation and access status

Run from the checkout root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/maine/data/turnout/build_turnout.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/maine/data/turnout/compare_vintages.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/maine/data/turnout/write_report.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/maine/data/turnout/hash_assets.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/maine/data/turnout/validate_turnout.py
```

The extraction/rebuild uses Python’s standard library and cached OOXML cell values, without rewriting source spreadsheets. The raw sheets retain source Excel addresses in losslessly compressed JSON. The [schema and reproduction notes](data/turnout/SCHEMA.md), [calculation controls](data/turnout/checks.json), [offline validation result](data/turnout/validation.json), [source manifest](data/turnout/manifest.json), [all-asset hashes](data/turnout/asset-manifest.json) and [file provenance](data/turnout/provenance.json) document the contract. Fractions use integer numerators/denominators; decimal shares are display values. Ties use descending votes, ascending raw county code (empty for UOCAVA), then ascending trimmed source name. Crossing uses **`5*cumulative >= 4*statewide`**, with the preceding prefix required to fail.

`fetch_evidence.py --only <source-id> ...` explicitly refreshes bounded sources (30-second timeout, 38-MiB decoded limit per response). It preserves old versions when bytes change. `extract_pdf_evidence.py` regenerates PDF text and the two scanned Union previews using Poppler. No API pagination is involved: complete linked workbooks/text/PDF publications were downloaded, and every worksheet/nonempty row/maximum Excel row and parsed source identity is inventoried. The validator checks uniqueness, full coverage, candidate controls, every unit’s candidate+BLANK=TBC identity, independent ballot ordering, exact fractions, minimality, priority/remainder partition, source hashes, FIPS, district-key uniqueness, registration/PDF controls, all 510 independent 2022 PDF rows, the actual independent worker’s reconciliation, report links, asset size and absence of caches.

The ordinary `www.maine.gov` result/file routes returned retained **403** responses; the tested live official **www3** routes returned **200** with the linked files. This is a demonstrated historical download route on the retrieval date, not a November 2026 live feed or cadence claim. Supplementary Bangor/Bar Harbor/Kittery direct attempts and their failures remain in the manifest; successful Union alternatives were used for independent local evidence. Original bytes, UTC retrieval timestamps, full response headers, redirects and original/saved SHA-256 are retained. Each saved asset is below 40 MiB, using lossless gzip; no dependencies or caches are included.

Remaining substantive gaps are precise Alfred correction mechanism/timing, original bytes for the browser-readable 2024 write-in notice, named allocation of presidential Others, statewide vote-return ward/method detail, unresolved combined-unit/registration and cross-year geography, the two 2022 source labeling defects, and current November 2026 reporting-boundary approval. None is repaired by inventing a county allocation or treating matching names as matching boundaries.

## Top 15 native units

Comparator ranks below are independent contest-volume ranks, not turnout rates.

| Senate rank | Native unit | County code | Senate votes | State share | President rank | Governor 2022 rank |
| ---: | --- | --- | ---: | ---: | ---: | ---: |
| 1 | Portland | CUM | 38,862 | 4.7331% | 1 | 1 |
| 2 | Lewiston | AND | 16,332 | 1.9891% | 2 | 2 |
| 3 | Bangor | PEN | 15,714 | 1.9138% | 3 | 5 |
| 4 | South Portland | CUM | 15,596 | 1.8995% | 4 | 3 |
| 5 | Scarborough | CUM | 15,269 | 1.8596% | 5 | 4 |
| 6 | Brunswick | CUM | 14,337 | 1.7461% | 6 | 6 |
| 7 | Saco | YOR | 12,689 | 1.5454% | 7 | 7 |
| 8 | Auburn | AND | 12,256 | 1.4927% | 8 | 8 |
| 9 | Windham | CUM | 11,315 | 1.3781% | 9 | 9 |
| 10 | Biddeford | YOR | 11,291 | 1.3752% | 10 | 11 |
| 11 | Gorham | CUM | 11,284 | 1.3743% | 11 | 10 |
| 12 | Sanford | YOR | 10,886 | 1.3258% | 12 | 13 |
| 13 | Westbrook | CUM | 10,504 | 1.2793% | 13 | 12 |
| 14 | Augusta | KEN | 9,859 | 1.2007% | 14 | 15 |
| 15 | York | YOR | 9,433 | 1.1489% | 15 | 14 |

## Exact ordered minimum-80 priority set

The JSON/CSV preserve raw trailing whitespace and exact encoded keys; this display trims names. `STATE` is the unallocated administrative row, not a county. All nonpriority units remain in the CSV and JSON remainder.

| Rank | Native county code | Native unit | Senate votes |
| ---: | --- | --- | ---: |
| 1 | CUM | Portland | 38,862 |
| 2 | AND | Lewiston | 16,332 |
| 3 | PEN | Bangor | 15,714 |
| 4 | CUM | South Portland | 15,596 |
| 5 | CUM | Scarborough | 15,269 |
| 6 | CUM | Brunswick | 14,337 |
| 7 | YOR | Saco | 12,689 |
| 8 | AND | Auburn | 12,256 |
| 9 | CUM | Windham | 11,315 |
| 10 | YOR | Biddeford | 11,291 |
| 11 | CUM | Gorham | 11,284 |
| 12 | YOR | Sanford | 10,886 |
| 13 | CUM | Westbrook | 10,504 |
| 14 | KEN | Augusta | 9,859 |
| 15 | YOR | York | 9,433 |
| 16 | CUM | Falmouth | 8,910 |
| 17 | YOR | Wells | 8,342 |
| 18 | YOR | Kennebunk | 8,329 |
| 19 | KEN | Waterville | 7,322 |
| 20 | CUM | Cape Elizabeth | 6,821 |
| 21 | SAG | Topsham | 6,525 |
| 22 | STATE | STATE UOCAVA | 6,434 |
| 23 | YOR | Kittery | 6,425 |
| 24 | CUM | Standish | 6,244 |
| 25 | CUM | Yarmouth | 6,198 |
| 26 | CUM | Freeport | 6,192 |
| 27 | YOR | Old Orchard Beach | 6,186 |
| 28 | CUM | Cumberland | 6,041 |
| 29 | CUM | Gray | 5,519 |
| 30 | PEN | Orono | 5,270 |
| 31 | YOR | Buxton | 5,245 |
| 32 | PEN | Brewer | 5,235 |
| 33 | SAG | Bath | 5,161 |
| 34 | AND | Lisbon | 5,065 |
| 35 | PEN | Hampden | 5,030 |
| 36 | HAN | Ellsworth/Fletchers Landing Twp | 4,901 |
| 37 | YOR | Waterboro | 4,654 |
| 38 | YOR | South Berwick | 4,648 |
| 39 | KEN | Winslow | 4,629 |
| 40 | YOR | Eliot | 4,617 |
| 41 | YOR | Berwick | 4,549 |
| 42 | WAL | Belfast | 4,149 |
| 43 | ARO | Presque Isle | 4,108 |
| 44 | PEN | Hermon | 4,085 |
| 45 | PEN | Old Town/Argyle Twp | 4,079 |
| 46 | ARO | Caribou/Connor | 3,916 |
| 47 | FRA | Farmington | 3,908 |
| 48 | KEN | Winthrop | 3,868 |
| 49 | CUM | Harpswell | 3,848 |
| 50 | KNO | Rockland | 3,846 |
| 51 | CUM | New Gloucester | 3,749 |
| 52 | KEN | Oakland | 3,691 |
| 53 | SOM | Skowhegan | 3,649 |
| 54 | AND | Turner | 3,605 |
| 55 | KNO | Camden | 3,603 |
| 56 | HAN | Bar Harbor | 3,573 |
| 57 | AND | Poland | 3,538 |
| 58 | CUM | Bridgton | 3,520 |
| 59 | YOR | Lebanon | 3,502 |
| 60 | SOM | Fairfield | 3,378 |
| 61 | YOR | North Berwick | 3,233 |
| 62 | CUM | Raymond | 3,215 |
| 63 | KEN | Sidney | 3,106 |
| 64 | CUM | North Yarmouth | 3,065 |
| 65 | KEN | Gardiner | 3,057 |
| 66 | YOR | Hollis | 3,041 |
| 67 | YOR | Lyman | 3,040 |
| 68 | OXF | Norway | 3,012 |
| 69 | AND | Sabattus | 2,990 |
| 70 | AND | Durham | 2,958 |
| 71 | OXF | Paris | 2,902 |
| 72 | HAN | Bucksport | 2,899 |
| 73 | PEN | Glenburn | 2,855 |
| 74 | YOR | Arundel | 2,851 |
| 75 | YOR | Kennebunkport | 2,773 |
| 76 | PEN | Lincoln | 2,767 |
| 77 | OXF | Rumford | 2,706 |
| 78 | KEN | Vassalboro | 2,657 |
| 79 | AND | Greene | 2,655 |
| 80 | FRA | Jay | 2,653 |
| 81 | ARO | Houlton | 2,634 |
| 82 | PEN | Millinocket/Twps | 2,624 |
| 83 | PEN | Orrington | 2,614 |
| 84 | KEN | China | 2,591 |
| 85 | KEN | Monmouth | 2,586 |
| 86 | CUM | Naples | 2,528 |
| 87 | KNO | Rockport | 2,493 |
| 88 | KEN | West Gardiner | 2,451 |
| 89 | OXF | Oxford | 2,428 |
| 90 | YOR | Limington | 2,419 |
| 91 | SOM | Madison | 2,412 |
| 92 | PIS | Dover-Foxcroft | 2,398 |
| 93 | KNO | Warren | 2,384 |
| 94 | WAL | Winterport | 2,360 |
| 95 | LIN | Wiscasset | 2,340 |
| 96 | LIN | Waldoboro | 2,292 |
| 97 | KEN | Litchfield | 2,280 |
| 98 | CUM | Casco | 2,273 |
| 99 | SAG | Woolwich | 2,248 |
| 100 | KEN | Belgrade | 2,239 |
| 101 | LIN | Boothbay | 2,192 |
| 102 | SAG | Richmond | 2,156 |
| 103 | FRA | Wilton/Twps | 2,155 |
| 104 | LIN | Bristol/Louds Island Twp | 2,152 |
| 105 | ARO | Fort Kent | 2,144 |
| 106 | PEN | Holden | 2,123 |
| 107 | ARO | Madawaska | 2,077 |
| 108 | SAG | Bowdoinham | 2,071 |
| 109 | HAN | Blue Hill | 2,040 |
| 110 | YOR | Alfred | 2,038 |
| 111 | SOM | Pittsfield | 2,032 |
| 112 | YOR | Limerick | 2,008 |
| 113 | OXF | Fryeburg | 2,004 |
| 114 | PEN | Dexter | 1,967 |
| 115 | SOM | Norridgewock | 1,897 |
| 116 | SAG | Bowdoin | 1,877 |
| 117 | YOR | Shapleigh | 1,872 |
| 118 | PEN | Milford/Greenfield Twp | 1,858 |
| 119 | PEN | Newport | 1,836 |
| 120 | AND | Minot | 1,833 |
| 121 | KEN | Farmingdale | 1,824 |
| 122 | KEN | Pittston | 1,818 |
| 123 | KNO | Saint George | 1,816 |
| 124 | KEN | Readfield | 1,810 |
| 125 | OXF | Bethel/Mason Twp | 1,806 |
| 126 | KEN | Hallowell | 1,803 |
| 127 | PEN | Carmel | 1,796 |
| 128 | AND | Mechanic Falls | 1,780 |
| 129 | LIN | Jefferson | 1,754 |
| 130 | WAL | Lincolnville | 1,748 |
| 131 | PEN | Levant | 1,738 |
| 132 | KEN | Clinton | 1,736 |
| 133 | YOR | Acton | 1,724 |
| 134 | KEN | Manchester | 1,693 |
| 135 | WAL | Searsport | 1,684 |
| 136 | CUM | Harrison | 1,683 |
| 137 | KNO | Union | 1,658 |
| 138 | ARO | Fort Fairfield | 1,641 |
| 139 | SAG | Phippsburg | 1,628 |
| 140 | KNO | Thomaston | 1,584 |
| 141 | KEN | Chelsea | 1,571 |
| 142 | PEN | Corinth | 1,570 |
| 143 | KEN | Windsor | 1,560 |
| 144 | KEN | Benton | 1,542 |
| 145 | HAN | Orland | 1,537 |
| 146 | LIN | Damariscotta | 1,498 |
| 147 | HAN | Hancock | 1,483 |
| 148 | WAS | Calais | 1,482 |
| 149 | LIN | Whitefield | 1,473 |
| 150 | PEN | Eddington | 1,469 |
| 151 | YOR | Dayton | 1,458 |
| 152 | SAG | West Bath | 1,421 |
| 153 | AND | Leeds | 1,416 |
| 154 | AND | Livermore | 1,413 |
| 155 | AND | Livermore Falls | 1,405 |
| 156 | HAN | Mount Desert | 1,388 |
| 157 | LIN | Boothbay Harbor | 1,385 |
| 158 | LIN | Newcastle | 1,368 |
| 159 | LIN | Nobleboro | 1,343 |
| 160 | HAN | Deer Isle | 1,325 |
| 161 | OXF | Dixfield | 1,303 |
| 162 | CUM | Sebago | 1,276 |
| 163 | SOM | Anson | 1,273 |
| 164 | CUM | Pownal | 1,251 |
