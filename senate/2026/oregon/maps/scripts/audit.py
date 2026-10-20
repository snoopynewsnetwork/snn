"""Deterministic full offline replay, DOM/object tests and self-only-excluded membership audit."""
from common import *
from acquire import body_of
from build import inventory,outputs,slug
from geography import build as geography_build
from originals import reconstruct
from replay import replay
from binary_audit import audit_zip
from render_previews import rendered
from html.parser import HTMLParser
import urllib.parse,re,collections,fitz,zipfile,struct
from PIL import Image

class DOM(HTMLParser):
 def __init__(self,b):
  super().__init__(convert_charrefs=True);self.pres=[];self.active=None;self.links=[];self.ids=[];self.parents=[];self.contexts=[];self.scripts=0;self.feed(b.decode('utf-8'))
 def handle_starttag(self,t,attrs):
  d=dict(attrs)
  if t=='pre':self.active=[d,'']
  if t=='script':self.scripts+=1
  if 'id'in d:self.ids.append(d['id'])
  if 'data-parent'in d:self.parents.append(d['data-parent'])
  if 'data-context-key'in d:self.contexts.append(d['data-context-key'])
  for k in ['href','src']:
   if k in d:self.links.append(d[k])
 def handle_data(self,d):
  if self.active:self.active[1]+=d
 def handle_endtag(self,t):
  if t=='pre' and self.active:self.pres.append(self.active);self.active=None

def objects_dom(pages,c):
 parents=c['all_36_county_parents'];original={p['county_key']:p for p in parents};known={x['key']:x for p in parents for x in p['source_native_constituents']};seen={};parentseen={}
 for path,b in pages.items():
  d=DOM(b);assert d.scripts==0 and len(d.ids)==len(set(d.ids))
  for attrs,text in d.pres:
   if attrs.get('data-kind') in ['parent','context']:
    obj=json.loads(text);key=attrs['data-key']
    if attrs['data-kind']=='context':assert key not in seen and obj==known[key];seen[key]=obj
    else:assert key not in parentseen and obj==original[key];parentseen[key]=obj
 assert parentseen==original and seen==known and len(seen)==510 and len(parentseen)==36
 assert DOM(pages['maps/index.html']).parents==list(original)
 assert DOM(pages['maps/known.html']).contexts==c['known_source_universe']['full_ordered_keys']
 assert DOM(pages['maps/unavailable.html']).parents==[p['county_key'] for p in parents if p['unknown_native_membership']]
 return {'static_DOM_pages':len(pages),'complete_parent_objects':len(parentseen),'complete_context_objects':len(seen),'unavailable_filter_parents':31,'known_order':'full510 qualified source order exactly preserved; not canonical statewide priority','JavaScript':False,'browser_render':False}

def full_inventory(inv,c):
 assert len(inv['parents'])==36 and len(inv['known_source_contexts'])==510 and len(inv['unavailable_native_parent_cases'])==31
 assert [r['county_key'] for r in inv['parents']]==[p['county_key'] for p in c['all_36_county_parents']]
 known={x['key']:x for p in c['all_36_county_parents'] for x in p['source_native_constituents']}
 for r in inv['parents']:
  obj=pointer(c,r['full_parent_ref']['pointer']);assert semantic(obj)==r['full_parent_ref']['full_object_semantic_sha256'];assert r['shared_parent_resource_keys'] and r['fallback_county_context']=='census-oregon-county2010';assert not r['current_result_leaf_polygon_joins'] and not r['current_geography_approved'];assert set(r['gaps'])=={'vintage','access','CRS','physical','legal','finer_ID','native_result_membership'}
 for r in inv['known_source_contexts']:
  obj=pointer(c,r['source_context_ref']['pointer']);assert obj==known[r['key']] and semantic(obj)==r['source_context_ref']['full_object_semantic_sha256'];assert r['inferred_leaf_join'] is None and not r['allocated_votes_ballots_registration']
 for r in inv['unavailable_native_parent_cases']:
  obj=pointer(c,r['full_unavailable_parent_ref']['pointer']);assert obj['unknown_native_membership'] and r['native_membership'] is None
 for k in ['canonical_statewide_native_order','canonical_top15','canonical_minimum80','canonical_priority','canonical_remainder']:assert inv[k] is None
 assert inv['inferred_result_leaf_polygon_joins']==0 and inv['spatial_allocations'] is False
 assert c['statewide_reported_votes']==2244493 and c['known_source_universe']['reported_votes']==1128521 and c['known_source_universe']['unknown_parent_votes']==1115972
 assert [len(p['source_native_constituents']) for p in c['all_36_county_parents'] if p['source_native_constituents']]==[118,118,107,12,155]

def membership(entries,actual):
 paths=[r['path'] for r in entries];assert len(paths)==len(set(paths)) and set(paths)==set(actual),'complete self-only-excluded file membership'
 for r in entries:
  b=(S/r['path']).read_bytes();assert len(b)==r['bytes']<40_000_000 and sha(b)==r['sha256'],r['path']

