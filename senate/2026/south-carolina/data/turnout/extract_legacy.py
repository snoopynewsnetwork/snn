"""Independently extract complete required-contest/public XML originals offline.

Reuse all138 county originals read-only with pinned hashes/metadata. Retain the
entire ZIP and every XML member via references; no unrelated-office derivative.
"""
import collections,csv,gzip,io,json,os,zipfile,xml.etree.ElementTree as E
from pathlib import Path
from acquire import H,S,body,sha
from build_turnout import dump,csvout,rank

PEER=H.parent/'baselines/source'
SPECS={'2024-pres':(2024,'President and Vice President',{'CON':8261,'UNC':8260,'GRN':6882,'REP':27,'LIB':8258,'DEM':7553,'WRK':8259}),
 '2020-senate':(2020,'U.S. Senate',{'CON':2268,'REP':3254,'DEM':3255,'NON':6}),
 '2022-senate':(2022,'U.S. Senate',{'REP':3536,'DEM':870,'NON':6}),
 '2022-governor':(2022,'Governor and Lieutenant Governor',{'REP':3471,'DEM':3473,'LIB':3472,'NON':6})}
def original(sid,shared=False):
    p=PEER/(sid+'.meta.json')if shared else S/(sid+'.meta.json')
    m=json.loads(p.read_text());assert m['http_status']==200
    zbytes=(p.parent/m['body_path']).read_bytes();assert sha(zbytes)==m['stored_sha256']and len(zbytes)==m['stored_bytes']
    raw=gzip.decompress(zbytes)if m.get('stored_encoding','gzip')=='gzip'else zbytes
    assert sha(raw)==m['original_sha256']and len(raw)==m['original_bytes']
    z=zipfile.ZipFile(io.BytesIO(raw));assert not z.testzip();assert z.namelist()==['detail.xml'];xml=z.read('detail.xml')
    ref=dict(source_id=sid,metadata_path=os.path.relpath(p,H),body_path=os.path.relpath((p.parent/m['body_path']).resolve(),H),stored_sha256=m['stored_sha256'],stored_bytes=m['stored_bytes'],original_sha256=m['original_sha256'],original_bytes=m['original_bytes'],stored_encoding=m.get('stored_encoding','gzip'),requested_url=m['requested_url'],final_url=m['final_url'],retrieved_utc=m['retrieved_utc'],http_status=m['http_status'],zip_member='detail.xml',xml_member_sha256=sha(xml),xml_member_bytes=len(xml))
    return E.fromstring(xml),ref
