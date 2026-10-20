"""Independent complete original header/candidate/native baseline field audit."""
from pathlib import Path
import csv
import hashlib
import json
import math
import re

S = Path(__file__).resolve().parents[1]
B = S / 'data/baselines'
N = 0


def ck(v, note=''):
    global N
    assert v, note
    N += 1


def read(p):
    return json.loads(p.read_bytes())


def pin(p):
    b = p.read_bytes()
    return dict(path=str(p.relative_to(S)), bytes=len(b), sha256=hashlib.sha256(b).hexdigest())


def near(a, b):
    ck(math.isclose(float(a), b, rel_tol=2e-11, abs_tol=1e-10), (a, b))


def main():
    proof = read(S / 'data/coordinator-native-original-review.json')
    original_rows = proof['all_original_source_rows']
    parent_path = S / 'data/turnout/extract/native-rows.json'
    parent_records = read(parent_path)
    parents = {r['source_id']: (r['county'], r['county_fips']) for rr in parent_records.values() for r in rr}
    headers = {r['source_id']: r['header_lines'][0]['complete_predata_nonnumeric_layout_lines'] for r in proof['complete_original_pins_and_header_representations']}
    definitions = {}
    header_fields = 0
    literal_caption_exceptions = []
    for scope, result in proof['source_results'].items():
        # Atlantic has complete literal names and party captions on two printed
        # header rows. Use those independent original captions as the schema,
        # then verify every other complete original header, including the one
        # Cumberland name line whose columns lack a double-space separator.
        atlas_sid = next(f['source_id'] for f in result['printed_county_footers'] if f['source_id'].endswith('-atlantic'))
        n = result['candidate_columns']
        lines = [re.split(r'\s{2,}', line.strip()) for line in headers[atlas_sid] if line.strip()]
        schema = [line for line in lines if len(line) == n]
        ck(len(schema) == 2)
        names, parties = schema
        definitions[scope] = list(zip(names, parties))
        for footer in result['printed_county_footers']:
            text = '\n'.join(headers[footer['source_id']])
            county = parents[footer['source_id']][0]
            ck(re.search(re.escape(county) + r'\s+County', text, re.I) is not None, 'original printed parent caption')
            for name, party in definitions[scope]:
                literal = name
                if footer['source_id'] == '2024-official-general-results-president-somerset' and name == 'Robert F. Kennedy Jr.':
                    literal = 'Robert F. Kenndy Jr.'
                    literal_caption_exceptions.append(dict(source_id=footer['source_id'],
                                                           original_printed_caption=literal,
                                                           Atlantic_schema_caption=name,
                                                           raw_header_lines=headers[footer['source_id']],
                                                           qualification='Distinct exact printed captions; original full page visually checked. No vote or current identity repair.'))
                ck(literal in text and party in text, (footer['source_id'], literal, party))
                header_fields += 2
    county_path = S / 'data/county-baselines.csv'
    native_path = B / 'native-baselines.csv'
    initial = [pin(county_path), pin(native_path), pin(B / 'priority-set.json')]
    counties = list(csv.DictReader(county_path.open()))
    native = list(csv.DictReader(native_path.open()))
    ck(len(counties) == 84 and len(native) == 2296)
    county_map = {(r['scope'], r['source_id']): r for r in counties}
    native_map = {(r['scope'], r['unit_key']): r for r in native}
    ck(len(county_map) == 84 and len(native_map) == 2296)
    checked_native = checked_county = 0
    for scope, result in proof['source_results'].items():
        for footer in result['printed_county_footers']:
            sid = footer['source_id']
            row = county_map[scope, sid]
            values = footer['printed_candidate_vector']
            county, fips = parents[sid]
            ck(row['county'] == county and row['county_fips'] == fips)
            ck(row['unit_key'] == scope + ':county:' + fips)
            verify(scope, row, values, definitions)
            checked_county += 1
        for original in original_rows[scope]:
            row = native_map[scope, original['key']]
            county, fips = parents[original['source_id']]
            for field, value in [('source_id', original['source_id']), ('page', str(original['page'])),
                                 ('line', str(original['line'])), ('native_label', original['native_label']),
                                 ('source_row', original['source_line']), ('county', county), ('county_fips', fips)]:
                ck(row[field] == value, (original['key'], field))
            values = original['values']
            ck(json.loads(row['literal_null_columns']) == [i for i, v in enumerate(values) if v is None])
            verify(scope, row, values, definitions)
            checked_native += 1
    priority = read(B / 'priority-set.json')
    ordered = sorted(original_rows['2024-senate'], key=lambda r: (-sum(v for v in r['values'] if v is not None), r['key']))
    keys = [r['key'] for r in ordered]
    ck(priority['total'] == 4031795 and priority['threshold_integer'] == (4 * 4031795 + 4) // 5)
    ck(len(priority['order']) == 575 and [r['key'] for r in priority['order']] == keys)
    ck(priority['priority_keys'] == keys[:233] and priority['remainder_keys'] == keys[233:])
    ck(priority['accepted_by_coordinator'] is False)
    ck(initial == [pin(county_path), pin(native_path), pin(B / 'priority-set.json')])
    out = dict(status='pass_independent_complete_original_baseline_core', checks=N,
               original_header_name_party_fields=header_fields, county_rows=checked_county,
               native_rows=checked_native, candidate_schemas={k: [dict(name=a, party=b) for a, b in v] for k, v in definitions.items()},
               exact_current_core_pins=initial, literal_caption_exceptions=literal_caption_exceptions,
               original_audit=pin(S/'data/coordinator-native-original-review.json'),
               complete_source_parent_metadata=pin(parent_path),
               qualifications='Full literal candidate/header/party/raw source/position/null/pair/other fields checked against complete original PDF replay. Known numeric source scope only, not statewide eligible writein allocation, later final peer equality, finer physical roster or current identity approval.')
    p = S/'data/coordinator-baseline-core-review.json'
    p.write_text(json.dumps(out, indent=2)+'\n')
    print(dict(checks=N, native=checked_native, county=checked_county, proof=pin(p)))


def verify(scope, row, values, definitions):
    names = definitions[scope]
    ck(row['A_name'] == names[0][0] and row['A_party'] == names[0][1])
    ck(row['B_name'] == names[1][0] and row['B_party'] == names[1][1])
    A, B = values[:2]
    ck(row['A'] == ('' if A is None else str(A)))
    ck(row['B'] == ('' if B is None else str(B)))
    P = (A or 0) + (B or 0)
    V = sum(v for v in values if v is not None)
    O = sum(v for v in values[2:] if v is not None)
    ck(int(row['pair_votes']) == P and int(row['other_named']) == O and int(row['published_candidate_total']) == V)
    if V:
        near(row['pair_participation'], P/V)
    else:
        ck(row['pair_participation'] == '')
    if P:
        near(row['A_pair_share'], A/P)
        near(row['A_pair_margin_pp'], 100*((A or 0)-(B or 0))/P)
    else:
        ck(row['A_pair_share'] == row['A_pair_margin_pp'] == '')
    candidates = json.loads(row['full_candidates_json'])
    ck(len(candidates) == len(values))
    for (name, party), votes, candidate in zip(names, values, candidates):
        ck(candidate == dict(name=name, party_ballot_label=party, votes=votes), (scope, row['unit_key'], candidate))


if __name__ == '__main__':
    main()
