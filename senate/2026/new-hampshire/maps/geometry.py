#!/usr/bin/env python3
"""Full geometry inventories and diagnostic-only previews. Never repairs source geometry."""
import io,zipfile,json,gzip,struct,math,collections,logging
import shapefile,shapely,pyproj
from shapely.geometry import shape,mapping,Polygon,MultiPolygon
from shapely.ops import transform,unary_union
from shapely.validation import explain_validity
from shapely.strtree import STRtree
from acquire import ROOT,body,sha
logging.getLogger('shapefile').setLevel(logging.ERROR)

def write(p,x):
 b=(json.dumps(x,separators=(',',':'),ensure_ascii=False)+'\n').encode();q=ROOT/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(gzip.compress(b,mtime=0)if str(q).endswith('.gz')else b)

def svg(geom,path,title):
 from html import escape
 if geom.is_empty:return
 minx,miny,maxx,maxy=geom.bounds;s=min(610/max(maxx-minx,1),450/max(maxy-miny,1));pts=[]
 polys=[geom]if geom.geom_type=='Polygon'else list(geom.geoms)
 for poly in polys:
  for ring in [poly.exterior,*poly.interiors]:
   coords=list(ring.coords);pts.append('M'+' L'.join(f'{30+(x-minx)*s:.3f},{500-(y-miny)*s:.3f}'for x,y,*_ in coords)+'Z')
 (ROOT/path).parent.mkdir(parents=True,exist_ok=True)
 (ROOT/path).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 680 550"><rect width="680" height="550" fill="#f6f8fc"/><text x="25" y="28" font-family="sans-serif" font-size="16">{escape(title)}</text><path d="{" ".join(pts)}" fill="#cce4f3" stroke="#23536f" stroke-width="1" fill-rule="evenodd"/><text x="25" y="535" font-family="sans-serif" font-size="12">Reference preview. No legal / November 2026 approval.</text></svg>')

def esri_poly(g):
 assert 'curveRings'not in g,'Curves retained natively; derivative conversion must be separately specified'
 points=[tuple(p[:2])for ring in g['rings']for p in ring];parts=[];n=0
 for ring in g['rings']:parts.append(n);n+=len(ring)
 s=shapefile.Shape(shapeType=5,points=points,parts=parts)
 s.bbox=[min(p[0]for p in s.points),min(p[1]for p in s.points),max(p[0]for p in s.points),max(p[1]for p in s.points)]
 return shape(s.__geo_interface__)

def topology(id,geoms,labels):
 valid=[g.is_valid for g in geoms];items=[]
 for i,g in enumerate(geoms):items.append({'id':labels[i],'type':g.geom_type,'is_valid':valid[i],'reason':explain_validity(g),'bounds':list(g.bounds),'is_empty':g.is_empty,'area_native_square_units':g.area,'parts':len(g.geoms)if hasattr(g,'geoms')else 1,'vertices':sum(len(r.coords)for p in ([g]if g.geom_type=='Polygon'else g.geoms)for r in [p.exterior,*p.interiors])})
 overlaps=[];tree=STRtree(geoms)
 for i,g in enumerate(geoms):
  for j0 in tree.query(g):
   j=int(j0)
   if j<=i or not valid[i]or not valid[j]:continue
   a=g.intersection(geoms[j]).area
   if a>0:overlaps.append({'a':labels[i],'b':labels[j],'area_native_square_units':a})
 holes=None
 if all(valid):
  u=unary_union(geoms);polys=[u]if u.geom_type=='Polygon'else list(u.geoms);holes=[{'bounds':list(Polygon(h).bounds),'area_native_square_units':Polygon(h).area}for p in polys for h in p.interiors]
 return {'dataset':id,'shapely_version':shapely.__version__,'native_crs_note':'Areas and bounds in native CRS; units in dataset metadata','features':items,'invalid_count':sum(not v for v in valid),'positive_area_overlaps':overlaps,'enclosed_union_holes':holes,'limitations':'No geometry repair/snap; overlap checked only between valid features. Enclosed holes are diagnostic spaces, not proven administrative gaps. External state/municipal legal envelope unavailable; all external-edge gap checks unverified.'}

