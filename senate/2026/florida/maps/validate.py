#!/usr/bin/env python3
"""Offline validation and exact owned file-manifest audit; no network."""
import sys
sys.dont_write_bytecode=True
import argparse,collections,gzip,hashlib,html.parser,json,pathlib,re,urllib.parse,xml.etree.ElementTree as ET
from PIL import Image,ImageChops
from acquire import ROOT,body
STATE=ROOT.parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def owned():return sorted([STATE/'precinct-maps.md']+[p for p in ROOT.rglob('*') if p.is_file()],key=lambda p:str(p.relative_to(STATE)))
def owned_rows():return [{'path':str(p.relative_to(STATE)),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in owned() if p!=ROOT/'asset-manifest.json']
def check_manifest():
 d=json.load(open(ROOT/'asset-manifest.json'));assert d['excluded_paths']==['maps/asset-manifest.json'];rows=owned_rows();assert rows==d['files'],'owned pathset/bytes/hash differs';assert len({r['path'] for r in rows})==len(rows);assert all(0<=r['bytes']<40000000 for r in rows)
 assert (ROOT/'asset-manifest.json').stat().st_size<40000000
 return {'status':'pass','exact_owned_pathset':len(rows),'manifest_bytes':(ROOT/'asset-manifest.json').stat().st_size,'manifest_sha256':sha((ROOT/'asset-manifest.json').read_bytes()),'exclusion_only':'maps/asset-manifest.json'}
class H(html.parser.HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.embeds=[];self.cards=[];self.countyrows=[];self.table=None;self.tags=collections.Counter()
 def handle_starttag(self,t,a):
  d=dict(a);self.tags[t]+=1
  if d.get('href'):self.links.append(d['href'])
  if d.get('src'):self.links.append(d['src']);self.embeds.append(d['src'])
  if t=='article':self.cards.append(d.get('data-key'))
  if t=='table':self.table=d.get('id')
  if t=='tr' and self.table=='all-counties' and d.get('data-key'):self.countyrows.append(d['data-key'])
 def handle_endtag(self,t):
  if t=='table':self.table=None

def main():
 d=json.load(open(STATE/'data/turnout/priority-set.json'));semantic=json.loads(gzip.decompress((ROOT/'frozen-contract.semantic.json.gz').read_bytes()));assert semantic==d;assert semantic['coordinator_accepted'] is False
 r=json.load(open(ROOT/'frozen-reference.json'));assert sha((STATE/r['canonical_contract']['path']).read_bytes())==r['canonical_contract']['sha256']
 for pin in r['references']:
  p=STATE/pin['path'];assert p.stat().st_size==pin['bytes'] and sha(p.read_bytes())==pin['sha256'],p
 inv=json.load(open(ROOT/'inventory.json'))['full67_inventory'];assert len(inv)==67;assert [x['frozen_parent'] for x in inv]==d['all_unit_order'];assert [x['frozen_parent']['key'] for x in inv[:22]]==d['ordered_priority_keys'];assert len(inv[22:])==45
 assert sum(x['frozen_parent']['votes'] for x in inv)==10757428;assert sum(x['frozen_parent']['votes'] for x in inv[:15])==7373225;assert sum(x['frozen_parent']['votes'] for x in inv[:21])==8572752;assert sum(x['frozen_parent']['votes'] for x in inv[:22])==8734473;assert sum(x['frozen_parent']['votes'] for x in inv[22:])==2022955
 assert all(x['downloads'] and x['preview'] for x in inv[:22]);assert all(not x['downloads'] and not x['preview'] for x in inv[22:]);assert all(x['official_home_from_retained_DOS_directory'] for x in inv)
 assert all(x['official_reference_acquired'] for x in inv[:22]);duval=inv[6];assert duval['frozen_parent']['name']=='Duval' and duval['source_geometry_feature_count']==295 and duval['geometry_source_scope']=='separate Census2020 fallback; not measured PDF precinct count'
 assert {x['source_id'] for x in duval['downloads']}=={'duval-census2020-vtd','duval-archived-countywide-pdf'} and duval['preview']=='previews/pdfs/duval-archived-countywide-pdf-p001.png'
 original=[json.loads(l) for l in gzip.decompress((STATE/r['identity_source']['path']).read_bytes()).splitlines()];diag=[json.loads(l) for l in gzip.decompress((ROOT/'identity-diagnostics.jsonl.gz').read_bytes()).splitlines()];assert len(diag)==len(original)==23532
 seen=set();counts=collections.Counter();cands=0;zeros=0
 for a,b in zip(original,diag):
  assert a==b['source_record'];assert b['source_native_record_sha256']==sha(json.dumps(a,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode());assert a['native_key'] not in seen;seen.add(a['native_key']);counts[a['context']]+=1;cands+=len(a['candidate_category_rows']);zeros+=sum(x['votes']==0 for x in a['candidate_category_rows']);assert b['physical_geometry_match'] is None and b['method_assignment'] is None and b['legal_named_writein_allocation'] is None and b['lexical_candidates']==[]
 assert dict(counts)=={'2024_president':5712,'2024_senate':5710,'2022_senate':6013,'2020_president':6097}
 ledger=json.load(open(ROOT/'source-ledger.json'));entities=0;errors=0
 for r0 in ledger['sources']:
  p=ROOT/'raw'/f"{r0['source_id']}.receipt.json";assert json.load(open(p))==r0
  b=body(r0['source_id']);assert len(b)==r0['original_bytes'] and sha(b)==r0['original_sha256'];entities+=1;errors+=r0['status']!=200
  if r0.get('stored_path'):
   s=(ROOT/r0['stored_path']).read_bytes();assert len(s)==r0['stored_bytes'] and sha(s)==r0['stored_sha256']
 shared={x['source_id']:x for x in ledger['sources'] if x.get('acquisition_role','').startswith('read-only immutable shared original')}
 assert set(shared)=={'duval-cdx-1141','duval-archived-countywide-pdf'}
 expected_shared={'duval-archived-countywide-pdf':(2628955,'044fdba7b7051901383875a284629d1276d037af73112c8bb68880f09b57043a'),'duval-cdx-1141':(245,'7fe55fb11dc22abdd6cba533ae4b959b883b7038c2333109b7032a11ad167747')}
 for key,(size,digest) in expected_shared.items():
  ref=shared[key];entry=ref['shared_receipt_provenance']['full_original_entry'];assert ref['original_bytes']==entry['bytes']==size and ref['original_sha256']==entry['raw_sha256']==digest;assert ref['response_headers']==entry['headers'] and ref['request_url']==entry['url'] and ref['final_url']==entry['final_url'] and ref['retrieved_utc']==entry['retrieved_at_utc'];assert ref['stored_path']=='../data/news/'+entry['asset'];assert ref['request_headers'] is None and ref['redirects'] is None and ref['encoding'] is None
  assert not any(p.name in (entry['asset'],key+'.pdf',key+'.body.gz') for p in ROOT.rglob('*') if p.is_file()),'shared original duplicated in maps'
 cdx=json.loads(body('duval-cdx-1141'));assert cdx==shared['duval-cdx-1141']['full_decoded_catalog'];assert cdx[1][0]=='20260106081626' and cdx[1][-1]=='2627790';assert cdx[1][1]==shared['duval-archived-countywide-pdf']['original_authority_url']
 assert json.load(open(ROOT/'raw/duval-other-pdf.receipt.json'))['status']==403
 acqs=0;features=0;stable_edit=0;maxbatch=0
 for p in ROOT.glob('*.acquisition.json'):
  a=json.load(open(p));pre=json.loads(body(a['ids_pre_source_id']));post=json.loads(body(a['ids_post_source_id']));assert set(pre['objectIds'])==set(post['objectIds']) and len(set(pre['objectIds']))==a['source_count'];got=[]
  for batch in a['batches']:
   b=json.loads(body(batch['source_id']));ids=[f['attributes'][a['object_id_field']] for f in b['features']];assert ids==batch['returned_ids'];assert set(ids)==set(batch['requested_ids']);assert len(ids)==len(set(ids))==batch['feature_count'];assert b.get('exceededTransferLimit') is not True;got+=ids;maxbatch=max(maxbatch,len(ids))
   q=urllib.parse.parse_qs(json.load(open(ROOT/'raw'/f"{batch['source_id']}.receipt.json"))['request_url'].split('?',1)[1]);assert q['outFields']==['*'] and q['returnGeometry']==['true'] and q['returnZ']==['true'] and q['returnM']==['true'] and q['returnTrueCurves']==['true'];assert not set(q)&{'outSR','geometryPrecision','quantizationParameters','maxAllowableOffset'}
  assert len(got)==len(set(got))==a['source_count'] and set(got)==set(pre['objectIds']);acqs+=1;features+=len(got);stable_edit+=a['pre_editingInfo']==a['post_editingInfo']
 assert acqs==11 and maxbatch<=50
 h=H();h.feed((ROOT/'index.html').read_text());assert h.cards==d['ordered_priority_keys'];assert h.countyrows==[r0['key'] for r0 in d['all_unit_order']];assert not any(urllib.parse.urlparse(u).scheme or u.startswith('//') for u in h.embeds);assert not any(h.tags[t] for t in ['iframe','script','object','embed']);local_links=0
 for url in h.links:
  u=urllib.parse.urlparse(url)
  if u.scheme or u.netloc or not u.path:continue
  p=(ROOT/urllib.parse.unquote(u.path)).resolve();assert p.exists(),url;local_links+=1
 markdown_links=0
 for url in re.findall(r'\]\(([^)]+)\)',(STATE/'precinct-maps.md').read_text()):
  u=urllib.parse.urlparse(url)
  if u.scheme or u.netloc:continue
  assert (STATE/urllib.parse.unquote(u.path)).exists(),url;markdown_links+=1
 svg_count=0
 for p in (ROOT/'previews').glob('*.svg'):
  t=ET.parse(p);assert t.getroot().tag.endswith('svg');assert not any('href' in k and (v.startswith('http') or v.startswith('//')) for el in t.iter() for k,v in el.attrib.items());svg_count+=1
 pdf=json.load(open(ROOT/'pdf-render-validation.json'));assert pdf['source_PDF_count']==14 and pdf['all_pages_rendered']==89;pngchecks=0;warnings=[]
 dpdf=next(x for x in pdf['PDFs'] if x['source_id']=='duval-archived-countywide-pdf');assert dpdf['page_count']==1 and dpdf['original_sha256']==expected_shared['duval-archived-countywide-pdf'][1];assert dpdf['metadata']['creationDate']=="D:20251118102119-05'00'";dtext=(ROOT/dpdf['text_extract']).read_text();assert 'School Board Districts with Precincts' in dtext and 'Map updated on 11/25 by MSL' in dtext
 for x in pdf['PDFs']:
  assert len(x['pages'])==x['page_count']
  for page in x['pages']:
   p=ROOT/page['preview_path'];assert sha(p.read_bytes())==page['PNG_sha256'];im=Image.open(p).convert('RGB');assert list(im.size)==page['preview_pixels'] and ImageChops.difference(im,Image.new('RGB',im.size,'white')).getbbox() is not None;pngchecks+=1
   if page['source_render_warnings']:warnings.append({'source_id':x['source_id'],'page_1based':page['page_1based'],'warning':page['source_render_warnings']})
 geo=json.load(open(ROOT/'geometry-summary.json'))['sources'];assert len(geo)==17
 for key,m in geo.items():
  details=json.load(open(ROOT/'geometry'/f'{key}.json'));assert len(details['all_features'])==m['feature_count'];assert details['source_metadata']==m
 assert len(json.load(open(ROOT/'geometry/lake.json'))['exact_XY_ring_duplicate_groups'])==92;assert geo['volusia']['counts']['curve_geometries']==31 and geo['volusia']['feature_count']==221
 native=json.load(open(ROOT/'native-original-validation.json'));assert native['ZIP_members_CRC_verified']==208 and native['original_field_comparisons']==4025606 and native['all_frozen_contract_constituents_checked']==23532
 peer=json.load(open(ROOT/'peer-compatibility-reference.json'))['full_coordinator_review'];peerpins=0
 for pin in peer['source_pins']:
  rp=STATE/pin['receipt'];bp=STATE/pin['body'];assert sha(rp.read_bytes())==pin['receipt_sha256'];assert sha(bp.read_bytes())==pin['stored_sha256'];assert sha(gzip.decompress(bp.read_bytes()))==pin['raw_sha256'];peerpins+=1
 files=owned();assert not any('__pycache__' in p.parts or p.suffix=='.pyc' for p in files);assert all(p.stat().st_size<40000000 for p in files);largest=max(files,key=lambda p:p.stat().st_size)
 out={'status':'pass_with_explicit_source_access_vintage_topology_and_browser_gaps','frozen_contract_bytes':23823926,'frozen_contract_sha256':r['canonical_contract']['sha256'],'recursive_semantic_equality_nodes':r['recursive_nodes_compared'],'full_parents':67,'ordered_priority':22,'priority_official_references_including_historical_Duval':22,'shared_original_references_checked':expected_shared,'Duval_archive_record_length_distinguished_from_entity_bytes':True,'remainder':45,'statewide_valid_named_votes':10757428,'priority_votes':8734473,'first21_votes':8572752,'threshold':8605943,'top15_votes':7373225,'remainder_votes':2022955,'native_counts':dict(counts),'all_full_native_records_equal_and_unallocated':23532,'candidate_category_source_rows':cands,'zero_vote_source_rows_preserved':zeros,'native_original_validation':native,'original_HTTP_entities_verified':entities,'error_entities_retained':errors,'ArcGIS_full_snapshots':acqs,'ArcGIS_features_across_snapshots':features,'ArcGIS_prepost_edit_metadata_equal':stable_edit,'maximum_batch':maxbatch,'geometry_snapshot_exports':17,'source_features_across_overlapping_exports':sum(m['feature_count'] for m in geo.values()),'invalid_or_uninterpretable_linear_geometry_source_contexts':sum(m['counts'].get('GEOS_invalid_or_uninterpretable',0) for m in geo.values()),'true_curves_preserved_and_excluded_from_linear_diagnostics':31,'lake184_features92_exact_duplicate_pairs':True,'source_empty_or_null_geometries':sum(m['counts'].get('empty_geometries',0)+m['counts'].get('null_geometries',0) for m in geo.values()),'SVGs_parsed_no_remote_refs':svg_count,'all_PDF_pages_rendered_and_hash_bounds_checked':pngchecks,'PDF_source_warnings':warnings,'HTML_exact22_and_all67_order':True,'HTML_no_remote_embeds_or_scripts':True,'HTML_local_links_checked':local_links,'Markdown_relative_links_checked':markdown_links,'peer_immutable_source_pins_checked_informational_only':peerpins,'largest_owned_file':{'path':str(largest.relative_to(STATE)),'bytes':largest.stat().st_size},'all_files_strictly_less_than40000000':True,'browser_UI':{'available_enabled_browser_surfaces':0,'native_Chrome_binding_error':'cgWindowNotFound','HTML_visual_browser_render_claimed':False,'static_visual_inspection':['previews/priority22-contact.png','previews/pdfs/broward-pdf-p001.png','previews/pdfs/collier-mapbook-alt-p034.png','previews/pdfs/escambia-pdf-p001.png','previews/pdfs/duval-archived-countywide-pdf-p001.png','raw/volusia-official-render.png']},'scope':'Research acquisition. No geometry repair, vote allocation, numeric masked-cell substitution, method assignment, current crosswalk, collector, measured cadence or forecast calibration. Duval historical official precinct-overlay PDF reused read-only by immutable hash, captured January6,2026; current original access unresolved and Census2020 fallback separate. No November2026 approval.','manifest_validation':'Run --check-manifest after writing final manifest; read-only audit avoids recursive hash mutation.'}
 (ROOT/'validation.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ['status','full_parents','ordered_priority','all_full_native_records_equal_and_unallocated','original_HTTP_entities_verified','ArcGIS_full_snapshots','geometry_snapshot_exports','all_PDF_pages_rendered_and_hash_bounds_checked','HTML_local_links_checked','Markdown_relative_links_checked','all_files_strictly_less_than40000000']}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--write-manifest',action='store_true');p.add_argument('--check-manifest',action='store_true');a=p.parse_args()
 if a.write_manifest:
  rows=owned_rows();assert all(x['bytes']<40000000 for x in rows);(ROOT/'asset-manifest.json').write_text(json.dumps({'schema_version':'fl-maps-assets-v1','owned_scope':['precinct-maps.md','maps/**'],'excluded_paths':['maps/asset-manifest.json'],'files':rows},indent=2)+'\n');print(json.dumps(check_manifest()))
 elif a.check_manifest:print(json.dumps(check_manifest()))
 else:main()
