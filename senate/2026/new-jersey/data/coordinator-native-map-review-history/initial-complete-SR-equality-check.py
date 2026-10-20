"""Independent raw native snapshot audit, without producer imports or writes.

Pins complete individual receipts/originals, not an active aggregate manifest.
This is source-integrity review, not a finished-package or geographic approval.
"""
from pathlib import Path
from collections import Counter
import gzip
import hashlib
import json
import math

S = Path(__file__).resolve().parents[1]
M = S / 'maps'
N = 0
PINS = {}


def ck(ok, note=''):
    global N
    assert ok, note
    N += 1


def sha(b):
    return hashlib.sha256(b).hexdigest()


def pin(p):
    b = p.read_bytes()
    r = dict(path=str(p.relative_to(S)), bytes=len(b), sha256=sha(b))
    PINS[r['path']] = r
    return r


def digest(v):
    return sha(json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode())


def receipt(name):
    p = M / 'receipts' / (name + '.json')
    pin(p)
    r = json.loads(p.read_bytes())
    ck(r['status'] == 200 and bool(r['hops']), name)
    h = r['hops'][-1]
    chunks = []
    for part in h['stored_parts']:
        p = M / part['path']
        actual = pin(p)
        ck((actual['bytes'], actual['sha256']) == (part['bytes'], part['sha256']), name)
        ck(actual['bytes'] < 40000000)
        chunks.append(p.read_bytes())
    raw = gzip.decompress(b''.join(chunks))
    ck((len(raw), sha(raw)) == (h['raw_bytes'], h['raw_sha256']), name)
    enc = next((v for k, v in h['response_headers'] if k.lower() == 'content-encoding'), '')
    ck(enc in ['', 'identity', 'gzip'], (name, enc))
    if enc == 'gzip':
        raw = gzip.decompress(raw)
    obj = json.loads(raw)
    ck('error' not in obj, name)
    return r, obj


def main():
    index = json.loads((M / 'native-feature-index.json').read_bytes())
    index_map = {(r['receipt'], r['feature_index']): r for r in index}
    ck(len(index_map) == len(index) == 6749)
    features = []
    services = []
    for service, count in [('state-election-service', 6348), ('burlington-election-service', 401)]:
        _, pre = receipt(service + '-meta-pre')
        _, post = receipt(service + '-meta-post')
        ck(pre == post, service + ' complete service metadata')
        _, layer = receipt(service + '-layer-pre')
        _, after = receipt(service + '-layer-post')
        ck(layer == after, service + ' complete layer metadata')
        _, a = receipt(service + '-count-pre')
        _, b = receipt(service + '-count-post')
        ck(a == b and a['count'] == count)
        _, a = receipt(service + '-ids-pre')
        _, b = receipt(service + '-ids-post')
        ids = a['objectIds']
        ck(len(ids) == len(set(ids)) == len(b['objectIds']) == len(set(b['objectIds'])) == count)
        ck(set(ids) == set(b['objectIds']))
        oid = next(f['name'] for f in layer['fields'] if f['type'] == 'esriFieldTypeOID')
        fields = {f['name'] for f in layer['fields'] if f['type'] != 'esriFieldTypeGeometry'}
        ordered = sorted(ids)
        returned = []
        totals = Counter()
        for start in range(0, count, 50):
            name = service + '-batch-%04d' % (start // 50)
            r, o = receipt(name)
            query = r['query']
            expected = ordered[start:start + 50]
            ck([int(x) for x in query['objectIds'].split(',')] == expected)
            ck(query['outFields'] == '*' and all(query[k] == 'true' for k in ['returnGeometry', 'returnZ', 'returnM', 'returnTrueCurves']))
            ck(not {'outSR', 'outCRS', 'geometryPrecision', 'quantizationParameters', 'maxAllowableOffset', 'datumTransformation', 'returnCentroid', 'returnEnvelope'}.intersection(query))
            ck(not o.get('exceededTransferLimit', False))
            ck(o['spatialReference'] == layer['extent']['spatialReference'])
            got = [f['attributes'][oid] for f in o['features']]
            ck(len(got) == len(set(got)) == len(expected) and set(got) == set(expected))
            returned.extend(got)
            for i, f in enumerate(o['features']):
                attrs = f['attributes']
                geom = f.get('geometry')
                ck(set(attrs) == fields)
                d = index_map[(name, i)]
                ck(d['attributes'] == attrs and d['service'] == service and d['current_or_source_row_join'] is False)
                rings = points = 0
                if geom is None:
                    case = 'null'
                elif 'curveRings' in geom:
                    case = 'true-curves'
                    ck(isinstance(geom['curveRings'], list))
                elif 'rings' in geom:
                    case = 'linear-rings'
                    rings = len(geom['rings'])
                    flat = []
                    for ring in geom['rings']:
                        ck(isinstance(ring, list))
                        for xy in ring:
                            ck(isinstance(xy, list) and len(xy) >= 2)
                            ck(all(type(v) in [int, float] and math.isfinite(v) for v in xy))
                            flat.append(xy)
                    points = len(flat)
                    ck(d['geometry_diagnostic']['parts'] == rings)
                    ck(d['geometry_diagnostic']['points'] == points)
                    if flat:
                        bbox = [min(x[0] for x in flat), min(x[1] for x in flat), max(x[0] for x in flat), max(x[1] for x in flat)]
                        ck(d['geometry_diagnostic']['native_bbox'] == bbox)
                else:
                    raise AssertionError((service, attrs[oid], 'unclassified original geometry'))
                totals[case] += 1
                totals['linear_ring_parts'] += rings
                totals['linear_native_positions'] += points
                features.append(dict(service=service, object_id=attrs[oid], receipt=name,
                                     native_feature_ordinal=i, complete_attributes_sha256=digest(attrs),
                                     complete_original_geometry_sha256=digest(geom),
                                     geometry_case=case, linear_ring_parts=rings, linear_native_positions=points))
        ck(len(returned) == len(set(returned)) == count and set(returned) == set(ids))
        services.append(dict(name=service, count=count, metadata_spatial_reference=layer['extent']['spatialReference'],
                             all_attribute_fields=len(fields), complete_service_and_layer_metadata_equal=True,
                             complete_pre_post_count_and_IDsets_equal=True, maximum_requested_batch=50,
                             geometry_counts=dict(totals), zero_source_or_current_joins=True))
    result = dict(status='pass_independent_raw_native_snapshot_integrity', checks=N,
                  services=services, complete_feature_fingerprints=features,
                  individually_rehashed_receipts_and_original_parts=list(PINS.values()),
                  producer_imports_or_writes=False, final_package_approval=False,
                  source_current_leaf_or_legal_crosswalk_approval=False,
                  qualification='Complete original attributes and geometry hashes retain all raw positions, true curves and nulls without repair/generalization. State layer is explicitly historical2019–2020 mature support; Burlington is a separate native scope. This audit does not certify topology, legal effectiveness, source-label equivalence, ballot allocation or a complete finished package.')
    out = S / 'data/coordinator-native-map-snapshot-review.json'
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + '\n')
    print(json.dumps(dict(checks=N, output=pin(out), services=services)))


if __name__ == '__main__':
    main()
