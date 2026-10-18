"""Independent original-byte extraction; no use of peer counts for construction."""
from common import *
import csv,collections,io
ELECTIONS=['2024NovGen','2020NovGen','2021JanFedRun','2022NovGen','2022DecGenRun']
def english(a):return next((x['text'] for x in a or [] if x.get('languageId')=='en'),None)
def writegz(name,rows):
 b=''.join(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n' for r in rows).encode();(ROOT/'extracts'/name).write_bytes(gzip.compress(b,mtime=0))
refs=js(ROOT/'shared-inputs.json');by_path={r['path']:r for r in refs}
def original(path):
 r=by_path[path];b=(GA/path).read_bytes();assert sha(b)==r['stored_sha256'];raw=gzip.decompress(b);assert sha(raw)==r['raw_sha256'];return json.loads(raw)
raw=gzip.decompress((GA/'data/turnout/source/county-fips-2020.body.gz').read_bytes()).decode()
fips={r['COUNTYNAME']:r['STATEFP']+r['COUNTYFP'] for r in csv.DictReader(io.StringIO(raw),delimiter='|') if r['STATE']=='GA'}
state_paths={'2020NovGen':'data/turnout/source/state-2020-selected.body.gz'}
for r in js(GA/'data/turnout/source/shared-references.json'):state_paths[r['election_key']]=r['path']
state={k:original(v) for k,v in state_paths.items()}
requests=js(GA/'data/turnout/source/requests-counties.json');positions=[];controls=[];natives=[];state_controls={};schemas={}
def schema(v,path='',out=None):
 if out is None:out={}
 out.setdefault(path,set()).add(type(v).__name__)
 if isinstance(v,dict):
  for k,x in v.items():schema(x,path+'/'+k,out)
 elif isinstance(v,list):
  for x in v:schema(x,path+'/*',out)
 return out
def option_rows(d,source,ek,f,level,unit,base,options):
 for oi,o in enumerate(options):
  ptr=base+'/'+str(oi)
  row={'source_path':source,'election_key':ek,'county_fips':f,'level':level,'native_id':unit,'candidate_ordinal':oi,'candidate_id':o['id'],'nativeId':o.get('nativeId'),'name':o.get('name'),'party':o.get('party'),'isWriteIn':o.get('isWriteIn'),'isQualifiedWriteIn':o.get('isQualifiedWriteIn'),'isWinner':o.get('isWinner'),'source_pointer':ptr,'kind':'TOTAL','method_ordinal':None,'group_id':None,'group_name':None,'votes':o['voteCount'],'raw_vote_type':type(o['voteCount']).__name__}
  positions.append(row)
  for gi,g in enumerate(o.get('groupResults') or []):positions.append({**row,'kind':'METHOD','method_ordinal':gi,'group_id':g['groupId'],'group_name':g.get('groupName'),'source_pointer':ptr+'/groupResults/'+str(gi),'votes':g['voteCount'],'raw_vote_type':type(g['voteCount']).__name__})
for ek,d in state.items():
 b=d['ballotItemWithBreakdown'];opts=b['summaryResults']['ballotOptions'];scope={english(o['name']):o['voteCount'] for o in opts}
 assert len(d['jurisdiction']['childLocalities'])==159
 assert len(b['breakdownResults'])==159
 assert set(english(x['name']) for x in d['jurisdiction']['childLocalities'])==set(fips)
 state_controls[ek]={'source_path':state_paths[ek],'election':d['election'],'contest_id':b['id'],'contest_name':b['name'],'reportingStatus':b['reportingStatus'],'voteTotal':b['voteTotal'],'candidates':scope,'county_rows':len(b['breakdownResults']),'source_fields':list(d),'raw_ballots':d['election']['ballotsCast'],'usable_ballots':None,'status':'historical; source official flag is not November2026 approval'}
 option_rows(d,state_paths[ek],ek,None,'state',None,'/ballotItemWithBreakdown/summaryResults/ballotOptions',opts)
 for i,x in enumerate(b['breakdownResults']):option_rows(d,state_paths[ek],ek,fips[english(x['locality']['name'])],'state_county',x['locality']['id'],f'/ballotItemWithBreakdown/breakdownResults/{i}/ballotOptions',x['ballotOptions'])
for q in requests:
 path='data/turnout/source/'+q['id']+'.body.gz';d=original(path);ek=q['election_key'];name=q['county_name'];f=fips[name];b=d['ballotItemWithBreakdown'];e=d['election'];opts=b['summaryResults']['ballotOptions']
 assert english(d['jurisdiction']['name'])==name
 assert set(x['id'] for x in d['precincts'])==set(x['precinct']['id'] for x in b['breakdownResults'])
 option_rows(d,path,ek,f,'county',None,'/ballotItemWithBreakdown/summaryResults/ballotOptions',opts)
 inv={x['id']:(i,x) for i,x in enumerate(d['precincts'])};turnout={x['id']:(i,x) for i,x in enumerate(d.get('voterTurnout') or [])}
 # Retain full source objects, including administrative/unknown contexts. Original holds all other fields too.
 controls.append({'source_path':path,'request':q,'election_key':ek,'county_fips':f,'county_name':name,'jurisdiction_id':d['jurisdiction']['id'],'election':e,'request_ballot_id':q['county_ballot_item_id'],'response_ballot_id':b['id'],'contest_name':b['name'],'reportingStatus':b['reportingStatus'],'voteTotal':b['voteTotal'],'underVoteCount':b.get('underVoteCount'),'overVoteCount':b.get('overVoteCount'),'pollingPlaces':d['pollingPlaces'],'statistics':d['statistics'],'voterRegistration':d['voterRegistration'],'voterTurnout':d['voterTurnout'],'native_count':len(d['precincts']),'county_options_sum':sum(o['voteCount'] for o in opts),'ballots_cast':e['ballotsCast'] if ek=='2024NovGen' else None,'registered_voters':e['totalVoters'] if ek=='2024NovGen' else None})
 for i,x in enumerate(b['breakdownResults']):
  uid=x['precinct']['id'];ii,ip=inv[uid]
  natives.append({'source_path':path,'election_key':ek,'county_fips':f,'native_id':uid,'breakdown_ordinal':i,'inventory_ordinal':ii,'inventory_object':ip,'turnout_ordinal':turnout[uid][0],'turnout_object':turnout[uid][1],'breakdown_precinct_object':x['precinct'],'voteTotal':x['voteTotal'],'source_pointer':f'/ballotItemWithBreakdown/breakdownResults/{i}','underVoteCount':x.get('underVoteCount'),'overVoteCount':x.get('overVoteCount')})
  option_rows(d,path,ek,f,'precinct',uid,f'/ballotItemWithBreakdown/breakdownResults/{i}/ballotOptions',x['ballotOptions'])
 schemas[ek]=schema(d,out=schemas.get(ek,{}))
# Independent controls; preserve exact source option scopes.
checks={'county_records':len(controls),'native_identities':len(natives),'positions':len(positions),'elections':{}}
for ek in ELECTIONS:
 cc=[c for c in controls if c['election_key']==ek];assert len(cc)==159 and len({c['county_fips'] for c in cc})==159
 cp=[r for r in positions if r['election_key']==ek and r['level']=='county' and r['kind']=='TOTAL']
 tally=collections.Counter()
 for r in cp:tally[english(r['name'])]+=r['votes']
 expected=state_controls[ek]['candidates'];diff={n:tally[n]-v for n,v in expected.items()};assert not any(diff.values())
 extras={n:v for n,v in tally.items() if n not in expected}
 if ek=='2024NovGen':assert extras=={'Claudia De la Cruz (Ind)':13,'Cornel West (Ind)':6}
 else:assert extras=={}
 for r in cp:
  methods=[z['votes'] for z in positions if z['source_path']==r['source_path'] and z['level']=='county' and z['candidate_ordinal']==r['candidate_ordinal'] and z['kind']=='METHOD']
  assert sum(methods)==r['votes']
 checks['elections'][ek]={'counties':len(cc),'named_state_votes':sum(expected.values()),'county_all_options':sum(tally.values()),'candidate_differences':diff,'extra_options':extras,'native_rows':sum(c['native_count'] for c in cc),'source_clocks':sorted({(c['election'].get('asOf'),c['election'].get('lastUpdated')) for c in cc})}
np=[r for r in positions if r['level']=='precinct'];checks['native_candidate_nulls']=sum(r['votes'] is None for r in np if r['kind']=='TOTAL');checks['native_method_nulls']=sum(r['votes'] is None for r in np if r['kind']=='METHOD');checks['native_method_null_counties']=len({r['county_fips'] for r in np if r['kind']=='METHOD' and r['votes'] is None});checks['native_known_candidate_votes']=sum(r['votes'] for r in np if r['kind']=='TOTAL' and r['votes'] is not None);checks['native_known_method_votes']=sum(r['votes'] for r in np if r['kind']=='METHOD' and r['votes'] is not None)
checks['native_candidate_residual']=5250066-checks['native_known_candidate_votes'];checks['native_method_residual']=5250066-checks['native_known_method_votes'];checks['2024_ballots']=sum(c['ballots_cast'] for c in controls if c['election_key']=='2024NovGen');checks['2024_registration']=sum(c['registered_voters'] for c in controls if c['election_key']=='2024NovGen')
assert checks['positions']==76400 and checks['native_identities']==2701 and checks['native_candidate_nulls']==40 and checks['native_method_nulls']==22416
assert checks['2024_ballots']==5297264 and checks['2024_registration']==7219868
save(ROOT/'extracts/history-checks.json',checks);save(ROOT/'extracts/state-controls.json',state_controls);save(ROOT/'extracts/native-field-schema.json',{k:{p:sorted(v) for p,v in s.items()} for k,s in schemas.items()});writegz('source-positions.jsonl.gz',positions);writegz('county-controls.jsonl.gz',controls);writegz('native-identities.jsonl.gz',natives)
print(json.dumps({k:v for k,v in checks.items() if k!='elections'},indent=2))
