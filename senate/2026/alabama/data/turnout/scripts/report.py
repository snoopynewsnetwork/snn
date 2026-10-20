#!/usr/bin/env python3
"""Reproducible human report from original-first calculations; no peer inputs."""
import pathlib,json,csv,io,collections
from fractions import Fraction
from freeze import write
R=pathlib.Path(__file__).resolve().parents[1];S=R.parents[1]
def j(p):return json.loads((R/p).read_text())
def fmt(n):return f'{n:,}'
def pct(a,b):return f'{100*a/b:.10f}%'
summary=j('native-rank-summary.json');countys=j('county-rank-sensitivity.json');us={y:j(f'native-units-{y}.json') for y in [2024,2022,2020]};control=j('statewide-controls.json');bc=j('ballot-registration-controls.json');disc=j('source-discrepancies.json');fa=j('field-audit.json');ballot={r['year']:r for r in bc['statewide']};rows=list(csv.DictReader((S/'data/county-turnout.csv').open()));c24=[r for r in rows if r['year']=='2024'];byf={r['county_fips']:r['county'] for r in c24}
urls={r['id']:r['url'] for r in j('source/original-receipts.json')}
http=[json.loads(p.read_text()) for p in (R/'source/http').glob('*.receipt.json')]
def url(prefix):return next(r['requested_url'] for r in http if r['original_sha256'].startswith(prefix))
zipurl={2024:url('4ecca55'),2022:url('4ea186'),2020:url('471fc54')};s=summary['2024'];priority=us[2024][:s['minimum80_count']];remainder=us[2024][s['minimum80_count']:]
for name,rs in [('priority-native-2024.csv',priority),('remainder-native-2024.csv',remainder)]:
 b=io.StringIO();f=csv.DictWriter(b,fieldnames=['rank','key','county_fips','county','native_label','method_context','reported_candidate_votes','cumulative_votes','source_member','column_1based']);f.writeheader();f.writerows({k:u[k] for k in f.fieldnames} for u in rs);write(R/name,b.getvalue())
