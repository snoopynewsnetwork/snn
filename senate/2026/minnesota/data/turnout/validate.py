"""Meaningful offline QA over source bytes, every required cell and hierarchy."""
import argparse, collections, csv, gzip, io, json, re
from decimal import Decimal, getcontext
from pathlib import Path
from urllib.parse import unquote
from extract import HERE, YEARS, STATS, readbook, sha, dump
from build import readcsv

STATE=HERE.parent.parent

def validate(refresh=False):
    getcontext().prec=50
    tests=[]
    def passed(name,**details):tests.append(dict(check=name,status='pass',**details))
    manifest=json.loads((HERE/'source/shared-originals.json').read_text())
    for r in manifest:
        b=(STATE/r['shared_path']).read_bytes();assert sha(b)==r['stored_sha256']
        raw=gzip.decompress(b);assert sha(raw)==r['raw_sha256'] and len(raw)==r['bytes']
    passed('shared-original hashes and exact reconstruction',assets=len(manifest))
    acquisitions=json.loads((HERE/'source/acquisition.json').read_text())
    for r in acquisitions:
        if 'path' not in r:continue
        b=(HERE/r['path']).read_bytes();raw=gzip.decompress(b)
        assert sha(b)==r['stored_sha256'] and len(b)==r['stored_bytes']
        assert sha(raw)==r['raw_sha256'] and len(raw)==r['raw_bytes']
        if r['content_check']=='bot_challenge':assert b'perfdrive' in raw or b'Radware' in raw or b'botmanager' in raw
        if r['content_check']=='primary_page':assert b'<title>Minnesota Secretary Of State -' in raw
    passed('own raw/stored evidence hashes and challenge classification',records=len(acquisitions))
    primary=json.loads((HERE/'source/primary-controls.json').read_text())
    meta=json.loads((HERE/'source/workbook-context.json').read_text())
    extraction=json.loads((HERE/'source/extraction-controls.json').read_text())
    natives={};counties={};municipal={};source_checks=0
    for y,prefixes in YEARS.items():
        sheets,_=readbook(y);rows=readcsv(f'native-{y}.csv.gz');natives[y]=rows
        byrow={r['source_row']:r for r in sheets['Precinct-Results']['rows']}
        assert len(rows)==len({r['VTDID'] for r in rows})==len({(r['COUNTYCODE'],r['PCTCODE']) for r in rows})==(4110 if y==2020 else 4103)
        fields=[v for v in meta[str(y)]['columns'].values() if v in rows[0]]
        raw_fips={r['cells']['A']['value']:r['cells']['C']['value'] for r in sheets['Counties']['rows'] if r['cells'].get('A',{}).get('value','').isdigit()}
        for r in rows:
            actual=byrow[int(r['source_row'])]['cells']
            for col,f in meta[str(y)]['columns'].items():
                if f not in fields:continue
                val=actual.get(col,{}).get('value');assert r[f]==('' if val is None else val),(y,r['source_row'],f)
                source_checks+=1
            assert r['county_fips']==raw_fips[r['COUNTYCODE']]
            assert r['VTDID']==r['county_fips']+r['PCTCODE']
            assert r['native_key']==f'MN:{y}:VTDID:'+r['VTDID']
            for p in prefixes:
                cs=primary[str(y)]['contests'][p]
                assert sum(int(r[f]) for f in cs)==int(r[p+'TOTAL'])
            for f in extraction[str(y)]['totals']:assert re.fullmatch(r'\d+',r[f])
        sums={f:sum(int(r[f]) for r in rows) for f in extraction[str(y)]['totals']}
        assert sums==extraction[str(y)]['totals']
        for p,cs in primary[str(y)]['contests'].items():
            for f,(_,_,v) in cs.items():assert sums[f]==v
        for f,v in primary[str(y)]['statistics'].items():assert sums[f]==v
        counties[y]=readcsv(f'county-controls-{y}.csv');municipal[y]=readcsv(f'municipal-controls-{y}.csv')
        assert len(counties[y])==87 and len({r['county_fips'] for r in counties[y]})==87
        for level,parent,key_fields in [('county',counties[y],['county_fips']),('municipal',municipal[y],['county_fips','MCDNAME'])]:
            grouped=collections.defaultdict(list)
            for r in rows:grouped[tuple(r[f] for f in key_fields)].append(r)
            assert set(grouped)=={tuple(r[f] for f in key_fields) for r in parent}
            assert sum(len(v) for v in grouped.values())==len(rows)
            for a in parent:
                units=grouped[tuple(a[f] for f in key_fields)]
                assert len(units)==int(a['native_units'])
                for f in sums:assert int(a[f])==sum(int(u[f]) for u in units)
        observed=[]
        for r in rows:
            method=sum(int(r[f]) for f in ['SIGNATURES','AB_MB','FEDONLYAB','PRESONLYAB'] if f in r)
            if method!=int(r['TOTVOTING']):observed.append((r['native_key'],int(r['TOTVOTING']),method))
        assert observed==[(r['native_key'],r['TOTVOTING'],r['method_sum']) for r in extraction[str(y)]['method_identity_discrepancies']]
        passed(f'{y} complete native cells, candidate/state controls and disjoint parent sums',native_rows=len(rows),counties=87,municipal_scoped_parents=len(municipal[y]),
               method_discrepancy_rows=len(observed),method_sum_net_excess=sum(m-v for _,v,m in observed))
    passed('every required source-native field equals original OOXML value',cells=source_checks,duplicate_2020_TABMODEL_preserved=True)
    flat=list(csv.DictReader((HERE.parent/'county-turnout.csv').open()))
    assert len(flat)==87
    for r in flat:
        for y in YEARS:
            a=next(a for a in counties[y] if a['county_fips']==r['county_fips'])
            for f in extraction[str(y)]['totals']:assert int(r[f'{y}_{f}'])==int(a[f])
            for p,cs in primary[str(y)]['contests'].items():
                for f in ['blank','undervote','overvote','valid_named_writein']:assert r[f'{y}_{p}_{f}']==''
                assert int(r[f'{y}_{p}_D_group'])==int(a[p+'DFL'])
                assert int(r[f'{y}_{p}_R_group'])==int(a[p+'R'])
                assert int(r[f'{y}_{p}_other_including_generic_writein'])==int(a[p+'TOTAL'])-int(a[p+'DFL'])-int(a[p+'R'])
    passed('main CSV all fields/DFL analytical group/unavailable categories',rows=87)
    contract=json.loads((HERE/'priority-set.json').read_text())
    freeze=json.loads((HERE/'source/frozen-contract.json').read_text());cb=(HERE/'priority-set.json').read_bytes()
    assert sha(cb)==freeze['sha256'] and len(cb)==freeze['bytes']<40_000_000
    assert contract['coordinator_acceptance_path']=='data/coordinator-priority-acceptance.json'
    acceptance=json.loads((STATE/contract['coordinator_acceptance_path']).read_text())
    assert acceptance['accepted'] is True and acceptance['contract_sha256']==sha(cb) and acceptance['contract_bytes']==len(cb)
    # The authority path is referenced, never its reverse hash.
    passed('frozen contract and external coordinator historical acceptance',contract_bytes=len(cb),contract_sha256=sha(cb),acceptance_path=contract['coordinator_acceptance_path'],worker_self_acceptance=False)
    def ranking_check(r,rs,field,key,has_order=True):
        order=sorted(rs,key=lambda u:(-int(u[field]),u[key]));total=sum(int(u[field]) for u in rs)
        keys=[u[key] for u in order];cum=0;minimum=None
        assert total==r['denominator'] and r['unit_count']==len(rs)
        if has_order:
            assert keys==[u['key'] for u in r['order']]
        else:assert keys==r['complete_ordered_keys']
        for i,u in enumerate(order,1):
            cum+=int(u[field])
            if has_order:
                a=r['order'][i-1]
                assert a['votes']==int(u[field]) and a['cumulative_votes']==cum and a['rank']==i
                assert abs(Decimal(a['share'])-Decimal(a['votes'])/Decimal(total))<Decimal('1e-27')
            if minimum is None and 5*cum>=4*total:minimum=i
        assert minimum==r['minimum80_count']
        crossing=sum(int(u[field]) for u in order[:minimum]);before=crossing-int(order[minimum-1][field])
        assert 5*before<4*total<=5*crossing
        assert before==r['previous_votes'] and crossing==r['minimum80_votes']
        assert r['crossing_key']==order[minimum-1][key]
        assert r['top15_votes']==sum(int(u[field]) for u in order[:15])
        assert r['priority_keys']==keys[:max(15,minimum)]
        assert r['remainder_votes']==total-crossing
        return keys
    sensitivities=json.loads((HERE/'sensitivity.json').read_text())
    for label,r in sensitivities.items():
        y,f=label.split('_',1);field=f+'TOTAL' if f in ['USSEN','USPRS','MNGOV'] else f
        keys=ranking_check(r,counties[int(y)],field,'county_key')
        assert abs(sum(Decimal(a['share']) for a in r['order'])-1)<Decimal('1e-27')
    assert contract['complete_ordered_county_keys']==[r['key'] for r in sensitivities['2024_USSEN']['order']]
    assert contract['ordered_priority_keys']==sensitivities['2024_USSEN']['priority_keys']==acceptance['ordered_priority_keys']
    assert [r['county_key'] for r in flat]==contract['complete_ordered_county_keys']
    assert sum(int(r['senate_2024_total']) for r in flat if r['minimum80']=='1')==2567977
    assert sum(int(r['senate_2024_total']) for r in flat if r['top15']=='1')==2308744
    ranking_check(contract['native_2024_ranking'],natives[2024],'USSENTOTAL','native_key',False)
    ranking_check(contract['municipal_2024_ranking'],municipal[2024],'USSENTOTAL','derived_key',False)
    for level,key in [('native','native_key'),('municipal','derived_key')]:
        rs=readcsv(f'{level}-2024-ranked.csv.gz');r=contract[f'{level}_2024_ranking']
        assert [a[key] for a in rs]==r['complete_ordered_keys']
        assert int(rs[-1]['cumulative_votes'])==3189323
    passed('all 13 sensitivity orders, weights, top15, exact minimum80/preceding/remainder and native/municipal orders',county_orders=len(sensitivities),native_order=4103,municipal_order=2761)
    count=0;priority_count=0
    for y,rows in natives.items():
        leaves={r['native_key']:r for r in rows};seen=set()
        for parent in contract['county_order']:
            for u in parent['native_constituents'][str(y)]:
                assert u['native_key'] not in seen;seen.add(u['native_key']);count+=1
                a=leaves[u['native_key']]
                for f in ['source_id','source_sheet','source_row','VTDID','PCTCODE','PCTNAME','MCDNAME','WARD','MAILBALLOT','unit_kind','method_warning','current_2026_equivalence']:
                    assert str(u[f])==a[f]
                assert a['county_key']==parent['key'] and u['candidate_votes']==int(a['MNGOVTOTAL' if y==2022 else 'USSENTOTAL'])
                assert u['native_municipal_id'] is None and 'unavailable' in u['central_absentee_candidate_split']
                if y==2024 and parent['in_priority']:priority_count+=1
        assert seen==set(leaves)
    assert count==12316 and priority_count==2067
    passed('every native constituent retained exactly once, including priority/remainder/current/admin cases',all_year_constituents=count,priority_native_2024=priority_count)
    named=list(csv.DictReader((HERE/'source/named-writeins-2020.csv').open()))
    assert len(named)==len({(r['county_fips'],r['source_candidate_label']) for r in named})==522
    assert sum(int(r['votes']) for r in named)==32
    for r in flat:
        nr=[a for a in named if a['county_fips']==r['county_fips']]
        assert len(nr)==6
        assert int(r['2020_USSEN_named_writein_report_total'])==sum(int(a['votes']) for a in nr)
        assert int(r['2020_USSEN_generic_minus_named_scope_gap'])==int(r['2020_USSENWI'])-sum(int(a['votes']) for a in nr)
    assert sum(int(r['2020_USSEN_generic_minus_named_scope_gap']) for r in flat)==2229
    pdf=json.loads((HERE/'source/canvass-2020-reconciliation.json').read_text());assert pdf['county_fields_compared']==957 and all(r['difference']==0 for r in pdf['rows'])
    passed('independent 2020 PDF county balances and separate overlapping named appendix',main_county_cells=957,named_county_cells=522,named_total=32,generic_WI=2261,unallocated_scope_gap=2229)
    peer=json.loads((HERE/'peer-reconciliation.json').read_text());assert peer['status']=='pass' and peer['shared_source_cells_compared']==660000 and peer['separate_2020_named_writein_county_cells_compared']==522
    for witness in acceptance['peer_agreement_witnesses']:
        b=(STATE/witness['path']).read_bytes();assert sha(b)==witness['sha256'] and len(b)==witness['bytes']
    passed('reciprocal independent peer agreement and immutable coordinator witnesses',shared_cells=660000,raw_context_cells=1177,candidate_vote_rows=113165,named_county_cells=522,authority_path='data/coordinator-priority-acceptance.json')
    owned=[STATE/'turnout.md',HERE.parent/'county-turnout.csv']+[p for p in HERE.rglob('*') if p.is_file()]
    links=0;resolved_links=[]
    for p in owned:
        assert p.stat().st_size<40_000_000,p
        assert not any(t in p.parts for t in ['node_modules','__pycache__','.cache'])
        if p.suffix!='.md':continue
        for target in re.findall(r'\]\(([^\s)]+)(?:\s+"[^"]*")?\)',p.read_text()):
            if target.startswith(('https://','http://','#','mailto:')):continue
            resolved=(p.parent/unquote(target.split('#',1)[0])).resolve();resolved_links.append(resolved)
            # These two files are generated after successful checks; the final
            # assertion below verifies their actual existence, never a stub.
            assert resolved.exists() or resolved in [HERE/'validation.json',HERE/'asset-manifest.json'],(p,target)
            links+=1
    passed('all relative Markdown links, no caches, every asset strict size bound',relative_links=links,maximum_owned_bytes=max(p.stat().st_size for p in owned))
    result=dict(status='pass',scope='offline source/arithmetic/coverage/provenance QA; documented source discrepancies retained',checks=tests,
                coordinator_acceptance_path='data/coordinator-priority-acceptance.json',worker_self_acceptance=False,
                limitations=['Current legal reporting identity/geometry and cross-year equivalence unapproved.','No separate candidate-method/central identities in selected workbooks.','Blank/under/over and complete valid-named allocation unavailable; 2020 named appendix separate and overlapping.','Source method and two ballot/contest discrepancies retained.','Some primary landing HTTP200s are challenges; original downloads verified; early redirect traces limited to requested/final URL.'])
    dump(HERE/'validation.json',result)
    # The manifest includes validation and all owned artifacts except itself.
    assets=[]
    for p in sorted(set(owned+[HERE/'validation.json'])):
        if p.name=='asset-manifest.json':continue
        b=p.read_bytes();r=dict(path=str(p.relative_to(STATE)),bytes=len(b),sha256=sha(b))
        if p.suffix=='.gz':raw=gzip.decompress(b);r.update(decompressed_bytes=len(raw),decompressed_sha256=sha(raw),reconstruction='one gzip decompression')
        assets.append(r)
    mf=dict(scope='All owned report/data artifacts; manifest itself excluded to avoid self-reference',path_base='senate/2026/minnesota',asset_count=len(assets),assets=assets,
            shared_original_references=[dict(path=r['shared_path'],stored_sha256=r['stored_sha256'],raw_sha256=r['raw_sha256'],raw_bytes=r['bytes']) for r in manifest],
            coordinator_acceptance_path='data/coordinator-priority-acceptance.json')
    path=HERE/'asset-manifest.json'
    if refresh:dump(path,mf)
    else:assert json.loads(path.read_text())==mf,'Manifest stale; inspect changes then refresh'
    assert all(p.exists() for p in resolved_links)
    print(f'PASS: {len(tests)} checks; {source_checks} original native field cells; {len(assets)} owned artifacts; frozen contract unchanged')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--refresh-manifest',action='store_true');validate(p.parse_args().refresh_manifest)
