# Mississippi historical partisanship and conditional paths

Working research snapshot: October 19, 2026 UTC. This is the **regular Class II** race.
The priority baseline is the other, Class I seat's **2024 Wicker–Pinkins Senate
contest**, while **2020 Hyde-Smith–Espy** is the same Class II seat. Historical
pair preferences, volumes and candidate identities are not 2026 projections.

At the 2024 two-name Senate weights, Pinkins trails Wicker by **311,439 votes**.
A uniform **12.812191 A-share points** ties the pair;
**13.312191 share points** gives an illustrative
**A+1 pair margin**, or **12,154.01 net votes**. All 82 counties remain in every
state calculation. This is a deterministic named-pair benchmark; it does not
transfer Pinkins's 2024 Democratic identity to his 2026 Independent candidacy.
The counts reconcile to the [sos-2024-certified-sen-pdf](https://www.sos.ms.gov/elections/electionresults/2024General/Statewide%20Results/Certification%20of%20Vote%20for%20United%20States%20Senate.pdf) (PDF p3).

**Current ordinary outcome and candidates.** The SOS's September 10, 2026
[clarification](https://www.sos.ms.gov/news/secretary-michael-watson-clarifies-vote-requirements-mississippi-elected-offices) and its
[sos-2026-majority-chart](https://mcusercontent.com/c9f52743f930fd93605c3a79c/files/db0bf77c-d59d-01a2-a6e1-ff93c657cab2/Majority_Chart.pdf) explicitly classify ordinary U.S. Senate as
**plurality**, separately from majority rules for statewide state offices and
judicial/county offices. The November 3 [sos-2026-sample-ballot](https://sos.ms.gov/content/documents/Elections/2026/Sample%20Ballot%209-9-26.pdf) (p1)
prints **Scott Colom—Democrat, Cindy Hyde-Smith—Republican, Ty Pinkins—Independent,
and Write-in**. It is headed SAMPLE; signed final certification, withdrawals,
valid write-in identities and result-system IDs remain unverified here. The
qualifying list is corroboration, not a substitute final ballot certificate.
A must strictly exceed every named rival to have a unique plurality; beating
Hyde-Smith while trailing Pinkins is not a win. No opposition union is assumed.

**Actual contests and source presentation.** There was no 2022 U.S. Senate or
governor election in Mississippi. The [sos-2022-certified-index](https://www.sos.ms.gov/elections/electionresults_aspx/elections_results_2022_certified.aspx) lists
congressional/judicial/district contests; state Senate district headings are not
a statewide U.S. Senate baseline. The actual recent same-seat midterm contests
are **November 6, 2018 special** and **November 27, 2018 runoff**, kept separate.
The [fec-2018-special-rule](https://www.fec.gov/updates/mississippi-special-election-reporting-senate-2018/) specifies majority/top-two special-runoff
rules for that election. The [sos-2018-runoff-certified-sen-pdf](https://www.sos.ms.gov/elections/electionresults/2018GeneralRunoff/Certified%20Results/United%20States%20Senate%20Special.pdf) has both
stages on its complete second page. Its December 3 signed runoff certificate
and December 13 summary clocks are separate observations, not an inferred
release chronology. The [house-clerk-2018-statistics](https://clerk.house.gov/member_info/electionInfo/2018/statistics2018.pdf) (PDF p28, printed
p26) supplies political party identities, but its footnotes substitute runoff
totals for Espy/Hyde-Smith alongside first-stage Bartee/McDaniel figures. Do not
sum that presentation as one electorate. County special ballot party cells
remain blank where blank in the original.

| Historical contest/stage | A | B | Other named candidates, separately | Named votes | A pair share % | A−B pair margin pp | A−B all-named margin pp |
|---|---:|---:|---|---:|---:|---:|---:|
| 2024 Senate, other seat | 451,981 | 763,420 | none published in this named scope | 1,215,401 | 37.1878 | -25.6244 | -25.6244 |
| 2024 president, separate | 466,668 | 747,744 | Chase Oliver 2,536; Jill Stein 1,873; Randall Terry 1,030; Shiva Ayyadurai 688; Claudia De la Cruz 1,075; Robert F. Kennedy Jr. 5,387; Peter Sonski 1,007 | 1,228,008 | 38.4275 | -23.1450 | -22.8888 |
| 2020 Senate, same seat | 578,691 | 709,511 | Jimmy L. Edwards 23,152 | 1,311,354 | 44.9224 | -10.1552 | -9.9759 |
| 2018 special, November 6 | 386,742 | 389,995 | Tobey Bernard Bartee 13,852; Chris McDaniel 154,878 | 945,467 | 49.7906 | -0.4188 | -0.3441 |
| 2018 runoff, November 27 | 420,819 | 486,769 | none published in this named scope | 907,588 | 46.3667 | -7.2665 | -7.2665 |

Complete individual candidate/party literals and source rows are in
[candidate-votes.csv](data/baselines/candidate-votes.csv); independent primary
readings, dates and clocks are in [the state ledger](data/baselines/source/primary-state-readings.json).
The 2020 CSV matches all three candidates in the [sos-2020-amended-sen-pdf](https://www.sos.ms.gov/elections/electionresults/2020General/Statewide%20Certified%20Results/US%20Senate_AMENDED.pdf):
578,691 / 709,511 / 23,152. The [sos-2020-certified-sen-pdf](https://www.sos.ms.gov/elections/electionresults/2020General/Statewide%20Certified%20Results/US%20Senate.pdf) instead prints
578,806 / 709,539 / 23,152, 143 more in total; both vintages survive. No county
residual is allocated from that difference.

The independent [2020 county-publication audit](data/baselines/county-2020-publication-controls.json)
now reads all **104 actual county packets: 82 original publications and 22
explicit Amended alternatives**, preserving all 312 printed Senate TOTAL fields.
Using each explicitly amended publication where available, otherwise its
original, reproduces every county CSV value and the amended statewide vector.
Three county publication pairs change: [sos-2020-county-adams](https://www.sos.ms.gov/elections/electionresults/2020General/County%20Recapitulation%20Reports/Adams.pdf) p4 versus
[sos-2020-county-adams-amended](https://www.sos.ms.gov/elections/electionresults/2020General/County%20Recapitulation%20Reports/Adams_Amended.pdf) p3 changes Espy 7,736→8,190 (+454);
[sos-2020-county-coahoma](https://www.sos.ms.gov/elections/electionresults/2020General/County%20Recapitulation%20Reports/Coahoma.pdf) versus [sos-2020-county-coahoma-amended](https://www.sos.ms.gov/elections/electionresults/2020General/County%20Recapitulation%20Reports/Coahoma_Amended.pdf)
p3 changes 6,452/2,161/46→6,337/2,133/46 (−115/−28/0); and
[sos-2020-county-prentiss](https://www.sos.ms.gov/elections/electionresults/2020General/County%20Recapitulation%20Reports/Prentiss.pdf) versus [sos-2020-county-prentiss-amended](https://www.sos.ms.gov/elections/electionresults/2020General/County%20Recapitulation%20Reports/Prentiss_Amended.pdf)
p3 changes 2,694/7,603/227→2,714/7,651/229 (+20/+48/+2).
The sum of all original county publications is 578,332/709,491/23,150,
which differs from the original statewide summary by −474/−48/−2.
Thus Coahoma matching the statewide amendment vector does not establish that
it was the only county publication to change, or that all original packets
share a certificate vintage. No chronology or residual assignment is inferred.
The [flat publication file](data/baselines/county-2020-publication-candidate-votes.csv)
preserves its earlier numeric/locator scope: 51 TOTAL ordinals were accepted
and 53 were targeting proposals at that checkpoint. The later
[physical TOTAL audit](data/baselines/native-2020-physical-TOTAL-audit.json)
independently counts actual columns in all 104 complete native grids; it
supersedes those locator proposals for the three-candidate Senate scope,
while preserving the earlier ledger unchanged.

The [2020 native coverage ledger](data/baselines/native-2020-coverage.json)
keeps all 104 publication vintages visible. Its current independent original
readings cover 104 publication
views and 2131 constituents across those
separate vintages; only 82
selected county views / 1765
native units enter its amended-where-linked comparison. Their Senate sum is
**578,691 / 709,511 / 23,152**, exactly the amended certificate and county CSV.
One printed Harrison administrative column is counted separately. The three-candidate native scope is complete: **2,131 native observations
across 104 publications**, with 104 TOTALs, 536 unused columns and one
separate Harrison administrative column. The [complete immutable witness](data/baselines/source/native-2020-104views-v1/snapshot.json)
and [flat source fields](data/baselines/native-2020-additional-candidate-votes.csv)
retain original hashes/pages/physical positions and all three identities.
Every source vector closes its own printed TOTAL. The selected82 partition
contains **1,765 native constituents**; original/amended alternatives remain
separate even where votes agree. Generic/method/ballot/registration fields
are unprinted in these selected SEMS candidate grids and are not zero-filled.
Complete packet-layout and printed-field availability are audited separately below.
Literal labels, original reading repairs, the earlier targeting proposals
and every dated immutable witness remain in the schema and correction ledgers.
Kemper's original header is **Lynville**, one n; old frozen55/60/65 **Lynnville**
readings remain unchanged. Broad band windows are reading aids, not exact
numeric polygons or current identities.

The new [41-publication reverse replay](data/baselines/native-2020-peer-41views-v3-reconciliation.json)
reuses those exact frozen38 bodies and adds Webster and both Prentiss
publications: 565 native observations, 2,475 candidate positions, all values,
roles and whitespace-folded literal labels matching. The older38 metadata
declarations remain their frozen versions; this is not a claim all41 bodies
are current mutable peer files. All earlier witnesses remain unchanged.


Both 2018 stages now have independently read county TOTALs for all 82 counties
in [the county-stage ledger](data/baselines/county-2018-readings.json): all 492
candidate fields reproduce the two statewide vectors exactly. The correction
history retains earlier Choctaw/Quitman manual digit errors and the original
magnified cells used to correct them. A later [complete-original native review](data/baselines/native-2018-original-readings.json)
reads Issaquena's five precincts separately for each stage: 36 numeric and 30
unused/null candidate positions, with each vector closing its printed TOTAL.
Both originals place TOTAL at physical column6. The prior special-election
machine ordinal4 merged three printed columns; the original target box and
four candidate totals were correct. The [prior ledger bytes](data/baselines/source/2018-physical-column-corrections-v1/prior-ledger-pin.json)
and explicit correction history remain separate. The current reverse comparison
records any peer ordinal still carrying4 as a metadata difference, without
calling it physical-column agreement. Party labels are unprinted beside these
special/runoff rows; named candidates and stages remain distinct.
The [complete original native ledger](data/baselines/native-2018-original-readings.json)
keeps all 164 stages separately. The historical regular ClassI contest and
unrelated offices remain intact in original bytes and are excluded from the
ClassII vectors. Literal-source correction histories preserve `Mclain`,
`Mccall` and `Mhoon Landing`, previous readings and all unchanged source votes.
No name, stage count or machine ordinal establishes current identity.

The complete [sos-2018-county-leflore](https://www.sos.ms.gov/elections/electionresults/2018General/County%20Recaps/Leflore.pdf)
PDF2/3 prints 18 Espy native cells summing **5,853**, against printed TOTAL
**5,863**. The other three named vectors close at Bartee185, Hyde-Smith2,199
and McDaniel493. [Own original row evidence](data/baselines/source/2018-leflore-native-TOTAL-exception-v1.json)
retains every glyph and the ten-vote source disagreement unallocated; county
certification controls and source-native weights remain separate. A stale
94-view output was inadvertently frozen as 98-view v1 after the initial builder
failed this closure. [The rejection record](data/baselines/source/native-2018-witness-rejections.json)
preserves and verifies those exact bytes, excludes them from accepted coverage,
and requires the separate 98-view v2. The freeze now requires requested,
builder and validator counts to agree before writing. [Bounded validation](data/baselines/native-2018-validation.json)
checks this exclusion, the single source discrepancy and prior witness continuity.

The [latest accepted source witness](data/baselines/source/native-2018-164views-v1/snapshot.json) now contains
**164 of 164 stage grids / 3,545
native observations across separate electorates**, 164 TOTALs,
842 unused columns and 3 administrative columns on
414 complete original pages. It preserves 11,126
numeric, 2,530 unused/null and 6 literal `X` positions.
The known numeric candidate vectors close their own printed controls except
Leflore's explicit Espy−10 source difference. All164 actual stage grids now have
original candidate/header review; this is narrower than full method/ballot controls.
Rankin prints50 native special columns but51 runoff columns, including `Mullins`
with literal X/X and null numeric values; Claiborne retains four more X positions.
Harrison's two `Invalid Addresses 9999` columns and JeffDavis's `PURGED VOTERS`
column remain separate administrative observations. No mark is converted to zero.
Both complete Tunica PDF2 originals and own unchanged-pixel upright crops
confirm the literal header `Mhoon Landing`. The
[separate header-correction history](data/baselines/source/2018-tunica-header-correction-v1.json)
pins the earlier142-view-v1 bodies and documents only two source-header objects
and six candidate-row label changes from `Moon Landing`; all votes, roles,
physical positions and original hashes remain unchanged. Frozen witnesses are
retained unchanged, without a geographic alias or current-ID join.
No cross-stage/current-ID or missing-method inference follows.

**Explicit 2024 repair and denominator limits.** The source CSV has Pinkins
450,749 and Wicker 761,934. The actual county index contains 84 links for 82
counties, including both original and explicitly Updated Pike/Coahoma files.
Independently rendered [sos-2024-county-pike-updated](https://www.sos.ms.gov/elections/electionresults/2024General/County%20Results/Pike%20Updated.pdf) p4 gives Pike
7,130 / 8,205 versus the CSV's 5,898 / 6,719. Those explicit candidate changes
of +1,232 / +1,486 explain all 2,718 Senate votes. Its nine presidential values
explain all 2,770 presidential votes and reproduce every signed candidate in
the [sos-2024-certified-pres-pdf](https://www.sos.ms.gov/elections/electionresults/2024General/Statewide%20Results/Certification%20of%20Vote%20for%20Electors%20for%20President%20and%20Vice%20President.pdf). No scaling or imputed allocation is
used. Coahoma's original and updated Senate totals agree with the CSV; no
cause of its update or certification/release sequence is inferred.

The certified Senate denominator is **1,215,401 two-name votes**, not all marks
or ballots. For example [sos-2024-county-lauderdale](https://www.sos.ms.gov/elections/electionresults/2024General/County%20Results/Lauderdale.pdf) p3 separately prints
Pinkins 10,139, Wicker 16,873, **79 generic write-in marks**, 10 overvotes and
492 undervotes, summing to 27,593 contest opportunities. Its literal methods
are Election Day, Absentee, Affidavit, 5 Day Absentee and Resolution. Generic
marks are not assumed valid named/write-in votes; absent generic fields in
other counties are not zero. This source-specific scope does not mutate the
certified two-name priority denominator.

**Primary native order and proposed exact 80% prefix.** The independent
[full native order](data/baselines/native-full-order.csv) contains all **1,736
preferred source-native units**. [All 84 separate source-view orders](data/baselines/native-source-orders.json)
retain original alternatives independently. The first 15 native units contribute
**60,019 / 1,215,400** source-native named votes. The descending prefix needs
**887 native units** to reach 80%: the first 886 supply **972,157**, below the
native integer threshold 972,320, and the first 887 supply **972,656**.
The crossing unit is [sos-2024-county-lauderdale](https://www.sos.ms.gov/elections/electionresults/2024General/County%20Results/Lauderdale.pdf) PDF9 physical column5,
printed **450 - Pickard**, Pinkins119/Wicker380, contribution499. All **849
nonpriority units / 242,744 source votes** remain in every complete native
state calculation. The signed county denominator 1,215,401 is separate; its
integer threshold 972,321 gives the same 887-unit prefix. Tunica's one unknown
vote remains unallocated: even the arithmetic upper bound 972,157+1 is below
both thresholds; its largest published unit394+1 cannot reach the499 cutoff.
No placement is inferred. Literal source-position keys break ties explicitly;
this selects one prefix, not a claim of a unique possible 80%-covering set.

[Independent reciprocal comparison](data/baselines/native-order-peer-reconciliation.json)
checks all 84 orders and every preferred native key, parent, rank, candidate
value and cumulative count. It preserves the working peer's 43 optional-ID
extraction additions separately from unchanged frozen84 nulls, plus explicit
wrap representations; literal headers and fallback source-position keys stay
intact. The [pinned native contract proposal](data/baselines/native-priority-contract.json)
uses **887 native units as primary**, with county-parent child-key lists and
all nonpriority keys. Those priority children occur in **77 county parents**;
five parents have no priority child. This is distinct from the 41-county
sensitivity. The immutable [v1 snapshot](data/baselines/source/native-priority-v1/snapshot.json)
pins the contract, full order, flat file and reciprocal proof together.
Coordinator acceptance and current 2026 reporting/geography approval remain
external qualifications. The completed retained-source field inventory below
does not self-approve the 887-unit dispatch proposal.

The separate **[v2 complete-field proposal](data/baselines/source/native-priority-v2/snapshot.json)**
now freezes all 2,266 preferred source columns / 24,926 candidate/null fields
and the [full 1,736-unit order with all eleven values](data/baselines/native-priority-source-fields-v2.csv).
The 887/849 arrays, all82 parent/child maps and77 priority authorities are
unchanged. The [immutable field-evidence companion](data/baselines/source/native-priority-v2-field-evidence-v1/snapshot.json)
pins all located printed controls and bounded historical peer bodies together
with that proposal. Its [independent validator](data/baselines/native-priority-v2-independent-validation.json)
reconstructs order and integer crossing without importing the producer. V1
remains byte-for-byte intact. Both versions retain Tunica's unallocated source
differences and explicit unknown fields; **v2 also awaits coordinator acceptance
and establishes no current2026 identity or dispatch authority**.

**Same-seat 2020 native arithmetic.** The independently reviewed 104 actual
2020 county publications supply 2,131 native observations across separate
versions. The [historical native calculator](data/baselines/historical_native_calculator.py)
uses the selected 82-publication partition's **1,765 native units** and actual
pair 1,288,202, preserving Jimmy L. Edwards's Libertarian 23,152 separately
(named denominator 1,311,354). Each of the 22 other county publications is
also a separate whole-county replacement partition; every state case retains
all 82 counties. No amendment pair is added together or joined by native name.

[Settings and output pins](data/baselines/native-2020-calculator-settings.json)
declare historical low2022EAC/base2024county/high2020native volume, separate
2018-stage mixes and five preference anchors. Only the 2020 anchor uses its
actual native preferences; other-year county preferences/mixes are conditional
assumptions over the 2020 native weights. The 90 preferred and 44 replacement
cases have [state targets](data/baselines/native-2020-state-targets.csv),
[all-county contributions](data/baselines/native-2020-county-contributions.csv),
236,510 native target/contribution rows in 31 lossless compressed files and
[4,264 local rows](data/baselines/native-2020-local-targets.csv), including the
separate zero-pool administrative observation. Selected-unit-only rows keep
every other unit fixed at the explicit scenario assumptions. Native outsiders
are retained individually and generic marks remain unresolved.

At observed 2020 volume/preference, Espy begins130,820 net votes behind.
The unbounded tie shift is5.077620 share points; clipping requires5.235635
(117 clipped units). A+1 pair margin needs5.766646 share points (124 clipped),
with target net12,882.02 votes. This bounded increment differs from the
unbounded0.5-share-point increment. [Independent validation](data/baselines/native-2020-target-validation.json)
integrates clipping breakpoints without importing bisection and checks all
3,311,140 native formulas, source keys and all82 county contributions.
Pair targets do not replace the ordinary plurality condition or map historical
candidates onto the actual 2026 field.

**Separate 2018 native arithmetic.** The complete [sos-2018-general-index](https://www.sos.ms.gov/elections-voting/election-results/2018/2018-general-election)
and [sos-2018-runoff-index](https://www.sos.ms.gov/elections-voting/election-results/2018/2018-general-election-runoff) originals supply 1,771 November6
native columns and 1,774 November27 columns. Three runoff columns contain
literal X/X; all 3,545 native observations stay in every corresponding output.
The [calculator](data/baselines/native_2018_calculator.py) models only the
explicit known numerical pool, with [settings and lossless file pins](data/baselines/native-2018-calculator-settings.json).
November6 known Espy386,732/Hyde-Smith389,995 pair776,727 plus separately
named Bartee13,852/McDaniel154,878 gives945,457 named votes; certified
county945,467 remains separate because LefloreEspy10 is unallocated.
Runoff known420,819/486,769 gives907,588; X fields remain numerical unknowns
although all known numeric cells close the printed TOTALs.

There are [180 state cases](data/baselines/native-2018-state-targets.csv),
[14,760 county contributions](data/baselines/native-2018-county-contributions.csv),
319,050 native rows in18 lossless files and
[7,096 local targets](data/baselines/native-2018-local-targets.csv).
Each stage separately uses observed native weights, historical low2022EAC,
base2024Senate/high2020Senate county pools, other-stage mix sensitivity,
common-volume variants and five named preference anchors. Other-year county
mix/preference assumptions do not establish native joins, candidate effects,
lower preferences or2026 forecasts. Selected-unit-only break-even keeps every
other known unit in all82 parents fixed at those stated assumptions; unknown X
units have explicit unknown status, zero administrative pools have no-pool status.

At observed November6 known-source volume/preference, the unbounded tie shift
is0.210048 share points; bounded clipping needs0.210108 (one clipped unit).
The A+1 pair target needs0.710678 share points (six clipped). Yet its all-named
majority cushion is **−160,962.73 votes**, so this pair target does not elect
Espy in the four-candidate majority special. Named majority requires
A pair share strictly above `(pair + Bartee + McDaniel)/(2*pair)`; valid
write-in scope remains separate. Observed runoff tie needs3.776461 bounded
share points (111 clipped), and A+1 needs4.309915 (113 clipped). Pair share,
margin points, net votes and named denominators are separate columns.
[Independent verification](data/baselines/native-2018-target-validation.json)
checks4,462,920 formulas using breakpoint slope integration rather than the
calculator's bisection: maximum net error below8e−11 votes. No state contains
an allocated Leflore residual, an X-to-zero conversion or a merged electorate.

**County parent sensitivity and practical targets.** The [82-row county file](data/county-baselines.csv)
contains all candidates' aggregate A/B/other values, all-named and pair
denominators, EAC controls and historical margins. The complete descending
order agrees independently with the turnout peer on all 82 keys, 1,148
2024/2020 literal candidate rows and 492 separate 2018 candidate fields;
[reconciliation](data/baselines/peer-reconciliation.json)
pins both artifacts' hashes. Top 15 supply **653,846 / 1,215,401 = 53.796730%**.
The minimum 80% prefix is **41 counties ending at Newton**: the first 40 have
970,209 (<972,320.8); 41 have 979,428 (80.584762%). The coordinator alone accepts
the priority contract. This 41-county calculation is a separate parent
sensitivity and never substitutes for the primary 887-native prefix. The CSV's
legacy `priority` flag is explicitly scoped to this county-parent sensitivity.
No 2026 native/boundary identity follows from rank.

Margins below use A−B pair percentage points, with A the named historical
Democrat. Target shares are one interchangeable statewide combination, not
necessary county-by-county requirements. One share point adds twice as many
margin points and `0.02*county_pair_votes` net votes at fixed pair turnout.

| Rank | County | 2024 Senate A / B | Senate pair margin pp | President pair margin pp | 2020 Senate pair margin pp | 2018 special pair margin pp | 2018 runoff pair margin pp | State weight % | Tie A share % | A+1 A share % | +1 share pp net votes |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Hinds | 60,625 / 25,901 | +40.13 | +46.73 | +52.26 | +53.87 | +54.04 | 7.119 | 82.878 | 83.378 | 1,730.52 |
| 2 | DeSoto | 28,914 / 49,073 | -25.85 | -24.70 | -16.23 | -9.88 | -18.11 | 6.417 | 49.888 | 50.388 | 1,559.74 |
| 3 | Harrison | 25,289 / 49,863 | -32.70 | -29.24 | -17.42 | -13.97 | -18.58 | 6.183 | 46.463 | 46.963 | 1,503.04 |
| 4 | Rankin | 17,267 / 51,542 | -49.81 | -47.62 | -40.96 | -38.06 | -42.58 | 5.661 | 37.906 | 38.406 | 1,376.18 |
| 5 | Madison | 21,180 / 34,181 | -23.48 | -17.50 | -8.42 | -7.49 | -9.66 | 4.555 | 51.070 | 51.570 | 1,107.22 |
| 6 | Jackson | 14,932 / 37,059 | -42.56 | -40.33 | -26.96 | -21.52 | -28.65 | 4.278 | 41.533 | 42.033 | 1,039.82 |
| 7 | Lee | 10,352 / 24,415 | -40.45 | -39.26 | -25.94 | -19.98 | -27.13 | 2.861 | 42.588 | 43.088 | 695.34 |
| 8 | Forrest | 11,221 / 17,104 | -20.77 | -18.19 | -3.90 | +8.07 | -1.51 | 2.331 | 52.427 | 52.927 | 566.50 |
| 9 | Lamar | 6,863 / 20,984 | -50.71 | -49.39 | -41.20 | -38.87 | -45.57 | 2.291 | 37.458 | 37.958 | 556.94 |
| 10 | Jones | 7,246 / 20,307 | -47.40 | -47.18 | -35.77 | +12.91 | -31.79 | 2.267 | 39.111 | 39.611 | 551.06 |
| 11 | Lauderdale | 10,139 / 16,873 | -24.93 | -21.39 | -11.58 | -10.13 | -14.22 | 2.222 | 50.347 | 50.847 | 540.24 |
| 12 | Lowndes | 10,690 / 13,548 | -11.79 | -8.23 | +3.10 | +5.70 | +2.75 | 1.994 | 56.916 | 57.416 | 484.76 |
| 13 | Pearl River | 4,012 / 20,157 | -66.80 | -67.39 | -55.81 | -40.91 | -56.96 | 1.989 | 29.412 | 29.912 | 483.38 |
| 14 | Lafayette | 8,447 / 14,761 | -27.21 | -22.14 | -5.76 | +3.08 | -1.22 | 1.909 | 49.209 | 49.709 | 464.16 |
| 15 | Hancock | 4,104 / 16,797 | -60.73 | -59.30 | -44.02 | -35.99 | -48.14 | 1.720 | 32.448 | 32.948 | 418.02 |
| 16 | Warren | 8,272 / 9,770 | -8.30 | -4.00 | +4.53 | +9.85 | +5.82 | 1.484 | 58.661 | 59.161 | 360.84 |
| 17 | Oktibbeha | 8,325 / 9,498 | -6.58 | -0.28 | +11.70 | +12.25 | +12.29 | 1.466 | 59.521 | 60.021 | 356.46 |
| 18 | Monroe | 5,025 / 10,920 | -36.97 | -36.18 | -24.03 | -16.56 | -20.09 | 1.312 | 44.327 | 44.827 | 318.90 |
| 19 | Lincoln | 4,080 / 11,599 | -47.96 | -45.69 | -36.80 | -37.18 | -36.10 | 1.290 | 38.834 | 39.334 | 313.58 |
| 20 | Pike | 7,130 / 8,205 | -7.01 | -3.53 | +5.87 | +9.47 | +7.07 | 1.262 | 59.307 | 59.807 | 306.70 |
| 21 | Alcorn | 2,280 / 12,576 | -69.31 | -68.93 | -52.27 | -47.94 | -54.72 | 1.222 | 28.160 | 28.660 | 297.12 |
| 22 | Marshall | 6,634 / 8,100 | -9.95 | -7.33 | +10.88 | +25.82 | +17.34 | 1.212 | 57.837 | 58.337 | 294.68 |
| 23 | Panola | 5,978 / 8,374 | -16.69 | -15.01 | +3.43 | +15.05 | +10.43 | 1.181 | 54.465 | 54.965 | 287.04 |
| 24 | Washington | 9,406 / 4,926 | +31.26 | +35.36 | +45.79 | +45.98 | +45.76 | 1.179 | 78.442 | 78.942 | 286.64 |
| 25 | Pontotoc | 2,304 / 11,556 | -66.75 | -68.27 | -54.69 | -44.31 | -55.97 | 1.140 | 29.436 | 29.936 | 277.20 |
| 26 | Tate | 3,498 / 9,225 | -45.01 | -44.19 | -26.46 | -13.51 | -20.99 | 1.047 | 40.306 | 40.806 | 254.46 |
| 27 | Union | 1,779 / 10,484 | -70.99 | -70.77 | -56.51 | -52.57 | -59.97 | 1.009 | 27.319 | 27.819 | 245.26 |
| 28 | Adams | 6,560 / 5,219 | +11.38 | +14.06 | +20.39 | +27.17 | +22.40 | 0.969 | 68.505 | 69.005 | 235.58 |
| 29 | Copiah | 5,287 / 6,388 | -9.43 | -6.12 | +5.22 | +9.35 | +11.31 | 0.961 | 58.097 | 58.597 | 233.50 |
| 30 | Marion | 3,241 / 7,845 | -41.53 | -42.01 | -30.37 | -20.18 | -27.34 | 0.912 | 42.047 | 42.547 | 221.72 |
| 31 | Simpson | 3,389 / 7,556 | -38.07 | -36.92 | -26.34 | -19.29 | -22.30 | 0.901 | 43.776 | 44.276 | 218.90 |
| 32 | George | 1,216 / 9,662 | -77.64 | -79.30 | -65.39 | -49.62 | -69.29 | 0.895 | 23.991 | 24.491 | 217.56 |
| 33 | Neshoba | 2,539 / 8,245 | -52.91 | -51.34 | -36.80 | -33.64 | -41.40 | 0.887 | 36.356 | 36.856 | 215.68 |
| 34 | Itawamba | 1,114 / 9,337 | -78.68 | -80.53 | -67.99 | -61.90 | -72.00 | 0.860 | 23.471 | 23.971 | 209.02 |
| 35 | Bolivar | 6,200 / 4,101 | +20.38 | +23.90 | +36.73 | +39.95 | +38.80 | 0.848 | 73.001 | 73.501 | 206.02 |
| 36 | Prentiss | 1,717 / 8,504 | -66.40 | -66.49 | -47.63 | -40.67 | -47.86 | 0.841 | 29.611 | 30.111 | 204.42 |
| 37 | Scott | 3,680 / 6,122 | -24.91 | -24.11 | -12.13 | -4.59 | -9.70 | 0.806 | 50.356 | 50.856 | 196.04 |
| 38 | Grenada | 3,989 / 5,689 | -17.57 | -16.38 | -4.96 | +2.96 | -5.34 | 0.796 | 54.029 | 54.529 | 193.56 |
| 39 | Tippah | 1,550 / 7,927 | -67.29 | -67.54 | -50.50 | -46.03 | -51.42 | 0.780 | 29.168 | 29.668 | 189.54 |
| 40 | Leflore | 6,231 / 3,111 | +33.40 | +38.82 | +46.29 | +45.45 | +42.77 | 0.769 | 79.511 | 80.011 | 186.84 |
| 41 | Newton | 2,562 / 6,657 | -44.42 | -43.68 | -33.86 | -21.08 | -33.80 | 0.759 | 40.603 | 41.103 | 184.38 |
| 42 | Clay | 4,886 / 4,228 | +7.22 | +10.50 | +21.27 | +22.85 | +24.11 | 0.750 | 66.422 | 66.922 | 182.28 |
| 43 | Wayne | 3,075 / 6,022 | -32.40 | -33.02 | -20.43 | +0.60 | -14.04 | 0.748 | 46.615 | 47.115 | 181.94 |
| 44 | Yazoo | 4,223 / 4,702 | -5.37 | -2.43 | +12.10 | +14.52 | +14.39 | 0.734 | 60.129 | 60.629 | 178.50 |
| 45 | Tishomingo | 1,038 / 7,824 | -76.57 | -79.50 | -63.81 | -59.54 | -67.14 | 0.729 | 24.525 | 25.025 | 177.24 |
| 46 | Covington | 2,879 / 5,924 | -34.59 | -33.54 | -21.29 | +1.09 | -14.56 | 0.724 | 45.517 | 46.017 | 176.06 |
| 47 | Winston | 3,439 / 4,937 | -17.88 | -18.40 | -5.94 | -0.71 | -4.58 | 0.689 | 53.870 | 54.370 | 167.52 |
| 48 | Leake | 3,116 / 5,229 | -25.32 | -23.56 | -9.52 | +1.20 | -6.56 | 0.687 | 50.152 | 50.652 | 166.90 |
| 49 | Jasper | 3,646 / 4,189 | -6.93 | -5.05 | +5.24 | +36.35 | +13.65 | 0.645 | 59.347 | 59.847 | 156.70 |
| 50 | Stone | 1,510 / 6,282 | -61.24 | -58.64 | -46.45 | -39.50 | -46.70 | 0.641 | 32.191 | 32.691 | 155.84 |
| 51 | Sunflower | 4,659 / 3,074 | +20.50 | +35.74 | +45.60 | +45.55 | +44.54 | 0.636 | 73.060 | 73.560 | 154.66 |
| 52 | Attala | 2,894 / 4,753 | -24.31 | -23.43 | -12.21 | -3.98 | -10.66 | 0.629 | 50.657 | 51.157 | 152.94 |
| 53 | Smith | 1,458 / 6,158 | -61.71 | -61.06 | -51.66 | -32.78 | -47.29 | 0.627 | 31.956 | 32.456 | 152.32 |
| 54 | Clarke | 2,350 / 5,151 | -37.34 | -35.40 | -25.74 | -26.48 | -23.57 | 0.617 | 44.141 | 44.641 | 150.02 |
| 55 | Chickasaw | 3,023 / 4,121 | -15.37 | -13.80 | +2.75 | +9.31 | +4.14 | 0.588 | 55.127 | 55.627 | 142.88 |
| 56 | Amite | 2,294 / 4,514 | -32.61 | -33.25 | -22.50 | -5.67 | -16.22 | 0.560 | 46.508 | 47.008 | 136.16 |
| 57 | Holmes | 5,226 / 1,456 | +56.42 | +62.69 | +69.36 | +70.42 | +71.30 | 0.550 | 91.022 | 91.522 | 133.64 |
| 58 | Coahoma | 4,533 / 2,146 | +35.74 | +40.23 | +49.63 | +50.40 | +49.03 | 0.550 | 80.682 | 81.182 | 133.58 |
| 59 | Walthall | 2,319 / 4,158 | -28.39 | -27.19 | -14.46 | -8.57 | -7.67 | 0.533 | 48.616 | 49.116 | 129.54 |
| 60 | Lawrence | 1,867 / 4,137 | -37.81 | -36.83 | -29.11 | -27.09 | -25.44 | 0.494 | 43.908 | 44.408 | 120.08 |
| 61 | Calhoun | 1,512 / 4,402 | -48.87 | -48.35 | -34.00 | -27.44 | -33.57 | 0.487 | 38.379 | 38.879 | 118.28 |
| 62 | Yalobusha | 2,243 / 3,609 | -23.34 | -21.16 | -6.39 | +0.60 | -2.17 | 0.481 | 51.141 | 51.641 | 117.04 |
| 63 | Greene | 891 / 4,712 | -68.20 | -70.24 | -57.22 | -32.31 | -57.12 | 0.461 | 28.714 | 29.214 | 112.06 |
| 64 | Perry | 1,089 / 4,412 | -60.41 | -60.82 | -46.00 | -30.51 | -44.45 | 0.453 | 32.609 | 33.109 | 110.02 |
| 65 | Jeff Davis | 2,970 / 2,383 | +10.97 | +13.83 | +22.05 | +31.72 | +28.28 | 0.440 | 68.295 | 68.795 | 107.06 |
| 66 | Carroll | 1,378 / 3,746 | -46.21 | -44.55 | -31.80 | -21.59 | -29.34 | 0.422 | 39.705 | 40.205 | 102.48 |
| 67 | Webster | 854 / 4,203 | -66.23 | -65.58 | -54.49 | -51.94 | -55.31 | 0.416 | 29.700 | 30.200 | 101.14 |
| 68 | Tallahatchie | 2,546 / 2,478 | +1.35 | +5.98 | +17.90 | +27.63 | +22.82 | 0.413 | 63.489 | 63.989 | 100.48 |
| 69 | Montgomery | 1,678 / 2,671 | -22.83 | -20.96 | -9.48 | -7.70 | -8.73 | 0.358 | 51.396 | 51.896 | 86.98 |
| 70 | Noxubee | 2,975 / 1,312 | +38.79 | +47.92 | +55.68 | +51.71 | +56.28 | 0.353 | 82.208 | 82.708 | 85.74 |
| 71 | Kemper | 2,234 / 1,824 | +10.10 | +16.94 | +26.57 | +26.10 | +26.95 | 0.334 | 67.864 | 68.364 | 81.16 |
| 72 | Franklin | 1,203 / 2,852 | -40.67 | -40.01 | -28.68 | -17.44 | -22.27 | 0.334 | 42.479 | 42.979 | 81.10 |
| 73 | Choctaw | 937 / 2,866 | -50.72 | -49.82 | -36.09 | -29.06 | -31.79 | 0.313 | 37.451 | 37.951 | 76.06 |
| 74 | Benton | 1,280 / 2,522 | -32.67 | -31.59 | -10.79 | -2.70 | -6.24 | 0.313 | 46.479 | 46.979 | 76.04 |
| 75 | Claiborne | 2,843 / 719 | +59.63 | +68.19 | +75.12 | +70.76 | +74.46 | 0.293 | 92.627 | 93.127 | 71.24 |
| 76 | Humphreys | 2,355 / 1,075 | +37.32 | +42.32 | +50.79 | +50.68 | +52.02 | 0.282 | 81.471 | 81.971 | 68.60 |
| 77 | Jefferson | 2,634 / 693 | +58.34 | +66.89 | +75.61 | +73.06 | +75.88 | 0.274 | 91.983 | 92.483 | 66.54 |
| 78 | Wilkinson | 1,710 / 1,136 | +20.17 | +25.66 | +35.20 | +45.38 | +39.58 | 0.234 | 72.897 | 73.397 | 56.92 |
| 79 | Tunica | 1,798 / 827 | +36.99 | +39.38 | +53.89 | +49.29 | +54.04 | 0.216 | 81.307 | 81.807 | 52.50 |
| 80 | Quitman | 1,629 / 952 | +26.23 | +31.33 | +44.64 | +46.43 | +44.66 | 0.212 | 75.927 | 76.427 | 51.62 |
| 81 | Sharkey | 1,229 / 556 | +37.70 | +37.10 | +39.01 | +38.91 | +41.23 | 0.147 | 81.664 | 82.164 | 35.70 |
| 82 | Issaquena | 291 / 304 | -2.18 | -1.54 | +8.58 | +16.86 | +14.66 | 0.049 | 61.720 | 62.220 | 11.90 |

**Historical volume, mix and preference sensitivity.** Every setting below is
implemented in [calculator.py](data/baselines/calculator.py); all 82 county
rows and selected-only requirements are in [county-targets.csv](data/baselines/county-targets.csv).
Low assigns each 2022 EAC F1a count to an illustrative named-pair pool (100%
assignment, not observed Senate participation). Base repeats actual 2024
two-name Senate volume. High repeats actual 2020 Senate pair volume. Additional
normalized rows isolate county composition at the 2024 pair total. Preference
anchors independently use 2024 Senate, 2024 president, 2020 Senate, 2018 special
or 2018 runoff pair shares. Additional actual midterm volume settings use each
2018 stage's county pair counts, with normalized versions isolating county mix.
All 90 state target settings have matching 82-row county implementations.
These historical ranges do not predict 2026 volume, candidate effects,
transfers from other candidates, lower preferences or remaining ballots.

| Pair-volume setting | Preference anchor | Pair votes | Baseline A−B net | Tie share shift pp | A+1 share shift pp |
|---|---|---:|---:|---:|---:|
| base-2024-Senate | 2024-senate | 1,215,401.00 | -311,439.00 | +12.812191 | +13.312191 |
| low-2022-EAC-counted-ballots | 2024-senate | 708,585.00 | -174,059.37 | +12.282180 | +12.782180 |
| low-2022-EAC-counted-ballots-normalized-to-2024-pair | 2024-senate | 1,215,401.00 | -298,555.48 | +12.282180 | +12.782180 |
| high-2020-Senate | 2024-senate | 1,288,202.00 | -307,659.72 | +11.941439 | +12.441439 |
| high-2020-Senate-normalized-to-2024-pair | 2024-senate | 1,215,401.00 | -290,272.75 | +11.941439 | +12.441439 |
| midterm-2018-special-pair | 2024-senate | 776,737.00 | -155,922.65 | +10.037030 | +10.537030 |
| midterm-2018-special-pair-normalized-to-2024-pair | 2024-senate | 1,215,401.00 | -243,980.33 | +10.037030 | +10.537030 |
| midterm-2018-runoff-pair | 2024-senate | 907,588.00 | -196,381.96 | +10.818894 | +11.318894 |
| midterm-2018-runoff-pair-normalized-to-2024-pair | 2024-senate | 1,215,401.00 | -262,985.88 | +10.818894 | +11.318894 |
| base-2024-Senate | 2024-president | 1,215,401.00 | -280,117.75 | +11.523676 | +12.023676 |
| low-2022-EAC-counted-ballots | 2024-president | 708,585.00 | -155,377.29 | +10.963913 | +11.463913 |
| low-2022-EAC-counted-ballots-normalized-to-2024-pair | 2024-president | 1,215,401.00 | -266,511.02 | +10.963913 | +11.463913 |
| high-2020-Senate | 2024-president | 1,288,202.00 | -273,347.14 | +10.609638 | +11.109638 |
| high-2020-Senate-normalized-to-2024-pair | 2024-president | 1,215,401.00 | -257,899.29 | +10.609638 | +11.109638 |
| midterm-2018-special-pair | 2024-president | 776,737.00 | -133,047.54 | +8.564516 | +9.064516 |
| midterm-2018-special-pair-normalized-to-2024-pair | 2024-president | 1,215,401.00 | -208,186.44 | +8.564516 | +9.064516 |
| midterm-2018-runoff-pair | 2024-president | 907,588.00 | -170,870.54 | +9.413442 | +9.913442 |
| midterm-2018-runoff-pair-normalized-to-2024-pair | 2024-president | 1,215,401.00 | -228,822.14 | +9.413442 | +9.913442 |
| base-2024-Senate | 2020-senate | 1,215,401.00 | -145,067.53 | +5.967888 | +6.467888 |
| low-2022-EAC-counted-ballots | 2020-senate | 708,585.00 | -76,967.23 | +5.431051 | +5.931051 |
| low-2022-EAC-counted-ballots-normalized-to-2024-pair | 2020-senate | 1,215,401.00 | -132,018.10 | +5.431051 | +5.931051 |
| high-2020-Senate | 2020-senate | 1,288,202.00 | -130,820.00 | +5.077620 | +5.577620 |
| high-2020-Senate-normalized-to-2024-pair | 2020-senate | 1,215,401.00 | -123,426.88 | +5.077620 | +5.577620 |
| midterm-2018-special-pair | 2020-senate | 776,737.00 | -48,739.51 | +3.137453 | +3.637453 |
| midterm-2018-special-pair-normalized-to-2024-pair | 2020-senate | 1,215,401.00 | -76,265.26 | +3.137453 | +3.637453 |
| midterm-2018-runoff-pair | 2020-senate | 907,588.00 | -71,638.40 | +3.946637 | +4.446637 |
| midterm-2018-runoff-pair-normalized-to-2024-pair | 2020-senate | 1,215,401.00 | -95,934.92 | +3.946637 | +4.446637 |
| base-2024-Senate | 2018-special | 1,215,401.00 | -63,304.19 | +2.604251 | +3.104251 |
| low-2022-EAC-counted-ballots | 2018-special | 708,585.00 | -29,157.80 | +2.057466 | +2.557466 |
| low-2022-EAC-counted-ballots-normalized-to-2024-pair | 2018-special | 1,215,401.00 | -50,012.93 | +2.057466 | +2.557466 |
| high-2020-Senate | 2018-special | 1,288,202.00 | -45,296.99 | +1.758148 | +2.258148 |
| high-2020-Senate-normalized-to-2024-pair | 2018-special | 1,215,401.00 | -42,737.09 | +1.758148 | +2.258148 |
| midterm-2018-special-pair | 2018-special | 776,737.00 | -3,253.00 | +0.209402 | +0.709402 |
| midterm-2018-special-pair-normalized-to-2024-pair | 2018-special | 1,215,401.00 | -5,090.14 | +0.209402 | +0.709402 |
| midterm-2018-runoff-pair | 2018-special | 907,588.00 | -13,186.11 | +0.726437 | +1.226437 |
| midterm-2018-runoff-pair-normalized-to-2024-pair | 2018-special | 1,215,401.00 | -17,658.24 | +0.726437 | +1.226437 |
| base-2024-Senate | 2018-runoff | 1,215,401.00 | -139,910.33 | +5.755727 | +6.255727 |
| low-2022-EAC-counted-ballots | 2018-runoff | 708,585.00 | -73,345.70 | +5.175504 | +5.675504 |
| low-2022-EAC-counted-ballots-normalized-to-2024-pair | 2018-runoff | 1,215,401.00 | -125,806.27 | +5.175504 | +5.675504 |
| high-2020-Senate | 2018-runoff | 1,288,202.00 | -124,277.84 | +4.823694 | +5.323694 |
| high-2020-Senate-normalized-to-2024-pair | 2018-runoff | 1,215,401.00 | -117,254.45 | +4.823694 | +5.323694 |
| midterm-2018-special-pair | 2018-runoff | 776,737.00 | -44,126.48 | +2.840504 | +3.340504 |
| midterm-2018-special-pair-normalized-to-2024-pair | 2018-runoff | 1,215,401.00 | -69,047.02 | +2.840504 | +3.340504 |
| midterm-2018-runoff-pair | 2018-runoff | 907,588.00 | -65,950.00 | +3.633256 | +4.133256 |
| midterm-2018-runoff-pair-normalized-to-2024-pair | 2018-runoff | 1,215,401.00 | -88,317.27 | +3.633256 | +4.133256 |

The conditional all-candidate denominator in the target files adds the anchor's
actual named outsiders, held fixed county by county, to the scenario pair pool.
It is separately labeled, with pair participation and all-candidate cushion;
generic marks remain unresolved. These outsiders retain their names in the
candidate ledger, never become Democrats, and are not mapped onto 2026 rivals.
In the 2018 November special, even A+1 among Espy and Hyde-Smith would leave
Bartee and McDaniel outside the pair: an Espy–Hyde-Smith pair tie or A+1 does
not meet the special election's majority threshold. At the fixed full field of
945,467, a majority needs at least 472,734 votes; November and runoff voters
are not assumed the same people and no transfer rate is inferred.

The [EAC 2022 v1.1 CSV](https://www.eac.gov/sites/default/files/2023-12/2022_EAVS_for_Public_Release_nolabel_V1.1_CSV.zip)
reports F1a 708,585 counted-ballot voters, registration 2,081,999 = active
1,922,707 + inactive 159,292. The [2024 v2 CSV](https://www.eac.gov/sites/default/files/2026-02/2024_EAVS_for_Public_Release_nolabel_V2_csv.zip)
reports F1a 1,225,176, registration 2,131,726 = active 1,965,948 + inactive
165,778. These survey cohorts are election-associated administrative counts,
not certified candidate totals or VEP. The original [2022 survey](https://www.eac.gov/sites/default/files/EAVS%202022/2022_EAVS_FINAL_508c.pdf)
and [2024 survey](https://www.eac.gov/sites/default/files/2024-04/2024_EAVS_FINAL_508c.pdf)
define A1 and F1; raw all-county values, comments, sentinel codes and source
positions survive. MS comments combine in-person/mail absentee; no mail-only
mix is inferred. 2024 F1a is below the Senate named pair in Pike, Copiah, Clay,
Winston, Tallahatchie, Claiborne, Jefferson and Sharkey. No ratio greater than
one is called a participation probability; these source disagreements remain.

The original F1 instruments define Election Day physical polling independently
of their abbreviated codebook labels and exclude provisional/mail drop-offs
from that subfield. All 82 F2 source flags are retained: 2022 identifies SEMS
under Other; 2024 marks the first four listed record sources. Those flags do
not resolve the different ballot/candidate universes.

**Bounded and selected-only arithmetic.** With pair volumes `T_u`, anchor
shares `s_u` and target net `G`, baseline `M=ΣT_u(2s_u−1)`, the unbounded
uniform share shift is `(G−M)/(2ΣT_u)`. For a tie this is `(B−A)/(2(A+B))`;
A+1 pair margin adds 0.5 share points when the unbounded shift is feasible.
The implementation explicitly clips shares to [0,1] and solves the monotone
bounded equation, retaining unbounded infeasibility, already-winning baselines,
impossible targets and no-positive-pool cases. The historical county base
tie/A+1 scenarios require no clipping. Fractional scenario votes are arithmetic
expectations, not rounded observed votes.

For selected unit `u` with all others fixed at the explicit row assumptions,
`q_u=[T_u+G−Σ_other T_j(2q_j−1)]/(2T_u)`. Raw requirements below zero are already
above target at zero selected share; requirements above one are impossible.
Every other county remains in the sum, including all nonpriority counties.
Use `--county Hinds --others-shift-pp 0 --target-pair-margin-pp 0` to vary it.

**Offline live remainder.** The same calculator accepts `--live-json FILE`:
an explicit counted dictionary by candidate and remaining units with stated
all-candidate pool sizes and shares. Counted A/B/other votes stay fixed; only
the stated remainder is forecast. Unknown remains unknown and negative pools
are rejected. Final pair/all-candidate denominators include counted plus
remaining votes. A+1 targets 1% of the **final pair denominator**, not only the
remainder. Selected-unit solves keep every other remaining unit at its input
shares and every counted candidate fixed, and require A to exceed each rival
for strict plurality. [Synthetic scenarios](data/baselines/synthetic-scenarios.json)
cover unknown/no/negative pools, secured/impossible thresholds, clipping,
an Independent Pinkins pair, and a pair winner who still loses to Pinkins.
They are arithmetic tests, not calibrated probabilities or November forecasts.

The [new frozen historical reciprocal comparison](data/baselines/native-2018-peer-41views-v3-reconciliation.json)
checks **41 independently original-read stage grids, 578 native observations
and 2,530 candidate/blank positions** after this package's all164 original
reading. Every raw hash, FIPS, physical source position, value, role and
whitespace-folded literal label agrees. This is a bounded independent replay;
the other 123 original-read stages retain their own source evidence and
coordinator pin/arithmetic audits. Earlier 10/12-stage witnesses remain unchanged.

**Native coverage and reproducibility.** Original bytes are retained or reused
read-only by exact hashes, including all 84 2024 county originals, all 164
2018 stage originals and all 104 2020 original/amended county publications.
The [source ledger](data/baselines/source/references.json) pins URLs, parents,
UTC retrieval, HTTP headers/status and raw/stored hashes/sizes. No file is
intentionally truncated or simplified; lossless gzip reconstructs originals.
The [schema](data/baselines/source/SCHEMA.md), [native source inventory](data/baselines/native-source-inventory.json),
[native cell observations](data/baselines/native-raw-cells.csv.gz) and
[coverage audit](data/baselines/native-coverage.json) preserve source page/column
identities, TOTAL/unused positions, method/control fields and unresolved OCR.
OCR is a reading aid. No historical name or column count proves a November
2026 reporting identity, administrative mapping, geometry or current approval.

Independent [15 summary-page readings](data/baselines/canvass-readings.json) and
[14 statistics panels](data/baselines/canvass-statistics-readings.json) preserve
all printed candidate, generic, method, under/over, ballots, registration and
blank fields in those panels, with statuses/clocks and source-vintage limits.
For example original Pike ballots 12,824 are not spliced into updated Pike,
and Quitman's 2,739 voting-method ballots differ from its 2,737 Senate and
presidential scan/manual processing universe. All original pages remain intact.
The [sos-2024-county-lincoln](https://www.sos.ms.gov/elections/electionresults/2024General/County%20Results/Lincoln.pdf) PDF9 independently prints **15,898 ballots**, equal to its two
contest totals, with registration 0 unusable; Senate residual 172 and
presidential residual 69 remain unclassified. See the [original reading](data/baselines/source/2024-lincoln-independent-controls.json).
The [sos-2024-county-montgomery](https://www.sos.ms.gov/elections/electionresults/2024General/County%20Results/Montgomery.pdf) PDF3 independently prints **885 ballots, 6,291 registered and
14.07%**, below its separate 4,349 named Senate / 4,424 named presidential
votes. The [complete original panel](data/baselines/source/2024-montgomery-independent-controls.json)
is retained literally, with statistics clock 10:24 AM and candidate summary
10:25 AM. These inconsistent scopes do not identify a chronology or corrected
ballot volume; neither is scaled or allocated.

Direct complete native reviews include [Coahoma Updated's 18 constituents](data/baselines/coahoma-updated-readings.json)
and [Alcorn's 17](data/baselines/alcorn-readings.json), all nine presidential
and two Senate candidates. Alcorn's explicit correction history preserves two
offsetting Sonski reading errors; county closure alone did not detect them.
Hinds's 108 Senate constituents reconcile separately in the
[native reading ledger](data/baselines/native-readings.json).
These bounded reviews do not establish complete statewide native acceptance.

The frozen independent [40-source Senate replay](data/baselines/native-2024-senate-reviewed-40views.json)
preserves **985 constituent columns, 40 separate TOTALs and 196 unused
columns** across 111 original pages. Its [flat file](data/baselines/native-2024-senate-reviewed-40views.csv)
retains both candidate cells, literal headers, source hashes, page/physical
bounds and source-scoped parsed label codes. All 2,442 candidate positions
agree with independently read peer originals: 1,970 constituent values, 80
TOTAL values and 392 unused nulls. Extraction used frozen position hints that
exclude peer votes and labels; original bytes were independently rendered and
read. Explicit original visual repairs retain the preceding machine readings.
The source publications remain the actual SOS county recapitulations, linked
from the [official county index](https://www.sos.ms.gov/elections/electionresults_aspx/elections_results_2024_county.aspx);
individual exact routes/hashes and positions are pinned in the source ledger.
Smith and Jones line-wrap representation differences survive explicitly.
[Validation](data/baselines/native-reviewed-validation.json) checks every
covered parent and source-bound position. This two-candidate set does not
establish complete nine-candidate presidential or whole-state native coverage.

[Native selected-unit targets](data/baselines/native-selected-targets.csv.gz)
contain **88,650** rows: 985 native constituents under the same 90 volume,
preference and target settings, with [explicit settings](data/baselines/native-calculator-settings.json).
Every state net and denominator includes **all 82 counties**. The selected
unit may move while every other geography stays at its stated anchor and
volume; unbounded requirements, impossible shares and clipped displays are
separate. Source2024 native weights within each parent remain fixed for other
historical county-volume sensitivities; this is a conditional mix assumption,
not a cross-year native identity or measured native preference. Local tie and
A+1 targets, source contributions, state weights and gains are separate fields.
That earlier bounded output does not provide the complete native statewide
clipping surface. The separate complete Senate-source calculation below uses
its own explicitly different native-source denominator.

The expanded [84-packet Senate ledger](data/baselines/native-2024-senate-reviewed-84views.json)
and [flat source-position file](data/baselines/native-2024-senate-reviewed-84views.csv)
cover all 82 counties plus original Pike/Coahoma alternatives: **1,779 native
constituents across alternative scopes, 84 TOTALs, 447 unused columns and 11
non-additive Kemper parallel observations**, or 4,642 numeric/null candidate
positions on 211 original pages. [Controls](data/baselines/native-2024-senate-reviewed-controls-84views.json)
retain every source scope separately. Preferred updated-where-explicit 82
packets contain **1,736 disjoint source-native constituents** summing Pinkins
451,980/Wicker 763,420. The [sos-2024-county-tunica](https://www.sos.ms.gov/elections/electionresults/2024General/County%20Results/Tunica.pdf) independently prints
1,798/827 in its ES&S summary PDF3, but 1,797/827 in its SEMS PDF7–8 native
rows and TOTAL. No native allocation of that one-vote difference is known.
The certified county denominator remains 1,215,401; this native-source universe
is separately **1,215,400**. Kemper PDF6 is explicitly UnOfficial, repeats the
first eleven source columns found on Official PDF7, and remains non-additive;
PDF8 adds three constituents and TOTAL. These are original page observations,
not an inferred release chronology. See [sos-2024-county-kemper](https://www.sos.ms.gov/elections/electionresults/2024General/County%20Results/Kemper.pdf) and
the [complete original exception readings](data/baselines/native-source-exception-readings.json).

The final replay agrees with the frozen peer checkpoint on all 4,642 candidate
positions and source-bound labels, preserving explicit wrap representations.
It keeps **58 Itawamba candidate-box metadata differences** from earlier
targeting aids separate from numeric agreement; six earlier expanded reading
boxes and the whole-row original review remain recorded. Source literal Lincoln
`Forrestry` and Walthall `4th Distrct West` are preserved as printed. No name,
ordinal or vote agreement establishes current 2026 geometry.

[Complete-source native targets](data/baselines/native-source-unit-targets.csv.gz)
contain **156,240 rows**, with [90 bounded state targets](data/baselines/native-source-state-targets.csv),
[7,380 county contributions](data/baselines/native-source-county-contributions.csv)
and [declared settings](data/baselines/native-source-calculator-settings.json).
Every scenario includes all 1,736 preferred native constituents in all 82
counties. Base volume is the actual 1,215,400 native-source named pair; low
uses 2022 county EAC F1a with illustrative pair participation=1; high uses
2020 county Senate pair volume; the two 2018 stages remain separate. Other
county mixes also have variants normalized to 1,215,400 to isolate composition.
Actual source2024 within-parent pair weights allocate those expressly
conditional county volume sensitivities. Only the 2024 Senate anchor uses
observed native preference; other anchors apply their historical county
preference uniformly within that source2024 parent. No cross-year native
identity, candidate effect or 2026 turnout is inferred. Shares clip to [0,1]
and the uniform shift is solved with the bounded native surface, retaining
unbounded shifts, clipped units and selected-unit-only impossible/already-winning
requirements separately. Every other native unit stays fixed for a selected
unit solve. The native and certified county universes remain separate.
At the actual native base, the bounded tie requires
**13.063828 share points**, with
**133 units clipped**; its unbounded formula gives
12.812243 points and is infeasible for
some native shares. A+1 requires **13.593568
bounded share points**, 137 clipped units and
12,154 native-source net votes. The bounded increment differs from the
unbounded 0.5-point increment because clipping changes the movable pool.
Use `native_state_calculator.py --unit SOURCE_POSITION_KEY --others-shift-pp 0
--target-pair-margin-pp 0` for a selected-source-unit solve with all others fixed.
[Offline validation](data/baselines/native-final-validation.json) checks source
hashes, positions, source balances and every target row. Historical native candidate arithmetic and the available printed vendor/method
scopes are documented separately; repeated source views are never additive.
The [pinned field-scope qualification](data/baselines/source/reviewed-source-scope.json)
lists source availability and external qualifications. Complete all-eleven-candidate original reviews
cover 1736 disjoint native constituents in
82 source views, with Kemper's eleven parallel
observations retained separately. The [field coverage ledger](data/baselines/native-allfield-coverage.json)
keeps all 82 parents visible, with
0 preferred native
units outside the completed nine-presidential original scope. The complete preferred
82-view witness retains 206 original pages, 82 separate TOTALs, 437 unused
columns and 11 Kemper parallels: 20,119 numeric and 4,807 null positions.
Tunica's Harris source sum 1,836 remains one below the ES&S/county control
1,837, alongside the distinct Pinkins one-vote difference. Neither is
allocated to a native unit. [Earlier Coahoma and Pike SEMS readings](data/baselines/native-alternative-allfield-readings.json)
retain all eleven vectors in two separate nonadditive alternatives, with
43 native constituents; they do not enlarge the preferred 1,736-unit pool.
The [complete candidate control comparison](data/baselines/native-2024-candidate-controls.json)
checks all 902 county/candidate vectors. The preferred presidential named
source denominator is 1,228,007, compared with the signed 1,228,008; only
Tunica Harris differs. All independent/Libertarian/Green/Constitution fields
remain named separately.
The [frozen post-transcription peer replay](data/baselines/native-presidential-peer-batches-reconciliation.json)
agrees at 19,872 presidential positions in
80 source views. The Alcorn/Coahoma all-eleven proof stays
separate, yielding bounded peer coverage of
82 preferred views
and 1,736
native units; 0 views /
0 native units remain outside it.
The [new immutable replay](data/baselines/source/presidential-peer-through-batch33-v4/reconciliation.json)
preserves all source fields and exact peer input bytes after own original reading.
Together with the separate two-view proof, 20,268 nine-presidential source positions
are checked, including all 1,736 native vectors, 82 TOTALs and 99 nonadditive Kemper
parallel positions. The older Perry/Tunica peer CSVs omit 126 unused template
positions (45 / 81) that are null in this package's own original readings;
those missing peer fields are preserved, without imputed peer nulls or a claim
of identical blank-position coverage. Eighteen Holmes candidate-label positions
retain two explicit A-hyphen-line-wrap representations, unequal under whitespace-only
folding. Numeric and role comparisons agree; the two literal representations remain
separate. Kemper's peer ledger has no header-box array, so exact header-box agreement
is not claimed. The [earlier 75-view replay](data/baselines/source/presidential-peer-through-batch26-v3/reconciliation.json)
retains its exact earlier bytes and narrower scope.
A separate [complete all-eleven-field reciprocal proof](data/baselines/native-2024-all11-complete-peer-reconciliation.json)
now checks **24,926 positions** against the peer's newly explicit immutable
all82 body: 19,096 native candidate values, 902 TOTALs, 4,807 unused nulls
and 121 nonadditive Kemper parallel values. Its 126 newly explicit peer blanks
close only that newer blank-position scope; the older witness above remains
unchanged. Twenty-two Holmes candidate-label positions retain the two literal
hyphen-wrap representations. No raster, crop-window or current-ID identity is
implied by value/role agreement.

The earlier [combined immutable
named-field witness](data/baselines/source/native-2024-named-v1/snapshot.json)
retains its original 52-view peer scope plus the separate two-view proof unchanged;
it does not silently adopt this expanded replay or imply all-field completion.
Winston's two complete original pages provide [143 numeric and 99 unused/null
candidate positions](data/baselines/winston-native-allfield-readings.json),
including all nine presidential vectors, each matching the printed TOTAL and
county control. The gray-scan OCR failures remain separate reading aids.

The [sos-2024-county-union](https://www.sos.ms.gov/elections/electionresults/2024General/County%20Results/Union.pdf) also contains a separate ES&S vendor
profile partition: all 20 profiles (PDF16,18,…54) and their **380 required
fields** have independent [original-image readings](data/baselines/union-native-profile-readings.json)
and a [flat field file](data/baselines/union-native-profile-fields.csv).
All 18 count-field sums close the independently read county summary/statistics,
including registration 17,084, ballots 12,533, blank 1, Senate 1,779/10,484
and generic marks 84. Printed turnout percentages are nonadditive.
Unprinted under/over fields remain unknown; residuals 186 Senate/37 president
are arithmetic residuals only. Profile and county clocks 4:58/4:52 PM stay
separate. [Reciprocal comparison](data/baselines/union-native-profile-peer-reconciliation.json)
agrees on all 380 source fields and exact text-layer targeting positions after
independent original-glyph review. This vendor partition is not deduplicated
with SEMS by matching names or counts.

The original [sos-2024-county-pike](https://www.sos.ms.gov/elections/electionresults/2024General/County%20Results/Pike.pdf) has 25 separate ES&S vendor
profiles across all 42 section pages (PDF15–56), with variable page lengths.
All **525 required fields** and 25 headers have independent
[original-image readings](data/baselines/pike-native-profile-readings.json)
and a [flat field file](data/baselines/pike-native-profile-fields.csv).
Nineteen available count vectors agree with the original county PDF12/13
panels: registration 24,692, ballots 12,824, named Senate 5,898/6,719 and
generic Senate marks 30. The profiles print blank ballots 1; the county panel
leaves blanks unprinted. Senate total votes cast 12,647 and contest totals
12,824 remain distinct, with no under/over allocation. All nine presidential
identities and generic marks remain separate, including the source's printed
`Peter Sonsk / Lauren Onak` truncation. Profile/county clocks 3:07/3:05 PM
do not establish release chronology. A [reciprocal check](data/baselines/pike-native-profile-peer-reconciliation.json)
agrees on all 525 fields, pages, printed codes and labels; independent reading
windows in different rasters remain separate. These original profiles are
not spliced into the updated Pike publication or joined to SEMS/current units.

[Alternative-unit targets](data/baselines/native-alternative-unit-targets.csv)
add 7,920 rows for original Pike/Coahoma SEMS views and the 20 Union/25 Pike
vendor profiles, with [360 source-mixture state targets](data/baselines/native-alternative-state-targets.csv).
Each alternative replaces its **entire county partition** while the other
81 counties stay in the state sum; no unit crosswalk is used. Base volume is
actual named pair in that expressly stated source mixture, including 1,212,682
for the original-Pike alternative. Low/base/high/mix and preference settings,
clipping and selected-only assumptions match [their saved settings](data/baselines/native-alternative-calculator-settings.json).
The 11 Kemper parallel observations have [22 local tie/A+1 targets](data/baselines/native-parallel-observation-local-targets.csv),
with no independent disjoint state-moving pool inferred for a repeated page.
These arithmetic scopes remain separate from certified county ranking and
current geography. [Supplemental validation](data/baselines/native-alternative-validation.json)
checks these fields and targets.

The [whole-packet printed-field inventory](data/baselines/printed-field-source-scope.json)
covers all **352 county originals / 3,238 pages**. All complete original
page layouts were inspected in [41 retained overview cards](data/baselines/source/original-page-scope-overviews.json),
with required irregular panels reread at full size. It preserves 15 county
summary panels, 14 statistics panels, 45 vendor profiles / 905 required numeric
fields, three additional SEMS E-013 named-vote presentations, and Union's
58 administrative split-ballot-style rows. This is the retained source scope;
it does not prove no county published a further document. Unprinted native
methods, generic marks, valid named write-ins, ballots, blanks and registration
status/date remain unavailable. All unrelated source offices and fields are
retained in complete original bytes without a second numerical derivative.
2020 ballot-measure under/over rows are not Senate methods; selected full
Alcorn/Hinds originals explicitly confirm that locator false positive.

The [three E-013 original readings](data/baselines/supplemental-2024-summary-readings.json)
are [sos-2024-county-bolivar](https://www.sos.ms.gov/elections/electionresults/2024General/County%20Results/Bolivar.pdf) PDF4, [sos-2024-county-grenada](https://www.sos.ms.gov/elections/electionresults/2024General/County%20Results/Grenada.pdf) PDF9
and [sos-2024-county-itawamba](https://www.sos.ms.gov/elections/electionresults/2024General/County%20Results/Itawamba.pdf) PDF12. Their 33 named candidate values
and six printed named totals match their own county controls; generic and
ballot/method fields are unprinted there, not inferred zero. These repeated
county presentations do not enlarge the preferred electorate.

Union PDF8–10's BP-009 **Precinct Split Ballot Styles Report** preserves
[all 58 split rows and 20 parent TOTALs](data/baselines/union-split-ballot-style-readings.json),
including explicit zero rows, blank Party cells and literal `NAS` split labels.
Its Grand Total **17,058 Total Voters** is 26 below the separate 17,084 vendor
registration count; their definitions/status do not establish a common universe.
No candidate values are printed by split. Their pair weights, tie/A+1 and
selected-only targets remain explicitly **unknown candidate allocation**,
not zero-pool or allocated registration votes. Their [flat source file](data/baselines/union-split-ballot-style-fields.csv)
retains source/page/parent/row keys; no SEMS/profile/current crosswalk is inferred.

All compressed outputs are lossless; original/stored byte hashes and exact
ordered CSV reconstruction are recorded in the settings and schema. Independent
peer replay is complete for preferred2024 named fields and bounded at41/104
2020 publications and41/164 2018 stage grids; no whole-historical independent
replay is claimed. Own complete-original named-source reading covers all of them.

Current method context also differs from the historical absentee groupings.
The [hb859-official-history](https://billstatus.ls.state.ms.us/2026/pdf/history/HB/HB0859.xml) records HB859 as Law, Chapter385,
approved March19 and effective July1,2026. Its CURRENT HTML is labeled As Sent
to Governor, while the linked [hb859-official-current-pdf](https://billstatus.ls.state.ms.us/documents/2026/pdf/HB/0800-0899/HB0859SG.pdf) p1 prints
As Passed the House; both labels are preserved. Section26/p49 requires a daily
aggregate in-person absentee ballot report at close of business, available on
request. This does not establish a public endpoint, Senate allocation or actual
release cadence. Section4/p8 postpones tallying until polls close, alongside
late-mail processing language. Later law/rule/court and actual November source
gates remain separate; no nightly completion or historical/current method join
is inferred. [Independent original readings](data/baselines/source/current-method-readings.json)
pin this bounded scope.

The current [sos-2026-current-absentee-info](https://www.sos.ms.gov/yall-vote/absentee-voting-information) FAQ9/10 prints a
November3 postmark deadline and November10 receipt deadline, described as
five business days. FAQ4 describes scanning in-person absentee paper ballots
and counting after polls close. The actual [court-2026-fifth-circuit-remand](https://www.ca5.uscourts.gov/opinions/unpub/24/24-60395.0.pdf)
(case24-60395, Document255-1, September9,2026) p2 affirms the district judgment
on Supreme Court remand in light of Watson. [Own complete-original readings](data/baselines/source/current-receipt-readings.json)
pin both court pages and the exact retained SOS clauses without duplicating
shared original bytes. Complete later mandate/district-docket and exception
review remains open. These printed instructions do not supply an outstanding
Senate vote count or a remaining pool for the calculator.

Current native extraction inventory: 3,238 of 3,238 original pages scanned; 352 of 352 source documents have complete page aids. All required named-source native grids and located required printed controls have original readings; machine aids remain diagnostic and are not accepted transcriptions. No missing values are filled with zero.

```sh
PYTHONDONTWRITEBYTECODE=1 python senate/2026/mississippi/data/baselines/reproduce.py
# Optional repeat of uncached independent raster OCR using retained originals:
PYTHONDONTWRITEBYTECODE=1 python senate/2026/mississippi/data/baselines/reproduce.py --ocr
```

The retained [full offline run](data/baselines/source/reproduction-1042020-70stage2018.json)
exited successfully through the 104-publication 2020 named-Senate scope and
70-stage 2018 native scope, including historical 2020 native targets and bounded
peer proofs. Its 26 completed checks and exact input/log hashes remain dated
evidence; later scope additions require their own checks.

The later [complete offline rebuild receipt](data/baselines/source/reproduction-1042020-118stage2018/completion.json)
pins an exit0 run through the same 104 actual 2020 publications and 118 reviewed
2018 stage grids, with 28 then-current bounded checks. Its execution script,
historical source builders, validation and manifest bytes are frozen losslessly;
the final log pin supersedes its pre-completion entry in that dated run manifest.
Later source additions are separate; this run leaves broader method/history gates open.

The [complete retained-original rebuild](data/baselines/source/reproduction-complete-original-v1/completion.json)
exited0 through all104 actual2020 publications, all164 distinct2018 stage
grids, all84 alternative2024 views, located required controls and the
county/native/live calculators, with **35 completed then-current checks**.
Its exact execution script, log, input witnesses and run outputs are pinned
losslessly. The later v2 proposal/field-companion integration has its own
independent checks and the final [validation](data/baselines/validation.json) /
[complete asset audit](data/baselines/asset-manifest.json); it does not rewrite
the earlier rebuild receipt or witnesses.

Original download commands are separate from offline rebuilds. Rerunning
acquisition later does not establish the old publication's release chronology.
The package supplies conditional arithmetic and source evidence, not an
implemented collector, calibrated Needle, known live cadence, 2026 turnout
forecast or approved current precinct boundary crosswalk.
