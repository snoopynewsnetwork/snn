"""Independent offline QA. --check is read-only; --write writes only owned QA.
Full byte/semantic/native-binary replay, all-order/local-link/image checks.
"""
from common import *
from audit_dependencies import audit
from investigate import receipts,links
from geometry import census,arcgis
from bs4 import BeautifulSoup
from urllib.parse import urlsplit,unquote,urljoin
import re,sys,xml.etree.ElementTree as ET,collections,tempfile,subprocess
from PIL import Image
def owned():return sorted([STATE/'precinct-maps.md']+[p for p in MAPS.rglob('*') if p.is_file()],key=lambda p:str(p))
def verify():
 dep=audit();assert semantic(dep)==semantic(load('qa/dependencies.json'))
 c=json.loads(check(dep['contract']));us=c['all_units'];inv=load('inventory-691.json');pri=load('priority-index-304.json');rem=load('remainder-387.json');ps=load('county-parents.json');assets=load('source/asset-catalog.json');es=receipts();ix={e['id']:e for e in es}
 assert len(es)==len(ix)
 assert len(inv)==691 and pri==inv[:304] and rem==inv[304:] and len(pri)==304 and len(rem)==387
 assert [e['key']for e in inv]==c['complete_ordered_keys']
 assert [e['key']for e in pri]==c['ordered_priority_keys']
 assert len(ps)==66 and [p['county_parent_key']for p in ps]==[p['parent_key']for p in c['county_parents']]
 for i,(e,u) in enumerate(zip(inv,us)):
  r=e['full_frozen_native_object'];assert r['contract']==dep['contract'] and r['JSON_pointer']=='/all_units/'+str(i) and r['recursive_semantic_sha256']==semantic(u)
  assert e['key']==u['key'] and e['rank']==i+1 and e['priority80']==(i<304)
  assert e['matched_physical_feature_ids'] is None and e['current_reporting_crosswalk'] is None
  assert all(e['qualifications'].values()) and e['fallback']['asset_id']=='census-SD-vtd20-original'
  assert e['fallback']['reporting_unit_crosswalk'] is None
  for ident in e['county_map_assets']:assert ident in {x['id']for x in assets}
 for i,(p,cp) in enumerate(zip(ps,c['county_parents'])):
  assert p['full_parent_object']['recursive_semantic_sha256']==semantic(cp) and p['full_parent_object']['JSON_pointer']=='/county_parents/'+str(i)
  assert p['ordered_all_native_keys']==cp['ordered_all_native_keys'] and p['ordered_priority_native_keys']==cp['ordered_priority_native_keys']
  assert p['current_geometry_approved'] is False and p['historical_to_current_crosswalk'] is None
  assert len(p['official_authority']['cells'])==9 and p['official_authority']['cells'][0]['text']==cp['county']
  if p['priority_parent']:assert p['source_receipt_ids'] or cp['county'] in ['Bon Homme','Haakon','Potter']
 assert sum(e['contest_votes']for e in pri)==343402 and sum(e['contest_votes']for e in inv[:303])==342947
 assert sum(e['contest_votes']for e in rem)==85326 and sum(e['contest_votes']for e in inv[:15])==61003
 # Every original/body/error plus every referenced asset measured independently.
 rawbytes=0
 for e in es:rawbytes+=len(original(e))
 for p in load('source/read-only-references.json'):check(p)
 for p in load('source/preparation-individual-pins.json'):check(p)
 # Replay actual app -> config -> webmap -> layer, rather than trusting a familiar ID.
 ma=json.loads(original(ix['minnehaha-app-data']));mw=json.loads(original(ix['minnehaha-webmap-data']))
 assert ma['map']['itemId']=='7cc5bcba864d4d4781b83b229f2b8819'
 ml=next(x for x in mw['operationalLayers'] if x.get('url','').endswith('/Election/Redistricting_2022/MapServer'))
 assert any(x['id']==4 and x['name']=='Voting Precincts' for x in ml['layers'])
 pa=json.loads(original(ix['pennington-app-data']));pw=json.loads(original(ix['pennington-webmap-data']))
 assert pa['widgets']['widget_7']['config']['initialMapDataSourceID']=='fe799037ba7240e1a5f8c16f12c9ecc0'
 assert any(x.get('url')=='https://gis.rcgov.org/server/rest/services/AGOL/Voting/MapServer/13' for x in pw['operationalLayers'])
 assert 'b03eeb32869e421fa0e92864794728f5' in original(ix['pennington-map-parent']).decode()
 discovery=json.loads((STATE/'data/coordinator-map-preparation/primary-web-reader-discovery.json').read_bytes())
 assert any('83db20af25c2402a8390082f51baa059' in u for o in discovery['observations']for u in o['observed_primary_hrefs'])
 for child in ['census-SD-directory','census-SD-state-layer-directory','census-SD-vtd20-original']:
  e=ix[child];parent=ix[e['parent_id']];assert any(urljoin(parent['url'],l['literal_href'])==e['url'] for l in links(parent))
 # Whole original binary geometry verification is rerun, not a check of a receipt alone.
 cg=census(ix['census-SD-vtd20-original'],render=False)
 assert semantic(cg)==semantic(json.loads(gzip.decompress((MAPS/'qa/Census-binary-geometry.json.gz').read_bytes())))
 ng={n:arcgis(es,n,render=False)for n in ['minnehaha','pennington']};assert semantic(ng)==semantic(load('qa/native-GIS.json'))
 # Static HTML full691 row identity/order and exact304 primary table.
 soup=BeautifulSoup((MAPS/'index.html').read_bytes(),'html.parser');rows=soup.select('tr[data-key]');assert [r['data-key']for r in rows]==c['complete_ordered_keys']
 assert [r['data-key']for r in soup.select('#priorities tr[data-key]')]==c['ordered_priority_keys']
 assert len(list((MAPS/'counties').glob('*.html')))==66
 checked_links=0;html_cache={}
 def target_check(base,url):
  nonlocal checked_links
  sp=urlsplit(url)
  if sp.scheme or sp.netloc:return
  dest=(base.parent/unquote(sp.path)).resolve() if sp.path else base
  assert dest.is_file(),(str(base),url,str(dest));checked_links+=1
  if sp.fragment and dest.suffix=='.html':
   if dest not in html_cache:html_cache[dest]={t.get('id')for t in BeautifulSoup(dest.read_bytes(),'html.parser').select('[id]')}
   assert unquote(sp.fragment) in html_cache[dest],(str(base),url)
 for p in owned():
  if p.suffix=='.html':
   ss=BeautifulSoup(p.read_bytes(),'html.parser');assert ss.title and ss.find('main')
   for el in ss.select('[href],[src]'):target_check(p,el.get('href',el.get('src')))
  elif p.suffix=='.md':
   for url in re.findall(r'\]\(([^\s)]+)\)',p.read_text()):target_check(p,url)
 svgs=list((MAPS/'previews').glob('*.svg'));assert len(svgs)==68
 for p in svgs:
  root=ET.parse(p).getroot();assert root.tag.endswith('svg') and root.find('{http://www.w3.org/2000/svg}title') is not None
  paths=root.findall('{http://www.w3.org/2000/svg}path');assert paths
  if p.name.startswith('census-'):assert len(paths)==cg['county_counts'][p.stem.split('-')[1]]
  for el in paths:
   assert not re.search(r'\b(?:nan|inf)\b',el.attrib['d'],re.I)
   assert el.attrib['d'].count('M ')==el.attrib['d'].count(' Z')
 pngs=list((MAPS/'previews').glob('*.png'))
 for p in pngs:
  with Image.open(p) as im:im.verify()
 pdfs=load('qa/PDF-inspection.json')
 for p in pdfs:
  e=ix[p['id']];b=original(e);assert sha(b)==p['original_raw_sha256'] and b.startswith(b'%PDF')
  with tempfile.TemporaryDirectory(prefix='sd-pdf-offline-qa-') as t:
   q=Path(t)/'original.pdf';q.write_bytes(b);out=subprocess.run(['pdfinfo',str(q)],capture_output=True,check=True).stdout.decode();count=int(next(l.split(':')[1].strip()for l in out.splitlines()if l.startswith('Pages:')));assert count==p['pages']
  sheet=Image.open(STATE/p['all_pages_contact_sheet']);assert sheet.size==(1320,((p['pages']+3)//4)*360)
  text=gzip.decompress((STATE/p['complete_text_path']).read_bytes())
  for r in p['large_complete_page_renders']:assert 1<=r['physical_page']<=p['pages'] and (STATE/r['path']).is_file()
 vr=load('qa/visual-review.json')
 for p in vr['actually_viewed_files']:check(p)
 replay=load('qa/reproducibility.json');assert replay['all_measured_bytes_identical'] and replay['reconstructed_original_PDF_exact'] and replay['reconstructed_full_nested_unit_exact'] and replay['network_requests']==0
 files=owned();limit=max(p.stat().st_size for p in files);assert limit<40000000
 assert not any(p.name=='__pycache__' for p in MAPS.rglob('*'))
 # The external acceptance can be read for authority, but its hash must not be
 # copied back into producer/output approval objects, even indirectly here.
 acceptance_digest=sha((STATE/ACCEPTANCE).read_bytes()).encode()
 assert not any(acceptance_digest in p.read_bytes() for p in files)
 return dict(status='pass_qualified_historical_maps_only',authority_path_only=ACCEPTANCE,complete_contract_reference=dep['contract'],frozen_reference_pins=len(dep['exact_references']),complete_recursive_object_references=len(dep['complete_semantic_objects']),full_CSV_companion_schemas=len(dep['complete_CSV_companion_semantics']),signed_county_vectors_checked=dep['signed_county_vectors_checked'],signed_candidate_fields_checked=dep['signed_candidate_fields_checked'],full_dependency_original_streams=len(dep['full_original_streams']),complete_reused_and_owned_receipts=len(es),receipt_original_bytes_checked=rawbytes,counts=load('qa/build-summary.json'),full691_primary304_remainder387_order_exact=True,all66_full_parent_objects_children_exact=True,all_source_candidate_method_null_admin_fields_resolve_recursively=True,all_original_SHP_positions_binary_checked=cg['position_count'],native_features=sum(v['feature_count']for v in ng.values()),native_curves_retained=sum(len(v['true_curve_features'])for v in ng.values()),native_pre_post_IDcount_metadata_pagination_pass=True,geometry_repaired=False,legal_outline_certification=False,approved_leaf_crosswalks=0,static_local_links_checked=checked_links,static_SVGs_parsed=len(svgs),PNGs_decoded=len(pngs),PDF_originals_reopened=len(pdfs),PDF_pages_reconciled=sum(p['pages']for p in pdfs),exact_offline_replay_and_reconstruction_pass=True,browser_session_used=False,all_files_strictly_under_40000000=True,maximum_owned_file_bytes=limit,owned_members_excluding_manifest=len([p for p in files if p!=MAPS/'asset-manifest.json']))
def manifest_check():
 d=load('asset-manifest.json');expected={str(p.relative_to(STATE))for p in owned()if p!=MAPS/'asset-manifest.json'};entries=d['owned_assets'];assert {p['path']for p in entries}==expected and len(entries)==len(expected)
 for p in entries:check(p)
 assert d['self_exclusion_only']=='maps/asset-manifest.json'
def main():
 assert sys.argv[1:] in [['--write'],['--check']]
 if sys.argv[1]=='--write':
  for name in ['qa/validation.json','asset-manifest.json']:
   if not (MAPS/name).exists():dump(name,{})
 result=verify()
 if sys.argv[1]=='--write':dump('qa/validation.json',result)
 else:assert semantic(result)==semantic(load('qa/validation.json'));manifest_check()
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
