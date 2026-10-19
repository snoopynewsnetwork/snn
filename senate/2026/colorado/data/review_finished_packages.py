"""Coordinator-only replay of final source seals, raw schemas and map binaries.

No producer module is imported. Source files and sealed worker trees are read only.
"""
from pathlib import Path
from collections import Counter
from urllib.parse import urlsplit, parse_qs
import ast
import csv
import gzip
import hashlib
import io
import json
import struct
import zipfile
import zlib
import shapefile
from shapely.geometry import Polygon, MultiPolygon
from shapely.strtree import STRtree

D = Path(__file__).resolve().parent
S = D.parent
M = S / 'maps'
O = D / 'results-sources'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def pin(p):
    b = p.read_bytes()
    return dict(path=str(p.relative_to(S)), bytes=len(b), sha256=sha(b))


def read(p):
    b = p.read_bytes()
    return gzip.decompress(b) if p.suffix == '.gz' else b


def load(p):
    b = read(p)
    return [json.loads(x) for x in b.splitlines()] if '.jsonl' in p.name else json.loads(b)


def sem(x):
    return sha(json.dumps(x, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode())


def ptr(x, p):
    for k in p.split('/')[1:]:
        k = k.replace('~1', '/').replace('~0', '~')
        x = x[int(k)] if isinstance(x, list) else x[k]
    return x


def seal(root, manifest, owned_key, refs_key, extras, expected):
    mf = load(root / manifest)
    owned, refs = mf[owned_key], mf[refs_key]
    assert len(owned) == expected[0] and len(refs) == expected[1]
    for e in owned + refs:
        assert pin(S / e['path']) == {k: e[k] for k in ['path', 'bytes', 'sha256']}
        assert e['bytes'] < 40_000_000
    actual = {str(p.relative_to(S)) for p in root.rglob('*') if p.is_file()} | set(extras)
    assert actual == {x['path'] for x in owned} | {str((root / manifest).relative_to(S))}
    assert not any(p.name in ['__pycache__', '.venv', 'node_modules', '.pytest_cache'] for p in root.rglob('*'))
    for p in root.rglob('*.py'):
        ast.parse(p.read_bytes(), filename=str(p))
    return dict(manifest=pin(root / manifest), owned=len(owned), immutable_external=len(refs),
                owned_bytes=sum(e['bytes'] for e in owned), maximum_stored_bytes=max(e['bytes'] for e in owned + refs))


def official_body(e):
    if not e.get('body_path') and not e.get('body_parts'):
        assert e.get('error') and e['status'] is None
        return None
    if e.get('body_parts'):
        chunks = []
        for p in e['body_parts']:
            b = (S / p['path']).read_bytes()
            assert sha(b) == p['sha256'] and len(b) == p['bytes'] < 40_000_000
            chunks.append(b)
        b = b''.join(chunks)
    else:
        b = (S / e['body_path']).read_bytes()
    assert len(b) == e['stored_bytes'] and sha(b) == e['stored_sha256']
    raw = gzip.decompress(b)
    assert len(raw) == e['raw_bytes'] and sha(raw) == e['raw_sha256']
    encoding = next((v for k, v in e['headers'].items() if k.lower() == 'content-encoding'), '')
    if encoding.lower() == 'gzip':
        return gzip.decompress(raw)
    if encoding.lower() == 'deflate':
        return zlib.decompress(raw)
    return raw


def map_body(key):
    e = load(M / 'raw' / (key + '.receipt.json'))
    chunks = []
    for p in e.get('parts', []):
        b = (M / p['path']).read_bytes()
        assert len(b) == p['bytes'] < 40_000_000 and sha(b) == p['sha256']
        chunks.append(b)
    if chunks:
        raw = gzip.decompress(b''.join(chunks))
        assert len(raw) == e['raw_bytes'] and sha(raw) == e['raw_sha256']
    else:
        assert e['status'] is None and e.get('error')
        raw = b''
    return raw


def model(rings):
    # ESRI source rings: clockwise shells, counterclockwise holes. No repair.
    def area(r):
        return sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(r, r[1:]))
    shells = [r for r in rings if area(r) < 0]
    holes = [r for r in rings if area(r) >= 0]
    polys = [Polygon(r) for r in shells]
    attached = [[] for r in shells]
    for h in holes:
        candidates = [i for i, p in enumerate(polys) if p.covers(Polygon(h))]
        assert candidates, 'orphan hole: retain source, do not reinterpret'
        attached[min(candidates, key=lambda i: polys[i].area)].append(h)
    adapted = [Polygon(r, h) for r, h in zip(shells, attached)]
    return adapted[0] if len(adapted) == 1 else MultiPolygon(adapted)


