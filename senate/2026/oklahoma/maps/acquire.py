#!/usr/bin/env python3
"""Acquire Oklahoma precinct-boundary evidence for the 26-county research priority.

Network script, standard library only. Run from the repository root:

    PYTHONDONTWRITEBYTECODE=1 uv run --with certifi==2024.8.30 python3 -I senate/2026/oklahoma/maps/acquire.py

certifi is optional and only supplies a CA bundle: www.oklegislature.gov chains
to Sectigo Public Server Authentication Root R46, which the macOS
/etc/ssl/cert.pem used by uv's Python lacks. Without certifi the system bundle
is used and that one request fails verification. TLS verification is never
disabled.

It re-downloads every source into senate/2026/oklahoma/maps/raw/ and rewrites
maps/source-manifest.json (one record per HTTP request: requested URL,
redirect chain with pre-signed storage URLs cut at the query, status,
selected response headers, UTC start/end times, SHA-256 and byte size of
the response body as received and as stored). Text bodies are
stored gzip-compressed (level 9, mtime 0, lossless); ZIP and PDF bodies are
stored byte-for-byte as received. A refresh replaces the working snapshot, so
preserve the previous raw/ tree first if it matters.

Sources (all public, no sign-in or token):
  * Oklahoma State Election Board (OSEB) "District and Precinct Maps" page,
    which names the OU Center for Spatial Analysis (CSA) Data Warehouse as the
    download location for GIS precinct maps.
  * CSA ArcGIS Online organisation 3xOwF6p0r7IHIjfn: hosted layer
    "Voter Precincts 2020" (State_Wide_2020_Precincts, layer pct_2020), its
    Hub shapefile download, and "Voter Precincts 2010" (Voter_Precints,
    PCT_2010) for the pre-2022 (2020 election) context, subset to the
    priority counties.
  * CSA precinct-map PDF catalogue (Hub pages, county groups, item metadata,
    HEAD sizes) plus a bounded set of PDFs for counties whose CSA maps were
    modified after the 2024 general election.
  * INCOG (Indian Nations Council of Governments) mirrors: statewide
    PCT_OK_State ("File was downloaded from CSA January 2025") and the
    Tulsa County layer PCT_TulsaCo (CSA, April 2022).
  * McClain County 911 "VotingPrecincts" hosted layer (county agency copy).
  * Oklahoma Statutes Title 26 (official compiled PDF) for 26 O.S. 3-118.

ArcGIS layers are enumerated with returnIdsOnly and fetched in object-ID
batches of 250 (well under maxRecordCount=2000) so a transfer limit cannot
silently truncate them. A resultOffset paging probe is also stored.
"""
import datetime
import gzip
import ssl
import hashlib
import json
import pathlib
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
RAW = HERE / 'raw'
MANIFEST = HERE / 'source-manifest.json'
UA = 'Mozilla/5.0 (compatible; election-research/1.0)'
BATCH = 250
POST_ELECTION_MS = 1730851200000  # 2024-11-06T00:00:00Z, day after the 2024 general election

# Priority order = 2024-president rank (turnout.md); Kay appended (rank 26).
# (county, 5-digit FIPS, OSEB 2-digit county code, CSA hub category label)
PRIORITY = [
    ('Oklahoma', '40109', '55', 'Oklahoma County'), ('Tulsa', '40143', '72', 'Tulsa County'),
    ('Cleveland', '40027', '14', 'Cleveland County'), ('Canadian', '40017', '09', 'Canadian County'),
    ('Rogers', '40131', '66', 'Rogers County'), ('Wagoner', '40145', '73', 'Wagoner County'),
    ('Comanche', '40031', '16', 'Comanche County'), ('Creek', '40037', '19', 'Creek County'),
    ('Payne', '40119', '60', 'Payne County'), ('Pottawatomie', '40125', '63', 'Pottawatomie County'),
    ('Grady', '40051', '26', 'Grady County'), ('Muskogee', '40101', '51', 'Muskogee County'),
    ('Logan', '40083', '42', 'Logan County'), ('Washington', '40147', '74', 'Washington County'),
    ('Garfield', '40047', '24', 'Garfield County'), ('McClain', '40087', '44', 'McClain County'),
    ('Osage', '40113', '57', 'Osage County'), ('Carter', '40019', '10', 'Carter County'),
    ('Le Flore', '40079', '40', 'Le Flore County'), ('Stephens', '40137', '69', 'Stephens County'),
    ('Delaware', '40041', '21', 'Delaware County'), ('Cherokee', '40021', '11', 'Cherokee County'),
    ('Bryan', '40013', '07', 'Bryan County'), ('Pittsburg', '40121', '61', 'Pittsburg County'),
    ('Mayes', '40097', '49', 'Mayes County'), ('Kay', '40071', '36', 'Kay County'),
]
CODES = [p[2] for p in PRIORITY]

