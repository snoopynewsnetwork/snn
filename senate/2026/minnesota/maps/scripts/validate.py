#!/usr/bin/env python3
"""Deterministic, offline validation. Does not rewrite originals or derived assets.
Default checks frozen artifacts plus owned manifest. --write records stable validation
before manifest sealing. Manifest excludes only itself and has no reverse hash cycle.
"""
import sys
sys.dont_write_bytecode=True
import json,gzip,hashlib,sqlite3,io,zipfile,re,collections,os
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote,urlsplit
from acquire import ROOT,read,sha
from native import wkb_blob,scan_wkb
STATE=ROOT.parent
checks=[]
def check(name,condition,detail=None):
 if not condition:raise AssertionError(name+': '+str(detail))
 checks.append({'check':name,'status':'pass','detail':detail})
def load(p):return json.loads((ROOT/p).read_text())
def doc(k):return json.loads(read(load('evidence/'+k+'.request.json')))
contract_bytes=(STATE/'data/turnout/priority-set.json').read_bytes();contract=json.loads(contract_bytes);accept=json.loads((STATE/'data/coordinator-priority-acceptance.json').read_text())
check('frozen_dispatch_contract',len(contract_bytes)==9885383 and sha(contract_bytes)=='b60b0bc4fed0c0b8618b6f851cc8f25d3c963bbd3ea12debecc5995dff54ceb1')
check('acceptance_path_authority',accept['contract_sha256']==sha(contract_bytes) and accept['ordered_priority_keys']==contract['ordered_priority_keys'])
compat=json.loads(gzip.decompress((ROOT/'compatibility.json.gz').read_bytes()));check('complete_contract_object_equality_every_field',compat['complete_frozen_contract']==contract)
co=contract['county_order'];counts={y:sum(len(c['native_constituents'][y]) for c in co) for y in ['2024','2022','2020']};check('all_native_constituents_all87',len(co)==87 and counts=={'2024':4103,'2022':4103,'2020':4110} and sum(counts.values())==12316,counts)
check('24_order_and_2067_native2024',len(contract['ordered_priority_keys'])==24 and [c['key'] for c in co[:24]]==contract['ordered_priority_keys'] and sum(len(c['native_constituents']['2024']) for c in co[:24])==2067)
check('historical_volume_coverage_arithmetic',sum(c['votes'] for c in co)==3189323 and sum(c['votes'] for c in co[:24])==2567977 and sum(c['votes'] for c in co[:23])==2543408 and sum(c['votes'] for c in co[24:])==621346)
for pin in load('input-pins.json')['inputs']:
 b=(STATE/pin['path']).read_bytes();check('input_pin:'+pin['path'],len(b)==pin['bytes'] and sha(b)==pin['sha256'])
# Full entities, ordered parts, offset arithmetic, original/stored hashes and HTTP errors all preserved.
request_count=0;original_bytes=0;stored_parts=0;unique_entities=set();unique_parts=set()
for p in sorted((ROOT/'evidence').glob('*.request.json')):
 m=json.loads(p.read_text());offset=0;unique_entities.add(m['original_entity_sha256'])
 for z in m['ordered_parts']:
  unique_parts.add(z['path'])
  b=(ROOT/z['path']).read_bytes();check('stored_part:'+z['path'],len(b)==z['stored_bytes'] and sha(b)==z['stored_sha256'] and len(b)<40000000)
  entity=gzip.decompress(b);check('ordered_offset:'+z['path'],z['offset']==offset and len(entity)==z['entity_bytes']);offset+=len(entity);stored_parts+=1
 b=read(m);check('original_entity:'+m['key'],offset==len(b)==m['original_entity_bytes'] and sha(b)==m['original_entity_sha256']);request_count+=1;original_bytes+=len(b)