def topology(features):
    models, keys, curves, invalid = [], [], [], []
    positions = 0
    for key, g in features:
        if 'curveRings' in g:
            curves.append(key)
            continue
        rings = g['rings']
        points = [p[:2] for r in rings for p in r]
        starts = []
        n = 0
        for r in rings:
            assert len(r) >= 4 and r[0][:2] == r[-1][:2]
            starts.append(n)
            n += len(r)
        adapted = shapefile.Shape(shapeType=5, points=points, parts=starts)
        assert list(adapted.points) == points and list(adapted.parts) == starts
        g2 = model([[p[:2] for p in r] for r in rings])
        if not g2.is_valid:
            invalid.append(key)
        models.append(g2)
        keys.append(key)
        positions += n
    tree = STRtree(models)
    pairs = []
    for i, g in enumerate(models):
        if not g.is_valid:
            continue
        for v in tree.query(g, predicate='intersects'):
            j = int(v)
            if j > i and models[j].is_valid:
                a = g.intersection(models[j]).area
                if a > 0:
                    pairs.append(dict(keys=[keys[i], keys[j]], native_area_squared=a))
    return dict(linear=len(models), original_XY_positions=positions, curves_excluded=curves, invalid=invalid,
                positive_area_pairs=pairs, legal_outline_or_current_crosswalk_approved=False)


def binary(key, expected_count, expected_xy):
    raw = map_body(key)
    z = zipfile.ZipFile(io.BytesIO(raw))
    assert z.testzip() is None
    names = z.namelist()
    shpname = next(n for n in names if n.lower().endswith('.shp'))
    stem = shpname[:-4]
    shp, shx, dbf = (z.read(stem + x) for x in ['.shp', '.shx', '.dbf'])
    assert struct.unpack_from('>i', shp, 0)[0] == 9994
    assert struct.unpack_from('>i', shp, 24)[0] * 2 == len(shp)
    assert struct.unpack_from('>i', shx, 24)[0] * 2 == len(shx)
    count = (len(shx) - 100) // 8
    assert count == expected_count == struct.unpack_from('<I', dbf, 4)[0]
    header, width = struct.unpack_from('<HH', dbf, 8)
    fields = []
    for at in range(32, header - 1, 32):
        v = dbf[at:at + 32]
        fields.append((v[:11].split(b'\0')[0].decode(), chr(v[11]), v[16], v[17]))
    reader = shapefile.Reader(shp=io.BytesIO(shp), shx=io.BytesIO(shx), dbf=io.BytesIO(dbf))
    assert fields == [tuple(v) for v in reader.fields[1:]]
    xy = 0
    digest = hashlib.sha256()
    field_digest = hashlib.sha256()
    for i in range(count):
        off, words = struct.unpack_from('>ii', shx, 100 + i * 8)
        assert struct.unpack_from('>ii', shp, off * 2) == (i + 1, words)
        p = shp[off * 2 + 8:off * 2 + 8 + words * 2]
        assert struct.unpack_from('<i', p, 0)[0] == 5
        nparts, npoints = struct.unpack_from('<ii', p, 36)
        parts = list(struct.unpack_from('<' + 'i' * nparts, p, 44))
        start = 44 + nparts * 4
        assert start + npoints * 16 == len(p)
        points = [struct.unpack_from('<dd', p, start + k * 16) for k in range(npoints)]
        shape = reader.shape(i)
        assert parts == list(shape.parts) and len(points) == len(shape.points)
        assert all(struct.pack('<dd', *a) == struct.pack('<dd', *b) for a, b in zip(points, shape.points))
        assert tuple(shape.bbox) == struct.unpack_from('<dddd', p, 4)
        adapted = shapefile.Shape(shapeType=5, points=points, parts=parts)
        assert list(adapted.parts) == parts and list(adapted.points) == points
        row = dbf[header + i * width:header + (i + 1) * width]
        assert row[0] == 32
        values = []
        at = 1
        for name, kind, size, decimals in fields:
            b = row[at:at + size]
            v = b.decode('utf-8').strip(' \0')
            values.append((float(v) if decimals else int(v)) if kind in 'NF' and v else v)
            at += size
        assert values == list(reader.record(i)) and at == width
        digest.update(p[start:])
        field_digest.update(row)
        xy += npoints
    assert xy == expected_xy
    return dict(source=key, records=count, original_XY=xy, XY_raw_double_sha256=digest.hexdigest(),
                complete_DBF_bytes_sha256=field_digest.hexdigest(), fields=fields,
                zip_members=[dict(name=n, bytes=z.getinfo(n).file_size, crc=z.getinfo(n).CRC, sha256=sha(z.read(n))) for n in names],
                every_original_XY_bit_pattern_part_offset_bbox_and_attribute_replayed=True,
                pyshp_version=shapefile.__version__, constructor='points/parts; no implicit closure')