AGOL = 'https://www.arcgis.com/sharing/rest'
CSA_ORG = '3xOwF6p0r7IHIjfn'
CSA2020_ITEM = '8c2c841e2eb54007bd1872c4274d6e07'
CSA2020 = 'https://services.arcgis.com/3xOwF6p0r7IHIjfn/arcgis/rest/services/State_Wide_2020_Precincts/FeatureServer'
CSA2010_ITEM = 'c83b09af406d48f7bbca30942fe186a8'
CSA2010 = 'https://services.arcgis.com/3xOwF6p0r7IHIjfn/arcgis/rest/services/Voter_Precints/FeatureServer'
CSA_HUB = 'https://csagis-uok.opendata.arcgis.com'
HUB_PAGES = {
    'precinct-maps': '9a627dc066e24cecb8b13e265def6caf',
    'county-wide-precinct-maps': '1d27628ba98d45ee8f44f4e5b6295b1c',
    'individual-precinct-maps': 'f75954e2b0f3491b84f328f65f868b4e',
    'precinct-map-books': 'cda51207f98f42eb8e7e945508c0e939',
}
INCOG_STATE = 'https://map11.incog.org/arcgis11wa/rest/services/PCT_OK_State'
INCOG_TULSA = 'https://map11.incog.org/arcgis11wa/rest/services/PCT_TulsaCo'
MCCLAIN911_ITEM = '6fb0fb11d2264184965e1551dde04ea5'
MCCLAIN911 = 'https://services3.arcgis.com/rZNttx9YenKXG402/arcgis/rest/services/VotingPrecincts/FeatureServer'
OSEB_MAPS = 'https://oklahoma.gov/elections/candidates/district-and-precinct-maps.html'
STATUTE26 = 'https://www.oklegislature.gov/OK_Statutes/CompleteTitles/os26.pdf'

KEEP_HEADERS = ('content-type', 'content-length', 'last-modified', 'etag', 'content-disposition', 'date',
                'cache-control', 'server', 'x-esri-ftiles-cache-compress', 'location')
records = []
try:
    import certifi
    SSL_CTX = ssl.create_default_context(cafile=certifi.where())
    CA_BUNDLE = f'certifi {certifi.__version__}'
except ImportError:
    SSL_CTX = ssl.create_default_context()
    CA_BUNDLE = 'system default'


def now():
    return datetime.datetime.now(datetime.UTC).isoformat(timespec='milliseconds').replace('+00:00', 'Z')


def sha(b):
    return hashlib.sha256(b).hexdigest()


def unsigned(url):
    """Drop the query of a pre-signed storage URL (temporary AWS credential and signature)."""
    return url.split('?', 1)[0] if url and 'X-Amz-' in url else url


class Recorder(urllib.request.HTTPRedirectHandler):
    def __init__(self):
        self.chain = []

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.chain.append({'status': code, 'from': req.full_url, 'location': unsigned(headers.get('Location'))})
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def http(url, method='GET'):
    last = None
    for attempt in range(4):
        rec = Recorder()
        opener = urllib.request.build_opener(rec, urllib.request.HTTPSHandler(context=SSL_CTX))
        req = urllib.request.Request(url, method=method, headers={'User-Agent': UA, 'Accept': '*/*'})
        start = now()
        try:
            with opener.open(req, timeout=180) as r:
                status, hdrs, body = r.status, r.headers, r.read()
        except urllib.error.HTTPError as e:
            status, hdrs, body = e.code, e.headers, e.read()
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            last = e
            time.sleep(2 * (attempt + 1))
            continue
        meta = {'retrieval_utc': start, 'completed_utc': now(), 'method': method, 'url': url,
                'redirects': rec.chain, 'status': status, 'attempt': attempt + 1,
                'headers': {k.lower(): v for k, v in hdrs.items() if k.lower() in KEEP_HEADERS}}
        if status >= 500 and attempt < 3:
            time.sleep(2 * (attempt + 1))
            continue
        return meta, body
    raise SystemExit(f'network failure for {url}: {last}')


