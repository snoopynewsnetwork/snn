#!/usr/bin/env python3
"""Offline build for the Oklahoma precinct-map package (no network).

Run from the repository root:

    PYTHONDONTWRITEBYTECODE=1 uv run --with shapely==2.0.6 --with pyproj==3.7.0 \
        --with matplotlib==3.9.2 --with pypdfium2==4.30.0 --with pyshp==2.3.1 \
        python3 -I senate/2026/oklahoma/maps/build.py

Inputs: maps/raw/ + maps/source-manifest.json (from acquire.py) and, read-only,
the turnout worker's county CSV, priority contract and OKER precinct exports.
Every raw file and every read-only input is hash-verified before use.

Outputs (all under maps/):
  counties/<fips>-<slug>/*.geojson.gz  county subsets of three layer vintages.
      Features are copied unchanged from the server GeoJSON (same geometry,
      coordinates, ring order and properties); only the county filter and a
      FeatureCollection wrapper with provenance foreign members are added.
  previews/*.png  rendered previews (derivatives; never used for analysis).
  index.csv / index.json  per-county map index.
  manifest.csv  every owned asset with role, source, vintage, CRS, counts, hashes.
  precinct-roster.csv  every precinct ID in the 26 counties across all rosters.
  id-reconciliation.csv  per county x layer x election match counts and rates.
  geometry-changes.csv  current vs 2024-baseline geometry differences.
  geometry-audit.json  validity, overlaps, gaps and per-layer structure.
  pdf-inventory.csv / pdf-audit.json  CSA PDF catalogue and downloaded PDFs.
  checks.json  build-time checks (validate.py re-checks independently).
  read-only-pins.json  hashes of the read-only peer inputs.
  index.html  offline gallery.
"""
import collections
import csv
import datetime
import gzip
import hashlib
import html
import io
import json
import math
import pathlib
import re
import sys
import zipfile

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.collections import PatchCollection  # noqa: E402
from matplotlib.patches import Patch, PathPatch  # noqa: E402
from matplotlib.path import Path as MPath  # noqa: E402
import numpy as np  # noqa: E402
import pypdfium2 as pdfium  # noqa: E402
import pyproj  # noqa: E402
import shapefile  # pyshp  # noqa: E402
import shapely  # noqa: E402
from shapely.geometry import shape  # noqa: E402
from shapely.strtree import STRtree  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
STATE = HERE.parent
REPO = STATE.parents[2]
RAW = HERE / 'raw'
TURNOUT = STATE / 'data' / 'turnout'
POST_ELECTION_MS = 1730851200000  # 2024-11-06T00:00:00Z
CHANGE_M2 = 100.0       # symmetric-difference area (m^2) above which a precinct is "geometry changed"
CHANGE_FRAC = 1e-4      # ... and above this fraction of the precinct area
OVERLAP_M2 = 1.0        # overlaps/gaps smaller than 1 m^2 are reported only in the tiny-residual count
TO_ALBERS = pyproj.Transformer.from_crs('EPSG:4269', 'EPSG:5070', always_xy=True)

checks = []


def check(name, ok, detail=None):
    checks.append({'check': name, 'pass': bool(ok), 'detail': detail})
    if not ok:
        print('FAIL', name, detail, file=sys.stderr)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, str):
        data = data.encode()
    path.write_bytes(data)
    return path


def gz(obj):
    return gzip.compress(json.dumps(obj, separators=(',', ':'), ensure_ascii=False).encode(), compresslevel=9, mtime=0)


def ms(v):
    return None if v is None else datetime.datetime.fromtimestamp(v / 1000, datetime.UTC).isoformat().replace('+00:00', 'Z')


# ---------------------------------------------------------------- inputs
MAN = json.loads((HERE / 'source-manifest.json').read_text())
REC = {r['id']: r for r in MAN['records']}
for r in MAN['records']:
    if r.get('stored_path'):
        b = (HERE / r['stored_path']).read_bytes()
        okh = sha(b) == r['stored_sha256'] and len(b) == r['stored_bytes']
        if r['storage'] == 'gzip-9-mtime0':
            body = gzip.decompress(b)
            okh = okh and sha(body) == r['body_sha256'] and len(body) == r['body_bytes']
        check(f'raw hash {r["id"]}', okh)
check('all raw requests HTTP 200', all(r['status'] == 200 for r in MAN['records']),
      [r['id'] for r in MAN['records'] if r['status'] != 200])


def raw(rel):
    r = REC[rel]
    b = (HERE / r['stored_path']).read_bytes()
    return gzip.decompress(b) if r['storage'] == 'gzip-9-mtime0' else b


def rawj(rel):
    return json.loads(raw(rel))


def feats(prefix, ext='geojson'):
    out = []
    for rid in sorted(k for k in REC if k.startswith(prefix + '/features-') and k.endswith('.' + ext)):
        out += rawj(rid)['features']
    return out


# Read-only peer inputs, pinned.
tman = {r['id']: r for r in json.loads((TURNOUT / 'source-manifest.json').read_text())}
pins = {}
for date in ('20241105', '20221108', '20201103'):
    r = tman[f'oker-{date}-precinct-csv']
    b = (TURNOUT / r['path']).read_bytes()
    check(f'read-only OKER {date} precinct export matches turnout manifest', sha(b) == r['stored_sha256'])
    pins[f'data/turnout/{r["path"]}'] = {'sha256': sha(b), 'bytes': len(b)}
for rel in ('data/county-turnout.csv', 'data/turnout/priority-set.json', 'data/turnout/reporting-units.json',
            'data/turnout/source-manifest.json'):
    b = (STATE / rel).read_bytes()
    pins[rel] = {'sha256': sha(b), 'bytes': len(b)}

CT = list(csv.DictReader(open(STATE / 'data' / 'county-turnout.csv', encoding='utf-8')))
BYCODE = {r['oseb_county_code']: r for r in CT}
PRI = [r for r in CT if r['pres2024_min80'] in ('1', 'true', 'True', 'yes')]
check('2024 minimum-80% set has 25 counties', len(PRI) == 25, len(PRI))
kay = [r for r in CT if r['county_fips'] == '40071'][0]
PRI = PRI + [kay]
PRI_FIPS = [r['county_fips'] for r in PRI]
EXPECTED = ['40109', '40143', '40027', '40017', '40131', '40145', '40031', '40037', '40119', '40125', '40051', '40101',
            '40083', '40147', '40047', '40087', '40113', '40019', '40079', '40137', '40041', '40021', '40013', '40121',
            '40097', '40071']
check('priority set = accepted 26 counties in turnout order', PRI_FIPS == EXPECTED, PRI_FIPS)
for code, r in BYCODE.items():
    check(f'census county code = 2*OSEB-1 ({r["county"]})', int(r['county_fips'][2:]) == 2 * int(code) - 1)
FIPS2CODE = {r['county_fips']: r['oseb_county_code'] for r in CT}
CODE2FIPS = {v: k for k, v in FIPS2CODE.items()}
NAME = {r['county_fips']: r['county'] for r in CT}


def oker(date, race):
    """Return {precinct_id: total votes in race} for the OKER precinct export."""
    z = zipfile.ZipFile(TURNOUT / f'raw/oker-{date}-precinct-csv.zip')
    votes, ids = collections.Counter(), set()
    with z.open(z.namelist()[0]) as f:
        for row in csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig')):
            ids.add(row['precinct'])
            if row['race_number'] == race:
                votes[row['precinct']] += int(row['cand_tot_votes'])
    for p in ids:
        votes.setdefault(p, 0)
    return votes


