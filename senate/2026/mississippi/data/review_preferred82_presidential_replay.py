"""Check complete preferred native named-Pres coverage; report unrepresented unused fields explicitly."""
from pathlib import Path
import collections,csv,gzip,io,json,re
from review_allfield_milestone import DATA,ROOT,NAMES,load,sources,sha,pin

def main():
 _,items,baselinepin=load('82views','94576fcfa4b7b245e2d5baa9e8366e4489594804f41694ea04a9f6315e46b336');ss=sources(items);p=DATA/'baselines/source/presidential-peer-through-batch26-v3/snapshot.json';b=p.read_bytes();assert sha(b)=='19b49aa4c79b631115df62751fc0f245f52a619ab2db8e6c4affac059fc2717f';snap=json.loads(b);inputs=[];flat=[]
 for x in snap['pins']:
  if x['original_path'].endswith('.csv'):
   pp=ROOT/x['stored_path'];z=pp.read_bytes();assert sha(z)==x['stored_sha256'];raw=gzip.decompress(z);assert sha(raw)==x['original_sha256'];inputs.append(pin(pp));flat.extend(csv.DictReader(io.StringIO(raw.decode())))
 for n in range(27,34):
  pp=DATA/'coordinator-qa'/f'presidential-batch{n}-replay'/f'batch{n}-presidential-original-cells.csv.gz';inputs.append(pin(pp));flat.extend(csv.DictReader(io.StringIO(gzip.decompress(pp.read_bytes()).decode())))
 dest=DATA/'coordinator-qa/preferred82-presidential-replay';dest.mkdir(exist_ok=True);pp=dest/'native-allfield-candidate-votes.csv.gz'
 if not pp.exists():pp.write_bytes(gzip.compress((DATA/'turnout/native-allfield-candidate-votes.csv').read_bytes(),mtime=0))
 inputs.append(pin(pp));flat.extend(csv.DictReader(io.StringIO(gzip.decompress(pp.read_bytes()).decode())))
 expected={};by={};state=collections.Counter()
 for sid,s in ss.items():
  for p0 in s['pages']:
   if 'roles'not in p0:
    role_alias={'summary_TOTAL':'source_TOTAL','unused':'unused_template_column'}
    p0['roles']=[role_alias.get(c['unit_type'],'source_native_reporting_constituent')for c in p0['columns']]
   for f in p0['fields']:
    candidate=f.get('candidate',f.get('field'));assert candidate is not None
    if candidate not in NAMES[:9]:continue
    for i,v in enumerate(f['values']):expected[(sid,p0['page'],i+1,candidate)]=(v,p0['roles'][i],p0)
 actual={};roles=collections.Counter()
 for row in flat:
  if row['candidate']not in NAMES[:9]:continue
  key=(row['source_id'],int(row['source_page']),int(row['source_column']),row['candidate']);assert key in expected and key not in actual;v=row.get('votes',row.get('direct_original_value',row.get('direct_original_visual_value')));v=None if v==''else int(v);ev,role,pg=expected[key]
  assert v==ev and row['source_raw_sha256']==ss[key[0]]['raw_sha256'];assert {'native_reporting_constituent':'source_native_reporting_constituent'}.get(row['role'],row['role'])==role
  label=pg['headers'][key[2]-1]['label_literal']if'headers'in pg else pg['columns'][key[2]-1]['native_label_literal']if'columns'in pg else pg['labels_literal'][key[2]-1]if key[2]-1<len(pg['labels_literal'])else''
  assert re.sub(r'\s+','',row['label_literal'])==re.sub(r'\s+','',label);actual[key]=v;roles[role]+=1
 missing=sorted(set(expected)-set(actual));assert all(expected[k][1]=='unused_template_column'and expected[k][0]is None for k in missing)
 for sid in ss:
  sums={n:sum(v for (s,p,c,can),v in actual.items()if s==sid and can==n and expected[(s,p,c,can)][1]=='source_native_reporting_constituent')for n in NAMES[:9]};totals={n:next(v for(s,p,c,can),v in actual.items()if s==sid and can==n and expected[(s,p,c,can)][1]=='source_TOTAL')for n in NAMES[:9]};assert sums==totals;by[sid]=sums;state.update(sums)
 assert len(ss)==82 and roles['source_native_reporting_constituent']==1736*9 and roles['source_TOTAL']==82*9 and roles['parallel_native_observation']==11*9
 omitted=collections.Counter(k[0]for k in missing);assert dict(omitted)=={'sos-2024-county-perry':45,'sos-2024-county-tunica':81}
 out={'status':'pass_all82_preferred_native_nine_presidential_vectors_with_explicit_unused_scope_difference','immutable_original82_snapshot_pin':baselinepin,'older_reciprocal_through26_snapshot_pin':pin(p),'complete_independent_CSV_input_pins':inputs,'preferred_source_views':len(ss),'preferred_native_constituents':1736,'compared_source_positions':len(actual),'position_roles':dict(roles),'missing_native_TOTAL_parallel_positions':0,'unrepresented_unused_null_positions':len(missing),'unrepresented_unused_null_positions_by_source':dict(omitted),'unrepresented_source_position_keys':missing,'native_candidate_source_sums_by_source':by,'statewide_named_source_vector':dict(state),'statewide_named_source_total':sum(state.values()),'qualification':'Independent turnout original transcriptions now cover every native nine-presidential vector and printed TOTAL across all82preferred sources, plus separately nonadditive Kemper parallels. All source/hash/page/physical ordinal/value/role/whitespace-only labels match the immutable independent original82ledger. The earlier direct Perry/Tunica CSVs do not represent126unused/unprinted template fields already null in the peer. They are recorded as absent from this CSV replay, not fabricated, zero-filled or silently accepted. This is not a fresh coordinator glyph read of every cell, complete alternative-publication/historical/method coverage, approved numeric polygons or current geographic/reporting identity.','formal_dispatch_accepted':False,'current_geography_approved':False,'complete_historical_methods':False}
 p=DATA/'coordinator-preferred82-presidential-replay-review.json';b=(json.dumps(out,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==b,'Immutable preferred82review drift'
 else:p.write_bytes(b)
 print(json.dumps({'status':out['status'],'compared_positions':len(actual),'unrepresented_unused_null_positions':len(missing),'state_named_source_total':sum(state.values()),'output_pin':pin(p)}))
if __name__=='__main__':main()
