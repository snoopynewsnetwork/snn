"""External coordinator historical dispatch seal; producer false flags unchanged."""
from pathlib import Path
import csv
import gzip
import hashlib
import io
import json

D = Path(__file__).resolve().parent
S = D.parent
T = D / 'turnout'
B = D / 'baselines'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def pin(p):
    b = p.read_bytes()
    assert len(b) < 40_000_000
    return dict(path=str(p.relative_to(S)), bytes=len(b), sha256=sha(b))


def sem(v):
    return sha(json.dumps(v, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode())


def complete(p):
    value = pin(p)
    raw = p.read_bytes()
    if p.suffix == '.gz':
        raw = gzip.decompress(raw)
        value.update(complete_reconstructed_bytes=len(raw), complete_reconstructed_sha256=sha(raw))
    name = p.name.removesuffix('.gz')
    if name.endswith('.json'):
        obj = json.loads(raw)
    elif name.endswith('.jsonl'):
        obj = [json.loads(line) for line in raw.splitlines() if line]
    elif name.endswith('.csv'):
        obj = list(csv.reader(io.StringIO(raw.decode('utf-8-sig'))))
        value['complete_header'] = obj[0]
    else:
        obj = None
    if obj is not None:
        value.update(full_semantic_sha256=sem(obj), complete_length=len(obj), semantic_type=type(obj).__name__)
    value.update(complete_body_required=True, projection_or_subset_substitution=False)
    return value


def main():
    cp = T / 'priority-set.json'
    c = json.loads(cp.read_bytes())
    assert pin(cp) == dict(path='data/turnout/priority-set.json', bytes=2641537,
                           sha256='486c051146782d315d3866e65dda2db86a6ee1a6767b98d94486aa5bd7e195a6')
    assert c['formal_coordinator_acceptance'] is False and c['current_geography_approved'] is False
    assert (len(c['full_order']), len(c['ordered_priority_keys']), len(c['ordered_remainder_keys'])) == (530, 311, 219)
    assert (c['total'], c['top15_votes'], c['priority_votes'], c['preceding_votes'], c['crossing_votes'], c['remainder_votes']) == (500606, 35875, 400539, 399708, 831, 100067)
    review_names = ['coordinator-native-original-review.json', 'coordinator-structure-original-review.json',
                    'coordinator-first-pair-target-review.json', 'coordinator-first-pair-seal-review.json']
    reviews = [pin(D / p) for p in review_names]
    for name in review_names:
        assert json.loads((D / name).read_bytes())['status'].startswith('pass')
    frozen = []
    for root in [T, B]:
        mf = json.loads((root / 'asset-manifest.json').read_bytes())
        entries = mf['owned'] + mf['shared_originals'] if root == T else mf['assets']
        for e in entries:
            path = S / e['path'] if root == T else (root / e['path']).resolve()
            b = path.read_bytes()
            assert len(b) == e['bytes'] < 40_000_000 and sha(b) == e['sha256']
        frozen.append(pin(root / 'asset-manifest.json'))
    paths = [T / 'extracts' / name for name in [
        'candidate-rows.jsonl.gz', 'tables.json', 'native-inventory.json', 'state-controls.json',
        'county-controls.csv', 'reconciliation.json', 'native-coverage.json', 'historical-hierarchy.json',
        'historical-rankings.json', 'method-rankings.json', 'participation-totals.json',
        'participation-sensitivity.json', 'participation-checks.json', 'registration-november.json',
        'monthly-registration-controls.json', 'structure-2024.json', 'candidate-list-rows.json',
        'candidate-universe.json', 'writein-rows.json', 'writein-controls.json', 'source-references.json']]
    paths += [T / 'source/original-inputs.json', T / 'sample-ballot-identities.json']
    # The additional complete sample index is at the producer's declared location.
    if not paths[-1].exists():
        paths[-1] = T / 'extracts/sample-ballot-identities.json'
    paths += [B / name for name in [
        'extracted/contest-tables.json', 'extracted/table-inventory.json', 'extracted/candidate-geography.csv',
        'extracted/state-original-csv-rows.csv', 'extracted/candidate-method-controls.csv',
        'extracted/county-parent-evidence.json', 'extracted/participation-hierarchy.json',
        'extracted/resolved-parent-evidence.json', 'extracted/district-structure.json',
        'extracted/candidate-lists.json', 'extracted/writeins.csv', 'extracted/participation-totals.csv',
        'extracted/monthly-registration-original-rows.json', 'extracted/monthly-registration-native.csv',
        'extracted/monthly-registration-controls.csv', 'source/shared-sources.json',
        'source/control-disagreements.json', 'source/native-coverage-gaps.json', 'source/source-id-qualifications.json']]
    companions = [complete(p) for p in paths]
    objects = []
    for field in ['full_order', 'all_available_source_constituents', 'administrative_cases', 'unavailable_administrative_cases']:
        for i, v in enumerate(c[field]):
            objects.append(dict(file='data/turnout/priority-set.json', pointer=f'/{field}/{i}', full_recursive_semantic_sha256=sem(v)))
    for key, v in c['county_native_hierarchy'].items():
        objects.append(dict(file='data/turnout/priority-set.json', pointer='/county_native_hierarchy/' + key.replace('~', '~0').replace('/', '~1'), full_recursive_semantic_sha256=sem(v)))
    raw_rows = [json.loads(line) for line in gzip.decompress((T / 'extracts/candidate-rows.jsonl.gz').read_bytes()).splitlines()]
    assert len(raw_rows) == 10699
    for i, v in enumerate(raw_rows):
        objects.append(dict(file='data/turnout/extracts/candidate-rows.jsonl.gz', JSONL_record=i + 1, full_recursive_semantic_sha256=sem(v)))
    for relative in ['extracts/structure-2024.json', 'extracts/registration-november.json', 'extracts/participation-totals.json']:
        obj = json.loads((T / relative).read_bytes())
        entries = enumerate(obj) if isinstance(obj, list) else obj.items()
        for k, v in entries:
            objects.append(dict(file='data/turnout/' + relative, pointer='/' + str(k).replace('~', '~0').replace('/', '~1'), full_recursive_semantic_sha256=sem(v)))
    parents = c['county_native_hierarchy']
    priority = set(c['ordered_priority_keys'])
    remainder = set(c['ordered_remainder_keys'])
    order = c['ordered_priority_keys'] + c['ordered_remainder_keys']
    parent_children = {}
    for name, value in parents.items():
        children = value['ordered_senate_native_keys']
        parent_children[name] = dict(full=children, priority=[k for k in children if k in priority], remainder=[k for k in children if k in remainder])
    assert set(k for v in parent_children.values() for k in v['full']) == set(order)
    fixed = ['turnout.md', 'county-partisanship.md', 'data/county-turnout.csv', 'data/county-baselines.csv',
             'data/turnout/validation.json', 'data/baselines/validation.json', 'data/baselines/priority-contracts.json',
             'data/baselines/peer/reconciliation-v1.json', 'data/baselines/peer/ranking-reconciliation.json',
             'data/baselines/peer/supplement-reconciliation.json']
    result = dict(schema='DE-external-complete-historical-source-dispatch-v1', status='accepted_complete_historical_source_native_research_dispatch_only',
                  coordinator_agent_id='d0fc3534-1613-4883-b48b-21a233fcfd9e', state='DE',
                  authority='External path only supplies historical research dispatch authority. Do not reverse-pin acceptance in producer or worker packages or change producer false flags.',
                  frozen_contract=pin(cp), producer_seals=frozen, frozen_first_pair_assets=[pin(S / p) for p in fixed],
                  independent_coordinator_reviews=reviews, primary_election='2024-11-05 Senate, otherClassI;2020sameClassII retained separately',
                  source_candidate_denominator=500606, top15_votes=35875,
                  minimum80=dict(count=311, votes=400539, preceding_count=310, preceding_votes=399708, crossing=c['crossing_key'], crossing_votes=831),
                  remainder=dict(count=219, votes=100067), full_native=530, all_county_parents=3,
                  priority_county_parents=sum(bool(v['priority']) for v in parent_children.values()),
                  ordered_priority_parent_literals=[k for k, v in parent_children.items() if v['priority']],
                  ordered_full_keys=[r['native_key'] for r in c['full_order']], ordered_priority_keys=c['ordered_priority_keys'], ordered_remainder_keys=c['ordered_remainder_keys'],
                  complete_hierarchy_reference=dict(file=pin(cp), pointer='/county_native_hierarchy'),
                  derived_ordered_child_arrays_by_parent=parent_children,
                  parent_child_representation='Derived priority/remainder arrays filter each original ordered_senate_native_keys by the full original key sets, preserving order; no new producer field or physical join asserted.',
                  complete_root_field_semantics=[dict(pointer='/' + k, full_recursive_semantic_sha256=sem(v)) for k, v in c.items()],
                  complete_source_companion_files=companions, complete_source_object_references=objects,
                  source_partitions=dict(native_contest_scopes=[530, 533, 436, 439, 516], all_year_union=1495, current_structure_source_rows=537,
                                         selected_original_candidate_rows=10699, selected_original_tables=2674,
                                         named_writein_rows=43, participation_total_rows=1631, November_RD_rows=1477),
                  complete_constituent_requirement='Preserve complete contract/every root field/all source candidate/method/header/party/null/stat/admin/position bodies and full raw original references, not a vote-only or selected-only projection. All five contest/alternative-view partitions and historical parent exceptions remain.',
                  source_qualifications=[
                      '2024Senate530native500606 all3reported candidates;2024pres533/511697 plus separate1215write-ins,2020Sen436/490935,2020pres439/504010 plus336,2022actualHouse516/321649 plus18; no2022Sen/Gov invented.',
                      'Separate write-in source sheets lack ED allocation; generic/invalid/nonvote/cast-ballot fields unavailable, not0.2020native early fields null despite separate stateCSV0.2022write-in sheet literal2020heading conflicts actual2022date/clock.',
                      'County/RD/ED/Wilmington overlap; NewCastle includes Wilmington. Department state publication versus county-office/canvass authority remains. Methods are attributes, not central-board IDs.',
                      '537source structure rows/six statutory districts and533sample-index identities remain historical administrative evidence, not current physical polygons. Three2020pres-only county parents unknown including0218Biden1 remain statewide unallocated.',
                      'Results-header participation and November1registration sources differ in numerator/denominator/date/status/universe. Sparse party fields staynull; no residual allocation or remaining-ballot pool.',
                      'Current qualified/declared lists, signed/later legal/ballot scope, feed IDs/current boundaries/cadence/remainder and calibrated probabilities remain external qualifications. Historical full-source research is complete, not self-approval of those future identities.'
                  ],
                  dispatch_requirements=[
                      'Inventory state and all3county election offices/canvass authorities; deeply inspect every actual priority parent using original public chains/config/download/schema/clock/status/error evidence, preserve311ordered shared-parent investigations plus219remainder/all530 hierarchy.',
                      'Acquire actual official/linked geographic assets and a qualified full-state fallback; retain source/vintage/CRS/geometry/fullattributes/count/IDs/page checks. Shared-parent references may be qualified research evidence, never inferred leaf/current/legal matches.',
                      'Independently reconstruct full frozen originals/contract/companions/objects, with exact complete immutable references. Acceptance path-only; no mutable newsroom aggregates, optional unfinished coordinator/peer reviews or producer rewrites. No collector/count allocation/cadence/probability.'
                  ], current_geography_approved=False, current_November_returns_admitted=False,
                  current_choice_or_reporting_IDs_approved=False, live_cadence_or_exact_remainder_approved=False, collector_or_probability_approval=False)
    p = D / 'coordinator-priority-acceptance.json'
    value = (json.dumps(result, indent=2, ensure_ascii=False) + '\n').encode()
    assert len(value) < 40_000_000
    if p.exists():
        assert p.read_bytes() == value
    else:
        p.write_bytes(value)
    print(json.dumps(dict(**pin(p), companions=len(companions), complete_objects=len(objects), contract_fields=len(c))))


if __name__ == '__main__':
    main()
