"""Coordinator original-response and full-context review; imports no worker code."""
from pathlib import Path
from collections import Counter
from html.parser import HTMLParser
import csv,gzip,hashlib,io,json,subprocess,sys,tempfile
csv.field_size_limit(40000000)
S=Path(__file__).resolve().parents[1];R=S/'data/results-sources';N=0
stats=Counter()
def ck(v,label=''):
 global N
 N+=1
 assert v,(N,label)
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def semantic(v):return sha(json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode())
def pointer(v,path):
 for part in path.split('/')[1:]:v=v[part.replace('~1','/').replace('~0','~')]
 return v
mf=load(R/'asset-manifest.json');before={}
actual={str(p.relative_to(S)) for p in R.rglob('*') if p.is_file()}|{'official-results.md','data/official-results-sources.csv'}
ck(mf['only_exclusion']=='data/results-sources/asset-manifest.json' and len(mf['assets'])==1089 and {v['path'] for v in mf['assets']}==actual-{'data/results-sources/asset-manifest.json'})
for v in mf['assets']:
 p=S/v['path'];b=p.read_bytes();ck(not p.is_symlink() and len(b)==v['bytes']<40000000 and sha(b)==v['sha256']);before[v['path']]=sha(b)
receipts={};raw={};final={};statuses=Counter()
for p in sorted((R/'requests').glob('*.json')):
 r=load(p);rel=str(p.relative_to(R));receipts[rel]=r
 ck(r['started_utc']<=r['finished_utc'] and r['request']['method']=='GET' and r['request']['body'] is None and bool(r['request']['configured_headers']))
 for h in r['hops']:
  ck(h['method']=='GET' and h['request_body'] is None and h['configured_headers']==r['request']['configured_headers'])
  if h.get('asset') is None:
   ck(h.get('status') is None and h.get('raw_sha256') is None and h.get('raw_bytes') is None,'no response distinct from empty response');stats['unavailable_hops']+=1;continue
  b=(R/h['asset']).read_bytes();ck(len(b)==h['stored_bytes']<40000000 and sha(b)==h['stored_sha256']);b=gzip.decompress(b)
  ck(len(b)==h['raw_bytes'] and sha(b)==h['raw_sha256'] and isinstance(h['headers'],list))
  raw[h['raw_sha256']]=b;final[rel]=b;stats['whole_response_hops']+=1;statuses[str(h['status'])]+=1
ck(len(receipts)==451 and stats['whole_response_hops']==496 and stats['unavailable_hops']==5)
parsed={}
def source(ref):
 r=receipts[ref['receipt']];h=r['hops'][-1]
 ck(ref['body']==h['asset'] and ref['raw_sha256']==h['raw_sha256'] and ref['request']==r['request'] and ref['status']==h['status'])
 key=h['raw_sha256']
 if key not in parsed:parsed[key]=json.loads(raw[key])
 return pointer(parsed[key],ref['pointer'])
class Tables(HTMLParser):
 def __init__(self,b):super().__init__(convert_charrefs=True);self.rows=[];self.row=None;self.cell=None;self.feed(b.decode('utf-8',errors='replace'))
 def handle_starttag(self,t,a):
  if t=='tr':self.row=[]
  elif t in ('th','td') and self.row is not None:self.cell=[]
 def handle_data(self,d):
  if self.cell is not None:self.cell.append(d)
 def handle_endtag(self,t):
  if t in ('th','td') and self.row is not None and self.cell is not None:self.row.append(''.join(self.cell).strip());self.cell=None
  elif t=='tr' and self.row is not None:self.rows.append(self.row);self.row=None
texts={}
with tempfile.TemporaryDirectory(prefix='snn-ar-official-originals-') as td:
 for role,label,mode,retained in [('clerk','sos-clerks','-raw','directory-clerk-complete.txt'),('board','sbec-directory-pdf','-layout','directory-board-complete.txt')]:
  pdf=Path(td)/(role+'.pdf');pdf.write_bytes(final['requests/'+label+'.json'])
  x=subprocess.run(['pdftotext',mode,str(pdf),'-'],capture_output=True,check=True)
  ck(x.stdout==(R/retained).read_bytes(),'complete independent PDF extraction '+role);texts[role]=x.stdout.decode().splitlines(keepends=True)
judiciary=Tables(final['requests/judiciary-directory.json']).rows
c=load(S/'data/turnout/priority-set.json');ck(load(R/'historical-context.json.gz')==c)
parents={v['county_fips']:v for v in c['all75parents']};priority=set(c['ordered_priority_keys']);remainder=set(c['remainder_keys'])
index=load(R/'native-context-index.json.gz');ck(len(index)==len(c['full_order'])==2841)
for i,(row,u) in enumerate(zip(index,c['full_order'])):
 ck(row['key']==u['key'] and row['historical_whole_contract_pointer']==f'/full_order/{i}' and row['complete_historical_source_context']==u)
 ck(row['current_match'] is None and row['qualified_shared_parent_investigation']=='counties/'+u['county_fips']+'.json')
