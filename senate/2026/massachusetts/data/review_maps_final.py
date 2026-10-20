"""Coordinator read-only audit of the complete sealed historical map package."""
from pathlib import Path
import collections
import gzip
import hashlib
import io
import json
import subprocess

S = Path(__file__).resolve().parents[1]
M = S / 'maps'
N = 0


def ck(value, note=''):
    global N
    assert value, note
    N += 1


def read(path):
    return json.loads(path.read_bytes())


def digest(path):
    h = hashlib.sha256()
    size = 0
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''):
            h.update(b)
            size += len(b)
    return size, h.hexdigest()


def pin(path):
    size, sha = digest(path)
    return dict(path=str(path.relative_to(S)), bytes=size, sha256=sha)


class Parts(io.RawIOBase):
    def __init__(self, parts):
        self.parts = iter(parts)
        self.f = None

    def readable(self):
        return True

    def readinto(self, buffer):
        while True:
            if self.f is None:
                item = next(self.parts, None)
                if item is None:
                    return 0
                self.f = (M / item['path']).open('rb')
            n = self.f.readinto(buffer)
            if n:
                return n
            self.f.close()
            self.f = None


def main():
    mf_path = M / 'asset-manifest.json'
    mf = read(mf_path)
    ck(digest(mf_path) == (2299659, 'a087f2e7aa4493b7b30805a789df2482b7bf9e51ff0580839651cffbffc9da1d'))
    ck(mf['excludes_only'] == 'maps/asset-manifest.json')
    owned = mf['owned_assets']
    ck(len(owned) == 10155)
    expected = {r['path'] for r in owned}
    actual = {str(p.relative_to(S)) for p in M.rglob('*') if p.is_file() and p != mf_path}
    actual.add('precinct-maps.md')
    ck(len(expected) == len(owned) and actual == expected)
    for r in owned:
        p = S / r['path']
        ck(digest(p) == (r['bytes'], r['sha256']), r['path'])
        ck(r['bytes'] < 40000000 and '__pycache__' not in p.parts and p.suffix != '.pyc')
    for r in mf['readonly_inputs']:
        ck(digest(S / r['path']) == (r['bytes'], r['sha256']), r['path'])
    ck(len(mf['readonly_inputs']) == 807)
    print('all 10155 owned and 807 dependency pins verified', flush=True)
    c = read(S / 'data/turnout/priority-set.json')
    inv = read(M / 'inventory.json')
    full = [u['full_source_object'] for u in inv['units']]
    ck(full == c['all_unit_order'])
    ck(inv['priority'] == c['ordered_priority_keys'])
    ck(inv['remainder'] == c['ordered_remainder_keys'])
    ck(inv['source_parent_objects'] == c['all_parent_child_maps'])
    ck(inv['rank_order'] == inv['priority'] + inv['remainder'])
    ck(len(inv['parents']) == 351 and sum(p['in_priority'] for p in inv['parents']) == 287)
    ck(sum(u['votes'] for u in full) == 3407108)
    ck(sum(u['votes'] for u in full[:1469]) == 2725231)
    ck(sum(u['votes'] for u in full[:1470]) == 2726450)
    for u in inv['units']:
        ck(u['geometry_match'] is None and u['current_approved'] is False)
    seen = {}
    statuses = collections.Counter()
    receipts = sorted((M / 'receipts').glob('*.json'))
    for p in receipts:
        r = read(p)
        statuses[str(r.get('status'))] += 1
        ck(r['method'] == 'GET' and bool(r['requested_url']) and bool(r['retrieved_utc']))
        for x in r.get('exchanges', []):
            ck(all(k in x for k in ['request_url', 'request_headers', 'request_body', 'status', 'response_headers', 'parts', 'raw_bytes', 'raw_sha256']))
            if x['raw_sha256'] in seen:
                ck(seen[x['raw_sha256']] == x['raw_bytes'])
                continue
            for part in x['parts']:
                ck(digest(M / part['path']) == (part['bytes'], part['sha256']))
            h = hashlib.sha256()
            size = 0
            with io.BufferedReader(Parts(x['parts'])) as compressed:
                with gzip.GzipFile(fileobj=compressed) as f:
                    for b in iter(lambda: f.read(1048576), b''):
                        h.update(b)
                        size += len(b)
            ck((size, h.hexdigest()) == (x['raw_bytes'], x['raw_sha256']))
            seen[x['raw_sha256']] = size
    print('all complete original responses reconstructed', len(seen), flush=True)
    pdfs = read(M / 'pdf-index.json')
    ck(len(pdfs) == 508 and sum(p['page_count'] for p in pdfs) == 3526)
    for pdf in pdfs:
        ck(pdf['raw_sha256'] in seen)
        ck(pdf['page_count'] == len(pdf['pages']))
        for page in pdf['pages']:
            ck(page['automatically_rendered'] is True and (M / page['render']).is_file())
    visual = read(M / 'visual-review.json')
    ck(len(visual['PDF_pages_actually_viewed']) == 6)
    ck(len(visual['native_previews_actually_viewed']) == 4)
    native = read(M / 'native-audit.json')
    ck(len(native['wards']['features']) == 2256 and len(native['subprecinct']['features']) == 147)
    invalid = [dict(layer=k, object_id=f['object_id'], attributes=f['attributes'])
               for k in ['wards', 'subprecinct'] for f in native[k]['features'] if f.get('valid') is False]
    ck(len(invalid) == 2)
    atlas = subprocess.run(['node', str(M / 'test_atlas.cjs')], capture_output=True, text=True, check=True)
    atlas_result = json.loads(atlas.stdout)
    ck(atlas_result['status'] == 'pass' and atlas_result['fullobjects'] == 2394 and atlas_result['priority'] == 1470)
    seal = read(M / 'final-seal.json')
    for r in seal['pins']:
        ck(digest(S / r['path']) == (r['bytes'], r['sha256']))
    ck(seal['current_legal_result_geometry_approval'] is False)
    ck(read(M / 'validation.json')['status'] == 'pass' and read(M / 'replay.json')['status'] == 'pass')
    out = dict(status='pass_complete_independent_sealed_map_review', checks=N,
               manifest=pin(mf_path), owned_files=len(owned), readonly_dependencies=len(mf['readonly_inputs']),
               total_owned_bytes=sum(r['bytes'] for r in owned), maximum_owned_bytes=max(r['bytes'] for r in owned),
               original_receipts=len(receipts), unique_complete_raw_entities=len(seen), complete_raw_bytes=sum(seen.values()),
               receipt_status_counts=dict(statuses), PDFs=len(pdfs), automatically_rendered_pages=3526,
               worker_manual_visual_scope=dict(PDF_first_pages=6, native_previews=4),
               independently_verified_complete_source_objects=2394, priority=1470, remainder=924,
               all_parents=351, priority_parents=287, native_features=[2256,147], unrepaired_invalid_features=invalid,
               atlas=atlas_result, native_raw_position_proof=pin(S / 'data/coordinator-native-map-snapshot-review.json'),
               qualifications='Complete raw/schema/ring-position integrity and native diagnostics do not approve legal/current geometry, result-polygon equivalence, eligible-writein completeness or live data. All508PDFs were automatically rendered by producer; coordinator does not claim whole-package visual inspection. No originalSHP archive was acquired or independently audited. Incidental nonmap source/navigation bodies have no map/current credit.',
               producer_imports=False, producer_writes=False, current_or_legal_leaf_approval=False)
    p = S / 'data/coordinator-maps-final-review.json'
    p.write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps(dict(checks=N, proof=pin(p))))


if __name__ == '__main__':
    main()
