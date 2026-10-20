#!/usr/bin/env python3
"""Render the owned historical partisanship report from saved numerical results."""
import csv,json
from pathlib import Path
D=Path(__file__).resolve().parent;STATE=D.parents[1]
def load(p):return json.loads(p.read_text())
def rows(p):return list(csv.DictReader(p.open()))
def main():
    E=load(D/'original-extract.json');B=rows(D.parent/'county-baselines.csv');ST=rows(D/'state-baselines.csv');SC=load(D/'state-scenarios.json');CT=rows(D/'county-target-scenarios.csv');PR=load(D/'priority-contract.json')['2024-senate'];REF={r['id']:r for r in load(D/'source/original-references.json')};COV=load(D/'coverage-controls.json');M=load(D/'state-candidate-methods.json')
    primary=next(r for r in ST if r['contest']=='2024-senate');s=[]
    s.append(f'''# New Mexico historical partisanship and conditional paths

Research completed from original public source captures on **2026-10-20 UTC**. These are historical arithmetic scenarios, not 2026 turnout projections, calibrated probabilities, a collector, or a current precinct crosswalk.

The 2024 Senate comparison already favors Martin Heinrich over Nella Louise Domenici by **91,355 votes**, or **10.113350 pair-margin points**. At its fixed county pair weights, a uniform **−5.056675 percentage-point shift in Heinrich's pair share** ties; **−4.556675 share points** gives the illustrative **A+1 pair margin**. No positive improvement is required to repeat that historical outcome. A means the explicitly named Democratic candidate in each historical contest; B means its named Republican opponent. “Other” never means Democratic. The actual [2024 Senate publication]({REF['elstats-2024-senate']['url']}) supplies the source labels; its county values were independently verified against all original county candidate columns in the [state canvass]({REF['official-2024-file-2']['url']}).

## Elections and current-source scope

The priority basis is **2024-11-05 Senate, Class I**, Heinrich–Domenici, the other seat. **2020-11-03 Senate, Class II**, Ben R. Lujan–Mark V. Ronchetti–Bob Walsh, is the same seat as the 2026 regular election. The actual midterm is **2022-11-08 governor**, not an invented 2022 Senate election. **2024 president** is a separate electorate/contest comparison. Historical event dates, contest/office IDs, candidates, parties, winner flags, source verification timestamps and every embedded metadata field are retained in [original page objects](data/baselines/source/independent-first-pin.json). The [Class II roster]({REF['senate-class-ii']['url']}) and [Class I roster]({REF['senate-class-i']['url']}) establish seat context.

The [2026 SOS index](https://www.sos.nm.gov/voting-and-elections/election-results/2026-election-results/) gives November 3 as the general date, while retaining generic November 2021 prose. Its actual linked [2911 results](https://electionresults.sos.nm.gov/default.aspx?eid=2911) identify the June 2 primary, updated June 23, 2026, 2:26 PM **MT**. Municipal and Rio Rancho runoff links have separate contexts. None identifies a November Senate result contest. Fresh October 20 requests, redirects, headers and full bodies are in [fresh receipts](data/baselines/source/fresh-observations.json).

The SOS-home-linked [**general** candidate portal](https://candidateportal.servis.sos.state.nm.us/CandidateList.aspx?eid=2917&cty=99) independently supplies all four Senate status records below. All 24 visible/hidden cell fields, original row attributes/positions and filing clocks are retained in [status records](data/baselines/current-senate-status-records.json); a fresh original read agrees on every cell. Filing clock timezone is unstated. Qualified status is not a signed final ballot or a current result-ID mapping. A bounded attempt to retrieve Otero's indexed general election notice returned **404 with an empty body**; no final ballot printing/write-in mapping is asserted. Primary write-in labels and old candidate IDs are not carried forward.

| General portal name | Party literal | Status | Filing clock literal |
|---|---|---|---|''')
    for r in load(D/'current-senate-status-records.json')['rows']:
        c=[c['text']for c in r['cells']];s.append(f'| {c[4]} | {c[8]} | {c[21]} | {c[19]} |')
    s.append('''
The Senate calculation treats an outright win as A exceeding every opponent's final vote count. A pair tie or pair cushion is an arithmetic benchmark, not the legal outcome rule. The official [2025 Election Handbook](https://www.donaanacountyelections.com/wp-content/uploads/2025/08/2025-NM_Election_Handbook_SOS-1.pdf), §§1-15-12–13, §1-14-18 and §1-13-11, covers the general election, state-officer canvass, plurality and tie-by-lot provisions. Its municipal runoff provisions (§1-22-16) remain separate; this package infers no Senate RCV transfers or lower preferences.

## State outcomes and complete candidates

These are named candidate votes, not ballots, registration or eligible population. “All candidate” means the complete published named field for that contest, not proof of an unreported generic/valid-write-in, undervote, blank or overvote universe. Those missing controls remain null. The 2024 Senate field has two candidates; its displayed other=0 describes that field only.

| Contest | A votes | B votes | Other named votes | All named votes | A+B | A pair share % | A−B pair margin pp | A−B all-candidate margin pp |
|---|---:|---:|---:|---:|---:|---:|---:|---:|''')
    for r in ST:s.append('| '+r['contest']+' | '+' | '.join(f'{int(r[k]):,}'for k in ['A','B','other','all_candidate_votes','pair_votes'])+f" | {100*float(r['A_pair_share']):.6f} | {float(r['pair_margin_pp']):+.6f} | {float(r['all_candidate_margin_pp']):+.6f} |")
    s.append('\nAll 33 county candidate vectors sum exactly to every statewide candidate control, independently checked against the original PDF county columns: **495 county candidate cells**, across 15 named candidacies/tickets. [PDF checks](data/baselines/pdf-county-controls.json) retain source page, text line, entire source line and column order. Source spellings/punctuation differ; labels are kept separately rather than silently harmonized. For example, narrative Luján and Doña Ana retain their accents here, while a source that prints `Lujan` or `Dona Ana` remains literal in its data. The Census `Doña Ana`→results `Dona Ana` county-only FIPS alias is explicit in the schema, never a precinct crosswalk.\n')
    for k,v in E.items():
        s.append(f"**{k}:** [official database]({REF[v['page_source_id']]['url']}), [original statewide candidate/method publication]({REF[M[k]['source_id']]['url']}).")
        s.append('')
        for j,c in enumerate(v['rows'][0]['cells'][2:-2],2):s.append(f"- {v['headers'][j]} — {v['parties'][j]}: **{c['value']:,}**.")
        s.append('')
    s.append('''
Independent, Libertarian, Green, Party for Socialism and Liberation and Liberal Party USA tickets stay named; none is reassigned to A. These four required contests each have a Democrat, so no fabricated Democratic or non-R coalition is needed. Counterfactual preference anchors do not establish candidate effects in 2026.

## All counties and fixed-weight targets

The table covers every county, ordered by 2024 Senate candidate volume. Margins are A−B **pair margin points** in the indicated contest. Weight is county A+B / state A+B for 2024 Senate. Tie/A+1 columns are illustrative county A pair shares under the common statewide shift; no county target is independently necessary. Every other county remains in statewide sums. [All 132 contest/county baseline rows](data/county-baselines.csv) include counts, denominators, source positions, historical winner and closeness bands (absolute pair margin ≤5, >5–10, >10 points). [All 1,056 county scenario rows](data/baselines/county-target-scenarios.csv) add contributions, gains and selected-only requirements.

| County source label | Senate net A−B | Senate margin pp | Same-seat 2020 margin pp | President 2024 margin pp | Governor 2022 margin pp | Senate weight % | Tie A share % | A+1 A share % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|''')
    for p in PR['county_sensitivity']['ordered']:
        c=p['county'];rs={r['contest']:r for r in B if r['county']==c};r=rs['2024-senate'];targets=[next(t for t in CT if t['county']==c and t['preference_anchor']=='2024-senate' and t['historical_volume_mix']=='base-2024-senate' and float(t['target_pair_margin_pp'])==g)for g in [0,1]]
        s.append(f"| {c} | {int(r['net_A_minus_B']):+,} | {float(r['pair_margin_pp']):+.3f} | {float(rs['2020-senate']['pair_margin_pp']):+.3f} | {float(rs['2024-president']['pair_margin_pp']):+.3f} | {float(rs['2022-governor']['pair_margin_pp']):+.3f} | {100*float(r['pair_weight_state']):.3f} | {100*float(targets[0]['target_A_pair_share']):.3f} | {100*float(targets[1]['target_A_pair_share']):.3f} |")
    s.append('''
At fixed positive county pair volume T_c, +1 A-share point changes net A−B by **0.02×T_c**: Bernalillo gains 6,094.76 net votes; these gains are saved for every county/native row where its pair volume is known. Share points, twice-as-large pair margin points, net votes and all-candidate margin points remain separate columns.

For pair volumes T_c and A shares s_c, `M=ΣT_c(2s_c−1)` and `T=ΣT_c`. The unbounded tie shift is `(B−A)/(2(A+B)) = −M/(2T)`. A+1 pair margin adds **0.5 share points**, with net target `0.01T`, not one vote. A one-point all-candidate margin would instead require `0.01V` net, where V includes held other candidates; the scenario files display the resulting all-candidate margin separately. With other candidates fixed, pair A/B target totals are `(T±target_net)/2`; all named candidate totals still sum to V and the full plurality leaders are checked.

Unbounded shifts are retained. Implementation clips `s_c+δ` to [0,1], then solves the common bounded δ by bisection; it does not clip and assume the original target still holds. Already-winning, impossible, unknown, invalid negative and no-positive-pool cases remain explicit. The primary county scenarios do not require clipping; native observed-universe and saved synthetic cases test it.

For a selected county only, with **all others fixed at their historical anchor shares (0 share-point adjustment)**, the requirement is `q_c=(T_c+gT−M_others)/(2T_c)`. Negative unbounded q is already secured even at q=0 under those assumptions; q>1 is impossible. Equality is a tie boundary. Unknown and zero pools are never divided through. The CLI allows a stated alternative shift in all other counties; its output records that assumption.

## Historical volume/mix and preference sensitivities

Low/base/high refer to **observed historical statewide contest volumes**, not a forecast range. Each county's volume V_c is the actual all-named-candidate total in 2022 governor (low), 2024 Senate (base), or 2024 president (high). The actual 2020 same-seat Senate mix is an additional context. Preference and participation anchors are independently selectable from all four contests: `p_c=(A_c+B_c)/all_candidates_c`, `T_c=V_c×p_c`, `s_c=A_c/(A_c+B_c)`. Every named other candidate retains its anchor county share of V_c. Thus changing volume/mix never silently assumes all governor/presidential voters participate in the Senate pair. Fractional scenario votes are expectations; historical counts remain integers. The [settings](data/baselines/settings.json) declare exactly these choices.

The following cases hold **2024 Heinrich–Domenici preferences/participation** fixed, so p_c=1. They isolate actual historical volume and county composition; no arbitrary ±10% turnout range is substituted. Uniformly scaling all county volumes alone would change net-vote magnitude, not tie share thresholds.

| Historical volume/mix | All-candidate volume | Pair volume | Fixed-share net A−B | Fixed-share margin pp | Tie A-share shift pp | A+1 A-share shift pp |
|---|---:|---:|---:|---:|---:|---:|''')
    for r in SC:
        if r['preference_anchor']!='2024-senate' or r['target_margin_pp']!=0:continue
        s.append(f"| {r['historical_volume_mix']} | {r['all_candidate_volume']:,.0f} | {r['volume']:,.2f} | {r['baseline_net']:+,.2f} | {r['baseline_margin_pp']:+.6f} | {r['shift_pp']:+.6f} | {r['shift_pp']+.5:+.6f} |")
    s.append('''
All **32 state target cases** (4 volume mixes × 4 preference anchors × 2 targets) and 1,056 county rows are retained in [state scenarios](data/baselines/state-scenarios.json). Candidate effects, changes in party coalitions, lower preferences, 2026 participation, vote-method mix and remaining-vote behavior are not inferred from these anchors.

## Complete native source coverage and qualified priority

Every source row is retained, including each administrative privacy aggregate and literal asterisk. Native IDs unavailable in the CSV stay null; the identity is contest/source + county literal + precinct literal + source position. Source precinct labels may describe physical or administrative contexts; central/method identity and polygons cannot be assumed. No name/count join establishes cross-year or November 2026 equivalence. Complete candidate/control/source cells are in [50,179 field rows](data/baselines/candidate-fields.csv); [8,558 native baseline rows](data/baselines/native-baselines.csv) and [17,116 native target rows](data/baselines/native-targets.csv) keep unknown cases present.

| Contest | Native source rows | Voter Privacy administrative rows | Masked candidate cells | All masked numeric cells |
|---|---:|---:|---:|---:|''')
    for k,v in COV.items():s.append(f"| {k} | {v['native_rows']:,} | {v['administrative_rows']} | {v['candidate_masks']:,} | {v['all_numeric_masks']:,} |")
    s.append('''
The 2024 Senate export has **2,181 rows with both candidate cells numeric**, totaling **902,421**. Within that explicitly observed universe, top 15 supply **14,647/902,421 = 1.623078%**; the smallest source-position-tied descending prefix reaching 80% is **1,392 rows**, **722,113/902,421 = 80.019525%**, versus 721,760 at 1,391. These include numeric privacy aggregates and do not prove a certified physical/native priority. The remaining 20 source rows have protected candidate cells. **Certified native full order, top 15 and minimum80 are null; canonical dispatch keys are empty.** No county substitution is authorized.

Complete certified county sensitivity, kept separate, has 10 counties reaching **725,900/903,311 = 80.359920%**, versus 704,286 at nine; the top 15 supply 806,821/903,311 = 89.318186%. Every county and every source-native row remains in the inventory. [Priority contract](data/baselines/priority-contract.json) preserves the initial literal-label tie convention; [source-scoped orders](data/baselines/source-scoped-orders.json) separately use source-position ties for exact peer comparison. Both are descending and retain all remainders. Tied order positions differed in 178 places; values, membership and integer crossing totals did not change.

Native uniform tie/A+1 targets are solved only within each contest's **directly known positive A+B universe**. Its denominator/unknown and zero row counts are in [native state scenarios](data/baselines/native-state-scenarios.json). They are not whole-state estimates. Whole-state all-native uniform target shares remain null because protected preferences/volumes cannot establish the clipped solution. A selected known native unit can separately be tested against the published whole-state historical net with every other context collectively fixed, subtracting only that directly printed row; unknown selected-unit values stay null. No privacy pool or county residual is assigned to precincts. Cross-year native low/high mixes remain unmodeled because no verified native crosswalk exists.

Source pitfalls are material: Chaves precinct 47 has both Senate candidate cells `*` while printed total votes/ballots are 0; Curry Voter Privacy has both candidates and total votes `*`, but printed total ballots 2. Neither is an inferred candidate zero. Printed total fields can omit protected candidates, so a printed zero is not proof of no contest votes. Known-lane county residuals remain unallocated in [coverage controls](data/baselines/coverage-controls.json). Otero literal 18 exists in the 2024 presidential export (Harris 91, Trump 273), but is absent from Senate; missing Senate scope is not zero. The 2020 legacy headline 1,925 differs from the database's 1,926 nonprivacy contexts. No invented row repair or ID join is made.

## Ballots, registration, methods and source disagreements

The original [2020 turnout page](https://electionresults.sos.nm.gov/VoterTurnoutDetails.aspx?eid=2782), [2022 page](https://electionresults.sos.nm.gov/VoterTurnoutDetails.aspx?eid=2838) and [2024 page](https://electionresults.sos.nm.gov/VoterTurnoutDetails.aspx?eid=2882) and their linked county service report **928,230 / 714,754 / 928,290 Ballots Cast**, with **1,351,811 / 1,364,559 / 1,343,825 Eligible Voters** respectively. Complete HTML native counts are 1,925 / 2,163 / 2,169; all ballot/eligible fields and original county IDs are retained in [turnout controls](data/baselines/turnout-controls.json). These are separate source universes from the ElectionStats candidate rows, not automatically joinable or voting-eligible-population measures. The source's signed 2022 PCT 051 Eligible Voters value −3 is preserved and flagged, never repaired to zero.

Portal clocks are **11/24/2020 1:47 PM MT**, **11/29/2022 4:39 PM MT**, and **5/30/2025 10:44 AM MT**. Retrieval clocks are UTC. PDF run clocks and filing clocks have no stated timezone; none is silently converted. The database verifiedAt values retain their source `Z` suffix. [Clock objects](data/baselines/source-clocks.json) retain literals. No live cadence is established by these snapshots.

The PDF administrative method headers sum to **928,172** in 2020, **58 below** the portal ballot count, across seven county discrepancies (Cibola −2, Dona Ana −6, Grant −4, Hidalgo +2, Luna +1, Sandoval −48, Valencia −1). The two later PDF ballot headers match portal totals. The discrepancy is retained by source/vintage, not rescaled. Separate candidate methods below reconcile exactly to candidate totals; county/native candidate methods remain unavailable in these statewide summary sources. Administrative ballot methods are not candidate methods.

| Contest / candidate source label | Early | Absentee | Election Day | Candidate total |
|---|---:|---:|---:|---:|''')
    for k,v in E.items():
        for j,cell in enumerate(v['rows'][0]['cells'][2:-2],2):
            vec=next(r['values']for r in M[k]['rows']if r['values'][-1]==cell['value']);s.append(f"| {k} / {v['headers'][j]} | "+' | '.join(f'{n:,}'for n in vec)+' |')
    s.append(f'''
These method vectors come directly from the linked original statewide candidate summaries above; [raw sections and rows](data/baselines/state-candidate-methods.json) retain each line. The legacy 2020/2022 CSVs independently agree and retain their native candidate/Race IDs, blank AreaNum and trailing cells. Blank AreaNum is statewide scope, not 33 missing county rows. The actual legacy 2024 election 2882 federal CSV is HTTP200 **header-only/unavailable**, not zero; ElectionStats CSV and original canvass restore the historical field. Document799's own embedded original remains403; the independently recovered SOS archive→RealFile table→public SDK GetWidgetFiles→literal PublicFiles canvass is a separate original, not claimed identical to799.

The original registration publications, [October31 statewide]({REF['registration-9-state']['url']}), [October31 county/precinct]({REF['registration-9-county']['url']}), [November26 statewide]({REF['registration-10-state']['url']}) and [November26 county/precinct]({REF['registration-10-county']['url']}), retain party stocks and literal source identities. State-table totals are **1,377,085** and **1,406,281**. The county-table total sums are **1,377,093** and **1,406,283**; native row totals sum **1,376,892** and **1,406,271**. These source disagreements remain explicit, including wrapped Hidalgo labels and blank party cells. Each vintage retains 2,168 native rows plus33county summaries and a separate grand total, without crosswalking these to election precincts. Active/inactive status is unstated in these tables; Eligible Voters and dated registration stocks have different dates/scopes and are never substituted for one another. [Registration controls](data/baselines/registration-controls.json), [native objects](data/baselines/registration-native-controls.json) and [all source disagreements](data/baselines/source-disagreements.json) preserve the details.

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
''')
    (STATE/'county-partisanship.md').write_text('\n'.join(s)+'\n')
if __name__=='__main__':main()
