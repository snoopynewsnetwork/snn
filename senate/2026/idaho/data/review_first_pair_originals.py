#!/usr/bin/env python3
"""Independent OOXML/source-position and canonical native contract audit.

No producer imports. Retained complete original entities are the cell authority.
Every declared selected candidate/statistic raw cell is compared, including
types, styles, nulls, formula text, literal labels and header fields.
"""
from collections import Counter, defaultdict
from pathlib import Path
import csv
import gzip
import hashlib
import io
import json
import posixpath
import re
import zipfile
import xml.etree.ElementTree as E

D = Path(__file__).resolve().parent
S = D.parent
T = D / 'turnout'
B = D / 'baselines'
NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
counts = Counter()
inputs = {}
books = {}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def read(p):
    b = p.read_bytes()
    inputs[str(p.relative_to(S))] = dict(path=str(p.relative_to(S)), bytes=len(b), sha256=sha(b))
    return b


def load(p):
    b = read(p)
    return json.loads(gzip.decompress(b) if p.suffix == '.gz' else b)


def table(p):
    b = read(p)
    return list(csv.DictReader(io.StringIO(b.decode())))


def check(test, kind, detail=''):
    assert test, (kind, detail)
    counts[kind] += 1


def workbook(raw):
    z = zipfile.ZipFile(io.BytesIO(raw))
    check(z.testzip() is None, 'OOXML_ZIP_CRC')
    shared = []
    if 'xl/sharedStrings.xml' in z.namelist():
        shared = [''.join(s.itertext()) for s in E.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si', NS)]
    rel = {r.attrib['Id']: r.attrib['Target'] for r in E.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
    sheets = {}
    for sheet in E.fromstring(z.read('xl/workbook.xml')).find('m:sheets', NS):
        target = rel[sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']]
        member = target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/' + target)
        rows = {}
        for row in E.fromstring(z.read(member)).findall('m:sheetData/m:row', NS):
            cells = {}
            for c in row:
                if not c.tag.endswith('}c'):
                    continue
                v, f = c.find('m:v', NS), c.find('m:f', NS)
                raw_v = v.text if v is not None else None
                value = raw_v
                if c.get('t') == 's' and raw_v is not None:
                    value = shared[int(raw_v)]
                elif c.get('t') == 'inlineStr':
                    inline = c.find('m:is', NS)
                    value = ''.join(inline.itertext()) if inline is not None else None
                col = re.sub('[0-9]', '', c.attrib['r'])
                cells[col] = dict(address=c.attrib['r'], value=value, type=c.get('t'),
                                  style=c.get('s'), raw_v=raw_v, formula=f.text if f is not None else None)
            rows[int(row.attrib['r'])] = cells
        sheets[sheet.attrib['name']] = dict(member=member, rows=rows)
    return sheets


def main():
    references = load(T / 'source/reused-originals.json')
    raw = {}
    for ref in references:
        p = (T / ref['reused_path']).resolve()
        b = read(p)
        r = gzip.decompress(b)
        check(sha(b) == ref['stored_sha256'] and sha(r) == ref['raw_sha256'] and len(r) == ref['bytes'],
              'complete_original_hash', ref['id'])
        raw[ref['id']] = r
    for source in ['sos-2024-all-races-xlsx', 'sos-2024-turnout-xlsx']:
        books[(source, None)] = workbook(raw[source])
    positions = load(B / 'source/candidate-positions.json.gz')
    statistics = load(B / 'source/statistics-positions.json.gz')
    for row in positions + statistics:
        key = row['source_id'], row.get('archive_member')
        if key in books:
            continue
        z = zipfile.ZipFile(io.BytesIO(raw[key[0]]))
        check(z.testzip() is None, 'parent_archive_CRC')
        books[key] = workbook(z.read(key[1]))
    check(len(positions) == 36565 and len(statistics) == 2099, 'complete_selected_field_scope')
    for row in positions:
        sheet = books[row['source_id'], row.get('archive_member')][row['worksheet']]
        check(sheet['member'] == row['worksheet_member'], 'actual_worksheet_member')
        original = sheet['rows'][row['row']]
        if 'raw_cells' in row:
            check(original == row['raw_cells'], 'complete_candidate_source_row_cells')
        else:
            check(original.get(row['column']) == row['raw_cell'], 'historical_candidate_raw_cell')
            check(original.get('A') == row['raw_label_cell'], 'historical_literal_label_raw_cell')
        c = row['candidate']
        v = original.get(row['column'], {}).get('value')
        check(c['votes'] == (int(v) if v is not None else None), 'selected_candidate_value_and_null')
        if row['contest'] == '2024-president':
            check(c['header_literal'] == original['F']['value'] and c['party'] == original.get('E', {}).get('value'),
                  'literal_2024_candidate_party')
        else:
            headers = [r.get(row['column'], {}).get('value') for i, r in sheet['rows'].items() if i < 8]
            check(c['header_literal'] in headers, 'literal_historical_candidate_header', c)
            check(c['party_header_literal'] in headers, 'literal_historical_party_header', c)
    for row in statistics:
        original = books[row['source_id'], row.get('archive_member')][row['worksheet']]['rows'][row['row']]
        check(original == row['raw_cells'], 'complete_statistics_raw_row_cells')
        cols = ['C', 'D', 'E', 'F'] if row['year'] == 2024 else ['D', 'E', 'F', 'G']
        for field, col in zip(['cutoff', 'day', 'registered', 'ballots'], cols):
            v = original.get(col, {}).get('value')
            check(row[field] == (int(v) if v is not None else None), 'statistics_value_null', (row['row'], field))
    # Every saved row/cell of both complete 2024 workbooks, including unrelated offices.
    for name, source in [('2024-races', 'sos-2024-all-races-xlsx'), ('2024-stats', 'sos-2024-turnout-xlsx')]:
        derivative = load(T / ('source/' + name + '-rows.json.gz'))
        check(derivative['original_sha256'] == sha(raw[source]), 'full_workbook_original_identity')
        for sheet in derivative['sheets']:
            original = books[source, None][sheet['sheet']]
            check(sheet['member'] == original['member'], 'complete_workbook_sheet')
            check({r['row'] for r in sheet['rows']} == set(original['rows']), 'all_workbook_rows_retained')
            for row in sheet['rows']:
                cells = original['rows'][row['row']]
                check(row['cells'] == {k: c['value'] for k, c in cells.items()}, 'all_workbook_cell_values')
                check(row['cell_metadata'] == {k: dict(address=c['address'], type=c['type'], style=c['style'],
                                                     raw_value=c['raw_v'], formula=c['formula'])
                                               for k, c in cells.items()}, 'all_workbook_types_styles_formula_nulls')
    fips_raw = gzip.decompress(read(T / 'source/fips2020.gz')).decode()
    check(sha(fips_raw.encode()) == '9f6e5f6eb6ac2f5e9a36d5fd01dec77991bddc75118f748a069441a4782970d6', 'Census_original_FIPS')
    fips = {r['COUNTYNAME']: r['STATEFP'] + r['COUNTYFP']
            for r in csv.DictReader(io.StringIO(fips_raw), delimiter='|') if r['STATE'] == 'ID'}
    check(len(fips) == 44, 'all44_original_county_codes')
    races = books['sos-2024-all-races-xlsx', None]['raw_races']['rows']
    groups = defaultdict(list)
    for number, cells in races.items():
        if cells.get('D', {}).get('value') == 'United States President':
            groups[cells['A']['value'], cells['B']['value']].append((number, cells))
    expected = []
    for (county, label), fields in groups.items():
        check(len(fields) == 13, 'all13_original_category_positions')
        first, last = min(n for n, _ in fields), max(n for n, _ in fields)
        key = f'ID:2024:pres:{fips[county]}:{first}'
        candidate = [x for x in fields if x[1]['F']['value'] not in ['Overvotes', 'Undervotes']]
        check(len(candidate) == 11, 'all11_original_candidate_fields')
        totals = {c['F']['value']: int(c['G']['value']) for _, c in fields}
        expected.append(dict(key=key, county=county, county_fips=fips[county], literal_precinct=label,
                             source_first_row=first, source_last_row=last,
                             candidate_votes=sum(int(c['G']['value']) for _, c in candidate),
                             overvotes=totals['Overvotes'], undervotes=totals['Undervotes'],
                             all_categories=sum(totals.values())))
    expected.sort(key=lambda r: (-r['candidate_votes'], r['key']))
    check(len(expected) == 985 and sum(r['candidate_votes'] for r in expected) == 905057, 'primary_original_universe')
    contract = load(T / 'priority-set.json')
    peer_contract = load(B / 'priority-contract.json')
    order = table(T / 'native-order.csv')
    cumulative = 0
    for rank, (u, row, cr) in enumerate(zip(expected, order, contract['complete_order']), 1):
        cumulative += u['candidate_votes']
        for k, v in u.items():
            check(row[k] == str(v), 'original_canonical_native_fields', (rank, k))
        check(int(row['rank']) == rank and int(row['cumulative_votes']) == cumulative, 'original_canonical_rank_cumulative')
        check(cr['key'] == u['key'], 'complete_contract_order')
    keys = [r['key'] for r in expected]
    check(peer_contract['ordered_keys'] == keys, 'independent_peer_full_canonical_order')
    check(contract['ordered_priority_keys'] == keys[:528] == peer_contract['ordered_priority_keys'], 'exact528_ordered_keys')
    check(contract['ordered_remainder_keys'] == keys[528:] == peer_contract['ordered_remainder_keys'], 'all457_remainder')
    check(sum(r['candidate_votes'] for r in expected[:527]) == 723753 and
          sum(r['candidate_votes'] for r in expected[:528]) == 724515 and
          expected[527]['candidate_votes'] == 762 and expected[527]['literal_precinct'] == 'Osburn', 'integer80_unique_crossing')
    for map_field, selected in [('ordered_child_keys_by_parent', keys),
                                ('ordered_priority_child_keys_by_parent', keys[:528]),
                                ('ordered_remainder_child_keys_by_parent', keys[528:])]:
        maps = {f: [k for k in selected if k.split(':')[3] == f] for f in fips.values()}
        check(contract[map_field] == maps == peer_contract[map_field], 'all44_complete_parent_child_maps')
    parents = {x['key']: x for x in contract['all_county_constituents']}
    check(set(parents) == set(fips.values()), 'all44_full_parent_objects')
    embedded = {u['key']: u for parent in parents.values() for u in parent['president_contexts']}
    for u in expected:
        check(all(embedded[u['key']][k] == v for k, v in u.items()), 'all985_full_embedded_source_units')
    for rel in contract['source_object_paths'].values():
        p = T / rel
        check(p.is_file(), 'every_complete_companion_dependency_present', rel)
        read(p)
    check(not contract['current_geography_approved'] and not contract['priority_accepted'], 'frozen_false_flags_preserved')
    for entry in inputs.values():
        p = S / entry['path']
        check(p.stat().st_size == entry['bytes'] and sha(p.read_bytes()) == entry['sha256'], 'input_bytes_stable')
    out = dict(status='pass_independent_original_cells_and_full_canonical_source_scope',
               producer_modules_imported=False, complete_originals=len(raw), workbooks=len(books),
               selected_candidate_positions=len(positions), selected_statistics_rows=len(statistics),
               native2024=985, priority528_votes=724515, preceding527_votes=723753,
               source_votes=905057, all44_parents=True, remainder457_votes=180542,
               complete_companion_dependencies_required=True, inputs=list(inputs.values()),
               checks=dict(counts), total_checks=sum(counts.values()),
               coordinator_priority_accepted=False, current_geography_approved=False,
               qualification='Only the complete historical source universe/order is reviewed here. '
                             'Boundary scopes, original nulls and source write-in disagreement stay unallocated. '
                             'No cross-year/current identity, eligible-universe exhaustion, feed or probability approval.')
    target = D / 'coordinator-first-pair-original-review.json'
    target.write_text(json.dumps(out, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(dict(path=str(target), bytes=target.stat().st_size,
                          sha256=sha(target.read_bytes()), checks=sum(counts.values()))))


if __name__ == '__main__':
    main()
