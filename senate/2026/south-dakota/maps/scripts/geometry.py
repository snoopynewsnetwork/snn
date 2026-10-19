"""Audit native binaries before any display/topology adapter; preserve every position.
Requires PyShp 3.1.6, Shapely, pyproj, Pillow for diagnostics/previews only.
No geometry is repaired; curves stay in exact Esri originals and are excluded
from linear topology/preview rather than silently chorded or densified.
"""
from common import *
import io,struct,zipfile,math,inspect,collections,urllib.parse,re
import shapefile,shapely
from pyproj import CRS
from shapely.geometry import Polygon,MultiPolygon,Point
from shapely.validation import explain_validity
from shapely.strtree import STRtree
from bs4 import BeautifulSoup
def area(r):return sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(r,r[1:]))/2
def rings_adapter(rings):
 # Preserve original order/closure; diagnostic adapter only when ring structure is sound.
 if not rings or any(len(r)<4 or r[0][:2]!=r[-1][:2] for r in rings):return None,'empty_or_unclosed_ring_adapter_withheld'
 shells=[(i,r) for i,r in enumerate(rings) if area(r)<0];holes=[(i,r) for i,r in enumerate(rings) if area(r)>=0]
 if not shells:return None,'no_clockwise_shell_or_orphan_hole_adapter_withheld'
 assigned={i:[] for i,r in shells}
 for hi,h in holes:
  containers=[(abs(area(r)),i) for i,r in shells if Polygon(r).covers(Point(h[0][:2]))]
  if not containers:return None,'orphan_hole_adapter_withheld'
  assigned[min(containers)[1]].append(h)
 polys=[Polygon(r,assigned[i]) for i,r in shells]
 return (polys[0] if len(polys)==1 else MultiPolygon(polys)),None
def topology(items,units,scope):
 gs=[];ids=[];bad=[];withheld=[]
 for ident,rings in items:
  g,reason=rings_adapter(rings)
  if reason:withheld.append(dict(id=ident,reason=reason));continue
  if not g.is_valid:bad.append(dict(id=ident,reason=explain_validity(g)));continue
  gs.append(g);ids.append(ident)
 overlaps=[]
 if gs:
  tree=STRtree(gs)
  for i,g in enumerate(gs):
   for j in tree.query(g,predicate='intersects'):
    j=int(j)
    if j<=i:continue
    v=g.intersection(gs[j]).area
    if v>0:overlaps.append(dict(a=ids[i],b=ids[j],intersection_area=v))
 return dict(units=units,scope=scope,valid_linear_geometries_tested=len(gs),invalid_linear_geometries=bad,withheld=withheld,positive_area_overlaps=overlaps,no_legal_gap_or_overlap_certification=True,same_vintage_legal_outline=None)
def svg(path,items,title,subtitle):
 pts=[p for _,rs in items for r in rs for p in r]
 if not pts:return
 xs=[p[0] for p in pts];ys=[p[1] for p in pts];xmin,xmax=min(xs),max(xs);ymin,ymax=min(ys),max(ys)
 scale=min(920/max(xmax-xmin,1e-12),620/max(ymax-ymin,1e-12))
 from html import escape
 out=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 760" role="img"><title>{escape(title)}</title><rect width="1000" height="760" fill="#fff"/><text x="35" y="32" font-family="sans-serif" font-size="22">{escape(title)}</text><text x="35" y="58" font-family="sans-serif" font-size="12">{escape(subtitle)}</text>']
 for i,(ident,rs) in enumerate(items):
  # Rounded display coordinates only; every source position remains in the raw original.
  d=' '.join('M '+' L '.join(f'{40+(p[0]-xmin)*scale:.3f},{700-(p[1]-ymin)*scale:.3f}' for p in r)+' Z' for r in rs)
  out.append(f'<path d="{d}" fill="hsl({(i*47)%360} 40% 84%)" fill-rule="evenodd" stroke="#29364b" stroke-width="0.6"><title>{escape(str(ident))}</title></path>')
 out.append('</svg>');(MAPS/path).write_text('\n'.join(out)+'\n')
