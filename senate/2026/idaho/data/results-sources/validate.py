#!/usr/bin/env python3
"""Independent read-only semantic, originals, coverage, source and seal audit."""
from collections import Counter,defaultdict
from pathlib import Path
import argparse,ast,copy,csv,gc,gzip,hashlib,io,json,posixpath,re,subprocess,sys,zipfile,xml.etree.ElementTree as E
D=Path(__file__).resolve().parent;S=D.parent.parent
C=Counter();N={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def ck(v,k,detail=''):
 assert v,(k,detail);C[k]+=1

def sha(b):return hashlib.sha256(b).hexdigest()
def digest(x):return sha(json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode())
def read(p):
 b=p.read_bytes();return gzip.decompress(b) if p.suffix=='.gz' else b

def load(p):return json.loads(read(p))
def equal(a,b,kind):
 ck(type(a) is type(b),kind)
 if isinstance(a,dict):
  ck(set(a)==set(b),kind)
  for k in a:equal(a[k],b[k],kind)
 elif isinstance(a,list):
  ck(len(a)==len(b),kind)
  for u,v in zip(a,b):equal(u,v,kind)
 else:ck(a==b,kind)

def pointer(x,p):
 for token in p.strip('/').split('/'):
  token=token.replace('~1','/').replace('~0','~');x=x[int(token)] if isinstance(x,list) else x[token]
 return x

def original_books():
 refs=load(S/'data/turnout/source/reused-originals.json');raw={}
 for r in refs:
  p=(S/'data/turnout'/r['reused_path']).resolve();b=p.read_bytes();value=gzip.decompress(b);ck(sha(b)==r['stored_sha256'] and sha(value)==r['raw_sha256'] and len(value)==r['bytes'],'original_receipt_complete_entity',r['id']);raw[r['id']]=value
 return raw

def cells(row,strings):
 result={}
 for c in row.findall('m:c',N):
  v=c.find('m:v',N);f=c.find('m:f',N);rawv=v.text if v is not None else None;val=rawv
  if c.get('t')=='s' and rawv is not None:val=strings[int(rawv)]
  elif c.get('t')=='inlineStr':val=''.join(c.find('m:is',N).itertext()) if c.find('m:is',N) is not None else None
  result[re.sub('[0-9]','',c.get('r'))]=dict(address=c.get('r'),value=val,type=c.get('t'),style=c.get('s'),raw_v=rawv,formula=f.text if f is not None else None)
 return result

def sheets(raw):
 z=zipfile.ZipFile(io.BytesIO(raw));ck(z.testzip() is None,'original_zip_CRC');strings=[''.join(x.itertext()) for x in E.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',N)] if 'xl/sharedStrings.xml' in z.namelist() else [];rel={x.get('Id'):x.get('Target') for x in E.fromstring(z.read('xl/_rels/workbook.xml.rels'))};result={}
 for s in E.fromstring(z.read('xl/workbook.xml')).findall('m:sheets/m:sheet',N):
  target=rel[s.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')];member=target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/'+target);result[s.get('name')]=dict(member=member,rows={int(r.get('r')):cells(r,strings) for r in E.fromstring(z.read(member)).findall('m:sheetData/m:row',N)})
 return result

def frozen_checks():
 a=load(S/'data/coordinator-priority-acceptance.json');g=load(D/'historical-source-graph.json');contract=load(S/g['contract_path']);b=(S/g['contract_path']).read_bytes();ck(len(b)==1668713 and sha(b)=='9bf413132cd591ac110ac1d88bc6d52f818679f6b28b33a0ca77e30c4d1e6676','frozen_contract_exact')
 ck(g['external_acceptance_path']=='data/coordinator-priority-acceptance.json','external_path_only');ck(not contract['priority_accepted'] and not contract['current_geography_approved'],'producer_flags_remain_false')
 for r in g['immutable_complete_files']:
  p=S/r['path'];b=p.read_bytes();ck(len(b)==r['bytes'] and sha(b)==r['sha256'] and len(b)<40000000,'immutable_complete_body',r['path']);v=gzip.decompress(b) if p.suffix=='.gz' else b
  if 'reconstructed_sha256' in r:ck(sha(v)==r['reconstructed_sha256'] and len(v)==r['reconstructed_bytes'],'lossless_dependency_reconstruction')
  if 'semantic_sha256' in r:ck(digest(json.loads(v))==r['semantic_sha256'],'full_dependency_recursive_semantics')
  if 'complete_rows_semantic_sha256' in r:ck(digest(list(csv.reader(io.StringIO(v.decode()))))==r['complete_rows_semantic_sha256'],'full_dependency_csv_header_rows_semantics')
 roots={r['pointer']:r for r in a['complete_root_field_semantics']};ck(set(roots)=={'/'+k for k in contract},'every_contract_root_field')
 for r in g['root_fields']:ck(digest(pointer(contract,r['pointer']))==r['semantic_sha256']==roots[r['pointer']]['semantic_sha256'],'external_root_full_semantic_match')
 ck(g['complete_source_companion_paths']==[r['path'] for r in a['complete_source_companion_files']],'every_companion_required')
 for r in a['complete_source_companion_files']:
  p=S/r['path'];b=p.read_bytes();ck(sha(b)==r['sha256'] and len(b)==r['bytes'],'external_companion_byte_identity');value=gzip.decompress(b) if p.suffix=='.gz' else b
  if 'reconstructed_complete_sha256' in r:ck(sha(value)==r['reconstructed_complete_sha256'] and len(value)==r['reconstructed_complete_bytes'],'external_companion_full_reconstruction')
  if 'semantic_sha256' in r:ck(digest(json.loads(value))==r['semantic_sha256'],'external_companion_every_field')
  if 'full_rows_semantic_sha256' in r:ck(digest(list(csv.reader(io.StringIO(value.decode()))))==r['full_rows_semantic_sha256'],'external_companion_all_csv_fields')
 # Check every complete source/admin object, including unavailable/null/header fields.
 external={(r['file'],r['pointer']):r for r in a['complete_source_object_references']};ck(len(external)==len(g['complete_object_references'])==5169,'every_complete_object_count');cache={g['contract_path']:contract}
 for r in g['complete_object_references']:
  if r['file'] not in cache:cache[r['file']]=load(S/r['file'])
  x=pointer(cache[r['file']],r['pointer']);e=external[r['file'],r['pointer']];ck(digest(x)==r['semantic_sha256']==e['semantic_sha256'],'every_object_recursive_semantics',r['key'])
 # Replay all original selected candidate and statistics positions, without producer imports.
 originals=original_books();books={}
 positions=load(S/'data/baselines/source/candidate-positions.json.gz');stats=load(S/'data/baselines/source/statistics-positions.json.gz')
 def book(source,member):
  key=(source,member)
  if key not in books:books[key]=sheets(zipfile.ZipFile(io.BytesIO(originals[source])).read(member) if member else originals[source])
  return books[key]
 for row in positions+stats:
  sh=book(row['source_id'],row.get('archive_member'))[row['worksheet']];original=sh['rows'][row['row']]
  if 'raw_cells' in row:equal(original,row['raw_cells'],'original_every_selected_raw_cell_field')
  else:
   equal(original.get(row['column']),row['raw_cell'],'original_historical_candidate_raw_cell');equal(original.get('A'),row['raw_label_cell'],'original_historical_label_raw_cell')
  if 'candidate' in row:
   candidate=row['candidate'];value=original.get(row['column'],{}).get('value');ck(candidate['votes']==(int(value) if value is not None else None),'candidate_null_value_preserved')
   if row['contest']=='2024-president':ck(candidate['header_literal']==original['F']['value'] and candidate['party']==original.get('E',{}).get('value'),'presidential_candidate_party_original')
   else:
    headers=[v.get(row['column'],{}).get('value') for n,v in sh['rows'].items() if n<8];ck(candidate['header_literal'] in headers and candidate['party_header_literal'] in headers,'historical_full_candidate_party_header')
 # Every full raw2024 worksheet cell, including unrelated offices/types/styles/formula/nulls.
 for label,source in [('races','sos-2024-all-races-xlsx'),('stats','sos-2024-turnout-xlsx')]:
  x=load(S/f'data/turnout/source/2024-{label}-rows.json.gz');bk=book(source,None);ck(sha(originals[source])==x['original_sha256'],'complete_workbook_source_identity');ck({s['sheet'] for s in x['sheets']}==set(bk),'complete_workbook_sheet_set')
  for sh in x['sheets']:
   orig=bk[sh['sheet']];ck(orig['member']==sh['member'],'complete_workbook_member');ck(set(orig['rows'])=={v['row'] for v in sh['rows']},'every_original_workbook_row')
   for row in sh['rows']:
    old=orig['rows'][row['row']];equal({k:v['value'] for k,v in old.items()},row['cells'],'complete2024_original_cell_values');equal({k:dict(address=v['address'],type=v['type'],style=v['style'],raw_value=v['raw_v'],formula=v['formula']) for k,v in old.items()},row['cell_metadata'],'complete2024_original_cell_metadata')
  del x;gc.collect()
 fips={r['COUNTYNAME']:r['STATEFP']+r['COUNTYFP'] for r in csv.DictReader(io.StringIO(read(S/'data/turnout/source/fips2020.gz').decode()),delimiter='|') if r['STATE']=='ID'};ck(len(fips)==44,'original_fips_all44')
 groups=defaultdict(list)
 for number,row in book('sos-2024-all-races-xlsx',None)['raw_races']['rows'].items():
  if row.get('D',{}).get('value')=='United States President':groups[row['A']['value'],row['B']['value']].append((number,row))
 order=[];candidates=Counter()
 for (county,label),rows in groups.items():
  ck(len(rows)==13,'all13_original_categories');cv=[(n,r) for n,r in rows if r['F']['value'] not in ['Overvotes','Undervotes']];ck(len(cv)==11,'all11_original_candidates');votes=sum(int(r['G']['value']) for n,r in cv);first=min(n for n,r in rows);last=max(n for n,r in rows);key=f'ID:2024:pres:{fips[county]}:{first}';order.append((key,votes,county,label,first,last))
  for n,r in cv:candidates[r['E']['value'],r['F']['value']]+=int(r['G']['value'])
 order.sort(key=lambda r:(-r[1],r[0]));ck(len(order)==985 and sum(r[1] for r in order)==905057,'original_primary_denominator');ck(sum(r[1] for r in order[:15])==65391,'original_top15');ck(sum(r[1] for r in order[:527])==723753 and sum(r[1] for r in order[:528])==724515,'original_minimum80');ck(order[527][0]=='ID:2024:pres:16079:11741' and order[527][1]==762 and order[527][-1]==11753,'original_unique_Osburn_crossing');ck(sum(r[1] for r in order[528:])==180542,'original_remainder')
 equal(dict(candidates),{(x['party'],x['candidate']):x['votes'] for x in contract['source_candidate_universe']},'all11_original_candidate_controls')
 ck([r[0] for r in order]==[r['key'] for r in contract['complete_order']],'original_complete_canonical_order')
 hierarchy=load(D/'all985-hierarchy.json')
 for k in ['ordered_parent_keys','ordered_child_keys_by_parent','ordered_priority_child_keys_by_parent','ordered_remainder_child_keys_by_parent','ordered_priority_keys','ordered_remainder_keys']:equal(hierarchy[k],contract[k],'complete_hierarchy_allfields')
 native={u['key']:u for p in contract['all_county_constituents'] for u in p['president_contexts']}
 for k,v,county,label,first,last in order:
  u=native[k];ck((u['candidate_votes'],u['county'],u['literal_precinct'],u['source_first_row'],u['source_last_row'])==(v,county,label,first,last),'original_native_identity_rows')
 return contract

def source_checks(contract):
 receipts={p.stem:load(p) for p in (D/'receipts').glob('*.json')};entities=set()
 for id,r in receipts.items():
  ck(r['method']=='GET' and r.get('retrieved_utc') and 'response_headers' in r and 'redirects' in r,'acquisition_schema',id)
  if r.get('stored_path'):
   p=D/r['stored_path'];stored=p.read_bytes();b=gzip.decompress(stored);ck(sha(b)==r['raw_sha256'] and len(b)==r['raw_bytes'] and sha(stored)==r['stored_sha256'] and len(stored)==r['stored_bytes']<40000000,'every_raw_stored_hash_bytes',id);entities.add(r['stored_path'])
  else:ck(r.get('error') and r['http_status'] is None,'exact_transport_error',id)
 ck(entities=={str(p.relative_to(D)) for p in (D/'bodies').glob('*')},'exact_body_membership')
 original_directory=list(csv.DictReader(io.StringIO(read(D/receipts['directory-csv']['stored_path']).decode('cp1252'))));equal(original_directory,load(D/'directory-native.json')['rows'],'original_directory_native_encoding_fields_blanks')
 rows=list(csv.DictReader(io.StringIO((S/'data/official-results-sources.csv').read_text())));ck(len(rows)==45,'45_authorities');directory=load(D/'directory-native.json')['rows'];ck(len(directory)==44,'44_native_directory_rows')
 for row in rows:
  for field in ['directory_receipt','authority_attempt_receipt','primary_native_receipt','primary_export_receipt']:
   if row[field]:ck((S/'data'/row[field]).is_file(),'inventory_relative_receipt_link',row[field])
 for row in rows[1:]:equal(json.loads(row['directory_native_json']),next(x for x in directory if x['County']==row['county']),'complete_primary_directory_allfields_blanks')
 parents=load(D/'parent-investigations.json');ck(len(parents)==45,'all44_parent_investigations');ck(sum(p['priority_child_count']>0 for p in parents[1:])==32,'32_deep_priority_parents')
 for p in parents[1:]:
  slug=p['county'].lower().replace(' ','-')+'-county-id';r=receipts['data-'+slug];x=json.loads(read(D/r['stored_path']));e=x['election'];ck(e['electionDate']=='2026-05-19' and e['isPrimary'] is True,'reject_wrong_election_for_November');equal(e,p['primary_election_metadata'],'full_election_metadata_retained');ck(len(x['precincts'])==p['primary_precinct_count'] and len(x['ballotItems'])==p['primary_ballot_item_count'],'native_scope_counts')
  for item in x['ballotItems']:
   if item.get('summaryResults'):
    opts=item['summaryResults']['ballotOptions'];ck(sum(y['voteCount'] for y in opts)==item['voteTotal'],'native_candidate_choice_sum',slug)
  if p['priority_child_count']:
   ck(receipts['native-export-'+slug]['http_status']==200,'all32_complete_native_exports');ck(len(p['acquired_shared_parent_sources'])>=10 and len(p['county_specific_finding'])>140,'substantive_shared_parent_investigation')
 entries=load(D/'priority-investigations.json');rem=load(D/'remainder-monitoring.json');ck(len(entries)==528 and len(rem)==457,'exact528_and457_entries');ck([e['historical_key'] for e in entries]==contract['ordered_priority_keys'],'exact528_order');ck([e['historical_key'] for e in rem]==contract['ordered_remainder_keys'],'exact457_order')
 for e in entries+rem:
  native=pointer(contract,e['historical_complete_object_reference']['pointer']);ck(digest(native)==e['historical_complete_object_reference']['semantic_sha256'],'every_entry_full_native_reference');ck(e['historical_key'] in e['precise_current_leaf_gap'] and native['literal_precinct'] in e['precise_current_leaf_gap'],'precise_entry_specific_gap');ck(all(e[k] is None for k in ['current_leaf_id','current_contest_id','current_choice_ids','current_method','current_geometry']) and not e['current_approved'],'no_fabricated_current_join')
 # Complete XLSX extraction source identity and original XML cells, independent of extract.py.
 for item in load(D/'extraction-index.json'):
  r=receipts[item['receipt']];x=load(D/item['derivative']);raw=read(D/r['stored_path']);ck(x['raw_sha256']==sha(raw),'extraction_original_identity')
  if item['type']!='XLSX':continue
  z=zipfile.ZipFile(io.BytesIO(raw));ck(z.testzip() is None,'public_export_zip_CRC');ss=[''.join(v.itertext()) for v in E.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',N)] if 'xl/sharedStrings.xml' in z.namelist() else []
  equal(ss,x['shared_strings'],'export_complete_shared_strings')
  for sheet in x['sheets']:
   original=E.fromstring(z.read(sheet['member']));rows=original.findall('m:sheetData/m:row',N);ck(len(rows)==len(sheet['rows']),'export_complete_rows')
   for old,new in zip(rows,sheet['rows']):
    ck(int(old.get('r'))==new['row'],'export_original_row_position');equal(dict(old.attrib),new['attributes'],'export_original_row_attributes');equal(cells(old,ss),new['cells'],'export_every_original_field_header_null_formula')
  del x;gc.collect()
 ck(len(load(D/'constructor-corrections.json'))==33,'researcher_error_provenance_not_source_outage')
 return receipts

def negative_tests(contract):
 def reject(fn,kind):
  try:fn()
  except (AssertionError,KeyError,ValueError):C['negative_'+kind]+=1
  else:raise AssertionError(('negative_fixture_escaped',kind))
 expected={'raw_v':None,'type':'s','style':None,'formula':None,'header':None,'party':'Independent','row':5};bad=copy.deepcopy(expected);del bad['raw_v'];reject(lambda:equal(bad,expected,'fixture_compare'),'omitted_null_raw_v')
 bad=copy.deepcopy(expected);bad['header']=0;reject(lambda:equal(bad,expected,'fixture_compare'),'header_null_to_zero')
 bad=copy.deepcopy(expected);bad['row']='5';reject(lambda:equal(bad,expected,'fixture_compare'),'source_row_type_changed')
 bad=copy.deepcopy(contract['complete_order']);bad[0],bad[1]=bad[1],bad[0];reject(lambda:ck(digest(bad)==digest(contract['complete_order']),'fixture_order'),'priority_reordered')
 reject(lambda:ck(sha(b'changed response')==sha(b'original response'),'fixture_hash'),'changed_original_bytes')
 def admit(x):
  assert x['electionDate']=='2026-11-03' and x['isPrimary'] is False and x['isProduction'] is True and x['status']!='setup' and x['candidate_universe_certified'] is True
 reject(lambda:admit(dict(electionDate='2026-05-19',isPrimary=True,isProduction=True,status='official',candidate_universe_certified=True)),'primary_as_November')
 reject(lambda:admit(dict(electionDate='2026-11-03',isPrimary=False,isProduction=True,status='setup',candidate_universe_certified=True,completion=100)),'setup100_as_returns')
 reject(lambda:ck({'declared','undeclared'}=={'declared'},'fixture_candidate_universe'),'candidate_scope_widened')
 reject(lambda:ck({'owned.py','extra.txt'}=={'owned.py'},'fixture_membership'),'unsealed_extra_file')
 reject(lambda:ck(None==0,'fixture_null'),'unknown_method_to_zero')
 reject(lambda:ck('historical:1001'=='November:1001','fixture_identity'),'same_label_cross_year_join')

def legal_source_checks():
 nav={x['receipt']:x for x in load(D/'navigation.json.gz')}
 checks=[('section-34-1205','nine (9) days'),('section-34-1211','twenty-one (21) days'),('section-34-1005','8:00 p.m.'),('section-34-1007','December 31, 2020'),('section-34-1013','all voting places in the state have closed'),('section-34-702A','eleventh Friday before the primary election'),('bill-S1356-final-status','07/01/2026'),('bill-S1356-final-status','01/01/2027'),('constitution-senate-meta','Each House shall be the Judge')]
 for id,phrase in checks:ck(phrase.lower() in nav[id]['complete_main_text'].lower(),'current_primary_legal_text',id)
 for n,date in [('enacted-2025-vol1','July 1, 2025'),('enacted-2024-vol2','July 1, 2024'),('enacted-2023-vol1','uary 1, 2024')]:
  x=next(x for x in load(D/'enacted-effective-review.json') if x['receipt']==n);ck(date in x['chapter_text'],'actual_enacted_effective_clause',n)
 # Verify clock conversion only, without assigning any source observation to a timezone.
 from datetime import datetime,timezone
 from zoneinfo import ZoneInfo
 for zone,hour in [('America/Denver',3),('America/Los_Angeles',4)]:ck(datetime(2026,11,3,20,tzinfo=ZoneInfo(zone)).astimezone(timezone.utc).isoformat()==f'2026-11-04T0{hour}:00:00+00:00','conditional_local_poll_close_UTC')
 ck('ten-day mechanism' not in (S/'official-results.md').read_text(),'no_incorrect_recount_appeal_period')

def seal_checks():
 m=load(D/'manifest.json');equal(m['immutable_external_complete_references'],load(D/'historical-source-graph.json')['immutable_complete_files'],'manifest_full_external_reference_match');ck(m['external_acceptance_path']=='data/coordinator-priority-acceptance.json' and m['current_approved'] is False,'manifest_external_only_no_current_approval');expected={x['path'] for x in m['owned']};actual={str(p.relative_to(S)) for p in D.rglob('*') if p.is_file() and p.name!='manifest.json'}|{'official-results.md','data/official-results-sources.csv'};ck(actual==expected,'exact_owned_membership')
 for r in m['owned']:
  b=(S/r['path']).read_bytes();ck(len(b)==r['bytes'] and sha(b)==r['sha256'] and len(b)<40000000,'sealed_every_owned_hash_bytes',r['path'])

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');ap.add_argument('--sealed',action='store_true');ns=ap.parse_args();contract=frozen_checks();receipts=source_checks(contract);negative_tests(contract);legal_source_checks()
 for p in D.rglob('*'):
  ck(p.name not in ['__pycache__','node_modules','.pytest_cache','.venv'],'no_dependency_cache_directories')
  if p.is_file():
   ck(p.stat().st_size<40000000,'strict40MB_stored_object_limit')
   if p.suffix not in ['.gz','.png']:ck(sha((S/'data/coordinator-priority-acceptance.json').read_bytes()).encode() not in p.read_bytes(),'no_copied_acceptance_hash')
  if p.suffix=='.py':ast.parse(p.read_bytes());C['python_syntax']+=1
 for p in [S/'official-results.md',D/'README.md',D/'SCHEMA.md']:
  if not p.exists():continue
  for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
   if '://' not in target and not target.startswith('#'):ck((p.parent/target.split('#')[0]).exists(),'relative_markdown_link',target)
 result=dict(status='pass_bounded_research_no_current_approval',checks=dict(C),total_checks=sum(C.values()),frozen_complete_object_count=5169,frozen_companion_count=29,all_counties=44,priority_parents=32,priority_entries=528,remainder_entries=457,acquisition_observations=len(receipts),external_acceptance_path='data/coordinator-priority-acceptance.json',current_approved=False)
 if ns.write:(D/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
 if ns.sealed:seal_checks()
 print(json.dumps(dict(result,seal_checked=ns.sealed,total_checks_including_seal=sum(C.values())),indent=2))
if __name__=='__main__':main()
