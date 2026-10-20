#!/usr/bin/env python3
"""Historical scenario build from independent positional extraction, never peer values."""
import csv,gzip,json,math,re,sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote
from calculator import calculate
from extract import P,save,csvout,js,load,sha
PAIRS={'2024':('Kamala D. Harris/Tim Walz','Donald J. Trump/JD Vance'),'2022':('Natalie James','Senator John Boozman'),'2020-sen':('Ricky Dale Harrington Jr.','Senator Tom Cotton'),'2020-pres':('Joseph R. Biden/Kamala Harris','Donald J. Trump/Michael R. Pence')}
def pair_for(y,c):return PAIRS['2020-sen' if y=='2020' and c=='U.S. Senate' else '2020-pres' if y=='2020' else y]
def getrecords():
 f=P/'candidate-records.csv.gz'
 return list(csv.DictReader(gzip.open(f,'rt') if f.exists() else (P/'candidate-records.csv').open()))
def groups():
 g={};rr=getrecords()
 for r in rr:
  if r['level']!='native' or r['method'] not in ['All','total votes']:continue
  lane=r['lane'];ci=r['county_id'];n=r['native_name'] if lane.endswith('xlsx') else r['native_id']
  key=f"AR:{lane}:{ci}:{quote(n,safe='')}";k=(lane,r['contest'],key)
  if k not in g:g[k]={'key':key,'lane':lane,'year':r['year'],'contest':r['contest'],'county_fips':ci,'county_name':r['county'],'native_id':r['native_id'] if lane.endswith('api') else None,'native_name':r['native_name'],'candidates':{},'party_literals':{},'source_positions':[],'methods':{}}
  u=g[k];assert r['candidate'] not in u['candidates'],k
  u['candidates'][r['candidate']]=int(r['votes']);u['party_literals'][r['candidate']]=r['party_literal'];u['source_positions'].append({'source_id':r['source_id'],'position':r['position']})
 # candidate-level methods, not merely geography totals.
 methods=defaultdict(lambda:defaultdict(dict))
 for r in rr:
  if r['lane']=='2024-xlsx' and r['method']!='total votes':
   key=f"AR:2024-xlsx:{r['county_id']}:{quote(r['native_name'],safe='')}";methods[key][r['method']][r['candidate']]=int(r['votes'])
 for u in g.values():
  u['votes']=sum(u['candidates'].values());u['methods']=dict(methods.get(u['key'],{}))
 return list(g.values())
def county_groups(units):
 g={}
 for u in units:
  k=(u['lane'],u['contest'],u['county_fips'])
  if k not in g:g[k]={**{f:u[f] for f in ['lane','year','contest','county_fips','county_name']},'key':f"AR:{u['lane']}-county:{u['county_fips']}",'candidates':defaultdict(int),'source_positions':[]}
  c=g[k]
  for n,v in u['candidates'].items():c['candidates'][n]+=v
  c['source_positions'].append(u['key'])
 for c in g.values():c['candidates']=dict(c['candidates']);c['votes']=sum(c['candidates'].values())
 return list(g.values())
def input_for(units,pair,volumes=None,label='own historical volume; all units'):
 others=[c for c in units[0]['candidates'] if c not in pair]
 out=[]
 for u in units:
  cs=u['candidates'];assert set(cs)==set(pair+tuple(others))
  a,b=cs[pair[0]],cs[pair[1]];t=a+b;full=sum(cs.values());o=full-t
  alloc={c:cs[c]/o if o else (1 if i==0 else 0) for i,c in enumerate(others)}
  out.append({'key':u['key'],'counted':{c:0 for c in cs},'remaining':volumes[u['key']] if volumes else full,'pair_participation':t/full if full else 1,'a_share':a/t if t else None,'other_allocation':alloc})
 return {'mode':'historical','objective':'pair_margin','pair':list(pair),'other_candidates':others,'units':out,'target_margin':0,'source_scope':label,'assumptions':'Historical named-candidate preferences and pair participation held fixed. Other allocations historical within unit; allocation when zero other pool is a numerical convention with zero effect. No crossyear native join, candidate effect, or 2026 turnout projection.'}
