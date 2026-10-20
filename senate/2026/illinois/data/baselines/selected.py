"""Offline selected county/native solve, holding every other unit explicitly fixed."""
import argparse,csv,json
from source_io import ROOT
from calculator import clip,selected_only,number
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--county-key');ap.add_argument('--native-key',help='Exact JSON unit_key from2024units');ap.add_argument('--others-share-shift-pp',type=float,default=0);ap.add_argument('--target-pair-margin-pp',type=float,default=0);a=ap.parse_args()
    if bool(a.county_key)==bool(a.native_key):ap.error('Choose exactly one county-key or native-key.')
    if not number(a.others_share_shift_pp)or not number(a.target_pair_margin_pp)or not -100<=a.target_pair_margin_pp<=100:
        print(json.dumps({'status':'invalid_scenario_parameters','expected':'Finite other share shift pp; finite target pair margin pp within[-100,100]'}));return
    if a.county_key:
        rows=[r for r in csv.DictReader((ROOT.parent/'county-baselines.csv').open())if r['year']=='2024'];units=[dict(key=r['county_key'],A=int(r['A']),B=int(r['B']))for r in rows]
        selected=a.county_key
    else:
        units=[dict(key=r['unit_key'],A=r['A'],B=r['B'])for r in json.loads((ROOT/'extract/2024-units.json').read_text())];selected=a.native_key
    matches=[r for r in units if r['key']==selected]
    if len(matches)!=1:ap.error('Unknown or nonunique source key.')
    u=matches[0]
    if u['A']is None or u['B']is None:print(json.dumps({'status':'unknown_source_pair_no_assigned_pool','observed':u}));return
    net=0;T=0
    for r in units:
        if r['A']is None or r['B']is None:continue # Only administrative observations for2024, retained in inventory.
        t=r['A']+r['B'];T+=t
        if r['key']!=selected and t>0:net+=t*(2*clip(r['A']/t+a.others_share_shift_pp/100)-1)
    result=selected_only(u['A']+u['B'],net,T,a.target_pair_margin_pp/100)
    print(json.dumps({'selected_key':selected,'all_units':len(units),'base':'2024 historical recorded pair votes','others_share_shift_pp':a.others_share_shift_pp,'others_shares_clipped_to':[0,1],'pair_denominator':T,'all_other_net_fixed':net,'target_pair_margin_pp':a.target_pair_margin_pp,**result},indent=2))
if __name__=='__main__':main()