RESULTS = {'2024': oker('20241105', '10001'), '2022': oker('20221108', '10011'), '2020': oker('20201103', '10003')}
RACE_LABEL = {'2024': '2024 president (race 10001)', '2022': '2022 U.S. Senate special (race 10011)',
              '2020': '2020 U.S. Senate (race 10003)'}
check('OKER 2024 export has 1,986 units', len(RESULTS['2024']) == 1986, len(RESULTS['2024']))
check('OKER 2022 export has 1,986 units', len(RESULTS['2022']) == 1986, len(RESULTS['2022']))
check('OKER 2020 export has 1,950 units', len(RESULTS['2020']) == 1950, len(RESULTS['2020']))
NONGEO = {'559999', '729999'}
for y, v in RESULTS.items():
    check(f'OKER {y}: the only xx9999 units are 559999 and 729999', {p for p in v if p.endswith('9999')} == NONGEO)
check('2024 president precinct votes total 1,566,173', sum(RESULTS['2024'].values()) == 1566173,
      sum(RESULTS['2024'].values()))
check('2022 special Senate precinct votes total 1,150,481', sum(RESULTS['2022'].values()) == 1150481)
check('2020 Senate precinct votes total 1,556,361', sum(RESULTS['2020'].values()) == 1556361)

# ---------------------------------------------------------------- layers
LAYERS = {}


def load_geojson_layer(key, prefix, idf, county_of):
    fs = feats(prefix)
    cnt = rawj(f'{prefix}/count.json')['count']
    ids = rawj(f'{prefix}/ids.json')['objectIds']
    check(f'{key}: features fetched = count = returnIdsOnly', len(fs) == cnt == len(ids), [len(fs), cnt, len(ids)])
    check(f'{key}: object IDs unique and equal to enumerated IDs', sorted(f['id'] for f in fs) == sorted(ids))
    for f in fs:
        f['_pid'] = idf(f['properties'])
        f['_code'] = county_of(f['properties'])
        f['_geom'] = shape(f['geometry']) if f['geometry'] else None
    LAYERS[key] = fs
    return fs


csa = load_geojson_layer('current', 'csa2020', lambda p: p['PCT_CEB'], lambda p: p['COUNTY'])
mir = load_geojson_layer('baseline2024', 'incog-state', lambda p: p['PCT_CEB'], lambda p: p['COUNTY'])
h10 = load_geojson_layer('hist2020', 'csa2010/priority-geometry', lambda p: p['PCT_CEB'], lambda p: p['COUNTY'])
tul = load_geojson_layer('tulsa_incog_2022', 'incog-tulsa', lambda p: '72' + f'{int(p["PCT"]):04d}',
                         lambda p: '72')
mcc = load_geojson_layer('mcclain911', 'mcclain911', lambda p: p['PCT_CEB'], lambda p: p['PCT_CEB'][:2])
a10 = [f['attributes'] for f in feats('csa2010/statewide-attributes', 'json')]
check('2010 statewide attributes = count', len(a10) == rawj('csa2010/statewide-attributes/count.json')['count'])
check('2010 priority geometry count = attribute rows in priority counties',
      len(h10) == sum(1 for a in a10 if a['COUNTY'] in {FIPS2CODE[f] for f in PRI_FIPS}))

LAYER_META = {
    'current': {
        'label': 'CSA Voter Precincts 2020 (pct_2020), as served',
        'role': 'current published geography (post-2024 edits); not a November 2026 approval',
        'publisher': 'OU Center for Spatial Analysis (CSA) with the Oklahoma State Election Board (item credits)',
        'source_url': 'https://services.arcgis.com/3xOwF6p0r7IHIjfn/arcgis/rest/services/State_Wide_2020_Precincts/FeatureServer/0',
        'native_crs': 'EPSG:4269 (NAD83 geographic)', 'served_crs': 'EPSG:4269 (outSR=4269, identical to native)',
        'file_tag': 'current-csa-pct2020',
    },
    'baseline2024': {
        'label': 'INCOG mirror PCT_OK_State of the CSA statewide file (downloaded from CSA January 2025)',
        'role': '2024-cycle baseline geometry (government mirror of the official file; IDs equal the 2024 results)',
        'publisher': 'Indian Nations Council of Governments (INCOG), mirroring CSA / Oklahoma State Election Board data',
        'source_url': 'https://map11.incog.org/arcgis11wa/rest/services/PCT_OK_State/FeatureServer/0',
        'native_crs': 'EPSG:2267 (ArcGIS 102724, NAD83 / Oklahoma North ftUS)',
        'served_crs': 'EPSG:4269 (server outSR=4269 projection of the native layer)',
        'file_tag': 'baseline2024-incog-mirror',
    },
    'hist2020': {
        'label': 'CSA Voter Precincts 2010 (PCT_2010), priority-county subset',
        'role': 'historical 2020-election geography (pre-2022 reprecincting); context only',
        'publisher': 'OU Center for Spatial Analysis (CSA)',
        'source_url': 'https://services.arcgis.com/3xOwF6p0r7IHIjfn/arcgis/rest/services/Voter_Precints/FeatureServer/0',
        'native_crs': 'EPSG:4269 (NAD83 geographic)', 'served_crs': 'EPSG:4269',
        'file_tag': 'historical2020-csa-pct2010',
    },
}
csa_layer = rawj('csa2020/layer.json')
mir_ms = rawj('incog-state/mapserver.json')
h10_layer = rawj('csa2010/priority-geometry/layer.json')
LAYER_META['current']['vintage'] = (f'dataLastEditDate {ms(csa_layer["editingInfo"]["dataLastEditDate"])}; item text '
                                    f'"Last Updated: 06/07/2022"; retrieved {REC["csa2020/features-001.geojson"]["retrieval_utc"]}')
LAYER_META['baseline2024']['vintage'] = ('service text: "File was downloaded from CSA January 2025. Boundaries last '
                                         f'updated 2024."; retrieved {REC["incog-state/features-001.geojson"]["retrieval_utc"]}')
LAYER_META['hist2020']['vintage'] = (f'dataLastEditDate {ms(h10_layer["editingInfo"]["dataLastEditDate"])} (service '
                                     f'republish time, not boundary date); retrieved {REC["csa2010/priority-geometry/features-001.geojson"]["retrieval_utc"]}')
check('current layer: maxRecordCount 2000 and 1984 < 2000', csa_layer['maxRecordCount'] == 2000 and len(csa) == 1984)
check('baseline mirror description states January 2025 CSA download',
      'downloaded from CSA January 2025' in mir_ms['serviceDescription'])

# Paging probe: one resultOffset page holds all 1984; next offset returns zero.
p0 = rawj('csa2020/paging-probe-offset0.json')
p1 = rawj('csa2020/paging-probe-offset1984.json')
check('paging probe: offset 0 returns 1984 rows, no transfer limit', len(p0['features']) == 1984 and not p0.get('exceededTransferLimit'))
check('paging probe: offset 1984 returns 0 rows', len(p1['features']) == 0)
check('paging probe IDs = enumerated current IDs', sorted(f['attributes']['PCT_CEB'] for f in p0['features']) == sorted(f['_pid'] for f in csa))