def store(rel, url, note=None, method='GET', binary=False, extra=None):
    """Fetch url and store under raw/rel (text gets .gz). Returns (record, body)."""
    meta, body = http(url, method=method)
    path = RAW / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    rec = {'id': rel, **meta, 'body_sha256': sha(body), 'body_bytes': len(body)}
    if method == 'HEAD':
        rec['stored_path'] = None
    else:
        data = body if binary else gzip.compress(body, compresslevel=9, mtime=0)
        if not binary:
            path = path.with_name(path.name + '.gz')
        path.write_bytes(data)
        rec.update({'stored_path': str(path.relative_to(HERE)), 'stored_sha256': sha(data), 'stored_bytes': len(data),
                    'storage': 'as-received' if binary else 'gzip-9-mtime0'})
    if note:
        rec['note'] = note
    if extra:
        rec.update(extra)
    records.append(rec)
    if meta['status'] != 200:
        print(f'WARN {meta["status"]} {url}', flush=True)
    print(f'{meta["status"]} {len(body):>10} {rel}', flush=True)
    return rec, body


def jget(rel, url, note=None, extra=None):
    rec, body = store(rel, url, note=note, extra=extra)
    try:
        return json.loads(body)
    except ValueError:
        raise SystemExit(f'non-JSON response for {url}')


def q(base, **params):
    return base + '/query?' + urllib.parse.urlencode(params)


def layer_capture(prefix, layer_url, where='1=1', geojson=True, out_sr='4269', note=None, oid_field=None,
                  attrs_only=False):
    """Enumerate a layer by IDs, then fetch features in object-ID batches."""
    info = jget(f'{prefix}/layer.json', layer_url + '?f=json', note=note)
    count = jget(f'{prefix}/count.json', q(layer_url, where=where, returnCountOnly='true', f='json'))['count']
    ids = jget(f'{prefix}/ids.json', q(layer_url, where=where, returnIdsOnly='true', f='json'))
    # MapServer layer JSON may omit objectIdField; the IDs response always names it.
    oid = oid_field or info.get('objectIdField') or ids.get('objectIdFieldName')
    if not oid:
        raise SystemExit(f'{prefix}: no object-ID field name')
    oids = sorted(ids['objectIds'] or [])
    if len(oids) != count:
        raise SystemExit(f'{prefix}: returnIdsOnly {len(oids)} != count {count}')
    got = 0
    for i in range(0, len(oids), BATCH):
        chunk = oids[i:i + BATCH]
        params = dict(objectIds=','.join(map(str, chunk)), outFields='*', orderByFields=oid,
                      f='geojson' if geojson else 'json')
        if attrs_only:
            params['returnGeometry'] = 'false'
        elif out_sr:
            params['outSR'] = out_sr
        d = jget(f'{prefix}/features-{i // BATCH + 1:03d}.{"geojson" if geojson else "json"}', q(layer_url, **params),
                 extra={'batch_object_ids': [chunk[0], chunk[-1]], 'batch_size_requested': len(chunk)})
        n = len(d.get('features', []))
        flag = d.get('exceededTransferLimit') or (d.get('properties') or {}).get('exceededTransferLimit')
        if n != len(chunk) or flag:
            raise SystemExit(f'{prefix}: batch {i // BATCH + 1} returned {n}/{len(chunk)} exceeded={flag}')
        got += n
    if got != count:
        raise SystemExit(f'{prefix}: fetched {got} != count {count}')
    return info, count


