"""Read original JSON geometry without closure, repair, hole assignment or curve linearization."""
from acquire import *
from collections import Counter,defaultdict
import math,struct,itertools
from PIL import Image,ImageDraw
import shapely,shapely.geometry,shapely.validation

def load(prefix):
 path=M/f'source/{prefix}-native-batches.json'
 if not path.exists() and prefix=='rigis':path=M/'source/native-batches.json'
 index=parsed(path);features=[]
 def data(name):return json.loads(read(parsed(M/f'requests/{name}.json')))
 ids=data(prefix+'-ids-pre');postids=data(prefix+'-ids-post');count=data(prefix+'-count-pre');postcount=data(prefix+'-count-post')
 assert ids==postids and count==postcount
 for r in index['batches']:
  req=parsed(M/f"requests/{r['request']}.json");q=urllib.parse.parse_qs(urllib.parse.urlparse(req['requested_url']).query)
  assert set(q)<=set(['f','objectIds','outFields','returnGeometry','returnZ','returnM','returnTrueCurves'])
  assert q['returnTrueCurves']==['true'] and q['returnZ']==['true'] and q['returnM']==['true'] and q['outFields']==['*']
  requested=list(map(int,q['objectIds'][0].split(',')));assert requested==r['requested_ids'] and len(requested)<=50
  x=json.loads(read(req));returned=[f['attributes'][ids['objectIdFieldName']] for f in x['features']]
  assert returned==r['returned_ids'] and set(returned)==set(requested) and len(returned)==len(requested) and not x.get('exceededTransferLimit',False)
  features+=x['features']
 assert len(features)==len(ids['objectIds'])==count['count'] and sorted(f['attributes'][ids['objectIdFieldName']] for f in features)==sorted(ids['objectIds'])
 return features,index

def differences(a,b,p=''):
 if type(a)!=type(b):return [dict(pointer=p,pre=a,post=b)]
 if isinstance(a,dict):
  out=[]
  for k in sorted(a.keys()|b.keys()):
   if k not in a or k not in b:out.append(dict(pointer=p+'/'+k,pre=a.get(k),post=b.get(k),pre_present=k in a,post_present=k in b))
   else:out+=differences(a[k],b[k],p+'/'+k)
  return out
 if isinstance(a,list):
  if len(a)!=len(b):return [dict(pointer=p,pre=a,post=b)]
  return sum([differences(v,b[i],p+'/'+str(i)) for i,v in enumerate(a)],[])
 return [] if a==b else [dict(pointer=p,pre=a,post=b)]
def geometry(g):
 if g is None:return dict(status='null',preview=False),None
 if 'curveRings' in g or 'curvePaths' in g:return dict(status='curved',preview=False,geometry_keys=list(g)),None
 if 'rings' not in g:return dict(status='unavailable_polygon',preview=False,geometry_keys=list(g)),None
 rings=g['rings'];counts=Counter();bits=hashlib.sha256();positions=0;bounds=[]
 for ring in rings:
  counts['rings']+=1
  if not ring:counts['empty_rings']+=1;continue
  if len(ring)<4:counts['short_rings']+=1
  if ring[0]!=ring[-1]:counts['open_rings']+=1
  for point in ring:
   positions+=1;counts['positions_'+str(len(point))+'D']+=1
   for v in point:
    assert isinstance(v,(int,float)) and not isinstance(v,bool)
    bits.update(struct.pack('<d',v))
   if len(point)>=2:bounds.append(point[:2])
   if any(not math.isfinite(v) for v in point):counts['nonfinite_positions']+=1
 d=dict(status='linear' if bounds else 'empty',preview=bool(bounds),counts=dict(counts),positions=positions,ordered_all_ordinate_IEEE754_sha256=bits.hexdigest(),native_bbox=[min(p[0] for p in bounds),min(p[1] for p in bounds),max(p[0] for p in bounds),max(p[1] for p in bounds)] if bounds else None)
 # GEOS only for already closed, finite, single-ring originals. No automatic closure/hole/orphan reinterpretation.
 shape=None
 if len(rings)==1 and len(rings[0])>=4 and rings[0][0]==rings[0][-1] and not counts['nonfinite_positions']:
  shape=shapely.geometry.Polygon([p[:2] for p in rings[0]])
  d['single_ring_GEOS_valid']=shape.is_valid;d['single_ring_GEOS_reason']=shapely.validation.explain_validity(shape)
  if not shape.is_valid:shape=None
 else:d['single_ring_GEOS_valid']=None;d['single_ring_GEOS_reason']='Excluded multi-ring/open/short/empty/nonfinite geometry; no source repair or hole assignment.'
 return d,shape

