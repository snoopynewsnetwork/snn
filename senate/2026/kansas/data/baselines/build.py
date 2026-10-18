"""Offline extraction, with independent OOXML parser and explicit source populations."""
import csv, gzip, io, json, re, sys
from collections import Counter, defaultdict
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'source'))
import read_sources as S
H=S.HERE
SPECS={
 'president_2024':dict(sid='sos-2024-president-precinct',year=2024,date='2024-11-05',stage='general',candidates=[('harris','Kamala D. Harris / Tim Walz','Democratic'),('trump','Donald J. Trump / JD Vance','Republican'),('kennedy','Robert F. Kennedy Jr./ Nicole Shanahan','Independent'),('oliver','Chase Oliver / Mike ter Maat','Libertarian')],controls=[544853,758802,16322,7614]),
 'senate_2022':dict(sid='sos-2022-senate-precinct',year=2022,date='2022-11-08',stage='general',candidates=[('holland','Mark R. Holland','Democratic'),('moran','Jerry Moran','Republican'),('graham','David C Graham','Libertarian')],controls=[372214,602976,29766]),
 'senate_2020':dict(sid='sos-2020-senate-precinct',year=2020,date='2020-11-03',stage='general',candidates=[('bollier','Barbara Bollier','Democratic'),('marshall','Roger Marshall','Republican'),('buckley','Jason Buckley','Libertarian')],controls=[571530,727962,68263]),
 'senate_primary_2026':dict(sid='sos-2026-senate-primary-precinct',year=2026,date='2026-08-04',stage='primary',candidates=[('anderson','Damon Anderson','Democratic'),('davis','Christy Davis','Democratic'),('hamilton','Adam Hamilton','Democratic'),('hart','Jason Hart','Democratic'),('latz','Kevin Latz','Democratic'),('murray','Erik Murray','Democratic'),('neumann','Sandy Spidel Neumann','Democratic'),('parelkar','Anne Parelkar','Democratic'),('schmidt','Patrick C. Schmidt','Democratic'),('soetaert','Michael "Mike" Soetaert','Democratic'),('taylor','Noah Taylor','Democratic'),('marshall','Roger Marshall','Republican'),('naramore','Pond Naramore','Republican')],controls=[5879,31857,77607,12412,4110,15177,12717,16836,13403,3716,30362,270632,68100])}
def jdump(path,obj): (H/path).write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def csvout(path,rows):
    if not rows: return
    b=io.StringIO(newline=''); w=csv.DictWriter(b,fieldnames=list(rows[0]),lineterminator='\n'); w.writeheader(); w.writerows(rows)
    data=b.getvalue().encode(); (H/path).write_bytes(gzip.compress(data,mtime=0) if str(path).endswith('.gz') else data)
