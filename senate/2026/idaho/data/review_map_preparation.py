"""Independent, offline review of the observed public Idaho boundary view.

This verifies source completeness and native positions. It does not join any
election reporting row, certify topology, or approve November boundaries.
"""
from pathlib import Path
from collections import Counter
import gzip, hashlib, json, urllib.parse

D = Path(__file__).resolve().parent
S = D.parent
O = D / 'coordinator-map-preparation'

def sha(b):
    return hashlib.sha256(b).hexdigest()

def pin(p):
    b = p.read_bytes()
    return dict(path=str(p.relative_to(S)), bytes=len(b), sha256=sha(b))

def main():
    source = O / 'acquisition-native-stage-v1.json'
    rows = json.loads(source.read_bytes())
    by = {r['id']: r for r in rows}
    assert len(by) == len(rows)
    bodies = {}
    for r in rows:
        if 'asset_path' not in r:
            assert r['status'] == 0 and r['error']
            continue
        b = (S / r['asset_path']).read_bytes()
        assert len(b) == r['stored_bytes'] < 40_000_000
        assert sha(b) == r['stored_sha256']
        raw = gzip.decompress(b)
        assert len(raw) == r['raw_bytes'] and sha(raw) == r['raw_sha256']
        bodies[r['id']] = raw
    def load(k):
        return json.loads(bodies[k])
    pre = load('state-precinct-layer-metadata')
    post = load('state-precinct-metadata-post')
    assert pre == post
    assert pre['objectIdField'] == 'OBJECTID'
    assert pre['geometryType'] == 'esriGeometryPolygon'
    ids = load('state-precinct-ids-pre')['objectIds']
    assert len(ids) == len(set(ids)) == 976
    assert set(ids) == set(load('state-precinct-ids-post')['objectIds'])
    assert load('state-precinct-count-pre') == load('state-precinct-count-post') == {'count': 976}
    features = []
    schemas = []
    native_crs = []
    for k in sorted(by):
        if not k.startswith('state-precinct-native-page'):
            continue
        r = by[k]
        query = urllib.parse.parse_qs(urllib.parse.urlparse(r['url']).query)
        wanted = list(map(int, query['objectIds'][0].split(',')))
        assert len(wanted) <= 50
        for forbidden in ['outSR', 'geometryPrecision', 'quantizationParameters', 'maxAllowableOffset', 'resultOffset']:
            assert forbidden not in query
        assert query['outFields'] == ['*']
        assert query['returnGeometry'] == ['true']
        assert query['returnTrueCurves'] == ['true']
        b = load(k)
        assert not b.get('exceededTransferLimit') and 'error' not in b
        fs = b['features']
        got = [f['attributes']['OBJECTID'] for f in fs]
        assert len(got) == len(set(got)) == len(wanted) and set(got) == set(wanted)
        schemas.append(b['fields'])
        native_crs.append(b['spatialReference'])
        features.extend(fs)
    assert len(schemas) == 20 and all(x == schemas[0] for x in schemas)
    assert all(x == native_crs[0] for x in native_crs)
    assert native_crs[0] == pre['extent']['spatialReference']
    assert len(features) == 976
    assert set(f['attributes']['OBJECTID'] for f in features) == set(ids)
    counties = Counter(f['attributes']['COUNTY'] for f in features)
    assert len(counties) == 44
    rings = points = 0
    defects = []
    for f in features:
        assert set(f['attributes']) == {x['name'] for x in schemas[0]}
        g = f.get('geometry')
        if not g or 'rings' not in g:
            defects.append(dict(OBJECTID=f['attributes']['OBJECTID'], condition='empty_or_non_linear', geometry=g))
            continue
        for ring in g['rings']:
            rings += 1
            points += len(ring)
            if len(ring) < 4 or ring[0] != ring[-1]:
                defects.append(dict(OBJECTID=f['attributes']['OBJECTID'], condition='short_or_open_ring'))
    out = dict(
        status='pass_complete_native_public_view_snapshot_with_explicit_scope_limits',
        immutable_acquisition=pin(source), observations=len(rows),
        complete_entities=len(bodies), exact_pre_post_layer_metadata=True,
        exact_pre_post_counts_and_ID_sets=True, bounded_pages=20, maximum_requested_IDs=50,
        features=976, counties=dict(sorted(counties.items())),
        ACTIVE_values=dict(Counter(f['attributes']['ACTIVE'] for f in features)),
        spatial_reference=native_crs[0], layer_editing_info=pre.get('editingInfo'),
        field_definitions=schemas[0], all_attributes_and_source_geometry_retained=True,
        rings=rings, native_coordinate_positions=points,
        structural_observations=defects,
        feature_semantic_sha256=sha(json.dumps(features,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()),
        no_output_CRS_rounding_quantization_offset_or_simplification=True,
        source_snapshot_is_2024_reporting_crosswalk=False,
        current_legal_or_November_reporting_geography_approved=False,
        topology_or_overlap_gap_certification=False,
        qualification='976 source features are distinct from 985 historical presidential and 986 statistics contexts. ACTIVE/source dates and publisher provenance do not establish reporting identity or legal approval; no join, allocation or repair was made.')
    target = D / 'coordinator-map-native-preparation-review.json'
    b = (json.dumps(out, indent=2, ensure_ascii=False) + '\n').encode()
    if target.exists():
        assert target.read_bytes() == b
    else:
        target.write_bytes(b)
    print(json.dumps(pin(target)))

if __name__ == '__main__':
    main()
