# Alabama historical partisanship and conditional targets

Observed **2026-10-20 UTC**. Alabama Class II; all 67 counties and every labeled original reporting column remain in the calculations. The primary volume basis is **2024 president**, not a nonexistent 2024 Senate contest. Under its historical weights, Harris trails Trump by **690,204** votes in a **2,235,028-vote named pair**, within **2,265,090 reported candidate plus generic write-in marks**. The unbounded tie shift is **+15.440612 A-share percentage points**. A feasible common shift with every native share clipped to [0,1] is **+15.936896 points**; the illustrative A+1 pair-margin target needs **+16.470824 points**, producing **22,350.28 expected net votes**. Fractional scenario counts are arithmetic expectations. These are historical conditional paths, not 2026 projections, probabilities or legal election calls. [2024 certified canvass, PDF pp. 5–6](https://www.sos.alabama.gov/sites/default/files/election-2024/State%20Certification%20of%202024%20General%20Election.pdf); [official native XLS archive](https://www.sos.alabama.gov/sites/default/files/election-data/2024-12/2024-General%20Precinct%20Level%20Results.zip).

## Complete primary evidence and identities

The [SOS data authority page](https://www.sos.alabama.gov/alabama-votes/voter/election-data) links the [2024](https://www.sos.alabama.gov/sites/default/files/election-data/2024-12/2024-General%20Precinct%20Level%20Results.zip), [2022](https://www.sos.alabama.gov/sites/default/files/election-data/2022-11/2022%20General%20Precinct%20Level%20Results.zip) and [2020](https://www.sos.alabama.gov/sites/default/files/election-data/2020-12/2020%20General%20Precinct%20Results.zip) original ZIPs. Each contains 67 XLS workbooks; every ZIP CRC, member hash and selected typed cell was independently extracted before reading peer derivatives. These are official SOS historical archives; an explicit within-workbook certification stamp/date is not supplied. County/state candidate aggregates independently agree with the separately certified canvasses. The [original-first witness](data/baselines/source/original-first-witness.json), [original references](data/baselines/source/original-references.json), [typed source](data/baselines/source/typed-workbooks.json.gz), and [schema](data/baselines/source/SCHEMA.md) preserve literal headers, all row descriptors, selected contest/admin rows, types, blanks, formulas and source positions. Entire original workbook bytes retain all other offices. Original large PDFs/ZIPs are stored once by exact hash in read-only shared evidence; ordered gzip reconstruction and complete receipts are pinned. No source candidate key is deduplicated or residual assigned.

The tables below use the named Democratic candidate as A and named Republican as B **only for the specified historical contest**. Independent ballot identities remain IND in the 2024 workbook, including Oliver and Stein; this does not convert them into Democrats or silently replace the ballot label with a national affiliation. Sophocleus is LIB in 2022. Generic Write-In is an unresolved mark category, not an identified eligible candidate. [2024 canvass](https://www.sos.alabama.gov/sites/default/files/election-2024/State%20Certification%20of%202024%20General%20Election.pdf); [2022 canvass, PDF pp. 4–5](https://www.sos.alabama.gov/sites/default/files/election-data/2022-11/Final%20Canvass%20of%20Results%20%28canvassed%20by%20state%20canvassing%20board%2011-28-2022%29.pdf); [2020 canvass, PDF pp. 3–4](https://www.sos.alabama.gov/sites/default/files/election-2020/Final%20Canvass%20of%20Results-Merged.pdf).

| Historical contest / stage | A (D) | B (R) | Other named / generic | Pair votes | Full reported marks | A pair share % | A−B pair margin pp |
|---|---:|---:|---|---:|---:|---:|---:|
| 2024 president; general | Kamala D. Harris 772,412 | Donald J. Trump 1,462,616 | Robert F. Kennedy Jr. 12,075; Chase Oliver 4,930; Jill Stein 4,319; Write-In 8,738 | 2,235,028 | 2,265,090 | 34.559388 | -30.881224 |
| 2022 Senate Class III; general/midterm | Will Boyd 436,746 | Katie Britt 942,154 | John Sophocleus 32,879; Write-In 2,459 | 1,378,900 | 1,414,238 | 31.673508 | -36.652984 |
| 2020 Senate Class II; general | Doug Jones 920,478 | Tommy Tuberville 1,392,076 | Write-In 3,891 | 2,312,554 | 2,316,445 | 39.803525 | -20.392951 |

These are three distinct general electorates, with no RCV rounds or general-election runoff stages combined. The 2020 Jones–Tuberville comparison is the same Class II seat; 2022 Boyd–Britt–Sophocleus is the other Class III seat and a midterm anchor. All named and known generic county/native sums equal their respective primary statewide controls. The [canvass cells](data/baselines/source/canvass-county-cells.json) preserve the 2024 Wilcox Stein **blank**, 2022 Washington Write-In **blank**, and 2020 Perry Write-In **dash** as null. The XLS archives independently report numeric zero for those scopes; both observations survive in the [disagreement table](data/baselines/source/canvass-xls-disagreements.json). Known PDF column sums agreeing with statewide controls do not make a blank/dash known zero. The 2024 Hale/Winston OCR and detached 2022 Henry label were independently read from complete retained [page images](data/baselines/source/visual-2024-005.png), [2024 second page](data/baselines/source/visual-2024-006.png), [2022 page](data/baselines/source/visual-2022-005.png), and [2020 page](data/baselines/source/visual-2020-004.png).

An initial **own parser error**, now corrected, grouped statewide minor-candidate sums by county row ordinal. Jefferson's original row 12 is Stein and row 13 Oliver, unlike Autauga. That created an erroneous 263-vote candidate offset, not a publication disagreement. The [exact old bodies/scripts](data/baselines/history/before-label-aggregation-correction.tar.gz), [original Jefferson reread](data/baselines/history/jefferson-label-order-independent-reread.json) and an actual literal-label regression survive. Current builds use candidate labels for every county and native unit; no root/peer values supply calculations. Separate earlier adapter failures and a floating-point checker error are retained in [history notes](data/baselines/history/repairs.md).

## Native coverage, administrative controls and exact priority

Native means a literal **historical workbook reporting column**, including ABSENTEE, PROVISIONAL, misspelled PROVSIONAL, combined/central groups, and named local columns. It is not proof of a polygon, polling site, split ballot style, exclusive method or current precinct ID. Bessemer and Birmingham absentee columns remain separate. Every administrative row and every source-native candidate row survives with its county/sheet/row/column. Parent FIPS comes from the original ZIP member identity and [Census county codes](https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt), with the explicit StClair → St. Clair county spelling mapping only. No cross-year native or November 2026 geometry join is asserted.

Sort is reported complete candidate-plus-generic marks descending, then the **complete exact source key ascending**. The [full independent inventory](data/baselines/source/independent-inventory.json) contains every order, cumulative integer count, priority and remainder array for all three years and both geographic levels. [All 67 parents](data/baselines/all67-parent-contract.json) contain complete constituent/priority/remainder arrays.

| Year | Native units | Minimum native 80% | Native top 15 share % | County minimum 80% | County top 15 share % |
|---|---:|---:|---:|---:|---:|
| 2024 | 2,085 | 887 | 5.095956 | 25 | 65.771779 |
| 2022 | 2,074 | 893 | 4.259679 | 27 | 65.030426 |
| 2020 | 2,111 | 874 | 9.785426 | 26 | 65.694674 |

For 2024 the threshold is the integer **1,812,072** marks. The first 886 units supply **1,811,981**; adding Calhoun `col030:OAK GROVE BAPT` (837) yields **887 units / 1,812,818 / 80.032934674%**. The 1,198 remaining units contribute **452,272**, and remain in every state target. The native priority spans 63 county parents; all 67 remain inventoried. The separate county sensitivity reaches 80% with 25 counties / 1,814,804 marks. This historical ranking does not establish eligible-write-in robustness, legal geographic approval or coordinator acceptance. [Official 2024 native archive](https://www.sos.alabama.gov/sites/default/files/election-data/2024-12/2024-General%20Precinct%20Level%20Results.zip).

The actual finished turnout peer `5b42c895-68ea-40c4-9b7c-534e46d14d7a` was captured read-only **after** the initial independent witness: [complete nonoriginal bodies](data/baselines/source/frozen-turnout-peer.tar.gz), [individual immutable original references](data/baselines/source/frozen-peer-original-references.json). Its manifest pin is `4e2a1f5ab3c66508444c112f9e6430006dce94f795a172837c7b95eaee557207`. Comparison finds **610,064 typed required cells**, candidate/admin fields, member identities, all three complete native orders and the exact 2024 full/887-priority/1,198-remainder arrays equal. Independent validation additionally compares every parent array and all 1,020 published ballot/registration numeric controls. [Reciprocal evidence](data/baselines/peer-reconciliation.json) records historical equality only; peer model/report/future/legal acceptance is not inferred. No finished peer was contacted or restarted.

Published turnout controls differ from contest marks:

| General election | Registered voters (printed scope) | Ballots cast | Candidate/generic contest marks |
|---|---:|---:|---:|
| 2024 | 3,861,929 | 2,272,911 | 2,265,090 |
| 2022 | 3,687,753 | 1,423,409 | 1,414,238 |
| 2020 | 3,708,804 | 2,329,114 | 2,316,445 |

Sources: [2024 total-ballot report](https://www.sos.alabama.gov/sites/default/files/election-data/2025-01/2024GeneralElectionTotalBallotsCast.pdf), [2022 report](https://www.sos.alabama.gov/sites/default/files/election-data/2023-05/General%20Election%202022%20Official%20Total%20Ballots%20Cast.pdf), [2020 report](https://www.sos.alabama.gov/sites/default/files/election-2020/2020_General_Total_Ballots_Cast_Report.pdf). Their registration active/inactive scope and extract/as-of date are unspecified; election date is not assumed to be registration extract date. Party/straight-party columns are preserved separately from candidate votes. Native registered-voter zeros, blanks and incompleteness are not usable complete registration coverage. Native ballot sums differ from the published county controls in **Cleburne 2024 −180** and **Cullman 2022 +90**, retained unallocated. Walker 2024 lacks contest under/over rows across 47 columns; Butler/Dale/Tuscaloosa 2022 lack them across 23/20/56; Randolph 2020 lacks blank-ballot rows across 28. Multiple other ballots−contest−over−under residuals and literal admin differences remain in the complete [administrative reconciliation](data/baselines/administrative-reconciliation.json). They are source controls, not repaired candidate votes or inferred remaining ballots.

## Historical volume, mix, preference and bounded paths

Low/base/high **observed contest-volume anchors** are 2022 Senate **1,414,238**, 2024 president **2,265,090**, and 2020 Senate **2,316,445**. They are historical sensitivities, not a researched 2026 turnout interval. The [implemented settings](data/baselines/scenario-settings.json) state the full-vote volume basis, source-year mix, named preference pair and pair participation. Every original-year native scenario uses its own units, own candidate preferences and own volumes. Scale-only native sensitivities retain 2024 units/preferences/participation/mix and multiply all volumes by the historical statewide full-total ratio. Separate county composition sensitivities retain 2024 county preferences and pair participation but use each 2022/2020 county's actual full-contest volume. Only county FIPS is joined for those parent sensitivities. No 2020/2022 native shares are assigned to 2024 precinct names. [Original authority](https://www.sos.alabama.gov/alabama-votes/voter/election-data).

| Implemented scenario | Pair volume | Full volume | Baseline A−B margin pp | Unbounded tie share pp | Bounded tie share pp | Bounded A+1 share pp |
|---|---:|---:|---:|---:|---:|---:|
| `native-2024-own-history` | 2,235,028.000 | 2,265,090 | -30.881224 | +15.440612 | +15.936896 | +16.470824 |
| `native-2022-own-history` | 1,378,900.000 | 1,414,238 | -36.652984 | +18.326492 | +19.181565 | +19.724641 |
| `native-2020-own-history` | 2,312,554.000 | 2,316,445 | -20.392951 | +10.196475 | +10.517358 | +11.044793 |
| `county-2024-own-history` | 2,235,028.000 | 2,265,090 | -30.881224 | +15.440612 | +15.440612 | +15.940612 |
| `county-2022-own-history` | 1,378,900.000 | 1,414,238 | -36.652984 | +18.326492 | +18.326492 | +18.826492 |
| `county-2020-own-history` | 2,312,554.000 | 2,316,445 | -20.392951 | +10.196475 | +10.196475 | +10.696475 |
| `native-2024-mix-scaled-to-2022-total` | 1,395,468.405 | 1,414,238 | -30.881224 | +15.440612 | +15.936896 | +16.470824 |
| `native-2024-mix-scaled-to-2020-total` | 2,285,701.423 | 2,316,445 | -30.881224 | +15.440612 | +15.936896 | +16.470824 |
| `county-2024-preferences-2022-mix-volume` | 1,395,548.938 | 1,414,238 | -29.987716 | +14.993858 | +14.993858 | +15.493858 |
| `county-2024-preferences-2020-mix-volume` | 2,285,732.240 | 2,316,445 | -29.669574 | +14.834787 | +14.834787 | +15.334787 |

For fixed pair weights, `δ_tie=(B−A)/(2(A+B))`; an illustrative A+1 **pair margin** adds **0.5 A-share points** to that unbounded shift. One A-share point transfers one point from B to A, adding **two margin points**, or `0.02 × pair votes` net. The native solver instead finds the feasible root of `Σ Tᵤ[2 clip(sᵤ+δ,0,1)−1]=gΣTᵤ`; clipping can change the additional shift needed for A+1. County homogeneous-share benchmarks have different clipping behavior and are shown separately. Target net votes and full-candidate margins are distinct: the 2024 A+1 pair net 22,350.28 is **0.986728121% of full reported marks**, not one full-field percentage point. The calculator supplies target candidate totals, full denominator and A's gap to the highest other named candidate. A pair tie/cushion can still lose to a third candidate; generic/unallocated choices prevent a full legal declaration.

Complete [native baselines](data/baselines/native-baselines.json.gz), [county CSV](data/county-baselines.csv), [scenario input/results](data/baselines/state-scenarios.json), and [all-parent native contributions](data/baselines/parent-native-contributions.json) retain every unit, weight, participation, baseline/target net, gain, clipping and selected-only raw threshold. No nonpriority unit disappears.

## All 67 county comparisons and primary-native contributions

Margins below are A−B percentage points in each named historical pair. Weight and +1-share-point net gain use 2024 pair votes. Target share is the **county aggregate of the clipped primary native A+1 scenario**, not an identical county shift. The final column solves only that county for a statewide pair tie while every other original 2024 unit is fixed at its actual baseline; values above 100% are impossible under those assumptions. County identities are election outcomes, not permanent partisan labels. Every table value derives from the [official 2024](https://www.sos.alabama.gov/sites/default/files/election-data/2024-12/2024-General%20Precinct%20Level%20Results.zip), [2022](https://www.sos.alabama.gov/sites/default/files/election-data/2022-11/2022%20General%20Precinct%20Level%20Results.zip) and [2020](https://www.sos.alabama.gov/sites/default/files/election-data/2020-12/2020%20General%20Precinct%20Results.zip) workbooks, reconciled to the canvasses above.

| County / FIPS | 2024 pair votes | 2024 margin pp | 2020 margin pp | 2022 margin pp | 2024 pair weight % | +1 share pp net votes | Native A+1 target share % | Selected-only tie share % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Autauga / 01001 | 27,923 | -46.72 | -40.16 | -55.58 | 1.2493 | 558.46 | 43.112 | 1262.547 |
| Baldwin / 01003 | 120,732 | -58.70 | -46.99 | -67.66 | 5.4018 | 2,414.64 | 37.123 | 306.494 |
| Barbour / 01005 | 9,764 | -14.83 | -4.09 | -19.15 | 0.4369 | 195.28 | 59.056 | 3577.018 |
| Bibb / 01007 | 9,191 | -64.77 | -53.07 | -65.72 | 0.4112 | 183.82 | 34.086 | 3772.397 |
| Blount / 01009 | 27,930 | -81.55 | -76.03 | -85.90 | 1.2496 | 558.60 | 25.694 | 1244.819 |
| Bullock / 01011 | 4,084 | +46.08 | +51.81 | +39.89 | 0.1827 | 81.68 | 87.770 | 8523.139 |
| Butler / 01013 | 8,423 | -22.81 | -11.02 | -30.03 | 0.3769 | 168.46 | 55.068 | 4135.735 |
| Calhoun / 01015 | 48,106 | -45.15 | -33.75 | -49.85 | 2.1524 | 962.12 | 43.668 | 744.805 |
| Chambers / 01017 | 14,116 | -23.42 | -9.22 | -32.76 | 0.6316 | 282.32 | 54.761 | 2483.048 |
| Cherokee / 01019 | 12,911 | -75.94 | -65.47 | -80.25 | 0.5777 | 258.22 | 28.499 | 2684.959 |
| Chilton / 01021 | 19,618 | -72.49 | -63.57 | -76.14 | 0.8778 | 392.36 | 30.223 | 1772.862 |
| Choctaw / 01023 | 6,618 | -24.00 | -12.99 | -25.49 | 0.2961 | 132.36 | 54.073 | 5252.599 |
| Clarke / 01025 | 11,892 | -17.14 | -7.98 | -19.36 | 0.5321 | 237.84 | 57.790 | 2943.399 |
| Clay / 01027 | 6,727 | -70.48 | -58.20 | -75.56 | 0.3010 | 134.54 | 31.232 | 5144.864 |
| Cleburne / 01029 | 7,593 | -84.06 | -76.47 | -86.37 | 0.3397 | 151.86 | 24.439 | 4552.970 |
| Coffee / 01031 | 22,096 | -58.35 | -48.06 | -66.47 | 0.9886 | 441.92 | 37.294 | 1582.653 |
| Colbert / 01033 | 26,851 | -46.84 | -32.14 | -50.61 | 1.2014 | 537.02 | 43.051 | 1311.828 |
| Conecuh / 01035 | 6,003 | -14.04 | -3.07 | -16.70 | 0.2686 | 120.06 | 59.402 | 5791.804 |
| Coosa / 01037 | 5,236 | -43.54 | -30.41 | -43.74 | 0.2343 | 104.72 | 44.584 | 6619.175 |
| Covington / 01039 | 16,991 | -72.76 | -62.92 | -76.86 | 0.7602 | 339.82 | 30.090 | 2044.706 |
| Crenshaw / 01041 | 6,457 | -54.87 | -41.95 | -60.24 | 0.2889 | 129.14 | 39.035 | 5367.183 |
| Cullman / 01043 | 42,743 | -81.10 | -72.66 | -84.50 | 1.9124 | 854.86 | 25.920 | 816.838 |
| Dale / 01045 | 18,960 | -52.70 | -39.26 | -60.52 | 0.8483 | 379.20 | 40.121 | 1843.808 |
| Dallas / 01047 | 15,426 | +32.71 | +40.48 | +30.57 | 0.6902 | 308.52 | 79.840 | 2303.501 |
| DeKalb / 01049 | 29,391 | -74.43 | -64.01 | -80.11 | 1.3150 | 587.82 | 29.257 | 1186.962 |
| Elmore / 01051 | 41,148 | -52.49 | -44.20 | -61.12 | 1.8411 | 822.96 | 40.217 | 862.438 |
| Escambia / 01053 | 14,848 | -46.61 | -31.72 | -52.85 | 0.6643 | 296.96 | 42.748 | 2350.929 |
| Etowah / 01055 | 45,680 | -56.10 | -44.65 | -61.41 | 2.0438 | 913.60 | 38.331 | 777.428 |
| Fayette / 01057 | 8,300 | -72.48 | -62.22 | -74.38 | 0.3714 | 166.00 | 30.230 | 4171.614 |
| Franklin / 01059 | 11,985 | -73.83 | -58.19 | -78.95 | 0.5362 | 239.70 | 29.554 | 2892.532 |
| Geneva / 01061 | 12,320 | -77.42 | -66.06 | -80.62 | 0.5512 | 246.40 | 27.761 | 2812.443 |
| Greene / 01063 | 4,018 | +55.95 | +65.84 | +59.30 | 0.1798 | 80.36 | 92.767 | 8666.874 |
| Hale / 01065 | 7,237 | +6.90 | +21.53 | +9.67 | 0.3238 | 144.74 | 69.918 | 4822.026 |
| Henry / 01067 | 9,252 | -51.08 | -38.04 | -53.05 | 0.4140 | 185.04 | 40.930 | 3754.486 |
| Houston / 01069 | 43,821 | -48.19 | -36.92 | -56.80 | 1.9606 | 876.42 | 42.300 | 813.432 |
| Jackson / 01071 | 23,349 | -71.94 | -60.92 | -76.89 | 1.0447 | 466.98 | 30.500 | 1492.047 |
| Jefferson / 01073 | 293,235 | +10.57 | +17.33 | +4.67 | 13.1200 | 5,864.70 | 69.822 | 172.972 |
| Lamar / 01075 | 6,839 | -76.43 | -70.08 | -79.29 | 0.3060 | 136.78 | 28.256 | 5057.874 |
| Lauderdale / 01077 | 43,034 | -52.01 | -36.86 | -56.97 | 1.9254 | 860.68 | 40.461 | 825.924 |
| Lawrence / 01079 | 16,007 | -62.73 | -47.10 | -63.47 | 0.7162 | 320.14 | 34.915 | 2174.580 |
| Lee / 01081 | 71,818 | -28.16 | -15.70 | -36.80 | 3.2133 | 1,436.36 | 52.382 | 516.444 |
| Limestone / 01083 | 52,468 | -44.42 | -36.32 | -53.79 | 2.3475 | 1,049.36 | 44.261 | 685.528 |
| Lowndes / 01085 | 5,625 | +37.49 | +48.19 | +36.33 | 0.2517 | 112.50 | 83.258 | 6203.893 |
| Macon / 01087 | 7,766 | +56.68 | +65.97 | +56.36 | 0.3475 | 155.32 | 89.491 | 4522.096 |
| Madison / 01089 | 193,254 | -9.11 | -2.44 | -21.11 | 8.6466 | 3,865.08 | 61.679 | 224.019 |
| Marengo / 01091 | 9,626 | -3.78 | +4.80 | -6.02 | 0.4307 | 192.52 | 64.457 | 3633.212 |
| Marion / 01093 | 13,442 | -82.19 | -73.12 | -85.63 | 0.6014 | 268.84 | 25.376 | 2576.246 |
| Marshall / 01095 | 39,987 | -72.23 | -62.78 | -79.21 | 1.7891 | 799.74 | 30.358 | 876.922 |
| Mobile / 01097 | 172,814 | -16.61 | -5.64 | -23.04 | 7.7321 | 3,456.28 | 57.263 | 241.391 |
| Monroe / 01099 | 9,747 | -23.26 | -11.17 | -22.91 | 0.4361 | 194.94 | 54.173 | 3578.968 |
| Montgomery / 01101 | 88,423 | +31.07 | +34.78 | +19.40 | 3.9562 | 1,768.46 | 79.999 | 455.818 |
| Morgan / 01103 | 52,841 | -53.10 | -43.40 | -62.30 | 2.3642 | 1,056.82 | 39.806 | 676.547 |
| Perry / 01105 | 4,443 | +42.88 | +51.16 | +42.47 | 0.1988 | 88.86 | 84.854 | 7838.758 |
| Pickens / 01107 | 8,853 | -23.46 | -12.94 | -30.54 | 0.3961 | 177.06 | 54.740 | 3936.406 |
| Pike / 01109 | 13,123 | -25.34 | -12.73 | -33.64 | 0.5872 | 262.46 | 53.802 | 2667.081 |
| Randolph / 01111 | 11,022 | -65.16 | -56.10 | -69.33 | 0.4931 | 220.44 | 33.891 | 3148.449 |
| Russell / 01113 | 20,500 | +1.68 | +11.63 | -5.01 | 0.9172 | 410.00 | 67.000 | 1734.263 |
| StClair / 01115 | 43,141 | -64.58 | -60.05 | -70.85 | 1.9302 | 862.82 | 34.180 | 817.649 |
| Shelby / 01117 | 112,753 | -41.31 | -36.03 | -51.44 | 5.0448 | 2,255.06 | 45.815 | 335.414 |
| Sumter / 01119 | 5,267 | +41.45 | +50.44 | +39.54 | 0.2357 | 105.34 | 86.666 | 6622.878 |
| Talladega / 01121 | 32,998 | -33.95 | -22.12 | -34.87 | 1.4764 | 659.96 | 49.497 | 1078.853 |
| Tallapoosa / 01123 | 19,859 | -49.90 | -40.21 | -56.30 | 0.8885 | 397.18 | 41.497 | 1762.813 |
| Tuscaloosa / 01125 | 84,123 | -20.59 | -9.96 | -26.33 | 3.7638 | 1,682.46 | 55.670 | 449.938 |
| Walker / 01127 | 29,566 | -72.25 | -61.42 | -75.90 | 1.3228 | 591.32 | 30.345 | 1181.100 |
| Washington / 01129 | 8,397 | -55.63 | -40.09 | -56.49 | 0.3757 | 167.94 | 38.589 | 4132.011 |
| Wilcox / 01131 | 5,242 | +31.59 | +39.43 | +29.59 | 0.2345 | 104.84 | 79.774 | 6649.199 |
| Winston / 01133 | 11,075 | -84.04 | -76.79 | -87.99 | 0.4955 | 221.50 | 24.453 | 3124.027 |

Harris leads in 12 county pairs in 2024; Boyd in 11 in 2022; Jones in 13 in 2020. Exact names, complete candidates, all-candidate denominators and closeness bands (absolute pair margin ≤5 pp, >5–10 pp, >10 pp) are in the CSV. Holding every other 2024 unit unchanged, **no single county can erase the statewide deficit** even at 100% of that county's fixed pair pool: all 67 selected-only raw tie shares exceed 100%. The illustrated path therefore requires gains across multiple counties under these fixed weights. County gains trade off across the whole state; no displayed county target is independently necessary for a win.

## Current named ballot mapping and legal limits

The current [2026 SOS authority page](https://www.sos.alabama.gov/alabama-votes/voter/election-information/2026) links **signed August 26 general-election state certifications**. Independently viewed [Democratic certification, PDF pp. 1–3](https://www.sos.alabama.gov/sites/default/files/election-2026/2026GeneralElectionStateCertificationofDemocraticCandidates.pdf) names **Everett Wess** for United States Senator; the [Republican state certification, PDF pp. 1–2](https://www.sos.alabama.gov/sites/default/files/election-2026/2026GeneralElectionStateCertificationofRepublicanCandidates.pdf) names **Barry Moore**. The linked [independent certification](https://www.sos.alabama.gov/sites/default/files/election-2026/2026GeneralElection-StateCertificationofIndependentCandidate.pdf) lists state legislative candidates, without a U.S. Senate candidate. The bounded [Autauga November specimen](https://www.sos.alabama.gov/sites/default/files/sample-ballots/2026/gen/Autauga-Sample.pdf) displays Wess (Democrat), Moore (Republican) and a write-in line. This mapping comes from final general publications, not old Senate candidates, primary winner inference or newsroom IDs. Fresh complete receipts and retained visual evidence are in [current source evidence](data/baselines/source/current-ballot-evidence.json).

The authority also links [August 28](https://www.sos.alabama.gov/sites/default/files/election-2026/Amended_2026_Republican_Certification.pdf) and [September 2](https://www.sos.alabama.gov/sites/default/files/election-2026/ALGOPAmendedCertification-SD25.pdf) amendments. Their retained complete originals concern omitted HD51 and SD25 certification; the attached lists continue Moore. The September 2 SOS cover distinguishes accepting an amendment from reprinting ballots. This bounded check does not exhaust later orders, all 67 final specimens, eligible write-ins or current geography. The original [2026 Voter Guide](https://www.sos.alabama.gov/sites/default/files/election-2026/2026-VoterGuide.pdf) distinguishes primary/runoff/general electorates. Primary majority/runoff rules do not become the general pair-margin target. The official [§17-12-21](https://alison.legislature.state.al.us/code-of-alabama?section=17-12-21) and [§17-12-23](https://alison.legislature.state.al.us/code-of-alabama?section=17-12-23) requests returned application shells in this environment; current operative text/tie treatment is a precise legal-verification gap. The tool computes mathematical full-field plurality comparisons and always leaves legal outcome declaration false. No historical candidate effect, transfer/lower preference, current write-in allocation or remaining-ballot inventory is inferred.

## Offline calculator and reproduction

`calculate.py` accepts a complete named candidate list, named pair, globally unique literal unit keys, fractional target in [−1,1], stated scope and assumptions. Historical units contain complete vote vectors and optional full-contest volume. Live units contain counted vectors, a stated full remaining pool, pair participation, remaining A share (null means unknown), and balanced allocations over every other supplied identity. Every count remains fixed. Preferences apply only to uncounted votes. `final_pair=counted A+B + remaining×pair participation`; `final_full=all counted + all remaining`. The selected-only solve holds every other explicit input fixed. Negative/>1 raw shares remain secured/impossible; zero pool and fixed-target status remain separate. Unknown positive pools remain unknown. Duplicate candidate/object fields or unit keys, blank/missing/nonstring keys, invalid/nonfinite/bool counts/shares/targets, unsupported settings, allocation imbalance and numeric overflow fail as strict JSON with exit 2 and empty stderr, before early returns.

```sh
# Repository root. Use an external temporary environment; no dependencies/cache in owned paths.
python3 -m pip install --no-cache-dir --target /private/tmp/al-baseline-deps xlrd==2.0.2
export PYTHONPATH=/private/tmp/al-baseline-deps
export PYTHONDONTWRITEBYTECODE=1
python3 senate/2026/alabama/data/baselines/extract_originals.py
python3 senate/2026/alabama/data/baselines/source_controls.py
python3 senate/2026/alabama/data/baselines/compare_peer.py
python3 senate/2026/alabama/data/baselines/build.py
python3 senate/2026/alabama/data/baselines/render_report.py
python3 senate/2026/alabama/data/baselines/verify_cli.py
python3 senate/2026/alabama/data/baselines/validate.py
python3 senate/2026/alabama/data/baselines/calculate.py \
  senate/2026/alabama/data/baselines/scenarios/cli/counted-fixed-final-denominator.input.txt
gzip -dc senate/2026/alabama/data/baselines/scenarios/native-2024-own-history-tie.input.json.gz | \
  python3 senate/2026/alabama/data/baselines/calculate.py
```

`acquire.py` is the optional online bounded-publication recheck, with immutable fresh receipts; historical calculations are fully offline from pinned originals. Regenerating owned outputs intentionally invalidates the publication manifest until resealed. Current validation runs the actual CLI for 71 saved real/synthetic cases and independently solves all 20 historical roots with exact rational, piecewise breakpoint algebra, checking every contribution, selected-only threshold, weight, balance and target residual. Synthetic cases include unknown/no-pool/negative/secured/impossible/clipping, zero-pair undefined preference, a pair leader losing the full field, invalid global identities in early-return branches and nonfinite JSON tokens. They are arithmetic tests, not calibrated probabilities. See [CLI results](data/baselines/cli-validation.json), [independent validation](data/baselines/validation.json), [final seal](data/baselines/final-seal.json) and [complete owned assets](data/baselines/asset-manifest.json).

Historical source coverage and deterministic calculations are complete within the published scopes. Coordinator acceptance, current legal/geographic approval, eligible named-write-in allocation and priority robustness, November live candidate/feed IDs, release cadence, remaining-vote estimates, collector implementation and probability calibration remain false/unknown. County controls do not substitute for missing finer data. The package supplies no 2026 turnout forecast or election call.
