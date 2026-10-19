#!/usr/bin/env python3
"""Offline diagnostic/preview reader. Never repairs or rewrites native originals."""
import collections,colorsys,gzip,html,io,json,logging,math,struct,zipfile
import shapefile,shapely,pyproj
from shapely.geometry import shape
from shapely.validation import explain_validity
from acquire import ROOT,STATE,body,sha,savejson
logging.getLogger('shapefile').setLevel(logging.ERROR)

def rings_to_shape(rings):
    # PyShp3 validates nonempty polygons in __init__. Passing points/parts at
    # construction also avoids lines=, which auto-closes rings in this API.
    points=[p[:2] for r in rings for p in r];parts=[];n=0
    for r in rings:parts.append(n);n+=len(r)
    assert all(len(r)>=4 and r[0]==r[-1] for r in rings), 'Native open/short ring: no implicit closure permitted'
    s=shapefile.Shape(shapeType=5,points=points,parts=parts)
    interface=s.__geo_interface__
    output_rings=interface['coordinates'] if interface['type']=='Polygon' else [r for p in interface['coordinates'] for r in p]
    normalized=lambda rr: collections.Counter(tuple(tuple(p[:2]) for p in r) for r in rr)
    exact=normalized(rings)==normalized(output_rings)
    assert s.points==points and list(s.parts)==parts and exact, 'Adapter changed/dropped original XY rings'
    proof=dict(input_rings=len(rings),output_rings=len(output_rings),input_xy_positions=len(points),output_xy_positions=sum(map(len,output_rings)),all_full_xy_rings_exact=exact,constructor_points_parts_unchanged=True,ring_role_errors=dict(s._errors))
    # PyShp's orphan-hole fallback changes a ring's interpreted role. Retain
    # that diagnostic but do not silently adopt the fallback as source truth.
    if s._errors:return None,proof
    return shape(interface),proof

def audit_features(features,units):
    records=[];gs=[];dups=collections.defaultdict(list);labels=collections.defaultdict(list)
    for i,f in enumerate(features):
        rings=f['rings'];pts=[p for r in rings for p in r]
        def numbers(v):
            if isinstance(v,(int,float)):yield v
            elif isinstance(v,dict):
                for x in v.values():yield from numbers(x)
            elif isinstance(v,list):
                for x in v:yield from numbers(x)
        finite=all(math.isfinite(v) for v in numbers(f.get('native_geometry',rings)))
        rec=dict(source_record=i,source_id=f['id'],attributes=f['attributes'],parts=len(rings),positions=len(pts),
          coordinate_dimension_counts=dict(collections.Counter(map(len,pts))),closed_rings=None if f.get('curves') else all(len(r)>0 and r[0]==r[-1] for r in rings),
          short_ring_indices=[j for j,r in enumerate(rings) if len(r)<4],finite=finite,empty=not bool(pts) and not f.get('curves',False),geometry_null=f.get('geometry_null',False),
          raw_geometry_sha256=f['raw_geometry_sha256'],curve_geometry=f.get('curves',False))
        try:
            g,adapter=(rings_to_shape(rings) if rings and finite and not f.get('curves') else (None,None))
            rec.update(adapter=adapter,valid=g.is_valid if g is not None else None,validity=explain_validity(g) if g is not None else ('Unavailable: source ring-role anomaly; no orphan-hole reinterpretation' if adapter else 'Not topologically evaluated: empty/nonfinite/true curves'),area=g.area if g is not None else None)
        except Exception as e:g=None;rec.update(valid=None,validity=str(e),area=None)
        gs.append(g)
        if g is not None:dups[sha(g.wkb)].append(i)
        label=next((f['attributes'][k] for k in ['PRECINCT','NAME20','DistName','NAME','Name'] if k in f['attributes']),None)
        if label is not None:labels[str(label)].append(i)
        records.append(rec)
    overlaps=[];skipped=[]
    good=[i for i,g in enumerate(gs) if g is not None and g.is_valid and not g.is_empty]
    tree=shapely.STRtree([gs[i] for i in good])
    for q,i in enumerate(good):
        for other in tree.query(gs[i]):
            j=good[int(other)]
            if j<=i:continue
            a=gs[i].intersection(gs[j]).area
            if a>0:overlaps.append(dict(records=[i,j],area=a))
    return dict(feature_count=len(features),units=units,area_units=units+' squared',features=records,
      topology_evaluated=sum(r.get('valid') is not None for r in records),topology_unavailable=[r['source_record'] for r in records if r.get('valid') is None],
      invalid=[r['source_record'] for r in records if r.get('valid') is False],empty=[r['source_record'] for r in records if r['empty']],
      nonfinite=[r['source_record'] for r in records if not r['finite']],curves=[r['source_record'] for r in records if r['curve_geometry']],
      duplicate_geometry_records=[v for v in dups.values() if len(v)>1],duplicate_literal_labels={k:v for k,v in labels.items() if len(v)>1},
      pairwise_positive_area_intersections=overlaps,intersection_skipped_records=[i for i in range(len(gs)) if i not in good],
      gap_review='Unknown: no certified same-vintage county outline. Positive areas are exact GEOS diagnostics without sliver tolerance, not certified legal overlaps. Invalid/curve/nonfinite records omitted from intersection math only, retained in originals and feature inventory.')

