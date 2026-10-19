# Colorado historical partisanship and conditional paths

Original-source research and offline arithmetic, observed October 19, 2026. **Historical extraction and frozen reciprocal checks pass; coordinator acceptance remains pending.** All 64 counties and all 3,199/3,232/3,205 native contexts remain in the calculations. Historical turnout anchors are not 2026 projections; these scenarios supply no calibrated win probability.

The November 3, 2026 regular election fills **Class II**, the Hickenlooper seat last elected on November 3, 2020. The November 8, 2022 Bennet–O’Dea contest is the other **Class III** seat and an actual midterm. Colorado held **no 2024 Senate election**; November 5, 2024 president is the priority basis. The original historical events and complete abstracts establish the three separate electorates. [Class II roster](https://www.senate.gov/senators/Class_II.htm), [Class III roster](https://www.senate.gov/senators/Class_III.htm), [2026 calendar](https://www.sos.state.co.us/pubs/elections/calendars/2026ElectionCalendar.pdf), [2024 abstract](https://www.coloradosos.gov/pubs/elections/Results/2024/2024BiennialAbstract.pdf), [2022 Senate](https://www.sos.state.co.us/pubs/elections/Results/Abstract/2022/general/usSenator.html), [2020 signed original](https://web.archive.org/web/20201214192735id_/https://www.sos.state.co.us/pubs/elections/Results/2020/StateAbstractCertAndReportSigned.pdf).

## Historical outcomes and denominators

A and B always mean the **named pair**, not every candidate with the same party label. The complete candidate fields below and in [county-baselines.csv](data/county-baselines.csv) preserve Libertarian, independent, unaffiliated, minor-party and named write-in identities. No non-Republican coalition is inferred. Brian Anthony Perry/Mark Sbani’s two Democratic-labeled presidential votes remain outside the Harris/Trump pair. Each contest is one general-election tally; no primary electorate, runoff, ranked-choice stage or transfer preference is combined with it. [Official public downloads](https://historicalelectiondata.coloradosos.gov/contest/26499), [2022](https://historicalelectiondata.coloradosos.gov/contest/25990), [2020](https://historicalelectiondata.coloradosos.gov/contest/3602).

| Year | Named A / B | A | B | Other named | All candidates | Pair votes | A pair % | Pair margin pp | All-candidate margin pp |
|---|---|---|---|---|---|---|---|---|---|
| 2024 | Kamala D. Harris and Tim Walz / Donald J. Trump and JD Vance | 1,728,159 | 1,377,441 | 87,145 | 3,192,745 | 3,105,600 | 55.646542 | 11.293083 | 10.984842 |
| 2022 | Michael Bennet / Joe O'Dea | 1,397,170 | 1,031,693 | 71,338 | 2,500,201 | 2,428,863 | 57.523623 | 15.047246 | 14.617905 |
| 2020 | John W. Hickenlooper / Cory Gardner | 1,731,114 | 1,429,492 | 75,184 | 3,235,790 | 3,160,606 | 54.771585 | 9.543170 | 9.321433 |

| Year | Native contexts | Administrative ballots | Active voters | Registered voters | Ballots minus named candidate votes |
|---|---|---|---|---|---|
| 2024 | 3,199 | 3,241,155 | 4,074,612 | 4,583,280 | 48,410 |
| 2022 | 3,232 | 2,543,316 | 3,839,814 | 4,355,778 | 43,115 |
| 2020 | 3,205 | 3,291,661 | 3,803,765 | 4,211,531 | 55,871 |

Administrative ballot/registration controls reconcile all counties to their official statewide footers. Registration describes historical source populations, not voting-eligible population or present registration; a uniform extraction date is unprinted. The ballot-minus-candidate differences are unclassified gaps, not observed undervotes, overvotes, blanks or remaining votes. Separate blank/under/over and generic invalid/unqualified write-in counts remain unknown. The source CSV’s “Total Ballots Cast” duplicates candidate votes in every row despite hasBallots=false, and is rejected as a participation denominator. [2024 turnout original](https://www.sos.state.co.us/pubs/elections/Results/2024/2024GeneralPrecinctVoterTurnout.xlsx), [2022 turnout tables](https://www.sos.state.co.us/pubs/elections/Results/Abstract/2022/general/turnout.html), [2020 booklet](https://web.archive.org/web/20221201025617id_/https://www.coloradosos.gov/pubs/elections/Results/Abstract/2020/2020BiennialAbstractBooklet.pdf). See [all original control positions](data/baselines/extracts/turnout-control-positions.jsonl.gz).

Complete statewide candidate universe, in **literal CSV column order**. “WI” is the abstract’s explicit named Write-In marker, not an inferred legal roster. Every candidate/county/native count and raw party object survives in the [long extract](data/baselines/extracts/all-candidate-votes.csv.gz) and [full SSR objects](data/baselines/source/historical-page-props.json). The independent controls are 896 PDF county/candidate cells for 2024, 576 HTML cells for 2022 and 512 signed/booklet PDF cells for 2020. [2024 PDF pages106–110](https://www.coloradosos.gov/pubs/elections/Results/2024/2024BiennialAbstract.pdf#page=106), [2022 original HTML](https://www.sos.state.co.us/pubs/elections/Results/Abstract/2022/general/usSenator.html), [2020 PDF pages106–107](https://web.archive.org/web/20221201025617id_/https://www.coloradosos.gov/pubs/elections/Results/Abstract/2020/2020BiennialAbstractBooklet.pdf#page=106).

| Year | Source candidate/ticket | CSV party label | Votes | Abstract marker | App isWriteIn |
|---|---|---|---|---|---|
| 2024 | Kamala D. Harris and Tim Walz | Democratic | 1,728,159 | unmarked | False |
| 2024 | Donald J. Trump and JD Vance | Republican | 1,377,441 | unmarked | False |
| 2024 | Robert F. Kennedy, Jr and Nicole Shanahan | Unaffiliated | 35,623 | unmarked | False |
| 2024 | Chase Russell Oliver and Mike Ter Maat | Libertarian | 21,439 | unmarked | False |
| 2024 | Jill Stein and Rudolph Ware | Green | 17,344 | unmarked | False |
| 2024 | Cornel West and Melina Abdullah | Unity Party of Colorado | 5,149 | unmarked | False |
| 2024 | Randall Terry and Stephen E. Broden | American Constitution | 3,522 | unmarked | False |
| 2024 | Blake Huber and Andrea Denault | Approval Voting | 2,196 | unmarked | False |
| 2024 | Peter Sonski and Lauren Onak | American Solidarity | 910 | WI | False |
| 2024 | Claudia De la Cruz and Karina Garcia | Socialist Labor | 905 | WI | False |
| 2024 | Chris Garrity and Cody Ballard | No Party Affiliation | 30 | WI | False |
| 2024 | Shiva Ayyadurai and Crystal Ellis | Independent | 15 | WI | False |
| 2024 | Bill Frankel and Steve Jenkins | Unaffiliated/Republican | 10 | WI | False |
| 2024 | Brian Anthony Perry and Mark Sbani | Democratic | 2 | WI | False |
| 2022 | Michael Bennet | Democratic | 1,397,170 | unmarked | False |
| 2022 | Joe O'Dea | Republican | 1,031,693 | unmarked | False |
| 2022 | Brian Peotter | Libertarian | 43,534 | unmarked | False |
| 2022 | T.J. Cole | Unity Party of Colorado | 16,379 | unmarked | False |
| 2022 | Frank Atwood | Approval Voting | 11,354 | unmarked | False |
| 2022 | Tom Harvey | Unaffiliated | 29 | WI | True |
| 2022 | Joanne Rock | Unaffiliated | 25 | WI | True |
| 2022 | John Carleton Rutledge | Libertarian | 9 | WI | True |
| 2022 | Robert Messman | Unaffiliated | 8 | unmarked | True |
| 2020 | John W. Hickenlooper | Democratic | 1,731,114 | unmarked | False |
| 2020 | Cory Gardner | Republican | 1,429,492 | unmarked | False |
| 2020 | Raymon Anthony Doane | Libertarian | 56,262 | unmarked | False |
| 2020 | Daniel Doyle | Approval Voting | 9,820 | unmarked | False |
| 2020 | Stephan "Seku" Evans | Unity Party of Colorado | 8,971 | unmarked | False |
| 2020 | Bruce Lohmiller | Green | 71 | WI | False |
| 2020 | Danny Skelly | Unaffiliated | 55 | WI | False |
| 2020 | Michael Sanchez | Unaffiliated | 5 | WI | False |

All 2020/2024 app write-in flags are false, including explicitly marked abstract columns. Robert Messman’s 2022 app flag is true while its original HTML header is unmarked. These disagreements remain in [candidate-presentation.json](data/baselines/source/candidate-presentation.json); none changes a count. The current 2020 index wrongly prints November 6 and omits federal links; exact original routes returned 404. Actual CDX-listed complete archived originals repair access: signed certificate December 8, 2020 for the November 3 election, with all 512 Senate county cells independently agreeing to the booklet. Capture/HTTP/PDF/client clocks are separate. [Current historical index](https://www.sos.state.co.us/pubs/elections/Results/Abstract/2020/general/index.html), [retained discovery/failed-response metadata](data/baselines/source/discovery-evidence.json).

## Complete geography and exact priority

The disjoint priority denominator is **3,192,745 named presidential candidate votes**, including six explicitly printed named write-in tickets. Top 15 native contexts supply 39,005 (1.221676%). The exact smallest 80% prefix has **1,992 contexts / 2,554,233 votes (80.001159%)**; 1,991 supply 2,553,363 and fail. Summit `2081359007` adds 870 at the crossing. The other **1,207 contexts / 638,512 votes** remain in every statewide calculation. Ranking is descending integer full-candidate votes, then literal `CO|year|contest_id|county_literal|native_id_literal` ascending. [Original 2024 download page](https://historicalelectiondata.coloradosos.gov/contest/26499), [full order](data/baselines/native-order.csv), [provisional contract](data/baselines/priority-contract.json).

The [three full native orders](data/baselines/historical-orders.json) and [all county→native maps](data/baselines/native-hierarchy.json) retain all 9,636 historical contexts and all 64 parents per year. “Precinct” is the source reporting label. Ballot styles, central mail groups, polling sites, vote centers, municipal parents and VTD polygons are not silently equated. All three originals lack vote-channel splits; method is null, not zero mail or zero in-person. County mail processing remains county-administered, not allocated from inferred precinct preferences. Historical IDs/names/counts alone establish no cross-year or November 2026 identity/geometry. [Source objects and flags](data/baselines/source/historical-page-props.json).

The 2024 turnout workbook supplies 3,183 county/native records and 1,043,548 G-only cached #VALUE! tail cells, which are not geography. Sixteen additional candidate-CSV rows contain literal zero candidate vectors and unavailable statistics. Weld’s trailing-space county literal is retained, with an explicit comparison-only alias. Montezuma rows2632/2633 contain shared strings `101*/9*/110*/194*` and `2868*/349*/3217*/1700*`, not absent counts. Annotated-inclusive ballots total 3,241,155; plain-numeric known ballots are 3,239,261. The relocation footnote says voters moved between precincts6/7 to correct a missing school-district question; no candidate counts or identity are reallocated. Eighteen unvalued inactive cells stay null. [Whole original XLSX](https://www.sos.state.co.us/pubs/elections/Results/2024/2024GeneralPrecinctVoterTurnout.xlsx), [sparse source cells](data/baselines/extracts/turnout-original-cells.jsonl.gz), [footnote/lanes/tail](data/baselines/extracts/turnout-lanes.json).

Independent frozen reciprocal QA checks 917,624 fields/positions against exact captured turnout peer bodies: original rows, full candidate/SSR/pseudocandidate objects, method/nulls, administrative controls, annotations, all three orders and exact80 agree. County/state control-key syntax differs (195 controls); this extract retains 18 empty XML cells omitted from the peer’s valued-cell derivative, with identical original workbook bytes. [Frozen receipt](data/baselines/peer-comparison/stable-v1/receipt.json), [reconciliation](data/baselines/peer-comparison/reconciliation.json). Later peer artifact changes are separately hashed observations, not retroactive equality. Formal contract acceptance belongs to the coordinator.

## Tie, cushion and historical sensitivity

For pair weights w and A pair shares s, T=Σw and M=Σw(2s−1). The unbounded tie share shift is **−M/(2T)=(B−A)/(2(A+B))**. A+1 means a **one percentage-point A-minus-B pair margin**, requiring another **0.5 A-share points** in the unbounded solve. A +1 A-share point changes pair margin by +2 points and contributes .02w net votes at fixed weight. All-candidate margin uses T+O instead, so its cushion differs. The saved targets solve Σw[2clip(s+δ,0,1)−1]=gT by bounded bisection; original unbounded shifts remain visible. Negative shifts are valid: every named Democratic pair already won its historical contest. Tie is a benchmark, not a win. [Calculator](data/baselines/calculate.py), [settings](data/baselines/scenario-settings.json), [state scenarios](data/baselines/state-scenarios.csv).

| Own-year anchor | A−B net | Tie A-share shift pp | A+1 A-share shift pp | A+1 net cushion | A+1 all-candidate margin pp |
|---|---|---|---|---|---|
| 2024 | 350,718 | -5.646542 | -5.146542 | 31,056.00 | 0.972705 |
| 2022 | 365,477 | -7.523623 | -7.023623 | 24,288.63 | 0.971467 |
| 2020 | 301,622 | -4.771585 | -4.271585 | 31,606.06 | 0.976765 |

Low/base/high are observed **2022/2024/2020 county pair volumes and mixes**: 2,428,863 / 3,105,600 / 3,160,606 pair votes, respectively. The corresponding all-candidate denominators are 2,500,201 / 3,192,745 / 3,235,790. Each of three preference anchors is crossed with all three volume anchors. Other participation is the volume-year county source count; no 2026 candidate effect, minor-party preference, transfer or reporting-order effect is inferred. These joint historical volume/mix changes are explicit sensitivity assumptions. Uniformly scaling all weights alone changes net votes and +1-share gain, while leaving shares and tie shifts unchanged. [Official historical contest pages](https://historicalelectiondata.coloradosos.gov/contest/26499), [2022](https://historicalelectiondata.coloradosos.gov/contest/25990), [2020](https://historicalelectiondata.coloradosos.gov/contest/3602).

| Preference anchor | Historical volume/mix | Pair votes | Fixed-share pair margin pp | Tie share shift pp | A+1 share shift pp |
|---|---|---|---|---|---|
| 2024 | low 2022 | 2,428,863 | 11.947032 | -5.973516 | -5.473516 |
| 2024 | base 2024 | 3,105,600 | 11.293083 | -5.646542 | -5.146542 |
| 2024 | high 2020 | 3,160,606 | 12.284048 | -6.142024 | -5.642024 |
| 2022 | low 2022 | 2,428,863 | 15.047246 | -7.523623 | -7.023623 |
| 2022 | base 2024 | 3,105,600 | 14.434271 | -7.217135 | -6.717135 |
| 2022 | high 2020 | 3,160,606 | 15.470118 | -7.735059 | -7.235059 |
| 2020 | low 2022 | 2,428,863 | 9.047507 | -4.523754 | -4.023754 |
| 2020 | base 2024 | 3,105,600 | 8.473459 | -4.236729 | -3.736729 |
| 2020 | high 2020 | 3,160,606 | 9.543170 | -4.771585 | -4.271585 |

Native sensitivity retains each preference year’s complete native universe and fixed within-county native pair fractions, then distributes the selected historical county pair volume by those fractions. Other counts use the analogous within-county other fractions. This is a conditional weighting construction, not a cross-year native join. All 57,816 native target rows retain weights, participation, local tie/A+1 targets, clipped statewide targets, net gains and selected-only solves; all 1,152 county target rows do likewise. [Native targets](data/baselines/native-targets.csv.gz), [county targets](data/baselines/county-targets.csv), [settings](data/baselines/scenario-settings.json).

| Native anchor | Target pair margin pp | Unbounded share shift pp | Bounded share shift pp | Clipped units | Achieved net |
|---|---|---|---|---|---|
| 2024 | 0 | -5.646541731 | -5.646671941 | 4 | 0.00000 |
| 2024 | 1.0 | -5.146541731 | -5.146634748 | 4 | 31,056.00000 |
| 2022 | 0 | -7.523623193 | -7.523793054 | 3 | -0.00000 |
| 2022 | 1.0 | -7.023623193 | -7.023770821 | 3 | 24,288.63000 |
| 2020 | 0 | -4.771584943 | -4.771691080 | 2 | 0.00000 |
| 2020 | 1.0 | -4.271584943 | -4.271656749 | 2 | 31,606.06000 |

Clipping changes the exact native thresholds: a constant unbounded shift would push several sparse Republican-heavy units below 0% A. Their shares are explicitly held at zero while the bounded solve adjusts every other positive-pool unit. Zero-pair contexts remain present with unknown share/no-positive-pool status. Bounded and unbounded shifts are therefore separate outputs, and the bounded tie-to-A+1 separation need not be exactly0.5 points. [Complete native target rows](data/baselines/native-targets.csv.gz), [bounded edge cases](data/baselines/bounded-scenarios.json).

## All 64 county contributions

This display uses 2024 preferences and 2024 actual pair weights. Margins in the first three columns use their own named pairs and pair denominators. Tie share is the statewide uniform benchmark. “Only county tie %” holds **every other county at its unshifted 2024 share and actual pair volume**, then solves this county alone; S means already secured even at0%, I means impossible even at100%. Those conditional targets are not independent necessities. Full counts, all-candidate denominators, participation and other scenarios remain in the linked data. [Primary 2024 source](https://historicalelectiondata.coloradosos.gov/contest/26499), [2022](https://historicalelectiondata.coloradosos.gov/contest/25990), [2020](https://historicalelectiondata.coloradosos.gov/contest/3602).

| County | 2020 margin pp | 2022 margin pp | 2024 margin pp | 2024 A pair % | Pair weight % | Net contribution | Net gain/+1share pp | State tie A % | Only county tie % |
|---|---|---|---|---|---|---|---|---|---|
| Adams | 14.02 | 17.46 | 9.26 | 54.631 | 7.312 | 21,032 | 4,541.60 | 48.984 | S |
| Alamosa | -0.88 | 4.62 | -11.14 | 44.432 | 0.235 | -813 | 146.02 | 38.786 | S |
| Arapahoe | 19.76 | 23.39 | 20.70 | 60.349 | 10.176 | 65,414 | 6,320.72 | 54.703 | 4.862 |
| Archuleta | -18.53 | -8.91 | -14.40 | 42.798 | 0.294 | -1,314 | 182.44 | 37.151 | S |
| Baca | -69.32 | -55.68 | -71.95 | 14.023 | 0.063 | -1,411 | 39.22 | 8.377 | S |
| Bent | -35.89 | -26.61 | -39.75 | 30.126 | 0.069 | -851 | 42.82 | 24.480 | S |
| Boulder | 53.12 | 58.22 | 57.30 | 78.650 | 6.147 | 109,391 | 3,818.14 | 73.004 | S |
| Broomfield | 21.17 | 29.08 | 29.35 | 64.677 | 1.465 | 13,355 | 909.94 | 59.030 | S |
| Chaffee | 4.54 | 15.30 | 13.96 | 56.980 | 0.452 | 1,958 | 280.52 | 51.333 | S |
| Cheyenne | -78.64 | -72.82 | -79.19 | 10.405 | 0.033 | -822 | 20.76 | 4.758 | S |
| Clear Creek | 10.41 | 18.50 | 17.11 | 58.553 | 0.190 | 1,012 | 118.32 | 52.907 | S |
| Conejos | -6.35 | -1.04 | -18.34 | 40.828 | 0.128 | -731 | 79.70 | 35.182 | S |
| Costilla | 29.62 | 36.29 | 15.21 | 57.606 | 0.065 | 305 | 40.10 | 51.959 | S |
| Crowley | -45.91 | -32.55 | -48.94 | 25.529 | 0.053 | -809 | 33.06 | 19.883 | S |
| Custer | -39.74 | -33.12 | -36.99 | 31.504 | 0.121 | -1,395 | 75.42 | 25.857 | S |
| Delta | -38.95 | -29.42 | -36.45 | 31.774 | 0.611 | -6,918 | 379.56 | 26.127 | S |
| Denver | 58.44 | 63.16 | 57.69 | 78.844 | 11.379 | 203,869 | 7,067.98 | 73.197 | 29.223 |
| Dolores | -51.78 | -42.41 | -53.60 | 23.198 | 0.045 | -751 | 28.02 | 17.551 | S |
| Douglas | -14.28 | -8.49 | -7.17 | 46.417 | 7.659 | -17,043 | 4,757.18 | 40.771 | S |
| Eagle | 26.73 | 28.45 | 25.08 | 62.541 | 0.872 | 6,795 | 541.82 | 56.895 | S |
| El Paso | -16.46 | -9.48 | -10.08 | 44.962 | 11.931 | -37,336 | 7,410.60 | 39.315 | S |
| Elbert | -54.22 | -51.35 | -52.27 | 23.867 | 0.643 | -10,441 | 399.54 | 18.221 | S |
| Fremont | -41.58 | -28.73 | -39.40 | 30.299 | 0.800 | -9,787 | 496.78 | 24.653 | S |
| Garfield | -0.09 | 7.82 | 2.14 | 51.072 | 0.954 | 635 | 592.42 | 45.425 | S |
| Gilpin | 7.80 | 16.04 | 13.18 | 56.591 | 0.128 | 525 | 79.66 | 50.944 | S |
| Grand | -5.14 | 1.14 | -0.83 | 49.587 | 0.308 | -79 | 191.30 | 43.940 | S |
| Gunnison | 27.01 | 34.70 | 30.24 | 65.119 | 0.341 | 3,198 | 211.52 | 59.473 | S |
| Hinsdale | -19.87 | -9.90 | -12.73 | 43.633 | 0.019 | -75 | 11.78 | 37.987 | S |
| Huerfano | -1.96 | 8.23 | -8.84 | 45.581 | 0.139 | -381 | 86.22 | 39.935 | S |
| Jackson | -61.32 | -53.32 | -57.13 | 21.437 | 0.026 | -461 | 16.14 | 15.791 | S |
| Jefferson | 14.19 | 20.66 | 20.03 | 60.013 | 11.314 | 70,370 | 7,027.60 | 54.367 | 10.108 |
| Kiowa | -78.77 | -66.76 | -75.89 | 12.057 | 0.027 | -642 | 16.92 | 6.410 | S |
| Kit Carson | -66.65 | -63.87 | -69.44 | 15.279 | 0.117 | -2,527 | 72.78 | 9.632 | S |
| La Plata | 14.71 | 22.39 | 19.17 | 59.586 | 1.117 | 6,653 | 694.02 | 53.940 | S |
| Lake | 20.64 | 25.88 | 17.09 | 58.546 | 0.121 | 642 | 75.12 | 52.900 | S |
| Larimer | 10.35 | 18.17 | 18.12 | 59.061 | 7.054 | 39,696 | 4,381.12 | 53.414 | S |
| Las Animas | -9.16 | 1.94 | -13.83 | 43.083 | 0.245 | -1,052 | 152.08 | 37.436 | S |
| Lincoln | -66.29 | -60.40 | -65.74 | 17.129 | 0.081 | -1,658 | 50.44 | 11.483 | S |
| Logan | -58.83 | -50.74 | -57.84 | 21.079 | 0.320 | -5,757 | 199.06 | 15.433 | S |
| Mesa | -32.01 | -18.49 | -24.90 | 37.549 | 2.879 | -22,266 | 1,788.24 | 31.902 | S |
| Mineral | -18.27 | -8.69 | -13.62 | 43.188 | 0.024 | -100 | 14.68 | 37.541 | S |
| Moffat | -66.39 | -59.03 | -64.23 | 17.885 | 0.210 | -4,191 | 130.50 | 12.239 | S |
| Montezuma | -25.22 | -15.69 | -21.53 | 39.235 | 0.475 | -3,179 | 295.30 | 33.588 | S |
| Montrose | -39.74 | -27.99 | -33.32 | 33.339 | 0.807 | -8,350 | 501.16 | 27.692 | S |
| Morgan | -43.19 | -43.06 | -49.84 | 25.082 | 0.422 | -6,539 | 262.42 | 19.435 | S |
| Otero | -25.14 | -12.92 | -27.13 | 36.435 | 0.280 | -2,356 | 173.68 | 30.788 | S |
| Ouray | 17.10 | 23.89 | 21.64 | 60.822 | 0.129 | 869 | 80.30 | 55.175 | S |
| Park | -19.33 | -12.01 | -17.03 | 41.486 | 0.376 | -1,987 | 233.38 | 35.839 | S |
| Phillips | -62.10 | -57.96 | -64.17 | 17.913 | 0.074 | -1,476 | 46.00 | 12.267 | S |
| Pitkin | 49.81 | 51.66 | 45.22 | 72.611 | 0.352 | 4,940 | 218.48 | 66.964 | S |
| Prowers | -46.86 | -43.22 | -51.50 | 24.249 | 0.163 | -2,606 | 101.20 | 18.602 | S |
| Pueblo | 0.82 | 9.36 | -5.25 | 47.374 | 2.673 | -4,360 | 1,660.32 | 41.727 | S |
| Rio Blanco | -70.56 | -63.99 | -64.86 | 17.572 | 0.117 | -2,351 | 72.50 | 11.926 | S |
| Rio Grande | -18.46 | -10.27 | -23.76 | 38.122 | 0.195 | -1,437 | 120.98 | 32.475 | S |
| Routt | 24.35 | 28.74 | 28.53 | 64.266 | 0.511 | 4,532 | 317.68 | 58.619 | S |
| Saguache | 14.64 | 19.15 | 3.87 | 51.935 | 0.106 | 127 | 65.62 | 46.289 | S |
| San Juan | 22.62 | 36.19 | 33.33 | 66.667 | 0.018 | 188 | 11.28 | 61.020 | S |
| San Miguel | 51.26 | 55.58 | 50.72 | 75.358 | 0.151 | 2,375 | 93.66 | 69.711 | S |
| Sedgwick | -55.02 | -44.75 | -57.48 | 21.262 | 0.043 | -765 | 26.62 | 15.616 | S |
| Summit | 35.34 | 39.50 | 38.33 | 69.164 | 0.548 | 6,518 | 340.12 | 63.517 | S |
| Teller | -38.35 | -31.16 | -36.37 | 31.813 | 0.513 | -5,791 | 318.42 | 26.167 | S |
| Washington | -76.65 | -69.97 | -76.20 | 11.899 | 0.089 | -2,107 | 55.30 | 6.252 | S |
| Weld | -21.94 | -19.26 | -21.53 | 39.237 | 5.642 | -37,717 | 3,504.42 | 33.591 | S |
| Yuma | -73.52 | -61.32 | -66.79 | 16.605 | 0.147 | -3,049 | 91.30 | 10.958 | S |

For selected unit c, q=[w_c+gT−Σ_other w_j(2s_j−1)]/(2w_c). The saved raw q remains unbounded; clipped display and statuses preserve already-secured, impossible and no-positive-pool cases. Every other unit stays at the explicit baseline assumption shown in settings. Integer one-net-vote cushions are distinct from A+1 percentage-point margins; expected fractional scenario counts are not rounded into fabricated official votes. A sufficient pair+1 result also needs A above each other candidate. Saved state scenarios include A minus all other votes combined as a conservative sufficiency check, not a claim that “other” is one party.

## Current ballot, counting rules and conditional live remainder

The **final official 2026 list**, certified September4 and updated September15 at11:09AM, supplies these nine Senate records. HTML and its linked complete XLSX independently agree. Printed candidates are N; Y identifies certified write-ins absent from printed candidate choices. None is stricken through in this captured Senate section. No historical or primary candidate ID becomes a November live ID. [Final official list](https://www.sos.state.co.us/pubs/elections/vote/generalCandidates.html), [official spreadsheet](https://www.sos.state.co.us/pubs/elections/vote/files/2026/2026GeneralCandidateListOfficial.xlsx), [retained roster](data/baselines/source/current-senate-roster.json).

| Name | Party as printed | Write-in? |
|---|---|---|
| Mark Baisley | Republican Party | N |
| John Hickenlooper | Democratic Party | N |
| Bob Chew | Forward Party | N |
| Christopher Baum | Approval Voting Party | N |
| Blake Huber | Libertarian Party | N |
| Adam Withrow | Unity Party | N |
| Donald Willoughby | Unaffiliated | Y |
| Will Powers | Republican Party | Y |
| Ryan Apelbaum | Republican Party | Y |

The legal Senate outcome is the highest vote total across all legal candidates. A highest-vote tie, after recounts, is resolved by lot; 50% of a selected pair is not a legal multi-candidate win threshold. The calculator checks named plurality when the whole conditional named field is supplied and otherwise leaves that outcome unknown. [Current2026 Title1, §1-11-101(2) and §1-10-105](https://olls.info/crs/crs2026-title-01.htm), linked authority from [SOS law index](https://www.sos.state.co.us/pubs/elections/lawsRulesResources.html).

Ordinary mail ballots must reach the clerk by7PM Election Day; a postmark is insufficient. County drop-box collection, receipt/SCORE credit, signature review, acceptance, opening, tabulation and publication are separate stages. Timely intercounty receipt is preserved under Rule7.4.10. The actual2026 calendar and current clerks guidance show **November12** for cure and eligible mailed military/overseas receipt, with a Veterans Day holiday adjustment; cure is11:59PM Mountain, mailed UOCAVA close of business. A raw “eight days” calculation would land on November11. [Mail FAQ](https://www.sos.state.co.us/pubs/elections/FAQs/mailBallotsFAQ.html), [rules effective10/09/2026](https://www.sos.state.co.us/pubs/rule_making/CurrentRules/8CCR1505-1/ElectionRules.pdf), [actual calendar](https://www.sos.state.co.us/pubs/elections/calendars/2026ElectionCalendar.pdf), [current clerks guidance](https://www.clerkandrecorder.org/2026-general-election).

Preserve a presentation disagreement: the current clerks page states an Election Day7PM receipt cutoff for electronic UOCAVA returns; current Title1 §§1-8.3-111/-113 describes timely submission and eighth-day receipt. The calendar also has literal typography/date defects, retained in the original. No electronic or other numeric live pool is inferred from these statements. The September14,2026 Supreme Court order **denied** the application to stay the USPS-rule preliminary injunction; an earlier August release alone would miss that later order. This order establishes no new Colorado arrival cutoff. [Current statute](https://olls.info/crs/crs2026-title-01.htm), [current clerks page](https://www.clerkandrecorder.org/2026-general-election), [actual Sept14 order26A305](https://www.supremecourt.gov/opinions/25pdf/26a305_4g15.pdf), [retained legal positions and qualifications](data/baselines/source/presentation-qualifications.json).

No actual outstanding-vote estimate is supplied. Issued-minus-returned, registration-minus-ballots and precincts-reporting percentages do not identify uncounted valid candidate votes. A live input must state its source/time/category/acceptance status and a conditional remaining candidate pool, keeping counted A/B and **each named other candidate** fixed. Ballot pool→contest participation and other-candidate participation require separate explicit assumptions. [Official mail processing guidance](https://www.sos.state.co.us/pubs/elections/FAQs/mailBallotsFAQ.html), [current rules](https://www.sos.state.co.us/pubs/rule_making/CurrentRules/8CCR1505-1/ElectionRules.pdf).

For remaining valid candidate votes U and other share o, U_pair=U(1−o). FINAL pair denominator=countedA+countedB+U_pair; FINAL all-candidate denominator=countedA+countedB+countedOthers+U. Required remaining A pair share for target pair margin g is [U_pair+g·FINAL_pair−counted_pair_lead]/(2U_pair). The multi-unit interface solves a selected remaining unit with all others fixed at their supplied volumes/preferences. Shares clip visibly; unknown/negative/no-pool/impossible/secured and unspecified other allocation remain distinct. [Offline implementation](data/baselines/calculate.py), [16 synthetic saved scenarios](data/baselines/live-scenarios.json). These demonstrate arithmetic, not a fitted or calibrated model.

## Reproduce, audit and handoff limits

```sh
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/colorado/data/baselines/reproduce.py
python3 senate/2026/colorado/data/baselines/calculate.py --selected-key 'CO|2024|26499|Denver|'
python3 senate/2026/colorado/data/baselines/calculate.py --live senate/2026/colorado/data/baselines/example-live-input.json
```

Start with [SCHEMA](data/baselines/source/SCHEMA.md), [reproduction script](data/baselines/reproduce.py), [validation](data/baselines/validation.json), [complete owned asset manifest](data/baselines/asset-manifest.json) and [exact source download chains](data/baselines/source/source-chains.json). Every raw original is retained intact or hash-referenced read-only, including unrelated source fields, failed routes and all PDF pages; gzip reconstruction is exact and every stored object is strictly below40,000,000 bytes. Blank/under/over, unqualified write-in scope, unavailable method splits, current ID/boundary joins, measured outstanding pools and current live publication cadence remain explicit gaps. Historical extraction does not approve those fields, project2026 turnout, infer candidate effects/lower preferences or implement a collector/Needle. Formal acceptance remains with the coordinator.
