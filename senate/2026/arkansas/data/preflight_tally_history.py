"""Observed public Tally constructors; preserve export/API historical disagreements."""
from pathlib import Path
import collections,gzip,hashlib,json
DATA=Path(__file__).resolve().parent;NEWS=DATA/'news'
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 refs={r['id']:r for r in json.loads((NEWS/'manifest.json').read_bytes())};pins={}
 def raw(sid):
  r=refs[sid];stored=(NEWS/r['asset']).read_bytes();b=gzip.decompress(stored)
  assert r['status']==200 and sha(b)==r['raw_sha256'] and sha(stored)==r['stored_sha256'] and len(stored)<40000000
  pins[sid]={'url':r['url'],'final_url':r['final_url'],'original_bytes':len(b),'raw_sha256':sha(b),'stored_bytes':len(stored),'stored_sha256':sha(stored),'asset':'data/news/'+r['asset']}
  return b
 def load(sid):return json.loads(raw(sid))
 parent=raw('sos-history-current').decode();assert 'https://arkansas.tally-enr.com/#election=1844' in parent and 'https://arkansas.tally-enr.com/#election=1841' in parent
 shell=raw('tally-history-shell').decode();client=raw('tally-current-public-client').decode();assert '/assets/index-1.10.2-CFvkHgVV.js' in shell
 assert 'function dK(){return`${lK()}/appConfig.json`}' in client and '/FullDataFile.json' in client
 assert 'Contest/GetContestResults' in client and 'Contest/GetContestSearchList' in client
 config=load('tally-app-config');public=load('tally-client-config');assert public['totalResultsClientId']=='arkansas' and public['clientStateId']=='arkansas' and public['ownerFips']=='05'
 tables={}
 for year,eid,sid in [(2022,'1844','1123'),(2020,'1841','560')]:
  info=load(f'tally-election-{year}-info');meta=load(f'tally-{year}-contest-metadata');api=load(f'tally-{year}-federal-state');county=load(f'tally-{year}-federal-pulaski');full=load(f'tally-full-data-{year}')
  assert info['electionID']==api['electionID']==county['electionID']==eid
  assert info['response']['name']==f'{year} General' and meta['response']['contests'][sid]['contestName']=='U.S. Senate'
  assert info['response']['voteTypes']=={'1':{'voteTypeID':'1','description':'All'}}
  names={id:c['name'] for id,c in meta['response']['contests'][sid]['choices'].items()};sen=api['response']['contests'][sid];assert len(sen['locations'])==75
  state={c['choiceID']:c['totalVotes'] for c in sen['choices']};summed=collections.Counter()
  rows=[]
  for key,c in sen['locations'].items():
   values={v['choiceID']:v['totalVotes'] for v in c['choices']};assert set(values)==set(state) and sum(values.values())==c['totalVotes']
   summed.update(values);rows.append({'source_location_id':key,'source_county_name':info['response']['locations'][key]['locationName'],'raw_source_pointer':f'/response/contests/{sid}/locations/{key}','choices':values,'total':c['totalVotes']})
  assert dict(summed)==state and sum(state.values())==sen['totalVotes']
  pulaski=county['response']['contests'][sid];totals=collections.Counter();unitrows=[]
  for key,u in pulaski['locations'].items():
   values={v['choiceID']:v['totalVotes'] for v in u['choices']};assert sum(values.values())==u['totalVotes'];totals.update(values)
   assert key in info['response']['locations']['05119']['locations']
   unitrows.append({'location_id':key,'source_pointer':f'/response/contests/{sid}/locations/{key}','source_location_object':info['response']['locations']['05119']['locations'][key],'candidate_counts':values,'total':u['totalVotes']})
  assert dict(totals)=={c['choiceID']:c['totalVotes']for c in pulaski['choices']}=={c['choiceID']:c['totalVotes']for c in sen['locations']['05119']['choices']}
  fsen=next(c for c in full['ContestData'] if c['ContestName']=='U.S. Senate');fullnames={c['Name']:c['TotalVotes']for c in fsen['Candidates']};difference={names[k]:fullnames[names[k]]-v for k,v in state.items()}
  wrappers=fsen['Counties'];labels=collections.Counter((w['CountyName'],p['PrecinctName'])for w in wrappers for p in w['Precincts'])
  full_sums=collections.Counter();leafsums=collections.Counter()
  for w in wrappers:
   full_sums.update({v['Name']:v['TotalVotes']for v in w['Candidates']})
   for p in w['Precincts']:leafsums.update({v['Name']:v['TotalVotes']for v in p['Candidates']})
  assert dict(full_sums)==dict(leafsums)==fullnames
  assert difference==({2022:{'Natalie James':360,'Kenneth Cates':45,'Senator John Boozman':934},2020:{'Ricky Dale Harrington Jr.':143,'Senator Tom Cotton':81}}[year])
  tables[str(year)]={'electionID':eid,'source_name':info['response']['name'],'source_isOfficial':info['isOfficial'],'publisher_lastUpdated':info['lastUpdated'],'versionID':info['versionID'],'Senate_contest_ID':sid,'candidate_metadata':meta['response']['contests'][sid]['choices'],'source_voteTypes':info['response']['voteTypes'],'API_named_state_controls':{names[k]:v for k,v in state.items()},'API_total':sen['totalVotes'],'API_75_county_vectors':rows,'Pulaski_original_native_controls':unitrows,'Pulaski_native_count':len(unitrows),'FullData_original_summary':fullnames,'FullData_original_total':fsen['TotalVotes'],'FullData_minus_API':difference,'FullData_repeated_County_wrappers':len(wrappers),'FullData_actual_unique_county_names':len({w['CountyName']for w in wrappers}),'FullData_native_leaf_positions':sum(len(w['Precincts'])for w in wrappers),'FullData_duplicate_literal_county_precinct_keys':[{'CountyName':k[0],'PrecinctName':k[1],'occurrences':v}for k,v in labels.items()if v>1],'FullData_internal_candidate_sums_match':True,'source_scope':'Neither format overwrites the other. isOfficial is publisher metadata; independent original certification/FEC and complete native/API county acquisition still required. Native All type is not an ED/method allocation.'}
 out={'status':'pass_observed_public_routes_with_retained_export_API_disagreements','source_pins':pins,'authority_chain':['ActualSOS historical links:#election=1844/#election=1841','ActualTally shell script src','Published production appConfig.json constructor','Returned public client configuration','Observed Election/Contest request constructors + source-returned IDs','Published FullDataFile download constructor'],'public_routes_only':'No auth, private endpoint or client allowlist used as election authority. Fragment election selection is UI state, not an HTTP query parameter.','tables':tables,'qualification':'Historical sources republished December2025, not measured election-night observations. FullData and API differ despite both marked official; retain every original field and compare actual primary certificates before selecting a historical baseline.2020 has no Democratic nominee; Harrington party field blank here requires actual ballot/certification rather than relabel asD. No current IDs, geography, cadence, exact remainder or accepted priority.'}
 (DATA/'coordinator-tally-history-preflight.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({y:{'API_total':t['API_total'],'FullData_total':t['FullData_original_total'],'difference':t['FullData_minus_API'],'counties':75,'Pulaski_native':t['Pulaski_native_count']}for y,t in tables.items()}))
if __name__=='__main__':main()