def main():
    assert pin(O / 'asset-manifest.json')['sha256'] == 'ceabc928bfe4eca20befc6f23be7c1e4fa65998b56b53655409d8e303b15df21'
    official = seal(O, 'asset-manifest.json', 'assets', 'immutable_external_files',
                    ['official-results.md', 'data/official-results-sources.csv'], (714, 82))
    maps = seal(M, 'asset-manifest.json', 'owned_files', 'read_only_dependencies', ['precinct-maps.md'], (749, 64))
    contract = load(D / 'turnout/priority-set.json')
    acceptance = load(D / 'coordinator-priority-acceptance.json')
    assert pin(D / 'coordinator-priority-acceptance.json')['sha256'] == '6560fcb3d90c26cb34a9b8c3037685b438b88e6a27cb4eec617b45c1cebb8b35'
    graph = load(O / 'historical-conservation.json.gz')
    assert len(graph['root_fields']) == len(contract) == 36
    for e in graph['root_fields']:
        assert sem(ptr(contract, e['pointer'])) == e['full_recursive_semantic_sha256']
    assert len(graph['complete_companions']) == 26
    assert [e['path'] for e in graph['complete_companions']] == [e['path'] for e in acceptance['complete_source_companion_files']]
    cache = {'data/turnout/priority-set.json': contract}
    for e in graph['complete_source_object_references']:
        if e['file'] not in cache:
            cache[e['file']] = load(S / e['file'])
        value = cache[e['file']][e['JSONL_record'] - 1] if 'JSONL_record' in e else ptr(cache[e['file']], e['pointer'])
        assert sem(value) == e['full_recursive_semantic_sha256']
    assert len(graph['complete_source_object_references']) == 13174
    receipts = load(O / 'acquisition.json')
    assert len(receipts) == 866 and len({e['id'] for e in receipts}) == 866
    status = Counter()
    bodies = {}
    for e in receipts:
        assert e['method'] == 'GET' and e['retrieved_utc'] and 'headers' in e and 'redirects' in e
        bodies[e['id']] = official_body(e)
        status[e['status']] += 1
    assert status == Counter({200: 817, 403: 11, 404: 36, None: 2})
    objects = load(O / 'response-objects.json.gz')
    for key, obj in objects.items():
        if '#__NEXT_DATA__' not in key:
            assert json.loads(bodies[key]) == obj
    denver = json.loads(bodies['denver-november-payload'])
    assert len(denver['Races']) == len(denver['Results']) == 68
    senate = next(x for x in denver['Results'] if x['RaceID'] == 1)
    assert senate['RaceTitle'] == 'United States Senator'
    assert [v['CandidateName'] for v in senate['CandidateVotes']] == ['Mark Baisley', 'John Hickenlooper', 'Bob Chew', 'Christopher Baum', 'Blake Huber', 'Adam Withrow', 'Write-in']
    assert all(x['Votes'] == 0 for r in denver['Results'] for x in r['CandidateVotes'])
    assert denver['WriteIns'] == denver['PrintableResults'] == [] and len(denver['VoterRegistrationInfo']) == 5
    assert all(senate[k] == 0 for k in ['TotalVotes', 'UnderVotes', 'OverVotes'])
    packets = load(O / 'priority-parent-primary-packets.json.gz')
    assert list(packets) == acceptance['ordered_priority_parent_literals'] and len(packets) == 45
    for county, packet in packets.items():
        for e in packet['complete_responses'].values():
            assert sem(json.loads(bodies[e['receipt']])) == e['full_recursive_semantic_sha256']
    rows = load(O / 'priority-investigations.jsonl.gz')
    assert [e['key'] for e in rows] == acceptance['ordered_priority_keys']
    assert all(e['current_admission'] is False and e['current_November_native_id'] is None for e in rows)
    map_receipts = [load(p) for p in sorted((M / 'raw').glob('*.receipt.json'))]
    for e in map_receipts:
        map_body(e['id'])
    assert len(map_receipts) == 186
    inventory = load(M / 'inventory.json')
    assert inventory['ordered_priority_keys'] == acceptance['ordered_priority_keys']
    assert inventory['ordered_remainder_keys'] == acceptance['ordered_remainder_keys']
    assert [e['key'] for e in inventory['all3199']] == acceptance['ordered_full_keys']
    for e in inventory['all3199']:
        assert e['leaf_geometry_match'] is False and e['current_legal_match'] is False
    service_results = []
    for f in sorted((M / 'raw').glob('*.service.json')):
        e = load(f)
        key = e['id']
        meta = json.loads(map_body(key + '-meta-pre'))
        assert meta == json.loads(map_body(key + '-meta-post'))
        ids = json.loads(map_body(key + '-ids-pre'))
        assert ids == json.loads(map_body(key + '-ids-post'))
        count = json.loads(map_body(key + '-count-pre'))
        assert count == json.loads(map_body(key + '-count-post'))
        assert count['count'] == len(ids['objectIds']) == e['count']
        fields = [x['name'] for x in meta['fields']]
        found, geometries = [], []
        for page in e['pages']:
            receipt = load(M / 'raw' / (page + '.receipt.json'))
            params = parse_qs(urlsplit(receipt['url']).query)
            wanted = list(map(int, params['objectIds'][0].split(',')))
            assert len(wanted) <= 50
            assert not set(params) & {'outSR', 'geometryPrecision', 'maxAllowableOffset', 'quantizationParameters', 'resultRecordCount'}
            assert all(params[k] == ['true'] for k in ['returnGeometry', 'returnZ', 'returnM', 'returnTrueCurves'])
            assert params['outFields'] == ['*']
            obj = json.loads(map_body(page))
            assert not obj.get('exceededTransferLimit', False)
            got = [x['attributes'][ids['objectIdFieldName']] for x in obj['features']]
            assert set(got) == set(wanted) and len(got) == len(wanted)
            found += got
            for feature in obj['features']:
                assert set(feature['attributes']) == set(fields)
                geometries.append((feature['attributes'][ids['objectIdFieldName']], feature['geometry']))
        assert set(found) == set(ids['objectIds']) and len(found) == len(set(found))
        service_results.append(dict(source=key, features=len(found), all_attributes_fields=meta['fields'],
                                    full_native_feature_semantic_sha256=sem(geometries), topology=topology(geometries)))
    assert [x['features'] for x in service_results] == [283, 8, 216, 20]
    assert len(service_results[0]['topology']['curves_excluded']) == 49
    binary_results = [binary('census-co-vtd', 3108, 1283644), binary('county-fremont-map-1-asset-1', 20, 27642)]
    result = dict(status='pass_independent_coordinator_finished_official_and_map_original_review',
                  official_seal=official, map_seal=maps, complete_contract_fields=36, companions=26, recursive_full_objects=13174,
                  official_acquisitions=866, official_statuses={str(k): v for k, v in status.items()},
                  complete_original_JSON_or_SSR_objects=len(objects), complete_primary_parent_packets=45,
                  denver_complete_original_pin=next({k: x[k] for k in ['url', 'raw_bytes', 'raw_sha256']} for x in receipts if x['id'] == 'denver-november-payload'),
                  denver_Senate_setup=senate, map_receipts=len(map_receipts), native_services=service_results,
                  original_binary= binary_results, priority=1992, inventory=3199, remainder=1207, full_parents=64,
                  current_geography_or_choice_ID_or_genuine_returns_approved=False,
                  limitations='Shared-parent source/map references; original curves and source vintages retained; native intersections are diagnostics only, no legal same-vintage outline or leaf join.')
    target = D / 'coordinator-finished-packages-review.json'
    value = (json.dumps(result, indent=2) + '\n').encode()
    if target.exists():
        assert target.read_bytes() == value
    else:
        target.write_bytes(value)
    print(json.dumps(pin(target)))


if __name__ == '__main__':
    main()
