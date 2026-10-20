"""Independent raw FirstMap acquisition replay; no election/geographic joins.

Uses the sealed individual response inventory. It neither imports producer
code nor creates a worker build dependency. Public source boundaries remain
qualified resources, never approved historical/current reporting units.
"""
from pathlib import Path
import gzip
import hashlib
import json
import math

S = Path(__file__).resolve().parents[2]
O = S / 'data/news/coordinator-map-preparation'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode()


def main():
    inventory = O / 'acquisition-complete-v1.json'
    rows = json.loads(inventory.read_bytes())
    by = {r['id']: r for r in rows}
    assert len(by) == len(rows)
    bodies = {}
    pins = []
    for r in rows:
        if 'asset_path' not in r:
            assert r['status'] == 0 and r.get('error')
            continue
        stored = (S / r['asset_path']).read_bytes()
        raw = gzip.decompress(stored)
        assert len(stored) == r['stored_bytes'] < 40_000_000
        assert sha(stored) == r['stored_sha256']
        assert len(raw) == r['raw_bytes'] and sha(raw) == r['raw_sha256']
        bodies[r['id']] = raw
        pins.append({k: r[k] for k in ['id', 'status', 'asset_path',
                    'stored_bytes', 'stored_sha256', 'raw_bytes', 'raw_sha256']})

    def get(key):
        assert by[key]['status'] == 200
        value = json.loads(bodies[key])
        assert 'error' not in value
        return value

    metadata = get('district-native-pre-metadata')
    assert bodies['district-native-pre-metadata'] == bodies['district-native-post-metadata']
    assert get('district-native-pre-count') == get('district-native-post-count')
    assert get('district-native-pre-ids') == get('district-native-post-ids')
    expected = get('district-native-pre-ids')
    ids = expected['objectIds']
    oid = expected['objectIdFieldName']
    count = get('district-native-pre-count')['count']
    assert len(ids) == len(set(ids)) == count
    assert metadata['objectIdField'] == oid
    field_names = [f['name'] for f in metadata['fields']]
    features = {}
    feature_receipts = []
    all_positions = 0
    all_rings = 0
    curve_ids = []
    nonclosed = []
    empty = []
    observed_sr = None
    for key in sorted(k for k in by if k.startswith('district-native-batch-')):
        receipt = by[key]
        params = receipt['query_parameters']
        assert params == dict(f='json', objectIds=','.join(map(str, receipt['requested_object_ids'])),
                              outFields='*', returnGeometry='true', returnTrueCurves='true',
                              returnZ='true', returnM='true')
        requested = receipt['requested_object_ids']
        assert 0 < len(requested) <= 50
        value = get(key)
        assert not value.get('exceededTransferLimit', False)
        assert value['objectIdFieldName'] == oid
        assert [f['name'] for f in value['fields']] == field_names
        sr = value['spatialReference']
        if observed_sr is None:
            observed_sr = sr
        assert sr == observed_sr
        assert all(metadata['extent']['spatialReference'][k] == v
                   for k, v in sr.items())
        actual = []
        for feature in value['features']:
            attrs = feature['attributes']
            assert list(attrs) == field_names
            object_id = attrs[oid]
            actual.append(object_id)
            assert object_id not in features
            features[object_id] = feature
            geometry = feature.get('geometry')
            rings = geometry.get('rings', []) if geometry else []
            positions = 0
            if not geometry:
                empty.append(object_id)
            if geometry and 'curveRings' in geometry:
                curve_ids.append(object_id)
            for ring in rings:
                all_rings += 1
                assert len(ring) >= 4
                if ring[0] != ring[-1]:
                    nonclosed.append(object_id)
                for point in ring:
                    assert len(point) >= 2
                    assert all(isinstance(x, (int, float)) and math.isfinite(x) for x in point)
                positions += len(ring)
            all_positions += positions
            feature_receipts.append(dict(object_id=object_id, attributes=attrs,
                                         complete_feature_sha256=sha(canonical(feature)),
                                         geometry_sha256=sha(canonical(geometry)),
                                         native_linear_rings=len(rings),
                                         native_linear_positions=positions,
                                         response_id=key))
        assert len(actual) == len(set(actual)) == len(requested)
        assert set(actual) == set(requested)
    assert set(features) == set(ids)
    output = dict(
        schema='DE-coordinator-original-FirstMap-acquisition-review-v1',
        status='pass_qualified_shared_resource_only',
        acquisition_inventory=dict(path=str(inventory.relative_to(S)),
                                   bytes=inventory.stat().st_size,
                                   sha256=sha(inventory.read_bytes())),
        immutable_individual_response_pins=pins,
        discovery='Actual Department Maps href -> FirstMap Hub page -> observed public JS dataset constructor -> complete dataset metadata service URL.',
        native_count=count, object_id_field=oid, all_attributes=field_names,
        query_spatial_reference=observed_sr,
        complete_metadata_spatial_reference=metadata['extent']['spatialReference'],
        native_linear_ring_count=all_rings,
        native_linear_coordinate_positions=all_positions,
        true_curve_object_ids=curve_ids, empty_geometry_object_ids=empty,
        nonclosed_linear_ring_object_ids=sorted(set(nonclosed)),
        pre_post_metadata_bytes_equal=True, pre_post_counts_equal=True,
        pre_post_id_sets_equal=True, exact_requested_returned_id_sets=True,
        complete_features=[r for r in sorted(feature_receipts, key=lambda r:r['object_id'])],
        source_vintage_limits='Hub description references2010 districts while server description explicitly says election RD-ED boundaries updatedNovember2023; template name Election Districts2022. These literal observations are not a legal effectiveness determination.',
        no_source_transform='Every response preserves all original attributes/native geometry including curve payloads; no outputCRS, rounding, quantization, offset pagination, simplification, repair or vote allocation requested.',
        historical_source_object_count=530, structure_source_object_count=537,
        counts_do_not_prove_identity=True,
        approved_historical_leaf_join=False, approved_current_geometry=False,
        legal_topology_certification=False,
        optional_coordinator_review_not_worker_build_dependency=True,
    )
    p = O / 'native-acquisition-review.json'
    p.write_text(json.dumps(output, indent=2, ensure_ascii=False, allow_nan=False)+'\n')
    print(json.dumps({k: output[k] for k in ['status', 'native_count', 'all_attributes',
          'native_linear_ring_count', 'native_linear_coordinate_positions',
          'true_curve_object_ids', 'empty_geometry_object_ids']}))
    print(json.dumps(dict(path=str(p.relative_to(S)), bytes=p.stat().st_size,
                          sha256=sha(p.read_bytes()))))


if __name__ == '__main__':
    main()
