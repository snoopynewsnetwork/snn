"""Independently rank frozen source-native units, never substitute parents."""
from pathlib import Path
import gzip
import hashlib
import json
import re
from collections import defaultdict

DATA = Path(__file__).resolve().parent
ROOT = DATA.parent
NAMES = ['Ty Pinkins','Roger F. Wicker']


def sha(b):
    return hashlib.sha256(b).hexdigest()


def pin(path):
    b = path.read_bytes()
    return {'path':str(path.relative_to(ROOT)),'bytes':len(b),'sha256':sha(b)}


def main():
    snapshot = DATA / 'turnout/qa/milestones/native-2024-84views/snapshot.json'
    source_pins = json.loads(snapshot.read_bytes())['pins']
    p = next(p for p in source_pins if p['path'].endswith('/native-constituents-reviewed.json.gz'))
    packed = (ROOT / p['path']).read_bytes()
    assert (len(packed),sha(packed)) == (p['bytes'],p['sha256'])
    units = json.loads(gzip.decompress(packed))
    native = [u for u in units if u['role'] == 'native_reporting_constituent']
    assert len(native) == 1779
    raw_path = DATA / 'turnout/native-source-orders.json'
    saved = DATA / 'coordinator-qa/native-source-orders-snapshot.json.gz'
    if not saved.exists():
        raw = raw_path.read_bytes()
        assert raw_path.read_bytes() == raw
        saved.write_bytes(gzip.compress(raw,mtime=0))
    evidence = json.loads(gzip.decompress(saved.read_bytes()))
    groups = defaultdict(list)
    for unit in native:
        groups[unit['source_id']].append(unit)
    assert len(groups) == 84 and set(groups) == set(evidence['source_views'])

    parsed_ID_additions = {}

    def verify(selected, expected):
        ordered = sorted(selected,key=lambda u:(-sum(u['candidate_votes'].values()),u['key']))
        total = sum(sum(u['candidate_votes'].values()) for u in ordered)
        assert expected['count'] == len(ordered) and expected['named_candidate_total'] == total
        assert len(expected['full_descending_order']) == len(ordered)
        cumulative = 0
        crossing = None
        for index,(u,row) in enumerate(zip(ordered,expected['full_descending_order']),1):
            votes = sum(u['candidate_votes'].values())
            cumulative += votes
            expected_ID = u['printed_native_id']
            if row['printed_native_id'] != expected_ID:
                assert expected_ID is None and isinstance(row['printed_native_id'],str)
                assert re.search(r'(?<![A-Za-z0-9])'+re.escape(row['printed_native_id'])+r'(?![A-Za-z0-9])',u['label_literal'])
                parsed_ID_additions[u['key']] = {'source_key':u['key'],'label_literal':u['label_literal'],
                    'frozen84_optional_ID':None,'order_optional_ID':row['printed_native_id']}
                expected_ID = row['printed_native_id']
            assert row == {'rank':index,'key':u['key'],'parent_county_fips':u['parent_county_fips'],
                           'source_id':u['source_id'],'source_page':u['source_page'],'source_column':u['source_column'],
                           'label_literal':u['label_literal'],'printed_native_id':expected_ID,
                           'candidate_votes':u['candidate_votes'],'named_candidate_votes':votes,'cumulative_votes':cumulative}
            if crossing is None and cumulative*5 >= total*4:
                crossing = {'count':index,'votes':cumulative,'preceding_count':index-1,
                            'preceding_votes':cumulative-votes,'crossing_key':u['key'],'crossing_votes':votes}
        assert crossing == expected['minimum80']
        assert expected['top15']['votes'] == sum(sum(u['candidate_votes'].values()) for u in ordered[:15])
        assert expected['candidate_sums'] == {n:sum(u['candidate_votes'][n] for u in ordered) for n in NAMES}
        assert expected['remainder'] == expected['full_descending_order'][crossing['count']:]
        assert expected['remainder_votes'] == total-crossing['votes']
        return ordered,crossing

    checks = []
    for sid,selected in sorted(groups.items()):
        ordered,crossing = verify(selected,evidence['source_views'][sid])
        checks.append({'source_id':sid,'source_native_count':len(ordered),
                       'source_named_votes':evidence['source_views'][sid]['named_candidate_total'],'minimum80':crossing})
    exclude = {'sos-2024-county-coahoma','sos-2024-county-pike'}
    selected = [u for u in native if u['source_id'] not in exclude]
    assert len(selected) == 1736 and len({u['parent_county_fips'] for u in selected}) == 82
    expected = evidence['preferred82_view']
    ordered,crossing = verify(selected,expected)
    assert crossing == {'count':887,'votes':972656,'preceding_count':886,'preceding_votes':972157,
                        'crossing_key':'28075:sos-2024-county-lauderdale:p9:c5','crossing_votes':499}
    assert expected['named_candidate_total'] == 1215400
    assert expected['top15']['votes'] == 60019 and expected['remainder_votes'] == 242744
    assert len(expected['remainder']) == 849
    boundary_votes = crossing['crossing_votes']
    tied = [u['key'] for u in ordered if sum(u['candidate_votes'].values()) == boundary_votes]
    chosen = {u['key'] for u in ordered[:887]}
    tunica = groups['sos-2024-county-tunica']
    largest_tunica = max(sum(u['candidate_votes'].values()) for u in tunica)
    assert largest_tunica == 394 and largest_tunica+1 < boundary_votes
    assert not chosen.intersection(u['key'] for u in tunica)
    assert len(parsed_ID_additions) == 43
    # These integer inequalities cover either denominator without placing the1.
    assert 5*(972157+1) < 4*1215400 and 5*(972157+1) < 4*1215401
    assert 5*972656 >= 4*1215401
    output = {
        'status':'pass_full1736_native_source_order_minimum887_with_unallocated_Tunica_gap',
        'frozen_source_unit_pin':p,'worker_order_snapshot':pin(saved),'all84_source_view_checks':checks,
        'preferred_native_units':1736,'parent_counties':82,'source_named_votes':1215400,
        'signed_county_named_votes':1215401,'unallocated_source_disagreement':{'Ty Pinkins':-1,'Roger F. Wicker':0},
        'top15_native_votes':60019,'source_top15_fraction':{'numerator':60019,'denominator':1215400},
        'separate_certified_denominator_fraction':{'numerator':60019,'denominator':1215401},
        'minimum80':crossing,'remaining_native_units':849,'remaining_source_votes':242744,
        'integer80_threshold_source':(4*1215400+4)//5,'integer80_threshold_certified':(4*1215401+4)//5,
        'source_order_tie_rule':'Descending named votes then ascending exact source-position key; no ordinal geography join.',
        'cutoff_tied_vote_count':boundary_votes,'cutoff_tied_keys':tied,
        'chosen_cutoff_tied_keys':[k for k in tied if k in chosen],
        '43_optional_ID_metadata_additions_after_frozen84':list(parsed_ID_additions.values()),
        'optional_ID_qualification':'These43 order metadata values are explicit substrings of unchanged source-literal headers; frozen84 null values stay unchanged. This audits extraction metadata only, not positive current identity, unique geography or any cross-source join.',
        'largest_Tunica_native_votes':largest_tunica,
        'one_vote_sensitivity':'Even adding the unlocated1 to the best886 gives972158 below both80% thresholds;887 source votes already exceed the certified threshold. All Tunica native counts are at most394, so a single missing vote placed in an existing Tunica unit or a new one-vote unit cannot reach the499 cutoff. No such placement is made. The selected prefix follows the declared deterministic sort; no uniqueness of all possible887-unit sets reaching80% is claimed.',
        'ordered887_keys':[u['key'] for u in ordered[:887]],
        'full1736_keys':[u['key'] for u in ordered],
        'county_parent_sensitivity_qualification':'The separate41-county prefix and its top15 share are not this native priority or a substitute source universe.',
        'scope':'This verifies all84 separate native-view orders and every preferred1736 native row from frozen original-read source objects. Alternative packets, TOTALs, blanks and Kemper parallel observations never enter the preferred sum. Proposed887 primary native dispatch is not yet coordinator accepted; remaining original-field gates and a coherent frozen contract remain required. Generic marks, current reporting/physical geography and historical joins are unapproved.'}
    (DATA / 'coordinator-native-order-review.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({k:output[k] for k in ['status','preferred_native_units','source_named_votes','top15_native_votes','minimum80','remaining_native_units','remaining_source_votes','cutoff_tied_keys']}))


if __name__ == '__main__':
    main()
