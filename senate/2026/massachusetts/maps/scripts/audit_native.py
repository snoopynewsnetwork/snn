"""Lossless native ArcGIS response checks and linear-only numeric diagnostics."""
from acquire import *
import json,struct,math,collections,inspect
import shapely
from shapely import from_wkb,STRtree

def polygon_wkb(rings):
 # WKB packs observed doubles, preserving values; caller rejects unclosed rings first.
 return struct.pack('<BII',1,3,len(rings))+b''.join(struct.pack('<I',len(r))+b''.join(struct.pack('<dd',*p[:2])for p in r)for r in rings)
def closed(r):return len(r)>=4 and struct.pack('<dd',*r[0][:2])==struct.pack('<dd',*r[-1][:2])
def signed(r):return math.fsum((r[i][0]-r[0][0])*(r[i+1][1]-r[0][1])-(r[i+1][0]-r[0][0])*(r[i][1]-r[0][1])for i in range(len(r)-1))/2

def diagnose(fs):
 rows=[];geoms=[];oids=[];roles=collections.Counter();points=0;bits=hashlib.sha256()
 for f in fs:
  oid=f['attributes']['OBJECTID'];g=f.get('geometry');rct=dict(object_id=oid,attributes=f['attributes'],geometry_keys=list(g)if g else None,diagnostic_status=None,rings=[])
  if not g:rct['diagnostic_status']='null_or_empty';rows.append(rct);continue
  if 'curveRings'in g:rct['diagnostic_status']='truecurves_preserved_not_linearized';rows.append(rct);continue
  rings=g.get('rings',[]);invalid=[];poly=[]
  for i,r in enumerate(rings):
   points+=len(r)
   for p in r:
    for d in p:bits.update(struct.pack('<d',d))
   isclosed=closed(r);finite=all(isinstance(n,(int,float))and math.isfinite(n)for p in r for n in p);area=signed(r)if finite else None
   role='clockwise_exterior'if area is not None and area<0 else 'counterclockwise_hole'if area is not None and area>0 else 'zero_area_unknown';roles[role]+=1
   rr=dict(index=i,vertices=len(r),dimensions=sorted(set(map(len,r))),bit_closed=isclosed,finite=finite,signed_native_area=area,source_orientation_role=role);rct['rings'].append(rr)
   if not isclosed or not finite:invalid.append(i);poly.append(None)
   else:
    try:poly.append(from_wkb(polygon_wkb([r])))
    except Exception as e:poly.append(None);invalid.append(i);rr['parse_error']=str(e)
  if invalid:rct['diagnostic_status']='invalid_or_unclosed_ring_no_repair';rows.append(rct);continue
  ex=[i for i,r in enumerate(rings)if signed(r)<0];holes=[i for i,r in enumerate(rings)if signed(r)>0];assigned={i:[]for i in ex};orphan=[]
  for h in holes:
   contain=[i for i in ex if poly[i].covers(poly[h])]
   if contain:assigned[min(contain,key=lambda i:poly[i].area)].append(h)
   else:orphan.append(h)
  rct['orphan_holes']=orphan;rct['exterior_hole_assignment']=assigned
  if orphan or any(signed(r)==0 for r in rings):rct['diagnostic_status']='orphan_or_zero_area_unknown_no_repair';rows.append(rct);continue
  components=[from_wkb(polygon_wkb([rings[i]]+[rings[h]for h in assigned[i]]))for i in ex]
  wkb=struct.pack('<BII',1,6,len(components))+b''.join(shapely.to_wkb(p,byte_order=1)for p in components)
  geo=from_wkb(wkb);rct.update(diagnostic_status='linear_only',valid=bool(shapely.is_valid(geo)),validity_reason=shapely.is_valid_reason(geo),native_area=geo.area,components=len(components))
  if rct['valid']:geoms.append(geo);oids.append(oid)
  rows.append(rct)
 tree=STRtree(geoms);overlaps=[]
 for i,g in enumerate(geoms):
  for j in tree.query(g):
   if j<=i:continue
   v=g.intersection(geoms[j]);a=v.area
   if a>0:overlaps.append(dict(a=oids[i],b=oids[j],positive_intersection_native_square_meters=a))
 return dict(features=rows,linear_valid_features=len(geoms),ring_roles=dict(roles),vertices=points,all_native_ordinate_double_bits_sha256=bits.hexdigest(),positive_area_pair_diagnostics=overlaps,legal_overlap_sliver_gap_certification=False,operative_outline=None,units='EPSG26986 meters; square meters for areas')
def main():
 out={}
 for prefix in ['wards','subprecinct']:
  a=json.loads((M/(prefix+'-layer0-acquisition.json')).read_bytes());ff=[]
  for x in a['batches']:
   b,r=load(M/x['receipt']);o=json.loads(b);ff+=o['features'];assert len(o['features'])==x['returned_count']
  out[prefix]=diagnose(ff)
 out['parser']=dict(shapely_version=shapely.__version__,GEOS=shapely.geos_version_string,constructor='shapely.from_wkb; manually packed WKB; bitwise closure required before parser; no Polygon/LinearRing constructor',implementation_file=inspect.getfile(from_wkb),constructor_source=inspect.getsource(from_wkb),original_SHP_ZIP_acquired=False,reason='No original ZIP href obtained from accessible source bodies; native services are complete. SHP/SHX/DBF byte audit is not claimed.')
 dump(M/'native-audit.json',out)
 print({p:{k:v for k,v in out[p].items()if k not in ['features','positive_area_pair_diagnostics']}|{'positive_pairs':len(out[p]['positive_area_pair_diagnostics'])}for p in ['wards','subprecinct']})
if __name__=='__main__':main()
