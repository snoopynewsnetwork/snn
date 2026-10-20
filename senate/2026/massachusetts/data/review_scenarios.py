"""Independent source-weight and saturation-event audit, no producer solver."""
from pathlib import Path
import csv,gzip,hashlib,io,json,math
S=Path(__file__).resolve().parents[1];B=S/'data/baselines';N=0
def ck(v,note=''):
 global N
 assert v,note;N+=1
def close(a,b,atol=2e-8):ck(math.isclose(a,b,rel_tol=2e-11,abs_tol=atol),(a,b))
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(S)),bytes=len(b),sha256=sha(b))
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def root(units,wanted):
 events={}
 for T,s in units:
  events[-s]=events.get(-s,0)+2*T;events[1-s]=events.get(1-s,0)-2*T
 x=-1.;f=-sum(t for t,s in units);slope=0
 for e,change in sorted(events.items()):
  nxt=f+slope*(e-x)
  if slope>0 and f<=wanted<=nxt:return x+(wanted-f)/slope
  x=e;f=nxt;slope+=change
 raise AssertionError('target not bracketed')
def main():
 refs={r['id']:r for r in read(S/'data/turnout/source/shared-originals.json')};originals={};inputpins=[]
 for tag,prefix in [('2024-senate','sos-2024-senate'),('2020-senate','sos-observed-2020-senate'),('2022-governor','sos-observed-2022-governor'),('2024-president','sos-observed-2024-president')]:
  originals[tag]={}
  for scope in ['municipal','precinct']:
   r=refs[prefix+'-'+scope+'-csv'];p=S/r['immutable_body_path'];z=p.read_bytes();ck(sha(z)==r['stored_sha256']);raw=gzip.decompress(z);ck(sha(raw)==r['raw_sha256']);rows=list(csv.reader(io.StringIO(raw.decode('utf-8-sig'))));originals[tag][scope]={json.dumps(r[:3],ensure_ascii=False,separators=(',',':')):[int(v.replace(',',''))for v in r[3:]]for r in rows[2:-1]};inputpins.append(pin(p))
 settings=read(B/'scenarios/settings.json');states=list(csv.DictReader((B/'scenarios/state-targets.csv').open()));ck(len(settings)==18 and len(states)==36);unitrows=0;maxshift=maxres=0.;reviewed=[]
 for cfg in settings:
  name=cfg['name'];scope=cfg['scope'];pref=originals[cfg['preference_anchor']][scope];volume=originals[cfg['volume_anchor']]['municipal'];inp=read(B/cfg['input_file']);units=inp['units'];ck(len(units)==len(pref));ck({r['key']for r in units}==set(pref));expected=[]
  for u in units:
   values=pref[u['key']];P=values[0]+values[1];town=json.loads(u['key'])[0]
   if scope=='municipal':v=volume[json.dumps([town,'',''],ensure_ascii=False,separators=(',',':'))];T=v[0]+v[1]
   else:T=P*cfg['scale']
   share=values[0]/P if P else .5;other=(sum(values[:-2])-P)*T/P if P else 0
   close(u['T'],T);close(u['share'],share);close(u['other_votes'],other);expected.append((T,share))
  T=sum(t for t,s in expected);M=sum(t*(2*s-1)for t,s in expected);other=sum(u['other_votes']for u in units)
  for target,suffix in [(0,'tie'),(.01,'Aplus1')]:
   st=next(r for r in states if r['scenario']==name and float(r['target_pair_margin'])==target);wanted=target*T;d=root(expected,wanted);maxshift=max(maxshift,abs(d-float(st['bounded_share_shift'])));close(d,float(st['bounded_share_shift']),1e-11);close(float(st['pair_total']),T);close(float(st['baseline_net_votes']),M);close(float(st['reported_final_denominator']),T+other);close(float(st['unbounded_share_shift']),(wanted-M)/(2*T));close(float(st['unbounded_share_shift_pp']),100*(wanted-M)/(2*T));close(float(st['bounded_share_shift_pp']),100*d)
   rows=list(csv.DictReader((B/'scenarios'/f'{name}-{suffix}.csv').open()));ck(len(rows)==len(units));net=0;weights=0
   for u,(t,s),r in zip(units,expected,rows):
    ck(r['key']==u['key']);vals=pref[u['key']];ck(int(r['source_A'])==vals[0]and int(r['source_B'])==vals[1]);x=max(0,min(1,s+d));fixed=M-t*(2*s-1);req=(wanted-fixed+t)/(2*t)if t else None
    for field,v in [('T',t),('share',s),('weight',t/T),('target_share',x),('target_pair_margin',2*x-1),('target_net_votes',t*(2*x-1)),('gain_net_votes',2*t*(x-s)),('gain_net_per_A_share_pp',.02*t),('other_units_fixed_net',fixed)]:close(float(r[field]),v)
    if req is None:ck(r['selected_only_status']=='no_positive_pool');ck(r['selected_only_raw_share']=='')
    else:close(float(r['selected_only_raw_share']),req);close(float(r['selected_only_clipped_share']),max(0,min(1,req)));ck(r['selected_only_status']==('already_secured'if req<0 else'impossible'if req>1 else'feasible'))
    weights+=float(r['weight']);net+=float(r['target_net_votes']);unitrows+=1
   close(weights,1);close(net,wanted,1e-6);maxres=max(maxres,abs(net-wanted));reviewed.append(pin(B/'scenarios'/f'{name}-{suffix}.csv'))
  reviewed.append(pin(B/cfg['input_file']))
 reviewed.extend([pin(B/'scenarios/settings.json'),pin(B/'scenarios/state-targets.csv')])
 out=dict(status='pass_independent_original_weight_and_saturation_event_math',checks=N,state_scenarios=36,source_settings=18,every_unit_target_rows=unitrows,all_nonpriority_retained=True,maximum_shift_error=maxshift,maximum_net_vote_residual=maxres,complete_original_inputs=inputpins,exact_scenario_inputs_outputs=reviewed,independent_solver='Sorted saturation breakpoint integration; no producer bisection/extractor imported.',qualification='Literal all351municipal comparison/mix assumptions and separate own-native contexts; synthetic2024fixed-mix scaling explicit, no old-native or current identity join. Namedpair targets distinct from generic/full-field plurality or eligibility; zero pool placeholders are arithmetic only. No2026projection or probability.')
 p=S/'data/coordinator-first-pair-math-review.json';p.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n');print(dict(checks=N,rows=unitrows,shift_error=maxshift,net_residual=maxres,pin=pin(p)))
if __name__=='__main__':main()
