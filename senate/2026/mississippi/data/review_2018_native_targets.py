"""Coordinator replay of source-bound2018 targets without producer code imports."""
from pathlib import Path
from collections import Counter,defaultdict
import csv,gzip,hashlib,io,json,math
from review_historical_native_targets import solve,clip,close
DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
QA=DATA/'coordinator-qa/2018-native-targets'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))
def freeze(p):
 q=QA/(p.name+'.gz')
 if q.exists():b=gzip.decompress(q.read_bytes())
 else:b=p.read_bytes();q.write_bytes(gzip.compress(b,mtime=0))
 return b,dict(original=dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b)),lossless_copy=pin(q))
def rows(b):return list(csv.DictReader(io.StringIO(b.decode())))
def main():
 QA.mkdir(parents=True,exist_ok=True)
 sb,setting_pin=freeze(DATA/'baselines/native-2018-calculator-settings.json');settings=json.loads(sb);sp=ROOT/settings['input_witness']['path'];assert pin(sp)==settings['input_witness']and pin(sp)['sha256']=='90e14d7f6f34992c39b3d9370e954cc2d56ad7a58147103eaa0607bc139288d0'
 snap=json.loads(sp.read_bytes());docs={}
 for r in snap['pins']:
  z=(ROOT/r['stored_path']).read_bytes();b=gzip.decompress(z);assert len(z)==r['stored_bytes']and sha(z)==r['stored_sha256']and len(b)==r['original_bytes']and sha(b)==r['original_sha256'];docs[Path(r['original_path']).name]=b
 ledger=json.loads(docs['native-2018-original-readings.json']);fips={r['source_id']:r['county_fips']for r in rows(docs['native-2018-original-candidate-votes.csv'])};units={};admins={};stages={'special':{},'runoff':{}};parents={st:defaultdict(lambda:dict(pair=0,outsiders=Counter()))for st in stages};printed={st:Counter()for st in stages};source_sum={st:Counter()for st in stages}
 for s in ledger['sources']:
  sid=s['source_id'];st=s['stage'];printed[st].update(s['controls']['printed_TOTAL'])
  for p in s['pages']:
   ff={f['candidate']:f for f in p['fields']}
   for i,c in enumerate(p['columns']):
    if c['role']not in ['native','administrative']:continue
    vals={n:f['values'][i]for n,f in ff.items()};marks={n:f.get('source_marks',{}).get(str(c['source_column']))for n,f in ff.items()};unknown=any(v is None for v in vals.values());assert not unknown or set(marks.values())=={'X'};a,b=vals['Mike Espy'],vals['Cindy Hyde-Smith'];other={n:v for n,v in vals.items()if n not in ['Mike Espy','Cindy Hyde-Smith']};key=f'{fips[sid]}:{sid}:p{p["page"]}:c{c["source_column"]}'
    u=dict(key=key,sid=sid,fips=fips[sid],stage=st,raw=s['raw_sha256'],page=p['page'],col=c['source_column'],label=c['label_literal'],role=c['role'],values=vals,marks=marks,A=a,B=b,other=other,n=None if unknown else a+b,unknown=unknown)
    assert key not in units and key not in admins
    if c['role']=='administrative':assert set(vals.values())=={0};admins[key]=u
    else:
     units[key]=u;stages[st][key]=u
     if not unknown:parents[st][u['fips']]['pair']+=u['n'];parents[st][u['fips']]['outsiders'].update(other);source_sum[st].update(vals)
 assert len(units)==3545 and len(admins)==3 and sum(u['unknown']for u in units.values())==3
 assert dict(source_sum['special'])=={'Tobey Bernard Bartee':13852,'Mike Espy':386732,'Cindy Hyde-Smith':389995,'Chris McDaniel':154878}
 assert dict(source_sum['runoff'])=={'Mike Espy':420819,'Cindy Hyde-Smith':486769}
 assert {n:source_sum['special'][n]-v for n,v in printed['special'].items()}=={'Tobey Bernard Bartee':0,'Mike Espy':-10,'Cindy Hyde-Smith':0,'Chris McDaniel':0}
 cb,county_pin=freeze(DATA/'county-baselines.csv');county={r['fips']:r for r in rows(cb)};vb,candidate_pin=freeze(DATA/'baselines/candidate-votes.csv');candidates=defaultdict(dict)
 for r in rows(vb):
  k=(r['contest'],r['fips']);name=r['candidate_literal'];assert name not in candidates[k];candidates[k][name]=int(r['votes'])
 def anchor_values(anchor,f):
  vv=candidates[anchor,f]
  if anchor=='2024-president':an=next(n for n in vv if 'Kamala D. Harris' in n);bn=next(n for n in vv if 'Donald J. Trump' in n)
  elif anchor=='2024-senate':an,bn='Ty Pinkins','Roger F. Wicker'
  else:an,bn='Mike Espy','Cindy Hyde-Smith'
  assert vv[an]+vv[bn]==int(county[f][anchor+'_pair_votes']);return vv[an],vv[bn],{n:v for n,v in vv.items()if n not in [an,bn]}
 state_bytes,state_pin=freeze(DATA/'baselines/native-2018-state-targets.csv');states=rows(state_bytes);assert len(states)==180;groups={};maxshift=maxnet=0.
 for r in states:
  st=r['stage'];uu=stages[st];pp=parents[st];assert set(pp)==set(county)and len(pp)==82;scenario=r['scenario'];anchor=r['preference_anchor'];margin=float(r['target_pair_margin_pp'])/100
  if scenario=='observed2018-'+st:cw={f:float(p['pair'])for f,p in pp.items()}
  else:
   options=[('low-2022-EAC-ballots','eac_2022_F1a'),('base-2024-Senate-county-mix','2024-senate_pair_votes'),('high-2020-Senate-county-mix','2020-senate_pair_votes'),('other-midterm-stage-county-mix',('2018-runoff'if st=='special'else'2018-special')+'_pair_votes')];field=next(field for prefix,field in options if scenario.startswith(prefix));cw={f:float(c[field])for f,c in county.items()}
   if scenario.endswith('-normalized-to-stage-pair'):factor=sum(p['pair']for p in pp.values())/sum(cw.values());cw={f:v*factor for f,v in cw.items()}
  known={k:u for k,u in uu.items()if not u['unknown']};w={k:cw[u['fips']]*u['n']/pp[u['fips']]['pair']for k,u in known.items()};q={k:((u['A']/u['n'])if u['n']else .5)if anchor=='2018-'+st else anchor_values(anchor,u['fips'])[0]/sum(anchor_values(anchor,u['fips'])[:2])for k,u in known.items()};outside={f:dict(p['outsiders'])if anchor=='2018-'+st else anchor_values(anchor,f)[2]for f,p in pp.items()};stateother=Counter()
  for values in outside.values():stateother.update(values)
  T=math.fsum(w.values());base=math.fsum(w[k]*(2*q[k]-1)for k in known);target=T*margin;delta=solve(list(w.values()),list(q.values()),target);O=sum(stateother.values());D=T+O;achieved=math.fsum(w[k]*(2*clip(q[k]+delta)-1)for k in known);clipped=sum(q[k]+delta<0 or q[k]+delta>1 for k in known)
  expected={'pair_votes':T,'baseline_net':base,'target_net':target,'achieved_net':achieved,'named_other_votes_fixed':O,'conditional_named_denominator':D,'target_A_named_share':(T+target)/(2*D),'target_A_minus_B_all_named_margin_pp':100*target/D,'majority_cushion_net':target-O,'strict_majority_requires_pair_share_greater_than':D/(2*T),'strict_named_plurality_requires_pair_share_greater_than':max(.5,max(stateother.values(),default=0)/T),'source_stage_pair_votes':sum(p['pair']for p in pp.values()),'source_stage_certified_pair_votes':printed[st]['Mike Espy']+printed[st]['Cindy Hyde-Smith']}
  for field,value in expected.items():close(r[field],value)
  assert json.loads(r['named_outsiders_fixed'])==dict(stateother)and int(r['native_observations'])==len(uu)and int(r['known_numeric_native'])==len(known)and int(r['unknown_source_mark_native'])==len(uu)-len(known)and int(r['clipped_units'])==clipped and int(r['state_counties'])==82
  close(r['bounded_shift'],delta,1e-12);close(r['unbounded_shift'],(target-base)/(2*T),1e-12);maxshift=max(maxshift,abs(float(r['bounded_shift'])-delta));maxnet=max(maxnet,abs(achieved-target));assert r['group']not in groups
  groups[r['group']]=dict(stage=st,scenario=scenario,anchor=anchor,margin=margin,uu=uu,known=known,cw=cw,w=w,q=q,pp=pp,other=outside,T=T,base=base,target=target,delta=delta,D=D,clipped=clipped,seen=set(),agg=defaultdict(lambda:[0.,0.,0.,0.]))
 output_pins=[];nrows=numeric_checks=unknownrows=0
 for a in settings['compressed_unit_outputs']:
  p=ROOT/a['path'];ppin=pin(p);assert ppin['sha256']==a['sha256']and ppin['bytes']==a['bytes']<40000000;raw=gzip.decompress(p.read_bytes());assert len(raw)==a['original_csv_bytes']and sha(raw)==a['original_csv_sha256'];file_rows=0
  for r in csv.DictReader(io.StringIO(raw.decode())):
   g=groups[r['group']];u=g['uu'][r['source_key']];k=u['key'];assert k not in g['seen'];g['seen'].add(k);file_rows+=1;nrows+=1;f=u['fips']
   assert r['stage']==u['stage']==g['stage']==a['stage']and r['scenario']==g['scenario']==a['scenario']and r['preference_anchor']==g['anchor'];assert r['source_id']==u['sid']and r['source_raw_sha256']==u['raw']and r['county_fips']==f and r['label_literal']==u['label']and int(r['source_page'])==u['page']and int(r['source_column'])==u['col']and r['role']=='native';assert json.loads(r['source_named_candidates'])==u['values']and json.loads(r['source_named_outsiders'])==u['other']and json.loads(r['source_marks'])==u['marks']
   if u['unknown']:
    assert r['model_status']=='unknown_source_mark_unmodeled'and r['selected_only_status']=='unknown_source_mark';assert all(r[x]==''for x in ['A','B','pair_votes','named_candidate_votes','within_parent_known_pair_weight','county_conditional_pair_pool','expected_pair_votes','state_pair_weight','baseline_A_share','baseline_net','target_A_share','target_net','net_gain','selected_only_fixed_other_net','selected_only_required_A_share','selected_only_required_shift_pp','selected_only_clipped_display_share']);unknownrows+=1;continue
   w=g['w'][k];q=g['q'][k];shifted=clip(q+g['delta']);old=w*(2*q-1);new=w*(2*shifted-1);fixed=g['base']-old;req=(w+g['target']-fixed)/(2*w)if w else None
   expected={'A':u['A'],'B':u['B'],'pair_votes':u['n'],'named_candidate_votes':sum(u['values'].values()),'within_parent_known_pair_weight':u['n']/g['pp'][f]['pair'],'county_conditional_pair_pool':g['cw'][f],'expected_pair_votes':w,'state_pair_votes':g['T'],'state_pair_weight':w/g['T'],'baseline_A_share':q,'baseline_net':old,'target_A_share':shifted,'target_net':new,'net_gain':new-old,'net_gain_for_one_A_share_pp':.02*w,'state_baseline_net':g['base'],'state_target_net':g['target'],'selected_only_fixed_other_net':fixed,'conditional_state_named_denominator':g['D']}
   for field,value in expected.items():close(r[field],value);numeric_checks+=1
   close(float(r['uniform_bounded_share_shift_pp'])/100,g['delta'],1e-12);close(float(r['uniform_unbounded_share_shift_pp'])/100,(g['target']-g['base'])/(2*g['T']),1e-12);assert r['model_status']=='known_numeric_source'
   if req is None:assert r['selected_only_status']=='no_positive_pool'and all(r[x]==''for x in ['selected_only_required_A_share','selected_only_required_shift_pp','selected_only_clipped_display_share'])
   else:
    close(r['selected_only_required_A_share'],req);close(r['selected_only_required_shift_pp'],100*(req-q));close(r['selected_only_clipped_display_share'],clip(req));close(fixed+w*(2*req-1),g['target']);assert r['selected_only_status']==('impossible'if req>1 else'already_above_target_at_zero_share'if req<0 else'feasible')
   for i,value in enumerate([w,old,new,new-old]):g['agg'][f][i]+=value
  assert file_rows==a['rows']and pin(p)==ppin;output_pins.append(ppin)
 assert nrows==319050 and unknownrows==270 and len(output_pins)==18 and all(g['seen']==set(g['uu'])for g in groups.values())
 cr,county_contribution_pin=freeze(DATA/'baselines/native-2018-county-contributions.csv');countyrows=rows(cr);assert len(countyrows)==14760 and len({(r['group'],r['county_fips'])for r in countyrows})==14760
 for r in countyrows:
  g=groups[r['group']];f=r['county_fips'];values=g['agg'][f]
  for field,value in zip(['pair','baseline_net','target_net','net_gain'],values):close(r[field],value)
  close(r['state_pair_weight'],values[0]/g['T']);assert json.loads(r['named_outsiders_fixed'])==g['other'][f];close(r['conditional_named_denominator'],values[0]+sum(g['other'][f].values()))
 lr,local_pin=freeze(DATA/'baselines/native-2018-local-targets.csv');local=rows(lr);assert len(local)==7096;seen=set();statuses=Counter()
 for r in local:
  k=r['source_key'];m=float(r['target_pair_margin_pp'])/100;u=(units|admins)[k];assert(k,m)not in seen;seen.add((k,m));assert r['role']==u['role']and r['label_literal']==u['label']and json.loads(r['source_named_candidates'])==u['values'];statuses[r['local_status']]+=1;n=u['n']
  if n is None:assert r['local_status']=='unknown_source_mark'and r['local_target_A_share']==r['local_share_shift_pp']==r['local_net_gain']==''
  elif n==0:assert r['local_status']=='no_positive_pool'and r['local_target_A_share']==r['local_share_shift_pp']==r['local_net_gain']==''
  else:
   O=sum(u['other'].values());close(r['local_target_A_share'],(1+m)/2);close(r['local_share_shift_pp'],100*((u['B']-u['A'])/(2*n)+m/2));close(r['local_net_gain'],m*n-u['A']+u['B']);close(r['local_target_all_named_A_minus_B_margin_pp'],100*m*n/(n+O));close(r['local_majority_requires_A_pair_share_greater_than'],(n+O)/(2*n));close(r['local_majority_cushion_net'],m*n-O);close(r['local_strict_named_plurality_requires_A_pair_share_greater_than'],max(.5,max(u['other'].values(),default=0)/n));assert r['local_status']=='feasible_pair_target'
 assert statuses['unknown_source_mark']==6 and statuses['no_positive_pool']==6
 observed={}
 for st in stages:
  for margin in [0,1]:
   g=groups[f'{st}|observed2018-{st}|2018-{st}|{margin}'];other=sum(sum(v.values())for v in g['other'].values());observed[f'{st}_pair_margin{margin}']=dict(known_numeric_pair_votes=g['T'],named_outsiders=dict(source_sum[st]-(Counter({'Mike Espy':source_sum[st]['Mike Espy'],'Cindy Hyde-Smith':source_sum[st]['Cindy Hyde-Smith']}))),bounded_A_share_shift_pp=100*g['delta'],clipped_units=g['clipped'],named_majority_cushion_net=g['target']-other,named_denominator=g['D'])
 out=dict(status='pass_independent_coordinator2018_native_piecewise_source_and_contribution_review',immutable164_witness=pin(sp),frozen_settings=setting_pin,frozen_county_inputs=county_pin,frozen_candidate_inputs=candidate_pin,frozen_state_targets=state_pin,compressed_target_pins=output_pins,frozen_county_contributions=county_contribution_pin,frozen_source_local_targets=local_pin,state_groups=len(groups),unit_target_rows=nrows,unit_numeric_formula_checks=numeric_checks,unknown_unmodeled_rows=unknownrows,county_contribution_rows=len(countyrows),source_local_rows=len(local),source_local_statuses=dict(statuses),max_independent_piecewise_shift_error=maxshift,max_achieved_net_error_votes=maxnet,observed_stage_targets=observed,qualification='Coordinator saturation-event integration imports no producer calculator or validation code. All180groups/319050unitrows/14760countycontributions/7096localrows reconstruct from immutable164source fields and frozen county/candidate inputs. LiteralXunknowns remain null/unmodeled in every applicable row, not zero; three admin0rows stay separate. LefloreEspy native−TOTAL10 stays unallocated and known numerical special pair776727 differs certified776737. Bartee/McDaniel remain separately named outsiders. A pair tie or A+1margin is not a special-stage majority or regular2026plurality win; full-valid-writein scope unknown. Other-year/stage county weights/preferences are conditional over exact-stage native weights, never identity joins or candidate-effect/turnout/probability forecasts. No full-method/current-geography/native887dispatch acceptance.',formal_native887_dispatch_accepted=False,current_geography_approved=False,calibrated_probability=False)
 p=DATA/'coordinator-native-2018-target-review.json';b=(json.dumps(out,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==b
 else:p.write_bytes(b)
 print(json.dumps(dict(output=pin(p),unit_rows=nrows,numeric_checks=numeric_checks,max_shift_error=maxshift,max_net_error=maxnet,local_statuses=dict(statuses))))
if __name__=='__main__':main()
