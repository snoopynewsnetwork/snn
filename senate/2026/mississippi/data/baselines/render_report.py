"""Render the question report from the exact saved settings/counts."""
import csv,json
from sources import *
def main():
    rows=list(csv.DictReader((BASE/'data/county-baselines.csv').open()));states=list(csv.DictReader((OUT/'state-targets.csv').open()));targets=list(csv.DictReader((OUT/'county-targets.csv').open()));counts=json.load((OUT/'county-contract.json').open());native=json.load((OUT/'native-coverage.json').open()) if (OUT/'native-coverage.json').exists() else {}
    source=references();link=lambda key:'['+key+']('+source[key]['url'].replace(' ','%20')+')'
    primary=json.load((OUT/'source/primary-state-readings.json').open());totals=counts['candidate_totals'];T=counts['state_total'];base=next(r for r in states if r['scenario']=='base-2024-Senate' and r['preference_anchor']=='2024-senate' and float(r['target_pair_margin_pp'])==0);cushion=next(r for r in states if r['scenario']=='base-2024-Senate' and r['preference_anchor']=='2024-senate' and float(r['target_pair_margin_pp'])==1)
    native_states=list(csv.DictReader((OUT/'native-source-state-targets.csv').open()));native_base=next(r for r in native_states if r['scenario']=='base-2024-native-Senate' and r['preference_anchor']=='2024-senate' and float(r['target_pair_margin_pp'])==0);native_cushion=next(r for r in native_states if r['scenario']=='base-2024-native-Senate' and r['preference_anchor']=='2024-senate' and float(r['target_pair_margin_pp'])==1)
    allfield=json.loads((OUT/'native-allfield-coverage.json').read_text())
    histnative=json.loads((OUT/'native-2020-coverage.json').read_text())
    native2018=json.loads((OUT/'native-2018-original-readings.json').read_text());native2018_validation=json.loads((OUT/'native-2018-validation.json').read_text());native2018counts=native2018['counts'];latest2018=native2018_validation['immutable_witnesses'][-1]['path'];pages2018=sum(len(s['pages']) for s in native2018['sources'])
    peerpres=json.loads((OUT/'native-presidential-peer-batches-reconciliation.json').read_text())
    text=f'''# Mississippi historical partisanship and conditional paths

Working research snapshot: October 19, 2026 UTC. This is the **regular Class II** race.
The priority baseline is the other, Class I seat's **2024 Wicker–Pinkins Senate
contest**, while **2020 Hyde-Smith–Espy** is the same Class II seat. Historical
pair preferences, volumes and candidate identities are not 2026 projections.

At the 2024 two-name Senate weights, Pinkins trails Wicker by **311,439 votes**.
A uniform **{100*float(base['unbounded_shift']):.6f} A-share points** ties the pair;
**{100*float(cushion['unbounded_shift']):.6f} share points** gives an illustrative
**A+1 pair margin**, or **12,154.01 net votes**. All 82 counties remain in every
state calculation. This is a deterministic named-pair benchmark; it does not
transfer Pinkins's 2024 Democratic identity to his 2026 Independent candidacy.
The counts reconcile to the {link('sos-2024-certified-sen-pdf')} (PDF p3).

**Current ordinary outcome and candidates.** The SOS's September 10, 2026
[clarification]({source['sos-2026-vote-rule-clarification']['final_url']}) and its
{link('sos-2026-majority-chart')} explicitly classify ordinary U.S. Senate as
**plurality**, separately from majority rules for statewide state offices and
judicial/county offices. The November 3 {link('sos-2026-sample-ballot')} (p1)
prints **Scott Colom—Democrat, Cindy Hyde-Smith—Republican, Ty Pinkins—Independent,
and Write-in**. It is headed SAMPLE; signed final certification, withdrawals,
valid write-in identities and result-system IDs remain unverified here. The
qualifying list is corroboration, not a substitute final ballot certificate.
A must strictly exceed every named rival to have a unique plurality; beating
Hyde-Smith while trailing Pinkins is not a win. No opposition union is assumed.

**Actual contests and source presentation.** There was no 2022 U.S. Senate or
governor election in Mississippi. The {link('sos-2022-certified-index')} lists
congressional/judicial/district contests; state Senate district headings are not
a statewide U.S. Senate baseline. The actual recent same-seat midterm contests
are **November 6, 2018 special** and **November 27, 2018 runoff**, kept separate.
The {link('fec-2018-special-rule')} specifies majority/top-two special-runoff
rules for that election. The {link('sos-2018-runoff-certified-sen-pdf')} has both
stages on its complete second page. Its December 3 signed runoff certificate
and December 13 summary clocks are separate observations, not an inferred
release chronology. The {link('house-clerk-2018-statistics')} (PDF p28, printed
p26) supplies political party identities, but its footnotes substitute runoff
totals for Espy/Hyde-Smith alongside first-stage Bartee/McDaniel figures. Do not
sum that presentation as one electorate. County special ballot party cells
remain blank where blank in the original.

| Historical contest/stage | A | B | Other named candidates, separately | Named votes | A pair share % | A−B pair margin pp | A−B all-named margin pp |
|---|---:|---:|---|---:|---:|---:|---:|
'''
    specs=[('2024 Senate, other seat','2024-senate','Ty Pinkins','Roger F. Wicker'),('2024 president, separate','2024-president',next(k for k in totals['2024-president'] if 'Kamala' in k),next(k for k in totals['2024-president'] if 'Donald' in k)),('2020 Senate, same seat','2020-senate','Mike Espy','Cindy Hyde-Smith'),('2018 special, November 6','2018-special','Mike Espy','Cindy Hyde-Smith'),('2018 runoff, November 27','2018-runoff','Mike Espy','Cindy Hyde-Smith')]
    for title,key,an,bn in specs:
        d=totals[key] if key in totals else primary[key]['candidates'];a=d[an];b=d[bn];o={n:v for n,v in d.items() if n not in [an,bn]};n=sum(d.values());others='; '.join(f'{k.replace("Presidential Electors for ","").split(" for President")[0]} {v:,}' for k,v in o.items()) or 'none published in this named scope'
        text+=f'| {title} | {a:,} | {b:,} | {others} | {n:,} | {100*a/(a+b):.4f} | {100*(a-b)/(a+b):+.4f} | {100*(a-b)/n:+.4f} |\n'
    text+=f'''
Complete individual candidate/party literals and source rows are in
[candidate-votes.csv](data/baselines/candidate-votes.csv); independent primary
readings, dates and clocks are in [the state ledger](data/baselines/source/primary-state-readings.json).
The 2020 CSV matches all three candidates in the {link('sos-2020-amended-sen-pdf')}:
578,691 / 709,511 / 23,152. The {link('sos-2020-certified-sen-pdf')} instead prints
578,806 / 709,539 / 23,152, 143 more in total; both vintages survive. No county
residual is allocated from that difference.

The independent [2020 county-publication audit](data/baselines/county-2020-publication-controls.json)
now reads all **104 actual county packets: 82 original publications and 22
explicit Amended alternatives**, preserving all 312 printed Senate TOTAL fields.
Using each explicitly amended publication where available, otherwise its
original, reproduces every county CSV value and the amended statewide vector.
Three county publication pairs change: {link('sos-2020-county-adams')} p4 versus
{link('sos-2020-county-adams-amended')} p3 changes Espy 7,736→8,190 (+454);
{link('sos-2020-county-coahoma')} versus {link('sos-2020-county-coahoma-amended')}
p3 changes 6,452/2,161/46→6,337/2,133/46 (−115/−28/0); and
{link('sos-2020-county-prentiss')} versus {link('sos-2020-county-prentiss-amended')}
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
readings cover {histnative['counts']['reviewed_source_publications']} publication
views and {histnative['counts']['native_constituents']} constituents across those
separate vintages; only {histnative['counts']['reviewed_selected82_publications']}
selected county views / {histnative['counts']['selected82_reviewed_native_constituents']}
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

The complete {link('sos-2018-county-leflore')}
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

The [latest accepted source witness]({latest2018}) now contains
**{native2018counts['source_views']} of 164 stage grids / {native2018counts['native_constituents_across_separate_stages']:,}
native observations across separate electorates**, {native2018counts['TOTAL_columns']} TOTALs,
{native2018counts['unused_columns']} unused columns and {native2018counts.get('administrative_columns',0)} administrative columns on
{pages2018} complete original pages. It preserves {native2018counts['numeric_positions']:,}
numeric, {native2018counts['unused_null_positions']:,} unused/null and {native2018counts['marked_native_positions']} literal `X` positions.
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
Independently rendered {link('sos-2024-county-pike-updated')} p4 gives Pike
7,130 / 8,205 versus the CSV's 5,898 / 6,719. Those explicit candidate changes
of +1,232 / +1,486 explain all 2,718 Senate votes. Its nine presidential values
explain all 2,770 presidential votes and reproduce every signed candidate in
the {link('sos-2024-certified-pres-pdf')}. No scaling or imputed allocation is
used. Coahoma's original and updated Senate totals agree with the CSV; no
cause of its update or certification/release sequence is inferred.

The certified Senate denominator is **1,215,401 two-name votes**, not all marks
or ballots. For example {link('sos-2024-county-lauderdale')} p3 separately prints
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
The crossing unit is {link('sos-2024-county-lauderdale')} PDF9 physical column5,
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

**Separate 2018 native arithmetic.** The complete {link('sos-2018-general-index')}
and {link('sos-2018-runoff-index')} originals supply 1,771 November6
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
'''
    targetmap={(r['fips'],float(r['target_pair_margin_pp'])):r for r in targets if r['scenario']=='base-2024-Senate' and r['preference_anchor']=='2024-senate'}
    for r in rows:
        a=int(r['2024-senate_A']);b=int(r['2024-senate_B']);t=a+b;q=targetmap[(r['fips'],0)];c=targetmap[(r['fips'],1)]
        text+=f'| {r["rank"]} | {r["county"]} | {a:,} / {b:,} | {float(r["2024-senate_pair_margin_pp"]):+.2f} | {float(r["2024-president_pair_margin_pp"]):+.2f} | {float(r["2020-senate_pair_margin_pp"]):+.2f} | {float(r["2018-special_pair_margin_pp"]):+.2f} | {float(r["2018-runoff_pair_margin_pp"]):+.2f} | {100*t/T:.3f} | {100*float(q["target_A_share"]):.3f} | {100*float(c["target_A_share"]):.3f} | {.02*t:,.2f} |\n'
    text+='''
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
'''
    for r in states:
        if float(r['target_pair_margin_pp'])!=0:continue
        c=next(x for x in states if x['scenario']==r['scenario'] and x['preference_anchor']==r['preference_anchor'] and float(x['target_pair_margin_pp'])==1)
        text+=f'| {r["scenario"]} | {r["preference_anchor"]} | {float(r["pair_votes"]):,.2f} | {float(r["baseline_net"]):+,.2f} | {100*float(r["bounded_shift"]):+.6f} | {100*float(c["bounded_shift"]):+.6f} |\n'
    text+=f'''
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
The {link('sos-2024-county-lincoln')} PDF9 independently prints **15,898 ballots**, equal to its two
contest totals, with registration 0 unusable; Senate residual 172 and
presidential residual 69 remain unclassified. See the [original reading](data/baselines/source/2024-lincoln-independent-controls.json).
The {link('sos-2024-county-montgomery')} PDF3 independently prints **885 ballots, 6,291 registered and
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
451,980/Wicker 763,420. The {link('sos-2024-county-tunica')} independently prints
1,798/827 in its ES&S summary PDF3, but 1,797/827 in its SEMS PDF7–8 native
rows and TOTAL. No native allocation of that one-vote difference is known.
The certified county denominator remains 1,215,401; this native-source universe
is separately **1,215,400**. Kemper PDF6 is explicitly UnOfficial, repeats the
first eleven source columns found on Official PDF7, and remains non-additive;
PDF8 adds three constituents and TOTAL. These are original page observations,
not an inferred release chronology. See {link('sos-2024-county-kemper')} and
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
**{100*float(native_base['bounded_shift']):.6f} share points**, with
**{native_base['clipped_units']} units clipped**; its unbounded formula gives
{100*float(native_base['unbounded_shift']):.6f} points and is infeasible for
some native shares. A+1 requires **{100*float(native_cushion['bounded_shift']):.6f}
bounded share points**, {native_cushion['clipped_units']} clipped units and
12,154 native-source net votes. The bounded increment differs from the
unbounded 0.5-point increment because clipping changes the movable pool.
Use `native_state_calculator.py --unit SOURCE_POSITION_KEY --others-shift-pp 0
--target-pair-margin-pp 0` for a selected-source-unit solve with all others fixed.
[Offline validation](data/baselines/native-final-validation.json) checks source
hashes, positions, source balances and every target row. Historical native candidate arithmetic and the available printed vendor/method
scopes are documented separately; repeated source views are never additive.
The [pinned field-scope qualification](data/baselines/source/reviewed-source-scope.json)
lists source availability and external qualifications. Complete all-eleven-candidate original reviews
cover {allfield['counts']['native_constituents']} disjoint native constituents in
{allfield['counts']['source_views']} source views, with Kemper's eleven parallel
observations retained separately. The [field coverage ledger](data/baselines/native-allfield-coverage.json)
keeps all 82 parents visible, with
{allfield['counts']['preferred_unreviewed_native_constituents']} preferred native
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
agrees at {peerpres['compared_positions']:,} presidential positions in
{peerpres['source_views']} source views. The Alcorn/Coahoma all-eleven proof stays
separate, yielding bounded peer coverage of
{peerpres['bounded_preferred_source_views_including_separate_two']} preferred views
and {peerpres['bounded_preferred_native_constituents_including_separate_two']:,}
native units; {peerpres['remaining_preferred_source_views']} views /
{peerpres['remaining_preferred_native_constituents']} native units remain outside it.
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

The {link('sos-2024-county-union')} also contains a separate ES&S vendor
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

The original {link('sos-2024-county-pike')} has 25 separate ES&S vendor
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
are {link('sos-2024-county-bolivar')} PDF4, {link('sos-2024-county-grenada')} PDF9
and {link('sos-2024-county-itawamba')} PDF12. Their 33 named candidate values
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
'''
    text+=f'''
Current method context also differs from the historical absentee groupings.
The {link('hb859-official-history')} records HB859 as Law, Chapter385,
approved March19 and effective July1,2026. Its CURRENT HTML is labeled As Sent
to Governor, while the linked {link('hb859-official-current-pdf')} p1 prints
As Passed the House; both labels are preserved. Section26/p49 requires a daily
aggregate in-person absentee ballot report at close of business, available on
request. This does not establish a public endpoint, Senate allocation or actual
release cadence. Section4/p8 postpones tallying until polls close, alongside
late-mail processing language. Later law/rule/court and actual November source
gates remain separate; no nightly completion or historical/current method join
is inferred. [Independent original readings](data/baselines/source/current-method-readings.json)
pin this bounded scope.

The current {link('sos-2026-current-absentee-info')} FAQ9/10 prints a
November3 postmark deadline and November10 receipt deadline, described as
five business days. FAQ4 describes scanning in-person absentee paper ballots
and counting after polls close. The actual {link('court-2026-fifth-circuit-remand')}
(case24-60395, Document255-1, September9,2026) p2 affirms the district judgment
on Supreme Court remand in light of Watson. [Own complete-original readings](data/baselines/source/current-receipt-readings.json)
pin both court pages and the exact retained SOS clauses without duplicating
shared original bytes. Complete later mandate/district-docket and exception
review remains open. These printed instructions do not supply an outstanding
Senate vote count or a remaining pool for the calculator.
'''
    text+=f'\nCurrent native extraction inventory: {native.get("extracted_pages",0):,} of {native.get("expected_pages",0):,} original pages scanned; {native.get("complete_page_sources",0)} of {native.get("source_documents",0)} source documents have complete page aids. All required named-source native grids and located required printed controls have original readings; machine aids remain diagnostic and are not accepted transcriptions. No missing values are filled with zero.\n'
    text+='''
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
'''
    (BASE/'county-partisanship.md').write_text(text)
if __name__=='__main__':main()