# ---------------------------------------------------------------- per-layer structure checks
audit = {'thresholds': {'change_m2': CHANGE_M2, 'change_fraction': CHANGE_FRAC, 'overlap_gap_m2': OVERLAP_M2,
                        'area_crs': 'EPSG:5070 (NAD83 / Conus Albers equal-area), via pyproj ' + pyproj.__version__},
         'library_versions': {'shapely': shapely.__version__, 'geos': '.'.join(map(str, shapely.geos_version)),
                              'pyproj': pyproj.__version__, 'proj': pyproj.proj_version_str,
                              'pyshp': shapefile.__version__, 'matplotlib': matplotlib.__version__,
                              'pypdfium2': pdfium.V_PYPDFIUM2},
         'layers': {}}


def albers(g):
    return shapely.transform(g, lambda xy: np.column_stack(TO_ALBERS.transform(xy[:, 0], xy[:, 1])))


def ring_issues(geom_json):
    bad = 0
    polys = [geom_json['coordinates']] if geom_json['type'] == 'Polygon' else geom_json['coordinates']
    nv = 0
    for poly in polys:
        for ring in poly:
            nv += len(ring)
            if len(ring) < 4 or ring[0] != ring[-1] or not all(math.isfinite(c) for pt in ring for c in pt):
                bad += 1
    return bad, nv, len(polys), sum(len(p) - 1 for p in polys)


def structure(key, fs, strict=True):
    rep = {'features': len(fs), 'geometry_types': collections.Counter(f['geometry']['type'] if f['geometry'] else None
                                                                     for f in fs),
           'empty': 0, 'ring_defects': 0, 'vertices': 0, 'parts': 0, 'holes': 0, 'invalid': []}
    ids = collections.Counter(f['_pid'] for f in fs)
    rep['duplicate_ids'] = sorted(k for k, v in ids.items() if v > 1)
    rep['bad_id_format'] = sorted(f['_pid'] for f in fs if not re.fullmatch(r'\d{6}', f['_pid']))
    rep['id_county_prefix_mismatch'] = sorted(f['_pid'] for f in fs if f['_pid'][:2] != f['_code'])
    for f in fs:
        if not f['geometry'] or f['_geom'].is_empty:
            rep['empty'] += 1
            continue
        b, nv, parts, holes = ring_issues(f['geometry'])
        rep['ring_defects'] += b
        rep['vertices'] += nv
        rep['parts'] += parts
        rep['holes'] += holes
        if not f['_geom'].is_valid:
            rep['invalid'].append({'precinct_id': f['_pid'], 'object_id': f['id'],
                                   'reason': shapely.is_valid_reason(f['_geom'])})
    rep['geometry_types'] = dict(rep['geometry_types'])
    audit['layers'][key] = rep
    if not strict:
        # Alternative county layers: defects are recorded as findings, not build failures.
        rep['findings'] = {k: rep[k] for k in ('empty', 'ring_defects', 'duplicate_ids', 'bad_id_format',
                                               'id_county_prefix_mismatch') if rep[k]}
        return rep
    check(f'{key}: no empty geometries', rep['empty'] == 0, rep['empty'])
    check(f'{key}: polygon/multipolygon only', set(rep['geometry_types']) <= {'Polygon', 'MultiPolygon'})
    check(f'{key}: closed finite rings with >= 4 positions', rep['ring_defects'] == 0, rep['ring_defects'])
    check(f'{key}: unique precinct IDs', not rep['duplicate_ids'], rep['duplicate_ids'])
    check(f'{key}: six-digit precinct IDs', not rep['bad_id_format'], rep['bad_id_format'][:10])
    check(f'{key}: ID county prefix = county code field', not rep['id_county_prefix_mismatch'],
          rep['id_county_prefix_mismatch'][:10])
    return rep


for key in ('current', 'baseline2024', 'hist2020', 'tulsa_incog_2022', 'mcclain911'):
    structure(key, LAYERS[key], strict=key in ('current', 'baseline2024', 'hist2020', 'tulsa_incog_2022'))
for key in ('current', 'baseline2024'):
    bad = [f['_pid'] for f in LAYERS[key] if f['properties']['CO_FIPS'] != CODE2FIPS[f['_code']][2:]]
    check(f'{key}: CO_FIPS agrees with OSEB county code (census = 2*code-1)', not bad, bad[:10])

# Precompute Albers geometries for priority counties.
PCODES = {FIPS2CODE[f] for f in PRI_FIPS}
for key in ('current', 'baseline2024', 'hist2020', 'tulsa_incog_2022', 'mcclain911'):
    for f in LAYERS[key]:
        f['_alb'] = albers(f['_geom']) if (f['_code'] in PCODES and f['_geom'] is not None) else None


def topology(key, code):
    fs = [f for f in LAYERS[key] if f['_code'] == code]
    geoms = [f['_alb'] for f in fs]
    tree = STRtree(geoms)
    pairs = tree.query(geoms, predicate='intersects')
    overlaps, tiny = [], 0
    for i, j in zip(*pairs):
        if i >= j or not (geoms[i].is_valid and geoms[j].is_valid):
            continue
        a = geoms[i].intersection(geoms[j]).area
        if a > OVERLAP_M2:
            overlaps.append({'a': fs[i]['_pid'], 'b': fs[j]['_pid'], 'area_m2': round(a, 1)})
        elif a > 0:
            tiny += 1
    valid = [g if g.is_valid else shapely.make_valid(g) for g in geoms]
    u = shapely.union_all(valid)
    holes = []
    for p in getattr(u, 'geoms', [u]):
        for ring in p.interiors:
            a = shapely.Polygon(ring).area
            if a > OVERLAP_M2:
                holes.append(round(a, 1))
    parts = len(getattr(u, 'geoms', [u]))
    return {'features': len(fs), 'overlap_pairs_gt_1m2': overlaps, 'tiny_overlap_pairs_le_1m2': tiny,
            'union_parts': parts, 'interior_gaps_gt_1m2': len(holes), 'interior_gap_area_m2': round(sum(holes), 1),
            'largest_gap_m2': max(holes) if holes else 0, 'union_area_km2': round(u.area / 1e6, 3)}


# ---------------------------------------------------------------- current vs baseline geometry
def compare(ka, kb, code):
    A = {f['_pid']: f for f in LAYERS[ka] if f['_code'] == code}
    B = {f['_pid']: f for f in LAYERS[kb] if f['_code'] == code}
    rows = []
    for pid in sorted(set(A) | set(B)):
        a, b = A.get(pid), B.get(pid)
        if a and b:
            ga = a['_alb'] if a['_alb'].is_valid else shapely.make_valid(a['_alb'])
            gb = b['_alb'] if b['_alb'].is_valid else shapely.make_valid(b['_alb'])
            sd = ga.symmetric_difference(gb).area
            area = max(ga.area, gb.area)
            hd = shapely.hausdorff_distance(ga, gb)
            status = 'changed' if (sd > CHANGE_M2 and sd > CHANGE_FRAC * area) else 'same-within-tolerance'
            rows.append({'precinct_id': pid, 'status': status, 'area_a_m2': round(ga.area, 1),
                         'area_b_m2': round(gb.area, 1), 'symdiff_m2': round(sd, 1),
                         'symdiff_fraction': round(sd / area, 8) if area else None, 'hausdorff_m': round(hd, 3)})
        else:
            rows.append({'precinct_id': pid, 'status': f'only-in-{ka}' if a else f'only-in-{kb}', 'area_a_m2':
                         round(a['_alb'].area, 1) if a else None, 'area_b_m2': round(b['_alb'].area, 1) if b else None,
                         'symdiff_m2': None, 'symdiff_fraction': None, 'hausdorff_m': None})
    return rows


