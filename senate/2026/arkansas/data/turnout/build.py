#!/usr/bin/env python3
"""Original-first Arkansas extraction/calculation; offline, no peer inputs.

Python standard library + pdftotext. Rebuild only owned derived paths.
Raw OOXML/JSON/PDF source bytes remain intact, including unrelated offices.
"""
import collections, csv, gzip, hashlib, io, json, pathlib, re, subprocess, tempfile
import urllib.parse, xml.etree.ElementTree as ET, zipfile
ROOT=pathlib.Path(__file__).resolve().parent
STATE=ROOT.parents[1]
REPO=ROOT.parents[4]
def sha(b): return hashlib.sha256(b).hexdigest()
def js(path,obj):
    (ROOT/path).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def gzjs(path,obj):
    (ROOT/path).write_bytes(gzip.compress((json.dumps(obj,ensure_ascii=False,separators=(',',':'))+'\n').encode(),mtime=0))
def read(key,shared=False):
    receipt=ROOT/'source'/(key+'.receipt.json') if shared else ROOT/'source/acquired'/(key+'.receipt.json')
    r=json.loads(receipt.read_text())
    p=REPO/r['shared_original_path'] if r.get('shared_original_path') else receipt.parent/r['asset']
    b=p.read_bytes(); assert sha(b)==r['stored_sha256'],str(p)
    raw=gzip.decompress(b); assert sha(raw)==r['raw_sha256'],key
    return raw
