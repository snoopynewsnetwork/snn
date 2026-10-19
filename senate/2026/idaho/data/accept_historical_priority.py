#!/usr/bin/env python3
"""External source-only historical dispatch acceptance; producer files stay frozen."""
from collections import Counter
from pathlib import Path
import ast
import csv
import gzip
import hashlib
import io
import json

D = Path(__file__).resolve().parent
S = D.parent


def sha(b):
    return hashlib.sha256(b).hexdigest()


def pin(p):
    b = p.read_bytes()
    assert len(b) < 40000000
    return dict(path=str(p.relative_to(S)), bytes=len(b), sha256=sha(b))


def digest(value):
    return sha(json.dumps(value, sort_keys=True, ensure_ascii=False,
                          separators=(',', ':'), allow_nan=False).encode())


def complete_file(p):
    result = pin(p)
    b = p.read_bytes()
    if p.suffix == '.gz':
        b = gzip.decompress(b)
        result['reconstructed_complete_bytes'] = len(b)
        result['reconstructed_complete_sha256'] = sha(b)
    name = p.name.removesuffix('.gz')
    if name.endswith('.json'):
        value = json.loads(b)
        result.update(semantic_sha256=digest(value), semantic_type=type(value).__name__,
                      complete_top_level_length=len(value) if isinstance(value, (list, dict)) else None)
    elif name.endswith('.csv'):
        rows = list(csv.reader(io.StringIO(b.decode())))
        result.update(complete_header=rows[0], complete_rows=len(rows) - 1,
                      full_rows_semantic_sha256=digest(rows))
    result['complete_body_required'] = True
    result['projection_or_vote_only_substitute_allowed'] = False
    return result


def verify_seals():
    summary = []
    for role, report, county in [('turnout', 'turnout.md', 'county-turnout.csv'),
                                  ('baselines', 'county-partisanship.md', 'county-baselines.csv')]:
        root = D / role
        m = json.loads((root / 'asset-manifest.json').read_bytes())
        entries = m['owned_assets' if role == 'turnout' else 'owned']
        actual = {str(p.relative_to(S)) for p in root.rglob('*') if p.is_file() and p.name != 'asset-manifest.json'}
        actual |= {report, 'data/' + county}
        assert actual == {r['path'] for r in entries}
        for entry in entries:
            p = S / entry['path']
            assert pin(p) == {k: entry[k] for k in ['path', 'bytes', 'sha256']}
            if entry.get('reconstructed_sha256'):
                raw = gzip.decompress(p.read_bytes())
                assert sha(raw) == entry['reconstructed_sha256'] and len(raw) == entry['reconstructed_bytes']
            if p.suffix == '.py':
                ast.parse(p.read_bytes())
        refs = m.get('read_only_references', [])
        for entry in refs:
            p = (root / entry['path']).resolve()
            b = p.read_bytes()
            assert sha(b) == entry['stored_sha256'] and len(b) == entry['stored_bytes'] < 40000000
            if entry.get('raw_sha256'):
                raw = gzip.decompress(b)
                assert sha(raw) == entry['raw_sha256'] and len(raw) == entry['raw_bytes']
        assert not any(p.name in ['__pycache__', 'node_modules', '.pytest_cache'] for p in root.rglob('*'))
        summary.append(dict(role=role, owned=len(entries), read_only_references=len(refs),
                            exact_membership=True, all_hashes_verified=True, manifest=pin(root / 'asset-manifest.json')))
    return summary


