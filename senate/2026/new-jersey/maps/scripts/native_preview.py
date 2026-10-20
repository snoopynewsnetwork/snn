from acquire import *
from PIL import Image,ImageDraw
from collections import Counter,defaultdict
import math,struct

def geometry_diagnostics(g):
 if g is None:return {'case':'null'}
 if 'curveRings' in g:return {'case':'curveRings','raw_curve_parts':len(g['curveRings']),'linear_certification':False}
 if 'rings' not in g:return {'case':'other-native-geometry','keys':list(g)}
 rings=g['rings'];pts=[p for r in rings for p in r];d={'case':'empty' if not pts else 'linear-rings','parts':len(rings),'points':len(pts),'unclosed_rings':sum(bool(r) and r[0]!=r[-1] for r in rings),'short_rings':sum(len(r)<4 for r in rings),'empty_rings':sum(not r for r in rings),'coordinate_dimensions':dict(Counter(str(len(p)) for p in pts)),'adjacent_duplicate_vertices':sum(a==b for r in rings for a,b in zip(r,r[1:]))}
 if pts:d['native_bbox']=[min(p[0] for p in pts),min(p[1] for p in pts),max(p[0] for p in pts),max(p[1] for p in pts)]
 return d

def run():
 counties=defaultdict(list);index=[];diagnostics=[];counts=Counter()
 for name in ['state-election-service','burlington-election-service']:
  contract=json.loads((BASE/'qa'/f'{name}-native-contract.json').read_bytes())
  for batch in contract['batches']:
   o=json.loads(content(batch['receipt']))
   for i,f in enumerate(o['features']):
    a=f['attributes'];g=f.get('geometry');county=a['COUNTY'] if name.startswith('state') else 'Burlington';d=geometry_diagnostics(g);counts[name+':'+d['case']]+=1
    diagnostics.append({'service':name,'receipt':batch['receipt'],'feature_index':i,'OBJECTID':a[contract['object_id_field']],**d})
    index.append({'service':name,'county':county,'receipt':batch['receipt'],'feature_index':i,'attributes':a,'geometry_diagnostic':d,'current_or_source_row_join':False})
    if name.startswith('state'):counties[county].append(f)
 previews=[]
 for county,fs in sorted(counties.items()):
  pts=[p for f in fs for r in (f.get('geometry') or {}).get('rings',[]) for p in r]
  x0=min(p[0] for p in pts);x1=max(p[0] for p in pts);y0=min(p[1] for p in pts);y1=max(p[1] for p in pts);scale=min(1120/(x1-x0),1430/(y1-y0));im=Image.new('RGB',(1200,1600),'white');draw=ImageDraw.Draw(im)
  draw.text((30,20),county+' | Historical state GIS | native NJ State Plane feet',fill='black');draw.text((30,40),'Affine linework preview only; no vote allocation/current legal certification',fill='black')
  for f in fs:
   for r in (f.get('geometry') or {}).get('rings',[]):
    if len(r)>1:draw.line([(40+(p[0]-x0)*scale,1540-(p[1]-y0)*scale) for p in r],fill='#274b67',width=1)
  p=BASE/'derived'/f'native-{county.lower().replace(" ","-")}.png';im.save(p)
  previews.append({'county':county,'preview':str(p.relative_to(BASE)),'features':len(fs),'native_extent':[x0,y0,x1,y1],'affine_scale':scale,'transform':'x=40+(nativeX-xmin)*scale; y=1540-(nativeY-ymin)*scale','curves':'not chorded; curve parts skipped if present','legal_certification':False})
 write(BASE/'native-feature-index.json',index);write(BASE/'qa/native-diagnostics.json',{'counts':dict(counts),'features':diagnostics,'scope':'linear-only diagnostics in original native units. No operative county outline supplied; gaps, overlap and slivers not legally certified. Curve/null/empty objects preserved without repair.'});write(BASE/'preview-index.json',previews);print(dict(counts))
if __name__=='__main__':run()
