#!/usr/bin/env python3
"""Build every-county/native historical targets and explicit conditional five-choice paths."""
import sys
sys.dont_write_bytecode=True
import csv,gzip,json,math
from pathlib import Path
from calculator import targets,live
BASE=Path(__file__).resolve().parent
def j(path,x):(BASE/path).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def jl(path,x):(BASE/path).write_bytes(gzip.compress(b''.join((json.dumps(r,separators=(',',':'),allow_nan=False)+'\n').encode()for r in x),mtime=0))
def readlines(path):return [json.loads(s)for s in gzip.decompress((BASE/path).read_bytes()).splitlines()]
def csvwrite(path,rows):
 with (BASE/path).open('w',newline='')as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
ANCHORS={'senate2024special':('Preston Love Jr.','Democratic','Pete Ricketts','Republican'),
 'senate2024regular':('Dan Osborn','By Petition (named independent)','Deb Fischer','Republican'),
 'president2024':('Kamala D. Harris & Tim Walz','Democratic','Donald J. Trump & JD Vance','Republican'),
 'governor2022':('Carol Blood & Al Davis','Democratic','Jim Pillen & Joe Kelly','Republican'),
 'senate2020':('Chris Janicek','Democratic','Ben Sasse','Republican')}
def main():
 t=json.loads((BASE/'extracts/state-controls.json').read_text());native=readlines('extracts/native-special.jsonl.gz');county=list(csv.DictReader((BASE.parent/'county-baselines.csv').open()))
 ci={r['county']:r for r in county};pair_total=sum(t['senate2024special']['state']);volumes={};state=[];detail=[];synthetic=[];settings=[]
 for mix,year in [('low_2022_voting_mix',2022),('base_2024_voting_mix',2024),('high_2020_voting_mix',2020)]:
  # Keep county-specific 2024 special named-pair participation, then change historical ballot volume/mix.
  volumes[mix]={c:sum(t['senate2024special']['county'][c])*t[f'votingmethod{year}']['county'][c][-1]/t['votingmethod2024']['county'][c][-1]for c in ci}
  settings.append(dict(mix=mix,ballot_anchor_year=year,actual_state_total_voting=t[f'votingmethod{year}']['state'][-1],pair_volume=sum(volumes[mix].values()),
   formula='T_c = historical Total Voting(year,c) * (2024special Love_c+Ricketts_c) / 2024 Total Voting(c)',
   native_formula='T_u = 2024special pair_u * T_c / 2024special pair_c; derived sensitivity weights, not observed older native turnout or a cross-year geography match',
   forecast=False))
 def run(sid,rows,anchor,mix,geography,source_total,source_scope):
  for target,margin in [('tie',0.0),('Aplus1_pair_margin',.01)]:
   result=targets(rows,margin);assert result['status']=='solved';a=ANCHORS[anchor]
   for r in result.pop('rows'):
    r.update(scenario=sid,target=target,anchor=anchor,A_candidate=a[0],A_identity=a[1],B_candidate=a[2],B_identity=a[3],geography=geography,source_total_scope=source_scope)
    detail.append(r)
   result.update(scenario=sid,target=target,anchor=anchor,mix=mix,geography=geography,A_candidate=a[0],A_identity=a[1],B_candidate=a[2],B_identity=a[3],
    anchor_published_source_votes=source_total,anchor_all_source_votes=source_total if anchor!='senate2024special'else None,anchor_pair_participation=sum(t[anchor]['state'][:2])/source_total if source_total and anchor!='senate2024special'else None,
    historical_generic_or_other_scope=source_scope,
    all_candidate_cushion_if_held_at_historical_participation_pp=(100*margin*sum(t[anchor]['state'][:2])/source_total)if source_total and anchor!='senate2024special'else None,
    all_candidate_cushion_qualification='Only a denominator conversion holding that source participation fixed. Generic special write-ins unknown statewide; all-source total is two named choices only for special.' )
   state.append(result)
 for anchor in ANCHORS:
  def crows(volume):
   return [dict(key='NE:county:'+r['county_fips'],county=r['county'],label=r['county'],q=t[anchor]['county'][r['county']][1]/sum(t[anchor]['county'][r['county']][:2]),T=volume[r['county']],
    anchor_A=t[anchor]['county'][r['county']][1],anchor_B=t[anchor]['county'][r['county']][0],county_pair_participation_2024special=sum(t['senate2024special']['county'][r['county']])/t['votingmethod2024']['county'][r['county']][-1])for r in county]
  source_total=sum(t[anchor]['state']);scope='two named only; statewide generic/eligible writeins unknown'if anchor=='senate2024special'else'all source candidate columns including separate scattering; generic is not necessarily a valid named vote'
  for mix,volume in volumes.items():run(anchor+'__'+mix,crows(volume),anchor,mix,'county',source_total,scope)
  own={c:sum(v[:2])for c,v in t[anchor]['county'].items()};run(anchor+'__own_historical_pair',crows(own),anchor,'own_historical_pair','county',source_total,scope)
 for mix,volume in volumes.items():
  rows=[dict(key=r['key'],county=r['county'],label=r['label'],q=r['A']/r['pair_votes']if r['pair_votes']else None,T=r['pair_votes']*volume[r['county']]/sum(t['senate2024special']['county'][r['county']]),anchor_A=r['A'],anchor_B=r['B'],county_pair_participation_2024special=sum(t['senate2024special']['county'][r['county']])/t['votingmethod2024']['county'][r['county']][-1])for r in native]
  run('native_senate2024special__'+mix,rows,'senate2024special',mix,'native',pair_total,'two named special; local generic separate and statewide unknown')
 # Keep all93/full1326 in each calculation; priority is not an exclusion filter.
 jl('scenarios/unit-targets.jsonl.gz',detail);csvwrite('scenarios/state-targets.csv',state);j('scenarios/state-targets.json',state)
 # Plain all-county/native base tables with weights, contribution, +1 share pp net leverage.
 baseline=[]
 for r in detail:
  if r['target']=='tie'and r['scenario']in ['senate2024special__base_2024_voting_mix','native_senate2024special__base_2024_voting_mix']:
   baseline.append({k:r[k]for k in ['key','county','label','geography','anchor_A','anchor_B','q','T','weight','baseline_net','net_gain_for_one_share_pp','target_share','target_margin','target_net','target_gain','selected_only_required_share_unbounded','selected_only_status']})
 csvwrite('unit-contributions.csv',baseline)
 # Conditional modern choices. Names come from final primary publication, shares are user assumptions.
 # Hold pair weights T fixed; model three other choices separately as fractions of final valid votes.
 current=[];current_detail=[]
 for geo in ['county','native']:
  anchors=['senate2024special','senate2024regular']if geo=='county'else['senate2024special']
  for anchor in anchors:
   for mix,volume in volumes.items():
    if geo=='county':rows=[dict(key='NE:county:'+ci[c]['county_fips'],county=c,q=t[anchor]['county'][c][1]/sum(t[anchor]['county'][c][:2]),T=volume[c])for c in sorted(ci)]
    else:rows=[dict(key=r['key'],county=r['county'],q=r['A']/r['pair_votes']if r['pair_votes']else None,T=r['pair_votes']*volume[r['county']]/sum(t['senate2024special']['county'][r['county']]))for r in native]
    # Both examples are explicit assumptions; stressed field illustrates losing to a third choice.
    for name,others in [('three_other_choices_1percent_each',{'Chuck Conboy':.01,'Mike Marvin':.01,'Robin Richards':.01}),('stress_Conboy55percent',{'Chuck Conboy':.55,'Mike Marvin':.01,'Robin Richards':.01})]:
     otherfraction=sum(others.values());P=sum(r['T']for r in rows);V=P/(1-otherfraction)
     # Solve both pair margin and +1 final all-candidate margin; then assess all5 totals.
     for target,margin in [('tie_Ricketts',0),('Osborn_plus1_pair',.01),('Osborn_plus1_all_candidate',.01/(1-otherfraction))]:
      out=targets(rows,margin);units=out.pop('rows');OA=sum(r['T']*r['target_share']for r in units);RB=P-OA
      scores={'Dan Osborn':OA,'Pete Ricketts':RB,**{k:V*v for k,v in others.items()}}
      largest=max(scores.values());winners=[k for k,v in scores.items()if abs(v-largest)<1e-7]
      # Under uniform other fractions, any feasible A must also beat each other candidate.
      legal_A_tie_boundary=max(P/2,max(V*v for v in others.values()));legal_pair_margin=(2*legal_A_tie_boundary-P)/P
      legal=targets(rows,legal_pair_margin)if legal_pair_margin<=1 else dict(status='impossible_target_margin')
      legal.pop('rows',None)
      sid=f'{geo}__{anchor}__{mix}__{name}__{target}'
      for r in units:current_detail.append(dict(scenario=sid,**r,final_valid_volume=r['T']/(1-otherfraction),Conboy=r['T']/(1-otherfraction)*others['Chuck Conboy'],Marvin=r['T']/(1-otherfraction)*others['Mike Marvin'],Richards=r['T']/(1-otherfraction)*others['Robin Richards']))
      current.append(dict(scenario=sid,geography=geo,historical_preference_anchor=anchor,mix=mix,target=target,
       explicit_candidate_transport_assumption=f'2026 Dan Osborn vs Pete Ricketts pair share assumed equal to {ANCHORS[anchor][0]} vs {ANCHORS[anchor][2]} historical share before the stated shift; no candidate effect inferred',
       other_final_share_assumptions=others,pair_volume=P,final_all_candidate_denominator=V,
       eligible_writein_assumption='zero in this illustrative example only; actual universe unaudited',candidate_totals=scores,
       unique_highest=winners[0]if len(winners)==1 else None,tie_highest=winners if len(winners)>1 else[],
       pair_margin_pp=100*(OA-RB)/P,all_candidate_margin_pp=100*(OA-RB)/V,
       legal_Osborn_tie_boundary_votes=legal_A_tie_boundary,legal_pair_share_boundary=legal_A_tie_boundary/P,
       legal_bounded_shift=legal,arithmetic=out,forecast=False))
 j('scenarios/current-five-choice.json',current);jl('scenarios/current-five-choice-units.jsonl.gz',current_detail)
 # Meaningful synthetic stress cases, each with the actual named five-choice identity frame.
 roster=['Chuck Conboy','Mike Marvin','Robin Richards'];co={k:0 for k in roster};ro={k:0 for k in roster}
 default=dict(synthetic=True,candidate_A='Dan Osborn',candidate_B='Pete Ricketts',counted_A=400,counted_B=500,counted_others=co,remaining_pair=200,remaining_others=ro,remaining_A_share=.75,assumptions='invented counts/pools only; every counted value fixed; no calibrated probability')
 cases=[('ordinary',{}),('unknown_pool',{'remaining_pair':None}),('unknown_other_pool',{'remaining_others':None}),('no_pool_tie',{'remaining_pair':0,'counted_A':500}),('no_pool_secured',{'remaining_pair':0,'counted_A':700}),('negative_pool',{'remaining_pair':-1}),('impossible',{'remaining_pair':50}),('secured',{'counted_A':1000,'remaining_pair':50}),('clip_high',{'remaining_A_share':1.4}),('clip_low',{'remaining_A_share':-.3}),('unknown_preference',{'remaining_A_share':None}),('third_candidate_wins_despite_pair_lead',{'counted_others':{'Chuck Conboy':900,'Mike Marvin':10,'Robin Richards':10}}),('nonzero_other_remaining_final_denominator',{'remaining_others':{'Chuck Conboy':70,'Mike Marvin':20,'Robin Richards':10}}),('selected_unit',{'remaining_units':[{'key':'first','remaining_pair':50,'A_share':.2},{'key':'selected','remaining_pair':150,'A_share':.8}],'selected_unit':'selected'}),('unknown_unit',{'remaining_units':[{'key':'unknown','remaining_pair':None,'A_share':.5}],'selected_unit':'unknown'}),('selected_no_pool',{'remaining_units':[{'key':'fixed','remaining_pair':200,'A_share':.9},{'key':'selected','remaining_pair':0,'A_share':.5}],'selected_unit':'selected'})]
 for name,change in cases:
  inp={**default,**change};j(f'scenarios/live-{name}.json',inp);synthetic.append(dict(name=name,input=inp,output=live(inp)))
 j('scenarios/live-results.json',synthetic)
 targetcases=[('clipping',[dict(key='high',T=90,q=.99),dict(key='low',T=10,q=.01)],0),('already_winning',[dict(key='one',T=100,q=.7)],0),('no_positive',[dict(key='zero',T=0,q=None)],0),('unknown_anchor',[dict(key='unknown',T=100,q=None)],0),('negative',[dict(key='negative',T=-10,q=.5)],0),('impossible_margin',[dict(key='one',T=100,q=.4)],1.1),('clip_anchor',[dict(key='outside',T=100,q=1.5)],0)]
 j('scenarios/target-edge-cases.json',[dict(name=name,rows=rows,margin=margin,output=targets(rows,margin))for name,rows,margin in targetcases])
 j('settings.json',dict(anchors={k:dict(A=v[0],A_identity=v[1],B=v[2],B_identity=v[3])for k,v in ANCHORS.items()},historical_volume_sensitivity=settings,
  native_preferences='Only special2024 complete statewide; other native comparators available in separate local extracts, never silently imputed statewide',
  target_margin_fractions=[0,.01],selected_only_assumption='all every other unit at explicit scenario baseline q,T, including nonpriority units',
  unknown_special_generic_writeins=None,nonpriority_included=True,probability_calibrated=False,actual_2026_turnout_projection=False))
 print(json.dumps(dict(historical_state_targets=len(state),historical_unit_targets=len(detail),modern_scenarios=len(current),modern_unit_rows=len(current_detail),live_cases=len(synthetic))))
if __name__=='__main__':main()