# Original full native tables and all72 exact-row county subsets, column order and BLOBs included.
full={};subset_rows=0;coordinate_positions=0
for v,k,t,n in [('2024','results','general_election_results_by_precinct_2024',4103),('2022','results','general_election_results_by_precinct_2022',4103),('current','current','bdry_votingdistricts',4105)]:
 c=sqlite3.connect(':memory:');c.deserialize(read(load('evidence/'+k+'-gpkg.request.json')));check('sqlite_integrity:'+v,c.execute('pragma integrity_check').fetchone()[0]=='ok');fields=c.execute('pragma table_info('+t+')').fetchall();rr=c.execute('select * from '+t+' order by OBJECTID').fetchall();names=[x[1] for x in fields];countycol=names.index('COUNTYFIPS');check('native_full_count:'+v,len(rr)==n)
 seen=[]
 for county in co:
  rows=[r for r in rr if r[countycol]==county['county_fips'][2:]];seen+=rows
  if county['in_priority']:
   p=ROOT/'counties'/county['county_fips']/(v+'.gpkg.gz');sub=sqlite3.connect(':memory:');sub.deserialize(gzip.decompress(p.read_bytes()));check('subset_exact_rows_columns_blobs:'+v+':'+county['county_fips'],sub.execute('pragma table_info('+t+')').fetchall()==fields and sub.execute('select * from '+t+' order by OBJECTID').fetchall()==rows);subset_rows+=len(rows)
 check('all87_partition_full_native:'+v,sorted(r[0] for r in seen)==sorted(r[0] for r in rr))
 gd=json.loads(gzip.decompress((ROOT/'diagnostics'/(v+'-geometry.json.gz')).read_bytes()));check('geometry_audit_row_coverage:'+v,len(gd['records'])==n and len({r['OBJECTID'] for r in gd['records']})==n)
 actual_positions=0;diag_byid={r['OBJECTID']:r for r in gd['records']};blobcol=names.index('Shape')
 for row in rr:
  blob=row[blobcol];wkb,header=wkb_blob(blob);scan=scan_wkb(wkb);diag=diag_byid[row[0]]
  assert diag['raw_geometry_sha256']==sha(blob) and diag['coordinate_positions']==scan['coordinate_positions'] and diag['types']==scan['types'] and diag['dimensions']==scan['dimensions']
  actual_positions+=scan['coordinate_positions']
 check('every_native_coordinate_dimension_curve_scan:'+v,actual_positions==gd['coordinate_positions']);coordinate_positions+=actual_positions
check('6203_priority_subset_rows_and1974218_coordinates',subset_rows==6203 and coordinate_positions==1974218,{'subset_rows':subset_rows,'coordinate_positions':coordinate_positions})
# Actual ZIP CRC/member hashes, PDFs and pages, not shells. Full paper member metadata preserved.
paper=json.loads(gzip.decompress((ROOT/'paper-audit.json.gz').read_bytes()));pdfs=0;pages=0
for county in co[:24]:
 f=county['county_fips'];pd=paper[f];b=read(load('evidence/lcc2025-'+f+'.request.json'));check('actual_zip_magic:'+f,b.startswith(b'PK'));z=zipfile.ZipFile(io.BytesIO(b));check('zip_crc:'+f,z.testzip() is None);check('paper_member_order:'+f,[m['member_path'] for m in pd['members']]==z.namelist())
 for i,member in enumerate(pd['members']):
  bb=z.read(member['member_path']);check('pdf_member:'+f+':'+str(i),bb.startswith(b'%PDF-') and len(bb)==member['original_bytes'] and sha(bb)==member['sha256'] and member['pages']==1 and len(member['full_page_text'])==1 and not member.get('error'));pdfs+=1;pages+=member['pages']
check('24_county_paper2068_PDF2068_pages',len(paper)==24 and pdfs==pages==2068)
# Complete observed batches and pre-post ID controls; no pagination truncation claimed away.
service=load('service-audit.json');batch_count=0
for k in ['current','results','results2022']:
 s=service[k];got=[]
 for batch in s['batches']:
  check('service_batch:'+batch['request_path'],sorted(batch['requested_ids'])==sorted(batch['received_ids']) and batch['exceededTransferLimit'] is not True);got+=batch['received_ids'];batch_count+=1
 check('pre_post_batch_native_sets:'+k,sorted(got)==sorted(s['pre_ids'])==sorted(s['post_ids'])==s['native_object_ids'] and len(got)==len(set(got))==s['native_count']==s['pre_count']==s['post_count'])
