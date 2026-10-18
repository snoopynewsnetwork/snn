#!/usr/bin/env python3
"""Independent event-slope target solver and original candidate/contribution audit."""
from pathlib import Path
import collections,csv,datetime,gzip,hashlib,io,json,math,runpy

ROOT=Path(__file__).resolve().parents[1];D=ROOT/'data';B=D/'baselines'
load=lambda p:json.loads(p.read_text())
def rows(p):return list(csv.DictReader(io.StringIO(gzip.decompress(p.read_bytes()).decode()if p.suffix=='.gz'else p.read_text())))
def near(a,b):assert math.isclose(float(a),float(b),rel_tol=2e-10,abs_tol=2e-6),(a,b)
def clip(x):return max(0.,min(1.,x))
def solve(shares,weights,goal):
    total=math.fsum(weights);assert total>0 and -total<=goal<=total
    events=collections.defaultdict(float)
    for s,w in zip(shares,weights):events[-s]+=2*w;events[1-s]-=2*w
    current=-1.;net=-total;slope=0.
    for x in sorted(events):
        following=net+slope*(x-current)
        if slope>0 and net-1e-7<=goal<=following+1e-7:return current+(goal-net)/slope
        current=x;net=following;slope+=events[x]
    raise AssertionError('No bounded solution')

