"""Offline build from frozen original receipts and independently extracted source rows.
Run extract_originals.py, extract_publications.py, pdf_controls.py first.
"""
import collections,csv,re,io
from fractions import Fraction
from common import *
def readrows(path):return [json.loads(l) for l in gzip.decompress((ROOT/path).read_bytes()).splitlines()]
def canon(name):
    name=re.sub(r'\([^)]*\)','',name)
    name=re.sub(r'^(DEM|REP|Ind|Lib)\s+','',name)
    if name.upper().startswith(('WRITE-IN','WRITE IN')):return 'writein'
    return re.sub('[^a-z0-9]','',name.lower())
def vec(r):
    f=r['fields'];return [int(f['total'])]+[int(f['group_'+str(i)]) for i in range(1,15)]
def plus(vs):return [sum(z) for z in zip(*vs)]
def rank(values,names,tiekeys=None):
    assert values and all(v is not None and v>=0 for v in values.values())
    order=sorted(values,key=lambda k:(-values[k],k if tiekeys is None else tiekeys[k]));total=sum(values.values());assert total>0
    cumulative=0;rows=[];cross=None
    for i,k in enumerate(order,1):
        cumulative+=values[k]
        rows.append(dict(rank=i,key=k,name=names[k],votes=values[k],cumulative_votes=cumulative,share_numerator=values[k],share_denominator=total,share_pct=100*values[k]/total,cumulative_pct=100*cumulative/total))
        if cross is None and 5*cumulative>=4*total:cross=i
    prior=sum(values[k] for k in order[:cross-1]);crossvotes=sum(values[k] for k in order[:cross]);top15=sum(values[k] for k in order[:15])
    assert 5*prior<4*total<=5*crossvotes
    return dict(total=total,order=rows,top15_keys=order[:15],top15_votes=top15,top15_exact_fraction=str(Fraction(top15,total)),top15_pct=100*top15/total,minimum80_count=cross,minimum80_keys=order[:cross],minimum80_votes=crossvotes,minimum80_pct=100*crossvotes/total,preceding_count=cross-1,preceding_votes=prior,preceding_pct=100*prior/total,crossing_key=order[cross-1],remainder_keys=order[cross:],remainder_votes=total-crossvotes,remainder_pct=100*(total-crossvotes)/total,integer_rule='5*cumulative >= 4*statewide',tie_rule='descending integer votes, then source member byte offset ascending' if tiekeys is not None else 'descending integer votes, then canonical key ascending')