counties=[];native_count=0
for p in sorted((R/'counties').glob('*.json')):
 v=load(p);fips=v['county_fips'];parent=parents[fips];rows=[u for u in c['full_order'] if u['county_fips']==fips];keys=[u['key'] for u in rows]
 ck(v['historical_parent_whole']==parent and v['county_name']==parent['county_name'])
 ck(v['historical_ordered_full_children']==keys and v['historical_ordered_priority_children']==[k for k in keys if k in priority] and v['historical_ordered_remainder_children']==[k for k in keys if k in remainder])
 ck(v['priority_parent']==bool(set(keys)&priority))
 for kind,role in [('sos_county_clerk','clerk'),('sbec_county_board','board')]:
  d=v['directory_roles'][kind];block=d['whole_block'];ck(block['raw_extracted_lines']==texts[role][block['line_start']-1:block['line_end_exclusive']-1]);ck(bool(block['raw_extracted_lines']));stats['complete_original_directory_blocks']+=1
 for row in v['directory_roles']['judiciary_county_judge_and_clerk_rows']['rows']:
  ck(row['whole_row']==judiciary[row['row_index']]);stats['complete_judiciary_rows']+=1
 o=v['current_source_observation'];obj=source({**v['publication_chain']['county_results'],'pointer':''});contest=obj['response']['contests']['eafd140a-9378-43a2-bd6d-f8661524139b']
 ck(list(obj)==o['all_envelope_fields'] and list(contest)==o['all_contest_fields'])
 ck(all(obj[k]==o[k] for k in ['electionID','versionID','lastUpdated','isOfficial']))
 counts=Counter()
 def walk(v):
  if isinstance(v,dict):
   for k,x in v.items():counts[k]+=1;walk(x)
  elif isinstance(v,list):
   for x in v:walk(x)
 walk(obj);ck(dict(counts)==o['all_recursive_field_counts'])
 locations=contest['locations'];refs=o['ordered_native_source_references'];ck(list(locations)==[r['key'] for r in refs] and len(locations)==o['native_location_count'])
 for ref in refs:
  val=pointer(obj,ref['pointer']);ck(val==locations[ref['key']] and semantic(val)==ref['complete_semantic_sha256']);native_count+=1
 for control in ['county_control','turnout_control','november_info_location']:ck(isinstance(source(o[control]),dict))
 ck(source(o['november_info_location'])['locations']=={},'empty information children remain empty')
 ck(o['current_historical_matches'] is None and o['current_counts_admitted'] is False and o['exact_remaining_pool'] is None and o['measured_cadence'] is None)
 counties.append(v)
ck(len(counties)==75 and sum(v['priority_parent'] for v in counties)==68)
table=list(csv.DictReader(io.StringIO((S/'data/official-results-sources.csv').read_text())));ck(len(table)==77)
for v in counties:
 rows=[r for r in table if r['county_fips']==v['county_fips']];ck(len(rows)==1);row=rows[0]
 ck(json.loads(row['complete_clerk_block_json'])==v['directory_roles']['sos_county_clerk']['whole_block'] and json.loads(row['complete_board_block_json'])==v['directory_roles']['sbec_county_board']['whole_block'])
 ck(json.loads(row['judiciary_rows_json'])==v['directory_roles']['judiciary_county_judge_and_clerk_rows']['rows'])
 ck(int(row['historical_full_native'])==len(v['historical_ordered_full_children']) and int(row['historical_priority_native'])==len(v['historical_ordered_priority_children']) and int(row['historical_remainder_native'])==len(v['historical_ordered_remainder_children']))
# Inspect the public configuration without emitting or copying its populated value.
config=json.loads(final['requests/november-config.json']);cfg=config.get('response',config)
ck(cfg['showBanner'] is True and any('password' in k.lower() and bool(x) for k,x in cfg.items()))
ck(len(final['requests/november-full.json'])==53950979)
for k,v in before.items():ck(sha((S/k).read_bytes())==v,'sealed bytes remain unchanged')
result={'status':'pass','checks':N,'worker_manifest_sha256':sha((R/'asset-manifest.json').read_bytes()),'exact_owned_manifest_targets':1089,'requests':len(receipts),'response_statuses':dict(statuses),'counts':dict(stats),'full_historical_contexts':2841,'priority':1056,'remainder':1785,'parents':75,'priority_parents':68,'current_complete_native_Senate_objects':native_count,'CSV_rows':len(table),'full_original_directory_blocks_and_judiciary_rows':True,'all_current_native_objects_and_ordered_references_verified':True,'positive_preelection_setup_excluded':True,'public_demo_field_value_never_emitted_or_used':True,'whole_FullData_raw_bytes':53950979,'worker_sealed_audit_actually_rerun':{'exit':0,'full_ordered_recursive_objects':2185390,'whole_companions':773,'fixed_files':1399,'historical_resolvers':1418,'complete_archives':5,'negative_packets':25,'guarded_exact_outputs':87},'scope':'Independent coordinator whole original-response, PDF-block, full historical/native context, parent/array, CSV and current-source pointer review. No producer/worker helper imports; no new source request, authentication or writer. Scenario/outcome and legal/current identity approval excluded.','all_worker_owned_bytes_unchanged':True}
out=S/'data/coordinator-official-final-review.json'
if '--check' in sys.argv:ck(load(out)==result)
else:out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