TURNOUT={}
FULLTURNOUT={}
def summarize(c):
 a,b=pair_for(c['year'],c['contest']);v=c['candidates'];t=v[a]+v[b];n=v[a]-v[b];m=n/t if t else None
 api=TURNOUT[(int(c['year']),c['county_fips'])];ft=FULLTURNOUT[(c['year'],c['county_name'])]
 return {k:c[k] for k in ['key','lane','year','contest','county_fips','county_name']}|{'candidate_a':a,'candidate_b':b,'a_votes':v[a],'b_votes':v[b],'other_votes':c['votes']-t,'all_candidate_votes':c['votes'],'pair_votes':t,'pair_participation':t/c['votes'] if c['votes'] else None,'a_pair_share':v[a]/t if t else None,'pair_margin':m,'all_candidate_pair_margin':n/c['votes'] if c['votes'] else None,'pair_winner':a if n>0 else b if n<0 else 'tie','margin_band':'undefined' if m is None else '<=5pp' if abs(m)<=.05 else '>5-10pp' if abs(m)<=.1 else '>10pp','candidates_json':json.dumps(v,ensure_ascii=False),'source_units_json':json.dumps(c['source_positions'],ensure_ascii=False),'ballots_cast':api['totalBallotsCast'] if c['lane'].endswith('api') else ft['VotesCast'] if c['lane'].endswith('full') else None,'registered_voters':api['registeredVoters'] if c['lane'].endswith('api') else ft['RegisteredVoters'] if c['lane'].endswith('full') else None,'api_ballots_cast':api['totalBallotsCast'],'api_registered_voters':api['registeredVoters'],'full_ballots_cast':ft['VotesCast'],'full_registered_voters':ft['RegisteredVoters'],'turnout_source_year':c['year'],'turnout_scope':'publication-specific county controls; no native turnout allocation','blank':None,'undervotes':None,'overvotes':None,'write_in_scope':'source reported choices only; no inferred eligible write-ins'}
