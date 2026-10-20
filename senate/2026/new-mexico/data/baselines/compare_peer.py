#!/usr/bin/env python3
"""Bounded comparison of immutable captured finished turnout outputs, never imports producer code."""
import datetime,gzip,hashlib,json
from pathlib import Path
D=Path(__file__).resolve().parent;P=D.parent/'turnout';F=D/'source/peer-freeze';F.mkdir(exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text())
def main():
    pin=D/'source/independent-first-pin.json';assert pin.exists()
    receipt=F/'capture.json'
    if not receipt.exists():
        names=['original-first-witness-v2.json','original-extract.json','priority-set.json','canvass-controls.json','legacy-methods.json','ballot-registration-extract.json','registration-stocks.json','county-summary.csv','native-inventory.json']
        capture={'captured_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'peer_agent_id':'5f787f59-e6ff-4494-b416-a0fb4383237f','peer_status_at_launch':'finished per actual launch context; not contacted or restarted','our_original_first_pin_sha256':sha(pin.read_bytes()),'scope':'exact captured stable core only; no assertion about future final files; no coordinator acceptance','files':[]}
        for n in names:
            b=(P/n).read_bytes();z=gzip.compress(b,mtime=0);(F/(n+'.gz')).write_bytes(z)
            capture['files'].append({'peer_path':'data/turnout/'+n,'frozen_path':n+'.gz','sha256':sha(b),'bytes':len(b),'stored_sha256':sha(z),'stored_bytes':len(z)})
        receipt.write_text(json.dumps(capture,indent=2)+'\n')
    cap=load(receipt)
    supplement=F/'sensitivity.capture.json'
    if not supplement.exists():
        b=(P/'sensitivity.json').read_bytes();z=gzip.compress(b,mtime=0);(F/'sensitivity.json.gz').write_bytes(z)
        supplement.write_text(json.dumps({'peer_path':'data/turnout/sensitivity.json','frozen_path':'sensitivity.json.gz','sha256':sha(b),'bytes':len(b),'stored_sha256':sha(z),'stored_bytes':len(z),'captured_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2)+'\n')
    cap['files'].append(load(supplement))
    def peer(n):
        r=next(r for r in cap['files']if r['peer_path'].endswith('/'+n));z=(F/r['frozen_path']).read_bytes();assert sha(z)==r['stored_sha256'];b=gzip.decompress(z);assert sha(b)==r['sha256'];return json.loads(b)
    E=load(D/'original-extract.json');PE=peer('original-extract.json');checks=0;gaps=[]
    def ck(a,b,context):
        nonlocal checks
        checks+=1
        if a!=b:gaps.append({'context':context,'ours':a,'peer':b})
    for k,v in E.items():
        p=PE[k];ck([v['headers'],v['parties']],p['header_rows'],k+' header');ck(v['raw_sha256'],p['raw_sha256'],k+' hash');ck(len(v['rows']),len(p['rows']),k+' count')
        ownmeta=load(D/'source'/v['page_data_path'])['props']['pageProps'];ck(ownmeta,p['metadata'],k+' complete_pageProps')
        for r,s in zip(v['rows'],p['rows']):
            label=k+':'+str(r['source_row']);ck(r['raw_row'],s['raw_row'],label+' all cells');ck(r['source_row'],s['source_row_1based'],label+' position');ck(r['scope'],s['level'],label+' scope');ck(r['county_literal'],s['county_literal'],label+' parent');ck(r['label_literal'],s['native_label'],label+' label');ck(r['administrative'],s['administrative'],label+' admin');ck(r['native_id'],s['native_numeric_id'],label+' ID')
            for x,y in zip(r['cells'][2:],s['fields']):
                for a,b in [('column','column_1based'),('header','label'),('party_literal','party_literal'),('literal','literal'),('value','value')]:ck(x[a],y[b],label+' '+a)
        ck([(r['county_literal'],r['label_literal'])for r in v['rows']if r['scope']=='Precinct'],[(r['county_literal'],r['native_label'])for r in p['rows']if r['level']=='Precinct'],k+' full inventory')
    # Every legacy selected source row, including trailing empty cell and native candidate/method IDs.
    legacy=load(D/'legacy-original-rows.json');pl=peer('legacy-methods.json')
    for k,v in pl.items():
        own=legacy[k];ck(own['header'],v['header'],k+' legacy header')
        for r in v['required_rows']:ck(own['rows'][r['source_row_1based']-2]['raw_row'],r['raw_row'],k+' legacy full method fields')
    pt=peer('ballot-registration-extract.json');t=load(D/'turnout-controls.json')
    for yr,v in t.items():
        p=pt[yr];ck(v['header']['ballots_cast'],p['state_ballots_cast'],yr+' ballots');ck(v['header']['eligible_voters'],p['state_eligible_voters'],yr+' eligible');ck(len(v['native_rows']),len(p['native_rows']),yr+' native turnout coverage')
        for a,b in zip(v['native_rows'],p['native_rows']):
            for x,y in [('county_id_literal','county_id_literal'),('label_literal','native_label'),('ballots_cast','ballots_cast'),('eligible_voters','eligible_voters')]:ck(a[x],b[y],yr+' turnout '+x)
    # All PDF county controls, statewide candidate methods, separate registration stocks.
    pc=peer('canvass-controls.json');ours=load(D/'pdf-county-controls.json')
    for k,vec in ours['vectors'].items():
        pv=pc['president_2024_county_controls'] if k=='2024-president' else pc['county_controls'][k[:4]]
        for a in vec:
            b=next(b for b in (pv if isinstance(pv,list)else pv['candidate_rows'])if b.get('candidate_csv_column_1based',b.get('csv_column_1based'))==vec.index(a)+3)
            ck(a['values'],b['county_values']+[b['state']],k+' pdf vector')
    methods=load(D/'state-candidate-methods.json')
    for k,v in methods.items():
        a=sorted(r['values']for r in v['rows']);b=sorted([r['early'],r['absentee'],r['election_day'],r['total']]for r in pc['statewide_candidate_methods'][k]['numeric_rows']);ck(a,b,k+' candidate methods')
    reg=load(D/'registration-controls.json');pr=peer('registration-stocks.json')
    for date,key in [('2024-10-31','9'),('2024-11-26','10')]:
        for r in reg[date]['rows']:
            a=next(t for t in pr[key]['state']['rows']if t['label_literal']==r['county_literal']);ck(r['values'],a['counts']+[a['total']],date+' '+r['county_literal']+' registration')
    priority=load(D/'priority-contract.json')['2024-senate'];pp=peer('priority-set.json')
    own=priority['observed_complete_candidate_rows_only'];p=pp['known_observation_scope'];keys=['nm:elstats:14873:'+r['county']+':'+r['label']for r in own['ordered']]
    initial_tie_difference=sum(a!=b for a,b in zip(keys,p['order']))
    source_order=sorted(own['ordered'],key=lambda r:(-r['all_candidate_votes'],r['source_row']))
    ck(['nm:elstats:14873:'+r['county']+':'+r['label']for r in source_order],p['order'],'complete descending observed native order; source-position ties');ck(own['denominator'],p['denominator'],'observed denominator');ck(own['minimum80'],p['metrics']['minimum80_count'],'exact minimum80');ck(own['minimum80_before'],p['metrics']['preceding_votes'],'exact80 before');ck(own['minimum80_at'],p['metrics']['minimum80_votes'],'exact80 crossing');ck(own['top15_total'],p['metrics']['top15_votes'],'top15 sum')
    counties=priority['county_sensitivity'];fips={r['cells'][6]['text']:r['cells'][2]['text']for r in load(D/'county-fips-source-rows.json')}
    fips['Dona Ana']=fips['Doña Ana']
    ck(['nm:county:'+fips[r['county']]for r in counties['ordered']],pp['county_sensitivity']['full_order'],'county full descending order');ck(counties['minimum80'],pp['county_sensitivity']['metrics']['minimum80_count'],'county exact80')
    ck(priority['canonical_dispatch_keys'],pp['ordered_priority_keys'],'empty certified dispatch');ck(priority['certified_native_minimum80'],pp['certified_native_minimum80'],'unknown certified minimum80')
    rn=load(D/'registration-native-controls.json')
    for vintage,v in rn.items():
        ours=[r for r in v['rows']if r['scope']!='grand_total'];prs=pr[vintage]['county']['rows'];ck(len(ours),len(prs),vintage+' all registration row count')
        for r,s in zip(ours,prs):
            for a,b in [('page','page'),('line','line_1based'),('county_literal','county_literal'),('label_literal','label_literal'),('counts','counts'),('total','total'),('continuations','label_continuations'),('raw_lines','raw_lines'),('party_order','party_order')]:ck(r[a],s[b],vintage+' native registration '+a)
    # Build all 18 source-scoped order contracts entirely from our own extraction.
    ownorders={};ps=peer('sensitivity.json')
    def metrics(rows,denom=None):
        rows=sorted(rows,key=lambda r:(-r['votes'],r['position']));T=sum(r['votes']for r in rows)if denom is None else denom;acc=0;cross=None
        for i,r in enumerate(rows,1):
            acc+=r['votes']
            if cross is None and 5*acc>=4*T:cross=i
        full=[r['key']for r in rows];cut=max(15,cross or 0)
        return {'denominator':T,'observed_votes':sum(r['votes']for r in rows),'unit_count':len(rows),'top15_votes':sum(r['votes']for r in rows[:15]),'minimum80_count':cross,'minimum80_votes':sum(r['votes']for r in rows[:cross])if cross else None,'preceding_votes':sum(r['votes']for r in rows[:cross-1])if cross else None,'full_order':full,'ordered_priority_keys':full[:cut],'ordered_remainder_keys':full[cut:]}
    for k,v in E.items():
        rs=[r for r in v['rows']if r['scope']=='County'];ownorders['county-'+k]=metrics([{'key':'nm:county:'+fips[r['label_literal']],'votes':sum(c['value']for c in r['cells'][2:-2]),'position':r['source_row']}for r in rs])
    bm=load(D/'administrative-method-controls.json')
    for yr,v in t.items():
        for label,field in [('ballots','calcVoterTurnout'),('eligible-voters','Voters')]:ownorders['county-'+yr+'-'+label]=metrics([{'key':'nm:county:'+fips[r['CountyName']],'votes':int(r[field]),'position':i}for i,r in enumerate(v['county_service'])])
        b=bm[yr];ownorders['county-'+yr+'-pdf-ballots']=metrics([{'key':'nm:county:'+fips[c],'votes':sum(r['values'][i]for r in b['rows']),'position':i}for i,c in enumerate(b['county_order'])])
    for date,vintage in [('2024-10-31','9'),('2024-11-26','10')]:ownorders['county-2024-registration-stock-'+vintage]=metrics([{'key':'nm:county:'+fips[r['county_literal']],'votes':r['values'][-1],'position':i}for i,r in enumerate(reg[date]['rows'])if r['county_literal']!='TOTAL'])
    rows=[{'key':'nm:elstats:14873:'+r['county']+':'+r['label'],'votes':r['all_candidate_votes'],'position':r['source_row'],'administrative':r['administrative']}for r in own['ordered']]
    ownorders['native-2024-senate-complete-candidate-rows-only']=metrics(rows)
    ownorders['native-2024-senate-known-rows-state-denominator']=metrics(rows,903311)
    ownorders['native-2024-senate-complete-nonadministrative-rows-only']=metrics([r for r in rows if not r['administrative']])
    ck(set(ownorders),set(ps),'all18 order names')
    for name,o in ownorders.items():
        p=ps[name]
        for field in ['denominator','observed_votes','unit_count','top15_votes','minimum80_count','minimum80_votes','preceding_votes','ordered_priority_keys','ordered_remainder_keys']:ck(o[field],p[field],name+' '+field)
        ck(o['full_order'],p['ordered_priority_keys']+p['ordered_remainder_keys'],name+' full order')
    (D/'source-scoped-orders.json').write_text(json.dumps(ownorders,indent=2)+'\n')
    out={'peer_agent_id':cap['peer_agent_id'],'scope':cap['scope'],'captured_receipt_sha256':sha(receipt.read_bytes()),'checks':checks,'failures':gaps,'passed':not gaps,'initial_literal_label_tie_sort_positions_differed':initial_tie_difference,'tie_convention_resolution':'Original own priority-contract.json retained label ties; source-scoped-orders.json separately declares source-position tie ordering, fully matches captured peer. Values/membership and crossing totals never changed.','orders_checked':len(ownorders),'coordinator_accepted':False,'certified_native_priority':None,'future_final_equality_claim':False}
    (D/'peer-reconciliation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'checks':checks,'failures':len(gaps),'passed':not gaps}));assert not gaps,[(x['context'])for x in gaps[:5]]
if __name__=='__main__':main()
