# New Hampshire historical partisanship and conditional paths

Research observed 2026-10-18 UTC. Complete accounting coverage is **320 source-native rows per contest**, with ten county controls and a disjoint town/city/ward/administrative hierarchy. The compatibility filename `county-baselines.csv` contains **960 native contest rows**, not ten county substitutes. [Baselines](data/county-baselines.csv), [hierarchy](data/baselines/hierarchy.json), [schema](data/baselines/source/SCHEMA.md), [validation](data/baselines/validation.json) and [asset audit](data/baselines/asset-manifest.json) provide the numerical package.

The priority comparison is **2024 president**. New Hampshire had no 2024 Senate election. The November 3, 2020 Shaheen–Messner–O’Donnell election is the same Class II seat as the November 3, 2026 regular election. November 8, 2022 Hassan–Bolduc–Kauffman is the other Class III seat and the actual midterm comparator. Election dates and offices appear on the original tallies; the Senate’s [Class II](https://www.senate.gov/senators/Class_II.htm) and [Class III](https://www.senate.gov/senators/Class_III.htm) rosters establish the separate cycles. The SOS [current filing calendar](https://www.sos.nh.gov/elections/running-office) identifies the 2026 general date. Retained current direct SOS requests returned 403; indexed text is qualified separately from acquired originals.

Historical source status: these are **official SOS historical general-election tallies recovered as archived original bytes**. The workbooks/PDFs alone do not establish their legal certification dates or every amendment’s issuance sequence. NARA’s signed presidential ascertainment separately certifies the four printed 2024 slates; Clerk/FEC publications provide statewide historical checks. Volunteer clerk compilations, newsroom/AP counts and projections are not promoted to certified returns.

## Full historical candidate controls

| Election / role | Complete reported field | Identity | Votes |
| --- | --- | --- | ---: |
| 2024 priority_president_no_2024_senate | Kamala D. Harris and Tim Walz | Democratic | 418,488 |
| 2024 priority_president_no_2024_senate | Donald J. Trump and JD Vance | Republican | 395,523 |
| 2024 priority_president_no_2024_senate | Chase Oliver and Mike ter Maat | Libertarian | 4,425 |
| 2024 priority_president_no_2024_senate | Jill Stein and Rudolph Ware | Green | 3,680 |
| 2024 priority_president_no_2024_senate | Write-Ins | generic_unallocated_not_a_candidate | 4,073 |
| 2022 other_Class_III_seat_actual_midterm | Maggie Hassan | Democratic | 332,490 |
| 2022 other_Class_III_seat_actual_midterm | Donald C. Bolduc | Republican | 275,631 |
| 2022 other_Class_III_seat_actual_midterm | Jeremy Kauffman | Libertarian | 12,390 |
| 2022 other_Class_III_seat_actual_midterm | Scatter | generic_unallocated_not_a_candidate | 464 |
| 2020 same_Class_II_seat | Jeanne Shaheen | Democratic | 450,778 |
| 2020 same_Class_II_seat | Corky Messner | Republican | 326,229 |
| 2020 same_Class_II_seat | Justin O’Donnell | Libertarian | 18,421 |
| 2020 same_Class_II_seat | Scatter | generic_unallocated_not_a_candidate | 486 |

[2024 president original XLS](https://web.archive.org/web/20241219142947id_/https://www.sos.nh.gov/sites/g/files/ehbemt561/files/inline-documents/sonh/2024-ge-president_3.xls); [2022 Senate selected `_5` original XLS](https://web.archive.org/web/20240114224201id_/https://www.sos.nh.gov/sites/g/files/ehbemt561/files/inline-documents/sonh/2022-ge-us-senator_5.xls); [2022 remediated original PDF](https://web.archive.org/web/20230322192318id_/https://www.sos.nh.gov/sites/g/files/ehbemt561/files/inline-documents/sonh/2022-ge-us-senator-remediated_1.pdf); [2020 Senate original PDF](https://web.archive.org/web/20221106132236id_/https://www.sos.nh.gov/sites/g/files/ehbemt561/files/documents/2020%20GE%20Election%20Tallies/2020-ge-united-states-senate.pdf). Complete headers, cell types, blanks, dashes, notes and source positions are retained in [raw extracts](data/baselines/source/extraction-inventory.json) and the original-byte references. **Scatter and Write-Ins remain unallocated source categories**, not named candidates, Democrats or established valid write-ins. A complete valid/named write-in allocation is unavailable in the retained statewide sources. Libertarian votes remain Libertarian. These are separate one-stage general electorates, without pooling primary votes or inventing transfer preferences.

| Election | A+B pair | Other reported marks | Candidate + generic marks | A−B net | Pair margin pp | All-reported margin pp |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2024 | 814,011 | 12,178 | 826,189 | +22,965 | +2.821215 | +2.779630 |
| 2022 | 608,121 | 12,854 | 620,975 | +56,859 | +9.349948 | +9.156407 |
| 2020 | 777,007 | 18,907 | 795,914 | +124,549 | +16.029328 | +15.648550 |

A is the named Democratic ticket/candidate in each historical comparison; B is the named Republican. All three A candidates won statewide. This is a historical outcome, not a permanent town label or a 2026 candidate-effect estimate. Pair ties are thresholds, not victories.

The 2024 president workbook also reports **4,482 undervotes and 362 overvotes**. Thus 826,189 candidate/generic marks + 4,844 under/over = **831,033 contest-accounting marks**. These are not interchangeable with the ballots-cast publication. Its state total is 831,467, leaving a 434 difference; the native ballot totals sum to 831,468, leaving 435. Neither residual is allocated to candidates or geographies. All seven presidential fields reconcile independently from native numeric sums through every county footer and state summary; source nulls remain null. [Clerk 2024 control](https://clerk.house.gov/member_info/electionInfo/2024/statistics2024.pdf) agrees with all seven fields. [FEC 2024 presidential publication](https://www.fec.gov/documents/5644/2024presgeresults.pdf) and [NARA ascertainment original](https://www.archives.gov/files/electoral-college/2024/ascertainment-new-hampshire.pdf) provide additional controls; four electors and two certificate pages are not added as separate votes.

## Complete native geography and priority

The originals include town rows, city wards and administrative territory labels. The hierarchy is state → county control → literal municipal parent → ward leaves where the source says “Ward”; unwarded native totals are accounting leaves. A city parent is never added to its wards. County summaries and repeated county footers are controls only. All 320 labels, including rows with unpopulated printed-candidate cells, stay in coverage. The sources do not supply a numeric reporting-unit ID; `nh-2024-pres:{countyFIPS}:{percentencoded trimmed literal label}` is a synthetic source-scoped key. Ward numbers are unique only within their explicit municipal parent. Census 2020 county/municipal codes are exact county-scoped name matches with legal-type suffixes only. Abbreviated or dissimilar territories stay unmatched. No clerk authority, cross-year ward crosswalk, current precinct boundary or November 2026 reporting equivalence is inferred.

The [full 320-row ordering](data/baselines/priority.csv) uses reported four-ticket + generic write-in numeric subtotals, descending, then county FIPS, then trimmed literal label in Unicode order. The top 15 contain **185,659 / 826,189 = 22.471735%**. The minimum integer 80% crossing is **143 units, 662,624 / 826,189 = 80.202472%**; 142 supply 660,378, below 80%. Tilton adds 2,246. The other **177 units supply 163,565** reported votes and remain in every statewide calculation.

The authoritative frozen [turnout contract](data/turnout/priority-set.json) and external [coordinator acceptance](data/coordinator-priority-acceptance.json) govern historical research dispatch. Acceptance is referenced by path only. It does not approve current geography, feeds or clerk channels. The independent [peer reconciliation](data/baselines/peer-reconciliation.json) checks all 23 × 320 source-native identities and positions, 34,880 parsed fields, 34,880 raw values, 20,480 BIFF candidate/administrative field types and all 320 ranked rows/order, with zero disagreements. The turnout worker’s [reciprocal audit](data/turnout/peer-agreement.json) separately verifies the baseline CSV and controls. The later display-label correction to the original full Donald C. Bolduc is recorded in the [coordinator version review](data/coordinator-peer-version-review.json); numerical/source fields were unchanged. The [coordinator target review](data/coordinator-target-review.json) independently checks the current960 baseline rows and scenario arithmetic. Party/candidate keys, field names and locator aliases are documented in the schema.

## County views that reconcile to native leaves

County rows below are compact views of complete native inputs, not election-reporting authority or substitutes for town/ward data. The [county controls](data/baselines/county-controls.json) retain every candidate; the [960-row native CSV](data/county-baselines.csv) supplies each source-native outcome, denominator and raw value.

| County | 2024 A−B net | 2024 pair margin pp | 2022 pair margin pp | 2020 pair margin pp | 2024 pair votes | 2024 pair weight % | Pair / reported % |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Belknap | -5,296 | -13.1630 | -9.6563 | +0.4511 | 40,234 | 4.9427 | 98.9134 |
| Carroll | -604 | -1.7636 | +2.5971 | +9.1954 | 34,248 | 4.2073 | 98.8170 |
| Cheshire | +4,496 | +10.0667 | +20.5317 | +26.0603 | 44,662 | 5.4867 | 98.3983 |
| Coos | -2,367 | -13.8413 | -3.4422 | +9.5781 | 17,101 | 2.1008 | 98.7242 |
| Grafton | +11,084 | +20.1887 | +27.1889 | +30.5956 | 54,902 | 6.7446 | 98.2235 |
| Hillsborough | +6,719 | +2.9108 | +8.8438 | +15.9371 | 230,833 | 28.3575 | 98.4614 |
| Merrimack | +4,817 | +5.2619 | +13.5608 | +20.2873 | 91,545 | 11.2462 | 98.4588 |
| Rockingham | -4,928 | -2.4622 | +3.1747 | +9.7953 | 200,150 | 24.5881 | 98.6340 |
| Strafford | +9,211 | +12.1943 | +19.8767 | +25.3245 | 75,535 | 9.2794 | 98.4965 |
| Sullivan | -167 | -0.6734 | +6.1502 | +12.2817 | 24,801 | 3.0468 | 98.3347 |

The same primary XLS/PDF citations above support each county/native field. County totals with negative A−B net favored the Republican in that contest; positive values favored the named Democrat. They do not imply that Libertarian/Green or unallocated write-ins belong to either coalition.

## Tie, A+1 and historical sensitivity

For fixed two-candidate weights `Tᵢ`, A share `sᵢ` and total `T`, baseline net votes are `M = ΣTᵢ(2sᵢ−1)`. An unbounded common shift `δ = −M/(2T)` ties. A **+1 percentage-point pair margin** targets `0.01T` net votes and adds **0.5 share points** to the unbounded tie shift. One share point changes pair margin by two points and net votes by `0.02Tᵢ`. A+1 is an illustrative pair margin, not one net vote or the legal winning rule. All-reported cushions use the separate candidate/generic denominator. No preference is defined for an unavailable/no-positive pair pool.

Shares are explicitly clipped to `[0,1]`; the implementation solves the bounded statewide equation by bisection and retains the unbounded result. In the 2024 native repeat, Martin’s Location has reported A=0/B=2; a negative shift cannot lower its A share. Unbounded tie shift is **−1.410607473 pp**; bounded shift is **−1.410610939 pp**. Both values remain in the outputs. For A+1 the unbounded shift is −0.910607473 pp; the bounded solve is reported separately. Already-winning baselines may tolerate a negative shift; a “required positive improvement” of zero does not mean the signed tie threshold is zero.

| Scenario | Historical pair volume | Baseline net | Tie shift share pp, unbounded | Tie shift share pp, bounded | A+1 shift share pp, bounded |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2024-own-native-repeat | 814,011.00 | +22,965.00 | -1.410607473 | -1.410610939 | -0.910609711 |
| 2022-own-native-repeat | 608,121.00 | +56,859.00 | -4.674974224 | -4.674974224 | -4.174974224 |
| 2020-own-native-repeat | 777,007.00 | +124,549.00 | -8.014663961 | -8.014663961 | -7.514663961 |
| 2024-preference-2022-county-mix-low-historical-volume | 608,121.00 | +17,087.13 | -1.404911868 | -1.404915259 | -0.904914052 |
| 2024-preference-2020-county-mix-middle-historical-volume | 777,007.00 | +21,915.22 | -1.410233237 | -1.410236628 | -0.910235426 |
| 2024-preference-2024-county-mix-high-historical-volume | 814,011.00 | +22,965.00 | -1.410607473 | -1.410610939 | -0.910609711 |
| 2022-county-preference-2024-native-volume | 814,011.00 | +76,234.78 | -4.682662671 | -4.682662671 | -4.182662671 |
| 2020-county-preference-2024-native-volume | 814,011.00 | +130,545.57 | -8.018661060 | -8.018661060 | -7.518661060 |

The low/base/high historical volume envelope (base means the middle historical anchor; the priority comparison remains2024) is **low 2022 = 608,121**, **base/middle 2020 = 777,007**, **high 2024 = 814,011 pair votes**. Own-native repeats use each contest’s own native geography and preference. Hybrid mix cases hold **2024 native preference and within-county pair proportions**, applying each historical county’s actual pair total. They therefore move county composition and total volume without a guessed town/ward crosswalk. The separate 2020/2022 county-preference anchors keep 2024 native volume and assign the corresponding historical **county** share uniformly within that county as an explicit scenario assumption. That assignment is not an observed ward preference. Hybrid all-reported volume scales each 2024 native candidate/generic subtotal by its county pair-volume ratio, retaining 2024 participation; other historical identities are never reassigned to 2026 candidates.

These are source-based historical volume/mix/preference sensitivities, **not 2026 turnout forecasts**. Candidate effects, ticket splitting in 2026, preference transfers and the size/composition/order of remaining votes are not inferred. Uniformly scaling every unit alone changes net-vote magnitudes, not shares. [Settings](data/baselines/scenario-settings.json), [16 statewide cases](data/baselines/state-scenarios.csv), [5,120 native target rows](data/baselines/native-targets.csv) and [160 county target rows](data/baselines/county-targets.csv) agree on volume bases, pair participation, targets and clips. Every native target includes weight, baseline/target contribution, gain, value of one share point and selected-unit-only requirement.

For selected unit `c`, every other unit fixed at `qⱼ = clip(sⱼ + explicit_shift)` gives `q_c = [T_c + gT − Σⱼ≠c Tⱼ(2qⱼ−1)]/(2T_c)`. Saved tables explicitly fix every other unit to its historical scenario anchor with **0 pp additional shift**. Requirements below 0 are already secured even at all-B in the selected pool; above 1 are impossible at all-A; a zero pool stays a zero-pool status. Unbounded requirements remain available alongside clipped displays. These are conditional tradeoffs, never individually necessary municipal targets.

| 2024-repeat county | Tie target A share % | Tie net contribution | Net-vote gain from baseline | Net votes per +1 pp A share | Selected-county-only tie A share %, others fixed |
| --- | ---: | ---: | ---: | ---: | ---: |
| Belknap | 42.007891 | -6,431.090 | -1,135.090 | 804.68 | 14.879207 |
| Carroll | 47.707586 | -1,570.212 | -966.212 | 684.96 | 15.590691 |
| Cheshire | 53.622751 | +3,235.986 | -1,260.014 | 893.24 | 29.323586 |
| Coos | 41.668906 | -2,849.401 | -482.401 | 342.02 | -24.065844 |
| Grafton | 58.683739 | +9,535.093 | -1,548.907 | 1,098.04 | 39.179811 |
| Hillsborough | 50.044770 | +206.689 | -6,512.311 | 4,616.66 | 46.481006 |
| Merrimack | 51.220336 | +2,234.312 | -2,582.688 | 1,830.90 | 40.087935 |
| Rockingham | 47.358312 | -10,574.676 | -5,646.676 | 4,003.00 | 43.031976 |
| Strafford | 54.686563 | +7,079.990 | -2,131.010 | 1,510.70 | 40.895611 |
| Sullivan | 48.252709 | -866.691 | -699.691 | 496.02 | 3.364784 |

## Actual 2026 ballot and legal outcome

The official [Farmington clerk](https://www.farmington.nh.us/1206/Town-Clerk-Tax-Collector) links its [November 3, 2026 general-election sample ballot](https://www.farmington.nh.us/DocumentCenter/View/3121). Page 1 visibly prints **John E. Sununu — Republican; Edmond Laplante — Constitution; Chris Pappas — Democratic**, and a Senate write-in space, with a one-candidate vote limit. This is an acquired general ballot publication, not a primary nominee list. The image-only original and [visual transcription with hash and page](data/baselines/source/primary-observations.json) are retained. Current result-feed candidate IDs, the valid write-in universe, statewide ballot-style inventory and any later amended publication remain unverified.

Under [RSA 659:81](https://gc.nh.gov/rsa/html/LXIII/659/659-81.htm), the highest-vote candidate wins the single seat after the state canvass. A must lead **every opponent**, including Laplante and any valid named write-in. There is no majority/50% legal requirement, RCV transfer or runoff stage in these Senate general comparisons. An A/B tie does not elect A; A+1 pair margin can coexist with a third-candidate plurality. The calculator separately reports this condition and a strict integer plurality minimum when the pool permits that arithmetic.

## Offline conditional remainder calculator

[calculator.py](data/baselines/calculator.py) runs without network access. Inputs contain fixed counted A/B and individually named others, plus explicit remaining units with **remaining total candidate votes**, pair participation, A preference within the pair and an optional named allocation of remaining nonpair votes. Unknown volume/preference stays unknown; negative volume and invalid participation are rejected. Requested shares outside [0,1] are clipped with both requested/used values shown. Counted votes are never rescaled or forecast.

`U = Σ remaining_total × pair_fraction`; `C_final = counted_A + counted_B + counted_named_others + Σremaining_total`; `T_final = counted_A + counted_B + U`. Final net is `L_counted + ΣUᵢ(2qᵢ−1)`. A target pair margin `g` requires remaining A share `[U + gT_final − L_counted]/(2U)`; an all-candidate margin substitutes `gC_final`. **A+1 on the final pair denominator adds 0.005×T_final/U to the remaining share**, not a flat 0.5 pp. Selected-unit mode fixes counted and every other remaining unit’s explicit assumptions. Generic unallocated others make the legal plurality unresolved rather than fabricated.

[20 saved synthetic inputs](data/baselines/synthetic-inputs.json) and [their results](data/baselines/synthetic-results.json) cover unknown, no-pool win/tie/loss, negative counts/pools, impossible/secured requirements, high/negative share clipping, no pair pool, a third candidate beating the A/B winner, unallocated others, final-denominator targets, selected-only impossible/secured/feasible and invalid participation. These are arithmetic stress cases, not calibrated probabilities. In the final-denominator example counted A100/B120/other10 plus remaining100 at 80% pair gives final pair300 and all-candidate330. An A+1 pair target requires remaining A pair share **64.375%**; A+1 all-candidate margin requires **64.5625%**. Neither is a prediction.

```sh
python3 senate/2026/new-hampshire/data/baselines/calculator.py --live senate/2026/new-hampshire/data/baselines/synthetic-inputs.json
python3 senate/2026/new-hampshire/data/baselines/calculator.py --selected nh-2024-pres:33015:Salem --others-share-shift-pp 0 --target-margin-pp 0
```

## Turnout, registration and retained disagreements

| General election | Regular ballots | Absentee ballots | State reported ballots | Native reported ballots | Checklist names | New registrations at polling place |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2020 | 554,282 | 260,217 | 814,499 | 814,499 | 1,119,232 | 75,611 |
| 2022 | 568,276 | 58,655 | 626,931 | 626,931 | 925,398 | 48,615 |
| 2024 | 731,944 | 99,524 | 831,467 | 831,468 | 1,013,075 | 96,623 |

Sources are the archived original [2020 ballots](https://web.archive.org/web/20240717182706id_/https://www.sos.nh.gov/sites/g/files/ehbemt561/files/documents/2020%20GE%20Election%20Tallies/2020-ge-ballots-cast.xls), [2020 checklist](https://web.archive.org/web/20240717182711id_/https://www.sos.nh.gov/sites/g/files/ehbemt561/files/documents/2020%20GE%20Election%20Tallies/2020-ge-names-on-checklist.xlsx), [2022 ballots `_3`](https://web.archive.org/web/20230125001254id_/https://www.sos.nh.gov/sites/g/files/ehbemt561/files/inline-documents/sonh/2022-ge-ballots-cast_3.xls), [2022 checklist `_2`](https://web.archive.org/web/20240114224201id_/https://www.sos.nh.gov/sites/g/files/ehbemt561/files/inline-documents/sonh/2022-ge-names-on-checklist_2.xlsx), [2024 ballots `_14`](https://web.archive.org/web/20250611055417id_/https://www.sos.nh.gov/sites/g/files/ehbemt561/files/inline-documents/sonh/2024-ge-ballots-cast_14.xls) and [2024 checklist `_7`](https://web.archive.org/web/20250611055423id_/https://www.sos.nh.gov/sites/g/files/ehbemt561/files/inline-documents/sonh/2024-ge-names-on-checklist_7.xlsx). Every selected workbook has all 320 native labels; full party registration and polling-place registration components are in [source-scoped native fields](data/baselines/native-fields.jsonl.gz). Names on checklist is the publication’s registration measure; the election header supplies its reference election. Active/inactive scope, exact administrative as-of instant and inclusion timing for new registrations are not established. Do not add new registrations to checklist names or call these voting-eligible population totals. Regular/absentee ballot methods do not provide candidate-by-method preferences or a separate supported early-vote pool.

The 2024 ballot state row has 731,944 regular + 99,524 absentee = **831,468**, one above its printed 831,467 total. Coos detail/footer reports absentee1,968/total17,511 while its summary reports1,967/17,510. Somersworth Ward3 reports regular1,119 + absentee103 =1,222 but printed total1,221. The 2024 checklist’s Hopkinton new-party components55+46+195=296 but its literal new-registration total is3. These are retained primary disagreements, not repaired values. They do not alter the priority denominator.

The retained 2022 Senate vintages differ: base Bolduc275,930/Hassan333,217/Kauffman12,280/Scatter459; `_1`275,928/333,193/12,390/464; `_2`275,928/332,193/12,390/464; selected `_5`275,631/332,490/12,390/464. The `_5` summary reverses major-candidate column order relative to its detail; extraction maps actual candidate headers. The [Clerk 2022 publication](https://clerk.house.gov/member_info/electionInfo/2022/statistics2022.pdf) agrees with `_2`, not `_5`: **297 fewer Hassan and 297 more Bolduc**, unchanged combined608,121/total620,975. `_5` and remediated PDF match all ten county controls and all native fields, but release/correction cause and certification chronology remain unresolved. Full native changes are in [vintage disagreements](data/baselines/vintage-disagreements.json); neither source is silently overwritten.

The 2020 original visibly marks **Keene Ward3*** and **Millsfield*** with correction notes; labels and notes remain literal. Coos all-dash rows and its dash scatter footer are not replaced by invented zeros. Selected 2024 `_3` is explicitly linked from the recovered SOS 2024 index and agrees with Clerk/FEC/NARA controls; later-captured unsuffixed and `_0` presidential originals differ and are retained as separate vintages. A later archive capture does not prove supersession. NARA’s first page is amended with testimony year2024; its second page literally says2020 under a2024 election header, with identical slate counts. The cause/release sequence is not established; the same [original NARA certificate](https://www.archives.gov/files/electoral-college/2024/ascertainment-new-hampshire.pdf) preserves both pages.

## Reproduction, evidence and limits

[source/SCHEMA.md](data/baselines/source/SCHEMA.md) defines fields, evidence chains, null policy, model bases and all scripts. Original responses are reused read-only by exact stored/original SHA256 and byte count, with the complete request/final URLs, UTC retrieval, response/redirect headers and available source clocks. Existing shared captures lack some redirect-hop metadata; that gap stays explicit. HTTP-content gzip is separately decoded only when recorded. Raw gzip files are lossless; no source was truncated or simplified. Every owned asset is strictly below40,000,000 bytes, and the complete manifest audits owned paths plus shared-byte references without duplicating large originals.

```sh
python3 senate/2026/new-hampshire/data/baselines/reproduce.py
# Optional bounded authority refresh or exact-URL replay; retained responses are not overwritten:
python3 senate/2026/new-hampshire/data/baselines/acquire.py --fetch
```

Offline validation checks source/raw/asset hashes, source identity uniqueness, complete native rosters, exact integer priority crossing/order, county/state candidate balances, retained administrative residuals, denominator/weight bounds, tie/A+1 solutions including clipping, selected-only feasibility, synthetic final denominators and relative links. No tests establish current boundaries, a known live reporting cadence, live collector operation, 2026 turnout, remaining-vote assumptions or calibrated win probabilities. Final valid write-in allocations, historical amendment chronology and current result-feed candidate/geography IDs remain specific handoff gaps.