def build():
 units=groups();counties=county_groups(units)
 for t in json.loads((P/'source/turnout-controls.json').read_text()):TURNOUT[(t['year'],t['county_id'])]=t['response']
 for year in ['2020','2022','2024']:
  for t in js(year+'-full')['Turnout']['CountyTurnout']:FULLTURNOUT[(year,t['CountyName'].upper())]=t
 save('native-baselines.json',units);csvout('../county-baselines.csv',[summarize(c) for c in counties])
 scenarios=[];targetrows=[];states=[]
 native_scopes=defaultdict(list);county_scopes=defaultdict(list)
 for u in units:native_scopes[(u['lane'],u['contest'])].append(u)
 for c in counties:county_scopes[(c['lane'],c['contest'])].append(c)
 for level,scopes in [('native',native_scopes),('county',county_scopes)]:
  for (lane,contest),us in scopes.items():
   pair=pair_for(us[0]['year'],contest);scenarios.append((f'{lane}-{contest}-{level}-own-history',input_for(us,pair,label=f'{lane}; {contest}; {level}; own historic volume')))
 # Explicit measured low/base/high volumes with distinct county mixes, 2024 preference anchor.
 base=county_scopes[('2024-xlsx','U.S. President')]
 for label,source in [('low-2022-senate',('2022-api','U.S. Senate')),('base-2024-president',('2024-xlsx','U.S. President')),('high-2020-president',('2020-api','U.S. President, Vice President'))]:
  mix={c['county_fips']:c['votes'] for c in county_scopes[source]};assert len(mix)==75
  scenarios.append((f'2024-preference-{label}-county',input_for(base,PAIRS['2024'],{c['key']:mix[c['county_fips']] for c in base},label=f'2024 presidential county preferences/participation; actual {label} county contest volumes')))
 # Other named preference anchors use primary 2024 county contest volumes, with their own pair participation.
 volume2024={c['county_fips']:c['votes'] for c in base}
 for anchor in [('2022-api','U.S. Senate'),('2020-api','U.S. Senate')]:
  us=county_scopes[anchor];pair=pair_for(us[0]['year'],anchor[1]);scenarios.append((f'{anchor[0]}-named-preferences-2024-volume-county',input_for(us,pair,{c['key']:volume2024[c['county_fips']] for c in us},label=f'{anchor[0]} {anchor[1]} named preference and pair participation, actual 2024 presidential county contest volumes; explicit conditional transfer')))
 # Complete native low/high volume scaling, same-year method mixes; no crossyear precinct allocation.
 primary=native_scopes[('2024-xlsx','U.S. President')];base_total=sum(c['votes'] for c in primary)
 for label,scope in [('low-2022-state-total',('2022-api','U.S. Senate')),('high-2020-state-total',('2020-api','U.S. President, Vice President'))]:
  anchor=sum(c['votes'] for c in county_scopes[scope]);scenarios.append((f'2024-native-{label}',input_for(primary,PAIRS['2024'],{u['key']:u['votes']*anchor/base_total for u in primary},label=f'2024 native composition/preferences/participation; uniformly scaled to measured {label}={anchor}, no crossyear native join')))
 for method in ['Election Day','Early Vote','Absentee','Provisional']:
  volumes={u['key']:sum(u['methods'][method].values()) for u in primary}
  scenarios.append((f'2024-native-{method}-mix',input_for(primary,PAIRS['2024'],volumes,label=f'2024 {method} actual unit volumes; full-contest 2024 native preference/participation anchor, conditional mix stress only')))
 # Historical input files and complete unit/county contribution and selected-only thresholds.
 (P/'scenarios').mkdir(exist_ok=True)
 for name,d in scenarios:
  save(f'scenarios/{name}.input.json',d)
  for margin in [0,.01]:
   d['target_margin']=margin;r=calculate(d);un=r['uniform'];base=r['baseline'];root=un.get('bounded_common_share_shift');F=r['final_pair_denominator'];M=base['pair_net_votes'];U=r['remaining_pair']
   states.append({'scenario':name,'target_pair_margin':margin,'source_scope':d['source_scope'],'units':len(d['units']),'all_candidate_total':r['final_all_candidate_denominator'],'pair_total':F,'baseline_net':M,'baseline_pair_margin':base['pair_margin'],'unbounded_share_shift':un.get('unbounded_pair_share_shift'),'bounded_share_shift':root,'status':un['status'],'clipped_units':len(un.get('clipped_units',[])),'target_net':un.get('target',{}).get('pair_net_votes') if un.get('target') else None,'residual':un.get('target',{}).get('objective_residual_net_votes') if un.get('target') else None})
   for row,u in zip(r['units'],d['units']):
    t=row['pair_pool'];q=u['a_share'];others_net=M-(t*(2*q-1) if q is not None else 0);required=(margin*F-others_net+t)/(2*t) if t else None
    targetrows.append({'scenario':name,'key':row['key'],'target_pair_margin':margin,'pair_votes':t,'all_candidate_volume':u['remaining'],'pair_participation':u['pair_participation'],'state_pair_weight':row['state_final_pair_weight'],'state_all_candidate_weight':u['remaining']/r['final_all_candidate_denominator'] if r['final_all_candidate_denominator'] else None,'baseline_a_share':row['baseline_a_share'],'baseline_net':row['baseline_remaining_net'],'target_a_share':row['target_a_share'],'target_pair_margin_unit':2*row['target_a_share']-1 if row['target_a_share'] is not None else None,'share_shift':row['target_a_share']-q if row['target_a_share'] is not None and q is not None else None,'target_net':row['target_remaining_net'],'net_gain':row['target_remaining_net']-row['baseline_remaining_net'] if row['target_remaining_net'] is not None and row['baseline_remaining_net'] is not None else None,'net_per_1_share_pp':row['net_gain_per_one_share_point'],'selected_only_required_raw':required,'selected_only_required_clipped':min(1,max(0,required)) if required is not None else None,'selected_only_status':'no-positive-pool' if required is None else 'secured' if required<0 else 'impossible' if required>1 else 'feasible','others_assumption':'every other unit fixed at historical source share/participation under this scenario volume'})
 csvout('state-scenarios.csv',states);csvout('unit-targets.csv',targetrows)
 save('build-summary.json',{'native_units_by_contest':{f'{k[0]}|{k[1]}':len(v) for k,v in native_scopes.items()},'counties_by_contest':{f'{k[0]}|{k[1]}':len(v) for k,v in county_scopes.items()},'scenarios':len(scenarios),'target_rows':len(targetrows)})
if __name__=='__main__':build()
