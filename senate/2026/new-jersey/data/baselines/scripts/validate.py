#!/usr/bin/env python3
"""Offline audit of original sources, complete geographies, arithmetic and owned assets."""
from pathlib import Path
import json,gzip,hashlib,csv,re,math,sys,collections,subprocess
from extract_originals import D,STATE,S,E,COUNTIES,FIPS,CANDIDATES,sha,BY,body
from calculator import live,InputError
CHECKS=[]
def yes(label,x,detail=None):
 CHECKS.append({'check':label,'pass':bool(x),**({'detail':detail} if detail is not None else {})})
 if not x:raise AssertionError(label+(' '+str(detail) if detail is not None else ''))
def close(a,b,tol=1e-6):return math.isclose(a,b,abs_tol=tol,rel_tol=1e-12)
def j(path):return json.loads(path.read_text(),parse_constant=lambda x:(_ for _ in ()).throw(ValueError('nonfinite JSON')))
def gzj(path):return json.loads(gzip.decompress(path.read_bytes()),parse_constant=lambda x:(_ for _ in ()).throw(ValueError('nonfinite JSON')))
def finite(x):
 if type(x) is float:return math.isfinite(x)
 if isinstance(x,dict):return all(finite(v) for v in x.values())
 if isinstance(x,list):return all(finite(v) for v in x)
 return True
def owned():return [STATE/'county-partisanship.md',STATE/'data/county-baselines.csv']+sorted(p for p in D.rglob('*') if p.is_file())
def csvread(p):return list(csv.DictReader(p.open()))

