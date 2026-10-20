"""Render report from independently extracted tables and executed scenario artifacts."""
import csv,json,re
from county import R,SPECS,COUNTIES

def main():
 c=list(csv.DictReader((R.parent/'county-baselines.csv').open()));idx={(r['contest'],r['county']):r for r in c};long=list(csv.DictReader((R/'county-candidates.csv').open()));sc=json.loads((R/'historical-scenarios.json').read_text());controls=json.loads((R/'state-controls.json').read_text());peer=json.loads((R/'peer-reconciliation.json').read_text());recon=json.loads((R/'native-reconciliation.json').read_text());native=json.loads((R/'native-units.json').read_text())
 text='''**Oregon historical partisanship and conditional paths — research snapshot 2026-10-20**

The complete **36-county** controls support historical conditional arithmetic. They do not establish a2026 forecast. Harris's2024 presidential pair led Trump by321,120 votes; repeating those county pair weights gives a tie after a **−7.433058 A-share-point** shift, or an illustrative A+1 pair margin after **−6.933058 points**. Negative shifts mean the historical baseline already wins that pair comparison. They are alternative statewide combinations, not required improvements in every county. The complete [official2024 abstract, archived December12](https://web.archive.org/web/20241212212240id_/https://sos.oregon.gov/elections/Documents/results/november-general-2024-results.pdf), page1, supplies all eight columns. [County baselines](data/county-baselines.csv) retain every parent and denominator.

The native geography is **partial**: five recovered2024 county publications close510 literal presidential rows, while31 parents lack a closed native universe. Canonical statewide native order/top15/minimum80 and approved dispatch remain **unavailable/null**. County sensitivities never substitute for native dispatch. All current-source, current-geography and acceptance flags remainfalse pending coordinator review. No old contest/result ID or geometry follows from an archived label.

Oregon's2026 regular election is ClassII.2020 Merkley is the same Senate seat;2022 Wyden is the other ClassIII seat and a midterm. Oregon held no2024 Senate contest.2024 president is the priority basis;2022 governor is a distinct substantial three-candidate sensitivity. These are separate electorates/contests, with no inferred candidate effect, lower preference, cross-year native join or2026 boundary equivalence. The [2020 candidate abstract](https://records.sos.state.or.us/ORSOSCMSearch/Search/DocumentStream.ashx?uri=13735450), page2, and [2022 candidate abstract](https://records.sos.state.or.us/ORSOSWebDrawer/Record/13735454/File/document), pages1/4, are independently extracted from retained complete originals. The latter reconstructs from three contiguous HTTP206 ranges; partial500 prefixes are not full PDFs. [Source receipts and byte chains](data/baselines/source/original-read-receipts.json) retain all qualifications.

**Complete statewide candidates and denominators**

A/B below are named source candidates, not a coalition of all non-Republicans. Party abbreviations remain the source labels: D Democratic, R Republican, PG Pacific Green, P Progressive, L Libertarian, C Constitution, NAV Nonaffiliated, WTP We The People. Misc. is a generic reported scope, not proved legally valid named write-ins. Native source aliases/slate labels and party headers remain unchanged in [raw evidence](data/baselines/source/raw-native-rows.jsonl.gz) and [abstract headings](data/baselines/source/abstract-evidence.json). The overlapping six-column vice-president table is [retained nonadditively](data/baselines/nonadditive-vice-president.csv); no absent West/Terry partner column is invented.

| Contest | Complete candidate/Misc. vector in original column order | Reported all-choice total | Named-only total | A/B pair total | A−B net |
| --- | --- | ---: | ---: | ---: | ---: |
'''
 for ct,(source,page,names,a,b) in SPECS.items():
  vals=controls[ct]['values'];v='; '.join(f'{name} ({party}) {n:,}' if party else f'{name} {n:,}' for (name,party),n in zip(names,vals));text+=f'| {ct} | {v} | {sum(vals):,} | {sum(vals)-vals[-1]:,} | {vals[a]+vals[b]:,} | {vals[a]-vals[b]:+,} |\n'
 text+='''
Every county candidate column sums exactly to the corresponding primary footer:864 source cells across the four contests. [Full county candidates](data/baselines/county-candidates.csv), [state controls](data/baselines/state-controls.json), source page/line/raw text, original SHA256 and retrieval clocks are retained. No rescaling, zero-filling, residual allocation or candidate-key deduplication is used.

The current [ORS254.065 official publication](https://www.oregonlegislature.gov/bills_laws/ors/ors254.html), independently downloaded in [current receipts](data/baselines/source/current/network-ors254.receipt.json), specifies the highest vote count for a single office, subject to its stated exception. Pair tie/+1 arithmetic does not replace full-field plurality. Johnson's168,431 NAV votes in2022 governor remain separate from Kotek and Drazan; Smith and Noble also remain separate. Kotek's actual917,074 of1,952,883 reported choices is below50% but above each named opponent. No RCV redistribution, runoff electorate or lower-preference estimate is inferred. Actual2026 ballot candidates/labels must be mapped from final official publications; the [current filings page](https://sos.oregon.gov/elections/pages/candidate-filings-local-measures.aspx) inspected here does not establish a final complete Senate ballot. [Current-election navigation](https://sos.oregon.gov/elections/Pages/current-election.aspx) and primary nominees/old IDs are not substituted.

**Every county, including the nonpriority remainder**

Margins are historical **A−B pair-margin percentage points** for the named Democratic/Republican pair in that contest; other candidates are retained in the linked full-field table. A positive value describes that election's Democratic pair lead, not a permanent county identity.2024 volume includes generic Misc. The table derives directly from the three cited official abstracts.

| County |2024 reported choices|2024 president pair margin|2020 same-seat Senate|2022 other-seat Senate|2022 governor|2024 native closed rows|
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
'''
 counts={'Clackamas':118,'Marion':118,'Multnomah':107,'Wasco':12,'Washington':155}
 for county in COUNTIES:
  rows=[idx[ct,county] for ct in ['2024-president','2020-senate','2022-senate','2022-governor']];ms=' | '.join(f"{100*float(r['A_minus_B_pair_margin']):+.2f}" for r in rows);text+=f"| {county} | {int(rows[0]['reported_all_choice_votes']):,} | {ms} | {counts.get(county,'unknown')} |\n"
 text+='''
**Historical volume, mix and preference sensitivities**

Low uses the actual2022 Senate all-choice county volume1,927,949; base uses actual2024 president2,244,493; high uses actual2020 Senate2,321,249. These settings deliberately change both historical total and county mix; their labels describe these selected historical anchors, not2026 turnout forecasts or confidence bounds. A fourth actual-governor-volume case uses1,952,883. Each preference anchor is separately2024 president,2020 Senate,2022 Senate or2022 governor. Within every county V is the selected source volume and pair volume is **V × that preference contest's county pair participation**. Other named/generic candidate fractions remain those of the preference contest. The full report settings match [calculator inputs and26 scenarios](data/baselines/historical-scenarios.json).

| Preference anchor | Historical volume/mix | Expected pair pool | Baseline A−B net | Tie A-share shift points | A+1 A-share shift points |
| --- | --- | ---: | ---: | ---: | ---: |
'''
 for o in sc:
  if not o['scenario_id'].endswith('-tie'):continue
  r=o['result'];plus=next(x for x in sc if x['scenario_id']==o['scenario_id'].removesuffix('-tie')+'-Aplus1')['result'];setting=o['scenario_id'][len(o['preference'])+1:-4]
  text+=f"| {o['preference']} | {setting}: {next(iter(o['mix']))} | {r['pair_volume']:,.3f} | {r['baseline_net_votes']:+,.3f} | {r['bounded_share_shift_points']:+.6f} | {plus['bounded_share_shift_points']:+.6f} |\n"
 text+='''
For fixed weights, unbounded tie shift=(B−A)/(2(A+B)); an A+1 pair-margin target adds.005 share fraction, **0.5 share points**. A1-point share gain creates2 pair-margin points and.02×pair-volume net votes. Share points, margin points and net votes are different outputs. For2024 president the A+1 target is21,600.8 net votes on2,160,080 pair votes; its reported-all-choice margin is about0.9624 points on2,244,493, not1 point on that denominator. The actual2022 governor pair-volume tie shift is−1.887694 share points; +1 pair margin is−1.387694, while its all-choice margin is0.905032 points. All other candidates remain explicit in each scenario, and the full-field named-opponent checks are saved separately.

The solver first displays the unbounded shift, clips every unit share to[0,1], then solves a feasible bounded shift with a residual check. These historical cases require no clipping, but executed synthetic fixtures exercise clipping. [936 county contribution rows](data/baselines/county-contributions.csv) retain all36 parents, expected volumes, pair participation, weights, baseline/target net contributions and net-vote gains. [Every local native/county tie and +1 target](data/baselines/local-pair-targets.csv) remains source-scoped; unknown preference/volume is null. [Known-source native scenarios](data/baselines/known-native-scenarios.json) model only their explicitly stated closed historical pool, never an incomplete statewide native electorate.

**Selected-unit-only paths**

There is no unique required performance in a county. [County selected-only targets](data/baselines/county-selected-targets.csv) change only the selected county, holding every other county at its named historical preference, volume, mix and participation. [Native selected-only state targets](data/baselines/native-selected-state-targets.csv) change one column-closed source-local unit, with all36 same-contest county totals and every other vote fixed at explicit aggregate historical assumptions. Unknown native rows stay unknown; no residual is assigned to an invented unit. Requirements below0 remain secured-even-at-zero; above1 remain impossible-even-at-one, alongside unbounded and clipped display shares. No-positive-pool and unknown cases remain separate.

For the base2024 presidential tie, illustrative selected-county results are:

| Selected county only | Historical A pair share | Other-county net votes fixed | Required A share, unbounded | Status |
| --- | ---: | ---: | ---: | --- |
'''
 selected=list(csv.DictReader((R/'county-selected-targets.csv').open()))
 for county in ['Multnomah','Washington','Baker']:
  r=next(x for x in selected if x['scenario_id']=='2024-president-base-tie' and x['county']==county);text+=f"| {county} | {100*float(r['selected_baseline_share']):.4f}% | {float(r['other_net_votes_fixed']):+,.0f} | {100*float(r['unbounded_required_share']):.4f}% | {r['status']} |\n"
 text+='''
**Native coverage, source scopes and exact80 contract**

The [Multnomah original CSV](https://multco.us/file/sovc2_-_election20241105general.csv/download) gives107 precinct vectors; its [presidential PDF](https://multco.us/file/2024-11_pres_vp.pdf/download) independently matches all107 and supplies separate ballot/registration/nonvote controls. The [Clackamas complete canvass](https://dochub.clackamas.us/documents/drupal/3a834f56-37f7-4942-84da-8b0c38e90021) gives118 literal rows although the header prints119 precincts:115/116 is one combined row, with no split allocation. [Marion's complete canvass](https://www.co.marion.or.us/CO/elections/Results/Documents/20241105/Canvass%20Results-12-2-2024%2007-24-08%20PM.pdf) gives118 rows. [Washington's scanned original](https://www.washingtoncountyor.gov/elections/documents/november-5-2024-ballots-cast-contest-precincts/download?inline) gives155, with explicit raster readings retained. [Wasco's full46-page original](https://records.sos.state.or.us/ORSOSWebDrawer/Record/10575034/File/document) gives12. All510 rows close all eight county columns, and [all ballot/over/under identities](data/baselines/known-native-controls.csv) balance. Their reporting keys are historical source-local identities, not geometry.

Washington's table ballots301,104 equals297,949 choices+170 overvotes+2,985 undervotes; its overall header prints301,105. No one-ballot residual is allocated. Wasco Precinct01 president has1,831 ballots, whereas some other offices print1,830. Clackamas Cast Votes excludes its separate Miscellaneous Write-In lane; Marion Cast Votes includes its generic write-in. Multnomah CSV overvote fields are candidate-specific; they do not become contest overvote-ballot totals. AB/ED/EV, Absentee Voting, Vote by Mail, central/reporting-group and Total presentations remain source-specific and nonadditive. The [raw method evidence](data/baselines/native-method-lanes.json), [nonadditive bindings](data/baselines/source/nonadditive-presentation-bindings.json), full original page index and source rows preserve all available lanes and unresolved identities.

The complete2020/2022 ZIP publications contain72 county-labeled original members:2020 has33 PDFs and three CSVs;2022 has36 PDFs. Their full bytes/member hashes/CRCs are retained once, but county filename is not contest completeness. The original2020 Benton115-page ZIP member is a distinct state-office publication; its separately recovered [262-page federal county original](https://re.bentoncountyor.gov/wp-content/uploads/2023/12/2020Nov03_Precinct-Results.pdf) is retained independently, as is the [189-page2022 original](https://re.bentoncountyor.gov/wp-content/uploads/2023/12/2022Nov08-Precinct-Results.pdf). [Every county/source/contest reconciliation](data/baselines/native-reconciliation.json) states missing columns, vectors and exact differences; [every original PDF page](data/baselines/source/whole-original-page-index.jsonl.gz) and required raw candidate/admin evidence remain available. Normalized historical closure is16 parents for2020 Senate,13 for2022 Senate,13 for2022 governor. Unclosed/OCR/identity/method cells are unknown, not zeros; raw text search absence is not proof of source absence.

The current [SOS historical-data page](https://sos.oregon.gov/elections/pages/historical-data.aspx) was refreshed and its literal2024 precinct search again returned no records for that particular query. Earlier observed public form responses returned older ZIPs and did not preserve requested filters; no guessed record enumeration or exhaustive absence claim follows. [Lane's official archive](https://www.lanecounty.org/government/county_departments/county_administration/general_county_administration/operations/county_clerk/elections/historical_election_details) says precinct results beginning2023 require request/redaction and may incur a fee. Its earlier complete200 body is retained; this worker's fresh request returned403. No outreach is authorized/performed. Bounded public recovery ends with these precise gaps.

The five-parent known-source universe has1,128,521 reported presidential choices; the other31 parents retain1,115,972 in complete county/state arithmetic, with unknown native membership. In the known-only [full descending order](data/baselines/known-native-order.csv), top15=112,024/1,128,521=9.926621%; first213 rows reach904,600, with predecessor902,447 below the exact integer threshold902,817. This is not statewide80%. Separately, [all36 county sensitivities](data/baselines/county-priority-order.csv) have top15=1,983,101/2,244,493=88.354074%; first11 reach1,814,630, while the preceding10 total1,764,398 below threshold1,795,595. Neither county order nor provisional known-only order is an approved native dispatch. [Contract and31 explicit unavailable parents](data/baselines/priority-contract.json) retain null canonical order/top15/minimum80.

**Turnout, registration and source disagreements**

| Election-specific statistical publication | Number Eligible/registration | Ballots Returned | Separate contest totals |
| --- | ---: | ---: | --- |
|2020|2,944,588|2,413,890|Senate2,321,249 reported choices|
|2022|2,985,820|1,997,689|Senate1,927,949; governor1,952,883|
|2024|3,060,374|2,308,256|President2,244,493|

All36 county participation columns close independently to their source footers. The complete archived primary statistical publications are [2020](https://web.archive.org/web/20210101093606id_/https://sos.oregon.gov/elections/Documents/statistics/november-2020-statistical-summary-participation.pdf), [2022](https://web.archive.org/web/20221221182416id_/https://sos.oregon.gov/elections/Documents/statistics/november-2022-statistical-summary-participation.pdf) and [2024](https://web.archive.org/web/20241227170225id_/https://sos.oregon.gov/elections/Documents/statistics/November-general-2024-statistical-summary-participation.pdf). [Party/county participation rows](data/baselines/participation-controls.csv) retain printed labels, zeros and anomalies.2024's General Election statistical heading coexists with repeated Primary Election wording on page1; Jefferson's We The People row prints0 Number Eligible and1 returned ballot. Those source values remain unchanged.

The separate [current general-turnout-history PDF](https://sos.oregon.gov/elections/Documents/History/Voter_Turnout_History_General_Election.pdf), generated09/12/2025, prints2020 Total Votes Cast2,317,965 and registration2,951,428, below the Senate contest's2,321,249 choices and different from the election-specific participation stock. The [November monthly registration publications](data/baselines/monthly-registration.csv) are yet another dated stock. Returned ballots, accepted/cast ballots, contest votes, blank/under/over counts and registration definitions cannot be forced equal. All statewide canvass ballot/blank/nonvote native controls remain unavailable outside verified source scopes; no county/native allocation is invented. Historical totals do not project2026 turnout or remaining votes.

**Offline conditional live remainder calculator**

Run `python3 -B senate/2026/oregon/data/baselines/scripts/calculator.py INPUT.json` from the repository root. [Schema and reproduction contract](data/baselines/source/SCHEMA.md) describes county/native/uniform/selected/live modes, actual source-key checks, finite scalar validation, supported denominators and unknown inputs. For a historical run use [a saved county fixture](data/baselines/fixtures/county-positive-historical-mix.input.json); for a live run use [the final-all-choice fixture](data/baselines/fixtures/live-final-all-choice.input.json). No network connection is needed.

Counted A/B/each other candidate remain fixed. Only a stated remaining pool, its pair participation, pair preference and nonpair allocation are forecast. Final pair denominator=countedA+countedB+remaining pair; final all-choice adds counted and remaining other votes. For target margin m, final denominator F, counted lead L and remaining pair U, required A share=(mF−L+U)/(2U). Selected-only adds every other remaining unit at its explicit fixed preference. Unknown, no-pool, negative-invalid, already-secured, impossible and clipped cases are saved as meaningful [executed CLI fixtures](data/baselines/fixtures/results.json), with separate full-field arithmetic plurality. They are not calibrated probabilities or inferred source preferences.

The synthetic live example fixes counted A40/B60/Named C10 and supplies100 remaining all-choice votes,80% pair participation,60% remaining A pair share and all nonpair votes to Named C. Final arithmetic is A88/B92/C30. Final pair denominator180 gives a+1 pair-margin threshold63.625% A among remaining pair votes; final all-choice denominator210 gives63.8125%. A different saved case lets Named C win despite an A/B pair threshold. Bool/null/text/nonfinite/malformed numeric targets, invalid mix/key/denominator surfaces and negative counted/remaining inputs return structured strictJSON errors; unknown source inputs remain explicitly unknown.

**Independent reconciliation and checks**

The immutable [pre-peer witness](data/baselines/source/pre-peer-witness.json), SHA256`208a3ad98dfb055eea0f895c0c0faf9881f684214e7d5a34c41e01f4df123b7f`, and [frozen independent bodies](data/baselines/source/pre-peer-body-map.json) precede opening turnout parsed counts/order/transcriptions. Actual turnout worker bd151c4c-70ea-4b72-9063-2012086b07e6 was already finished and was not contacted/restarted. [Read-only captured peer comparison](data/baselines/peer-reconciliation.json) matches all864 county source cells/parties/raw positions,144 county totals, participation/monthly stocks, all4,080 known native presidential cells and the complete510-row order using the peer's versioned FIPS/native-key tie rule. The [peer-compatible re-expression](data/baselines/source/peer-contract-native-order.json) preserves our source-local keys alongside that contract; equal-volume tie ordering is declared, not a changed count.

The comparison also matches1,827 full original CSV candidate/method-counter dictionaries. It preserves one shared candidate and16 control disagreements in **unclosed Douglas2022 normalization**, rather than importing peer values.2020 closed-parent sets differ: our original-raster Coos closes while peer Harney closes;2022 governor our independently read Wasco closes beyond the peer's set. Tillamook was independently reparsed from its original named-unit headings after the initial comparison exposed an extraction gap. Source repairs and earlier bodies are both retained. These are scope/normalization findings, not mutual or coordinator acceptance.

The package executes63 real CLI fixtures and120 independent analytic piecewise-linear bounded-root checks. [Validation](data/baselines/validation.json) audits identities, uniqueness, candidate controls, raw/source hashes, complete/partial coverage, volumes/weights/denominators, exact80/predecessor/order, bounds, links and asset sizes. [Reproduction script](data/baselines/scripts/reproduce.py) rebuilds the source extraction, calculations, report and QA offline; acquisition is a separate bounded explicit action. The [asset manifest](data/baselines/asset-manifest.json) and [acyclic seal](data/baselines/seal.json) pin the finished owned package. No dependency/cache directory, Git mutation, delegated research, implemented live collector, approved current precinct map, measured live cadence or calibrated Needle is claimed. Future final-ballot/legal/feed/geometry/private-source exhaustion is a qualification, not an unfinished recovery loop.
'''
 parts=re.split(r'(\]\([^)]*\)|`[^`]*`)',text)
 for i in range(0,len(parts),2):
  parts[i]=re.sub(r'([A-Za-z])(\d)',r'\1 \2',parts[i])
  parts[i]=re.sub(r'(\d)([A-Za-z])',r'\1 \2',parts[i])
  parts[i]=parts[i].replace('ClassIII','Class III').replace('ClassII','Class II').replace('SHA 256','SHA256')
 text=''.join(parts).replace('remainfalse','remain false')
 text=re.sub(r';(?=\d)', '; ',text)
 text=re.sub(r'([A-Za-z)])\.(?=\d)',r'\1. ',text)
 (R.parent.parent/'county-partisanship.md').write_text(text)
 print(json.dumps({'report':'county-partisanship.md','bytes':len(text.encode())}))
if __name__=='__main__':main()
