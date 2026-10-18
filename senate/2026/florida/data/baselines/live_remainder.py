#!/usr/bin/env python3
"""Offline conditional arithmetic, no feed/remaining estimate/probability calibration.
Input counts are all-candidate CONTEST votes, never ballots. Counted votes remain fixed.
"""
import argparse,json,math
from pathlib import Path
from calculate import clip,selected_threshold
D=Path(__file__).resolve().parent

def calculate(x):
 counted=x.get('counted',{});A=x.get('A','A');B=x.get('B','B');out={'id':x.get('id'),'A':A,'B':B,'counted_fixed':counted,'arithmetic_only':True}
 if A==B or A not in counted or B not in counted:return {**out,'status':'invalid_candidate_mapping'}
 if any(not isinstance(n,(float,int)) or not math.isfinite(n) or n<0 for n in counted.values()):return {**out,'status':'invalid_negative_or_nonfinite_counted'}
 pools=x.get('remaining')
 if pools is None:return {**out,'status':'unknown_remaining_pool','final_denominator':None,'required_A_pair_share':None}
 remaining_all=0.;U=0.;qknown=True;allknown=True;projected=dict(counted);entries=[]
 for p in pools:
  n=p.get('contest_votes');part=p.get('pair_fraction');q=p.get('A_pair_share')
  if n is None or part is None:return {**out,'status':'unknown_remaining_pool_or_participation','final_denominator':None,'required_A_pair_share':None}
  if not all(isinstance(v,(float,int)) and math.isfinite(v) for v in [n,part]) or n<0 or not 0<=part<=1:return {**out,'status':'invalid_remaining_pool','final_denominator':None}
  remaining_all+=n;t=n*part;U+=t;clipped=False
  if q is None and t>0:qknown=False
  elif q is not None:
   if not isinstance(q,(float,int)) or not math.isfinite(q):return {**out,'status':'invalid_share'}
   clipped=q!=clip(q);q=clip(q)
  else:q=.5
  others=p.get('other_allocation',{})
  if n-t>1e-9:
   if not others:allknown=False
   elif any(k in [A,B] or not isinstance(v,(float,int)) or not math.isfinite(v) or v<0 for k,v in others.items()) or abs(math.fsum(others.values())-1)>1e-10:return {**out,'status':'invalid_other_allocation'}
  entry={'pool_id':p['id'],'remaining_contest_votes':n,'pair_fraction':part,'pair_votes':t,'A_pair_share_input':p.get('A_pair_share'),'A_pair_share_used':q,'share_was_clipped':clipped,'other_allocation':others};entries.append(entry)
  if q is not None:projected[A]+=t*q;projected[B]+=t*(1-q)
  for k,fraction in others.items():projected[k]=projected.get(k,0)+(n-t)*fraction
 F=math.fsum(counted.values())+remaining_all;P=counted[A]+counted[B]+U;g=x.get('target_margin_pp',0)/100;denom=x.get('target_denominator','pair')
 if denom not in ['pair','all']:return {**out,'status':'invalid_target_denominator'}
 target_net=g*(P if denom=='pair' else F);L=counted[A]-counted[B];req=selected_threshold(U,L,target_net)
 out.update({'remaining_pools':entries,'remaining_contest_votes':remaining_all,'remaining_pair_votes':U,'final_denominator':F,'final_pair_denominator':P,'target_denominator':denom,'target_margin_pp':100*g,'target_net_votes':target_net,'counted_A_minus_B':L,'required_A_pair_share':req['required_share_unbounded'],'required_A_pair_share_clipped':req['clipped_share'],'threshold_status':req['status'],'strict_pair_win_requires':'greater than tie threshold; target cushion meets specified net margin, not statutory threshold'})
 if x.get('selected_pool'):
  matches=[p for p in entries if p['pool_id']==x['selected_pool']]
  if len(matches)!=1:return {**out,'status':'invalid_selected_pool'}
  selected=matches[0];others=[p for p in entries if p!=selected]
  if any(p['A_pair_share_used'] is None and p['pair_votes']>0 for p in others):out['selected_only']={'status':'unknown_other_pool_preference'}
  else:
   other_net=L+math.fsum(p['pair_votes']*(2*p['A_pair_share_used']-1) for p in others);conditional=selected_threshold(selected['pair_votes'],other_net,target_net);conditional['other_counted_and_remaining_net_fixed']=other_net
   # Other-candidate plurality thresholds, with their explicit remaining allocation fixed.
   if allknown and selected['pair_votes']>0:
    a_without=counted[A]+math.fsum(p['pair_votes']*p['A_pair_share_used'] for p in others);thresholds={k:(n-a_without)/selected['pair_votes'] for k,n in projected.items() if k not in [A,B]};conditional['required_share_to_tie_each_other']=thresholds;conditional['plurality_required_share_unbounded']=max([conditional['required_share_unbounded']]+list(thresholds.values()));conditional['plurality_threshold_is_strict_for_outright_win']=True
   out['selected_only']=conditional
 if not qknown:return {**out,'status':'unknown_remaining_preference','projected_candidates':None,'legal_plurality_outcome':'unknown'}
 if not allknown:return {**out,'status':'unknown_other_candidate_allocation','projected_candidates':None,'legal_plurality_outcome':'unknown'}
 leader=max(projected.values());winners=[k for k,n in projected.items() if abs(n-leader)<1e-8];lead=projected[A]-projected[B]
 out.update({'status':'no_pool' if remaining_all==0 else 'calculated','projected_candidates':projected,'projected_A_minus_B':lead,'projected_pair_margin_pp':100*lead/P if P>0 else None,'projected_all_candidate_margin_pp':100*lead/F if F>0 else None,'projected_A_all_candidate_share':projected[A]/F if F>0 else None,'legal_plurality_outcome':'no_votes' if F==0 else 'tie_requires_legal_resolution' if len(winners)>1 else winners[0],'target_met':lead>=target_net-1e-8,'final_candidate_sum_residual':math.fsum(projected.values())-F})
 return out

