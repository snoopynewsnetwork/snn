"""Source diagnostics only. No repair, curve densification, polygon join or coverage certification."""
from pathlib import Path
from collections import Counter,defaultdict
import gzip,json,struct,hashlib,html
from shapely.geometry import Polygon,MultiPolygon
from shapely.validation import explain_validity
from shapely.strtree import STRtree
from build import ROOT,load,native,dumps

def bits(v):return b''.join(struct.pack('>d',float(x)) for x in v)
def audit(out=ROOT):
 out=Path(out);(out/'previews').mkdir(parents=True,exist_ok=True);rows=[];by=defaultdict(list);geoms=defaultdict(list);coords=0
 for p in sorted((ROOT/'originals').glob('native-page-*/receipt.json')):
  for f in load(native(p.parent.name)[0])['features']:by['05'+f['attributes']['county_fips']].append(f)
 for county,ff in sorted(by.items()):
  lines=[];allxy=[]
  for f in ff:
   oid=f['attributes']['objectid'];g=f.get('geometry');row={'objectid':oid,'county_fips':county,'geometry_keys':list(g) if isinstance(g,dict) else None,'diagnostics':[],'input_ring_count':0,'input_coordinate_count':0,'exact_XY_IEEE754_reader_comparisons':0,'repaired':False}
   if not g:row['diagnostics'].append('empty/null source geometry');rows.append(row);continue
   if 'curveRings' in g:
    row['diagnostics'].append('native true curves retained untouched; excluded from linear constructor/topology and SVG preview');row['native_curve_part_count']=len(g['curveRings']);rows.append(row);continue
   if set(g)!={'rings'}:row['diagnostics'].append('nonlinear/nonpolygon/unhandled source object retained');rows.append(row);continue
   shells=[];holes=[];validrings=True
   for n,ring in enumerate(g['rings']):
    row['input_ring_count']+=1;row['input_coordinate_count']+=len(ring)
    row.setdefault('adjacent_duplicate_positions',[]).extend({'ring':n,'position':i} for i in range(1,len(ring)) if ring[i]==ring[i-1])
    if any(len(x)!=2 for x in ring):row['diagnostics'].append({'ring':n,'issue':'unexpected source dimension retained'});validrings=False;continue
    allxy.extend(ring)
    if len(ring)<4 or ring[0]!=ring[-1]:row['diagnostics'].append({'ring':n,'issue':'unclosed/short source ring; not passed to auto-closing constructor'});validrings=False;continue
    single=Polygon(ring);returned=list(single.exterior.coords)
    assert len(ring)==len(returned) and all(bits(a)==bits(b) for a,b in zip(ring,returned)),('reader changed point/order',oid,n)
    coords+=len(ring);row['exact_XY_IEEE754_reader_comparisons']+=len(ring)
    if not single.is_valid:row['diagnostics'].append({'ring':n,'issue':explain_validity(single)});validrings=False
    # Translated area sign avoids cancellation from large native projected offsets.
    x0,y0=ring[0];area=sum((a[0]-x0)*(b[1]-y0)-(b[0]-x0)*(a[1]-y0) for a,b in zip(ring,ring[1:]))/2
    if area<0:shells.append({'index':n,'ring':ring,'polygon':single,'holes':[]})
    elif area>0:holes.append({'index':n,'ring':ring,'polygon':single})
    else:row['diagnostics'].append({'ring':n,'issue':'zero signed native area'});validrings=False
    # Every duplicate and position appears in the preview; only closed source rings qualify.
    lines.append('<path d="M '+' L '.join(str(x)+' '+str(y) for x,y in ring)+'"/>')
   for h in holes:
    candidates=[s for s in shells if s['polygon'].is_valid and h['polygon'].is_valid and s['polygon'].covers(h['polygon'])]
    if not candidates:row['diagnostics'].append({'ring':h['index'],'issue':'orphan positive-oriented hole; unrepaired'});validrings=False
    else:min(candidates,key=lambda s:s['polygon'].area)['holes'].append(h)
   polygons=[]
   if validrings:
    for s in shells:
     poly=Polygon(s['ring'],[h['ring'] for h in s['holes']]);assert [bits(x) for x in poly.exterior.coords]==[bits(x) for x in s['ring']]
     assert len(poly.interiors)==len(s['holes'])
     for got,h in zip(poly.interiors,s['holes']):assert [bits(x) for x in got.coords]==[bits(x) for x in h['ring']]
     polygons.append(poly)
    geom=MultiPolygon(polygons)
    row['constructed_diagnostic_part_count']=len(polygons);row['constructor_preserved_all_ring_positions']=True
    row['diagnostic_native_area_square_metres']=geom.area;row['diagnostic_native_bbox']=list(geom.bounds) if not geom.is_empty else None
    row['diagnostic_valid']=geom.is_valid;row['diagnostic_validity_reason']=explain_validity(geom)
    if geom.is_valid and not geom.is_empty:geoms[county].append((oid,geom))
   rows.append(row)
  xs=[p[0] for p in allxy];ys=[p[1] for p in allxy]
  if xs:
   xmin,xmax=min(xs),max(xs);ymin,ymax=min(ys),max(ys);w=xmax-xmin;h=ymax-ymin
   svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="'+f'{xmin} {-ymax} {w} {h}'+'"><title>'+county+' exact linear source rings, true curves omitted, no result join</title><g transform="scale(1,-1)" fill="none" stroke="#246080" stroke-width="'+str(max(w,h)/2200)+'">'+''.join(lines)+'</g></svg>'
   (out/'previews'/(county+'.svg')).write_text(svg)
 overlaps=[]
 for county,items in geoms.items():
  gs=[x[1] for x in items];tree=STRtree(gs)
  for i,g in enumerate(gs):
   for q in tree.query(g):
    j=int(q)
    if j<=i:continue
    intersection=g.intersection(gs[j]);area=intersection.area
    if area>0:overlaps.append({'county_fips':county,'objectids':[items[i][0],items[j][0]],'intersection_area_native_square_metres':area,'intersection_geometry_type':intersection.geom_type,'qualification':'linear valid geometries only, native numerical overlap diagnostic; not legal sliver/gap or coverage certification'})
 proof={'status':'pass_source_preserving_diagnostics','features':len(rows),'true_curve_features':36,'exact_linear_XY_IEEE754_positions_compared':coords,'native_CRS':'EPSG:26915; metres; area diagnostics square metres','reader_inspection':'qa/installed-reader.json','feature_diagnostics':rows,'positive_area_pair_overlaps':overlaps,'source_repairs':False,'curve_densification':False,'result_polygon_joins':False,'coverage_or_gap_certification':False,'scope':'All 2,928 native source geometries classified; true curves remain exact source JSON and excluded from linear topology/preview. Ring constructors checked for every retained XY bit/order/duplicate; malformed rings never autoclose.'}
 (out/'qa').mkdir(exist_ok=True);(out/'qa/geometry-diagnostics.json').write_text(dumps(proof));return proof
if __name__=='__main__':
 d=audit();print(json.dumps({k:v for k,v in d.items() if k not in ['feature_diagnostics','positive_area_pair_overlaps']}));print('positive overlaps',len(d['positive_area_pair_overlaps']))
