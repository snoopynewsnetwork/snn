"""Independent coordinator original-weight/complete-model/clipped-root review.
No producer import; exact-rational affine breakpoint sweep versus bisection.
"""
from pathlib import Path
from collections import defaultdict,Counter
from fractions import Fraction as Q
import csv,gzip,json,math,sys
S=Path(__file__).resolve().parents[1];B=S/'data/baselines';N=0;max_shift=max_net=0.0

def ck(v,msg):
 global N
 N+=1
 if not v:raise AssertionError(msg)
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def close(a,b,tol=2e-6):ck(a is not None and b is not None and math.isfinite(float(a))and math.isfinite(float(b))and abs(float(a)-float(b))<=tol,('numeric',a,b,tol))
def frac(v):return Q(str(v))
def root(units,goal):
 events=defaultdict(Q);pool=Q(0)
 for w,q in units:
  pool+=w
  if w:events[-q]+=2*w;events[1-q]-=2*w
 last=Q(-1);value=-pool;slope=Q(0)
 for x in sorted(events):
  at=value+slope*(x-last)
  if slope and value<=goal<=at:return last+(goal-value)/slope
  value=at;last=x;slope+=events[x]
 if goal==pool:return Q(1)
 raise AssertionError('no feasible piecewise root')
source=read(B/'native-baselines.json.gz');native_scopes=defaultdict(list);county_scopes=defaultdict(list);county_index={};native_index={}
for u in source:
 scope=(u['lane'],u['contest']);native_scopes[scope].append(u);native_index[scope,u['key']]=u;key=f'AR:{u["lane"]}-county:{u["county_fips"]}';k=scope+(key,)
 if k not in county_index:
  c={'key':key,'county_fips':u['county_fips'],'votes':0,'candidates':Counter(),'children':[]};county_index[k]=c;county_scopes[scope].append(c)
 c=county_index[k];c['candidates'].update(u['candidates']);c['votes']+=u['votes'];c['children'].append(u['key'])
county_csv=list(csv.DictReader((S/'data/county-baselines.csv').open(newline='')));ck(len(county_csv)==len(county_index)==675,'complete derived county/source/contest universes')
for r in county_csv:
 c=county_index[r['lane'],r['contest'],r['key']];ck(json.loads(r['candidates_json'])==dict(c['candidates'])and json.loads(r['source_units_json'])==c['children'],'every county candidate/vector/constituent list derives original native records')
 a=c['candidates'][r['candidate_a']];b=c['candidates'][r['candidate_b']];ck(int(r['a_votes'])==a and int(r['b_votes'])==b and int(r['pair_votes'])==a+b and int(r['all_candidate_votes'])==c['votes']and int(r['other_votes'])==c['votes']-a-b,'every county baseline pair/other balance')
 if r['year']=='2020'and r['contest']=='U.S. Senate':ck(r['candidate_a']=='Ricky Dale Harrington Jr.','named Libertarian scenario never fabricated Democrat')