def preview(features,out,title):
 lines=[];points=[]
 for f in features:
  g=f.get('geometry')
  if g and 'rings' in g and 'curveRings' not in g:
   for r in g['rings']:
    if r and all(len(p)>=2 and math.isfinite(p[0]) and math.isfinite(p[1]) for p in r):lines.append(r);points+=r
 if not points:return
 xmin=min(p[0] for p in points);xmax=max(p[0] for p in points);ymin=min(p[1] for p in points);ymax=max(p[1] for p in points)
 scale=min(1320/max(xmax-xmin,1),880/max(ymax-ymin,1));tf=lambda p:(40+(p[0]-xmin)*scale,70+(ymax-p[1])*scale)
 svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="1000" viewBox="0 0 1400 1000"><rect width="1400" height="1000" fill="white"/>',f'<text x="30" y="30" font-size="20">{title}</text>','<text x="30" y="55" font-size="13">Native linear rings, stroke only. Curved/unavailable excluded. No legal/current/result crosswalk.</text>']
 im=Image.new('RGB',(1400,1000),'white');draw=ImageDraw.Draw(im);draw.text((30,20),title,fill='black');draw.text((30,43),'Native linear rings only; no current/legal/results match.',fill='black')
 for line in lines:
  coords=[tf(p) for p in line];d='M'+' L'.join(f'{x:.4f},{y:.4f}' for x,y in coords);svg.append(f'<path d="{d}" fill="none" stroke="#1c4774" stroke-width="0.7"/>')
  if len(coords)>=2:draw.line(coords,fill='#1c4774',width=1)
 svg.append('</svg>');out.parent.mkdir(parents=True,exist_ok=True);out.with_suffix('.svg').write_text('\n'.join(svg));im.save(out.with_suffix('.png'))

def run():
 report={};allf={}
 for prefix in ['rigis','sos']:
  fs,index=load(prefix);ids=json.loads(read(parsed(M/f'requests/{prefix}-ids-pre.json')));allf[prefix]=fs;diag=[];single=[];towns=Counter();labels=Counter()
  for f in fs:
   d,shape=geometry(f.get('geometry'));diag.append(dict(objectid=f['attributes'][ids['objectIdFieldName']],attributes=f['attributes'],geometry_audit=d))
   if shape is not None:single.append((f['attributes'][ids['objectIdFieldName']],shape))
   towns[f['attributes']['TOWN']]+=1;labels[f['attributes']['DISTRICT']]+=1
  intersections=[]
  for (aid,ap),(bid,bp) in itertools.combinations(single,2):
   if ap.intersects(bp):
    area=ap.intersection(bp).area
    if area>0:intersections.append(dict(objectid_a=aid,objectid_b=bid,native_coordinate_square_units=area))
  changes={}
  for kind in ['service','layer']:
   x=json.loads(read(parsed(M/f'requests/{prefix}-{kind}-pre.json')));y=json.loads(read(parsed(M/f'requests/{prefix}-{kind}-post.json')))
   changes[kind]=differences(x,y)
  report[prefix]=dict(feature_count=len(fs),native_crs=index['native_crs'],town_feature_counts=dict(towns),duplicate_district_labels={k:v for k,v in labels.items() if v>1},prepost_exact_semantic_changes=changes,prepost_full_entity_equal={kind:read(parsed(M/f'requests/{prefix}-{kind}-pre.json'))==read(parsed(M/f'requests/{prefix}-{kind}-post.json')) for kind in ['service','layer']},features=diag,single_ring_valid_intersection_scope=len(single),positive_area_intersection_diagnostics=intersections,topology_limits='Only already-closed finite valid single-ring native polygons are intersected. All multi-ring, curved, null, empty, invalid, short and open geometries are excluded from GEOS intersections. All linear raw rings remain in stroke previews, without added closure. No independent same-vintage legal state/municipal outline was acquired; no legal overlap/gap/sliver certification. No SHP/SHX/DBF originals acquired or binary-audit claim.')
  (M/'derived').mkdir(exist_ok=True);(M/f'derived/{prefix}-native-features.json.gz').write_bytes(gzip.compress(canon(fs)+b'\n',mtime=0))
  c=parsed(S/'data/turnout/priority-set.json');parents=c['municipal_and_administrative_parent_sensitivity']['full_inventory']
  for p in parents:
   if p['geography_type']!='municipality':continue
   subset=[f for f in fs if f['attributes']['TOWN']==p['name']]
   preview(subset,M/f"previews/{prefix}-{p['key'].split(':')[-1]}",f"{prefix.upper()} {p['name']} ({len(subset)} source features)")
  preview(fs,M/f'previews/{prefix}-statewide',f'{prefix.upper()} all {len(fs)} source features')
 report['source_comparison']=dict(full_feature_objects_equal=allf['rigis']==allf['sos'],scope='No source substitution or current/result-ID equivalence inferred.')
 dump(M/'qa/native-audit.json',report)
 print(json.dumps({p:{k:v for k,v in report[p].items() if k not in ['features','positive_area_intersection_diagnostics']} for p in ['rigis','sos']}))
if __name__=='__main__':run()
