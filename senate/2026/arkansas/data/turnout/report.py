#!/usr/bin/env python3
"""Generate the report exclusively from the original-first turnout package."""
import csv, json, pathlib
from decimal import Decimal
P=pathlib.Path(__file__).resolve().parent
S=P.parents[1]
def load(n):return json.loads((P/n).read_text())
def pct(n,d):return f'{Decimal(n)*100/Decimal(d):.8f}%'
def num(n):return f'{n:,}'
def main():
    contract=load('priority-set.json');stats=load('orders/statistics.json');checks=load('build-checks.json');api=load('extracted/api-controls.json');full=load('extracted/full-controls.json');t=load('extracted/turnout-controls.json')
    rows=contract['full_order'];st=stats['2024-xlsx'];n=st['minimum80_count'];cross=rows[n-1]
    reciprocal=load('reciprocal.json') if (P/'reciprocal.json').exists() else None
    xurl='https://www.sos.arkansas.gov/uploads/elections/2024_General_Election_and_Nonpartisan_Judicial_Runoff_Election_Precinct_Level_Results.xlsx'
    pdf='https://www.sos.arkansas.gov/uploads/elections/GE2024_report.pdf'
    hist='https://sos.arkansas.gov/elections/research/election-results'
    apiurl=lambda y:f'https://enr-results-api.totalresults.com/Contest/GetContestResults?cId=arkansas&electionID={ {2024:1846,2022:1844,2020:1841}[y]}&contestType=FED'
    fullurl=lambda y:f'https://results.tally-enr.com/results/arkansas/{ {2024:1846,2022:1844,2020:1841}[y]}/FullDataFile.json'
    clerk=lambda y:f'https://clerk.house.gov/member_info/electionInfo/{y}/statistics{y}.pdf'
    out=[f'''# Arkansas reported vote volume and native reporting geography

Observed **2026-10-20 UTC**. Priority basis: **2024 U.S. President, seven reported ballot candidate choices**, from the complete official precinct XLSX. Arkansas did not hold a 2024 U.S. Senate election. This is a historical vote-volume ranking; candidate votes are not ballots cast. The [SOS historical index]({hist}) links the [original XLSX]({xurl}) and [Official Results PDF]({pdf}); the file described as precinct “CSV” is actually OOXML. Its 69,355 data rows cover 669 contest titles; the complete original bytes, including unrelated offices, are retained by immutable hash.

**The top 15 native units contribute {num(st['top15_votes'])} / {num(st['denominator'])} = {pct(st['top15_votes'],st['denominator'])}. The minimum descending set reaching 80% contains {num(n)} units: {num(st['minimum80_votes'])} votes = {pct(st['minimum80_votes'],st['denominator'])}.** The preceding {num(st['preceding_count'])} have {num(st['preceding_votes'])} votes = {pct(st['preceding_votes'],st['denominator'])}; **{cross['county_name']} / {cross['native_name']}** contributes {num(cross['votes'])} and crosses the integer threshold of {num(st['integer_threshold'])}. The remaining {num(st['remainder_count'])} units contribute {num(st['remainder_votes'])}, remain in all statewide arithmetic, and appear in the full order and remainder arrays. These are calculations from the [official precinct candidate rows]({xurl}), reconciled to all 525 county/candidate cells in the [PDF]({pdf}) and the [House Clerk]({clerk(2024)}).

The [exact dispatch contract](data/turnout/priority-set.json) contains all 2,841 primary units, ordered priority keys, full order, remainder, all 75 county parents, and every recovered native constituent in each source/year lane. The compatibility file [county-turnout.csv](data/county-turnout.csv) contains **2,841 native rows**, not substituted county rows. The 1,056 priority units have parents in **{len(contract['priority_parent_fips'])} counties**. The [75-county control table](data/turnout/extracted/all75-county-controls.csv) and separate county sensitivities are supporting views, not native dispatch. **The bounded captured-final baseline source/field/order reciprocal passes; coordinator acceptance remains pending.** The [reciprocal proof](data/turnout/reciprocal.json) identifies the exact finished-peer capture and exclusions. This package does not self-approve a geography or a November source.

## The exact top 15

County and unit labels below are source literals. A school-like label is a reported-unit name, not evidence that the unit is a polling site or school district. No name-based type, polygon or November identity is inferred. Source: [SOS precinct XLSX]({xurl}); raw row positions are in the linked CSV and [lossless relevant-row extraction](data/turnout/extracted/2024-xlsx-president-raw-rows.json.gz).

| Rank | County FIPS | County | Literal native unit | Candidate votes | State share | Cumulative share |
| ---: | --- | --- | --- | ---: | ---: | ---: |''']
    for r in rows[:15]:out.append(f"| {r['rank']} | {r['county_fips']} | {r['county_name']} | {r['native_name']} | {num(r['votes'])} | {pct(r['votes'],st['denominator'])} | {pct(r['cumulative_votes'],st['denominator'])} |")
    out.append('''
The complete minimum set is precisely ranks 1–1,056 in the [full native order](data/turnout/orders/2024-xlsx.csv); ranks 1,057–2,841 are its remainder. The JSON gives the exact ordered key lists so a reader need not reconstruct a large set from prose. Ties use the literal source-scoped key ascending after descending integer votes. Because the largest 1,055 sum below 80%, no selection of 1,055 units can reach it. No rounded percentage decides the crossing.

| Position | County | Native unit | Votes | Cumulative votes | Cumulative share |
| ---: | --- | --- | ---: | ---: | ---: |''')
    for r in rows[n-3:n+2]:out.append(f"| {r['rank']} | {r['county_name']} | {r['native_name']} | {num(r['votes'])} | {num(r['cumulative_votes'])} | {pct(r['cumulative_votes'],st['denominator'])} |")
    out.append(f'''
## Candidate universe and whole-state primary reconciliation

Every one of the 2,841 literal county/precinct pairs has exactly seven candidate rows: 19,887 rows in total. Every candidate sums from native rows through all 75 county parents to the [Official Results PDF]({pdf}), the [2024 API]({apiurl(2024)}), and the [House Clerk]({clerk(2024)}). The parser matches each source's candidate descriptor/name or ballot-party identity; it does not reuse one global row ordinal. The primary PDF's candidate order and the API's choice IDs differ. The saved [PDF controls](data/turnout/extracted/2024-pdf-controls.json) retain each line and seven numeric cells; [Clerk controls](data/turnout/extracted/clerk-controls.json) retain each identity token and line.

| 2024 candidate/ticket literal | XLSX/PDF ballot label | Native sum = PDF = API = Clerk | FullData | FullData minus primary |
| --- | --- | ---: | ---: | ---: |''')
    parties=rows[0]['party_literals']
    for name,v in api['2024']['candidates'].items():out.append(f"| {name} | {parties[name]} | {num(v)} | {num(full['2024']['candidates'][name])} | +{num(full['2024']['api_difference'][name])} |")
    out.append(f'''| **All seven** | | **1,182,676** | **1,184,575** | **+1,899** |

The XLSX has no blank, undervote, overvote, generic write-in, valid-write-in or named-write-in field. The API's actual `writeInChoices`/`writeinChoices` arrays are retained as published, and no extra candidate is inserted. The reported candidate universe is complete for these sources; the inspected sources do **not** establish a separately eligible/named write-in universe. An eligible-write-in-complete rank/minimum/dispatch therefore remains null, rather than being claimed from absent fields. No unreported category is converted to zero. Source scopes: [XLSX]({xurl}), [API]({apiurl(2024)}), [candidate metadata](https://enr-results-api.totalresults.com/Contest/GetContestSearchList?cid=arkansas&electionID=1846).

## Disjoint hierarchy and source-native identity qualifications

The primary arithmetic uses each literal XLSX county/precinct pair once, with its seven candidate rows and four additive candidate-vote method columns. County parents are sums of those leaves; statewide and county summaries are control views and are never added to leaves. FullData's `Counties` array contains repeated county wrappers, generally one precinct each: 2,839 wrappers in 2024, 2,467 in 2022, and 2,574 in 2020, but only 75 distinct county parents. Source-array positions survive; wrappers are not treated as additional counties. Complete original and relevant raw records survive, without deduplication or repair. Sources: [2024 FullData]({fullurl(2024)}), [2022 FullData]({fullurl(2022)}), [2020 FullData]({fullurl(2020)}).

The API supplies returned county FIPS-like IDs and native string IDs, including leading zeros. The client config identifies Arkansas/05. The XLSX and FullData have literal native names but no native IDs. Source keys constructed here are explicit source/year/parent/position or literal-name keys, not invented official IDs. **2,836** XLSX units have a unique exact county/name and seven-candidate-vector match to a 2024 API unit; that records evidence of a historical source match, not legal/geometry approval. Five XLSX units retain unavailable API-ID matches:

| County | XLSX literal | Votes | Actual comparison |
| --- | --- | ---: | --- |
| Conway | MENIFEE CITY | 137 | Same-name API ID 49458440 has 218 votes; not an identical constituent |
| Conway | MENIFEE RURAL | 81 | No literal API counterpart |
| White | Beebe Ward 3 | 709 | Same-name API ID 10759416 has 1,681 votes; not an identical constituent |
| White | Beebe Ward 3C | 972 | No literal API counterpart |
| Ouachita | `001  Camden` | 1,106 | API literal spacing differs; no silent name normalization |

The API Menifee vector equals the sum of the two XLSX Menifee vectors, and its Beebe Ward 3 vector equals the two XLSX Beebe vectors, candidate by candidate. This is an observed numerical relationship; it is not a recovered authoritative crosswalk. Native API coverage is 2,839 units; the primary XLSX retains all 2,841. Its 80% crossing is consequently one unit later than the API's 1,055-unit crossing, despite identical statewide and county controls. Both full orders are preserved. Sources: [XLSX]({xurl}), [Conway API](https://enr-results-api.totalresults.com/Contest/GetContestResults?cId=arkansas&electionID=1846&contestType=FED&locationId=05029), [White API](https://enr-results-api.totalresults.com/Contest/GetContestResults?cId=arkansas&electionID=1846&contestType=FED&locationId=05145), [Ouachita API](https://enr-results-api.totalresults.com/Contest/GetContestResults?cId=arkansas&electionID=1846&contestType=FED&locationId=05103). See [exact disagreements](data/turnout/extracted/2024-xlsx-api-native-disagreements.json).

Literal Central/ward/split-looking names are retained. Their administrative type and polygon eligibility remain unknown where the source supplies no type. Methods are separate columns, not extra geographic rows. No historical precinct, polling site, vote center, VTD, municipal area, combined unit or November 2026 boundary is declared equivalent from names or counts. All-year native inventories and raw returned IDs are in [source-native universes](data/turnout/extracted/source-native-universes.json.gz) and the contract's parent/source arrays. Source hierarchy: [2024 ElectionInfo](https://enr-results-api.totalresults.com/Election/GetElectionInfo?cId=arkansas&electionID=1846), [2022 ElectionInfo](https://enr-results-api.totalresults.com/Election/GetElectionInfo?cId=arkansas&electionID=1844), [2020 ElectionInfo](https://enr-results-api.totalresults.com/Election/GetElectionInfo?cId=arkansas&electionID=1841).

## Publication disagreements and the actual historical Senate contests

The [House Clerk's 2022 named candidate totals]({clerk(2022)}) independently agree with the [API]({apiurl(2022)}); the [2020 Clerk]({clerk(2020)}) agrees with its [API]({apiurl(2020)}). That supports the API candidate lane for these comparators. FullData is a separately published official-format source that internally balances to its own statewide candidates; it is not silently replaced, rescaled or “corrected.” No amendment cause or chronology is established by its differing totals.

| Election/contest | Candidate literal in vendor | API = Clerk | FullData | Difference |
| --- | --- | ---: | ---: | ---: |''')
    for year in [2022,2020]:
        for name,v in api[str(year)]['candidates'].items():out.append(f"| {year} U.S. Senate | {name} | {num(v)} | {num(full[str(year)]['candidates'][name])} | +{num(full[str(year)]['api_difference'][name])} |")
    out.append(f'''
**2022 Boozman–James–Cates is the actual other-seat Class III Senate midterm comparator. 2020 Cotton–Harrington is the same Class II seat.** The Clerk identifies Harrington as Libertarian, and there was no Democratic Senate nominee in that two-candidate 2020 result. Any opposition scenario must name **Ricky Dale Harrington Jr. (Libertarian)**; a Democratic baseline is unavailable, not manufactured from Harrington or a zero column. The 2022 Clerk identifies Cates as Libertarian. Sources: [2020 Senate table]({clerk(2020)}), [2022 Senate table]({clerk(2022)}). The midterm here is Senate, and no 2024 Senate result is introduced.

Raw vendor party metadata remains separate from these ballot identities. PartyID `1`/blank PartyName stays unknown in that lane, and the API's party dictionary literally contains Nevada party names, including `Nevada Green Party`. No global party mapping overwrites it. Original candidate IDs, order, `isWriteIn`, raw party IDs/names, nulls, headers and JSON/OOXML source positions remain in original and [relevant extractions](data/turnout/extracted/source-metadata.json). Sources: [2024 metadata](https://enr-results-api.totalresults.com/Contest/GetContestSearchList?cid=arkansas&electionID=1846), [2022 metadata](https://enr-results-api.totalresults.com/Contest/GetContestSearchList?cid=arkansas&electionID=1844), [2020 metadata](https://enr-results-api.totalresults.com/Contest/GetContestSearchList?cid=arkansas&electionID=1841).

The FullData excess is localized to Conway/White in 2024 and 2022, and Conway in 2020; all **19 differing county/candidate cells** are retained in the [difference inventory](data/turnout/extracted/full-vs-api-county-candidate-differences.json). In those differing FullData native rows the published vector is exactly twice the corresponding API vector. That observed equality does not authorize deduplication, subtracting a row or allocating a residual. API state/county/native candidates each close separately; FullData wrapper/precinct/state candidates each close separately. Sources: [2024 API]({apiurl(2024)}) / [FullData]({fullurl(2024)}), [2022 API]({apiurl(2022)}) / [FullData]({fullurl(2022)}), [2020 API]({apiurl(2020)}) / [FullData]({fullurl(2020)}).

| Source-scoped native universe | Native units | Contest votes | Top 15 votes / share | Minimum 80% units | Preceding votes | Crossing cumulative votes | Remainder votes |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |''')
    for lane in ['2024-xlsx','2024-api','2024-full','2022-api','2022-full','2020-api','2020-full']:
        a=stats[lane];out.append(f"| [{lane}](data/turnout/orders/{lane}.csv) | {num(a['units'])} | {num(a['denominator'])} | {num(a['top15_votes'])} / {pct(a['top15_votes'],a['denominator'])} | {num(a['minimum80_count'])} | {num(a['preceding_votes'])} | {num(a['minimum80_votes'])} | {num(a['remainder_votes'])} |")
    mid=stats['2022-api'];mc=mid['crossing_geography'];old=stats['2020-api'];oc=old['crossing_geography']
    out.append(f'''
The 2022 API minimum has **{num(mid['minimum80_count'])} native units**, crossing at **{mc['county_name']} / {mc['native_name']}**, native ID `{mc['native_id']}`, with {num(mc['votes'])} votes. The preceding {num(mid['preceding_count'])} contribute {num(mid['preceding_votes'])} / {num(mid['denominator'])}; the crossing sum is {num(mid['minimum80_votes'])}. The 2020 API minimum has **{num(old['minimum80_count'])} units**, crossing at **{oc['county_name']} / {oc['native_name']}**, ID `{oc['native_id']}`; preceding {num(old['preceding_count'])} have {num(old['preceding_votes'])}, crossing sum {num(old['minimum80_votes'])}. Each order, crossing key, full candidate vector, remainder and integer proof is retained in [statistics](data/turnout/orders/statistics.json) and its CSV. Comparisons change both election and candidate/contest context; they are not pure turnout or 2026 forecasts. Sources: [2022 results]({apiurl(2022)}), [2020 results]({apiurl(2020)}).

## Ballots, registration, methods and separate sensitivities

The public [Turnout endpoint](https://enr-results-api.totalresults.com/Turnout/GetTurnout?cId=arkansas&electionID=1846), constructed by the linked public client, returns all 75 county controls. All 75 county queries were downloaded in each required year. **Every county response in all three years returns an empty native `locations` object**, despite `hasLocationTurnout=true`. Thus exact native ballots/registration ranks are unavailable. The actual original responses, including `ballotsReceived`, `ballotsCast`, percent and completion fields, survive in [turnout controls](data/turnout/extracted/turnout-controls.json) and per-year compressed raw records. These flags and “received” totals are not evidence of an outstanding pool or a private suppressed cell.

| Year | Reported contest votes, chosen lane | Ballots cast, source VotesCast | Registered voters, source stock | Ballots minus contest votes |
| --- | ---: | ---: | ---: | ---: |''')
    for year in ['2024','2022','2020']:
        a=api[year]['total_votes'];b=t[year]['county_sum_ballots'];out.append(f"| {year} | {num(a)} | {num(b)} | {num(t[year]['county_sum_registration'])} | {num(b-a)} |")
    out.append(f'''
All county ballot and registration sums match their source statewide controls, and the API and FullData ballot/registration integers agree in these snapshots. Registration is the published `RegisteredVoters` stock; active/inactive scope and registration snapshot date are not documented in the inspected response. Source election dates, retrieval UTC, update strings and official flags remain separate. These are neither voting-eligible population counts nor demonstrated 2026 participation denominators. The ballot-minus-contest differences above cannot be apportioned into blanks, undervotes, overvotes or write-ins from these sources. Sources: [2024 turnout](https://enr-results-api.totalresults.com/Turnout/GetTurnout?cId=arkansas&electionID=1846), [2022 turnout](https://enr-results-api.totalresults.com/Turnout/GetTurnout?cId=arkansas&electionID=1844), [2020 turnout](https://enr-results-api.totalresults.com/Turnout/GetTurnout?cId=arkansas&electionID=1841), and each year's FullData.

The primary XLSX reports **Election Day {num(checks['primary_methods']['Election Day'])}, Early Vote {num(checks['primary_methods']['Early Vote'])}, Absentee {num(checks['primary_methods']['Absentee'])}, Provisional {num(checks['primary_methods']['Provisional'])} candidate votes**. Their sum is 1,182,676, and every original candidate row's four methods add exactly to its total. These are candidate-vote methods, not method ballot counts. API `voteTypeID=1` is explicitly described as **All**, never Election Day. Historical 2020/2022 candidate-method splits beyond All are unavailable in these sources. Sources: [XLSX]({xurl}), [vote-type dictionary](https://enr-results-api.totalresults.com/Election/GetElectionInfo?cId=arkansas&electionID=1846).

The following sensitivities rerank complete source-scoped universes without changing the primary priority contract. Each CSV retains every unit, including published zeros. County distributions compare volume composition only; no registration-derived ballot counts, residual allocation or rescaling is performed.

| Sensitivity universe | Denominator | Top 15 votes / share | Minimum 80% units | Preceding cumulative | Crossing cumulative |
| --- | ---: | --- | ---: | ---: | ---: |''')
    lanes=[f'{y}-county-{field}' for y in [2024,2022,2020] for field in ['contest','VotesCast','RegisteredVoters']]+['2024-xlsx-election-day','2024-xlsx-early-vote','2024-xlsx-absentee','2024-xlsx-provisional']
    for lane in lanes:
        a=stats[lane];out.append(f"| [{lane}](data/turnout/orders/{lane}.csv) | {num(a['denominator'])} | {num(a['top15_votes'])} / {pct(a['top15_votes'],a['denominator'])} | {num(a['minimum80_count'])} | {num(a['preceding_votes'])} | {num(a['minimum80_votes'])} |")
    out.append(f'''
The 2024 county contest top 15 are {', '.join(p['county_name'] for p in contract['all75parents'][:15])}; they supply 785,928 / 1,182,676 = {pct(785928,1182676)}. The county minimum is 29 (951,687 votes); 28 have 943,482 and Logan crosses with 8,205. This is explicitly a county sensitivity; it does not replace the 1,056 native-unit priority. The all-75 table below retains the other 46 county parents too. Source: [official 75-county PDF]({pdf}).

Completion counters are not geographic or vote-completion denominators. API ElectionInfo/Turnout reports 192,150 / 149,550 / 120,525 statewide “totalPrecincts” for 2024/2022/2020; the recovered target-contest native inventories have 2,839 / 2,467 / 2,574. FullData's turnout counters are 2,841 / 2,469 / 2,575, also distinct from some contest arrays. The values are preserved literally and are not used to estimate missing votes, coverage or cadence. The API update strings are December 16, 2025 (2024: `19:41:49.5225815Z`; 2022: `20:01:52.3236434Z`; 2020: `21:10:47.9174647Z`), while FullData HTTP Last-Modified is June 2026; these are publication metadata, not a demonstrated election-night sequence or amendment chronology. Sources: each year's ElectionInfo, Turnout and FullData, with [individual receipts](data/turnout/source/original-pins.json).

## All 75 county parents, separate control view

Descending 2024 presidential candidate volume. All 75 are included regardless of native priority membership. Source counts: [2024 official PDF]({pdf}), [2022 API]({apiurl(2022)}), [2020 API]({apiurl(2020)}), and the three official turnout endpoints cited above. Full candidate/party/method/source records remain in the data package.

| Rank | FIPS | County | President 2024 | Senate 2022 | Senate 2020 | Ballots 2024 | Registered 2024 | Primary native units / priority |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |''')
    for p in contract['all75parents']:
        f=p['county_fips'];co=p['source_scoped_county_controls'];pp=[r for r in rows if r['county_fips']==f];pr=sum(r['rank']<=n for r in pp)
        out.append(f"| {p['rank']} | {f} | {p['county_name']} | {num(p['votes'])} | {num(co['2022']['api_total_votes'])} | {num(co['2020']['api_total_votes'])} | {num(co['2024']['full_turnout']['VotesCast'])} | {num(co['2024']['full_turnout']['RegisteredVoters'])} | {len(pp)} / {pr} |")
    out.append(f'''
## Bounded captured-final reciprocal

The same turnout worker verified all **1,027 old manifest targets plus the manifest itself**, exact 1,028-file membership, and all **19 individually pinned shared-original references before edits**. It then froze all 1,028 whole turnout bodies and all **314 actual final baseline bodies** (313 targets plus manifest) before numerical comparison. Whole mutable bodies are losslessly captured; large existing original gzips and historical archives are reused only by individual immutable path/hash/size/role pins. The [capture registry](data/turnout/history/captured-final-reciprocal/capture.json) reconstructs every old path/body, including old report, scripts, raw/control/hierarchy/order/null/admin witnesses, validation, seal, manifest and history. The old manifests are read from the captures, never checked against later mutable files.

The peer is actual finished Arkansas baseline agent `302e0938-9d85-4b49-99c1-87bbb564364d`. Captured baseline manifest SHA-256 is `6d320e1b8b87fbea6788a7343544e39fab21dc81019c6f3e63251ba81baee8c4`; captured final seal SHA-256 is `65b1de23e7354ededcb3df40dc2be6f4aaea02efea3bf3191b1d1b66aecc7f22`. Its independently frozen original-first ten-body archive predates peer input and remains individually pinned. A complete peer freeze establishes provenance, not equality of every peer output.

The [independent reciprocal](data/turnout/reciprocal.json) passes **{reciprocal['checks']:,} strict typed structural/value checks, zero errors**. It compares 490 whole original receipts and raw/stored byte pins; 19,887 complete workbook rows/198,870 cells, headers/types/raw-v/shared strings; 198,525 required positional candidate/party/method rows; 24,096 complete selected raw source controls; 10,454 native descriptors with explicit contest context; four complete metadata records; all 225 complete county turnout envelopes; all 20 full rank orders and integer proofs; and all 75 parent/full 2,841/1,056 priority/1,785 remainder arrays. Source positions are checked through explicit companion expansion. Original child arrays omitted from a node witness are covered by exact child-node/pointer inventories and retained whole original bytes, not silently projected away. All 2,836 matches, five exact-match gaps and 19 required county/candidate differences remain source-scoped.

The captured peer's final reverse proof reports 162,714 passing checks with zero errors, superseding its earlier adapter proof; the whole old checker/report/schema/failing adapter history is retained in the peer capture. This statement applies only to that captured final source/native/field/order/array proof. It does not assert later/future peer report, calculator, scenario, target, outcome, pool or current-state equality. Contextual 2020 presidential numeric differences and baseline-only scenarios are outside turnout numeric equality; their whole shared raw original entity bytes/metadata remain preserved.

The [isolated original-scope replay](data/turnout/isolated-replay.json) rebuilt **49 output bodies byte-for-byte against their whole old captured bodies**, using only fixed individual original pins in a temporary tree. Audit hooks denied network, non-PDF-extraction subprocesses, mutable helper/peer discovery reads and all producer/outside writes. The [24 complete negative inputs](data/turnout/reciprocal-fixtures.json) all reject missing native/candidate/method/null/admin/header/source/companion/control/metadata fields, wrong IDs/order/80%/duplicates, county substitution, residual allocation, source normalization and current/feed admission. These are fixtures, not modified election counts. An actual checker cache-lookup failure, its whole version, error and input context were retained [before the narrow adapter fix](data/turnout/history/reciprocal-state-document-adapter/actual-error.txt); no source or calculator value changed.

The full canonical contract differs only in its explicit bounded-review status. Every other field/object/value/null/admin/source/ID/key/order and the native CSV remain exact against the old whole-body capture. Coordinator/legal/current/native-geometry/November-feed/collector/forecast/probability approvals remain false or unknown.

## Reproduction, retained evidence and bounded finish

Read-only checks and an isolated original-only rebuild:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/arkansas/data/turnout/replay_original_scopes.py --check
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/arkansas/data/turnout/reciprocal.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/arkansas/data/turnout/test_reciprocal.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/arkansas/data/turnout/validate.py --sealed
```

The original-only builder is retained unchanged; the bounded replay executes its captured old body only in an isolated temporary output tree. Explicit review status is separately reproducible through `reciprocal_status.py`; it refuses any other canonical semantic change.
''')
    out.append('''
The separately invoked [acquirer](data/turnout/acquire.py) retrieves the exact public routes and returned county IDs; it reuses successful receipts on replay and refuses failed responses as inputs. It stores complete original response bytes with gzip, requested/final URLs, UTC times, curl status/redirect metadata, raw response headers, raw/stored SHA-256 and sizes. The 471 successful acquired receipts cover the archive, all three years' metadata/results/turnout, 225 county result responses, 225 county turnout responses, all three House Clerk PDFs and current 2024 originals. Large shared originals are reused read-only by individually pinned hashes/receipts; no mutable newsroom manifest, numerical preflight or peer derivative is a build input. Reused original bytes are reconstructed by a single gzip decompression; no truncation, simplification, demographic expansion or source repair occurs. Four timeout receipts and empty bodies were retained before successful bounded retries. The early failing native-match assumption and exact failing build/fixture also survive under [history](data/turnout/history/native-match-finding/finding.json), distinguished from the source disagreement.

The [source schema and authority chain](data/turnout/source/SCHEMA.md), [build checks](data/turnout/build-checks.json), [offline validation](data/turnout/validation.json), [final seal](data/turnout/final-seal.json) and [complete owned asset manifest](data/turnout/asset-manifest.json) describe reproducibility and audit scope. The manifest excludes only itself, is written last, and includes every owned report/script/receipt/history/proof/validation/seal. A final read-only audit checks exact membership, hashes, source dependencies, relative links, no cache/dependency directories and the strict <40,000,000-byte bound. Official PDF pages 2–3 were rendered and visually checked against the extracted headings, candidate identities, county columns and totals. The original-first [core snapshot](data/turnout/history/original-first-core/snapshot.json) freezes raw/extracted/control/order evidence before any peer input; the final package adds turnout and method sensitivities independently.

Material external qualifications remain: coordinator acceptance beyond the bounded captured-final reciprocal; authoritative fine-unit crosswalk/type/legal geography; eligible/named write-in completeness; native ballot/registration and blank/under/over controls; registration status/date definitions; current certified November candidates/IDs/ballots/rules and later controlling documents; live publication cadence, exact outstanding pool and calibrated probability. The historical all-unit inventory, reported-candidate statewide reconciliation, full descending order and minimum-80 arithmetic are complete within their stated source scopes. This is research, with no implemented collector, calibrated Needle or real 2026 turnout forecast.
''')
    (S/'turnout.md').write_text('\n'.join(out)+'\n')
if __name__=='__main__':main()
