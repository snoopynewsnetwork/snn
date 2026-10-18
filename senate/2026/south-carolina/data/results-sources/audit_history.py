#!/usr/bin/env python3
"""Independent, offline results-source audit. Does not call worker/coordinator parsers.
Every frozen object survives by a pinned dependency AND full copies in county-records.json.gz.
XML indices are zero-based ALL-child indices, not XPath same-name indices.
"""
import collections,csv,functools,gzip,hashlib,io,json,pathlib,re,zipfile,xml.etree.ElementTree as ET
ROOT=pathlib.Path(__file__).resolve().parent;DATA=ROOT.parent;T=DATA/'turnout'
sha=lambda b:hashlib.sha256(b).hexdigest()
def write(n,d): (ROOT/n).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def point(d,p):
 for x in p.strip('/').split('/'):
  x=x.replace('~1','/').replace('~0','~');d=d[int(x)] if isinstance(d,list) else d[x]
 return d
def xp(root,path):
 parts=path.strip('/').split('/');assert parts[0]==root.tag
 for part in parts[1:]:
  m=re.fullmatch(r'(.+)\[(\d+)\]',part)
  if m:
   tag,i=m.groups();root=list(root)[int(i)];assert root.tag==tag
  else:
   children=[x for x in root if x.tag==part];assert len(children)==1;root=children[0]
 return root

