# South Dakota historical partisanship and conditional paths to win

Observed **2026-10-19 UTC**. Complete historical coverage is **66 counties**, with **691 native presidential rows in2024, 687 native Senate rows in2022, and693 native Senate rows in2020**. These are source-specific reporting universes, not current precinct geometry. All units, including the entire nonpriority remainder, stay in state calculations. The current contest is **Brian L Bengs, Independent, versus Mike Rounds, Republican**; there is no current Democratic Senate choice in the inspected official publication ballot. Numerical historical Democratic outcomes below remain election-specific. Conditional named opposition scenarios do not relabel Bengs or treat every non-Republican as Democratic.

The [current Lincoln County publication ballot](https://www.lincolncountysd.gov/DocumentCenter/View/1989/Sample-Ballot-2026-PDF), linked by the [county elections page](https://www.lincolncountysd.gov/159/Elections), states November3,2026 and lists Rounds Republican Party/Bengs Independent. Primary web inspection succeeded; direct original downloads returned404/empty, including alternate same-resource routes. The [retained web observation](data/baselines/source/lincoln-ballot-web-observation.txt) is labeled parsed evidence, not original PDF bytes. The separately retained [current SOS candidate list](https://vip.sdsos.gov/candidatelist.aspx?eid=774) has Bengs IND and Rounds REP active and Julian Beaudion DEM withdrawn August4. That current list is corroboration, not a primary nominee or a final vendor-ID map. The [official2026 precinct manual](https://sdsos.gov/elections-voting/assets/2026%20Documents/2026PrecinctManual.pdf), PDFp15, says write-in votes are not counted. No eligible ordinary write-in choice is invented; invalid-mark counts remain unavailable.

Rounds is in [ClassII](https://www.senate.gov/senators/Class_II.htm), last regularly elected in2020; Thune is in [ClassIII](https://www.senate.gov/senators/Class_III.htm), elected in2022. Thus2020 Rounds–Ahlers is the **same seat**,2022 Thune–Bengs–Lesnar is the **other seat and actual midterm**, and2024 president is the recent statewide priority basis. There was no South Dakota Senate election in2024. General-election plurality under [SDCL12-20-39](https://sdlegislature.gov/Statutes/12-20-39) is distinct from party-primary/runoff electorates. These baselines have one general-election stage; no RCV or runoff preference transfers are inferred.

The signed statewide canvasses supply these full candidate fields; every66-county vector sums to its statewide candidate control. The printed2020 order is **Rounds then Ahlers**, visually checked in the [original page derivative](data/baselines/source/visual-senate-2020-column-order.png).

| Election / source | Complete named candidate votes and ballot identities | All-candidate denominator | A−B pair margin | A−B all-candidate margin |
| --- | --- | ---: | ---: | ---: |
| [2024 president](https://sdsos.gov/elections-voting/assets/Archive/2024%20Assets/Recount-Canvass-and-Canvass-Docs-General/2024GeneralElectionCanvassWithCert.pdf) | Kamala D. Harris and Tim Walz (DEM) 146,859; Chase Oliver and Mike ter Maat (LIB) 2,778; Donald J. Trump and JD Vance (REP) 272,081; Robert F. Kennedy, Jr. and Nicole Shanahan (IND) 7,204 | 428,922 | -29.8902 pp | -29.1946 pp |
| [2020 same-seat Senate](https://sdsos.gov/elections-voting/assets/Archive/2020%20Assests/2020GeneralStateCanvassFinal%26Certificate.pdf) | Mike Rounds (REP) 276,232; Dan Ahlers (DEM) 143,987 | 420,219 | -31.4705 pp | -31.4705 pp |
| [2022 other-seat Senate / midterm](https://sdsos.gov/elections-voting/assets/Archive/2022%20Assets/2022Generalcanvassreport.pdf) | Brian L. Bengs (DEM) 91,007; Tamara J Lesnar (LIB) 14,697; John R. Thune (REP) 242,316 | 348,020 | -45.3941 pp | -43.4771 pp |

A is Harris in2024, Ahlers in2020 and **Bengs Democratic on the2022 ballot**. Oliver Libertarian, Kennedy Independent and Lesnar Libertarian remain separate candidates. A−B describes the named pair only. Harris carried5 counties against Trump, Ahlers5 against Rounds and Bengs3 against Thune; those are historical outcomes, not permanent county identities. The [county/candidate table](data/baselines/county-candidates.csv) retains all594 named candidate counts, party labels, printed columns and source positions.

**Native evidence and source disagreements.** The actual official history/client/public export chains and complete originals are pinned in the [schema](data/baselines/source/SCHEMA.md) and [asset manifest](data/baselines/asset-manifest.json). The2024 chain is [official history](https://sdsos.gov/elections-voting/election-resources/election-history/2024_Election_History.aspx) → [actual election684](https://electionresults.sd.gov/default.aspx?eid=684) → [published Presidential Electors Precinct Level control](https://electionresults.sd.gov/resultsSW.aspx?type=SWR&map=CTY&eid=684). Original form fields, POST controls and responses remain. The workbook literally says2024 Unofficial General Election Results. All691 rows close their own66 county TOTALs: Harris146811, Oliver2777, Trump271938, Kennedy7202 =428728. Compared with signed totals, differences are **−48/−1/−143/−2=−194 in24 counties**; [every county/candidate difference](data/baselines/native-signed-differences.csv) remains unallocated. A691/691 reporting counter and freshly generated Downloaded at clock do not make those certified votes or establish live cadence.

Independently parsed [2022 public Senate export](https://electionresults.sd.gov/resultsSW.aspx?type=SWR&map=CTY&eid=471), discovered through its actual history link and public form, supplies687 native rows/66 parents and matches every signed county/candidate count. It remains source-labeled unofficial. The separately retained [2022 precinct canvass PDF](https://sdsos.gov/elections-voting/assets/Archive/2022%20Assets/2022PrecintCanvass.pdf) has679 rows/65 parents; its66 Senate pages include Minnehaha continuation but **omit Yankton**. Missing PDF native coverage is2462 Bengs/340 Lesnar/6051 Thune, not zero. Yankton’s8 public native rows fill public-source coverage without inventing missing PDF rows or an ID crosswalk. The [recount certificate](https://sdsos.gov/elections-voting/assets/Archive/2022%20Assets/2022GeneralStateCanvassRecountReport.pdf) is District15 House, not new Senate votes to add.

The [2020 public Senate export](https://electionresults.sd.gov/resultsSW.aspx?type=SWR&map=CTY&eid=422), independently parsed from its observed history/client/form chain, supplies693 native rows/66 parents: Rounds276208/Ahlers143970=420178. It trails signed controls by **24 Rounds and17 Ahlers votes,41 overall, across21 counties**. Exact county differences and full raw cells are retained. Neither this discrepancy nor2024’s is allocated to native rows. Native names/counts alone establish no cross-year physical equivalence.

All four2024 county-canvass PDF groups and the complete2020 county original are retained once, losslessly. Their source page hierarchy and full text remain; scanned OCR is not accepted as image truth. For example [Brookings group page40](data/baselines/source/visual-brookings-2024.png) visibly prints5978/112/8575/274, while OCR contains5974/712/8575/274; [Marshall group page2](data/baselines/source/visual-marshall-2024.png) prints Harris782 while OCR reads742. These images support signed values and do not explain the public workbook deficits. Comprehensive certified native transcription and discrepancy resolution are not claimed. The statewide all-race2024 XLSX separately mislabels D7 as Trump and E7 as Trump1, omitting Oliver; [literal headers/XML](data/baselines/source/candidate-header-presentation.json) are preserved. The admitted native and Aurora workbooks correctly name all four; no candidate is silently relabeled from numerical resemblance.

The Census [name/code change notice](https://www.census.gov/programs-surveys/geography/technical-documentation/county-changes.2010.html) identifies Oglala Lakota46102 as the former Shannon46113 effective May1,2015. The used2020/22/24 county sources name Oglala Lakota; it is not a67th county. All worksheet identities, literal administrative/combined/Absentee labels, original positions and missing method cases remain. A place name or VP label is not proof of a precinct, polling site, vote center, municipal parent or VTD geometry. The current setup’s673 overall versus656 Senate units is neither a precinct crosswalk nor actual counted votes.

**Turnout and registration controls.** The books’ Votes Cast and active registration denominators are separate from named contest votes. Source dates and every county raw line remain in [turnout-registration-controls.csv](data/baselines/turnout-registration-controls.csv). Native ballots/registration/blank/under/over fields are unavailable, not zero. The difference between Votes Cast and contest votes is unclassified.

| Official returns book / turnout PDF page | Votes Cast | Named contest votes | Unclassified difference | Turnout-table registered | Separate active / inactive registration |
| --- | ---: | ---: | ---: | ---: | ---: |
| [2024 book, p23](https://sdsos.gov/elections-voting/assets/Archive/2024%20Assets/Post-Election-Audit-General/ElectionReturns2024.pdf) | 436,478 | 428,922 | 7,556 | 624,175 | 624,175 / 63,901 |
| [2022 book, p25](https://sdsos.gov/elections-voting/assets/Archive/Prior%20to%202026/Election%20Returns%202022.pdf) | 354,670 | 348,020 | 6,650 | 597,073 | 597,069 / 61,369 |
| [2020 book, p15](https://sdsos.gov/elections-voting/assets/Archive/Prior%20to%202026/ElectionReturns2020web.pdf) | 427,529 | 420,219 | 7,310 | 578,655 | 578,666 / 56,646 |

Registration tables are dated November5,2024 / November8,2022 / November3,2020. Turnout-table registered minus registration-table active is0 / +4 / −11 respectively; county differences remain. These are **historical turnout anchors**, not2026 projections. A separately published2024 terminology page’s registration figure625192 differs from the book624175; it is another source, not a value to normalize into this book. Party registration is not a candidate preference estimate.

**Exact source-native concentration.** Independent descending sort uses all four candidate tickets, then ascending county FIPS, numeric worksheet ordinal and source row. [Full native2024 inventory](data/baselines/native-2024.csv) and [complete priority contract](data/baselines/priority-contract.json) retain every691 row, all66 parents and every remaining unit. Top15 provide61003/428728=14.2288%. The smallest source-native prefix reaching80% is304 units:343402/428728=80.0979%;303 provide342947, below the integer target342983. Crossing unit is Hamlin **Precinct-26**, `sd:2024:pres:46057:sheet32:row14`,455 votes. Remaining387 units provide85326 votes.

This is explicitly an **unofficial source-native/source-denominator** contract. The signed denominator428922 has ceil80 target343138. The303 source votes are191 short of that, while194 votes remain unallocated in known county scopes. No certified minimum/membership robustness is proved:343402 as an observed source crossing does not approve a certified native priority set. Coordinator acceptance and current geography are external. Separately, signed county concentration reaches80% at21 counties/346205 votes;20 have342469 and top15 counties318769. County concentration is a separate sensitivity, not a replacement for finer native order.

**Tie, cushion and feasible paths.** At fixed pair weights, unbounded share shift `(B−A)/(2*(A+B))` ties; A+1 pair-margin needs another0.5 A-share percentage points when nothing clips. Share points, pair-margin points and net votes are separate: a+1 share-point change adds+2 margin points and `.02*pair_volume` net votes. A+1 margin is1% of pair volume, not one vote or1% of all candidate votes. Shares are clipped to[0,1] and the feasible uniform shift is solved again, retaining the unclipped value. Negative/already-winning, no-positive-pool and bounded-impossible cases remain explicit.

| Source and full historical weights | Pair votes | Baseline A−B net | Unbounded tie share shift | Feasible clipped tie shift | Feasible A+1 shift | A+1 net cushion / all-candidate margin |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Signed2024 counties | 418,940 | -125,222 | +14.945100 pp | +14.954311 pp | +15.457885 pp | 4,189.40 / 0.976728 pp |
| Signed2020 counties | 420,219 | -132,245 | +15.735248 pp | +15.735248 pp | +16.237571 pp | 4,202.19 / 1.000000 pp |
| Signed2022 counties | 333,323 | -151,309 | +22.697054 pp | +22.728028 pp | +23.231519 pp | 3,333.23 / 0.957770 pp |
| Public2024 native691 | 418,749 | -125,127 | +14.940573 pp | +14.968032 pp | +15.472878 pp | 4,187.49 / 0.976724 pp |
| Public2020 native693 | 420,178 | -132,238 | +15.735950 pp | +15.747718 pp | +16.251421 pp | 4,201.78 / 1.000000 pp |
| Public2022 native687 | 333,323 | -151,309 | +22.697054 pp | +22.751580 pp | +23.257119 pp | 3,333.23 / 0.957770 pp |

The2024 county tie needs14.954311 share points after clipping Oglala Lakota, versus14.945100 unbounded. Native clipping changes the root further because unit weights/preferences differ. Targets in [unit-targets.csv.gz](data/baselines/unit-targets.csv.gz) contain all17756 county/native contributions, pair/all-candidate weights, participation, target shares/margins, net gains and the net-vote value of one share point. Each statewide target reconciles exactly within floating arithmetic tolerance. These are alternative sufficient combinations under fixed assumptions; no county target is individually necessary. A tie is not a win. [State targets](data/baselines/state-targets.json) also retain every historical other candidate and compare full plurality, so pair arithmetic never substitutes for the legal rule.

The separate **named2026 Bengs Independent versus Rounds Republican** scenario assumes Bengs repeats one stated historical A pair preference with that scenario’s pair volume, and that only those two current choices receive valid votes. Its all-candidate denominator is then that pair’s volume. Historical Libertarian/Independent shares and candidate-specific effects are not transferred to Bengs; no Democratic2026 choice is fabricated. Historical full-field denominator/cushion results remain alongside this explicitly different named-pair assumption.

**Historical low/base/high volume and mix sensitivity.** Low uses actual2022 Senate county all-candidate volumes (348020), base actual2020 same-seat Senate (420219), high actual2024 president (428922). For each historical preference anchor, county pair participation comes from that anchor’s own candidate votes, so scenario pair totals differ. Other candidates retain their own county all-candidate shares. All66 counties remain.

| Preference anchor | Volume/mix | Scenario pair volume | Baseline A−B net | Bounded tie share shift | Bounded A+1 share shift |
| --- | --- | ---: | ---: | ---: | ---: |
| 2024 | low: observed2022 counties | 339,929.775 | -102,451.606 | +15.079444 pp | +15.582953 pp |
| 2024 | base: observed2020 counties | 410,446.481 | -122,270.389 | +14.904253 pp | +15.408068 pp |
| 2024 | high: observed2024 counties | 418,940.000 | -125,222.000 | +14.954311 pp | +15.457885 pp |
| 2020 | low: observed2022 counties | 348,020.000 | -110,652.669 | +15.897458 pp | +16.400741 pp |
| 2020 | base: observed2020 counties | 420,219.000 | -132,245.000 | +15.735248 pp | +16.237571 pp |
| 2020 | high: observed2024 counties | 428,922.000 | -135,595.922 | +15.806594 pp | +16.309284 pp |
| 2022 | low: observed2022 counties | 333,323.000 | -151,309.000 | +22.728028 pp | +23.231519 pp |
| 2022 | base: observed2020 counties | 402,484.978 | -181,292.106 | +22.553940 pp | +23.057735 pp |
| 2022 | high: observed2024 counties | 410,824.366 | -185,587.036 | +22.617911 pp | +23.121465 pp |

The native low/base/high cases uniformly scale each election’s **own** complete native mix to those historical statewide all-candidate volumes; observed cases keep original votes unchanged. They preserve native pair participation and preferences, changing volume but not composition. This is explicitly sensitivity scaling, not allocation of certified residuals or a cross-year unit join. County-mix effects and native total-only effects are separated in [scenario settings](data/baselines/scenario-settings.json). None establishes2026 turnout, a candidate coalition, reporting method effects or lower preferences.

**Selected-unit-only and live remainder.** [Selected-unit-break-even.csv.gz](data/baselines/selected-unit-break-even.csv.gz) solves every county/native unit under each applicable scenario while every other unit stays at its stated historical preference, volume and zero shift. It retains required shares outside0–100%, with impossible/secured status and separate clipped display. [Editable historical input](data/baselines/historical-input-example.json) and the offline calculator allow another explicit elsewhere shift; all66 counties remain fixed except the selected one.

The [offline calculator](data/baselines/scripts/calculator.py) keeps all counted A/B/other votes fixed and forecasts only the stated remaining all-candidate pool, candidate by candidate. Remaining pair pool equals remaining total times one minus declared other-candidate shares. Required A share for margin m is `(m*FINAL_pair − counted_net + remaining_pair_pool)/(2*remaining_pair_pool)`. FINAL_pair includes counted pair votes; the final all-candidate denominator also includes all counted and forecast other votes. Selected-only live holds every other remaining contribution fixed. Final plurality compares all declared candidates. No completion flag supplies remaining votes.

The [15 synthetic cases](data/baselines/live-synthetic-scenarios.json) cover unknown pool/preference, no pool (tie/won/lost), negative inputs, impossible/secured paths, explicit low/high preference clipping, selected-only fixed elsewhere, a third candidate beating the pair winner, a positive other-only pool, and the FINAL denominator. In the latter case, counted400 Bengs/500 Rounds plus100 remaining pair votes needs105% remaining Bengs share for A+1: target net is10 on final1000, so it is impossible. Replacing that final denominator with remaining100 would be wrong. [Bounded synthetic cases](data/baselines/bounded-synthetic-scenarios.json) separately retain a negative already-winning shift, clipping, a restricted-shift impossible case and no positive pool. These are arithmetic examples, not calibrated probabilities or remaining-vote evidence. Reproduction/CLI commands are in the [schema](data/baselines/source/SCHEMA.md).

**Every county, numerical historical outcomes.** This compact table shows all signed county pair margins and full candidate-vote denominators; positive means the named historical A beat B. Complete counts for each candidate, raw rows, party identities and all denominator columns are in [county-baselines.csv](data/county-baselines.csv) and [county-candidates.csv](data/baselines/county-candidates.csv). Sources are the signed2024/2020/2022 canvasses cited above, not a constructed2026 electorate.

| County / FIPS | 2024 Harris−Trump pair margin | 2024 all candidates | 2020 Ahlers−Rounds pair margin | 2020 all candidates | 2022 Bengs−Thune pair margin | 2022 all candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Aurora / 46003 | -55.523 pp | 1,393 | -42.633 pp | 1,405 | -70.383 pp | 1,214 |
| Beadle / 46005 | -41.049 pp | 7,010 | -43.977 pp | 7,090 | -57.065 pp | 5,837 |
| Bennett / 46007 | -26.948 pp | 1,088 | -25.043 pp | 1,166 | -39.734 pp | 1,020 |
| Bon Homme / 46009 | -52.472 pp | 2,992 | -44.214 pp | 2,990 | -63.216 pp | 2,554 |
| Brookings / 46011 | -17.845 pp | 14,939 | -20.952 pp | 14,538 | -35.355 pp | 12,351 |
| Brown / 46013 | -27.333 pp | 17,043 | -27.993 pp | 17,451 | -42.197 pp | 13,921 |
| Brule / 46015 | -43.559 pp | 2,423 | -39.301 pp | 2,491 | -57.221 pp | 2,098 |
| Buffalo / 46017 | +27.912 pp | 466 | +18.165 pp | 545 | +7.733 pp | 390 |
| Butte / 46019 | -62.062 pp | 5,082 | -59.706 pp | 4,770 | -69.115 pp | 4,158 |
| Campbell / 46021 | -70.944 pp | 836 | -71.857 pp | 867 | -79.278 pp | 663 |
| Charles Mix / 46023 | -43.678 pp | 3,615 | -33.754 pp | 3,801 | -55.437 pp | 3,089 |
| Clark / 46025 | -53.812 pp | 1,842 | -51.272 pp | 1,847 | -70.072 pp | 1,593 |
| Clay / 46027 | +6.705 pp | 5,657 | -0.883 pp | 5,664 | -10.517 pp | 4,713 |
| Codington / 46029 | -41.770 pp | 13,510 | -44.662 pp | 13,105 | -57.037 pp | 11,004 |
| Corson / 46031 | -12.078 pp | 1,143 | -7.753 pp | 1,264 | -23.041 pp | 925 |
| Custer / 46033 | -46.701 pp | 6,001 | -45.638 pp | 5,456 | -57.385 pp | 5,040 |
| Davison / 46035 | -38.711 pp | 9,177 | -39.760 pp | 8,433 | -56.106 pp | 7,210 |
| Day / 46037 | -30.459 pp | 2,932 | -27.868 pp | 2,964 | -49.791 pp | 2,514 |
| Deuel / 46039 | -52.962 pp | 2,298 | -46.371 pp | 2,342 | -63.464 pp | 1,986 |
| Dewey / 46041 | +13.096 pp | 1,871 | +9.147 pp | 1,946 | -3.356 pp | 1,560 |
| Douglas / 46043 | -73.260 pp | 1,658 | -72.418 pp | 1,704 | -83.579 pp | 1,467 |
| Edmunds / 46045 | -61.638 pp | 2,031 | -54.907 pp | 1,987 | -69.109 pp | 1,687 |
| Fall River / 46047 | -50.540 pp | 4,274 | -50.375 pp | 4,002 | -61.100 pp | 3,641 |
| Faulk / 46049 | -66.818 pp | 1,130 | -64.141 pp | 1,188 | -73.333 pp | 947 |
| Grant / 46051 | -46.554 pp | 3,630 | -45.265 pp | 3,749 | -61.138 pp | 3,198 |
| Gregory / 46053 | -61.552 pp | 2,267 | -56.699 pp | 2,254 | -71.267 pp | 2,024 |
| Haakon / 46055 | -81.064 pp | 1,125 | -81.371 pp | 1,138 | -87.826 pp | 970 |
| Hamlin / 46057 | -61.514 pp | 3,226 | -57.199 pp | 3,070 | -71.628 pp | 2,703 |
| Hand / 46059 | -58.070 pp | 1,764 | -59.311 pp | 1,858 | -72.500 pp | 1,510 |
| Hanson / 46061 | -60.299 pp | 2,046 | -52.203 pp | 2,360 | -67.787 pp | 1,629 |
| Harding / 46063 | -88.030 pp | 820 | -81.750 pp | 800 | -92.982 pp | 668 |
| Hughes / 46065 | -30.924 pp | 8,435 | -41.892 pp | 8,763 | -52.923 pp | 7,451 |
| Hutchinson / 46067 | -58.889 pp | 3,736 | -58.871 pp | 3,754 | -72.530 pp | 3,142 |
| Hyde / 46069 | -56.342 pp | 695 | -59.775 pp | 711 | -72.242 pp | 580 |
| Jackson / 46071 | -35.676 pp | 1,129 | -35.849 pp | 1,113 | -48.317 pp | 899 |
| Jerauld / 46073 | -43.902 pp | 999 | -44.433 pp | 997 | -62.892 pp | 864 |
| Jones / 46075 | -77.654 pp | 550 | -66.779 pp | 596 | -78.555 pp | 465 |
| Kingsbury / 46077 | -44.707 pp | 2,801 | -41.778 pp | 2,779 | -63.867 pp | 2,530 |
| Lake / 46079 | -31.758 pp | 5,906 | -29.686 pp | 5,885 | -52.082 pp | 4,918 |
| Lawrence / 46081 | -32.247 pp | 15,409 | -36.579 pp | 13,743 | -46.765 pp | 12,146 |
| Lincoln / 46083 | -27.077 pp | 36,393 | -31.668 pp | 32,234 | -45.581 pp | 27,980 |
| Lyman / 46085 | -40.353 pp | 1,447 | -33.333 pp | 1,599 | -52.998 pp | 1,299 |
| Marshall / 46091 | -24.444 pp | 2,109 | -21.994 pp | 2,187 | -40.011 pp | 1,879 |
| McCook / 46087 | -50.473 pp | 3,031 | -42.552 pp | 2,907 | -66.571 pp | 2,533 |
| McPherson / 46089 | -70.510 pp | 1,299 | -64.421 pp | 1,321 | -79.661 pp | 1,102 |
| Meade / 46093 | -52.181 pp | 14,672 | -53.056 pp | 13,531 | -61.438 pp | 11,770 |
| Mellette / 46095 | -20.723 pp | 740 | -21.401 pp | 771 | -43.103 pp | 624 |
| Miner / 46097 | -48.325 pp | 1,167 | -40.838 pp | 1,146 | -66.940 pp | 1,004 |
| Minnehaha / 46099 | -12.989 pp | 93,986 | -15.260 pp | 91,572 | -30.536 pp | 74,144 |
| Moody / 46101 | -32.564 pp | 3,189 | -16.584 pp | 3,220 | -45.203 pp | 2,642 |
| Oglala Lakota / 46102 | +72.688 pp | 3,062 | +68.135 pp | 3,201 | +63.479 pp | 2,440 |
| Pennington / 46103 | -27.167 pp | 56,580 | -32.543 pp | 56,878 | -41.917 pp | 45,153 |
| Perkins / 46105 | -70.955 pp | 1,591 | -69.708 pp | 1,644 | -79.121 pp | 1,369 |
| Potter / 46107 | -66.379 pp | 1,298 | -67.630 pp | 1,384 | -76.792 pp | 1,093 |
| Roberts / 46109 | -23.417 pp | 4,149 | -17.737 pp | 4,296 | -40.898 pp | 3,531 |
| Sanborn / 46111 | -56.397 pp | 1,212 | -52.332 pp | 1,179 | -68.410 pp | 1,002 |
| Spink / 46115 | -39.922 pp | 3,139 | -37.674 pp | 3,164 | -57.559 pp | 2,664 |
| Stanley / 46117 | -47.627 pp | 1,735 | -54.237 pp | 1,652 | -64.570 pp | 1,447 |
| Sully / 46119 | -61.991 pp | 901 | -63.754 pp | 927 | -69.022 pp | 783 |
| Todd / 46121 | +51.911 pp | 2,126 | +43.565 pp | 2,502 | +44.530 pp | 1,911 |
| Tripp / 46123 | -64.122 pp | 2,654 | -62.677 pp | 2,690 | -75.235 pp | 2,237 |
| Turner / 46125 | -52.739 pp | 4,538 | -50.418 pp | 4,542 | -67.283 pp | 3,848 |
| Union / 46127 | -41.479 pp | 8,876 | -45.115 pp | 8,771 | -53.853 pp | 6,717 |
| Walworth / 46129 | -60.264 pp | 2,466 | -59.064 pp | 2,565 | -69.065 pp | 2,038 |
| Yankton / 46135 | -26.270 pp | 10,832 | -29.017 pp | 10,842 | -42.159 pp | 8,853 |
| Ziebach / 46137 | -2.918 pp | 781 | +0.881 pp | 908 | -23.296 pp | 678 |

**Reconciliation and handoff.** The independent originals-first extractor and redirected preflight reproductions reconcile all198 county vectors/594 candidate rows. Full public-native keys/literals/candidates/method scope/source cells/hashes and all691 descending order/304 keys agree with the actual turnout peer; the separate2022 PDF’s679 labels, triples and pages also agree. [Peer reconciliation](data/baselines/peer-reconciliation.json) pins both read-only inputs and711 independent checks. Local keys for2020/22 use a documented source-locator bijection; none is a geography crosswalk.

The [validator](data/baselines/validation.json) checks full-state denominators, weights, all-unit contributions, selected-only equations, bounded roots, synthetic final-denominator/plurality cases, exact integer80 crossings, full-field controls, raw originals/ordered parts, owned hashes, links and strict stored-object size bounds. The [complete owned manifest](data/baselines/asset-manifest.json) pins assets and read-only original/source chains. No Git actions or peer/shared file writes were performed.

Material qualifications remain precise: public2024 −194 and public2020 −41 are unallocated source-vintage disagreements; certified native priority membership robustness is unproved; original2022 PDF omits Yankton despite complete reconciled public coverage; scanned certified county-native rows are not comprehensively transcribed; direct current publication-ballot PDF bytes could not be downloaded despite successful primary web inspection. Current final operational IDs, approved November geometry, actual remaining-vote assumptions, collector/replay cadence and probability calibration remain external work. Historical targets/calculators are complete and usable offline under their declared assumptions.
