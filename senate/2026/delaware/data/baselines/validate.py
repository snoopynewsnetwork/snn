#!/usr/bin/env python3
"""Offline independent conservation/bounds/source audit. --check-assets verifies final seal."""
from pathlib import Path
import json,csv,gzip,hashlib,collections,re,sys,math
P=Path(__file__).resolve().parent

def main():
 checks=[]
 def test(name,value,detail=None):
  assert value,(name,detail);checks.append(dict(check=name,status='pass',detail=detail))
 receipts=[]
 for n in ['shared-sources.json','current-acquisition.json','additional-acquisition.json','registration-acquisition.json','support-acquisition.json']:
  receipts+=json.loads((P/'source'/n).read_text())
 for r in receipts:
  f=P/r.get('shared_asset',r.get('asset'));z=f.read_bytes();b=gzip.decompress(z);test('source hashes '+r['id'],hashlib.sha256(z).hexdigest()==r['stored_sha256'] and hashlib.sha256(b).hexdigest()==r['raw_sha256']);test('source complete and under40MB '+r['id'],len(z)<40000000 and len(b)==r.get('raw_bytes',r.get('bytes')))
 for f in ['stable-extraction-v1.json','stable-supplement-v1.json']:
  for r in json.loads((P/'source'/f).read_text()):test('stable original-first derivative '+r['path'],hashlib.sha256((P/r['path']).read_bytes()).hexdigest()==r['sha256'])
 base=list(csv.DictReader((P/'native-baselines.csv').open()));source=json.loads((P/'extracted/contest-tables.json').read_text());groups=collections.defaultdict(list)
 for r in base:groups[(r['year'],r['office_key'],r['view'])].append(r)
 for key,rs in groups.items():
  test('unique source geography '+str(key),len({r['geo_key'] for r in rs})==len(rs))
  for r in rs:
   A,B,T,C,O=[int(r[x]) for x in ['A','B','pair_total','named_total','named_other']];test('candidate denominator identity '+str(key)+r['geo_key'],A+B==T and T+O==C and sum(v['votes'] for v in json.loads(r['candidates_json']))==C)
  state=next(r for r in base if r['year']==key[0] and r['office_key']==key[1] and r['view']=='statewide')
  test('all state votes '+str(key),sum(int(r['A']) for r in rs)==int(state['A']) and sum(int(r['B']) for r in rs)==int(state['B']) and sum(int(r['named_total']) for r in rs)==int(state['named_total']))
  test('all weights sum '+str(key),abs(sum(float(r['pair_state_weight']) for r in rs)-1)<1e-12 and abs(sum(float(r['named_state_weight']) for r in rs)-1)<1e-12)
 # Every candidate and every available method across RD/ED independently balanced to original statewide tables.
 balances=[]
 for yr,office in sorted(set((r['year'],r['office_key']) for r in source)):
  st=next(t for t in source if t['year']==yr and t['office_key']==office and t['view']=='statewide');state={rr['fields'].get('Candidate',rr['fields'].get('Candidate Name')):rr['fields'] for rr in st['rows']}
  for view in ['byrepdist','byelectiondist']:
   tabs=[t for t in source if t['year']==yr and t['office_key']==office and t['view']==view]
   for cand,sr in state.items():
    for method in ['Machine Votes','Absentee Votes','Early Voting Votes','Total Votes']:
     vals=[rr['fields'].get(method) for tb in tabs for rr in tb['rows'] if rr['fields'].get('Candidate',rr['fields'].get('Candidate Name'))==cand];target=sr.get(method)
     if target is not None:
      total=sum(int(v.replace(',','')) for v in vals if v not in [None,'']);test('RD/ED each candidate method balance '+str((yr,office,view,cand,method)),total==int(target.replace(',','')))
     else:test('absent method never zero-filled '+str((yr,office,view,cand,method)),all(v is None for v in vals))
 # Original substring positions verified, separate from common schema comparison.
 raw_by={r['id']:gzip.decompress((P/r.get('shared_asset',r.get('asset'))).read_bytes()).decode('utf-8-sig',errors='replace') for r in receipts if r['id'] in set(tb['source_id'] for tb in source)}
 for tb in source:
  t=raw_by[tb['source_id']];ss=t[tb['source_char_start']:tb['source_char_end']];test('original table bounds '+str((tb['year'],tb['view'],tb['office_key'],tb['geo_key'])),ss.startswith('<table') and ss.endswith('</table>'))
  for r in tb['rows']:test('original row bounds '+str((tb['source_id'],r['source_char_start'])),t[r['source_char_start']:r['source_char_end']].startswith('<tr') and t[r['source_char_start']:r['source_char_end']].endswith('</tr>'))
 contracts=json.loads((P/'priority-contracts.json').read_text());ranking=list(csv.DictReader((P/'geography-ranking.csv').open()))
 for c in contracts:
  rs=[r for r in ranking if int(r['year'])==c['year'] and r['office_key']==c['office_key'] and r['view']==c['view'] and r['metric']==c['metric']];order=sorted(rs,key=lambda r:int(r['rank']));T=sum(int(r['votes']) for r in order);n=c['minimum80_count'];test('exact integer80 crossing '+str((c['year'],c['office_key'],c['view'],c['metric'])),c['threshold_integer']==(4*T+4)//5 and 5*sum(int(r['votes']) for r in order[:n-1])<4*T<=5*sum(int(r['votes']) for r in order[:n]));test('full descending order '+str((c['year'],c['office_key'],c['view'],c['metric'])),[(int(r['votes']),r['geo_key']) for r in order]==sorted([(int(r['votes']),r['geo_key']) for r in order],key=lambda z:(-z[0],z[1])))
 targets=list(csv.DictReader((P/'unit-targets.csv').open()));scenarios=list(csv.DictReader((P/'state-scenarios.csv').open()));sg=collections.defaultdict(list)
 for r in targets:sg[(r['scenario'],r['target_pair_margin'])].append(r)
 for r in scenarios:
  rs=sg[(r['scenario'],r['target_pair_margin'])];T=float(r['pair_volume']);g=float(r['target_pair_margin']);test('scenario statewide target '+r['scenario']+str(g),len(rs)==int(r['units']) and abs(sum(float(x['target_net']) for x in rs)-g*T)<1e-6 and abs(sum(float(x['pair_weight']) for x in rs)-1)<1e-12)
  for x in rs:
   t=float(x['scenario_pair_volume']);q=float(x['target_A_share']) if x['target_A_share']!='' else None;test('bounded unit shares '+r['scenario']+x['geo_key'],q is None and t==0 or q is not None and 0<=q<=1)
   if t>0:
    sel=float(x['selected_only_required_share']);other=float(x['selected_other_net_fixed']);test('selected-only unbounded identity '+r['scenario']+x['geo_key'],abs(other+t*(2*sel-1)-g*T)<1e-6)
 test('synthetic calculator substantive assertions',json.loads((P/'synthetic-validation.json').read_text())['status']=='pass')
 rawpeer=json.loads((P/'peer/reconciliation-v1.json').read_text());test('reciprocal10699rawfields+positions',rawpeer['matched_source_rows']==10699 and not rawpeer['differences'] and rawpeer['unmatched_peer_rows']==0)
 test('supplemental original fields reciprocal',json.loads((P/'peer/supplement-reconciliation.json').read_text())['status']=='pass')
 test('all five native ranking orders reciprocal',json.loads((P/'peer/ranking-reconciliation.json').read_text())['status']=='pass')
 for f in [P.parent.parent/'county-partisanship.md',P/'source/SCHEMA.md']:
  test('required report/schema exists '+f.name,f.is_file())
  for link in re.findall(r'\]\(([^)]+)\)',f.read_text()):
   if '://' in link or link.startswith('#'):continue
   path=link.split('#')[0].strip('<>');target=(f.parent/path).resolve();test('relative link '+path,target.exists() or ('--check-assets' not in sys.argv and target in [(P/'validation.json').resolve(),(P/'asset-manifest.json').resolve()]))
 files=[f for f in P.rglob('*') if f.is_file()];test('every owned asset strictly below40000000',all(f.stat().st_size<40000000 for f in files));test('no caches/dependency directories',not any(d.name in ['__pycache__','node_modules','.venv','venv'] for d in P.rglob('*') if d.is_dir()))
 if '--check-assets' in sys.argv:
  mf=json.loads((P/'asset-manifest.json').read_text());test('asset manifest every owned path+external verified',all((P/r['path']).is_file() and (P/r['path']).stat().st_size==r['bytes'] and hashlib.sha256((P/r['path']).read_bytes()).hexdigest()==r['sha256'] for r in mf['assets']))
  expected={str(f.relative_to(P)) for f in P.rglob('*') if f.is_file() and f.name!='asset-manifest.json'}|{'../../county-partisanship.md','../county-baselines.csv'};test('asset inventory exhaustive owned',expected<={r['path'] for r in mf['assets']});print('Final asset seal pass;',len(checks),'checks');return
 out=dict(status='pass',check_count=len(checks),checks=checks,counts=dict(baselines=len(base),source_tables=len(source),candidate_rows=sum(len(t['rows']) for t in source),targets=len(targets),state_scenarios=len(scenarios)),external_qualifications=['No current approved November2026 geography/candidate feed mapping or measured cadence','Header and participation/November1 registered controls have separate definitions/vintages; no unexplained residual allocation','Historic blank/under/over/generic writein quantities unavailable in retained contest products','Named supplementary writeins not allocated to absent native/county rows','Not calibrated probabilities or2026 turnout forecasts'])
 (P/'validation.json').write_text(json.dumps(out,indent=2)+'\n');print('Validation pass;',len(checks),'checks')
if __name__=='__main__':main()
