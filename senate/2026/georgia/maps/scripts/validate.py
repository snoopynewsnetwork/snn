#!/usr/bin/env python3
"""Meaningful independent offline checks; updates only owned manifest/validation on request."""
import argparse, collections, csv, datetime, gzip, hashlib, html.parser, io, json, math, pathlib, re, struct, sys, urllib.parse, zipfile
import shapefile, shapely, pyproj, fitz, PIL, requests
from acquire import ROOT,STATE,sha,entity,read_record,dump

def load(p):return json.loads(p.read_text())
def gzload(p):return json.loads(gzip.decompress(p.read_bytes()))
def pointer(d,p):
    for k in p.strip('/').split('/'):
        k=k.replace('~1','/').replace('~0','~');d=d[int(k)] if isinstance(d,list) else d[k]
    return d

def validate(manifest_will_be_created=False):
    checks={}
    pins=load(ROOT/'input-pins.json')
    expected={'turnout.md':'c9f89b6334d961d0d0daa32f583a74ef11078ffa38d452f55688e2ba63d2fafa','data/county-turnout.csv':'4c2e9a0725fcb355dd10b96bf662da3f1bb41e3492be75a75a0ef7b15f7c0104','data/turnout/asset-manifest.json':'591cb2c893a377c9e56c2480a599dec290dfd68d8ac7baa51319bba70c4e4220','county-partisanship.md':'7951f084f0ac62996df5b09a54a9dd59f64c05506c500b9c14c83d668831bd4b','data/county-baselines.csv':'940c99db5c49586cda8f6a9085d1faea60bfb67fd20e2fc4ca186ff597e5542d','data/baselines/asset-manifest.json':'bd089283cb93d3e74105da216a9d280e4d9f2b4b282054abeff0dcd3a44a0418','data/turnout/priority-set.json':'1f589d2785d985af2eb33de50adad5a398924ab55f9343deaf79ac5c7378d97a'}
    for p,x in pins.items():
        b=(STATE/p).read_bytes();assert len(b)==x['bytes'] and sha(b)==x['sha256'],p
        if p in expected:assert x['sha256']==expected[p],p
    checks['frozen_first_wave_and_external_acceptance_pins']=len(pins)
    c=load(STATE/'data/turnout/priority-set.json');a=load(STATE/'data/coordinator-priority-acceptance.json');proof=load(STATE/'data/coordinator-priority-membership-review.json')
    assert a['accepted'] and a['contract_sha256']==expected['data/turnout/priority-set.json'] and a['ordered_dispatch_keys']==c['ordered_priority_keys']
    assert len(c['coverage'])==159 and len(c['ordered_priority_keys'])==44 and c['full_candidate_priority_order'] is None
    assert sum(x['votes'] for x in c['coverage'])==5250047
    assert sum(x['votes'] for x in c['coverage'][:15])==2939795
    assert sum(x['votes'] for x in c['coverage'][:43])==4199292
    assert sum(x['votes'] for x in c['coverage'][:44])==4222572
    assert (5250905*4+4)//5==4200724 and 4199292+858==4200150<4200724<=4222572
    assert proof['maximum_Liberty_all_valid']==23258<23280 and 22353+858==23211<23280
    checks['priority_bounds_and_named_four_order']='pass; membership/cardinality44 only; full-candidate order unknown'
    inv=load(ROOT/'inventory.json');assert len(inv)==159 and len({x['county_fips'] for x in inv})==159
    assert [x['county_key'] for x in sorted([v for v in inv if v['named_four_dispatch_rank']],key=lambda x:x['named_four_dispatch_rank'])]==a['ordered_dispatch_keys']
    origkeys={x['key'] for k in c['coverage'] for x in k['constituents']};keys={key for k in inv for key in k['source_native_keys']};assert keys==origkeys and len(keys)==2701
    assert sum(x['source_native2024_count'] for x in inv if x['named_four_dispatch_rank'])==1938
    assert sum(x['source_native2024_count'] for x in inv if not x['named_four_dispatch_rank'])==763
    checks['county_native_scopes']=dict(counties=159,priority_counties=44,priority_native=1938,nonpriority_native=763,all_native=2701)
    # Exact byte reconstruction, not merely stored-file hashes.
    receipts=[load(p) for p in (ROOT/'receipts').glob('*.json')]
    for r in receipts:
        assert [s['order'] for s in r['storage']]==list(range(len(r['storage'])))
        for s in r['storage']:
            z=(ROOT/s['path']).read_bytes();assert len(z)==s['stored_bytes'] and sha(z)==s['stored_sha256']
            b=gzip.decompress(z) if s.get('encoding','gzip')=='gzip' else z
            assert len(b)==s['entity_bytes'] and sha(b)==s['entity_sha256']
        b=entity(r);assert len(b)==r['entity_bytes'] and sha(b)==r['entity_sha256']
        if r.get('parent'):assert (ROOT/'receipts'/f'{r["parent"]}.json').exists(),r['id']
    checks['exact_http_entities_and_storage']=len(receipts)
    z=zipfile.ZipFile(io.BytesIO(entity('state-2024-precinct-zip')));assert z.testzip() is None
    arch=load(ROOT/'extracts/archive-inspection.json')
    for x in arch['members']:
        b=z.read(x['name']);assert len(b)==x['bytes'] and sha(b)==x['sha256'] and f'{z.getinfo(x["name"]).CRC:08x}'==x['crc32']
    base=next(n[:-4] for n in z.namelist() if n.endswith('.shp'));shp=z.read(base+'.shp');shx=z.read(base+'.shx');dbf=z.read(base+'.dbf')
    assert struct.unpack('>I',shp[24:28])[0]*2==len(shp) and struct.unpack('>I',shx[24:28])[0]*2==len(shx)
    cursor=100;n=0
    while cursor<len(shp):
        recnum,words=struct.unpack('>II',shp[cursor:cursor+8]);offset2,length2=struct.unpack('>II',shx[100+8*n:108+8*n]);assert offset2*2==cursor and length2==words and recnum==n+1
        cursor+=8+words*2;n+=1
    assert cursor==len(shp) and n==(len(shx)-100)//8==struct.unpack('<I',dbf[4:8])[0]==2724
    reader=shapefile.Reader(shp=io.BytesIO(shp),shx=io.BytesIO(shx),dbf=io.BytesIO(dbf));allrows=list(reader.iterShapeRecords());assert len(allrows)==2724
    # Every selected vertex/part/native attribute compared independently to original SHP/DBF.
    geometries=[]
    for x in inv:
        indices=[i for i,s in enumerate(allrows) if s.record['FIPS']==x['county_fips']];assert indices==x['state_map2024_row_ordinals']
        if x['named_four_dispatch_rank']:
            d=gzload(ROOT/f'extracts/{x["county_fips"]}-state2024-native-geometry.json.gz');assert d['original_crs_wkt']==z.read(base+'.prj').decode()
            assert [r['row_ordinal'] for r in d['features']]==indices
            for r in d['features']:
                raw=allrows[r['row_ordinal']];assert r['attributes']==raw.record.as_dict()
                assert r['points']==[list(v) for v in raw.shape.points] and r['parts']==list(raw.shape.parts)
                assert r['bbox']==list(raw.shape.bbox) and r['z'] is None and r['m'] is None and r['shape_type']==5
            geometries+=d['features']
    unknown=gzload(ROOT/'extracts/state2024-unmatched-native-geometry.json.gz')['features'];assert len(unknown)==27
    assert [r['row_ordinal'] for r in unknown]==[i for i,s in enumerate(allrows) if not s.record['FIPS']]
    for r in unknown:
        raw=allrows[r['row_ordinal']];assert r['attributes']==raw.record.as_dict() and r['points']==[list(v) for v in raw.shape.points] and r['parts']==list(raw.shape.parts)
    assert sum(len(s.shape.points) for s in allrows)==1775333 and sum(len(s.shape.parts) for s in allrows)==3436
    checks['original_zip_shp_shx_dbf_and_full_coordinates']=dict(member_crc_hashes='pass',records=n,vertices=1775333,parts=3436,priority_exact_native_rows=len(geometries),unassigned_exact_rows=27)
    # Independently audit complete historical context and redaction positions from original JSON.
    hp=load(ROOT/'historical-source-pins.json')
    for p,x in hp.items():
        b=(STATE/p).read_bytes();assert len(b)==x['bytes'] and sha(b)==x['sha256']
        if 'entity_sha256' in x:assert sha(gzip.decompress(b))==x['entity_sha256']
    ctx=[json.loads(s) for s in gzip.decompress((ROOT/'extracts/native-contexts.jsonl.gz').read_bytes()).splitlines()];assert len(ctx)==2701
    cc={x['key']:x for v in c['coverage'] for x in v['constituents']};sources={};nullcand=nullmethod=ballots=registration=0;nativecount=0;null_method_counties=set()
    for x in ctx:
        q=x['contract_constituent'];assert q==cc[q['key']]
        p=x['source_body_path']
        if p not in sources:
            raw=gzip.decompress((STATE/p).read_bytes());d=json.loads(raw);sources[p]=d
            assert sha(raw)==x['source_body_entity_sha256']
            for row in d['ballotItemWithBreakdown']['breakdownResults']:
                nativecount+=1
                for cand in row['ballotOptions']:
                    nullcand+=cand['voteCount'] is None
                    for g in cand['groupResults']:
                        if g['voteCount'] is None:nullmethod+=1;null_method_counties.add(x['county_fips'])
            ballots+=d['election']['ballotsCast'];registration+=d['election']['totalVoters']
        d=sources[p];assert pointer(d,x['original_precinct_pointer'])==x['original_precinct_object']
        assert pointer(d,x['original_turnout_pointer'])==x['original_turnout_object']
        assert d['election']==x['county_source_election'] and d['jurisdiction']==x['county_source_jurisdiction']
        assert x['geographic_join_status'].startswith('no approved')
    assert len(sources)==159 and nativecount==2701 and nullcand==40 and nullmethod==22416 and len(null_method_counties)==130
    assert ballots==5297264 and registration==7219868
    checks['native_original_objects_and_null_controls']=dict(county_originals=159,identities=2701,candidate_nulls=40,method_nulls=22416,method_null_counties=130,ballots=ballots,registration=registration)
    # All service batches: IDs, flags, geometry omissions and exact parsed extraction.
    services=load(ROOT/'service-inspection.json');complete=0;features_total=0
    for s in services:
        if not s.get('advertised_count'):continue
        meta=json.loads(entity(s['id']+'-metadata'));oid=s['oid_field']
        before=json.loads(entity(s['id']+'-ids-before'))['objectIds'];after=json.loads(entity(s['id']+'-ids-after'))['objectIds']
        seen=[];sets=[]
        for b in s['batches']:
            d=json.loads(entity(b));assert not d.get('exceededTransferLimit',False)
            seen += [f['attributes'][oid] for f in d['features']];sets.append(d)
        assert len(seen)==len(set(seen))==s['advertised_count'] and sorted(seen)==sorted(before)==sorted(after)
        d=gzload(ROOT/f'extracts/{s["id"]}-service-native.json.gz');assert d['metadata']==meta and d['feature_sets']==sets
        present=sum('geometry' in f for x in sets for f in x['features']);assert present==s['geometry_key_count']
        if s['status']=='complete':
            assert present==len(seen) and s['null_geometry_count']==s['omitted_geometry_count']==s['empty_geometry_count']==0 and s['metadata_editingInfo_equal'];complete+=1;features_total+=len(seen)
        else:assert s['status']=='complete_ids_geometry_unavailable' and present==0
    assert complete==12 and features_total==1044
    checks['services']=dict(complete_native_snapshots=complete,complete_features=features_total,omitted_geometry_captures=sum(s['status']=='complete_ids_geometry_unavailable' for s in services),all_ids_pre_post_transfer_checks='pass')
    # Source-specific map claims and exact original control bytes.
    large=ROOT/'originals/forsyth-current-large-retry.pdf';doc=fitz.open(large);txt=' '.join(p.get_text() for p in doc)
    assert 'November 3, 2026' in txt and 'General Election' in txt
    assert 'may become final' in ' '.join((ROOT/'qa/columbia-2026-notice-100.txt').read_text().split())
    assert 'The approved changes result in the elimination of South Forsyth (21)' in entity('forsyth-precinct-parent').decode()
    assert all(len(x['attempt_receipt_ids'])>0 for x in load(ROOT/'gaps.json'))
    assert len(load(ROOT/'gaps.json'))==44
    checks['documentary_scope_and_exact_gaps']='pass; Forsyth November publication, Columbia proposals, all44 exact gaps retained'
    # Static offline links, card order, native detail pages and no remote visual dependencies.
    class Links(html.parser.HTMLParser):
        def __init__(self):super().__init__();self.refs=[];self.cards=[]
        def handle_starttag(self,tag,attrs):
            a=dict(attrs)
            if tag in ['a','img','script','link']:
                u=a.get('href') if tag in ['a','link'] else a.get('src')
                if u:self.refs.append((tag,u))
            if tag=='article':self.cards.append(a.get('id'))
    broken=[];links=0
    for p in list(ROOT.rglob('*.html'))+[STATE/'precinct-maps.md',ROOT/'SCHEMA.md']:
        s=p.read_text()
        if p.suffix=='.html':
            parser=Links();parser.feed(s);refs=parser.refs
            if p.name=='index.html':assert parser.cards==['county-'+k.rsplit(':',1)[-1] for k in a['ordered_dispatch_keys']]
        else:refs=[('a',u) for u in re.findall(r'\[[^\]]*\]\(([^)]+)\)',s)]
        for tag,u in refs:
            if u.startswith(('https:','http:','mailto:','data:','#')):
                assert tag not in ['img','script','link'],(p,u)
                continue
            target=p.parent/urllib.parse.unquote(u.split('#')[0].split('?')[0]);links+=1
            if not target.exists() and not (manifest_will_be_created and target.resolve() in {ROOT/'manifest.json',ROOT/'manifest.csv',ROOT/'validation.json'}):broken.append((str(p.relative_to(STATE)),u))
    assert not broken,broken
    checks['offline_relative_links_and_card_order']=dict(checked_links=links,broken=broken,county_native_pages=len(list((ROOT/'counties').glob('*.html'))))
    owned=[p for p in ROOT.rglob('*') if p.is_file()]+[STATE/'precinct-maps.md']
    assert all(p.stat().st_size<40_000_000 for p in owned)
    assert not any(p.name in ('__pycache__','node_modules','.cache') for p in ROOT.rglob('*'))
    originals=list((ROOT/'originals').glob('*'));hashes=[sha(p.read_bytes()) for p in originals];assert len(hashes)==len(set(hashes))
    checks['artifact_bounds']=dict(max_file_bytes=max(p.stat().st_size for p in owned),strict_cap=40000000,no_duplicate_original_entities=True,no_cache_or_dependency_trees=True)
    return checks