text=f'''# Alabama reported vote volume

Observed 2026-10-20 UTC. **Complete historical native reporting coverage is recovered: 2,085 labeled 2024 columns across all 67 counties.** The priority denominator is **2,265,090 reported 2024 presidential candidate and generic write-in votes**, independently extracted from the [official statewide precinct archive]({zipurl[2024]}) and reconciled for every county/candidate to the [certified November 26 canvass, PDF pages 5–6]({urls['sos-2024-canvass-original']}). Alabama had no 2024 U.S. Senate election. These columns are the native historical reporting geography, including absentee and provisional contexts, rather than 2,085 approved physical precinct polygons.

**Top 15: 115,428 / 2,265,090 = {pct(115428,2265090)}. Minimum descending 80% set: 887 units, 1,812,818 / 2,265,090 = {pct(1812818,2265090)}.** The preceding 886 units have 1,811,981 votes ({pct(1811981,2265090)}). Calhoun’s **OAK GROVE BAPT**, source column 30, adds 837 and crosses the threshold. The remaining **1,198 units / 452,272 votes** remain in statewide arithmetic. No crossing tie occurs. Full [descending order](data/turnout/native-order-2024.csv), [ordered 887-unit set](data/turnout/priority-native-2024.csv), [ordered remainder](data/turnout/remainder-native-2024.csv) and [exact dispatch contract](data/turnout/priority-set.json) retain every literal label, parent FIPS and source column. All these calculations use the [original precinct archive]({zipurl[2024]}).

The contract is a measured **historical** priority. **Independent peer agreement and coordinator acceptance remain false/pending** because no Alabama partisanship peer existed at launch. No dispatch acceptance, November 2026 geographic approval or cross-year unit equivalence is claimed. The compatibility file [county-turnout.csv](data/county-turnout.csv) contains the separate 67-county parent sensitivity for three elections; it never substitutes county totals for native reporting columns.

## Exact top 15 native contexts

| Rank | County | Literal native reporting label | Candidate/write-in votes |
| ---: | --- | --- | ---: |
'''
for u in us[2024][:15]:text+=f"| {u['rank']} | {u['county']} | {u['native_label']} | {fmt(u['reported_candidate_votes'])} |\n"
text+=f'''
Source: [official 2024 precinct workbooks]({zipurl[2024]}), `Precinct Results` sheet, each candidate row and the header column pinned in [native-units-2024.json](data/turnout/native-units-2024.json). The largest context is Madison ABSENTEE, 15,691 candidate votes; its separate source ballot field is 15,310, demonstrating why the two measures cannot be interchanged.

## Integer threshold, hierarchy and candidate universe

Sort by reported candidate/write-in votes descending, then the complete source-scoped key ascending for reproducible ties. The smallest k satisfies `5 × cumulative(k) >= 4 × statewide_votes`. Here `5 × 1,811,981 = 9,059,905 < 9,060,360 = 4 × 2,265,090 <= 9,064,090 = 5 × 1,812,818`. Since the largest 886 units cannot reach 80%, no smaller set can. Exact rational weights and cumulative fractions are retained without rounded-threshold decisions. [Source archive]({zipurl[2024]}); [calculation](data/turnout/scripts/build.py).

The disjoint arithmetic layer is the set of labeled columns within each county workbook. County and statewide controls are overlapping parents and are never added to their constituents. In 2024 there are 1,947 ordinary precinct/site reporting columns, 68 absentee columns, 67 provisional columns and 3 combined provisional/absentee columns. Classification uses explicit method words, including the literal misspelling `PROVSIONAL`; a church or school named “Central” is not a central-counting method. Ordinary columns have **unspecified method**, not proven Election Day exclusivity. Native column labels can represent combined precincts (for example Jefferson `PREC 1065/4060 - CENTER POINT`), sites, split names or administrative contexts. We do not merge them by similar names. [All original headers]({zipurl[2024]}); [complete typed extracts](data/turnout/source/workbooks-2024.json.gz); [coverage](data/turnout/native-coverage.json).

Keys preserve election, county FIPS, original 1-based source column and percent-encoded literal header. The source has no separate statewide numeric precinct-ID field; `native_id` therefore retains the source header, with standalone numeric ID null. County FIPS is verified against the [Census reference]({url('9f6e5f')}); it does not validate precinct geography. All 67 parents have complete constituent arrays, explicit administrative geometry cases and unavailable current-ID/write-in-detail cases in the contract. The 887-unit set touches {len(set(u['county'] for u in priority))} counties; {', '.join(sorted(set(u['county'] for u in remainder)-set(u['county'] for u in priority)))} have no priority unit but every one of their units remains in the order and denominator.

| Contest and source status | Published candidate / ballot identity | Native statewide votes | Canvass control |
| --- | --- | ---: | ---: |
'''
parties={2024:['D / DEM','R / REP','I / IND','I / IND','I / IND','generic Write-In / NON'],2022:['D / DEM','R / REP','L / LIB','generic Write-In / NON'],2020:['D / DEM','R / REP','generic Write-In / NON']}
for y in [2024,2022,2020]:
 for (n,v),party in zip(control[str(y)].items(),parties[y]):text+=f'| {y} {"President" if y==2024 else "U.S. Senate"} | {n} ({party}) | {fmt(v)} | {fmt(v)} |\n'
