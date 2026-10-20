"""Offline independent native replay and linear-only ring diagnostics/previews; no result joins."""
from common import *
from acquire import body_of
from native import diff
import urllib.parse,math,html,collections,zipfile,struct
from shapely.geometry import LineString
import shapely

def entity(path):return json.loads(body_of(load(path)))
def native_replay(snap):
 pre={t:entity(snap['pre_'+t]) for t in ['service','layer','count','ids']};post={t:entity(snap['post_'+t]) for t in pre};oid=pre['ids']['objectIdFieldName'];ids=pre['ids']['objectIds'];assert len(ids)==len(set(ids))==pre['count']['count'];allgot=[];features=[]
 for page in snap['pages']:
  r=load(page['request']);q=urllib.parse.parse_qs(urllib.parse.urlsplit(r['requested_url']).query);allowed={'f','objectIds','outFields','returnGeometry','returnZ','returnM','returnTrueCurves'};assert set(q)==allowed and q['outFields']==['*'] and all(q[k]==['true'] for k in ['returnGeometry','returnZ','returnM','returnTrueCurves']);asked=list(map(int,q['objectIds'][0].split(',')));assert asked==page['requested_ids'] and len(asked)<=50
  x=entity(page['request']);got=[v['attributes'][oid] for v in x['features']];assert len(got)==len(set(got)) and set(asked)==set(got) and got==page['returned_ids'] and not x.get('exceededTransferLimit',False)
  expected={f['name'] for f in pre['layer']['fields'] if f['type']!='esriFieldTypeGeometry'}
  for f in x['features']:assert expected<=set(f['attributes'])
  # Native CRS is checked literally, without treating EPSG aliases as an output transform.
  if x.get('spatialReference') is None:assert all(not f.get('geometry') for f in x['features']), 'missing CRS with present geometry'
  else:assert all(pre['layer']['extent']['spatialReference'].get(k)==v for k,v in x['spatialReference'].items()),(snap['key'],'native SR',x.get('spatialReference'),pre['layer']['extent']['spatialReference'])
  allgot+=got;features+=x['features']
 assert len(allgot)==len(set(allgot))==len(ids) and set(allgot)==set(ids)
 changes={t:diff(pre[t],post[t]) for t in pre};assert changes==snap['pre_post_changes'];assert snap['ids_and_count_stable']==(set(ids)==set(post['ids']['objectIds']) and pre['count']==post['count'])
 return pre,features

