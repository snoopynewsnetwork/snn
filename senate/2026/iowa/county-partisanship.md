# Iowa county partisanship and conditional targets

Research snapshot: 2026-10-18 UTC (work began 2026-10-17 America/Chicago). **All 99 counties and all three historical contests reconcile to original SOS canvass controls.** Repeating the 2020 same-seat Senate result at its actual D+R weights leaves D behind by 110,138 votes: a uniform **+3.399623 D-share points** ties, and **+3.899623 share points** yields illustrative **D+1 pair-margin**. At actual 2024 county all-candidate volumes with each county's 2020 pair participation and preferences, the corresponding shifts are **+3.347015** and **+3.847015** points. County gains can offset one another; these are conditional combinations, not necessary improvements in every county. [Original 2020 canvass](https://sos.iowa.gov/elections/pdf/2020/general/canvsummary.pdf), [2024 canvass](https://sos.iowa.gov/elections/pdf/2024/general/canvsummary.pdf).

The 2020 Ernst–Greenfield contest is the same Class II seat as 2026; 2022 Grassley–Franken is the other Class III seat and midterm comparator. **Iowa had no 2024 Senate election**; the 2024 baseline and priority basis here are president. Historical D/R labels describe these numerical observations. The actual November 2026 roster, candidate IDs and reporting geography are not inferred from these archives or the June 2026 primary. [Iowa race seat reference](README.md), [SOS results index](https://sos.iowa.gov/iowans/election-results-statistics).

## Original evidence, candidate universe and controls

The [SOS index](https://sos.iowa.gov/iowans/election-results-statistics) actually links the [2024](https://sos.iowa.gov/elections/pdf/2024/general/canvsummary.pdf), [2022](https://sos.iowa.gov/elections/pdf/2022/general/canvsummary.pdf) and [2020](https://sos.iowa.gov/elections/pdf/2020/general/canvsummary.pdf) original PDFs. Each county's Election Day plus Absentee equals Total for every candidate and metric. Independent county sums reproduce every published state column, including generic Write-in and under/over. The 2020 PDF provides only a statewide Total footer: its statewide method sums are county-derived, not independently printed state method controls. Dates printed on the 2024 and 2020 canvass covers are 12/02/2024 and 11/30/2020; no explicit 2022 canvass date was located. Transport Last-Modified is retained separately. See [source references](data/baselines/sources.json), [full header evidence](data/baselines/candidate-headers.json), [7,484 candidate/metric cells](data/baselines/canvass-candidate-method.csv) and [state checks](data/baselines/state-controls.csv).

| Contest | D | R | Named nonmajor | Generic Write-in | Candidate + generic | Under | Over | Reported Total | D counties |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2020-senate | 754,859 | 864,997 | 50,761 | 1,211 | 1,671,828 | 27,438 | 864 | 1,700,130 | 8 |
| 2022-senate | 533,330 | 681,501 | 0 | 1,815 | 1,216,646 | 13,448 | 322 | 1,230,416 | 5 |
| 2024-president | 707,278 | 927,019 | 22,552 | 6,657 | 1,663,506 | 8,586 | 1,919 | 1,674,011 | 5 |

All 2020 candidates are retained separately: Joni Ernst (REP), Theresa Greenfield (DEM), Rick Stewart (LIB), Suzanne Herzog (no party printed), and generic Write-in. 2022 prints Chuck Grassley (REP), Michael Franken (DEM), Write-in. 2024 prints Harris/Walz (DEM), Trump/Vance (REP), Oliver/ter Maat (LIB), Ayyadurai/Ellis (no party printed), De la Cruz/Garcia (PSL), Stodden/Cholensky (SOC), Kennedy/Shanahan (WTP), Write-in. Full names remain in the CSV. Generic marks are not identified as individually named or valid write-ins. No named opposition or other candidate becomes a Democratic vote. [2020 original](https://sos.iowa.gov/elections/pdf/2020/general/canvsummary.pdf), [2022 original](https://sos.iowa.gov/elections/pdf/2022/general/canvsummary.pdf), [2024 original](https://sos.iowa.gov/elections/pdf/2024/general/canvsummary.pdf).

The 2024 source candidate-plus-generic denominator is **1,663,506**, including **6,657** generic marks; named columns alone are **1,656,849**. The source does not resolve a separately named-valid write-in universe. Reported Total **1,674,011** also includes 8,586 under and 1,919 over and is not the ranking denominator. The exact minimum 80% county set is **41**: first 40 supply **1,322,507**, then Henry (`19087`) contributes **9,600** for **1,332,107**. Top 15 supply **991,869**. All integers and full 99-row order independently match the turnout worker; the [coordinator accepted county priority](data/coordinator-baseline-reconciliation.json). That acceptance does not approve historical/current finer geography. [Full order](data/baselines/priority-order.csv), [exact calculation](data/baselines/priority.json), [independent peer checks](data/baselines/peer-reconciliation.json), [primary 2024 source](https://sos.iowa.gov/elections/pdf/2024/general/canvsummary.pdf).

Ballots/voters and registration come from separate [2024 turnout](https://sos.iowa.gov/elections/pdf/2024/general/turnout.pdf), [2022 turnout](https://sos.iowa.gov/elections/pdf/2022/general/turnout.pdf) and [2020 turnout](https://sos.iowa.gov/elections/pdf/2020/general/turnout.pdf) reports. In 2024 Des Moines County, turnout-report Election Day/Absentee are **9,996/9,175**, versus canvass **10,003/9,168**. The state method totals differ by the same −7/+7 (992,112/681,899 versus 992,119/681,892), with the same 1,674,011 total. Both observations remain; no method is reassigned. Active/inactive registration and source percentages remain separate, including printed active percentages over 100%. [Scope comparisons](data/baselines/turnout-scope-checks.csv).

## Native reporting evidence and explicit conflicts

All actual [2022 county exports](https://sos.iowa.gov/precinct-results-county-2022-general-0) and [2020 county exports](https://sos.iowa.gov/precinct-results-county-2020-general) were retained losslessly. The [source manifest](data/baselines/sources.json) records their actual parent chains, bytes, hashes, statuses, clocks and errors. 2022 XML Spreadsheet files have an `.xls` extension; 2020 is XLSX except the actual [Scott PDF](https://sos.iowa.gov/elections/pdf/precinctresults/2020general/scott.pdf). Black Hawk's linked double-space filename failed; the explicitly labeled [single-space filename repair](https://sos.iowa.gov/elections/pdf/precinctresults/2022general/black%20hawk.xls) returned the original XML. Failed Adair/Story alternatives remain recorded alongside valid XLSX. Nothing is deduplicated or filled from a residual.

Independent extraction retains **1,653 constituent rows plus 99 controls in 2022**, and **1,661 plus 99 in 2020**, including 63 Scott constituents. All **2,385** candidate/method county sums and native footers exactly equal primary county controls. Every candidate's native Election Day plus Absentee equals its Total. All sparse workbook rows/cells across every worksheet are retained under `data/baselines/cells/`, with original files authoritative for document properties and formatting. [Native units](data/baselines/native-units.csv), [native candidate/method cells](data/baselines/native-candidate-method.csv), [registration/ballot cells](data/baselines/native-registration-ballots.csv), [coverage](data/baselines/native-coverage.csv), [controls](data/baselines/native-checks.csv).

The actual SOS-linked [2024 Clarity app](https://electionresults.iowa.gov/IA/122322/web.345435/) initially returned 403, then a later request returned the real app. Its observed scripts/configuration led to pinned state version `356043`, [actual settings and participating county IDs/versions](https://electionresults.iowa.gov/IA/122322/356043/json/en/electionsettings.json), [state XML](https://electionresults.iowa.gov/IA/122322/356043/reports/detailxml.zip) and all 99 county XML/settings/status sources. The state XML clock is **12/16/2024 8:19:40 AM CST**; county clocks/versions remain individually pinned. Our independent raw extraction of all 99 county XMLs gives **26,448 candidate/method unit cells** and **2,376 county controls**, all equal to the primary canvass; state XML's 1,608 comparison cells and state summary JSON's eight candidates also match. Every named candidate and generic Write-in is present. Under/over are not published at candidate-unit level in these XMLs and remain unknown. [2024 summary](data/baselines/clarity-2024-summary.json), [native candidate cells](data/baselines/clarity-2024-native-candidate-method.csv), [county controls](data/baselines/clarity-2024-county-candidate-method.csv), [state JSON](https://electionresults.iowa.gov/IA/122322/356043/json/sum.json).

2024 has **1,653 candidate units**, **1,651 XML turnout units**, and **1,653 status units**; these are separate contexts. **Lucas (`19117`) has seven candidate/status units but five XML turnout units.** `Chariton City Hall Precinct ` and `Chariton Community Center Precinct `, including trailing spaces, are absent only from XML turnout. Its five turnout rows sum to **2,733** ballots versus **4,676** in the county XML control; the seven status B values sum to 4,676. No allocation or identity repair is made. Root VoterTurnout units have no native contest key; a separate context key prevents an implicit candidate-unit join. See [original Lucas XML](https://electionresults.iowa.gov/IA/Lucas/122381/354852/reports/detailxml.zip), [original status](https://electionresults.iowa.gov/IA/Lucas/122381/354852/json/status.json), [context conflicts](data/baselines/clarity-2024-context-coverage.csv), [native identities](data/baselines/clarity-2024-native-units.csv) and [status fields](data/baselines/clarity-2024-status-units.csv). Status codes and reporting fractions are not vote-completion percentages.

Local 2024 party headers differ from state SOC for Stodden/Cholensky in **14 counties/42 method rows**, including SPA/SPU/PSI/NoP labels. Exact ticket-name counts match; each original label remains intact, with no party rewriting. [Difference ledger](data/baselines/clarity-2024-party-label-differences.csv), [state XML](https://electionresults.iowa.gov/IA/122322/356043/reports/detailxml.zip). Equal historical unit counts or matching names do not establish equal physical precincts, ballot styles, central absentee boards or polygons, or a cross-year/November 2026 crosswalk.

The read-only turnout statistics evidence retains **4,990 native labels**: 1,658 in 2024, 1,651 in 2022, 1,681 in 2020, separately from candidate exports and Grand Totals. We independently verified all **327,516 demographic/age/metric rows (2,620,128 numeric/percentage cells)** and every label against exact original PDF page/line text. [Verification](data/baselines/statistics-verification.json), [peer statistics contract](data/turnout/SCHEMA.md). The [2022 statistics](https://sos.iowa.gov/elections/pdf/2022/general/precinctstats.pdf) preserve Harrison's January 27, 2023 addendum. The [2020 county report](https://sos.iowa.gov/elections/pdf/2020/general/countystats.pdf) covers 97 counties, omitting Henry and Story; the [revised state report](https://sos.iowa.gov/elections/pdf/2020/general/statestats.pdf) and [precinct report](https://sos.iowa.gov/elections/pdf/2020/general/precinctstats.pdf) have separate clocks/scopes. The state source warns that delayed revisions need not sum to precincts. Its printed REGISTERED total 2,203,254 differs from age-bin sum 2,203,256 by +2; this intrinsic source disagreement remains.

The [Cass local file](https://www.casscountyia.gov/wp-content/uploads/2019/10/2024.11.05-General-Election-Results.pdf), linked from its [official results page](https://www.casscountyia.gov/county-government/elections/), internally says **Unofficial Final Results, 11/12/2024 1:04:10 PM CST**. Its “Election Day” heading accompanies countywide candidate totals, not a usable method split: candidate+generic 7,217, ballots 7,292, registration 9,661 and 12/12 reporting. This source scope is retained separately from SOS registration/vintage. [Inspected preview](data/baselines/review/cass-page1.png).

## Scenario arithmetic and historical sensitivity

Let `s_c=D/(D+R)`, `V_c` the named historical county candidate-plus-generic volume, `p_c=(D+R)/A` in that county's preference baseline, and `T_c=V_c*p_c`. Native historical checks use exact integer D+R. `M0=sum(T_c*(2*s_c-1))`; pair tie shift is `-M0/(2*sum(T))`. At fixed pair weights, **one D-share percentage point changes the D-minus-R margin by two points and net votes by `0.02*T_c`**. Pair D+1 adds 0.5 D-share points to a feasible unbounded tie. All-candidate D+1 instead requires net `.01*sum(V)`, a separate denominator. These formulas reproduce the original counts, not a 2026 population/turnout estimate. [Primary 2020](https://sos.iowa.gov/elections/pdf/2020/general/canvsummary.pdf), [2022](https://sos.iowa.gov/elections/pdf/2022/general/canvsummary.pdf), [2024](https://sos.iowa.gov/elections/pdf/2024/general/canvsummary.pdf), [actual implementation](data/baselines/calculate.py).

| Native preference/volume | Observed D−R votes | Pair margin pp | Tie D-share shift pp | D+1 D-share shift pp | D+1 net votes |
| --- | --- | --- | --- | --- | --- |
| 2020-senate | -110,138 | -6.799246 | +3.399623 | +3.899623 | 16,198.56 |
| 2022-senate | -148,171 | -12.196841 | +6.098420 | +6.598420 | 12,148.31 |
| 2024-president | -219,741 | -13.445598 | +6.722799 | +7.222799 | 16,342.97 |

Low/base/high use **actual** 2022 Senate/2024 presidential/2020 Senate county candidate volumes, respectively. The table below holds 2020 same-seat county preferences and pair participation fixed, changing county volume/mix. Uniformly scaling all counties would change net magnitudes but leave the share threshold unchanged; these observed mixes also alter composition. No arbitrary 2026 participation multipliers are presented as researched turnout bounds.

| Volume/mix | Candidate+generic volume | Pair pool | Baseline D−R net | Tie share pp | D+1 share pp |
| --- | --- | --- | --- | --- | --- |
| 2022-senate | 1,216,646 | 1,179,016.394 | -77,198.107 | +3.273835 | +3.773835 |
| 2024-president | 1,663,506 | 1,611,927.934 | -107,902.939 | +3.347015 | +3.847015 |
| 2020-senate | 1,671,828 | 1,619,856.000 | -110,138.000 | +3.399623 | +3.899623 |

There are **36 state scenarios, 3,564 county targets and 3,564 selected-county solves**: three preference baselines × (three historical all-candidate mixes plus exact native-pair check) × tie/pair-D+1/all-candidate-D+1. Every state's weights, pair participation, county contribution and net gain use its declared settings. [Settings](data/baselines/scenario-settings.json), [state results](data/baselines/state-scenarios.csv), [all county targets](data/baselines/county-target-scenarios.csv), [separate named-other amounts](data/baselines/scenario-other-candidates.csv). Named nonmajor candidates and generic marks retain their separate baseline shares. D exceeds every separately fixed other in these illustrative D+1 cases; this does not assert a 2026 candidate universe.

The solver reports unbounded values, clips shares to [0,1] and re-solves feasible bounded thresholds. No actual historical scenario needs clipping. Synthetic tests exercise it and already-winning negative shifts, impossible targets and zero/unknown pools. A mathematical tie is not an integer plurality win. These are deterministic scenarios, with fractional expected votes and display rounding after calculation; no probabilities are assigned.

## One county, or the remaining vote, conditional on everything else

For the following examples, every other county remains at **2020 Senate preferences**, at **actual 2024 candidate-plus-generic county volume × its own 2020 pair participation**. Total pair pool is 1,611,927.933944. Only the selected county's D/R allocation changes. Required share is `(target_net-other_net+selected_T)/(2*selected_T)`; above 100% means impossible under these fixed assumptions, not a clipped winning path.

| Selected county | Pair pool | Fixed other net | Tie D share | D+1 pair D share | Tie status |
| --- | --- | --- | --- | --- | --- |
| Polk | 249,335.027 | -143,869.300 | 78.8506% | 82.0831% | feasible |
| Linn | 118,979.502 | -123,339.658 | 101.8323% | 108.6063% | impossible |
| Johnson | 84,759.774 | -142,808.834 | 134.2433% | 143.7521% | impossible |
| Adams | 2,067.756 | -107,009.977 | 2637.5873% | 3027.3644% | impossible |

All 99 solves and alternative mixes are in [selected-county-break-even.csv](data/baselines/selected-county-break-even.csv). The [selected native-unit example](data/baselines/selected-native-unit-example.json) varies only historical 2022 Polk `DES MOINES 1` Absentee while holding every other historical statewide vote fixed; it honestly returns impossible. It establishes no current-unit crosswalk.

The offline `calculate.py --live-json INPUT.json` interface keeps counted votes fixed and varies only explicitly supplied remaining pair pools/shares. For a selected pool, required share is `(target_final_net-counted_lead-other_remaining_net+selected_U)/(2*selected_U)`. **Target final net uses counted plus all remaining votes**, not only the selected pool. Synthetic counted D40/R60/other10 plus remaining pair100/other20 requires 60% D of the pair remainder to tie; **61%** gives D+1 of final pair200; **61.15%** gives D+1 of final all-candidate230. These values are tests, not live observations. [Examples](data/baselines/live-remainder-examples.json), [calculator/schema](data/baselines/SCHEMA.md).

## All 99 counties

Signed margins below are observed **D-minus-R pair-margin points**; positive means the D candidate led in that historical contest. The scenario columns use 2020 same-seat preferences and actual 2024 all-candidate county volumes with 2020 county pair participation. Weight is county share of scenario pair pool; baseline/target net are D−R. “+1 pp gain” means one D-share point at fixed pair volume. The D+1 shares form one statewide combination, not separate necessary county conditions. Every integer candidate count, source/method and denominator is retained in [county-baselines.csv](data/county-baselines.csv) and [primary-derived county rows](data/baselines/county-contests.csv), sourced from the three [SOS original canvasses](https://sos.iowa.gov/iowans/election-results-statistics).

| County | FIPS | 2020 Senate pp | 2022 Senate pp | 2024 pres pp | Pair weight % | Baseline net | +1 pp gain | D+1 target D % | D+1 target net |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Adair | 19001 | -39.89 | -43.97 | -45.73 | 0.2453 | -1,577.26 | 79.08 | 33.9018 | -1,273.04 |
| Adams | 19003 | -43.19 | -42.84 | -44.96 | 0.1283 | -892.96 | 41.36 | 32.2545 | -733.87 |
| Allamakee | 19005 | -26.50 | -32.61 | -34.79 | 0.4381 | -1,871.40 | 141.25 | 40.5984 | -1,328.00 |
| Appanoose | 19007 | -36.34 | -42.67 | -47.23 | 0.3871 | -2,267.27 | 124.79 | 35.6778 | -1,787.21 |
| Audubon | 19009 | -33.41 | -37.22 | -39.07 | 0.1961 | -1,056.02 | 63.21 | 37.1397 | -812.86 |
| Benton | 19011 | -25.86 | -32.49 | -33.66 | 0.8715 | -3,632.26 | 280.97 | 40.9194 | -2,551.36 |
| Black Hawk | 19013 | +8.94 | +1.91 | +1.18 | 3.7945 | +5,470.79 | 1,223.28 | 58.3192 | +10,176.77 |
| Boone | 19015 | -13.66 | -16.60 | -21.89 | 0.9204 | -2,027.03 | 296.72 | 47.0156 | -885.53 |
| Bremer | 19017 | -16.20 | -20.90 | -22.46 | 0.8847 | -2,309.83 | 285.21 | 45.7482 | -1,212.64 |
| Buchanan | 19019 | -17.10 | -24.69 | -28.65 | 0.6452 | -1,778.61 | 207.99 | 45.2956 | -978.47 |
| Buena Vista | 19021 | -21.97 | -39.86 | -33.67 | 0.4531 | -1,604.70 | 146.06 | 42.8607 | -1,042.79 |
| Butler | 19023 | -36.28 | -44.39 | -45.91 | 0.4839 | -2,830.01 | 156.02 | 35.7079 | -2,229.81 |
| Calhoun | 19025 | -39.29 | -47.06 | -47.26 | 0.3060 | -1,938.27 | 98.65 | 34.1999 | -1,558.74 |
| Carroll | 19027 | -33.86 | -42.54 | -42.50 | 0.6702 | -3,657.78 | 216.07 | 36.9186 | -2,826.54 |
| Cass | 19029 | -35.31 | -42.23 | -41.36 | 0.4364 | -2,483.90 | 140.69 | 36.1924 | -1,942.65 |
| Cedar | 19031 | -15.97 | -21.49 | -22.12 | 0.6412 | -1,650.98 | 206.70 | 45.8597 | -855.80 |
| Cerro Gordo | 19033 | +0.85 | -9.56 | -11.83 | 1.3882 | +190.77 | 447.54 | 54.2733 | +1,912.49 |
| Cherokee | 19035 | -35.59 | -48.45 | -46.38 | 0.3664 | -2,101.83 | 118.13 | 36.0542 | -1,647.39 |
| Chickasaw | 19037 | -26.78 | -32.60 | -37.62 | 0.3734 | -1,611.90 | 120.38 | 40.4570 | -1,148.79 |
| Clarke | 19039 | -31.31 | -39.77 | -42.57 | 0.2668 | -1,346.91 | 86.02 | 38.1895 | -1,015.97 |
| Clay | 19041 | -33.29 | -43.67 | -43.74 | 0.5125 | -2,749.72 | 165.21 | 37.2037 | -2,114.14 |
| Clayton | 19043 | -25.98 | -31.66 | -34.92 | 0.5682 | -2,379.61 | 183.16 | 40.8553 | -1,674.98 |
| Clinton | 19045 | -6.88 | -14.17 | -19.17 | 1.4296 | -1,585.59 | 460.89 | 50.4067 | +187.46 |
| Crawford | 19047 | -30.89 | -49.84 | -43.93 | 0.3916 | -1,949.77 | 126.25 | 38.4032 | -1,464.09 |
| Dallas | 19049 | -6.09 | -5.74 | -4.81 | 3.8061 | -3,738.64 | 1,227.05 | 50.8001 | +981.82 |
| Davis | 19051 | -40.08 | -48.55 | -55.03 | 0.2364 | -1,527.39 | 76.22 | 33.8085 | -1,234.16 |
| Decatur | 19053 | -35.35 | -42.00 | -47.82 | 0.2235 | -1,273.66 | 72.06 | 36.1722 | -996.44 |
| Delaware | 19055 | -33.22 | -42.09 | -40.21 | 0.6133 | -3,284.44 | 197.72 | 37.2354 | -2,523.81 |
| Des Moines | 19057 | -0.92 | -11.50 | -15.27 | 1.1307 | -167.07 | 364.53 | 53.3887 | +1,235.27 |
| Dickinson | 19059 | -30.69 | -40.60 | -40.44 | 0.6817 | -3,373.01 | 219.78 | 38.4997 | -2,527.52 |
| Dubuque | 19061 | -1.17 | -7.07 | -8.70 | 3.1742 | -597.49 | 1,023.33 | 53.2631 | +3,339.27 |
| Emmet | 19063 | -28.86 | -43.78 | -44.48 | 0.2856 | -1,328.28 | 92.06 | 39.4185 | -974.12 |
| Fayette | 19065 | -19.98 | -27.10 | -30.97 | 0.5913 | -1,903.89 | 190.62 | 43.8593 | -1,170.56 |
| Floyd | 19067 | -8.89 | -21.32 | -26.07 | 0.4571 | -655.41 | 147.38 | 49.3998 | -88.45 |
| Franklin | 19069 | -33.22 | -42.79 | -42.25 | 0.2946 | -1,577.56 | 94.96 | 37.2347 | -1,212.23 |
| Fremont | 19071 | -39.98 | -43.37 | -45.21 | 0.2264 | -1,459.00 | 72.99 | 33.8579 | -1,178.21 |
| Greene | 19073 | -26.39 | -31.53 | -33.40 | 0.2940 | -1,250.56 | 94.78 | 40.6533 | -885.92 |
| Grundy | 19075 | -39.60 | -45.56 | -42.45 | 0.4312 | -2,752.65 | 139.02 | 34.0464 | -2,217.84 |
| Guthrie | 19077 | -34.46 | -38.00 | -38.50 | 0.3916 | -2,175.14 | 126.25 | 36.6178 | -1,689.46 |
| Hamilton | 19079 | -23.26 | -31.78 | -33.69 | 0.4544 | -1,703.66 | 146.48 | 42.2164 | -1,140.15 |
| Hancock | 19081 | -36.07 | -45.00 | -48.01 | 0.3566 | -2,073.77 | 114.97 | 35.8096 | -1,631.47 |
| Hardin | 19083 | -31.77 | -37.90 | -38.80 | 0.5082 | -2,602.41 | 163.84 | 37.9632 | -1,972.12 |
| Harrison | 19085 | -32.56 | -43.06 | -42.52 | 0.4700 | -2,466.71 | 151.54 | 37.5690 | -1,883.75 |
| Henry | 19087 | -25.91 | -34.11 | -36.51 | 0.5687 | -2,375.44 | 183.35 | 40.8916 | -1,670.07 |
| Howard | 19089 | -14.84 | -27.04 | -32.20 | 0.2901 | -693.99 | 93.52 | 46.4263 | -334.21 |
| Humboldt | 19091 | -43.57 | -51.35 | -50.62 | 0.3064 | -2,151.39 | 98.76 | 32.0637 | -1,771.45 |
| Ida | 19093 | -48.19 | -56.73 | -54.07 | 0.2210 | -1,716.90 | 71.26 | 29.7540 | -1,442.76 |
| Iowa | 19095 | -24.13 | -30.84 | -28.18 | 0.5794 | -2,253.94 | 186.78 | 41.7795 | -1,535.40 |
| Jackson | 19097 | -18.48 | -26.21 | -32.96 | 0.6400 | -1,906.23 | 206.34 | 44.6087 | -1,112.44 |
| Jasper | 19099 | -18.13 | -24.34 | -28.02 | 1.2082 | -3,530.06 | 389.52 | 44.7844 | -2,031.58 |
| Jefferson | 19101 | +6.30 | -0.76 | -6.94 | 0.5029 | +510.73 | 162.13 | 56.9972 | +1,134.43 |
| Johnson | 19103 | +41.18 | +42.68 | +38.57 | 5.2583 | +34,905.89 | 1,695.20 | 74.4381 | +41,427.34 |
| Jones | 19105 | -19.73 | -25.46 | -26.74 | 0.6596 | -2,097.90 | 212.65 | 43.9815 | -1,279.83 |
| Keokuk | 19107 | -41.08 | -49.52 | -52.08 | 0.3097 | -2,050.91 | 99.86 | 33.3088 | -1,666.75 |
| Kossuth | 19109 | -36.07 | -42.59 | -44.74 | 0.5065 | -2,944.45 | 163.28 | 35.8137 | -2,316.32 |
| Lee | 19111 | -6.55 | -21.75 | -28.42 | 0.9674 | -1,021.67 | 311.86 | 50.5710 | +178.07 |
| Linn | 19113 | +12.97 | +9.04 | +10.05 | 7.3812 | +15,436.72 | 2,379.59 | 60.3341 | +24,591.04 |
| Louisa | 19115 | -28.74 | -40.33 | -41.55 | 0.3071 | -1,422.63 | 99.01 | 39.4781 | -1,041.75 |
| Lucas | 19117 | -40.91 | -45.68 | -48.83 | 0.2795 | -1,843.07 | 90.10 | 33.3909 | -1,496.46 |
| Lyon | 19119 | -67.46 | -73.19 | -70.44 | 0.4243 | -4,614.41 | 136.80 | 20.1169 | -4,088.13 |
| Madison | 19121 | -32.69 | -35.60 | -39.06 | 0.6025 | -3,174.50 | 194.23 | 37.5026 | -2,427.31 |
| Mahaska | 19123 | -45.17 | -51.51 | -52.21 | 0.6549 | -4,768.16 | 211.14 | 31.2641 | -3,955.90 |
| Marion | 19125 | -32.15 | -38.60 | -38.30 | 1.1768 | -6,099.11 | 379.37 | 37.7702 | -4,639.66 |
| Marshall | 19127 | -5.05 | -18.17 | -15.82 | 1.0337 | -840.69 | 333.26 | 51.3244 | +441.37 |
| Mills | 19129 | -35.52 | -40.83 | -39.56 | 0.4952 | -2,835.64 | 159.66 | 36.0863 | -2,221.43 |
| Mitchell | 19131 | -18.92 | -30.24 | -31.57 | 0.3473 | -1,059.31 | 111.98 | 44.3871 | -628.53 |
| Monona | 19133 | -35.46 | -45.99 | -45.87 | 0.2780 | -1,589.40 | 89.64 | 36.1158 | -1,244.56 |
| Monroe | 19135 | -40.98 | -47.39 | -51.19 | 0.2503 | -1,653.24 | 80.69 | 33.3586 | -1,342.82 |
| Montgomery | 19137 | -41.01 | -42.84 | -39.61 | 0.3060 | -2,022.52 | 98.65 | 33.3444 | -1,643.02 |
| Muscatine | 19139 | -4.56 | -15.74 | -15.18 | 1.1785 | -866.77 | 379.93 | 51.5656 | +594.82 |
| O'Brien | 19141 | -55.16 | -63.55 | -61.54 | 0.4576 | -4,069.07 | 147.54 | 26.2667 | -3,501.50 |
| Osceola | 19143 | -58.71 | -69.50 | -65.07 | 0.1953 | -1,848.54 | 62.98 | 24.4944 | -1,606.26 |
| Page | 19145 | -42.73 | -45.60 | -42.88 | 0.4409 | -3,036.89 | 142.13 | 32.4798 | -2,490.12 |
| Palo Alto | 19147 | -29.98 | -44.47 | -45.54 | 0.3002 | -1,450.56 | 96.77 | 38.8575 | -1,078.28 |
| Plymouth | 19149 | -47.76 | -57.68 | -54.90 | 0.8478 | -6,526.24 | 273.31 | 29.9685 | -5,474.81 |
| Pocahontas | 19151 | -44.95 | -53.27 | -54.81 | 0.2142 | -1,552.20 | 69.06 | 31.3717 | -1,286.52 |
| Polk | 19153 | +14.42 | +12.69 | +11.03 | 15.4681 | +35,966.36 | 4,986.70 | 61.0595 | +55,150.27 |
| Pottawattamie | 19155 | -14.34 | -22.83 | -20.24 | 2.6524 | -6,130.38 | 855.09 | 46.6777 | -2,840.84 |
| Poweshiek | 19157 | -10.06 | -15.35 | -17.21 | 0.6026 | -977.07 | 194.26 | 48.8172 | -229.76 |
| Ringgold | 19159 | -43.74 | -45.49 | -51.90 | 0.1608 | -1,133.78 | 51.85 | 31.9792 | -934.32 |
| Sac | 19161 | -45.55 | -53.28 | -52.16 | 0.3266 | -2,398.02 | 105.30 | 31.0733 | -1,992.94 |
| Scott | 19163 | +3.17 | -3.62 | -3.95 | 5.4138 | +2,764.82 | 1,745.32 | 55.4311 | +9,479.08 |
| Shelby | 19165 | -38.59 | -47.42 | -43.50 | 0.3905 | -2,429.41 | 125.90 | 34.5509 | -1,945.07 |
| Sioux | 19167 | -69.61 | -75.96 | -71.88 | 1.1612 | -13,029.69 | 374.35 | 19.0407 | -11,589.56 |
| Story | 19169 | +15.25 | +13.97 | +10.53 | 2.9784 | +7,320.12 | 960.18 | 61.4707 | +11,013.96 |
| Tama | 19171 | -17.31 | -28.24 | -27.33 | 0.5171 | -1,442.72 | 166.71 | 45.1929 | -801.39 |
| Taylor | 19173 | -50.82 | -56.73 | -56.28 | 0.1845 | -1,511.71 | 59.49 | 28.4356 | -1,282.85 |
| Union | 19175 | -30.13 | -34.92 | -36.67 | 0.3576 | -1,736.94 | 115.29 | 38.7814 | -1,293.41 |
| Van Buren | 19177 | -41.61 | -51.52 | -56.33 | 0.2187 | -1,466.62 | 70.49 | 33.0411 | -1,195.44 |
| Wapello | 19179 | -14.32 | -26.48 | -31.88 | 0.8729 | -2,014.33 | 281.40 | 46.6887 | -931.79 |
| Warren | 19181 | -16.13 | -18.65 | -21.04 | 1.9722 | -5,126.33 | 635.80 | 45.7842 | -2,680.39 |
| Washington | 19183 | -19.96 | -25.50 | -24.72 | 0.6966 | -2,241.23 | 224.56 | 43.8665 | -1,377.35 |
| Wayne | 19185 | -47.21 | -56.70 | -58.10 | 0.1884 | -1,433.67 | 60.74 | 30.2443 | -1,199.99 |
| Webster | 19187 | -19.66 | -28.96 | -31.59 | 1.0039 | -3,181.50 | 323.66 | 44.0172 | -1,936.38 |
| Winnebago | 19189 | -17.11 | -32.19 | -31.15 | 0.3365 | -928.27 | 108.48 | 45.2899 | -510.95 |
| Winneshiek | 19191 | -3.94 | -6.45 | -9.41 | 0.7220 | -458.73 | 232.77 | 51.8763 | +436.74 |
| Woodbury | 19193 | -12.84 | -27.13 | -23.33 | 2.5614 | -5,300.57 | 825.76 | 47.4280 | -2,123.87 |
| Worth | 19195 | -14.71 | -26.38 | -28.58 | 0.2569 | -609.21 | 82.82 | 46.4913 | -290.60 |
| Wright | 19197 | -30.68 | -40.33 | -37.04 | 0.3415 | -1,688.78 | 110.09 | 38.5076 | -1,265.25 |

## Reproduction, checks and remaining limits

[SCHEMA.md](data/baselines/SCHEMA.md) documents keys, full candidate/metric definitions, denominator choices, statuses, aliases and build order. [Source references](data/baselines/sources.json) reuse original bytes read-only; [HTTP refreshes](data/baselines/http-refresh.json) preserve independent request chains. [Peer reconciliation](data/baselines/peer-reconciliation.json) compares every shared candidate/native/method/registration/priority field with the actual turnout worker; [statistics verification](data/baselines/statistics-verification.json) checks every shared statistics cell directly against original pages. [Offline validator](data/baselines/validate.py), [validation results](data/baselines/validation.json) and [owned asset inventory](data/baselines/asset-manifest.json) cover all 99 uniqueness/coverage, every available control, native completeness/duplicates, exact integer priority, weights/gains/bounds, correct final-denominator arithmetic, hashes/sizes and local links. No artifact reaches 40,000,000 bytes; compressed originals are not truncated.

Remaining limits are explicit: generic write-in named validity; some native registration zeroes and unit/count scope conflicts; absent finer under/over in 2024 XML; historical physical precinct/split/central-absentee classification and cross-year/2026 geographic crosswalks; actual November roster and source approval; remaining-vote evidence; and model calibration. This package implements an offline scenario calculator. It does not implement a live collector, calibrated Needle, 2026 turnout projection or win forecast.
