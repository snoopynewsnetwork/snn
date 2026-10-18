#!/usr/bin/env python3
"""Offline, deterministic extraction. No joins of results to geometry and no repairs."""
import collections, colorsys, csv, gzip, hashlib, html, io, json, math, pathlib, struct, sys, zipfile
import shapefile
from pyproj import CRS
from shapely.geometry import shape, Polygon
from shapely.validation import explain_validity
from shapely.strtree import STRtree
import shapely
from acquire import ROOT, STATE, entity, read_record, sha, dump

def writegz(p, obj):
    p.parent.mkdir(exist_ok=True,parents=True)
    b=json.dumps(obj,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()
    z=gzip.compress(b,mtime=0);assert len(z)<40_000_000;p.write_bytes(z)
def csvwrite(p,rows):
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def svg(p,rows,title,footer='2024 state reference · full extent · preview coordinates rounded in display pixels'):
    points=[xy for r in rows for xy in r['points'] if all(math.isfinite(c) for c in xy[:2])]
    if not points:return
    xmin=min(v[0] for v in points);xmax=max(v[0] for v in points);ymin=min(v[1] for v in points);ymax=max(v[1] for v in points)
    scale=min(720/(xmax-xmin or 1),490/(ymax-ymin or 1));ox=(800-(xmax-xmin)*scale)/2;oy=45
    a=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600"><rect width="800" height="600" fill="#f3f6f8"/>',f'<text x="25" y="28" font-family="sans-serif" font-size="19">{html.escape(title)}</text>']
    for j,r in enumerate(rows):
        parts=list(r['parts'])+[len(r['points'])];paths=[]
        for k in range(len(parts)-1):
            pts=r['points'][parts[k]:parts[k+1]]
            paths.append('M'+' L'.join(f'{ox+(x-xmin)*scale:.2f},{oy+(ymax-y)*scale:.2f}' for x,y,*_ in pts)+' Z')
        color='#'+''.join(f'{round(x*255):02x}' for x in colorsys.hls_to_rgb(((j*137)%360)/360,0.78,0.35))
        a.append(f'<path d="{" ".join(paths)}" fill="{color}" stroke="#334e61" stroke-width="0.65" fill-rule="evenodd"><title>{html.escape(str(r["attributes"]))}</title></path>')
    a.append(f'<text x="25" y="572" font-family="sans-serif" font-size="12">{html.escape(footer)}</text></svg>')
    p.parent.mkdir(exist_ok=True,parents=True);p.write_text(''.join(a))

def geometry_diagnostics(rows,units):
    bad=[];null=[];nonfinite=[];geoms=[];validrows=[];vertex=parts=0
    for r in rows:
        key=r['row_ordinal'];pts=r['points'];vertex+=len(pts);parts+=len(r['parts'])
        if not pts:null.append(key);continue
        if any(not math.isfinite(c) for xy in pts for c in xy):nonfinite.append(key);continue
        try:g=shape(r['geo_interface'])
        except Exception as e:bad.append(dict(row=key,reason=str(e)));continue
        if not g.is_valid:bad.append(dict(row=key,reason=explain_validity(g)));continue
        geoms.append(g);validrows.append(key)
    overlaps=[]
    if geoms:
        tree=STRtree(geoms)
        for i,g in enumerate(geoms):
            for j0 in tree.query(g):
                j=int(j0)
                if j<=i:continue
                x=g.intersection(geoms[j]);area=x.area
                if area>0:overlaps.append(dict(rows=[validrows[i],validrows[j]],area=area))
    return dict(rows=len(rows),vertices=vertex,parts=parts,null_geometry_rows=null,nonfinite_rows=nonfinite,
                invalid_rows=bad,valid_rows_checked_for_overlap=len(geoms),positive_area_overlap_pairs=overlaps,
                area_units=units,repair='none; invalid geometries excluded from overlap intersections, preserved unchanged')

def main():
    contract_bytes=(STATE/'data/turnout/priority-set.json').read_bytes()
    assert sha(contract_bytes)=='1f589d2785d985af2eb33de50adad5a398924ab55f9343deaf79ac5c7378d97a' and len(contract_bytes)==2293339
    contract=json.loads(contract_bytes);accept=json.loads((STATE/'data/coordinator-priority-acceptance.json').read_text())
    assert accept['accepted'] and accept['ordered_dispatch_keys']==contract['ordered_priority_keys']
    counties=contract['coverage'];assert len(counties)==159 and sum(len(x['constituents']) for x in counties)==2701
    priority=contract['ordered_priority_keys'];assert len(priority)==44
    (ROOT/'extracts').mkdir(exist_ok=True);(ROOT/'counties').mkdir(exist_ok=True)
    # Original archive, not a geometry-changing export.
    raw=entity('state-2024-precinct-zip');z=zipfile.ZipFile(io.BytesIO(raw));assert z.testzip() is None
    members=[]
    for i in z.infolist():members.append(dict(name=i.filename,bytes=i.file_size,crc32=f'{i.CRC:08x}',sha256=sha(z.read(i.filename))))
    base=next(n[:-4] for n in z.namelist() if n.endswith('.shp'))
    shp=z.read(base+'.shp');shx=z.read(base+'.shx');dbf=z.read(base+'.dbf');prj=z.read(base+'.prj').decode();crs=CRS.from_wkt(prj)
    reader=shapefile.Reader(shp=io.BytesIO(shp),shx=io.BytesIO(shx),dbf=io.BytesIO(dbf))
    assert len(reader)==2724 and (len(shx)-100)//8==2724 and struct.unpack('<I',dbf[4:8])[0]==2724
    rows=[];bycounty=collections.defaultdict(list);attrs=[]
    for ordinal,sr in enumerate(reader.iterShapeRecords()):
        s=sr.shape;attr=sr.record.as_dict()
        r=dict(row_ordinal=ordinal,record_number=ordinal+1,shape_type=s.shapeType,attributes=attr,points=[list(x) for x in s.points],parts=list(s.parts),bbox=list(s.bbox) if hasattr(s,'bbox') else None,
               z=list(s.z) if hasattr(s,'z') else None,m=list(s.m) if hasattr(s,'m') else None,geo_interface=s.__geo_interface__ if s.shapeType else None)
        rows.append(r);bycounty[attr['FIPS']].append(r);attrs.append(dict(row_ordinal=ordinal,**attr))
    assert len([k for k in bycounty if k])==159
    csvwrite(ROOT/'extracts/state2024-all-attributes.csv',attrs)
    dump(ROOT/'extracts/archive-inspection.json',dict(id='state-2024-precinct-zip',members=members,crc_test='pass',shp_records=len(rows),shx_records=(len(shx)-100)//8,dbf_records=struct.unpack('<I',dbf[4:8])[0],shape_type=reader.shapeType,extent=list(reader.bbox),prj_wkt_literal=prj,crs=crs.to_json_dict(),axis_storage='Shapefile XY = longitude,latitude; CRS authority axis order preserved separately',units='degrees',curves='SHP type5 polygon has linear vertices; Z/M absent',blank_fips_rows=[r['row_ordinal'] for r in bycounty['']]))
    writegz(ROOT/'extracts/state2024-unmatched-native-geometry.json.gz',dict(crs_wkt=prj,features=bycounty['']))
    svg(ROOT/'previews/state2024-unmatched.svg',bycounty[''],'27 rows with blank county attributes - unassigned')
    # Preserve every historical source object and source key; no geographic join.
    pins={};contexts=[];nativetable={}
    native_csv=list(csv.DictReader((STATE/'data/turnout/native-units.csv').open()))
    bykey={r['native_key']:r for r in native_csv};assert len(bykey)==2701
    for c in counties:
        source=c['constituents'][0]['source_id'] if c['constituents'] else None
        assert source
        bp=STATE/'data/turnout/source'/f'{source}.body.gz';hp=bp.with_name(f'{source}.http.json')
        b=gzip.decompress(bp.read_bytes());d=json.loads(b);meta=json.loads(hp.read_text())
        pins[str(bp.relative_to(STATE))]=dict(bytes=bp.stat().st_size,sha256=sha(bp.read_bytes()),entity_bytes=len(b),entity_sha256=sha(b))
        pins[str(hp.relative_to(STATE))]=dict(bytes=hp.stat().st_size,sha256=sha(hp.read_bytes()))
        inv={p['id']:(i,p) for i,p in enumerate(d['precincts'])};turn={p['id']:(i,p) for i,p in enumerate(d['voterTurnout'])}
        native=[]
        for x in c['constituents']:
            i,p=inv[x['native_id']];j,t=turn[x['native_id']];row=bykey[x['key']]
            obj=dict(county_key=c['key'],county_fips=c['county_fips'],priority=c['key'] in priority,contract_constituent=x,extracted_native_row=row,
                     original_precinct_object=p,original_precinct_pointer=f'/precincts/{i}',original_turnout_object=t,original_turnout_pointer=f'/voterTurnout/{j}',
                     source_id=source,source_body_path=str(bp.relative_to(STATE)),source_body_entity_sha256=sha(b),
                     county_source_election=d['election'],county_source_jurisdiction=d['jurisdiction'],geographic_join_status='no approved crosswalk; all map rows and result identities remain separate')
            contexts.append(obj);native.append(obj)
        nativetable[c['county_fips']]=native
    b=''.join(json.dumps(o,ensure_ascii=False,separators=(',',':'))+'\n' for o in contexts).encode();(ROOT/'extracts/native-contexts.jsonl.gz').write_bytes(gzip.compress(b,mtime=0))
    dump(ROOT/'historical-source-pins.json',pins)
    local=json.loads((ROOT/'county-research.json').read_text()) if (ROOT/'county-research.json').exists() else {}
    inventory=[];diagnostics={};cards=[]
    for c in counties:
        fips=c['county_fips'];rr=bycounty[fips];rank=priority.index(c['key'])+1 if c['key'] in priority else None
        info=local.get(fips,{})
        entry=dict(county_key=c['key'],county_fips=fips,county_name=c['county_name'],named_four_dispatch_rank=rank,source_native2024_count=len(c['constituents']),state_map2024_fips_rows=len(rr),
                   source_native_keys=[x['key'] for x in c['constituents']],state_map2024_row_ordinals=[r['row_ordinal'] for r in rr],map_crosswalk_status='unapproved; counts/names/IDs do not establish physical equivalence',
                   november2026_approval='No approved reporting crosswalk; documentary status recorded separately',documentary_status=info.get('documentary_status','No acquired election-specific approval evidence'),reference_scope='General Assembly catalog Statewide Voting Precincts (2024), county attribution only where source FIPS is explicit',
                   local_research=info)
        inventory.append(entry)
        if rank:
            assert rr
            writegz(ROOT/f'extracts/{fips}-state2024-native-geometry.json.gz',dict(source_archive='state-2024-precinct-zip',original_crs_wkt=prj,selection=f"source FIPS == '{fips}' only; blank-FIPS rows remain unassigned",features=rr))
            svg(ROOT/f'previews/{fips}-state2024.svg',rr,c['county_name'])
            diagnostics[fips]=geometry_diagnostics(rr,'square degrees (native NAD83 longitude/latitude planar diagnostic; not ground area)')
        # Every county has a native-detail page, including all 763 nonpriority identities.
        nr=''.join('<tr><td>'+html.escape(o['contract_constituent']['native_name'])+'</td><td><code>'+html.escape(o['contract_constituent']['native_id'])+'</code></td><td>'+str(o['contract_constituent']['source_position'])+'</td><td>'+html.escape(o['source_id'])+'</td><td>unreviewed / no approved map join</td></tr>' for o in nativetable[fips])
        mr=''.join('<tr><td>'+str(r['row_ordinal'])+'</td><td>'+html.escape(str(r['attributes']['DISTRICT']))+'</td><td>'+html.escape(str(r['attributes']['PRECINCT_I']))+'</td><td>'+html.escape(str(r['attributes']['PRECINCT_N']))+'</td></tr>' for r in rr)
        links=''.join(f'<li><a href="../{html.escape(x)}">{html.escape(x)}</a></li>' for x in info.get('assets',[]) if (ROOT/x).exists())
        body=f'<h1>{html.escape(c["county_name"])} · {fips}</h1><p><a href="../index.html">Map index</a> · {len(rr)} explicit-FIPS 2024 map rows; {len(c["constituents"])} historical result identities. No approved crosswalk.</p>'
        if rank:body+=f'<img class="map" src="../previews/{fips}-state2024.svg" alt="2024 reference precinct map"><p><a href="../extracts/{fips}-state2024-native-geometry.json.gz">Full native coordinate/attribute extraction (gzip JSON)</a> · <a href="../originals/state-2024-precinct-zip.zip">Original complete statewide ZIP</a></p>'
        body+=f'<p>{html.escape(info.get("finding","Not a deep-inspection priority. 2024 reference only; current map/approval not investigated at county level."))}</p><ul>{links}</ul><h2>Historical reporting identities — separate source scope</h2><p>Full objects, county source IDs/clocks and attributes: <a href="../extracts/native-contexts.jsonl.gz">all 2,701 native contexts</a>. isVirtual:false and source label precinct do not prove physical geometry.</p><table><tr><th>Source name</th><th>Full source GUID</th><th>Breakdown ordinal</th><th>Source</th><th>Map status</th></tr>{nr}</table><h2>Map-native rows — no votes assigned</h2><table><tr><th>Original row ordinal</th><th>DISTRICT</th><th>PRECINCT_I</th><th>PRECINCT_N</th></tr>{mr}</table>'
        (ROOT/f'counties/{fips}.html').write_text(page(c['county_name'],body))
    dump(ROOT/'inventory.json',inventory);csvwrite(ROOT/'inventory.csv',[{k:v for k,v in x.items() if k not in ('source_native_keys','state_map2024_row_ordinals','local_research')} for x in inventory])
    dump(ROOT/'geometry-diagnostics.json',dict(shapely_version=shapely.__version__,geos_version=shapely.geos_version_string,whole_state=geometry_diagnostics(rows,'square degrees (native NAD83 longitude/latitude planar diagnostic; not ground area)'),by_priority_county=diagnostics,
        unassigned_rows=geometry_diagnostics(bycounty[''],'square degrees'),coverage_limit='Intersections test valid shapes within explicit county FIPS, not legal-boundary gaps; no polygon repair or allocation.'))
    # Service capture diagnostics retain full original feature batches, attributes and CRS.
    sv=[]
    for p in sorted((ROOT/'services').glob('*.json')):
        s=json.loads(p.read_text());features=[f for b in s['batches'] for f in json.loads(entity(b)).get('features',[])];geo=[f.get('geometry') for f in features]
        s['geometry_key_count']=sum('geometry' in f for f in features)
        s['null_geometry_count']=sum('geometry' in f and f['geometry'] is None for f in features)
        s['omitted_geometry_count']=sum('geometry' not in f for f in features)
        s['empty_geometry_count']=sum(g is not None and g.get('rings')==[] for g in geo)
        if s.get('status')=='complete' and s['geometry_key_count']!=len(features):s['status']='complete_ids_geometry_unavailable'
        s['geometry_types']=dict(collections.Counter(tuple(sorted(g)) if g else ('null_or_omitted',) for g in geo)) if False else sorted(set(','.join(sorted(g)) if g else 'null_or_omitted' for g in geo))
        s['accepted_physical_or_reporting_crosswalk']=False
        if features:
            meta=json.loads(entity(s['metadata_id']));sr=meta.get('extent',{}).get('spatialReference',{})
            try:
                code=sr.get('latestWkid') or sr.get('wkid');code={102667:2240,102100:3857}.get(code,code)
                ccrs=CRS.from_wkt(sr['wkt']) if sr.get('wkt') else CRS.from_epsg(code)
                s['crs_details']=dict(source_spatial_reference=sr,wkt=ccrs.to_wkt(),projjson=ccrs.to_json_dict(),axis_storage='Literal service x,y sequence; metadata authority axis order retained separately')
                units=ccrs.axis_info[0].unit_name
            except Exception as e:s['crs_details']=dict(source_spatial_reference=sr,error=str(e));units='unknown native coordinate unit'
            writegz(ROOT/f'extracts/{s["id"]}-service-native.json.gz',dict(metadata=meta,capture_index=s,feature_sets=[json.loads(entity(b)) for b in s['batches']]))
            rr=[];unsupported=[]
            for i,f in enumerate(features):
                g=f.get('geometry')
                if g and 'rings' in g:
                    points=[];parts=[]
                    for ring in g['rings']:parts.append(len(points));points+=ring
                    if not points:continue
                    ss=shapefile.Shape(shapeType=5,points=points,parts=parts)
                    rr.append(dict(row_ordinal=f['attributes'][s['oid_field']],attributes=f['attributes'],points=ss.points,parts=ss.parts,geo_interface=ss.__geo_interface__))
                elif g:unsupported.append(dict(oid=f['attributes'][s['oid_field']],geometry_keys=sorted(g)))
            if rr:
                s['geometry_diagnostics']=geometry_diagnostics(rr,f'square {units}; planar native-coordinate diagnostic')
                svg(ROOT/f'previews/{s["id"]}.svg',rr,s['id']+' - local GIS publication','Local GIS publication · full extent · rounded display pixels · no vote allocation')
            s['curve_or_unsupported_geometry_diagnostics']=unsupported
        sv.append(s)
    dump(ROOT/'service-inspection.json',sv)
    order={v['county_key']:v for v in inventory}
    for i,key in enumerate(priority):
        c=order[key];f=c['county_fips'];info=c['local_research'];assets=info.get('assets',[])
        links=' · '.join(f'<a href="{html.escape(x)}">{html.escape(pathlib.Path(x).name)}</a>' for x in assets if (ROOT/x).exists())
        for service in info.get('service_ids',[]):
            x=f'extracts/{service}-service-native.json.gz'
            if (ROOT/x).exists():links+=f' · <a href="{x}">Local GIS full native data</a> · <a href="services/{service}.json">Capture checks</a>'
        thumb=''
        if assets:
            base=pathlib.Path(assets[0]).stem;png=f'qa/{base}-page1.png'
            if (ROOT/png).exists():thumb=f'<details><summary>Local original preview (separate vintage)</summary><a href="{assets[0]}"><img src="{png}" alt="Original PDF first page"></a></details>'
        cards.append(f'<article data-county="{html.escape(c["county_name"].lower())}" id="county-{f}"><span class="rank">{i+1:02}</span><h2>{html.escape(c["county_name"])}</h2><a href="counties/{f}.html"><img src="previews/{f}-state2024.svg" alt="2024 state reference precinct shapes for {html.escape(c["county_name"])}"></a><p>{c["state_map2024_fips_rows"]} map rows · {c["source_native2024_count"]} historical identities</p><p>{html.escape(info.get("finding","2024 reference; current map/approval unavailable."))}</p><p><a href="extracts/{f}-state2024-native-geometry.json.gz" download>Full coordinates + attributes</a> · <a href="originals/state-2024-precinct-zip.zip">Original ZIP</a> · <a href="counties/{f}.html">Native detail</a></p><p class="assets">{links}</p>{thumb}<p class="gap">November 2026 reporting-boundary crosswalk: unestablished. Documentary changes, where found, are described above.</p></article>')
    table=''.join(f'<tr><td>{x["named_four_dispatch_rank"] or "—"}</td><td><a href="counties/{x["county_fips"]}.html">{html.escape(x["county_name"])}</a></td><td>{x["county_fips"]}</td><td>{x["state_map2024_fips_rows"]}</td><td>{x["source_native2024_count"]}</td><td>no approved crosswalk</td></tr>' for x in inventory)
    body='<header><p class="eyebrow">Georgia · downloaded official assets · research snapshot 2026-10-18 UTC</p><h1>Precinct map library</h1><p>44 county cards in the exact named-four dispatch order. All 159 counties and 2,701 historical reporting identities remain visible. These are reference assets; votes have not been assigned to polygons.</p><p><a href="../precinct-maps.md">Research report</a> · <a href="SCHEMA.md">Schema & reproduction</a> · <a href="manifest.json">Artifact manifest</a> · <a href="geometry-diagnostics.json">Geometry diagnostics</a> · <a href="inventory.json">Complete inventory</a></p><p class="notice">2024 statewide original: 2,724 map rows, including 27 with blank county attributes. Those 27 stay unassigned. A map count, label or matching name is not a reporting crosswalk. Current publication and documentary adoption are recorded separately.</p><label>Filter county cards <input id="filter" type="search" placeholder="County name"></label></header><main><div class="cards">'+''.join(cards)+'</div><h2>All 159 counties — full historical native detail</h2><table><tr><th>Dispatch rank</th><th>County</th><th>FIPS</th><th>2024 map rows</th><th>2024 source identities</th><th>Crosswalk</th></tr>'+table+'</table><p><a href="previews/state2024-unmatched.svg">Unassigned map preview</a> · <a href="extracts/state2024-unmatched-native-geometry.json.gz">All 27 original unknown-context geometries</a> · <a href="extracts/state2024-all-attributes.csv">Every map-native row and attribute</a></p></main><script>document.getElementById("filter").addEventListener("input",e=>{document.querySelectorAll("article").forEach(x=>x.hidden=!x.dataset.county.includes(e.target.value.toLowerCase()))})</script>'
    (ROOT/'index.html').write_text(page('Georgia precinct map library',body))
    dump(ROOT/'build-summary.json',dict(counties=159,priority_counties=44,historical_native_identities=2701,priority_native_identities=sum(x['source_native2024_count'] for x in inventory if x['named_four_dispatch_rank']),nonpriority_native_identities=sum(x['source_native2024_count'] for x in inventory if not x['named_four_dispatch_rank']),map_rows=2724,map_explicit_county_rows=len(rows)-len(bycounty['']),map_unassigned_rows=len(bycounty['']),priority_map_rows=sum(x['state_map2024_fips_rows'] for x in inventory if x['named_four_dispatch_rank']),all_priority_have_actual_reference_geometry=True,approved_current_crosswalks=0))
    print((ROOT/'build-summary.json').read_text())

def page(title,body):
    return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(title)+'</title><style>body{font:15px/1.55 system-ui,sans-serif;color:#203745;background:#eef2f5;margin:0;padding:30px}header,main{max-width:1450px;margin:auto}h1{font-size:42px;letter-spacing:-1.4px;margin:8px 0}h2{font-size:21px}a{color:#065b85}p{max-width:100ch}.eyebrow{letter-spacing:.12em;font-size:11px;text-transform:uppercase}.notice{background:#dce9f1;padding:18px;border-left:4px solid #226b8c}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(310px,1fr));gap:20px;margin:25px 0}article{background:white;border:1px solid #d5dfe5;border-radius:9px;padding:20px;position:relative}article[hidden]{display:none}article img{width:100%;aspect-ratio:4/3;object-fit:contain}.rank{float:right;color:#48798f;font-size:24px}.assets{font-size:12px;overflow-wrap:anywhere}.gap{font-size:12px;color:#66542f;background:#fff5de;padding:8px}table{border-collapse:collapse;width:100%;background:white;font-size:13px}th,td{border-bottom:1px solid #d9e1e5;padding:8px;text-align:left;overflow-wrap:anywhere}input{padding:9px;border:1px solid #8ca7b5;border-radius:5px}code{font-size:11px}.map{max-width:100%;width:800px}ul{padding-left:22px}</style>'+body+'</html>'

if __name__=='__main__':main()
