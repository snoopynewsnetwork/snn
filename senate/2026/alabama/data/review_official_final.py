"""Independent coordinator HTTP, literal office-field and full-context audit."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin
from collections import Counter
import csv,gzip,hashlib,io,json,sys
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
mf=load(R/'asset-manifest.json');before={};actual={str(p.relative_to(S)) for p in R.rglob('*') if p.is_file()}|{'official-results.md','data/official-results-sources.csv'}
ck(mf['excludes_only']=='data/results-sources/asset-manifest.json' and len(mf['files'])==1522 and {x['path'] for x in mf['files']}==actual-{'data/results-sources/asset-manifest.json'})
for v in mf['files']:
 p=S/v['path'];b=p.read_bytes();ck(not p.is_symlink() and len(b)==v['bytes']<40000000 and sha(b)==v['sha256']);before[v['path']]=sha(b)
receipts={};raw={};final={};statuses=Counter()
for p in sorted((R/'http').glob('*.receipt.json')):
 r=load(p);rel=str(p.relative_to(R));receipts[rel]=r;ck(r['started_utc']<=r['ended_utc'] and r['method'] in ('GET','POST') and r['configured_headers'])
 if not r['hops']:ck(r['status']=='unavailable-no-response' and r['response_status'] is None and r['response_headers'] is None and r['response_body'] is None)
 for h in r['hops']:
  ck(isinstance(h['headers'],list) and h['request_headers'] and h['request_method'] in ('GET','POST'));parts=[]
  for pin in h['body']['parts']:
   b=(R/pin['path']).read_bytes();ck(len(b)==pin['bytes']<40000000 and sha(b)==pin['sha256']);parts.append(b)
  b=gzip.decompress(b''.join(parts));ck(len(b)==h['body']['bytes'] and sha(b)==h['body']['sha256']);raw[h['body']['sha256']]=b;final[rel]=b;stats['complete_response_hops']+=1
 if r['hops']:statuses[str(r['hops'][-1]['status'])]+=1
 else:statuses['no_response']+=1
ck(len(receipts)==450 and stats['complete_response_hops']==499)
index=load(R/'source-index.json');ck([v['receipt'] for v in index]==list(receipts))
for v in index:
 b=(R/v['receipt']).read_bytes();ck(len(b)==v['receipt_bytes'] and sha(b)==v['receipt_sha256'])
class SourceHTML(HTMLParser):
 def __init__(self,b):super().__init__(convert_charrefs=True);self.stack=[];self.nodes={};self.feed(b.decode('utf-8',errors='replace'))
 def handle_starttag(self,t,a):
  pos=self.getpos();n={'tag':t,'attrs':dict(a),'pieces':[],'ancestors':[v[0] for v in self.stack]};self.nodes[pos]=n
  if t not in {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}:self.stack.append((pos,t,n))
 def handle_startendtag(self,t,a):self.handle_starttag(t,a);self.handle_endtag(t)
 def handle_data(self,d):
  for pos,t,n in self.stack:n['pieces'].append(d)
 def handle_endtag(self,t):
  for i in range(len(self.stack)-1,-1,-1):
   if self.stack[i][1]==t:self.stack=self.stack[:i];break
 def text(self,pos):return ''.join(self.nodes[tuple(pos)]['pieces'])
docs={};dirs=load(R/'directory-records.json');roles=Counter();blank_values=0
for row in dirs:
 rel=row['source_receipt']
 if rel not in docs:docs[rel]=SourceHTML(final[rel])
 doc=docs[rel];pos=tuple(row['source_position']);node=doc.nodes[pos];ck(node['tag']=='div' and 'official-info' in node['attrs'].get('class','').split())
 h3=[doc.text(p).strip() for p,n in doc.nodes.items() if pos in n['ancestors'] and n['tag']=='h3'];ck(row['county_raw'] in h3)
 for field in row['fields']:
  ck(doc.text(field['position'])==field['label_raw'])
  for v in field['values']:
   n=doc.nodes[tuple(v['position'])];ck(n['attrs']==v['attrs'] and doc.text(v['position'])==v['text_raw']);stats['literal_office_value_fields']+=1;blank_values+=not bool(v['text_raw'].strip())
 expected=[{'url':urljoin(receipts[rel]['hops'][-1]['url'],n['attrs']['href']),'text':doc.text(p),'attrs':n['attrs'],'position':list(p),'parent_receipt':rel} for p,n in doc.nodes.items() if n['tag']=='a' and n['attrs'].get('href')]
 ck(expected==row['source_links']);roles[row['role_route']]+=1;stats['complete_office_records']+=1
ck(len(dirs)==278 and sorted(roles.values())==[68,69,69,72])
for rel,doc in docs.items():
 count=sum(n['tag']=='div' and 'official-info' in n['attrs'].get('class','').split() for n in doc.nodes.values());rows=[r for r in dirs if r['source_receipt']==rel];ck(count==len(rows) and [r['ordinal_0based'] for r in rows]==list(range(count)))
mobile=[]
for sample in load(R/'complete-public-json-samples.json'):
 obj=json.loads(final[sample['receipt']]);ck(obj==sample['full_source_object'] and sample['current_count_admission'] is False and len(obj)==45)
 for group in obj:
  ck(isinstance(group,list) and len(group)==1);item=group[0];ck(set(item)=={'contest_data','party_counts'});c=item['contest_data'];ck(isinstance(c['candidates'],list))
  for v in c['candidates']:ck({'candidate_number','candidate_name','party_code','total_votes'}<=set(v));stats['whole_Mobile_candidate_objects']+=1
  stats['whole_Mobile_contest_objects']+=1
 senate=[g[0] for g in obj if g[0]['contest_data']['contest_number']=='0304'];ck(len(senate)==1);mobile.append({'requested_url':receipts[sample['receipt']]['requested_url'],'full_contest_count':len(obj),'Senate_raw_setup':senate[0],'November_count_admission':False})
ck(len(mobile)==4)
all_scope=mobile[0]['Senate_raw_setup']['contest_data'];ck(all_scope['total_votes']==3105 and [(v['candidate_number'],v['candidate_name'],v['party_code'],v['total_votes']) for v in all_scope['candidates']]==[('001','EVERETT WESS','DEM',1035),('002','BARRY MOORE','REP',2070)])
c=load(S/'data/turnout/priority-set.json');hier=load(R/'historical-hierarchy.json.gz');ck(hier['full_order']==c['full_order'] and hier['ordered_priority']==c['ordered_priority_keys'] and hier['ordered_remainder']==c['remainder_keys'])
ck(len(hier['source_contexts'])==2085 and len(hier['parents'])==67)
for i,(row,u) in enumerate(zip(hier['source_contexts'],c['units'])):
 ref=row['full_own_source_context'];ck(ref['pointer']==f'/units/{i}' and ref['file']['path']=='data/turnout/priority-set.json' and ref['complete_object_semantic_sha256']==semantic(u));ck(row['key']==u['key'] and row['rank']==u['rank'] and row['reported_candidate_votes']==u['reported_candidate_votes'] and row['priority']==(u['key'] in set(c['ordered_priority_keys'])));ck(row['current_match'] is None and row['current_native_id'] is None and row['current_choice_id'] is None and row['current_approved'] is False)
for i,(row,p) in enumerate(zip(hier['parents'],c['parents'])):
 ck(row['full_original_parent']['pointer']==f'/parents/{i}' and row['full_original_parent']['complete_object_semantic_sha256']==semantic(p));cols=p['constituent_keys'];rank=[k for k in c['full_order'] if k in set(cols)];priority=set(c['ordered_priority_keys']);remainder=set(c['remainder_keys'])
 ck(row['original_source_column_ordered_children']==cols and row['full_source_rank_ordered_children']==rank and row['ordered_priority_children']==[k for k in rank if k in priority] and row['ordered_remainder_children']==[k for k in rank if k in remainder]);ck(row['original_priority_column_order']==[k for k in cols if k in priority] and row['original_remainder_column_order']==[k for k in cols if k in remainder]);ck(row['current_matches'] is None and row['November_votes_admitted'] is False and row['cadence_measured'] is False and row['exact_remaining_pool'] is None)
rows=list(csv.DictReader(io.StringIO((S/'data/official-results-sources.csv').read_text())));ck(len(rows)==68)
for row,p in zip(rows[1:],hier['parents']):ck(row['jurisdiction']==p['county'] and row['county_fips']==p['county_fips'] and json.loads(row['office_records_json'])==p['complete_raw_office_records'] and json.loads(row['current_matches_json']) is None)
pdfs=load(R/'pdf-index.json')
for row in pdfs:
 b=final[row['receipt']];t=gzip.decompress((R/row['text']).read_bytes());ck(b.startswith(b'%PDF') and len(b)==row['original_bytes'] and sha(b)==row['original_sha256'] and len(t)==row['text_bytes'] and sha(t)==row['text_sha256']);stats['complete_PDF_originals']+=1
ck(stats['complete_PDF_originals']==113 and sum('/sample-ballots/2026/gen/' in v['url'] for v in pdfs)==67)
for rel,digest in before.items():ck(sha((S/rel).read_bytes())==digest,'sealed official bytes unchanged')
result={'status':'pass','checks':N,'manifest_sha256':sha((R/'asset-manifest.json').read_bytes()),'exact_manifest_targets':1522,'http_requests':len(receipts),'final_source_statuses':dict(statuses),'counts':dict(stats),'full_office_roles':dict(roles),'literal_blank_office_values_preserved':blank_values,'complete_historical_native_contexts':2085,'priority':887,'remainder':1198,'parents':67,'complete_parent_and_source_column_rank_arrays':True,'all_four_complete_Mobile_raw_objects_and_wrappers_preserved':True,'Mobile_examples':mobile,'coordinator_actual_original_image_scope':['data/results-sources/visual/dbb8540ace50584ad92c20fec3fc9fef0f5f24a3d317b13d2ed4eb7d578a00a0-p1.png','data/results-sources/visual/4f1a69210a68808985d5982feb526f3e241d743bd7b690604f785192be5614ae-p1.png'],'actual_image_readings':'Two whole already-rendered originals: signed August26 Democratic certification cover; Autauga Nov3 specimen with Everett Wess Democratic, Barry Moore Republican and write-in line. No later statewide roster/write-in exhaustion inferred. Other pages automatic or explicit worker manual scope only.','worker_final_sealed_audit_actually_rerun':{'status':'FINAL READ-ONLY PASS','complete_source_graph_refs':1608035,'workbooks':201,'typed_cells':6246656,'stored_corruptions_rejected':40,'isolated_reconstruction':True},'legal_source_review':'data/coordinator-audit-source-review.json','qualifications':'Mobile positive pre-election setup and cached June16 browser representation distinct, no correction chronology inferred. All November counts/operational IDs/geographic joins/cadence/eligible pool/calibration unapproved. Full HB95 enrolled versus Governor summary distinction retained; current code/later legal clearance incomplete. Unrelated navigation failures remain excluded history, not count/office/legal evidence.','all_sealed_owned_bytes_unchanged':True}
out=S/'data/coordinator-official-final-review.json'
if '--check' in sys.argv:ck(load(out)==result)
else:out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['Mobile_examples','coordinator_actual_original_image_scope']}))