def census(e,render=True):
 b=original(e);assert sha(b)=='b48632cb589f4b6c45b5a353fd04e3e9426bbb08503440687960a0498ac06edb'
 z=zipfile.ZipFile(io.BytesIO(b));assert z.testzip() is None
 members=[dict(name=i.filename,bytes=i.file_size,compressed_bytes=i.compress_size,CRC32=f'{i.CRC:08x}',sha256=sha(z.read(i))) for i in z.infolist()]
 def member(ext):return z.read(next(n for n in z.namelist() if n.endswith(ext)))
 shp,shx,dbf=member('.shp'),member('.shx'),member('.dbf')
 assert struct.unpack('>i',shp[24:28])[0]*2==len(shp)
 assert struct.unpack('>i',shx[24:28])[0]*2==len(shx)
 assert shapefile.__version__=='3.1.6'
 # Verify actual constructor semantics, especially parts positional argument vs lines.
 constructor=inspect.getsource(shapefile.Shape.__init__)
 ptest=[(0.,0.),(0.,1.),(1.,0.)];st=shapefile.Shape(shapeType=5,points=ptest,parts=[0]);assert list(st.points)==ptest
 assert 'lines' in str(inspect.signature(shapefile.Shape)) and '_with_polygon_rings_closed(lines)' in constructor
 reader=shapefile.Reader(shp=io.BytesIO(shp),shx=io.BytesIO(shx),dbf=io.BytesIO(dbf),encoding='utf-8')
 count,hlen,rlen=struct.unpack('<IHH',dbf[4:12]);assert count==len(reader)==785
 assert len(dbf) in [hlen+count*rlen,hlen+count*rlen+1]
 fields=[x[0] for x in reader.fields[1:]];records=[];groups=collections.defaultdict(list);positions=0;pos=100
 for i,sr in enumerate(reader.iterShapeRecords()):
  num,words=struct.unpack('>ii',shp[pos:pos+8]);body=shp[pos+8:pos+8+words*2]
  offset,sw=struct.unpack('>ii',shx[100+i*8:108+i*8]);assert offset*2==pos and sw==words and num==i+1
  typ=struct.unpack('<i',body[:4])[0];assert typ==5
  bbox=struct.unpack('<4d',body[4:36]);nparts,npts=struct.unpack('<ii',body[36:44]);parts=list(struct.unpack('<'+'i'*nparts,body[44:44+4*nparts]));xyoff=44+4*nparts
  pts=[struct.unpack('<dd',body[k:k+16]) for k in range(xyoff,xyoff+16*npts,16)]
  assert xyoff+16*npts==len(body);s=sr.shape
  assert s.shapeType==typ and list(s.parts)==parts and list(s.bbox)==list(bbox)
  assert len(s.points)==npts
  # Compare every double bit pattern, preserving repeats, closure, signs and precision.
  for j,p in enumerate(s.points):assert struct.pack('<dd',*p)==body[xyoff+j*16:xyoff+(j+1)*16]
  clone=shapefile.Shape(shapeType=typ,points=list(s.points),parts=list(s.parts))
  assert list(clone.points)==list(s.points) and list(clone.parts)==parts
  rawdbf=dbf[hlen+i*rlen:hlen+(i+1)*rlen];assert rawdbf[0]==32
  attrs=sr.record.as_dict();assert set(attrs)==set(fields)
  # Independently decode each DBF field from original record bytes.
  cur=1
  for descriptor in reader.fields[1:]:
   name,ft,size,decimal=descriptor;raw=rawdbf[cur:cur+size];cur+=size
   val=raw.decode('utf-8').strip().strip('\x00')
   if ft=='C':assert attrs[name]==val,(i,name)
   elif ft in ['F','N']:assert attrs[name]==(float(val) if decimal else int(val)),(i,name)
   else:raise AssertionError(('unhandled DBF type',descriptor))
  assert cur==rlen
  rings=[pts[k:parts[j+1] if j+1<len(parts) else npts] for j,k in enumerate(parts)]
  fips=attrs['STATEFP20']+attrs['COUNTYFP20'];ident=attrs['GEOID20'];groups[fips].append((ident,rings));positions+=npts
  records.append(dict(record=i+1,shape_type=typ,attributes=attrs,offset_bytes=pos,content_bytes=len(body),original_record_sha256=sha(shp[pos:pos+8+words*2]),DBF_record_sha256=sha(rawdbf),parts=parts,positions=npts,XY_bytes_sha256=sha(body[xyoff:]),bbox=bbox,ring_closed=[r[0]==r[-1] for r in rings],consecutive_duplicate_positions=sum(a==b for r in rings for a,b in zip(r,r[1:])),Z=None,M=None))
  pos+=8+words*2
 assert pos==len(shp) and positions==505985 and len(groups)==66
 diagnostics={}
 for f,items in groups.items():
  diagnostics[f]=topology(items,'square angular degrees (native NAD83 geographic XY)','Census 2020 VTD; county subset; no current reporting join')
  if render:svg(f'previews/census-{f}.svg',items,f'{f} | Census 2020 VTD fallback','Historical display only. No reporting-row / physical-precinct / November 2026 crosswalk.')
 return dict(original_id=e['id'],raw_sha256=sha(b),ZIP_members=members,CRS_PRJ=member('.prj').decode(),DBF_fields=reader.fields[1:],feature_count=count,position_count=positions,county_counts={f:len(v) for f,v in sorted(groups.items())},records=records,constructor_version=shapefile.__version__,constructor_signature=re.sub(r'0x[0-9a-fA-F]+','PROCESS_ADDRESS_OMITTED',str(inspect.signature(shapefile.Shape))),constructor_source_sha256=sha(constructor.encode()),all_positions_binary_equal_before_adapter=True,lines_constructor_implicitly_closes_avoided=True,diagnostics=diagnostics)