def svg(key,features,title):
    pts=[p for f in features for r in f['rings'] for p in r if len(p)>=2 and math.isfinite(p[0]) and math.isfinite(p[1])]
    if not pts:return None
    xs,ys=zip(*[(p[0],p[1]) for p in pts]);x0,y0,x1,y1=min(xs),min(ys),max(xs),max(ys);scale=min(920/(x1-x0),610/(y1-y0));ox=(1000-(x1-x0)*scale)/2;oy=80+(650-(y1-y0)*scale)/2
    out=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 800" role="img">',f'<title>{html.escape(title)}</title>','<rect width="1000" height="800" fill="#f6f4ee"/>',f'<text x="32" y="34" font-family="sans-serif" font-size="22">{html.escape(title)}</text>','<text x="32" y="61" font-family="sans-serif" font-size="14">Shared map reference; source units are not joined to SEMS columns</text>']
    for i,f in enumerate(features):
        commands=[]
        for r in f['rings']:
            if not r:continue
            commands.append('M'+' L'.join(f'{ox+(p[0]-x0)*scale:.2f},{oy+(y1-p[1])*scale:.2f}' for p in r)+' Z')
        rgb=colorsys.hls_to_rgb(((i*137)%360)/360,.78,.38);color='#'+''.join(f'{round(v*255):02x}' for v in rgb)
        out.append(f'<path d="{" ".join(commands)}" fill="{color}" stroke="#3d5459" stroke-width="0.6" fill-rule="evenodd"><title>Source record {i}</title></path>')
    skipped=sum(bool(f.get('curves')) or not bool(f['rings']) for f in features)
    out+=[f'<text x="32" y="744" font-family="sans-serif" font-size="14">{skipped} curve/empty records omitted from drawing; retained unchanged in source inventory.</text>','<text x="32" y="766" font-family="sans-serif" font-size="14">Display coordinates rounded only in this preview. Originals retain complete native precision.</text>','<text x="32" y="787" font-family="sans-serif" font-size="14">No November approval, certified county outline, legal gap finding or vote allocation.</text>','</svg>']
    path=ROOT/'previews'/f'{key}.svg';path.write_text('\n'.join(out)+'\n');return str(path.relative_to(STATE))

