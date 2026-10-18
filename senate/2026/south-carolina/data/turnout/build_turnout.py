"""Build the SC turnout package from complete original captures; no network.

Run with PYTHONDONTWRITEBYTECODE=1 python3 build_turnout.py. Every source row is
retained; hierarchy levels and combined/method views overlap and are never added.
"""
import collections, csv, gzip, hashlib, io, json, os
from pathlib import Path
from acquire import H, S, body, sha

LABELS=['2024-pres','2020-senate','2022-senate','2022-governor']
def dump(path,value):
    (H/path).parent.mkdir(parents=True,exist_ok=True)
    (H/path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def csvout(path,rows):
    rows=list(rows); out=io.StringIO(newline='')
    w=csv.DictWriter(out,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    raw=out.getvalue().encode();(H/path).parent.mkdir(parents=True,exist_ok=True)
    (H/path).write_bytes(gzip.compress(raw,mtime=0)if str(path).endswith('.gz')else raw)
def walk(node,pointer='/data/contestGranularData/divisions',parents=()):
    yield node,pointer,parents
    for i,c in enumerate(node.get('children')or[]):
        yield from walk(c,pointer+f'/children/{i}',parents+(node['division']['id'],))
def cellkey(r):return (r['candidateId'],r['partyId'],r['voteChannelId'])
def index(node):
    a={cellkey(r):r['votes']for r in node['granularRow']}
    assert len(a)==len(node['granularRow']);return a
def rank(rows,value):
    ordered=sorted(rows,key=lambda r:(-r[value],r['geography_key']))
    total=sum(r[value]for r in rows);cum=0;result=[]
    for i,r in enumerate(ordered,1):
        cum+=r[value];result.append(dict(rank=i,**r,cumulative_votes=cum,share_numerator=r[value],share_denominator=total,cumulative_share=cum/total))
    n=next(i for i,r in enumerate(result,1)if r['cumulative_votes']*5>=total*4)
    return result,dict(total=total,unit_count=len(rows),top15_votes=sum(r[value]for r in ordered[:15]),top15_fraction=f'{sum(r[value]for r in ordered[:15])}/{total}',top15_pct=100*sum(r[value]for r in ordered[:15])/total,
       minimum80_count=n,minimum80_votes=result[n-1]['cumulative_votes'],minimum80_pct=100*result[n-1]['cumulative_votes']/total,threshold_integer=(4*total+4)//5,
       preceding_count=n-1,preceding_votes=result[n-2]['cumulative_votes']if n>1 else 0,crossing_key=result[n-1]['geography_key'],crossing_name=result[n-1]['name'],crossing_votes=result[n-1][value],
       ordered_keys=[r['geography_key']for r in result],priority_keys=[r['geography_key']for r in result[:max(15,n)]],remainder_keys=[r['geography_key']for r in result[max(15,n):]],remainder_votes=total-result[max(15,n)-1]['cumulative_votes'])
def native_class(name):
    if name in ['Failsafe','Failsafe Provisional','Provisional']:return 'administrative named source unit; no physical polygon inferred'
    if name.lower().startswith(('absentee','early voting')):return 'method-named source reporting unit; no physical polygon inferred'
    if 'central' in name.lower():return 'source precinct with central in name; administrative/physical role unresolved'
    return 'source precinct identity; physical/current equivalence unverified'

def main():
    census=list(csv.DictReader(io.StringIO(body('census-county').decode()),delimiter='|'))
    fips={r['COUNTYNAME'].removesuffix(' County'):r['STATEFP']+r['COUNTYFP']for r in census if r['STATE']=='SC'}
    assert len(fips)==46
    fips_upper={k.upper():v for k,v in fips.items()}
    allpositions=[];native=[];universes={};controls={};countyby={};candidate_rows=[];rankingrows=[];nativeby={}
    for label in LABELS:
        d=json.loads(body(label+'-combined'))['data'];g=d['contestGranularData'];cm=d['contest']
        mg=json.loads(body(label+'-methods'))['data']['contestGranularData']
        candidates={r['candidateId']:r for r in g['candidates']}
        assert len(candidates)==len(g['candidates'])
        actual={cid for cid,r in candidates.items()if r['candidate']['pseudocandidate']in [None,'ALL_OTHER_CANDIDATES']}
        parties={int(r['id']):r['name']for r in g['parties']}
        universes[label]={'contest_metadata':cm,'candidate_metadata':g['candidates'],'method_metadata':g['voteChannels'],'party_metadata':g['parties'],'real_candidate_ids':sorted(actual),'write_in_scope':'generic ALL_OTHER_CANDIDATES separately retained; no named/valid subset supplied'if 6 in actual else'no write-in option supplied; president/vice-president excluded by SC7-13-360','combined_source_meta':f'source/{label}-combined.meta.json','method_source_meta':f'source/{label}-methods.meta.json'}
        county_names={c['division']['id']:c['division']['name']for c in g['divisions']['children']}
        assert set(county_names.values())==set(fips)
        flat=list(walk(g['divisions']));mflat=list(walk(mg['divisions']));assert len(flat)==len(mflat)
        mn={p+(n['division']['id'],):(n,ptr)for n,ptr,p in mflat}
        hierarchy=[];methodhier=[];methoddiff=[];counties=[];precincts=[];c_native=collections.defaultdict(list)
        for mode,tree in [('combined',g['divisions']),('methods',mg['divisions'])]:
            for node,ptr,parents in walk(tree):
                own=index(node)
                for i,row in enumerate(node['granularRow']):
                    raw=dict(contest_label=label,observation_scope=mode,division_path=list(parents)+( [node['division']['id']] ),division=node['division'],raw_ordinal=i,raw_value=row,source_pointer=ptr+f'/granularRow/{i}')
                    allpositions.append(raw)
                    candidate_rows.append(dict(contest_label=label,observation_scope=mode,division_path='/'.join(raw['division_path']),source_pointer=raw['source_pointer'],raw_ordinal=i,
                       division_id=node['division']['id'],division_name=node['division']['name'],division_type=node['division']['divisionTypeName'],candidate_id=row['candidateId'],party_id=row['partyId'],method_id=row['voteChannelId'],votes=row['votes'],candidate_name=candidates[row['candidateId']]['displayName'],party_name=parties.get(row['partyId']),scope='candidate'if row['candidateId']in actual else'overlapping_control',raw_row_json=json.dumps(row,separators=(',',':'))))
                if node.get('children'):
                    child=[index(c)for c in node['children']]
                    assert all(set(x)==set(own)for x in child)
                    for key,v in own.items():
                        parts=[a[key]for a in child];delta=None if v is None or None in parts else v-sum(parts)
                        if delta!=0:(hierarchy if mode=='combined'else methodhier).append(dict(division_path='/'.join(parents+(node['division']['id'],)),key=key,parent=v,children=parts if delta is None else sum(parts),difference=delta))
        for node,ptr,parents in flat:
            path=parents+(node['division']['id'],);mnode,mptr=mn[path];a=index(node);b=index(mnode)
            assert len(parents)<=2
            countyname=county_names[path[1]]if len(path)>1 else None
            cfips=fips.get(countyname);key='SC:state'if len(path)==1 else('SC:'+cfips if len(path)==2 else f'SC:{label}:{cfips}:db:{path[-1]}')
            vals={k[0]:v for k,v in a.items()};assert len(vals)==len(a)
            for k,v in a.items():
                parts=[vv for kk,vv in b.items()if kk[:2]==k[:2]]
                delta=None if not parts or v is None or None in parts else v-sum(parts)
                if delta!=0:methoddiff.append(dict(geography_key=key,county=countyname,native_name=node['division']['name'],division_path='/'.join(path),candidate_id=k[0],party_id=k[1],kind='candidate'if k[0]in actual else'overlapping_control',combined=v,method_sum=None if delta is None else sum(parts),difference=delta))
            record=dict(contest_label=label,geography_key=key,parent_key=None if len(path)==1 else('SC:state'if len(path)==2 else'SC:'+cfips),county=countyname,county_fips=cfips,native_division_id=path[-1],native_division_path='/'.join(path),name=node['division']['name'],native_type=node['division']['divisionTypeName'],raw_division=node['division'],source_pointer=ptr,
              candidate_votes=sum(vals[cid]for cid in actual),generic_write_in=vals.get(6),total_votes_control=vals.get(4),ballots_control=vals.get(1),combined_under_over=vals.get(10),blank=None,undervotes_separate=None,overvotes_separate=None,registered_voters=None,identity_status='actual county parent'if len(path)==2 else(native_class(node['division']['name'])if len(path)==3 else'state summary'),method_ids=sorted({str(k[2])for k in b}),raw_candidate_cells=[dict(candidate_id=k[0],party_id=k[1],method_id=k[2],votes=v)for k,v in a.items()])
            native.append(record)
            if len(path)==2:
                counties.append(dict(geography_key=key,name=countyname,county_fips=cfips,native_county_id=path[-1],candidate_votes=record['candidate_votes'],ballots_control=record['ballots_control'],combined_under_over=record['combined_under_over']))
            if len(path)==3:precincts.append(record);c_native[cfips].append(record)
        order,stat=rank(counties,'candidate_votes');countyby[label]={r['county_fips']:r for r in order}
        nord,nstat=rank([dict(geography_key=r['geography_key'],name=r['name'],county=r['county'],county_fips=r['county_fips'],native_id=r['native_division_id'],identity_status=r['identity_status'],candidate_votes=r['candidate_votes'])for r in precincts],'candidate_votes')
        csvout(f'extracts/{label}-native-order.csv',nord)
        for r in order:rankingrows.append(dict(contest_label=label,basis='candidate_votes',**r))
        controls[label]={'state_candidate_votes':sum(r['candidate_votes']for r in counties),'county_ranking':stat,'native_ranking':nstat,'native_precinct_count':len(precincts),'state_cells':g['divisions']['granularRow'],'combined_hierarchy_residuals':hierarchy,'method_hierarchy_residuals':methodhier,'combined_minus_method':methoddiff,'state_method_cells':mg['divisions']['granularRow']}
        assert not hierarchy
        assert sum(r['candidate_votes']for r in precincts)==stat['total']==sum(r['votes']for r in g['divisions']['granularRow']if r['candidateId']in actual)
        nativeby[label]=c_native
    csvout('extracts/candidate-method-controls.csv.gz',candidate_rows)
    csvout('extracts/native-units.csv.gz',({**r,'raw_division':json.dumps(r['raw_division'],separators=(',',':')),'method_ids':json.dumps(r['method_ids']),'raw_candidate_cells':json.dumps(r['raw_candidate_cells'],separators=(',',':'))}for r in native))
    raw=b''.join((json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n').encode()for r in allpositions)
    (H/'extracts/source-positions.jsonl.gz').write_bytes(gzip.compress(raw,mtime=0))
    regrows=[];regby={};regchecks={};vhmbynative={}
    for year in [2024,2022,2020]:
        regby[year]={};vhmbynative[year]=collections.defaultdict(list);diffs=[]
        for typ in ['VOT','REG']:
            sid=f'vhm-{year}-{typ}-county';arr=json.loads(body(sid))['voterHistoryResults']['countyPrecinctResults']
            summary=[r for r in arr if r['isSummary']==1];assert len(summary)==1
            for i,r in enumerate(arr):
                key='SC:state'if r['isSummary']else('SC:'+fips_upper[r['county']]if r['county']else f'SC:vhm:{year}:county:unassigned:row{i}')
                regrows.append(dict(source_id=sid,source_pointer=f'/voterHistoryResults/countyPrecinctResults/{i}',year=year,data_type=typ,level='state_summary'if r['isSummary']else'county'if r['county']else'unassigned_administrative',geography_key=key,county=r['county'],precinct=None,precinct_code=None,source_ordinal=i,is_summary=r['isSummary'],total_registered=r['totalRegistered'],total_participating=r['totalVoting']if typ=='VOT'else None,raw_total_voting=r['totalVoting'],source_percent_voting=r['percentVoting']))
                if typ=='VOT' and r['county'] and not r['isSummary']:regby[year][fips_upper[r['county']]]=r
            for field in ['totalRegistered','totalVoting']:
                assert sum(r[field]for r in arr if not r['isSummary'])==summary[0][field]
            if typ=='VOT':state_summary=summary[0]
        for cfips,r in regby[year].items():
            sid=f'vhm-{year}-VOT-precinct-{r["county"].lower()}';arr=json.loads(body(sid))['voterHistoryResults']['countyPrecinctResults']
            summaries=[r for r in arr if r['isSummary']];assert len(summaries)==1
            for i,p in enumerate(arr):
                key=f'SC:vhm:{year}:{cfips}:code:{p["precinctCode"]}:row:{i}'
                rec=dict(source_id=sid,source_pointer=f'/voterHistoryResults/countyPrecinctResults/{i}',year=year,data_type='VOT',level='county_summary'if p['isSummary']else'vhm_native_precinct',geography_key=key,county=r['county'],precinct=p['precinct'],precinct_code=p['precinctCode'],source_ordinal=i,is_summary=p['isSummary'],total_registered=p['totalRegistered'],total_participating=p['totalVoting'],raw_total_voting=p['totalVoting'],source_percent_voting=p['percentVoting'])
                regrows.append(rec)
                if not p['isSummary']:vhmbynative[year][cfips].append(rec)
            for field in ['totalRegistered','totalVoting']:
                total=sum(p[field]for p in arr if not p['isSummary'])
                if total!=r[field]or summaries[0][field]!=r[field]:diffs.append(dict(county=r['county'],field=field,county_value=r[field],precinct_sum=total,precinct_summary=summaries[0][field]))
        regchecks[str(year)]={'state_summary':{k:state_summary[k]for k in ['totalRegistered','totalVoting','percentVoting']},'named_counties':len(regby[year]),'native_precinct_rows':sum(map(len,vhmbynative[year].values())),'precinct_rollup_disagreements':diffs,'unassigned_rows':[r for r in regrows if r['year']==year and r['level']=='unassigned_administrative'],'scope':'printed election lists: all active and some inactive; VHM marks/returns, not BCM ballots'}
    csvout('extracts/registration-participation.csv.gz',regrows)
    dump('registration-reconciliation.json',regchecks)
    dump('candidate-universe.json',universes);dump('controls.json',controls)
    primary=controls['2024-pres']['county_ranking'];base=countyby['2024-pres'];wide=[]
    for cfips,r in sorted(base.items(),key=lambda x:x[1]['rank']):
        out=dict(county=r['name'],county_fips=cfips,geography_key=r['geography_key'],native_county_id=r['native_county_id'],rank_2024_pres=r['rank'],votes_2024_pres=r['candidate_votes'],cumulative_2024_pres=r['cumulative_votes'],share_2024_pres=r['candidate_votes']/primary['total'],priority=r['geography_key']in primary['priority_keys'])
        for label in LABELS:
            n=next(n for n in native if n['contest_label']==label and n['county_fips']==cfips and n['native_type']=='County')
            for field in ['candidate_votes','generic_write_in','ballots_control','combined_under_over','blank','undervotes_separate','overvotes_separate']:
                out[label.replace('-','_')+'_'+field]=n[field]
            for cell in n['raw_candidate_cells']:
                out[label.replace('-','_')+f'_c{cell["candidate_id"]}_p{cell["party_id"]}']=cell['votes']
        for year in [2024,2022,2020]:
            for field in ['totalRegistered','totalVoting','percentVoting']:out[f'vhm_{year}_{field}']=regby[year][cfips][field]
        wide.append(out)
    csvout('../county-turnout.csv',wide)
    sensitivity=[]
    for label in LABELS:
        rows=list(countyby[label].values())
        ordered,stat=rank([dict(geography_key=r['geography_key'],name=r['name'],value=r['ballots_control'])for r in rows],'value');sensitivity.append(dict(contest=label,basis='history_combined_ballots_control',**stat))
        for row in ordered:rankingrows.append(dict(contest_label=label,basis='combined_ballots_control',rank=row['rank'],geography_key=row['geography_key'],name=row['name'],county_fips=row['geography_key'].split(':')[-1],native_county_id=base[row['geography_key'].split(':')[-1]]['native_county_id'],candidate_votes=row['value'],ballots_control=row['value'],combined_under_over=None,cumulative_votes=row['cumulative_votes'],share_numerator=row['share_numerator'],share_denominator=row['share_denominator'],cumulative_share=row['cumulative_share']))
    for year in [2024,2022,2020]:
        for field in ['totalRegistered','totalVoting']:
            rows=[dict(geography_key='SC:'+f,name=r['county'],value=r[field])for f,r in regby[year].items()]
            unknown=[r for r in regrows if r['year']==year and r['level']=='unassigned_administrative'and r['data_type']=='VOT']
            rows += [dict(geography_key=r['geography_key'],name='Unassigned source county row',value=r['total_registered'if field=='totalRegistered'else'total_participating'])for r in unknown]
            _,stat=rank(rows,'value');sensitivity.append(dict(contest=f'vhm-{year}',basis=field,**stat))
    csvout('extracts/county-rankings.csv',rankingrows);dump('sensitivity.json',sensitivity)
    county_contract=[]
    for r in sorted(base.values(),key=lambda x:x['rank']):
        f=r['county_fips']; constituents={}
        for label in LABELS:
            constituents[label]=[dict(geography_key=n['geography_key'],native_id=n['native_division_id'],native_path=n['native_division_path'],native_name=n['name'],native_type=n['native_type'],raw_division=n['raw_division'],identity_status=n['identity_status'],candidate_votes=n['candidate_votes'],source_pointer=n['source_pointer'],combined_source_ref=label+'-combined',method_source_ref=label+'-methods',method_source_pointer=n['source_pointer'],method_ids=n['method_ids'])for n in nativeby[label][f]]
        vhm={str(y):[dict(geography_key=n['geography_key'],precinct_code=n['precinct_code'],native_name=n['precinct'],raw_identity=dict(county=None,precinct=n['precinct'],precinctCode=n['precinct_code'],isSummary=n['is_summary']),total_registered=n['total_registered'],total_participating=n['total_participating'],source_id=n['source_id'],source_pointer=n['source_pointer'],complete_raw_row_reference='source_observations[source_id] original body at source_pointer; all original fields retained')for n in vhmbynative[y][f]]for y in [2024,2022,2020]}
        county_contract.append(dict(**r,in_priority=r['geography_key']in primary['priority_keys'],historical_constituents=constituents,voter_history_constituents=vhm,current_2026_constituents={'status':'unavailable_unverified','units':[]},physical_crosswalk_status='unavailable: database IDs, VHM codes and names do not establish geometry or cross-year/2026 equivalence'))
    observations={}
    sourceids=[label+'-'+mode for label in LABELS for mode in ['combined','methods']]+[p.stem.removesuffix('.meta')for p in sorted(S.glob('vhm-*.meta.json'))]
    for sid in sourceids:
        m=json.loads((S/(sid+'.meta.json')).read_text());observations[sid]=dict(source_id=sid,metadata_path='source/'+sid+'.meta.json',body_path=os.path.relpath((S/m['body_path']).resolve(),H),stored_encoding=m.get('stored_encoding','gzip'),original_sha256=m['original_sha256'],original_bytes=m['original_bytes'],stored_sha256=m['stored_sha256'],stored_bytes=m['stored_bytes'],requested_url=m['requested_url'],final_url=m['final_url'],retrieved_utc=m['retrieved_utc'],http_status=m['http_status'])
    for r in regchecks['2024']['unassigned_rows']:
        r['raw_identity']=dict(county=None,precinct=None,precinctCode=None,isSummary=0)
        r['complete_raw_row_reference']='source_observations[source_id] original body at source_pointer; all original fields retained'
    dump('priority-set.json',dict(schema_version='sc-turnout-1',state='SC',contest='2024-11-05 President of the United States',contest_id='7131',denominator='reported votes for all seven named presidential slates; no extra total/ballot/under-over rows',candidate_ids=universes['2024-pres']['real_candidate_ids'],acceptance_status='independent turnout calculation; peer agreement and coordinator acceptance recorded separately',coordinator_acceptance_path='data/coordinator-priority-acceptance.json',source_observations=observations,source_state_divisions={label:json.loads(body(label+'-combined'))['data']['contestGranularData']['divisions']['division']for label in LABELS},**primary,all_county_order=primary['ordered_keys'],ordered_priority_keys=primary['priority_keys'],counties=county_contract,native_priority_order_path='extracts/2024-pres-native-order.csv',native_priority_summary=controls['2024-pres']['native_ranking'],source_disjointness='46 counties partition the state; native precincts partition each county within each contest; method views and parents overlap; VHM is a separate source universe',unavailable_cases=['No approved current2026 boundaries or native crosswalk','Separate blank, undervote and overvote fields unavailable: combined control only','2020 source candidate method allocation gaps retained in controls.json','2024 VHM unnamed county row cannot be drilled down through observed nonempty county route'],vhm_administrative_rows=regchecks['2024']['unassigned_rows']))
    dump('build-summary.json',dict(source_positions=len(allpositions),native_hierarchy_rows=len(native),candidate_method_control_rows=len(candidate_rows),registration_rows=len(regrows),contests={k:{'state_votes':v['state_candidate_votes'],'native_precinct_count':v['native_precinct_count'],'method_residuals':len(v['combined_minus_method']),'candidate_method_residuals':sum(r['kind']=='candidate'for r in v['combined_minus_method']),'combined_hierarchy_residuals':len(v['combined_hierarchy_residuals'])}for k,v in controls.items()},priority=primary))
    print(json.dumps(json.loads((H/'build-summary.json').read_text()),indent=2))
if __name__=='__main__':main()