def jlout(path,rows):
    data=''.join(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n' for r in rows).encode()
    (H/path).write_bytes(gzip.compress(data,mtime=0))
def number(v):
    if v is None or v=='': return None
    return int(v.replace(',','')) if re.fullmatch(r'[0-9,]+',v) else None
def county(v): return {'Comanche ':'Comanche'}.get(v,v)
def canon(label,spec):
    for k,n,p in spec['candidates']:
        if k in label.lower(): return k,n,p
    if 'write-in' in label.lower(): return 'generic_write_in','Generic write-in (source scope; not named valid candidate)','Unspecified'
    raise ValueError(label)
def key(sid,sheet,ct,components):
    return sid+'|'+sheet+'|'+ct+'|'+S.sha(json.dumps(components,ensure_ascii=False,separators=(',',':')).encode())
def main():
    fips={r['COUNTYNAME'].removesuffix(' County'):r['STATEFP']+r['COUNTYFP'] for r in csv.DictReader(io.StringIO(S.raw('county-codes-2020').decode()),delimiter='|') if r['STATE']=='KS'}
    assert len(fips)==105
    rawrows=[]; records=[]; units={}; footers={}; summary=[]; source_ids=set(); auxiliary=[]
    def capture(sid):
        source_ids.add(sid)
        data=list(S.workbook(sid))
        for sheet,path,rs in data:
            rawrows.extend(dict(source_id=sid,sheet=sheet,xml_path=path,row=i,cells=c) for i,c in rs)
        return data
    def add(prefix,sid,sheet,i,c,ct,components,cols,labels,parties,role='detail'):
        spec=SPECS[prefix]; ct=county(ct); assert ct in fips,(sid,ct)
        uk=key(sid,sheet,ct,components)
        if role=='detail':
            if uk not in units: units[uk]=dict(source_id=sid,baseline=prefix,sheet=sheet,county=ct,county_fips=fips[ct],unit_key=uk,native_components=components,candidates={},rows=[],method='not separately published',electorate='separate party primary' if spec['stage']=='primary' else 'general')
            u=units[uk]
        for col,label,party in zip(cols,labels,parties):
            ck,name,identity=canon(label,spec); v=number(c.get(col)); electorate=identity if spec['stage']=='primary' else 'general'
            rec=dict(source_id=sid,baseline=prefix,election_date=spec['date'],stage=spec['stage'],electorate=electorate,sheet=sheet,source_row=i,vote_column=col,county=ct,county_fips=fips[ct],unit_key=uk,role=role,native_components_json=json.dumps(components,ensure_ascii=False,separators=(',',':')),source_candidate=label,source_party=party,canonical_candidate=ck,candidate_name=name,party_identity=identity,votes=v,raw_value=c.get(col),value_status='published_integer' if v is not None else ('blank_unavailable' if c.get(col) in [None,''] else 'redacted_or_text_unavailable'),method='not separately published')
            records.append(rec)
            if role=='detail':
                assert ck not in u['candidates'],('duplicate source candidate key',uk,ck)
                u['candidates'][ck]=v; u['rows'].append([i,col]);
            else: footers[(prefix,ct,ck)]=v
    for prefix,spec in SPECS.items():
        sid=spec['sid']; data=capture(sid)
        for index,(sheet,path,rs) in enumerate(data):
            if index==0:
                for i,c in rs:
                    if i==1 or not c.get('A'): continue
                    add(prefix,sid,sheet,i,c,c['A'],[['precinct',c.get('B')],['VTD',c.get('G')]],['F'],[c['D']],[c.get('E')])
            else:
                ct=sheet.title()
                if prefix=='president_2024':
                    cols,ids={'Johnson':(['D','E','F','G'],['A','B','C']),'Sedgwick':(['B','C','D','E'],['A']),'Shawnee':(['C','D','E','F'],['A','B']),'Wyandotte':(['B','C','D','E'],['A'])}[ct]; header=2
                elif prefix=='senate_2022':
                    cols,ids={'Johnson':(['E','F','G'],['A','B','C','D']),'Sedgwick':(['C','D','E'],['A','B']),'Shawnee':(['C','D','E'],['A','B']),'Wyandotte':(['C','D','E'],['A','B'])}[ct]; header=2
                elif prefix=='senate_2020':
                    cols,ids,header={'Johnson':(['B','C','D'],['A'],3),'Shawnee':(['B','C','D','E'],['A'],3),'Sedgwick':(['B','C','D','E'],['A'],4),'Wyandotte':(['E','F','H','I'],['B'],5)}[ct]
                else:
                    cols=list('BCDEFGHIJKLMN'); ids=['A']; header=2 if ct=='Shawnee' else 3
                headers=dict(rs); labels=[headers[header].get(col) for col in cols]
                parties=[]
                for col,label in zip(cols,labels):
                    previous=headers.get(header-1,{}).get(col) if prefix in ['senate_2020','senate_primary_2026'] else None
                    token=label.split()[0] if label else None
                    parties.append(previous if previous and previous.upper() in ['NON','DEM','REP','LIB','IND'] else (token if token and token.upper() in ['DEM','REP','LIB','IND'] else None))
                for i,c in rs:
                    if i<=header or not any(c.get(a) for a in ids): continue
                    role='county_footer' if any((c.get(a) or '').upper() in ['TOTALS','COUNTY TOTALS'] for a in ids) else 'detail'
                    add(prefix,sid,sheet,i,c,ct,[[a,c.get(a)] for a in ids],cols,labels,parties,role)
                    if prefix=='senate_2020' and ct=='Sedgwick':
                        auxiliary.append(dict(source_id=sid,sheet=sheet,source_row=i,column='F',county=ct,role=role,category='reported_contest_total_including_generic_write_ins',raw_value=c.get('F'),votes=number(c.get('F'))))
                    if prefix=='senate_2020' and ct=='Wyandotte':
                        auxiliary.append(dict(source_id=sid,sheet=sheet,source_row=i,column='D',county=ct,role=role,category='unrelated_president_Biden_published_alongside_Senate',raw_value=c.get('D'),votes=number(c.get('D'))))
    # Broad 2024 is a separate complete 4-ticket context universe, never added to precinct data.
    broad=capture('sos-2024-president-county')
    for i,c in broad[0][2]:
        if i==1: continue
        add('president_2024','sos-2024-president-county',broad[0][0],i,c,c['E'],[[col,c.get(col)] for col in 'ABCDEF'],['J'],[c['H']],[c['I']])
    # A one-value source row belongs to the same native unit as other candidate rows.
    counts=defaultdict(Counter); available=defaultdict(Counter); missing=defaultdict(Counter)
    for u in units.values():
        for ck,v in u['candidates'].items():
            if ck=='generic_write_in': continue
            if v is None: missing[(u['source_id'],u['county'])][ck]+=1
            else: available[(u['source_id'],u['county'])][ck]+=v
    # Native detail counts; county footers remain independent totals where available.
    countyvalues={}; checks=[]
    for prefix,spec in SPECS.items():
        for ct in fips:
            vals={}
            for ck,name,party in spec['candidates']:
                sid='sos-2024-president-county' if prefix=='president_2024' else spec['sid']
                vals[ck]=footers[(prefix,ct,ck)] if (prefix,ct,ck) in footers else available[(sid,ct)][ck]
                checks.append(dict(baseline=prefix,county=ct,candidate=ck,source_id=spec['sid'],native_known_sum=available[(spec['sid'],ct)][ck],native_unavailable_cells=missing[(spec['sid'],ct)][ck],county_control=vals[ck],county_control_minus_native_known=vals[ck]-available[(spec['sid'],ct)][ck],control_basis='county_footer' if (prefix,ct,ck) in footers else ('broader_workbook' if prefix=='president_2024' else 'main_native_sum')))
            countyvalues[prefix,ct]=vals
        sums=[sum(countyvalues[prefix,ct][ck] for ct in fips) for ck,_,_ in spec['candidates']]
        assert sums==spec['controls'],(prefix,sums,spec['controls'])
        pdfid={'president_2024':'sos-2024-general-canvass','senate_2022':'sos-2022-general-canvass','senate_2020':'sos-2020-general-canvass','senate_primary_2026':'sos-2026-primary-canvass'}[prefix]
        source_ids.add(pdfid); text=S.pdf(pdfid); (H/'source'/ (pdfid+'.txt')).write_text(text)
        for (ck,name,party),value in zip(spec['candidates'],sums):
            assert f'{value:,}' in text.split('\f')[0],(pdfid,value)
            summary.append(dict(baseline=prefix,election_date=spec['date'],stage=spec['stage'],electorate=party if spec['stage']=='primary' else 'general',candidate=ck,candidate_name=name,party=party,county_sum=value,statewide_control=value,difference=0,control_source=pdfid))
    # County turnout controls with source-defined denominators/vintages.
    turnout={}; traw=[]
    for i,c in broad[1][2]:
        if i==1: continue
        ct=c['A']
        traw.append(dict(source_id='sos-2024-president-county',sheet=broad[1][0],row=i,county=ct,ballots=number(c.get('B')),registration=number(c.get('C')),mail_returns=None,mail_returns_raw=None,source_turnout_fraction=c.get('D')))
        if ct in fips: turnout[2024,ct]=(number(c['B']),number(c['C']))
    for sheet,path,rs in capture('turnout-2022'):
        for i,c in rs:
            if i<4 or not c.get('D'): continue
            literal=(c.get('A') or 'TOTAL').removesuffix(' COUNTY')
            ct={x.upper():x for x in fips}.get(literal,literal)
            traw.append(dict(source_id='turnout-2022',sheet=sheet,row=i,county=ct,ballots=number(c.get('D')),registration=number(c.get('F')),mail_returns=number(c.get('B')),mail_returns_raw=c.get('B'),source_turnout_fraction=None))
            if ct in fips: turnout[2022,ct]=(number(c['D']),number(c['F']))
    # Retain registration raw rows; do not interpret absent party cells as zeros.
    reg={}
    for sheet,path,rs in capture('registration-2024-november'):
        for i,c in rs:
            if c.get('A') in fips: reg[c['A']]=number(c.get('I'))
    source_ids.update(['county-codes-2020','certification-2024','npr-primary','npr-senate-primary','sumner-county-home','sumner-election-office','sumner-archive','sumner-2022-county-summary-candidate','sumner-2022-actual-linked-summary'])
    npr=json.loads(S.raw('npr-senate-primary')); vintage=[]
    for race in npr['races']:
        for result in race['results']:
            for c in result['candidates']:
                ck=c['last'].lower(); official=dict((k,v) for (k,n,p),v in zip(SPECS['senate_primary_2026']['candidates'],SPECS['senate_primary_2026']['controls']))[ck]
                vintage.append(dict(stage='primary',electorate=race['party'],candidate_key=ck,NPR_AP_candidate_id=c['id'],NPR_AP_label=c['first']+' '+c['last'],NPR_AP_votes=c['votes'],NPR_AP_updated_epoch_ms=result['updated'],SOS_canvass_votes=official,SOS_minus_NPR_AP=official-c['votes'],revision_cause='not established',November_mapping='not established'))
    csvout('primary-vintage-comparison.csv',vintage)
    rows=[]
    for ct in sorted(fips):
        r=dict(county_fips=fips[ct],county_key='US-KS-'+fips[ct],county=ct)
        for prefix,spec in SPECS.items():
            if spec['stage']!='general': continue
            vals=countyvalues[prefix,ct]; total=sum(vals.values()); a,b=list(vals.values())[:2]; pair=a+b
            for ck,n,p in spec['candidates']: r[prefix+'_'+ck+'_votes']=vals[ck]
            for k,v in dict(named_votes=total,d_votes=a,r_votes=b,other_named_votes=total-pair,pair_votes=pair,pair_participation=pair/total,d_pair_share=a/pair,d_minus_r_pair_margin_pp=100*(a-b)/pair,d_minus_r_named_margin_pp=100*(a-b)/total,d_minus_r_net_votes=a-b,historical_winner='D' if a>b else ('R' if b>a else 'tie'),margin_band='within_5pp' if abs(a-b)/pair<=.05 else ('5_to_10pp' if abs(a-b)/pair<=.1 else 'over_10pp')).items(): r[prefix+'_'+k]=v
        for y in [2024,2022]:
            r[f'ballots_{y}_source_workbook'],r[f'registration_{y}_source_workbook']=turnout[y,ct]
        r['registration_2024_november_separate_publication']=reg[ct]
        r['generic_write_in_2020_published_supplement']=footers.get(('senate_2020',ct,'generic_write_in'))
        rows.append(r)
    denom=sum(r['president_2024_named_votes'] for r in rows); order=sorted(rows,key=lambda r:(-r['president_2024_named_votes'],r['county_fips']))
    cum=0; n80=None; ranking=[]
    for rank,r in enumerate(order,1):
        cum+=r['president_2024_named_votes']
        if n80 is None and 5*cum>=4*denom: n80=rank
        ranking.append(dict(rank=rank,county=r['county'],county_fips=r['county_fips'],named_votes=r['president_2024_named_votes'],cumulative_votes=cum,share=r['president_2024_named_votes']/denom,cumulative_share=cum/denom,in_top15=rank<=15,in_minimum80=n80 is None or rank==n80))
        r.update(president_2024_rank=rank,president_2024_named_weight=r['president_2024_named_votes']/denom,president_2024_cumulative_votes=cum)
    for r in rows:
        r['priority_top15_or_min80']=r['president_2024_rank']<=max(15,n80)
        for p in ['president_2024','senate_2022','senate_2020']:
            r[p+'_pair_weight']=r[p+'_pair_votes']/sum(x[p+'_pair_votes'] for x in rows)
    csvout('../county-baselines.csv',rows); csvout('county-priority.csv',ranking); csvout('candidate-controls.csv',summary); csvout('native-county-reconciliation.csv',checks); csvout('turnout-registration-controls.csv',traw)
    csvout('native-candidates.csv.gz',records); jlout('source/raw-rows.jsonl.gz',rawrows)
    native=[]
    for u in units.values():
        spec=SPECS[u['baseline']]; cks=[k for k,_,_ in spec['candidates']]; vals=[u['candidates'].get(k) for k in cks]
        # Every required key exists, including blank/redacted values.
        assert set(cks)<=set(u['candidates']),u
        u['complete_named_values']=all(v is not None for v in vals)
        u['known_named_votes']=sum(v for v in vals if v is not None)
        u['named_votes']=sum(vals) if u['complete_named_values'] else None
        u['A_votes']=vals[0] if spec['stage']=='general' else None; u['B_votes']=vals[1] if spec['stage']=='general' else None
        u['pair_votes']=sum(vals[:2]) if spec['stage']=='general' and all(v is not None for v in vals[:2]) else None
        u['electorate_named_totals']={party:sum(u['candidates'][k] for k,_,p in spec['candidates'] if p==party) if all(u['candidates'][k] is not None for k,_,p in spec['candidates'] if p==party) else None for party in ['Democratic','Republican']} if spec['stage']=='primary' else {'general':u['named_votes']}
        native.append(u)
    jlout('native-units.jsonl.gz',native)
    inventory=[]
    for sid in sorted({u['source_id'] for u in native}):
        us=[u for u in native if u['source_id']==sid]
        for sheet in sorted({u['sheet'] for u in us}):
            part=[u for u in us if u['sheet']==sheet]
            inventory.append(dict(source_id=sid,sheet=sheet,counties=len({u['county'] for u in part}),units=len(part),complete_units=sum(u['complete_named_values'] for u in part),unavailable_units=sum(not u['complete_named_values'] for u in part),zero_complete_units=sum(u['named_votes']==0 for u in part),known_named_votes=sum(u['known_named_votes'] for u in part),exact_named_votes=sum(u['named_votes'] for u in part) if all(u['complete_named_values'] for u in part) else None))
    csvout('native-coverage.csv',inventory)
    native_state=[]
    for sid in sorted({u['source_id'] for u in native}):
        part=[u for u in native if u['source_id']==sid];prefix=part[0]['baseline'];spec=SPECS[prefix]
        for (ck,name,party),control in zip(spec['candidates'],spec['controls']):
            vals=[u['candidates'][ck] for u in part]; known=sum(v for v in vals if v is not None)
            native_state.append(dict(source_id=sid,baseline=prefix,electorate=party if spec['stage']=='primary' else 'general',candidate=ck,known_native_sum=known,unavailable_native_cells=sum(v is None for v in vals),statewide_named_control=control,control_minus_known_native=control-known,interpretation='unallocated source-scope residual; unavailable cells remain unavailable'))
    csvout('native-state-controls.csv',native_state)
    csvout('source/auxiliary-controls.csv',auxiliary)
    m=S.metadata(); refs=[]
    source_ids.update(x for x in m if Path(m[x]['stored_path']).parent==H/'source')
    for sid in sorted(source_ids):
        v=m[sid].copy(); fullpath=Path(v['stored_path']); original=S.raw(sid)
        v.update(stored_path=str(fullpath.relative_to(S.ROOT)),stored_bytes=fullpath.stat().st_size,original_bytes=len(original),original_sha256=S.sha(original),requested_url=v.get('requested_url',v.get('url')))
        if 'parent' not in v:
            specific={'npr-primary':'NPR Kansas primary application; newsroom historical product','npr-senate-primary':'npr-primary → supplied Senate JSON configuration','sumner-county-home':'Sumner County Kansas official authority root','sumner-election-office':'sumner-county-home → County Clerk and Election Officer / Election Office','sumner-archive':'sumner-election-office → Election Results archive','sumner-2022-actual-linked-summary':'sumner-archive → literal 2022 PDF href with query; official redirect to linked Revize storage','sumner-2022-county-summary-candidate':'Alternative primary Revize route; exact original hash independently equals sumner-2022-actual-linked-summary'}
            v['parent']=specific.get(sid,'current-results → labeled election/year download; retained original coordinator capture')
        refs.append(v)
    jdump('source/references.json',refs)
    jdump('build-summary.json',dict(counties=105,candidate_controls=summary,native_inventory=inventory,priority=dict(denominator=denom,top15=sum(x['named_votes'] for x in ranking[:15]),minimum80_count=n80,previous_sum=ranking[n80-2]['cumulative_votes'],crossing_sum=ranking[n80-1]['cumulative_votes'],crossing_county=ranking[n80-1]['county'],names=[r['county'] for r in ranking[:n80]]),source_conflicts=['2024 turnout broader workbook 1343020/2031120 versus certification release 1344147/2031132; separate source scopes retained','native suppression gaps are not allocated; footer totals retained separately','2020 generic write-ins in three supplements total 456 outside named certificate denominator']))
    print(json.dumps(dict(counties=len(rows),candidate_rows=len(records),native_units=len(native),priority_count=n80,denominator=denom)))
if __name__=='__main__': main()
