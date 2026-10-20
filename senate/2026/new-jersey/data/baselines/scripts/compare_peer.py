#!/usr/bin/env python3
"""Read only the peer's immutable original-first witness and exact frozen bodies."""
from pathlib import Path
import json,gzip,hashlib,ast,os
from extract_originals import D,STATE,E,S,sha,save,CANDIDATES,FIPS
R=STATE/'data/turnout';W=R/'pre-peer-witness.json';EXPECTED='7e26b6b14d5f881af05800aec84beaa4f38abbeb40b034dad1b49e2a061454f1'
CAP=S/'peer-original-first';CAP.mkdir(exist_ok=True)
def load(name):return json.loads(gzip.decompress((CAP/(name.replace('/','__')+'.gz')).read_bytes()))
def capture():
 assert sha(W.read_bytes())==EXPECTED,'peer witness changed'
 w=json.loads(W.read_text());names=['data/turnout/extract/'+n+'.json' for n in ['native-rows','municipal-footers','ballot-rows','ballot-footers','state-candidate-controls','turnout-controls']]+['data/turnout/all-source-orders.json','data/turnout/priority-set.json','data/turnout/build_turnout.py','data/turnout/county-chains.json','data/turnout/discrepancy-ledger.json','data/turnout/source/SCHEMA.md']
 wanted=set(names);pins=[]
 for a in w['frozen_bodies']:
  if a['path'] not in wanted:continue
  p=STATE/a['frozen_path'];z=p.read_bytes();b=gzip.decompress(z);assert sha(b)==a['original_sha256'] and sha(z)==a['stored_sha256']
  q=CAP/(a['path'].replace('/','__')+'.gz')
  if q.exists():assert q.read_bytes()==z,'never overwrite frozen capture'
  else:q.write_bytes(z)
  pins.append({'path':a['path'],'frozen_reference':os.path.relpath(p,S),'raw_sha256':sha(b),'raw_bytes':len(b),'captured_path':str(q.relative_to(D)),'stored_sha256':sha(z),'stored_bytes':len(z)})
 assert len(pins)==len(names),(len(pins),len(names))
 if not (CAP/'peer-witness.json').exists():(CAP/'peer-witness.json').write_bytes(W.read_bytes())
 save(D/'peer-capture.json',{'peer_agent':'04473229-3e65-45b1-b628-b2fe909eaeee','witness_sha256':EXPECTED,'own_witness_sha256':sha((S/'pre-peer-witness.json').read_bytes()),'scope':'only frozen completed original-first core; no later/future final-byte claim','pins':pins})
