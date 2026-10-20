"""Independent coordinator audit of complete originals, native geometry and static atlas.

No producer modules or writers are imported. Owned package bytes remain frozen.
"""
from pathlib import Path
from collections import Counter
from html.parser import HTMLParser
import gzip, hashlib, json, math, re, struct, subprocess, tempfile, urllib.parse
import shapely.geometry, shapely.validation

S = Path(__file__).resolve().parents[1]
M = S / 'maps'
N = 0

def ck(value, label=''):
    global N
    N += 1
    assert value, (N, label)

def sha(b):
    return hashlib.sha256(b).hexdigest()

def load(path):
    p = S / path
    b = p.read_bytes()
    return json.loads(gzip.decompress(b) if p.suffix == '.gz' else b)

def exact(r):
    b = (S / r['path']).read_bytes()
    ck(len(b) == r['bytes'] and sha(b) == r['sha256'], r['path'])
    return b

manifest = load('maps/manifest.json')
ck(manifest['excludes_only'] == 'maps/manifest.json')
owned = {str(p.relative_to(S)) for p in M.rglob('*') if p.is_file()} | {'precinct-maps.md'}
rows = manifest['owned_files']
ck(len(rows) == len({r['path'] for r in rows}) == 710)
ck({r['path'] for r in rows} == owned - {'maps/manifest.json'})
for r in rows:
    ck(r['bytes'] < 40000000)
    exact(r)
for r in manifest['fixed_external_build_inputs']:
    exact(r)
for r in manifest['external_complete_original_references']:
    b = (S / r['path']).read_bytes()
    ck(len(b) == r['stored_bytes'] and sha(b) == r['stored_sha256'])
    raw = gzip.decompress(b) if r['compression'] == 'gzip' else b
    ck(len(raw) == r['raw_bytes'] and sha(raw) == r['raw_sha256'])
authority_digest = sha((S / 'data/coordinator-priority-acceptance.json').read_bytes())
for p in M.rglob('*'):
    ck(not set(p.relative_to(M).parts) & {'__pycache__', 'node_modules', '.pytest_cache', '.venv'})
    if p.is_file() and p.suffix in ['.py', '.json', '.md', '.html']:
        ck(authority_digest.encode() not in p.read_bytes())
for r in load('maps/final-seal.json')['proofs']:
    exact(r)
for p in ['maps/final-seal.json', 'maps/qa/validation.json']:
    ck(sha((M / 'manifest.json').read_bytes()).encode() not in (S / p).read_bytes())

requests = {}
raws = {}
statuses = Counter()
hops = 0
unique_entities = set()
all_parts = set()
for p in sorted((M / 'requests').glob('*.json')):
    r = json.loads(p.read_bytes())
    ck(r['id'] == p.stem and r['request_method'] == 'GET' and r['request_body'] is None)
    ck(r['requested_url'] and r['utc_start'] and r['utc_end'] and isinstance(r['configured_headers'], dict))
    requests[r['id']] = r
    for h in r['hops']:
        hops += 1
        if 'status' in h:
            statuses[h['status']] += 1
            ck(h['url'] and h['utc'] and isinstance(h['headers'], list))
        if 'parts' not in h:
            continue
        parts = []
        for i, part in enumerate(h['parts']):
            b = (M / part['path']).read_bytes()
            ck(part['part'] == i and len(b) == part['stored_bytes'] < 40000000 and sha(b) == part['stored_sha256'])
            raw = gzip.decompress(b)
            ck(len(raw) == part['raw_bytes'] and sha(raw) == part['raw_sha256'])
            parts.append(raw)
            all_parts.add(part['path'])
        raw = b''.join(parts)
        ck(len(raw) == h['raw_bytes'] and sha(raw) == h['raw_sha256'])
        unique_entities.add(sha(raw))
        raws[r['id']] = raw
ck(len(requests) == 197)
ck(all_parts == {str(p.relative_to(M)) for p in (M / 'originals').glob('*')})
ck(load('maps/source/acquisition-index.json')['request_ids'] == sorted(requests))