def main():
    manifest_bytes=(B/'asset-manifest.json').read_bytes()
    assert hashlib.sha256(manifest_bytes).hexdigest()=='a8d9c6698ca551efca6b84f91a28b65f428b17efa484e193a714fba1d5cae735'
    manifest=load(B/'asset-manifest.json');assert len(manifest['owned_files'])==73
    for item in manifest['owned_files']:
        body=(ROOT/item['path']).read_bytes()
        assert len(body)==item['bytes']<40000000 and hashlib.sha256(body).hexdigest()==item['sha256'],item['path']
    for item in manifest['source_references']:
        body=(ROOT/item['path']).read_bytes()
        assert len(body)==item['stored_bytes'] and hashlib.sha256(body).hexdigest()==item['stored_sha256'],item['path']
        original=gzip.decompress(body)
        assert len(original)==item['original_bytes'] and hashlib.sha256(original).hexdigest()==item['original_sha256'],item['path']
    # This helper is coordinator-authored and reads original ZIP/XML, not worker extracts.
    ns=runpy.run_path(str(D/'review_priority.py'));source={}
    for year in [2024,2022,2020]:
        rs=ns['workbook'](f'sos-{year}-precinct-original')['Precinct-Results']
        # Header addresses use actual column letters; remove row digits, never numeric cell positions.
        import re
        header={re.sub(r'\d+$','',k):v['value']for k,v in rs[0]['cells'].items()}
        rr={}
        for r in rs[1:]:
            v={header[re.sub(r'\d+$','',k)]:x['value']for k,x in r['cells'].items()}
            if v.get('VTDID')and re.fullmatch(r'\d{9}',v['VTDID']):rr[str(r['source_row'])]=v
        source[year]=rr
    baselines={};counts={};candidate_checks=0
    for level,path in [('county',D/'county-baselines.csv'),('native',B/'native-baselines.csv.gz'),('municipal',B/'municipal-baselines.csv.gz')]:
        rr=rows(path);counts[level]=len(rr)
        baselines[level]={(r['contest'],r['unit_key']):r for r in rr}
        assert len(rr)==len(baselines[level])
    for r in baselines['native'].values():
        raw=source[int(r['year'])][r['source_row']];prefix=r['A_field'].removesuffix('DFL')
        allv=sum(int(v)for k,v in raw.items()if k.startswith(prefix)and k!=prefix+'TOTAL')
        a=int(raw[r['A_field']]);b=int(raw[r['B_field']]);other=allv-a-b
        for key,value in [('A',a),('B',b),('other',other),('all_candidate_votes',allv),('pair_votes',a+b),('net_A_minus_B',a-b)]:assert int(r[key])==value;candidate_checks+=1
        assert r['A_source_party']=='Democratic-Farmer-Labor'and r['B_source_party']=='Republican'
        assert r['VTDID']==raw['VTDID']and r['MCDNAME']==raw['MCDNAME']and r['PCTNAME']==raw['PCTNAME']
    for level in ['county','municipal']:
        sums=collections.defaultdict(lambda:collections.Counter())
        for r in baselines['native'].values():
            key='MN:county:'+r['county_fips']if level=='county'else json.dumps([int(r['year']),r['county_fips'],r['MCDNAME']],separators=(',',':'))
            for k in ['A','B','other','all_candidate_votes','pair_votes']:sums[(r['contest'],key)][k]+=int(r[k])
        assert set(sums)==set(baselines[level])
        for key,value in sums.items():
            for k,v in value.items():assert int(baselines[level][key][k])==v;candidate_checks+=1
    states=load(B/'state-scenarios.json');state_index={(r['scenario'],r['contest'],r['level'],r['target']):r for r in states};assert len(state_index)==len(states)==64
    groups=collections.defaultdict(list)
    for level in ['county','native','municipal']:
        for r in rows(B/(level+'-targets.csv.gz')):groups[(r['scenario'],r['contest'],level,r['target'])].append(r)
    assert set(groups)==set(state_index)
    row_count=0;clipped_groups=0
    for key,rr in groups.items():
        scenario,contest,level,target=key;state=state_index[key];base=[baselines[level][(contest,r['unit_key'])]for r in rr]
        assert len(rr)==len({r['unit_key']for r in rr})==state['all_units']
        assert {r['unit_key']for r in rr}=={k[1]for k in baselines[level]if k[0]==contest}
        volume=[];weights=[];shares=[]
        for r,b in zip(rr,base):
            own=int(b['all_candidate_votes']);pair=int(b['pair_votes']);s=int(b['A'])/pair if pair else .5
            if scenario=='own-historical-volume':v=own;w=pair
            else:
                assert level=='county'
                if '-mix-volume'in scenario:
                    anchor={'low-2022-mix-volume':'2022-governor','base-2024-mix-volume':'2024-senate','high-2020-mix-volume':'2020-senate'}[scenario]
                    v=int(baselines[level][(anchor,r['unit_key'])]['all_candidate_votes'])
                else:
                    anchor='2022-governor'if scenario.startswith('low')else'2020-senate'
                    final=sum(int(x['all_candidate_votes'])for (c,k),x in baselines[level].items()if c==anchor)
                    initial=sum(int(x['all_candidate_votes'])for (c,k),x in baselines[level].items()if c=='2024-senate')
                    v=int(baselines[level][('2024-senate',r['unit_key'])]['all_candidate_votes'])*final/initial
                w=v*pair/own if own else 0
            volume.append(v);weights.append(w);shares.append(s)
            for k,vv in [('baseline_A',int(b['A'])),('baseline_B',int(b['B'])),('baseline_other',int(b['other'])),('scenario_all_votes',v),('scenario_pair_votes',w),('scenario_other_votes',v-w)]:near(r[k],vv)
        total=math.fsum(weights);allv=math.fsum(volume);net=math.fsum(w*(2*s-1)for w,s in zip(weights,shares));goal=0 if target=='tie'else .01*total;delta=solve(shares,weights,goal)
        near(state['pair_volume'],total);near(state['all_candidate_volume'],allv);near(state['baseline_net'],net);near(state['bounded_shift_share_pp'],delta*100);near(state['unbounded_shift_share_pp'],(goal-net)/(2*total)*100)
        near(state['target_net'],goal);near(sum(float(r['pair_weight'])for r in rr),1)
        clipped=0
        for r,w,s,v in zip(rr,weights,shares,volume):
            q=clip(s+delta);expected=w*(2*q-1);near(r['target_net'],expected);near(r['gain_net'],2*w*(q-s));near(r['plus1_share_pp_net_gain'],.02*w)
            near(r['plus1_share_pp_feasible_gain'],2*w*(clip(s+.01)-s));near(r['pair_weight'],w/total);near(r['all_vote_weight'],v/allv)
            if w:
                near(r['target_share'],q);othernet=net-w*(2*s-1);required=(w+goal-othernet)/(2*w);near(r['selected_others_net'],othernet);near(r['selected_required_raw_share'],required);near(r['selected_clipped_share'],clip(required))
                assert r['selected_status']==('already_secured'if required<0 else'impossible'if required>1 else'boundary'if required in[0,1]else'feasible')
            else:assert r['target_share']==''and r['selected_required_raw_share']==''
            clipped+=bool(w and not 0<=s+delta<=1);row_count+=1
        near(sum(float(r['target_net'])for r in rr),goal);assert clipped==state['clipped_units'];clipped_groups+=bool(clipped)
    bounded_cases=load(B/'bounded-solver-cases.json')
    for r in bounded_cases:
        c=r['input'];o=r['output'];ss=c['shares'];ww=c['weights'];goal=c['target']
        if any(w<0 for w in ww):assert o['status']=='invalid_weights_or_target';continue
        if any(s is None for s in ss):assert o['status']=='unknown_or_invalid_preference';continue
        if not sum(ww):assert o['status']=='no_positive_pool';continue
        if abs(goal)>sum(ww):assert o['status']=='impossible';continue
        delta=solve(ss,ww,goal);near(o['bounded_shift'],delta)
        clipped=sum(w>0 and not 0<=s+delta<=1 for s,w in zip(ss,ww));assert o['clipped_units']==clipped
        if c['id']=='clipping-required':assert clipped>0
    examples=load(B/'live-scenarios-output.json')
    for r in examples:
        spec=r['input'];units=spec['units'];A=spec['A'];Bkey=spec['B']
        assert r['counted_held_fixed']
        if r['status']in ['unknown_remaining_pool','invalid_negative_or_nonfinite_pool','invalid_duplicate_units']:continue
        counted=collections.Counter()
        for u in units:counted.update(u['counted'])
        assert dict(counted)==r['counted_totals']
        total_remaining=sum(u['remaining_all']for u in units);remaining_pair=sum(u['remaining_all']*u['pair_fraction']for u in units)
        final_all=sum(counted.values())+total_remaining;final_pair=counted[A]+counted[Bkey]+remaining_pair
        near(r['final_all_candidate_denominator'],final_all);near(r['final_pair_denominator'],final_pair)
        near(sum(r['final_candidate_totals'].values()),final_all)
        if remaining_pair:
            lead=counted[A]-counted[Bkey]
            for label,goal in [('tie',0),('Aplus1_final_pair_margin',.01*final_pair),('Aplus1_final_all_candidate_margin',.01*final_all)]:near(r['targets'][label]['raw_share'],(remaining_pair+goal-lead)/(2*remaining_pair))
        finals=r['final_candidate_totals'];assert r['A_strictly_exceeds_every_supplied_opponent']==all(finals[A]>v for k,v in finals.items()if k!=A)
    out={'status':'pass_final_frozen_baseline_assets_and_targets','reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'Independent original OOXML candidate sums, native-to-county/municipal controls, event-slope clipped solver and final-denominator remainder arithmetic; no worker calculator imported.','owned_asset_hashes':73,'shared_original_hashes':len(manifest['source_references']),'final_baseline_manifest_sha256':hashlib.sha256(manifest_bytes).hexdigest(),'final_baseline_report_sha256':hashlib.sha256((ROOT/'county-partisanship.md').read_bytes()).hexdigest(),'final_baseline_csv_sha256':hashlib.sha256((D/'county-baselines.csv').read_bytes()).hexdigest(),'baseline_rows':counts,'original_candidate_and_aggregate_checks':candidate_checks,'state_scenarios':64,'target_rows':row_count,'clipped_state_groups':clipped_groups,'bounded_solver_cases':len(bounded_cases),'synthetic_remainder_cases':len(examples),'scope':'Conditional historical arithmetic only; no probability calibration, future turnout assumption or legal/current crosswalk approval.'}
    p=D/'coordinator-target-review.json'
    if p.exists():
        old=load(p)
        if {k:v for k,v in old.items()if k!='reviewed_utc'}=={k:v for k,v in out.items()if k!='reviewed_utc'}:out['reviewed_utc']=old['reviewed_utc']
    p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))

if __name__=='__main__':main()
