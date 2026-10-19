#!/usr/bin/env python3
"""Independent original CSV/SSR source and full native contract replay."""
from collections import Counter, defaultdict
from pathlib import Path
import csv
import gzip
import hashlib
import io
import json
import re

D = Path(__file__).resolve().parent
S = D.parent
T = D / 'turnout'
counts = Counter()


def sha(b):
    return hashlib.sha256(b).hexdigest()


def pin(p):
    b = p.read_bytes()
    return dict(path=str(p.relative_to(S)), bytes=len(b), sha256=sha(b))


def check(value, kind, detail=''):
    assert value, (kind, detail)
    counts[kind] += 1


def main():
    manifest = {r['id']: r for r in json.loads((D / 'news/manifest.json').read_bytes())}
    universes_path = T / 'extracts/candidate-universes.json'
    universes = json.loads(universes_path.read_bytes())
    source_rows_path = T / 'extracts/historical-source-rows.jsonl.gz'
    observed = [json.loads(line) for line in gzip.decompress(source_rows_path.read_bytes()).splitlines()]
    observed_by_position = {(r['source_id'], r['source_record']): r for r in observed}
    check(len(observed_by_position) == len(observed) == 9831, 'all9831_complete_source_objects')
    expected, originals = [], []
    by_year = {}
    for year, contest, contest_id, native_count, total in [
            (2024, 'president', '26499', 3199, 3192745),
            (2022, 'senate', '25990', 3232, 2500201),
            (2020, 'senate', '3602', 3205, 3235790)]:
        def original(kind):
            source_id = f'sos-history-observed-{year}-{contest}-' + kind
            receipt = manifest[source_id]
            p = D / 'news' / receipt['asset']
            stored = p.read_bytes()
            raw = gzip.decompress(stored)
            check(sha(stored) == receipt['stored_sha256'] and sha(raw) == receipt['raw_sha256']
                  and len(raw) == receipt['bytes'], 'complete_original_hash', source_id)
            originals.append(dict(receipt=receipt, stored_original=pin(p)))
            return source_id, raw
        source_id, raw = original('table-csv')
        rows = list(csv.reader(io.StringIO(raw.decode('utf-8-sig'))))
        page_id, page = original('contest')
        match = re.search(r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.*?)</script>', page.decode(), re.S)
        props = json.loads(match.group(1))['props']['pageProps']
        universe = universes[str(year)]
        check(universe['page_properties'] == props, 'complete_original_SSR_properties')
        check(universe['header'] == rows[0] and universe['party_header'] == rows[1], 'all_raw_headers_parties')
        check(props['contest']['id'] == contest_id and props['contest']['event']['hasBallots'] is False,
              'source_contest_and_pseudo_ballot_scope')
        columns = len(rows[0]) - 4
        county = None
        native = []
        counties = {}
        state = None
        for number, fields in enumerate(rows[2:], 3):
            check(len(fields) == columns + 4 and all(v.isdigit() for v in fields[2:]), 'complete_numeric_CSV_schema')
            level = fields[0]
            if level == 'County':
                county = fields[1]
                key = f'CO|{year}|{contest_id}|{county}'
                label = None
            elif level == 'Precinct':
                check(county is not None, 'actual_county_parent_before_native')
                key = f'CO|{year}|{contest_id}|{county}|{fields[1]}'
                label = fields[1]
            else:
                check(level == 'State', 'source_role_literal')
                key = f'CO|{year}|{contest_id}|State'
                label = None
            votes = [int(v) for v in fields[2:-2]]
            check(sum(votes) == int(fields[-2]) == int(fields[-1]), 'candidate_sum_and_duplicate_pseudo_ballots')
            check(len(votes) == columns, 'all_candidate_positions')
            r = observed_by_position[source_id, number]
            fields_expected = dict(year=year, contest_id=contest_id, source_id=source_id,
                                   source_record=number, key=key, level_literal=level,
                                   county_literal=county if level != 'State' else None,
                                   native_id_literal=label, raw_fields=fields, candidate_values=votes,
                                   candidate_votes=sum(votes), source_TOTAL_VOTES=int(fields[-2]),
                                   source_TOTAL_BALLOTS=int(fields[-1]))
            for field, value in fields_expected.items():
                check(r[field] == value, 'all_source_row_fields', (source_id, number, field))
            for field in ['method', 'blank', 'undervote', 'overvote', 'administrative_ballots', 'registration']:
                check(r[field] is None, 'unavailable_not_invented_zero')
            expected.append(fields_expected)
            if level == 'County':
                counties[county] = votes
            elif level == 'Precinct':
                native.append(r)
            else:
                state = votes
        check(len(native) == native_count and len(counties) == 64, 'full_native_and64_parent_coverage')
        for name, votes in counties.items():
            children = [r for r in native if r['county_literal'] == name]
            check([sum(r['candidate_values'][i] for r in children) for i in range(columns)] == votes,
                  'every_native_candidate_vector_to_county')
        check([sum(v[i] for v in counties.values()) for i in range(columns)] == state,
              'all64_county_candidate_vectors_to_state')
        check(sum(state) == total, 'independent_state_denominator')
        by_year[year] = dict(native=native, counties=counties, denominator=total,
                             candidates=columns, source_properties=props)
    check(sum(len(r['candidate_values']) for r in expected if r['level_literal'] == 'Precinct') == 99514,
          'all99514_native_candidate_positions')
    check(sum(len(r['raw_fields']) - 2 for r in expected) == 121191, 'all121191_numeric_source_positions')
    contract_path = T / 'priority-set.json'
    c = json.loads(contract_path.read_bytes())
    primary = sorted(by_year[2024]['native'], key=lambda r: (-r['candidate_votes'], r['key']))
    keys = [r['key'] for r in primary]
    check(len(c['full_order']) == 3199, 'complete_full_order')
    cumulative = 0
    for rank, (actual, source) in enumerate(zip(c['full_order'], primary), 1):
        cumulative += source['candidate_votes']
        for field in ['key', 'source_id', 'source_record', 'county_literal', 'native_id_literal',
                      'raw_fields', 'candidate_values', 'candidate_votes', 'source_TOTAL_VOTES', 'source_TOTAL_BALLOTS']:
            check(actual[field] == source[field], 'full_primary_contract_source_fields')
        check(actual['rank'] == rank and actual['cumulative_votes'] == cumulative, 'full_rank_cumulative')
    check(cumulative == 3192745 and sum(r['candidate_votes'] for r in primary[:15]) == 39005, 'top15_full_denominator')
    check(sum(r['candidate_votes'] for r in primary[:1991]) == 2553363 and
          sum(r['candidate_votes'] for r in primary[:1992]) == 2554233, 'minimum_integer80_crossing')
    check(primary[1991]['county_literal'] == 'Summit' and primary[1991]['native_id_literal'] == '2081359007'
          and primary[1991]['candidate_votes'] == 870, 'actual_crossing_source_identity')
    check(c['ordered_priority_keys'] == keys[:1992] and c['ordered_remainder_keys'] == keys[1992:], 'exact_priority_remainder_arrays')
    check(len(keys[1992:]) == 1207 and sum(r['candidate_votes'] for r in primary[1992:]) == 638512, 'all_remainder_preserved')
    hierarchy = {p['county']: p for p in c['county_native_hierarchy']}
    check(len(hierarchy) == 64 and len(c['county_parents']) == 64, 'complete_parent_hierarchy')
    remainder_children = {}
    for name, parent in hierarchy.items():
        full = [r['key'] for r in primary if r['county_literal'] == name]
        check(parent['all_native_keys'] == full, 'ordered_parent_full_children')
        check(parent['priority_native_keys'] == [k for k in full if k in set(keys[:1992])],
              'ordered_parent_priority_children')
        remainder_children[name] = [k for k in full if k in set(keys[1992:])]
        check(set(full) == set(parent['priority_native_keys']) | set(remainder_children[name]) and
              not set(parent['priority_native_keys']) & set(remainder_children[name]), 'parent_disjoint_full_partition')
    check(not c['current_geography_approved'] and not c['formal_coordinator_acceptance'], 'false_flags_unchanged')
    out = dict(status='pass_independent_original_CSV_SSR_full_native_contract',
               producer_modules_imported=False, complete_originals=originals,
               complete_historical_objects=9831, all_candidate_native_positions=99514,
               numeric_source_positions=121191, native_counts={str(y): len(v['native']) for y, v in by_year.items()},
               all64_candidate_controls_each_year=True,
               complete_source_universe=pin(universes_path), complete_source_rows=pin(source_rows_path),
               frozen_contract=pin(contract_path), source_denominator=3192745, top15_votes=39005,
               parent_remainder_representation='Source contract stores complete full/priority parent arrays and '
               'complete global remainder. The following ordered parent remainder arrays are independently '
               'derived by exact source-key intersection; they are not falsely attributed as an existing field.',
               derived_ordered_remainder_child_keys_by_parent=remainder_children,
               minimum80_count=1992, minimum80_votes=2554233, preceding1991_votes=2553363,
               remainder1207_votes=638512, checks=dict(counts), total_checks=sum(counts.values()),
               current_geography_approved=False, coordinator_priority_accepted=False,
               qualification='CSV candidate universe and complete original source objects only. '
                             'Duplicate pseudo-ballots are not administrative participation; annotations, sparse statistics, '
                             'write-in flags, current identities, method/under/over gaps and operational admission stay separate.')
    path = D / 'coordinator-first-pair-source-review.json'
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(dict(**pin(path), checks=sum(counts.values()))))


if __name__ == '__main__':
    main()
