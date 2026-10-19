"""Producer-free final map seal, full source and Cassia binary replay."""
from pathlib import Path
from collections import Counter
import ast
import gzip
import hashlib
import io
import json
import struct
import zipfile
import shapefile
from shapely.geometry import Polygon, MultiPolygon
from shapely.strtree import STRtree

D = Path(__file__).resolve().parent
S = D.parent
M = S / 'maps'


def sha(value):
    return hashlib.sha256(value).hexdigest()


def load(path):
    value = path.read_bytes()
    return json.loads(gzip.decompress(value) if path.suffix == '.gz' else value)


def pin(path):
    value = path.read_bytes()
    return dict(path=str(path.relative_to(S)), bytes=len(value), sha256=sha(value))


def semantic(value):
    return sha(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode())


def pointer(value, path):
    for key in path.split('/')[1:]:
        key = key.replace('~1', '/').replace('~0', '~')
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value


def body(entry):
    def part(value):
        stored = (S / value['stored_path']).read_bytes()
        assert sha(stored) == value['stored_sha256'] and len(stored) == value['stored_bytes'] < 40_000_000
        return gzip.decompress(stored) if value['stored_path'].endswith('.gz') else stored
    if 'stored_parts' in entry:
        chunks = []
        offset = 0
        for item in entry['stored_parts']:
            assert item['offset'] == offset
            raw = part(item)
            assert sha(raw) == item['raw_sha256'] and len(raw) == item['raw_bytes']
            chunks.append(raw)
            offset += len(raw)
        raw = b''.join(chunks)
    else:
        raw = part(entry)
    assert sha(raw) == entry['raw_sha256'] and len(raw) == entry['raw_bytes']
    return raw


def cassia(raw):
    archive = zipfile.ZipFile(io.BytesIO(raw))
    assert archive.testzip() is None and len(archive.namelist()) == 8
    members = {Path(n).suffix: archive.read(n) for n in archive.namelist()}
    shp, shx, dbf = (members[x] for x in ['.shp', '.shx', '.dbf'])
    assert struct.unpack('>i', shp[:4])[0] == 9994
    assert struct.unpack('>i', shp[24:28])[0] * 2 == len(shp)
    assert struct.unpack('<ii', shp[28:36]) == (1000, 5)
    assert struct.unpack('>i', shx[24:28])[0] * 2 == len(shx)
    count = (len(shx) - 100) // 8
    assert count == 24
    dbf_count = struct.unpack_from('<I', dbf, 4)[0]
    header_size, record_size = struct.unpack_from('<HH', dbf, 8)
    assert dbf_count == count and dbf[header_size - 1] == 13
    fields = []
    for at in range(32, header_size - 1, 32):
        descriptor = dbf[at:at + 32]
        fields.append(dict(name=descriptor[:11].split(b'\0')[0].decode(), type=chr(descriptor[11]), length=descriptor[16], decimals=descriptor[17]))
    reader = shapefile.Reader(shp=io.BytesIO(shp), shx=io.BytesIO(shx), dbf=io.BytesIO(dbf))
    assert len(reader) == count
    assert [(x['name'], x['type'], x['length'], x['decimals']) for x in fields] == [tuple(x) for x in reader.fields[1:]]
    position_digest = hashlib.sha256()
    positions = 0
    models = []
    records = []
    for i in range(count):
        offset, words = struct.unpack_from('>ii', shx, 100 + i * 8)
        record_number, content_words = struct.unpack_from('>ii', shp, offset * 2)
        assert record_number == i + 1 and content_words == words
        payload = shp[offset * 2 + 8:offset * 2 + 8 + words * 2]
        assert struct.unpack_from('<i', payload)[0] == 5
        n_parts, n_points = struct.unpack_from('<ii', payload, 36)
        parts = list(struct.unpack_from('<' + 'i' * n_parts, payload, 44))
        start = 44 + 4 * n_parts
        assert start + n_points * 16 == len(payload)
        points = [struct.unpack_from('<dd', payload, start + j * 16) for j in range(n_points)]
        parsed = reader.shape(i)
        assert list(parsed.parts) == parts and len(parsed.points) == n_points
        assert all(struct.pack('<dd', *a) == struct.pack('<dd', *b) for a, b in zip(points, parsed.points))
        reconstructed = shapefile.Shape(shapeType=5, points=points, parts=parts)
        assert list(reconstructed.parts) == parts and list(reconstructed.points) == points
        position_digest.update(payload[start:])
        positions += n_points
        record = dbf[header_size + i * record_size:header_size + (i + 1) * record_size]
        assert record[:1] == b' '
        values = []
        at = 1
        for field in fields:
            chunk = record[at:at + field['length']]
            assert field['type'] == 'C'
            values.append(chunk.decode().rstrip(' \0'))
            at += field['length']
        assert at == record_size and values == list(reader.record(i))
        assert list(struct.unpack_from('<dddd', payload, 4)) == list(parsed.bbox)
        rings = [points[a:b] for a, b in zip(parts, parts[1:] + [n_points])]
        assert all(len(r) >= 4 and r[0] == r[-1] for r in rings)
        signed = lambda r: sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(r, r[1:]))
        shells = [r for r in rings if signed(r) < 0]
        holes = [r for r in rings if signed(r) >= 0]
        polygons = [Polygon(r) for r in shells]
        attached = [[] for _ in shells]
        for hole in holes:
            candidates = [j for j, p in enumerate(polygons) if p.covers(Polygon(hole))]
            assert candidates
            attached[min(candidates, key=lambda j: polygons[j].area)].append(hole)
        adapted = [Polygon(r, h) for r, h in zip(shells, attached)]
        model = adapted[0] if len(adapted) == 1 else MultiPolygon(adapted)
        assert model.is_valid and not model.is_empty
        models.append(model)
        records.append(dict(record=i + 1, attributes=dict(zip([x['name'] for x in fields], values)), raw_record_sha256=sha(record), parts=parts, points=n_points))
    assert positions == 17319
    tree = STRtree(models)
    pairs = []
    for i, model in enumerate(models):
        for found in tree.query(model, predicate='intersects'):
            j = int(found)
            if j > i:
                area = model.intersection(models[j]).area
                if area > 0:
                    pairs.append(dict(records=[i + 1, j + 1], native_area_square_US_survey_feet=area))
    assert len(pairs) == 34
    return dict(records=records, dbf_fields=fields, original_XY_positions=positions, original_XY_bytes_sha256=position_digest.hexdigest(),
                all_original_XY_parts_offsets_attributes_and_bboxes_replayed=True, pyshp_version=shapefile.__version__,
                points_parts_constructor_preserves_source=True, invalid=0, native_positive_area_pairs=pairs,
                complete_members=[dict(name=n, bytes=len(archive.read(n)), sha256=sha(archive.read(n))) for n in archive.namelist()])


