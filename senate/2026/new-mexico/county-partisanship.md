# New Mexico historical partisanship and conditional paths

Research completed from original public source captures on **2026-10-20 UTC**. These are historical arithmetic scenarios, not 2026 turnout projections, calibrated probabilities, a collector, or a current precinct crosswalk.

The 2024 Senate comparison already favors Martin Heinrich over Nella Louise Domenici by **91,355 votes**, or **10.113350 pair-margin points**. At its fixed county pair weights, a uniform **−5.056675 percentage-point shift in Heinrich's pair share** ties; **−4.556675 share points** gives the illustrative **A+1 pair margin**. No positive improvement is required to repeat that historical outcome. A means the explicitly named Democratic candidate in each historical contest; B means its named Republican opponent. “Other” never means Democratic. The actual [2024 Senate publication](https://electionstats.sos.nm.gov/contest/14873) supplies the source labels; its county values were independently verified against all original county candidate columns in the [state canvass](https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/ee3072ab0d43456cb15a51f7d82c77a2/e2ad2789-7c82-48ba-9e96-b86dae0fb886/General%20Election%20State%20Canvass.pdf).

## Elections and current-source scope

The priority basis is **2024-11-05 Senate, Class I**, Heinrich–Domenici, the other seat. **2020-11-03 Senate, Class II**, Ben R. Lujan–Mark V. Ronchetti–Bob Walsh, is the same seat as the 2026 regular election. The actual midterm is **2022-11-08 governor**, not an invented 2022 Senate election. **2024 president** is a separate electorate/contest comparison. Historical event dates, contest/office IDs, candidates, parties, winner flags, source verification timestamps and every embedded metadata field are retained in [original page objects](data/baselines/source/independent-first-pin.json). The [Class II roster](https://www.senate.gov/senators/Class_II.htm) and [Class I roster](https://www.senate.gov/senators/Class_I.htm) establish seat context.

The [2026 SOS index](https://www.sos.nm.gov/voting-and-elections/election-results/2026-election-results/) gives November 3 as the general date, while retaining generic November 2021 prose. Its actual linked [2911 results](https://electionresults.sos.nm.gov/default.aspx?eid=2911) identify the June 2 primary, updated June 23, 2026, 2:26 PM **MT**. Municipal and Rio Rancho runoff links have separate contexts. None identifies a November Senate result contest. Fresh October 20 requests, redirects, headers and full bodies are in [fresh receipts](data/baselines/source/fresh-observations.json).

The SOS-home-linked [**general** candidate portal](https://candidateportal.servis.sos.state.nm.us/CandidateList.aspx?eid=2917&cty=99) independently supplies all four Senate status records below. All 24 visible/hidden cell fields, original row attributes/positions and filing clocks are retained in [status records](data/baselines/current-senate-status-records.json); a fresh original read agrees on every cell. Filing clock timezone is unstated. Qualified status is not a signed final ballot or a current result-ID mapping. A bounded attempt to retrieve Otero's indexed general election notice returned **404 with an empty body**; no final ballot printing/write-in mapping is asserted. Primary write-in labels and old candidate IDs are not carried forward.

| General portal name | Party literal | Status | Filing clock literal |
|---|---|---|---|
| BEN R LUJAN | DEM | Qualified | 2/3/2026 9:44:07 AM |
| LARRY E MARKER | REP | Qualified | 3/17/2026 9:10:00 AM |
| MIRA OCONNELL | DTS | Disqualified | 6/25/2026 4:31:00 PM |
| BOB PERLS | FWD | Disqualified | 6/25/2026 11:44:16 AM |

The Senate calculation treats an outright win as A exceeding every opponent's final vote count. A pair tie or pair cushion is an arithmetic benchmark, not the legal outcome rule. The official [2025 Election Handbook](https://www.donaanacountyelections.com/wp-content/uploads/2025/08/2025-NM_Election_Handbook_SOS-1.pdf), §§1-15-12–13, §1-14-18 and §1-13-11, covers the general election, state-officer canvass, plurality and tie-by-lot provisions. Its municipal runoff provisions (§1-22-16) remain separate; this package infers no Senate RCV transfers or lower preferences.

## State outcomes and complete candidates

These are named candidate votes, not ballots, registration or eligible population. “All candidate” means the complete published named field for that contest, not proof of an unreported generic/valid-write-in, undervote, blank or overvote universe. Those missing controls remain null. The 2024 Senate field has two candidates; its displayed other=0 describes that field only.

| Contest | A votes | B votes | Other named votes | All named votes | A+B | A pair share % | A−B pair margin pp | A−B all-candidate margin pp |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2024-senate | 497,333 | 405,978 | 0 | 903,311 | 903,311 | 55.056675 | +10.113350 | +10.113350 |
| 2020-senate | 474,483 | 418,483 | 24,271 | 917,237 | 892,966 | 53.135618 | +6.271235 | +6.105292 |
| 2022-governor | 370,168 | 324,701 | 17,387 | 712,256 | 694,869 | 53.271624 | +6.543248 | +6.383519 |
| 2024-president | 478,802 | 423,391 | 21,210 | 923,403 | 902,193 | 53.070906 | +6.141812 | +6.000739 |

All 33 county candidate vectors sum exactly to every statewide candidate control, independently checked against the original PDF county columns: **495 county candidate cells**, across 15 named candidacies/tickets. [PDF checks](data/baselines/pdf-county-controls.json) retain source page, text line, entire source line and column order. Source spellings/punctuation differ; labels are kept separately rather than silently harmonized. For example, narrative Luján and Doña Ana retain their accents here, while a source that prints `Lujan` or `Dona Ana` remains literal in its data. The Census `Doña Ana`→results `Dona Ana` county-only FIPS alias is explicit in the schema, never a precinct crosswalk.

**2024-senate:** [official database](https://electionstats.sos.nm.gov/contest/14873), [original statewide candidate/method publication](https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/ee3072ab0d43456cb15a51f7d82c77a2/c7e73a30-8a5e-4a1b-bb76-669da1347713/2024%20General%20Summary%20Results%20Report.pdf).

- Martin Heinrich — Democratic: **497,333**.
- Nella Louise Domenici — Republican: **405,978**.

**2020-senate:** [official database](https://electionstats.sos.nm.gov/contest/13251), [original statewide candidate/method publication](https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/ee3072ab0d43456cb15a51f7d82c77a2/067ee04f-38ad-4484-871b-8776afc09e37/2020%20General%20Candidate%20Summary%20Results%20Report.PDF).

- Ben R. Lujan — Democratic: **474,483**.
- Mark V. Ronchetti — Republican: **418,483**.
- Bob Walsh — Libertarian: **24,271**.

**2022-governor:** [official database](https://electionstats.sos.nm.gov/contest/11090), [original statewide candidate/method publication](https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/ee3072ab0d43456cb15a51f7d82c77a2/05f5f6e8-d139-452f-a03e-3a3a71ddd602/2022%20General%20Election%20Candidate%20Summary%20Results%20Report.pdf).

- Michelle Lujan Grisham and Howie C. Morales — Democratic: **370,168**.
- Mark V. Ronchetti and Ant L. Thornton — Republican: **324,701**.
- Karen Evette Bedonie and Efren Gallardo Jr. — Libertarian: **17,387**.

**2024-president:** [official database](https://electionstats.sos.nm.gov/contest/14877), [original statewide candidate/method publication](https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/ee3072ab0d43456cb15a51f7d82c77a2/c7e73a30-8a5e-4a1b-bb76-669da1347713/2024%20General%20Summary%20Results%20Report.pdf).

- Kamala D. Harris and Timothy Walz — Democratic: **478,802**.
- Donald J. Trump and JD Vance — Republican: **423,391**.
- Robert F. Kennedy, Jr and Nicole Shanahan — Independent: **9,553**.
- Jill Stein and Rudolph Ware — Green: **4,611**.
- Chase Oliver and Mike Ter Maat — Libertarian: **3,745**.
- Claudia De La Cruz and Karina Garcia — Party for Socialism and Liberation: **2,442**.
- Laura Ebke and Trisha Butler — Liberal Party USA: **859**.


Independent, Libertarian, Green, Party for Socialism and Liberation and Liberal Party USA tickets stay named; none is reassigned to A. These four required contests each have a Democrat, so no fabricated Democratic or non-R coalition is needed. Counterfactual preference anchors do not establish candidate effects in 2026.

## All counties and fixed-weight targets

The table covers every county, ordered by 2024 Senate candidate volume. Margins are A−B **pair margin points** in the indicated contest. Weight is county A+B / state A+B for 2024 Senate. Tie/A+1 columns are illustrative county A pair shares under the common statewide shift; no county target is independently necessary. Every other county remains in statewide sums. [All 132 contest/county baseline rows](data/county-baselines.csv) include counts, denominators, source positions, historical winner and closeness bands (absolute pair margin ≤5, >5–10, >10 points). [All 1,056 county scenario rows](data/baselines/county-target-scenarios.csv) add contributions, gains and selected-only requirements.

| County source label | Senate net A−B | Senate margin pp | Same-seat 2020 margin pp | President 2024 margin pp | Governor 2022 margin pp | Senate weight % | Tie A share % | A+1 A share % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Bernalillo | +69,588 | +22.835 | +16.564 | +21.578 | +17.249 | 33.736 | 56.361 | 56.861 |
| Dona Ana | +10,360 | +12.471 | +19.360 | +9.988 | +16.138 | 9.196 | 51.179 | 51.679 |
| Santa Fe | +42,129 | +51.069 | +50.617 | +50.021 | +52.609 | 9.133 | 70.478 | 70.978 |
| Sandoval | +6,514 | +8.305 | +1.499 | +5.912 | +2.415 | 8.683 | 49.096 | 49.596 |
| San Juan | -13,339 | -25.903 | -31.541 | -32.478 | -33.118 | 5.701 | 31.992 | 32.492 |
| Valencia | -3,047 | -9.327 | -15.006 | -16.678 | -18.775 | 3.616 | 40.280 | 40.780 |
| McKinley | +8,869 | +35.112 | +34.567 | +25.312 | +38.008 | 2.796 | 62.499 | 62.999 |
| Otero | -4,918 | -21.039 | -29.362 | -27.575 | -31.290 | 2.588 | 34.424 | 34.924 |
| Eddy | -10,796 | -47.447 | -52.627 | -56.570 | -58.759 | 2.519 | 21.220 | 21.720 |
| Chaves | -8,168 | -37.790 | -43.557 | -45.583 | -49.044 | 2.393 | 26.048 | 26.548 |
| Lea | -11,289 | -55.298 | -59.756 | -62.441 | -69.163 | 2.260 | 17.295 | 17.795 |
| Taos | +8,608 | +52.790 | +54.789 | +48.829 | +54.927 | 1.805 | 71.339 | 71.839 |
| Rio Arriba | +4,511 | +28.993 | +30.213 | +19.852 | +25.913 | 1.722 | 59.440 | 59.940 |
| Curry | -5,644 | -38.374 | -40.634 | -43.389 | -47.627 | 1.628 | 25.756 | 26.256 |
| Grant | +1,667 | +11.964 | +5.484 | +5.194 | +8.490 | 1.542 | 50.926 | 51.426 |
| Los Alamos | +3,396 | +28.006 | +18.108 | +31.249 | +24.550 | 1.342 | 58.946 | 59.446 |
| San Miguel | +4,020 | +36.969 | +37.599 | +28.495 | +40.210 | 1.204 | 63.428 | 63.928 |
| Lincoln | -3,436 | -34.443 | -41.799 | -39.188 | -42.456 | 1.104 | 27.722 | 28.222 |
| Cibola | +1,154 | +13.180 | +3.358 | +1.587 | +2.828 | 0.969 | 51.533 | 52.033 |
| Luna | -658 | -8.488 | -11.544 | -19.329 | -14.135 | 0.858 | 40.699 | 41.199 |
| Socorro | +339 | +4.796 | +2.097 | -3.795 | -0.640 | 0.783 | 47.341 | 47.841 |
| Torrance | -2,147 | -30.432 | -38.472 | -38.952 | -40.075 | 0.781 | 29.727 | 30.227 |
| Roosevelt | -2,608 | -40.061 | -43.494 | -44.060 | -49.015 | 0.721 | 24.913 | 25.413 |
| Sierra | -716 | -12.298 | -26.401 | -19.655 | -25.539 | 0.645 | 38.794 | 39.294 |
| Colfax | -325 | -5.665 | -13.048 | -14.346 | -13.956 | 0.635 | 42.111 | 42.611 |
| Quay | -1,232 | -34.413 | -35.374 | -41.793 | -44.754 | 0.396 | 27.737 | 28.237 |
| Mora | +666 | +27.773 | +27.252 | +17.517 | +31.126 | 0.265 | 58.830 | 59.330 |
| Catron | -1,061 | -46.312 | -51.453 | -50.839 | -52.037 | 0.254 | 21.787 | 22.287 |
| Guadalupe | +408 | +21.725 | +15.996 | +0.735 | +7.710 | 0.208 | 55.806 | 56.306 |
| Hidalgo | -195 | -11.048 | -15.278 | -23.577 | -17.255 | 0.195 | 39.419 | 39.919 |
| Union | -834 | -51.229 | -53.659 | -53.477 | -54.094 | 0.180 | 19.329 | 19.829 |
| De Baca | -317 | -37.163 | -48.241 | -51.813 | -54.434 | 0.094 | 26.362 | 26.862 |
| Harding | -144 | -34.286 | -36.948 | -39.765 | -36.919 | 0.046 | 27.800 | 28.300 |

At fixed positive county pair volume T_c, +1 A-share point changes net A−B by **0.02×T_c**: Bernalillo gains 6,094.76 net votes; these gains are saved for every county/native row where its pair volume is known. Share points, twice-as-large pair margin points, net votes and all-candidate margin points remain separate columns.

For pair volumes T_c and A shares s_c, `M=ΣT_c(2s_c−1)` and `T=ΣT_c`. The unbounded tie shift is `(B−A)/(2(A+B)) = −M/(2T)`. A+1 pair margin adds **0.5 share points**, with net target `0.01T`, not one vote. A one-point all-candidate margin would instead require `0.01V` net, where V includes held other candidates; the scenario files display the resulting all-candidate margin separately. With other candidates fixed, pair A/B target totals are `(T±target_net)/2`; all named candidate totals still sum to V and the full plurality leaders are checked.

Unbounded shifts are retained. Implementation clips `s_c+δ` to [0,1], then solves the common bounded δ by bisection; it does not clip and assume the original target still holds. Already-winning, impossible, unknown, invalid negative and no-positive-pool cases remain explicit. The primary county scenarios do not require clipping; native observed-universe and saved synthetic cases test it.

For a selected county only, with **all others fixed at their historical anchor shares (0 share-point adjustment)**, the requirement is `q_c=(T_c+gT−M_others)/(2T_c)`. Negative unbounded q is already secured even at q=0 under those assumptions; q>1 is impossible. Equality is a tie boundary. Unknown and zero pools are never divided through. The CLI allows a stated alternative shift in all other counties; its output records that assumption.

## Historical volume/mix and preference sensitivities

Low/base/high refer to **observed historical statewide contest volumes**, not a forecast range. Each county's volume V_c is the actual all-named-candidate total in 2022 governor (low), 2024 Senate (base), or 2024 president (high). The actual 2020 same-seat Senate mix is an additional context. Preference and participation anchors are independently selectable from all four contests: `p_c=(A_c+B_c)/all_candidates_c`, `T_c=V_c×p_c`, `s_c=A_c/(A_c+B_c)`. Every named other candidate retains its anchor county share of V_c. Thus changing volume/mix never silently assumes all governor/presidential voters participate in the Senate pair. Fractional scenario votes are expectations; historical counts remain integers. The [settings](data/baselines/settings.json) declare exactly these choices.

The following cases hold **2024 Heinrich–Domenici preferences/participation** fixed, so p_c=1. They isolate actual historical volume and county composition; no arbitrary ±10% turnout range is substituted. Uniformly scaling all county volumes alone would change net-vote magnitude, not tie share thresholds.

| Historical volume/mix | All-candidate volume | Pair volume | Fixed-share net A−B | Fixed-share margin pp | Tie A-share shift pp | A+1 A-share shift pp |
|---|---:|---:|---:|---:|---:|---:|
| low-2022-governor | 712,256 | 712,256.00 | +78,082.90 | +10.962757 | -5.481379 | -4.981379 |
| base-2024-senate | 903,311 | 903,311.00 | +91,355.00 | +10.113350 | -5.056675 | -4.556675 |
| high-2024-president | 923,403 | 923,403.00 | +92,359.60 | +10.002091 | -5.001045 | -4.501045 |
| context-2020-same-seat | 917,237 | 917,237.00 | +93,765.83 | +10.222639 | -5.111320 | -4.611320 |

All **32 state target cases** (4 volume mixes × 4 preference anchors × 2 targets) and 1,056 county rows are retained in [state scenarios](data/baselines/state-scenarios.json). Candidate effects, changes in party coalitions, lower preferences, 2026 participation, vote-method mix and remaining-vote behavior are not inferred from these anchors.

## Complete native source coverage and qualified priority

Every source row is retained, including each administrative privacy aggregate and literal asterisk. Native IDs unavailable in the CSV stay null; the identity is contest/source + county literal + precinct literal + source position. Source precinct labels may describe physical or administrative contexts; central/method identity and polygons cannot be assumed. No name/count join establishes cross-year or November 2026 equivalence. Complete candidate/control/source cells are in [50,179 field rows](data/baselines/candidate-fields.csv); [8,558 native baseline rows](data/baselines/native-baselines.csv) and [17,116 native target rows](data/baselines/native-targets.csv) keep unknown cases present.

| Contest | Native source rows | Voter Privacy administrative rows | Masked candidate cells | All masked numeric cells |
|---|---:|---:|---:|---:|
| 2024-senate | 2,201 | 33 | 30 | 36 |
| 2020-senate | 1,959 | 33 | 316 | 326 |
| 2022-governor | 2,196 | 33 | 668 | 671 |
| 2024-president | 2,202 | 33 | 9,408 | 9,408 |

The 2024 Senate export has **2,181 rows with both candidate cells numeric**, totaling **902,421**. Within that explicitly observed universe, top 15 supply **14,647/902,421 = 1.623078%**; the smallest source-position-tied descending prefix reaching 80% is **1,392 rows**, **722,113/902,421 = 80.019525%**, versus 721,760 at 1,391. These include numeric privacy aggregates and do not prove a certified physical/native priority. The remaining 20 source rows have protected candidate cells. **Certified native full order, top 15 and minimum80 are null; canonical dispatch keys are empty.** No county substitution is authorized.

Complete certified county sensitivity, kept separate, has 10 counties reaching **725,900/903,311 = 80.359920%**, versus 704,286 at nine; the top 15 supply 806,821/903,311 = 89.318186%. Every county and every source-native row remains in the inventory. [Priority contract](data/baselines/priority-contract.json) preserves the initial literal-label tie convention; [source-scoped orders](data/baselines/source-scoped-orders.json) separately use source-position ties for exact peer comparison. Both are descending and retain all remainders. Tied order positions differed in 178 places; values, membership and integer crossing totals did not change.

Native uniform tie/A+1 targets are solved only within each contest's **directly known positive A+B universe**. Its denominator/unknown and zero row counts are in [native state scenarios](data/baselines/native-state-scenarios.json). They are not whole-state estimates. Whole-state all-native uniform target shares remain null because protected preferences/volumes cannot establish the clipped solution. A selected known native unit can separately be tested against the published whole-state historical net with every other context collectively fixed, subtracting only that directly printed row; unknown selected-unit values stay null. No privacy pool or county residual is assigned to precincts. Cross-year native low/high mixes remain unmodeled because no verified native crosswalk exists.

Source pitfalls are material: Chaves precinct 47 has both Senate candidate cells `*` while printed total votes/ballots are 0; Curry Voter Privacy has both candidates and total votes `*`, but printed total ballots 2. Neither is an inferred candidate zero. Printed total fields can omit protected candidates, so a printed zero is not proof of no contest votes. Known-lane county residuals remain unallocated in [coverage controls](data/baselines/coverage-controls.json). Otero literal 18 exists in the 2024 presidential export (Harris 91, Trump 273), but is absent from Senate; missing Senate scope is not zero. The 2020 legacy headline 1,925 differs from the database's 1,926 nonprivacy contexts. No invented row repair or ID join is made.

## Ballots, registration, methods and source disagreements

The original [2020 turnout page](https://electionresults.sos.nm.gov/VoterTurnoutDetails.aspx?eid=2782), [2022 page](https://electionresults.sos.nm.gov/VoterTurnoutDetails.aspx?eid=2838) and [2024 page](https://electionresults.sos.nm.gov/VoterTurnoutDetails.aspx?eid=2882) and their linked county service report **928,230 / 714,754 / 928,290 Ballots Cast**, with **1,351,811 / 1,364,559 / 1,343,825 Eligible Voters** respectively. Complete HTML native counts are 1,925 / 2,163 / 2,169; all ballot/eligible fields and original county IDs are retained in [turnout controls](data/baselines/turnout-controls.json). These are separate source universes from the ElectionStats candidate rows, not automatically joinable or voting-eligible-population measures. The source's signed 2022 PCT 051 Eligible Voters value −3 is preserved and flagged, never repaired to zero.

Portal clocks are **11/24/2020 1:47 PM MT**, **11/29/2022 4:39 PM MT**, and **5/30/2025 10:44 AM MT**. Retrieval clocks are UTC. PDF run clocks and filing clocks have no stated timezone; none is silently converted. The database verifiedAt values retain their source `Z` suffix. [Clock objects](data/baselines/source-clocks.json) retain literals. No live cadence is established by these snapshots.

The PDF administrative method headers sum to **928,172** in 2020, **58 below** the portal ballot count, across seven county discrepancies (Cibola −2, Dona Ana −6, Grant −4, Hidalgo +2, Luna +1, Sandoval −48, Valencia −1). The two later PDF ballot headers match portal totals. The discrepancy is retained by source/vintage, not rescaled. Separate candidate methods below reconcile exactly to candidate totals; county/native candidate methods remain unavailable in these statewide summary sources. Administrative ballot methods are not candidate methods.

| Contest / candidate source label | Early | Absentee | Election Day | Candidate total |
|---|---:|---:|---:|---:|
| 2024-senate / Martin Heinrich | 285,829 | 83,877 | 127,627 | 497,333 |
| 2024-senate / Nella Louise Domenici | 258,327 | 31,364 | 116,287 | 405,978 |
| 2020-senate / Ben R. Lujan | 188,958 | 225,824 | 59,701 | 474,483 |
| 2020-senate / Mark V. Ronchetti | 252,200 | 92,079 | 74,204 | 418,483 |
| 2020-senate / Bob Walsh | 10,466 | 7,503 | 6,302 | 24,271 |
| 2022-governor / Michelle Lujan Grisham and Howie C. Morales | 184,438 | 69,304 | 116,426 | 370,168 |
| 2022-governor / Mark V. Ronchetti and Ant L. Thornton | 161,998 | 26,607 | 136,096 | 324,701 |
| 2022-governor / Karen Evette Bedonie and Efren Gallardo Jr. | 6,147 | 1,836 | 9,404 | 17,387 |
| 2024-president / Kamala D. Harris and Timothy Walz | 278,916 | 84,056 | 115,830 | 478,802 |
| 2024-president / Donald J. Trump and JD Vance | 265,101 | 30,031 | 128,259 | 423,391 |
| 2024-president / Robert F. Kennedy, Jr and Nicole Shanahan | 4,449 | 1,025 | 4,079 | 9,553 |
| 2024-president / Jill Stein and Rudolph Ware | 2,156 | 652 | 1,803 | 4,611 |
| 2024-president / Chase Oliver and Mike Ter Maat | 1,903 | 528 | 1,314 | 3,745 |
| 2024-president / Claudia De La Cruz and Karina Garcia | 1,032 | 315 | 1,095 | 2,442 |
| 2024-president / Laura Ebke and Trisha Butler | 380 | 117 | 362 | 859 |

These method vectors come directly from the linked original statewide candidate summaries above; [raw sections and rows](data/baselines/state-candidate-methods.json) retain each line. The legacy 2020/2022 CSVs independently agree and retain their native candidate/Race IDs, blank AreaNum and trailing cells. Blank AreaNum is statewide scope, not 33 missing county rows. The actual legacy 2024 election 2882 federal CSV is HTTP200 **header-only/unavailable**, not zero; ElectionStats CSV and original canvass restore the historical field. Document799's own embedded original remains403; the independently recovered SOS archive→RealFile table→public SDK GetWidgetFiles→literal PublicFiles canvass is a separate original, not claimed identical to799.

The original registration publications, [October31 statewide](https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/ee3072ab0d43456cb15a51f7d82c77a2/226d9a5e-df71-40e0-9d61-13468b7b457d/Statewide_10-31-2024.pdf), [October31 county/precinct](https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/ee3072ab0d43456cb15a51f7d82c77a2/2744ee55-8c95-47ac-9fef-8a2c5d076d2f/County_Precinct_10-31-2024.pdf), [November26 statewide](https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/ee3072ab0d43456cb15a51f7d82c77a2/923c8443-ebb6-4285-a80f-aea73cce0453/Statewide_11-26-2024.pdf) and [November26 county/precinct](https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/ee3072ab0d43456cb15a51f7d82c77a2/962abffd-6197-48ce-8c9a-1b846fc255a0/County_Precincts_11-26-2024.pdf), retain party stocks and literal source identities. State-table totals are **1,377,085** and **1,406,281**. The county-table total sums are **1,377,093** and **1,406,283**; native row totals sum **1,376,892** and **1,406,271**. These source disagreements remain explicit, including wrapped Hidalgo labels and blank party cells. Each vintage retains 2,168 native rows plus33county summaries and a separate grand total, without crosswalking these to election precincts. Active/inactive status is unstated in these tables; Eligible Voters and dated registration stocks have different dates/scopes and are never substituted for one another. [Registration controls](data/baselines/registration-controls.json), [native objects](data/baselines/registration-native-controls.json) and [all source disagreements](data/baselines/source-disagreements.json) preserve the details.

Embedded page `nVotes` and `nVotesParty1` lanes differ in 12 candidate/control objects across the four contests, including2024 Senate. They remain separate source fields; `nVotes`/CSV agrees with the canvass. No party-key deduplication or hidden residual reconstruction is performed. Blank/under/over/generic write-in controls and full native method partitions are unavailable in the admitted required-contest sources; a ballot-minus-candidate difference is not labeled an undervote.

## Offline live remainder calculator

[calculator.py](data/baselines/calculator.py) keeps counted A/B and **each named other candidate** fixed. Input `remaining` means remaining **valid all-candidate votes**, not all unprocessed ballots. Declare pair participation p and remaining A pair share q; pair pool U=remaining×p. A supplied other mix allocates remaining nonpair votes to named opponents, or the result stays unknown. Final pair denominator is `counted_A+counted_B+U`; final all-candidate denominator also includes counted and forecast others. Preference clipping applies only to forecast q; counted votes never move.

For final pair-margin g, the tie/cushion boundary is `q=[U+g×FINAL_PAIR_DENOMINATOR−(counted_A−counted_B)]/(2U)`. Outright plurality additionally requires A's final votes to exceed **every** named other opponent. The output separates these thresholds and full-field leaders; a pair success can still lose to C. Negative pools/invalid participation are rejected, unknown inputs remain unknown, and no-positive-pool cases use the fixed final count. [Fourteen saved synthetic live cases](data/baselines/live-synthetic-scenarios.json) include unknowns, no pool, negative, secured, impossible, both clipping directions, missing other mix, third-candidate victory and a +1 case using the correct final denominator. [Bounded historical arithmetic stress cases](data/baselines/bounded-synthetic-scenarios.json) test actual clipping and infeasible targets. These are arithmetic examples with no calibrated probability or inferred remaining vote pool.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/new-mexico/data/baselines/run_offline.py
python3 senate/2026/new-mexico/data/baselines/calculator.py --county Bernalillo --others-shift-pp 0 --target-margin-pp 0
python3 senate/2026/new-mexico/data/baselines/calculator.py --live-json /path/to/explicit-live-input.json
```

## Reconciliation and handoff

The bounded October20 calculator repair resolved actual malformed-input failures found by the coordinator: booleans accepted as numbers, malformed/null containers reaching iteration, nonfinite values reaching arithmetic/strict JSON serialization, nonfinite CLI parameters, and unknown county lookup. Validation now precedes arithmetic on every live, uniform and selected-unit surface. Invalid requests return strict JSON with safe field/reason information and `final:null`, without echoing nonfinite input or producing a traceback. Numeric booleans, malformed numeric nulls/text, nonfinite values, negative counts/pools, invalid participation/target bounds, malformed named-other mappings/keys, bad mix normalization, duplicate supplied unit identities and unrepresentable derived results are rejected. Finite live preference clipping and intended unknown remaining/preference/volume cases remain supported. External CLI targets and other-unit shifts must be finite and within [−100,+100] percentage points; internal finite out-of-feasible-range mathematical stress targets retain their documented impossible status.

All **132 actual subprocess regressions** pass: **97 negative** and **35 positive**, including the21exact supplied cases and all16previously failing cases. Exact old failing calculator/stdout/stderr/fixture/finding bytes, all103priorowned bodies and the prior manifest were losslessly frozen **before mutation** in [repair history](data/baselines/repair-history/pre-input-validation-v1/freeze.json), SHA256 `b0291453d6b01926e9ea05a6276c863c2fcf59d226890456e4660d377f97af48`; all64original-source bodies are reused read-only by their exact references. The old manifest hash `b7889d8a9b68cfc4dbca9beed0ef1b8400a7bcbeca6b0bb97796da15ce52173b` identifies only that prior handoff. [Regression transcripts](data/baselines/repair-regressions/results.json) retain exact fixture/output hashes and exit codes; [historical invariance](data/baselines/repair-regressions/historical-invariance.json) checks unchanged source/count/mask/native/target bytes and valid prior live outputs. [Final seal metadata](data/baselines/final-seal.json) pins validation/regression/history before the manifest is written, without a reverse current-manifest hash cycle. The turnout reciprocal review concerns an immutable **pre-repair source core only** and excludes calculators, scenarios, this report, later manifests and future-byte equality. No peer was contacted or restarted for this repair; no source was expanded. Current/legal/geographic/feed/forecast/publication approvals remain false.

The actual original-first turnout peer **5f787f59-e6ff-4494-b416-a0fb4383237f** was finished at launch and was never contacted/restarted. My [independent-first pin](data/baselines/source/independent-first-pin.json), SHA256 `6770ae96313d9f9d2e0964da2470fd903d1f72122e260eece7635370aca014b7`, predates reading its derivatives. Its witness-v2 SHA256 is `427ad9e10b16e85cc675f6479796f09813afa5a72845b1199d4dd6b4e8ae7c51`. An immutable captured core is retained under [peer freeze](data/baselines/source/peer-freeze/capture.json). Independent comparison passed **376,717 checks**, including all source cells/positions/metadata, candidate methods, PDF county vectors, native turnout/registration fields, all18source-scoped full orders and exact integer80 crossings. Registration header alignment and wrapped-label parsing were repaired against original text; originals were unchanged. This is equality to the captured core only, not a claim about later final peer bytes or coordinator acceptance. [Bounded reconciliation](data/baselines/peer-reconciliation.json) states that limit. Coordinator alone accepts any dispatch contract.

[SCHEMA and reproduction contract](data/baselines/source/SCHEMA.md), [offline validation](data/baselines/validation.json), [asset manifest](data/baselines/asset-manifest.json) and [source receipts](data/baselines/source/original-references.json) cover the owned report/data, complete originals by exact shared content-addressed references, raw/stored hashes/bytes, request/final URLs, redirects and UTC retrieval. No dependency/cache directories are retained; every stored artifact is strictly below40,000,000 bytes. Report links and generated bounds are audited. The manifest excludes its own bytes to avoid a hash cycle; validation is sealed before the manifest.

Material limits are protected native values and exact certified native priority; unmatched/varying historical source universes; the disclosed2020ballot/registration/source-lane discrepancies; unavailable native candidate methods and blank/under/over/write-in controls; unapproved2026native identities/geometry; final ballot/result-ID mapping; current remaining-vote assumptions and probability calibration. These remain explicit gaps, not reasons to invent data or defer the completed conditional research.

