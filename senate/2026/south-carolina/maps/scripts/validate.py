#!/usr/bin/env python3
"""Deterministic offline validation. Never imports acquisition or build code.
--verify-manifest additionally verifies self-excluding full owned inventory.
"""
import sys
sys.dont_write_bytecode=True
import pathlib,json,gzip,hashlib,re,urllib.parse,xml.etree.ElementTree as ET,zlib,struct
from html.parser import HTMLParser
import fitz
from PIL import Image
ROOT=pathlib.Path(__file__).resolve().parents[1]
PIN='a4dc8e50ce09889e5873d1f54c887dbef50a42a0b7bf600b4ab6663afab4ccef'
def sha(b):return hashlib.sha256(b).hexdigest()
def readj(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def body(m):
 if 'ordered_parts' in m:return b''.join(gzip.decompress((ROOT/p['path']).read_bytes()) for p in m['ordered_parts'])
 b=(ROOT/m['path']).read_bytes();return gzip.decompress(b) if m['compression']=='gzip' else b
class HTML(HTMLParser):
 def __init__(self):super().__init__();self.keys=[];self.links=[];self.embeds=[];self.all46rows=0;self.intable=False;self.inbody=False
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='li' and a.get('class')=='priority-entry':self.keys.append(a['data-key'])
  if tag=='table' and a.get('id')=='all46-inventory':self.intable=True
  if tag=='tbody' and self.intable:self.inbody=True
  if tag=='tr' and self.inbody:self.all46rows+=1
  if 'href' in a:self.links.append(a['href'])
  if 'src' in a:self.links.append(a['src']);self.embeds.append(a['src'])
 def handle_endtag(self,tag):
  if tag=='tbody':self.inbody=False
  if tag=='table':self.intable=False

def run():
 assertions=[]
 def check(ok,name):
  assert ok,name
  assertions.append(name)
 b=(ROOT.parent/'data/turnout/priority-set.json').read_bytes();contract=json.loads(b);accept=readj(ROOT.parent/'data/coordinator-priority-acceptance.json');check(sha(b)==PIN and len(b)==33917555,'exact_external_frozen_contract_pin');check(accept['accepted'] and accept['contract']['sha256']==PIN,'external_acceptance_matches_contract')
 cc=readj(ROOT/'contract-compatibility.json.gz');check(cc['frozen_contract']==contract,'every_complete_frozen_top_level_source_and_county_object_equal');check(len(cc['county_diagnostics'])==46,'all46_compatibility_diagnostics');counties=contract['counties'];keys=[c['geography_key'] for c in counties];check(keys==contract['ordered_keys'],'full_descending46_order');check([c['geography_key'] for c in counties if c['in_priority']]==contract['ordered_priority_keys']==accept['ordered_priority_keys'],'exact_ordered17_priority');check(keys[17:]==contract['remainder_keys'],'complete_ordered29_remainder');check(sum(c['candidate_votes'] for c in counties)==2548140 and sum(c['candidate_votes'] for c in counties[:17])==2061601 and sum(c['candidate_votes'] for c in counties[17:])==486539,'baseline_volume_controls_46_17_29');check(len(cc['frozen_contract']['source_observations'])==152 and len(cc['frozen_contract']['legacy_source_observations'])==140 and len(cc['frozen_contract']['original_combined_json_observations'])==277,'complete_distinct_global_source_catalogs');check(cc['join_policy']['approved_crosswalks']==[] and cc['join_policy']['vote_allocations']==[] and cc['join_policy']['VHM_reassignments']==[],'no_approved_crosswalk_allocation_or_VHM_reassignment')
 final_pins={
  'turnout.md':'053087a84e260ecb87cf496d4c708c23103d665a36743ab77fd0e4eafc17429d',
  'data/county-turnout.csv':'c44f964af5b7e43845a99e19a7177375e7685651726ede44f47a47a2e37aa65a',
  'data/turnout/asset-manifest.json':'70ae7c258291328257baa9061c8d3854ccb371c40f80298803d8b06197583f95',
  'data/turnout/validation.json':'708ce41f8bcf275829543d2ddec0082e4fe8692b6978b096224f24638828c80d',
  'data/baselines/asset-manifest.json':'41c90cccc7767494146ec76bbbf1ccf1f68ccb01419fa0dbf1e1e1be79e43994',
  'data/county-baselines.csv':'d9bb5070b6c5e05152c74679a819eccbba52b78e5d86f7f13a5fcebb377d0c87',
  'county-partisanship.md':'69c0e0e897cdbde46787701a76ce1e6a529afc7320c058a0289d45a39cd19469'}
 for path,pin in final_pins.items():check(sha((ROOT.parent/path).read_bytes())==pin,path+':final_launch_input_pin')
 allfiles=[p for p in ROOT.rglob('*') if p.is_file()];check(not any('__pycache__' in p.parts or p.suffix in ['.pyc','.pyo'] for p in allfiles),'no_caches_or_bytecode');check(all(p.stat().st_size<40000000 for p in allfiles),'every_owned_stored_asset_strictly_below40million_bytes')
 gzips=0
 for p in allfiles:
  if p.suffix=='.gz':
   raw=p.read_bytes();d=gzip.decompress(raw);check((zlib.crc32(d)&0xffffffff)==struct.unpack('<I',raw[-8:-4])[0] and len(d)%2**32==struct.unpack('<I',raw[-4:])[0],p.relative_to(ROOT).as_posix()+':gzip_CRC_size');gzips+=1
 captures={}
 for p in sorted((ROOT/'raw').glob('*.request.json')):
  m=readj(p);captures[m['id']]=m;original=body(m);check(sha(original)==m['original_sha256'] and len(original)==m['original_bytes'],m['id']+':complete_original_entity_hash_size')
  if 'ordered_parts' not in m:
   stored=(ROOT/m['path']).read_bytes();check(sha(stored)==m['stored_sha256'] and len(stored)==m['stored_bytes'],m['id']+':stored_entity_hash_size')
 cache={}
 def entity(n):
  if n not in cache:cache[n]=body(captures[n])
  return cache[n]
 def native(prefix,audit,oid):
  pre=json.loads(entity(prefix+'pre-ids'));post=json.loads(entity(prefix+'post-ids'));count=json.loads(entity(prefix+'pre-count'))['count'];check(set(pre['objectIds'])==set(post['objectIds']) and len(pre['objectIds'])==count==json.loads(entity(prefix+'post-count'))['count'],prefix+'all_ID_pre_post_count_sets')
  ids=[];features=[]
  for page in audit['pages']:
   d=json.loads(entity(page['capture']));check(not d.get('error') and not d.get('exceededTransferLimit') and not d.get('transform'),page['capture']+':no_error_truncation_or_quantization')
   query=urllib.parse.parse_qs(urllib.parse.urlsplit(captures[page['capture']]['requested_url']).query);requested=set(map(int,query['objectIds'][0].split(',')));got={f['attributes'][oid] for f in d['features']};check(requested==got and len(d['features'])==len(got)<=80,page['capture']+':bounded_exact_all_ID_batch');check(query['outFields']==['*'] and query['returnTrueCurves']==['true'] and query['returnZ']==['true'] and query['returnM']==['true'] and not any(k in query for k in ['outSR','geometryPrecision','maxAllowableOffset','quantizationParameters']),page['capture']+':full_native_request_options');ids.extend(f['attributes'][oid] for f in d['features']);features.extend(d['features'])
  check(len(ids)==len(set(ids))==count and set(ids)==set(pre['objectIds']),prefix+'complete_unique_acquired_features')
  return features
 audit=readj(ROOT/'native-audit.json.gz');layer_pre=json.loads(entity('rfa-precinct-layer'));layer_post=json.loads(entity('rfa-precinct-layer-post'));check(all(layer_pre.get(k)==layer_post.get(k) for k in ['fields','spatialReference','sourceSpatialReference','hasZ','hasM','geometryType','maxRecordCount']),'pre_post_native_schema_CRS_dimension_metadata_equal');check(all(p['spatialReference']['latestWkid']==6570 for p in audit['pages']),'every_native_response_CRS6570');features=native('native-',audit,'OBJECTID');check(all(set(f['attributes'])=={x['name'] for x in layer_pre['fields']} for f in features),'all_declared_native_attributes_present_every_feature');check(len(features)==2315 and len(audit['features'])==2315,'2315_full_state_native_records');check(sum(sum(len(r) for r in f['geometry']['rings']) for f in features)==1277142,'all1277142_native_coordinate_positions');check(sum(len(f['geometry']['rings']) for f in features)==2332,'all2332_native_rings');check(sum(r['geometry_diagnostics'].get('valid') is False for r in audit['features'])==2 and len(audit['topology']['positive_area_overlaps'])==791 and len(audit['topology']['skipped_pairs'])==18,'retained_invalid_geometry_overlap_and_skipped_pair_diagnostics');check(sum(r['geometry_diagnostics']['missing'] for r in audit['features'])==0,'no_missing_native_geometry_observed')
 fby={f['attributes']['OBJECTID']:f for f in features}
 for r in audit['features']:
  loc=r['original_locator'];raw=entity(loc['capture'])[loc['byte_start_inclusive']:loc['byte_end_exclusive']];check(sha(raw)==loc['feature_sha256'] and len(raw)==loc['feature_original_bytes'] and json.loads(raw)==fby[r['OBJECTID']],f'native_OBJECTID{r["OBJECTID"]}:exact_feature_byte_offset_hash_object')
 geos=readj(ROOT/'county-geometry-inventory.json');check(len(geos)==46 and [x['geography_key'] for x in geos]==keys,'native_all46_partition_order');check(sum(x['native_count'] for x in geos)==2315 and len({i for x in geos for i in x['native_OBJECTID_set']})==2315,'native_all46_disjoint_ID_partition')
 subset_count=0
 for g in geos[:17]:
  raw=gzip.decompress((ROOT/g['exact_native_subset']).read_bytes());d=json.loads(raw);check(sha(raw)==g['exact_subset_original_sha256'] and len(raw)==g['exact_subset_original_bytes'],g['county_fips']+':subset_hash_bytes');check([f['attributes']['OBJECTID'] for f in d['features']]==g['native_OBJECTID_set'] and d['features']==[fby[i] for i in g['native_OBJECTID_set']],g['county_fips']+':every_subset_attribute_coordinate_part_unchanged');check(len(d['features'])==g['native_count'] and d['spatialReference']==audit['native_crs'],g['county_fips']+':subset_count_CRS');orig_slices=[entity(l['capture'])[l['byte_start_inclusive']:l['byte_end_exclusive']] for l in g['subset_feature_origins']];start=raw.index(b'"features":[')+len(b'"features":[');check(raw[start:-3]==b','.join(orig_slices),g['county_fips']+':byte_identical_original_feature_lexemes');svg=ET.fromstring((ROOT/g['preview']).read_bytes());check(len(svg.findall('.//{http://www.w3.org/2000/svg}path'))==g['native_count'],g['county_fips']+':SVG_feature_count');subset_count+=len(d['features'])
 check(subset_count==1639,'exact17_subsets_total1639')
 alternative=readj(ROOT/'alternative-native-audit.json.gz')
 for a in alternative:
  oid=next(x['name'] for x in json.loads(entity(a['source_id']+'-layer'))['fields'] if x['type']=='esriFieldTypeOID');ff=native(a['source_id']+'-',a,oid);check(len(ff)==a['geometry_count'],a['source_id']+':full_alternative_count');index={x['attributes'][oid]:x for x in ff}
  for r in a['features']:
   loc=r['original_locator'];raw=entity(loc['capture'])[loc['byte_start_inclusive']:loc['byte_end_exclusive']];check(sha(raw)==loc['feature_sha256'] and json.loads(raw)==index[r['attributes'][oid]],a['source_id']+':original_offset_hash_ID'+str(r['attributes'][oid]))
 pdfs=readj(ROOT/'pdf-inventory.json');check(len(pdfs)==18 and sum(x['page_count'] for x in pdfs)==18,'18_actual_RFA_PDF_sheets_pages')
 for pdf in pdfs:
  raw=entity(pdf['id']);check(raw.startswith(b'%PDF') and sha(raw)==pdf['sha256'] and len(fitz.open(stream=raw,filetype='pdf'))==pdf['page_count'],pdf['id']+':PDF_original_bytes_and_page_count')
  for page in pdf['pages']:
   im=Image.open(ROOT/page['preview']);im.verify();check(max(im.size)==1800,pdf['id']+':real_page_render_dimensions')
 supplements=readj(ROOT/'supplement-inventory.json')
 for s in supplements:
  if 'external_original_path' in s:
   raw=gzip.decompress((ROOT.parent/s['external_original_path']).read_bytes());check(sha(raw)==s['original_metadata']['original_sha256'] and len(raw)==s['original_metadata']['original_bytes'],'peer_Lexington_original_exact_pin');check(sha((ROOT.parent/s['external_original_path']).read_bytes())==s['original_metadata']['stored_sha256'],'peer_Lexington_stored_exact_pin')
  elif s.get('page_count'):raw=entity(s['source_id'])
  else:raw=None
  if raw and s.get('page_count'):check(len(fitz.open(stream=raw,filetype='pdf'))==s['page_count'],s['source_id']+':supplement_all_PDF_pages')
  for p in s.get('pages',[]):Image.open(ROOT/p['preview']).verify()
 inventory=readj(ROOT/'all46-inventory.json');check([x['geography_key'] for x in inventory]==keys and len(inventory)==46,'all46_inventory_complete_order');notes=readj(ROOT/'scope-notes.json');check(len(notes)==46 and all(n.get('baseline') and n.get('current_publication') and n.get('november_scope') and n.get('current_changes_and_finer_scope_gap') for n in notes),'all46_explicit_baseline_current_November_and_finer_gaps');index=HTML();index.feed((ROOT/'index.html').read_text());check(index.keys==contract['ordered_priority_keys'] and len(index.keys)==17,'exactly17_ordered_preview_download_entries');check(index.all46rows==46,'HTML_inventory46_rows');check(not any(urllib.parse.urlsplit(u).scheme in ['http','https'] for u in index.embeds),'offline_no_remote_embedded_assets')
 broken=[]
 for url in index.links:
  u=urllib.parse.urlsplit(url)
  if u.scheme or not u.path:continue
  path=ROOT/urllib.parse.unquote(u.path)
  if not path.is_file():broken.append(url)
 report=ROOT.parent/'precinct-maps.md'
 for url in re.findall(r'\]\(([^)]+)\)',report.read_text()):
  u=urllib.parse.urlsplit(url)
  if u.scheme or not u.path:continue
  if not (report.parent/urllib.parse.unquote(u.path)).is_file():broken.append(url)
 check(not broken,'all_HTML_and_report_relative_file_links_resolve')
 # No mutable aggregate hashes enter the output: manifest verification is an independent final assertion.
 if '--verify-manifest' in sys.argv:
  mf=readj(ROOT/'manifest.json');owned={str(p.relative_to(ROOT.parent)) for p in ROOT.rglob('*') if p.is_file() and p!=ROOT/'manifest.json'}|{'precinct-maps.md'};listed={r['path'] for r in mf['owned_assets']};check(owned==listed,'manifest_self_exclusion_only_complete_owned_file_set')
  for r in mf['owned_assets']:
   p=ROOT.parent/r['path'];check(len(p.read_bytes())==r['bytes'] and sha(p.read_bytes())==r['sha256'],r['path']+':manifest_size_hash')
  for r in mf['external_inputs']:
   p=ROOT.parent/r['path'];check(len(p.read_bytes())==r['bytes'] and sha(p.read_bytes())==r['sha256'],r['path']+':external_input_size_hash')
 result={'schema':'sc-map-validation-v1','status':'pass','input_contract':{'path':'data/turnout/priority-set.json','sha256':PIN,'bytes':33917555},'source_family_objects_preserved':'complete recursive equality, every field/array/object','all_counties':46,'priority_counties':17,'remainder_counties':29,'primary_native_pages':29,'primary_native_features':2315,'priority_native_features':1639,'native_rings':2332,'native_coordinate_positions':1277142,'native_invalid_features_retained':2,'positive_area_pair_overlaps_retained':791,'invalid_candidate_pairs_skipped':18,'RFA_original_PDFs':18,'RFA_original_PDF_pages':18,'supplement_PDF_pages':sum(s.get('page_count',0) for s in supplements),'county_native_alternatives':{a['source_id']:a['geometry_count'] for a in alternative},'captures':len(captures),'gzip_members_CRC_size_checked':gzips,'HTML_priority_entries':17,'HTML_inventory_rows':46,'broken_relative_links':broken,'remote_embedded_assets':0,'approved_reporting_or_physical_crosswalks':0,'geometry_repairs':0,'vote_allocations':0,'all_stored_assets_below_bytes':40000000,'complete_asset_manifest_rule':'manifest.json excludes only itself; final --verify-manifest checks all owned and external hashes without embedding an aggregate hash','remaining_gaps':['No immutable election-day2024 physical boundary original','No complete legally approved November physical/reporting crosswalk','Retained native invalid geometry and overlaps; no repair','No same-vintage trusted legal outline to certify gaps','Explicit per-county blocked/local/current-change and finer-scope differences','Browser UI unavailable; real source PDF images visually reviewed and HTML/SVG links/counts checked offline']}
 out=(json.dumps(result,indent=2,ensure_ascii=False)+'\n').encode();(ROOT/'validation.json').write_bytes(out);print(json.dumps({'status':'pass','checks':len(assertions),'validation_sha256':sha(out),'validation_bytes':len(out),'manifest_verified':'--verify-manifest' in sys.argv}))
if __name__=='__main__':run()