native = {}
native_oids = {}
native_summary = []
native_audit = load('maps/qa/native-audit.json')
for prefix, indexpath in [('rigis', 'maps/source/native-batches.json'), ('sos', 'maps/source/sos-native-batches.json')]:
    idx = load(indexpath)
    before = {k: json.loads(raws[prefix + '-' + k + '-pre']) for k in ['service', 'layer', 'count', 'ids']}
    after = {k: json.loads(raws[prefix + '-' + k + '-post']) for k in before}
    ck(before == after)
    ck(all(raws[prefix + '-' + k + '-pre'] == raws[prefix + '-' + k + '-post'] for k in ['service', 'layer']))
    ids = before['ids']['objectIds']
    oid = before['ids']['objectIdFieldName']
    native_oids[prefix] = oid
    ck(len(ids) == len(set(ids)) == before['count']['count'] == 416)
    fields = {f['name'] for f in before['layer']['fields'] if f['type'] != 'esriFieldTypeGeometry'}
    features = []
    for page in idx['batches']:
        r = requests[page['request']]
        q = urllib.parse.parse_qs(urllib.parse.urlsplit(r['requested_url']).query)
        ck(set(q) == {'f', 'objectIds', 'outFields', 'returnGeometry', 'returnZ', 'returnM', 'returnTrueCurves'})
        ck(q['outFields'] == ['*'] and all(q[k] == ['true'] for k in ['returnGeometry', 'returnZ', 'returnM', 'returnTrueCurves']))
        asked = list(map(int, q['objectIds'][0].split(',')))
        ck(asked == page['requested_ids'] and len(asked) <= 50)
        response = json.loads(raws[page['request']])
        got = [f['attributes'][oid] for f in response['features']]
        ck(got == page['returned_ids'] and set(got) == set(asked) and len(got) == len(asked))
        ck(not response.get('exceededTransferLimit', False))
        ck(response['spatialReference'] == idx['native_crs'])
        for f in response['features']:
            ck(set(f['attributes']) == fields)
        features += response['features']
    ck(len(idx['batches']) == 9)
    ck(len(features) == 416 and sorted(f['attributes'][oid] for f in features) == sorted(ids))
    ck(features == load('maps/derived/' + prefix + '-native-features.json.gz'))
    qa = native_audit[prefix]
    ck(qa['prepost_exact_semantic_changes'] == {'service': [], 'layer': []})
    rings = positions = 0
    valid_single = invalid_single = 0
    for f, row in zip(features, qa['features'], strict=True):
        ck(row['attributes'] == f['attributes'] and row['objectid'] == f['attributes'][oid])
        g = f.get('geometry')
        ck(g is not None and set(g) == {'rings'})
        hh = hashlib.sha256()
        points = []
        for ring in g['rings']:
            rings += 1
            for point in ring:
                positions += 1
                ck(len(point) == 2 and all(isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) for x in point))
                for value in point:
                    hh.update(struct.pack('<d', value))
                points.append(point)
        d = row['geometry_audit']
        ck(hh.hexdigest() == d['ordered_all_ordinate_IEEE754_sha256'])
        ck(d['positions'] == sum(map(len, g['rings'])))
        ck(d['native_bbox'] == [min(x[0] for x in points), min(x[1] for x in points), max(x[0] for x in points), max(x[1] for x in points)])
        if len(g['rings']) == 1:
            ring = g['rings'][0]
            ck(len(ring) >= 4 and ring[0] == ring[-1])
            shape = shapely.geometry.Polygon(ring)
            ck(shape.is_valid == d['single_ring_GEOS_valid'] and shapely.validation.explain_validity(shape) == d['single_ring_GEOS_reason'])
            valid_single += shape.is_valid
            invalid_single += not shape.is_valid
    ck(valid_single == qa['single_ring_valid_intersection_scope'])
    ck(not qa['positive_area_intersection_diagnostics'])
    native[prefix] = features
    native_summary.append(dict(source=prefix, features=416, batches=9, CRS=idx['native_crs'], rings=rings, XY_positions=positions, valid_single_ring_subset=valid_single, invalid_single_ring=invalid_single, full_prepost_equal=True))