def assets():
    return sorted([p for p in ROOT.rglob('*') if p.is_file() and p.name not in ('manifest.json','manifest.csv')]+[STATE/'precinct-maps.md'])
def manifest():
    rows=[dict(path=str(p.relative_to(STATE)),bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in assets()]
    dump(ROOT/'manifest.json',dict(schema='georgia-maps-artifact-manifest-v1',scope='Owned maps/** and precinct-maps.md only; excludes the two manifest files themselves',artifacts=rows,read_only_inputs=load(ROOT/'input-pins.json'),historical_source_pins='historical-source-pins.json'))
    with (ROOT/'manifest.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['path','bytes','sha256']);w.writeheader();w.writerows(rows)
def check_manifest():
    m=load(ROOT/'manifest.json');assert {x['path'] for x in m['artifacts']}=={str(p.relative_to(STATE)) for p in assets()}
    for x in m['artifacts']:
        p=STATE/x['path'];assert p.stat().st_size==x['bytes'] and sha(p.read_bytes())==x['sha256'],x['path']
    assert list(csv.DictReader((ROOT/'manifest.csv').open()))==[{k:str(v) for k,v in x.items()} for x in m['artifacts']]
    return len(m['artifacts'])

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--update-manifest',action='store_true');args=p.parse_args()
    checks=validate(args.update_manifest)
    if args.update_manifest:
        dump(ROOT/'validation.json',dict(status='pass',checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),checks=checks,versions=dict(python=sys.version,pyshp=shapefile.__version__,shapely=shapely.__version__,geos=shapely.geos_version_string,pyproj=pyproj.__version__,pymupdf=fitz.VersionBind,pillow=PIL.__version__,requests=requests.__version__)))
        manifest()
    n=check_manifest();print(json.dumps(dict(status='pass',checks=checks,owned_artifacts_verified=n),indent=2))