def crosswalk(code, chg):
    """Area-only overlay between changed/removed baseline and changed/added current polygons."""
    bset = {c['precinct_id'] for c in chg if c['status'] in ('changed', 'only-in-baseline2024')}
    cset = {c['precinct_id'] for c in chg if c['status'] in ('changed', 'only-in-current')}
    B = {f['_pid']: f['_alb'] for f in LAYERS['baseline2024'] if f['_code'] == code and f['_pid'] in bset}
    C = {f['_pid']: f['_alb'] for f in LAYERS['current'] if f['_code'] == code and f['_pid'] in cset}
    rows, conserve = [], []
    for b, gb in sorted(B.items()):
        tot = 0.0
        for c, gc in sorted(C.items()):
            a = gb.intersection(gc).area
            if a > CHANGE_M2:
                tot += a
                rows.append({'baseline2024_id': b, 'current_id': c, 'intersection_m2': round(a, 1),
                             'share_of_baseline_area': round(a / gb.area, 6), 'share_of_current_area': round(a / gc.area, 6)})
        conserve.append((b, round(tot, 1), round(gb.area, 1)))
    for c, gc in sorted(C.items()):
        tot = sum(r['intersection_m2'] for r in rows if r['current_id'] == c)
        conserve.append((c, round(tot, 1), round(gc.area, 1)))
    return rows, conserve


def compare_alt(alt_key, code):
    """Geometry agreement of a county alternative layer with the current CSA layer, by precinct ID."""
    ids = collections.Counter(f['_pid'] for f in LAYERS[alt_key])
    usable = [f for f in LAYERS[alt_key] if ids[f['_pid']] == 1 and re.fullmatch(r'\d{6}', f['_pid'])]
    cur = {f['_pid']: f for f in LAYERS['current'] if f['_code'] == code}
    out = {'alt_features': len(LAYERS[alt_key]), 'excluded_blank_or_duplicate_ids':
           sorted({f['_pid'] for f in LAYERS[alt_key]} - {f['_pid'] for f in usable}), 'same_within_tolerance': [],
           'different': [], 'alt_only': [], 'current_only': sorted(set(cur) - {f['_pid'] for f in usable})}
    for f in usable:
        c = cur.get(f['_pid'])
        if not c:
            out['alt_only'].append(f['_pid'])
            continue
        ga = f['_alb'] if f['_alb'].is_valid else shapely.make_valid(f['_alb'])
        gc = c['_alb']
        sd = ga.symmetric_difference(gc).area
        if sd > CHANGE_M2 and sd > CHANGE_FRAC * max(ga.area, gc.area):
            out['different'].append({'precinct_id': f['_pid'], 'symdiff_m2': round(sd, 1),
                                     'symdiff_fraction': round(sd / max(ga.area, gc.area), 6)})
        else:
            out['same_within_tolerance'].append(f['_pid'])
    out['same_within_tolerance'] = len(out['same_within_tolerance'])
    return out


# ---------------------------------------------------------------- Hub shapefile vs REST
zb = raw('csa2020/hub-download-shapefile.zip')
z = zipfile.ZipFile(io.BytesIO(zb))
check('hub shapefile ZIP CRCs', z.testzip() is None)
members = {i.filename: {'bytes': i.file_size, 'crc32': f'{i.CRC:08x}', 'zip_datetime': '%04d-%02d-%02d %02d:%02d:%02d' % i.date_time}
           for i in z.infolist()}
stem = [n[:-4] for n in z.namelist() if n.endswith('.shp')][0]
sr = shapefile.Reader(shp=io.BytesIO(z.read(stem + '.shp')), shx=io.BytesIO(z.read(stem + '.shx')),
                      dbf=io.BytesIO(z.read(stem + '.dbf')))
shp_fields = [f[0] for f in sr.fields[1:]]
shp_recs = sr.shapeRecords()
prj = z.read(stem + '.prj').decode()
rest_by = {f['_pid']: f for f in csa}
shp_diff_attr, shp_geom_max, shp_ids = [], 0.0, []
common_fields = [f for f in shp_fields if f in csa[0]['properties']]
for sr_ in shp_recs:
    rec = sr_.record.as_dict()
    pid = rec['PCT_CEB']
    shp_ids.append(pid)
    f = rest_by.get(pid)
    if not f:
        continue
    for k in common_fields:
        a, b = rec[k], f['properties'][k]
        if isinstance(a, float) or isinstance(b, float):
            if a is None or b is None or abs(float(a) - float(b)) > 1e-6 * max(1, abs(float(b))):
                shp_diff_attr.append((pid, k, a, b))
        elif str(a).strip() != str(b if b is not None else '').strip():
            shp_diff_attr.append((pid, k, a, b))
    g = shapely.normalize(shape(sr_.shape.__geo_interface__))
    shp_geom_max = max(shp_geom_max, shapely.hausdorff_distance(g, shapely.normalize(f['_geom'])))
shp_info = {'zip_sha256': sha(zb), 'zip_bytes': len(zb), 'members': members, 'prj': prj, 'records': len(shp_recs),
            'fields': shp_fields, 'fields_compared': common_fields,
            'attribute_differences': [list(map(str, d)) for d in shp_diff_attr[:50]],
            'attribute_difference_count': len(shp_diff_attr),
            'max_hausdorff_degrees_vs_rest': shp_geom_max,
            'last_modified_header': REC['csa2020/hub-download-shapefile.zip']['headers'].get('last-modified'),
            'redirects': REC['csa2020/hub-download-shapefile.zip']['redirects']}
audit['hub_shapefile'] = shp_info
check('hub shapefile: 1984 records, same PCT_CEB set as REST', len(shp_recs) == 1984 and set(shp_ids) == set(rest_by),
      len(shp_recs))
check('hub shapefile: shared attribute values equal REST', not shp_diff_attr, len(shp_diff_attr))
check('hub shapefile: geometry within 1e-6 degrees of REST (Hausdorff)', shp_geom_max < 1e-6, shp_geom_max)
check('hub shapefile: .prj is GCS North American 1983', 'GCS_North_American_1983' in prj)

# ---------------------------------------------------------------- CSA PDF catalogue
search = []
for rid in sorted(k for k in REC if k.startswith('csa/catalog/search-title-precinct-')):
    search += rawj(rid)['results']
cw_page = raw('csa/catalog/hubpage-county-wide-precinct-maps-data.json').decode()
mb_page = raw('csa/catalog/hubpage-precinct-map-books-data.json').decode()
heads = {r['item_id']: r for r in MAN['records'] if r['id'].startswith('csa/pdf-head/')}
pdfs = {r['item_id']: r for r in MAN['records'] if r['id'].startswith('csa/pdf/')}
groups = collections.defaultdict(list)
for rid in sorted(k for k in REC if k.startswith('csa/groups/')):
    groups[REC[rid]['county_fips']] += rawj(rid)['results']
