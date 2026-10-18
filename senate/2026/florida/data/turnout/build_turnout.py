#!/usr/bin/env python3
"""Offline Florida original-source extraction and exact county-volume priority.
No rescaling, residual allocation, candidate-key collapse or cross-year native join.
"""
import collections,csv,gzip,hashlib,io,json,re,zipfile
from pathlib import Path
from urllib.parse import quote
from html_tables import Tables
from xlsx_cells import sheets
D=Path(__file__).resolve().parent;STATE=D.parent.parent;NEWS=D.parent/'news'
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def write_contract(x):
    p=D/'priority-set.json';b=(json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode();freeze=D/'priority-freeze.json'
    assert len(b)<40000000
    if freeze.exists():
        pin=json.loads(freeze.read_text())
        assert sha(b)==pin['sha256'] and len(b)==pin['bytes'],'Frozen priority would drift; refusing overwrite'
        assert p.read_bytes()==b,'Existing frozen priority bytes do not match reproducible build'
        return
    p.write_bytes(b)
def compact(x):return json.dumps(x,ensure_ascii=False,separators=(',',':'))
def gzjson(p,rows):p.write_bytes(gzip.compress((''.join(compact(x)+'\n' for x in rows)).encode(),mtime=0))
def csvout(p,rows):
    assert rows
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def body(sid):
    rec=json.loads((D/'source'/f'{sid}.receipt.json').read_text());b=(D/rec['stored_path']).read_bytes();assert sha(b)==rec['stored_sha256'];r=gzip.decompress(b);assert sha(r)==rec['raw_sha256'];assert rec['status']==200;return r
def primary(sid):
    rows=Tables(body(sid).decode('cp1252')).rows;header=rows[1][1:];county={};tot=None;positions={}
    for pos,row in enumerate(rows,1):
        if len(row)!=len(header)+1 or row[0] in ('County','% Votes'):continue
        values=[int(x.replace(',','')) for x in row[1:]]
        if row[0]=='Total':tot=dict(zip(header,values));continue
        assert row[0] not in county;county[row[0]]=dict(zip(header,values));positions[row[0]]=pos
    assert len(county)==67
    assert tot=={c:sum(x[c] for x in county.values()) for c in header}
    return dict(source_id=sid,candidates=header,county=county,statewide=tot,county_source_tr_1based=positions)
def normal(s):return s.upper().replace(' COUNTY','').replace('DE SOTO','DESOTO').strip()
def main():
    (D/'extracts').mkdir(exist_ok=True)
    # Rebuild from entity pins, never from later edits to the coordinator's mutable aggregate.
    pinfile=D/'source'/'shared-source-references.json'
    if pinfile.exists():
        pinned=json.loads(pinfile.read_text());lookup={sid:{**{k:v for k,v in r.items() if k!='relative_path'},'asset':Path(r['relative_path']).name} for sid,r in pinned.items()}
    else:
        manifest=json.loads((NEWS/'manifest.json').read_text());lookup={x['id']:x for x in manifest}
    ids=['dos-2024-precinct-official-storage-alias','dos-2022-precinct-official-storage-alias','dos-2020-precinct-zip','dos-precinct-schema-official-storage-alias','dos-2024-president-archive-20261009173646','nara-2024-index','nara-2024-ascertainment']
    refs={}
    for sid in ids:
        r=dict(lookup[sid]);p=NEWS/r['asset'];b=p.read_bytes();assert sha(b)==r['stored_sha256'];assert sha(gzip.decompress(b))==r['raw_sha256'];r['stored_bytes']=len(b);r['original_bytes']=len(gzip.decompress(b));r['relative_path']='../../news/'+r.pop('asset');refs[sid]=r
    dump(D/'source'/'shared-source-references.json',refs)
    primary_tables={key:primary(sid) for key,sid in [('2024_senate','dos-senate-2024-unencoded'),('2022_senate','dos-senate-2022-unencoded'),('2024_president','dos-president-2024-current'),('2020_president','dos-president-2020-current')]}
    # Independently parse archived presidential original, rather than trusting current bytes.
    archived=Tables(gzip.decompress((NEWS/lookup['dos-2024-president-archive-20261009173646']['asset']).read_bytes()).decode('cp1252')).rows
    assert archived==Tables(body('dos-president-2024-current').decode('cp1252')).rows
    dump(D/'extracts'/'primary-county-tables.json',primary_tables)
    controls=[]
    for context,t in primary_tables.items():
        for county,v in t['county'].items():
            for candidate,votes in v.items():controls.append(dict(context=context,county=county,candidate_party=candidate,votes=votes,source_id=t['source_id'],source_tr=t['county_source_tr_1based'][county],source_td_1based=t['candidates'].index(candidate)+2))
    csvout(D/'extracts'/'primary-county-candidates.csv',controls)
    eavs={};eavs_positions=[];fips={}
    keep=lambda k:k.startswith(('F1','F2','E1','C1','C8','B18')) or k in ['A1a','A1b','A1c','A1d','A1d_Other','A1Comments']
    for y in ['2024','2022']:
        z=zipfile.ZipFile(io.BytesIO(body('eavs-'+y)));assert z.testzip() is None
        name=[n for n in z.namelist() if n.lower().endswith('.csv')][0];b=z.read(name);rows=csv.DictReader(io.StringIO(b.decode('utf-8-sig')));out={}
        for pos,r in enumerate(rows,2):
            if r['State_Abbr']!='FL':continue
            k=r['FIPSCode'][:5];assert r['FIPSCode']==k+'00000';assert k not in out
            fips[normal(r['Jurisdiction_Name'])]=k;out[k]={key:v for key,v in r.items() if keep(key)}
            eavs_positions.append(dict(context=y,fips=k,county=r['Jurisdiction_Name'],source_id='eavs-'+y,source_member=name,source_csv_row_1based=pos,fields=out[k]))
        assert len(out)==67;eavs[y]=out
    gzjson(D/'extracts'/'eavs-controls.jsonl.gz',eavs_positions)
    book={};bookrows=[]
    for y in ['2024','2022']:
        sheet,rows=list(sheets(body('bookclosing-'+y)))[0];out={};total=None
        header={re.sub(r'\d','',k):v.strip() for r in rows for k,v in r.items() if re.sub(r'\D','',k)=='9'}
        tcol='T' if y=='2024' else 'N';pcol='U' if y=='2024' else 'O'
        for r in rows:
            a=[(k,v.strip()) for k,v in r.items() if re.match(r'^A\d+$',k)]
            if not a:continue
            cell,name=a[0];pos=re.sub(r'\D','',cell)
            if name=='Total':total=int(r[tcol+pos]);continue
            if normal(name) not in fips:continue
            key=fips[normal(name)];vals={header[re.sub(r'\d','',k)]:v for k,v in r.items() if re.sub(r'\d','',k) in header and v!=''}
            out[key]=dict(active=int(r[tcol+pos]),rep=int(r['B'+pos]),dem=int(r['C'+pos]),precincts=int(r[pcol+pos]));bookrows.append(dict(context=y,fips=key,source_id='bookclosing-'+y,sheet=sheet,row=int(pos),cells=r,labels=vals))
        assert len(out)==67 and sum(r['active'] for r in out.values())==total;book[y]=out
    gzjson(D/'extracts'/'bookclosing-controls.jsonl.gz',bookrows)
    diagnostics=[]
    for original in eavs_positions:
        f=original['fields'];numeric=lambda v:bool(re.fullmatch(r'\d+',v))
        regkeys=['A1b','A1c']+(['A1d'] if original['context']=='2024' else [])
        regdiff=int(f['A1a'])-sum(int(f[k]) for k in regkeys) if all(numeric(f[k]) for k in ['A1a']+regkeys) else None
        methkeys=['F1b','F1c','F1d','F1e','F1f','F1g','F1h'];known={k:int(f[k]) for k in methkeys if numeric(f.get(k,''))};unknown={k:f.get(k,'') for k in methkeys if not numeric(f.get(k,''))}
        diagnostics.append(dict(context=original['context'],fips=original['fips'],county=original['county'],source_member=original['source_member'],source_csv_row_1based=original['source_csv_row_1based'],registered_total_raw=f['A1a'],registered_components={k:f[k] for k in regkeys},registration_total_minus_components_if_all_available=regdiff,participation_F1a_raw=f['F1a'],known_method_fields=known,unknown_or_not_applicable_method_fields=unknown,sum_known_method_components_minus_F1a=sum(known.values())-int(f['F1a']),method_sum_scope='arithmetic diagnostic only; components not assumed disjoint, blank/sentinel not imputed zero',F1Comments=f.get('F1Comments'),F2_derivation={k:v for k,v in f.items() if k.startswith('F2')},A1Comments=f.get('A1Comments')))
    dump(D/'extracts'/'source-control-diagnostics.json',diagnostics)
    native={};members=[];raw_rows=[];countynames={};raw_totals={};county_raw={};native_contexts={};all_rows=0
    jobs=[('2024','dos-2024-precinct-official-storage-alias',{'100000':'2024_president','120000':'2024_senate'}),('2022','dos-2022-precinct-official-storage-alias',{'120000':'2022_senate'}),('2020','dos-2020-precinct-zip',{'100000':'2020_president'})]
    for year,sid,codes in jobs:
        z=zipfile.ZipFile(io.BytesIO(gzip.decompress((NEWS/lookup[sid]['asset']).read_bytes())));assert z.testzip() is None
        selected=[];units={}
        for info in z.infolist():
            b=z.read(info);recount='recount' in info.filename.lower();member=dict(year=year,source_id=sid,source_member=info.filename,bytes=len(b),sha256=sha(b),crc32=f'{info.CRC:08x}',recount_overlap_excluded=recount,all_rows=0,selected_rows=0);offset=0
            for pos,line in enumerate(b.splitlines(keepends=True),1):
                try:s=line.decode('utf-8-sig');encoding='utf-8-sig'
                except UnicodeDecodeError:s=line.decode('cp1252');encoding='cp1252'
                fields=s.rstrip('\r\n').split('\t')
                if not s.strip():offset+=len(line);continue
                assert len(fields)==19,(info.filename,pos,len(fields));member['all_rows']+=1;all_rows+=1
                if fields[13] not in codes:offset+=len(line);continue
                member['selected_rows']+=1;context=codes[fields[13]];code=fields[0];name=fields[1];countynames[code]=name;countyfips=fips[normal(name)]
                key='/'.join([context,code,fields[2],quote(fields[5],safe=''),quote(fields[6],safe='')]);ck=tuple(fields[14:18]);v=int(fields[18]);assert v>=0
                record=dict(source_id=sid,source_member=info.filename,source_row_1based=pos,source_byte_offset=offset,source_line_bytes=len(line),source_line_sha256=sha(line),source_encoding=encoding,context=context,native_key=key,recount_overlap_excluded=recount,fields=fields)
                selected.append(record);offset+=len(line)
                if recount:continue
                raw_totals.setdefault(context,collections.Counter())[ck]+=v;county_raw.setdefault((context,code),collections.Counter())[ck]+=v
                u=units.setdefault(key,dict(context=context,native_key=key,parent_key='county:'+countyfips,fips=countyfips,county_code=code,county=name,source_id=sid,source_member=info.filename,election_number=fields[2],election_date=fields[3],election_name=fields[4],precinct_id=fields[5],polling_location=fields[6],contest_name=fields[11],district=fields[12],contest_code=fields[13],method_scope='all methods combined; no method field in original19',native_type='submitted precinct identifier and polling label; geometry/physical status unverified',registration_observations=[],candidate_category_rows=[]))
                u['precinct_id_available']=bool(fields[5].strip())
                u['source_label_method_hint_only']=bool(re.search(r'absent|early|mail|provis|central|\bEV\b|\bVBM\b',fields[5]+' '+fields[6],re.I))
                u['method_scope']='not separately coded in original19; polling label retained, not a validated method'
                u['administrative_case']='source label identifies EV; administrative/physical classification and geometry unresolved' if fields[6].startswith('EV --') or fields[6]=='MAIN OFFICE EV' else 'polling-label identity retained; physical precinct/split/style classification unverified'
                reg=fields[7:11]
                if reg not in u['registration_observations']:u['registration_observations'].append(reg)
                u['candidate_category_rows'].append(dict(candidate_label=fields[14],party=fields[15],fvrs_id=fields[16],doe_candidate_id=fields[17],votes=v,source_row_1based=pos))
            member['encoding']=encoding;members.append(member)
        gzjson(D/'extracts'/f'native-source-rows-{year}.jsonl.gz',selected)
        for k,u in units.items():
            assert len(u['candidate_category_rows'])==len(set(tuple(r[x] for x in ['candidate_label','party','fvrs_id','doe_candidate_id']) for r in u['candidate_category_rows']))
            native_contexts.setdefault(u['context'],[]).append(u)
        native.update(units)
    dump(D/'extracts'/'original-member-inventory.json',members)
    gzjson(D/'extracts'/'native-units.jsonl.gz',list(native.values()))
    summary=[];discrepancies=[];candidate_sums=[]
    for context,t in primary_tables.items():
        byname={normal(k):v for k,v in t['county'].items()}
        for ck,v in raw_totals[context].items():
            label,party,fvrs,doe=ck;primary_key=f'{label} ({party})';control=t['statewide'].get(primary_key)
            candidate_sums.append(dict(context=context,candidate_label=label,party=party,fvrs_id=fvrs,doe_candidate_id=doe,native_compiled_votes=v,primary_named_valid_votes=control,universe='generic_writein_marks' if doe=='900' else 'overvotes' if doe=='901' else 'undervotes' if doe=='902' else 'named_ballot_candidate',native_minus_primary=None if control is None else v-control))
        for code,name in countynames.items():
            cr=county_raw[(context,code)];p=byname[normal(name)]
            for ck,v in cr.items():
                label,party,fvrs,doe=ck
                if doe in ('900','901','902'):continue
                cp=p[f'{label} ({party})']
                if v!=cp:discrepancies.append(dict(context=context,county=name,county_code=code,fips=fips[normal(name)],candidate=label,native_compiled_votes=v,primary_county_votes=cp,native_minus_primary=v-cp))
    csvout(D/'extracts'/'native-primary-candidate-controls.csv',candidate_sums);dump(D/'extracts'/'source-discrepancies.json',discrepancies)
    totals={k:sum(t['statewide'].values()) for k,t in primary_tables.items()}
    central={'BAY','CAL','ESC','HOL','JAC','OKA','SAN','WAL','WAS'}
    for code,name in countynames.items():
        f=fips[normal(name)];row=dict(geography_key='county:'+f,county=name,county_fips=f,source_county_code=code,timezone_scope='America/Chicago|America/New_York; split Gulf; do not infer precinct timezone' if code=='GUL' else 'America/Chicago' if code in central else 'America/New_York')
        for context,t in primary_tables.items():
            p=next(v for n,v in t['county'].items() if normal(n)==normal(name));cr=county_raw[(context,code)];row[context+'_candidate_votes']=sum(p.values());row[context+'_valid_named_writeins']=sum(v for k,v in p.items() if k.endswith('(WRI)'))
            for doe,suffix in [('900','generic_writein_marks'),('901','overvotes'),('902','undervotes')]:row[context+'_'+suffix]=sum(v for k,v in cr.items() if k[3]==doe)
            row[context+'_compiled_named_ballot_votes']=sum(v for k,v in cr.items() if k[3] not in ('900','901','902'))
            row[context+'_native_units']=sum(u['county_code']==code for u in native_contexts[context]);row[context+'_blank_ballots']='';row[context+'_native_method_detail']='unavailable; combined'
        for y in ['2024','2022']:
            row['eavs_'+y+'_counted_participation_F1a']=eavs[y][f]['F1a'];row['bookclosing_'+y+'_active_registered']=book[y][f]['active'];row['eavs_'+y+'_registered_total_A1a']=eavs[y][f]['A1a'];row['eavs_'+y+'_active_registered_A1b']=eavs[y][f]['A1b'];row['eavs_'+y+'_inactive_registered_A1c']=eavs[y][f]['A1c']
        summary.append(row)
    summary.sort(key=lambda r:(-r['2024_senate_candidate_votes'],r['county_fips']));cum=0;cross=None
    for rank,r in enumerate(summary,1):
        cum+=r['2024_senate_candidate_votes'];r['rank_2024_senate']=rank;r['state_share_2024_senate']=format(r['2024_senate_candidate_votes']/totals['2024_senate'],'.14f');r['cumulative_votes_2024_senate']=cum;r['cumulative_share_2024_senate']=format(cum/totals['2024_senate'],'.14f');r['top15']=int(rank<=15)
        if cross is None and 5*cum>=4*totals['2024_senate']:cross=rank
    for r in summary:r['minimum80']=int(r['rank_2024_senate']<=cross)
    csvout(D.parent/'county-turnout.csv',summary)
    total=totals['2024_senate'];top=sum(r['2024_senate_candidate_votes'] for r in summary[:15]);crossvotes=summary[cross-1]['cumulative_votes_2024_senate'];preceding=summary[cross-2]['cumulative_votes_2024_senate']
    sensitivities=[]
    for metric in ['2024_senate_candidate_votes','2024_president_candidate_votes','2022_senate_candidate_votes','2020_president_candidate_votes','eavs_2024_counted_participation_F1a','eavs_2022_counted_participation_F1a','bookclosing_2024_active_registered','bookclosing_2022_active_registered']:
        ordered=sorted(summary,key=lambda r:(-int(r[metric]),r['county_fips']));den=sum(int(r[metric]) for r in ordered);c=0;minimum=None
        for i,r in enumerate(ordered,1):
            c+=int(r[metric])
            if minimum is None and 5*c>=4*den:minimum=i;mv=c;prev=c-int(r[metric])
        sensitivities.append(dict(metric=metric,statewide=den,top15=sum(int(r[metric]) for r in ordered[:15]),minimum80_count=minimum,preceding_votes=prev,crossing_votes=mv,crossing_geography=ordered[minimum-1]['geography_key'],full_order=[r['geography_key'] for r in ordered],priority_counties_share_numerator=sum(int(r[metric]) for r in summary[:cross])))
    dump(D/'sensitivity.json',sensitivities)
    contract=dict(schema_version='fl-turnout-priority-v1',state='FL',target_election=dict(date='2026-11-03',type='special',senate_class='III',term_end='2029-01-03'),priority_basis=dict(context='2024_senate',date='2024-11-05',senate_class='I',source_id='dos-senate-2024-unencoded',universe='all six valid named candidates including Howard Knepper WRI; excludes generic marks/under/over',statewide_candidate_votes=total),status='pending_independent_peer_and_coordinator_review',coordinator_accepted=False,complete_coverage=dict(expected_county_count=67,actual_county_count=len(summary),disjoint_level='county supervisors; 67 mutually exclusive counties',native_context_counts={k:len(v) for k,v in native_contexts.items()},native_method_status='original19 fields combine methods; EAVS county participation methods separate, no candidate-by-method allocation',november_2026_native_crosswalk='unavailable; historical names/counts are not approval'),ordered_priority_keys=[r['geography_key'] for r in summary[:cross]],top15=dict(count=15,votes=top,denominator=total,exact_fraction=f'{top}/{total}'),minimum80=dict(count=cross,votes=crossvotes,denominator=total,preceding_count=cross-1,preceding_votes=preceding,crossing_key=summary[cross-1]['geography_key'],crossing_county_votes=summary[cross-1]['2024_senate_candidate_votes'],integer_proof=dict(preceding_times5=5*preceding,statewide_times4=4*total,crossing_times5=5*crossvotes)),all_unit_order=[dict(key=r['geography_key'],rank=r['rank_2024_senate'],name=r['county'],fips=r['county_fips'],source_county_code=r['source_county_code'],votes=r['2024_senate_candidate_votes'],cumulative_votes=r['cumulative_votes_2024_senate'],priority=bool(r['minimum80']),timezone_scope=r['timezone_scope']) for r in summary],remainder=dict(count=67-cross,votes=total-crossvotes,ordered_keys=[r['geography_key'] for r in summary[cross:]]),native_constituents=[],administrative_cases=dict(recount_members='retained in whole ZIP/member inventory; overlapping, excluded from selected base; no selected required contests',central_absentee_early='all source IDs/labels retained as submitted; combined method in ZIP cannot be disaggregated; administrative/method totals never added to county totals',valid_writein_native_allocation='unavailable in compiled ZIP; county-valid controls retained independently; no generic-to-valid conversion',geometry='unavailable in turnout assignment; no historical-to-November2026 equivalence'),evidence=dict(native_units='extracts/native-units.jsonl.gz',raw_selected='extracts/native-source-rows-{2024,2022,2020}.jsonl.gz',primary_county_candidates='extracts/primary-county-candidates.csv',member_inventory='extracts/original-member-inventory.json',source_conflicts='extracts/source-discrepancies.json',eavs_methods='extracts/eavs-controls.jsonl.gz'))
    for r in summary:
        uu=[u for u in native_contexts['2024_senate'] if u['county_code']==r['source_county_code']]
        contract['native_constituents'].append(dict(parent_key=r['geography_key'],constituent_count=len(uu),valid_named_writein_native_allocation=None,method_detail_available=False,units=[{k:u[k] for k in ['native_key','source_id','source_member','election_number','precinct_id','precinct_id_available','polling_location','contest_code','method_scope','native_type','source_label_method_hint_only','administrative_case']} for u in uu],other_contexts={c:[u['native_key'] for u in v if u['county_code']==r['source_county_code']] for c,v in native_contexts.items() if c!='2024_senate'}))
    # Each historical context is disjoint internally; never add years/contests together.
    fields=['native_key','parent_key','fips','county_code','source_id','source_member','election_number','election_date','precinct_id','precinct_id_available','polling_location','contest_code','method_scope','native_type','source_label_method_hint_only','administrative_case']
    for parent in contract['native_constituents']:
        code=next(r['source_county_code'] for r in summary if r['geography_key']==parent['parent_key'])
        parent['other_contexts']={c:dict(constituent_count=sum(u['county_code']==code for u in vv),units=[{k:u[k] for k in fields} for u in vv if u['county_code']==code]) for c,vv in native_contexts.items() if c!='2024_senate'}
        for u in parent['units']:u['source_rows_1based']=[r['source_row_1based'] for r in native[u['native_key']]['candidate_category_rows']]
    contract['coordinator_acceptance_path']='data/coordinator-priority-acceptance.json'
    contract['status']='worker_prepared_peer_agreed_external_coordinator_acceptance_required'
    contract['peer_agreement_path']='data/turnout/peer-agreement.json'
    for r in contract['all_unit_order']:
        r['ordinary_poll_close_2026_utc']=None if r['source_county_code']=='GUL' else '2026-11-04T01:00:00Z' if r['source_county_code'] in central else '2026-11-04T00:00:00Z'
        r['ordinary_election_admin_clock']=None if r['source_county_code']=='GUL' else r['timezone_scope']
        r['poll_hours_source']='source/gulf-election-day.receipt.json' if r['source_county_code']=='GUL' else 'source/poll-hours-law.receipt.json'
    contract['native_identity_exceptions']=[dict(context=c,native_key=u['native_key'],reason='precinct ID empty in source; distinguish by unchanged polling label and source row/member') for c,vv in native_contexts.items() for u in vv if not u['precinct_id_available']]
    contract['source_objects']=dict(primary_county_tables={c:dict(source_id=t['source_id'],receipt='source/'+t['source_id']+'.receipt.json',raw_sha256=json.loads((D/'source'/f"{t['source_id']}.receipt.json").read_text())['raw_sha256'],county_count=67,candidate_universe=t['candidates'],statewide_controls=t['statewide']) for c,t in primary_tables.items()},native_originals={y:dict(source_id=sid,reference='source/shared-source-references.json',raw_sha256=lookup[sid]['raw_sha256'],all_fields=19,recount_policy='retain overlapping originals; exclude from selected base') for y,sid,_ in jobs},methods=dict(candidate_by_method='unavailable in compiled schema; no candidate allocation from EAVS',source_native_labels='retained verbatim; hints are not validated method categories',county_participation='extracts/eavs-controls.jsonl.gz',eavs_2024_version='2.0 released2026-02-12',eavs_2022_version='1.1 released2023-12-18',method_fields=['F1a','F1b','F1c','F1d','F1e','F1f','F1g','F1h','F1Comments','F2_1','F2_2','F2_3','F2_4','F2_5','F2_Other','F2Comments'],non_additivity='county comments disclose UOCAVA/provisional overlaps, missing fields and vote-history differences; preserve sentinels; never sum method columns as disjoint without county proof'),registration=dict(source='extracts/bookclosing-controls.jsonl.gz',active_status=True,dates={'2024':'2024-10-07','2022':'2022-10-11'},eavs_status='A1a total/A1b active/A1c inactive/A1d other where supplied, survey election contexts vary; never replace bookclosing or repeated ZIP fields'),authority_directory=dict(source_index='source/supervisors-index.receipt.json',county_records='source/supervisor-{source_county_code}.receipt.json',expected=67,recovered_http200=67),administrative=dict(valid_named_writein_native_allocation=None,blank_ballot_native_counts=None,november2026_crosswalk=None,physical_precinct_geometry=None,ballot_style_crosswalk=None,source_labels_and_blank_ids='retained without repair; see native_identity_exceptions and all native constituents'))
    write_contract(contract)
    stats=dict(primary_statewide={k:t['statewide'] for k,t in primary_tables.items()},primary_totals=totals,all_original_rows=all_rows,selected_rows=sum(m['selected_rows'] for m in members),native_units={k:len(v) for k,v in native_contexts.items()},source_discrepancies=discrepancies,top15=contract['top15'],minimum80=contract['minimum80'],remainder=contract['remainder'],eavs_sums={y:{k:sum(int(r[k]) for r in rr.values() if re.fullmatch(r'\d+',r[k])) for k in ['F1a','A1a','A1b','A1c']} for y,rr in eavs.items()},bookclosing_sums={y:sum(r['active'] for r in rr.values()) for y,rr in book.items()})
    dump(D/'calculation.json',stats);print(json.dumps({k:v for k,v in stats.items() if k!='primary_statewide'},indent=2))
if __name__=='__main__':main()
