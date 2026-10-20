#!/usr/bin/env python3
"""Independent offline source, arithmetic, coverage and asset checks; nonzero exit on failure."""
import argparse,collections,csv,gzip,hashlib,json,math,re
from pathlib import Path
D=Path(__file__).resolve().parent;STATE=D.parents[1];S=D/'source'
sha=lambda b:hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text())
def csvrows(p):return list(csv.DictReader(p.open()))
def owned():return sorted([STATE/'county-partisanship.md',D.parent/'county-baselines.csv',*[p for p in D.rglob('*')if p.is_file()and p!=D/'asset-manifest.json']])
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--audit',action='store_true');args=ap.parse_args();checks=0;fail=[]
    def ck(x,label):
        nonlocal checks
        checks+=1
        if not x:fail.append(label)
    def close(a,b,label,tol=1e-7):ck(abs(a-b)<tol,label)
    refs=load(S/'original-references.json')
    for r in refs+load(S/'fresh-observations.json'):
        p=STATE/r['asset'];z=p.read_bytes();b=gzip.decompress(z);ck(sha(z)==r['stored_sha256'],r['id']+' stored hash');ck(sha(b)==r['raw_sha256'],r['id']+' raw hash');ck(len(z)==r['stored_bytes'],r['id']+' stored bytes');ck(len(b)==r['bytes'],r['id']+' raw bytes');ck(len(z)<40000000,r['id']+' bound')
    for r in load(S/'independent-first-pin.json')['files']:
        b=(STATE/r['path']).read_bytes();ck(sha(b)==r['sha256']and len(b)==r['bytes'],'independent pin '+r['path'])
    E=load(D/'original-extract.json');expected={'2024-senate':(2201,30,36,[497333,405978]),'2020-senate':(1959,316,326,[474483,418483,24271]),'2022-governor':(2196,668,671,[370168,324701,17387]),'2024-president':(2202,9408,9408,[478802,423391,9553,4611,3745,2442,859])};fieldrows=csvrows(D/'candidate-fields.csv');pos=0;county_by={};state_by={}
    for k,v in E.items():
        cr=[r for r in v['rows']if r['scope']=='County'];nr=[r for r in v['rows']if r['scope']=='Precinct'];sr=v['rows'][0];county_by[k]={r['label_literal']:r for r in cr};state_by[k]=[c['value']for c in sr['cells'][2:-2]]
        ck(len(cr)==33,k+' counties');ck(len(nr)==expected[k][0],k+' native');ck(len({(r['county_literal'],r['label_literal'])for r in nr})==len(nr),k+' unique identities');ck(sum(r['administrative']for r in nr)==33,k+'33admin');ck(state_by[k]==expected[k][3],k+' full state field');ck(sum(c['masked']for r in nr for c in r['cells'][2:-2])==expected[k][1],k+' candidate masks');ck(sum(c['masked']for r in nr for c in r['cells'][2:])==expected[k][2],k+' all masks')
        for j in range(2,len(v['headers'])):ck(sum(r['cells'][j]['value']for r in cr)==sr['cells'][j]['value'],k+' county/state column '+str(j))
        for r in v['rows']:
            ck(r['source_row']>=3,k+' source row');ck(len(r['raw_row'])==len(v['headers']),k+' source width');ck(r['native_id']is None,k+' no invented numeric nativeID')
            for j,c in enumerate(r['cells']):
                ck(c['column']==j+1 and c['literal']==r['raw_row'][j],k+' raw cell position');ck(c['header']==v['headers'][j]and c['party_literal']==v['parties'][j],k+'header/party');ck(c['masked']==(c['literal']=='*'),k+' mask');ck(c['value']==(int(c['literal'])if c['literal'].isdigit()else None),k+' numeric/missing')
                if j>=2:
                    f=fieldrows[pos];pos+=1
                    ck(f['contest']==k and int(f['source_row'])==r['source_row']and int(f['source_column'])==j+1 and f['literal']==c['literal']and f['field_label']==c['header']and f['party_literal']==c['party_literal'],k+' longform identity');ck(f['value']==(''if c['value']is None else str(c['value'])),k+' longform null/value')
    ck(pos==len(fieldrows)==50179,'all50179source positions')
    for name,county,label in [('zero-total masked','Chaves','47'),('privacy masked','Curry','Voter Privacy')]:
        r=next(r for r in E['2024-senate']['rows']if r['scope']=='Precinct'and r['county_literal']==county and r['label_literal']==label);ck(any(c['value']is None for c in r['cells'][2:4]),name+' candidates unknown')
    B=csvrows(D.parent/'county-baselines.csv');N=csvrows(D/'native-baselines.csv');ck(len(B)==132 and len(N)==8558,'complete baseline rows')
    for k in E:
        rs=[r for r in B if r['contest']==k];T=sum(state_by[k][:2]);V=sum(state_by[k]);close(sum(float(r['pair_weight_state'])for r in rs),1,k+'county weights');close(sum(float(r['all_candidate_weight_state'])for r in rs),1,k+'allcandidateweights')
        for r in rs:
            vals=[c['value']for c in county_by[k][r['county']]['cells'][2:-2]];ck(int(r['A'])==vals[0]and int(r['B'])==vals[1]and int(r['other'])==sum(vals[2:]),k+' baseline candidate balance');ck(int(r['all_candidate_votes'])==sum(vals)and int(r['pair_votes'])==sum(vals[:2]),k+'denominators');close(float(r['A_pair_share']),vals[0]/sum(vals[:2]),k+'share');close(float(r['pair_margin_pp']),100*(vals[0]-vals[1])/sum(vals[:2]),k+'margin');close(float(r['gain_net_per_A_share_pp']),.02*sum(vals[:2]),k+'gain')
    pdf=load(D/'pdf-county-controls.json');ck(sum(x['county_candidate_cells']for x in pdf['checks'])==495,'495 PDF cells')
    for k,vecs in pdf['vectors'].items():
        for j,r in enumerate(vecs):
            ck(sum(r['values'][:-1])==r['values'][-1]==state_by[k][j],k+' PDF statewide control')
            for c,v in zip(r['county_order'],r['values']):ck(county_by[k][c]['cells'][j+2]['value']==v,k+' original PDF county candidate')
    sc=load(D/'state-scenarios.json');ct=csvrows(D/'county-target-scenarios.csv');ck(len(sc)==32 and len(ct)==1056,'all county/state target cases');settings=load(D/'settings.json');ck(settings['volume_anchors']=={'low-2022-governor':'2022-governor','base-2024-senate':'2024-senate','high-2024-president':'2024-president','context-2020-same-seat':'2020-senate'},'volume declarations')
    for s in sc:
        rs=[r for r in ct if r['preference_anchor']==s['preference_anchor']and r['historical_volume_mix']==s['historical_volume_mix']and float(r['target_pair_margin_pp'])==s['target_margin_pp']];ck(len(rs)==33,'33 counties per case');T=sum(float(r['pair_volume'])for r in rs);V=sum(float(r['all_candidate_volume'])for r in rs);close(T,s['volume'],'scenario pair volume');close(V,s['all_candidate_volume'],'scenario all volume');close(sum(float(r['pair_weight'])for r in rs),1,'scenario weights');close(sum(float(r['target_net'])for r in rs),s['target_net'],'actual scenario target sum');close(s['solved_net'],s['target_margin_pp']/100*T,'bounded root');close(sum(float(r['net_gain'])for r in rs),s['net_gain'],'gains reconcile');close(s['all_candidate_target_margin_pp'],100*s['target_net']/V,'allcandidate target denominator');close(sum(s['other_candidate_expected_votes'].values())+T,V,'other candidate scope')
        for r in rs:
            vals=[c['value']for c in county_by[r['preference_anchor']][r['county']]['cells'][2:-2]];pool=sum(vals[:2]);allv=sum(vals);vol=sum(c['value']for c in county_by[r['volume_contest']][r['county']]['cells'][2:-2]);close(float(r['all_candidate_volume']),vol,'declared actual historical county volume');close(float(r['pair_participation']),pool/allv,'county pair participation');close(float(r['pair_volume']),vol*pool/allv,'pair implementation');q=float(r['target_A_pair_share']);ck(0<=q<=1,'bounded target share');close(q,max(0,min(1,float(r['baseline_A_pair_share'])+s['shift'])),'clipped implementation');close(float(r['target_net']),float(r['pair_volume'])*(2*q-1),'county target contribution');close(float(r['gain_net_per_A_share_pp']),.02*float(r['pair_volume']),'county gain');other=s['baseline_net']-float(r['pair_volume'])*(2*float(r['baseline_A_pair_share'])-1);req=(float(r['pair_volume'])+s['target_net']-other)/(2*float(r['pair_volume']));close(float(r['selected_only_unbounded_share']),req,'selected-only boundary');ck(r['selected_only_status']==('already_secured'if req<0 else ('impossible'if req>1 else 'feasible')),'selected feasibility status')
    nt=csvrows(D/'native-targets.csv');ns=load(D/'native-state-scenarios.json');ck(len(nt)==17116 and len(ns)==8,'complete native target rows')
    for s in ns:
        rs=[r for r in nt if r['contest']==s['contest']and float(r['target_pair_margin_pp'])==s['target']*100];ck(len(rs)==expected[s['contest']][0],'native unknown rows survive');close(sum(float(r['observed_universe_target_net'])for r in rs if r['observed_universe_target_net']!=''),s['target_net'],'observed-universe bounded root')
        for r in rs:
            ck(r['statewide_all_native_uniform_target_share']=='','unknown fullnative target remains null')
            if r['historical_pair_pool']=='':ck(r['observed_universe_target_share']==''and r['fullstate_selected_only_unbounded_share']==''and r['selected_status']=='unknown','unknown native selected remainsunknown')
            elif float(r['historical_pair_pool'])>0:ck(0<=float(r['observed_universe_target_share'])<=1,'native bounded share')
    orders=load(D/'source-scoped-orders.json');ck(len(orders)==18,'all18source orders')
    for name,o in orders.items():
        ck(len(o['full_order'])==o['unit_count']==len(set(o['full_order'])),name+' unique full order');ck(o['ordered_priority_keys']+o['ordered_remainder_keys']==o['full_order'],name+' complete nonpriority remainder');ck(5*o['minimum80_votes']>=4*o['denominator']and 5*o['preceding_votes']<4*o['denominator'],name+' minimum integer80')
    pri=load(D/'priority-contract.json')
    for k,v in pri.items():
        ck(v['canonical_dispatch_keys']==[]and v['certified_native_minimum80']is None and v['certified_native_order']is None,k+' certified native unavailable')
        for scope in ['county_sensitivity','observed_complete_candidate_rows_only']:
            o=v[scope];values=[r[o['field']]for r in o['ordered']];ck(values==sorted(values,reverse=True),k+' full descending');ck(sum(values)==o['denominator'],k+' order denominator');ck(5*o['minimum80_at']>=4*o['denominator']>5*o['minimum80_before'],k+' observed integer crossing')
    dis=load(D/'source-disagreements.json');ck(dis['ballots']['2020']['pdf_minus_portal']==-58,'2020 ballot discrepancy retained');ck(dis['2024_literal_key_president_only']==[['Otero','18']],'unmatched source scope preserved');ck(dis['registration_stocks']['2024-10-31']['state_report_total']==1377085 and dis['registration_stocks']['2024-10-31']['native_sum']==1376892,'registration source disagreement retained')
    peer=load(D/'peer-reconciliation.json');ck(peer['passed']and peer['checks']==376717 and not peer['failures'],'captured peer full comparison');ck(not peer['future_final_equality_claim']and not peer['coordinator_accepted'],'peer scope qualified')
    live=load(D/'live-synthetic-scenarios.json');ck(len(live)==14,'14meaningful live cases');ordinary=live['ordinary'];ck(ordinary['final']['A']==88 and ordinary['final']['B']==82 and ordinary['final']['other']=={'C':25},'live fixed counted plus remainder');ck(ordinary['final']['pair_denominator']==170 and ordinary['final']['all_candidate_denominator']==195,'live FINAL denominators');close(live['Aplus1_final_denominator']['pair_target']['required_share_unbounded'],.573125,'live +1 correct final denominator');ck(live['unknown_remaining']['status']=='unknown'and live['unknown_preference']['status']=='unknown','unknown live');ck(live['negative_pool']['status']=='invalid_negative_or_bounds','negative rejected');ck(live['secured']['pair_target']['status']=='already_secured'and live['impossible']['pair_target']['status']=='impossible','secured/impossible');ck(live['no_pool']['pair_target']['status']=='no_positive_pool'and live['no_pair_pool']['pair_target']['status']=='no_positive_pool','no pools');ck(live['clip_high']['clipped_preference']and live['clip_high']['used_remaining_A_pair_share']==1 and live['clip_low']['used_remaining_A_pair_share']==0,'clipping explicit');ck(live['other_candidate_wins']['final']['plurality_leaders']==['C']and not live['other_candidate_wins']['final']['A_outright_plurality'],'pair benchmark not legal outcome')
    for name,o in live.items():
        if o.get('final')is None:continue
        x=o['input'];f=o['final'];ck(o['fixed_counted_votes']=={'A':x['counted_A'],'B':x['counted_B'],'other':x['counted_other']},name+'counted fixed');close(f['A']+f['B'],f['pair_denominator'],name+'pair balance');close(f['pair_denominator']+sum(f['other'].values()),f['all_candidate_denominator'],name+'allcandidatebalance');close(f['all_candidate_denominator'],x['counted_A']+x['counted_B']+sum(x['counted_other'].values())+x['remaining'],name+'remainder only')
    bound=load(D/'bounded-synthetic-scenarios.json');ck(bound['clipping']['clipped_units']>0 and abs(bound['clipping']['solved_net']-90)<1e-9,'bounded clipping solved after clip');ck(bound['impossible']['status']=='impossible'and bound['unknown']['status']=='unknown'and bound['no_pool']['status']=='no_positive_pool','bounded edge statuses')
    regress=load(D/'repair-regressions/results.json');ck(regress['status']=='pass'and not regress['failures'],'actual CLI input regressions');ck(regress['coordinator_exact_cases']==21 and regress['case_count']>=132,'all21actualcases and expanded parameter cases');ck(regress['calculator_sha256']==sha((D/'calculator.py').read_bytes()),'regressions match current calculator')
    for r in regress['cases']:
        ck(r['passed']and r['exit_code']==0 and not r['stderr']and r['strict_JSON_error']is None,r['name']+' strict stdout/no traceback');ck(sha(r['stdout'].encode())==r['stdout_sha256']and sha(r['stderr'].encode())==r['stderr_sha256'],r['name']+' exact transcript hash')
        parsed=json.loads(r['stdout'],parse_constant=lambda x:(_ for _ in ()).throw(ValueError(x)))
        if r['expected']=='invalid':ck(parsed['status'].startswith('invalid')and parsed.get('final')is None and 'input'not in parsed,r['name']+' safe structured rejection')
        if 'fixture'in r:
            f=r['fixture'];b=(STATE/f['path']).read_bytes();ck(sha(b)==f['sha256']and len(b)==f['bytes'],r['name']+' exact fixture bytes')
    invariant=load(D/'repair-regressions/historical-invariance.json');ck(invariant['status']=='pass'and not invariant['unexpected_changes']and invariant['all_valid_prior_live_cases_equal'],'source/scenario invariance to complete prior archive')
    history=load(D/'repair-history/pre-input-validation-v1/freeze.json');ck(len(history['external_original_assets'])==64 and history['prior_owned_count']==103,'complete103priorowned plus64original references')
    for r in history['files']:
        z=(STATE/r['stored_path']).read_bytes();b=gzip.decompress(z);ck(sha(z)==r['stored_sha256']and sha(b)==r['raw_sha256']and len(b)==r['raw_bytes'],'immutable repair history '+r['original_path'])
    # Relative report links are resolved without network. Schema's inline code paths are documented, not links.
    links=[]
    for p in [STATE/'county-partisanship.md',S/'SCHEMA.md']:
        for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if link.startswith(('https://','http://','#')):continue
            path=(p.parent/link.split('#')[0]).resolve();ck(path.exists()or (not args.audit and path in [D/'asset-manifest.json',D/'validation.json',D/'final-seal.json']),'relative link '+link);links.append(str(path.relative_to(STATE)))
    for p in owned():ck(p.stat().st_size<40000000,'owned strict bound '+str(p.relative_to(STATE)))
    ck(not list(D.rglob('__pycache__')),'no retained cache directories')
    if args.audit:
        manifest=load(D/'asset-manifest.json');actual={str(p.relative_to(STATE))for p in owned()};listed={r['path']for r in manifest['owned']};ck(actual==listed,'complete owned asset inventory')
        for r in manifest['owned']+manifest['external_original_assets']:
            b=(STATE/r['path']).read_bytes();ck(len(b)==r['bytes']and sha(b)==r['sha256'],'sealed hash '+r['path'])
        ck(manifest['self_excluded']and 'data/baselines/asset-manifest.json'not in listed,'acyclic seal')
        attestation=load(D/'final-seal.json')
        for field,path in [('calculator_sha256','calculator.py'),('validation_sha256','validation.json'),('regression_sha256','repair-regressions/results.json'),('historical_invariance_sha256','repair-regressions/historical-invariance.json'),('history_freeze_sha256','repair-history/pre-input-validation-v1/freeze.json')]:ck(attestation[field]==sha((D/path).read_bytes()),'final seal pin '+field)
        ck(attestation['current_manifest_not_pinned_here']and not any(attestation['approvals'].values()),'no reverse current MF pin or operational approvals')
    out={'status':'pass'if not fail else 'fail','checks':checks,'failures':fail,'offline':True,'source_contests':4,'counties_each':33,'native_rows':{k:v[0]for k,v in expected.items()},'original_candidate_control_positions':50179,'independent_PDF_county_candidate_cells':495,'county_scenarios':1056,'state_target_cases':32,'native_target_rows':17116,'source_scoped_orders':18,'peer_captured_checks':376717,'input_regression_cases':regress['case_count'],'input_regression_negative_cases':regress['negative_cases'],'input_regression_positive_cases':regress['positive_cases'],'prior_handoff_history_verified':True,'certified_native_priority':None,'canonical_dispatch_keys':[],'relative_links_checked':len(links),'historical_not_projection':True,'no_protected_values_allocated':True,'asset_seal_phase':'post-validation seal; audit-only does not rewrite this file'}
    if not args.audit:(D/'validation.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'checks':checks,'failures':fail[:15],'audit':args.audit}));assert not fail
if __name__=='__main__':main()
