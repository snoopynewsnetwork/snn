#!/usr/bin/env python3
"""Offline, original-byte-aware QA; creates complete owned asset manifest.
No network or Git. Known source conflicts are verified, never repaired.
"""
import collections,csv,gzip,hashlib,io,json,re,zipfile
from fractions import Fraction
from pathlib import Path
from html_tables import Tables
D=Path(__file__).resolve().parent;S=D.parent.parent
def sha(b):return hashlib.sha256(b).hexdigest()
def readjson(p):return json.loads(p.read_text())
def writejson(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
    checks=[];receipts=list((D/'source').glob('*.receipt.json'));source_count=0
    for p in receipts:
        r=readjson(p)
        if 'stored_path' not in r:assert 'error' in r;continue
        stored=(D/r['stored_path']).read_bytes();raw=gzip.decompress(stored)
        assert len(stored)==r['stored_bytes'] and sha(stored)==r['stored_sha256'];assert len(raw)==r['raw_bytes'] and sha(raw)==r['raw_sha256'];assert r.get('retrieved_utc') and r.get('requested_url');source_count+=1
    refs=readjson(D/'source/shared-source-references.json');zips={};rawmembers={}
    for sid,r in refs.items():
        stored=(D/'source'/r['relative_path']).read_bytes();assert sha(stored)==r['stored_sha256'];raw=gzip.decompress(stored);assert sha(raw)==r['raw_sha256']
        if 'precinct' in sid and 'schema' not in sid:
            z=zipfile.ZipFile(io.BytesIO(raw));assert z.testzip() is None;zips[sid]=z
            for info in z.infolist():rawmembers[(sid,info.filename)]=z.read(info)
    checks.append(dict(check='HTTP and shared original stored/raw hashes',status='pass',own_receipts=source_count,shared_entities=len(refs)))
    inv=readjson(D/'extracts/original-member-inventory.json');expected_selected={};allrows=0
    for m in inv:
        b=rawmembers[(m['source_id'],m['source_member'])];assert len(b)==m['bytes'] and sha(b)==m['sha256'];assert f"{zips[m['source_id']].getinfo(m['source_member']).CRC:08x}"==m['crc32'];assert len(b.splitlines())==m['all_rows'];allrows+=m['all_rows'];expected_selected[(m['source_id'],m['source_member'])]=m['selected_rows']
    assert allrows==1707538 and len(inv)==208
    positions=set();seen=collections.Counter();bycontext=collections.Counter();countycategory=collections.Counter();rowfields={};row_count=0
    for year in ['2024','2022','2020']:
        for line in gzip.open(D/'extracts'/f'native-source-rows-{year}.jsonl.gz','rt'):
            r=json.loads(line);key=(r['source_id'],r['source_member'],r['source_row_1based']);assert key not in positions;positions.add(key);b=rawmembers[key[:2]];rawline=b[r['source_byte_offset']:r['source_byte_offset']+r['source_line_bytes']];assert sha(rawline)==r['source_line_sha256'];fields=rawline.decode(r['source_encoding']).rstrip('\r\n').split('\t');assert len(fields)==19 and fields==r['fields'];assert int(fields[18])>=0;rowfields[key]=fields;seen[key[:2]]+=1;row_count+=1
            assert fields[0] in r['native_key'] and fields[13] in ('100000','120000')
            if not r['recount_overlap_excluded']:
                countycategory[(r['context'],fields[0],*fields[14:18])]+=int(fields[18])
    assert row_count==211874;assert dict(seen)=={k:v for k,v in expected_selected.items() if v}
    checks.append(dict(check='all retained selected fields against exact original source-line bytes/positions',status='pass',positions=row_count,fields=row_count*19,members=len(inv),all_original_rows=allrows))
    units={};blank=collections.Counter();regmulti=0
    for line in gzip.open(D/'extracts/native-units.jsonl.gz','rt'):
        u=json.loads(line);assert u['native_key'] not in units;units[u['native_key']]=u;bycontext[u['context']]+=1
        assert u['method_scope']=='not separately coded in original19; polling label retained, not a validated method'
        if not u['precinct_id_available']:assert not u['precinct_id'].strip();blank[u['context']]+=1
        regmulti+=len(u['registration_observations'])!=1
        for r in u['candidate_category_rows']:
            f=rowfields[(u['source_id'],u['source_member'],r['source_row_1based'])];assert [r['candidate_label'],r['party'],r['fvrs_id'],r['doe_candidate_id'],str(r['votes'])]==f[14:19];assert f[7:11] in u['registration_observations'];assert f[5:7]==[u['precinct_id'],u['polling_location']]
    assert dict(bycontext)=={'2024_president':5712,'2024_senate':5710,'2022_senate':6013,'2020_president':6097};assert dict(blank)=={'2022_senate':9};assert not regmulti
    controls=readjson(D/'extracts/primary-county-tables.json');cc=list(csv.DictReader((D.parent/'county-turnout.csv').open()));assert len(cc)==67;assert len({r['county_fips'] for r in cc})==67;assert len({r['source_county_code'] for r in cc})==67
    for context,t in controls.items():
        receipt=readjson(D/'source'/f"{t['source_id']}.receipt.json");tr=Tables(gzip.decompress((D/receipt['stored_path']).read_bytes()).decode('cp1252')).rows;assert tr[1][1:]==t['candidates'];assert len(t['county'])==67
        assert {candidate:sum(v[candidate] for v in t['county'].values()) for candidate in t['candidates']}==t['statewide']
        for county,v in t['county'].items():assert dict(zip(t['candidates'],[int(x.replace(',','')) for x in tr[t['county_source_tr_1based'][county]-1][1:]]))==v
        for r in cc:
            norm=lambda s:s.upper().replace('DE SOTO','DESOTO').strip();v=next(v for k,v in t['county'].items() if norm(k)==norm(r['county']));assert sum(v.values())==int(r[context+'_candidate_votes']);assert sum(v for k,v in v.items() if k.endswith('(WRI)'))==int(r[context+'_valid_named_writeins']);assert r[context+'_blank_ballots']==''
            for doe,suf in [('900','generic_writein_marks'),('901','overvotes'),('902','undervotes')]:assert sum(v for k,v in countycategory.items() if k[0]==context and k[1]==r['source_county_code'] and k[-1]==doe)==int(r[context+'_'+suf])
    assert sum(len(t['candidates'])*67 for t in controls.values())==2479
    checks.append(dict(check='complete primary candidates/counties/state controls; raw categories distinct',status='pass',county_count=67,primary_candidate_cells=2479,native_contexts=dict(bycontext),blank_precinct_ids=dict(blank),known_source_differences=readjson(D/'extracts/source-discrepancies.json')))
    federal=readjson(D/'extracts/federal-candidate-reconciliation.json');assert len(federal)==15
    for r in federal:assert r['clerk_votes']==r['dos_all_county_sum']==controls[r['context']]['statewide'][r['dos_header']] and r['difference']==0
    for r in readjson(D/'source/federal-original-references.json'):
        stored=(D/'source'/r['stored_original_relative_to_this_source']).read_bytes();assert sha(stored)==r['stored_sha256'] and len(stored)==r['stored_bytes'];raw=gzip.decompress(stored);assert sha(raw)==r['raw_sha256'] and len(raw)==r['raw_bytes']
    assert controls['2024_president']['statewide']['Trump / Vance (REP)']==6110125
    assert controls['2024_president']['statewide']['Ayyadurai / Ellis (WRI)']==199 and controls['2024_president']['statewide']['Fox / McVay (WRI)']==6
    checks.append(dict(check='independent House Clerk Senate controls and visually inspected signed NARA presidential controls',status='pass',federal_candidate_controls=15,NARA_Trump=6110125,NARA_named_writeins=205))
    p=readjson(D/'priority-set.json');pin=readjson(D/'priority-freeze.json');raw=(D/'priority-set.json').read_bytes();assert sha(raw)==pin['sha256'] and len(raw)==pin['bytes'];assert not p['coordinator_accepted'];assert p['coordinator_acceptance_path']=='data/coordinator-priority-acceptance.json'
    total=sum(int(r['2024_senate_candidate_votes']) for r in cc);assert total==10757428;assert cc==sorted(cc,key=lambda r:(-int(r['2024_senate_candidate_votes']),r['county_fips']));c=0
    assert sum(Fraction(int(r['2024_senate_candidate_votes']),total) for r in cc)==1
    for i,r in enumerate(cc,1):
        c+=int(r['2024_senate_candidate_votes']);assert int(r['rank_2024_senate'])==i and int(r['cumulative_votes_2024_senate'])==c;assert p['all_unit_order'][i-1]['key']==r['geography_key'];assert p['all_unit_order'][i-1]['votes']==int(r['2024_senate_candidate_votes']);assert int(r['top15'])==(i<=15);assert int(r['minimum80'])==(i<=22)
    assert p['top15']['votes']==sum(int(r['2024_senate_candidate_votes']) for r in cc[:15]);assert p['minimum80']['preceding_votes']==sum(int(r['2024_senate_candidate_votes']) for r in cc[:21]);assert p['minimum80']['votes']==sum(int(r['2024_senate_candidate_votes']) for r in cc[:22]);assert 5*p['minimum80']['preceding_votes']<4*total<=5*p['minimum80']['votes'];assert p['ordered_priority_keys']==[r['geography_key'] for r in cc[:22]];assert p['remainder']['votes']==total-p['minimum80']['votes']
    gulf=next(r for r in p['all_unit_order'] if r['source_county_code']=='GUL');assert gulf['ordinary_poll_close_2026_utc'] is None and gulf['ordinary_election_admin_clock'] is None
    covered=[]
    for parent in p['native_constituents']:
        assert len(parent['units'])==parent['constituent_count'];assert parent['valid_named_writein_native_allocation'] is None
        for u in parent['units']:assert units[u['native_key']]['parent_key']==parent['parent_key'];covered.append(u['native_key'])
        for context,other in parent['other_contexts'].items():
            assert len(other['units'])==other['constituent_count']
            for u in other['units']:assert units[u['native_key']]['context']==context and units[u['native_key']]['parent_key']==parent['parent_key'];covered.append(u['native_key'])
    assert len(covered)==len(set(covered))==len(units);assert set(covered)==set(units)
    for r in cc:
        rec=readjson(D/'source'/f"supervisor-{r['source_county_code']}.receipt.json");assert rec['status']==200
    checks.append(dict(check='frozen contract, complete disjoint county/native coverage, weights/order/strict minimum crossing, authority inventory',status='pass',native_constituents=len(covered),county_order=67,priority_count=22,sha256=pin['sha256'],bytes=pin['bytes'],Gulf_singular_clock=None))
    acceptance_path=S/p['coordinator_acceptance_path'];acceptance=readjson(acceptance_path);assert acceptance['accepted'] and acceptance['status']=='accepted_historical_dispatch_only';assert acceptance['contract']['sha256']==pin['sha256'] and acceptance['contract']['bytes']==pin['bytes'];assert acceptance['ordered_priority_keys']==p['ordered_priority_keys']
    for witness in acceptance['peer_witnesses']+acceptance['independent_reviews']:
        b=(S/witness['path']).read_bytes();assert sha(b)==witness['sha256'] and len(b)==witness['bytes']
    checks.append(dict(check='external coordinator historical-only acceptance and immutable independent witnesses',status='pass',authority_path=p['coordinator_acceptance_path'],scope='historical dispatch only; no current geography/method/ballot approval',worker_contract_acceptance_flag=False))
    for s in readjson(D/'sensitivity.json'):
        ordered=sorted(cc,key=lambda r:(-int(r[s['metric']]),r['county_fips']));den=sum(int(r[s['metric']]) for r in ordered);assert den==s['statewide'];assert s['full_order']==[r['geography_key'] for r in ordered];k=s['minimum80_count'];assert sum(int(r[s['metric']]) for r in ordered[:k-1])==s['preceding_votes'];assert sum(int(r[s['metric']]) for r in ordered[:k])==s['crossing_votes'];assert 5*s['preceding_votes']<4*den<=5*s['crossing_votes'];assert sum(int(r[s['metric']]) for r in cc[:22])==s['priority_counties_share_numerator']
    eavs=[json.loads(x) for x in gzip.open(D/'extracts/eavs-controls.jsonl.gz','rt')];book=[json.loads(x) for x in gzip.open(D/'extracts/bookclosing-controls.jsonl.gz','rt')];assert len(eavs)==len(book)==134;assert all(re.fullmatch(r'\d+',r['fields']['F1a']) for r in eavs);assert any(r['fields']['F1c']=='-99' for r in eavs);assert any(r['fields']['F1b']=='-99' for r in eavs)
    for y in ['2024','2022']:
        assert len({r['fips'] for r in eavs if r['context']==y})==67;assert len({r['fips'] for r in book if r['context']==y})==67
    checks.append(dict(check='eight complete alternative metric orders/denominators and source-scoped EAVS/bookclosing controls',status='pass',eavs_rows=len(eavs),bookclosing_rows=len(book),method_overlaps_and_sentinels_preserved=True))
    peer=readjson(D/'peer-agreement.json');assert peer['status']=='pass' and peer['raw_fields_compared']==4025606
    # Peer hashes represent a specific independent comparison, not ongoing file ownership.
    checks.append(dict(check='independent peer agreement witness',status='pass',positions=peer['raw19_source_positions'],primary_candidate_cells=peer['primary_county_candidate_cells'],eavs_shared_fields=peer['eavs_shared_fields'],bookclosing_exact_cells=peer['bookclosing_exact_cells']))
    links=0;deferred=[]
    for md in [S/'turnout.md',D/'source/SCHEMA.md']:
        for target in re.findall(r'\]\(([^)]+)\)',md.read_text()):
            if target.startswith(('http://','https://','#')):continue
            path=target.split('#')[0].split(':')[0];dest=(md.parent/path).resolve()
            if dest in [(D/'validation.json').resolve(),(D/'asset-manifest.json').resolve()]:deferred.append(dest)
            else:assert dest.exists(),(md,target)
            links+=1
    checks.append(dict(check='all report/schema relative Markdown links',status='pass',links=links))
    assets=[S/'turnout.md',D.parent/'county-turnout.csv']+[p for p in D.rglob('*') if p.is_file() and p.name not in ['asset-manifest.json','validation.json']]
    assert not any('__pycache__' in p.parts or p.suffix=='.pyc' for p in assets),'Remove owned interpreter cache before delivery'
    assert all(p.stat().st_size<40000000 for p in assets)
    validation=dict(status='pass_with_documented_source_gaps',offline=True,checks=checks,coordinator_accepted=False,priority_freeze=pin,asset_policy='Complete owned files including validation.json; asset-manifest excludes only itself to avoid a self hash; every artifact strictly below40000000bytes',material_limits=['compiled primary differences retained','valid write-in native allocations unavailable','candidate-by-method unavailable in compiled schema','EAVS method overlap and source differences retained','blank ballots and uniform tabulator-ballot counts unavailable','historical native IDs not approved November2026 boundaries','Gulf singular polling/admin clock null'])
    writejson(D/'validation.json',validation);assets.append(D/'validation.json');assets=sorted(assets,key=lambda p:str(p.relative_to(S)))
    items=[dict(path=str(p.relative_to(S)),bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in assets]
    manifest=dict(schema_version=1,root='senate/2026/florida',self_excluded='data/turnout/asset-manifest.json',assets=items,shared_originals=refs,reconstruction='Each gzip fully restores original entity or complete extracted JSONL. Original ZIP bytes/member positions/hashes retained. No truncation/simplification.')
    writejson(D/'asset-manifest.json',manifest)
    assert all(p.exists() for p in deferred)
    for r in items:assert r['bytes']<40000000 and sha((S/r['path']).read_bytes())==r['sha256']
    actual={str(p.relative_to(S)) for p in D.rglob('*') if p.is_file() and p.name!='asset-manifest.json'}|{'turnout.md','data/county-turnout.csv'};assert actual=={r['path'] for r in items}
    print(json.dumps(dict(status=validation['status'],checks=len(checks),asset_count=len(items),maximum_asset_bytes=max(r['bytes'] for r in items),relative_links=links,priority_sha256=pin['sha256'],candidate_votes=total,priority_count=22,all_native_contexts=len(units)),indent=2))
if __name__=='__main__':main()
