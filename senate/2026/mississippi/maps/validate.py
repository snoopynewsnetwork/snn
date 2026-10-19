#!/usr/bin/env python3
"""Offline, read-only by default; --write finalizes owned validation/manifest."""
import argparse,ast,collections,datetime,gzip,html,json,pathlib,re,sys,urllib.parse
from html.parser import HTMLParser
import fitz
from acquire import ROOT,STATE,body,sha,savejson
from compatibility import CONTRACT,canonical,contract,loadref,pin
from geometry import archive,audit_features,rings_to_shape

def all_owned():
    return sorted([STATE/'precinct-maps.md']+[p for p in ROOT.rglob('*') if p.is_file() and p!=ROOT/'manifest.json'])
def manifest():
    rows=[pin(str(p.relative_to(STATE))) for p in all_owned()]
    return dict(schema='ms-maps-owned-manifest-v1',scope=['precinct-maps.md','maps/**'],excluded_only='maps/manifest.json',files=rows,files_count=len(rows),listed_bytes=sum(p['bytes'] for p in rows),maximum_stored_bytes=max(p['bytes'] for p in rows),no_git_state_operations=True)
def verify_manifest():
    m=json.loads((ROOT/'manifest.json').read_text());expected=manifest();assert m==expected,'Manifest exact membership/hash/bytes mismatch';return m

