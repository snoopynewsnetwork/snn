"""Queued original-source diagnostic, never an accepted worker dispatch.
Frozen individual input receipts; no appendable discovery ledger at replay.
"""
from pathlib import Path
import collections,csv,gzip,hashlib,io,json
S=Path(__file__).resolve().parents[1];D=S/'data'
def sha(b):return hashlib.sha256(b).hexdigest()
def load(r):
 z=(S/r['path']).read_bytes();b=gzip.decompress(z);assert len(z)==r['stored_bytes']and sha(z)==r['stored_sha256'];assert len(b)==r['raw_bytes']and sha(b)==r['raw_sha256'];return list(csv.reader(io.StringIO(b.decode('utf-8-sig'))))
def main():
 inputs=json.loads((D/'coordinator-native-diagnostic-originals.json').read_bytes());native=load(inputs['native']);town=load(inputs['municipal']);assert len(native[2:-1])==2394 and len(town[2:-1])==351
 assert native[0][3:]==town[0][3:]and native[-1]==town[-1];columns=native[0][3:];assert columns[-3:]==['All Others','Blanks','Total Votes Cast'];records=[];agg=collections.defaultdict(lambda:[0]*5)
 for ordinal,row in enumerate(native[2:-1],3):
  v=[int(x.replace(',',''))for x in row[3:]];assert sum(v[:-1])==v[-1];k=row[:3];assert len(v)==5
  records.append(dict(source_tuple=k,CSV_record_ordinal=ordinal,source_row_sha256=sha(json.dumps(row,ensure_ascii=False,separators=(',',':')).encode()),raw_row=row,values=v))
  for i,n in enumerate(v):agg[row[0]][i]+=n
 assert len({tuple(r['source_tuple'])for r in records})==2394
 for row in town[2:-1]:assert agg[row[0]]==[int(x.replace(',',''))for x in row[3:]]
 controls=[int(x.replace(',',''))for x in native[-1][3:]];assert [sum(r['values'][i]for r in records)for i in range(5)]==controls
 scenarios=[]
 for scope,indices in [('reported_named_plus_AllOthers',[0,1,2]),('printed_named_pair_only',[0,1]),('source_ballot_TotalVotesCast',[4])]:
  order=sorted([dict(source_tuple=r['source_tuple'],CSV_record_ordinal=r['CSV_record_ordinal'],votes=sum(r['values'][i]for i in indices))for r in records],key=lambda r:(-r['votes'],r['source_tuple'],r['CSV_record_ordinal']));den=sum(r['votes']for r in order);cum=0;n=None
  for i,r in enumerate(order,1):
   r.update(rank=i,cumulative_votes=cum+r['votes']);cum+=r['votes']
   if n is None and cum*5>=den*4:n=i
  assert order[n-2]['cumulative_votes']*5<den*4<=order[n-1]['cumulative_votes']*5
  scenarios.append(dict(scope=scope,denominator=den,top15=sum(r['votes']for r in order[:15]),minimum80_count=n,previous=order[n-2],crossing=order[n-1],remainder_votes=den-order[n-1]['cumulative_votes'],full_order=order))
 out=dict(status='pass_original_queued_diagnostic_only_not_accepted_priority',source_pins=inputs,headers=native[:2],state_control_columns=columns,state_controls=controls,native=2394,municipalities=351,all_2394_complete_original_rows=records,explicit_scope_rankings=scenarios,tie_rule='Descending scope-specific integer source votes, then exact CityTown/Ward/Pct literal tuple, then original record ordinal. Provisional presentation only; actual workers must independently reconcile canonical arrays.',no_worker_values_read=True,formal_priority_accepted=False,current_geography_approved=False,eligible_writein_scope_approved=False,qualification='AllOthers is a distinct reported aggregate, not legal/named write-in allocation. Blanks stay separate; source totals/parents do not infer physical/current/method/geographic compatibility. No current worker launched or acceptance implied.')
 p=D/'coordinator-native-priority-diagnostic.json';p.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n');assert p.stat().st_size<40000000;print(json.dumps({k:out[k]for k in ['status','native','municipalities']}));print(json.dumps([{k:s[k]for k in ['scope','denominator','top15','minimum80_count','crossing']}for s in scenarios]));print(p.stat().st_size,sha(p.read_bytes()))
if __name__=='__main__':main()