def examples():
 base={'A':'Synthetic A','B':'Synthetic B','counted':{'Synthetic A':400,'Synthetic B':500,'Named independent':100}}
 items=[{**base,'id':'unknown_pool','remaining':None},{**base,'id':'negative_pool','remaining':[{'id':'x','contest_votes':-5,'pair_fraction':1,'A_pair_share':.5}]},{**base,'id':'no_pool_lost','remaining':[]},{**base,'id':'unknown_preference','remaining':[{'id':'x','contest_votes':200,'pair_fraction':1,'A_pair_share':None}]},{**base,'id':'impossible','remaining':[{'id':'x','contest_votes':50,'pair_fraction':1,'A_pair_share':1}]},{**base,'id':'clipped_high','remaining':[{'id':'x','contest_votes':500,'pair_fraction':.8,'A_pair_share':1.2,'other_allocation':{'Named independent':1}}]},{**base,'id':'clipped_low','remaining':[{'id':'x','contest_votes':500,'pair_fraction':1,'A_pair_share':-.2}]},{**base,'id':'no_positive_pair_pool','remaining':[{'id':'x','contest_votes':100,'pair_fraction':0,'A_pair_share':None,'other_allocation':{'Named independent':1}}]},{**base,'id':'secured','counted':{'Synthetic A':700,'Synthetic B':500,'Named independent':100},'remaining':[{'id':'x','contest_votes':50,'pair_fraction':1,'A_pair_share':0}]},{**base,'id':'no_pool_tie','counted':{'Synthetic A':500,'Synthetic B':500,'Named independent':100},'remaining':[]},{**base,'id':'all_zero','counted':{'Synthetic A':0,'Synthetic B':0},'remaining':[]},{**base,'id':'other_wins','counted':{'Synthetic A':400,'Synthetic B':300,'Named independent':1000},'remaining':[{'id':'x','contest_votes':100,'pair_fraction':1,'A_pair_share':1}],'selected_pool':'x'},{**base,'id':'selected_pool_final_all_denominator','target_margin_pp':1,'target_denominator':'all','selected_pool':'county-C','remaining':[{'id':'county-C','contest_votes':1000,'pair_fraction':.8,'A_pair_share':.6,'other_allocation':{'Named independent':1}},{'id':'other66','contest_votes':500,'pair_fraction':.9,'A_pair_share':.4,'other_allocation':{'Named independent':1}}]},{**base,'id':'unknown_other_identity','remaining':[{'id':'x','contest_votes':100,'pair_fraction':.8,'A_pair_share':.5}]},{**base,'id':'invalid_negative_counted','counted':{'Synthetic A':-1,'Synthetic B':500},'remaining':[]}]
 (D/'synthetic-live-inputs.json').write_text(json.dumps(items,indent=2)+'\n');outputs=[calculate(x) for x in items];(D/'synthetic-live-results.json').write_text(json.dumps(outputs,indent=2,allow_nan=False)+'\n');return outputs
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path);p.add_argument('--examples',action='store_true');a=p.parse_args()
 if a.examples:examples();print('15 synthetic arithmetic cases saved; no calibrated probabilities.')
 elif a.input:
  x=json.loads(a.input.read_text());print(json.dumps([calculate(z) for z in x] if isinstance(x,list) else calculate(x),indent=2,allow_nan=False))
 else:p.error('--input JSON or --examples required')