def main():
    seals = verify_seals()
    contract_path = D / 'turnout/priority-set.json'
    contract_pin = pin(contract_path)
    assert contract_pin['bytes'] == 1668713 and contract_pin['sha256'] == '9bf413132cd591ac110ac1d88bc6d52f818679f6b28b33a0ca77e30c4d1e6676'
    c = json.loads(contract_path.read_bytes())
    assert not c['current_geography_approved'] and not c['priority_accepted']
    assert len(c['complete_order']) == 985 and len(c['ordered_priority_keys']) == 528
    assert len(c['ordered_remainder_keys']) == 457 and len(c['all_county_constituents']) == 44
    reviews = ['coordinator-initial-native-order-review.json', 'coordinator-first-pair-original-review.json',
               'coordinator-first-pair-target-review.json', 'coordinator-turnout-final-seal-review.json']
    for name in reviews:
        assert json.loads((D / name).read_bytes())['status'].startswith('pass')
    fixed = ['turnout.md', 'county-partisanship.md', 'data/county-turnout.csv', 'data/county-baselines.csv',
             'data/turnout/asset-manifest.json', 'data/turnout/validation.json',
             'data/turnout/peer-qa/comparison.json', 'data/turnout/peer-qa/peer-snapshot-manifest.json',
             'data/turnout/attribution-history/pre-repair-witness.json',
             'data/turnout/attribution-history/repair-proof.json',
             'data/baselines/asset-manifest.json', 'data/baselines/validation.json',
             'data/baselines/handoff.json', 'data/baselines/qa/peer-comparison.json',
             'data/baselines/priority-contract.json']
    companions = [D / 'turnout' / p for p in c['source_object_paths'].values()]
    companions += [D / 'baselines' / p for p in [
        'source/native-units.json.gz', 'source/controls.json.gz', 'source/candidate-positions.json.gz',
        'source/statistics-positions.json.gz', 'source/reused-originals.json',
        'source/additional-reused-originals.json', 'source/2022-writein-scope-disagreement.json',
        'source/independent-reference-receipts.json', 'source/2022-statistics-tables.json']]
    companion_pins = [complete_file(p) for p in dict.fromkeys(companions)]
    objects = []
    for i, parent in enumerate(c['all_county_constituents']):
        objects.append(dict(file=contract_pin['path'], pointer=f'/all_county_constituents/{i}',
                            semantic_sha256=digest(parent), role='complete_parent', source_key=parent['key']))
        for j, unit in enumerate(parent['president_contexts']):
            objects.append(dict(file=contract_pin['path'], pointer=f'/all_county_constituents/{i}/president_contexts/{j}',
                                semantic_sha256=digest(unit), role='complete_2024_source_native', source_key=unit['key']))
    historical = {}
    for name in ['historical-native.json.gz', 'historical-administrative-controls.json.gz']:
        path = D / 'turnout' / name
        data = json.loads(gzip.decompress(path.read_bytes()))
        historical[name] = dict(objects=len(data), by_contest_and_role=dict(Counter(
            str((u['year'], u['contest'], u['role'])) for u in data)))
        for i, unit in enumerate(data):
            objects.append(dict(file=str(path.relative_to(S)), pointer=f'/{i}', semantic_sha256=digest(unit),
                                role=unit['role'], source_key=unit['key']))
    primary = c['primary_priority']
    assert primary['denominator'] == 905057 and primary['minimum80_votes'] == 724515
    assert primary['preceding_votes'] == 723753 and primary['crossing_votes'] == 762
    assert primary['remainder_votes'] == 180542 and primary['top15_votes'] == 65391
    parents = [p for p in c['ordered_parent_keys'] if c['ordered_priority_child_keys_by_parent'][p]]
    assert len(parents) == 32
    output = dict(
        schema='ID-external-historical-source-native-dispatch-v1',
        status='accepted_complete_historical_source_native_research_dispatch_only', state='ID',
        coordinator_agent_id='d0fc3534-1613-4883-b48b-21a233fcfd9e',
        authority='This external path alone authorizes historical research dispatch. Reference it by path only; '
                  'producer flags remain false, no reverse acceptance hash or self-approval.',
        frozen_contract=contract_pin, frozen_first_pair_assets=[pin(S / p) for p in fixed],
        independent_coordinator_reviews=[pin(D / p) for p in reviews], producer_seals=seals,
        primary_election='2024-11-05 President; no 2024 federal Senate election in Idaho',
        geography='Actual source-native reporting observations, including administrative/absentee labels; '
                  'not an approved set of physical or November2026 precincts',
        source_candidate_universe=c['source_candidate_universe'], source_candidate_denominator=905057,
        noncandidate_categories=c['noncandidate_categories'],
        top15_votes=65391, minimum80=dict(count=528, votes=724515, preceding_count=527,
                                         preceding_votes=723753, crossing=primary['crossing_key'], crossing_votes=762),
        remainder=dict(count=457, votes=180542), all_county_parents=44, priority_county_parents=32,
        ordered_full_keys=[r['key'] for r in c['complete_order']], ordered_priority_keys=c['ordered_priority_keys'],
        ordered_remainder_keys=c['ordered_remainder_keys'], ordered_priority_parent_keys=parents,
        ordered_parent_keys=c['ordered_parent_keys'],
        ordered_child_keys_by_parent=c['ordered_child_keys_by_parent'],
        ordered_priority_child_keys_by_parent=c['ordered_priority_child_keys_by_parent'],
        ordered_remainder_child_keys_by_parent=c['ordered_remainder_child_keys_by_parent'],
        complete_root_field_semantics=[dict(pointer='/' + k, semantic_sha256=digest(v),
                                            complete_recursive_semantics_required=True) for k, v in c.items()],
        complete_source_companion_files=companion_pins,
        complete_source_object_references=objects, separate_historical_scopes=historical,
        complete_constituent_requirement='Preserve the entire pinned contract, all root fields, full parent/source objects '
                                       'and every complete companion body, including raw cell metadata, candidates, '
                                       'parties, methods, nulls, administrative/appendix controls, original receipts '
                                       'and unavailable fields. Vote-only projections or selected-only subsets are insufficient.',
        source_qualifications=[
            '2024 statistics986 versus presidential985 includes an explicitly all-zero Bingham/BONNEVILLE27 '
            'statistics-only record, not an inferred zero presidential observation.',
            'Seven Boundary literal race/stat pairs disagree: absentee stats0 versus race2721, geographic rows '
            'sum2724 extra stats ballots, net3 unallocated. Name matching is diagnostic, not scope/geometry approval.',
            'Original2020 native candidate nulls8 Senate/42 president and statistics nulls32/35/33/9 remain null '
            'despite known-sum closure. No null is filled from residual arithmetic.',
            '2022 HTML LisaMarie46 versus general governor named write-in67 is unexplained publication/scope '
            'disagreement. HTML stage is unknown; distinct actual primary22/21/6712 is not merged.',
            'Two statewide null statistics appendix headings and five lexical ABS flags have explicit peer '
            'representation differences. Six earlier tied order pairs are preserved as dated witnesses; canonical '
            'dispatch uses descending candidate total then lexical full source-position key.',
            'Bounded TwinFalls LD24 sample prints AchillesIND/FlemingIND/LoesbyLIB/RischREP; it does not establish '
            'signed statewide/later eligible write-in exhaustion, choice keys or current reporting IDs.',
            'Historical volume/participation/preference arithmetic, pair margins and full-field plurality tests '
            'remain conditional. No inferred candidate effect, current turnout forecast or calibrated probability.'
        ],
        source_scope_repair=c['source_scope_attribution_review'],
        dispatch_requirements=[
            'Inventory state and all44 official county authorities. Investigate32 priority parents with actual '
            'source requests and528 explicitly ordered shared-parent entry records; retain all457 remainder.',
            'Acquire actual official/officially linked maps and qualified alternatives for the528 ordered priorities. '
            'Shared-parent assets are valid research references only with precise finer-entry/access/vintage gaps.',
            'Retain the complete frozen contract and all companion/history/source objects through exact-byte '
            'references and full recursive semantic verification; no source-ID/name/count geographic joins.',
            'Acceptance is external and path-only in worker packages. No frozen producer writes or reverse hash. '
            'No further first-pair restart is required for current/legal/feed qualifications outside owned scope.'
        ],
        current_geography_approved=False, current_result_IDs_approved=False,
        current_November_returns_admitted=False, statewide_later_eligible_writein_exhaustion=False,
        live_cadence_or_exact_remainder_approved=False, collector_or_probability_approval=False)
    path = D / 'coordinator-priority-acceptance.json'
    encoded = (json.dumps(output, indent=2, ensure_ascii=False) + '\n').encode()
    assert len(encoded) < 40000000
    if path.exists():
        assert path.read_bytes() == encoded
    else:
        path.write_bytes(encoded)
    print(json.dumps(pin(path)))


if __name__ == '__main__':
    main()
