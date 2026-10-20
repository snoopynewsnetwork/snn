"""Coordinator independent source-weight/selected-only/clipped-target audit.
No producer module imports; roots use exact-rational affine breakpoint sweeps.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import defaultdict
import csv,gzip,json,math,sys
S=Path(__file__).resolve().parents[1];B=S/'data/baselines';N=0;max_shift=max_net=0.0

def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def ck(v,msg):
 global N
 N+=1
 if not v:raise AssertionError(msg)
def close(a,b,tol=2e-6):
 ck(a is not None and b is not None and math.isfinite(float(a))and math.isfinite(float(b))and abs(float(a)-float(b))<=tol,('numeric',a,b,tol))
def frac(v):return Q(str(v))
def solve(units,target):
 events=defaultdict(Q);pool=Q(0);qs=[]
 for full,w,q in units:
  pool+=w;qs.append((w,q))
  if w:events[-q]+=2*w;events[1-q]-=2*w
 last=Q(-1);value=-pool;slope=Q(0);goal=target*pool
 for x in sorted(events):
  at=value+slope*(x-last)
  if slope and value<=goal<=at:return last+(goal-value)/slope
  value=at;last=x;slope+=events[x]
 if goal==pool:return Q(1)
 raise AssertionError('no bounded affine root')
raw_native=read(B/'source/native-observations.json.gz');raw_county=read(B/'source/county-observations.json')
lookup={r['key']:r for r in raw_native+raw_county};ck(len(lookup)==6471,'all native/county source records unique')
pairs={2024:['Kamala D. Harris','Donald J. Trump'],2022:['Will Boyd','Katie Britt'],2020:['Doug Jones','Tommy Tuberville']}
for path,source in [(B/'native-baselines.json.gz',raw_native),(B/'county-baselines-complete.json.gz',raw_county)]:
 rows=read(path);ck(len(rows)==len(source),'complete baseline source universe')
 for out,src in zip(rows,source):
  counts={c['candidate_literal'].strip():c['votes']for c in src['candidate_rows']};a,b=(counts[k]for k in pairs[src['year']]);pair=a+b;full=sum(counts.values())
  ck(out['key']==src['key']and out['a_votes']==a and out['b_votes']==b and out['pair_votes']==pair and out['all_candidate_votes']==full and out['other_votes']==full-pair,'each original complete baseline balance')
  ck(out['administrative_rows']==src['administrative_rows'],'all original admin/null observations retained')
  ck({v['candidate']['id']:v['votes']for v in out['candidate_votes']}==counts,'every full candidate identity/count')
  if pair:
   close(out['a_pair_share'],Q(a,pair),1e-12);close(out['pair_margin_fraction'],Q(a-b,pair),1e-12)
  else:ck(out['a_pair_share']is None and out['pair_margin_fraction']is None,'undefined zero pair preference')
  if full:close(out['pair_participation'],Q(pair,full),1e-12)
csvrows=list(csv.DictReader((S/'data/county-baselines.csv').open(newline='')));counties={r['key']:r for r in read(B/'county-baselines-complete.json.gz')};ck(len(csvrows)==201,'all county CSV source rows')
for row in csvrows:
 src=counties[row['key']]
 for k,v in src.items():
  expected=json.dumps(v,ensure_ascii=False,allow_nan=False,separators=(',',':'))if isinstance(v,(dict,list))else ''if v is None else str(v)
  ck(row[k]==expected,'whole CSV field '+k)
settings=read(B/'scenario-settings.json');ck(len(settings)==10,'all historical preference/mix settings')
fulls={y:sum(r['reported_contest_votes']for r in raw_county if r['year']==y)for y in pairs}
summary=read(B/'state-scenarios.json');proofs=[];primary_results={}
for st in settings:
 yr=st['preference_year'];raw=raw_native if st['level']=='native'else raw_county;srcs=[r for r in raw if r['year']==yr]
 for label,target in [('tie',0),('a-plus-1-pair-margin',.01)]:
  stem=st['id']+'-'+label;inp=read(B/'scenarios'/(stem+'.input.json.gz'));out=read(B/'scenarios'/(stem+'.result.json.gz'))
  ck(inp['pair']==pairs[yr]and inp['target_pair_margin']==target and inp['mode']=='historical','named pair/target/source mode')
  ck([r['key']for r in srcs]==[r['key']for r in inp['units']]==[r['key']for r in out['units']],'entire ordered source electorate, including nonpriority')
  ids=[c['id']for c in inp['candidates']];ai,bi=[ids.index(k)for k in pairs[yr]];others=[i for i in range(len(ids))if i not in (ai,bi)];tuples=[];source_vectors=[]
  for src,unit in zip(srcs,inp['units']):
   vals={v['candidate_literal'].strip():v['votes']for v in src['candidate_rows']};parties={v['candidate_literal'].strip():v['party_literal'].strip()for v in src['candidate_rows']};v=[vals[k]for k in ids]
   ck(unit['votes']==v and len(ids)==len(vals),'every exact original candidate vector')
   for cand in inp['candidates']:ck(cand['party']==parties[cand['id']]and cand['scope']==('generic_write_in'if cand['id']=='Write-In'else'named'),'source candidate/party/scope')
   expected=sum(v)
   if st['volume_year']!=yr:
    if st['level']=='native':expected*=fulls[st['volume_year']]/fulls[yr]
    else:expected=next(r['reported_contest_votes']for r in raw_county if r['year']==st['volume_year']and r['county_fips']==src['county_fips'])
   close(unit['volume'],expected,1e-8)
   full=frac(unit['volume']);w=full*Q(v[ai]+v[bi],sum(v))if sum(v)else Q(0);q=Q(v[ai],v[ai]+v[bi])if v[ai]+v[bi]else None
   tuples.append((full,w,q));source_vectors.append(v)
  den=sum(w for f,w,q in tuples);full=sum(f for f,w,q in tuples);baseline=sum(w*(2*q-1)for f,w,q in tuples if w);goal=frac(target)*den;delta=solve(tuples,frac(target));unbounded=(goal-baseline)/(2*den)
  close(out['final_pair_denominator'],den);close(out['final_full_candidate_denominator'],full);close(out['baseline_pair_net_votes'],baseline);close(out['target_pair_net_votes'],goal);close(out['common_shift']['bounded_share_shift'],delta,1e-12);close(out['common_shift']['unbounded_share_shift'],unbounded,1e-12)
  net=Q(0);target_counts=[Q(0)for _ in ids]
  for unit,(f,w,q),v in zip(out['units'],tuples,source_vectors):
   ck(unit['counted']==[0]*len(ids)and unit['source_votes']==v,'historical counted/source vectors preserved')
   close(unit['remaining_full'],f);close(unit['pair_pool'],w);close(unit['remaining_pair_weight'],w/den,1e-12);close(unit['one_share_point_net_gain'],w/50)
   if w:
    share=max(Q(0),min(Q(1),q+delta));n=w*(2*share-1);net+=n
    close(unit['target_a_share'],share,1e-12);close(unit['target_remaining_pair_net'],n);close(unit['net_gain_to_target'],n-w*(2*q-1));close(unit['selected_only_required_a_share_raw'],(goal-(baseline-w*(2*q-1))+w)/(2*w),1e-9)
    target_counts[ai]+=w*share;target_counts[bi]+=w*(1-share)
   else:ck(unit['a_share']is None and unit['target_a_share']is None,'zero pair remains undefined')
   other=sum(v[i]for i in others)
   for i in others:target_counts[i]+=(f-w)*Q(v[i],other)if other else 0
  ck(net==goal,'exact rational target residual zero')
  for actual,expected in zip(out['target_candidates'],target_counts):close(actual['votes'],expected)
  close(sum(v['votes']for v in out['target_candidates']),full)
  rec=next(r for r in summary if r['scenario']==st['id']and r['target']==label);close(rec['bounded_shift_share_points'],100*delta,1e-10);close(rec['unbounded_shift_share_points'],100*unbounded,1e-10)
  max_shift=max(max_shift,abs(float(delta)-out['common_shift']['bounded_share_shift']));observed_net=math.fsum(u['target_remaining_pair_net']for u in out['units']);max_net=max(max_net,abs(observed_net-float(goal)))
  proofs.append({'scenario':stem,'complete_units':len(srcs),'bounded_shift':float(delta),'unbounded_shift':float(unbounded),'independent_exact_net_residual':'0','current_forecast':False})
  if st['id']=='native-2024-own-history':primary_results[label]=(inp,out,tuples,delta,goal,baseline,den)
contribs=read(B/'parent-native-contributions.json');ck(len(contribs)==134,'both targets every67 native parent contribution')
for label,(inp,out,tuples,delta,goal,base,den)in primary_results.items():
 for row in [r for r in contribs if r['target']==label]:
  selected=[i for i,u in enumerate(inp['units'])if lookup[u['key']]['county_fips']==row['county_fips']];keys=[inp['units'][i]['key']for i in selected];weight=sum(tuples[i][1]for i in selected);old=sum(tuples[i][1]*(2*tuples[i][2]-1)for i in selected if tuples[i][1]);new=sum(tuples[i][1]*(2*max(Q(0),min(Q(1),tuples[i][2]+delta))-1)for i in selected if tuples[i][1])
  ck(set(row['native_keys'])==set(keys)and row['native_count']==len(keys),'all parent native constituents')
  close(row['pair_votes'],weight);close(row['state_pair_weight'],weight/den,1e-12);close(row['baseline_net'],old);close(row['target_net'],new);close(row['net_gain'],new-old);close(row['one_share_point_net_gain'],weight/50);close(row['selected_county_only_required_a_share_raw'],(goal-(base-old)+weight)/(2*weight),1e-12)
out={'status':'pass_independent_original_weight_clipped_target_and_selected_only_review','checks':N,'native_baselines':6270,'county_baselines':201,'complete_scenarios':len(proofs),'target_units':sum(r['complete_units']for r in proofs),'parent_contributions':134,'maximum_bounded_shift_difference':max_shift,'maximum_output_net_residual_votes':max_net,'independent_method':'exact-rational piecewise affine breakpoint sweep from original-count vectors and source-verified volumes; producer solver uses floating bisection','producer_import_or_write':False,'current_or_legal_approval':False,'scenarios':proofs}
body=(json.dumps(out,indent=2)+'\n').encode();p=S/'data/coordinator-baseline-math-review.json'
if '--check'in sys.argv:ck(p.read_bytes()==body,'same frozen review')
else:p.write_bytes(body)
print(json.dumps({k:v for k,v in out.items()if k!='scenarios'}))