ck(native['rigis'] != native['sos'])
ck([(r['rings'], r['XY_positions']) for r in native_summary] == [(1584, 151257), (420, 151110)])

c = load('data/turnout/priority-set.json')
ck(gzip.decompress((M / 'derived/full-source-contract.json.gz').read_bytes()) == (S / 'data/turnout/priority-set.json').read_bytes())
o = load('maps/derived/context-observations.json')
full = c['complete_descending_order']
inv = c['all_source_native_constituents']
parents = c['municipal_and_administrative_parent_sensitivity']['full_inventory']
ck(len(full) == 458 and len(inv) == 497 and len(parents) == 43)
ck(o['ordered_full_keys'] == [x['key'] for x in full])
ck(o['ordered_priority_keys'] == [x['key'] for x in full[:242]] == c['ordered_priority_keys'])
ck(o['ordered_remainder_keys'] == [x['key'] for x in full[242:]])
ck(all(x is False for x in o['approvals'].values()))
ck(len(o['all_497_inventory_observations']) == 497 and len(o['ordered_full_observations']) == 458)
observations = {r['source_key']: r for r in o['ordered_full_observations']}
for a, b in zip(o['ordered_full_observations'], full, strict=True):
    ck(a['source_key'] == b['key'] and a['source_anchor'] == b['source_anchor'] and a['source_inventory_key'] == b['native_key'] and a['parent_key'] == b['parent_key'])
    ck(set(a['gaps']) == {'access', 'vintage', 'crs', 'finer', 'current', 'legal', 'physical', 'ballotstyle'})
for r, p in zip(o['complete_parent_resource_records'], parents, strict=True):
    ck(r['complete_parent'] == p)
    children = [x for x in full if x['parent_key'] == p['key']]
    ck(r['child_arrays'] == o['parent_child_arrays'][p['key']] == dict(original_ordered_native_inventory_keys=p['native_keys'], full_source_rank_ordered_children=[x['key'] for x in children], ordered_priority_children=[x['key'] for x in children if x['key'] in o['ordered_priority_keys']], ordered_remainder_children=[x['key'] for x in children if x['key'] not in o['ordered_priority_keys']]))
    ck(r['inventory_constituent_ranked_keys'] == [x['key'] for x in full if x['native_key'] in p['native_keys']])
    if p['geography_type'] == 'municipality':
        ck(set(r['shared_native_resources']) == {'rigis', 'sos'})
        for prefix in native:
            res = r['shared_native_resources'][prefix]
            positions = [dict(full_array_position=i, objectid=f['attributes'][native_oids[prefix]], attributes=f['attributes']) for i, f in enumerate(native[prefix]) if f['attributes']['TOWN'] == p['name']]
            ck(positions == res['feature_positions'] and len(positions) == res['feature_count'])
            ck(res['current_approval'] is False and res['legal_approval'] is False)
    else:
        ck(r['shared_native_resources'] == {} and r['physical_geometry_available'] is False)
ck(sum(p['geography_type'] == 'municipality' for p in parents) == 39)
directory = load('maps/source/directory-observation.json')
ck(len(directory['literal_municipal_links']) == 39 and len(directory['priority_order']) == 37)
for slug in directory['priority_order']:
    ck('municipal-' + slug in requests)