def main():
    existing=list(csv.DictReader((H/'../county-turnout.csv').open()));fips={r['county']:r['county_fips']for r in existing}
    pos=[];cells=[];turnout=[];native=[];refs={};checks={};rosters={};candidateidentity=[];state_controls={}
    def save(sid,ptr,el,label,context):
        pos.append(dict(source_id=sid,source_pointer=ptr,contest_label=label,context=context,tag=el.tag,attributes=dict(el.attrib),text=el.text))
    def descend(sid,ptr,el,label,context):
        save(sid,ptr,el,label,context)
        for i,ch in enumerate(el):descend(sid,ptr+f'/{ch.tag}[{i}]',ch,label,context)
    for year in [2024,2022,2020]:
        sid=f'legacy{year}-detailxml';r,ref=original(sid);refs[sid]=ref
        state_controls[str(year)]=dict(source_id=sid,timestamp=r.findtext('Timestamp'),election_name=r.findtext('ElectionName'),date=r.findtext('ElectionDate'),region=r.findtext('Region'),election_voter_turnout=dict(r.find('ElectionVoterTurnout').attrib))
        for i,e in enumerate(r):
            if e.tag in ['Timestamp','ElectionName','ElectionDate','Region','ElectionVoterTurnout']:descend(sid,f'/ElectionResult/{e.tag}[{i}]',e,None,'state election metadata/turnout')
        for i,co in enumerate(r.find('ElectionVoterTurnout').find('Counties')):
            turnout.append(dict(year=year,source_id=sid,source_pointer=f'/ElectionResult/ElectionVoterTurnout/Counties/County[{i}]',level='state_county_control',county=co.attrib['name'],county_fips=fips[co.attrib['name']],native_name=None,**{k:co.attrib.get(k)for k in ['totalVoters','ballotsCast','voterTurnout','precinctsParticipating','precinctsReported','precinctsReportingPercent']},raw_attributes=json.dumps(co.attrib,separators=(',',':'))))
    for label,(year,title,mapping)in SPECS.items():
        r,_=original(f'legacy{year}-detailxml');statecontest=next(c for c in r.findall('Contest')if c.attrib['text']==title);statechoices={mapping[c.attrib['party']]:c for c in statecontest.findall('Choice')}
        cchecks=[];allcounty=[];allnative=[];rosters[label]={}
        g=json.loads(body(label+'-combined'))['data']['contestGranularData'];mg=json.loads(body(label+'-methods'))['data']['contestGranularData'];methods={int(v['id']):v['name']for v in mg['voteChannels']};db={c['division']['name']:c for c in g['divisions']['children']};dbm={c['division']['name']:c for c in mg['divisions']['children']}
        for ci,c in enumerate(r):
            if c is statecontest:descend(f'legacy{year}-detailxml',f'/ElectionResult/Contest[{ci}]',c,label,'state required contest')
        countychoices=collections.defaultdict(int);countyvotes=collections.Counter();native_total=0
        for cname,cfips in fips.items():
            if year==2022 and cname=='Clarendon':
                rosters[label][cfips]=[];continue # XML disabled: original TXT/JSON extracted separately, never imputed.
            sid=f'legacy{year}-county-{cname.lower()}';root,ref=original(sid,True);refs[sid]=ref
            assert root.findtext('Region')==cname
            matches=[(i,c)for i,c in enumerate(root)if c.tag=='Contest'and ' '.join(c.attrib['text'].split())==title];assert len(matches)==1,(label,cname)
            ordinal,c=matches[0];base=f'/ElectionResult/Contest[{ordinal}]';descend(sid,base,c,label,'county required contest')
            vt=root.find('VoterTurnout');save(sid,'/ElectionResult/VoterTurnout',vt,label,'county election turnout')
            for j,p in enumerate(vt.find('Precincts')):
                save(sid,f'/ElectionResult/VoterTurnout/Precincts/Precinct[{j}]',p,label,'native election turnout')
                turnout.append(dict(year=year,source_id=sid,source_pointer=f'/ElectionResult/VoterTurnout/Precincts/Precinct[{j}]',level='county_native_turnout',county=cname,county_fips=cfips,native_name=p.attrib['name'],**{k:p.attrib.get(k)for k in ['totalVoters','ballotsCast','voterTurnout','precinctsParticipating','precinctsReported','precinctsReportingPercent']},raw_attributes=json.dumps(p.attrib,separators=(',',':'))))
            names=[];native_counts=collections.defaultdict(dict);sourcepath=collections.defaultdict(list);flags=[]
            for k,ca in enumerate(c.findall('Choice')):
                choice_child_index=list(c).index(ca)
                party=ca.attrib.get('party');comparison_party='NON'if party is None and ca.attrib['text']=='Write-In'else party;cid=mapping[comparison_party];candidateidentity.append(dict(contest=label,county=cname,source_id=sid,choice_attributes=ca.attrib,history_candidate_id=cid,history_party_id=next(x['partyId']for x in g['candidates']if x['candidateId']==cid),identity_note='original CON is Constitution; historicalDBparty274 labels Conservative'if label=='2020-senate'and cid==2268 else'cross-source candidate mapping by explicit original slate/name/party and statewide total; no candidate ID equivalence inferred'))
                votes=int(ca.attrib['totalVotes']);countychoices[cid]+=votes;countyvotes[cname]+=votes
                assert votes==next(x['votes']for x in db[cname]['granularRow']if x['candidateId']==cid)
                methodsum=0
                for mi,method in enumerate(ca.findall('VoteType')):
                    method_child_index=list(ca).index(method)
                    mname=method.attrib['name'];mv=int(method.attrib['votes']);methodsum+=mv
                    compare_name={'Provionsal':'Provisional'}.get(mname,mname) # explicit source spelling alias, raw label retained
                    expected=next(x['votes']for x in dbm[cname]['granularRow']if x['candidateId']==cid and methods[x['voteChannelId']]==compare_name)
                    assert mv==expected
                    childsum=sum(int(p.attrib['votes'])for p in method)
                    if childsum!=mv:flags.append(dict(candidate_id=cid,method=mname,parent=mv,children=childsum))
                    seen=[]
                    for pi,p in enumerate(method):
                        pname=p.attrib['name'];seen.append(pname)
                        if pname not in names:names.append(pname)
                        key=(cid,mname);assert key not in native_counts[pname]
                        native_counts[pname][key]=int(p.attrib['votes']);ptr=base+f'/Choice[{choice_child_index}]/VoteType[{method_child_index}]/Precinct[{pi}]';sourcepath[pname].append(ptr)
                        cells.append(dict(contest_label=label,source_id=sid,county=cname,county_fips=cfips,contest_key=c.attrib['key'],choice_key=ca.attrib['key'],choice_text=ca.attrib['text'],party=party,history_candidate_id=cid,method=mname,native_name=pname,native_ordinal=pi,votes=int(p.attrib['votes']),source_pointer=ptr,raw_attributes=json.dumps(p.attrib,separators=(',',':'))))
                    assert len(seen)==len(set(seen)),(sid,'duplicate native names within single scope')
                assert methodsum==votes
            roster=[]
            for i,name in enumerate(names):
                counts=native_counts[name];available=len(counts);expected=len(c.findall('Choice'))*6
                value=sum(counts.values())if available==expected else None
                rec=dict(contest_label=label,source_id=sid,geography_key=f'SC:enr:{label}:{cfips}:unit:{i}',county=cname,county_fips=cfips,name=name,source_native_id=None,native_ordinal=i,contest_key=c.attrib['key'],candidate_votes=value,available_candidate_method_cells=available,expected_candidate_method_cells=expected,identity_status='administrative source name; no polygon inferred'if name in ['Failsafe','Failsafe Provisional','Provisional']else'original reporting identity; no DB/physical/current crosswalk asserted',source_pointers=sourcepath[name][:1],complete_positions_reference='extracts/legacy-candidate-methods.csv.gz filtered source_id/contest/native_name')
                native.append(rec);roster.append(rec);allnative.append(dict(geography_key=rec['geography_key'],name=name,county=cname,candidate_votes=value));native_total+=value if value is not None else 0
            rosters[label][cfips]=roster
            allcounty.append(dict(geography_key='SC:'+cfips,name=cname,candidate_votes=countyvotes[cname]))
            cchecks.append(dict(county=cname,source_id=sid,contest_attributes=c.attrib,turnout_attributes=vt.attrib,native_candidate_contexts=len(names),native_turnout_contexts=len(vt.find('Precincts')),method_rollup_residuals=flags,candidate_total=countyvotes[cname],native_candidate_sum=sum(sum(v.values())for v in native_counts.values()),turnout_native_reg_sum=sum(int(p.attrib['totalVoters'])for p in vt.find('Precincts')),turnout_native_ballots_sum=sum(int(p.attrib['ballotsCast'])for p in vt.find('Precincts'))))
        state_differences={str(cid):int(ca.attrib['totalVotes'])-countychoices[cid]for cid,ca in statechoices.items()}
        if year!=2022:assert not any(state_differences.values())
        else:
            for cid,delta in state_differences.items():assert delta==next(x['votes']for x in db['Clarendon']['granularRow']if x['candidateId']==int(cid))
        order,stat=rank(allcounty,'candidate_votes');nativeorder,nstat=rank(allnative,'candidate_votes');csvout(f'extracts/{label}-legacy-native-order.csv',nativeorder)
        checks[label]=dict(state_choice_totals={str(k):int(v.attrib['totalVotes'])for k,v in statechoices.items()},county_ranking=stat,native_ranking=nstat,counties=cchecks,native_total=native_total,XML_missing_counties=['Clarendon']if year==2022 else[],XML_state_minus_county_candidates=state_differences,method_alias_rule={'raw_Provionsal':'comparison_Provisional; original label preserved'})
    (H/'extracts/legacy-source-positions.jsonl.gz').write_bytes(gzip.compress(b''.join((json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n').encode()for r in pos),mtime=0))
    csvout('extracts/legacy-candidate-methods.csv.gz',cells);csvout('extracts/legacy-turnout-controls.csv.gz',turnout)
    csvout('extracts/legacy-native-units.csv.gz',({**r,'source_pointers':json.dumps(r['source_pointers'],separators=(',',':'))}for r in native))
    dump('legacy-observations.json',refs);dump('legacy-reconciliation.json',dict(source_positions=len(pos),candidate_method_native_rows=len(cells),native_rows=len(native),turnout_rows=len(turnout),state_election_controls=state_controls,contests=checks));dump('legacy-native-rosters.json',rosters);dump('legacy-candidate-identities.json',candidateidentity)
    # Extend the contract and compatibility table without altering DB/VHM scopes.
    contract=json.loads((H/'priority-set.json').read_text());contract['legacy_source_observations']=refs;contract['legacy_state_election_controls']=state_controls
    contract['voter_history_geographic_scope']='Literal requested-county history response labels; physical election-day membership/current-address relationship unresolved. Sparse names resembling other counties remain unchanged; raw county is null in precinct rows. No physical or cross-year crosswalk.'
    for c in contract['counties']:c['original_enr_constituents']={label:rosters[label][c['county_fips']]for label in SPECS}
    dump('priority-set.json',contract)
    for r in existing:
        for year in [2024,2022,2020]:
            control=next(x for x in turnout if x['year']==year and x['county']==r['county']and x['level']=='state_county_control')
            r[f'enr_{year}_election_registered_control']=control['totalVoters'];r[f'enr_{year}_election_ballots_control']=control['ballotsCast'];r[f'enr_{year}_source_turnout_percent']=control['voterTurnout']
    csvout('../county-turnout.csv',existing)
    print(json.dumps(dict(source_positions=len(pos),native_rows=len(native),candidate_method_rows=len(cells),counties={k:len(v['counties'])for k,v in checks.items()},statecontrols=state_controls),indent=2))
if __name__=='__main__':main()
