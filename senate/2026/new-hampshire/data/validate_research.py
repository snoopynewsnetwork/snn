#!/usr/bin/env python3
"""Coordinator historical, source, map and whole-package integration."""
from pathlib import Path
import ast
import contextlib
import datetime
import gzip
import hashlib
import io
import json
import re
import runpy
from html.parser import HTMLParser
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
D = ROOT/'data'
load = lambda p: json.loads(p.read_text())
sha = lambda b: hashlib.sha256(b).hexdigest()
for name in ['review_priority.py','review_targets.py']:
    with contextlib.redirect_stdout(io.StringIO()):
        runpy.run_path(str(D/name),run_name='__main__')
counts = {}
for folder,expected in [('turnout',211),('baselines',124)]:
    manifest = load(D/folder/'asset-manifest.json')
    entries = manifest['assets']
    assert len(entries) == len({r['path'] for r in entries}) == expected
    for r in entries:
        b = (ROOT/r['path']).read_bytes()
        assert len(b) == r['bytes'] < 40_000_000 and sha(b) == r['sha256'],r['path']
    counts[folder] = len(entries)
refs = load(D/'baselines/asset-manifest.json')['shared_original_references']
assert len(refs) == 79
for r in refs:
    b = (ROOT/r['path']).read_bytes()
    assert sha(b) == r['stored_sha256']
    raw = gzip.decompress(b) if b[:2] == b'\x1f\x8b' else b
    # The shared reference identifies decoded source bytes where HTTP gzip exists.
    if raw[:2] == b'\x1f\x8b' and sha(raw) != r['original_sha256']:
        raw = gzip.decompress(raw)
    assert sha(raw) == r['original_sha256'] and len(raw) == r['original_bytes'],r['path']
a = load(D/'coordinator-priority-acceptance.json')
b = (D/a['contract']).read_bytes()
assert a['accepted'] and len(b) == a['contract_bytes'] == 3653481
assert sha(b) == a['contract_sha256'] == '11c042966c67a50e496ad6f839afd8e3c8b28afe6e2761c6cda1aa51f7ce90fc'
for key in ['independent_coordinator_review','peer_agreement']:
    r = a[key]
    assert sha((ROOT/r['path']).read_bytes()) == r['sha256']
turnout = load(D/'turnout/validation.json')
baseline = load(D/'baselines/validation.json')
assert turnout['status'] == 'pass'
assert baseline['status'] == 'pass_with_explicit_primary_source_disagreements_and_operational_gaps'
assert load(D/'turnout/peer-agreement.json')['status'] == 'agreed_after_independent_full_comparison'
links = 0
for p in [ROOT/'turnout.md',ROOT/'county-partisanship.md',D/'turnout/source/SCHEMA.md',D/'baselines/source/SCHEMA.md']:
    for dest in re.findall(r'\]\(([^)]+)\)',p.read_text()):
        dest = dest.strip().strip('<>')
        if not dest or dest.startswith(('http:','https:','#','mailto:','data:')):
            continue
        assert (p.parent/unquote(dest.split('#')[0])).exists(),(p,dest)
        links += 1
for folder in ['turnout','baselines']:
    for p in (D/folder).rglob('*'):
        assert p.name not in ['node_modules','__pycache__','.venv']
        if p.is_file():
            assert p.stat().st_size < 40_000_000 and p.suffix != '.pyc'
            if p.suffix == '.py':
                ast.parse(p.read_text(),filename=str(p))
out = {'status':'pass_first_wave_only_full_integration_pending',
       'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
       'native_reporting_leaves':320,'county_controls':10,'retained_rosters':23,
       'source_scoped_records':7360,'original_field_checks':34880,
       'reported_candidate_generic_denominator':826189,'priority_units':143,
       'priority_votes':662624,'preceding_votes':660378,'remainder_units':177,
       'state_targets':16,'native_targets':5120,'county_targets':160,'synthetic_remainders':20,
       'worker_asset_hashes':counts,'shared_original_hashes':len(refs),'first_wave_relative_links':links,
       'contract_sha256':sha(b),'current_geometry_approved':False,'current_results_feed_approved':False,
       'collector_implemented':False,'calibrated_forecast':False,
       'scope':'Historical first-wave source/target/asset reconciliation only; official-results/maps research and complete state publication remain pending.'}