pdf_rows = []
for fips in PRI_FIPS:
    nm = NAME[fips].replace(' ', '')
    for r in search:
        if r['type'] == 'PDF' and r['title'].replace('Le Flore', 'LeFlore').startswith(nm + ' County'):
            role = ('county-wide map (Hub County-wide page)' if r['id'] in cw_page else
                    'map book (Hub Precinct Map Books page)' if r['id'] in mb_page else 'not linked from Hub pages')
            h = heads.get(r['id'])
            d = pdfs.get(r['id'])
            pdf_rows.append({'county_fips': fips, 'county': NAME[fips], 'item_id': r['id'], 'title': r['title'],
                             'kind': role, 'item_created_utc': ms(r['created']), 'item_modified_utc': ms(r['modified']),
                             'modified_after_2024_general': r['modified'] > POST_ELECTION_MS,
                             'content_length': h['headers'].get('content-length') if h else None,
                             'downloaded_path': d['stored_path'] if d else '', 'sha256': d['stored_sha256'] if d else '',
                             'url': f'https://www.arcgis.com/sharing/rest/content/items/{r["id"]}/data'})
    for r in groups[fips]:
        d = pdfs.get(r['id'])
        pdf_rows.append({'county_fips': fips, 'county': NAME[fips], 'item_id': r['id'], 'title': r['title'],
                         'kind': 'individual precinct map (Hub Individual page group)',
                         'item_created_utc': ms(r['created']), 'item_modified_utc': ms(r['modified']),
                         'modified_after_2024_general': r['modified'] > POST_ELECTION_MS, 'content_length': None,
                         'downloaded_path': d['stored_path'] if d else '', 'sha256': d['stored_sha256'] if d else '',
                         'url': f'https://www.arcgis.com/sharing/rest/content/items/{r["id"]}/data'})
check('every priority county has a Hub-linked county-wide PDF and map book',
      all(any(p['county_fips'] == f and p['kind'].startswith('county-wide') for p in pdf_rows) and
          any(p['county_fips'] == f and p['kind'].startswith('map book') for p in pdf_rows) for f in PRI_FIPS))
check('all downloaded PDFs appear in the inventory', set(pdfs) <= {p['item_id'] for p in pdf_rows})

pdf_audit = []
(HERE / 'previews' / 'pdf').mkdir(parents=True, exist_ok=True)
PRODUCED_RE = re.compile(r'Map Produced By:?\s*Center for Spatial Analysis\s*University of Oklahoma\s*'
                         r'((?:January|February|March|April|May|June|July|August|September|October|November|December),?'
                         r'\s*\d{4})')
TITLE_RE = re.compile(r'(?:County Precinct\s+(\d+)|Precinct\s+(\d+)\s+School)')
# Manual visual review (2026-10-18) of PDFs with no extractable text layer; observations, not inferences.
VISUAL_REVIEW = {
    '8727fcd016764fe2a1f54a5c59bfc2a8': {
        'printed_produced_by': 'November, 2023',
        'observation': ('Wagoner County Voter Precincts county-wide map. Footer reads "Map Produced By: Center for '
                        'Spatial Analysis, University of Oklahoma, November, 2023", yet the map labels precincts 105 '
                        'and 211, which are absent from the 2024 OKER results and the January 2025 mirror. The ArcGIS '
                        'item was modified 2025-11-07. The printed date and content disagree; neither is resolved here.')},
    'e37b4128a0374a81b7f14e7e296cf9e4': {
        'printed_produced_by': 'November, 2025',
        'observation': ('Wagoner County Precinct 211 individual map; footer "November, 2025". The current layer '
                        'shows 730211 carved from 2024 precinct 730206 (see geometry-crosswalk.csv).')},
}
for iid, r in sorted(pdfs.items(), key=lambda kv: kv[1]['id']):
    b = (HERE / r['stored_path']).read_bytes()
    doc = pdfium.PdfDocument(b)
    page = doc[0]
    w, h = page.get_size()
    txt = re.sub(r'\s+', ' ', page.get_textpage().get_text_bounded())
    produced = PRODUCED_RE.search(txt)
    title_m = TITLE_RE.search(txt)
    scale = 900 / max(w, h)
    img = page.render(scale=scale).to_pil().convert('RGB').quantize(colors=128)
    prev = HERE / 'previews' / 'pdf' / (pathlib.Path(r['stored_path']).stem + '.png')
    buf = io.BytesIO()
    img.save(buf, format='PNG', optimize=True)
    write(prev, buf.getvalue())
    vr = VISUAL_REVIEW.get(iid, {})
    pdf_audit.append({'path': r['stored_path'], 'item_id': iid, 'title': r['item_title'], 'county_fips': r['county_fips'],
                      'role': r.get('role'), 'pages': len(doc), 'page1_points': [round(w, 1), round(h, 1)],
                      'sha256': sha(b), 'bytes': len(b), 'item_created_utc': ms(r.get('item_created_ms')),
                      'item_modified_utc': ms(r.get('item_modified_ms')),
                      'header_last_modified': r['headers'].get('last-modified'), 'text_chars_page1': len(txt),
                      'printed_produced_by_text': produced.group(1) if produced else None,
                      'printed_produced_by_visual': vr.get('printed_produced_by'),
                      'printed_precinct_number_text': (title_m.group(1) or title_m.group(2)) if title_m else None,
                      'visual_review': vr.get('observation'), 'preview': str(prev.relative_to(HERE))})
    doc.close()
check('every downloaded PDF has a printed production date (text layer or visual review)',
      all(p['printed_produced_by_text'] or p['printed_produced_by_visual'] for p in pdf_audit),
      [p['path'] for p in pdf_audit if not (p['printed_produced_by_text'] or p['printed_produced_by_visual'])])

# ---------------------------------------------------------------- county loop
roster_rows, rec_rows, change_rows, index_rows, county_json, xwalk_rows = [], [], [], [], [], []
(HERE / 'counties').mkdir(exist_ok=True)
(HERE / 'previews').mkdir(exist_ok=True)
manifest_rows = []


def add_manifest(path, **kw):
    b = path.read_bytes()
    row = {'path': str(path.relative_to(HERE)), 'sha256': sha(b), 'bytes': len(b)}
    row.update(kw)
    manifest_rows.append(row)
    return row


def fc(key, fs, fips):
    meta = LAYER_META[key]
    return {'type': 'FeatureCollection', 'crs': {'type': 'name', 'properties': {'name': 'EPSG:4269'}},
            'oklahoma_precinct_maps': {'county': NAME[fips], 'county_fips': fips, 'oseb_county_code': FIPS2CODE[fips],
                                       'layer': meta['label'], 'role': meta['role'], 'publisher': meta['publisher'],
                                       'source_url': meta['source_url'], 'vintage': meta['vintage'],
                                       'native_crs': meta['native_crs'], 'served_crs': meta['served_crs'],
                                       'axis_order': 'longitude, latitude (as served)',
                                       'transformation': 'county filter only; features byte-for-value identical to the server GeoJSON pages'},
            'features': [{k: v for k, v in f.items() if not k.startswith('_')} for f in fs]}


def draw(ax, geoms, fc_, ec, lw, ls='-', z=1, alpha=1.0):
    patches = []
    for g in geoms:
        for p in getattr(g, 'geoms', [g]):
            verts, codes = [], []
            for ring in [p.exterior] + list(p.interiors):
                c = np.asarray(ring.coords)
                verts += c.tolist()
                codes += [MPath.MOVETO] + [MPath.LINETO] * (len(c) - 2) + [MPath.CLOSEPOLY]
            patches.append(PathPatch(MPath(verts, codes)))
    if patches:
        ax.add_collection(PatchCollection(patches, facecolor=fc_, edgecolor=ec, linewidth=lw, linestyle=ls,
                                          zorder=z, alpha=alpha))


