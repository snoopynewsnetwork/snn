"""Independent original-preference and piecewise-linear bounded target audit."""
import collections,csv,gzip,json,math,pathlib
ROOT=pathlib.Path(__file__).resolve().parent
BASE=ROOT/'baselines'
def rows(name):
 p=BASE/name
 with (gzip.open(p,'rt') if p.suffix=='.gz' else p.open()) as f:return list(csv.DictReader(f))
def near(a,b,tol=0.000003):assert abs(float(a)-float(b))<=tol,(a,b)
def clipped(x):return min(1,max(0,x))
def solve(weights,shares,target):
 total=sum(weights);net=-total;slope=0;previous=-2.0;events=collections.defaultdict(float)
 for w,s in zip(weights,shares):
  events[-s]+=2*w;events[1-s]-=2*w
 assert -total<=target<=total
 for point,change in sorted(events.items()):
  end=net+slope*(point-previous)
  if slope>0 and net-1e-8<=target<=end+1e-8:return previous+(target-net)/slope
  net=end;slope+=change;previous=point
  if abs(net-target)<1e-8:return point
 raise AssertionError(('unreached target',target,total))
def main():
 raw=json.loads((ROOT/'coordinator-primary-table-review.json').read_text())['tables']
 tables={}
 for context,table in raw.items():
  ai=next(i for i,label in enumerate(table['headers']) if '(DEM)' in label)
  bi=next(i for i,label in enumerate(table['headers']) if '(REP)' in label)
  tables[context.replace('_','-')]={r['county_literal'].casefold():(r['votes'][ai],r['votes'][bi],sum(r['votes'])) for r in table['counties']}
 states=rows('state-scenarios.csv');county_groups=collections.defaultdict(list)
 for row in rows('county-scenarios.csv.gz'):county_groups[row['scenario_id']].append(row)
 checked=0;max_error=0;clip_groups=0
 for state in states:
  group=county_groups[state['scenario_id']];assert len(group)==67
  pref=tables[state['preference_anchor']];mix=tables[state['mix_anchor']]
  volume=float(state['all_candidate_volume']);mix_total=sum(r[2] for r in mix.values())
  weights=[];shares=[];allvolumes=[]
  for row in group:
   name=row['county'].casefold();a,b,v=pref[name];all_volume=volume*mix[name][2]/mix_total;pair=all_volume*(a+b)/v;share=a/(a+b)
   near(row['all_volume'],all_volume);near(row['pair_volume'],pair);near(row['share'],share,1e-12)
   assert int(row['historical_A'])==a and int(row['historical_B'])==b
   weights.append(pair);shares.append(share);allvolumes.append(all_volume)
  P=sum(weights);baseline=sum(t*(2*s-1) for t,s in zip(weights,shares))
  target=0.0 if state['target']=='tie' else 0.01*(P if state['target']=='Aplus1_pair_margin' else volume)
  near(state['pair_volume'],P);near(state['target_A_minus_B'],target);near(state['baseline_A_minus_B'],baseline)
  delta=solve(weights,shares,target);unbounded=(target-baseline)/(2*P)
  near(state['bounded_shift_share_pp'],delta*100,1e-9);near(state['unbounded_shift_share_pp'],unbounded*100,1e-9)
  net=0
  for row,t,s,all_v in zip(group,weights,shares,allvolumes):
   q=clipped(s+delta);m=t*(2*q-1);net+=m
   near(row['target_A_pair_share'],q,1e-10);near(row['target_net_votes'],m);near(row['gain_net_votes_per_1pp_A_share'],0.02*t)
   near(row['target_A_all_share'],t*q/all_v,1e-10)
   conditional=(target-(baseline-t*(2*s-1))+t)/(2*t)
   near(row['selected_only_unbounded_A_pair_share'],conditional,1e-8)
   near(row['selected_only_clipped_A_pair_share'],clipped(conditional),1e-10)
   checked+=1
  error=abs(net-target);max_error=max(max_error,error);assert error<0.000004
  near(state['computed_A'],(P+net)/2);near(state['computed_B'],(P-net)/2)
  near(state['weight_sum'],1,1e-12)
  if int(state['clipped_units']):clip_groups+=1
 # Independently derive original compiled native A/B from already byte-verified candidate positions.
 original={}
 with gzip.open(ROOT/'turnout/extracts/native-units.jsonl.gz','rt') as f:
  for line in f:
   r=json.loads(line);year,office=r['context'].split('_',1)
   key=(year,office,r['county_code'],r['election_number'],r['precinct_id'],r['polling_location'])
   a=sum(v['votes'] for v in r['candidate_category_rows'] if v['party']=='DEM')
   b=sum(v['votes'] for v in r['candidate_category_rows'] if v['party']=='REP')
   assert key not in original;original[key]=(a,b)
 native_states=rows('native-state-scenarios.csv');native_groups=collections.defaultdict(list)
 for row in rows('native-scenarios.csv.gz'):native_groups[row['scenario_id']].append(row)
 native_checked=0;native_clip_groups=0
 original_pair=collections.Counter()
 for key,(a,b) in original.items():original_pair[key[0]+'-'+key[1]]+=a+b
 native_volumes={'low':min(original_pair.values()),'base':original_pair['2024-senate'],'high':max(original_pair.values())}
 for state in native_states:
  group=native_groups[state['scenario_id']];context=state['context'];P=float(state['pair_volume'])
  near(P,native_volumes[state['volume_label']]);weights=[];shares=[]
  for row in group:
   key=tuple(json.loads(row['native_key']));a,b=original[key];assert key[0]+'-'+key[1]==context
   assert int(row['historical_A'])==a and int(row['historical_B'])==b
   t=(a+b)*P/original_pair[context];s=a/(a+b) if a+b else 0.5
   near(row['native_pair_volume'],t);assert row['all_valid_denominator']==''
   if a+b:near(row['baseline_share'],s,1e-12)
   else:assert row['baseline_share']==''
   weights.append(t);shares.append(s)
  target=float(state['target_net']);baseline=sum(t*(2*s-1) for t,s in zip(weights,shares))
  near(state['baseline_net'],baseline);delta=solve(weights,shares,target)
  near(state['bounded_shift_share_pp'],delta*100,1e-9)
  net=0
  for row,t,s in zip(group,weights,shares):
   q=clipped(s+delta);m=t*(2*q-1);net+=m
   near(row['target_net_votes'],m);near(row['gain_net_votes_per_1pp'],0.02*t)
   if t:
    near(row['target_share'],q,1e-10)
    conditional=(target-baseline+t*(2*s-1)+t)/(2*t)
    near(row['selected_only_unbounded_share'],conditional,1e-7)
   else:assert row['target_share']==''
   native_checked+=1
  error=abs(net-target);max_error=max(max_error,error);assert error<0.000005
  if int(state['clipped_units']):native_clip_groups+=1
 output={'status':'pass_independent_original_preference_piecewise_targets','county_state_scenarios':len(states),'county_target_rows':checked,'native_state_scenarios':len(native_states),'native_target_rows':native_checked,'county_clipping_groups':clip_groups,'native_clipping_groups':native_clip_groups,'maximum_net_error_votes':max_error,'method':'Independent source-derived shares/weights; piecewise-linear event/slope root, not worker solver imports.','scope':'Historical scenarios and fixed-other conditional arithmetic only; no current forecast/valid-writein-native allocation or physical join.'}
 (ROOT/'coordinator-target-review.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output))
if __name__=='__main__':main()