def main():
    manifest = load(M / 'manifest.json')
    assert pin(M / 'manifest.json')['sha256'] == 'b47655e01297dba9922d5ef64816182ea29543e738b2f110db72e33ee42eabe2'
    owned = manifest['owned']
    references = load(M / 'frozen-references.json')['references']
    assert len(owned) == 1632 and len(references) == 204
    for item in owned + references:
        assert pin(S / item['path']) == {k: item[k] for k in ['path', 'bytes', 'sha256']}
        assert item['bytes'] < 40_000_000
    assert {str(p.relative_to(S)) for p in M.rglob('*') if p.is_file()} | {'precinct-maps.md'} == {x['path'] for x in owned} | {'maps/manifest.json'}
    assert not any(x['path'].endswith('news/manifest.json') for x in references)
    for entry in load(M / 'source/frozen-reference-overrides.json')['overrides']:
        stored = (S / entry['stored_path']).read_bytes()
        assert sha(stored) == entry['stored_sha256'] and len(stored) == entry['stored_bytes']
        original = gzip.decompress(stored)
        assert sha(original) == entry['original_sha256'] and len(original) == entry['original_bytes']
    receipts = [load(p) for p in sorted((M / 'source').glob('*.receipt.json')) if not p.name.startswith('native-')]
    assert len(receipts) == 500
    status = Counter()
    for entry in receipts:
        raw = body(entry)
        status[entry['status']] += 1
        assert entry['retrieved_utc'] and entry['method'] == 'GET' and 'headers' in entry and 'redirects' in entry
    assert status == Counter({200: 469, 403: 12, 404: 17, 405: 2})
    contract = load(D / 'turnout/priority-set.json')
    inventory = load(M / 'inventory.json')
    for name in ['ordered_parent_keys', 'ordered_priority_keys', 'ordered_remainder_keys']:
        assert inventory[name] == contract[name]
    assert inventory['ordered_full_keys'] == [x['key'] for x in contract['complete_order']]
    assert len(inventory['observations']) == 985 and len(inventory['parents']) == 44
    assert inventory['current_geography_approved'] is False
    parents = {x['key']: x for x in inventory['parents']}
    assert sum(bool(x['priority_children']) for x in parents.values()) == 32
    for entry in inventory['observations']:
        ref = entry['source_complete_object']
        assert semantic(pointer(contract, ref['pointer'])) == ref['semantic_sha256']
        assert entry['resource_ids'] == parents[entry['parent_key']]['acquired_resource_ids']
        assert entry['matched_native_feature_ids'] is None
    for path in M.rglob('*.py'):
        ast.parse(path.read_bytes(), filename=str(path))
    assert not any(p.name in ['__pycache__', 'node_modules', '.venv', '.pytest_cache'] for p in M.rglob('*'))
    z = next(x for x in receipts if x['id'] == 'additional-16031-map-0-20')
    binary = cassia(body(z))
    result = dict(status='pass_independent_finished_map_seal_and_original_binary_review', manifest=pin(M / 'manifest.json'),
                  exact_owned=1632, immutable_external=204, full_source_native=985, priority=528, remainder=457, parents=44,
                  actual_HTTP_receipts=500, HTTP_statuses={str(k): v for k, v in status.items()},
                  complete_Franklin_66706754_byte_original_reconstructed=True, Cassia_binary_original=binary,
                  state_original_topology_review=pin(D / 'coordinator-map-original-topology-review.json'),
                  current_geometry_or_native_result_crosswalk_approved=False,
                  limits='Actual acquired shared geographic references; source defects/vintages remain unchanged. No legal same-vintage outline audit or current child-to-feature match is established.')
    target = D / 'coordinator-finished-maps-review.json'
    value = (json.dumps(result, indent=2) + '\n').encode()
    if target.exists():
        assert target.read_bytes() == value
    else:
        target.write_bytes(value)
    print(json.dumps(pin(target)))


if __name__ == '__main__':
    main()
