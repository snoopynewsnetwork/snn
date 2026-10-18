"""Read-only audit against actual turnout peer's stable schema and artifacts."""
import json,hashlib
from extract import H,S,readcsv,dump
P=H.parent/'turnout'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def compare_rows(own,peer,keys):
 a={tuple(r[k] for k in keys):r for r in own};b={tuple(r[k] for k in keys):r for r in peer};assert len(a)==len(own) and len(b)==len(peer)
 diffs=[];fields=sorted(set(own[0])&set(peer[0]));n=0
 for key in sorted(a.keys()&b.keys()):
  for f in fields:
   n+=1
   if str(a[key][f])!=str(b[key][f]):diffs.append(dict(key=key,field=f,own=a[key][f],peer=b[key][f]))
 return dict(own_rows=len(own),peer_rows=len(peer),keys=keys,compared_fields=fields,compared_cells=n,own_only_keys=sorted(a.keys()-b.keys()),peer_only_keys=sorted(b.keys()-a.keys()),differences=diffs,own_only_fields=sorted(set(own[0])-set(peer[0])),peer_only_fields=sorted(set(peer[0])-set(own[0])))
def main():
 before={str(p):sha(p) for p in P.rglob('*') if p.is_file() and p.name!='peer-reconciliation.json'}
 out={'peer_id':'a2143988-db08-4b96-a032-b31b5401db97','peer_files':[],'tables':{}}
 for y in [2024,2022,2020]:
  for level,op,pp,keys in [('native',H/f'native-{y}.csv.gz',P/f'native-{y}.csv.gz',['native_key']),('county',H/f'county-controls-{y}.csv',P/f'county-controls-{y}.csv',['county_fips']),('municipal',H/f'municipal-controls-{y}.csv.gz',P/f'municipal-controls-{y}.csv',['county_fips','MCDNAME'])]:
   out['tables'][f'{y}-{level}']=compare_rows(readcsv(op),readcsv(pp),keys);out['peer_files'].append(dict(path=str(pp.relative_to(H.parent)),bytes=pp.stat().st_size,sha256=sha(pp)))
 own=json.loads((S/'workbook-context.json').read_text());peer=json.loads((P/'source/workbook-context.json').read_text());out['column_map_equal']={y:own[y]['columns']==peer[y]['columns'] for y in own}
 # Compare raw non-native source values by exact cell address and row, despite different column-key serialization.
 md=[];cells=0;out['metadata_own_only_sheets']={y:sorted(set(own[y]['metadata'])-set(peer[y]['metadata'])) for y in own}
 for y in own:
  for sheet,a in own[y]['metadata'].items():
   if sheet not in peer[y]['metadata']:continue
   b=peer[y]['metadata'][sheet];br={r['source_row']:r for r in b['rows']}
   for r in a['rows']:
    rr=br[r['source_row']]
    for address,v in r['cells'].items():
     col=''.join(t for t in address if t.isalpha());bv=rr['cells'][col];cells+=1
     if any(v[k]!=bv.get(k) for k in ['value','type','formula']):md.append(dict(year=y,sheet=sheet,cell=address,own=v,peer=bv))
 out['metadata_cells_compared']=cells;out['metadata_differences']=md
 o=json.loads((H/'priority-contract.json').read_text());p=json.loads((P/'priority-set.json').read_text());out['county_priority']={
 'full_order_equal':o['2024-county']['order']==p['complete_ordered_county_keys'],
 'priority_order_equal':o['2024-county']['priority_keys']==p['ordered_priority_keys'],
 'controls_equal':o['2024-county']['total']==p['statewide_candidate_votes'] and o['2024-county']['top15']==p['top15']['top15_votes'] and all(o['2024-county'][a]==p['minimum80'][b] for a,b in [('minimum80_count','minimum80_count'),('minimum80_votes','minimum80_votes'),('previous_votes','previous_votes'),('crossing_key','crossing_key'),('outside_votes','remainder_votes')])}
 for level in ['native','municipal']:
  op=H/f'{level}-2024-ranked.csv.gz'
  if not op.exists():continue
  pp=P/f'{level}-2024-ranked.csv.gz'
  if pp.exists():
   a=readcsv(op);b=readcsv(pp);out[level+'_ranking']=dict(peer_fields=list(b[0]),own_rows=len(a),peer_rows=len(b))
   key='native_key' if level=='native' else 'derived_key'
   out[level+'_ranking']['full_order_equal']=[r['unit_key'] for r in a]==[r.get(key,r.get('unit_key')) for r in b]
 # Audit every peer priority constituent, retaining all source methods and identities from native audits above.
 constituents=[]
 native={y:{r['native_key']:r for r in readcsv(H/f'native-{y}.csv.gz')} for y in [2024,2022,2020]}
 for county in p['county_order']:
  for sy,rows in county['native_constituents'].items():
   for r in rows:
    a=native[int(sy)][r['native_key']]
    for f in ['source_id','source_sheet','source_row','VTDID','PCTCODE','PCTNAME','MCDNAME','WARD','MAILBALLOT']:
     if r[f]!=a[f]:constituents.append(dict(key=r['native_key'],field=f,own=a[f],peer=r[f]))
 out['priority_constituent_differences']=constituents
 out['all_year_orders']={}
 for y,prefix in [(2024,'USSEN'),(2022,'MNGOV'),(2020,'USSEN')]:
  for level,path,key in [('native',P/f'native-{y}.csv.gz','native_key'),('county',P/f'county-controls-{y}.csv','county_key')]:
   peer_sorted=sorted(readcsv(path),key=lambda r:(-int(r[prefix+'TOTAL']),r[key]));out['all_year_orders'][f'{y}-{level}']=[r['unit_key'] for r in readcsv(H/f'{level}-{y}-ranked.csv.gz')]==[r[key] for r in peer_sorted]
 sensitivity=json.loads((P/'sensitivity.json').read_text());out['turnout_sensitivity_contracts']={}
 for y,prefix in [(2024,'USSEN'),(2022,'MNGOV'),(2020,'USSEN')]:
  a=o[f'{y}-county'];b=sensitivity[f'{y}_{prefix}'];out['turnout_sensitivity_contracts'][str(y)]=a['order']==[r['key'] for r in b['order']] and a['total']==b['denominator'] and a['minimum80_votes']==b['minimum80_votes'] and a['previous_votes']==b['previous_votes'] and a['priority_keys']==b['priority_keys']
 out['peer_files_unchanged_during_audit']=all(sha(__import__('pathlib').Path(p))==v for p,v in before.items())
 out['peer_priority_sha256']=sha(P/'priority-set.json')
 out['status']='pass' if all(not x['differences'] and not x['own_only_keys'] and not x['peer_only_keys'] for x in out['tables'].values()) and not md and all(out['column_map_equal'].values()) and all(out['county_priority'].values()) and not constituents and all(out['all_year_orders'].values()) and all(out['turnout_sensitivity_contracts'].values()) and out['peer_files_unchanged_during_audit'] and all(out[k].get('full_order_equal',True) for k in ['native_ranking','municipal_ranking'] if k in out) else 'differences'
 out['acceptance']='Peer arithmetic/schema audit only. Coordinator alone accepts historical dispatch; no current legal geographic approval.'
 dump(H/'peer-reconciliation.json',out)
 print(json.dumps({k:v for k,v in out.items() if k not in ['tables','peer_files']},indent=2));print('shared cells',sum(x['compared_cells'] for x in out['tables'].values()))
if __name__=='__main__':main()