def main():
    RAW.mkdir(exist_ok=True)
    # 1. Authority chain and law.
    store('oseb/district-and-precinct-maps.html', OSEB_MAPS,
          note='OSEB page naming the CSA Data Warehouse as the GIS precinct-map download location.')
    store('statute/os26.pdf', STATUTE26, binary=True,
          note='Official compiled Oklahoma Statutes Title 26 (Elections); 26 O.S. 3-118 governs precinct changes.')

    # 2. CSA catalogue.
    store('csa/catalog/hub-home.html', CSA_HUB + '/', note='CSA Hub site linked from the OSEB page.')
    start = 1
    while start > 0:
        d = jget(f'csa/catalog/search-title-precinct-{start:04d}.json',
                 AGOL + '/search?' + urllib.parse.urlencode({'q': f'title:precinct orgid:{CSA_ORG}', 'num': 100,
                                                            'start': start, 'sortField': 'title', 'sortOrder': 'asc',
                                                            'f': 'json'}))
        start = d.get('nextStart', -1)
    pages = {}
    for name, pid in HUB_PAGES.items():
        jget(f'csa/catalog/hubpage-{name}-item.json', f'{AGOL}/content/items/{pid}?f=json')
        pages[name] = jget(f'csa/catalog/hubpage-{name}-data.json', f'{AGOL}/content/items/{pid}/data?f=json')
    groups = {}

    def walk(o):
        if isinstance(o, dict):
            if o.get('name') == 'category-card':
                s = o.get('settings', {})
                groups[s.get('category')] = s.get('groupId')
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for x in o:
                walk(x)
    walk(pages['individual-precinct-maps'])
    group_rows = {}
    for county, fips, code, label in PRIORITY:
        gid = groups.get(label) or groups.get(label.replace(' County', ''))
        if not gid:
            raise SystemExit(f'no CSA individual-map group for {label}')
        rows, start = [], 1
        while start > 0:
            d = jget(f'csa/groups/{fips}-group-search-{start:04d}.json',
                     f'{AGOL}/content/groups/{gid}/search?' + urllib.parse.urlencode(
                         {'q': '*', 'num': 100, 'start': start, 'sortField': 'title', 'sortOrder': 'asc', 'f': 'json'}),
                     extra={'county_fips': fips, 'group_id': gid})
            rows += d.get('results', [])
            start = d.get('nextStart', -1)
        group_rows[fips] = rows

    # County-wide maps and map books: item metadata + HEAD size for every priority-county precinct PDF item.
    search = []
    for p in sorted((RAW / 'csa/catalog').glob('search-title-precinct-*.json.gz')):
        search += json.loads(gzip.decompress(p.read_bytes()))['results']
    norm = lambda t: t.replace('Le Flore', 'LeFlore')
    county_items = []
    for county, fips, code, label in PRIORITY:
        for r in search:
            if r['type'] == 'PDF' and norm(r['title']).startswith(norm(county) + ' County'):
                county_items.append((fips, r))
    for fips, r in county_items:
        store(f'csa/pdf-head/{fips}-{r["id"]}.head', f'{AGOL}/content/items/{r["id"]}/data', method='HEAD',
              extra={'county_fips': fips, 'item_id': r['id'], 'item_title': r['title']})

    # Bounded PDF downloads: CSA PDFs (re)modified after the 2024 general election.
    # County-wide map items modified after 2024-11-05, and individual precinct maps modified after it, except
    # where a county re-exported every individual map at once (all modified post-election), in which case only
    # individual maps *created* after the election are taken.
    cw_ids = set()
    walk_ids = json.dumps(pages['county-wide-precinct-maps'])
    for fips, r in county_items:
        if r['id'] in walk_ids and r['title'].endswith('Voter Precincts'):
            cw_ids.add(r['id'])
            if r['modified'] > POST_ELECTION_MS:
                store(f'csa/pdf/{fips}-countywide-{r["id"]}.pdf', f'{AGOL}/content/items/{r["id"]}/data', binary=True,
                      extra={'county_fips': fips, 'item_id': r['id'], 'item_title': r['title'],
                             'item_modified_ms': r['modified'], 'role': 'county-wide precinct map'})
    for county, fips, code, label in PRIORITY:
        rows = group_rows[fips]
        late_mod = [r for r in rows if r['modified'] > POST_ELECTION_MS]
        bulk = rows and len(late_mod) == len(rows)
        take = [r for r in rows if r['created'] > POST_ELECTION_MS] if bulk else late_mod
        for r in take:
            store(f'csa/pdf/{fips}-precinct-{r["title"]}-{r["id"]}.pdf', f'{AGOL}/content/items/{r["id"]}/data',
                  binary=True, extra={'county_fips': fips, 'item_id': r['id'], 'item_title': r['title'],
                                      'item_created_ms': r['created'], 'item_modified_ms': r['modified'],
                                      'role': 'individual precinct map', 'selection': 'created-after-election' if bulk
                                      else 'modified-after-election'})

    # 3. CSA statewide 2020-census precinct layer (current published layer).
    jget('csa2020/item.json', f'{AGOL}/content/items/{CSA2020_ITEM}?f=json')
    store('csa2020/item-metadata.xml', f'{AGOL}/content/items/{CSA2020_ITEM}/info/metadata/metadata.xml')
    jget('csa2020/service.json', CSA2020 + '?f=json')
    layer_capture('csa2020', CSA2020 + '/0', note='CSA Voter Precincts 2020, layer pct_2020, native EPSG:4269.')
    jget('csa2020/paging-probe-offset0.json', q(CSA2020 + '/0', where='1=1', outFields='OBJECTID_1,PCT_CEB',
                                                returnGeometry='false', resultOffset=0, resultRecordCount=2000,
                                                orderByFields='OBJECTID_1', f='json'))
    jget('csa2020/paging-probe-offset1984.json', q(CSA2020 + '/0', where='1=1', outFields='OBJECTID_1,PCT_CEB',
                                                   returnGeometry='false', resultOffset=1984, resultRecordCount=2000,
                                                   orderByFields='OBJECTID_1', f='json'))
    store('csa2020/hub-download-shapefile.zip',
          f'{CSA_HUB}/api/download/v1/items/{CSA2020_ITEM}/shapefile?layers=0', binary=True,
          note='CSA Hub (Data Warehouse) shapefile download; redirects to a cached hub.arcgis.com export.')

    # 4. CSA 2010-census precinct layer (2020 election context): statewide attributes, priority geometry.
    jget('csa2010/item.json', f'{AGOL}/content/items/{CSA2010_ITEM}?f=json')
    jget('csa2010/service.json', CSA2010 + '?f=json')
    layer_capture('csa2010/statewide-attributes', CSA2010 + '/0', attrs_only=True, geojson=False,
                  note='Attributes only, all counties.')
    where = 'COUNTY IN (' + ','.join(f"'{c}'" for c in CODES) + ')'
    layer_capture('csa2010/priority-geometry', CSA2010 + '/0', where=where,
                  note='Geometry for the 26 priority counties only (bounded subset).')

    # 5. INCOG mirrors.
    jget('incog-state/mapserver.json', INCOG_STATE + '/MapServer?f=json')
    jget('incog-state/featureserver.json', INCOG_STATE + '/FeatureServer?f=json')
    jget('incog-state/mapserver-layer0.json', INCOG_STATE + '/MapServer/0?f=json')
    layer_capture('incog-state', INCOG_STATE + '/FeatureServer/0',
                  note='INCOG mirror of the CSA statewide file; native EPSG:2267 (ArcGIS 102724); served outSR=4269.')
    jget('incog-tulsa/mapserver-layer0.json', INCOG_TULSA + '/MapServer/0?f=json')
    jget('incog-tulsa/iteminfo.json', INCOG_TULSA + '/MapServer/0/iteminfo?f=json')
    layer_capture('incog-tulsa', INCOG_TULSA + '/MapServer/0',
                  note='INCOG Tulsa County precinct layer (CSA, April 2022); native EPSG:2267; served outSR=4269.')

    # 6. McClain County 911 hosted copy.
    jget('mcclain911/item.json', f'{AGOL}/content/items/{MCCLAIN911_ITEM}?f=json')
    layer_capture('mcclain911', MCCLAIN911 + '/0', note='McClain County 911 VotingPrecincts layer.')

    records.sort(key=lambda r: r['id'])
    MANIFEST.write_text(json.dumps({'generated_utc': now(), 'user_agent': UA, 'ca_bundle': CA_BUNDLE, 'records': records}, indent=1) + '\n')
    print(f'{len(records)} records -> {MANIFEST.relative_to(HERE.parent)}')


if __name__ == '__main__':
    sys.exit(main())