class DOM(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.stack = []; self.pre = None; self.objects = []; self.keys = []; self.parents = []; self.links = []; self.scripts = 0
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ['script', 'iframe']: self.scripts += 1
        if tag == 'details': self.stack.append(a)
        if tag == 'pre': self.pre = ''
        if tag == 'li' and 'data-key' in a: self.keys.append(a['data-key'])
        if tag == 'li' and 'data-parent' in a: self.parents.append(a['data-parent'])
        for k in ['href', 'src']:
            if k in a: self.links.append(a[k])
    def handle_data(self, text):
        if self.pre is not None: self.pre += text
    def handle_endtag(self, tag):
        if tag == 'pre' and self.pre is not None:
            self.objects.append((self.stack[-1]['class'], json.loads(self.pre)))
            self.pre = None
        if tag == 'details': self.stack.pop()

doms = {}; links = 0
for p in M.rglob('*.html'):
    d = DOM(p.read_text()); doms[p] = d; ck(d.scripts == 0)
    for u in d.links:
        v = urllib.parse.urlsplit(u)
        if v.scheme or u.startswith('//'): continue
        target = (p.parent / urllib.parse.unquote(v.path)).resolve() if v.path else p
        ck(target.is_file(), (str(p), u)); links += 1
for mode, values in [('priority', full[:242]), ('full', full), ('remainder', full[242:])]:
    d = doms[M / (mode + '.html')]
    ck(d.keys == [r['key'] for r in values])
    ck([v for cl, v in d.objects if cl == 'ranked-object'] == values)
    ck([v for cl, v in d.objects if cl == 'qualification'] == [observations[r['key']] for r in values])
for p, r in zip(parents, o['complete_parent_resource_records'], strict=True):
    d = doms[M / 'parents' / (r['slug'] + '.html')]
    ck([v for cl, v in d.objects if cl == 'constituent'] == [x for x in inv if x['key'] in p['native_keys']])
    ck([v for cl, v in d.objects if cl == 'parent-object'] == [r])
    ck([v for cl, v in d.objects if cl == 'ranked-object'] == [x for x in full if x['native_key'] in p['native_keys']])
ck(doms[M / 'index.html'].parents == directory['priority_order'])

pdfs = load('maps/qa/pdf-rendering.json')
ck(pdfs['original_pdf_count'] == 21 and pdfs['total_pages'] == 36)
ck({r['request'] for r in pdfs['publications']} == {k for k, b in raws.items() if b.startswith(b'%PDF') and requests[k]['hops'][-1]['status'] == 200})
with tempfile.TemporaryDirectory(prefix='ri-root-map-pdf-') as tmp:
    for r in pdfs['publications']:
        raw = raws[r['request']]
        ck(sha(raw) == r['raw_sha256'])
        p = Path(tmp) / 'source.pdf'; p.write_bytes(raw)
        info = subprocess.run(['pdfinfo', str(p)], capture_output=True, check=True, timeout=20).stdout.decode()
        ck(int(re.search(r'^Pages:\s*(\d+)', info, re.M).group(1)) == r['pages'] == len(r['rendered_all_pages']))
        for image in r['rendered_all_pages']:
            ck((M / image).read_bytes().startswith(b'\x89PNG\r\n\x1a\n'))

result = dict(status='pass_independent_full_map_source_native_DOM_review', checks=N, owned_manifest_targets=710, complete_owned_files=711, complete_original_external_refs=148, own_requests=len(requests), own_response_hops=hops, unique_response_entities=len(unique_entities), response_statuses=dict(statuses), native_sources=native_summary, all_priority_source_objects=242, complete_full_ranked_objects=458, explicit_remainder=216, inventory_objects=497, full_parent_objects=43, municipalities=39, priority_municipal_chains=37, static_HTML_pages=len(doms), local_HTML_links=links, original_PDFs=21, automatically_rendered_PDF_pages=36, coordinator_actual_manual_scope=dict(whole_original_PDF_pages=['Cranston citywide map page1', 'Glocester2026 map page1'], complete_native_previews=['SOS Cranston'], other_pages_claimed_manually=False), shapefile_binary_audit_claim=False, spatial_allocation=False, current_or_legal_leaf_match_approval=False, producer_writes_or_imports=False, reviewed_manifest=dict(path='maps/manifest.json', bytes=(M/'manifest.json').stat().st_size, sha256=sha((M/'manifest.json').read_bytes())))
(S / 'data/coordinator-maps-final-review.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(dict(status=result['status'], checks=N, features=832, HTML_pages=len(doms), PDF_pages=36)))
