"""Independent offline integrity/semantic checks; --sealed is strictly read-only.
No network, producer imports, collector, current-ID or legal approval.
"""
from pathlib import Path
from collections import Counter
from xml.etree import ElementTree as ET
import csv,gzip,hashlib,io,json,re,sys,zipfile
O=Path(__file__).resolve().parent; S=O.parents[1]
REPORT=S/'official-results.md'; CSV=S/'data/official-results-sources.csv'
def sha(b): return hashlib.sha256(b).hexdigest()
def load(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def raw_body(b):return b''.join(gzip.decompress((O/part['path']).read_bytes())for part in b.get('parts',[b]))
def owned(): return sorted([REPORT,CSV,*[p for p in O.rglob('*') if p.is_file()]])
def xml(e):return dict(tag=e.tag,attributes=e.attrib,text=e.text,tail=e.tail,children=[xml(c) for c in e])
def current_rejections(v):
 # Research qualification only: even a synthetic passing schema needs review.
 reasons=[]
 if v.get('date')!='2026-11-03':reasons.append('date')
 if v.get('stage')!='General':reasons.append('stage')
 if v.get('office')!='Senator in Congress':reasons.append('office')
 if v.get('kind')!='genuine_returns':reasons.append('publication_kind')
 if v.get('scope_observed') is not True:reasons.append('unobserved_scope')
 if not v.get('complete_envelope'):reasons.append('incomplete_envelope')
 if not v.get('observed_native_ids'):reasons.append('unobserved_ids')
 if v.get('coordinator_accepted') is not True:reasons.append('coordinator_review')
 return reasons
def remaining(v):
 # Only explicitly sourced eligible outstanding *votes* could populate a pool.
 if v.get('kind')!='explicit_eligible_unprocessed_votes' or not v.get('source_status'):return None
 n=v.get('value');return n if type(n) is int and n>=0 else None
def run(sealed=False):
 checks=0
 def ck(v,label):
  nonlocal checks
  if not v:raise AssertionError(label)
  checks+=1
 files=owned(); ck(REPORT.exists() and CSV.exists(),'report and inventory exist')
 for p in files:
  ck(p.stat().st_size<40000000,'strict stored size '+str(p))
  ck(not any(x in p.parts for x in ['__pycache__','node_modules','.cache']),'no cache/dependency tree')
 # Authority is PATH ONLY; do not copy its bytes/digest to owned artifacts.
 authority=S/'data/coordinator-priority-acceptance.json'; a=load(authority)
 authority_digest=sha(authority.read_bytes())
 for p in files:
  if p.suffix in ['.json','.md','.csv','.py']:
   ck(authority_digest not in p.read_text(),'no reverse authority pin '+str(p))
 deps=load(O/'readonly-inputs.json')
 for r in deps:
  ck(r['path']!='data/coordinator-priority-acceptance.json','no authority copy')
  b=(S/r['path']).read_bytes();ck(len(b)==r['bytes'] and sha(b)==r['sha256'],'readonly input '+r['path'])
 replay=load(O/'reconstruction.json')
 ck((replay['root_fields'],replay['whole_companions'],replay['recursive_objects'],replay['complete_partitions'],replay['producer_assets'])==(25,174,397917,3,781),'whole replay scope')
 ck(replay['checks']==401790 and not replay['producer_writer_run'],'independent replay passed')
 c=load(S/'data/turnout/priority-set.json');h=load(O/'all-parent-hierarchy.json.gz')
 priority=load(O/'priority-investigations.json.gz');remainder=load(O/'remainder-investigations.json.gz');rows=priority+remainder
 ck((len(priority),len(remainder),len(h['parents']))==(1470,924,351),'1470/924/351 hierarchy')
 ck(h['ordered_full_keys']==a['ordered_full_keys'],'full source rank order')
 ck(h['ordered_priority_keys']==c['ordered_priority_keys'] and h['ordered_remainder_keys']==c['ordered_remainder_keys'],'partition orders')
 ck(len(c)==25 and len(c['all_parent_child_maps'])==351,'all roots and parents')
 ck(sum(p['priority_parent'] for p in h['parents'])==287,'287 shared priority parents')
 parentmap={p['source_parent_key']:p for p in h['parents']};child_keys=[]
 for p,original in zip(h['parents'],c['all_parent_child_maps']):
  ck(p['all_source_child_arrays']==original,'whole parent child arrays')
  evidence=load(O/p['investigation'])
  ck(evidence['historical_parent_full_object']==original,'full parent body')
  ck(evidence['source_parent_key']==p['source_parent_key'],'explicit parent identity')
  ck(not evidence['secretary_local_election_directory']['raw_field_completeness'],'directory access not fabricated')
  ck(evidence['current']['current_admission'] is False and evidence['current']['eligible_unprocessed_votes'] is None,'parent admission qualification')
  for field in ['current_date_native_id','current_election_native_id','current_stage_native_id','current_office_native_id','current_candidate_choice_ids','current_party_ids','current_reporting_unit_ids','current_method_ids','current_status_ids','geographic_match']:
   ck(evidence['current'][field] is None,'no native inference '+field)
  for chain in evidence['bounded_chain_requests']:
   ck((O/chain['receipt']).exists(),'parent receipt materializable')
   if chain.get('structure'):ck((O/chain['structure']).exists(),'whole sample materializable')
  child_keys.extend(original['native_keys_source_order'])
 ck(Counter(child_keys)==Counter(a['ordered_full_keys']),'every child exactly once across parents')
 for i,(r,original) in enumerate(zip(rows,c['all_unit_order'])):
  ck(r['research_rank']==i+1,'research order')
  ck(r['complete_frozen_order_object']==original and r['complete_original_source_record']==original['source_record'],'whole recursive record')
  ck(r['historical_native_key']==a['ordered_full_keys'][i],'literal key')
  p=parentmap[r['source_parent_key']]
  ck(r['historical_native_key'] in p['all_source_child_arrays']['native_keys_source_order'],'literal membership proof')
  ck(r['parent_investigation']==p['investigation'] and r['shared_parent_proof']['explicit_shared'],'shared parent not leaf feed')
  ck(not r['current']['returns_admitted'] and all(v is None for k,v in r['current'].items() if k!='returns_admitted'),'no current leaf admission')
 def named(r):return sum(int(v.replace(',','')) for v in r['complete_original_source_record']['raw_row'][3:5])
 # Raw row is retained without requiring a vote-only projection.
 if 'raw_row' not in rows[0]['complete_original_source_record']:
  receipts=load(O/'source/reused-original-receipts.json');src=next(r for r in receipts if r['id']=='sos-2024-senate-precinct-csv')
  rr=list(csv.reader(io.StringIO(gzip.decompress((S/src['immutable_body_path']).read_bytes()).decode('utf-8-sig'))))
  bykey={json.dumps(r[:3],ensure_ascii=False,separators=(',',':')):r for r in rr[2:-1]}
  amounts=[sum(int(x.replace(',','')) for x in bykey[r['historical_native_key']][3:5]) for r in rows]
 else:amounts=[named(r) for r in rows]
 ck((sum(amounts),sum(amounts[:15]),sum(amounts[:1469]),sum(amounts[:1470]),sum(amounts[1470:]))==(3407108,58012,2725231,2726450,680658),'independent exact cutoff arithmetic')
 ck(rows[1469]['literal_tuple']==['Northampton','3','B'] and amounts[1469]==1219,'crossing tuple and increment')
 with CSV.open(newline='') as f:inventory=list(csv.DictReader(f))
 ck(len(inventory)==355 and sum(r['authority_scope']=='municipal research parent' for r in inventory)==351,'all municipal inventory plus four state/federal roles')
 for r in inventory:
  ck((O/r['authority_investigation']).exists(),'authority locator exists')
  ck(r['current_November_returns_admitted']=='false' and r['known_eligible_remaining_votes']=='','inventory admission/pool qualification')
 with (O/'all-unit-index.csv').open(newline='') as f:locators=list(csv.DictReader(f))
 ck(len(locators)==2394,'all context locators')
 for i,r in enumerate(locators):
  ck(int(r['research_rank'])==i+1 and r['historical_literal_key']==rows[i]['historical_native_key'],'ordered locator literal')
  ck(r['source_parent_key']==rows[i]['source_parent_key'],'locator shared parent')
  ck(int(r['zero_based_record'])==(i if i<1470 else i-1470),'exact complete-body locator')
 # Every response hop body, including redirects/errors, independently rehashed.
 seen=set();http=[load(p) for p in sorted((O/'source/http').glob('*.json'))]
 for r in http:
  ck(all(k in r for k in ['method','query','request_body','parent','literal_href','started_utc','requested_url','final_url','status','error','redirects']),'exact request envelope')
  for hop in r['redirects']:
   ck(all(k in hop for k in ['requested_url','final_url','utc','status','request_headers','response_headers','body']),'hop envelope')
  for b in [r.get('body'),*[hop.get('body') for hop in r['redirects']]]:
   if not b:continue
   for part in b.get('parts',[b]):
    if part['path'] in seen:continue
    seen.add(part['path']);stored=(O/part['path']).read_bytes();raw=gzip.decompress(stored)
    ck(len(stored)==part['stored_bytes'] and sha(stored)==part['stored_sha256'],'stored entity exact')
    ck(len(raw)==part['raw_bytes'] and sha(raw)==part['raw_sha256'],'complete raw part exact')
    ck(Path(part['path']).name.startswith(b['raw_sha256']),'once by whole body hash')
   if 'parts' in b:
    raw=raw_body(b);ck(len(raw)==b['raw_bytes'] and sha(raw)==b['raw_sha256'],'ordered full split reconstruction')
    ck([p['byte_start'] for p in b['parts']]==[sum(x['raw_bytes'] for x in b['parts'][:i])for i in range(len(b['parts']))],'ordered byte ranges')
 ck(seen=={'source/byhash/'+p.name for p in (O/'source/byhash').glob('*.gz')},'no orphan originals')
 idx=load(O/'structure-index.json');positive={r['body']['raw_sha256'] for r in http if r['status']==200 and r.get('body')}
 ck(positive=={r['body_sha256'] for r in idx['responses']},'every distinct positive body has complete structure')
 coverage=load(O/'coverage.json')
 ck(coverage['actual_response_receipts']==len(http) and coverage['response_statuses']==dict(Counter(str(r['status'])for r in http)),'coverage all statuses')
 ck(coverage['complete_structural_samples']==dict(Counter(r['format'] for r in idx['responses'])),'coverage full format counts')
 ck(coverage['priority_parent_HTTP_attempts']==287,'all priority parents actual bounded HTTP attempts')
 for r in idx['responses']:
  z=load(O/r['structure']);b=raw_body(z['original_body'])
  ck(sha(b)==r['body_sha256'],'structure points to whole original')
  if z['format']=='JSON':ck(z['complete_response']==json.loads(b),'complete JSON response including all envelope fields')
  if z['format']=='JavaScript':ck(z['complete_text']==b.decode('utf-8','replace'),'whole observed script')
  if z['format']=='PDF':ck(z['pages']==z['text'].split('\f'),'complete text page boundaries, not visual assertion')
  if z['format']=='XLSX':
   archive=zipfile.ZipFile(io.BytesIO(b));ck([m['name'] for m in z['members']]==archive.namelist(),'every workbook member')
   for m in z['members']:
    raw=archive.read(m['name']);ck(len(raw)==m['bytes'] and sha(raw)==m['sha256'],'complete workbook member hash')
    if m['name'].endswith(('.xml','.rels')) and m['tree'] is not None:ck(m['tree']==xml(ET.fromstring(raw)),'every recursive cell/XML position')
 ck(len(idx['historical_csv'])==8,'all historical CSV bodies')
 for r in idx['historical_csv']:
  z=load(O/r['structure']);raw=gzip.decompress((S/r['body_path']).read_bytes());rr=list(csv.reader(io.StringIO(raw.decode('utf-8-sig'))))
  ck(z['all_records_including_ragged_headers_party_rows_blanks_and_footer']==rr,'all CSV raw cells/headers/party/footer')
  ck(z['record_lengths']==list(map(len,rr)),'ragged/null distinctions')
  for i,col in enumerate(z['columns']):ck(col['party_position_exists']==(i<len(rr[1])) and col['party_raw']==(rr[1][i] if i<len(rr[1]) else None),'party null vs blank position')
 q=load(O/'current-qualification.json');ck(all(v is None for v in q['current_native_ids'].values()) and not q['current_returns_admitted'],'current IDs and votes unknown')
 ck(q['eligible_unprocessed_votes'] is None and q['measured_cadence'] is None,'unknown pool and measured cadence')
 fixtures=load(O/'fixtures.json')
 for f in fixtures['admission_cases']:ck(f['required_rejection'] in current_rejections(f['input']),f['name'])
 for f in fixtures['remaining_cases']:ck(remaining(f['input'])==f['expected'],f['name'])
 correction=fixtures['cumulative_correction'];ck(correction['later']['named']==98 and correction['later']['named']-correction['earlier']['named']==-2,'correction may reduce cumulative vote count')
 ck(correction['expected_current']==correction['later'] and correction['expected_current']['null_method'] is None,'replace cumulative snapshot, retain null/blank/control fields')
 visual=load(O/'visual-qa.json')
 for r in visual['actual_viewed_pages']:
  b=(O/r['preview']).read_bytes();ck(len(b)==r['bytes'] and sha(b)==r['sha256'],'viewed preview exact')
 # Static report link QA. Public URLs already frozen; no refresh is attempted.
 for target in re.findall(r'\]\(([^)]+)\)',REPORT.read_text()):
  if not target.startswith(('http:','https:','#')):ck((REPORT.parent/target.split('#')[0]).exists(),'report artifact link '+target)
 if sealed:
  manifest=load(O/'asset-manifest.json');expected={str(p.relative_to(S)) for p in files if p!=O/'asset-manifest.json'}
  ck({r['path'] for r in manifest['owned']}==expected,'manifest excludes only itself')
  ck(len(manifest['owned'])==len(expected),'no duplicate manifest members')
  for r in manifest['owned']:
   b=(S/r['path']).read_bytes();ck(len(b)==r['bytes'] and sha(b)==r['sha256'],'sealed asset '+r['path'])
  seal=load(O/'final-seal.json');ck('manifest_sha256' not in seal,'acyclic final seal')
  for r in seal['pinned_owned']:
   b=(S/r['path']).read_bytes();ck(len(b)==r['bytes'] and sha(b)==r['sha256'],'final seal own pin')
 result=dict(status='pass',sealed_read_only=sealed,checks=checks,owned_files_at_validation=len(files),complete_HTTP_receipts=len(http),distinct_complete_response_entities=len(seen),structural_positive_bodies=len(positive),priority=1470,remainder=924,parents=351,priority_parents=287,negative_admission_cases=len(fixtures['admission_cases']),remaining_pool_cases=len(fixtures['remaining_cases']),actual_viewed_PDF_pages=3,current_admission=False,legal_or_roster_exhaustion=False)
 if not sealed:(O/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result));return result
if __name__=='__main__':run('--sealed' in sys.argv)