def preview(key,features,oid,write=True):
 rows=[];paths=[];coords=[];counts=collections.Counter()
 for f in features:
  g=f.get('geometry');r={'object_id':f['attributes'].get(oid),'geometry_status':None,'rings':[]}
  if not g:r['geometry_status']='null_or_empty_excluded';counts['null_or_empty_excluded']+=1
  elif 'curveRings'in g or 'curvePaths'in g:r['geometry_status']='curved_excluded_whole_feature';counts['curved_excluded_whole_feature']+=1
  elif not g.get('rings'):r['geometry_status']='empty_or_nonpolygon_excluded';counts['empty_or_nonpolygon_excluded']+=1
  else:
   r['geometry_status']='linear_source_positions';counts['linear_features']+=1
   for i,ring in enumerate(g['rings']):
    finite=all(len(p)>=2 and all(isinstance(v,(int,float)) and math.isfinite(v) for v in p[:2]) for p in ring);closed=bool(ring and ring[0][:2]==ring[-1][:2]);short=len(ring)<4
    rr={'ring':i,'positions':len(ring),'finite_xy':finite,'closed':closed,'short':short,'simple_closed_ring':None,'ring_area_diagnostic':None}
    if finite and closed and not short:
     line=LineString([p[:2] for p in ring]);rr['simple_closed_ring']=bool(line.is_simple and line.is_ring)
     # Shoelace magnitude only; no shell/hole/legal-outline interpretation.
     rr['ring_area_diagnostic']=abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(ring,ring[1:])))/2
     counts['nonsimple_closed_rings']+=not rr['simple_closed_ring']
    counts['open_rings']+=not closed;counts['short_rings']+=short
    if finite and ring:paths.append(ring);coords.extend(p[:2] for p in ring)
    r['rings'].append(rr)
  rows.append(r)
 header=f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="900" viewBox="0 0 1200 900"><rect width="1200" height="900" fill="#f5f4ed"/><text x="24" y="30" font-family="sans-serif" font-size="20">{html.escape(key)} — native linear ring preview</text><text x="24" y="54" font-family="sans-serif" font-size="13">Curved/empty features excluded. Stroke only; no shell/hole reinterpretation or result join.</text>'
 if coords:
  xs,ys=zip(*coords);xmin,xmax,ymin,ymax=min(xs),max(xs),min(ys),max(ys);scale=min(1140/max(xmax-xmin,1e-30),790/max(ymax-ymin,1e-30))
  for ring in paths:
   d='M'+' L'.join(f'{30+(p[0]-xmin)*scale:.2f},{855-(p[1]-ymin)*scale:.2f}' for p in ring);header+=f'<path d="{d}" fill="none" stroke="#174d69" stroke-width="0.65"/>'
 svg=(header+'</svg>\n').encode()
 if write:(M/'previews'/f'{key}.svg').write_bytes(svg)
 return {'key':key,'counts':dict(counts),'full_ring_diagnostics':rows,'preview_path':'maps/previews/'+key+'.svg','preview_sha256':sha(svg),'source_repair':False,'topology_scope':'linear closed source-ring simplicity only; curved/empty excluded, open/short preserved but excluded from closed-ring topology. No legal gap/overlap/sliver certification, no polygon shell/hole assignment or positive-area intersection test.'}

def build(write=True):
 output=[]
 for p in sorted((M/'native').glob('*.json')):
  snap=load(str(p.relative_to(S)))
  if not snap['complete']:continue
  pre,features=native_replay(snap);a=preview(snap['key'],features,snap['object_id_field'],write);a['full_snapshot']=str(p.relative_to(S));a['feature_count']=len(features);output.append(a)
 # Binary sources use raw positions/parts parsed independently by the binary audit, not GeoJSON conversion.
 for summary in load('maps/qa/binary-summary.json'):
  r=load(summary['request']);b=body_of(r);z=zipfile.ZipFile(io.BytesIO(b))
  for l in load(summary['audit'])['layers']:
   shp=z.read(l['stem']+'.shp');features=[]
   for rec in l['shp_shx_records']:
    rings=[]
    if rec['shape_type']!=0:
     start=rec['shp_offset']+8+44+len(rec['parts'])*4;pts=[list(struct.unpack_from('<2d',shp,start+16*j)) for j in range(rec['positions'])];rings=[pts[a:b] for a,b in zip(rec['parts'],rec['parts'][1:]+[len(pts)])]
    features.append({'attributes':{'raw_record':rec['record']},'geometry':{'rings':rings}})
   key='binary-'+r['key'];a=preview(key,features,'raw_record',write);a['binary_audit']=summary['audit'];a['feature_count']=len(features);output.append(a)
 result={'status':'pass','native_snapshots':sum('full_snapshot'in x for x in output),'binary_layers':sum('binary_audit'in x for x in output),'shapely_version':shapely.__version__,'GEOS_version':shapely.geos_version_string,'layers':output,'inferred_result_polygon_joins':0,'spatial_vote_ballot_registration_allocation':False}
 if write:save('maps/qa/geography.json.gz',result)
 return result
if __name__=='__main__':
 r=build();print(json.dumps({'status':r['status'],'native':r['native_snapshots'],'binary':r['binary_layers'],'layers':[{k:x[k] for k in ['key','feature_count','counts']} for x in r['layers']]}))
