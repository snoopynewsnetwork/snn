"""Independent final map audit; no worker modules or PyShp adapter imported."""
from pathlib import Path
from collections import Counter
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import ast, gzip, hashlib, io, json, math, re, struct, zipfile
import shapely
from shapely.geometry import Polygon, MultiPolygon, LinearRing, Point

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'
MAP = ROOT / 'maps'
def sha(b): return hashlib.sha256(b).hexdigest()
def pin(p):
    b=p.read_bytes(); return dict(path=str(p.relative_to(ROOT)), bytes=len(b), sha256=sha(b))
def canon(x): return json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
def checked(p):
    b=(ROOT/p['path']).read_bytes(); assert len(b)==p['bytes']<40000000 and sha(b)==p['sha256']; return b
def readjson(p): return json.loads(p.read_bytes())
class Links(HTMLParser):
    def __init__(self): super().__init__(); self.refs=[]; self.ids=[]; self.tags=Counter()
    def handle_starttag(self,tag,attrs):
        a=dict(attrs); self.tags[tag]+=1
        if 'id' in a:self.ids.append(a['id'])
        for k in ('href','src'):
            if k in a:self.refs.append(a[k])

def main():
    mp=MAP/'manifest.json'; assert pin(mp)['sha256']=='a212a838b3a906a2b3afe28d661d4b61a820a5275422b4972f718b9a5a13ad9c'
    m=readjson(mp); expected={str(p.relative_to(ROOT))for p in MAP.rglob('*')if p.is_file()and p!=mp}|{'precinct-maps.md'}
    assert len(m['files'])==len(expected)==321 and {p['path']for p in m['files']}==expected
    sizes=[]
    for p in m['files']:
        b=checked(p); sizes.append(len(b)); path=ROOT/p['path']; assert not path.is_symlink()
        if path.suffix=='.py':ast.parse(b,filename=p['path'])
    assert sum(sizes)==60435395 and max(sizes)==4130951 and m['excluded_only']=='maps/manifest.json'
    assert not any(p.name in ('__pycache__','node_modules','.venv','.pytest_cache')or p.suffix in('.pyc','.pyo')for p in MAP.rglob('*'))
    v=readjson(MAP/'validation.json'); assert v['check_count']==len(v['checks'])==13 and all(c['status']=='pass'for c in v['checks'])
    assert pin(MAP/'validation.json')['sha256']=='e924b4822a6230a1f029d85570fcb4906e698817d3deec2e29e27a2a4cfd5a81'
    cp=readjson(MAP/'compatibility.json'); q=json.loads(checked(cp['complete_contract'])); idx=readjson(MAP/'index.json')
    assert sha(canon(q))==cp['complete_contract_object_sha256'] and idx['complete_contract']==cp['complete_contract']
    assert len(cp['canonical_file_references'])==401
    refs={p['path']:p for p in cp['canonical_file_references']}
    for p in refs.values():checked(p)
    for versions in cp['canonical_resolution'].values():
        for a in versions:
            b=checked(refs[a['canonical_path']]);b=gzip.decompress(b)if a['canonical_path'].endswith('.gz')else b
            assert len(b)==a['raw_bytes'] and sha(b)==a['raw_sha256']
    hd=readjson(DATA/'turnout/historical-native-complete-dependencies.json'); historical={}
    for year,n in [('2020',104),('2018',164)]:
        ss=[]
        for p in hd[year]['canonical_lossless_component_pins']:
            z=(ROOT/p['stored_path']).read_bytes();assert len(z)==p['stored_bytes']and sha(z)==p['stored_sha256']
            b=gzip.decompress(z);assert len(b)==p['original_bytes']and sha(b)==p['original_sha256']
            if p['original_path'].endswith('readings.json'):ss+=json.loads(b)['sources']
        assert len(ss)==n; byid={s['source_id']:s for s in ss};assert len(byid)==n
        for a in hd[year]['complete_source_objects_in_ledger_order']:
            s=byid[a['source_id']]
            assert sha(canon(s))==a['complete_source_object_sha256']and s['raw_sha256']==a['source_raw_sha256']
        assert cp['historical'][year]['ordered_partitions']==hd[year]['ordered_source_partitions']
        historical[year]=dict(complete_recursive_source_objects=n,all_exact_canonical_object_hashes=True)
    full=q['all_unit_order']; keys=[p['key']for p in full]; priority=q['ordered_priority_keys']
    assert len(keys)==len(set(keys))==1736 and len(priority)==887 and keys[:887]==priority
    assert idx['ordered_priority_keys']==priority and [p['key']for p in idx['full_preferred_native_entries']]==keys
    assert idx['priority_entries']==idx['full_preferred_native_entries'][:887]
    assert sum(p['named_candidate_votes']for p in full)==1215400
    assert [sum(p['named_candidate_votes']for p in full[:n])for n in(15,886,887)]==[60019,972157,972656]
    assert sum(p['named_candidate_votes']for p in full[887:])==242744
    for e in idx['full_preferred_native_entries']:
        a=e['complete_native_object_reference']; obj=q
        for part in a['json_pointer'].split('/')[1:]:obj=obj[int(part)]if isinstance(obj,list)else obj[part]
        assert sha(canon(obj))==a['canonical_object_sha256']
        for k in('key','label_literal','printed_native_id','source_id','source_page','source_raw_sha256','parent_county_fips'):assert e[k]==obj[k]
        assert e['physical_column']==obj['source_column']and e['source_role']==obj['role']
        assert e['geometry_feature_ids']is None and e['approved_current_crosswalk']is None and e['map_reference_ids']and e['gap']
    assert len(idx['all82parents'])==82 and sum(bool(p['priority_child_keys'])for p in idx['all82parents'])==77
    for p in idx['all82parents']:
        assert p['full_child_keys']==[r['key']for r in full if r['parent_county_fips']==p['parent_county_fips']]
        assert p['priority_child_keys']==q['native_priority_by_parent'][p['parent_county_fips']]
        assert p['remainder_child_keys']==[k for k in p['full_child_keys']if k not in priority]
        assert not p['current_approval']and p['gap']and p['discovery_depth']
    htmlcounts={}; markdownlinks=0
    for p in [MAP/'index.html',MAP/'inventory.html']:
        parser=Links();parser.feed(p.read_text());assert not parser.tags['script']and not parser.tags['iframe']
        for target in parser.refs:
            u=urlsplit(target)
            if not u.scheme and u.path:assert (p.parent/unquote(u.path)).exists(),(p,target)
        assert len(parser.ids)==len(set(parser.ids));htmlcounts[p.name]=dict(tags=dict(parser.tags),refs=len(parser.refs))
    for p in [ROOT/'precinct-maps.md']+list(MAP.glob('*.md')):
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            u=urlsplit(target)
            if not u.scheme and u.path:assert (p.parent/unquote(u.path)).exists(),(p,target)
            markdownlinks+=1
    audit=readjson(MAP/'geometry-audit.json');oldsp=readjson(MAP/'history/adapter-failure-v1/snapshot.json');old={}
    for p in oldsp['pins']:
        z=(ROOT/p['stored_path']).read_bytes();assert len(z)==p['stored_bytes']and sha(z)==p['stored_sha256'];b=gzip.decompress(z);assert len(b)==p['raw_bytes']and sha(b)==p['raw_sha256'];old[p['original_path']]=b
    oldaudit=json.loads(old['maps/geometry-audit.json']);finger=lambda f:{k:f[k]for k in('source_record','source_id','attributes','parts','positions','coordinate_dimension_counts','closed_rings','short_ring_indices','finite','empty','geometry_null','raw_geometry_sha256','curve_geometry')}
    for a,b in zip(oldaudit['archives_and_native_sources'],audit['archives_and_native_sources']):
        assert a['source_id']==b['source_id']and list(map(finger,a['diagnostics']['features']))==list(map(finger,b['diagnostics']['features']))
    receipts={p['id']:p for p in readjson(MAP/'shared-map-references.json')['sources']}
    for p in (MAP/'source').glob('*.receipt.json'):
        a=readjson(p);receipts[a['id']]=a
    def raw(sid):
        a=receipts[sid];z=(ROOT/a['path']).read_bytes();assert len(z)==a['stored_bytes']and sha(z)==a['stored_sha256'];b=gzip.decompress(z);assert len(b)==a['raw_bytes']and sha(b)==a['raw_sha256'];return b
    def polygon(rings):
        if not rings:return None
        assert all(len(r)>=4 and r[0]==r[-1]for r in rings)
        # Direct Esri winding interpretation, independent of the repaired PyShp adapter.
        shells=[r for r in rings if not LinearRing(r).is_ccw];holes=[r for r in rings if LinearRing(r).is_ccw]
        assert shells; ps=[Polygon(s)for s in shells];assigned=[[]for s in shells]
        for h in holes:
            candidates=[i for i,p in enumerate(ps)if p.covers(Point(h[0]))];assert candidates
            assigned[min(candidates,key=lambda i:ps[i].area)].append(h)
        polygons=[Polygon(s,hs)for s,hs in zip(shells,assigned)]
        return polygons[0]if len(polygons)==1 else MultiPolygon(polygons)
    groups=[];total=Counter()
    for a in audit['archives_and_native_sources']:
        sid=a['source_id'];ringsets=[];curves=set()
        if 'shapefile'in a:
            z=zipfile.ZipFile(io.BytesIO(raw(sid)));name=next(n for n in z.namelist()if n.endswith('.shp'));sb=z.read(name);pos=100
            while pos<len(sb):
                _,words=struct.unpack_from('>II',sb,pos);b=sb[pos+8:pos+8+2*words];nr,np=struct.unpack_from('<II',b,36);starts=list(struct.unpack_from('<'+'I'*nr,b,44));off=44+4*nr;pts=[struct.unpack_from('<dd',b,off+16*j)for j in range(np)];ringsets.append([pts[l:r]for l,r in zip(starts,starts[1:]+[np])]);pos+=8+2*words
        else:
            if sid in ('desoto-native','harrison-native'):
                proof=readjson(MAP/f'source/{sid}.service-proof.json');features=[f for batch in proof['batches']for f in json.loads(raw(batch['id']))['features']]
            else:
                w=json.loads(raw('lamar-webmap'));features=w['operationalLayers'][9]['featureCollection']['layers'][0]['featureSet']['features']
            for i,f in enumerate(features):
                g=f.get('geometry')or{};ringsets.append(g.get('rings',[]))
                if 'curveRings'in g:curves.add(i)
        ds=a['diagnostics'];assert len(ringsets)==len(ds['features']);gs=[]
        for i,rr in enumerate(ringsets):
            g=None if i in curves else polygon(rr);d=ds['features'][i]
            assert (None if g is None else g.is_valid)==d['valid'],(sid,i)
            if g is not None:assert math.isclose(g.area,d['area'],rel_tol=1e-13,abs_tol=1e-14)
            gs.append(g)
        good=[i for i,g in enumerate(gs)if g is not None and g.is_valid and not g.is_empty];tree=shapely.STRtree([gs[i]for i in good]);pairs={}
        for i in good:
            for found in tree.query(gs[i]):
                j=good[int(found)]
                if j>i:
                    area=gs[i].intersection(gs[j]).area
                    if area>0:pairs[i,j]=area
        expected={tuple(p['records']):p['area']for p in ds['pairwise_positive_area_intersections']};assert pairs.keys()==expected.keys(),sid
        assert all(math.isclose(x,expected[k],rel_tol=1e-12,abs_tol=1e-14)for k,x in pairs.items())
        invalid=[i for i,g in enumerate(gs)if g is not None and not g.is_valid];evaluated=sum(g is not None for g in gs)
        assert invalid==ds['invalid'];total.update(features=len(gs),evaluated=evaluated,invalid=len(invalid),curves=len(curves),empty=sum(not rr and i not in curves for i,rr in enumerate(ringsets)),positive_pairs=len(pairs))
        groups.append(dict(source_id=sid,features=len(gs),evaluated=evaluated,invalid_source_records=invalid,true_curve_source_records=sorted(curves),positive_area_pairs=len(pairs),native_units=ds['units'],source_pair_areas_recomputed=True))
    assert total==dict(features=2282,evaluated=2279,invalid=2,curves=2,empty=1,positive_pairs=221),total
    repair=readjson(MAP/'adapter-repair.json');assert repair['features']==2282 and repair['linear_topology_evaluated']==2279 and repair['all_evaluated_adapter_rings_exact']
    visual=readjson(MAP/'visual-qa.json')
    for p in visual['actually_inspected_files']:checked(p)
    out=dict(status='pass_independent_final_maps_manifest_full_payload_originals_topology_and_static_QA',report=pin(ROOT/'precinct-maps.md'),manifest=pin(mp),validation=pin(MAP/'validation.json'),owned_entries=321,listed_bytes=sum(sizes),maximum_stored_bytes=max(sizes),all_asset_hashes_sizes_membership_AST_no_cache=True,complete_canonical_references=401,historical_recursive_objects=historical,preferred_native=1736,priority_native=887,priority_parents=77,remainder_native=849,all_parents=82,complete_native_object_references_checked=True,approved_current_entry_level_matches=0,html=htmlcounts,markdown_links=markdownlinks,binary_review=pin(DATA/'coordinator-map-final-originals-v1-review.json'),adapter_history=pin(MAP/'history/adapter-failure-v1/snapshot.json'),all_failed_vs_final_feature_native_fingerprints_exact=True,independent_topology_totals=dict(total),independent_topology_groups=groups,topology_solver='Direct signed-ring Esri shell/hole construction and GEOS STRtree intersections; no producer code or PyShp adapter imported',coordinator_static_visuals_actually_viewed=['maps/previews/contact-1.png','maps/previews/contact-2.png','maps/previews/contact-3.png','maps/previews/contact-4.png'],producer_visual_QA=pin(MAP/'visual-qa.json'),browser_render_unavailable_qualified=True,current_geographic_approval=False,qualification='All observations retain source/vintage and shared-parent-only scope. Two invalid Love observations are separate publications, not two certified legal defects. Curves/empty excluded from linear math only, no repair or allocation. Pair areas are native-unit diagnostics; gaps/sliver significance/approved current outlines unknown. HTML checked structurally, not claimed browser-rendered.')
    p=DATA/'coordinator-finished-maps-review.json';b=(json.dumps(out,indent=2)+'\n').encode()
    if p.exists():assert p.read_bytes()==b
    else:p.write_bytes(b)
    print(json.dumps(pin(p)))

if __name__=='__main__':main()
