# Virginia historical partisanship and conditional paths

Research snapshot: **2026-10-20 UTC**. All **133 locality parents: 95 counties and 38 independent cities** remain distinct. Historical counts describe named contests, not permanent partisan identities or 2026 turnout forecasts. This assignment supplies source evidence and offline arithmetic; it implements no collector, probability model or election call.

At the 2024 Kaine–Cao baseline, Kaine already leads by **397,204 votes**. Fixed pair weights give an unbounded tie shift of **−4.476016 A-share percentage points**; an illustrative **A+1 pair-margin** uses **−3.976016 share points**. At native resolution clipping one low-share unit changes the feasible tie shift to **−4.476158 points**. A+1 needs no native clipping. These are alternative conditional statewide combinations; no locality is individually required to improve. Counts come from the official [2024 Senate table](https://va2.elstats.civera.com/api/download_contest/161257_table.csv?split_party=false) and its [historical contest](https://historical.elections.virginia.gov/contest/161257); the independent bounded calculation is retained in [state targets](data/baselines/historical-state-targets.csv).

Virginia’s 2026 regular race is **Class II**. **2020 Warner–Gade** is the same seat; **2024 Kaine–Cao** is the other Class I seat and the primary recent-volume basis. **2018 Senate** is the actual recent Senate midterm comparator. Virginia held neither Senate nor governor in 2022: the retained 2022 turnout/House administration is separate. Primary contest identities are explicit in [2020](https://historical.elections.virginia.gov/contest/144564), [2018](https://historical.elections.virginia.gov/contest/134055) and the separate [2024 presidential contest](https://historical.elections.virginia.gov/contest/161256).

The current [ELECT November federal publication](https://www.elections.virginia.gov/casting-a-ballot/candidate-list/november-3-2026-gen-elect-federal-offices/) and its linked [10/6/2026 workbook](https://www.elections.virginia.gov/media/castyourballot/candidatelist/2026/2026-November-Federal-Offices-Candidate-List-(rev-10-6-2026).xlsx) list **Mark R. Warner — Democratic** and **Bert Mizusawa — Republican** for Senate. This is a published general-election roster snapshot, not primary-nominee inference. [Retained cells](data/baselines/current-ballot-publication.json) preserve row positions; later amendments and operational November candidate/feed IDs require rechecking. Historical candidate effects and current remaining-vote preferences are not inferred from those names.

## Complete candidate and denominator controls

Every count below uses the source’s printed candidate votes plus generic write-in marks. These are contest votes/marks, **not ballots cast**. A/B pair denominators exclude every other candidate and generic category; all-candidate denominators retain them. State controls equal every native candidate sum in all four independent extractions. The full [532-row locality file](data/county-baselines.csv), [11,009 native rows](data/baselines/native-baselines.csv), [original hierarchy/control extraction](data/baselines/source-controls.json) and [source pins](data/baselines/source/input-pins.json) retain complete identities and raw evidence.

| Contest / pair A–B | A | B | Other printed marks | A+B | All candidates+generic | A pair share | Pair margin | A-leading parents |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2024-senate: Timothy M. Kaine – Hung Cao | 2,417,115 | 2,019,911 | 8,509 | 4,437,026 | 4,445,535 | 54.476016% | +8.952032 pp | 45 |
| 2024-president: Kamala D. Harris – Donald J. Trump | 2,335,395 | 2,075,085 | 95,461 | 4,410,480 | 4,505,941 | 52.951039% | +5.902079 pp | 43 |
| 2020-senate: Mark Robert Warner – Daniel Mac Arthur Gade | 2,466,500 | 1,934,199 | 4,388 | 4,400,699 | 4,405,087 | 56.047914% | +12.095828 pp | 49 |
| 2018-senate: Timothy Michael Kaine – Corey Alan Stewart | 1,910,370 | 1,374,313 | 67,074 | 3,284,683 | 3,351,757 | 58.159950% | +16.319901 pp | 52 |

Complete fields: 2024 Senate Timothy M. Kaine (Democratic) 2,417,115; Hung Cao (Republican) 2,019,911; generic Write-Ins 8,509. 2020 Senate Mark Robert Warner (Democratic) 2,466,500; Daniel Mac Arthur Gade (Republican) 1,934,199; generic 4,388. 2018 Senate Timothy Michael Kaine (Democratic) 1,910,370; Corey Alan Stewart (Republican) 1,374,313; **Matthew Joseph Waters (Libertarian) 61,565**; generic 5,509. President: **Kamala D. Harris (Democratic) 2,335,395; Donald J. Trump (Republican) 2,075,085; Jill E. Stein (Green) 34,888; Chase R. Oliver (Libertarian) 19,814; Cornel R. West (Independent) 8,984; Claudia De la Cruz (Independent) 8,410; generic 23,365**. These are separate candidates; no independent/Libertarian/generic vote is labeled Democratic. The direct downloads are [2020](https://va2.elstats.civera.com/api/download_contest/144564_table.csv?split_party=false), [2018](https://va2.elstats.civera.com/api/download_contest/134055_table.csv?split_party=false) and [president](https://va2.elstats.civera.com/api/download_contest/161256_table.csv?split_party=false).

**Source disagreements remain:** 2018 named candidates close at state, locality and native levels, but locality footer generic sums are **5,473**, versus **5,509 native/state**. Native-minus-footer residuals are Fairfax City +1, Richmond City +10, Roanoke County +25; all 36 stay unallocated. The footer denominator is 3,351,721; native/state denominator is 3,351,757. Scenario parent weights explicitly use native aggregates. Both [2018](https://historical.elections.virginia.gov/contest/134055) and [2020](https://historical.elections.virginia.gov/contest/144564) compiled pages warn of conflicting official/unofficial totals. Their arithmetic closure does not settle certification chronology or cause. Literal exported Undervotes0 is not established as a ballot-universe control.

The [2024 Senate HTML](https://historical.elections.virginia.gov/contest/161257) retains alternative `nVotesParty1`: Kaine 2,418,944; Cao 2,020,475; Total Votes Cast 4,439,419, versus the selected CSV/`nVotes` fields. The [presidential page](https://historical.elections.virginia.gov/contest/161256) also differs in its alternate party fields. Whole candidate/pseudocandidate/party/control objects survive in [hydration extracts](data/baselines/extracted/). No field is silently repaired, rescaled or used to explain a residual. Historical database verification clocks (2024 Senate 2026-05-18T14:20:50Z; president 2026-05-18T13:39:02Z; 2020 2025-10-23T21:35:07Z; 2018 null) are distinct from original certification dates. Original signed/amended certification chronology remains unresolved in this bounded package.

## Native coverage and priority contract

The primary source has **2,669 native rows**, including precinct/provisional/central/admin identities; 2020 has 2,846 and 2018 has 2,825. President independently has 2,669 rows across all 133 parents. No native count/name equality establishes crossyear geometry. Full official 2024 state plus all133 locality Senate JSON entities, candidate/method objects, UUIDs, virtual flags, reporting statuses and null controls are pinned. Each unique complete within-parent candidate vector associates the historical record with an unaltered API object as a numerical check, not approved geographic equivalence. The [source-native associations](data/baselines/native-associations.json.gz) retain both identities, every matching bulk constituent and turnout row. The official bulk report retains **48 extra allzero Senate rows (16 triplets) with blank PrecinctId**; they are not deduplicated. All 2,669 presidential seven-component vectors independently match their official bulk controls. The acquisition chain begins at the historical pages and linked [official 2024 ENR](https://enr.elections.virginia.gov/results/public/Virginia/elections/2024NovemberGeneral); exact individual URLs/receipts are in the pins.

Sort reported named+generic volume descending, ties **numeric original logical CSV record ascending**. Native minimum80 is **1,538 rows / 3,557,034 votes / 80.0136%**; 1,537 rows supply 3,555,604, below the integer threshold **3,556,428**. All 1,131 remaining rows / 888,501 votes stay in every statewide scenario. Top15 native rows supply 80,617 / 1.8134%. Parent sensitivity is 44 localities, crossing at 3,577,883; its preceding43 supply 3,556,301. Parent top15 supply 2,483,152. [Complete own order](data/baselines/independent-priority.json) and [all17source orders](data/baselines/all-source-sensitivity-orders.json.gz) retain every nonpriority/unknown case. This reported-mark contract does not establish legal eligible named-write-in robustness.

| Native rank | Parent | Literal historical label | Source record | Reported marks |
|---:|---|---|---:|---:|
| 1 | Fairfax County | Provisional | 954 | 14,667 |
| 2 | Prince William County | PRINCE WILLIAM COUNTY PROVISIONALS | 2132 | 6,673 |
| 3 | Chesterfield County | 319 - Magnolia | 523 | 5,636 |
| 4 | Richmond City | Provisional | 2235 | 4,909 |
| 5 | Loudoun County | LOUDOUN COUNTY PROVISIONALS | 1582 | 4,727 |
| 6 | Chesterfield County | 320 - Dry Creek | 524 | 4,710 |
| 7 | Virginia Beach City | PROVISIONALS | 2701 | 4,674 |
| 8 | Arlington County | PROVISIONALS | 188 | 4,515 |
| 9 | Chesterfield County | 504 - Robious | 545 | 4,423 |
| 10 | James City County | 402 - Stonehouse B | 1417 | 4,413 |
| 11 | Chesterfield County | 108 - Ecoff | 490 | 4,327 |
| 12 | Arlington County | 118 - Precinct 118 | 151 | 4,278 |
| 13 | Chesterfield County | 211 - Nash | 505 | 4,266 |
| 14 | Chesterfield County | 414 - Crenshaw | 537 | 4,218 |
| 15 | Chesterfield County | 109 - Elizabeth Scott | 491 | 4,181 |

Own extraction/parser/input pins/full order were frozen [before peer access](data/baselines/pre-peer-witness.json), SHA256 `0ceae3b881ee35bfc226f28313b657a0b09c23f34f7ad982d1695fad1526d56c`. The [captured turnout core](data/baselines/peer-capture.json) is lossless and read-only. [Candidate/native/method audit](data/baselines/peer-reconciliation.json), [raw-field/control audit](data/baselines/peer-additional-reconciliation.json) and [all17 full-order/crossing audit](data/baselines/peer-all-order-audit.json) find zero source differences. Checker tolerance/scope failures are separately retained in history. No peer values enter this build; no later peer model/calculator equivalence is claimed. Coordinator priority acceptance remains pending; arithmetic agreement is not legal geographic approval.

## Historical conditional targets

For fixed pair volume `T=sum(A+B)` and baseline net `M=A−B`, unbounded A-share shift is `(g*T−M)/(2*T)`, where `g=0` ties and `g=0.01` means A+1 **pair margin**. Tie is `(B−A)/(2*(A+B))`; A+1 adds **0.5 A-share points**. One A-share point adds two pair-margin points and `0.02*unit_pair_votes` net votes. All-candidate margins instead divide that net by all candidate/generic marks. A+1 in the 2024 Senate pair is **44,370.26 net votes**, or **0.998086 all-candidate margin points**, not one all-candidate point. Fractional scenario votes are arithmetic expectations, not historical counts or a legal minimum vote count.

The feasible solver explicitly clips each share to[0,1] and solves a common shift with every nonpriority unit included. Unbounded values remain visible; zero-pair units have undefined preferences. [23,082 historical unit targets](data/baselines/historical-unit-targets.csv) cover every native row and every native-aggregated parent for both targets in each contest; [26,690 method target rows](data/baselines/native-method-targets.csv) retain five 2024 methods per native unit, including zero/admin groups. Every row keeps participation, pair/all weights, net contributions, one-point gains and selected-only raw requirements/statuses. The standalone single-locality requirements hold every other locality at its stated **unshifted** baseline share/volume, not its uniform target. Negative requirements mean secured under those assumptions; >1 means impossible; they are not clipped into feasibility.

| Contest / native scope | Tie unbounded share pp | Tie bounded share pp | A+1 unbounded share pp | A+1 bounded share pp |
|---|---:|---:|---:|---:|
| 2024-senate | -4.476016 | -4.476158 | -3.976016 | -3.976016 |
| 2024-president | -2.951039 | -2.951091 | -2.451039 | -2.451046 |
| 2020-senate | -6.047914 | -6.047929 | -5.547914 | -5.547928 |
| 2018-senate | -8.159950 | -8.159988 | -7.659950 | -7.659985 |

Virginia Senate uses **highest votes/plurality**, under [§24.2-673](https://law.lis.virginia.gov/vacode/title24.2/chapter6/section24.2-673/); congressional ties are determined by the State Board by lot before recount under [§24.2-674](https://law.lis.virginia.gov/vacode/title24.2/chapter6/section24.2-674/). Pair tie/A+1 scenarios do not replace the full-field legal threshold. Generic marks are not eligible named candidate allocations. A pair leader can lose to another named candidate; the calculator exposes supplied-field plurality separately. No RCV/elimination/runoff stage is invented for these contests, and no lower preference is inferred.

## All133 locality comparisons

Signed margins below are **A−B pair percentage points** for that column’s named contest. 2024 Senate A=Kaine, president A=Harris, 2020 A=Warner, 2018 A=Kaine. “Mixed” means the pair leader differs across these four elections, not a permanent classification. The last three columns are 2024 Senate parent-scope A-share percentages: illustrative uniform tie, A+1 and selected-only tie with every other parent fixed at the original 2024 baseline. Full candidate counts, other votes, denominator scopes and contributions remain in the linked CSVs. These calculations derive directly from the four official contest downloads cited above.

| Locality | 2024 Senate margin pp | 2024 president margin pp | 2020 same-seat margin pp | 2018 midterm margin pp | History | Tie share % | A+1 share % | Selected-only tie % / status |
|---|---:|---:|---:|---:|---|---:|---:|---|
| Fairfax County | +35.79 | +35.99 | +39.95 | +45.05 | A all four | 63.419 | 63.919 | 33.663 / feasible |
| Loudoun County | +17.63 | +16.79 | +23.71 | +29.01 | A all four | 54.338 | 54.838 | -28.723 / secured |
| Virginia Beach City | +5.52 | +2.69 | +7.92 | +11.03 | A all four | 48.284 | 48.784 | -35.352 / secured |
| Prince William County | +22.17 | +18.49 | +28.58 | +32.66 | A all four | 56.611 | 57.111 | -27.429 / secured |
| Chesterfield County | +10.55 | +9.11 | +7.45 | +10.11 | A all four | 50.801 | 51.301 | -39.884 / secured |
| Henrico County | +31.09 | +29.32 | +30.30 | +32.98 | A all four | 61.067 | 61.567 | -46.348 / secured |
| Arlington County | +57.39 | +59.86 | +58.92 | +68.20 | A all four | 74.219 | 74.719 | -76.470 / secured |
| Chesapeake City | +5.96 | +3.85 | +7.90 | +11.08 | A all four | 48.506 | 49.006 | -103.544 / secured |
| Richmond City | +67.50 | +67.77 | +66.73 | +72.64 | A all four | 79.273 | 79.773 | -101.735 / secured |
| Norfolk City | +44.33 | +42.18 | +48.26 | +52.84 | A all four | 67.689 | 68.189 | -161.509 / secured |
| Stafford County | +3.45 | +0.81 | +4.08 | +3.95 | A all four | 47.247 | 47.747 | -189.395 / secured |
| Alexandria City | +56.94 | +58.92 | +58.96 | +66.48 | A all four | 73.994 | 74.494 | -170.492 / secured |
| Spotsylvania County | -4.91 | -8.67 | -4.87 | -3.75 | B all four | 43.067 | 43.567 | -205.331 / secured |
| Newport News City | +32.31 | +29.22 | +35.37 | +37.54 | A all four | 61.680 | 62.180 | -199.277 / secured |
| Hanover County | -24.34 | -26.05 | -25.85 | -23.03 | B all four | 33.352 | 33.852 | -238.307 / secured |
| Albemarle County | +33.48 | +34.60 | +34.73 | +37.12 | A all four | 62.264 | 62.764 | -234.721 / secured |
| Hampton City | +43.02 | +40.45 | +44.80 | +48.99 | A all four | 67.033 | 67.533 | -249.791 / secured |
| Roanoke County | -18.79 | -22.73 | -15.17 | -17.43 | B all four | 36.130 | 36.630 | -310.361 / secured |
| Suffolk City | +19.55 | +16.10 | +18.93 | +22.99 | A all four | 55.300 | 55.800 | -316.065 / secured |
| Frederick County | -23.12 | -28.74 | -25.01 | -23.13 | B all four | 33.964 | 34.464 | -347.735 / secured |
| James City County | +5.80 | +6.29 | +4.23 | +5.75 | A all four | 48.423 | 48.923 | -336.334 / secured |
| Bedford County | -48.35 | -50.77 | -42.53 | -44.85 | B all four | 21.348 | 21.848 | -366.639 / secured |
| Rockingham County | -32.95 | -37.44 | -36.74 | -36.63 | B all four | 29.050 | 29.550 | -377.991 / secured |
| Montgomery County | +7.43 | +3.55 | +10.31 | +16.60 | A all four | 49.238 | 49.738 | -372.361 / secured |
| Fauquier County | -21.46 | -21.92 | -17.61 | -12.89 | B all four | 34.795 | 35.295 | -407.910 / secured |
| Augusta County | -43.26 | -47.97 | -41.82 | -42.33 | B all four | 23.893 | 24.393 | -421.751 / secured |
| Roanoke City | +27.76 | +23.96 | +32.32 | +31.44 | A all four | 59.406 | 59.906 | -411.720 / secured |
| Portsmouth City | +42.63 | +39.18 | +44.06 | +47.21 | A all four | 66.838 | 67.338 | -420.616 / secured |
| York County | -4.97 | -6.22 | -6.48 | -4.20 | B all four | 43.039 | 43.539 | -456.411 / secured |
| Lynchburg City | -6.73 | -8.03 | +3.85 | +5.21 | mixed | 42.157 | 42.657 | -497.512 / secured |
| Pittsylvania County | -36.70 | -43.38 | -31.29 | -35.23 | B all four | 27.174 | 27.674 | -565.685 / secured |
| Campbell County | -44.95 | -48.97 | -37.34 | -41.47 | B all four | 23.049 | 23.549 | -613.643 / secured |
| Franklin County | -40.59 | -45.69 | -32.63 | -35.95 | B all four | 25.228 | 25.728 | -617.567 / secured |
| Washington County | -43.26 | -53.66 | -45.46 | -42.26 | B all four | 23.896 | 24.396 | -653.875 / secured |
| Culpeper County | -20.82 | -25.24 | -16.72 | -14.84 | B all four | 35.116 | 35.616 | -661.785 / secured |
| Henry County | -23.36 | -33.03 | -17.28 | -23.80 | B all four | 33.842 | 34.342 | -755.804 / secured |
| Isle of Wight County | -15.83 | -19.97 | -15.94 | -10.98 | B all four | 37.609 | 38.109 | -770.027 / secured |
| Shenandoah County | -33.78 | -42.69 | -37.86 | -33.79 | B all four | 28.634 | 29.134 | -792.163 / secured |
| Louisa County | -23.49 | -26.42 | -19.96 | -15.86 | B all four | 33.780 | 34.280 | -794.457 / secured |
| Charlottesville City | +68.38 | +70.01 | +71.69 | +76.52 | A all four | 79.716 | 80.216 | -775.967 / secured |
| Gloucester County | -34.34 | -38.71 | -32.02 | -27.94 | B all four | 28.353 | 28.853 | -833.937 / secured |
| Warren County | -32.48 | -38.05 | -32.46 | -27.38 | B all four | 29.286 | 29.786 | -856.830 / secured |
| Orange County | -20.73 | -24.91 | -18.37 | -16.50 | B all four | 35.158 | 35.658 | -862.528 / secured |
| Botetourt County | -38.70 | -45.51 | -37.09 | -40.47 | B all four | 26.176 | 26.676 | -890.593 / secured |
| Powhatan County | -42.78 | -44.47 | -42.34 | -40.10 | B all four | 24.135 | 24.635 | -926.528 / secured |
| Goochland County | -18.86 | -18.80 | -19.41 | -15.71 | B all four | 36.093 | 36.593 | -972.138 / secured |
| Tazewell County | -48.01 | -69.30 | -53.89 | -57.56 | B all four | 21.521 | 22.021 | -1016.642 / secured |
| Halifax County | -16.01 | -21.20 | -8.66 | -13.44 | B all four | 37.517 | 38.017 | -1085.467 / secured |
| Caroline County | -5.55 | -8.90 | +0.54 | +4.61 | mixed | 42.750 | 43.250 | -1089.786 / secured |
| Pulaski County | -34.99 | -44.99 | -30.69 | -31.70 | B all four | 28.028 | 28.528 | -1109.018 / secured |
| Danville City | +26.85 | +21.25 | +30.41 | +26.11 | A all four | 58.950 | 59.450 | -1083.171 / secured |
| Amherst County | -32.69 | -36.77 | -25.75 | -26.28 | B all four | 29.179 | 29.679 | -1120.739 / secured |
| Prince George County | -17.36 | -21.50 | -15.51 | -12.25 | B all four | 36.842 | 37.342 | -1122.957 / secured |
| Accomack County | -9.80 | -13.42 | -5.50 | -4.82 | B all four | 40.624 | 41.124 | -1122.391 / secured |
| Harrisonburg City | +29.50 | +25.88 | +32.73 | +38.96 | A all four | 60.274 | 60.774 | -1112.639 / secured |
| Fluvanna County | -3.55 | -6.34 | -0.32 | +1.60 | mixed | 43.747 | 44.247 | -1150.124 / secured |
| New Kent County | -30.47 | -32.10 | -32.96 | -28.91 | B all four | 30.291 | 30.791 | -1176.590 / secured |
| Wise County | -44.85 | -63.62 | -49.11 | -47.29 | B all four | 23.101 | 23.601 | -1191.139 / secured |
| Carroll County | -54.41 | -63.61 | -52.75 | -53.17 | B all four | 18.319 | 18.819 | -1221.968 / secured |
| Mecklenburg County | -15.57 | -20.91 | -11.76 | -11.85 | B all four | 37.738 | 38.238 | -1209.295 / secured |
| Manassas City | +18.57 | +15.13 | +25.75 | +28.78 | A all four | 54.811 | 55.311 | -1196.655 / secured |
| Dinwiddie County | -18.25 | -23.28 | -13.25 | -7.25 | B all four | 36.400 | 36.900 | -1240.592 / secured |
| King George County | -23.63 | -25.35 | -18.57 | -16.49 | B all four | 33.709 | 34.209 | -1259.698 / secured |
| Wythe County | -50.24 | -59.91 | -45.48 | -45.41 | B all four | 20.404 | 20.904 | -1299.133 / secured |
| Smyth County | -45.37 | -60.84 | -43.19 | -43.79 | B all four | 22.837 | 23.337 | -1368.933 / secured |
| Staunton City | +16.96 | +13.57 | +13.58 | +15.82 | A all four | 54.004 | 54.504 | -1426.727 / secured |
| Fairfax City | +33.67 | +34.32 | +37.90 | +42.08 | A all four | 62.361 | 62.861 | -1427.647 / secured |
| Fredericksburg City | +34.17 | +32.33 | +35.11 | +40.08 | A all four | 62.610 | 63.110 | -1437.019 / secured |
| Russell County | -49.65 | -67.76 | -50.37 | -44.16 | B all four | 20.700 | 21.200 | -1478.132 / secured |
| Salem City | -13.06 | -19.47 | -11.89 | -15.02 | B all four | 38.992 | 39.492 | -1483.652 / secured |
| Page County | -44.22 | -54.56 | -44.79 | -42.40 | B all four | 23.415 | 23.915 | -1503.114 / secured |
| Petersburg City | +75.34 | +73.66 | +78.37 | +80.53 | A all four | 83.192 | 83.692 | -1459.438 / secured |
| Rockbridge County | -28.86 | -34.11 | -24.50 | -22.14 | B all four | 31.092 | 31.592 | -1525.155 / secured |
| Greene County | -20.65 | -25.03 | -19.05 | -19.74 | B all four | 35.200 | 35.700 | -1625.889 / secured |
| Winchester City | +16.22 | +9.91 | +15.22 | +17.81 | A all four | 53.633 | 54.133 | -1638.039 / secured |
| King William County | -35.45 | -40.91 | -34.51 | -27.53 | B all four | 27.799 | 28.299 | -1719.529 / secured |
| Waynesboro City | -0.69 | -5.77 | -0.46 | +1.80 | mixed | 45.178 | 45.678 | -1736.496 / secured |
| Scott County | -54.94 | -70.78 | -59.18 | -56.33 | B all four | 18.054 | 18.554 | -1818.082 / secured |
| Westmoreland County | -8.10 | -14.41 | -1.91 | +0.39 | mixed | 41.476 | 41.976 | -1865.704 / secured |
| Lee County | -52.74 | -72.36 | -54.47 | -50.61 | B all four | 19.156 | 19.656 | -2011.642 / secured |
| Southampton County | -19.42 | -25.69 | -14.24 | -11.89 | B all four | 35.812 | 36.312 | -2003.994 / secured |
| Clarke County | -13.50 | -17.11 | -12.54 | -9.00 | B all four | 38.776 | 39.276 | -2010.756 / secured |
| Floyd County | -30.87 | -37.64 | -26.85 | -25.53 | B all four | 30.089 | 30.589 | -2044.384 / secured |
| Appomattox County | -45.98 | -51.42 | -39.41 | -44.43 | B all four | 22.535 | 23.035 | -2066.842 / secured |
| Patrick County | -49.11 | -60.84 | -49.70 | -50.75 | B all four | 20.971 | 21.471 | -2088.240 / secured |
| Nelson County | -3.51 | -7.59 | +1.60 | +5.41 | mixed | 43.768 | 44.268 | -2071.534 / secured |
| Prince Edward County | +0.54 | -2.61 | +9.53 | +11.92 | mixed | 45.796 | 46.296 | -2112.206 / secured |
| Giles County | -42.56 | -54.88 | -39.84 | -37.70 | B all four | 24.246 | 24.746 | -2171.123 / secured |
| Buchanan County | -48.30 | -70.84 | -48.13 | -39.29 | B all four | 21.375 | 21.875 | -2176.677 / secured |
| Falls Church City | +60.00 | +63.27 | +60.07 | +68.29 | A all four | 75.522 | 76.022 | -2138.028 / secured |
| Colonial Heights City | -25.21 | -32.72 | -29.62 | -33.05 | B all four | 32.919 | 33.419 | -2241.457 / secured |
| Hopewell City | +20.15 | +13.91 | +19.37 | +14.53 | A all four | 55.598 | 56.098 | -2246.301 / secured |
| Madison County | -32.28 | -35.49 | -27.61 | -23.31 | B all four | 29.382 | 29.882 | -2334.681 / secured |
| Northumberland County | -20.32 | -21.33 | -11.96 | -15.10 | B all four | 35.365 | 35.865 | -2392.517 / secured |
| Alleghany County | -31.58 | -48.48 | -29.28 | -27.50 | B all four | 29.733 | 30.233 | -2404.420 / secured |
| Poquoson City | -43.19 | -46.48 | -43.33 | -40.53 | B all four | 23.929 | 24.429 | -2453.499 / secured |
| Grayson County | -52.40 | -62.64 | -50.85 | -50.11 | B all four | 19.323 | 19.823 | -2479.692 / secured |
| Amelia County | -41.52 | -44.58 | -34.59 | -32.72 | B all four | 24.763 | 25.263 | -2480.263 / secured |
| Buckingham County | -17.12 | -23.73 | -9.15 | -7.39 | B all four | 36.966 | 37.466 | -2497.252 / secured |
| Williamsburg City | +44.75 | +45.19 | +40.86 | +49.09 | A all four | 67.897 | 68.397 | -2478.384 / secured |
| Brunswick County | +12.37 | +8.58 | +19.38 | +21.65 | A all four | 51.709 | 52.209 | -2524.402 / secured |
| Bristol City | -28.25 | -39.93 | -27.41 | -31.88 | B all four | 31.400 | 31.900 | -2674.304 / secured |
| Lancaster County | -7.23 | -7.08 | -2.69 | -4.69 | B all four | 41.911 | 42.411 | -2692.195 / secured |
| Middlesex County | -24.80 | -27.58 | -21.10 | -19.48 | B all four | 33.125 | 33.625 | -2868.061 / secured |
| Dickenson County | -43.37 | -62.49 | -42.95 | -31.51 | B all four | 23.838 | 24.338 | -2886.731 / secured |
| Nottoway County | -17.65 | -22.52 | -10.46 | -5.90 | B all four | 36.700 | 37.200 | -2879.441 / secured |
| Northampton County | +9.50 | +6.19 | +16.37 | +15.85 | A all four | 50.276 | 50.776 | -2894.491 / secured |
| Radford City | +5.75 | +0.53 | +13.80 | +20.68 | A all four | 48.397 | 48.897 | -3014.813 / secured |
| Charlotte County | -27.96 | -32.74 | -18.05 | -19.75 | B all four | 31.546 | 32.046 | -3294.550 / secured |
| Essex County | -3.61 | -7.81 | +4.53 | +3.45 | mixed | 43.720 | 44.220 | -3300.911 / secured |
| Mathews County | -36.40 | -39.66 | -32.99 | -28.12 | B all four | 27.323 | 27.823 | -3341.770 / secured |
| Manassas Park City | +27.48 | +20.48 | +35.84 | +41.29 | A all four | 59.266 | 59.766 | -3345.734 / secured |
| Lunenburg County | -17.29 | -22.93 | -14.10 | -12.14 | B all four | 36.879 | 37.379 | -3462.562 / secured |
| Martinsville City | +28.83 | +22.90 | +35.56 | +29.70 | A all four | 59.937 | 60.437 | -3574.986 / secured |
| Cumberland County | -20.15 | -22.34 | -11.97 | -10.22 | B all four | 35.450 | 35.950 | -3624.317 / secured |
| Rappahannock County | -17.88 | -18.10 | -10.40 | -3.63 | B all four | 36.584 | 37.084 | -3930.980 / secured |
| Sussex County | +7.85 | +4.46 | +15.35 | +17.12 | A all four | 49.447 | 49.947 | -4057.069 / secured |
| Surry County | +3.05 | -0.66 | +10.94 | +16.34 | mixed | 47.048 | 47.548 | -4533.010 / secured |
| Charles City County | +14.17 | +10.86 | +22.62 | +29.19 | A all four | 52.609 | 53.109 | -4672.660 / secured |
| Greensville County | +15.43 | +9.32 | +19.70 | +21.49 | A all four | 53.240 | 53.740 | -4686.718 / secured |
| King and Queen County | -21.37 | -25.87 | -16.36 | -10.13 | B all four | 34.838 | 35.338 | -4756.677 / secured |
| Richmond County | -24.03 | -30.42 | -16.36 | -17.12 | B all four | 33.510 | 34.010 | -4791.829 / secured |
| Franklin City | +27.05 | +23.02 | +28.77 | +28.02 | A all four | 59.051 | 59.551 | -5266.640 / secured |
| Bland County | -58.49 | -70.24 | -56.72 | -58.35 | B all four | 16.279 | 16.779 | -5793.121 / secured |
| Craig County | -56.51 | -65.08 | -51.75 | -49.61 | B all four | 17.267 | 17.767 | -6413.837 / secured |
| Lexington City | +27.60 | +27.08 | +34.86 | +45.29 | A all four | 59.323 | 59.823 | -6909.586 / secured |
| Buena Vista City | -33.59 | -45.25 | -25.66 | -22.24 | B all four | 28.727 | 29.227 | -7019.425 / secured |
| Galax City | -33.38 | -44.20 | -29.25 | -31.79 | B all four | 28.832 | 29.332 | -7374.450 / secured |
| Bath County | -46.67 | -54.13 | -38.82 | -32.95 | B all four | 22.191 | 22.691 | -7716.101 / secured |
| Covington City | -16.09 | -33.50 | -9.01 | -9.87 | B all four | 37.481 | 37.981 | -8087.474 / secured |
| Emporia City | +35.54 | +31.21 | +38.88 | +31.34 | A all four | 63.292 | 63.792 | -9443.822 / secured |
| Norton City | -23.24 | -43.87 | -25.14 | -24.44 | B all four | 33.903 | 34.403 | -12539.329 / secured |
| Highland County | -34.13 | -44.94 | -33.86 | -31.74 | B all four | 28.460 | 28.960 | -13128.231 / secured |

## Historical volume/mix sensitivity

**Low/base/high are historical anchors**, not 2026 estimates: 2018 Senate 3,351,757; 2024 Senate 4,445,535; 2024 president 4,505,941 all-candidate/generic marks. Each of four historical native-aggregated parent mixes allocates the chosen statewide all-mark volume. Every parent retains its own **2024 Senate pair participation** `(A+B)/all marks`; final pair volume is the sum of those products. Four separate historical pair preference anchors (2018 Senate, 2020 Senate, 2024 Senate, 2024 president) are crossed with those volumes/mixes. Minor/generic identities and conditional within-other shares follow the stated preference anchor. Single generic-only pools are explicit category assumptions, not eligible named allocation. All 96 tie/A+1 scenarios and 12,768 parent rows are saved in [state sensitivity](data/baselines/sensitivity-state.csv), [locality sensitivity](data/baselines/sensitivity-localities.csv) and [declared settings](data/baselines/build-settings.json). None joins native precinct identities across years.

Selected rows below hold 2024 Senate preferences; all rows use the per-parent 2024 Senate participation above. They distinguish volume from composition. Uniform scaling of the same mix changes net-vote magnitudes, not its required share shift.

| Historical all-mark volume | Parent mix | Final pair votes | Baseline A−B net | Pair margin pp | Bounded tie share shift pp |
|---|---|---:|---:|---:|---:|
| low-2018-senate | 2024-senate | 3,345,341.55 | +299,476.06 | +8.952032 | -4.476016 |
| base-2024-senate | 2024-senate | 4,437,026.00 | +397,204.00 | +8.952032 | -4.476016 |
| base-2024-senate | 2024-president | 4,437,029.43 | +396,304.57 | +8.931754 | -4.465877 |
| base-2024-senate | 2020-senate | 4,436,974.09 | +426,949.70 | +9.622542 | -4.811271 |
| base-2024-senate | 2018-senate | 4,436,887.84 | +478,789.40 | +10.791109 | -5.395554 |
| high-2024-president | 2024-senate | 4,497,316.38 | +402,601.21 | +8.952032 | -4.476016 |

## Turnout and registration controls are separate

The official [annual registration/turnout summary](https://www.elections.virginia.gov/resultsreports/registrationturnout-statistics/) reports 2024 Total Voting **4,535,314**, Total Registered **6,434,637**; 2022 **3,021,956 / 6,132,331**; 2020 **4,486,821 / 5,975,696**; 2018 **3,374,382 / 5,666,962**. Annual registration includes active, inactive and overseas as defined by that page. The exact retained summary cells and offsets are in [annual controls](data/baselines/annual-controls.json); they are not contest-vote denominators.

The linked official 2024 turnout CSV has 2,669 source rows /133parents, observed TotalVoteTurnout **4,537,976** with **131 blank rows**, **2,662 above annual Total Voting**. The native API voterTurnout array has **2,536 entries**, with133native identities absent: absent values stay unknown. Its ballotsCast sum is **4,407,747**; voterTurnout sum **4,537,976**; voterRegistration **6,434,637**. Separate local-election metadata ballotsCast sums **4,526,538**; state-election ballotsCast is literal0. State API registration stock totals **6,482,067**. No difference is assigned to under/over/blank votes, and no counted percentage/registration difference becomes a remaining pool. These exact controls and null identities are retained in [turnout scopes](data/baselines/turnout-scope-controls.json), from original official report/API URLs pinned individually.

The [November1 registration publication](https://www.elections.virginia.gov/media/registration-statistics/2024/10/csv/Daily_Registrant_Count_By_Locality_2024_11_01_054233.csv) has **2,536 precinct rows /133parents**, active **5,888,756**, inactive **485,681**, AllVoters **6,374,437**. Parent/state totals repeat on each row and are counted once per scope; all133parent precinct sums close to repeated controls in [registration audit](data/baselines/registration-controls.json). Military/overseas/temp fields overlap and are not added as disjoint voters. This is a dated registration stock, not the annual/current stock or eligible remaining votes.

The official [2018](https://apps.elections.virginia.gov/SBE_CSV/ELECTIONS/ELECTIONTURNOUT/Turnout-2018%20November%20General.csv), [2020](https://apps.elections.virginia.gov/SBE_CSV/ELECTIONS/ELECTIONTURNOUT/Turnout-2020%20November%20General.csv) and [2022 administrative files](https://apps.elections.virginia.gov/SBE_CSV/ELECTIONS/ELECTIONTURNOUT/Turnout-2022%20November%20General.csv) retain every district/method/registration row. Congressional observed row sums are respectively **3,372,459 /4,477,318 /3,017,916**, below annual controls by **1,923 /9,503 /4,040**. Congressional views cover133parents; Local views cover127/132/133. Repeated source tuples (13 Congressional groups in2018;2 in2020), overlapping Local/Congressional views, blanks and repeated registration stocks prevent a disjoint ballot interpretation. [Coverage and exact missing parents](data/baselines/administrative-coverage.json) remain explicit; no deduplication, zero fill or residual allocation repairs them.

## Offline counted-plus-remainder calculator

Run from the repository root:

```sh
python3 -B senate/2026/virginia/data/baselines/calculator.py senate/2026/virginia/data/baselines/scenarios/fixtures/counted-fixed-final-denominator.input.json
python3 -B senate/2026/virginia/data/baselines/calculator.py senate/2026/virginia/data/baselines/scenarios/actual-2024-native-Aplus1.input.json
```

The first synthetic fixture fixes counted A40/B60/Other10 and supplies only100remaining candidate votes, pair participation0.8, remaining A share0.75 and Other allocation1. Final counts are A100/B80/Other30: **final pair180; final all-candidate210**. Remaining tie share is62.5%; a final A+1 pair target requires63.625%. Preferences apply only to the remainder. This is arithmetic, not a calibrated probability or a researched remaining ballot pool. For selected-only inputs, every other counted/remainder volume/preference remains explicitly supplied and fixed.

The [strict contract](data/baselines/source/SCHEMA.md) rejects invalid targets, volumes, shares, allocations, candidate collisions, global duplicate/missing/blank/nonstring unit keys, duplicate JSON fields and nonfinite tokens **before** unknown/no-pool early returns. Exact key strings remain literal. [Actual CLI evidence](data/baselines/cli-validation.json) retains successful and rejected inputs/stdout/exit/stderr, with counted-fixed/final-denominator, unknown, no-pool, negative, secured/impossible, selected unknown-other, clipping and pair-leader-loses-full-field cases. No-positive-pool and fixed-target statuses are distinct; unknown positive-pool preference is not0.5; raw negative/>1 thresholds remain visible. Supplied-universe plurality stays separate from complete-field plurality and always from a legal declaration.

## Reproduce, validate and remaining qualifications

```sh
python3 -B senate/2026/virginia/data/baselines/reproduce.py
python3 -B senate/2026/virginia/data/baselines/validate.py --sealed
```

[Validation](data/baselines/validation.json) independently checks all candidate/native/locality sums, denominator and participation settings, every target contribution/weight/gain/selected threshold, clipped roots using linear breakpoint segments, exact integer80 crossing/order, captured peer scopes, source/raw/archive hashes and links/bounds. [Asset manifest](data/baselines/asset-manifest.json) includes every owned report/CSV/script/evidence/history/proof/seal file and excludes only itself; [final seal](data/baselines/final-seal.json) avoids a reverse manifest hash cycle. Complete shared originals are referenced by immutable hash rather than duplicated. Every stored file is strictly below40,000,000bytes, with no caches/dependency directories. Exact old failing bodies distinguish encoding/blank-record/scope/tolerance checker issues from source/model changes.

Remaining external qualifications: final/current ballot amendments and feed candidate mapping; legal eligible named write-in allocation; 2018/2020 source-warning and certification chronology; incompatible administrative turnout/registration scopes; current precinct/method/geometry compatibility; actual accepted remaining pools and publication cadence; candidate effects and lower preferences; genuine historical release replay and calibration. Those are not silently neutralized. This package makes no approved November geography, exact outstanding votes, current feed acceptance, implemented collector, real2026 turnout forecast or calibrated Needle claim.
