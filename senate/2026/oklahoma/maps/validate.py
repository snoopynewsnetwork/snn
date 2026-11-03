#!/usr/bin/env python3
"""Offline validation of the Oklahoma precinct-map package (standard library only).

Run from the repository root after build.py:

    PYTHONDONTWRITEBYTECODE=1 uv run python3 -I senate/2026/oklahoma/maps/validate.py

Re-checks independently of build.py: raw and derived hashes, the 40 MB object
bound, unlisted files, county GeoJSON structure and counts, ID match rates
against the pinned OKER precinct exports, ArcGIS enumeration/pagination
evidence, read-only pins and every relative link in precinct-maps.md and
index.html. Writes maps/validation.json (which also records SHA-256/bytes of
the scripts and reports that are not in manifest.csv) and exits non-zero on
any failure.
"""
import collections
import csv
import gzip
import hashlib
import io
import json
import pathlib
import re
import sys
import urllib.parse
import zipfile

HERE = pathlib.Path(__file__).resolve().parent
STATE = HERE.parent
LIMIT = 40 * 1000 * 1000
results = []


def check(name, ok, detail=None):
    results.append({'check': name, 'pass': bool(ok), 'detail': detail})
    if not ok:
        print('FAIL', name, detail, file=sys.stderr)


def sha(b):
    return hashlib.sha256(b).hexdigest()


# 1. Raw evidence.
man = json.loads((HERE / 'source-manifest.json').read_text())
stored = set()
for r in man['records']:
    if not r.get('stored_path'):
        continue
    p = HERE / r['stored_path']
    stored.add(r['stored_path'])
    b = p.read_bytes()
    ok = sha(b) == r['stored_sha256'] and len(b) == r['stored_bytes']
    if r['storage'] == 'gzip-9-mtime0':
        body = gzip.decompress(b)
        ok = ok and sha(body) == r['body_sha256'] and len(body) == r['body_bytes']
    check(f'raw {r["id"]}', ok)
check('raw: every request returned HTTP 200', all(r['status'] == 200 for r in man['records']))

# 2. Manifest of owned assets.
rows = list(csv.DictReader(open(HERE / 'manifest.csv', encoding='utf-8')))
listed = set()
for r in rows:
    b = (HERE / r['path']).read_bytes()
    listed.add(r['path'])
    check(f'manifest {r["path"]}', sha(b) == r['sha256'] and len(b) == int(r['bytes']))
check('manifest lists every stored raw file', stored <= listed, sorted(stored - listed)[:5])

# 3. Size bound and unlisted files.
OTHER = {'acquire.py', 'build.py', 'validate.py', 'source-manifest.json', 'manifest.csv', 'index.csv', 'index.json',
         'index.html', 'checks.json', 'geometry-audit.json', 'pdf-audit.json', 'pdf-inventory.csv',
         'precinct-roster.csv', 'id-reconciliation.csv', 'geometry-changes.csv', 'geometry-crosswalk.csv',
         'read-only-pins.json', 'validation.json'}
files = sorted(p for p in HERE.rglob('*') if p.is_file())
big = [(str(p.relative_to(HERE)), p.stat().st_size) for p in files if p.stat().st_size >= LIMIT]
check('every file < 40,000,000 bytes', not big, big)
unlisted = [str(p.relative_to(HERE)) for p in files if str(p.relative_to(HERE)) not in listed | OTHER]
check('no unlisted files (no caches, no strays)', not unlisted, unlisted[:10])
md = STATE / 'precinct-maps.md'
check('precinct-maps.md < 40 MB', md.stat().st_size < LIMIT)

# 4. Pinned read-only inputs.
pins = json.loads((HERE / 'read-only-pins.json').read_text())
for rel, v in pins.items():
    b = (STATE / rel).read_bytes()
    check(f'read-only pin {rel}', sha(b) == v['sha256'] and len(b) == v['bytes'])

# 5. Priority set.
ct = list(csv.DictReader(open(STATE / 'data' / 'county-turnout.csv', encoding='utf-8')))
pri = [r['county_fips'] for r in ct if r['pres2024_min80'] == 'True'] + ['40071']
idx = list(csv.DictReader(open(HERE / 'index.csv', encoding='utf-8')))
check('index.csv = 25 county 2024 80% set + Kay, in turnout order', [r['county_fips'] for r in idx] == pri,
      [r['county_fips'] for r in idx])
code = {r['county_fips']: r['oseb_county_code'] for r in ct}