text+=f'''
Sources: [2024 canvass PDF 5–6]({urls['sos-2024-canvass-original']}), [2022 canvass PDF 4–5]({urls['sos-2022-canvass-original']}), [2020 canvass PDF 3–4]({urls['sos-2020-canvass-original']}); independently extracted [2024]({zipurl[2024]}), [2022]({zipurl[2022]}) and [2020]({zipurl[2020]}) native archives. The 2022 Senate is the actual **Class III midterm/other seat**, Boyd–Britt–Sophocleus. The 2020 Jones–Tuberville Senate is the previous **Class II** election. No nonexistent 2024 Senate or governor contest is introduced. Each native candidate’s raw padded name, party, contest string and source row is preserved in [candidate-universe.json](data/turnout/candidate-universe.json). The canonical name used for comparison is an explicit whitespace-trimmed presentation value; no source candidate rows are deduplicated. “NON” is the archive label on a generic Write-In row, not a named independent candidate or proof of eligible/valid write-in adjudication.

Every native candidate sum matches every **numeric** county canvass cell, and all candidate statewide sums match printed totals. Three PDF exceptions stay source-scoped: Wilcox 2024 Stein is blank; Washington 2022 Senate Write-In is blank; Perry 2020 Senate Write-In is a printed dash. They remain null in [canvass-cells.json](data/turnout/canvass-cells.json). Independently downloaded native XLS cells for these scopes are explicit numeric zeros, so native candidate coverage closes without assigning a residual or modifying any PDF null. Legal named/valid write-in allocation remains unavailable. [Candidate reconciliation](data/turnout/candidate-reconciliation.json); [full page visual transcriptions](data/turnout/source/visual-transcriptions.json).

The damaged 2024 embedded OCR was not silently repaired: Hale’s six cells (3,868 / 3,369 / 30 / 10 / 13 / 15) and Winston’s (884 / 10,191 / 36 / 8 / 10 / 20) were read on the complete original page renders. Henry 2022’s numeric row is mistakenly separated under `Total` by text extraction; the printed row is Henry. Exact OCR aliases and raw lines survive alongside explicit joins, character positions and page numbers. Adjacent 2022 Lieutenant Governor and 2020 presidential columns are not added to Senate. All unrelated original PDF pages and XLS rows remain available without a second analytical model of unrelated offices. [Unaltered extraction and warnings](data/turnout/source/SCHEMA.md); [visual evidence](data/turnout/source/visual-transcriptions.json).

## Actual midterm and same-seat comparators

| Native reporting scope | Units | Candidate votes | Top 15 votes / share | Minimum 80% units / votes | Preceding units / votes | Crossing unit | Remainder votes |
| --- | ---: | ---: | --- | --- | --- | --- | ---: |
'''
for y in [2024,2022,2020]:
 t=summary[str(y)];text+=f"| {y} {'President' if y==2024 else 'Senate'} | {t['unit_count']} | {fmt(t['denominator'])} | {fmt(t['top15_votes'])} / {pct(t['top15_votes'],t['denominator'])} | {t['minimum80_count']} / {fmt(t['minimum80_votes'])} | {t['preceding_count']} / {fmt(t['preceding_votes'])} | {t['crossing_county']}: {t['crossing_label']} ({fmt(t['crossing_votes'])}) | {fmt(t['remainder_votes'])} |\n"
text+=f'''
The comparator orders, exact fractions, full priority and remainder arrays are retained in [native-rank-summary.json](data/turnout/native-rank-summary.json), with complete [2022 order](data/turnout/native-order-2022.csv) and [2020 order](data/turnout/native-order-2020.csv). These are independent election-vintage universes: 2,074 and 2,111 units. The different counts and matching labels establish no crosswalk. Sources: [2022 native archive]({zipurl[2022]}), [2020 native archive]({zipurl[2020]}).

## Ballots, registration and method sensitivity

Candidate votes are not ballots cast. Published blank-ballot, contest undervote and overvote fields remain separate and are never inserted into the candidate denominator. Absentee is a method/context or a report statistic, not extra votes to add to county totals. The source’s Democratic/Republican ballot statistics are preserved with their original headers; 2020/2022 explicitly label straight-party ballots, while the 2024 report says Democrat Ballots / Republican Ballots. They are not candidate totals or party registration.

| Election | Official county ballot-report total | Native ballot-field sum | Report registered voters | Report absentee ballots | Raw native registration sum |
| --- | ---: | ---: | ---: | ---: | ---: |
'''
for y in [2024,2022,2020]:
 b=ballot[y];d=disc['statewide_native'][str(y)];text+=f"| {y} | {fmt(b['ballots_cast'])} | {fmt(d['ballots_cast_known_sum'])} | {fmt(b['registered_voters'])} | {fmt(b['absentee_ballots'])} | {fmt(d['registration_known_sum'])} |\n"
