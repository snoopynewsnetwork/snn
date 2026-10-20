"""Original CSV-only known-source-mark order; no legal/physical join approval."""
from collections import defaultdict
from pathlib import Path
import csv
import gzip
import hashlib
import io
import json

D = Path(__file__).resolve().parent


def sha(b):
    return hashlib.sha256(b).hexdigest()


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode()


def main():
    pin = json.loads((D / 'coordinator-native-category-source-pin.json').read_bytes())
    stored = (D / 'news' / pin['asset']).read_bytes()
    raw = gzip.decompress(stored)
    assert sha(stored) == pin['stored_sha256'] and sha(raw) == pin['raw_sha256']
    reader = csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))
    headers = reader.fieldnames
    groups = defaultdict(list)
    presentations = set()
    printed = ['Kamala D. Harris', 'Donald J. Trump', 'Robert F. Kennedy Jr.']
    for position, row in enumerate(reader, 2):
        groups[(row['JurisdictionID'], row['PrecinctName'])].append(dict(source_CSV_line=position, fields=row))
        presentations.add(tuple(row[k] for k in ['JurisdictionID', 'JurisContainerID', 'JurisName', 'PrecinctName']))
    assert len(groups) == 10062 and len(presentations) == 11535
    units = []
    for (authority, precinct), rows in groups.items():
        cells = {}
        for name in printed:
            matches = [r for r in rows if r['fields']['CandidateName'] == name]
            assert len(matches) <= 1
            cells[name] = int(matches[0]['fields']['VoteCount']) if matches else None
        known = sum(v for v in cells.values() if v is not None)
        generic_rows = [r for r in rows if r['fields']['CandidateName'] in
                        ['WRITE-IN', 'Write-In', 'Write-in', 'write-in']]
        generic = sum(int(r['fields']['VoteCount']) for r in generic_rows)
        key = json.dumps(['2024', authority, precinct], ensure_ascii=False, separators=(',', ':'))
        units.append(dict(unit_key=key, authority_ID=authority, literal_precinct=precinct,
                          printed_candidate_cells=cells, known_printed_source_record_sum=known,
                          generic_source_record_sum=generic,
                          literal_generic_category_labels=[r['fields']['CandidateName'] for r in generic_rows],
                          named_pool_status='unavailable_administrative_only' if all(v is None for v in cells.values()) else 'recorded_printed_known_scope',
                          full_original_row_count=len(rows),
                          full_original_rows_sha256=sha(encoded(rows)),
                          original_CSV_positions=[r['source_CSV_line'] for r in rows]))
    input_pin_path = D / 'coordinator-review-inputs/printed-priority-input-pin.json'
    if input_pin_path.exists():
        input_pin = json.loads(input_pin_path.read_bytes())
        pinned_body = (D.parent / input_pin['immutable_body_path']).read_bytes()
        assert sha(pinned_body) == input_pin['stored_sha256']
        peer_bytes = gzip.decompress(pinned_body)
        assert sha(peer_bytes) == input_pin['raw_sha256']
    else:
        peer_bytes = (D / 'baselines/priority/contracts.json').read_bytes()
    frozen = D / 'coordinator-review-inputs' / ('baseline-priority-contracts-' + sha(peer_bytes) + '.json.gz')
    frozen.parent.mkdir(exist_ok=True)
    snapshot = gzip.compress(peer_bytes, mtime=0)
    if frozen.exists():
        assert frozen.read_bytes() == snapshot
    else:
        frozen.write_bytes(snapshot)
    input_pin = dict(observed_path='data/baselines/priority/contracts.json',
                     immutable_body_path=str(frozen.relative_to(D.parent)),
                     stored_bytes=len(snapshot), stored_sha256=sha(snapshot),
                     raw_bytes=len(peer_bytes), raw_sha256=sha(peer_bytes))
    if input_pin_path.exists():
        assert json.loads(input_pin_path.read_bytes()) == input_pin
    else:
        input_pin_path.write_text(json.dumps(input_pin, indent=2)+'\n')
    peer = json.loads(peer_bytes)['contracts']
    scopes = {}
    for name, extra in [('native-2024-printed-observed', False), ('native-2024-printed-plus-generic-records', True)]:
        ordered = sorted(units, key=lambda r:(-(r['known_printed_source_record_sum'] + (r['generic_source_record_sum'] if extra else 0)), r['authority_ID'], r['literal_precinct']))
        denominator = sum(r['known_printed_source_record_sum'] + (r['generic_source_record_sum'] if extra else 0) for r in ordered)
        total = 0
        cumulative = []
        crossing = None
        for i, row in enumerate(ordered, 1):
            value = row['known_printed_source_record_sum'] + (row['generic_source_record_sum'] if extra else 0)
            total += value
            cumulative.append(total)
            if crossing is None and 5 * total >= 4 * denominator:
                crossing = i
        claim = peer[name]
        keys = [r['unit_key'] for r in ordered]
        assert keys == claim['full_order']
        assert keys[:crossing] == claim['keys']
        assert claim['denominator'] == denominator == total
        assert claim['minimum_count'] == crossing
        assert claim['before_votes'] == cumulative[crossing-2]
        assert claim['crossing_votes'] == cumulative[crossing-1]
        assert 5 * cumulative[crossing-2] < 4 * denominator <= 5 * cumulative[crossing-1]
        scopes[name] = dict(denominator=denominator, full_count=len(keys),
                            minimum_count=crossing, preceding_votes=cumulative[crossing-2],
                            crossing_votes=cumulative[crossing-1], crossing_source_object=ordered[crossing-1],
                            top15_votes=cumulative[14], remainder_count=len(keys)-crossing,
                            remainder_votes=denominator-cumulative[crossing-1],
                            full_order=keys, full_cumulative_integer_votes=cumulative,
                            priority_keys=keys[:crossing], remainder_keys=keys[crossing:])
    out = dict(schema='IL-coordinator-original-printed-native-rank-review-v1',
               status='pass_exact_source_record_scope_only',
               original_pin='coordinator-native-category-source-pin.json',
               original_headers=headers, raw_rows=sum(len(v) for v in groups.values()),
               source_authorities=len({r['authority_ID'] for r in units}),
               complete_presentations=len(presentations),
               source_grouping='Original authority ID and literal precinct; complete container/category/name rows retained by source positions and complete original row digest. No physical precinct equivalence inferred.',
               producer_comparison=input_pin,
               all_source_groups=units, scopes=scopes,
               unknown_named_pool_contexts=[r['unit_key'] for r in units if r['named_pool_status'].startswith('unavailable')],
               absent_Kennedy_contexts=[r['unit_key'] for r in units if r['printed_candidate_cells'][printed[2]] is None and r['named_pool_status'].startswith('recorded')],
               nulls_not_imputed=True, valid_writein_allocation_approved=False,
               legal_valid_vote_80_membership_robustness=False,
               physical_precinct_count_approved=False, current_geography_approved=False,
               dispatch_acceptance=False,
               qualification='Empty known-record sums are arithmetic aggregates, never observed zero named candidate cells; generic source records are not adjudicated eligible write-ins. County17 is a separate sensitivity.')
    p = D / 'coordinator-printed-native-priority-review.json'
    data = json.dumps(out, indent=2, ensure_ascii=False, allow_nan=False).encode()+b'\n'
    p.write_bytes(data)
    print(json.dumps(dict(path=str(p.relative_to(D.parent)), bytes=len(data), sha256=sha(data),
                          scopes={k:{x:v[x] for x in ['denominator','minimum_count','preceding_votes','crossing_votes','top15_votes','remainder_count','remainder_votes']} for k,v in scopes.items()})))


if __name__ == '__main__':
    main()