def main():
 capture();diff=[];checks=[]
 def eq(label,a,b):
  ok=a==b;checks.append({'check':label,'pass':ok})
  if not ok:diff.append({'check':label,'own':a,'peer':b})
 own=json.loads((E/'native-contests.json').read_text());peer=load('data/turnout/extract/native-rows.json');pf=load('data/turnout/extract/municipal-footers.json');po=load('data/turnout/all-source-orders.json')
 for scope,cs in own.items():
  rows=[r for c in cs for r in c['rows']];pr={r['key']:r for r in peer[scope]};eq(scope+' full key order',[r['key'] for r in rows],[r['key'] for r in peer[scope]])
  for r in rows:
   p=pr[r['key']]
   for a,b in [('source_id','source_id'),('page','page'),('line','line'),('county','county'),('county_fips','county_fips'),('label','native_label'),('votes','values'),('raw','source_line')]:eq(r['key']+' '+a,r[a],p[b])
   eq(r['key']+' unit type',r['type']=='administrative',p['unit_type']=='administrative')
  for c,p in zip(cs,pf[scope]):
   r=c['footer']
   for a,b in [('source_id','source_id'),('page','page'),('line','line'),('county','county'),('label','native_label'),('votes','values'),('raw','source_line')]:eq(r['key']+' footer '+a,r[a],p[b])
  eq(scope+' full descending order', [r['key'] for r in sorted(rows,key=lambda r:(-r['numeric_sum'],r['key']))],[r['key'] for r in po[scope]])
 # Literal candidate definitions are parsed from peer script AST, never executed.
 t=gzip.decompress((CAP/'data__turnout__build_turnout.py.gz').read_bytes()).decode();node=next(n for n in ast.parse(t).body if isinstance(n,ast.Assign) and any(isinstance(k,ast.Name) and k.id=='CANDS' for k in n.targets));eq('candidate full field/order/party',CANDIDATES,ast.literal_eval(node.value))
 controls=json.loads((E/'county-candidate-controls.json').read_text());pc=load('data/turnout/extract/state-candidate-controls.json')
 for scope,cs in controls.items():
  for c,p in zip(cs,pc[scope]):
   text=gzip.decompress((E/(c['source_id']+'.layout.txt.gz')).read_bytes()).decode().split('\f')[c['page']-1]
   eq(scope+f' page{c["page"]} full literal header/page',text,p['raw_page_text'])
   eq(scope+f' page{c["page"]} state total',c['footer']['votes'],p['published_total'])
   eq(scope+f' page{c["page"]} county candidate cells',[(r['county'],r['votes'],r['raw']) for r in c['counties']],[(r['county'],r['votes'],r['source_line']) for r in p['county_cells']])
 balls=json.loads((E/'ballot-records.json').read_text());pb=load('data/turnout/extract/ballot-rows.json');pbf=load('data/turnout/extract/ballot-footers.json')
 fieldmap={'registered_voters':'registered_voters','ballots_cast':'ballots_cast','mail_ballots':'vote_by_mail_ballots_cast','provisional_ballots':'provisional_ballots_cast','election_day_provisional':'election_day_provisional_ballots_cast','early_voting_provisional':'early_voting_provisional_ballots_cast','tokens':'tokens','raw':'source_line','label':'native_label','key':'key'}
 for year in ['2024','2020','2022']:
  cs=[c for c in balls if str(c['year'])==year]
  for kind,pdict in [('rows',pb),('footers',pbf)]:
   rows=[r for c in cs for r in c[kind]];pr={r['key']:r for r in pdict[year]};eq(year+' ballot '+kind+' key order',[r['key'] for r in rows],list(pr))
   for r in rows:
    if r['key'] not in pr:continue
    for a,b in fieldmap.items():eq(r['key']+' '+a,r[a],pr[r['key']][b])
    pct=float(r['published_percent'].rstrip('%')) if r['published_percent'] is not None else None;eq(r['key']+' percent',pct,pr[r['key']]['published_percent'])
  for metric in ['ballots_cast','registered_voters']:
   rows=[r for c in cs for r in c['rows'] if r[metric] is not None];eq(year+' '+metric+' full order',[r['key'] for r in sorted(rows,key=lambda r:(-r[metric],r['key']))],[r['key'] for r in po[year+'-'+metric]])
 tc=json.loads((E/'turnout-controls.json').read_text());pt=load('data/turnout/extract/turnout-controls.json')
 for sid,c in tc.items():
  year='2024' if '2024' in sid else '2022' if '2022' in sid else '2020';eq(year+' county turnout all raw rows',[r['raw'] for r in c['rows'] if len(r['tokens'])==5],[r['source_line'] for r in pt[year]])
 p=load('data/turnout/priority-set.json');q=json.loads((D/'priority-set.json').read_text());eq('complete priority order',[r['key'] for r in q['order']],p['complete_ordered_keys']);eq('exact minimum80 keys',q['priority_keys'],p['ordered_priority_keys']);eq('full21 parents',sorted(set(r['county'] for r in q['order'])),sorted(c['county'] for c in p['county_coverage']))
 save(D/'peer-comparison.json',{'scope':'frozen original-first only; later finer/report/scenario/final artifacts outside equality claim','checks':len(checks),'passed':sum(x['pass'] for x in checks),'failed':sum(not x['pass'] for x in checks),'differences':diff,'schema_distinctions':['own grouped by county; peer flat per scope','own semantic type municipal-labelled; peer municipality, identical admin distinction','own published percent string retains percent sign; peer numeric, compared after explicit conversion','own shared source IDs omit shared- prefix; underlying raw page and cells compared exactly','own native cells retain raw char spans; peer sparse exception evidence uses explicit checked cells','No frozen peer finer/source chains incorporated into own arithmetic; retained for read-only provenance/coverage inspection'], 'coordinator_priority_acceptance':False});print(len(checks),len(diff));print(json.dumps(diff[:5])[:5000])
if __name__=='__main__':main()