def all_owned():return sorted(['precinct-maps.md']+[str(p.relative_to(S)) for p in M.rglob('*') if p.is_file() and str(p.relative_to(S))!='maps/asset-manifest.json'])
def audit(sealed=True,deep=True):
 from report import report
 assert (S/'precinct-maps.md').read_bytes()==report(),'deterministic report'
 inv=load('maps/inventory.json.gz');c=json.loads(exact(inv['frozen_contract']));full_inventory(inv,c);regenerated=inventory();assert inv==regenerated,'deterministic full inventory'
 pages=outputs(inv);dom=objects_dom(pages,c)
 for path,b in pages.items():assert (S/path).read_bytes()==b,'deterministic full atlas '+path
 for path,b in rendered():assert (S/path).read_bytes()==b,'deterministic selected PNG '+path
 for p in M.rglob('*'):
  assert p.name not in ['__pycache__','node_modules','.cache','.pytest_cache'],p
  if p.is_file():assert p.stat().st_size<40_000_000,p
 # Inspect every actual HTML href/src and local Markdown link, including fragments.
 links=0;pending=[]
 for path,b in pages.items():
  for url in DOM(b).links:
   u=urllib.parse.urlsplit(url)
   if u.scheme:assert u.scheme in ['http','https'];continue
   target=((S/path).parent/urllib.parse.unquote(u.path)).resolve() if u.path else (S/path).resolve();assert target.is_file(),(path,url)
   if u.fragment and target.suffix=='.html':assert urllib.parse.unquote(u.fragment) in DOM(target.read_bytes()).ids,(path,url)
   links+=1
 for path in ['precinct-maps.md','maps/SCHEMA.md','maps/README.md']:
  for url in re.findall(r'\[[^\]]*\]\(([^)]+)\)',(S/path).read_text()):
   if urllib.parse.urlsplit(url).scheme:continue
   target=((S/path).parent/urllib.parse.unquote(url.split('#')[0])).resolve()
   if not target.is_file() and not sealed and str(target.relative_to(S)) in ['maps/qa/validation.json','maps/finalseal.json','maps/asset-manifest.json']:
    pending.append(str(target.relative_to(S)));continue
   assert target.is_file() or (url.endswith('/') and target.is_dir()),(path,url);links+=1
 requests=0;entities=0
 for p in sorted((M/'requests').glob('*.json')):
  r=load(str(p.relative_to(S)));requests+=1
  for e in r['entities']:
   if e.get('body'):original(e['body']);entities+=1
 for name in load('maps/references/navigation-fixed.json'):
  x=load(name);original_receipt=exact(x['source_receipt']);assert json.loads(original_receipt)==x['receipt']
  for e in x['receipt'].get('entities',[]):
   if e.get('body'):original(e['body']);entities+=1
 originalproof=reconstruct();assert originalproof==load('maps/qa/original-reconstruction.json')
 sourceproof=replay();assert sourceproof==load('maps/qa/source-replay.json')
 geo=geography_build(write=False);assert geo==load('maps/qa/geography.json.gz')
 binaries=0;cells=0;xy=0;members=0
 for summary in load('maps/qa/binary-summary.json'):
  proof=audit_zip(Path(summary['request']).stem,body_of(load(summary['request'])));assert proof==load(summary['audit']);binaries+=1;members+=len(proof['members'])
  for layer in proof['layers']:cells+=layer['dbf_cells_checked'];xy+=layer['xy_IEEE754_values_checked']
 countyproof=load('maps/qa/binary-census-oregon-county2010.json.gz')['layers'][0]
 fields=[f['name'] for f in countyproof['dbf_schema']];fips_index=fields.index('GEOID10');assert {r['cells'][fips_index]['value'] for r in countyproof['dbf_records']}=={p['county_fips'] for p in c['all_36_county_parents']}
 pubs=load('maps/renders/index.json');pagecount=0
 for p in pubs:
  b=body_of(load(p['request']))
  if p['member']:
   with zipfile.ZipFile(io.BytesIO(b)) as z:b=z.read(p['member'])
  assert sha(b)==p['source_pdf_sha256'] and len(b)==p['source_pdf_bytes']
  with fitz.open(stream=b,filetype='pdf') as doc:
   assert len(doc)==p['page_count']==len(p['pages']);assert doc.metadata==p['metadata'];text='\n\f\n'.join(page.get_text() for page in doc).encode();assert gzip.decompress(exact(p['text']))==text
   for page,meta in zip(doc,p['pages']):
    assert (page.rect.width,page.rect.height)==(meta['width_points'],meta['height_points']);img=exact(meta['render']);assert img.startswith(b'\x89PNG\r\n\x1a\n')
    with Image.open(io.BytesIO(img)) as image:
     assert max(image.size)==1600 and abs(image.width/image.height-page.rect.width/page.rect.height)<0.005;image.verify()
    pagecount+=1
 if sealed:membership(load('maps/asset-manifest.json')['files'],all_owned())
 result={'status':'pass','read_only':True,'authority_path':AUTH,'source_replay':sourceproof,'map_requests':requests,'reused_individual_receipts':len(load('maps/references/navigation-fixed.json')),'verified_original_response_entities':entities,'all_parents':36,'complete_known_contexts':510,'unavailable_native_parent_cases':31,'atlas':dom,'native_snapshots':geo['native_snapshots'],'native_features_nonadditive':sum(v['feature_count'] for v in inv['native_snapshots'].values() if v['complete']),'native_ID_pages':sum(len(v['pages']) for v in inv['native_snapshots'].values()),'zip_originals_audited':binaries,'zip_members_CRC_checked':members,'dbf_cells_checked':cells,'SHP_XY_IEEE754_values_checked':xy,'whole_PDFs':len(pubs),'complete_rendered_PDF_pages':pagecount,'relative_links_checked':links,'pending_preseal_targets':sorted(set(pending)),'inferred_result_leaf_polygon_joins':0,'spatial_allocations':False,'coordinator_acceptance':False}
 return result
if __name__=='__main__':
 import sys
 result=audit(sealed='--preseal' not in sys.argv)
 if '--write-validation'in sys.argv:save('maps/qa/validation.json',result)
 print(json.dumps(result))
