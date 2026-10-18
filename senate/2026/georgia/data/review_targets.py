#!/usr/bin/env python3
"""Coordinator audit: breakpoint solve, serialized targets, fixed remainder arithmetic."""
import collections,csv,datetime,gzip,hashlib,io,json,math
from pathlib import Path
D=Path(__file__).resolve().parent;ROOT=D.parent;B=D/'baselines'
def rows(path):
 b=path.read_bytes();return list(csv.DictReader(io.StringIO((gzip.decompress(b) if path.suffix=='.gz' else b).decode())))
def near(a,b):assert math.isclose(float(a),float(b),rel_tol=3e-11,abs_tol=4e-7),(a,b)
def clip(v):return min(1.,max(0.,v))
def solve(weights,shares,target):
 points=sorted({-1.,1.}|{-s for s in shares}|{1-s for s in shares})
 def net(d):return math.fsum(w*(2*clip(s+d)-1) for w,s in zip(weights,shares))
 left=points[0];lv=net(left)
 for right in points[1:]:
  rv=net(right)
  if lv<=target<=rv and rv!=lv:return left+(right-left)*(target-lv)/(rv-lv)
  left,lv=right,rv
 raise AssertionError('unreachable goal')
def status(q):return 'already_secured' if q<0 else 'impossible' if q>1 else 'feasible'
def main():
 base=rows(D/'county-baselines.csv');assert len(base)==795
 by={e:{r['county_fips']:r for r in base if r['election_key']==e} for e in {r['election_key'] for r in base}}
 assert len(by)==5 and all(len(v)==159 for v in by.values());keys=set(next(iter(by.values())))
 states=rows(B/'state-scenarios.csv');county=rows(B/'county-targets.csv.gz');assert len(states)==50 and len(county)==7950
 for st in states:
  rs=[r for r in county if r['scenario']==st['scenario']];assert len(rs)==159 and {r['county_fips'] for r in rs}==keys
  pref=by[st['preference_anchor']];mix=by[st['mix_volume_anchor']];g=float(st['target_pair_margin_pp'])/100
  weights=[int(mix[r['county_fips']]['pair_votes']) for r in rs];shares=[int(pref[r['county_fips']]['A'])/int(pref[r['county_fips']]['pair_votes']) for r in rs]
  P=sum(weights);M=math.fsum(t*(2*s-1) for t,s in zip(weights,shares));delta=solve(weights,shares,g*P);O=sum(int(x['other_named_valid_votes']) for x in mix.values());extra=858 if st['mix_volume_anchor']=='2024NovGen' else 0
  near(st['pair_votes'],P);near(st['baseline_net'],M);near(st['unbounded_shift_pp'],100*(g*P-M)/(2*P));near(st['bounded_shift_pp'],100*delta);near(st['actual_net'],g*P)
  near(st['named_other_fixed'],O);near(st['separate_state_qualified_writeins'],extra);near(st['final_allcandidate_denominator'],P+O+extra);near(st['majority_cushion_votes'],(g*P-O-extra)/2)
  assert (st['A_strict_majority']=='True')==((g*P-O-extra)/2>0)
  for r,t,s in zip(rs,weights,shares):
   q=clip(s+delta);outside=M-t*(2*s-1);selected=(t+g*P-outside)/(2*t)
   near(r['baseline_A_pair_share'],s);near(r['expected_pair_votes'],t);near(r['pair_weight'],t/P);near(r['baseline_net'],t*(2*s-1));near(r['target_A_pair_share'],q);near(r['target_net'],t*(2*q-1));near(r['actual_shift_share_pp'],100*(q-s));near(r['linear_gain_for_plus1_share_pp_net'],.02*t);near(r['gain_for_plus1_share_pp_net'],2*t*(clip(s+.01)-s))
   near(r['outside_fixed_net'],outside);near(r['selected_raw_required_share'],selected);near(r['selected_required_share'],clip(selected));assert r['selected_status']==status(selected)
 native=rows(B/'native-baselines.csv.gz');nt=rows(B/'native-targets.csv.gz');assert len(native)==2701 and len(nt)==5402
 index={(r['county_fips'],r['native_GUID']):r for r in native};assert len(index)==2701
 assert collections.Counter((r['county_fips'],r['native_GUID']) for r in nt)==collections.Counter({k:2 for k in index})
 P=sum(int(r['pair_votes']) for r in by['2024NovGen'].values());M=sum(int(r['A'])-int(r['B']) for r in by['2024NovGen'].values())
 known=[r for r in native if r['pair_votes'] and float(r['pair_votes'])>0];ts=[float(r['pair_votes']) for r in known];ss=[float(r['A'])/float(r['pair_votes']) for r in known];KP=sum(ts);KM=sum(float(r['A'])-float(r['B']) for r in known);shifts={}
 for st in json.loads((B/'native-state-scenarios.json').read_text()):
  g=st['target_pair_margin_pp']/100;shift=solve(ts,ss,g*P-(M-KM));shifts[g]=shift
  near(st['bounded_shift_pp'],shift*100);near(st['unallocated_withheld_pair_votes_held_fixed'],P-KP);near(st['unallocated_withheld_net_held_fixed'],M-KM);near(st['allstate_actual_net_including_withheld_fixed'],g*P)
 for r in nt:
  u=index[r['county_fips'],r['native_GUID']];g=float(r['target_pair_margin_pp'])/100
  assert r['source_id']==u['source_id'] and r['source_pointer']==u['source_pointer']
  if not u['pair_votes']:
   assert r['status']=='redacted_unknown_no_allocation' and r['target_share']=='';continue
  t=float(u['pair_votes']);near(r['pair_votes'],t)
  if not t:assert r['status']=='no_positive_pool';continue
  s=float(u['A'])/t;q=clip(s+shifts[g]);near(r['target_share'],q);near(r['target_net'],t*(2*q-1));near(r['pair_weight_in_complete_county_state'],t/P);near(r['selected_unbounded_share'],(t+g*P-(M-(float(u['A'])-float(u['B']))))/(2*t))
 mb=rows(B/'method-baselines.csv.gz');mt=rows(B/'method-targets.csv.gz');assert len(mb)==13984 and len(mt)==27968
 groups=collections.defaultdict(list)
 for r in mb:groups[r['unit_level'],r['election_key']].append(r)
 method_index={(r['unit_level'],r['election_key'],r['county_fips'],r['native_GUID'],r['group_GUID']):r for r in mb};assert len(method_index)==13984
 method_shifts={}
 for st in json.loads((B/'method-state-scenarios.json').read_text()):
  k=(st['unit_level'],st['election_key']);g=st['target_pair_margin_pp']/100;rs=groups[k];known=[r for r in rs if r['pair_votes'] and int(r['pair_votes'])>0];ts=[int(r['pair_votes']) for r in known];ss=[int(r['A'])/int(r['pair_votes']) for r in known];P=sum(int(r['pair_votes']) for r in by[k[1]].values());M=sum(int(r['A'])-int(r['B']) for r in by[k[1]].values());WM=M-sum(int(r['A'])-int(r['B']) for r in known);WP=P-sum(ts);shift=solve(ts,ss,g*P-WM);method_shifts[k+(g,)]=shift
  near(st['bounded_shift_pp'],100*shift);near(st['unallocated_redacted_pair_votes_held_fixed'],WP);near(st['unallocated_redacted_net_held_fixed'],WM);near(st['allstate_actual_net'],g*P)
 for r in mt:
  k=(r['unit_level'],r['election_key'],r['county_fips'],r['native_GUID'],r['group_GUID']);u=method_index[k];assert r['status']==u['status'];g=float(r['target_pair_margin_pp'])/100
  if not u['pair_votes']:assert r['target_A_pair_share']=='' and r['selected_status']=='unknown_redacted';continue
  t=int(u['pair_votes']);near(r['pair_votes'],t)
  if not t:assert r['selected_status']=='no_positive_pool';continue
  P=sum(int(x['pair_votes']) for x in by[r['election_key']].values());M=sum(int(x['A'])-int(x['B']) for x in by[r['election_key']].values());s=int(u['A'])/t;q=clip(s+method_shifts[k[:2]+(g,)])
  near(r['target_A_pair_share'],q);near(r['target_net'],t*(2*q-1));near(r['selected_raw_required_share'],(t+g*P-(M-(int(u['A'])-int(u['B']))))/(2*t))
 cases=json.loads((B/'live-scenarios.json').read_text());outs=json.loads((B/'live-results.json').read_text());assert len(cases)==len(outs)==13
 for case,out in zip(cases,outs):
  rs=case['units'];assert out['name']==case['name']
  A0=sum(r['counted_A'] for r in rs);B0=sum(r['counted_B'] for r in rs);O0=sum(r['counted_other'] for r in rs)
  near(out['counted_A'],A0);near(out['counted_B'],B0);near(out['counted_other'],O0)
  if 'final_A' not in out:
   assert out['status'] in ['invalid_duplicate_unit','unknown_remaining_assumptions','invalid_negative_counted','invalid_negative_remaining'];continue
  U=sum(r['remaining_total']*r['remaining_pair_fraction'] for r in rs);A=A0+sum(r['remaining_total']*r['remaining_pair_fraction']*clip(r['remaining_A_pair_share']) for r in rs);Bv=B0+sum(r['remaining_total']*r['remaining_pair_fraction']*(1-clip(r['remaining_A_pair_share'])) for r in rs);O=O0+sum(r['remaining_total']*(1-r['remaining_pair_fraction']) for r in rs);P=A+Bv;F=P+O
  near(out['final_A'],A);near(out['final_B'],Bv);near(out['final_other'],O);near(out['FINAL_pair_denominator'],P);near(out['FINAL_allcandidate_denominator'],F);near(out['majority_cushion_votes'],A-F/2);assert out['A_strict_majority']==(A>F/2)
  if U:
   near(out['required_remaining_A_pair_share_unbounded'],(U+case.get('target_pair_margin_pp',0)/100*P-(A0-B0))/(2*U));near(out['majority_remaining_A_share_boundary_strictly_exceed'],(F/2-A0)/U)
   pick=case.get('selected_unit',rs[0]['id']);x=next(x for x in rs if x['id']==pick);u=x['remaining_total']*x['remaining_pair_fraction'];outside=A0-B0+sum(v['remaining_total']*v['remaining_pair_fraction']*(2*clip(v['remaining_A_pair_share'])-1) for v in rs if v['id']!=pick)
   if u:near(out['selected_required_share_unbounded'],(u+case.get('target_pair_margin_pp',0)/100*P-outside)/(2*u))
 mf=json.loads((B/'asset-manifest.json').read_text())
 for asset in mf['assets']:
  b=(ROOT/asset['path']).read_bytes();assert len(b)==asset['bytes']<40000000 and hashlib.sha256(b).hexdigest()==asset['sha256'],asset['path']
 result={'status':'pass','checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'independent_solver':'piecewise linear breakpoints; worker uses bisection','county_election_rows':795,'state_scenarios':50,'county_targets':7950,'native_targets':5402,'method_targets':27968,'live_cases':13,'owned_asset_hashes':len(mf['assets']),'scope':'Historical conditional arithmetic; fixed withheld pools and all-candidate majority separated from pair margin. No live forecast or current geography approval.'}
 out=D/'coordinator-target-review.json'
 if out.exists():
  old=json.loads(out.read_text())
  if {k:v for k,v in old.items() if k!='checked_utc'}=={k:v for k,v in result.items() if k!='checked_utc'}:result['checked_utc']=old['checked_utc']
 out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
