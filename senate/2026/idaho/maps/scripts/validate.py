#!/usr/bin/env python3
"""Read-only complete package validation; --write-qa only before seal."""
import ast,collections,csv,gzip,hashlib,html,io,json,re,sys,urllib.parse
from html.parser import HTMLParser
from pathlib import Path
from PIL import Image
import fitz
from evidence import MAPS,ROOT,own_receipts,original,sha
from verify_history import verify as history,semantic,pointer,checkpin
from native import verify as native,receipts,body
from shapefile_qa import verify as shpverify
from fixtures import run as fixtures,inventory_rules
from build import build
from geometry import diagnose

class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.ids=[];self.unit_rows=[]
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  for k in ['href','src']:
   if a.get(k):self.links.append(a[k])
  if t=='tr' and 'data-priority' in a:self.unit_rows.append(a)

def manifest_paths():return {str(p.relative_to(ROOT)):p for p in MAPS.rglob('*') if p.is_file() and p.name!='manifest.json'}|{'precinct-maps.md':ROOT/'precinct-maps.md'}
def check_manifest():
 m=json.loads((MAPS/'manifest.json').read_text());paths=manifest_paths();assert set(paths)=={x['path'] for x in m['owned']}
 for x in m['owned']:
  b=paths[x['path']].read_bytes();assert len(b)==x['bytes']<40000000 and sha(b)==x['sha256'],x['path']
 assert m['acceptance_path']=='data/coordinator-priority-acceptance.json'
 assert m['frozen_references_sha256']==sha((MAPS/'frozen-references.json').read_bytes())
 return len(paths)