check('51_complete_control_batches',batch_count==51)
w=doc('waconia-native');linear=doc('waconia-preview-linearized');check('truecurves_retained_native_and_preview_distinct',len(w['features'])==4 and all('curveRings' in f['geometry'] for f in w['features']) and all('rings' in f['geometry'] for f in linear['features']) and [f['attributes'] for f in w['features']]==[f['attributes'] for f in linear['features']] and service['waconia']['all_ids_equal'])
diffs=load('service-attribute-differences.json');check('all3444_service_native_attribute_differences_preserved',len(diffs)==3444 and {d['native_field'] for d in diffs}=={'Shape_Area','Shape_Length'})
# Exactly24 cards and all87 table rows, with local relative links resolving offline.
class Index(HTMLParser):
 def __init__(self):super().__init__();self.cards=[];self.rows=[];self.links=[]
 def handle_starttag(self,t,a):
  d=dict(a)
  if t=='article':self.cards.append(d.get('data-county-key'))
  if t=='tr' and 'data-county-key' in d:self.rows.append(d['data-county-key'])
  for name in ['href','src']:
   if name in d:self.links.append(d[name])
h=Index();h.feed((ROOT/'index.html').read_text());check('exact24_ordered_cards',h.cards==accept['ordered_priority_keys']);check('exact87_ordered_inventory_rows',h.rows==[c['key'] for c in co])
for url in h.links:
 s=urlsplit(url)
 if not s.scheme and s.path:check('index_relative_link:'+url,(ROOT/unquote(s.path)).exists())
# Local report references, external sources excluded from offline existence check.
report=(STATE/'precinct-maps.md').read_text()
for target in re.findall(r'\]\(([^)]+)\)',report):
 u=urlsplit(target)
 if not u.scheme and u.path:check('report_relative_link:'+target,(STATE/unquote(u.path)).exists())
# No caches, dependencies, oversized stored objects or unmanifested owned objects.
owned=[p for p in ROOT.rglob('*') if p.is_file()]+[STATE/'precinct-maps.md'];check('every_owned_object_strict_under40million',all(p.stat().st_size<40000000 for p in owned),max(p.stat().st_size for p in owned));check('no_cache_or_dependency_trees',not any(p.name in ['__pycache__','node_modules','.cache','.venv'] for p in ROOT.rglob('*')))
result={'status':'pass','scope':'Offline preservation/coverage/schema/ID/binary/paper/link checks; not current legal/results/method/candidate approval, not a crosswalk or allocation. No topology repairs.','summary':{'county_count':87,'priority_cards':24,'historical_constituents':12316,'priority_2024_native_records':2067,'priority_native_subset_rows_all3vintages':subset_rows,'all_state_coordinate_positions':coordinate_positions,'paper_pdfs':pdfs,'paper_pages':pages,'control_batches':batch_count,'original_request_entities':request_count,'ordered_original_part_references':stored_parts,'unique_original_entities':len(unique_entities),'unique_original_parts':len(unique_parts),'original_entity_bytes':original_bytes},'checks':checks}
if '--write' in sys.argv:(ROOT/'validation.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
else:
 check('validation_exact_reproduction',load('validation.json')==result)
 mf=load('asset-manifest.json');actual={str(p.relative_to(STATE)) for p in owned if p!=ROOT/'asset-manifest.json'};listed={x['path'] for x in mf['assets']};check('owned_manifest_complete_self_exclusion_only',actual==listed,{'actual':len(actual),'listed':len(listed)})
 for x in mf['assets']:
  b=(STATE/x['path']).read_bytes();assert len(b)==x['bytes'] and sha(b)==x['sha256'],x['path']
 print('MANIFEST PASS',len(listed),'owned assets; self excluded only')
print('OFFLINE PASS',json.dumps(result['summary'],sort_keys=True))
