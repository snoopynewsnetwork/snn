# Nebraska historical partisanship and conditional winning paths

Research observed **October 19, 2026**. The priority baseline is the **2024 Class II two-year Senate special**, Pete Ricketts versus Preston Love Jr. Its published named-candidate denominator is **935,005**, with Ricketts **585,103** and Love **349,902**. Repeating those shares and weights leaves Love **235,201 votes behind**. A county-uniform **+12.577526 percentage-point A-share shift** ties the pair; **+13.077526 points** produces an illustrative **A+1 percentage-point pair margin**, or **9,350.05 expected net votes**. This is historical arithmetic, not a 2026 turnout forecast or candidate preference estimate. [Official 2024 canvass, PDF page 17](https://sos.nebraska.gov/sites/default/files/doc/elections/2024/2024%20General%20Canvass%20Book.pdf).

All **93 counties** and the complete disjoint **1,326 source-native special-election contexts** enter statewide calculations. Native clipping changes the base tie shift to **+12.582664 share points** and the A+1 shift to **+13.085124**, clipping six target shares at 100%. The unbounded formula is retained alongside the feasible bounded solution. The complete [native baseline CSV](data/baselines/native-baselines.csv) preserves the source-native inventory. Complete per-unit weights, gains, contributions and selected-unit-only thresholds are in [unit targets](data/baselines/scenarios/unit-targets.jsonl.gz) and [contributions](data/baselines/unit-contributions.csv). No nonpriority unit is dropped. Source originals are the [retained archived state HTML](data/baselines/source/reused-originals.json), [Douglas detail workbook](https://www.votedouglascounty-ne.gov/elections/2024/General/GN24ResultsDetail.xls), and [Lancaster final precinct PDF](https://web.archive.org/web/20260714153214id_/https://www.lancaster.ne.gov/DocumentCenter/View/25879/GN24-Precinct-Summary-Report-Final).

## Elections and complete candidate denominators

The 2024 six-year Fischer–Osborn contest is the **other Class I seat**; it is not the Ricketts–Love special. Dan Osborn is the named **By Petition independent**, never a Democrat. The actual recent midterm comparison is **2022 governor**, with no 2022 Senate election in the official canvass or final statewide candidate list. The earlier same-seat election is **2020 Senate**, with Janicek, Libertarian Siadek, qualified write-in Love, and scattering kept separate. No coalition is inferred. The [previous-elections authority index](https://sos.nebraska.gov/previous-elections) links the [2024](https://sos.nebraska.gov/sites/default/files/doc/elections/2024/2024%20General%20Canvass%20Book.pdf), [2022](https://sos.nebraska.gov/sites/default/files/doc/elections/2022/2022%20General%20Canvass%20Book.pdf) and [2020](https://sos.nebraska.gov/sites/default/files/doc/elections/2020/2020-General-Canvass-Book.pdf) canvasses and candidate lists. The 2024 candidate list explicitly prints two- and six-year Senate terms; the 2022 list has no Senate office. See [independently acquired list evidence](data/baselines/source/acquisition.json).

| Election / actual PDF pages | Complete published candidate columns, in source order | Published-column total | A versus B named pair | Pair total | Unbounded tie A-share shift |
| --- | --- | ---: | --- | ---: | ---: |
| 2024 same-seat Class II special / 17 | Pete Ricketts (Republican) **585,103**; Preston Love Jr. (Democratic) **349,902** | 935,005 | Love (Democratic) vs Ricketts (Republican) | 935,005 | +12.577526 pp |
| 2024 other-seat Class I regular / 16 | Deb Fischer (Republican) **499,124**; Dan Osborn (By Petition) **436,493**; Write-In Scatterings (generic scope) **2,719** | 938,336 | Osborn (By Petition) vs Fischer (Republican) | 935,617 | +3.347043 pp |
| 2024 president statewide / 11–12 | Donald J. Trump & JD Vance (Republican) **564,816**; Kamala D. Harris & Tim Walz (Democratic) **369,995**; Chase Oliver & Mike ter Maat (Libertarian) **6,399**; Cornel West & Melina Abdullah (Legal Marijuana NOW) **3,062**; Jill Stein & Samson Kpadenou (BY PETITION) **2,887**; Write-In Scatterings (generic scope) **5,023** | 952,182 | Harris/Walz (Democratic) vs Trump/Vance (Republican) | 934,811 | +10.420342 pp |
| 2022 governor / 13–14 | Jim Pillen & Joe Kelly (Republican) **398,334**; Carol Blood & Al Davis (Democratic) **242,006**; Scott Zimmerman & Jason Blumenthal (Libertarian) **26,455**; Write-In Scatterings (generic scope) **5,798** | 672,593 | Blood/Davis (Democratic) vs Pillen/Kelly (Republican) | 640,340 | +12.206640 pp |
| 2020 same-seat Senate / 16–17 | Ben Sasse (Republican) **583,507**; Chris Janicek (Democratic) **227,191**; Gene Siadek (Libertarian) **55,115**; Preston Love Jr. (Write-In) **58,411**; Write-In Scatterings (generic scope) **5,788** | 930,012 | Janicek (Democratic) vs Sasse (Republican) | 810,698 | +21.975878 pp |

The special's published-column total is **two named candidates only**, not a verified all-eligible-candidate denominator. The regular contest's 938,336 includes 2,719 scattering; its named pair is 935,617. President's 952,182 includes every printed slate and 5,023 scattering; statewide and congressional-district elector tables overlap and are not added. The 2020 Love write-in identity is distinct from his 2024 Democratic nomination. Every county/candidate column reconciles to its own statewide primary control in [state controls](data/baselines/extracts/state-controls.json), [complete county candidate rows](data/baselines/county-candidates.csv), and [county baselines](data/county-baselines.csv). Generic/scattering marks do not establish legally eligible named votes. [2024 canvass pages 11–17](https://sos.nebraska.gov/sites/default/files/doc/elections/2024/2024%20General%20Canvass%20Book.pdf), [2020 canvass pages 16–17](https://sos.nebraska.gov/sites/default/files/doc/elections/2020/2020-General-Canvass-Book.pdf), [write-in validity rule §32-1005](https://nebraskalegislature.gov/laws/statutes.php?statute=32-1005).

## Current five-choice publication and legal outcome

The current [SOS 2026 elections parent](https://sos.nebraska.gov/elections), freshly retrieved October 19, links the September 11 [Final Statewide General Candidate List](https://sos.nebraska.gov/sites/default/files/doc/elections/2026/Final_Statewide_General_Candidate_Filing_List_9.11.26.pdf). Its complete first page was independently rendered and visually read: **Pete Ricketts — Republican; Mike Marvin — Legal Marijuana NOW; Robin Richards — Nebraska Working People; Chuck Conboy — America First; Dan Osborn — By Petition**, six years, vote for one. There is **no Democratic-labeled Senate row**. The [September 11 certification announcement](https://sos.nebraska.gov/secretary-state-certifies-ballot-2026-general-election) and its linked one-page PDF are distinct evidence from the list. The fresh final-list bytes match retained SHA256 `d27a071715896b8c82b8cce8d48200b4207ba10c44f1778f56f92c4efcd7cf96`; all 24 original pages remain retained. [Roster/page evidence](data/baselines/extracts/current-final-roster.json), [complete page preview](data/baselines/source/previews/final-candidates-page1.png), [fresh receipts](data/baselines/source/acquisition.json).

The old setup catalog's literal parties and five choices remain separate from candidate identity; all five share **148**, a contest/search identifier, not five unique choice IDs. The setup uses `Legal Marijuana Now`, while the final printed list uses `NOW`. No old candidate ID is reused for November. No setup zero is admitted as counted votes. Later withdrawals, court changes, eligible write-ins, a signed certification instrument and unique November result keys are not established by this package. [Original setup and final roster](data/baselines/extracts/current-final-roster.json), [primary certification announcement](https://sos.nebraska.gov/secretary-state-certifies-ballot-2026-general-election).

Senate winning arithmetic compares **every individual candidate total**. A pair tie or pair A+1 does not ensure a five-choice plurality; equal highest totals require the statutory tie process. The offline tool retains every other choice separately and checks unique highest totals; it also exposes strict integer thresholds. No ranked-choice transfers, runoff electorate, lower preferences or automatic Love/Janicek/Osborn coalition is assumed. [Canvass/tie rule §32-1038](https://nebraskalegislature.gov/laws/statutes.php?statute=32-1038), [final vote-for-one publication](https://sos.nebraska.gov/sites/default/files/doc/elections/2026/Final_Statewide_General_Candidate_Filing_List_9.11.26.pdf).

## Native coverage, source disagreements and exact priority scope

Independent extraction selects 895 native contexts from 91 **complete** archived state HTML entities, 233 from the complete Douglas BIFF special table and 198 from the complete 1,431-page Lancaster PDF. Their disjoint named vectors close all 93 county canvass controls and 585,103 / 349,902 statewide. No state-HTML-to-local-workbook/PDF native crosswalk is used. The two truncated state-app entities retain 118 native headers each, partial final candidate rows and exactly 1,048,576 bytes; all 93 `_TOT` administrative rows remain separate. This leaves **329 full administrative/partial alternative objects**, never added to ranked children. Original public CSVs are race-area exports, not precinct recovery. [Raw receipts/URLs/hashes](data/baselines/source/reused-originals.json), [HTML coverage](data/baselines/extracts/html-coverage.json), [all original context positions](data/baselines/extracts/html-original-contexts.jsonl.gz), [complete native selection](data/baselines/extracts/native-special.jsonl.gz).

The full descending native order uses **named votes descending, stable source key ascending**. The smallest integer prefix is **765 / 748,190 / 935,005 = 80.019893%**; the preceding 764 have **747,645 = 79.961604%**. The crossing context is Lancaster **10 D-1**, actual PDF page **685**, Ricketts 190 / Love 355, pair 545. Native top 15 supply **26,773 = 2.863407%**. County concentration alone gives 20 counties / 753,953; that is sensitivity, not the source-native priority. Full 1,326 order, 561 remainder, all 93 parents/full-child/priority-child maps and all count/method fields independently agree with the actual turnout peer. [Independent reconciliation, bound to inspected peer hashes](data/baselines/peer-reconciliation.json), [original-derived controls](data/baselines/extracts/independent-controls.json). Coordinator acceptance remains separate.

Generic special marks are observed as Douglas 701, Lancaster 377, York 12, Nemaha 10, Clay 8, Nance 5, Garfield 2, Gosper 2 and Deuel 0: **1,117 across nine counties**. Only the first two counties' **431 selected native contexts / 1,078 marks** attach to the disjoint partition. Generic fields in the other **895 selected HTML contexts are unknown**. An explicit partial sensitivity adds only those known 1,078 marks: denominator **936,083**, 765-prefix **749,234**, and it replaces `html:39:0003` with Lancaster `page-419`. This is not a legally eligible-vote universe, complete all-candidate priority or proof of robust membership. If 233 genuinely eligible extra votes existed wholly outside the fixed named-scope 765, that set would fall below 80%; 1,795 wholly inside the fixed 764 could bring that set to 80%. These are conditional bounds, with no placement or eligibility inferred. The 30,231 difference between Total Voting and named special votes is only coarse capacity, including under/over/blank and non-Senate eligibility. [Original-derived universe and full sensitivity order](data/baselines/candidate-universe.json), [independent peer QA](data/baselines/universe-peer-QA.json), [source rules](https://nebraskalegislature.gov/laws/statutes.php?statute=32-1005).

Additional source checks preserve all 46 scanned contest contexts: York's 12 native contexts per Senate contest and 13 presidential contexts, Garfield's two native contexts per contest, and Deuel's three county-summary contests. Twelve further text-summary contexts cover Nemaha, Clay, Nance and Gosper. They independently close 21 county/contest vectors; OCR repairs are explicit and based on full rendered original pages, not residual allocation. Garfield's 14-page original includes school-district attachments on pages 13–14, beyond its 12-page native footer. Deuel explicitly says **UNOFFICIAL**; its president/regular-Senate method cells are blank and remain null. Alternate native PDF labels are never joined to state HTML IDs. York page 89 and Lancaster page 1431 each have a **presidential-only New or Former Resident** context; missing Senate sections are unavailable, not invented zero records. [Source references](data/baselines/source/extra-original-references.json), [independent scan contexts](data/baselines/extracts/independent-scan-contexts.jsonl.gz), [manual source-image repairs](data/baselines/source/scan-manual-repairs.json), [text summary contexts](data/baselines/extracts/extra-text-summary-contexts.jsonl.gz).

Douglas instructions combine early and polling-place votes; there is no native candidate-by-method split. All five BIFF tables preserve 1,167 contest contexts and 95 trailing 2020 formatted blank rows outside the actual footer. Twenty-one separate local PDF candidate fields agree. Preserve ballot-volume disagreements: 2024 Senate reconstructed Total Votes + over + under **277,919** versus PDF ballots **277,920**; president reconstructs 277,920. The one-ballot within-year difference is literal **03-02**, 1,201 Senate versus 1,202 president. The 2022 governor reconstruction **193,649** differs from summary ballots **193,653**; 2020 Senate **278,566** differs from **278,576**. The separate 2020 state canvass prints Douglas Total Voting **278,518**, so the local PDF is **58 higher** and the workbook reconstruction is **48 higher** than that state control; these are additional source disagreements, not an allocation. The 2020 PDF's Write-In Totals 29,275 is parent to Love 27,229 plus Not Assigned 2,046, not another candidate to add. No unexplained residual is repaired. [Douglas original archive](https://www.votedouglascounty-ne.gov/election_results.aspx), [summary controls and disagreements](data/baselines/extracts/douglas-summary-controls.json), [all original cells/types](data/baselines/extracts/douglas-original-rows.jsonl.gz).

Lancaster retains TOTAL, Election Day, Early Voting and Provisional columns for 595 selected contexts, with 199 separate statistics records; every row/method/contest balance passes. `Not Assigned` overlaps `Write-In Totals`. Registration has no method split. At statewide county level, complete 2024/2022/2020 registration and voting-method fields are retained independently. “Registered Voters” is the election canvass's printed denominator; no active/inactive status or separate snapshot date is invented. “Total Voting,” contest votes, valid named votes and registration remain different quantities. [Lancaster originals and receipt chain](data/baselines/source/reused-originals.json), [method contexts](data/baselines/extracts/lancaster-native-contexts.jsonl.gz), [statistics](data/baselines/extracts/lancaster-statistics.json), [2024 canvass pages 6–9](https://sos.nebraska.gov/sites/default/files/doc/elections/2024/2024%20General%20Canvass%20Book.pdf), [2022 pages 6–9](https://sos.nebraska.gov/sites/default/files/doc/elections/2022/2022%20General%20Canvass%20Book.pdf), [2020 pages 7–10](https://sos.nebraska.gov/sites/default/files/doc/elections/2020/2020-General-Canvass-Book.pdf).

Local and state registration figures also disagree, while the cited local ballot totals match the separate state Total Voting controls. The publication snapshots/statuses are not established as equivalent; none is repaired or allocated. [Complete comparison and source rows](data/baselines/extracts/registration-source-disagreements.json).

| County / primary local publication | Local registered | State canvass registered | Local minus state |
| --- | ---: | ---: | ---: |
| [Nemaha](https://countyelectionresults.nebraska.gov/election_files/Nemaha/2024_General_official_results.pdf) | 4,465 | 4,469 | -4 |
| [Clay](https://countyelectionresults.nebraska.gov/election_files/Clay/2024_General_official_results.pdf) | 4,179 | 4,167 | +12 |
| [Nance](https://countyelectionresults.nebraska.gov/election_files/Nance/2024_General_official_results.pdf) | 2,407 | 2,404 | +3 |
| [Gosper](https://countyelectionresults.nebraska.gov/election_files/Gosper/2024_General_official_results.pdf) | 1,431 | 1,432 | -1 |
| [Lancaster](https://web.archive.org/web/20260714153214id_/https://www.lancaster.ne.gov/DocumentCenter/View/25879/GN24-Precinct-Summary-Report-Final) | 206,570 | 206,406 | +164 |
| [Deuel](https://countyelectionresults.nebraska.gov/election_files/Deuel/2024_General_unofficial_results.pdf) | 1,412 | 1,411 | +1 |

The November 11 public CSV still has Ricketts 577,711 / Love 341,868 and Fischer 493,039 / Osborn 427,278 despite 1326/1326 counters. January 19's separate export matches final named controls. Their literal clocks have no established timezone; they are not a proved correction sequence or a percent-votes-counted signal. Preserve old export party codes `REP`, `DEM`, `PET` and source candidate IDs separately from current setup 148. [Original rows and complete headers/trailing empty field](data/baselines/extracts/historical-Senate-export-rows.jsonl.gz), [download receipts](data/baselines/candidate-universe.json).

## Declared historical volume and preference sensitivity

Each county's 2024-special pair participation is `p_c=(Love_c+Ricketts_c)/2024_TotalVoting_c`. For a historical mix year y, use `T_c=TotalVoting_y,c*p_c`. Base reproduces all 935,005 named votes exactly. Low and high change both historical volume and county mix. For native sensitivity, distribute that county's hypothetical T in its **observed 2024-special pair proportions**; this is not observed older native turnout or a cross-year identity join. The five preference anchors above remain separate. Each also has its own actual historical pair-weight run. [Settings](data/baselines/settings.json), [all 46 state targets](data/baselines/scenarios/state-targets.csv), primary voting statistics cited above.

| Sensitivity | Historical Total Voting | Derived special-pair volume | County-uniform special tie share shift | Native bounded tie share shift |
| --- | ---: | ---: | ---: | ---: |
| low_2022_voting_mix | 682,716 | 661,341.247 | +12.974902 pp | +12.981888 pp |
| base_2024_voting_mix | 965,236 | 935,005.000 | +12.577526 pp | +12.582664 pp |
| high_2020_voting_mix | 966,920 | 936,614.982 | +12.774667 pp | +12.780777 pp |

For weights T and baseline q, the net contribution is `T*(2*q-1)`. At fixed positive weights, `(B-A)/(2*(A+B))` is the unbounded tie shift; A+1 pair margin adds **0.5 share points**, not one. One share point changes pair margin by two points and net votes by `0.02*T` before clipping. The calculator explicitly clips target shares and solves the monotone bounded statewide equation. A negative shift for an already-winning anchor is retained; zero pool, unknown anchor, infeasible margin and unbounded selected requirements have separate statuses. An exact continuous tie may not be integer-realizable: with 935,005 pair votes, 467,503 A votes beat 467,502 B by one vote; the illustrative 1-point cushion is a different target. [Calculator implementation](data/baselines/calculator.py), [edge cases](data/baselines/scenarios/target-edge-cases.json).

Fifty-four explicit [current five-choice paths](data/baselines/scenarios/current-five-choice.json) retain Conboy, Marvin and Richards individually. They show assumptions of 1% each, and a stress case with Conboy 55%, Marvin 1%, Richards 1%, holding stated pair volume fixed. Historical Love–Ricketts or Osborn–Fischer pair shares are transported to Osborn–Ricketts **only as an explicit user-assumption scenario**; no candidate effect is estimated. All county/native contributions remain in [five-choice unit rows](data/baselines/scenarios/current-five-choice-units.jsonl.gz). Pair A+1 and final all-candidate A+1 use different denominators. With three other choices at 1% each, +1 pair point is +0.97 all-candidate points; the full denominator is T/0.97. The 55% third-choice case makes a pair-only path fail the legal highest-vote condition. Eligible write-ins are assumed zero only in those synthetic examples, not in actual ballot research. These examples are arithmetic, not probabilities or preferred turnout assumptions. Final names/parties derive only from the [final primary publication](https://sos.nebraska.gov/sites/default/files/doc/elections/2026/Final_Statewide_General_Candidate_Filing_List_9.11.26.pdf).

## Every county: special baseline and conditional tie contribution

These labels describe November 2024 outcomes. Love leads in Douglas and Lancaster; the other 91 counties favor Ricketts. Under the distinct regular Senate baseline, named independent Osborn leads in Douglas, Lancaster, Sarpy and Thurston. Neither observation makes all opposition Democratic. Complete comparator candidates and denominators for every county are in the linked CSVs. [2024 canvass pages 16–17](https://sos.nebraska.gov/sites/default/files/doc/elections/2024/2024%20General%20Canvass%20Book.pdf).

“Selected alone” fixes **every other county** at its own observed 2024-special pair share and volume. Values above 100% are impossible under those assumptions; they remain unbounded in the data. The uniform target is an alternative statewide combination, not a necessary county target. Every native unit has the same selected-unit-only calculation in the compressed targets file; all 1,326 are individually insufficient to erase the statewide deficit with the rest fixed. [Generated full target rows](data/baselines/scenarios/unit-targets.jsonl.gz).

| County | Love / Ricketts | Love pair share | Named weight | Love–Ricketts net | Uniform-tie Love share | +1 share pp net gain | Selected alone tie share |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Adams | 3,715 / 10,438 | 26.249% | 1.5137% | -6,723 | 38.826% | 283.06 | 857.172% impossible |
| Antelope | 342 / 3,066 | 10.035% | 0.3645% | -2,724 | 22.613% | 68.16 | 3460.754% impossible |
| Arthur | 18 / 267 | 6.316% | 0.0305% | -249 | 18.893% | 5.70 | 41269.649% impossible |
| Banner | 25 / 357 | 6.545% | 0.0409% | -332 | 19.122% | 7.64 | 30792.016% impossible |
| Blaine | 29 / 261 | 10.000% | 0.0310% | -232 | 22.578% | 5.80 | 40561.897% impossible |
| Boone | 423 / 2,569 | 14.138% | 0.3200% | -2,146 | 26.715% | 59.84 | 3944.636% impossible |
| Box Butte | 985 / 3,876 | 20.263% | 0.5199% | -2,891 | 32.841% | 97.22 | 2439.529% impossible |
| Boyd | 207 / 849 | 19.602% | 0.1129% | -642 | 32.180% | 21.12 | 11156.013% impossible |
| Brown | 170 / 1,457 | 10.449% | 0.1740% | -1,287 | 23.026% | 32.54 | 7238.506% impossible |
| Buffalo | 5,791 / 17,707 | 24.645% | 2.5131% | -11,916 | 37.222% | 469.96 | 525.115% impossible |
| Burt | 888 / 2,696 | 24.777% | 0.3833% | -1,808 | 37.354% | 71.68 | 3306.041% impossible |
| Butler | 749 / 3,758 | 16.619% | 0.4820% | -3,009 | 29.196% | 90.14 | 2625.904% impossible |
| Cass | 4,606 / 10,808 | 29.882% | 1.6485% | -6,202 | 42.459% | 308.28 | 792.828% impossible |
| Cedar | 614 / 4,263 | 12.590% | 0.5216% | -3,649 | 25.167% | 97.54 | 2423.918% impossible |
| Chase | 165 / 1,669 | 8.997% | 0.1961% | -1,504 | 21.574% | 36.68 | 6421.238% impossible |
| Cherry | 306 / 2,671 | 10.279% | 0.3184% | -2,365 | 22.856% | 59.54 | 3960.581% impossible |
| Cheyenne | 733 / 3,689 | 16.576% | 0.4729% | -2,956 | 29.154% | 88.44 | 2676.018% impossible |
| Clay | 506 / 2,767 | 15.460% | 0.3501% | -2,261 | 28.037% | 65.46 | 3608.509% impossible |
| Colfax | 772 / 2,713 | 22.152% | 0.3727% | -1,941 | 34.730% | 69.70 | 3396.628% impossible |
| Cuming | 664 / 3,720 | 15.146% | 0.4689% | -3,056 | 27.724% | 87.68 | 2697.639% impossible |
| Custer | 632 / 5,206 | 10.826% | 0.6244% | -4,574 | 23.403% | 116.76 | 2025.223% impossible |
| Dakota | 1,981 / 4,067 | 32.755% | 0.6468% | -2,086 | 45.332% | 120.96 | 1977.207% impossible |
| Dawes | 884 / 2,922 | 23.226% | 0.4071% | -2,038 | 35.804% | 76.12 | 3113.098% impossible |
| Dawson | 1,887 / 6,579 | 22.289% | 0.9054% | -4,692 | 34.867% | 169.32 | 1411.381% impossible |
| Deuel | 143 / 851 | 14.386% | 0.1063% | -708 | 26.964% | 19.88 | 11845.423% impossible |
| Dixon | 520 / 2,314 | 18.349% | 0.3031% | -1,794 | 30.926% | 56.68 | 4167.978% impossible |
| Dodge | 4,991 / 11,195 | 30.835% | 1.7311% | -6,204 | 43.413% | 323.72 | 757.392% impossible |
| Douglas | 142,256 / 127,726 | 52.691% | 28.8749% | +14,530 | 65.268% | 5,399.64 | 96.250% |
| Dundy | 79 / 834 | 8.653% | 0.0976% | -755 | 21.230% | 18.26 | 12889.321% impossible |
| Fillmore | 557 / 2,435 | 18.616% | 0.3200% | -1,878 | 31.194% | 59.84 | 3949.114% impossible |
| Franklin | 195 / 1,395 | 12.264% | 0.1701% | -1,200 | 24.842% | 31.80 | 7408.522% impossible |
| Frontier | 158 / 1,231 | 11.375% | 0.1486% | -1,073 | 23.953% | 27.78 | 8477.934% impossible |
| Furnas | 308 / 2,096 | 12.812% | 0.2571% | -1,788 | 25.390% | 48.08 | 4904.680% impossible |
| Gage | 3,015 / 7,795 | 27.891% | 1.1561% | -4,780 | 40.468% | 216.20 | 1115.777% impossible |
| Garden | 131 / 972 | 11.877% | 0.1180% | -841 | 24.454% | 22.06 | 10673.753% impossible |
| Garfield | 85 / 902 | 8.612% | 0.1056% | -817 | 21.189% | 19.74 | 11923.556% impossible |
| Gosper | 157 / 971 | 13.918% | 0.1206% | -814 | 26.496% | 22.56 | 10439.495% impossible |
| Grant | 13 / 345 | 3.631% | 0.0383% | -332 | 16.209% | 7.16 | 32852.933% impossible |
| Greeley | 158 / 1,049 | 13.090% | 0.1291% | -891 | 25.668% | 24.14 | 9756.297% impossible |
| Hall | 6,273 / 16,100 | 28.038% | 2.3928% | -9,827 | 40.616% | 447.46 | 553.674% impossible |
| Hamilton | 927 / 4,585 | 16.818% | 0.5895% | -3,658 | 29.395% | 110.24 | 2150.354% impossible |
| Harlan | 233 / 1,558 | 13.009% | 0.1915% | -1,325 | 25.587% | 35.82 | 6579.202% impossible |
| Hayes | 21 / 472 | 4.260% | 0.0527% | -451 | 16.837% | 9.86 | 23858.316% impossible |
| Hitchcock | 150 / 1,271 | 10.556% | 0.1520% | -1,121 | 23.133% | 28.42 | 8286.453% impossible |
| Holt | 589 / 4,818 | 10.893% | 0.5783% | -4,229 | 23.471% | 108.14 | 2185.861% impossible |
| Hooker | 50 / 370 | 11.905% | 0.0449% | -320 | 24.482% | 8.40 | 28012.024% impossible |
| Howard | 590 / 2,925 | 16.785% | 0.3759% | -2,335 | 29.363% | 70.30 | 3362.461% impossible |
| Jefferson | 813 / 2,786 | 22.590% | 0.3849% | -1,973 | 35.167% | 71.98 | 3290.178% impossible |
| Johnson | 563 / 1,556 | 26.569% | 0.2266% | -993 | 39.147% | 42.38 | 5576.380% impossible |
| Kearney | 627 / 2,963 | 17.465% | 0.3840% | -2,336 | 30.043% | 71.80 | 3293.245% impossible |
| Keith | 656 / 3,486 | 15.838% | 0.4430% | -2,830 | 28.415% | 82.84 | 2855.058% impossible |
| Keya Paha | 34 / 498 | 6.391% | 0.0569% | -464 | 18.969% | 10.64 | 22111.748% impossible |
| Kimball | 242 / 1,444 | 14.353% | 0.1803% | -1,202 | 26.931% | 33.72 | 6989.472% impossible |
| Knox | 662 / 3,727 | 15.083% | 0.4694% | -3,065 | 27.661% | 87.78 | 2694.520% impossible |
| Lancaster | 78,598 / 77,189 | 50.452% | 16.6616% | +1,409 | 63.030% | 3,115.74 | 125.940% impossible |
| Lincoln | 3,296 / 13,034 | 20.184% | 1.7465% | -9,738 | 32.761% | 326.60 | 740.334% impossible |
| Logan | 25 / 417 | 5.656% | 0.0473% | -392 | 18.234% | 8.84 | 26612.104% impossible |
| Loup | 64 / 364 | 14.953% | 0.0458% | -300 | 27.531% | 8.56 | 27491.706% impossible |
| Madison | 3,054 / 12,376 | 19.793% | 1.6503% | -9,322 | 32.370% | 308.60 | 781.948% impossible |
| McPherson | 11 / 268 | 3.943% | 0.0298% | -257 | 16.520% | 5.58 | 42154.659% impossible |
| Merrick | 654 / 3,645 | 15.213% | 0.4598% | -2,991 | 27.790% | 85.98 | 2750.744% impossible |
| Morrill | 332 / 2,047 | 13.955% | 0.2544% | -1,715 | 26.533% | 47.58 | 4957.230% impossible |
| Nance | 306 / 1,473 | 17.201% | 0.1903% | -1,167 | 29.778% | 35.58 | 6627.684% impossible |
| Nemaha | 869 / 2,490 | 25.871% | 0.3592% | -1,621 | 38.448% | 67.18 | 3526.928% impossible |
| Nuckolls | 328 / 1,894 | 14.761% | 0.2376% | -1,566 | 27.339% | 44.44 | 5307.313% impossible |
| Otoe | 2,331 / 5,717 | 28.964% | 0.8607% | -3,386 | 41.541% | 160.96 | 1490.203% impossible |
| Pawnee | 282 / 1,078 | 20.735% | 0.1455% | -796 | 33.313% | 27.20 | 8667.831% impossible |
| Perkins | 158 / 1,247 | 11.246% | 0.1503% | -1,089 | 23.823% | 28.10 | 8381.388% impossible |
| Phelps | 657 / 4,283 | 13.300% | 0.5283% | -3,626 | 25.877% | 98.80 | 2393.877% impossible |
| Pierce | 398 / 3,471 | 10.287% | 0.4138% | -3,073 | 22.864% | 77.38 | 3049.845% impossible |
| Platte | 2,818 / 12,709 | 18.149% | 1.6606% | -9,891 | 30.727% | 310.54 | 775.543% impossible |
| Polk | 448 / 2,360 | 15.954% | 0.3003% | -1,912 | 28.532% | 56.16 | 4204.006% impossible |
| Red Willow | 1,338 / 3,919 | 25.452% | 0.5622% | -2,581 | 38.029% | 105.14 | 2262.479% impossible |
| Richardson | 847 / 2,980 | 22.132% | 0.4093% | -2,133 | 34.710% | 76.54 | 3095.048% impossible |
| Rock | 64 / 746 | 7.901% | 0.0866% | -682 | 20.479% | 16.20 | 14526.481% impossible |
| Saline | 1,765 / 3,809 | 31.665% | 0.5961% | -2,044 | 44.242% | 111.48 | 2141.469% impossible |
| Sarpy | 41,332 / 57,907 | 41.649% | 10.6137% | -16,575 | 54.226% | 1,984.78 | 160.151% impossible |
| Saunders | 3,240 / 10,081 | 24.322% | 1.4247% | -6,841 | 36.900% | 266.42 | 907.143% impossible |
| Scotts Bluff | 3,599 / 11,302 | 24.153% | 1.5937% | -7,703 | 36.730% | 298.02 | 813.365% impossible |
| Seward | 2,157 / 6,981 | 23.605% | 0.9773% | -4,824 | 36.182% | 182.76 | 1310.544% impossible |
| Sheridan | 319 / 2,123 | 13.063% | 0.2612% | -1,804 | 25.641% | 48.84 | 4828.808% impossible |
| Sherman | 286 / 1,367 | 17.302% | 0.1768% | -1,081 | 29.879% | 33.06 | 7131.670% impossible |
| Sioux | 60 / 612 | 8.929% | 0.0719% | -552 | 21.506% | 13.44 | 17509.003% impossible |
| Stanton | 447 / 2,599 | 14.675% | 0.3258% | -2,152 | 27.253% | 60.92 | 3875.492% impossible |
| Thayer | 452 / 2,384 | 15.938% | 0.3033% | -1,932 | 28.515% | 56.72 | 4162.641% impossible |
| Thomas | 41 / 346 | 10.594% | 0.0414% | -305 | 23.172% | 7.74 | 30398.320% impossible |
| Thurston | 825 / 1,234 | 40.068% | 0.2202% | -409 | 52.646% | 41.18 | 5751.603% impossible |
| Valley | 321 / 1,935 | 14.229% | 0.2413% | -1,614 | 26.806% | 45.12 | 5227.017% impossible |
| Washington | 3,239 / 9,145 | 26.155% | 1.3245% | -5,906 | 38.732% | 247.68 | 975.771% impossible |
| Wayne | 894 / 3,160 | 22.052% | 0.4336% | -2,266 | 34.630% | 81.08 | 2922.903% impossible |
| Webster | 262 / 1,477 | 15.066% | 0.1860% | -1,215 | 27.644% | 34.78 | 6777.602% impossible |
| Wheeler | 49 / 419 | 10.470% | 0.0501% | -370 | 23.048% | 9.36 | 25138.782% impossible |
| York | 1,448 / 5,470 | 20.931% | 0.7399% | -4,022 | 33.508% | 138.36 | 1720.851% impossible |

## Offline live-remainder calculator and reproduction

Run from the repository root:

```sh
python3 -B senate/2026/nebraska/data/baselines/calculator.py live senate/2026/nebraska/data/baselines/scenarios/live-ordinary.json
python3 -B senate/2026/nebraska/data/baselines/reproduce.py
python3 -B senate/2026/nebraska/data/baselines/validate.py --check-manifest
```

The [16 meaningful synthetic live inputs and outputs](data/baselines/scenarios/live-results.json) cover unknown pool, unknown other additions, no pool/tie/secured, negative pool, impossible, secured, clipping both directions, unknown preference, third-candidate victory, nonzero remaining other votes and selected remaining units. Edit a copied input within the owned directory to declare a different pool. The calculator needs no network. Counted A, B and each other candidate stay fixed. Let counted lead be L, remaining pair U, counted pair C and final other votes O. Final pair denominator is `C+U`; final all-candidate denominator is `C+U+O`. Tie remainder share is `(U-L)/(2*U)`; final pair A+1 is `(U-L+0.01*(C+U))/(2*U)`, while final all-candidate A+1 substitutes the full final denominator. Selected-unit thresholds subtract explicit remaining net votes everywhere else. Unknown pool/preferences stay unknown; no remaining pool uses observed outcomes. Strict integer plurality compares A with B and each other candidate. No calibrated win probability is emitted. [Offline calculator](data/baselines/calculator.py).

The [SCHEMA and reproduction contract](data/baselines/source/SCHEMA.md) explains every file, units, source keys, party identities, nulls, bounded shifts and external dependencies. The [validator](data/baselines/validate.py), [validation output](data/baselines/validation.json) and [asset manifest](data/baselines/asset-manifest.json) audit candidate sums, identities, all native/order/parent coverage, exact integer 80%, scenario denominators, clipping, counted-vote preservation, relative links and raw/stored hashes. Complete originals are reused read-only by individual hashes; no dependency/cache directories or artifacts at or above 40,000,000 bytes are retained. Acquisition can be refreshed separately with `acquire.py --fetch` and `--linked-documents`; offline reproduction never fetches.

Material limits remain explicit: statewide eligible/generic special-write-in completeness and priority robustness are unproved; current ballot changes/write-ins/unique result IDs are unaudited; historical-native geometry/current equivalence is unapproved. Native comparison coverage is complete for the priority special only: other-seat/president local observations and 2022/2020 Douglas contexts remain source-scoped, rather than filling missing statewide native comparisons. Unexplained ballot disagreements and old partial/truncated publications are retained. No current live collector, genuine current counts, arrival cadence, remaining-vote estimate, calibrated Needle or 2026 turnout projection is claimed.