def archive(rec):
    raw=body(rec);z=zipfile.ZipFile(io.BytesIO(raw));assert z.testzip() is None
    members=[]
    for n in z.namelist():
        b=z.read(n);members.append(dict(name=n,bytes=len(b),sha256=sha(b),crc32=f'{z.getinfo(n).CRC:08x}',first16_hex=b[:16].hex()))
    shp=next(n for n in z.namelist() if n.lower().endswith('.shp'));stem=shp[:-4];sb=z.read(shp);xb=z.read(stem+'.shx');db=z.read(stem+'.dbf');prj=z.read(stem+'.prj').decode();crs=pyproj.CRS.from_wkt(prj);units=crs.axis_info[0].unit_name
    assert struct.unpack('>i',sb[:4])[0]==9994 and struct.unpack('<i',sb[28:32])[0]==1000
    assert struct.unpack('>i',sb[24:28])[0]*2==len(sb)
    assert struct.unpack('>i',xb[:4])[0]==9994 and struct.unpack('>i',xb[24:28])[0]*2==len(xb)
    offsets=[];pos=100
    while pos<len(sb):
        num,length=struct.unpack('>ii',sb[pos:pos+8]);offsets.append(dict(record_number=num,byte_offset=pos,content_bytes=length*2));pos+=8+length*2
    assert pos==len(sb)
    shx=[struct.unpack('>ii',xb[i:i+8]) for i in range(100,len(xb),8)]
    assert [(p['byte_offset']//2,p['content_bytes']//2) for p in offsets]==shx
    ndb=struct.unpack('<I',db[4:8])[0];hlen,rlen=struct.unpack('<HH',db[8:12]);assert len(offsets)==ndb==len(shx)
    assert len(db) in [hlen+ndb*rlen,hlen+ndb*rlen+1]
    deleted=[i for i in range(ndb) if db[hlen+i*rlen:hlen+i*rlen+1]==b'*']
    cp=z.read(stem+'.cpg').decode().strip() if stem+'.cpg' in z.namelist() else 'utf-8'
    encoding={'65001':'utf-8','1252':'cp1252'}.get(cp,cp)
    rd=shapefile.Reader(shp=io.BytesIO(sb),shx=io.BytesIO(xb),dbf=io.BytesIO(db),encoding=encoding)
    fs=[]
    for i,s in enumerate(rd.shapes()):
        ends=list(s.parts)[1:]+[len(s.points)];rings=[list(map(list,s.points[a:b])) for a,b in zip(s.parts,ends)]
        attrs=rd.record(i).as_dict() if i not in deleted else {'__deleted_DBF_record__':True}
        off=offsets[i];fs.append(dict(id=i,attributes=attrs,rings=rings,raw_geometry_sha256=sha(sb[off['byte_offset']+8:off['byte_offset']+8+off['content_bytes']])))
    return dict(source_id=rec['id'],archive_sha256=sha(raw),zip_crc_pass=True,members=members,
      shapefile=dict(shape_type=rd.shapeType,shp_magic=9994,version=1000,shp_bytes=len(sb),shx_bytes=len(xb),dbf_bytes=len(db),dbf_header_records=ndb,dbf_record_length=rlen,dbf_header_length=hlen,deleted_dbf_records=deleted,record_offsets=offsets,shx_offsets_equal=True,dbf_shape_index_counts_equal=True,fields=[list(f) for f in rd.fields],codepage=cp,crs_wkt=prj,crs_authority=crs.to_authority(),units=units),
      diagnostics=audit_features(fs,units)),fs

def build():
    shared=json.loads((ROOT/'shared-map-references.json').read_text())['sources'];receipts=[json.loads(p.read_text()) for p in (ROOT/'source').glob('*.receipt.json')];audits=[];previews={};county_fallback={}
    for r in shared:
        if r.get('status')==200 and r['requested_url'].endswith('.zip'):
            a,fs=archive(r);audits.append(a)
            if r['id']=='maris-2020-precinct-zip':
                for f in fs:county_fallback.setdefault(f['attributes']['STATEFP20']+f['attributes']['COUNTYFP20'],[]).append(f)
                for fips,features in county_fallback.items():previews[f'vtd2020-{fips}']=svg(f'vtd2020-{fips}',features,f'{fips} | MARIS / Census 2020 VTD | {len(features)} features')
            else:previews[r['id']]=svg(r['id'],fs,r['id']+f' | {len(fs)} features | 2023 label')
    for key in ['desoto-native','harrison-native']:
        proof=json.loads((ROOT/f'source/{key}.service-proof.json').read_text());fs=[];metadata=json.loads(body(next(r for r in receipts if r['id']==key+'-pre')))
        for batch in proof['batches']:
            response=json.loads(body(next(r for r in receipts if r['id']==batch['id'])))
            for f in response['features']:
                g=f.get('geometry') or {};fs.append(dict(id=f['attributes'].get(metadata.get('objectIdField','OBJECTID'),f['attributes'].get('FID')),attributes=f['attributes'],rings=g.get('rings',[]),native_geometry=g,geometry_null=f.get('geometry') is None,curves='curveRings' in g,raw_geometry_sha256=sha(json.dumps(g,separators=(',',':'),ensure_ascii=False).encode())))
        sr=proof['native_spatial_reference'];units=pyproj.CRS.from_epsg(sr.get('latestWkid',sr['wkid'])).axis_info[0].unit_name
        audit=dict(source_id=key,service_proof=proof,diagnostics=audit_features(fs,units));audits.append(audit);previews[key]=svg(key,fs,key+f' | {len(fs)} source features | vintage unapproved')
    web=json.loads(body(next(r for r in receipts if r['id']=='lamar-webmap')))
    layer=next(l for l in web['operationalLayers'] if l['title']=='Voting_Precints')['featureCollection']['layers'][0];fs=[]
    for f in layer['featureSet']['features']:
        g=f.get('geometry') or {};fs.append(dict(id=f['attributes']['OBJECTID'],attributes=f['attributes'],rings=g.get('rings',[]),native_geometry=g,geometry_null=f.get('geometry') is None,curves='curveRings' in g,raw_geometry_sha256=sha(json.dumps(g,separators=(',',':')).encode())))
    a=dict(source_id='lamar-webmap-collection',json_pointer='/operationalLayers/'+str(next(i for i,l in enumerate(web['operationalLayers']) if l['title']=='Voting_Precints'))+'/featureCollection/layers/0',spatialReference=layer['featureSet'].get('spatialReference'),diagnostics=audit_features(fs,'metre'),qualification='Complete embedded collection as published, not a service query: original underlying shapefile/precision/generalization history unavailable. No independent service source count or edit clock.');audits.append(a);previews[a['source_id']]=svg(a['source_id'],fs,'Lamar county-linked embedded collection | 25 source features')
    savejson(ROOT/'geometry-audit.json',dict(schema='native-geometry-audit-v2-constructor-adapter',pyshp=shapefile.__version__,shapely=shapely.__version__,GEOS=shapely.geos_version_string,pyproj=pyproj.__version__,archives_and_native_sources=audits,previews=previews,
      adapter_basis='Polygon constructed with complete original XY points/parts; no implicit closure. Every original ring/position retained exactly with multiplicity; Esri shell/hole organization checked. Orphan-hole fallback not accepted as source geometry. Z/M remain in original native bytes and are not used in planar XY topology.',
      superseded_failure_history='maps/history/adapter-failure-v1/snapshot.json',
      unchanged_originals=True,coordinate_preservation='ZIP bytes and complete native JSON responses are canonical. Display derivatives may round; no source repair/simplification/normalization.',county_fallback_feature_counts={k:len(v) for k,v in county_fallback.items()}))
    print('geometry audits',len(audits),'previews',len(previews))

if __name__=='__main__':build()