def arcgis(es,name,render=True):
 ix={e['id']:e for e in es}
 def obj(k):return json.loads(original(ix[name+'-'+k]))
 pre,post=obj('ids-pre'),obj('ids-post');ids=pre['objectIds'];meta=obj('layer-metadata')
 assert pre==post and len(ids)==len(set(ids))==obj('count-pre')['count']==obj('count-post')['count']
 assert original(ix[name+'-layer-metadata'])==original(ix[name+'-metadata-post'])
 fs=[];pages=[]
 for e in es:
  if e['id'].startswith(name+'-native-page'):
   d=json.loads(original(e));q=urllib.parse.parse_qs(urllib.parse.urlsplit(e['url']).query)
   assert not set(k.lower() for k in q)&{'outsr','geometryprecision','quantizationparameters','maxallowableoffset'}
   assert q['returnTrueCurves']==['true'] and q['returnZ']==['true'] and q['returnM']==['true'] and q['outFields']==['*']
   assert 'error' not in d and not d.get('exceededTransferLimit')
   got=[f['attributes'][pre['objectIdFieldName']] for f in d['features']]
   assert len(got)==len(set(got))<=50 and set(got)==set(e['requested_object_ids'])
   pages.append(dict(id=e['id'],requested_ids=e['requested_object_ids'],returned_ids=got,spatialReference=d.get('spatialReference'),all_response_fields=list(d)))
   fs+=d['features']
 assert {f['attributes'][pre['objectIdFieldName']] for f in fs}==set(ids) and len(fs)==len(ids)
 sr=meta['extent']['spatialReference'];crs=CRS.from_wkt(sr['wkt']) if 'wkt' in sr else CRS.from_epsg(sr['latestWkid'])
 assert all(abs(ax.unit_conversion_factor-0.3048006096012192)<1e-12 for ax in crs.axis_info)
 curves=[];linear=[];records=[];null=[];empty=[]
 for f in fs:
  ident=f['attributes'][pre['objectIdFieldName']];g=f.get('geometry')
  rec=dict(id=ident,attributes=f['attributes'],complete_native_feature_semantic_sha256=semantic(f),geometry_keys=list(g) if g else [],Z_M_present_in_positions=sorted({len(v) for v in walk(g) if isinstance(v,list) and v and all(isinstance(x,(int,float)) for x in v)}) if g else [])
  if g is None:null.append(ident)
  elif 'curveRings' in g:curves.append(ident)
  elif not g.get('rings'):empty.append(ident)
  else:linear.append((ident,g['rings']))
  records.append(rec)
 if render:svg(f'previews/{name}-native-linear.svg',linear,name.title()+' | native linear features',f'Display only; {len(curves)} true-curve features omitted visibly from preview, retained unchanged in originals.')
 return dict(feature_count=len(fs),pages=pages,metadata=meta,records=records,true_curve_features=curves,null_geometry=null,empty_geometry=empty,pre_post_metadata_exact=True,pre_post_counts_IDsets_exact=True,source_generalization_unknown=True,diagnostics=topology(linear,'square US survey feet (native projected XY)','Only linear, valid native features; true curves excluded; incomplete pair coverage'),original_native_geometry_unchanged=True,current_reporting_crosswalk_approved=False)
def main():
 es=load('source/reused-receipts.json');c=census(next(e for e in es if e['id']=='census-SD-vtd20-original'))
 b=(json.dumps(c,ensure_ascii=False,indent=2)+'\n').encode();(MAPS/'qa/Census-binary-geometry.json.gz').write_bytes(gzip.compress(b,mtime=0))
 a={name:arcgis(es,name) for name in ['minnehaha','pennington']};dump('qa/native-GIS.json',a)
 print('Census',c['feature_count'],c['position_count'],'GIS',[(k,v['feature_count'],len(v['true_curve_features'])) for k,v in a.items()])
if __name__=='__main__':main()
