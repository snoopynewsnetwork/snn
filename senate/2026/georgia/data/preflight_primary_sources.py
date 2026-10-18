#!/usr/bin/env python3
"""Coordinator primary app discovery/control checks; no research dispatch approval."""
from pathlib import Path
from collections import Counter
import datetime,gzip,hashlib,json,re
ROOT=Path(__file__).resolve().parent;NEWS=ROOT/'news'
manifest={r['id']:r for r in json.loads((NEWS/'manifest.json').read_text())}
def raw(key):
 m=manifest[key];s=(NEWS/m['asset']).read_bytes();b=gzip.decompress(s)
 assert len(b)==m['bytes'] and hashlib.sha256(b).hexdigest()==m['raw_sha256'] and hashlib.sha256(s).hexdigest()==m['stored_sha256']
 return b
def read(key):
 assert manifest[key]['status']==200
 return json.loads(raw(key))
def text(value):return ' | '.join(x['text']for x in value)
main=raw('sos-results-main-js').decode();service=raw('sos-results-service-chunk-js').decode();shell=raw('sos-results-app').decode()
assert '<base href="/results/public/">'in shell and 'endpoint:"/results/public/api"'in main
assert '${this.baseUrl}/jurisdictions/${t}'in service and '${this.baseUrl}/elections/${t}/${r}/data'in service and '/ballot-item/${o}'in service
jurisdiction=read('sos-results-jurisdiction');assert len(jurisdiction['elections'])==117
ids={e['publicElectionId']:e for e in jurisdiction['elections']}
assert not any(e['electionDate']=='2026-11-03'for e in ids.values())
checks=[];priority=[]
for prefix,eid,contest in [('2024-general','2024NovGen','President of the US'),('2021-federal-runoff','2021JanFedRun','US Senate (Perdue)'),('2022-general','2022NovGen','US Senate'),('2022-runoff','2022DecGenRun','US Senate')]:
 key='sos-'+prefix+'-api-data-selected';d=read(key);x=d['ballotItemWithBreakdown'];assert text(x['name'])==contest
 assert manifest[key]['url'].endswith('/data/ballot-item/'+x['id'])
 assert eid in ids and d['election']['electionDate']==ids[eid]['electionDate']
 assert d['election']['isOfficialResults']and d['election']['isProduction']
 counties=x['breakdownResults'];assert len(counties)==len({text(c['locality']['name'])for c in counties})==159
 assert len(d['localityElections'])==159
 candidates=x['summaryResults']['ballotOptions'];sums=Counter();method_cells=0;method_errors=[]
 for c in counties:
  assert sum(a['voteCount']for a in c['ballotOptions'])==c['voteTotal']
  for a in c['ballotOptions']:
   sums[text(a['name'])]+=a['voteCount'];groups=a['groupResults']
   method_cells+=len(groups)
   if sum(g['voteCount']for g in groups)!=a['voteCount']:method_errors.append({'county':text(c['locality']['name']),'candidate':text(a['name']),'candidate_votes':a['voteCount'],'method_sum':sum(g['voteCount']for g in groups)})
 assert not method_errors,method_errors
 assert sum(sums.values())==x['voteTotal']==sum(c['voteTotal']for c in counties)
 assert {text(c['name']):c['voteCount']for c in candidates}==dict(sums)
 checks.append({'source_id':key,'URL':manifest[key]['url'],'public_election_id':eid,'source_ballot_item_id':x['id'],'contest':contest,'date':ids[eid]['electionDate'],'all_counties':159,'candidate_count':len(candidates),'candidate_votes':x['voteTotal'],'candidate_controls':dict(sums),'county_candidate_cells':sum(len(c['ballotOptions'])for c in counties),'county_candidate_method_cells':method_cells,'state_asOf':d['election']['asOf'],'state_lastUpdated':d['election']['lastUpdated'],'state_ballotsCast':d['election']['ballotsCast'],'state_totalVoters':d['election']['totalVoters'],'precinct_rows':len(d['precincts']),'polling_place_rows':len(d['pollingPlaces']),'source_sha256':manifest[key]['raw_sha256']})
 if eid=='2024NovGen':
  ranked=sorted(counties,key=lambda c:(-c['voteTotal'],text(c['locality']['name'])));den=x['voteTotal'];cumulative=0
  for c in ranked:
   if cumulative*5>=den*4:break
   priority.append({'name':text(c['locality']['name']),'votes':c['voteTotal'],'source_locality_id':c['locality']['id'],'parent_ballot_item_id':c['parentBallotItemId']});cumulative+=c['voteTotal']
  top15=sum(c['voteTotal']for c in ranked[:15]);prior=cumulative-priority[-1]['votes']
  clerk=(ROOT.parent.parent/'ohio/data/baselines/house-2024.txt').read_text();section=clerk.split('GEORGIA',1)[1].split('FOR UNITED STATES REPRESENTATIVE',1)[0]
  for label,v in [('Republican',2663117),('Democratic',2548017),('Libertarian',20684),('Green',18229)]:
   m=re.search(label+r'\s*\.+\s*([\d,]+)',section);assert m and int(m[1].replace(',',''))==v
result={'status':'pass','checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Primary historical app preflight only; independent full candidate universe/native/county/FIPS reconciliation required before acceptance.','app_discovery':'Official results index -> published SPA base/main/imported service chunk -> literal API endpoint/templates -> jurisdiction published electionIDs -> metadata/data -> returned ballot-itemIDs -> selected county breakdown. No guessed election/contest IDs.','jurisdiction_elections':117,'November2026_general_ID_observed':False,'root_current_child_localities':len(jurisdiction['childLocalities']),'historical_checks':checks,'2024_named_candidate_denominator':den,'top15_named_candidate_votes':top15,'provisional_named_only_priority_count':len(priority),'provisional_named_only_priority_votes':cumulative,'provisional_preceding_named_votes':prior,'provisional_priority':priority,'qualified_writein_gap':'Separate official2024 qualified write-in PDF web-parser observation lists9 presidential names totaling858; original PDF GET403 here, county allocation unavailable. Named4 app/Clerk totals exclude this separate category; no allocation/zero inference.','limits':['Historical metadata asOf, lastUpdated, election date and current retrieval are separate clocks.','Root jurisdiction childLocalities6 belongs to a recent special view, not complete statewide county authority coverage; each retained baseline has159localityElections.','State ballotsCast0 and active/inactive registration0 beside populated county/totalVoters are not validated statewide zeros.','Selected state county breakdowns contain no actual precinct/polling-place rows; county-name/GUID/parent IDs not FIPS or approved geography.','Archive ZIP/direct SOS documents403 retained separately from later successful app responses.','2021 same-seat Ossoff/Perdue runoff and other-seat Warnock/Loeffler runoff are distinct;2022 general vsrunoff electorates stay separate.']}
out=ROOT/'coordinator-primary-preflight.json'
if out.exists():
 old=json.loads(out.read_text())
 if {k:v for k,v in old.items()if k!='checked_utc'}=={k:v for k,v in result.items()if k!='checked_utc'}:result['checked_utc']=old['checked_utc']
out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items()if k not in('historical_checks','provisional_priority')},indent=2))
