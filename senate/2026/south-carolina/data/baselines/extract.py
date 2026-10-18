"""Offline independent extraction, all original positions and scopes preserved."""
from pathlib import Path
import csv, gzip, hashlib, io, json, collections, os, urllib.parse
BASE=Path(__file__).resolve().parent; SRC=BASE/'source'; DATA=BASE.parent
LABELS=['2024-pres','2020-senate','2022-senate','2022-governor']
PAIRS={'2024-pres':(7553,27),'2020-senate':(3255,3254),'2022-senate':(870,3536),'2022-governor':(3473,3471)}
def dump(p,x): p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def compact(x): return json.dumps(x,ensure_ascii=False,separators=(',',':'))
def sha(b):return hashlib.sha256(b).hexdigest()
def loadbody(meta_path):
    m=json.loads(meta_path.read_text());p=meta_path.parent/m['body_path'];stored=p.read_bytes()
    assert sha(stored)==m['stored_sha256'] and len(stored)==m['stored_bytes']<40000000
    raw=gzip.decompress(stored) if p.suffix=='.gz' else stored
    assert sha(raw)==m['original_sha256'] and len(raw)==m['original_bytes']
    if 'request_file' in m:assert sha((meta_path.parent/m['request_file']).read_bytes())==m['request_sha256']
    return raw,m
def rows(path,items):
    items=list(items);assert items
    out=io.StringIO(newline='');w=csv.DictWriter(out,fieldnames=list(items[0]));w.writeheader();w.writerows(items)
    raw=out.getvalue().encode();path.write_bytes(gzip.compress(raw,mtime=0) if path.suffix=='.gz' else raw)
def walk(node,path=(),ptr='/data/contestGranularData/divisions',county=None):
    path=path+(node['division']['id'],)
    if node['division']['divisionTypeName']=='County':county=node['division']['name']
    yield node,path,ptr,county
    for i,ch in enumerate(node.get('children') or []):yield from walk(ch,path,ptr+f'/children/{i}',county)
def cellmap(node):
    d={}
    for r in node['granularRow']:
        k=(r['candidateId'],r['partyId'],r['voteChannelId']);assert k not in d,k;d[k]=r['votes']
    return d
def priority(items,total):
    items=sorted(items,key=lambda r:(-r['votes'],r['key']))
    cumulative=0;order=[]
    for i,r in enumerate(items,1):
        cumulative+=r['votes'];order.append(dict(rank=i,**r,cumulative=cumulative))
    n=next(i+1 for i,r in enumerate(order) if 5*r['cumulative']>=4*total)
    return dict(total=total,unit_count=len(items),top15_votes=sum(r['votes'] for r in order[:15]),threshold_integer=(4*total+4)//5,
                minimum80_count=n,minimum80_votes=order[n-1]['cumulative'],preceding_votes=order[n-2]['cumulative'] if n>1 else 0,
                crossing_key=order[n-1]['key'],crossing_name=order[n-1]['name'],crossing_votes=order[n-1]['votes'],
                ordered_keys=[r['key'] for r in order],order=order)