p = D/'coordinator-first-wave-validation.json'
if p.exists():
    previous = load(p)
    if {k:v for k,v in previous.items()if k!='checked_utc'} == {k:v for k,v in out.items()if k!='checked_utc'}:
        out['checked_utc'] = previous['checked_utc']
p.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))

# Full four-question package, after actual completion/freeze of all workers.
for name in ['review_results.py','review_maps.py','news/inspect_evidence.py']:
    with contextlib.redirect_stdout(io.StringIO()):
        runpy.run_path(str(D/name),run_name='__main__')
for path,expected,key in [(D/'results-sources/asset-manifest.json',2994,'owned_assets'),
                          (ROOT/'maps/asset-manifest.json',1252,'assets')]:
    m=load(path)
    assert len(m[key])==expected
    for r in m[key]:
        b=(ROOT/r['path']).read_bytes()
        assert len(b)==r['bytes']<40_000_000 and sha(b)==r['sha256'],r['path']
for r in load(D/'results-sources/asset-manifest.json')['read_only_references']:
    b=(ROOT/r['path']).read_bytes()
    assert len(b)==r['bytes'] and sha(b)==r['sha256'],r['path']
assert load(D/'results-sources/validation.json')['status']=='pass_with_explicit_primary_source_disagreements_and_operational_gaps'
assert load(ROOT/'maps/validation.json')['status']=='pass'
class Links(HTMLParser):
    def __init__(self):
        super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        self.links += [v for k,v in attrs if k in ['href','src'] and v]
all_links=0;files=0;total=0;largest={'bytes':0}
for p in ROOT.rglob('*'):
    assert p.name not in ['node_modules','__pycache__','.venv']
    if not p.is_file():continue
    n=p.stat().st_size;assert n<40_000_000 and p.suffix!='.pyc',p
    if p==(D/'coordinator-checks.json'):continue
    files+=1;total+=n
    if n>largest['bytes']:largest={'path':str(p.relative_to(ROOT)),'bytes':n}
    if p.suffix=='.py':ast.parse(p.read_text(),filename=str(p))
    destinations=[]
    if p.suffix=='.md':destinations=re.findall(r'\]\(([^)]+)\)',p.read_text())
    elif p.suffix=='.html':
        h=Links();h.feed(p.read_text());destinations=h.links
    for dest in destinations:
        dest=dest.strip().strip('<>')
        if not dest or dest.startswith(('http:','https:','#','mailto:','data:','javascript:','tel:')):continue
        local=unquote(dest.split('#')[0].split('?')[0])
        target=(p.parent/local).resolve()
        assert target.exists() or target==(D/'coordinator-checks.json').resolve(),(p.relative_to(ROOT),dest)
        all_links+=1
final={'status':'pass_with_documented_source_and_operational_gaps',
       'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
       'scope':'Complete four-question research package, coordinator news/strategy and independent original/source/map/target review; no current live implementation or geographic approval.',
       'native_leaves':320,'source_rosters':23,'source_scoped_records':7360,
       'original_field_checks':34880,'priority':143,'priority_votes':662624,'denominator':826189,
       'state_targets':16,'native_targets':5120,'county_targets':160,'synthetic_remainders':20,
       'assignment_asset_hashes':{'turnout':211,'partisanship':124,'official_results':2994,'maps':1252},
       'total_assignment_asset_hashes':4581,'official_read_only_references':360,
       'official_response_captures':705,'official_priority_parent_inspections':98,'current_primary_municipal_channels':79,
       'map_response_captures':145,'map_full_coordinate_derivatives':468,'map_PDF_capture_records':44,'map_actual_PDF_pages':124,
       'news_response_captures':len(load(D/'news/manifest.json')),
       'all_local_Markdown_HTML_resource_links':all_links,'package_files_excluding_this_output':files,'stored_bytes_excluding_this_output':total,'largest_object':largest,
       'current_geometry_approved':False,'current_feed_approved':False,'exact_outstanding_votes_verified':False,
       'collector_implemented':False,'calibrated_forecast':False}
p=D/'coordinator-checks.json'
if p.exists():
    previous=load(p)
    if {k:v for k,v in previous.items()if k!='checked_utc'}=={k:v for k,v in final.items()if k!='checked_utc'}:final['checked_utc']=previous['checked_utc']
p.write_text(json.dumps(final,indent=2)+'\n')
print(json.dumps(final,indent=2))