volumes={scope:sum(r['votes']for r in rows)for scope,rows in county_scopes.items()};base=('2024-xlsx','U.S. President');primary=native_scopes[base];primary_county=county_scopes[base]
state_rows=list(csv.DictReader((B/'state-scenarios.csv').open(newline='')));states={(r['scenario'],r['target_pair_margin']):r for r in state_rows};ck(len(states)==len(state_rows)==58,'all58state target controls')
unit_rows=defaultdict(list)
for r in csv.DictReader((B/'unit-targets.csv').open(newline='')):unit_rows[r['scenario'],r['target_pair_margin']].append(r)
proof=[];target_count=0
for path in sorted((B/'scenarios').glob('*.input.json')):
 name=path.name.removesuffix('.input.json');d=read(path);A,Bname=d['pair']
 if name.endswith('-own-history'):
  lane,contest,level,_=d['source_scope'].split('; ');scope=(lane,contest);source_rows=native_scopes[scope]if level=='native'else county_scopes[scope];expected_vol={r['key']:r['votes']for r in source_rows}
 elif 'named-preferences-2024-volume-county'in name:
  yr=name[:4];scope=(yr+'-api','U.S. Senate');source_rows=county_scopes[scope];byf={r['county_fips']:r['votes']for r in primary_county};expected_vol={r['key']:byf[r['county_fips']]for r in source_rows}
 elif name.startswith('2024-preference-'):
  source_rows=primary_county;scope=base;mix=('2022-api','U.S. Senate')if'low'in name else('2020-api','U.S. President, Vice President')if'high'in name else base
  byf={r['county_fips']:r['votes']for r in county_scopes[mix]};expected_vol={r['key']:byf[r['county_fips']]for r in source_rows}
 elif name.endswith('-state-total'):
  source_rows=primary;scope=base;mix=('2022-api','U.S. Senate')if'low'in name else('2020-api','U.S. President, Vice President');expected_vol={r['key']:r['votes']*volumes[mix]/volumes[base]for r in source_rows}
 else:
  ck(name.startswith('2024-native-')and name.endswith('-mix'),'declared implemented native method mix');method=name.removeprefix('2024-native-').removesuffix('-mix');source_rows=primary;scope=base;expected_vol={r['key']:sum(r['methods'][method].values())for r in source_rows}
 ck([r['key']for r in d['units']]==[r['key']for r in source_rows],'all complete source units in declared order, including nonpriority')
 if scope[0].startswith('2020')and scope[1]=='U.S. Senate':ck(A=='Ricky Dale Harrington Jr.'and Bname=='Senator Tom Cotton','actual named opposition pair scope')
 tuples=[]
 for u,src in zip(d['units'],source_rows):
  cv=src['candidates'];pair=cv[A]+cv[Bname];full=sum(cv.values());q=Q(cv[A],pair)if pair else None
  ck(u['counted']=={c:0 for c in cv},'all historical counted fixed zero for complete supplied candidate field');close(u['remaining'],expected_vol[src['key']],1e-8);close(u['pair_participation'],Q(pair,full)if full else 1,1e-12)
  if pair:close(u['a_share'],q,1e-12)
  else:ck(u['a_share']is None,'zero pair preference remains undefined')
  other=full-pair
  for k,v in u['other_allocation'].items():
   if other:close(v,Q(cv[k],other),1e-12)
  w=frac(u['remaining'])*frac(u['pair_participation']);tuples.append((frac(u['remaining']),w,frac(u['a_share'])if u['a_share']is not None else None))
 F=sum(w for f,w,q in tuples);allfull=sum(f for f,w,q in tuples);baseline=sum(w*(2*q-1)for f,w,q in tuples if w)
 for target in ['0','0.01']:
  st=states[name,target];rows=unit_rows[name,target];ck(len(rows)==len(tuples)and[r['key']for r in rows]==[r['key']for r in d['units']],'all complete target contribution rows')
  goal=frac(target)*F;delta=root([(w,q)for f,w,q in tuples],goal);unbounded=(goal-baseline)/(2*F)
  close(st['pair_total'],F);close(st['all_candidate_total'],allfull);close(st['baseline_net'],baseline);close(st['baseline_pair_margin'],baseline/F,1e-12);close(st['bounded_share_shift'],delta,1e-12);close(st['unbounded_share_shift'],unbounded,1e-12);close(st['target_net'],goal)
  net=Q(0);observed=[];clip=0
  for row,u,(f,w,q)in zip(rows,d['units'],tuples):
   close(row['pair_votes'],w);close(row['all_candidate_volume'],f);close(row['state_pair_weight'],w/F,1e-12);close(row['state_all_candidate_weight'],f/allfull,1e-12);close(row['net_per_1_share_pp'],w/50)
   if w:
    share=max(Q(0),min(Q(1),q+delta));n=w*(2*share-1);old=w*(2*q-1);net+=n;required=(goal-(baseline-old)+w)/(2*w)
    close(row['baseline_a_share'],q,1e-12);close(row['baseline_net'],old);close(row['target_a_share'],share,1e-12);close(row['target_pair_margin_unit'],2*share-1,1e-12);close(row['share_shift'],share-q,1e-12);close(row['target_net'],n);close(row['net_gain'],n-old);close(row['selected_only_required_raw'],required,1e-8);close(row['selected_only_required_clipped'],max(Q(0),min(Q(1),required)),1e-12)
    ck(row['selected_only_status']==('secured'if required<0 else'impossible'if required>1 else'feasible'),'raw selected-only requirement classification')
    clip+=not(0<=u['a_share']+float(st['bounded_share_shift'])<=1)
   else:ck(row['baseline_a_share']==''and row['target_a_share']==''and row['selected_only_required_raw']==''and row['selected_only_status']=='no-positive-pool','zero pair target undefined, not neutral')
   observed.append(float(row['target_net']))
  ck(net==goal,'exact rational root residual0 across all nonpriority contributions');ck(int(st['clipped_units'])==clip,'all actual clipped source units')
  max_shift=max(max_shift,abs(float(delta)-float(st['bounded_share_shift'])));max_net=max(max_net,abs(math.fsum(observed)-float(goal)));target_count+=len(rows)
  proof.append({'scenario':name,'target':target,'units':len(rows),'source_scope':d['source_scope'],'bounded_shift':float(delta),'unbounded_shift':float(unbounded),'exact_net_residual':'0','clipped_units':clip})
ck(len(proof)==58 and target_count==83690,'all29 source models/all83690target rows')
out={'status':'pass_independent_source_weight_piecewise_clipped_historical_target_review','checks':N,'source_models':29,'state_targets':58,'complete_unit_targets':target_count,'all_county_source_contest_rows':675,'maximum_shift_difference':max_shift,'maximum_output_net_residual_votes':max_net,'method':'exact-rational affine breakpoint sweep from source-verified inputs, distinct from producer bisection','producer_import_or_write':False,'native_crossyear_join_or_current_forecast':False,'proofs':proof}
body=(json.dumps(out,indent=2)+'\n').encode();p=S/'data/coordinator-baseline-math-review.json'
if '--check'in sys.argv:ck(p.read_bytes()==body,'exact frozen root proof')
else:p.write_bytes(body)
print(json.dumps({k:v for k,v in out.items()if k!='proofs'}))
