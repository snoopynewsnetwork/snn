#!/usr/bin/env python3
"""Build all-native and all-county baselines and historical sensitivities offline."""
import csv,gzip,json,pathlib
from calculate import solve
BASE=pathlib.Path(__file__).resolve().parent
def load(p):
    b=(BASE/p).read_bytes();return json.loads(gzip.decompress(b) if p.endswith('.gz') else b)
def save(p,d):
    b=(json.dumps(d,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode();(BASE/p).write_bytes(gzip.compress(b,mtime=0) if p.endswith('.gz') else b)
PAIRS={2024:['Kamala D. Harris','Donald J. Trump'],2022:['Will Boyd','Katie Britt'],2020:['Doug Jones','Tommy Tuberville']}
def candidates(year,rows):
    rr=next(x for x in rows if x['year']==year)['candidate_rows']
    return [{'id':r['candidate_literal'].strip(),'name':r['candidate_literal'].strip(),'party':r['party_literal'].strip(),'scope':'generic_write_in' if r['candidate_literal'].strip()=='Write-In' else 'named'} for r in rr]
def vector(u,cs):
    d={r['candidate_literal'].strip():r['votes'] for r in u['candidate_rows']}
    assert len(d)==len(cs)
    return [d[c['id']] for c in cs]
def baseline_row(u,cs,pair):
    v=vector(u,cs);assert all(type(x) is int for x in v)
    a,b=[v[[c['id'] for c in cs].index(n)] for n in pair];p=a+b;f=sum(v)
    return {'key':u['key'],'year':u['year'],'county':u['county'],'county_fips':u['county_fips'],'native_header_literal':u.get('native_header_literal'),'source_member':u['member'],'member_sha256':u['member_sha256'],'source_column':u.get('source_column'),'pair_a':pair[0],'pair_b':pair[1],'a_votes':a,'b_votes':b,'pair_votes':p,'all_candidate_votes':f,'other_votes':f-p,'pair_participation':p/f if f else None,'a_pair_share':a/p if p else None,'pair_margin_fraction':(a-b)/p if p else None,'all_candidate_pair_margin_fraction':(a-b)/f if f else None,'historical_leader':'tie' if a==b else (pair[0] if a>b else pair[1]),'closeness_band_pair_margin':'undefined' if not p else ('within_5pp' if abs((a-b)/p)<=.05 else ('5_to_10pp' if abs((a-b)/p)<=.1 else 'over_10pp')),'candidate_votes':[{'candidate':c, 'votes':n} for c,n in zip(cs,v)],'administrative_rows':u['administrative_rows'],'source_scope':'official historical XLS numeric observations; no current geography equivalence'}
def main():
    native=load('source/native-observations.json.gz');county=load('source/county-observations.json');canvass=load('source/canvass-county-cells.json');ballots=load('source/ballot-registration-controls.json');inventory=load('source/independent-inventory.json')
    baselines={};countyrows=[];nativerows=[];admin=[];state=[]
    for y in [2024,2022,2020]:
        cs=candidates(y,county);nrows=[baseline_row(u,cs,PAIRS[y]) for u in native if u['year']==y];crows=[baseline_row(u,cs,PAIRS[y]) for u in county if u['year']==y]
        for r in crows:
            cv=next(x for x in canvass if x['year']==y and x['county_fips']==r['county_fips']);br=next(x for x in ballots if x['year']==y and x['county_fips']==r['county_fips']);r['canvass_candidate_cells']=cv['candidate_cells'];r['canvass_pdf_page']=cv['pdf_page_1based'];r['ballot_registration_control']=br
            cu=next(x for x in county if x['year']==y and x['county_fips']==r['county_fips'])
            def ad(name):
                rr=[x for x in cu['administrative_rows'] if x['field_literal'].strip().lower()==name.lower() and (name not in ('Over Votes','Under Votes') or x['contest_literal'].strip() in ('UNITED STATES SENATOR','PRESIDENT AND VICE PRESIDENT OF THE UNITED STATES'))]
                return rr[0]['complete_sum'] if len(rr)==1 else None
            bb=ad('Ballots Cast - Total');reg=ad('Registered Voters - Total');over=ad('Over Votes');under=ad('Under Votes');blank=ad('Ballots Cast - Blank')
            admin.append({'year':y,'county_fips':r['county_fips'],'county':r['county'],'native_count':cu['native_count'],'native_ballots_complete':bb,'published_county_ballots':br['ballots_cast'],'native_minus_published_ballots':None if bb is None else bb-br['ballots_cast'],'native_registered_complete':reg,'published_registered':br['registered_voters'],'native_registration_zero_is_not_coverage':reg==0,'native_blank_ballots':blank,'contest_over_complete':over,'contest_under_complete':under,'ballots_minus_contest_over_under':None if any(x is None for x in (bb,over,under)) else bb-r['all_candidate_votes']-over-under,'missing_field_rows':[f for f in ['Over Votes','Under Votes','Ballots Cast - Blank'] if ad(f) is None and not any(x['field_literal'].strip()==f and (f=='Ballots Cast - Blank' or x['contest_literal'].strip() in ('UNITED STATES SENATOR','PRESIDENT AND VICE PRESIDENT OF THE UNITED STATES')) for x in cu['administrative_rows'])],'unknown_cells':[x for x in cu['administrative_rows'] if x['unknown_cells']>0],'registration_definition':br['registration_definition']})
        state.append({'year':y,'pair':PAIRS[y],'a':sum(r['a_votes'] for r in crows),'b':sum(r['b_votes'] for r in crows),'other':sum(r['other_votes'] for r in crows),'full':sum(r['all_candidate_votes'] for r in crows),'a_leading_counties':[r['county'] for r in crows if r['a_votes']>r['b_votes']],'candidate_controls':next(x['candidate_controls'] for x in inventory if x['year']==y)})
        baselines[y]={'native':nrows,'county':crows,'candidates':cs};nativerows+=nrows;countyrows+=crows
    save('native-baselines.json.gz',nativerows);save('county-baselines-complete.json.gz',countyrows);save('administrative-reconciliation.json',admin);save('state-baselines.json',state)
    # Compatibility CSV is long by election; nested candidates and exact source
    # administrative fields are strict JSON strings, not discarded identities.
    with (BASE.parent/'county-baselines.csv').open('w',newline='') as f:
        cols=list(countyrows[0]);w=csv.DictWriter(f,cols);w.writeheader()
        for row in sorted(countyrows,key=lambda r:(r['county_fips'],-r['year'])):w.writerow({k:json.dumps(v,ensure_ascii=False,allow_nan=False,separators=(',',':')) if isinstance(v,(dict,list)) else v for k,v in row.items()})
    # Each native electorate is independent: NO cross-year native join.
    settings=[]
    for y,level in [(2024,'native'),(2022,'native'),(2020,'native'),(2024,'county'),(2022,'county'),(2020,'county')]:
        settings.append({'id':f'{level}-{y}-own-history','level':level,'preference_year':y,'volume_year':y,'volume_basis':'all named plus generic contest votes in each original unit','mix':'own election native units' if level=='native' else 'own election county mix','label':{2022:'low',2024:'base',2020:'high'}[y]+' observed historical volume and preference anchor','join':'none'})
    # Separate scale-only native tests retain 2024 identities, pair participation,
    # preferences and mix; only the statewide observed historical total is used.
    fulls={s['year']:s['full'] for s in state}
    for y in [2022,2020]:settings.append({'id':f'native-2024-mix-scaled-to-{y}-total','level':'native','preference_year':2024,'volume_year':y,'volume_basis':f'2024 unit all-candidate counts scaled by observed {y}/2024 statewide contest totals','mix':'2024 source-native mix','label':{2022:'low',2020:'high'}[y]+' scale-only sensitivity','join':'none; scalar statewide total only'})
    for y in [2022,2020]:settings.append({'id':f'county-2024-preferences-{y}-mix-volume','level':'county','preference_year':2024,'volume_year':y,'volume_basis':f'observed {y} county all-candidate contest votes with 2024 county pair participation/preferences','mix':f'{y} all-candidate county mix','label':{2022:'low',2020:'high'}[y]+' county composition sensitivity','join':'Census county FIPS; administrative parent only, no native equivalence'})
    save('scenario-settings.json',settings)
    summaries=[]
    for s in settings:
        y=s['preference_year'];level=s['level'];rows=baselines[y][level];cs=baselines[y]['candidates']
        units=[]
        for row in rows:
            vol=row['all_candidate_votes']
            if s['volume_year']!=y:
                if level=='native':vol*=fulls[s['volume_year']]/fulls[y]
                else:vol=next(r['all_candidate_votes'] for r in baselines[s['volume_year']]['county'] if r['county_fips']==row['county_fips'])
            units.append({'key':row['key'],'votes':[x['votes'] for x in row['candidate_votes']],'volume':vol})
        for target,label in [(0,'tie'),(.01,'a-plus-1-pair-margin')]:
            data={'mode':'historical','candidates':cs,'pair':PAIRS[y],'units':units,'target_pair_margin':target,'scope':s['id'],'assumptions':json.dumps(s,sort_keys=True)+'; every nonpriority unit retained; original nonpair allocations held fixed; not 2026 forecast'}
            output=solve(data);name=s['id']+'-'+label;save('scenarios/'+name+'.input.json.gz',data);save('scenarios/'+name+'.result.json.gz',output)
            summaries.append({'scenario':s['id'],'target':label,'units':len(units),'pair':PAIRS[y],'full_candidate_volume':output['final_full_candidate_denominator'],'pair_volume':output['final_pair_denominator'],'baseline_pair_net':output['baseline_pair_net_votes'],'baseline_pair_margin_fraction':output['baseline_pair_margin_fraction'],'target_pair_net':output['target_pair_net_votes'],'unbounded_shift_share_points':output['common_shift']['unbounded_share_shift']*100,'bounded_shift_share_points':output['common_shift']['bounded_share_shift']*100,'clipping_applied':output['common_shift']['clipping_applied'],'target_net_over_full_candidate_denominator':output['same_net_full_candidate_margin_fraction'],'residual':output['common_shift']['residual_net_votes']})
    save('state-scenarios.json',summaries)
    # Complete per-native and parent order/priority/remainder arrays remain in
    # original independent inventory. Add explicit all67 parent constituent sets.
    parents=[];iv=next(x for x in inventory if x['year']==2024)['native'];priority=set(iv['priority_keys'])
    for cf in iv['all67_parents']:
        rr=sorted([u for u in native if u['year']==2024 and u['county_fips']==cf],key=lambda u:u['key']);parents.append({'county_fips':cf,'county':rr[0]['county'],'full_keys':[u['key'] for u in rr],'priority_keys':[u['key'] for u in rr if u['key'] in priority],'remainder_keys':[u['key'] for u in rr if u['key'] not in priority],'votes':sum(u['reported_contest_votes'] for u in rr)})
    save('all67-parent-contract.json',parents)
    contributions=[]
    nbase=baselines[2024]['native']; lookup={r['key']:r for r in nbase}
    for label in ['tie','a-plus-1-pair-margin']:
        result=load('scenarios/native-2024-own-history-'+label+'.result.json.gz')
        for p in parents:
            us=[u for u in result['units'] if u['key'] in set(p['full_keys'])];pair=sum(u['pair_pool'] for u in us);net=sum(u['target_remaining_pair_net'] for u in us);baseline=sum(u['baseline_remaining_pair_net'] for u in us)
            contributions.append({'target':label,'county':p['county'],'county_fips':p['county_fips'],'native_keys':p['full_keys'],'native_count':len(us),'pair_votes':pair,'all_candidate_votes':p['votes'],'state_pair_weight':pair/result['final_pair_denominator'],'baseline_net':baseline,'target_net':net,'net_gain':net-baseline,'target_pair_a_share':(net/pair+1)/2 if pair else None,'one_share_point_net_gain':.02*pair,'selected_county_only_required_a_share_raw':(result['target_pair_net_votes']-(result['baseline_pair_net_votes']-baseline)+pair)/(2*pair) if pair else None,'others_held_fixed':'all native units outside this county at their original 2024 shares and volumes; selected county pair share can vary freely','target_setting':'aggregate of primary clipped native common-share scenario, not a uniform county share shift'})
    save('parent-native-contributions.json',contributions)
    print(json.dumps({'county_rows':len(countyrows),'native_rows':len(nativerows),'scenarios':len(summaries),'state_baselines':state},indent=2))
if __name__=='__main__':main()
