#!/usr/bin/env python3
"""Read-only independent offline checks. --record records only deterministic owned validation.json."""
import argparse,collections,csv,gzip,html,json,math,pathlib,re,subprocess,sys,xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import unquote,urlsplit
import fitz
from acquire import ROOT,STATE,sha,body,save_json
from frozen import audit,walk
import native

class IndexParser(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.keys=[];self.parentids=[];self.inline_network=[]
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  for k in ['href','src']:
   if k in d:self.links.append(d[k])
  if tag=='tr' and 'data-key' in d:self.keys.append(d['data-key'])
  if 'data-parent' in d:self.parentids.append(d['data-parent'])
  if tag in ['script','img','link','iframe'] and any(str(d.get(k,'')).startswith(('http:','https:','//')) for k in ['href','src']):self.inline_network.append(d)

def checks(record=False):
 a,c,f=audit(False);saved=json.loads((ROOT/'frozen-references.json').read_text());assert f==saved
 stats={'frozen_exact_file_pins':len(f['files']),'frozen_reference_edges':len(f['edges']),'complete_contract_fields':len(f['complete_contract_fields'])}
 # Complete referenced tree semantic identity, not just vote fields or a key list.
 for ref in f['complete_contract_fields']:
  v=c[ref['JSON_pointer'][1:]];assert ref['complete_recursive_object'] and ref['semantic_sha256']==sha(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
  assert ref['recursive_nodes']==sum(1 for _ in walk(v))
 stats['complete_contract_recursive_nodes']=sum(x['recursive_nodes'] for x in f['complete_contract_fields'])
 method_vectors=0;html_vectors=0;observed_generic=0;unknown_generic=0
 for u in c['constituents']:
  assert sum(u['candidate_values'])==u['priority_votes_state_scope']
  if u['generic_writeins'] is None:unknown_generic+=1
  else:
   observed_generic+=u['generic_writeins'];assert u['reported_candidate_and_generic_votes']==sum(u['candidate_values'])+u['generic_writeins']
  if u.get('source_candidate_objects'):
   assert [x['votes'] for x in u['source_candidate_objects']]==u['candidate_values'];html_vectors+=1
  if u.get('candidate_method_values'):
   for i,(label,values) in enumerate(u['candidate_method_values'].items()):
    assert len(values)==4 and values[0]==sum(values[1:]) and values[0]==u['candidate_values'][i];method_vectors+=1
  if u.get('ballots') is not None:assert u['ballots']==sum(u['candidate_values'])+u['generic_writeins']+u['under']+u['over']
  if u.get('contest_volume_arithmetic') is not None:assert u['contest_volume_arithmetic']==sum(u['candidate_values'])+u['generic_writeins']+u['under']+u['over']
 assert unknown_generic==895 and observed_generic==1078 and html_vectors==895 and method_vectors==396
 assert sum(p['full_child_named_votes'] for p in c['all93_parents'])==935005
 assert sum(p['priority_child_named_votes'] for p in c['all93_parents'])==748190
 assert 5*748190>=4*935005 and 5*747645<4*935005
 assert 5*748190<4*(935005+233) and 5*748190>=4*(935005+232)
 assert 5*(747645+1795)>=4*(935005+1795) and 5*(747645+1794)<4*(935005+1794)
 stats.update({'all_preferred_candidate_vectors_checked':1326,'HTML_source_candidate_objects_checked':1790,'Lancaster_candidate_method_balances_checked':396,'unknown_HTML_generic_fields_preserved':895,'observed_generic_marks_not_eligible_allocation':1078,'all93_parent_named_balances_checked':True,'integer80_and_writein_conditional_breakpoints_checked':True})

 # Audit source original reconstruction against immutable receipt graph. Never consume mutable news ledger.
 pins={x['path']:x for x in f['files']};bynames=collections.defaultdict(list)
 for rel in pins:bynames[pathlib.Path(rel).name].append(STATE/rel)
 source_ids=set();reconstructed=set();unresolved=[]
 for rel in pins:
  p=STATE/rel
  try:j=json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
  except (ValueError,UnicodeDecodeError,OSError):continue
  for pointer,x in walk(j):
   if not isinstance(x,dict):continue
   if isinstance(x.get('id'),str) and x.get('raw_sha256'):source_ids.add(x['id'])
   if x.get('asset') and x.get('stored_sha256') and x.get('raw_sha256'):
    matches=[q for q in bynames[pathlib.Path(x['asset']).name] if sha(q.read_bytes())==x['stored_sha256']]
    if not matches:unresolved.append((rel,pointer,x.get('id'),x.get('asset')));continue
    raw=gzip.decompress(matches[0].read_bytes()) if matches[0].suffix=='.gz' else matches[0].read_bytes();assert sha(raw)==x['raw_sha256'],(rel,pointer)
    if 'raw_bytes' in x:assert len(raw)==x['raw_bytes']
    elif 'bytes' in x:assert len(raw)==x['bytes']
    reconstructed.add(x['raw_sha256'])
 # Some full receipt objects are documentary alternatives not selected bodies in the manifest. Their preserved exact parent stays authoritative.
 assert not unresolved,unresolved[:10]
 stats['frozen_original_entities_reconstructed']=len(reconstructed)
 for u in c['constituents']:assert u['source_id'] in source_ids,u['source_id']
 stats['native_source_references_resolved']=len(c['constituents'])
 rs=[json.loads(p.read_text()) for p in sorted((ROOT/'receipts').glob('*.json'))];byid={r['id']:r for r in rs};origin=set()
 for r in rs:
  for x in r['storage']:
   p=STATE/x['path'];b=p.read_bytes();assert len(b)==x['bytes'] and sha(b)==x['sha256'] and len(b)<40_000_000
  b=body(r);assert len(b)==r['original_bytes'] and sha(b)==r['original_sha256'];origin.add(r['original_sha256'])
  assert r['method']=='GET' and r['requested_url']==r['url'];assert r['retrieved_utc'];assert isinstance(r['headers'],dict)
  if r.get('parent_receipt'):
   pp=STATE/r['parent_receipt'];assert pp.is_file()
   parent=json.loads(pp.read_text());pb=body(parent)
   # Exact literal HTML links or explicit JSON documented constructors (not guessed IDs).
   if r.get('literal_href'):assert r['literal_href'].encode() in pb or html.escape(r['literal_href'],quote=True).encode() in pb or r['url'] in [l['url'] for l in parent.get('literal_links',[])],r['id']
  if r.get('excluded_from_source_graph'):assert r['status'] is None
 stats['owned_acquisition_receipts']=len(rs);stats['owned_unique_entities_and_errors']=len(origin)
 for prefix,title in [('sarpy','Voting Precinct'),('adams','Precinct'),('scottsbluff','Voting Precincts')]:
  wm=json.loads(body(byid[prefix+'-webmap']));layer=next(l for l in wm['operationalLayers'] if l.get('title')==title);meta=byid[prefix+'-native-layer-metadata'];assert meta['url'].split('?')[0]==layer['url']
 stats['new_literal_webmap_service_chains_verified']=3
 rr=native.prep();refs=json.loads((ROOT/'source-references.json').read_text())['references']
 prepby={x['id']:x for x in rr};chain_count=0;chains=set()
 for x in rr:
  if x.get('JSON_pointer') and x.get('parent_id') and x.get('literal_service_url'):
   parent=prepby[x['parent_id']];pj=json.loads(native.raw(parent));v=pj
   for token in x['JSON_pointer'].strip('/').split('/'):
    token=token.replace('~1','/').replace('~0','~');v=v[int(token)] if isinstance(v,list) else v[token]
   assert v==x['literal_service_url'];chain_count+=1;chains.add((x['parent_id'],x['JSON_pointer'],v))
 assert chain_count==6 and len(chains)==2
 stats['preparation_literal_webmap_service_pointers_verified']=chain_count
 for x in refs:
  b=(STATE/x['path']).read_bytes();assert len(b)==x['bytes'] and sha(b)==x['sha256']
 stats['shared_map_receipts_verified']=len(rr)
 # Replay the original SHP/SHX/DBF and native JSON parsers independently of saved derived results.
 counters=collections.Counter()
 def same_json(p,j):assert json.loads(p.read_text())==j,str(p);counters['regenerated_JSON_objects_exact']+=1
 def same_gz(p,j):assert json.loads(gzip.decompress(p.read_bytes()))==j,str(p);counters['regenerated_native_objects_exact']+=1
 # SVG generation is captured to a temporary in-memory target object without changing files.
 class Target:
  def __init__(self,p):self.p=p;self.parent=self
  def mkdir(self,**kwargs):pass
  def write_text(self,text):assert self.p.read_text()==text,str(self.p);counters['regenerated_SVGs_exact']+=1
 orig_svg=native.svg
 def same_svg(p,*args):return orig_svg(Target(p),*args)
 native.save_json=same_json;native.write_gz=same_gz;native.svg=same_svg
 for prefix in ['douglas','lancaster']:native.service(rr,prefix)
 own=[r for r in rs if '-native-layer-' in r['id']]
 for prefix in ['sarpy','adams','scottsbluff']:native.service(own,prefix)
 fs=native.census(rr);stats.update(counters)
 assert len(fs)==1402
 for p in (ROOT/'counties').glob('*.json.gz'):
  j=json.loads(gzip.decompress(p.read_bytes()));fips=p.name[:5];expected=[f for f in fs if '31'+f['attributes']['COUNTYFP20']==fips];assert j['features']==expected and j['source_native_positions_preserved']
 stats['complete_Census_county_slices_verified']=93
 idx=json.loads((ROOT/'index.json').read_text());parents=json.loads((ROOT/'parents.json').read_text());units=idx['inventory'];assert len(units)==1326 and len(parents)==93
 for k in ['ordered_priority_keys','ordered_full_keys','ordered_remainder_keys','parent_full_child_map','parent_priority_child_map','child_parent_map']:assert idx[k]==c[k]
 assert [u['key'] for u in units]==c['ordered_full_keys'];assert [u['key'] for u in units if u['priority']]==c['ordered_priority_keys'];pm={p['parent_key']:p for p in parents}
 assert sum(p['priority_parent'] for p in parents)==58
 assert idx['resource_coverage']=={'priority_parents_with_county_or_municipal_map_resource':17,'priority_entries_with_shared_county_or_municipal_map_resource':603,'priority_parents_Census_only':41,'priority_entries_Census_only':162,'resource_is_not_entry_or_full_county_coverage_proof':True}
 stats['priority_Census_only_entries']=162;stats['priority_shared_county_or_municipal_resource_entries']=603
 for i,u in enumerate(units):
  assert u['rank']==i+1 and u['complete_frozen_observation']['JSON_pointer']=='/constituents/'+str(i)
  frozen=c['constituents'][i];assert u['complete_frozen_observation']['semantic_sha256']==sha(json.dumps(frozen,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
  assert all(u[x] is None for x in ['entry_level_legal_match','entry_level_native_match','entry_level_physical_match','entry_level_current_match']);assert not u['votes_allocated_to_geometry']
  assert u['native_label_literal']==frozen['native_label_literal'] and u['county_fips']==frozen['county_fips'];assert u['shared_parent_map_assets']
  assert frozen['source_id'] in u['specific_source_access_vintage_finer_geometry_gaps']
  for asset in u['shared_parent_map_assets']:
   b=(STATE/asset['path']).read_bytes();assert len(b)==asset['bytes'] and sha(b)==asset['sha256']
 for p,orig in zip(parents,c['all93_parents']):
  for k in ['parent_key','county','county_fips','full_child_keys','priority_child_keys','full_child_named_votes','priority_child_named_votes']:assert p[k]==orig[k]
  assert p['Census_fallback']['features']==len(p['Census_fallback']['source_positions']);assert p['legal_current_approval'] is False and p['historical_reporting_match'] is None
  for x in [p['Census_fallback']['native_asset'],p['Census_fallback']['preview']]+([p['native_service']['native_asset'],p['native_service']['preview'],p['native_service']['diagnostics']] if p['native_service'] else []):assert sha((STATE/x['path']).read_bytes())==x['sha256']
 for name,expected in [('priority-index.csv',units[:765]),('full-inventory.csv',units),('remainder-index.csv',units[765:])]:
  rows=list(csv.DictReader((ROOT/name).open()));assert [r['key'] for r in rows]==[u['key'] for u in expected]
 stats.update({'priority_entries':765,'full_entries':1326,'remainder_entries':561,'parents':93,'priority_parents':58,'entry_level_matches_claimed':0})
 parser=IndexParser();parser.feed((ROOT/'index.html').read_text());assert parser.keys==c['ordered_priority_keys'] and parser.parentids==[p['parent_key'] for p in parents];assert not parser.inline_network
 links=0
 for href in parser.links:
  if href.startswith(('#','http:','https:','mailto:','data:')):continue
  dest=ROOT/unquote(urlsplit(href).path)
  if record and dest==ROOT/'asset-manifest.json' and not dest.exists():continue # initial manifest bootstrap only; final read-only validation requires it
  assert dest.is_file(),href;links+=1
 for p in (ROOT/'previews').glob('*.svg'):
  tree=ET.parse(p);paths=tree.findall('.//{http://www.w3.org/2000/svg}path');assert paths,p;assert not any(x.attrib.get('href','').startswith('http') for x in tree.iter())
 mdlinks=0
 for mp in [STATE/'precinct-maps.md',ROOT/'SCHEMA.md']:
  for href in re.findall(r'\[[^\]]*\]\(([^)]+)\)',mp.read_text()):
   if href.startswith(('http:','https:','mailto:','#')):continue
   target=mp.parent/unquote(href.split('#')[0])
   if record and target in [ROOT/'asset-manifest.json',ROOT/'validation.json'] and not target.exists():continue
   assert target.exists(),(mp,href);mdlinks+=1
 stats['local_Markdown_links_checked']=mdlinks
 stats['static_local_HTML_links_checked']=links;stats['SVG_files_parsed']=len(list((ROOT/'previews').glob('*.svg')))
 pdfs=json.loads((ROOT/'qa/pdf-structure.json').read_text())['PDFs'];pages=0
 for x in pdfs:
  p=STATE/x['source_path'];b=p.read_bytes();assert sha(b)==x['original_sha256'];doc=fitz.open(p);assert len(doc)==x['page_count']
  for row,page in zip(x['pages'],doc):assert row['text']==page.get_text() and row['png_sha256']==sha((STATE/row['complete_page_png']).read_bytes());pages+=1
 assert len(pdfs)==16 and pages==17
 stats['complete_original_PDFs_checked']=len(pdfs);stats['complete_original_PDF_pages_checked']=pages
 # Existing manifest content and complete owned membership. No shared/peer writes.
 if (ROOT/'asset-manifest.json').exists():
  import audit_assets
  current=audit_assets.manifest();old=json.loads((ROOT/'asset-manifest.json').read_text());assert old==current,'Owned asset membership/hash drift';stats['full_manifest_verified']=True;stats['owned_manifest_entries']=len(old['owned_artifacts'])
 else:stats['full_manifest_verified']=False
 stats['no_asset_at_or_above_40000000']=all(p.stat().st_size<40_000_000 for p in ROOT.rglob('*') if p.is_file())
 assert stats['no_asset_at_or_above_40000000']
 result={'schema':'NE-map-offline-validation-v1','status':'pass_historical_named_dispatch_with_explicit_map_identity_gaps','checks':stats,'browser_render_tested':False,'browser_access_observation':'CUA getState returned browsers=[] (no enabled browser tab surface); Chrome native app was listed. No browser rendering was performed. Static HTML/link/SVG/PDF checks do not claim it.','no_current_or_eligible_writein_approval':True,'no_worker_self_acceptance':True,'qualification':'Complete historical research with source/access/vintage/geometry qualifications; all source discrepancies and unknowns remain unallocated.'}
 if record:save_json(ROOT/'validation.json',result)
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--record',action='store_true');a=p.parse_args();print(json.dumps(checks(a.record),indent=2))
