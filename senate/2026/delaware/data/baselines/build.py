#!/usr/bin/env python3
"""Build complete historical baselines, exact ranks and conditional targets offline."""
from pathlib import Path
import csv,json,collections,hashlib,math
from extract import writecsv,writejson,COUNTIES
from calculators import uniform,selected,clip,live
P=Path(__file__).resolve().parent

def main():
 rows=list(csv.DictReader((P/'extracted/candidate-geography.csv').open())); wi=list(csv.DictReader((P/'extracted/writeins.csv').open()));hier=json.loads((P/'extracted/participation-hierarchy.json').read_text());structure=json.loads((P/'extracted/district-structure.json').read_text());officeparents=json.loads((P/'extracted/county-parent-evidence.json').read_text())
 hm={(r['year'],r['geo_key']):r for r in hier};sm={r['geo_key']:r for r in structure};om={(r['year'],r['geo_key']):r for r in officeparents};groups=collections.defaultdict(list)
 for r in rows:
  # State repeats in county wide views are controls, not additive units.
  if r['view'] in ['bycounty','bycountyw'] and r['geo_key']=='State':continue
  groups[(int(r['year']),r['office_key'],r['view'],r['geo_key'])].append(r)
 base=[];parentchecks=[]
 for (yr,office,view,key),rs in groups.items():
  a=next(r for r in rs if r['party'].lower().startswith('democratic'));b=next(r for r in rs if r['party'].lower().startswith('republican'));A=int(a['total']);B=int(b['total']);T=A+B;C=sum(int(r['total']) for r in rs);O=C-T;county=rs[0]['county'] or None;parent_basis='County source column' if view in ['bycounty','bycountyw'] else None
  if view=='byelectiondist':
   candidates=[]
   if om[(yr,key)]['county']:candidates.append(('county-office membership',om[(yr,key)]['county']))
   if (yr,key) in hm:candidates.append(('same-year participation hierarchy',hm[(yr,key)]['county']))
   if yr in [2022,2024] and key in sm:candidates.append(('published 2022–2032 structure, updated 2024-02-13',sm[key]['county']))
   assert len(set(c for label,c in candidates))<=1,(yr,key,candidates)
   county=candidates[0][1] if candidates else None;parent_basis='; '.join(x[0] for x in candidates) or 'Unavailable; retained statewide without guessed county'
   parentchecks.append(dict(year=yr,office_key=office,geo_key=key,county=county,evidence=candidates))
  supplements=[r for r in wi if int(r['year'])==yr and r['office_key']==office and ((view=='statewide') or (view=='bycounty' and r['geo_key']==key))]
  supp=sum(int(r['total']) for r in supplements)
  if office=='USSenator':full=C;fullscope='HTML complete printed field; archived declared-writein list and tally have no Senate entries; generic writeins unavailable'
  elif view=='statewide' or (yr==2024 and view=='bycounty'):full=C+supp;fullscope='HTML printed candidates plus separate official named write-in tally; generic writeins unavailable'
  else:full=None;fullscope='HTML printed candidates only; separate write-ins lack this geography allocation'
  fullother=None if full is None else full-T
  data=dict(year=yr,election_date=rs[0]['election_date'],office_key=office,comparison_role=('same Class II Senate seat' if yr==2020 and office=='USSenator' else 'priority other Class I Senate seat' if yr==2024 and office=='USSenator' else 'actual at-large House midterm; no 2022 Senate/governor' if yr==2022 else 'separate presidential comparison'),view=view,geo_key=key,geo_label=rs[0]['geo_label'],county=county,fips=COUNTIES.get(county),parent_basis=parent_basis,A_candidate=a['candidate'],A_party=a['party'],B_candidate=b['candidate'],B_party=b['party'],A=A,B=B,pair_total=T,named_other=O,named_total=C,supplement_writeins_at_this_scope=supp if full is not None else None,combined_published_total=full,denominator_scope=fullscope,pair_A_share=A/T if T else None,pair_margin=(A-B)/T if T else None,net_A_minus_B=A-B,named_margin=(A-B)/C if C else None,combined_margin=(A-B)/full if full else None,pair_participation_named=T/C if C else None,candidates_json=json.dumps([{'candidate':r['candidate'],'party':r['party'],'votes':int(r['total'])} for r in rs],ensure_ascii=False),supplement_candidates_json=json.dumps([{'candidate':r['candidate'],'party':None,'votes':int(r['total']),'source':r['source_id']} for r in supplements],ensure_ascii=False),source_id=rs[0]['source_id'],source_char_start=min(int(r['source_char_start']) for r in rs),source_char_end=max(int(r['source_char_end']) for r in rs))
  base.append(data)
 # Each view is separately exhaustive, never summed with another view.
 for r in base:
  state=next(x for x in base if x['year']==r['year'] and x['office_key']==r['office_key'] and x['view']=='statewide')
  r['named_state_weight']=r['named_total']/state['named_total'];r['pair_state_weight']=r['pair_total']/state['pair_total'];r['pair_gain_net_per_1pp']=.02*r['pair_total'];r['state_pair_margin_gain_pp_per_1pp']=2*r['pair_state_weight'];r['pair_winner']='A' if r['A']>r['B'] else 'B' if r['B']>r['A'] else 'tie';r['closeness_band']=None if r['pair_margin'] is None else '<=5pp' if abs(r['pair_margin'])<=.05 else '>5–10pp' if abs(r['pair_margin'])<=.1 else '>10pp'
 writecsv(P/'native-baselines.csv',base);writecsv(P.parent/'county-baselines.csv',[r for r in base if r['view']=='bycounty']);writejson(P/'extracted/resolved-parent-evidence.json',parentchecks)
 # Full native/county/RD/Wilmington descending ranks, lexical literal-key tiebreak.
 ranks=[];contracts=[]
 scenarios=[];targets=[]
 for group,bs in groupby(base).items():
  yr,office,view=group
  for metric in ['named_total','pair_total']:
   order=sorted(bs,key=lambda r:(-r[metric],r['geo_key']));total=sum(r[metric] for r in order);cum=0;cross=None;threshold=(4*total+4)//5
   for i,r in enumerate(order,1):
    before=cum;cum+=r[metric]
    if cross is None and cum>=threshold:cross=i
    ranks.append(dict(year=yr,office_key=office,view=view,metric=metric,rank=i,geo_key=r['geo_key'],county=r['county'],votes=r[metric],state_total=total,cumulative_votes=cum,cumulative_share=cum/total if total else None,minimum80_member=before<threshold,top15_member=i<=15))
   contracts.append(dict(year=yr,office_key=office,view=view,metric=metric,state_total=total,threshold_integer=threshold,minimum80_count=cross,minimum80_keys=[r['geo_key'] for r in order[:cross]],before_crossing=sum(r[metric] for r in order[:cross-1]),at_crossing=sum(r[metric] for r in order[:cross]),top15_count=min(15,len(order)),top15_votes=sum(r[metric] for r in order[:15]),priority_union_keys=[r['geo_key'] for r in order[:max(min(15,len(order)),cross)]],descending_order=[r['geo_key'] for r in order],sort='descending integer contest votes; lexical source geo_key for ties',county_geometry_approval=False))
  scenario(f'{yr}-{office}-{view}-historical',bs,[r['pair_total'] for r in bs],[r['pair_A_share'] for r in bs],scenarios,targets,'Own historical pair volume and own preference; named other held fixed',bs)
 # Cross-county historical volume/mix and preference sensitivity; stable county identities only.
 cs={}
 for r in base:
  if r['view']=='bycounty':cs[(r['year'],r['office_key'],r['geo_key'])]=r
 anchors=[('low',2022,'RepresentativeinCongress'),('base',2024,'USSenator'),('high',2024,'PresidentandVicePresident')]
 prefs=[(2020,'USSenator'),(2022,'RepresentativeinCongress'),(2024,'USSenator'),(2024,'PresidentandVicePresident')]
 primary=[cs[(2024,'USSenator',c)] for c in COUNTIES]
 settings=[]
 for label,y,o in anchors:
  vols=[cs[(y,o,c)]['named_total'] for c in COUNTIES];ts=[v*r['pair_participation_named'] for v,r in zip(vols,primary)]
  for py,po in prefs:
   ss=[cs[(py,po,c)]['pair_A_share'] for c in COUNTIES];sid=f'county-{label}-volume-{y}-{o}-preference-{py}-{po}'
   scenario(sid,primary,ts,ss,scenarios,targets,'Historical named-candidate county volume times county 2024 Senate pair participation; preferences explicitly from indicated contest',primary,vols)
   settings.append(dict(scenario=sid,volume_anchor=f'{y} {o}',preference_anchor=f'{py} {po}',all_named_volume=sum(vols),pair_volume=sum(ts),county_volumes=dict(zip(COUNTIES,vols)),county_pair_participation={r['geo_key']:r['pair_participation_named'] for r in primary},candidate_effects='not inferred',unallocated_supplements='2022 House18 and 2024 president1215 remain outside named volume anchor; not allocated into pair votes'))
 # Native historical volume sensitivity scales existing 2024 Senate units uniformly, no cross-year joins.
 ed=[r for r in base if r['year']==2024 and r['office_key']=='USSenator' and r['view']=='byelectiondist'];basevol=sum(r['named_total'] for r in ed)
 for label,y,o in anchors:
  vol=sum(cs[(y,o,c)]['named_total'] for c in COUNTIES);scale=vol/basevol
  scenario(f'native-{label}-historical-volume-scale',ed,[r['pair_total']*scale for r in ed],[r['pair_A_share'] for r in ed],scenarios,targets,'2024 Senate native mix/preferences; uniform scale by stated statewide historical named volume ratio; no cross-year native join',ed,[r['named_total']*scale for r in ed])
 writecsv(P/'geography-ranking.csv',ranks);writejson(P/'priority-contracts.json',contracts);writecsv(P/'state-scenarios.csv',scenarios);writecsv(P/'unit-targets.csv',targets);writejson(P/'scenario-settings.json',settings)
 summary={'primary_county':next(r for r in contracts if r['year']==2024 and r['office_key']=='USSenator' and r['view']=='bycounty' and r['metric']=='named_total'),'primary_native':next(r for r in contracts if r['year']==2024 and r['office_key']=='USSenator' and r['view']=='byelectiondist' and r['metric']=='named_total'),'counts':dict(baselines=len(base),targets=len(targets),scenarios=len(scenarios),ranks=len(ranks))}
 writejson(P/'summary.json',summary);print(json.dumps(summary['counts']));print({k:({kk:vv for kk,vv in v.items() if kk not in ['descending_order','minimum80_keys','priority_union_keys']} if isinstance(v,dict) else v) for k,v in summary.items()})

