#!/usr/bin/env python3
"""Externally seal complete historical Colorado research scope, not current IDs."""
from pathlib import Path
from collections import Counter
import ast
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
    assert len(b) < 40000000
    return dict(path=str(p.relative_to(S)), bytes=len(b), sha256=sha(b))


def semantic(value):
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(',', ':'), allow_nan=False).encode())


def complete(p):
    result = pin(p)
    b = p.read_bytes()
    if p.suffix == '.gz':
        b = gzip.decompress(b)
        result.update(complete_reconstructed_bytes=len(b), complete_reconstructed_sha256=sha(b))
    name = p.name.removesuffix('.gz')
    if name.endswith('.json'):
        value = json.loads(b)
        result.update(full_semantic_sha256=semantic(value), semantic_type=type(value).__name__,
                      complete_length=len(value) if isinstance(value, (list, dict)) else None)
    elif name.endswith('.jsonl'):
        rows = [json.loads(line) for line in b.splitlines() if line]
        result.update(complete_rows=len(rows), full_semantic_sha256=semantic(rows))
    elif name.endswith('.csv'):
        rows = list(csv.reader(io.StringIO(b.decode())))
        result.update(complete_header=rows[0], complete_rows=len(rows) - 1, full_semantic_sha256=semantic(rows))
    result.update(complete_body_required=True, projection_or_subset_substitution=False)
    return result


def seals():
    result = []
    for root, report, county in [(T, 'turnout.md', 'county-turnout.csv'),
                                 (B, 'county-partisanship.md', 'county-baselines.csv')]:
        manifest = json.loads((root / 'asset-manifest.json').read_bytes())
        entries = manifest['assets']
        actual = {str(p.relative_to(S)) for p in root.rglob('*') if p.is_file() and p.name != 'asset-manifest.json'}
        actual |= {report, 'data/' + county}
        assert actual == {e['path'] for e in entries}
        for entry in entries:
            p = S / entry['path']
            assert pin(p) == {k: entry[k] for k in ['path', 'bytes', 'sha256']}
            if p.suffix == '.py':
                ast.parse(p.read_bytes())
        refs = manifest.get('referenced_originals', [])
        for entry in refs:
            p = S / entry['path']
            b = p.read_bytes()
            assert len(b) == entry['bytes'] < 40000000 and sha(b) == entry['sha256']
            if entry.get('raw_sha256'):
                raw = gzip.decompress(b)
                assert len(raw) == entry['raw_bytes'] and sha(raw) == entry['raw_sha256']
        if root == T:
            source_pins = json.loads((T / manifest['shared_originals'].split(';', 1)[0]).read_bytes())
            for entry in source_pins:
                p = (T / 'source' / entry['reference_path']).resolve()
                b = p.read_bytes()
                raw = gzip.decompress(b)
                assert len(b) < 40000000 and sha(b) == entry['stored_sha256']
                assert len(raw) == entry['bytes'] and sha(raw) == entry['raw_sha256']
            for entry in json.loads((T / manifest['shared_visuals'].split(';', 1)[0]).read_bytes()):
                p = S / entry['reference_path']
                b = p.read_bytes()
                assert len(b) == entry['bytes'] and sha(b) == entry['sha256']
            refs = source_pins
        assert not any(p.name in ['__pycache__', 'node_modules', '.pytest_cache'] for p in root.rglob('*'))
        result.append(dict(role=root.name, manifest=pin(root / 'asset-manifest.json'),
                           owned_entries=len(entries), read_only_original_references=len(refs),
                           exact_membership=True, all_hashes_sizes_verified=True))
    return result