def validate(preseal=False):
 h=history();refs=json.loads((MAPS/'frozen-references.json').read_text())
 assert refs['authority_path']=='data/coordinator-priority-acceptance.json'
 assert not any(e['path'].endswith(('coordinator-priority-acceptance.json','acquisition-native-stage-v1.json','coordinator-map-native-preparation-review.json','news/manifest.json')) for e in refs['references'])
 for e in refs['references']:checkpin(e)
 fs,nq=native();assert nq==json.loads((MAPS/'qa/native-verification.json').read_text())
 topo=diagnose(fs);assert topo==json.loads((MAPS/'qa/topology.json').read_text())
 sq=shpverify();assert sq==json.loads((MAPS/'qa/cassia-shapefile.json').read_text())
 inv=json.loads((MAPS/'inventory.json').read_text());inventory_rules(inv)
 a=json.loads((ROOT/'data/coordinator-priority-acceptance.json').read_text());c=json.loads((ROOT/'data/turnout/priority-set.json').read_text());parents=inv['parents'];ps={p['key']:p for p in parents}
 assert inv['ordered_full_keys']==a['ordered_full_keys'] and inv['ordered_priority_keys']==a['ordered_priority_keys'] and inv['ordered_remainder_keys']==a['ordered_remainder_keys']
 assert inv['ordered_parent_keys']==a['ordered_parent_keys'] and sum(bool(p['priority_children']) for p in parents)==32
 assert sum(p['state_map_feature_count'] for p in parents)==976
 for p in parents:
  r=p['complete_source_parent'];assert semantic(pointer(c,r['pointer']))==r['semantic_sha256']
  assert p['ordered_child_keys']==a['ordered_child_keys_by_parent'][p['key']] and p['ordered_priority_child_keys']==a['ordered_priority_child_keys_by_parent'][p['key']] and p['ordered_remainder_child_keys']==a['ordered_remainder_child_keys_by_parent'][p['key']]
  if p['priority_children']:assert p['source_requests'] and p['findings'] and len(p['findings'])>200
 rids={'state-public-native'}|{r['resource_id'] for r in inv['supplemental_resources']}
 assert len(rids)==len(inv['supplemental_resources'])+1
 for u in inv['observations']:
  r=u['source_complete_object'];v=pointer(c,r['pointer']);assert semantic(v)==r['semantic_sha256'] and v['key']==u['key'] and v['county_fips']==u['parent_key'] and v['literal_precinct']==u['literal_precinct'] and v['literal_method_flags']==u['literal_method_flags']
  assert all(i in rids for i in u['resource_ids']) and u['resource_ids']==ps[u['parent_key']]['acquired_resource_ids']
 # Complete acquired entities, including errors, are reconstructed and independently checked.
 rs=own_receipts();own={r['id']:r for r in rs};status=collections.Counter();pdfs={}
 for r in rs:
  b=original(r);status[str(r['status'])]+=1
  assert all(k in r for k in ['requested_url','final_url','method','retrieved_utc','headers','redirects','raw_bytes','raw_sha256','encoding','purpose','body_error'])
  assert r['method']=='GET' and r['retrieved_utc'].endswith('+00:00')
  if r['status']>=400:assert r['body_error'] is not None
  parent=own.get(r['parent'])
  if parent and r['literal_href'] and not r['literal_href'].startswith(('explicit ','Observed ')):
   raw=original(parent).decode(errors='replace');assert html.unescape(r['literal_href']) in html.unescape(raw) or any(x.get('href')==r['literal_href'] for x in parent.get('links',[])),r['id']
  if b.startswith(b'%PDF-'):pdfs[r['raw_sha256']]=r
 for s in inv['supplemental_resources']:assert s['resource_id'] in own and own[s['resource_id']]['status']==200
 # Each state native complete original points at an exact frozen individual body.
 paths={e['path'] for e in refs['references']}
 for r in receipts():assert r['asset_path'] in paths;body(r)
 pq=json.loads((MAPS/'qa/pdf-render.json').read_text());assert pq['originals']==len(pdfs)==150 and pq['pages']==335
 assert set(pdfs)=={p['sha256'] for p in pq['pdfs']}
 page_count=0
 for p in pq['pdfs']:
  r=pdfs[p['sha256']];doc=fitz.open(stream=original(r),filetype='pdf');assert len(doc)==p['complete_pages'] and doc.metadata==p['metadata']
  assert len(p['pages'])==len(doc)
  for i,x in enumerate(p['pages']):
   assert x['page']==i+1 and [doc[i].rect.width,doc[i].rect.height]==[x['width_points'],x['height_points']]
   im=Image.open(MAPS/x['png']);assert list(im.size)==x['render_pixels'];page_count+=1
  assert (MAPS/p['complete_text_path']).is_file()
 previews=json.loads((MAPS/'qa/native-preview-render.json').read_text());assert len(previews['previews'])==44 and sum(x['features'] for x in previews['previews'])==976 and sum(x['rings'] for x in previews['previews'])==1032 and sum(x['original_positions'] for x in previews['previews'])==749523
 for p in previews['previews']:
  assert (MAPS/p['svg']).stat().st_size==p['svg_bytes'];Image.open(MAPS/p['png']).verify()
 for path in MAPS.rglob('*'):
  if path.is_file():assert path.stat().st_size<40000000,path
  assert path.name not in ['__pycache__','node_modules','.pytest_cache'],path
  if path.suffix=='.py':ast.parse(path.read_text())
 # Offline HTML all original keys exactly once; local links and anchors resolve.
 doc=Links();doc.feed((MAPS/'index.html').read_text());assert len(doc.ids)==len(set(doc.ids))
 assert len(doc.unit_rows)==985 and sum(r['data-priority']=='true' for r in doc.unit_rows)==528
 for row,key in zip(doc.unit_rows,a['ordered_full_keys']):assert row['data-search'].startswith(key+' ')
 checked=0
 for u in doc.links:
  parsed=urllib.parse.urlsplit(u)
  if parsed.scheme or parsed.netloc:continue
  path=(MAPS/urllib.parse.unquote(parsed.path)).resolve() if parsed.path else MAPS/'index.html'
  assert path.exists() or (preseal and path==MAPS/'manifest.json'),u
  if parsed.fragment and path==MAPS/'index.html':assert parsed.fragment in doc.ids,u
  checked+=1
 for p in [ROOT/'precinct-maps.md']+list(MAPS.glob('*.md')):
  for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
   target=target.strip('<>');u=urllib.parse.urlsplit(target)
   if u.scheme or u.netloc or not u.path:continue
   q=(p.parent/urllib.parse.unquote(u.path)).resolve();assert q.exists() or (preseal and q in [MAPS/'manifest.json',MAPS/'qa/validation.json']),(p,target);checked+=1
 files,newinv=build();assert newinv==inv
 for path,b in files.items():assert (MAPS/path).read_bytes()==b,path
 f=fixtures(inv);assert f==json.loads((MAPS/'qa/negative-fixtures.json').read_text())
 owned_count=check_manifest() if not preseal else None
 return dict(status='pass_historical_map_research_sealed_for_coordinator_review' if not preseal else 'pass_preseal_research_validation',acceptance_path='data/coordinator-priority-acceptance.json',historical_complete=h,frozen_individual_references=len(refs['references']),owned_manifest_entries=owned_count,parents=44,priority_parents=32,observations=985,priority=528,remainder=457,all_priority_entries_have_actual_acquired_qualified_resource=True,exact_child_polygon_matches=0,acquired_HTTP_receipts=len(rs),HTTP_statuses=dict(sorted(status.items())),native_receipts=len(receipts()),native_features=976,native_fields=10,native_rings=1032,native_original_XY=749523,native_invalid=topo['invalid'],native_positive_area_pairs=len(topo['positive_area_pairs']),Cassia_SHP_records=24,Cassia_XY=sq['XY_positions'],Cassia_invalid=sq['topology']['invalid'],Cassia_positive_area_pairs=len(sq['topology']['positive_area_pairs']),complete_PDF_originals=150,complete_PDF_pages_rendered_and_checked=page_count,supplemental_resources=len(inv['supplemental_resources']),negative_fixtures=f['count'],deterministic_replay='inventory.json and index.html exact bytes',local_links_checked=checked,all_owned_files_strictly_below_40000000=True,geometry_repair=False,numeric_votes_attached_to_polygons=False,current_geography_approved=False,coordinator_acceptance=None)
if __name__=='__main__':
 pre='--preseal' in sys.argv;result=validate(pre)
 if '--write-qa' in sys.argv:
  assert pre,'Only preseal QA writes allowed';(MAPS/'qa/validation.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))
