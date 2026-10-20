#!/usr/bin/env python3
"""Meaningful offline source/calculator/coverage/member audit. --sealed is read only."""
import csv,gzip,hashlib,json,math,re,sys,datetime,subprocess,os
from pathlib import Path
from urllib.parse import unquote
P=Path(__file__).resolve().parent;STATE=P.parent.parent;ROOT=P.parents[4]
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def files():return sorted([f for f in P.rglob('*') if f.is_file() and f.name!='asset-manifest.json']+[STATE/'county-partisanship.md',P.parent/'county-baselines.csv'])
def main():
 checks={};findings=[]
 def check(name,value):
  checks[name]=bool(value)
  if not value:findings.append(name)
 def near(a,b,tol=1e-7):return abs(a-b)<=tol
 owned=files();check('all owned strictly below 40000000B',all(f.stat().st_size<40000000 for f in owned));check('no dependency or cache dirs',not any(f.name in ['__pycache__','node_modules','.venv'] for f in P.rglob('*')))
 pins=read(P/'source/original-pins.json');seen={};missing=[]
 for r in pins:
  if 'path' not in r:missing.append(r['receipt']['id']);continue
  f=ROOT/r['path'];stored=f.read_bytes();digest=sha(stored);check('stored source '+r['receipt']['id']+' '+r['receipt_sha256'],digest==r['stored_sha256'] and len(stored)==r['stored_bytes'] and len(stored)<40000000)
  if r['path'] not in seen:
   raw=gzip.decompress(stored) if f.suffix=='.gz' else stored;seen[r['path']]=sha(raw);check('original source '+r['path'],seen[r['path']]==r['raw_sha256'] and len(raw)==r['raw_bytes'])
  receipt=ROOT/r['receipt_path'];check('receipt '+r['receipt_sha256'],sha(receipt.read_bytes())==r['receipt_sha256'])
 check('every original receipt has available body',not missing)
 for r in read(P/'source/original-timeout-pins.json'):check('timeout original '+r['path'],sha(Path(r['path']).read_bytes())==r['sha256'])
 for folder in ['current','network-refresh','supplemental']:
  for receipt in (P/'source'/folder).glob('*.receipt.json'):
   r=read(receipt);f=receipt.with_name(receipt.name.replace('.receipt.json','.body.gz'));s=f.read_bytes();check('owned receipt '+folder+'/'+receipt.name,sha(s)==r['stored_sha256'] and sha(gzip.decompress(s))==r['raw_sha256'])
 units=read(P/'native-baselines.json.gz');keys=[(u['lane'],u['contest'],u['key']) for u in units];check('native lane/contest keys unique',len(keys)==len(set(keys)))
 scopes={(u['lane'],u['contest']) for u in units}
 for scope in scopes:
  us=[u for u in units if (u['lane'],u['contest'])==scope];check('75 native parents '+str(scope),len({u['county_fips'] for u in us})==75);check('all complete vector totals '+str(scope),all(sum(u['candidates'].values())==u['votes'] for u in us))
 inv=read(P/'source/native-inventory.json');ik=[(u['year'],u['contest_id'],u['county_id'],u['native_id']) for u in inv];check('source inventory scope keys unique',len(ik)==len(set(ik)))
 nodes=read(P/'source/contest-controls.json.gz')
 for n in nodes:
  choices=n['raw'].get('choices',n['raw'].get('Candidates',[]));cks=[c.get('choiceID',c.get('Name')) for c in choices]
  check('candidate keys '+n['source_id']+' '+n['position'],len(cks)==len(set(cks)) and n['total']==n['sum_choices'])
 cs=list(csv.DictReader((P.parent/'county-baselines.csv').open()));check('675 county baseline rows',len(cs)==675)
 for r in cs:
  v=json.loads(r['candidates_json']);check('county denominator '+r['key']+' '+r['contest'],sum(v.values())==int(r['all_candidate_votes']) and v[r['candidate_a']]+v[r['candidate_b']]==int(r['pair_votes']))
 # Registration and ballot controls are kept separate from contest and native reporting counts.
 tc=read(P/'source/turnout-controls.json');tc_results=[]
 for year in [2020,2022,2024]:
  rows=[r for r in tc if r['year']==year];state=rows[0]['publication']['turnout'];ballots=sum(r['response']['totalBallotsCast'] for r in rows);reg=sum(r['response']['registeredVoters'] for r in rows)
  check(str(year)+' all75 turnout responses',len(rows)==75 and len({r['county_id'] for r in rows})==75)
  check(str(year)+' ballot balance',ballots==state['totalBallotsCast']);check(str(year)+' registration balance',reg==state['registeredVoters']);check(str(year)+' native turnout unavailable',all(r['response']['locations']=={} for r in rows))
  tc_results.append({'year':year,'state_ballots':state['totalBallotsCast'],'county_sum_ballots':ballots,'state_registration':state['registeredVoters'],'county_sum_registration':reg,'native_available':False,'raw_state_total_precincts':state['totalPrecincts'],'counted_ballots_minus_selected_contest_not_undervotes':True})
 peer=read(P/'peer-reconciliation.json');check('peer complete raw and normalized checks',peer['status']=='pass' and peer['checks']==peer['passing'] and peer['checks']>120916 and peer['orders_compared']==20)
 orders=read(P/'independent-complete-orders.json')
 for scope,rows in orders.items():
  den=sum(r['votes'] for r in rows);ordered=sorted(rows,key=lambda r:(-r['votes'],r['key']));check('full descending '+scope,[r['key'] for r in rows]==[r['key'] for r in ordered]);check('all order keys '+scope,len({r['key'] for r in rows})==len(rows));c=0
  for i,r in enumerate(rows,1):c+=r['votes'];check('rank '+scope+' '+r['key'],r['rank']==i and c==r['cumulative_votes'] and r['share_denominator']==den)
  crossing=next((i for i,r in enumerate(rows) if 5*r['cumulative_votes']>=4*den),None);check('minimum80 '+scope,crossing is not None and (crossing==0 or 5*rows[crossing-1]['cumulative_votes']<4*den))
 check('primary priority control',peer['priority']=={'units':2841,'total':1182676,'minimum80_count':1056,'threshold':946141,'before':946007,'crossing':946377,'remainder':1785})
 calc=read(P/'calculator-validation.json');check('actual CLI and independent contributions',calc['status']=='pass' and calc['cli_cases']==60 and calc['historical_states']==58 and calc['unit_contributions_checked']==83690 and calc['max_state_net_residual']<1e-6)
 actual=read(P/'fixtures/actual-history-receipts.json');check('two actual complete historical CLI runs',actual['primary-native']['units']==2841 and actual['named-libertarian']['units']==75 and all(r['exit']==0 and r['stderr_bytes']==0 for r in actual.values()))
 source=read(P/'source/checks-summary.json');check('primary PDF all525 source fields',source['pdf_cells']==525 and source['all_exact'] and source['unmatched']==5)
 check('required publication differences',len([r for r in read(P/'source/full-api-differences.json') if not(r['year']=='2020' and 'President' in r['contest'])])==19)
 d=read(P/'source/full-api-native-discrepancies.json');check('native double evidence',len(d['doubled'])==6 and not d['other_differences'])
 # Every final output is strict JSON except intentionally invalid CLI input cases.
 for f in owned:
  if f.suffix=='.json' and not f.name.endswith('.input.json'):
   try:json.loads(f.read_text(),parse_constant=lambda v:(_ for _ in ()).throw(ValueError(v)));ok=True
   except Exception:ok=False
   check('strict JSON '+str(f.relative_to(STATE)),ok)
 # Relative report/schema/source-document links; directories are legitimate linked inventories.
 links=[];deferred=[]
 for f in owned:
  if f.suffix!='.md':continue
  for target in re.findall(r'\]\(([^)]+)\)',f.read_text()):
   if re.match(r'^[a-zA-Z]+:|^#',target):continue
   t=unquote(target.strip('<>').split('#')[0]);p=f.parent/t
   if '--write' in sys.argv and not p.exists() and p.resolve() in {(P/'validation.json').resolve(),(P/'final-seal.json').resolve(),(P/'asset-manifest.json').resolve()}:deferred.append(target)
   else:check('relative link '+str(f.relative_to(STATE))+' '+target,p.exists())
   links.append(target)
 snapshot=read(P/'history/original-first/snapshot.json');check('original-first immutable archive',sha((P/'history/original-first/core.tar.gz').read_bytes())==snapshot['archive_sha256'])
 for r in read(P/'history/peer-frozen/receipts.json')['paths']:check('frozen peer unchanged '+r['path'],sha(Path(r['path']).read_bytes())==r['sha256'])
 if '--sealed' in sys.argv:
  manifest=read(P/'asset-manifest.json');current={str(f.relative_to(STATE)):f for f in owned};entries={r['path']:r for r in manifest['assets']};check('manifest exact owned membership',set(current)==set(entries))
  for name,f in current.items():check('manifest hash '+name,name in entries and sha(f.read_bytes())==entries[name]['sha256'] and f.stat().st_size==entries[name]['bytes'])
 result={'status':'pass' if not findings else 'fail','checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':len(checks),'passed':sum(checks.values()),'failures':findings,'owned_assets':len(owned),'max_owned_bytes':max(f.stat().st_size for f in owned),'distinct_original_bodies':len(seen),'county_source_contest_rows':len(cs),'native_source_contest_rows':len(units),'all_shared_orders':len(orders),'calculator':calc,'turnout_controls':tc_results,'relative_links_checked':len(links),'preseal_audit_links_deferred_until_sealed':deferred,'qualification':'historical source numeric arithmetic audit; current ballot/geography/legal later updates/live cadence/pools/calibration not approved'}
 if '--write' in sys.argv:(P/'validation.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
 print(json.dumps(result,indent=2,allow_nan=False))
 if findings:sys.exit(1)
if __name__=='__main__':main()
