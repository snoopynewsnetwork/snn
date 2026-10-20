"""Independent complete native-request/schema/ring-position snapshot audit."""
from pathlib import Path
import collections
import gzip
import hashlib
import json
import math
import struct

S = Path(__file__).resolve().parents[1]
M = S/'maps'
N = 0


def ck(v, note=''):
    global N
    assert v, note
    N += 1


def sha(b):
    return hashlib.sha256(b).hexdigest()


def pin(p):
    b = p.read_bytes()
    return dict(path=str(p.relative_to(S)), bytes=len(b), sha256=sha(b))


def read(p):
    return json.loads(p.read_bytes())


def original(name):
    p = M/'receipts'/(name+'.json')
    r = read(p)
    ck(r['status'] == 200)
    chunks = []
    for part in r['parts']:
        z = (M/part['path']).read_bytes()
        ck(len(z) == part['bytes'] < 40000000 and sha(z) == part['sha256'])
        chunks.append(z)
    b = gzip.decompress(b''.join(chunks))
    ck(len(b) == r['raw_bytes'] and sha(b) == r['raw_sha256'])
    data = json.loads(b)
    ck('error' not in data, name)
    return r, data, pin(p)


def main():
    audit_path = M/'native-audit.json'
    audit = read(audit_path)
    results = []
    sources = []
    for kind, short, expected in [('wards', 'wards', 2256), ('subprecinct', 'subprecinct', 147)]:
        prefix = short+'-layer0'
        ap = M/(prefix+'-acquisition.json')
        acq = read(ap)
        sources.append(pin(ap))
        rr, pre, rp = original(prefix+'-pre')
        rr, post, rp2 = original(prefix+'-post')
        sources.extend([rp, rp2])
        ck(pre == post and pre['extent']['spatialReference']['wkid'] == 26986)
        fields = {v['name'] for v in pre['fields'] if v['type'] != 'esriFieldTypeGeometry'}
        oid = pre['objectIdField']
        rr, pre_ids, rp = original(prefix+'-ids-pre')
        rr, post_ids, rp2 = original(prefix+'-ids-post')
        sources.extend([rp, rp2])
        ids = pre_ids['objectIds']
        ck(ids == post_ids['objectIds'] and len(ids) == len(set(ids)) == expected)
        for suffix in ['count-pre', 'count-post']:
            rr, count, rp = original(prefix+'-'+suffix)
            sources.append(rp)
            ck(count['count'] == expected)
        rr, service_pre, rp = original(short+'-service-pre')
        rr, service_post, rp2 = original(short+'-service-post')
        sources.extend([rp, rp2])
        changed = sorted(k for k in set(service_pre)|set(service_post) if service_pre.get(k) != service_post.get(k))
        ck(changed == (['initialExtent'] if kind == 'wards' else []), changed)
        features = []
        for batch in acq['batches']:
            name = Path(batch['receipt']).stem
            rr, data, rp = original(name)
            sources.append(rp)
            query = rr['query']
            requested = [int(v) for v in query['objectIds'].split(',')]
            got = [f['attributes'][oid] for f in data['features']]
            ck(0 < len(requested) <= 50 and len(got) == len(set(got)))
            ck(requested == batch['requested_ids'] and set(requested) == set(got) == set(batch['returned_ids']))
            ck(query['outFields'] == '*')
            for key in ['returnGeometry', 'returnZ', 'returnM', 'returnTrueCurves']:
                ck(query[key] == 'true')
            ck(not any(k in query for k in ['outSR', 'geometryPrecision', 'quantizationParameters', 'maxAllowableOffset']))
            ck(not data.get('exceededTransferLimit', False))
            features.extend(data['features'])
        ck(len(features) == expected and len({f['attributes'][oid] for f in features}) == expected)
        ck(set(ids) == {f['attributes'][oid] for f in features} == set(acq['ids']))
        af = {r['object_id']: r for r in audit[kind]['features']}
        ck(set(af) == set(ids))
        rings = positions = scalar_coordinates = 0
        geometry_stream = hashlib.sha256()
        towns = set()
        for feature in features:
            attrs = feature['attributes']
            a = af[attrs[oid]]
            ck(set(attrs) == fields and attrs == a['attributes'])
            towns.add(attrs['TOWN'])
            geom = feature.get('geometry')
            ck(isinstance(geom, dict) and list(geom) == a['geometry_keys'])
            ck('rings' in geom and 'curveRings' not in geom)
            ck(len(geom['rings']) == len(a['rings']))
            for ring, reported in zip(geom['rings'], a['rings']):
                ck(len(ring) == reported['vertices'])
                dims = sorted({len(p) for p in ring})
                ck(dims == reported['dimensions'] == [2])
                start = b''.join(struct.pack('<d', v) for v in ring[0])
                end = b''.join(struct.pack('<d', v) for v in ring[-1])
                ck((start == end) == reported['bit_closed'])
                for point in ring:
                    for value in point:
                        ck(type(value) in (float, int) and math.isfinite(value))
                        geometry_stream.update(struct.pack('<d', value))
                        scalar_coordinates += 1
                    positions += 1
                rings += 1
        results.append(dict(scope=kind, features=len(features), fields=sorted(fields), source_town_attributes=len(towns),
                            batches=len(acq['batches']), rings=rings, native_positions=positions,
                            scalar_coordinate_positions=scalar_coordinates, native_coordinate_stream_sha256=geometry_stream.hexdigest(),
                            native_CRS=pre['extent']['spatialReference'], service_changed_fields=changed,
                            original_feature_objects_sha256=sha(json.dumps(features, sort_keys=True, separators=(',', ':'), allow_nan=False).encode())))
    out = dict(status='pass_independent_complete_native_snapshot_schema_and_ring_position_integrity', checks=N,
               layers=results, complete_individual_receipt_pins=sources, bounded_derived_audit=pin(audit_path),
               qualifications='2256ward/precinct and147subprecinct snapshot features remain separate scopes; no source-vote/physical/current join or spatial allocation. Layer metadata/count/IDs stable; wards service initialExtent differs and is retained as a viewport-only observed metadata difference. This proof verifies complete raw batches, all attributes/schema and every native ring coordinate position, not independent legal topology, overlaps or current correctness. Worker source invalidity/overlap diagnostics remain unrepaired and qualified. No originalSHP archive is claimed.',
               producer_import_or_mutation=False, current_or_legal_crosswalk_approved=False)
    p = S/'data/coordinator-native-map-snapshot-review.json'
    p.write_text(json.dumps(out, indent=2)+'\n')
    print(dict(checks=N, layers=[dict(scope=r['scope'], features=r['features'], positions=r['native_positions']) for r in results], proof=pin(p)))


if __name__ == '__main__':
    main()