# 6. OKER results (pinned).
def oker(date):
    z = zipfile.ZipFile(STATE / f'data/turnout/raw/oker-{date}-precinct-csv.zip')
    with z.open(z.namelist()[0]) as f:
        return {row['precinct'] for row in csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig'))}


res = {'2024': oker('20241105'), '2022': oker('20221108'), '2020': oker('20201103')}
nongeo = {'559999', '729999'}

# 7. County GeoJSON recomputation.
for r in idx:
    c = code[r['county_fips']]
    for key, path, feat_col in (('current', r['current_path'], 'current_features'),
                                ('baseline2024', r['baseline2024_path'], 'baseline2024_features'),
                                ('hist2020', r['hist2020_path'], 'hist2020_features')):
        d = json.loads(gzip.decompress((HERE / path).read_bytes()))
        fs = d['features']
        ids = [f['properties']['PCT_CEB'] for f in fs]
        ok = (d['type'] == 'FeatureCollection' and d['crs']['properties']['name'] == 'EPSG:4269' and
              len(fs) == int(r[feat_col]) and len(set(ids)) == len(ids) and all(i[:2] == c for i in ids) and
              all(f['geometry']['type'] in ('Polygon', 'MultiPolygon') for f in fs) and
              all(f['properties']['COUNTY'] == c for f in fs))
        check(f'{r["county"]} {key}: structure, count, unique in-county IDs', ok)
        for ring_ok in [all(len(rg) >= 4 and rg[0] == rg[-1]
                            for f in fs for poly in ([f['geometry']['coordinates']] if f['geometry']['type'] == 'Polygon'
                                                     else f['geometry']['coordinates']) for rg in poly)]:
            check(f'{r["county"]} {key}: closed rings', ring_ok)
        if key == 'current':
            geo = {p for p in res['2024'] if p[:2] == c and p not in nongeo}
            m = len(set(ids) & geo)
            check(f'{r["county"]}: current vs 2024 results match rate',
                  abs(m / len(geo) - float(r['current_vs_2024_results_match_rate'])) < 1e-6 and
                  m == int(r['current_vs_2024_matched']), [m, len(geo)])
            ng = sorted(p for p in res['2024'] if p[:2] == c and p in nongeo)
            check(f'{r["county"]}: non-geographic units', ' '.join(ng) == r['results2024_nongeographic_units'])
        if key == 'baseline2024':
            geo = {p for p in res['2024'] if p[:2] == c and p not in nongeo}
            check(f'{r["county"]}: baseline mirror IDs = 2024 results geographic IDs', set(ids) == geo)

# 8. ArcGIS enumeration evidence from raw pages.
recs = {r['id']: r for r in man['records']}


def rawj(i):
    b = (HERE / recs[i]['stored_path']).read_bytes()
    return json.loads(gzip.decompress(b) if recs[i]['storage'] == 'gzip-9-mtime0' else b)


for prefix, ext in (('csa2020', 'geojson'), ('incog-state', 'geojson'), ('csa2010/priority-geometry', 'geojson'),
                    ('csa2010/statewide-attributes', 'json'), ('incog-tulsa', 'geojson'), ('mcclain911', 'geojson')):
    n = rawj(f'{prefix}/count.json')['count']
    ids = rawj(f'{prefix}/ids.json')['objectIds']
    pages = sorted(k for k in recs if k.startswith(prefix + '/features-'))
    got = []
    for k in pages:
        d = rawj(k)
        got += [f.get('id', (f.get('attributes') or {}).get('OBJECTID_1')) for f in d['features']]
        check(f'{k}: no exceededTransferLimit', not d.get('exceededTransferLimit') and
              not (d.get('properties') or {}).get('exceededTransferLimit'))
    check(f'{prefix}: count = IDs = features fetched ({n})', n == len(ids) == len(got) and sorted(got) == sorted(ids),
          [n, len(ids), len(got)])
lay = rawj('csa2020/layer.json')
check('csa2020 maxRecordCount 2000; 250-ID batches used', lay['maxRecordCount'] == 2000 and
      all(r.get('batch_size_requested', 0) <= 250 for r in man['records']))

# 9. Build checks file.
bc = json.loads((HERE / 'checks.json').read_text())
check('build checks.json: zero failures', bc['failed'] == 0 and bc['passed'] > 0, [bc['passed'], bc['failed']])

# 10. Links.
def links(path, text, pattern):
    bad = []
    for target in re.findall(pattern, text):
        t = urllib.parse.unquote(target.split('#')[0])
        if not t or re.match(r'^[a-z]+:', t):
            continue
        dest = (path.parent / t).resolve()
        if dest == (HERE / 'validation.json').resolve():
            continue  # written by this script below
        if not dest.exists():
            bad.append(target)
    return bad


mdtext = md.read_text(encoding='utf-8')
check('precinct-maps.md: relative links resolve', not links(md, mdtext, r'\]\(([^)\s]+)\)'),
      links(md, mdtext, r'\]\(([^)\s]+)\)'))
ht = (HERE / 'index.html').read_text(encoding='utf-8')
check('index.html: relative href/src resolve', not links(HERE / 'index.html', ht, r'(?:href|src)="([^"]+)"'),
      links(HERE / 'index.html', ht, r'(?:href|src)="([^"]+)"')[:5])

# Hashes of owned files not in manifest.csv (scripts, reports, tables); validation.json excluded (self).
owned = {}
for name in sorted(OTHER - {'validation.json'}):
    b = (HERE / name).read_bytes()
    owned[f'maps/{name}'] = {'sha256': sha(b), 'bytes': len(b)}
b = md.read_bytes()
owned['precinct-maps.md'] = {'sha256': sha(b), 'bytes': len(b)}
total = sum(p.stat().st_size for p in files)
out = {'checks': results, 'passed': sum(r['pass'] for r in results), 'failed': sum(not r['pass'] for r in results),
       'files': len(files), 'total_bytes': total, 'largest_file': max(((str(p.relative_to(HERE)), p.stat().st_size)
                                                                       for p in files), key=lambda x: x[1]),
       'owned_file_hashes': owned}
(HERE / 'validation.json').write_text(json.dumps(out, indent=1) + '\n')
print(f'{out["passed"]} passed, {out["failed"]} failed; {len(files)} files, {total} bytes')
sys.exit(1 if out['failed'] else 0)