def load(key): return json.loads(read(key))
def csvout(path,rows):
    rows=list(rows); assert rows
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def key(lane,county,native): return f'AR:{lane}:{county}:'+urllib.parse.quote(native,safe='')
def rank(rows,field='votes'):
    rows=sorted(rows,key=lambda r:(-r[field],r['key']))
    total=sum(r[field] for r in rows);cum=0;cross=None
    result=[]
    for n,r in enumerate(rows,1):
        prev=cum;cum+=r[field]
        if cross is None and 5*cum>=4*total: cross=n
        result.append(dict(r,rank=n,cumulative_votes=cum,share_numerator=r[field],share_denominator=total,cumulative_share_numerator=cum))
    assert cross is not None
    stats=dict(units=len(rows),denominator=total,top15_count=min(15,len(rows)),top15_votes=sum(r[field] for r in rows[:15]),minimum80_count=cross,minimum80_votes=result[cross-1]['cumulative_votes'],preceding_count=cross-1,preceding_votes=result[cross-2]['cumulative_votes'] if cross>1 else 0,crossing_key=result[cross-1]['key'],crossing_geography=result[cross-1],remainder_count=len(rows)-cross,remainder_votes=total-result[cross-1]['cumulative_votes'],integer_threshold=(4*total+4)//5,tie_break='descending votes, then literal source-scoped key ascending')
    assert 5*stats['preceding_votes']<4*total<=5*stats['minimum80_votes']
    return result,stats
def vectors(choices,namefield='Name',votefield='TotalVotes'):
    out=collections.Counter()
    for c in choices: out[c[namefield]]+=c[votefield]
    return dict(out)
def pdftext(body):
    with tempfile.NamedTemporaryFile(suffix='.pdf') as f:
        f.write(body);f.flush()
        return subprocess.run(['pdftotext','-layout',f.name,'-'],capture_output=True,check=True).stdout.decode()
def xml_extract():
    raw=read('sos-2024-general-precinct-original',True);assert raw[:2]==b'PK'
    ns={'x':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    z=zipfile.ZipFile(io.BytesIO(raw));strings=[''.join(n.itertext()) for n in ET.fromstring(z.read('xl/sharedStrings.xml'))]
    doc=ET.fromstring(z.read('xl/worksheets/sheet1.xml'));header=None;relevant=[];all_inventory=collections.Counter();position=[]
    for row in doc.findall('x:sheetData/x:row',ns):
        cells=[];values=[]
        for c in row:
            v=c.find('x:v',ns);val=strings[int(v.text)] if c.get('t')=='s' else v.text if v is not None else None
            cells.append(dict(ref=c.get('r'),type=c.get('t'),v=v.text if v is not None else None,value=val));values.append(val)
        if header is None: header=values;continue
        d=dict(zip(header,values));all_inventory[d['contest']]+=1
        if d['contest']=='U.S. President':
            d['source_row']=int(row.get('r'));d['source_cells']=cells
            relevant.append(d)
    assert len(relevant)==19887 and len(header)==10
    assert all(len(r['source_cells'])==10 for r in relevant)
    gzjs('extracted/2024-xlsx-president-raw-rows.json.gz',dict(source_sha256=sha(raw),member='xl/worksheets/sheet1.xml',headers=header,rows=relevant,all_contests_inventory=dict(all_inventory)))
    return relevant,header,all_inventory
def main():
    checks={};orders={};stats={};all_native={};api_controls={};full_controls={};county_by_year={};turnout={};metadata_out={};differences=[]
    xlsx,headers,inventory=xml_extract()
    # Each lane is extracted independently before any cross-source joins.
    for year in [2024,2022,2020]:
        info=load(f'{year}-info');meta=load(f'{year}-metadata');state=load(f'{year}-federal-state');full=load(f'{year}-full')
        title='U.S. President' if year==2024 else 'U.S. Senate'
        cm=meta['response']['contests'];matches=[(cid,c) for cid,c in cm.items() if c['contestName']==title]
        assert len(matches)==1,(year,matches)
        cid,desc=matches[0];s=state['response']['contests'][cid]
        locs=info['response']['locations']; assert len(locs)==75
        metadata_out[str(year)]={k:v for k,v in info.items() if k!='response'}|dict(response={k:v for k,v in info['response'].items() if k!='locations'},contest=desc,source_receipts=[f'source/acquired/{year}-info.receipt.json',f'source/acquired/{year}-metadata.receipt.json'],state_contest=s)
        countymap={k:v['locationName'] for k,v in locs.items()}
        api_rows=[];raw_records=[];county_records=[];native_inventory=[];countyvectors={};countytotals={};statevector={desc['choices'][c['choiceID']]['name']:c['totalVotes'] for c in s['choices']}
        assert sum(statevector.values())==s['totalVotes']
        for fips,loc in locs.items():
            response=load(f'{year}-federal-{fips}');c=response['response']['contests'][cid]
            assert c['totalVotes']==s['locations'][fips]['totalVotes']
            cv={desc['choices'][v['choiceID']]['name']:v['totalVotes'] for v in c['choices']};countyvectors[fips]=cv;countytotals[fips]=c['totalVotes']
            assert sum(cv.values())==c['totalVotes']
            county_records.append(dict(county_fips=fips,county_name=loc['locationName'],source_contest_pointer=f'/response/contests/{cid}',raw_contest=c,source_id=f'{year}-federal-{fips}'))
            native_sum=collections.Counter();nvotes=0
            for nid,nloc in loc['locations'].items():
                native_inventory.append(dict(county_fips=fips,native_id=nid,raw_location=nloc,source_pointer=f'/response/locations/{fips}/locations/{nid}'))
            for nid,n in c['locations'].items():
                assert nid in loc['locations'],(year,fips,nid)
                name=loc['locations'][nid]['locationName'];nv={desc['choices'][v['choiceID']]['name']:v['totalVotes'] for v in n['choices']}
                assert len(nv)==len(n['choices']) # reject duplicated names rather than deduplicate
                assert sum(nv.values())==n['totalVotes']
                native_sum.update(nv);nvotes+=n['totalVotes']
                ptr=f'/response/contests/{cid}/locations/{nid}'
                raw_records.append(dict(source_id=f'{year}-federal-{fips}',source_pointer=ptr,county_fips=fips,native_id=nid,raw_location=loc['locations'][nid],raw_result=n))
                api_rows.append(dict(key=key(f'{year}-api',fips,nid),county_fips=fips,county_name=loc['locationName'],native_id=nid,native_name=name,votes=n['totalVotes'],candidates=nv,source_id=f'{year}-federal-{fips}',source_pointer=ptr,method_scope='voteType 1 All; no disaggregated methods in this result',write_in_choices=n.get('writeinChoices',n.get('writeInChoices')),ballots_cast=None,registered_voters=None,blank=None,undervotes=None,overvotes=None))
            assert dict(native_sum)==cv,(year,fips,'native candidate balance',native_sum,cv)
            assert nvotes==c['totalVotes']
        summed=collections.Counter()
        for v in countyvectors.values():summed.update(v)
        assert dict(summed)==statevector
        api_controls[str(year)]=dict(contest_id=cid,title=title,candidates=statevector,total_votes=s['totalVotes'],county_count=len(countymap),native_count=len(api_rows),native_inventory_count=len(native_inventory),native_missing_result=[r for r in native_inventory if key(f'{year}-api',r['county_fips'],r['native_id']) not in {t['key'] for t in api_rows}],isOfficial=info['isOfficial'],lastUpdated=info['lastUpdated'])
        all_native[f'{year}-api']=api_rows;county_by_year[str(year)]=dict(names=countymap,candidates=countyvectors,votes=countytotals)
        gzjs(f'extracted/{year}-api-original-relevant-records.json.gz',dict(state=state,metadata=desc,counties=county_records,native_records=raw_records,native_inventory=native_inventory))
        orders[f'{year}-api'],stats[f'{year}-api']=rank(api_rows)
        fc=[(i,c) for i,c in enumerate(full['ContestData']) if c['ContestName']==title];assert len(fc)==1
        fi,fc=fc[0];fnative=[];fcandidate_sum=collections.Counter();parent_candidates=collections.defaultdict(collections.Counter);wrappers=[]
        reverse={v.upper():k for k,v in countymap.items()};assert len(reverse)==75
        for wi,w in enumerate(fc['Counties']):
            fips=reverse[w['CountyName'].upper()];pn=collections.Counter()
            wrappers.append(dict(source_pointer=f'/ContestData/{fi}/Counties/{wi}',raw=w))
            for pi,p in enumerate(w['Precincts']):
                vector=vectors(p['Candidates']);assert len(vector)==len(p['Candidates']);assert sum(vector.values())==p['TotalVotes'];pn.update(vector)
                ptr=f'/ContestData/{fi}/Counties/{wi}/Precincts/{pi}'
                fnative.append(dict(key=key(f'{year}-full',fips,f'{wi}/{pi}'),county_fips=fips,county_name=w['CountyName'],native_id=None,native_name=p['PrecinctName'],votes=p['TotalVotes'],candidates=vector,source_id=f'{year}-full',source_pointer=ptr,source_wrapper_index=wi,source_precinct_index=pi,method_scope='All; no native method fields',ballots_cast=None,registered_voters=None,blank=None,undervotes=None,overvotes=None))
            assert dict(pn)==vectors(w['Candidates']);assert sum(pn.values())==w['TotalVotes']
            fcandidate_sum.update(pn);parent_candidates[fips].update(pn)
        assert dict(fcandidate_sum)==vectors(fc['Candidates']);assert sum(fcandidate_sum.values())==fc['TotalVotes']
        all_native[f'{year}-full']=fnative
        full_controls[str(year)]=dict(contest_position=fi,candidates=vectors(fc['Candidates']),total_votes=fc['TotalVotes'],county_wrapper_count=len(fc['Counties']),distinct_parents=len(parent_candidates),native_count=len(fnative),isOfficial=full['ElectionInfo']['IsOfficial'],api_difference={n:v-statevector.get(n,0) for n,v in vectors(fc['Candidates']).items()})
        gzjs(f'extracted/{year}-full-original-relevant-records.json.gz',dict(contest_position=fi,state={k:v for k,v in fc.items() if k!='Counties'},wrappers=wrappers,turnout=full['Turnout'],election_info=full['ElectionInfo']))
        orders[f'{year}-full'],stats[f'{year}-full']=rank(fnative)
        t=full['Turnout'];ct=t['CountyTurnout'];assert len(ct)==75
        ts=load(f'{year}-turnout-state');tc={f:load(f'{year}-turnout-{f}') for f in locs}
        assert set(ts['response']['locations'])==set(locs)
        for row in ct:
            f=reverse[row['CountyName'].upper()];r=tc[f]['response'];state_row=ts['response']['locations'][f]
            for field,ff in [('registeredVoters','RegisteredVoters'),('totalBallotsCast','VotesCast')]:
                assert r[field]==state_row[field]==row[ff]
            assert r['ballotsCast']==state_row['ballotsCast']
            assert sum(v['ballotsCast'] for v in r['ballotsCast'])==r['totalBallotsCast']
        assert sum(r['VotesCast'] for r in ct)==t['VotesCast']==ts['response']['totalBallotsCast']==info['turnout']['totalBallotsCast']
        assert sum(r['RegisteredVoters'] for r in ct)==t['RegisteredVoters']==ts['response']['registeredVoters']==info['turnout']['registeredVoters']
        gzjs(f'extracted/{year}-turnout-original-records.json.gz',dict(state=ts,counties=tc))
        turnout[str(year)]=dict(state_full=t,state_api=info['turnout'],state_turnout_api=ts['response'],county={reverse[r['CountyName'].upper()]:r for r in ct},native_turnout_returned_counts={f:len(r['response'].get('locations',{})) for f,r in tc.items()},registration_definition='Source RegisteredVoters; active/inactive scope and snapshot date not specified',ballot_definition='Source VotesCast; not candidate votes. API ballotsCast and ballotsReceived are published All-type totals, not outstanding ballots.',county_sum_ballots=sum(r['VotesCast'] for r in ct),county_sum_registration=sum(r['RegisteredVoters'] for r in ct))
        # Ballot and registration county distributions are separate sensitivity universes.
        for field in ['VotesCast','RegisteredVoters']:
            rows=[dict(key=key(f'{year}-full-{field}',reverse[r['CountyName'].upper()],r['CountyName']),county_fips=reverse[r['CountyName'].upper()],county_name=r['CountyName'],votes=r[field]) for r in ct]
            orders[f'{year}-county-{field}'],stats[f'{year}-county-{field}']=rank(rows)
        for fips,v in parent_candidates.items():
            for name,n in v.items():
                if n!=countyvectors[fips][name]:differences.append(dict(year=year,county_fips=fips,candidate=name,api=countyvectors[fips][name],full=n,full_minus_api=n-countyvectors[fips][name]))
        county_rows=[dict(key=key(f'{year}-api-county',fips,countymap[fips]),county_fips=fips,county_name=countymap[fips],votes=countytotals[fips]) for fips in countymap]
        orders[f'{year}-county-contest'],stats[f'{year}-county-contest']=rank(county_rows)
    # Preserve every source disagreement; a numerical doubling is not a repair license.
    native_comparisons={}
    for year in [2024,2022,2020]:
        aa={(r['county_fips'],r['native_name']):r for r in all_native[f'{year}-api']}
        ff={(r['county_fips'],r['native_name']):r for r in all_native[f'{year}-full']}
        assert len(aa)==len(all_native[f'{year}-api']) and len(ff)==len(all_native[f'{year}-full'])
        assert set(aa)==set(ff)
        changed=[]
        for pair,a in aa.items():
            f=ff[pair]
            if a['candidates']!=f['candidates']:
                changed.append(dict(county_fips=pair[0],native_name=pair[1],api=a,full=f,full_equals_twice_api=all(f['candidates'][c]==2*v for c,v in a['candidates'].items())))
        native_comparisons[str(year)]=dict(exact_literal_pair_coverage=len(aa),changed=changed,all_other_native_candidate_vectors_identical=True)
    js('extracted/publication-native-comparison.json',native_comparisons)
    # Primary XLSX: preserve literal pairs, including all published zeros.
    reverse={v.upper():k for k,v in county_by_year['2024']['names'].items()};native=collections.defaultdict(list)
    for row in xlsx:native[(row['county'],row['precinct'])].append(row)
    primary=[];methods=collections.Counter();candidate_county=collections.defaultdict(collections.Counter);x_api_diffs=[];matches=[]
    apilookup=collections.defaultdict(list)
    for r in all_native['2024-api']:apilookup[(r['county_name'],r['native_name'])].append(r)
    for (county,precinct),rows in native.items():
        fips=reverse[county];vector={r['choice']:int(r['total votes']) for r in rows};assert len(vector)==7==len(rows)
        for r in rows:
            assert sum(int(r[m]) for m in headers[5:9])==int(r['total votes'])
            for m in headers[5:9]:methods[m]+=int(r[m])
        v=sum(vector.values());candidate_county[fips].update(vector)
        api=apilookup.get((county,precinct),[]);match=api[0] if len(api)==1 else None
        exact_name_match=match
        if match and match['candidates']!=vector:
            x_api_diffs.append(dict(county=county,precinct=precinct,xlsx=vector,api=match['candidates'],api_key=match['key']))
            match=None
        primary.append(dict(key=key('2024-xlsx',fips,precinct),county_fips=fips,county_name=county,native_id=None,native_name=precinct,votes=v,candidates=vector,party_literals={r['choice']:r['party'] for r in rows},methods={m:sum(int(r[m]) for r in rows) for m in headers[5:9]},source_rows=[r['source_row'] for r in rows],source_id='sos-2024-general-precinct-original',source_pointer='xl/worksheets/sheet1.xml',matched_api_native_id=match['native_id'] if match else None,matched_api_key=match['key'] if match else None,match_basis='exact literal county/name plus identical seven-candidate vector' if match and match['candidates']==vector else 'unavailable or nonidentical',unit_type='source literal precinct/reporting unit; legal polygon and precinct vs administrative type unverified',ballots_cast=None,registered_voters=None,blank=None,undervotes=None,overvotes=None,write_in_scope='seven named ballot choices; no write-in field in XLSX'))
    js('extracted/2024-xlsx-api-native-disagreements.json',x_api_diffs)
    assert len(primary)==2841
    assert dict(candidate_county)==county_by_year['2024']['candidates']
    all_native['2024-xlsx']=primary;orders['2024-xlsx'],stats['2024-xlsx']=rank(primary)
    for method in headers[5:9]:
        slug=method.lower().replace(' ','-');lane='2024-xlsx-'+slug
        rows=[dict(key=r['key'],county_fips=r['county_fips'],county_name=r['county_name'],native_name=r['native_name'],votes=r['methods'][method],method=method,source_id=r['source_id'],source_rows=r['source_rows']) for r in primary]
        orders[lane],stats[lane]=rank(rows)
    gzjs('extracted/source-native-universes.json.gz',all_native)
    js('extracted/source-metadata.json',metadata_out)
    js('extracted/api-controls.json',api_controls);js('extracted/full-controls.json',full_controls);js('extracted/turnout-controls.json',turnout);js('extracted/full-vs-api-county-candidate-differences.json',differences)
    # Independent primary PDF county rows, all seven candidate cells.
    text=pdftext(read('sos-2024-general-state-original',True));(ROOT/'source/2024-official-report.txt').write_text(text)
    section=text.split('U.S. President',1)[1].split('U.S. Congress District 01',1)[0]
    pdf_candidates=re.findall(r'#\d-([^\n]+) \(([^)]+)\)',section);assert len(pdf_candidates)==7
    pdf_rows={};pdf_positions=[]
    for ln,line in enumerate(section.splitlines(),1):
        mt=re.match(r'^([A-Za-z][A-Za-z .]*?)\s{2,}((?:\d+\s+){7}\d+)\s*$',line)
        if mt:
            name=mt[1].strip();vals=list(map(int,mt[2].split()));pdf_rows[name]=vals;pdf_positions.append(dict(section_line=ln,raw_line=line,county=name,values=vals))
    assert len(pdf_rows)==76
    norm=lambda s:re.sub('[^A-Z]','',s.upper())
    name_to_fips={norm(v):k for k,v in county_by_year['2024']['names'].items()}
    for name,vals in pdf_rows.items():
        if name=='Totals':continue
        fips=name_to_fips[norm(name)];actual=candidate_county[fips]
        assert sum(vals[:-1])==vals[-1]
        assert [actual[n] for n,p in pdf_candidates]==vals[:-1],(name,actual,vals)
    assert pdf_rows['Totals'][:-1]==[sum(v[n] for v in candidate_county.values()) for n,p in pdf_candidates]
    js('extracted/2024-pdf-controls.json',dict(candidates=pdf_candidates,rows=pdf_positions,total=pdf_rows['Totals'],checked_county_candidate_cells=525))
    clerk_checks={}
    for year in [2024,2022,2020]:
        text=pdftext(read(f'clerk-{year}'));(ROOT/f'source/clerk-{year}.txt').write_text(text)
        section=text.split('ARKANSAS',1)[1].split('CALIFORNIA',1)[0]
        if year==2024:section=section.split('FOR UNITED STATES REPRESENTATIVE',1)[0]
        else:section=section.split('FOR UNITED STATES SENATOR',1)[1].split('FOR UNITED STATES REPRESENTATIVE',1)[0]
        lines=[line for line in section.splitlines() if re.search(r'\d[\d,]*\s*$',line)]
        numbers=[int(re.search(r'(\d[\d,]*)\s*$',line)[1].replace(',','')) for line in lines]
        assert sorted(numbers)==sorted(api_controls[str(year)]['candidates'].values()),(year,numbers)
        tokens={2024:{'Donald J. Trump/JD Vance':'Republican','Kamala D. Harris/Tim Walz':'Democratic','Robert F. Kennedy, Jr./Nicole Shanahan':'Independent','Chase Oliver/Mike ter Maat':'Libertarian','Jill Stein/Rudolph Ware':'Green','Peter Sonski/Lauren Onak':'American Solidarity','Michael Wood/John G. Pietrowski':'Prohibition'},2022:{'Senator John Boozman':'John Boozman','Natalie James':'Natalie James','Kenneth Cates':'Kenneth Cates'},2020:{'Senator Tom Cotton':'Tom Cotton','Ricky Dale Harrington Jr.':'Ricky Dale Harrington'}}[year]
        named_controls={}
        for name,token in tokens.items():
            matching=[line for line in lines if token in line];assert len(matching)==1,(year,token)
            value=int(re.search(r'(\d[\d,]*)\s*$',matching[0])[1].replace(',',''))
            assert value==api_controls[str(year)]['candidates'][name],(year,name,value)
            named_controls[name]=dict(clerk_identity_token=token,clerk_line=matching[0],votes=value)
        clerk_checks[str(year)]=dict(lines=lines,values=numbers,candidate_controls=named_controls,agrees_api=True,agrees_full=sorted(numbers)==sorted(full_controls[str(year)]['candidates'].values()))
    js('extracted/clerk-controls.json',clerk_checks)
    for lane,rows in orders.items():
        csvout(ROOT/'orders'/(lane+'.csv'),({k:(json.dumps(v,ensure_ascii=False,separators=(',',':')) if isinstance(v,(dict,list)) else v) for k,v in r.items()} for r in rows))
    js('orders/statistics.json',stats)
    # Compatibility county filename actually contains all native primary rows.
    csvout(STATE/'data/county-turnout.csv',({k:(json.dumps(v,ensure_ascii=False,separators=(',',':')) if isinstance(v,(dict,list)) else v) for k,v in r.items()} for r in orders['2024-xlsx']))
    parent_order=orders['2024-county-contest'];parents=[]
    for p in parent_order:
        f=p['county_fips'];natives={lane:[dict(key=r['key'],native_id=r.get('native_id'),native_name=r['native_name'],votes=r['votes'],source_id=r['source_id'],source_pointer=r['source_pointer'],source_rows=r.get('source_rows'),methods=r.get('methods'),matched_api_native_id=r.get('matched_api_native_id')) for r in rr if r['county_fips']==f] for lane,rr in all_native.items()}
        parents.append(dict(p,source_native_constituents=natives,source_scoped_county_controls={y:dict(api_candidate_votes=county_by_year[y]['candidates'][f],api_total_votes=county_by_year[y]['votes'][f],full_turnout=turnout[y]['county'][f],api_turnout=turnout[y]['state_turnout_api']['locations'][f]) for y in ['2024','2022','2020']},administrative_cases='Literal native names retained without inferred geometry; Central labels may be place names. Unknown type remains unknown.',current_2026_native_ids=None,current_2026_geometry_approval=None))
    st=stats['2024-xlsx'];ordered=orders['2024-xlsx'];priority=ordered[:st['minimum80_count']]
    contract=dict(schema_version='arkansas-turnout-v1',state='AR',state_fips='05',priority_basis='2024 U.S. President XLSX seven reported candidate votes, reconciled to official PDF/API/House Clerk',acceptance_status='pending independent peer and coordinator review; historical source inventory only',geographic_level='literal 2024 source county/precinct reporting units, not county substitution',coverage=dict(parents=75,primary_native_units=len(ordered),primary_candidate_rows=len(xlsx),complete_reported_source_universe=True,eligible_named_write_in_completeness=None,source_only_native_units=[r for r in ordered if r['matched_api_native_id'] is None],current_2026_native_coverage=None),statistics=st,top15_keys=[r['key'] for r in ordered[:15]],ordered_priority_keys=[r['key'] for r in priority],priority_parent_fips=sorted({r['county_fips'] for r in priority}),full_order=ordered,remainder_keys=[r['key'] for r in ordered[st['minimum80_count']:]],all75parents=parents,source_universe_counts={lane:len(rows) for lane,rows in all_native.items()},separate_sensitivity_statistics=stats,unavailable_cases=dict(eligible_write_in_order=None,eligible_write_in_minimum80=None,november_2026_order=None,november_2026_priority_keys=[],native_ballot_order=None,native_registration_order=None,native_blank_under_over=None,geometry_crosswalk=None),provenance=dict(primary_raw_sha256=sha(read('sos-2024-general-precinct-original',True)),source_pins='source/original-pins.json',source_receipts='source/acquired/',raw_extraction='extracted/2024-xlsx-president-raw-rows.json.gz',all_native='extracted/source-native-universes.json.gz'))
    js('priority-set.json',contract)
    county_table=[]
    for p in parent_order:
        f=p['county_fips'];row=dict(county_fips=f,county_name=p['county_name'])
        for year in ['2024','2022','2020']:
            row.update({f'{year}_api_contest_votes':county_by_year[year]['votes'][f],f'{year}_api_candidates':json.dumps(county_by_year[year]['candidates'][f],separators=(',',':')),f'{year}_full_ballots_cast':turnout[year]['county'][f]['VotesCast'],f'{year}_full_registered_voters':turnout[year]['county'][f]['RegisteredVoters']})
        county_table.append(row)
    csvout(ROOT/'extracted/all75-county-controls.csv',county_table)
    checks.update(primary_total=st['denominator'],primary_native_units=len(primary),primary_parents=75,primary_candidate_rows=len(xlsx),xlsx_all_rows=sum(inventory.values()),xlsx_all_contests=len(inventory),pdf_county_candidate_cells=525,api_all75_native_candidate_balances=True,primary_api_exact_native_matches=sum(r['matched_api_native_id'] is not None for r in primary),primary_api_unmatched=[dict(county=r['county_name'],name=r['native_name'],votes=r['votes'],key=r['key']) for r in primary if r['matched_api_native_id'] is None],primary_methods=dict(methods),api_controls=api_controls,full_controls=full_controls,clerk_checks=clerk_checks,ballot_registration_county_controls={y:{k:v for k,v in t.items() if k.startswith('county_sum')} for y,t in turnout.items()},all_rank_statistics=stats,source_vintage_differences_retained=len(differences),peer_agreement='unavailable: peer not launched; no acceptance inferred')
    js('build-checks.json',checks)
    print(json.dumps({k:v for k,v in checks.items() if k in ['primary_total','primary_native_units','primary_api_exact_native_matches','primary_api_unmatched','primary_methods','source_vintage_differences_retained']},indent=2))
if __name__=='__main__':main()
