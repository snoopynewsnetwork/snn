#!/usr/bin/env python3
"""Generate the owned research report from exact offline arithmetic."""
import json
import pathlib
import sys
sys.dont_write_bytecode = True
from extract import ROOT


def main():
    q=json.loads((ROOT/'priority-set.json').read_text())
    aa=json.loads((ROOT/'reconciliation.json').read_text());a={x['source_id']:x for x in aa}
    ss=json.loads((ROOT/'sensitivity.json').read_text())
    peer=json.loads((ROOT/'peer-agreement.json').read_text())
    acceptance_path=ROOT.parent/'coordinator-priority-acceptance.json'
    acceptance=json.loads(acceptance_path.read_text())if acceptance_path.exists()else None
    acceptance_text=(f"**Historical dispatch formally accepted at {acceptance['accepted_at_utc']}** in the [coordinator-owned acceptance record](data/coordinator-priority-acceptance.json). Its scope is historical research dispatch only. Current geometry, clerk authority, live feeds, valid/named write-in allocation and calibrated models remain unapproved."if acceptance and acceptance.get('accepted')else 'Historical acceptance remains pending in the coordinator-owned external record.')
    shared={r['id']:r for r in json.loads((ROOT/'source/shared-originals.json').read_text())}
    def url(sid):
        return shared[sid]['url']if sid in shared else json.loads((ROOT/'source'/f'{sid}.json').read_text())['requested_url']
    def cite(sid,title):return f'[{title}]({url(sid)})'
    p=q['basis_source_id'];s22='sos-archived-2022-ge-us-senator-5-xls';s20='sos-2020-senate-archived-original'
    b24='2024-ge-ballots-cast-14-xls';b22='2022-ge-ballots-cast-3-xls';b20='2020-ge-ballots-cast-xls'
    c24='2024-ge-names-on-checklist-7-xlsx';c22='2022-ge-names-on-checklist-2-xlsx';c20='2020-ge-names-on-checklist-xlsx'
    lines=[f'''# New Hampshire turnout volume: towns, city wards and retained administrative labels

Research observed 2026-10-18 UTC. **Priority basis: November 5, 2024 president, four printed tickets plus the source's generic Write-Ins.** The complete original contains 320 native labels. This report ranks their reported numeric candidate/write-in subtotals, not ballots cast or participation rates. No county summary or city parent is added to its component rows. Primary basis: {cite(p,'SOS original `_3` workbook, archived 2024-12-19')}; [independent extraction and controls](data/turnout/reconciliation.json).

**Top 15:** {', '.join(r['display_label'] for r in q['all_units'][:15])}. Their exact share is **185,659 / 826,189 = 22.4717346757219%**.

**Minimum descending set reaching 80%: the first 143 native rows in the complete order below.** They contribute **662,624 / 826,189 = 80.2024718315059%**. The first **142** contribute **660,378 / 826,189 = {100*660378/826189:.12f}%**. **Tilton, 2,246 votes, crosses at rank 143.** The integer threshold is 660,952: `5 * 660378 < 4 * 826189 <= 5 * 662624`. Since the largest 142 rows fall short, no set of 142 rows can reach 80%. The remaining **177 labels supply 163,565 votes ({100*163565/826189:.12f}%)** and remain in every state total. Top 15 is contained within the 143-row priority. [Exact ordered dispatch contract](data/turnout/priority-set.json); [all 320 rows](data/county-turnout.csv).

## Correct election and seat context

The Senate identifies Shaheen's seat as Class II, elected in November 2020 for the term ending January 2027; Hassan's Class III seat was elected in November 2022. Thus 2020 Shaheen–Messner–O'Donnell is the same-seat baseline, and 2022 Hassan–Bolduc–Kauffman is the actual recent midterm comparator. New Hampshire had no 2024 Senate election; its 2024 official index lists president and governor, and its House Clerk federal table has president and House contests. The current SOS calendar gives September 8, 2026 primary and November 3, 2026 general. Sources: [Senate Class II](https://www.senate.gov/senators/Class_II.htm), [Class III](https://www.senate.gov/senators/Class_III.htm), [SOS 2026 calendar](https://www.sos.nh.gov/elections/2026-2027-political-calendar), {cite('archived-2024-results-index','actual official 2024 index, archived September 2026')}, {cite('house-clerk-2024','House Clerk 2024')}. Fresh direct SOS index/calendar requests returned 403; current indexed official text was inspected, and original archived publications were recovered separately. No 2024 Senate figures or 2022 presidential figures are fabricated.

## Disjoint accounting and native identity

The selected workbook supplies **73 explicitly labeled city-ward rows**, **Berlin as one city row**, and **246 other town/territory labels**. It has 12 distinct explicitly named warded city parents. County summaries and ten county footers are controls, not extra reporting leaves. Berlin is not expanded into guessed wards; Derry is not split into invented districts. Polling sites, ballot styles, VTDs, absentee counting groups and 2026 precinct geometry are not supplied by this source. [Native hierarchy and source locators](data/turnout/geography.json); {cite(p,'original workbook')}.

`county-turnout.csv` is a compatibility filename: each of its 320 rows is a native accounting leaf, not one of ten county aggregates. `geography_key` is a project key made from the 2024 contest, verified county FIPS and percent-encoded, whitespace-trimmed literal label. It is **not a source-native numeric ID**. The original supplies labels, sheet names and row positions, not numeric precinct IDs; these positions and literal labels survive separately. Ward numbers are always qualified by their explicit city parent. The contract inventories every available native row in all retained result/administrative vintages, including blank/dash cases and unavailable finer constituents.

County FIPS are verified against {cite('census-nh-cousub-codes','the Census 2020 official subdivision code list')}. Exact county-scoped town/city/township name matches provide parent Census GEOIDs for 302 native rows. **18 administrative/abbreviated labels remain without a parent GEOID**; no name-similarity crosswalk is guessed. A Census parent identifier is not a ward FIPS, approved precinct boundary, election authority, or proof of cross-year geometry. All 18 stay in the accounting and dispatch roster. Actual clerk channels must be established from actual official publications; a county or town name alone conveys no clerk authority.

There are **20 rows with at least one unpopulated candidate field**; **16 have all four printed-ticket fields blank and generic Write-Ins numerically 0**. Their reported numeric subtotal is 0, but their candidate cells are null/blank, not invented zeros. Four other partly populated candidate rows are Springfield (Oliver and Stein blank), Milan (Stein blank), Waterville Valley (Stein blank), and Millsfield (Oliver and Stein blank). Three additional rows have only missing under/over fields: Manchester Ward 7, Wentworth and Monroe. All seven statewide numeric columns reconcile despite those literals. No unexplained candidate residual is distributed. The bottom-of-order tie rule is county FIPS then trimmed literal label. {cite(p,'Original BIFF source')}; [explicit missing-cell audit](data/turnout/reconciliation.json).

## Candidate universe and whole-state primary reconciliation

The source's printed tickets are Harris/Walz (Democratic), Trump/Vance (Republican), Oliver/ter Maat (Libertarian), and Stein/Ware (Green). It reports one generic `Write-Ins` column, not a named or legally validated write-in allocation. Those five categories are the complete reported priority universe. Generic write-ins must not be added again as named write-ins. The {cite('fec-pres-2024','FEC January 16, 2025 compilation')} reports the same four tickets plus 4,073 scattered write-ins and 826,189 total. Neither it nor the original establishes named write-in totals or the legal validity of every generic mark. A separate named/valid write-in allocation remains unavailable for this source scope. [Candidate/party identities and literal header positions](data/turnout/contest-candidates.json).

| 2024 source category | Sum of all native rows | County footers/summary/state | House Clerk | FEC |
| --- | ---: | ---: | ---: | ---: |
| Harris / Walz, d | 418,488 | 418,488 | 418,488 | 418,488 |
| Trump / Vance, r | 395,523 | 395,523 | 395,523 | 395,523 |
| Oliver / ter Maat, l | 4,425 | 4,425 | 4,425 | 4,425 |
| Stein / Ware, g | 3,680 | 3,680 | 3,680 | 3,680 |
| Generic Write-Ins / scattered | 4,073 | 4,073 | 4,073 | 4,073 |
| **Candidate/write-in subtotal** | **826,189** | **826,189** | **826,189, calculated** | **826,189** |
| Undervotes, separate | 4,482 | 4,482 | 4,482 | Not this table's candidate total |
| Overvotes, separate | 362 | 362 | 362 | Not this table's candidate total |

Every county balances for every column; no county is omitted. The named-ticket sum is 822,116; D+R is 814,011; the two minor tickets plus generic write-ins total 12,178. Candidate/write-in votes plus under/over total **831,033**, a contest-category sum, **not the separate ballots-cast report**. Sources: {cite(p,'SOS `_3`')}, {cite('house-clerk-2024','House Clerk federal statistics')}, {cite('fec-pres-2024','FEC candidate table')}; [checks and full county controls](data/turnout/reconciliation.json).

The retained NARA certificate repeats four electors per slate and two certificate pages: its four slate totals are counted once (822,116), not four times or twice. One page is marked Amended with testimony year 2024; the other literally prints 2020 with a 2024 election header, and the four totals agree. Its release/correction chronology is unproved. It cannot control generic write-ins or municipal/ward allocations. {cite('nara-2024-NH-ascertainment','Original NARA New Hampshire ascertainment')}; [coordinator's read-only visual evidence](data/news/nara-state-control.json).

## Same-seat 2020 and actual 2022 midterm

Each selected Senate original independently retains **320 native labels, ten county footers and ten county summaries**. All numeric native, county and statewide candidate sums agree. In 2020, source dashes remain dashes/null: Coos scatter is a dash in its controls, while its populated rows have numeric 0; neither is silently recoded to the other. `Keene Ward 3*` and `Millsfield*` retain their literal asterisks and the source's correction footnotes. The 2022 remediated PDF and `_5` have identical candidate count vectors in county-table order; administrative abbreviations remain literal and are not used as a geographic crosswalk. {cite(s20,'2020 original Senate PDF')}, {cite(s22,'2022 `_5` Senate original')}, {cite('sos-archived-2022-ge-us-senator-remediated-1-pdf','2022 remediated Senate PDF')}.

| Contest | Democrat | Republican | Libertarian | Scatter | All reported candidate/scatter votes |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2020 Senate, same Class II seat | Jeanne Shaheen 450,778 | Corky Messner 326,229 | Justin O'Donnell 18,421 | 486 | **795,914** |
| 2022 Senate, other Class III seat, selected later SOS version | Maggie Hassan 332,490 | Donald C. Bolduc 275,631 | Jeremy Kauffman 12,390 | 464 | **620,975** |

The 2022 `_5` **summary** orders Hassan then Bolduc, while its **detail** orders Bolduc then Hassan. Candidate identity comes from each actual header, not a fixed column or the worksheets' misleading `gov` suffix. Earlier originals remain intact. The base workbook reports Hassan 333,217 / Bolduc 275,930 / Kauffman 12,280 / Scatter 459; `_1`: 333,193 / 275,928 / 12,390 / 464; `_2`: 332,193 / 275,928 / 12,390 / 464. `_5` and the remediated PDF report the table above. The freshly retrieved {cite('house-clerk-2022','House Clerk 2022 PDF')} still matches `_2`, with 297 fewer Hassan votes and 297 more Bolduc votes than the selected later SOS version. Both sum to 620,975. No source is rescaled or mixed, and archive capture/suffix/Last-Modified clocks do not prove the cause or precise public release sequence. [Every retained vintage and row-level disagreement](data/turnout/vintage-differences.json).

The 2024 `_0` presidential workbook reports 418,351 / 395,397 / 4,424 / 3,676 / 4,070 generic marks (plus 4,473 under / 353 over). The unsuffixed workbook captured in June 2025 reports 418,354 / 395,408 / 4,423 / 3,676 / 3,934 (plus 4,400 / 353). Later capture alone does not make it the accepted replacement: the {cite('archived-2024-results-index','actual SOS index archived September 17, 2026')} specifically links `_3`, `_14` ballots and `_7` checklist. `_3` also agrees with the national primary controls. All indexed originals recovered here remain in provenance. [Full source-scoped states](data/turnout/controls.json).

## Ballots, registration and method sensitivity

These are separate official administrative products. `Regular` and `Absentee` are their actual method labels; no candidate-by-method allocation, central absentee board, early-vote subdivision, blank count or Senate under/over count is synthesized. They have all 320 native labels, with original cells and positions retained. Checklist is the source's registration stock for the named general election, by Republican/Democratic/Undeclared, with polling-place registrations reported separately. The workbooks do not establish an active/inactive split or a precise statewide snapshot hour; amendment/capture dates are not registration as-of dates. Polling-place registrations are not added to checklist totals. Sources: {cite(b20,'2020 ballots')}, {cite(c20,'2020 checklist')}, {cite(b22,'2022 ballots `_3`')}, {cite(c22,'2022 checklist `_2`')}, {cite(b24,'2024 ballots `_14`')}, {cite(c24,'2024 checklist `_7`')}.

| Measure | 2020 general | 2022 general, actual midterm | 2024 general |
| --- | ---: | ---: | ---: |
| Selected Senate/president candidate + generic/scatter | 795,914 Senate | 620,975 Senate | 826,189 president |
| Ballots, source statewide summary | 814,499 | 626,931 | 831,467 |
| Ballots, sum of native Total cells | 814,499 | 626,931 | **831,468** |
| Regular, native sum | 554,282 | 568,276 | 731,944 |
| Absentee, native sum | 260,217 | 58,655 | **99,525** |
| Checklist total, native and state | 1,119,232 | 925,398 | 1,013,075 |
| Polling-place registrations, source Total column | 75,611 | 48,615 | 96,623 |

**Known administrative disagreements are retained, not repaired.** In 2024 `_14`, Coos native/footer Absentee is 1,968 and Total 17,511, versus summary 1,967 and 17,510. Somersworth Ward 3 has Regular 1,119 + Absentee 103 = 1,222, versus its literal Total 1,221. Thus native method components sum to 831,469, native Total to 831,468, state summary Total to 831,467, and state summary method components to 831,468. These are four specified scopes, not one interchangeable exact ballot figure. Hopkinton's polling-place registration components 55 + 46 + 195 = 296, but its literal Total is 3; the state component sum is 96,916 versus Total 96,623, a 293 difference. The separately reported checklist party stock does balance exactly. {cite(b24,'2024 ballot original')}; {cite(c24,'2024 checklist original')}; [complete field/row audits](data/turnout/administrative-audit.json).

The earlier 2024 ballot `_6` summary is 832,518; native Totals sum to 832,517 (Strafford footer/native 77,188 versus summary 77,189). It retains its own arithmetic and is not blended into `_14`. Earlier ballot/checklist originals and every original amendment byte remain recoverable. In 2022 `_3`, all native method/Total fields and county/state controls agree at 626,931, and the workbook literally notes an update on 12.8.22. The 2020 total is 814,499 with a literal update note 11.19.20; its original places paired county tables side by side, so source column A or G is retained as part of each locator. {cite('2024-ge-ballots-cast-6-xls','2024 `_6` original')}, {cite(b22,'2022 `_3` original')}, {cite(b20,'2020 original')}.

2024 native ballots exceed candidate/write-in marks by 5,279 and the contest-category sum including under/over by 435. The corresponding ballot-minus-Senate-mark gaps are 18,585 in 2020 and 5,956 in 2022. These subtractions **do not identify blank ballots, invalid write-ins, unreported undervotes or voter eligibility**, since the products have distinct source vintages and definitions. Blank/under/over fields absent from Senate originals remain unavailable. Ballots divided by checklist are descriptive source-product ratios, not voting-eligible turnout or a 2026 forecast: 2020 {100*814499/1119232:.8f}%, 2022 {100*626931/925398:.8f}%, and 2024 {100*831468/1013075:.8f}% using native Total cells (the 831,467 summary gives {100*831467/1013075:.8f}%).

Re-ranking each complete source by its own reported measure produces the sensitivities below. Each has its own complete order in [sensitivity.json](data/turnout/sensitivity.json); no current or cross-year geographic equivalence is inferred. The fixed 143-row priority has exact literal county/label matches in the selected 2024 administrative files: it contains 666,554 / 831,468 = {100*666554/831468:.8f}% of native ballot Total cells, and 817,376 / 1,013,075 = {100*817376/1013075:.8f}% of checklist stock. It also has exact literal county/label matches in the 2022 Senate original and contributes 495,056 / 620,975 = {100*495056/620975:.8f}% there. These are source-label comparisons, not ward-boundary crosswalks. No partial matching sample is presented as a complete fixed-set ballot comparison.

| Source-scoped measure | State native sum | Top-15 votes / share | Minimum 80% count | Preceding votes | Crossing label | Crossing cumulative | Remainder votes |
| --- | ---: | ---: | ---: | ---: | --- | ---: | ---: |''']
    names={s22:'2022 Senate',s20:'2020 Senate',b24:'2024 ballot Total cells (summary differs)',b22:'2022 ballot Total',b20:'2020 ballot Total',c24:'2024 checklist Total',c22:'2022 checklist Total',c20:'2020 checklist Total'}
    for sid,x in ss.items():
        t=x['top15'];m=x['minimum80'];lines.append(f"| {names[sid]} | {x['denominator']:,} | {t['votes']:,} / {t['percent']:.8f}% | {m['count']} | {m['preceding_votes']:,} | {m['crossing_geography']} | {m['votes']:,} | {x['remainder']['votes']:,} |")
    lines.append(f'''
## Provenance, publication status and reproduction

These are official historical result/administrative publications recovered as complete archived original files after current SOS access failures, with the selected 2024 index chain recovered independently. National certificate/statistics controls corroborate specified scopes. The worksheets are not timestamped live snapshots, and this work does not assign a certification date or legal status to every generic write-in. The {cite('2024-state-general-election-media-guide-pdf','official 2024 media guide')} describes moderator announcements, Return of Votes delivery to SOS, post-election certificates and the state's certification process. It does not establish actual November 2026 cadence. Current local-clerk authority/feeds remain separate research work.

Newsroom/volunteer preparation stays outside the baseline. The [retained coordinator newsroom evidence](local-news-results.md) distinguishes NHPR/WMUR historical/primary products, shared AP suppliers and `nhelectionresults.org`'s expressly unofficial clerk/volunteer returns and statistical projections. A volunteer site's 317/320 polling-place flag or a newsroom's 318 flag is not proof of this source's reporting geography, complete certified returns or a November roster. No projections are added to reported votes. No collector, calibrated Needle, 2026 turnout forecast, approved current precinct map or live cadence is claimed.

- [Source schema, exact decoding/rebuild instructions and known gaps](data/turnout/source/SCHEMA.md).
- [Lossless shared-original references, hashes, HTTP metadata and original/download chains](data/turnout/source/shared-originals.json); new captures have individual `.json`, `.headers.txt` and `.body.gz` under `data/turnout/source/`. The shared news originals are reused read-only, not duplicated. Source UTC retrieval, archive capture, election header, HTTP Last-Modified and document update notes are distinct clocks.
- [Original-byte extraction](data/turnout/extract.py), [calculation](data/turnout/build_turnout.py), [report generator](data/turnout/report.py), [offline validator](data/turnout/validate_turnout.py), [acquisition](data/turnout/acquire.py).
- [All candidate/method/registration source-native field records](data/turnout/native-fields.jsonl.gz), [primary balances](data/turnout/reconciliation.json), [vintage differences](data/turnout/vintage-differences.json), [validation](data/turnout/validation.json), [complete owned asset manifest](data/turnout/asset-manifest.json).

The [actual reciprocal peer agreement](data/turnout/peer-agreement.json) records **{peer['status']}** for peer `d272caf4-db4f-4c84-8950-c5e0fabe93e7`. [Reproducible read-only comparison](data/turnout/compare_peer.py) checks all 23 × 320 native rows, all 34,880 parsed fields and raw values, source positions, shared BIFF types, primary original hashes, county/state controls, the 960-row baseline CSV, and every priority row/key/order/threshold. It reports zero disagreements. Each worker extracted originals independently; peer outputs were not used as count/build inputs or edited to match.

The **frozen** dispatch contract refers only by path to `data/coordinator-priority-acceptance.json`, relative to this state directory. That external, coordinator-owned record alone grants historical acceptance; the contract's worker flag remains provisional/false. It contains no reverse acceptance hash. Acceptance and current-boundary approval are separate: arithmetic agreement does not approve legal geography, clerk authority or future reporting equivalence.

{acceptance_text} A [separate reciprocal control supplement](data/turnout/peer-control-agreement.json) additionally compares all 483 county-summary, county-footer and state-summary records (2,289 fields) with zero disagreements; the accepted peer record stays byte-for-byte unchanged.

## Complete native order and remainder

Every row below comes from {cite(p,'the selected official `_3` presidential workbook')}. Votes exclude under/over and are numeric reported subtotals; `†` marks at least one blank candidate field, with literal cells retained in the CSV/native extracts. City parents and county controls are never extra rows. `Priority` is the union of top 15 and minimum-80%; **ranks 144–320 are the full remainder**, including 16 unpopulated printed-ticket rows with generic numeric 0. Percentage displays are rounded; exact integer counts govern membership.

| Rank | County context | Native label | Reported candidate/write-in votes | Cumulative votes | Cumulative % | Priority |
| ---: | --- | --- | ---: | ---: | ---: | --- |''')
    for r in q['all_units']:
        flag=' †'if r['candidate_field_completeness']!='complete_numeric'else ''
        lines.append(f"| {r['rank']} | {r['county']} | {r['display_label']}{flag} | {r['reported_candidate_write_in_votes']:,} | {r['cumulative_votes']:,} | {100*r['cumulative_votes']/q['denominator']:.8f} | {'Yes'if r['rank']<=143 else 'Remainder'} |")
    (ROOT.parent.parent/'turnout.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