def audit():
 b=(T/'priority-set.json').read_bytes();assert len(b)==33917555 and sha(b)=='a4dc8e50ce09889e5873d1f54c887dbef50a42a0b7bf600b4ab6663afab4ccef'
 c=json.loads(b);accept=json.loads((DATA/'coordinator-priority-acceptance.json').read_bytes());assert accept['accepted'] and accept['contract']['sha256']==sha(b)
 obs={};dependencies=[]
 def pin(p,role):
  p=p.resolve();b=p.read_bytes();dependencies.append({'path':str(p.relative_to(DATA.parent)),'role':role,'bytes':len(b),'sha256':sha(b)})
 pin(T/'priority-set.json','frozen complete contract');pin(DATA/'coordinator-priority-acceptance.json','external historical acceptance')
 for k in ['source_observations','legacy_source_observations','original_combined_json_observations']:
  for ident,o in c[k].items():
   if 'body_path' not in o:continue
   obs[ident]=o;p=T/o['body_path'];stored=p.read_bytes();assert len(stored)==o['stored_bytes'] and sha(stored)==o['stored_sha256'];raw=gzip.decompress(stored);assert len(raw)==o['original_bytes'] and sha(raw)==o['original_sha256'];pin(p,'reused original '+ident)
   if o.get('metadata_path'):pin(T/o['metadata_path'],'reused metadata '+ident)
 @functools.lru_cache(maxsize=12)
 def document(ident):
  o=obs[ident];b=gzip.decompress((T/o['body_path']).read_bytes())
  if 'zip_member' in o:
   b=zipfile.ZipFile(io.BytesIO(b)).read(o['zip_member']);
   if o.get('xml_member_sha256'):assert sha(b)==o['xml_member_sha256']
   return ET.fromstring(b) if b.lstrip().startswith(b'<?xml') else b
  return json.loads(b)
 labels=['2024-pres','2020-senate','2022-senate','2022-governor'];db={};checks={};db_metadata={};residuals=[];county_controls=[]
 for label in labels:
  combined=document(label+'-combined')['data']['contestGranularData'];methods=document(label+'-methods')['data']['contestGranularData']
  actual={x['candidateId'] for x in combined['candidates'] if x['candidate']['pseudocandidate'] in [None,'ALL_OTHER_CANDIDATES']}
  db_metadata[label]={'combined':{k:v for k,v in combined.items() if k!='divisions'},'methods':{k:v for k,v in methods.items() if k!='divisions'},'source_ids':[label+'-combined',label+'-methods']}
  for mode,d in [('combined',combined),('methods',methods)]:
   stack=[(d['divisions'],'/data/contestGranularData/divisions',[])];nodes=leaves=positions=0
   while stack:
    n,p,anc=stack.pop();anc=anc+[n['division']['id']];db[label,mode,p]=n;nodes+=1;positions+=len(n['granularRow'])
    if not n.get('children'):leaves+=1
    else:
     child_sums=collections.Counter()
     for x in n['children']:
      for row in x['granularRow']:child_sums[row['candidateId'],row['partyId'],row['voteChannelId']]+=row['votes'] or 0
     for row in n['granularRow']:
      key=(row['candidateId'],row['partyId'],row['voteChannelId']);delta=(row['votes'] or 0)-child_sums[key]
      if delta:residuals.append({'contest':label,'scope':mode,'pointer':p,'raw_row':row,'child_sum':child_sums[key],'residual':delta})
    for i,x in reversed(list(enumerate(n.get('children') or []))):stack.append((x,p+'/children/'+str(i),anc))
   checks[label+':'+mode]={'nodes':nodes,'leaves':leaves,'positions':positions}
  root=combined['divisions'];assert len(root['children'])==46
  for n in root['children']:
   name=n['division']['name'];f=next(x for x in c['counties'] if x['name']==name)
   total=sum(x['votes'] for x in n['granularRow'] if x['candidateId'] in actual)
   if label=='2024-pres':assert total==f['candidate_votes']
   county_controls.append({'contest':label,'county_fips':f['county_fips'],'division':n['division'],'combined_rows':n['granularRow'],'candidate_votes':total,'source_id':label+'-combined'})
  for row in root['granularRow']:
   assert row['votes']==sum(next(x['votes'] for x in n['granularRow'] if (x['candidateId'],x['partyId'],x['voteChannelId'])==(row['candidateId'],row['partyId'],row['voteChannelId'])) for n in root['children'])
 # Verify every retained raw DB position, including candidate/control flags and all methods.
 n=0;seen=set()
 with gzip.open(T/'extracts/source-positions.jsonl.gz','rt') as f:
  for line in f:
   r=json.loads(line);key=(r['contest_label'],r['observation_scope'],r['source_pointer']);assert key not in seen;seen.add(key)
   path,idx=r['source_pointer'].rsplit('/granularRow/',1);node=db[r['contest_label'],r['observation_scope'],path];assert node['granularRow'][int(idx)]==r['raw_value'];assert node['division']==r['division'];n+=1
 assert n==516586==sum(v['positions'] for v in checks.values())
 # Verify XML raw positions with repaired full-child locators, not name-only guesses.
 xmln=0;xml_ids=set();xml_seen=set()
 with gzip.open(T/'extracts/legacy-source-positions.jsonl.gz','rt') as f:
  for line in f:
   r=json.loads(line);root=document(r['source_id']);node=xp(root,r['source_pointer']);key=(r['source_id'],r['source_pointer'],r.get('contest_label'),r.get('context'));assert key not in xml_seen;xml_seen.add(key)
   assert node.tag==r['tag'] and dict(node.attrib)==r['attributes'] and node.text==r['text'];xmln+=1;xml_ids.add(r['source_id'])
 assert xmln==290542
 jsonn=0
 with gzip.open(T/'extracts/legacy-json-source-positions.jsonl.gz','rt') as f:
  for line in f:
   r=json.loads(line);assert point(document(r['source_id']),r['source_pointer'])==r['raw_object'];jsonn+=1
 assert jsonn==368
 # Clarendon enabled TXT is a separate alternative. Verify every retained original line/column.
 txtid='legacy2022-clarendon-pinned-detailtxt';o=obs[txtid];tb=gzip.decompress((T/o['body_path']).read_bytes());tz=zipfile.ZipFile(io.BytesIO(tb));txt=tz.read(tz.namelist()[0]).decode('utf-8-sig').splitlines();txtn=0
 with gzip.open(T/'extracts/clarendon-2022-txt-source-positions.jsonl.gz','rt') as f:
  for line in f:
   r=json.loads(line);assert txt[r['line_ordinal']]==r['raw_line'];assert re.split(r'\s{2,}',r['raw_line'].strip())==r['fields'];txtn+=1
 txtcells=0;txtnativecells=0
 with open(T/'extracts/clarendon-2022-txt-candidate-methods.csv',newline='') as f:
  for r in csv.DictReader(f):
   fields=re.split(r'\s{2,}',txt[int(r['line_ordinal'])].strip());assert int(fields[int(r['column_ordinal'])].replace(',',''))==int(r['votes']);txtcells+=1;txtnativecells+=r['level']=='native'
 counts=collections.Counter();native_totals=collections.Counter();xmltotals=collections.Counter();vhmn=0;xml_unavailable=[]
 for county in c['counties']:
  for label,units in county['historical_constituents'].items():
   d=document(label+'-combined')
   actual={x['candidateId'] for x in d['data']['contestGranularData']['candidates'] if x['candidate']['pseudocandidate'] in [None,'ALL_OTHER_CANDIDATES']}
   for u in units:
    node=point(d,u['source_pointer']);assert node['division']==u['raw_division'];assert node['division']['id']==u['native_id'];assert node['division']['name']==u['native_name'];assert sum(r['votes'] for r in node['granularRow'] if r['candidateId'] in actual)==u['candidate_votes'];mn=point(document(u['method_source_ref']),u['method_source_pointer']);assert node['division']==mn['division'];assert sorted({str(r['voteChannelId']) for r in mn['granularRow']})==sorted(u['method_ids']);counts['db_leaves']+=1
  for year,units in county['voter_history_constituents'].items():
   for u in units:
    raw=point(document(u['source_id']),u['source_pointer']);assert all(raw[k]==v for k,v in u['raw_identity'].items());assert raw['totalRegistered']==u['total_registered'];assert raw['totalVoting']==u['total_participating'];vhmn+=1
  for label,units in county['original_enr_combined_json_constituents'].items():
   for u in units:
    d=document(u['source_id']);assert point(d,u['native_name_pointer'])==u['native_name'];v=point(d,u['candidate_vector_pointer']);assert sum(v)==u['candidate_votes'];native_totals[label]+=sum(v);counts['json_leaves']+=1
  for label,units in county['original_enr_constituents'].items():
   for u in units:
    for pp in u['source_pointers']:
     node=xp(document(u['source_id']),pp);assert node.attrib['name']==u['name']
    counts['xml_leaves']+=1
 assert counts['db_leaves']==9635 and counts['json_leaves']==9635 and counts['xml_leaves']==9579 and vhmn==7078
 for label in labels:assert native_totals[label]==sum(x['candidate_votes'] for x in county_controls if x['contest']==label)
 for n in ['source-positions.jsonl.gz','legacy-source-positions.jsonl.gz','legacy-json-source-positions.jsonl.gz','legacy-candidate-methods.csv.gz','clarendon-2022-txt-source-positions.jsonl.gz','clarendon-2022-txt-candidate-methods.csv','native-units.csv.gz','legacy-native-units.csv.gz','legacy-json-native-units.csv.gz']:pin(T/'extracts'/n,'complete source-position reference')
 for n in ['turnout.md','data/county-turnout.csv','data/turnout/asset-manifest.json','data/turnout/validation.json','county-partisanship.md','data/county-baselines.csv','data/baselines/asset-manifest.json']:pin(DATA.parent/n,'final peer output metadata pin')
 assert [x['geography_key'] for x in c['counties']]==c['ordered_keys'];assert len(c['counties'])==46
 assert sum(x['candidate_votes'] for x in c['counties'])==2548140;assert sum(x['candidate_votes'] for x in c['counties'][:17])==2061601
 write('historical-identities.json',db_metadata);write('historical-county-controls.json',county_controls);write('historical-residuals.json',residuals)
 # References include every separate source entity and every metadata record. No aggregate-dependent hashes.
 dependencies=list({x['path']:x for x in dependencies}.values());write('dependencies.json',sorted(dependencies,key=lambda x:x['path']))
 out={'status':'pass_independent_original_scoped_audit','contract_sha256':sha(b),'contract_bytes':len(b),'db':checks,'db_positions':sum(x['positions'] for x in checks.values()),'xml_positions':xmln,'Clarendon_TXT_lines':txtn,'Clarendon_TXT_method_cells':txtcells,'Clarendon_TXT_native_method_cells':txtnativecells,'Clarendon_TXT_county_summary_method_cells':txtcells-txtnativecells,'xml_source_ids':sorted(xml_ids),'json_complete_objects':jsonn,'native_counts':dict(counts),'vhm_leaves':vhmn,'county_count':46,'priority_count':17,'remainder_count':29,'remainder_votes':486539,'state_actual_candidate_controls':dict(native_totals),'db_hierarchy_residuals':len(residuals),'source_entity_count':len(obs),'scope':'original source positions and source-native views only; all cross-view identities/geography/method differences remain; no November results admitted'}
 write('historical-audit.json',out);print(json.dumps(out,indent=2))
if __name__=='__main__':audit()