def main():
    code=loadbody(SRC/'county-fips.meta.json')[0].decode()
    fips={r['COUNTYNAME'].removesuffix(' County'):r['STATEFP']+r['COUNTYFP'] for r in csv.DictReader(io.StringIO(code),delimiter='|') if r['STATE']=='SC'}
    assert len(fips)==46
    dump(SRC/'county-fips-crosswalk.json',dict(source='county-fips.meta.json',scope='county names only; no native ID/geometry crosswalk',counties=fips))
    allrows=[];native=[];methodbase=[];universe={};checks={};rankings={};observations={};countywide={n:dict(county=n,county_fips=f,geography_key='SC:'+f) for n,f in fips.items()}
    for lab in LABELS:
        for mode in ['combined','methods']:
            mp=SRC/(lab+'-'+mode+'.meta.json');m=json.loads(mp.read_text())
            observations[lab+'-'+mode]=dict(source_id=lab+'-'+mode,meta_path=os.path.relpath(mp,DATA),body_path=os.path.relpath(SRC/m['body_path'],DATA),original_sha256=m['original_sha256'],original_bytes=m['original_bytes'],retrieved_utc=m['retrieved_utc'],requested_url=m['requested_url'],final_url=m['final_url'])
        j=json.loads(loadbody(SRC/(lab+'-combined.meta.json'))[0])['data'];g=j['contestGranularData']
        mj=json.loads(loadbody(SRC/(lab+'-methods.meta.json'))[0])['data'];mg=mj['contestGranularData']
        assert not j.get('errors') and not mj.get('errors')
        # Metadata lists are retained in full, including repeated method candidate keys.
        universe[lab]={'contest':j['contest'],'combined_metadata':{k:v for k,v in g.items() if k!='divisions'},
                       'methods_contest':mj['contest'],'methods_metadata':{k:v for k,v in mg.items() if k!='divisions'}}
        cands={c['candidateId']:c for c in g['candidates']};assert len(cands)==len(g['candidates'])
        parties={int(p['id']):p['name'] for p in g['parties']};real={k for k,c in cands.items() if c['candidate']['pseudocandidate'] in [None,'ALL_OTHER_CANDIDATES']}
        a_id,b_id=PAIRS[lab]
        cn={path:(node,ptr,c) for node,path,ptr,c in walk(g['divisions'])};mn={path:(node,ptr,c) for node,path,ptr,c in walk(mg['divisions'])}
        assert cn.keys()==mn.keys()
        rollups=[];method_rollups=[];viewdiff=[];metadata_diff=[]
        for mode,tree in [('combined',g['divisions']),('methods',mg['divisions'])]:
            for node,path,ptr,c in walk(tree):
                d=node['division'];own=cellmap(node)
                for ordinal,r in enumerate(node['granularRow']):
                    cc=cands[r['candidateId']];pseudo=cc['candidate']['pseudocandidate']
                    scope='candidate' if pseudo is None else ('generic_write_in' if pseudo=='ALL_OTHER_CANDIDATES' else 'control:'+pseudo)
                    allrows.append(dict(contest_label=lab,observation_scope=mode,division_path='/'.join(path),source_pointer=ptr+f'/granularRow/{ordinal}',
                        raw_ordinal=ordinal,division_id=d['id'],division_name=d['name'],division_type=d['divisionTypeName'],candidate_id=r['candidateId'],
                        party_id=r['partyId'],method_id=r['voteChannelId'],votes=r['votes'],candidate_name=cc['displayName'],party_name=parties.get(r['partyId'],''),scope=scope,raw_row_json=compact(r)))
                if node.get('children'):
                    children=[cellmap(x) for x in node['children']]
                    for k,v in own.items():
                        vs=[x.get(k) for x in children];sv=sum(vs) if all(x is not None for x in vs) else None
                        if sv!=v:(rollups if mode=='combined' else method_rollups).append(dict(path='/'.join(path),key=k,parent=v,children=sv,difference=v-sv if sv is not None else None))
        state=cellmap(g['divisions']);state_total=sum(v for (c,p,m),v in state.items() if c in real);pair_total=sum(v for (c,p,m),v in state.items() if c in [a_id,b_id])
        for c in g['candidates']:
            v=state.get((c['candidateId'],c['partyId'],0))
            if c['nVotes']!=v:metadata_diff.append(dict(candidate=c['candidateId'],metadata=c['nVotes'],granular=v))
        state_named=sum(v for (c,p,m),v in state.items() if c in real and cands[c]['candidate']['pseudocandidate'] is None)
        for path,(node,ptr,c) in cn.items():
            d=node['division'];typ=d['divisionTypeName'];own=cellmap(node);met=cellmap(mn[path][0])
            def val(cid):
                vs=[v for (k,p,m),v in own.items() if k==cid];return sum(vs) if vs and all(v is not None for v in vs) else None
            A=val(a_id);B=val(b_id);total=sum(v for (cid,p,m),v in own.items() if cid in real)
            key='SC:state' if typ=='State' else ('SC:'+fips[c] if typ=='County' else 'SC:'+lab+':'+fips[c]+':db:'+d['id'])
            parent='' if typ=='State' else ('SC:state' if typ=='County' else 'SC:'+fips[c])
            channels=sorted({str(k[2]) for k in met})
            n=dict(contest_label=lab,geography_key=key,parent_key=parent,county=c or '',county_fips=fips.get(c,''),native_division_id=d['id'],native_division_path='/'.join(path),name=d['name'],native_type=typ,source_pointer=ptr,
                candidate_votes=total,generic_write_in=val(6),total_votes_control=val(4),ballots_control=val(1),combined_under_over=val(10),blank=None,undervotes_separate=None,overvotes_separate=None,registered_voters=None,
                identity_status='state summary' if typ=='State' else ('county name to Census FIPS; no finer crosswalk' if typ=='County' else 'historical database precinct; no cross-year/current boundary equivalence'),
                raw_division=compact(d),source_observation_refs=compact([lab+'-combined',lab+'-methods']),
                method_ids=compact(channels),raw_candidate_cells=compact([dict(candidate_id=r['candidateId'],party_id=r['partyId'],method_id=r['voteChannelId'],votes=r['votes']) for r in node['granularRow']]),
                A_name=cands[a_id]['displayName'],B_name=cands[b_id]['displayName'],A=A,B=B,other=total-A-B,pair_votes=A+B,pair_participation=(A+B)/total if total else None,
                A_pair_share=A/(A+B) if A+B else None,A_all_share=A/total if total else None,net_A_minus_B=A-B,pair_margin_pp=100*(A-B)/(A+B) if A+B else None,
                all_margin_pp=100*(A-B)/total if total else None,contest_weight=total/state_total,pair_weight=(A+B)/pair_total,share_pp1_net_gain=.02*(A+B))
            native.append(n)
            for (cid,p,m),v in own.items():
                vs=[vv for (cc,pp,mm),vv in met.items() if cc==cid and pp==p];mv=sum(vs) if vs and all(x is not None for x in vs) else None
                if v!=mv:viewdiff.append(dict(path='/'.join(path),county=c,candidate_id=cid,party_id=p,scope='candidate' if cid in real else 'control',combined=v,methods=mv,difference=v-mv if mv is not None else None))
            for ch in channels:
                cr=[r for r in mn[path][0]['granularRow'] if str(r['voteChannelId'])==ch]
                def cv(cid):
                    vv=[r['votes'] for r in cr if r['candidateId']==cid];return sum(vv) if vv and all(v is not None for v in vv) else None
                ma,mb=cv(a_id),cv(b_id);mt=sum(r['votes'] for r in cr if r['candidateId'] in real)
                methodbase.append(dict(contest_label=lab,geography_key=key,division_path='/'.join(path),county=c or '',county_fips=fips.get(c,''),native_type=typ,method_id=ch,
                    method_name=next(x['name'] for x in mg['voteChannels'] if x['id']==ch),A=ma,B=mb,other=mt-ma-mb if ma is not None and mb is not None else None,candidate_votes=mt,
                    pair_votes=ma+mb if ma is not None and mb is not None else None,combined_pair_weight=(ma+mb)/pair_total if ma is not None and mb is not None else None,
                    A_pair_share=ma/(ma+mb) if ma is not None and mb is not None and ma+mb else None,share_pp1_net_gain=.02*(ma+mb) if ma is not None and mb is not None else None,
                    ballots_control=cv(1),under_over_control=cv(10),method_scope_status='2020 incomplete allocation; never substitute for combined totals' if lab=='2020-senate' else 'candidate allocations reconcile; method ballot controls remain source-scoped'))
            if typ=='County':
                w=countywide[c];prefix=lab.replace('-','_');w['native_county_id']=d['id']
                w.update({prefix+'_'+k:n[k] for k in ['candidate_votes','generic_write_in','ballots_control','combined_under_over','blank','undervotes_separate','overvotes_separate','A','B','other','pair_votes','pair_participation','A_pair_share','A_all_share','net_A_minus_B','pair_margin_pp','all_margin_pp','contest_weight','pair_weight','share_pp1_net_gain']})
                w.update({f'{prefix}_c{cid}_p{p}':v for (cid,p,m),v in own.items()})
        nr=[r for r in native if r['contest_label']==lab]
        rankitems=lambda typ:[dict(key=r['geography_key'],name=r['name'],county=r['county'],votes=r['candidate_votes'],raw_division=json.loads(r['raw_division']),source_pointer=r['source_pointer'],source_observation_refs=json.loads(r['source_observation_refs'])) for r in nr if r['native_type']==typ]
        rankings[lab]={'county':priority(rankitems('County'),state_total),'native':priority(rankitems('Precinct'),state_total)}
        checks[lab]=dict(counties=len(rankitems('County')),native=len(rankitems('Precinct')),total=state_total,named=state_named,pair=pair_total,other=state_total-pair_total,
                         A=sum(v for (cid,p,m),v in state.items() if cid==a_id),B=sum(v for (cid,p,m),v in state.items() if cid==b_id),
                         combined_rollup_residuals=rollups,method_rollup_residuals=method_rollups,combined_minus_methods=viewdiff,metadata_minus_granular=metadata_diff)
        assert not rollups and len(rankitems('County'))==46
    reg=[];vhmchecks=[];refs=[]
    for mp in sorted((DATA/'turnout/source').glob('vhm-*.meta.json')):
        raw,m=loadbody(mp);j=json.loads(raw);sid=m['id'];parts=sid.split('-');year=parts[1];dtype=parts[2];level=parts[3];name='-'.join(parts[4:])
        original=j['voterHistoryResults']['countyPrecinctResults'];rr=[]
        for i,r in enumerate(original):
            county=r['county'] or (urllib.parse.parse_qs(urllib.parse.urlparse(m['requested_url']).query)['county'][0] if level=='precinct' else '')
            lev='summary' if r['isSummary'] else ('unassigned_administrative' if level=='county' and not county else level)
            geo=('SC:vhm:'+year+':county:unassigned:row'+str(i)) if lev=='unassigned_administrative' else ('SC:vhm:'+year+':'+level+':'+(county or 'state')+':'+str(r['precinctCode'] or i))
            n=dict(source_id=sid,source_pointer=f'/voterHistoryResults/countyPrecinctResults/{i}',year=year,data_type=dtype,level=lev,geography_key=geo,county=county,precinct=r['precinct'],precinct_code=r['precinctCode'],source_ordinal=i,is_summary=r['isSummary'],total_registered=r['totalRegistered'],total_participating=r['totalVoting'] if dtype=='VOT' else None,raw_total_voting=r['totalVoting'],source_percent_voting=r['percentVoting'],raw_identity_json=compact({k:r[k]for k in ['county','precinct','precinctCode','isSummary']}))
            reg.append(n);rr.append(n)
            if level=='county' and county and not r['isSummary'] and dtype=='VOT':
                cn=next(c for c in fips if c.upper()==county.upper());countywide[cn].update({f'vhm_{year}_totalRegistered':r['totalRegistered'],f'vhm_{year}_totalVoting':r['totalVoting'],f'vhm_{year}_percentVoting':r['percentVoting']})
        sums=[r for r in rr if r['is_summary']];detail=[r for r in rr if not r['is_summary']]
        vhmchecks.append(dict(source_id=sid,row_count=len(rr),detail_count=len(detail),summary_count=len(sums),
                              registered_detail=sum(r['total_registered'] for r in detail),participating_detail=sum(r['raw_total_voting'] for r in detail),
                              summary=[dict(registered=r['total_registered'],participating=r['raw_total_voting']) for r in sums]))
        refs.append(dict(meta_path=os.path.relpath(mp,BASE),meta_sha256=sha(mp.read_bytes()),body_path=os.path.relpath(mp.parent/m['body_path'],BASE),original_sha256=m['original_sha256'],stored_sha256=m['stored_sha256'],stored_bytes=m['stored_bytes'],original_bytes=m['original_bytes'],reuse='original public primary source reused read-only; independently parsed, not independently reacquired here'))
    rank=rankings['2024-pres']['county'];ordered=[]
    for r in rank['order']:
        w=countywide[r['name']];w.update(rank_2024_pres=r['rank'],votes_2024_pres=r['votes'],cumulative_2024_pres=r['cumulative'],share_2024_pres=r['votes']/rank['total'],priority=r['rank']<=max(15,rank['minimum80_count']));ordered.append(w)
    # Consistent field order despite source dictionary order; no fabricated missing counts.
    fields=list(ordered[0]);assert all(set(r)==set(fields) for r in ordered)
    rows(DATA/'county-baselines.csv',({k:r[k] for k in fields} for r in ordered))
    rows(BASE/'candidate-method-controls.csv.gz',allrows);rows(BASE/'native-units.csv.gz',native);rows(BASE/'method-baselines.csv.gz',methodbase);rows(BASE/'registration-participation.csv.gz',reg)
    dump(BASE/'candidate-universe.json',universe);dump(BASE/'controls.json',checks);dump(BASE/'vhm-controls.json',vhmchecks);dump(BASE/'shared-primary-references.json',refs)
    dump(BASE/'priority-set.json',dict(schema_version='sc-partisanship-1',denominator='all seven named presidential slates; overlapping controls excluded',acceptance='independently calculated; coordinator acceptance required',coordinator_acceptance_path='data/coordinator-priority-acceptance.json',**rank,comparisons=rankings,source_observations=observations))
    print(compact(dict(positions=len(allrows),native_hierarchy=len(native),method_units=len(methodbase),registration_positions=len(reg),county_rows=len(ordered),total=rank['total'],min80=rank['minimum80_count'],crossing=rank['crossing_name'])))
if __name__=='__main__':main()