text+=f'''
Sources: current linked [2024 Official Total Ballots Cast]({url('f1cfb4')}), [2022 Official Total Ballots Cast]({url('823fe8')}), retained [2020 Total Ballots Cast report]({urls['sos-2020-ballots-original']}) and the separate original native archives. Each report’s 67 county sums closes its own statewide footer for all five integer columns. “Registered Voters” is the printed denominator; these reports do not specify active/inactive composition, a registration extract clock, or voting-eligible population. Election date is not an invented registration-as-of timestamp. Report turnout percentages are retained as printed and recomputed from integer totals only for that scope. All 204 county/footer turnout and absentee percentage pairs agree at their displayed precision; [turnout-rates.json](data/turnout/turnout-rates.json) retains exact rational rates and the rounding check.

**Unrepaired source discrepancies:** 2024 Cleburne native ballot sum is 180 below its report; 2022 Cullman native sum is 90 above its report. The 2024 native sum is 2,272,731 versus report 2,272,911; 2022 is 1,423,499 versus 1,423,409. All other county ballot-report comparisons close, including all 67 in 2020. Candidate sums close independently in each election. We do not allocate these discrepancies to candidates, provisional ballots, rejected ballots or a particular unit. Published fields can also fail within-unit identities: {fa['2024']['candidate_above_ballots_unit_count']} native units in 2024 have more candidate votes than their ballot-field value. These are retained source discrepancies, not evidence of a particular cause. [Full county differences](data/turnout/source-discrepancies.json); [every unit arithmetic exception](data/turnout/field-audit.json).

The raw registration fields sum to substantially less than the report totals. Many counties publish zeros throughout their native registration rows; 2024 Madison PROVISIONAL ABSENTEE has a blank registration cell, as do Hale, Henry and Macon PROVISIONAL in 2022. Missing stays null and printed zero stays zero. A 2020 numeric native registration ranking is retained only as a **raw-field sensitivity**, not a complete statewide registration geography. A certified native registration-based priority cannot be established from these fields.

| Source-scoped field | 2024 | 2022 | 2020 |
| --- | --- | --- | --- |
'''
for field in ['blank_ballots_source','under_votes_source','over_votes_source']:
 vals=[]
 for y in [2024,2022,2020]:
  d=fa[str(y)]['field_coverage'][field];vals.append(f"{fmt(d['known_sum'])} known sum; {d['unknown_cells']} unknown cells")
 text+='| '+field+' | '+' | '.join(vals)+' |\n'
text+=f'''
Walker’s 2024 presidential under/over rows are unavailable for all 47 source units; 2022 Senate under/over rows are unavailable in Butler (23), Dale (20), Tuscaloosa (56). Randolph’s 2020 blank-ballot row is unavailable for 28 units. Unknown rows do not become zeros. Method/context totals and constituent keys for all counties and years are in [field-audit.json](data/turnout/field-audit.json), directly derived from the [2024]({zipurl[2024]}), [2022]({zipurl[2022]}) and [2020]({zipurl[2020]}) original fields.

| Sensitivity denominator | Total | Top-15 share | Minimum 80% count | Crossing cumulative / preceding cumulative |
| --- | ---: | ---: | ---: | --- |
'''
for label,file,match in [('Native ballot fields','native-ballot-registration-sensitivity.json','ballots_cast_source'),('County ballot report','ballot-registration-sensitivity.json','ballots_cast_report'),('County registered voters report','ballot-registration-sensitivity.json','registered_voters_report')]:
 dat=j(file)
 for y in [2024,2022,2020]:
  t=dat[f'{y}_{match}']['summary'];text+=f"| {y} {label} | {fmt(t['denominator'])} | {pct(t['top15_votes'],t['denominator'])} | {t['minimum80_count']} | {fmt(t['minimum80_votes'])} / {fmt(t['preceding_votes'])} |\n"