def main():
    producer_seals = seals()
    cp = T / 'priority-set.json'
    c = json.loads(cp.read_bytes())
    assert pin(cp)['sha256'] == 'defa4fd873faffd60157def7cc99a6cb58a08b5a7c55ad04620c4d0efb53712a'
    assert cp.stat().st_size == 6319325 and len(c['full_order']) == 3199
    assert not c['formal_coordinator_acceptance'] and not c['current_geography_approved']
    assert len(c['ordered_priority_keys']) == 1992 and len(c['ordered_remainder_keys']) == 1207
    assert c['total'] == 3192745 and c['priority_votes'] == 2554233 and c['preceding_votes'] == 2553363
    review_names = ['coordinator-first-pair-source-review.json', 'coordinator-first-pair-target-review.json',
                    'coordinator-annotated-turnout-review.json']
    for name in review_names:
        assert json.loads((D / name).read_bytes())['status'].startswith('pass')
    source_review = json.loads((D / review_names[0]).read_bytes())
    companion_paths = [
        T / 'extracts/historical-source-rows.jsonl.gz', T / 'extracts/candidate-universes.json',
        T / 'extracts/public-historical-CSV-original-positions.jsonl.gz',
        T / 'extracts/2024-native-statistics.jsonl.gz', T / 'extracts/2024-workbook-footnotes-tail.json',
        T / 'extracts/2024-statistics-county-reconciliation.json', T / 'extracts/county-turnout-registration.json',
        T / 'extracts/county-administrative-controls.json', T / 'extracts/turnout-control-positions.jsonl.gz',
        T / 'extracts/independent-candidate-controls.jsonl.gz', T / 'source/montezuma-annotated-count-correction.json',
        T / 'source/shared-source-pins.json', T / 'source/visual-review.json',
        T / 'peer-comparison/proof-v1/OOXML-cell-position-map.jsonl.gz',
        T / 'peer-comparison/proof-v1/control-key-representations.json',
        T / 'peer-comparison/proof-v1/source-identity-clock-scope-map.json',
        B / 'source/historical-page-props.json', B / 'source/candidate-presentation.json',
        B / 'source/reused-originals.json', B / 'source/supplemental-originals.json',
        B / 'extracts/original-csv-records.jsonl.gz', B / 'extracts/all-candidate-votes.csv.gz',
        B / 'extracts/turnout-original-cells.jsonl.gz', B / 'extracts/turnout-control-positions.jsonl.gz',
        B / 'source/current-senate-roster.json', B / 'source/current-senate-spreadsheet-rows.json']
    companions = [complete(p) for p in companion_paths]
    objects = []
    for field in ['full_order', 'county_parents', 'county_native_hierarchy', 'csv_only_statistics_unavailable']:
        for i, value in enumerate(c[field]):
            objects.append(dict(file='data/turnout/priority-set.json', pointer=f'/{field}/{i}',
                                full_recursive_semantic_sha256=semantic(value)))
    historical_path = T / 'extracts/historical-source-rows.jsonl.gz'
    historical = [json.loads(line) for line in gzip.decompress(historical_path.read_bytes()).splitlines() if line]
    assert len(historical) == 9831
    for i, value in enumerate(historical):
        objects.append(dict(file=str(historical_path.relative_to(S)), JSONL_record=i + 1,
                            full_recursive_semantic_sha256=semantic(value), source_key=value['key']))
    maps = c['county_native_hierarchy']
    priority_parents = [p['county'] for p in maps if p['priority_native_keys']]
    remainder_maps = source_review['derived_ordered_remainder_child_keys_by_parent']
    fixed = ['turnout.md', 'county-partisanship.md', 'data/county-turnout.csv', 'data/county-baselines.csv',
             'data/turnout/asset-manifest.json', 'data/turnout/validation.json', 'data/turnout/peer-agreement.json',
             'data/turnout/turn-release.json', 'data/baselines/asset-manifest.json', 'data/baselines/validation.json',
             'data/baselines/handoff.json', 'data/baselines/peer-comparison/reconciliation.json',
             'data/baselines/priority-contract.json']
    output = dict(schema='CO-external-complete-historical-source-native-dispatch-v1',
                  status='accepted_complete_historical_source_native_research_dispatch_only', state='CO',
                  coordinator_agent_id='d0fc3534-1613-4883-b48b-21a233fcfd9e',
                  authority='External path alone authorizes the narrow historical research dispatch; use path-only '
                            'references in worker packages, no reverse acceptance hash or producer writes.',
                  frozen_contract=pin(cp), producer_seals=producer_seals,
                  frozen_first_pair_assets=[pin(S / p) for p in fixed],
                  independent_coordinator_reviews=[pin(D / p) for p in review_names],
                  primary_election='2024-11-05 President; Colorado had no2024Senate election',
                  source_geography='Actual public historical CSV source-native Precinct observations, not a current '
                                   'physical precinct, vote-center, ballot-style or method crosswalk',
                  source_candidate_denominator=3192745, top15_votes=39005,
                  minimum80=dict(count=1992, votes=2554233, preceding_count=1991, preceding_votes=2553363,
                                 crossing=c['crossing_key'], crossing_votes=870),
                  remainder=dict(count=1207, votes=638512), all_county_parents=64,
                  priority_county_parents=len(priority_parents), ordered_priority_parent_literals=priority_parents,
                  ordered_full_keys=[r['key'] for r in c['full_order']],
                  ordered_priority_keys=c['ordered_priority_keys'], ordered_remainder_keys=c['ordered_remainder_keys'],
                  complete_hierarchy_reference=dict(file=pin(cp), pointer='/county_native_hierarchy',
                                                    complete_recursive_semantics_required=True),
                  derived_ordered_remainder_child_keys_by_parent=remainder_maps,
                  remainder_map_qualification=source_review['parent_remainder_representation'],
                  complete_root_field_semantics=[dict(pointer='/' + k, full_recursive_semantic_sha256=semantic(v))
                                                  for k, v in c.items()],
                  complete_source_companion_files=companions, complete_source_object_references=objects,
                  separate_source_partitions=dict(Counter(str((r['year'], r['level_literal'])) for r in historical)),
                  complete_constituent_requirement='Preserve the entire pinned contract and every complete source '
                  'companion/header/party/pseudocandidate/native/admin/null/flag/clock/type/style/formula/sourceposition '
                  'object. Full raw original references and XML empty-cell supplements remain. Vote-only projections '
                  'and selected-only source subsets are insufficient.',
                  source_qualifications=[
                      '3199/3232/3205 historical native source scopes and all64 parents remain separate by year/contest. '
                      'County sensitivity rankings never replace the1992native order.',
                      'CSVTotalBallots duplicates candidate totals; sourcehasBallots false. It is not administrative '
                      'turnout, blank/under/over, received envelopes or an exact remaining pool.',
                      'Original statistics3183 source rows preserve eight annotated Montezuma shared strings and '
                      'relocation footnote. Annotated-inclusive active4074612/inactive-known508668/total4583280/ballots3241155 '
                      'are separate from numeric-only values; other blanks stay null, no residual allocation.',
                      'Sixteen explicit zero-candidate CSV-only contexts lack statistics; do not invent administrative '
                      'zeros.18 unvalued Dcells exist in the original and supplemental mapping; valued-only and sparse '
                      'derivatives are explicitly different presentations.',
                      '195 control-key/null representations differ across producers. Native source-position mapping '
                      'and complete original records agree; no silent geography alias or current identity follows.',
                      'All2020/2024 raw candidate isWriteIn flags false conflict with separately printed write-in labels; '
                      'literal flags and complete named candidate/party/pseudocandidate objects remain unchanged.',
                      'Current final official HTML/XLSX names9 Senate records including3write-ins; current live choice '
                      'keys, later changes and reporting/geographic crosswalks require separate authority.',
                      'Current rules/electronic UOCAVA presentation differences, complete later legal coverage, native '
                      'method splits/generic-invalid write-ins/blank-under-over and actual outstanding pools remain '
                      'qualified. Scenarios are conditional, not a2026 turnout forecast or probability.'
                  ],
                  dispatch_requirements=[
                      'Inventory state and all64county authorities, then investigate every priority parent with actual '
                      'requests/config/download/source chains. Preserve1992ordered shared-parent entry investigations '
                      'plus1207remainder and complete all64 hierarchy; precise finer-entry/access/current-ID gaps.',
                      'Acquire actual official/officially linked geographic assets for the1992priority observations. '
                      'Qualified shared-parent/Census references are acceptable with exact source/vintage/finer gaps, '
                      'never inferred leaf/legal/current matches.',
                      'Independently replay full frozen contract and companions/semantic references. Acceptance stays '
                      'path-only and producer false flags unchanged; no optional coordinator/current newsroom mutable '
                      'aggregate dependencies, vote-only projections, source allocation or finished-worker restart.'
                  ], current_geography_approved=False, current_November_returns_admitted=False,
                  current_result_IDs_approved=False, live_cadence_or_exact_remainder_approved=False,
                  collector_or_probability_approval=False)
    p = D / 'coordinator-priority-acceptance.json'
    b = (json.dumps(output, indent=2, ensure_ascii=False) + '\n').encode()
    assert len(b) < 40000000
    if p.exists():
        assert p.read_bytes() == b
    else:
        p.write_bytes(b)
    print(json.dumps(pin(p)))


if __name__ == '__main__':
    main()