for rank, fips in enumerate(PRI_FIPS, 1):
    code = FIPS2CODE[fips]
    name = NAME[fips]
    sl = f'{fips}-{slug(name)}'
    cur = [f for f in csa if f['_code'] == code]
    base = [f for f in mir if f['_code'] == code]
    hist = [f for f in h10 if f['_code'] == code]
    ids = {'current': {f['_pid'] for f in cur}, 'baseline2024': {f['_pid'] for f in base},
           'hist2020': {f['_pid'] for f in hist}}
    res = {y: {p: v for p, v in RESULTS[y].items() if p[:2] == code} for y in RESULTS}
    geo = {y: {p for p in res[y] if p not in NONGEO} for y in res}
    ng = {y: sorted(p for p in res[y] if p in NONGEO) for y in res}
    roster_ind = {r['title'] for r in groups[fips]}
    extra = {}
    if fips == '40143':
        extra['tulsa_incog_2022'] = {f['_pid'] for f in tul}
    if fips == '40087':
        extra['mcclain911'] = {f['_pid'] for f in mcc}
    # Roster.
    every = set().union(*ids.values(), *geo.values(), roster_ind, *extra.values())
    for pid in sorted(every):
        roster_rows.append({'county_fips': fips, 'county': name, 'precinct_id': pid,
                            'in_current_csa_layer': pid in ids['current'],
                            'in_baseline2024_mirror': pid in ids['baseline2024'],
                            'in_csa_individual_map_group': pid in roster_ind,
                            'in_oker_2024_results': pid in geo['2024'], 'in_oker_2022_results': pid in geo['2022'],
                            'in_oker_2020_results': pid in geo['2020'], 'in_csa_pct2010_layer': pid in ids['hist2020'],
                            'in_county_alt_layer': (pid in extra[next(iter(extra))]) if extra else '',
                            'votes_2024_president': res['2024'].get(pid, ''),
                            'votes_2022_senate_special': res['2022'].get(pid, ''),
                            'votes_2020_senate': res['2020'].get(pid, '')})
    # Reconciliation.
    recon = {}
    pairs = [('current', '2024'), ('current', '2022'), ('baseline2024', '2024'), ('baseline2024', '2022'),
             ('hist2020', '2020'), ('csa_individual_maps', '2024')] + [(k, '2024') for k in extra] + \
            [(k, '2020') for k in extra]
    lay_ids = dict(ids, csa_individual_maps=roster_ind, **extra)
    for lk, y in pairs:
        L, G = lay_ids[lk], geo[y]
        m = L & G
        tot_votes = sum(res[y].values())
        unmatched_votes = sum(res[y][p] for p in G - L)
        row = {'county_fips': fips, 'county': name, 'layer': lk, 'results': RACE_LABEL[y], 'layer_features': len(L),
               'results_geographic_units': len(G), 'results_nongeographic_units': ' '.join(ng[y]),
               'matched': len(m), 'results_match_rate': round(len(m) / len(G), 6) if G else None,
               'layer_match_rate': round(len(m) / len(L), 6) if L else None,
               'results_only_ids': ' '.join(sorted(G - L)), 'layer_only_ids': ' '.join(sorted(L - G)),
               'county_contest_votes': tot_votes, 'votes_in_nongeographic_units': sum(res[y][p] for p in ng[y]),
               'votes_in_unmatched_geographic_units': unmatched_votes,
               'vote_weighted_polygon_coverage': round((tot_votes - unmatched_votes - sum(res[y][p] for p in ng[y])) /
                                                       tot_votes, 6) if tot_votes else None}
        rec_rows.append(row)
        recon[f'{lk}~{y}'] = row
    # Geometry change, topology.
    chg = compare('current', 'baseline2024', code)
    for c in chg:
        change_rows.append({'county_fips': fips, 'county': name, **c})
    changed = [c for c in chg if c['status'] != 'same-within-tolerance']
    topo = {k: topology(k, code) for k in ('current', 'baseline2024')}
    if hist:
        topo['hist2020'] = topology('hist2020', code)
    xw, conserve = crosswalk(code, chg)
    for r in xw:
        xwalk_rows.append({'county_fips': fips, 'county': name, **r})
    for pid, tot, area in conserve:
        check(f'{name}: changed precinct {pid} fully covered by crosswalk pieces (within {CHANGE_M2:g} m2)',
              abs(tot - area) <= CHANGE_M2, [tot, area])
    alt_cmp = {k: compare_alt(k, code) for k in extra}
    # County files.
    files = {}
    for key, fs in (('current', cur), ('baseline2024', base), ('hist2020', hist)):
        p = write(HERE / 'counties' / sl / f'{LAYER_META[key]["file_tag"]}.geojson.gz', gz(fc(key, fs, fips)))
        files[key] = add_manifest(p, role=LAYER_META[key]['role'], county_fips=fips, county=name,
                                  publisher=LAYER_META[key]['publisher'], source_url=LAYER_META[key]['source_url'],
                                  vintage=LAYER_META[key]['vintage'], crs='EPSG:4269 lon/lat (GeoJSON crs member)',
                                  native_crs=LAYER_META[key]['native_crs'], feature_count=len(fs),
                                  format='GeoJSON FeatureCollection, gzip-9 mtime 0',
                                  limitations='Derived county subset of raw pages; no simplification, repair or rounding.')
    # Preview.
    fig, ax = plt.subplots(figsize=(7.2, 7.2), dpi=110)
    lat0 = np.mean([f['_geom'].centroid.y for f in cur])
    ax.set_aspect(1 / math.cos(math.radians(lat0)))
    chg_ids = {c['precinct_id'] for c in changed if c['status'] == 'changed'}
    new_ids = ids['current'] - geo['2024']
    gone = [f for f in base if f['_pid'] not in ids['current']]
    draw(ax, [f['_geom'] for f in cur if f['_pid'] not in chg_ids | new_ids], '#e8edf2', '#41556b', 0.35)
    draw(ax, [f['_geom'] for f in cur if f['_pid'] in chg_ids - new_ids], '#f6c55b', '#7a5200', 0.6, z=2)
    draw(ax, [f['_geom'] for f in cur if f['_pid'] in new_ids], '#e4572e', '#6b1b06', 0.7, z=3)
    draw(ax, [f['_geom'] for f in gone], 'none', '#1b4f9c', 1.1, ls='--', z=4)
    fsz = 5.5 if len(cur) <= 45 else 4.5 if len(cur) <= 120 else 3
    for f in cur:
        pt = f['_geom'].representative_point()
        ax.text(pt.x, pt.y, str(int(f['_pid'][2:])), fontsize=fsz, ha='center', va='center', color='#1d2733', zorder=5)
    ax.autoscale_view()
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    sub = (f'{len(cur)} current polygons (CSA, data edit {ms(csa_layer["editingInfo"]["dataLastEditDate"])[:10]}); '
           f'2024 results IDs matched {recon["current~2024"]["matched"]}/{len(geo["2024"])}')
    if ng['2024']:
        sub += f'\nNon-geographic results unit {ng["2024"][0]} (all absentee + early votes) has no polygon'
    ax.set_title(f'{name} County ({fips}) precincts\n', fontsize=11, loc='left')
    ax.text(0, 1.0, sub, transform=ax.transAxes, fontsize=7.5, va='bottom', color='#333')
    handles = [Patch(facecolor='#e8edf2', edgecolor='#41556b', label='current = 2024 baseline (within tolerance)')]
    if chg_ids - new_ids:
        handles.append(Patch(facecolor='#f6c55b', edgecolor='#7a5200', label=f'geometry changed since 2024 baseline ({len(chg_ids - new_ids)})'))
    if new_ids:
        handles.append(Patch(facecolor='#e4572e', edgecolor='#6b1b06', label=f'ID not in 2024 results ({len(new_ids)})'))
    if gone:
        handles.append(Patch(facecolor='none', edgecolor='#1b4f9c', linestyle='--', label=f'2024 precinct absent now ({len(gone)})'))
    ax.legend(handles=handles, loc='upper left', bbox_to_anchor=(0, -0.01), fontsize=7, frameon=False, ncol=1,
              title='Labels: precinct number (last 4 ID digits). Preview only: NAD83 lon/lat, no basemap; not an official map.',
              title_fontsize=6, alignment='left')
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=110, bbox_inches='tight', metadata={'Software': None})
    plt.close(fig)
    from PIL import Image
    im = Image.open(io.BytesIO(buf.getvalue())).convert('RGB').quantize(colors=64)
    b2 = io.BytesIO()
    im.save(b2, format='PNG', optimize=True)
    prev = write(HERE / 'previews' / f'{sl}.png', b2.getvalue())
    add_manifest(prev, role='preview (derivative image; not for analysis)', county_fips=fips, county=name,
                 publisher='generated by build.py', source_url='', vintage='current vs baseline2024',
                 crs='display only', native_crs='', feature_count=len(cur), format='PNG',
                 limitations='Rendered from county GeoJSON; quantized colours; no basemap.')
    # Status.
    id_same = ids['current'] == ids['baseline2024'] == geo['2024']
    geom_changed = sorted(c['precinct_id'] for c in chg if c['status'] == 'changed')
    status = ('current-equals-2024-baseline' if id_same and not geom_changed else 'current-differs-from-2024-baseline')
    county_pdfs = [p for p in pdf_rows if p['county_fips'] == fips]
    late = [p for p in county_pdfs if p['modified_after_2024_general']]
    index_rows.append({
        'priority_rank': rank, 'county': name, 'county_fips': fips, 'oseb_county_code': code,
        'status': status, 'november_2026_approval': 'not established',
        'current_features': len(cur), 'current_path': files['current']['path'], 'current_sha256': files['current']['sha256'],
        'baseline2024_features': len(base), 'baseline2024_path': files['baseline2024']['path'],
        'baseline2024_sha256': files['baseline2024']['sha256'],
        'hist2020_features': len(hist), 'hist2020_path': files['hist2020']['path'],
        'results2024_geographic_units': len(geo['2024']), 'results2024_nongeographic_units': ' '.join(ng['2024']),
        'current_vs_2024_matched': recon['current~2024']['matched'],
        'current_vs_2024_results_match_rate': recon['current~2024']['results_match_rate'],
        'current_vs_2024_layer_match_rate': recon['current~2024']['layer_match_rate'],
        'baseline_vs_2024_results_match_rate': recon['baseline2024~2024']['results_match_rate'],
        'current_vs_2022_results_match_rate': recon['current~2022']['results_match_rate'],
        'baseline_vs_2022_results_match_rate': recon['baseline2024~2022']['results_match_rate'],
        'hist2020_vs_2020_results_match_rate': recon['hist2020~2020']['results_match_rate'],
        'current_vote_weighted_polygon_coverage_2024': recon['current~2024']['vote_weighted_polygon_coverage'],
        'ids_added_since_2024': ' '.join(sorted(ids['current'] - ids['baseline2024'])),
        'ids_removed_since_2024': ' '.join(sorted(ids['baseline2024'] - ids['current'])),
        'geometry_changed_since_2024': ' '.join(geom_changed),
        'current_invalid_geometries': ' '.join(sorted(i['precinct_id'] for i in audit['layers']['current']['invalid']
                                                      if i['precinct_id'][:2] == code)),
        'current_overlap_pairs_gt_1m2': len(topo['current']['overlap_pairs_gt_1m2']),
        'current_interior_gaps_gt_1m2': topo['current']['interior_gaps_gt_1m2'],
        'zero_vote_precincts_2024': ' '.join(sorted(p for p in geo['2024'] if res['2024'][p] == 0)),
        'crosswalk_rows': len(xw),
        'csa_individual_maps': len(roster_ind),
        'csa_pdf_items_modified_after_2024_general': len(late),
        'preview': str(prev.relative_to(HERE)),
    })
    county_json.append({'priority_rank': rank, 'county': name, 'county_fips': fips, 'oseb_county_code': code,
                        'status': status, 'files': {k: v['path'] for k, v in files.items()},
                        'preview': str(prev.relative_to(HERE)), 'reconciliation': recon, 'topology': topo,
                        'geometry_changes_vs_baseline2024': changed, 'geometry_crosswalk_area_only': xw,
                        'alternative_layer_comparison': alt_cmp,
                        'pdfs_modified_after_2024_general': [{k: p[k] for k in ('title', 'kind', 'item_modified_utc',
                                                                                 'downloaded_path')} for p in late]})

