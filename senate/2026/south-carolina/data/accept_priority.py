"""Record reviewed historical dispatch authority without approving current joins."""
import datetime
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONTRACT_HASH = 'a4dc8e50ce09889e5873d1f54c887dbef50a42a0b7bf600b4ab6663afab4ccef'


def pin(path):
    raw = path.read_bytes()
    return {'path': str(path.relative_to(HERE.parent)), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def main():
    contract_path = HERE / 'turnout/priority-set.json'
    contract_pin = pin(contract_path)
    assert contract_pin['sha256'] == CONTRACT_HASH
    # External authority is deliberately absent from the frozen contract hashes.
    contract = json.loads(contract_path.read_bytes())
    assert contract_pin['bytes'] == 33917555
    assert contract['coordinator_acceptance_path'] == 'data/coordinator-priority-acceptance.json'
    assert len(contract['counties']) == 46
    reviews = []
    for filename in ['coordinator-native-review.json', 'coordinator-legacy-review.json', 'coordinator-target-review.json', 'coordinator-original-target-review.json']:
        path = HERE / filename
        value = json.loads(path.read_bytes())
        assert value['status'].startswith('pass')
        if 'contract_sha256' in value:
            assert value['contract_sha256'] == CONTRACT_HASH
        reviews.append(pin(path))
    output = HERE / 'coordinator-priority-acceptance.json'
    if output.exists():
        record = json.loads(output.read_bytes())
        assert record['contract'] == contract_pin
        for witness in record['peer_witnesses']:
            assert pin(HERE.parent / witness['path']) == witness
        print('Existing immutable historical acceptance verified.')
        return
    snapshots = HERE / 'coordinator-witnesses'
    snapshots.mkdir(exist_ok=True)
    witnesses = []
    for source, name in [('turnout/peer-agreement.json', 'turnout-peer-agreement.json'),
                         ('baselines/peer-reconciliation.json', 'baselines-peer-reconciliation.json'),
                         ('baselines/peer-original-reconciliation.json', 'baselines-peer-original-reconciliation.json')]:
        path = HERE / source
        raw = path.read_bytes()
        witness = json.loads(raw)
        assert witness['status'].startswith('pass')
        for value in witness.get('evidence', {}).values():
            if isinstance(value, dict) and 'path' in value and 'sha256' in value:
                asset = path.parent / value['path']
                data = asset.read_bytes()
                assert hashlib.sha256(data).hexdigest() == value['sha256']
                assert len(data) == value['bytes']
        for field in ['input_hashes', 'peer_hashes']:
            for relative, expected in witness.get(field, {}).items():
                assert hashlib.sha256((HERE / relative).read_bytes()).hexdigest() == expected, relative
        assert path.read_bytes() == raw
        saved = snapshots / name
        assert not saved.exists()
        saved.write_bytes(raw)
        witnesses.append(pin(saved))
    priority = contract['counties'][:17]
    record = {
        'status': 'accepted_historical_dispatch_only', 'accepted': True,
        'accepted_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'coordinator_agent_id': 'd0fc3534-1613-4883-b48b-21a233fcfd9e',
        'contract': contract_pin, 'independent_reviews': reviews, 'peer_witnesses': witnesses,
        'actual_first_pair': {'turnout': '46dcb766-b312-4aaf-ac85-921179115c95', 'partisanship': '2a77ed30-c478-46c3-8980-817b50d4e679'},
        'denominator': 2548140, 'top15_votes': 1974167, 'minimum80_count': 17,
        'minimum80_votes': 2061601, 'previous_votes': 2019337, 'integer_threshold': 2038512,
        'crossing': {'county': 'Oconee', 'fips': '45073', 'votes': 42264},
        'remainder_count': 29, 'remainder_votes': 486539,
        'ordered_priority_keys': contract['priority_keys'],
        'ordered_priority': [{'county': c['name'], 'county_fips': c['county_fips'], 'geography_key': c['geography_key'], 'candidate_votes': c['candidate_votes']} for c in priority],
        'retained_scopes': {'database_hierarchy_objects': 9823, 'database_leaves': 9635,
                            'combined_ENR_JSON_leaves': 9635, 'XML_leaves': 9579,
                            'VHM_history_labels': 7078,
                            'Clarendon_2022': 'XML unavailable; enabled original TXT and separate combined JSON retained without gap imputation'},
        'scope_limits': ['Historical research dispatch only; no current source, physical boundary, method dictionary or cross-year/geographic approval.',
                         'Database, original XML/TXT, combined JSON, VHM and administrative aggregates overlap and are not added.',
                         'VHM requested-county/history labels have unresolved physical membership; raw null county and all original names/codes/counts survive.',
                         'Source candidate party differences, omitted Clerk rows, original-vs-database method values and registration residuals remain explicit.',
                         'Second-pair launch requires an actual free worker slot; this record neither launches agents nor declares any question package complete.']
    }
    output.write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps({'status': record['status'], 'contract': contract_pin, 'priority_count': len(priority), 'witnesses': len(witnesses)}, indent=2))


if __name__ == '__main__':
    main()
