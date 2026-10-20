#!/usr/bin/env python3
"""Independent original-first Illinois extraction. Offline; no peer imports.
Requires beautifulsoup4. All original CSV fields and logical record positions
are preserved. Geographic projections are explicit views, not physical joins.
"""
from pathlib import Path
from collections import Counter,defaultdict
from urllib.parse import urljoin,quote
import csv,gzip,hashlib,io,json,zipfile
from bs4 import BeautifulSoup

D=Path(__file__).resolve().parent;S=D/'source';N=D.parent/'news';E=D/'extract';E.mkdir(exist_ok=True)
PARENTS={'104':'64','105':'16','106':'92','107':'88','108':'48','110':'101'}
YEARS=[2024,2022,2020]
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def gzjson(p,rows):p.write_bytes(gzip.compress((''.join(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n' for r in rows)).encode(),mtime=0))
def writecsv(p,rows):
    assert rows
    with p.open('w',newline='')as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
PINS={}
def original(sid):
    p=S/(sid+'.receipt.json')
    if p.exists():
        a=json.loads(p.read_text());assert a['status']==200,sid
        file=S/a['asset'];b=gzip.decompress(file.read_bytes());size=a['raw_bytes'];url=a['final_url']
    else:
        snapshot=S/'shared-originals.json'
        if not snapshot.exists():
            selected=[r for r in json.loads((N/'manifest.json').read_text())if r['id'].startswith('sos-')]
            dump(snapshot,selected)
        a=next(x for x in json.loads(snapshot.read_text())if x['id']==sid)
        file=N/a['asset'];b=gzip.decompress(file.read_bytes());size=a['bytes'];url=a['final_url']
    assert sha(file.read_bytes())==a['stored_sha256'] and sha(b)==a['raw_sha256'] and len(b)==size
    PINS[sid]={'path':str(file.relative_to(D.parent.parent)),'stored_sha256':sha(file.read_bytes()),'stored_bytes':file.stat().st_size,'raw_sha256':sha(b),'raw_bytes':len(b),'url':url,'receipt_path':str(p.relative_to(D.parent.parent))if p.exists()else'data/turnout/source/shared-originals.json','receipt_sha256':sha(p.read_bytes())if p.exists()else sha((S/'shared-originals.json').read_bytes()),'retrieved_at_utc':a.get('retrieved_at_utc'),'source_headers':a.get('headers'),'status':a.get('status'),'parent':a.get('parent',a.get('parent_source_id'))}
    return b,url
def table(body,year):
    soup=BeautifulSoup(body,'html.parser');name='PRESIDENT AND VICE PRESIDENT'if year==2024 else'UNITED STATES SENATOR'
    label=soup.find(string=lambda x:x and x.strip()==name)
    if label is None:return None
    t=label.find_parent('div').find_next('table')
    if t is None:return None
    if 'Candidate'not in t.get_text():return None
    return t
def candidate_rows(body,year,url):
    t=table(body,year)
    if t is None:return None
    rows=[];total=None
    for pos,tr in enumerate(t.find_all('tr')):
        cells=[c.get_text(' ',strip=True)for c in tr.find_all(['th','td'])]
        if not cells or cells[0]=='Candidate':continue
        assert len(cells)==4,cells
        if cells[0]=='Vote Totals':total=int(cells[2].replace(',',''));continue
        a=tr.find('a',href=True);rows.append({'table_id':t.get('id'),'tr_position_0based':pos,'name':cells[0],'party':cells[1],'votes':int(cells[2].replace(',','')),'votes_literal':cells[2],'percentage_literal':cells[3],'href':a['href']if a else None,'detail_url':urljoin(url,a['href'])if a else None})
    assert total==sum(x['votes']for x in rows)
    return rows,total
def ranking(rows,field,key='key'):
    def tie(r):
        if 'precinct_name_literal'in r:return(r['authority_id'],r['precinct_name_literal'])
        return(r.get('county_authority_id',r.get('authority_id',r[key])),)
    rows=sorted(rows,key=lambda r:(r[field]is None,-(r[field]or 0),tie(r)));total=sum(r[field]for r in rows if r[field]is not None);cum=0;k=None
    for i,r in enumerate(rows,1):
        cum+=r[field]or 0;r.update(rank=i if r[field]is not None else None,order_position=i,cumulative_votes=cum,share_numerator=r[field],share_denominator=total,share=r[field]/total if r[field]is not None else None,cumulative_share=cum/total)
        if k is None and 5*cum>=4*total:k=i
    assert k and 5*rows[k-1]['cumulative_votes']>=4*total and (k==1 or 5*rows[k-2]['cumulative_votes']<4*total)
    return rows,{'denominator':total,'top15_votes':sum(r[field]for r in rows[:15]),'top15_count':min(15,len(rows)),'top15_fraction':f'{sum(r[field]for r in rows[:15])}/{total}','minimum80_count':k,'preceding_count':k-1,'preceding_votes':rows[k-2]['cumulative_votes']if k>1 else 0,'crossing_key':rows[k-1][key],'crossing_votes':rows[k-1][field],'cumulative80_votes':rows[k-1]['cumulative_votes'],'remainder_count':len(rows)-k,'remainder_votes':total-rows[k-1]['cumulative_votes'],'ordered_priority_keys':[r[key]for r in rows[:max(k,15)]],'full_order':[r[key]for r in rows],'remainder_keys':[r[key]for r in rows[k:]]}
def main():
    controls={};native={};states={};names={};rawout=[];allstate=[];cats=[];nativeunits={};native_authorities={}
    for year in YEARS:
        sid='sos-2024-president-csv'if year==2024 else f'sos-observed-{year}-senate-native-csv';b,url=original(sid)
        reader=csv.DictReader(io.StringIO(b.decode('utf-8-sig')));fields=reader.fieldnames;rr=list(reader);assert len(fields)==12
        rawout.extend({'year':year,'source_id':sid,'record_position_1based':i,'csv_physical_line_header_offset':1,'fields':r}for i,r in enumerate(rr,1))
        rawstat=Counter();groups=defaultdict(list);contexts=defaultdict(list);auth=defaultdict(Counter)
        for i,r in enumerate(rr,1):
            rawstat[r['CandidateName']]+=int(r['VoteCount']);groups[(r['JurisdictionID'],r['PrecinctName'])].append((i,r));contexts[(r['JurisdictionID'],r['JurisContainerID'],r['JurisName'],r['PrecinctName'])].append(i);auth[r['JurisdictionID']][r['CandidateName']]+=int(r['VoteCount']);names[r['JurisdictionID']]=r['JurisName']
        sb,surl=original(f'sos-observed-{year}-federal-statewide-page');st,total=candidate_rows(sb,year,surl);states[year]=st
        allstate.extend(dict(year=year,**r)for r in st);printed=[r['name']for r in st if r['name']in rawstat];assert len(printed)==(3 if year!=2020 else 5)
        assert all(rawstat[r['name']]==r['votes']for r in st if r['name']in printed)
        units=[]
        for (aid,prec),items in groups.items():
            c=Counter();regs=set();cc=defaultdict(list)
            for pos,r in items:c[r['CandidateName']]+=int(r['VoteCount']);regs.add(r['Registration']);cc[(r['JurisContainerID'],r['JurisName'])].append(pos)
            assert len(regs)==1
            printed_values={n:c[n]if any(r['CandidateName']==n for _,r in items)else None for n in printed}
            v=sum(x for x in printed_values.values()if x is not None);generic=sum(z for n,z in c.items()if n.lower()=='write-in')
            u={'key':f'il:{year}:authority:{aid}:label:{quote(prec,safe="")}','year':year,'authority_id':aid,'authority_name':names[aid],'county_authority_parent_id':PARENTS.get(aid,aid),'precinct_name_literal':prec,'printed_candidate_votes':printed_values,'printed_observed_sum':v,'generic_writein_marks':generic if any(n.lower()=='write-in'for n in c)else None,'printed_plus_generic_observed':v+generic,'literal_categories':dict(c),'registration_literal':next(iter(regs)),'source_records_1based':[i for i,_ in items],'source_contexts':[{'container_id':a,'juris_name':n,'source_records_1based':z}for(a,n),z in cc.items()],'method':None,'method_status':'no method column; label never decoded into a method','scope':'authority + literal source precinct label observation projection; not approved physical precinct identity','geometry_status':'unverified historical/current mapping','administrative_only':all(x is None for x in printed_values.values()),'missing_printed_candidate_rows':[n for n,v in printed_values.items()if v is None]}
            u['printed_known_recorded_sum']=v
            if u['administrative_only']:u['printed_observed_sum']=None
            units.append(u)
        nativeunits[year]=units;gzjson(E/f'native-units-{year}.jsonl.gz',units)
        gzjson(E/f'source-contexts-{year}.jsonl.gz',[{'year':year,'authority_id':k[0],'container_id':k[1],'juris_name':k[2],'precinct_name':k[3],'source_records_1based':v}for k,v in contexts.items()])
        authorities=[{'key':f'il:authority:{a}','authority_id':a,'authority_name':names[a],'county_authority_parent_id':PARENTS.get(a,a),'printed_observed_sum':sum(c[n]for n in printed),'generic_writein_marks':sum(v for n,v in c.items()if n.lower()=='write-in'),'printed_plus_generic_observed':sum(c[n]for n in printed)+sum(v for n,v in c.items()if n.lower()=='write-in'),'literal_categories':dict(c),'native_projection_count':sum(u['authority_id']==a for u in units),'source_context_count':sum(k[0]==a for k in contexts)}for a,c in auth.items()]
        for a in authorities:
            a['generic_writein_source_present']=any(n.lower()=='write-in'for n in a['literal_categories'])
            a['generic_writein_recorded_sum']=a['generic_writein_marks']
            if not a['generic_writein_source_present']:a['generic_writein_marks']=None
        native_authorities[year]=authorities;gzjson(E/f'authority-native-{year}.jsonl.gz',authorities)
        native[year]=(rr,auth,printed)
        generic=sum(v for k,v in rawstat.items()if k.lower()=='write-in');named=sum(r['votes']for r in st if r['name']not in printed)
        controls[year]={'raw_rows':len(rr),'raw_fields':len(rr)*12,'raw_columns':fields,'authority_count':len(auth),'full_source_contexts':len(contexts),'authority_literal_precinct_groups':len(groups),'printed_total':sum(rawstat[n]for n in printed),'state_named_total':total,'state_named_additional':named,'generic_writein_marks':generic,'generic_minus_named_additional_unallocated':generic-named,'literal_category_sums':dict(rawstat),'state_candidate_rows':len(st),'administrative_only_native_groups':[u['key']for u in units if u['administrative_only']],'missing_printed_candidate_rows':sum(len(u['missing_printed_candidate_rows'])for u in units),'source_sha256':sha(b)}
        cats.extend({'year':year,'category_literal':k,'votes':v,'classification':'printed_candidate'if k in printed else'generic_writein_marks'if k.lower()=='write-in'else'nonvote_category'}for k,v in rawstat.items())
    gzjson(E/'original-native-records.jsonl.gz',rawout);writecsv(E/'statewide-source-rows.csv',allstate);writecsv(E/'native-category-controls.csv',cats)
    dump(E/'independent-controls.json',controls)
    # Native ranking is exact only for its stated reported-mark scope.
    for field in ['printed_observed_sum','printed_plus_generic_observed']:
        order,metrics=ranking([dict(u)for u in nativeunits[2024]],field);gzjson(E/f'native-2024-order-{field}.jsonl.gz',order);dump(E/f'native-2024-{field}-priority.json',metrics)
        order,metrics=ranking([dict(u)for u in native_authorities[2024]],field);gzjson(E/f'authority-2024-order-{field}.jsonl.gz',order);dump(E/f'authority-2024-{field}-priority.json',metrics)
    for year in [2022,2020]:
        for field in ['printed_observed_sum','printed_plus_generic_observed']:
            order,metrics=ranking([dict(u)for u in nativeunits[year]],field);gzjson(E/f'native-{year}-order-{field}.jsonl.gz',order);dump(E/f'native-{year}-{field}-priority.json',metrics)
    # Independently extract all 306 county tables. These are combined county
    # views, never extra votes to add to the 108 native authorities.
    zb,_=original('census-counties-2024');zf=zipfile.ZipFile(io.BytesIO(zb));cc=list(csv.DictReader(io.StringIO(zf.read(zf.namelist()[0]).decode('utf-8-sig')),delimiter='\t'))
    norm=lambda s:''.join(c for c in s.upper().replace('COUNTY','')if c.isalpha())
    fips={norm(r['NAME']):r['GEOID']for r in cc if r['USPS']=='IL'};assert len(fips)==102
    counties=[];county_candidates=[];emptycity=[];turnouts=[];county_orders={}
    for year in YEARS:
        rr,auth,printed=native[year]
        tb,tu=original(f'turnout-{year}');soup=BeautifulSoup(tb,'html.parser')
        assert soup.find('select').find('option',selected=True)['value']=={2024:'66',2022:'62',2020:'58'}[year]
        tt=next(t for t in soup.find_all('table')if 'Total Ballots Cast'in t.get_text());turn={}
        for i,tr in enumerate(tt.find_all('tr')):
            cs=[c.get_text(' ',strip=True)for c in tr.find_all(['td','th'])]
            if not cs or cs[0]=='Jurisdiction Name':continue
            assert len(cs)==4,cs
            turn[cs[0]]={'year':year,'jurisdiction_literal':cs[0],'historical_Total_Voters':int(cs[1].replace(',','')),'ballots_cast':int(cs[2].replace(',','')),'percentage_literal':cs[3],'source_table_id':tt.get('id'),'tr_position_0based':i}
        assert len(turn)==103
        control=turn.pop('All Jurisdictions');assert sum(t['ballots_cast']for t in turn.values())==control['ballots_cast'];assert sum(t['historical_Total_Voters']for t in turn.values())==control['historical_Total_Voters']
        controls[year]['turnout_table_control']=control;turnouts.extend(turn.values());sums=Counter()
        for cid in map(str,range(1,103)):
            sid=f'county-selector-{year}-UA'if cid=='1'else f'authority-{year}-{int(cid):03}';b,u=original(sid);s=BeautifulSoup(b,'html.parser')
            assert s.find('select',id='ContentPlaceHolder1_ddlElections').find('option',selected=True)['value']=={2024:'66',2022:'62',2020:'58'}[year]
            assert s.find('select',id='ContentPlaceHolder1_ddlJurisdictions').find('option',selected=True)['value']==cid
            cr,total=candidate_rows(b,year,u);assert len(set(c['name']for c in cr))==len(cr)
            cs={c['name']:c['votes']for c in cr};ids=[cid]+[a for a,p in PARENTS.items()if p==cid]
            for name in printed:assert cs[name]==sum(auth[a][name]for a in ids),(year,cid,name)
            for c in cr:sums[c['name']]+=c['votes'];county_candidates.append(dict(year=year,county_authority_id=cid,source_id=sid,**c))
            t=turn[names[cid]];v=sum(cs[n]for n in printed);wi=total-v;generic=sum(x['generic_writein_recorded_sum']for x in native_authorities[year]if x['authority_id']in ids)
            c={'key':f'il:county:{fips[norm(names[cid])]}','year':year,'county_authority_id':cid,'county_fips':fips[norm(names[cid])],'county_name':names[cid],'authority_ids':','.join(ids),'all_named_votes':total,'printed_votes':v,'additional_named_votes':wi,'native_generic_writein_marks':generic,'printed_plus_generic_marks':v+generic,'generic_minus_named_difference':generic-wi,'ballots_cast':t['ballots_cast'],'historical_Total_Voters':t['historical_Total_Voters'],'native_registration_once_per_literal_label':sum(int(x['registration_literal'])for x in nativeunits[year]if x['authority_id']in ids),'source_id':sid}
            counties.append(c)
            c['native_generic_writein_source_present']=any(x['generic_writein_source_present']for x in native_authorities[year]if x['authority_id']in ids)
            c['native_generic_writein_observed']=generic if c['native_generic_writein_source_present']else None
        assert dict(sums)=={r['name']:r['votes']for r in states[year]},(year,sums)
        for aid in PARENTS:
            sid=f'authority-{year}-{int(aid):03}';b,u=original(sid);s=BeautifulSoup(b,'html.parser');assert s.find('select',id='ContentPlaceHolder1_ddlJurisdictions').find('option',selected=True)['value']==aid
            assert table(b,year)is None and 'No information was found for this election.'in s.get_text()
            emptycity.append({'year':year,'authority_id':aid,'source_id':sid,'status':'no information was found; native authority exists in by-office CSV; named allocation unavailable'})
        for field in ['all_named_votes','printed_votes','printed_plus_generic_marks','ballots_cast','historical_Total_Voters']:
            order,met=ranking([dict(c)for c in counties if c['year']==year],field);writecsv(E/f'county-{year}-order-{field}.csv',order);county_orders[f'{year}:{field}']=met
    writecsv(E/'county-candidate-source-rows.csv',county_candidates);writecsv(E/'county-all-years.csv',counties);writecsv(E/'county-turnout-controls.csv',turnouts);dump(E/'city-selector-unavailable.json',emptycity);dump(E/'county-priorities.json',county_orders)
    # Complete actual authority inventory and compatibility CSV: explicitly 108,
    # not 102 county substitutions. Legal named allocations stay null if absent.
    current,_=original('registration-current-csv');cur=list(csv.DictReader(io.StringIO(current.decode('utf-8-sig'))));reg={r['JID']:r for r in cur if r['JID']};assert len(reg)==108
    assert sum(int(r['A'])for r in reg.values())==int(cur[-1]['A']);assert sum(int(r['I'])for r in reg.values())==int(cur[-1]['I'])
    inventory=[];compat=[]
    for a in sorted(native_authorities[2024],key=lambda r:int(r['authority_id'])):
        aid=a['authority_id'];parent=PARENTS.get(aid,aid);county=next(c for c in counties if c['year']==2024 and c['county_authority_id']==parent)
        item={'key':a['key'],'authority_id':aid,'name':a['authority_name'],'type':'city_commission'if aid in PARENTS else'county_authority_excluding_city_commission'if aid in PARENTS.values()else'county_authority','county_fips':county['county_fips'],'county_key':county['key'],'county_parent_authority_id':parent,'source_containers':sorted({r['JurisContainerID']for r in native[2024][0]if r['JurisdictionID']==aid}),'native_constituent_keys':[u['key']for u in nativeunits[2024]if u['authority_id']==aid],'current_registration_row_literal':reg[aid],'current_identity_compatibility':'same source ID roster only; boundaries/cross-year native identity unverified'}
        inventory.append(item)
        x={'key':a['key'],'authority_id':aid,'authority_name':a['authority_name'],'authority_type':item['type'],'county_fips':county['county_fips'],'county_parent_authority_id':parent,'president_2024_printed_votes':a['printed_observed_sum'],'president_2024_generic_writein_marks':a['generic_writein_marks'],'president_2024_printed_plus_generic_marks':a['printed_plus_generic_observed'],'president_2024_all_named_votes':county['all_named_votes']if len(county['authority_ids'].split(','))==1 else None,'native_observation_groups_2024':a['native_projection_count'],'native_source_contexts_2024':a['source_context_count'],'historical_2024_registration_once_per_literal_label':sum(int(u['registration_literal'])for u in nativeunits[2024]if u['authority_id']==aid),'ballots_cast_2024':county['ballots_cast']if len(county['authority_ids'].split(','))==1 else None,'registration_2026_A':int(reg[aid]['A']),'registration_2026_I':int(reg[aid]['I']),'current_registration_source_clock':'10/19/2026 10:18 AM; timezone not specified','current_registration_status':'unofficial statewide voter registration database; fluctuates daily'}
        for year in [2022,2020]:
            o=next(r for r in native_authorities[year]if r['authority_id']==aid);x[f'senate_{year}_printed_votes']=o['printed_observed_sum'];x[f'senate_{year}_generic_writein_marks']=o['generic_writein_marks'];x[f'senate_{year}_generic_writein_recorded_sum']=o['generic_writein_recorded_sum'];x[f'senate_{year}_generic_writein_source_present']=o['generic_writein_source_present']
        x['president_2024_generic_writein_recorded_sum']=a['generic_writein_recorded_sum'];x['president_2024_generic_writein_source_present']=a['generic_writein_source_present']
        compat.append(x)
    order,met=ranking(compat,'president_2024_printed_plus_generic_marks');writecsv(D.parent/'county-turnout.csv',order);dump(E/'authority-inventory.json',inventory)
    dispatch={'schema_version':'illinois-turnout-1','state':'IL','priority_contest':'2024 president; no 2024 Senate election','approval_status':'provisional source-scope research only; coordinator acceptance pending; reciprocal checks in peer-reconciliation.json','current_geometry_approved':False,'primary_geography':'108 disjoint native election authority IDs; county combined views separately scoped','county_valid_named_priority':county_orders['2024:all_named_votes'],'authority_reported_marks_priority':met,'authority_printed_candidate_priority':json.loads((E/'authority-2024-printed_observed_sum-priority.json').read_text()),'native_reported_marks_priority':json.loads((E/'native-2024-printed_plus_generic_observed-priority.json').read_text()),'native_printed_candidate_priority':json.loads((E/'native-2024-printed_observed_sum-priority.json').read_text()),'ordered_priority_keys':met['ordered_priority_keys'],'full_order':met['full_order'],'remainder_keys':met['remainder_keys'],'authority_inventory':inventory,'native_constituents':nativeunits[2024],'coverage':{'counties':102,'authorities':108,'raw_rows':59623,'source_contexts':11535,'authority_literal_label_observations':10062},'unavailable_cases':emptycity,'qualifications':['Reported marks include generic write-in marks, not legal named candidate totals or ballots.','County valid named vote total reconciles all 27 source reporting rows; 27 rows do not mean 27 presidential tickets.','Valid native write-in allocation unavailable in by-office export. No allocation of 16,469 source-scope residual.','Literal source labels may represent split ballot styles, federal-only groups or administrative cases; no polygons or current mapping inferred.','Four blank-label administrative-only groups and sparse absent Kennedy observations are retained.']}
    primary=dispatch['native_printed_candidate_priority']
    dispatch.update(primary_scope='2024 native printed-known candidate source observations: Harris, Trump, Kennedy where reported; absent cells null; no generic marks in denominator',primary_order_unit='authority ID + literal precinct name observation projection; full original source presentations nested, not deduplicated',primary_priority=primary,ordered_priority_keys=primary['ordered_priority_keys'],full_order=primary['full_order'],remainder_keys=primary['remainder_keys'],remainder_unavailable_named_context_keys=controls[2024]['administrative_only_native_groups'],coordinator_acceptance=False,peer_arithmetic_agreement='see peer-reconciliation.json; agreement does not approve geography or eligible universe')
    dispatch['primary_geography']='10062 native authority/literal-label observation groups including4 unavailable named pools;108 authorities;11535 full presentation contexts'
    dispatch['county_priority_expanded_authority_keys']=[a['key']for k in dispatch['county_valid_named_priority']['ordered_priority_keys']for a in inventory if a['county_key']==k]
    dispatch['native_order_artifact']='extract/native-2024-order-printed_observed_sum.jsonl.gz'
    dispatch['original_native_record_objects']={'path':'extract/original-native-records.jsonl.gz','format':'JSONL gzip; fields object preserves all12 original columns; filter year=2024 and record_position_1based; source_contexts lists ordered source record positions','source_positions':'logical CSV records excluding header, starting1; peer including-header positions equal this+1','sha256':sha((E/'original-native-records.jsonl.gz').read_bytes()),'native_context_objects':'extract/source-contexts-2024.jsonl.gz','no_deduplication':True}
    dispatch['named_pool_unavailable_keys']=controls[2024]['administrative_only_native_groups']
    dispatch['primary_scope_missing_cells']=[{'key':u['key'],'missing_candidates':u['missing_printed_candidate_rows']}for u in nativeunits[2024]if u['missing_printed_candidate_rows']]
    dispatch['native_to_authority_parent_map']={u['key']:f'il:authority:{u["authority_id"]}'for u in nativeunits[2024]}
    # Compact full native table for consumers; no absent category becomes zero.
    for scope in ['printed_observed_sum','printed_plus_generic_observed']:
        order,_=ranking([dict(u)for u in nativeunits[2024]],scope)
        rows=[]
        for u in order:
            rows.append({'order_position':u['order_position'],'rank':u['rank'],'key':u['key'],'authority_id':u['authority_id'],'authority_name':u['authority_name'],'precinct_name_literal':u['precinct_name_literal'],'printed_known_votes':u['printed_observed_sum'],'printed_known_recorded_sum':u['printed_known_recorded_sum'],'generic_writein_marks':u['generic_writein_marks'],'under_votes':u['literal_categories'].get('Under Votes'),'over_votes':u['literal_categories'].get('Over Votes'),'blank_ballots':u['literal_categories'].get('Blank Ballots'),'ranking_value':u[scope],'cumulative_votes':u['cumulative_votes'],'denominator':u['share_denominator'],'share':u['share'],'cumulative_share':u['cumulative_share'],'administrative_only':u['administrative_only'],'missing_candidates':json.dumps(u['missing_printed_candidate_rows']),'method':None})
        out=io.StringIO();w=csv.DictWriter(out,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows);(E/f'native-2024-order-{scope}.csv.gz').write_bytes(gzip.compress(out.getvalue().encode(),mtime=0))
    registration_reconciliation=[{'year':c['year'],'county_fips':c['county_fips'],'county_name':c['county_name'],'native_registration_once_per_label':c['native_registration_once_per_literal_label'],'turnout_table_Total_Voters':c['historical_Total_Voters'],'difference_native_minus_turnout':c['native_registration_once_per_literal_label']-c['historical_Total_Voters'],'scope':'separate source fields; not presumed identical registration snapshot/status'}for c in counties]
    writecsv(E/'registration-source-reconciliation.csv',registration_reconciliation)
    dump(E/'denominator-reconciliation.json',{year:{'printed_known_votes':controls[year]['printed_total'],'named_source_total':controls[year]['state_named_total'],'native_generic_marks':controls[year]['generic_writein_marks'],'native_all_reported_categories_sum':sum(controls[year]['literal_category_sums'].values()),'ballots':controls[year]['turnout_table_control']['ballots_cast'],'ballots_minus_named':controls[year]['turnout_table_control']['ballots_cast']-controls[year]['state_named_total'],'ballots_minus_all_native_categories':controls[year]['turnout_table_control']['ballots_cast']-sum(controls[year]['literal_category_sums'].values()),'native_registration_once_per_label':sum(c['native_registration_once_per_literal_label']for c in counties if c['year']==year),'turnout_table_Total_Voters':controls[year]['turnout_table_control']['historical_Total_Voters']}for year in YEARS})
    dump(D/'priority-set.json',dispatch);dump(E/'independent-controls.json',controls)
    dump(E/'source-pins.json',PINS)
    print(json.dumps(controls,indent=2))
if __name__=='__main__':main()