def build():
    roots=readrows('extracts/selected-root-rows.jsonl.gz');work=readrows('extracts/workbook-selected-rows.jsonl.gz');hier=json.loads((ROOT/'extracts/municipal-hierarchy.json').read_text());html=json.loads((ROOT/'extracts/html-controls.json').read_text());pdf=json.loads((ROOT/'extracts/pdf-controls.json').read_text())
    # Census identification only: no population/geometry or precinct crosswalk inferred.
    cr=json.loads((ROOT/'source/acquired/census-municipal-ids.receipt.json').read_text());ct=Tree(original(cr)).root
    census={}
    for row in list(ct.all('tr'))[1:]:
        cells=[clean(x.text()) for x in row.children if isinstance(x,Node) and x.tag=='td']
        if len(cells)==24 and cells[7]!='County subdivisions not defined':census[cells[7]]=dict(geoid=cells[2],state=cells[3],county=cells[4],cousub=cells[5],name=cells[8],source_id=cr['id'])
    assert len(census)==39
    names={p['key']:p['name'] for p in hier};assert len(names)==39 and set(names.values())==set(census)
    native=[];municipal=[];reconciliations=[];controls=[]
    for year in ['2020','2022','2024']:
        ps=[p for p in hier if p['year']==year];assert len(ps)==39
        parent={c['code']:(p,c) for p in ps for c in p['children']};assert len(parent)==sum(len(p['children']) for p in ps)
        rr=[r for r in roots if year in r['source_id']];ww=[r for r in work if year in r['source_id'] and 'writeins' not in r['source_id']]
        codes=set(parent)|{r['fields']['reporting_code'] for r in rr}|{r['columns']['B'].zfill(4) for r in ww}
        bycode={}
        for code in sorted(codes):
            rs=[r for r in rr if r['fields']['reporting_code']==code];xs=[r for r in ww if r['columns']['B'].zfill(4)==code]
            rn={r['fields']['reporting_name'].rstrip() for r in rs};xn={r['columns']['A'] for r in xs};assert len(rn)<=1 and len(xn)<=1
            if code in parent:
                p,c=parent[code];key=p['key'];label=c['label'];parentproof=dict(source_id=p['source_id'],url=p['url'],raw_sha256=p['raw_sha256'],child_url=c['url'],label=label);geo_type='municipality'
            else:
                # Absence of a municipal parent is explicit, never allocated by code/name.
                assert code in ['9001','9002','9011','9012']
                key='RI:state-admin:'+code;label=next(iter(rn or xn));parentproof=None;geo_type='state_administrative';names[key]=label
            literal_name=next(iter(rn or xn));role='published_precinct_context'
            if geo_type=='state_administrative':role='federal_administrative_context'
            elif 'presidential' in literal_name.lower() or 'presidential' in label.lower():role='presidential_only_context'
            elif 'limited' in literal_name.lower() or 'limited' in label.lower():role='limited_ballot_context'
            stats={}
            for title in ['REGISTERED VOTERS - TOTAL','BALLOTS CAST - TOTAL','BALLOTS CAST - BLANK']:
                match=[r for r in xs if r['columns']['H']==title];assert len(match)<=1
                stats[title]=None if not match else dict(values=[int(match[0]['columns'].get(c,'0')or 0) for c in 'CDEF'],key=match[0]['key'],columns=match[0]['columns'])
            contests={}
            for title in (['Governor'] if year=='2022' else ['Presidential Electors For:','Senator in Congress']):
                rcs=[r for r in rs if r['fields']['contest_title'].strip()==title]
                if not rcs:contests[title]=dict(status='unavailable_in_source',candidate_rows=None,total=None,methods=None);continue
                assert len({r['fields']['candidate'] for r in rcs})==len(rcs)
                contests[title]=dict(status='published',candidate_rows=[r['key'] for r in rcs],candidate_fields=[r['fields'] for r in rcs],total=sum(int(r['fields']['total']) for r in rcs),methods=plus([vec(r)[1:] for r in rcs]),undervotes=None,overvotes=None,contest_ballots=None,unavailable_reason='Native technical/XLSX candidate views do not publish contest under/over/ballot fields')
            n=dict(key=f'RI:{year}:native:{code}',year=year,code=code,reporting_name=literal_name,raw_reporting_names=sorted(rn),workbook_reporting_names=sorted(xn),parent_key=key if geo_type=='municipality' else 'RI:state',dispatch_key=key,geography_type=geo_type,role=role,physical_geometry_status='unverified; native context is not proof of a physical precinct or current boundary',parent_proof=parentproof,source_row_keys=[r['key'] for r in rs],workbook_row_keys=[r['key'] for r in xs],statistics=stats,contests=contests)
            native.append(n);bycode[code]=n
        keys=sorted(set(n['dispatch_key'] for n in bycode.values()))
        for key in keys:
            ns=[n for n in bycode.values() if n['dispatch_key']==key];p=next((p for p in ps if p['key']==key),None)
            totals={}
            for title in (['Governor'] if year=='2022' else ['Presidential Electors For:','Senator in Congress']):
                available=[n for n in ns if n['contests'][title]['status']=='published']
                totals[title]=None if not available else dict(total=sum(n['contests'][title]['total'] for n in available),methods=plus([n['contests'][title]['methods'] for n in available]),published_native_keys=[n['key'] for n in available],unavailable_native_keys=[n['key'] for n in ns if n not in available],generic_writein=sum(int(f['total']) for n in available for f in n['contests'][title]['candidate_fields'] if canon(f['candidate_name'].strip())=='writein'))
            stats={}
            for title in ['REGISTERED VOTERS - TOTAL','BALLOTS CAST - TOTAL','BALLOTS CAST - BLANK']:
                aa=[n for n in ns if n['statistics'][title] is not None]
                stats[title]=dict(values=None if not aa else plus([n['statistics'][title]['values'] for n in aa]),available_native_keys=[n['key'] for n in aa],unavailable_native_keys=[n['key'] for n in ns if n not in aa],definition='Sum of published rows; missing native rows remain unavailable. Registration status/extract-date not specified beyond election/publication scope.')
            municipal.append(dict(year=year,key=key,name=names[key],geography_type='municipality' if p else 'state_administrative',municipal_fips=None if not p else census[p['name']],native_keys=[n['key'] for n in ns],contests=totals,statistics=stats,source_parent=p))
        for title in (['Governor'] if year=='2022' else ['Presidential Electors For:','Senator in Congress']):
            selected=[r for r in rr if r['fields']['contest_title'].strip()==title];candidate_groups=collections.defaultdict(list)
            for r in selected:candidate_groups[(r['fields']['contest'],r['fields']['candidate'],r['fields']['party'],r['fields']['candidate_name'])].append(r)
            for identity,rows in candidate_groups.items():
                v=plus([vec(r) for r in rows]); nm=canon(identity[3].strip());hc=[r for r in html if r['source_id']=={'2024':'ri-2024-general-old-authority','2020':'ri-2020-observed-state-summary','2022':'ri-2022-observed-historical-seed'}[year] and r['contest']==title and canon(r['candidate'])==nm];pc=[r for r in pdf if r['year']==year and r['contest']==title and canon(r['label'])==nm]
                assert len(hc)==len(pc)==1,(year,title,identity,nm,hc,pc)
                assert v[:4]==[hc[0]['total']]+[m['votes'] for m in hc[0]['methods']]==pc[0]['values']
                xcs=[r for r in ww if r['columns']['H']==title and canon(r['columns'].get('I',''))==nm]
                assert len(xcs)==len(rows)
                for row in rows:
                    f=row['fields'];xr=[r for r in xcs if r['columns']['B'].zfill(4)==f['reporting_code']];assert len(xr)==1
                    assert [int(xr[0]['columns'][c]) for c in 'CDEF']==vec(row)[:4]
                    assert xr[0]['columns']['A']==f['reporting_name'].strip()
                    assert xr[0]['columns'].get('G','').strip()==f['party'].strip()
                # Check each municipality's HTML control, retaining full original identity separately.
                for p in ps:
                    cs={c['code'] for c in p['children']};local=[r for r in rows if r['fields']['reporting_code'] in cs];hs=[r for r in html if r['source_id']==p['source_id'] and r['contest']==title and canon(r['candidate'])==nm];assert len(hs)==1
                    assert plus([vec(r) for r in local])[:4]==[hs[0]['total']]+[m['votes'] for m in hs[0]['methods']]
                reconciliations.append(dict(year=year,contest=title,source_native_contest=identity[0],source_native_candidate=identity[1],party=identity[2],candidate_name=identity[3],total_and_14_groups=v,native_count=len(rows),root_row_keys=[r['key'] for r in rows],html=hc[0],board_pdf=pc[0],board_workbook_rows=len(xcs),all_municipal_candidate_method_agreement=True))
            controls.append(dict(year=year,contest=title,candidate_total=sum(int(r['fields']['total']) for r in selected),native_count=len(set(r['fields']['reporting_code'] for r in selected)),board_pdf_non_candidate=[r for r in pdf if r['year']==year and r['contest']==title and (r['label'].strip().startswith(('Over','Under','Contest','Total Votes')))]))
    dump(ROOT/'native-inventory.json',native);dump(ROOT/'municipal-controls.json',municipal);dump(ROOT/'candidate-reconciliation.json',reconciliations);dump(ROOT/'state-controls.json',controls)
    rankings={}
    for year,title,key in [('2024','Senator in Congress','senate2024'),('2024','Presidential Electors For:','president2024'),('2020','Senator in Congress','senate2020'),('2020','Presidential Electors For:','president2020'),('2022','Governor','governor2022')]:
        ms=[m for m in municipal if m['year']==year and m['contests'][title] is not None];values={m['key']:m['contests'][title]['total'] for m in ms};rankings[key]=rank(values,names)
        rankings[key]['unavailable_geographies']=[m['key'] for m in municipal if m['year']==year and m['contests'][title]is None]
        if key=='senate2024':rankings['senate2024_named_only']=rank({m['key']:m['contests'][title]['total']-m['contests'][title]['generic_writein'] for m in ms},names)
    for year in ['2020','2022','2024']:
        for title,label in [('BALLOTS CAST - TOTAL','ballots'),('REGISTERED VOTERS - TOTAL','registration'),('BALLOTS CAST - BLANK','blank')]:
            ms=[m for m in municipal if m['year']==year and m['statistics'][title]['values']is not None]
            if ms:rankings[label+year]=rank({m['key']:m['statistics'][title]['values'][0] for m in ms},names)
    dump(ROOT/'rankings.json',rankings)
    primary=rankings['senate2024'];top=set(primary['top15_keys']);priority=set(primary['minimum80_keys'])|top
    contract=dict(schema='ri-turnout-priority-v1',state='RI',state_fips='44',election='2024-11-05',contest='0002 Senator in Congress',basis='root technical reported printed-candidate votes plus generic Write-in, reconciled to Board PDF and XLSX; eligibility unresolved',reporting_parent_type='39 municipalities plus four unallocated state administrative entries',coverage=dict(municipalities=39,state_administrative=4,senate_native=458,presidential_native=497),peer_agent_id=None,peer_agreement='pending; no peer derivative accessed',coordinator_acceptance='pending',current_2026_geographic_approval=False,ordered_priority_keys=[r['key'] for r in primary['order'] if r['key']in priority],complete_descending_order=primary['order'],top15={k:primary[k] for k in ['top15_keys','top15_votes','top15_exact_fraction','top15_pct']},minimum80={k:primary[k] for k in primary if k.startswith(('minimum80','preceding','crossing','remainder'))},all_geographies=[dict(**m,priority=m['key']in priority,top15=m['key']in top) for m in municipal if m['year']=='2024'],all_source_native_constituents=[n for n in native if n['year']=='2024'],historical_inventory_path='native-inventory.json',all_candidate_rows_path='extracts/selected-root-rows.jsonl.gz',all_raw_long_views_path='extracts/all-long-rows.jsonl.gz',limitations=['Native context IDs are source/year scoped; no November 2026 precinct identity/geometry approval','Administrative federal entries have no municipal parent or FIPS assignment','39 presidential-only contexts have unavailable Senate rows, never fabricated zero','Method groups4-14 have no published labels; registration/method administrative zeroes remain source values','Generic write-ins are not a verified universe of legally eligible named write-ins'])
    dump(ROOT/'priority-set.json',contract)
    rows=[]
    for order in primary['order']:
        k=order['key'];m=next(m for m in municipal if m['year']=='2024' and m['key']==k)
        row=dict(rank=order['rank'],geography_key=k,geography=m['name'],geography_type=m['geography_type'],municipality_fips=''if m['municipal_fips']is None else m['municipal_fips']['geoid'],state_fips='44',county_fips_context_only=''if m['municipal_fips']is None else '44'+m['municipal_fips']['county'],senate2024_votes=order['votes'],senate2024_generic_writein=m['contests']['Senator in Congress']['generic_writein'],senate2024_share=order['votes']/primary['total'],senate2024_cumulative_votes=order['cumulative_votes'],senate2024_cumulative_share=order['cumulative_votes']/primary['total'],top15=k in top,priority80=k in priority)
        for yr,ct,col in [('2024','Presidential Electors For:','president2024'),('2020','Senator in Congress','senate2020'),('2022','Governor','governor2022')]:
            mm=next(x for x in municipal if x['year']==yr and x['key']==k);c=mm['contests'][ct];row[col+'_votes']=''if c is None else c['total']
        for yr in ['2024','2022','2020']:
            mm=next(x for x in municipal if x['year']==yr and x['key']==k)
            for title,col in [('BALLOTS CAST - TOTAL','ballots'),('REGISTERED VOTERS - TOTAL','registration'),('BALLOTS CAST - BLANK','blank')]:
                st=mm['statistics'][title];row[col+yr]=''if st['values']is None else st['values'][0]
                row[col+yr+'_missing_native_count']=len(st['unavailable_native_keys'])
        rows.append(row)
    with (STATE/'data/county-turnout.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    # Parent arithmetic above is a sensitivity only. Canonical dispatch ranks each
    # actual native Senate source code, without replacing it by its parent.
    (ROOT/'parent-sensitivity.csv').write_bytes((STATE/'data/county-turnout.csv').read_bytes())
    contract.update(schema='ri-turnout-parent-sensitivity-v1',canonical_dispatch=False,peer_agent_id='5d9f9b63-0cf2-4b55-b52b-579cbc1d76d1')
    dump(ROOT/'parent-sensitivity.json',contract)
    natives=[n for n in native if n['year']=='2024' and n['contests']['Senator in Congress']['status']=='published']
    assert len(natives)==458
    rootbykey={r['key']:r for r in roots};anchor={}
    for n in natives:
        ar=min((rootbykey[k] for k in n['contests']['Senator in Congress']['candidate_rows']),key=lambda r:r['byte_offset'])
        anchor[n['key']]=dict(key=ar['key'],source_id=ar['source_id'],source_raw_sha256=ar['key'].split(':')[0],member=ar['member'],byte_offset=ar['byte_offset'],line=ar['line'])
    nn={anchor[n['key']]['key']:n['reporting_name'] for n in natives};ties={anchor[n['key']]['key']:anchor[n['key']]['byte_offset'] for n in natives}
    nr=rank({anchor[n['key']]['key']:n['contests']['Senator in Congress']['total'] for n in natives},nn,ties)
    nmap={anchor[n['key']]['key']:n for n in natives}
    for r in nr['order']:
        n=nmap[r['key']];r.update(native_key=n['key'],native_code=n['code'],parent_key=n['parent_key'],role=n['role'],source_anchor=anchor[n['key']])
    named=rank({anchor[n['key']]['key']:sum(int(f['total']) for f in n['contests']['Senator in Congress']['candidate_fields'] if canon(f['candidate_name'])!='writein') for n in natives},nn,ties)
    rankings['native_senate2024']=nr;rankings['native_senate2024_named_only']=named
    # Separate native comparisons, each with its own original election/contest scope.
    for yr,title,label in [('2024','Presidential Electors For:','native_president2024'),('2020','Senator in Congress','native_senate2020'),('2022','Governor','native_governor2022')]:
        ss=[n for n in native if n['year']==yr and n['contests'][title]['status']=='published'];v={n['key']:n['contests'][title]['total'] for n in ss};nm={n['key']:n['reporting_name'] for n in ss}
        rankings[label]=rank(v,nm)
    for label,field in [('native_ballots2024','BALLOTS CAST - TOTAL'),('native_registration2024','REGISTERED VOTERS - TOTAL')]:
        ss=[n for n in native if n['year']=='2024' and n['statistics'][field]is not None]
        rankings[label]=rank({n['key']:n['statistics'][field]['values'][0] for n in ss},{n['key']:n['reporting_name'] for n in ss})
    dump(ROOT/'rankings.json',rankings)
    prioritykeys=[r['key'] for r in nr['order'] if r['key'] in set(nr['minimum80_keys'])|set(nr['top15_keys'])]
    contract=dict(schema='ri-turnout-native-priority-v2',state='RI',state_fips='44',election='2024-11-05',contest='0002 Senator in Congress',basis='458 native source codes; root reported printed candidates plus generic Write-in; eligibility unverified',primary_geography='source-native reporting contexts; no polygon implication',coverage=dict(senate_native=458,presidential_native=497,unavailable_senate_contexts=39,municipal_parents=39,state_administrative_native=4),peer_agent_id='5d9f9b63-0cf2-4b55-b52b-579cbc1d76d1',peer_agreement='pending; no peer derivative accessed',coordinator_acceptance='pending',current_2026_geographic_approval=False,ordered_priority_keys=prioritykeys,complete_descending_order=nr['order'],top15={k:nr[k] for k in ['top15_keys','top15_votes','top15_exact_fraction','top15_pct']},minimum80={k:nr[k] for k in nr if k.startswith(('minimum80','preceding','crossing','remainder'))},all_source_native_constituents=[dict(**n,senate_source_anchor=anchor.get(n['key'])) for n in native if n['year']=='2024'],municipal_and_administrative_parent_sensitivity=dict(full_inventory=[m for m in municipal if m['year']=='2024'],rankings=primary,path='parent-sensitivity.json',canonical_dispatch=False),named_only_sensitivity=named,all_candidate_rows_path='extracts/selected-root-rows.jsonl.gz',all_raw_long_views_path='extracts/all-long-rows.jsonl.gz',historical_inventory_path='native-inventory.json',limitations=contract['limitations'])
    dump(ROOT/'priority-set.json',contract)
    nativecsv=[]
    for r in nr['order']:
        n=nmap[r['key']];ct=n['contests']['Senator in Congress'];a=anchor[n['key']]
        d=dict(rank=r['rank'],source_position_key=r['key'],native_key=n['key'],native_code=n['code'],native_name=n['reporting_name'],source_id=a['source_id'],archive_raw_sha256=a['source_raw_sha256'],member=a['member'],first_senate_record_byte_offset=a['byte_offset'],first_senate_record_line=a['line'],municipal_parent_key=''if n['geography_type']=='state_administrative' else n['parent_key'],state_parent_key='RI:state',role=n['role'],physical_geometry_status='unverified',senate2024_reported_candidate_generic_votes=r['votes'],share_numerator=r['votes'],share_denominator=nr['total'],cumulative_votes=r['cumulative_votes'],share_pct=r['share_pct'],cumulative_pct=r['cumulative_pct'],top15=r['key']in nr['top15_keys'],priority80=r['key']in prioritykeys)
        for i,v in enumerate(ct['methods'],1):d[f'group_{i}']=v
        for title,col in [('REGISTERED VOTERS - TOTAL','registration2024'),('BALLOTS CAST - TOTAL','election_ballots2024'),('BALLOTS CAST - BLANK','election_blank2024')]:d[col]=''if n['statistics'][title]is None else n['statistics'][title]['values'][0]
        d.update(senate_contest_ballots='',senate_undervotes='',senate_overvotes='',valid_named_writeins='')
        for f in ct['candidate_fields']:
            cd=f['candidate'];d['candidate_'+cd+'_name']=f['candidate_name'];d['candidate_'+cd+'_party']=f['party'];d['candidate_'+cd+'_votes']=int(f['total'])
        nativecsv.append(d)
    with (STATE/'data/county-turnout.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(nativecsv[0]));w.writeheader();w.writerows(nativecsv)
    print(json.dumps({k:{j:v for j,v in r.items() if j not in ['order','remainder_keys','top15_keys','minimum80_keys']} for k,r in rankings.items()},indent=2))
    return rankings
if __name__=='__main__':build()
