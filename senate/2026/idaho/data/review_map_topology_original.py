"""Producer-free native-ring replay; diagnostic topology, never a legal crosswalk."""
from pathlib import Path
import collections
import gzip
import hashlib
import json
import math
import struct
from shapely.geometry import Polygon, MultiPolygon
from shapely.strtree import STRtree
from shapely.validation import explain_validity
import shapely

D = Path(__file__).resolve().parent
S = D.parent
O = D / 'coordinator-map-preparation'


def sha(value):
    return hashlib.sha256(value).hexdigest()


def semantic(value):
    return sha(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode())


def bits(value):
    return struct.pack('>d', value)


def orientation(ring):
    return math.fsum(a[0] * b[1] - b[0] * a[1] for a, b in zip(ring, ring[1:]))


def main():
    receipts = json.loads((O / 'acquisition-native-stage-v1.json').read_bytes())
    features = []
    pages = []
    for entry in sorted(receipts, key=lambda x: x['id']):
        if not entry['id'].startswith('state-precinct-native-page'):
            continue
        stored = (S / entry['asset_path']).read_bytes()
        raw = gzip.decompress(stored)
        assert sha(stored) == entry['stored_sha256'] and sha(raw) == entry['raw_sha256']
        obj = json.loads(raw)
        assert not obj.get('exceededTransferLimit') and not obj.get('error')
        features.extend(obj['features'])
        pages.append(dict(id=entry['id'], source=entry['asset_path'], raw_sha256=sha(raw)))
    assert len(pages) == 20 and len(features) == 976
    assert len({x['attributes']['OBJECTID'] for x in features}) == 976
    source_digest = semantic(features)
    models = []
    ids = []
    observations = []
    rings = positions = 0
    for feature in features:
        geometry = feature['geometry']
        assert set(geometry) == {'rings'}
        source = geometry['rings']
        assert all(len(r) >= 4 and r[0] == r[-1] for r in source)
        shells = [r for r in source if orientation(r) < 0]
        holes = [r for r in source if orientation(r) >= 0]
        assert shells
        bases = [Polygon(r) for r in shells]
        attached = [[] for _ in shells]
        for hole in holes:
            shape = Polygon(hole)
            owners = [i for i, polygon in enumerate(bases) if polygon.covers(shape)]
            assert owners
            attached[min(owners, key=lambda i: bases[i].area)].append(hole)
        parts = [Polygon(shell, internal) for shell, internal in zip(shells, attached)]
        for shell, internal, polygon in zip(shells, attached, parts):
            for original, reconstructed in [(shell, list(polygon.exterior.coords))] + list(zip(internal, [list(x.coords) for x in polygon.interiors])):
                assert len(original) == len(reconstructed)
                assert all(len(a) == len(b) == 2 and all(bits(x) == bits(y) for x, y in zip(a, b)) for a, b in zip(original, reconstructed))
                rings += 1
                positions += len(original)
        model = parts[0] if len(parts) == 1 else MultiPolygon(parts)
        attrs = feature['attributes']
        observations.append(dict(OBJECTID=attrs['OBJECTID'], COUNTY=attrs['COUNTY'], PCNCT_NME=attrs['PCNCT_NME'],
                                 full_source_attribute_digest=semantic(attrs), valid=bool(model.is_valid),
                                 validity=explain_validity(model), empty=bool(model.is_empty), native_area=model.area))
        if model.is_valid and not model.is_empty:
            models.append(model)
            ids.append(attrs['OBJECTID'])
    assert rings == 1032 and positions == 749523
    assert semantic(features) == source_digest
    tree = STRtree(models)
    pairs = []
    for i, model in enumerate(models):
        for found in tree.query(model, predicate='intersects'):
            j = int(found)
            if j > i:
                area = model.intersection(models[j]).area
                if area > 0:
                    pairs.append(dict(OBJECTIDs=[ids[i], ids[j]], native_square_metres=area))
    bad = [x for x in observations if not x['valid']]
    assert len(bad) == 1 and len(models) == 975 and len(pairs) == 241
    output = dict(status='pass_complete_original_native_geometry_diagnostics', engine='shapely ' + shapely.__version__,
                  original_pages=pages, complete_source_feature_semantic_sha256=source_digest,
                  features=976, counties=len({x['attributes']['COUNTY'] for x in features}),
                  rings=rings, original_native_positions=positions, every_XY_double_bit_pattern_and_position_preserved=True,
                  every_original_attribute_digest_preserved=True, diagnostics=observations,
                  invalid_features=bad, valid_nonempty_topology_features=975, positive_area_intersections=pairs,
                  source_modified_or_repaired=False, historical_votes_or_current_IDs_joined=False,
                  current_legal_geometry_or_gap_overlap_sliver_certification=False,
                  qualification='Native source-unit diagnostics only. Closed source rings were passed unchanged; clockwise shells and full-contained counterclockwise holes are explicit. Invalid observations remain in original data, excluded from pair intersections. No vote allocation, source repair or same-vintage legal-outline comparison is made.')
    target = D / 'coordinator-map-original-topology-review.json'
    value = (json.dumps(output, indent=2) + '\n').encode()
    if target.exists():
        assert target.read_bytes() == value
    else:
        target.write_bytes(value)
    print(json.dumps(dict(path=str(target.relative_to(S)), bytes=len(value), sha256=sha(value), invalid=bad, overlap_pairs=len(pairs))))


if __name__ == '__main__':
    main()
