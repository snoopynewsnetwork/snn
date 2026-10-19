"""Independent source-bound 2020 target review; no producer solver imports."""
from pathlib import Path
from collections import defaultdict,Counter
import csv,gzip,hashlib,io,json,math
DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
QA=DATA/'coordinator-qa/historical-native-targets'
NAMES=['Mike Espy','Cindy Hyde-Smith','Jimmy L. Edwards']
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))
def frozen(p):
 q=QA/(p.name+'.gz')
 if q.exists():b=gzip.decompress(q.read_bytes())
 else:b=p.read_bytes();q.write_bytes(gzip.compress(b,mtime=0))
 return b,dict(original=dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b)),lossless_copy=pin(q))
def clip(x):return min(1.,max(0.,x))
def close(a,b,tolerance=1e-6):assert abs(float(a)-b)<=tolerance,(a,b)
def solve(weights,shares,target):
 events=defaultdict(list);T=math.fsum(weights)
 for w,q in zip(weights,shares):events[-q].append(2*w);events[1-q].append(-2*w)
 x,net,slope=-1.,-T,0.
 for end,changes in sorted(events.items()):
  nextnet=net+slope*(end-x)
  if slope>0 and net<=target<=nextnet:return x+(target-net)/slope
  x,net=end,nextnet;slope+=math.fsum(changes)
 raise AssertionError('No feasible saturation segment')
