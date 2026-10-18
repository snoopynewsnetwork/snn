# Texas historical county outcomes and conditional winning paths

Observed October 17, 2026 Central / October 18 UTC. **All 254 counties are complete for four historical contests.** The accepted county baseline comes from actual archived SOS county canvasses, independently reconciled to primary statewide canvasses. It is not a 2026 forecast, live probability, collector, or approval of current precinct geography. No current 2026 candidate roster is used.

The [1,016-row county file](data/county-baselines.csv), [6,604 candidate cells](data/baselines/county-candidates.csv), [26 statewide controls](data/baselines/state-candidate-controls.csv), [source ledger](data/baselines/source-ledger.json) and [schema/reproduction instructions](data/baselines/SCHEMA.md) retain denominators, names, parties, native labels, source vintages and conflicts. All original integer votes remain unchanged.

The 2020 Cornyn–Hegar contest is the **same Class II seat** as 2026. The 2024 Cruz–Allred race is the **other Class I seat** and the primary volume contract. The 2024 presidential result is a separate comparison; the actual 2022 Abbott–O'Rourke governor election is the midterm comparator. Texas had no 2022 Senate election.

## Primary sources and reconciliation

The [archived 2024 SOS county canvass](https://web.archive.org/web/20250422200023id_/https://results.texas-election.com/static/data/Reports/49664/CountybyCountyCanvassReport.pdf?v=1732821787446) supplies all 254 counties and all valid named candidates for Senate and president. The [archived statewide canvass](https://web.archive.org/web/20250207120710id_/https://results.texas-election.com/static/data/Reports/49664/OfficialCanvassReport.pdf?v=1738929456565) and [House Clerk publication](https://clerk.house.gov/member_info/electionInfo/2024/statistics2024.pdf) independently agree with the county candidate sums. Three recovered county capture vintages have zero candidate/county differences in these contests. Pinned MEDSL commit `df531089c78e6d0098db1a6bfb3849a066a06995`, version `2025-11-25`, agrees in every one of its 1,270 Texas Senate candidate/county cells; its README's TLC attribution alone would not establish that allocation. The actual SOS original provides the independent check.

The [2020 county canvass](https://web.archive.org/web/20241003141927id_/https://results.texas-election.com/static/data/Reports/44144/CountybyCountyCanvassReport.pdf?v=1727719562719) and [2020 statewide canvass](https://web.archive.org/web/20241211212639id_/https://results.texas-election.com/static/data/Reports/44144/OfficialCanvassReport.pdf?v=1630675822190) agree exactly with [House Clerk 2020](https://clerk.house.gov/member_info/electionInfo/2020/statistics2020.pdf). The earlier retained 2020 county/state copies have identical Senate values. The [2022 county canvass](https://web.archive.org/web/20241003233021id_/https://results.texas-election.com/static/data/Reports/47009/CountybyCountyCanvassReport.pdf) and [2022 statewide canvass](https://web.archive.org/web/20230627134547id_/https://results.texas-election.com/static/data/Reports/47009/OfficialCanvassReport.pdf) agree exactly; the [Legislature’s January 12, 2023 joint canvass](https://journals.senate.texas.gov/SJRNL/88R/HTML/88RSJ01-12-F.HTM) independently confirms the four party candidates and 1,637 combined write-ins. All four contests reconcile every county total and each named candidate to a separately parsed statewide control.

The actual printed county footer is **`07/01/2025 10.42 AM`**, while the statewide 2024 PDF prints **`01/07/2025 10:42 AM`**. [Visual county evidence](data/baselines/raw/primary-county-preview-036.png) preserves the former. These literals, archive capture datetimes, HTTP retrieval UTC and publication status remain separate. No certification date, date-format interpretation, correction cause or release cadence is inferred. Native `COLLINGSWOR` and `THROCKMORT` remain unchanged; two explicit aliases map them to FIPS. There is no fuzzy county matching.

The [independent peer audit](data/baselines/peer-reconciliation.json) checks every shared candidate value, county D/R/other/total, native identity, full ranking and exact priority set. The coordinator separately accepted the county contract in its [read-only audit](data/coordinator-baseline-reconciliation.json). That acceptance does not certify the finer reporting-unit layer.

## Actual recent outcomes

Percentages below use the named D+R pair; the all-candidate denominator remains separate. “D counties” describes that election’s observed pair outcome, not a permanent identity.

| Contest | D | R | Other valid | All valid candidates | D pair share % | D−R pair margin pp | D counties |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2020-senate | 4,888,764 | 5,962,983 | 292,293 | 11,144,040 | 45.050479 | -9.899042 | 21 |
| 2022-governor | 3,553,656 | 4,437,099 | 112,153 | 8,102,908 | 44.472093 | -11.055814 | 19 |
| 2024-senate | 5,031,249 | 5,990,741 | 269,864 | 11,291,854 | 45.647374 | -8.705252 | 19 |
| 2024-president | 4,835,250 | 6,393,597 | 159,827 | 11,388,674 | 43.060966 | -13.878068 | 12 |

The complete named minority-candidate universe is retained: 2024 Senate Ted Brown LIB 267,039, Tracy Andrus WRI 919 and Analisa Roche WRI 1,906; 2020 Senate Kerry Douglas McKennon LIB 209,722, David B. Collins GRE 81,893 and Ricardo Turullols-Bonilla WRI 678; 2022 governor Mark Tippetts LIB 81,932, Delilah Barrios GRE 28,584, Jacqueline Abernathy WRI 1,243 and Mark V Goloby WRI 394. These voters are not relabeled Democrats.

The 2024 presidential comparison retains Oliver/ter Maat LIB 68,557 and Stein/Ware GRE 82,701, plus six valid write-in slates: Ayyadurai/Ellis 433; Cuellar/Lasley 98; De la Cruz/Garcia 2,374; Fox/McVay 26; Sonski/Onak 3,780; West/Abdullah 1,858. The six sum to 8,569, matching the Clerk’s aggregate. The candidate extract preserves the full SOS slate spellings and party/ballot codes.

Allred’s 2024 pair net was **−959,492** on **11,021,990** pair votes; the 269,864 other valid votes bring the contest to 11,291,854. Harris’s presidential pair net was −1,558,347. A Senate-versus-president difference is an observed contest difference, not an estimate of a transferable candidate effect.

## Numerical paths, turnout weights and bounds

Let `s_c=D_c/(D_c+R_c)`, `T_c` be a stated hypothetical final pair volume, `T=ΣT_c`, and `M=ΣT_c(2s_c−1)`. The unbounded uniform A-share shift is `(g*T−M)/(2*T)`, with `g=0` for a tie and `g=.01` for an illustrative A+1 **pair-margin** target. A is the named Democrat in these historical pair scenarios. A +1 share-point shift adds two margin points and `0.02*T_c` net votes; a D+1 pair margin adds **0.5 share points** to the tie shift.

At actual 2024 Senate pair weights, the tie shift is **+4.352625978 share points**; A+1 requires **+4.852625978**. A tie implies 5,510,995 expected votes for each member of the pair. The +1 margin cushion means 110,219.90 expected net votes on 11,021,990 pair votes; these fractional scenario targets are not rounded historical counts.

The bounded solver uses `clip(s_c+δ,0,1)` and solves the statewide sum after clipping. None of the retained actual scenarios clips a county, so algebraic and feasible shifts agree. The validator also checks a deliberately extreme case where clipping changes the solution. Required selected-county shares below zero are already secured, above one are impossible, and zero-pool shares remain undefined. Already-winning inputs can require zero or negative improvement; the calculator does not impose a positive shift.

The first four scenarios hold Allred/Cruz county preference fixed. Low uses actual 2022 governor all-candidate volumes (8,102,908); base uses 2024 Senate (11,291,854); high uses 2024 presidential volume (11,388,674); 2020 Senate supplies an additional historical mix (11,144,040). Each county’s volume is converted to pair votes using **its own 2024 Senate pair participation**, not a statewide average. These are historical volume/mix sensitivities, not researched 2026 low/base/high turnout estimates. The other three rows show each comparator’s own actual preferences and pair participation.

| Scenario | Hypothetical pair votes | Baseline net A−B | Tie share shift pp | A+1 pair shift pp |
| --- | ---: | ---: | ---: | ---: |
| low-2022-governor-volume | 7,909,579.46 | -659,087.55 | +4.166388 | +4.666388 |
| base-2024-senate-volume | 11,021,990.00 | -959,492.00 | +4.352626 | +4.852626 |
| high-2024-president-volume | 11,116,349.05 | -961,102.25 | +4.322922 | +4.822922 |
| 2020-senate-volume | 10,876,820.97 | -815,168.82 | +3.747275 | +4.247275 |
| 2020-senate-own-preference-and-volume | 10,851,747.00 | -1,074,219.00 | +4.949521 | +5.449521 |
| 2022-governor-own-preference-and-volume | 7,990,755.00 | -883,443.00 | +5.527907 | +6.027907 |
| 2024-president-own-preference-and-volume | 11,228,847.00 | -1,558,347.00 | +6.939034 | +7.439034 |

An A+1 **all-candidate** margin is a different target: 112,918.54 net votes on 11,291,854 valid candidates, requiring +4.864868050 pair-share points in the base scenario. It does not transfer Brown, Andrus or Roche votes into Allred’s pool. Both margin definitions appear in the [21 statewide settings](data/baselines/state-target-scenarios.csv) and [5,334 county target rows](data/baselines/county-target-scenarios.csv).

The following top-15 counties illustrate contribution arithmetic. Weight uses 2024 Senate **pair votes**, while the attention ranking uses **all five candidates**. Pair margins are signed D−R; the A+1 share is the illustrative uniform base scenario, not an independently necessary county result. All remaining counties and all four historical comparisons are in the county CSV.

| County / FIPS | Pair weight % | 2024 Senate margin pp | 2024 president margin pp | Baseline net | Net gain from +1 share pp | Uniform A+1 pair target share % |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Harris / 48201 | 13.6800 | +11.6564 | +5.6205 | +175,757 | 30,156.22 | 60.6808 |
| Dallas / 48113 | 7.4640 | +29.1273 | +22.6163 | +239,625 | 16,453.62 | 69.4163 |
| Tarrant / 48439 | 7.2734 | +0.2264 | -5.1934 | +1,815 | 16,033.38 | 54.9658 |
| Bexar / 48029 | 6.5883 | +16.4757 | +9.8599 | +119,641 | 14,523.30 | 63.0905 |
| Travis / 48453 | 5.1208 | +44.2950 | +40.0503 | +250,007 | 11,288.26 | 77.0001 |
| Collin / 48085 | 4.5360 | -5.3608 | -11.4461 | -26,802 | 9,999.20 | 52.1722 |
| Denton / 48121 | 3.9798 | -8.5037 | -13.3518 | -37,302 | 8,773.08 | 50.6008 |
| Fort Bend / 48157 | 3.1428 | +7.7999 | +1.6203 | +27,019 | 6,928.02 | 58.7526 |
| Montgomery / 48339 | 2.7280 | -42.2109 | -45.9133 | -126,918 | 6,013.52 | 33.7472 |
| Williamson / 48491 | 2.6994 | +1.5545 | -2.4891 | +4,625 | 5,950.54 | 55.6299 |
| El Paso / 48141 | 2.1305 | +20.7940 | +15.3182 | +48,829 | 4,696.46 | 65.2496 |
| Hidalgo / 48215 | 1.8721 | +6.7512 | -2.9000 | +13,931 | 4,126.94 | 58.2283 |
| Brazoria / 48039 | 1.4270 | -14.7079 | -19.9515 | -23,133 | 3,145.66 | 47.4987 |
| Galveston / 48167 | 1.4011 | -23.1807 | -27.7424 | -35,798 | 3,088.60 | 43.2623 |
| Bell / 48027 | 1.1423 | -11.9348 | -16.4078 | -15,027 | 2,518.18 | 48.8852 |

Holding all other counties at actual 2024 Senate shares and volume makes the tradeoff concrete: Harris alone must move from 55.828217% to **87.645600%** A share for a statewide tie, or **91.300564%** for A+1 pair margin. Its baseline +175,757 net contribution must become +1,135,249 for the tie; the required gain is the entire 959,492 statewide deficit. A +1 share-point gain there contributes 30,156.22 net votes. Dallas alone would need **122.878613%** for a tie (impossible); other counties’ changes or turnout assumptions must compensate. The CSV carries the selected-only solve for every county in every scenario.

Reproduce a selected-county solve:

```sh
python3 senate/2026/texas/data/baselines/targets.py --county-fips 48201 --margin-pp 0
python3 senate/2026/texas/data/baselines/targets.py --county-fips 48113 --margin-pp 1 --denominator pair
```

The [exact priority contract](data/baselines/priority-set.json) is separate from pair weights: top 15 = **7,369,697/11,291,854 (65.265607%)**; the smallest 80% set is **34 counties, 9,076,868 votes (80.384213%)**. The preceding 33 supply 9,018,686; Midland’s 58,182 crosses the exact integer inequality. All 220 remaining counties remain in every statewide calculation.

## Fixed-counted remainder check

The [offline remainder calculator](data/baselines/live_remainder.py) fixes counted A, B and other votes and solves only the future pair pool. [Saved examples](data/baselines/live-examples.json) are explicitly synthetic: counted A 3,000,000; B 3,300,000; other 100,000. Assume 4,000,000 pair votes and 100,000 other votes remain. The final pair denominator is **10,300,000**; all-candidate denominator **10,500,000**.

The statewide tie requires **53.7500%** A in the pair remainder. A+1 pair margin requires **55.0375%**, giving 103,000 final net votes; A+1 all-candidate margin requires **55.0625%**, giving 105,000. Using the remaining-vote denominator for the final cushion would be wrong. The initial counted −300,000 net is unchanged in every calculation.

For a selected illustrative Harris remainder of 1,000,000 pair votes, hold the other 253 counties’ 3,000,000 at 54% A, contributing +240,000 future net. Harris then needs **53.0000%** for a statewide tie, **58.1500%** for A+1 pair margin, or **58.2500%** for A+1 all-candidate margin. Its label does not establish which precincts/methods remain, so no countywide baseline is claimed comparable to that remainder.

Low/base/high statewide remaining pair pools of 2/4/6 million, keeping 100,000 other remaining, require respectively **59.6250% / 55.0625% / 53.541667%** for A+1 all-candidate margin. Unknown remaining inputs return unknown; negative counts are invalid; no positive pool leaves the share undefined and evaluates the fixed lead separately. The fixtures include already-secured and impossible remainders. These are conditional arithmetic checks, not probabilities or a calibrated election call.

## Denominator and finer-geography limits

The [SOS historical participation page](https://www.sos.state.tx.us/elections/historical/70-92.shtml) reports 2024 registered voters 18,623,931 and native ‘Turnout’ 11,388,674; 2022 17,672,143 / 8,102,908; 2020 16,955,519 / 11,315,056. Those participation figures equal presidential/governor candidate totals here. They do not prove an all-ballot county control or provide county method counts. The [registration/participation extract](data/baselines/registration-participation-controls.csv) retains the actual label. County ballot/registration/under/over fields stay undefined when the selected source lacks them.

The [TLC publisher explicitly describes](https://data.capitol.texas.gov/topic/about/elections) VTD data as derived for redistricting and warns it can differ from official returns. Each of five retained files has 9,712 VTD rows across 254 prefixes, with original CNTYVTD/VTDKEY. Even the 2022 results use the published 2024 VTD vintage; these are not native precinct returns. The [full VTD cells](data/baselines/tlc-vtd-cells.csv.gz) and [county disagreements](data/baselines/tlc-county-disagreements.csv) preserve every value.

TLC 2024 Senate is lower than primary by Allred 107, Cruz 104, Brown 95, Andrus 385 and Roche 930. TLC presidential generic write-in 24,730 exceeds the primary six named valid write-ins’ 8,569 by 16,161; other candidate discrepancies remain, including Oliver +6. TLC 2022 governor has Abbott −2, O’Rourke +1,116, Tippetts +10, Barrios +6, and generic write-in +2,730 against the named valid universe. TLC registration/‘Turnout’ sums differ too: 2024 +62,586/+72,124; 2022 +41,222/+40,139 versus the SOS summary. No residual is distributed or rescaled.

The [source-native inventory](data/baselines/native-units.csv.gz) preserves **31,702 OpenElections identities**, including administrative/central/combined labels and units lacking selected-contest rows: 10,786 for 2024, 5,055 for 2022 and 15,861 for 2020. The [302,233 selected raw cells](data/baselines/native-coverage.json) retain all native candidate, party, office, district, method and row identities with no candidate-key deduplication. All shared raw fields and inventory counts independently agree with the turnout worker. Repeated column-header records are retained as anomalies. Duplicates and method nonadditivity are diagnostics, not silently fixed counts.

The 2024 layer has 184 county-named files but only 182 literal county identities: Hardin’s file says Hunt; Jeff Davis’s says Grayson. Both file and literal identities remain explicit; these are not accepted Hardin/Jeff Davis allocations. The 2022 and 2020 layers cover only 101 and 248 mapped counties respectively. Missing native coverage is not filled with zeros or TLC VTDs. Source typos/blank county mappings are documented individually. There is no complete authenticated 254-county native precinct ground truth or cross-year/2026 unit crosswalk.

Actual primary county originals were retained for Harris, Bexar, Angelina, Midland, Dallas and Travis. The [primary unit audit](data/baselines/primary-unit-audit.json) preserves full extracted PDF text and reporting labels: Harris 1,584; Bexar 776 ballot-style units; Angelina 41 including 11B/17B; Midland 46 including suffixes. These primary unit-label checks do not certify every vote table or map a unit to a polygon. A separate [full Harris Senate extraction](data/baselines/harris-primary-senate-unit-controls.csv.gz) independently reconciles all five candidates, ballots, under/over and five ballot methods in all 1,584 units. Its totals are 1,567,610 ballots; 2,664,202 registered; 18,623 undervotes and 73 overvotes. [County ballot/registration controls](data/baselines/county-ballot-registration-controls.csv) also retain Dallas 858,562 ballots / 1,469,952 registered and Travis 587,090 / 925,858 from the original vendor worksheets; their separate candidate-vintage conflicts are preserved. Dallas and Travis retain every row/cell/attribute of every vendor XML worksheet, plus independently checked registration/president/Senate row arrays and method controls.

The [vendor conflict table](data/baselines/primary-vendor-candidate-conflicts.csv) shows why source precedence matters. Dallas vendor Senate 842,940 exceeds SOS 842,425 by 515: generic write-in 818 versus named valid 222 (+596), offset by major/named party candidate differences totaling −81 (Cruz −31, Allred −42, Brown −8). Travis vendor 578,885 exceeds SOS 578,541 by 344: generic write-in 601 versus named valid 239 (+362), with Cruz −6 and Allred −12. All source integers and literal write-in scopes are retained; no cause or revision direction is assumed. Primary county baselines remain on the explicitly chosen SOS canvass.

## Reproduction and remaining work

Run the commands in [SCHEMA.md](data/baselines/SCHEMA.md). The [offline validator](data/baselines/validate.py) rechecks raw hashes, primary candidate/county sums, uniqueness, all-county weights, native retention, exact integer 80% minimum, full order, uniform/conditional arithmetic, clipping, zero/unknown/infeasible pools, local links and strict asset limits. [Validation results](data/baselines/validation.json) and the [owned asset manifest](data/baselines/asset-manifest.json) are retained.

Historical preference stability, turnout volumes and mix, geographic matching, reporting-order effects, candidate effects and any future missing-data treatment remain assumptions. No residual imputation is performed here. Current full 2026 ballot status must come from official final publications before candidate mapping; primary nominees or old feed IDs are insufficient. Native original coverage, duplicate keys, method definitions, unresolved source snapshots and 2026 boundaries remain visible gaps. No generic polling or registration preference proxy, calibrated needle, live collector or current precinct approval is supplied.
