"""External immutable historical dispatch acceptance; never edit a worker freeze."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json

DATA = Path(__file__).resolve().parent
ROOT = DATA.parent


def pin(p):
    b = p.read_bytes()
    return dict(path=str(p.relative_to(ROOT)), bytes=len(b), sha256=hashlib.sha256(b).hexdigest())


def main():
    cp = DATA / 'turnout/priority-set.json'
    contract_pin = pin(cp)
    assert contract_pin == dict(path='data/turnout/priority-set.json', bytes=13065430, sha256='782ca7899236ba06e53effee549c4e6845f936c9b4ceea3fecc8828dd9a08c32')
    c = json.loads(cp.read_bytes())
    required = {
        'coordinator-finished-baseline-review.json': 'ca2bb7e33bde77e878b50d10ebd02a23caf63a4706602a31d5715e01d3278eab',
        'coordinator-finished-turnout-review.json': 'f3f04505de9ce3c24c917d5d1706897ec10a64565f291a4efc7518c189a62fef',
        'coordinator-final-named-peer-integration-review.json': '7ed367ff38cb6fcd950a910e05c66c24a08493941f6c418458dc2d7cd51fa50a',
        'coordinator-integrated-preferred82-all11-payload-review.json': '1d2be9c2467a3093deee4fc0bd15d6ac7c246e35ce7263051367f4aca72b50f0',
        'coordinator-historical-native-2020-104views-v1-review.json': '7b55b19ce583901f84e1d2bf8fa30e8fb1d10d04518aad880a0ecae38451a545',
        'coordinator-historical-native-2018-164views-v1-review.json': 'f14d8124795065129b66ae82cc296d31b344cfd5c9f4b0c11d03e082db67624b',
        'coordinator-worker-historical-full-peer-scope-review.json': '3891d4b30c4686bfe650cb79cea47ca63c83097a0b76485656da2a5aa41145eb',
        'coordinator-independent-2018-through43-review.json': '61749b4a661d6fec94570713fa25c11750768d530d8e53c8114f0eab0bbf7b83',
        'coordinator-turnout-native-2020-fortyfour-review.json': 'e431f5502babfe216b4f7f097169186d2e7ca86f574f01171411ea29ffc94d48',
        'coordinator-printed-field-source-inventory-review.json': '7bba5328602618c82cac3a9485ffd4feb47dec8333b8dc8777301ee6623a3355',
        'coordinator-union2024-split-style-review.json': 'a082e5e0319819af2e47f1b188d2e7ba79873e4ba86ca40bb5933450341ea367',
        'coordinator-native-2018-target-review.json': '9bddb6b7e7cb0679705bca1ca4aa60305ed97183eb3e82b8a00530a2393ca24d',
        'coordinator-historical-native-target-review.json': 'f95d7720e9f6a334d6785fdfa0c26fa41139eefe4625c04ec89239f56fef96cf',
    }
    reviews = []
    for name, expected in required.items():
        p = DATA / name
        a = pin(p)
        assert a['sha256'] == expected, name
        reviews.append(a)
    baseline = json.loads((DATA / 'coordinator-finished-baseline-review.json').read_bytes())
    turnout = json.loads((DATA / 'coordinator-finished-turnout-review.json').read_bytes())
    for review in (baseline, turnout):
        for key in ('owned_manifest', 'report', 'county_CSV', 'validation'):
            assert pin(ROOT / review[key]['path']) == review[key]
    assert not any(p.name == '__pycache__' or p.suffix in ('.pyc', '.pyo') for folder in ('turnout', 'baselines') for p in (DATA / folder).rglob('*'))
    assert c['priority_count'] == 887 and len(c['all_unit_order']) == 1736 and len(c['native_priority_by_parent']) == 82
    assert sum(bool(v) for v in c['native_priority_by_parent'].values()) == 77
    assert c['minimum80']['preceding_votes'] == 972157 and c['minimum80']['votes'] == 972656
    assert 5 * (972157 + 1) < 4 * 1215401 <= 5 * 972656
    assert c['current_2026_geographic_approval'] is False
    dependencies = [pin(DATA / 'turnout/source/2024-preferred-all11-source-fields-v1.json.gz'), pin(DATA / 'turnout/historical-native-complete-dependencies.json'), pin(DATA / 'baselines/source/native-priority-v2/snapshot.json'), pin(DATA / 'baselines/source/native-priority-v2-field-evidence-v1/snapshot.json')]
    p = DATA / 'coordinator-priority-acceptance.json'
    if p.exists():
        prior = json.loads(p.read_bytes())
        assert prior['contract'] == contract_pin and prior['independent_reviews'] == reviews and prior['complete_source_dependencies'] == dependencies and prior['accepted']
        print(json.dumps(pin(p)))
        return
    record = dict(
        status='accepted_historical_dispatch_only', accepted=True,
        accepted_at_utc=datetime.now(timezone.utc).isoformat(),
        coordinator_agent_id='d0fc3534-1613-4883-b48b-21a233fcfd9e',
        actual_finished_first_pair=dict(turnout='5d6e201c-4b06-46e7-9976-ae38ebf52676', partisanship='39cd2d0d-222c-4017-b21a-3b4f2cc54f67'),
        contract=contract_pin, independent_reviews=reviews,
        frozen_first_pair_reports=[baseline['report'], turnout['report']],
        frozen_first_pair_manifests=[baseline['owned_manifest'], turnout['owned_manifest']],
        frozen_first_pair_validations=[baseline['validation'], turnout['validation']],
        complete_source_dependencies=dependencies,
        authority='External coordinator historical research dispatch only. Frozen worker status/peer/current flags remain unchanged; no reverse acceptance hash or worker self-approval.',
        primary_unit_scope='Preferred82 actual2024SEMS source-native reporting columns, two named Senate candidates; source positions are not approved current physical/reporting units.',
        source_denominator=1215400, certified_named_denominator=1215401,
        source_candidate_sums={'Ty Pinkins':451980, 'Roger F. Wicker':763420},
        certified_candidate_sums={'Ty Pinkins':451981, 'Roger F. Wicker':763420},
        unallocated_Tunica_Pinkins_difference=1,
        top15_votes=60019, minimum80_count=887, minimum80_votes=972656, previous_votes=972157,
        source_integer80_threshold=972320, certified_integer80_threshold=972321,
        crossing=c['minimum80'], remainder_count=849, remainder_votes=242744,
        ordered_priority_keys=c['ordered_priority_keys'],
        ordered_priority=c['all_unit_order'][:887],
        full_native_count=1736, all_parent_counties=82, priority_parent_authorities=77,
        parent_all_native_keys_reference='data/baselines/native-priority-contract-v2.json:parent_all_native_keys',
        parent_priority_native_keys=c['native_priority_by_parent'],
        county_parent_sensitivity=dict(count=41, votes=979428, preceding40=970209, top15=653846, scope='sensitivity_only_not_primary_dispatch'),
        source_field_partitions=dict(preferred2024_columns=2266, preferred2024_named_or_null_positions=24926, alternative2024_source_views=84, native2020_publications=104, native2020_observations_across_versions=2131, selected2020_publications=82, selected2020_native=1765, native2018_distinct_stage_views=164, native2018_observations=3545, native2018_literal_X_positions=6),
        independent_historical_original_native_replay=dict(turnout2020_publications=44, turnout2018_stages=43, whole_independent_historical_native_replay=False, peer_reciprocal2020_publications=41, peer_reciprocal2018_stages=41),
        scope_limits=[
            'Accepted historical named-source concentration/scenario research with all source partitions preserved; not current2026 geography/reporting/candidate/method/ballot certification or approval.',
            'Tunica2024Pinkins andHarris source−1 each; Leflore2018Espy native5853vsprinted5863−10; all remain unallocated. No source repair or vote allocation.',
            'Historical2020original/amended and2018special/runoff are distinct source partitions; administrative and parallel rows are nonadditive, sixX numericalnull.',
            'Montgomery885ballots versus named4349Sen4424Pres remains incompatible; Union17058styleTotalVoters versus17084registration−26 is unresolved. Candidate pools/weights/targets unknown for all58styles even zeroTotalVoters rows.',
            'Generic marks do not establish eligible named write-ins; all unprinted fields remain unavailable. EAC/registration/method dates and definitions remain separate.',
            'All full104/164 canonical source objects are pinned dependencies; own independent original-native replay remains44/104and43/164 and is not relabeled complete.',
            'Current SAMPLE candidates, plurality chart and bounded legal sources do not establish final signed candidate universe, November feed IDs, complete later operative orders, current native crosswalks, exact outstanding votes or calibrated probabilities.',
            'Actual second-pair launch requires free finished slots and its own assignments. Acceptance does not mark official/maps work complete or publish the state.',
        ],
        current2026_geography_approved=False,
    )
    p.write_text(json.dumps(record, indent=2) + '\n')
    assert pin(cp) == contract_pin
    print(json.dumps(pin(p)))


if __name__ == '__main__':
    main()
