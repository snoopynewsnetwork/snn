#!/usr/bin/env python3
"""Independent ordered extraction of retained primary HTTP entities. Standard library only."""
import csv,gzip,hashlib,io,json,pathlib,collections
R=pathlib.Path(__file__).resolve().parents[1]; S=R.parents[1]; T=S/'data/turnout/source'; N=S/'data/news'
def sha(b): return hashlib.sha256(b).hexdigest()
def dump(name,x): (R/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def csvout(name,rows):
    rows=list(rows)
    if not rows:return
    p=R/name; fields=list(rows[0]);buf=io.StringIO(newline='');w=csv.DictWriter(buf,fields);w.writeheader();w.writerows(rows)
    b=buf.getvalue().encode();p.write_bytes(gzip.compress(b,mtime=0) if name.endswith('.gz') else b)
def txt(x):
    if x is None:return ''
    if isinstance(x,str):return x
    return next((a.get('text') or '' for a in x if a.get('languageId')=='en'), (x[0].get('text') or '') if x else '')
refs=[]
def read(p,meta=None,role='input'):
    z=p.read_bytes(); b=gzip.decompress(z) if p.suffix=='.gz' else z
    if meta:
        assert sha(b)==meta['raw_sha256'],p
        assert sha(z)==meta['stored_sha256'],p
    refs.append({'path':str(p.relative_to(S)),'role':role,'stored_bytes':len(z),'stored_sha256':sha(z),'raw_bytes':len(b),'raw_sha256':sha(b),'http_metadata_path':str(meta_path.relative_to(S)) if (meta_path:=p.with_name(p.name.replace('.body.gz','.http.json'))).exists() else None,'acquisition':meta})
    return b
fipsrows=list(csv.DictReader(io.StringIO(read(T/'county-fips-2020.body.gz',json.load(open(T/'county-fips-2020.http.json'))).decode()),delimiter='|'))
fips={r['COUNTYNAME']:r['STATEFP']+r['COUNTYFP'] for r in fipsrows if r['STATE']=='GA'};assert len(fips)==159
requests=json.load(open(T/'requests-counties.json'));assert len(requests)==795
states={}
for ref in json.load(open(T/'shared-references.json')):
    states[ref['election_key']]=json.loads(read(S/ref['path'],ref,'state-selected'))
states['2020NovGen']=json.loads(read(T/'state-2020-selected.body.gz',json.load(open(T/'state-2020-selected.http.json')),'state-selected'))
long=[];units=[];base=[];controls=[];checks=[];clocks=[]
def options_rows(d,e,cf,cn,sid,level,unit,un,pos,opts,pointer):
    seen=set()
    for i,o in enumerate(opts):
        assert o['id'] not in seen,(sid,pointer,o['id']);seen.add(o['id'])
        common=dict(election_key=e,county_fips=cf,county_name=cn,source_id=sid,source_pointer=pointer+f'/{i}',unit_level=level,native_GUID=unit,native_name=un,native_position=pos,candidate_GUID=o['id'],nativeId=o.get('nativeId'),candidate_ordinal=i,candidate_name=txt(o['name']),party=(o.get('party') or {}).get('abbreviation'),isWriteIn=o.get('isWriteIn'),isQualifiedWriteIn=o.get('isQualifiedWriteIn'))
        long.append({**common,'group_GUID':'','group_name':'TOTAL','group_ordinal':-1,'votes':o['voteCount']})
        groups=o.get('groupResults') or [];seen_g=set()
        for j,g in enumerate(groups):
            assert g['groupId'] not in seen_g;seen_g.add(g['groupId'])
            long.append({**common,'source_pointer':common['source_pointer']+f'/groupResults/{j}','group_GUID':g['groupId'],'group_name':txt(g['groupName']),'group_ordinal':j,'votes':g['voteCount']})
        if groups: checks.append({'kind':'candidate_method_sum','source_id':sid,'pointer':pointer+f'/{i}','difference':sum(g['voteCount'] for g in groups)-o['voteCount'] if o['voteCount'] is not None and all(g['voteCount'] is not None for g in groups) else None})
def derive(e,cf,cn,uid,un,sid,pointer,opts,total,ballots,reg,level):
    a=[o for o in opts if txt(o['name']).endswith('(Dem)')];b=[o for o in opts if txt(o['name']).endswith('(Rep)')];assert len(a)==len(b)==1
    av=a[0]['voteCount'];bv=b[0]['voteCount'];pair=av+bv if av is not None and bv is not None else None
    complete=all(o['voteCount'] is not None for o in opts)
    named=sum(o['voteCount'] for o in opts if e!='2024NovGen' or txt(o['name']) in ['Donald J. Trump (Rep)','Kamala D. Harris (Dem)','Chase Oliver (Lib)','Jill Stein (Grn)']) if complete else None
    return dict(election_key=e,county_fips=cf,county_name=cn,unit_level=level,native_GUID=uid,native_name=un,source_id=sid,source_pointer=pointer,A_name=txt(a[0]['name']),A_party='Dem',A=av,B_name=txt(b[0]['name']),B_party='Rep',B=bv,pair_votes=pair,source_alloption_votes=sum(o['voteCount'] for o in opts) if complete else None,source_voteTotal=total,named_valid_option_votes=named,other_named_valid_votes=named-pair if named is not None and pair is not None else None,void_option_votes=sum(o['voteCount'] for o in opts)-named if complete else None,additional_qualified_writeins=None if e=='2024NovGen' else '',all_valid_candidate_denominator_status='redacted_native_options' if not complete else 'named_four_only_county_qualified_writeins_unknown' if e=='2024NovGen' else 'published_options_no_additional_Senate_writeins_observed',A_pair_share=av/pair if pair else None,A_minus_B_net=av-bv if pair is not None else None,pair_margin_pp=100*(av-bv)/pair if pair else None,named_allvote_margin_pp=100*(av-bv)/named if named and pair is not None else None,historical_winner='unknown' if pair is None else 'A' if av>bv else 'B' if bv>av else 'tie',closeness_band='unknown' if not pair else 'within_5pp' if abs(av-bv)/pair<=.05 else '5_to_10pp' if abs(av-bv)/pair<=.1 else 'over_10pp',ballots_cast=ballots,registered_voters=reg,ballot_registration_scope='source_election_and_native_turnout; status/date_not_defined' if ballots is not None else 'unavailable_zero_placeholders',underVoteCount=None,overVoteCount=None)
for req in requests:
    sid=req['id'];e=req['election_key'];cn=req['county_name'];cf=fips[cn];p=T/(sid+'.body.gz');meta=json.load(open(T/(sid+'.http.json')));assert meta['status']==200
    d=json.loads(read(p,meta,'county-selected'));q=d['ballotItemWithBreakdown'];opts=q['summaryResults']['ballotOptions'];ed=d['election'];uid=d['jurisdiction']['id']
    options_rows(d,e,cf,cn,sid,'county',uid,cn,0,opts,'/ballotItemWithBreakdown/summaryResults/ballotOptions')
    n=len(d['precincts']);v=d['voterTurnout'];ballots=ed.get('ballotsCast') if n else None;reg=ed.get('totalVoters') if n else None
    r=derive(e,cf,cn,uid,cn,sid,'/ballotItemWithBreakdown',opts,q['voteTotal'],ballots,reg,'county');r.update(underVoteCount=q.get('underVoteCount'),overVoteCount=q.get('overVoteCount'));base.append(r)
    bd=q['breakdownResults'];native=d['precincts'];vt={x['id']:x for x in v};assert len(vt)==len(v)
    clocks.append({'source_id':sid,'election_key':e,'election':ed,'jurisdiction_id':uid,'jurisdiction_shortName':d['jurisdiction'].get('shortName'),'reporting_status':q.get('reportingStatus'),'statistics':d['statistics'],'voterRegistration':d['voterRegistration'],'precincts':native,'pollingPlaces':d['pollingPlaces'],'voterTurnout':v,'underVoteCount':q.get('underVoteCount'),'overVoteCount':q.get('overVoteCount'),'rankedChoiceSummaryResults':q.get('rankedChoiceSummaryResults')})
    checks.append({'kind':'county_option_sum','source_id':sid,'pointer':'/ballotItemWithBreakdown/voteTotal','difference':sum(o['voteCount'] for o in opts)-q['voteTotal']})
    inv=dict(election_key=e,county_fips=cf,county_name=cn,source_id=sid,native_count=n,native_breakdown_count=len(bd),turnout_count=len(v),polling_place_count=len(d['pollingPlaces']),isVirtual_true=sum(x.get('isVirtual') is True for x in native),native_coverage='published_precincts' if n else 'county_only_native_unavailable',raw_ballots=ed.get('ballotsCast'),raw_registered=ed.get('totalVoters'),ballots_cast=ballots,registered_voters=reg,source_underVoteCount=q.get('underVoteCount'),source_overVoteCount=q.get('overVoteCount'));units.append(inv)
    if n:
        assert len(bd)==n==len(v);assert {x['id'] for x in native}=={x['precinct']['id'] for x in bd}==set(vt)
        checks.extend([{'kind':'native_ballots','source_id':sid,'pointer':'/voterTurnout','difference':sum(x['ballotsCast'] for x in v)-ballots},{'kind':'native_registration','source_id':sid,'pointer':'/voterTurnout','difference':sum(x['voterRegistration'] for x in v)-reg}])
    native_sums=collections.Counter();native_methods=collections.Counter();native_missing=collections.Counter();method_missing=collections.Counter()
    for i,x in enumerate(bd):
        z=x['precinct'];no=x['ballotOptions'];options_rows(d,e,cf,cn,sid,'native_precinct',z['id'],txt(z['name']),i,no,f'/ballotItemWithBreakdown/breakdownResults/{i}/ballotOptions')
        t=vt[z['id']];nr=derive(e,cf,cn,z['id'],txt(z['name']),sid,f'/ballotItemWithBreakdown/breakdownResults/{i}',no,x['voteTotal'],t['ballotsCast'],t['voterRegistration'],'native_precinct');nr.update(underVoteCount=x.get('underVoteCount'),overVoteCount=x.get('overVoteCount'));controls.append(nr)
        checks.append({'kind':'native_option_sum','source_id':sid,'pointer':nr['source_pointer'],'difference':sum(o['voteCount'] for o in no)-x['voteTotal'] if all(o['voteCount'] is not None for o in no) and x['voteTotal'] is not None else None})
        for o in no:
            key=(txt(o['name']),(o.get('party') or {}).get('abbreviation'))
            if o['voteCount'] is None:native_missing[key]+=1
            else:native_sums[key]+=o['voteCount']
            for g in o.get('groupResults') or []:
                if g['voteCount'] is None:method_missing[key+(g['groupId'],)]+=1
                else:native_methods[key+(g['groupId'],)]+=g['voteCount']
    if n:
        for o in opts:
            key=(txt(o['name']),(o.get('party') or {}).get('abbreviation'))
            checks.append({'kind':'native_candidate_sum','source_id':sid,'pointer':o['id'],'difference':native_sums[key]-o['voteCount'] if not native_missing[key] else None,'known_sum':native_sums[key],'county_control':o['voteCount'],'unallocated_residual':o['voteCount']-native_sums[key],'missing_cells':native_missing[key]})
            for g in o.get('groupResults') or []:checks.append({'kind':'native_candidate_method_sum','source_id':sid,'pointer':o['id']+'/'+g['groupId'],'difference':native_methods[key+(g['groupId'],)]-g['voteCount'] if not method_missing[key+(g['groupId'],)] else None,'known_sum':native_methods[key+(g['groupId'],)],'county_control':g['voteCount'],'unallocated_residual':g['voteCount']-native_methods[key+(g['groupId'],)],'missing_cells':method_missing[key+(g['groupId'],)]})
# Preserve state summary AND each state-published county observation separately.
state_rows=[];state_comp=[];party_disagreements=[]
for e,d in states.items():
    q=d['ballotItemWithBreakdown'];sid='state--'+e;opts=q['summaryResults']['ballotOptions']
    options_rows(d,e,'','Georgia',sid,'state',d['jurisdiction']['id'],'Georgia',0,opts,'/ballotItemWithBreakdown/summaryResults/ballotOptions')
    state_rows.append({'election_key':e,'election':d['election'],'voterRegistration':d['voterRegistration'],'voterTurnout':d['voterTurnout'],'statistics':d['statistics'],'contest':{k:v for k,v in q.items() if k!='breakdownResults'},'childLocalities':d['jurisdiction']['childLocalities']})
    aggregate=collections.Counter()
    for i,x in enumerate(q['breakdownResults']):
        cn=txt(x['locality']['name']);cf=fips[cn];co=next(r for r in base if r['election_key']==e and r['county_fips']==cf)
        options_rows(d,e,cf,cn,sid,'state_county',x['locality']['id'],cn,i,x['ballotOptions'],f'/ballotItemWithBreakdown/breakdownResults/{i}/ballotOptions')
        county_opts=[r for r in long if r['source_id']==co['source_id'] and r['unit_level']=='county' and r['group_name']=='TOTAL']
        for o in x['ballotOptions']:
            key=(o['nativeId'],txt(o['name']),(o.get('party') or {}).get('abbreviation'));aggregate[key]+=o['voteCount'];matches=[r for r in county_opts if r['candidate_name']==key[1]];assert len(matches)==1,(e,cn,key,[(r['nativeId'],r['candidate_name']) for r in county_opts])
            if matches[0]['party']!=key[2] or matches[0]['nativeId']!=key[0]: party_disagreements.append({'election_key':e,'county_name':cn,'nativeId':o['nativeId'],'name':txt(o['name']),'county_party':matches[0]['party'],'state_party':key[2],'county_nativeId':matches[0]['nativeId'],'state_nativeId':key[0]})
            checks.append({'kind':'state_county_candidate','source_id':co['source_id'],'pointer':o['id'],'difference':matches[0]['votes']-o['voteCount']})
            for g in o.get('groupResults') or []:
                rows=[r for r in long if r['source_id']==co['source_id'] and r['unit_level']=='county' and r['candidate_GUID']==matches[0]['candidate_GUID'] and r['group_GUID']==g['groupId']];assert len(rows)==1
                checks.append({'kind':'state_county_candidate_method','source_id':co['source_id'],'pointer':o['id']+'/'+g['groupId'],'difference':rows[0]['votes']-g['voteCount']})
    for o in opts:
        key=(o['nativeId'],txt(o['name']),(o.get('party') or {}).get('abbreviation'));state_comp.append({'election_key':e,'nativeId':o['nativeId'],'candidate_name':txt(o['name']),'party':key[2],'state_votes':o['voteCount'],'state_county_votes':aggregate[key],'difference':aggregate[key]-o['voteCount']})
csvout('../county-baselines.csv',base);csvout('native-baselines.csv.gz',controls);csvout('candidate-methods.csv.gz',long);csvout('native-coverage.csv',units);csvout('state-candidate-controls.csv',state_comp)
dump('source/party-disagreements.json',party_disagreements);dump('source/shared-inputs.json',refs);dump('source/source-controls.json',state_rows);(R/'source/county-controls.jsonl.gz').write_bytes(gzip.compress(('\n'.join(json.dumps(x,ensure_ascii=False) for x in clocks)+'\n').encode(),mtime=0))
dump('extraction-checks.json',{'checks':len(checks),'by_kind':dict(collections.Counter(x['kind'] for x in checks)),'nonzero_differences':[x for x in checks if x['difference'] not in [0,None]],'unverifiable_redacted_checks':sum(x['difference'] is None for x in checks),'native_residuals':[x for x in checks if 'known_sum' in x],'county_rows':len(base),'native_rows':len(controls),'candidate_method_rows':len(long),'state_candidate_controls':state_comp})
assert all(x['difference'] in [0,None] for x in checks);assert all(x['difference']==0 for x in state_comp)
print(json.dumps({'county_rows':len(base),'native_rows':len(controls),'long_rows':len(long),'checks':len(checks),'state_controls':state_comp},indent=2))
