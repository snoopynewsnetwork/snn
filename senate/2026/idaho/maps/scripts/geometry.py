#!/usr/bin/env python3
"""Native topology diagnostics and separate display derivatives; never repairs source."""
import collections,json,sys,html
from pathlib import Path
import shapely
from shapely.geometry import Polygon,MultiPolygon
from shapely.strtree import STRtree
from shapely.validation import explain_validity
from PIL import Image,ImageDraw,ImageFont
from native import verify,MAPS,ROOT

def area(r):return sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(r,r[1:]))/2

def adapt(f):
 g=f.get('geometry');reason=[]
 if not g:return None,['null_or_empty_geometry']
 if 'curveRings' in g:return None,['true_curves_explicitly_excluded_from_linear_topology']
 if set(g)!={'rings'}:return None,['unhandled_geometry_members_retained']
 rs=g['rings']
 if any(len(r)<4 or r[0]!=r[-1] for r in rs):return None,['open_or_short_rings_retained_unclosed']
 shells=[r for r in rs if area(r)<0];holes=[r for r in rs if area(r)>=0]
 if not shells:return None,['no_clockwise_shell_retained']
 ps=[Polygon(r) for r in shells];assigned=[[] for _ in shells]
 for r in holes:
  hp=Polygon(r);matches=[i for i,p in enumerate(ps) if p.covers(hp)]
  if not matches:return None,['orphan_or_crossing_hole_retained']
  i=min(matches,key=lambda i:ps[i].area);assigned[i].append(r)
 parts=[Polygon(r,hs) for r,hs in zip(shells,assigned)]
 for original,p,hs in zip(shells,parts,assigned):
  assert list(map(list,p.exterior.coords))==original
  assert [list(map(list,h.coords)) for h in p.interiors]==hs
 out=parts[0] if len(parts)==1 else MultiPolygon(parts)
 return out,reason

def diagnose(features):
 ds=[];usable=[];indices=[]
 for f in features:
  geom,reasons=adapt(f);a=f['attributes'];d=dict(object_id=a['OBJECTID'],county=a['COUNTY'],native_name=a['PCNCT_NME'],adaptation_exclusions=reasons)
  if geom is not None:
   d.update(is_valid=bool(geom.is_valid),is_empty=bool(geom.is_empty),validity=explain_validity(geom),native_area_units_squared=geom.area,bounds=list(geom.bounds))
   if geom.is_valid and not geom.is_empty:usable.append(geom);indices.append(a['OBJECTID'])
  ds.append(d)
 tree=STRtree(usable);pairs=[];errors=[]
 for i,p in enumerate(usable):
  for j in tree.query(p,predicate='intersects'):
   j=int(j)
   if j<=i:continue
   try:
    overlap=p.intersection(usable[j]);a=overlap.area
    if a>0:pairs.append(dict(object_ids=[indices[i],indices[j]],intersection_area_native_units_squared=a))
   except Exception as e:errors.append(dict(object_ids=[indices[i],indices[j]],error=repr(e)))
 return dict(status='source_geometry_diagnostics_only',engine='shapely '+shapely.__version__,native_crs='ESRI:102605 / EPSG:8826',native_area_units='square metre (CRS axis units checked independently with pyproj)',source_repair=False,same_vintage_legal_outline=None,legal_gap_overlap_sliver_claim=False,linear_adapter='Esri clockwise shells; counterclockwise holes assigned by full covers to smallest containing shell; every exterior/interior double and position order checked; invalid or excluded geometries remain in raw sources and previews',features=ds,linear_excluded=sum(bool(d['adaptation_exclusions']) for d in ds),invalid=sum(d.get('is_valid') is False for d in ds),valid_nonempty=len(usable),positive_area_pairs=pairs,intersection_errors=errors)

def previews(features):
 groups=collections.defaultdict(list)
 for f in features:groups[f['attributes']['COUNTY']].append(f)
 c=json.loads((ROOT/'data/turnout/priority-set.json').read_text());byname={p['county'].removesuffix(' County'):p['key'] for p in c['all_county_constituents']}
 cards=[];counts=[]
 font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',20)
 for name,fs in sorted(groups.items(),key=lambda x:byname[x[0]]):
  k=byname[name];rings=[r for f in fs for r in f['geometry']['rings']];pts=[p for r in rings for p in r];xs=[p[0] for p in pts];ys=[p[1] for p in pts];xmin,xmax=min(xs),max(xs);ymin,ymax=min(ys),max(ys);w=xmax-xmin;h=ymax-ymin
  pad=max(w,h)*.02;sv=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{xmin-pad} {-ymax-pad} {w+2*pad} {h+2*pad}" role="img"><title>{html.escape(name)} public native-layer geometry, no vote join</title><g transform="scale(1,-1)" fill="#dbe8ed" stroke="#23485b" stroke-width="{max(w,h)/1800}">']
  im=Image.new('RGB',(1200,900),'#ffffff');dr=ImageDraw.Draw(im);scale=min(1160/w,820/h);dx=(1200-w*scale)/2;dy=50+(820-h*scale)/2
  for f in fs:
   a=f['attributes'];paths=[]
   for ring in f['geometry']['rings']:
    paths.append('M'+' L'.join(repr(p[0])+','+repr(p[1]) for p in ring)+' Z')
   sv.append('<path fill-rule="evenodd" d="'+' '.join(paths)+'"><title>'+html.escape(json.dumps(a,ensure_ascii=False))+'</title></path>')
   for ring in f['geometry']['rings']:
    scaled=[(dx+(p[0]-xmin)*scale,dy+(ymax-p[1])*scale) for p in ring]
    dr.polygon(scaled,fill='#dbe8ed' if area(ring)<0 else 'white',outline='#23485b')
  sv.append('</g></svg>');out=('\n'.join(sv)+'\n').encode();assert len(out)<40000000;(MAPS/'previews'/f'{k}.svg').write_bytes(out)
  dr.text((20,10),f'{name}: {len(fs)} native map features | no historical/current join',fill='#15364a',font=font);im.save(MAPS/'previews'/f'{k}.png')
  card=im.copy();card.thumbnail((300,225));cards.append(card);counts.append(dict(county=name,key=k,features=len(fs),rings=len(rings),original_positions=len(pts),svg_bytes=len(out),svg=f'previews/{k}.svg',png=f'previews/{k}.png'))
 sheet=Image.new('RGB',(1500,9*225),'#edf1f3')
 for i,card in enumerate(cards):sheet.paste(card,((i%5)*300,(i//5)*225))
 sheet.save(MAPS/'previews/native-contact-sheet.png')
 return counts
if __name__=='__main__':
 fs,_=verify();qa=diagnose(fs);(MAPS/'qa/topology.json').write_text(json.dumps(qa,indent=2)+'\n');p=previews(fs);(MAPS/'qa/native-preview-render.json').write_text(json.dumps(dict(rendered_scope='all 976 features, all 1032 rings, all 749523 positions; every county PNG/SVG rendered; actual human/agent viewed scope recorded separately',previews=p),indent=2)+'\n');print(json.dumps(dict(invalid=qa['invalid'],linear_excluded=qa['linear_excluded'],overlap_pairs=len(qa['positive_area_pairs']),previews=len(p))))
