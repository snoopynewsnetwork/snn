"""Coordinator audit of original entities and full current-source context.

No worker modules, writers, network acquisition or source mutation are used.
The worker's separate whole frozen-graph replay and denied-socket rebuild are
also required; this script independently checks the source-facing products.
"""
from pathlib import Path
from collections import Counter
from html.parser import HTMLParser
import csv,gzip,hashlib,io,json,re,sys,urllib.parse

S=Path(__file__).resolve().parents[1];R=S/'data/results-sources';N=0;CACHE={};JSON={}
def ck(v,label=''):
    global N
    N+=1
    assert v,(N,label)
def sha(b):return hashlib.sha256(b).hexdigest()
def sem(x):return sha(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def load(p):
    b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def original(pin):
    k=pin['raw_sha256']
    if k not in CACHE:
        b=(R/pin['path']).read_bytes();ck(len(b)==pin['stored_bytes'] and sha(b)==pin['stored_sha256'],pin['path'])
        b=gzip.decompress(b);ck(len(b)==pin['raw_bytes'] and sha(b)==k,k);CACHE[k]=b
    return CACHE[k]
def resolve(ref):
    pin=ref['complete_response_entity'];key=pin['raw_sha256'];b=original(pin)
    if key not in JSON:JSON[key]=json.loads(b)
    v=JSON[key]
    for k in ref['pointer'].split('/')[1:]:
        k=k.replace('~1','/').replace('~0','~');v=v[int(k)] if isinstance(v,list) else v[k]
    return v
def fullfields(v):
    global N
    N+=1
    if isinstance(v,dict):
        for x in v.values():fullfields(x)
    elif isinstance(v,list):
        for x in v:fullfields(x)
class Text(HTMLParser):
    def __init__(self):super().__init__(convert_charrefs=True);self.pieces=[];self.skip=0
    def handle_starttag(self,t,a):
        if t in ['script','style']:self.skip+=1
    def handle_endtag(self,t):
        if t in ['script','style']:self.skip=max(0,self.skip-1)
    def handle_data(self,d):
        if not self.skip:self.pieces.append(d)
def compact(t):return re.sub(r'\s+','',t)

manifest=load(R/'asset-manifest.json');rows=manifest['files']
ck(manifest['excludes_only']=='data/results-sources/asset-manifest.json')
actual={str(p.relative_to(S)) for p in R.rglob('*') if p.is_file()}|{'official-results.md','data/official-results-sources.csv'}
ck(len(rows)==len({r['path'] for r in rows})==2661)
ck({r['path'] for r in rows}==actual-{'data/results-sources/asset-manifest.json'})
for p in rows:
    b=(S/p['path']).read_bytes();ck(len(b)==p['bytes']<40000000 and sha(b)==p['sha256'],p['path'])
for p in R.rglob('*'):ck(not {'__pycache__','node_modules','.venv','.pytest_cache'}.intersection(p.parts))
receipts={};statuses=Counter();hopcount=0
for p in sorted((R/'requests').glob('*.json')):
    r=load(p);ck(r['key']==p.stem and r['key'] not in receipts);receipts[r['key']]=r
    ck(bool(r['public_parent_edge']) and r['request_method'] in ['GET','POST'] and bool(r['started_at_utc']))
    if r['request_method']=='POST':
        ck(set(r['submitted_fields'])=={'LocalityUid'});ck(urllib.parse.parse_qs(r['submitted_body'])=={k:[v] for k,v in r['submitted_fields'].items()})
    for h in r['hops']:
        hopcount+=1;statuses[str(h['status'])]+=1
        if h.get('body') is not None:
            original(h['body']);ck(isinstance(h['response_headers'],list) and isinstance(h['status'],int))
        else:ck(bool(h.get('error')) or h['status'] is None)
ck(len(receipts)==1192 and len(CACHE)==1182)
def body(key):return original(receipts[key]['hops'][-1]['body'])
contract=load(S/'data/turnout/priority-set.json');ordered=contract['ordered_units'];parents=load(R/'parent-investigations.json')
ck(len(ordered)==2669 and len(parents)==133)
ck(sum(p['kind']=='county' for p in parents)==95 and sum(p['kind']!='county' for p in parents)==38)
state=json.loads(body('november-senate'));e=state['election'];sitem=state['ballotItemWithBreakdown']
ck(e['isProduction'] is True and e['isPrimary'] is False and e['isOfficialResults'] is False and e['electionDate']=='2026-11-03')
ck(sitem['voteTotal']==0 and len(sitem['breakdownResults'])==133)
ck([o['nativeId'] for o in sitem['summaryResults']['ballotOptions']]==['cs290','cs291','wi-cc142'])
native=methods=directory=0;original_native=[]
for p,hp in zip(parents,contract['parent_inventory']):
    ck(p['historical_parent_key']==hp['historical_parent_key'] and p['literal_parent']==hp['historical_literal_label'])
    hk=p['historical_parent_key'];expected=[u['key'] for u in ordered if u['parent_key']==hk]
    ck(p['hierarchy']['full_source_rank_ordered_children']==expected)
    ck(p['hierarchy']['ordered_priority_children']==[k for k in expected if k in contract['ordered_priority_keys']])
    ck(p['hierarchy']['ordered_remainder_children']==[k for k in expected if k in contract['ordered_remainder_keys']])
    j=resolve(p['complete_current_locality_body']);fullfields(j);le=j['election'];item=j['ballotItemWithBreakdown'];xs=item['breakdownResults']
    ck(le['electionDate']=='2026-11-03' and le['isProduction'] and not le['isPrimary'] and not le['isOfficialResults'])
    ck(le['id']==p['current_election_id_observed_setup_only'] and item['id']==p['current_contest_id_observed_setup_only'])
    ck(item['voteTotal']==p['current_candidate_vote_sum']==0 and len(xs)==p['current_native_objects'])
    ck(item['reportingStatus']==p['current_reporting_status'])
    for key,source in [('source_asOf','asOf'),('source_lastUpdated','lastUpdated'),('source_nextUpdateAt','nextUpdateAt'),('source_ballotsCast_literal','ballotsCast'),('source_totalVoters_literal','totalVoters')]:ck(p[key]==le[source])
    cm=0
    for x in xs:
        native+=1;ck(x['voteTotal']==0 and len(x['ballotOptions'])==3)
        ck([o['nativeId'] for o in x['ballotOptions']]==['cs290','cs291','wi-cc142'])
        for o in x['ballotOptions']:
            ck(o['voteCount']==0 and len(o['groupResults'])==5 and sum(g['voteCount'] for g in o['groupResults'])==0)
            for g in o['groupResults']:ck(g['voteCount']==0 and bool(g['groupId']) and len(g['groupName'])>0);cm+=1
        original_native.append(x)
    ck(cm==p['current_candidate_method_objects']);methods+=cm
    for k in ['current_leaf_mapping','current_method_crossyear_mapping','current_geometry_mapping','remaining_eligible_vote_pool','measured_vote_publication_cadence']:ck(p[k] is None)
    ck(p['current_returns_admitted'] is False)
    role=p['complete_directory_contact_role_fields']
    if role['status']=='observed':
        r=receipts[p['selected_directory_request']]
        ck(r['submitted_fields']['LocalityUid']==p['directory_option']['attributes']['value'])
        directory+=1;text=body(r['key']).decode('utf-8');start=text.index('General Registrar Office Contact Information')
        rawrows=[m.group(0) for m in re.finditer(r'<div class="data-row">(.*?)</div>',text[start:],re.S)]
        ck(rawrows==[v['complete_inner_html'] for v in role['fields']])
        for i,v in enumerate(role['fields']):
            ck(v['row_position']==i)
            rawcells=re.findall(r'<p\b[^>]*>(.*?)</p>',rawrows[i],re.S)
            ck(len(rawcells)==len(v['paragraph_values_in_order']))
            for raw,parsed in zip(rawcells,v['paragraph_values_in_order']):
                t=Text();t.feed(raw);ck(compact(''.join(t.pieces))==compact(parsed))
    else:ck(p['literal_parent']=='Covington City' and role['fields'] is None)
ck(native==2528 and methods==37920 and directory==132)
ni=[json.loads(b) for b in gzip.decompress((R/'current-native-inventory.jsonl.gz').read_bytes()).splitlines()]
ck(len(ni)==native)
for n,x in zip(ni,original_native):ck(resolve(n['whole_current_native_context'])==x and n['whole_current_native_semantic_sha256']==sem(x) and n['votes_admitted'] is False and n['unapproved_historical_match'] is None)
full=[json.loads(b) for b in gzip.decompress((R/'full-native-hierarchy.jsonl.gz').read_bytes()).splitlines()]
pr=[json.loads(b) for b in gzip.decompress((R/'priority-investigations.jsonl.gz').read_bytes()).splitlines()]
rest=[json.loads(b) for b in gzip.decompress((R/'remainder-investigations.jsonl.gz').read_bytes()).splitlines()]
ck(len(full)==2669 and full[:1538]==pr and full[1538:]==rest)
for r,u in zip(full,ordered):ck(r['source_key']==u['key'] and r['source_rank']==u['rank'] and r['current_native_match'] is None and r['current_physical_geometry_match'] is None)
sections=load(R/'inspections/code-sections.json');law=body('law-full').decode('utf-8');starts=[m.start() for m in re.finditer(r'<b>§ 24\.2-',law)]
ck(len(sections)==len(starts)==590)
for i,section in enumerate(sections):
    lo,hi=section['character_span'];ck(lo==starts[i] and (i+1==len(starts) or hi==starts[i+1]))
    t=Text();t.feed(law[lo:hi]);ck(compact(''.join(t.pieces))==compact(section['complete_text']))
ck(any('2027' in s['title'] for s in sections))
csvrows=list(csv.DictReader(io.StringIO((S/'data/official-results-sources.csv').read_text())))
ck(len(csvrows)==133 and [r['parent_key'] for r in csvrows]==[p['historical_parent_key'] for p in parents])
result={'status':'pass','checks':N,'owned_manifest_targets':len(rows),'manifest_sha256':sha((R/'asset-manifest.json').read_bytes()),'actual_requests':len(receipts),'response_hops':hopcount,'distinct_complete_original_entities':len(CACHE),'response_status_counts':dict(sorted(statuses.items())),'whole_current_state_and_locality_Senate_entities':134,'whole_current_native_objects':native,'candidate_native_method_entries':methods,'admitted_votes':False,'directory_complete_records':directory,'missing_directory_parent':'Covington City; local pages separate','full_code_sections_and_versions':len(sections),'historical_ordered_inventory':len(full),'ordered_priority':len(pr),'ordered_remainder':len(rest),'review_scope':'Independent original entity/hash/request/full current objects/parent arrays/directory literal rows/590 full code spans; worker whole frozen graph and 94-product offline rebuild additionally rerun. No legal/geometry/live approval.'}
out=S/'data/coordinator-official-final-review.json'
if '--check' in sys.argv:ck(load(out)==result)
else:out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