# Statewide reconciliation (for context).
state = {}
for lk, L in (('current', {f['_pid'] for f in csa}), ('baseline2024', {f['_pid'] for f in mir}),
              ('hist2020_all_counties', {a['PCT_CEB'] for a in a10})):
    for y in RESULTS:
        G = set(RESULTS[y]) - NONGEO
        state[f'{lk}~{y}'] = {'layer_features': len(L), 'results_geographic_units': len(G), 'matched': len(L & G),
                              'layer_only': sorted(L - G), 'results_only': sorted(G - L)}
check('statewide: 2024 baseline mirror IDs = 2024 OKER geographic IDs (1984)',
      not state['baseline2024~2024']['layer_only'] and not state['baseline2024~2024']['results_only'])
check('statewide: CSA 2010 layer IDs = 2020 OKER geographic IDs (1948)',
      not state['hist2020_all_counties~2020']['layer_only'] and not state['hist2020_all_counties~2020']['results_only'])

# Statewide overview preview.
fig, ax = plt.subplots(figsize=(9, 4.6), dpi=110)
ax.set_aspect(1 / math.cos(math.radians(35.5)))
pri_codes = {FIPS2CODE[f] for f in PRI_FIPS}
draw(ax, [f['_geom'] for f in csa if f['_code'] not in pri_codes], '#f4f4f4', '#b9b9b9', 0.15)
draw(ax, [f['_geom'] for f in csa if f['_code'] in pri_codes], '#cfe0f3', '#3d6a99', 0.2, z=2)
for fips in PRI_FIPS:
    u = shapely.union_all([shapely.make_valid(f['_geom']) for f in csa if f['_code'] == FIPS2CODE[fips]])
    draw(ax, [u], 'none', '#0d2c4f', 0.9, z=3)
    c = u.representative_point()
    ax.text(c.x, c.y, NAME[fips], fontsize=5, ha='center', va='center', zorder=4)
ax.autoscale_view()
ax.set_xticks([])
ax.set_yticks([])
for s in ax.spines.values():
    s.set_visible(False)
ax.set_title('Oklahoma: 26 priority counties (blue) over 1,984 current CSA precinct polygons', fontsize=10, loc='left')
buf = io.BytesIO()
fig.savefig(buf, format='png', dpi=110, bbox_inches='tight', metadata={'Software': None})
plt.close(fig)
from PIL import Image  # noqa: E402
im = Image.open(io.BytesIO(buf.getvalue())).convert('RGB').quantize(colors=64)
b2 = io.BytesIO()
im.save(b2, format='PNG', optimize=True)
ov = write(HERE / 'previews' / 'statewide-priority.png', b2.getvalue())
add_manifest(ov, role='preview (derivative image; not for analysis)', county_fips='40', county='statewide',
             publisher='generated by build.py', source_url='', vintage='current', crs='display only', native_crs='',
             feature_count=len(csa), format='PNG', limitations='Overview only.')