text+='''
Full field orders, crossing keys, exact fractions and remainders are in [native ballot sensitivity](data/turnout/native-ballot-registration-sensitivity.json) and [county ballot/registration/absentee sensitivity](data/turnout/ballot-registration-sensitivity.json). These compare source-scoped volume mixes; they are not 2026 forecasts. Native ballot minima use raw native fields and inherit their discrepancies. County registration sensitivity uses each report’s stated registered-voter denominator, not the incomplete native fields. The same official ballot reports and archives cited above supply these calculations.

## All 67 county parents, separate sensitivity

'''
t=countys['2024'];text+=f'''At county aggregation only, the 2024 top 15 contribute **1,489,790 / 2,265,090 = {pct(1489790,2265090)}**. The smallest county set has **25 counties / 1,814,804 votes = {pct(1814804,2265090)}**; the preceding 24 have 1,791,248 and Jackson adds 23,556. These are the overlapping parent controls of the [native archive]({zipurl[2024]}) reconciled to the [canvass]({urls['sos-2024-canvass-original']}), not the native dispatch set.

Ordered 25-county sensitivity: {', '.join(byf[k.split(':')[-1]] for k in t['priority_keys'])}. All 42 remainder counties supply 450,286 votes. The 2022 county minimum is 27 (1,144,634 / 1,414,238); 2020 is 26 (1,868,545 / 2,316,445). Complete county orders and remainders are retained in [county-rank-sensitivity.json](data/turnout/county-rank-sensitivity.json); source rows and all separate ballot/registration fields are in the [201-row county CSV](data/county-turnout.csv).

| 2024 county rank | FIPS | County | 2024 president votes | Native contexts | 2024 report ballots | 2024 report registration |
| ---: | --- | --- | ---: | ---: | ---: | ---: |
'''
for r in c24:text+=f"| {r['rank_candidate_volume']} | {r['county_fips']} | {r['county']} | {fmt(int(r['candidate_votes']))} | {r['native_unit_count']} | {fmt(int(r['ballots_cast_report']))} | {fmt(int(r['registered_voters_report']))} |\n"
text+=f'''
Sources for every row: [2024 original archive]({zipurl[2024]}), [2024 certified canvass]({urls['sos-2024-canvass-original']}), [official ballot report]({url('f1cfb4')}), [Census county FIPS]({url('9f6e5f')}). No population/VTD/name-based allocation was used.

## Current context and bounded qualifications

The current [2026 SOS authority page](https://www.sos.alabama.gov/alabama-votes/voter/election-information/2026) was downloaded in full on October 20. Its signed August 26 [Democratic state certification]({url('dbb854')}) (PDF 3) lists Everett Wess for U.S. Senate; the [Republican state certification]({url('a3a109')}) (PDF 2) lists Barry Moore. The complete one-page [independent certification]({url('707afb')}) has state legislative entries and no U.S. Senate entry. The linked [Autauga common sample]({url('4f1a69')}) visibly displays Everett Wess (Democrat), Barry Moore (Republican), and a separate Write-in line for November 3. These are dated bounded observations; one sample and the retained certifications do not exhaust later amendments, legal eligibility, write-in adjudication or all county ballot styles. They do not change the historical ranking universe. Images and page regions are pinned in [visual-transcriptions.json](data/turnout/source/visual-transcriptions.json).

The linked [2026 Voter Guide]({url('5c280')}) gives 7 a.m.–7 p.m. polling hours with Eastern-time qualification (PDF 7), separates provisional procedures (PDF 9–10), and gives general absentee application/delivery deadlines with a UOCAVA exception (PDF 3 and later absentee sections). These are method/eligibility context, not a current count of accepted ballots. The guide’s general-election description permits straight-party or individual candidate marking (PDF 11). This assignment has not exhausted later law/dockets, approved November native IDs/geometry, November vote counts, publication cadence, exact outstanding votes or probability calibration. No live collector or calibrated Needle is implemented or claimed.

## Reproduction, original bytes and QA

The [original-first witness](data/turnout/source/original-first-witness.json) pins every complete original body and all 201 ZIP-member hashes, before any peer derivative. Original retained canvasses are reused read-only by individual immutable hash and receipt; the 46,116,016-byte 2024 PDF reconstructs losslessly from its single 29,769,765-byte shared gzip. Every stored artifact is strictly below 40,000,000 bytes. Requested/final URLs, UTC retrieval, status, headers and redirects are retained for fresh downloads; [download-chains.json](data/turnout/source/download-chains.json) pins each actual authority hyperlink with original parent hash and HTML position; ZIP member names, sizes, CRCs and source timestamps are pinned. Existing shared receipt limitations and the failed Census API / successful direct Census recovery remain explicit in [acquisition qualifications](data/turnout/source/acquisition-qualifications.json). No protected data or private-cell reconstruction is used.

Run the offline sequence in [SCHEMA.md](data/turnout/source/SCHEMA.md). [validation.json](data/turnout/validation.json) records comparison of 6,246,656 raw cells and 85,129 target candidate/method/administrative cells against all 201 original XLS members, plus identity checks, primary statewide/county candidate reconciliation, disjoint coverage, exact rank/threshold proofs, source and asset hashes, missing-field semantics and link/bounds checks. [final-seal.json](data/turnout/final-seal.json) records the bounded completion state; [asset-manifest.json](data/turnout/asset-manifest.json) inventories every owned artifact except itself, including scripts, histories, receipts, report, validation and seal. It also pins shared originals separately. Manifest is written last; a read-only membership/hash/size audit follows. The manifest is not hashed back into validation or seal.

**Research/offline QA is complete within the recovered historical scope. Actual independent peer agreement and coordinator acceptance remain pending, separately and explicitly.** Future geographic/legal/live-count qualifications do not justify inventing missing data or holding this worker open indefinitely.
'''
write(S/'turnout.md',text)
print('report bytes',len(text.encode()))