def run(finalizing=False):
    checks=[];measures={}
    def ok(name,detail):checks.append(dict(check=name,status='pass',detail=detail))
    c=contract();cp=json.loads((ROOT/'compatibility.json').read_text());idx=json.loads((ROOT/'index.json').read_text());g=json.loads((ROOT/'geometry-audit.json').read_text());acq=json.loads((ROOT/'acquisition.json').read_text());sources=acq['sources'];byid={s['id']:s for s in sources}
    assert cp['complete_contract']==idx['complete_contract']==CONTRACT and cp['contract_json_pointer']==''
    assert json.loads(loadref(CONTRACT))==c and sha(canonical(c))==cp['complete_contract_object_sha256']
    assert idx['current_2026_geographic_approval'] is False and c['current_2026_geographic_approval'] is False
    ok('complete_root_contract_recursive_equality',dict(bytes=CONTRACT['bytes'],sha256=CONTRACT['sha256'],all_root_fields=list(c),current_approval=False))
    for p in cp['canonical_file_references']:loadref(p)
    for logical,versions in cp['canonical_resolution'].items():
        for v in versions:
            b=loadref(next(p for p in cp['canonical_file_references'] if p['path']==v['canonical_path']));assert len(b)==v['raw_bytes'] and sha(b)==v['raw_sha256']
    ok('complete_canonical_dependency_bodies',dict(exact_files=len(cp['canonical_file_references']),logical_paths=len(cp['canonical_resolution']),mutable_aggregate_reads=False))
    hd=json.loads(loadref(next(p for p in cp['canonical_file_references'] if p['path']=='data/turnout/historical-native-complete-dependencies.json')));hist={}
    for year,n in [('2020',104),('2018',164)]:
        objects=[]
        for p in hd[year]['canonical_lossless_component_pins']:
            packed=(STATE/p['stored_path']).read_bytes();assert sha(packed)==p['stored_sha256'] and len(packed)==p['stored_bytes'];b=gzip.decompress(packed);assert sha(b)==p['original_sha256'] and len(b)==p['original_bytes']
            if p['original_path'].endswith('readings.json'):objects+=json.loads(b)['sources']
        by={s['source_id']:s for s in objects};assert len(objects)==len(by)==n
        for p in hd[year]['complete_source_objects_in_ledger_order']:
            s=by[p['source_id']];assert sha(canonical(s))==p['complete_source_object_sha256'] and s['raw_sha256']==p['source_raw_sha256']
            assert [x['page'] for x in s['pages']]==p['pages']
        hist[year]=dict(full_recursive_objects=n,canonical_hashes_pages_and_source_hashes_exact=True,ordered_partitions=hd[year]['ordered_source_partitions'])
        if year=='2018':
            marks=[]
            for s in objects:
                for page in s['pages']:
                    for row in page.get('candidate_rows',page.get('rows',[])):
                        for col,mark in row.get('source_marks',{}).items():
                            if mark=='X':
                                values=row.get('votes',row.get('values'));assert values[int(col)-1] is None;marks.append((s['source_id'],page['page'],col,row['candidate']))
            # Candidate rows have a stable field name in these full frozen objects.
            if not marks:
                def walk(v):
                    if isinstance(v,dict):
                        if 'source_marks' in v:
                            for col,mark in v['source_marks'].items():
                                if mark=='X':
                                    vals=v.get('values',v.get('votes'));assert vals[int(col)-1] is None;marks.append((col,v.get('candidate')))
                        for q in v.values():walk(q)
                    elif isinstance(v,list):
                        for q in v:walk(q)
                walk(objects)
            assert len(marks)==6,len(marks);hist[year]['six_literal_X_numerical_nulls']=True
    ok('historical_full_source_objects_not_index_only',hist)
    keys=c['ordered_priority_keys'];full=[r['key'] for r in c['all_unit_order']]
    assert len(keys)==len(set(keys))==887 and len(full)==len(set(full))==1736
    assert idx['ordered_priority_keys']==keys==[e['key'] for e in idx['priority_entries']]
    assert idx['priority_entries']==idx['full_preferred_native_entries'][:887]
    assert [e['key'] for e in idx['full_preferred_native_entries']]==full==c['source_native_preferred_ordered_keys']
    assert sum(r['named_candidate_votes'] for r in c['all_unit_order'][:15])==60019
    assert sum(r['named_candidate_votes'] for r in c['all_unit_order'][:886])==972157
    assert sum(r['named_candidate_votes'] for r in c['all_unit_order'][:887])==972656
    assert sum(r['named_candidate_votes'] for r in c['all_unit_order'][887:])==242744
    assert sum(r['named_candidate_votes'] for r in c['all_unit_order'])==1215400
    assert full[886]=='28075:sos-2024-county-lauderdale:p9:c5' and c['all_unit_order'][886]['named_candidate_votes']==499
    for denom in [1215400,1215401]:assert 972157*5<denom*4<=972656*5
    ok('exact_887_order_1736_inventory_and_integer_thresholds',dict(priority=887,parents=77,full=1736,remainder=849,top15=60019,previous=972157,crossing=972656,remainder_votes=242744,unallocated_Pinkins=1))
    for e in idx['full_preferred_native_entries']:
        ref=e['complete_native_object_reference'];parts=ref['json_pointer'].split('/')[1:];obj=c
        for p in parts:obj=obj[int(p)] if isinstance(obj,list) else obj[p]
        assert ref['canonical_object_sha256']==sha(canonical(obj))
        for k in ['key','label_literal','printed_native_id','source_id','source_page','source_raw_sha256','parent_county_fips']:assert e[k]==obj[k]
        assert e['physical_column']==obj['source_column'] and e['source_role']==obj['role']
        assert e['geometry_feature_ids'] is None and e['approved_current_crosswalk'] is None and e['gap'] and e['map_reference_ids']
    assert len(c['source_native_constituents'])==2321 and len(c['source_native_inventory'])==84
    for p in idx['all82parents']:
        f=p['parent_county_fips'];assert p['priority_child_keys']==c['native_priority_by_parent'][f]
        assert p['full_child_keys']==[r['key'] for r in c['all_unit_order'] if r['parent_county_fips']==f]
        assert p['remainder_child_keys']==[k for k in p['full_child_keys'] if k not in keys]
        assert p['fallback_feature_count']>0 and p['gap'] and p['discovery_depth'] and not p['current_approval']
        for s in p['primary_attempt_ids']:assert s in byid
    assert len(idx['all82parents'])==82 and sum(p['priority_count']>0 for p in idx['all82parents'])==77
    ok('every_full_native_object_parent_child_null_and_alternative_preserved',dict(preferred_native_objects=1736,all_source_role_objects=2321,source_views=84,full_parents=82,shared_reference_only=True))
    rawpaths=collections.defaultdict(set)
    for s in sources:
        assert s['requested_url'] and s['request_method']=='GET' and s['retrieved_at_utc']
        if s.get('path') or s.get('segments'):
            b=body(s);assert len(b)==s['raw_bytes'] and sha(b)==s['raw_sha256'];rawpaths[s['raw_sha256']].add(s.get('path',str(s.get('segments'))))
            assert s['final_url'] and isinstance(s['headers'],dict) and isinstance(s['redirects'],list)
        else:assert s['status']==0 and s['error_type'] and s['error']
    assert all(len(v)==1 for v in rawpaths.values()),'Duplicate response bodies stored under distinct paths'
    ok('all_complete_acquisition_raw_stored_hashes_and_errors',dict(attempts=len(sources),unique_raw_bodies=len(rawpaths),body_deduplication=True))
    # Replay the corrected owned diagnostic reader against exact original bytes.
    count=0
    for s in sources:
        if s['id'].startswith('maris-') and s.get('status')==200 and s['requested_url'].endswith('.zip'):
            actual,fs=archive(s);expected=next(a for a in g['archives_and_native_sources'] if a['source_id']==s['id']);assert json.loads(json.dumps(actual))==expected,s['id'];count+=1
    assert count==14
    ok('actual_zip_crc_member_magic_offsets_dbf_and_recomputed_geometry',dict(archives=14,records=2054,all_diagnostic_objects_recursively_equal=True))
    for key,expected_count in [('desoto-native',154),('harrison-native',49)]:
        proof=json.loads((ROOT/f'source/{key}.service-proof.json').read_text());meta=json.loads(body(byid[key+'-pre']));post=json.loads(body(byid[key+'-post']));oid=meta.get('objectIdField') or next(f['name'] for f in meta['fields'] if f['type']=='esriFieldTypeOID');ids=json.loads(body(byid[key+'-ids-pre']))['objectIds'];postids=json.loads(body(byid[key+'-ids-post']))['objectIds'];assert len(ids)==len(set(ids))==expected_count and sorted(ids)==sorted(postids) and meta==post
        assert json.loads(body(byid[key+'-count-pre']))['count']==json.loads(body(byid[key+'-count-post']))['count']==expected_count
        fs=[];got=[]
        for batch in proof['batches']:
            url=urllib.parse.parse_qs(urllib.parse.urlsplit(byid[batch['id']]['requested_url']).query);assert url['outFields']==['*'] and all(url[k]==['true'] for k in ['returnGeometry','returnZ','returnM','returnTrueCurves'])
            assert not any(k in url for k in ['outSR','maxAllowableOffset','geometryPrecision','quantizationParameters'])
            d=json.loads(body(byid[batch['id']]));assert not d.get('exceededTransferLimit') and not d.get('error')
            want=list(map(int,url['objectIds'][0].split(',')));actual=[f['attributes'][oid] for f in d['features']];assert sorted(want)==sorted(actual) and len(want)<=50;got+=actual
            for f in d['features']:
                assert set(f['attributes'])=={q['name'] for q in meta['fields'] if q['type']!='esriFieldTypeGeometry'}
                v=f.get('geometry') or {};fs.append(dict(id=f['attributes'][oid],attributes=f['attributes'],rings=v.get('rings',[]),native_geometry=v,geometry_null=f.get('geometry') is None,curves='curveRings' in v,raw_geometry_sha256=sha(json.dumps(v,separators=(',',':'),ensure_ascii=False).encode())))
        assert sorted(got)==sorted(ids) and len(got)==len(set(got))
        a=next(a for a in g['archives_and_native_sources'] if a['source_id']==key);assert json.loads(json.dumps(audit_features(fs,a['diagnostics']['units'])))==a['diagnostics']
    ok('both_native_services_complete_ids_all_attributes_curves_and_recomputed_topology',dict(complete_features=203,source_default_precision_uncertainty=True,edit_clock_uncertainty=True))
    w=json.loads(body(byid['lamar-webmap']));l=next(x for x in w['operationalLayers'] if x['title']=='Voting_Precints')['featureCollection']['layers'][0];fs=[]
    for f in l['featureSet']['features']:
        v=f.get('geometry') or {};fs.append(dict(id=f['attributes']['OBJECTID'],attributes=f['attributes'],rings=v.get('rings',[]),native_geometry=v,geometry_null=f.get('geometry') is None,curves='curveRings' in v,raw_geometry_sha256=sha(json.dumps(v,separators=(',',':')).encode())))
    a=next(a for a in g['archives_and_native_sources'] if a['source_id']=='lamar-webmap-collection');assert len(fs)==25 and json.loads(json.dumps(audit_features(fs,a['diagnostics']['units'])))==a['diagnostics']
    ok('complete_embedded_collection_empty_feature_unrepaired',dict(features=25,empty_OBJECTID=17,underlying_native_precision_unknown=True))
    features=[f for a in g['archives_and_native_sources'] for f in a['diagnostics']['features']];assert len(features)==2282
    assert sum(f['valid'] is not None for f in features)==2279 and sum(f['valid'] is False for f in features)==2 and sum(f['valid'] is None for f in features)==3
    assert all(f['adapter']['all_full_xy_rings_exact'] and f['adapter']['input_rings']==f['adapter']['output_rings'] and f['adapter']['input_xy_positions']==f['adapter']['output_xy_positions'] for f in features if f['valid'] is not None)
    assert sum(len(a['diagnostics']['pairwise_positive_area_intersections']) for a in g['archives_and_native_sources'])==221
    assert sum(f['curve_geometry'] for f in features)==2 and sum(f['empty'] for f in features)==1
    old=json.loads(gzip.decompress((ROOT/'history/adapter-failure-v1/geometry-audit.json.gz').read_bytes()));snap=json.loads((ROOT/'history/adapter-failure-v1/snapshot.json').read_text())
    for p in snap['pins']:
        b=(STATE/p['stored_path']).read_bytes();assert len(b)==p['stored_bytes'] and sha(b)==p['stored_sha256'];b=gzip.decompress(b);assert len(b)==p['raw_bytes'] and sha(b)==p['raw_sha256']
    for b,a in zip(old['archives_and_native_sources'],g['archives_and_native_sources']):
        for bf,af in zip(b['diagnostics']['features'],a['diagnostics']['features']):
            for k in ['source_id','attributes','parts','positions','raw_geometry_sha256','curve_geometry','empty']:assert bf[k]==af[k]
    outer=[[0,0],[0,10],[10,10],[10,0],[0,0]];hole=[[2,2],[8,2],[8,8],[2,8],[2,2]];outer2=[[20,0],[20,5],[25,5],[25,0],[20,0]];test,proof=rings_to_shape([hole,outer2,outer]);assert test.area==89 and len(test.geoms)==2 and sum(len(x.interiors) for x in test.geoms)==1
    ok('corrected_adapter_full_ring_semantics_and_failed_history',dict(evaluated=2279,invalid=2,curve_unavailable=2,empty_unavailable=1,positive_area_source_pairs=221,source_bytes_attributes_fingerprints_unchanged=True,no_legal_gap_or_overlap_certification=True))
    class Links(HTMLParser):
        def __init__(self):super().__init__();self.links=[];self.ids=[];self.remote_embeds=[]
        def handle_starttag(self,t,a):
            v=dict(a)
            if v.get('id'):self.ids.append(v['id'])
            for k in ['href','src']:
                u=v.get(k)
                if not u:continue
                self.links.append(u)
                if urllib.parse.urlsplit(u).scheme in ['https','http'] and t!='a':self.remote_embeds.append((t,u))
    linkcount=0
    for p in [*ROOT.glob('*.html'),*ROOT.glob('*.md'),STATE/'precinct-maps.md',*ROOT.glob('previews/*.svg')]:
        txt=p.read_text()
        if p.suffix in ['.html','.svg']:
            parser=Links();parser.feed(txt);links=parser.links;assert not parser.remote_embeds
        else:links=re.findall(r'\[[^\]]*\]\(([^)]+)\)',txt)
        for u in links:
            parsed=urllib.parse.urlsplit(html.unescape(u))
            if parsed.scheme in ['https','http','mailto']:continue
            assert not parsed.scheme and not parsed.path.startswith('/'),(p,u)
            target=(p.parent/urllib.parse.unquote(parsed.path)).resolve() if parsed.path else p
            assert target.exists() or (finalizing and target in [ROOT/'validation.json',ROOT/'manifest.json']),(p,u)
            if parsed.fragment and target.suffix=='.html':assert f'id="{parsed.fragment}"' in target.read_text(),(p,u)
            linkcount+=1
    text=(ROOT/'index.html').read_text();rows=re.findall(r'<tr data-priority-rank="(\d+)" id="unit-\d+"><td>\d+<small>([^<]+)</small>',text);assert [int(r[0]) for r in rows]==list(range(1,888)) and [html.unescape(r[1]) for r in rows]==keys
    assert len(re.findall('data-full-rank=',(ROOT/'inventory.html').read_text()))==1736
    ok('all_relative_markdown_html_links_exact_order_no_remote_embeds',dict(local_links_checked=linkcount,priority_HTML_entries=887,full_HTML_entries=1736))
    svgs=list((ROOT/'previews').glob('*.svg'));assert len(svgs)==98
    assert fitz.open(str(ROOT/'previews/map-preview-atlas.pdf')).page_count==10
    qa=json.loads((ROOT/'visual-qa.json').read_text());assert qa['browser_visual_qa']=='unavailable_no_browser_surface_Chrome_cgWindowNotFound'
    for p in qa['actually_inspected_files']:assert pin(p['path'])=={k:p[k] for k in ['path','bytes','sha256']}
    ok('actual_static_visual_QA_pins_and_explicit_browser_limitation',dict(SVGs=98,atlas_pages=10,inspected_files=len(qa['actually_inspected_files']),browser='unavailable, not claimed'))
    owned=all_owned()
    for p in owned:
        assert p.stat().st_size<40000000,p
        assert '__pycache__' not in p.parts and p.suffix!='.pyc',p
        if p.suffix=='.py':ast.parse(p.read_text())
    ok('strict_file_limit_owned_scope_no_cache_and_python_AST',dict(maximum_bytes=max(p.stat().st_size for p in owned),owned_files_before_finalization=len(owned)))
    measures.update(priority_entries=887,priority_parents=77,full_preferred_entries=1736,parents=82,remainder=849,canonical_readonly_dependencies=len(cp['canonical_file_references']),native_features=2282,linear_topology_evaluated=2279,invalid_linear=2,curve_unavailable=2,empty_unavailable=1,positive_area_source_pairs=221,current_native_geometry_matches=0)
    return dict(schema='ms-maps-final-validation-v1',status='pass_bounded_acquisition_complete_inventory_qualified_native_geometry',checked_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),checks=checks,check_count=len(checks),measurements=measures,artifact_pins=[pin(p) for p in ['precinct-maps.md','maps/index.json','maps/index.html','maps/compatibility.json','maps/geometry-audit.json','maps/acquisition.json','maps/adapter-repair.json','maps/previews/map-preview-atlas.pdf']],manifest_policy='Exact owned membership/hash/bytes; excludes only maps/manifest.json. Final manifest verified after write; no manifest self-hash or reverse dispatch pin.',qualification='Completed bounded map references and offline inventory, not approved current legal/native coverage. All source originals read-only; invalid/empty/curves retained. No allocation/collector/forecast/calibrated probability.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();result=run(finalizing=a.write)
    if a.write:
        savejson(ROOT/'validation.json',result);savejson(ROOT/'manifest.json',manifest())
    m=verify_manifest()
    print(json.dumps(dict(status='pass',checks=result['check_count'],measurements=result['measurements'],manifest_files=m['files_count'],manifest_bytes=m['listed_bytes'],maximum_stored_file=m['maximum_stored_bytes'],validation=pin('maps/validation.json'),manifest=pin('maps/manifest.json')),indent=2))