for p in pdf_audit:
    add_manifest(HERE / p['preview'], role='preview of CSA PDF page 1 (derivative image)', county_fips=p['county_fips'],
                 county=NAME[p['county_fips']], publisher='generated by build.py', source_url='', vintage='',
                 crs='', native_crs='', feature_count='', format='PNG', limitations='Page-1 render at <=900 px.')

# Raw originals into the manifest.
ROLE = {'csa2020/': 'original: CSA current statewide layer pages / metadata',
        'csa2010/': 'original: CSA 2010-census layer (2020 context)', 'incog-state/': 'original: INCOG statewide mirror',
        'incog-tulsa/': 'original: INCOG Tulsa County 2022 layer (alternative)',
        'mcclain911/': 'original: McClain County 911 layer (alternative)', 'csa/pdf/': 'original: CSA precinct-map PDF',
        'csa/': 'original: CSA catalogue evidence', 'oseb/': 'original: OSEB authority page',
        'statute/': 'original: Oklahoma Statutes Title 26'}
for r in MAN['records']:
    if not r.get('stored_path'):
        continue
    role = next(v for k, v in ROLE.items() if r['id'].startswith(k))
    fcnt = ''
    if '/features-' in r['id']:
        fcnt = len(rawj(r['id'])['features'])
    elif r['id'] == 'csa2020/hub-download-shapefile.zip':
        fcnt = 1984
    add_manifest(HERE / r['stored_path'], role=role, county_fips=r.get('county_fips', ''), county='',
                 publisher='', source_url=r['url'], vintage=f'retrieved {r["retrieval_utc"]}',
                 crs='EPSG:4269 (outSR)' if r['id'].endswith('.geojson') else '', native_crs='', feature_count=fcnt,
                 format=r['storage'], limitations=r.get('note', ''))

# ---------------------------------------------------------------- write tables
def wcsv(name, rows):
    if not rows:
        return
    out = io.StringIO()
    w = csv.DictWriter(out, fieldnames=list(rows[0].keys()), lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
    write(HERE / name, out.getvalue())


wcsv('index.csv', index_rows)
wcsv('precinct-roster.csv', roster_rows)
wcsv('id-reconciliation.csv', rec_rows)
wcsv('geometry-changes.csv', [r for r in change_rows])
wcsv('pdf-inventory.csv', pdf_rows)
wcsv('geometry-crosswalk.csv', xwalk_rows)
audit['statewide_reconciliation'] = state
audit['counties'] = {c['county_fips']: c['topology'] for c in county_json}
write(HERE / 'geometry-audit.json', json.dumps(audit, indent=1, default=str) + '\n')
write(HERE / 'pdf-audit.json', json.dumps(pdf_audit, indent=1) + '\n')
write(HERE / 'read-only-pins.json', json.dumps(pins, indent=1, sort_keys=True) + '\n')
index = {
    'title': 'Oklahoma 2026 U.S. Senate: precinct map index for the 26-county priority set',
    'priority_set': 'Exact 25-county 2024-president minimum 80% set (turnout.md) plus Kay (2022/2020 Senate 80% sets).',
    'layers': LAYER_META,
    'nongeographic_units': {'559999': 'Oklahoma County countywide absentee-mail + early unit; no polygon',
                            '729999': 'Tulsa County countywide absentee-mail + early unit; no polygon'},
    'november_2026_approval': ('Not established for any county. No public roster of units approved for November 3, '
                               '2026 reporting was found; OKER 2026 exports sit behind the app sign-in, which this '
                               'assignment does not use. 26 O.S. 3-118 allows precinct changes in 2025-2026 after a '
                               '30-day posted/mailed notice.'),
    'statewide_reconciliation': {k: {kk: (vv if not isinstance(vv, list) or len(vv) <= 20 else f'{len(vv)} IDs; see geometry-audit.json')
                                     for kk, vv in v.items()} for k, v in state.items()},
    'counties': county_json,
}
write(HERE / 'index.json', json.dumps(index, indent=1, default=str) + '\n')

# Offline HTML gallery.
cards = []
for r in index_rows:
    cards.append(
        f'<article><h2>{r["priority_rank"]}. {html.escape(r["county"])} <small>{r["county_fips"]}</small></h2>'
        f'<a href="{r["preview"]}"><img src="{r["preview"]}" alt="{html.escape(r["county"])} precinct preview" '
        f'loading="lazy"></a><p class="{r["status"]}">{r["status"].replace("-", " ")}</p>'
        f'<p>{r["current_features"]} current polygons; 2024 IDs matched {r["current_vs_2024_matched"]}/'
        f'{r["results2024_geographic_units"]}{"; non-geographic unit " + r["results2024_nongeographic_units"] if r["results2024_nongeographic_units"] else ""}</p>'
        f'<p><a href="{r["current_path"]}">current GeoJSON.gz</a> · <a href="{r["baseline2024_path"]}">2024 baseline</a> · '
        f'<a href="{r["hist2020_path"]}">2020 context</a></p></article>')
page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Oklahoma precinct maps</title><style>
:root{{--bg:#fff;--fg:#1d2733;--muted:#5b6876;--card:#f5f7f9;--warn:#8a5a00}}
@media (prefers-color-scheme:dark){{:root{{--bg:#11161c;--fg:#e6edf3;--muted:#9aa7b4;--card:#1b232c;--warn:#f0b54a}}}}
body{{background:var(--bg);color:var(--fg);font:15px/1.45 system-ui,sans-serif;margin:0 auto;max-width:1200px;padding:16px}}
main{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px}}
article{{background:var(--card);border-radius:8px;padding:10px}} img{{width:100%;height:auto;background:#fff;border-radius:4px}}
h2{{font-size:16px;margin:0 0 6px}} small,p{{color:var(--muted);font-size:13px;margin:6px 0}}
.current-differs-from-2024-baseline{{color:var(--warn);font-weight:600}} a{{color:inherit}}
</style></head><body><h1>Oklahoma precinct maps: 26 priority counties</h1>
<p>Generated offline by build.py from the CSA statewide layer (current, data edit 2025-11-05), the INCOG mirror of the January 2025 CSA file (2024 baseline) and the CSA 2010-census layer (2020 context). See <a href="../precinct-maps.md">precinct-maps.md</a>. Previews are not official maps. No November 2026 approval is established.</p>
<p><img src="previews/statewide-priority.png" alt="Statewide overview" style="max-width:900px"></p>
<main>{"".join(cards)}</main></body></html>
'''
write(HERE / 'index.html', page)

# Manifest of owned assets (raw + derived); excludes this manifest itself and scripts/reports.
manifest_rows.sort(key=lambda r: r['path'])
wcsv('manifest.csv', manifest_rows)
write(HERE / 'checks.json', json.dumps({'checks': checks, 'passed': sum(c['pass'] for c in checks),
                                        'failed': sum(not c['pass'] for c in checks)}, indent=1, default=str) + '\n')
print(f'{sum(c["pass"] for c in checks)} checks passed, {sum(not c["pass"] for c in checks)} failed')
sys.exit(0 if all(c['pass'] for c in checks) else 1)