def main():
 QA.mkdir(parents=True,exist_ok=True);settings_raw,settings_pin=frozen(DATA/'baselines/native-2020-calculator-settings.json');settings=json.loads(settings_raw);sp=ROOT/settings['input_witness']['path'];assert pin(sp)==settings['input_witness'];assert sha(sp.read_bytes())=='1ff6e98fd18f70ec473ce0b5adac5e082f4f1900a7d03d6090e9181150a71568';snap=json.loads(sp.read_bytes());docs={}
 for a in snap['pins']:
  z=(ROOT/a['stored_path']).read_bytes();b=gzip.decompress(z);assert len(z)==a['stored_bytes']and sha(z)==a['stored_sha256']and len(b)==a['original_bytes']and sha(b)==a['original_sha256']
  if a['original_path'].endswith('.json'):docs[Path(a['original_path']).name]=json.loads(b)
 selected={s['source_id']for s in docs['native-2020-coverage.json']['all104_publication_status']if s['selected_for_82_county_amended_where_explicit_control']};units={};admins={}
 for name in ['coahoma-2020-amendment-readings.json','native-2020-additional-readings.json']:
  for s in docs[name]['sources']:
   for p in s['pages']:
    fields={f['candidate']:f['values']for f in p['fields']}
    for i,c in enumerate(p['columns']):
     if c['role']not in ['source_native_reporting_constituent','source_administrative_reporting_column']:continue
     vals=[fields[n][i]for n in NAMES];assert all(type(v)is int and v>=0 for v in vals);key=f'{s["county_fips"]}:{s["source_id"]}:p{p["page"]}:c{c["source_column"]}';assert key not in units and key not in admins
     u=dict(key=key,sid=s['source_id'],fips=s['county_fips'],raw=s['raw_sha256'],page=p['page'],column=c['source_column'],label=c['label_literal'],A=vals[0],B=vals[1],other=vals[2],n=vals[0]+vals[1],role=c['role']);(units if c['role']=='source_native_reporting_constituent'else admins)[key]=u
 assert len(units)==2131 and len(admins)==1 and len(selected)==82
 preferred={k:u for k,u in units.items()if u['sid']in selected};assert len(preferred)==1765 and [sum(u[k]for u in preferred.values())for k in ['A','B','other']]==[578691,709511,23152]
 partitions={'preferred82':preferred}
 for sid in sorted({u['sid']for u in units.values()}-selected):
  replacement={k:u for k,u in units.items()if u['sid']==sid};fips={u['fips']for u in replacement.values()};assert len(fips)==1;partitions['replace-'+sid]={k:u for k,u in preferred.items()if u['fips']not in fips}|replacement
 assert len(partitions)==23
 county_raw,county_pin=frozen(DATA/'county-baselines.csv');cc={r['fips']:r for r in csv.DictReader(io.StringIO(county_raw.decode()))};assert len(cc)==82;metadata={r['partition']:r for r in settings['partitions']};parents={}
 for part,uu in partitions.items():
  pp=defaultdict(lambda:[0,0])
  for u in uu.values():pp[u['fips']][0]+=u['n'];pp[u['fips']][1]+=u['other']
  assert set(pp)==set(cc)and all(n>0 for n,o in pp.values());parents[part]=dict(pp);m=metadata[part];assert m['native_units']==len(uu)and m['source_ids']==sorted({u['sid']for u in uu.values()})and m['pair_votes']==sum(p[0]for p in pp.values())and m['other_votes']==sum(p[1]for p in pp.values())
 state_raw,state_pin=frozen(DATA/'baselines/native-2020-state-targets.csv');states=list(csv.DictReader(io.StringIO(state_raw.decode())));assert len(states)==134;groups={};max_shift_error=max_net_error=0.
 for r in states:
  part=r['partition'];uu=partitions[part];pp=parents[part];scenario=r['scenario'];anchor=r['preference_anchor'];margin=float(r['target_pair_margin_pp'])/100
  if scenario in ['high-observed2020-native','observed2020-source-replacement']:cw={f:float(v[0])for f,v in pp.items()}
  else:
   options=[('low-2022-EAC-ballots','eac_2022_F1a'),('base-2024-Senate-county-mix','2024-senate_pair_votes'),('midterm2018-special-county-mix','2018-special_pair_votes'),('midterm2018-runoff-county-mix','2018-runoff_pair_votes')];field=next(field for prefix,field in options if scenario.startswith(prefix));cw={f:float(c[field])for f,c in cc.items()}
   if scenario.endswith('-normalized-to-2020-pair'):factor=1288202/math.fsum(cw.values());cw={f:v*factor for f,v in cw.items()}
  w={k:cw[u['fips']]*u['n']/pp[u['fips']][0]for k,u in uu.items()};q={k:(u['A']/u['n']if u['n']else .5)if anchor=='2020-senate'else float(cc[u['fips']][anchor+'_A'])/float(cc[u['fips']][anchor+'_pair_votes'])for k,u in uu.items()};T=math.fsum(w.values());base=math.fsum(w[k]*(2*q[k]-1)for k in uu);target=margin*T;delta=solve(list(w.values()),list(q.values()),target);out={f:v[1]if anchor=='2020-senate'else int(cc[f][anchor+'_other'])for f,v in pp.items()};O=sum(out.values());D=T+O;achieved=math.fsum(w[k]*(2*clip(q[k]+delta)-1)for k in uu);clipped=sum(q[k]+delta<0 or q[k]+delta>1 for k in uu)
  for field,value in [('pair_votes',T),('baseline_net',base),('target_net',target),('achieved_net',achieved),('historical_named_other_votes_fixed',O),('conditional_named_all_candidate_denominator',D),('conditional_A_minus_B_all_candidate_margin_pp',100*target/D),('conditional_A_named_share',(T+target)/(2*D))]:close(r[field],value)
  close(r['bounded_shift'],delta,1e-12);close(r['unbounded_shift'],(target-base)/(2*T),1e-12);assert int(r['clipped_units'])==clipped and int(r['state_counties'])==82 and int(r['native_units'])==len(uu);max_shift_error=max(max_shift_error,abs(float(r['bounded_shift'])-delta));max_net_error=max(max_net_error,abs(achieved-target));assert r['group']not in groups
  groups[r['group']]=dict(part=part,scenario=scenario,anchor=anchor,margin=margin,units=uu,parents=pp,county_weights=cw,weights=w,shares=q,T=T,base=base,target=target,shift=delta,other=out,O=O,D=D,clipped=clipped,seen=set(),county=defaultdict(lambda:[0.,0.,0.,0.]))
 assert sum(g['part']=='preferred82'for g in groups.values())==90
 outputs=[];nrows=numeric_checks=0
 for a in settings['compressed_unit_outputs']:
  p=ROOT/a['path'];ppin=pin(p);assert ppin['bytes']==a['bytes']<40000000 and ppin['sha256']==a['sha256'];raw=gzip.decompress(p.read_bytes());assert len(raw)==a['original_csv_bytes']and sha(raw)==a['original_csv_sha256'];file_rows=0
  for r in csv.DictReader(io.StringIO(raw.decode())):
   g=groups[r['group']];u=g['units'][r['source_key']];k=u['key'];assert k not in g['seen'];g['seen'].add(k);f=u['fips'];w=g['weights'][k];q=g['shares'][k];shifted=clip(q+g['shift']);old=w*(2*q-1);new=w*(2*shifted-1);fixed=g['base']-old;required=(w+g['target']-fixed)/(2*w)if w else None
   assert r['partition']==g['part']==a['partition']and r['scenario']==g['scenario']==a['scenario']and r['preference_anchor']==g['anchor'];assert r['source_raw_sha256']==u['raw']and r['source_id']==u['sid']and r['county_fips']==f and r['label_literal']==u['label']and int(r['source_page'])==u['page']and int(r['source_column'])==u['column']and r['role']==u['role']
   for field,value in {'A':u['A'],'B':u['B'],'other':u['other'],'pair_votes':u['n'],'named_candidate_votes':u['n']+u['other'],'within_parent_historical_pair_weight':u['n']/g['parents'][f][0],'county_conditional_pair_pool':g['county_weights'][f],'expected_pair_votes':w,'state_pair_votes':g['T'],'state_pair_weight':w/g['T'],'baseline_A_share':q,'baseline_net':old,'target_A_share':shifted,'target_net':new,'net_gain':new-old,'net_gain_for_one_A_share_pp':.02*w,'state_baseline_net':g['base'],'state_target_net':g['target'],'selected_only_fixed_other_net':fixed,'conditional_state_named_all_candidate_denominator':g['D']}.items():close(r[field],value);numeric_checks+=1
   close(float(r['uniform_bounded_share_shift_pp'])/100,g['shift'],1e-12);close(float(r['uniform_unbounded_share_shift_pp'])/100,(g['target']-g['base'])/(2*g['T']),1e-12)
   if required is None:assert r['selected_only_required_A_share']==r['selected_only_required_shift_pp']==r['selected_only_clipped_display_share']==''and r['selected_only_status']=='no_positive_pool'
   else:
    close(r['selected_only_required_A_share'],required);close(r['selected_only_required_shift_pp'],100*(required-q));close(r['selected_only_clipped_display_share'],clip(required));close(fixed+w*(2*required-1),g['target']);assert r['selected_only_status']==('impossible'if required>1 else'already_above_target_at_zero_share'if required<0 else'feasible')
   for i,v in enumerate([w,old,new,new-old]):g['county'][f][i]+=v
   file_rows+=1;nrows+=1
  assert file_rows==a['rows']and pin(p)==ppin;outputs.append(ppin)
 assert nrows==236510 and all(g['seen']==set(g['units'])for g in groups.values())and len(outputs)==31
 cb,cpin=frozen(DATA/'baselines/native-2020-county-contributions.csv');county_rows=list(csv.DictReader(io.StringIO(cb.decode())));assert len(county_rows)==10988 and len({(r['group'],r['county_fips'])for r in county_rows})==10988
 for r in county_rows:
  g=groups[r['group']];f=r['county_fips'];values=g['county'][f]
  for field,value in zip(['pair','baseline_net','target_net','net_gain'],values):close(r[field],value)
  close(r['state_pair_weight'],values[0]/g['T']);close(r['named_other_votes_fixed'],g['other'][f]);close(r['conditional_named_denominator'],values[0]+g['other'][f])
 lb,lpin=frozen(DATA/'baselines/native-2020-local-targets.csv');local=list(csv.DictReader(io.StringIO(lb.decode())));assert len(local)==4264;seen=set();nopool=0
 for r in local:
  k=r['source_key'];m=float(r['target_pair_margin_pp'])/100;u=(units|admins)[k];assert(k,m)not in seen;seen.add((k,m));assert r['role']==u['role']and r['label_literal']==u['label']and[int(r[x])for x in['A','B','other']]==[u[x]for x in['A','B','other']]
  if u['n']:
   close(r['local_target_A_share'],(1+m)/2);close(r['local_share_shift_pp'],100*((u['B']-u['A'])/(2*u['n'])+m/2));close(r['local_net_gain'],m*u['n']-(u['A']-u['B']));close(r['local_strict_named_plurality_requires_A_pair_share_greater_than'],max(.5,u['other']/u['n']))
  else:assert r['local_status']=='no_positive_pool'and r['local_target_A_share']==r['local_share_shift_pp']=='';nopool+=1
 base=groups['preferred82|high-observed2020-native|2020-senate|0'];plus=groups['preferred82|high-observed2020-native|2020-senate|1'];assert base['clipped']==117 and plus['clipped']==124
 out=dict(status='pass_independent_source_bound_2020_native_piecewise_and_contribution_review',immutable_original104_witness=pin(sp),frozen_county_inputs=county_pin,frozen_settings=settings_pin,frozen_state_targets=state_pin,frozen_county_contributions=cpin,frozen_source_local_targets=lpin,original_compressed_target_pins=outputs,source_publications=104,alternative_native_observations=2131,preferred_native_units=1765,preferred_parent_counties=82,preferred_pair_denominator=1288202,named_Edwards_votes_separate=23152,preferred_named_denominator=1311354,whole_county_partitions=23,state_groups=134,preferred_groups=90,unit_target_rows=nrows,unit_numeric_formula_checks=numeric_checks,county_contribution_rows=len(county_rows),source_local_target_rows=len(local),zero_pair_source_local_cases=nopool,max_independent_piecewise_shift_error=max_shift_error,max_achieved_net_error_votes=max_net_error,actual2020_pair_tie_bounded_share_shift_pp=100*base['shift'],actual2020_pair_tie_clipped_units=base['clipped'],actual2020_A_plus1_bounded_share_shift_pp=100*plus['shift'],actual2020_A_plus1_clipped_units=plus['clipped'],qualification='Original immutable104 source fields independently reconstruct every partition;22 alternatives replace exactly one entire county with all82 parents retained. Coordinator saturation-event integration imports neither producer calculator nor validation code. All134 group shifts,236510 source-bound unit rows,10988 county contributions and4264 source-local rows recompute. Other-year county volume/preference anchors are conditional over2020 native weights, not a native cross-year join or candidate-effect/projection. Edwards remains separately named; generic write-ins remain unknown rather than allocated. Pair targets and conditional denominators do not establish legal2026plurality, source methods/current geography, forecast/calibrated probability or native887dispatch acceptance.',formal_native887_dispatch_accepted=False,complete_historical_method_question=False,current_geography_approved=False,real2026_forecast=False)
 p=DATA/'coordinator-historical-native-target-review.json';body=(json.dumps(out,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==body
 else:p.write_bytes(body)
 print(json.dumps(dict(output=pin(p),state_groups=134,unit_target_rows=nrows,unit_numeric_formula_checks=numeric_checks,max_shift_error=max_shift_error,max_net_error=max_net_error)))
if __name__=='__main__':main()
