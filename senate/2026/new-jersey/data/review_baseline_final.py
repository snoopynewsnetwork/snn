"""Read-only final producer seal, originals, witnesses and review continuity."""
from pathlib import Path
import gzip
import hashlib
import json
import re

S = Path(__file__).resolve().parents[1]
B = S / 'data/baselines'
N = 0


def ck(v, note=''):
    global N
    assert v, note
    N += 1


def sha(b):
    return hashlib.sha256(b).hexdigest()


def read(p):
    return json.loads(p.read_bytes())


def pin(p):
    b = p.read_bytes()
    return dict(path=str(p.relative_to(S)), bytes=len(b), sha256=sha(b))


def exact(p, r):
    b = p.read_bytes()
    ck(len(b) == r['bytes'] and sha(b) == r['sha256'], str(p))
    ck(len(b) < 40000000, 'strict stored size')
    return b


def main():
    mf_path = B/'asset-manifest.json'
    ck(sha(mf_path.read_bytes()) == 'e8770b5e614530e0f9b99ef99894e5585428365655713279b3799eff919ff75a')
    mf = read(mf_path)
    files = mf['files']
    actual = {str(p.relative_to(S)) for p in B.rglob('*') if p.is_file() and p != mf_path}
    actual.update({'county-partisanship.md', 'data/county-baselines.csv'})
    ck(len(files) == len({r['path'] for r in files}) == 318)
    ck(actual == {r['path'] for r in files}, 'self only excluded from membership')
    for r in files:
        exact(S/r['path'], r)
    ck(not any(p.name in ('__pycache__', 'node_modules', '.venv', 'venv') for p in B.rglob('*')))
    refs = read(B/'source/original-references.json')
    ck(len(refs) == 417)
    full_bodies = 0
    for r in refs:
        if 'inherited_receipt_path' in r:
            ck(sha((B/'source'/r['inherited_receipt_path']).read_bytes()) == r['inherited_receipt_sha256'])
        if r.get('body_reference'):
            p = B/'source'/r['body_reference']
            z = p.read_bytes()
            ck(sha(z) == r['stored_sha256'] and len(z) == r['stored_bytes'] and len(z) < 40000000)
            raw = gzip.decompress(z) if p.suffix == '.gz' else z
            ck(sha(raw) == r['raw_sha256'] and len(raw) == r['raw_bytes'])
            full_bodies += 1
    new_receipts = 0
    for p in (B/'source').glob('*.receipt.json'):
        r = read(p)
        if r.get('asset'):
            z = (B/'source'/r['asset']).read_bytes()
            raw = gzip.decompress(z)
            ck(len(z) == r['stored_bytes'] and sha(z) == r['stored_sha256'])
            ck(len(raw) == r['raw_bytes'] and sha(raw) == r['raw_sha256'])
        else:
            ck('client_error' in r and 'status' not in r)
        new_receipts += 1
    witness = read(B/'source/pre-peer-witness.json')
    ck(sha((B/'source/pre-peer-witness.json').read_bytes()) == 'd8a93b13b137b8336b2bb47a0ab4373aff6ca5212363dbe76dbb8711137bfc40')
    ck(witness['peer_read'] is False)
    for r in witness['pins']:
        z = (B/r['frozen_body']).read_bytes()
        raw = gzip.decompress(z)
        ck(sha(z) == r['stored_sha256'] and sha(raw) == r['sha256'] and len(raw) == r['bytes'])
        exact(B/r['path'], r)
    finer = read(B/'source/finer-original-extraction-witness.json')
    for r in finer['files']:
        exact(B/'source/finer-first-bodies'/Path(r['path']).name, r)
    reproduction = read(B/'reproduction.json')
    ck(reproduction['pass'] and len(reproduction['steps']) == 8 and not reproduction['changed'])
    ck(reproduction['product_count'] == len(reproduction['exact_products']) == 232)
    for name, digest in reproduction['exact_products'].items():
        ck(sha((S/name).read_bytes()) == digest)
    validation = read(B/'validation.json')
    ck(validation['pass'] and validation['failed'] == 0 and validation['checks'] == 29315)
    ck(all(v['pass'] for v in validation['checks_detail']))
    seal = read(B/'finalseal.json')
    ck(seal['manifest_reverse_pin'] is None)
    for key, p in [('validation_sha256', B/'validation.json'), ('reproduction_sha256', B/'reproduction.json'),
                   ('core_witness_sha256', B/'source/pre-peer-witness.json'), ('report_sha256', S/'county-partisanship.md'),
                   ('county_csv_sha256', S/'data/county-baselines.csv'), ('priority_sha256', B/'priority-set.json'),
                   ('core_peer_comparison_sha256', B/'peer-comparison.json'), ('finer_peer_comparison_sha256', B/'peer-finer-comparison.json'),
                   ('source_reference_index_sha256', B/'source/original-references.json')]:
        ck(seal[key] == sha(p.read_bytes()), key)
    for key in ('coordinator_priority_accepted', 'current_reporting_geometry_approved',
                'statewide_eligible_write_in_allocation_verified', 'collector_implemented',
                'calibrated_probability', 'real2026_turnout_projection'):
        ck(seal[key] is False)
    core = read(S/'data/coordinator-baseline-core-review.json')
    for r in core['exact_current_core_pins']:
        exact(S/r['path'], r)
    math_review = read(S/'data/coordinator-first-pair-math-review.json')
    for r in math_review['exact_settings_and_outputs']:
        exact(S/r['path'], r)
    cli = read(S/'data/coordinator-live-input-review/review.json')
    exact(S/cli['calculator']['path'], cli['calculator'])
    ck(cli['cases'] == 33 and core['native_rows'] == 2296 and math_review['every_unit_rows'] == 8588)
    checked_links = 0
    for p in (S/'county-partisanship.md', B/'source/SCHEMA.md'):
        for link in re.findall(r'\]\(([^)]+)\)', p.read_text()):
            if link.startswith(('https:', 'http:', '#', 'mailto:')):
                continue
            ck((p.parent/link.strip('<>').split('#')[0]).resolve().exists(), link)
            checked_links += 1
    result = dict(status='pass_independent_final_baseline_seal_and_complete_original_continuity', checks=N,
                  owned_listed_entries=318, owned_files_including_manifest=319,
                  complete_original_reference_entries=len(refs), verified_original_full_body_entries=full_bodies,
                  new_original_receipts=new_receipts, original_first_witness_pins=len(witness['pins']),
                  finer_original_first_witness_pins=len(finer['files']), deterministic_rebuilt_products=232,
                  producer_readonly_sealed_validator_checks=29636, relative_links=checked_links,
                  final_pins=[pin(p) for p in (mf_path, B/'validation.json', B/'finalseal.json', B/'reproduction.json',
                                             S/'county-partisanship.md', S/'data/county-baselines.csv')],
                  independent_reviews=[pin(S/'data'/n) for n in ['coordinator-native-original-review.json',
                                       'coordinator-turnout-final-review.json', 'coordinator-baseline-core-review.json',
                                       'coordinator-first-pair-math-review.json', 'coordinator-live-input-review/review.json']],
                  qualifications='Known municipal/admin source575 rows, not finest statewide precinct/current geography or eligible writein completeness. Original/finer method/null/label/protected scopes nonadditive; Neptune/Somerset/Clerk/caption differences unallocated. Frozen reciprocal stable-core scope is distinct from later final producer files.',
                  producer_writes_or_imports=False, formal_coordinator_dispatch_accepted=False)
    p = S/'data/coordinator-baseline-final-review.json'
    p.write_text(json.dumps(result, indent=2)+'\n')
    print(dict(checks=N, exact_listed_owned=318, originals=len(refs), proof=pin(p)))


if __name__ == '__main__':
    main()