def build():
 z=zipfile.ZipFile(io.BytesIO(body('granit-pbp')));assert z.testzip()is None;members=[];controls={};zipfeatures=[];zipgeoms=[]
 for i in z.infolist():members.append({'member':i.filename,'bytes':i.file_size,'compressed_bytes':i.compress_size,'crc32':f'{i.CRC:08x}','sha256':sha(z.read(i.filename))})
 for stem in ['pbp','pba']:
  shp=z.read(stem+'.shp');shx=z.read(stem+'.shx');dbf=z.read(stem+'.dbf');r=shapefile.Reader(shp=io.BytesIO(shp),shx=io.BytesIO(shx),dbf=io.BytesIO(dbf));n=(len(shx)-100)//8;assert len(shx)==100+8*n;assert len(shp)==2*struct.unpack('>i',shp[24:28])[0];assert len(shx)==2*struct.unpack('>i',shx[24:28])[0];assert n==len(r)==struct.unpack('<I',dbf[4:8])[0]
  headerlen,recordlen=struct.unpack('<HH',dbf[8:12]);deletions=[dbf[headerlen+i*recordlen]for i in range(n)];assert all(v==32 for v in deletions);offsets=[];recs=[]
  for i in range(n):
   off,words=struct.unpack('>ii',shx[100+8*i:108+8*i]);off*=2;recnum,actualwords=struct.unpack('>ii',shp[off:off+8]);assert actualwords==words and recnum==i+1;assert off+8+2*words<=len(shp);s=r.shape(i);a=r.record(i).as_dict();obj={'record_index_zero_based':i,'shp_record_number':recnum,'attributes':a,'shape_type':s.shapeType,'bbox':list(s.bbox),'points':[list(p)for p in s.points],'parts':list(s.parts),'z':list(s.z)if hasattr(s,'z')else None,'m':list(s.m)if hasattr(s,'m')else None,'raw_shp_record_sha256':sha(shp[off:off+8+2*words]),'shp_byte_offset':off,'content_bytes':2*words};recs.append(obj);offsets.append(off)
   if stem=='pbp':
    g=shape(s.__geo_interface__);zipgeoms.append(g);zipfeatures.append({'type':'Feature','id':i,'properties':a,'geometry':mapping(g)})
  assert offsets==sorted(offsets);assert offsets[-1]+8+2*struct.unpack('>i',shp[offsets[-1]+4:offsets[-1]+8])[0]==len(shp)
  write(f'derived/granit-archive-{stem}-native.json.gz',recs)
  controls[stem]={'records':n,'shape_type':r.shapeType,'bbox':list(r.bbox),'parts':sum(len(r.shape(i).parts)for i in range(n)),'vertices':sum(len(r.shape(i).points)for i in range(n)),'shp_shx_offsets_and_record_lengths_verified':True,'dbf_records':n,'dbf_header_bytes':headerlen,'dbf_record_bytes':recordlen,'deleted_records':0,'fields':[list(x)for x in r.fields[1:]],'crs_wkt':z.read(stem+'.prj').decode(),'true_curves':'SHP source stores straight-segment shapes; no source true-curve representation supplied','Z':False,'M':False}
 write('derived/zip-controls.json',{'source':'granit-pbp','zip_crc_all_members_pass':True,'members':members,'native_controls':controls})
 write('derived/granit-archive-polygons.geojson.gz',{'type':'FeatureCollection','name':'GRANIT original native EPSG3437 coordinates; reference only','crs':{'type':'name','properties':{'name':'EPSG:3437'}},'features':zipfeatures})
 topo=[topology('granit-archive',zipgeoms,[f['properties']['NAME']for f in zipfeatures])]
 datasets={'archive':zipfeatures}
 for id in ['granit-live','keene-wards','merrimack-wards','hudson-wards']:
  audit=json.loads((ROOT/'derived'/f'{id}-service-audit.json').read_text());features=[f for b in audit['batches']for f in json.loads(body(b['id']))['features']];geoms=[esri_poly(f['geometry'])for f in features];labels=[f['attributes'].get('name',f['attributes'].get('WARD',f['attributes'].get('Ward',f['attributes'].get('VotingDistrict_Name'))))for f in features];topo.append(topology(id,geoms,labels));fc=[{'type':'Feature','id':f['attributes'][audit['object_id_field']],'properties':f['attributes'],'geometry':mapping(g)}for f,g in zip(features,geoms)];datasets[id]=fc
  write(f'derived/{id}-native.geojson.gz',{'type':'FeatureCollection','name':'Native CRS reference derivative; original responses authoritative','crs':{'type':'name','properties':{'name':'EPSG:'+str(audit['native_crs'].get('latestWkid',audit['native_crs']['wkid']))}},'features':fc})
 write('derived/topology.json',topo)
 c=json.loads((ROOT.parent/'data/turnout/priority-set.json').read_text());towns=[];seen=set();t=pyproj.Transformer.from_crs(3437,4326,always_xy=True)
 for u in c['all_units']:
  k=(u['county_fips'],u['municipal_parent_label'])
  if k in seen:continue
  seen.add(k);a=[f for f in zipfeatures if f['properties']['NAME']==k[1]and f['properties']['COUNTY']==int(k[0][-3:])];b=[f for f in datasets['granit-live']if f['properties']['name']==k[1]and f['properties']['county']==int(k[0][-3:])]
  d={'county_fips':k[0],'source_parent_label':k[1],'match_policy':'Exact literal parent label and explicit source county attribute only; not cross-year legal/electoral equivalence','archive_record_ids':[f['id']for f in a],'live_object_ids':[f['id']for f in b]}
  if a and b and k[1] not in set(json.loads((ROOT/'source/administrative-scope.json').read_text())['labels']):
   assert len(a)==len(b)==1;slug='m-'+k[0]+'-'+str(a[0]['id']);g=shape(b[0]['geometry']);svg(g,'previews/'+slug+'.svg',k[1]+' — municipal parent reference')
   for suffix,fs in [('archive',a),('live',b)]:
    geo=[]
    for f in fs:geo.append({**f,'geometry':mapping(transform(t.transform,shape(f['geometry'])))})
    write(f'derived/municipal/{slug}-{suffix}.geojson',{'type':'FeatureCollection','name':k[1]+' municipal reference; no election-boundary approval','features':geo})
   d.update(preview='previews/'+slug+'.svg',archive_geojson=f'derived/municipal/{slug}-archive.geojson',live_geojson=f'derived/municipal/{slug}-live.geojson',native_vertices=sum(len(r.coords)for p in ([g]if g.geom_type=='Polygon'else g.geoms)for r in [p.exterior,*p.interiors]),current_approval=False)
  towns.append(d)
 # Officially linked ward geometry retained independently, never infer results crosswalk from its 2010 attributes.
 for f in datasets['keene-wards']:
  ward=f['properties']['WARD'];svg(shape(f['geometry']),f"previews/keene-{ward.lower().replace(' ','-')}.svg",'Keene '+ward+' — city-linked reference')
 for id in ['merrimack-wards','hudson-wards']:
  geoms=[shape(f['geometry'])for f in datasets[id]];combined=MultiPolygon([p for g in geoms for p in ([g]if g.geom_type=='Polygon'else g.geoms)]);svg(combined,'previews/'+id+'.svg',id.replace('-',' ')+' — current linked reference')
  for f in datasets[id]:
   lab=f['properties'].get('Ward',f['properties'].get('VotingDistrict_Name'));svg(shape(f['geometry']),'previews/'+id+'-'+str(f['id'])+'.svg',id+' '+str(lab))
 write('derived/municipal-reference-matches.json',towns)
 print('ZIP',controls['pbp']['records'],'polygons',controls['pba']['records'],'lines; nativeparts/vertices',controls['pbp']['parts'],controls['pbp']['vertices']);print('Topology',[(x['dataset'],x['invalid_count'],len(x['positive_area_overlaps']),None if x['enclosed_union_holes']is None else len(x['enclosed_union_holes']))for x in topo]);print('explicit parent matches',sum(bool(t['archive_record_ids'])for t in towns),'of',len(towns))
if __name__=='__main__':build()
