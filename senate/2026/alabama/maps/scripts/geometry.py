"""Unrepaired geometry diagnostics and separate native-coordinate SVG previews."""
from html_tools import ROOT,entity
import json,gzip,html,hashlib
from pathlib import Path
from collections import Counter
from shapely.geometry import Polygon,MultiPolygon
from shapely.validation import explain_validity
from shapely.strtree import STRtree
import shapely

def signed(r):return sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(r,r[1:]))/2

def examine(features,units):
 stats=Counter();details=[];geoms=[];indices=[]
 for i,rings in enumerate(features):
  d={'source_index':i,'unclosed_parts':[],'short_parts':[],'duplicate_consecutive_positions':0,'orphan_holes':[],'valid':None};outers=[];holes=[]
  for j,ring in enumerate(rings):
   stats['parts']+=1;stats['positions']+=len(ring)
   d['duplicate_consecutive_positions']+=sum(a==b for a,b in zip(ring,ring[1:]))
   if len(ring)<4:d['short_parts'].append(j)
   if ring and ring[0]!=ring[-1]:d['unclosed_parts'].append(j)
   if len(ring)>=4 and ring[0]==ring[-1]:
    # ESRI polygon shells are clockwise. No constructor is applied to unclosed rings.
    (outers if signed(ring)<0 else holes).append((j,ring))
  if not d['short_parts'] and not d['unclosed_parts'] and outers:
   shells=[Polygon(r) for _,r in outers];assigned=[[] for _ in shells]
   for hj,hr in holes:
    hp=Polygon(hr);candidates=[k for k,p in enumerate(shells) if p.is_valid and hp.is_valid and p.covers(hp)]
    if not candidates:d['orphan_holes'].append(hj)
    else:assigned[min(candidates,key=lambda k:shells[k].area)].append(hr)
   gs=[Polygon(outer,hh) for (_,outer),hh in zip(outers,assigned)];g=gs[0] if len(gs)==1 else MultiPolygon(gs)
   d['valid']=g.is_valid;d['reason']=explain_validity(g);d['empty']=g.is_empty
   if g.is_valid and not g.is_empty:indices.append(i);geoms.append(g)
  elif not rings:d['empty']=True
  details.append(d)
 overlaps=[]
 if geoms:
  tree=STRtree(geoms)
  for i,g in enumerate(geoms):
   for j in tree.query(g):
    j=int(j)
    if j<=i:continue
    area=g.intersection(geoms[j]).area
    if area>0:overlaps.append({'source_indices':[indices[i],indices[j]],'intersection_area_in_native_squared_units':area})
 return {'counts':dict(stats),'features':details,'positive_area_overlaps':overlaps,'coordinate_units':units,'qualification':'Unrepaired diagnostics in source coordinate units, no legal coverage/sliver/gap certification. No buffer, union repair, autoclosure, vote/ballot/registration allocation or result-label join. Invalid/empty/orphan/unclosed raw objects remain in originals.'}

def svg(rings,title,target):
 pts=[p for rr in rings for ring in rr for p in ring]
 if not pts:return
 xmin=min(p[0] for p in pts);xmax=max(p[0] for p in pts);ymin=min(p[1] for p in pts);ymax=max(p[1] for p in pts);w=xmax-xmin;h=ymax-ymin
 paths=[]
 for rr in rings:
  ds=[]
  for ring in rr:
   if ring:ds.append('M'+' L'.join(repr(p[0])+','+repr(-p[1]) for p in ring)+' Z')
  paths.append('<path d="'+' '.join(ds)+'"/>')
 target.parent.mkdir(exist_ok=True)
 target.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="960" height="720" viewBox="'+f'{xmin} {-ymax} {w} {h}'+'"><title>'+html.escape(title)+'</title><g fill="#dae9e8" stroke="#244a55" stroke-width="'+repr(max(w,h)/2000)+'" fill-rule="evenodd">'+''.join(paths)+'</g></svg>')

def main():
 out=[]
 for path in sorted((ROOT/'zip-audit').glob('*.json.gz')):
  x=json.loads(gzip.decompress(path.read_bytes()))
  for ds in x['datasets']:
   rings=[]
   for r in ds['records']:
    pp=r['parts'];points=r['points'];rings.append([points[a:pp[j+1] if j+1<len(pp) else len(points)] for j,a in enumerate(pp)])
   title=ds['shp'];audit=examine(rings,'degrees if confirmed in retained PRJ; see exact CRS WKT');out.append({'original_sha256':x['original_sha256'],'shp':title,'audit':audit,'source_crs_wkt':ds['source_crs_wkt']})
   # One full statewide fallback preview; county full-resolution originals remain in their ZIPs.
   if title.startswith('cb_2020_01_vtd'):svg(rings,'2020 Census cartographic VTD context; source-generalized; no reporting-unit matches',ROOT/'previews/census-2020-vtd-context.svg')
 for layer in json.loads((ROOT/'native-service-captures.json').read_text()):
  rings=[];nonpoly=[];truecurves=[];features=[]
  for p in layer['pages']:
   _,b=entity(p['receipt']);features+=json.loads(b)['features']
  for i,f in enumerate(features):
   g=f.get('geometry')
   if not g:rings.append([])
   elif 'curveRings' in g: truecurves.append(i);rings.append([])
   elif 'rings' in g:rings.append(g['rings'])
   else:nonpoly.append(i);rings.append([])
  out.append({'layer_url':layer['layer_url'],'native_crs':layer['native_spatial_reference'],'nonpolygon_indices':nonpoly,'truecurve_indices':truecurves,'audit':examine(rings,'native layer units; WKID102100/3857 is metres, no geodesic/legal area claim')})
  if layer['metadata_geometry_type']=='esriGeometryPolygon':svg(rings,'Madison source-labelled2026 precinct geometry; current/legal identity unapproved',ROOT/'previews/madison-source-precincts.svg')
 (ROOT/'geometry-diagnostics.json.gz').write_bytes(gzip.compress(json.dumps({'shapely_version':shapely.__version__,'datasets':out},separators=(',',':')).encode(),mtime=0));print('unrepaired geometry datasets',len(out))
if __name__=='__main__':main()
