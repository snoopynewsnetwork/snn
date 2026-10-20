"""Generate report from integer outputs. Primary dispatch is native, parents are sensitivity."""
from common import *
def run():
    ranks=json.loads((ROOT/'rankings.json').read_text());r=ranks['native_senate2024'];parent=ranks['senate2024'];candidate=json.loads((ROOT/'candidate-reconciliation.json').read_text());pdf=json.loads((ROOT/'extracts/pdf-controls.json').read_text());ns=json.loads((ROOT/'native-inventory.json').read_text());ms=json.loads((ROOT/'municipal-controls.json').read_text())
    top=', '.join(f"{x['native_code']} {x['name']}"for x in r['order'][:15]);minimum=', '.join(x['native_code']for x in r['order'][:r['minimum80_count']]);pnames=', '.join(x['name']for x in parent['order'][:21])
    out=f'''# Rhode Island vote-volume ranking and turnout controls

Research: 2026-10-20 UTC. **Canonical priority ranks all 458 actual 2024 Senate source reporting codes**, using printed-candidate votes plus the source's generic Write-in. This is reported vote volume, not ballots cast, a turnout rate, a verified eligible-write-in universe or a 2026 forecast. The 43 municipality/state-administrative parent ranking is a separate sensitivity.

**Native top 15:** {top}. They supply **34,697 / 491,948 = {r['top15_pct']:.10f}%**.

**Minimum descending set reaching 80%: 242 native contexts**, totaling **394,072 / 491,948 = {r['minimum80_pct']:.10f}%**. The preceding **241 total 393,066 = {r['preceding_pct']:.10f}%**. **Cumberland 0804 (code 0804), 1,006 votes, crosses at rank 242**. Its anchor is root `rigen2024l.txt`, line 4061, zero-based byte 1,075,900, in archive SHA-256 `a2fd599d247e1e7b5d5e0d8de1dcf43491500532f47310284df548ac9848e444`. The **216-context remainder contributes 97,876 = {r['remainder_pct']:.10f}%**, including 15 explicitly published zero-total Senate contexts. Sorting largest first proves that no set of only 241 contexts reaches 80%. The integer test is `5*cumulative >= 4*491948`; the required integer total is 393,559. Ties use ascending first Senate record byte position within the root member. [Original long ZIP](https://www.ri.gov/election/results/2024/general_election/data/rigen2024l.zip), [Board official summary, pp. 1–2](https://elections.ri.gov/sites/g/files/xkgbur756/files/2024-12/Gen24SummaryReport.pdf).

The [dispatch contract](data/turnout/priority-set.json) contains all 458 ordered native source-position keys, the exact ordered priority keys, preceding/crossing/remainder arithmetic, all 497 available native inventory entries, complete candidate constituent positions and all 14 method slots. [The compatibility CSV](data/county-turnout.csv) has **458 native rows**; its filename does not authorize county or municipal substitution. The complete order below defines the exact set as ranks 1–242 and the remainder as ranks 243–458. **Peer agreement and coordinator acceptance are pending; no peer derivative has been accessed.** This is an original-first research package, not accepted geographic dispatch or publication approval.

## Exact 242-code priority set

Order is significant; names, source positions, parents, candidate rows and counts are in the full table and contract.

`{minimum}`

## Primary authority and original publication scope

The [current RI.gov technical index](https://www.ri.gov/election/results/2024/general_election/data/) calls the downloads courtesy technical data supplied by the Board, disclaims suitability, and directs users to the Board website for official results. RI.gov's technical surface is not an independent Secretary-certified canvass. The [current Board previous-results page](https://elections.ri.gov/elections/previous-election-results) independently links the RI.gov historical pages, original summary PDFs and XLSX publications. The complete original response graph, requested/final URLs, UTC retrieval, headers, statuses, raw/stored hashes and literal anchors are retained in [source graph](data/turnout/source/source-graph.json) and [frozen original receipts](data/turnout/source/inputs/original-receipts.json). Earlier 403 responses and sandbox DNS failures survive alongside successful later requests; a failure is not a declaration that the public source does not exist.

The 2024 technical HTML/index prints **November 22, 2024 05:31 PM**. The Board summary prints **OFFICIAL RESULTS**, election November 5, 2024, and **12/03/2024 11:19AM**. The 2022 Board summary prints **OFFICIAL RESULTS**, November 8 election and **11/22/2022 12:14PM**; technical HTML prints November 22, 2022 02:54 PM. The Board's 2020 summary prints **Run Date 11/24/20 02:26 PM**, while its linked technical HTML labels official results updated November 30, 2020 12:49 PM. Those clocks have no stated timezone here. The [Board FAQ](https://elections.ri.gov/faq) distinguishes official/certified stages from preliminary totals. This package verifies the Board publication labels and numerical controls; it does not supply a separately signed certification instrument or establish an exhaustive later-amendment history. The current linked XLSX publication is a separate observation whose numeric agreement is tested, not a date inferred from its URL. [2022 Board summary](https://elections.ri.gov/sites/g/files/xkgbur756/files/2023-06/STATEWIDE%20SUMMARY.pdf), [2020 Board summary](https://elections.ri.gov/sites/g/files/xkgbur756/files/2022-02/statewidesummary2020gen.pdf).

Every member of all six technical ZIPs, including Mac metadata, is retained once in the original ZIP reference and inventoried with CRC/hash/size. Root short/long prefixes agree on **20,921 records (2024), 24,973 (2022), 16,573 (2020)**. Root, nested results and setup are nonadditive views. Selected root/nested differences affect **57 candidate/context rows and 114 numeric fields in 2024; 2,712 rows and 9,706 fields in 2022; 4,829 rows and 16,072 fields in 2020**. Setup fields are explicit zeros. Root is selected because it agrees exactly with Board controls and municipal HTML, not from filename or ZIP clock. No test designation, correction cause or chronology is inferred. [All view differences](data/turnout/extracts/archive-view-comparison.json), [ZIP inventory](data/turnout/source/zip-members.json), [all full long rows](data/turnout/extracts/all-long-rows.jsonl.gz).

## Candidate universe and whole-state reconciliation

The tables preserve source party and candidate strings, including party prefixes within names. Generic Write-in is a separate published bucket. No named entries are added to it. Each candidate's sum over all applicable native codes agrees exactly with its independent Board PDF control, Board XLSX total and first-three-method vector, and technical statewide HTML. Every municipality's candidate/method vector also agrees with its linked HTML. [Candidate reconciliation](data/turnout/candidate-reconciliation.json), [PDF positions](data/turnout/extracts/pdf-controls.json), [HTML positions](data/turnout/extracts/html-controls.json), [XLSX source cells](data/turnout/extracts/workbook-selected-rows.jsonl.gz).

| Year/contest | Native candidate code | Party, verbatim | Candidate, verbatim trimmed | Native sum = Board control | First / second / third method totals |
| --- | --- | --- | --- | ---: | --- |
'''
    for c in candidate:
        v=c['total_and_14_groups'];out+=f"| {c['year']} / {c['contest']} | {c['source_native_candidate']} | `{c['party']}` | {c['candidate_name'].strip()} | {v[0]:,} | {v[1]:,} / {v[2]:,} / {v[3]:,} |\n"
    out+='''
2024 Senate is **Whitehouse–Morgan, the other Class I seat**; 2020 Reed–Waters is the relevant same Class II seat. **2022 governor is the actual recent midterm comparator.** No 2022 Rhode Island Senate or 2024 governor contest is invented. Historical elections and candidate effects are separate. [2024 state summary](https://www.ri.gov/election/results/2024/general_election/), [2020 state summary](https://www.ri.gov/election/results/2020/general_election/), [2022 state summary](https://www.ri.gov/election/results/2022/general_election/).

The [Board's 2024 federal/state write-in workbook](https://elections.ri.gov/sites/g/files/xkgbur756/files/2025-04/Write%20In%20Report%20City%20Totals%20RQ.xlsx), linked from its [publications page](https://elections.ri.gov/elections/publications), has 39 municipal Senate headline totals summing **1,239**, exactly the technical municipal generic total. The four federal-admin generic buckets contribute another **5**, producing **1,244 statewide**. The workbook's literal detail cells sum **1,226**; nine municipal detail/headline differences are retained individually in [write-in scope comparison](data/turnout/extracts/writein-scope-comparison.json). Repeated spellings and `Blank`/`None` entries are not deduplicated or treated as valid named candidates. Details have no method or native precinct allocation. These differences remain unallocated. [All literal selected cells and formulas](data/turnout/extracts/2024-senate-writein-cells.json). The separately linked historical write-in PDFs are retained in full; 2020's Senate scan lacks a usable text layer and its first page is explicitly a state Senate in General Assembly District4 tally, not a U.S. Senate eligible-candidate roster. Generic eligibility and valid named write-in coverage remain unresolved, not a finish gate.

A **named printed candidates only arithmetic sensitivity** excludes every generic bucket: **490,704 statewide**, native top 15 **34,630 (7.0572076038%)**, minimum **242 contexts / 393,148 (80.1191757149%)**, preceded by **392,143**. Its own full order and membership are retained in `rankings.json` and the contract. This deliberately extreme alternative does not assert legal 80% membership robustness under unknown write-in eligibility.

## Native inventory and disjoint parents

Municipal parentage comes from each original city/town page's literal child links, independently acquired for all **39 municipalities in all three years**. It is not inferred from matching names or numeric ranges. [All 117 parent pages and complete child arrays](data/turnout/extracts/municipal-hierarchy.json). The [official Census 2020 county-subdivision table](https://tigerweb.geo.census.gov/tigerwebmain/Files/acs26/tigerweb_acs26_cousub_2020_tab20_ri.html) supplies municipal 10-digit GEOIDs and county context only; its nonmunicipal undefined-water entry is not an election geography. These historical identification labels do not approve current boundaries or a 2026 precinct crosswalk.

| Source scope | Municipal linked native contexts | Separate state-admin contexts | Senate/governor contexts | President contexts | Ballot contexts | Registration contexts |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2024 | 493 | 4 | 458 Senate | 497 | 497 | 483 |
| 2022 | 454 | 4 in statistics only | 454 governor | No presidential election | 458 | 442 |
| 2020 | 500 | 4 | 465 Senate | 504 | 504 | 504 |

In 2024, **39 presidential-only contexts are absent from Senate**, not zero Senate votes. The 458 actual Senate contexts include 15 source-published zero totals; these are different from unavailable rows. The [497-entry native inventory](data/turnout/native-inventory.json) is year scoped (the full file also contains the separate 2020 and 2022 inventories); each entry retains literal code/name, parent-link evidence, administrative/limited/presidential role, raw row keys, source fields and null availability. The complete primary dispatch inventory is repeated in the contract. Native keys and the source-position anchors are not assertions that equal labels across years refer to the same boundaries, split styles, scanners, sites, vote centers or VTDs.

**9001 Federal Precinct #1, 9002 Federal Precinct #2, 9011 Federal Precinct #1S and 9012 Federal Precinct #2S** have no municipal parent in the published hierarchy. They remain under the state, with no municipality, municipal FIPS or polygon allocation. Their 2024 Senate votes are **487, 526, 378, 82** (sum **1,473**). All are included in the canonical native denominator and order. Their published mail vector does not authorize a speculative municipal or physical join. The municipal-only Senate sum **490,475** plus these four entries closes **491,948**. [Root long ZIP](https://www.ri.gov/election/results/2024/general_election/data/rigen2024l.zip), [Board XLSX](https://elections.ri.gov/sites/g/files/xkgbur756/files/2025-01/Gen24EX%20%281%29.xlsx).

## Ballots, registration, blanks and method scope

| Year and scope | Candidate + generic votes | Under | Over | Contest ballot scope | State Election Ballots Cast | Registered Voters – Total | Election blank ballots |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2024 Senate | 491,948 | 15,770 | 143 | 507,861 published | 517,231 | 787,559 | 6,171 |
| 2024 president | 513,386 | 2,824 | 1,021 | 517,231 published | 517,231 | 787,559 | 6,171 |
| 2022 governor | 357,670 | 3,485 | 119 | 361,274, arithmetic sum of candidate/under/over | 361,449 | 815,417 | unavailable |
| 2020 Senate | 494,262 | 20,539 | 162 | 514,963, arithmetic sum of candidate/under/over | 521,185 | 808,953 | 3,342 |
| 2020 president | 517,757 | 2,217 | 1,211 | 521,185, arithmetic sum of candidate/under/over | 521,185 | 808,953 | 3,342 |

Sources: [2024 Board summary pp. 1–2](https://elections.ri.gov/sites/g/files/xkgbur756/files/2024-12/Gen24SummaryReport.pdf), [2022 Board summary pp. 1–2](https://elections.ri.gov/sites/g/files/xkgbur756/files/2023-06/STATEWIDE%20SUMMARY.pdf), [2020 Board summary p. 1](https://elections.ri.gov/sites/g/files/xkgbur756/files/2022-02/statewidesummary2020gen.pdf). All retained PDF numeric controls include page, line and original line text. The five contest identities above are separate; 2020 president is retained for source closure, not substituted for same-seat Senate.

The 2024 Senate under/over gap is **15,913 within its own 507,861 contest-ballot scope**. The remaining **9,370** between that scope and state election ballots equals the published ballot total in the 39 absent-Senate presidential contexts. The analogous 2020 difference is **6,222**, again exactly those 39 contexts' ballots. In 2022 the separate four federal administrative statistical contexts have **175 ballots**, exactly the difference between state ballots and the governor candidate/under/over sum; there are no governor rows for those contexts, so no governor zeros are fabricated. These are verified source coverage reconciliations, not residual allocations. [Native statistics and controls](data/turnout/native-inventory.json), [state controls](data/turnout/state-controls.json).

Election `Ballots Cast - Blank` is a separate source statistic, not another candidate or a field to add to contest under/over totals. Municipal/native contest under/over and contest-ballot fields are unavailable in the acquired candidate exports and remain null; no statewide total is allocated downward. Ballot and registration row universes differ: in 2024, 14 native contexts lack registration rows; in 2022, 16 do. Explicit administrative registration zeroes are preserved. Registration totals sum over available rows and reconcile exactly to the Board summary, but active/inactive status and exact registration extract date are not specified beyond the election/publication scope. The published rounded statewide ballot/registration rates are 65.68% (2024), 44.33% (2022) and 64.43% (2020); none is a voting-eligible-population rate. No missing registration is filled with zero. [Board XLSX 2024](https://elections.ri.gov/sites/g/files/xkgbur756/files/2025-01/Gen24EX%20%281%29.xlsx), [2022](https://elections.ri.gov/sites/g/files/xkgbur756/files/2023-06/RIGEN22%20%282%29.xlsx), [2020](https://elections.ri.gov/sites/g/files/xkgbur756/files/2022-02/rigen20.xlsx).

All 14 method slots are preserved per raw candidate row. The 2022 description labels groups 1–3 Election Day / Mail Ballots / Early Voting; the same linked description is used by the 2024 technical index. The 2020 index links the 2016 description, whose third slot is **unlabelled**; 2020 HTML calls the matching vector **Emergency ballots**, and its XLSX says **Emergency**. Groups 4–14 remain unlabelled even where their reported values are zero. Source labels are retained separately rather than mapped to a current method by position. Registration's method zeroes do not define registration by voting method. [2022/2024 format](https://www.ri.gov/election/results/20220819_data_description.pdf), [2020-linked format](https://www.ri.gov/election/results/20160902_data_description.pdf), [method scope metadata](data/turnout/source/method-scopes.json).

The 2024 official PDF's **414 of 458 Senate** and **453 of 497 president** reporting flags do not mean percentages of votes completed or exact outstanding pools. The technical pages warn that a precinct with several scanners can show 100% reported after one scanner. This package establishes no current November feed, collection implementation, live cadence, feed exhaustion, exact remaining votes, probability calibration or approved current geometry. Historical five-minute technical-page language is not a 2026 contract. [Board summary](https://elections.ri.gov/sites/g/files/xkgbur756/files/2024-12/Gen24SummaryReport.pdf), [technical Senate page](https://www.ri.gov/election/results/2024/general_election/races/2.html).

## Separate native sensitivity orders

Each row independently ranks its own original reporting universe. These are historical volume/denominator sensitivities, not cross-year native identity joins. Registration covers its published rows only; the 497-ballot sensitivity includes the 39 unavailable Senate contexts.

| Ranking basis | Reporting contexts | State volume | Top 15 votes/records | Top 15 % | Minimum 80% count | Preceding votes | Crossing cumulative |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
'''
    for key,label in [('native_senate2024','2024 Senate reported candidate + generic'),('native_senate2024_named_only','2024 Senate printed candidates only'),('native_president2024','2024 president candidate + generic'),('native_governor2022','2022 governor candidate + generic'),('native_senate2020','2020 same-seat Senate candidate + generic'),('native_ballots2024','2024 election ballots'),('native_registration2024','2024 registration records')]:
        x=ranks[key];out+=f"| {label} | {len(x['order'])} | {x['total']:,} | {x['top15_votes']:,} | {x['top15_pct']:.8f} | {x['minimum80_count']} | {x['preceding_votes']:,} | {x['minimum80_votes']:,} |\n"
    out+=f'''
All full sensitivity orders, crossings and remainders are in [rankings.json](data/turnout/rankings.json), calculated from the primary originals cited above. The primary 242-context set is not replaced by any sensitivity.

## Municipality and administrative parent sensitivity only

The 43 disjoint parent entries retain all 39 municipalities and the four separate state-admin entries, with full child arrays and FIPS evidence in [parent sensitivity](data/turnout/parent-sensitivity.json) and [43-row CSV](data/turnout/parent-sensitivity.csv). They are **not canonical native dispatch**.

Parent top 15 contribute **333,390 / 491,948 = {parent['top15_pct']:.10f}%**. The minimum parent set is **21 municipalities / 395,379 = {parent['minimum80_pct']:.10f}%**, preceded by **20 / 386,501 = {parent['preceding_pct']:.10f}%**, crossing at Tiverton; parent remainder **96,569**. Exact parent order through crossing: **{pnames}**. Native prioritization may select contexts in municipalities outside this parent set.

The actual **2022 governor** comparator totals **357,670**. Its parent top 15 contribute **239,262 (66.89462354%)**. The parent minimum is **22 / 292,789 (81.86009450%)**, versus **21 / 286,002 (79.96253530%)**, crossing at East Greenwich. Native governor priority instead needs 231 contexts; these are different geographic questions. All four federal-admin governor cells remain unavailable while their published election ballots survive. [Original governor HTML](https://www.ri.gov/election/results/2022/general_election/), [Board summary](https://elections.ri.gov/sites/g/files/xkgbur756/files/2023-06/STATEWIDE%20SUMMARY.pdf).

| Parent rank | Municipality or state-admin entry | 2024 Senate | Cumulative | 2020 Senate | 2022 governor | 2024 president | 2024 election ballots | 2024 registration |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
'''
    for x in parent['order']:
        key=x['key'];m={yr:next(m for m in ms if m['year']==yr and m['key']==key)for yr in ['2024','2020','2022']}
        g=m['2022']['contests']['Governor'];out+=f"| {x['rank']} | {x['name']} | {x['votes']:,} | {x['cumulative_votes']:,} | {m['2020']['contests']['Senator in Congress']['total']:,} | {'unavailable'if g is None else format(g['total'],',')} | {m['2024']['contests']['Presidential Electors For:']['total']:,} | {m['2024']['statistics']['BALLOTS CAST - TOTAL']['values'][0]:,} | {m['2024']['statistics']['REGISTERED VOTERS - TOTAL']['values'][0]:,} |\n"
    out+='''
## Complete canonical 458-native order

Source: root [2024 long ZIP](https://www.ri.gov/election/results/2024/general_election/data/rigen2024l.zip), every candidate/method row independently reconciled to [Board XLSX](https://elections.ri.gov/sites/g/files/xkgbur756/files/2025-01/Gen24EX%20%281%29.xlsx) and [Board summary](https://elections.ri.gov/sites/g/files/xkgbur756/files/2024-12/Gen24SummaryReport.pdf). Native source code/name and source-position keys are separate; byte offsets and all raw fields are in the CSV/contract. `P` denotes ranks 1–242; `R` denotes the full remainder. Source-published zeroes remain in order. All contexts retain their municipal parent or explicit state-admin role in the contract.

| Rank | Native code | Source name | Votes | State % | Cumulative votes | Cumulative % | Set |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
'''
    for x in r['order']:out+=f"| {x['rank']} | `{x['native_code']}` | {x['name']} | {x['votes']:,} | {x['share_pct']:.6f} | {x['cumulative_votes']:,} | {x['cumulative_pct']:.6f} | {'P'if x['rank']<=242 else 'R'} |\n"
    out+='''
## Reproduction, offline QA and review status

Run `python3 -B senate/2026/rhode-island/data/turnout/rebuild.py` from the repository root to reproduce acquisition-independent extracts, reconciliation, CSV and report. Then run `python3 -B senate/2026/rhode-island/data/turnout/validate_turnout.py` for read-only verification. No network, mutable shared-manifest selection, peer-directory glob, dependency install or cache is required. Python standard library and Poppler `pdftotext` are used. Original raw ZIP/PDF objects are reused once through exact-hash references; the full unused content remains available without extracting an unrelated-office assignment. See [schema](data/turnout/source/SCHEMA.md).

[Validation](data/turnout/validation.json) records full primary state/candidate/method/native/parent closure, source positions, null/administrative coverage, native ordering and integer minimum crossing, and intentional corruption cases. [Repair history](data/turnout/history/repair-history.json) records the initial PDF decimal parsing failure and the steering that separated parent sensitivity from native dispatch. [Original-first body witness](data/turnout/qa/pre-peer-body-witness.json) freezes exact full bodies (including report/scripts/CSV/full source objects by immutable references), with byte-exact reconstruction. [Final seal](data/turnout/final-seal.json) precedes the [complete owned asset manifest](data/turnout/asset-manifest.json); the manifest excludes only itself. A final read-only audit follows sealing. No reverse current-manifest pin or digest cycle is used.

**Pending external review:** actual peer `5d9f9b63-0cf2-4b55-b52b-579cbc1d76d1` has launched. Independent peer agreement is unperformed; no peer derivative has been accessed. Coordinator acceptance/publication remain pending. This bounded original-first worker turn ends after offline QA and immutable witness completion. Legal write-in eligibility, exhaustive later certification/amendment history, current native identities/geometry, November feed availability/cadence and remaining-vote/probability claims remain qualified as described above.
'''
    (STATE/'turnout.md').write_text(out)
if __name__=='__main__':run()