def main(sealed=False):
 refs=j(S/'original-references.json');yes('417 immutable original reference entries',len(refs)==417)
 for r in refs:
  if 'inherited_receipt_path' in r:
   yes('inherited receipt exact '+r['receipt_filename'],sha((S/r['inherited_receipt_path']).read_bytes())==r['inherited_receipt_sha256'])
  if r['body_reference']:
   p=S/r['body_reference'];z=p.read_bytes();b=gzip.decompress(z) if p.suffix=='.gz' else z
   yes('original raw/stored identity '+r['receipt_filename'],sha(z)==r['stored_sha256'] and len(z)==r['stored_bytes'] and sha(b)==r['raw_sha256'] and len(b)==r['raw_bytes'] and len(z)<40000000)
 for p in S.glob('*.receipt.json'):
  r=j(p)
  if r.get('asset'):
   z=(S/r['asset']).read_bytes();b=gzip.decompress(z);yes('new source receipt/body '+r['id'],sha(z)==r['stored_sha256'] and len(z)==r['stored_bytes'] and sha(b)==r['raw_sha256'] and len(b)==r['raw_bytes'])
  else:yes('client error has no invented status '+r['id'],'client_error' in r and 'status' not in r)
 core=j(S/'pre-peer-witness.json');yes('immutable core witness',sha((S/'pre-peer-witness.json').read_bytes())=='d8a93b13b137b8336b2bb47a0ab4373aff6ca5212363dbe76dbb8711137bfc40')
 for r in core['pins']:
  z=(D/r['frozen_body']).read_bytes();b=gzip.decompress(z);yes('core frozen body '+r['path'],sha(b)==r['sha256'] and len(b)==r['bytes'] and sha(z)==r['stored_sha256']);yes('stable core current body '+r['path'],sha((D/r['path']).read_bytes())==r['sha256'])
 for r in j(S/'finer-original-extraction-witness.json')['files']:
  p=S/'finer-first-bodies'/Path(r['path']).name;yes('preserved initial finer body '+r['path'],sha(p.read_bytes())==r['sha256'] and p.stat().st_size==r['bytes'])
 native=j(E/'native-contests.json');allkeys=[]
 for scope,cs in native.items():
  yes(scope+' all21 explicit parents',[c['county'] for c in cs]==COUNTIES)
  keys=[]
  for c in cs:
   yes(scope+c['county']+' candidate field/order',[(x['name'],x['party_ballot_label']) for x in c['candidates']]==CANDIDATES[scope]);t=gzip.decompress((E/(c['source_id']+'.layout.txt.gz')).read_bytes()).decode().split('\f')
   for r in c['rows']+[c['footer']]:
    keys.append(r['key']);yes('source position/key '+r['key'],r['key']==f'{r["source_id"]}:p{r["page"]:04}:l{r["line"]:04}' and r['raw']==t[r['page']-1].splitlines()[r['line']-1]);yes('source native numeric/null vector '+r['key'],len(r['votes'])==len(CANDIDATES[scope]) and all(v is None or type(v) is int and v>=0 for v in r['votes']) and sum(v for v in r['votes'] if v is not None)==r['numeric_sum'])
   yes(scope+c['county']+' all candidate footer balances',[sum((r['votes'][i] or 0) for r in c['rows']) for i in range(len(c['candidates']))]==c['footer']['votes'])
  yes(scope+' unique positional keys',len(keys)==len(set(keys)));allkeys+=keys
 yes('global keys unique',len(allkeys)==len(set(allkeys)))
 yes('all2296 native objects',sum(len(c['rows']) for cs in native.values() for c in cs)==2296)
 rec=j(E/'candidate-reconciliation.json');yes('588 candidate county cells independently balanced',len(rec)==588 and all(r['pass'] and r['municipal_footer']==r['county_pdf_cell'] for r in rec))
 county=csvread(STATE/'data/county-baselines.csv');nat=csvread(D/'native-baselines.csv');yes('84county and2296native baseline CSV rows',len(county)==84 and len(nat)==2296)
 for r in county+nat:
  v=json.loads(r['full_candidates_json']);N=sum(x['votes'] for x in v if x['votes'] is not None);P=v[0]['votes']+v[1]['votes'];yes('CSV full candidate/denominator '+r['unit_key'],N==float(r['published_candidate_total']) and P==float(r['pair_votes']) and sum((x['votes'] or 0) for x in v[2:])==float(r['other_named']))
  if P:yes('CSV pair share '+r['unit_key'],close(float(r['A_pair_share']),v[0]['votes']/P))
 orders=j(D/'all-source-orders.json');yes('all10 source measure orders',len(orders)==10)
 for scope,cs in native.items():
  arr=[r for c in cs for r in c['rows']];expected=sorted(arr,key=lambda r:(-sum(v for v in r['votes'] if v is not None),r['key']));yes(scope+' complete source order',[r['key'] for r in orders[scope]]==[r['key'] for r in expected])
 p=j(D/'priority-set.json');expected=orders['2024-senate'];N=sum(r['volume'] for r in expected);cum=0;cross=None
 for i,r in enumerate(expected,1):
  cum+=r['volume']
  if cross is None and 5*cum>=4*N:cross=i
 yes('exact integer80 crossing233/232 and complete575',N==4031795 and cross==233 and p['threshold_integer']==3225436 and p['before_votes']==3224325 and p['crossing_votes']==3229453 and len(p['order'])==575)
 yes('priority and342 remainder exhaustive ordered partition',p['priority_keys']==[r['key'] for r in expected[:233]] and p['remainder_keys']==[r['key'] for r in expected[233:]] and len(p['remainder_keys'])==342)
 yes('priority all21 parents',set(r['county'] for r in expected[:233])==set(COUNTIES));yes('no coordinator approval inferred',p['accepted_by_coordinator'] is False)
 balls=j(E/'ballot-records.json');tc=j(E/'typed-turnout-controls.json');yes('63all-county ballot original scopes',len(balls)==63)
 for year in ['2024','2020','2022']:
  yes(year+' typed21county+state',len(tc[year])==22 and {r['county'] for r in tc[year] if r['county']}==set(COUNTIES))
  for field in ['registered_voters','ballots_cast','ballots_rejected','election_districts']:yes(year+field+' county/state sum',sum(r[field] for r in tc[year] if r['county'])==next(r[field] for r in tc[year] if not r['county']))
  for measure in ['registered_voters','ballots_cast']:
   source=[r for c in balls if str(c['year'])==year for r in c['rows'] if r[measure] is not None];yes(year+measure+' complete order', [r['key'] for r in orders[year+'-'+measure]]==[r['key'] for r in sorted(source,key=lambda r:(-r[measure],r['key']))])
 for c in balls:
  yes(c['source_id']+' unique ballot rows',len(c['rows'])==len({r['key'] for r in c['rows']}))
  for f in ['registered_voters','ballots_cast','mail_ballots','provisional_ballots','election_day_provisional','early_voting_provisional']:
   if c['footers'][0][f] is not None:yes(c['source_id']+' source footer '+f,sum(r[f] for r in c['rows'] if r[f] is not None)==c['footers'][0][f])
 gaps=j(D/'discrepancy-ledger.json');yes('Somerset420 literal unallocated',any(x['kind']=='municipal-ballot-footer_vs_state-control' and x['difference']==420 and x['county']=='Somerset' and x['allocation'] is None for x in gaps));yes('Neptune both contest scopes literal',sum(x['kind']=='literal-Neptune-candidate_vs_ballot-labels' for x in gaps)==2);yes('Clerk+61/+39 preserved',any(r.get('difference')==[61,39] and r['allocation'] is None for r in gaps))
 links=j(D/'exact-label-ballot-links.json');yes('all native ballot joins preserve gaps',len(links)==2296);yes('2024Senate144 exact-label gaps',j(D/'ballot-link-summary.json')['2024-senate']['no_exact_link']==144)
 scenarios=j(D/'state-scenarios.json');settings=j(D/'scenario-settings.json');target=csvread(D/'targets.csv');yes('13settings40states8588units',len(settings)==13 and len(scenarios)==40 and len(target)==8588)
 groups=collections.defaultdict(list)
 for r in target:groups[r['scenario'],r['level'],float(r['target_pair_margin'])].append(r)
 for st in scenarios:
  rs=groups[st['scenario'],st['level'],st['target_pair_margin']];label=st['scenario']+'/'+st['level']+'/'+str(st['target_pair_margin']);yes(label+' complete unique universe',len(rs)==st['units'] and len(rs)==len({r['unit_key'] for r in rs}) and {r['county'] for r in rs}==set(COUNTIES));yes(label+' pair/other/full volumes',close(st['pair_volume']+st['other_volume'],st['published_candidate_volume']));yes(label+' all weights',close(sum(float(r['weight']) for r in rs),1));yes(label+' target net and shift identity',close(st['actual_net'],st['target_pair_margin']*st['pair_volume']) and close(st['unbounded_shift_share_pp']/100,(st['target_net']-st['baseline_net'])/(2*st['pair_volume'])))
  yes(label+' independent summed contributions',close(sum(float(r['target_net']) for r in rs),st['target_net']) and close(sum(float(r['base_net']) for r in rs),st['baseline_net']))
  for r in rs:
   T=float(r['pair']);s=float(r['base_share']);q=float(r['share_bounded_target']);outside=float(r['other_units_fixed_net']);raw=float(r['selected_only_raw_share']) if r['selected_only_raw_share'] else None;delta=st['bounded_shift_share_pp']/100
   yes(label+r['unit_key']+' bounded share/weight/contribution/gain',0<=q<=1 and close(q,max(0,min(1,s+delta))) and close(float(r['weight']),T/st['pair_volume']) and close(float(r['target_net']),T*(2*q-1)) and close(float(r['net_gain']),2*T*(q-s)) and close(float(r['net_gain_per_share_pp']),.02*T) and close(outside,st['baseline_net']-float(r['base_net'])))
   if T:
    req=(st['target_net']-outside+T)/(2*T);status='already-secured' if req<0 else 'impossible' if req>1 else 'feasible';yes(label+r['unit_key']+' selected-only outside fixed',close(raw,req) and r['selected_only_status']==status)
   else:yes(label+r['unit_key']+' zero pool preserved',raw is None and r['selected_only_status']=='no-positive-pool')
  yes(label+' candidate A/B/other denominator',close(st['A_votes']+st['B_votes']+sum(st['full_other_votes'].values()),st['published_candidate_volume']))
 chain=j(D/'county-chains.json');h=j(D/'native-hierarchy.json');yes('all21 source chains and575full hierarchy',len(chain)==21 and [r['county'] for r in chain]==COUNTIES and len(h['all_units'])==575 and len({r['key'] for r in h['all_units']})==575 and sum(r['in_priority'] for r in h['all_units'])==233 and h['finer_layers_additive_to_main'] is False)
 b=gzj(E/'bergen-required-rows.json.gz');yes('Bergen complete3250each/142pages',collections.Counter(r['scope'] for r in b['rows'])=={'senate':3250,'president':3250} and len(b['headers'])==142)
 for scope in ['senate','president']:
  yes('Bergen '+scope+' raw row identities',len({r['key'] for r in b['rows'] if r['scope']==scope})==3250)
  fc=j(D/'finer-controls.json')['Bergen'][scope];yes('Bergen '+scope+'70municipal source summaries',fc['municipal_summary_rows']==70 and fc['suppressed_rows']==7)
  actual=next(r for r in county if r['scope']=='2024-'+scope and r['county']=='Bergen');expected={a['name']:a['votes'] for a in json.loads(actual['full_candidates_json'])};yes('Bergen '+scope+' all summary candidate controls',fc['numeric_only_candidate_sums']==expected)
 m=gzj(E/'morris-required-worksheets.json.gz');yes('Morris all4required native/statistic sheets',len(m)==4 and {r['worksheet']['name'] for r in m}=={'Table of Contents','Registered Voters','2','3'})
 sal=gzj(E/'salem-required-dom.json.gz');yes('Salem43IDs86complete tables',len(sal)==86 and len({r['native_precinct_id'] for r in sal})==43 and all({r['native_contest_id'] for r in sal if r['native_precinct_id']==u}=={'1','2'} for u in {r['native_precinct_id'] for r in sal}))
 for r in sal:yes('Salem candidate keys unique '+r['key'],len(r['candidates'])==len({c['candidate_key'] for c in r['candidates']}) and all(type(c['votes']) is int and c['votes']>=0 for c in r['candidates']))
 cur=j(D/'current-general-publication.json');yes('actual current general4field/all21 no oldIDs',len(cur['candidates'])==4 and all(len(r['county_rows'])==21 and r['live_candidate_id'] is None for r in cur['candidates']) and cur['no_primary_nominee_substitution'] and cur['no_old_feed_ID_mapping'])
 q=j(D/'quarantine.json');yes('future XML quarantined',not q['admitted'] and not q['arithmetic_input'] and q['actual_election_date_field'] is None and not q['count_supplier_verified'])
 pc=j(D/'peer-comparison.json');pf=j(D/'peer-finer-comparison.json');yes('frozen peer40921 zero',pc['checks']==40921 and pc['failed']==0);yes('frozen finer constituent comparison zero',pf['difference_count']==0)
 for cap in ['peer-capture.json','peer-finer-capture.json']:
  for r in j(D/cap)['pins']:
   p=D/r.get('captured_path',r.get('capture'));z=p.read_bytes();raw=gzip.decompress(z);yes('frozen peer capture '+str(p.name),sha(z)==r['stored_sha256'] and sha(raw)==r['raw_sha256'])
 ret=j(D/'peer-completed-return-pin.json');z=(D/ret['owned_capture']).read_bytes();yes('peer completed core-only return pin',sha(z)==ret['stored_sha256'] and sha(gzip.decompress(z))==ret['raw_sha256'])
 tests=j(D/'calculator-tests.json');yes('meaningful strict calculator tests',tests['passed']==tests['tests'] and tests['tests']>=35 and all(r['pass'] for r in tests['checks']))
 for p in sorted((D/'synthetic').glob('*.input.json')):
  x=j(p)
  try:r=live(x)
  except InputError as e:r={'error':str(e)}
  yes('synthetic exact recomputation '+p.stem,r==j(p.with_name(p.name.replace('.input.','.output.'))) and finite(r))
 rp=j(D/'reproduction.json');yes('eight original-only scripts exact deterministic rebuild',rp['pass'] and len(rp['steps'])==8 and all(s['exit']==0 for s in rp['steps']) and not rp['changed'])
 for p,hsh in rp['exact_products'].items():yes('reproduced product current '+p,sha((STATE/p).read_bytes())==hsh)
 pending=[]
 for p in [STATE/'county-partisanship.md',S/'SCHEMA.md']:
  for raw in re.findall(r'\]\(([^)]+)\)',p.read_text()):
   if raw.startswith(('https:','http:','#','mailto:')):continue
   q=(p.parent/raw.split('#')[0]).resolve()
   if not q.exists() and not sealed and q in [D/'validation.json',D/'finalseal.json',D/'asset-manifest.json']:pending.append(str(q.relative_to(STATE)));continue
   yes('relative link exists '+raw,q.exists())
 for p in owned():
  yes('owned file bound '+str(p.relative_to(STATE)),p.stat().st_size<40000000)
  yes('owned no retained cache/dependency '+str(p.relative_to(STATE)),not any(k in p.parts for k in ['__pycache__','node_modules','.venv','.cache']))
  if p.suffix=='.json':yes('strict finite JSON '+str(p.relative_to(STATE)),finite(j(p)))
 if sealed:
  mf=j(D/'asset-manifest.json');present={str(p.relative_to(STATE)):p for p in owned() if p!=D/'asset-manifest.json'};listed={r['path']:r for r in mf['files']};yes('manifest excludes only itself exact membership',set(listed)==set(present) and len(listed)==len(mf['files']))
  for path,r in listed.items():yes('manifest bytes/hash '+path,present[path].stat().st_size==r['bytes'] and sha(present[path].read_bytes())==r['sha256'])
  seal=j(D/'finalseal.json');yes('seal no current-manifest reverse pin',seal['manifest_reverse_pin'] is None and seal['validation_sha256']==sha((D/'validation.json').read_bytes()))
  yes('final report exact sealed',seal['report_sha256']==sha((STATE/'county-partisanship.md').read_bytes()))
  print(json.dumps({'sealed_pass':True,'checks':len(CHECKS),'owned_assets':len(listed)+1,'pending_links':pending}));return
 result={'pass':True,'checks':len(CHECKS),'failed':0,'scope':'complete owned original/native/candidate/turnout/scenario/calculator/reproduction/link/asset audit; manifest membership checked read-only after seal','summary':{'counties':21,'native_objects':2296,'priority_universe':575,'priority':233,'remainder':342,'candidate_county_cells':588,'state_scenarios':40,'target_rows':8588,'original_reference_entries':417,'peer_core_checks':40921,'peer_finer_checks':pf['checks'],'synthetic_tests':tests['tests']},'planned_generated_links':sorted(set(pending)),'checks_detail':CHECKS,'external_limits':['current reporting IDs/finest geometry','later roster amendments','statewide legally eligible write-in allocation','November live cadence/remainder','probability calibration'],'coordinator_acceptance':False,'collector_implemented':False,'calibrated_probability':False}
 (D/'validation.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps({'pass':True,'checks':len(CHECKS),'pending_links':pending}))
if __name__=='__main__':
 try:main('--sealed' in sys.argv)
 except Exception as e:
  if '--sealed' not in sys.argv:(D/'validation.json').write_text(json.dumps({'pass':False,'error':str(e),'checks':CHECKS},indent=2,allow_nan=False)+'\n')
  raise