def groupby(base):
 out=collections.defaultdict(list)
 for r in base:out[(r['year'],r['office_key'],r['view'])].append(r)
 return out

def scenario(sid,bs,ts,ss,scenarios,targets,assumption,primary,vols=None):
 T=sum(ts);M=sum(t*(2*s-1) for t,s in zip(ts,ss) if t>0);vols=vols or [r['named_total'] for r in bs];Other=sum(v-t for v,t in zip(vols,ts));C=T+Other
 for g in [0,.01]:
  sol=uniform(list(zip(ts,ss)),g);d=sol['bounded_shift'];nets=[]
  for r,t,s,v in zip(bs,ts,ss,vols):
   q=clip(s+d) if t>0 else None;net=t*(2*q-1) if t>0 else 0;nets.append(net);ownnet=t*(2*s-1) if t>0 else 0;sel=selected(T,t,M-ownnet,g)
   targets.append(dict(scenario=sid,year=r['year'],office_key=r['office_key'],view=r['view'],geo_key=r['geo_key'],county=r['county'],target_pair_margin=g,scenario_named_volume=v,scenario_pair_volume=t,scenario_named_other=v-t,pair_weight=t/T if T else None,preference_A_share=s,baseline_net=ownnet,uniform_unbounded_shift=sol['raw_shift'],uniform_bounded_shift=d,target_A_share=q,target_pair_margin_unit=None if q is None else 2*q-1,target_net=net,net_gain=net-ownnet,share_shift_pp=None if q is None else 100*(q-s),pair_margin_shift_pp=None if q is None else 200*(q-s),net_gain_per_1pp_unclipped=.02*t,net_gain_per_1pp_clipped=0 if t==0 else 2*t*(clip(s+.01)-s),selected_only_required_share=sel['required_share_unbounded'],selected_only_clipped_share=sel['required_share_clipped'],selected_only_status=sel['status'],selected_other_net_fixed=sel['fixed_other_net'],selected_other_preference_assumption='Every other unit at indicated unshifted preference and stated pair volume',assumption=assumption))
  assert abs(sum(nets)-g*T)<1e-6,(sid,g,sum(nets),g*T)
  combined_available=sid.endswith('-historical') and all(r['combined_published_total'] is not None for r in bs)
  combined_total=sum(r['combined_published_total'] for r in bs) if combined_available else None
  scenarios.append(dict(combined_published_volume=combined_total,combined_published_margin_pp=None if combined_total is None else 100*sum(nets)/combined_total,source_named_writein_supplement=None if combined_total is None else combined_total-C,scenario=sid,target_pair_margin=g,units=len(bs),pair_volume=T,named_volume=C,named_other=Other,baseline_net=M,baseline_pair_margin=M/T if T else None,raw_shift_share_pp=100*sol['raw_shift'] if sol['raw_shift'] is not None else None,bounded_shift_share_pp=100*d if d is not None else None,target_net=sum(nets),target_pair_margin_pp=g*100,target_named_all_candidate_margin_pp=100*sum(nets)/C if C else None,net_needed_for_1pp_all_candidate_margin=.01*C,status=sol['status'],clipped_units=sol['clipped_units'],already_at_target=M>=g*T,assumption=assumption,legal_scope='Pair arithmetic; plurality requires A to exceed every individual other candidate too. Historical Senate minor candidates below pair ties; no lower preferences inferred.'))

if __name__=='__main__':main()
