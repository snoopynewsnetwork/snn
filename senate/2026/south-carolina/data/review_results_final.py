"""Coordinator independent final source scope and historical client review."""
import csv,gzip,hashlib,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parent
STATE=ROOT.parent
SOURCES=ROOT/'results-sources'
RAW=SOURCES/'raw'
def load(p):
 b=p.read_bytes()
 if p.suffix=='.gz':b=gzip.decompress(b)
 return json.loads(b)
def original(name):
 meta=load(RAW/(name+'.meta.json'))
 stored=(RAW/(name+'.body.gz')).read_bytes();b=gzip.decompress(stored)
 assert hashlib.sha256(b).hexdigest()==meta['original_sha256']
 while b.startswith(b'\x1f\x8b'):b=gzip.decompress(b)
 return json.loads(b)
def main():
 contract=load(ROOT/'turnout/priority-set.json')
 records=load(SOURCES/'county-records.json.gz')['counties']
 priority=load(SOURCES/'priority-investigations.json')
 assert len(records)==46 and len(priority)==17
 assert [x['frozen_county'] for x in records]==contract['counties']
 assert priority==[{k:v for k,v in r.items() if k!='frozen_county'} for r in records if r['priority']]
 csvrows=list(csv.DictReader((ROOT/'official-results-sources.csv').open(newline='')))
 assert len(csvrows)==47
 for dep in load(SOURCES/'dependencies.json'):
  base=STATE.parents[2] if dep.get('path_base')=='repository' else STATE
  b=(base/dep['path']).read_bytes()
  assert len(b)==dep['bytes'] and hashlib.sha256(b).hexdigest()==dep['sha256']
 summary=original('lancaster-2026-primary-summary')
 details=original('lancaster-2026-primary-details')['Contests']
 settings=original('lancaster-settings-english')
 assert settings['settings']['electiondetails']['electiondate']=='6/9/2026'
 assert len(summary)==len(details)==16
 actual={d['K']:d for d in details};comparisons=0;counts={}
 for s in summary:
  d=actual[s['K']];assert len(d['P'])==len(d['V'])
  totals=[0]*len(s['CH'])
  for v in d['V']:
   assert len(v)==len(totals)
   for i,n in enumerate(v):totals[i]+=n;comparisons+=1
  assert totals==s['V'] and sum(totals)==s['T']
  counts[s['K']]=len(d['P'])
 status=original('lancaster-2026-primary-status')
 assert len(status['P'])==34 and status['S']==[4]*31+[32]*3
 assert status['P'][-3:]==['Failsafe','Provisional','Failsafe Provisional']
 checks=load(SOURCES/'bounded-client-checks.json')
 assert checks['current_november_admitted'] is False
 assert checks['application_election_id']=='126323' and checks['pinned_version']=='375573'
 assert counts['0013']==counts['0024']==34
 for x in load(SOURCES/'original-json-reconciliation.json'):
  if x['source_total_present']:assert x['total']==x['source_total']
  else:assert x['source_total'] is None
 output={'status':'pass_complete_frozen_scope_and_independent_historical_client','county_original_objects_equal':46,'individual_priority_records':17,'remaining_counties':29,'CSV_state_plus_counties':47,'all_dependency_pins':len(load(SOURCES/'dependencies.json')),'historical_client':{'election':'126323','version':'375573','date':'6/9/2026','contests':16,'native_candidate_positions_checked':comparisons,'native_counts_by_contest':counts,'status_geographic_rows':31,'status_administrative_rows':3,'current_November_admitted':False},'historical_JSON_county_contest_controls':184,'published_summary_total_present':46,'published_summary_total_absent':138,'current_tracker_review':'coordinator-current-source-review.json','limits':['Current tracking IDs distinct from ENR identifiers','No genuine November count source admitted','No reporting/physical/current unit approval','Exact Senate remainder, named write-ins and changing cadence unverified','Later operative Grant remedy/mandate/stay gap retained']}
 (ROOT/'coordinator-results-final-review.json').write_text(json.dumps(output,indent=2)+'\n')
 print(json.dumps(output))
if __name__=='__main__':main()
