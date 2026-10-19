#!/usr/bin/env python3
"""Frozen read-only peer comparison. Subsequent peer changes are not byte-equality claims."""
from pathlib import Path
import json,gzip,hashlib,csv,io,datetime
D=Path(__file__).resolve().parent;S=D.parent.parent;P=D.parent/'turnout';F=D/'peer-comparison/stable-v1'
def sha(b):return hashlib.sha256(b).hexdigest()
def jlines(b):return [json.loads(s)for s in gzip.decompress(b).splitlines()]
def main():
 F.mkdir(parents=True,exist_ok=True);receipt=F/'receipt.json'
 names=['data/turnout/priority-set.json','data/turnout/native-unit-order.csv','data/turnout/county-order.csv','data/county-turnout.csv','data/turnout/extracts/historical-source-rows.jsonl.gz','data/turnout/extracts/candidate-universes.json','data/turnout/extracts/candidate-universe.csv','data/turnout/extracts/2024-native-statistics.jsonl.gz','data/turnout/extracts/native-rankings.json','data/turnout/extracts/county-turnout-registration.json','data/turnout/extracts/turnout-control-positions.jsonl.gz','data/turnout/extracts/county-administrative-controls.json','data/turnout/extracts/native-coverage.json','data/turnout/source/SCHEMA.md','data/turnout/asset-manifest.json']
 if not receipt.exists():
  entries=[]
  for i,n in enumerate(names):
   b=(S/n).read_bytes();target=F/(str(i)+'.snapshot.gz');target.write_bytes(gzip.compress(b,mtime=0));entries.append(dict(peer_path=n,bytes=len(b),sha256=sha(b),snapshot=target.name,stored_bytes=target.stat().st_size,stored_sha256=sha(target.read_bytes())))
  receipt.write_text(json.dumps(dict(captured_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),peer_id='ab649b9b-13a0-445e-9af2-9b022a78404d',scope='exact selected stable peer bodies captured AFTER independent extraction; no later byte-equality inference',entries=entries),indent=2)+'\n')
 r=json.loads(receipt.read_text());lookup={e['peer_path']:e for e in r['entries']}
 def body(n):
  e=lookup[n];b=(F/e['snapshot']).read_bytes();assert sha(b)==e['stored_sha256'];b=gzip.decompress(b);assert sha(b)==e['sha256']and len(b)==e['bytes'];return b
 def peer(n):return body('data/turnout/'+n)
 own=jlines((D/'extracts/original-csv-records.jsonl.gz').read_bytes());other=jlines(peer('extracts/historical-source-rows.jsonl.gz'));assert len(own)==len(other);checks=0;gaps=[];unvalued=[]
 by={(x['year'],x['source_record']):x for x in other};assert len(by)==len(other)
 for x in own:
  o=by[(x['year'],x['record_ordinal'])]
  for a,b in [('raw_fields','raw_fields'),('source_id','source_id'),('contest_id','contest_id'),('level_literal','level_literal')]:assert x[a]==o[b];checks+=1
  if x['level_literal']=='Precinct':
   for k in ['key','county_literal','native_id_literal']:assert x[k]==o[k];checks+=1
   for k in ['method','blank','undervote','overvote','administrative_ballots','registration']:assert o[k]is None;checks+=1
 ownpages=json.loads((D/'source/historical-page-props.json').read_text());otherpages=json.loads(peer('extracts/candidate-universes.json'))
 for y in ownpages:assert ownpages[y]==otherpages[y]['page_properties'];checks+=1
 # Every candidate long row: original row index, column, party/name, IDs and flags.
 long=list(csv.DictReader(io.StringIO(gzip.decompress((D/'extracts/all-candidate-votes.csv.gz').read_bytes()).decode())));pc=list(csv.DictReader(io.StringIO(peer('extracts/candidate-universe.csv').decode())));pc={(x['year'],x['display_name']):x for x in pc}
 for x in long:
  pr=by[(int(x['year']),int(x['source_record']))];p=pc[(x['year'],x['candidate_literal'])];col=int(x['source_column']);assert int(x['votes'])==int(pr['raw_fields'][col-1]);checks+=1
  for a,b in [('candidate_in_contest_id','candidate_in_contest_id'),('candidate_id','candidate_id'),('isWriteIn_literal','app_isWriteIn'),('isMasked_literal','app_isMasked'),('party_literal','party_header')]:assert x[a]==p[b];checks+=1
 # Exact native sparse raw cell representation comparison, explicitly adapting field names only.
 stats=jlines((D/'extracts/turnout-original-cells.jsonl.gz').read_bytes());ps=jlines(peer('extracts/2024-native-statistics.jsonl.gz'));ps={x['source_row']:x for x in ps};assert len(stats)==len(ps)==3183
 for x in stats:
  p=ps[x['source_row']];assert x['county_literal']==p['county_literal']and x['native_id_literal']==p['native_id_literal'];checks+=2
  normalized={cell['attributes']['r']:dict(attributes=cell['attributes'],value=cell['raw_v'],decoded=cell['text'],formula=cell['formula'])for cell in x['raw_cells'].values()};
  for addr,cell in normalized.items():
   if addr not in p['cells']:
    assert cell['value']is None and cell['decoded']is None and cell['formula']is None;unvalued.append(dict(source_row=x['source_row'],address=addr,own_cell=cell,peer_derivative='omitted unvalued source cell'))
   else:assert cell==p['cells'][addr];checks+=4
  assert set(p['cells'])<=set(normalized)
  for col,label in zip('CDEF',['active','inactive','total','ballots']):assert x['plain_numeric'][col]==p[label]and x['annotated_inclusive'][col]==p['published_'+label];checks+=2
 ownorder=json.loads((D/'historical-orders.json').read_text());po=json.loads(peer('extracts/native-rankings.json'))
 for y,rs in ownorder.items():
  pr=po[y]['full_order'];assert len(rs)==len(pr)
  for a,b in zip(rs,pr):
   assert a['key']==b['key']and a['candidate_votes']==b['candidate_votes']and a['source_record']==b['source_record'];checks+=3
  for i in range(1,len(rs)):assert (-rs[i-1]['candidate_votes'],rs[i-1]['key'])<=(-rs[i]['candidate_votes'],rs[i]['key']);checks+=1
 owncontract=json.loads((D/'priority-contract.json').read_text());pcn=json.loads(peer('priority-set.json'));assert owncontract['ordered_keys']==[x['key']for x in pcn['full_order']];assert owncontract['priority_keys']==pcn['ordered_priority_keys'];assert owncontract['denominator']==pcn['total'];checks+=3
 for a,b in [('rank','minimum80_count'),('key','crossing_key'),('cumulative','priority_votes'),('previous','preceding_votes')]:assert owncontract['crossing'][a]==pcn[b];checks+=1
 turnout=json.loads((D/'extracts/county-turnout-registration.json').read_text());pt=json.loads(peer('extracts/county-turnout-registration.json'));assert turnout==pt;checks+=64*3*3
 # Independently compare every county candidate total, rank, source ordinal and all explicit nulls in full_order.
 nc=list(csv.DictReader(io.StringIO(peer('native-unit-order.csv').decode())));ours=list(csv.DictReader((D/'native-order.csv').open()));assert len(nc)==len(ours)
 for a,b in zip(ours,nc):
  for k in ['rank','key','county_literal','native_id_literal','candidate_votes','cumulative_votes','source_record']:assert a[k]==b[k];checks+=1
 # Preserve expected representation differences: county/state local keys vs only native canonical contract.
 gaps=['Own county keys include a final empty native component; peer county keys omit it. Exact native canonical keys all agree.','Own state key has empty county/native components; peer state key ends State. These controls are not additive native units.','Own sparse derivative retains18 actual unvalued D cells, peer valued-only derivative omits them; original workbook is identical. Details retained, no zeros invented.','Current source flags, candidates, maps and legal scope require coordinator acceptance; historical agreement grants no current join.','This comparison concerns the frozen receipt bodies only, not later peer calculator/report/manifest changes.']
 out=dict(status='pass_frozen_peer_semantic_comparison_pending_coordinator_acceptance',checks=checks,frozen_receipt='stable-v1/receipt.json',source_records=len(own),named_candidate_positions=len(long),native_records=sum(len(v)for v in ownorder.values()),full_SSR_objects_equal=True,all_valued_sparse_raw_cells_equal=True,explicit_unvalued_cell_representation_differences=unvalued,annotated_source_lanes_equal=True,all_three_full_native_orders_equal=True,all64_county_turnout_controls_equal=True,exact_priority_equal=True,representation_differences_and_gaps=gaps,current_peer_body_observations=[dict(path=e['peer_path'],frozen_sha256=e['sha256'],present_sha256=sha((S/e['peer_path']).read_bytes()),still_equal=sha((S/e['peer_path']).read_bytes())==e['sha256'])for e in r['entries']])
 (D/'peer-comparison/reconciliation.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k not in ['current_peer_body_observations','representation_differences_and_gaps']}))
if __name__=='__main__':main()
